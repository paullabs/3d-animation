"""Objetos do vídeo "E se o seu cérebro fosse 10 vezes mais rápido?" (mesmo acabamento de ficha: tinta, sombra e brilho por dentro).
Desenhados de frente (plano XZ), origem no centro da base. Os pequenos (copo, régua, bola, luvas, cronômetro) são mostrados
fora de escala na ficha; na cena entram com o tamanho real (copo 0,11 m, régua 0,30 m, bola 0,22 m)."""
import math
import cena, props, lib
from props import _mix
from lib import empty
from char2d import rrect
from puppet2d import circle, stroke
from objetos import caixa

TINTA = "#14110e"


def copo(nm, loc, s=1.0, parent=None, agua=0.62):
    """copo de vidro com água (0,08 x 0,11 m): vidro claro, água mais azul, brilho e borda"""
    r = empty(nm, parent, loc); r.scale = (s, s, s)
    corpo = [(-0.04, 0.11), (0.04, 0.11), (0.032, 0.0), (-0.032, 0.0)]
    props.inked(nm + "_vidro", corpo, "#cfeaf5", r, w=0.0028, shade=0.006, shade_color="#a9cfe0", rim=0.003, rim_color="#ffffff")
    h = 0.11 * agua; w = 0.04 - 0.008 * (1 - agua)
    props.poly(nm + "_agua", [(-0.0375 + 0.0 * h, h), (0.0375, h), (0.0322, 0.006), (-0.0322, 0.006)], "#6fb7e0", -0.003, r)
    props.poly(nm + "_nivel", rrect(-0.037, h - 0.004, 0.037, h, 0.001, 1), "#b6e2f7", -0.004, r)
    props.poly(nm + "_brilho", stroke([(-0.028, 0.095), (-0.022, 0.03)], 0.004), "#ffffff", -0.005, r)
    props.poly(nm + "_borda", rrect(-0.041, 0.106, 0.041, 0.112, 0.002, 2), "#eef9ff", -0.002, r)
    return r


def regua(nm, loc, s=1.0, parent=None):
    """régua de 30 cm na vertical: 0 embaixo (onde a mão pega), marcas a cada cm e números de 5 em 5.
    Uma faixa vermelha mostra os 3 mm e uma azul os 30 cm (a comparação do vídeo)."""
    r = empty(nm, parent, loc); r.scale = (s, s, s)
    props.inked(nm + "_corpo", rrect(-0.018, -0.004, 0.018, 0.304, 0.003, 2), "#e8d08a", r, w=0.002, shade=0.004, shade_color="#cdb36a", rim=0.002, rim_color="#fff3c4")
    for k in range(31):
        c = 0.01 * k
        comp = 0.016 if k % 5 == 0 else 0.009
        props.poly(f"{nm}_m{k}", rrect(-0.018 + 0.001, c - 0.0004, -0.018 + 0.001 + comp, c + 0.0004, 0.0001, 1), "#3a3226", -0.003, r)
    mat = props.FM("#3a3226")
    for k in (0, 10, 20, 30):
        t = lib.text(f"{nm}_n{k}", str(k), 0.016, mat, r, (0.0058, -0.0035, 0.01 * k + (0.012 if k == 0 else -0.008 if k == 30 else 0.0)), lib.font())
        t.rotation_euler = (math.pi / 2, 0, 0)
    props.poly(nm + "_tres", rrect(0.019, 0.0, 0.026, 0.003, 0.0004, 1), "#e2364b", -0.004, r)          # 3 mm
    props.poly(nm + "_trinta", rrect(0.019, 0.0, 0.026, 0.30, 0.0004, 1), "#2a6ad8", -0.004, r)         # 30 cm
    return r


def bola(nm, loc, s=1.0, parent=None):
    """bola de futebol (0,22 m): gomos escuros, costuras e brilho"""
    r = empty(nm, parent, loc); r.scale = (s, s, s)
    R = 0.11
    props.inked(nm + "_b", circle(0.0, R, R, 40), "#f4f1ea", r, w=0.004, shade=0.012, shade_color="#cfcabd", rim=0.004, rim_color="#ffffff")
    def pent(cx, cz, rr, rot):
        return [(cx + rr * math.cos(math.radians(rot + 72 * k)), cz + rr * math.sin(math.radians(rot + 72 * k))) for k in range(5)]
    props.poly(nm + "_c", pent(0.0, R, 0.036, 90), "#1c2230", -0.003, r)
    for k in range(5):
        a = math.radians(90 + 72 * k + 36)
        px, pz = 0.082 * math.cos(a), R + 0.082 * math.sin(a)
        props.poly(f"{nm}_p{k}", pent(px, pz, 0.026, math.degrees(a)), "#1c2230", -0.003, r)
        a0 = math.radians(90 + 72 * k)
        props.poly(f"{nm}_s{k}", stroke([(0.036 * math.cos(a0), R + 0.036 * math.sin(a0)), (0.062 * math.cos(a), R + 0.062 * math.sin(a))], 0.0028), "#1c2230", -0.003, r)
    props.poly(nm + "_br", stroke([(-0.06, R + 0.07), (-0.02, R + 0.095)], 0.007), "#ffffff", -0.005, r)
    return r


