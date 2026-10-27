"""Legenda de "os passos" (pedido de 26/10/2026: "bota a legenda palavra por palavra no centro, apenas uma palavra por vez, com efeito de bounce").
UMA palavra por vez, no centro da tela, Avenir Next Heavy, branca com contorno escuro grosso (lê sobre ônibus branco, céu e espaço); as palavras de número e de
ordem ficam em âmbar. Cada palavra entra com um bounce de mola (nasce a 55%, passa de 110% e assenta em ~0,25 s) no quadro em que a voz a diz (palavras.json)
e fica até a próxima; numa pausa longa some logo depois da palavra. O texto sai de um stream de quadros RGBA (faixa de 1080x420) que o ffmpeg sobrepõe ao filme,
na MESMA passada do Fuji (um encode só, sem perda extra).
python3 legenda_passos.py SAIDA.mp4 [--fuji 0.5 | --sem-fuji] [--audio ARQ.wav] [--teste T SAIDA.png]"""
import os, sys, json, math, subprocess, glob
import numpy as np
from PIL import Image, ImageDraw, ImageFont

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.abspath(os.path.join(AQUI, ".."))
FPS = 24
LARG, ALT = 1080, 300                                         # a faixa da legenda (pequena, perto da parte de baixo do quadro)
Y0 = 1920 - ALT - 230                                         # 230 px de margem embaixo (fica abaixo do corpo e acima da área do celular)
FONTE = "/System/Library/Fonts/Avenir Next.ttc"
BRANCO, AMBAR, CONTORNO = (255, 255, 255), (255, 210, 31), (14, 16, 20)
NUMEROS = {"um", "três", "sete", "quinze", "dois", "trinta", "sessenta", "dezoito", "oitocentos", "vinte", "oito", "oitenta", "cento", "cinquenta", "doze",
           "quatrocentos", "setenta", "quarenta", "mil", "meio", "primeiro", "segundo", "terceiro", "quarto", "quinto", "nono", "décimo", "vigésimo", "oitavo",
           "décimo", "uma", "metro", "metros"}
NUMEROS -= {"metro", "metros", "uma"}                           # "metros" e "quilômetros" ficam brancos: o número é a palavra antes
PAUSA_LONGA = 0.30                                              # depois de uma palavra, se a próxima só vem depois disso, a legenda some em 0,12 s


def palavras():
    p = json.load(open(os.path.join(RAIZ, "roteiros", "voz-passos", "palavras.json")))
    out = []
    for w in p:
        t = w["txt"].strip().strip(",.:;!").strip()
        if t:
            out.append(dict(txt=t, t0=w["t0"], t1=w["t1"]))
    return out


def linha_do_tempo(ws):
    """(inicio, fim, palavra) de cada legenda: do t0 da palavra ao t0 da próxima; numa pausa longa, ao t1 + 0,12 s"""
    seg = []
    for i, w in enumerate(ws):
        ini = w["t0"]
        prox = ws[i + 1]["t0"] if i + 1 < len(ws) else w["t1"] + 0.3
        fim = prox if prox - w["t1"] <= PAUSA_LONGA else w["t1"] + 0.12
        if i + 1 < len(ws) and ws[i + 1]["t0"] < w["t0"] + 0.06:
            fim = max(fim, ini + 0.06)
        seg.append((ini, fim, w["txt"]))
    return seg


def desenha(txt, cor):
    """a palavra pronta (RGBA, fundo transparente) no tamanho máximo: o maior corpo que cabe em 820 px de largura (até 190 px)"""
    corpo = 96
    while corpo > 40:
        f = ImageFont.truetype(FONTE, corpo, index=8)
        l, t, r, b = f.getbbox(txt, stroke_width=int(corpo * 0.07))
        if r - l <= 640:
            break
        corpo -= 6
    sw = max(6, int(corpo * 0.07))
    l, t, r, b = f.getbbox(txt, stroke_width=sw)
    W, H = r - l + 2 * sw + 40, b - t + 2 * sw + 40
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sombra = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ds = ImageDraw.Draw(sombra); ds.text((20 - l + 0, 20 - t + int(corpo * 0.05)), txt, font=f, fill=(0, 0, 0, 150), stroke_width=sw, stroke_fill=(0, 0, 0, 150))
    from PIL import ImageFilter
    sombra = sombra.filter(ImageFilter.GaussianBlur(corpo * 0.04))
    im = Image.alpha_composite(im, sombra)
    d = ImageDraw.Draw(im)
    d.text((20 - l, 20 - t), txt, font=f, fill=cor, stroke_width=sw, stroke_fill=CONTORNO)
    return im


