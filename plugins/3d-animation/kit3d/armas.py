"""Armas de desenho (chapadas, com contorno e borda de luz), para cenas narradas. Nada realista: só a silhueta que se reconhece."""
import math
import lib
from lib import empty, key
import props
from char2d import rrect
from puppet2d import circle, smooth

METAL, METAL_ES = "#2a2c38", "#1a1b24"
MADEIRA, MADEIRA_ES = "#9a5a2c", "#6e3c1b"


def ak47(name, parent=None, loc=(0, 0, 0), s=1.0, rim="#ffb36e"):
    """fuzil de assalto estilo AK: o cano aponta para +x; a origem é o cabo (onde a mão segura). ~0,9 m"""
    root = empty(name, parent, loc); root.scale = (s, s, s)
    P = lambda nm, pts, cor, y=0.0, sh=None, rimw=0.012: props.inked(f"{name}_{nm}", pts, cor, root, loc=(0, y, 0), w=0.008,
                                                                    shade=0.012 if sh else 0.0, shade_color=sh, rim=rimw, rim_color=rim)
    P("coronha", smooth([(-0.52, -0.07), (-0.5, 0.0), (-0.14, 0.055), (-0.13, 0.0), (-0.2, -0.03), (-0.5, -0.12)], 4), MADEIRA, 0.002, MADEIRA_ES)
    P("corpo", rrect(-0.15, -0.01, 0.2, 0.075, 0.015, 3), METAL, 0.0, METAL_ES)
    P("cabo", [(-0.04, 0.0), (0.02, 0.0), (-0.01, -0.13), (-0.07, -0.12)], METAL, -0.002, METAL_ES, rimw=0.008)
    P("carregador", smooth([(0.07, 0.0), (0.15, 0.0), (0.2, -0.12), (0.24, -0.22), (0.16, -0.25), (0.12, -0.13)], 4), METAL, -0.003, METAL_ES)
    P("guarda", rrect(0.2, -0.0, 0.42, 0.065, 0.02, 3), MADEIRA, 0.001, MADEIRA_ES)
    P("tubo", rrect(0.2, 0.065, 0.46, 0.09, 0.01, 2), METAL, 0.0015, rimw=0.006)
    P("cano", rrect(0.42, 0.015, 0.7, 0.042, 0.008, 2), METAL, 0.0012, rimw=0.006)
    P("mira", [(0.6, 0.042), (0.63, 0.042), (0.625, 0.1), (0.605, 0.1)], METAL, 0.0011, rimw=0.004)
    P("boca", rrect(0.68, 0.01, 0.73, 0.047, 0.006, 2), METAL_ES, 0.001, rimw=0.004)
    return root


def cai_na_mao(o, f_mao, altura=1.6, frames=11, rot_alvo=-30.0, rot_queda=-78.0, afunda=0.075, freq=2.8, zeta=0.28, dur=30):
    """O fuzil cai e quica na mão seguindo curvas contínuas (curvas.py), gravadas quadro a quadro:
    - queda: curva "queda" (ease-in), de 'altura' m acima até a mão, girando de rot_queda até perto de rot_alvo;
    - impacto (f_mao): mola amortecida (curvas.pancada): afunda 'afunda' m, volta passando do ponto, assenta;
    - o giro assenta com mola (curvas.mola), passando um pouco do alvo;
    - squash e stretch ligados ao deslocamento (afundou = achata, subiu = estica), nada de valor fixo.
    A queda é na vertical do MUNDO, convertida para o espaço do pai (a mão)."""
    import bpy, math
    from mathutils import Vector
    import curvas
    sc = bpy.context.scene; sc.frame_set(f_mao); bpy.context.view_layer.update()
    pm = o.parent.matrix_world.to_3x3()
    cima = pm.inverted() @ Vector((0, 0, 1.0))
    p0 = o.location.copy(); base = tuple(o.scale)
    rot_fim_queda = rot_alvo + (rot_queda - rot_alvo) * 0.35            # chega ainda um pouco girado e a mola termina o giro
    o.scale = (0.0001,) * 3; key(o, "scale", f_mao - frames - 1, "CONSTANT")
    for f in range(f_mao - frames, f_mao + dur + 1):
        if f <= f_mao:
            u = (f - (f_mao - frames)) / frames; sq = curvas.s("queda", u)
            off = altura * (1 - sq); rot = rot_queda + (rot_fim_queda - rot_queda) * sq
            esticar = 0.10 * sq ** 3                                    # estica um pouco ao acelerar (stretch na queda)
            sx, sy, sz = 1 - 0.5 * esticar, 1.0, 1 + esticar
        else:
            t = (f - f_mao) / 24.0
            d = curvas.pancada(t, freq, zeta)                           # 1 = afundamento máximo
            off = -afunda * d
            rot = rot_alvo + (rot_fim_queda - rot_alvo) * (1 - curvas.mola(t, freq, zeta))
            esq = max(-1.0, min(1.0, d))                                # d>0: afundou -> achata; d<0: voltou passando -> estica
            sz = 1 - 0.20 * esq; sx = 1 + 0.10 * esq; sy = 1.0
        o.location = p0 + cima * off; key(o, "location", f, "LINEAR")
        o.rotation_euler = (0, math.radians(rot), 0); key(o, "rotation_euler", f, "LINEAR")
        o.scale = (base[0] * sx, base[1] * sy, base[2] * sz); key(o, "scale", f, "LINEAR")