def luvas(nm, loc, s=1.0, parent=None):
    """par de luvas de goleiro (palma voltada para a gente): palma branca, dedos, polegar e punho laranja"""
    r = empty(nm, parent, loc); r.scale = (s, s, s)
    for k, dx in enumerate((-0.11, 0.11)):
        g = empty(f"{nm}_g{k}", r, (dx, 0, 0))
        props.inked(f"{nm}_pal{k}", rrect(-0.07, 0.08, 0.07, 0.2, 0.03, 4), "#f4f1ea", g, w=0.004, shade=0.01, shade_color="#d4cfc2", rim=0.004, rim_color="#ffffff")
        for i, x in enumerate((-0.052, -0.017, 0.017, 0.052)):
            h = 0.26 + 0.02 * (1 - abs(x) * 8)
            props.inked(f"{nm}_d{k}{i}", rrect(x - 0.015, 0.19, x + 0.015, h, 0.014, 3), "#f4f1ea", g, w=0.004)
        props.inked(f"{nm}_pol{k}", rrect(-0.11 if k == 0 else 0.07, 0.11, -0.07 if k == 0 else 0.11, 0.2, 0.014, 3), "#f4f1ea", g, w=0.004)
        props.inked(f"{nm}_pu{k}", rrect(-0.06, 0.0, 0.06, 0.085, 0.01, 2), "#e0602a", g, w=0.004, shade=0.008, shade_color="#b4491d")
        props.poly(f"{nm}_pq{k}", circle(0.0, 0.14, 0.03, 20), "#e8e2d2", -0.004, g)
        for i in range(3):
            props.poly(f"{nm}_ln{k}{i}", stroke([(-0.04, 0.1 + 0.03 * i), (0.04, 0.1 + 0.03 * i)], 0.003), "#cfcabd", -0.005, g)
    return r


def cronometro(nm, loc, s=1.0, parent=None, txt="0,025 s"):
    """medidor de reação: caixa escura com visor verde e botão vermelho"""
    r = empty(nm, parent, loc); r.scale = (s, s, s)
    props.inked(nm + "_c", rrect(-0.2, 0.0, 0.2, 0.26, 0.035, 5), "#232a37", r, w=0.01, shade=0.02, shade_color="#161b25", rim=0.008, rim_color="#8a90a0")
    props.poly(nm + "_visor", rrect(-0.165, 0.09, 0.165, 0.23, 0.02, 4), "#0f1a14", -0.003, r)
    t = lib.text(nm + "_t", txt, 0.085, props.FM("#8ff0a0", 1.4), r, (0.0, -0.006, 0.16), lib.font())
    t.rotation_euler = (math.pi / 2, 0, 0)
    props.poly(nm + "_bt", circle(-0.12, 0.045, 0.026, 18), "#e2364b", -0.004, r)
    props.poly(nm + "_bt2", circle(-0.05, 0.045, 0.026, 18), "#c8ccd6", -0.004, r)
    props.poly(nm + "_pe", rrect(0.04, 0.035, 0.17, 0.055, 0.005, 2), "#3a4356", -0.004, r)
    return r


def bloco_largada(nm, loc, s=1.0, parent=None):
    """bloco de largada de lado: trilho com espetos na pista e dois apoios inclinados de pé"""
    r = empty(nm, parent, loc); r.scale = (s, s, s)
    props.inked(nm + "_trilho", rrect(-0.28, 0.0, 0.28, 0.035, 0.008, 2), "#3a4356", r, w=0.005, shade=0.008, shade_color="#232a37", rim=0.004, rim_color="#9aa3b0")
    for k, x in enumerate((-0.25, 0.25)):
        props.poly(f"{nm}_esp{k}", [(x - 0.012, 0.0), (x + 0.012, 0.0), (x, -0.03)], "#c8ccd6", -0.003, r)
    props.inked(nm + "_a1", [(-0.2, 0.035), (-0.13, 0.035), (-0.06, 0.2), (-0.12, 0.215)], "#e0602a", r, w=0.005, shade=0.008, shade_color="#b4491d", rim=0.004, rim_color="#ffb48a")
    props.inked(nm + "_a2", [(0.04, 0.035), (0.11, 0.035), (0.17, 0.15), (0.11, 0.165)], "#e0602a", r, w=0.005, shade=0.008, shade_color="#b4491d", rim=0.004, rim_color="#ffb48a")
    for k, (a, b) in enumerate((((-0.18, 0.06), (-0.1, 0.19)), ((0.06, 0.06), (0.14, 0.14)))):
        props.poly(f"{nm}_t{k}", stroke([a, b], 0.006), "#7a2a10", -0.004, r)
    return r


