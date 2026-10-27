"""Roupa de presidiário para o herói: camisa listrada (listras horizontais recortadas na silhueta da jaqueta),
mangas e calça lisas, e um X riscado à mão no peito (sem número, para não remeter a ninguém).
Usar: H = uniforme.heroi_preso("heroi", "front", rim=...) (já vem vestido)."""
from heroi import clip, LAYER
from puppet2d import smooth, stroke
from char2d import rrect, mesh_pts
from lib import empty
import math
from puppet2d import flatmat

CLARA, ESCURA = "#e6e1d6", "#33404c"
PAL = dict(hoodie=CLARA, dark="#b9b3a6", hoodie_sh_ink="#8f8a80", pants=ESCURA)
TONS = {"hoodie": (CLARA, "#c4beb2"), "dark": ("#b9b3a6", "#9c968a"), "pants": (ESCURA, "#263039")}

CORPO = {
    "front": [(-0.135, -0.055), (0.135, -0.055), (0.168, 0.02), (0.172, 0.14), (0.176, 0.37), (0.158, 0.44), (0.1, 0.468),
              (0.0, 0.474), (-0.1, 0.468), (-0.158, 0.44), (-0.176, 0.37), (-0.172, 0.14), (-0.168, 0.02)],
    "q": [(-0.1, -0.055), (0.125, -0.055), (0.15, 0.02), (0.152, 0.14), (0.142, 0.33), (0.105, 0.435), (0.02, 0.468),
          (-0.075, 0.455), (-0.118, 0.38), (-0.13, 0.14), (-0.125, 0.02)],
}


def vestir(H, listras=7, marca=True):
    """listras escuras por cima do tronco e o X no peito (camadas logo à frente da jaqueta)"""
    v = "front" if H.view in ("front", "back") else "q"
    bw = H.prop["body_w"]
    corpo = smooth([(x * bw, z) for x, z in CORPO[v]], 6)
    lay = H._layers()["torso"]
    y = -(lay + 0.25) * LAYER
    m = H._mat("listra", ESCURA)
    passo = (0.474 + 0.055) / listras
    for i in range(listras):
        z0 = -0.055 + i * passo + passo * 0.52
        faixa = [(-0.3, z0), (0.3, z0), (0.3, z0 + passo * 0.42), (-0.3, z0 + passo * 0.42)]
        pts = clip(faixa, corpo)
        if len(pts) >= 3:
            mesh_pts(f"{H.name}_listra{i}", pts, m, H.j["torso"], y)
    if marca and H.view != "back":
        cx = -0.07 * bw if v == "front" else 0.03
        yy = -(lay + 0.32) * LAYER
        mesh_pts(f"{H.name}_placa", rrect(cx - 0.05, 0.27, cx + 0.05, 0.37, 0.008, 3), H._mat("placa", "#f4f1ea"), H.j["torso"], yy)
        tinta = H._mat("risco", "#c62f35")
        mesh_pts(f"{H.name}_x1", stroke([(cx - 0.032, 0.29), (cx - 0.004, 0.32), (cx + 0.03, 0.352)], 0.006), tinta, H.j["torso"], yy - 0.02 * LAYER)
        mesh_pts(f"{H.name}_x2", stroke([(cx + 0.03, 0.288), (cx + 0.002, 0.318), (cx - 0.028, 0.35)], 0.006), tinta, H.j["torso"], yy - 0.02 * LAYER)


TERNO, TERNO_SH, TERNO_FAR, CALCA, CALCA_SH = "#22305a", "#1a2547", "#141c38", "#1d2850", "#151d3c"
FAIXA_VERDE, FAIXA_AMARELA = "#1f9d55", "#f2c94c"


def heroi_presidente(name, view="front", rim="#ffd2bc"):
    """o herói de terno azul-marinho, camisa branca e gravata, com a faixa presidencial verde e amarela.
    Devolve (H, faixa): 'faixa' é uma raiz presa ao tronco, para animar a faixa caindo no peito."""
    from heroi import Heroi
    M = {"hoodie_sh": flatmat(f"{name}_hoodie_sh", TERNO_SH), "hoodie_far": flatmat(f"{name}_hoodie_far", TERNO_FAR),
         "pants_sh": flatmat(f"{name}_pants_sh", CALCA_SH), "pants_far": flatmat(f"{name}_pants_far", "#10162e")}
    H = Heroi(name, view, pal=dict(PAL, hoodie=TERNO, dark=TERNO_SH, hoodie_sh_ink="#0e1428", pants=CALCA, rim=rim), mats=M)
    v = "front" if view in ("front", "back") else "q"
    bw = H.prop["body_w"]
    corpo = smooth([(x * bw, z) for x, z in CORPO[v]], 6)
    lay = H._layers()["torso"]
    y = -(lay + 0.25) * LAYER
    if view != "back":
        cx = 0.0 if v == "front" else 0.04
        mesh_pts(f"{name}_camisa", clip([(cx - 0.06, 0.48), (cx + 0.06, 0.48), (cx, 0.33)], corpo), H._mat("camisa", "#f4f1ea"), H.j["torso"], y)
        mesh_pts(f"{name}_gravata", [(cx - 0.014, 0.455), (cx + 0.014, 0.455), (cx + 0.022, 0.36), (cx, 0.335), (cx - 0.022, 0.36)],
                 H._mat("gravata", "#8f1f27"), H.j["torso"], y - 0.02 * LAYER)
    # a faixa: diagonal do ombro direito dele (esquerda da tela) ao quadril oposto, recortada na silhueta do tronco
    faixa = empty(f"{name}_faixa", H.j["torso"], (0, 0, 0))
    yf = -(lay + 0.4) * LAYER
    def banda(a, b, w):
        dx, dz = b[0] - a[0], b[1] - a[1]; n = math.hypot(dx, dz); nx, nz = -dz / n * w, dx / n * w
        return [(a[0] + nx, a[1] + nz), (b[0] + nx, b[1] + nz), (b[0] - nx, b[1] - nz), (a[0] - nx, a[1] - nz)]
    a, b = (-0.2 * bw, 0.5), (0.2 * bw, -0.02)
    for k, (w, cor) in enumerate(((0.05, FAIXA_AMARELA), (0.038, FAIXA_VERDE))):
        pts = clip(banda(a, b, w), corpo)
        if len(pts) >= 3:
            mesh_pts(f"{name}_faixa{k}", pts, H._mat(f"faixa{k}", cor), faixa, yf - k * 0.02 * LAYER)
    return H, faixa


def heroi_preso(name, view="front", rim="#ffd2bc", listras=7, marca=True):
    """o herói com a roupa de presidiário: as cores de sombra das mangas e da calça vêm pré-definidas
    (o Heroi cria algumas com cor fixa se não existirem)"""
    from heroi import Heroi
    M = {"hoodie_sh": flatmat(f"{name}_hoodie_sh", "#c4beb2"), "hoodie_far": flatmat(f"{name}_hoodie_far", "#a9a397"),
         "pants_sh": flatmat(f"{name}_pants_sh", "#263039"), "pants_far": flatmat(f"{name}_pants_far", "#1d252d")}
    H = Heroi(name, view, pal=dict(PAL, rim=rim), mats=M)
    vestir(H, listras, marca)
    return H
