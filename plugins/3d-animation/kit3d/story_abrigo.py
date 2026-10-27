"""Storyboard renderizado de "O abrigo" (decupagem: personagem/abrigo/decupagem-cinema.md): um quadro parado por plano, com a lente,
a posição, o foco e a profundidade de campo do plano de verdade. Usa as mesmas peças do prod_abrigo (cenários, elenco 2D e 3D, mãos do POV).
blender -b -P story_abrigo.py -- PLANO SAIDA.png [--scale 0.5] [--samples 16]      (PLANO = 1A, 1B, ... ; --list mostra todos)"""
import os, sys, math, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy, lib
from lib import *
from mathutils import Vector
import cena, props, luz, frente, sets4 as S, unidades as UN, ambiente3d as AM
import elenco_abrigo as EA, elenco3d_abrigo as E3, objetos_abrigo as OA
import prod_abrigo as PA
from prod_abrigo import pal, mundo, halo, rua, ceu, morro_abrigo, sala_abrigo, lampadas, mesa_cena, maos, troca_mao, SALA
from heroi3d import corrida
from prod_pcc4 import Timeline, _mix
from char2d import rrect
from puppet2d import circle, stroke, smooth

PLANOS = {}


def plano(nome, lente, texto):
    def deco(fn):
        PLANOS[nome] = (lente, texto, fn); return fn
    return deco


# ---------------------------------------------------------------- câmera e peças comuns
def camera(loc, alvo, lens, fstop=8.0, foco=None, roll=0.0, clip=0.03):
    """câmera de verdade do plano: lente em mm (sensor 24 mm na largura), mira, rolagem e foco (ponto ou distância)"""
    sc = bpy.context.scene
    cd = bpy.data.cameras.new("cam"); cam = bpy.data.objects.new("cam", cd); sc.collection.objects.link(cam); sc.camera = cam
    cd.lens = lens; cd.sensor_fit = "HORIZONTAL"; cd.sensor_width = 24; cd.clip_start = clip
    cam.location = loc
    e = (Vector(alvo) - Vector(loc)).to_track_quat("-Z", "Y").to_euler(); e.rotate_axis("Z", math.radians(roll)); cam.rotation_euler = e
    cd.dof.use_dof = True; cd.dof.aperture_fstop = fstop
    alvo_f = foco if foco is not None else alvo
    cd.dof.focus_distance = alvo_f if isinstance(alvo_f, (int, float)) else (Vector(alvo_f) - Vector(loc)).length
    return cam


def ator2(fn, nome, view, x, y, z=0.0, p=None, espelho=False, face=None, intent=None):
    """personagem 2D parado no quadro 1 (pose e rosto)"""
    p = p or pal("abrigo")
    H = fn(nome, view, rim=p["borda"])
    w = empty(nome + "_inv", None, (x, y, z)); H.root.parent = w
    e = EA.ESCALA.get(nome, 1.0); w.scale = (-e if espelho else e, e, e)
    tl = Timeline(H, 1, 24, 24); tl.stand(1, 24, 0.0)
    tl.face(1, 1.0, **(face or dict(lid="esperto", lidv=0.45, brow=-8, mouth="reta")))
    if intent:
        tl.intent(1, **intent)
    PA._finish(H, tl, 1, 24)
    if view == "front":
        frente.bracos(H, 1, 24, [(1, dict(shF=5, elF=0, shB=5, elB=0))])
    cena.contact_shadow(H, dict(shadow=_mix(p["chao"], "#000000", 0.4)))
    return H, w


def ator3(chave, nome, x, y, rot=0.0, pose=None, rosto=None, p=None):
    """personagem 3D parado: pose (dict do Heroi3D.pose), rosto (boca, lid)"""
    H = E3.faz(chave, nome + "_inv")
    H.pose(**(pose or dict(ombro=(-5, 7), cotovelo=(-14, -10), abre=(5, 5))))
    H.raiz.location = (x, y, 0); H.raiz.rotation_euler.z = math.radians(rot)
    r = dict(boca="reta", lid=0.4); r.update(rosto or {}); H.rosto(**r)
    cena.ground_disc(nome + "_sb", 0.42, 0.26, cena.amat(nome + "_sb_m", "#000000", 1.0, 0.38, ("radial", 1.1)), (x, y + 0.05, 0.003), n=32)
    return H


def corre(chave, nome, x, y, rot=180.0, fase=3, inclina=12):
    """personagem 3D no meio da passada de corrida"""
    ch = corrida(1, 30, (x, y, 0), (x, y + 0.001, 0), rot=rot, ciclo=12, inclina=inclina, arranque=0.0, freia=0.0)
    d = dict(ch[fase][1]); d["pos"] = (x, y, 0)
    return ator3(chave, nome, x, y, rot, pose=d)


def maos_em(H, alvo_e, alvo_d, passos=4):
    """move a raiz do boneco 3D para que o meio das duas mãos caia no meio dos dois alvos (x, y) e acerta a altura pelo quadril"""
    for _ in range(passos):
        bpy.context.view_layer.update()
        me = H.punho["F"].matrix_world.translation; md = H.punho["B"].matrix_world.translation
        m = (me + md) / 2; t = (Vector(alvo_e) + Vector(alvo_d)) / 2
        d = t - m
        H.raiz.location.x += d.x; H.raiz.location.y += d.y; H.quadril.location.z += d.z


def rua_viva(p, yf=46.0):
    mundo(p)
    ceu(p, yf + 6, topo="#7f857b", meio="#b6b4a2")
    rua(p, -8.0, yf, acesas=0.04)
    for yv in (14.0, 28.0, 40.0):
        S.neblina(p, yv, 0.10, z1=40.0)
    morro_abrigo(p, yf)


