"""Camada de texto do PCC v4 ("Você acabou de entrar no PCC"): legendas e rótulo do nível, com entrada suave.
- Legenda: blocos de até 3 palavras numa linha; o bloco entra subindo 18 px e aparecendo (sem estouro);
  a palavra falada fica coral e um sublinhado desliza de uma palavra para a outra.
- Rótulo do nível no alto ("NÍVEL 1" coral + nome em branco), que entra junto com o nível e fica até o próximo.
python3 overlay_pcc3.py SAIDA.mov [--preview DIR t1,t2,...]"""
import json, os, subprocess, sys, math
from functools import lru_cache
from PIL import Image, ImageDraw, ImageFont, ImageFilter

FPS = 24; W, H = 1080, 1920
VOZ = (__import__("canal38_env").RAIZ + "/roteiros/voz-pcc3")
FONT = "/System/Library/Fonts/Avenir Next.ttc"
PAL = json.load(open(VOZ + "/palavras.json"))
TEMPOS = json.load(open(VOZ + "/tempos.json"))
BRANCO, CORAL, ESCURO = (255, 255, 255, 255), (255, 176, 140, 255), (10, 22, 27, 255)
Y_LEG = 1330                                  # uma palavra por vez, baixa, numa faixa que ainda se lê no Reels
NIVEIS = [(3, "NÍVEL 1", "O PONTO"), (5, "NÍVEL 2", "O GERENTE"), (7, "NÍVEL 3", "O MEMBRO"), (9, "NÍVEL 4", "CHEFE DE SETOR"),
          (11, "NÍVEL 5", "O TOPO"), (13, "O PREÇO", "")]


def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def ease(u):                       # mesma "S suave" da câmera (aproximação da curva A)
    u = clamp(u); return u * u * u * (u * (6 * u - 15) + 10)


def ease_out(u):
    u = clamp(u); return 1 - (1 - u) ** 3


@lru_cache(maxsize=4096)
def texto(s, size, fill=BRANCO, idx=8):
    """texto com contorno escuro fino e sombra macia embaixo (lê em fundo claro e escuro)"""
    f = ImageFont.truetype(FONT, size, index=idx)
    l, t, r, b = f.getbbox(s, stroke_width=3)
    w, h = r - l + 40, b - t + 44
    base = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(base)
    d.text((20 - l, 18 - t + 6), s, font=f, fill=(0, 0, 0, 150), stroke_width=4, stroke_fill=(0, 0, 0, 150))
    base = base.filter(ImageFilter.GaussianBlur(6))
    d = ImageDraw.Draw(base)
    d.text((20 - l, 18 - t), s, font=f, fill=fill, stroke_width=3, stroke_fill=ESCURO)
    return base


def put(canvas, im, cx, cy, alpha=1.0):
    if alpha <= 0.003:
        return
    if alpha < 1.0:
        a = im.getchannel("A").point(lambda v: int(v * alpha)); im = im.copy(); im.putalpha(a)
    x, y = int(round(cx - im.width / 2)), int(round(cy - im.height / 2))
    canvas.alpha_composite(im, (max(0, x), max(0, y)), (max(0, -x), max(0, -y)))


# ---------------------------------------------------------------- legenda
JUNTA = {("quinze", "por", "cento"): "15%", ("oitenta", "por", "cento"): "80%", ("quinze",): "15", ("doze",): "12"}


def tokens():
    out = []; i = 0
    while i < len(PAL):
        w = PAL[i]; txt = w["txt"]
        hit = None
        for seq, rep in sorted(JUNTA.items(), key=lambda kv: -len(kv[0])):      # números por extenso viram algarismo
            n = len(seq)
            if i + n <= len(PAL) and all(PAL[i + j]["frase"] == w["frase"] for j in range(n)) and \
                    tuple(x["txt"].strip(".,:;!?").lower() for x in PAL[i:i + n]) == seq:
                last = PAL[i + n - 1]["txt"]; pont = last[len(last.rstrip(".,:;!?")):]
                hit = (n, rep + pont); break
        if hit:
            n, rep = hit
            out.append(dict(txt=rep, t0=w["t0"], t1=PAL[i + n - 1]["t1"], frase=w["frase"], fim=rep[-1] in ".,:;!?")); i += n; continue
        if txt.strip(".,:;!?") == "R$" and i + 1 < len(PAL) and PAL[i + 1]["frase"] == w["frase"]:     # "R$" + valor juntos
            n = PAL[i + 1]
            out.append(dict(txt="R$ " + n["txt"], t0=w["t0"], t1=n["t1"], frase=w["frase"], fim=n["txt"][-1] in ".,:;!?")); i += 2; continue
        out.append(dict(txt=txt, t0=w["t0"], t1=w["t1"], frase=w["frase"], fim=txt[-1] in ".,:;!?")); i += 1
    for t in out:
        t["txt"] = t["txt"].upper()
    return out


