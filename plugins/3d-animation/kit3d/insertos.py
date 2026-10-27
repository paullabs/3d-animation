"""Objetos dos insertos (o objeto em foco em tela cheia): celular na mão, contador de dígitos girando."""
import bpy, math, random
import lib
from lib import empty, key
import cena, sets, props
from char2d import rrect, ellipse, taper
from puppet2d import circle

PELE, PELE_RIM = "#0d1020", "#3c4258"
MANGA, MANGA_SH = "#c62f35", "#8f1f27"


def celular(name, loc, s=1.0, tela="#dfe8f7"):
    """celular de verdade (7,6 x 15,6 cm) com conversa na tela; devolve (raiz, [balões em ordem de chegada])"""
    root = empty(name, None, loc); root.scale = (s, s, s)
    w, h = 0.038, 0.078
    props.inked(name + "_corpo", rrect(-w, -h, w, h, 0.009, 6), "#0c0e15", root, w=0.0015, rim=0.0016, rim_color="#4a5270")
    props.poly(name + "_tela", rrect(-w + 0.0035, -h + 0.0035, w - 0.0035, h - 0.0035, 0.006, 5), tela, -0.0006, root, strength=1.25)
    props.poly(name + "_topo", rrect(-w + 0.0035, h - 0.019, w - 0.0035, h - 0.0035, 0.006, 5), "#2a3148", -0.0009, root)
    props.poly(name + "_av", circle(-w + 0.011, h - 0.011, 0.0045, 20), "#8a93ad", -0.0012, root)
    props.poly(name + "_nome", rrect(-w + 0.019, h - 0.013, -w + 0.045, h - 0.009, 0.0015, 2), "#c9d0e4", -0.0012, root)
    props.poly(name + "_ilha", rrect(-0.008, h - 0.0075, 0.008, h - 0.0045, 0.0015, 2), "#05060a", -0.0014, root)
    baloes = []
    spec = [(-1, 0.040, 0.018), (1, 0.014, 0.014), (-1, -0.012, 0.018), (1, -0.040, 0.022)]
    for i, (lado, zc, hb) in enumerate(spec):
        bw = 0.05
        x0 = -w + 0.007 if lado < 0 else w - 0.007 - bw
        b = empty(f"{name}_bal{i}", root, (x0 + bw / 2, -0.0016, zc))
        cor = "#ffffff" if lado < 0 else "#bfe3ff"
        props.poly(f"{name}_bal{i}_f", rrect(-bw / 2, -hb / 2, bw / 2, hb / 2, 0.004, 4), cor, 0.0, b)
        for k in range(2 if hb > 0.015 else 1):
            zl = hb / 2 - 0.0055 - k * 0.0055
            props.poly(f"{name}_bal{i}_l{k}", rrect(-bw / 2 + 0.004, zl - 0.0012, bw / 2 - 0.004 - 0.012 * k, zl + 0.0012, 0.001, 2), "#7d869e", -0.0003, b)
        if lado > 0:
            for k in range(2):                                                       # dois "vistos" azuis
                x0c = bw / 2 - 0.0105 + 0.0028 * k; z0c = -hb / 2 + 0.0028
                props.poly(f"{name}_bal{i}_ok{k}", props.stroke([(x0c, z0c + 0.0012), (x0c + 0.0012, z0c), (x0c + 0.0034, z0c + 0.0026)], 0.00045), "#2f7fd8", -0.0004, b)
        baloes.append(b)
    return root, baloes


def mao_segura(name, parent, s=1.0):
    """mão preta do herói segurando o celular por baixo, com a manga vermelha saindo do quadro (coordenadas do celular)"""
    root = empty(name, parent, (0, 0, 0))
    props.inked(name + "_braco", [(0.03, -0.075), (0.095, -0.16), (0.16, -0.2), (0.2, -0.12), (0.075, -0.05)], PELE, root, loc=(0, 0.004, 0), w=0.0015, rim=0.003, rim_color=PELE_RIM)
    props.inked(name + "_punho", [(0.07, -0.125), (0.13, -0.215), (0.24, -0.2), (0.24, -0.1), (0.15, -0.09)], MANGA, root, loc=(0, 0.002, 0), w=0.0018, shade=0.008, shade_color=MANGA_SH)
    props.inked(name + "_palma", ellipse(0.022, -0.06, 0.035, 0.03, 32), PELE, root, loc=(0, 0.003, 0), w=0.0015, rim=0.003, rim_color=PELE_RIM)
    for i, zc in enumerate((-0.035, -0.012, 0.011)):                                   # dedos do lado esquerdo
        props.inked(f"{name}_dedo{i}", rrect(-0.046, zc - 0.0065, -0.03, zc + 0.0065, 0.006, 4), PELE, root, loc=(0, -0.003, 0), w=0.0012, rim=0.002, rim_color=PELE_RIM)
    props.inked(name + "_polegar", taper(0.05, -0.055, 0.009, 0.03, -0.012, 0.0075), PELE, root, loc=(0, -0.003, 0), w=0.0012, rim=0.002, rim_color=PELE_RIM)
    return root


def odometro(name, loc, F, t_gira, t_some, t_fim, s=1.0, texto="R$ 52.000.000.000", seed=3):
    """painel com o número em dígitos que giram (trocam a cada 2 quadros) e viram '?' um a um a partir de t_some"""
    rnd = random.Random(seed)
    root = empty(name, None, loc); root.scale = (s, s, s)
    chars = list(texto)
    cw = {".": 0.07, " ": 0.06}
    larg = sum(cw.get(ch, 0.16) for ch in chars)
    props.inked(name + "_pl", rrect(-larg / 2 - 0.12, -0.2, larg / 2 + 0.12, 0.2, 0.05, 6), "#0b0f1a", root, w=0.008, rim=0.006, rim_color="#2a3654")
    x = -larg / 2; slot = 0
    for ch in chars:
        wch = cw.get(ch, 0.16); xc = x + wch / 2; x += wch
        if not ch.isdigit():
            cor = "#ffd24a" if ch in "R$" else "#c9d3ea"
            props.txt(f"{name}_c{slot}_{ord(ch)}", ch, 0.2 if ch in "R$" else 0.24, cor, (xc, -0.004, -0.085), root, ink=None)
            continue
        props.poly(f"{name}_jan{slot}", rrect(xc - 0.07, -0.15, xc + 0.07, 0.15, 0.02, 3), "#151c2e", -0.002, root)
        objs = []
        for d in "0123456789?":
            t = props.txt(f"{name}_d{slot}_{d}", d, 0.24, "#ffd24a" if d == "?" else "#f4f6ff", (xc, -0.006, -0.085), root, ink=None)
            objs.append(t)
        f = F(t_gira) - 1
        fq = F(t_some) + slot * 1
        cur = None
        while f <= F(t_fim) + 2:
            dg = 10 if f >= fq else rnd.randrange(10)
            if dg != cur:
                for k, o in enumerate(objs):
                    props.blink_vis(o, [(f, k == dg)], True)
                cur = dg
            f += 2 if f < fq else 200
        for k, o in enumerate(objs):            # antes de girar: tudo apagado
            props.blink_vis(o, [(F(t_gira) - 30, False)], True)
        slot += 1
    return root