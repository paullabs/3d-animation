"""Monta a prancha do herói em 3D (3 figurinos x 4 ângulos). python3 ficha_montar_3d.py PASTA SAIDA.png"""
import sys
from PIL import Image, ImageDraw, ImageFont
S, SAIDA = sys.argv[1], sys.argv[2]
F = "/System/Library/Fonts/Avenir Next.ttc"
fT, fS, fN = ImageFont.truetype(F, 60, index=0), ImageFont.truetype(F, 34, index=5), ImageFont.truetype(F, 30, index=2)
W = 3100
LIN = [("casa", "Você (em casa)"), ("goleiro", "Você (goleiro, em guarda)"), ("menino", "Menino pegador de bolas (escala 0,72)")]
ANG = ["de frente", "3/4", "de lado", "de costas"]
imgs = [Image.open(f"{S}/{n}.png").convert("RGB").crop((0, 250, 3100, 1080)) for n, _ in LIN]
cab = 170
sheet = Image.new("RGB", (W, cab + sum(i.height + 70 for i in imgs)), (201, 194, 180)); d = ImageDraw.Draw(sheet)
d.text((80, 50), "O herói em 3D de verdade: mesmo desenho, com volume e câmera livre", font=fT, fill=(30, 28, 26))
y = cab
for (n, nome), im in zip(LIN, imgs):
    d.text((80, y), nome, font=fS, fill=(60, 56, 52)); y += 50
    sheet.paste(im, (0, y))
    for i, a in enumerate(ANG):
        x = 3100 / 2 + (-3.0 + i * 2.0) * 387.5
        d.text((x - d.textlength(a, font=fN) / 2, y + im.height - 40), a, font=fN, fill=(30, 28, 26))
    y += im.height + 20
sheet = sheet.crop((0, 0, W, y)); sheet.save(SAIDA); print("ok", SAIDA, sheet.size)
