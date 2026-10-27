"""O galpão do grupo, rico (26/10/2026, storyboard v5 das sequências 6 a 17 de "O abrigo, parte 2"; guia: personagem/abrigo/guia-luz-e-suspense.md).
O galpao3d original é só caixa, portão e parede. Aqui entra a vida de quem mora ali: colchões e cobertores, estante de latas, varal, fio de lâmpadas de festa
(as bolas de luz do fundo), lampião pendurado sobre a fogueira, barris, sacos de areia, cartazes de desaparecidos, canos no teto, parede da frente.
A luz conta a história: âmbar quente = a fogueira, o lampião e as velas (gente); azul frio = as frestas do portão e as janelas altas (a rua, o perigo).
Coordenadas do mundo: o centro do chão é (0,0,0); o portão fica em +y (y=4), a parede da frente em y=-4,15; x de -5 a 5; teto a 4,2 m."""
import math, random
import bpy
from mathutils import Vector
import lib
from lib import empty
import cena
import heroi3d as H3
import objetos3d_abrigo as O3
import ambiente_noite as AN

M = O3.M
AMBAR, AZUL = "#ff9a3c", "#7f9cc8"


def colchao(nome, x, y, rot=0.0, cor="#7a5a4a", seed=1):
    rnd = random.Random(seed)
    r = empty(nome, None, (x, y, 0)); r.rotation_euler.z = math.radians(rot)
    O3.caixa(nome + "_c", (0.85, 1.9, 0.12), M("#8f8a7c", "#6a665a"), r, (0, 0, 0.06), chanfro=0.035)
    O3.caixa(nome + "_cob", (0.9, 1.25, 0.05), M(cor), r, (rnd.uniform(-0.02, 0.02), -0.28, 0.145), chanfro=0.02, rot=(0, 0, rnd.uniform(-4, 4)))
    O3.caixa(nome + "_dobra", (0.9, 0.18, 0.07), M(cor), r, (0, 0.38, 0.16), chanfro=0.03)
    O3.caixa(nome + "_tr", (0.5, 0.3, 0.1), M("#c9c2a8", "#a39c82"), r, (0, 0.78, 0.17), chanfro=0.045, rot=(0, 0, rnd.uniform(-8, 8)))
    return r


def mochila(nome, x, y, rot=0.0, cor="#4a5a46"):
    r = empty(nome, None, (x, y, 0)); r.rotation_euler.z = math.radians(rot)
    O3.caixa(nome + "_c", (0.34, 0.2, 0.45), M(cor), r, (0, 0, 0.225), chanfro=0.05)
    O3.caixa(nome + "_b", (0.26, 0.08, 0.22), M("#2e342c"), r, (0, -0.13, 0.15), chanfro=0.03)
    return r


def estante(nome, x, y, rot=0.0, w=1.6, d=0.4, h=2.0, seed=1):
    """estante de ferro com latas, garrafas e caixas: o que sobrou do mercado do bairro"""
    rnd = random.Random(seed)
    r = empty(nome, None, (x, y, 0)); r.rotation_euler.z = math.radians(rot)
    m = M("#5a5f66", "#3c4046")
    for sx in (-w / 2, w / 2):
        for sy in (-d / 2, d / 2):
            O3.caixa(f"{nome}_p{sx}{sy}", (0.04, 0.04, h), m, r, (sx, sy, h / 2), chanfro=0.004, contorno=0.002)
    cores = ["#8e5a3a", "#a8884a", "#5a7a5a", "#8a3a32", "#7a8a96"]
    for k in range(4):
        z = 0.22 + k * 0.55
        O3.caixa(f"{nome}_t{k}", (w, d, 0.03), m, r, (0, 0, z), chanfro=0.004, contorno=0.002)
        n = int(w / 0.17)
        for j in range(n):
            xl = -w / 2 + 0.12 + j * (w - 0.24) / max(1, n - 1)
            if rnd.random() < 0.2:
                continue
            if rnd.random() < 0.3:
                O3.caixa(f"{nome}_cx{k}{j}", (0.14, 0.18, 0.2), M("#8a7656", "#665640"), r, (xl, 0, z + 0.115), chanfro=0.01, contorno=0.002)
            else:
                lata_s(f"{nome}_l{k}{j}", (xl, rnd.uniform(-0.05, 0.05), z + 0.015), rnd.choice(cores), r)
    return r


def lata_s(nome, loc, cor, pai=None, rot=0.0):
    """lata barata (2 peças) para estantes e chão; a lata3d completa é para o macro"""
    O3.cilindro(nome + "_c", 0.037, 0.1, M("#b4b8c0", "#80868e"), pai, (loc[0], loc[1], loc[2] + 0.05), seg=14, contorno=0.0015)
    O3.cilindro(nome + "_r", 0.0375, 0.062, M(cor), pai, (loc[0], loc[1], loc[2] + 0.05), seg=14, contorno=0.0)


