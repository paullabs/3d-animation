"""PCC, versão 2: um acontecimento a cada ~1 s (roteiros/decupagem-pcc.md).
Cada CENÁRIO monta a ação do seu trecho com tempos absolutos e tem vários enquadramentos que se trocam por marcadores
(limpo.cortes). Os PLANOS só escolhem o intervalo de quadros a renderizar.
blender -b -P prod_pcc2.py -- PLANO OUT [--scale 1] [--samples 16] [--at t1,t2] [--frames a,b] [--list]"""
import sys, os, math, json, random
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy, lib
from lib import *
import cena, props, limpo, dinheiro as D, insertos as I, semantico as S
from heroi import Heroi
from anim import Timeline
from acting import Actor
from prod_pcc import F, wt, hero, finish, FPS

PLANOS = {}


def plano(name, t0, t1, cenario):
    PLANOS[name] = (t0, t1, cenario)


def ctx(sc, t0, t1):
    return dict(sc=sc, f0=F(t0), f1=F(t1) - 1, t0=t0, t1=t1, F=F)


# ====================================================================== GANCHO: a cela (0 - 1.37 e 2.83 - 6.41)
def cela(c):
    sc = c["sc"]
    P = dict(cena.PAL["drama"])
    sc.world.node_tree.nodes["Background"].inputs[0].default_value = (0.01, 0.015, 0.03, 1)
    END = F(6.6)
    props.cela_interior(P, END + 30)
    gr = bpy.data.objects["grade_frente"]
    gr.location.z = 4.8; key(gr, "location", F(2.9), "BEZIER")
    props.drop(gr, F(3.02), 0.0, 4.8, frames=6, bounce=0.04)
    # a luz de cima (a única que bate nele) e a poça no chão
    cone = cena.poly_mesh("lamp_cone", [(-1, 0, 0), (1, 0, 0), (0.16, 0, 1), (-0.16, 0, 1)], cena.amat("lamp_cone_m", "#e9f1ff", 1.0, 0.09, ("shaft", 1.5, 0.8)))
    cone.location = (0.15, 0.45, 0.0); cone.scale = (0.95, 1, 4.6)
    cena.ground_disc("lamp_poca", 0.8, 0.45, cena.amat("lamp_poca_m", "#5d6f96", 1.0, 0.5, ("radial", 1.4)), (0.15, 0.1, 0.003), n=48)
    H = hero(c, P)
    tl = Timeline(H, -10, END, FPS); tl.stand(-10, END, 0.15); a = Actor(tl, 0.15)
    tl.intent(-10, head=10, torso=3)
    tl.face(-10, 0.0, lid="sono", lidv=0.7, brow=-6, mouth="reta", look=(0.0, -0.6))
    tl.intent(F(0.3), head=10, torso=3); tl.intent(F(0.55), head=-3, torso=0)
    tl.face(F(0.4), 1.0, lid="esperto", lidv=0.55, brow=-9, mouth="reta", look=(0.15, 0.05))           # "Imagina": ergue o olhar
    f = a.point(F(0.5), up=6)                                                                       # "comandar"
    tl.face(F(0.72), 1.0, lid="esperto", lidv=0.6, brow=-12, mouth="sorriso", look=(1.0, 0.1))
    a.release(F(2.3), 12)
    tl.face(F(2.85), 1.0, lid="sono", lidv=0.62, brow=-8, mouth="reta", look=(0.2, 0.0))
    tl.face(F(3.6), 1.0, lid="sono", lidv=0.6, brow=-6, mouth="reta", look=(0.9, 0.25))              # olha a luz da polícia
    tl.face(F(4.6), 1.0, lid="esperto", lidv=0.6, brow=-8, mouth="reta", look=(0.1, 0.0))
    tl.intent(F(5.25), head=0, torso=0); tl.intent(F(5.5), head=-6, torso=-2)
    tl.face(F(5.33), 1.0, lid="esperto", lidv=0.55, mouth="sorriso", brow=-10, browtilt=0.014, look=(0.0, 0.05))   # "o chefe"
    tl.face(F(5.86), 1.0, lid="esperto", lidv=0.5, mouth="sorriso", brow=-4, browup=0.012, browtilt=0.018, look=(0.0, 0.05))  # "PCC"
    finish(H, tl, -10, END)
    # polícia: vermelho e azul se alternando pela janela (lavagem que pega o rosto no close)
    red = cena.disc("pol_r", 1.5, cena.amat("pol_r_m", "#ff2d3d", 1.0, 0.17, ("radial", 1.4)), (1.4, -0.45, 1.75))
    blu = cena.disc("pol_b", 1.5, cena.amat("pol_b_m", "#2d7bff", 1.0, 0.2, ("radial", 1.4)), (1.4, -0.45, 1.75))
    jr = cena.disc("pol_jr", 0.7, cena.amat("pol_jr_m", "#ff2d3d", 1.6, 0.55, ("radial", 1.2)), (1.3, 1.4, 2.5))
    jb = cena.disc("pol_jb", 0.7, cena.amat("pol_jb_m", "#2d7bff", 1.6, 0.55, ("radial", 1.2)), (1.3, 1.4, 2.5))
    t = 3.6; sr = [(F(-1), False)]; sb = [(F(-1), False)]
    while t < 6.6:
        sr += [(F(t), True), (F(t) + 4, False)]; sb += [(F(t) + 5, True), (F(t) + 9, False)]
        t += 0.42
    for o, sq in ((red, sr), (jr, sr), (blu, sb), (jb, sb)):
        props.blink_vis(o, sq, True)
    cams = limpo.cortes(c, [
        (0.0, [(0.0, (0.15, -1.18, 1.46)), (0.85, (0.15, -1.06, 1.47))], dict(lens=50, focus=1.15, fstop=0.8)),          # 1 PP
        (0.85, [(0.85, (0.5, -1.75, 1.12)), (1.37, (0.58, -1.62, 1.12))], dict(lens=35, focus=1.7, fstop=0.8)),           # 2 PM baixo
        (2.83, [(2.83, (0.15, -2.95, 1.32)), (3.55, (0.15, -2.75, 1.32))], dict(lens=50, focus=2.9, fstop=1.0)),          # 4 pela grade
        (3.55, [(3.55, (0.28, -1.0, 1.5)), (4.71, (0.22, -0.92, 1.5))], dict(lens=50, focus=0.98, fstop=0.8)),            # 5 PP polícia
        (4.71, [(4.71, (0.62, -3.9, 1.6)), (5.31, (0.55, -3.75, 1.6))], dict(lens=35, focus=3.8, fstop=1.4)),             # 6 PG cela
        (5.31, [(5.31, (0.1, -1.06, 1.36)), (6.41, (0.12, -0.9, 1.38))], dict(lens=50, focus=1.0, fstop=0.8)),            # 7 PP baixo
    ])
    props.shake_rig(cams[2][1], F(3.02) + 3, 8, 0.03, seed=4)
    # a luz acende tremendo no primeiro quadro (lâmpada fluorescente)
    dk, a_dk = props.dim(cams[0][0], "acende", "#02030a")
    props.wash(a_dk, [(1, 0.95), (3, 0.25), (4, 0.85), (6, 0.12), (7, 0.55), (9, 0.0)], "CONSTANT")


