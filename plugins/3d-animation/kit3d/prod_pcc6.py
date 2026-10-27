"""PCC v4, cenas dos níveis refeitas com linguagem de cinema (a partir de 8,89 s):
- PROFUNDIDADE: primeiro plano desfocado perto da lente, assunto em foco no meio, fundo afastado com névoa;
- ESCALA ÚNICA: herói, figurantes e objetos no tamanho real (1,75 m); nada de herói gigante;
- PLANOS: cada cena tem 2 ou 3 planos (aberto, close no rosto ou no objeto, por cima do ombro, de baixo, de cima),
  trocados por marcadores nos tempos da fala; entre cenas, corte em movimento (transicao.py).
blender -b -P prod_pcc6.py -- CENA OUT [--scale 1] [--samples 16] [--at t1,t2] [--list]   (a1 e a2 vêm de prod_pcc4.py)"""
import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy, lib
from lib import *
import cena, props, luz, curvas, frente, uniforme as U, grana as G, area, transicao as TR, sets4 as S, trono as T, quadro as Q, adereco as AD
import prod_pcc4 as P4
from prod_pcc4 import cena_, wt, camera_movel, baked_slide, seguro, F, FPS, finish, Timeline, P, _mix
from acting import Actor
from char2d import rrect
from puppet2d import circle, stroke

VAR = {
    "esquina":  dict(mid="#2c3290", low="#171b55", halo="#ffb04a", luz="#ffd9a0"),
    "avenida":  dict(mid="#20267a", low="#12164a", halo="#6f9bff", luz="#cfe0ff"),
    # roteiro de cor (v7): cada lugar numa família diferente, com a luz na cor oposta à da parede para o assunto saltar
    "fundos":   dict(mid="#6a4430", low="#341f15", top="#120a07", chao="#1a0f0a", halo="#ffb35a", luz="#ffdcaa", pedra="#7a5038", aresta="#ffcf9a",
                     borda="#ffc98a"),                                                      # madeira quente: o dinheiro verde salta
    "delegacia": dict(mid="#3e5272", low="#1c2a42", top="#080e18", chao="#0d1522", halo="#ff4a52", luz="#ffd6d0", pedra="#4c6488", aresta="#d6e4ff",
                      borda="#ff8a8a"),                                                     # aço frio com alarme vermelho
    "salao":    dict(mid="#5a2c86", low="#2b1450", top="#0f0620", chao="#12082a", halo="#ffb070", luz="#ffd8b0", pedra="#6a3c9a", aresta="#e0b8ff"),
    "escritorio": dict(mid="#0f4e5a", low="#082d35", top="#03141a", chao="#051114", halo="#ff7b2e", luz="#ffb877", pedra="#125560", aresta="#86ecec",
                       borda="#ff9e5a"),                                                    # petróleo com abajur laranja
    "casa":     dict(mid="#242a80", low="#111550", halo="#ffb04a", luz="#ffd9a0", pedra="#343a98", aresta="#9aa4ff"),
    "celas":    dict(mid="#3c4659", low="#1b2131", top="#07090f", chao="#0b0e16", halo="#ffcf7a", luz="#fff0c8", pedra="#4c5672", aresta="#d2daee",
                     borda="#ffd08a", grade="#05070c"),                                      # cinza frio, uma luz quente só
}
DIRS = {"v": (0, 0, 1), "h": (1, 0, 0)}


def pal(nome):
    return S.var(P, **VAR[nome])


