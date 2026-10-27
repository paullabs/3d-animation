"""Monta as pranchas do storyboard de "O abrigo": uma faixa por cena (título, fala e mensagem) com os quadros de cada plano e,
embaixo de cada quadro, o plano, o tempo, a lente e o trecho da fala. Lê a decupagem (md) e as legendas dos planos no story_abrigo.py.
python3 story_montar_abrigo.py PASTA_DOS_QUADROS DECUPAGEM.md SAIDA_PREFIXO"""
import re, sys, textwrap
from PIL import Image, ImageDraw, ImageFont
Q, MD, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
F = "/System/Library/Fonts/Avenir Next.ttc"
fT, fS, fQ, fC, fL = (ImageFont.truetype(F, n, index=i) for n, i in ((44, 0), (26, 5), (24, 2), (22, 0), (20, 2)))
BG, INK, SUB, AMB = (34, 38, 34), (236, 232, 218), (170, 168, 152), (217, 182, 106)
src = open("story_abrigo.py").read()
PL = {m[0]: (m[1], m[2]) for m in re.findall(r'@plano\("([^"]+)", "([^"]+)", "([^"]+)"\)', src)}
md = open(MD).read()
cenas = []
for bloco in re.split(r"\n### ", md)[1:]:
    cab = bloco.split("\n")[0]
    m = re.match(r"(\d+)\. (.+?) \((.+?)\)", cab)
    if not m:
        continue
    n, titulo, faixa = int(m.group(1)), m.group(2), m.group(3)
    fala = re.search(r"\*\"(.+?)\"\*", bloco).group(1)
    msg = re.search(r"\*\*Mensagem:\*\* (.+)", bloco).group(1)
    tempos = {}
    for r in re.findall(r"^\| (\d+[A-Z][^|]*?) \| ([\d,]+ a [\d,]+) \|", bloco, re.M):
        tempos[r[0].strip()] = r[1]
    cenas.append((n, titulo, faixa, fala, msg, tempos))
ORDEM = {1: ["1A", "1B", "1C", "1D"], 2: ["2A", "2B", "2C", "2D"], 3: ["3A", "3B", "3C", "3D"], 4: ["4A", "4B", "4C"], 5: ["5A", "5B", "5C"],
         6: ["6A", "6A2", "6B", "6C", "6D"], 7: ["7A", "7B", "7C", "7C2"], 8: ["8A", "8B"], 9: ["9A", "9B", "9C"], 10: ["10A", "10B", "10C"], 11: ["11A", "11B"]}
EXTRA = {"3A": "3A–3C", "3B": "3A–3C", "3C": "3A–3C", "6A2": "6A", "7C2": "7C"}
TW, TH, GAP, M = 300, 533, 22, 50
COLS = 5
W = M * 2 + COLS * TW + (COLS - 1) * GAP


def faixa_cena(c):
    n, titulo, faixa, fala, msg, tempos = c
    pls = ORDEM[n]
    im = Image.new("RGB", (W, 2000), BG); d = ImageDraw.Draw(im)
    y = 30
    d.text((M, y), f"{n}. {titulo}", font=fT, fill=INK); d.text((M + d.textlength(f"{n}. {titulo}", font=fT) + 20, y + 14), faixa, font=fS, fill=SUB); y += 64
    for ln in textwrap.wrap("“" + fala + "”", 88):
        d.text((M, y), ln, font=fQ, fill=INK); y += 32
    for ln in textwrap.wrap("Mensagem: " + msg, 95):
        d.text((M, y), ln, font=fL, fill=AMB); y += 28
    y += 14
    for i, pl in enumerate(pls):
        x = M + i * (TW + GAP)
        q = Image.open(f"{Q}/{pl}.png").convert("RGB").resize((TW, TH), Image.LANCZOS)
        im.paste(q, (x, y)); d.rectangle((x - 1, y - 1, x + TW, y + TH), outline=(70, 74, 66), width=1)
        lente, txt = PL[pl]
        t = tempos.get(EXTRA.get(pl, pl), "")
        yy = y + TH + 10
        d.text((x, yy), f"{pl}" + (f"  ·  {t} s" if t else ""), font=fC, fill=AMB); yy += 30
        for ln in textwrap.wrap(lente, 30):
            d.text((x, yy), ln, font=fL, fill=INK); yy += 26
        for ln in textwrap.wrap("“" + txt + "”", 30):
            d.text((x, yy), ln, font=fL, fill=SUB); yy += 26
    return im.crop((0, 0, W, y + TH + 150))


grupos = [(1, 2), (3, 4, 5), (6, 7, 8), (9, 10, 11)]
for gi, g in enumerate(grupos):
    fx = [faixa_cena(c) for c in cenas if c[0] in g]
    H = sum(f.height for f in fx) + 120
    pr = Image.new("RGB", (W, H), BG); d = ImageDraw.Draw(pr)
    d.text((M, 34), f"O abrigo · storyboard ({gi + 1}/4)", font=fT, fill=INK)
    y = 110
    for f in fx:
        pr.paste(f, (0, y)); y += f.height
        d.line((M, y - 20, W - M, y - 20), fill=(70, 74, 66), width=2)
    pr.save(f"{OUT}-{gi + 1}.png"); print("ok", f"{OUT}-{gi + 1}.png", pr.size)
