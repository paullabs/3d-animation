"""PCC v4, cenas dos níveis (a partir de 8,89 s): um cenário próprio por cena, cortes em movimento (transicao.py),
gestos com curvas contínuas (curvas.py) e dinheiro verde em volume (grana.py).
blender -b -P prod_pcc5.py -- CENA OUT [--scale 1] [--samples 16] [--at t1,t2] [--list]   (a1 e a2 vêm de prod_pcc4.py)"""
import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy, lib
from lib import *
import cena, props, luz, curvas, frente, uniforme as U, grana as G, area, armas, transicao as TR, sets4 as S, trono as T
import prod_pcc4 as P4
from prod_pcc4 import cena_, wt, camera_movel, baked_slide, seguro, escada5, cresce, surge, F, FPS, finish, Timeline, P, _mix
from acting import Actor
from char2d import rrect
from puppet2d import circle

VARIACOES = {
    "esquina":  dict(mid="#2c3290", low="#171b55", halo="#ffb04a", luz="#ffd9a0"),
    "avenida":  dict(mid="#20267a", low="#12164a", halo="#6f9bff", luz="#cfe0ff"),
    "fundos":   dict(mid="#1f6a74", low="#0f3a44", top="#06161c", chao="#07202a", halo="#ff9a4a", luz="#ffd09a", pedra="#2a8a94", aresta="#9be8e8"),
    "delegacia": dict(mid="#3a4aa8", low="#1b2370", halo="#8fb0ff", luz="#dfe8ff", pedra="#4a5ac0", aresta="#c8d2ff"),
    "salao":    dict(mid="#5a2c86", low="#2b1450", top="#0f0620", chao="#12082a", halo="#ffb070", luz="#ffd8b0", pedra="#6a3c9a", aresta="#e0b8ff"),
    "escritorio": dict(mid="#3a2a8a", low="#1d1458", halo="#ff8a3a", luz="#ffc488", pedra="#4a3aa0", aresta="#c0b4ff"),
    "casa":     dict(mid="#242a80", low="#111550", halo="#ffb04a", luz="#ffd9a0", pedra="#343a98", aresta="#9aa4ff"),
}


def pal(nome):
    return S.var(P, **VARIACOES[nome])


def camara(c, t0, t1, p0, p1, foco0, foco1, entra=None, sai=None, k=0.32, lens=30, fstop=2.2, curva="easy"):
    """câmera de uma cena: desliza de p0 a p1 com a curva, centrada na área segura; entra/sai = 'v' ou 'h' (corte em movimento)"""
    cam, rig = camera_movel(c, [(t0, p0, 0.0)], lens=lens, focus=foco0, fstop=fstop)
    seguro(cam)
    baked_slide(cam, F(t0), F(t1), p0, p1, curva)
    cd = cam.data
    for t_, d_ in ((t0, foco0), (t1, foco1)):
        cd.dof.focus_distance = d_; cd.dof.keyframe_insert("focus_distance", frame=F(t_))
    dirs = {"v": (0, 0, 1), "h": (1, 0, 0)}
    if entra:
        d_ent = k * (-p0[1])
        if entra == "v":                                   # a rampa de entrada vem de baixo: a câmera não pode entrar no chão
            d_ent = min(d_ent, max(0.3, p0[2] - 0.7))
        TR.rampa_inicio(cam, F(t0), dirs[entra], d_ent, 4)
    if sai:
        TR.rampa_fim(cam, F(t1), dirs[sai], k * (-p1[1]), 4)
    return cam


def heroi(p, view, x, A, END, y=0.0, k=1.32):
    """o herói com a roupa de presidiário, num invólucro em (x, y) com escala k (maior que o cenário: lê-se de longe).
    As posições do gesto (Timeline/Actor) são locais ao invólucro, a partir de 0."""
    H = U.heroi_preso("heroi", view, rim=p["borda"])
    w = empty("heroi_inv", None, (x, y, 0)); w.scale = (k, k, k); H.root.parent = w
    tl = Timeline(H, A, END, FPS); tl.stand(A, END, 0.0)
    return H, tl


def sombra_h(H, p):
    cena.contact_shadow(H, dict(shadow=_mix(p["chao"], "#000000", 0.4)))


# ====================================================================== B1. O ponto de venda (8,89 - 13,56)
@cena_("b1", 8.89, 13.56)
def b1(c):
    A, END = F(8.5), F(13.9); t0, t1 = 8.89, 13.56
    p = pal("esquina"); wy = 3.0
    S.fundo(p, wy, z_meio=2.2, x=(-14, 14), z=(-3, 12), escuro=0.1)
    S.cidade(p, wy - 0.2, -6, 8, 0.0, seed=3, lit=0.10, cor=_mix(p["top"], p["mid"], 0.2))
    cena.poly_mesh("calcada", [(-14, -30, 0.0), (14, -30, 0.0), (14, 1.2, 0.0), (-14, 1.2, 0.0)], props.FM(_mix(p["chao"], p["pedra"], 0.3)))
    S.poste(p, "poste", 1.75, 2.0, h=4.0, cor_luz=p["halo"], frames=END, poeira=20, seed=9)
    # estante do ponto: 4 prateleiras x 5 maços (20 maços = o que o ponto vende no turno); 3 deles são os 15%
    sx, esp, s_ = 0.85, 0.37, 2.2
    S.caixa3d(p, "fundo_est", sx, 0.62, 2.05, 2.0, d=0.02, cor=_mix(p["top"], p["mid"], 0.2), tampo=_mix(p["top"], p["mid"], 0.2), aresta=_mix(p["top"], p["mid"], 0.2))
    zs = [0.32, 0.78, 1.24, 1.70]
    for r, z in enumerate(zs):
        S.caixa3d(p, f"prat{r}", sx, 0.0, 2.05, z, d=0.62, base=z - 0.06, cor=_mix(p["top"], p["pedra"], 0.35), tampo=_mix(p["top"], p["pedra"], 0.55), aresta=p["aresta"])
    ped = (-0.38, -0.1, 0.55)
    S.caixa3d(p, "ped_b1", ped[0], ped[2] * 0 + ped[1], 0.5, ped[2], d=0.5)
    tp = 9.1; n = 0; escolhidos = []
    for r, z in enumerate(zs):
        for i in range(5):
            x = sx - 2 * esp + i * esp
            sel = (r == 3 and i < 3)                                              # 3 de 20 = 15%
            o = S.maco_pop(f"m{r}_{i}", (x, 0.3, z), s_, F(tp + 0.045 * n), A, desat=0.0 if sel else 0.6, zk=3.0)
            n += 1
            if sel:
                escolhidos.append((o, (x, 0.3, z)))
    t_q = wt(3, "quinze") - 0.1
    for j, (o, pos) in enumerate(escolhidos):                                    # em "quinze por cento", os 3 vão para o pedestal
        f0 = F(t_q + 0.16 * j)
        o.location = pos
        S.arco(o, f0, f0 + 10, pos, (ped[0], -0.1, ped[2] + 0.001 + j * 0.07), alt=0.5)
    # ele, de frente, ao lado do pedestal
    H, tl = heroi(p, "front", -1.05, A, END)
    tl.face(A, 0.0, lid="esperto", lidv=0.55, brow=-6, mouth="pequena", look=(0.9, 0.2))
    tl.face(F(wt(3, "começo")), 1.0, wide=0.3, brow=8, browup=0.012, mouth="pequena", look=(0.9, 0.3))
    tl.face(F(t_q), 1.0, lid="esperto", lidv=0.5, brow=-14, browtilt=0.02, mouth="sorriso", look=(0.8, -0.2))
    tl.face(F(wt(3, "turno")), 1.0, eye="cifrao", mouth="sorrisao", browup=0.015, extras=("brilho",))
    finish(H, tl, A, END)
    frente.bracos(H, A, END, [(A, dict(shF=5, elF=0, shB=5, elB=0)), (F(t_q) - 10, dict(shF=4, elF=2, shB=4, elB=2)), (F(t_q) - 2, dict(shF=-2, elF=4, shB=-1, elB=4)),
                              (F(t_q) + 12, dict(shF=38, elF=-80, wrF=-8, shB=34, elB=-76, wrB=-8)), (F(t_q) + 26, dict(shF=34, elF=-72, wrF=-6, shB=30, elB=-68, wrB=-6))])
    sombra_h(H, p)
    camara(c, t0, t1, (0.35, -5.8, 1.35), (0.55, -5.2, 1.3), 5.8, 5.2, entra="v", sai="h")