# ====================================================================== GANCHO: 40 mil pessoas (1.37 - 2.83)
def multidao(c):
    sc = c["sc"]
    cena.sets.FOG.update(color="#0c1430", near=40.0, far=420.0, max=0.8)
    props.skywall("ceu_m", 900, [(-100, "#0f1838"), (60, "#0a1230"), (200, "#050a1a"), (500, "#020409")], -3000, 3000, -400, 900)
    sc.world.node_tree.nodes["Background"].inputs[0].default_value = (0.004, 0.006, 0.015, 1)
    cols = ["#2b3866", "#30406f", "#27335d", "#344576", "#2d3b6a"]
    crowd, heads, prof = props.multidao("multidao", 40000, 2.0, 9.0, 340.0, -0.50, 0.04, cols, seed=11, head="#161e3a")
    props.terreno("encosta", prof, 9.0, 340.0, color="#0a1026")
    # luz única: o facho que desce da janela da cela no alto e ilumina o meio da multidão
    ty, wz = 360.0, 73.0
    cena.flat("torre", cena.rect(-60, -40, 60, 88), "#151d38", ty, fog=False)
    cena.flat("torre_c", cena.rect(-14, 88, 14, 104), "#151d38", ty, fog=False)
    for k in range(-9, 10):
        for r in range(6):
            if not (abs(k) <= 1 and r == 4):
                cena.flat(f"torre_j{k}_{r}", cena.rect(k * 6 - 1.0, 20 + r * 11, k * 6 + 1.0, 24 + r * 11), "#0c1124", ty - 0.3, fog=False)
    cena.flat("torre_jan", cena.rect(-3.0, wz - 2.2, 3.0, wz + 2.2), "#ffd9a0", ty - 0.6, 3.0, fog=False)
    for i in range(5):
        cena.flat(f"torre_jan_b{i}", cena.rect(-3.0 + 6.0 * (i + 0.5) / 5 - 0.18, wz - 2.2, -3.0 + 6.0 * (i + 0.5) / 5 + 0.18, wz + 2.2), "#1a1208", ty - 0.7, fog=False)
    cena.sets.glow("torre_jan_glow", "#ffb35c", 60, (0, ty - 2, wz), power=2.2, strength=0.9)
    cone = cena.poly_mesh("torre_cone", [(-1, 0, 0), (1, 0, 0), (0.08, 0, 1), (-0.08, 0, 1)], cena.amat("torre_cone_m", "#ffb35c", 1.0, 0.12, ("shaft", 1.2, 0.9)))
    cone.location = (0, ty - 4, 4); cone.scale = (70, 1, 70)
    cena.sets.glow("poca_multidao", "#ffc98a", 90, (0, 150, 12), power=1.5, strength=0.5)
    rnd = np.random.default_rng(5)
    idx = rnd.choice(len(heads), 14, replace=False)
    for i, j in enumerate(idx):
        h = heads[j]
        ln = props.fio(f"fio{i}", (0.0, ty - 5, wz - 1.0), (float(h[0]), float(h[1]), float(h[2]) + 0.3), w=0.12 + 0.0006 * float(h[1]), color="#ffcf8f", strength=2.0, alpha=0.4)
        t = 1.75 + 0.8 * (i / 14.0)
        ln.scale = (0.0001,) * 3; key(ln, "scale", F(t) - 1, "CONSTANT")
        ln.scale = (1, 1, 1); key(ln, "scale", F(t) + 4, "BEZIER")
    limpo.cortes(c, [(1.37, [(1.37, (0.0, 2.0, 2.4)), (2.0, (0.0, -2.0, 8.0)), (2.83, (0.0, -6.0, 15.0))], dict(lens=35, dof=False))])



