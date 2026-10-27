"""Kit de cenário rico da noite de "O abrigo" parte 2 (26/10/2026, guia: personagem/abrigo/guia-luz-e-suspense.md).
Três camadas por cena (primeiro plano, ação, fundo), luz com motivo (janela acesa âmbar, poste, lanterna) e partículas.
Convenção: coordenadas do mundo, z para cima; o beco corre ao longo de x entre as paredes y=y0-larg/2 (face para +y) e y=y0+larg/2 (face para -y).
beco_rico(), loja_escura(), poste(), carro(), neblina_x(), neblina_y(), poca_agua(), janela(), varal(), escada_incendio(), pichacao(), predios_ao_fundo()"""
import math, random
import bpy
from mathutils import Vector
import lib
import cena, props
import heroi3d as H3
import objetos3d_abrigo as O3
import objetos3d_abrigo_b as O3B

QUENTE, QUENTE_BR = "#ffcf7a", "#d9b66a"
M = O3.M


def _mat(cor, s=None, b=None):
    return M(cor, s, b or "#9a9c92")


# ---------------------------------------------------------------- luz
def poca_de_luz(nome, x, y, rx=1.2, ry=0.9, alfa=0.38, cor=QUENTE_BR):
    return cena.ground_disc(nome, rx, ry, cena.amat(nome + "_m", cor, 1.0, alfa, ("radial", 1.2)), (x, y, 0.006), n=32)


def feixe(nome, p0, p1, larg0=0.5, larg1=1.6, alfa=0.16, cor=QUENTE_BR, eixo="y"):
    """feixe de luz translúcido de um ponto alto (p0) até o chão (p1): quadrilátero em pé, aberto no chão"""
    m = cena.amat(nome + "_m", cor, 1.0, alfa, ("shaft", 1.2, 0.4)) if False else cena.amat(nome + "_m", cor, 1.0, alfa, ("radial", 1.1))
    (x0, y0, z0), (x1, y1, z1) = p0, p1
    if eixo == "y":
        v = [(x0 - larg0 / 2, y0, z0), (x0 + larg0 / 2, y0, z0), (x1 + larg1 / 2, y1, z1), (x1 - larg1 / 2, y1, z1)]
    else:
        v = [(x0, y0 - larg0 / 2, z0), (x0, y0 + larg0 / 2, z0), (x1, y1 + larg1 / 2, z1), (x1, y1 - larg1 / 2, z1)]
    return cena.poly_mesh(nome, v, m)


def neblina_x(xs, y0, y1, alfa=0.1, cor="#7b86a4", z1=7.0, nome="nx"):
    """véus de névoa perpendiculares ao beco (em cada x): o que está atrás fica mais apagado (perspectiva atmosférica)"""
    for k, x in enumerate(xs):
        cena.poly_mesh(f"{nome}{k}", [(x, y0, 0.0), (x, y1, 0.0), (x, y1, z1), (x, y0, z1)], cena.amat(f"{nome}{k}_m", cor, 1.0, alfa))


def neblina_y(ys, x0, x1, alfa=0.1, cor="#7b86a4", z1=9.0, nome="ny"):
    for k, y in enumerate(ys):
        cena.poly_mesh(f"{nome}{k}", [(x0, y, 0.0), (x1, y, 0.0), (x1, y, z1), (x0, y, z1)], cena.amat(f"{nome}{k}_m", cor, 1.0, alfa))


