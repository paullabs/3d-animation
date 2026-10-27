"""Objetos 3D de "O abrigo", parte 2 (decupagem v3, 25/10/2026): o que faltava em 3D para os planos fechados de até 1,3 s.
Quadro de giz com riscos de cinco em cinco, privada transbordando, porta do banheiro entreaberta, caderno com lápis, baralho, jaqueta jeans
na cadeira, garfo, moscas, vapor, giz. Mesmo acabamento de objetos3d_abrigo (tom chapado, faixa de sombra, borda âmbar, contorno de tinta).
Convenção igual à da parte 1: z para cima, a frente dos objetos olha para -y."""
import math, random
import bpy, bmesh
from mathutils import Vector
from lib import empty
import heroi3d as H3
from heroi3d import esfera, tubo, _objeto, plano
import objetos3d_abrigo as O3
from objetos3d_abrigo import M, caixa, cilindro, anel, torno, vidro, brilha

GIZ = "#e6e1d0"


def blob(cx, cy, rx, ry, z=0.006, n=22, seed=1, ruido=0.16):
    """contorno irregular e arredondado (poça): lista de (x, y, z) em volta de (cx, cy)"""
    rnd = random.Random(seed)
    k = [1.0 + ruido * rnd.uniform(-1, 1) for _ in range(n)]
    k = [(k[i - 1] + 2 * k[i] + k[(i + 1) % n]) / 4 for i in range(n)]           # suaviza o ruído
    return [(cx + rx * k[i] * math.cos(2 * math.pi * i / n), cy + ry * k[i] * math.sin(2 * math.pi * i / n), z) for i in range(n)]


def giz3d(nome, loc=(0, 0, 0), s=1.0, pai=None, rot=(0, 0, 0)):
    """um toco de giz (6 cm), com a ponta gasta"""
    r = empty(nome, pai, loc); r.scale = (s,) * 3; r.rotation_euler = tuple(math.radians(a) for a in rot)
    cilindro(nome + "_c", 0.0055, 0.06, M("#efeadb", "#c8c2ae", "#ffffff"), r, (0, 0, 0), seg=14, eixo="Y", contorno=0.0015)
    return r


def quadro_giz3d(nome, loc=(0, 0, 0), s=1.0, dias=1, pai=None, colunas=8, riscos_por_dia=1):
    """quadro de giz de parede (1,3 x 0,9 m): moldura de madeira, lousa verde-escura com poeira de giz, bandeja com um toco de giz e os riscos
    dos dias em grupos de cinco (quatro em pé e um cortando), da esquerda para a direita e de cima para baixo.
    Origem no centro; a lousa olha para -y."""
    r = empty(nome, pai, loc); r.scale = (s,) * 3
    mad, mad_e = M("#7a5232", "#573820"), M("#573820")
    lou = M("#2d3a33", "#26312b", "#6a7a6e")
    W, H, E = 1.30, 0.92, 0.05
    caixa(nome + "_lousa", (W - 0.08, 0.02, H - 0.08), lou, r, (0, 0.0, 0), chanfro=0.004, contorno=0.003)
    for k, (x, z, sx, sz) in enumerate(((0, H / 2 - 0.025, W, 0.05), (0, -H / 2 + 0.025, W, 0.05), (-W / 2 + 0.025, 0, 0.05, H), (W / 2 - 0.025, 0, 0.05, H))):
        caixa(f"{nome}_mold{k}", (sx, 0.05, sz), mad, r, (x, -0.01, z), chanfro=0.008)
    caixa(nome + "_bandeja", (W - 0.1, 0.07, 0.025), mad_e, r, (0, -0.04, -H / 2 - 0.005), chanfro=0.006)
    giz3d(nome + "_tocogiz", (0.28, -0.05, -H / 2 + 0.022), 1.0, r, rot=(0, 0, 80))
    # poeira de giz apagada (manchas claras e largas, quase transparentes)
    rnd = random.Random(11)
    for k in range(5):
        caixa(f"{nome}_mancha{k}", (rnd.uniform(0.25, 0.5), 0.002, rnd.uniform(0.04, 0.09)), M("#3c4a42", "#3c4a42", "#3c4a42"), r,
              (rnd.uniform(-0.45, 0.45), -0.012, rnd.uniform(-0.3, 0.3)), chanfro=0.0, contorno=0.0, rot=(0, rnd.uniform(-20, 20), 0))
    mg = M(GIZ, "#c8c2ae", "#ffffff")
    gx0, gz0 = -W / 2 + 0.11, H / 2 - 0.11
    for d in range(dias):
        g, k = divmod(d, 5)
        col, lin = g % colunas, g // colunas
        x0 = gx0 + col * 0.145; z0 = gz0 - lin * 0.125
        if k < 4:
            tilt = rnd.uniform(-3, 3)
            caixa(f"{nome}_risco{d}", (0.0085, 0.006, 0.085), mg, r, (x0 + k * 0.026, -0.017, z0), chanfro=0.002, contorno=0.0, rot=(0, tilt, 0))
        else:
            caixa(f"{nome}_corte{g}", (0.0085, 0.006, 0.125), mg, r, (x0 + 0.039, -0.018, z0), chanfro=0.002, contorno=0.0, rot=(0, 64, 0))
    return r


