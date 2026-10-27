"""O MUNDO FIXO de "os passos" (crítica de 25/10/2026: "o prédio some; a cada hora o cenário muda; está sempre mostrando as mesmas cenas; tem que ser o mesmo
ambiente para a pessoa identificar e comparar o antes e o depois; cores mais vivas").
Antes cada plano montava a rua de novo (escalada por 2^-n), com limpezas e vizinhança diferentes em cada n. Agora a rua é UMA SÓ, em metros reais, igual em
todos os planos: o que muda é onde o boneco pisa (o passo n), a escala dele e a câmera.
Layout (metros; o boneco pisa em (0, y_n) com y_n = S2.eu_y(n); a rua corre ao longo de y e ele anda para -y):
  +x: o ônibus (3,2 m) e o ponto; o poste de 7 m; os três prédios de comparação, cada um colado no ponto de pouso do seu passo
      (5 andares = 15 m no 3º passo, 10 andares = 30 m no 4º, 18 andares = 55 m no 5º); os prédios baixos e coloridos da avenida; o horizonte de torres.
  -x: o parque (grama e árvores, só de longe, para a câmera lateral nunca bater em nada).
  Réguas que ficam: ao pisar, cada passo deixa a sua régua de pé na rua (3,6 / 7,2 / 14,4 / 28,8 / 57,6 m) com a pílula do número: quem olha de longe
  vê a escada de alturas e compara o antes e o depois.
Uso: E = avenida(n, reguas_ate=n - 1): monta tudo e põe o boneco (de 1,8 u) na origem da cena, como o resto do kit já espera (escala k = 2^-n)."""
import os, sys, math, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy
import lib, cena
import objetos3d_abrigo as O3, cidade3d as C3
import objetos3d_passos as OP, objetos3d_passos_b as OB
import story_passos as SP
import story_passos2 as S2
from heroi3d import plano
import elenco3d_abrigo as E3

# o boneco e o amigo mais vivos (o vermelho e o verde)
E3.ESPEC['eu'].update(roupa='#d03a32', escura='#a2261f', gola='#a2261f')
E3.ESPEC['viz2'].update(roupa='#27b36a', escura='#1b8a50', gola='#1b8a50', calca='#2d3a4a')

# cores vivas (o boneco é vermelho e o amigo verde: os prédios ficam no amarelo, no verde-água e no azul, que contrastam com os dois)
CEU = dict(chao="#74d474", horizonte="#dff3ff", meio="#6fbaff", topo="#1d6fe8")
GRAMA, ASFALTO, FAIXA, CALCADA, PRACA = "#63c964", "#454b58", "#ffffff", "#f6e8c4", "#f0e1b6"
PRED = dict(p5="#ffc23c", p10="#18b0b0", p18="#3b72f2")
VIVAS = ["#5cc8f0", "#ffd24d", "#a98bfa", "#5fe3b1", "#ff9db4", "#9be564", "#ffa84d", "#6fa8ff"]

Y = {k: S2.eu_y(k) for k in range(0, 6)}                    # onde ele pisa em cada passo (m): 0, -2,52, -7,56, -17,64, -37,8, -78,12
X_AM, Y_AM = -0.7, Y[1] + 1.3                               # o amigo, no chão onde parou
ALT = lambda k: 1.8 * 2 ** k
REGUA_XY = lambda k: (0.3 * 2 ** k, Y[k] - 0.6 * 2 ** k)    # a régua de cada passo (a mesma posição, em u, que a fita lateral usa)


def _poli(nome, pts, cor):
    return cena.poly_mesh(nome, pts, plano(cor))


