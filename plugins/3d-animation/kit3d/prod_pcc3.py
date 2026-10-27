"""PCC, versão 3: 15 cenas planejadas (roteiros/decupagem-pcc.md e personagem/pcc/storyboard).
Cada cena é um lugar só, com um movimento de câmera suave e os elementos entrando na ordem do storyboard.
blender -b -P prod_pcc3.py -- CENA OUT [--scale 1] [--samples 16] [--at t1,t2] [--list]"""
import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy, lib
from lib import *
import cena, props, limpo, trono as T, frente, luz, curvas
from heroi import Heroi
from anim import Timeline
from acting import Actor
from prod_pcc import F, wt, finish, FPS
_mix = props._mix

CENAS = {}


def cena_(name, t0, t1):
    def deco(fn):
        CENAS[name] = (t0, t1, fn); return fn
    return deco


def camera_movel(c, keys, lens=40, focus=None, fstop=2.8):
    """uma câmera só, que desliza com aceleração e desaceleração. keys = [(t, (x, y, z), shift_y)].
    O shift (lente descentralizada) deixa olhar para baixo sem girar a câmera."""
    sc = c["sc"]
    cam = cena.camera(sc, [(F(t), p) for t, p, _ in keys], lens=lens, focus=focus or 5.0, fstop=fstop)
    for t, p, sy in keys:
        cam.data.shift_y = sy; cam.data.keyframe_insert("shift_y", frame=F(t))
    if focus is None:
        cam.data.dof.use_dof = False
    rig = empty("camrig"); cam.parent = rig
    return cam, rig


# ====================================================================== 1. O rei (0,0 - 3,55)
PALETA = os.environ.get("PALETA", "petroleo")       # escolhida pelo usuário em 22/10/2026


@cena_("c1", 0.0, 3.55)
def c1(c):
    sc = c["sc"]; END = F(3.8)
    p = T.PALETAS[PALETA]
    Z_D, K = 2.5, 2.4
    T.salao(p, END + 30)
    T.estrado(p, Z_D)
    T.trono(p, "trono", (0.0, 0.0, Z_D), K)
    H = Heroi("heroi", "front", pal=dict(rim=p["borda"]))
    wrap = empty("heroi_wrap", None, (0.0, -0.02, Z_D)); wrap.scale = (K, K, K); H.root.parent = wrap
    tf0 = -10
    tl = Timeline(H, tf0, END, FPS); tl.stand(tf0, END, 0.0)
    tl.intent(tf0, torso=0, head=0)
    tl.face(tf0, 0.0, lid="sono", lidv=0.6, brow=-10, mouth="reta", look=(0.0, -0.4))
    tl.face(F(0.3), 1.0, lid="esperto", lidv=0.5, brow=-16, browtilt=0.02, mouth="sorriso", look=(0.0, 0.0))     # "Imagina": olhar maligno
    tl.face(F(2.25), 1.0, lid="esperto", lidv=0.42, brow=-18, browtilt=0.024, mouth="sorriso", look=(0.0, -0.25))
    finish(H, tl, tf0, END)
    repouso = dict(shF=26, elF=6, wrF=0, shB=26, elB=6, wrB=0)
    manda = dict(shF=62, elF=-70, wrF=-10, shB=26, elB=6, wrB=0)                                            # "comandar": ergue a mão
    frente.bracos(H, tf0, END, [(tf0, repouso), (F(0.85), repouso), (F(1.1), manda), (F(1.8), manda), (F(2.25), repouso)])
    frente.sentado(H, tf0, END)
    # o povo de costas, com borda de luz do trono, e a onda de reverência
    faixas = T.multidao_contada(p, F, t0=1.37, dur=1.3)              # cada pessoa acende quando o "40.000" passa por ela
    T.reverencia(faixas, F, 2.5)
    # "de dentro de uma cela": a grade desce na frente do estrado
    gr = props.grade("grade_trono", -6.2, 6.2, 0.0, 11.5, -3.25, p["grade"], n=14, w=0.16, rails=2)
    gr.location.z = 16.0; key(gr, "location", F(2.92), "QUAD")
    gr.location.z = 0.0; key(gr, "location", F(3.17), "CONSTANT")
    # primeiro plano: duas colunas perto da câmera que entram pelas bordas enquanto ela recua (moldura e profundidade)
    for x in (-2.9, 2.9):
        sg = 1 if x < 0 else -1
        props.poly(f"col_frente{x}", cena.rect(x - 0.9, -2, x + 0.9, 40), _mix(p["coluna"], "#000000", 0.35), -31.0)
        xa = x + 0.9 * sg
        props.poly(f"col_frente{x}_luz", cena.rect(min(xa, xa - 0.1 * sg), -2, max(xa, xa - 0.1 * sg), 40), p["coluna_luz"], -31.01)
    # dois fachos inclinados das janelas altas (luz de cima, mesma cor do halo)
    for x, sg in ((-7.5, 1), (7.5, -1)):
        fx = cena.poly_mesh(f"facho{x}", [(-1, 0, 0), (1, 0, 0), (0.25, 0, 1), (-0.25, 0, 1)], cena.amat(f"facho{x}_m", p["luz"], 1.0, 0.07, ("shaft", 1.2, 0.8)))
        fx.location = (x * 0.22, 5.5, 2.0); fx.scale = (1.8, 1, 22.0); fx.rotation_euler = (0, math.radians(-sg * 20), 0)
    # câmera: um recuo só, sem parada. A distância cresce em escala logarítmica (o zoom parece constante) e a curva
    # acelera devagar e chega ao fim ainda em movimento, entrando na cortina que leva à cena 2
    cam, rig = camera_movel(c, [(0.0, (0.0, -3.7, 4.9), 0.0)], lens=40, focus=3.7, fstop=2.0)
    recuo_suave(cam, F(0.25), F(3.55), d0=3.7, d1=41.0, z0=4.9, z1=8.2, sh1=-0.26, curva=os.environ.get("CURVA", "easy"))      # curva A escolhida pelo usuário
    cortina(cam, p, F(3.18), F(3.55), entra=True)


