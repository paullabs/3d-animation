"""Unidades de dinheiro do canal (regra de 23/10/2026: todo número vira proporção, simples como livro infantil).
Sempre as mesmas, para o olho aprender uma vez:
  - notinha  = 1 salário mínimo  -> uma cédula verde de frente (som: tique)
  - maço     = R$ 1 milhão       -> cubo verde de 0,229 m (o tamanho real de 1 milhão em notas de R$ 100; som: papel)
  - cubo     = R$ 1 bilhão       -> cubo verde de 2,29 m, maior que o herói (som: boom)
O cubo é desenhado como um tijolo de dinheiro: frente com as folhas empilhadas e a cinta, tampo com a cédula, laterais mais escuras.
Origem de todo cubo: centro da base."""
import math
import bpy
from lib import empty, key
import curvas
import grana as G
from char2d import rrect
from puppet2d import circle

MACO, CUBO = 0.229, 2.29
FRENTE, LINHA, TAMPO, TAMPO_CL, TAMPO_LUZ, LADO, CINTA, ARESTA = "#b9dcb4", "#86b98d", "#4c9a62", "#a6d9ae", "#7cc28c", "#5f9f6c", "#efe6cf", "#e4f6e2"


def cubo(name, loc, lado=CUBO, parent=None, linhas=9, tarja=False):
    """tijolo de dinheiro de 'lado' metros (maço: 0,229; bilhão: 2,29). tarja=True põe uma faixa preta na frente (nome escondido)"""
    l = lado; h = l / 2
    P = []
    # frente (y = -h): folhas, linhas das camadas e a cinta de papel
    P.append(([(-h, -h, 0), (h, -h, 0), (h, -h, l), (-h, -h, l)], FRENTE))
    for k in range(1, linhas):
        z = l * k / linhas; e = l * 0.006
        P.append(([(-h, -h - l * 0.0004, z - e), (h, -h - l * 0.0004, z - e), (h, -h - l * 0.0004, z + e), (-h, -h - l * 0.0004, z + e)], LINHA))
    c0, c1 = -l * 0.09, l * 0.09
    P.append(([(c0, -h - l * 0.0008, 0), (c1, -h - l * 0.0008, 0), (c1, -h - l * 0.0008, l), (c0, -h - l * 0.0008, l)], CINTA))
    if tarja:
        P.append(([(-h * 0.8, -h - l * 0.0012, l * 0.42), (h * 0.8, -h - l * 0.0012, l * 0.42), (h * 0.8, -h - l * 0.0012, l * 0.58), (-h * 0.8, -h - l * 0.0012, l * 0.58)], "#0b0b10"))
    # laterais
    for x in (-h, h):
        P.append(([(x, -h, 0), (x, h, 0), (x, h, l), (x, -h, l)], LADO))
    # tampo (z = l): a cédula vista de cima, com a cinta atravessando
    P.append(([(-h, -h, l), (h, -h, l), (h, h, l), (-h, h, l)], TAMPO))
    for i, (pts, cor) in enumerate([(circle(0, 0, l * 0.26, 32), TAMPO_CL), (circle(0, 0, l * 0.19, 32), TAMPO_LUZ)]):
        P.append(([(x, y, l + l * 0.0006 * (i + 1)) for x, y in pts], cor))
    P.append(([(c0, -h, l + l * 0.002), (c1, -h, l + l * 0.002), (c1, h, l + l * 0.002), (c0, h, l + l * 0.002)], CINTA))
    # aresta clara de cima da frente (o volume se lê de longe)
    P.append(([(-h, -h - l * 0.001, l - l * 0.012), (h, -h - l * 0.001, l - l * 0.012), (h, -h - l * 0.001, l), (-h, -h - l * 0.001, l)], ARESTA))
    root = empty(name, parent, loc)
    o = G._malha(name + "_m", P, None); o.parent = root
    return root


def maco(name, loc, parent=None):
    return cubo(name, loc, MACO, parent, linhas=6)


def notinha(name, loc, s=2.4, parent=None):
    """uma cédula verde de frente (1 salário mínimo)"""
    return G.nota(name, loc, s, parent)


