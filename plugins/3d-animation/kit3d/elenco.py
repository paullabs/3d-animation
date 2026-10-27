"""Elenco do canal (pedido de 23/10/2026: "os outros personagens ficam sem rosto, simplificados demais; dar vida a eles").
Todos usam o MESMO boneco do herói (heroi.Heroi): cabeça preta, olho branco sem pupila, sobrancelha fina, muitas bocas,
traço com contorno e borda de luz. O que muda é a roupa (paleta), o cabelo, o chapéu e os acessórios, sempre desenhados
com o mesmo traço (H.P: contorno fino, sombra e brilho por dentro). Nada de silhueta sem rosto para quem age na cena.
Uso: H = elenco.juiz("juiz1", "front", rim="#ffe4d0")  -> depois Timeline/finish como o herói."""
import math
from heroi import Heroi, clip, LAYER
from puppet2d import smooth, stroke, circle, flatmat
from char2d import rrect, mesh_pts
from lib import empty
import uniforme as U

VIEWX = {"front": dict(eyes=(-0.074, 0.074), mx=0.0), "q": dict(eyes=(0.004, 0.112), mx=0.07)}


def _base(name, view, roupa, calca, rim, sombra=None, outros=None, prop=None):
    """o boneco com a paleta da roupa (jaqueta = roupa, calça = calca)"""
    sh = sombra or _esc(roupa, 0.25)
    M = {"hoodie_sh": flatmat(f"{name}_hoodie_sh", sh), "hoodie_far": flatmat(f"{name}_hoodie_far", _esc(roupa, 0.4)),
         "pants_sh": flatmat(f"{name}_pants_sh", _esc(calca, 0.25)), "pants_far": flatmat(f"{name}_pants_far", _esc(calca, 0.4))}
    pal = dict(U.PAL, hoodie=roupa, dark=sh, hoodie_sh_ink=_esc(roupa, 0.5), pants=calca, rim=rim)
    pal.update(outros or {})
    return Heroi(name, view, pal=pal, mats=M, prop=prop)


def _esc(hexcor, k):
    h = hexcor.lstrip("#"); r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return "#%02x%02x%02x" % (int(r * (1 - k)), int(g * (1 - k)), int(b * (1 - k)))


def _lay(H, parte, d=0.0):
    return H._layers()[parte] + d


def _cor(H, k, cor):
    H._mat(k, cor); return k


def _corpo(H):
    v = "front" if H.view in ("front", "back") else "q"
    bw = H.prop["body_w"]
    return smooth([(x * bw, z) for x, z in U.CORPO[v]], 6)


# ---------------------------------------------------------------- cabelo, chapéus e rosto (presos na cabeça: H.face, raio 0,2)
def cabelo(H, tipo, cor):
    k = _cor(H, f"cab_{tipo}", cor)
    L = _lay(H, "head")
    if tipo == "laterais":                                       # careca com tufos dos lados (mais velho)
        for s in (-1, 1):
            H.P(f"tufo{s}", smooth([(s * 0.17, 0.09), (s * 0.235, 0.06), (s * 0.245, -0.02), (s * 0.2, -0.06), (s * 0.16, 0.0)], 6), k, H.face, L - 0.3, rimw=0.006)
    elif tipo == "penteado":                                     # penteado para trás, liso
        pts = [(0.215 * math.cos(math.radians(a)), 0.215 * math.sin(math.radians(a)) + 0.005) for a in range(15, 166, 10)]
        pts += [(0.19 * math.cos(math.radians(a)), 0.12 + 0.025 * math.cos(math.radians(a))) for a in range(165, 14, -15)]
        H.P("cabelo", smooth(pts, 4), k, H.face, L + 0.2, rimw=0.0)   # forma côncava: sem brilho (o recorte só aceita forma convexa)
    elif tipo == "coque":                                        # cabelo preso em coque (juíza)
        pts = [(0.215 * math.cos(math.radians(a)), 0.215 * math.sin(math.radians(a))) for a in range(5, 176, 10)]
        pts += [(0.2 * math.cos(math.radians(a)), 0.09) for a in range(175, 4, -15)]
        H.P("cabelo", smooth(pts, 4), k, H.face, L + 0.2, rimw=0.0)   # forma côncava: sem brilho (o recorte só aceita forma convexa)
        H.P("coque", circle(0.0, 0.25, 0.085, 32), k, H.face, L - 0.3, rimw=0.008)
    elif tipo == "curto":
        pts = [(0.212 * math.cos(math.radians(a)), 0.212 * math.sin(math.radians(a))) for a in range(20, 161, 10)]
        pts += [(0.16 * math.cos(math.radians(a)), 0.15) for a in range(160, 19, -35)]
        H.P("cabelo", smooth(pts, 4), k, H.face, L + 0.2, rimw=0.0)   # forma côncava: sem brilho (o recorte só aceita forma convexa)


