"""Objetos do vídeo "O abrigo" (mesmo acabamento de ficha: tinta, sombra e brilho por dentro).
Desenhados de lado ou de frente (plano XZ), origem no centro da base, tamanho real em metros; na ficha os pequenos aparecem
ampliados (fora de escala). A Pipoca (porquinha-da-índia) é a única personagem que não é boneco: nasce aqui.
Paleta: abrigo em verde-musgo e bronze, luz de lâmpada quente; o resto entra com uma cor de destaque por objeto."""
import math
import cena, props, lib
from props import _mix
from lib import empty
from char2d import rrect
from puppet2d import circle, stroke, smooth

TINTA = "#14110e"
BRONZE, BRONZE_S, BRONZE_L = "#b88a52", "#8a6234", "#e8c08a"
MUSGO, MUSGO_S, MUSGO_L = "#5d7a64", "#46604d", "#9bbd9f"
MADEIRA, MADEIRA_S, MADEIRA_L = "#8a5a34", "#6a4228", "#c89868"


def rot(pts, ang, cx=0.0, cz=0.0):
    c, s = math.cos(math.radians(ang)), math.sin(math.radians(ang))
    return [(cx + (x - cx) * c - (z - cz) * s, cz + (x - cx) * s + (z - cz) * c) for x, z in pts]


def mv(pts, dx, dz):
    return [(x + dx, z + dz) for x, z in pts]


def ring(nm, cx, cz, R, w, cor, y, parent):
    pts = [(cx + R * math.cos(math.radians(a)), cz + R * math.sin(math.radians(a))) for a in range(0, 361, 10)]
    return props.poly(nm, stroke(pts, w), cor, y, parent)


def arco(nm, cx, cz, R, a0, a1, w, cor, y, parent, passo=8):
    n = max(2, int(abs(a1 - a0) / passo) + 1)
    pts = [(cx + R * math.cos(math.radians(a0 + (a1 - a0) * k / (n - 1))), cz + R * math.sin(math.radians(a0 + (a1 - a0) * k / (n - 1)))) for k in range(n)]
    return props.poly(nm, stroke(pts, w), cor, y, parent)


# ---------------------------------------------------------------- a Pipoca
def porquinha(nm, loc, s=1.0, parent=None, vista="lado"):
    """Pipoca, a porquinha-da-índia (0,26 m), no tom sério do vídeo: pelo marrom-escuro com manchas cor de areia, olho pequeno e fundo,
    orelha de rosa murcha e um suéter de tricô vermelho-tijolo, largo e gasto, com remendo (o único vermelho vivo da ficha, de propósito)."""
    r = empty(nm, parent, loc); r.scale = (s, s, s)
    PEL, PEL_S, PEL_L, AREIA = "#6e4e34", "#4e3623", "#9a7650", "#b89c70"
    VER, VER_S, VER_L, CRE = "#8e302b", "#64211f", "#b65048", "#a89f86"
    if vista == "lado":
        corpo = smooth([(-0.15, 0.045), (-0.17, 0.09), (-0.13, 0.14), (-0.04, 0.16), (0.06, 0.155), (0.13, 0.13), (0.155, 0.09), (0.14, 0.045), (0.08, 0.022), (-0.02, 0.018), (-0.1, 0.025)], 5)
        props.inked(nm + "_corpo", corpo, PEL, r, w=0.003, shade=0.014, shade_color=PEL_S, rim=0.003, rim_color="#d9b98a")
        for k, (x0, x1) in enumerate(((0.09, 0.13), (-0.13, -0.085))):
            props.inked(f"{nm}_pata{k}", rrect(x0, 0.0, x1, 0.04, 0.008, 2), PEL_S, r, w=0.003)
        cab = smooth([(0.1, 0.05), (0.115, 0.125), (0.17, 0.155), (0.215, 0.13), (0.245, 0.085), (0.235, 0.06), (0.185, 0.04), (0.125, 0.04)], 4)
        props.inked(nm + "_cab", cab, PEL, r, w=0.003, shade=0.01, shade_color=PEL_S, rim=0.003, rim_color="#d9b98a")
        props.poly(nm + "_mancha", smooth([(0.17, 0.152), (0.215, 0.128), (0.24, 0.088), (0.2, 0.09), (0.175, 0.11)], 3), AREIA, -0.004, r)
        props.poly(nm + "_orelha", smooth([(0.12, 0.13), (0.14, 0.17), (0.17, 0.158), (0.165, 0.128)], 3), "#7a5a4e", -0.005, r)
        props.poly(nm + "_focinho", circle(0.244, 0.082, 0.008, 12), "#2a1a14", -0.006, r)
        props.poly(nm + "_olho", circle(0.2, 0.113, 0.0085, 14), "#0d1020", -0.006, r)
        props.poly(nm + "_brilho", circle(0.2025, 0.1165, 0.0022, 8), "#b9b09a", -0.007, r)
        for k, dz in enumerate((-0.01, 0.0, 0.01)):
            props.poly(f"{nm}_bigode{k}", stroke([(0.238, 0.082 + dz), (0.27, 0.078 + dz * 2.2)], 0.0009), "#cfc6ae", -0.006, r)
        sue = smooth([(-0.165, 0.05), (-0.17, 0.09), (-0.13, 0.145), (-0.04, 0.167), (0.06, 0.162), (0.122, 0.14), (0.13, 0.07), (0.07, 0.03), (-0.02, 0.03), (-0.1, 0.03)], 4)
        props.inked(nm + "_sue", sue, VER, r, w=0.003, shade=0.014, shade_color=VER_S, rim=0.003, rim_color=VER_L)
        props.poly(nm + "_gola", rrect(0.092, 0.06, 0.14, 0.15, 0.014, 3), VER_S, -0.005, r)
        props.poly(nm + "_lista", rrect(-0.16, 0.09, 0.12, 0.103, 0.002, 1), CRE, -0.005, r)
        for k in range(11):
            x = -0.15 + 0.0245 * k
            props.poly(f"{nm}_pt{k}", stroke([(x, 0.04), (x + 0.004, 0.084)], 0.0014), VER_S, -0.006, r)
            props.poly(f"{nm}_pu{k}", stroke([(x, 0.11), (x + 0.004, 0.158 - 0.0045 * abs(k - 5) * 0.4)], 0.0014), VER_S, -0.006, r)
        props.poly(nm + "_remendo", rrect(-0.06, 0.115, -0.015, 0.15, 0.003, 1), "#6a6a52", -0.007, r)
        for k in range(4):
            props.poly(f"{nm}_pn{k}", stroke([(-0.06 + 0.0115 * k, 0.115), (-0.06 + 0.0115 * k, 0.15)], 0.0007), "#2a2a20", -0.008, r)
    else:
        corpo = smooth([(-0.115, 0.04), (-0.13, 0.09), (-0.1, 0.145), (0.0, 0.162), (0.1, 0.145), (0.13, 0.09), (0.115, 0.04), (0.0, 0.016)], 5)
        props.inked(nm + "_corpo", corpo, PEL, r, w=0.003, shade=0.014, shade_color=PEL_S, rim=0.003, rim_color="#d9b98a")
        for k, x in enumerate((-0.065, 0.065)):
            props.inked(f"{nm}_pata{k}", rrect(x - 0.022, 0.0, x + 0.022, 0.036, 0.008, 2), PEL_S, r, w=0.003)
        sue = smooth([(-0.115, 0.045), (-0.13, 0.09), (-0.1, 0.14), (0.0, 0.145), (0.1, 0.14), (0.13, 0.09), (0.115, 0.045), (0.0, 0.03)], 4)
        props.inked(nm + "_sue", sue, VER, r, w=0.003, shade=0.014, shade_color=VER_S, rim=0.003, rim_color=VER_L)
        props.poly(nm + "_lista", rrect(-0.128, 0.07, 0.128, 0.083, 0.002, 1), CRE, -0.005, r)
        for k in range(9):
            x = -0.1 + 0.025 * k
            props.poly(f"{nm}_pt{k}", stroke([(x, 0.036), (x, 0.066)], 0.0014), VER_S, -0.006, r)
        props.inked(nm + "_gola", rrect(-0.07, 0.128, 0.07, 0.17, 0.014, 3), VER_S, r, w=0.003)
        for k, sg in enumerate((-1, 1)):
            props.poly(f"{nm}_orelha{k}", smooth([(sg * 0.05, 0.2), (sg * 0.075, 0.232), (sg * 0.098, 0.208), (sg * 0.088, 0.18)], 3), "#7a5a4e", -0.003, r)
        cab = smooth([(-0.085, 0.172), (-0.09, 0.212), (-0.05, 0.25), (0.0, 0.257), (0.05, 0.25), (0.09, 0.212), (0.085, 0.172), (0.0, 0.158)], 4)
        props.inked(nm + "_cab", cab, PEL, r, w=0.003, shade=0.01, shade_color=PEL_S, rim=0.003, rim_color="#d9b98a")
        props.poly(nm + "_mancha", smooth([(-0.016, 0.245), (0.016, 0.245), (0.024, 0.195), (0.0, 0.18), (-0.024, 0.195)], 3), AREIA, -0.005, r)
        for k, sg in enumerate((-1, 1)):
            props.poly(f"{nm}_olho{k}", circle(sg * 0.043, 0.212, 0.0095, 14), "#0d1020", -0.006, r)
            props.poly(f"{nm}_brilho{k}", circle(sg * 0.043 + 0.002, 0.2155, 0.0024, 8), "#b9b09a", -0.007, r)
        props.poly(nm + "_focinho", circle(0.0, 0.183, 0.0085, 12), "#2a1a14", -0.006, r)
        for k, sg in enumerate((-1, 1)):
            for j, dz in enumerate((-0.009, 0.0, 0.009)):
                props.poly(f"{nm}_big{k}{j}", stroke([(sg * 0.02, 0.187 + dz), (sg * 0.07, 0.187 + dz * 2.2)], 0.0009), "#cfc6ae", -0.006, r)
    return r


