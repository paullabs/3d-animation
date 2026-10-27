"""Renderiza a ficha de "os passos" em paralelo e monta as pranchas (elenco, poses, objetos, Burj e palco).
python3 ficha_passos_montar.py PASTA [ITEM ...] [--jobs 8] [--scale 1.0] [--so-montar]
Saída: PASTA/<item>.png e ../personagem/passos/ficha-passos-{elenco,poses,objetos,burj-palco}.png"""
import os, sys, subprocess, re
from concurrent.futures import ThreadPoolExecutor
from PIL import Image, ImageDraw, ImageFont
AQUI = os.path.dirname(os.path.abspath(__file__))
BL = __import__("canal38_env").BLENDER
SAI = os.path.join(AQUI, "..", "personagem", "passos")
a = sys.argv[1:]
pasta = a[0]
opt = lambda n, d: a[a.index(n) + 1] if n in a else d
jobs, esc = int(opt("--jobs", "8")), opt("--scale", "1.0")
pedidos = [x for i, x in enumerate(a[1:], 1) if not x.startswith("--") and a[i - 1] not in ("--jobs", "--scale")]
os.makedirs(pasta, exist_ok=True)
lst = subprocess.run([BL, "-b", "-P", f"{AQUI}/ficha_passos.py", "--", "--list"], capture_output=True, text=True, cwd=AQUI).stdout
TIT = {l.split(" | ")[0]: l.split(" | ", 1)[1] for l in lst.splitlines() if re.match(r"^[a-z0-9_]+ \| ", l)}


def um(i):
    dst = f"{pasta}/{i}.png"
    r = subprocess.run([BL, "-b", "-P", f"{AQUI}/ficha_passos.py", "--", i, dst, "--scale", esc], capture_output=True, text=True, cwd=AQUI)
    if not os.path.exists(dst):
        print("FALHOU", i); print("\n".join((r.stdout + r.stderr).splitlines()[-12:]))
    ik = [l for l in (r.stdout + r.stderr).splitlines() if l.startswith("IK ")]
    for l in ik:
        print(i, l)
    return i


if "--so-montar" not in a:
    with ThreadPoolExecutor(jobs) as ex:
        list(ex.map(um, pedidos or list(TIT)))

F = lambda s: ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", s)
FB = lambda s: ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Black.ttf", s)


def prancha(nome, titulo, itens, cols, tw, th, sub=None):
    itens = [i for i in itens if os.path.exists(f"{pasta}/{i}.png")]
    lin = (len(itens) + cols - 1) // cols
    cab, leg, m = 110, 52, 14
    W = cols * (tw + m) + m; H = cab + lin * (th + leg + m) + m
    im = Image.new("RGB", (W, H), (26, 30, 30)); d = ImageDraw.Draw(im)
    d.text((m, 22), titulo, font=FB(40), fill=(242, 180, 65))
    if sub:
        d.text((m, 72), sub, font=F(22), fill=(200, 205, 195))
    for k, i in enumerate(itens):
        x, y = m + (k % cols) * (tw + m), cab + (k // cols) * (th + leg + m)
        t = Image.open(f"{pasta}/{i}.png").convert("RGB"); t = t.resize((tw, int(t.height * tw / t.width)))
        im.paste(t.crop((0, 0, tw, min(th, t.height))), (x, y))
        palavras, linhas, cur = TIT.get(i, i).split(), [], ""
        for p in palavras:
            if d.textlength((cur + " " + p).strip(), font=F(19)) <= tw - 4:
                cur = (cur + " " + p).strip()
            else:
                linhas.append(cur); cur = p
        linhas.append(cur)
        for j, l in enumerate(linhas[:2]):
            d.text((x + 2, y + th + 4 + 21 * j), l, font=F(19), fill=(225, 225, 215))
    out = os.path.join(SAI, f"ficha-passos-{nome}.png"); im.save(out); print(out, im.size)


prancha("elenco", "ELENCO", ["eu_frente", "eu_3q", "eu_lado", "eu_costas", "moca", "zelador", "limpador"], 7, 300, 533,
        "o 'eu' (blusa vermelha escura, cabeça preta, olho branco) com 1,8 m; a moça do ponto; o zelador e o limpador do prédio de 18 andares")
ordem = [l for l in TIT if l.startswith("pose_")]
prancha("poses", "POSES DO 'EU' (de lado e em 3/4)", ordem, 6, 300, 533,
        "joelho nunca travado reto, cotovelo dobrado, ombro e quadril em sentidos opostos no passo, peso no pé de apoio, mãos no chão por IK")
prancha("objetos", "OBJETOS", ["onibus", "ponto", "poste", "porta", "relogio", "poca", "predios", "predio18_topo", "macro_palito", "macro_lata",
                               "manometro", "raiox", "aviao", "nuvens", "espaco"], 5, 330, 587,
        "cada número do roteiro tem um objeto que o olho reconhece")
prancha("burj-palco", "BURJ KHALIFA E PALCO DE MEDIDA", ["burj_dubai", "burj_planta", "burj_agulha", "palco_dubai", "palco_dia", "palco_azul", "palco_preto"], 4, 400, 711,
        "Burj fiel: planta em Y, 27 recuos em espiral, aletas e agulha · palco: lente de 135 mm, régua afastada, número ao lado, fantasmas dos tamanhos anteriores")
