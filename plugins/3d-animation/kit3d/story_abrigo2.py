"""Storyboard da parte 2 de "O abrigo" (26/10/2026): um quadro parado por plano da decupagem (personagem/abrigo/decupagem-parte2.md, tabela em roteiros/abrigo2_planos.json),
com a lente, o foco e a profundidade de verdade. Reaproveita a rua, o bunker, o elenco e os objetos do ep. 1 (story3_abrigo) e as peças novas (objetos3d_abrigo2).
blender -b -P story_abrigo2.py -- PLANO SAIDA.png [--scale 0.5] [--samples 16]      (--list mostra os planos desenhados)
O pós (luz de fim de tarde / noite / flashback, a montagem de abertura com glitch) é por cima dos quadros, em story_abrigo2_rodar.py."""
import os, sys, math, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy, lib
from lib import *
from mathutils import Vector, Euler
import cena, props
import story3_abrigo as S3
import story_abrigo as SA
import objetos3d_abrigo as O3, objetos3d_abrigo_b as O3B, objetos3d_abrigo2 as O2, elenco3d_abrigo as E3, ambiente_noite as AN, ambiente_galpao as AG
from prod_abrigo import halo

BY = S3.BY
RAIZ = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
BUILD = {}
GRADE = {}                                                          # plano -> luz do pós (tarde1, tarde2, noite, flash, galpao)


def C(loc, alvo, lente, f=8.0, foco=None, roll=0.0):
    return S3.cam(tuple(loc), tuple(alvo), lente, fstop=f, foco=tuple(foco) if foco is not None else None, roll=roll)


def reg(ids, grade=None):
    def deco(fn):
        for i in ids.split():
            BUILD[i] = fn
            if grade:
                GRADE[i] = grade
        return fn
    return deco


def olha(h, alvo):
    d = Vector(alvo) - Vector(h.raiz.location)
    h.raiz.rotation_euler.z = math.atan2(d.x, -d.y)


def sem(nome, chave, x, y, rot=0.0, curva=1.0, seed=2, bf=True):
    return O2.sem_osso(nome, chave, (x, y, 0.0), rot=rot, curva=curva, seed=seed, bracos_frente=bf)


def rua(carros=True):
    return S3.rua3(morta=True, aberta=0.0, carros=carros)


def eu_rosto(nome, x, y, rot, boca="o", lid=0.1, olhar=0.0):
    h = SA.ator3("eu", nome, x, y, rot=rot, rosto=dict(boca=boca, lid=lid))
    h.cabeca.rotation_euler.z = math.radians(olhar)
    return h


# ====================================================================== galpão
GC = (0.0, -0.8)                                                    # onde o narrador acorda
PRE = {"lider": (0.0, 1.75), "radio": (-1.7, 1.5), "cochicho": (1.6, 1.2), "taco": (-1.4, -0.3), "jovem": (1.4, -0.4), "solto": (-0.7, -2.0),
       "careca": (0.8, -2.0), "trancas": (-2.1, 0.5), "menino": (2.1, 0.2)}


def galpao(grupo=True, quem=None, narr=None, fogo=True, olhar_para=None, anel=None, rico=True):
    """o galpão com o tambor de fogo, a mesa do rádio, caixotes e o grupo em volta do narrador. narr = None | 'em_pe' | 'deitado'. Devolve (dict do grupo, narrador)"""
    O2.galpao3d("galpao")
    if rico:
        AG.galpao_rico(fogo=fogo)
    if fogo:
        O2.tambor_fogo3d("tambor", (0.0, 0.5, 0))
    O3.mesa3d("mesa", (-2.4, 2.2, 0), tam=(1.4, 0.7, 0.78))
    O2.radio3d("radio", (-2.6, 2.25, 0.78), 1.0)
    O2.fone_mesa3d("fone", (-2.05, 2.1, 0.78))
    for k, (x, y) in enumerate(((-1.0, -0.2), (1.3, 0.1), (-0.3, 2.6))):
        O3.caixa(f"caixote{k}", (0.5, 0.4, 0.42), O3.M("#7a6448", "#5a4632"), None, (x, y, 0.21), chanfro=0.015)
    G = {}
    if grupo:
        for k in (quem or list(PRE)):
            h = O2.faz_grupo(k, k)
            x, y = PRE[k]
            h.raiz.location = (x, y, 0)
            olha(h, olhar_para or (GC[0], GC[1], 0))
            h.pose(ombro=(-4, 4), cotovelo=(-12, -12), abre=(6, 6)); h.rosto(boca="reta", lid=0.35)
            G[k] = h
        if anel:                                                    # em círculo, inclinados para o narrador (o POV de quem acorda no chão)
            ks = list(G)
            for j, k in enumerate(ks):
                a = 2 * math.pi * j / len(ks) + 0.5
                G[k].raiz.location = (GC[0] + anel * math.sin(a), GC[1] + anel * math.cos(a) * 1.0, 0)
                olha(G[k], (GC[0], GC[1], 0))
                G[k].pose(ombro=(-4, 4), cotovelo=(-12, -12), abre=(6, 6), tronco=16, cabeca=22)
    N = None
    if narr:
        N = SA.ator3("eu", "eu", GC[0], GC[1], rot=0, rosto=dict(boca="o", lid=0.25))
        if narr == "deitado":
            N.raiz.rotation_euler.x = math.radians(-90); N.raiz.location = (GC[0], GC[1] - 0.75, 0.16)
    return G, N


# ====================================================================== 1. A coisa
def abr():
    return S3.ruina_final()


@reg("1A")
def p1A():
    abr(); C((0.0, BY - 14.0, 9.0), (0, BY - 1.0, 0.9), 24, 11.0, foco=(0, BY - 1.1, 1.0))


@reg("1B")
def p1B():
    abr(); C((0.0, BY - 6.6, 1.3), (0.0, BY - 1.1, 1.25), 85, 2.0, foco=(0.05, BY - 1.1, 1.3))


@reg("1C")
def p1C():
    S3.p11D()
    for o in bpy.data.objects:
        if o.name.startswith("zumbi"):
            o.hide_render = True


@reg("1D")
def p1D():
    S3.p11D()


@reg("1E")
def p1E():
    abr(); sem("so", "padeira", 1.7, BY - 4.8, rot=180)
    C((0.4, BY - 0.2, 1.55), (1.6, BY - 5.0, 1.1), 28, 5.6, foco=(1.7, BY - 4.8, 1.2))


@reg("1F")
def p1F():
    abr(); sem("so", "padeira", 0.0, BY - 6.0, rot=180, seed=2)
    C((0.35, BY - 2.7, 1.4), (0.0, BY - 6.0, 1.3), 85, 2.8, foco=(0.0, BY - 6.0, 1.3))


@reg("11E", "noite")
def p11E():
    p1F()


@reg("1G")
def p1G():
    abr(); C((0.0, BY - 3.4, 1.25), (-0.6, BY - 1.1, 1.22), 50, 2.0, foco=(-0.6, BY - 1.1, 1.22))


@reg("1H")
def p1H():
    abr(); sem("so", "padeira", -0.6, BY - 3.6, rot=180)
    C((-0.2, BY - 0.45, 0.17), (-0.6, BY - 3.2, 0.25), 18, 8.0, foco=(-0.6, BY - 2.0, 0.2))


# ====================================================================== 2. O ataque e a fuga
@reg("2A")
def p2A():
    rua(); ze = SA.ator3("ze", "ze", -0.3, BY - 3.2, rot=180, rosto=dict(boca="o", lid=0.0))
    s = sem("so", "padeira", -0.5, BY - 5.0, rot=180, curva=1.6); s.raiz.location.z = 0.45
    C((2.6, BY - 3.4, 0.5), (-0.3, BY - 3.9, 1.0), 35, 4.0, foco=(-0.4, BY - 4.4, 1.0))


@reg("2B")
def p2B():
    rua(); SA.ator3("ze", "ze", 0.0, BY - 2.5, rot=0, rosto=dict(boca="o", lid=0.0))
    c = C((0.0, BY - 4.2, 1.3), (0.0, BY - 2.5, 1.25), 50, 2.0, foco=(0.0, BY - 2.5, 1.25))
    O3.caixa("cobre", (0.55, 3.0, 0.12), O3.M("#0b0c0e", "#050506", "#2a3036"), c, (0.3, 0.0, -1.1), chanfro=0.02)


def pov_maos(c, esq="fechada", dir="fechada"):
    r, me, md = O3.maos_pov3d(c, "maos", d=0.5, escala=1.0)
    me.pose(esq); md.pose(dir)
    me.raiz.location = (-0.17, 0.62, -0.26); md.raiz.location = (0.17, 0.40, -0.19)
    me.raiz.rotation_euler = (math.radians(-6), 0, math.radians(6)); md.raiz.rotation_euler = (math.radians(26), 0, math.radians(-6))


@reg("2C")
def p2C():
    rua(); SA.ator3("rita", "rita", 0.7, BY - 3.6, rot=0, pose=dict(ombro=(-10, -40), cotovelo=(-12, -20), abre=(4, 4)), rosto=dict(boca="o", lid=0.0))
    c = C((0.0, BY - 3.0, 1.5), (0.6, BY - 6.0, 1.25), 24, 8.0, foco=(0.6, BY - 3.7, 1.2))
    pov_maos(c)


@reg("2D")
def p2D():
    rua(); b = O3.bicicleta3d("bici", (0.9, BY - 7.2, 0.0), 1.0, cor="#6a665a", poeira=0.85); b.rotation_euler.z = math.radians(80)
    SA.corre("eu", "eu", 0.0, BY - 5.0, rot=0, fase=3); SA.corre("rita", "rita", 1.0, BY - 5.4, rot=0, fase=6)
    C((0.4, BY - 1.6, 1.7), (0.4, BY - 8.0, 1.0), 16, 8.0, foco=(0.5, BY - 5.2, 1.0), roll=2.0)


@reg("2E")
def p2E():
    rua(); SA.corre("eu", "eu", 0.0, BY - 8.0, rot=0, fase=3).rosto(boca="o", lid=0.0)
    SA.corre("rita", "rita", 0.9, BY - 8.4, rot=0, fase=6).rosto(boca="o", lid=0.0)
    C((0.4, BY - 12.5, 1.4), (0.4, BY - 8.0, 1.2), 85, 2.0, foco=(0.45, BY - 8.2, 1.2))


# ====================================================================== 3. As outras
@reg("3A", "tarde1")
def p3A():
    rua(); SA.corre("eu", "eu", 0.2, 8.0, rot=0, fase=3); SA.corre("rita", "rita", 1.0, 8.3, rot=0, fase=6)
    C((2.5, -1.0, 7.5), (0.2, 8.0, 0.6), 24, 11.0, foco=(0.2, 8.0, 0.8))


@reg("3B", "tarde2")
def p3B():
    rua(); halo("sol", 0.5, -20.0, 2.4, 4.0, "#f6e2a8", 0.95)
    import random
    rnd = random.Random(11)
    for k in range(16):                                                 # a silhueta dos prédios quebrados contra o sol
        x = -16 + 2.2 * k + rnd.uniform(-0.6, 0.6); hh = rnd.uniform(2.5, 8)
        O3.caixa(f"sil{k}", (rnd.uniform(2.5, 4.5), 3.0, hh), O3.M("#14110e", "#14110e", "#14110e"), None, (x, -18.5, hh / 2), chanfro=0.0, contorno=0.0, rot=(0, rnd.uniform(-5, 5), 0))
    C((0.0, 4.0, 1.4), (0.0, -20.0, 2.2), 50, 11.0, foco=(0.0, -12.0, 2.0))


def olhos_no_escuro(x, y, z=1.4):
    O3.caixa("vao", (2.6, 0.2, 2.4), O3.M("#07080a", "#050506", "#14171a"), None, (x, y, 1.2), chanfro=0.0, contorno=0.0)
    for sx in (-0.18, 0.18):
        esf = H3esfera = O2.esfera("olhoB" + str(sx), 0.13, 0.03, 0.2, O2.plano("#6b6d66"), None, (x + sx, y - 0.12, z), contorno=0.0, seg=16, an=10)


@reg("3C", "tarde2")
def p3C():
    rua(); olhos_no_escuro(3.4, 12.0)
    C((1.4, 8.6, 1.4), (3.4, 12.0, 1.4), 35, 4.0, foco=(3.4, 12.0, 1.4))


@reg("3D", "tarde2")
def p3D():
    rua(); O3.caixa("toldo", (3.0, 1.4, 0.06), O3.M("#6a5a46", "#4a3e30"), None, (0.0, 11.5, 2.4), chanfro=0.0, rot=(24, 0, 4))
    O2.poca("p", 0.0, 10.6, 0.5, 0.35, seed=3)
    s = sem("so", "mercado", 0.0, 10.6, rot=0, curva=1.2, seed=8)
    O2.pingo("pg", None, (0.4, 11.0, 2.2), comp=0.9, r=0.025)
    C((2.8, 8.0, 1.5), (0.0, 10.8, 1.3), 28, 5.6, foco=(0.0, 10.7, 1.3))


@reg("3E", "tarde2")
def p3E():
    rua(); SA.corre("eu", "eu", 0.0, 7.0, rot=0, fase=3); SA.corre("rita", "rita", 0.9, 7.3, rot=0, fase=6)
    for k, (x, y, ch) in enumerate(((-1.8, 11.0, "padeira"), (1.9, 12.5, "mercado"), (-0.4, 14.0, "viz1"), (2.4, 15.5, "viz2"), (-2.2, 16.5, "viz3"))):
        sem(f"so{k}", ch, x, y, rot=0, curva=1.0, seed=3 + k)
    C((-0.8, 3.0, 1.4), (0.5, 11.0, 1.2), 50, 8.0, foco=(0.0, 7.2, 1.2))


@reg("3F", "tarde2")
def p3F():
    rua(); sem("so", "padeira", 0.3, 13.0, rot=0, curva=1.0, seed=2)
    c = C((0.0, 6.0, 1.55), (0.1, 16.0, 1.2), 20, 8.0, foco=(0.3, 13.0, 1.2))
    pov_maos(c)


# ====================================================================== 4. A mão que solta
@reg("4A", "noite")
def p4A():
    rua(); eu_rosto("eu", 0.0, 8.0, 0, boca="o", lid=0.05, olhar=-28)
    C((0.1, 6.4, 1.45), (0.0, 8.0, 1.42), 85, 2.0, foco=(0.0, 8.0, 1.42))


@reg("4B", "noite")
def p4B():
    rua(); sem("so", "padeira", 0.0, 12.0, rot=0, curva=1.0, seed=2)
    C((1.5, 3.0, 1.4), (0.0, 12.0, 1.2), 35, 11.0, foco=(0.0, 9.0, 1.2))


@reg("4C", "noite")
def p4C():
    rua()
    O3.maos_pov3d  # as duas mãos (a do narrador e a da Rita) se soltando
    a, _ = S3.mao_braco("mao_a", "dir", (0.38, 7.55, 1.1), (0.0, 1.0, 0.0), flexao=-10, pose="aberta")
    b = SA.ator3("rita", "rita", 0.85, 8.1, rot=180, pose=dict(ombro=(-80, -10), cotovelo=(-10, -10), abre=(6, 6)), rosto=dict(boca="o", lid=0.0))
    C((0.2, 6.2, 1.3), (0.45, 7.9, 1.1), 50, 2.8, foco=(0.4, 7.6, 1.1))


@reg("4D", "noite")
def p4D():
    rua(); O3.sueter3d("sue", (0.5, 8.0, 0.03), 2.6, dobrado=False)
    C((0.5, 7.0, 0.14), (0.5, 8.0, 0.06), 18, 2.8, foco=(0.5, 8.0, 0.05))


@reg("4E", "noite")
def p4E():
    rua()
    for k, (x, y, ch) in enumerate(((-4.0, 5.0, "padeira"), (4.0, 7.0, "mercado"), (-1.0, 14.0, "viz1"), (3.0, 11.0, "viz2"))):
        sem(f"so{k}", ch, x, y, rot=90 if x < 0 else -90, curva=1.0, seed=3 + k)
    C((0.0, 8.0, 1.5), (-5.0, 6.0, 1.2), 24, 5.6, foco=(-4.0, 5.2, 1.2), roll=-3)


@reg("4F", "noite")
def p4F():
    rua(); SA.ator3("eu", "eu", 0.0, 10.0, rot=0, rosto=dict(boca="o", lid=0.0))
    for k, (x, y, ch) in enumerate(((-4.0, 10.0, "padeira"), (4.0, 10.0, "mercado"), (0.0, 15.0, "viz1"), (0.0, 5.0, "viz2"))):
        sem(f"so{k}", ch, x, y, rot=0, curva=1.0, seed=3 + k)
    C((0.0, 3.0, 9.5), (0.0, 10.0, 0.0), 24, 11.0, foco=(0.0, 10.0, 0.8))


# ====================================================================== 5. A pancada
@reg("5A", "noite")
def p5A():
    rua(); O2.lanterna3d("lant", (2.2, 9.5, 0.95), 1.4, rot=(0, 0, 0), comp=2.6)
    h = O2.faz_grupo("taco", "taco"); h.raiz.location = (2.6, 10.2, 0); h.raiz.rotation_euler.z = 0
    C((-1.2, 5.5, 1.1), (2.2, 9.8, 1.0), 35, 4.0, foco=(2.2, 9.6, 1.0))


@reg("5B", "noite")
def p5B():
    rua(); h = O2.faz_grupo("taco", "taco"); h.raiz.location = (0.0, 7.0, 0); h.raiz.rotation_euler.z = 0
    h.pose(ombro=(-170, -150), cotovelo=(-20, -30), abre=(8, 10)); h.rosto(boca="reta", lid=0.3)
    bpy.context.view_layer.update()
    O2.taco3d("taco_obj", tuple(h.punho["B"].matrix_world.translation + Vector((0, -0.02, 0.0))), rot=(-40, 0, 0))
    C((0.0, 4.6, 1.55), (0.0, 7.0, 1.7), 24, 5.6, foco=(0.0, 7.0, 1.7), roll=6.0)


