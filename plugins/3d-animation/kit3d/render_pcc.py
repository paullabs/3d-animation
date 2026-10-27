"""Renderiza os planos do PCC em paralelo.
python3 render_pcc.py [--scale 0.5] [--samples 8] [--jobs 4] [--only n1,n2a] [--out DIR]"""
import subprocess, sys, os, time, json
from concurrent.futures import ThreadPoolExecutor

KIT = os.path.dirname(os.path.abspath(__file__))
BLENDER = __import__("canal38_env").BLENDER
a = sys.argv[1:]
arg = lambda n, d=None: a[a.index(n) + 1] if n in a else d
PROD = arg("--prod", "prod_pcc.py"); scale = float(arg("--scale", "0.5")); samples = int(arg("--samples", "8")); jobs = int(arg("--jobs", "4"))
out = arg("--out", os.path.join(KIT, "..", "render_pcc", f"s{scale:g}"))
lista = subprocess.check_output([BLENDER, "-b", "--factory-startup", "--python", os.path.join(KIT, PROD), "--", "x", "x", "--list"], stderr=subprocess.DEVNULL).decode()
shots = {}
for ln in lista.splitlines():
    p = ln.split()
    if len(p) >= 5 and p[0] != "Blender" and "-" in p[1]:
        shots[p[0]] = (int(p[-1].split("-")[0]), int(p[-1].split("-")[1]))
only = arg("--only")
names = [n for n in shots if (not only or n in only.split(","))]
os.makedirs(out, exist_ok=True)


def run(n):
    d = os.path.join(out, n); os.makedirs(d, exist_ok=True)
    f0, f1 = shots[n]
    have = len([f for f in os.listdir(d) if f.startswith("f_")])
    if have >= f1 - f0 + 1 and "--force" not in a:
        return n, 0.0, "pronto"
    for f in os.listdir(d):
        os.remove(os.path.join(d, f))
    t = time.time()
    r = subprocess.run([BLENDER, "-b", "--factory-startup", "--python", os.path.join(KIT, PROD), "--", n, d, "--scale", str(scale), "--samples", str(samples)],
                       capture_output=True, text=True)
    ok = len([f for f in os.listdir(d) if f.startswith("f_")])
    return n, time.time() - t, f"{ok}/{f1 - f0 + 1} quadros" + ("" if ok == f1 - f0 + 1 else "  ERRO: " + r.stdout[-600:] + r.stderr[-300:])


with ThreadPoolExecutor(jobs) as ex:
    for n, dt, msg in ex.map(run, names):
        print(f"{n:6s} {dt:6.1f}s  {msg}", flush=True)
json.dump(shots, open(os.path.join(out, "planos.json"), "w"))
