"""Monta a ficha do reflexo (elenco + objetos) com os nomes. python3 ficha_montar_reflexo.py PASTA SAIDA.png"""
import json, sys
from PIL import Image, ImageDraw, ImageFont
S, SAIDA = sys.argv[1], sys.argv[2]
F = "/System/Library/Fonts/Avenir Next.ttc"
fT, fN, fS, fP = ImageFont.truetype(F, 66, index=0), ImageFont.truetype(F, 30, index=2), ImageFont.truetype(F, 32, index=5), ImageFont.truetype(F, 27, index=2)
W = 3100
BLOCOS = [("elenco_frente", "Elenco de frente: \"você\" em três figurinos (casa, goleiro, velocista) e quem cruza o seu caminho", (0, 280, 3100, 1150), 1400, 3100),
          ("elenco_q", "De 3/4, com a expressão de cada um", (0, 280, 3100, 1150), 1400, 3100),
          ("pequenos", "Objetos pequenos, fora de escala (na cena entram com o tamanho real)", (0, 440, 3300, 1000), 1300, 3300),
          ("cenario", "Cenário e torcida (fora de escala)", (0, 140, 4300, 1000), 1400, 4300)]
imgs = []
for nome, sub, crop, alt, larg in BLOCOS:
    im = Image.open(f"{S}/{nome}.png").convert("RGB").crop(crop)
    k = W / im.width
    imgs.append((nome, sub, crop, alt, larg, im.resize((W, int(im.height * k))), k))
cab = 190
sheet = Image.new("RGB", (W, cab + sum(i[5].height + 60 for i in imgs)), (201, 194, 180)); d = ImageDraw.Draw(sheet)
d.text((80, 60), "E se o seu cérebro fosse 10 vezes mais rápido? Ficha de elenco e objetos", font=fT, fill=(30, 28, 26))
y = cab
for nome, sub, crop, alt, larg, im, k in imgs:
    d.text((80, y + 6), sub, font=fS, fill=(60, 56, 52)); y += 50
    sheet.paste(im, (0, y))
    for rot, x, yy in json.load(open(f"{S}/{nome}.png.json")):
        px = x * larg * k; py = (yy * alt - crop[1]) * k
        fnt = fN if nome.startswith("elenco") else fP
        lw = max(d.textlength(l, font=fnt) for l in rot.split("\n"))
        d.multiline_text((px - lw / 2, y + py + 6), rot, font=fnt, fill=(30, 28, 26), align="center")
    y += im.height + 70
sheet = sheet.crop((0, 0, W, y)); sheet.save(SAIDA)
print("ok", SAIDA, sheet.size)