def bigode(H, cor):
    k = _cor(H, "bigode", cor); mx = VIEWX["front" if H.view == "front" else "q"]["mx"]
    H.P("bigode", smooth([(mx - 0.07, -0.06), (mx, -0.045), (mx + 0.07, -0.06), (mx + 0.05, -0.08), (mx, -0.07), (mx - 0.05, -0.08)], 5), k, H.face, _lay(H, "head", 1.0), rimw=0.0)


def barba(H, cor):
    k = _cor(H, "barba", cor)
    pts = [(0.2 * math.cos(math.radians(a)), 0.2 * math.sin(math.radians(a))) for a in range(200, 341, 10)]
    pts += [(0.15 * math.cos(math.radians(a)), -0.08 + 0.02 * math.sin(math.radians(a))) for a in range(340, 199, -20)]
    H.P("barba", smooth(pts, 4), k, H.face, _lay(H, "head", 0.3), rimw=0.0)


def oculos(H, cor="#e8e2d4"):
    k = _cor(H, "oculos", cor)
    ex = VIEWX["front" if H.view == "front" else "q"]["eyes"]
    for i, x in enumerate(ex):
        aro = [(x + 0.058 * math.cos(math.radians(a)), 0.012 + 0.046 * math.sin(math.radians(a))) for a in range(0, 361, 12)]
        mesh_pts(f"{H.name}_oc{i}", stroke(aro, 0.006), H.M[k], H.face, -(_lay(H, "head", 1.2)) * LAYER)
    mesh_pts(f"{H.name}_ocp", stroke([(ex[0] + 0.058, 0.02), (ex[1] - 0.058, 0.02)], 0.005), H.M[k], H.face, -(_lay(H, "head", 1.2)) * LAYER)


def quepe(H, cor="#1a2340", aba="#0c1020", distintivo="#e8c76a"):
    L = _lay(H, "head", 0.4)
    H.P("quepe", rrect(-0.2, 0.13, 0.2, 0.3, 0.05, 5), _cor(H, "quepe", cor), H.face, L, rimw=0.008)
    H.P("quepe_aba", smooth([(-0.23, 0.12), (0.26, 0.12), (0.24, 0.16), (-0.21, 0.16)], 3), _cor(H, "quepe_aba", aba), H.face, L + 0.2, rimw=0.0)
    H.P("quepe_dist", circle(0.0, 0.22, 0.035, 20), _cor(H, "quepe_dist", distintivo), H.face, L + 0.3, outline=False, rim=False)


def capacete(H, cor="#f2f2ee"):
    L = _lay(H, "head", 0.4)
    pts = [(0.215 * math.cos(math.radians(a)), 0.1 + 0.2 * math.sin(math.radians(a)) ** 0.7) for a in range(0, 181, 6)]
    H.P("capacete", pts, _cor(H, "capacete", cor), H.face, L, rimw=0.01)
    H.P("capacete_aba", rrect(-0.26, 0.08, 0.26, 0.125, 0.02, 3), _cor(H, "capacete_aba", _esc(cor, 0.12)), H.face, L + 0.2, rimw=0.0)
    H.P("capacete_crista", rrect(-0.025, 0.12, 0.025, 0.3, 0.012, 2), _cor(H, "capacete_crista", _esc(cor, 0.08)), H.face, L + 0.1, rimw=0.0)