def privada3d(nome, loc=(0, 0, 0), s=1.0, transborda=1.0, pai=None):
    """privada de louça suja (a frente para -y): base, bacia, assento, caixa acoplada com a tampa e o botão; transborda = 0..1, a água marrom-esverdeada
    sobe pela bacia, escorre pelas laterais e abre uma poça no chão"""
    r = empty(nome, pai, loc); r.scale = (s,) * 3
    lou = M("#d6d1bf", "#aaa592", "#ffffff"); sujo = M("#3e4a2a", "#2e381e", "#8a9a5a")
    torno(nome + "_base", [(0.07, 0.0), (0.12, 0.06), (0.17, 0.2), (0.2, 0.32), (0.21, 0.38)], lou, r, (0, -0.02, 0), seg=40)
    bacia = esfera(nome + "_bacia", 0.205, 0.265, 0.07, lou, r, (0, -0.04, 0.42), contorno=0.004, seg=40, an=16)
    anel(nome + "_aro", 0.19, 0.02, lou, r, (0, -0.04, 0.46), eixo="Z", seg=40)
    caixa(nome + "_tampa", (0.4, 0.05, 0.015), M("#c8c3b0"), r, (0, 0.17, 0.5), chanfro=0.006)
    caixa(nome + "_caixa", (0.42, 0.2, 0.36), lou, r, (0, 0.22, 0.68), chanfro=0.025)
    caixa(nome + "_caixa_tp", (0.44, 0.22, 0.03), lou, r, (0, 0.22, 0.875), chanfro=0.012)
    cilindro(nome + "_botao", 0.022, 0.02, M("#b4b8c0"), r, (0, 0.2, 0.905), seg=16)
    tubo(nome + "_cano", [(0.14, 0.3, 0.52), (0.14, 0.36, 0.52), (0.14, 0.36, 0.0)], [0.016] * 3, M("#7a7e74"), r, seg=12, tampa=3)
    # a água: disco dentro da bacia e o transbordo
    esfera(nome + "_agua", 0.17, 0.225, 0.012, sujo, r, (0, -0.04, 0.4 + 0.07 * transborda), contorno=0.0, seg=32, an=8)
    if transborda > 0.2:
        for k, x in enumerate((-0.12, 0.0, 0.13)):
            caixa(f"{nome}_escorre{k}", (0.03, 0.012, 0.3 * transborda), sujo, r, (x, -0.31, 0.36), chanfro=0.004, contorno=0.0)
        import cena
        cena.poly_mesh(nome + "_poca", blob(r.location.x + 0.0, r.location.y - 0.45 * s, 0.62 * s * transborda + 0.2, 0.5 * s * transborda + 0.15, z=0.006, seed=3), plano("#33381e"))
        cena.poly_mesh(nome + "_poca_br", blob(r.location.x + 0.1 * s, r.location.y - 0.55 * s, 0.3 * s * transborda + 0.1, 0.2 * s * transborda + 0.06, z=0.008, seed=5), plano("#4a5028"))
    return r


def porta_comum3d(nome, loc=(0, 0, 0), s=1.0, abre=0.0, pai=None, cor="#5a625a"):
    """porta simples de ferro pintada (0,8 x 2,05 m) com batente, maçaneta e dobradiças, aberta 'abre' graus em volta da dobradiça da esquerda;
    atrás dela, o vão escuro. Origem no meio do vão, no chão; a porta olha para -y."""
    r = empty(nome, pai, loc); r.scale = (s,) * 3
    bat, fol = M("#3a4046", "#2a3036"), M(cor, "#434a43", "#c8c8b0")
    for k, (x, z, sx, sz) in enumerate(((-0.46, 1.03, 0.08, 2.1), (0.46, 1.03, 0.08, 2.1), (0.0, 2.09, 1.0, 0.08))):
        caixa(f"{nome}_bat{k}", (sx, 0.22, sz), bat, r, (x, 0.0, z), chanfro=0.01)
    caixa(nome + "_vao", (0.84, 0.05, 2.02), M("#06090a", "#06090a", "#06090a"), r, (0.0, 0.14, 1.01), chanfro=0.0, contorno=0.0)
    d = empty(nome + "_folha", r, (-0.42, -0.06, 0.0)); d.rotation_euler.z = math.radians(abre)
    caixa(nome + "_f", (0.84, 0.045, 2.0), fol, d, (0.42, 0, 1.0), chanfro=0.008)
    for k, z in enumerate((0.35, 1.0, 1.7)):
        cilindro(f"{nome}_dobr{k}", 0.014, 0.1, M("#8a9298"), d, (0.0, 0.0, z), seg=14)
    caixa(nome + "_macaneta", (0.1, 0.05, 0.025), M("#b4b8c0"), d, (0.74, -0.04, 1.0), chanfro=0.008)
    return r


