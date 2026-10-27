import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy, lib
from lib import *
from puppet2d import flatmat
from char2d import rrect, mesh_pts
from heroi import Heroi
reset(2400, 1500, 24, 16)
sc = lib.scene
w = sc.world.node_tree.nodes["Background"]; w.inputs[0].default_value = (*srgb("#2a2142"), 1); w.inputs[1].default_value = 1
FB = bpy.data.fonts.load("/System/Library/Fonts/Supplemental/Arial Black.ttf")
V = [("ATUAL", {}),
     ("A · EQUILIBRADO", dict(neck=1.6, arm=1.25, leg=1.35, hand=1.12, body_w=0.86)),
     ("B · MAIS GRÁFICO", dict(neck=2.0, arm=1.45, leg=1.6, hand=1.22, body_w=0.76))]
for i, (nm, p) in enumerate(V):
    for j, v in enumerate(("front", "q")):
        h = Heroi(f"v{i}{v}", v, prop=p)
        h.pose(1, dict(x=i * 2.0 + j * 0.85 - 0.42), "CONSTANT")
    t = lib.text(f"lb{i}", nm, 0.11, flatmat("lw", "#f3efe6"), None, (i * 2.0, -0.3, -0.18), FB); t.rotation_euler = (math.pi / 2, 0, 0)
cd = bpy.data.cameras.new("c"); cd.type = "ORTHO"; cd.ortho_scale = 5.6
co = bpy.data.objects.new("c", cd); sc.collection.objects.link(co); co.location = (2.0, -10, 0.85); co.rotation_euler = (math.radians(90), 0, 0)
sc.camera = co; sc.frame_set(1); sc.render.filepath = sys.argv[-1]; bpy.ops.render.render(write_still=True)
