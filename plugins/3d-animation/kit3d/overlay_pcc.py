"""Camada de selos de nível, legendas e números do vídeo PCC (feita em PIL, sem desfoque de câmera).
python3 overlay_pcc.py SAIDA.mov [--preview t1,t2,...]   -> .mov com canal alfa (qtrle) 1080x1920 a 24 qps
Fontes de tempo: roteiros/voz-pcc/tempos.json e palavras.json."""
import json, math, os, subprocess, sys
from functools import lru_cache
from PIL import Image, ImageDraw, ImageFont, ImageFilter

FPS = 24; W, H = 1080, 1920
VOZ = (__import__("canal38_env").RAIZ + "/roteiros/voz-pcc")
FONT = "/System/Library/Fonts/Avenir Next.ttc"
FIDX = 8          # Avenir Next Heavy (mais limpa que a Arial Black)
STEP_COLORS = ["#5b6f94", "#6a73a0", "#8577a8", "#b07fa0", "#e0a23f"]
INK = (13, 16, 32, 255)
PAL = json.load(open(VOZ + "/palavras.json"))
TEMPOS = json.load(open(VOZ + "/tempos.json"))


def rgb(h, a=255):
    h = h.lstrip("#"); return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), a)


def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def ease_out_back(u, c=1.70158):
    u = clamp(u); return 1 + (c + 1) * (u - 1) ** 3 + c * (u - 1) ** 2


def ease_out(u):
    u = clamp(u); return 1 - (1 - u) ** 3


def ease_in_out(u):
    u = clamp(u); return u * u * (3 - 2 * u)


@lru_cache(maxsize=4096)
def spr(text, size, fill=(255, 255, 255, 255), stroke=0, stroke_fill=(0, 0, 0, 255)):
    f = ImageFont.truetype(FONT, size, index=FIDX)
    l, t, r, b = f.getbbox(text, stroke_width=stroke)
    w, h = r - l + 2 * stroke + 12, b - t + 2 * stroke + 12
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.text((6 + stroke - l, 6 + stroke - t), text, font=f, fill=fill, stroke_width=stroke, stroke_fill=stroke_fill)
    return im


@lru_cache(maxsize=4096)
def sombra(text, size, fill=(255, 255, 255, 255), stroke=3):
    """texto com contorno fino e sombra macia (como as legendas do IfverseTales)"""
    t = spr(text, size, fill, stroke, (8, 9, 16, 255))
    sh = spr(text, size, (0, 0, 0, 170), stroke + 2, (0, 0, 0, 170))
    out = Image.new("RGBA", (t.width + 24, t.height + 24), (0, 0, 0, 0))
    out.alpha_composite(sh, (12, 16)); out = out.filter(ImageFilter.GaussianBlur(4))
    out.alpha_composite(t, (12, 12))
    return out


def put(canvas, im, cx, cy, scale=1.0, alpha=1.0):
    if alpha <= 0.003 or scale <= 0.003:
        return
    if scale != 1.0:
        im = im.resize((max(1, int(im.width * scale)), max(1, int(im.height * scale))), Image.LANCZOS)
    if alpha < 1.0:
        a = im.getchannel("A").point(lambda v: int(v * alpha)); im = im.copy(); im.putalpha(a)
    x, y = int(cx - im.width / 2), int(cy - im.height / 2)
    x0, y0 = max(0, x), max(0, y); x1, y1 = min(W, x + im.width), min(H, y + im.height)
    if x1 <= x0 or y1 <= y0:
        return
    canvas.alpha_composite(im.crop((x0 - x, y0 - y, x1 - x, y1 - y)), (x0, y0))