def recuo_suave(cam, fa, fb, d0, d1, z0, z1, sh1, curva="easy", x0=0.0, x1=0.0):
    """grava a câmera quadro a quadro. O progresso s segue uma curva do After Effects (curvas.py);
    a distância vai de d0 a d1 em escala log (o afastamento parece constante), a altura sobe pouco e
    a lente descentralizada (shift) faz o resto do "olhar para baixo", sem girar a câmera"""
    cd = cam.data
    for f in range(fa, fb + 1):
        u = min(1.0, max(0.0, (f - fa) / (fb - fa)))
        s_ = curvas.s(curva, u)
        d = d0 * (d1 / d0) ** s_
        cam.location = (x0 + (x1 - x0) * s_, -d, z0 + (z1 - z0) * s_); key(cam, "location", f, "LINEAR")
        cd.shift_y = sh1 * s_ ** 0.8; cd.keyframe_insert("shift_y", frame=f)
        cd.dof.focus_distance = d + 0.2; cd.dof.keyframe_insert("focus_distance", frame=f)
    lib.all_interp(cd, "LINEAR")


def cortina(cam, p, fa, fb, entra=True):
    """transição em movimento: uma coluna escura passa bem perto da lente (desfocada) da direita para a esquerda.
    entra=True: chega e cobre a tela no fim, acelerando; entra=False: começa cobrindo e sai, desacelerando.
    Usar entra=True no fim de uma cena e entra=False no começo da seguinte, com a mesma duração."""
    root = empty("cortina_" + cam.name, cam, (0.0, -0.4, -0.7))
    cena.poly_mesh("cortina_f_" + cam.name, [(-0.8, -2.0, 0), (0.8, -2.0, 0), (0.8, 2.0, 0), (-0.8, 2.0, 0)], props.FM(_mix(p["coluna"], "#000000", 0.45))).parent = root
    for x in (-0.8, 0.77):
        cena.poly_mesh(f"cortina_b{x}_" + cam.name, [(x, -2.0, 0.001), (x + 0.03, -2.0, 0.001), (x + 0.03, 2.0, 0.001), (x, 2.0, 0.001)], props.FM(p["coluna_luz"])).parent = root
    xa, xb = (1.5, 0.0) if entra else (0.0, -1.7)
    root.location.x = xa; key(root, "location", fa - 1 if entra else fa - 1, "CONSTANT")
    root.location.x = xa; key(root, "location", fa, "QUAD")
    root.location.x = xb; key(root, "location", fb, "QUAD")
    for fc in lib._fcs(root):
        for kp in fc.keyframe_points:
            kp.easing = "EASE_IN" if entra else "EASE_OUT"
    return root


