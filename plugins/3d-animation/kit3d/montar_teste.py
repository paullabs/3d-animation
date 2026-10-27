"""Monta só os trechos já renderizados (para aprovar um pedaço antes do vídeo todo): cor de cada plano, texto por cima e a
narração do mesmo tempo. Trechos seguidos viram um bloco; blocos separados são emendados com 0,4 s de preto.
python3 montar_teste.py --dir ../render_pcc2/s0.5 --ov ../render_pcc2/overlay.mov --out ../personagem/pcc/teste.mp4"""
import json, os, subprocess, sys

FPS = 24
a = sys.argv[1:]
arg = lambda n, d=None: a[a.index(n) + 1] if n in a else d
D = os.path.abspath(arg("--dir")); ov = os.path.abspath(arg("--ov")); out = os.path.abspath(arg("--out"))
audio = arg("--audio", os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "roteiros", "voz-pcc", "narracao.wav"))
k = float(arg("--scale", "0.5"))
shots = json.load(open(os.path.join(D, "planos.json")))
ordem = sorted(shots, key=lambda n: shots[n][0])


def post():
    if "--limpo" in a:                                       # sem bloom, ruído nem vinheta: a imagem sai com o contraste que o render deu (só uma curva em S leve)
        return "curves=all='0/0.02 0.25/0.22 0.5/0.52 0.78/0.82 1/1',eq=saturation=1.05,format=yuv420p"
    s = lambda v: f"{v * k:.1f}"
    return (f"format=gbrp,split[a][b];[b]curves=all='0/0 0.55/0 1/1',gblur=sigma={s(20)}[g];[a][g]blend=all_mode=screen:all_opacity=0.5,"
            "curves=all='0/0.02 0.25/0.215 0.5/0.52 0.78/0.83 1/1',eq=saturation=1.08,vignette=angle=PI/6,noise=alls=4:allf=t,format=yuv420p")      # curva em S leve: mais contraste sem esmagar as sombras


tmp = os.path.join(D, "_teste"); os.makedirs(tmp, exist_ok=True)

# borrão de movimento só nos quadros vizinhos de um corte em movimento (transicao.py):
# --borrao "a1:fim:v:290:6,a2:inicio:v:290:6" = plano:lado:direção (v/h):pixels no pico (em 1080x1920):quadros
BORRAO = {}
for item in (arg("--borrao", "") or "").split(","):
    if item:
        n_, lado, dr, px, nq = item.split(":"); BORRAO.setdefault(n_, []).append((lado, dr, float(px), int(nq)))


def borrar(src, dst, L, dr):
    """média de cópias deslocadas ao longo do movimento (borrão direcional), L em pixels deste tamanho de quadro"""
    import numpy as np
    from PIL import Image
    im = np.asarray(Image.open(src).convert("RGB")).astype(np.float32)
    n = max(2, int(L / 3)); acc = np.zeros_like(im)
    for i in range(n):
        d = int(round(-L / 2 + L * i / (n - 1)))
        acc += np.roll(im, d, axis=0 if dr == "v" else 1)
    Image.fromarray((acc / n).clip(0, 255).astype(np.uint8)).save(dst)


def quadros(n, f0, f1):
    """pasta com os quadros do plano; se houver borrão, cópia com os quadros do corte borrados"""
    src = os.path.join(D, n)
    if n not in BORRAO:
        return src
    import shutil
    dst = os.path.join(tmp, "q_" + n); os.makedirs(dst, exist_ok=True)
    for f in range(f0, f1 + 1):
        shutil.copyfile(os.path.join(src, f"f_{f:04d}.png"), os.path.join(dst, f"f_{f:04d}.png"))
    for lado, dr, px, nq in BORRAO[n]:
        for i in range(nq):
            f = f1 - i if lado == "fim" else f0 + i
            peso = (nq - i) / nq                                     # o pico de velocidade fica colado no corte
            borrar(os.path.join(src, f"f_{f:04d}.png"), os.path.join(dst, f"f_{f:04d}.png"), px * k * peso, dr)
    return dst
blocos = []
for n in ordem:
    f0, f1 = shots[n]
    if blocos and blocos[-1][-1][2] + 1 == f0:
        blocos[-1].append((n, f0, f1))
    else:
        blocos.append([(n, f0, f1)])
partes = []
for bi, bl in enumerate(blocos):
    segs = []
    for n, f0, f1 in bl:
        seg = os.path.join(tmp, f"{n}.mp4")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS), "-start_number", str(f0), "-i", os.path.join(quadros(n, f0, f1), "f_%04d.png"),
                        "-frames:v", str(f1 - f0 + 1), "-vf", post(), "-c:v", "libx264", "-crf", arg("--crf-seg", "14"), "-pix_fmt", "yuv420p", "-r", str(FPS), seg], check=True)
        segs.append(seg)
    lst = os.path.join(tmp, f"b{bi}.txt"); open(lst, "w").write("".join(f"file '{p}'\n" for p in segs))
    base = os.path.join(tmp, f"b{bi}_base.mp4")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", base], check=True)
    fa, fb = bl[0][1], bl[-1][2]
    t0, dur = (fa - 1) / FPS, (fb - fa + 1) / FPS
    parte = os.path.join(tmp, f"b{bi}.mp4")
    fc = "[0:v]scale=1080:1920:flags=lanczos[b];[1:v]setpts=PTS-STARTPTS[o];[b][o]overlay=format=auto,format=yuv420p[v];[2:a]asetpts=PTS-STARTPTS,afade=t=in:d=0.03,afade=t=out:st=%.3f:d=0.05[aa]" % (dur - 0.05)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", base, "-ss", f"{t0:.4f}", "-t", f"{dur:.4f}", "-i", ov, "-ss", f"{t0:.4f}", "-t", f"{dur:.4f}", "-i", audio,
                    "-filter_complex", fc, "-map", "[v]", "-map", "[aa]", "-c:v", "libx264", "-crf", arg("--crf-seg", "18"), "-c:a", "aac", "-b:a", "256k", "-ar", "48000", "-t", f"{dur:.4f}", parte], check=True)
    partes.append(parte)
    if bi < len(blocos) - 1:
        preto = os.path.join(tmp, f"preto{bi}.mp4")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i", f"color=c=black:s=1080x1920:r={FPS}:d=0.4", "-f", "lavfi", "-i", "anullsrc=r=48000:cl=mono",
                        "-t", "0.4", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", preto], check=True)
        partes.append(preto)
lst = os.path.join(tmp, "partes.txt"); open(lst, "w").write("".join(f"file '{p}'\n" for p in partes))
os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst, "-c:v", "libx264", "-crf", arg("--crf-final", "19"), "-preset", arg("--preset-final", "medium"), "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", arg("--audio-kbps", "192") + "k", out], check=True)
print("ok", out, [(b[0][0], b[-1][0]) for b in blocos])