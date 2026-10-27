"""Elenco do vídeo "O abrigo" (pedido de 24/10/2026: "mais seriedade, personagens mais maduros, paleta de The Walking Dead").
Mesmo boneco do canal (cabeça preta, olho branco, borda de luz), agora adulto de verdade: cabeça menor (0,76 a 0,80), corpo mais largo
e alto, sobrancelha pesada e pálpebra meio caída (cansaço), roupa gasta com barra suja, mancha de poeira e remendo.
Paleta: tudo apagado e barrento (oliva, jeans desbotado, cinza de concreto, poeira, ferrugem); o único vermelho vivo é o suéter da Pipoca
e o vermelho seco do que já aconteceu. A luz de borda é âmbar fraca, de lâmpada de abrigo.
Zé (camisa de trabalho oliva; fecha e abre a porta), Lu (jaqueta jeans; depois, magra, de cinza), Rita (a menor, cardigã suja e a tiara gasta),
a dona da padaria e o rapaz do mercado (lá fora), e o narrador, que nunca aparece: só as mãos (objetos_abrigo.maos_pov).
Uso: H = elenco_abrigo.ze("ze", "q", rim=elenco_abrigo.RIM)"""
import math
from heroi import clip, LAYER
from puppet2d import smooth, stroke, circle
from char2d import rrect, mesh_pts
import elenco as E
from elenco import _base, _esc, _lay, _y, _cor, _corpo, cabelo, bone, bigode, barba, lapelas, botoes, cinto, rugas

RIM = "#d9c08a"
ESCALA = {"rita": 0.74}
CRIANCA = dict(body_w=0.92, head=0.96, leg=0.76, arm=1.0, arm_len=0.88, hand=0.92, neck_len=0.5)
# paleta da série (sai daqui a cor de cada peça; a ficha mostra as amostras)
PAL = {"poeira": "#a89f86", "oliva": "#59603f", "musgo": "#46604f", "jeans": "#4f6275", "concreto": "#8c8d84", "ferrugem": "#8a4a2c",
       "sangue_seco": "#6e2a26", "osso": "#d8d0bb", "noite": "#1e2420", "lampada": "#d9b66a", "tijolo": "#8e302b", "barro": "#6e4e34"}


def sujeira(H, roupa, remendo=None, k=0.34):
    """roupa gasta: barra suja, risco de poeira no peito e, se pedir, um remendo costurado (só de frente e de 3/4)"""
    if H.view == "back":
        return
    corpo = _corpo(H); cx = 0.0 if H.view == "front" else 0.04
    suja = H._mat("suja", _esc(roupa, k))
    pts = clip([(cx - 0.2, -0.06), (cx + 0.2, -0.06), (cx + 0.2, 0.03), (cx + 0.12, 0.075), (cx + 0.05, 0.035), (cx - 0.04, 0.085), (cx - 0.12, 0.04), (cx - 0.2, 0.065)], corpo)
    if len(pts) >= 3:
        mesh_pts(f"{H.name}_suja", pts, suja, H.j["torso"], _y(H, "torso", 0.28))
    mesh_pts(f"{H.name}_risco", stroke([(cx - 0.09, 0.36), (cx + 0.01, 0.22), (cx + 0.05, 0.16)], 0.008), H._mat("risco", _esc(roupa, 0.2)), H.j["torso"], _y(H, "torso", 0.29))
    if remendo:
        mesh_pts(f"{H.name}_rem", rrect(cx + 0.06, 0.1, cx + 0.125, 0.185, 0.004, 1), H._mat("rem", remendo), H.j["torso"], _y(H, "torso", 0.52))
        for i in range(3):
            mesh_pts(f"{H.name}_rem_p{i}", stroke([(cx + 0.06 + 0.02 * i + 0.005, 0.1), (cx + 0.06 + 0.02 * i + 0.005, 0.185)], 0.0016), H._mat("rem_p", "#1e2420"), H.j["torso"], _y(H, "torso", 0.55))


