"""Objetos do canal com acabamento de ficha (contorno de tinta, sombra e brilho por dentro, como o boneco).
Todos desenhados de frente (plano XZ), com origem no centro da base, para ficarem em pé na cena ou sobre a mesa.
O que é dinheiro está em unidades.py (notinha, maço, cubo, cubo_mil)."""
import math
import cena, props
from props import _mix
from lib import empty
from char2d import rrect
from puppet2d import circle, stroke

TINTA = "#14110e"


def envelope(nm, loc, s=1.0, parent=None, cor="#f4efe6"):
    r = empty(nm, parent, loc); r.scale = (s, s, s)
    props.inked(nm + "_c", rrect(-0.12, 0.0, 0.12, 0.16, 0.012, 3), cor, r, w=0.007, shade=0.012, shade_color=_mix(cor, "#000000", 0.12), rim=0.006, rim_color="#ffffff")
    props.poly(nm + "_aba", [(-0.12, 0.16), (0.0, 0.07), (0.12, 0.16)], _mix(cor, "#000000", 0.18), -0.003, r)
    props.poly(nm + "_selo", circle(0.0, 0.085, 0.018, 18), "#a8323a", -0.005, r)
    return r


def contrato(nm, loc, s=1.0, parent=None):
    r = empty(nm, parent, loc); r.scale = (s, s, s)
    props.inked(nm + "_f", rrect(-0.22, 0.0, 0.22, 0.6, 0.01, 2), "#f7f3ea", r, w=0.007, shade=0.012, shade_color="#e2dccd")
    props.poly(nm + "_tit", cena.rect(-0.15, 0.52, 0.15, 0.545), "#2a3550", -0.003, r)
    for k in range(8):
        props.poly(f"{nm}_l{k}", cena.rect(-0.17, 0.44 - k * 0.04, 0.17 - 0.05 * (k % 3), 0.452 - k * 0.04), "#a3a9b5", -0.003, r)
    props.poly(nm + "_ass", stroke([(-0.15, 0.08), (-0.1, 0.11), (-0.06, 0.07), (0.0, 0.1), (0.04, 0.08)], 0.005), "#1a2a6a", -0.004, r)
    props.poly(nm + "_lin", cena.rect(-0.17, 0.065, 0.06, 0.07), "#5a6070", -0.003, r)
    props.poly(nm + "_selo", circle(0.13, 0.09, 0.045, 24), "#b8323a", -0.004, r)
    props.poly(nm + "_selo2", circle(0.13, 0.09, 0.03, 24), "#d84a4a", -0.005, r)
    return r


def estojo_joias(nm, loc, s=1.0, parent=None, aberto=True):
    """estojo aberto com colar e anel brilhando (as joias do presente)"""
    r = empty(nm, parent, loc); r.scale = (s, s, s)
    props.inked(nm + "_tampa", rrect(-0.2, 0.17, 0.2, 0.36, 0.03, 4), "#3a1a2a", r, w=0.01, shade=0.015, shade_color="#2a1020", rim=0.008, rim_color="#e8c76a")
    props.poly(nm + "_veludo", rrect(-0.17, 0.2, 0.17, 0.33, 0.02, 3), "#5a2a46", -0.003, r)
    props.inked(nm + "_base", rrect(-0.22, 0.0, 0.22, 0.17, 0.03, 4), "#3a1a2a", r, w=0.01, shade=0.015, shade_color="#2a1020", rim=0.008, rim_color="#e8c76a")
    colar = [(0.12 * math.cos(math.radians(a)), 0.27 + 0.05 * math.sin(math.radians(a))) for a in range(200, 341, 10)]
    props.poly(nm + "_colar", stroke(colar, 0.008), "#ffe08a", -0.006, r)
    for k, a in enumerate(range(210, 331, 30)):
        props.poly(f"{nm}_g{k}", circle(0.12 * math.cos(math.radians(a)), 0.27 + 0.05 * math.sin(math.radians(a)), 0.016, 14), "#fff4c8", -0.008, r)
    props.poly(nm + "_pingente", circle(0.0, 0.205, 0.026, 18), "#bfe8ff", -0.008, r)
    props.poly(nm + "_anel", circle(0.0, 0.1, 0.04, 24), "#ffe08a", -0.006, r)
    props.poly(nm + "_anel_f", circle(0.0, 0.1, 0.027, 24), "#3a1a2a", -0.007, r)
    props.poly(nm + "_anel_p", circle(0.0, 0.142, 0.018, 16), "#ffffff", -0.008, r)
    gl = cena.disc(nm + "_gl", 0.35 * s, cena.amat(nm + "_gl_m", "#ffd27a", 1.2, 0.35, ("radial", 1.4)), (loc[0], loc[1] + 0.02, loc[2] + 0.25 * s))
    return r


