"""O abrigo por dentro em 3D de verdade (pedido de 24/10/2026: "modelar mais, tudo muito flat").
Concreto verde-musgo com juntas de painel, tubos e eletrodutos no teto, grade de ventilação, cabos presos na parede, caixotes, e a
parede do fundo com o vão da porta de verdade (dá para ver o lado de fora pelo vidro da janelinha).
Usa as peças de objetos3d_abrigo."""
import math, random
import bpy
from lib import empty
import cena, props
import objetos3d_abrigo as O3
from objetos3d_abrigo import M, caixa, cilindro, tubo
import prod_abrigo as PA


def sala3d(p, wy=5.5, x0=-3.6, x1=3.6, h=2.9, y0=-10.0, porta_x=None, porta_s=1.0, seed=4):
    """a sala: chão de lajota, paredes com juntas de painel, teto com vigas, tubos, eletrodutos e luminárias; se porta_x, abre o vão da porta na parede do fundo"""
    rnd = random.Random(seed)
    PA.sala_abrigo(p, wy=wy, x0=x0, x1=x1, h=h, y0=y0, pilastra=0, fundo=porta_x is None)
    par = M("#4a5c50", "#364539", "#8a9a7e")
    if porta_x is not None:
        w2 = 0.62 * porta_s
        for k, (a, b) in enumerate(((x0, porta_x - w2), (porta_x + w2, x1))):
            caixa(f"parede_f{k}", (b - a, 0.3, h), par, None, ((a + b) / 2, wy + 0.15, h / 2), chanfro=0.0, contorno=0.0)
        caixa("parede_ftopo", (2 * w2, 0.3, h - 2.32 * porta_s), par, None, (porta_x, wy + 0.15, (h + 2.32 * porta_s) / 2), chanfro=0.0, contorno=0.0)
    for k in range(int((x1 - x0) / 1.2)):                                              # juntas dos painéis de concreto
        x = x0 + 1.2 * (k + 1)
        if porta_x is not None and abs(x - porta_x) < 0.75 * porta_s:
            continue
        caixa(f"junta{k}", (0.02, 0.02, h), M("#3a4a3f"), None, (x, wy - 0.012, h / 2), chanfro=0.0, contorno=0.0)
    caixa("rodape_f", (x1 - x0, 0.04, 0.12), M("#33402f"), None, ((x0 + x1) / 2, wy - 0.02, 0.06), chanfro=0.0, contorno=0.0)
    tm = M("#6a6e64", "#4a4e46", "#c8c0a0")
    for k, (z, y, r) in enumerate(((h - 0.12, wy - 0.25, 0.06), (h - 0.1, wy - 0.45, 0.035), (h - 0.18, 1.0, 0.045))):
        tubo(f"cano{k}", [(x0, y, z), (x1, y, z)], [r, r], tm, None, seg=16, tampa=2)
        for j in range(int((x1 - x0) / 1.4)):
            caixa(f"brac{k}_{j}", (0.04, 0.05, 0.14), M("#3a3d36"), None, (x0 + 0.7 + 1.4 * j, y, z + 0.06), chanfro=0.0, contorno=0.0)
    tubo("eletroduto", [(x0 + 0.02, wy - 0.6, 0.3), (x0 + 0.02, wy - 0.6, h - 0.05), (x0 + 0.02, 0.0, h - 0.05)], [0.018] * 3, M("#8a8a7e"), None, seg=10, tampa=2)
    caixa("quadro_luz", (0.05, 0.35, 0.45), M("#5a6058", "#3e443c"), None, (x0 + 0.03, wy - 0.6, 1.4), chanfro=0.01)
    caixa("ventil", (0.6, 0.04, 0.35), M("#3a4038"), None, ((x0 + x1) / 2 + 1.6, wy - 0.02, h - 0.45), chanfro=0.01)
    for k in range(6):
        caixa(f"ventil_r{k}", (0.56, 0.03, 0.02), M("#22281f"), None, ((x0 + x1) / 2 + 1.6, wy - 0.045, h - 0.6 + 0.055 * k), chanfro=0.0, contorno=0.0)
    for k in range(3 if x1 - x0 > 6 else 0):
        caixa(f"caixote{k}", (0.6, 0.45, 0.4), M("#6b5a3e", "#4e4130", "#a8916a"), None, (x1 - 0.5, wy - 2.6 + 0.55 * k, 0.2 + (0.4 if k == 2 else 0)), chanfro=0.02, rot=(0, 0, rnd.uniform(-8, 8)))


def fora_porta(p, porta_x, wy, vizinhos=True, s=1.15):
    """o lado de fora atrás da porta: luz branca suja e, se vizinhos, a dona da padaria e o rapaz do mercado colados no vidro"""
    import elenco3d_abrigo as E3
    cena.poly_mesh("fora_ceu", [(porta_x - 6, wy + 3.0, -1), (porta_x + 6, wy + 3.0, -1), (porta_x + 6, wy + 3.0, 6), (porta_x - 6, wy + 3.0, 6)], props.FM("#ece8d8"))
    PA.halo("fora_gl", porta_x, wy + 2.9, 2.2, 3.0, "#ffffff", 0.6)
    out = []
    if vizinhos:
        for nm, ch, dx, ang in (("padeira", "padeira", -0.1, 8), ("mercado", "mercado", 0.17, -10)):
            h_ = E3.faz(ch, nm + "_inv"); h_.raiz.location = (porta_x + dx, wy + 0.45, 0.62); h_.raiz.rotation_euler.z = math.radians(ang)
            h_.pose(ombro=(-100, -96), cotovelo=(-70, -64), abre=(18, 16), tronco=-14, cabeca=-6); h_.rosto(boca="o", lid=0.0)
            out.append(h_)
    return out
