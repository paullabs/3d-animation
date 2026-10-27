"""A rua do bairro de "O abrigo" em 3D de verdade (pedido de 24/10/2026: "deixar a cidade um pouco mais viva, ela está muito flat").
Prédios com volume e fachada detalhada (janelas com moldura e peitoril, varandas com grade, aparelhos de ar, toldos e placas de comércio,
portas de aço de loja, calhas, caixas d'água e antenas no telhado), calçada com meio-fio, postes com fios caídos entre eles, árvores,
carros estacionados, lixeiras e placas. Tudo no acabamento do herói 3D (tom chapado, faixa de sombra, borda de luz, contorno).
Cada prédio junta as peças por material numa malha só (rápido de renderizar). A rua corre ao longo de +y; x = 0 é o meio dela.
ruinas=True dá a mesma rua depois: prédios quebrados em dentes, sem vidro, entulho, tudo cinza de pó."""
import math, random
import bpy, bmesh
from mathutils import Vector, Matrix
from lib import empty
import heroi3d as H3
from heroi3d import _objeto, tubo, esfera, plano
import objetos3d_abrigo as O3
from objetos3d_abrigo import M, caixa, cilindro, anel, brilha, vidro
from props import _mix


class Lote:
    """acumula caixas por material e vira uma malha por material"""
    def __init__(self, nome):
        self.nome = nome; self.bms = {}

    def caixa(self, mat, centro, tam):
        bm = self.bms.setdefault(mat, bmesh.new())
        bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix.Translation(Vector(centro)) @ Matrix.Diagonal((*tam, 1.0)))

    def fecha(self, mats, contorno=0.006, pai=None):
        out = []
        for k, bm in self.bms.items():
            o = _objeto(f"{self.nome}_{k}", bm, mats[k], pai, (0, 0, 0), contorno if k not in ("vidro", "luz") else 0.0)
            for p in o.data.polygons:
                p.use_smooth = False
            out.append(o)
        return out


LOJAS = ["PADARIA", "MERCADO", "FARMÁCIA", "BAR", "AÇOUGUE", "OFICINA", "LOJA", "SALÃO"]