def gaiola(nm, loc, s=1.0, parent=None):
    """gaiola da Pipoca (0,6 x 0,45 m): bandeja, grade, casinha de madeira, bebedouro e feno"""
    r = empty(nm, parent, loc); r.scale = (s, s, s)
    props.inked(nm + "_bandeja", rrect(-0.3, 0.0, 0.3, 0.06, 0.012, 3), "#5a6a72", r, w=0.005, shade=0.01, shade_color="#3f4d54", rim=0.003, rim_color="#9db0b8")
    props.poly(nm + "_feno", smooth([(-0.28, 0.06), (-0.2, 0.09), (-0.1, 0.075), (0.05, 0.095), (0.18, 0.07), (0.28, 0.06)], 3), "#d9c27a", -0.003, r)
    props.inked(nm + "_casa", rrect(-0.27, 0.06, -0.07, 0.2, 0.01, 2), MADEIRA, r, w=0.004, shade=0.008, shade_color=MADEIRA_S, rim=0.003, rim_color=MADEIRA_L)
    props.inked(nm + "_telhado", [(-0.29, 0.2), (-0.05, 0.2), (-0.17, 0.27)], "#a9503a", r, w=0.004, shade=0.008, shade_color="#7e3a2a")
    props.poly(nm + "_porta", smooth([(-0.19, 0.06), (-0.19, 0.13), (-0.17, 0.15), (-0.15, 0.13), (-0.15, 0.06)], 3), "#1c1410", -0.004, r)
    for k in range(13):
        x = -0.285 + 0.0475 * k
        props.poly(f"{nm}_barra{k}", stroke([(x, 0.06), (x, 0.42)], 0.0035), "#aab4bb", -0.006, r)
    props.inked(nm + "_topo", rrect(-0.3, 0.42, 0.3, 0.45, 0.008, 2), "#5a6a72", r, w=0.004, rim=0.003, rim_color="#9db0b8")
    props.inked(nm + "_alca", [(-0.04, 0.45), (0.04, 0.45), (0.03, 0.5), (-0.03, 0.5)], "#5a6a72", r, w=0.004)
    props.inked(nm + "_bebedouro", rrect(0.325, 0.16, 0.375, 0.38, 0.02, 3), "#bfe2f2", r, w=0.004, shade=0.006, shade_color="#8cc0d8")
    props.poly(nm + "_agua", rrect(0.332, 0.17, 0.368, 0.3, 0.01, 2), "#6fb7e0", -0.004, r)
    props.poly(nm + "_bico", stroke([(0.35, 0.16), (0.33, 0.1)], 0.005), "#c8ccd6", -0.004, r)
    return r


# ---------------------------------------------------------------- fora do abrigo
def bicicleta(nm, loc, s=1.0, parent=None, cor="#8e3a30"):
    """a bicicleta do narrador (1,3 x 0,95 m): quadro vermelho, cesta de vime na frente com a boneca dentro e a campainha no guidão"""
    r = empty(nm, parent, loc); r.scale = (s, s, s)
    R = 0.33
    for k, x in enumerate((-0.5, 0.5)):
        ring(f"{nm}_pneu{k}", x, R, R, 0.026, "#1c1c22", -0.002, r)
        ring(f"{nm}_aro{k}", x, R, R - 0.03, 0.008, "#c8ccd6", -0.003, r)
        for a in range(0, 180, 30):
            p = [(x + (R - 0.03) * math.cos(math.radians(a)), R + (R - 0.03) * math.sin(math.radians(a))), (x - (R - 0.03) * math.cos(math.radians(a)), R - (R - 0.03) * math.sin(math.radians(a)))]
            props.poly(f"{nm}_raio{k}_{a}", stroke(p, 0.0022), "#9aa3b0", -0.003, r)
        props.poly(f"{nm}_cubo{k}", circle(x, R, 0.026, 14), "#c8ccd6", -0.004, r)
    A, B, C, D, F = (-0.5, R), (-0.08, 0.32), (-0.22, 0.8), (0.36, 0.76), (0.5, R)
    for k, (a, b) in enumerate(((A, B), (B, C), (A, C), (C, D), (B, (0.34, 0.7)), ((0.38, 0.78), F))):
        props.poly(f"{nm}_tubo{k}", stroke([a, b], 0.013), cor, -0.005, r)
        props.poly(f"{nm}_tubo_l{k}", stroke([(a[0] - 0.003, a[1] + 0.004), (b[0] - 0.003, b[1] + 0.004)], 0.003), _mix(cor, "#ffffff", 0.45), -0.006, r)
    props.poly(nm + "_canote", stroke([C, (-0.22, 0.84)], 0.009), "#9aa3b0", -0.005, r)
    props.inked(nm + "_selim", smooth([(-0.36, 0.84), (-0.3, 0.87), (-0.14, 0.87), (-0.1, 0.85), (-0.14, 0.82), (-0.3, 0.82)], 3), "#3a2a20", r, w=0.004, rim=0.003, rim_color="#7a5a40")
    props.poly(nm + "_coroa", circle(B[0], B[1], 0.06, 20), "#9aa3b0", -0.004, r)
    props.poly(nm + "_coroa_c", circle(B[0], B[1], 0.03, 14), "#5a626e", -0.005, r)
    props.poly(nm + "_pedivela", stroke([B, (B[0] + 0.05, B[1] - 0.11)], 0.008), "#5a626e", -0.005, r)
    props.poly(nm + "_pedal", rrect(B[0] + 0.015, B[1] - 0.13, B[0] + 0.1, B[1] - 0.115, 0.004, 1), "#1c1c22", -0.006, r)
    props.poly(nm + "_corrente", stroke([(A[0], A[1] - 0.025), (B[0], B[1] - 0.058)], 0.003), "#3a3d46", -0.003, r)
    props.poly(nm + "_mesa", stroke([(0.36, 0.78), (0.32, 0.96)], 0.01), "#9aa3b0", -0.005, r)
    props.poly(nm + "_guidao", stroke([(0.32, 0.96), (0.43, 0.99)], 0.011), "#1c1c22", -0.005, r)
    props.poly(nm + "_punho", rrect(0.4, 0.975, 0.47, 1.0, 0.01, 2), "#1c1c22", -0.006, r)
    # cesta de vime com a boneca
    props.poly(nm + "_boneca_cor", rrect(0.5, 0.93, 0.6, 1.1, 0.02, 3), "#a8786f", -0.004, r)
    props.poly(nm + "_boneca_cab", circle(0.55, 1.17, 0.058, 22), "#0d1020", -0.005, r)
    for k, dx in enumerate((-0.02, 0.02)):
        props.poly(f"{nm}_boneca_o{k}", circle(0.55 + dx, 1.18, 0.012, 8), "#ffffff", -0.006, r)
    props.inked(nm + "_cesta", [(0.4, 0.82), (0.68, 0.82), (0.7, 1.02), (0.38, 1.02)], "#c9a26a", r, loc=(0, -0.004, 0), w=0.005, shade=0.012, shade_color="#a07e4a", rim=0.004, rim_color="#ecd09a")
    for k in range(5):
        props.poly(f"{nm}_vime_h{k}", stroke([(0.395 + 0.002 * k, 0.84 + 0.04 * k), (0.685 + 0.003 * k, 0.84 + 0.04 * k)], 0.0022), "#a07e4a", -0.0095, r)
    for k in range(6):
        props.poly(f"{nm}_vime_v{k}", stroke([(0.42 + 0.05 * k, 0.83), (0.42 + 0.05 * k, 1.01)], 0.0022), "#a07e4a", -0.0095, r)
    props.poly(nm + "_campainha", circle(0.37, 1.0, 0.03, 18), "#c8ccd6", -0.007, r)
    props.poly(nm + "_campainha_b", stroke([(0.355, 1.012), (0.372, 1.02)], 0.004), "#ffffff", -0.008, r)
    props.poly(nm + "_campainha_t", rrect(0.363, 1.026, 0.377, 1.04, 0.003, 1), "#5a626e", -0.008, r)
    return r


