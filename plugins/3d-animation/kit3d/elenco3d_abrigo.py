"""O elenco de "O abrigo" em 3D de verdade (mesmo desenho do 2D, com volume e câmera livre), para as cenas em que a gente mescla:
close que gira em volta do rosto, a porta que se fecha vista do corredor, o Zé sozinho jogando baralho.
Mesma paleta apagada do elenco_abrigo (Walking Dead). Cada função devolve um Heroi3D já com cabelo e acessórios; a Pipoca é uma peça própria.
Uso: h = elenco3d_abrigo.faz("ze", "ze3"); h.pose(...); h.rosto(boca="reta", lid=0.45)"""
import math
import bpy
from mathutils import Vector
import heroi3d as H3
from heroi3d import Heroi3D, esfera, tubo, estilo, _interp, JAQUETA

PAL = {"poeira": "#a89f86", "oliva": "#59603f", "musgo": "#46604f", "jeans": "#4f6275", "concreto": "#8c8d84", "tijolo": "#8e302b"}
BORDA = "#d9c08a"                                          # borda de luz âmbar fraca (a lâmpada do abrigo)


def _M(h, cor):
    return estilo(cor, None, h.borda)


def _casca(nome, h, k, z_cima, z_baixo, mat, contorno=0.005, phi=None, colunas=120, linhas=16):
    """pedaço de casca esférica em volta do crânio (raio k x o da cabeça), costurado como grade: cada coluna (azimute, 0 = frente, -y) vai de
    z_cima(azimute) até z_baixo(azimute), em raios acima do centro. O contorno é liso (nada de dente de serra): é assim que sai uma linha do cabelo.
    z_cima = 1 fecha no topo da cabeça. phi = (a, b) em radianos recorta só uma fatia do azimute (a barba não dá a volta)."""
    import bmesh
    r = h.R
    bm = bmesh.new()
    a0, a1 = phi if phi else (0.0, 2 * math.pi)
    n = colunas if not phi else int(colunas * (a1 - a0) / (2 * math.pi)) + 1
    def pt(a, z):
        q = math.sqrt(max(0.0, 1 - z * z))
        return (k * r * q * math.sin(a), -k * r * q * math.cos(a), k * r * z)
    cols = []
    for c in range(n):
        a = a0 + (a1 - a0) * c / (n if not phi else n - 1)
        za, zb = z_cima(a), z_baixo(a)
        cols.append([(a, za + (zb - za) * j / linhas) for j in range(linhas + 1)])
    polo = bm.verts.new(pt(0.0, 1.0)) if all(abs(z_cima(a) - 1.0) < 1e-6 for a, _ in [(c[0][0], 0) for c in cols]) else None
    V = [[(polo if (polo and j == 0) else bm.verts.new(pt(a, z))) for j, (a, z) in enumerate(col)] for col in cols]
    for c in range(n if not phi else n - 1):
        c2 = (c + 1) % n
        for j in range(linhas):
            vs = [V[c][j], V[c2][j], V[c2][j + 1], V[c][j + 1]]
            uniq = []
            for v in vs:
                if v not in uniq:
                    uniq.append(v)
            if len(uniq) >= 3:
                bm.faces.new(uniq)
    return H3._objeto(nome, bm, mat, h.cabeca, (0, 0, r), contorno)


def _frente(y):
    return max(0.0, -y)


def cabelo(h, tipo, cor):
    """cabelo de casca com linha do cabelo de verdade: alto na testa (acima da sobrancelha), mais baixo nas costeletas e na nuca"""
    m = _M(h, cor); r = h.R; C = h.cabeca
    topo = {"curto": 0.80, "recuado": 0.90, "coque": 0.76, "solto": 0.74}[tipo]       # onde o cabelo começa na testa
    nuca = {"curto": -0.05, "recuado": 0.05, "coque": -0.30, "solto": -0.80}[tipo]    # até onde ele desce atrás
    def baixo(a):
        f = max(0.0, math.cos(a)) ** 1.25                                              # 1 na frente, 0 nos lados e atrás
        return nuca + (topo - nuca) * f - 0.35 * abs(math.sin(a)) ** 3 * (1 - f)       # as costeletas descem um pouco
    _casca(h.nome + "_cab", h, 1.045, lambda a: 1.0, baixo, m)
    if tipo == "coque":
        esfera(h.nome + "_coque", r * 0.4, r * 0.4, r * 0.36, m, C, (0, r * 0.62, r * 1.95), contorno=0.005, seg=28, an=16)
    elif tipo == "solto":
        esfera(h.nome + "_massa", r * 0.95, r * 0.42, r * 1.05, m, C, (0, r * 0.62, r * 0.3), contorno=0.005, seg=36, an=20)


def barba(h, cor):
    """barba por fazer: casca fina na parte de baixo do rosto (mandíbula e queixo); a boca (traço branco) passa por cima"""
    def cima(a):
        return 0.12 - 0.42 * max(0.0, math.cos(a))
    _casca(h.nome + "_barba", h, 1.016, cima, lambda a: -0.98, _M(h, cor), contorno=0.0, phi=(-2.0, 2.0), colunas=96, linhas=14)


