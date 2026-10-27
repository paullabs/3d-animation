"""junta os quadros de teste de uma cena numa tira: python3 sheet.py PASTA PREFIXO SAIDA.jpg"""
import sys, glob
from PIL import Image
fs = sorted(glob.glob(f"{sys.argv[1]}/{sys.argv[2]}_*.png"))
ims = [Image.open(f).convert("RGB") for f in fs]
w, h = ims[0].size; out = Image.new("RGB", (w * len(ims), h))
for i, im in enumerate(ims): out.paste(im, (i * w, 0))
k = min(1.0, 2000 / out.width); out = out.resize((int(out.width * k), int(out.height * k))); out.save(sys.argv[3]); print(len(ims), out.size)