def sirene(nm, loc, s=1.0, parent=None):
    """sirene do bairro (poste de 3,2 m): duas cornetas, luz vermelha no topo e ondas de som"""
    r = empty(nm, parent, loc); r.scale = (s, s, s)
    props.inked(nm + "_poste", rrect(-0.05, 0.0, 0.05, 3.2, 0.012, 3), "#8a9096", r, w=0.012, shade=0.02, shade_color="#6a7076", rim=0.008, rim_color="#e0e4e8")
    props.inked(nm + "_base", rrect(-0.12, 0.0, 0.12, 0.12, 0.012, 3), "#6a7076", r, w=0.01)
    props.inked(nm + "_braco", rrect(-0.45, 2.78, 0.45, 2.84, 0.01, 2), "#6a7076", r, w=0.01)
    for k, sg in enumerate((-1, 1)):
        corneta = [(sg * 0.38, 2.64), (sg * 0.38, 3.0), (sg * 0.82, 3.2), (sg * 0.82, 2.44)]
        props.inked(f"{nm}_corneta{k}", corneta, "#8a4a36", r, w=0.01, shade=0.02, shade_color="#5e3022", rim=0.008, rim_color="#c9996e")
        props.poly(f"{nm}_boca{k}", rrect(sg * 0.8 - 0.015, 2.46, sg * 0.8 + 0.015, 3.18, 0.0, 1), "#2a1410", -0.01, r)
        for j in range(3):
            arco(f"{nm}_onda{k}_{j}", sg * 0.82, 2.82, 0.22 + 0.18 * j, -40 if sg > 0 else 140, 40 if sg > 0 else 220, 0.016 - 0.003 * j, "#8e3a30", -0.012, r)
    props.inked(nm + "_farol", rrect(-0.09, 3.2, 0.09, 3.38, 0.04, 4), "#a8342c", r, w=0.008, shade=0.012, shade_color="#6e211c", rim=0.006, rim_color="#d98a80")
    return r


def multidao(nm, loc, s=1.0, n=5):
    """a vizinhança batendo na porta (silhuetas, sem rosto): cada um numa cor apagada para a gente não virar um bloco só"""
    x, y, z = loc
    cores = ["#a56a5a", "#6a7f9a", "#8a8f5a", "#9a6a8a", "#c8b48a", "#5a8a8a"]
    for k in range(n):
        props.pessoa(f"{nm}_{k}", x + (k - (n - 1) / 2) * 0.6 * s, y + 0.05 * (k % 2), cores[k % len(cores)], (0.92 + 0.06 * (k % 3)) * s, flip=1 if k % 2 else -1, z=z, rim="#ffe4c8")


def porta_abrigo(nm, loc, s=1.0, parent=None, aberta=0.0, luz_fora="#f2efe0"):
    """a porta do abrigo (1,2 x 2,5 m): batente de aço, o vão (luz de fora) e a FOLHA verde-musgo que corre de lado ('<nm>_folha'; aberta = 0 fechada, 1 toda
    para a direita); a roda de giro de bronze é '<nm>_roda' (gira em y), três trincos de um lado, três dobradiças do outro, a janelinha redonda e a placa"""
    r = empty(nm, parent, loc); r.scale = (s, s, s)
    props.inked(nm + "_batente", rrect(-0.62, 0.0, 0.62, 2.3, 0.03, 3), "#3a4650", r, w=0.02, shade=0.03, shade_color="#2a333b", rim=0.01, rim_color="#8a98a4")
    props.poly(nm + "_vao", rrect(-0.52, 0.05, 0.52, 2.22, 0.02, 2), luz_fora, -0.012, r)
    f = empty(nm + "_folha", r, (aberta * 1.15, 0, 0))
    props.inked(nm + "_porta", rrect(-0.52, 0.05, 0.52, 2.22, 0.03, 3), MUSGO, f, loc=(0, -0.02, 0), w=0.014, shade=0.04, shade_color=MUSGO_S, rim=0.012, rim_color=MUSGO_L)
    for k, (z0, z1) in enumerate(((0.16, 0.95), (1.4, 2.12))):
        props.poly(f"{nm}_painel{k}", rrect(-0.42, z0, 0.42, z1, 0.02, 3), _mix(MUSGO, "#000000", 0.12), -0.04, f)
    for k, (x, z) in enumerate([(sx, sz) for sx in (-0.46, 0.46) for sz in (0.12, 0.55, 1.0, 1.4, 1.8, 2.16)]):
        props.poly(f"{nm}_rebite{k}", circle(x, z, 0.014, 8), MUSGO_L, -0.042, f)
    for k, z in enumerate((0.4, 1.15, 1.9)):
        props.inked(f"{nm}_trinco{k}", rrect(0.44, z - 0.05, 0.64, z + 0.05, 0.012, 2), "#aab4bb", f, loc=(0, -0.045, 0), w=0.006, shade=0.008, shade_color="#7e8a92")
        props.inked(f"{nm}_dobradica{k}", rrect(-0.64, z - 0.09, -0.46, z + 0.09, 0.01, 2), "#2a333b", f, loc=(0, -0.045, 0), w=0.006, rim=0.004, rim_color="#8a98a4")
    cx, cz = 0.0, 1.15
    ro = empty(nm + "_roda", f, (cx, -0.055, cz))
    ring(nm + "_roda_aro", 0.0, 0.0, 0.28, 0.034, BRONZE, 0.0, ro)
    for k in range(6):
        a = math.radians(60 * k + 15)
        props.poly(f"{nm}_raio{k}", stroke([(0, 0), (0.28 * math.cos(a), 0.28 * math.sin(a))], 0.016), BRONZE, -0.002, ro)
        props.poly(f"{nm}_pino{k}", circle(0.31 * math.cos(a), 0.31 * math.sin(a), 0.028, 12), BRONZE_L, -0.004, ro)
    props.inked(nm + "_cubo", circle(0, 0, 0.09, 24), BRONZE_S, ro, loc=(0, -0.006, 0), w=0.008, shade=0.01, shade_color="#5e4020", rim=0.006, rim_color=BRONZE_L)
    props.poly(nm + "_cubo_c", circle(0, 0, 0.035, 14), BRONZE_L, -0.014, ro)
    props.poly(nm + "_jan_aro", circle(0.0, 1.8, 0.16, 28), BRONZE, -0.05, f)
    props.poly(nm + "_jan", circle(0.0, 1.8, 0.135, 28), "#efe9d6", -0.053, f)
    props.inked(nm + "_placa", rrect(-0.3, 2.36, 0.3, 2.52, 0.012, 3), BRONZE, r, w=0.008, shade=0.012, shade_color=BRONZE_S, rim=0.005, rim_color=BRONZE_L)
    t = lib.text(nm + "_placa_t", "ABRIGO", 0.1, props.FM("#2a1c0e"), r, (0.0, -0.014, 2.44), lib.font()); t.rotation_euler = (math.pi / 2, 0, 0)
    return r


