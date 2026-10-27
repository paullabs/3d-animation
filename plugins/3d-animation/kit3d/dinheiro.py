"""Dinheiro que se reconhece de longe: nota de R$ 100 (azul) com o "100" e a cinta de papel, maço visto de frente,
parede e paletes de maços numa malha só (milhares de maços sem pesar) e a nota grande com detalhes para o inserto.
Medidas reais: nota de 15,6 x 7 cm; maço de 100 notas = R$ 10 mil."""
import bpy, math
import numpy as np
import lib
from lib import empty
import cena, props
from char2d import rrect
from puppet2d import circle

W, H = 0.156, 0.070
AZUL, AZUL_CL, AZUL_ES, AZUL_TINTA = "#4f8fc6", "#93c3e8", "#1f4f84", "#0f2a4a"
CINTA, CINTA_ES, BORDA, BORDA_LIN = "#efe6cf", "#bfae86", "#d9e6f0", "#a9c3d8"
PASSO_X, PASSO_Z = W + 0.009, H + 0.007


def _r(x0, z0, x1, z1):
    return [(x0, z0), (x1, z0), (x1, z1), (x0, z1)]


def molde_maco(topo=False, detalhe=True):
    """camadas de um maço visto de frente (origem no meio da base), de trás para a frente: [(polígono, cor)]"""
    w, h = W, H
    L = [(_r(-w / 2 - 0.004, -0.004, w / 2 + 0.004, h + 0.004), AZUL_TINTA), (_r(-w / 2, 0, w / 2, h), AZUL)]
    if detalhe:
        L += [(_r(-w / 2 + 0.006, 0.006, -w / 2 + 0.058, h - 0.006), AZUL_CL),
              (circle(-w / 2 + 0.032, h / 2, 0.017, 16), AZUL_ES),
              (_r(w / 2 - 0.056, 0.017, w / 2 - 0.048, 0.055), AZUL_ES),
              (rrect(w / 2 - 0.044, 0.017, w / 2 - 0.028, 0.055, 0.006, 2), AZUL_ES),
              (rrect(w / 2 - 0.039, 0.025, w / 2 - 0.033, 0.047, 0.002, 1), AZUL),
              (rrect(w / 2 - 0.025, 0.017, w / 2 - 0.009, 0.055, 0.006, 2), AZUL_ES),
              (rrect(w / 2 - 0.020, 0.025, w / 2 - 0.014, 0.047, 0.002, 1), AZUL)]
    L += [(_r(-0.008, -0.003, 0.024, h + 0.003), CINTA), (_r(-0.008, -0.003, -0.005, h + 0.003), CINTA_ES), (_r(0.021, -0.003, 0.024, h + 0.003), CINTA_ES)]
    if topo:   # a borda das notas vista de cima, só no maço do alto da pilha
        sk, th = 0.014, 0.018
        L += [([(-w / 2, h), (w / 2, h), (w / 2 + sk, h + th), (-w / 2 + sk, h + th)], BORDA)]
        for k in (1, 2, 3):
            z, d = h + th * k / 4, sk * k / 4
            L += [([(-w / 2 + d, z - 0.0008), (w / 2 + d, z - 0.0008), (w / 2 + d, z + 0.0008), (-w / 2 + d, z + 0.0008)], BORDA_LIN)]
        L += [([(-0.008, h), (0.024, h), (0.024 + sk, h + th), (-0.008 + sk, h + th)], CINTA)]
    return L


def malha(name, molde, pos, s=1.0, dy=0.00025, parent=None):
    """muitas cópias de um molde (camadas cada vez mais perto da câmera) numa malha só. pos = [(x, z)] ou [(x, z, y)]"""
    cores = []
    for _, c in molde:
        if c not in cores:
            cores.append(c)
    tpl = [(np.array(p, dtype=np.float32), cores.index(c), li) for li, (p, c) in enumerate(molde)]
    verts, faces, mats = [], [], []
    n = 0
    for p in pos:
        x, z = p[0], p[1]; y0 = p[2] if len(p) > 2 else 0.0
        for pts, ci, li in tpl:
            k = len(pts)
            v = np.empty((k, 3), dtype=np.float32)
            v[:, 0] = x + pts[:, 0] * s; v[:, 1] = y0 - li * dy; v[:, 2] = z + pts[:, 1] * s
            verts.append(v); faces.append(tuple(range(n, n + k))); mats.append(ci); n += k
    me = bpy.data.meshes.new(name)
    me.from_pydata(np.concatenate(verts).tolist(), [], faces)
    for c in cores:
        me.materials.append(props.FM(c))
    me.polygons.foreach_set("material_index", np.array(mats, dtype=np.int32)); me.update()
    o = bpy.data.objects.new(name, me); bpy.context.scene.collection.objects.link(o)
    if parent:
        o.parent = parent
    return o


