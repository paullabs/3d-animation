"""Provas dos objetos 3D de "O abrigo". blender -b -P teste3d_abrigo.py -- MODO SAIDA.png [--scale 0.5]
MODO = objetos | maos | porta | rua | rua_morta"""
import os, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy, lib
from lib import *
from mathutils import Vector
import cena, props, sets4 as S
import objetos3d_abrigo as O3, cidade3d as C3, elenco3d_abrigo as E3
import story_abrigo as SA
from story_abrigo import camera
from prod_abrigo import pal, mundo, halo, ceu

a = sys.argv[sys.argv.index("--") + 1:]
MODO, OUT = a[0], a[1]
k = float(a[a.index("--scale") + 1]) if "--scale" in a else 0.5
W, H = (int(1080 * k), int(1920 * k)) if MODO != "objetos" else (int(3000 * k), int(1700 * k))
lib.reset(W, H, 24, 16)
sc = bpy.context.scene; sc.frame_start = sc.frame_end = 1

if MODO == "objetos":
    bpy.context.scene.world.node_tree.nodes["Background"].inputs[0].default_value = (*srgb("#9a9c8e"), 1)
    cena.poly_mesh("chao", [(-30, -30, 0), (30, -30, 0), (30, 30, 0), (-30, 30, 0)], props.FM("#7a7c6e"))
    props.skywall("parede", 6.0, [(-2, "#9a9c8e"), (10, "#9a9c8e")], -40, 40, -2, 20)
    O3.porta3d("porta", (-4.6, 1.0, 0), 1.0, aberta=0.0)
    O3.bicicleta3d("bici", (-2.2, 0.4, 0), 1.0); bpy.data.objects["bici"].rotation_euler.z = math.radians(-20)
    O3.sirene3d("sirene", (0.2, 2.0, 0), 0.8)
    O3.estante3d("est", (2.2, 1.0, 0), 1.3)
    O3.galao3d("gal1", (3.6, 0.0, 0), 2.0, nivel=1.0); O3.galao3d("gal2", (4.2, 0.0, 0), 2.0, nivel=0.15)
    O3.gaiola3d("gai", (5.4, 0.2, 0), 1.6, vazia=True)
    O3.mesa3d("mesa", (-0.9, -1.8, 0), (1.6, 0.9, 0.78))
    O3.prato3d("pr1", (-1.4, -1.8, 0.78), 2.2, "cheio"); O3.prato3d("pr2", (-0.9, -1.8, 0.78), 2.2, "colher"); O3.prato3d("pr3", (-0.4, -1.8, 0.78), 2.2, "carne")
    O3.cadeira3d("cad", (1.0, -1.6, 0), rot=-20)
    O3.cama3d("cama", (3.4, -1.9, 0), dobrada=False)
    for kk, ac in enumerate((True, False)):
        O3.lampada3d(f"lamp{kk}", (5.4 + 0.5 * kk, -1.2, 1.6), 1.6, acesa=ac)
    md = O3.Mao3D("mao_a", "dir", None, (6.6, -1.6, 1.0), 2.4); md.raiz.rotation_euler = (math.radians(-60), 0, math.radians(20)); md.pose("aberta")
    mf = O3.Mao3D("mao_f", "esq", None, (7.4, -1.6, 1.0), 2.4); mf.raiz.rotation_euler = (math.radians(-60), 0, math.radians(-20)); mf.pose("fechada")
    cam = camera((1.2, -11.5, 5.0), (1.2, 0.0, 0.9), 26, fstop=11.0)
elif MODO == "maos":
    p = pal("rua"); mundo(p); ceu(p, 60.0, topo="#7f857b", meio="#b6b4a2")
    C3.rua3d(p, -8, 16.5, carros=False)
    C3.rua3d(p, 24, 56, carros=False, seed=9)                       # a rua continua depois do bunker (fundo)
    C3.entrada_bunker("bunker", (0, 17.0, 0), 1.0, aberta=0.9)
    for yv in (10.0, 30.0):
        S.neblina(p, yv, 0.06, z1=40.0)
    SA.corre("ze", "ze", -0.35, 9.0, fase=3); SA.corre("lu", "lu", 0.55, 7.4, fase=6)
    SA.corre("padeira", "padeira", 1.6, 12.5, fase=1, inclina=8); SA.corre("mercado", "mercado", -1.4, 14.0, fase=5)
    by = 2.0
    b = O3.bicicleta3d("bici", (0.0, by, 0.0), 1.0); b.rotation_euler.z = math.radians(90)
    cam = camera((0.0, by - 0.42, 1.48), (0.0, 17.0, 1.25), 22, fstop=8.0, foco=(0.0, 9.0, 1.2), roll=-2)
    for lado, sy in (("esq", -1), ("dir", 1)):
        m = O3.Mao3D("mao_" + lado, lado, None, (sy * 0.25, by + 0.30, 1.01), 1.0)
        m.raiz.rotation_euler = (math.radians(-12), 0, math.radians(-6 * sy)); m.pose("segura")
