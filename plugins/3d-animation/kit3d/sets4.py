"""Peças de cenário do PCC v4: cada cena tem um lugar próprio. Tudo chapado, com borda de luz, na paleta índigo.
Convenção: a parede fica em y = wy (positivo, longe), os personagens em y ≈ 0 e o que é mais perto da câmera tem y < 0."""
import math, random
import bpy
import lib
from lib import empty, key, srgb
import cena, props, luz, curvas
from char2d import rrect
from puppet2d import circle, stroke

_mix = props._mix


def var(p, **kw):
    d = dict(p); d.update(kw); return d


def fundo(p, wy, z_meio=2.0, x=(-20, 20), z=(-3, 14), escuro=0.0):
    """parede com degradê vertical (claro no meio, escuro no alto) e chão; 'escuro' mistura o fundo com a cor do topo"""
    mid = _mix(p["mid"], p["top"], 0.45 + escuro); low = _mix(p["low"], p["top"], 0.35 + escuro)
    bpy.context.scene.world.node_tree.nodes["Background"].inputs[0].default_value = (*srgb(p["top"]), 1)
    props.skywall(f"parede_{wy}", wy, [(z[0], low), (z_meio, mid), (z_meio + 3.5, _mix(mid, p["top"], 0.55)), (z[1], p["top"])], x[0], x[1], z[0], z[1])
    cena.poly_mesh(f"chao_{wy}", [(x[0], -30, -0.004), (x[1], -30, -0.004), (x[1], wy, -0.004), (x[0], wy, -0.004)], props.FM(p["chao"]))
    # o chão não é uma cor só: uma poça de luz embaixo do assunto e o escurecimento em direção à câmera
    cena.ground_disc(f"poca_{wy}", 4.2, 2.6, cena.amat(f"poca_{wy}_m", _mix(p["pedra"], p["luz"], 0.2), 1.0, 0.42, ("radial", 1.3)), (0.0, -0.4, 0.002), n=64)
    cena.ground_disc(f"esc_{wy}", 7.0, 6.0, cena.amat(f"esc_{wy}_m", "#000000", 1.0, 0.55, ("radial", 0.9)), (0.0, -9.0, 0.003), n=64)


def caixa3d(p, name, x, y, w, h, d=0.5, cor=None, tampo=None, aresta=None, base=0.0):
    """bloco com frente, tampo e aresta clara (mesa, mureta, pedestal). (x, y) = centro da frente; y é a frente."""
    cor = cor or _mix(p["top"], "#000000", 0.2)
    tampo = tampo or _mix(cor, p["aresta"], 0.35)
    cena.poly_mesh(name + "_f", [(x - w / 2, y, base), (x + w / 2, y, base), (x + w / 2, y, h), (x - w / 2, y, h)], props.FM(cor))
    cena.poly_mesh(name + "_t", [(x - w / 2, y, h), (x + w / 2, y, h), (x + w / 2, y + d, h), (x - w / 2, y + d, h)], props.FM(tampo))
    e = min(0.03, h - base)
    cena.poly_mesh(name + "_a", [(x - w / 2, y - 0.001, h - e), (x + w / 2, y - 0.001, h - e), (x + w / 2, y - 0.001, h), (x - w / 2, y - 0.001, h)], props.FM(aresta or p["aresta"]))


def cidade(p, y, x0, x1, base, seed=1, lit=0.14, cor=None, luzc=None, hmax=5.5):
    """prédios de silhueta com janelas acesas (poucas): fundo de cidade"""
    rnd = random.Random(seed); x = x0; cor = cor or _mix(p["top"], p["mid"], 0.25); luzc = luzc or p["friso"]
    k = 0
    while x < x1:
        w = rnd.uniform(0.9, 1.9); h = rnd.uniform(1.6, hmax)
        props.poly(f"pred{seed}_{k}", cena.rect(x, base, x + w, base + h), cor, y)
        for i in range(int((w - 0.2) / 0.34)):
            for j in range(int((h - 0.3) / 0.55)):
                if rnd.random() < lit:
                    xx = x + 0.15 + i * 0.34; zz = base + 0.25 + j * 0.55
                    props.poly(f"pred{seed}_{k}_j{i}_{j}", cena.rect(xx, zz, xx + 0.17, zz + 0.26), luzc, y - 0.01)
        x += w + rnd.uniform(0.0, 0.25); k += 1