def rua_morta(p, yf=46.0):
    """a mesma rua depois: as fachadas viram ruínas, a cinza cai, o céu é branco sujo"""
    mundo(p)
    ceu(p, yf + 6, topo="#a9a597", meio="#cfc9b4")
    PA.ruinas_rua(p, -8.0, yf + 4)
    for yv, al in ((6.0, 0.12), (14.0, 0.18), (26.0, 0.26), (40.0, 0.34)):
        S.neblina(p, yv, al, z1=40.0)
    cena.dust(p, 120, (-5, 5), 30, seed=3, color="#e8e2cc", alpha=0.85, y_range=(-2.0, 14.0), z_range=(0.2, 4.5), size=(0.008, 0.02))


def janela_escura(nome="porta"):
    folha = bpy.data.objects[nome + "_folha"]
    props.poly(nome + "_jan_esc", circle(0.0, 1.8, 0.135, 28), "#0b1210", -0.056, folha)


# ====================================================================== 1. A corrida
@plano("1A", "20 mm, de baixo", "Quando a sirene tocou")
def p1A():
    p = pal("rua"); rua_viva(p)
    OA.sirene("sirene", (3.0, 7.0, 0.0), 1.0)
    halo("sirene_gl", 3.0, 6.95, 3.3, 0.9, "#c8342c", 0.55)
    corre("lu", "lu", 0.4, 15.0, fase=2)
    camera((2.25, 4.9, 0.85), (3.0, 7.0, 2.85), 20, fstop=4.0, foco=(3.0, 7.0, 2.85), roll=-6)


@plano("1B", "14 mm, no chão", "eu larguei a bicicleta")
def p1B():
    p = pal("rua"); rua_viva(p)
    b = OA.bicicleta("bici", (0.4, 2.6, 0.0), 1.0, cor="#8e3a30"); b.rotation_euler = (math.radians(55), 0, math.radians(-10))
    corre("ze", "ze", -0.5, 11.0, fase=3); corre("lu", "lu", 0.7, 9.5, fase=6)
    bpy.context.view_layer.update()
    hub = bpy.data.objects["bici_cubo1"].matrix_world.translation.copy()
    camera((hub.x + 0.55, hub.y - 0.75, 0.16), (hub.x - 0.6, hub.y + 2.5, 0.35), 14, fstop=2.8, foco=(hub.x, hub.y, hub.z), roll=4)


@plano("1C", "24 mm, POV correndo", "e corri pro abrigo, no fim da rua")
def p1C():
    p = pal("rua"); rua_viva(p)
    corre("ze", "ze", -0.55, 24.5, fase=3); corre("lu", "lu", 0.75, 22.6, fase=6)
    cam = camera((0.05, 17.5, 1.62), (0.0, 46.0, 1.35), 24, fstop=8.0, foco=(0.0, 24.0, 1.3), roll=2.5)
    r, mE, mD, _ = maos(cam, "maos", escala=0.5, d=0.5, y=-0.33)
    troca_mao("maos", "esq", -10, "fechada"); troca_mao("maos", "dir", -10, "fechada")
    mE.location = (-0.17, 0, 0.09); mD.location = (0.17, 0, -0.03)


@plano("1D", "35 mm, contraplano da porta", "O céu ficou branco na mesma hora")
def p1D():
    p = pal("rua"); mundo(p)
    rua(p, -12.0, 46.0, acesas=0.0)
    props.skywall("ceu_tras", -14.0, [(-2.0, "#fbf8ee"), (5.0, "#f4f0e2"), (14.0, "#e6e1cf"), (120.0, "#c9c4b0")], -160, 160, -2.0, 120.0)
    halo("clarao", 0.0, -13.0, 5.0, 22.0, "#ffffff", 0.95)
    for yv, al in ((8.0, 0.35), (16.0, 0.3), (26.0, 0.22), (34.0, 0.14)):
        S.neblina(p, yv, al, cor="#f6f2e4", z1=40.0)
    corre("ze", "ze", -0.45, 39.0, rot=180, fase=3); corre("lu", "lu", 0.55, 37.2, rot=180, fase=6)
    for s_ in (-1, 1):                                        # o batente da porta emoldura o plano (de dentro do abrigo)
        cena.poly_mesh(f"bat{s_}", [(s_ * 0.4, 45.2, 0.0), (s_ * 1.6, 45.2, 0.0), (s_ * 1.6, 45.2, 3.0), (s_ * 0.4, 45.2, 3.0)], props.FM("#1c2420"))
    cena.poly_mesh("bat_topo", [(-1.6, 45.2, 2.0), (1.6, 45.2, 2.0), (1.6, 45.2, 3.0), (-1.6, 45.2, 3.0)], props.FM("#1c2420"))
    camera((0.1, 46.6, 1.25), (0.0, 30.0, 1.5), 35, fstop=4.0, foco=(0.0, 38.0, 1.4))


# ====================================================================== 2. A porta
def foyer(p, aberta=0.0, luz=True, wy=4.6):
    sala_abrigo(p, wy=wy, x0=-2.7, x1=2.7, pilastra=0)
    OA.porta_abrigo("porta", (0, wy - 0.08, 0), 1.15, aberta=aberta, luz_fora="#f4f1e6")
    if luz:
        halo("porta_gl", 0.0, wy - 0.1, 1.2, 2.2, "#f4f1e6", 0.5)
        luz_ = __import__("luz"); luz_.feixe("feixe_porta", 0.0, wy - 0.5, 0.0, 2.6, 1.8, 0.9, "#f4f1e6", forca=0.9, frames=30, poeira=30, seed=12)
    lampadas(wy - 0.3, 1, x=-1.3, s=1.2, nome="lampA")
    return wy


