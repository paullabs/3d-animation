"""Ficha da parte 2 de "O abrigo" (26/10/2026): o Sem-Osso, a gosma, o esqueleto que fica, o grupo de 9, o galpão, os objetos e a torre.
blender -b -P ficha_abrigo2.py -- PASTA MODO [--scale 1.0]      (um modo por processo: o kit guarda materiais entre as cenas)
MODOS: semosso_frente, semosso_lado, semosso_bone, gosma, olhos, esqueleto, grupo, galpao, objetos, torre
depois: python3 ficha_abrigo2_montar.py PASTA"""
import os, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy, lib
from lib import *
from mathutils import Vector
import cena, props
import elenco3d_abrigo as E3, objetos3d_abrigo as O3, objetos3d_abrigo_b as O3B, objetos3d_abrigo2 as O2
import story_abrigo as SA
from prod_abrigo import pal, mundo

a = sys.argv[sys.argv.index("--") + 1:]
OUT, MODO = a[0], a[1]
ESC = float(a[a.index("--scale") + 1]) if "--scale" in a else 1.0
os.makedirs(OUT, exist_ok=True)
TAM = {"cabeca_f": (600, 900), "cabeca_3q": (600, 900), "cabeca_p": (600, 900), "cabeca_m": (600, 900),  "grupo": (1800, 900), "galpao": (1200, 900), "objetos": (1200, 900), "gosma": (1200, 900)}


def base(fundo="#8f9082", chao="#7a7c6c"):
    w, h = TAM.get(MODO, (600, 900))
    lib.reset(int(w * ESC), int(h * ESC), 24, 24)
    sc = bpy.context.scene; sc.frame_start = sc.frame_end = 1
    p = pal("abrigo"); mundo(p)
    sc.world.node_tree.nodes["Background"].inputs[0].default_value = (*srgb(fundo), 1)
    if chao:
        cena.poly_mesh("chao", [(-60, -60, 0), (60, -60, 0), (60, 60, 0), (-60, 60, 0)], props.FM(chao))
        props.skywall("fundo", 8.0, [(-2, fundo), (10, fundo)], -60, 60, -2, 30)
    return sc


def cam(loc, alvo, lente, fstop=16.0):
    c = SA.camera(loc, alvo, lente, fstop=fstop)
    O3.olha_camera(c)
    return c


def render():
    sc = bpy.context.scene; sc.render.filepath = f"{OUT}/{MODO}.png"; bpy.ops.render.render(write_still=True)


if MODO == "semosso_frente":
    base("#6e7068", "#5e6058")
    h = O2.sem_osso("so", "padeira", (0, 0, 0), rot=-18)
    cam((0.3, -3.6, 1.0), (0, 0, 0.85), 50)
elif MODO == "semosso_lado":
    base("#6e7068", "#5e6058")
    h = O2.sem_osso("so", "padeira", (0, 0, 0), rot=-90, curva=1.3, seed=5)
    cam((0.0, -3.6, 0.9), (0, 0, 0.8), 50)
elif MODO == "semosso_bone":
    base("#6e7068", "#5e6058")
    h = O2.sem_osso("so", "mercado", (0, 0, 0), rot=24, curva=0.8, seed=8)
    cam((-0.3, -3.6, 1.0), (0, 0, 0.85), 50)
elif MODO == "gosma":
    # da poça ao corpo, da esquerda para a direita: poça, poças se juntando, a gosma subindo, o corpo quase formado
    base("#6e7068", "#5e6058")
    O2.poca("p1", -1.65, 0.0, 0.32, 0.22, seed=1)
    O2.mancha("m2", [(-0.95 + 0.07 * k, 0.02 * math.sin(k)) for k in range(9)], larg=0.12, seed=2)
    O2.gosma("p2", [(-0.6 + 0.05 * math.cos(k), 0.0, 0.01 + 0.03 * k, 1.0, (0.14 - 0.015 * k, 0.12 - 0.012 * k, 0.05)) for k in range(5)], brilhos=4, seed=2)
    O2.gosma("p3", [(0.3, 0.0, 0.0, 1.0, (0.2, 0.17, 0.04))] + [(0.3 + 0.03 * math.sin(k * 0.9), -0.01 * k, 0.06 + 0.07 * k, 1.0, (0.13 - 0.007 * k, 0.11 - 0.006 * k, 0.07))
                    for k in range(9)], brilhos=5, seed=3)
    O2.sem_osso("so", "padeira", (1.55, 0.1, 0), rot=-28, curva=1.4, seed=9)
    cam((0.0, -5.2, 0.95), (0.0, 0.0, 0.55), 28)
