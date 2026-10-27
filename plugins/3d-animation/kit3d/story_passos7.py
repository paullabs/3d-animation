"""Plano v7 de "os passos" (aprovado em 25/10/2026: "anima o plano v7 com os dois ângulos"; personagem/passos/plano-v7.md).
Falas 1 a 7 (0 a 38,76 s) refeitas: A AVENIDA DA MEDIDA. Uma rua só, o mesmo mundo em todos os planos (o amigo fica no chão onde parou;
o poste e os prédios nos mesmos lugares), e dois ângulos por passo, cada um com a sua função:
  DE FRENTE (3/4)  = o impacto: pé alto, pisada, poeira e o rosto de susto;
  DE LADO (35 mm)  = a medida: a fita métrica, a referência (amigo, poste, prédios) e as pílulas com os números.
Planos: 1A frente (0-3,58) | 1B lado, a fita sobe (3,58-8,80) | 2A frente (8,80-10,0) | 2B lado (10,0-11,48) | 3A frente | 3B lado |
        4C, 4D, 4E (a queda, do v2, já de lado) | 5A frente | 5B lado | 5C rosto gritando | 5D lado, a onda desce | 6A frente | 6B lado |
        6C lado (o prédio de 55 m e a cabeça de 57,6 m) | 6D o cabelo, de longe | 6E o cabelo e o palito, de perto | 7A de pé, o peito pulsa | 7B e 7C raio X.
Mesmo uso do story_passos2: blender -b -P story_passos6.py -- PLANO x.png [--scale 0.5] | --list"""
import os, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy
from mathutils import Vector
import story_passos4 as S4                                 # (traz o v3 inteiro e o amigo)
import mundo7 as W                                          # O MUNDO FIXO: a mesma rua, os mesmos prédios, as mesmas réguas em todos os planos
import story_passos3 as S3
import story_passos2 as S2
import story_passos as SP
import provas_passos5 as PV                                # a avenida, a pílula, a fita lateral e a linha de altura
import objetos3d_passos as OP, objetos3d_passos_b as OB
import objetos3d_abrigo as O3
import elenco3d_abrigo as E3
import poses_passos as PP
import cena

SHOTS = S2.SHOTS
# toda rua do filme vem do mundo fixo (mundo7.py): nenhuma limpeza, nenhum prédio que some entre um plano e outro
PV.avenida = lambda n, extras=(): W.avenida(n)
S2.rua2 = lambda n, **kw: W.avenida(n)
S4.rua_vazia = lambda n, extras=(): W.avenida(n)
T_FIM = 38.76
MANTEM = ("4C", "4D", "4E")                                 # a queda: continua como no v2/v3 (já é de lado, no mesmo mundo)
for _k in [k for k, d in SHOTS.items() if d["t0"] < T_FIM - 0.01 and k not in MANTEM]:
    del SHOTS[_k]

X_AM_M, Y_AM_M = -1.4, 1.3                                  # onde o amigo fica, em metros, em relação ao ponto do 1º pouso (x, y)


def novo(nome, t0, t1, palavras, lente, nota):
    def deco(fn):
        SHOTS[nome] = dict(t0=t0, t1=t1, palavras=palavras, modo="M", lente=lente, nota=nota, fn=fn)
        it = sorted(SHOTS.items(), key=lambda kv: kv[1]["t0"]); SHOTS.clear(); SHOTS.update(it)
        return fn
    return deco


def amigo_mundo(n, pose="olha_baixo", cabeca=-28, olha=-24, rosto=None):
    """o amigo (verde) no chão onde parou, visto no passo n"""
    return W.amigo(n, pose, cabeca, olha, rosto)


def baixo(loc, alvo_xy, z_alvo, lente, z_foco, fstop=7.0):
    """câmera rente ao chão SEM inclinar (sem prédio caindo): olha na horizontal e o enquadramento sobe pela 'shift' da lente"""
    c = S2.cam(loc, (alvo_xy[0], alvo_xy[1], loc[2]), lente, fstop=fstop, foco=(alvo_xy[0], alvo_xy[1], z_foco), clip=0.003)
    d = math.hypot(alvo_xy[0] - loc[0], alvo_xy[1] - loc[1])
    c.data.shift_y = (z_alvo - loc[2]) / (d * 36.0 / lente)
    return c