def planos(c, lista, entra=None, sai=None, k=0.32):
    """uma câmera por plano, trocada por marcador no início de cada plano.
    Cada plano diz O QUE tem de aparecer: caixa0 -> caixa1 = (x0, x1, z0, z1, y) no começo e no fim do plano;
    a câmera é calculada (quadro.enquadra) para a caixa caber na área segura do Reels, com 'preenche' de respiro.
    alt0/alt1 = altura da câmera (de cima/de baixo: o shift compensa e a caixa continua centrada).
    chaves = objetos que não podem sair da área segura (conferidos com VERIFICA=1); chaves_fim = só no último quadro."""
    sc = c["sc"]; cams = []
    for i, pl in enumerate(lista):
        lens = pl.get("lens", 35); pre = pl.get("preenche", 0.85)
        p0, s0, d0 = Q.enquadra(pl["caixa0"], lens, pre, pl.get("alt0"))
        p1, s1, d1 = Q.enquadra(pl.get("caixa1", pl["caixa0"]), lens, pre, pl.get("alt1", pl.get("alt0")))
        cam, rig = camera_movel(c, [(pl["t0"], p0, 0.0)], lens=lens, focus=d0, fstop=pl.get("fstop", 1.8))
        cam.name = f"cam_pl{i}"
        cd = cam.data
        if cd.animation_data:
            act = cd.animation_data.action; cd.animation_data_clear()
            if act:
                bpy.data.actions.remove(act)
        fa, fb = F(pl["t0"]), F(pl["t1"])
        for f in range(fa, fb + 1):
            u = (f - fa) / max(1, fb - fa); s_ = curvas.s(pl.get("curva", "easy"), u)
            cam.location = tuple(a + (b - a) * s_ for a, b in zip(p0, p1)); key(cam, "location", f, "LINEAR")
            cd.shift_x = s0[0] + (s1[0] - s0[0]) * s_; cd.shift_y = s0[1] + (s1[1] - s0[1]) * s_
            cd.keyframe_insert("shift_x", frame=f); cd.keyframe_insert("shift_y", frame=f)
            cd.dof.focus_distance = d0 + (d1 - d0) * s_; cd.dof.keyframe_insert("focus_distance", frame=f)
        lib.all_interp(cd, "LINEAR")
        m = sc.timeline_markers.new(f"pl{i}", frame=fa); m.camera = cam
        cams.append((cam, pl, d0, d1))
    sc.camera = cams[0][0]
    if entra:
        cam, pl, d0, d1 = cams[0]; d = k * d0
        if entra == "v":
            d = min(d, max(0.3, cam.location.z - 0.7))
        TR.rampa_inicio(cam, F(pl["t0"]), DIRS[entra], d, 4)
    if sai:
        cam, pl, d0, d1 = cams[-1]
        TR.rampa_fim(cam, F(pl["t1"]), DIRS[sai], k * d1, 4)
    if os.environ.get("VERIFICA"):
        for i, (cam, pl, d0, d1) in enumerate(cams):
            fa, fb = F(pl["t0"]), F(pl["t1"])
            objs = [bpy.data.objects.get(n) for n in pl.get("chaves", [])]
            probs = Q.verifica(sc, cam, objs, [fa + 5, (fa + fb) // 2, fb - 5])
            objs = [bpy.data.objects.get(n) for n in pl.get("chaves_fim", [])]
            probs += Q.verifica(sc, cam, objs, [fb - 5])
            falta = [n for n in pl.get("chaves", []) + pl.get("chaves_fim", []) if bpy.data.objects.get(n) is None]
            print(f"QUADRO plano {i} ({pl['t0']:.2f}-{pl['t1']:.2f}): " + ("ok" if not probs and not falta else f"FORA {probs} SEM-OBJETO {falta}"))
    return cams


def heroi(p, view, x, A, END, y=0.0, name="heroi"):
    """o herói no tamanho real (mesma escala dos figurantes), com a roupa de presidiário"""
    H = U.heroi_preso(name, view, rim=p["borda"])
    w = empty(name + "_inv", None, (x, y, 0)); H.root.parent = w
    tl = Timeline(H, A, END, FPS); tl.stand(A, END, 0.0)
    cena.contact_shadow(H, dict(shadow=_mix(p["chao"], "#000000", 0.4)))
    return H, tl, w


def prof(p, ys=(2.0, 4.5), alfa=0.16):
    """véus de névoa atrás do assunto: cada camada mais distante fica mais apagada"""
    for y in ys:
        S.neblina(p, y, alfa)


# ====================================================================== B1. O ponto (8,89 - 13,56)
@cena_("b1", 8.89, 13.56)
def b1(c):
    A, END = F(8.5), F(13.9)
    p = pal("esquina"); wy = 8.0
    S.fundo(p, wy, z_meio=2.6, x=(-16, 16), z=(-3, 14), escuro=0.1)
    S.cidade(p, wy - 0.4, -8, 9, 0.0, seed=3, lit=0.12, cor=_mix(p["top"], p["mid"], 0.25), hmax=6.5)
    cena.poly_mesh("calcada", [(-16, -30, 0.0), (16, -30, 0.0), (16, 1.6, 0.0), (-16, 1.6, 0.0)], props.FM(_mix(p["chao"], p["pedra"], 0.3)))
    S.bokeh_fundo(p, "bk1", wy - 0.6, -3, 3, 0.5, 4.5, n=16, cor=p["halo"], seed=5)
    prof(p, (2.4, 5.0))
    S.poste(p, "poste", -1.0, 3.2, h=4.2, cor_luz=p["halo"], frames=END, poeira=20, seed=9)
    # estante de 20 maços atrás dele, à direita (4 prateleiras x 5)
    sx, sy, esp, s_ = 0.62, 0.75, 0.21, 1.25
    S.caixa3d(p, "est_fundo", sx, sy + 0.42, 1.18, 1.8, d=0.02, cor=_mix(p["top"], p["mid"], 0.25), tampo=_mix(p["top"], p["mid"], 0.25), aresta=_mix(p["top"], p["mid"], 0.25))
    zs = [0.38, 0.76, 1.14, 1.52]
    for r, z in enumerate(zs):
        S.caixa3d(p, f"prat{r}", sx, sy, 1.18, z, d=0.42, base=z - 0.04, cor=_mix(p["top"], p["pedra"], 0.35), tampo=_mix(p["top"], p["pedra"], 0.6), aresta=p["aresta"])
    escolhidos = []; n = 0
    for r, z in enumerate(zs):
        for i in range(5):
            x = sx - 2 * esp + i * esp; sel = (r == 3 and i < 3)
            o = S.maco_pop(f"m{r}_{i}", (x, sy + 0.2, z), s_, F(9.05 + 0.04 * n), A, desat=0.0 if sel else 0.6, zk=3.0); n += 1
            if sel:
                escolhidos.append((o, (x, sy + 0.2, z)))
    # ele, de frente, com as mãos à frente; os 3 maços (15%) voam da estante para as mãos dele
    H, tl, w = heroi(p, "front", -0.15, A, END)
    t_q = wt(3, "quinze") - 0.05
    for j, (o, pos) in enumerate(escolhidos):
        f0 = F(t_q + 0.14 * j)
        S.arco(o, f0, f0 + 11, pos, (-0.15, -0.16, 0.92 + j * 0.055), alt=0.35)
    tl.face(A, 0.0, lid="esperto", lidv=0.55, brow=-6, mouth="pequena", look=(0.9, 0.2))
    tl.face(F(wt(3, "começo")), 1.0, wide=0.3, brow=8, browup=0.012, mouth="pequena", look=(0.9, 0.3))
    tl.face(F(t_q), 1.0, lid="esperto", lidv=0.5, brow=-14, browtilt=0.02, mouth="sorriso", look=(0.3, -0.5))
    tl.face(F(wt(3, "vende")), 1.0, eye="cifrao", mouth="sorrisao", browup=0.015, extras=("brilho",))
    finish(H, tl, A, END)
    segura = dict(shF=30, elF=-100, wrF=0, shB=30, elB=-100, wrB=0)
    frente.bracos(H, A, END, [(A, dict(shF=5, elF=0, shB=5, elB=0)), (F(t_q) - 12, dict(shF=4, elF=2, shB=4, elB=2)), (F(t_q) - 6, dict(shF=-2, elF=6, shB=-2, elB=6)),
                              (F(t_q) + 4, dict(shF=34, elF=-108, shB=34, elB=-108)), (F(t_q) + 10, segura)],
                  extras=[(F(t_q) + 11, "shF", -6, 2.8, 0.28), (F(t_q) + 11, "shB", -6, 2.8, 0.28)])
    # primeiro plano: o poste da calçada, bem perto da lente (desfocado)
    S.coluna_fg(p, "poste_fg", 0.95, -1.9, w=0.16)
    S.caixa3d(p, "muro1", 0.0, 2.9, 7.0, 2.6, d=0.05, cor=_mix(p["pedra"], p["top"], 0.55), tampo=_mix(p["pedra"], p["top"], 0.4), aresta=_mix(p["pedra"], p["top"], 0.4))
    AD.cartazes(p, "cart1", -2.9, 1.5, 2.88, n=4, seed=2)
    AD.fios(p, "fios1", [(-3.5, 4.2), (-1.0, 4.4), (1.6, 4.1), (4.0, 4.3)], 2.7)
    AD.sacos(p, "saco1", 1.35, 0.6)
    AD.moto(p, "moto1", -1.55, 1.4, s=0.9)
    planos(c, [
        dict(t0=8.89, t1=10.55, caixa0=(-0.6, 1.35, -0.1, 2.0, 0.0), caixa1=(-0.55, 1.3, -0.08, 1.95, 0.0), lens=32, fstop=2.0, preenche=0.82,
             chaves=["heroi_inv", "est_fundo_f"]),
        dict(t0=10.55, t1=12.15, caixa0=(-0.55, 0.8, 0.72, 1.75, 0.3), caixa1=(-0.5, 0.6, 0.75, 1.65, 0.1), lens=40, fstop=2.2,
             chaves=["m3_0", "m3_1", "m3_2"]),
        dict(t0=12.15, t1=13.56, caixa0=(-0.5, 0.2, 0.95, 1.88, 0.0), caixa1=(-0.45, 0.15, 1.02, 1.85, 0.0), lens=50, fstop=1.6),
    ], entra="h", sai="h")


# ====================================================================== B2. A polícia chega (13,56 - 16,61)
def hidrante(p, name, x, y, s=1.0):
    root = empty(name, None, (x, y, 0)); root.scale = (s, s, s)
    cor = "#b5322f"
    props.inked(name + "_c", rrect(-0.13, 0.0, 0.13, 0.55, 0.05, 4), cor, root, w=0.0, rim=0.015, rim_color=p["borda"])
    props.inked(name + "_t", circle(0, 0.58, 0.11, 20), cor, root, w=0.0)
    props.poly(name + "_l", cena.rect(-0.22, 0.3, 0.22, 0.38), _mix(cor, "#000000", 0.3), -0.002, root)
    return root


@cena_("b2", 13.56, 16.61)
def b2(c):
    A, END = F(13.2), F(17.0)
    p = pal("avenida"); wy = 10.0
    S.fundo(p, wy, z_meio=2.8, x=(-20, 20), z=(-3, 14), escuro=0.15)
    S.cidade(p, wy - 0.4, -10, 11, 0.0, seed=7, lit=0.12, cor=_mix(p["top"], p["mid"], 0.25), hmax=7.0)
    cena.poly_mesh("asfalto", [(-20, -30, 0.0), (20, -30, 0.0), (20, 6.0, 0.0), (-20, 6.0, 0.0)], props.FM(_mix(p["chao"], p["mid"], 0.22)))
    for k in range(-9, 10):
        cena.poly_mesh(f"faixa{k}", [(k * 1.8, 3.4, 0.003), (k * 1.8 + 0.9, 3.4, 0.003), (k * 1.8 + 0.9, 3.55, 0.003), (k * 1.8, 3.55, 0.003)], props.FM(_mix(p["aresta"], p["chao"], 0.35)))
    prof(p, (2.0, 6.5))
    S.poste(p, "poste2", -1.6, 5.0, h=4.6, cor_luz=p["luz"], frames=END, poeira=10, seed=4)
    # a viatura (tamanho real) chega pelo fundo, atrás dele, e freia
    vt, vr, vb = S.viatura(p, "vtr", 6.5, 3.0, s=1.0, flip=-1)
    f_a, f_b = F(wt(4, "rua")) - 10, F(15.1)
    vt.location.x = 6.5; key(vt, "location", f_a - 1, "CONSTANT")
    for f in range(f_a, f_b + 1):
        u = (f - f_a) / (f_b - f_a); vt.location.x = 6.5 - 5.3 * curvas.s("easy", u) ** 0.8; key(vt, "location", f, "LINEAR")
    S.pisca_sirene(vr, vb, f_a, END, per=8)
    S.luz_cor("lvm", "#ff3b4a", 0.5, -0.4, 1.5, 2.2, f_a + 6, END, per=16, fase=0, alfa=0.24)
    S.luz_cor("lvb", "#3d7bff", 0.5, -0.4, 1.5, 2.2, f_a + 6, END, per=16, fase=8, alfa=0.24)
    H, tl, w = heroi(p, "q", -0.3, A, END); a = Actor(tl, 0.0)
    tl.intent(A, head=-4, torso=0)
    tl.face(A, 0.0, lid="esperto", lidv=0.55, brow=-6, mouth="reta", look=(0.8, 0.1))
    tl.face(F(wt(4, "polícia")), 1.0, eye="ponto", brow=26, browup=0.025, mouth="o", extras=("!",), look=(0.9, 0.1))
    tl.face(F(wt(4, "chega")) + 4, 1.0, wide=0.6, brow=20, browup=0.02, mouth="nervosa", look=(0.9, 0.1), extras=("suor",))
    a.take(F(wt(4, "polícia")) + 2, back=-0.18)
    finish(H, tl, A, END)
    hidrante(p, "hid", 0.85, -1.6)                                                   # primeiro plano, desfocado
    AD.semaforo(p, "sem2", 2.2, 1.6, h=3.0)
    S.bokeh_fundo(p, "bk2", 8.5, -4, 5, 0.2, 1.2, n=10, cor="#ffd9a0", seed=12, r=(0.05, 0.12), alfa=0.5)
    planos(c, [
        dict(t0=13.56, t1=15.2, caixa0=(-0.85, 1.75, 0.0, 2.2, 0.6), caixa1=(-0.8, 1.7, 0.0, 2.15, 0.6), lens=30, fstop=2.0,
             chaves=["heroi_inv"], chaves_fim=["vtr"]),
        dict(t0=15.2, t1=16.61, caixa0=(-0.85, -0.1, 1.05, 1.92, 0.0), caixa1=(-0.8, -0.15, 1.1, 1.9, 0.0), lens=50, fstop=1.6),
    ], entra="h", sai="h")


# ====================================================================== B3. O gerente (16,61 - 22,53)
@cena_("b3", 16.61, 22.53)
def b3(c):
    A, END = F(16.2), F(22.9)
    p = pal("fundos"); wy = 4.5
    S.fundo(p, wy, z_meio=2.0, x=(-10, 10), z=(-3, 10), escuro=0.05)
    # fundo: estante de caixas e a persiana com luz (longe e com névoa)
    for r in range(4):
        for i in range(6):
            x = -2.4 + i * 0.95; z = 0.3 + r * 0.75
            props.poly(f"cx{r}_{i}", rrect(x - 0.38, z, x + 0.38, z + 0.55, 0.03, 3), _mix(p["pedra"], p["top"], 0.45 + 0.1 * ((r + i) % 2)), wy - 0.3)
    for i in range(7):
        props.poly(f"slat{i}", cena.rect(1.2, 1.2 + i * 0.32, 2.6, 1.2 + i * 0.32 + 0.15), _mix(p["luz"], p["mid"], 0.55), wy - 0.35, strength=1.0)
    prof(p, (1.4, 3.2))
    luz.feixe("feixe_mesa", 0.0, 0.7, 0.78, 4.6, 1.3, 0.22, p["luz"], forca=1.2, frames=END, poeira=40, seed=31)
    S.caixa3d(p, "mesa", 0.0, -0.3, 1.9, 0.78, d=0.85, cor=_mix(p["top"], p["pedra"], 0.3), tampo=_mix(p["top"], p["pedra"], 0.55))
    for x in (-0.6, 0.6):
        props.poly(f"gaveta{x}", rrect(x - 0.28, 0.35, x + 0.28, 0.62, 0.02, 3), _mix(p["top"], p["pedra"], 0.4), -0.302)
    # dinheiro: pilha de 20 maços (a de cima = 5%) e, em "faturar", o bloco de 70 maços (R$ 700 mil)
    pilha, _ = G.bloco("pilha20", (0.55, -0.15, 0.78), 1, 1, 20, s=1.6, zk=1.5)
    t_p = wt(5, "5%")
    G.cresce_bloco(pilha, F(t_p - 0.7), F(t_p - 0.3))
    props.blink_vis(pilha, [(A, True), (F(wt(5, "faturar")) - 2, True), (F(wt(5, "faturar")) - 1, False)], True)
    topo = G.maco("topo20", (0.55, -0.11, 0.78 + 19 * G.T * 1.6 * 1.5), n=1, s=1.6, zk=1.5)
    props.blink_vis(topo, [(A, False), (F(t_p - 0.1), True)], True)
    S.arco(topo, F(t_p) + 2, F(t_p) + 14, (0.55, -0.11, 0.78 + 19 * G.T * 2.4), (0.05, -0.12, 0.84), alt=0.18)
    props.blink_vis(topo, [(F(wt(5, "faturar")) - 1, False)], True)
    bloco, _ = G.bloco("bloco70", (0.0, -0.2, 0.78), 7, 2, 5, s=1.35, zk=3.0)
    G.cresce_bloco(bloco, F(wt(5, "faturar")), F(wt(5, "faturar")) + 12)
    props.blink_vis(bloco, [(A, False), (F(wt(5, "faturar")) - 1, False), (F(wt(5, "faturar")), True)], True)
    # ele, sentado de frente atrás da mesa
    H, tl, w = heroi(p, "front", -0.05, A, END, y=0.3)
    tl.face(A, 0.0, lid="esperto", lidv=0.55, brow=-8, mouth="reta", look=(0.6, -0.2))
    tl.face(F(wt(5, "gerente")), 1.0, lid="esperto", lidv=0.5, brow=-12, browtilt=0.018, mouth="sorriso", look=(0.0, 0.0))
    tl.face(F(t_p), 1.0, wide=0.2, brow=6, mouth="lado", look=(0.9, -0.4))
    tl.face(F(wt(5, "faturar")), 1.0, eye="cifrao", mouth="sorrisao", browup=0.015, extras=("brilho",))
    finish(H, tl, A, END)
    frente.sentado(H, A, END)
    frente.bracos(H, A, END, [(A, dict(shF=14, elF=-60, shB=14, elB=-60)), (F(t_p) + 6, dict(shF=14, elF=-60, shB=14, elB=-60)),
                              (F(t_p) + 12, dict(shF=30, elF=-96, wrF=-6, shB=14, elB=-60)), (F(t_p) + 40, dict(shF=22, elF=-80, shB=16, elB=-64))],
                  extras=[(F(t_p) + 14, "shF", -5, 2.8, 0.3)])
    S.planta(p, "planta3", -0.95, -1.7, s=1.1)                                       # primeiro plano
    AD.relogio(p, "rel3", -1.25, 2.85, 4.15)
    AD.calendario(p, "cal3", -1.95, 2.05, 4.15)
    AD.telefone(p, "tel3", -0.62, -0.12, 0.78)
    AD.papeis(p, "pap3", -0.3, -0.13, 0.78)
    planos(c, [
        dict(t0=16.61, t1=17.45, caixa0=(-1.1, 1.1, 0.2, 1.75, -0.3), caixa1=(-1.05, 1.05, 0.25, 1.7, -0.3), lens=35, fstop=2.0,
             chaves=["pilha20", "mesa_f"]),
        dict(t0=17.45, t1=19.65, caixa0=(-0.3, 0.9, 0.7, 1.6, -0.1), caixa1=(-0.25, 0.85, 0.72, 1.55, -0.1), lens=40, fstop=2.2,
             chaves=["pilha20"]),
        dict(t0=19.65, t1=22.53, caixa0=(-0.95, 0.95, 0.55, 1.75, -0.1), caixa1=(-0.9, 0.9, 0.6, 1.7, -0.1), alt0=2.3, alt1=2.6, lens=32, fstop=2.4,
             chaves_fim=["bloco70"]),
    ], entra="h", sai="h")


# ====================================================================== B4. O policial cobra (22,53 - 28,62)
@cena_("b4", 22.53, 28.62)
def b4(c):
    A, END = F(22.1), F(29.0)
    p = pal("delegacia"); wy = 3.6
    S.fundo(p, wy, z_meio=2.2, x=(-12, 12), z=(-3, 10), escuro=0.05)
    props.poly("porta", rrect(1.45, 0.0, 2.15, 2.1, 0.04, 3), _mix(p["top"], "#000000", 0.2), wy - 0.05)
    cena.disc("lamp_porta", 0.6, cena.amat("lamp_porta_m", p["luz"], 1.0, 0.5, ("radial", 1.4)), (1.8, wy - 0.1, 2.5))
    # o painel das 42 fichas na parede (7 x 6), que acende em "42"
    fx0, fz0, dx, dz = -0.95, 0.75, 0.31, 0.4
    for k in range(42):
        r, i = divmod(k, 7)
        f_ = empty(f"fi{k}", None, (fx0 + i * dx, wy - 0.08, fz0 + (5 - r) * dz))
        props.poly(f"fi{k}_c", rrect(-0.13, -0.17, 0.13, 0.17, 0.02, 3), "#ece2cc", 0.0, f_)                 # ficha de papel creme: salta da parede fria
        props.poly(f"fi{k}_h", circle(0, 0.06, 0.055, 12), "#1c2130", -0.002, f_)
        props.poly(f"fi{k}_b", rrect(-0.09, -0.15, 0.09, 0.0, 0.035, 3), "#2c3448", -0.002, f_)
        props.poly(f"fi{k}_bo", cena.rect(-0.11, -0.165, 0.11, -0.13), "#d8343c", -0.003, f_)   # faixa vermelha de condenado
        fa, fb = F(24.9) + 2, F(wt(6, "42")) + 10                                        # as fichas enchem o painel desde o começo do plano até o "42"
        P4.surge(f_, fa + round((fb - fa) * k / 41), 4, de=0.6)
    gr = props.grade("grade_fichas", -1.15, 1.15, 0.0, 2.55, wy - 0.15, p["grade"], n=9, w=0.045, rails=0)
    for z in (0.0, 2.45):
        props.poly(f"gf_t{z}", cena.rect(-1.15, z, 1.15, z + 0.1), p["grade"], -0.001, gr)
    f_c = F(wt(6, "condenados"))
    gr.location = (0.0, wy - 0.15, 0.55 + 3.2); key(gr, "location", f_c - 1, "CONSTANT")
    for f in range(f_c, f_c + 8):
        u = (f - f_c) / 7; gr.location.z = 0.55 + 3.2 * (1 - curvas.s("queda", u)); key(gr, "location", f, "LINEAR")
    prof(p, (2.4,))
    # o PM de costas em primeiro plano (grande, desfocado) e o herói à frente dele, entregando o envelope
    S.pm(p, "pm", 0.45, -1.4, h=1.0, flip=-1, cor="#121827")
    H, tl, w = heroi(p, "front", -0.2, A, END, y=0.2)
    tl.face(A, 0.0, lid="esperto", lidv=0.5, brow=-4, mouth="pequena", look=(0.6, 0.0))
    tl.face(F(wt(6, "cobra")), 1.0, lid="triste", lidv=0.3, brow=14, mouth="nervosa", look=(0.7, -0.1), extras=("suor",))
    tl.face(F(wt(6, "viu")), 1.0, lid="esperto", lidv=0.5, brow=-8, mouth="lado", look=(0.3, 0.1))
    finish(H, tl, A, END)
    fc = F(wt(6, "cobra"))
    frente.bracos(H, A, END, [(A, dict(shF=5, elF=0, shB=5, elB=0)), (fc - 6, dict(shF=4, elF=4, shB=5, elB=0)), (fc + 6, dict(shF=48, elF=-70, wrF=-12, shB=5, elB=0)),
                              (fc + 22, dict(shF=48, elF=-70, wrF=-12, shB=5, elB=0)), (fc + 34, dict(shF=6, elF=-4, shB=5, elB=0))])
    env = empty("env", None, (0.0, 0.05, 1.12))
    props.inked("env_f", rrect(-0.1, -0.065, 0.1, 0.065, 0.01, 2), "#f4efe6", env, w=0.0, rim=0.006, rim_color="#ffffff")
    props.poly("env_v", [(-0.1, 0.065), (0.0, 0.0), (0.1, 0.065)], "#cfc8bb", -0.002, env)
    props.poly("env_g", cena.rect(0.05, -0.065, 0.1, -0.02), "#4c9a62", -0.003, env, strength=1.1)
    fa, fb = fc + 8, F(wt(6, "fingir")) + 4
    S.mostra(env, [(fa, fb + 3)])
    S.arco(env, fa, fb, (0.05, 0.05, 1.12), (0.3, -1.25, 1.35), alt=0.15)
    S.mostra(w, [(A, F(24.9))]); S.mostra(bpy.data.objects["pm"], [(A, F(24.9))])     # no plano do painel, só as fichas
    AD.quadro_avisos(p, "qa4", -2.1, 1.6, 3.54)
    AD.banco(p, "banco4", 2.3, 3.0)
    AD.bandeira(p, "band4", -2.8, 3.2)
    planos(c, [
        dict(t0=22.53, t1=24.9, caixa0=(-0.75, 0.9, -0.1, 2.0, 0.2), caixa1=(-0.7, 0.85, -0.08, 1.95, 0.2), lens=35, fstop=1.8, preenche=0.8,
             chaves=["heroi_inv"]),
        dict(t0=24.9, t1=28.62, caixa0=(-1.55, 1.5, 0.2, 3.5, 3.5), caixa1=(-1.25, 1.2, 0.45, 3.25, 3.5), lens=35, fstop=2.4,
             chaves_fim=["fi0", "fi6", "fi35", "fi41", "grade_fichas"]),
    ], entra="h", sai="h")


# ====================================================================== B5. O membro paga (28,62 - 33,68)
@cena_("b5", 28.62, 33.68)
def b5(c):
    A, END = F(28.2), F(34.0)
    p = pal("salao"); wy = 4.5
    S.fundo(p, wy, z_meio=2.2, x=(-10, 10), z=(-3, 10))
    emb = empty("embl", None, (0.6, wy - 0.05, 2.0))
    for k, (r, cor) in enumerate(((1.2, _mix(p["mid"], p["halo"], 0.2)), (0.95, _mix(p["mid"], p["top"], 0.4)), (0.68, _mix(p["mid"], p["halo"], 0.35)), (0.36, _mix(p["mid"], p["top"], 0.5)))):
        props.poly(f"embl{k}", circle(0, 0, r, 40), cor, -0.001 * k, emb)
    cena.disc("halo_embl", 2.8, cena.amat("halo_embl_m", p["halo"], 1.0, 0.35, ("radial", 1.5)), (0.6, wy - 0.1, 2.0))
    prof(p, (1.6, 3.4))
    luz.feixe("feixe_caixa", 0.35, 0.3, 0.0, 4.4, 1.2, 0.25, p["luz"], forca=1.2, frames=END, poeira=30, seed=12)
    S.caixa3d(p, "caixa", 0.35, -0.4, 0.62, 1.0, d=0.55, cor=_mix(p["top"], p["pedra"], 0.4), tampo=_mix(p["top"], p["pedra"], 0.65))
    props.poly("fenda2", rrect(-0.24, -0.01, 0.24, 0.08, 0.02, 3), p["halo"], 0.0, empty("fenda_r2", None, (0.35, -0.4015, 0.8)))
    props.poly("fenda", rrect(-0.22, 0.0, 0.22, 0.06, 0.02, 3), "#05030f", 0.0, empty("fenda_r", None, (0.35, -0.402, 0.81)))
    H, tl, w = heroi(p, "q", -0.4, A, END, y=0.15); a = Actor(tl, 0.0)
    tl.intent(A, head=-2, torso=0)
    tl.face(A, 0.0, lid="esperto", lidv=0.55, brow=-6, mouth="sorriso", look=(0.9, 0.1))
    tl.face(F(wt(7, "agora")), 1.0, wide=0.2, brow=6, mouth="pequena", look=(0.9, -0.1))
    tl.face(F(wt(7, "paga")), 1.0, lid="triste", lidv=0.35, brow=14, mouth="nervosa", look=(0.9, -0.3))
    tl.face(F(32.4), 1.0, lid="sono", lidv=0.7, brow=18, mouth="triste", extras=("sombra",), look=(0.6, -0.5))
    tl.intent(F(wt(7, "paga")) - 6, shF=10, elF=60); tl.intent(F(wt(7, "paga")), shF=55, elF=40, wrF=10)
    tl.intent(F(32.2), shF=10, elF=70)
    a.slump(F(32.3), frames=16)
    finish(H, tl, A, END)
    for i in range(5):                                                               # as notas entram na fenda, uma a uma
        n = G.nota(f"nota_pg{i}", (0.0, 0.0, 0.0), 1.8)
        f0 = F(wt(7, "paga") + 0.1 + 0.42 * i)
        n.scale = (0.0001,) * 3; key(n, "scale", f0 - 1, "CONSTANT")
        n.scale = (1, 1, 1); key(n, "scale", f0, "CONSTANT")
        S.arco(n, f0, f0 + 9, (-0.1, -0.35, 1.05), (0.35, -0.44, 0.9), alt=0.25)
        for f in range(f0 + 9, f0 + 14):
            u = (f - (f0 + 9)) / 4; n.scale = (1, 1, max(0.0001, 1 - u)); key(n, "scale", f, "LINEAR")
        n.scale = (0.0001,) * 3; key(n, "scale", f0 + 15, "CONSTANT")
    S.planta(p, "planta5", -1.0, -1.7, s=1.2)
    AD.vela(p, "vela5a", 1.15, 0.6, frames=END)
    AD.vela(p, "vela5b", -1.25, 0.9, frames=END)
    AD.cortina(p, "cort5e", -2.6, 4.3, lado=1)
    AD.cortina(p, "cort5d", 2.6, 4.3, lado=-1)
    planos(c, [
        dict(t0=28.62, t1=30.4, caixa0=(-0.8, 0.8, -0.1, 2.0, -0.2), caixa1=(-0.75, 0.75, -0.08, 1.95, -0.2), lens=32, fstop=2.0,
             chaves=["heroi_inv", "caixa_f"]),
        dict(t0=30.4, t1=32.45, caixa0=(-0.35, 0.75, 0.6, 1.35, -0.4), caixa1=(-0.3, 0.7, 0.62, 1.3, -0.4), lens=45, fstop=2.0,
             chaves=["fenda_r"]),
        dict(t0=32.45, t1=33.68, caixa0=(-0.72, -0.02, 1.0, 1.9, 0.15), caixa1=(-0.7, -0.05, 1.05, 1.88, 0.15), lens=50, fstop=1.6),
    ], entra="h", sai="h")


# ====================================================================== B6. O tribunal do crime (33,68 - 38,45)
@cena_("b6", 33.68, 38.45)
def b6(c):
    A, END = F(33.3), F(38.8)
    p = S.var(P, **T.PALETAS["vinho"]); wy = 4.6
    S.fundo(p, wy, z_meio=2.4, x=(-10, 10), z=(-3, 10))
    luz.feixe("feixe_trib", 0.0, 1.6, 0.0, 6.0, 1.9, 0.35, p["luz"], forca=1.3, frames=END, poeira=50, seed=44)
    cena.disc("halo_trib", 3.0, cena.amat("halo_trib_m", p["halo"], 1.0, 0.38, ("radial", 1.5)), (0.0, wy - 0.1, 1.8))
    for i, x in enumerate((-0.7, 0.0, 0.7)):
        S.pm(p, f"juiz{i}", x, 1.6, h=1.0, flip=1, cor=_mix(p["mid"], "#000000", 0.55), rim=p["borda"])
    S.caixa3d(p, "mesa_t", 0.0, 1.25, 2.4, 0.95, d=0.55, cor=_mix(p["top"], p["mid"], 0.5), tampo=_mix(p["top"], p["aresta"], 0.3))
    pv, bloco = props.martelo("martelo", (0.8, 1.15, 1.04), 0.8)
    tt = F(wt(8, "tribunal"))
    for ff, a_ in ((A, -50), (tt - 8, -64), (tt - 2, -64), (tt, 0), (tt + 3, -9), (tt + 6, 0), (tt + 40, 0)):
        pv.rotation_euler = (0, math.radians(a_), 0); key(pv, "rotation_euler", ff, "BEZIER" if ff != tt else "LINEAR")
    cor_f = ["#c8343c", "#e0484f", "#ff5a5a"]; comps = [0.7, 1.15, 1.6]
    for i, (x, cp, nome) in enumerate(zip((-1.0, 0.0, 1.0), comps, ("surra", "braço", "morte"))):
        ban = empty(f"ban{i}", None, (x, wy - 0.15, 4.4))
        props.poly(f"ban{i}_f", [(-0.25, 0.0), (0.25, 0.0), (0.25, -cp), (0.0, -cp - 0.12), (-0.25, -cp)], cor_f[i], 0.0, ban, strength=1.05)
        ic = empty(f"ban{i}_ic", ban, (0, -0.002, -cp + 0.15))
        if i == 0:
            props.poly(f"ban{i}_ic1", circle(0, 0, 0.09, 12), "#ffffff", 0.0, ic)
        elif i == 1:
            props.poly(f"ban{i}_ic1", [(-0.07, 0.12), (0.03, 0.12), (-0.01, 0.01), (0.08, 0.01), (-0.06, -0.14), (-0.02, -0.02), (-0.1, -0.02)], "#ffffff", 0.0, ic)
        else:
            cv = props.caveira(f"ban{i}_cv", (0, -0.003, 0.0), 0.18); cv.parent = ic
        ts = wt(8, nome)
        ban.location.z = 6.0; key(ban, "location", F(ts) - 1, "CONSTANT")
        for f in range(F(ts), F(ts) + 10):
            u = (f - F(ts)) / 9; ban.location.z = 6.0 + (4.1 - 6.0) * curvas.s("queda", u); key(ban, "location", f, "LINEAR")
    prof(p, (2.4,))
    # contraplano: no primeiro plano ele de costas (plano 1); depois de frente, em close, com os juízes atrás (plano 2)
    f_troca = F(wt(8, "pune")) - 2
    Hc, tlc, wc = heroi(p, "back", 0.0, A, END, y=-0.6, name="heroi_costas")
    tlc.intent(A, head=10, torso=3)
    tlc.bake()                                                   # de costas: sem rosto (sem piscar)
    S.mostra(wc, [(A, f_troca)])
    H, tl, w = heroi(p, "front", 0.0, A, END, y=-0.6)
    tl.face(A, 0.0, lid="triste", lidv=0.3, brow=12, mouth="nervosa", look=(0.0, -0.4), extras=("suor",))
    tl.face(F(wt(8, "surra")), 1.0, wide=0.5, brow=20, browup=0.02, mouth="grito", look=(0.0, 0.0), extras=("suor", "!"))
    tl.face(F(wt(8, "morte")), 1.0, eye="ponto", brow=26, browup=0.025, mouth="o", extras=("suor", "!"))
    tl.intent(A, head=10, torso=4)
    finish(H, tl, A, END)
    frente.bracos(H, A, END, [(A, dict(shF=4, elF=-10, shB=4, elB=-10)), (F(wt(8, "surra")), dict(shF=4, elF=-10, shB=4, elB=-10)), (F(wt(8, "surra")) + 8, dict(shF=20, elF=-60, shB=20, elB=-60))])
    S.mostra(w, [(f_troca, END + 5)])
    for x in (-0.7, 0.0, 0.7):
        props.poly(f"cad6{x}", rrect(x - 0.28, 0.0, x + 0.28, 2.15, 0.08, 4), _mix(p["top"], "#000000", 0.3), 1.85)
    AD.cortina(p, "cort6e", -2.4, 4.4, lado=1, cor=_mix(p["mid"], "#000000", 0.5))
    AD.cortina(p, "cort6d", 2.4, 4.4, lado=-1, cor=_mix(p["mid"], "#000000", 0.5))
    planos(c, [
        dict(t0=33.68, t1=wt(8, "pune") - 0.08, caixa0=(-1.4, 1.4, 0.0, 2.6, 1.0), caixa1=(-1.3, 1.3, 0.05, 2.5, 1.0), alt0=0.9, alt1=0.85, lens=30, fstop=2.8,
             chaves=["juiz0", "juiz2"]),
        dict(t0=wt(8, "pune") - 0.08, t1=38.45, caixa0=(-0.42, 0.42, 1.0, 1.95, -0.6), caixa1=(-0.4, 0.4, 1.05, 1.92, -0.6), lens=50, fstop=1.6),
    ], entra="h", sai="h")


# ====================================================================== B7. Chefe de setor: o dinheiro passa pela mão (38,45 - 42,33)
@cena_("b7", 38.45, 42.33)
def b7(c):
    A, END = F(38.0), F(42.7)
    p = pal("escritorio"); wy = 4.0
    S.fundo(p, wy, z_meio=2.2, x=(-10, 10), z=(-3, 10))
    props.poly("jan_m", cena.rect(-2.2, 0.85, 2.2, 3.9), p["grade"], wy - 0.02)
    props.poly("jan_c", cena.rect(-2.1, 0.95, 2.1, 3.8), _mix(p["halo"], p["mid"], 0.45), wy - 0.04, strength=1.1)
    props.poly("jan_c2", cena.rect(-2.1, 0.95, 2.1, 1.8), _mix(p["halo"], p["mid"], 0.2), wy - 0.045, strength=1.1)
    S.cidade(p, wy - 0.1, -2.1, 2.1, 0.95, seed=14, lit=0.25, cor=_mix(p["top"], p["mid"], 0.1), luzc=p["luz"], hmax=2.3)
    for x in (-0.7, 0.7):
        props.poly(f"jan_div{x}", cena.rect(x - 0.03, 0.85, x + 0.03, 3.9), p["grade"], wy - 0.12)
    S.bokeh_fundo(p, "bk7", wy - 0.2, -2, 2, 1.0, 3.6, n=12, cor=p["luz"], seed=8)
    prof(p, (2.2,))
    luz.feixe("feixe_esc", 0.0, 0.6, 0.78, 5.0, 1.5, 0.3, p["luz"], forca=1.0, frames=END, poeira=30, seed=51)
    S.caixa3d(p, "mesa_e", 0.0, -0.32, 1.9, 0.78, d=0.9, cor=_mix(p["top"], p["pedra"], 0.35), tampo=_mix(p["top"], p["pedra"], 0.6))
    # dois montes de maços sobre a mesa; as notas voam de um para o outro pelas mãos dele (contando, sem parar)
    mE, _ = G.bloco("monteE", (-0.62, -0.25, 0.78), 2, 2, 6, s=1.3, zk=3.0)
    mD, _ = G.bloco("monteD", (0.62, -0.25, 0.78), 2, 2, 3, s=1.3, zk=3.0)
    G.cresce_bloco(mD, F(wt(9, "dinheiro")), END)
    H, tl, w = heroi(p, "front", 0.0, A, END, y=0.3)
    tl.face(A, 0.0, lid="esperto", lidv=0.5, brow=-10, mouth="reta", look=(0.0, -0.3))
    tl.face(F(wt(9, "setor")), 1.0, lid="esperto", lidv=0.5, brow=-14, browtilt=0.02, mouth="sorriso", look=(0.0, 0.0))
    tl.face(F(wt(9, "muito")), 1.0, lid="esperto", lidv=0.45, brow=-10, mouth="sorriso", look=(-0.5, -0.6))
    tl.face(F(wt(9, "passa")), 1.0, eye="cifrao", mouth="sorrisao", browup=0.015, extras=("brilho",), look=(0.5, -0.6))
    finish(H, tl, A, END)
    frente.sentado(H, A, END)
    # mãos: contando em ritmo (a esquerda pega, a direita solta), com a curva contínua
    ks = [(A, dict(shF=16, elF=-70, shB=16, elB=-70))]
    f = F(wt(9, "muito")) - 4; k = 0
    while f < END:
        ks.append((f, dict(shF=24 + 6 * (k % 2), elF=-96 + 8 * (k % 2), wrF=-6, shB=26 - 6 * (k % 2), elB=-100 + 8 * ((k + 1) % 2), wrB=-6))); f += 5; k += 1
    frente.bracos(H, A, END, ks)
    f = F(wt(9, "muito")); i = 0
    while f < END - 6:                                                               # uma nota a cada 3 quadros, em arco
        n = G.nota(f"cn{i}", (0, 0, 0), 1.6)
        S.mostra(n, [(f, f + 9)])
        S.arco(n, f, f + 8, (-0.45, -0.08, 0.95), (0.45, -0.08, 0.95), alt=0.3, curva="easy")
        f += 3; i += 1
    S.planta(p, "planta7", 1.05, -1.6, s=1.2)
    AD.luminaria_mesa(p, "lum7", 0.85, -0.05, 0.78)
    AD.papeis(p, "pap7", -0.15, -0.15, 0.78, n=2)
    planos(c, [
        dict(t0=38.45, t1=wt(9, "muito") - 0.1, caixa0=(-1.2, 1.2, 0.3, 3.0, 0.0), caixa1=(-1.0, 1.0, 0.4, 1.8, 0.0), alt0=2.6, alt1=1.5, lens=32, fstop=2.0,
             chaves_fim=["monteE", "monteD"]),
        dict(t0=wt(9, "muito") - 0.1, t1=42.33, caixa0=(-0.85, 0.85, 0.6, 1.75, -0.2), caixa1=(-0.8, 0.8, 0.62, 1.7, -0.2), lens=45, fstop=2.0,
             chaves=["monteE", "monteD"]),
    ], entra="h", sai="h")


# ====================================================================== B8. O tesoureiro e a inveja (42,33 - 48,43)
@cena_("b8", 42.33, 48.43)
def b8(c):
    A, END = F(41.9), F(48.8)
    p = pal("casa"); wy = 6.0
    S.fundo(p, wy, z_meio=2.2, x=(-14, 14), z=(-3, 12), escuro=0.12)
    S.cidade(p, wy - 0.3, -9, 10, 0.0, seed=21, lit=0.05, cor=_mix(p["top"], p["mid"], 0.1), hmax=4.5)
    cena.poly_mesh("calcada8", [(-14, -30, 0.0), (14, -30, 0.0), (14, 1.2, 0.0), (-14, 1.2, 0.0)], props.FM(_mix(p["chao"], p["pedra"], 0.25)))
    def casa(nome, x, wcasa, h, cor, yy):
        props.poly(nome + "_p", cena.rect(x - wcasa / 2, 0.0, x + wcasa / 2, h), cor, yy)
        props.poly(nome + "_t", [(x - wcasa / 2 - 0.15, h), (x + wcasa / 2 + 0.15, h), (x, h + 0.9)], _mix(cor, "#000000", 0.35), yy - 0.01)
    casa("cE", -2.3, 2.0, 2.6, _mix(p["pedra"], p["top"], 0.4), 2.2)
    casa("cD", 2.4, 2.0, 2.6, _mix(p["pedra"], p["top"], 0.4), 2.2)
    casa("cC", 0.15, 2.0, 2.8, _mix(p["pedra"], p["mid"], 0.1), 1.6)
    props.poly("porta8", rrect(0.25, 0.0, 0.85, 1.95, 0.03, 3), _mix(p["top"], "#000000", 0.2), 1.55)
    props.poly("jan_c8", cena.rect(-0.65, 1.1, -0.1, 1.85), _mix(p["halo"], p["mid"], 0.2), 1.55, strength=1.1)
    cena.disc("lamp_casa", 0.9, cena.amat("lamp_casa_m", p["halo"], 1.0, 0.55, ("radial", 1.4)), (0.55, 1.5, 2.1))
    prof(p, (3.0,))
    # janelas dos vizinhos com olhos acendendo (inveja)
    pos = [(-2.75, 1.7), (-1.85, 1.6), (2.0, 1.65), (2.85, 1.7), (-2.3, 0.8), (2.4, 0.85)]
    for i, (x, z) in enumerate(pos):
        props.poly(f"vj{i}", cena.rect(x - 0.24, z - 0.22, x + 0.24, z + 0.26), "#04051a", 2.15)
        ol = S.olhos(f"ol{i}", x, z, 2.14, s=1.1)
        ti = wt(10, "inveja") + 0.16 * i
        props.blink_vis(ol, [(A, False), (F(ti) - 1, False), (F(ti), True), (F(ti) + 6, False), (F(ti) + 8, True), (F(wt(10, "fuzilado")) + 2, False)], True)
    # o tesoureiro anda até a porta; a mira o encontra em "fuzilado"
    ts = props.pessoa("tes", -1.0, 0.6, "#1a2060", 1.0, flip=-1, rim=p["borda"])
    props.inked("pasta", rrect(0.0, -0.08, 0.16, 0.0, 0.01, 2), "#7a4a2a", ts, loc=(0.24, -0.003, 0.74), w=0.0, rim=0.006, rim_color="#ffc88a")
    f_ini, f_fim = F(wt(10, "tesoureiro")), F(wt(10, "fuzilado"))
    for f in range(f_ini, f_fim + 1):
        u = (f - f_ini) / (f_fim - f_ini); ts.location.x = -1.0 + 1.5 * curvas.s("easy", u); ts.location.z = 0.025 * abs(math.sin((f - f_ini) * 0.55)); key(ts, "location", f, "LINEAR")
    f_m = F(wt(10, "fuzilado"))
    mr = S.mira("mira", (1.0, 0.2, 2.8), 0.8)
    for f in range(f_m - 8, f_m + 1):
        u = (f - (f_m - 8)) / 8; s_ = curvas.s("queda", u)
        mr.location = (1.0 + (0.5 - 1.0) * s_, 0.2, 2.8 + (1.3 - 2.8) * s_); key(mr, "location", f, "LINEAR")
        v = 1.4 - 0.6 * s_; mr.scale = (v, v, v); key(mr, "scale", f, "LINEAR")
    S.mostra(mr, [(f_m - 8, f_m + 3)])
    fl = cena.disc("flash8", 0.5, cena.amat("flash8_m", "#ffffff", 3.0, 0.9, ("radial", 1.1)), (0.5, 0.3, 1.15))
    S.mostra(fl, [(f_m, f_m + 3)])
    S.mostra(ts, [(A, f_m + 2)])
    pq = props.inked("pasta_c", rrect(-0.08, 0.0, 0.08, 0.1, 0.01, 2), "#7a4a2a", None, loc=(0.55, 0.4, 0.55), w=0.0, rim=0.006, rim_color="#ffc88a")
    S.mostra(pq, [(f_m + 3, END + 5)])
    for f in range(f_m + 3, f_m + 10):
        u = (f - f_m - 3) / 6; pq.location.z = 0.55 * (1 - u * u); key(pq, "location", f, "LINEAR")
    # primeiro plano: uma cerca baixa bem perto da lente (o ponto de vista de quem vigia)
    for i in range(6):
        props.poly(f"cerca{i}", cena.rect(-0.9 + i * 0.36, 0.0, -0.84 + i * 0.36, 0.95), _mix(p["top"], "#000000", 0.4), -1.6)
    props.poly("cerca_t", cena.rect(-1.2, 0.72, 1.2, 0.78), _mix(p["top"], "#000000", 0.4), -1.61)
    AD.arvore(p, "arv8a", -3.6, 2.8, s=1.0)
    AD.arvore(p, "arv8b", 3.7, 2.9, s=1.1)
    AD.fios(p, "fios8", [(-4.5, 3.9), (0.0, 4.2), (4.5, 3.8)], 2.4)
    AD.caixa_correio(p, "cc8", 1.25, 1.2)
    planos(c, [
        dict(t0=42.33, t1=wt(10, "tesoureiro") - 0.15, caixa0=(-3.1, -1.5, 0.45, 2.05, 2.1), caixa1=(-3.0, -1.6, 0.5, 2.0, 2.1), lens=40, fstop=2.0,
             chaves_fim=["ol0", "ol1", "ol4"]),
        dict(t0=wt(10, "tesoureiro") - 0.15, t1=wt(10, "fuzilado") - 0.4, caixa0=(-1.45, 1.35, 0.0, 3.0, 0.8), caixa1=(-1.3, 1.25, 0.05, 2.9, 0.8), lens=32, fstop=2.2,
             chaves=["tes", "porta8"]),
        dict(t0=wt(10, "fuzilado") - 0.4, t1=48.43, caixa0=(-0.2, 1.3, 0.0, 2.4, 1.0), caixa1=(-0.1, 1.2, 0.05, 2.3, 1.0), lens=40, fstop=2.0,
             chaves=["porta8"]),
    ], entra="h", sai="h")


# ====================================================================== B9. O topo (48,43 - 53,21)
@cena_("b9", 48.43, 53.21)
def b9(c):
    A, END = F(48.0), F(53.6)
    p = S.var(P, top="#1a1250", mid="#d85a7a", low="#ff9650", chao="#2a1850", halo="#ffb050", luz="#ffe0b0", pedra="#3a2a78", aresta="#ffd0a0", borda="#ffd6a0", grade="#0d0830")
    wy = 9.0
    bpy.context.scene.world.node_tree.nodes["Background"].inputs[0].default_value = (*srgb(p["top"]), 1)
    props.skywall("ceu9", wy, [(-3, "#ff9650"), (1.2, "#ff7a5a"), (3.5, "#d85a7a"), (7, "#7a3a9a"), (12, "#241470")], -25, 25, -3, 14)
    cena.poly_mesh("chao9", [(-25, -30, -0.004), (25, -30, -0.004), (25, wy, -0.004), (-25, wy, -0.004)], props.FM(p["chao"]))
    cena.disc("sol9", 1.8, cena.amat("sol9_m", "#fff0c0", 2.0, 1.0, ("radial", 1.1)), (1.2, wy - 0.1, 2.0))
    cena.disc("halo9", 5.5, cena.amat("halo9_m", "#ffd090", 1.0, 0.5, ("radial", 1.6)), (1.2, wy - 0.15, 2.0))
    S.cidade(p, wy - 0.4, -12, 12, 0.0, seed=33, lit=0.08, cor="#2a1468", luzc="#ffd090", hmax=4.0)
    props.poly("mureta9", cena.rect(-8, 0.0, 8, 0.95), "#1a0f50", 2.6)
    props.poly("mureta9a", cena.rect(-8, 0.9, 8, 0.95), p["aresta"], 2.59)
    prof(p, (3.4, 6.0), alfa=0.12)
    S.caixa3d(p, "mesa9", 0.25, -0.25, 1.3, 0.78, d=0.7, cor="#1e1458", tampo="#3a2a88")
    ms = []
    for i in range(10):
        r, col = divmod(i, 5)
        ms.append(G.maco(f"m9_{i}", (-0.14 + 0.2 * col, -0.05, 0.78 + r * 0.085), n=1, s=1.25, zk=3.0))
    for j, x in enumerate((0.75, 1.15, 1.55)):
        props.pessoa(f"poucos{j}", x, 0.55, "#2a1a80", 1.0, flip=-1, rim=p["borda"])
    for i in range(2, 10):
        f0 = F(wt(11, "oitenta") + 0.06 * (i - 2))
        S.arco(ms[i], f0, f0 + 12, tuple(ms[i].location), (0.7 + 0.1 * (i % 4), -0.1, 0.78 + 0.085 * (i // 4)), alt=0.3)
    H, tl, w = heroi(p, "front", -0.55, A, END, y=0.15)
    tl.face(A, 0.0, lid="esperto", lidv=0.55, brow=-8, mouth="sorriso", look=(0.9, 0.1))
    tl.face(F(wt(11, "poucos")), 1.0, lid="esperto", lidv=0.5, brow=-12, browtilt=0.02, mouth="lado", look=(1.0, 0.0))
    tl.face(F(wt(11, "dinheiro")), 1.0, lid="esperto", lidv=0.45, brow=-16, browtilt=0.024, mouth="sorriso", look=(0.0, 0.0))
    finish(H, tl, A, END)
    frente.bracos(H, A, END, [(A, dict(shF=5, elF=0, shB=5, elB=0)), (F(wt(11, "divide")), dict(shF=5, elF=-2, shB=5, elB=-2)), (F(wt(11, "poucos")), dict(shF=10, elF=-30, shB=44, elB=-76, wrB=-10))])
    S.coluna_fg(p, "vidro9", 1.0, -1.7, w=0.1)
    AD.varal_luzes(p, "var9", -2.6, 2.6, 2.8, 1.8)
    AD.espreguicadeira(p, "esp9", -1.7, 1.5)
    S.planta(p, "planta9", 2.1, 1.2, s=1.1)
    planos(c, [
        dict(t0=48.43, t1=wt(11, "oitenta") - 0.12, caixa0=(-0.95, 1.85, 0.0, 2.1, 0.3), caixa1=(-0.9, 1.8, 0.05, 2.05, 0.3), lens=30, fstop=2.2,
             chaves=["heroi_inv", "poucos0", "poucos2"]),
        dict(t0=wt(11, "oitenta") - 0.12, t1=wt(11, "dinheiro") + 0.3, caixa0=(-0.35, 1.3, 0.55, 1.45, -0.1), caixa1=(-0.3, 1.25, 0.6, 1.4, -0.1), alt0=1.55, alt1=1.5, lens=40, fstop=2.0,
             chaves=["mesa9_t"]),
        dict(t0=wt(11, "dinheiro") + 0.3, t1=53.21, caixa0=(-0.92, -0.18, 1.0, 1.9, 0.15), caixa1=(-0.9, -0.2, 1.05, 1.88, 0.15), lens=50, fstop=1.6),
    ], entra="h", sai="h")


# ====================================================================== B10. A traição (53,21 - 59,65)
@cena_("b10", 53.21, 59.65)
def b10(c):
    A, END = F(52.8), F(60.0)
    p = S.var(P, **T.PALETAS["vinho"]); wy = 4.0
    S.fundo(p, wy, z_meio=2.4, x=(-10, 10), z=(-3, 10))
    for x in (-2.0, 2.0):
        props.poly(f"col10{x}", cena.rect(x - 0.3, 0, x + 0.3, 6), _mix(p["coluna"], p["top"], 0.2), wy - 0.1)
    cena.disc("halo10", 3.2, cena.amat("halo10_m", p["halo"], 1.0, 0.4, ("radial", 1.5)), (0.0, wy - 0.1, 2.0))
    luz.feixe("feixe10", 0.0, 1.2, 0.0, 6.0, 1.8, 0.4, p["luz"], forca=1.2, frames=END, poeira=45, seed=61)
    prof(p, (2.6,))
    xs = [-1.2, -0.6, 0.0, 0.6, 1.2]
    cores = ["#3a1840", "#46203e", "#52262c", "#46203e", "#3a1840"]
    figs = []
    for i, (x, cor) in enumerate(zip(xs, cores)):
        figs.append(S.pm(p, f"chefe10_{i}", x, 1.2, h=1.0, flip=1 if x < 0 else -1, cor=cor, rim=p["borda"]))
    S.caixa3d(p, "mesa10", 0.0, 0.85, 3.0, 0.95, d=0.7, cor=_mix(p["top"], p["mid"], 0.55), tampo=_mix(p["top"], p["aresta"], 0.25))
    cr = S.coroa("coroa10", (0.0, 1.18, 1.86), 0.85)
    t_tr = wt(12, "traição")
    for i, d in ((1, -1), (3, 1)):
        o = figs[i]; base = o.location.x
        for f in range(F(t_tr) - 1, F(t_tr) + 18):
            u = min(1.0, max(0.0, (f - F(t_tr)) / 14)); s_ = curvas.s("easy", u)
            o.rotation_euler = (0, math.radians(7 * d * s_), 0); key(o, "rotation_euler", f, "LINEAR")
            o.location.x = base + 0.05 * d * s_; key(o, "location", f, "LINEAR")
    f_m = F(wt(12, "matar"))
    mr = S.mira("mira10", (0.0, 0.9, 2.6), 0.7)
    for f in range(f_m - 10, f_m + 1):
        u = (f - (f_m - 10)) / 10; s_ = curvas.s("queda", u)
        mr.location = (0.0, 0.9, 2.6 + (1.6 - 2.6) * s_); key(mr, "location", f, "LINEAR")
        v = 1.4 - 0.7 * s_; mr.scale = (v, v, v); key(mr, "scale", f, "LINEAR")
    f_l = F(wt(12, "líder"))
    S.mostra(mr, [(f_m - 10, f_l + 2)])
    cr.location = (0.0, 1.18, 1.86); key(cr, "location", f_l - 1, "CONSTANT")
    for f in range(f_l, f_l + 14):
        u = (f - f_l) / 13; cr.location = (0.16 * u, 1.18 - 0.4 * u, 1.86 - 1.0 * u * u); cr.rotation_euler = (0, math.radians(120 * u), 0)
        key(cr, "location", f, "LINEAR"); key(cr, "rotation_euler", f, "LINEAR")
    S.mostra(cr, [(A, f_l + 15)])
    omb = S.ombro(p, "ombro10", -0.75, -1.4, 1.2, s=1.25)                              # por cima do ombro de um chefe
    S.mostra(omb, [(A, F(wt(12, "em", 0) + 0.85))])                                        # só no plano aberto (nos closes ficaria na lente)
    AD.lustre(p, "lus10", 0.0, 3.2, 1.6, frames=END)
    AD.garrafas(p, "gar10", -0.95, 0.83, 0.95)
    AD.garrafas(p, "gar10b", 0.75, 0.83, 0.95, n=2)
    AD.cortina(p, "cort10e", -2.7, 3.9, lado=1)
    AD.cortina(p, "cort10d", 2.7, 3.9, lado=-1)
    planos(c, [
        dict(t0=53.21, t1=wt(12, "em", 0) + 0.85, caixa0=(-1.65, 1.65, 0.3, 2.4, 0.9), caixa1=(-1.55, 1.55, 0.35, 2.35, 0.9), lens=32, fstop=2.0,
             chaves=["chefe10_0", "chefe10_4", "coroa10"]),
        dict(t0=wt(12, "em", 0) + 0.85, t1=wt(12, "mandaram") - 0.1, caixa0=(-1.55, 0.4, 0.95, 2.3, 1.2), caixa1=(-1.5, 0.35, 1.0, 2.25, 1.2), lens=45, fstop=1.8,
             chaves=["coroa10"]),                                                            # a coroa inteira no quadro: eles cochicham olhando para ela
        dict(t0=wt(12, "mandaram") - 0.1, t1=59.65, caixa0=(-0.5, 0.5, 0.95, 2.3, 1.2), caixa1=(-0.45, 0.45, 1.0, 2.25, 1.2), lens=45, fstop=1.8,
             chaves=["coroa10"]),
    ], entra="h", sai="h")


# ====================================================================== B11. O preço (59,65 - 62,82)
@cena_("b11", 59.65, 62.82)
def b11(c):
    A, END = F(59.3), F(63.2)
    p = pal("celas"); wy = 4.4
    S.fundo(p, wy, z_meio=2.6, x=(-10, 10), z=(-3, 10), escuro=0.12)
    prof(p, (0.8, 3.0))
    pisos = [0.0, 1.35, 2.7]; cores = ["#2a2f6a", "#33397a", "#3c4288", "#262b66", "#30367a"]
    n = 0; livre = None
    for r, z in enumerate(pisos):
        props.poly(f"laje{r}", cena.rect(-1.95, z - 0.05, 1.95, z + 0.02), _mix(p["aresta"], p["mid"], 0.45), 1.95)
        for i in range(5):
            x = -1.5 + i * 0.75
            props.poly(f"cel{r}_{i}", cena.rect(x - 0.34, z + 0.02, x + 0.34, z + 1.22), _mix(p["top"], p["mid"], 0.25), 2.0)
            props.pessoa(f"ch{n}", x, 1.9, cores[(r + i) % 5], 0.62, flip=1 if i % 2 else -1, rim=p["borda"], z=z + 0.02)
            if n == 14:
                livre = (x, z)
            else:
                t = wt(13, "só") - 0.12 + 0.07 * n
                j = props.jaula(f"j{n}", x, z + 0.02, w=0.62, h=1.2, y=1.75)
                j.location.z = z + 2.6; key(j, "location", F(t) - 1, "CONSTANT")
                for f in range(F(t), F(t) + 7):
                    u = (f - F(t)) / 6; j.location.z = z + 0.02 + 2.6 * (1 - curvas.s("queda", u)); key(j, "location", f, "LINEAR")
            n += 1
    xl, zl = livre
    fo = cena.disc("foco_livre", 0.8, cena.amat("foco_livre_m", "#ffe9a8", 1.0, 0.0, ("radial", 1.3)), (xl, 1.85, zl + 0.65))
    node = [nn for nn in fo.data.materials[0].node_tree.nodes if nn.type == "MATH" and nn.operation == "MULTIPLY"][0]
    for f_, a_ in ((F(wt(13, "só")) + 6, 0.0), (F(wt(13, "solto")), 0.75)):
        node.inputs[1].default_value = a_; node.inputs[1].keyframe_insert("default_value", frame=f_)
    # ele de costas, em primeiro plano, olhando o bloco de celas (por cima do ombro)
    Hc, tlc, wc = heroi(p, "back", -0.55, A, END, y=-1.0, name="heroi_costas")
    tlc.intent(A, head=-10, torso=-2)
    tlc.bake()                                                   # de costas: sem rosto (sem piscar)
    for r, z in enumerate(pisos):
        AD.placa_numero(p, f"pn{r}", -2.15, z + 1.0, 1.9, str(r + 1))
        for i in range(5):
            cena.disc(f"lamp11_{r}_{i}", 0.18, cena.amat("lamp11_m", p["luz"], 1.0, 0.35, ("radial", 1.4)), (-1.5 + i * 0.75, 1.88, z + 1.3))
    planos(c, [
        dict(t0=59.65, t1=wt(13, "só") - 0.1, caixa0=(-2.2, 2.2, -0.1, 4.1, 1.9), caixa1=(-2.1, 2.1, 0.0, 4.0, 1.9), lens=30, fstop=2.4,
             chaves=["cel0_0", "cel2_4", "cel0_4", "cel2_0"]),
        dict(t0=wt(13, "só") - 0.1, t1=62.82, caixa0=(xl - 0.9, xl + 0.9, zl - 0.3, zl + 1.5, 1.9), caixa1=(xl - 0.55, xl + 0.55, zl - 0.1, zl + 1.35, 1.9), lens=40, fstop=2.0,
             chaves=["ch14"]),
    ], entra="h", sai="h")


# ====================================================================== B12. Ainda quer subir? (62,82 - 64,80)
@cena_("b12", 62.82, 64.8)
def b12(c):
    A, END = F(62.4), F(65.2)
    p = pal("celas"); wy = 3.0
    pe = dict(p, mid=_mix(p["mid"], p["top"], 0.5), low=_mix(p["low"], p["top"], 0.4))
    S.fundo(pe, wy, z_meio=1.8, x=(-10, 10), z=(-3, 10))
    luz.feixe("feixe_b12", 0.0, 0.6, 0.0, 5.0, 1.3, 0.3, p["luz"], forca=1.4, frames=END, poeira=40, seed=77)
    cena.disc("halo_b12", 1.6, cena.amat("halo_b12_m", p["halo"], 1.0, 0.45, ("radial", 1.5)), (0.0, wy - 0.1, 1.6))
    # ele atrás da grade (em primeiro plano, desfocada), de frente, olhando para cima
    gr = props.grade("grade_fim", -1.4, 1.4, 0.0, 3.0, -0.55, p["grade"], n=8, w=0.05, rails=0)
    H, tl, w = heroi(p, "front", 0.0, A, END)
    tl.intent(A, head=-8, torso=0)
    tl.face(A, 0.0, wide=0.3, brow=8, browup=0.012, mouth="pequena", look=(0.2, 0.8))
    tl.face(F(wt(14, "quer")), 1.0, lid="esperto", lidv=0.6, brow=-10, browtilt=0.018, mouth="lado", look=(0.0, 0.0))
    tl.intent(F(wt(14, "quer")) - 4, head=6, torso=2)
    finish(H, tl, A, END)
    frente.bracos(H, A, END, [(A, dict(shF=5, elF=0, shB=5, elB=0))])
    planos(c, [
        dict(t0=62.82, t1=64.8, caixa0=(-0.45, 0.45, 0.95, 1.95, 0.0), caixa1=(-0.42, 0.42, 1.02, 1.92, 0.0), lens=50, fstop=1.6),
    ], entra="h", sai=None)


if __name__ == "__main__":
    P4.main()
