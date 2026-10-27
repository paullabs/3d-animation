"""Storyboard do PCC (versão 3): 15 cenas, cada uma com o quadro final diagramado na grade 9:16, a ordem em que os
elementos entram (números amarelos) e o movimento de câmera. Gera folhas PNG para aprovação antes de animar.
python3 storyboard_pcc.py OUT_DIR"""
import os, sys, math
from PIL import Image, ImageDraw, ImageFont

FONT = "/System/Library/Fonts/Avenir Next.ttc"
f = lambda size, idx=7: ImageFont.truetype(FONT, size, index=idx)
K = 0.3                                  # 1080x1920 -> 324x576
FW, FH = int(1080 * K), int(1920 * K)
CW, PAD = FW + 36, 18
AMARELO, BRANCO, CINZA, VERM, AZUL = (255, 210, 64), (240, 242, 248), (150, 156, 175), (214, 52, 60), (46, 100, 192)
TINTA = (12, 15, 28)


class Q:
    """um quadro desenhado em coordenadas de tela cheia (1080 x 1920)"""
    def __init__(self, top, bottom):
        self.im = Image.new("RGB", (FW, FH))
        d = ImageDraw.Draw(self.im)
        for y in range(FH):
            u = y / FH
            d.line([(0, y), (FW, y)], fill=tuple(int(top[i] + (bottom[i] - top[i]) * u) for i in range(3)))
        self.ov = Image.new("RGBA", (FW, FH), (0, 0, 0, 0))
        self.d = ImageDraw.Draw(self.ov)
        self.marks = []

    def p(self, x, y):
        return (x * K, y * K)

    def rect(self, x0, y0, x1, y1, fill, r=0, outline=None, w=0):
        if fill is not None and len(fill) == 4 and fill[3] == 0:
            fill = None                                           # só contorno (preencher com alfa 0 apagaria o que está atrás)
        self.d.rounded_rectangle([x0 * K, y0 * K, x1 * K, y1 * K], radius=r * K, fill=fill, outline=outline, width=w)

    def poly(self, pts, fill):
        self.d.polygon([self.p(*q) for q in pts], fill=fill)

    def circ(self, x, y, r, fill, outline=None, w=0):
        self.d.ellipse([(x - r) * K, (y - r) * K, (x + r) * K, (y + r) * K], fill=fill, outline=outline, width=w)

    def line(self, pts, fill, w=3, dash=None):
        pts = [self.p(*q) for q in pts]
        if not dash:
            self.d.line(pts, fill=fill, width=w); return
        for (a, b) in zip(pts, pts[1:]):
            L = math.dist(a, b); n = int(L / dash)
            for i in range(0, n, 2):
                u0, u1 = i / n, min(1, (i + 1) / n)
                self.d.line([(a[0] + (b[0] - a[0]) * u0, a[1] + (b[1] - a[1]) * u0), (a[0] + (b[0] - a[0]) * u1, a[1] + (b[1] - a[1]) * u1)], fill=fill, width=w)

    def txt(self, x, y, s, size, fill=BRANCO, idx=8, anchor="mm"):
        self.d.text((x * K, y * K), s, font=f(int(size * K), idx), fill=fill, anchor=anchor)

    def luz(self, x, y_top, y_bot, w_top, w_bot, cor=(255, 236, 200), a=40):
        self.poly([(x - w_top, y_top), (x + w_top, y_top), (x + w_bot, y_bot), (x - w_bot, y_bot)], (*cor, a))
        self.d.ellipse([(x - w_bot * 1.1) * K, (y_bot - 40) * K, (x + w_bot * 1.1) * K, (y_bot + 40) * K], fill=(*cor, a + 15))

    def heroi(self, x, base, h=700, jaqueta=VERM, olhar=1):
        s = h / 700.0
        self.rect(x - 34 * s, base - 300 * s, x - 6 * s, base, (43, 100, 192))
        self.rect(x + 6 * s, base - 300 * s, x + 34 * s, base, (36, 84, 165))
        self.rect(x - 70 * s, base - 520 * s, x + 70 * s, base - 280 * s, jaqueta, r=30 * s)
        self.rect(x - 8 * s, base - 560 * s, x + 8 * s, base - 515 * s, TINTA)
        self.circ(x, base - 620 * s, 72 * s, TINTA, (120, 180, 255), max(1, int(5 * s * K * 3)))
        for dx in (-26, 18):
            self.circ(x + (dx + 8 * olhar) * s, base - 628 * s, 14 * s, (240, 236, 226))

    def gente(self, x, base, h=420, cor=(34, 42, 70)):
        s = h / 420.0
        self.rect(x - 52 * s, base - 300 * s, x + 52 * s, base, cor, r=24 * s)
        self.circ(x, base - 350 * s, 46 * s, (20, 25, 44))

    def num(self, x, y, n):
        self.marks.append((x, y, n))

    def cam(self, a, b, label="câmera"):
        self.line([a, b], (255, 255, 255, 210), 2, dash=7)
        ang = math.atan2(b[1] - a[1], b[0] - a[0])
        tip = self.p(*b)
        for s_ in (-1, 1):
            self.d.line([tip, (tip[0] - 9 * math.cos(ang + s_ * 0.5), tip[1] - 9 * math.sin(ang + s_ * 0.5))], fill=(255, 255, 255, 230), width=2)
        self.d.text(((a[0] + b[0]) / 2 * K + 6, (a[1] + b[1]) / 2 * K - 6), label, font=f(11, 6), fill=(255, 255, 255, 200), anchor="ls")

    def final(self):
        g = ImageDraw.Draw(self.ov)
        for y0, y1 in ((200, 380),):                                   # zona do título
            g.rectangle([0, y0 * K, FW, y1 * K], outline=(255, 210, 64, 70))
        for x in (360, 540, 720):
            self.line([(x, 0), (x, 1920)], (255, 255, 255, 28 if x != 540 else 45), 1, dash=6)
        self.line([(0, 1250), (1080, 1250)], (255, 255, 255, 60), 1, dash=6)  # linha da legenda
        g.text((4, 1250 * K - 3), "legenda", font=f(9, 6), fill=(255, 255, 255, 110), anchor="ls")
        g.text((4, 200 * K + 11), "título", font=f(9, 6), fill=(255, 210, 64, 140), anchor="ls")
        for x, y, n in self.marks:
            cx, cy = x * K, y * K
            g.ellipse([cx - 10, cy - 10, cx + 10, cy + 10], fill=AMARELO, outline=TINTA, width=2)
            g.text((cx, cy + 1), str(n), font=f(13, 8), fill=TINTA, anchor="mm")
        im = self.im.convert("RGBA"); im.alpha_composite(self.ov)
        return im.convert("RGB")


