"""Ficha do narrador ("eu") de "O abrigo": de frente, de três quartos e pedalando de lado.
blender -b -P ficha_narrador.py -- PASTA MODO     (MODO = frente | tres_quartos | bicicleta; um por vez, porque o kit guarda materiais entre as cenas;
depois: python3 ficha_narrador_montar.py PASTA SAIDA.png)"""
import os, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy, lib
from lib import *
from mathutils import Vector
import cena, props
import elenco3d_abrigo as E3, objetos3d_abrigo as O3
import story_abrigo as SA
from prod_abrigo import pal, mundo

OUT, MODO = sys.argv[sys.argv.index("--") + 1:][:2]
os.makedirs(OUT, exist_ok=True)


def base(nome, w=600, h=900):
    lib.reset(w, h, 24, 24)
    sc = bpy.context.scene; sc.frame_start = sc.frame_end = 1
    p = pal("abrigo"); mundo(p)
    bpy.context.scene.world.node_tree.nodes["Background"].inputs[0].default_value = (*srgb("#8f9082"), 1)
    cena.poly_mesh("chao", [(-30, -30, 0), (30, -30, 0), (30, 30, 0), (-30, 30, 0)], props.FM("#7a7c6c"))
    props.skywall("fundo", 6.0, [(-2, "#8f9082"), (10, "#8f9082")], -40, 40, -2, 20)
    return sc


def render(nome):
    sc = bpy.context.scene; sc.render.filepath = f"{OUT}/{nome}.png"; bpy.ops.render.render(write_still=True)


if MODO == "frente":
    base("frente")
    h = E3.faz("eu", "eu_inv"); h.pose(ombro=(-4, 4), cotovelo=(-12, -12), abre=(6, 6)); h.rosto(boca="reta", lid=0.3)
    SA.camera((0, -3.7, 1.0), (0, 0, 0.9), 50, fstop=16.0)
elif MODO == "tres_quartos":
    base("tres")
    h = E3.faz("eu", "eu_inv"); h.pose(ombro=(-6, 6), cotovelo=(-16, -16), abre=(6, 6)); h.raiz.rotation_euler.z = math.radians(-38); h.rosto(boca="reta", lid=0.3)
    SA.camera((0, -3.7, 1.0), (0, 0, 0.9), 50, fstop=16.0)
else:
    base("bici")
    import story3_abrigo as S3
    b, h = S3.ciclista(0.0, 0.0)
    SA.camera((3.7, 0.0, 0.95), (0, -0.05, 0.9), 40, fstop=16.0)
render(MODO)
