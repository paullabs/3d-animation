"""Ficha do personagem estilo IfverseTales."""
import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy, bmesh, lib
from lib import *
from mathutils import Vector
from stick import Stick, flat
out = sys.argv[sys.argv.index("--") + 2] if "--" in sys.argv else "/tmp/stick"
os.makedirs(out, exist_ok=True)
reset(720, 1000, 30, 32)
sc = lib.scene
room = Room(); room.color(1, "#3a2d55", "#c8735a")
fl = bpy.data.objects["floor"]; fl.data.materials[0] = flat("floor_flat", "#2a2034")
sun = bpy.data.lights.new("sun", "SUN"); sun.energy = 3.0
so = bpy.data.objects.new("sun", sun); sc.collection.objects.link(so); so.rotation_euler = (math.radians(50), 0, math.radians(-35))
H = Stick("heroi")
EXP = {
 "neutro": dict(mouth=(1.0, 0.35)),
 "sorriso": dict(mouth=(1.1, 1.0), brow=-4),
 "esperto": dict(mouth=(1.1, 0.8), brow=-12, browup=-0.02, look=(0.6, 0)),
 "choque": dict(mouth=(0.5, -0.6), eye=1.35, brow=14, browup=0.03),
 "triste": dict(mouth=(0.9, -0.8), brow=22, eye=0.9),
 "raiva": dict(mouth=(1.0, -0.5), brow=-24, browup=-0.03),
}
POSES = {
 "parado": dict(),
 "andando": dict(legA=-24, shinA=10, legB=22, shinB=28, armA=(20, 0, 4), armB=(-20, 0, 4), foreA=-12, foreB=-22, torso=(6, 0, 0), rz=-70),
 "pensando": dict(armA=(-20, 0, 18), foreA=-130, head=(8, 10, 0), brow=12, look=(0.8, 0.6), mouth=(0.8, 0.3)),
 "sentado": dict(pelvis_z=0.5, legA=-90, legB=-90, shinA=90, shinB=90, torso=(10, 0, 0), armA=(-40, 0, 6), armB=(-40, 0, 6), foreA=-50, foreB=-50, rz=-30),
 "apontando": dict(armA=(-90, 0, 12), foreA=-5, mouth=(1.1, 0.9), brow=-8, rz=-25),
}
def cam(loc, tgt, lens=40):
    cd = bpy.data.cameras.new("c"); cd.sensor_width = 24; cd.lens = lens
    co = bpy.data.objects.new("c", cd); sc.collection.objects.link(co); co.location = loc
    co.rotation_euler = (Vector(tgt) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    return co
def shoot(name, co, w=720, h=1000, frame=1):
    sc.camera = co; sc.render.resolution_x, sc.render.resolution_y = w, h
    sc.frame_set(frame); sc.render.filepath = f"{out}/{name}.png"; bpy.ops.render.render(write_still=True)
H.pose(1, {}, "CONSTANT")
for nm, ang in (("1front", 0), ("2three", 35), ("3side", 90), ("4back", 180)):
    a = math.radians(ang)
    shoot("view_" + nm, cam((math.sin(a) * 5.4, -math.cos(a) * 5.4, 1.1), (0, 0, 1.02), 50))
f = 2
for nm, e in EXP.items():
    H.pose(f, e, "CONSTANT"); shoot(f"exp_{f}_{nm}", cam((0.35, -1.5, 1.9), (0, 0, 1.84), 50), 500, 500, f); f += 1
for nm, e in POSES.items():
    H.pose(f, e, "CONSTANT"); shoot(f"pose_{f}_{nm}", cam((0.0, -5.4, 1.1), (0, 0, 0.95), 50), 720, 1000, f); f += 1