def predio(nome, xf, y0, comp, alt, cor, lado, seed=1, loja=None, ruina=False, poeira=0.0):
    """prédio com a fachada no plano x = xf, de y0 a y0 + comp, virado para a rua (lado = +1: prédio à direita da rua, a fachada olha para -x)"""
    import lib
    rnd = random.Random(seed)
    pc = lambda c: _mix(c, "#9a968a", poeira)
    prof = 6.0; xc = xf + lado * prof / 2
    L = Lote(nome)
    mats = {"parede": M(pc(cor), pc(_mix(cor, "#000000", 0.28))), "escuro": M(pc(_mix(cor, "#000000", 0.4))), "claro": M(pc(_mix(cor, "#ffffff", 0.25))),
            "vidro": M(pc("#1d2622"), pc("#141a17"), "#6a7a72"), "luz": brilha("#e8c47a", 1.3), "metal": M(pc("#6a6e70"), pc("#4a4e50")),
            "toldo": M(pc(rnd.choice(("#7a3a30", "#46604f", "#4f6275", "#8a6a3a"))), None), "porta": M(pc("#5a5e5c"), pc("#3e4240"))}
    if ruina:
        # paredes quebradas: pedaços de alturas diferentes, sem vidro, vãos escuros
        y = y0
        while y < y0 + comp:
            w = rnd.uniform(0.8, 2.2); h = rnd.uniform(0.8, alt * 0.8)
            L.caixa("parede", (xc, y + w / 2, h / 2), (prof, w, h))
            if h > 1.6:
                L.caixa("vidro", (xf - lado * 0.01, y + w / 2, h * 0.6), (0.04, w * 0.5, 0.7))
            y += w
        for k in range(int(comp)):
            L.caixa("escuro", (xf - lado * rnd.uniform(0.3, 1.6), y0 + rnd.uniform(0, comp), 0.15), (rnd.uniform(0.3, 0.9), rnd.uniform(0.3, 0.9), rnd.uniform(0.15, 0.45)))
        return L.fecha(mats)
    L.caixa("parede", (xc, y0 + comp / 2, alt / 2), (prof, comp, alt))
    L.caixa("escuro", (xf - lado * 0.08, y0 + comp / 2, alt + 0.06), (0.25, comp + 0.1, 0.18))                  # cornija
    L.caixa("escuro", (xf - lado * 0.04, y0 + comp / 2, 3.1), (0.1, comp, 0.12))                                   # faixa entre loja e andares
    n = max(1, int(comp / 1.9)); passo = comp / n
    andares = [3.6 + 1.6 * k for k in range(int((alt - 3.8) / 1.6))]
    for i in range(n):
        yc = y0 + (i + 0.5) * passo
        for j, z in enumerate(andares):
            L.caixa("claro", (xf - lado * 0.04, yc, z - 0.08), (0.1, 0.95, 0.06))                                  # peitoril
            L.caixa("escuro", (xf - lado * 0.02, yc, z + 0.45), (0.06, 0.92, 1.0))                                 # moldura
            L.caixa("luz" if rnd.random() < 0.12 else "vidro", (xf - lado * 0.045, yc, z + 0.45), (0.04, 0.76, 0.84))
            L.caixa("escuro", (xf - lado * 0.06, yc, z + 0.45), (0.03, 0.04, 0.84))                                # caixilho do meio
            if rnd.random() < 0.18:                                                                                 # aparelho de ar
                L.caixa("metal", (xf - lado * 0.22, yc + 0.25, z - 0.32), (0.4, 0.55, 0.36))
            if rnd.random() < 0.12 and j > 0:                                                                       # varanda com grade
                L.caixa("claro", (xf - lado * 0.45, yc, z - 0.12), (0.9, 1.6, 0.08))
                for b in range(9):
                    L.caixa("metal", (xf - lado * 0.88, yc - 0.75 + 0.19 * b, z + 0.35), (0.025, 0.025, 0.9))
                L.caixa("metal", (xf - lado * 0.88, yc, z + 0.8), (0.04, 1.6, 0.04))
    # térreo: loja com porta de aço, toldo e placa
    yl = y0 + comp / 2
    L.caixa("porta", (xf - lado * 0.03, yl, 1.25), (0.06, min(comp - 0.6, 3.2), 2.5))
    for k in range(14):
        L.caixa("escuro", (xf - lado * 0.065, yl, 0.15 + 0.17 * k), (0.012, min(comp - 0.6, 3.2), 0.02))
    L.caixa("toldo", (xf - lado * 0.55, yl, 2.85), (1.1, min(comp - 0.4, 3.5), 0.08))
    L.caixa("toldo", (xf - lado * 1.08, yl, 2.65), (0.04, min(comp - 0.4, 3.5), 0.4))
    L.caixa("metal", (xf - lado * 0.1, y0 + 0.2, alt / 2), (0.08, 0.08, alt))                                     # calha
    if rnd.random() < 0.6:                                                                                          # caixa d'água no telhado
        L.caixa("claro", (xc, y0 + comp * 0.3, alt + 0.6), (1.2, 1.2, 1.1))
    obs = L.fecha(mats)
    if loja:
        t = lib.text(nome + "_placa", loja, 0.42, plano(pc("#e8e0c8")), None, (xf - lado * 0.08, yl, 3.28), lib.font())
        t.rotation_euler = (math.pi / 2, 0, math.radians(90 if lado > 0 else -90))
    return obs


def carro(nome, loc, rot=0.0, cor="#4f6275", poeira=0.0):
    """carro popular estacionado (3,8 x 1,6 m): carroceria, cabine com vidros, rodas, faróis"""
    pc = lambda c: _mix(c, "#9a968a", poeira)
    r = empty(nome, None, loc); r.rotation_euler.z = math.radians(rot)
    caixa(nome + "_corpo", (3.8, 1.6, 0.7), M(pc(cor), pc(_mix(cor, "#000000", 0.3)), "#e0d6bc"), r, (0, 0, 0.6), chanfro=0.12)
    caixa(nome + "_cabine", (2.0, 1.45, 0.6), M(pc(cor), pc(_mix(cor, "#000000", 0.3))), r, (-0.2, 0, 1.2), chanfro=0.15)
    for sy in (-1, 1):
        caixa(f"{nome}_vidro{sy}", (1.7, 0.04, 0.42), M(pc("#26302c"), pc("#1a201c"), "#8a9a92"), r, (-0.2, sy * 0.73, 1.22), chanfro=0.04, contorno=0.0)
    caixa(nome + "_parabrisa", (0.04, 1.3, 0.45), M(pc("#26302c"), pc("#1a201c"), "#8a9a92"), r, (0.82, 0, 1.2), chanfro=0.03, contorno=0.0, rot=(0, 25, 0))
    for sx in (-1.25, 1.25):
        for sy in (-0.78, 0.78):
            cilindro(f"{nome}_roda{sx}{sy}", 0.3, 0.22, M("#1c1c22"), r, (sx, sy, 0.3), seg=20, eixo="Y")
            cilindro(f"{nome}_calota{sx}{sy}", 0.16, 0.23, M(pc("#9aa0a8")), r, (sx, sy, 0.3), seg=16, eixo="Y", contorno=0.0)
    for sy in (-0.55, 0.55):
        caixa(f"{nome}_farol{sy}", (0.04, 0.3, 0.14), M(pc("#e8e2cc")), r, (1.91, sy, 0.72), chanfro=0.02, contorno=0.0)
    return r