@reg("5C", "noite")
def p5C():
    rua(); n = SA.ator3("eu", "eu", 0.0, 6.0, rot=0, rosto=dict(boca="o", lid=1.2))
    n.raiz.rotation_euler.x = math.radians(-90); n.raiz.location = (0.0, 5.25, 0.16)
    O2.lanterna3d("lant", (1.0, 9.0, 0.5), 1.4, rot=(10, 0, 0), comp=2.5)
    for k, (x, y) in enumerate(((0.4, 8.6), (1.4, 8.8))):
        h = O2.faz_grupo(("taco", "jovem")[k], f"g{k}"); h.raiz.location = (x, y, 0)
    C((0.3, 4.4, 0.14), (0.0, 6.0, 0.16), 18, 2.8, foco=(0.0, 5.6, 0.15))


@reg("5D", "noite")
def p5D():
    p5C()


# ====================================================================== 6 a 8. O galpão
@reg("6A", "galpao")
def p6A():
    galpao(anel=1.0); C((0.0, GC[1], 0.18), (0.0, GC[1] + 0.15, 2.0), 14, 1.0, foco=(0.0, GC[1], 0.4))


@reg("6B", "galpao")
def p6B():
    galpao(anel=1.0); C((0.0, GC[1], 0.18), (0.05, GC[1] + 0.2, 2.0), 14, 11.0, foco=(0.5, GC[1] + 1.0, 1.5), roll=3.0)


@reg("6C", "galpao")
def p6C():
    galpao(narr="deitado"); C((0.3, -1.4, 4.0), (0.0, -0.6, 0.0), 24, 8.0, foco=(0.0, -0.8, 0.2))


@reg("6D", "galpao")
def p6D():
    G, _ = galpao(narr="em_pe", quem=["radio", "taco", "cochicho"])
    O2.lanterna3d("lant", (-0.5, -1.7, 1.25), 1.4, rot=(0, 0, 0), comp=1.2)
    C((0.1, -2.9, 1.25), (-0.3, -1.1, 1.2), 35, 4.0, foco=(-0.5, -1.7, 1.25))


@reg("6E", "galpao")
def p6E():
    galpao(grupo=False); eu_rosto("eu", 0.0, 0.0, 0, boca="o", lid=0.6)
    O2.lanterna3d("lant", (-0.5, -1.0, 1.5), 1.4, rot=(0, 0, 0), comp=0.9)
    C((0.05, -1.6, 1.45), (0.0, 0.0, 1.42), 85, 2.0, foco=(0.0, 0.0, 1.42))


@reg("7A", "galpao")
def p7A():
    galpao(narr="em_pe"); C((0.0, 1.4, 1.6), (0.0, -1.2, 1.2), 35, 5.6, foco=(0.0, -0.8, 1.3))


@reg("7B", "galpao")
def p7B():
    galpao(grupo=False); h = O2.faz_grupo("taco", "taco"); h.raiz.location = (0.4, -1.3, 0); olha(h, (0, 0, 0))
    h.pose(ombro=(-80, -80), cotovelo=(-40, -40), abre=(8, 8)); bpy.context.view_layer.update()
    O2.taco3d("t", tuple(h.punho["B"].matrix_world.translation), rot=(-20, 0, 0))
    C((0.0, -0.4, 0.9), (0.45, -1.3, 1.0), 18, 4.0, foco=(0.45, -1.3, 1.0))


@reg("7C", "galpao")
def p7C():
    galpao(grupo=False); eu_rosto("eu", 0.0, 0.0, 0, boca="o", lid=0.1)
    h = O2.faz_grupo("radio", "radio"); h.raiz.location = (-0.35, -0.75, 0); olha(h, (0, 0, 0))
    O2.lanterna3d("lant", (-0.1, -0.7, 1.45), 1.4, rot=(0, 0, 0), comp=0.5)
    C((1.7, -0.4, 1.5), (-0.1, -0.4, 1.45), 50, 2.8, foco=(-0.1, -0.4, 1.45))


@reg("7D", "galpao")
def p7D():
    galpao(grupo=False); eu_rosto("eu", 0.0, 0.0, 0, boca="reta", lid=0.0)
    C((0.0, -0.8, 1.48), (-0.06, 0.0, 1.48), 85, 1.8, foco=(-0.06, 0.0, 1.48))


@reg("7E", "galpao")
def p7E():
    galpao(narr=None); C((0.0, GC[1], 1.35), (0.0, 1.0, 1.3), 35, 5.6, foco=(0.0, 1.2, 1.3))


@reg("7F", "galpao")
def p7F():
    galpao(narr=None, quem=["lider", "radio", "jovem", "careca"])
    a = O2.faz_grupo("cochicho", "coc"); a.raiz.location = (1.1, 0.7, 0); a.raiz.rotation_euler.z = math.radians(-90)
    b = O2.faz_grupo("taco", "tac"); b.raiz.location = (1.55, 0.7, 0); b.raiz.rotation_euler.z = math.radians(90)
    a.pose(tronco=14, cabeca=8); a.rosto(boca="o", lid=0.4)
    C((0.0, -0.3, 1.5), (1.3, 0.75, 1.5), 50, 2.8, foco=(1.3, 0.75, 1.5))


@reg("7G", "galpao")
def p7G():
    G, _ = galpao(narr=None)
    for k, h in G.items():
        h.rosto(boca="reta", lid=0.0)
    C((0.0, GC[1], 1.4), (0.3, 1.0, 1.3), 28, 5.6, foco=(0.0, 1.5, 1.3))


@reg("8C", "galpao")
def p8C():
    galpao(narr=None); C((0.0, GC[1], 1.4), (-1.4, 0.2, 1.4), 50, 4.0, foco=(-1.4, -0.3, 1.4))


@reg("7H", "galpao")
def p7H():
    galpao(narr=None); eu_rosto("eu", 0.0, 0.0, 0, boca="reta", lid=0.2)
    h = O2.faz_grupo("radio", "radio"); h.raiz.location = (-0.5, -0.9, 0); olha(h, (0, 0, 0)); h.pose(ombro=(-60, -40), cotovelo=(-30, -30), abre=(8, 8))
    C((0.7, -1.7, 1.5), (-0.2, -0.3, 1.4), 50, 2.8, foco=(-0.2, -0.3, 1.4))


@reg("8A", "galpao")
def p8A():
    galpao(narr=None); c = C((0.0, GC[1], 1.35), (-1.0, GC[1] + 3.0, 1.4), 28, 5.6, foco=(-1.4, 1.2, 1.4)); pov_maos(c, "aberta", "aberta")


@reg("8B", "galpao")
def p8B():
    galpao(quem=["lider", "radio", "cochicho", "careca"]); h = O2.faz_grupo("jovem", "jv"); h.raiz.location = (1.6, 0.9, 0); olha(h, (0, GC[1], 0))
    h2 = E3.faz("ze", "zeverde"); h2.raiz.location = (1.1, 1.1, 0); h2.raiz.rotation_euler.z = math.radians(180)
    C((0.0, GC[1], 1.35), (1.4, 1.3, 1.3), 28, 5.6, foco=(1.1, 1.1, 1.3))


@reg("8D", "galpao")
def p8D():
    G, _ = galpao(narr=None, quem=["radio", "taco", "jovem"])
    L = O2.faz_grupo("lider", "lid"); L.raiz.location = (0.3, 0.4, 0); olha(L, (0.0, GC[1], 0))
    C((0.0, -2.4, 1.4), (0.2, 0.5, 1.3), 35, 5.6, foco=(0.3, 0.4, 1.3))


# ====================================================================== 9 a 12. A gosma, os ossos e os Sem-Osso
@reg("9A 11A", "galpao")
def p9A():
    galpao(quem=["radio", "taco", "cochicho", "jovem"], narr=None)
    L = O2.faz_grupo("lider", "lid"); L.raiz.location = (0.0, 1.75, 0); L.raiz.rotation_euler.z = 0; L.rosto(boca="reta", lid=0.55)
    C((0.35, -0.3, 1.5), (0.0, 1.75, 1.5), 85 if False else 50, 2.8, foco=(0.0, 1.75, 1.5))


@reg("11A", "galpao")
def p11A():
    galpao(quem=["radio", "taco"], narr=None)
    L = O2.faz_grupo("lider", "lid"); L.raiz.location = (0.0, 1.75, 0); L.rosto(boca="reta", lid=0.55)
    C((0.25, 0.7, 1.52), (0.0, 1.75, 1.5), 85, 2.0, foco=(0.0, 1.75, 1.5))


@reg("9B", "flash")
def p9B():
    S3.p1F()


@reg("9C", "flash")
def p9C():
    S3.rua3(aberta=0.0, branco=True); s = sem("so", "padeira", 0.0, BY - 0.9, rot=0, curva=0.6, seed=2)
    C((0.8, BY - 3.7, 1.15), (0.0, BY - 0.9, 1.15), 85, 2.8, foco=(0.0, BY - 0.9, 1.15))


@reg("9D", "flash")
def p9D():
    S3.rua3(aberta=0.0, branco=True); s = sem("so", "padeira", 0.0, BY - 0.9, rot=0, curva=0.9, seed=2)
    C((0.7, BY - 2.8, 0.75), (0.0, BY - 0.9, 0.6), 50, 4.0, foco=(0.0, BY - 0.9, 0.6))


@reg("9E", "flash")
def p9E():
    S3.rua3(aberta=0.0, branco=True); O2.poca("p", 0.2, BY - 0.8, 0.7, 0.4, seed=4); O3.caixa("av", (0.45, 0.4, 0.04), O3.M("#5b4034", "#3e2c24"), None, (0.2, BY - 0.8, 0.05), chanfro=0.0)
    C((0.9, BY - 2.0, 0.18), (0.2, BY - 0.8, 0.08), 18, 4.0, foco=(0.2, BY - 0.8, 0.08))


@reg("10A", "flash")
def p10A():
    S3.rua3(aberta=0.0, branco=True); O3.caixa("av", (0.5, 0.4, 0.04), O3.M("#5b4034", "#3e2c24"), None, (0.0, BY - 0.9, 0.06), chanfro=0.0, rot=(0, 0, 14))
    O2.mancha("rast", [(0.2 + 0.3 * k, BY - 1.0 - 0.15 * k) for k in range(9)], larg=0.22, seed=4)
    C((-2.6, BY - 2.8, 0.9), (1.0, BY - 1.7, 0.2), 35, 5.6, foco=(0.5, BY - 1.4, 0.15))


def esq_pilar():
    O3.caixa("pilar", (0.45, 0.45, 2.6), O3.M("#8c8d84", "#6e6f68"), None, (0.0, BY - 0.2, 1.3), chanfro=0.02)
    O3B.esqueleto3d("esq_a", (0.0, BY - 0.55, -0.8), (0, 0, 8), quadril=(-88, -84), joelho=(4, 14), ombro=(6, 10), abre=(14, 20), cotovelo=(-10, -30), cabeca=28, queixo=22, poeira=0.3)


@reg("10B", "flash")
def p10B():
    S3.rua3(aberta=0.0, carros=False); esq_pilar(); C((1.1, BY - 3.2, 1.0), (0.1, BY - 0.6, 0.6), 50, 4.0, foco=(0.0, BY - 0.6, 0.7))


@reg("12A", "flash")
def p12A():
    S3.rua3(aberta=0.0, carros=False); esq_pilar(); C((0.2, BY - 2.4, 0.9), (0.0, BY - 0.6, 0.82), 85, 2.0, foco=(0.0, BY - 0.6, 0.8))


def ossos_rua(n=14, seed=5):
    import random
    rnd = random.Random(seed)
    for k in range(n):
        x, y = rnd.uniform(-3.6, 3.6), rnd.uniform(3.0, 15.0)
        O3B.esqueleto_deitado(f"os{k}", (x, y), rumo=rnd.uniform(0, 360), de_lado=rnd.choice((0, 90, 180)), z=0.1, poeira=0.6, seed=seed + k)


@reg("10C", "noite")
def p10C():
    rua(); ossos_rua(); C((0.0, -2.0, 8.0), (0.0, 8.0, 0.0), 24, 11.0, foco=(0.0, 8.0, 0.5))


@reg("10D", "noite")
def p10D():
    rua(); ossos_rua(8, 9)
    for k, y in enumerate((5.0, 6.2, 7.4)):                      # esqueletos sentados nos degraus
        O3.caixa(f"deg{k}", (3.0, 1.0, 0.22 + 0.2 * k), O3.M("#6f6e66", "#55544e"), None, (-3.4, y + 0.6, 0.11 + 0.1 * k), chanfro=0.01)
    O3B.esqueleto3d("esq_s", (-3.2, 6.0, 0.35), (0, 0, 90), quadril=(-88, -84), joelho=(4, 14), cabeca=15, poeira=0.5)
    C((0.8, 2.6, 0.9), (-2.8, 7.0, 0.6), 35, 5.6, foco=(-2.8, 6.2, 0.6))


@reg("10E", "tarde2")
def p10E():
    rua(); O3B.esqueleto_deitado("cr", (0.0, 6.0), rumo=0, de_lado=0, z=0.1, poeira=0.6, seed=3)
    O2.lanterna3d("lant", (1.4, 4.8, 0.7), 1.4, rot=(0, 0, 40), comp=1.6)
    C((0.1, 4.6, 0.55), (0.0, 6.0, 0.3), 85, 2.0, foco=(0.0, 6.0, 0.25))


@reg("11B 12F 15C", "galpao")
def p11B():
    galpao(quem=["lider", "radio", "taco"]); eu_rosto("eu", 0.0, -0.8, 0, boca="o", lid=0.05)
    C((0.0, -2.5, 1.46), (0.0, -0.8, 1.42), 50, 2.8, foco=(0.0, -0.8, 1.42))


@reg("11C", "noite")
def p11C():
    rua(); O2.poca("p1", -1.5, 7.0, 0.35, 0.25, seed=1)
    O2.mancha("m2", [(-0.9 + 0.1 * k, 7.0 + 0.04 * math.sin(k)) for k in range(10)], larg=0.12, seed=2)
    O2.gosma("p2", [(0.4, 7.0, 0.0, 1.0, (0.25, 0.2, 0.04))], brilhos=3, seed=2)
    O2.gosma("p3", [(1.7, 7.0, 0.0, 1.0, (0.2, 0.17, 0.04))] + [(1.7, 7.0, 0.06 + 0.07 * k, 1.0, (0.12 - 0.006 * k, 0.1 - 0.005 * k, 0.07)) for k in range(5)], brilhos=4, seed=3)
    C((0.0, 5.6, 0.75), (0.0, 7.0, 0.05), 28, 8.0, foco=(0.0, 7.0, 0.1))


@reg("11D", "noite")
def p11D():
    rua(); O2.poca("p1", -0.8, 7.0, 0.4, 0.28, seed=1)
    O2.gosma("p3", [(0.4, 7.0, 0.0, 1.0, (0.2, 0.17, 0.04))] + [(0.4 + 0.03 * math.sin(k), 7.0, 0.06 + 0.1 * k, 1.0, (0.14 - 0.007 * k, 0.12 - 0.006 * k, 0.08)) for k in range(9)], brilhos=5, seed=3)
    sem("so", "padeira", 1.9, 7.4, rot=-90, curva=1.4, seed=9)
    C((-0.2, 4.6, 0.5), (0.8, 7.0, 0.8), 35, 4.0, foco=(0.5, 7.0, 0.8))


@reg("12B", "flash")
def p12B():
    S3.rua3(aberta=0.0, carros=False); S3.esqueletos_porta(); C((-1.5, BY - 5.4, 1.15), (0.1, BY - 0.8, 1.2), 24, 5.6, foco=(0.0, BY - 1.5, 0.5))


@reg("12C", "flash")
def p12C():
    S3.p2E()


@reg("12D", "flash")
def p12D():
    S3.p2F()


@reg("12E", "noite")
def p12E():
    rua(); sem("so", "padeira", 0.0, BY - 0.62, rot=180, curva=0.9, seed=2)
    C((1.75, BY - 2.05, 1.5), (-0.2, BY - 0.15, 1.5), 35, 4.0, foco=(0.0, BY - 0.62, 1.3))


# ====================================================================== 13 a 15. O rádio, a torre e o portão
@reg("13A", "galpao")
def p13A():
    galpao(grupo=False); L = O2.faz_grupo("lider", "lid"); L.raiz.location = (-2.6, 3.05, 0); L.pose(ombro=(-40, -40), cotovelo=(-60, -60), abre=(8, 8))
    C((-1.9, 0.6, 1.35), (-2.6, 2.3, 1.15), 50, 2.8, foco=(-2.6, 3.0, 1.3))


@reg("13B", "galpao")
def p13B():
    galpao(grupo=False); R = O2.faz_grupo("radio", "rad"); R.raiz.location = (-2.6, 3.05, 0)
    R.pose(ombro=(-40, -40), cotovelo=(-60, -60), abre=(8, 8))
    C((-1.8, 0.7, 1.35), (-2.6, 2.3, 1.2), 35, 4.0, foco=(-2.6, 3.0, 1.3))


@reg("13C 13E", "galpao")
def p13C():
    galpao(grupo=False); R = O2.faz_grupo("radio", "rad"); R.raiz.location = (-3.0, 3.1, 0); olha(R, (-3.3, 3.84, 0)); R.pose(ombro=(-100, -40), cotovelo=(-20, -50), abre=(8, 8))
    C((-3.3, 2.2, 1.4), (-3.3, 3.84, 1.35), 50, 4.0, foco=(-3.3, 3.84, 1.35))


@reg("13E")
def p13E():
    galpao(grupo=False); C((-3.55, 2.85, 1.68), (-3.55, 3.84, 1.68), 50, 4.0, foco=(-3.55, 3.84, 1.68))


@reg("13D", "galpao")
def p13D():
    galpao(grupo=False); C((-2.5, 1.2, 1.7), (-2.4, 3.84, 1.8), 24, 8.0, foco=(-2.4, 3.84, 1.8))


@reg("13F 15A", "galpao")
def p13F():
    galpao(narr="em_pe"); C((0.0, -3.5, 1.5), (0.0, 0.5, 1.1), 28, 8.0, foco=(0.0, 0.5, 1.1))


@reg("15F", "galpao")
def p15F():
    G, N = galpao(narr="em_pe")
    for k, h in G.items():
        olha(h, (0.6, 3.8, 0)); h.rosto(boca="o", lid=0.0)
    N.raiz.rotation_euler.z = math.radians(180)
    C((0.6, 3.1, 1.6), (0.0, -0.8, 1.3), 28, 5.6, foco=(0.0, -0.8, 1.3))


