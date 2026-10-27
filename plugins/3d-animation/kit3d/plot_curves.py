"""desenha as curvas de /tmp/anim_curves.json num PNG (sem bibliotecas): python3 plot_curves.py saida.png canal1,canal2,..."""
import json, sys, subprocess
d = json.load(open("/tmp/anim_curves.json")); out = sys.argv[1]; chans = sys.argv[2].split(",")
W, Hh = 1400, 180 * len(chans)
img = bytearray([24, 20, 36] * W * Hh)
cols = [(255, 120, 90), (120, 200, 255), (255, 210, 110), (150, 255, 150), (230, 150, 255), (255, 255, 255)]
for ci, c in enumerate(chans):
    a = d[c]; lo, hi = min(a), max(a); hi = hi if hi > lo else lo + 1
    y0 = ci * 180
    for x in range(W):
        img[(y0 + 179) * W * 3 + x * 3: (y0 + 179) * W * 3 + x * 3 + 3] = bytes([60, 55, 80])
    prev = None
    for i, v in enumerate(a):
        x = int(i / (len(a) - 1) * (W - 1)); y = y0 + 10 + int((1 - (v - lo) / (hi - lo)) * 160)
        pts = [(x, y)] if prev is None else [(prev[0] + (x - prev[0]) * t / 8, prev[1] + (y - prev[1]) * t / 8) for t in range(9)]
        for px, py in pts:
            px, py = int(px), int(py)
            for dy in (-1, 0, 1):
                if 0 <= py + dy < Hh:
                    o = ((py + dy) * W + px) * 3; img[o:o + 3] = bytes(cols[ci % len(cols)])
        prev = (x, y)
open("/tmp/plot.ppm", "wb").write(b"P6 %d %d 255\n" % (W, Hh) + bytes(img))
subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", "/tmp/plot.ppm", out], check=True)
print(out, {c: (round(min(d[c]), 3), round(max(d[c]), 3)) for c in chans})