def poste(nome, x, y, acesa=True, alt=4.6, cor_luz=QUENTE, rot=0.0, braco=0.9):
    r = lib.empty(nome, None, (x, y, 0)); r.rotation_euler.z = math.radians(rot)
    m = _mat("#3a3c40", "#2a2c30")
    O3.cilindro(nome + "_p", 0.07, alt, m, r, (0, 0, alt / 2), seg=12)
    H3.tubo(nome + "_b", [(0, 0, alt), (0, 0, alt + 0.15), (braco * 0.5, 0, alt + 0.3), (braco, 0, alt + 0.22)], [0.045, 0.04, 0.035, 0.03], m, r, seg=10, tampa=4, contorno=0.003)
    O3.caixa(nome + "_c", (0.34, 0.16, 0.1), m, r, (braco, 0, alt + 0.18), chanfro=0.02)
    if acesa:
        O3.caixa(nome + "_l", (0.28, 0.12, 0.03), O3.brilha(cor_luz, 2.0), r, (braco, 0, alt + 0.11), chanfro=0.0, contorno=0.0)
        O3.halo_cam(nome + "_halo", (braco, 0, alt + 0.05), 1.3, QUENTE_BR, 0.5, pai=r)
        feixe(nome + "_fx", (x + braco, y, alt), (x + braco, y, 0.0), 0.5, 3.4, 0.06, eixo="y")
        poca_de_luz(nome + "_pool", x + braco, y, 1.9, 1.5, 0.4)
    return r


def carro(nome, x, y, rot=0.0, cor="#5a5e66", queimado=False):
    r = lib.empty(nome, None, (x, y, 0)); r.rotation_euler.z = math.radians(rot)
    c = "#2c2c2e" if queimado else cor
    O3.caixa(nome + "_c", (4.2, 1.8, 0.7), _mat(c), r, (0, 0, 0.62), chanfro=0.12)
    O3.caixa(nome + "_t", (2.2, 1.6, 0.6), _mat(c), r, (-0.2, 0, 1.2), chanfro=0.14)
    for k, (dx, dy) in enumerate(((-1.4, -0.9), (1.4, -0.9), (-1.4, 0.9), (1.4, 0.9))):
        O3.cilindro(f"{nome}_r{k}", 0.34, 0.22, _mat("#18181a", "#0e0e10"), r, (dx, dy, 0.34), eixo="Y")
    O3.caixa(nome + "_vid", (1.9, 1.62, 0.34), O3.vidro("#aab8c4", 0.25, 0.5), r, (-0.2, 0, 1.26), chanfro=0.0, contorno=0.0)
    return r


def poca_agua(nome, x, y, rx=0.9, ry=0.55, cor="#3a4a66", brilho=None, seed=1):
    """poça d'água parada: espelho escuro azulado; brilho = (cor, alfa) cria o reflexo da luz acima (uma faixa clara)"""
    pts = O3B.blob(x, y, rx, ry, z=0.008, n=22, seed=seed, ruido=0.22)
    cena.poly_mesh(nome, pts, props.FM(cor))
    if brilho:
        cena.ground_disc(nome + "_ref", rx * 0.5, ry * 0.45, cena.amat(nome + "_refm", brilho[0], 1.2, brilho[1], ("radial", 1.1)), (x, y, 0.011), n=24)


# ---------------------------------------------------------------- parede e fachada
def mancha_parede(nome, x, z, w, h, y_face, normal, cor="#4a4c46", alfa=0.5, seed=1):
    pts = O3B.blob(0, 0, w / 2, h / 2, z=0.0, n=16, seed=seed, ruido=0.3)
    v = [(x + px, y_face + normal * 0.012, z + py) for px, py, _ in pts]
    cena.poly_mesh(nome, v, cena.amat(nome + "_m", cor, 1.0, alfa))


def tijolos(nome, x0, x1, y_face, normal, z1=5.0, seed=1):
    """as juntas dos tijolos (linhas escuras) e alguns tijolos faltando: a parede deixa de ser uma caixa lisa"""
    rnd = random.Random(seed)
    L = abs(x1 - x0); cx = (x0 + x1) / 2
    for k in range(int(z1 / 0.28)):
        O3.caixa(f"{nome}_j{k}", (L, 0.012, 0.012), _mat("#53554e"), None, (cx, y_face + normal * 0.008, 0.28 * k + 0.14), chanfro=0.0, contorno=0.0)
    for k in range(26):
        x = rnd.uniform(min(x0, x1) + 0.3, max(x0, x1) - 0.3); z = rnd.uniform(0.3, z1 - 0.3)
        O3.caixa(f"{nome}_b{k}", (rnd.uniform(0.22, 0.5), 0.02, 0.14), _mat("#4a4c46", "#3a3c37"), None, (x, y_face + normal * 0.012, z), chanfro=0.0, contorno=0.0)
    for k in range(7):
        mancha_parede(f"{nome}_m{k}", rnd.uniform(min(x0, x1) + 0.5, max(x0, x1) - 0.5), rnd.uniform(0.6, z1 - 0.5), rnd.uniform(0.6, 1.6), rnd.uniform(0.5, 1.4), y_face, normal,
                      seed=seed + k)