@reg("14A", "galpao")
def p14A():
    galpao(grupo=False); C((-2.5, 1.3, 1.0), (-2.6, 2.25, 0.95), 85, 4.0, foco=(-2.6, 2.1, 0.95))


@reg("14B", "galpao")
def p14B():
    G, _ = galpao(narr="em_pe")
    for k, h in G.items():
        olha(h, (-2.6, 2.25, 0)); h.pose(ombro=(-4, 4), cotovelo=(-12, -12), abre=(6, 6), tronco=14)
    C((-0.4, -0.9, 1.45), (-2.5, 2.1, 1.2), 35, 4.0, foco=(-1.7, 1.5, 1.3))


@reg("14C", "galpao")
def p14C():
    galpao(grupo=False); L = O2.faz_grupo("lider", "lid"); L.raiz.location = (4.4, 1.0, 1.4); L.pose(ombro=(-150, -150), cotovelo=(-20, -20), abre=(6, 6)); L.raiz.rotation_euler.z = math.radians(-90)
    C((3.2, -0.6, 1.2), (4.5, 1.2, 2.6), 24, 5.6, foco=(4.4, 1.0, 1.6))


def telhado():
    import random
    base_f = props.FM("#1c2028")
    cena.poly_mesh("chao_t", [(-400, -60, 0), (400, -60, 0), (400, 900, 0), (-400, 900, 0)], base_f)
    rnd = random.Random(6)
    for k in range(110):
        x = rnd.uniform(-160, 160); y = rnd.uniform(30, 380); w = rnd.uniform(5, 14); hgt = rnd.uniform(3, 11 + y * 0.03)
        O3.caixa(f"pred{k}", (w, rnd.uniform(5, 12), hgt), O3.M("#262b35", "#1d212a", "#3a404c"), None, (x, y, hgt / 2), chanfro=0.0, contorno=0.0, rot=(0, rnd.uniform(-6, 6), rnd.uniform(-8, 8)))
    O3.torno("morro", [(260, 0), (220, 30), (140, 60), (60, 78), (0, 82)], O3.M("#20242d", "#181b22", "#2e333e"), None, (40, 520, 0), seg=64, contorno=0.0)
    O2.torre3d("torre", (40, 520, 82), H=120)
    O3.caixa("telhado", (8.0, 6.0, 0.3), O3.M("#2e3036", "#24262b", "#4a4c54"), None, (0, -2.0, 13.85), chanfro=0.02)
    O3.caixa("parapeito", (8.0, 0.35, 0.7), O3.M("#3a3c40", "#2a2c30", "#5a5c64"), None, (0, 0.8, 14.3), chanfro=0.02)
    bpy.context.scene.world.node_tree.nodes["Background"].inputs[0].default_value = (*srgb("#141a26"), 1)


@reg("14D")
def p14D():
    telhado()
    L = O2.faz_grupo("lider", "lid"); L.raiz.location = (-0.6, -1.5, 14.0); L.raiz.rotation_euler.z = math.radians(180)
    N = SA.ator3("eu", "eu", 0.5, -1.5, rot=180, rosto=dict(boca="reta", lid=0.3)); N.raiz.location.z = 14.0
    C((0.0, -4.2, 15.5), (0.0, 0.5, 15.3), 35, 5.6, foco=(0.0, -1.5, 15.3))


@reg("14E")
def p14E():
    telhado()
    N = SA.ator3("eu", "eu", 0.0, -1.6, rot=180, rosto=dict(boca="reta", lid=0.3)); N.raiz.location.z = 14.0
    C((0.0, -3.0, 15.6), (36.0, 520.0, 115.0), 85, 4.0, foco=(36.0, 520.0, 100.0))


@reg("15B", "galpao")
def p15B():
    galpao(quem=["taco", "cochicho"]); L = O2.faz_grupo("lider", "lid"); L.raiz.location = (0.0, 1.75, 0); L.rosto(boca="triste", lid=0.6)
    C((0.7, 0.0, 1.55), (0.0, 1.75, 1.5), 50, 2.8, foco=(0.0, 1.75, 1.5))


@reg("15D", "noite")
def p15D():
    rua(); O3.sueter3d("sue", (0.5, 8.0, 0.03), 2.6, dobrado=False)
    C((0.9, 7.0, 0.16), (0.5, 8.0, 0.06), 18, 2.8, foco=(0.5, 8.0, 0.05))


@reg("15E", "galpao")
def p15E():
    galpao(quem=["lider", "radio"]); eu_rosto("eu", 0.0, -0.8, 0, boca="reta", lid=0.3)
    C((0.5, -2.4, 1.45), (-0.1, -0.8, 1.4), 50, 2.8, foco=(0.0, -0.8, 1.4))


@reg("16A", "galpao")
def p16A():
    galpao(grupo=False); C((-0.6, -3.6, 1.6), (0.6, 3.86, 1.6), 24, 8.0, foco=(0.6, 3.86, 1.6))


@reg("16B", "galpao")
def p16B():
    galpao(grupo=False); O2.poca("under", 0.6, 3.55, 0.45, 0.2, seed=2)
    C((0.6, 2.3, 0.12), (0.6, 3.8, 0.15), 18, 4.0, foco=(0.6, 3.8, 0.15))


@reg("16C", "galpao")
def p16C():
    galpao(grupo=False); C((0.6, 2.6, 2.6), (0.6, 3.86, 3.1), 50, 4.0, foco=(0.6, 3.86, 3.1))


@reg("16D", "galpao")
def p16D():
    galpao(grupo=False); N = SA.ator3("eu", "eu", 0.3, 2.4, rot=180, rosto=dict(boca="reta", lid=0.2))
    L = O2.faz_grupo("lider", "lid"); L.raiz.location = (0.95, 2.3, 0); L.raiz.rotation_euler.z = math.radians(180); L.pose(ombro=(-60, 4), cotovelo=(-60, -12), abre=(40, 6))
    C((-0.2, 0.7, 1.45), (0.6, 3.0, 1.2), 50, 4.0, foco=(0.5, 2.4, 1.2))


@reg("16E 17B", "galpao")
def p16E():
    galpao(grupo=False); N = SA.ator3("eu", "eu", 0.6, 3.5, rot=180, rosto=dict(boca="reta", lid=0.8)); N.cabeca.rotation_euler.z = math.radians(-70)
    C((-0.7, 3.2, 1.5), (0.6, 3.6, 1.5), 85, 2.0, foco=(0.6, 3.55, 1.5))


@reg("16F", "galpao")
def p16F():
    galpao(grupo=False); N = SA.ator3("eu", "eu", 0.6, 3.1, rot=180, rosto=dict(boca="reta", lid=0.2))
    C((0.6, 2.2, 1.46), (0.6, 3.86, 1.4), 50, 1.8, foco=(0.6, 3.86, 1.4))


@reg("17A", "galpao")
def p17A():
    galpao(grupo=False)
    c = C((1.2, 2.4, 1.3), (2.3, 3.76, 1.15), 35, 4.0, foco=(2.3, 3.76, 1.15))
    m = S3.mao_em("mao", "dir", (2.2, 3.66, 1.15), (0.5, 1.0, 0.0), pose="aberta")


@reg("17C", "galpao")
def p17C():
    galpao(grupo=False); b = bpy.data.objects.get("galpao_portao_barra")
    if b:
        b.location.x -= 0.2
    C((1.9, 2.7, 1.2), (2.3, 3.76, 1.15), 85, 2.8, foco=(2.3, 3.76, 1.15))


# ====================================================================== DIREÇÃO DE CENA v2 (26/10/2026): sequências 1 a 5 refeitas
# (personagem/abrigo/analise-parte2.md): reação antes da causa, o monstro revelado aos poucos, geografia única (a fuga é para -y, o monstro vem do
# entulho à direita) e câmera que se move: planos em MOV têm dois quadros, o de início e o do fim (--fim).
import random as _rnd
FIM = False
MOV = set()


def CM(a, b):
    """câmera que anda: a = quadro de início, b = quadro de fim; cada um (loc, alvo, lente, fstop, foco)"""
    t = b if FIM else a
    loc, alvo, lente, f, foco = t[:5]
    return C(loc, alvo, lente, f, foco=foco, roll=(t[5] if len(t) > 5 else 0.0))


def mov(ids):
    for i in ids.split():
        MOV.add(i)


def trio(olhar=0.0, ze_x=-0.6, ze_y=None):
    """os três no vão do bunker, como no último quadro do ep. 1 (Zé à esquerda, narrador no meio, Rita à direita com o suéter)"""
    p = S3.rua3(morta=True, aberta=0.9, carros=True)
    ze = SA.ator3("ze", "ze", ze_x, BY - 1.1 if ze_y is None else ze_y, rot=0, pose=dict(ombro=(-3, 5), cotovelo=(-10, -10), abre=(4, 4)), rosto=dict(boca="triste", lid=0.68))
    eu = SA.ator3("eu", "eu", 0.05, BY - 1.1, rot=0, pose=dict(ombro=(-3, 5), cotovelo=(-10, -10), abre=(4, 4)), rosto=dict(boca="triste", lid=0.68))
    ri = SA.ator3("rita", "rita", 0.7, BY - 1.1, rot=0, pose=dict(ombro=(5, -40), cotovelo=(-10, -60), abre=(4, 4)), rosto=dict(boca="triste", lid=0.68))
    bpy.context.view_layer.update()
    m = ri.punho["B"].matrix_world.translation
    O3.sueter3d("sueter_fim", (m.x, m.y - 0.06, m.z - 0.06), 1.5)
    b = O3.bicicleta3d("bici", (-1.9, BY - 2.6, 0.0), 1.0, cor="#6a665a", poeira=0.85); b.rotation_euler.z = math.radians(80)
    S3.esqueletos_porta()
    for h in (ze, eu, ri):
        h.cabeca.rotation_euler.z = math.radians(olhar)
    return p, ze, eu, ri


def entulho_dir():
    """o monte de entulho ao lado do abrigo, à direita (x de 2 a 4), de onde sai o monstro (a câmera escondida do 11D do ep. 1)"""
    rnd = _rnd.Random(14)
    for k, (x, y, tam, rz) in enumerate(((2.7, BY - 2.0, (0.9, 0.6, 0.5), 25), (3.3, BY - 1.7, (0.7, 0.5, 0.75), -18), (2.1, BY - 2.4, (0.8, 0.4, 0.35), 52),
                                         (3.9, BY - 2.3, (0.8, 0.7, 0.6), 10), (3.0, BY - 2.7, (0.6, 0.5, 0.4), -40), (3.6, BY - 1.1, (0.9, 0.8, 0.9), 70))):
        O3.caixa(f"ent{k}", tam, O3.M("#4a4b45", "#33342f", "#6c6d64"), None, (x, y, tam[2] / 2), chanfro=0.03, rot=(rnd.uniform(-6, 6), rnd.uniform(-8, 8), rz))
    v = O3.cilindro("verg", 0.015, 1.3, O3.M("#2c2b2a", "#1e1d1c", "#4a4846"), None, (3.1, BY - 2.2, 0.75), seg=10)
    v.rotation_euler = (math.radians(70), math.radians(12), math.radians(40))


def monstro(x, y, z=0.0, rot=-112, curva=1.0, chave="padeira", seed=2):
    s = sem("so", chave, x, y, rot=rot, curva=curva, seed=seed)
    s.raiz.location.z = z
    return s


mov("1A")


@reg("1A")
def p1A_v2():
    trio(); CM(((0.0, BY - 12.0, 5.5), (0, BY - 1.0, 0.9), 24, 11.0, (0, BY - 1.1, 1.0)), ((0.0, BY - 14.5, 9.0), (0, BY - 1.0, 0.9), 24, 11.0, (0, BY - 1.1, 1.0)))


@reg("1B")
def p1B_v2():
    trio(); mov("1B")
    CM(((0.0, BY - 6.6, 1.38), (0.0, BY - 1.1, 1.3), 50, 4.0, (0.05, BY - 1.1, 1.3)), ((0.0, BY - 5.2, 1.38), (0.0, BY - 1.1, 1.3), 50, 4.0, (0.05, BY - 1.1, 1.3)))


@reg("1C")
def p1C_v2():
    trio(olhar=36); C((0.0, BY - 4.4, 1.4), (0.05, BY - 1.1, 1.35), 60, 2.0, foco=(0.05, BY - 1.1, 1.35))


@reg("1D")
def p1D_v2():
    trio(); entulho_dir(); mov("1D")
    O2.gosma("mao", [(3.0, BY - 2.55, 0.42, 1.0, (0.12, 0.06, 0.04)), (3.14, BY - 2.65, 0.4, 1.0, (0.035, 0.03, 0.1)), (2.9, BY - 2.65, 0.4, 1.0, (0.03, 0.03, 0.09)), (3.02, BY - 2.68, 0.38, 1.0, (0.03, 0.03, 0.09)), (3.0, BY - 2.4, 0.5, 1.0, (0.05, 0.1, 0.03))], res=0.01, brilhos=3, seed=4)
    O2.mancha("rastro_c", [(3.0 + 0.05 * k, BY - 2.0 - 0.1 * k) for k in range(8)], larg=0.1, seed=3)
    CM(((3.3, BY - 4.0, 0.14), (3.0, BY - 2.6, 0.14), 18, 4.0, (3.0, BY - 2.6, 0.14)), ((3.3, BY - 4.0, 0.14), (3.0, BY - 2.6, 0.75), 18, 4.0, (3.0, BY - 2.6, 0.5)))


@reg("1E")
def p1E_v2():
    trio(); entulho_dir(); mov("1E")
    monstro(3.4, BY - 1.5, z=(0.0 if FIM else -0.6), rot=-110, curva=(1.0 if FIM else 1.9))
    CM(((-2.6, BY - 4.4, 0.5), (3.0, BY - 1.8, 0.9), 24, 8.0, (3.2, BY - 1.5, 1.0)), ((-2.6, BY - 4.4, 0.5), (3.1, BY - 1.7, 1.55), 24, 8.0, (3.3, BY - 1.5, 1.3)))


@reg("1F")
def p1F_v2():
    trio(olhar=36); entulho_dir(); mov("1F")
    monstro(1.9, BY - 2.2, rot=-100, curva=1.0)
    c = CM(((0.9, BY - 5.4, 1.3), (1.9, BY - 2.2, 1.25), 50, 1.8, (0.9, BY - 5.4 + 0.8, 1.3)), ((0.9, BY - 5.4, 1.3), (1.9, BY - 2.2, 1.25), 50, 1.8, (1.9, BY - 2.2, 1.25)))
    v = O3.cilindro("verg_fg", 0.012, 1.0, O3.M("#2c2b2a", "#1e1d1c", "#4a4846"), None, (1.0, BY - 4.8, 1.2), seg=10)
    v.rotation_euler = (math.radians(80), math.radians(-14), math.radians(10))


@reg("1F2")
def p1F2_v2():
    trio(olhar=36); mov("1F2")
    monstro(1.55, BY - 2.0, rot=-95, curva=1.0)
    CM(((-0.6, BY - 3.4, 1.3), (1.2, BY - 2.0, 1.12), 85, 1.8, (1.2, BY - 2.0, 1.12)), ((0.5, BY - 2.5, 1.28), (1.2, BY - 2.0, 1.12), 85, 1.8, (1.2, BY - 2.0, 1.12)))


@reg("1G")
def p1G_v2():
    trio(olhar=20, ze_x=(0.9 if FIM else -0.6), ze_y=(BY - 2.0 if FIM else None)); mov("1G")
    monstro(2.6, BY - 2.3, rot=-100, curva=1.0)
    C((-1.7, BY - 2.0, 1.5), (1.5, BY - 2.2, 1.2), 35, 4.0, foco=(1.5, BY - 2.2, 1.2))


@reg("1H")
def p1H_v2():
    trio(olhar=20, ze_x=0.9, ze_y=BY - 2.0); mov("1H")
    monstro(2.3, BY - 2.5, rot=-100, curva=1.0)
    CM(((-0.1, BY - 0.45, 0.16), (1.6, BY - 2.4, 0.2), 18, 8.0, (1.6, BY - 2.4, 0.2)), ((0.7, BY - 1.2, 0.16), (1.8, BY - 2.4, 0.22), 18, 8.0, (1.8, BY - 2.4, 0.2)))


# ---------------------------------------------------------------- 2. o ataque e a fuga
@reg("2A")
def p2A_v2():
    trio(olhar=20, ze_x=0.9, ze_y=BY - 2.0); entulho_dir(); mov("2A")
    s = monstro((1.7 if FIM else 2.9), BY - 2.1, z=(0.9 if FIM else 0.0), rot=-100, curva=(1.5 if FIM else 1.7))
    CM(((0.6, BY - 6.4, 1.0), (1.6, BY - 2.0, 1.1), 28, 5.6, (1.6, BY - 2.0, 1.1)), ((0.6, BY - 6.4, 1.0), (1.6, BY - 2.0, 1.1), 28, 5.6, (1.6, BY - 2.0, 1.1)))


@reg("2B")
def p2B_v2():
    rua(); z = SA.ator3("ze", "ze", 0.9, BY - 2.0, rot=0, rosto=dict(boca="o", lid=0.0))
    olha(z, (3.0, BY - 1.7, 0))
    entulho_dir()
    monstro((1.5 if FIM else 2.5), BY - 2.1, z=(1.0 if FIM else 0.6), rot=-100, curva=1.5)
    CM(((2.3, BY - 3.9, 1.35), (1.4, BY - 2.0, 1.3), 35, 4.0, (1.0, BY - 2.0, 1.3)), ((2.1, BY - 3.6, 1.35), (1.3, BY - 2.0, 1.3), 35, 4.0, (1.0, BY - 2.0, 1.3)))


@reg("2C")
def p2C_v2():
    rua(); SA.ator3("rita", "rita", 0.7, BY - 1.1, rot=0, pose=dict(ombro=(-10, -40), cotovelo=(-12, -20), abre=(4, 4)), rosto=dict(boca="o", lid=0.0)).cabeca.rotation_euler.z = math.radians(40)
    c = C((0.05, BY - 0.7, 1.5), (0.75, BY - 1.6, 1.2), 24, 8.0, foco=(0.7, BY - 1.1, 1.2))
    pov_maos(c)