def arvore(nome, loc, s=1.0, cor="#4a5a3e", seca=False):
    r = empty(nome, None, loc); r.scale = (s,) * 3
    tubo(nome + "_tronco", [(0, 0, 0), (0.05, 0, 1.4), (-0.05, 0, 2.4)], [0.12, 0.09, 0.07], M("#4a3a2a", "#2e241a"), r, seg=12, tampa=3)
    if seca:
        for k in range(5):
            a = 2 * math.pi * k / 5
            tubo(f"{nome}_galho{k}", [(-0.05, 0, 2.2), (0.6 * math.cos(a), 0.6 * math.sin(a), 3.0)], [0.04, 0.015], M("#3a3026"), r, seg=8, tampa=2)
        return r
    rnd = random.Random(int(loc[1] * 10))
    for k in range(6):
        esfera(f"{nome}_copa{k}", rnd.uniform(0.6, 0.9), rnd.uniform(0.6, 0.9), rnd.uniform(0.5, 0.75), M(_mix(cor, "#000000", rnd.uniform(0, 0.15)), _mix(cor, "#000000", 0.35)),
               r, (rnd.uniform(-0.5, 0.5), rnd.uniform(-0.5, 0.5), 2.8 + rnd.uniform(-0.2, 0.6)), contorno=0.008, seg=20, an=12)
    return r


def poste_luz(nome, loc, lado=1, torto=0.0, poeira=0.0):
    """poste de concreto com a luminária em braço; torto = inclinação (graus) depois da onda"""
    pc = lambda c: _mix(c, "#9a968a", poeira)
    r = empty(nome, None, loc); r.rotation_euler = (0, math.radians(torto * lado), 0)
    cilindro(nome + "_poste", 0.11, 7.2, M(pc("#8a8a80"), pc("#6a6a60")), r, (0, 0, 3.6), seg=12, r2=0.08)
    tubo(nome + "_braco", [(0, 0, 6.6), (-lado * 0.6, 0, 6.9), (-lado * 1.4, 0, 6.95)], [0.035] * 3, M(pc("#6a6a60")), r, seg=10, tampa=3)
    caixa(nome + "_lum", (0.5, 0.22, 0.12), M(pc("#4a4a44")), r, (-lado * 1.5, 0, 6.88), chanfro=0.03)
    caixa(nome + "_traves", (0.9, 0.06, 0.06), M(pc("#5a5a50")), r, (0, 0, 6.2), chanfro=0.01)
    return r


def fio(nome, a, b, flecha=0.5, r=0.012):
    """fio elétrico caído entre dois pontos (catenária simples)"""
    pts = []
    for k in range(13):
        u = k / 12
        p = Vector(a).lerp(Vector(b), u); p.z -= flecha * 4 * u * (1 - u)
        pts.append(tuple(p))
    return tubo(nome, pts, [r] * len(pts), M("#1c1c22"), None, seg=6, tampa=2, contorno=0.0)


