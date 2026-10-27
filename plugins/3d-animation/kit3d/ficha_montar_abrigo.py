"""Monta a ficha de "O abrigo" (elenco + objetos) com os nomes. python3 ficha_montar_abrigo.py PASTA SAIDA.png
Corta cada prancha no que não é fundo (com margem para os rótulos) e escreve os nomes embaixo de cada item."""
import json, sys
from PIL import Image, ImageDraw, ImageFont, ImageChops
S, SAIDA = sys.argv[1], sys.argv[2]
F = "/System/Library/Fonts/Avenir Next.ttc"
fT, fN, fS, fP = ImageFont.truetype(F, 66, index=0), ImageFont.truetype(F, 30, index=2), ImageFont.truetype(F, 32, index=5), ImageFont.truetype(F, 27, index=2)
W = 3100
FUNDO = (154, 156, 142)
BLOCOS = [("elenco_frente", "2D (o traço do canal): a turma do abrigo, quem fica lá fora e a Pipoca"),
          ("elenco_q", "2D de 3/4, com o olhar cansado de cada um"),
          ("elenco3d_frente", "3D de verdade (mesmo desenho, com volume): para as cenas em que a câmera gira em volta"),
          ("elenco3d_q", "3D de 3/4"),
          ("pequenos_a", "Dentro do abrigo: bicho, água, comida (objetos fora de escala; na cena entram no tamanho real)"),
          ("pequenos_b", "Dentro do abrigo: baralho, luz, calendário de giz e as mãos de quem narra"),
          ("cenario", "Cenário: o que fica do lado de fora, a porta e os móveis")]
imgs = []
for nome, sub in BLOCOS:
    im = Image.open(f"{S}/{nome}.png").convert("RGB")
    rot = json.load(open(f"{S}/{nome}.png.json"))
    lin = im.crop((0, 0, im.width, int(im.height * 0.8)))                     # só acima do chão (a faixa escura do fundo)
    bb = ImageChops.difference(lin, Image.new("RGB", lin.size, FUNDO)).point(lambda v: 255 if v > 14 else 0).getbbox()
    x0, y0, x1, y1 = bb
    ymax = max(y1, max(int(r[2] * im.height) for r in rot) + 130)             # deixa espaço para os rótulos
    crop = (max(0, x0 - 140), max(0, y0 - 50), min(im.width, x1 + 140), min(im.height, ymax))
    c = im.crop(crop); k = W / c.width
    imgs.append((nome, sub, im.size, crop, c.resize((W, int(c.height * k))), k, rot))
AMOSTRAS = [("poeira", "#a89f86"), ("oliva", "#59603f"), ("musgo", "#46604f"), ("jeans gasto", "#4f6275"), ("concreto", "#8c8d84"), ("ferrugem", "#8a4a2c"),
            ("tijolo (a Pipoca)", "#8e302b"), ("sangue seco", "#6e2a26"), ("osso", "#d8d0bb"), ("noite", "#1e2420"), ("lâmpada (só luz)", "#d9b66a")]
cab = 190 + 250
sheet = Image.new("RGB", (W, cab + sum(i[4].height + 120 for i in imgs)), FUNDO); d = ImageDraw.Draw(sheet)
d.text((80, 60), "O abrigo: ficha de elenco e objetos (paleta pós-apocalipse, sem brilho)", font=fT, fill=(30, 28, 26))
y = 190
d.text((80, y), "Paleta: tudo apagado e barrento; só a Pipoca e o que já aconteceu têm vermelho; a luz é âmbar fraca, de lâmpada de abrigo", font=fS, fill=(40, 38, 34))
for i, (nm, cor) in enumerate(AMOSTRAS):
    x0 = 80 + i * 270
    d.rounded_rectangle((x0, y + 60, x0 + 240, y + 150), 10, fill=cor, outline=(30, 28, 24), width=2)
    d.text((x0, y + 160), nm, font=fP, fill=(30, 28, 24))
y = cab
for nome, sub, (iw, ih), crop, im, k, rot in imgs:
    d.text((80, y + 6), sub, font=fS, fill=(60, 56, 52)); y += 58
    sheet.paste(im, (0, y))
    for r, x, yy in rot:
        px = (x * iw - crop[0]) * k; py = (yy * ih - crop[1]) * k
        fnt = fN if nome.startswith("elenco") else fP
        lw = max(d.textlength(l, font=fnt) for l in r.split("\n"))
        d.multiline_text((px - lw / 2, y + py + 6), r, font=fnt, fill=(30, 28, 26), align="center")
    y += im.height + 62
sheet = sheet.crop((0, 0, W, y)); sheet.save(SAIDA)
print("ok", SAIDA, sheet.size)
