"""Objetos de cena (riqueza de detalhe) no mesmo traço chapado: cada lugar ganha 3 a 5 peças que contam onde estamos.
Todos recebem a paleta p e uma posição (x, y, z); o que fica longe deve ir atrás de um véu de névoa (sets4.neblina)."""
import math, random
from lib import empty, key
import cena, props
from char2d import rrect
from puppet2d import circle, stroke

_mix = props._mix


def _esc(p, k=0.3):
    return _mix(p["top"], "#000000", k)


def fios(p, nome, pts, y, cor=None, w=0.012):
    """fios de poste (linha que cai um pouco entre os pontos)"""
    cor = cor or _esc(p, 0.45)
    for i, ((xa, za), (xb, zb)) in enumerate(zip(pts, pts[1:])):
        seg = [(xa + (xb - xa) * u, za + (zb - za) * u - 0.25 * math.sin(math.pi * u)) for u in [k / 12 for k in range(13)]]
        props.poly(f"{nome}{i}", stroke(seg, w), cor, y)


def cartazes(p, nome, x0, z0, y, n=4, seed=1):
    """cartazes velhos colados na parede (retângulos claros e meio apagados, levemente tortos)"""
    rnd = random.Random(seed); cores = [p["aresta"], p["halo"], "#e8e2d6", p["luz"]]
    x = x0
    for i in range(n):
        w = rnd.uniform(0.32, 0.5); h = rnd.uniform(0.45, 0.7); z = z0 + rnd.uniform(-0.12, 0.12)
        r = empty(f"{nome}{i}", None, (x + w / 2, y, z + h / 2)); r.rotation_euler = (0, math.radians(rnd.uniform(-4, 4)), 0)
        cor = _mix(cores[i % 4], p["mid"], 0.55)
        props.poly(f"{nome}{i}_p", rrect(-w / 2, -h / 2, w / 2, h / 2, 0.01, 2), cor, 0.0, r)
        for k in range(3):
            props.poly(f"{nome}{i}_l{k}", cena.rect(-w / 2 + 0.05, h / 2 - 0.12 - k * 0.1, w / 2 - 0.05 - 0.08 * (k % 2), h / 2 - 0.09 - k * 0.1), _mix(cor, "#000000", 0.35), -0.001, r)
        x += w + rnd.uniform(0.05, 0.15)


def sacos(p, nome, x, y, n=3):
    cor = _esc(p, 0.5)
    for i in range(n):
        props.inked(f"{nome}{i}", [(math.cos(a) * 0.2 * (1.1 if math.sin(a) < 0 else 0.9), 0.2 + math.sin(a) * 0.2) for a in [2 * math.pi * k / 18 for k in range(18)]],
                    cor, None, loc=(x + i * 0.28, y - 0.01 * i, 0.0), w=0.0, rim=0.015, rim_color=p["borda"])


def moto(p, nome, x, y, s=1.0, flip=1):
    r = empty(nome, None, (x, y, 0)); r.scale = (s * flip, s, s); cor = _esc(p, 0.4)
    for xx in (-0.55, 0.55):
        props.poly(f"{nome}_r{xx}", circle(xx, 0.3, 0.3, 24), "#05061a", 0.0, r)
        props.poly(f"{nome}_a{xx}", circle(xx, 0.3, 0.14, 18), _mix(p["aresta"], p["top"], 0.5), -0.001, r)
    props.inked(nome + "_c", [(-0.55, 0.32), (-0.1, 0.62), (0.35, 0.62), (0.55, 0.32), (0.2, 0.42)], cor, r, w=0.0, rim=0.02, rim_color=p["borda"])
    props.poly(nome + "_g", stroke([(0.35, 0.62), (0.5, 0.95), (0.62, 0.98)], 0.03), cor, -0.002, r)
    props.poly(nome + "_b", rrect(-0.35, 0.6, 0.15, 0.72, 0.04, 3), "#0d1020", -0.003, r)
    return r


