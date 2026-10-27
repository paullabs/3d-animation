import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy, lib
from lib import *
from heroi import Heroi
reset(1600, 1000, 24, 8)
sc = lib.scene
sc.world.node_tree.nodes["Background"].inputs[0].default_value = (*srgb("#3a2f55"), 1); sc.world.node_tree.nodes["Background"].inputs[1].default_value = 1
for i, v in enumerate(("front", "q", "side")):
    h = Heroi(f"c{v}", v); h.pose(1, dict(x=i * 1.1), "CONSTANT")
cd = bpy.data.cameras.new("c"); cd.type = "ORTHO"; cd.ortho_scale = 3.4
co = bpy.data.objects.new("c", cd); sc.collection.objects.link(co); co.location = (1.1, -10, 1.15); co.rotation_euler = (math.radians(90), 0, 0)
sc.camera = co; sc.frame_set(1); sc.render.filepath = sys.argv[-1]; bpy.ops.render.render(write_still=True)