def bone(H, cor="#c0603a"):
    L = _lay(H, "head", 0.4)
    pts = [(0.21 * math.cos(math.radians(a)), 0.1 + 0.15 * math.sin(math.radians(a))) for a in range(0, 181, 12)]
    H.P("bone", smooth(pts, 3), _cor(H, "bone", cor), H.face, L, rimw=0.008)
    H.P("bone_aba", smooth([(0.05, 0.085), (0.32, 0.075), (0.3, 0.115), (0.05, 0.125)], 3), _cor(H, "bone_aba", _esc(cor, 0.2)), H.face, L + 0.2, rimw=0.0)


def viseira(H, cor="#2f8a5a"):
    H.P("viseira", smooth([(-0.22, 0.12), (0.22, 0.12), (0.26, 0.16), (-0.26, 0.16)], 3), _cor(H, "viseira", cor), H.face, _lay(H, "head", 0.4), rimw=0.0)
    H.P("viseira_f", rrect(-0.2, 0.15, 0.2, 0.19, 0.02, 3), _cor(H, "viseira_f", _esc(cor, 0.3)), H.face, _lay(H, "head", 0.35), rimw=0.0)


# ---------------------------------------------------------------- roupas (presas no tronco)
def gravata(H, cor="#8f1f27", camisa="#f4f1ea"):
    if H.view == "back":
        return
    corpo = _corpo(H); y = -(_lay(H, "torso", 0.25)) * LAYER
    cx = 0.0 if H.view == "front" else 0.04
    mesh_pts(f"{H.name}_camisa", clip([(cx - 0.06, 0.48), (cx + 0.06, 0.48), (cx, 0.33)], corpo), H._mat("camisa", camisa), H.j["torso"], y)
    mesh_pts(f"{H.name}_gravata", [(cx - 0.014, 0.455), (cx + 0.014, 0.455), (cx + 0.022, 0.36), (cx, 0.335), (cx - 0.022, 0.36)],
             H._mat("gravata", cor), H.j["torso"], y - 0.02 * LAYER)


def toga(H, cor="#14141a", gola="#f4f1ea"):
    """toga de juiz: painel preto do peito até abaixo do joelho, por cima das pernas; gola branca"""
    k = _cor(H, "toga", cor)
    H.P("toga", smooth([(-0.19, 0.47), (0.19, 0.47), (0.2, 0.2), (0.215, -0.42), (-0.215, -0.42), (-0.2, 0.2)], 4), k, H.j["torso"], _lay(H, "torso", 0.15),
        shade=0.025, rimw=0.012)
    for s_ in (-1, 1):                                            # a abertura da toga na frente (duas faixas de cetim)
        H.P(f"toga_cetim{s_}", rrect(s_ * 0.03 - 0.022, -0.42, s_ * 0.03 + 0.022, 0.4, 0.01, 2), _cor(H, "toga_cetim", "#2a2a36"), H.j["torso"],
            _lay(H, "torso", 0.3), rimw=0.0)
    if H.view != "back":
        H.P("toga_gola", smooth([(-0.07, 0.48), (0.07, 0.48), (0.05, 0.39), (0.0, 0.36), (-0.05, 0.39)], 4), _cor(H, "toga_gola", gola), H.j["torso"],
            _lay(H, "torso", 0.4), rimw=0.0)