elif MODO.startswith("cabeca"):
    # a cabeça de perto: cabeca_f (frente), cabeca_3q (três quartos), cabeca_p (perfil), cabeca_m (rapaz do mercado, três quartos)
    base("#6e7068", None)
    ch, rot = {"cabeca_f": ("padeira", 0), "cabeca_3q": ("padeira", -42), "cabeca_p": ("padeira", -90), "cabeca_m": ("mercado", -30)}[MODO]
    h = O2.sem_osso("so", ch, (0, 0, 0), rot=rot, curva=1.0, seed=2, bracos_frente=False)
    h.cabeca.rotation_euler = (math.radians(-26), 0, 0)
    bpy.context.view_layer.update()
    c = h.cabeca.matrix_world.translation + Vector((0, 0, h.R * 1.15))
    cam((c.x, c.y - 2.7, c.z), (c.x, c.y, c.z), 85, fstop=22)
elif MODO == "olhos":
    # o vivo e o Sem-Osso de perto: o olho branco aceso e o olho cinza apagado
    base("#6e7068", None)
    v = E3.faz("eu", "eu"); v.raiz.location = (-0.24, 0, -1.1); v.rosto(boca="reta", lid=0.2)
    s = O2.sem_osso("so", "padeira", (0.24, 0, -1.1), rot=0, curva=0.0)
    s.pose(cabeca=-4, alt=0.86)
    cam((0.0, -2.6, 0.45), (0.0, 0, 0.42), 50)
elif MODO == "esqueleto":
    # o que fica: o esqueleto sentado contra o pilar (a mesma pose do ep. 1) e a gosma indo embora pelo chão
    base("#6e7068", "#5e6058")
    O3.caixa("pilar", (0.45, 0.45, 2.6), O3.M("#8c8d84", "#6e6f68"), None, (0, 0.35, 1.3), chanfro=0.02)
    O3B.esqueleto3d("esq_a", (0.0, -0.1, -0.8), (0, 0, 8), quadril=(-88, -84), joelho=(4, 14), ombro=(6, 10), abre=(14, 20), cotovelo=(-10, -30), cabeca=28, queixo=22, poeira=0.3)
    O2.mancha("rastro", [(0.25 + 0.09 * k, -0.25 - 0.025 * k - 0.04 * math.sin(k * 0.6)) for k in range(18)], larg=0.13, seed=4)
    O2.gosma("bolo", [(1.85, -0.75, 0.0, 1.0, (0.16, 0.13, 0.04)), (1.85, -0.75, 0.08, 1.0, (0.1, 0.09, 0.09))], brilhos=4, seed=4)
    cam((1.1, -3.4, 1.0), (0.45, 0.0, 0.5), 35)
elif MODO == "grupo":
    base("#8a8578", "#77756c")
    ordem = ["lider", "radio", "cochicho", "taco", "jovem", "solto", "careca", "trancas", "menino"]
    for i, k in enumerate(ordem):
        h = O2.faz_grupo(k, k)
        x = -3.6 + i * 0.8
        h.raiz.location = (x, 0, 0); h.raiz.rotation_euler.z = math.radians(-6 + 3 * (i % 3))
        h.pose(ombro=(-4, 4), cotovelo=(-12, -12), abre=(6, 6))
        h.rosto(boca="reta", lid=0.35)
        if k == "taco":
            h.pose(ombro=(-4, -30), cotovelo=(-12, -60), abre=(6, 10))
            bpy.context.view_layer.update()
            O2.taco3d("taco_obj", tuple(h.punho["B"].matrix_world.translation + Vector((0, -0.04, -0.06))), rot=(-20, 0, 0))
        if k == "lider":
            h.rosto(boca="reta", lid=0.5)
    e = E3.faz("eu", "eu"); e.raiz.location = (3.75, 0.3, 0); e.pose(ombro=(-4, 4), cotovelo=(-12, -12), abre=(6, 6)); e.rosto(boca="reta", lid=0.2)
    cam((0.05, -9.0, 1.3), (0.05, 0, 0.95), 24)