@reg("2D")
def p2D_v2():
    rua(); mov("2D")
    b = O3.bicicleta3d("bici", (-1.9, BY - 2.6, 0.0), 1.0, cor="#6a665a", poeira=0.85); b.rotation_euler.z = math.radians(80)
    d = 0.0 if not FIM else 3.0
    SA.corre("eu", "eu", 0.1, BY - 3.0 - d, rot=0, fase=3).rosto(boca="o", lid=0.0); SA.corre("rita", "rita", 0.95, BY - 3.4 - d, rot=0, fase=6).rosto(boca="o", lid=0.0)
    CM(((0.4, BY - 0.3, 1.7), (0.5, BY - 6.0, 1.0), 16, 8.0, (0.5, BY - 3.2, 1.0)), ((0.4, BY - 3.3, 1.7), (0.5, BY - 9.0, 1.0), 16, 8.0, (0.5, BY - 6.2, 1.0)))


@reg("2E")
def p2E_v2():
    rua(); mov("2E")
    d = 0.0 if not FIM else 3.0
    SA.corre("eu", "eu", 0.0, BY - 6.5 - d, rot=0, fase=3).rosto(boca="o", lid=0.0)
    SA.corre("rita", "rita", 0.9, BY - 6.9 - d, rot=0, fase=6).rosto(boca="o", lid=0.0)
    CM(((0.4, BY - 10.0, 1.4), (0.4, BY - 6.5, 1.2), 85, 2.0, (0.45, BY - 6.7, 1.2)), ((0.4, BY - 13.0, 1.4), (0.4, BY - 9.5, 1.2), 85, 2.0, (0.45, BY - 9.7, 1.2)))


# ---------------------------------------------------------------- 3. as outras (a rua escurece; eles descem a rua para -y)
mov("2B 1A 1B 1D 1E 1F 1F2 1G 1H 2A 2D 2E 3A 3C 3D 3E 3F 4A 4B 4F 5A")


@reg("3A", "tarde1")
def p3A_v2():
    rua(); d = 0.0 if not FIM else 3.0
    SA.corre("eu", "eu", 0.2, 11.0 - d, rot=0, fase=3); SA.corre("rita", "rita", 1.0, 11.3 - d, rot=0, fase=6)
    CM(((2.8, 1.0, 6.0), (0.2, 10.0, 0.6), 24, 11.0, (0.2, 10.0, 0.8)), ((2.8, 4.0, 9.0), (0.2, 8.0, 0.6), 24, 11.0, (0.2, 8.0, 0.8)))


@reg("3C", "tarde2")
def p3C_v2():
    rua(); olhos_no_escuro(3.4, 12.0)
    CM(((1.0, 6.4, 1.4), (3.4, 12.0, 1.4), 35, 4.0, (3.4, 12.0, 1.4)), ((2.2, 9.2, 1.4), (3.4, 12.0, 1.4), 35, 4.0, (3.4, 12.0, 1.4)))


@reg("3E", "tarde2")
def p3E_v2():
    rua(); d = 0.0 if not FIM else 2.5
    SA.corre("eu", "eu", 0.0, 7.0 + d * 0.0 - (d if FIM else 0), rot=0, fase=3); SA.corre("rita", "rita", 0.9, 7.3 - (d if FIM else 0), rot=0, fase=6)
    for k, (x, y, ch) in enumerate(((-1.8, 10.0, "padeira"), (1.9, 12.5, "mercado"), (-0.4, 14.0, "viz1"), (2.4, 15.5, "viz2"), (-2.2, 16.5, "viz3"))):
        sem(f"so{k}", ch, x, y - (d if FIM else 0) * (1.0 - 0.15 * k), rot=0, curva=1.0, seed=3 + k)
    CM(((-0.6, 3.2, 1.4), (0.5, 10.0, 1.2), 50, 8.0, (0.0, 7.2, 1.2)), ((-0.6, 0.5, 1.4), (0.5, 7.5, 1.2), 50, 8.0, (0.0, 4.7, 1.2)))


@reg("3F", "tarde2")
def p3F_v2():
    rua(); sem("so", "padeira", 0.3, -1.0, rot=180, curva=1.0, seed=2)
    c = CM(((0.0, 5.0, 1.55), (0.1, -4.0, 1.2), 20, 8.0, (0.3, -1.0, 1.2)), ((0.0, 3.2, 1.55), (-0.4, -4.0, 1.2), 20, 8.0, (0.3, -1.0, 1.2)))
    pov_maos(c)


# ---------------------------------------------------------------- o beco (à esquerda da rua, ao longo de x)
def noite_base():
    """a cidade à noite fora da rua principal: chão aberto, céu azulado, ruínas ao longe (o beco e a outra rua não existem no cenário do ep. 1)"""
    S3.mundo_("cinza")
    bpy.context.scene.world.node_tree.nodes["Background"].inputs[0].default_value = (*srgb("#6a7694"), 1)
    cena.poly_mesh("chao_n", [(-90, -70, 0), (90, -70, 0), (90, 70, 0), (-90, 70, 0)], props.FM("#767880"))
    for yy in (60.0, -60.0):
        props.skywall(f"ceu_n{yy}", yy, [(-2.0, "#8e9ab4"), (6.0, "#7a86a4"), (14.0, "#5e6a8a"), (120.0, "#4a5576")], -200, 200, -2.0, 120.0)
    rnd = _rnd.Random(21)
    for k in range(40):                                                   # ruínas ao longe
        x = rnd.uniform(-70, 70); y = rnd.choice((rnd.uniform(14, 50), rnd.uniform(-50, -2)))
        if -26 < x < 0 and 2 < y < 12:
            continue
        hh = rnd.uniform(4, 16)
        O3.caixa(f"ru{k}", (rnd.uniform(4, 10), rnd.uniform(4, 9), hh), O3.M("#5a5d66", "#454851", "#7a7e88"), None, (x, y, hh / 2), chanfro=0.0, contorno=0.0, rot=(0, rnd.uniform(-4, 4), rnd.uniform(-10, 10)))


def beco(x0=-4.5, x1=-16.0, y=6.5, larg=3.0):
    for k, dy in enumerate((-larg / 2, larg / 2)):
        O3.caixa(f"beco{k}", (abs(x1 - x0), 0.5, 5.5), O3.M("#7a7c74", "#5a5c55", "#9a9c92"), None, ((x0 + x1) / 2, y + dy, 2.75), chanfro=0.0)
    S3.halo("luz_beco", x1 - 1.5, y, 2.2, 2.6, "#c9a860", 0.5) if hasattr(S3, "halo") else None
    for k in range(5):
        O3.caixa(f"lixo{k}", (0.5, 0.4, 0.3 + 0.1 * (k % 3)), O3.M("#3a3631"), None, (x0 - 2 - 2.2 * k, y + (-1.0 if k % 2 else 1.0), 0.18), chanfro=0.02, rot=(0, 0, 20 * k))


@reg("4A", "noite2")
def p4A_v2():
    noite_base(); beco(); mov("4A")
    h = eu_rosto("eu", -8.0, 6.5, 90, boca="o", lid=0.05, olhar=-35)
    CM(((-5.6, 6.5, 1.5), (-8.0, 6.5, 1.5), 50, 3.2, (-8.0, 6.5, 1.45)), ((-6.4, 6.5, 1.5), (-8.0, 6.5, 1.5), 50, 3.2, (-8.0, 6.5, 1.45)))


@reg("4B", "noite2")
def p4B_v2():
    noite_base(); beco(); sem("so", "padeira", -4.0, 6.5, rot=-90, curva=1.0, seed=2)
    C((-11.0, 6.5, 1.35), (-4.5, 6.5, 1.2), 35, 11.0, foco=(-6.0, 6.5, 1.2))


@reg("4C", "noite2")
def p4C_v2():
    noite_base(); beco()
    a, _ = S3.mao_braco("mao_a", "dir", (-8.0, 6.3, 1.1), (1.0, 0.0, 0.0), flexao=-10, pose="aberta")
    b = SA.ator3("rita", "rita", -7.2, 6.5, rot=90, pose=dict(ombro=(-80, -10), cotovelo=(-10, -10), abre=(6, 6)), rosto=dict(boca="o", lid=0.0))
    C((-8.5, 5.4, 1.3), (-7.7, 6.4, 1.1), 50, 2.8, foco=(-7.9, 6.4, 1.1))


@reg("4D", "noite2")
def p4D_v2():
    noite_base(); beco(); O3.sueter3d("sue", (-9.0, 6.5, 0.03), 2.6, dobrado=False)
    C((-10.2, 6.5, 0.14), (-9.0, 6.5, 0.06), 18, 2.8, foco=(-9.0, 6.5, 0.05))


@reg("4E", "noite2")
def p4E_v2():
    noite_base(); beco()
    for k, (x, y, ch) in enumerate(((-6.4, 6.5, "padeira"), (-5.6, 7.7, "mercado"), (-7.4, 5.3, "viz1"))):
        sem(f"so{k}", ch, x, y, rot=-90, curva=1.0, seed=3 + k)
    C((-13.0, 6.5, 1.5), (-4.5, 6.5, 1.2), 24, 5.6, foco=(-4.4, 6.5, 1.2), roll=-3)


@reg("4F", "noite2")
def p4F_v2():
    noite_base(); beco(); SA.ator3("eu", "eu", -16.5, 6.5, rot=0, rosto=dict(boca="o", lid=0.0))
    for k, (x, y, ch) in enumerate(((-24.0, 6.5, "padeira"), (-16.5, 1.0, "mercado"), (-16.5, 12.0, "viz1"), (-9.0, 6.5, "viz2"))):
        sem(f"so{k}", ch, x, y, rot=0, curva=1.0, seed=3 + k)
    CM(((-16.5, -1.0, 4.0), (-16.5, 6.5, 0.8), 24, 11.0, (-16.5, 6.5, 0.8)), ((-16.5, -1.0, 10.0), (-16.5, 6.5, 0.5), 24, 11.0, (-16.5, 6.5, 0.5)))


# ---------------------------------------------------------------- 5. a pancada (no fim do beco, na outra rua)
@reg("5A", "noite2")
def p5A_v2():
    noite_base(); beco(); O2.lanterna3d("lant", (-20.5, 5.0, 0.95), 1.4, rot=(0, 0, 90), comp=3.0)
    h = O2.faz_grupo("taco", "taco"); h.raiz.location = (-21.0, 4.6, 0); h.raiz.rotation_euler.z = math.radians(-90)
    CM(((-16.5, 8.6, 1.2), (-20.5, 5.0, 1.0), 35, 4.0, (-20.5, 5.0, 1.0)), ((-17.6, 7.4, 1.2), (-20.5, 5.0, 1.0), 35, 4.0, (-20.5, 5.0, 1.0)))


@reg("5B", "noite2")
def p5B_v2():
    noite_base(); beco(); h = O2.faz_grupo("taco", "taco"); h.raiz.location = (-19.0, 6.5, 0); h.raiz.rotation_euler.z = math.radians(-90)
    h.pose(ombro=(-170, -150), cotovelo=(-20, -30), abre=(8, 10)); h.rosto(boca="reta", lid=0.3)
    bpy.context.view_layer.update()
    O2.taco3d("taco_obj", tuple(h.punho["B"].matrix_world.translation + Vector((0, 0, 0.0))), rot=(-40, 0, 0))
    C((-16.5, 6.5, 1.55), (-19.0, 6.5, 1.7), 24, 5.6, foco=(-19.0, 6.5, 1.7), roll=6.0)


@reg("5C", "noite2")
def p5C_v2():
    noite_base(); beco(); n = SA.ator3("eu", "eu", -17.0, 6.5, rot=0, rosto=dict(boca="o", lid=1.2))
    n.raiz.rotation_euler.x = math.radians(-90); n.raiz.location = (-17.0, 5.75, 0.16)
    O2.lanterna3d("lant", (-19.5, 7.0, 0.5), 1.4, rot=(10, 0, 90), comp=2.5)
    for k, y in enumerate((7.4, 5.4)):
        h = O2.faz_grupo(("taco", "jovem")[k], f"g{k}"); h.raiz.location = (-19.8, y, 0); h.raiz.rotation_euler.z = math.radians(-90)
    C((-16.0, 5.6, 0.14), (-17.5, 6.5, 0.16), 18, 2.8, foco=(-17.0, 6.2, 0.15))


@reg("5D", "noite2")
def p5D_v2():
    p5C_v2()


# ====================================================================== CENÁRIO RICO (26/10/2026, guia-luz-e-suspense.md)
def noite_rica(ceu="noite"):
    """a noite com profundidade: ruínas de prédios com janelas acesas ao fundo, névoa em camadas, chão aberto (substitui noite_base nos planos ricos)"""
    S3.mundo_("cinza")
    cor_ceu = {"noite": ("#6a7694", "#8e9ab4", "#7a86a4", "#5e6a8a", "#4a5576"), "tarde": ("#a8806a", "#d8b48a", "#b8906e", "#8a6a58", "#5a4a44")}[ceu]
    bpy.context.scene.world.node_tree.nodes["Background"].inputs[0].default_value = (*srgb(cor_ceu[0]), 1)
    cena.poly_mesh("chao_n", [(-90, -70, 0), (90, -70, 0), (90, 70, 0), (-90, 70, 0)], props.FM("#767880" if ceu == "noite" else "#8a7a6a"))
    for yy in (60.0, -60.0):
        props.skywall(f"ceu_n{yy}", yy, [(-2.0, cor_ceu[1]), (6.0, cor_ceu[2]), (14.0, cor_ceu[3]), (120.0, cor_ceu[4])], -200, 200, -2.0, 120.0)
    AN.predios_ao_fundo(-75, 75, 44.0, n=16, seed=7, acesas=0.22, nome="pn")
    AN.predios_ao_fundo(-75, 75, -34.0, n=16, seed=9, acesas=0.22, nome="ps")
    AN.neblina_y([20.0, 32.0], -90, 90, alfa=0.07, cor="#8a96b2" if ceu == "noite" else "#c9a888")
    AN.neblina_y([-10.0, -22.0], -90, 90, alfa=0.07, cor="#8a96b2" if ceu == "noite" else "#c9a888", nome="nys")
    cena.dust(S3.pal("cinza"), 70, (-24, 2), 40, seed=5, color="#d8dde8", alpha=0.7, y_range=(2.0, 11.0), z_range=(0.3, 4.6), size=(0.008, 0.02))


def praca_noite(x=-21.0, y=6.5):
    """o fim do beco: uma praça de esquina com postes, um carro queimado, lixo, poças e neblina (onde o grupo está)"""
    AN.poste("pz1", x + 3.0, y - 4.0, acesa=True, rot=180); AN.poste("pz2", x - 4.0, y + 5.0, acesa=False, rot=0)
    AN.carro("cq", x - 3.5, y - 2.5, rot=20, queimado=True); AN.carro("cq2", x + 1.0, y + 6.0, rot=-70)
    AN.caixote("pxa", x + 2.0, y + 1.5, 20, 2); AN.barril("pb1", x - 1.5, y - 3.0); AN.lixeira("plx", x + 1.2, y - 2.0)
    AN.poca_agua("ppq", x + 0.5, y + 0.5, 1.8, 0.9, brilho=("#ffcf7a", 0.4), seed=3); AN.papeis("ppp", x, y, 6.0, 20)
    AN.neblina_x([x - 3.0, x - 8.0], y - 12, y + 12, alfa=0.08)


@reg("3C", "tarde2")
def p3C_v3():
    noite_rica("tarde"); AN.loja_escura("loja", 3.4, 11.0, rot=0.0, w=5.0); AN.poste("pl3", -1.5, 12.0, acesa=False)
    AN.carro("c3", -2.5, 6.0, rot=8, queimado=True)
    for k, sx in enumerate((-0.18, 0.18)):
        H3o = O2.esfera("olhoL" + str(k), 0.075 if FIM else 0.02, 0.02, 0.11 if FIM else 0.02, O2.plano("#cfd2c8"), None, (3.4 + sx + 0.4, 13.0, 1.15), contorno=0.0, seg=16, an=10)
    CM(((1.0, 5.2, 1.35), (3.6, 12.6, 1.2), 35, 4.0, (3.6, 12.6, 1.2)), ((2.0, 8.0, 1.3), (3.6, 12.6, 1.2), 35, 4.0, (3.6, 12.6, 1.2)))


@reg("3D", "tarde2")
def p3D_v3():
    noite_rica("tarde"); AN.poste("pl4", 1.6, 9.0, acesa=not FIM)
    O3.caixa("toldo", (3.0, 1.4, 0.06), O3.M("#6a5a46", "#4a3e30"), None, (-1.5, 10.8, 2.4), chanfro=0.0, rot=(24, 0, 4))
    AN.caixote("cx3", -2.6, 9.6, 30, 2); AN.carro("c4", 4.5, 14.0, rot=-30)
    AN.poca_agua("pq4", -0.4, 9.2, 1.0, 0.6, brilho=("#ffcf7a", 0.4))
    O2.poca("p", -0.2, 10.4, 0.5, 0.35, seed=3)
    s = sem("so", "mercado", (-0.1 if not FIM else 0.5), (10.6 if not FIM else 9.0), rot=(0 if not FIM else 20), curva=1.2, seed=8)
    O2.pingo("pg", None, (-1.2, 11.0, 2.2), comp=0.9, r=0.025)
    CM(((3.0, 6.0, 1.2), (-0.2, 10.4, 1.2), 28, 5.6, (-0.2, 10.4, 1.2)), ((2.4, 5.4, 1.2), (0.2, 9.4, 1.2), 28, 5.6, (0.4, 9.2, 1.2)))


@reg("4A", "noite2")
def p4A_v3():
    noite_rica(); AN.beco_rico(); mov("4A")
    eu_rosto("eu", -8.0, 6.5, 90, boca="o", lid=0.05, olhar=-35)
    CM(((-6.9, 6.5, 1.45), (-8.0, 6.5, 1.42), 85, 2.0, (-8.0, 6.5, 1.42)), ((-7.3, 6.5, 1.45), (-8.0, 6.5, 1.42), 85, 2.0, (-8.0, 6.5, 1.42)))


