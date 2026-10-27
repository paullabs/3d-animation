"""mede a trajetória da cabeça vs quadril a partir de /tmp/anim_curves.json e desenha num PNG.
python3 measure.py saida.png [f_ini f_fim]"""
import json, math, sys, subprocess
d = json.load(open("/tmp/anim_curves.json")); out = sys.argv[1]
a = int(sys.argv[2]) if len(sys.argv) > 2 else 20; b = int(sys.argv[3]) if len(sys.argv) > 3 else 90
X, Z = d["x"], d["hipz"]; T, C, H = d["torso"], d["chest"], d["head"]; CZ = d.get("chestz", [0] * len(X))
def rot(v, ang):
    r = math.radians(ang); x, z = v
    return (x * math.cos(r) + z * math.sin(r), -x * math.sin(r) + z * math.cos(r))
def head_pos(k):
    # quadril -> peito (0, .2+cz) girado pelo tronco -> pescoço (.02,.26) girado por tronco+peito -> cabeça (0,.1) e centro (0,.2)
    x, z = X[k], Z[k]
    v = rot((0, 0.2 + CZ[k]), T[k]); x += v[0]; z += v[1]
    v = rot((0.02, 0.26), T[k] + C[k]); x += v[0]; z += v[1]
    v = rot((0, 0.1), T[k] + C[k] + 0.3 * H[k]); x += v[0]; z += v[1]
    v = rot((0, 0.2), T[k] + C[k] + H[k]); x += v[0]; z += v[1]
    return x, z
hx, hz = zip(*[head_pos(k) for k in range(len(X))])
rng = range(a, b)
def detrend(s):
    s = [s[k] for k in rng]; n = len(s); m = (s[-1] - s[0]) / (n - 1)
    return [s[i] - (s[0] + m * i) for i in range(n)]
def jerk(s):
    return sum(abs(s[i + 1] - 2 * s[i] + s[i - 1]) for i in range(1, len(s) - 1)) / (len(s) - 2) * 1000
rows = {"quadril x (desvio)": detrend(X), "cabeça x (desvio)": detrend(hx), "quadril z": [Z[k] for k in rng], "cabeça z": [hz[k] for k in rng]}
for n, s in rows.items():
    print(f"{n:20s} amplitude {max(s) - min(s):.4f} m   aspereza {jerk(s):.3f}")
W, Hh = 1200, 200 * len(rows)
img = bytearray([24, 20, 36] * W * Hh)
cols = [(255, 120, 90), (120, 200, 255), (255, 210, 110), (150, 255, 150)]
for ci, (n, s) in enumerate(rows.items()):
    lo, hi = min(s), max(s); hi = hi if hi > lo else lo + 1e-6
    scale = max(hi - lo, 0.06)
    mid = (hi + lo) / 2
    for i, v in enumerate(s):
        x = int(i / (len(s) - 1) * (W - 1)); y = ci * 200 + 100 - int((v - mid) / scale * 170)
        for dy in (-1, 0, 1):
            o = ((y + dy) * W + x) * 3; img[o:o + 3] = bytes(cols[ci])
open("/tmp/m.ppm", "wb").write(b"P6 %d %d 255\n" % (W, Hh) + bytes(img))
subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", "/tmp/m.ppm", out], check=True)
