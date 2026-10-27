"""Monta as pranchas do storyboard de "os passos": 10 planos por prancha (5 x 2), com o id, o tempo, a lente e as palavras de cada plano.
python3 story_passos2_montar.py PASTA_DOS_QUADROS SAIDA_PREFIXO      -> SAIDA_PREFIXO-1.png ...  (usa --json do story_passos2.py para os textos)"""
import sys, os, json, subprocess
from PIL import Image, ImageDraw, ImageFont
AQUI = os.path.dirname(os.path.abspath(__file__))
BL = __import__("canal38_env").BLENDER
pasta, pref = sys.argv[1], sys.argv[2]
tmp = pref + "_meta.json"
subprocess.run([BL, "-b", "-P", f"{AQUI}/story_passos2.py", "--", "--json", tmp], capture_output=True, cwd=AQUI)
meta = json.load(open(tmp)); os.remove(tmp)
ids = list(meta)
W, H = 400, 711
fnt = ImageFont.truetype("/System/Library/Fonts/Menlo.ttc", 22)
fpq = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 19)
def quebra(t, f, w, d):
    ls, cur = [], ""
    for p in t.split():
        if d.textlength((cur + " " + p).strip(), font=f) <= w:
            cur = (cur + " " + p).strip()
        else:
            ls.append(cur); cur = p
    return ls + ([cur] if cur else [])
paginas = [ids[i:i + 10] for i in range(0, len(ids), 10)]
for pi, pg in enumerate(paginas, 1):
    cols, lin, cab = 5, 2, 110
    sheet = Image.new("RGB", (cols * (W + 12) + 12, lin * (H + cab + 12) + 12), (28, 32, 30)); d = ImageDraw.Draw(sheet)
    for k, i in enumerate(pg):
        x, y = 12 + (k % cols) * (W + 12), 12 + (k // cols) * (H + cab + 12)
        im = Image.open(f"{pasta}/{i}.png").convert("RGB").resize((W, H))
        sheet.paste(im, (x, y + cab))
        m = meta[i]
        d.text((x, y), f"{i}", font=fnt, fill=(240, 190, 90))
        d.text((x + 56, y), f"{m['t0']:.1f}-{m['t1']:.1f} s  · {m['modo']} · {'palco' if m['modo'] == 'P' else m['lente'].split(',')[0]}", font=fnt, fill=(220, 220, 210))
        for j, l in enumerate(quebra("“" + m["palavras"] + "”" if m["palavras"] else "", fpq, W, d)[:3]):
            d.text((x, y + 32 + 22 * j), l, font=fpq, fill=(170, 200, 170))
    sheet.save(f"{pref}-{pi}.png"); print(f"{pref}-{pi}.png", sheet.size)