# ====================================================================== B2. A polícia chega (13,56 - 16,61)
@cena_("b2", 13.56, 16.61)
def b2(c):
    A, END = F(13.2), F(17.0); t0, t1 = 13.56, 16.61
    p = pal("avenida"); wy = 6.0
    S.fundo(p, wy, z_meio=2.4, x=(-18, 18), z=(-3, 12), escuro=0.15)
    S.cidade(p, wy - 0.3, -9, 10, 0.0, seed=7, lit=0.12, cor=_mix(p["top"], p["mid"], 0.25), hmax=6.5)
    cena.poly_mesh("asfalto", [(-18, -30, 0.0), (18, -30, 0.0), (18, 4.2, 0.0), (-18, 4.2, 0.0)], props.FM(_mix(p["chao"], p["mid"], 0.22)))
    for k in range(-8, 9):                                                         # faixa tracejada no chão
        cena.poly_mesh(f"faixa{k}", [(k * 1.8, 1.7, 0.003), (k * 1.8 + 0.9, 1.7, 0.003), (k * 1.8 + 0.9, 1.85, 0.003), (k * 1.8, 1.85, 0.003)], props.FM(_mix(p["aresta"], p["chao"], 0.35)))
    S.poste(p, "poste2", -1.9, 3.4, h=4.4, cor_luz=p["luz"], frames=END, poeira=10, seed=4)
    # a viatura entra da direita e freia (curva ease-out), com a sirene
    vt, vr, vb = S.viatura(p, "vtr", 4.2, 0.9, s=0.62, flip=-1)
    f_a, f_b = F(wt(4, "rua")), F(wt(4, "chega")) + 4
    for f in range(f_a, f_b + 1):
        u = (f - f_a) / (f_b - f_a); vt.location.x = 4.2 - 3.0 * curvas.s("easy", u) ** 0.8; key(vt, "location", f, "LINEAR")
    vt.location.x = 4.2; key(vt, "location", f_a - 1, "CONSTANT")
    S.pisca_sirene(vr, vb, f_a, END, per=8)
    S.luz_cor("lvm", "#ff3b4a", -0.6, -0.5, 1.4, 2.6, f_a, END, per=16, fase=0, alfa=0.22)
    S.luz_cor("lvb", "#3d7bff", -0.6, -0.5, 1.4, 2.6, f_a, END, per=16, fase=8, alfa=0.22)
    # ele de lado, parado na rua; se assusta e dá um passo para trás
    H, tl = heroi(p, "q", -0.85, A, END); a = Actor(tl, 0.0)
    tl.intent(A, head=-4, torso=0)
    tl.face(A, 0.0, lid="esperto", lidv=0.55, brow=-6, mouth="reta", look=(0.8, 0.1))
    tl.face(F(wt(4, "polícia")), 1.0, eye="ponto", brow=26, browup=0.025, mouth="o", extras=("!",), look=(0.9, 0.1))
    tl.face(F(wt(4, "chega")) + 6, 1.0, wide=0.6, brow=20, browup=0.02, mouth="nervosa", look=(0.9, 0.1), extras=("suor",))
    a.take(F(wt(4, "polícia")) + 2, back=-0.22)
    finish(H, tl, A, END)
    sombra_h(H, p)
    camara(c, t0, t1, (0.15, -5.6, 1.3), (0.5, -5.2, 1.25), 5.6, 5.2, entra="h", sai="v")