def garrafao(nome, x, y, cor="#6a94b4"):
    O3.cilindro(nome + "_c", 0.15, 0.42, O3.vidro(cor, 0.35, 0.5), None, (x, y, 0.23), seg=18, contorno=0.003)
    O3.cilindro(nome + "_tp", 0.05, 0.08, M("#2e5a8a"), None, (x, y, 0.47), seg=14)
    return None


def luzes_x(nome, y, x0, x1, z=3.7, n=12, seed=3, queda=0.35):
    """fio de lâmpadas de festa atravessando o galpão ao longo de x: as bolas de luz que viram bokeh no fundo desfocado"""
    rnd = random.Random(seed)
    pts = [(x0 + (x1 - x0) * t / 10, y, z - queda * math.sin(math.pi * t / 10)) for t in range(11)]
    H3.tubo(nome + "_fio", pts, [0.006] * 11, M("#1c1c20"), None, seg=6, tampa=2, contorno=0.0)
    for k in range(n):
        t = (k + 0.5) / n
        xx = x0 + (x1 - x0) * t; zz = z - queda * math.sin(math.pi * t) - 0.07
        cor = rnd.choice(("#ffcf7a", "#ffe3a8", "#ffb25a", "#f2f0e0", "#ff9a6a"))
        H3.esfera(f"{nome}_b{k}", 0.05, 0.05, 0.06, O3.brilha(cor, 2.4), None, (xx, y, zz), contorno=0.0, seg=14, an=10)
        O3.halo_cam(f"{nome}_h{k}", (xx, y, zz), 0.26, cor, 0.5)


def varal_x(nome, y, x0, x1, z=3.15, seed=3):
    rnd = random.Random(seed)
    pts = [(x0 + (x1 - x0) * t / 10, y, z - 0.22 * math.sin(math.pi * t / 10)) for t in range(11)]
    H3.tubo(nome + "_corda", pts, [0.008] * 11, M("#6a665a"), None, seg=6, tampa=2, contorno=0.0)
    cores = ["#8a4a3a", "#4a6a8a", "#c9c2a8", "#6a8a5a", "#a0805a", "#7a5a8a", "#9a9486"]
    for k in range(7):
        t = (k + 0.7) / 7.8
        xx = x0 + (x1 - x0) * t; zz = z - 0.22 * math.sin(math.pi * t) - 0.3
        w, h = rnd.choice(((0.5, 0.6), (0.4, 0.8), (0.8, 0.6)))
        O3.caixa(f"{nome}_r{k}", (w, 0.03, h), M(cores[k % len(cores)]), None, (xx, y, zz), chanfro=0.0, contorno=0.002, rot=(0, rnd.uniform(-6, 6), rnd.uniform(-4, 4)))


def lampiao(nome, x, y, z=3.25, comp=0.9):
    """lampião a querosene pendurado numa viga: vidro, chama, halo âmbar (a luz de gente)"""
    H3.tubo(nome + "_cabo", [(x, y, 4.05), (x, y, z + 0.16)], [0.004, 0.004], M("#1c1c20"), None, seg=6, tampa=2, contorno=0.0)
    O3.cilindro(nome + "_base", 0.05, 0.03, M("#3a3632"), None, (x, y, z - 0.09), seg=16)
    O3.cilindro(nome + "_vidro", 0.055, 0.15, O3.vidro("#ffe0a0", 0.3, 0.6), None, (x, y, z), seg=16, contorno=0.002)
    O3.cilindro(nome + "_chama", 0.025, 0.07, O3.brilha("#ffcf7a", 3.0), None, (x, y, z - 0.02), r2=0.004, seg=10, contorno=0.0)
    O3.cilindro(nome + "_topo", 0.05, 0.025, M("#3a3632"), None, (x, y, z + 0.09), seg=16)
    O3.halo_cam(nome + "_halo", (x, y, z), comp, AMBAR, 0.42)


def vela(nome, x, y, z, s=1.0):
    O3.cilindro(nome + "_c", 0.016 * s, 0.07 * s, M("#d8d0b4", "#a8a088"), None, (x, y, z + 0.035 * s), seg=12, contorno=0.0015)
    O3.cilindro(nome + "_ch", 0.008 * s, 0.03 * s, O3.brilha("#ffcf7a", 3.4), None, (x, y, z + 0.085 * s), r2=0.002, seg=8, contorno=0.0)
    O3.halo_cam(nome + "_h", (x, y, z + 0.09 * s), 0.3 * s, "#ffb860", 0.4)