# ====================================================================== as cenas
NOITE = ((8, 11, 22), (14, 20, 38))
CELA = ((10, 13, 24), (20, 26, 44))
COFRE = ((18, 12, 9), (44, 30, 21))
PAPEL = ((205, 199, 189), (232, 226, 216))


def escada_desenho(q, x0=150, base=1460, passo_w=150, passo_h=160, cor=(30, 38, 62), luz5=True, nums=True):
    for k in range(5):
        x = x0 + k * passo_w; top = base - (k + 1) * passo_h
        q.rect(x, top, x0 + 5 * passo_w + 60, base, cor)
        q.rect(x, top, x + passo_w, top + 6, (70, 84, 120) if k < 4 else AMARELO)
        if nums:
            q.txt(x + passo_w / 2, top + 70, str(k + 1), 64, BRANCO if k < 4 else AMARELO)
    return x0 + 4 * passo_w + passo_w / 2, base - 5 * passo_h


def c1(q):
    q.rect(380, 820, 700, 1010, (22, 30, 56))
    q.rect(500, 760, 580, 820, (22, 30, 56))
    q.rect(515, 870, 565, 930, (255, 214, 150))
    q.luz(540, 900, 1500, 30, 260, (255, 200, 130), 28)
    for r in range(9):
        y = 1040 + r * 100; n = 7 + r * 3
        for i in range(n):
            q.gente(1080 * (i + 0.5) / n, y + 60, 50 + r * 30, (40 + r * 2, 52 + r * 2, 92 + r * 3))
    for k in range(-3, 4):
        q.line([(540, 900), (540 + k * 150, 1200)], (255, 205, 140, 160), 2)
    q.txt(540, 270, "40.000", 120, BRANCO); q.txt(540, 350, "PESSOAS", 46, AMARELO)
    q.num(160, 1120, 1); q.num(900, 270, 2); q.num(760, 1150, 3); q.num(620, 900, 4)
    q.cam((540, 1600), (540, 1000), "avança até a janela")