@plano("2A", "24 mm, dolly baixo", "O Zé foi o último a entrar")
def p2A():
    p = pal("abrigo"); wy = foyer(p, aberta=1.0)
    corre("ze", "ze", 0.15, wy - 0.7, rot=0, fase=2, inclina=4)
    ator2(EA.lu, "lu", "q", -1.25, 0.9, face=dict(wide=0.3, browup=0.015, mouth="pequena", look=(1.0, 0.0)))
    ator2(EA.rita, "rita", "q", -1.85, 1.9, face=dict(lid="esperto", lidv=0.35, browup=0.02, mouth="reta", look=(1.0, 0.1)))
    camera((-0.35, -1.7, 1.0), (0.1, wy, 1.25), 24, fstop=4.0, foco=(0.15, wy - 0.7, 1.2))


@plano("2B", "14 mm, colada na roda", "e trancou a porta")
def p2B():
    p = pal("abrigo"); wy = foyer(p, aberta=0.13, luz=False)
    halo("fresta_gl", -0.6, wy - 0.15, 1.3, 0.9, "#f4f1e6", 0.55)
    ze = ator3("ze", "ze", 0.0, wy - 0.75, rot=180, pose=dict(ombro=(-92, -92), cotovelo=(-18, -18), abre=(12, 12), tronco=-4))
    ze.fecha_mao("F"); ze.fecha_mao("B")
    roda = bpy.data.objects["porta_roda"]; roda.rotation_euler = (0, math.radians(-40), 0)
    bpy.context.view_layer.update()
    c = roda.matrix_world.translation
    maos_em(ze, (c.x - 0.2 + 0.15, c.y - 0.06, c.z + 0.12), (c.x + 0.2 + 0.15, c.y - 0.06, c.z - 0.05))
    camera((0.62, wy - 0.78, 1.5), (0.05, wy - 0.12, 1.3), 14, fstop=2.8, foco=(0.1, wy - 0.15, 1.32))


@plano("2C", "50 mm, foco nos rostos", "o povo batia e gritava")
def p2C():
    p = pal("abrigo"); wy = foyer(p, aberta=0.0, luz=False)
    folha = bpy.data.objects["porta_folha"]
    OA.rostos_janela("jan", folha, z=1.8)
    halo("jan_gl", 0.0, wy - 0.16, 2.07, 0.45, "#f4f1e6", 0.5)
    ze = ator3("ze", "ze", 0.08, wy - 0.85, rot=180, pose=dict(ombro=(-6, 6), cotovelo=(-12, -12)))
    t = lib.text("bang", "BANG!", 0.13, props.FM("#e8e0c4"), None, (0.12, wy - 0.3, 2.32), lib.font(), outline=0.008); t.rotation_euler = (math.pi / 2, 0, math.radians(-8))
    camera((0.36, wy - 1.75, 1.82), (0.0, wy - 0.15, 2.05), 50, fstop=2.0, foco=(0.0, wy - 0.15, 2.07))


@plano("2D", "85 mm, rosto", "Ele não abriu.")
def p2D():
    p = pal("abrigo"); wy = foyer(p, aberta=0.0, luz=False)
    janela_escura()
    ze = ator3("ze", "ze", 0.0, wy - 1.0, rot=0, pose=dict(ombro=(-4, 6), cotovelo=(-12, -12), cabeca=10), rosto=dict(lid=0.62))
    camera((0.06, wy - 2.75, 1.62), (0.0, wy - 1.0, 1.6), 85, fstop=2.0, foco=(0.0, wy - 1.12, 1.62))


# ====================================================================== 3, 4 e 5. Dentro do abrigo
def abrigo(p, wy=5.5, nivel=1.0, lamp=3, dia=1, galao=1.0, mesa=True):
    """a sala principal (a mesma em todas as cenas): estante à esquerda, calendário de giz, galões, a porta no canto, as lâmpadas e a mesa"""
    sala_abrigo(p, wy=wy)
    OA.prateleira("est", (-2.45, wy - 0.15, 0.0), 1.9, nivel=nivel)
    OA.quadro_giz("giz", (-0.4, wy - 0.12, 1.45), 1.7, dias=dia, rotulo=f"DIA {dia}")
    OA.galao("galao_a", (1.55, wy - 0.4, 0.0), 1.7, nivel=galao); OA.galao("galao_b", (1.95, wy - 0.4, 0.0), 1.7, nivel=galao)
    OA.porta_abrigo("porta", (3.05, wy - 0.1, 0), 0.95, aberta=0.0)
    lampadas(wy - 1.6, lamp, x=-0.3, nome="lamp")
    if mesa:
        mesa_cena(p)
    return wy


@plano("3A", "20 mm, travelling na estante", "Lá dentro tinha comida")
def p3A():
    p = pal("abrigo"); wy = abrigo(p)
    camera((-3.05, wy - 1.25, 1.05), (-2.35, wy - 0.15, 0.85), 20, fstop=2.8, foco=(-2.6, wy - 0.2, 0.9), roll=-2)


@plano("3B", "20 mm, o travelling chega à água", "água")
def p3B():
    p = pal("abrigo"); wy = abrigo(p)
    camera((1.3, wy - 1.45, 0.62), (1.85, wy - 0.4, 0.42), 20, fstop=2.8, foco=(1.75, wy - 0.45, 0.4))


@plano("3C", "24 mm, a câmera sobe", "e luz")
def p3C():
    p = pal("abrigo"); wy = abrigo(p)
    camera((-0.25, wy - 2.9, 1.45), (-0.3, wy - 1.6, 2.5), 24, fstop=4.0, foco=(-0.3, wy - 1.6, 2.45))