def blocos():
    toks = tokens(); bl = []; cur = []
    for k, t in enumerate(toks):
        cur.append(t)
        n = len(" ".join(x["txt"] for x in cur)); prox = toks[k + 1] if k + 1 < len(toks) else None
        if len(cur) >= 3 or t["fim"] or prox is None or prox["frase"] != t["frase"] or n + 1 + len(prox["txt"]) > 16:
            bl.append(cur); cur = []
    return bl


BLOCOS = blocos()


def legenda(cv, t):
    """uma palavra por vez, no centro da área segura, embaixo: entra subindo 10 px em 0,08 s e sai quando vem a próxima.
    Números ficam coral; o resto branco. Nada largo cobrindo a cena."""
    toks = [w for b in BLOCOS for w in b]
    for k, w in enumerate(toks):
        a0 = w["t0"] - 0.03
        prox = toks[k + 1]["t0"] - 0.03 if k + 1 < len(toks) else 1e9
        a1 = min(prox, w["t1"] + 0.25)
        if not (a0 <= t < a1):
            continue
        u = ease_out((t - a0) / 0.08); a = u * clamp((a1 - t) / 0.05)
        num = any(ch.isdigit() for ch in w["txt"])
        put(cv, texto(w["txt"].strip(",.:;"), 68, CORAL if num else BRANCO), W / 2 - 27, Y_LEG + 10 * (1 - u), a)
        return


# ---------------------------------------------------------------- rótulo do nível (alto da tela)
def nivel(cv, t):
    ini = {f["n"]: f["inicio"] for f in TEMPOS["falas"]}
    for k, (fr, l1, l2) in enumerate(NIVEIS):
        a0 = ini[fr] - 0.05
        a1 = ini[NIVEIS[k + 1][0]] - 0.2 if k + 1 < len(NIVEIS) else TEMPOS["total"]
        if not (a0 <= t < a1):
            continue
        u = ease_out((t - a0) / 0.25); a = u * clamp((a1 - t) / 0.15)
        put(cv, texto(l1, 40, CORAL, 8), W / 2 - 27, 318 + 14 * (1 - u), a)
        if l2:
            put(cv, texto(l2, 58, BRANCO, 8), W / 2 - 27, 380 + 14 * (1 - u), a * clamp((t - a0 - 0.08) / 0.2))


def _t(frase, txt):
    return [w for w in PAL if w["frase"] == frase and w["txt"].strip(".,:;!?").lower() == txt.lower()][0]["t0"]