def frente(vis=3.2, alvo=(0.1, 0.0, 0.95), lente=28, az=-30.0, el=-6.0):
    """a câmera do impacto: de frente, em 3/4 (à esquerda dele), um pouco de baixo"""
    return SP.cam_v(alvo, vis, lente, az=az, el=el, fstop=8.0, foco=alvo)


def lado(vis, alvo, lente=35):
    return PV.lateral(vis, alvo, lente)


def fita_e_pilulas(n, regua_y=-0.6, y_amigo=None, tam=0.11):
    """a fita métrica de pé (à direita dele, de lado) com a pílula da altura; e, se o amigo está no quadro, a linha de 1,8 m na cabeça dele
    (a linha cruza a cabeça e a pílula fica logo acima, sem encostar no corpo de ninguém)"""
    PV.regua_lateral(0.3, regua_y, 1.8, PV.altura(n), tam)
    if y_amigo is not None:
        k = 2.0 ** -n
        z = 1.8 * k
        OB.caixa("l_am", (tam * 0.05, 0.5 * k * 2, tam * 0.07), O3.brilha(OP.AMBAR, 1.6), (-1.2, y_amigo, z), cont=0.0)
        PV.pilula_amarela("l_am_p", "1,8 m", (-1.2, y_amigo, z + tam * 1.2), tam * 0.9)


def impacto(n, extras, amigo_no_quadro=False, rosto=None, vis=3.2, camera=None, pose="subida"):
    """o impacto: o mesmo mundo, outro ângulo a cada passo (camera = função que põe a câmera)"""
    PV.avenida(n, extras)
    h = S2.eu(pose, loc=(0, 0, 0), rosto=rosto or dict(boca="reta"))
    f = S2.pe_de(h, "F")
    OP.poeira_pouso(f.x, f.y - 0.05, r=0.45)
    if amigo_no_quadro:
        amigo_mundo(n)
    (camera or (lambda: frente(vis)))()
    return h


# ======================================================================== FALAS 1 e 2
@novo("1A", 0.00, 3.58, "E se cada passo que você desse dobrasse a sua altura?", "35 mm, de frente, travelling para trás",
      "Os dois andam de frente, do mesmo tamanho; o joelho dele sobe e fica no ar; em 'dobrasse' ele pisa e dobra; o amigo se assusta.")
def p1A():
    S4.rua_vazia(1)
    S2.eu("passagem", loc=(S4.X_EU, S4.Y0, 0), sombra=True)
    S4.amigo(1, S4.X_AM, S4.Y0, "passagem")
    OP.poeira_pouso(S4.X_EU + 0.02, -0.12, r=0.3)
    S2.cam((0.0, S4.Y0 - 1.7, 0.47), (-0.02, S4.Y0, 0.49), 35, fstop=8.0, foco=(0.0, S4.Y0, 0.5))


S4.AM_FIM = (X_AM_M * 0.5, Y_AM_M * 0.5)                    # onde o amigo para no 1A = onde ele fica no mundo (n = 1)


@novo("1B", 3.58, 8.80, "Você começa com um metro e oitenta. Depois do primeiro passo, são três metros e meio.", "35 mm, de lado, a fita sobe",
      "De lado: a fita métrica sobe do chão até a cabeça do amigo (1,8 m) e continua até a cabeça dele (3,6 m); as pílulas acendem em 'um' e em 'três'.")
def p1B():
    PV.avenida(1, ())
    S2.eu("olha_baixo", loc=(0, 0, 0), rosto=dict(boca="o"))
    amigo_mundo(1)
    fita_e_pilulas(1, y_amigo=Y_AM_M * 0.5)
    lado(3.7, (0.0, 0.3, 0.95))


