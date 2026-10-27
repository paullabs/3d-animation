"""Monta a prancha da ficha (elenco + objetos) com os nomes, a partir das renderizações de ficha_elenco.py.
python3 ficha_montar.py PASTA_DAS_RENDERS SAIDA.png "Título" """
import json, sys
from PIL import Image, ImageDraw, ImageFont

S, SAIDA, TITULO = sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else "Ficha do elenco e dos objetos"
F = "/System/Library/Fonts/Avenir Next.ttc"
fT, fN, fS, fP = ImageFont.truetype(F, 66, index=0), ImageFont.truetype(F, 30, index=2), ImageFont.truetype(F, 32, index=5), ImageFont.truetype(F, 27, index=2)
NOMES = {"presidente": "Presidente", "juiz": "Juiz", "juiza": "Juíza", "deputado": "Deputado", "empreiteiro": "Empreiteiro", "policial": "Policial",
         "fiscal": "Fiscal da alfândega", "diplomata": "Diplomata", "trabalhador": "Trabalhador", "contador": "Contador",
         "notinha = 1 salário mínimo": "notinha\n1 salário mínimo", "maço = R$ 1 milhão": "maço\nR$ 1 milhão", "livro do orçamento": "livro do\norçamento",
         "faixa presidencial": "faixa\npresidencial", "estojo de joias": "estojo\nde joias", "pasta confidencial": "pasta\nconfidencial",
         "tribuna com microfones": "tribuna com\nmicrofones", "cadeira presidencial": "cadeira\npresidencial", "relógio de ouro": "relógio\nde ouro"}
AJUSTE = {"carrinho de mão": (0, -120), "martelo": (0, 40)}         # rótulos que encostariam em outro objeto
W = 3600
BLOCOS = [("elenco_frente", "Elenco de frente, na mesma escala. Cada um com silhueta, figurino e objeto próprios", (0, 260, 4800, 1250), 1400, 4800),
          ("elenco_q", "De 3/4, com a expressão de cada um", (0, 260, 4800, 1250), 1400, 4800),
          ("obj_dinheiro", "Dinheiro: unidades e onde ele se esconde", (0, 280, 3600, 1500), 2000, 3600),
          ("obj_poder", "Poder e cenário", (0, 180, 3600, 1450), 2000, 3600),
          ("obj_pequenos", "Objetos de cena (fora de escala)", (0, 650, 3600, 1650), 2000, 3600)]
imgs = []
for nome, sub, crop, alt, larg in BLOCOS:
    im = Image.open(f"{S}/{nome}.png").convert("RGB").crop(crop)
    k = W / im.width
    imgs.append((nome, sub, crop, alt, larg, im.resize((W, int(im.height * k))), k))
cab = 190
sheet = Image.new("RGB", (W, cab + sum(i[5].height + 60 for i in imgs)), (201, 194, 180)); d = ImageDraw.Draw(sheet)
d.text((80, 60), TITULO, font=fT, fill=(30, 28, 26))
y = cab
for nome, sub, crop, alt, larg, im, k in imgs:
    d.text((80, y + 6), sub, font=fS, fill=(60, 56, 52)); y += 50
    sheet.paste(im, (0, y))
    for rot, x, yy in json.load(open(f"{S}/{nome}.png.json")):
        t = NOMES.get(rot, rot); dx, dy = AJUSTE.get(rot, (0, 0))
        px = x * larg * k + dx; py = (yy * alt - crop[1]) * k + dy
        fnt = fN if nome.startswith("elenco") else fP
        lw = max(d.textlength(l, font=fnt) for l in t.split("\n"))
        d.multiline_text((px - lw / 2, y + py + (6 if nome.startswith("elenco") else 0)), t, font=fnt, fill=(30, 28, 26), align="center")
    y += im.height + 10
sheet.save(SAIDA)
print("ok", SAIDA, sheet.size)