def colete(H, cor):
    corpo = _corpo(H); k = _cor(H, "colete", cor)
    pts = clip([(-0.2, 0.42), (-0.06, 0.42), (0.0, 0.25), (0.06, 0.42), (0.2, 0.42), (0.2, -0.06), (-0.2, -0.06)], corpo)
    if len(pts) >= 3:
        mesh_pts(f"{H.name}_colete", pts, H.M[k], H.j["torso"], -(_lay(H, "torso", 0.3)) * LAYER)


def macacao(H, cor):
    corpo = _corpo(H); k = _cor(H, "macacao", cor)
    pts = clip([(-0.12, 0.32), (0.12, 0.32), (0.14, -0.06), (-0.14, -0.06)], corpo)
    if len(pts) >= 3:
        mesh_pts(f"{H.name}_peito", pts, H.M[k], H.j["torso"], -(_lay(H, "torso", 0.3)) * LAYER)
    for s in (-1, 1):
        mesh_pts(f"{H.name}_alca{s}", stroke([(s * 0.1, 0.32), (s * 0.13, 0.47)], 0.014), H.M[k], H.j["torso"], -(_lay(H, "torso", 0.3)) * LAYER)


def faixa_estrangeira(H, cor="#6a2a8a", borda="#e8c76a"):
    """faixa diplomática (de outro país): diagonal ao contrário da do presidente"""
    corpo = _corpo(H); bw = H.prop["body_w"]
    def banda(a, b, w):
        dx, dz = b[0] - a[0], b[1] - a[1]; n = math.hypot(dx, dz); nx, nz = -dz / n * w, dx / n * w
        return [(a[0] + nx, a[1] + nz), (b[0] + nx, b[1] + nz), (b[0] - nx, b[1] - nz), (a[0] - nx, a[1] - nz)]
    a, b = (0.2 * bw, 0.5), (-0.2 * bw, -0.02)
    for i, (w, c) in enumerate(((0.045, borda), (0.034, cor))):
        pts = clip(banda(a, b, w), corpo)
        if len(pts) >= 3:
            mesh_pts(f"{H.name}_fe{i}", pts, H._mat(f"fe{i}", c), H.j["torso"], -(_lay(H, "torso", 0.45 + 0.02 * i)) * LAYER)


# ---------------------------------------------------------------- detalhes de figurino e de rosto (o que dá vida)
def _y(H, parte, d):
    return -(_lay(H, parte, d)) * LAYER


def lapelas(H, cor):
    """lapelas do paletó em V, do colarinho até o primeiro botão (frente e 3/4)"""
    if H.view == "back":
        return
    k = _cor(H, "lapela", cor); cx = 0.0 if H.view == "front" else 0.04; bw = H.prop["body_w"]
    for s_ in (-1, 1):
        pts = [(cx + s_ * 0.055, 0.47), (cx + s_ * 0.115 * bw, 0.44), (cx + s_ * 0.075 * bw, 0.33), (cx + s_ * 0.02, 0.2), (cx + s_ * 0.03, 0.33)]
        mesh_pts(f"{H.name}_lap{s_}", pts if s_ > 0 else pts[::-1], H.M[k], H.j["torso"], _y(H, "torso", 0.32))


def botoes(H, cor="#1a1a20", zs=(0.16, 0.08)):
    if H.view == "back":
        return
    k = _cor(H, "botao", cor); cx = 0.012 if H.view == "front" else 0.05
    for i, z in enumerate(zs):
        mesh_pts(f"{H.name}_bt{i}", circle(cx, z, 0.011, 12), H.M[k], H.j["torso"], _y(H, "torso", 0.5))


def lenco_bolso(H, cor="#f4f1ea"):
    if H.view == "back":
        return
    k = _cor(H, "lenco", cor); bw = H.prop["body_w"]; x = 0.09 * bw if H.view == "front" else 0.1
    mesh_pts(f"{H.name}_lenco", [(x - 0.03, 0.33), (x + 0.03, 0.33), (x + 0.02, 0.36), (x, 0.345), (x - 0.02, 0.365)], H.M[k], H.j["torso"], _y(H, "torso", 0.5))


