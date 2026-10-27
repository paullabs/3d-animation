"""Renderiza o storyboard da parte 2 de "O abrigo" (story_abrigo2.py) em paralelo, aplica a luz do pós (fim de tarde, noite, flashback, galpão),
faz os 17 quadros da montagem de abertura com glitch e monta as pranchas.
python3 story_abrigo2_rodar.py PASTA [ID ...] [--scale 0.5] [--samples 16] [--jobs 8] [--so-pos]      (--so-pos: refaz o pós e as pranchas sem renderizar de novo)
Saída: PASTA/raw/<id>.png (cru), PASTA/<id>.png (com o pós), PASTA/M<n>.png, PASTA/prancha-<k>.png, PASTA/prancha-montagem.png"""
import os, sys, json, subprocess, random
from concurrent.futures import ThreadPoolExecutor
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.abspath(os.path.join(AQUI, ".."))
BL = __import__("canal38_env").BLENDER
a = sys.argv[1:]
pasta = a[0]
opt = lambda n, d: a[a.index(n) + 1] if n in a else d
esc, smp, jobs = opt("--scale", "0.5"), opt("--samples", "16"), int(opt("--jobs", "8"))
ids_arg = [x for i, x in enumerate(a[1:], 1) if not x.startswith("--") and a[i - 1] not in ("--scale", "--samples", "--jobs")]
os.makedirs(pasta + "/raw", exist_ok=True)
PL = json.load(open(f"{RAIZ}/roteiros/abrigo2_planos.json"))
ORDEM, META = PL["ordem"], PL["planos"]
lst = subprocess.run([BL, "-b", "-P", f"{AQUI}/story_abrigo2.py", "--", "--list"], capture_output=True, text=True).stdout.splitlines()
DESENHADOS = [l for l in lst if l.startswith("10A ")][-1].split()
GRADE = json.loads([l for l in lst if l.startswith("{")][-1])
MOV = [l for l in lst if l.startswith("MOV ")][-1].split()[1:]


# ---------------------------------------------------------------- pós
def arr(im):
    return np.asarray(im.convert("RGB"), dtype=np.float32) / 255.0


def img(x):
    return Image.fromarray((np.clip(x, 0, 1) * 255).astype(np.uint8))


def vinheta(x, k=0.45):
    h, w = x.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w]
    d = np.sqrt(((xx - w / 2) / (w / 2)) ** 2 + ((yy - h / 2) / (h / 2)) ** 2)
    return x * (1 - k * np.clip(d - 0.35, 0, 1.2)[..., None])



TENSAO = {"tarde1": (1.28, 0.62, 0.52, 0.028, 0.92), "tarde2": (1.26, 0.74, 0.46, 0.028, 1.08), "noite": (1.32, 0.7, 0.55, 0.03, 1.0), "noite2": (1.34, 0.78, 0.55, 0.03, 1.0),
          "galpao": (1.3, 0.82, 0.5, 0.03, 1.0), "flash": (1.22, 0.55, 0.5, 0.04, 0.95), "cinza": (1.32, 0.55, 0.55, 0.03, 0.9)}


def tensao(x, kind, rng=None):
    """acabamento de tensão (27/10: "amador, nada tenso"): curva de contraste que afunda os pretos, cor puxada para o frio, vinheta pesada e grão de filme"""
    c, sat, vig, grao, gam = TENSAO.get(kind or "cinza", TENSAO["cinza"])
    x = np.clip(x, 0, 1) ** (1.0 / gam)
    x = np.clip(0.5 + (x - 0.5) * c - 0.03, 0, 1)
    lum = (x * np.array([0.3, 0.59, 0.11])).sum(axis=2, keepdims=True)
    quente = np.clip((x[..., 0] - x[..., 2]) * 3.0, 0, 1)[..., None]
    x = lum + (x - lum) * (sat + (1.0 - sat) * 0.9 * quente)
    h, w = x.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w]
    d = np.sqrt(((xx - w / 2) / (w / 2)) ** 2 + ((yy - h * 0.48) / (h / 2)) ** 2)
    x = x * (1 - vig * np.clip(d - 0.28, 0, 1.3)[..., None] ** 1.4)
    r = rng or np.random.default_rng()
    x = x + r.normal(0, grao, (h, w))[..., None]
    return np.clip(x, 0, 1)