@novo("2A", 8.80, 10.0, "No segundo passo,", "28 mm, de frente (3/4)",
      "O mesmo ponto de vista do 1º impacto: o pé B sobe, pisa em 'passo' (9,38 s) e ele dobra para 7,2 m; poeira; susto.")
def p2A():
    # de baixo, da calçada: o tênis enorme em primeiro plano (16 mm), o amigo e o ônibus lá atrás
    impacto(2, (), amigo_no_quadro=True, camera=lambda: baixo((-0.95, -0.85, 0.07), (0.1, 0.0), 0.85, 16, 0.4))


@novo("2B", 10.0, 11.48, "são sete metros.", "35 mm, de lado",
      "De lado: o poste de 7 m ao lado dele (7,2 m); o amigo, lá atrás, na ponta esquerda; a fita com a pílula 7,2 m.")
def p2B():
    PV.avenida(2, ("poste",))
    S2.eu("olha_baixo", loc=(0, 0, 0), rosto=dict(boca="o"))
    amigo_mundo(2)
    fita_e_pilulas(2, y_amigo=(S2.eu_y(1) + Y_AM_M - S2.eu_y(2)) * 0.25)
    lado(5.0, (0.0, 0.6, 1.7))


# ======================================================================== FALAS 3 e 4 (a queda continua no 4C, 4D e 4E)
@novo("3A", 11.48, 12.52, "No terceiro,", "28 mm, de frente (3/4)",
      "O 3º impacto: pisa em 'terceiro' (11,82 s) e dobra para 14,4 m; o prédio de 5 andares ao fundo.")
def p3A():
    # de frente, um pouco de cima, mais perto: o rosto e o prédio amarelo de 5 andares atrás
    impacto(3, ("p5",), camera=lambda: frente(3.0, alvo=(0.1, 0.0, 1.05), lente=35, az=-40.0, el=10.0))


@novo("3B", 12.52, 13.92, "são quinze metros.", "35 mm, de lado",
      "De lado: 14,4 m na altura do prédio de 5 andares (15 m); a fita com a pílula.")
def p3B():
    PV.avenida(3, ("p5",))
    S2.eu("olha_baixo", loc=(0, 0, 0), rosto=dict(boca="o"))
    fita_e_pilulas(3)
    lado(2.8, (0.0, -0.05, 1.25))                                  # mais perto: a cabeça dele e o telhado do prédio amarelo


# ======================================================================== FALA 5
@novo("5A", 17.36, 18.30, "No quarto,", "28 mm, de frente (3/4)",
      "Ele se levanta e pisa em 'quarto' (17,78 s): dobra para 28,8 m; o prédio de 10 andares ao fundo.")
def p5A():
    # por cima do ombro, de trás: ele se levanta e pisa em direção ao prédio de 10 andares lá na frente
    PV.avenida(4, ("p10",))
    S2.eu("apoio", loc=(0, 0, 0), rosto=dict(boca="o"))
    OP.poeira_pouso(0.02, -0.12, r=0.4)
    S2.cam((-0.5, 2.6, 1.25), (0.0, -0.6, 0.8), 24, fstop=8.0, foco=(0.0, 0.0, 0.8))


@novo("5B", 18.30, 20.06, "são quase trinta metros.", "35 mm, de lado",
      "De lado: 28,8 m na altura do prédio de 10 andares (30 m); a fita com a pílula.")
def p5B():
    PV.avenida(4, ("p10",))
    S2.eu("olha_baixo", loc=(0, 0, 0), rosto=dict(boca="o"))
    fita_e_pilulas(4)
    lado(5.5, (0.0, 0.55, 1.9))                                    # mais largo: as réguas dos passos de antes ficam à esquerda


@novo("5C", 20.06, 21.12, "Sua voz leva", "65 mm, de frente, o rosto",
      "O rosto: ele grita para baixo com as mãos em volta da boca.")
def p5C():
    PV.avenida(4, ("p10",))
    h = S2.eu("grito", loc=(0, 0, 0))
    SP.cam_v((0.0, 0.0, 1.45), 1.7, 65, az=-22, el=-4, fstop=5.0, foco=(0.0, 0.0, 1.55))