# ====================================================================== B3. O gerente (16,61 - 22,53)
@cena_("b3", 16.61, 22.53)
def b3(c):
    A, END = F(16.2), F(22.9); t0, t1 = 16.61, 22.53
    p = pal("fundos"); wy = 2.4
    S.fundo(p, wy, z_meio=2.0, x=(-10, 10), z=(-3, 10), escuro=0.0)
    for i in range(7):                                                             # persiana: faixas de luz na parede, à esquerda
        props.poly(f"slat{i}", cena.rect(-2.4, 1.1 + i * 0.36, -0.9, 1.1 + i * 0.36 + 0.16), _mix(p["luz"], p["mid"], 0.7), wy - 0.05, strength=0.9)
    props.poly("jan_moldura", cena.rect(-2.5, 1.0, -0.8, 3.7), p["grade"], wy - 0.03)
    for i in range(7):
        props.poly(f"jan_slat{i}", cena.rect(-2.4, 1.1 + i * 0.36, -0.9, 1.1 + i * 0.36 + 0.16), _mix(p["luz"], p["mid"], 0.6), wy - 0.06, strength=1.0)
    luz.feixe("feixe_mesa", 0.55, 0.9, 0.9, 5.2, 1.6, 0.25, p["luz"], forca=1.2, frames=END, poeira=40, seed=31)
    S.caixa3d(p, "mesa", 0.55, -0.3, 2.5, 0.9, d=0.85, cor=_mix(p["top"], p["pedra"], 0.3), tampo=_mix(p["top"], p["pedra"], 0.55))
    # pilha de 20 maços (R$ 200 mil) e, depois, o bloco de 70 maços (R$ 700 mil)
    pilha, _ = G.bloco("pilha20", (0.15, 0.0, 0.9), 1, 1, 20, s=3.0, zk=1.6)
    pilha.scale = (3.0, 3.0, 0.0001)
    t_p = wt(5, "5%")
    G.cresce_bloco(pilha, F(t_p - 0.9), F(t_p - 0.4))
    props.blink_vis(pilha, [(A, True), (F(wt(5, "ponto")) + 2, True), (F(wt(5, "ponto")) + 3, False)], True)
    topo = G.maco("topo20", (0.15, 0.0, 0.9 + 19 * G.T * 3.0 * 1.6), n=1, s=3.0, zk=1.6)           # a camada de cima = 5%
    props.blink_vis(topo, [(A, False), (F(t_p - 0.05), True), (F(t_p) + 22, False)], True)
    bloco, larg = G.bloco("bloco70", (0.7, 0.0, 0.9), 7, 2, 5, s=1.9, zk=4.0)
    G.cresce_bloco(bloco, F(wt(5, "faturar")), F(wt(5, "faturar")) + 12)
    props.blink_vis(bloco, [(A, False), (F(wt(5, "faturar")) - 1, False), (F(wt(5, "faturar")), True)], True)
    # ele, atrás da mesa
    H, tl = heroi(p, "front", -0.35, A, END, y=0.25)
    tl.face(A, 0.0, lid="esperto", lidv=0.55, brow=-8, mouth="reta", look=(0.8, 0.0))
    tl.face(F(wt(5, "gerente")), 1.0, lid="esperto", lidv=0.5, brow=-12, browtilt=0.018, mouth="sorriso", look=(0.8, -0.1))
    tl.face(F(t_p), 1.0, wide=0.2, brow=6, mouth="lado", look=(0.9, -0.2))
    tl.face(F(wt(5, "faturar")), 1.0, eye="cifrao", mouth="sorrisao", browup=0.015, extras=("brilho",))
    finish(H, tl, A, END)
    frente.bracos(H, A, END, [(A, dict(shF=5, elF=0, shB=5, elB=0)), (F(t_p) - 8, dict(shF=5, elF=-4, shB=5, elB=-4)),
                              (F(t_p) + 10, dict(shF=40, elF=-85, wrF=-8, shB=10, elB=-20)), (F(t_p) + 40, dict(shF=14, elF=-30, wrF=0, shB=8, elB=-14))])
    sombra_h(H, p)
    camara(c, t0, t1, (0.35, -5.4, 1.4), (0.55, -4.7, 1.45), 5.4, 4.7, entra="v", sai="h")


# ====================================================================== B4. O policial cobra (22,53 - 28,62)
@cena_("b4", 22.53, 28.62)
def b4(c):
    A, END = F(22.1), F(29.0); t0, t1 = 22.53, 28.62
    p = pal("delegacia"); wy = 3.2
    S.fundo(p, wy, z_meio=2.2, x=(-12, 12), z=(-3, 10), escuro=0.05)
    # fachada da delegacia: porta, lâmpada e o escudo na parede
    props.poly("porta", rrect(-0.4, 0.0, 0.4, 2.1, 0.04, 3), _mix(p["top"], "#000000", 0.2), wy - 0.05)
    props.poly("porta_v", cena.rect(-0.3, 1.0, 0.3, 1.9), _mix(p["mid"], p["luz"], 0.3), wy - 0.06, strength=1.1)
    cena.disc("lamp_porta", 0.5, cena.amat("lamp_porta_m", p["luz"], 1.0, 0.5, ("radial", 1.4)), (0.0, wy - 0.1, 2.5))
    escudo = empty("escudo", None, (-1.5, wy - 0.06, 2.3))
    props.inked("escudo_p", [(-0.4, 0.4), (0.4, 0.4), (0.4, -0.1), (0.0, -0.45), (-0.4, -0.1)], p["aresta"], escudo, w=0.0, rim=0.02, rim_color="#ffffff")
    props.poly("escudo_e", props.star5(0.2, 0.46) if hasattr(props, "star5") else circle(0, 0.1, 0.15, 5), p["top"], -0.002, escudo)
    S.caixa3d(p, "degrau", 0.0, 2.2, 3.0, 0.2, d=0.8)
    # o PM à direita e o envelope que passa de mão em mão
    pmx = 0.95
    S.pm(p, "pm", pmx, 0.0, h=1.0, flip=-1)
    H, tl = heroi(p, "q", -0.75, A, END); a = Actor(tl, 0.0)
    tl.intent(A, head=3, torso=1)
    tl.face(A, 0.0, lid="esperto", lidv=0.5, brow=-4, mouth="pequena", look=(0.9, 0.1))
    tl.face(F(wt(6, "cobra")), 1.0, lid="triste", lidv=0.3, brow=14, mouth="nervosa", look=(0.9, 0.0), extras=("suor",))
    tl.face(F(wt(6, "viu")), 1.0, lid="esperto", lidv=0.5, brow=-8, mouth="lado", look=(0.5, 0.1))
    finish(H, tl, A, END)
    sombra_h(H, p)
    env = empty("env", None, (-0.45, -0.05, 1.05))
    props.inked("env_f", rrect(-0.1, -0.065, 0.1, 0.065, 0.01, 2), "#f4efe6", env, w=0.0, rim=0.006, rim_color="#ffffff")
    props.poly("env_v", [(-0.1, 0.065), (0.0, 0.0), (0.1, 0.065)], "#cfc8bb", -0.002, env)
    props.poly("env_g", cena.rect(0.05, -0.065, 0.1, -0.02), "#4c9a62", -0.003, env, strength=1.1)
    fa, fb = F(wt(6, "cobra")) + 4, F(wt(6, "fingir"))
    env.scale = (0.0001,) * 3; key(env, "scale", fa - 1, "CONSTANT")
    env.scale = (1, 1, 1); key(env, "scale", fa, "CONSTANT")
    S.arco(env, fa, fb, (-0.45, -0.05, 1.05), (pmx - 0.35, -0.05, 1.05), alt=0.12)
    env.scale = (1, 1, 1); key(env, "scale", fb + 2, "CONSTANT")
    env.scale = (0.0001,) * 3; key(env, "scale", fb + 3, "CONSTANT")
    # em "42": o painel de fichas (14 x 3) sobe pela parede; em "condenados", as grades descem por cima
    ficha_esp, ficha_z0 = 0.235, 3.2
    fichas = []
    for r in range(3):
        for i in range(14):
            k = r * 14 + i
            x = -1.5 + i * ficha_esp - 0.2; z = ficha_z0 + r * 0.38
            f_ = empty(f"fi{k}", None, (x, wy - 0.08, z)); f_.scale = (0.0001,) * 3
            props.poly(f"fi{k}_c", rrect(-0.1, -0.15, 0.1, 0.15, 0.015, 3), _mix(p["top"], p["aresta"], 0.25), 0.0, f_)
            props.poly(f"fi{k}_h", circle(0, 0.055, 0.045, 10), "#0d1020", -0.002, f_)
            props.poly(f"fi{k}_b", rrect(-0.075, -0.13, 0.075, 0.0, 0.03, 3), "#1a2060", -0.002, f_)
            props.poly(f"fi{k}_bo", cena.rect(-0.05, 0.085, 0.05, 0.105), "#0a0f3a", -0.003, f_)
            t = wt(6, "42") + 0.025 * k
            surge(f_, F(t), 4, de=0.6)
            fichas.append(f_)
    gr = props.grade("grade_fichas", -1.75, 1.75, 0.0, 1.35, wy - 0.15, p["grade"], n=16, w=0.04, rails=0)
    for z in (0.0, 1.25):
        props.poly(f"gf_t{z}", cena.rect(-1.75, z, 1.75, z + 0.1), p["grade"], -0.001, gr)
    gr.location = (-0.2, wy - 0.15, 3.1)
    gr.location.z = 3.1 + 2.6; key(gr, "location", F(wt(6, "condenados")) - 1, "CONSTANT")
    for f in range(F(wt(6, "condenados")), F(wt(6, "condenados")) + 8):
        u = (f - F(wt(6, "condenados"))) / 7; gr.location.z = 3.1 + 2.6 * (1 - curvas.s("queda", u)); key(gr, "location", f, "LINEAR")
    camara(c, t0, t1, (0.1, -5.0, 1.2), (0.0, -6.3, 2.5), 5.0, 6.3, entra="h", sai="v")