@reg("4B", "noite2")
def p4B_v3():
    noite_rica(); AN.beco_rico(); mov("4B")
    AN.poste("pb4", -2.5, 3.6, acesa=True, rot=180)
    O3.halo_cam("contraluz", (-2.0, 6.5, 2.0), 4.2, "#f2e2b0", 0.55)
    AN.mancha_parede("sombraM", (-6.4 if FIM else -5.6), 1.7, (1.3 if FIM else 0.8), 3.4, 5.25, +1, cor="#08080a", alfa=0.6)
    sem("so", "padeira", (-5.0 if FIM else -3.8), 6.5, rot=-90, curva=1.0, seed=2)
    C((-11.0, 6.5, 1.3), (-4.5, 6.5, 2.3), 35, 8.0, foco=(-4.5, 6.5, 1.3))


@reg("4C", "noite2")
def p4C_v3():
    noite_rica(); AN.beco_rico()
    a, _ = S3.mao_braco("mao_a", "dir", (-8.0, 6.3, 1.1), (1.0, 0.0, 0.0), flexao=-10, pose="aberta")
    b = SA.ator3("rita", "rita", -7.2, 6.5, rot=90, pose=dict(ombro=(-80, -10), cotovelo=(-10, -10), abre=(6, 6)), rosto=dict(boca="o", lid=0.0))
    C((-8.6, 5.5, 1.3), (-7.7, 6.4, 1.1), 50, 2.8, foco=(-7.9, 6.4, 1.1))


@reg("4D", "noite2")
def p4D_v3():
    noite_rica(); AN.beco_rico(); O3.sueter3d("sue", (-9.3, 6.4, 0.03), 2.6, dobrado=False)
    AN.poca_agua("pq5", -9.3, 6.4, 0.8, 0.5, brilho=("#ffcf7a", 0.3))
    C((-10.5, 6.2, 0.16), (-9.3, 6.4, 0.08), 18, 2.8, foco=(-9.3, 6.4, 0.06))


@reg("4E", "noite2")
def p4E_v3():
    noite_rica(); AN.beco_rico(); AN.poste("pb4", -2.5, 3.6, acesa=True, rot=180)
    for k, (x, y, ch) in enumerate(((-6.4, 6.5, "padeira"), (-5.4, 7.6, "mercado"), (-7.6, 5.4, "viz1"))):
        sem(f"so{k}", ch, x, y, rot=-90, curva=1.0, seed=3 + k)
    C((-13.0, 6.5, 1.5), (-4.5, 6.5, 1.3), 24, 8.0, foco=(-6.0, 6.5, 1.3), roll=-3)


@reg("4F", "noite2")
def p4F_v3():
    noite_rica(); AN.beco_rico(); praca_noite(); mov("4F")
    SA.ator3("eu", "eu", -17.5, 6.5, rot=0, rosto=dict(boca="o", lid=0.0))
    for k, (x, y, ch) in enumerate(((-24.0, 6.5, "padeira"), (-17.5, 0.5, "mercado"), (-17.5, 12.5, "viz1"), (-10.5, 6.5, "viz2"))):
        sem(f"so{k}", ch, x, y, rot=0, curva=1.0, seed=3 + k)
    CM(((-17.5, -1.0, 4.0), (-17.5, 6.5, 0.8), 24, 11.0, (-17.5, 6.5, 0.8)), ((-17.5, -1.0, 10.0), (-17.5, 6.5, 0.5), 24, 11.0, (-17.5, 6.5, 0.5)))


@reg("5A", "noite2")
def p5A_v3():
    noite_rica(); AN.beco_rico(); praca_noite(); mov("5A")
    O2.lanterna3d("lant", (-22.5, 5.0, 0.95), 1.4, rot=(0, 0, 90), comp=3.2)
    h = O2.faz_grupo("taco", "taco"); h.raiz.location = (-23.0, 4.6, 0); h.raiz.rotation_euler.z = math.radians(-90)
    CM(((-18.0, 8.6, 1.2), (-22.5, 5.0, 1.0), 35, 4.0, (-22.5, 5.0, 1.0)), ((-19.0, 7.4, 1.2), (-22.5, 5.0, 1.0), 35, 4.0, (-22.5, 5.0, 1.0)))


@reg("5B", "noite2")
def p5B_v3():
    noite_rica(); AN.beco_rico(); praca_noite()
    h = O2.faz_grupo("taco", "taco"); h.raiz.location = (-20.5, 6.5, 0); h.raiz.rotation_euler.z = math.radians(-90)
    h.pose(ombro=(-170, -150), cotovelo=(-20, -30), abre=(8, 10)); h.rosto(boca="reta", lid=0.3)
    bpy.context.view_layer.update()
    O2.taco3d("taco_obj", tuple(h.punho["B"].matrix_world.translation), rot=(-40, 0, 0))
    C((-17.6, 6.5, 1.55), (-20.5, 6.5, 1.7), 24, 5.6, foco=(-20.5, 6.5, 1.7), roll=6.0)


@reg("5C", "noite2")
def p5C_v3():
    noite_rica(); AN.beco_rico(); praca_noite()
    n = SA.ator3("eu", "eu", -18.5, 6.5, rot=0, rosto=dict(boca="o", lid=1.2))
    n.raiz.rotation_euler.x = math.radians(-90); n.raiz.location = (-18.5, 5.75, 0.16)
    O2.lanterna3d("lant", (-21.0, 7.0, 0.5), 1.4, rot=(10, 0, 90), comp=2.8)
    for k, y in enumerate((7.4, 5.4)):
        hh = O2.faz_grupo(("taco", "jovem")[k], f"g{k}"); hh.raiz.location = (-21.3, y, 0); hh.raiz.rotation_euler.z = math.radians(-90)
    C((-17.3, 5.6, 0.16), (-18.8, 6.5, 0.18), 18, 2.8, foco=(-18.5, 6.2, 0.15))


@reg("5D", "noite2")
def p5D_v3():
    p5C_v3()


# ====================================================================== v4 (26/10): "parece uma lanterna, não dá para identificar; o fundo de 4A tem que enriquecer;
# 4C simplista demais; captar mais cenas próximas (aí não precisa expandir o cenário); explorar tipos de câmera"
mov("3C 3C2 4A 4B 4C 4D 4E 5A")


@reg("3C", "tarde2")
def p3C_v4():
    noite_rica("tarde"); AN.padaria("pad", 3.4, 11.0); AN.poste("pl3", -1.2, 11.5, acesa=False)
    AN.carro("c3", -2.5, 7.0, rot=8, queimado=True); AN.lixeira("lx3", 0.2, 9.5); AN.caixote("cx4", 7.2, 9.6, 15, 2)
    AN.poca_agua("pq6", 3.0, 9.4, 2.0, 0.8, brilho=("#ffcf7a", 0.4), seed=4)
    CM(((3.4, 3.6, 1.7), (3.4, 11.0, 1.9), 28, 8.0, (3.4, 11.0, 1.9)), ((3.4, 6.4, 1.5), (3.4, 11.0, 1.7), 28, 8.0, (3.4, 11.0, 1.7)))


@reg("3C2", "tarde2")
def p3C2_v4():
    noite_rica("tarde"); AN.padaria("pad", 3.4, 11.0)
    k = 1.0 if FIM else 0.55
    for i, sx in enumerate((-0.2, 0.2)):
        O2.esfera("olhoL" + str(i), 0.09 * k, 0.03, 0.13 * k, O3.brilha("#eef6ea", 2.6), None, (3.4 + sx + 0.3, 13.0, 1.55), contorno=0.0, seg=16, an=10)
    O3.halo_cam("olhohalo", (3.7, 12.9, 1.55), 0.7, "#dfeadc", 0.3)
    CM(((3.9, 8.4, 1.5), (3.6, 13.0, 1.5), 50, 2.8, (3.6, 13.0, 1.55)), ((3.8, 9.6, 1.5), (3.6, 13.0, 1.5), 50, 2.8, (3.6, 13.0, 1.55)))


@reg("4A", "noite2")
def p4A_v4():
    noite_rica(); AN.beco_rico(); praca_noite(-17.5, 6.5); O3.halo_cam("contraluz2", (-17.0, 6.5, 2.2), 3.6, "#f2e2b0", 0.5)
    eu_rosto("eu", -8.0, 6.5, 90, boca="o", lid=0.05, olhar=-35)
    CM(((-6.0, 5.9, 1.55), (-8.0, 6.6, 1.5), 85, 2.0, (-8.0, 6.5, 1.5)), ((-6.8, 6.0, 1.55), (-8.0, 6.6, 1.5), 85, 2.0, (-8.0, 6.5, 1.5)))


@reg("4B", "noite2")
def p4B_v4():
    noite_rica(); AN.beco_rico(); AN.poste("pb4", -2.5, 3.6, acesa=True, rot=180)
    O3.halo_cam("contraluz", (-2.0, 6.5, 2.0), 4.2, "#f2e2b0", 0.55)
    AN.poca_agua("pqm", -5.2, 6.5, 1.7, 0.9, cor="#4a5a78", brilho=("#fff2c8", 0.5), seed=6)
    mx = -5.0 if FIM else -3.8
    AN.reflexo_na_poca("refl", mx - 0.2, 6.5)
    AN.mancha_parede("sombraM", (-6.4 if FIM else -5.6), 1.7, (1.3 if FIM else 0.8), 3.4, 5.25, +1, cor="#08080a", alfa=0.6)
    sem("so", "padeira", mx, 6.5, rot=-90, curva=1.0, seed=2)
    CM(((-9.8, 6.0, 0.42), (-4.4, 6.5, 1.15), 28, 4.0, (-4.4, 6.5, 1.2)), ((-9.0, 6.1, 0.42), (-4.4, 6.5, 1.15), 28, 4.0, (-4.4, 6.5, 1.2)))


def par_de_maos(sep, pose_a, pose_b, z=1.25, y=6.5, x=-9.0):
    """duas mãos frente a frente (macro): a do narrador (manga vermelha) vem da esquerda da imagem, a da Rita (manga rosada) da direita"""
    pa = empty("pa", None, (x, y + sep, z)); pa.rotation_euler.z = math.radians(180)
    pb = empty("pb", None, (x, y - sep, z + 0.012)); pb.rotation_euler.z = 0.0
    a = O3.Mao3D("mn", "esq", pa, (0, 0, 0), 1.0, manga_comp=0.9)
    b = O3.Mao3D("mr", "dir", pb, (0, 0, 0), 1.0, manga="#8a6c6a", manga_comp=0.9)
    a.pose(pose_a); b.pose(pose_b)
    return a, b


@reg("4C", "noite2")
def p4C_v4():
    noite_rica(); AN.beco_rico(); AN.poste("pb5", -2.5, 3.6, acesa=True, rot=180); O3.halo_cam("contraluz3", (-2.0, 6.5, 1.6), 4.2, "#f2e2b0", 0.6)
    par_de_maos((0.2 if FIM else 0.1), ("aberta" if FIM else "segura"), ("aberta" if FIM else "segura"))
    CM(((-9.95, 6.5, 1.2), (-9.0, 6.5, 1.2), 85, 2.0, (-9.0, 6.5, 1.2)), ((-9.95, 6.5, 1.2), (-9.0, 6.5, 1.2), 85, 2.0, (-9.0, 6.5, 1.2)))


@reg("4D", "noite2")
def p4D_v4():
    noite_rica(); AN.beco_rico()
    AN.poca_agua("pq5", -9.3, 6.4, 0.9, 0.55, brilho=("#ffcf7a", 0.4))
    O3.sueter3d("sue", (-9.3, 6.4, (0.03 if FIM else 0.42)), 2.6, dobrado=False)
    if FIM:
        for k, R in enumerate((0.25, 0.45, 0.7)):
            O3.anel(f"onda{k}", R, 0.006, O3.brilha("#b8c8dc", 0.8), None, (-9.3, 6.4, 0.014), eixo="Z", seg=36, contorno=0.0)
    CM(((-10.4, 6.0, 0.3), (-9.3, 6.4, 0.2), 50, 2.8, (-9.3, 6.4, 0.2)), ((-10.4, 6.0, 0.22), (-9.3, 6.4, 0.1), 50, 2.8, (-9.3, 6.4, 0.08)))


@reg("4E", "noite2")
def p4E_v4():
    noite_rica(); AN.beco_rico(); AN.poste("pb4", -2.5, 3.6, acesa=True, rot=180)
    for k, (x, y, ch) in enumerate(((-6.4, 6.5, "padeira"), (-5.4, 7.6, "mercado"), (-7.6, 5.4, "viz1"))):
        sem(f"so{k}", ch, x, y, rot=-90, curva=1.0, seed=3 + k)
    CM(((-13.0, 6.5, 1.5), (-4.5, 6.5, 1.3), 24, 8.0, (-6.0, 6.5, 1.3), -3.0), ((-12.5, 6.2, 1.5), (-9.5, 9.5, 1.4), 24, 8.0, (-9.5, 9.0, 1.3), -14.0))


@reg("5A", "noite2")
def p5A_v4():
    noite_rica(); AN.beco_rico(); praca_noite()
    rot = 28.0 if FIM else 0.0
    lan = O2.lanterna3d("lant", (-22.5, 5.0, 1.0), 1.0, rot=(0, 0, rot), comp=3.4)
    AN.poca_agua("pqa", -22.5, 2.5, 1.6, 0.8, brilho=("#fff2c8", 0.5), seed=2)
    mao = empty("pm", None, (-22.5, 5.16, 1.0)); mao.rotation_euler.z = math.radians(180 + rot)
    m = O3.Mao3D("mt", "dir", mao, (0, 0, 0), 1.0, manga="#354a3c", manga_comp=0.6); m.pose("segura")
    mao.location = (-22.5 + 0.0, 5.16 + 0.04, 1.0)
    CM(((-21.6, 5.55, 1.1), (-22.5, 4.9, 1.0), 50, 2.8, (-22.5, 5.0, 1.0)), ((-21.6, 5.55, 1.1), (-22.5, 4.9, 1.0), 50, 2.8, (-22.5, 5.0, 1.0)))

#V5-PART1
# ====================================================================== v5 (26/10/2026): sequências 6 a 17 com a direção aprovada nas sequências 3 a 5
# luz que conta a história (âmbar = gente, azul = perigo, borda fria = Sem-Osso), cenário rico em camadas, mais planos próximos (macro, close, detalhe) e câmera
# variada: POV, contra-plongée, grua, por cima do ombro, câmera de objeto, rack focus, travelling, tilt. Doc: personagem/abrigo/decupagem-parte2-v3-seq6a17.md
mov("7F 6A 6B 6C 6D 6E 7A 7B 7C 7D 7E 7G 7H 8A 8B 8C 8D 9A 9B 9C 9D 9E 10A 10B 10C 10D 10E 11A 11B 11C 11D 11E 12A 12B 12C 12D 12E 12F "
    "13A 13B 13C 13D 13E 13F 14A 14B 14C 14D 14E 15A 15B 15B2 15B3 15C 15D 15E 15F 16A 16B 16C 16D 16F 17A 17B 17C")


def gr(chave, x, y, alvo=None, rot=None, boca="reta", lid=0.35, nome=None, sentado=0.0, **pose):
    """um do grupo do galpão: de pé (ou sentado numa altura 'sentado'), olhando para o alvo"""
    h = O2.faz_grupo(chave, nome or ("g_" + chave))
    h.raiz.location = (x, y, 0)
    p = dict(ombro=(-4, 4), cotovelo=(-12, -12), abre=(6, 6)); p.update(pose)
    if sentado:
        p.update(quadril=(-88, -88), joelho=(88, 88), alt=sentado)
    h.pose(**p); h.rosto(boca=boca, lid=lid)
    if alvo is not None:
        olha(h, (alvo[0], alvo[1], 0))
    if rot is not None:
        h.raiz.rotation_euler.z = math.radians(rot)
    return h


def eu_(x, y, rot=0.0, boca="reta", lid=0.3, olhar=0.0, nome="eu", chao=False, **pose):
    """o narrador de vermelho; chao=True senta no chão com as pernas esticadas"""
    p = dict(ombro=(-3, 5), cotovelo=(-10, -10), abre=(4, 4)); p.update(pose)
    if chao:
        p.update(quadril=(-88, -88), joelho=(4, 4), alt=0.1)
    h = SA.ator3("eu", nome, x, y, rot=rot, pose=p, rosto=dict(boca=boca, lid=lid))
    h.cabeca.rotation_euler.z = math.radians(olhar)
    return h


def mao_cor(nome, lado, pulso, dir_braco, manga, flexao=0.0, pose="aberta", escala=1.0, roll=0.0, manga_comp=1.5):
    """a mão 3D de alguém do grupo: igual à S3.mao_braco, mas com a manga da roupa dele (a vermelha é só do narrador)"""
    d = Vector(dir_braco).normalized()
    piv = empty(nome + "_piv", None, tuple(pulso))
    piv.rotation_euler = (math.asin(max(-1.0, min(1.0, d.z))), 0, math.atan2(-d.x, d.y))
    m = O3.Mao3D(nome, lado, piv, (0, 0, 0), escala, manga=manga, manga_comp=manga_comp)
    m.raiz.rotation_euler = (0, math.radians(roll), 0)
    m.pose(pose); m.gira(dobra=flexao)
    return m, piv


def manga_de(chave):
    return O2.GRUPO[chave]["roupa"]


def galo(h):
    """o galo na testa do narrador (a pancada do 5B)"""
    p = h._sobre_cabeca(0.07, 0.085, 1.0)
    O2.esfera("galo", 0.05, 0.035, 0.045, O3.M("#4a2e3c", "#2e1c28", "#8a6a7a"), h._C, p, contorno=0.003, seg=16, an=10)


def pano_cinza(nome, loc, rot=(0, 0, 0), s=1.0):
    O3.caixa(nome, (0.2 * s, 0.15 * s, 0.025 * s), O3.M("#8a8a82", "#6a6a62"), None, loc, chanfro=0.01, rot=rot)


def pontas_dos_dedos(m):
    """posição no mundo da ponta de cada dedo da Mao3D (para pôr a gosma nas pontas)"""
    bpy.context.view_layer.update()
    out = []
    for cadeia in m.falanges:
        o = cadeia[2]
        out.append(o.matrix_world @ Vector((0, 0.03, 0)))
    return out


def cabo_a_frio():
    pass


# ---------------------------------------------------------------- 6. acordar no galpão
@reg("6A", "galpao")
def p6A_v5():
    galpao(anel=1.25, narr=None)
    CM(((0.0, GC[1], 0.17), (0.0, GC[1] + 0.1, 2.2), 24, 1.2, (0.0, 6.0, 2.0)), ((0.0, GC[1], 0.19), (0.0, GC[1] + 0.2, 2.2), 24, 1.6, (0.0, GC[1] + 0.9, 1.7)))