@plano("3D", "35 mm, foco na Pipoca", "Por uns dias, a gente se sentiu seguro")
def p3D():
    p = pal("abrigo"); wy = abrigo(p)
    for k, x in enumerate((-1.0, -0.1, 0.75)):
        OA.mesa_prato(f"pr{k}", (x, 3.15, 0.78), 1.3, None, nivel="cheio")
    OA.porquinha("pipoca", (0.2, 3.0, 0.78), 1.0, vista="lado")
    feliz = dict(eye="feliz", mouth="sorriso", browup=0.012)
    ator2(EA.ze, "ze", "front", -1.0, 3.75, z=-0.3, face=feliz); ator2(EA.lu, "lu", "front", -0.1, 3.75, z=-0.3, face=feliz)
    ator2(EA.rita, "rita", "front", 0.75, 3.75, z=-0.3, face=feliz)
    camera((0.55, 1.4, 1.02), (-0.15, 3.6, 1.05), 28, fstop=2.0, foco=(0.2, 3.0, 0.88))


@plano("4A", "20 mm, o mesmo quadro da 3A", "Só que a comida foi acabando")
def p4A():
    p = pal("abrigo"); wy = abrigo(p, nivel=0.5, dia=14)
    camera((-3.05, wy - 1.25, 1.05), (-2.35, wy - 0.15, 0.85), 20, fstop=2.8, foco=(-2.6, wy - 0.2, 0.9), roll=-2)


@plano("4B", "28 mm, POV de cima", "A gente comia um pouco menos a cada dia")
def p4B():
    p = pal("abrigo"); wy = abrigo(p, dia=18)
    pr = OA.prato("prato", (-0.3, 3.25, 0.783), 1.7, nivel="metade"); pr.rotation_euler = (math.radians(-90), 0, 0)
    cam = camera((-0.3, 2.95, 1.3), (-0.3, 3.28, 0.78), 28, fstop=8.0, foco=(-0.3, 3.28, 0.78))
    r, mE, mD, _ = maos(cam, "maos", escala=0.26, d=0.3, y=-0.2)
    troca_mao("maos", "esq", -10, "fechada"); troca_mao("maos", "dir", -10, "fechada")
    OA.faca("garfo_m", (0.02, -0.01, 0.25), 1.6, parent=bpy.data.objects["maos_inv_dir"]).rotation_euler = (0, math.radians(-70), 0)
    mE.location = (-0.24, 0, 0.0); mD.location = (0.2, 0, 0.06)


@plano("4C", "50 mm, por cima do ombro do Zé", "já dava pra ver que não ia dar pra todo mundo")
def p4C():
    p = pal("abrigo"); wy = abrigo(p, nivel=0.15, dia=21)
    ator2(EA.lu, "lu", "front", -0.95, 3.75, z=-0.3, face=dict(lid="esperto", lidv=0.45, brow=-10, mouth="reta", look=(0.2, -0.4)))
    ator2(EA.rita, "rita", "front", 0.6, 3.75, z=-0.3, face=dict(lid="esperto", lidv=0.35, browup=0.015, mouth="reta", look=(-0.2, -0.4)))
    ze = ator3("ze", "ze", -0.2, 2.35, rot=180, pose=dict(ombro=(-48, -44), cotovelo=(-62, -66), abre=(4, 4), cabeca=14))
    bpy.context.view_layer.update()
    m = (ze.punho["F"].matrix_world.translation + ze.punho["B"].matrix_world.translation) / 2
    cad = OA.caderno("caderno", (m.x, m.y + 0.06, m.z - 0.04), 1.0); cad.rotation_euler = (math.radians(-55), 0, 0)
    camera((0.32, 1.55, 1.78), (-0.15, 3.6, 1.15), 50, fstop=2.0, foco=(m.x, m.y + 0.08, m.z))


@plano("5A", "35 mm, POV no calendário", "Na terceira semana")
def p5A():
    p = pal("abrigo"); wy = abrigo(p, dia=21)
    cam = camera((-0.2, wy - 1.35, 1.55), (-0.4, wy - 0.12, 1.45), 35, fstop=8.0, foco=(-0.4, wy - 0.12, 1.45))
    r, mE, mD, _ = maos(cam, "maos", escala=0.42, d=0.45, y=-0.32)
    troca_mao("maos", "dir", -10, "fechada")
    mE.location = (-0.45, 0, -0.4); mD.location = (0.16, 0, 0.36)
    props.inked("giz_mao", rrect(-0.012, 0.0, 0.012, 0.11, 0.004, 2), "#ece7d8", bpy.data.objects["maos_inv_dir"], loc=(-0.06, -0.012, 0.27), w=0.003)


@plano("5B", "16 mm, rente ao chão", "o banheiro entupiu")
def p5B():
    p = pal("banheiro"); mundo(p); wy = 3.4
    AM.sala("ban", -1.6, 1.6, -6.0, wy, 2.6, dict(parede="#5f6e58", lateral="#46543f", teto="#1a2018", viga="#232b21", chao="#2b3329", linha="#222a20", pilastra="#6a7a62"), piso="lajotas", passo_pilastra=0, passo_viga=0)
    for k in range(7):
        cena.poly_mesh(f"azul{k}", [(-1.6, wy - 0.02, 0.35 * k), (1.6, wy - 0.02, 0.35 * k), (1.6, wy - 0.02, 0.35 * k + 0.012), (-1.6, wy - 0.02, 0.35 * k + 0.012)], props.FM("#7b8a72"))
    OA.privada("vaso", (0.1, wy - 0.3, 0.0), 1.5, transborda=1.0)
    agua = cena.poly_mesh("agua", [(-0.9, wy - 0.3, 0.004), (1.0, wy - 0.3, 0.004), (1.2, 1.2, 0.004), (0.5, 0.15, 0.004), (-0.3, 0.05, 0.004), (-1.1, 0.9, 0.004)], props.FM("#4a5a36"))
    cena.poly_mesh("agua_br", [(-0.2, 2.2, 0.006), (0.45, 2.1, 0.006), (0.35, 1.2, 0.006), (-0.25, 1.3, 0.006)], props.FM("#8a9a6a"))
    for k, (x, z) in enumerate(((0.3, 1.5), (-0.2, 1.75), (0.5, 1.2))):
        OA.mosca2d(f"mosca{k}", (x, wy - 0.6, z), 2.5)
    lampadas(wy - 1.0, 1, x=0.2, s=1.0, nome="lamp_b")
    camera((0.35, 0.55, 0.13), (0.1, wy, 0.7), 16, fstop=4.0, foco=(0.1, wy - 0.4, 0.4))