def mochila(nm, loc, s=1.0, parent=None):
    r = empty(nm, parent, loc); r.scale = (s, s, s)
    props.inked(nm + "_c", rrect(-0.2, 0.0, 0.2, 0.48, 0.09, 6), "#2b3240", r, w=0.012, shade=0.03, shade_color="#1c2230", rim=0.012, rim_color="#d8f7ff")
    props.inked(nm + "_t", rrect(-0.2, 0.32, 0.2, 0.5, 0.07, 5), "#3a4356", r, loc=(0, -0.004, 0), w=0.012)
    props.poly(nm + "_bolso", rrect(-0.13, 0.06, 0.13, 0.24, 0.04, 4), "#232a37", -0.006, r)
    props.poly(nm + "_ziper", cena.rect(-0.12, 0.215, 0.12, 0.225), "#9aa3b0", -0.008, r)
    props.poly(nm + "_alca", stroke([(-0.06, 0.5), (-0.04, 0.56), (0.04, 0.56), (0.06, 0.5)], 0.012), "#1c2230", 0.002, r)
    return r


def calendario(nm, loc, s=1.0, parent=None):
    r = empty(nm, parent, loc); r.scale = (s, s, s)
    props.inked(nm + "_b", rrect(-0.42, 0.0, 0.42, 1.0, 0.04, 4), "#f6f1e4", r, w=0.012, shade=0.02, shade_color="#ddd5c2")
    props.poly(nm + "_topo", rrect(-0.42, 0.8, 0.42, 1.0, 0.04, 4), "#c8323e", -0.003, r)
    for k in range(5):
        props.poly(f"{nm}_ar{k}", circle(-0.3 + k * 0.15, 0.97, 0.022, 14), "#5a5f6e", -0.005, r)
    for i in range(7):
        for j in range(4):
            props.poly(f"{nm}_d{i}{j}", rrect(-0.37 + i * 0.105, 0.6 - j * 0.15, -0.29 + i * 0.105, 0.72 - j * 0.15, 0.01, 2), "#e6dfcd", -0.003, r)
    return r


def livro(nm, loc, s=1.0, parent=None, cor="#5a2a46"):
    """o livro do orçamento, aberto e em pé (lombada no meio)"""
    r = empty(nm, parent, loc); r.scale = (s, s, s)
    props.inked(nm + "_capa", rrect(-0.5, -0.02, 0.5, 0.46, 0.02, 3), cor, r, loc=(0, 0.004, 0), w=0.01)
    for sgn in (-1, 1):
        props.inked(f"{nm}_pag{sgn}", rrect(min(0, 0.47 * sgn), 0.0, max(0, 0.47 * sgn), 0.42, 0.01, 2), "#f6efe0", r, w=0.006, shade=0.01, shade_color="#e2d8c2")
        for k in range(7):
            x0, x1 = (0.05, 0.4) if sgn > 0 else (-0.42, -0.07)
            props.poly(f"{nm}_l{sgn}{k}", cena.rect(x0, 0.34 - k * 0.042, x1 - 0.06 * (k % 2), 0.352 - k * 0.042), "#8a7f9a", -0.004, r)
    props.poly(nm + "_lombada", cena.rect(-0.008, 0.0, 0.008, 0.42), "#c2b49a", -0.005, r)
    return r


def retrato(nm, loc, s=1.0, parent=None, fundo="#e6dcc6", pessoa="#1d2230"):
    """retrato oficial sem rosto (ninguém real): moldura de madeira com filete dourado"""
    r = empty(nm, parent, loc); r.scale = (s, s, s)
    props.inked(nm + "_m", rrect(-0.42, -0.52, 0.42, 0.52, 0.03, 4), "#7a4e30", r, w=0.012, shade=0.02, shade_color="#5a3820", rim=0.012, rim_color="#e8c76a")
    props.poly(nm + "_f", rrect(-0.35, -0.45, 0.35, 0.45, 0.02, 3), fundo, -0.003, r)
    props.poly(nm + "_c", circle(0, 0.05, 0.13, 32), pessoa, -0.005, r)
    props.poly(nm + "_o", rrect(-0.24, -0.45, 0.24, -0.12, 0.1, 6), pessoa, -0.005, r)
    props.poly(nm + "_faixa", [(-0.2, -0.13), (-0.12, -0.13), (0.2, -0.43), (0.12, -0.45)], "#1f9d55", -0.006, r)
    return r