elif MODO == "galpao":
    base("#3a3c38", None)
    O2.galpao3d("galpao")
    O2.tambor_fogo3d("tambor", (0.2, 0.6, 0))
    O3.mesa3d("mesa", (-2.4, 2.2, 0), tam=(1.4, 0.7, 0.78))
    O2.radio3d("radio", (-2.6, 2.25, 0.78), 1.0)
    O2.fone_mesa3d("fone", (-2.05, 2.1, 0.78))
    O2.lanterna3d("lant", (-1.9, 2.0, 0.81), 1.0, rot=(0, 0, 30), facho=False)
    O2.taco3d("taco", (2.6, 3.5, 0.0), rot=(14, 0, 0))
    for k, (x, y) in enumerate(((-1.0, -0.4), (1.3, -0.2), (0.4, 1.9))):        # caixotes de sentar em volta do fogo
        O3.caixa(f"caixote{k}", (0.5, 0.4, 0.42), O3.M("#7a6448", "#5a4632"), None, (x, y, 0.21), chanfro=0.015)
    cam((-3.9, -3.7, 1.7), (-0.4, 2.4, 1.6), 20)
elif MODO == "objetos":
    base("#8a8578", "#77756c")
    O3.mesa3d("mesa", (0, 0.1, 0), tam=(2.4, 0.9, 0.78))
    O2.radio3d("radio", (-0.75, 0.15, 0.78), 1.0)
    O2.fone_mesa3d("fone", (-0.25, -0.05, 0.78))
    O2.lanterna3d("lant", (0.2, -0.1, 0.81), 1.0, rot=(0, 0, -25), facho=False)
    O2.taco3d("taco", (0.55, 0.05, 0.81), rot=(90, 0, 70))
    O3B.quadro_giz3d("giz", (-0.55, 0.75, 1.55), 0.8, dias=14, colunas=4)
    O2.mapa3d("mapa", (0.6, 0.75, 1.6), 0.75)
    O3.caixa("parede", (4.0, 0.2, 3.0), O3.M("#9a968a", "#7a766c"), None, (0, 0.88, 1.5), chanfro=0.0, contorno=0.0)
    cam((0.0, -3.0, 1.5), (0.0, 0.3, 1.15), 35)
elif MODO == "torre":
    # de noite, do telhado do galpão: a cidade em ruínas e, lá longe no morro, a torre com a luz vermelha
    base("#141a26", None)
    cena.poly_mesh("chao", [(-400, -60, 0), (400, -60, 0), (400, 900, 0), (-400, 900, 0)], props.FM("#1c2028"))
    import random
    rnd = random.Random(6)
    for k in range(110):                                                     # ruínas: blocos de alturas quebradas, mais baixos que o telhado
        x = rnd.uniform(-160, 160); y = rnd.uniform(30, 380); w = rnd.uniform(5, 14); hgt = rnd.uniform(3, 11 + y * 0.03)
        O3.caixa(f"pred{k}", (w, rnd.uniform(5, 12), hgt), O3.M("#262b35", "#1d212a", "#3a404c"), None, (x, y, hgt / 2), chanfro=0.0, contorno=0.0,
                 rot=(0, rnd.uniform(-6, 6), rnd.uniform(-8, 8)))
    O3.torno("morro", [(260, 0), (220, 30), (140, 60), (60, 78), (0, 82)], O3.M("#20242d", "#181b22", "#2e333e"), None, (40, 520, 0), seg=64, contorno=0.0)
    O2.torre3d("torre", (40, 520, 82), H=120)
    O3.caixa("telhado", (8.0, 6.0, 0.3), O3.M("#2e3036", "#24262b", "#4a4c54"), None, (0, -2.0, 13.85), chanfro=0.02)
    O3.caixa("parapeito", (8.0, 0.35, 0.7), O3.M("#3a3c40", "#2a2c30", "#5a5c64"), None, (0, 0.8, 14.3), chanfro=0.02)
    cam((0.0, -3.0, 15.6), (36, 520, 115), 35, fstop=22)
render()