@plano("5C", "28 mm, dolly para dentro", "e o cheiro ruim tomou conta do abrigo")
def p5C():
    p = pal("banheiro"); wy = abrigo(p, dia=21)
    S.neblina(p, 2.2, 0.26, cor="#8aa83e", z1=6.0); S.neblina(p, 4.4, 0.2, cor="#7a9a3a", z1=6.0)
    nariz = dict(shF=104, elF=138, wrF=-20)
    ator2(EA.ze, "ze", "q", -1.35, 2.6, intent=nariz, face=dict(lid="esperto", lidv=0.7, brow=14, mouth="nervosa", look=(1.0, 0.1)))
    ator2(EA.lu, "lu", "q", 0.9, 2.1, espelho=True, intent=nariz, face=dict(lid="esperto", lidv=0.7, brow=14, mouth="nervosa", look=(1.0, 0.1)))
    ator2(EA.rita, "rita", "front", -0.25, 3.3, face=dict(lid="esperto", lidv=0.85, browup=0.02, mouth="reta", look=(0.0, 0.5)))
    camera((0.0, -0.9, 1.45), (-0.2, 3.0, 1.15), 28, fstop=4.0, foco=(-0.2, 2.6, 1.2))


# ====================================================================== 6. A Pipoca
def caixote_gaiola(p, wy, vazia=False):
    S.caixa3d(p, "caixote", 1.45, 4.3, 0.9, 0.5, d=0.7, cor="#3a342a", tampo="#6b5a3e", aresta="#8a7650")
    if vazia:
        OA.gaiola_vazia("gaiola", (1.45, 4.35, 0.5), 1.7)
    else:
        OA.gaiola("gaiola", (1.45, 4.35, 0.5), 1.7); OA.porquinha("pip_g", (1.35, 4.28, 0.58), 1.5, vista="lado")


@plano("6A", "50 mm, câmera parada", "Aí a Pipoca, a nossa porquinha-da-índia...")
def p6A():
    p = pal("abrigo"); wy = abrigo(p, dia=60, mesa=False); caixote_gaiola(p, wy)
    camera((1.45, 2.55, 0.98), (1.45, 4.35, 0.85), 50, fstop=2.8, foco=(1.45, 4.3, 0.85))


@plano("6A2", "50 mm, o mesmo quadro", "... sumiu.")
def p6A2():
    p = pal("abrigo"); wy = abrigo(p, dia=60, mesa=False); caixote_gaiola(p, wy, vazia=True)
    camera((1.45, 2.55, 0.98), (1.45, 4.35, 0.85), 50, fstop=2.8, foco=(1.45, 4.3, 0.85))


@plano("6B", "24 mm, POV", "Ninguém falou nada")
def p6B():
    p = pal("abrigo"); wy = abrigo(p, dia=60, mesa=False); caixote_gaiola(p, wy, vazia=True)
    bpy.data.objects["gaiola_su"].scale = (0.0001,) * 3
    ator2(EA.ze, "ze", "q", -0.9, 4.3, espelho=True, face=dict(lid="esperto", lidv=0.6, brow=-6, mouth="reta", look=(1.0, 0.3)))
    ator2(EA.lu, "lu", "front", 0.1, 4.7, face=dict(lid="esperto", lidv=0.75, browup=0.012, mouth="reta", look=(0.0, 0.9)))
    cam = camera((1.45, 2.4, 1.5), (0.3, 4.7, 1.2), 24, fstop=8.0, foco=(0.1, 4.6, 1.3))
    r, mE, mD, _ = maos(cam, "maos", escala=0.42, d=0.45, y=-0.32)
    troca_mao("maos", "dir", -10, "fechada")
    mE.location = (-0.6, 0, -0.9); mD.location = (0.12, 0, 0.12)
    OA.sueter_dobrado("su_mao", (0.0, -0.02, 0.28), 1.25, parent=bpy.data.objects["maos_inv_dir"])


@plano("6C", "85 mm, f/1,8, o prato", "naquela noite, tinha carne no jantar")
def p6C():
    p = pal("escuro"); wy = abrigo(p, dia=60, lamp=1)
    OA.mesa_prato("prato_c", (-0.1, 3.15, 0.78), 2.2, None, nivel="carne")
    for k in range(3):
        props.poly(f"vapor{k}", stroke([(0.03 * math.sin(t * 6 + k), t * 0.2) for t in [i / 8 for i in range(9)]], 0.004), "#d8d0bb", 0.0, None,
                   mat=cena.amat(f"vapor{k}_m", "#d8d0bb", 1.0, 0.35)).location = (-0.18 + 0.08 * k, 3.14, 0.9)
    f = OA.faca("garfo", (0.14, 3.1, 0.96), 1.8); f.rotation_euler = (0, math.radians(-120), 0)
    camera((-0.05, 2.25, 1.02), (-0.1, 3.15, 0.86), 85, fstop=1.8, foco=(-0.1, 3.15, 0.86))