# ====================================================================== B5. O membro paga (28,62 - 33,68)
@cena_("b5", 28.62, 33.68)
def b5(c):
    A, END = F(28.2), F(34.0); t0, t1 = 28.62, 33.68
    p = pal("salao"); wy = 2.8
    S.fundo(p, wy, z_meio=2.2, x=(-10, 10), z=(-3, 10))
    emb = empty("embl", None, (0.9, wy - 0.05, 2.4))                               # emblema de anéis: sem letras
    for k, (r, cor) in enumerate(((1.0, _mix(p["mid"], p["halo"], 0.2)), (0.78, _mix(p["mid"], p["top"], 0.4)), (0.56, _mix(p["mid"], p["halo"], 0.35)), (0.3, _mix(p["mid"], p["top"], 0.5)))):
        props.poly(f"embl{k}", circle(0, 0, r, 40), cor, -0.001 * k, emb)
    cena.disc("halo_embl", 2.4, cena.amat("halo_embl_m", p["halo"], 1.0, 0.35, ("radial", 1.5)), (0.9, wy - 0.1, 2.4))
    luz.feixe("feixe_caixa", 0.9, 0.8, 0.0, 4.4, 1.4, 0.3, p["luz"], forca=1.2, frames=END, poeira=30, seed=12)
    # a caixa de arrecadação: bloco com fenda e uma luz acima
    S.caixa3d(p, "caixa", 0.9, 0.0, 0.85, 1.05, d=0.7, cor=_mix(p["top"], p["pedra"], 0.4), tampo=_mix(p["top"], p["pedra"], 0.65))
    props.poly("fenda", rrect(-0.28, 0.0, 0.28, 0.07, 0.02, 3), "#05030f", -0.001, empty("fenda_r", None, (0.9, -0.002, 0.82)))
    props.poly("fenda2", rrect(-0.3, -0.01, 0.3, 0.09, 0.02, 3), p["halo"], 0.0, empty("fenda_r2", None, (0.9, -0.0015, 0.81)))
    # ele de lado, com as notas na mão; elas entram na fenda uma a uma (arco + encolhe)
    H, tl = heroi(p, "q", -0.5, A, END); a = Actor(tl, 0.0)
    tl.intent(A, head=-2, torso=0)
    tl.face(A, 0.0, lid="esperto", lidv=0.55, brow=-6, mouth="sorriso", look=(0.9, 0.1))
    tl.face(F(wt(7, "agora")), 1.0, wide=0.2, brow=6, mouth="pequena", look=(0.9, -0.1))
    tl.face(F(wt(7, "paga")), 1.0, lid="triste", lidv=0.35, brow=14, mouth="nervosa", look=(0.9, -0.3))
    tl.face(F(32.0), 1.0, lid="sono", lidv=0.7, brow=18, mouth="triste", extras=("sombra",), look=(0.6, -0.5))
    tl.intent(F(wt(7, "paga")) - 6, shF=10, elF=60); tl.intent(F(wt(7, "paga")), shF=55, elF=40, wrF=10)
    tl.intent(F(32.2), shF=10, elF=70)
    finish(H, tl, A, END)
    sombra_h(H, p)
    for i in range(5):
        n = G.nota(f"nota_pg{i}", (0.0, 0.0, 0.0), 2.4)
        tf = wt(7, "paga") + 0.1 + 0.42 * i
        f0 = F(tf)
        p0 = (-0.1, -0.2, 1.1); p1 = (0.9, -0.1, 0.9)
        n.scale = (0.0001,) * 3; key(n, "scale", f0 - 1, "CONSTANT")
        n.scale = (2.4 / 1.0 * 1.0,) * 3
        n.scale = (1, 1, 1); key(n, "scale", f0, "CONSTANT")
        S.arco(n, f0, f0 + 9, p0, (0.9, -0.1, 0.92), alt=0.35)
        for f in range(f0 + 9, f0 + 14):                                         # afunda na fenda: encolhe em z
            u = (f - (f0 + 9)) / 4; n.scale = (1, 1, max(0.0001, 1 - u)); key(n, "scale", f, "LINEAR")
        n.scale = (0.0001,) * 3; key(n, "scale", f0 + 15, "CONSTANT")
    camara(c, t0, t1, (0.45, -5.0, 1.3), (0.4, -4.6, 1.35), 5.0, 4.6, entra="v", sai="h")