def rostos_janela(nm, folha, z=1.8, k=2.1):
    """o que se vê pela janelinha de fora: dois rostos de vizinhos (cabeça escura, olhos brancos arregalados, boca aberta) e duas mãos espalmadas no vidro
    (desenhados pequenos e ampliados por k). Devolve os empties (rostoA, rostoB, maoA, maoB) para animar: chegar perto do vidro a cada batida"""
    w = empty(nm + "_wrap", folha, (0, -0.06, z)); w.scale = (k, k, k)
    out = []
    for i, x in enumerate((-0.026, 0.03)):
        g = empty(f"{nm}_rosto{i}", w, (x, 0, 0.004))
        props.poly(f"{nm}_cab{i}", circle(0, 0, 0.03, 20), "#0d1020", 0.0, g)
        for j, dx in enumerate((-0.011, 0.011)):
            props.poly(f"{nm}_ol{i}{j}", circle(dx, 0.005, 0.0085, 10), "#f6f1e4", -0.002, g)
        props.poly(f"{nm}_bc{i}", smooth([(-0.009, -0.013), (0.009, -0.013), (0.007, -0.023), (-0.007, -0.023)], 3), "#f6f1e4", -0.002, g)
        out.append(g)
    for i, x in enumerate((-0.045, 0.05)):
        g = empty(f"{nm}_mao{i}", w, (x, 0, -0.035))
        props.poly(f"{nm}_pa{i}", circle(0, 0, 0.014, 12), "#0d1020", 0.0, g)
        for j in range(5):
            a = math.radians(30 + 30 * j)
            props.poly(f"{nm}_de{i}{j}", stroke([(0.009 * math.cos(a), 0.009 * math.sin(a)), (0.026 * math.cos(a), 0.026 * math.sin(a))], 0.004), "#0d1020", 0.0, g)
        out.append(g)
    return out


# ---------------------------------------------------------------- dentro do abrigo
def cadeira_balanco(nm, loc, s=1.0, parent=None, manta="#4f8a5c"):
    """cadeira de balanço de madeira (de lado), com uma manta jogada no encosto: onde o Zé fica sentado jogando baralho"""
    r = empty(nm, parent, loc); r.scale = (s, s, s)
    arc = [(x, 0.05 + 0.07 * (x / 0.44) ** 2) for x in [-0.44 + 0.88 * k / 14 for k in range(15)]]
    props.poly(nm + "_patim", stroke(arc, 0.014), MADEIRA_S, -0.002, r)
    for k, x in enumerate((-0.3, 0.26)):
        props.poly(f"{nm}_perna{k}", stroke([(x, 0.05 + 0.07 * (x / 0.44) ** 2), (x + 0.01, 0.42)], 0.014), MADEIRA, -0.004, r)
    props.inked(nm + "_assento", rrect(-0.34, 0.4, 0.3, 0.45, 0.012, 3), MADEIRA, r, w=0.006, shade=0.012, shade_color=MADEIRA_S, rim=0.004, rim_color=MADEIRA_L)
    props.inked(nm + "_encosto", [(-0.36, 0.44), (-0.29, 0.44), (-0.37, 1.0), (-0.45, 1.0)], MADEIRA, r, loc=(0, -0.006, 0), w=0.006, shade=0.012, shade_color=MADEIRA_S, rim=0.004, rim_color=MADEIRA_L)
    props.poly(nm + "_apoio", stroke([(0.24, 0.45), (0.26, 0.7), (-0.3, 0.7)], 0.012), MADEIRA_S, -0.01, r)
    props.inked(nm + "_manta", smooth([(-0.46, 0.98), (-0.33, 0.98), (-0.27, 0.62), (-0.2, 0.46), (-0.38, 0.5), (-0.44, 0.76)], 3), manta, r, loc=(0, -0.012, 0), w=0.005, shade=0.01, shade_color=_mix(manta, "#000000", 0.25), rim=0.004, rim_color=_mix(manta, "#ffffff", 0.4))
    return r


def baralho(nm, loc, s=1.0, parent=None):
    """baralho: cinco cartas abertas em leque (copas, ouros, paus, espadas e copas) e o monte virado ao lado; cada carta tem 6,4 x 8,9 cm"""
    r = empty(nm, parent, loc); r.scale = (s, s, s)
    def carta(k, ang, naipe, cx):
        g = empty(f"{nm}_c{k}", r, (cx, -0.002 * k, 0.0))
        base = rot(rrect(-0.032, 0.0, 0.032, 0.089, 0.005, 2), ang)
        props.inked(f"{nm}_c{k}_f", base, "#f7f3ea", g, w=0.0012, shade=0.0018, shade_color="#d9d3c4")
        cor = "#c8323e" if naipe in ("copas", "ouros") else "#1c2230"
        def P(pts, dz=0.0):
            return rot(mv(pts, 0.0, 0.0445 + dz), ang)
        if naipe == "copas":
            sim = [P(circle(-0.011, 0.012, 0.0115, 12)), P(circle(0.011, 0.012, 0.0115, 12)), P([(-0.0215, 0.007), (0.0215, 0.007), (0.0, -0.022)])]
        elif naipe == "ouros":
            sim = [P([(0.0, 0.026), (0.018, 0.0), (0.0, -0.026), (-0.018, 0.0)])]
        elif naipe == "paus":
            sim = [P(circle(0.0, 0.013, 0.0105, 12)), P(circle(-0.0125, -0.006, 0.0105, 12)), P(circle(0.0125, -0.006, 0.0105, 12)), P(rrect(-0.003, -0.026, 0.003, 0.0, 0.0, 1))]
        else:
            sim = [P(circle(-0.011, -0.004, 0.0115, 12)), P(circle(0.011, -0.004, 0.0115, 12)), P([(-0.0215, 0.001), (0.0215, 0.001), (0.0, 0.03)]), P(rrect(-0.003, -0.026, 0.003, -0.004, 0.0, 1))]
        for j, pts in enumerate(sim):
            props.poly(f"{nm}_c{k}_s{j}", pts, cor, -0.003, g)
        props.poly(f"{nm}_c{k}_ca", circle(*rot([(-0.02, 0.078)], ang)[0], 0.004, 8), cor, -0.003, g)
    for k, (ang, nap) in enumerate(((28, "copas"), (14, "ouros"), (0, "paus"), (-14, "espadas"), (-28, "copas"))):
        carta(k, ang, nap, -0.07 - 0.0 * k)
    for k in range(4):                                                  # o monte virado, com o verso azul
        props.inked(f"{nm}_m{k}", mv(rrect(-0.032, 0.0, 0.032, 0.089, 0.005, 2), 0.12, 0.0), "#34506e" if k == 3 else "#f1ece0", r, loc=(0, -0.02 - 0.003 * k, 0.003 * k), w=0.0012, shade=0.0016, shade_color="#1c3f82")
    props.poly(nm + "_verso", mv(rrect(-0.025, 0.007, 0.025, 0.082, 0.003, 1), 0.12, 0.009), "#f4f1ea", -0.028, r)
    props.poly(nm + "_verso2", mv(rrect(-0.02, 0.012, 0.02, 0.077, 0.003, 1), 0.12, 0.009), "#34506e", -0.029, r)
    props.poly(nm + "_verso3", mv([(0.0, 0.03), (0.012, 0.0445), (0.0, 0.059), (-0.012, 0.0445)], 0.12, 0.009), "#f4f1ea", -0.03, r)
    return r