def caderno3d(nome, loc=(0, 0, 0), s=1.0, pai=None, aberto=True):
    """caderno de capa dura (21 x 15 cm) aberto, com as folhas, a linha de contas e um lápis; de fundo, a capa"""
    r = empty(nome, pai, loc); r.scale = (s,) * 3
    capa, pag = M("#5a2a24", "#3e1c18", "#c08070"), M("#e4dcc4", "#bdb59e", "#ffffff")
    caixa(nome + "_capa", (0.215, 0.155, 0.006), capa, r, (0, 0, 0), chanfro=0.002)
    for sx in (-1, 1):
        caixa(f"{nome}_pag{sx}", (0.1, 0.145, 0.012), pag, r, (sx * 0.052, 0, 0.009), chanfro=0.002, contorno=0.002, rot=(0, -sx * 2.0, 0))
    mt = M("#6a6a60")
    for k in range(7):
        caixa(f"{nome}_linha{k}", (0.085, 0.001, 0.0008), mt, r, (0.052, -0.055 + 0.018 * k, 0.0155), chanfro=0.0, contorno=0.0)
        caixa(f"{nome}_linha_e{k}", (0.085, 0.001, 0.0008), mt, r, (-0.052, -0.055 + 0.018 * k, 0.0155), chanfro=0.0, contorno=0.0)
    for k in range(3):
        caixa(f"{nome}_conta{k}", (0.012, 0.001, 0.0008), M("#2a2a26"), r, (0.03 + 0.02 * k, -0.034, 0.0158), chanfro=0.0, contorno=0.0)
    lap = empty(nome + "_lapis", r, (0.09, -0.02, 0.02)); lap.rotation_euler.z = math.radians(30)
    cilindro(nome + "_lapis_c", 0.004, 0.14, M("#c8a24a", "#9a7a2e"), lap, (0, 0, 0), seg=6, eixo="Y", contorno=0.0012)
    cilindro(nome + "_lapis_p", 0.004, 0.015, M("#d8c8a0"), lap, (0, 0.077, 0), seg=6, eixo="Y", r2=0.0008, contorno=0.0012)
    return r


def carta3d(nome, loc=(0, 0, 0), s=1.0, verso=True, pai=None, rot=(0, 0, 0)):
    """carta de baralho (6,4 x 8,9 cm) deitada (z para cima): verso azul com borda, ou frente creme com um naipe vermelho"""
    r = empty(nome, pai, loc); r.scale = (s,) * 3; r.rotation_euler = tuple(math.radians(a) for a in rot)
    if verso:
        caixa(nome + "_c", (0.064, 0.089, 0.002), M("#d8d0bb", "#aaa28c", "#ffffff"), r, (0, 0, 0.001), chanfro=0.0006, contorno=0.0012)
        caixa(nome + "_v", (0.054, 0.079, 0.0016), M("#34506e", "#26405a", "#6a86a8"), r, (0, 0, 0.0016), chanfro=0.0004, contorno=0.0)
        caixa(nome + "_v2", (0.036, 0.061, 0.0016), M("#4a6a8e", "#34506e", "#6a86a8"), r, (0, 0, 0.0021), chanfro=0.0004, contorno=0.0)
    else:
        caixa(nome + "_c", (0.064, 0.089, 0.002), M("#e8e2cc", "#bdb59e", "#ffffff"), r, (0, 0, 0.001), chanfro=0.0006, contorno=0.0012)
        caixa(nome + "_n", (0.022, 0.022, 0.0016), M("#8e302b", "#64211f", "#d08070"), r, (0, 0, 0.0021), chanfro=0.0004, contorno=0.0, rot=(0, 0, 45))
        caixa(nome + "_n1", (0.008, 0.008, 0.0016), M("#2a2a26"), r, (-0.021, 0.036, 0.0021), chanfro=0.0, contorno=0.0)
    return r


def jaqueta3d(nome, loc=(0, 0, 0), s=1.0, pai=None, cor="#4f6275"):
    """a jaqueta jeans da Lu pendurada no encosto da cadeira (de frente para -y): ombros, corpo caído, gola, bolsos e as mangas penduradas"""
    r = empty(nome, pai, loc); r.scale = (s,) * 3
    jq, jq_e = M(cor, "#3a4a5a", "#8aa0b4"), M("#3a4a5a")
    esfera(nome + "_ombros", 0.2, 0.05, 0.07, jq, r, (0, 0, 0.0), contorno=0.004, seg=32, an=16)
    esfera(nome + "_corpo", 0.19, 0.06, 0.3, jq, r, (0, -0.005, -0.27), contorno=0.004, seg=32, an=20)
    for k, sx in enumerate((-1, 1)):
        tubo(f"{nome}_manga{k}", [(sx * 0.2, 0, -0.01), (sx * 0.235, -0.01, -0.2), (sx * 0.24, -0.02, -0.42)], [0.052, 0.046, 0.04], jq, r, seg=20, tampa=5, contorno=0.004)
        caixa(f"{nome}_punho{k}", (0.085, 0.07, 0.03), jq_e, r, (sx * 0.24, -0.02, -0.435), chanfro=0.008)
        caixa(f"{nome}_bolso{k}", (0.07, 0.012, 0.07), jq_e, r, (sx * 0.085, -0.055, -0.2), chanfro=0.005, contorno=0.002)
    for k, sx in enumerate((-1, 1)):
        caixa(f"{nome}_gola{k}", (0.07, 0.04, 0.045), jq_e, r, (sx * 0.05, -0.02, 0.055), chanfro=0.01, rot=(0, sx * 18, 0))
    for k in range(5):
        cilindro(f"{nome}_botao{k}", 0.009, 0.006, M("#b88a52"), r, (0, -0.067, -0.08 - 0.07 * k), seg=12, eixo="Y", contorno=0.0015)
    return r