def telao_bolsa(nm, loc, empresa="PETROBRAS", s=1.0, parent=None):
    """telão de cotação: nome da empresa (texto, não o logotipo), gráfico que despenca e seta vermelha"""
    r = empty(nm, parent, loc); r.scale = (s, s, s)
    props.inked(nm + "_mold", rrect(-2.0, 0.0, 2.0, 2.3, 0.05, 4), "#0a1220", r, w=0.03, rim=0.02, rim_color="#5a6a82")
    props.poly(nm + "_tela", rrect(-1.9, 0.1, 1.9, 2.2, 0.04, 4), "#0e1a2e", -0.003, r)
    props.txt(nm + "_nome", empresa, 0.26, "#f2f4f8", (-0.85, -0.006, 1.92), r, align="CENTER", ink=None)
    props.poly(nm + "_marca", cena.rect(-1.75, 1.8, -1.65, 2.05), "#1f9d55", -0.006, r)
    props.poly(nm + "_marca2", cena.rect(-1.62, 1.8, -1.55, 2.05), "#f2c94c", -0.006, r)
    for k in range(5):
        props.poly(f"{nm}_g{k}", cena.rect(-1.75, 0.35 + k * 0.3, 1.75, 0.36 + k * 0.3), "#1c2a42", -0.004, r)
    pts = [(-1.7, 1.45), (-1.2, 1.5), (-0.8, 1.38), (-0.4, 1.42), (0.0, 1.1), (0.4, 0.85), (0.8, 0.6), (1.2, 0.45), (1.6, 0.3)]
    segs = []
    for k in range(len(pts) - 1):
        segs.append(props.poly(f"{nm}_s{k}", stroke([pts[k], pts[k + 1]], 0.03), "#ff4a52", -0.007, r, strength=1.4))
    props.poly(nm + "_seta", [(1.45, 0.62), (1.85, 0.62), (1.65, 0.3)], "#ff4a52", -0.008, r, strength=1.4)
    return r, segs


def faixa_presidencial(nm, loc, s=1.0, parent=None):
    r = empty(nm, parent, loc); r.scale = (s, s, s)
    props.poly(nm + "_a", [(-0.07, 0.0), (0.07, 0.0), (0.13, -0.95), (0.01, -0.98)], "#f2c94c", 0.0, r)
    props.poly(nm + "_v", [(-0.06, 0.0), (0.06, 0.0), (0.12, -0.94), (0.02, -0.96)], "#1f9d55", -0.002, r)
    props.poly(nm + "_br", circle(0.05, -0.5, 0.035, 18), "#f2c94c", -0.004, r)
    return r


# ================================================================ novos objetos (ficha v2): dinheiro escondido, poder, prova e castigo
import unidades as UN


def _q(nm, pts, cor):
    return cena.poly_mesh(nm, pts, props.FM(cor))


def caixa(nm, x, y, z, w, h, d, frente, tampo=None, lado=None, aresta=None):
    """caixa 3D simples (frente, tampo e as duas laterais), origem no centro da frente embaixo"""
    tampo = tampo or _mix(frente, "#ffffff", 0.18); lado = lado or _mix(frente, "#000000", 0.25)
    _q(nm + "_f", [(x - w / 2, y, z), (x + w / 2, y, z), (x + w / 2, y, z + h), (x - w / 2, y, z + h)], frente)
    _q(nm + "_t", [(x - w / 2, y, z + h), (x + w / 2, y, z + h), (x + w / 2, y + d, z + h), (x - w / 2, y + d, z + h)], tampo)
    for s in (-1, 1):
        _q(f"{nm}_l{s}", [(x + s * w / 2, y, z), (x + s * w / 2, y + d, z), (x + s * w / 2, y + d, z + h), (x + s * w / 2, y, z + h)], lado)
    if aresta:
        _q(nm + "_a", [(x - w / 2, y - 0.002, z + h - 0.01), (x + w / 2, y - 0.002, z + h - 0.01), (x + w / 2, y - 0.002, z + h), (x - w / 2, y - 0.002, z + h)], aresta)


def maletinha_dinheiro(nm, loc, s=1.0):
    """maleta executiva aberta, cheia de maços (tampa levantada atrás)"""
    x, y, z = loc
    caixa(nm + "_tampa", x, y + 0.32 * s, z + 0.1 * s, 0.62 * s, 0.4 * s, 0.03 * s, "#3a2416", aresta="#c9a45a")
    caixa(nm + "_base", x, y, z, 0.62 * s, 0.12 * s, 0.34 * s, "#4a2e1c", tampo="#2a1a10", aresta="#c9a45a")
    for i in range(4):
        for j in range(2):
            UN.cubo(f"{nm}_m{i}{j}", (x - 0.21 * s + i * 0.14 * s, y + 0.06 * s + j * 0.12 * s, z + 0.12 * s), 0.11 * s, linhas=4)
    _q(nm + "_fecho", [(x - 0.04 * s, y - 0.003, z + 0.05 * s), (x + 0.04 * s, y - 0.003, z + 0.05 * s), (x + 0.04 * s, y - 0.003, z + 0.09 * s), (x - 0.04 * s, y - 0.003, z + 0.09 * s)], "#e8c76a")


