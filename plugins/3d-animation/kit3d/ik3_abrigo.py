"""Cinemática inversa dos braços do Heroi3D (dois ossos, em matemática pura: sem atualizar a cena a cada tentativa).
Pedido de 25/10/2026: "o braço atravessa a mesa", "objeto entrando no outro". Os braços eram posados no olho (ombro, cotovelo) e a mão acabava dentro da
mesa ou longe do prato. Aqui a mão vai para um PONTO do mundo (o prato, a boca, o giz, a alça do galão) e o resultado vira os ângulos do boneco.
    alcanca(H, "F", ponto)               -> (ombro, abre, cotovelo, erro em metros)
    braco_pose(H, "F", ponto, base)      -> dict de pose (ombro, cotovelo, abre) com o outro braço da 'base' intacto
Convenção do Heroi3D: ombro e cotovelo negativos = para a frente; abre = para o lado (graus)."""
import math
import bpy
from mathutils import Vector, Matrix, Euler

OFF_MAO = (0.002, 0.0, -0.042)                      # o centro da mão redonda no sistema do punho
OFF_PEGA_F = (-0.004, -0.062, -0.03)                # o 'pega' do punho fechado (entre o polegar e o indicador)
OFF_PEGA_B = (0.004, -0.062, -0.03)


def _cadeia(H, s):
    bpy.context.view_layer.update()
    T = H.tronco.matrix_world.copy()
    o, c, w = H.ombro[s], H.cotovelo[s], H.punho[s]
    return T @ Matrix.Translation(o.location), Matrix.Translation(c.location), Matrix.Translation(w.location)


def ponto(H, s, ombro, abre, cotovelo, off=OFF_MAO, cad=None):
    """onde fica o ponto 'off' da mão, no mundo, com esses ângulos"""
    A, C, W = cad or _cadeia(H, s)
    sg = 1 if s == "F" else -1
    R = Euler((math.radians(ombro), math.radians(abre * sg), 0.0), "XYZ").to_matrix().to_4x4()
    Rc = Matrix.Rotation(math.radians(cotovelo), 4, "X")
    return A @ R @ C @ Rc @ W @ Vector(off)


def alcanca(H, s, alvo, off=OFF_MAO, abre=None, ombro_max=30.0, faixa_abre=(-70, 70)):
    """acha (ombro, abre, cotovelo) em graus que põem o ponto 'off' da mão em 'alvo' (mundo); abre = fixo, ou None para procurar.
    Devolve também o erro em metros (alvo fora do alcance: o braço estica na direção dele e o erro mostra a falta)"""
    alvo = Vector(alvo)
    cad = _cadeia(H, s)
    abres = [abre] if abre is not None else list(range(int(faixa_abre[0]), int(faixa_abre[1]) + 1, 5))
    melhor = (1e9, 0.0, 0.0, 0.0)
    for ox in range(-200, int(ombro_max) + 1, 5):
        for ab in abres:
            for cx in range(-150, -3, 5):
                d = (ponto(H, s, ox, ab, cx, off, cad) - alvo).length + 0.0004 * abs(ab)
                if d < melhor[0]:
                    melhor = (d, ox, ab, cx)
    d, ox, ab, cx = melhor
    passo = 4.0
    while passo > 0.1:                                                  # refina em volta do melhor
        achou = False
        for dox, dab, dcx in ((passo, 0, 0), (-passo, 0, 0), (0, passo, 0), (0, -passo, 0), (0, 0, passo), (0, 0, -passo)):
            if abre is not None and dab:
                continue
            nx, na, nc = ox + dox, min(faixa_abre[1], max(faixa_abre[0], ab + dab)), min(-3.0, cx + dcx)
            dd = (ponto(H, s, nx, na, nc, off, cad) - alvo).length + 0.0004 * abs(na)
            if dd < d - 1e-6:
                d, ox, ab, cx, achou = dd, nx, na, nc, True
        if not achou:
            passo /= 2
    erro = (ponto(H, s, ox, ab, cx, off, cad) - alvo).length
    return ox, ab, cx, erro


def braco_pose(H, s, alvo, base=None, off=OFF_MAO, abre=None, aviso=0.03, nome="", faixa_abre=(-70, 70)):
    """dict de pose com o braço 's' no alvo e o outro braço como está em 'base' (por padrão a última pose do boneco)"""
    base = dict(base if base is not None else getattr(H, "_ultima", {}))
    ox, ab, cx, erro = alcanca(H, s, alvo, off, abre, faixa_abre=faixa_abre)
    import os
    if os.environ.get("IK_DEBUG"):
        print(f"IKD {nome or H.nome}.{s}: alvo {tuple(round(v, 2) for v in alvo)} ombro {ox:.0f} abre {ab:.0f} cot {cx:.0f} erro {erro * 100:.1f} cm")
    if erro > aviso:
        print(f"IK {nome or H.nome}.{s}: falta {erro * 100:.1f} cm até o alvo {tuple(round(v, 2) for v in alvo)}")
    i = 0 if s == "F" else 1
    for k, v in (("ombro", ox), ("abre", ab), ("cotovelo", cx)):
        t = list(base.get(k, (0.0, 0.0)))
        t[i] = v; base[k] = tuple(t)
    return base


def boca_de(H):
    """o ponto da boca no mundo (o centro da caixa do objeto da boca)"""
    bpy.context.view_layer.update()
    b = H.boca
    pts = [b.matrix_world @ Vector(c) for c in b.bound_box]
    return sum(pts, Vector()) / len(pts)


def cabeca_de(H):
    bpy.context.view_layer.update()
    return H.cabeca.matrix_world @ Vector((0, 0, H.R))