def garfo3d(nome, loc=(0, 0, 0), s=1.0, pai=None, rot=(0, 0, 0)):
    """garfo de aço (17 cm), cabo ao longo de +y e os dentes na ponta"""
    r = empty(nome, pai, loc); r.scale = (s,) * 3; r.rotation_euler = tuple(math.radians(a) for a in rot)
    mt = M("#c8ccd6", "#9096a2", "#ffffff")
    tubo(nome + "_cabo", [(0, -0.09, 0), (0, 0.02, 0.0)], [0.004, 0.0035], mt, r, seg=8, tampa=2, contorno=0.0012)
    caixa(nome + "_cabeca", (0.026, 0.026, 0.002), mt, r, (0, 0.04, 0), chanfro=0.0006, contorno=0.0012)
    for k, x in enumerate((-0.01, -0.0033, 0.0033, 0.01)):
        caixa(f"{nome}_dente{k}", (0.0028, 0.03, 0.002), mt, r, (x, 0.07, 0), chanfro=0.0006, contorno=0.001)
    return r


def moscas3d(nome, centro, n=3, raio=0.2, s=1.0, seed=4):
    """algumas moscas paradas no ar em volta de um ponto (corpo preto de 1 cm e asas claras)"""
    rnd = random.Random(seed); out = []
    for k in range(n):
        p = (centro[0] + rnd.uniform(-raio, raio), centro[1] + rnd.uniform(-raio, raio), centro[2] + rnd.uniform(-raio, raio) * 0.8)
        r = empty(f"{nome}{k}", None, p); r.scale = (s,) * 3; r.rotation_euler.z = rnd.uniform(0, 6.28)
        esfera(f"{nome}{k}_c", 0.005, 0.008, 0.005, M("#16181a", "#16181a", "#8a8a80"), r, (0, 0, 0), contorno=0.0008, seg=10, an=6)
        for sx in (-1, 1):
            esfera(f"{nome}{k}_a{sx}", 0.0075, 0.004, 0.0008, plano("#cfd4cf"), r, (sx * 0.006, 0.002, 0.004), contorno=0.0, seg=8, an=4).rotation_euler.y = math.radians(sx * 25)
        out.append(r)
    return out


def vapor3d(nome, base, n=3, alt=0.2, s=1.0, cor="#e8e2d0"):
    """fiapos de vapor (tubos finos e sinuosos, translúcidos) subindo de um prato"""
    out = []
    for k in range(n):
        x0 = base[0] + (k - (n - 1) / 2) * 0.05 * s
        pts = [(x0 + 0.012 * s * math.sin(2.2 * t + k), base[1] + 0.008 * s * math.cos(1.7 * t + k), base[2] + alt * s * t) for t in [i / 8 for i in range(9)]]
        out.append(tubo(f"{nome}{k}", pts, [0.0035 * s] * 9, vidro(cor, 0.35, 0.3), None, seg=8, tampa=3, contorno=0.0))
    return out


def lagrima3d(nome, loc, s=1.0):
    """uma lágrima: gota de vidro azulada"""
    return esfera(nome, 0.007 * s, 0.006 * s, 0.011 * s, vidro("#cfe4ee", 0.5, 0.6), None, loc, contorno=0.0008, seg=12, an=8)


def colher3d(nome, loc=(0, 0, 0), s=1.0, pai=None):
    """colher de aço (17 cm): cabo ao longo de +y e a concha na ponta (a parte funda olha para cima, +z)"""
    r = empty(nome, pai, loc); r.scale = (s,) * 3
    mt = M("#c8ccd6", "#9096a2", "#ffffff")
    tubo(nome + "_cabo", [(0, -0.09, 0), (0, 0.03, 0.0)], [0.0042, 0.0036], mt, r, seg=8, tampa=2, contorno=0.0012)
    esfera(nome + "_concha", 0.021, 0.03, 0.007, mt, r, (0, 0.06, 0.0), contorno=0.0012, seg=20, an=10)
    return r


def orienta(obj, direcao):
    """gira um objeto cujo eixo +y é a frente (garfo, colher, mão) para apontar em 'direcao' (vetor no mundo): primeiro sobe/desce (x), depois gira (z)"""
    from mathutils import Vector
    d = Vector(direcao).normalized()
    obj.rotation_euler = (math.asin(max(-1.0, min(1.0, d.z))), 0, math.atan2(-d.x, d.y))
    return obj


