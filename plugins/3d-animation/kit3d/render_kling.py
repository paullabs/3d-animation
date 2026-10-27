"""Renderiza UM plano do blockout para o Kling 4.0 (pedido de 23/10/2026: "o vídeo vira o esqueleto da versão realista"):
- passe limpo (LIMPO=1: sem números, rótulos, anéis, ecos, poeira, cartão no ar nem filtro de tempo);
- só a câmera do plano, com folga antes e depois (o Kling precisa de material e o corte é feito depois, no quadro do blockout);
- 720x1280 (9:16), 24 qps; grava PNGs e um mp4 h264 pronto para subir.
blender -b -P render_kling.py -- PROD CENA CAMERA FOLGA_ANTES FOLGA_DEPOIS PASTA [--samples 16]
Imprime FAIXA quadro_ini quadro_fim corte_ini corte_fim (o trecho do plano dentro do clipe, em quadros do clipe)."""
import sys, os, importlib, subprocess

a = sys.argv[sys.argv.index("--") + 1:]
prod, nome, cam_nome = a[0], a[1], a[2]
h0, h1, pasta = int(a[3]), int(a[4]), a[5]
amostras = int(a[a.index("--samples") + 1]) if "--samples" in a else 16
os.environ["LIMPO"] = "1"
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy, lib
sys.argv = [sys.argv[0], "--", "x", "x", "--list"]
importlib.import_module(prod.replace(".py", ""))                       # o prod primeiro (régua de tempo certa)
import prod_pcc4 as P4
t0, t1, fn = P4.CENAS[nome]
lib.reset(720, 1280, P4.FPS, amostras); sc = lib.scene
c = dict(sc=sc, f0=P4.F(t0), f1=P4.F(t1) - 1, t0=t0, t1=t1, F=P4.F)
fn(c)
marcas = sorted([(m.frame, m.camera) for m in sc.timeline_markers if m.camera], key=lambda q: q[0])
fa = next(fr for fr, cm in marcas if cm.name == cam_nome)
seg = [fr for fr, cm in marcas if fr > fa]
fb = (seg[0] - 1) if seg else c["f1"]
cam = bpy.data.objects[cam_nome]
for m in list(sc.timeline_markers):
    sc.timeline_markers.remove(m)
sc.camera = cam
sc.frame_start, sc.frame_end = fa - h0, fb + h1
os.makedirs(pasta, exist_ok=True)
sc.render.image_settings.file_format = "PNG"; sc.render.filepath = os.path.join(pasta, "f_")
bpy.ops.render.render(animation=True)
mp4 = os.path.join(pasta, f"{nome}_{cam_nome}.mp4")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", str(P4.FPS), "-start_number", str(fa - h0), "-i", os.path.join(pasta, "f_%04d.png"),
                "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "14", mp4], check=True)
print("FAIXA", fa - h0, fb + h1, h0, h0 + (fb - fa), "plano", fa, fb, "->", mp4)