# ====================================================================== GANCHO: o celular na cela (6.41 - 7.34)
def celular(c):
    limpo.estudio("aco", cx=0.0, cz=1.0, raio=0.35, wall_y=0.9, poeira=20)
    props.grade("grade_fundo", -1.0, 1.0, 0.3, 1.8, 0.7, "#05070d", n=9, w=0.025, rails=1)
    cena.disc("tela_luz", 0.17, cena.amat("tela_luz_m", "#bcd4ff", 1.0, 0.3, ("radial", 2.2)), (0.0, 0.05, 1.0))
    ph, bal = I.celular("cel", (0.0, 0.0, 1.0), 1.0)
    I.mao_segura("mao", ph)
    ph.rotation_euler = (0, math.radians(-8), 0); key(ph, "rotation_euler", F(6.41), "BEZIER")
    ph.rotation_euler = (0, math.radians(-4), 0); key(ph, "rotation_euler", F(7.34), "BEZIER")
    for i, (b, t) in enumerate(zip(bal, (6.3, 6.55, 6.8, 7.05))):
        S.pop(b, F(t), 1.0, 5, 0.12)
        props.blink_vis(b, [(F(5.0), False), (F(t) - 1, False), (F(t), True)], True)
    limpo.cortes(c, [(6.41, [(6.41, (0.035, -0.36, 0.985)), (7.34, (0.03, -0.32, 0.99))], dict(lens=50, focus=0.33, fstop=1.2))])