def broche(H, cor="#1f9d55", cor2="#f2c94c"):
    if H.view == "back":
        return
    bw = H.prop["body_w"]; x = -0.095 * bw if H.view == "front" else -0.02
    mesh_pts(f"{H.name}_br1", circle(x, 0.36, 0.016, 14), H._mat("broche1", cor2), H.j["torso"], _y(H, "torso", 0.5))
    mesh_pts(f"{H.name}_br2", circle(x, 0.36, 0.01, 14), H._mat("broche2", cor), H.j["torso"], _y(H, "torso", 0.6))


def cinto(H, cor="#2a2018", fivela="#d9c27a"):
    bw = H.prop["body_w"]
    mesh_pts(f"{H.name}_cinto", rrect(-0.17 * bw, -0.07, 0.17 * bw, -0.035, 0.008, 2), H._mat("cinto", cor), H.j["torso"], _y(H, "torso", 0.5))
    if H.view != "back":
        cx = 0.0 if H.view == "front" else 0.05
        mesh_pts(f"{H.name}_fivela", rrect(cx - 0.025, -0.075, cx + 0.025, -0.03, 0.006, 2), H._mat("fivela", fivela), H.j["torso"], _y(H, "torso", 0.6))


def distintivo(H, cor="#e8c76a"):
    if H.view == "back":
        return
    bw = H.prop["body_w"]; x = -0.09 * bw if H.view == "front" else 0.0
    pts = [(x + 0.03 * math.cos(math.radians(90 + 72 * k + (36 if j else 0))) * (1 if not j else 0.45),
            0.33 + 0.03 * math.sin(math.radians(90 + 72 * k + (36 if j else 0))) * (1 if not j else 0.45)) for k in range(5) for j in (0, 1)]
    mesh_pts(f"{H.name}_dist", pts, H._mat("dist", cor), H.j["torso"], _y(H, "torso", 0.6))


def dragonas(H, cor="#e8c76a"):
    for s_ in ("F", "B"):
        mesh_pts(f"{H.name}_drag{s_}", rrect(-0.05, -0.012, 0.05, 0.012, 0.006, 2), H._mat("drag", cor), H.j["sh" + s_], _y(H, "armF" if s_ == "F" else "armB", 0.3))


def radio(H):
    if H.view == "back":
        return
    bw = H.prop["body_w"]; x = 0.1 * bw if H.view == "front" else 0.1
    mesh_pts(f"{H.name}_radio", rrect(x - 0.022, 0.3, x + 0.022, 0.38, 0.006, 2), H._mat("radio", "#101318"), H.j["torso"], _y(H, "torso", 0.6))
    mesh_pts(f"{H.name}_radio_l", circle(x, 0.365, 0.006, 8), H._mat("radio_l", "#7cf08a"), H.j["torso"], _y(H, "torso", 0.7))
    mesh_pts(f"{H.name}_radio_a", rrect(x + 0.008, 0.38, x + 0.014, 0.43, 0.002, 1), H._mat("radio", "#101318"), H.j["torso"], _y(H, "torso", 0.6))


def relogio(H, cor="#e8c76a"):
    mesh_pts(f"{H.name}_relogio", rrect(-0.032, 0.0, 0.032, 0.03, 0.01, 2), H._mat("relogio", cor), H.j["wrF"], _y(H, "armF", 0.6))


def rugas(H, cor="#3a3a46"):
    for i, z in enumerate((0.14, 0.165)):
        mesh_pts(f"{H.name}_ruga{i}", stroke([(-0.07, z), (-0.02, z + 0.006), (0.03, z + 0.004), (0.07, z - 0.004)], 0.004), H._mat("ruga", cor), H.face, _y(H, "head", 1.0))


def brincos(H, cor="#e8c76a"):
    for s_ in (-1, 1):
        if H.view == "q" and s_ > 0:
            continue
        mesh_pts(f"{H.name}_brinco{s_}", circle(s_ * 0.2, -0.07, 0.018, 12), H._mat("brinco", cor), H.face, _y(H, "head", 1.0))


