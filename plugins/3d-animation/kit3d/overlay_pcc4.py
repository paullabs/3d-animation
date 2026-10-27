"""Camada de texto do PCC v7 (voz da ElevenLabs): textos discretos, que entram, dizem e saem.
- Legenda: trechos curtos (até 3 palavras), em caixa normal, Demi Bold 46 px, sombra macia em vez de contorno grosso.
  O trecho inteiro aparece apagado e cada palavra acende quando é dita; dinheiro em verde, outros números em âmbar.
- Rótulo do nível: pequeno, no canto de cima à esquerda, aparece por 2,4 s quando o nível começa e some.
- Contadores (ícone + número): menores, no canto de cima à direita, ficam só 2,2 s.
python3 overlay_pcc4.py SAIDA.mov [--preview DIR t1,t2,...]"""
import json, os, subprocess, sys, math
from functools import lru_cache
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import overlay_pcc3 as O3

FPS = 24; W, H = 1080, 1920
VOZ = (__import__("canal38_env").RAIZ + "/roteiros/voz-pcc5")
FONT = "/System/Library/Fonts/Avenir Next.ttc"
PAL = json.load(open(VOZ + "/palavras.json"))
TEMPOS = json.load(open(VOZ + "/tempos.json"))
BRANCO, CORAL, VERDE, AMBAR = (255, 255, 255, 255), (255, 176, 140, 255), (142, 229, 155, 255), (255, 214, 140, 255)
Y_LEG = 1310; X_MEIO = W / 2 - 27                           # centro da área segura
NIVEIS = [(3, "NÍVEL 1", "O ponto"), (5, "NÍVEL 2", "O gerente"), (7, "NÍVEL 3", "O membro"), (9, "NÍVEL 4", "Chefe de setor"),
          (11, "NÍVEL 5", "O topo"), (13, "NO FIM", "O preço")]
DINHEIRO = ("reais", "mil", "milhões")
clamp, ease_out, put = O3.clamp, O3.ease_out, O3.put


@lru_cache(maxsize=4096)
def texto(s, size, fill=BRANCO, idx=2, sombra=150):
    """texto com sombra macia (sem contorno grosso): lê em fundo claro e escuro sem pesar"""
    f = ImageFont.truetype(FONT, size, index=idx)
    l, t, r, b = f.getbbox(s)
    w, h = r - l + 48, b - t + 48
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.text((24 - l, 24 - t + 4), s, font=f, fill=(0, 0, 0, sombra), stroke_width=3, stroke_fill=(0, 0, 0, sombra))
    im = im.filter(ImageFilter.GaussianBlur(7))
    d = ImageDraw.Draw(im)
    d.text((24 - l, 24 - t), s, font=f, fill=fill, stroke_width=1, stroke_fill=(10, 16, 30, 90))
    return im


def largura(s, size, idx=2):
    return ImageFont.truetype(FONT, size, index=idx).getlength(s)


@lru_cache(maxsize=256)
def mancha(larg):
    """mancha escura bem desfocada, sem borda: não parece uma caixa"""
    w, h = larg + 160, 150
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((60, 50, w - 60, h - 50), radius=25, fill=(6, 8, 16, 200))
    return im.filter(ImageFilter.GaussianBlur(24))


# ---------------------------------------------------------------- legenda
def trechos():
    bl = []; cur = []
    for k, w in enumerate(PAL):
        cur.append(w); prox = PAL[k + 1] if k + 1 < len(PAL) else None
        fim = w["txt"][-1] in ".,:;!?"
        n = len(" ".join(x["txt"] for x in cur))
        if len(cur) >= 3 or fim or prox is None or prox["frase"] != w["frase"] or n + 1 + len(prox["txt"]) > 18:
            bl.append(cur); cur = []
    return bl


TRECHOS = trechos()


def cor_palavra(tr, i):
    s = tr[i]["txt"].strip(".,:;!?…")
    num = any(ch.isdigit() for ch in s)
    vizinho = tr[i + 1]["txt"].strip(".,:;!?").lower() if i + 1 < len(tr) else ""
    if num and (vizinho in DINHEIRO or s.lower() in DINHEIRO):
        return VERDE
    if s.lower() in DINHEIRO and i > 0 and any(ch.isdigit() for ch in tr[i - 1]["txt"]):
        return VERDE
    return AMBAR if num else BRANCO


def legenda(cv, t, size=54):
    for k, tr in enumerate(TRECHOS):
        a0 = tr[0]["t0"] - 0.08
        prox = TRECHOS[k + 1][0]["t0"] - 0.08 if k + 1 < len(TRECHOS) else 1e9
        a1 = min(prox, tr[-1]["t1"] + 0.45)
        if not (a0 <= t < a1):
            continue
        u = ease_out((t - a0) / 0.14); sai = clamp((a1 - t) / 0.08)
        pal = [w["txt"].rstrip(",.:;") for w in tr]
        esp = largura(" ", size); ws = [largura(p, size) for p in pal]; tot = sum(ws) + esp * (len(pal) - 1)
        x = X_MEIO - tot / 2
        put(cv, mancha(int(tot)), X_MEIO, Y_LEG + 6, u * sai * 0.55)          # sombra macia atrás do trecho: lê até sobre a camisa branca
        for i, (p, wd) in enumerate(zip(pal, ws)):
            aceso = clamp((t - tr[i]["t0"] + 0.04) / 0.1)            # a palavra acende quando é dita
            a = u * sai * (0.42 + 0.58 * aceso)
            put(cv, texto(p, size, cor_palavra(tr, i)), x + wd / 2, Y_LEG + 8 * (1 - u), a)
            x += wd + esp
        return