# ====================================================================== GANCHO: a escada dos 5 níveis (7.34 - 8.96 e 10.22 - 11.18)
def escada(c):
    sc = c["sc"]
    limpo.palco("noite", wall_y=3.0, spot=False, poeira=0, linhas=False, frames=F(11.4))
    P = limpo.P_de("noite")
    cores = ["#151b2d", "#171e32", "#1a2137", "#1c243c", "#202942"]
    root, parts = props.escada(0.6, colors=cores, numbers=False)
    SW, SH = props.STEP["SW"], props.STEP["SH"]
    tempos = [7.40, 7.52, 7.64, 7.76, 7.98]
    for k in range(1, 6):
        x0 = props.STEP["X0"] + (k - 1) * SW
        cx, cz = x0 + SW / 2, k * SH - 0.55
        props.txt(f"num{k}_apagado", str(k), 0.62, "#2a3352", (cx, 0.596, cz), None, ink=None)
        cor = "#ffd24a" if k == 5 else "#ffffff"
        n = props.txt(f"num{k}", str(k), 0.62, cor, (cx, 0.592, cz), None, ink=props.INK, ow=0.06)
        S.pop(n, F(tempos[k - 1]), 1.0, 6, 0.25)
        props.blink_vis(n, [(F(6.0), False), (F(tempos[k - 1]) - 1, False), (F(tempos[k - 1]), True)], True)
        props.poly(f"deg{k}_luz", cena.rect(x0, k * SH - 0.03, x0 + SW + (props.STEP["TERR"] if k == 5 else 0), k * SH), "#3a4870" if k < 5 else "#ffd24a", 0.597)
    # o topo é o único lugar com luz
    xt = props.STEP["X0"] + 4 * SW + 1.2
    cone = cena.poly_mesh("topo_cone", [(-1, 0, 0), (1, 0, 0), (0.2, 0, 1), (-0.2, 0, 1)], cena.amat("topo_cone_m", "#ffe2a0", 1.0, 0.13, ("shaft", 1.3, 0.85)))
    cone.location = (xt, 0.9, 5 * SH); cone.scale = (1.7, 1, 7.0)
    cena.sets.glow("topo_g", "#ffd07a", 4.0, (xt, 0.85, 5 * SH + 0.8), power=2.0, strength=0.9)
    cena.dust(dict(dust="#ffe6c0"), 40, (xt - 1.6, xt + 1.6), F(11.4), size=(0.008, 0.02), z_range=(5 * SH, 5 * SH + 5), y_range=(0.0, 0.9), alpha=0.5)
    q = props.interrogacao("pergunta", xt, 5 * SH + 2.1, 1.0, y=0.85)
    S.pop(q, F(10.25), 1.0, 8, 0.25)
    props.blink_vis(q, [(F(6.0), False), (F(10.25) - 1, False), (F(10.25), True)], True)
    H = hero(c, P)
    tl = Timeline(H, F(7.0), F(11.4), FPS); tl.stand(F(7.0), F(11.4), -0.25); a = Actor(tl, -0.25)
    tl.intent(F(7.0), head=-12, torso=-2)
    tl.face(F(7.0), 0.0, browtilt=0.016, mouth="pequena", look=(0.7, 0.7))
    tl.face(F(10.22), 1.0, wide=1.0, browup=0.03, mouth="o", look=(0.8, 0.9), extras=("suor",))
    tl.intent(F(10.25), head=-16, torso=-4)
    finish(H, tl, F(7.0), F(11.4))
    limpo.cortes(c, [
        (7.34, [(7.34, (1.2, -8.6, 2.6)), (8.96, (5.8, -9.4, 5.6))], dict(lens=35, dof=False)),                         # 9 PG a escada
        (10.22, [(10.22, (-0.3, -1.12, 1.4)), (11.18, (-0.28, -1.0, 1.42))], dict(lens=50, focus=1.1, fstop=0.8)),       # 11 PP
    ])


# ====================================================================== GANCHO: o número (8.96 - 10.22)
def numero(c):
    limpo.estudio("aco", cx=0.0, cz=1.0, raio=1.6, wall_y=1.0, poeira=25)
    I.odometro("odo", (0.0, 0.0, 1.0), F, 8.96, 9.85, 10.3, s=0.68)
    limpo.cortes(c, [(8.96, [(8.96, (0.0, -2.95, 1.0)), (10.22, (0.0, -2.8, 1.0))], dict(lens=35, focus=2.8, fstop=2.0))])