def rua3d(p, y0=-8.0, y1=46.0, larg=3.4, seed=3, ruina=False, poeira=0.0, carros=True):
    """a rua inteira: asfalto com faixa, meio-fio e calçada de verdade (degrau), prédios dos dois lados, postes com fios, árvores, carros, lixeiras"""
    import cena, props
    rnd = random.Random(seed)
    pc = lambda c: _mix(c, "#9a968a", poeira)
    cena.poly_mesh("asfalto", [(-larg, y0, 0), (larg, y0, 0), (larg, y1, 0), (-larg, y1, 0)], props.FM(pc("#3c3f39")))
    y = y0
    while y < y1:
        cena.poly_mesh(f"faixa_{int(y * 10)}", [(-0.06, y, 0.004), (0.06, y, 0.004), (0.06, y + 1.4, 0.004), (-0.06, y + 1.4, 0.004)], props.FM(pc("#b8b098")))
        y += 3.0
    for s in (-1, 1):
        caixa(f"calcada{s}", (1.8, y1 - y0, 0.15), M(pc("#7a7a6e"), pc("#5e5e54")), None, (s * (larg + 0.9), (y0 + y1) / 2, 0.075), chanfro=0.0, contorno=0.0)
        caixa(f"meiofio{s}", (0.14, y1 - y0, 0.17), M(pc("#a8a494"), pc("#7e7a6c")), None, (s * (larg + 0.07), (y0 + y1) / 2, 0.085), chanfro=0.02, contorno=0.003)
    tons = ["#7a7462", "#857c66", "#66705e", "#8a7e6a", "#6f746c", "#7d6e5c", "#8e8a78"]
    lojas = list(LOJAS); rnd.shuffle(lojas)
    for s in (-1, 1):
        y = y0; k = 0
        while y < y1:
            comp = rnd.choice((5.0, 6.0, 7.5)); alt = rnd.choice((5.6, 7.2, 8.8, 10.4))
            predio(f"pr{s}_{k}", s * (larg + 1.8), y, comp, alt, rnd.choice(tons), s, seed=seed * 31 + k * 7 + s, loja=lojas[(k + (s > 0) * 3) % len(lojas)] if rnd.random() < 0.7 else None,
                   ruina=ruina, poeira=poeira)
            y += comp + rnd.choice((0.0, 0.0, 0.0, 1.6)); k += 1
    postes = []
    for s in (-1, 1):
        y = y0 + 4.0; k = 0
        while y < y1:
            postes.append(poste_luz(f"poste{s}_{k}", (s * (larg + 0.45), y, 0.15), lado=s, torto=(rnd.choice((-14, 9, 18, -6)) if ruina else 0.0), poeira=poeira))
            if not ruina and k % 2 == 0:
                arvore(f"arv{s}_{k}", (s * (larg + 1.2), y + 2.6, 0.15), rnd.uniform(0.85, 1.1))
            elif ruina and k % 3 == 0:
                arvore(f"arv{s}_{k}", (s * (larg + 1.2), y + 2.6, 0.15), rnd.uniform(0.85, 1.1), seca=True)
            y += 9.0; k += 1
    if not ruina:
        for s in (-1, 1):
            ys = [p_.location.y for p_ in postes if (p_.location.x > 0) == (s > 0)]
            for a, b in zip(ys, ys[1:]):
                for h in (6.25, 6.0):
                    fio(f"fio{s}_{a:.0f}_{h}", (s * (larg + 0.45), a, h), (s * (larg + 0.45), b, h), flecha=0.45)
        for a in [p_.location.y for p_ in postes if p_.location.x > 0][::2]:
            fio(f"fio_cruza_{a:.0f}", (-(larg + 0.45), a, 6.1), (larg + 0.45, a + 1.0, 6.1), flecha=0.8)
    if carros:
        cores = ["#4f6275", "#7a3a30", "#8a8a80", "#46604f", "#a89f86"]
        for k in range(5):
            s = rnd.choice((-1, 1)); yy = y0 + 6 + k * 9 + rnd.uniform(-1.5, 1.5)
            c = carro(f"carro{k}", (s * (larg - 1.05), yy, 0.0), rot=90 + rnd.uniform(-3, 3), cor=cores[k % len(cores)], poeira=poeira)
            if ruina:
                c.rotation_euler = (math.radians(rnd.uniform(-6, 6)), math.radians(rnd.uniform(-4, 4)), math.radians(90 + rnd.uniform(-25, 25)))
        for k in range(4):
            s = rnd.choice((-1, 1))
            cilindro(f"lixeira{k}", 0.25, 0.8, M(pc("#46604f"), pc("#2e4034")), None, (s * (larg + 0.4), y0 + 3 + 11 * k, 0.55), seg=16)