# ====================================================================== B6. O tribunal do crime (33,68 - 38,45)
@cena_("b6", 33.68, 38.45)
def b6(c):
    global P
    A, END = F(33.3), F(38.8); t0, t1 = 33.68, 38.45
    p = S.var(P, **T.PALETAS["vinho"]); wy = 3.4
    S.fundo(p, wy, z_meio=2.4, x=(-10, 10), z=(-3, 10), escuro=0.0)
    luz.feixe("feixe_trib", 0.0, 0.2, 0.0, 6.0, 1.7, 0.35, p["luz"], forca=1.4, frames=END, poeira=50, seed=44)
    cena.disc("halo_trib", 3.0, cena.amat("halo_trib_m", p["halo"], 1.0, 0.38, ("radial", 1.5)), (0.0, wy - 0.1, 1.6))
    for i, x in enumerate((-0.7, 0.0, 0.7)):                                      # três juízes atrás da mesa
        S.pm(p, f"juiz{i}", x, 0.9, h=1.05, flip=1, cor=_mix(p["mid"], "#000000", 0.55), rim=p["borda"])
    S.caixa3d(p, "mesa_t", 0.0, 0.55, 2.7, 0.95, d=0.6, cor=_mix(p["top"], p["mid"], 0.5), tampo=_mix(p["top"], p["aresta"], 0.3))
    pv, bloco = props.martelo("martelo", (0.95, 0.4, 1.04), 0.9)
    tt = F(wt(8, "tribunal"))
    ang = lambda d: math.radians(d)
    for ff, a_ in ((A, -50), (tt - 8, -64), (tt - 2, -64), (tt, 0), (tt + 3, -9), (tt + 6, 0), (tt + 40, 0)):
        pv.rotation_euler = (0, ang(a_), 0); key(pv, "rotation_euler", ff, "BEZIER" if ff != tt else "LINEAR")
    # as três penas, em faixas que descem do teto: cada uma mais longa (e mais vermelha) que a anterior
    cor_f = ["#c8343c", "#e0484f", "#ff5a5a"]
    comps = [0.7, 1.25, 1.85]
    for i, (x, cp, nome) in enumerate(zip((-1.3, 0.0, 1.3), comps, ("surra", "braço", "morte"))):
        ban = empty(f"ban{i}", None, (x, wy - 0.12, 4.4))
        props.poly(f"ban{i}_f", [(-0.28, 0.0), (0.28, 0.0), (0.28, -cp), (0.0, -cp - 0.12), (-0.28, -cp)], cor_f[i], 0.0, ban, strength=1.05)
        props.poly(f"ban{i}_s", cena.rect(-0.28, -cp * 0.35, -0.2, 0.0), _mix(cor_f[i], "#000000", 0.3), -0.001, ban)
        ic = empty(f"ban{i}_ic", ban, (0, -0.002, -cp + 0.15))
        if i == 0:
            props.poly(f"ban{i}_ic1", circle(0, 0, 0.1, 12), "#ffffff", 0.0, ic)
            props.poly(f"ban{i}_ic2", circle(0, 0, 0.05, 10), cor_f[i], -0.001, ic)
        elif i == 1:
            props.poly(f"ban{i}_ic1", [(-0.07, 0.12), (0.03, 0.12), (-0.01, 0.01), (0.08, 0.01), (-0.06, -0.14), (-0.02, -0.02), (-0.1, -0.02)], "#ffffff", 0.0, ic)
        else:
            cv = props.caveira(f"ban{i}_cv", (0, -0.003, 0.0), 0.2); cv.parent = ic
        ts = wt(8, nome)
        for f in range(F(ts) - 1, F(ts) + 10):                                    # desce do teto e assenta (curva queda)
            u = (f - F(ts)) / 9; ban.location.z = 4.4 - (4.4 - 3.9) * 0 - (cp * 0.0) - 0.0
            ban.location.z = 5.5 + (3.75 - 5.5) * curvas.s("queda", max(0.0, min(1.0, u))); key(ban, "location", f, "LINEAR")
    # ele, pequeno, no cone de luz, cabeça baixa
    H, tl = heroi(p, "front", 0.0, A, END, y=-0.9)
    tl.face(A, 0.0, lid="triste", lidv=0.3, brow=12, mouth="nervosa", look=(0.0, -0.4), extras=("suor",))
    tl.face(F(wt(8, "surra")), 1.0, wide=0.4, brow=20, browup=0.02, mouth="grito", look=(0.0, 0.0), extras=("suor", "!"))
    tl.intent(A, head=14, torso=5)
    finish(H, tl, A, END)
    frente.bracos(H, A, END, [(A, dict(shF=4, elF=-10, shB=4, elB=-10)), (F(wt(8, "tribunal")) - 4, dict(shF=3, elF=-14, shB=3, elB=-14)), (F(wt(8, "tribunal")) + 8, dict(shF=18, elF=-50, wrF=-6, shB=18, elB=-50, wrB=-6))],
                  extras=[(tt, "shF", -6, 2.8, 0.3), (tt, "shB", -6, 2.8, 0.3)])
    sombra_h(H, p)
    camara(c, t0, t1, (0.0, -5.2, 1.5), (0.0, -6.0, 1.9), 5.2, 6.0, entra="h", sai="v")


# ====================================================================== B7. O chefe de setor (38,45 - 42,33)
@cena_("b7", 38.45, 42.33)
def b7(c):
    A, END = F(38.0), F(42.7); t0, t1 = 38.45, 42.33
    p = pal("escritorio"); wy = 3.0
    S.fundo(p, wy, z_meio=2.2, x=(-10, 10), z=(-3, 10))
    props.poly("jan_m", cena.rect(-1.75, 0.95, 1.75, 3.65), p["grade"], wy - 0.02)
    props.poly("jan_c", cena.rect(-1.65, 1.05, 1.65, 3.55), _mix(p["halo"], p["mid"], 0.45), wy - 0.04, strength=1.1)
    props.poly("jan_c2", cena.rect(-1.65, 1.05, 1.65, 1.9), _mix(p["halo"], p["mid"], 0.2), wy - 0.045, strength=1.1)
    S.cidade(p, wy - 0.1, -1.6, 1.6, 1.05, seed=14, lit=0.22, cor=_mix(p["top"], p["mid"], 0.1), luzc=p["luz"], hmax=2.0)
    for x in (-0.55, 0.55):
        props.poly(f"jan_div{x}", cena.rect(x - 0.03, 0.95, x + 0.03, 3.65), p["grade"], wy - 0.12)
    luz.feixe("feixe_esc", 0.2, 0.6, 0.0, 5.0, 1.8, 0.35, p["luz"], forca=1.0, frames=END, poeira=30, seed=51)
    S.caixa3d(p, "mesa_e", 0.15, -0.35, 3.2, 0.9, d=0.9, cor=_mix(p["top"], p["pedra"], 0.35), tampo=_mix(p["top"], p["pedra"], 0.6))
    # esteira: os maços passam da esquerda para a direita, na altura da mão dele (movimento constante, como correia)
    n = 11; passo = 0.5; vel = 0.62
    for i in range(n):
        m = G.maco(f"cm{i}", (0, -0.15, 0.9), n=1, s=1.7, zk=3.0)
        x_i = lambda t: -2.6 + i * passo + vel * (t - A / 24.0)
        for f in range(A, END + 1, 2):
            x = -2.6 + i * passo + vel * ((f - A) / 24.0)
            m.location = (x if x < 3.6 else 3.6, -0.15, 0.9); key(m, "location", f, "LINEAR")
    # ele atrás da mesa, no centro, com a mão acompanhando o dinheiro
    H, tl = heroi(p, "front", 0.15, A, END, y=0.3)
    tl.face(A, 0.0, lid="esperto", lidv=0.5, brow=-10, mouth="reta", look=(0.8, -0.2))
    tl.face(F(wt(9, "setor")), 1.0, lid="esperto", lidv=0.5, brow=-14, browtilt=0.02, mouth="sorriso", look=(0.9, -0.3))
    tl.face(F(wt(9, "dinheiro")), 1.0, eye="cifrao", mouth="sorrisao", browup=0.015, extras=("brilho",))
    finish(H, tl, A, END)
    frente.bracos(H, A, END, [(A, dict(shF=5, elF=0, shB=5, elB=0)), (F(wt(9, "muito")), dict(shF=24, elF=-64, wrF=-6, shB=4, elB=-4)),
                              (F(wt(9, "passa")), dict(shF=32, elF=-80, wrF=-10, shB=4, elB=-4)), (F(wt(9, "mão")), dict(shF=26, elF=-70, wrF=-8, shB=10, elB=-20))])
    sombra_h(H, p)
    camara(c, t0, t1, (0.25, -5.0, 1.45), (0.15, -4.3, 1.5), 5.0, 4.3, entra="v", sai="h")