@reg("6B", "galpao")
def p6B_v5():
    galpao(anel=1.1, narr=None)
    CM(((-0.12, GC[1], 0.17), (0.05, GC[1] + 0.2, 2.0), 14, 2.8, (0.5, 0.3, 1.7), 5.0), ((0.12, GC[1], 0.17), (0.0, GC[1] + 0.2, 2.0), 14, 2.8, (0.5, 0.3, 1.7), -4.0))


@reg("6C", "galpao")
def p6C_v5():
    galpao(narr="deitado")
    CM(((0.5, -3.4, 3.5), (0.0, -0.6, 0.2), 24, 8.0, (0.0, -0.8, 0.3)), ((0.25, -2.1, 2.5), (0.0, -0.6, 0.2), 28, 8.0, (0.0, -0.8, 0.3)))


@reg("6D", "galpao")
def p6D_v5():
    galpao(quem=["taco", "cochicho", "jovem", "careca"], anel=1.8, narr=None)
    h = gr("radio", -0.55, -0.2, alvo=(0.0, GC[1]), ombro=(-75, -75), cotovelo=(-35, -35), abre=(10, -10), boca="reta", lid=0.4)
    bpy.context.view_layer.update()
    pf, pb = h.punho["F"].matrix_world.translation, h.punho["B"].matrix_world.translation
    m = (pf + pb) / 2
    O2.lanterna3d("lant", tuple(m + Vector((0, -0.04, 0))), 1.4, rot=(0, 0, (28 if FIM else 0)), comp=1.4)
    CM(((0.0, GC[1] - 0.1, 0.3), (m.x, m.y, m.z - 0.1), 35, 4.0, (m.x, m.y, m.z)), ((0.0, GC[1] + 0.2, 0.55), (m.x + 0.1, m.y, m.z), 35, 4.0, (m.x, m.y, m.z)))


@reg("6E", "galpao")
def p6E_v5():
    galpao(grupo=False)
    n = eu_(0.0, 0.0, 0, boca="o", lid=0.62); galo(n)
    O2.lanterna3d("lant", (-0.5, -1.05, 1.58), 1.4, rot=(0, 0, 18), comp=0.8)
    O3.halo_cam("flare", (-0.2, -0.9, 1.55), 0.55, "#eef4ff", 0.55)
    CM(((0.05, -1.7, 1.45), (0.0, 0.0, 1.42), 85, 2.0, (-0.5, -1.05, 1.58)), ((0.05, -1.7, 1.45), (0.0, 0.0, 1.42), 85, 2.0, (0.0, -0.18, 1.45)))


# ---------------------------------------------------------------- 7. "eles tavam esperando eu virar uma daquelas coisas"
def canos(h, tipo="taco"):
    """o cano ou taco na mão do grupo: segurado com as duas mãos na frente do corpo"""
    bpy.context.view_layer.update()
    pf, pb = h.punho["F"].matrix_world.translation, h.punho["B"].matrix_world.translation
    m = (pf + pb) / 2
    O2.taco3d("cano" + h.nome, tuple(m - Vector((0, 0, 0.3))), rot=(0, 0, 0))


@reg("7A", "galpao")
def p7A_v5():
    galpao(grupo=False)
    eu_(0.0, -1.9, 180, boca="reta", lid=0.4, chao=True, nome="eu")
    for k, (ch, x, y, tipo) in enumerate((("lider", 0.0, 1.5, None), ("radio", -1.3, 0.9, None), ("cochicho", 1.3, 0.9, None), ("taco", -0.8, -0.35, 1), ("jovem", 0.85, -0.3, 1),
                                          ("trancas", -1.75, -0.6, 1), ("menino", 1.8, -0.55, 1), ("careca", 2.4, 0.5, None), ("solto", -2.4, 0.4, 1))):
        h = gr(ch, x, y, alvo=(0.0, -1.9), boca="reta", lid=0.3, ombro=(-55, -55) if tipo else (-4, 4), cotovelo=(-45, -45) if tipo else (-12, -12))
        if tipo:
            canos(h)
    CM(((0.35, -3.5, 0.8), (0.0, 0.3, 1.3), 22, 2.8, (0.0, 0.2, 1.4)), ((0.2, -3.2, 0.85), (0.0, 0.3, 1.3), 22, 2.8, (0.0, 0.2, 1.4)))


@reg("7B", "galpao")
def p7B_v5():
    galpao(grupo=True, quem=["taco", "solto", "trancas", "lider"])
    ox, oy = -2.8, -1.4
    O2.taco3d("cano", (ox, oy, 0.62), rot=(0, 0, 0))
    mao_cor("mA", "dir", (ox + 0.12, oy - 0.34, 1.02), (-0.3, 1.0, 0.05), manga_de("taco"), flexao=0, pose="segura")
    mao_cor("mB", "esq", (ox - 0.1, oy - 0.32, 1.2), (0.3, 1.0, 0.0), manga_de("taco"), flexao=0, pose="segura")
    pts = [(ox + 0.03, oy - 0.02, 0.9), (ox + 0.12, oy - 0.1, 0.72), (ox + 0.16, oy - 0.2, 0.55), (ox + 0.08, oy - 0.26, 0.42), (ox - 0.04, oy - 0.2, 0.34), (ox - 0.1, oy - 0.1, 0.3), (ox - 0.02, oy, 0.28)]
    O2.tubo("corda", pts, [0.011] * 7, O3.M("#a8946a", "#7a6a48"), None, seg=10, tampa=2, contorno=0.002)
    CM(((ox + 0.3, oy - 1.5, 1.3), (ox, oy - 0.1, 0.95), 50, 2.8, (ox, oy - 0.3, 1.0)), ((ox + 0.15, oy - 1.2, 1.15), (ox, oy - 0.1, 0.95), 50, 2.8, (ox, oy - 0.3, 1.0)))


@reg("7C", "galpao")
def p7C_v5():
    galpao(grupo=False)
    n = eu_(0.0, 0.0, 0, boca="o", lid=0.1); galo(n)
    gr("radio", -0.5, -0.5, alvo=(0, 0), ombro=(-82, 4), cotovelo=(-62, -12), tronco=6)
    O2.lanterna3d("lant", (-0.6, -0.75, 1.5), 1.4, rot=(0, 0, -35), comp=0.9)
    CM(((0.9, -1.0, 1.5), (-0.15, -0.2, 1.5), 50, 2.0, (0.0, -0.19, 1.5)), ((0.75, -0.9, 1.5), (-0.15, -0.2, 1.5), 50, 2.0, (0.0, -0.19, 1.5)))


@reg("7D", "galpao")
def p7D_v5():
    galpao(grupo=False)
    eu_(0.0, 0.0, 0, boca="reta", lid=0.0)
    O2.lanterna3d("lant", (0.45, -0.6, 1.62), 1.4, rot=(0, 0, 150), comp=0.7, facho=True)
    CM(((0.0, -0.78, 1.5), (-0.07, 0.0, 1.5), 85, 1.8, (-0.07, -0.19, 1.5)), ((0.0, -0.55, 1.5), (-0.07, 0.0, 1.5), 85, 1.8, (-0.07, -0.19, 1.5)))


@reg("7E", "galpao")
def p7E_v5():
    galpao(grupo=False)
    pos = (("lider", 0.0, 2.2, (-1.2, 2.0)), ("radio", -1.1, 1.9, (0.0, 2.2)), ("cochicho", 1.1, 1.9, (0.0, 2.2)), ("taco", -0.65, 1.3, (0.7, 1.3)), ("jovem", 0.7, 1.3, (-0.7, 1.3)))
    for ch, x, y, al in pos:
        gr(ch, x, y, alvo=al, boca="reta", lid=0.3)
    CM(((0.25, -1.1, 1.85), (0.0, 2.0, 1.3), 35, 2.0, (0.0, 1.9, 1.5)), ((0.05, -0.9, 1.8), (0.0, 2.0, 1.3), 35, 2.0, (0.0, 1.9, 1.5)))


@reg("7F", "galpao")
def p7F_v5():
    galpao(grupo=False)
    a = gr("cochicho", 1.4, 0.7, alvo=(1.8, 0.7), tronco=18, cabeca=10, boca="o", lid=0.4)
    b = gr("taco", 1.85, 0.7, alvo=(1.3, 0.7), cabeca=8, boca="reta", lid=0.55)
    gr("lider", 0.1, 1.5, alvo=(1.3, 0.7)); gr("careca", 2.5, 1.4, alvo=(1.3, 0.7))
    CM(((1.5, -1.0, 1.55), (1.5, 0.7, 1.55), 50, 2.0, (1.5, 0.7, 1.56)), ((1.5, -0.75, 1.55), (1.5, 0.7, 1.55), 50, 2.0, (1.5, 0.7, 1.56)))


@reg("7G", "galpao")
def p7G_v5():
    galpao(grupo=False)
    for k in range(7):
        x = -3.0 + 1.0 * k
        gr(("lider", "radio", "cochicho", "taco", "jovem", "careca", "solto")[k], x, 1.7 + 0.15 * (k % 2), rot=0, boca="reta", lid=0.0 if k != 3 else 0.2)
    CM(((0.0, -0.8, 1.45), (-1.8, 1.7, 1.55), 28, 4.0, (-2.0, 1.7, 1.55)), ((0.0, -0.8, 1.45), (1.8, 1.7, 1.55), 28, 4.0, (2.0, 1.7, 1.55)))


@reg("7H", "galpao")
def p7H_v5():
    galpao(grupo=False)
    ox, oy = -1.6, -0.2
    pano_cinza("pano", (ox, oy, 1.12), rot=(0, 0, 10), s=1.2)
    mao_cor("mR", "dir", (ox + 0.04, oy + 0.17, 1.1), (-0.15, -1.0, 0.0), manga_de("radio"), pose="segura")
    mao_cor("mE", "esq", (ox + 0.04, oy - 0.17, 1.02), (0.0, 1.0, 0.1), "#b02a22", pose="aberta")
    CM(((ox + 0.7, oy - 0.6, 1.4), (ox, oy, 1.08), 35, 2.8, (ox, oy, 1.1)), ((ox + 0.6, oy - 0.5, 1.3), (ox, oy, 1.08), 35, 2.8, (ox, oy, 1.1)))



# ---------------------------------------------------------------- 8. "Cadê a Rita? Cadê o Zé? Ninguém ali sabia."
def anel_neutro(quem, r=1.9, c=(0.0, -0.8), a0=0.4, boca="reta", lid=0.3, olha_c=True, **pose):
    out = {}
    for j, ch in enumerate(quem):
        a = a0 + 2 * math.pi * j / len(quem)
        out[ch] = gr(ch, c[0] + r * math.sin(a), c[1] + r * math.cos(a) * 0.9, alvo=c if olha_c else None, boca=boca, lid=lid, **pose)
    return out


@reg("8A", "galpao")
def p8A_v5():
    galpao(grupo=False)
    anel_neutro(["lider", "radio", "cochicho", "taco", "jovem", "solto", "careca", "trancas", "menino"], 2.1, (0.0, -0.9))
    c = CM(((0.0, -0.9, 0.22), (0.0, 0.6, 2.0), 28, 4.0, (0.0, 1.2, 1.5)), ((0.0, -0.95, 1.0), (-1.2, 1.4, 1.25), 28, 4.0, (-1.6, 1.4, 1.3)))
    pov_maos(c, "aberta", "aberta")


@reg("8B", "galpao")
def p8B_v5():
    galpao(grupo=False)
    gr("lider", -0.5, 1.9, alvo=(1.6, 0.9)); gr("radio", 0.4, 1.9, alvo=(1.6, 0.9)); gr("cochicho", 2.9, 1.5, alvo=(1.6, 0.9)); gr("careca", 3.0, 0.3, alvo=(1.6, 0.9))
    z = E3.faz("ze", "zeverde"); z.raiz.location = (1.7, 0.9, 0); z.raiz.rotation_euler.z = math.radians(25 if FIM else 180)
    z.pose(ombro=(-5, 7), cotovelo=(-14, -10), abre=(5, 5)); z.rosto(boca="reta", lid=0.35)
    CM(((0.2, -0.9, 1.45), (1.6, 0.9, 1.4), 35, 4.0, (1.7, 0.9, 1.4)), ((0.4, -0.8, 1.45), (1.6, 0.9, 1.4), 35, 4.0, (1.7, 0.9, 1.4)))


@reg("8C", "galpao")
def p8C_v5():
    galpao(grupo=False)
    gr("trancas", -2.24, 1.0, rot=0, olha=(-18 if not FIM else 18), boca="triste", lid=0.5)
    gr("solto", -1.76, 1.15, rot=0, olha=(18 if not FIM else -18), boca="triste", lid=0.5)
    gr("jovem", -3.2, 1.8, rot=0, boca="reta"); gr("careca", -0.8, 2.0, rot=0, boca="reta")
    CM(((-2.0, -1.7, 1.58), (-2.0, 1.0, 1.58), 85, 2.0, (-2.0, 1.05, 1.62)), ((-2.0, -1.55, 1.58), (-2.0, 1.0, 1.58), 85, 2.0, (-2.0, 1.05, 1.62)))


@reg("8D", "galpao")
def p8D_v5():
    galpao(grupo=False)
    eu_(0.0, -1.25, 180, boca="triste", lid=0.4, chao=True, nome="eu")
    gr("radio", -1.3, 0.1, alvo=(0.4, 0.5)); gr("taco", -1.0, -0.9, alvo=(0.4, 0.2)); gr("cochicho", 1.7, 0.8, alvo=(0.4, 0.2)); gr("jovem", 1.5, -0.5, alvo=(0.4, 0.2))
    L = gr("lider", (0.5 if FIM else 0.9), (-0.35 if FIM else 1.5), alvo=(0.0, -1.25), boca="reta", lid=0.4)
    CM(((0.05, -3.0, 0.95), (0.3, 0.8, 1.35), 35, 2.8, (0.8, 1.4, 1.5)), ((0.05, -2.9, 0.9), (0.4, -0.2, 1.4), 35, 2.8, (0.5, -0.35, 1.5)))


# ---------------------------------------------------------------- 9. o líder conta: o ar, a gosma
@reg("9A", "galpao")
def p9A_v5():
    galpao(grupo=False)
    eu_(-0.5, -1.45, 160, boca="reta", lid=0.4, chao=True, nome="eu")
    L = gr("lider", 0.0, 1.9, alvo=(-0.2, -1.4), boca="reta", lid=0.5, ombro=(-50, -50), cotovelo=(-70, -70))
    bpy.context.view_layer.update()
    m = (L.punho["F"].matrix_world.translation + L.punho["B"].matrix_world.translation) / 2
    O3.cilindro("caneca", 0.045, 0.1, O3.M("#8a8a82"), None, (m.x, m.y - 0.02, m.z), seg=14)
    CM(((-0.7, -1.95, 1.0), (0.1, 1.9, 1.5), 85, 2.0, (0.0, 1.9, 1.55)), ((-0.55, -1.6, 1.05), (0.1, 1.9, 1.5), 85, 2.0, (0.0, 1.9, 1.55)))


@reg("9B", "flash")
def p9B_v5():
    S3.rua3(aberta=0.0, branco=True); S3.cogumelo(11.0)
    for k, (ch, x, y, rot) in enumerate((("viz1", -1.2, BY - 6.5, 180), ("viz2", 1.1, BY - 8.0, 175), ("viz3", -0.2, BY - 10.5, 185), ("viz4", 1.8, BY - 12.0, 170))):
        h = SA.ator3(ch, f"v{k}", x, y, rot=rot, pose=dict(ombro=(-110, -60), cotovelo=(-30, -50), abre=(8, 14), tronco=-6, cabeca=-14), rosto=dict(boca="o", lid=0.0))
    cena.dust(S3.pal("cinza"), 90, (-4, 4), 40, seed=8, color="#f4f1e6", alpha=0.85, y_range=(BY - 14.0, BY - 2.0), z_range=(0.3, 6.0), size=(0.01, 0.025))
    CM(((0.6, BY - 15.0, 0.9), (0.0, BY - 8.0, 5.0), 24, 5.6, (0.0, BY - 9.0, 1.5)), ((0.3, BY - 12.5, 1.0), (0.0, BY - 7.0, 5.5), 24, 5.6, (0.0, BY - 8.0, 1.5)))


@reg("9C", "flash")
def p9C_v5():
    S3.rua3(aberta=0.0, branco=True)
    s = sem("so", "padeira", 0.0, BY - 0.9, rot=0, curva=(0.8 if FIM else 0.5), seed=2)
    CM(((0.9, BY - 3.6, 1.3), (0.0, BY - 0.9, 1.3), 85, 2.8, (0.0, BY - 0.9, 1.3)), ((0.5, BY - 2.6, 1.3), (0.0, BY - 0.9, 1.3), 85, 2.0, (0.0, BY - 0.9, 1.3)))


@reg("9D", "flash")
def p9D_v5():
    S3.rua3(aberta=0.0, branco=True)
    k = 1.0 if FIM else 0.0
    m, piv = mao_cor("mao", "dir", (0.0, BY - 1.35, 1.0), (0.0, 1.0, 0.0), "#d8d0bb", pose="aberta")
    bpy.context.view_layer.update()
    for j, pt in enumerate(pontas_dos_dedos(m)):
        r = 0.012 + 0.012 * k
        O2.gosma(f"gd{j}", [(pt.x, pt.y, pt.z, 1.0, (r, r, r * (1.2 + 1.5 * k)))], res=0.004, brilhos=1, seed=j + 2)
        O2.pingo(f"pg{j}", None, (pt.x, pt.y, pt.z - 0.02), comp=0.03 + 0.09 * k, r=0.005)
    O2.gosma("palma", [(0.0, BY - 1.28, 1.015, 1.0, (0.05 + 0.03 * k, 0.03, 0.012 + 0.01 * k))], res=0.004, brilhos=2, seed=9)
    CM(((0.25, BY - 1.95, 1.2), (0.0, BY - 1.25, 1.0), 85, 2.0, (0.0, BY - 1.25, 1.0)), ((0.2, BY - 1.75, 1.12), (0.0, BY - 1.25, 0.98), 85, 2.0, (0.0, BY - 1.25, 0.98)))