elif MODO == "entrada":
    p = pal("rua"); mundo(p); ceu(p, 60.0, topo="#7f857b", meio="#b6b4a2")
    C3.rua3d(p, -8, 22, carros=False)
    C3.entrada_bunker("bunker", (0, 23.0, 0), 1.0, aberta=0.9)
    SA.corre("ze", "ze", -0.05, 22.2, fase=3)
    cam = camera((2.6, 15.5, 1.1), (0.0, 23.0, 1.6), 24, fstop=5.6, foco=(0.0, 22.5, 1.3))
elif MODO == "porta":
    import cenario3d_abrigo as CA
    p = pal("abrigo"); wy = 4.6
    CA.sala3d(p, wy=wy, x0=-2.7, x1=2.7, porta_x=0.0, porta_s=1.15)
    O3.porta3d("porta", (0, wy - 0.1, 0), 1.15)
    CA.fora_porta(p, 0.0, wy)
    ze = SA.ator3("ze", "ze", 0.1, wy - 0.95, rot=180)
    cam = camera((0.38, wy - 1.75, 1.95), (0.0, wy - 0.1, 2.08), 50, fstop=2.2, foco=(0.0, wy - 0.12, 2.06))
elif MODO in ("cctv1", "cctv2"):
    import cenario3d_abrigo as CA
    p = pal("escuro"); wy = 5.5
    CA.sala3d(p, wy=wy)
    O3.estante3d("est", (-2.7, wy - 0.3, 0), 1.6, nivel=0.15)
    O3.galao3d("gal1", (-1.5, wy - 0.3, 0), 1.6, nivel=0.3); O3.galao3d("gal2", (-1.1, wy - 0.3, 0), 1.6, nivel=0.0)
    O3.mesa3d("mesa", (-0.6, 2.6, 0), (2.0, 0.9, 0.78))
    O3.cadeira3d("cad1", (-1.85, 2.6, 0), rot=-90); O3.cadeira3d("cad2", (0.65, 2.6, 0), rot=90)
    O3.cama3d("cama", (2.2, 4.3, 0), dobrada=False)
    for kk in range(3):
        caixa_ = O3.caixa(f"cx{kk}", (0.6, 0.45, 0.4), O3.M("#6b5a3e", "#4e4130", "#a8916a"), None, (2.9, 0.6 + 0.5 * kk, 0.2 + 0.4 * (kk == 1)), chanfro=0.02)
    for kk, (x, ac) in enumerate(((-0.6, True), (0.9, False), (-2.1, False))):
        O3.lampada3d(f"lamp{kk}", (x, 2.6, 2.35), 1.0, acesa=ac, fio=0.4)
    cena.ground_disc("poca_luz", 2.0, 1.6, cena.amat("poca_luz_m", "#d9b66a", 1.0, 0.22, ("radial", 1.2)), (-0.6, 2.6, 0.006), n=40)
    if MODO == "cctv1":
        # os meses, calados: cada um num canto, ninguém se olha
        z = SA.sentado("ze", "ze", -1.85, 2.6, rot=90, ombro=(-30, -28), cotovelo=(-70, -72)); z.rosto(boca="reta", lid=0.75); z.cabeca.rotation_euler = (math.radians(22), 0, 0)
        ri = SA.ator3("rita", "rita", -2.9, 3.6, rot=60, pose=dict(quadril=(-115, -115), joelho=(140, 140), ombro=(-60, -60), cotovelo=(-80, -80), alt=0.28, cabeca=20), rosto=dict(lid=0.8))
        lu = SA.ator3("lu_fraca", "lu", 2.3, 4.3, rot=0, pose=dict(ombro=(-6, 4), cotovelo=(-10, -10)), rosto=dict(lid=0.85))
        lu.raiz.rotation_euler = (math.radians(-90), 0, math.radians(90)); lu.raiz.location = (2.95, 4.3, 0.58)
        cam = camera((-3.05, 1.25, 2.5), (-0.35, 3.95, 0.65), 16, fstop=16.0)
    else:
        # a briga: o Zé e a Lu de pé, frente a frente na mesa; a Rita encolhida ao fundo
        z = SA.ator3("ze", "ze", -1.0, 3.3, rot=-70, pose=dict(ombro=(-70, 10), cotovelo=(-40, -12), abre=(20, 6), tronco=-8, cabeca=-4), rosto=dict(boca="o", lid=0.2))
        lu = SA.ator3("lu_fraca", "lu", 0.25, 3.0, rot=105, pose=dict(ombro=(-35, -40), cotovelo=(-60, -70), abre=(12, 12), tronco=-4), rosto=dict(boca="o", lid=0.3))
        ri = SA.ator3("rita", "rita", -2.9, 4.7, rot=40, pose=dict(quadril=(-115, -115), joelho=(140, 140), ombro=(-60, -60), cotovelo=(-80, -80), alt=0.28, cabeca=25), rosto=dict(lid=0.8))
        cam = camera((2.25, 1.05, 2.5), (-0.65, 3.45, 0.95), 16, fstop=16.0)
