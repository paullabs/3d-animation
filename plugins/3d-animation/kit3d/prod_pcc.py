"""Produção do vídeo PCC (5 níveis). Cada plano é um cenário próprio, renderizado à parte e montado depois.
blender -b -P prod_pcc.py -- PLANO OUT_DIR [--scale 1] [--samples 16] [--at t1,t2,...] [--frames a,b,c] [--list]
Os tempos vêm da narração (roteiros/voz-pcc/tempos.json e palavras.json)."""
import sys, os, math, json, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy, lib
from lib import *
import cena, props, limpo, semantico as S
from heroi import Heroi
from anim import Timeline
from acting import Actor

FPS = 24
VOZ = (__import__("canal38_env").RAIZ + "/roteiros/voz-pcc")
PAL_ = json.load(open(VOZ + "/palavras.json")) if os.path.exists(VOZ + "/palavras.json") else []


def F(t):
    return 1 + round(t * FPS)


def wt(frase, txt, nth=0):
    """tempo (s) em que a palavra 'txt' começa na frase 'frase' (n-ésima ocorrência)"""
    ws = [w for w in PAL_ if w["frase"] == frase and w["txt"].strip(".,:;!?…").lower() == txt.lower()]
    return ws[nth]["t0"]


SHOTS = {}


def shot(name, t0, t1):
    def deco(fn):
        SHOTS[name] = (t0, t1, fn); return fn
    return deco


def camera(c, keys, focus=4.5, fstop=0.8, lens=35, dof=True, interp="BEZIER"):
    """câmera que só desliza (translação); o 'rig' (pai) serve para tremidas de impacto"""
    cam = cena.camera(c["sc"], keys, lens=lens, focus=focus, fstop=fstop)
    cam.data.dof.use_dof = dof
    rig = empty("camrig"); cam.parent = rig
    c["cam"], c["rig"] = cam, rig
    return cam, rig


def hero(c, P, x=0.0, name="heroi", view="q", pal=None, prop=None, shadow=True, long=False):
    H = Heroi(name, view, pal=dict(rim=P["rim"], **(pal or {})), prop=prop)
    if shadow:
        cena.contact_shadow(H, P)
    if long:
        cena.long_shadow(H, P)
    return H


def finish(H, tl, f0, f1, boil=True):
    tl.bake(); tl.blinks(); tl.darts()
    if boil:
        H.boil(f0, f1, FPS, rate=3)


# ====================================================================== a rua do giz (níveis 1 e 2)
MEMBROS = ((1.0, 0.25, 1.0), (1.6, 0.6, 1.04), (2.0, 0.1, 0.98), (1.35, 1.0, 0.95), (1.15, -0.25, 1.02))
CORES_M = ["#2b2f45", "#3a2f3f", "#2a3a45", "#33323f", "#2d3340"]


def rua_giz(c):
    f1 = c["f1"]; tf0 = c["f0"] - 24
    limpo.palco("noite", spot_x=1.45, spot_w=1.45, frames=f1 + 30)
    P = limpo.P_de("noite")
    cena.ground_disc("giz_piso", 1.25, 0.95, cena.amat("giz_piso_m", "#cfe0ff", 1.0, 0.07), (1.35, 0.55, 0.0025), n=72)
    props.ring("giz", 1.35, 0.55, 1.25, 0.95, 0.06, "#aab6cc", gaps=((0.30, 0.36), (0.78, 0.82)))
    for i, (mx, my, mh) in enumerate(MEMBROS):
        p = props.pessoa(f"membro{i}", mx, my, "#141927", mh, flip=1 if i % 2 else -1, P=P, rim="#7f9bd0")
        props.sway(p, tf0, f1, 1.0 + 0.3 * i, 60 + 9 * i, i * 1.7)
    return P


def zera_balanco(tl, canais=("shF", "shB"), a=None, b=None):
    """tira o balanço de braço da caminhada (para segurar a caixa) entre os quadros a e b"""
    i0 = tl.i(a) if a is not None else 0; i1 = tl.i(b) if b is not None else tl.n
    for ch in canais:
        for k in range(i0, i1):
            tl.add[ch][k] = 0.0


# ====================================================================== NÍVEL 1: o ajudante (11.18 - 16.61)
@shot("n1", 11.18, 16.61)
def n1(c):
    sc, f0, f1 = c["sc"], c["f0"], c["f1"]; tf0 = f0 - 24
    P = rua_giz(c)
    H = hero(c, P, long=True)
    props.tint(H, props.GRAY)
    props.caixa("caixa", H.j["chest"], (0.38, -0.028, -0.09), 1.0)
    tl = Timeline(H, tf0, f1, FPS)
    t_walk = 10.45
    tl.stand(tf0, F(t_walk), -1.6)
    fend, xend = tl.walk(F(t_walk), 5, -1.6, step=12, stride=0.40)
    tl.stand(fend + 1, f1, xend)
    zera_balanco(tl)
    tl.intent(tf0, shF=20, elF=76, wrF=6, shB=16, elB=80, wrB=6, torso=0, head=0)
    tl.face(tf0, 0.0, lid="triste", lidv=0.3, brow=18, mouth="nervosa", extras=("suor",))
    a = Actor(tl, xend)
    a.look_around(F(12.75), beats=((0, (0.9, 0.1)), (16, (-0.8, 0.15)), (34, (0.9, 0.0))))
    tl.face(F(12.7), 1.0, wide=0.4, look=(0.9, 0.1), brow=20, mouth="nervosa", extras=("suor",))
    tl.intent(F(14.9), torso=0, head=0); tl.intent(F(15.15), torso=7, head=4)
    tl.face(F(15.1), 1.0, lid="triste", lidv=0.3, brow=14, look=(1.0, 0.0), mouth="pequena")
    tl.intent(F(15.5), torso=-9, head=-7)
    tl.face(F(15.45), 1.0, eye="ponto", brow=26, browup=0.025, mouth="o", extras=("!",))
    a.body(F(15.45), [(5, dict(dx=-0.02, e="out")), (12, dict(dx=-0.1, fF=(-0.1, 0.0, 0.0), fB=(-0.1, 0.0, 0.0), e="io"))], move_to=xend - 0.1)
    tl.intent(F(16.0), torso=9, head=15)
    tl.face(F(15.95), 1.0, lid="sono", lidv=0.8, brow=18, mouth="triste", extras=("sombra",), look=(0.0, -0.6))
    finish(H, tl, tf0, f1)
    red = props.ring("giz_vermelho", 1.35, 0.55, 1.25, 0.95, 0.08, "#e2364b", gaps=((0.30, 0.36), (0.78, 0.82)), z=0.0035)
    props.blink_vis(red, [(F(11.0), False), (F(15.12), True), (F(15.28), False), (F(15.36), True), (F(15.56), False), (F(15.66), True), (F(15.92), False)], True)
    camera(c, [(f0, (0.1, -3.7, 1.35)), (f1, (0.55, -3.45, 1.35))], focus=3.6, fstop=0.7)