@plano("6D", "35 mm, travelling nos rostos", "e ninguém teve coragem de perguntar de quê")
def p6D():
    p = pal("escuro"); wy = abrigo(p, dia=60, lamp=1)
    for k, x in enumerate((-1.0, -0.1)):
        OA.mesa_prato(f"pr{k}", (x, 3.15, 0.78), 1.3, None, nivel="carne")
    OA.mesa_prato("pr_rita", (1.05, 3.15, 0.78), 1.3, None, nivel="carne")
    baixo = dict(lid="esperto", lidv=0.7, brow=-6, mouth="reta", look=(0.0, -0.9))
    ator2(EA.ze, "ze", "front", -1.0, 3.75, z=-0.3, face=baixo, intent=dict(head=14))
    ator2(EA.lu, "lu", "front", -0.1, 3.75, z=-0.3, face=baixo, intent=dict(head=14))
    ator2(EA.rita, "rita", "front", 0.75, 3.75, z=-0.3, face=dict(lid="esperto", lidv=0.75, browup=0.02, mouth="reta", look=(0.0, -0.8)))
    for j in range(2):
        props.poly(f"lagrima{j}", circle(0, 0, 0.011, 8), "#cfd6d0", 0.0, None).location = (0.72 + 0.07 * j, 3.6, 0.98 - 0.08 * j)
    camera((0.55, 2.0, 1.05), (0.6, 3.75, 0.98), 35, fstop=2.2, foco=(0.75, 3.7, 1.0))


# ====================================================================== 7. Os meses
def quarto_meses(p, wy=5.5, dia=200, lamp=1, cama_dobrada=False, lu=True):
    sala_abrigo(p, wy=wy)
    OA.quadro_giz("giz_a", (-1.9, wy - 0.12, 1.45), 2.3, dias=90, rotulo=f"DIA {dia}")
    OA.quadro_giz("giz_b", (0.45, wy - 0.12, 1.45), 2.3, dias=90, rotulo="")
    lampadas(wy - 1.6, lamp, x=-1.0, nome="lamp")
    OA.cama("cama", (1.3, 4.1, 0.0), 1.15, manta="#6e6a4a", dobrada=cama_dobrada)
    OA.cadeira("cad", (-0.05, 4.3, 0.0), 1.3)
    if cama_dobrada:
        OA.jaqueta_pendurada("jaq", (-0.05, 4.22, 0.62), 1.3)
    if lu and not cama_dobrada:
        ator2(EA.lu_fraca, "lu_fraca", "front", 1.55, 4.55, z=-0.78, face=dict(lid="esperto", lidv=0.82, browup=0.012, mouth="reta", look=(-1.0, 0.3)))


@plano("7A", "24 mm, do alto de um canto", "Os meses foram passando, e todo mundo ficou calado")
def p7A():
    p = pal("escuro"); quarto_meses(p)
    S.caixa3d(p, "cx_ze", -2.2, 3.2, 0.8, 0.42, d=0.6, cor="#2a2a24", tampo="#4a4a3c", aresta="#6a6a52")
    ator2(EA.ze, "ze", "q", -2.2, 3.6, z=-0.34, espelho=True, face=dict(lid="esperto", lidv=0.7, brow=-6, mouth="reta", look=(1.0, 0.5)))
    S.caixa3d(p, "cx_r", -0.9, 2.2, 0.7, 0.4, d=0.5, cor="#2a2a24", tampo="#4a4a3c", aresta="#6a6a52")
    ator2(EA.rita, "rita", "front", -0.9, 2.55, z=-0.32, face=dict(lid="esperto", lidv=0.8, browup=0.014, mouth="reta", look=(0.4, 0.8)))
    camera((1.6, 1.3, 1.95), (-1.0, 3.6, 0.85), 24, fstop=8.0, foco=(-0.8, 3.4, 0.9))


@plano("7B", "35 mm, de perfil", "O Zé e a Lu viviam brigando")
def p7B():
    p = pal("escuro"); wy = 5.5
    sala_abrigo(p, wy=wy)
    OA.quadro_giz("giz_a", (-0.6, wy - 0.12, 1.45), 2.3, dias=90, rotulo="DIA 200")
    lampadas(3.0, 1, x=0.4 * 1.2, s=1.2, nome="lamp")
    ator2(EA.ze, "ze", "q", -0.55, 3.4, face=dict(lid="esperto", lidv=0.4, brow=-14, mouth="nervosa", look=(1.0, 0.0)), intent=dict(shF=40, elF=55))
    ator2(EA.lu_fraca, "lu_fraca", "q", 0.55, 3.4, espelho=True, face=dict(lid="esperto", lidv=0.45, brow=-12, mouth="nervosa", look=(1.0, 0.0)), intent=dict(shF=20, elF=40))
    camera((0.05, 1.15, 1.48), (0.0, 3.4, 1.45), 35, fstop=2.8, foco=(0.0, 3.4, 1.45), roll=1.5)


@plano("7C", "28 mm, dolly para a cama", "mas a Lu foi ficando fraca...")
def p7C():
    p = pal("escuro"); quarto_meses(p)
    camera((0.75, 1.75, 1.15), (0.75, 4.2, 0.6), 28, fstop=2.8, foco=(1.55, 4.45, 0.7))


@plano("7C2", "28 mm, o mesmo quadro", "... e um dia morreu.")
def p7C2():
    p = pal("escuro"); quarto_meses(p, cama_dobrada=True)
    camera((0.75, 1.75, 1.15), (0.75, 4.2, 0.6), 28, fstop=2.8, foco=(1.0, 4.2, 0.6))


# ====================================================================== 8. O baralho
def sentado(chave, nome, x, y, rot, alt=0.5, **extra):
    d = dict(quadril=(-88, -88), joelho=(88, 88), tornozelo=(0, 0), ombro=(-40, -40), cotovelo=(-60, -60), abre=(10, 10), alt=alt)
    d.update(extra)
    return ator3(chave, nome, x, y, rot, pose=d)