def taca(nm, loc, s=1.0, parent=None):
    """taça dourada genérica (a Copa): bojo, haste, base com faixa verde e duas alças"""
    r = empty(nm, parent, loc); r.scale = (s, s, s)
    ouro, esc, luz = "#e8b84a", "#b88a22", "#fff0a8"
    props.inked(nm + "_base", rrect(-0.12, 0.0, 0.12, 0.05, 0.012, 3), esc, r, w=0.006, shade=0.008, shade_color="#8a6618", rim=0.004, rim_color=luz)
    props.poly(nm + "_faixa", rrect(-0.11, 0.018, 0.11, 0.034, 0.003, 1), "#1f9d55", -0.003, r)
    props.inked(nm + "_haste", [(-0.035, 0.05), (0.035, 0.05), (0.025, 0.2), (-0.025, 0.2)], ouro, r, w=0.006, shade=0.01, shade_color=esc, rim=0.004, rim_color=luz)
    bojo = [(-0.13, 0.4), (0.13, 0.4), (0.115, 0.3), (0.06, 0.22), (-0.06, 0.22), (-0.115, 0.3)]
    props.inked(nm + "_bojo", bojo, ouro, r, w=0.006, shade=0.02, shade_color=esc, rim=0.006, rim_color=luz)
    for k, sg in enumerate((-1, 1)):
        props.poly(f"{nm}_alca{k}", stroke([(sg * 0.125, 0.37), (sg * 0.185, 0.33), (sg * 0.15, 0.27)], 0.014), ouro, 0.003, r)
    props.poly(nm + "_brilho", stroke([(-0.085, 0.37), (-0.065, 0.28)], 0.012), luz, -0.005, r)
    return r


def telao_replay(nm, loc, s=1.0, parent=None):
    """telão do estádio passando a repetição: moldura, bola em movimento e botão de play"""
    r = empty(nm, parent, loc); r.scale = (s, s, s)
    props.inked(nm + "_m", rrect(-1.2, 0.0, 1.2, 1.4, 0.05, 4), "#1a1d26", r, w=0.02, shade=0.03, shade_color="#10131b", rim=0.012, rim_color="#8a90a0")
    props.poly(nm + "_t", rrect(-1.1, 0.1, 1.1, 1.3, 0.03, 3), "#2f6f4a", -0.004, r)
    for k in range(4):
        props.poly(f"{nm}_gr{k}", rrect(-1.1 + k * 0.55, 0.1, -0.83 + k * 0.55, 1.3, 0.0, 1), "#357a52", -0.005, r)
    props.poly(nm + "_gol", rrect(0.35, 0.1, 1.05, 0.62, 0.0, 1), "#1f4f35", -0.006, r)
    for k in range(5):
        props.poly(f"{nm}_tr{k}", circle(-0.85 + k * 0.17, 0.58 + 0.07 * k, 0.045 + 0.015 * k, 14), "#f4f1ea", -0.007 - 0.001 * k, r)
    props.poly(nm + "_play", [(-0.09, 0.45), (-0.09, 0.8), (0.18, 0.625)], "#ffffff", -0.01, r)
    mat = props.FM("#ffffff")
    t = lib.text(nm + "_rp", "REPLAY", 0.12, mat, r, (-0.65, -0.012, 1.18), lib.font()); t.rotation_euler = (math.pi / 2, 0, 0)
    props.poly(nm + "_rec", circle(-1.0, 1.18, 0.035, 12), "#ff3b4a", -0.008, r, strength=1.5)
    return r


