"""Prancha do herói em 3D: quatro ângulos (de frente, 3/4, de lado e de costas) de um figurino.
blender -b -P ficha_3d.py -- FIGURINO SAIDA.png     FIGURINO = casa | goleiro | menino"""
import os, sys, math
os.environ["VOZ_NOVA"] = ""
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy, lib
from lib import *
import cena, props
import heroi3d as H3

argv = sys.argv[sys.argv.index("--") + 1:]
FIG, SAIDA = argv[0], argv[1]
FUNDO, CHAO = "#c9c2b4", "#a99f8e"
lib.reset(3100, 1300, 24, 32)
sc = bpy.context.scene
sc.world.node_tree.nodes["Background"].inputs[0].default_value = (*srgb(FUNDO), 1)
cena.poly_mesh("parede", [(-40, 3.0, -1), (40, 3.0, -1), (40, 3.0, 12), (-40, 3.0, 12)], props.FM(FUNDO))
cena.poly_mesh("chao", [(-40, -20, 0), (40, -20, 0), (40, 3.0, 0), (-40, 3.0, 0)], props.FM(CHAO))
for i, ang in enumerate((0, 45, 90, 180)):
    x = -3.0 + i * 2.0
    if FIG == "goleiro":
        h = H3.Heroi3D(f"g{i}", "#e0602a", "#1c2230", luvas=True, escura="#b4491d", gola="#f4f1ea")
        h.pose(ombro=(-38, -38), cotovelo=(-62, -62), abre=(18, 18), quadril=(-22, -22), joelho=(44, 44), tornozelo=(-22, -22), inclina=-8, tronco=-4)
        h.quadril.location.z = 0.78
        h.rosto(boca="reta", lid=0.4)
    elif FIG == "menino":
        h = H3.Heroi3D(f"m{i}", "#f4f1ea", "#2a3a5a", escala=0.72, cabeca=0.95, body_w=0.92, arm_len=0.95, escura="#7ac943", gola="#7ac943")
        h.pose(ombro=(-6, 8), cotovelo=(-14, -10), abre=(6, 6)); h.rosto(boca="o")
    else:
        h = H3.Heroi3D(f"c{i}")
        h.pose(ombro=(-6, 8), cotovelo=(-14, -10), abre=(6, 6)); h.rosto(boca="reta")
    h.raiz.location = (x, 0, 0); h.raiz.rotation_euler.z = math.radians(ang)
    cena.ground_disc(f"sombra{i}", 0.4, 0.25, cena.amat(f"sombra{i}_m", "#000000", 1.0, 0.35, ("radial", 1.1)), (x, 0.05, 0.003), n=32)
cam_d = bpy.data.cameras.new("cam"); cam = bpy.data.objects.new("cam", cam_d); sc.collection.objects.link(cam); sc.camera = cam
cam_d.type = "ORTHO"; cam_d.ortho_scale = 8.0
cam.location = (0.0, -10.0, 0.95); cam.rotation_euler = (math.radians(90), 0, 0)
sc.render.filepath = SAIDA
bpy.ops.render.render(write_still=True)