def escala(idade):
    """o bounce: nasce a 55%, passa de 110% e assenta (mola amortecida); idade em segundos desde que a palavra entrou"""
    return 1.0 - 0.45 * math.exp(-idade * 13.0) * math.cos(idade * 30.0)


def faixa_de(seg, cache, f):
    """a faixa RGBA do quadro f (0-based)"""
    t = (f + 0.5) / FPS
    atual = None
    for ini, fim, txt in seg:
        if ini <= t < fim:
            atual = (ini, txt)
    quadro = np.zeros((ALT, LARG, 4), np.uint8)
    if atual is None:
        return quadro
    ini, txt = atual
    if txt not in cache:
        cache[txt] = desenha(txt, AMBAR if txt.lower() in NUMEROS else BRANCO)
    base = cache[txt]
    idade = max(0.0, t - ini)
    s = escala(idade)
    w, h = max(2, int(base.width * s)), max(2, int(base.height * s))
    im = base.resize((w, h), Image.LANCZOS)
    op = min(1.0, idade / 0.05)
    if op < 1.0:
        a = np.array(im); a[..., 3] = (a[..., 3] * op).astype(np.uint8); im = Image.fromarray(a)
    x, y = (LARG - w) // 2, (ALT - h) // 2
    canvas = Image.new("RGBA", (LARG, ALT), (0, 0, 0, 0)); canvas.paste(im, (x, y), im)
    return np.array(canvas)


def quadros_base():
    """a lista de quadros do render cheio, na ordem do filme (a mesma da montagem)"""
    lista = os.path.join(RAIZ, "render_passos", "lista_final.txt")
    out = subprocess.run([__import__("canal38_env").BLENDER, "-b", "-P", os.path.join(AQUI, "story_passos9.py"), "--", "--list"], capture_output=True, text=True).stdout
    ids = [l.split(" | ")[0] for l in out.splitlines() if " | " in l and l.split(" | ")[0][:1].isdigit()]
    n = 0
    with open(lista, "w") as L:
        for i in ids:
            for fp in sorted(glob.glob(os.path.join(RAIZ, "render_passos", "full", i, "[0-9]*.png"))):
                L.write(f"file '{fp}'\nduration {1 / FPS:.6f}\n"); n += 1
    return lista, n


def main():
    a = sys.argv[1:]
    seg = linha_do_tempo(palavras())
    cache = {}
    if "--teste" in a:
        i = a.index("--teste"); t = float(a[i + 1]); saida = a[i + 2]
        f = int(round(t * FPS))
        lista, n = quadros_base()
        base = subprocess.run(["ffmpeg", "-v", "error", "-f", "concat", "-safe", "0", "-i", lista, "-vf", f"select=eq(n\\,{f})", "-frames:v", "1", "-f", "image2pipe", "-vcodec", "png", "-"], capture_output=True).stdout
        import io
        im = Image.open(io.BytesIO(base)).convert("RGBA")
        im.alpha_composite(Image.fromarray(faixa_de(seg, cache, f)), (0, Y0)); im.convert("RGB").save(saida); print("ok", saida); return
    saida = a[0]
    fuji = None if "--sem-fuji" in a else float(a[a.index("--fuji") + 1]) if "--fuji" in a else 0.5
    audio = a[a.index("--audio") + 1] if "--audio" in a else os.path.join(RAIZ, "roteiros", "som-passos", "mix_v2.wav")
    lista, n = quadros_base()
    sys.path.insert(0, AQUI)
    if fuji is None:
        grafo = "[0:v]fps=24,format=yuv420p[fx];[fx][1:v]overlay=0:%d:format=auto,format=yuv420p[v]" % Y0
    else:
        import pos_fuji
        g = pos_fuji.grafo(fuji).replace("[0:v]", "[0:v]fps=24,", 1)
        grafo = g + "[fx];[fx][1:v]overlay=0:%d:format=auto,format=yuv420p[v]" % Y0
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lista,
           "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{LARG}x{ALT}", "-r", str(FPS), "-i", "-",
           "-i", audio, "-filter_complex", grafo, "-map", "[v]", "-map", "2:a", "-r", "24", "-c:v", "libx264", "-preset", "slow", "-b:v", "11M", "-maxrate", "14M",
           "-bufsize", "22M", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "256k", "-shortest", saida]
    pr = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    try:
        for f in range(n + 30):
            pr.stdin.write(faixa_de(seg, cache, f).tobytes())
    except BrokenPipeError:
        pass
    finally:
        try:
            pr.stdin.close()
        except Exception:
            pass
    pr.wait()
    print("ok", saida, "quadros", n, "palavras", len(seg))


if __name__ == "__main__":
    main()