def galao(nm, loc, s=1.0, parent=None, nivel=1.0):
    """galão de água de 5 litros (0,2 x 0,33 m); nivel = quanto de água sobra (1,0 cheio, 0,5 'meio galão')"""
    r = empty(nm, parent, loc); r.scale = (s, s, s)
    props.inked(nm + "_vaso", rrect(-0.1, 0.0, 0.1, 0.28, 0.03, 4), "#cfeaf5", r, w=0.004, shade=0.012, shade_color="#a9cfe0", rim=0.003, rim_color="#ffffff")
    h = 0.26 * nivel
    props.poly(nm + "_agua", rrect(-0.093, 0.007, 0.093, 0.007 + h, 0.02, 3), "#4c97d0", -0.003, r)
    props.poly(nm + "_nivel", rrect(-0.093, 0.007 + h - 0.006, 0.093, 0.007 + h, 0.002, 1), "#9dd0f0", -0.004, r)
    props.inked(nm + "_gargalo", rrect(-0.04, 0.28, 0.04, 0.325, 0.01, 2), "#cfeaf5", r, w=0.004, shade=0.006, shade_color="#a9cfe0")
    props.inked(nm + "_tampa", rrect(-0.046, 0.318, 0.046, 0.345, 0.008, 2), "#1f4f8a", r, w=0.004, rim=0.003, rim_color="#6a9ad8")
    props.poly(nm + "_alca", stroke([(0.1, 0.26), (0.15, 0.26), (0.15, 0.17), (0.1, 0.17)], 0.011), "#a9cfe0", -0.003, r)
    props.poly(nm + "_rotulo", rrect(-0.07, 0.07, 0.07, 0.19, 0.012, 2), "#f4f1ea", -0.006, r)
    props.poly(nm + "_gota", [(0.0, 0.17), (-0.022, 0.12), (0.0, 0.1), (0.022, 0.12)], "#2a6ad8", -0.007, r)
    props.poly(nm + "_br", stroke([(-0.08, 0.25), (-0.078, 0.14)], 0.004), "#ffffff", -0.007, r)
    return r


def lata(nm, loc, s=1.0, parent=None, cor="#c8323e"):
    """lata de conserva (0,075 x 0,1 m): rótulo colorido, tampa e fundo de metal"""
    r = empty(nm, parent, loc); r.scale = (s, s, s)
    props.inked(nm + "_corpo", rrect(-0.037, 0.0, 0.037, 0.1, 0.004, 2), "#c8ccd6", r, w=0.0025, shade=0.006, shade_color="#9aa3b0", rim=0.002, rim_color="#ffffff")
    props.poly(nm + "_rotulo", rrect(-0.037, 0.018, 0.037, 0.082, 0.0, 1), cor, -0.003, r)
    props.poly(nm + "_faixa", rrect(-0.037, 0.045, 0.037, 0.055, 0.0, 1), "#f4f1ea", -0.004, r)
    props.poly(nm + "_br", stroke([(-0.026, 0.078), (-0.026, 0.024)], 0.003), "#ffffff", -0.005, r)
    return r


def prateleira(nm, loc, s=1.0, parent=None, nivel=1.0):
    """estante de latas do abrigo (1,0 x 1,0 m, três prateleiras); nivel = quanto da comida ainda está lá (1,0 dia 1, 0,15 meses depois)"""
    r = empty(nm, parent, loc); r.scale = (s, s, s)
    props.inked(nm + "_fundo", rrect(-0.5, 0.0, 0.5, 1.0, 0.01, 2), _mix(MUSGO_S, "#000000", 0.25), r, w=0.01)
    for k, x in enumerate((-0.5, 0.5)):
        props.inked(f"{nm}_mont{k}", rrect(x - 0.025, 0.0, x + 0.025, 1.04, 0.006, 2), MADEIRA_S, r, loc=(0, -0.01, 0), w=0.006)
    cores = ["#8e5a3a", "#59603f", "#4f6275", "#a89f86"]
    n_lata = 8
    ocupa = int(round(nivel * n_lata))
    for k, z in enumerate((0.02, 0.35, 0.68)):
        props.inked(f"{nm}_tab{k}", rrect(-0.5, z, 0.5, z + 0.03, 0.004, 1), MADEIRA, r, loc=(0, -0.012, 0), w=0.005, shade=0.006, shade_color=MADEIRA_S, rim=0.003, rim_color=MADEIRA_L)
        slots = list(range(n_lata))
        quais = slots[:ocupa] if nivel >= 0.5 else [slots[0], slots[-1]][:max(ocupa, 1 if nivel > 0 else 0)]
        for j in quais:
            lata(f"{nm}_lata{k}_{j}", (-0.4 + 0.115 * j, -0.02, z + 0.03), 1.0, r, cores[(j + k) % len(cores)])
    if nivel < 0.5:                                                      # uma lata amassada caída: já ninguém arruma
        g = lata(nm + "_caida", (0.1, -0.02, 0.05), 1.0, r, "#4f8a5c"); g.rotation_euler = (0, math.radians(80), 0)
    return r


def prato(nm, loc, s=1.0, parent=None, nivel="cheio"):
    """prato visto de cima (0,24 m): cheio de arroz, ervilha e feijão; 'pouco' (dia 21) com quase nada; 'carne' (dia 60), o pedaço escuro que ninguém perguntou de quê"""
    r = empty(nm, parent, loc); r.scale = (s, s, s)
    props.inked(nm + "_prato", circle(0.0, 0.12, 0.12, 40), "#f1ede2", r, w=0.004, shade=0.006, shade_color="#d9d3c4", rim=0.003, rim_color="#ffffff")
    props.poly(nm + "_funda", circle(0.0, 0.12, 0.085, 36), "#e3dece", -0.003, r)
    if nivel == "cheio":
        props.poly(nm + "_arroz", smooth([(-0.07, 0.1), (-0.05, 0.16), (0.0, 0.18), (0.01, 0.12), (-0.02, 0.07)], 4), "#fffaf0", -0.004, r)
        props.poly(nm + "_feijao", smooth([(0.0, 0.07), (0.05, 0.1), (0.07, 0.15), (0.03, 0.18), (0.0, 0.12)], 4), "#5a3a2a", -0.004, r)
        for k in range(8):
            a = math.radians(40 * k)
            props.poly(f"{nm}_erv{k}", circle(-0.02 + 0.045 * math.cos(a), 0.08 + 0.03 * math.sin(a), 0.009, 8), "#5aa84a", -0.006, r)
        props.poly(nm + "_carne", smooth([(0.02, 0.15), (0.075, 0.17), (0.085, 0.13), (0.045, 0.115)], 3), "#a9603a", -0.006, r)
    elif nivel == "metade":
        props.poly(nm + "_arroz", smooth([(-0.05, 0.1), (-0.035, 0.15), (0.0, 0.16), (0.0, 0.1), (-0.02, 0.07)], 4), "#fffaf0", -0.004, r)
        for k in range(4):
            props.poly(f"{nm}_erv{k}", circle(-0.02 + 0.03 * k, 0.1 + 0.015 * (k % 2), 0.009, 8), "#5aa84a", -0.006, r)
    elif nivel == "vazio":
        props.poly(nm + "_resto", smooth([(-0.02, 0.11), (0.0, 0.13), (0.02, 0.11), (0.0, 0.1)], 3), "#fffaf0", -0.004, r)
        props.poly(nm + "_colher", stroke([(0.0, 0.0), (0.02, 0.1)], 0.004), "#c8ccd6", -0.007, r)
        props.poly(nm + "_colher_c", circle(0.021, 0.115, 0.014, 12), "#c8ccd6", -0.007, r)
    elif nivel == "pouco":
        for k in range(3):
            props.poly(f"{nm}_erv{k}", circle(-0.02 + 0.03 * k, 0.12 + 0.01 * (k % 2), 0.009, 8), "#5aa84a", -0.006, r)
        props.poly(nm + "_arroz", smooth([(-0.045, 0.1), (-0.03, 0.125), (-0.015, 0.1)], 3), "#fffaf0", -0.004, r)
    else:
        props.poly(nm + "_carne", smooth([(-0.065, 0.1), (-0.04, 0.17), (0.04, 0.18), (0.07, 0.12), (0.03, 0.07), (-0.03, 0.07)], 4), "#8a4a2c", -0.004, r)
        props.poly(nm + "_gordura", smooth([(0.0, 0.16), (0.04, 0.17), (0.05, 0.13), (0.02, 0.125)], 3), "#d9b48a", -0.005, r)
        props.poly(nm + "_br", stroke([(-0.04, 0.15), (-0.01, 0.17)], 0.005), "#c07a52", -0.006, r)
    props.poly(nm + "_garfo", stroke([(0.16, 0.04), (0.16, 0.2)], 0.004), "#c8ccd6", -0.007, r)
    for k in range(3):
        props.poly(f"{nm}_gd{k}", stroke([(0.148 + 0.012 * k, 0.2), (0.148 + 0.012 * k, 0.24)], 0.0018), "#c8ccd6", -0.007, r)
    return r