def semaforo(p, nome, x, y, h=3.2, cor_on="#ff3b4a"):
    esc = _esc(p, 0.4)
    props.poly(nome + "_h", cena.rect(x - 0.05, 0, x + 0.05, h), esc, y)
    props.inked(nome + "_cx", rrect(x - 0.16, h - 0.75, x + 0.16, h, 0.05, 3), esc, None, loc=(0, y - 0.01, 0), w=0.0, rim=0.015, rim_color=p["borda"])
    for i, c in enumerate((cor_on, "#3a2a10", "#0e2a1a")):
        props.poly(f"{nome}_l{i}", circle(x, h - 0.15 - i * 0.22, 0.08, 16), c, y - 0.02, strength=1.6 if i == 0 else 1.0)
    cena.disc(nome + "_g", 0.35, cena.amat(nome + "_gm", cor_on, 1.0, 0.35, ("radial", 1.4)), (x, y - 0.03, h - 0.15))


def relogio(p, nome, x, z, y, r=0.22):
    props.inked(nome, circle(x, z, r, 40), "#e8e2d6", None, loc=(0, y, 0), w=0.02, rim=0.0)
    props.poly(nome + "_p1", stroke([(x, z), (x, z + r * 0.65)], 0.012), "#0d1020", y - 0.002)
    props.poly(nome + "_p2", stroke([(x, z), (x + r * 0.45, z - r * 0.2)], 0.012), "#0d1020", y - 0.002)


def calendario(p, nome, x, z, y):
    props.poly(nome, rrect(x - 0.2, z - 0.25, x + 0.2, z + 0.25, 0.01, 2), "#e8e2d6", y)
    props.poly(nome + "_t", cena.rect(x - 0.2, z + 0.15, x + 0.2, z + 0.25), "#c8343c", y - 0.001)
    for i in range(4):
        for j in range(3):
            props.poly(f"{nome}_d{i}{j}", cena.rect(x - 0.16 + i * 0.085, z + 0.05 - j * 0.09, x - 0.1 + i * 0.085, z + 0.1 - j * 0.09), "#9a948a", y - 0.002)


def telefone(p, nome, x, y, z):
    props.inked(nome, rrect(x - 0.13, z, x + 0.13, z + 0.08, 0.02, 3), "#14151c", None, loc=(0, y, 0), w=0.0, rim=0.01, rim_color=p["borda"])
    props.poly(nome + "_f", stroke([(x - 0.12, z + 0.1), (x - 0.06, z + 0.14), (x + 0.06, z + 0.14), (x + 0.12, z + 0.1)], 0.025), "#14151c", y - 0.001)


def papeis(p, nome, x, y, z, n=3):
    for i in range(n):
        props.poly(f"{nome}{i}", rrect(x - 0.12 + i * 0.02, z + i * 0.006, x + 0.12 + i * 0.02, z + 0.012 + i * 0.006, 0.003, 2), "#e8e2d6", y - 0.001 * i)


def quadro_avisos(p, nome, x, z, y, w=0.9, h=0.65):
    props.inked(nome, rrect(x - w / 2, z - h / 2, x + w / 2, z + h / 2, 0.02, 3), "#6e4a2a", None, loc=(0, y, 0), w=0.0, rim=0.02, rim_color=p["borda"])
    rnd = random.Random(5)
    for i in range(5):
        px = x - w / 2 + 0.12 + rnd.uniform(0, w - 0.3); pz = z - h / 2 + 0.1 + rnd.uniform(0, h - 0.3)
        props.poly(f"{nome}_f{i}", rrect(px, pz, px + 0.18, pz + 0.22, 0.005, 2), "#e8e2d6", y - 0.002)


def banco(p, nome, x, y, w=1.2):
    esc = _esc(p, 0.35)
    props.poly(nome + "_t", cena.rect(x - w / 2, 0.42, x + w / 2, 0.48), _mix(esc, p["aresta"], 0.3), y)
    props.poly(nome + "_e", cena.rect(x - w / 2, 0.62, x + w / 2, 0.85), esc, y + 0.05)
    for xx in (x - w / 2 + 0.08, x + w / 2 - 0.12):
        props.poly(f"{nome}_p{xx}", cena.rect(xx, 0, xx + 0.05, 0.45), esc, y + 0.01)