@reg("9E", "flash")
def p9E_v5():
    S3.rua3(aberta=0.0, branco=True)
    k = 1.0 if FIM else 0.0
    O2.poca("p", 0.2, BY - 0.8, 0.5 + 0.55 * k, 0.3 + 0.3 * k, seed=4)
    O3.caixa("av", (0.45, 0.4, 0.04), O3.M("#5b4034", "#3e2c24"), None, (0.2 - 0.1 * k, BY - 0.8, 0.05), chanfro=0.0, rot=(0, 0, 14))
    CM(((1.2, BY - 1.8, 0.2), (0.2, BY - 0.8, 0.08), 18, 4.0, (0.2, BY - 0.8, 0.08)), ((0.7, BY - 1.6, 0.18), (0.4, BY - 0.8, 0.07), 18, 4.0, (0.4, BY - 0.8, 0.07)))


# ---------------------------------------------------------------- 10. os esqueletos
@reg("10A", "flash")
def p10A_v5():
    S3.rua3(aberta=0.0, branco=True)
    O3.caixa("av", (0.5, 0.4, 0.04), O3.M("#5b4034", "#3e2c24"), None, (0.0, BY - 0.9, 0.06), chanfro=0.0, rot=(0, 0, 14))
    O2.mancha("rast", [(0.2 + 0.3 * k, BY - 1.0 - 0.15 * k) for k in range(9)], larg=0.22, seed=4)
    t = 1.0 if FIM else 0.0
    gx, gy = 0.25 + 1.6 * t, BY - 1.05 - 0.75 * t
    O2.gosma("g", [(gx, gy, 0.0, 1.0, (0.3, 0.22, 0.07)), (gx + 0.1, gy - 0.04, 0.08, 1.0, (0.16, 0.13, 0.1)), (gx - 0.1, gy + 0.05, 0.05, 1.0, (0.1, 0.1, 0.07))], brilhos=3, seed=3)
    CM(((-0.5, BY - 2.0, 0.55), (0.1, BY - 0.95, 0.1), 35, 5.6, (0.15, BY - 1.0, 0.1)), ((0.8, BY - 2.7, 0.5), (1.8, BY - 1.75, 0.12), 35, 5.6, (1.85, BY - 1.8, 0.12)))


@reg("10B", "flash")
def p10B_v5():
    S3.rua3(aberta=0.0, carros=False); esq_pilar()
    O3.caixa("av2", (0.4, 0.35, 0.03), O3.M("#5b4034", "#3e2c24"), None, (-0.2, BY - 0.9, 0.025), chanfro=0.0, rot=(0, 0, 20))
    CM(((1.8, BY - 3.6, 1.15), (0.1, BY - 0.6, 0.6), 50, 4.0, (0.0, BY - 0.6, 0.7)), ((0.9, BY - 2.2, 0.8), (0.0, BY - 0.6, 0.68), 50, 4.0, (0.0, BY - 0.6, 0.7)))


@reg("10C", "noite2")
def p10C_v5():
    rua(); ossos_rua(26, 11)
    CM(((0.0, -3.0, 11.0), (0.0, 8.0, 0.0), 20, 11.0, (0.0, 8.0, 0.5)), ((0.0, -0.5, 5.5), (0.0, 9.0, 0.0), 22, 11.0, (0.0, 9.0, 0.5)))


@reg("10D", "noite2")
def p10D_v5():
    rua(); ossos_rua(8, 9)
    for k, y in enumerate((5.0, 6.2, 7.4)):
        O3.caixa(f"deg{k}", (3.0, 1.0, 0.22 + 0.2 * k), O3.M("#6f6e66", "#55544e"), None, (-3.4, y + 0.6, 0.11 + 0.1 * k), chanfro=0.01)
    O3B.esqueleto3d("esq_s", (-3.2, 6.0, 0.35), (0, 0, 90), quadril=(-88, -84), joelho=(4, 14), cabeca=15, poeira=0.5)
    O3B.esqueleto_deitado("esq_f", (0.6, 3.6), rumo=70, de_lado=0, z=0.1, poeira=0.6, seed=21)
    CM(((-1.2, 1.8, 0.9), (-3.0, 6.5, 0.6), 35, 4.0, (-3.0, 6.2, 0.6)), ((1.0, 1.8, 0.9), (-3.0, 6.5, 0.6), 35, 4.0, (-3.0, 6.2, 0.6)))


@reg("10E", "noite2")
def p10E_v5():
    rua(); O3B.esqueleto_deitado("cr", (0.0, 6.0), rumo=0, de_lado=0, z=0.1, poeira=0.6, seed=3)
    O3B.esqueleto_deitado("cr2", (0.9, 6.9), rumo=50, de_lado=90, z=0.1, poeira=0.6, seed=8)
    rz = 75.0 if FIM else 20.0
    O2.lanterna3d("lant", (1.5, 4.7, 0.55), 1.4, rot=(0, 0, rz), comp=1.8)
    CM(((0.1, 5.2, 0.45), (0.0, 6.0, 0.15), 85, 2.0, (0.0, 6.0, 0.15)), ((0.1, 5.4, 0.4), (0.0, 6.0, 0.15), 85, 2.0, (0.0, 6.0, 0.15)))


# ---------------------------------------------------------------- 11. os Sem-Osso
@reg("11A", "galpao")
def p11A_v5():
    galpao(quem=["radio", "taco"], narr=None)
    L = gr("lider", 0.0, 1.75, rot=0, boca="reta", lid=0.55)
    CM(((1.3, 0.4, 1.58), (0.0, 1.75, 1.55), 85, 2.0, (0.0, 1.55, 1.55)), ((1.1, 0.3, 1.58), (0.0, 1.75, 1.55), 85, 2.0, (0.0, 1.55, 1.55)))


@reg("11B", "galpao")
def p11B_v5():
    galpao(grupo=False)
    eu_(0.0, -0.8, 0, boca="o", lid=0.0)
    CM(((0.0, -1.6, 1.56), (0.0, -0.8, 1.56), 85, 2.0, (0.0, -1.0, 1.56), -6.0), ((0.0, -1.42, 1.56), (0.0, -0.8, 1.56), 85, 2.0, (0.0, -1.0, 1.56), -6.0))


@reg("11C", "noite2")
def p11C_v5():
    rua(); AN.poste("pz11", 3.5, 10.0, acesa=True, rot=180)
    t = 1.0 if FIM else 0.0
    O2.poca("p1", -1.4 + 1.0 * t, 7.0, 0.3 + 0.1 * t, 0.22 + 0.05 * t, seed=1)
    O2.mancha("m2", [(-1.0 + 0.1 * k, 7.0 + 0.04 * math.sin(k)) for k in range(10)], larg=0.12, seed=2)
    O2.gosma("p2", [(0.3, 7.0, 0.0, 1.0, (0.25 + 0.1 * t, 0.2 + 0.06 * t, 0.04))], brilhos=3, seed=2)
    O2.gosma("p3", [(1.6 - 0.9 * t, 7.0, 0.0, 1.0, (0.2, 0.17, 0.04))] + [(1.6 - 0.9 * t, 7.0, 0.06 + 0.07 * k, 1.0, (0.12 - 0.006 * k, 0.1 - 0.005 * k, 0.07)) for k in range(5)], brilhos=4, seed=3)
    AN.poca_agua("pq11", 0.3, 7.6, 1.8, 0.8, brilho=("#ffcf7a", 0.4), seed=2)
    CM(((0.0, 5.4, 0.55), (0.0, 7.0, 0.05), 28, 8.0, (0.0, 7.0, 0.1)), ((0.0, 5.9, 0.32), (0.0, 7.0, 0.05), 28, 8.0, (0.0, 7.0, 0.1)))


@reg("11D", "noite2")
def p11D_v5():
    rua(); AN.poste("pz11", 3.0, 11.0, acesa=True, rot=180)
    t = 1.0 if FIM else 0.0
    O2.poca("p1", -0.8, 7.0, 0.4, 0.28, seed=1)
    O2.gosma("p3", [(0.4, 7.0, 0.0, 1.0, (0.2, 0.17, 0.04))] + [(0.4 + 0.03 * math.sin(k), 7.0, 0.06 + 0.1 * k, 1.0, (0.14 - 0.007 * k, 0.12 - 0.006 * k, 0.08)) for k in range(int(9 - 3 * t))], brilhos=5, seed=3)
    sem("so", "padeira", 1.5, 7.2, rot=-100, curva=1.4, seed=9).raiz.location.z = (0.0 if FIM else -0.9)
    CM(((-0.9, 5.0, 0.3), (0.6, 7.0, 1.0), 35, 4.0, (0.8, 7.0, 0.9)), ((-0.7, 5.2, 0.25), (0.8, 7.0, 1.0), 35, 4.0, (1.0, 7.1, 1.0)))


@reg("11E", "noite2")
def p11E_v5():
    rua(); AN.poste("pz11", 0.0, 13.0, acesa=True, rot=180); AN.poste("pz12", -3.8, 9.0, acesa=False, rot=0)
    sem("so1", "mercado", -1.5, 8.5, rot=0, curva=1.0, seed=4); sem("so2", "viz1", 1.3, 7.4, rot=0, curva=1.0, seed=6)
    sem("so", "padeira", 0.1, 5.6 if not FIM else 5.0, rot=0, curva=1.0, seed=2)
    AN.poca_agua("pq11", 0.0, 4.2, 1.6, 0.9, cor="#4a5a78", brilho=("#fff2c8", 0.5), seed=6)
    CM(((0.2, 1.8, 1.0), (0.0, 5.6, 1.15), 35, 2.8, (0.0, 5.6, 1.2)), ((0.15, 2.8, 1.1), (0.0, 5.0, 1.2), 35, 2.8, (0.0, 5.0, 1.25)))



# ---------------------------------------------------------------- 12. os ossos na frente da nossa porta
@reg("12A", "flash")
def p12A_v5():
    S3.rua3(aberta=0.0, carros=False); esq_pilar()
    CM(((0.25, BY - 2.6, 0.9), (0.0, BY - 0.6, 0.82), 85, 2.0, (0.0, BY - 0.6, 0.8)), ((0.1, BY - 1.7, 0.86), (0.0, BY - 0.6, 0.82), 85, 2.0, (0.0, BY - 0.6, 0.8)))


@reg("12B", "flash")
def p12B_v5():
    S3.rua3(aberta=0.0, carros=False); S3.esqueletos_porta()
    CM(((-2.6, BY - 7.0, 0.45), (0.1, BY - 0.8, 1.1), 24, 5.6, (0.0, BY - 2.0, 0.4)), ((-1.5, BY - 4.4, 0.9), (0.1, BY - 0.8, 1.2), 24, 5.6, (0.0, BY - 1.5, 0.5)))


@reg("12C", "flash")
def p12C_v5():
    S3.p2E()
    CM(((1.75, BY - 2.05, 1.5), (-0.2, BY - 0.15, 1.6), 24, 4.0, (0.2, BY - 0.5, 1.5), -2.0), ((1.15, BY - 1.5, 1.5), (-0.2, BY - 0.15, 1.6), 24, 4.0, (0.2, BY - 0.5, 1.5), -2.0))


@reg("12D", "flash")
def p12D_v5():
    S3.p2F()
    bpy.context.view_layer.update(); c0 = bpy.context.scene.camera
    loc = Vector(c0.location); fw = c0.matrix_world.to_quaternion() @ Vector((0, 0, -1)); al = loc + fw * 1.5
    CM(((loc.x, loc.y, loc.z), tuple(al), 50, 3.2, tuple(al)), (tuple(loc + fw * 0.45), tuple(al), 50, 3.2, tuple(al)))


@reg("12E", "noite2")
def p12E_v5():
    rua(); AN.poste("pz12", -3.0, BY - 4.0, acesa=True, rot=0)
    sem("so", "padeira", 0.0, BY - 0.62, rot=180, curva=0.9, seed=2)
    CM(((1.8, BY - 1.6, 1.3), (0.0, BY - 0.62, 1.25), 35, 4.0, (0.0, BY - 0.62, 1.25)), ((1.4, BY - 1.0, 1.25), (0.0, BY - 0.62, 1.25), 35, 4.0, (0.0, BY - 0.62, 1.25)))


@reg("12F", "galpao")
def p12F_v5():
    galpao(grupo=False)
    eu_(0.0, -0.8, 0, boca="triste", lid=0.3)
    CM(((0.0, -2.6, 1.5), (0.0, -0.8, 1.5), 50, 2.0, (0.0, -1.0, 1.5)), ((0.0, -2.0, 1.5), (0.0, -0.8, 1.5), 50, 2.0, (0.0, -1.0, 1.5)))


# ---------------------------------------------------------------- 13. o rádio e o quadro de giz
def giz_cor(S, manga, riscado=0.0):
    """a mão de quem risca o quadro (com a manga dela) e o toco de giz; riscado = o quanto o risco novo já desceu"""
    dC = Vector((-0.10, 0.94, 0.32)).normalized()
    giz = O3B.giz3d("giz_na_mao", tuple(S - dC * 0.03), 1.0); O3B.orienta(giz, dC)
    d = Vector((-0.8, 0.5, 0.3)).normalized()
    q = Euler((math.asin(d.z), 0, math.atan2(-d.x, d.y))).to_quaternion()
    dedos = q @ Vector((0, math.cos(math.radians(4)), math.sin(math.radians(4))))
    pulso = Vector(S) - dC * 0.045 - dedos * 0.10
    mao_cor("mao_giz", "dir", tuple(pulso), tuple(d), manga, flexao=4.0, pose="pinca", roll=-10, manga_comp=1.9)
    topo = S.z + 0.09
    O3.caixa("risco_novo", (0.0085, 0.006, max(0.01, topo - S.z + riscado)), O3.M(O3B.GIZ, "#c8c2ae", "#ffffff"), None, (S.x, S.y + 0.003, (topo + S.z - riscado) / 2), chanfro=0.002, contorno=0.0)


@reg("13A", "galpao")
def p13A_v5():
    galpao(grupo=False)
    mao_cor("hL", "esq", (-2.28, 2.12, 0.9), (-1.0, 0.0, -0.05), manga_de("lider"), pose="pinca", flexao=-8)
    CM(((-3.1, 1.2, 1.12), (-2.55, 2.15, 0.95), 50, 2.8, (-2.5, 2.12, 0.95)), ((-2.95, 1.35, 1.05), (-2.55, 2.15, 0.95), 50, 2.8, (-2.5, 2.12, 0.95)))


@reg("13B", "galpao")
def p13B_v5():
    galpao(grupo=False)
    gr("radio", -2.6, 3.05, rot=0, ombro=(-40, -40), cotovelo=(-60, -60), boca="reta", lid=0.4)
    CM(((-1.3, 1.2, 1.5), (-2.6, 2.7, 1.2), 28, 2.8, (-2.6, 2.7, 1.3)), ((-1.6, 1.5, 1.5), (-2.6, 2.7, 1.2), 28, 2.8, (-2.6, 2.7, 1.3)))


@reg("13C", "galpao")
def p13C_v5():
    galpao(grupo=False)
    giz_cor(Vector((-3.5, 3.80, 1.30 - (0.07 if FIM else 0.0))), manga_de("radio"), riscado=(0.06 if FIM else 0.0))
    CM(((-2.7, 2.7, 1.45), (-3.4, 3.8, 1.3), 50, 2.8, (-3.5, 3.8, 1.3)), ((-2.8, 2.75, 1.4), (-3.4, 3.8, 1.3), 50, 2.8, (-3.5, 3.8, 1.3)))


@reg("13D", "galpao")
def p13D_v5():
    galpao(grupo=False)
    CM(((-3.7, 2.4, 1.5), (-3.3, 3.84, 1.4), 28, 2.8, (-3.3, 3.84, 1.4)), ((-1.9, 2.3, 2.0), (-1.6, 3.86, 2.1), 28, 2.8, (-1.6, 3.86, 2.1)))


@reg("13E", "galpao")
def p13E_v5():
    galpao(grupo=False)
    O3.halo_cam("vela_giz", (-3.0, 3.5, 1.7), 0.5, "#ffcf7a", 0.22)
    CM(((-3.3, 2.3, 1.42), (-3.3, 3.84, 1.38), 35, 4.0, (-3.3, 3.84, 1.38)), ((-3.3, 3.05, 1.4), (-3.3, 3.84, 1.38), 35, 4.0, (-3.3, 3.84, 1.38)))


@reg("13F", "galpao")
def p13F_v5():
    galpao(grupo=False)
    for k, ch in enumerate(("lider", "radio", "cochicho", "taco", "jovem", "solto", "careca", "trancas", "menino")):
        gr(ch, -3.2 + 0.8 * k, 1.5 + 0.12 * (k % 2), rot=0, boca="reta", lid=0.3)
    CM(((0.0, -3.4, 1.6), (0.0, 1.5, 1.4), 28, 5.6, (0.0, 1.5, 1.4)), ((0.0, -2.8, 1.6), (0.0, 1.5, 1.4), 28, 5.6, (0.0, 1.5, 1.4)))


# ---------------------------------------------------------------- 14. a voz na torre
@reg("14A", "galpao")
def p14A_v5():
    galpao(grupo=False)
    rnd = _rnd.Random(3)
    for k in range(16):
        O2.esfera(f"pz{k}", 0.004, 0.004, 0.004, O3.brilha("#ffe3a8", 3.0), None, (-2.7 + rnd.uniform(-0.15, 0.15), 2.0 + rnd.uniform(-0.2, 0.05), 0.95 + rnd.uniform(-0.12, 0.12)), contorno=0.0, seg=8, an=6)
    O3.halo_cam("brilho_r", (-2.5, 2.0, 1.0), 0.5, "#ffb860", 0.3)
    CM(((-2.68, 1.6, 1.0), (-2.68, 2.12, 0.97), 35, 2.8, (-2.68, 2.12, 0.97)), ((-2.68, 1.75, 1.0), (-2.68, 2.12, 0.97), 35, 2.8, (-2.68, 2.12, 0.97)))


