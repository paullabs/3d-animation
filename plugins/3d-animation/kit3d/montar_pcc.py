"""Monta o vídeo PCC: cor de cada plano, emenda, selos/legendas por cima e áudio.
python3 montar_pcc.py --scale 0.5 --out ../personagem/pcc/pcc_rascunho.mp4 [--audio mix.wav] [--sem-overlay]"""
import json, os, subprocess, sys

KIT = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(KIT, ".."))
FPS = 24
a = sys.argv[1:]
arg = lambda n, d=None: a[a.index(n) + 1] if n in a else d
scale = float(arg("--scale", "0.5"))
out = arg("--out", os.path.join(ROOT, "personagem", "pcc", "pcc_rascunho.mp4"))
audio = arg("--audio", os.path.join(ROOT, "roteiros", "voz-pcc", "narracao.wav"))
D = os.path.join(ROOT, "render_pcc", f"s{scale:g}")
shots = json.load(open(os.path.join(D, "planos.json")))
ordem = sorted(shots, key=lambda n: shots[n][0])
k = scale

# ---- cor por plano (bloom, balanço, vinheta, grão); o sigma do bloom acompanha a resolução
def post(kind):
    s = lambda v: f"{v * k:.1f}"
    bloom = lambda cut, sig, op: f"format=gbrp,split[a][b];[b]curves=all='0/0 {cut}/0 1/1',gblur=sigma={s(sig)}[g];[a][g]blend=all_mode=screen:all_opacity={op}"
    if kind == "manha":
        return bloom(0.62, 26, 0.5) + ",colorbalance=rs=0.02:bs=-0.03:rh=0.03:bh=-0.04,vignette=angle=PI/5,noise=alls=4:allf=t,format=yuv420p"
    if kind == "drama":
        return bloom(0.5, 22, 0.6) + ",colorbalance=bs=0.05:bm=0.02:rh=0.03,curves=all='0/0 0.25/0.18 0.75/0.8 1/1',vignette=angle=PI/4,noise=alls=6:allf=t,format=yuv420p"
    if kind == "gancho":
        return bloom(0.5, 22, 0.55) + ",colorbalance=bs=0.04:bm=0.02,vignette=angle=PI/4.5,noise=alls=5:allf=t,format=yuv420p"
    return bloom(0.7, 14, 0.25) + ",vignette=angle=PI/5,noise=alls=3:allf=t,format=yuv420p"


MOOD = dict(h1a="gancho", cela="drama", p2="drama", p1="drama", h3="drama", n5b="info", n5c2="info")
tmp = os.path.join(D, "_seg"); os.makedirs(tmp, exist_ok=True)
lista = []
for n in ordem:
    f0, f1 = shots[n]
    seg = os.path.join(tmp, f"{n}.mp4")
    if not os.path.exists(seg) or os.path.getmtime(seg) < os.path.getmtime(os.path.join(D, n, f"f_{f0:04d}.png")):
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS), "-start_number", str(f0), "-i", os.path.join(D, n, "f_%04d.png"),
                        "-frames:v", str(f1 - f0 + 1), "-vf", post(MOOD.get(n, "manha")), "-c:v", "libx264", "-crf", "12", "-preset", "medium",
                        "-pix_fmt", "yuv420p", "-r", str(FPS), seg], check=True)
    lista.append(seg)
open(os.path.join(tmp, "lista.txt"), "w").write("".join(f"file '{p}'\n" for p in lista))
base = os.path.join(tmp, "base.mp4")
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", os.path.join(tmp, "lista.txt"), "-c", "copy", base], check=True)

os.makedirs(os.path.dirname(out), exist_ok=True)
ov = os.path.join(ROOT, "render_pcc", "overlay.mov")
if "--sem-overlay" not in a:
    if not os.path.exists(ov) or "--refaz-overlay" in a:
        subprocess.run([sys.executable, os.path.join(KIT, "overlay_pcc.py"), ov], check=True)
    fc = f"[0:v]scale=1080:1920:flags=lanczos[b];[b][1:v]overlay=format=auto,format=yuv420p[v]"
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-i", base, "-i", ov, "-i", audio, "-filter_complex", fc, "-map", "[v]", "-map", "2:a",
           "-c:v", "libx264", "-crf", "16", "-preset", "medium", "-c:a", "aac", "-b:a", "192k", "-shortest", out]
else:
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-i", base, "-i", audio, "-vf", "scale=1080:1920:flags=lanczos", "-c:v", "libx264", "-crf", "16",
           "-preset", "medium", "-c:a", "aac", "-b:a", "192k", "-shortest", out]
subprocess.run(cmd, check=True)
print("ok", out)
