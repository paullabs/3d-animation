"""Prova do estilo IfverseTales: boneco 2D andando, fundo em camadas, câmera que só desliza.
blender -b -P proto2d.py -- --scale 0.5 --out DIR [--still 1.0,4.5] [--captions]"""
import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy, lib
from lib import *
import sets2d
from puppet2d import Puppet
argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
arg = lambda n, d=None: argv[argv.index(n) + 1] if n in argv else d
FPS = 24; DUR = 5.0
k = float(arg("--scale", "0.5"))
reset(int(1080 * k), int(1920 * k), FPS, int(arg("--samples", "24")))
sc = lib.scene; sc.frame_start, sc.frame_end = 1, int(DUR * FPS)
F = lambda t: 1 + round(t * FPS)
sets2d.dusk_street2d()
H = Puppet("heroi", rim="#ffb47a")
H.walk(0.0, 3.6, -1.1, 1.9, FPS, extra=dict(eye="open", mouth="flat"))
H.pose(F(3.95), dict(x=2.0, lean=0, turn=0.0, head=-4, eye="open", lidopen=0.55, lid=-8, mouth="smile", armF=6, foreF=-10, armB=-6), "BEZIER")
H.pose(F(5.0), dict(x=2.0, lean=0, turn=0.0, head=-6, eye="open", lidopen=0.5, lid=-10, mouth="smile", armF=6, foreF=-10, armB=-6), "CONSTANT")
# câmera: só translação (sem girar), lente 35, desfoque no boneco
cd = bpy.data.cameras.new("cam"); cd.sensor_width = 24; cd.lens = 35
cam = bpy.data.objects.new("cam", cd); sc.collection.objects.link(cam); sc.camera = cam
cam.rotation_euler = (math.radians(90), 0, 0)
cd.dof.use_dof = True; cd.dof.focus_distance = 5.2; cd.dof.aperture_fstop = 0.22
for t, cx, cz, cy in ((0.0, -0.7, 1.75, -5.2), (3.8, 1.75, 1.75, -5.2), (5.0, 2.0, 1.7, -4.7)):
    cam.location = (cx, cy, cz); key(cam, "location", F(t), "BEZIER")
caps = captions(cam, 1, F(DUR), "E se você tivesse 500 de QI?", hi=["500"], lens=35, size=0.24)
if "--captions" in argv:
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
out = arg("--out", "/tmp/proto2d"); os.makedirs(out, exist_ok=True)
if "--still" in argv:
    for t in arg("--still").split(","):
        sc.frame_set(F(float(t))); sc.render.filepath = f"{out}/still_{t}.png"; bpy.ops.render.render(write_still=True)
else:
    sc.render.image_settings.file_format = "PNG"; sc.render.filepath = f"{out}/f_"
    bpy.ops.render.render(animation=True)
