"""VISÃO AMPLA do mundo fixo, de cima (pedido de 25/10/2026: "você precisa ter uma visão ampla para os objetos não colidirem; tem que dar um espaço").
Mostra a rua, o ônibus, os prédios, as réguas e, em vermelho, o espaço que o boneco ocupa em cada passo (corpo de ponta a ponta de braço, com a margem).
blender -b -P mapa_topo.py -- SAIDA.png"""
import os, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy, lib, cena
import mundo7 as W
import story_passos2 as S2
from heroi3d import plano

lib.reset(900, 1500, 24, 8)
W.construir(5)
for k in range(1, 6):
    r = 0.30 * 2 ** k                                        # meia-largura do corpo com os braços (0,30 u de cada lado); o anel claro é a margem de 0,1 u
    cena.ground_disc(f"hero{k}", r, r, plano("#e53935"), (0.0, W.Y[k], 0.4), n=48)
    cena.ground_disc(f"hero_m{k}", r + 0.10 * 2 ** k, r + 0.10 * 2 ** k, plano("#ffb3b0"), (0.0, W.Y[k], 0.3), n=48)
cd = bpy.data.cameras.new("topo"); cd.type = "ORTHO"; cd.ortho_scale = 150.0; cd.clip_end = 2000
cam = bpy.data.objects.new("topo", cd); bpy.context.scene.collection.objects.link(cam); bpy.context.scene.camera = cam
cam.location = (12.0, -52.0, 500.0); cam.rotation_euler = (0, 0, 0)
bpy.context.scene.render.filepath = sys.argv[sys.argv.index("--") + 1]
bpy.ops.render.render(write_still=True)