# ====================================================================== B8. O tesoureiro e a inveja (42,33 - 48,43)
@cena_("b8", 42.33, 48.43)
def b8(c):
    A, END = F(41.9), F(48.8); t0, t1 = 42.33, 48.43
    p = pal("casa"); wy = 3.4
    S.fundo(p, wy, z_meio=2.2, x=(-12, 12), z=(-3, 10), escuro=0.12)
    S.cidade(p, wy + 0.5, -8, 9, 0.0, seed=21, lit=0.05, cor=_mix(p["top"], p["mid"], 0.1), hmax=3.0)
    cena.poly_mesh("calcada8", [(-14, -30, 0.0), (14, -30, 0.0), (14, 1.0, 0.0), (-14, 1.0, 0.0)], props.FM(_mix(p["chao"], p["pedra"], 0.25)))
    def casa(nome, x, w, h, cor, yy, luzes):
        props.poly(nome + "_p", cena.rect(x - w / 2, 0.0, x + w / 2, h), cor, yy)
        props.poly(nome + "_t", [(x - w / 2 - 0.15, h), (x + w / 2 + 0.15, h), (x, h + 0.9)], _mix(cor, "#000000", 0.35), yy - 0.01)
        return
    casa("cE", -2.0, 1.9, 2.5, _mix(p["pedra"], p["top"], 0.4), 1.7, None)
    casa("cD", 1.7, 1.9, 2.5, _mix(p["pedra"], p["top"], 0.4), 1.7, None)
    casa("cC", -0.15, 1.7, 2.8, _mix(p["pedra"], p["mid"], 0.1), 1.3, None)         # a casa dele, no centro
    props.poly("porta8", rrect(0.15, 0.0, 0.75, 1.9, 0.03, 3), _mix(p["top"], "#000000", 0.2), 1.25)
    for x in (-0.65, -0.55):
        pass
    props.poly("jan_c8", cena.rect(-0.85, 1.1, -0.25, 1.9), _mix(p["halo"], p["mid"], 0.2), 1.25, strength=1.1)
    cena.disc("lamp_casa", 0.9, cena.amat("lamp_casa_m", p["halo"], 1.0, 0.55, ("radial", 1.4)), (0.45, 1.2, 2.05))
    props.poly("lamp_casa_p", circle(0.45, 2.05, 0.06, 10), p["luz"], 1.24, strength=1.6)
    # vizinhos olhando: pares de olhos amarelos acendem nas janelas escuras, um a um, em "inveja"
    pos = [(-2.4, 1.6), (-1.7, 1.5), (1.4, 1.55), (2.1, 1.6), (-2.0, 0.7), (1.8, 0.8)]
    for i, (x, z) in enumerate(pos):
        props.poly(f"vj{i}", cena.rect(x - 0.22, z - 0.22, x + 0.22, z + 0.25), "#04051a", 1.65)
        ol = S.olhos(f"ol{i}", x, z, 1.64, s=1.0)
        ti = wt(10, "inveja") + 0.18 * i
        props.blink_vis(ol, [(A, False), (F(ti) - 1, False), (F(ti), True), (F(ti) + 6, False), (F(ti) + 8, True), (F(wt(10, "fuzilado")) + 2, False)], True)
    # o tesoureiro caminha até a porta com a pasta; a mira o encontra em "fuzilado"
    ts = props.pessoa("tes", -1.3, 0.0, "#1a2060", 1.0, flip=-1, rim=p["borda"])
    pasta = props.inked("pasta", rrect(0.0, -0.08, 0.16, 0.0, 0.01, 2), "#7a4a2a", ts, loc=(0.24, -0.003, 0.74), w=0.0, rim=0.006, rim_color="#ffc88a")
    f_ini, f_fim = F(wt(10, "tesoureiro")), F(wt(10, "fuzilado"))
    for f in range(f_ini, f_fim + 1):
        u = (f - f_ini) / (f_fim - f_ini); ts.location.x = -1.3 + 1.6 * curvas.s("easy", u); ts.location.z = 0.025 * abs(math.sin((f - f_ini) * 0.55)); key(ts, "location", f, "LINEAR")
    mr = S.mira("mira", (1.2, -0.3, 3.0), 1.0)
    f_m = F(wt(10, "fuzilado"))
    for f in range(f_m - 8, f_m + 1):
        u = (f - (f_m - 8)) / 8; s_ = curvas.s("queda", u)
        mr.location = (1.2 + (0.3 - 1.2) * s_, -0.3, 3.0 + (1.15 - 3.0) * s_); key(mr, "location", f, "LINEAR")
        v = 1.7 - 0.7 * s_; mr.scale = (v, v, v); key(mr, "scale", f, "LINEAR")
    mr.scale = (0.0001,) * 3; key(mr, "scale", f_m - 9, "CONSTANT")
    mr.scale = (0.0001,) * 3; key(mr, "scale", f_m + 3, "CONSTANT")
    fl = cena.disc("flash8", 0.6, cena.amat("flash8_m", "#ffffff", 3.0, 0.9, ("radial", 1.1)), (0.3, -0.35, 1.1))
    props.blink_vis(fl, [(A, False), (f_m, True), (f_m + 3, False)], True)
    props.blink_vis(ts, [(A, True), (f_m + 1, True), (f_m + 2, False)], True)
    pq = props.inked("pasta_c", rrect(-0.08, 0.0, 0.08, 0.1, 0.01, 2), "#7a4a2a", None, loc=(0.35, -0.15, 0.0), w=0.0, rim=0.006, rim_color="#ffc88a")
    props.blink_vis(pq, [(A, False), (f_m + 2, False), (f_m + 3, True)], True)
    pq.location = (0.35, -0.15, 0.55); key(pq, "location", f_m + 2, "CONSTANT")
    for f in range(f_m + 3, f_m + 10):
        u = (f - f_m - 3) / 6; pq.location.z = 0.55 * (1 - u * u); key(pq, "location", f, "LINEAR")
    camara(c, t0, t1, (-0.45, -5.6, 1.35), (-0.2, -5.0, 1.3), 5.6, 5.0, entra="h", sai="v")