def mala_dinheiro(nm, loc, s=1.0):
    """mala de rodinhas aberta, transbordando de maços (os casos de dinheiro escondido em malas)"""
    x, y, z = loc
    caixa(nm + "_c", x, y, z + 0.06 * s, 0.5 * s, 0.7 * s, 0.26 * s, "#2c3a52", tampo="#1c2638", aresta="#8aa0c0")
    for k in range(3):
        _q(f"{nm}_fr{k}", [(x - 0.25 * s + 0.12 * s * (k + 1) - 0.006, y - 0.002, z + 0.08 * s), (x - 0.25 * s + 0.12 * s * (k + 1) + 0.006, y - 0.002, z + 0.08 * s),
                            (x - 0.25 * s + 0.12 * s * (k + 1) + 0.006, y - 0.002, z + 0.74 * s), (x - 0.25 * s + 0.12 * s * (k + 1) - 0.006, y - 0.002, z + 0.74 * s)], "#1c2638")
    for k in range(3):
        for j in range(2):
            UN.cubo(f"{nm}_m{k}{j}", (x - 0.15 * s + k * 0.15 * s, y + 0.05 * s + j * 0.12 * s, z + 0.76 * s), 0.12 * s, linhas=4)
    UN.cubo(f"{nm}_mt", (x + 0.02 * s, y + 0.1 * s, z + 0.88 * s), 0.12 * s, linhas=4)
    for sx in (-1, 1):
        props.poly(f"{nm}_roda{sx}", circle(x + sx * 0.18 * s, z + 0.04 * s, 0.04 * s, 16), "#101318", y - 0.01)
    props.poly(nm + "_puxador", cena.rect(x - 0.12 * s, z + 0.76 * s, x - 0.1 * s, z + 1.0 * s), "#8aa0c0", y + 0.24 * s)
    props.poly(nm + "_puxador_t", cena.rect(x - 0.12 * s, z + 0.98 * s, x + 0.12 * s, z + 1.01 * s), "#8aa0c0", y + 0.24 * s)


def caixa_papelao(nm, loc, s=1.0):
    x, y, z = loc
    caixa(nm, x, y, z, 0.6 * s, 0.42 * s, 0.4 * s, "#b07a45", tampo="#c8925a", lado="#8a5a30")
    for k in range(3):
        UN.cubo(f"{nm}_m{k}", (x - 0.15 * s + k * 0.15 * s, y + 0.15 * s, z + 0.42 * s), 0.13 * s, linhas=4)
    _q(nm + "_aba1", [(x - 0.3 * s, y, z + 0.42 * s), (x, y, z + 0.42 * s), (x - 0.06 * s, y - 0.12 * s, z + 0.55 * s), (x - 0.34 * s, y - 0.1 * s, z + 0.5 * s)], "#c8925a")
    _q(nm + "_fita", [(x - 0.03 * s, y - 0.002, z + 0.2 * s), (x + 0.03 * s, y - 0.002, z + 0.2 * s), (x + 0.03 * s, y - 0.002, z + 0.42 * s), (x - 0.03 * s, y - 0.002, z + 0.42 * s)], "#d8c8a0")


def cofre(nm, loc, s=1.0):
    """cofre de aço com a porta aberta e prateleiras de maços"""
    x, y, z = loc
    caixa(nm + "_c", x, y + 0.05 * s, z, 0.7 * s, 0.9 * s, 0.6 * s, "#3a4250", tampo="#4a5464", lado="#2a303a")
    _q(nm + "_dentro", [(x - 0.3 * s, y + 0.045 * s, z + 0.06 * s), (x + 0.3 * s, y + 0.045 * s, z + 0.06 * s), (x + 0.3 * s, y + 0.045 * s, z + 0.84 * s), (x - 0.3 * s, y + 0.045 * s, z + 0.84 * s)], "#1a1e26")
    for r in range(3):
        for i in range(4):
            UN.cubo(f"{nm}_m{r}{i}", (x - 0.21 * s + i * 0.14 * s, y + 0.12 * s, z + 0.08 * s + r * 0.26 * s), 0.12 * s, linhas=4)
    # a porta aberta (girada para a esquerda, vista de lado)
    _q(nm + "_porta", [(x - 0.35 * s, y + 0.04 * s, z + 0.02 * s), (x - 0.5 * s, y - 0.5 * s, z + 0.02 * s), (x - 0.5 * s, y - 0.5 * s, z + 0.88 * s), (x - 0.35 * s, y + 0.04 * s, z + 0.88 * s)], "#5a6476")
    _q(nm + "_porta_borda", [(x - 0.5 * s, y - 0.5 * s, z + 0.02 * s), (x - 0.53 * s, y - 0.49 * s, z + 0.02 * s), (x - 0.53 * s, y - 0.49 * s, z + 0.88 * s), (x - 0.5 * s, y - 0.5 * s, z + 0.88 * s)], "#2a303a")
    props.poly(nm + "_roda", circle(x - 0.44 * s, z + 0.45 * s, 0.05 * s, 20), "#c8ccd6", y - 0.3 * s)