def bandeira(p, nome, x, y, h=2.6):
    props.poly(nome + "_m", cena.rect(x - 0.025, 0, x + 0.025, h), _esc(p, 0.3), y)
    pts = [(x + 0.03, h - 0.05), (x + 0.75, h - 0.1), (x + 0.75, h - 0.55), (x + 0.03, h - 0.5)]
    props.inked(nome + "_b", pts, "#2f8a54", None, loc=(0, y - 0.01, 0), w=0.0, rim=0.015, rim_color=p["borda"])
    props.poly(nome + "_l", [(x + 0.18, h - 0.3), (x + 0.39, h - 0.17), (x + 0.6, h - 0.3), (x + 0.39, h - 0.43)], "#ffd24a", y - 0.02)


def vela(p, nome, x, y, z=0.0, h=1.1, frames=200):
    esc = _esc(p, 0.3)
    props.poly(nome + "_p", cena.rect(x - 0.03, z, x + 0.03, z + h), esc, y)
    props.poly(nome + "_b", rrect(x - 0.15, z, x + 0.15, z + 0.06, 0.02, 2), esc, y)
    props.poly(nome + "_c", cena.rect(x - 0.035, z + h, x + 0.035, z + h + 0.18), "#e8e2d6", y - 0.001)
    ch = empty(nome + "_ch", None, (x, y - 0.002, z + h + 0.2))
    props.poly(nome + "_cf", [(math.sin(a) * 0.035, 0.03 + math.cos(a) * 0.06 if math.cos(a) > 0 else math.cos(a) * 0.03) for a in [2 * math.pi * k / 16 for k in range(16)]], "#ffcf6a", 0.0, ch, strength=2.0)
    cena.disc(nome + "_g", 0.3, cena.amat(nome + "_gm", "#ffb050", 1.0, 0.35, ("radial", 1.5)), (x, y - 0.004, z + h + 0.22))
    rnd = random.Random(int(x * 100) + 7)
    for f in range(-30, frames + 30, 3):                       # a chama tremula
        v = 1 + rnd.uniform(-0.12, 0.12); ch.scale = (1 / v ** 0.5, 1, v); key(ch, "scale", f, "BEZIER")


def cortina(p, nome, x, y, lado=1, h=4.5, w=0.9, cor=None):
    cor = cor or _mix(p["mid"], "#000000", 0.45)
    for i in range(5):
        xx = x + lado * i * w / 5
        props.poly(f"{nome}{i}", cena.rect(xx - w / 10, 0, xx + w / 10, h), _mix(cor, p["borda"], 0.06 * (i % 2)), y - 0.001 * i)


def lustre(p, nome, x, z, y, frames=200):
    esc = _esc(p, 0.3)
    props.poly(nome + "_c", cena.rect(x - 0.01, z, x + 0.01, z + 1.5), esc, y)
    props.inked(nome + "_a", [(x - 0.45, z), (x + 0.45, z), (x + 0.3, z + 0.12), (x - 0.3, z + 0.12)], "#c9a050", None, loc=(0, y - 0.01, 0), w=0.0, rim=0.01, rim_color="#fff0c0")
    for i in range(5):
        xx = x - 0.4 + i * 0.2
        props.poly(f"{nome}_l{i}", circle(xx, z - 0.06, 0.05, 12), "#fff0c0", y - 0.02, strength=1.8)
    cena.disc(nome + "_g", 0.9, cena.amat(nome + "_gm", "#ffd090", 1.0, 0.4, ("radial", 1.4)), (x, y - 0.03, z))


def garrafas(p, nome, x, y, z, n=3):
    cores = ["#2f6a40", "#6a3a20", "#cfd8e8"]
    for i in range(n):
        xx = x + i * 0.16; c = cores[i % 3]
        props.inked(f"{nome}{i}", [(xx - 0.05, z), (xx + 0.05, z), (xx + 0.05, z + 0.22), (xx + 0.02, z + 0.28), (xx + 0.02, z + 0.36), (xx - 0.02, z + 0.36), (xx - 0.02, z + 0.28), (xx - 0.05, z + 0.22)],
                    c, None, loc=(0, y - 0.001 * i, 0), w=0.0, rim=0.01, rim_color="#ffffff")