def campainha3d(nome, loc=(0, 0, 0), s=1.0, pai=None, poeira=0.0, limpa=False):
    """campainha de bicicleta de verdade: cúpula cromada em torno de z, base achatada, pino e o botão de tocar (a alavanca) em cima; poeira (0 a 1) mistura com
    cinza; limpa = uma faixa cromada brilhante onde o polegar passou"""
    from props import _mix
    pc = lambda c: _mix(c, "#9a968a", poeira)
    r = empty(nome, pai, loc); r.scale = (s,) * 3
    torno(nome + "_cupula", [(0.036, 0.0), (0.036, 0.004), (0.033, 0.012), (0.026, 0.02), (0.016, 0.026), (0.006, 0.029), (0.0, 0.03)], M(pc("#c8ccd6"), pc("#8a909c"), "#ffffff"), r, (0, 0, 0), seg=40)
    cilindro(nome + "_base", 0.012, 0.012, M(pc("#5a626e")), r, (0, 0, -0.004), seg=16)
    cilindro(nome + "_pino", 0.0035, 0.022, M(pc("#5a626e")), r, (0, 0, 0.037), seg=10, contorno=0.0015)
    tubo(nome + "_alavanca", [(0, 0, 0.044), (0.012, 0, 0.05), (0.03, 0, 0.044)], [0.0035, 0.0035, 0.0035], M(pc("#8a909c")), r, seg=10, tampa=3, contorno=0.0015)
    esfera(nome + "_botao", 0.007, 0.007, 0.005, M(pc("#1c1c22")), r, (0.033, 0, 0.044), contorno=0.0012, seg=12, an=8)
    if limpa:
        esfera(nome + "_faixa", 0.0045, 0.03, 0.0035, M("#f4f6fa", "#c8ccd6", "#ffffff"), r, (0.0, 0.0, 0.0285), contorno=0.0, seg=12, an=8).rotation_euler = (0, math.radians(8), 0)
    return r


# ---------------------------------------------------------------- o cogumelo da explosão (pedido de 25/10/2026: "tem que aparecer a explosão de cogumelo lá no fundo, expandindo")
def cogumelo3d(nome, loc=(0, -20.5, 0), H=22.0, seed=4):
    """nuvem de cogumelo de bolhas de papel (mesmo tom chapado com contorno): coluna torcida, anel de condensação, chapéu que rola,
    a barriga do chapéu acesa de laranja, a bola de fogo no pé e a poeira que se espalha no chão.
    Cresce pelo tempo da história: cogumelo_em(raiz, T) (T em segundos desde o começo do filme)"""
    rnd = random.Random(seed)
    r = empty(nome, None, loc)
    poe, poe_s = "#8e8676", "#6e6658"
    col, col_s = "#b7a48a", "#8a775f"
    cap, cap_s = "#c9bba4", "#9a8a72"
    fogo, fogo2 = _fogo_mat(nome + "_fogo_m", 2.4), _fogo_mat(nome + "_fogo2_m", 2.9)      # materiais próprios: a cor muda com o tempo
    # poeira no chão (fica, só se espalha)
    pe = empty(nome + "_pe", r, (0, 0, 0))
    for k in range(14):
        a = 2 * math.pi * k / 14 + rnd.uniform(-0.2, 0.2); d = H * rnd.uniform(0.12, 0.3)
        esfera(f"{nome}_poe{k}", H * rnd.uniform(0.08, 0.13), H * rnd.uniform(0.08, 0.13), H * rnd.uniform(0.04, 0.07), M(poe, poe_s), pe,
               (d * math.cos(a), d * math.sin(a), H * 0.02), contorno=0.04, seg=20, an=12)
    for k in range(5):
        a = 2 * math.pi * k / 5
        esfera(f"{nome}_fogo{k}", H * 0.07, H * 0.07, H * 0.06, fogo if k % 2 else fogo2, pe, (H * 0.06 * math.cos(a), H * 0.06 * math.sin(a), H * 0.05), contorno=0.0, seg=16, an=10)
    # coluna: bolhas empilhadas, mais finas no meio, com um leve S
    co = empty(nome + "_coluna", r, (0, 0, 0))
    n = 11
    for k in range(n):
        u = k / (n - 1); z = H * (0.06 + 0.6 * u); rr = H * (0.085 - 0.03 * math.sin(math.pi * u) + 0.02 * u)
        x = H * 0.025 * math.sin(2.6 * u + 0.4)
        for j in range(3):
            a = 2 * math.pi * j / 3 + k
            esfera(f"{nome}_col{k}_{j}", rr * 0.85, rr * 0.85, rr * 0.75, M(col, col_s), co, (x + rr * 0.45 * math.cos(a), rr * 0.45 * math.sin(a), z), contorno=0.04, seg=18, an=10)
    # anel de condensação em volta da coluna
    an = empty(nome + "_anel", r, (0, 0, H * 0.46))
    for k in range(12):
        a = 2 * math.pi * k / 12
        esfera(f"{nome}_ane{k}", H * 0.07, H * 0.07, H * 0.025, M("#dcd5c6", "#b0a894"), an, (H * 0.2 * math.cos(a), H * 0.2 * math.sin(a), 0), contorno=0.03, seg=16, an=8)
    # chapéu: um anel de bolhas que rola + o domo; a barriga acesa por baixo
    ch = empty(nome + "_chapeu", r, (0, 0, H * 0.72))
    for k in range(14):
        a = 2 * math.pi * k / 14; rb = H * rnd.uniform(0.11, 0.14)
        esfera(f"{nome}_cap{k}", rb, rb, rb * 0.85, M(cap, cap_s), ch, (H * 0.2 * math.cos(a), H * 0.2 * math.sin(a), rnd.uniform(-0.02, 0.02) * H), contorno=0.05, seg=20, an=12)
    for k in range(7):
        a = 2 * math.pi * k / 7; d = H * (0.0 if k == 0 else 0.11)
        esfera(f"{nome}_domo{k}", H * 0.14, H * 0.14, H * 0.11, M(cap, cap_s), ch, (d * math.cos(a), d * math.sin(a), H * 0.1), contorno=0.05, seg=20, an=12)
    esfera(nome + "_barriga", H * 0.24, H * 0.24, H * 0.06, fogo, ch, (0, 0, -H * 0.07), contorno=0.0, seg=28, an=12)
    r["H"] = H
    cogumelo_em(r, 0.0)
    return r


