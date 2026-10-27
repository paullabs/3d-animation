"""Renderiza a animação da parte 2 de "O abrigo" em paralelo e monta o vídeo com a voz-teste.
python3 anim_abrigo2_rodar.py PASTA [ID ...] [--scale 0.5] [--samples 10] [--jobs 8] [--video saida.mp4] [--so-video]
PASTA/raw/<id>/NNNN.png (Blender), PASTA/graded/<id>/NNNN.png (com a luz do pós). Planos sem builder repetem o último quadro do anterior; 1M usa os quadros M1..M17 da pasta de storyboard."""
import os, sys, json, subprocess, shutil, re
from concurrent.futures import ThreadPoolExecutor
import numpy as np
from PIL import Image, ImageFilter

AQUI = os.path.dirname(os.path.abspath(__file__)); RAIZ = os.path.abspath(os.path.join(AQUI, ".."))
BL = __import__("canal38_env").BLENDER
a = sys.argv[1:]; pasta = os.path.abspath(a[0])
opt = lambda n, d: a[a.index(n) + 1] if n in a else d
esc, smp, jobs, video = opt("--scale", "0.5"), opt("--samples", "10"), int(opt("--jobs", "8")), opt("--video", None)
ids_arg = [x for i, x in enumerate(a[1:], 1) if not x.startswith("--") and a[i - 1] not in ("--scale", "--samples", "--jobs", "--video")]
PL = json.load(open(f"{RAIZ}/roteiros/abrigo2_planos.json")); ORDEM, META = PL["ordem"], PL["planos"]
lst = subprocess.run([BL, "-b", "-P", f"{AQUI}/story_abrigo2.py", "--", "--list"], capture_output=True, text=True).stdout.splitlines()
DESENHADOS = [l for l in lst if l.startswith("10A ")][-1].split()
GRADE = json.loads([l for l in lst if l.startswith("{")][-1])
src = open(f"{AQUI}/story_abrigo2_rodar.py").read()
exec(src[src.index("def arr(im)"):src.index("def estatica")])               # arr, img, vinheta, grade
STORY = os.path.abspath(opt("--story", f"{RAIZ}/personagem/abrigo/story_p2_final"))


def nq(i):
    m = META[i]; return round(m["t1"] * 24) - round(m["t0"] * 24)


def renderiza(i):
    n = nq(i); d = f"{pasta}/raw/{i}"
    pronto = os.path.isdir(d) and len([f for f in os.listdir(d) if f.endswith(".png")]) >= n
    if not pronto:
      subprocess.run([BL, "-b", "-P", f"{AQUI}/anim_abrigo2.py", "--", i, f"{pasta}/raw", "--scale", esc, "--samples", smp, "--n", str(n)], capture_output=True)
    ok = os.path.isdir(d) and len([f for f in os.listdir(d) if f.endswith(".png")]) >= n
    if ok:
        g = f"{pasta}/graded/{i}"; os.makedirs(g, exist_ok=True)
        for f in sorted(os.listdir(d)):
            if f.endswith(".png"):
                im = Image.open(f"{d}/{f}").convert("RGB")
                gk = GRADE.get(i) or ('cinza' if i != '1M' else None)
                im = grade(im, gk) if gk else im
                j = int(f[:4]) - 1
                if i == "5D":                                                  # a imagem fecha pelas bordas e pisca (íris), até o preto
                    k = 1.25 * max(0.0, 1 - j / max(1, n - 5)) ** 1.3
                    if j in (n // 3, n // 3 + 1):
                        k = min(1.4, k + 0.35)
                    x = arr(im); h_, w_ = x.shape[:2]; yy, xx = np.mgrid[0:h_, 0:w_]
                    dd = np.sqrt(((xx - w_ / 2) / (w_ / 2)) ** 2 + ((yy - h_ / 2) / (h_ / 2)) ** 2)
                    im = img(x * (dd < k)[..., None])
                elif i == "17C" and j >= n - 10:
                    im = img(arr(im) * max(0.0, (n - 1 - j) / 10.0))
                im.save(f"{g}/{f}")
    return i, ok


def monta():
    seq = f"{pasta}/seq"; shutil.rmtree(seq, ignore_errors=True); os.makedirs(seq)
    k = 0; ultimo = None
    M = [Image.open(f"{STORY}/M{j}.png").convert("RGB") for j in range(1, 18) if os.path.exists(f"{STORY}/M{j}.png")]
    for i in ORDEM:
        n = nq(i); g = f"{pasta}/graded/{i}"
        fr = sorted(os.listdir(g)) if os.path.isdir(g) else []
        for j in range(n):
            k += 1
            if i == "1M" and M:
                im = M[min(len(M) - 1, int(j * len(M) / n))]; im.save(f"{seq}/{k:06d}.png"); ultimo = f"{seq}/{k:06d}.png"; continue
            if fr:
                p = f"{g}/{fr[min(j, len(fr) - 1)]}"
            else:
                p = ultimo
            if p is None:
                continue
            os.symlink(os.path.abspath(p), f"{seq}/{k:06d}.png"); ultimo = p
    voz = f"{RAIZ}/roteiros/voz-abrigo2/teste/narracao.wav"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", "24", "-i", f"{seq}/%06d.png", "-i", voz, "-c:v", "libx264", "-crf", "17", "-pix_fmt", "yuv420p",
                    "-c:a", "aac", "-b:a", "192k", "-shortest", video])
    print("video", video, k, "quadros")


if "--so-video" not in a:
    alvo = [i for i in (ids_arg or ORDEM) if i in DESENHADOS]
    with ThreadPoolExecutor(jobs) as ex:
        for i, ok in ex.map(renderiza, alvo):
            print("ok" if ok else "FALHOU", i, flush=True)
if video:
    monta()