def grade(im, kind):
    x = arr(im)
    return img(tensao(_grade0(x, kind), kind))


def _grade0(x, kind):
    if kind == "tarde1":
        x = x * np.array([1.0, 0.92, 0.82]) * 0.86
    elif kind == "tarde2":
        x = x * np.array([0.95, 0.76, 0.62]) * 0.66
        x = vinheta(x, 0.5)
    elif kind == "noite":
        x = x * np.array([0.42, 0.52, 0.78]) * 0.62
        x = vinheta(x, 0.6)
    elif kind == "noite2":
        x0 = np.clip(x, 0, 1)
        x = x0 ** 0.78
        x = x * np.array([0.62, 0.74, 1.0]) * 0.95
        quente = np.clip((x0[..., 0] - x0[..., 2]) * 3.5, 0, 1)[..., None]            # a luz âmbar (janela, poste, lanterna) mantém a cor: quente contra o azul frio
        x = x * (1 - quente) + (x0 ** 0.8) * quente * 1.05
        x = vinheta(x, 0.5)
    elif kind == "galpao":
        x = x * np.array([1.0, 0.93, 0.82]) * 0.9
        x = vinheta(x, 0.45)
    elif kind == "flash":
        g = x.mean(axis=2, keepdims=True)
        x = (x * 0.35 + g * 0.65) * np.array([1.05, 0.98, 0.86])
        x = (x - 0.5) * 1.12 + 0.5
        rnd = np.random.default_rng(3)
        x = x + rnd.normal(0, 0.035, x.shape[:2])[..., None]
        x = vinheta(x, 0.4)
    return x


def estatica(size, seed=1):
    rnd = np.random.default_rng(seed)
    w, h = size
    n = rnd.random((h, w)) ** 1.4
    n[::3] *= 0.6
    return img(np.stack([n, n, n * 1.04], axis=2))


def rgb(im, d=18):
    x = arr(im); o = np.zeros_like(x)
    o[..., 0] = np.roll(x[..., 0], d, axis=1); o[..., 1] = x[..., 1]; o[..., 2] = np.roll(x[..., 2], -d, axis=1)
    return img(o)


def scan(im, f=0.45):
    x = arr(im); x[::4] *= f
    return img(x)


def tremor(im, d=22):
    x = arr(im); y = np.roll(x, d, axis=1) * 0.5 + np.roll(x, -d, axis=0) * 0.5
    return img(y)


def pb_so_vermelho(im):
    x = arr(im); g = x.mean(axis=2, keepdims=True)
    verm = np.clip((x[..., 0] - np.maximum(x[..., 1], x[..., 2])) * 4.0, 0, 1)[..., None]
    return img(g * (1 - verm) + x * verm * 1.4)


def inverte(im):
    return img(1 - arr(im))


def duplo(im, d=30):
    x = arr(im); return img(0.6 * x + 0.4 * np.roll(x, d, axis=0))


def estoura(im):
    x = arr(im); return img(x * 0.4 + 0.75)


def so_vermelho(im):
    x = arr(im); r = np.clip((x[..., 0] - np.maximum(x[..., 1], x[..., 2])) * 5, 0, 1)
    o = np.zeros_like(x); o[..., 0] = r; o[..., 1] = r * 0.15; o[..., 2] = r * 0.1
    return img(o)


def sacode(im, d=40):
    return img(np.roll(arr(im), d, axis=0))


def iris(im, k):
    x = arr(im); h, w = x.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w]
    d = np.sqrt(((xx - w / 2) / (w / 2)) ** 2 + ((yy - h / 2) / (h / 2)) ** 2)
    return img(x * (d < k)[..., None] * (1 - 0.0))


def rampa(im):
    return img(0.7 * arr(im) + 0.3 * np.asarray(arr(im.filter(ImageFilter.GaussianBlur(10)))))