# ---------------------------------------------------------------- rótulo do nível (pequeno, some depois)
def nivel(cv, t, dura=2.4):
    ini = {f["n"]: f["inicio"] for f in TEMPOS["falas"]}
    for fr, l1, l2 in NIVEIS:
        a0 = ini[fr] - 0.1; a1 = a0 + dura
        if not (a0 <= t < a1):
            continue
        u = ease_out((t - a0) / 0.35); a = u * clamp((a1 - t) / 0.45)
        i1 = texto(l1, 24, CORAL, 0, 110); i2 = texto(l2, 38, BRANCO, 2, 120)
        x = 92 + 14 * (1 - u)
        put(cv, i1, x + i1.width / 2 - 24, 312, a)
        put(cv, i2, x + i2.width / 2 - 24, 350, a * clamp((t - a0 - 0.08) / 0.25))


# ---------------------------------------------------------------- contadores (pequenos, temporários)
def _t(frase, txt):
    return [w for w in PAL if w["frase"] == frase and w["txt"].strip(".,:;!?").lower() == txt.lower()][0]["t0"]


def _entradas():
    return [
        (_t(3, "15%"), O3.icone_nota, "15%", BRANCO),
        (_t(5, "5%"), O3.icone_nota, "5%", BRANCO),
        (_t(5, "700"), O3.icone_nota, "700 mil", VERDE),
        (_t(6, "42"), O3.icone_sirene, "42", BRANCO),
        (_t(7, "950"), O3.icone_nota, "−950", CORAL),
        (_t(10, "5"), O3.icone_nota, "5 mi", VERDE),
        (_t(11, "80%"), O3.icone_nota, "80%", VERDE),
        (_t(13, "só"), O3.icone_cadeado, "14/15", CORAL),
    ]


X_HUD, Y_HUD = 945, 318


def _hud(cv, t, a0, a1, ic, txt, cor, pulo=1.0):
    u = ease_out((t - a0) / 0.2); a = u * clamp((a1 - t) / 0.3)
    num = texto(txt, int(46 * pulo), cor, 2, 130); icone = ic(34)
    w = icone.width + 6 + num.width - 48
    x0 = X_HUD - w + 18 * (1 - u)
    put(cv, icone, x0 + icone.width / 2, Y_HUD, a)
    put(cv, num, x0 + icone.width + 6 + num.width / 2 - 24, Y_HUD, a)


def contadores(cv, t):
    a0 = _t(1, "salário"); t0 = a0 + 0.15; t1 = _t(1, "dia") - 0.05; b = t1 + 1.6
    if a0 <= t < b:                                            # o salário sobe de 100 em 100 até 1.200
        pos = clamp((t - t0) / (t1 - t0)); k = 0 if t < t0 else min(12, 1 + int(12 * pos))
        tk = t0 + (t1 - t0) * max(0, k - 1) / 11 if k else a0
        pulo = 1.0 + 0.1 * max(0.0, 1 - (t - tk) / 0.12) if k else 1.0
        _hud(cv, t, a0, b, O3.icone_nota, f"{k * 100:,}".replace(",", "."), VERDE, pulo)
    ents = _entradas()
    for i, (a0, ic, txt, cor) in enumerate(ents):
        a1 = min(a0 + 2.2, ents[i + 1][0] - 0.05) if i + 1 < len(ents) else TEMPOS["total"] - 0.6
        if a0 - 0.05 <= t < a1:
            _hud(cv, t, a0 - 0.05, a1, ic, txt, cor)


def frame(t):
    cv = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    nivel(cv, t); contadores(cv, t); legenda(cv, t)
    if t > TEMPOS["total"] - 0.6:
        v = clamp((t - (TEMPOS["total"] - 0.6)) / 0.5)
        cv.alpha_composite(Image.new("RGBA", (W, H), (0, 0, 0, int(255 * v))))
    return cv


def main():
    a = sys.argv[1:]
    if "--preview" in a:
        out = a[a.index("--preview") + 1]; os.makedirs(out, exist_ok=True)
        fundo = a[a.index("--fundo") + 1] if "--fundo" in a else None
        for t in [float(x) for x in a[a.index("--preview") + 2].split(",")]:
            if fundo:
                bg = Image.open(f"{fundo}").convert("RGBA").resize((W, H))
            else:
                bg = Image.new("RGBA", (W, H), (61, 104, 114, 255))
            bg.alpha_composite(frame(t))
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
