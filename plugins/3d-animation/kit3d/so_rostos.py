"""Grava só o rostos.json das cenas (monta cada cena sem renderizar), para quando o render já existe.
blender -b -P so_rostos.py -- PROD PASTA_RENDER [cena1,cena2]"""
import sys, os, importlib
a = sys.argv[sys.argv.index("--") + 1:]
prod, pasta = a[0], a[1]
so = a[2].split(",") if len(a) > 2 else None
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy, lib
import prod_pcc4 as P4
sys.argv = [sys.argv[0], "--", "x", "x", "--list"]
importlib.import_module(prod.replace(".py", ""))
for nome, (t0, t1, fn) in list(P4.CENAS.items()):
    if so and nome not in so:
        continue
    lib.reset(108, 192, P4.FPS, 1); sc = lib.scene
    c = dict(sc=sc, f0=P4.F(t0), f1=P4.F(t1) - 1, t0=t0, t1=t1, F=P4.F)
    sys.argv = [sys.argv[0], "--", nome, os.path.join(pasta, nome)]
    fn(c)