def cabelo2(H, tipo, cor):
    """cabelo de verdade (substitui o 'boné' liso do kit): linha do cabelo irregular acima da sobrancelha, costeleta nas laterais, mechas que riscam o volume.
    tipo: curto | recuado (entradas fundas nas têmporas) | coque (preso, com o coque) | solto (cai até o ombro)"""
    k = _cor(H, f"cab2_{tipo}", cor); L = _lay(H, "head")
    ext = [(0.215 * math.cos(math.radians(a)), 0.215 * math.sin(math.radians(a)) + 0.004) for a in range(-8, 189, 8)]              # contorno de fora, do lado direito ao esquerdo
    if tipo == "recuado":
        inte = [(-0.19, 0.06), (-0.17, 0.115), (-0.125, 0.15), (-0.085, 0.175), (-0.05, 0.168), (0.0, 0.19), (0.05, 0.168), (0.085, 0.175), (0.125, 0.15), (0.17, 0.115), (0.19, 0.06)]
    elif tipo == "coque":
        inte = [(-0.19, 0.02), (-0.18, 0.1), (-0.14, 0.15), (-0.08, 0.17), (-0.02, 0.165), (0.05, 0.172), (0.11, 0.155), (0.165, 0.115), (0.19, 0.04), (0.192, -0.02)]
    elif tipo == "solto":
        inte = [(-0.19, -0.1), (-0.18, 0.06), (-0.14, 0.13), (-0.09, 0.17), (-0.02, 0.15), (0.05, 0.168), (0.11, 0.15), (0.165, 0.1), (0.185, 0.0), (0.19, -0.1)]
    else:
        inte = [(-0.19, 0.03), (-0.18, 0.1), (-0.14, 0.15), (-0.09, 0.172), (-0.03, 0.162), (0.04, 0.175), (0.1, 0.16), (0.16, 0.12), (0.185, 0.06), (0.192, 0.0)]
    pts = ext[::-1] + inte if False else ext + inte
    H.P("cabelo", smooth(pts, 3), k, H.face, L + 0.2, rimw=0.0)
    for i in range(4):                                                                       # mechas: traços um tom mais claro que seguem o volume
        a0 = 28 + 32 * i
        mesh_pts(f"{H.name}_mecha{i}", stroke([(0.17 * math.cos(math.radians(a)), 0.17 * math.sin(math.radians(a)) + 0.004) for a in range(a0, a0 + 26, 5)], 0.003), H._mat("mecha", _esc(cor, -0.0) if False else _mixc(cor)), H.face, -(_lay(H, "head", 0.5)) * LAYER)
    if tipo == "solto":
        for s_ in (-1, 1):
            H.P(f"cab_lado{s_}", smooth([(s_ * 0.19, 0.0), (s_ * 0.245, -0.04), (s_ * 0.26, -0.15), (s_ * 0.22, -0.24), (s_ * 0.185, -0.12)], 4), k, H.face, L - 0.2, rimw=0.004)
    if tipo == "coque":
        H.P("coque", circle(0.0, 0.265, 0.075, 28), k, H.face, L - 0.3, rimw=0.006)


def _mixc(cor):
    h = cor.lstrip("#"); r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return "#%02x%02x%02x" % tuple(min(255, int(c + (255 - c) * 0.22)) for c in (r, g, b))


def barba2(H, cor):
    """barba por fazer: sombra no maxilar, do lado de uma orelha ao outro, subindo nas bochechas; a boca fica por cima"""
    k = _cor(H, "barba2", cor)
    ext = [(0.203 * math.cos(math.radians(a)), 0.203 * math.sin(math.radians(a))) for a in range(188, 353, 8)]
    inte = [(0.168, -0.01), (0.135, -0.04), (0.09, -0.052), (0.04, -0.046), (0.0, -0.056), (-0.04, -0.046), (-0.09, -0.052), (-0.135, -0.04), (-0.168, -0.01)]
    H.P("barba", smooth(ext + inte, 3), k, H.face, _lay(H, "head", 0.3), rimw=0.0)


def tiara(H, cor="#8e8c84", gema="#7a4a4a"):
    """tiara de plástico de criança, já lascada e sem brilho: zigue-zague no alto da cabeça e uma pedra fosca"""
    pts = [(-0.15, 0.14), (-0.1, 0.215), (-0.05, 0.185), (0.0, 0.25), (0.05, 0.185), (0.1, 0.215), (0.15, 0.14)]
    mesh_pts(f"{H.name}_tiara", stroke(pts, 0.014), H._mat("tiara", cor), H.face, -(_lay(H, "head", 1.3)) * LAYER)
    mesh_pts(f"{H.name}_gema", circle(0.0, 0.232, 0.017, 16), H._mat("tiara_g", gema), H.face, -(_lay(H, "head", 1.4)) * LAYER)


def tranca(H, cor="#3a2418"):
    """duas marias-chiquinhas desfeitas, caindo dos lados da cabeça"""
    k = _cor(H, "tranca", cor)
    for s in (-1, 1):
        H.P(f"tranca{s}", smooth([(s * 0.2, 0.08), (s * 0.26, 0.04), (s * 0.275, -0.06), (s * 0.24, -0.15), (s * 0.2, -0.08)], 5), k, H.face, _lay(H, "head", -0.4), rimw=0.006)