def _fogo_mat(nome, forca):
    from lib import srgb
    m = bpy.data.materials.new(nome); m.use_nodes = True
    nt = m.node_tree; nt.nodes.clear()
    em = nt.nodes.new("ShaderNodeEmission"); em.inputs[1].default_value = forca
    out = nt.nodes.new("ShaderNodeOutputMaterial"); nt.links.new(em.outputs[0], out.inputs[0])
    return m


# a cor da explosão pelo tempo (pedido de 25/10/2026): nasce branco-amarela, vira laranja, fica vermelha e por fim o céu estoura em branco
COR_FOGO = [(0.0, "#fff6d2"), (1.4, "#ffd27a"), (3.0, "#ff9440"), (4.8, "#e8522e"), (6.5, "#d23a26"), (9.0, "#b8301e")]


def cor_no_tempo(T, tab=COR_FOGO, clarear=0.0):
    from lib import srgb
    for (ta, ca), (tb, cb) in zip(tab, tab[1:]):
        if T <= tb:
            u = max(0.0, (T - ta) / (tb - ta)); u = u * u * (3 - 2 * u)
            a, b = srgb(ca), srgb(cb)
            c = [x + (y - x) * u for x, y in zip(a, b)]
            break
    else:
        c = list(srgb(tab[-1][1]))
    return [x + (1 - x) * clarear for x in c]


def cogumelo_em(r, T, f=None):
    """o tamanho do cogumelo no segundo T do filme: nasce pequeno no 1A, sobe e engorda até o clarão (6,5 s) e continua devagar depois.
    f = quadro para gravar a chave"""
    from lib import key
    H = r["H"]
    u = min(max(T / 6.5, 0.0), 1.0); g = 0.38 + 0.62 * (1 - (1 - u) ** 2) + 0.03 * max(0.0, T - 6.5)
    nm = r.name
    r.scale = (g, g, g)
    ch = bpy.data.objects[nm + "_chapeu"]; co = bpy.data.objects[nm + "_coluna"]; an = bpy.data.objects[nm + "_anel"]
    ch.location.z = H * (0.6 + 0.12 * u); ch.rotation_euler.z = 0.12 * T                 # o chapéu sobe e rola devagar
    ch.scale = (0.8 + 0.25 * u, 0.8 + 0.25 * u, 0.85 + 0.15 * u)
    co.scale = (1.0, 1.0, 0.85 + 0.15 * u); an.scale = (0.7 + 0.5 * u,) * 2 + (1.0,); an.location.z = H * (0.38 + 0.08 * u)
    for k, extra in (("_fogo_m", 0.0), ("_fogo2_m", 0.35)):
        m = bpy.data.materials.get(nm + k)
        if m:
            em = next(n for n in m.node_tree.nodes if n.type == "EMISSION")
            em.inputs[0].default_value = (*cor_no_tempo(T, clarear=extra), 1)
            if f is not None:
                em.inputs[0].keyframe_insert("default_value", frame=f)
    for gl in [bpy.data.materials.get(n) for n in ("cogumelo_gl_m", "cogumelo_chao_m")]:   # o brilho no céu e o reflexo na rua seguem a cor do fogo
        if gl is None:
            continue
        em = next(n for n in gl.node_tree.nodes if n.type == "EMISSION")
        em.inputs[0].default_value = (*cor_no_tempo(T, clarear=0.25), 1)
        if f is not None:
            em.inputs[0].keyframe_insert("default_value", frame=f)
    if f is not None:
        for o in (r, ch, co, an):
            key(o, "scale", f, "LINEAR")
        key(ch, "location", f, "LINEAR"); key(ch, "rotation_euler", f, "LINEAR"); key(an, "location", f, "LINEAR")


# ---------------------------------------------------------------- esqueleto (pedido de 25/10/2026: a Lu vira esqueleto na cama; os vizinhos ficam como esqueletos na porta)
OSSO, OSSO_S = "#e2dac2", "#a89e86"