@novo("5D", 21.12, 23.58, "um décimo de segundo para chegar aos pés.", "35 mm, de lado, a onda desce",
      "De lado: a onda branca desce da boca até os pés em câmera lenta; a linha de 29 m e os tempos 0, 0,05 e 0,1 s; a poça balança no fim.")
def p5D():
    PV.avenida(4, ("p10", "poca"))
    h = S2.eu("grito", loc=(0, 0, 0))
    b = Vector((0.0, -0.1, 1.5))
    tam = 0.1
    # a medida: da boca aos pés, 29 m (1,7 u)
    OB.caixa("mede_vert", (tam * 0.05, tam * 0.05, 1.4), O3.brilha(OP.AMBAR, 1.6), (-0.3, -0.55, 0.8), cont=0.0)
    PV.pilula("p_29", "25 m", (-0.35, -0.55, 0.8), tam * 1.1)
    for i, (z, t) in enumerate(((1.5, "0 s"), (0.8, "0,05 s"), (0.1, "0,1 s"))):
        PV.pilula(f"p_t{i}", t, (-0.3, 0.62, z), tam)
        O3.anel(f"som{i}", 0.5 + 0.1 * i, 0.012, O3.brilha("#ffffff", 1.8 - 0.4 * i), None, (0.0, -0.05, z), eixo="Z", seg=64, contorno=0.0)
    O3.anel("onda_desce", 0.5, 0.02, O3.brilha("#ffffff", 2.2), None, (0.0, -0.05, 1.5), eixo="Z", seg=64, contorno=0.0)
    px, py, _ = S2.em_u(4, *S2.LUGAR["poca"])
    OB.ondas_poca("onda", (px, py, 0.0), n=3, r0=0.04, passo=0.05)
    lado(3.7, (0.0, 0.0, 1.25))


# ======================================================================== FALA 6
@novo("6A", 23.58, 24.96, "No quinto passo,", "28 mm, de frente (3/4)",
      "O 5º impacto: pisa em 'quinto' (23,92 s) e dobra para 57,6 m; o prédio de 18 andares ao fundo.")
def p6A():
    # rente ao chão, de frente (16 mm): ele enorme e o prédio azul de 18 andares atrás
    impacto(5, ("p18",), camera=lambda: baixo((0.5, -1.9, 0.1), (0.0, 0.0), 1.0, 20, 0.6))


@novo("6B", 24.96, 26.76, "são quase sessenta metros.", "35 mm, de lado",
      "De lado: 57,6 m ao lado do prédio de 18 andares (55 m); a fita com a pílula.")
def p6B():
    PV.avenida(5, ("p18",))
    S2.eu("olha_baixo", loc=(0, 0, 0), rosto=dict(boca="o"))
    fita_e_pilulas(5)
    lado(4.6, (0.0, 0.75, 1.6))                                     # de longe: a escada de alturas (3,6 / 7,2 / 14,4 / 28,8 / 57,6 m) toda na rua


@novo("6C", 26.76, 29.02, "Isso é mais alto que um prédio de dezoito andares.", "35 mm, de lado, sobe até o topo",
      "De lado: o topo do prédio (55 m) numa linha, a cabeça dele (57,6 m) passando da linha; a câmera sobe até o topo.")
def p6C():
    PV.avenida(5, ("p18",))
    S2.eu("olha_baixo", loc=(0, 0, 0), rosto=dict(boca="reta"))
    k = 2.0 ** -5
    tam = 0.1
    PV.linha_altura("topo_pred", 55 * k, -0.9, 0.95, tam, "prédio: 55 m", x=-0.3)
    PV.pilula("p_ele", "ele: 57,6 m", (-0.3, -0.9 - 0.62, 1.8 + tam * 0.4), tam)
    lado(3.0, (0.0, 0.0, 1.0))