def quadro_giz(nm, loc, s=1.0, parent=None, dias=17, rotulo="DIA 17"):
    """calendário de giz na parede: lousa verde-escura com os dias riscados de quatro em quatro e o corte de cinco (0,9 x 0,6 m)"""
    r = empty(nm, parent, loc); r.scale = (s, s, s)
    props.inked(nm + "_moldura", rrect(-0.46, 0.0, 0.46, 0.62, 0.012, 3), MADEIRA, r, w=0.008, shade=0.012, shade_color=MADEIRA_S, rim=0.005, rim_color=MADEIRA_L)
    props.poly(nm + "_lousa", rrect(-0.42, 0.04, 0.42, 0.58, 0.006, 2), "#2c3a3a", -0.004, r)
    t = lib.text(nm + "_t", rotulo, 0.09, props.FM("#ece7d8"), r, (0.0, -0.012, 0.51), lib.font()); t.rotation_euler = (math.pi / 2, 0, 0)
    grupos = dias // 5
    resto = dias % 5
    def traco(k, x0, z0, n, corte):
        for i in range(n):
            props.poly(f"{nm}_g{k}_{i}", stroke([(x0 + 0.018 * i, z0), (x0 + 0.018 * i + 0.002, z0 + 0.075)], 0.0028), "#ece7d8", -0.008, r)
        if corte:
            props.poly(f"{nm}_g{k}_cr", stroke([(x0 - 0.012, z0 + 0.02), (x0 + 0.018 * 3 + 0.014, z0 + 0.055)], 0.0028), "#ece7d8", -0.009, r)
    k = 0
    for k in range(grupos):
        traco(k, -0.36 + 0.115 * (k % 6), 0.26 - 0.12 * (k // 6), 4, True)
    if resto:
        traco(grupos, -0.36 + 0.115 * (grupos % 6), 0.26 - 0.12 * (grupos // 6), resto, False)
    props.poly(nm + "_giz", rrect(0.2, 0.045, 0.27, 0.058, 0.004, 1), "#ece7d8", -0.008, r)
    return r


def lampadas(nm, loc, s=1.0, parent=None, ligadas=3):
    """três lâmpadas penduradas num fio (0,5 m de queda); as primeiras 'ligadas' acesas, as outras queimadas (cinza)"""
    r = empty(nm, parent, loc); r.scale = (s, s, s)
    props.poly(nm + "_fio", stroke([(-0.45, 0.5), (0.0, 0.47), (0.45, 0.5)], 0.004), "#1c1c22", 0.002, r)
    for k, x in enumerate((-0.4, 0.0, 0.4)):
        zf = 0.49 if k != 1 else 0.468
        on = k < ligadas
        props.poly(f"{nm}_cabo{k}", stroke([(x, zf), (x, 0.4)], 0.004), "#1c1c22", 0.002, r)
        props.inked(f"{nm}_soquete{k}", rrect(x - 0.02, 0.36, x + 0.02, 0.41, 0.006, 2), "#3a3d46", r, w=0.003)
        if on:
            props.inked(f"{nm}_bulbo{k}", circle(x, 0.29, 0.05, 24), "#ffe3a0", r, w=0.003, rim=0.003, rim_color="#fff8dc", strength=1.4)
            props.poly(f"{nm}_fila{k}", stroke([(x - 0.012, 0.29), (x, 0.31), (x + 0.012, 0.29)], 0.002), "#e08a3c", -0.004, r)
        else:
            props.inked(f"{nm}_bulbo{k}", circle(x, 0.29, 0.05, 24), "#6a7078", r, w=0.003, shade=0.008, shade_color="#4a5058", rim=0.003, rim_color="#a8b0b8")
            props.poly(f"{nm}_fila{k}", stroke([(x - 0.012, 0.29), (x, 0.31), (x + 0.012, 0.29)], 0.002), "#2a2d34", -0.004, r)
    return r


# ---------------------------------------------------------------- o narrador (só as mãos)
def maos_pov(nm, loc, s=1.0, parent=None):
    """as mãos de quem conta a história, vistas dos olhos dele (sobem da borda de baixo do quadro). Cada lado tem a manga (cinza-azulada, com punho claro)
    e duas mãos que se trocam por escala: '<nm>_esq_aberta' e '<nm>_esq_fechada' (idem dir). A mão do boneco é preta (como no elenco todo), com borda de luz.
    Devolve a raiz; os lados são '<nm>_esq' e '<nm>_dir'."""
    r = empty(nm, parent, loc); r.scale = (s, s, s)
    MANGA, MANGA_S, PUNHO = "#6a7f9a", "#4f6178", "#aab6c8"
    PELE, RIM = "#0d1020", "#ffe4c8"
    for lado, sg in (("esq", -1), ("dir", 1)):
        g = empty(f"{nm}_{lado}", r, (sg * 0.2, 0, 0.0))
        props.inked(f"{nm}_{lado}_manga", [(-0.12, -0.3), (0.1, -0.3), (0.085, 0.1), (-0.095, 0.1)], MANGA, g, w=0.005, shade=0.014, shade_color=MANGA_S, rim=0.004, rim_color="#b4c4dc")
        props.inked(f"{nm}_{lado}_punho", rrect(-0.1, 0.1, 0.09, 0.14, 0.008, 2), PUNHO, g, loc=(0, -0.004, 0), w=0.004)
        # aberta: palma voltada para a gente, quatro dedos e o polegar para o lado de dentro
        a = empty(f"{nm}_{lado}_aberta", g, (0, 0, 0))
        props.inked(f"{nm}_{lado}_palma", rrect(-0.075, 0.14, 0.07, 0.27, 0.03, 4), PELE, a, loc=(0, -0.006, 0), w=0.003, rim=0.004, rim_color=RIM)
        for i, (x, h) in enumerate(((-0.06, 0.16), (-0.021, 0.19), (0.021, 0.2), (0.06, 0.17))):
            props.inked(f"{nm}_{lado}_d{i}", rrect(x - 0.0155, 0.25, x + 0.0155, 0.25 + h, 0.014, 3), PELE, a, loc=(0, -0.007, 0), w=0.003, rim=0.003, rim_color=RIM)
        props.inked(f"{nm}_{lado}_pol", rot(rrect(-0.012, 0.0, 0.024, 0.11, 0.014, 3), 50 * sg), PELE, a, loc=(-0.07 * sg, -0.007, 0.18), w=0.003, rim=0.003, rim_color=RIM)
        # fechada: punho com os nós dos dedos para cima, polegar por cima, como segurando o guidão
        f = empty(f"{nm}_{lado}_fechada", g, (0, 0, 0))
        props.inked(f"{nm}_{lado}_punho_m", rrect(-0.085, 0.14, 0.085, 0.27, 0.04, 4), PELE, f, loc=(0, -0.006, 0), w=0.003, rim=0.004, rim_color=RIM)
        for i, x in enumerate((-0.06, -0.02, 0.02, 0.06)):
            props.poly(f"{nm}_{lado}_n{i}", stroke([(x, 0.235), (x, 0.262)], 0.0035), "#2a3050", -0.01, f)
        props.inked(f"{nm}_{lado}_pol_f", rot(rrect(-0.012, 0.0, 0.024, 0.1, 0.014, 3), 70 * sg), PELE, f, loc=(-0.075 * sg, -0.008, 0.16), w=0.003, rim=0.003, rim_color=RIM)
        f.scale = (0.0001,) * 3                                                                # por padrão a mão está aberta
    return r


# ---------------------------------------------------------------- peças da produção (cena a cena)
def guidao_pov(nm, loc=(0, 0, 0), s=1.0, parent=None):
    """o guidão da bicicleta visto dos olhos de quem pedala (de trás): barra preta, dois punhos, a campainha prateada à esquerda e a ponta da cesta ao fundo"""
    r = empty(nm, parent, loc); r.scale = (s, s, s)
    props.inked(nm + "_barra", rrect(-0.36, 0.0, 0.36, 0.03, 0.012, 3), "#1c1c22", r, loc=(0, 0.02, 0), w=0.004, rim=0.003, rim_color="#8a8a80")
    for k, sg in enumerate((-1, 1)):
        props.inked(f"{nm}_punho{k}", rrect(sg * 0.2 - 0.09 if sg < 0 else 0.11, -0.014, sg * 0.2 + 0.09 if sg > 0 else -0.11, 0.044, 0.02, 3), "#2a2a30", r, loc=(0, 0.015, 0), w=0.004)
    props.inked(nm + "_sino", circle(-0.5, 0.05, 0.05, 20), "#c8ccd6", r, loc=(0, 0.01, 0), w=0.004, shade=0.01, shade_color="#8a909c", rim=0.004, rim_color="#ffffff")
    props.poly(nm + "_sino_t", rrect(-0.515, 0.095, -0.485, 0.125, 0.004, 1), "#5a626e", -0.002, r)
    return r


def cama(nm, loc, s=1.0, parent=None, manta="#6e6a4a", dobrada=False):
    """cama de ferro (1,9 x 0,6 m, de frente): estrado, colchão, travesseiro e a manta; dobrada = manta dobrada ao pé, cama vazia"""
    r = empty(nm, parent, loc); r.scale = (s, s, s)
    props.inked(nm + "_pe", rrect(-0.95, 0.0, -0.9, 0.55, 0.01, 2), "#3a4046", r, w=0.005)
    props.inked(nm + "_cabeceira", rrect(0.9, 0.0, 0.95, 0.7, 0.01, 2), "#3a4046", r, w=0.005)
    props.inked(nm + "_estrado", rrect(-0.95, 0.2, 0.95, 0.26, 0.01, 2), "#4a5258", r, w=0.005, rim=0.003, rim_color="#8a9298")
    props.inked(nm + "_colchao", rrect(-0.92, 0.26, 0.92, 0.38, 0.03, 3), "#b8b19a", r, w=0.005, shade=0.012, shade_color="#8f8a76", rim=0.003, rim_color="#e8e2c8")
    props.inked(nm + "_trav", rrect(0.55, 0.38, 0.88, 0.46, 0.04, 3), "#d8d0bb", r, w=0.005, shade=0.008, shade_color="#aaa28c")
    if dobrada:
        props.inked(nm + "_manta", rrect(-0.9, 0.38, -0.45, 0.47, 0.03, 3), manta, r, w=0.005, shade=0.01, shade_color=_mix(manta, "#000000", 0.3), rim=0.003, rim_color=_mix(manta, "#ffffff", 0.35))
    else:
        props.inked(nm + "_manta", smooth([(-0.92, 0.36), (-0.9, 0.5), (-0.4, 0.55), (0.3, 0.5), (0.5, 0.42), (0.5, 0.36)], 4), manta, r, w=0.005, shade=0.012, shade_color=_mix(manta, "#000000", 0.3), rim=0.003, rim_color=_mix(manta, "#ffffff", 0.35))
    return r


def cadeira(nm, loc, s=1.0, parent=None):
    """cadeira de madeira simples, de frente (0,45 x 0,9 m)"""
    r = empty(nm, parent, loc); r.scale = (s, s, s)
    for k, x in enumerate((-0.19, 0.19)):
        props.inked(f"{nm}_perna{k}", rrect(x - 0.02, 0.0, x + 0.02, 0.45, 0.005, 2), MADEIRA_S, r, w=0.004)
        props.inked(f"{nm}_montante{k}", rrect(x - 0.02, 0.45, x + 0.02, 0.9, 0.005, 2), MADEIRA_S, r, loc=(0, 0.01, 0), w=0.004)
    props.inked(nm + "_assento", rrect(-0.23, 0.42, 0.23, 0.47, 0.01, 2), MADEIRA, r, loc=(0, -0.01, 0), w=0.005, shade=0.008, shade_color=MADEIRA_S, rim=0.003, rim_color=MADEIRA_L)
    props.inked(nm + "_encosto", rrect(-0.21, 0.66, 0.21, 0.78, 0.01, 2), MADEIRA, r, loc=(0, -0.012, 0), w=0.005, shade=0.008, shade_color=MADEIRA_S)
    return r


def jaqueta_pendurada(nm, loc, s=1.0, parent=None, cor="#4f6275"):
    """a jaqueta jeans da Lu pendurada no encosto: ombros caídos, mangas moles e a gola"""
    r = empty(nm, parent, loc); r.scale = (s, s, s)
    props.inked(nm + "_corpo", smooth([(-0.26, 0.0), (-0.28, 0.3), (-0.2, 0.42), (0.0, 0.46), (0.2, 0.42), (0.28, 0.3), (0.26, 0.0), (0.0, -0.02)], 4), cor, r, w=0.005, shade=0.014, shade_color=_mix(cor, "#000000", 0.3), rim=0.003, rim_color=_mix(cor, "#ffffff", 0.3))
    for k, sg in enumerate((-1, 1)):
        props.inked(f"{nm}_manga{k}", smooth([(sg * 0.26, 0.38), (sg * 0.33, 0.3), (sg * 0.34, 0.05), (sg * 0.29, 0.0), (sg * 0.25, 0.1)], 4), cor, r, loc=(0, -0.004, 0), w=0.005, shade=0.01, shade_color=_mix(cor, "#000000", 0.3))
    props.poly(nm + "_gola", [(-0.07, 0.45), (0.07, 0.45), (0.04, 0.34), (-0.04, 0.34)], _mix(cor, "#000000", 0.28), -0.006, r)
    props.poly(nm + "_ziper", stroke([(0.0, 0.34), (0.0, 0.0)], 0.0025), "#8a7a50", -0.007, r)
    return r


def caderno(nm, loc, s=1.0, parent=None):
    """caderno de capa dura aberto, com linhas de contas (0,3 x 0,22 m, visto de cima)"""
    r = empty(nm, parent, loc); r.scale = (s, s, s)
    props.inked(nm + "_capa", rrect(-0.16, 0.0, 0.16, 0.22, 0.008, 2), "#4a3a2a", r, w=0.004)
    for k, sg in enumerate((-1, 1)):
        props.inked(f"{nm}_pag{k}", rrect(sg * 0.075 - 0.07, 0.01, sg * 0.075 + 0.07, 0.21, 0.004, 2), "#d9d2bb", r, loc=(0, -0.004, 0), w=0.002)
        for j in range(8):
            props.poly(f"{nm}_l{k}{j}", rrect(sg * 0.075 - 0.055, 0.03 + 0.02 * j, sg * 0.075 + 0.055, 0.032 + 0.02 * j, 0.0, 1), "#6a6a5e", -0.007, r)
    return r


def lata_aberta(nm, loc, s=1.0, parent=None):
    """lata de conserva já aberta, com a tampa dobrada: o que a Lu divide com a ponta da faca"""
    r = lata(nm, (0, 0, 0), 1.0, None, "#8a4a2c"); r.parent = parent; r.location = loc; r.scale = (s, s, s)
    props.poly(nm + "_tampa", [(-0.037, 0.1), (0.037, 0.1), (0.05, 0.125), (-0.02, 0.115)], "#aab4bb", -0.006, r)
    return r


def faca(nm, loc, s=1.0, parent=None):
    r = empty(nm, parent, loc); r.scale = (s, s, s)
    props.inked(nm + "_lamina", [(0.0, 0.0), (0.16, 0.012), (0.16, 0.0)], "#c8ccd6", r, w=0.002, rim=0.0015, rim_color="#ffffff")
    props.inked(nm + "_cabo", rrect(-0.1, -0.006, 0.0, 0.016, 0.004, 2), "#2a2118", r, w=0.002)
    return r


def sueter_dobrado(nm, loc, s=1.0, parent=None):
    """o suéter de tricô da Pipoca, dobrado no fundo da gaiola (0,18 x 0,1 m)"""
    r = empty(nm, parent, loc); r.scale = (s, s, s)
    props.inked(nm + "_dob", smooth([(-0.09, 0.0), (-0.1, 0.05), (-0.05, 0.1), (0.05, 0.1), (0.1, 0.05), (0.09, 0.0)], 4), "#8e302b", r, w=0.003, shade=0.012, shade_color="#64211f", rim=0.003, rim_color="#b65048")
    props.poly(nm + "_lista", rrect(-0.095, 0.045, 0.095, 0.058, 0.002, 1), "#a89f86", -0.004, r)
    for k in range(8):
        props.poly(f"{nm}_pt{k}", stroke([(-0.08 + 0.023 * k, 0.005), (-0.078 + 0.023 * k, 0.04)], 0.0014), "#64211f", -0.005, r)
    props.poly(nm + "_gola", rrect(-0.03, 0.095, 0.03, 0.12, 0.008, 2), "#64211f", -0.004, r)
    return r


def gaiola_vazia(nm, loc, s=1.0, parent=None):
    """a gaiola da Pipoca com a porta aberta e o suéter dobrado no fundo"""
    r = gaiola(nm, loc, s, parent)
    sueter_dobrado(nm + "_su", (0.08, -0.02, 0.07), 1.0, r)
    props.inked(nm + "_porta", rrect(0.28, 0.1, 0.31, 0.36, 0.004, 1), "#aab4bb", r, loc=(0.0, -0.012, 0), w=0.003)
    return r


def privada(nm, loc, s=1.0, parent=None, transborda=1.0):
    """vaso sanitário de frente (0,4 x 0,75 m): caixa, tampa, bacia e uma poça escura que cresce no chão"""
    r = empty(nm, parent, loc); r.scale = (s, s, s)
    props.inked(nm + "_caixa", rrect(-0.2, 0.42, 0.2, 0.75, 0.025, 3), "#c9c4b0", r, loc=(0, 0.02, 0), w=0.005, shade=0.01, shade_color="#a39e8a", rim=0.003, rim_color="#efe9d0")
    props.inked(nm + "_bacia", smooth([(-0.19, 0.4), (0.19, 0.4), (0.2, 0.3), (0.12, 0.12), (0.1, 0.0), (-0.1, 0.0), (-0.12, 0.12), (-0.2, 0.3)], 4), "#d4cfba", r, w=0.005, shade=0.012, shade_color="#aaa58f", rim=0.003, rim_color="#f2edd6")
    props.poly(nm + "_agua", smooth([(-0.15, 0.4), (0.15, 0.4), (0.16, 0.36), (-0.16, 0.36)], 2), "#4f5e3a", -0.006, r)
    pc = empty(nm + "_poca", r, (0, -0.02, 0))
    props.poly(nm + "_poca_f", smooth([(-0.55, 0.0), (-0.3, 0.025), (0.3, 0.03), (0.6, 0.0), (0.3, -0.03), (-0.3, -0.025)], 3), "#3f4a2c", -0.002, pc)
    pc.scale = (transborda, 1, transborda)
    return r


def mosca2d(nm, loc, s=1.0, parent=None):
    """mosca de lado (2 cm): corpo escuro e duas asas claras; cresce com 's' para aparecer na ficha"""
    r = empty(nm, parent, loc); r.scale = (s, s, s)
    props.poly(nm + "_c", circle(0, 0, 0.007, 10), "#14110e", -0.002, r)
    for k, sg in enumerate((-1, 1)):
        props.poly(f"{nm}_a{k}", smooth([(sg * 0.002, 0.003), (sg * 0.012, 0.012), (sg * 0.014, 0.004)], 3), "#cfd6d0", -0.003, r)
    return r


def mesa_prato(nm, loc, s=1.0, parent=None, nivel="cheio"):
    """prato de frente sobre a mesa (visto de lado: elipse achatada) com a comida; mesma lógica do prato visto de cima"""
    r = empty(nm, parent, loc); r.scale = (s, s, s)
    props.inked(nm + "_prato", smooth([(-0.12, 0.012), (-0.1, 0.0), (0.1, 0.0), (0.12, 0.012), (0.08, 0.02), (-0.08, 0.02)], 3), "#e8e4d4", r, w=0.002, shade=0.004, shade_color="#bdb8a6")
    if nivel == "cheio":
        props.poly(nm + "_c", smooth([(-0.08, 0.02), (-0.05, 0.055), (0.02, 0.065), (0.07, 0.04), (0.08, 0.02)], 3), "#fffaf0", -0.003, r)
        props.poly(nm + "_c2", smooth([(0.0, 0.02), (0.03, 0.05), (0.07, 0.04), (0.07, 0.02)], 3), "#a9603a", -0.004, r)
    elif nivel == "pouco":
        props.poly(nm + "_c", smooth([(-0.03, 0.02), (-0.01, 0.034), (0.03, 0.03), (0.04, 0.02)], 3), "#fffaf0", -0.003, r)
    elif nivel == "carne":
        props.poly(nm + "_c", smooth([(-0.06, 0.02), (-0.04, 0.05), (0.03, 0.058), (0.07, 0.035), (0.06, 0.02)], 3), "#8a4a2c", -0.003, r)
        props.poly(nm + "_g", smooth([(0.0, 0.042), (0.03, 0.055), (0.05, 0.04), (0.02, 0.034)], 3), "#d9b48a", -0.004, r)
    return r


def poste_torto(nm, loc, s=1.0, parent=None, ang=18):
    """poste de luz vergado pela onda de choque (4,2 m), com o fio solto"""
    r = empty(nm, parent, loc); r.scale = (s, s, s); r.rotation_euler = (0, math.radians(ang), 0)
    props.inked(nm + "_poste", [(-0.07, 0.0), (0.07, 0.0), (0.045, 4.2), (-0.045, 4.2)], "#5a5a52", r, w=0.012, shade=0.03, shade_color="#3f3f38", rim=0.01, rim_color="#a8a490")
    props.inked(nm + "_braco", rrect(-0.04, 4.1, 0.9, 4.18, 0.02, 3), "#5a5a52", r, w=0.01)
    props.poly(nm + "_lampada", rrect(0.78, 4.0, 0.98, 4.1, 0.03, 3), "#3a3a34", -0.01, r)
    props.poly(nm + "_fio", stroke([(0.98, 4.05), (1.05, 3.4), (0.92, 2.9), (1.1, 2.4)], 0.008), "#14110e", -0.012, r)
    return r


def ruina(nm, loc, s=1.0, parent=None, cor="#6a665a", seed=1):
    """casa em pedaços (4 m): paredes quebradas em dentes, janela sem vidro, telhado caído e entulho no pé"""
    import random
    rnd = random.Random(seed)
    r = empty(nm, parent, loc); r.scale = (s, s, s)
    top = [(-2.0, 0.0), (-2.0, 2.2)]
    x = -2.0
    while x < 2.0:
        x += rnd.uniform(0.25, 0.6); top.append((min(x, 2.0), rnd.uniform(1.1, 2.6)))
    top += [(2.0, 0.0)]
    props.inked(nm + "_parede", top, cor, r, w=0.02)
    props.poly(nm + "_sombra", [(1.0, 0.0), (2.0, 0.0), (2.0, 2.2)] + [(x, z) for x, z in top[::-1] if x > 1.0][:0], _mix(cor, "#000000", 0.25), -0.01, r)
    props.poly(nm + "_janela", rrect(-0.9, 0.9, -0.2, 1.7, 0.02, 2), "#1c1c1a", -0.03, r)
    props.poly(nm + "_porta", rrect(0.5, 0.0, 1.2, 1.6, 0.02, 2), "#232320", -0.03, r)
    props.inked(nm + "_telha", [(-0.6, 1.0), (0.5, 0.3), (1.8, 0.0), (1.9, 0.14), (0.6, 0.5), (-0.5, 1.15)], "#5a4a3a", r, loc=(0, -0.05, 0), w=0.012)
    for k in range(7):
        props.poly(f"{nm}_ent{k}", smooth([(-2.2 + 0.7 * k, 0.0), (-2.0 + 0.7 * k, 0.18 + 0.1 * (k % 3)), (-1.7 + 0.7 * k, 0.1), (-1.6 + 0.7 * k, 0.0)], 3), _mix(cor, "#000000", 0.2 + 0.05 * (k % 3)), -0.06, r)
    return r