def janela(nome, x, z, y_face, normal, acesa=True, cortina="#b5a07c", w=0.9, h=1.3, sombra=False):
    """janela de prédio: moldura, vidro (âmbar emissivo se acesa), cortina, brilho em volta; sombra = uma silhueta que passa atrás da cortina"""
    y = y_face + normal * 0.06
    O3.caixa(nome + "_mold", (w + 0.2, 0.12, h + 0.2), _mat("#3a3c40", "#2a2c30"), None, (x, y, z), chanfro=0.02)
    if acesa:
        O3.caixa(nome + "_vid", (w, 0.05, h), O3.brilha(QUENTE, 1.5), None, (x, y + normal * 0.05, z), chanfro=0.0, contorno=0.0)
        O3.caixa(nome + "_cort", (w * 0.55, 0.04, h * 0.9), _mat(cortina, "#8c7c5c"), None, (x - w * 0.22, y + normal * 0.08, z), chanfro=0.0, contorno=0.0)
        if sombra:
            O3.caixa(nome + "_sil", (0.22, 0.03, 0.62), O3.M("#23190f", "#23190f", "#23190f"), None, (x + w * 0.18, y + normal * 0.1, z - 0.15), chanfro=0.03, contorno=0.0)
            H3.esfera(nome + "_silc", 0.1, 0.02, 0.11, O3.M("#23190f", "#23190f", "#23190f"), None, (x + w * 0.18, y + normal * 0.1, z + 0.28), contorno=0.0, seg=14, an=10)
        O3.halo_cam(nome + "_halo", (x, y + normal * 0.4, z), 1.5, QUENTE_BR, 0.42)
        pass
    else:
        O3.caixa(nome + "_vid", (w, 0.05, h), O3.vidro("#4a5568", 0.5, 0.6), None, (x, y + normal * 0.05, z), chanfro=0.0, contorno=0.0)


def janela_x(nome, x, z, y_face, normal, **k):
    janela(nome, x, z, y_face, normal, **k)


def varal(nome, x, y0, y1, z=3.9, seed=3):
    """varal de roupas atravessando o beco (de y0 a y1): corda mole e camisas, calças e um lençol pendurados"""
    rnd = random.Random(seed)
    pts = [(x, y0 + (y1 - y0) * t / 10, z - 0.28 * math.sin(math.pi * t / 10)) for t in range(11)]
    H3.tubo(nome + "_corda", pts, [0.008] * 11, _mat("#6a665a"), None, seg=6, tampa=2, contorno=0.0)
    cores = ["#8a4a3a", "#4a6a8a", "#c9c2a8", "#6a8a5a", "#a0805a", "#7a5a8a"]
    for k in range(6):
        t = (k + 0.7) / 6.8
        yy = y0 + (y1 - y0) * t; zz = z - 0.28 * math.sin(math.pi * t) - 0.3
        w, h = rnd.choice(((0.5, 0.6), (0.4, 0.8), (0.9, 0.7)))
        O3.caixa(f"{nome}_r{k}", (0.03, w, h), _mat(cores[k]), None, (x, yy, zz), chanfro=0.0, contorno=0.002, rot=(rnd.uniform(-6, 6), 0, rnd.uniform(-5, 5)))


def fios(nome, x, y0, y1, z=4.7, n=3, seed=2):
    rnd = random.Random(seed)
    for k in range(n):
        xx = x + rnd.uniform(-0.15, 0.15); zz = z + rnd.uniform(-0.2, 0.2)
        pts = [(xx, y0 + (y1 - y0) * t / 10, zz - 0.4 * math.sin(math.pi * t / 10)) for t in range(11)]
        H3.tubo(f"{nome}{k}", pts, [0.012] * 11, _mat("#1c1c20", "#101012"), None, seg=6, tampa=2, contorno=0.0)