# ====================================================================== 2. O chefe na cela (3,55 - 7,34)
def baked_slide(cam, fa, fb, p0, p1, curva="easy"):
    """desliza p0 -> p1 seguindo a curva escolhida (curvas.py), gravado quadro a quadro"""
    for f in range(fa, fb + 1):
        u = (f - fa) / (fb - fa); s_ = curvas.s(curva, u)
        cam.location = tuple(a + (b - a) * s_ for a, b in zip(p0, p1)); key(cam, "location", f, "LINEAR")


@cena_("c2", 3.55, 7.34)
def c2(c):
    sc = c["sc"]; A, END = F(3.3), F(7.8)
    p = T.PALETAS[PALETA]
    wy = 1.8
    sc.world.node_tree.nodes["Background"].inputs[0].default_value = (*lib.srgb(p["top"]), 1)
    props.skywall("cela_parede", wy, [(-1, p["low"]), (1.6, p["mid"]), (3.6, _mix(p["mid"], p["top"], 0.5)), (6, p["top"])], -9, 9, -2, 9)
    for k in range(-6, 7):                                        # juntas das placas de concreto
        props.poly(f"cela_junta{k}", cena.rect(k * 1.2 - 0.008, -1, k * 1.2 + 0.008, 9), _mix(p["mid"], p["top"], 0.3), wy - 0.01)
    cena.poly_mesh("cela_chao", [(-9, -9, -0.004), (9, -9, -0.004), (9, wy, -0.004), (-9, wy, -0.004)], props.FM(p["chao"]))
    # a janela no eixo, com grade, e o facho que desce dela com poeira
    props.poly("jan_moldura", cena.rect(-0.55, 2.25, 0.55, 3.05), p["grade"], wy - 0.02)
    props.poly("jan_vidro", cena.rect(-0.47, 2.33, 0.47, 2.97), "#d6e7e4", wy - 0.03, strength=1.15)
    for i in range(4):
        xb = -0.47 + 0.94 * (i + 0.5) / 4
        props.poly(f"jan_barra{i}", cena.rect(xb - 0.025, 2.25, xb + 0.025, 3.05), p["grade"], wy - 0.04)
    luz.feixe("feixe_jan", 0.0, wy - 0.3, 0.0, 2.65, 1.5, 0.42, p["luz"], forca=1.3, frames=END, poeira=70, seed=3)
    # banco de concreto e o chefe sentado de frente
    props.inked("banco", cena.rect(-1.15, 0.0, 1.15, 0.64), p["pedra"], None, (0, 0.3, 0), w=0.012, rim=0.02, rim_color=p["aresta"])
    H = Heroi("heroi", "front", pal=dict(rim=p["borda"]))
    tl = Timeline(H, A, END, FPS); tl.stand(A, END, 0.0)
    tl.face(A, 0.0, lid="sono", lidv=0.62, brow=-8, mouth="reta", look=(0.0, -0.5))
    tl.face(F(4.4), 1.0, lid="sono", lidv=0.55, brow=-6, mouth="reta", look=(0.15, 0.85))                         # olha a luz da polícia na janela
    tl.face(F(5.3), 1.0, lid="esperto", lidv=0.5, brow=-16, browtilt=0.02, mouth="sorriso", look=(0.0, 0.0))      # "o chefe": para a câmera
    tl.face(F(6.4), 1.0, lid="esperto", lidv=0.45, brow=-4, browup=0.014, browtilt=0.022, mouth="sorriso", look=(0.0, 0.0))   # "faz isso"
    tl.intent(A, head=6); tl.intent(F(4.3), head=6); tl.intent(F(4.6), head=-4); tl.intent(F(5.2), head=-4); tl.intent(F(5.45), head=0)
    finish(H, tl, A, END)
    frente.bracos(H, A, END, [(A, dict(shF=10, elF=-42, wrF=-10, shB=10, elB=-42, wrB=-10))])
    frente.sentado(H, A, END)
    # a grade da porta na frente, com um vão no eixo (não corta o rosto)
    porta = props.grade("cela_porta", -3.0, 3.0, 0.0, 4.6, -1.3, p["grade"], n=10, w=0.07, rails=0)
    for z in (0.04, 4.45):                                        # trilhos só no pé e no alto (nada cruzando o corpo)
        props.poly(f"cela_porta_t{z}", cena.rect(-3.0, z, 3.0, z + 0.09), p["grade"], -0.001, porta)
    # polícia: vermelho e azul varrem a parede da esquerda para a direita
    for i, (cor, atraso) in enumerate((("#ff3b4a", 0.0), ("#3d7bff", 0.21))):
        d = cena.disc(f"pol{i}", 1.9, cena.amat(f"pol{i}_m", cor, 1.0, 0.0, ("radial", 1.4)), (-4.0, wy - 0.05, 2.4))
        m = d.data.materials[0]; sk = [n for n in m.node_tree.nodes if n.type == "MATH" and n.operation == "MULTIPLY"][0].inputs[1]
        t = 4.25 + atraso
        for k in range(3):
            d.location.x = -4.0; key(d, "location", F(t + k * 0.62), "LINEAR")
            d.location.x = 4.0; key(d, "location", F(t + k * 0.62 + 0.55), "LINEAR")
        for f_, a_ in ((F(4.2), 0.0), (F(4.4), 0.42), (F(5.6), 0.42), (F(6.2), 0.12)):
            sk.default_value = a_; sk.keyframe_insert("default_value", frame=f_)
    # "CHEFE DO PCC": linha que se desenha do ombro dele e a etiqueta que assenta
    lin = empty("rotulo_linha", None, (0.0, -0.25, 1.5))                # rótulo no eixo, acima da cabeça, no vão da grade
    props.poly("rotulo_l1", cena.rect(-0.004, 0.0, 0.004, 0.06), "#ffffff", 0.0, lin)
    lin.scale = (1, 1, 0.0001); key(lin, "scale", F(5.31) - 1, "CONSTANT")
    lin.scale = (1, 1, 1); key(lin, "scale", F(5.31) + 5, "BEZIER")
    rot = empty("rotulo", None, (0.0, -0.26, 1.68))
    props.inked("rotulo_placa", props.rrect(-0.23, -0.09, 0.23, 0.13, 0.03, 4), _mix(p["top"], "#000000", 0.2), rot, loc=(0, 0.003, 0), w=0.0, rim=0.006, rim_color=p["halo"])
    props.txt("rotulo_a", "CHEFE", 0.085, "#ffffff", (0.0, 0.0, 0.07), rot, ink=_mix(p["top"], "#000000", 0.3), ow=0.06)
    props.txt("rotulo_b", "DO PCC", 0.085, p["halo"], (0.0, 0.0, -0.035), rot, ink=_mix(p["top"], "#000000", 0.3), ow=0.06)
    sub = props.poly("rotulo_sub", cena.rect(-0.2, 1.59, 0.2, 1.6), "#ffffff", -0.262)
    for o, base in ((rot, (1, 1, 1)), (sub, (1, 1, 1))):
        o.scale = (0.0001,) * 3; key(o, "scale", F(5.31) + 3, "CONSTANT")
        o.scale = (0.92, 0.92, 0.92); key(o, "scale", F(5.31) + 4, "BEZIER")
        o.scale = base; key(o, "scale", F(5.31) + 12, "BEZIER")
    # câmera: chega já andando (a cortina sai pela esquerda), desliza para a direita e se aproxima, sem parar
    cam, rig = camera_movel(c, [(3.55, (-0.55, -4.4, 1.0), 0.0)], lens=40, focus=4.4, fstop=2.2)
    baked_slide(cam, F(3.55), F(7.34), (-0.55, -4.4, 1.05), (0.25, -2.6, 1.06))
    cd = cam.data
    for t_, d_ in ((3.55, 4.4), (7.8, 2.45)):
        cd.dof.focus_distance = d_; cd.dof.keyframe_insert("focus_distance", frame=F(t_))
    cortina(cam, p, F(3.55), F(3.55) + 9, entra=False)
    cortina(cam, p, F(7.34) - 9, F(7.34), entra=True)            # sai para a escada sem parar
    luz.bokeh("bokeh_cela", -3.6, (-1.6, 1.6), (0.2, 2.4), p["luz"], n=8, frames=END, r=(0.015, 0.04), alpha=0.1)


