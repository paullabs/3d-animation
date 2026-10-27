"""Renderiza a animação de "os passos" (anim_passos.py) em paralelo, um plano por processo, e monta o vídeo com a voz.
python3 anim_passos_rodar.py PASTA [ID ...] [--scale 0.5] [--samples 10] [--jobs 8] [--teste] [--video saida.mp4]
--teste: o primeiro, o do meio e o último quadro de cada plano numa folha (PASTA/teste.png).
Sem IDs usa todos os planos do story_passos2. O vídeo junta os quadros de PASTA/<id>/ na ordem do filme e põe a voz roteiros/voz-passos/narracao.wav."""
import os, sys, subprocess, glob, re
from concurrent.futures import ThreadPoolExecutor
from PIL import Image, ImageDraw, ImageFont
AQUI = os.path.dirname(os.path.abspath(__file__))
BL = __import__("canal38_env").BLENDER
VOZ = os.path.join(AQUI, "..", "roteiros", "voz-passos", "narracao.wav")
a = sys.argv[1:]
opt = lambda n, d: a[a.index(n) + 1] if n in a else d
pasta = a[0]; teste = "--teste" in a
VAL = ("--scale", "--samples", "--jobs", "--video", "--mix")
ids = [x for i, x in enumerate(a[1:], 1) if not x.startswith("--") and a[i - 1] not in VAL]
esc, smp, jobs = opt("--scale", "0.5"), opt("--samples", "10"), int(opt("--jobs", "8"))
os.makedirs(pasta, exist_ok=True)
lst = subprocess.run([BL, "-b", "-P", f"{AQUI}/story_passos4.py", "--", "--list"], capture_output=True, text=True, cwd=AQUI).stdout
TODOS = [l.split(" | ")[0] for l in lst.splitlines() if re.match(r"^\d+[A-Z]+ \| ", l)]
ids = ids or TODOS


def um(i):
    cmd = [BL, "-b", "-P", f"{AQUI}/anim_passos4.py", "--", i, pasta, "--scale", esc, "--samples", smp]
    if teste:
        cmd += ["--quadros", "1,M,N"]
    r = subprocess.run(cmd, capture_output=True, text=True, cwd=AQUI)
    ok = ("OK " + i + " ") in r.stdout
    if not ok:
        print("FALHOU", i); print("\n".join((r.stdout + r.stderr).splitlines()[-16:]))
    return i, ok


with ThreadPoolExecutor(jobs) as ex:
    res = list(ex.map(um, ids))
print("ok:", " ".join(i for i, o in res if o)); print("falhou:", " ".join(i for i, o in res if not o))
if teste:
    lin = [(i, sorted(glob.glob(f"{pasta}/{i}/q*.png"))) for i, o in res if o]
    w, h = 180, 320
    cols = 3; per = 6
    for pg in range(0, len(lin), per):
        bloco = lin[pg:pg + per]
        sheet = Image.new("RGB", (8 + 2 * (cols * (w + 4) + 40), 8 + 3 * (h + 8)), (30, 34, 30)); d = ImageDraw.Draw(sheet)
        f = ImageFont.truetype("/System/Library/Fonts/Menlo.ttc", 16)
        for r_, (i, fs) in enumerate(bloco):
            x0 = 8 + (r_ % 2) * (cols * (w + 4) + 40); y0 = 8 + (r_ // 2) * (h + 8)
            d.text((x0, y0), i, font=f, fill=(230, 190, 110))
            for c, fp in enumerate(fs[:3]):
                sheet.paste(Image.open(fp).convert("RGB").resize((w, h)), (x0 + 40 + c * (w + 4), y0))
        sheet.save(f"{pasta}/teste{pg // per + 1}.png")
    print("folhas", f"{pasta}/teste*.png")
elif "--video" in a:
    lista = os.path.join(pasta, "lista.txt")
    with open(lista, "w") as L:
        for i in TODOS:
            for fp in sorted(glob.glob(f"{pasta}/{i}/[0-9]*.png")):
                L.write(f"file '{os.path.abspath(fp)}'\nduration {1/24:.6f}\n")
    out = opt("--video", "")
    audio = opt("--mix", VOZ)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lista, "-i", audio,
                    "-r", "24", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", "-vf", "scale=1080:1920:flags=lanczos",
                    "-c:a", "aac", "-b:a", "192k", "-shortest", out], check=True)
    print("video", out)