def poste(p, name, x, wy, h=3.4, cor_luz="#ffb85a", forca=1.3, frames=2000, poeira=25, seed=5):
    """poste de rua com cone de luz e poça no chão"""
    esc = _mix(p["top"], "#000000", 0.25)
    props.poly(name + "_haste", cena.rect(x - 0.05, 0, x + 0.05, h), esc, wy - 0.4)
    props.poly(name + "_braco", cena.rect(x - 0.05, h - 0.05, x + 0.55, h + 0.03), esc, wy - 0.4)
    props.poly(name + "_lamp", rrect(x + 0.4, h - 0.12, x + 0.75, h - 0.02, 0.03, 3), cor_luz, wy - 0.41, strength=1.6)
    luz.feixe(name + "_f", x + 0.58, wy - 0.5, 0.0, h - 0.1, 1.5, 0.22, cor_luz, forca=forca, frames=frames, poeira=poeira, seed=seed)


def pm(p, name, x, y, h=1.0, flip=1, cor="#1a2060", rim=None):
    """policial de silhueta: pessoa com boné (aba) e faixa clara no peito"""
    r = props.pessoa(name, x, y, cor, h, flip=flip, rim=rim or p["borda"])
    esc = _mix(cor, "#000000", 0.4)
    props.poly(name + "_bone", [(-0.15, 1.69), (0.15, 1.69), (0.14, 1.79), (0.0, 1.82), (-0.14, 1.79)], esc, -0.0005, r)
    props.poly(name + "_aba", cena.rect(0.05, 1.67, 0.24, 1.705), esc, -0.0006, r)
    props.poly(name + "_peito", cena.rect(-0.2, 1.12, 0.2, 1.16), "#c9d2ff", -0.0007, r)
    return r


def viatura(p, name, x, y, s=1.0, flip=1, luzes=True):
    """viatura de lado (silhueta clara com faixa): devolve (raiz, luz vermelha, luz azul)"""
    root = empty(name, None, (x, y, 0)); root.scale = (s * flip, s, s)
    ci = "#dfe4ff"; esc = "#161a55"
    props.poly(name + "_rodaE", circle(-1.3, 0.4, 0.4, 24), "#05061a", 0.0, root)
    props.poly(name + "_rodaD", circle(1.3, 0.4, 0.4, 24), "#05061a", 0.0, root)
    props.inked(name + "_corpo", rrect(-2.1, 0.45, 2.1, 1.0, 0.1, 5), ci, root, loc=(0, -0.01, 0), w=0.0, rim=0.03, rim_color=p["borda"])
    props.inked(name + "_cab", [(-0.95, 1.0), (-0.6, 1.5), (0.8, 1.5), (1.2, 1.0)], ci, root, loc=(0, -0.01, 0), w=0.0, rim=0.03, rim_color=p["borda"])
    props.poly(name + "_vid1", [(-0.78, 1.03), (-0.54, 1.42), (0.05, 1.42), (0.05, 1.03)], "#6f7fe0", -0.02, root)
    props.poly(name + "_vid2", [(0.12, 1.03), (0.12, 1.42), (0.74, 1.42), (1.03, 1.03)], "#6f7fe0", -0.02, root)
    props.poly(name + "_faixa", cena.rect(-2.1, 0.62, 2.1, 0.78), esc, -0.02, root)
    props.poly(name + "_faixa2", cena.rect(-2.1, 0.78, 2.1, 0.84), "#e2534c", -0.02, root)
    props.poly(name + "_farol", rrect(1.92, 0.7, 2.1, 0.88, 0.04, 3), "#ffe2a0", -0.03, root, strength=1.4)
    props.poly(name + "_roda_aro_e", circle(-1.3, 0.4, 0.2, 18), "#8f98d8", -0.02, root)
    props.poly(name + "_roda_aro_d", circle(1.3, 0.4, 0.2, 18), "#8f98d8", -0.02, root)
    r = props.poly(name + "_luzv", cena.rect(-0.45, 1.5, -0.05, 1.62), "#ff3b4a", -0.03, root, strength=1.6)
    b = props.poly(name + "_luzb", cena.rect(0.05, 1.5, 0.45, 1.62), "#3d7bff", -0.03, root, strength=1.6)
    return root, r, b


