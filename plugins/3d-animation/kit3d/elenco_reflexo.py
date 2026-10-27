"""Elenco do vídeo "E se o seu cérebro fosse 10 vezes mais rápido?" (mesmo boneco, mesmo traço do elenco do presidente).
"Você" aparece em três figurinos (em casa, goleiro e velocista), sempre com a cabeça lisa do herói; os outros têm cabelo e
acessório próprios. O menino pegador de bolas é o mesmo boneco com proporção de criança (cabeça grande, perna curta) e vai
com escala de mundo ~0,72 (ver ESCALA).
Uso: H = elenco_reflexo.goleiro("voce_goleiro", "q", rim="#ffe4d0")"""
import math
from heroi import Heroi, LAYER
from puppet2d import smooth, stroke, circle
from char2d import rrect, mesh_pts
import elenco as E
from elenco import _base, _esc, _lay, _y, _cor, cabelo, bone, viseira, cinto

ESCALA = {"menino": 0.72}


def _gola(H, cor, tipo="v"):
    """gola da camisa (V ou redonda): faixa de outra cor no pescoço"""
    if H.view == "back":
        return
    cx = 0.0 if H.view == "front" else 0.04
    pts = [(cx - 0.075, 0.485), (cx + 0.075, 0.485), (cx, 0.37)] if tipo == "v" else [(cx - 0.07, 0.485), (cx + 0.07, 0.485), (cx + 0.05, 0.44), (cx - 0.05, 0.44)]
    mesh_pts(f"{H.name}_gola", pts, H._mat("gola", cor), H.j["torso"], _y(H, "torso", 0.35))


def _numero(H, digito, cor="#f4f1ea", z=0.2):
    """número no peito, riscado como polilinha (1, 7 e 9)"""
    if H.view == "back":
        return
    cx = 0.0 if H.view == "front" else 0.04
    formas = {"1": [[(-0.025, 0.05), (0.012, 0.09), (0.012, -0.09)]],
              "7": [[(-0.035, 0.09), (0.035, 0.09), (-0.01, -0.09)]],
              "9": [[(0.03 * math.cos(math.radians(t)), 0.05 + 0.04 * math.sin(math.radians(t))) for t in range(0, 361, 30)], [(0.03, 0.05), (0.03, 0.0), (0.02, -0.06), (-0.01, -0.09)]]}[digito]
    for i, f in enumerate(formas):
        mesh_pts(f"{H.name}_num{i}", stroke([(cx + x, z + y) for x, y in f], 0.011), H._mat("numero", cor), H.j["torso"], _y(H, "torso", 0.6))


def luvas(H, cor="#f4f1ea", punho="#e0602a"):
    """luvas grandes nas duas mãos (por cima da mão pele): palma redonda, dedos e punho colorido"""
    for s in ("F", "B"):
        w = H.j["wr" + s]; y = _y(H, "armF" if s == "F" else "armB", 0.9)
        mesh_pts(f"{H.name}_luva{s}", [(x * 1.0, z) for x, z in circle(0.0, -0.045, 0.062, 28)], H._mat("luva", cor), w, y)
        for i, dx in enumerate((-0.036, -0.012, 0.012, 0.036)):
            mesh_pts(f"{H.name}_dedo{s}{i}", stroke([(dx, -0.07), (dx, -0.105)], 0.016), H._mat("luva", cor), w, y)
        mesh_pts(f"{H.name}_punho{s}", rrect(-0.05, 0.012, 0.05, 0.05, 0.008, 2), H._mat("luva_p", punho), w, y - 0.0005)   # cobre a ponta da manga: sem vão


def faixa_cabeca(H, cor="#f4f1ea"):
    L = _lay(H, "head", 0.45)
    H.P("faixa_cab", rrect(-0.214, 0.075, 0.214, 0.118, 0.012, 3), _cor(H, "faixa_cab", cor), H.face, L, rimw=0.0)


def braçadeira(H, cor="#f2c94c"):
    mesh_pts(f"{H.name}_bracad", rrect(-0.045, -0.02, 0.045, 0.03, 0.006, 2), H._mat("bracad", cor), H.j["shF"], _y(H, "armF", 0.5))