def colar_perolas(H):
    if H.view == "back":
        return
    for k in range(9):
        a = math.radians(200 + 140 * k / 8)
        mesh_pts(f"{H.name}_perola{k}", circle(0.07 * math.cos(a), 0.47 + 0.05 * math.sin(a), 0.008, 10), H._mat("perola", "#f6f1e6"), H.j["torso"], _y(H, "torso", 0.7))


def lapis_orelha(H):
    mesh_pts(f"{H.name}_lapis", rrect(0.15, 0.02, 0.29, 0.042, 0.006, 2), H._mat("lapis", "#f2c94c"), H.face, _y(H, "head", -0.4))
    mesh_pts(f"{H.name}_lapis_p", [(0.29, 0.02), (0.32, 0.031), (0.29, 0.042)], H._mat("lapis_p", "#e8d2a6"), H.face, _y(H, "head", -0.45))


def ligas_manga(H, cor="#8f1f27"):
    for s_ in ("F", "B"):
        mesh_pts(f"{H.name}_liga{s_}", rrect(-0.045, -0.012, 0.045, 0.012, 0.004, 1), H._mat("liga", cor), H.j["el" + s_], _y(H, "armF" if s_ == "F" else "armB", 0.3))


def medalha(H):
    if H.view == "back":
        return
    bw = H.prop["body_w"]; x = 0.1 * bw if H.view == "front" else 0.08
    mesh_pts(f"{H.name}_fita", [(x - 0.018, 0.36), (x + 0.018, 0.36), (x + 0.012, 0.31), (x - 0.012, 0.31)], H._mat("fita", "#6a2a8a"), H.j["torso"], _y(H, "torso", 0.6))
    mesh_pts(f"{H.name}_med", circle(x, 0.295, 0.02, 14), H._mat("med", "#e8c76a"), H.j["torso"], _y(H, "torso", 0.7))


def toalha_ombro(H):
    mesh_pts(f"{H.name}_toalha", rrect(-0.06, -0.12, 0.06, 0.04, 0.02, 3), H._mat("toalha", "#f0ece0"), H.j["shF"], _y(H, "armF", 0.4))