# ====================================================================== NÍVEL 2: o membro (16.61 - 21.96)
@shot("n2a", 16.61, 21.96)
def n2a(c):
    sc, f0, f1 = c["sc"], c["f0"], c["f1"]; tf0 = f0 - 24
    P = rua_giz(c)
    # ---- o herói: cinza -> vermelho ao cruzar o giz
    H = hero(c, P, long=True)
    props.tint(H, props.GRAY, f=tf0)
    T_CRUZA = 18.15
    props.tint(H, props.GRAY, f=F(T_CRUZA + 0.42)); props.tint(H, props.RED, f=F(T_CRUZA + 0.55))
    boxp = props.caixa("caixa", H.j["chest"], (0.38, -0.028, -0.09), 1.0)
    tl = Timeline(H, tf0, f1, FPS); a = Actor(tl, -0.05)
    tl.stand(tf0, f1, -0.05)
    fend, xend = tl.walk(F(T_CRUZA), 3, -0.05, step=9, stride=0.30)
    tl.stand(fend + 1, f1, xend)
    zera_balanco(tl)
    tl.intent(tf0, shF=20, elF=76, wrF=6, shB=16, elB=80, wrB=6, torso=9, head=15)
    a = Actor(tl, xend)
    tl.face(tf0, 0.0, lid="sono", lidv=0.8, brow=18, mouth="triste", extras=("sombra",), look=(0.0, -0.6))
    tl.intent(F(17.3), torso=9, head=15); tl.intent(F(17.8), torso=0, head=-4)
    tl.face(F(17.75), 1.0, wide=0.6, browup=0.02, mouth="o", look=(-0.9, 0.5))                  # sente a mão no ombro
    tl.face(F(18.35), 1.0, browtilt=0.016, mouth="pequena", look=(0.7, 0.2))                      # curioso, vai entrar
    tl.face(F(18.95), 1.0, eye="feliz", mouth="sorrisao", browup=0.015)                           # agora é do grupo
    tl.intent(F(18.9), torso=-3, head=-6)
    tl.intent(F(19.6), torso=0, head=0)
    # a caixa escapa das mãos
    T_CAI = 20.2
    tl.intent(F(T_CAI - 0.15), shF=24, elF=70, shB=20, elB=74); tl.intent(F(T_CAI + 0.05), shF=4, elF=10, shB=-4, elB=10, wrF=0, wrB=0)
    tl.face(F(T_CAI), 1.0, eye="ponto", brow=26, browup=0.025, mouth="grito", extras=("!",))
    tl.face(F(20.8), 1.0, lid="sorriso", brow=16, mouth="nervosa", extras=("vergonha",), look=(0.0, -0.6))
    tl.intent(F(20.85), torso=8, head=12)
    finish(H, tl, tf0, f1)
    # ---- o padrinho: preto, de chapéu, um pouco maior e mais perto da câmera
    PD = Heroi("padrinho", "q", pal=dict(rim=P["rim"]))
    props.tint(PD, props.BLACK)
    wrap = empty("padrinho_wrap", None, (0, -0.3, 0)); wrap.scale = (1.08, 1.08, 1.08); PD.root.parent = wrap
    cena.contact_shadow(PD, P)
    props.chapeu(PD.face)
    ficha_ = props.ficha("ficha", PD.j["wrB"], (0.06, -0.01, -0.12), 0.8)
    props.blink_vis(ficha_, [(f0 - 30, False), (F(19.45), True)], True)
    tp = Timeline(PD, tf0, f1, FPS); ap = Actor(tp, -1.82)
    tp.stand(tf0, f1, -1.82)
    fe1, x1 = tp.walk(F(15.7), 4, -1.82, step=12, stride=0.40)
    tp.stand(fe1 + 1, F(T_CRUZA), x1)
    fe2, x2 = tp.walk(F(T_CRUZA + 0.05), 3, x1, step=9, stride=0.30)
    tp.stand(fe2 + 1, f1, x2)
    zera_balanco(tp, ("shF",), a=F(17.55))
    ap = Actor(tp, x2)
    tp.intent(F(17.45), shF=4, elF=10)
    tp.intent(F(17.95), shF=52, elF=40, wrF=-4)                                                  # mão no ombro do herói
    tp.face(tf0, 1.0, lid="sono", lidv=0.62, brow=-8, browup=-0.008, mouth="reta")
    tp.face(F(19.55), 1.0, lid="esperto", lidv=0.7, mouth="sorriso", brow=-6, browtilt=0.016)    # apresenta a ficha
    tp.intent(F(19.4), shB=-4, elB=10, torso=0); tp.intent(F(19.85), shB=118, elB=26, wrB=-6, torso=-3)
    tp.intent(F(20.95), shB=118, elB=26); tp.intent(F(21.3), shB=0, elB=10)
    tp.face(F(21.3), 1.0, eye="x", mouth="o", mouthv=0.5, brows=False)                           # leva a pancada do erro
    tp.face(F(21.62), 1.0, lid="sono", lidv=0.85, brow=14, mouth="triste", extras=("sombra",))
    ap.take(F(21.3), back=-0.05)
    finish(PD, tp, tf0, f1)
    # ---- a caixa cai e o conteúdo se espalha
    sc.frame_set(F(T_CAI)); bpy.context.view_layer.update()
    p0 = props.world_pos(boxp, F(T_CAI))
    queda = props.caixa("caixa_queda", None, (p0.x, p0.y, p0.z), 1.0)
    props.blink_vis(queda, [(f0 - 5, False), (F(T_CAI), True)], True)
    props.blink_vis(boxp, [(f0 - 5, True), (F(T_CAI), False)], True)
    props.ballistic(queda, F(T_CAI), (p0.x, p0.y, p0.z), (0.5, 0.0, 0.8), ground=0.13, e=0.3, spin=-160, frames=44)
    for i in range(4):
        pac = props.inked(f"pacote{i}", [(-0.05, -0.035), (0.05, -0.035), (0.05, 0.035), (-0.05, 0.035)], "#f4efe2", None, (p0.x, p0.y - 0.02, p0.z), w=0.006)
        props.blink_vis(pac, [(f0 - 5, False), (F(T_CAI) + 1, True)], True)
        props.ballistic(pac, F(T_CAI) + 1, (p0.x, p0.y - 0.02, p0.z), (0.5 + 0.55 * i, 0.0, 1.6 + 0.35 * (i % 2)), ground=0.04, e=0.25, spin=300 * (1 if i % 2 else -1), frames=44)
    # ---- a plaquinha "ERRO!" nasce na cabeça do herói e voa para o padrinho
    xh = xend
    tag = props.tag_erro("erro", (xh + 0.1, -0.1, 1.95), 1.0)
    tag.scale = (0.0001,) * 3
    f_in, f_fly, f_hit = F(20.62), F(21.0), F(21.28)
    S.pop(tag, f_in, 1.0, 7, 0.2)
    tag.location = (xh + 0.1, -0.1, 1.95); key(tag, "location", f_fly, "BEZIER")
    tag.location = (x2 + 0.35, -0.4, 2.2); key(tag, "location", f_hit, "BEZIER")
    tag.scale = (1, 1, 1); key(tag, "scale", f_hit - 1, "CONSTANT")
    tag.scale = (0.0001,) * 3; key(tag, "scale", f_hit, "CONSTANT")
    st = props.estrelas("impacto", (x2 + 0.35, -0.45, 2.0), s=1.0)
    props.blink_vis(st, [(f0 - 5, False), (f_hit, True), (f_hit + 5, False)], True)
    f_c = F(T_CRUZA + 0.5)
    br = props.estrelas("brilho_cruza", (xend - 0.2, -0.1, 1.2), r0=0.12, r1=0.4, s=1.2)
    props.blink_vis(br, [(f0 - 5, False), (f_c, True), (f_c + 6, False)], True)
    ouro = props.ring("giz_ouro", 1.35, 0.55, 1.25, 0.95, 0.12, "#ffd24a", gaps=((0.30, 0.36), (0.78, 0.82)), z=0.0035)
    props.blink_vis(ouro, [(f0 - 5, False), (f_c, True), (f_c + 4, False), (f_c + 7, True), (f_c + 12, False)], True)
    camera(c, [(f0, (-0.1, -4.5, 1.5)), (f1, (0.85, -4.3, 1.5))], focus=4.3)
    props.shake_rig(c["rig"], f_hit, 8, 0.05)


