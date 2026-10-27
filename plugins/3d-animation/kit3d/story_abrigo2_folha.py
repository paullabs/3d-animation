"""Folha de contato de revisão do storyboard da parte 2: python3 story_abrigo2_folha.py PASTA SAIDA.png ID [ID ...] [--cols 4] [--w 270]
Cada plano vira um quadro (e, se existir <id>_fim.png, um segundo quadro ao lado, com um traço no meio); legenda com o id e o tempo."""
import os, sys, json
from PIL import Image, ImageDraw, ImageFont
a = sys.argv[1:]
pasta, saida = a[0], a[1]
ids = [x for i, x in enumerate(a[2:], 2) if not x.startswith("--") and a[i - 1] not in ("--cols", "--w")]
cols = int(a[a.index("--cols") + 1]) if "--cols" in a else 4
W = int(a[a.index("--w") + 1]) if "--w" in a else 270
H = int(W * 16 / 9)
RAIZ = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
META = json.load(open(f"{RAIZ}/roteiros/abrigo2_planos.json"))["planos"]
F = ImageFont.truetype("/System/Library/Fonts/Avenir Next.ttc", 17, index=2)
celulas = []
for i in ids:
    ims = []
    for suf in ("", "_fim"):
        p = f"{pasta}/{i}{suf}.png"
        if os.path.exists(p):
            ims.append(Image.open(p).convert("RGB").resize((W, H)))
    if ims:
        celulas.append((i, ims))
cw = lambda ims: len(ims) * W + (len(ims) - 1) * 4
lins = []
cur, curw = [], 0
for c in celulas:
    w = cw(c[1]) + 10
    if cur and curw + w > cols * (W + 10):
        lins.append(cur); cur, curw = [], 0
    cur.append(c); curw += w
if cur:
    lins.append(cur)
Wt = max(sum(cw(c[1]) + 10 for c in l) for l in lins) + 10
im = Image.new("RGB", (Wt, len(lins) * (H + 34) + 10), (28, 30, 28)); d = ImageDraw.Draw(im)
y = 8
for l in lins:
    x = 10
    for i, ims in l:
        for k, q in enumerate(ims):
            im.paste(q, (x + k * (W + 4), y + 26))
        m = META.get(i, {})
        d.text((x, y + 2), f"{i}  {m.get('t0', '')}-{m.get('t1', '')}  {m.get('palavras', '')[:28]}", font=F, fill=(236, 214, 150))
        x += cw(ims) + 10
    y += H + 34
im.save(saida); print(saida, im.size)
