"""Camada de texto do vídeo do presidente corrupto (mesma régua do PCC v7): textos discretos, que entram, dizem e saem.
- Legenda: trechos curtos (até 3 palavras), em caixa normal, Demi Bold 46 px, sombra macia em vez de contorno grosso.
  O trecho inteiro aparece apagado e cada palavra acende quando é dita; dinheiro em verde, outros números em âmbar.
- Rótulo do nível: pequeno, no canto de cima à esquerda, aparece por 2,4 s quando o nível começa e some.
- Contadores (ícone + número): menores, no canto de cima à direita, ficam só 2,2 s.
- Rostos (23/10/2026): nada de texto na frente de um rosto. O render grava onde estão as cabeças (rostos.py -> rostos.json);
  cada trecho de legenda, rótulo e contador escolhe o primeiro lugar livre de rostos durante todo o tempo em que fica na tela.
python3 overlay_presidente.py SAIDA.mov --rostos PASTA_DO_RENDER [--preview DIR t1,t2,...]"""
import json, os, subprocess, sys, math
from functools import lru_cache
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import overlay_pcc3 as O3
import glob

FPS = 24; W, H = 1080, 1920
VOZ = (__import__("canal38_env").RAIZ + "/roteiros/voz-presidente")
FONT = "/System/Library/Fonts/Avenir Next.ttc"
PAL = json.load(open(VOZ + "/palavras.json"))
TEMPOS = json.load(open(VOZ + "/tempos.json"))
BRANCO, CORAL, VERDE, AMBAR = (255, 255, 255, 255), (255, 176, 140, 255), (142, 229, 155, 255), (255, 214, 140, 255)
Y_LEG = 1310; X_MEIO = W / 2 - 27                           # centro da área segura
NIVEIS = [(3, "NÍVEL 1", "O Congresso"), (5, "NÍVEL 2", "A estatal"), (7, "NÍVEL 3", "A empreiteira"), (9, "NÍVEL 4", "O orçamento"),
          (11, "NÍVEL 5", "O topo"), (13, "NO FIM", "O preço")]
DINHEIRO = ("reais", "mil", "milhões")
clamp, ease_out, put = O3.clamp, O3.ease_out, O3.put


# ---------------------------------------------------------------- rostos (texto nunca na frente de um rosto)
ROSTOS = {}                                    # quadro do Blender -> [(x0, y0, x1, y1) em px de 1080x1920]
FOLGA = 22


def carrega_rostos(pasta):
    """rostos.json de cada cena (gravado no render por rostos.py)"""
    for arq in glob.glob(os.path.join(pasta, "*", "rostos.json")):
        j = json.load(open(arq)); passo = j["passo"]
        for q, lst in j["quadros"].items():
            caixas = [(b[0] * W - FOLGA, b[1] * H - FOLGA, b[2] * W + FOLGA, b[3] * H + FOLGA) for b in lst]
            for d in range(passo):
                ROSTOS.setdefault(int(q) + d, []).extend(caixas)


def sobra(r, a0, a1):
    """quanto do retângulo r cobre rostos entre a0 e a1 (soma das áreas em comum, quadro a quadro)"""
    tot = 0.0
    for f in range(int(a0 * FPS) + 1, int(a1 * FPS) + 2):
        for b in ROSTOS.get(f, ()):
            dx = min(r[2], b[2]) - max(r[0], b[0]); dy = min(r[3], b[3]) - max(r[1], b[1])
            if dx > 0 and dy > 0:
                tot += dx * dy
    return tot


def escolhe(cands, a0, a1):
    """o primeiro lugar livre de rostos; se nenhum estiver livre, o que cobre menos"""
    custos = [(sobra(r, a0, a1), i) for i, (r, _) in enumerate(cands)]
    for c, i in custos:
        if c == 0:
            return cands[i][1]
    return cands[min(custos)[1]][1]


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


Y_LEGS = (Y_LEG, 1185, 470)                     # embaixo (padrão), um pouco acima, ou lá em cima se o rosto estiver embaixo


@lru_cache(maxsize=512)
def y_legenda(k, a0, a1, tot):
    cands = [((X_MEIO - tot / 2 - 30, y - 42, X_MEIO + tot / 2 + 30, y + 42), y) for y in Y_LEGS]
    return escolhe(cands, a0, a1)


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
        x = X_MEIO - tot / 2; Y = y_legenda(k, a0, a1, int(tot))
        put(cv, mancha(int(tot)), X_MEIO, Y + 6, u * sai * 0.55)          # sombra macia atrás do trecho: lê até sobre a camisa branca
        for i, (p, wd) in enumerate(zip(pal, ws)):
            aceso = clamp((t - tr[i]["t0"] + 0.04) / 0.1)            # a palavra acende quando é dita
            a = u * sai * (0.42 + 0.58 * aceso)
            put(cv, texto(p, size, cor_palavra(tr, i)), x + wd / 2, Y + 8 * (1 - u), a)
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
        x0, y0 = lugar_nivel(fr, a0, a1, i2.width - 48)
        x = x0 + 14 * (1 - u)
        put(cv, i1, x + i1.width / 2 - 24, y0, a)
        put(cv, i2, x + i2.width / 2 - 24, y0 + 38, a * clamp((t - a0 - 0.08) / 0.25))


