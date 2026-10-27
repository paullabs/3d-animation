"""História: Primeiro dia no cartel. blender -b -P cartel.py -- [--still N:SEG] [--out DIR] [--scale 0.5] [--samples 16]
Lê timing.json (feito por make_voice.py) para saber a duração de cada plano."""
import sys, os, json, math, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy
import lib
from lib import *
from human import Person

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
def arg(name, default=None):
    return argv[argv.index(name) + 1] if name in argv else default

HERE = os.path.dirname(os.path.abspath(__file__))
T = json.load(open(os.path.join(HERE, "timing.json")))
FPS = T["fps"]; SH = T["shots"]
sc_ = float(arg("--scale", "1.0"))
reset(int(1080 * sc_), int(1920 * sc_), FPS, int(arg("--samples", "24")))
scene = lib.scene
scene.frame_start, scene.frame_end = 1, T["total_frames"]
room = Room(); lights()

HI = ["duas horas", "morreu", "bigode", "chefe", "rival", "hum", "ameaça", "paz", "sócios", "chefe", "colado", "aceitado"]
PAL = {
    "blue":  ("#2f6aa3", "#08182c"), "night": ("#1b2540", "#04070f"), "red": ("#8e2218", "#1c0605"),
    "wine":  ("#6b1634", "#13030a"), "gold": ("#a57a1c", "#1e1405"), "green": ("#22703a", "#041a0c"),
}
BG = ["blue", "night", "blue", "night", "wine", "red", "red", "gold", "green", "gold", "blue", "night"]

def S(i):            # plano 1..12 -> (f0, f1, n_frames)
    s = SH[i - 1]; return s["f0"], s["f1"], s["f1"] - s["f0"]
def F(i, t):         # frame do plano i, t segundos depois do início
    return S(i)[0] + round(t * FPS)

# ----------------------------------------------------------- elenco
R = Person("recruta", shirt="#f2b705", pants="#3a4a6b", hair="cap", hair_color="#3b2412")
R.add_mustache("#1a1208")
badge_novo = R.add_badge("NOVO")
badge_chefe = R.add_badge("CHEFE", "#ffd43b", "#111111")
B = Person("chefe", skin="#b5c79a", shirt="#2b2b35", pants="#24242c", hair="sides", hair_color="#9a9a9a", tie="#c0392b", belly=1.3)
B.add_mustache("#9a9a9a"); B.must_scale(1, 1.0, "CONSTANT")
G1 = Person("capanga1", shirt="#3a3a46", pants="#2a2a33", hair="cap", hair_color="#111111", sunglasses=True, tie="#777777", scale=1.04, skin="#e0b08a")
G2 = Person("capanga2", shirt="#3a3a46", pants="#2a2a33", hair=None, sunglasses=True, tie="#777777", scale=1.0, skin="#8d5a3b")
V = Person("rival", shirt="#8c1d40", pants="#5a1228", hair="puff", hair_color="#d8d8d8", tie="#ffd43b", scale=1.03, skin="#d89b72", belly=1.1)
V.add_mustache("#d8d8d8"); V.must_scale(1, 0.9, "CONSTANT")
V1 = Person("rival1", shirt="#6d1631", pants="#3d0c1b", hair="cap", hair_color="#111111", sunglasses=True, skin="#e0b08a")
V2 = Person("rival2", shirt="#6d1631", pants="#3d0c1b", hair=None, sunglasses=True, skin="#8d5a3b", scale=1.05)
CAST = {"R": R, "B": B, "G1": G1, "G2": G2, "V": V, "V1": V1, "V2": V2}

# ----------------------------------------------------------- cenário
wood = mat("wood", "#4a2f1b", 0.7); gold_m = mat("goldtrim", "#d9a82b", 0.3); leather = mat("leather", "#6b1d1d", 0.4)
desk_top = box("desk_top", (3.0, 0.9, 0.1), wood, None, (0, 0.35, 0.78), 0.03)
desk_front = box("desk_front", (2.9, 0.08, 0.74), wood, None, (0, -0.03, 0.4), 0.02)
desk_trim = box("desk_trim", (3.04, 0.05, 0.05), gold_m, None, (0, -0.1, 0.8), 0.01)
chair_seat = box("chair_seat", (0.8, 0.72, 0.12), leather, None, (0, 0.95, 0.39), 0.04, True)
chair_back = box("chair_back", (0.8, 0.12, 1.15), leather, None, (0, 1.35, 0.95), 0.05, True)
rug = box("rug", (1.1, 1.7, 0.05), mat("rug", "#7a1f1f", 0.9), None, (-2.4, 1.45, 0.3), 0.02)
for o in (desk_top, desk_front, desk_trim, chair_seat, chair_back, rug):
    pass