def tornozeleira(nm, loc, s=1.0):
    """tornozeleira eletrônica: tira preta e caixinha com a luz verde"""
    r = empty(nm, None, loc); r.scale = (s, s, s)
    props.inked(nm + "_tira", rrect(-0.14, 0.0, 0.14, 0.07, 0.03, 4), "#1a1c22", r, w=0.008, rim=0.006, rim_color="#6a7080")
    props.inked(nm + "_cx", rrect(-0.07, -0.03, 0.07, 0.1, 0.02, 4), "#2a2d36", r, loc=(0, -0.004, 0), w=0.008, shade=0.01, shade_color="#1a1c22", rim=0.006, rim_color="#8a90a0")
    props.poly(nm + "_led", circle(0.035, 0.065, 0.012, 12), "#5cf07a", -0.01, r, strength=1.6)
    return r


def algemas(nm, loc, s=1.0):
    r = empty(nm, None, loc); r.scale = (s, s, s)
    for sx in (-1, 1):
        aro = [(sx * 0.1 + 0.07 * math.cos(math.radians(a)), 0.08 + 0.07 * math.sin(math.radians(a))) for a in range(0, 361, 12)]
        props.poly(f"{nm}_aro{sx}", stroke(aro, 0.014), "#c8ccd6", -0.002 * (sx + 2), r)
    props.poly(nm + "_corr", stroke([(-0.035, 0.1), (0.0, 0.085), (0.035, 0.1)], 0.01), "#9aa0ac", -0.006, r)
    return r


def tribuna(nm, loc, s=1.0, mics=5):
    """púlpito de discurso com vários microfones de imprensa (cada um com uma cor de emissora, sem marca)"""
    x, y, z = loc
    caixa(nm, x, y, z, 0.7 * s, 1.05 * s, 0.4 * s, "#3a2a20", tampo="#5a4232", aresta="#c9a45a")
    props.poly(nm + "_bras", circle(x, z + 0.65 * s, 0.12 * s, 32), "#e8c76a", y - 0.003)
    props.poly(nm + "_bras2", circle(x, z + 0.65 * s, 0.09 * s, 32), "#1f6b4a", y - 0.004)
    cores = ["#c8323e", "#2a6ad8", "#f2f2ee", "#1f9d55", "#f29a2e"]
    for k in range(mics):
        a = -0.5 + k / max(1, mics - 1)
        mx = x + a * 0.24 * s
        props.poly(f"{nm}_haste{k}", stroke([(mx, z + 1.0 * s), (mx + a * 0.05 * s, z + 1.22 * s)], 0.008 * s), "#1a1c22", y - 0.02)
        props.poly(f"{nm}_mic{k}", rrect(mx + a * 0.05 * s - 0.03 * s, z + 1.2 * s, mx + a * 0.05 * s + 0.03 * s, z + 1.32 * s, 0.015 * s, 3), "#1a1c22", y - 0.025)
        props.poly(f"{nm}_cubo{k}", rrect(mx + a * 0.05 * s - 0.035 * s, z + 1.15 * s, mx + a * 0.05 * s + 0.035 * s, z + 1.2 * s, 0.006 * s, 2), cores[k % 5], y - 0.03)


def camera_tv(nm, loc, s=1.0):
    r = empty(nm, None, loc); r.scale = (s, s, s)
    for sx in (-1, 0, 1):
        props.poly(f"{nm}_tripe{sx}", stroke([(0.0, 0.85), (sx * 0.28, 0.0)], 0.014), "#1a1c22", 0.01, r)
    props.inked(nm + "_corpo", rrect(-0.22, 0.85, 0.24, 1.12, 0.03, 4), "#2a2d36", r, w=0.01, shade=0.02, shade_color="#1a1c22", rim=0.008, rim_color="#8a90a0")
    props.inked(nm + "_lente", rrect(0.24, 0.9, 0.38, 1.07, 0.02, 3), "#1a1c22", r, w=0.01)
    props.poly(nm + "_vidro", circle(0.38, 0.985, 0.06, 20), "#5a8ad8", -0.004, r)
    props.poly(nm + "_rec", circle(-0.16, 1.07, 0.014, 12), "#ff3b4a", -0.004, r, strength=1.5)
    props.poly(nm + "_alca", stroke([(-0.12, 1.12), (-0.08, 1.18), (0.12, 1.18), (0.16, 1.12)], 0.012), "#1a1c22", 0.002, r)
    return r


def celular(nm, loc, s=1.0):
    """celular com uma conversa (balões, sem texto legível)"""
    r = empty(nm, None, loc); r.scale = (s, s, s)
    props.inked(nm + "_c", rrect(-0.085, 0.0, 0.085, 0.34, 0.022, 5), "#16181e", r, w=0.008, rim=0.006, rim_color="#8a90a0")
    props.poly(nm + "_tela", rrect(-0.072, 0.02, 0.072, 0.32, 0.014, 4), "#e8edf2", -0.003, r)
    for k, (x0, x1, cor) in enumerate(((-0.06, 0.02, "#d8dde4"), (-0.01, 0.06, "#9ae0a8"), (-0.06, 0.03, "#d8dde4"), (0.0, 0.06, "#9ae0a8"))):
        props.poly(f"{nm}_b{k}", rrect(x0, 0.24 - k * 0.055, x1, 0.28 - k * 0.055, 0.012, 3), cor, -0.005, r)
    return r