@lru_cache(maxsize=64)
def lugar_nivel(fr, a0, a1, larg):
    """canto de cima à esquerda; se houver rosto ali, desce para perto da legenda"""
    cands = [((x - 10, y - 30, x + larg + 20, y + 62), (x, y)) for x, y in ((92, 312), (92, 1090), (988 - larg, 312))]
    return escolhe(cands, a0, a1)


# ---------------------------------------------------------------- contadores (pequenos, temporários)
def _t(frase, txt):
    return [w for w in PAL if w["frase"] == frase and w["txt"].strip(".,:;!?").lower() == txt.lower()][0]["t0"]


@lru_cache(maxsize=8)
def icone_calendario(h=44):
    w = int(h * 0.9); im = Image.new("RGBA", (w + 12, h + 12), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((6, 6, 6 + w, 6 + h), radius=5, fill=(246, 241, 228, 255))
    d.rounded_rectangle((6, 6, 6 + w, 6 + int(h * 0.3)), radius=5, fill=(226, 54, 75, 255))
    return im


@lru_cache(maxsize=8)
def icone_ampulheta(h=44):
    w = int(h * 0.7); im = Image.new("RGBA", (w + 12, h + 12), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.polygon([(6, 6), (6 + w, 6), (6 + w // 2, 6 + h // 2), (6 + w, 6 + h), (6, 6 + h), (6 + w // 2, 6 + h // 2)], fill=(255, 214, 140, 255))
    d.rectangle((4, 4, 8 + w, 9), fill=(230, 232, 245, 255)); d.rectangle((4, 3 + h, 8 + w, 8 + h), fill=(230, 232, 245, 255))
    return im


@lru_cache(maxsize=8)
def icone_pino(h=44):
    w = int(h * 0.75); im = Image.new("RGBA", (w + 12, h + 12), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.ellipse((6, 6, 6 + w, 6 + w), fill=(127, 230, 255, 255)); d.polygon([(8, 6 + w * 0.7), (4 + w, 6 + w * 0.7), (6 + w // 2, 6 + h)], fill=(127, 230, 255, 255))
    d.ellipse((6 + w * 0.3, 6 + w * 0.3, 6 + w * 0.7, 6 + w * 0.7), fill=(10, 22, 27, 255))
    return im


def _entradas():
    """o número de cada proporção, no canto, com o ícone da unidade (sem palavras)"""
    nota, cad = O3.icone_nota, O3.icone_cadeado
    return [
        (_t(3, "30"), nota, "30 mil", VERDE),
        (_t(3, "100"), nota, "×100", VERDE),
        (_t(4, "25"), cad, "25", CORAL),
        (_t(5, "1%"), nota, "1–3%", BRANCO),
        (_t(5, "30"), nota, "30 mi", VERDE),
        (_t(6, "6"), nota, "6 bi", VERDE),
        (_t(6, "17"), icone_calendario, "17", BRANCO),
        (_t(7, "4"), nota, "4 bi", VERDE),
        (_t(7, "12"), icone_pino, "12", BRANCO),
        (_t(8, "17"), nota, "−17 bi", CORAL),
        (_t(9, "45"), nota, "45 bi", VERDE),
        (_t(9, "40"), icone_calendario, "40 mi", VERDE),
        (_t(11, "16"), nota, "16 mi", VERDE),
        (_t(11, "800"), icone_ampulheta, "800", BRANCO),
        (_t(13, "4"), cad, "4/7", CORAL),
    ]


X_HUD, Y_HUD = 945, 318


@lru_cache(maxsize=64)
def lugar_hud(a0, a1, w):
    """canto de cima à direita; se houver rosto, outro canto (nunca na frente da cara)"""
    pos = ((X_HUD - w, Y_HUD), (135, Y_HUD), (X_HUD - w, 1090), (135, 1090), (X_HUD - w, 470))
    return escolhe([((x - 12, y - 34, x + w + 12, y + 34), (x, y)) for x, y in pos], a0, a1)


def _hud(cv, t, a0, a1, ic, txt, cor, pulo=1.0):
    u = ease_out((t - a0) / 0.2); a = u * clamp((a1 - t) / 0.3)
    num = texto(txt, int(46 * pulo), cor, 2, 130); icone = ic(34)
    w = icone.width + 6 + num.width - 48
    xb, yb = lugar_hud(a0, a1, w)
    x0 = xb + 18 * (1 - u)
    put(cv, icone, x0 + icone.width / 2, yb, a)
    put(cv, num, x0 + icone.width + 6 + num.width / 2 - 24, yb, a)


def contadores(cv, t):
    ents = _entradas()
    for i, (a0, ic, txt, cor) in enumerate(ents):
        a1 = min(a0 + 2.2, ents[i + 1][0] - 0.05) if i + 1 < len(ents) else TEMPOS["total"] - 0.6
        corte = [f["inicio"] - 0.12 for f in TEMPOS["falas"] if f["inicio"] - 0.12 > a0]
        if corte:
            a1 = min(a1, corte[0] - 0.05)                     # o contador nunca passa para a cena seguinte
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
    if "--rostos" in a:
        carrega_rostos(a[a.index("--rostos") + 1])
        print("rostos em", len(ROSTOS), "quadros")
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