def cena_cabelo():
    """o gigante (57,6 m) de perfil, no ponto do 5º pouso, olhando para o prédio azul; o limpador no balancim, na altura da cabeça dele"""
    import ik3_abrigo as IK
    W.avenida(5)
    g = S2.eu(dict(cabeca=-4, olha=0), loc=(0, 0, 0), rot=90, sombra=False)
    bpy.context.view_layer.update()
    piso = bpy.data.objects["p18_bal_piso"].matrix_world.translation
    k = 2.0 ** -5
    h = E3.faz("limpador", "limp"); h.raiz.scale = (S2.EU_ESC * k * 0.95,) * 3
    h.pose(**h.pe_no_chao(**dict(SP.STAND))); h.raiz.location = (piso.x, piso.y, piso.z); h.raiz.rotation_euler.z = math.radians(-90)
    PP.assenta(h, piso.z + 0.0035)
    bpy.context.view_layer.update()
    return g, h


@novo("6D", 29.02, 30.26, "O seu cabelo", "70 mm, o gigante de perfil, de longe",
      "O gigante de perfil, a cabeça perto do balancim do prédio azul; o limpador de janela olha para ele.")
def p6D():
    # o gigante de perfil com a cabeça na altura do balancim; o limpador (1,8 m) fica na beirada do balancim, na frente do prédio
    cena_cabelo()
    S2.cam((0.5, -2.6, 1.45), (0.3, 0.0, 1.35), 50, fstop=8.0, foco=(0.3, 0.0, 1.4), clip=0.01)
    PV.pilula_y("rot_gig", "gigante: 57,6 m", (0.06, -0.12, 1.98), 0.05)
    PV.pilula_y("rot_lim", "limpador: 1,8 m", (0.52, -0.12, 1.9), 0.04)


@novo("6E", 30.26, 32.72, "tem a grossura de um palito de dente.", "65 mm, de perto",
      "O fio do cabelo dele ao lado do palito de dente: a mesma grossura; as pílulas dizem 2,4 mm e 2 mm.")
def p6E():
    from heroi3d import tubo
    import ik3_abrigo as IK
    W.construir(0)                                                       # o mesmo mundo, em metros: a vinheta fica no ar, em cima da avenida
    base = Vector((0.0, 0.0, 20.0))
    h = E3.faz("limpador", "limp"); h.raiz.scale = (S2.EU_ESC,) * 3
    h.pose(**h.pe_no_chao(**dict(SP.STAND))); h.raiz.location = (base.x + 0.55, base.y + 0.05, base.z); h.raiz.rotation_euler.z = math.radians(-90)
    PP.assenta(h, base.z)
    bpy.context.view_layer.update()
    alvo = Vector((base.x - 0.05, base.y - 0.02, base.z + 1.12))
    P = IK.braco_pose(h, "F", tuple(alvo), dict(getattr(h, "_ultima", {})), nome="limp")
    h.pose(**P); bpy.context.view_layer.update()
    m = h.punho["F"].matrix_world.translation
    pc = Vector((m.x - 0.02, m.y - 0.055, m.z + 0.105))
    OP.palito("palito", tuple(pc), 0.002, 0.065, eixo="Z")
    fim = pc + Vector((0.0046, 0.0, 0.0))
    tubo("fio_solto", [(fim.x + 0.03, fim.y, pc.z + 0.34), (fim.x + 0.012, fim.y, pc.z + 0.21), (fim.x + 0.0075, fim.y, pc.z + 0.1), (fim.x, fim.y, pc.z + 0.03), (fim.x, fim.y, pc.z - 0.01)],
         [0.0012] * 5, OP.M("#2a1c16", "#120c09", "#6a4a3a"), None, seg=12, tampa=4, contorno=0.0)
    for q, (dx, dz, esp) in enumerate(((-0.05, 0.30, 0.0008), (0.045, 0.28, 0.0009), (0.075, 0.31, 0.0008))):
        tubo(f"fio_ao_fundo{q}", [(fim.x + dx, fim.y + 0.04, pc.z + 0.34), (fim.x + dx * 0.9, fim.y + 0.04, pc.z + dz * 0.8), (fim.x + dx * 0.85, fim.y + 0.04, pc.z + dz * 0.55)],
             [esp] * 3, OP.M("#2a1c16", "#120c09", "#6a4a3a"), None, seg=10, tampa=4, contorno=0.0)
    # o quadro: o palito no meio, grande, e o fio ao lado dele (4,6 mm de distância, a mesma grossura de 2 mm contra 2,4 mm)
    cx = pc.x + 0.0023
    S2.cam((cx, pc.y - 0.17, pc.z), (cx, pc.y, pc.z), 50, fstop=8.0, foco=(pc.x, pc.y, pc.z), clip=0.005)
    tam = 0.0036
    PV.pilula_y("t_pal", "palito: 2 mm", (pc.x - 0.019, pc.y - 0.01, pc.z + 0.03), tam)
    PV.pilula_y("t_fio", "cabelo: 2,4 mm", (pc.x + 0.024, pc.y - 0.01, pc.z - 0.03), tam)