def cano_horizontal(nome, x0, x1, y_face, normal, z=3.2, r=0.07):
    O3.cilindro(nome, r, abs(x1 - x0), _mat("#4a4c52", "#34363c"), None, ((x0 + x1) / 2, y_face + normal * (r + 0.02), z), eixo="X", seg=12)
    for k in range(int(abs(x1 - x0) / 2.2)):
        O3.caixa(f"{nome}_s{k}", (0.1, 0.1 + r, 0.1), _mat("#2e3034"), None, (min(x0, x1) + 1.1 + k * 2.2, y_face + normal * 0.05, z), chanfro=0.01)


def escada_incendio(nome, x, y_face, normal, z=3.1, comp=2.6):
    """escada de incêndio: plataforma de grade, guarda-corpo e a escada em diagonal até quase o chão"""
    m = _mat("#34363a", "#24262a")
    yy = y_face + normal * 0.5
    O3.caixa(nome + "_pl", (comp, 0.9, 0.06), m, None, (x, yy, z), chanfro=0.01)
    for k in range(7):
        H3.tubo(f"{nome}_g{k}", [(x - comp / 2 + k * comp / 6, yy + normal * 0.42, z), (x - comp / 2 + k * comp / 6, yy + normal * 0.42, z + 0.95)], [0.014] * 2, m, None, seg=6, tampa=2, contorno=0.0)
    H3.tubo(nome + "_corr", [(x - comp / 2, yy + normal * 0.42, z + 0.95), (x + comp / 2, yy + normal * 0.42, z + 0.95)], [0.02] * 2, m, None, seg=8, tampa=2, contorno=0.0)
    for k in range(9):
        t = k / 8
        O3.caixa(f"{nome}_d{k}", (0.1, 0.7, 0.04), m, None, (x + comp / 2 + 0.2 + 0.55 * t, yy, z - 0.28 - (z - 0.9) * t), chanfro=0.0)


def pichacao(nome, texto, x, z, y_face, normal, tam=0.35, cor="#a8322a", rot=0.0):
    t = lib.text(nome, texto, tam, O3.brilha(cor, 0.9), None, (x, y_face + normal * 0.03, z))
    t.rotation_euler = (math.radians(90), 0, math.radians(180 if normal > 0 else 0) + math.radians(rot))
    t.data.font = lib.font()
    return t


# ---------------------------------------------------------------- objetos de rua (os que contam quem morava ali)
def lixeira(nome, x, y, tampa=True, rot=0.0):
    r = lib.empty(nome, None, (x, y, 0)); r.rotation_euler.z = math.radians(rot)
    O3.cilindro(nome + "_c", 0.32, 0.9, _mat("#4a5a4e", "#34423a"), r, (0, 0, 0.45), r2=0.28, seg=20)
    if tampa:
        O3.cilindro(nome + "_t", 0.34, 0.06, _mat("#3a463e"), r, (0.04, 0.0, 0.93), seg=20)
    return r


def saco(nome, x, y, s=1.0, cor="#2c2e30"):
    H3.esfera(nome, 0.3 * s, 0.26 * s, 0.24 * s, _mat(cor, "#1c1e20"), None, (x, y, 0.2 * s), contorno=0.004, seg=16, an=10)


def caixote(nome, x, y, rot=0.0, n=1, cor="#7a6448"):
    for k in range(n):
        O3.caixa(f"{nome}{k}", (0.6, 0.45, 0.42), _mat(cor, "#5a4632"), None, (x, y, 0.21 + 0.42 * k), chanfro=0.015, rot=(0, 0, rot + 12 * k))


def barril(nome, x, y, cor="#5a4a3a"):
    O3.cilindro(nome, 0.28, 0.86, _mat(cor, "#3e3226"), None, (x, y, 0.43), seg=20)
    O3.anel(nome + "_a", 0.285, 0.012, _mat("#34281e"), None, (x, y, 0.3), eixo="Z")