# ---------------------------------------------------------------- movimentos (curvas suaves e molas, nada de pose a pose)
def esconde_ate(o, f):
    """invisível até o quadro f"""
    base = tuple(o.scale)
    o.scale = (0.0001,) * 3; key(o, "scale", f - 1, "CONSTANT")
    o.scale = base; key(o, "scale", f, "CONSTANT")


def pop(o, f, n=8, s=1.0):
    """aparece com mola (passa um pouco do tamanho e assenta)"""
    esconde_ate(o, f)
    for k in range(n + 1):
        v = s * curvas.mola(k / 24.0, 3.2, 0.42) if k < n else s
        o.scale = (max(v, 0.0001),) * 3; key(o, "scale", f + k, "LINEAR")


def sobe_do_chao(o, f, n=10, s=1.0, passa=0.06):
    """cresce em altura a partir do chão (o cubo 'brota'), com um leve passar do ponto.
    Em pilha use passa=0: o de baixo não pode subir para dentro do de cima"""
    esconde_ate(o, f)
    for k in range(n + 4):
        u = min(1.0, k / n); v = curvas.s("onda" if not passa else "easy", u) + passa * curvas.pancada((k - n) / 24.0, 3.0, 0.4) * (k >= n)
        o.scale = (s, s, max(0.0001, s * v)); key(o, "scale", f + k, "LINEAR")


def cai(o, f, altura=3.0, n=9, quique=0.06):
    """cai do alto em ease-in e assenta com uma mola curta (impacto)"""
    z0 = o.location.z
    esconde_ate(o, f)
    for k in range(n + 1):
        o.location.z = z0 + altura * (1 - curvas.s("queda", k / n)); key(o, "location", f + k, "LINEAR")
    # achata e volta no impacto (squash na escala z)
    base = tuple(o.scale)
    for k in range(10):
        v = 1 - 0.12 * curvas.pancada(k / 24.0, 3.0, 0.35)
        o.scale = (base[0] * (2 - v) ** 0.5, base[1], base[2] * v); key(o, "scale", f + n + k, "LINEAR")
    o.scale = base


def onda_mola(u, passa=0.045):
    """curva "onda" do After Effects (sai devagar, onda rápida no meio) e, depois de chegar (u > 1), passa um pouco do ponto
    e assenta com uma mola curta: nada para seco. u = tempo normalizado da viagem (0 a 1, e além para o assentamento)"""
    if u <= 0:
        return 0.0
    if u <= 1:
        return curvas.s("onda", u)
    k = (u - 1) * 11                                   # ~quadros depois da chegada (viagem de ~11 quadros)
    return 1 + passa * math.sin(math.pi * k / 4.5) * math.exp(-k / 3.2)


def voa(o, f0, f1, p0, p1, alt=0.4, assenta=8):
    """vai de p0 a p1 num arco, na curva onda, e assenta com um quique curto"""
    n = max(1, f1 - f0)
    for f in range(f0, f1 + 1 + assenta):
        t = (f - f0) / n; u = onda_mola(t); a = min(1.0, t)
        o.location = (p0[0] + (p1[0] - p0[0]) * u, p0[1] + (p1[1] - p0[1]) * u, p0[2] + (p1[2] - p0[2]) * u + alt * 4 * a * (1 - a))
        key(o, "location", f, "LINEAR")


def some(o, f, n=5):
    o.scale = o.scale.copy(); key(o, "scale", f, "LINEAR")
    o.scale = (0.0001,) * 3; key(o, "scale", f + n, "LINEAR")


# ---------------------------------------------------------------- o cubo de 1 bilhão como ele é: 1.000 maços (10 x 10 x 10)
GRADE = "#5f9f6c"


def _grade_face(P, eixo, fixo, u0, u1, v0, v1, n, cor=GRADE, e=0.006, off=0.0):
    """linhas de grade sobre uma face: eixo = "xz" (frente, y fixo), "xy" (tampo, z fixo) ou "yz" (lateral, x fixo)"""
    du, dv = (u1 - u0) / n, (v1 - v0) / n
    for k in range(1, n):
        u = u0 + k * du; v = v0 + k * dv
        for (a0, a1, b0, b1) in ((u - e, u + e, v0, v1), (u0, u1, v - e, v + e)):
            if eixo == "xz":
                P.append(([(a0, fixo - off, b0), (a1, fixo - off, b0), (a1, fixo - off, b1), (a0, fixo - off, b1)], cor))
            elif eixo == "xy":
                P.append(([(a0, b0, fixo + off), (a1, b0, fixo + off), (a1, b1, fixo + off), (a0, b1, fixo + off)], cor))
            else:
                P.append(([(fixo + off, a0, b0), (fixo + off, a1, b0), (fixo + off, a1, b1), (fixo + off, a0, b1)], cor))