def esqueleto3d(nome, loc=(0, 0, 0), rot=(0, 0, 0), s=1.0, ombro=(0, 0), cotovelo=(0, 0), abre=(8, 8), quadril=(0, 0), joelho=(0, 0),
                cabeca=0.0, queixo=12.0, poeira=0.0, seed=3):
    """esqueleto de desenho (crânio com órbitas fundas, mandíbula solta, coluna em vértebras, costelas em arco, bacia, braços e pernas em juntas),
    em pé no espaço local (pés em z = 0, o rosto para -y), posto e girado pela raiz. ombro/quadril: negativo = para a frente (como o Heroi3D).
    poeira (0 a 1) suja o osso de cinza."""
    from props import _mix
    rnd = random.Random(seed)
    os_ = M(_mix(OSSO, "#8a867a", poeira), _mix(OSSO_S, "#5e5a52", poeira))
    escuro = M("#1c1a18", "#1c1a18", "#3a3630")
    r = empty(nome, None, loc); r.scale = (s,) * 3; r.rotation_euler = tuple(math.radians(a) for a in rot)
    # bacia e coluna
    esfera(nome + "_bacia", 0.15, 0.08, 0.09, os_, r, (0, 0, 0.95), contorno=0.005, seg=24, an=14)
    for k in range(10):
        z = 1.02 + 0.048 * k
        esfera(f"{nome}_vert{k}", 0.026, 0.024, 0.02, os_, r, (0, 0.04 * math.sin(k * 0.3), z), contorno=0.003, seg=12, an=8)
    # costelas: arcos que saem da coluna e quase se fecham na frente (esterno)
    for k in range(6):
        z = 1.16 + 0.045 * k; rx = 0.13 + 0.02 * math.sin(math.pi * k / 5); ry = 0.095
        for sx in (-1, 1):
            pts = [(sx * rx * math.sin(a), ry * math.cos(a) - 0.005, z - 0.03 * math.sin(a)) for a in [math.radians(t) for t in range(0, 170, 17)]]
            tubo(f"{nome}_cost{k}{sx}", pts, [0.011] * len(pts), os_, r, seg=8, tampa=2, contorno=0.002)
    caixa(nome + "_esterno", (0.035, 0.02, 0.2), os_, r, (0, -0.1, 1.27), chanfro=0.008, contorno=0.002)
    for sx in (-1, 1):
        tubo(f"{nome}_clav{sx}", [(0, -0.07, 1.42), (sx * 0.17, -0.02, 1.44)], [0.012, 0.012], os_, r, seg=8, tampa=3, contorno=0.002)
    # crânio
    cab = empty(nome + "_cab", r, (0, 0, 1.52)); cab.rotation_euler.x = math.radians(cabeca)
    esfera(nome + "_pesc", 0.03, 0.03, 0.05, os_, cab, (0, 0.0, 0.02), contorno=0.003, seg=12, an=8)
    esfera(nome + "_cranio", 0.1, 0.115, 0.11, os_, cab, (0, 0.0, 0.14), contorno=0.005, seg=28, an=18)
    for sx in (-1, 1):
        esfera(f"{nome}_orbita{sx}", 0.03, 0.02, 0.032, escuro, cab, (sx * 0.042, -0.098, 0.15), contorno=0.0, seg=16, an=10)
    esfera(nome + "_nariz", 0.012, 0.01, 0.016, escuro, cab, (0, -0.108, 0.105), contorno=0.0, seg=10, an=6)
    for k in range(6):
        caixa(f"{nome}_dente{k}", (0.012, 0.008, 0.016), M("#f0ead8", "#c8c0aa"), cab, (-0.03 + 0.012 * k, -0.098, 0.075), chanfro=0.003, contorno=0.001)
    mand = empty(nome + "_mand", cab, (0, -0.02, 0.09)); mand.rotation_euler.x = math.radians(queixo)
    esfera(nome + "_mandibula", 0.065, 0.07, 0.03, os_, mand, (0, -0.045, -0.025), contorno=0.004, seg=20, an=12)
    # braços e pernas em juntas
    for i, sx in enumerate((-1, 1)):
        om = empty(f"{nome}_ombro{sx}", r, (sx * 0.18, -0.01, 1.43)); om.rotation_euler = (math.radians(ombro[i]), math.radians(sx * abre[i]), 0)
        esfera(f"{nome}_cab_umero{sx}", 0.03, 0.03, 0.03, os_, om, (0, 0, 0), contorno=0.003, seg=12, an=8)
        tubo(f"{nome}_umero{sx}", [(0, 0, 0), (0, 0, -0.3)], [0.017, 0.015], os_, om, seg=10, tampa=4, contorno=0.002)
        co = empty(f"{nome}_cotov{sx}", om, (0, 0, -0.3)); co.rotation_euler.x = math.radians(cotovelo[i])
        esfera(f"{nome}_cot_n{sx}", 0.022, 0.022, 0.022, os_, co, (0, 0, 0), contorno=0.003, seg=12, an=8)
        for dx in (-0.012, 0.012):
            tubo(f"{nome}_rad{sx}{dx}", [(dx, 0, 0), (dx * 0.8, 0, -0.26)], [0.009, 0.008], os_, co, seg=8, tampa=3, contorno=0.0015)
        mao = empty(f"{nome}_mao{sx}", co, (0, 0, -0.27))
        esfera(f"{nome}_carpo{sx}", 0.025, 0.012, 0.02, os_, mao, (0, 0, 0), contorno=0.002, seg=10, an=6)
        for d in range(4):
            tubo(f"{nome}_dedo{sx}{d}", [(-0.018 + 0.012 * d, 0, -0.01), (-0.02 + 0.013 * d, -0.01, -0.075 + 0.006 * abs(d - 1.5))], [0.005, 0.004], os_, mao, seg=6, tampa=2, contorno=0.001)
        qd = empty(f"{nome}_quad{sx}", r, (sx * 0.09, 0, 0.92)); qd.rotation_euler.x = math.radians(quadril[i])
        esfera(f"{nome}_cab_femur{sx}", 0.032, 0.032, 0.032, os_, qd, (0, 0, 0), contorno=0.003, seg=12, an=8)
        tubo(f"{nome}_femur{sx}", [(0, 0, 0), (0, 0, -0.43)], [0.022, 0.019], os_, qd, seg=10, tampa=4, contorno=0.002)
        jo = empty(f"{nome}_joelho{sx}", qd, (0, 0, -0.43)); jo.rotation_euler.x = math.radians(joelho[i])
        esfera(f"{nome}_patela{sx}", 0.026, 0.026, 0.028, os_, jo, (0, -0.01, 0), contorno=0.003, seg=12, an=8)
        tubo(f"{nome}_tibia{sx}", [(0, 0, 0), (0, 0, -0.42)], [0.018, 0.015], os_, jo, seg=10, tampa=4, contorno=0.002)
        esfera(f"{nome}_pe{sx}", 0.035, 0.08, 0.02, os_, jo, (0, -0.05, -0.44), contorno=0.003, seg=12, an=8)
    return r