def cachecol(H, cor="#f2c94c", listra="#1f9d55"):
    if H.view == "back":
        return
    cx = 0.0 if H.view == "front" else 0.04
    mesh_pts(f"{H.name}_cc", rrect(cx - 0.11, 0.41, cx + 0.11, 0.49, 0.03, 4), H._mat("cachecol", cor), H.j["torso"], _y(H, "torso", 0.55))
    mesh_pts(f"{H.name}_cc_l", stroke([(cx - 0.1, 0.45), (cx + 0.1, 0.45)], 0.012), H._mat("cachecol_l", listra), H.j["torso"], _y(H, "torso", 0.6))
    mesh_pts(f"{H.name}_cc_p", rrect(cx + 0.04, 0.3, cx + 0.085, 0.42, 0.008, 2), H._mat("cachecol", cor), H.j["torso"], _y(H, "torso", 0.57))


def colete_cor(H, cor, listras="#f4f1ea"):
    """colete refletivo do menino: peito todo e duas tiras claras"""
    E.colete(H, cor)
    if H.view != "back":
        cx = 0.0 if H.view == "front" else 0.04
        for i, dx in enumerate((-0.07, 0.07)):
            mesh_pts(f"{H.name}_tira{i}", rrect(cx + dx - 0.012, -0.05, cx + dx + 0.012, 0.4, 0.004, 1), H._mat("tira", listras), H.j["torso"], _y(H, "torso", 0.45))


# ---------------------------------------------------------------- "você"
def voce_casa(name, view="front", rim="#ffe4d0", objeto=None):
    """o herói de sempre (cabeça lisa, jaqueta) em casa"""
    H = Heroi(name, view)
    return H


def goleiro(name, view="front", rim="#ffe4d0", objeto=None):
    H = _base(name, view, "#e0602a", "#1c2230", rim, prop=dict(body_w=1.06, head=0.84, leg=0.92, arm=1.05))
    _gola(H, "#f4f1ea"); _numero(H, "1"); luvas(H)
    return H


def velocista(name, view="front", rim="#d8f7ff", objeto=None):
    H = _base(name, view, "#1f8a5a", "#1a1c22", rim, prop=dict(body_w=0.94, head=0.82, leg=0.98, arm=1.05))
    _gola(H, "#f4f1ea", "r"); _numero(H, "7"); faixa_cabeca(H)
    return H


# ---------------------------------------------------------------- os outros
def atacante(name, view="front", rim="#ffe4d0", objeto=None):
    H = _base(name, view, "#2a5acb", "#e8e8ee", rim, prop=dict(body_w=1.04, head=0.82, leg=0.94))
    _gola(H, "#f4f1ea"); _numero(H, "9"); braçadeira(H); cabelo(H, "curto", "#2a1a10")
    return H


def menino(name, view="front", rim="#ffe4d0", objeto=None):
    """pegador de bolas: proporção de criança (a escala de mundo vem de ESCALA)"""
    H = _base(name, view, "#f4f1ea", "#2a3a5a", rim, prop=dict(body_w=0.9, head=1.06, leg=0.72, arm=1.0, arm_len=0.86, hand=0.92, neck_len=0.5))   # braço curto e grosso: o fino (arm 0,86) soltava a mão
    colete_cor(H, "#7ac943"); bone(H, "#2a5acb")
    return H


def torcedor(name, view="front", rim="#ffe4d0", objeto=None):
    H = _base(name, view, "#1f9d55", "#2a3a5a", rim, prop=dict(body_w=1.12, head=0.84, leg=0.86, neck_len=0.5))
    cachecol(H); viseira(H, "#f2c94c"); E.barba(H, "#3a2a20")
    return H


def pessoa(name, view="front", rim="#ffe4d0", objeto=None):
    """a 'pessoa normal' do vídeo: jaqueta cinza-azulada, calça escura, cabelo curto (nada que a destaque)"""
    H = _base(name, view, "#6a7f9a", "#3a3a44", rim, prop=dict(body_w=1.04, head=0.82, leg=0.92))
    cabelo(H, "curto", "#4a3a2a"); _gola(H, "#aab6c8", "r")
    return H


ELENCO = [("voce_casa", voce_casa), ("goleiro", goleiro), ("velocista", velocista), ("atacante", atacante), ("menino", menino), ("torcedor", torcedor)]