def carimbo(nm, loc, s=1.0):
    r = empty(nm, None, loc); r.scale = (s, s, s)
    props.inked(nm + "_cabo", rrect(-0.03, 0.12, 0.03, 0.26, 0.03, 4), "#6a3a22", r, w=0.008, rim=0.006, rim_color="#c8925a")
    props.inked(nm + "_base", rrect(-0.08, 0.05, 0.08, 0.12, 0.01, 2), "#3a2416", r, w=0.008)
    props.inked(nm + "_borr", rrect(-0.085, 0.02, 0.085, 0.05, 0.006, 2), "#b8323a", r, w=0.006)
    props.inked(nm + "_marca", rrect(-0.14, -0.02, 0.14, 0.0, 0.004, 2), "#c84a52", r, loc=(0.25, 0, 0), w=0.0)
    return r


def relogio_luxo(nm, loc, s=1.0):
    r = empty(nm, None, loc); r.scale = (s, s, s)
    props.poly(nm + "_pulso", rrect(-0.035, -0.12, 0.035, 0.12, 0.02, 3), "#d9b45a", 0.002, r)
    props.inked(nm + "_caixa", circle(0, 0, 0.06, 32), "#e8c76a", r, w=0.008, rim=0.008, rim_color="#fff2c8")
    props.poly(nm + "_mostrador", circle(0, 0, 0.045, 32), "#1a1c22", -0.003, r)
    props.poly(nm + "_p1", stroke([(0, 0), (0.0, 0.032)], 0.004), "#f2f2ee", -0.005, r)
    props.poly(nm + "_p2", stroke([(0, 0), (0.024, -0.01)], 0.004), "#f2f2ee", -0.005, r)
    for k in range(4):
        a = math.radians(45 + 90 * k)
        props.poly(f"{nm}_d{k}", circle(0.052 * math.cos(a), 0.052 * math.sin(a), 0.006, 8), "#ffffff", -0.004, r)
    return r


def champanhe(nm, loc, s=1.0):
    r = empty(nm, None, loc); r.scale = (s, s, s)
    props.inked(nm + "_garrafa", [(-0.05, 0.0), (0.05, 0.0), (0.055, 0.22), (0.02, 0.3), (0.018, 0.38), (-0.018, 0.38), (-0.02, 0.3), (-0.055, 0.22)],
                "#1f4a2a", r, w=0.008, shade=0.012, shade_color="#143220", rim=0.008, rim_color="#8ae0a8")
    props.poly(nm + "_rotulo", rrect(-0.045, 0.08, 0.045, 0.16, 0.008, 2), "#e8d8a8", -0.004, r)
    props.poly(nm + "_lacre", rrect(-0.022, 0.32, 0.022, 0.39, 0.006, 2), "#e8c76a", -0.004, r)
    for sx in (-1, 1):
        x0 = sx * 0.13
        props.poly(f"{nm}_taca{sx}", [(x0 - 0.04, 0.26), (x0 + 0.04, 0.26), (x0 + 0.01, 0.15), (x0 + 0.006, 0.02), (x0 + 0.04, 0.0), (x0 - 0.04, 0.0), (x0 - 0.006, 0.02), (x0 - 0.01, 0.15)],
                   "#d8eef2", 0.0, r)
        props.poly(f"{nm}_vinho{sx}", [(x0 - 0.034, 0.24), (x0 + 0.034, 0.24), (x0 + 0.01, 0.16), (x0 - 0.01, 0.16)], "#f2d27a", -0.002, r)
    return r


def charuto(nm, loc, s=1.0):
    r = empty(nm, None, loc); r.scale = (s, s, s)
    props.inked(nm + "_cinz", rrect(-0.12, 0.0, 0.12, 0.05, 0.02, 3), "#5a4a3a", r, w=0.008, rim=0.006, rim_color="#c8b090")
    props.poly(nm + "_ch", rrect(-0.1, 0.05, 0.12, 0.08, 0.015, 3), "#7a4a2a", -0.003, r)
    props.poly(nm + "_anel", rrect(0.04, 0.05, 0.065, 0.08, 0.003, 1), "#c8323e", -0.005, r)
    props.poly(nm + "_brasa", circle(-0.1, 0.065, 0.014, 12), "#ff7a3a", -0.006, r, strength=1.6)
    for k in range(3):
        props.poly(f"{nm}_fumo{k}", stroke([(-0.11, 0.09 + k * 0.05), (-0.13 + 0.03 * (k % 2), 0.12 + k * 0.05)], 0.008), "#c8c8d0", -0.002, r)
    return r


