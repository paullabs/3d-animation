"""Ambientes 3D de verdade (crítica de 23/10/2026: "o ambiente é um fundo chapado, falta o 3D").
Uma sala é uma caixa aberta para a câmera: chão com linhas em perspectiva, paredes laterais com pilastras, teto com vigas,
parede do fundo. A câmera entra nela e anda em profundidade, e as linhas e pilastras dão a paralaxe.
Tudo em cor chapada (emissão), como o resto do canal; a profundidade vem das camadas, das linhas e da névoa."""
import math
import cena, props
from props import _mix
from lib import empty


def _quad(nome, pts, cor):
    return cena.poly_mesh(nome, pts, props.FM(cor))


def sala(nome, x0, x1, y0, y1, h, c, piso="tabuas", passo_pilastra=1.6, passo_viga=1.4, fundo=True):
    """c = dict(parede, lateral, teto, viga, chao, linha, pilastra). piso: "tabuas" (linhas ao longo da profundidade)
    ou "lajotas" (grade). As paredes laterais ficam um pouco mais escuras que a do fundo (a luz vem de frente)."""
    _quad(f"{nome}_chao", [(x0, y0, 0), (x1, y0, 0), (x1, y1, 0), (x0, y1, 0)], c["chao"])
    if piso == "tabuas":
        n = int((x1 - x0) / 0.32)
        for i in range(1, n):
            x = x0 + i * (x1 - x0) / n
            _quad(f"{nome}_tab{i}", [(x - 0.008, y0, 0.001), (x + 0.008, y0, 0.001), (x + 0.008, y1, 0.001), (x - 0.008, y1, 0.001)], c["linha"])
    elif piso == "lajotas":
        n = int((x1 - x0) / 0.9)
        for i in range(1, n):
            x = x0 + i * (x1 - x0) / n
            _quad(f"{nome}_lx{i}", [(x - 0.01, y0, 0.001), (x + 0.01, y0, 0.001), (x + 0.01, y1, 0.001), (x - 0.01, y1, 0.001)], c["linha"])
        m = int((y1 - y0) / 0.9)
        for j in range(1, m):
            y = y0 + j * (y1 - y0) / m
            _quad(f"{nome}_ly{j}", [(x0, y - 0.01, 0.001), (x1, y - 0.01, 0.001), (x1, y + 0.01, 0.001), (x0, y + 0.01, 0.001)], c["linha"])
    for lado, x in (("e", x0), ("d", x1)):
        _quad(f"{nome}_lat{lado}", [(x, y0, 0), (x, y1, 0), (x, y1, h), (x, y0, h)], c["lateral"])
        _quad(f"{nome}_rod{lado}", [(x + (0.01 if lado == "e" else -0.01), y0, 0), (x + (0.01 if lado == "e" else -0.01), y1, 0),
                                    (x + (0.01 if lado == "e" else -0.01), y1, 0.12), (x + (0.01 if lado == "e" else -0.01), y0, 0.12)], c["linha"])
        if passo_pilastra:
            y = y0 + passo_pilastra * 0.5
            k = 0
            while y < y1 - 0.2:
                dx = 0.12 if lado == "e" else -0.12
                _quad(f"{nome}_pil{lado}{k}", [(x + dx, y - 0.16, 0), (x + dx, y + 0.16, 0), (x + dx, y + 0.16, h), (x + dx, y - 0.16, h)], c["pilastra"])
                _quad(f"{nome}_pil{lado}{k}_s", [(x, y - 0.16, 0), (x + dx, y - 0.16, 0), (x + dx, y - 0.16, h), (x, y - 0.16, h)], _mix(c["pilastra"], "#000000", 0.35))
                y += passo_pilastra; k += 1
    _quad(f"{nome}_teto", [(x0, y0, h), (x1, y0, h), (x1, y1, h), (x0, y1, h)], c["teto"])
    if passo_viga:
        y = y0 + passo_viga * 0.5; k = 0
        while y < y1:
            _quad(f"{nome}_viga{k}", [(x0, y, h - 0.22), (x1, y, h - 0.22), (x1, y + 0.18, h - 0.22), (x0, y + 0.18, h - 0.22)], c["viga"])
            _quad(f"{nome}_viga{k}_f", [(x0, y, h - 0.22), (x1, y, h - 0.22), (x1, y, h), (x0, y, h)], _mix(c["viga"], "#000000", 0.3))
            y += passo_viga; k += 1
    if fundo:
        _quad(f"{nome}_fundo", [(x0, y1, 0), (x1, y1, 0), (x1, y1, h), (x0, y1, h)], c["parede"])


def colunata(nome, x, y0, y1, passo, h, cor, w=0.32, sombra=None):
    """fileira de colunas lisas ao longo da profundidade (frente clara, lateral escura)"""
    y = y0; k = 0
    while y <= y1:
        _quad(f"{nome}{k}_f", [(x - w / 2, y, 0), (x + w / 2, y, 0), (x + w / 2, y, h), (x - w / 2, y, h)], cor)
        _quad(f"{nome}{k}_l", [(x - w / 2 if x > 0 else x + w / 2, y, 0), (x - w / 2 if x > 0 else x + w / 2, y + w, 0),
                               (x - w / 2 if x > 0 else x + w / 2, y + w, h), (x - w / 2 if x > 0 else x + w / 2, y, h)], sombra or _mix(cor, "#000000", 0.3))
        y += passo; k += 1


