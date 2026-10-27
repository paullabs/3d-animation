"""python3 ficha_narrador_montar.py PASTA SAIDA.png"""
import sys, textwrap
from PIL import Image, ImageDraw, ImageFont
P, OUT = sys.argv[1], sys.argv[2]
F = "/System/Library/Fonts/Avenir Next.ttc"
fT, fS, fL = (ImageFont.truetype(F, n, index=i) for n, i in ((44, 0), (24, 2), (20, 0)))
BG, INK, SUB, AMB = (34, 38, 34), (236, 232, 218), (170, 168, 152), (217, 182, 106)
ims = [("De frente", "frente"), ("De três quartos", "tres_quartos"), ("Pedalando (de lado)", "bicicleta")]
W, H, G, M = 600, 900, 20, 40
im = Image.new("RGB", (M * 2 + 3 * W + 2 * G, 1260), BG); d = ImageDraw.Draw(im)
d.text((M, 30), "O abrigo · o narrador (\"eu\")", font=fT, fill=INK)
d.text((M, 92), "Personagem novo, pedido de 25/10/2026 (abrir o filme de frente para quem pedala). É o dono das mãos de primeira pessoa: a mesma blusa de lã vermelha escura com punho canelado.", font=fL, fill=SUB)
for i, (t, f) in enumerate(ims):
    x = M + i * (W + G)
    im.paste(Image.open(f"{P}/{f}.png").convert("RGB").resize((W, H)), (x, 140)); d.rectangle((x - 1, 139, x + W, 140 + H), outline=(70, 74, 66))
    d.text((x, 1055), t, font=fS, fill=AMB)
notas = ["Blusa vermelha escura (#6e2422), calça jeans escura, cabelo curto e escuro, cabeça preta e olhos brancos como o resto do elenco.",
         "Só aparece de frente no plano 1A (pedalando para a câmera, de cabeça erguida para a sirene) e correndo no meio da multidão em 1E, 1F e 2A. Do resto do filme, só as mãos.",
         "O vermelho da blusa é escuro de propósito: o único vermelho vivo do filme continua sendo o suéter da Pipoca."]
y = 1100
for n in notas:
    for ln in textwrap.wrap(n, 150):
        d.text((M, y), ln, font=fL, fill=INK); y += 26
    y += 6
im.save(OUT); print("ok", OUT, im.size)