def cartazes(nome, x, y0, y1, z0=1.5, n=6, seed=4):
    """cartazes de desaparecidos na parede esquerda: papéis amarelados com um retrato escuro e linhas de texto"""
    rnd = random.Random(seed)
    for k in range(n):
        y = y0 + (y1 - y0) * (k + 0.5) / n + rnd.uniform(-0.05, 0.05); z = z0 + rnd.uniform(-0.1, 0.55)
        w, h = rnd.uniform(0.22, 0.3), rnd.uniform(0.3, 0.38)
        O3.caixa(f"{nome}{k}", (0.006, w, h), M("#cbbf9a", "#a89c78"), None, (-4.86, y, z), chanfro=0.0, contorno=0.002, rot=(0, rnd.uniform(-5, 5), 0))
        O3.caixa(f"{nome}f{k}", (0.004, w * 0.5, h * 0.4), M("#3a3630"), None, (-4.855, y, z + h * 0.15), chanfro=0.0, contorno=0.0)
        for j in range(2):
            O3.caixa(f"{nome}t{k}{j}", (0.004, w * 0.7, 0.012), M("#4a463e"), None, (-4.855, y, z - h * 0.18 - j * 0.04), chanfro=0.0, contorno=0.0)


def brasas(nome, x, y, z0=1.0, n=14, seed=2):
    rnd = random.Random(seed)
    for k in range(n):
        a = rnd.uniform(0, 6.28); d = rnd.uniform(0, 0.22); z = z0 + rnd.uniform(0.1, 1.5)
        s = rnd.uniform(0.008, 0.016)
        H3.esfera(f"{nome}{k}", s, s, s, O3.brilha(rnd.choice(("#ffd27a", "#ff9a3c", "#ffb44e")), 3.5), None, (x + d * math.cos(a) * (1 + z * 0.3), y + d * math.sin(a) * (1 + z * 0.3), z), contorno=0.0, seg=8, an=6)


def fogo_extra(x, y):
    """chamas a mais no tambor: um envelope translúcido grande (o calor) e mais línguas de alturas diferentes"""
    rnd = random.Random(5)
    for k in range(5):
        a = rnd.uniform(0, 6.28); d = rnd.uniform(0.02, 0.18); h = rnd.uniform(0.25, 0.62)
        O3.cilindro(f"gfl{k}", rnd.uniform(0.035, 0.07), h, O3.brilha(rnd.choice(("#ffe08a", "#ffb44e", "#ff8a3c")), 2.8), None, (x + d * math.cos(a), y + d * math.sin(a), 0.88 + h / 2), r2=0.004, contorno=0.0, seg=14)
    O3.cilindro("gfl_env", 0.2, 0.7, O3.vidro("#ff9a3c", 0.07, 0.8), None, (x, y, 0.88 + 0.35), r2=0.03, contorno=0.0, seg=20, tampa=False)


def azul_do_portao():
    """a rua, do outro lado do aço: frestas de luz azul-fria no chão, saindo debaixo do portão e pelas junções"""
    m = cena.amat("fresta_m", AZUL, 1.0, 0.26, ("radial", 0.9))
    for k, x in enumerate((-0.9, -0.1, 0.8, 1.7)):
        cena.poly_mesh(f"fresta{k}", [(x - 0.03, 3.88, 0.012), (x + 0.03, 3.88, 0.012), (x + 0.1, 2.4, 0.012), (x - 0.1, 2.4, 0.012)], m)
    AN.poca_de_luz("azul_portao", 0.6, 3.1, 2.2, 1.0, 0.16, AZUL)