def cadeira_presidencial(nm, loc, s=1.0):
    r = empty(nm, None, loc); r.scale = (s, s, s)
    props.inked(nm + "_encosto", rrect(-0.32, 0.5, 0.32, 1.45, 0.12, 8), "#5a1a22", r, w=0.014, shade=0.03, shade_color="#40121a", rim=0.012, rim_color="#e8c76a")
    for i in range(3):
        for j in range(4):
            props.poly(f"{nm}_capit{i}{j}", circle(-0.18 + i * 0.18, 0.7 + j * 0.2, 0.015, 10), "#2a0a10", -0.005, r)
    props.inked(nm + "_assento", rrect(-0.38, 0.42, 0.38, 0.56, 0.05, 4), "#6a2028", r, loc=(0, -0.01, 0), w=0.012)
    for sx in (-1, 1):
        props.inked(f"{nm}_braco{sx}", rrect(sx * 0.33 - 0.06, 0.42, sx * 0.33 + 0.06, 0.78, 0.04, 4), "#40121a", r, loc=(0, -0.015, 0), w=0.01)
    props.poly(nm + "_pe", cena.rect(-0.03, 0.08, 0.03, 0.42), "#1a1c22", 0.01, r)
    props.poly(nm + "_base", rrect(-0.3, 0.0, 0.3, 0.08, 0.03, 3), "#1a1c22", 0.012, r)
    return r


def bandeira_brasil(nm, loc, s=1.0):
    r = empty(nm, None, loc); r.scale = (s, s, s)
    props.poly(nm + "_mastro", cena.rect(-0.02, 0.0, 0.02, 2.4), "#c8ccd6", 0.01, r)
    props.poly(nm + "_ponta", circle(0.0, 2.43, 0.04, 16), "#e8c76a", 0.009, r)
    pano = [(0.02 + 0.9 * k / 10, 2.3 - 0.03 * math.sin(k * 0.8)) for k in range(11)] + [(0.02 + 0.9 * k / 10, 1.7 - 0.03 * math.sin(k * 0.8)) for k in range(10, -1, -1)]
    props.poly(nm + "_verde", pano, "#1f9d55", 0.0, r)
    props.poly(nm + "_losango", [(0.12, 2.0), (0.47, 2.24), (0.82, 2.0), (0.47, 1.76)], "#f2c94c", -0.002, r)
    props.poly(nm + "_circ", circle(0.47, 2.0, 0.15, 32), "#2a4aa8", -0.004, r)
    props.poly(nm + "_faixa_b", [(0.33, 2.04), (0.61, 1.98), (0.61, 2.0), (0.33, 2.06)], "#f6f4ee", -0.006, r)
    return r


def notebook(nm, loc, s=1.0):
    """notebook aberto com uma planilha (colunas e células verdes de dinheiro)"""
    r = empty(nm, None, loc); r.scale = (s, s, s)
    props.inked(nm + "_tela", rrect(-0.3, 0.06, 0.3, 0.46, 0.02, 3), "#1a1c22", r, w=0.01, rim=0.008, rim_color="#8a90a0")
    props.poly(nm + "_vid", rrect(-0.27, 0.09, 0.27, 0.43, 0.01, 2), "#f2f4f8", -0.003, r)
    for i in range(5):
        for j in range(6):
            cor = "#a8e0b0" if (i == 4) else ("#d8dde6" if j % 2 else "#e8ecf2")
            props.poly(f"{nm}_c{i}{j}", cena.rect(-0.26 + i * 0.105, 0.38 - j * 0.05, -0.16 + i * 0.105, 0.42 - j * 0.05), cor, -0.005, r)
    props.inked(nm + "_base", [(-0.34, 0.0), (0.34, 0.0), (0.3, 0.06), (-0.3, 0.06)], "#8a90a0", r, loc=(0, -0.01, 0), w=0.01)
    return r


def pasta_confidencial(nm, loc, s=1.0):
    r = empty(nm, None, loc); r.scale = (s, s, s)
    props.inked(nm + "_c", rrect(-0.24, 0.0, 0.24, 0.34, 0.012, 3), "#c9a26a", r, w=0.008, shade=0.012, shade_color="#a8844e", rim=0.006, rim_color="#ecd2a0")
    props.poly(nm + "_aba", rrect(-0.24, 0.3, -0.05, 0.37, 0.01, 2), "#b8925a", 0.002, r)
    props.poly(nm + "_tarja", [(-0.2, 0.1), (0.2, 0.22), (0.2, 0.27), (-0.2, 0.15)], "#c8323e", -0.004, r)
    for k in range(3):
        props.poly(f"{nm}_l{k}", cena.rect(-0.18, 0.05 + k * 0.03, 0.05, 0.06 + k * 0.03), "#8a6a3a", -0.004, r)
    return r