def esqueleto_deitado(nome, cabeca_em, rumo=0.0, de_lado=0.0, z=0.0, **k):
    """esqueleto caído no chão (ou na cama): a cabeça em 'cabeca_em' (x, y), o corpo na direção 'rumo' (graus, 0 = pés para -y),
    de barriga para cima (de_lado = 0) ou virado (90 = de bruços). Devolve a raiz."""
    ang = math.radians(rumo)
    pe = (cabeca_em[0] + 1.62 * math.sin(ang) * 0, cabeca_em[1], z)
    r = esqueleto3d(nome, (0, 0, 0), (0, 0, 0), **k)
    r.rotation_mode = "XYZ"
    # deitado: o eixo do corpo (z local) vai para o chão na direção oposta ao rumo; gira em x -90 e depois em z pelo rumo
    from mathutils import Euler as _E, Matrix as _Mx
    R = _Mx.Rotation(ang, 4, "Z") @ _Mx.Rotation(math.radians(de_lado), 4, "Y") @ _Mx.Rotation(math.radians(-90), 4, "X")
    cab_local = Vector((0, 0, 1.66))
    p = Vector((cabeca_em[0], cabeca_em[1], z)) - (R.to_3x3() @ cab_local) + Vector((0, 0, 0.0))
    r.matrix_world = _Mx.Translation(p) @ R
    return r


def sueter_pendurado3d(nome, s=1.0):
    """o suéter da Pipoca aberto, pendurado pela gola (a mão pega pela gola e ele cai): corpinho de tricô, duas manguinhas, a listra creme.
    A origem é a gola (o ponto que a mão segura); o corpo cai para -z"""
    r = empty(nome, None, (0, 0, 0)); r.scale = (s,) * 3
    ver, ver_s = M("#8e302b", "#64211f", "#d08070"), M("#64211f")
    torno(nome + "_corpo", [(0.026, 0.0), (0.05, -0.02), (0.056, -0.06), (0.054, -0.11), (0.05, -0.135), (0.044, -0.14)], ver, r, (0, 0, 0), seg=28)
    r_ = bpy.data.objects[nome + "_corpo"]; r_.scale.y = 0.55                      # achatado: é pano, não lata
    torno(nome + "_lista", [(0.0572, -0.07), (0.0572, -0.082)], M("#a89f86"), r, (0, 0, 0), seg=28)
    bpy.data.objects[nome + "_lista"].scale.y = 0.56
    anel(nome + "_gola", 0.026, 0.007, ver_s, r, (0, 0, 0), eixo="Z", seg=20)
    for sx in (-1, 1):
        tubo(f"{nome}_manga{sx}", [(sx * 0.045, 0, -0.03), (sx * 0.07, 0, -0.06), (sx * 0.078, 0, -0.085)], [0.016, 0.014, 0.013], ver, r, seg=12, tampa=4)
    for k in range(7):
        tubo(f"{nome}_nerv{k}", [(-0.04 + 0.013 * k, -0.031, -0.11), (-0.04 + 0.013 * k, -0.031, -0.138)], [0.0025, 0.0025], ver_s, r, seg=6, tampa=2, contorno=0.0)
    return r