def avental(H, cor="#8a5a4a", barra="#a89f86"):
    """avental de padeira, desbotado e manchado: peito e saia, bolso e alça no pescoço"""
    if H.view == "back":
        return
    corpo = _corpo(H); cx = 0.0 if H.view == "front" else 0.04
    pts = clip([(cx - 0.12, 0.34), (cx + 0.12, 0.34), (cx + 0.18, -0.06), (cx - 0.18, -0.06)], corpo)
    if len(pts) >= 3:
        mesh_pts(f"{H.name}_av", pts, H._mat("av", cor), H.j["torso"], _y(H, "torso", 0.3))
    for s_, d in ((-1, -0.1), (1, 0.1)):
        mesh_pts(f"{H.name}_av_{s_}", stroke([(cx + d, 0.34), (cx + d * 0.4, 0.47)], 0.012), H._mat("av", cor), H.j["torso"], _y(H, "torso", 0.3))
    mesh_pts(f"{H.name}_av_bolso", rrect(cx - 0.07, 0.06, cx + 0.07, 0.16, 0.012, 2), H._mat("av_b", _esc(cor, 0.25)), H.j["torso"], _y(H, "torso", 0.45))
    mesh_pts(f"{H.name}_av_linha", rrect(cx - 0.17, -0.06, cx + 0.17, -0.035, 0.004, 1), H._mat("av_c", barra), H.j["torso"], _y(H, "torso", 0.45))
    mesh_pts(f"{H.name}_av_mancha", smooth([(cx - 0.05, 0.28), (cx + 0.02, 0.3), (cx + 0.08, 0.24), (cx + 0.03, 0.2), (cx - 0.04, 0.22)], 3), H._mat("av_m", PAL["sangue_seco"]), H.j["torso"], _y(H, "torso", 0.5))


def ze(name, view="front", rim=RIM, objeto=None):
    """Zé: o mais velho, camisa de trabalho oliva, barba grisalha por fazer, cabelo curto; o que tranca a porta"""
    H = _base(name, view, PAL["oliva"], "#3a3a32", rim, prop=dict(body_w=1.18, head=0.78, leg=0.9, neck_len=0.5, arm=1.06))
    botoes(H, "#8d8a76", (0.2, 0.1, 0.0)); cinto(H, "#2a2118", "#8a7a50"); sujeira(H, PAL["oliva"], remendo="#6e6a4a")
    cabelo2(H, "recuado", "#c9c6ba"); barba2(H, "#3a3a36"); bigode(H, "#c9c6ba"); rugas(H)
    return H


def lu(name, view="front", rim=RIM, objeto=None):
    """Lu: jaqueta jeans desbotada, cabelo preso num coque baixo; a que briga com o Zé"""
    H = _base(name, view, PAL["jeans"], "#2d3036", rim, prop=dict(body_w=1.02, head=0.76, leg=0.96, neck_len=0.6))
    lapelas(H, "#3e4e5f"); botoes(H, "#7a7458", (0.2, 0.1, 0.0)); cabelo2(H, "coque", "#3a2a22"); sujeira(H, PAL["jeans"], remendo="#6e6a58"); rugas(H, "#2a2a34")
    return H


def lu_fraca(name, view="front", rim=RIM, objeto=None):
    """Lu meses depois: top cinza, muito mais magra, cabelo solto sem cuidado; é quando ela morre"""
    H = _base(name, view, PAL["concreto"], "#2d3036", rim, prop=dict(body_w=0.84, head=0.76, leg=0.96, neck_len=0.62, arm=0.88, arm_len=1.0))
    cabelo2(H, "coque", "#3a2a22"); sujeira(H, PAL["concreto"], k=0.4); rugas(H, "#2a2a34")
    return H


def rita(name, view="front", rim=RIM, objeto=None):
    """Rita: a mais nova; cardigã malva suja, marias-chiquinhas soltas e a tiara de plástico lascada"""
    H = _base(name, view, "#8a6c6a", "#4a4a42", rim, prop=dict(CRIANCA))
    cabelo2(H, "curto", "#3a2418"); tranca(H); tiara(H); sujeira(H, "#8a6c6a")
    return H


def padeira(name, view="front", rim=RIM, objeto=None):
    """dona da padaria: blusa de linho suja, avental manchado e coque grisalho; bate na porta do lado de fora"""
    H = _base(name, view, "#b2a88f", "#3d3631", rim, prop=dict(body_w=1.14, head=0.78, leg=0.88, neck_len=0.5))
    avental(H); cabelo2(H, "coque", "#c9c6ba"); rugas(H, "#2a2a34")
    return H


def mercado(name, view="front", rim=RIM, objeto=None):
    """rapaz do mercado: camisa bege suja, colete musgo do uniforme e boné desbotado"""
    H = _base(name, view, "#a5a28c", "#33362e", rim, prop=dict(body_w=1.04, head=0.78, leg=0.94))
    E.colete(H, PAL["musgo"]); bone(H, PAL["musgo"]); sujeira(H, "#a5a28c")
    return H


ELENCO = [("ze", ze), ("lu", lu), ("lu_fraca", lu_fraca), ("rita", rita), ("padeira", padeira), ("mercado", mercado)]