def luminaria_mesa(p, nome, x, y, z, cor_luz=None):
    esc = _esc(p, 0.3)
    props.poly(nome + "_b", rrect(x - 0.1, z, x + 0.1, z + 0.03, 0.01, 2), esc, y)
    props.poly(nome + "_h", stroke([(x, z + 0.02), (x - 0.08, z + 0.3), (x + 0.05, z + 0.45)], 0.012), esc, y)
    props.poly(nome + "_c", [(x - 0.05, z + 0.38), (x + 0.18, z + 0.48), (x + 0.2, z + 0.4), (x + 0.02, z + 0.32)], "#2f8a54", y - 0.001)
    cena.disc(nome + "_g", 0.35, cena.amat(nome + "_gm", cor_luz or p["luz"], 1.0, 0.4, ("radial", 1.5)), (x + 0.12, y - 0.01, z + 0.3))


def arvore(p, nome, x, y, s=1.0):
    r = empty(nome, None, (x, y, 0)); r.scale = (s, s, s); cor = _esc(p, 0.45)
    props.poly(nome + "_t", cena.rect(-0.08, 0, 0.08, 1.6), cor, 0.0, r)
    for i, (cx, cz, rr) in enumerate(((0, 2.2, 0.75), (-0.5, 1.8, 0.55), (0.5, 1.85, 0.55), (0.0, 2.8, 0.5))):
        props.poly(f"{nome}_c{i}", circle(cx, cz, rr, 28), _mix(cor, p["mid"], 0.12 * i), -0.001 * i, r)
    return r


def caixa_correio(p, nome, x, y):
    props.poly(nome + "_p", cena.rect(x - 0.03, 0, x + 0.03, 1.0), _esc(p, 0.3), y)
    props.inked(nome + "_c", rrect(x - 0.18, 1.0, x + 0.18, 1.25, 0.08, 4), "#2a4a9a", None, loc=(0, y - 0.01, 0), w=0.0, rim=0.015, rim_color=p["borda"])


def varal_luzes(p, nome, x0, x1, z, y, n=12, cor="#ffd090"):
    pts = [(x0 + (x1 - x0) * k / 24, z - 0.3 * math.sin(math.pi * k / 24)) for k in range(25)]
    props.poly(nome + "_f", stroke(pts, 0.006), _esc(p, 0.4), y)
    for i in range(n):
        u = (i + 0.5) / n; xx = x0 + (x1 - x0) * u; zz = z - 0.3 * math.sin(math.pi * u) - 0.05
        props.poly(f"{nome}_l{i}", circle(xx, zz, 0.035, 10), cor, y - 0.002, strength=2.0)
        cena.disc(f"{nome}_g{i}", 0.12, cena.amat(nome + "_gm", cor, 1.0, 0.35, ("radial", 1.4)), (xx, y - 0.004, zz))


def espreguicadeira(p, nome, x, y, flip=1):
    r = empty(nome, None, (x, y, 0)); r.scale = (flip, 1, 1); cor = _mix(p["mid"], "#000000", 0.4)
    props.poly(nome + "_a", [(-0.6, 0.35), (0.3, 0.35), (0.6, 0.85), (0.5, 0.88), (0.22, 0.42), (-0.6, 0.42)], cor, 0.0, r)
    for xx in (-0.5, 0.2):
        props.poly(f"{nome}_p{xx}", cena.rect(xx, 0, xx + 0.04, 0.36), cor, 0.001, r)


def placa_numero(p, nome, x, z, y, txt):
    props.inked(nome, rrect(x - 0.14, z - 0.1, x + 0.14, z + 0.1, 0.02, 3), "#e8e2d6", None, loc=(0, y, 0), w=0.0, rim=0.0)
    props.txt(nome + "_t", txt, 0.1, "#0d1020", (x, y - 0.002, z - 0.035), None, ink=None)