def carrinho(nome, x, y, rot=0.0):
    """carrinho de supermercado virado de lado (o mundo parou no meio da compra)"""
    r = lib.empty(nome, None, (x, y, 0.3)); r.rotation_euler = (math.radians(70), 0, math.radians(rot))
    m = _mat("#9a9ea4", "#6a6e74")
    O3.caixa(nome + "_c", (0.9, 0.5, 0.04), m, r, (0, 0, 0), chanfro=0.0)
    for k in range(5):
        H3.tubo(f"{nome}_g{k}", [(-0.45 + k * 0.225, -0.25, 0), (-0.45 + k * 0.225, -0.25, 0.5)], [0.01] * 2, m, r, seg=6, tampa=2, contorno=0.0)
        H3.tubo(f"{nome}_h{k}", [(-0.45 + k * 0.225, 0.25, 0), (-0.45 + k * 0.225, 0.25, 0.5)], [0.01] * 2, m, r, seg=6, tampa=2, contorno=0.0)
    H3.tubo(nome + "_alca", [(-0.45, -0.25, 0.5), (-0.7, -0.25, 0.62), (-0.7, 0.25, 0.62), (-0.45, 0.25, 0.5)], [0.016] * 4, m, r, seg=8, tampa=3, contorno=0.0)


def papeis(nome, x, y, raio=2.5, n=14, seed=4):
    rnd = random.Random(seed)
    for k in range(n):
        a = rnd.uniform(0, 6.28); d = rnd.uniform(0, raio)
        O3.caixa(f"{nome}{k}", (rnd.uniform(0.12, 0.3), rnd.uniform(0.1, 0.22), 0.004), _mat(rnd.choice(("#c9c6b4", "#a8a594", "#b8a888"))), None,
                 (x + d * math.cos(a), y + d * math.sin(a), 0.012), chanfro=0.0, contorno=0.0, rot=(0, 0, rnd.uniform(0, 360)))


def vapor(nome, x, y, alt=2.2, alfa=0.14):
    """vapor de bueiro: a tampa de ferro e nuvens suaves (brilho redondo que olha para a câmera), sem colunas de vidro"""
    O3.cilindro(nome + "_bueiro", 0.4, 0.04, _mat("#2a2c30"), None, (x, y, 0.02), seg=20)
    O3.halo_cam(f"{nome}_n0", (x, y, 0.7), 0.5, "#c9d2dc", 0.08)


def luzes_festa(nome, x, y0, y1, z=4.2, n=10, seed=3):
    """fio de lâmpadas de festa atravessando o beco (sobra do tempo antes da bomba): bolinhas acesas âmbar e brancas que viram 'bokeh' no fundo desfocado"""
    rnd = random.Random(seed)
    pts = [(x, y0 + (y1 - y0) * t / 10, z - 0.35 * math.sin(math.pi * t / 10)) for t in range(11)]
    H3.tubo(nome + "_fio", pts, [0.006] * 11, _mat("#1c1c20"), None, seg=6, tampa=2, contorno=0.0)
    for k in range(n):
        t = (k + 0.5) / n
        yy = y0 + (y1 - y0) * t; zz = z - 0.35 * math.sin(math.pi * t) - 0.06
        cor = rnd.choice(("#ffcf7a", "#ffe3a8", "#ffb25a", "#f2f0e0"))
        H3.esfera(f"{nome}_b{k}", 0.045, 0.045, 0.055, O3.brilha(cor, 2.2), None, (x, yy, zz), contorno=0.0, seg=14, an=10)
        if k % 3 == 0:
            O3.halo_cam(f"{nome}_h{k}", (x, yy, zz), 0.22, cor, 0.5)


def reflexo_na_poca(nome, x, y, rx=0.3, ry=0.9, olhos=True):
    """o reflexo escuro e esticado do monstro na poça (chega antes do corpo) com dois pontos claros no lugar dos olhos"""
    cena.ground_disc(nome, rx, ry, cena.amat(nome + "_m", "#05060a", 1.0, 0.75, ("radial", 0.9)), (x, y, 0.013), n=28)
    if olhos:
        for sy in (-0.07, 0.07):
            cena.ground_disc(f"{nome}_o{sy}", 0.035, 0.045, cena.amat(f"{nome}_om{sy}", "#cfd6e0", 2.0, 0.9, ("radial", 0.8)), (x - 0.55, y + sy, 0.015), n=12)