@plano("8A", "28 mm, de cima, a pino", "Agora o Zé passa o dia jogando baralho sozinho")
def p8A():
    p = pal("escuro"); wy = 5.5
    sala_abrigo(p, wy=wy)
    lampadas(wy - 1.6, 1, x=0.0, nome="lamp")
    S.caixa3d(p, "mesa8", 0.2, 3.0, 2.2, 0.78, d=1.0, cor="#3a342a", tampo="#6b5a3e", aresta="#8a7650")
    S.caixa3d(p, "banco", -1.25, 3.3, 0.45, 0.45, d=0.45, cor="#2a2a24", tampo="#4a4a3c")
    S.caixa3d(p, "cad8", 1.65, 3.3, 0.45, 0.45, d=0.45, cor="#4a3424", tampo="#6a4a30")
    jq = OA.jaqueta_pendurada("jaq", (1.65, 3.5, 0.47), 1.1); jq.rotation_euler = (math.radians(-90), 0, math.radians(90))
    ze = sentado("ze", "ze", -1.1, 3.5, rot=90, ombro=(-62, -58), cotovelo=(-38, -40))
    cartas = [(-0.55, 3.35), (-0.5, 3.62), (0.85, 3.35), (0.92, 3.6), (0.2, 3.5)]
    for k, (x, y) in enumerate(cartas):
        c = PA.carta(f"carta{k}", (x, y, 0.79), 2.6, verso=(k % 2 == 0)); c.rotation_euler = (math.radians(-90), 0, math.radians(17 * k - 30))
    camera((0.2, 3.35, 2.75), (0.2, 3.5, 0.78), 28, fstop=8.0, foco=(0.2, 3.5, 0.8), roll=90)


@plano("8B", "45 mm, por cima da jaqueta", "pelos dois lados")
def p8B():
    p = pal("escuro"); wy = 5.5
    sala_abrigo(p, wy=wy)
    OA.quadro_giz("giz_a", (-0.5, wy - 0.12, 1.5), 2.2, dias=90, rotulo="DIA 300")
    lampadas(wy - 1.6, 1, x=0.4, nome="lamp")
    S.caixa3d(p, "mesa8", 0.2, 2.9, 1.8, 0.78, d=1.0, cor="#3a342a", tampo="#6b5a3e", aresta="#8a7650")
    ze = sentado("ze", "ze", 0.15, 4.25, rot=0, ombro=(-48, -40), cotovelo=(-50, -56))
    ze.rosto(boca="sorriso", lid=0.5)
    OA.cadeira("cad", (0.95, 2.35, 0.0), 1.3); OA.jaqueta_pendurada("jaq", (0.95, 2.3, 0.62), 1.3)
    c = PA.carta("carta_m", (0.0, 3.3, 0.79), 2.6, verso=False); c.rotation_euler = (math.radians(-70), 0, 0)
    camera((0.8, 1.45, 1.25), (0.15, 4.2, 1.15), 45, fstop=2.0, foco=(0.15, 4.2, 1.25))


# ====================================================================== 9. A porta de novo
@plano("9A", "20 mm, do chão", "Quando só restava meio galão d'água")
def p9A():
    p = pal("escuro"); wy = abrigo(p, dia=700, lamp=1, nivel=0.1, galao=0.0, mesa=False)
    ze = ator3("ze", "ze", -0.25, 3.7, rot=0, pose=dict(ombro=(-62, -58), cotovelo=(-112, -110), abre=(14, 14), tronco=-4, cabeca=-14), rosto=dict(lid=0.7))
    bpy.context.view_layer.update()
    m = (ze.punho["F"].matrix_world.translation + ze.punho["B"].matrix_world.translation) / 2
    g = OA.galao("galao_z", (m.x + 0.05, m.y - 0.12, m.z - 0.05), 1.6, nivel=0.08); g.rotation_euler = (0, math.radians(-110), 0)
    camera((0.2, 2.15, 0.3), (-0.2, 3.7, 1.5), 20, fstop=4.0, foco=(-0.2, 3.6, 1.5))


@plano("9B", "35 mm, atrás do Zé", "o Zé finalmente...")
def p9B():
    p = pal("escuro"); wy = abrigo(p, dia=700, lamp=1, nivel=0.1, galao=0.0, mesa=False)
    ator3("ze", "ze", 2.55, 3.6, rot=200, pose=dict(quadril=(-22, 14), joelho=(12, 28), tornozelo=(6, -8), ombro=(16, -14), cotovelo=(-14, -12), tronco=-3))
    ator2(EA.rita, "rita", "q", 0.9, 1.75, face=dict(lid="esperto", lidv=0.6, browup=0.014, mouth="reta", look=(1.0, 0.3)))
    camera((0.95, 0.9, 1.45), (2.9, 5.3, 1.15), 35, fstop=2.8, foco=(2.55, 3.6, 1.2))


@plano("9C", "14 mm, o mesmo quadro da 2B", "... destrancou a porta.")
def p9C():
    p = pal("escuro"); wy = foyer(p, aberta=-0.28, luz=True)
    halo("fresta_gl", 0.55, wy - 0.15, 1.3, 1.6, "#ffffff", 0.75)
    ze = ator3("ze", "ze", 0.0, wy - 0.75, rot=180, pose=dict(ombro=(-92, -92), cotovelo=(-18, -18), abre=(12, 12), tronco=-4))
    ze.fecha_mao("F"); ze.fecha_mao("B")
    roda = bpy.data.objects["porta_roda"]; roda.rotation_euler = (0, math.radians(60), 0)
    bpy.context.view_layer.update()
    c = roda.matrix_world.translation
    maos_em(ze, (c.x - 0.2, c.y - 0.06, c.z + 0.12), (c.x + 0.2, c.y - 0.06, c.z - 0.05))
    import random
    rnd = random.Random(3)
    for k in range(16):
        props.poly(f"ferrugem{k}", circle(0, 0, 0.008, 6), "#b8692e", 0.0, None).location = (c.x + rnd.uniform(-0.35, 0.35), c.y - 0.12, c.z + rnd.uniform(-0.4, 0.3))
    camera((0.62, wy - 0.78, 1.5), (0.05, wy - 0.12, 1.3), 14, fstop=2.8, foco=(0.1, wy - 0.15, 1.32))