@lru_cache(maxsize=8)
def icone_nota(h=44):
    """cédula verde desenhada (o ícone do contador): sem texto"""
    w = int(h * 2.1); im = Image.new("RGBA", (w + 12, h + 12), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((6, 6, 6 + w, 6 + h), radius=6, fill=(44, 106, 64, 255))
    d.rounded_rectangle((10, 10, 2 + w, 2 + h), radius=4, fill=(76, 154, 98, 255))
    r = int(h * 0.3); cx, cy = 6 + w // 2, 6 + h // 2
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(166, 217, 174, 255))
    d.rounded_rectangle((cx - w // 2 + 8, cy - r, cx - w // 2 + 8 + w // 8, cy + r), radius=3, fill=(124, 194, 140, 255))
    d.rounded_rectangle((cx + w // 2 - 8 - w // 8, cy - r, cx + w // 2 - 8, cy + r), radius=3, fill=(124, 194, 140, 255))
    return im


@lru_cache(maxsize=8)
def icone_sirene(h=44):
    """sirene de viatura: cúpula vermelha e base azul (sem texto)"""
    w = int(h * 1.3); im = Image.new("RGBA", (w + 12, h + 12), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((6, 6 + int(h * 0.62), 6 + w, 6 + h), radius=5, fill=(61, 123, 255, 255))
    d.pieslice((6 + int(w * 0.12), 6, 6 + int(w * 0.88), 6 + int(h * 1.3)), 180, 360, fill=(255, 59, 74, 255))
    d.ellipse((6 + int(w * 0.42), 6 + int(h * 0.18), 6 + int(w * 0.58), 6 + int(h * 0.34)), fill=(255, 190, 190, 255))
    return im


@lru_cache(maxsize=8)
def icone_cadeado(h=44):
    """cadeado fechado (presos)"""
    w = int(h * 0.9); im = Image.new("RGBA", (w + 12, h + 12), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.arc((6 + int(w * 0.2), 6, 6 + int(w * 0.8), 6 + int(h * 0.7)), 180, 360, fill=(230, 232, 245, 255), width=6)
    d.rounded_rectangle((6, 6 + int(h * 0.4), 6 + w, 6 + h), radius=6, fill=(255, 176, 140, 255))
    d.ellipse((6 + int(w * 0.38), 6 + int(h * 0.58), 6 + int(w * 0.62), 6 + int(h * 0.78)), fill=(10, 22, 27, 255))
    return im


def _fala(n):
    return TEMPOS["falas"][n - 1]["inicio"]


def _entradas():
    """contadores de jogo no canto de cima da área segura (ícone + número, sem palavras): (início, fim, ícone, texto, cor)"""
    fim = TEMPOS["total"] - 0.6
    return [
        (_t(3, "quinze") - 0.05, _fala(4) - 0.08, icone_nota, "15%", BRANCO),
        (_t(5, "5%") - 0.05, _t(5, "faturar") - 0.1, icone_nota, "5%", BRANCO),
        (_t(5, "700") - 0.15, _fala(6) - 0.08, icone_nota, "700 MIL", BRANCO),
        (_t(6, "42") - 0.05, _fala(7) - 0.08, icone_sirene, "42", BRANCO),
        (_t(7, "950") - 0.1, _fala(8) - 0.08, icone_nota, "-950", CORAL),
        (_t(10, "milhões") - 0.25, _fala(11) - 0.08, icone_nota, "5 MI", BRANCO),
        (_t(11, "oitenta") - 0.05, _fala(12) - 0.08, icone_nota, "80%", BRANCO),
        (_t(13, "só") - 0.05, fim, icone_cadeado, "14/15", CORAL),
    ]


X_HUD, Y_HUD = 945, 302


def _desenha_hud(cv, t, a0, a1, ic, texto, cor, pulo=1.0):
    u = ease_out((t - a0) / 0.18); a = u * clamp((a1 - t) / 0.12)
    num = texto if isinstance(texto, Image.Image) else texto_img(texto, int(60 * pulo), cor)
    icone = ic()
    w = icone.width + 8 + num.width - 30
    x0 = X_HUD - w + 30 * (1 - u)
    put(cv, icone, x0 + icone.width / 2, Y_HUD, a)
    put(cv, num, x0 + icone.width + 8 + num.width / 2 - 15, Y_HUD, a)


def texto_img(s, size, cor):
    return texto(s, size, cor, 8)


def salario(cv, t):
    """contador do salário (a1): a cédula verde e o valor que sobe de 100 em 100 com as notas que caem; depois, os valores de cada nível"""
    a0 = _t(1, "salário"); t0 = a0 + 0.15; t1 = _t(1, "dia") - 0.05; b = _fala(2) - 0.05
    if a0 <= t < b:
        pos = clamp((t - t0) / (t1 - t0))
        k = 0 if t < t0 else min(12, 1 + int(12 * pos))
        tk = t0 + (t1 - t0) * max(0, k - 1) / 11 if k else a0
        pulo = 1.0 + 0.14 * max(0.0, 1 - (t - tk) / 0.12) if k else 1.0
        _desenha_hud(cv, t, a0, b, icone_nota, f"{k * 100:,}".replace(",", "."), BRANCO, pulo)
    for a0, a1, ic, txt, cor in _entradas():
        if a0 <= t < a1:
            _desenha_hud(cv, t, a0, a1, ic, txt, cor)


def frame(t):
    cv = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    nivel(cv, t); salario(cv, t); legenda(cv, t)
    if t > TEMPOS["total"] - 0.6:
        v = clamp((t - (TEMPOS["total"] - 0.6)) / 0.5)
        cv.alpha_composite(Image.new("RGBA", (W, H), (0, 0, 0, int(255 * v))))
    return cv


def main():
    a = sys.argv[1:]
    if "--preview" in a:
        out = a[a.index("--preview") + 1]; os.makedirs(out, exist_ok=True)
        for t in [float(x) for x in a[a.index("--preview") + 2].split(",")]:
            bg = Image.new("RGBA", (W, H), (61, 104, 114, 255)); bg.alpha_composite(frame(t))
            bg.convert("RGB").resize((540, 960)).save(f"{out}/ov_{t:06.2f}.png")
        return
    out = a[0]; n = int(math.ceil(TEMPOS["total"] * FPS))
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-c:v", "qtrle", "-an", out], stdin=subprocess.PIPE)
    for k in range(n):
        p.stdin.write(frame(k / FPS).tobytes())
    p.stdin.close(); p.wait()
    print("ok", out, n, "quadros")


if __name__ == "__main__":
    main()