elif MODO in ("cmp_fora_fechada", "cmp_fora_aberta"):
    p = pal("rua"); mundo(p); ceu(p, 60.0, topo="#7f857b", meio="#b6b4a2")
    C3.rua3d(p, -8, 22, carros=False)
    C3.entrada_bunker("bunker", (0, 23.0, 0), 1.0, aberta=(0.0 if MODO.endswith("fechada") else 0.9))
    if MODO.endswith("aberta"):
        SA.corre("ze", "ze", -0.05, 22.2, fase=3)
    cam = camera((0.35, 18.0, 1.5), (0.0, 23.0, 1.5), 28, fstop=5.6, foco=(0.0, 23.0, 1.4))
elif MODO in ("cmp_dentro_fechada", "cmp_dentro_aberta"):
    import cenario3d_abrigo as CA, elenco_abrigo as EA
    p = pal("abrigo"); wy = 4.6
    CA.sala3d(p, wy=wy, x0=-2.7, x1=2.7, porta_x=0.0, porta_s=1.15)
    O3.porta3d("porta", (0, wy - 0.1, 0), 1.15, aberta=(0.0 if MODO.endswith("fechada") else 0.9), lado="dentro")
    # do lado de fora da porta, a MESMA rua (a câmera olha de dentro do bunker para a rua)
    pr = pal("rua")
    import prod_abrigo as PA_
    props.skywall("ceu_fora", wy + 45.0, [(-2.0, "#b6b4a2"), (6.0, "#9aa094"), (14.0, "#7f857b"), (120.0, "#7f857b")], -160, 160, -2.0, 120.0)
    rua_ = C3.rua3d(pr, wy + 0.4, wy + 40.0, carros=False, seed=5)
    for o in bpy.data.objects:                                                # a rua de fora fica atrás da parede do fundo
        pass
    for yv in (wy + 10.0, wy + 24.0):
        S.neblina(pr, yv, 0.08, z1=40.0)
    if MODO.endswith("aberta"):
        SA.corre("ze", "ze", 0.0, wy + 1.2, rot=0, fase=2, inclina=4)
        SA.corre("lu", "lu", 0.35, wy + 4.5, rot=0, fase=5)
        SA.corre("padeira", "padeira", -0.5, wy + 9.0, rot=0, fase=1)
    cam = camera((0.25, wy - 4.6, 1.45), (0.0, wy, 1.4), 24, fstop=5.6, foco=(0.0, wy - 0.2, 1.3))
else:
    p = pal("rua" if MODO == "rua" else "cinza"); mundo(p); ceu(p, 52.0, topo="#7f857b" if MODO == "rua" else "#a9a597", meio="#b6b4a2" if MODO == "rua" else "#cfc9b4")
    C3.rua3d(p, -8, 46, ruina=(MODO != "rua"), poeira=(0.0 if MODO == "rua" else 0.6))
    for yv in (14.0, 28.0, 40.0):
        S.neblina(p, yv, 0.08 if MODO == "rua" else 0.2, z1=40.0)
    cam = camera((0.4, -6.5, 1.55), (0.0, 30.0, 3.2), 22, fstop=11.0)
O3.olha_camera(cam)
for pre in [x for x in os.environ.get('HIDE', '').split(',') if x]:
    for o in bpy.data.objects:
        if o.name.startswith(pre):
            o.hide_render = True
sc.render.filepath = OUT; bpy.ops.render.render(write_still=True)