@shot("n2b", 21.96, 23.92)
def n2b(c):
    sc, f0, f1 = c["sc"], c["f0"], c["f1"]; tf0 = f0 - 6
    P = cena.PAL["manha"]
    sets_FOG = cena.sets.FOG; sets_FOG.update(color=P["haze"], near=4.0, far=110.0, max=0.9)
    props.sala(P, "#f1dfc4", "#c9a98a", "#8a6455")
    cena.shafts(P, [(2.5, 1.0, 1.4, 9.0, 0.2), (0.2, 0.6, 2.0, 9.5, 0.16)], f1 + 30, top_z=7.0)
    cena.dust(P, 80, (-3, 4), f1 + 30, size=(0.008, 0.02), z_range=(0.2, 3.4), y_range=(-1.5, 1.2))
    H = hero(c, P, long=False)
    tl = Timeline(H, tf0, f1, FPS); tl.stand(tf0, f1, -0.7)
    a = Actor(tl, -0.7)
    tl.face(tf0, 0.0, lid="apertado", lidv=0.75, browtilt=-0.012, brow=-8, mouth="lado", look=(0.8, 0.2))
    a.cross_arms(F(22.0))
    tl.face(F(23.3), 1.0, lid="sono", lidv=0.8, brow=18, mouth="triste", extras=("sombra",), look=(0.8, -0.2))
    finish(H, tl, tf0, f1)
    cal, centers = props.calendario("cal", 0.75, 1.5)
    for i, (cx, cz) in enumerate(centers):
        t = 22.30 + i * 0.105
        m = props.moeda(f"moeda{i}", (0.75 + cx, -0.03, 1.5 + cz), 0.115)
        props.drop(m, F(t), 1.5 + cz, 1.5 + cz + 2.6, frames=7, bounce=0.2)
        props.blink_vis(m, [(f0 - 5, False), (F(t) - 1, False), (F(t), True)], True)
    camera(c, [(f0, (0.0, -4.5, 1.5)), (f1, (0.1, -4.35, 1.5))], focus=4.4)


# ====================================================================== GANCHO: a multidão (0.0 - 3.55)
@shot("h1a", 0.0, 3.55)
def h1a(c):
    sc, f0, f1 = c["sc"], c["f0"], c["f1"]
    P = dict(cena.PAL["drama"])
    sets_ = cena.sets
    sets_.FOG.update(color="#1a2a55", near=60.0, far=560.0, max=0.78)
    props.skywall("ceu_h1", 900, [(-100, "#1b2c5a"), (40, "#13214a"), (140, "#0a1332"), (400, "#03060f")], -3000, 3000, -400, 800)
    cena.disc("lua_h1", 15.0, cena.amat("lua_h1_m", "#e8f2ff", 2.0, 1.0), (-260, 880, 330))
    sets_.glow("lua_h1_g", "#7fa0d8", 150, (-260, 870, 330), power=2.4, strength=0.55)
    cols = ["#3a4a78", "#47406a", "#33567a", "#4d4066", "#3d5a52", "#58476e", "#36496e", "#5a6280", "#8a4a52"]
    crowd, heads, prof = props.multidao("multidao", 40000, 2.0, 9.0, 340.0, -0.50, 0.04, cols, seed=11, head="#0c0f22")
    props.terreno("encosta", prof, 9.0, 340.0, color="#121c3e")
    sc.world.node_tree.nodes["Background"].inputs[0].default_value = (0.005, 0.008, 0.02, 1)
    # a torre da cela no alto da encosta
    ty = 360.0
    cena.flat("torre", cena.rect(-34, -40, 34, 96), "#0d1320", ty, fog=True)
    cena.flat("torre_topo", cena.rect(-38, 96, 38, 101), "#080c16", ty - 0.2, fog=True)
    cena.flat("torre_luz", cena.rect(-34, -40, -26, 96), "#16203a", ty - 0.2, fog=True)
    rnd = random.Random(3)
    for r in range(9):
        for k in range(-5, 6):
            if abs(k) <= 1 and r in (6, 7):
                continue
            on = rnd.random() < 0.18
            cena.flat(f"torre_j{r}_{k}", cena.rect(k * 5.6 - 1.0, 12 + r * 8.6, k * 5.6 + 1.0, 12 + r * 8.6 + 3.4), "#ffc266" if on else "#0a0f1b", ty - 0.4, 1.4 if on else 1.0, fog=True)
    # a janela da cela (a mesma do plano seguinte)
    wz = 73.0
    cena.flat("torre_jan", cena.rect(-3.0, wz - 2.2, 3.0, wz + 2.2), "#ffd9a0", ty - 0.6, 3.0, fog=False)
    for i in range(5):
        cena.flat(f"torre_jan_b{i}", cena.rect(-3.0 + 6.0 * (i + 0.5) / 5 - 0.18, wz - 2.2, -3.0 + 6.0 * (i + 0.5) / 5 + 0.18, wz + 2.2), "#1a1208", ty - 0.7, fog=False)
    sets_.glow("torre_jan_glow", "#ffb35c", 70, (0, ty - 2, wz), power=2.0, strength=1.1)
    # luz que desce da janela sobre a multidão
    cone = cena.poly_mesh("torre_cone", [(-1, 0, 0), (1, 0, 0), (0.1, 0, 1), (-0.1, 0, 1)], cena.amat("torre_cone_m", "#ffb35c", 1.0, 0.16, ("shaft", 1.1, 0.9)))
    cone.location = (0, ty - 4, 4); cone.scale = (60, 1, 70)
    # fios finos da janela até a multidão: desenham-se enquanto a câmera sobe
    rnd2 = np_random(5)
    idx = rnd2.choice(len(heads), 26, replace=False)
    for i, j in enumerate(idx):
        h = heads[j]
        ln = props.fio(f"fio{i}", (0.0, ty - 5, wz - 1.0), (float(h[0]), float(h[1]), float(h[2]) + 0.3), w=0.16 + 0.0007 * float(h[1]), color="#9fd6ff", strength=3.0, alpha=0.55)
        t = 1.9 + 0.9 * (i / 26.0)
        ln.scale = (0.0001,) * 3; key(ln, "scale", F(t) - 1, "CONSTANT")
        ln.scale = (1, 1, 1); key(ln, "scale", F(t) + 5, "BEZIER")
    cam, rig = camera(c, [(f0, (0.0, 0.0, 2.0)), (F(1.7), (0.0, 6.0, 15.0)), (F(3.0), (0.0, 120.0, 58.0)), (f1, (0.0, 205.0, 73.0))], focus=300.0, fstop=4.0)
    cam.data.dof.use_dof = False