# ======================================================================== FALA 7
@novo("7A", 32.72, 33.96, "Nessa altura,", "35 mm, de lado, ele de pé",
      "Ele de pé na avenida, os braços soltos, o peito sobe e desce; o coração pulsa (anel vermelho no peito).")
def p7A():
    PV.avenida(5, ("p18",))
    S2.eu("olha_baixo", loc=(0, 0, 0), rosto=dict(boca="reta"))
    for i in range(2):
        O3.anel(f"pulso{i}", 0.16 + 0.1 * i, 0.012, O3.brilha("#ff4a3a", 1.8), None, (-0.12, 0.0, 1.25), eixo="X", seg=48, contorno=0.0)
    lado(3.7, (0.0, -0.1, 1.25))


@novo("7B", 33.96, 36.34, "o coração precisa de mais de uma atmosfera e meia", "50 mm, raio X na rua",
      "Ali mesmo na rua, o corpo dele fica translúcido: o coração vermelho bate e um manômetro ao lado sobe até 1,65 atm.")
def p7B():
    h, zc = S3.raio_x_rua()
    OP.manometro("man", (0.36, -0.25, zc), 0.2, 1.65, " ", faixa=(0.0, 2.0), zona_vermelha=1.5)
    OB.caixa("man_placa", (0.5, 0.02, 0.56), OP.M("#f4f1e8", "#d9d4c4"), (0.36, -0.2, zc), cont=0.0)       # placa clara atrás do mostrador: separa do fundo
    PV.pilula_y("man_lab", "pressão no coração: 1,65 atm", (0.36, -0.3, zc - 0.36), 0.03)
    OB_tubo = S3.tubo
    OB_tubo("mangueira", [(0.08, -0.04, zc), (0.22, -0.14, zc - 0.06), (0.33, -0.22, zc)], [0.007] * 3, OP.M("#3a3f46"), None, seg=10, tampa=4, contorno=0.002)
    S2.cam((0.35, -2.4, 1.25), (0.22, 0.0, 1.2), 50, fstop=5.6, foco=(0.1, -0.1, 1.25))


@novo("7C", 36.34, 38.76, "de pressão para levar o sangue até a cabeça.", "50 mm, raio X na rua",
      "O sangue sobe em pulsos do coração até a cabeça; a chave ao lado mostra a distância: 16 m (a pílula escura, que se lê).")
def p7C():
    h, zc = S3.raio_x_rua()
    H = S3.H
    OB.caixa("chave_16", (0.012, 0.012, H - zc), O3.brilha(OP.AMBAR, 1.5), (-0.3, -0.05, (H + zc) / 2), cont=0.0)
    for z in (zc, H):
        OB.caixa(f"chave_p{z:.2f}", (0.06, 0.012, 0.012), O3.brilha(OP.AMBAR, 1.5), (-0.27, -0.05, z), cont=0.0)
    PV.pilula_y("t16", "16 m", (-0.43, -0.07, (H + zc) / 2), 0.1)
    S2.cam((-0.14, -2.6, 1.42), (-0.14, 0.0, 1.42), 50, fstop=5.6, foco=(0.0, -0.1, 1.5))


def main():
    S2.main()


if __name__ == "__main__":
    main()