# montagem de abertura: (quadros, fonte, efeito)
MONT = [("M1", 4, None, "estatica"), ("M2", 5, "3C", "rgb+scan"), ("M3", 3, None, "estatica"), ("M4", 5, "2A", "tremor"), ("M5", 3, None, "estatica"),
        ("M6", 5, "4C", "pb_vermelho"), ("M7", 3, None, "estatica"), ("M8", 10, "3D", "rampa"), ("M9", 8, "11C", "trava"), ("M10", 10, "11D", "rgb"),
        ("M11", 6, "1F", "inverte"), ("M12", 3, "5B", "duplo"), ("M13", 3, "6B", "estoura"), ("M14", 2, "14E", "so_vermelho"), ("M15", 2, "16A", "sacode"),
        ("M16", 3, "1F", "rgb-max"), ("M17", 5, None, "preto")]


def monta_m(pasta):
    out = {}
    for mid, n, src, ef in MONT:
        if src is None:
            sz = Image.open(f"{pasta}/{ORDEM[0]}.png").size if os.path.exists(f"{pasta}/{ORDEM[0]}.png") else (540, 960)
            im = estatica(sz, int(mid[1:])) if ef == "estatica" else Image.new("RGB", sz, (0, 0, 0))
        else:
            im = Image.open(f"{pasta}/{src}.png").convert("RGB")
            im = {"rgb+scan": lambda i: scan(rgb(i)), "tremor": tremor, "pb_vermelho": pb_so_vermelho, "rampa": rampa, "trava": lambda i: i,
                  "rgb": rgb, "inverte": inverte, "duplo": duplo, "estoura": estoura, "so_vermelho": so_vermelho, "sacode": sacode,
                  "rgb-max": lambda i: rgb(i, 44)}[ef](im)
        im.save(f"{pasta}/{mid}.png")
        out[mid] = (n, src, ef)
    return out


# ---------------------------------------------------------------- render
def um(i):
    dst = f"{pasta}/raw/{i}.png"
    base, fim = (i[:-4], ["--fim"]) if i.endswith("_fim") else (i, [])
    r = subprocess.run([BL, "-b", "-P", f"{AQUI}/story_abrigo2.py", "--", base, dst, "--scale", esc, "--samples", smp] + fim, capture_output=True, text=True)
    ok = os.path.exists(dst)
    if not ok:
        print("FALHOU", i); print("\n".join((r.stdout + r.stderr).splitlines()[-12:]))
    return i, ok


if "--so-pos" not in a:
    ids = ids_arg or DESENHADOS
    ids = ids + [i + "_fim" for i in ids if i in MOV and i + "_fim" not in ids]
    with ThreadPoolExecutor(jobs) as ex:
        res = list(ex.map(um, ids))
    print("ok:", " ".join(i for i, o in res if o)); print("falhou:", " ".join(i for i, o in res if not o))

# pós
for i in DESENHADOS + [m + "_fim" for m in MOV]:
    p = f"{pasta}/raw/{i}.png"
    if os.path.exists(p):
        im = Image.open(p).convert("RGB")
        k = GRADE.get(i[:-4] if i.endswith("_fim") else i)
        if i == "5D":
            im = iris(grade(im, "noite2"), 0.55)
        elif k:
            im = grade(im, k)
        im.save(f"{pasta}/{i}.png")
sz = Image.open(f"{pasta}/{[i for i in DESENHADOS if os.path.exists(f'{pasta}/{i}.png')][0]}.png").size
for i in ORDEM:
    if i.startswith("P"):
        Image.new("RGB", sz, (0, 0, 0)).save(f"{pasta}/{i}.png")
mont = monta_m(pasta)

# pranchas
F = lambda n, k=0: ImageFont.truetype("/System/Library/Fonts/Menlo.ttc", n)
FA = ImageFont.truetype("/System/Library/Fonts/Avenir Next.ttc", 17, index=0)
FB = ImageFont.truetype("/System/Library/Fonts/Avenir Next.ttc", 22, index=2)
BG, INK, AMB, SUB = (30, 34, 30), (236, 232, 218), (230, 190, 110), (170, 168, 152)
TW, TH = 300, 533