def padaria(nome, x, y, w=5.0):
    """a padaria da padeira (a mesma do ep. 1): letreiro PADARIA, toldo listrado, vitrine quebrada e a luz de emergência âmbar no fundo; a frente olha para -y"""
    r = loja_escura(nome, x, y, 0.0, w)
    O3.caixa(nome + "_letr", (w * 0.7, 0.12, 0.62), _mat("#3f5a47", "#2a3e30"), None, (x, y - 0.12, 3.35), chanfro=0.02)
    t = lib.text(nome + "_txt", "PADARIA", 0.46, O3.brilha("#e8dcc0", 0.7), None, (x, y - 0.2, 3.35))
    t.rotation_euler = (math.radians(90), 0, 0); t.data.font = lib.font()
    for k in range(10):                                                    # o toldo listrado (vermelho e creme)
        O3.caixa(f"{nome}_tl{k}", (w / 10 + 0.01, 1.3, 0.05), _mat("#a8453a" if k % 2 == 0 else "#d8cdb0", "#7a2e26" if k % 2 == 0 else "#a89c80"), None,
                 (x - w / 2 + w / 20 + k * w / 10, y - 0.65, 3.0), chanfro=0.0, rot=(-14, 0, 0))
    for k, dx in enumerate((-1.6, 1.7)):                                   # um pão na vitrine e uma bandeja caída
        O3.caixa(f"{nome}_pao{k}", (0.4, 0.2, 0.14), _mat("#8a6a3a", "#5a4424"), None, (x + dx, y + 0.9, 1.07), chanfro=0.05)
    return r


# ---------------------------------------------------------------- conjuntos
def predios_ao_fundo(x0, x1, y, n=14, seed=7, acesas=0.25, altura=(5, 14), nome="pf"):
    """a silhueta da cidade ao fundo, com janelas (umas acesas em âmbar) e o topo quebrado: profundidade e vida longe"""
    rnd = random.Random(seed)
    for k in range(n):
        x = x0 + (x1 - x0) * (k + rnd.uniform(0.1, 0.9)) / n; w = rnd.uniform(4, 8); hh = rnd.uniform(*altura)
        O3.caixa(f"{nome}{k}", (w, 5.0, hh), _mat("#4e515c", "#3a3d46", "#6a6e7a"), None, (x, y + rnd.uniform(-2, 2), hh / 2), chanfro=0.0, contorno=0.0, rot=(0, rnd.uniform(-2, 2), rnd.uniform(-4, 4)))
        yf = y - 2.55
        for r_ in range(int(hh / 1.6)):
            for c_ in range(int(w / 1.5)):
                if rnd.random() < 0.45:
                    xx = x - w / 2 + 0.8 + c_ * 1.5; zz = 1.2 + r_ * 1.6
                    ac = rnd.random() < acesas
                    O3.caixa(f"{nome}{k}_w{r_}_{c_}", (0.7, 0.05, 0.9), O3.brilha(QUENTE, 1.2) if ac else _mat("#252932", "#1a1d24"), None, (xx, yf, zz), chanfro=0.0, contorno=0.0)


