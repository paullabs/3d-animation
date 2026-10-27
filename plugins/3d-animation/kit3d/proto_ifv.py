"""Protótipo de cena no estilo IfverseTales: rua ao entardecer, personagem andando, câmera com parallax e desfoque.
blender -b -P proto_ifv.py -- --scale 0.5 --out DIR [--still 1.0,3.0]"""
import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy, lib
from lib import *
from mathutils import Vector
import sets
from stick import Stick
argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
arg = lambda n, d=None: argv[argv.index(n) + 1] if n in argv else d
FPS = 24; DUR = 5.0
k = float(arg("--scale", "0.5"))
reset(int(1080 * k), int(1920 * k), FPS, int(arg("--samples", "16")))
sc = lib.scene; sc.frame_start, sc.frame_end = 1, int(DUR * FPS)
sets.dusk_street()
sun = bpy.data.lights.new("sun", "SUN"); sun.energy = 3.0
so = bpy.data.objects.new("sun", sun); sc.collection.objects.link(so); so.rotation_euler = (math.radians(55), 0, math.radians(-140))
H = Stick("heroi")
F = lambda t: 1 + round(t * FPS)
# caminhada: x de -2.2 a 1.6, olhando para +X
x0, x1 = -2.2, 1.4
N = 10
for i in range(N + 1):
    u = i / N; t = DUR * 0.8 * u
    sgn = 1 if i % 2 else -1
    mid = 0 < i < N
    H.pose(F(t), dict(loc=(x0 + (x1 - x0) * u, 0.0, 0.0), rz=90,
                      legA=26 * sgn if mid else 0, legB=-26 * sgn if mid else 0,
                      shinA=(18 if sgn < 0 else 4) if mid else 0, shinB=(18 if sgn > 0 else 4) if mid else 0,
                      armA=(-22 * sgn if mid else 0, 0, 4), armB=(22 * sgn if mid else 0, 0, 4),
                      foreA=-18, foreB=-18, torso=(5, 0, 0), pelvis_z=0.95 + (0.025 if i % 2 else 0),
                      mouth=(1.0, 0.4), brow=0), "BEZIER")
# para e olha para a câmera
H.pose(F(DUR * 0.8 + 0.35), dict(loc=(x1 + 0.1, 0, 0), rz=35, mouth=(1.1, 0.9), brow=-10, browup=-0.015, look=(0.0, 0.0)), "BEZIER")
H.pose(F(DUR), dict(loc=(x1 + 0.1, 0, 0), rz=30, mouth=(1.1, 1.0), brow=-12, browup=-0.02), "CONSTANT")
# câmera lateral acompanhando (parallax real com prédios e skyline)
cd = bpy.data.cameras.new("cam"); cd.sensor_width = 24; cd.lens = 30
cam = bpy.data.objects.new("cam", cd); sc.collection.objects.link(cam); sc.camera = cam
cd.dof.use_dof = True; cd.dof.focus_distance = 5.0; cd.dof.aperture_fstop = 1.6
tg = empty("cam_t")
c = cam.constraints.new("TRACK_TO"); c.target = tg; c.track_axis = "TRACK_NEGATIVE_Z"; c.up_axis = "UP_Y"
cd.dof.focus_distance = 5.6
for t, cx, tx, cz in ((0, -2.6, -1.9, 0.9), (DUR, 0.9, 1.3, 1.0)):
    cam.location = (cx, -5.6, cz); key(cam, "location", F(t), "BEZIER")
    tg.location = (tx, 0.5, 2.3); key(tg, "location", F(t), "BEZIER")
caps = captions(cam, 1, F(DUR), "E se você tivesse 500 de QI?", hi=["500"], lens=30, size=0.25)
if "--captions" in argv:
    # passada só da legenda: fundo transparente, sem desfoque
    keep = set()
    for c_ in caps:
        keep.add(c_.name); keep.update(ch.name for ch in c_.children)
    for o in sc.objects:
        if o.type in ("MESH", "FONT", "CURVE") and o.name not in keep:
            o.hide_render = True
    sc.render.film_transparent = True; cd.dof.use_dof = False
else:
    for c_ in caps:
        c_.hide_render = True
        for ch in c_.children:
            ch.hide_render = True
out = arg("--out", "/tmp/proto"); os.makedirs(out, exist_ok=True)
if "--still" in argv:
    for t in arg("--still").split(","):
        sc.frame_set(F(float(t))); sc.render.filepath = f"{out}/still_{t}.png"; bpy.ops.render.render(write_still=True)
else:
    sc.render.image_settings.file_format = "PNG"; sc.render.filepath = f"{out}/f_"
    bpy.ops.render.render(animation=True)