# ====================================================================== 3. Os 5 níveis (7,34 - 11,18)
def escada5(p, x0=0.0, sw=0.95, sh=1.2, terraco=1.3, y=0.6):        # alta e estreita: cabe no 9:16
    """5 degraus iguais subindo da esquerda para a direita, em pedra da paleta, com aresta clara e o número na face.
    Cada degrau é uma raiz (para crescer do chão); devolve [(raiz, número apagado, número aceso)]"""
    out = []
    for k in range(5):
        xa = x0 + k * sw; xb = x0 + 5 * sw + terraco; top = (k + 1) * sh
        r = empty(f"deg{k}", None, (0, y - 0.01 * k, 0))
        cor = _mix(p["pedra"], p["mid"], 0.12 * k)
        props.poly(f"deg{k}_f", cena.rect(xa, 0.0, xb, top), cor, 0.0, r)
        props.poly(f"deg{k}_a", cena.rect(xa, top - 0.05, xb, top), p["aresta"] if k < 4 else p["halo"], -0.002, r)
        props.poly(f"deg{k}_s", cena.rect(xa, 0.0, xa + 0.05, top), _mix(cor, "#000000", 0.25), -0.003, r)
        n0 = props.txt(f"num{k}_0", str(k + 1), 0.48, _mix(cor, p["aresta"], 0.25), (xa + sw / 2, y - 0.06, top - 0.5), None, ink=None)
        n1 = props.txt(f"num{k}_1", str(k + 1), 0.48, p["friso"] if k < 4 else p["halo"], (xa + sw / 2, y - 0.07, top - 0.5), None,
                       ink=_mix(p["top"], "#000000", 0.3), ow=0.05)
        out.append((r, n0, n1))
    return out