def c2(q):
    q.rect(0, 0, 1080, 1460, (20, 26, 46))
    q.rect(0, 1460, 1080, 1920, (12, 15, 28))
    q.rect(410, 470, 670, 690, (60, 90, 140)); [q.rect(440 + i * 60, 470, 452 + i * 60, 690, TINTA) for i in range(4)]
    q.luz(540, 0, 1460, 70, 330)
    q.heroi(540, 1460, 760)
    for x in (40, 110, 970, 1040):
        q.rect(x - 14, 0, x + 14, 1920, (6, 8, 14))
    q.rect(410, 470, 670, 690, (220, 50, 60, 60))
    q.line([(640, 860), (760, 760), (980, 760)], (255, 255, 255, 220), 2)
    q.txt(870, 735, "CHEFE DO PCC", 40, BRANCO)
    q.num(700, 520, 1); q.num(880, 690, 2); q.num(470, 840, 3)
    q.cam((540, 1720), (540, 1480), "aproxima devagar")


def c3(q):
    tx, ty = escada_desenho(q)
    q.luz(tx + 40, 300, ty, 40, 160, (255, 220, 150), 40)
    q.rect(tx - 80, ty - 260, tx + 160, ty - 120, (14, 18, 32), r=20, outline=AMARELO, w=2)
    q.txt(tx + 40, ty - 190, "R$ ?", 60, AMARELO)
    q.heroi(105, 1460, 300, olhar=1)
    q.num(230, 1210, 1); q.num(tx + 200, ty - 30, 2); q.num(tx - 110, ty - 190, 3); q.num(150, 1080, 4)
    q.cam((300, 1700), (620, 1460), "sobe na diagonal")


def giz(q, cor=(140, 155, 185), cx=700):
    q.d.ellipse([(cx - 300) * K, 1380 * K, (cx + 300) * K, 1540 * K], outline=cor, width=3)


def c4(q):
    q.luz(700, 0, 1460, 80, 320, (200, 215, 255), 22)
    giz(q, (200, 60, 70))
    for i, x in enumerate((560, 650, 740, 830)):
        q.gente(x, 1450 + (i % 2) * 20, 640)
    q.heroi(250, 1480, 680, jaqueta=(140, 146, 160))
    q.rect(300, 950, 400, 1030, (190, 150, 95), r=6)
    q.num(700, 820, 1); q.num(150, 760, 2); q.num(430, 950, 3); q.num(420, 1500, 4)
    q.cam((200, 1720), (480, 1720), "desliza para a direita")


def c5(q):
    q.luz(620, 0, 1460, 80, 340, (200, 215, 255), 22)
    giz(q, AMARELO, 760)
    for i, x in enumerate((700, 790, 880, 960)):
        q.gente(x, 1450 + (i % 2) * 20, 640)
    q.heroi(500, 1480, 700)
    q.gente(270, 1480, 760, (24, 26, 36)); q.rect(200, 690, 340, 715, TINTA)
    q.line([(330, 930), (420, 940)], (40, 42, 60), 6)
    q.rect(330, 500, 560, 560, VERM, r=12); q.txt(445, 531, "ERRO", 36, BRANCO)
    q.line([(270, 700), (270, 640), (420, 640)], (255, 255, 255, 200), 2)
    q.txt(430, 640, "PADRINHO", 30, BRANCO, anchor="lm")
    q.num(160, 900, 1); q.num(590, 1100, 2); q.num(230, 600, 3); q.num(600, 470, 4)
    q.cam((540, 1720), (540, 1520), "aproxima")