def cubo_mil(name, loc, lado=CUBO, n=10, tirar=0, parent=None):
    """R$ 1 bilhão = 1.000 maços de R$ 1 milhão (10 x 10 x 10), com a grade de cada maço nas três faces.
    tirar = quantas fileiras da camada de cima (na frente) saem como um bloco à parte: tirar=3 -> 3 x 10 = 30 maços = 3%.
    Devolve (raiz do cubo, raiz do bloco tirado ou None). Origem: centro da base."""
    l = lado; h = l / 2; c = l / n; e = l * 0.0028
    zt = l - c if tirar else l                                  # altura da frente (sem a camada que saiu)
    yt = -h + tirar * c                                         # onde começa o tampo inteiro
    P = []
    P.append(([(-h, -h, 0), (h, -h, 0), (h, -h, zt), (-h, -h, zt)], FRENTE))
    _grade_face(P, "xz", -h, -h, h, 0, zt if not tirar else zt, n if not tirar else n, e=e, off=l * 0.0005)
    if tirar:                                                   # tampo rebaixado onde o bloco saiu + degrau
        P.append(([(-h, -h, zt), (h, -h, zt), (h, yt, zt), (-h, yt, zt)], TAMPO))
        _grade_face(P, "xy", zt, -h, h, -h, yt, n, e=e, off=l * 0.0006)
        P.append(([(-h, yt, zt), (h, yt, zt), (h, yt, l), (-h, yt, l)], FRENTE))
    P.append(([(-h, yt, l), (h, yt, l), (h, h, l), (-h, h, l)], TAMPO))
    _grade_face(P, "xy", l, -h, h, yt, h, n, e=e, off=l * 0.0006)
    for x in (-h, h):
        if tirar:
            P.append(([(x, -h, 0), (x, h, 0), (x, h, l), (x, yt, l), (x, yt, zt), (x, -h, zt)], LADO))
        else:
            P.append(([(x, -h, 0), (x, h, 0), (x, h, l), (x, -h, l)], LADO))
        _grade_face(P, "yz", x, -h, h, 0, l, n, e=e, off=(l * 0.0005) * (1 if x > 0 else -1))
    root = empty(name, parent, loc)
    o = G._malha(name + "_m", P, None); o.parent = root
    bloco = None
    if tirar:
        Q = []
        Q.append(([(-h, -h, zt), (h, -h, zt), (h, -h, l), (-h, -h, l)], FRENTE))
        _grade_face(Q, "xz", -h, -h, h, zt, l, n, e=e, off=l * 0.0005)
        Q.append(([(-h, -h, l), (h, -h, l), (h, yt, l), (-h, yt, l)], TAMPO))
        du = l / n
        for k in range(1, n):                                    # grade do tampo do bloco (10 x tirar)
            u = -h + k * du
            Q.append(([(u - e, -h, l + l * 0.0006), (u + e, -h, l + l * 0.0006), (u + e, yt, l + l * 0.0006), (u - e, yt, l + l * 0.0006)], GRADE))
        for k in range(1, tirar):
            v = -h + k * c
            Q.append(([(-h, v - e, l + l * 0.0006), (h, v - e, l + l * 0.0006), (h, v + e, l + l * 0.0006), (-h, v + e, l + l * 0.0006)], GRADE))
        for x in (-h, h):
            Q.append(([(x, -h, zt), (x, yt, zt), (x, yt, l), (x, -h, l)], LADO))
        Q.append(([(-h, yt, zt), (h, yt, zt), (h, yt, l), (-h, yt, l)], LADO))
        bloco = empty(name + "_bloco", root, (0, 0, 0))
        ob = G._malha(name + "_bloco_m", Q, None); ob.parent = bloco
    return root, bloco