# ====================================================================== 10. Lá fora
@plano("10A", "24 mm, POV, o mesmo quadro da 1C", "Lá fora, não tinha mais nada")
def p10A():
    p = pal("cinza"); rua_morta(p)
    camera((0.05, 17.5, 1.62), (0.0, 46.0, 1.35), 24, fstop=8.0, foco=(0.0, 30.0, 1.3), roll=0.5)


@plano("10B", "50 mm, no chão", "Só cinza, poeira e silêncio")
def p10B():
    p = pal("cinza"); rua_morta(p)
    sr = OA.sirene("sirene_caida", (-1.95, 2.2, 0.35), 0.8); sr.rotation_euler = (0, math.radians(84), 0)
    cena.dust(p, 50, (-1.5, 2.0), 30, seed=9, color="#ece7d4", alpha=0.9, y_range=(0.6, 2.4), z_range=(0.05, 1.4), size=(0.006, 0.014))
    camera((0.75, -0.35, 0.38), (0.25, 2.2, 0.32), 50, fstop=2.8, foco=(0.3, 2.15, 0.3))


@plano("10C", "14 mm, o mesmo quadro da 1B", "A minha bicicleta ainda estava lá, no mesmo lugar")
def p10C():
    p = pal("cinza"); rua_morta(p)
    b = OA.bicicleta("bici", (0.4, 2.6, 0.0), 1.0, cor="#6a665a"); b.rotation_euler = (math.radians(55), 0, math.radians(-10))
    bpy.context.view_layer.update()
    hub = bpy.data.objects["bici_cubo1"].matrix_world.translation.copy()
    cam = camera((hub.x + 0.55, hub.y - 0.75, 0.16), (hub.x - 0.6, hub.y + 2.5, 0.35), 14, fstop=2.8, foco=(hub.x, hub.y, hub.z), roll=4)
    r, mE, mD, _ = maos(cam, "maos", escala=0.5, d=0.42, y=-0.27)
    troca_mao("maos", "dir", -10, "aberta")
    mE.location = (-0.6, 0, -0.9); mD.location = (-0.12, 0, 0.3)
    props.inked("relogio", circle(0, 0.06, 0.05, 20), "#aab6c8", bpy.data.objects["maos_inv_dir"], loc=(0.0, -0.012, 0.0), w=0.005)
    props.poly("relogio_m", circle(0.0, 0.06, 0.037, 20), "#d8d0bb", -0.016, bpy.data.objects["maos_inv_dir"])


# ====================================================================== 11. O preço
def fim_mundo(p):
    mundo(p)
    ceu(p, 140.0, topo="#8d8a7c", meio="#c4bea8")
    PA.ruinas_rua(p, -80.0, 120.0, seed=11)
    cena.poly_mesh("morro11", [(-30, 40.0, 0), (-18, 40.0, 5.0), (-6, 40.0, 8.0), (0, 40.0, 8.6), (10, 40.0, 7.2), (22, 40.0, 3.6), (34, 40.0, 0)], props.FM("#3b4235"))
    halo("morro_gl", 0.0, 39.8, 1.5, 3.4, "#d9b66a", 0.55)
    OA.porta_abrigo("porta_morro", (0, 39.7, 0), 1.0, aberta=0.8, luz_fora="#e8c470")
    OA.bicicleta("bici", (0.05, 36.2, 0.0), 1.0, cor="#6a665a")
    for yv, al in ((20.0, 0.10), (30.0, 0.16), (38.0, 0.2)):
        S.neblina(p, yv, al, z1=40.0)
    ze = ator3("ze", "ze", -0.55, 35.5, rot=0, pose=dict(ombro=(-3, 5), cotovelo=(-10, -10), abre=(4, 4)), rosto=dict(lid=0.68))
    ri = ator3("rita", "rita", 0.55, 35.5, rot=0, pose=dict(ombro=(-30, 5), cotovelo=(-50, -10), abre=(4, 4)), rosto=dict(lid=0.68))
    bpy.context.view_layer.update()
    m = ri.punho["F"].matrix_world.translation
    OA.sueter_dobrado("sueter_fim", (m.x, m.y - 0.08, m.z - 0.08), 1.3)


@plano("11A", "40 mm, de frente", "A gente sobreviveu")
def p11A():
    p = pal("cinza"); fim_mundo(p)
    camera((0.05, 31.9, 1.3), (0.0, 35.5, 1.25), 40, fstop=2.8, foco=(0.0, 35.5, 1.3))


@plano("11B", "28 mm, a grua sobe e recua", "Só pra ficar sozinho num mundo que acabou")
def p11B():
    p = pal("cinza"); fim_mundo(p)
    camera((0.0, 6.0, 9.5), (0.0, 37.0, 1.0), 28, fstop=11.0, foco=(0.0, 36.0, 1.0))


# ---------------------------------------------------------------- main
def main():
    argv = sys.argv[sys.argv.index("--") + 1:]
    if "--list" in argv:
        for k, (l, t, _) in PLANOS.items():
            print(f"PLANO {k} | {l} | {t}")
        return
    nome, out = argv[0], argv[1]
    k = float(argv[argv.index("--scale") + 1]) if "--scale" in argv else 0.5
    smp = int(argv[argv.index("--samples") + 1]) if "--samples" in argv else 16
    lib.reset(int(1080 * k), int(1920 * k), 24, smp)
    sc = bpy.context.scene; sc.frame_start, sc.frame_end = 1, 24
    PLANOS[nome][2]()
    sc.frame_set(1)
    sc.render.filepath = out
    bpy.ops.render.render(write_still=True)


if __name__ == "__main__":
    main()