def carrinho_dinheiro(nm, loc, s=1.0):
    x, y, z = loc
    props.poly(nm + "_roda", circle(x + 0.45 * s, z + 0.12 * s, 0.12 * s, 24), "#1a1c22", y - 0.02)
    props.poly(nm + "_aro", circle(x + 0.45 * s, z + 0.12 * s, 0.05 * s, 16), "#8a90a0", y - 0.03)
    _q(nm + "_cacamba", [(x - 0.45 * s, y, z + 0.25 * s), (x + 0.4 * s, y, z + 0.25 * s), (x + 0.52 * s, y, z + 0.55 * s), (x - 0.5 * s, y, z + 0.55 * s)], "#2a6a8a")
    for sx in (-1, 1):
        props.poly(f"{nm}_cabo{sx}", stroke([(x - 0.45 * s, z + 0.4 * s), (x - 0.95 * s, z + 0.55 * s)], 0.02 * s), "#6a4a2a", y + 0.05 * sx)
    props.poly(nm + "_pe", stroke([(x - 0.35 * s, z + 0.26 * s), (x - 0.38 * s, z)], 0.02 * s), "#1a1c22", y - 0.01)
    for k in range(5):
        for j in range(2):
            UN.cubo(f"{nm}_m{k}{j}", (x - 0.34 * s + k * 0.17 * s, y + 0.12 * s, z + 0.55 * s + j * 0.15 * s), 0.14 * s, linhas=4)


def jatinho(nm, loc, s=1.0):
    r = empty(nm, None, loc); r.scale = (s, s, s)
    corpo = [(-1.3, 0.25), (0.9, 0.25), (1.35, 0.4), (1.3, 0.52), (0.85, 0.6), (-1.0, 0.6), (-1.35, 0.95), (-1.5, 0.95), (-1.4, 0.55)]
    props.inked(nm + "_corpo", corpo, "#f2f4f8", r, w=0.014, shade=0.03, shade_color="#c8ccd6", rim=0.01, rim_color="#ffffff")
    props.poly(nm + "_faixa", [(-1.3, 0.33), (1.0, 0.33), (1.2, 0.38), (-1.3, 0.38)], "#2a3a6a", -0.004, r)
    for k in range(6):
        props.poly(f"{nm}_jan{k}", rrect(-0.75 + k * 0.22, 0.44, -0.67 + k * 0.22, 0.52, 0.02, 3), "#2a3a6a", -0.006, r)
    props.poly(nm + "_cab", [(1.0, 0.47), (1.22, 0.45), (1.12, 0.55), (0.98, 0.56)], "#2a3a6a", -0.006, r)
    props.poly(nm + "_asa", [(-0.3, 0.3), (0.3, 0.3), (-0.05, 0.05), (-0.45, 0.05)], "#d8dce4", -0.008, r)
    props.poly(nm + "_motor", rrect(-1.05, 0.62, -0.65, 0.76, 0.06, 4), "#c8ccd6", 0.004, r)
    for sx in (-0.6, 0.85):
        props.poly(f"{nm}_trem{sx}", stroke([(sx, 0.25), (sx, 0.08)], 0.02), "#1a1c22", 0.004, r)
        props.poly(f"{nm}_pneu{sx}", circle(sx, 0.06, 0.06, 16), "#1a1c22", 0.003, r)
    return r


def congresso(nm, loc, s=1.0, cor="#e8e2d4", sombra="#c8c0ae"):
    """silhueta do Congresso Nacional: as duas torres, a cúpula e a tigela (arquitetura, sem marca)"""
    r = empty(nm, None, loc); r.scale = (s, s, s)
    props.inked(nm + "_base", rrect(-2.4, 0.0, 2.4, 0.35, 0.02, 2), sombra, r, w=0.012)
    for sx in (-0.18, 0.18):
        props.inked(f"{nm}_torre{sx}", rrect(sx - 0.15, 0.35, sx + 0.15, 2.9, 0.01, 2), cor, r, loc=(0, 0.01, 0), w=0.012, shade=0.03, shade_color=sombra)
        for k in range(9):
            props.poly(f"{nm}_tj{sx}{k}", cena.rect(sx - 0.12, 0.55 + k * 0.26, sx + 0.12, 0.6 + k * 0.26), sombra, 0.005, r)
    cup = [(-1.6 + 0.6 * math.cos(math.radians(a)), 0.35 + 0.45 * math.sin(math.radians(a))) for a in range(0, 181, 10)]
    props.inked(nm + "_cupula", cup, cor, r, loc=(0, -0.01, 0), w=0.012)
    tig = [(1.6 + 0.75 * math.cos(math.radians(a)), 0.75 - 0.42 * math.sin(math.radians(a))) for a in range(0, 181, 10)]
    props.inked(nm + "_tigela", tig, cor, r, loc=(0, -0.01, 0), w=0.012)
    return r