def c6(q):
    q.rect(160, 520, 920, 1180, (245, 240, 230), r=24)
    q.rect(160, 520, 920, 610, VERM, r=24); q.rect(160, 580, 920, 610, VERM)
    q.txt(540, 566, "MENSALIDADE", 40, BRANCO)
    for i in range(12):
        cx = 255 + (i % 4) * 190; cy = 690 + (i // 4) * 170
        q.rect(cx - 80, cy - 65, cx + 80, cy + 65, (225, 220, 208), r=12)
        q.circ(cx, cy, 44, (242, 184, 58), (190, 130, 30), 2)
    q.num(190, 500, 1); q.num(255, 690, 2)
    q.cam((540, 1500), (540, 1420), "quase parada")


def c7(q):
    q.rect(330, 450, 1000, 1180, (232, 222, 196), r=16)
    for i in range(4):
        for j in range(5):
            q.rect(370 + i * 155, 490 + j * 135, 495 + i * 155, 600 + j * 135, (205, 190, 160), r=8)
    q.rect(525, 625, 805, 870, (0, 0, 0, 0), r=10, outline=VERM, w=4)
    q.poly([(660, 700), (660, 620), (720, 640), (660, 660)], VERM)
    q.heroi(220, 1600, 980)
    q.num(960, 430, 1); q.num(110, 900, 2); q.num(820, 620, 3)
    q.cam((540, 1720), (600, 1720), "desliza pouco")


def c8(q):
    xs = (220, 540, 860)
    for x, cor, lab in zip(xs, ((245, 240, 230), (60, 66, 90), (30, 30, 36)), ("REGRA", "TRIBUNAL", "PENA")):
        q.rect(x - 130, 680, x + 130, 940, cor, r=24)
        q.txt(x, 990, lab, 38, BRANCO)
    q.line([(150, 760), (290, 870)], VERM, 6); q.line([(290, 760), (150, 870)], VERM, 6)
    q.rect(480, 740, 600, 790, (180, 140, 90), r=10)
    q.circ(860, 790, 70, (230, 228, 220)); q.circ(835, 785, 16, TINTA); q.circ(885, 785, 16, TINTA)
    for a, b in ((360, 400), (680, 720)):
        q.line([(a, 810), (b + 10, 810)], BRANCO, 4)
        q.poly([(b + 30, 810), (b + 8, 796), (b + 8, 824)], BRANCO)
    q.num(220, 640, 1); q.num(540, 640, 2); q.num(860, 640, 3); q.num(990, 1060, 4)
    q.cam((200, 1500), (880, 1500), "acompanha o fluxo")


def c9(q):
    q.rect(380, 450, 700, 610, VERM, r=20); q.txt(540, 530, "VOCÊ", 44, BRANCO)
    q.line([(540, 610), (540, 680)], (190, 170, 150), 4); q.line([(300, 680), (780, 680)], (190, 170, 150), 4)
    labs = ("DROGA", "DINHEIRO", "ADVOGADOS", "REDES SOCIAIS")
    for i, lab in enumerate(labs):
        x = 300 + (i % 2) * 480; y = 800 + (i // 2) * 250
        q.line([(x, 680), (x, y - 90)], (190, 170, 150), 3) if i < 2 else None
        q.rect(x - 200, y - 90, x + 200, y + 90, (52, 40, 31), r=18, outline=(110, 86, 66), w=2)
        q.circ(x - 130, y, 42, (200, 160, 90) if i != 3 else (61, 123, 255))
        q.txt(x + 40, y, lab, 32 if i < 3 else 26, BRANCO)
    q.num(720, 450, 1); q.num(800, 650, 2); q.num(100, 800, 3); q.num(990, 1050, 4)
    q.cam((540, 1600), (540, 1420), "aproxima do quadro")


def c10(q):
    tx, ty = escada_desenho(q, x0=-420, base=1850, passo_w=240, passo_h=180)
    q.luz(tx + 120, 0, ty, 60, 260, (255, 220, 150), 55)
    q.heroi(tx + 120, ty, 640)
    q.num(tx - 60, ty - 300, 1); q.num(tx + 330, ty - 560, 2)
    q.cam((700, 1750), (760, 1550), "sobe até o topo")


def c11(q):
    q.txt(540, 440, "PCC", 60, BRANCO)
    q.rect(450, 395, 630, 485, (0, 0, 0, 0), r=40, outline=VERM, w=4)
    for i in range(10):
        for j in range(9):
            x = 160 + i * 84; y = 620 + j * 70
            q.rect(x - 20, y - 26, x + 20, y + 26, VERM, r=6); q.rect(x - 12, y - 18, x + 12, y - 2, (210, 230, 255))
    for x in (300, 540, 780):
        q.line([(x, 590), (540, 490)], (214, 52, 60, 140), 2)
    q.num(540, 1190, 1); q.num(90, 620, 2); q.num(990, 900, 3); q.num(700, 440, 4)
    q.cam((540, 1600), (540, 1680), "afasta devagar")


def c12(q):
    q.luz(540, 0, 1420, 80, 420, (255, 214, 160), 30)
    for r in range(8):
        for i in range(6 if r % 2 else 7):
            x = 540 + (i - (2.5 if r % 2 else 3)) * 104; y = 1400 - r * 58
            q.rect(x - 48, y - 26, x + 48, y + 26, (79, 143, 198), r=3, outline=(15, 42, 74), w=2)
            q.rect(x - 6, y - 28, x + 10, y + 28, (239, 230, 207))
    q.txt(540, 270, "R$ 52", 120, BRANCO); q.txt(540, 350, "BILHÕES DE REAIS", 40, BRANCO)
    for i in range(5):
        x = 260 + i * 140
        q.circ(x, 1600, 16, AMARELO); q.txt(x, 1650, str(2020 + i), 26, BRANCO)
    q.line([(260, 1600), (820, 1600)], (120, 110, 100), 3)
    q.num(160, 1250, 1); q.num(940, 290, 2); q.num(940, 1600, 3)
    q.cam((540, 1780), (540, 1880), "afasta")


def c13(q):
    q.rect(0, 0, 1080, 1920, (0, 0, 0, 0))
    for i in range(5):
        y = 1500 - i * 250
        q.poly([(110, y), (230, y - 200), (350, y)], (120, 134, 168))
        q.poly([(200, y - 150), (230, y - 200), (260, y - 150)], BRANCO)
        q.txt(390, y - 120, str(i + 1), 46, BRANCO, anchor="lm")
    for k in range(40):
        y = 1500 - k * 32
        q.rect(600, y - 28, 900, y, (79, 143, 198), outline=(15, 42, 74), w=2)
    q.line([(80, 250), (1000, 250)], AMARELO, 3, dash=10)
    q.txt(750, 200, "52 km", 60, AMARELO)
    q.num(960, 1460, 1); q.num(960, 900, 2); q.num(60, 1100, 3); q.num(960, 250, 4)
    q.cam((1000, 1700), (1000, 700), "sobe junto com a pilha")


def c14(q):
    q.rect(0, 1320, 1080, 1920, (24, 30, 50))
    for i in range(6):                                   # a câmera mostra ~6 dos 15 por vez enquanto desliza
        x = 140 + i * 160
        q.gente(x, 1320, 420, (70, 78, 112))
        if i < 5:
            q.rect(x - 62, 840, x + 62, 1320, (0, 0, 0, 0), outline=(150, 160, 190), w=3)
            for b in range(3):
                q.line([(x - 31 + b * 31, 840), (x - 31 + b * 31, 1320)], (150, 160, 190), 3)
    q.luz(940, 0, 1320, 40, 130, (255, 236, 170), 60)
    q.num(80, 780, 1); q.num(300, 800, 2); q.num(1010, 860, 3)
    q.cam((200, 1700), (800, 1700), "desliza pela fila")


def c15(q):
    escada_desenho(q, x0=300, base=1460, passo_w=130, passo_h=140, luz5=True)
    q.heroi(220, 1460, 560, olhar=1)
    q.txt(540, 300, "AINDA QUER SUBIR?", 62, BRANCO)
    q.num(120, 800, 1); q.num(980, 300, 2)
    q.cam((540, 1600), (540, 1800), "afasta e escurece")


CENAS = [
    (c1, NOITE, "1 · A prisão", "0,0–3,6 s", "Imagina comandar quarenta mil pessoas de dentro de uma cela.",
     "Um só movimento: avança por cima da multidão até a janela acesa.",
     ["multidão e prisão já na tela (nada de quadro vazio)", "1,4 s  \"40.000 PESSOAS\" no título", "2,0 s  fios de luz saem da janela, simétricos",
      "3,2 s  a janela enche a tela e vira a cela"]),
    (c2, CELA, "2 · O chefe", "3,6–7,3 s", "A polícia diz que o chefe do PCC faz isso.",
     "Cela simétrica; aproxima devagar de corpo inteiro até a cintura.",
     ["4,3 s  luz vermelha e azul passa pela janela, uma vez", "5,3 s  linha e etiqueta \"CHEFE DO PCC\" no terço direito",
      "6,4 s  ele levanta o olhar para a câmera, meio sorriso"]),
    (c3, NOITE, "3 · Os 5 níveis", "7,3–11,2 s", "No último dos cinco níveis, tem um número que parece mentira.",
     "Escada de 5 degraus iguais na diagonal; a câmera sobe por ela.",
     ["7,5 s  degraus sobem em ordem 1 a 5", "8,0 s  só o degrau 5 recebe luz", "9,3 s  cartão \"R$ ?\" sobre o topo",
      "10,2 s  o herói lá embaixo olha para cima"]),
    (c4, NOITE, "4 · Nível 1: o ajudante", "11,2–16,6 s", "Você é ajudante: faz serviço pra facção, mas não é um deles.",
     "Rua escura, círculo de giz à direita; a câmera desliza devagar.",
     ["o grupo já está no círculo", "12,1 s  o herói (cinza) entra pela esquerda com a caixa", "13,6 s  entrega a caixa na borda do círculo",
      "15,2 s  tenta entrar: a linha fica vermelha e ele para"]),
    (c5, NOITE, "5 · Nível 2: o membro", "16,6–22,0 s", "Você vira membro: um padrinho te indica e responde pelos seus erros.",
     "O mesmo lugar (continuidade); aproxima.",
     ["17,6 s  o padrinho entra e põe a mão no ombro", "18,1 s  ele cruza a linha: giz dourado, jaqueta fica vermelha",
      "19,1 s  etiqueta \"PADRINHO\"", "20,8 s  a caixa cai e \"ERRO\" vai em linha reta até o padrinho"]),
    (c6, PAPEL, "6 · A mensalidade", "22,0–23,9 s", "E você paga mensalidade.",
     "Objeto em fundo claro liso, centralizado.",
     ["22,0 s  o calendário (12 meses em grade 4 × 3)", "22,3 s  uma moeda em cada mês, na ordem de leitura"]),
    (c7, PAPEL, "7 · Nível 3: o fiscal", "23,9–27,0 s", "Você vira fiscal de uma área.",
     "Mapa reto, centralizado; o herói grande no terço esquerdo.",
     ["23,9 s  o mapa do bairro visto de cima", "25,4 s  o herói entra, braços cruzados", "26,5 s  a área é contornada em vermelho e recebe a bandeira"]),
    (c8, ((26, 28, 38), (44, 46, 60)), "8 · O tribunal do crime", "27,0–31,8 s", "Quem quebra as regras vai pro tribunal do crime, e a pena pode ser a morte.",
     "Fluxo de 3 passos na mesma linha; a câmera acompanha da esquerda para a direita.",
     ["27,2 s  regra com X", "28,7 s  seta + tribunal (uma batida do martelo)", "30,1 s  seta + pena", "31,0 s  caveira e a tela escurece"]),
    (c9, COFRE, "9 · Nível 4: chefe de setor", "31,8–41,0 s", "Você chefia um setor, como numa empresa. Droga, dinheiro, advogados e redes sociais.",
     "Organograma reto; aproxima devagar.",
     ["32,9 s  o seu cartão no topo", "33,9 s  a linha desce e abre 4 vagas", "36,4 a 39,5 s  os 4 setores ocupam as vagas na ordem da fala",
      "cada setor com ícone próprio"]),
    (c10, ((40, 30, 20), (90, 64, 36)), "10 · Nível 5: o topo", "41,0–43,6 s", "No nível cinco, você está no topo.",
     "Volta à escada da cena 3 (continuidade); sobe até o degrau 5.",
     ["41,4 s  ele sobe no degrau 5, na luz", "43,0 s  a luz cresce, olhos de cifrão"]),
    (c11, ((14, 16, 26), (30, 34, 50)), "11 · Os postos", "43,6–47,5 s", "Uma investigação apontou que postos de gasolina ligados à facção...",
     "Fundo liso; tudo numa grade perfeita.",
     ["43,7 s  pasta da investigação no centro", "45,1 s  vira uma bomba de combustível", "45,8 s  1, 10, 100, 1.000 bombas, preenchendo a grade",
      "47,0 s  a grade se liga ao selo \"PCC\""]),
    (c12, COFRE, "12 · O dinheiro", "47,5–51,5 s", "...movimentaram cinquenta e dois bilhões de reais em cinco anos.",
     "As bombas viram maços nos mesmos lugares; uma luz só; afasta devagar.",
     ["47,5 s  cada bomba vira um maço de R$ 100", "48,2 s  os maços se empilham num bloco reto; \"R$ 52 BILHÕES\" no título",
      "50,4 s  linha do tempo 2020–2024 acende ano a ano"]),
    (c13, ((10, 20, 50), (110, 160, 220)), "13 · Cinco Everests", "51,5–55,9 s", "Em notas de cem, seria uma pilha de mais de cinco Everests.",
     "Uma nota no centro; a pilha cresce e a câmera sobe junto, sem corte.",
     ["51,6 s  uma nota de R$ 100 grande", "52,6 s  as notas se empilham e a câmera começa a subir", "53,3 s  Everests 1 a 5 passam ao lado",
      "54,5 s  topo: linha e \"52 km\""]),
    (c14, ((8, 10, 20), (16, 20, 36)), "14 · O preço", "55,9–61,6 s", "Mas o topo tem um preço: dos chefes de lá, só um está solto.",
     "Fila reta de 15 chefes, espaços iguais; a câmera desliza pela fila.",
     ["57,8 s  os 15 chefes", "58,9 s  grades descem uma a uma em 14 deles", "59,6 s  o último fica solto, com luz"]),
    (c15, NOITE, "15 · Ainda quer subir?", "61,6–63,6 s", "Ainda quer subir?",
     "O herói no pé da escada (mesmo lugar da cena 3); afasta e escurece.",
     ["ele olha para o topo", "a pergunta no título; escurece no fim"]),
]


def cartao(i, cena):
    fn, bg, titulo, tempo, fala, camera, ordem = cena
    q = Q(*bg); fn(q); quadro = q.final()
    linhas_t = []
    d0 = ImageDraw.Draw(Image.new("RGB", (1, 1)))

    def quebra(s, fonte, larg):
        out, cur = [], ""
        for w in s.split():
            t = (cur + " " + w).strip()
            if d0.textlength(t, font=fonte) > larg and cur:
                out.append(cur); cur = w
            else:
                cur = t
        return out + [cur]
    fF, fC, fO = f(14, 4), f(13, 5), f(13, 7)
    L = quebra("“" + fala + "”", fF, FW)
    C = quebra("Câmera: " + camera, fC, FW)
    O = [quebra(o, fO, FW - 26) for o in ordem]
    h = 52 + FH + 14 + 19 * len(L) + 8 + 18 * len(C) + 10 + sum(18 * len(o) + 4 for o in O) + 16
    return (titulo, tempo, quadro, L, C, O, fF, fC, fO), h


def folha(cards, out):
    ws = [cartao(i, c) for i, c in enumerate(cards)]
    H = max(h for _, h in ws)
    im = Image.new("RGB", (len(ws) * CW + PAD, H + PAD), (24, 25, 30))
    d = ImageDraw.Draw(im)
    for k, ((titulo, tempo, quadro, L, C, O, fF, fC, fO), _) in enumerate(ws):
        x = PAD + k * CW; y = PAD
        d.text((x, y + 16), titulo, font=f(19, 8), fill=BRANCO, anchor="ls")
        d.text((x, y + 38), tempo, font=f(14, 5), fill=AMARELO, anchor="ls")
        im.paste(quadro, (x, y + 52)); d.rectangle([x - 1, y + 51, x + FW, y + 52 + FH], outline=(70, 72, 84))
        yy = y + 52 + FH + 14
        for ln in L:
            d.text((x, yy), ln, font=fF, fill=(205, 208, 220)); yy += 19
        yy += 8
        for ln in C:
            d.text((x, yy), ln, font=fC, fill=(150, 200, 255)); yy += 18
        yy += 10
        for n, o in enumerate(O, 1):
            d.ellipse([x, yy + 1, x + 17, yy + 18], fill=AMARELO)
            d.text((x + 8.5, yy + 10), str(n), font=f(11, 8), fill=TINTA, anchor="mm")
            for ln in o:
                d.text((x + 26, yy), ln, font=fO, fill=(230, 232, 240)); yy += 18
            yy += 4
    im.save(out)


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "."
    os.makedirs(out, exist_ok=True)
    for i in range(0, len(CENAS), 5):
        folha(CENAS[i:i + 5], os.path.join(out, f"storyboard-{i // 5 + 1}.png"))
    print("ok", out)