def galpao_rico(fogo=True, lamp=True):
    """tudo o que faz do galpão um lugar onde gente vive. Chamar depois de O2.galpao3d."""
    # parede da frente (atrás da câmera, na maioria dos planos; vista quando se olha do portão para trás)
    parede = lib_FM("#8e8a7e")
    O3.caixa("g_frente", (10.0, 0.25, 4.2), parede, None, (0, -4.15, 2.1), chanfro=0.0, contorno=0.0)
    for k in range(1, 10):
        O3.caixa(f"g_fjunta{k}", (10.0, 0.01, 0.012), M("#86827a"), None, (0, -4.02, 0.4 * k), chanfro=0.0, contorno=0.0)
    O3.caixa("g_porta_f", (1.1, 0.06, 2.1), M("#4a4c48", "#34363a"), None, (-3.2, -4.0, 1.05), chanfro=0.01)
    # camas
    colchao("col1", -4.2, -2.6, 8, "#7a5a4a", 1); colchao("col2", -4.2, -0.5, -4, "#4a5a6a", 2); colchao("col3", -4.2, 1.6, 6, "#8a7a52", 3)
    colchao("col4", 4.1, -2.6, -6, "#5a6a52", 4); colchao("col5", 4.1, -0.6, 4, "#6a4a5a", 5)
    mochila("moc1", -3.3, -3.3, 30); mochila("moc2", 3.3, -3.4, -20, "#6a5a42"); mochila("moc3", 3.5, -0.8, 80, "#3a4a5a")
    # estantes e caixas
    estante("est1", 3.7, 3.6, 0, w=1.7, seed=3); estante("est2", -2.6, -3.85, 0, w=1.5, seed=7)
    for k, (x, y, rot, n) in enumerate(((4.3, 2.0, 12, 2), (4.1, 3.5, -8, 1))):
        O3.caixa(f"gcx{k}", (0.55, 0.45, 0.4 * n), M("#7a6448", "#5a4632"), None, (x, y, 0.2 * n), chanfro=0.015, rot=(0, 0, rot))
    garrafao("gj1", -4.3, 3.4); garrafao("gj2", -4.5, 2.8, "#7aa4b4"); garrafao("gj3", 3.6, -3.4)
    # barris e sacos de areia junto ao portão (a barricada de quem tem medo do que bate)
    AN.barril("gb1", -4.3, 3.45); AN.barril("gb2", 4.5, 3.4, )
    for k, (x, y, z) in enumerate(((-1.7, 3.55, 0.12), (-1.25, 3.55, 0.12), (-1.5, 3.55, 0.34), (-1.95, 3.5, 0.12))):
        O3.caixa(f"gsaco{k}", (0.42, 0.26, 0.2), M("#8e8466", "#6a604a"), None, (x, y, z), chanfro=0.07, rot=(0, 0, 6 * k - 8))
    cartazes("gcz", -2.6, 3.4, 1.6, 1.45, 7)
    # no teto: canos, fios, varais e as bolas de luz
    for k, y in enumerate((3.6, -3.7)):
        H3.tubo(f"gcano{k}", [(-5, y, 3.85), (5, y, 3.85)], [0.07, 0.07], M("#4a4c52", "#34363c"), None, seg=12, tampa=2, contorno=0.003)
    AN.fios("gfio", 0.0, -3.9, 3.9, z=3.95, n=3, seed=4)
    varal_x("gvar1", -2.9, -4.6, 4.6, 3.1, 3); varal_x("gvar2", 2.5, -4.6, 4.6, 3.2, 5)
    luzes_x("gluz1", -0.2, -4.7, 4.7, 3.7, 14, 3); luzes_x("gluz2", 1.6, -4.7, 4.7, 3.55, 12, 8, 0.3); luzes_x("gluz3", -2.0, -4.7, 4.7, 3.75, 12, 12, 0.3)
    if lamp:
        lampiao("gamp", 0.0, 0.5, 3.1, 1.1)
    # luzes com motivo: a fogueira (âmbar) no chão, a rua (azul) nas frestas e nas janelas
    if fogo:
        fogo_extra(0.0, 0.5)
        AN.poca_de_luz("g_fogo", 0.0, 0.5, 2.8, 2.2, 0.32, AMBAR)
        brasas("gbr", 0.0, 0.5)
    azul_do_portao()
    for sx in (-1, 1):
        AN.feixe(f"g_jan{sx}", (sx * 4.9, 0.4, 3.5), (sx * 3.1, 0.4, 0.02), 1.2, 1.6, 0.07, AZUL, eixo="x")
        AN.poca_de_luz(f"g_pjan{sx}", sx * 3.4, 0.4, 0.9, 1.3, 0.12, AZUL)
    # velas na mesa do rádio e uma caneca
    vela("gv1", -2.0, 2.45, 0.78); vela("gv2", -3.0, 1.95, 0.78, 0.8)
    O3.cilindro("gcaneca", 0.04, 0.09, M("#8a8a82"), None, (-3.0, 2.0, 0.825), seg=14)
    # lixo do dia a dia no chão
    rnd = random.Random(9)
    for k in range(8):
        lata_s(f"gl{k}", (rnd.uniform(-3.5, 3.5), rnd.uniform(-3.3, 3.0), 0.0), rnd.choice(("#8e5a3a", "#a8884a", "#5a7a5a")))
    cena.dust({}, 90, (-4, 4), 40, seed=3, color="#e8d8b8", alpha=0.5, y_range=(-3.5, 3.5), z_range=(0.3, 3.8), size=(0.006, 0.014))


def lib_FM(cor):
    import props
    return props.FM(cor)