def construir(reguas_ate=0):
    """a rua toda, em metros reais. reguas_ate = até que passo as réguas deixadas no chão já existem"""
    rnd = random.Random(7)
    SP.ceu_dia(CEU)
    y0, y1 = 130.0, -420.0
    _poli("chao_largo", [(-4000, -4000, -0.05), (4000, -4000, -0.05), (4000, 4000, -0.05), (-4000, 4000, -0.05)], GRAMA)
    _poli("asfalto", [(-3.4, y0, 0), (3.4, y0, 0), (3.4, y1, 0), (-3.4, y1, 0)], ASFALTO)
    y = y0
    while y > y1:
        _poli(f"faixa_{int(y * 10)}", [(-0.07, y, 0.004), (0.07, y, 0.004), (0.07, y - 1.6, 0.004), (-0.07, y - 1.6, 0.004)], FAIXA)
        y -= 3.4
    for s in (-1, 1):
        OB.caixa(f"calcada{s}", (1.8, y0 - y1, 0.15), OP.M(CALCADA, "#d9c79b"), (s * 4.3, (y0 + y1) / 2, 0.075), cont=0.0)
        OB.caixa(f"meiofio{s}", (0.16, y0 - y1, 0.2), OP.M("#ffffff", "#cfc6ad"), (s * 3.48, (y0 + y1) / 2, 0.1), cont=0.004)
    _poli("praca", [(5.2, y0, 0.01), (60, y0, 0.01), (60, y1, 0.01), (5.2, y1, 0.01)], PRACA)

    # o ônibus e o ponto (3,2 m): o primeiro termômetro, ao lado do 1º passo
    OB.onibus("onibus", (2.7, 0.0, 0.0), rot=0, cor="#ffffff", faixa="#ff3b57")
    OB.ponto_onibus("ponto", (4.9, 7.5, 0.15), rot=-90)
    # o poste de 7 m (a fileira de postes só vai até o 4º passo: depois o corpo dele ocuparia o lugar deles)
    for k, yy in enumerate((38.6, 16.6, -5.4, -27.4)):
        C3.poste_luz(f"poste_{k}", (5.0, yy, 0.15), lado=1)
    # os prédios de comparação, colados no ponto de pouso do 3º, do 4º e do 5º passo (o centro do prédio na mesma altura y do pouso)
    OB.predio_alto("p5", 11.5, Y[3], 5, w=11, cor=PRED["p5"])
    OB.predio_alto("p10", 15.0, Y[4], 10, w=15, cor=PRED["p10"])
    OB.predio_alto("p18", 20.0, Y[5], 18, w=20, cor=PRED["p18"], balancim=True, face_balancim="esq")
    # a avenida: prédios baixos e coloridos dos dois lados do começo, de frente para a rua
    for i, yy in enumerate(range(70, -2, -12)):
        OP.torre(f"av_{i}", 12.0 + rnd.uniform(-0.5, 1.5), yy, rnd.uniform(7, 10), rnd.uniform(9, 12), rnd.choice((9.0, 12.0, 15.0)), cor=VIVAS[(i * 3) % len(VIVAS)], cont=0.04)
    # o fundo: quarteirões coloridos atrás da praça e o horizonte de torres no fim da avenida (para onde ele olha no 1º plano)
    for i in range(0, 22):
        yy = 60 - i * 26.0 + rnd.uniform(-4, 4)
        xx = 38.0 + rnd.choice((0, 0, 22, 44)) + rnd.uniform(-3, 3)
        OP.torre(f"fd_{i}", xx, yy, rnd.uniform(14, 26), rnd.uniform(14, 24), rnd.choice((24.0, 36.0, 48.0, 66.0, 90.0)), cor=VIVAS[(i * 5 + 2) % len(VIVAS)], cont=0.06)
    for i in range(0, 14):
        xx = -70.0 + i * 11.0 + rnd.uniform(-2, 2)
        OP.torre(f"hz_{i}", xx, 190.0 + rnd.uniform(0, 40), rnd.uniform(14, 26), 16.0, rnd.choice((30.0, 48.0, 70.0, 110.0)), cor=VIVAS[(i * 3 + 1) % len(VIVAS)], cont=0.08)
    # o parque do lado -x: árvores só de longe (a câmera lateral fica entre elas e ele)
    for i in range(0, 46):
        C3.arvore(f"arv_{i}", (-20.0 - rnd.uniform(0, 60), 90.0 - i * 8.5 + rnd.uniform(-3, 3), 0.0), rnd.uniform(1.2, 2.2), cor=rnd.choice(("#3fb950", "#52c75f", "#2ea84a")))
    # as réguas que ficam: uma para cada passo já dado
    import provas_passos5 as PV
    for k in range(1, reguas_ate + 1):
        x, y_ = REGUA_XY(k)
        PV.regua_lateral(x, y_, ALT(k), ALT(k), 0.11 * 2 ** k, nome=f"rf{k}")


def avenida(n, reguas=True, extras=None):
    """a rua do passo n com o boneco de 1,8 u na origem (a rua é escalada por 2^-n e deslocada para o ponto de pouso do passo n)"""
    E = SP.no_mundo(n, lambda: construir(n - 1 if reguas else 0), cont_u=0.0035)
    k = 2.0 ** -n
    E.location = (0.0, -Y[n] * k, 0.0)
    return E


def amigo(n, pose="olha_baixo", cabeca=-28, olha=-24, rosto=None):
    """o amigo no chão onde parou, visto no passo n (verde: é a única cor que ele tem e não se confunde com o prédio)"""
    import story_passos4 as S4
    k = 2.0 ** -n
    return S4.amigo(n, X_AM * k, (Y_AM - Y[n]) * k, pose, cabeca=cabeca, olha=olha, rosto=rosto or dict(boca="o"))