# ====================================================================== DINHEIRO: maços caindo na mesa (47.46 - 48.22)
def macos_caem(c):
    limpo.estudio("cofre", cx=0.0, cz=0.2, raio=0.7, table_z=0.0, wall_y=0.8, poeira=20)
    pilhas = [(-0.083, 5), (0.083, 4), (0.0, 0)]
    t = 47.42; i = 0
    ordem = [(x, r) for r in range(5) for (x, n) in pilhas[:2] if r < n]
    for (x, r) in ordem:
        topo = (r == 4) if x < 0 else (r == 3)
        m = D.malha(f"maco{i}", D.molde_maco(topo, True), [(0.0, 0.0)])
        m.location = (x, -0.004 * r, r * D.PASSO_Z)
        props.drop(m, F(t), r * D.PASSO_Z, r * D.PASSO_Z + 0.55, frames=4, bounce=0.05)
        props.blink_vis(m, [(F(45.0), False), (F(t) - 1, False), (F(t), True)], True)
        t += 0.075; i += 1
    cena.ground_disc("macos_sombra", 0.2, 0.06, cena.amat("macos_sombra_m", "#050302", 1.0, 0.6, ("radial", 1.2)), (0.0, 0.02, 0.0015))
    limpo.cortes(c, [(47.46, [(47.46, (0.0, -0.95, 0.24)), (48.22, (0.0, -0.88, 0.25))], dict(lens=50, focus=0.92, fstop=1.4))])


# ====================================================================== DINHEIRO: 52 bilhões (48.22 - 50.20)
def bilhoes(c):
    limpo.estudio("cofre", cx=0.0, cz=0.8, raio=3.5, table_z=0.0, wall_y=40.0, poeira=0)
    e = limpo.ESTUDIOS["cofre"]
    D.palete("pal_0", (0.0, 0.0, 0.0), cols=8, rows=13, detalhe=True)
    k = 0
    for row, y in enumerate((2.2, 4.6, 7.2, 10.0, 13.0, 16.5, 20.5, 25.0)):
        for col in range(-4, 5):
            if row == 0 and col == 0:
                continue
            x = col * 1.65 + (0.82 if row % 2 else 0.0)
            for nivel in range(1 if row == 0 else (2 if row < 3 else 3)):              # ao fundo, paletes empilhados
                D.palete(f"pal_{row}_{col}_{nivel}", (x, y + 0.01 * nivel, nivel * 1.18), cols=8, rows=13, detalhe=False); k += 1
        # ar entre as fileiras: cada uma um pouco mais escura que a da frente
        cena.poly_mesh(f"ar{row}", [(-40, y - 0.6, -1), (40, y - 0.6, -1), (40, y - 0.6, 30), (-40, y - 0.6, 30)], cena.amat(f"ar{row}_m", e["edge"], 1.0, 0.16))
        cena.ground_disc(f"poca{row}", 2.2, 1.0, cena.amat("poca_m", e["table_hi"], 1.0, 0.6, ("radial", 1.5)), (0.0, y - 0.3, 0.002))
    cone = cena.poly_mesh("luz0", [(-1, 0, 0), (1, 0, 0), (0.2, 0, 1), (-0.2, 0, 1)], cena.amat("luz0_m", e["light"], 1.0, 0.08, ("shaft", 1.4, 0.8)))
    cone.location = (0.0, 0.5, 0.0); cone.scale = (1.4, 1, 5.0)
    limpo.cortes(c, [(48.22, [(48.22, (0.0, -0.95, 0.62)), (48.7, (0.0, -1.6, 0.75)), (50.2, (0.0, -6.2, 1.55))],
                      dict(lens=50, focus=1.0, fstop=2.8, dof=False))])