def beco_rico(x0=-4.5, x1=-16.0, y=6.5, larg=3.0, seed=5, altura=7.0):
    """o beco: paredes de tijolo com juntas e manchas, janelas (duas acesas, uma com sombra que passa), escada de incêndio, canos, varal, fios, lixo, carrinho,
    poças com o reflexo das janelas, vapor, papéis e pichações. As paredes estão em y-larg/2 (face para +y) e y+larg/2 (face para -y)."""
    ya, yb = y - larg / 2, y + larg / 2
    ia, ib = ya + 0.25, yb - 0.25                                  # as faces de dentro
    L = abs(x1 - x0); cx = (x0 + x1) / 2
    for k, yy in enumerate((ya, yb)):
        O3.caixa(f"beco{k}", (L, 0.5, altura), _mat("#7a7c74", "#5a5c55", "#9a9c92"), None, (cx, yy, altura / 2), chanfro=0.0)
    xs = (min(x0, x1), max(x0, x1))
    tijolos("tjA", xs[0], xs[1], ia, +1, seed=seed); tijolos("tjB", xs[0], xs[1], ib, -1, seed=seed + 9)
    # janelas: parede A (face +y): acesa e apagadas; parede B (face -y): acesa com sombra
    for k, (xx, zz, ac, sb) in enumerate(((-7.0, 4.4, True, False), (-9.8, 3.2, False, False), (-12.5, 4.6, True, True), (-14.8, 3.0, False, False))):
        janela(f"jA{k}", xx, zz, ia, +1, acesa=ac, sombra=sb)
    for k, (xx, zz, ac, sb) in enumerate(((-6.0, 3.0, False, False), (-8.6, 4.6, True, True), (-11.4, 3.2, True, False), (-14.0, 4.5, False, False))):
        janela(f"jB{k}", xx, zz, ib, -1, acesa=ac, sombra=sb)
    for k, (xx, ac) in enumerate(((-6.4, True), (-11.2, False), (-9.4, True))):          # janelas do térreo: viram bolas de luz âmbar quando a câmera fecha no rosto
        janela(f"jTA{k}", xx, 1.9, ia, +1, acesa=ac, w=0.8, h=1.0)
    for k, (xx, ac) in enumerate(((-7.4, True), (-12.6, True), (-10.0, False))):
        janela(f"jTB{k}", xx, 1.9, ib, -1, acesa=ac, w=0.8, h=1.0)
    cano_horizontal("cA", xs[0] + 0.3, xs[1] - 0.3, ia, +1, z=2.6); cano_horizontal("cB", xs[0] + 0.3, xs[1] - 0.3, ib, -1, z=5.4, r=0.05)
    for k, xx in enumerate((-7.6, -13.4)):
        O3.cilindro(f"dren{k}", 0.05, 4.4, _mat("#4a4c52", "#34363c"), None, (xx, ia + 0.07, 2.3), seg=10)
    escada_incendio("esc", -10.4, ib, -1, z=3.4)
    varal("var", -9.0, ia + 0.05, ib - 0.05, z=4.2); varal("var2", -12.6, ia + 0.05, ib - 0.05, z=4.9, seed=8)
    fios("fio", -7.8, ia, ib, n=4, seed=3); fios("fio2", -14.2, ia, ib, n=3, seed=4)
    # chão: lixo, carrinho, poças, papéis, vapor
    lixeira("lx1", -5.7, ia + 0.4); lixeira("lx2", -13.6, ib - 0.4, tampa=False, rot=40); saco("sc1", -6.4, ia + 0.4); saco("sc2", -6.9, ia + 0.5, 0.8); saco("sc3", -13.0, ib - 0.5, 1.1)
    caixote("cx", -8.4, ia + 0.4, n=2); caixote("cy", -15.2, ib - 0.4, 45, n=1); barril("br", -11.2, ia + 0.4); carrinho("car", -10.8, ib - 0.7, 10)
    poca_agua("pq1", -7.0, y, 1.0, 0.6, brilho=(QUENTE, 0.32), seed=2); poca_agua("pq2", -12.4, y + 0.3, 1.2, 0.5, brilho=(QUENTE, 0.3), seed=5); poca_agua("pq3", -9.8, y - 0.2, 0.7, 0.4, seed=7)
    papeis("pap", -10.0, y, 5.5, 18); vapor("vp", -8.0, ib - 0.5)
    pichacao("pc1", "NÃO RESPIRE", -8.0, 1.5, ia, +1, tam=0.32); pichacao("pc2", "ABRIGO 3  >", -12.2, 1.1, ib, -1, tam=0.3, cor="#c9c2a8")
    poca_de_luz("luzA", -7.0, y, 1.4, 1.2); poca_de_luz("luzB", -12.4, y, 1.5, 1.2)
    for k, xx in enumerate((-6.4, -8.2, -10.4, -13.4)):
        luzes_festa(f"fe{k}", xx, ia + 0.05, ib - 0.05, z=4.6 - 0.3 * (k % 2), seed=3 + k)
    neblina_x([x0 - 2.5 * k for k in range(1, 5)], ya, yb, alfa=0.09, z1=altura)