def np_random(seed):
    import numpy as np
    return np.random.default_rng(seed)


# ====================================================================== GANCHO: a cela (3.55 - 7.34)
@shot("cela", 3.55, 7.34)
def cela(c):
    sc, f0, f1 = c["sc"], c["f0"], c["f1"]
    P = dict(cena.PAL["drama"])
    sc.world.node_tree.nodes["Background"].inputs[0].default_value = (0.01, 0.015, 0.03, 1)
    info = props.cela_interior(P, f1 + 30)
    H = hero(c, P)
    tl = Timeline(H, f0, f1, FPS); tl.stand(f0, f1, 0.15); a = Actor(tl, 0.15)
    tl.face(f0, 0.0, lid="sono", lidv=0.62, brow=-8, browup=-0.008, mouth="reta", look=(0.6, 0.15))
    a.cross_arms(F(3.62))
    tl.intent(F(5.2), torso=0, head=0); tl.intent(F(5.55), torso=-2, head=-5)
    tl.face(F(5.3), 1.0, lid="esperto", lidv=0.55, mouth="sorriso", brow=-8, browtilt=0.012, look=(-0.5, 0.1))   # o chefe (leve sorriso frio)
    tl.face(F(6.7), 1.0, lid="sono", lidv=0.62, brow=-8, browup=-0.008, mouth="reta", look=(0.6, 0.15))
    finish(H, tl, f0, f1)
    # luzes da polícia piscando (vermelho/azul) pela janela e no fundo
    red = cena.disc("pol_verm", 1.7, cena.amat("pol_verm_m", "#ff2d3d", 2.0, 0.3, ("radial", 1.5)), (0.3, 1.3, 2.6))
    blu = cena.disc("pol_azul", 1.7, cena.amat("pol_azul_m", "#2d7bff", 2.0, 0.3, ("radial", 1.5)), (2.1, 1.3, 2.6))
    wash_r = cena.poly_mesh("pol_lav_r", [(-4.5, 1.46, -1), (4.5, 1.46, -1), (4.5, 1.46, 4.4), (-4.5, 1.46, 4.4)], cena.amat("pol_lav_rm", "#ff2d3d", 1.0, 0.08))
    wash_b = cena.poly_mesh("pol_lav_b", [(-4.5, 1.46, -1), (4.5, 1.46, -1), (4.5, 1.46, 4.4), (-4.5, 1.46, 4.4)], cena.amat("pol_lav_bm", "#2d7bff", 1.0, 0.08))
    t = 4.19; seq_r = []; seq_b = []
    while t < 7.3:
        seq_r += [(F(t), True), (F(t) + 3, False)]; seq_b += [(F(t) + 3, True), (F(t) + 6, False)]
        t += 0.5
    for o, sq in ((red, seq_r), (wash_r, seq_r), (blu, seq_b), (wash_b, seq_b)):
        props.blink_vis(o, [(f0 - 5, False)] + sq, True)
    # etiqueta "CHEFE" sobre ele quando a narração diz "o chefe do PCC"
    tg = props.inked("chefe_tag", props.rrect(-0.3, -0.12, 0.3, 0.12, 0.05, 5), "#e2364b", None, (0.2, -1.35, 2.05), w=0.014, shade=0.02, shade_color="#a82336")
    props.txt("chefe_tag_t", "CHEFE", 0.15, "#ffffff", (0.0, -0.006, 0.0), tg, ink="#7a1626", ow=0.05)
    tg.scale = (0.62, 0.62, 0.62)
    S.pop(tg, F(wt(2, "chefe")), 0.62, 7, 0.2)
    props.blink_vis(tg, [(f0 - 5, False), (F(wt(2, "chefe")) - 1, False), (F(wt(2, "chefe")), True)], True)
    # o LED da câmera de vigia pisca
    props.blink_vis(info["led"], [(f, (i % 2 == 0)) for i, f in enumerate(range(f0, f1, 12))], True)
    camera(c, [(f0, (0.15, -2.7, 1.55)), (F(4.4), (0.15, -2.95, 1.55)), (f1, (0.15, -3.7, 1.5))], focus=2.9, fstop=0.9)


# ====================================================================== FINAL: a cela de novo (61.61 - 63.55)
@shot("p2", 61.61, 63.55)
def p2(c):
    sc, f0, f1 = c["sc"], c["f0"], c["f1"]
    P = dict(cena.PAL["drama"])
    sc.world.node_tree.nodes["Background"].inputs[0].default_value = (0.01, 0.015, 0.03, 1)
    info = props.cela_interior(P, f1 + 30, final=True, pcc_x=-1.05)
    H = hero(c, P, view="front")
    tl = Timeline(H, f0, f1, FPS); tl.stand(f0, f1, 0.0); a = Actor(tl, 0.0)
    tl.face(f0, 0.0, lid="sono", lidv=0.62, brow=-8, browup=-0.008, mouth="reta")
    tl.face(F(62.3), 1.0, lid="apertado", lidv=0.6, brow=-10, mouth="reta")
    finish(H, tl, f0, f1)
    props.blink_vis(info["led"], [(f, (i % 2 == 0)) for i, f in enumerate(range(f0, f1, 10))], True)
    camera(c, [(f0, (0.0, -3.2, 1.55)), (f1, (0.0, -2.35, 1.6))], focus=3.0, fstop=0.9)