def cresce(o, fa, n=8, curva="easy", eixo=2, s0=0.0001):
    """cresce no eixo dado seguindo a curva (gravado quadro a quadro)"""
    for f in range(fa - 1, fa + n + 1):
        u = min(1.0, max(0.0, (f - fa) / n)); v = max(s0, curvas.s(curva, u))
        sc_ = [1.0, 1.0, 1.0]; sc_[eixo] = v; o.scale = sc_; key(o, "scale", f, "LINEAR")


def surge(o, fa, n=8, curva="easy", de=0.9):
    """aparece do 'de' ao tamanho cheio seguindo a curva (sem quique); antes disso, escondido"""
    o.scale = (0.0001,) * 3; key(o, "scale", fa - 1, "CONSTANT")
    for f in range(fa, fa + n + 1):
        v = de + (1 - de) * curvas.s(curva, (f - fa) / n); o.scale = (v, v, v); key(o, "scale", f, "LINEAR")


@cena_("c3", 7.34, 11.18)
def c3(c):
    sc = c["sc"]; A, END = F(7.0), F(11.6)
    p = T.PALETAS[PALETA]
    wy = 3.5
    sc.world.node_tree.nodes["Background"].inputs[0].default_value = (*lib.srgb(p["top"]), 1)
    props.skywall("esc_parede", wy, [(-2, p["low"]), (2.5, p["mid"]), (7, _mix(p["mid"], p["top"], 0.55)), (13, p["top"])], -30, 30, -4, 20)
    cena.poly_mesh("esc_chao", [(-30, -30, -0.004), (30, -30, -0.004), (30, wy, -0.004), (-30, wy, -0.004)], props.FM(p["chao"]))
    xt = 5 * 0.95 + 0.65                                          # meio do terraço do topo
    cena.disc("esc_halo", 4.5, cena.amat("esc_halo_m", p["halo"], 1.0, 0.5, ("radial", 1.6)), (xt - 0.6, wy - 0.1, 7.0))
    degs = escada5(p)
    for k, (r, n0, n1) in enumerate(degs):                         # 1 a 5 sobem em ordem, e o número acende
        t = 7.40 + 0.12 * k
        cresce(r, F(t), 7)
        surge(n0, F(t) + 5, 5)
        n1.scale = (0.0001,) * 3; key(n1, "scale", F(t) + 6, "CONSTANT")
        surge(n1, F(t) + 7 if k < 4 else F(7.98), 6)
    # "cinco": a luz acende só no topo (tremula como refletor ligando)
    luz.feixe("feixe_topo", xt, 0.9, 6.0, 17.0, 1.3, 0.35, p["luz"], forca=1.5, frames=END, poeira=50, seed=11)
    liga = [(A, False), (F(7.98), True), (F(7.98) + 2, False), (F(7.98) + 3, True)]
    for o in [o for o in bpy.data.objects if o.name.startswith("feixe_topo")]:
        props.blink_vis(o, liga, True)
    # "número": cartão "R$ ?" sobre o topo
    card = empty("cartao", None, (xt - 0.3, 0.3, 7.75))
    props.inked("cartao_p", props.rrect(-0.85, -0.42, 0.85, 0.42, 0.12, 6), _mix(p["top"], "#000000", 0.2), card, w=0.0, rim=0.03, rim_color=p["halo"])
    props.txt("cartao_t", "R$ ?", 0.5, p["friso"], (0.0, -0.01, -0.02), card, ink=None)
    surge(card, F(9.30), 9)
    for f_, v in ((F(10.22), 1.0), (F(10.22) + 4, 1.08), (F(10.22) + 10, 1.0)):     # "mentira": pulsa uma vez
        card.scale = (v, v, v); key(card, "scale", f_, "BEZIER")
    # o herói pequeno no pé da escada, olhando para cima
    H = Heroi("heroi", "q", pal=dict(rim=p["borda"]))
    tl = Timeline(H, A, END, FPS); tl.stand(A, END, -0.9)
    tl.intent(A, head=-12, torso=-2)
    tl.face(A, 0.0, browtilt=0.016, mouth="pequena", look=(0.7, 0.7))
    tl.face(F(9.35), 1.0, wide=0.5, browup=0.02, mouth="o", look=(0.75, 0.85))
    tl.face(F(10.22), 1.0, wide=1.0, browup=0.03, mouth="o", look=(0.8, 0.9), extras=("suor",))
    tl.intent(F(10.2), head=-12); tl.intent(F(10.4), head=-17, torso=-4)
    finish(H, tl, A, END)
    cena.contact_shadow(H, dict(shadow=_mix(p["chao"], "#000000", 0.4)))
    # câmera: sai da cortina perto do pé da escada e sobe recuando até mostrar a escada inteira com o topo aceso
    cam, rig = camera_movel(c, [(7.34, (0.2, -5.4, 1.8), 0.0)], lens=40, focus=6.0, fstop=4.0)
    baked_slide(cam, F(7.34), F(11.18), (0.2, -5.4, 1.8), (2.45, -12.6, 4.4))
    cortina(cam, p, F(7.34), F(7.34) + 9, entra=False)