def pisca_sirene(r, b, f0, f1, per=8):
    """vermelha e azul se alternando (cada uma 'per' quadros ligada)"""
    sr, sb = [(f0 - 1, False)], [(f0 - 1, False)]
    f = f0
    while f < f1:
        sr += [(f, True), (f + per // 2, False)]; sb += [(f + per // 2, True), (f + per, False)]; f += per
    props.blink_vis(r, sr, True); props.blink_vis(b, sb, True)


def luz_cor(name, cor, x, y, z, r, f0, f1, per=8, fase=0, alfa=0.3):
    """mancha de luz colorida (disco radial) que pisca; devolve o disco"""
    d = cena.disc(name, r, cena.amat(name + "_m", cor, 1.0, alfa, ("radial", 1.4)), (x, y, z))
    sq = [(f0 - 1, False)]
    f = f0 + fase
    while f < f1:
        sq += [(f, True), (f + per // 2, False)]; f += per
    props.blink_vis(d, sq, True)
    return d


def mira(name, loc, s=1.0, cor="#ff4a4a"):
    """mira vermelha (círculo e cruz); a raiz fica em 'loc'"""
    root = empty(name, None, loc); root.scale = (s, s, s)
    ang = [(0.45 * math.cos(2 * math.pi * i / 40), 0.45 * math.sin(2 * math.pi * i / 40)) for i in range(41)]
    props.poly(name + "_aro", stroke(ang, 0.012), cor, 0.0, root, strength=1.4)
    for a, b in (((-0.62, 0), (-0.2, 0)), ((0.2, 0), (0.62, 0)), ((0, -0.62), (0, -0.2)), ((0, 0.2), (0, 0.62))):
        props.poly(f"{name}_c{a}{b}", stroke([a, b], 0.012), cor, -0.001, root, strength=1.4)
    props.poly(name + "_pt", circle(0, 0, 0.02, 12), cor, -0.002, root, strength=1.6)
    return root


def olhos(name, x, z, y, s=1.0, cor="#ffd24a"):
    """par de olhos amarelos brilhando numa janela escura (inveja)"""
    root = empty(name, None, (x, y, z)); root.scale = (s, s, s)
    for dx in (-0.11, 0.11):
        props.poly(f"{name}_o{dx}", [(dx + 0.07 * math.cos(2 * math.pi * i / 16) * 1.0, 0.045 * math.sin(2 * math.pi * i / 16)) for i in range(16)], cor, 0.0, root, strength=1.8)
        props.poly(f"{name}_p{dx}", circle(dx + 0.02, 0.0, 0.02, 8), "#2a1a00", -0.001, root)
    return root


def coroa(name, loc, s=1.0, cor="#ffc46a"):
    root = empty(name, None, loc); root.scale = (s, s, s)
    props.inked(name + "_b", [(-0.22, 0.0), (0.22, 0.0), (0.26, 0.28), (0.13, 0.15), (0.0, 0.32), (-0.13, 0.15), (-0.26, 0.28)], cor, root, w=0.0, rim=0.012, rim_color="#fff0c0", shade=0.015, shade_color=_mix(cor, "#000000", 0.35))
    for x in (-0.26, 0.0, 0.26):
        props.poly(f"{name}_p{x}", circle(x, 0.31 if x == 0 else 0.29, 0.03, 10), "#fff0c0", -0.002, root, strength=1.4)
    return root


def maco_pop(name, loc, s, t_pop, f0, desat=0.0, tamanho=1, zk=1.0):
    """um maço verde (G.maco) que aparece em t_pop; com desat > 0 fica apagado (cinza-esverdeado), sem destaque"""
    import grana as G
    antigo = props.DESAT
    props.DESAT = desat
    o = G.maco(name, loc, n=tamanho, s=s, zk=zk)
    props.DESAT = antigo
    props.blink_vis(o, [(f0, False), (t_pop - 1, False), (t_pop, True)], True)
    return o


def arco(o, f0, f1, p0, p1, alt=0.35, curva="easy"):
    """leva o objeto de p0 a p1 num arco (parábola), seguindo a curva (quadro a quadro)"""
    import curvas as C
    for f in range(f0, f1 + 1):
        u = (f - f0) / max(1, f1 - f0); s = C.s(curva, u)
        o.location = (p0[0] + (p1[0] - p0[0]) * s, p0[1] + (p1[1] - p0[1]) * s, p0[2] + (p1[2] - p0[2]) * s + alt * 4 * s * (1 - s))
        key(o, "location", f, "LINEAR")

# ---------------------------------------------------------------- profundidade: névoa entre camadas e primeiro plano
def neblina(p, y, alfa=0.18, cor=None, nome=None, z0=-1.0, z1=14.0, largura=40.0):
    """véu translúcido na profundidade y: tudo que fica atrás dele fica mais apagado (perspectiva atmosférica)"""
    nome = nome or f"neblina_{y:.2f}"
    m = cena.amat(nome + "_m", cor or _mix(p["mid"], p["top"], 0.2), 1.0, alfa)
    return cena.poly_mesh(nome, [(-largura, y, z0), (largura, y, z0), (largura, y, z1), (-largura, y, z1)], m)


def ombro(p, name, x, y, z, s=1.0, cor=None, flip=1):
    """ombro e cabeça de alguém de costas, bem perto da lente (primeiro plano por cima do ombro)"""
    cor = cor or _mix(p["top"], "#000000", 0.35)
    root = empty(name, None, (x, y, z)); root.scale = (s * flip, s, s)
    props.poly(name + "_corpo", [(-0.42, -0.6), (0.42, -0.6), (0.4, -0.05), (0.26, 0.12), (0.1, 0.16), (-0.1, 0.16), (-0.26, 0.12), (-0.4, -0.05)], cor, 0.0, root)
    props.poly(name + "_cab", circle(0.0, 0.42, 0.21, 32), cor, -0.001, root)
    props.poly(name + "_rim", stroke([(-0.3, 0.1), (-0.2, 0.15), (0.0, 0.18)], 0.012), p["borda"], -0.002, root)
    return root


def planta(p, name, x, y, z=0.0, s=1.0, cor=None):
    """vaso com folhas de silhueta (primeiro plano)"""
    cor = cor or _mix(p["top"], "#000000", 0.3)
    root = empty(name, None, (x, y, z)); root.scale = (s, s, s)
    props.poly(name + "_vaso", [(-0.18, 0.0), (0.18, 0.0), (0.22, 0.38), (-0.22, 0.38)], cor, 0.0, root)
    rnd = random.Random(int(abs(x) * 100) + 3)
    for i in range(9):
        a = math.radians(-70 + i * 17 + rnd.uniform(-6, 6)); L = rnd.uniform(0.55, 0.95)
        tip = (math.sin(a) * L, 0.38 + math.cos(a) * L)
        mid = (tip[0] * 0.5 + math.cos(a) * 0.09, 0.38 + (tip[1] - 0.38) * 0.5)
        props.poly(f"{name}_f{i}", [(0.0, 0.38), mid, tip, (tip[0] * 0.5 - math.cos(a) * 0.09, mid[1])], cor, -0.001 * i, root)
    return root


def coluna_fg(p, name, x, y, h=6.0, w=0.35, cor=None):
    """borda vertical escura bem perto da lente (moldura do quadro)"""
    cor = cor or _mix(p["top"], "#000000", 0.4)
    props.poly(name, cena.rect(x - w / 2, -1.0, x + w / 2, h), cor, y)
    props.poly(name + "_l", cena.rect(x + w / 2 - 0.02, -1.0, x + w / 2, h), p["borda"], y - 0.001)


def bokeh_fundo(p, name, y, x0, x1, z0, z1, n=14, cor=None, seed=3, r=(0.08, 0.2), alfa=0.35):
    """luzes de fundo desfocadas (discos grandes e suaves) para profundidade"""
    rnd = random.Random(seed)
    m = cena.amat(name + "_m", cor or p["luz"], 1.3, alfa, ("radial", 1.2))
    for i in range(n):
        cena.disc(f"{name}{i}", rnd.uniform(*r), m, (rnd.uniform(x0, x1), y, rnd.uniform(z0, z1)), n=24)


def mostra(o, intervalos, f_ini=-50):
    """liga/desliga um objeto (por escala) nos intervalos de quadros dados: [(fa, fb)]"""
    seq = [(f_ini, False)]
    for fa, fb in intervalos:
        seq += [(fa, True), (fb, False)]
    props.blink_vis(o, seq, True)