@reg("14B", "galpao")
def p14B_v5():
    galpao(grupo=False)
    ps = [(-3.7, 1.2, "lider"), (-3.0, 0.5, "radio"), (-2.3, 0.3, "cochicho"), (-1.6, 0.6, "taco"), (-1.2, 1.3, "jovem"), (-3.4, -0.4, "solto"), (-2.0, -0.4, "careca"), (-0.9, 0.0, "trancas"), (-4.0, 0.3, "menino")]
    for x, y, ch in ps:
        gr(ch, x, y, alvo=(-2.6, 2.25), tronco=14, boca="reta", lid=0.2)
    O3.halo_cam("glow_r", (-2.5, 1.85, 1.0), 1.3, "#ffb860", 0.3)
    CM(((-2.6, 2.8, 1.3), (-2.4, 0.5, 1.5), 35, 2.8, (-2.4, 0.4, 1.5)), ((-2.55, 2.7, 1.25), (-2.4, 0.5, 1.5), 35, 2.8, (-2.4, 0.4, 1.5)))


@reg("14C", "galpao")
def p14C_v5():
    galpao(grupo=False)
    O3.caixa("alcapao", (0.9, 0.9, 0.02), O3.brilha("#5a78a8", 1.4), None, (4.6, 1.2, 4.1), chanfro=0.0, contorno=0.0)
    O3.halo_cam("luz_alcapao", (4.6, 1.2, 4.0), 1.2, "#7f9cc8", 0.28)
    L = gr("lider", 4.25, 1.2, rot=90, ombro=(-150, -150), cotovelo=(-20, -20), quadril=(-55, -10), joelho=(65, 10), boca="reta", lid=0.4)
    L.raiz.location.z = 2.3
    N = eu_(4.25, 1.2, 90, boca="reta", lid=0.3, ombro=(-150, -150), cotovelo=(-20, -20), quadril=(-40, -5), joelho=(50, 5)); N.raiz.location.z = 0.9
    CM(((4.3, -1.7, 1.2), (4.4, 1.2, 2.3), 28, 4.0, (4.4, 1.2, 2.0)), ((4.3, -1.5, 2.2), (4.4, 1.2, 3.2), 28, 4.0, (4.4, 1.2, 3.0)))


@reg("14D", "noite2")
def p14D_v5():
    telhado()
    L = gr("lider", -0.35, -1.5, rot=180, ombro=(-70, 5), cotovelo=(-40, -12), boca="reta", lid=0.4, nome="lid"); L.raiz.location.z = 14.0
    N = SA.ator3("eu", "eu", 0.35, -1.5, rot=180, rosto=dict(boca="reta", lid=0.3)); N.raiz.location.z = 14.0
    bpy.context.view_layer.update()
    m = L.punho["F"].matrix_world.translation
    O2.lanterna3d("lant", (m.x, m.y - 0.05, m.z), 1.4, rot=(0, 0, 140), comp=1.6)
    cena.dust({}, 80, (-3.0, 3.0), 40, seed=12, color="#cfd4de", alpha=0.7, y_range=(-4.0, 0.0), z_range=(14.0, 16.5), size=(0.008, 0.02))
    CM(((0.0, 0.9, 15.1), (0.0, -1.5, 14.9), 35, 2.8, (-0.05, -1.5, 15.2)), ((0.0, 0.4, 15.0), (0.0, -1.5, 14.9), 35, 2.8, (-0.05, -1.5, 15.2)))


@reg("14E", "noite2")
def p14E_v5():
    telhado()
    N = SA.ator3("eu", "eu", 0.0, -1.6, rot=180, rosto=dict(boca="reta", lid=0.3)); N.raiz.location.z = 14.0
    CM(((0.0, -2.9, 15.7), (0.0, -1.6, 15.7), 50, 2.8, (0.0, -1.6, 15.7)), ((0.0, -3.0, 15.6), (36.0, 520.0, 115.0), 85, 4.0, (36.0, 520.0, 100.0)))


# ---------------------------------------------------------------- 15. só eu
@reg("15A", "galpao")
def p15A_v5():
    galpao(grupo=False)
    for k, ch in enumerate(("lider", "radio", "cochicho", "taco", "jovem", "solto", "careca", "trancas", "menino")):
        gr(ch, -3.2 + 0.8 * k, 1.3 + 0.1 * (k % 2), rot=0, boca="reta", lid=0.2)
    CM(((-2.4, -0.7, 1.62), (-2.4, 1.3, 1.6), 50, 2.8, (-2.4, 1.3, 1.62)), ((2.4, -0.7, 1.62), (2.4, 1.3, 1.6), 50, 2.8, (2.4, 1.3, 1.62)))


@reg("15B", "galpao")
def p15B_v5():
    galpao(quem=["taco", "cochicho"], narr=None)
    gr("lider", 0.0, 1.75, rot=0, boca="triste", lid=0.78, cabeca=18)
    CM(((0.95, -0.1, 1.62), (0.0, 1.75, 1.55), 85, 2.0, (0.0, 1.75, 1.55)), ((0.8, 0.2, 1.62), (0.0, 1.75, 1.55), 85, 2.0, (0.0, 1.75, 1.55)))


def mao_pingando(nome, lado, pulso, dir_braco, manga, k=1.0, pose="relaxada"):
    """a mão do líder com as pontas dos dedos já viradas gosma: um brilho de óleo e pingos (eles também vão derreter)"""
    m, piv = mao_cor(nome, lado, pulso, dir_braco, manga, pose=pose)
    for j, pt in enumerate(pontas_dos_dedos(m)):
        r = 0.011 * (0.7 + 0.5 * k)
        O2.gosma(f"{nome}_gd{j}", [(pt.x, pt.y, pt.z, 1.0, (r, r, r * 1.3))], res=0.003, brilhos=1, seed=j + 4)
        O2.pingo(f"{nome}_pg{j}", None, (pt.x, pt.y, pt.z - 0.015), comp=0.02 + 0.07 * k, r=0.004)
    return m


@reg("15B2", "galpao")
def p15B2_v5():
    galpao(grupo=False)
    ox, oy = -3.0, -0.6
    mao_pingando("hL", "esq", (ox + 0.3, oy, 0.78), (-1.0, 0.0, -0.1), manga_de("lider"), k=(1.0 if FIM else 0.5))
    CM(((ox + 0.2, oy - 0.8, 1.0), (ox + 0.12, oy, 0.74), 85, 2.0, (ox + 0.12, oy, 0.74)), ((ox + 0.2, oy - 0.75, 0.95), (ox + 0.12, oy, 0.74), 85, 2.0, (ox + 0.12, oy, 0.74)))


@reg("15B3", "galpao")
def p15B3_v5():
    galpao(grupo=False)
    ox, oy = -3.0, -0.6
    mao_cor("mn", "dir", (ox + 0.08, oy - 0.15, 1.02), (0.0, 1.0, 0.05), "#b02a22", pose="aberta")
    mao_pingando("hL", "esq", (ox - 0.02, oy + 0.45, 1.05), (0.0, -1.0, 0.0), manga_de("lider"), k=1.0, pose="relaxada")
    CM(((ox + 0.1, oy - 0.85, 1.1), (ox + 0.04, oy + 0.2, 1.03), 85, 1.8, (ox, oy + 0.4, 1.05)), ((ox + 0.1, oy - 0.85, 1.1), (ox + 0.04, oy + 0.2, 1.03), 85, 1.8, (ox + 0.08, oy - 0.12, 1.02)))


@reg("15C", "galpao")
def p15C_v5():
    galpao(grupo=False)
    for k, ch in enumerate(("lider", "radio", "cochicho", "taco", "jovem", "solto", "careca", "trancas", "menino")):
        a = math.radians(-100 + 25 * k)
        gr(ch, 2.0 * math.sin(a), -1.0 + 2.0 * math.cos(a), alvo=(0.0, -1.0), boca="reta", lid=0.0)
    CM(((0.0, -1.0, 1.55), (-1.6, 0.9, 1.5), 24, 2.8, (-1.7, 0.9, 1.5), 3.0), ((0.0, -1.0, 1.55), (1.6, 0.9, 1.5), 24, 2.8, (1.7, 0.9, 1.5), -3.0))


def sueter_aberto(nome, x, y):
    """o suéter da Rita aberto no chão: corpo, duas mangas esticadas, gola e listra creme"""
    m = O3.M("#8e302b", "#64211f", "#d08070")
    O3.caixa(nome + "_c", (0.5, 0.6, 0.035), m, None, (x, y, 0.02), chanfro=0.015, rot=(0, 0, 12))
    O3.caixa(nome + "_l", (0.51, 0.07, 0.038), O3.M("#a89f86"), None, (x, y + 0.02, 0.022), chanfro=0.004, contorno=0.0, rot=(0, 0, 12))
    for sg in (-1, 1):
        O3.caixa(f"{nome}_m{sg}", (0.55, 0.16, 0.035), m, None, (x + sg * 0.42, y + 0.1, 0.02), chanfro=0.015, rot=(0, 0, 12 + sg * 28))
    O3.caixa(nome + "_g", (0.18, 0.08, 0.04), O3.M("#64211f"), None, (x + 0.05, y + 0.3, 0.03), chanfro=0.02, rot=(0, 0, 12))


@reg("15D", "noite2")
def p15D_v5():
    rua(); sueter_aberto("sue", 0.5, 8.0)
    cena.dust({}, 70, (-2.0, 3.0), 40, seed=14, color="#d8dde8", alpha=0.8, y_range=(6.5, 9.5), z_range=(0.2, 2.0), size=(0.01, 0.02))
    CM(((0.2, 6.9, 1.4), (0.5, 8.0, 0.05), 35, 4.0, (0.5, 8.0, 0.05)), ((0.3, 7.2, 0.8), (0.5, 8.0, 0.05), 35, 4.0, (0.5, 8.0, 0.05)))


@reg("15E", "galpao")
def p15E_v5():
    galpao(grupo=False)
    n = eu_(0.0, -0.8, 0, boca="reta", lid=0.3, ombro=(-38, 5), cotovelo=(-88, -10))
    n.fecha_mao("F")
    bpy.context.view_layer.update()
    m = n.punho["F"].matrix_world.translation
    pano_cinza("pano_m", (m.x, m.y - 0.03, m.z - 0.03), rot=(10, 20, 30), s=1.2)
    CM(((0.3, -2.2, 0.9), (0.0, -0.8, 0.95), 50, 2.0, (0.0, -1.0, 0.95)), ((0.2, -2.2, 1.35), (0.0, -0.8, 1.45), 50, 2.0, (0.0, -1.0, 1.5)))


@reg("15F", "galpao")
def p15F_v5():
    galpao(grupo=False)
    for ch, (x, y) in PRE.items():
        h = gr(ch, x, y, alvo=((0.6, 3.8) if FIM else (0.0, 0.5)), boca=("o" if FIM else "reta"), lid=(0.0 if FIM else 0.3))
    eu_(GC[0], GC[1], rot=(180 if True else 0), boca=("o" if FIM else "reta"), lid=0.0)
    CM(((1.3, 3.4, 1.55), (0.0, -0.5, 1.35), 28, 5.6, (0.0, -0.3, 1.4)), ((1.2, 3.1, 1.55), (0.0, -0.5, 1.35), 28, 5.6, (0.0, -0.3, 1.4)))


# ---------------------------------------------------------------- 16. o portão
@reg("16A", "galpao")
def p16A_v5():
    galpao(grupo=False)
    cena.dust({}, 40, (-1.0, 2.4), 40, seed=15, color="#e8e0cc", alpha=0.7, y_range=(3.0, 3.8), z_range=(1.0, 3.1), size=(0.008, 0.018))
    CM(((-0.9, -3.6, 1.6), (0.6, 3.86, 1.6), 24, 8.0, (0.6, 3.86, 1.6)), ((-0.2, -1.9, 1.6), (0.6, 3.86, 1.6), 24, 8.0, (0.6, 3.86, 1.6)))


@reg("16B", "galpao")
def p16B_v5():
    galpao(grupo=False)
    O3.caixa("faixa_luz", (3.2, 0.36, 0.012), O3.brilha("#aac4f0", 2.4), None, (0.6, 3.68, 0.008), chanfro=0.0, contorno=0.0)
    dx = 0.5 if FIM else 0.0
    for k, (x, rx) in enumerate(((0.1, 0.07), (0.55, 0.12), (1.0, 0.06))):
        cena.ground_disc(f"sombra{k}", rx * 1.6, 0.12, cena.amat(f"sombra{k}_m", "#05060a", 1.0, 0.97, ("radial", 0.9)), (x + dx, 3.7, 0.02), n=20)
    cena.poly_mesh("glow_az", [(-1.0, 3.83, 0.0), (2.2, 3.83, 0.0), (2.2, 3.83, 0.6), (-1.0, 3.83, 0.6)], cena.amat("glow_az_m", "#aac4f0", 1.0, 0.3, ("radial", 1.0)))
    CM(((0.6, 2.7, 0.3), (0.6, 3.7, 0.02), 24, 4.0, (0.6, 3.7, 0.02)), ((0.6, 2.95, 0.22), (0.6, 3.7, 0.02), 24, 4.0, (0.6, 3.7, 0.02)))


@reg("16C", "galpao")
def p16C_v5():
    galpao(grupo=False)
    b = bpy.data.objects.get("galpao_portao_barra")
    if b and FIM:
        b.location.x -= 0.07; b.location.z += 0.012
    cena.dust({}, 30, (1.5, 2.8), 40, seed=17, color="#e8e0cc", alpha=0.8, y_range=(3.6, 3.78), z_range=(1.2, 3.0), size=(0.006, 0.014))
    CM(((1.7, 2.9, 1.5), (2.3, 3.76, 1.17), 50, 2.8, (2.3, 3.76, 1.17)), ((1.8, 2.95, 1.45), (2.3, 3.76, 1.17), 50, 2.8, (2.3, 3.76, 1.17)))


@reg("16D", "galpao")
def p16D_v5():
    galpao(grupo=False)
    eu_(0.5, 1.7, 180, boca="reta", lid=0.2, nome="eu")
    L = gr("lider", 1.0, 1.55, rot=180, ombro=(-60, 4), cotovelo=(-70, -12), boca="reta", lid=0.4)
    CM(((0.9, 3.4, 1.5), (0.6, 1.7, 1.4), 50, 2.8, (0.55, 1.7, 1.45)), ((0.8, 3.1, 1.5), (0.6, 1.7, 1.4), 50, 2.8, (0.55, 1.7, 1.45)))


@reg("16E", "galpao")
def p16E_v5():
    galpao(grupo=False)
    N = eu_(0.6, 2.7, 180, boca="o", lid=0.0, nome="eu")
    O3.halo_cam("rim_fogo", (0.6, 2.2, 1.6), 0.7, "#ff9a3c", 0.3)
    CM(((0.55, 3.55, 1.52), (0.6, 2.7, 1.52), 85, 4.0, (0.6, 2.9, 1.52)), ((0.55, 3.4, 1.52), (0.6, 2.7, 1.52), 85, 4.0, (0.6, 2.9, 1.52)))


@reg("16F", "galpao")
def p16F_v5():
    galpao(grupo=False)
    eu_(0.6, 3.1, 180, boca="reta", lid=0.2)
    CM(((0.6, 1.7, 1.5), (0.6, 3.86, 1.4), 50, 1.8, (0.6, 3.86, 1.4)), ((0.6, 2.35, 1.48), (0.6, 3.86, 1.4), 50, 1.8, (0.6, 3.86, 1.4)))


# ---------------------------------------------------------------- 17. o ferrolho
@reg("17A", "galpao")
def p17A_v5():
    galpao(grupo=False)
    S3.mao_em("mao", "dir", (2.33, 3.70, 1.17), (-0.3, 1.0, -0.1), pose="segura")
    CM(((1.2, 2.4, 1.3), (2.3, 3.76, 1.15), 35, 4.0, (2.3, 3.76, 1.15)), ((1.35, 2.55, 1.28), (2.3, 3.76, 1.15), 35, 4.0, (2.3, 3.76, 1.15)))


@reg("17B", "galpao")
def p17B_v5():
    galpao(grupo=False)
    eu_(0.6, 3.6, 180, boca="reta", lid=1.2, olhar=-85, nome="eu")
    O3.halo_cam("bafo", (0.6, 3.78, 1.42), 0.3, "#c9d2dc", 0.22)
    cena.poly_mesh("faixa_az", [(0.4, 3.82, 1.0), (0.8, 3.82, 1.0), (0.8, 3.82, 1.9), (0.4, 3.82, 1.9)], cena.amat("faixa_az_m", "#aac4f0", 1.0, 0.18))
    CM(((1.5, 3.5, 1.5), (0.6, 3.6, 1.5), 85, 1.8, (0.6, 3.6, 1.5)), ((1.2, 3.45, 1.5), (0.6, 3.6, 1.5), 85, 1.8, (0.6, 3.6, 1.5)))


@reg("17C", "galpao")
def p17C_v5():
    galpao(grupo=False)
    b = bpy.data.objects.get("galpao_portao_barra")
    m = S3.mao_em("mao", "dir", (2.33, 3.70, 1.17), (-0.3, 1.0, -0.1), pose="segura")
    if FIM:
        if b:
            b.location.x -= 0.3
        bpy.data.objects["mao_piv"].location.x -= 0.3
    CM(((1.9, 2.7, 1.2), (2.2, 3.76, 1.17), 85, 2.8, (2.2, 3.76, 1.17)), ((1.8, 2.8, 1.2), (2.1, 3.76, 1.17), 85, 2.8, (2.1, 3.76, 1.17)))

#V5-END1

# ====================================================================== principal
def main():
    argv = sys.argv[sys.argv.index("--") + 1:]
    if "--list" in argv:
        for k_, f_ in BUILD.items():                                      # roda o corpo uma vez a seco só para registrar o MOV? não: MOV é declarado nos builders
            pass
        print(" ".join(sorted(BUILD))); print(json.dumps(GRADE, ensure_ascii=False)); print("MOV " + " ".join(sorted(MOV))); return
    nome, out = argv[0], argv[1]
    global FIM
    FIM = "--fim" in argv
    k = float(argv[argv.index("--scale") + 1]) if "--scale" in argv else 0.5
    smp = int(argv[argv.index("--samples") + 1]) if "--samples" in argv else 16
    lib.reset(int(1080 * k), int(1920 * k), 24, smp)
    sc = bpy.context.scene; sc.frame_start, sc.frame_end = 1, 24
    BUILD[nome]()
    sc.frame_set(1)
    sc.render.filepath = out
    bpy.ops.render.render(write_still=True)


if __name__ == "__main__":
    main()
