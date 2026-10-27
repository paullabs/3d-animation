"""Transição invisível: corte em movimento (match cut por velocidade).
A câmera da cena A acelera no fim (rampa de entrada) e a da cena B já começa andando na MESMA velocidade de tela e
desacelera (rampa de saída). O corte cai no pico de velocidade, onde o olho não acompanha os detalhes; um borrão de
movimento só nos quadros vizinhos do corte (feito na montagem) esconde a emenda. Nada cobre a tela, nada fica parado.

Velocidade de tela = velocidade no mundo / distância da câmera ao assunto. Para a emenda não "dar tranco",
delta_B = delta_A * dist_B / dist_A (mesma rampa, mesma duração)."""
from mathutils import Vector
from lib import key, _fcs


def _pos(cam, f):
    vals = [0.0, 0.0, 0.0]
    for fc in _fcs(cam):
        if fc.data_path == "location":
            vals[fc.array_index] = fc.evaluate(f)
    return Vector(vals)


def rampa_fim(cam, f_corte, direcao, delta, n=7):
    """últimos n quadros: soma um deslocamento que acelera (u²) até 'delta' metros na direção dada (x, y, z)"""
    d = Vector(direcao).normalized()
    base = {f: _pos(cam, f) for f in range(f_corte - n, f_corte)}
    for f in range(f_corte - n, f_corte):
        u = (f - (f_corte - n) + 1) / n
        cam.location = base[f] + d * delta * u * u; key(cam, "location", f, "LINEAR")


def rampa_inicio(cam, f_corte, direcao, delta, n=7):
    """primeiros n quadros: começa 'delta' metros atrás na direção e chega desacelerando (1-u)² ao caminho normal"""
    d = Vector(direcao).normalized()
    base = {f: _pos(cam, f) for f in range(f_corte, f_corte + n + 1)}
    for f in range(f_corte, f_corte + n + 1):
        u = (f - f_corte) / n
        cam.location = base[f] - d * delta * (1 - u) ** 2; key(cam, "location", f, "LINEAR")
