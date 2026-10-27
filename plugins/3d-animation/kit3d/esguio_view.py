import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy, lib
from lib import *
from heroi import Heroi
reset(2400, 1350, 24, 16)
sc = lib.scene
sc.world.node_tree.nodes["Background"].inputs[0].default_value = (*srgb("#3a2f55"), 1); sc.world.node_tree.nodes["Background"].inputs[1].default_value = 1
for i, v in enumerate(("front", "q", "q", "side")):
    h = Heroi(f"e{i}", v, prop=Heroi.ESGUIO)
    h.pose(1, dict(x=i * 0.95, face=(-1 if i == 2 else 1)), "CONSTANT")
cd = bpy.data.cameras.new("c"); cd.type = "ORTHO"; cd.ortho_scale = 4.4
co = bpy.data.objects.new("c", cd); sc.collection.objects.link(co); co.location = (1.42, -10, 1.0); co.rotation_euler = (math.radians(90), 0, 0)
sc.camera = co; sc.frame_set(1); sc.render.filepath = sys.argv[-1]; bpy.ops.render.render(write_still=True)