def loja_escura(nome, x, y, rot=0.0, w=5.0):
    """loja de esquina com a vitrine quebrada: balcão, prateleiras vazias e UMA luz de emergência âmbar no fundo; os dois olhos (acende no plano 3C)
    ficam atrás do balcão. A frente da loja olha para -y (ajuste por rot)."""
    r = lib.empty(nome, None, (x, y, 0)); r.rotation_euler.z = math.radians(rot)
    par = _mat("#6e7068", "#52544d")
    O3.caixa(nome + "_fundo", (w, 0.3, 3.6), par, r, (0, 2.6, 1.8), chanfro=0.0)
    for s_ in (-1, 1):
        O3.caixa(f"{nome}_lat{s_}", (0.3, 2.8, 3.6), par, r, (s_ * w / 2, 1.3, 1.8), chanfro=0.0)
    O3.caixa(nome + "_teto", (w, 2.8, 0.3), par, r, (0, 1.3, 3.75), chanfro=0.0)
    O3.caixa(nome + "_chao", (w, 2.8, 0.06), _mat("#4a4c46"), r, (0, 1.3, 0.03), chanfro=0.0, contorno=0.0)
    O3.caixa(nome + "_bal", (3.0, 0.7, 1.0), _mat("#5a4632", "#3e3024"), r, (0.4, 1.3, 0.5), chanfro=0.02)
    for k in range(3):
        O3.caixa(f"{nome}_pr{k}", (w - 0.8, 0.3, 0.04), _mat("#4a3a2a"), r, (0, 2.38, 0.9 + 0.7 * k), chanfro=0.0)
        for j in range(3):
            if (j + k) % 2 == 0:
                O3.caixa(f"{nome}_lt{k}{j}", (0.3, 0.18, 0.26), _mat(("#8a4a3a", "#4a6a8a", "#c9c2a8")[j]), r, (-1.4 + j * 1.2, 2.36, 1.05 + 0.7 * k), chanfro=0.01)
    O3.caixa(nome + "_ceg", (0.7, 0.05, 0.14), O3.brilha("#ffbf66", 1.6), r, (0.0, 2.43, 2.9), chanfro=0.0, contorno=0.0)   # luz de emergência
    O3.halo_cam(nome + "_halo", (0.0, 2.2, 2.9), 2.2, QUENTE_BR, 0.5, pai=r)
    # vitrine quebrada: moldura e cacos
    O3.caixa(nome + "_vit", (w - 0.2, 0.06, 2.0), O3.vidro("#aab8c4", 0.16, 0.5), r, (0, -0.1, 1.5), chanfro=0.0, contorno=0.0)
    for k, (cx, cz) in enumerate(((-1.2, 0.9), (0.8, 1.3), (1.6, 0.6), (-0.3, 1.8))):
        H3.tubo(f"{nome}_rach{k}", [(cx, -0.14, cz), (cx + 0.5, -0.14, cz + 0.4), (cx + 0.2, -0.14, cz + 0.9)], [0.007] * 3, O3.brilha("#dfe7ea", 0.7), r, seg=6, tampa=2, contorno=0.0)
    for k in range(10):
        O3.caixa(f"{nome}_caco{k}", (0.1, 0.06, 0.02), O3.brilha("#dfe7ea", 0.6), r, (-2.0 + 0.45 * k, -0.9 - 0.3 * (k % 3), 0.02), chanfro=0.0, contorno=0.0, rot=(0, 0, 30 * k))
    O3.caixa(nome + "_toldo", (w + 0.4, 1.4, 0.06), _mat("#6a5a46", "#4a3e30"), r, (0, -0.55, 3.0), chanfro=0.0, rot=(-14, 0, 0))
    poca_agua(nome + "_pq", x, y - 1.3, 1.6, 0.7, brilho=(QUENTE, 0.45), seed=4)
    poca_de_luz(nome + "_pl", x, y - 0.8, 2.4, 1.4, 0.36)
    return r
