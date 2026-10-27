"""Auditoria de direção de cena de "O abrigo" (pedido de 25/10/2026: "revise se eu apareço nas cenas ou em primeira pessoa; mais direções de cena quebradas"):
para cada plano diz QUEM aparece no quadro (a cabeça dentro da imagem) e se há mãos de POV; o narrador ('eu') tem de estar numa de duas formas:
corpo (de vermelho, no quadro) ou primeira pessoa (as mãos de manga vermelha, ou a câmera é ele). Plano de grupo sem nenhum dos dois = 'AUSENTE'.
blender -b -P audita_elenco.py -- PLANO     (imprime uma linha 'AUD plano: ...')"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy
from bpy_extras.object_utils import world_to_camera_view
import anim3_abrigo as A, lib

nome = sys.argv[sys.argv.index("--") + 1]
N = A.quadros(nome)
lib.reset(100, 180, 24, 2)
A.ST.SHOTS[nome]["fn"]()
if nome in A.ANIM:
    A.ANIM[nome](N)
sc = bpy.context.scene; cam = sc.camera
vis = {}
for f in (1, (N + 1) // 2, N):
    sc.frame_set(f); bpy.context.view_layer.update()
    for k, H in A.REG.items():
        try:
            p = H.cabeca.matrix_world @ __import__("mathutils").Vector((0, 0, H.R))
        except Exception:
            continue
        x, y, z = world_to_camera_view(sc, cam, p)
        if z > 0 and -0.02 <= x <= 1.02 and -0.02 <= y <= 1.02:
            vis[k] = vis.get(k, 0) + 1
maos = sorted({k.split("_")[0] for k in A.MAOS})
mv = 0
for k, m in A.MAOS.items():
    try:
        p = m.raiz.matrix_world.translation
        x, y, z = world_to_camera_view(sc, cam, p)
        if z > 0 and -0.1 <= x <= 1.1 and -0.1 <= y <= 1.1:
            mv += 1
    except Exception:
        pass
quem = sorted(k for k, v in vis.items() if v >= 1 and not k.startswith(("pv", "viz", "zumbi")))
mult = sum(1 for k in vis if k.startswith(("pv", "viz")))
print(f"AUD {nome}: quem={','.join(quem) or '-'}; multidão={mult}; maos_pov={'sim' if mv else 'não'}; eu={'CORPO' if 'eu' in vis else ('MÃOS' if mv else 'ausente')}")