# ====================================================================== DINHEIRO: em cinco anos (50.20 - 51.50)
def cinco_anos(c):
    limpo.estudio("cofre", cx=0.0, cz=1.1, raio=2.2, table_z=0.0, wall_y=1.5, poeira=25)
    alturas = [5, 10, 15, 20, 26]
    tempos = [50.22, 50.42, 50.62, 50.82, 51.02]
    prev = None
    for i, (n, t) in enumerate(zip(alturas, tempos)):
        p = D.parede(f"pilha{i}", 7, n, (0.0, -0.002 * i, 0.0), 1.0, True)
        props.blink_vis(p, [(F(49.0), False), (F(t), True)] + ([(F(tempos[i + 1]), False)] if i < 4 else []), True)
        S.grow_up(p, F(t), 5, 0.04) if i == 0 else None
        ano = props.txt(f"ano{i}", str(2020 + i), 0.16, "#ffd24a", (0.82, -0.05, n * D.PASSO_Z + 0.06), None, ink=props.INK, ow=0.06)
        props.blink_vis(ano, [(F(49.0), False), (F(t), True)] + ([(F(tempos[i + 1]), False)] if i < 4 else []), True)
        S.pop(ano, F(t), 1.0, 5, 0.2)
    limpo.cortes(c, [(50.2, [(50.2, (0.1, -3.0, 0.95)), (51.5, (0.1, -3.45, 1.62))], dict(lens=35, focus=3.0, fstop=2.0))])


# ====================================================================== DINHEIRO: a nota de cem (51.50 - 52.60)
def nota(c):
    limpo.estudio("cofre", cx=0.0, cz=1.0, raio=0.35, wall_y=0.6, poeira=20)
    notas = []
    for i, (dx, dz, rot, t) in enumerate(((0.0, 0.0, -5.0, 51.4), (-0.03, 0.025, 7.0, 52.28), (0.035, -0.02, -14.0, 52.36))):
        n = D.nota_grande(f"nota{i}", (dx, 0.01 * i, 1.0 + dz), 1.2)
        n.rotation_euler = (0, math.radians(rot), 0)
        if i:
            props.slide(n, F(t), F(t) + 4, (dx + (0.3 if i == 1 else -0.3), 0.01 * i, 1.0 + dz), (dx, 0.01 * i, 1.0 + dz))
            props.blink_vis(n, [(F(50.0), False), (F(t), True)], True)
        notas.append(n)
    r0 = notas[0]
    r0.rotation_euler = (0, math.radians(-7), 0); key(r0, "rotation_euler", F(51.5), "BEZIER")
    r0.rotation_euler = (0, math.radians(-3), 0); key(r0, "rotation_euler", F(52.6), "BEZIER")
    limpo.cortes(c, [(51.5, [(51.5, (0.0, -0.5, 0.975)), (52.6, (0.0, -0.46, 0.978))], dict(lens=50, focus=0.5, fstop=1.6))])


# ====================================================================== planos (intervalos a renderizar)
plano("h1", 0.0, 1.37, cela)
plano("h2", 1.37, 2.83, multidao)
plano("h3", 2.83, 6.41, cela)
plano("h4", 6.41, 7.34, celular)
plano("h5", 7.34, 8.96, escada)
plano("h6", 8.96, 10.22, numero)
plano("h7", 10.22, 11.18, escada)
plano("m1", 47.46, 48.22, macos_caem)
plano("m2", 48.22, 50.20, bilhoes)
plano("m3", 50.20, 51.50, cinco_anos)
plano("m4", 51.50, 52.60, nota)


def main():
    argv = sys.argv[sys.argv.index("--") + 1:]
    arg = lambda n, d=None: argv[argv.index(n) + 1] if n in argv else d
    if "--list" in argv:
        for k, (a, b, _) in PLANOS.items():
            print(f"{k:6s} {a:6.2f}-{b:6.2f}  quadros {F(a)}-{F(b) - 1}")
        return
    name, out = argv[0], argv[1]
    t0, t1, fn = PLANOS[name]
    k = float(arg("--scale", "1.0"))
    reset(int(1080 * k), int(1920 * k), FPS, int(arg("--samples", "16")))
    sc = lib.scene
    c = ctx(sc, t0, t1)
    sc.frame_start, sc.frame_end = c["f0"], c["f1"]
    fn(c)
    os.makedirs(out, exist_ok=True)
    if "--at" in argv or "--frames" in argv:
        fr = [F(float(x)) for x in arg("--at").split(",")] if "--at" in argv else [int(x) for x in arg("--frames").split(",")]
        for f in fr:
            sc.frame_set(f); sc.render.filepath = f"{out}/{name}_{f:04d}.png"; bpy.ops.render.render(write_still=True)
    else:
        sc.render.image_settings.file_format = "PNG"; sc.render.filepath = f"{out}/f_"
        bpy.ops.render.render(animation=True)


if __name__ == "__main__":
    main()