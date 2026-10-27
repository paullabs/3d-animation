"""A balança GANHO × RISCO que acompanha a subida: coluna, travessão que inclina, dois pratos pendurados.
No prato GANHO caem maços de dinheiro; no prato RISCO caem pesos vermelhos. O travessão inclina para o lado mais pesado."""
import math
import lib
from lib import empty, key
import cena, props, dinheiro as D, curvas
from char2d import rrect
from puppet2d import circle

_mix = props._mix


def balanca(p, name, loc, s=1.0, braco=1.6):
    """devolve dict(raiz, travessao, prato_g, prato_r): os pratos ficam sempre na vertical (contra-giram o travessão)"""
    root = empty(name, None, loc); root.scale = (s, s, s)
    escuro = _mix(p["top"], "#000000", 0.25)
    props.inked(name + "_base", rrect(-0.55, 0.0, 0.55, 0.14, 0.05, 4), escuro, root, w=0.0, rim=0.02, rim_color=p["friso"])
    props.inked(name + "_col", rrect(-0.07, 0.1, 0.07, 2.2, 0.03, 3), escuro, root, w=0.0, rim=0.02, rim_color=p["friso"])
    props.inked(name + "_topo", circle(0, 2.25, 0.12, 32), p["friso"], root, w=0.0)
    trav = empty(name + "_trav", root, (0, -0.01, 2.2))
    props.inked(name + "_barra", rrect(-braco, -0.035, braco, 0.035, 0.03, 3), escuro, trav, w=0.0, rim=0.015, rim_color=p["friso"])
    pratos = {}
    for lado, sg, cor, rot in (("g", -1, p["friso"], "GANHO"), ("r", 1, "#e0484f", "RISCO")):
        piv = empty(f"{name}_piv{lado}", trav, (sg * braco, 0, 0))
        pr = empty(f"{name}_prato{lado}", piv, (0, 0, 0))
        for k in (-1, 1):
            props.poly(f"{name}_fio{lado}{k}", props.stroke([(0.0, 0.0), (k * 0.5, -1.05)], 0.008), p["friso"], 0.01, pr)
        props.inked(f"{name}_pr{lado}", [(-0.62, -1.05), (0.62, -1.05), (0.48, -1.2), (-0.48, -1.2)], escuro, pr, w=0.0, rim=0.02, rim_color=cor)
        props.txt(f"{name}_rot{lado}", rot, 0.26, cor, (0.0, -0.02, -1.5), pr, ink=None)
        pratos[lado] = (piv, pr)
    return dict(raiz=root, trav=trav, g=pratos["g"], r=pratos["r"])


def inclina(B, keys, curva="easy"):
    """keys = [(quadro, ângulo em graus)]; + = o lado do RISCO desce. Os pratos contra-giram e ficam na vertical."""
    ks = sorted(keys)
    for (fa, a0), (fb, a1) in zip(ks, ks[1:]):
        for f in range(fa, fb + 1):
            u = (f - fa) / max(1, fb - fa); a = a0 + (a1 - a0) * curvas.s(curva, u)
            B["trav"].rotation_euler = (0, math.radians(a), 0); key(B["trav"], "rotation_euler", f, "LINEAR")
            for lado in ("g", "r"):
                piv = B[lado][0]
                piv.rotation_euler = (0, -math.radians(a), 0); key(piv, "rotation_euler", f, "LINEAR")


def maco_no_prato(p, name, prato, f, x, nivel=0):
    """um maço de R$ 100 que cai no prato GANHO; devolve o objeto"""
    m = D.malha(name, D.molde_maco(True, True), [(0.0, 0.0)], s=2.2)
    m.parent = prato; m.location = (x, -0.03 - 0.002 * nivel, -1.05 + nivel * D.PASSO_Z * 2.2)
    z = m.location.z
    m.scale = (1, 1, 1)
    props.blink_vis(m, [(f - 40, False), (f - 1, False), (f, True)], True)
    m.location.z = z + 1.5; key(m, "location", f, "LINEAR")
    for i in range(1, 8):
        u = i / 7; m.location.z = z + 1.5 * (1 - u * u); key(m, "location", f + i, "LINEAR")
    return m


def peso_no_prato(p, name, prato, f, x, nivel=0, rotulo=""):
    """um peso vermelho (com um rótulo curto) que cai no prato RISCO"""
    w = empty(name, prato, (x, -0.03 - 0.002 * nivel, -1.05 + nivel * 0.3))
    props.inked(name + "_p", [(-0.26, 0.0), (0.26, 0.0), (0.18, 0.28), (-0.18, 0.28)], "#c8343c", w, w=0.0, rim=0.02, rim_color="#ff8a8f")
    props.inked(name + "_a", circle(0, 0.33, 0.06, 20), "#c8343c", w, w=0.0)
    if rotulo:
        props.txt(name + "_t", rotulo, 0.075, "#ffffff", (0, -0.01, 0.12), w, ink=None)
    z = w.location.z
    props.blink_vis(w, [(f - 40, False), (f - 1, False), (f, True)], True)
    w.location.z = z + 1.5; key(w, "location", f, "LINEAR")
    for i in range(1, 8):
        u = i / 7; w.location.z = z + 1.5 * (1 - u * u); key(w, "location", f + i, "LINEAR")
    return w