# ====================================================================== execução
def main():
    argv = sys.argv[sys.argv.index("--") + 1:]
    arg = lambda n, d=None: argv[argv.index(n) + 1] if n in argv else d
    if "--list" in argv:
        for k, (a, b, _) in CENAS.items():
            print(f"{k:6s} {a:6.2f}-{b:6.2f}  quadros {F(a)}-{F(b) - 1}")
        return
    name, out = argv[0], argv[1]
    t0, t1, fn = CENAS[name]
    k = float(arg("--scale", "1.0"))
    reset(int(1080 * k), int(1920 * k), FPS, int(arg("--samples", "16")))
    sc = lib.scene
    c = dict(sc=sc, f0=F(t0), f1=F(t1) - 1, t0=t0, t1=t1, F=F)
    sc.frame_start, sc.frame_end = c["f0"], c["f1"]
    fn(c)
    os.makedirs(out, exist_ok=True)
    if "--at" in argv:
        for t in arg("--at").split(","):
            f = F(float(t)); sc.frame_set(f); sc.render.filepath = f"{out}/{name}_{f:04d}.png"; bpy.ops.render.render(write_still=True)
    else:
        sc.render.image_settings.file_format = "PNG"; sc.render.filepath = f"{out}/f_"
        bpy.ops.render.render(animation=True)


if __name__ == "__main__":
    main()