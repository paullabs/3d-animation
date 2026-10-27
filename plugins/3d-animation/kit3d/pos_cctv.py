"""Visual de câmera de segurança (pedido de 24/10/2026: "aquela câmera de segurança, com aquele feitinho de câmera de segurança").
Quadro a quadro em PIL: lente barril, imagem lavada e esverdeada, ruído, linhas de varredura, vinheta, carimbo de câmera/dia/hora e o REC piscando.
python3 pos_cctv.py ENTRADA.png SAIDA.png [--cam "CAM 02"] [--dia 200] [--hora 03:14:07] [--quadro 0]"""
import sys, random
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

FONT = "/System/Library/Fonts/Menlo.ttc"


def barril(im, k=0.12):
    a = np.asarray(im).astype(np.float32); h, w = a.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    nx, ny = (xx - w / 2) / (w / 2), (yy - h / 2) / (h / 2)
    r2 = nx * nx * (w / h) ** 2 * 0.3 + ny * ny * 0.3
    f = 1 + k * r2
    sx = np.clip(nx / f * (w / 2) + w / 2, 0, w - 1).astype(np.int32); sy = np.clip(ny / f * (h / 2) + h / 2, 0, h - 1).astype(np.int32)
    return Image.fromarray(a[sy, sx].astype(np.uint8))


def aplica(im, cam="CAM 02", dia=200, hora="03:14:07", quadro=0, seed=1):
    im = im.convert("RGB")
    w, h = im.size
    im = barril(im)
    a = np.asarray(im).astype(np.float32) / 255.0
    lum = a @ np.array([0.3, 0.59, 0.11], dtype=np.float32)
    lum = np.clip((lum - 0.06) * 1.25, 0, 1) ** 0.9
    cor = np.stack([lum * 0.86 + 0.04, lum * 0.97 + 0.05, lum * 0.82 + 0.03], -1)
    rnd = np.random.default_rng(seed + quadro)
    cor += rnd.normal(0, 0.035, (h, w, 1)).astype(np.float32)
    cor[::3] *= 0.9                                                         # linhas de varredura
    yy, xx = np.mgrid[0:h, 0:w]
    v = 1 - 0.42 * (((xx - w / 2) / (w / 2)) ** 2 + ((yy - h / 2) / (h / 2)) ** 2) ** 1.4
    cor *= np.clip(v, 0, 1)[..., None]
    im = Image.fromarray((np.clip(cor, 0, 1) * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.6))
    d = ImageDraw.Draw(im); s = w / 540
    f = ImageFont.truetype(FONT, int(22 * s))
    d.text((int(28 * s), int(300 * s)), f"{cam}", font=f, fill=(225, 235, 220))
    d.text((int(28 * s), int(330 * s)), f"DIA {dia}  {hora}", font=f, fill=(225, 235, 220))
    if (quadro // 12) % 2 == 0:
        d.ellipse((w - int(118 * s), int(302 * s), w - int(100 * s), int(320 * s)), fill=(220, 60, 50))
    d.text((w - int(92 * s), int(300 * s)), "REC", font=f, fill=(225, 235, 220))
    return im


if __name__ == "__main__":
    a = sys.argv[1:]
    arg = lambda n, d: a[a.index(n) + 1] if n in a else d
    aplica(Image.open(a[0]), arg("--cam", "CAM 02"), arg("--dia", "200"), arg("--hora", "03:14:07"), int(arg("--quadro", "0"))).save(a[1])
    print("ok", a[1])