# ====================================================================== GANCHO: a escada e o '?' (7.34 - 11.18)
@shot("h3", 7.34, 11.18)
def h3(c):
    sc, f0, f1 = c["sc"], c["f0"], c["f1"]
    P, st = props.cena_escada(c, "alvorada")
    H = hero(c, P)
    tl = Timeline(H, f0, f1, FPS); tl.stand(f0, f1, 0.0); a = Actor(tl, 0.0)
    tl.intent(f0, head=-14, torso=-2)
    tl.face(f0, 0.0, browtilt=0.016, mouth="pequena", look=(0.6, 0.6))
    tl.face(F(8.9), 1.0, wide=0.6, browup=0.02, mouth="o", look=(0.7, 0.8))                 # "tem um número..."
    tl.face(F(10.2), 1.0, wide=1.0, browup=0.03, mouth="o", look=(0.8, 0.9), extras=("?",))  # "parece mentira"
    finish(H, tl, f0, f1)
    q = props.interrogacao("pergunta", 8.4, 7.5, 1.35)
    t_q = F(9.2)
    S.pop(q, t_q, 1.35, 9, 0.25)
    props.blink_vis(q, [(f0 - 5, False), (t_q - 1, False), (t_q, True)], True)
    for k in range(t_q + 14, f1, 14):                                                       # pulsa
        q.scale = (1.35, 1.35, 1.35); key(q, "scale", k, "BEZIER")
        q.scale = (1.5, 1.5, 1.5); key(q, "scale", k + 7, "BEZIER")
    camera(c, [(f0, (1.0, -7.6, 1.8)), (F(8.7), (3.4, -8.4, 3.6)), (f1, (7.6, -8.0, 7.4))], focus=8.0, fstop=2.0, dof=False)


# ====================================================================== NÍVEL 5: o topo (41.02 - 43.56)
@shot("n5a", 41.02, 43.56)
def n5a(c):
    sc, f0, f1 = c["sc"], c["f0"], c["f1"]
    P, st = props.cena_escada(c, "dourado", numbers=True, sun_x=22.0)
    SH = props.STEP["SH"] * props.STEP["N"]
    H = hero(c, P, long=False)
    wrap = empty("heroi_wrap", None, (0, 0.0, SH)); H.root.parent = wrap
    tl = Timeline(H, f0, f1, FPS); tl.stand(f0, f1, 8.1); a = Actor(tl, 8.1)
    tl.face(f0, 0.0, eye="ponto", brow=26, browup=0.025, mouth="o")
    tl.face(F(41.55), 1.0, eye="cifrao", mouth="sorrisao", browup=0.015, extras=("brilho",))   # olhos de cifrão
    a.celebrate(F(41.35)); a.release(F(42.4), 14)
    tl.face(F(42.9), 1.0, eye="cifrao", mouth="sorrisao", browup=0.015, extras=("brilho",))
    finish(H, tl, f0, f1)
    # ele chega pulando de baixo para o terraço (sobe de fora do quadro)
    wrap.location.z = SH - 4.5; key(wrap, "location", f0, "BEZIER")
    wrap.location.z = SH - 4.5; key(wrap, "location", F(41.1), "BEZIER")
    wrap.location.z = SH + 0.25; key(wrap, "location", F(41.34), "BEZIER")
    wrap.location.z = SH; key(wrap, "location", F(41.46), "BEZIER")
    camera(c, [(f0, (8.6, -7.0, 7.4)), (f1, (8.9, -6.4, 8.7))], focus=6.9, fstop=2.0)


# ====================================================================== FINAL: os 15 do topo e as grades (55.92 - 61.61)
@shot("p1", 55.92, 61.61)
def p1(c):
    sc, f0, f1 = c["sc"], c["f0"], c["f1"]
    P, st = props.cena_escada(c, "noite_fria", gray=True, numbers=True, stars=True)
    SH = props.STEP["SH"] * props.STEP["N"]
    H = hero(c, P)
    wrap = empty("heroi_wrap", None, (0, 0.0, SH)); H.root.parent = wrap
    tl = Timeline(H, f0, f1, FPS); tl.stand(f0, f1, 7.7); a = Actor(tl, 7.7)
    tl.intent(f0, head=-6)
    tl.face(f0, 0.0, lid="sono", lidv=0.8, brow=14, mouth="triste", look=(0.7, 0.3))
    tl.face(F(59.3), 1.0, wide=0.7, brow=22, browup=0.02, mouth="nervosa", look=(0.8, 0.2), extras=("suor",))
    tl.face(F(60.4), 1.0, eye="ponto", brow=30, browup=0.03, mouth="grito", extras=("suor", "!"))
    finish(H, tl, f0, f1)
    cores = ["#2a2f45", "#33294a", "#2a3d4d", "#3a2f3a", "#2d3a33", "#3a3a4a", "#2b2a3c"]
    X0F, DX = 8.55, 0.36
    for i in range(15):
        f = props.pessoa(f"chefe{i}", X0F + DX * i, 0.0, cores[i % len(cores)], 1.0, flip=1 if i % 2 else -1, P=P, z=SH)
        props.sway(f, f0, f1, 0.8, 70 + 5 * i, i * 0.7)
    t0c = wt(13, "só") - 0.12
    for i in range(14):
        tcl = t0c + 0.07 * i
        j = props.jaula(f"jaula{i}", X0F + DX * i, SH, w=0.36, h=1.9)
        props.drop(j, F(tcl), SH, SH + 3.4, frames=6, bounce=0.1)
        props.blink_vis(j, [(f0 - 5, False), (F(tcl) - 1, False), (F(tcl), True)], True)
    # o único solto: foco de luz e um pulo curto
    xs = X0F + DX * 14
    foco = cena.disc("foco_solto", 1.3, cena.amat("foco_solto_m", "#ffe9a8", 1.0, 0.0, ("radial", 1.3)), (xs, 0.2, SH + 1.0))
    m = foco.data.materials[0]
    node = [n for n in m.node_tree.nodes if n.type == "MATH" and n.operation == "MULTIPLY"][0]
    for f_, a_ in ((F(t0c + 0.07 * 14), 0.0), (F(t0c + 0.07 * 14 + 0.3), 0.55)):
        node.inputs[1].default_value = a_; node.inputs[1].keyframe_insert("default_value", frame=f_)
    camera(c, [(f0, (10.62, -10.2, 6.9)), (f1, (10.72, -9.9, 6.9))], focus=9.0, fstop=2.0, dof=False)


# ====================================================================== NÍVEL 3: o fiscal (23.92 - 31.78)
def sala_fria(c, P=None):
    P = P or dict(cena.PAL["manha"])
    cena.sets.FOG.update(color="#cfd8e6", near=6.0, far=80.0, max=0.5)
    props.sala(P, top="#e4eaf2", bottom="#aab6c8", floor="#6b7385", y=1.4)
    cena.shafts(P, [(2.6, 0.9, 1.3, 9.0, 0.2), (0.4, 0.6, 2.0, 9.5, 0.14)], c["f1"] + 30, top_z=7.0)
    cena.dust(P, 70, (-3, 4), c["f1"] + 30, size=(0.008, 0.02), z_range=(0.2, 3.8), y_range=(-1.5, 1.2))
    return P