contract = box("contract", (0.5, 0.7, 0.012), mat("paper", "#f6f1e4", 0.8), None, (-0.1, 0.2, 0.845), 0.003)
paz = text("paz", "PAZ", 0.18, mat("stamp", "#d11a2a", 0.6, emit=0.6), contract, (0, 0.05, 0.012), font())
paz.rotation_euler = (0, 0, 14 * D2R)
set_visible(contract, 1, False)
paz.scale = (0.0001,) * 3; setkey(paz, "scale", (0.0001,) * 3, 1, "CONSTANT")
pen = None

# balão "HUM."
bub = empty("bubble", None, (0.3, 0.55, 1.72))
sphere("bub_body", 0.5, mat("bubble", "#ffffff", 0.5, emit=0.4), bub, (0, 0, 0), (0.46, 0.12, 0.28))
t_hum = text("bub_txt", "HUM.", 0.15, mat("bubtxt", "#111111", 0.5), bub, (0, -0.07, 0), font())
t_hum.rotation_euler = (90 * D2R, 0, 0)
sphere("bub_tail", 0.07, mat("bubble", "#ffffff"), bub, (-0.2, 0, -0.26), (1, 0.4, 1))
bub.scale = (0.0001,) * 3; setkey(bub, "scale", (0.0001,) * 3, 1, "CONSTANT")

# gotas de suor
drops = []
for i in range(3):
    d = sphere(f"drop{i}", 0.04, mat("sweat", "#7fd0ff", 0.2, emit=0.3), None, (0, 0, -5), (0.7, 0.7, 1.1))
    drops.append(d)

# linhas de impacto atrás do rival
rays = empty("rays", None, (0, -3.4, 1.75))
rnd = random.Random(7)
for i in range(16):
    a = i * 22.5 * D2R
    arm = empty(f"ray_arm{i}", rays); arm.rotation_euler = (0, a, 0)
    L = 0.7 + rnd.random() * 0.6
    box(f"ray{i}", (0.035, 0.02, L), mat("ray", "#fff4b0", 0.5, emit=1.2), arm, (0, 0, 0.95 + L / 2), 0.005)
set_visible(rays, 1, False)

# dinheiro
money = empty("money")
notes = []
mg = mat("note", "#2f9e44", 0.6, emit=0.15)
for i in range(70):
    n = box(f"note{i}", (0.2, 0.1, 0.012), mg, money, (0, 0, 0), 0.002)
    notes.append(n)
set_visible(money, 1, False)

# ponto de interrogação
qm = text("qmark", "?", 0.7, mat("qm", "#ffd43b", 0.5, emit=0.8), None, (0.5, 0.8, 1.95), font(), extrude=0.04)
qm.rotation_euler = (90 * D2R, 0, 0)
qm.scale = (0.0001,) * 3; setkey(qm, "scale", (0.0001,) * 3, 1, "CONSTANT")


# ----------------------------------------------------------- poses base
SIT = dict(pelvis_z=0.52, legA=-90, legB=-90, shinA=90, shinB=90)
def sit(**kw):
    d = dict(SIT); d.update(kw); return d

def act(p, i, steps, hold=True):
    """steps: [(t_seg, pose_dict)] relativo ao início do plano i"""
    for k, (t, pz) in enumerate(steps):
        last = hold and k == len(steps) - 1
        p.pose(min(F(i, t), S(i)[1] - 1), pz, "CONSTANT" if last else "BEZIER")

def cast_in(i, names):
    f0 = S(i)[0]
    for n, p in CAST.items():
        p.vis(f0, n in names)

