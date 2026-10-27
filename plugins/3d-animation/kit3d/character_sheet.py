"""Ficha de personagem: vistas (frente, 3/4, lado, costas), expressões e poses.
blender -b --python character_sheet.py -- --out DIR   -> DIR/view_*.png exp_*.png pose_*.png"""
import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy, lib
from lib import *
from mathutils import Vector
from human import Person

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
out = argv[argv.index("--out") + 1] if "--out" in argv else "/tmp/sheet"
os.makedirs(out, exist_ok=True)
reset(700, 1000, 30, 48)
sc = lib.scene
sc.frame_start, sc.frame_end = 1, 40
room = Room(); lights()
room.color(1, "#3b4a63", "#10151f")

P = Person("recruta", skin="#e9b58c", shirt="#f2b705", pants="#33425f", shoes="#e8e8ea",
           hair="cap", hair_color="#3b2412", collar="#d9a300")
P.add_badge("NOVO")

EXP = {
 "neutro":   dict(brow=0, eye=1.0, mouth=(1.0, 0.5)),
 "medo":     dict(brow=26, eye=1.45, mouth=(0.8, 1.6), head=(-3, 0, 0)),
 "raiva":    dict(brow=-24, eye=0.85, mouth=(1.2, 0.35), head=(4, 0, 0)),
 "choque":   dict(brow=34, eye=1.75, mouth=(0.9, 2.4), head=(-5, 0, 0)),
 "convencido": dict(brow=-12, eye=0.78, mouth=(1.5, 0.3), head=(-4, 8, 0)),
 "triste":   dict(brow=30, eye=0.9, mouth=(0.7, 0.4), head=(8, 0, 0)),
 "riso":     dict(brow=-8, eye=0.5, mouth=(1.5, 2.2), head=(-8, 0, 0)),
}
POSES = {
 "parado":  dict(),
 "sentado": dict(loc=(0, 0.6, 0), pelvis_z=0.52, legA=-90, legB=-90, shinA=90, shinB=90, armA=(-35, 0, 6), armB=(-35, 0, -6), foreA=-40, foreB=-40),
 "apontando": dict(armA=(-90, 0, 10), foreA=-5, torso=(4, 0, 0), brow=-10, mouth=(1.1, .8)),
 "pensando": dict(armA=(-20, 0, 20), foreA=-125, head=(6, 10, 0), brow=14, look=(0.8, 0.5), legB=-8, shinB=14),
 "correndo": dict(legA=-50, shinA=70, legB=30, shinB=10, armA=(35, 0, 10), foreA=-85, armB=(-60, 0, 10), foreB=-85, torso=(12, 0, 0), eye=1.3, mouth=(.9, 1.6), brow=12, loc=(0, 0, 0.08)),
}
def cam(loc, tgt, lens=40):
    cd = bpy.data.cameras.new("c"); cd.sensor_width = 24; cd.lens = lens
    co = bpy.data.objects.new("c", cd); sc.collection.objects.link(co); co.location = loc
    co.rotation_euler = (Vector(tgt) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    return co

def shoot(name, co, w=700, h=1000, frame=1):
    sc.camera = co; sc.render.resolution_x, sc.render.resolution_y = w, h
    sc.frame_set(frame); sc.render.filepath = f"{out}/{name}.png"
    bpy.ops.render.render(write_still=True)

# vistas: frente, 3/4, lado, costas
P.pose(1, dict(), "CONSTANT")
for nm, ang in (("front", 0), ("three", 35), ("side", 90), ("back", 180)):
    a = math.radians(ang)
    d = 5.2
    shoot("view_" + nm, cam((math.sin(a) * d, -math.cos(a) * d, 1.0), (0, 0, 0.93), 50))
# expressões (close do rosto)
f = 2
for nm, e in EXP.items():
    P.pose(f, e, "CONSTANT")
    shoot("exp_" + nm, cam((0.0, -1.35, 1.78), (0, 0, 1.76), 50), 500, 500, f)
    f += 1
# poses
for nm, e in POSES.items():
    P.pose(f, e, "CONSTANT")
    if nm == "sentado":
        shoot("pose_" + nm, cam((2.9, -4.4, 0.95), (0, 0.4, 0.85), 50), 700, 1000, f)
    else:
        shoot("pose_" + nm, cam((2.5, -4.6, 1.0), (0, 0, 0.93), 50), 700, 1000, f)
    f += 1