@shot("n3a", 23.92, 27.0)
def n3a(c):
    sc, f0, f1 = c["sc"], c["f0"], c["f1"]
    P = sala_fria(c)
    mp, centers, g = props.mapa("mapa", 0.55, 2.0)
    blocks = [(1, 2), (2, 2), (1, 3), (2, 3), (2, 4), (3, 3)]
    hl, hc = props.area_realce("area", mp, centers, blocks, g["bw"], g["bh"])
    t_a = F(wt(7, "fiscal")); t_f = F(wt(7, "área"))
    props.blink_vis(hl, [(f0 - 5, False), (t_a - 1, False), (t_a, True)], True)
    flag = props.bandeira("bandeira", (hc[0] - 0.1, -0.03, hc[1] - 0.15), 1.0, mp)
    props.blink_vis(flag, [(f0 - 5, False), (t_f - 1, False), (t_f, True)], True)
    S.pop(flag, t_f, 1.0, 8, 0.25)
    H = hero(c, P)
    wrap = empty("heroi_wrap", None, (-1.0, -0.45, 0.0)); wrap.scale = (1.4, 1.4, 1.4); H.root.parent = wrap
    tl = Timeline(H, f0, f1, FPS); tl.stand(f0, f1, 0.0); a = Actor(tl, 0.0)
    tl.face(f0, 0.0, lid="sono", lidv=0.55, brow=-6, mouth="reta", look=(0.7, 0.2))
    a.cross_arms(F(24.45))
    tl.face(F(24.9), 1.0, lid="esperto", lidv=0.6, mouth="sorriso", brow=-6, browtilt=0.016)
    tl.intent(F(25.7), torso=0, head=-5); tl.intent(F(26.1), torso=-2, head=-9)
    finish(H, tl, f0, f1)
    camera(c, [(f0, (0.0, -5.0, 1.95)), (f1, (0.12, -4.6, 2.05))], focus=4.6, fstop=1.0)


@shot("n3b", 27.0, 31.78)
def n3b(c):
    sc, f0, f1 = c["sc"], c["f0"], c["f1"]
    P = sala_fria(c)
    cam, rig = camera(c, [(f0, (0.1, -4.8, 1.95)), (f1, (0.1, -4.35, 2.0))], focus=4.5, fstop=1.0)
    # 1) as regras e o X de "quebrou"
    cl, caixas = props.prancheta("regras", (0.0, 0.0, 2.15), 1.5)
    S.pop(cl, f0 - 3, 1.5, 6, 0.15)
    for i, (bx, bz) in enumerate(caixas):
        x_ = props.xis(f"xis{i}", (bx * 1.5, -0.05, 2.15 + bz * 1.5), 1.1)
        tt = F(wt(7, "quebra") + 0.06 * i)
        props.blink_vis(x_, [(f0 - 5, False), (tt - 1, False), (tt, True)], True)
        S.pop(x_, tt, 1.1, 5, 0.3)
    t_v = F(wt(7, "tribunal") - 0.08)
    props.vanish(cl, t_v - 4, 4)
    for i in range(3):
        props.vanish(bpy.data.objects[f"xis{i}"], t_v - 4, 4)
    # 2) o tribunal e o martelo
    tb = props.tribunal("tribunal", (0.0, 0.1, 1.55), 1.0)
    props.blink_vis(tb, [(f0 - 5, False), (t_v - 1, False), (t_v, True)], True)
    S.pop(tb, t_v, 1.0, 7, 0.12)
    pv, bloco = props.martelo("martelo", (1.55, -0.05, 1.5), 1.0)
    props.blink_vis(bloco, [(f0 - 5, False), (t_v - 1, False), (t_v, True)], True)
    t_hit = F(wt(7, "tribunal") + 0.02)
    ang = lambda d: math.radians(d)
    pv.rotation_euler = (0, ang(-50), 0); key(pv, "rotation_euler", f0, "BEZIER")
    pv.rotation_euler = (0, ang(-50), 0); key(pv, "rotation_euler", t_v + 3, "BEZIER")
    pv.rotation_euler = (0, ang(-64), 0); key(pv, "rotation_euler", t_hit - 3, "BEZIER")
    pv.rotation_euler = (0, ang(0), 0); key(pv, "rotation_euler", t_hit, "BEZIER")
    pv.rotation_euler = (0, ang(-9), 0); key(pv, "rotation_euler", t_hit + 3, "BEZIER")
    pv.rotation_euler = (0, ang(0), 0); key(pv, "rotation_euler", t_hit + 6, "BEZIER")
    props.blink_vis(pv, [(f0 - 5, False), (t_v - 1, False), (t_v, True)], True)
    fx = props.estrelas("batida", (0.05, -0.1, 1.3), r0=0.15, r1=0.5, s=1.3)
    props.blink_vis(fx, [(f0 - 5, False), (t_hit, True), (t_hit + 6, False)], True)
    props.shake_rig(rig, t_hit, 10, 0.09, seed=5)
    wsh, a_wsh = props.dim(cam, "flash", "#ffffff")
    props.wash(a_wsh, [(f0, 0.0), (t_hit - 1, 0.0), (t_hit, 0.55), (t_hit + 5, 0.0)])
    # 3) a régua da pena (o tribunal e o martelo saem) e o escurecer
    t_r = F(wt(7, "pena") - 0.4)
    for o in (tb, pv, bloco, fx):
        props.vanish(o, t_r, 4)
    rg, marc, xi, xf = props.regua_pena("regua", (0.0, 0.0, 2.1), 2.4)
    props.blink_vis(rg, [(f0 - 5, False), (t_r - 1, False), (t_r + 2, True)], True)
    S.pop(rg, t_r + 2, 1.0, 8, 0.1)
    t_p = F(wt(7, "pena")); t_m = F(wt(7, "morte"))
    marc.location.x = xi; key(marc, "location", t_p - 2, "BEZIER")
    marc.location.x = xi + (xf - xi) * 0.22; key(marc, "location", t_p + 10, "BEZIER")
    marc.location.x = xi + (xf - xi) * 0.55; key(marc, "location", t_m - 8, "BEZIER")
    marc.location.x = xf; key(marc, "location", t_m, "BEZIER")
    cav = props.caveira("caveira", (0.0, -0.1, 3.05), 0.78)
    cav.scale = (0.78, 0.78, 0.78)
    props.blink_vis(cav, [(f0 - 5, False), (t_m - 1, False), (t_m, True)], True)
    S.pop(cav, t_m, 0.78, 9, 0.25)
    props.shake_rig(rig, t_m, 12, 0.11, seed=9)
    dk, a_dk = props.dim(cam, "escuro", "#05060c")
    props.wash(a_dk, [(f0, 0.0), (t_r, 0.0), (t_p + 8, 0.45), (t_m - 2, 0.62), (t_m + 4, 0.8)])