def entrada_bunker(nome, loc=(0, 24.0, 0), s=1.0, aberta=0.85, poeira=0.0):
    """a entrada do abrigo no fim da rua: bloco de concreto meio enterrado num monte de terra, pórtico grosso em volta da porta de cofre
    (aberta, com a luz âmbar de dentro), placa ABRIGO, lâmpada de grade em cima da porta, sacos de areia dos lados e o respiro no topo.
    O vão tem 1,5 m de largura: quem corre entra pelo meio sem encostar no batente."""
    import lib
    pc = lambda c: _mix(c, "#9a968a", poeira)
    r = empty(nome, None, loc); r.scale = (s,) * 3
    conc, conc_e, terra = M(pc("#6f7268"), pc("#55584f"), "#c8c4b0"), M(pc("#585b52")), M(pc("#4f523f"), pc("#3a3d2e"), "#9a9a7a")
    caixa(nome + "_bloco", (7.0, 4.5, 3.4), conc, r, (0, 3.45, 1.7), chanfro=0.08)          # a frente do bloco fica atrás do túnel da porta
    caixa(nome + "_bloco_frente", (7.0, 1.2, 3.4), conc, r, (0, 0.6, 1.7), chanfro=0.0, contorno=0.0) if False else None
    for sx in (-1, 1):
        caixa(f"{nome}_lado{sx}", (2.6, 1.3, 3.4), conc, r, (sx * 2.2, 0.6, 1.7), chanfro=0.04)
    caixa(nome + "_teto_tunel", (1.9, 1.3, 0.75), conc, r, (0, 0.6, 3.02), chanfro=0.02)
    rnd = random.Random(5)
    for k in range(9):                                                         # o monte de terra que cobre o bloco
        x = -4.6 + 1.15 * k
        esfera(f"{nome}_terra{k}", rnd.uniform(1.6, 2.2), rnd.uniform(2.6, 3.2), rnd.uniform(1.5, 2.3) * (1.4 if abs(x) < 2.5 else 1.0), terra, r,
               (x, 3.4 + rnd.uniform(-0.3, 0.3), 2.2 if abs(x) < 3.2 else 0.6), contorno=0.008, seg=24, an=14)
    for sx in (-1, 1):                                                         # pórtico: colunas e viga grossas
        caixa(f"{nome}_col{sx}", (1.3, 0.6, 3.0), conc, r, (sx * 1.4, -0.15, 1.5), chanfro=0.05)
    caixa(nome + "_viga", (4.1, 0.7, 0.6), conc, r, (0, -0.2, 3.15), chanfro=0.05)
    caixa(nome + "_soleira", (1.6, 0.8, 0.08), conc_e, r, (0, -0.25, 0.04), chanfro=0.02)
    caixa(nome + "_dentro", (1.5, 0.2, 2.6), brilha("#e0b860", 1.25), r, (0, 0.9, 1.3), chanfro=0.0, contorno=0.0)
    caixa(nome + "_tunel_e", (0.1, 1.2, 2.6), M(pc("#4a4a3e")), r, (-0.76, 0.35, 1.3), chanfro=0.0, contorno=0.0)
    caixa(nome + "_tunel_d", (0.1, 1.2, 2.6), M(pc("#4a4a3e")), r, (0.76, 0.35, 1.3), chanfro=0.0, contorno=0.0)
    O3.halo_cam(nome + "_luz_dentro", (0, -0.1, 1.4), 2.2, "#e0b860", 0.4, pai=r)
    p_ = O3.porta3d(nome + "_porta", (0, 0.12, 0.0), 1.15, aberta=aberta, pai=r, lado="fora")   # a mesma porta da cena de dentro, vista de fora
    caixa(nome + "_placa", (1.3, 0.06, 0.32), M(pc("#b88a52"), pc("#8a6234")), r, (0, -0.58, 3.15), chanfro=0.02)
    t = lib.text(nome + "_placa_t", "ABRIGO", 0.22, plano(pc("#2a1c0e")), r, (0, -0.62, 3.12), lib.font()); t.rotation_euler = (math.pi / 2, 0, 0)
    O3.lampada3d(nome + "_lamp", (0, -0.6, 2.75), 1.0, acesa=True, fio=0.05)
    for sx in (-1, 1):                                                         # sacos de areia
        for k in range(6):
            fila, col = divmod(k, 3)
            caixa(f"{nome}_saco{sx}_{k}", (0.6, 0.38, 0.24), M(pc("#8a7e5e"), pc("#6a6046"), "#c8b88a"), r,
                  (sx * (2.4 + 0.62 * col + 0.3 * (fila % 2)), -0.7, 0.13 + 0.23 * fila), chanfro=0.09, contorno=0.004)
    cilindro(nome + "_respiro", 0.22, 1.6, M(pc("#7a7e74")), r, (2.2, 2.4, 4.3), seg=20)
    cilindro(nome + "_respiro_t", 0.36, 0.12, M(pc("#5a5e54")), r, (2.2, 2.4, 5.15), seg=20)
    return r
