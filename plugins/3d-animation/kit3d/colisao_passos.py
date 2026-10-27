"""Conferência de colisão do storyboard v2 de "os passos" (pedido de 25/10/2026: "melhorar as colisões").
Para cada plano, com a cena montada e SEM renderizar:
  1. COLISÃO: peça a peça (malha contra malha, BVH) entre o corpo de cada boneco e todo o resto que é sólido (prédios, carros, poste, ônibus, ondas, anéis, Lua...);
     entre dois bonecos também. Chão, céu, sombras, poeira e fantasmas não contam.
  2. TEXTO CORTADO: número ou rótulo que sai do quadro (margem de 3%).
  3. TEXTO SOBRE CORPO: número que cai em cima de uma peça do corpo (caixa na tela de peças grandes do corpo, para não acusar o braço esticado em diagonal).
  4. TEXTO SOBRE TEXTO.
Imprime uma linha por problema e "OK <plano>" se não achar nenhum. Uso: blender -b -P story_passos2.py -- PLANO x.png --colisao"""
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from bpy_extras.object_utils import world_to_camera_view

FORA = ("rf", "sb", "sg", "seta", "vaso_vazio", "poeira", "dust", "chao", "domo", "palco", "neblina", "fant", "est", "areia", "cidade_chao", "lago", "avenida", "mar", "campo", "halo",
        "sombra", "ceu", "fundo", "pt", "mk", "linha", "fio_luz", "dist", "chave", "r2_", "ref_", "fita", "risco", "regua", "reg", "fant_pt", "serra", "asfalto", "faixa_",
        "calcada", "meiofio", "corpo_dummy", "dummy", "pulso", "fluxo", "vaso", "coracao", "cor_", "mangueira", "atm", "refl", "fio_solto", "palito", "nuv", "fq")
GRUPOS = ("eu", "moca", "zel", "limp", "eu1", "eu2", "amigo")


def _grupo(o):
    n = o.name
    p = n.split("_")[0]
    return p if p in GRUPOS or (p.startswith("eu") and p[2:].isdigit()) else None


def _solido(o):
    n = o.name.lower()
    return o.type == "MESH" and not o.hide_render and not any(n.startswith(x) or ("_" + x) in n for x in FORA)


