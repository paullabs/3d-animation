"""Renderiza planos do storyboard v3 em paralelo e monta uma folha de contato para conferir.
python3 story3_rodar.py PASTA [ID ID ...] [--scale 0.5] [--samples 16] [--jobs 6] [--folha folha.png] [--colunas 6]
Sem IDs, renderiza todos. CCTV: aplica pos_cctv no quadro (os planos marcados no SHOTS)."""
import os, sys, subprocess, re
from concurrent.futures import ThreadPoolExecutor
from PIL import Image, ImageDraw, ImageFont
AQUI = os.path.dirname(os.path.abspath(__file__))
BL = __import__("canal38_env").BLENDER
a = sys.argv[1:]
pasta = a[0]
opt = lambda n, d: a[a.index(n) + 1] if n in a else d
esc, smp, jobs, folha, cols = opt("--scale", "0.5"), opt("--samples", "16"), int(opt("--jobs", "6")), opt("--folha", ""), int(opt("--colunas", "6"))
ids = [x for i, x in enumerate(a[1:], 1) if not x.startswith("--") and a[i - 1] not in ("--scale", "--samples", "--jobs", "--folha", "--colunas")]
os.makedirs(pasta, exist_ok=True)
if not ids:
    out = subprocess.run([BL, "-b", "-P", f"{AQUI}/story3_abrigo.py", "--", "--list"], capture_output=True, text=True, cwd=AQUI).stdout
    ids = [l.split(" | ")[0] for l in out.splitlines() if re.match(r"^\d+[A-Z]+ \| ", l)]


def um(i):
    dst = f"{pasta}/{i}.png"
    r = subprocess.run([BL, "-b", "-P", f"{AQUI}/story3_abrigo.py", "--", i, dst, "--scale", esc, "--samples", smp], capture_output=True, text=True, cwd=AQUI)
    ok = os.path.exists(dst)
    if ok and os.path.exists(dst + ".cctv"):
        import json
        c = json.load(open(dst + ".cctv")); os.remove(dst + ".cctv")
        subprocess.run(["python3", f"{AQUI}/pos_cctv.py", dst, dst, "--cam", c["cam"], "--dia", str(c["dia"]), "--hora", c["hora"]], capture_output=True)
    if not ok:
        print("FALHOU", i); print("\n".join((r.stdout + r.stderr).splitlines()[-14:]))
    return i, ok


with ThreadPoolExecutor(jobs) as ex:
    res = list(ex.map(um, ids))
print("ok:", " ".join(i for i, o in res if o)); print("falhou:", " ".join(i for i, o in res if not o))
if folha:
    ims = [(i, Image.open(f"{pasta}/{i}.png").convert("RGB")) for i, o in res if o]
    w, h = 300, 533
    lin = (len(ims) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * (w + 8) + 8, lin * (h + 30) + 8), (30, 34, 30)); d = ImageDraw.Draw(sheet)
    f = ImageFont.truetype("/System/Library/Fonts/Menlo.ttc", 18)
    for k, (i, im) in enumerate(ims):
        x, y = 8 + (k % cols) * (w + 8), 8 + (k // cols) * (h + 30)
        sheet.paste(im.resize((w, h)), (x, y + 24)); d.text((x, y), i, font=f, fill=(230, 190, 110))
    sheet.save(folha); print("folha", folha, sheet.size)