def walk(p0, p1, dur, rz, n_steps=5, base=None):
    out = []; base = base or {}
    N = n_steps * 2
    for k in range(N + 1):
        u = k / N
        loc = tuple(a + (b - a) * u for a, b in zip(p0, p1))
        sw = 28 if k % 2 == 0 else -28
        sw = 0 if k in (0, N) else sw * (1 if (k // 2) % 2 == 0 else 1)
        sgn = 1 if k % 2 else -1
        d = dict(loc=loc, rz=rz, legA=28 * sgn if 0 < k < N else 0, legB=-28 * sgn if 0 < k < N else 0,
                 armA=(-22 * -sgn if 0 < k < N else 0, 0, 8), armB=(-22 * sgn if 0 < k < N else 0, 0, -8),
                 pelvis_z=0.92 + (0.03 if k % 2 else 0.0))
        d.update(base)
        out.append((dur * u, d))
    return out

cam = Cam()
cams = {}
LENS = 34
def tele(p, t, lens):
    """mesma composição com lente mais longa: afasta a câmera do alvo"""
    k = LENS / lens * 0.66
    return tuple(tt + (pp - tt) * k for pp, tt in zip(p, t))

def shot_cam(i, p0, p1, t0, t1, lens=22, shake=0.0, interp="BEZIER"):
    f0, f1, _ = S(i)
    p0, p1 = tele(p0, t0, lens), tele(p1, t1, lens)
    cams[i] = cam.shot(f0, f1 + 1, p0, p1, t0, t1, LENS, shake, interp)
    room.color(f0, *PAL[BG[i - 1]])
    return cams[i]

TALL = dict(brow=0)
# ================================================================ PLANO 1 — gancho
cast_in(1, ["R"])
set_visible(R.root, S(1)[0], True, 1.0)
R.vis(S(1)[0], True)
act(R, 1, [
    (0.0, sit(loc=(0, 0.95, 0), rz=0, brow=16, browup=0.0, eye=1.2, mouth=(0.8, 0.6), torso=(4, 0, 0), head=(-4, 0, 0),
              armA=(-38, 0, 6), armB=(-38, 0, -6), foreA=-38, foreB=-38)),
    (1.2, sit(loc=(0, 0.95, 0), rz=0, brow=24, browup=0.02, eye=1.45, mouth=(0.7, 0.9), torso=(2, 0, 0), head=(-2, 4, 0),
              armA=(-40, 0, 6), armB=(-40, 0, -6), foreA=-44, foreB=-44, look=(0.6, 0.3))),
    (2.6, sit(loc=(0, 0.95, 0), rz=0, brow=22, eye=1.35, mouth=(0.7, 0.8), torso=(5, 0, 0), head=(-3, -4, 0),
              armA=(-40, 0, 6), armB=(-40, 0, -6), foreA=-44, foreB=-44, look=(-0.6, 0.2))),
    (3.6, sit(loc=(0, 0.95, 0), rz=0, brow=26, eye=1.5, mouth=(0.7, 1.0), torso=(5, 0, 0), head=(-3, 0, 0),
              armA=(-40, 0, 6), armB=(-40, 0, -6), foreA=-44, foreB=-44)),
])
shot_cam(1, (0.0, -2.0, 1.45), (0.05, -0.9, 1.36), (0, 0.95, 1.15), (0, 0.95, 1.12), 22)
badge_chefe.scale = (0.0001,) * 3; setkey(badge_chefe, "scale", (0.0001,) * 3, 1, "CONSTANT")

# ================================================================ PLANO 2 — chefe morto, capangas "shhh"
cast_in(2, ["B", "G1", "G2", "R"])
R.vis(S(2)[0], False)
act(B, 2, [(0, sit(loc=(0, 0.95, 0), rz=0, torso=(-6, 0, 0), head=(-38, 0, 8), eye=0.08, mouth=(1.0, 1.3), brow=10,
                 armA=(6, 0, 18), armB=(6, 0, -18), foreA=-4, foreB=-4)),
           (3.0, sit(loc=(0, 0.95, 0), rz=0, torso=(-8, 0, 0), head=(-42, 0, 6), eye=0.08, mouth=(1.0, 1.3), brow=10,
                 armA=(8, 0, 20), armB=(8, 0, -20), foreA=-4, foreB=-4))])
for g, x, rzv, side in ((G1, 1.35, -28, "A"), (G2, -1.35, 28, "B")):
    other = "B" if side == "A" else "A"
    base = dict(loc=(x, 0.75, 0), rz=rzv, brow=-10, eye=1.0, mouth=(0.5, 0.45), head=(0, 0, 0))
    up = dict(base); up["arm" + side] = (-62, 0, 0); up["fore" + side] = -128
    up2 = dict(up); up2["mouth"] = (0.4, 0.4)
    g.pose(F(2, 0), base, "BEZIER")
    g.pose(F(2, 0.5), up, "BEZIER")
    g.pose(min(F(2, 3.0), S(2)[1] - 1), up2, "CONSTANT")
shot_cam(2, (0.0, -0.6, 5.0), (0.0, -1.5, 1.9), (0, 0.8, 0.9), (0, 0.95, 1.05), 22)

# ================================================================ PLANO 3 — o bigode
cast_in(3, ["R", "G1"])
act(R, 3, [(0, sit(loc=(0, 0.95, 0), brow=18, eye=1.35, mouth=(0.8, 0.7), head=(-3, 0, 0))),
           (0.7, sit(loc=(0, 0.95, 0), brow=26, eye=1.5, mouth=(0.7, 1.0), head=(-4, 0, 0))),
           (2.3, sit(loc=(0, 0.95, 0), brow=-8, eye=1.15, mouth=(1.1, 0.3), head=(0, 3, 0)))])
act(G1, 3, [(0, dict(loc=(0.95, 0.8, 0), rz=-90, armA=(-20, 0, 0), foreA=-10, brow=-8, mouth=(0.5, 0.4))),
            (0.8, dict(loc=(0.85, 0.78, 0), rz=-90, armA=(-86, 0, 0), foreA=-24, brow=-12, mouth=(0.5, 0.4))),
            (1.4, dict(loc=(0.85, 0.78, 0), rz=-90, armA=(-86, 0, 0), foreA=-24, brow=-12, mouth=(0.5, 0.4))),
            (2.3, dict(loc=(1.1, 0.85, 0), rz=-90, armA=(-30, 0, 0), foreA=-10, brow=-8, mouth=(0.5, 0.4)))])
# bigode "pop"
R.must_scale(F(3, 0.9), 0.0001, "CONSTANT")
R.must_scale(F(3, 0.9) + 1, 1.7, "BEZIER")
R.must_scale(F(3, 1.25), 1.15, "CONSTANT")
shot_cam(3, (0.55, -0.3, 1.6), (0.35, -1.0, 1.5), (0.35, 0.9, 1.35), (0.35, 0.9, 1.3), 24)

# ================================================================ PLANO 4 — sentado na cadeira do chefe
cast_in(4, ["R", "G1", "G2", "B"])
act(B, 4, [(0, dict(loc=(-2.4, 0.95, 0.3), rx=-90, rz=0, pelvis_z=0.55, eye=0.08, mouth=(1.0, 1.2), head=(-20, 0, 0),
                    armA=(0, 0, 14), armB=(0, 0, -14))), (2.3, dict(loc=(-2.4, 0.95, 0.3), rx=-90, rz=0, pelvis_z=0.55, eye=0.08, mouth=(1.0, 1.2), head=(-20, 0, 0)))])
act(R, 4, walk((-1.9, 0.95, 0), (-0.15, 0.95, 0), 1.0, 0, 3, dict(brow=22, eye=1.3, mouth=(0.7, 0.8))) +
    [(1.25, sit(loc=(0, 0.95, 0), brow=22, eye=1.3, mouth=(0.7, 0.8), pelvis_z=0.7, legA=-40, legB=-40, shinA=40, shinB=40, torso=(12, 0, 0))),
     (1.7, sit(loc=(0, 0.95, 0), brow=24, eye=1.4, mouth=(0.7, 0.9), head=(-3, 0, 0), armA=(-38, 0, 6), armB=(-38, 0, -6), foreA=-40, foreB=-40)),
     (2.35, sit(loc=(0, 0.95, 0), brow=24, eye=1.4, mouth=(0.7, 0.9), head=(-3, 0, 0), armA=(-38, 0, 6), armB=(-38, 0, -6), foreA=-40, foreB=-40))])
act(G1, 4, walk((-3.3, 0.95, 0), (-1.55, 0.95, 0), 1.0, 90, 3, dict(brow=-10, mouth=(0.5, 0.4), armA=(-84, 0, 0), armB=(-84, 0, 0), foreA=-10, foreB=-10))
    + [(2.35, dict(loc=(-1.55, 0.95, 0), rz=90, armA=(-84, 0, 0), armB=(-84, 0, 0), foreA=-10, foreB=-10, brow=-10, mouth=(0.5, 0.4)))])
act(G2, 4, [(0, dict(loc=(1.7, 0.6, 0), rz=-35, arm_=0, armA=(-20, 0, 0), brow=-8, mouth=(0.5, 0.4))),
            (2.35, dict(loc=(1.7, 0.6, 0), rz=-35, armA=(-20, 0, 0), brow=-8, mouth=(0.5, 0.4)))])
shot_cam(4, (-2.6, -1.8, 1.5), (2.0, -2.2, 1.6), (-0.3, 0.8, 1.0), (0.0, 0.85, 1.05), 22)

# ================================================================ PLANO 5 — rival entra
cast_in(5, ["R", "V", "V1", "V2"])
act(R, 5, [(0, sit(loc=(0, 0.95, 0), rz=0, brow=22, eye=1.3, torso=(0, 0, 0), armA=(-38, 0, 6), armB=(-38, 0, -6), foreA=-40, foreB=-40)),
           (2.1, sit(loc=(0, 0.95, 0), rz=0, brow=26, eye=1.4, torso=(2, 0, 0), armA=(-38, 0, 6), armB=(-38, 0, -6), foreA=-40, foreB=-40))])
base = dict(brow=-12, mouth=(0.5, 0.4), armA=(-8, 0, 8), armB=(-8, 0, -8))
act(V, 5, walk((0, -6.2, 0), (0, -2.3, 0), 2.0, 180, 5, base))
act(V1, 5, walk((1.1, -7.2, 0), (1.05, -3.0, 0), 2.0, 180, 5, base))
act(V2, 5, walk((-1.1, -7.2, 0), (-1.05, -3.0, 0), 2.0, 180, 5, base))
shot_cam(5, (1.3, -0.6, 1.3), (1.0, -1.1, 1.25), (0, -4.0, 1.1), (0, -2.6, 1.2), 22)

# ================================================================ PLANO 6 — "hum"
cast_in(6, ["R"])
act(R, 6, [(0, sit(loc=(0, 0.95, 0), brow=26, eye=1.45, mouth=(0.6, 0.5), head=(-2, 0, 0),
                   armA=(-38, 0, 6), armB=(-38, 0, -6), foreA=-40, foreB=-40)),
           (0.7, sit(loc=(0, 0.95, 0), brow=30, eye=1.55, mouth=(0.9, 1.0), head=(-4, 0, 0),
                   armA=(-38, 0, 6), armB=(-38, 0, -6), foreA=-40, foreB=-40)),
           (1.0, sit(loc=(0, 0.95, 0), brow=30, eye=1.5, mouth=(0.7, 0.55), head=(-2, 0, 0),
                   armA=(-38, 0, 6), armB=(-38, 0, -6), foreA=-40, foreB=-40)),
           (2.4, sit(loc=(0, 0.95, 0), brow=32, eye=1.55, mouth=(0.7, 0.55), head=(-3, 0, 0), look=(0.8, 0.0),
                   armA=(-38, 0, 6), armB=(-38, 0, -6), foreA=-40, foreB=-40))])
setkey(bub, "scale", (0.0001,) * 3, F(6, 0.45), "CONSTANT")
setkey(bub, "scale", (1.25, 1.25, 1.25), F(6, 0.45) + 1, "BEZIER")
setkey(bub, "scale", (1.0, 1.0, 1.0), F(6, 0.75), "CONSTANT")
setkey(bub, "scale", (0.0001,) * 3, S(7)[0], "CONSTANT")
for k, d in enumerate(drops):
    t0 = 0.2 + k * 0.55
    x = (-0.33, 0.34, -0.28)[k]
    d.location = (x, 0.6, 1.7); key(d, "location", F(6, t0), "CONSTANT")
    d.location = (x + 0.02, 0.6, 1.25); key(d, "location", F(6, t0 + 0.8), "LINEAR")
    d.location = (x + 0.02, 0.6, -5); key(d, "location", F(6, t0 + 0.85), "CONSTANT")
    if k == 0:
        d.location = (0, 0, -5); key(d, "location", 1, "CONSTANT")
shot_cam(6, (0.15, -1.55, 1.4), (0.05, -1.1, 1.33), (0, 0.95, 1.3), (0, 0.95, 1.28), 24, shake=0.012)

# ================================================================ PLANO 7 — rival recua
cast_in(7, ["V", "R"])
R.vis(S(7)[0], True)
act(R, 7, [(0, sit(loc=(0, 0.95, 0), brow=-4, eye=1.0, mouth=(1.0, 0.3), armA=(-38, 0, 6), armB=(-38, 0, -6), foreA=-40, foreB=-40))])
act(V, 7, [(0, dict(loc=(0, -1.55, 0), rz=180, brow=-10, mouth=(0.6, 0.4), eye=1.0)),
           (0.35, dict(loc=(0, -1.55, 0), rz=180, brow=-10, mouth=(0.6, 0.4), eye=1.0)),
           (0.65, dict(loc=(0, -1.75, 0), rz=180, torso=(-16, 0, 0), head=(-8, 0, 0), brow=34, eye=1.7, mouth=(0.9, 1.4),
                       armA=(-170, 0, 22), armB=(-170, 0, -22), foreA=-18, foreB=-18)),
           (2.3, dict(loc=(0, -1.8, 0), rz=180, torso=(-18, 0, 0), head=(-8, 0, 0), brow=36, eye=1.8, mouth=(0.9, 1.5),
                      armA=(-175, 0, 26), armB=(-175, 0, -26), foreA=-20, foreB=-20))])
set_visible(rays, F(7, 0.62), True)
rays.scale = (0.2,) * 3; key(rays, "scale", F(7, 0.62), "CONSTANT")
setkey(rays, "scale", (1.25, 1.25, 1.25), F(7, 0.62) + 3, "BEZIER")
setkey(rays, "scale", (1.0, 1.0, 1.0), F(7, 1.0), "CONSTANT")
setkey(rays, "scale", (0.0001,) * 3, S(8)[0], "CONSTANT")
shot_cam(7, (0.5, 0.0, 1.95), (0.5, 0.0, 1.95), (0.0, -1.6, 1.75), (0.0, -1.7, 1.75), 22, shake=0.0)
tg7 = (0.0, -1.65, 1.75)
for fr, pp in ((S(7)[0], (0.5, 0.25, 1.95)), (F(7, 0.6), (0.5, -0.25, 1.95)), (S(7)[1] + 1, (0.4, -0.45, 1.93))):
    cams[7].location = tele(pp, tg7, 22); key(cams[7], 'location', fr, 'BEZIER')
# ================================================================ PLANO 8 — assina a paz
cast_in(8, ["V", "R"])
R.vis(S(8)[0], True)
act(R, 8, [(0, sit(loc=(0, 0.95, 0), brow=-6, eye=1.0, mouth=(1.1, 0.3), armA=(-38, 0, 6), armB=(-38, 0, -6), foreA=-40, foreB=-40))])
set_visible(contract, S(8)[0], True)
sign = [(0, dict(loc=(0.1, -0.62, 0), rz=180, brow=20, eye=1.3, mouth=(0.6, 0.5), torso=(25, 0, 0), head=(10, 0, 0),
                 armA=(-120, 0, 10), foreA=-40))]
for k in range(8):
    sign.append((0.25 + k * 0.1, dict(loc=(0.1, -0.62, 0), rz=180, brow=20, eye=1.3, mouth=(0.6, 0.5), torso=(40, 0, 0), head=(14, 0, 0),
                                       armA=(-62 - (3 if k % 2 else 0), 0, 8 - (6 if k % 2 else 0)), foreA=-30 - (5 if k % 2 else 0))))
sign.append((1.45, dict(loc=(0.1, -0.62, 0), rz=180, brow=10, eye=1.2, mouth=(0.9, 0.5), torso=(15, 0, 0), head=(0, 0, 0), armA=(-100, 0, 14), foreA=-50)))
act(V, 8, sign)
setkey(paz, "scale", (0.0001,) * 3, F(8, 1.1), "CONSTANT")
setkey(paz, "scale", (3.0, 3.0, 3.0), F(8, 1.1) + 1, "BEZIER")
setkey(paz, "scale", (1.0, 1.0, 1.0), F(8, 1.2), "CONSTANT")
set_visible(contract, S(9)[0], False)

shot_cam(8, (2.2, -0.4, 1.9), (1.6, -0.3, 1.6), (0.0, -0.1, 1.0), (0.0, -0.1, 1.15), 22)

# ================================================================ PLANO 9 — sócios
cast_in(9, ["V", "R"])
R.vis(S(9)[0], True)
act(R, 9, [(0, sit(loc=(0, 0.95, 0), brow=8, eye=1.2, mouth=(1.1, 0.4), armA=(-38, 0, 6), armB=(-38, 0, -6), foreA=-40, foreB=-40)),
           (0.5, sit(loc=(0, 0.95, 0), brow=-8, eye=1.1, mouth=(1.3, 0.5), torso=(8, 0, 0), armA=(-38, 0, 6), armB=(-84, 0, -2), foreA=-40, foreB=-14)),
           (1.0, sit(loc=(0, 0.95, 0), brow=-8, eye=1.1, mouth=(1.3, 0.5), torso=(8, 0, 0), armA=(-38, 0, 6), armB=(-84, 0, -2), foreA=-40, foreB=-14)),
           (1.35, sit(loc=(0, 0.95, 0), brow=-8, eye=1.1, mouth=(1.3, 0.5), torso=(8, 0, 0), armA=(-38, 0, 6), armB=(-88, 0, -2), foreA=-40, foreB=-14)),
           (2.3, sit(loc=(0, 0.95, 0), brow=-8, eye=1.1, mouth=(1.3, 0.5), torso=(8, 0, 0), armA=(-38, 0, 6), armB=(-84, 0, -2), foreA=-40, foreB=-14))])
sh = []
for k, t in enumerate((0, 0.5, 0.7, 0.9, 1.1, 1.3, 1.5, 2.3)):
    dy = -0.04 if k % 2 else 0.0
    sh.append((t, dict(loc=(0, -0.3, 0), rz=180, brow=-10, eye=1.0, mouth=(1.3, 0.5), torso=(14, 0, 0), head=(0, 0, 0),
                       armA=(-84 + (4 if k % 2 else 0), 0, -4), foreA=-16 + (6 if k % 2 else 0))))
act(V, 9, sh)
setkey(money, "scale", (1, 1, 1), S(9)[0], "CONSTANT")
rr = random.Random(3)
for n in notes:
    x, y = rr.uniform(-1.9, 1.9), rr.uniform(-0.6, 1.8)
    d0 = rr.uniform(0.0, 1.2)
    top = rr.uniform(4.0, 6.5)
    n.location = (x, y, top); n.rotation_euler = (rr.uniform(0, 3), rr.uniform(0, 3), rr.uniform(0, 3))
    key(n, "location", S(9)[0], "CONSTANT"); key(n, "rotation_euler", S(9)[0], "CONSTANT")
    n.location = (x, y, top); key(n, "location", F(9, d0), "LINEAR")
    n.location = (x + rr.uniform(-0.4, 0.4), y, 0.03); n.rotation_euler = (rr.uniform(0, 12), rr.uniform(0, 12), rr.uniform(0, 12))
    key(n, "location", F(9, d0 + 1.1), "LINEAR"); key(n, "rotation_euler", F(9, d0 + 1.1), "LINEAR")
setkey(money, "scale", (0.0001,) * 3, S(10)[0], "CONSTANT")
shot_cam(9, (2.7, 0.6, 1.35), (2.0, 0.5, 1.3), (0, 0.3, 1.2), (0, 0.3, 1.2), 22)

# ================================================================ PLANO 10 — virou o chefe
cast_in(10, ["R", "G1", "G2"])
suit = mat("recruta_shirt", "#f2b705")
for m_, old, new in ((R.mats["shirt"], "#f2b705", "#2b2b35"), (R.mats["pants"], "#3a4a6b", "#24242c")):
    p_ = m_.node_tree.nodes["Principled BSDF"].inputs["Base Color"]
    p_.default_value = (*srgb(old), 1); p_.keyframe_insert("default_value", frame=1)
    p_.default_value = (*srgb(old), 1); p_.keyframe_insert("default_value", frame=S(10)[0] - 1)
    p_.default_value = (*srgb(new), 1); p_.keyframe_insert("default_value", frame=S(10)[0])
setkey(badge_novo, "scale", (1, 1, 1), 1, "CONSTANT")
setkey(badge_novo, "scale", (0.0001,) * 3, S(10)[0], "CONSTANT")
setkey(badge_chefe, "scale", (1, 1, 1), S(10)[0], "CONSTANT")
act(R, 10, [(0, sit(loc=(0, 0.95, 0), brow=-14, eye=0.9, mouth=(1.3, 0.35), head=(4, 0, 0), torso=(-6, 0, 0),
                    armA=(-30, 0, 40), armB=(-30, 0, -40), foreA=-95, foreB=-95)),
            (1.5, sit(loc=(0, 0.95, 0), brow=-16, eye=0.85, mouth=(1.4, 0.3), head=(6, 0, 0), torso=(-8, 0, 0),
                      armA=(-30, 0, 40), armB=(-30, 0, -40), foreA=-95, foreB=-95))])
for g, x, rzv in ((G1, 1.5, -20), (G2, -1.5, 20)):
    g.pose(F(10, 0), dict(loc=(x, 0.5, 0), rz=rzv, torso=(0, 0, 0), brow=-6, mouth=(0.6, 0.4)), "BEZIER")
    g.pose(F(10, 0.5), dict(loc=(x, 0.5, 0), rz=rzv, torso=(55, 0, 0), head=(20, 0, 0), brow=-6, mouth=(0.6, 0.4)), "CONSTANT")
shot_cam(10, (0.0, -1.6, 0.9), (0.0, -1.1, 1.1), (0, 0.95, 1.3), (0, 0.95, 1.35), 22)

# ================================================================ PLANO 11 — bigode descolando
cast_in(11, ["R"])
act(R, 11, [(0, sit(loc=(0, 0.95, 0), brow=-6, eye=1.0, mouth=(1.1, 0.3), armA=(-30, 0, 40), armB=(-30, 0, -40), foreA=-95, foreB=-95, look=(0, 0))),
            (0.9, sit(loc=(0, 0.95, 0), brow=-6, eye=1.0, mouth=(1.1, 0.3), armA=(-30, 0, 40), armB=(-30, 0, -40), foreA=-95, foreB=-95, look=(-0.9, 0.2))),
            (1.7, sit(loc=(0, 0.95, 0), brow=14, eye=1.3, mouth=(0.8, 0.4), armA=(-30, 0, 40), armB=(-30, 0, -40), foreA=-95, foreB=-95, look=(0.9, 0.2))),
            (2.6, sit(loc=(0, 0.95, 0), brow=18, eye=1.4, mouth=(0.7, 0.5), armA=(-30, 0, 40), armB=(-30, 0, -40), foreA=-95, foreB=-95, look=(-0.9, 0.2))),
            (3.7, sit(loc=(0, 0.95, 0), brow=20, eye=1.4, mouth=(0.7, 0.5), armA=(-30, 0, 40), armB=(-30, 0, -40), foreA=-95, foreB=-95, look=(0, 0.3)))])
for t, ang in ((0.0, 0), (1.7, 0), (2.0, 34), (2.25, 18), (2.5, 38), (3.7, 30)):
    R.must_peel(min(F(11, t), S(11)[1] - 1), ang, "BEZIER")
shot_cam(11, (0.1, -1.25, 1.35), (0.0, -0.85, 1.3), (0, 0.95, 1.3), (0, 0.95, 1.28), 26)

# ================================================================ PLANO 12 — pergunta
cast_in(12, ["R"])
R.must_peel(S(12)[0], 26, "CONSTANT")
act(R, 12, [(0, sit(loc=(0, 0.95, 0), brow=8, eye=1.1, mouth=(0.8, 0.4), head=(-2, 0, 0), armA=(-38, 0, 6), armB=(-120, 0, -30), foreA=-40, foreB=-110)),
            (1.0, sit(loc=(0, 0.95, 0), brow=14, eye=1.15, mouth=(0.8, 0.4), head=(-4, 8, 0), armA=(-38, 0, 6), armB=(-120, 0, -30), foreA=-40, foreB=-110)),
            (1.9, sit(loc=(0, 0.95, 0), brow=14, eye=1.15, mouth=(0.8, 0.4), head=(-4, 8, 0), armA=(-38, 0, 6), armB=(-120, 0, -30), foreA=-40, foreB=-110))])
setkey(qm, "scale", (0.0001,) * 3, F(12, 0.3), "CONSTANT")
setkey(qm, "scale", (1.5, 1.5, 1.5), F(12, 0.3) + 1, "BEZIER")
setkey(qm, "scale", (1.0, 1.0, 1.0), F(12, 0.6), "CONSTANT")
shot_cam(12, (0.0, -1.6, 1.4), (0.0, -1.3, 1.38), (0.1, 0.95, 1.45), (0.1, 0.95, 1.45), 22)

# ================================================================ legendas
for i in range(1, 13):
    f0, f1, _ = S(i)
    captions(cams[i], f0, f1, SH[i - 1]["text"], hi=[HI[i - 1]], lens=LENS)

all_interp(room.m.node_tree, "LINEAR"); all_interp(room.fm.node_tree, "LINEAR")
for m_ in (R.mats["shirt"], R.mats["pants"]):
    all_interp(m_.node_tree, "LINEAR")

# ================================================================ render
out = arg("--out", os.path.join(HERE, "render"))
os.makedirs(out, exist_ok=True)
if "--norender" in argv:
    pass
elif "--still" in argv:
    for spec in arg("--still").split(","):
        i, sec = spec.split(":")
        f = F(int(i), float(sec))
        scene.frame_set(f)
        scene.render.filepath = os.path.join(out, f"still_s{int(i):02d}_{sec}.png")
        bpy.ops.render.render(write_still=True)
else:
    scene.render.image_settings.file_format = "PNG"
    scene.render.filepath = os.path.join(out, "f_")
    if "--blend" in argv:
        bpy.ops.wm.save_as_mainfile(filepath=os.path.join(HERE, "cartel.blend"))
    bpy.ops.render.render(animation=True)
