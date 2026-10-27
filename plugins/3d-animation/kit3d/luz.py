"""Luz de cinema em 2D falso: facho volumétrico em camadas (miolo forte, borda que some aos poucos),
poça no chão, poeira que brilha DENTRO do facho e bokeh (partículas grandes e desfocadas perto da câmera)."""
import bpy, math, random
import lib
from lib import key
import cena


def _cone(name, x, y, z0, z1, w_bot, w_top, color, alpha, power=1.2, soft=0.9, rot=0.0):
    o = cena.poly_mesh(name, [(-1, 0, 0), (1, 0, 0), (w_top / w_bot, 0, 1), (-w_top / w_bot, 0, 1)],
                       cena.amat(name + "_m", color, 1.0, alpha, ("shaft", power, soft)))
    o.location = (x, y, z0); o.scale = (w_bot, 1, z1 - z0); o.rotation_euler = (0, math.radians(rot), 0)
    return o


def feixe(name, x, y, z_chao, z_fonte, w_chao, w_fonte, color, forca=1.0, rot=0.0, poca=True, frames=200, poeira=60, seed=1):
    """facho de luz de cima. 3 cones encaixados (largo e fraco, médio, miolo estreito) fazem a borda suave."""
    for i, (k, a, p) in enumerate(((1.35, 0.05, 1.0), (1.0, 0.08, 1.3), (0.55, 0.1, 1.7))):
        _cone(f"{name}_c{i}", x, y - 0.002 * i, z_chao, z_fonte, w_chao * k, w_fonte * (0.6 + 0.4 * k), color, a * forca, p, 0.95, rot)
    if poca:
        for i, (k, a) in enumerate(((1.4, 0.25), (0.8, 0.35))):
            cena.ground_disc(f"{name}_poca{i}", w_chao * k, w_chao * k * 0.32, cena.amat(f"{name}_poca{i}_m", color, 1.0, a * forca, ("radial", 1.6)),
                             (x + math.tan(math.radians(-rot)) * 0.0, y - 0.3, z_chao + 0.003 + 0.0005 * i), n=48)
    if poeira:
        poeira_no_feixe(name, x, y, z_chao, z_fonte, w_chao, w_fonte, color, poeira, frames, seed, rot)


def poeira_no_feixe(name, x, y, z0, z1, w0, w1, color, n, frames, seed=1, rot=0.0, size=(0.012, 0.035)):
    """partículas que só aparecem dentro do facho e brilham mais no miolo; flutuam devagar (nunca param)"""
    rnd = random.Random(seed)
    m_forte = cena.amat(f"{name}_pf_m", color, 2.2, 0.9, ("radial", 1.8))
    m_fraca = cena.amat(f"{name}_pw_m", color, 1.4, 0.45, ("radial", 1.8))
    ang = math.radians(rot)
    for i in range(n):
        u = rnd.random(); z = z0 + (z1 - z0) * (0.05 + 0.9 * u)
        w = w0 + (w1 - w0) * (z - z0) / (z1 - z0)
        v = rnd.uniform(-1, 1) * rnd.uniform(0.3, 1.0)
        xx = x + v * w + math.sin(ang) * (z - z0) * -1.0
        yy = y + rnd.uniform(-0.8, 0.8)
        r = rnd.uniform(*size)
        o = cena.disc(f"{name}_p{i}", r, m_forte if abs(v) < 0.45 else m_fraca, (xx, yy, z), n=12)
        ph = rnd.uniform(0, 6.28); dx = rnd.uniform(-0.05, 0.05); dz = rnd.uniform(-0.04, 0.06)
        f = -30
        while f <= frames + 30:
            o.location = (xx + dx * f / 24.0 + 0.03 * math.sin(ph + f / 40.0), yy, z + dz * f / 24.0 + 0.03 * math.sin(ph * 1.3 + f / 33.0))
            key(o, "location", f, "BEZIER")
            s = r * (0.5 + 0.5 * (0.5 + 0.5 * math.sin(ph * 2.1 + f / 11.0)))          # cintila
            o.scale = (s, 1, s); key(o, "scale", f, "BEZIER")
            f += 12


def bokeh(name, cam_y, x_range, z_range, color, n=14, frames=200, seed=5, dist=(1.2, 3.0), r=(0.03, 0.09), alpha=0.22):
    """partículas grandes e desfocadas bem perto da câmera (dão profundidade ao quadro)"""
    rnd = random.Random(seed)
    m = cena.amat(f"{name}_m", color, 1.5, alpha, ("radial", 1.1))
    for i in range(n):
        x = rnd.uniform(*x_range); z = rnd.uniform(*z_range); y = cam_y + rnd.uniform(*dist)
        o = cena.disc(f"{name}{i}", rnd.uniform(*r), m, (x, y, z), n=24)
        dx, dz = rnd.uniform(-0.04, 0.04), rnd.uniform(-0.02, 0.04)
        o.location = (x, y, z); key(o, "location", -30, "LINEAR")
        o.location = (x + dx * (frames + 60) / 24, y, z + dz * (frames + 60) / 24); key(o, "location", frames + 30, "LINEAR")