def bigode(h, cor):
    pts = [h._sobre_cabeca(x, -0.052 - 0.02 * (1 - abs(x) / 0.075), 1.012) for x in (-0.075, -0.04, 0.0, 0.04, 0.075)]
    tubo(h.nome + "_bigode", pts, [0.0075 * h.R / 0.2] * 5, _M(h, cor), h.cabeca, seg=10, tampa=4, contorno=0.0)


def bone(h, cor):
    """boné: casca que cobre o alto e a nuca (acima da sobrancelha na frente) e a aba curta"""
    r = h.R; C = h.cabeca; m = _M(h, cor)
    _casca(h.nome + "_bone", h, 1.075, lambda a: 1.0, lambda a: -0.05 + 0.78 * max(0.0, math.cos(a)) ** 1.1, m)
    esfera(h.nome + "_aba", r * 0.72, r * 0.5, r * 0.045, m, C, (0, -r * 0.98, r * 1.72), contorno=0.005, seg=32, an=10)


def tiara(h, cor="#8e8c84", gema="#7a4a4a"):
    r = h.R; C = h.cabeca; el = math.radians(52); pts = []
    for i, a in enumerate(range(-70, 71, 10)):
        k = 1.03 + (0.03 if i % 2 else 0.0)
        a = math.radians(a)
        pts.append((r * k * math.cos(el) * math.sin(a), -r * k * math.cos(el) * math.cos(a), r + r * k * math.sin(el) + (0.02 if i % 2 else 0.0)))
    tubo(h.nome + "_tiara", pts, [0.006] * len(pts), _M(h, cor), C, seg=10, tampa=4, contorno=0.0)
    esfera(h.nome + "_gema", 0.012, 0.008, 0.012, _M(h, gema), C, (0, -r * 0.62, r + r * 0.92), contorno=0.0, seg=12, an=8)


def tranca(h, cor):
    r = h.R; C = h.cabeca; m = _M(h, cor)
    for s, x in (("F", -1), ("B", 1)):
        esfera(f"{h.nome}_tranca{s}", r * 0.2, r * 0.2, r * 0.55, m, C, (x * r * 1.0, r * 0.15, r * 0.72), contorno=0.005, seg=20, an=12)


def _zp(h, z):
    bw = h.bw
    return 0.6 * _interp([(a, b * bw) for a, b in JAQUETA], z) + 0.025


def avental(h, cor):
    esfera(h.nome + "_av", 0.118 * h.bw, 0.012, 0.27, _M(h, cor), h.tronco, (0, -_zp(h, 0.12) - 0.004, 0.1), contorno=0.005, seg=32, an=16)
    for s, x in (("F", -1), ("B", 1)):
        tubo(f"{h.nome}_av_alca{s}", [(x * 0.07, -_zp(h, 0.34) - 0.008, 0.34), (x * 0.03, -_zp(h, 0.44) - 0.008, 0.44)], [0.007] * 2, _M(h, cor), h.tronco, seg=10, tampa=4, contorno=0.0)


def colete(h, cor):
    for s, x in (("F", -1), ("B", 1)):
        esfera(f"{h.nome}_colete{s}", 0.052 * h.bw, 0.014, 0.25, _M(h, cor), h.tronco, (x * 0.075 * h.bw, -_zp(h, 0.18) - 0.004, 0.16), contorno=0.005, seg=24, an=14)


