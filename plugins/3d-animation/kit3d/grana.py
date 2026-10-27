"""Dinheiro verde em volume (pedido do usuário: "o dinheiro tem que ser verde" e "mostrar em volume").
Tudo em 3D de verdade (a câmera horizontal enxerga o tampo das coisas abaixo do olho) com cor chapada:
- nota: a cédula de frente (para leque e close)
- maco: o maço deitado: frente com as folhas e a cinta de papel, tampo com a cédula
- bloco: muitos maços num bloco reto (só as faces que aparecem: a frente da fileira da frente e o tampo da camada de cima)
Medidas reais: cédula 15,6 x 7 cm; maço de 100 cédulas com ~1,1 cm de altura."""
import math
import numpy as np
import bpy
import lib
from lib import empty, key
import cena, props
from char2d import rrect
from puppet2d import circle

W, D, T = 0.156, 0.070, 0.011                   # largura, fundo, altura de um maço
VERDE, VERDE_ES, VERDE_CL, VERDE_LUZ = "#4c9a62", "#2c6a40", "#a6d9ae", "#7cc28c"
FOLHAS, FOLHAS_LIN, LADO = "#b9dcb4", "#7db488", "#8fbf93"
CINTA, CINTA_ES = "#efe6cf", "#c4b38c"


def _face(w, h):
    """desenho da cédula em 2D (origem no centro): [(polígono, cor)] de trás para a frente"""
    r = min(w, h) * 0.08
    return [(rrect(-w / 2, -h / 2, w / 2, h / 2, r, 3), VERDE_ES),
            (rrect(-w / 2 + w * 0.025, -h / 2 + h * 0.06, w / 2 - w * 0.025, h / 2 - h * 0.06, r * 0.7, 3), VERDE),
            (circle(0, 0, h * 0.3, 28), VERDE_CL),
            (circle(0, 0, h * 0.22, 28), VERDE_LUZ),
            (rrect(-w / 2 + w * 0.07, -h * 0.28, -w / 2 + w * 0.2, h * 0.28, r * 0.5, 2), VERDE_LUZ),
            (rrect(w / 2 - w * 0.2, -h * 0.28, w / 2 - w * 0.07, h * 0.28, r * 0.5, 2), VERDE_LUZ)]


def _malha(name, polys, mats_cores):
    """polys = [(lista de vértices 3D, cor)] -> uma malha com um material por cor"""
    cores = []
    for _, c in polys:
        if c not in cores:
            cores.append(c)
    verts, faces, mi = [], [], []
    n = 0
    for pts, c in polys:
        verts += pts; faces.append(tuple(range(n, n + len(pts)))); mi.append(cores.index(c)); n += len(pts)
    me = bpy.data.meshes.new(name); me.from_pydata(verts, [], faces)
    for c in cores:
        me.materials.append(props.FM(c))
    me.polygons.foreach_set("material_index", np.array(mi, dtype=np.int32)); me.update()
    o = bpy.data.objects.new(name, me); bpy.context.scene.collection.objects.link(o)
    return o


def nota(name, loc, s=1.0, parent=None):
    """cédula de frente (plano XZ), camadas cada vez mais perto da câmera"""
    polys = [([(x * s, -i * 0.0004, z * s) for x, z in pts], c) for i, (pts, c) in enumerate(_face(W, D))]
    o = _malha(name, polys, None); o.location = loc
    if parent:
        o.parent = parent
    return o


def _maco_polys(x, y, z, n=1, topo=True, frente=True, cinta=True, tk=T):
    """polígonos de uma pilha de n maços com o canto da frente-esquerda-baixo em (x, y, z)"""
    P = []
    h = n * tk
    if frente:                                   # frente: folhas com uma linha por maço e a cinta
        P.append(([(x, y, z), (x + W, y, z), (x + W, y, z + h), (x, y, z + h)], FOLHAS))
        for k in range(1, n):
            zz = z + k * tk
            P.append(([(x, y - 0.0003, zz - 0.0006), (x + W, y - 0.0003, zz - 0.0006), (x + W, y - 0.0003, zz + 0.0006), (x, y - 0.0003, zz + 0.0006)], FOLHAS_LIN))
        if cinta:
            cx0, cx1 = x + W * 0.42, x + W * 0.58
            P.append(([(cx0, y - 0.0006, z), (cx1, y - 0.0006, z), (cx1, y - 0.0006, z + h), (cx0, y - 0.0006, z + h)], CINTA))
    if frente:                                   # as laterais (só aparece a do lado oposto à câmera... a outra fica atrás da frente)
        for xx in (x, x + W):
            P.append(([(xx, y, z), (xx, y + D, z), (xx, y + D, z + h), (xx, y, z + h)], LADO))
    if topo:                                     # tampo: a cédula vista de cima (plano XY)
        for i, (pts, c) in enumerate(_face(W, D)):
            P.append(([(x + W / 2 + px, y + D / 2 + py, z + h + 0.0004 * (i + 1)) for px, py in pts], c))
        if cinta:
            cx0, cx1 = x + W * 0.42, x + W * 0.58
            P.append(([(cx0, y, z + h + 0.004), (cx1, y, z + h + 0.004), (cx1, y + D, z + h + 0.004), (cx0, y + D, z + h + 0.004)], CINTA))
    return P


def maco(name, loc, n=1, s=1.0, parent=None, zk=1.0):
    """um maço (ou uma pilha de n maços) deitado, origem no centro da base; zk engrossa o maço (cartum: o volume se lê de longe)"""
    root = empty(name, parent, loc); root.scale = (s, s, s)
    o = _malha(name + "_m", _maco_polys(-W / 2, -D / 2, 0.0, n, tk=T * zk), None); o.parent = root
    return root


def bloco(name, loc, cols, fundo, camadas, s=1.0, gap=0.004, parent=None, zk=1.0):
    """bloco reto de maços: cols na largura x fundo na profundidade x camadas de altura.
    Só as faces visíveis (frente da fileira da frente e tampo da camada de cima). Origem: centro da base, na frente."""
    root = empty(name, parent, loc); root.scale = (s, s, s)
    P = []
    larg = cols * (W + gap) - gap
    for i in range(cols):
        x = -larg / 2 + i * (W + gap)
        P += _maco_polys(x, 0.0, 0.0, camadas, topo=False, frente=True, tk=T * zk)
        for j in range(fundo):
            P += _maco_polys(x, j * (D + gap), (camadas - 1) * T * zk, 1, topo=True, frente=False, tk=T * zk)
    o = _malha(name + "_m", P, None); o.parent = root
    return root, larg


def cresce_bloco(root, f0, f1, curva="easy"):
    """o bloco sobe do chão (escala em z) seguindo a curva"""
    import curvas
    for f in range(f0 - 1, f1 + 1):
        u = min(1.0, max(0.0, (f - f0) / max(1, f1 - f0)))
        root.scale = (root.scale.x, root.scale.y, max(0.0001, curvas.s(curva, u)) * root.scale.x); key(root, "scale", f, "LINEAR")