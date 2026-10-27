"""Área segura do Reels (1080 x 1920). Medidas mais citadas para Meta em 2025–2026: livre 270 px em cima,
670 px embaixo (legenda, nome, áudio), 65 px à esquerda e 120 px à direita (botões). Tudo que importa fica
dentro de SEGURA; o assunto principal fica no centro dela (x 512, y 760), não no centro da tela.
Fontes: hopperhq.com/blog/instagram-reel-size, revid.ai/instagram-reels-safe-zone."""
W, H = 1080, 1920
SEGURA = (65, 270, 960, 1250)                  # x0, y0, x1, y1
CX, CY = (SEGURA[0] + SEGURA[2]) / 2, (SEGURA[1] + SEGURA[3]) / 2
Y_LEGENDA = 1150                               # legenda dentro da área, acima da faixa de baixo
Y_ROTULO = 330                                 # rótulo do nível, logo abaixo da faixa de cima


def shift_padrao():
    """shift da lente que põe o ponto mirado pela câmera no centro da área segura (sensor_fit horizontal:
    o shift é medido na maior dimensão do quadro, a altura)"""
    return ((W / 2 - CX) / W, -(H / 2 - CY) / W)          # com sensor_fit horizontal o shift é medido na LARGURA; + em y desce o assunto


def guia(im):
    """desenha a área segura por cima de uma imagem PIL (para conferir os quadros de teste)"""
    from PIL import ImageDraw
    k = im.width / W
    d = ImageDraw.Draw(im, "RGBA")
    x0, y0, x1, y1 = [v * k for v in SEGURA]
    d.rectangle([0, 0, im.width, y0], fill=(255, 0, 0, 40)); d.rectangle([0, y1, im.width, im.height], fill=(255, 0, 0, 40))
    d.rectangle([x1, y0, im.width, y1], fill=(255, 0, 0, 40)); d.rectangle([0, y0, x0, y1], fill=(255, 0, 0, 40))
    d.rectangle([x0, y0, x1, y1], outline=(255, 255, 0, 200), width=2)
    d.line([(CX * k, y0), (CX * k, y1)], fill=(255, 255, 0, 90)); d.line([(x0, CY * k), (x1, CY * k)], fill=(255, 255, 0, 90))
    return im