# ====================================================================== NÍVEL 4: o chefe de setor (31.78 - 41.02)
@shot("n4", 31.78, 41.02)
def n4(c):
    sc, f0, f1 = c["sc"], c["f0"], c["f1"]
    limpo.palco("quente", spot_x=0.2, spot_w=1.9, frames=f1 + 30)
    P = limpo.P_de("quente")
    props.DESAT = 0.55
    X0 = -0.12
    props.inked("painel", props.rrect(-0.75 + X0, 0.95, 1.95 + X0, 3.88, 0.06, 5), "#1b1410", None, (0, 0.5, 0), w=0.02, rim=0.012, rim_color="#4a382b")
    topo = props.inked("card_topo", props.rrect(-0.8, -0.24, 0.8, 0.24, 0.06, 5), "#c62f35", None, (X0 + 0.55, -0.02, 3.47), w=0.018, shade=0.03, shade_color="#8f1f27", rim=0.01, rim_color="#e8545a")
    props.txt("card_topo_t", "FACÇÃO", 0.17, "#ffffff", (0.0, -0.006, 0.0), topo, ink=None)
    rows = [("DROGA", "#c99a5b", props.icone_pacote, 36.26, 35), ("DINHEIRO", "#f2b83a", lambda n, p, l, s: props.moeda(n, (l[0], l[1], l[2]), 0.17 * s, p), 37.10, 24),
            ("ADVOGADOS", "#4a4f6a", props.icone_maleta, 37.96, 10), ("REDES", "#3d7bff", props.icone_curtir, 39.48, -7)]
    zs = [2.92, 2.43, 1.94, 1.45]
    props.poly("tronco", cena.rect(X0 - 0.62, zs[-1] - 0.02, X0 - 0.585, 3.47), "#b9a58e", 0.45)
    props.poly("tronco_topo", cena.rect(X0 - 0.62, 3.45, X0 - 0.25, 3.49), "#b9a58e", 0.45)
    t_sk = F(33.3)
    for i, (lab, col, ic, tt, up) in enumerate(rows):
        ph = props.inked(f"ph{i}", props.rrect(X0 - 0.45, zs[i] - 0.21, X0 + 1.65, zs[i] + 0.21, 0.06, 5), "#2a201a", None, (0, 0.2, 0), w=0.012, rim=0.01, rim_color="#4a382b")
        props.poly(f"stub{i}", cena.rect(X0 - 0.62, zs[i] - 0.02, X0 - 0.45, zs[i] + 0.02), "#b9a58e", 0.45)
        props.blink_vis(ph, [(f0 - 5, False), (t_sk + 3 * i - 1, False), (t_sk + 3 * i, True)], True)
        S.pop(ph, t_sk + 3 * i, 1.0, 6, 0.12)
        cd = props.orgcard(f"card{i}", (X0 + 0.6, -0.02, zs[i]), 2.1, 0.42, lab, "#5a463a", ic, 0.13, fill="#33281f", txt_c="#f1e6d6", shade_c="#241b15", rim_c="#6a5242")
        props.blink_vis(cd, [(f0 - 5, False), (F(tt) - 1, False), (F(tt), True)], True)
        S.pop(cd, F(tt), 1.0, 7, 0.14)
    props.blink_vis(topo, [(f0 - 5, False), (F(32.35) - 1, False), (F(32.35), True)], True)
    S.pop(topo, F(32.35), 1.0, 7, 0.12)
    vm = props.inked("voce", props.rrect(-0.32, -0.12, 0.32, 0.12, 0.05, 5), "#e2364b", None, (X0 + 1.25, -0.06, zs[0] + 0.42), w=0.014, shade=0.02, shade_color="#a82336")
    props.txt("voce_t", "VOCÊ", 0.14, "#ffffff", (0, -0.006, 0), vm, ink="#7a1626", ow=0.05)
    tv = F(wt(8, "setor"))
    props.blink_vis(vm, [(f0 - 5, False), (tv - 1, False), (tv, True), (F(36.1), False)], True)
    S.pop(vm, tv, 1.0, 7, 0.2)
    H = hero(c, P)
    tl = Timeline(H, f0, f1, FPS); tl.stand(f0, f1, -1.1); a = Actor(tl, -1.1)
    tl.face(f0, 0.0, lid="esperto", lidv=0.6, mouth="sorriso", brow=-6, browtilt=0.012, look=(0.8, 0.3))
    a.cross_arms(F(32.3)); a.release(F(35.0), 12)
    for lab, col, ic, tt, up in rows:
        f = a.point(F(tt - 0.32), up=up); a.release(f + 8, 10, chans=("shF", "elF", "wrF"))
        tl.face(F(tt - 0.4), 1.0, lid="esperto", lidv=0.7, mouth="lado", brow=-8, browtilt=0.014, look=(0.9, 0.4 + up / 100.0))
    finish(H, tl, f0, f1)
    props.DESAT = 0.0
    camera(c, [(f0, (-0.05, -5.3, 2.0)), (f1, (0.08, -4.95, 2.05))], focus=5.0, fstop=0.8)


# ====================================================================== NÍVEL 5: os postos de gasolina (43.56 - 51.5)
@shot("n5b", 43.56, 51.5)
def n5b(c):
    sc, f0, f1 = c["sc"], c["f0"], c["f1"]
    P = dict(cena.PAL["drama"], horizon="#1b2f5c", sky_mid="#10204a", sky_top="#060b1c")
    cena.sky(P, sc)
    cena.sets.FOG.update(color="#10204a", near=200.0, far=900.0, max=0.0)
    sets_ = cena.sets
    sets_.glow("fundo_brilho", "#2a4a9a", 40, (0.0, 6.0, 1.5), power=1.6, strength=0.7)
    t_p = F(wt(11, "postos")); t_i = F(43.6)
    pasta, lupa = props.pasta_investigacao("pasta", (0.0, 0.0, 1.5), 1.25)
    S.pop(pasta, f0 - 2, 1.25, 7, 0.15)
    lupa.location = (0.45, -0.02, -0.15); key(lupa, "location", f0, "BEZIER")
    lupa.location = (0.1, -0.02, 0.25); key(lupa, "location", F(44.4), "BEZIER")
    lupa.location = (0.5, -0.02, -0.1); key(lupa, "location", F(45.0), "BEZIER")
    props.vanish(pasta, t_p - 3, 4)
    ZC = 1.5
    cols_, rows_ = 25, 40
    grid = [((i - (cols_ - 1) / 2) * 1.1, (j - (rows_ - 1) / 2) * 1.0) for i in range(cols_) for j in range(rows_)]
    grid.sort(key=lambda p_: (p_[0] / 1.1) ** 2 + (p_[1]) ** 2 * 0.55)
    est = [grid[0:1], grid[1:10], grid[10:100], grid[100:]]
    tms = [t_p, F(45.55), F(45.95), F(46.35)]
    for k, grp in enumerate(est):
        o = props.campo_icones(f"postos{k}", props.BOMBA, [(x, z - 0.45) for x, z in grp], 1.0, jitter=0.0)
        o.location = (0.0, 0.0, ZC)
        o.scale = (0.0001,) * 3; key(o, "scale", tms[k] - 1, "CONSTANT")
        S.pop(o, tms[k], 1.0 if k else 2.4, 9, 0.1)
        if k == 0:
            o.scale = (2.4,) * 3; key(o, "scale", F(45.5) - 1, "BEZIER")
            o.scale = (1.0,) * 3; key(o, "scale", F(45.55), "BEZIER")
    pcc = props.etiqueta("pcc", "PCC", (0.0, -0.6, ZC + 2.5), 1.0, "#e2364b", 0.34, 0.95)
    t_f = F(wt(11, "facção"))
    props.blink_vis(pcc, [(f0 - 5, False), (t_f - 1, False), (t_f, True)], True)
    S.pop(pcc, t_f, 6.0, 9, 0.2)
    props.vanish(pcc, F(48.05), 4)
    rnd = random.Random(21)
    t_m = wt(11, "movimentaram")
    for i in range(70):
        x0 = rnd.uniform(-12, 12); z0 = ZC + rnd.uniform(-17, 12)
        t0 = F(t_m + 0.05 + rnd.uniform(0.0, 2.6)); dur = rnd.randint(18, 30)
        m = props.moeda(f"coin{i}", (x0, -0.8, z0), 0.42, None)
        props.blink_vis(m, [(f0 - 5, False), (t0 - 1, False), (t0, True), (t0 + dur, False)], True)
        props.slide(m, t0, t0 + dur, (x0, -0.8, z0), (x0 * 0.55, -0.8, z0 + rnd.uniform(5, 9)), "LINEAR")
    camera(c, [(f0, (0.0, -4.6, 1.5)), (F(45.4), (0.0, -4.6, 1.5)), (F(46.7), (0.0, -42.0, ZC)), (f1, (0.0, -41.0, ZC))], focus=20.0, fstop=3.0, dof=False)


