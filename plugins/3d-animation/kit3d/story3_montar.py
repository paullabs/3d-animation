"""Monta as pranchas do storyboard v3 de "O abrigo": uma faixa por fala (título, tempo, fala e mensagem) com um quadro por plano e, embaixo de
cada quadro, o plano, o tempo (início a fim e duração), a lente e o trecho da fala. Tudo vem do SHOTS (story3_abrigo.py --json).
python3 story3_montar.py PASTA_DOS_QUADROS META.json SAIDA_PREFIXO"""
import json, sys, textwrap
from PIL import Image, ImageDraw, ImageFont
Q, META, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
S = json.load(open(META))
R = json.load(open((__import__("canal38_env").RAIZ + "/roteiros/abrigo.json")))
T = json.load(open((__import__("canal38_env").RAIZ + "/roteiros/voz-abrigo/tempos.json")))
FAL = [f["fala"] for b in R["blocos"] for f in b["falas"]]
TIT = {1: "A corrida", 2: "A porta", 3: "Os primeiros dias", 4: "A comida acaba", 5: "O banheiro", 6: "A Pipoca", 7: "Os meses", 8: "O baralho", 9: "A porta de novo", 10: "Lá fora", 11: "O preço"}
MSG = {1: "um dia comum que acaba de uma vez; só existe um lugar para ir.", 2: "a escolha do Zé. A porta vira um muro entre quem vive e quem fica.",
       3: "alívio. A lista do que garante a vida, que depois vai acabar.", 4: "a conta não fecha, e todo mundo percebe.", 5: "o abrigo começa a apodrecer.",
       6: "o horror fica sugerido, não mostrado. A culpa é de todos, pelo silêncio.", 7: "o tempo gasta as pessoas. A morte é contada por uma ausência.",
       8: "a solidão vira loucura mansa.", 9: "não dá mais para ficar. A porta abre.", 10: "o mundo acabou; só um objeto da vida antes resistiu.", 11: "sobreviver não foi ganhar."}
F = "/System/Library/Fonts/Avenir Next.ttc"
fT, fS, fQ, fC, fL = (ImageFont.truetype(F, n, index=i) for n, i in ((44, 0), (26, 5), (24, 2), (22, 0), (20, 2)))
BG, INK, SUB, AMB = (34, 38, 34), (236, 232, 218), (170, 168, 152), (217, 182, 106)
TW, TH, GAP, M, COLS = 300, 533, 18, 40, 6
W = M * 2 + COLS * TW + (COLS - 1) * GAP


def ids_da_fala(n):
    return [k for k in S if k[:-1].isdigit() and int(k.rstrip("ABCDEFGHIJK")) == n]


def faixa(n):
    ids = ids_da_fala(n)
    lin = (len(ids) + COLS - 1) // COLS
    im = Image.new("RGB", (W, 230 + lin * (TH + 190)), BG); d = ImageDraw.Draw(im)
    f = T["falas"][n - 1]
    t0, t1 = S[ids[0]]["t0"], S[ids[-1]]["t1"]
    y = 24
    d.text((M, y), f"{n}. {TIT[n]}", font=fT, fill=INK)
    d.text((M + d.textlength(f"{n}. {TIT[n]}", font=fT) + 20, y + 14), f"{t0:.1f} a {t1:.1f} s  ·  {len(ids)} planos", font=fS, fill=SUB); y += 62
    for ln in textwrap.wrap("“" + FAL[n - 1] + "”", 110):
        d.text((M, y), ln, font=fQ, fill=INK); y += 32
    for ln in textwrap.wrap("Mensagem: " + MSG[n], 120):
        d.text((M, y), ln, font=fL, fill=AMB); y += 28
    y += 12
    for i, k in enumerate(ids):
        c, r = i % COLS, i // COLS
        x, yy = M + c * (TW + GAP), y + r * (TH + 190)
        q = Image.open(f"{Q}/{k}.png").convert("RGB").resize((TW, TH), Image.LANCZOS)
        im.paste(q, (x, yy)); d.rectangle((x - 1, yy - 1, x + TW, yy + TH), outline=(70, 74, 66), width=1)
        s = S[k]; dur = s["t1"] - s["t0"]
        ty = yy + TH + 8
        d.text((x, ty), f"{k}  ·  {s['t0']:.2f}–{s['t1']:.2f} s", font=fC, fill=AMB); ty += 28
        d.text((x, ty), f"({dur:.2f} s)", font=fL, fill=SUB); ty += 24
        for ln in textwrap.wrap(s["lente"], 27)[:3]:
            d.text((x, ty), ln, font=fL, fill=INK); ty += 24
        for ln in textwrap.wrap("“" + s["palavras"] + "”", 27)[:2]:
            d.text((x, ty), ln, font=fL, fill=SUB); ty += 24
    return im.crop((0, 0, W, y + lin * (TH + 190)))


grupos = [(1, 2), (3, 4, 5), (6, 7), (8, 9, 10, 11)]
for gi, g in enumerate(grupos):
    fx = [faixa(n) for n in g]
    H = sum(f.height for f in fx) + 110
    pr = Image.new("RGB", (W, H), BG); d = ImageDraw.Draw(pr)
    d.text((M, 30), f"O abrigo · storyboard v3 ({gi + 1}/4)", font=fT, fill=INK)
    y = 100
    for f in fx:
        pr.paste(f, (0, y)); y += f.height
        d.line((M, y - 14, W - M, y - 14), fill=(70, 74, 66), width=2)
    pr.save(f"{OUT}-{gi + 1}.png"); print("ok", f"{OUT}-{gi + 1}.png", pr.size)