def tapete(nome, x, y0, y1, w, cor, borda=None):
    _quad(nome, [(x - w / 2, y0, 0.003), (x + w / 2, y0, 0.003), (x + w / 2, y1, 0.003), (x - w / 2, y1, 0.003)], cor)
    if borda:
        for s in (-1, 1):
            xb = x + s * (w / 2 - 0.05)
            _quad(f"{nome}_b{s}", [(xb - 0.03, y0, 0.004), (xb + 0.03, y0, 0.004), (xb + 0.03, y1, 0.004), (xb - 0.03, y1, 0.004)], borda)


def janela_lateral(nome, x, y, z0, z1, larg, cor_luz, lado=1):
    """janela recortada na parede lateral (plano YZ), virada para dentro"""
    dx = -0.02 * lado
    _quad(nome, [(x + dx, y - larg / 2, z0), (x + dx, y + larg / 2, z0), (x + dx, y + larg / 2, z1), (x + dx, y - larg / 2, z1)], cor_luz)


def persiana(nome, x, y, z0, z1, larg, cor_luz, cor_ripa, n=11):
    """janela de persiana na parede do fundo: luz atrás e ripas escuras na frente (luz fria em faixas)"""
    _quad(nome, [(x - larg / 2, y - 0.01, z0), (x + larg / 2, y - 0.01, z0), (x + larg / 2, y - 0.01, z1), (x - larg / 2, y - 0.01, z1)], cor_luz)
    passo = (z1 - z0) / n
    for k in range(n):
        z = z0 + k * passo
        _quad(f"{nome}_r{k}", [(x - larg / 2, y - 0.02, z), (x + larg / 2, y - 0.02, z), (x + larg / 2, y - 0.02, z + passo * 0.45), (x - larg / 2, y - 0.02, z + passo * 0.45)], cor_ripa)
    for s in (-1, 1):
        _quad(f"{nome}_mol{s}", [(x + s * larg / 2 - 0.05, y - 0.03, z0 - 0.05), (x + s * larg / 2 + 0.05, y - 0.03, z0 - 0.05),
                                 (x + s * larg / 2 + 0.05, y - 0.03, z1 + 0.05), (x + s * larg / 2 - 0.05, y - 0.03, z1 + 0.05)], cor_ripa)


def patio(nome, x0, x1, y0, y1, cor, linha, passo=1.2):
    """chão externo (concreto, asfalto) com juntas em grade: as linhas em perspectiva dão a profundidade"""
    _quad(f"{nome}_chao", [(x0, y0, 0), (x1, y0, 0), (x1, y1, 0), (x0, y1, 0)], cor)
    x = x0 + passo; k = 0
    while x < x1:
        _quad(f"{nome}_jx{k}", [(x - 0.012, y0, 0.001), (x + 0.012, y0, 0.001), (x + 0.012, y1, 0.001), (x - 0.012, y1, 0.001)], linha); x += passo; k += 1
    y = y0 + passo; k = 0
    while y < y1:
        _quad(f"{nome}_jy{k}", [(x0, y - 0.012, 0.001), (x1, y - 0.012, 0.001), (x1, y + 0.012, 0.001), (x0, y + 0.012, 0.001)], linha); y += passo; k += 1


def predio(nome, x, y, w, h, d, cor, lateral, janelas=None, acesas=0.35, seed=1, passo=(0.9, 1.1)):
    """bloco de prédio com frente, lateral e tampo; grade de janelas (algumas acesas)"""
    import random
    rnd = random.Random(seed)
    _quad(f"{nome}_f", [(x - w / 2, y, 0), (x + w / 2, y, 0), (x + w / 2, y, h), (x - w / 2, y, h)], cor)
    _quad(f"{nome}_l", [(x + w / 2, y, 0), (x + w / 2, y + d, 0), (x + w / 2, y + d, h), (x + w / 2, y, h)], lateral)
    _quad(f"{nome}_e", [(x - w / 2, y, 0), (x - w / 2, y + d, 0), (x - w / 2, y + d, h), (x - w / 2, y, h)], lateral)
    if janelas:
        apag, acesa = janelas
        px, pz = passo
        nx, nz = int((w - 0.4) / px), int((h - 0.8) / pz)
        for i in range(nx):
            for j in range(nz):
                cx = x - (nx - 1) * px / 2 + i * px; cz = 0.9 + j * pz
                cor_j = acesa if rnd.random() < acesas else apag
                _quad(f"{nome}_j{i}_{j}", [(cx - 0.25, y - 0.01, cz), (cx + 0.25, y - 0.01, cz), (cx + 0.25, y - 0.01, cz + 0.6), (cx - 0.25, y - 0.01, cz + 0.6)], cor_j)