def confere(nome, margem=0.03, mostrar=12):
    sc = bpy.context.scene
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    malhas = [o for o in bpy.data.objects if o.type == "MESH" and not o.hide_render]
    corpos = {}
    for o in malhas:
        g = _grupo(o)
        if g and "fant" not in o.name and "contorno" not in o.name and not o.name.endswith("_sb"):
            corpos.setdefault(g, []).append(o)
    outros = [o for o in malhas if _solido(o) and _grupo(o) is None]
    achados = []

    def bvh(o):
        """árvore de triângulos no ESPAÇO DO MUNDO (o FromObject usa o espaço local do objeto, que faz peças de lugares diferentes parecerem coladas)"""
        ev = o.evaluated_get(dg)
        me = ev.to_mesh()
        mw = o.matrix_world
        verts = [mw @ v.co for v in me.vertices]
        polys = [tuple(p.vertices) for p in me.polygons]
        tree = BVHTree.FromPolygons(verts, polys)
        ev.to_mesh_clear()
        return tree

    def caixa(o):
        pts = [o.matrix_world @ Vector(c) for c in o.bound_box]
        return Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts))), Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))

    def toca(a, b):
        (a0, a1), (b0, b1) = caixa(a), caixa(b)
        return all(a0[i] < b1[i] and a1[i] > b0[i] for i in range(3))

    arvores = {}
    for g, partes in corpos.items():
        # só as peças "de volume" do boneco (não o rosto: olho, boca e sobrancelha encostam de propósito na cabeça)
        for p in partes:
            if any(k in p.name for k in ("olho", "palpebra", "sobr", "boca", "ziper", "bolso", "cabelo", "barba", "bigode", "bone", "tranca", "tiara")):
                continue
            for q in outros:
                if toca(p, q):
                    ta = arvores.setdefault(p.name, bvh(p)); tb = arvores.setdefault(q.name, bvh(q))
                    par = ta.overlap(tb)
                    if len(par) > 6:
                        achados.append((g, q.name + f' [{p.name}]', len(par)))
    gs = list(corpos)
    for i in range(len(gs)):
        for j in range(i + 1, len(gs)):
            n = 0
            for p in corpos[gs[i]]:
                if any(k in p.name for k in ("olho", "palpebra", "sobr", "boca", "ziper", "bolso", "cabelo")):
                    continue
                for q in corpos[gs[j]]:
                    if toca(p, q):
                        n += len(arvores.setdefault(p.name, bvh(p)).overlap(arvores.setdefault(q.name, bvh(q))))
            if n > 6:
                achados.append((gs[i], gs[j], n))
    vistos = set(); linhas = []
    for a, b, n in achados:
        chave = (a, b.split("_")[0] if isinstance(b, str) else b)
        if chave in vistos:
            continue
        vistos.add(chave); linhas.append(f"COLISÃO {a} ~ {b} ({n} faces)")

    cam = sc.camera
    def retangulo(o):
        pts = [world_to_camera_view(sc, cam, o.matrix_world @ Vector(c)) for c in o.bound_box]
        return min(p.x for p in pts), min(p.y for p in pts), max(p.x for p in pts), max(p.y for p in pts), min(p.z for p in pts)
    textos = [o for o in bpy.data.objects if o.type == "FONT" and not o.hide_render and not any(k in o.name for k in ("_placa", "_dest", "_pt", "_h")) and not o.name.startswith("rf")]   # (as réguas que ficam no chão são cenário: ficam atrás dele)
    rt = {}
    for t in textos:
        x0, y0, x1, y1, z = retangulo(t)
        if z <= 0 or (x1 - x0) < 0.004:                                  # rótulo ainda sem escala (vai nascer): não conta
            continue
        rt[t.name] = (x0, y0, x1, y1, t.data.body)
        if x0 < margem or x1 > 1 - margem or y0 < margem or y1 > 1 - margem:
            if x1 > 0 and x0 < 1 and y1 > 0 and y0 < 1:
                linhas.append(f"TEXTO CORTADO '{t.data.body}' (x {x0:.2f}..{x1:.2f}, y {y0:.2f}..{y1:.2f})")
    grandes = []
    for g, partes in corpos.items():
        for p in partes:
            if any(k in p.name for k in ("jaqueta", "cranio", "coxa", "canela", "braco", "antebraco", "sapato", "pelve", "mao")):
                grandes.append((g, p.name) + retangulo(p)[:4])
    for nm, (x0, y0, x1, y1, corpo) in rt.items():
        for g, pn, a0, b0, a1, b1 in grandes:
            if x0 < a1 and x1 > a0 and y0 < b1 and y1 > b0 and (min(x1, a1) - max(x0, a0)) * (min(y1, b1) - max(y0, b0)) > 0.0006:
                linhas.append(f"TEXTO SOBRE CORPO '{corpo}' ~ {g}/{pn}")
                break
    nomes = list(rt)
    for i in range(len(nomes)):
        for j in range(i + 1, len(nomes)):
            a, b = rt[nomes[i]], rt[nomes[j]]
            if a[0] < b[2] and a[2] > b[0] and a[1] < b[3] and a[3] > b[1] and (min(a[2], b[2]) - max(a[0], b[0])) * (min(a[3], b[3]) - max(a[1], b[1])) > 0.0004:
                linhas.append(f"TEXTO SOBRE TEXTO '{a[4]}' ~ '{b[4]}'")
    if linhas:
        for l in linhas[:mostrar]:
            print(f"{nome}: {l}")
    else:
        print(f"OK {nome}")