def parede(name, cols, rows, loc=(0, 0, 0), s=1.0, detalhe=True, tijolo=True, parent=None):
    """parede de maços empilhados (desencontrados como tijolo); a fileira de cima mostra a borda das notas.
    A origem fica no meio da base. Devolve o objeto (largura = cols * PASSO_X * s)."""
    corpo, topo = [], []
    for r in range(rows):
        off = (PASSO_X / 2 if (tijolo and r % 2) else 0.0)
        for i in range(cols - (1 if (tijolo and r % 2) else 0)):
            x = (i - (cols - 1) / 2) * PASSO_X + off
            (topo if r == rows - 1 else corpo).append((x, r * PASSO_Z))
    root = empty(name, parent, loc); root.scale = (s, s, s)
    if corpo:
        malha(name + "_c", molde_maco(False, detalhe), corpo, parent=root)
    malha(name + "_t", molde_maco(True, detalhe), topo, parent=root)
    return root


def palete(name, loc, cols=8, rows=13, s=1.0, detalhe=False):
    """um palete de madeira com um bloco de maços em cima"""
    root = empty(name, None, loc); root.scale = (s, s, s)
    wd = cols * PASSO_X + 0.04
    props.poly(name + "_mad", _r(-wd / 2, 0.0, wd / 2, 0.13), "#5a3d26", 0.0, root)
    for k in range(5):
        x = -wd / 2 + 0.03 + k * (wd - 0.1) / 4
        props.poly(f"{name}_pe{k}", _r(x, 0.0, x + 0.07, 0.13), "#3a2617", -0.001, root)
    props.poly(name + "_tab", _r(-wd / 2, 0.1, wd / 2, 0.13), "#7a5634", -0.002, root)
    parede(name + "_m", cols, rows, (0, -0.004, 0.135), 1.0, detalhe, tijolo=False, parent=root)
    return root


def nota_grande(name, loc, s=1.0, parent=None):
    """a nota de R$ 100 com detalhes (para o inserto em tela cheia). Origem no centro; largura W * s."""
    root = empty(name, parent, loc); root.scale = (s, s, s)
    w, h = W, H
    props.inked(name + "_b", rrect(-w / 2, -h / 2, w / 2, h / 2, 0.003, 3), AZUL, root, ink=AZUL_TINTA, w=0.0016)
    props.poly(name + "_pain", rrect(-w / 2 + 0.005, -h / 2 + 0.005, -w / 2 + 0.062, h / 2 - 0.005, 0.003, 3), AZUL_CL, -0.0002, root)
    props.poly(name + "_ef", circle(-w / 2 + 0.034, 0.002, 0.022, 32), "#6fa6d6", -0.0004, root)
    props.poly(name + "_ef1", circle(-w / 2 + 0.034, 0.002, 0.018, 32), "#bcdcf2", -0.0005, root)              # medalhão da efígie
    props.poly(name + "_ef2", circle(-w / 2 + 0.034, 0.002, 0.0145, 32), "#5f99cf", -0.0006, root)
    props.poly(name + "_ef3", circle(-w / 2 + 0.034, 0.005, 0.0062, 24), "#3b74ad", -0.0007, root)
    props.poly(name + "_ef4", rrect(-w / 2 + 0.026, -0.012, -w / 2 + 0.042, -0.003, 0.004, 3), "#3b74ad", -0.0007, root)
    for k in range(7):                                      # linhas finas de segurança
        z = -h / 2 + 0.01 + k * 0.008
        pts = [(-w / 2 + 0.066 + 0.004 * i, z + 0.0018 * math.sin(i * 0.9 + k)) for i in range(20)]
        props.poly(f"{name}_lin{k}", props.stroke(pts, 0.0005), "#78acd9", -0.0003, root)
    props.txt(name + "_100", "100", 0.034, AZUL_ES, (w / 2 - 0.03, -0.0008, -0.002), root, ink=None)
    props.txt(name + "_100p", "100", 0.012, AZUL_ES, (-w / 2 + 0.072, -0.0008, h / 2 - 0.016), root, ink=None)
    props.txt(name + "_bc", "BANCO CENTRAL DO BRASIL", 0.0058, AZUL_TINTA, (0.012, -0.0008, h / 2 - 0.011), root, ink=None)
    props.txt(name + "_re", "REAIS", 0.008, AZUL_TINTA, (w / 2 - 0.03, -0.0008, -h / 2 + 0.008), root, ink=None)
    return root