"""Renderiza a animação de "O abrigo" (anim3_abrigo.py) em paralelo, um plano por processo, e monta o vídeo com a voz.
python3 anim3_rodar.py PASTA ID [ID ...] [--scale 0.5] [--samples 10] [--jobs 5] [--teste] [--video saida.mp4] [--t0 0 --t1 14.3]
--teste: só o primeiro, o do meio e o último quadro de cada plano, numa folha (PASTA/teste.png)."""
import os, sys, subprocess, glob
from concurrent.futures import ThreadPoolExecutor
from PIL import Image, ImageDraw, ImageFont
AQUI = os.path.dirname(os.path.abspath(__file__))
BL = __import__("canal38_env").BLENDER
VOZ = os.path.join(AQUI, "..", "roteiros", "voz-abrigo", "narracao.wav")
a = sys.argv[1:]
opt = lambda n, d: a[a.index(n) + 1] if n in a else d
pasta = a[0]; teste = "--teste" in a
VAL = ("--scale", "--samples", "--jobs", "--video", "--t0", "--t1")
ids = [x for i, x in enumerate(a[1:], 1) if not x.startswith("--") and a[i - 1] not in VAL]
esc, smp, jobs = opt("--scale", "0.5"), opt("--samples", "10"), int(opt("--jobs", "5"))
os.makedirs(pasta, exist_ok=True)


def um(i):
    cmd = [BL, "-b", "-P", f"{AQUI}/anim3_abrigo.py", "--", i, pasta, "--scale", esc, "--samples", smp]
    if teste:
        cmd += ["--quadros", "1,M,N"]
    r = subprocess.run(cmd, capture_output=True, text=True, cwd=AQUI)
    ok = ("OK " + i) in r.stdout
    if not ok:
        print("FALHOU", i); print("\n".join((r.stdout + r.stderr).splitlines()[-18:]))
    return i, ok


with ThreadPoolExecutor(jobs) as ex:
    res = list(ex.map(um, ids))

# câmera de segurança (7B, 7D, 8B): o visual de CCTV quadro a quadro, com o relógio andando (o Blender não tem PIL)
import json, tempfile
tj = tempfile.mktemp(suffix=".json")
subprocess.run([BL, "-b", "-P", f"{AQUI}/story3_abrigo.py", "--", "--json", tj], capture_output=True, cwd=AQUI)
META = json.load(open(tj)) if os.path.exists(tj) else {}


def cctv(i):
    c = META.get(i, {}).get("cctv")
    if not c:
        return
    h, m, s_ = map(int, c["hora"].split(":"))
    for fp in sorted(glob.glob(f"{pasta}/{i}/[0-9]*.png")) + sorted(glob.glob(f"{pasta}/{i}/q*.png")):
        f = int(os.path.basename(fp).strip("q").split(".")[0]); t = h * 3600 + m * 60 + s_ + (f - 1) // 24
        hora = f"{t // 3600 % 24:02d}:{t // 60 % 60:02d}:{t % 60:02d}"
        subprocess.run(["python3", f"{AQUI}/pos_cctv.py", fp, fp, "--cam", c["cam"], "--dia", str(c["dia"]), "--hora", hora, "--quadro", str(f)], capture_output=True)


with ThreadPoolExecutor(jobs) as ex:
    list(ex.map(cctv, [i for i, o in res if o]))
print("ok:", " ".join(i for i, o in res if o)); print("falhou:", " ".join(i for i, o in res if not o))
if teste:
    lin = [(i, sorted(glob.glob(f"{pasta}/{i}/q*.png"))) for i, o in res if o]
    w, h = 180, 320
    sheet = Image.new("RGB", (8 + 3 * (w + 6) + 60, 8 + len(lin) * (h + 8)), (30, 34, 30)); d = ImageDraw.Draw(sheet)
    f = ImageFont.truetype("/System/Library/Fonts/Menlo.ttc", 16)
    for r_, (i, fs) in enumerate(lin):
        d.text((8, 8 + r_ * (h + 8)), i, font=f, fill=(230, 190, 110))
        for c, fp in enumerate(fs[:3]):
            sheet.paste(Image.open(fp).convert("RGB").resize((w, h)), (60 + c * (w + 6), 8 + r_ * (h + 8)))
    sheet.save(f"{pasta}/teste.png"); print("folha", f"{pasta}/teste.png")
elif "--video" in a:
    lista = os.path.join(pasta, "lista.txt")
    with open(lista, "w") as L:
        for i, o in res:
            for fp in sorted(glob.glob(f"{pasta}/{i}/[0-9]*.png")):
                L.write(f"file '{os.path.abspath(fp)}'\nduration {1/24:.6f}\n")
    t0, t1 = float(opt("--t0", "0")), float(opt("--t1", "14.3"))
    out = opt("--video", "")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lista, "-ss", str(t0), "-t", str(t1 - t0), "-i", VOZ,
                    "-r", "24", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", "-vf", "scale=1080:1920:flags=lanczos",
                    "-c:a", "aac", "-b:a", "192k", "-shortest", out], check=True)
    print("video", out)