def mao(H, tipo):
    """objeto na mão da frente (preso ao punho: o eixo -z é o sentido do braço, para baixo)"""
    w = H.j["wrF"]; y = _y(H, "armF", 0.8)
    def m(k, cor):
        return H._mat(k, cor)
    if tipo == "maleta":
        mesh_pts(f"{H.name}_mal_alca", stroke([(-0.04, -0.05), (-0.04, -0.02), (0.04, -0.02), (0.04, -0.05)], 0.008), m("mal_e", "#2a1a10"), w, y)
        mesh_pts(f"{H.name}_mal", rrect(-0.16, -0.3, 0.16, -0.05, 0.02, 3), m("mal", "#5a3a22"), w, y - 0.001)
        mesh_pts(f"{H.name}_mal_f", rrect(-0.025, -0.1, 0.025, -0.07, 0.005, 2), m("mal_f", "#e8c76a"), w, y - 0.002)
    elif tipo == "prancheta":
        mesh_pts(f"{H.name}_pr", rrect(-0.1, -0.3, 0.1, -0.02, 0.012, 2), m("pr", "#8a5a3a"), w, y)
        mesh_pts(f"{H.name}_pr_p", rrect(-0.085, -0.285, 0.085, -0.05, 0.006, 2), m("pr_p", "#f7f3ea"), w, y - 0.001)
        mesh_pts(f"{H.name}_pr_c", rrect(-0.035, -0.06, 0.035, -0.03, 0.006, 2), m("pr_c", "#b8bcc4"), w, y - 0.002)
        for k in range(5):
            mesh_pts(f"{H.name}_pr_l{k}", rrect(-0.065, -0.1 - k * 0.035, 0.05, -0.094 - k * 0.035, 0.002, 1), m("pr_l", "#9aa3b0"), w, y - 0.002)
    elif tipo == "rolo":
        mesh_pts(f"{H.name}_rolo", rrect(-0.03, -0.32, 0.03, 0.05, 0.03, 4), m("rolo", "#cfe2f2"), w, y)
        mesh_pts(f"{H.name}_rolo_f", rrect(-0.032, -0.12, 0.032, -0.1, 0.004, 1), m("rolo_f", "#c8323e"), w, y - 0.001)
    elif tipo == "calculadora":
        mesh_pts(f"{H.name}_calc", rrect(-0.06, -0.17, 0.06, -0.02, 0.012, 2), m("calc", "#2a2d34"), w, y)
        mesh_pts(f"{H.name}_calc_v", rrect(-0.045, -0.06, 0.045, -0.032, 0.004, 1), m("calc_v", "#a8e0b0"), w, y - 0.001)
        for i in range(3):
            for j in range(3):
                mesh_pts(f"{H.name}_calc_b{i}{j}", rrect(-0.042 + i * 0.03, -0.155 + j * 0.03, -0.022 + i * 0.03, -0.138 + j * 0.03, 0.003, 1), m("calc_b", "#e6e8ee"), w, y - 0.001)
    elif tipo == "pasta":
        mesh_pts(f"{H.name}_pasta", rrect(-0.13, -0.3, 0.13, -0.03, 0.01, 2), m("pasta", "#c9a26a"), w, y)
        mesh_pts(f"{H.name}_pasta_e", rrect(-0.13, -0.08, 0.02, -0.03, 0.01, 2), m("pasta_e", "#b08a56"), w, y - 0.001)
        mesh_pts(f"{H.name}_pasta_s", circle(0.06, -0.2, 0.035, 18), m("pasta_s", "#b8323a"), w, y - 0.001)
    elif tipo == "martelo":
        mesh_pts(f"{H.name}_mt_cabo", rrect(-0.012, -0.22, 0.012, 0.02, 0.01, 2), m("mt_cabo", "#8a5a34"), w, y)
        mesh_pts(f"{H.name}_mt_cab", rrect(-0.07, -0.27, 0.07, -0.2, 0.015, 3), m("mt_cab", "#6a4228"), w, y - 0.001)
        mesh_pts(f"{H.name}_mt_cinta", rrect(-0.072, -0.245, 0.072, -0.228, 0.004, 1), m("mt_cinta", "#d8c27e"), w, y - 0.002)
    elif tipo == "microfone":
        mesh_pts(f"{H.name}_mic", rrect(-0.014, -0.18, 0.014, 0.02, 0.01, 2), m("mic", "#1a1c22"), w, y)
        mesh_pts(f"{H.name}_mic_c", circle(0.0, -0.2, 0.035, 18), m("mic_c", "#3a3d46"), w, y - 0.001)
    elif tipo == "envelope":
        mesh_pts(f"{H.name}_env", rrect(-0.1, -0.16, 0.1, -0.02, 0.008, 2), m("env", "#f4efe6"), w, y)
        mesh_pts(f"{H.name}_env_a", [(-0.1, -0.02), (0.0, -0.09), (0.1, -0.02)], m("env_a", "#d8d0c0"), w, y - 0.001)


# ---------------------------------------------------------------- o elenco
def juiz(name, view="front", rim="#ffe4d0", objeto="martelo"):
    H = _base(name, view, "#1c1c24", "#16161c", rim, prop=dict(body_w=1.04, head=0.84, leg=0.82))
    toga(H); cabelo(H, "laterais", "#e8e4dc"); oculos(H); rugas(H)
    if objeto:
        mao(H, objeto)
    return H