# ====================================================================== NÍVEL 5: a pilha vista de baixo (51.5 - 52.6)
@shot("n5c1", 51.5, 52.6)
def n5c1(c):
    sc, f0, f1 = c["sc"], c["f0"], c["f1"]
    P, st = props.cena_escada(c, "alvorada", numbers=False, stars=True)
    for o in list(bpy.data.objects):
        if o.name.startswith(("deg", "escada")):
            o.hide_render = True
    props.pilha_notas("pilha_base", 1.0, 2.4, 60, 0.5)
    props.txt("nota100", "R$ 100", 0.34, "#ffffff", (1.0, -0.02, 0.9), None, ink=props.INK, ow=0.08)
    H = hero(c, P)
    tl = Timeline(H, f0, f1, FPS); tl.stand(f0, f1, -0.7); a = Actor(tl, -0.7)
    tl.intent(f0, head=-22)
    tl.face(f0, 0.0, eye="ponto", brow=26, browup=0.025, mouth="o", extras=("!",))
    finish(H, tl, f0, f1)
    camera(c, [(f0, (0.1, -4.6, 2.2)), (f1, (0.2, -4.4, 2.6))], focus=4.5, fstop=1.0)


# ====================================================================== NÍVEL 5: cinco Everests (52.6 - 55.92)
@shot("n5c2", 52.6, 55.92)
def n5c2(c):
    sc, f0, f1 = c["sc"], c["f0"], c["f1"]
    P = dict(cena.PAL["manha"])
    sc.world.node_tree.nodes["Background"].inputs[0].default_value = (0.01, 0.02, 0.06, 1)
    props.skywall("ceu_pilha", 3.0, [(-10, "#a7d6f7"), (10, "#7ab6ee"), (26, "#4a80d2"), (42, "#2447a0"), (54, "#0f2468"), (66, "#050a24"), (90, "#02040d")], -60, 60, -30, 100)
    for i in range(70):
        rr = random.Random(i)
        cena.disc(f"est{i}", rr.uniform(0.08, 0.2), cena.amat("est_m", "#ffffff", 3.0, 0.9), (rr.uniform(-13, 13), 2.5, rr.uniform(58, 92)))
    E = 10.0
    tons = ["#e8f0fa", "#d3e2f3"]
    for k in range(5):
        props.montanha_cel(f"ever{k}", (-3.0, 0.0, k * E), 5.2, E, k + 1, tons[k % 2])
    props.montanha_cel("ever5", (-3.0, 0.0, 5 * E), 5.2, E * 0.875, "+", "#cfe0f4")
    props.pilha_notas("pilha", 3.0, 5.2, int(58.75 / 0.5), 0.5)
    props.etiqueta("topo_km", "52 km", (3.0, -0.3, 61.6), 1.0, "#ffd24a", 0.8, 1.8)
    props.txt("topo_km_s", "R$ 52 bilhões", 0.6, "#ffffff", (3.0, -0.3, 63.5), None, ink=props.INK, ow=0.08)
    for i in range(22):
        props.poly(f"tr{i}", cena.rect(-5.6 + 0.5 * i, 4 * E + E + 0.0 - 0.06, -5.6 + 0.5 * i + 0.3, 4 * E + E + 0.06), "#ffd24a", -0.02)
    props.etiqueta("lin5", "5 EVEREST", (-3.0, -0.3, 5 * E + 0.9), 1.0, "#e2364b", 0.55, 1.5)
    props.poly("chao_linha", cena.rect(-8, -0.12, 8, 0.0), "#2a3a66", 0.2)
    props.pessoa("voce_ponto", -0.0, 0.0, "#c62f35", 0.05)
    props.txt("voce_txt", "VOCÊ", 0.5, "#ffffff", (0.0, -0.02, 1.6), None, ink=props.INK, ow=0.08)
    props.poly("voce_seta", [(-0.25, 1.15), (0.25, 1.15), (0.0, 0.6)], "#ffffff", -0.01)
    t5 = F(wt(12, "cinco")); t_e = F(wt(12, "Everests"))
    destaque = cena.disc("destaque5", 4.5, cena.amat("destaque5_m", "#ffd24a", 1.0, 0.35, ("radial", 1.2)), (-3.0, -0.2, 4 * E + E / 2))
    props.blink_vis(destaque, [(f0 - 5, False), (t5 - 1, False), (t5, True), (t5 + 12, False)], True)
    camera(c, [(f0, (0.0, -17.0, 7.0)), (F(53.3), (0.0, -17.0, 12.0)), (F(54.5), (0.0, -17.0, 42.0)), (F(55.3), (0.0, -17.0, 49.0)), (f1, (0.0, -17.0, 49.5))], focus=17.0, fstop=3.0, dof=False)


# ====================================================================== execução
def main():
    argv = sys.argv[sys.argv.index("--") + 1:]
    arg = lambda n, d=None: argv[argv.index(n) + 1] if n in argv else d
    if "--list" in argv:
        for k, (a, b, _) in SHOTS.items():
            print(f"{k:6s} {a:6.2f}-{b:6.2f}  quadros {F(a)}-{F(b) - 1}")
        return
    name, out = argv[0], argv[1]
    t0, t1, fn = SHOTS[name]
    k = float(arg("--scale", "1.0"))
    reset(int(1080 * k), int(1920 * k), FPS, int(arg("--samples", "16")))
    sc = lib.scene; f0, f1 = F(t0), F(t1) - 1
    sc.frame_start, sc.frame_end = f0, f1
    c = dict(sc=sc, f0=f0, f1=f1, t0=t0, t1=t1)
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