def tile(sheet, d, x, y, pid, extra_ok=True):
    p = f"{pasta}/{pid}.png"
    if os.path.exists(p):
        sheet.paste(Image.open(p).convert("RGB").resize((TW, TH)), (x, y + 30))
        pf = f"{pasta}/{pid}_fim.png"
        if os.path.exists(pf):                                            # plano com câmera que anda: o quadro do fim, pequeno, no canto
            iw, ih = int(TW * 0.46), int(TH * 0.46)
            sheet.paste(Image.open(pf).convert("RGB").resize((iw, ih)), (x + TW - iw - 4, y + 30 + TH - ih - 4))
            d.rectangle((x + TW - iw - 5, y + 30 + TH - ih - 5, x + TW - 3, y + 30 + TH - 3), outline=(230, 190, 110), width=2)
            d.text((x + TW - iw - 2, y + 30 + TH - ih - 22), "fim", font=F(14), fill=(230, 190, 110))
    else:
        d.rectangle((x, y + 30, x + TW, y + 30 + TH), outline=(120, 60, 60)); d.text((x + 70, y + 280), "sem quadro", font=FA, fill=(160, 80, 80))
    m = META.get(pid, {})
    d.text((x, y), f"{pid}  {m.get('t0', 0):.1f}-{m.get('t1', 0):.1f}s", font=F(15), fill=AMB)
    return m


def prancha(nome, ids, cols, titulo):
    lin = (len(ids) + cols - 1) // cols
    W, Hh = cols * (TW + 14) + 14, 70 + lin * (TH + 30 + 96 + 14)
    sh = Image.new("RGB", (W, Hh), BG); d = ImageDraw.Draw(sh)
    d.text((14, 16), titulo, font=FB, fill=INK)
    for k, pid in enumerate(ids):
        x, y = 14 + (k % cols) * (TW + 14), 60 + (k // cols) * (TH + 30 + 96 + 14)
        m = tile(sh, d, x, y, pid)
        txt = f"{m.get('palavras', '')} · {m.get('lente', '')}"
        import textwrap
        for j, ln in enumerate(textwrap.wrap(txt, 40)[:4]):
            d.text((x, y + 30 + TH + 4 + 22 * j), ln, font=FA, fill=SUB)
    sh.save(f"{pasta}/{nome}"); print("prancha", nome, sh.size)


corpo = [i for i in ORDEM if not i.startswith("P") and i != "1M"]
grupos = [corpo[k:k + 15] for k in range(0, len(corpo), 15)]
sel = [i for i in ids_arg if i in corpo]
if sel:
    grupos = [[i for i in corpo if i in sel][k:k + 15] for k in range(0, len(sel), 15)]
for k, g in enumerate(grupos, 1):
    prancha(f"{'prancha-rev' if sel else 'prancha'}-{k}.png", g, 5, f"O abrigo, parte 2 · storyboard {k}/{len(grupos)} · {g[0]} a {g[-1]}")
# a montagem de abertura
sh = Image.new("RGB", (6 * (TW + 14) + 14, 70 + 3 * (TH + 30 + 60)), BG); d = ImageDraw.Draw(sh)
d.text((14, 16), "A montagem de abertura (1M, 3,3 s, 79 quadros): 17 cortes com glitch", font=FB, fill=INK)
for k, (mid, (n, src, ef)) in enumerate(mont.items()):
    x, y = 14 + (k % 6) * (TW + 14), 60 + (k // 6) * (TH + 30 + 60)
    sh.paste(Image.open(f"{pasta}/{mid}.png").convert("RGB").resize((TW, TH)), (x, y + 30))
    d.text((x, y), f"{mid}  {n} quadros", font=F(15), fill=AMB)
    d.text((x, y + 30 + TH + 4), f"{src or 'estática/preto'} · {ef}", font=FA, fill=SUB)
sh.save(f"{pasta}/prancha-montagem.png"); print("prancha-montagem")