# ====================================================================== B9. O topo (48,43 - 53,21)
@cena_("b9", 48.43, 53.21)
def b9(c):
    A, END = F(48.0), F(53.6); t0, t1 = 48.43, 53.21
    p = S.var(P, top="#1a1250", mid="#d85a7a", low="#ff9650", chao="#2a1850", halo="#ffb050", luz="#ffe0b0", pedra="#3a2a78", aresta="#ffd0a0", borda="#ffd6a0", grade="#0d0830")
    wy = 6.0
    bpy.context.scene.world.node_tree.nodes["Background"].inputs[0].default_value = (*srgb(p["top"]), 1)
    props.skywall("ceu9", wy, [(-3, "#ff9650"), (1.2, "#ff7a5a"), (3.5, "#d85a7a"), (7, "#7a3a9a"), (12, "#241470")], -20, 20, -3, 12)
    cena.poly_mesh("chao9", [(-20, -30, -0.004), (20, -30, -0.004), (20, wy, -0.004), (-20, wy, -0.004)], props.FM(p["chao"]))
    cena.disc("sol9", 1.6, cena.amat("sol9_m", "#fff0c0", 2.0, 1.0, ("radial", 1.1)), (1.4, wy - 0.1, 1.9))
    cena.disc("halo9", 5.0, cena.amat("halo9_m", "#ffd090", 1.0, 0.5, ("radial", 1.6)), (1.4, wy - 0.15, 1.9))
    S.cidade(p, wy - 0.3, -9, 10, 0.0, seed=33, lit=0.08, cor="#2a1468", luzc="#ffd090", hmax=3.4)
    props.poly("mureta9", cena.rect(-6, 0.0, 6, 0.95), "#1a0f50", 1.5)
    props.poly("mureta9a", cena.rect(-6, 0.9, 6, 0.95), p["aresta"], 1.49)
    S.caixa3d(p, "mesa9", 0.2, 0.0, 1.8, 0.8, d=0.8, cor="#1e1458", tampo="#3a2a88")
    # 10 maços sobre a mesa: 8 (80%) vão para os poucos da direita; 2 ficam
    pos0 = [(-0.4 + 0.4 * (i % 5) - 0.4, 0.35, 0.8 + 0.0) for i in range(10)]
    ms = []
    for i in range(10):
        r, col = divmod(i, 5)
        m = G.maco(f"m9_{i}", (-0.55 + 0.4 * col, 0.25, 0.8 + r * 0.16), n=1, s=2.3, zk=3.0)
        ms.append(m)
    pessoas = []
    for j, x in enumerate((1.25, 1.75, 2.25)):
        pes = props.pessoa(f"poucos{j}", x, 0.0, "#2a1a80", 1.0, flip=-1, rim=p["borda"])
        pessoas.append(pes)
    t_d = wt(11, "divide")
    for i in range(10):
        if i in (0, 1):
            continue
        f0 = F(wt(11, "oitenta") + 0.05 * (i - 2)); dest = (0.95 + 0.09 * (i % 4), -0.15, 0.04 + 0.05 * (i // 4))
        S.arco(ms[i], f0, f0 + 12, ms[i].location.copy()[:], dest, alt=0.5)
    H, tl = heroi(p, "front", -1.1, A, END)
    tl.face(A, 0.0, lid="esperto", lidv=0.55, brow=-8, mouth="sorriso", look=(0.9, 0.1))
    tl.face(F(wt(11, "poucos")), 1.0, lid="esperto", lidv=0.5, brow=-12, browtilt=0.02, mouth="lado", look=(1.0, 0.0))
    tl.face(F(wt(11, "dinheiro")), 1.0, wide=0.3, brow=4, mouth="pequena", look=(1.0, -0.1))
    finish(H, tl, A, END)
    frente.bracos(H, A, END, [(A, dict(shF=5, elF=0, shB=5, elB=0)), (F(wt(11, "topo")), dict(shF=5, elF=-2, shB=5, elB=-2)),
                              (F(wt(11, "divide")), dict(shF=12, elF=-30, shB=40, elB=-70, wrB=-10)), (F(wt(11, "oitenta")), dict(shF=12, elF=-30, shB=42, elB=-76, wrB=-10))])
    sombra_h(H, p)
    camara(c, t0, t1, (0.1, -5.6, 1.4), (0.7, -5.0, 1.35), 5.6, 5.0, entra="v", sai="h")


# ====================================================================== B10. A traição (53,21 - 59,65)
@cena_("b10", 53.21, 59.65)
def b10(c):
    A, END = F(52.8), F(60.0); t0, t1 = 53.21, 59.65
    p = S.var(P, **T.PALETAS["vinho"]); wy = 3.2
    S.fundo(p, wy, z_meio=2.4, x=(-10, 10), z=(-3, 10))
    for x in (-2.2, 2.2):
        props.poly(f"col10{x}", cena.rect(x - 0.35, 0, x + 0.35, 6), _mix(p["coluna"], p["top"], 0.2), wy - 0.1)
        props.poly(f"col10l{x}", cena.rect(x + (-0.35 if x > 0 else 0.28), 0, x + (-0.28 if x > 0 else 0.35), 6), p["coluna_luz"], wy - 0.11)
    cena.disc("halo10", 3.4, cena.amat("halo10_m", p["halo"], 1.0, 0.4, ("radial", 1.5)), (0.0, wy - 0.1, 2.0))
    luz.feixe("feixe10", 0.0, 0.3, 0.0, 6.0, 1.9, 0.4, p["luz"], forca=1.2, frames=END, poeira=45, seed=61)
    xs = [-1.5, -0.8, 0.0, 0.8, 1.5]
    cores = ["#3a1840", "#46203e", "#52262c", "#46203e", "#3a1840"]
    figs = []
    for i, (x, cor) in enumerate(zip(xs, cores)):
        h = 1.12 if i == 2 else 1.0
        fg = S.pm(p, f"chefe10_{i}", x, 0.9, h=h, flip=1 if x < 0 else -1, cor=cor, rim=p["borda"]); figs.append(fg)
    S.caixa3d(p, "mesa10", 0.0, 0.45, 3.9, 0.95, d=0.8, cor=_mix(p["top"], p["mid"], 0.55), tampo=_mix(p["top"], p["aresta"], 0.25))
    cr = S.coroa("coroa10", (0.0, 0.88, 2.04), 1.0)                                  # em cima do líder (centro)
    # traição: os dois mais próximos do líder se inclinam para ele
    t_tr = wt(12, "traição")
    for i, d in ((1, -1), (3, 1)):
        o = figs[i]; rz0 = o.rotation_euler.copy(); base = o.location.x
        for f in range(F(t_tr) - 1, F(t_tr) + 18):
            u = min(1.0, max(0.0, (f - F(t_tr)) / 14)); s_ = curvas.s("easy", u)
            o.rotation_euler = (0, math.radians(7 * d * s_), 0); key(o, "rotation_euler", f, "LINEAR")
            o.location.x = base + 0.05 * d * s_; key(o, "location", f, "LINEAR")
    # "mandaram matar": mira no líder; a coroa recebe um X e cai; o líder encolhe
    t_mt = wt(12, "matar"); f_m = F(t_mt)
    mr = S.mira("mira10", (0.0, -0.25, 3.0), 1.0)
    for f in range(f_m - 10, f_m + 1):
        u = (f - (f_m - 10)) / 10; s_ = curvas.s("queda", u)
        mr.location = (0.0, -0.25, 3.0 + (1.65 - 3.0) * s_); key(mr, "location", f, "LINEAR")
        v = 1.8 - 0.8 * s_; mr.scale = (v, v, v); key(mr, "scale", f, "LINEAR")
    mr.scale = (0.0001,) * 3; key(mr, "scale", f_m - 11, "CONSTANT")
    mr.scale = (0.0001,) * 3; key(mr, "scale", F(wt(12, "líder")) + 2, "CONSTANT")
    f_l = F(wt(12, "líder"))
    cr.location = (0.0, 0.88, 2.04); key(cr, "location", f_l - 1, "CONSTANT")
    for f in range(f_l, f_l + 14):                                                   # a coroa cai com giro (queda em ease-in)
        u = (f - f_l) / 13; cr.location = (0.18 * u, 0.88 - 0.4 * u, 2.04 - 1.6 * u * u); cr.rotation_euler = (0, math.radians(120 * u), 0)
        key(cr, "location", f, "LINEAR"); key(cr, "rotation_euler", f, "LINEAR")
    props.blink_vis(cr, [(A, True), (f_l + 14, True), (f_l + 15, False)], True)
    # ele, de lado, na ponta esquerda, vendo a cena
    H, tl = heroi(p, "q", -2.0, A, END); a = Actor(tl, 0.0)
    tl.intent(A, head=4, torso=1)
    tl.face(A, 0.0, lid="esperto", lidv=0.55, brow=-4, mouth="pequena", look=(0.9, 0.1))
    tl.face(F(t_tr), 1.0, wide=0.4, brow=14, browup=0.015, mouth="nervosa", look=(0.9, 0.1))
    tl.face(F(t_mt), 1.0, eye="ponto", brow=26, browup=0.025, mouth="o", extras=("!",), look=(0.9, 0.1))
    finish(H, tl, A, END)
    sombra_h(H, p)
    camara(c, t0, t1, (-0.75, -5.8, 1.5), (-0.5, -5.3, 1.6), 5.8, 5.3, entra="h", sai="v")


# ====================================================================== B11. O preço (59,65 - 62,82)
@cena_("b11", 59.65, 62.82)
def b11(c):
    A, END = F(59.3), F(63.2); t0, t1 = 59.65, 62.82
    p = pal("casa"); wy = 2.6
    S.fundo(p, wy, z_meio=2.6, x=(-10, 10), z=(-3, 10), escuro=0.12)
    pisos = [0.0, 1.35, 2.7]
    cores = ["#2a2f6a", "#33397a", "#3c4288", "#262b66", "#30367a"]
    n = 0; livre = None
    for r, z in enumerate(pisos):
        props.poly(f"laje{r}", cena.rect(-1.9, z - 0.05, 1.9, z + 0.02), _mix(p["aresta"], p["mid"], 0.45), wy - 0.1)
        for i in range(5):
            x = -1.5 + i * 0.75
            props.poly(f"cel{r}_{i}", cena.rect(x - 0.34, z + 0.02, x + 0.34, z + 1.22), _mix(p["top"], p["mid"], 0.25), wy - 0.05)
            pes = props.pessoa(f"ch{n}", x, 0.2 + 0.0, cores[(r + i) % 5], 0.58, flip=1 if i % 2 else -1, rim=p["borda"], z=z + 0.02)
            if n == 14:
                livre = (x, z)
            else:
                t = wt(13, "só") - 0.12 + 0.07 * n
                j = props.jaula(f"j{n}", x, z + 0.02, w=0.62, h=1.2, y=-0.2)
                j.location.z = z + 0.02 + 2.6; key(j, "location", F(t) - 1, "CONSTANT")
                for f in range(F(t), F(t) + 7):
                    u = (f - F(t)) / 6; j.location.z = z + 0.02 + 2.6 * (1 - curvas.s("queda", u)); key(j, "location", f, "LINEAR")
            n += 1
    xl, zl = livre
    cena.disc("foco_livre", 0.9, cena.amat("foco_livre_m", "#ffe9a8", 1.0, 0.0, ("radial", 1.3)), (xl, 0.1, zl + 0.65))
    m = bpy.data.objects["foco_livre"].data.materials[0]
    node = [nn for nn in m.node_tree.nodes if nn.type == "MATH" and nn.operation == "MULTIPLY"][0]
    for f_, a_ in ((F(wt(13, "só")) + 6, 0.0), (F(wt(13, "solto")), 0.7)):
        node.inputs[1].default_value = a_; node.inputs[1].keyframe_insert("default_value", frame=f_)
    # ele, de frente, lá embaixo à esquerda, olhando para cima (a escada de celas)
    H, tl = heroi(p, "front", -1.55, A, END, y=-0.8)
    tl.face(A, 0.0, wide=0.4, brow=10, browup=0.012, mouth="pequena", look=(0.3, 0.8))
    tl.face(F(wt(13, "só")), 1.0, eye="ponto", brow=26, browup=0.025, mouth="o", extras=("!",), look=(0.3, 0.8))
    finish(H, tl, A, END)
    frente.bracos(H, A, END, [(A, dict(shF=5, elF=0, shB=5, elB=0))])
    sombra_h(H, p)
    camara(c, t0, t1, (-0.1, -6.2, 1.5), (0.05, -7.6, 2.4), 6.2, 7.6, entra="v", sai="v")


# ====================================================================== B12. Ainda quer subir? (62,82 - 64,80)
@cena_("b12", 62.82, 64.8)
def b12(c):
    A, END = F(62.4), F(65.2); t0, t1 = 62.82, 64.8
    p = P; wy = 3.5
    pe = dict(p, mid=_mix(p["mid"], p["top"], 0.45), low=_mix(p["low"], p["top"], 0.35))
    S.fundo(pe, wy, z_meio=3.0, x=(-30, 30), z=(-4, 20))
    cena.disc("halo_b12", 5.0, cena.amat("halo_b12_m", p["halo"], 1.0, 0.45, ("radial", 1.5)), (2.4, wy - 0.1, 5.0))
    pd = dict(p, pedra=_mix(p["pedra"], p["aresta"], 0.28), mid=p["aresta"])
    degs = escada5(pd)
    for k, (r, n0, n1) in enumerate(degs):
        n0.scale = (0.0001,) * 3; key(n0, "scale", A, "CONSTANT")
    luz.feixe("feixe_b12", 4.4, 0.9, 6.0, 17.0, 1.5, 0.35, p["luz"], forca=1.5, frames=END, poeira=35, seed=77)
    H, tl = heroi(p, "q", -0.55, A, END)
    tl.intent(A, head=-18, torso=-3)
    tl.face(A, 0.0, wide=0.3, brow=8, browup=0.012, mouth="pequena", look=(0.8, 0.9))
    tl.face(F(wt(14, "quer")), 1.0, lid="esperto", lidv=0.6, brow=-8, browtilt=0.016, mouth="lado", look=(0.8, 0.9))
    finish(H, tl, A, END)
    sombra_h(H, p)
    camara(c, t0, t1, (1.7, -9.0, 3.2), (2.3, -13.5, 4.2), 9.0, 13.5, entra="v", sai=None)


if __name__ == "__main__":
    P4.main()