def juiza(name, view="front", rim="#ffe4d0", objeto=None):
    H = _base(name, view, "#1c1c24", "#16161c", rim, prop=dict(body_w=0.94, head=0.8, leg=0.86, neck_len=0.65))
    toga(H); cabelo(H, "coque", "#5a3a2a"); brincos(H); colar_perolas(H)
    if objeto:
        mao(H, objeto)
    return H


def deputado(name, view="front", rim="#ffc890", objeto="pasta"):
    H = _base(name, view, "#5c6474", "#4a5262", rim, prop=dict(body_w=1.22, head=0.86, leg=0.8, neck_len=0.45))
    lapelas(H, "#454c5a"); gravata(H, "#2a5a8a"); botoes(H); broche(H); lenco_bolso(H, "#f2c94c")
    cabelo(H, "penteado", "#a8a8b0"); bigode(H, "#a8a8b0")
    if objeto:
        mao(H, objeto)
    return H


def empreiteiro(name, view="front", rim="#ffc890", objeto="rolo"):
    H = _base(name, view, "#7a5236", "#3a3a44", rim, prop=dict(body_w=1.32, head=0.88, leg=0.8, neck_len=0.4, arm=1.2))
    lapelas(H, "#5a3a24"); gravata(H, "#1f4a3a", "#f0ece0"); botoes(H, "#3a2416"); capacete(H); bigode(H, "#2a2a30"); relogio(H)
    if objeto:
        mao(H, objeto)
    return H


def policial(name, view="front", rim="#d8e4ff", objeto=None):
    H = _base(name, view, "#1e2a48", "#141c34", rim, prop=dict(body_w=1.12, head=0.8, leg=0.9))
    colete(H, "#2a3656"); distintivo(H); radio(H); dragonas(H); cinto(H, "#0c1020", "#c8ccd6"); quepe(H)
    if objeto:
        mao(H, objeto)
    return H


def fiscal(name, view="front", rim="#d8f7ff", objeto="prancheta"):
    H = _base(name, view, "#8ab4d0", "#2a3646", rim, prop=dict(body_w=0.98, head=0.8, leg=0.86))
    quepe(H, "#2a3646", "#1a2230", "#d8f7ff"); cinto(H, "#1a2230", "#c8ccd6"); dragonas(H, "#2a3646")
    if objeto:
        mao(H, objeto)
    return H


def diplomata(name, view="front", rim="#ffc890", objeto="maleta"):
    H = _base(name, view, "#24243a", "#1c1c2e", rim, prop=dict(body_w=1.02, head=0.8, leg=0.92, neck_len=0.6))
    lapelas(H, "#18182a"); gravata(H, "#5a1a2a"); faixa_estrangeira(H); medalha(H); lenco_bolso(H)
    barba(H, "#3a3a44"); cabelo(H, "curto", "#3a3a44")
    if objeto:
        mao(H, objeto)
    return H


def trabalhador(name, view="front", rim="#ffd0a0", objeto=None):
    H = _base(name, view, "#c8bca4", "#3a5a8a", rim, prop=dict(body_w=1.06, head=0.8, leg=0.85, arm=1.2))
    macacao(H, "#3a5a8a"); bone(H); cinto(H, "#5a3a22", "#c8ccd6")
    if objeto:
        mao(H, objeto)
    return H


def contador(name, view="front", rim="#ffd9a8", objeto="calculadora"):
    H = _base(name, view, "#e8e2d4", "#3a3a44", rim, prop=dict(body_w=0.9, head=0.88, leg=0.78, neck_len=0.5))
    colete(H, "#4a3a2e"); gravata(H, "#2a2a30"); viseira(H); oculos(H, "#f4f1ea"); ligas_manga(H); lapis_orelha(H)
    if objeto:
        mao(H, objeto)
    return H


ELENCO = [("presidente", None), ("juiz", juiz), ("juiza", juiza), ("deputado", deputado), ("empreiteiro", empreiteiro),
          ("policial", policial), ("fiscal", fiscal), ("diplomata", diplomata), ("trabalhador", trabalhador), ("contador", contador)]