def pill(w, h, fill, outline=None, ow=0, radius=None):
    im = Image.new("RGBA", (w + 24, h + 24), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((12, 12, 12 + w, 12 + h), radius=radius if radius is not None else h // 2, fill=fill, outline=outline, width=ow)
    return im


# ---------------------------------------------------------------- legendas (palavra em destaque)
NUMEROS = {("quarenta", "mil"): "40 MIL", ("cinquenta", "e", "dois", "bilhões"): "52 BILHÕES", ("trezentos", "anos"): "300 ANOS"}


def tokens():
    """palavras da legenda com tempo, juntando números por extenso em um só bloco ('quarenta mil' -> '40 MIL')"""
    out = []; i = 0
    while i < len(PAL):
        w = PAL[i]; hit = None
        for seq, rep in NUMEROS.items():
            n = len(seq)
            if i + n <= len(PAL) and PAL[i]["frase"] == PAL[i + n - 1]["frase"] and \
                    tuple(x["txt"].strip(".,:;!?…").lower() for x in PAL[i:i + n]) == seq:
                hit = (n, rep); break
        if hit:
            n, rep = hit
            out.append(dict(txt=rep, t0=PAL[i]["t0"], t1=PAL[i + n - 1]["t1"], frase=w["frase"], fim=PAL[i + n - 1]["txt"][-1] in ".,:;!?…"))
            i += n; continue
        txt = w["txt"]
        core = txt.strip(".,:;!?…")
        if core.lower() == "cinco":
            txt = txt.replace(core, "5")
        out.append(dict(txt=txt.upper(), t0=w["t0"], t1=w["t1"], frase=w["frase"], fim=txt[-1] in ".,:;!?…"))
        i += 1
    return out


def blocos():
    """agrupa os tokens em blocos de até 3 palavras e até 15 letras (uma linha só); quebra também na pontuação"""
    toks = tokens(); blocks = []; cur = []
    for k, t in enumerate(toks):
        cur.append(t)
        n = len(" ".join(x["txt"] for x in cur))
        prox = toks[k + 1] if k + 1 < len(toks) else None
        quebra = (len(cur) >= 3 or t["fim"] or prox is None or prox["frase"] != t["frase"]
                  or (prox and n + 1 + len(prox["txt"]) > 15))
        if quebra:
            blocks.append(cur); cur = []
    return blocks


BLOCOS = blocos()


def caption(canvas, t):
    for bi, b in enumerate(BLOCOS):
        t0 = b[0]["t0"] - 0.04
        t1 = (BLOCOS[bi + 1][0]["t0"] - 0.04) if bi + 1 < len(BLOCOS) and BLOCOS[bi + 1][0]["frase"] == b[0]["frase"] else b[-1]["t1"] + 0.14
        if not (t0 <= t < t1):
            continue
        # uma linha só; palavra ativa em amarelo
        words = b; size = 62
        pop = 0.92 + 0.08 * ease_out((t - t0) / 0.08)
        parts = []
        for w in words:
            act = w["t0"] - 0.02 <= t < w["t1"] + 0.06
            parts.append(sombra(w["txt"], size, (255, 210, 64, 255) if act else (255, 255, 255, 255)))
        gap = 4
        tw = sum(p.width for p in parts) + gap * (len(parts) - 1)
        x = -tw / 2
        for p, w in zip(parts, words):
            act = w["t0"] - 0.02 <= t < w["t1"] + 0.06
            put(canvas, p, W / 2 + (x + p.width / 2) * pop, 1250, pop)
            x += p.width + gap


# ---------------------------------------------------------------- selo de nível
NIVEIS = [  # (início, fim, rótulo, nº do nível, cor da barra)
    (7.55, 11.1, "5 NÍVEIS", 0, "#ffffff"),
    (11.25, 16.55, "NÍVEL 1 · O AJUDANTE", 1, STEP_COLORS[0]),
    (16.72, 23.85, "NÍVEL 2 · O MEMBRO", 2, STEP_COLORS[1]),
    (24.0, 31.7, "NÍVEL 3 · O FISCAL", 3, STEP_COLORS[2]),
    (31.85, 40.95, "NÍVEL 4 · O CHEFE DE SETOR", 4, STEP_COLORS[3]),
    (41.1, 55.85, "NÍVEL 5 · O TOPO", 5, STEP_COLORS[4]),
    (56.0, 61.5, "O PREÇO DO TOPO", 6, "#e2364b"),
]


SEM_TITULO = [(47.4, 52.6)]          # trechos em que o número grande ocupa o alto da tela


def badge(canvas, t):
    """título no alto, como o 'YOU'RE 5 AGAIN' do IfverseTales: linha amarela + linha branca, sem caixa"""
    for (a, b, label, lv, col) in NIVEIS:
        if not (a <= t < b + 0.2) or any(x <= t < y for x, y in SEM_TITULO):
            continue
        alpha = clamp((t - a) / 0.18) * (1.0 if t < b else clamp(1 - (t - b) / 0.2))
        dy = 14 * (1 - ease_out((t - a) / 0.25))
        if "·" in label:
            l1, l2 = [x.strip() for x in label.split("·")]
        else:
            l1, l2 = label, None
        c1 = (226, 54, 75, 255) if lv == 6 else (255, 210, 64, 255)
        put(canvas, sombra(l1, 70, c1, 3), W / 2, 250 + dy, 1.0, alpha)
        if l2:
            put(canvas, sombra(l2, 44, (255, 255, 255, 255), 3), W / 2, 318 + dy, 1.0, alpha)
        return


# ---------------------------------------------------------------- números grandes
def glow_text(text, size, fill, stroke, blur=18, glow_col=(255, 255, 255, 140)):
    base = spr(text, size, fill, stroke, INK)
    g = Image.new("RGBA", (base.width + 120, base.height + 120), (0, 0, 0, 0))
    mask = spr(text, size, glow_col, stroke + 6, glow_col)
    g.alpha_composite(mask, (60, 60))
    g = g.filter(ImageFilter.GaussianBlur(blur))
    g.alpha_composite(base, (60, 60))
    return g


def contador_40k(canvas, t):
    a, b = 1.37, 3.40
    if not (a <= t < b + 0.2):
        return
    u = clamp((t - 1.37) / 1.3)                     # mesmo ritmo do povo que acende (trono.multidao_contada)
    val = int(round(40000 * ease_out(u)))
    txt = f"{val:,}".replace(",", ".")
    alpha = clamp((t - a) / 0.1) * (1.0 if t < b else clamp(1 - (t - b) / 0.2))
    sc = 0.7 + 0.3 * ease_out_back((t - a) / 0.3) if t - a < 0.3 else 1.0
    put(canvas, glow_text(txt, 170, (255, 255, 255, 255), 4), W / 2, 270, sc, alpha)       # no título: o rei e o povo ficam livres
    put(canvas, sombra("PESSOAS", 56, (255, 210, 64, 255)), W / 2, 385, sc, alpha * clamp((t - a - 0.25) / 0.2))


def bloco_dinheiro(canvas, t):
    """R$ 52 BILHÕES no alto (o dinheiro fica livre embaixo, em fundo limpo) e depois EM 5 ANOS"""
    a, b = 48.15, 51.45
    if not (a <= t < b + 0.2):
        return
    alpha = clamp((t - a) / 0.12) * (1.0 if t < b else clamp(1 - (t - b) / 0.2))
    u = clamp((t - 48.22) / 0.9)
    val = int(round(52 * ease_out(u)))
    sc = 0.75 + 0.25 * ease_out_back((t - a) / 0.35) if t - a < 0.35 else 1.0
    cy = 330
    put(canvas, spr("R$", 84, (255, 212, 59, 255), 9, INK), W / 2 - 190, cy - 70, sc, alpha)
    put(canvas, glow_text(str(val), 250, (255, 255, 255, 255), 12, glow_col=(255, 212, 59, 150)), W / 2 + 30, cy, sc, alpha)
    ub = clamp((t - 48.82) / 0.25)
    put(canvas, spr("BILHÕES DE REAIS", 64, (255, 255, 255, 255), 8, INK), W / 2, cy + 150, 0.8 + 0.2 * ease_out_back(ub), alpha * clamp(ub * 2))
    if t >= 50.2:
        ta = clamp((t - 50.2) / 0.2)
        txt = spr("EM 5 ANOS", 56, (13, 16, 32, 255), 0)
        im = pill(txt.width + 80, 96, (255, 212, 59, 255), INK, 5, 48)
        im.alpha_composite(txt, (12 + 40, 12 + 48 - txt.height // 2))
        put(canvas, im, W / 2, cy + 250, 0.8 + 0.2 * ease_out_back(ta), alpha * ta)


def pill_postos(canvas, t):
    a, b = 46.8, 47.38
    if not (a <= t < b + 0.15):
        return
    alpha = clamp((t - a) / 0.12) * (1.0 if t < b else clamp(1 - (t - b) / 0.15))
    sc = 0.7 + 0.3 * ease_out_back((t - a) / 0.3) if t - a < 0.3 else 1.0
    txt = spr("MAIS DE 1.000 POSTOS", 62, (255, 255, 255, 255), 0)
    im = pill(txt.width + 90, 118, (13, 16, 32, 235), (255, 212, 59, 255), 5, 59)
    im.alpha_composite(txt, (12 + 45, 12 + 59 - txt.height // 2))
    put(canvas, im, W / 2, 500, sc, alpha)


# ---------------------------------------------------------------- clarões nos cortes e fade final
FLASHES = [(7.34, 0.35, (255, 255, 255)), (11.18, 0.3, (255, 255, 255)), (23.92, 0.3, (255, 255, 255)), (31.78, 0.3, (255, 255, 255)),
           (41.02, 0.45, (255, 236, 190)), (55.92, 0.45, (226, 54, 75)), (3.55, 0.25, (255, 255, 255))]


def flashes(canvas, t):
    a = 0.0; col = (255, 255, 255)
    for (tf, amp, c) in FLASHES:
        if tf <= t < tf + 0.18:
            v = amp * (1 - (t - tf) / 0.18)
            if v > a:
                a, col = v, c
    if t > 62.95:
        v = clamp((t - 62.95) / 0.5)
        if v > 0:
            ov = Image.new("RGBA", (W, H), (0, 0, 0, int(255 * v))); canvas.alpha_composite(ov)
    if a > 0.01:
        ov = Image.new("RGBA", (W, H), (*col, int(255 * a))); canvas.alpha_composite(ov)


def frame(t):
    cv = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    contador_40k(cv, t); pill_postos(cv, t); bloco_dinheiro(cv, t)
    badge(cv, t); caption(cv, t); flashes(cv, t)
    return cv


def main():
    a = sys.argv[1:]
    if "--preview" in a:
        out = a[a.index("--preview") - 1] if a.index("--preview") > 0 else "/tmp/ov"
        os.makedirs(out, exist_ok=True)
        for t in [float(x) for x in a[a.index("--preview") + 1].split(",")]:
            bg = Image.new("RGBA", (W, H), (60, 70, 100, 255)); bg.alpha_composite(frame(t))
            bg.convert("RGB").resize((540, 960)).save(f"{out}/ov_{t:06.2f}.png")
        return
    out = a[0]
    total = TEMPOS["total"]
    n = int(math.ceil(total * FPS))
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
           "-c:v", "qtrle", "-an", out]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for k in range(n):
        t = k / FPS
        p.stdin.write(frame(t).tobytes())
    p.stdin.close(); p.wait()
    print("ok", out, n, "quadros")


if __name__ == "__main__":
    main()
