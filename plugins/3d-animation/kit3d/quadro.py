"""Planejamento de quadro: a câmera é calculada a partir do que PRECISA aparecer (a "caixa do assunto"), e um conferente
verifica, quadro a quadro, se cada objeto-chave ficou dentro da área segura do Reels (area.py).

Modelo da câmera (sensor_fit horizontal, 24 mm, olhando para +y, sem girar):
  largura do quadro na distância d: Wm = d * 24 / lente; altura Hm = Wm * 16/9;
  o shift desloca o centro do quadro em (sx * Wm, sy * Wm).
Com o shift padrão (area.shift_padrao), a câmera na altura do centro da caixa já põe a caixa no centro da área segura."""
import math
import area

FRAC_W = (area.SEGURA[2] - area.SEGURA[0]) / area.W         # fração da largura que é segura
FRAC_H = (area.SEGURA[3] - area.SEGURA[1]) / area.H         # fração da altura que é segura
OFF_X = area.CX / area.W - 0.5                               # centro da área segura, em larguras, a partir do centro
OFF_Y = 0.5 - area.CY / area.H                               # idem, em alturas (para cima)


def enquadra(caixa, lente=35, preenche=0.85, alt=None):
    """caixa = (x0, x1, z0, z1, y): o retângulo (no plano de profundidade y) que tem de caber na área segura.
    preenche = quanto da área segura a caixa ocupa (0,85 = 15% de respiro).
    alt = altura da câmera (de cima ou de baixo); sem alt, a câmera fica na altura do centro da caixa.
    Devolve ((x, y, z) da câmera, (shift_x, shift_y), distância até o plano da caixa)."""
    x0, x1, z0, z1, yb = caixa
    bw, bh = x1 - x0, z1 - z0
    wm = max(bw / (FRAC_W * preenche), bh / (FRAC_H * preenche * 16 / 9))
    d = wm * lente / 24.0
    hm = wm * 16 / 9
    bcx, bcz = (x0 + x1) / 2, (z0 + z1) / 2
    cz = bcz if alt is None else alt
    sy = ((bcz - cz) - OFF_Y * hm) / wm
    return (bcx, yb - d, cz), (-OFF_X, sy), d


def verifica(sc, cam, objetos, frames, tol=8, nome=""):
    """confere se os objetos (e todos os filhos com malha) ficam dentro da área segura nos quadros dados.
    Devolve a lista de problemas [(quadro, objeto, lado, pixels para fora)]"""
    import bpy
    from bpy_extras.object_utils import world_to_camera_view
    probs = []
    x0, y0, x1, y1 = area.SEGURA
    for f in frames:
        sc.frame_set(f); bpy.context.view_layer.update()
        for ob in objetos:
            if ob is None:
                continue
            if ob.scale.length < 0.01 and ob.type == "EMPTY":
                continue
            pts = []
            for o in [ob] + list(ob.children_recursive):
                if o.type not in ("MESH", "CURVE", "FONT") or o.matrix_world.to_scale().length < 0.001:
                    continue
                if o.hide_render:
                    continue
                for v in o.bound_box:
                    pts.append(o.matrix_world @ __import__("mathutils").Vector(v))
            if not pts:
                continue
            px = []; py = []
            for p in pts:
                co = world_to_camera_view(sc, cam, p)
                if co.z <= 0:
                    continue
                px.append(co.x * area.W); py.append((1 - co.y) * area.H)
            if not px:
                continue
            for lado, fora in (("esquerda", x0 - min(px)), ("direita", max(px) - x1), ("cima", y0 - min(py)), ("baixo", max(py) - y1)):
                if fora > tol:
                    probs.append((f, ob.name, lado, int(fora)))
    return probs