# nome -> (parâmetros do Heroi3D, acessórios, escala)
ESPEC = {
    "ze": dict(roupa=PAL["oliva"], calca="#3a3a32", escura="#3f452c", gola="#3f452c", cabeca=0.78, body_w=1.18, arm_len=1.12, acess=[("cabelo", "recuado", "#c9c6ba"), ("barba", "#3a3a36"), ("bigode", "#c9c6ba")]),
    "lu": dict(roupa=PAL["jeans"], calca="#2d3036", escura="#3e4e5f", gola="#3e4e5f", cabeca=0.76, body_w=1.02, arm_len=1.14, acess=[("cabelo", "coque", "#3a2a22")]),
    "lu_fraca": dict(roupa=PAL["concreto"], calca="#2d3036", escura="#6e6f68", gola="#6e6f68", cabeca=0.76, body_w=0.86, arm_len=1.14, acess=[("cabelo", "coque", "#3a2a22")]),
    "rita": dict(roupa="#8a6c6a", calca="#4a4a42", escura="#6a4e4c", gola="#6a4e4c", cabeca=0.96, body_w=0.92, arm_len=0.95, escala=0.74, acess=[("cabelo", "curto", "#3a2418"), ("tranca", "#3a2418"), ("tiara",)]),
    "eu": dict(roupa="#6e2422", calca="#363c48", escura="#5a1c1a", gola="#5a1c1a", cabeca=0.78, body_w=1.04, arm_len=1.12, acess=[("cabelo", "curto", "#2a1c16")]),
    # vizinhos da multidão (para ninguém ser clone do outro)
    "viz1": dict(roupa="#7a6a58", calca="#3a3631", escura="#5e5244", gola="#5e5244", cabeca=0.78, body_w=1.1, arm_len=1.12, acess=[("cabelo", "solto", "#2e2420")]),
    "viz2": dict(roupa="#56656e", calca="#2f3236", escura="#434f57", gola="#434f57", cabeca=0.8, body_w=1.08, arm_len=1.14, acess=[("cabelo", "curto", "#1e1a18"), ("barba", "#2a2826")]),
    "viz3": dict(roupa="#8a7d5e", calca="#3e3a30", escura="#6e6448", gola="#6e6448", cabeca=0.78, body_w=1.16, arm_len=1.12, acess=[("cabelo", "recuado", "#bdb9ad"), ("bigode", "#bdb9ad")]),
    "viz4": dict(roupa="#6c5866", calca="#33302f", escura="#54434f", gola="#54434f", cabeca=0.76, body_w=1.0, arm_len=1.12, acess=[("cabelo", "coque", "#4a3a30")]),
    "padeira": dict(roupa="#b2a88f", calca="#3d3631", escura="#8f866f", gola="#8f866f", cabeca=0.78, body_w=1.14, arm_len=1.12, acess=[("cabelo", "coque", "#c9c6ba"), ("avental", "#8a5a4a")]),
    "mercado": dict(roupa="#a5a28c", calca="#33362e", escura="#7d7a68", gola="#7d7a68", cabeca=0.78, body_w=1.04, arm_len=1.16, acess=[("bone", PAL["musgo"]), ("colete", PAL["musgo"])]),
}


def faz(chave, nome):
    e = dict(ESPEC[chave]); acess = e.pop("acess")
    h = Heroi3D(nome, sapato="#1e2420", borda=BORDA, **e)
    h.bw = e.get("body_w", 1.0)
    for a in acess:
        {"cabelo": cabelo, "barba": barba, "bigode": bigode, "bone": bone, "tiara": tiara, "tranca": tranca, "avental": avental, "colete": colete}[a[0]](h, *a[1:])
    return h


def pipoca(nome, loc=(0, 0, 0), escala=1.0, rot=0.0):
    """Pipoca em 3D (0,26 m, de focinho para -Y): pelo marrom com mancha cor de areia, orelhas murchas, suéter de tricô vermelho-tijolo com listra e remendo"""
    from lib import empty
    PEL, PEL_S, AREIA, VER, VER_S, CRE = "#6e4e34", "#4e3623", "#b89c70", "#7a2a26", "#541c1a", "#a89f86"
    R = empty(nome, None, loc); R.scale = (escala,) * 3; R.rotation_euler.z = math.radians(rot)
    M = lambda c: estilo(c, None, BORDA)
    esfera(nome + "_corpo", 0.085, 0.15, 0.09, M(PEL), R, (0, 0.0, 0.095), contorno=0.003, seg=40, an=22)
    esfera(nome + "_cab", 0.07, 0.085, 0.07, M(PEL), R, (0, -0.16, 0.1), contorno=0.003, seg=36, an=20)
    esfera(nome + "_mancha", 0.02, 0.03, 0.012, M(AREIA), R, (0, -0.185, 0.165), contorno=0.0, seg=16, an=10)
    esfera(nome + "_focinho", 0.012, 0.012, 0.011, M("#2a1a14"), R, (0, -0.243, 0.09), contorno=0.0, seg=12, an=8)
    for s, x in (("F", -1), ("B", 1)):
        esfera(f"{nome}_orelha{s}", 0.022, 0.008, 0.028, M("#7a5a4e"), R, (x * 0.052, -0.14, 0.165), contorno=0.003, seg=16, an=10)
        esfera(f"{nome}_olho{s}", 0.0105, 0.008, 0.0115, M("#0d1020"), R, (x * 0.047, -0.2245, 0.124), contorno=0.0, seg=12, an=8)
        esfera(f"{nome}_pata_f{s}", 0.022, 0.035, 0.02, M(PEL_S), R, (x * 0.05, -0.115, 0.02), contorno=0.003, seg=16, an=10)
        esfera(f"{nome}_pata_t{s}", 0.025, 0.04, 0.02, M(PEL_S), R, (x * 0.055, 0.1, 0.02), contorno=0.003, seg=16, an=10)
    esfera(nome + "_sue", 0.09, 0.1, 0.098, M(VER), R, (0, 0.05, 0.097), contorno=0.004, seg=40, an=22)
    esfera(nome + "_gola", 0.074, 0.03, 0.08, M(VER_S), R, (0, -0.072, 0.105), contorno=0.004, seg=28, an=16)
    esfera(nome + "_lista", 0.0915, 0.011, 0.1, M(CRE), R, (0, 0.05, 0.097), contorno=0.0, seg=36, an=18)
    esfera(nome + "_remendo", 0.012, 0.02, 0.016, M("#6a6a52"), R, (0.088, 0.1, 0.13), contorno=0.0, seg=12, an=8)
    return R