def gol(nm, loc, s=1.0, parent=None):
    """gol visto de frente (7,32 x 2,44 m) com rede: travessão e traves brancos"""
    r = empty(nm, parent, loc); r.scale = (s, s, s)
    W, H = 7.32, 2.44
    props.poly(nm + "_fundo", rrect(-W / 2, 0.0, W / 2, H, 0.0, 1), "#2b3a44", 0.02, r)
    for k in range(1, 24):
        props.poly(f"{nm}_rv{k}", rrect(-W / 2 + k * W / 24 - 0.008, 0.0, -W / 2 + k * W / 24 + 0.008, H, 0.0, 1), "#7e8f9a", 0.01, r)
    for k in range(1, 8):
        props.poly(f"{nm}_rh{k}", rrect(-W / 2, k * H / 8 - 0.008, W / 2, k * H / 8 + 0.008, 0.0, 1), "#7e8f9a", 0.01, r)
    for k, x in enumerate((-W / 2, W / 2)):
        props.inked(f"{nm}_tr{k}", rrect(x - 0.06, 0.0, x + 0.06, H + 0.06, 0.02, 3), "#f4f1ea", r, loc=(0, -0.02, 0), w=0.015, shade=0.015, shade_color="#cfcabd", rim=0.01, rim_color="#ffffff")
    props.inked(nm + "_tv", rrect(-W / 2 - 0.06, H, W / 2 + 0.06, H + 0.12, 0.02, 3), "#f4f1ea", r, loc=(0, -0.02, 0), w=0.015, shade=0.015, shade_color="#cfcabd", rim=0.01, rim_color="#ffffff")
    return r


def camera_cabo(nm, loc, s=1.0, parent=None, rompe=True):
    """câmera de TV pendurada por cabos (estilo aérea): quatro cabos até o alto; um deles arrebenta (ponta esfiapada)"""
    r = empty(nm, parent, loc); r.scale = (s, s, s)
    props.inked(nm + "_corpo", rrect(-0.28, 0.0, 0.28, 0.34, 0.04, 5), "#2a2d36", r, w=0.012, shade=0.025, shade_color="#1a1c22", rim=0.01, rim_color="#8a90a0")
    props.inked(nm + "_lente", rrect(0.28, 0.06, 0.46, 0.26, 0.025, 4), "#1a1c22", r, w=0.012)
    props.poly(nm + "_vidro", circle(0.46, 0.16, 0.07, 22), "#5a8ad8", -0.004, r)
    props.poly(nm + "_rec", circle(-0.2, 0.3, 0.018, 12), "#ff3b4a", -0.004, r, strength=1.5)
    props.poly(nm + "_gim", rrect(-0.1, 0.34, 0.1, 0.4, 0.01, 2), "#3a4356", -0.003, r)
    for k, (x, z) in enumerate(((-0.8, 1.4), (0.8, 1.4), (-0.35, 1.5), (0.35, 1.5))):
        if rompe and k == 1:
            pts = [(0.08, 0.4), (0.3, 0.75), (0.45, 1.0)]
            props.poly(f"{nm}_cabo{k}", stroke(pts, 0.014), "#1a1c22", 0.002, r)
            esf = [(0.45, 1.0), (0.5, 1.06), (0.46, 1.08), (0.54, 1.14), (0.5, 1.15)]
            props.poly(f"{nm}_esf{k}", stroke(esf, 0.01), "#c8323e", 0.002, r)
        else:
            props.poly(f"{nm}_cabo{k}", stroke([(x * 0.1, 0.4), (x, z)], 0.014), "#1a1c22", 0.002, r)
    return r


def mesa_cozinha(nm, loc, s=1.0):
    """mesa de cozinha de madeira (1,1 x 0,7 m, altura 0,74) para o copo cair da borda"""
    x, y, z = loc
    caixa(nm + "_tampo", x, y, z + 0.7 * s, 1.1 * s, 0.045 * s, 0.7 * s, "#a67c52", tampo="#c89868", aresta="#e8c898")
    for k, (dx, dy) in enumerate(((-0.5, 0.04), (0.5, 0.04), (-0.5, 0.58), (0.5, 0.58))):
        caixa(f"{nm}_pe{k}", x + dx * s, y + dy * s, z, 0.055 * s, 0.7 * s, 0.055 * s, "#6e4e32")
    return None


def torcida(nm, loc, s=1.0, n=7):
    """sete torcedores de silhueta em cores de camisa diferentes (para a arquibancada se levantando)"""
    x, y, z = loc
    cores = ["#1f9d55", "#f2c94c", "#2a5acb", "#e0602a", "#f4f1ea", "#1f9d55", "#e2364b"]
    for k in range(n):
        props.pessoa(f"{nm}_{k}", x + (k - (n - 1) / 2) * 0.55 * s, y, cores[k % len(cores)], 0.9 * s, flip=1 if k % 2 else -1, z=z, rim="#ffe9c8")
