"""Onde estão os rostos na tela, quadro a quadro (pedido de 23/10/2026: "cuidado para as coisas não ficarem na frente do rosto,
texto e tudo mais"). Grava rostos.json ao lado dos quadros renderizados; o overlay lê e tira legenda, nível e contador da frente.
Também avisa CABEÇA CORTADA quando um rosto grande aparece só em parte no quadro (regra: ou o rosto inteiro, ou nenhum)."""
import json, math
import bpy
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view

MIN_ALT = 0.022           # rosto menor que isso (fração da altura do quadro, ~42 px) é figurante de fundo: não manda no texto


def cabecas():
    return [o for o in bpy.data.objects if o.type == "MESH" and o.name.endswith(("_head_o", "_cranio"))]      # contorno da cabeça (boneco e silhueta)


def camera_no_quadro(sc, f):
    ms = sorted([m for m in sc.timeline_markers if m.camera and m.frame <= f], key=lambda m: m.frame)
    return ms[-1].camera if ms else sc.camera


def visivel(o):
    p = o
    while p is not None:
        if p.hide_render or min(abs(v) for v in p.matrix_world.to_scale()) < 1e-4:
            return False
        p = p.parent
    return True


def caixa(sc, cam, o, folga=0.18):
    pts = [world_to_camera_view(sc, cam, o.matrix_world @ Vector(c)) for c in o.bound_box]
    if any(p.z <= 0 for p in pts):
        return None
    xs = [p.x for p in pts]; ys = [1 - p.y for p in pts]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    dx, dy = (x1 - x0) * folga, (y1 - y0) * folga
    return [x0 - dx, y0 - dy * 1.6, x1 + dx, y1 + dy]          # mais folga em cima (cabelo, chapéu, quepe)


def exporta(c, saida, passo=2):
    sc = c["sc"]; heads = cabecas(); out = {}; avisos = set()
    for f in range(c["f0"], c["f1"] + 1, passo):
        sc.frame_set(f); cam = camera_no_quadro(sc, f); lista = []
        for o in heads:
            if not visivel(o):
                continue
            b = caixa(sc, cam, o)
            if b is None or b[2] < 0 or b[0] > 1 or b[3] < 0 or b[1] > 1:
                continue
            if b[3] - b[1] < MIN_ALT:
                continue
            lista.append([round(v, 4) for v in b])
            corte = b[1] < -0.01 or b[0] < -0.01 or b[2] > 1.01
            dentro = max(0.0, min(b[3], 1) - max(b[1], 0)) / max(1e-6, b[3] - b[1])
            if corte and 0.05 < dentro < 0.85:
                avisos.add((o.name, cam.name))
        out[f] = lista
    json.dump(dict(passo=passo, quadros=out, cortadas=sorted(avisos)), open(saida, "w"))
    for nm, cn in sorted(avisos):
        print(f"CABEÇA CORTADA: {nm} na câmera {cn}")
    print(f"ROSTOS {len(out)} quadros -> {saida}")
    return avisos
