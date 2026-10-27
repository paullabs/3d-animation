"""Storyboard v3 de "O abrigo" (decupagem v3: personagem/abrigo/decupagem-cinema-v3.md): 67 planos de no máximo 1,3 s, um quadro parado por plano,
com a lente, a posição, o foco e a profundidade de campo de verdade, agora com os objetos 3D (objetos3d_abrigo, objetos3d_abrigo_b), a rua viva
(cidade3d), o bunker à vista, a porta única de dentro e de fora, as mãos 3D de quem conta e a câmera de segurança (pos_cctv).
A tabela SHOTS é a fonte única: o storyboard (story3_montar.py) e a decupagem em texto (story3_doc.py) saem dela.
blender -b -P story3_abrigo.py -- PLANO SAIDA.png [--scale 0.5] [--samples 16]      (PLANO = 1A, 1B, ... ; --list mostra todos)"""
import os, sys, math, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy, lib
from lib import *
from mathutils import Vector, Euler, Matrix
import cena, props, luz, sets4 as S
import objetos3d_abrigo as O3, objetos3d_abrigo_b as O3B, cidade3d as C3, cenario3d_abrigo as CA, elenco3d_abrigo as E3
import story_abrigo as SA, ik3_abrigo as IK
from prod_abrigo import pal, mundo, halo, ceu
from heroi3d import corrida

SHOTS = {}
ESQ = None                                                 # a esquerda da câmera do 11D (de onde o vulto entra)
ZUMBI = None                                               # o vulto desfocado do plano final (11D)
BY = 17.0                                                  # onde fica o bunker no fim da rua (y)


def shot(nome, t0, t1, palavras, lente, foco, mov, vemos, cctv=None):
    """registra um plano: tempo (s) na voz aprovada, as palavras cobertas, lente e posição, foco, movimento, o que se vê e por quê"""
    def deco(fn):
        SHOTS[nome] = dict(t0=t0, t1=t1, palavras=palavras, lente=lente, foco=foco, mov=mov, vemos=vemos, cctv=cctv, fn=fn)
        return fn
    return deco


# ---------------------------------------------------------------- câmera e peças comuns
def cam(*a, **k):
    c = SA.camera(*a, **k)
    O3.olha_camera(c)
    return c


def mundo_(nome="rua"):
    p = pal(nome); mundo(p); return p


def rua3(morta=False, aberta=0.9, y_b=BY, carros=False, nevoa=True, fundo=True, y0=-8.0, branco=False):
    """a rua do bairro em 3D, o bunker no fim e a rua que continua atrás dele; morta = a mesma rua depois (ruínas, cinza, céu branco sujo)"""
    p = pal("cinza" if morta else "rua"); mundo(p)
    topo, meio = ("#a9a597", "#cfc9b4") if morta else (("#dedcd0", "#f4f1e6") if branco else ("#7f857b", "#b6b4a2"))     # branco = depois do clarão
    ceu(p, 60.0, topo=topo, meio=meio)
    ceu(p, y0 - 14.0, topo=topo, meio=meio)                                                                          # o céu também atrás, para quando a câmera olha a rua para trás
    cena.poly_mesh("chao_largo", [(-300, y0 - 14.0, -0.03), (300, y0 - 14.0, -0.03), (300, y_b + 130.0, -0.03), (-300, y_b + 130.0, -0.03)], props.FM(p["chao"]))
    C3.rua3d(p, y0, y_b - 0.5, carros=carros, ruina=morta, poeira=0.6 if morta else 0.0)
    if fundo:
        C3.rua3d(p, y_b + 7, y_b + 39, carros=False, seed=9, ruina=morta, poeira=0.6 if morta else 0.0)
    C3.entrada_bunker("bunker", (0, y_b, 0), 1.0, aberta=aberta, poeira=0.6 if morta else 0.0)
    if aberta < 0.05:                                                   # porta fechada: a luz de dentro não vaza pela rua
        bpy.data.objects["bunker_luz_dentro"].hide_render = True
    if branco:
        for yv in (3.0, 8.0, 12.0):
            S.neblina(p, yv, 0.2, cor="#f6f3e8", z1=40.0)
    elif nevoa:
        for yv in (10.0, 30.0):
            S.neblina(p, yv, 0.14 if morta else 0.06, z1=40.0)
    if morta:
        cena.dust(p, 90, (-5, 5), 30, seed=3, color="#e8e2cc", alpha=0.85, y_range=(-2.0, y_b), z_range=(0.2, 4.5), size=(0.008, 0.02))
    return p


SIRENE_S = 1.8                                                  # a sirene de bairro tem uns 6 m de poste


def sirene(x=4.4, y=8.5, caida=False, poeira=0.0, ondas=True, lado=-1):
    if caida:                                                   # deitada no asfalto: o poste ao longo de x e o braço das cornetas na horizontal
        piv = empty("sirene_piv", None, (x, y, 0.34)); piv.rotation_euler = (0, math.radians(84), math.radians(10))
        s = O3.sirene3d("sirene", (0, 0, 0), SIRENE_S, pai=piv, acesa=False, poeira=poeira); s.rotation_euler.z = math.radians(90)
        return s
    s = O3.sirene3d("sirene", (x, y, 0), SIRENE_S, acesa=True, poeira=poeira); s.rotation_euler.z = math.radians(90)      # o braço fica ao longo da rua
    if ondas:                                                                                                    # as ondas de som saem da corneta que olha para a câmera (-y)
        for k, R in enumerate((0.35, 0.62, 0.9)):
            O3.anel(f"onda_{k}", R, 0.014, O3.brilha("#e2443a", 1.4), None, (x, y + lado * (0.79 * SIRENE_S + 0.15 + R * 0.35), 2.82 * SIRENE_S), eixo="Y", seg=40, a0=-50, a1=50, contorno=0.0)
    return s


def ciclista(x, y, cor="#8e3a30", ombro=(-50, -50), cotovelo=(-6, -6)):
    """quem conta ('eu', blusa vermelha escura) pedalando a bicicleta de cesta, de frente para +y: a bicicleta no meio da rua, o corpo sentado no selim,
    as mãos nas manoplas, uma perna na frente e a outra atrás"""
    b = O3.bicicleta3d("bici", (x, y, 0.0), 1.0, cor); b.rotation_euler.z = math.radians(90)
    h = E3.faz("eu", "eu_inv")
    h.pose(quadril=(-46, 14), joelho=(78, 30), tornozelo=(10, -6), ombro=ombro, cotovelo=cotovelo, abre=(12, 12), tronco=-12, cabeca=-6, alt=0.93)
    h.raiz.location = (x, y - 0.27, 0.0); h.raiz.rotation_euler.z = math.radians(180)
    cena.ground_disc("eu_sb", 0.6, 0.3, cena.amat("eu_sb_m", "#000000", 1.0, 0.38, ("radial", 1.1)), (x, y, 0.003), n=32)
    return b, h


def corredores(lista, rosto=dict(boca="o", lid=0.0)):
    """lista de (chave, nome, x, y, fase, rot) de gente correndo, com cara de susto; devolve os bonecos"""
    out = []
    for ch, nm, x, y, fase, rot in lista:
        h = SA.corre(ch, nm, x, y, rot=rot, fase=fase, inclina=12)
        h.rosto(**rosto); out.append(h)
    return out


def luz_branca(x, y, z, r=7.0, alfa=0.9):
    return halo("clarao", x, y, z, r, "#ffffff", alfa)


def fora_dia(p, wy, morta=False, branco=False, y1=40.0):
    """o lado de fora atrás da porta de dentro: a MESMA rua em 3D, longe da parede do fundo; branco = o clarão"""
    props.skywall("ceu_fora", wy + 45.0, [(-2.0, "#fbf8ee" if branco else ("#cfc9b4" if morta else "#b6b4a2")), (6.0, "#f4f0e2" if branco else ("#a9a597" if morta else "#9aa094")),
                                         (14.0, "#e6e1cf" if branco else ("#a9a597" if morta else "#7f857b")), (120.0, "#c9c4b0" if branco else ("#a9a597" if morta else "#7f857b"))], -160, 160, -2.0, 120.0)
    C3.rua3d(p, wy + 0.4, wy + y1, carros=False, seed=5, ruina=morta, poeira=0.6 if morta else 0.0)
    for yv in (wy + 10.0, wy + 24.0):
        S.neblina(p, yv, 0.5 if branco else (0.16 if morta else 0.08), cor="#f6f2e4" if branco else None, z1=40.0)


def foyer3(aberta=0.0, wy=4.6, fora="nenhum", vizinhos=False, lamp=True):
    """a porta por dentro: a sala curta do vão da porta (a mesma porta3d das cenas e da rua); fora = nenhum | branco | viva | morta"""
    p = pal("abrigo")
    CA.sala3d(p, wy=wy, x0=-2.7, x1=2.7, porta_x=0.0, porta_s=1.15)
    O3.porta3d("porta", (0, wy - 0.1, 0), 1.15, aberta=aberta, lado="dentro")
    if fora == "nenhum":
        CA.fora_porta(p, 0.0, wy, vizinhos=vizinhos)
    else:
        fora_dia(p, wy, morta=(fora == "morta"), branco=(fora == "branco"))
    if lamp:
        O3.lampada3d("lampA", (-1.2, wy - 1.3, LAMP_Z), LAMP_S, acesa=True, fio=0.35)
    return p, wy


# ====================================================================== 1. A corrida (0,00 a 7,12 s)
# Geografia (pedido de 25/10/2026): a rua corre ao longo de +y e o bunker fica no fim dela. Câmeras "da rua" olham para +y (o rumo da corrida);
# câmeras "do bunker" olham para -y (a multidão vem correndo para nós). Abre de frente para quem pedala, depois entra nos olhos dele (POV).
COG = (2.2, -20.5)                                         # onde sobe o cogumelo: depois do fim da rua, atrás de quem pedala (a rua olha para -y)


def cogumelo(t):
    """o cogumelo da explosão lá no fundo, no tamanho do segundo t do filme (o anim3_abrigo faz ele crescer quadro a quadro)"""
    r = O3B.cogumelo3d("cogumelo", (COG[0], COG[1], 0), 22.0)
    halo("cogumelo_gl", COG[0], COG[1] + 0.5, 12.0, 16.0, "#ffb070", 0.35)
    ch = cena.disc("cogumelo_chao", 30.0, cena.amat("cogumelo_chao_m", "#ffb070", 1.0, 0.3, ("radial", 1.6)), (COG[0], COG[1] + 2.0, 0.025))
    ch.rotation_euler.x = math.radians(90)                            # o reflexo quente da explosão no asfalto, mais forte lá no fundo
    O3B.cogumelo_em(r, t)
    return r


# Quem não vai entrar (pedido de 25/10/2026: "ele larga a bicicleta e não tem ninguém; depois aparece muita gente atrás"): os vizinhos correm
# desde o primeiro plano, atrás de quem pedala, todos a 2,9 m/s; o rapaz do mercado chega à porta em 8,75 s, quando ela acaba de fechar.
ATRASO_V = 2.9
ATRASADOS = [("mercado", "mercado", 1.2, 0.0, 5), ("padeira", "padeira", -1.0, -1.6, 1), ("viz1", "vizA", 0.3, -3.0, 4),
             ("viz2", "vizB", 1.8, -4.4, 2), ("viz3", "vizC", -1.8, -5.8, 6), ("viz4", "vizD", -0.4, -7.0, 3)]


def atrasados(t, n=6):
    """os vizinhos que correm atrás, onde estão no segundo t do filme"""
    y_m = BY - ATRASO_V * (8.75 - t)
    return corredores([(ch, nm, x, y_m + dy, fase, 180) for ch, nm, x, dy, fase in ATRASADOS[:n]])


# Continuidade refeita em 25/10/2026 ("tem muito corte sem sentido"): uma linha só de ação, cada corte nasce do plano anterior.
# O cogumelo já está lá no fundo desde o 1A e cresce o tempo todo; quem conta freia, pula da bicicleta e sai correndo (1B → 1C no mesmo gesto);
# o POV corre atrás do Zé, da Lu e da Rita (1D); do bunker vemos os mesmos chegando e, atrás deles, o cogumelo (1E); de cima, a geografia
# inteira enquanto o céu clareia (1F); o clarão estoura e vai baixando sobre a porta enquanto quem conta entra e o Zé chama e entra por último (2A);
# de dentro, o Zé atravessa a porta, vira e fecha (2B). Quem ficou para trás no 1E (padeira, mercado, vizinhos) é quem bate na porta no 2D a 2F.
@shot("1A", 0.00, 1.20, "Quando a sirene tocou", "24 mm, de frente para quem pedala, baixa, recuando junto", "o rosto de quem conta e o cogumelo atrás", "dolly para trás",
      "De frente para quem conta, pedalando na nossa direção. Atrás dele, no fim da rua, o cogumelo da explosão sobe por cima dos prédios e a sirene grita no poste. Ele olha para trás por cima do ombro.")
def p1A():
    p = rua3(carros=False)
    by = 2.0
    cogumelo(0.6)
    sirene(3.2, by - 6.0, lado=1)
    b, h = ciclista(0.0, by)
    h.pose(quadril=(-46, 14), joelho=(78, 30), tornozelo=(10, -6), ombro=(-50, -50), cotovelo=(-6, -6), abre=(12, 12), tronco=-12, cabeca=-8, olha=-18, alt=0.93)
    h.rosto(boca="o", lid=0.0)
    atrasados(0.0)
    cam((0.55, by + 2.4, 0.9), (0.4, by - 0.3, 1.45), 24, fstop=5.6, foco=(0.0, by - 0.25, 1.3), roll=-2)


@shot("1B", 1.20, 2.00, "eu larguei", "24 mm, três quartos, baixa, na calçada", "ele pulando da bicicleta", "parada",
      "Ainda na rua, de três quartos: ele freia, põe o pé no chão e pula da bicicleta para o lado; a bicicleta segue sozinha e começa a tombar. O cogumelo continua atrás, maior.")
def p1B():
    p = rua3(carros=False)
    by = 5.0
    cogumelo(1.6)
    b, h = ciclista(0.0, by)
    h.pose(quadril=(-30, 20), joelho=(40, 20), tornozelo=(10, 0), ombro=(-40, 20), cotovelo=(-30, -40), abre=(14, 20), tronco=-16, cabeca=-4, alt=0.98)
    h.raiz.location = (0.45, by - 0.1, 0.0); h.rosto(boca="o", lid=0.0)
    b.rotation_euler = (math.radians(-12), 0, math.radians(90))
    atrasados(1.2)
    cam((1.25, by + 4.6, 1.05), (0.55, by - 6.0, 1.9), 24, fstop=5.6, foco=(0.2, by, 1.0))


@shot("1C", 2.00, 3.00, "a bicicleta", "14 mm, no chão, colada na roda da frente", "a bicicleta caindo e ele saindo", "parada",
      "No chão, colado na roda da frente: a bicicleta termina de cair na direção da lente e bate no asfalto, a roda girando. Atrás dela, as pernas dele já correm para o bunker, e lá na frente o Zé e a Lu.")
def p1C():
    p = rua3(carros=False)
    by = 5.3
    b = O3.bicicleta3d("bici", (0.0, by, 0.0), 1.0); b.rotation_euler = (math.radians(-55), 0, math.radians(90))
    eu = SA.corre("eu", "eu", 0.9, by + 2.4, rot=180, fase=3)
    corredores([("ze", "ze", -0.5, by + 7.0, 3, 180), ("lu", "lu", 0.7, by + 5.8, 6, 180)])
    bpy.context.view_layer.update()
    hub = bpy.data.objects["bici_cubo1"].matrix_world.translation.copy()
    cam((hub.x - 0.75, hub.y - 0.55, 0.16), (hub.x + 0.5, hub.y + 3.0, 0.45), 14, fstop=2.8, foco=(hub.x, hub.y, hub.z), roll=-4)


@shot("1D", 3.00, 4.10, "e corri pro abrigo", "24 mm, POV correndo, mãos fechadas balançando", "o bunker no fim da rua", "câmera na mão",
      "Os olhos de quem corre: os punhos balançam, o Zé, a Lu e a Rita correm na frente e o bunker cresce no fim da rua, com a porta aberta e a luz âmbar.")
def p1D():
    p = rua3(carros=False)
    corredores([("ze", "ze", -0.35, 10.6, 3, 180), ("lu", "lu", 0.55, 9.6, 6, 180), ("rita", "rita", 1.0, 11.8, 2, 180)])
    c = cam((0.05, 6.6, 1.62), (0.0, BY, 1.3), 24, fstop=8.0, foco=(0.0, 11.0, 1.2), roll=2.0)
    r, me, md = O3.maos_pov3d(c, "maos", d=0.5, escala=1.0)
    me.pose("fechada"); md.pose("fechada")
    me.raiz.location = (-0.17, 0.62, -0.26); md.raiz.location = (0.17, 0.40, -0.19)
    me.raiz.rotation_euler = (math.radians(-6), 0, math.radians(6)); md.raiz.rotation_euler = (math.radians(26), 0, math.radians(-6))


def sem_halo_do_bunker():
    """a câmera dentro do pórtico fica atrás do halo âmbar da porta: esconde para a imagem não virar sépia"""
    o = bpy.data.objects.get("bunker_luz_dentro")
    if o is not None:
        o.hide_render = True


def gente_correndo(perto=True):
    """vista do bunker: a Rita e a Lu chegam e entram, o Zé chega e para do lado da porta, quem conta vem logo atrás;
    lá atrás quem não vai chegar a tempo (padeira, mercado, vizinhos) e, no fim da rua, o cogumelo"""
    L = [("rita", "rita", 0.4, BY - 2.2, 2, 180), ("lu", "lu", 0.15, BY - 3.6, 6, 180), ("ze", "ze", 0.95, BY - 2.8, 3, 180), ("eu", "eu", -0.2, BY - 5.6, 5, 180)]
    return corredores(L) + atrasados(4.1)


@shot("1E", 4.10, 5.30, "no fim da rua", "24 mm, do bunker, no vão da porta, olhando a rua de volta", "os que chegam e o cogumelo atrás", "parada",
      "A câmera chega ao bunker antes de quem corre e se vira: a Rita e a Lu passam por nós e entram, o Zé chega e para do lado da porta, quem conta vem logo atrás. Lá atrás, quem não vai chegar a tempo, e no fim da rua o cogumelo, enorme.")
def p1E():
    p = rua3(carros=False); sem_halo_do_bunker()
    cogumelo(4.7)
    gente_correndo()
    cam((-0.5, BY - 0.2, 1.5), (0.3, BY - 22.0, 2.6), 24, fstop=8.0, foco=(0.0, BY - 6.0, 1.4))


@shot("1F", 5.30, 6.50, "O céu ficou branco na mesma hora", "20 mm, do alto do bunker, olhando a rua inteira", "a rua, a porta e o cogumelo", "parada",
      "Do alto, em cima da porta: lá embaixo o Zé chamando na porta e quem conta chegando; no meio da rua os vizinhos ainda correndo; no fim, o cogumelo. A luz dele vai tomando o céu até ficar branco.")
def p1F():
    p = rua3(carros=False); sem_halo_do_bunker()
    cogumelo(5.9)
    SA.ator3("ze", "ze", 0.9, BY - 1.8, rot=-160, pose=dict(ombro=(-148, 8), cotovelo=(-24, -12), abre=(10, 4), tronco=-4, cabeca=4, olha=-14), rosto=dict(boca="o", lid=0.0))
    corredores([("eu", "eu", -0.1, BY - 3.2, 5, 180)]); atrasados(5.3)
    luz_branca(COG[0], COG[1] + 1.0, 14.0, 60.0, 0.0)
    cam((-2.0, BY + 0.9, 7.6), (0.3, BY - 11.0, -0.4), 18, fstop=8.0, foco=(0.0, BY - 6.0, 1.0))


@shot("2A", 6.50, 7.90, "(clarão) O Zé foi o último a entrar", "24 mm, de fora, três quartos, na altura dos olhos", "a porta e quem passa", "parada",
      "O clarão estoura e vai baixando até a imagem voltar: quem conta passa pela porta, o Zé no batente acena para quem ainda vem lá longe, desiste, vira e entra por último.")
def p2A():
    p = rua3(carros=False, branco=True)
    corredores([("eu", "eu", -0.2, BY - 1.2, 3, 180)], rosto=dict(boca="o", lid=0.0))
    SA.ator3("ze", "ze", 0.85, BY - 1.0, rot=-25, pose=dict(ombro=(-148, 8), cotovelo=(-24, -12), abre=(10, 4), tronco=-4, cabeca=4, olha=-14), rosto=dict(boca="o", lid=0.0))
    atrasados(6.5, 4)
    cam((-2.5, BY - 3.5, 1.25), (0.2, BY - 0.2, 1.2), 24, fstop=5.6, foco=(0.0, BY - 0.8, 1.2))


@shot("2B", 7.90, 9.20, "e trancou a", "18 mm, de fora, de lado, baixa, colada no pilar", "a porta fechando na cara de quem chega", "parada",
      "De fora e de lado: a folha corre e fecha o vão de luz âmbar enquanto o rapaz do mercado, a dona da padaria e os vizinhos chegam correndo. O rapaz estica o braço, mas a porta bate na frente dele; ele chega a tempo só de bater no aço. Fica claro que ninguém entrou.")
def p2B():
    p = rua3(aberta=0.55, carros=False, branco=True)
    atrasados(7.9, 4)
    cam((-2.7, BY - 2.6, 1.05), (0.35, BY - 0.1, 1.3), 20, fstop=4.0, foco=(0.3, BY - 0.4, 1.3))


@shot("2C", 9.20, 9.90, "porta", "14 mm, colada na roda de giro", "as mãos do Zé", "parada",
      "As mãos 3D do Zé agarram a roda de bronze e giram: a folha fechou, a fresta sumiu e fica só o âmbar. Este enquadramento volta no fim, ao contrário.")
def p2C():
    p, wy = foyer3(aberta=0.0, fora="branco", lamp=False)
    ze = SA.ator3("ze", "ze", 0.0, wy - 0.75, rot=180, pose=dict(ombro=(-92, -92), cotovelo=(-18, -18), abre=(12, 12), tronco=-4))
    ze.fecha_mao("F"); ze.fecha_mao("B")
    roda = bpy.data.objects["porta_roda"]; roda.rotation_euler = (0, math.radians(-40), 0)
    bpy.context.view_layer.update()
    c = roda.matrix_world.translation
    SA.maos_em(ze, (c.x - 0.2 + 0.15, c.y - 0.06, c.z + 0.12), (c.x + 0.2 + 0.15, c.y - 0.06, c.z - 0.05))
    cam((0.62, wy - 0.78, 1.5), (0.05, wy - 0.12, 1.3), 14, fstop=2.8, foco=(0.1, wy - 0.15, 1.32))


def povo(y_b=BY, n=6):
    """quem ficou lá fora, de costas para a câmera, colado na porta"""
    ch = [("padeira", "pv0", -0.55, 1.5, 175), ("mercado", "pv1", 0.35, 1.7, 185), ("viz1", "pv2", 1.2, 2.3, 170), ("viz2", "pv3", -1.45, 2.4, 190),
          ("viz3", "pv4", 0.0, 3.1, 180), ("viz4", "pv5", -0.7, 3.4, 178)][:n]
    out = []
    for k, (chave, nome, dx, dy, rot) in enumerate(ch):
        h = SA.ator3(chave, nome, dx, y_b - dy, rot=rot, pose=dict(ombro=(-118 + 8 * (k % 3), -96 - 6 * (k % 2)), cotovelo=(-22, -40), abre=(10, 6), tronco=-6, cabeca=-8))
        out.append(h)
    return out


@shot("2D", 9.90, 11.00, "Do lado de fora, o povo", "24 mm, baixo, atrás da multidão, de fora", "a porta fechada", "parada",
      "O outro lado da mesma porta, agora fechada, com a placa ABRIGO em cima: o povo do bairro, que chegou tarde, de costas para nós, colado no aço, sob o céu branco do clarão. Quem corria não entrou a tempo.")
def p2D():
    p = rua3(aberta=0.0, carros=False, branco=True)
    povo(BY, 6)
    cam((-1.5, BY - 5.4, 1.15), (0.1, BY, 1.5), 24, fstop=5.6, foco=(0.0, BY - 0.2, 1.5), roll=-2)


@shot("2E", 11.00, 12.10, "batia e gritava", "24 mm, de fora, três quartos pela direita, perto", "os punhos no aço, a fachada e o céu branco", "parada",
      "De fora, de três quartos pela direita: a dona da padaria e o rapaz do mercado gritam e batem os punhos no aço da porta, sob a placa ABRIGO, entre os pilares de concreto e os sacos de areia; atrás, os vizinhos que chegaram tarde e o céu branco. Não tem como achar que estão dentro (pedido de 25/10/2026).")
def p2E():
    p = rua3(aberta=0.0, carros=False, nevoa=False, branco=True)
    cogumelo(11.0)
    for nome, dx, rot, pose in (("pad", -0.34, 178, dict(ombro=(-96, -84), cotovelo=(-6, -20), abre=(-6, -6), tronco=-4, cabeca=-6)),
                                ("mer", 0.36, 182, dict(ombro=(-100, -92), cotovelo=(-6, -14), abre=(-6, -6), tronco=-4, cabeca=-6))):
        h = SA.ator3("padeira" if nome == "pad" else "mercado", nome, dx, BY - 0.52, rot=rot, pose=pose, rosto=dict(boca="o", lid=0.0))
        h.fecha_mao("F"); h.fecha_mao("B")
    for ch, nm, x, y, rot in (("viz1", "vizA", -1.0, BY - 1.25, 160), ("viz2", "vizB", -0.35, BY - 1.35, 176), ("viz3", "vizC", -1.7, BY - 1.6, 150), ("viz4", "vizD", 0.3, BY - 1.55, 186)):
        SA.ator3(ch, nm, x, y, rot=rot, pose=dict(ombro=(-120, -60), cotovelo=(-30, -50), abre=(8, 14), tronco=-6, cabeca=-8), rosto=dict(boca="o", lid=0.0))
    cam((1.75, BY - 2.05, 1.5), (-0.2, BY - 0.15, 1.6), 24, fstop=4.0, foco=(0.2, BY - 0.5, 1.5), roll=-2)


def vizinhos_vidro(wy, porta_x=0.0, s_porta=1.15):
    """a dona da padaria e o rapaz do mercado coladas no vidro (do lado de fora): o rosto da padeira no meio da janelinha, o do rapaz atrás, de boca aberta"""
    zj = 1.75 * s_porta
    out = []
    for nm, ch, dx, dy, ang, esc in (("padeira", "padeira", -0.12, 0.42, 6, 1.0), ("mercado", "mercado", 0.3, 0.95, -8, 1.0)):
        h = E3.faz(ch, nm + "_inv")
        h.raiz.location = (porta_x + dx, wy + dy, zj - 1.63 * esc + 0.03); h.raiz.rotation_euler.z = math.radians(ang)
        h.pose(ombro=(-100, -98), cotovelo=(-62, -58), abre=(22, 18), tronco=-8, cabeca=-4); h.rosto(boca="o", lid=0.0)
        out.append(h)
    return out


@shot("2F", 12.10, 13.30, "pedindo pra entrar", "50 mm, f/3,2, atrás do Zé, para a janelinha", "dos rostos no vidro", "parada",
      "Pela janelinha de vidro de verdade, a dona da padaria e o rapaz do mercado, de boca aberta e mãos coladas. Em primeiro plano, desfocada, a nuca do Zé, a um palmo da porta, de costas para eles.")
def p2F():
    p, wy = foyer3(aberta=0.0, fora="nenhum", vizinhos=False, lamp=False)
    vizinhos_vidro(wy)
    ze = SA.ator3("ze", "ze", 0.08, wy - 0.85, rot=180, pose=dict(ombro=(-6, 6), cotovelo=(-12, -12)))
    cam((0.32, wy - 1.6, 1.9), (0.0, wy - 0.15, 2.05), 50, fstop=3.2, foco=(0.0, wy - 0.15, 2.07))


@shot("2G", 13.30, 14.30, "Ele não abriu.", "85 mm, f/2, de frente, rosto do Zé", "os olhos", "parada",
      "O rosto dele, duro, a janelinha escura atrás: lá fora não tem mais ninguém. Os olhos baixam. É aqui que o filme faz a pergunta moral.")
def p2G():
    p, wy = foyer3(aberta=0.0, fora="nenhum", vizinhos=False, lamp=False)
    for o in ("fora_ceu", "fora_gl"):                                  # ninguém lá fora: a janelinha apaga
        bpy.data.objects[o].hide_render = True
    ze = SA.ator3("ze", "ze", 0.0, wy - 1.0, rot=0, pose=dict(ombro=(-4, 6), cotovelo=(-12, -12), cabeca=12), rosto=dict(boca="triste", lid=0.55))
    cam((0.06, wy - 2.75, 1.62), (0.0, wy - 1.0, 1.6), 85, fstop=2.0, foco=(0.0, wy - 1.12, 1.62))




def lata_deitada(nome, centro, yaw=0.0, s=1.4, cor="#8e5a3a", aberta=True, eixo_y=True):
    """lata vazia deitada no chão com o centro em 'centro' (a origem da lata é a base, então o deslocamento é refeito)"""
    r = O3.lata3d(nome, (0, 0, 0), s, cor, None, rot=0.0, aberta=aberta)
    r.rotation_euler = (math.radians(90 if eixo_y else 0), 0, math.radians(yaw))
    bpy.context.view_layer.update()
    c = Vector(centro) - r.matrix_world.to_3x3() @ Vector((0, 0, 0.05 * s))
    r.location = c
    return r


PILHA = (-2.45, 3.85)


def pilha_de_latas(n_base=6, n_meio=4):
    """as latas vazias do abrigo, empilhadas no chão (a comida acabou): fileira de baixo e fileira do meio, com a boca para todo lado"""
    rnd = random.Random(8); cores = ["#8e5a3a", "#59603f", "#4f6275", "#a89f86", "#7a3a30"]
    px, py = PILHA; d = 0.112
    for i in range(n_base):
        lata_deitada(f"vazia_b{i}", (px + (i - (n_base - 1) / 2) * d, py + rnd.uniform(-0.015, 0.015), 0.052), rnd.uniform(-12, 12), cor=cores[i % 5])
    for i in range(n_meio):
        lata_deitada(f"vazia_m{i}", (px + (i - (n_meio - 1) / 2) * d, py + rnd.uniform(-0.015, 0.015), 0.052 + 0.097), rnd.uniform(-14, 14), cor=cores[(i + 2) % 5])

# ---------------------------------------------------------------- o risco do dia no quadro, com quem risca (pedido de 25/10/2026:
# "quando ele riscar ali, ficou bugado": era só uma mão preta solta; agora é o personagem inteiro, de lado, com o braço alcançando o quadro)
RISCO = {}


def risco_dia(wy, d, centro=(-0.55, 1.22), s=1.25):
    """começo, fim, centro e comprimento (mundo) do risco do dia d (0, 1, ...) do quadro_giz3d, como o objeto desenha"""
    gx0, gz0 = -0.65 + 0.11, 0.46 - 0.11
    g, k = divmod(d, 5); col, lin = g % 8, g // 8
    x0 = gx0 + col * 0.145; z0 = gz0 - lin * 0.125
    yf = wy - 0.1 - 0.0265
    if k < 4:
        bx = centro[0] + s * (x0 + k * 0.026); zc = centro[1] + s * z0; h = 0.0425 * s
        return Vector((bx, yf, zc + h)), Vector((bx, yf, zc - h)), Vector((bx, yf, zc)), 2 * h, 0.0
    bx = centro[0] + s * (x0 + 0.039); zc = centro[1] + s * z0
    up = Vector((math.sin(math.radians(64)), 0, math.cos(math.radians(64)))); half = 0.0625 * s
    return Vector((bx, yf, zc)) - up * half, Vector((bx, yf, zc)) + up * half, Vector((bx, yf, zc)), 2 * half, 64.0


def quem_risca(wy, d, quem="eu", lado="F", dist=0.36):
    """põe o personagem de frente para o quadro, o ombro do braço que risca na altura do risco, o toco de giz no punho fechado (preso por
    'copiar rotação' a um eixo parado: ele aponta sempre para o quadro). Devolve o boneco e o risco"""
    a, b, c, L, ang = risco_dia(wy, d)
    RISCO.update(a=a, b=b, c=c, L=L, ang=ang, d=d, lado=lado)
    O3.caixa("risco_novo", (0.0106, 0.0075, L), O3.M(O3B.GIZ, "#c8c2ae", "#ffffff"), None, tuple(c), chanfro=0.002, contorno=0.0, rot=(0, ang if ang else 0.0, 0))
    H = SA.ator3(quem, quem, 0.0, wy - 0.1 - 0.0265 - dist, rot=180, pose=dict(ombro=(-6, -4), cotovelo=(-14, -16), abre=(6, 6), tronco=-5, cabeca=-4), rosto=dict(boca="reta", lid=0.2))
    bpy.context.view_layer.update()
    sh = H.ombro[lado].matrix_world.translation
    H.raiz.location.x += c.x - sh.x                              # o ombro do braço que risca fica na frente do risco
    bpy.context.view_layer.update()
    dg = Vector((0.0, 0.95, 0.31)).normalized()
    pega = H.fecha_mao(lado)
    giz = O3B.giz3d("giz_na_mao", (0, 0, 0), 1.0, pega)
    ori = empty("giz_ori", None, (0, 0, 0)); O3B.orienta(ori, dg)
    cr = giz.constraints.new("COPY_ROTATION"); cr.target = ori
    RISCO.update(dg=dg, off=IK.OFF_PEGA_F if lado == "F" else IK.OFF_PEGA_B, pega=pega)
    return H


def ponta_giz(p):
    """onde fica o 'pega' (o punho) para a ponta do giz tocar em p"""
    return p - RISCO["dg"] * 0.03

# ---------------------------------------------------------------- o abrigo por dentro (a sala principal)
def mao_em(nome, lado, ponta, direcao, pose="pinca", escala=1.0, roll=0.0, recuo=0.10, relogio=False, manga_comp=1.1):
    """mão 3D de quem conta no espaço do mundo: a ponta dos dedos cai em 'ponta' e os dedos apontam para 'direcao' (roll gira em volta do braço)"""
    d = Vector(direcao).normalized()
    piv = empty(nome + "_piv", None, tuple(Vector(ponta) - d * recuo * escala))
    piv.rotation_euler = (math.asin(max(-1.0, min(1.0, d.z))), 0, math.atan2(-d.x, d.y))
    m = O3.Mao3D(nome, lado, piv, (0, 0, 0), escala, relogio=relogio, manga_comp=manga_comp)      # manga comprida: o braço sai do quadro, não termina no ar
    m.raiz.rotation_euler = (0, math.radians(roll), 0)
    m.pose(pose)
    return m


def mao_braco(nome, lado, pulso, dir_braco, flexao=0.0, pose="pinca", escala=1.0, roll=0.0, relogio=False, manga_comp=1.1):
    """mão 3D com o PULSO em 'pulso', o antebraço apontando para 'dir_braco' (quase na horizontal, como num braço de verdade) e a mão dobrada 'flexao' graus
    em relação a ele (negativo = dedos para baixo). Devolve (mão, direção dos dedos no mundo)."""
    d = Vector(dir_braco).normalized()
    piv = empty(nome + "_piv", None, tuple(pulso))
    piv.rotation_euler = (math.asin(max(-1.0, min(1.0, d.z))), 0, math.atan2(-d.x, d.y))
    m = O3.Mao3D(nome, lado, piv, (0, 0, 0), escala, relogio=relogio, manga_comp=manga_comp)
    m.raiz.rotation_euler = (0, math.radians(roll), 0)
    m.pose(pose); m.gira(dobra=flexao)
    dedos = piv.rotation_euler.to_quaternion() @ Vector((0, math.cos(math.radians(flexao)), math.sin(math.radians(flexao))))
    return m, dedos


def mao_segura(nome, lado, ponta, dir_ferr, dir_braco, flexao=0.0, pose="pinca", escala=1.0, roll=0.0, aperto=0.045, relogio=False, manga_comp=1.1):
    """a mão pega uma ferramenta (giz, lápis) pelo ponto de aperto, a 'aperto' m atrás da ponta; o antebraço vem de 'dir_braco' (um vetor quase horizontal,
    como num braço de verdade) e o pulso dobra 'flexao'. A ferramenta é posta de acordo com dir_ferr (ela não precisa ficar na linha dos dedos).
    Devolve (mão, direção dos dedos)."""
    dC = Vector(dir_ferr).normalized()
    ap = Vector(ponta) - dC * aperto
    d = Vector(dir_braco).normalized()
    q = Euler((math.asin(max(-1.0, min(1.0, d.z))), 0, math.atan2(-d.x, d.y))).to_quaternion()
    dedos = q @ Vector((0, math.cos(math.radians(flexao)), math.sin(math.radians(flexao))))
    pulso = ap - dedos * 0.10 * escala
    return mao_braco(nome, lado, tuple(pulso), dir_braco, flexao=flexao, pose=pose, escala=escala, roll=roll, relogio=relogio, manga_comp=manga_comp)[0], dedos


GIZ_Z = 1.22                                                             # o quadro mais baixo: quem conta alcança o risco de cima sem se esticar (25/10)
LAMP_X = (-2.1, -0.6, 0.9)
LAMP_Z, LAMP_S = 2.1, 1.6                                               # lâmpadas um pouco maiores que o real (o desenho do canal exagera o que precisa ser lido)


def luzes(lamp=(1, 1, 1), y=2.6, z=None, pocas=True):
    """as três lâmpadas do fio (1 = acesa), com o brilho em volta e a poça de luz no chão"""
    for k, (x, ac) in enumerate(zip(LAMP_X, lamp)):
        O3.lampada3d(f"lamp{k}", (x, y, z or LAMP_Z), LAMP_S, acesa=bool(ac), fio=0.35)
        if ac and pocas:
            cena.ground_disc(f"poca{k}", 1.5, 1.1, cena.amat(f"poca{k}_m", "#d9b66a", 1.0, 0.2, ("radial", 1.2)), (x, y - 0.3, 0.006), n=40)


def abrigo3(nivel=1.0, lamp=(1, 1, 1), dia=1, galao=1.0, mesa=True, cadeiras=True, pal_nome="abrigo", wy=5.5, estante=True, giz=True, dim=False):
    """a sala principal em 3D: estante à esquerda, calendário de giz, galões, a porta no canto (a mesma porta3d), a mesa sob as lâmpadas"""
    p = pal(pal_nome)
    CA.sala3d(p, wy=wy, porta_x=2.9, porta_s=0.95)
    O3.porta3d("porta", (2.9, wy - 0.1, 0), 0.95, aberta=0.0)
    CA.fora_porta(p, 2.9, wy, vizinhos=False)
    if dim:                                                      # depois do dia 0 a luz de fora é cinza, não branca
        bpy.data.objects["fora_ceu"].hide_render = True; bpy.data.objects["fora_gl"].hide_render = True
    if estante:
        O3.estante3d("est", (-2.7, wy - 0.3, 0), 1.6, nivel=nivel)
    if giz:
        O3B.quadro_giz3d("giz", (-0.55, wy - 0.1, GIZ_Z), 1.25, dias=dia)
    O3.galao3d("galao_a", (-1.5, wy - 0.3, 0), 1.6, nivel=galao); O3.galao3d("galao_b", (-1.1, wy - 0.3, 0), 1.6, nivel=galao)
    if mesa:
        O3.mesa3d("mesa", (-0.6, 2.6, 0), (2.0, 0.9, 0.78))
        if cadeiras:
            O3.cadeira3d("cad1", (-1.85, 2.6, 0), rot=90); O3.cadeira3d("cad2", (0.65, 2.6, 0), rot=-90)
    luzes(lamp)
    return p, wy


# ====================================================================== 3. Os primeiros dias (14,30 a 19,74 s)
@shot("3A", 14.30, 15.50, "Lá dentro tinha", "24 mm, na altura dos olhos, parado", "a sala inteira", "parada",
      "O primeiro olhar para dentro: concreto verde-musgo, canos no teto, a estante cheia, o calendário de giz com um risco, os galões, a mesa posta sob as lâmpadas. Tudo no lugar: é o 'antes' que o filme vai desmanchar.")
def p3A():
    p, wy = abrigo3()
    cam((0.4, 0.3, 1.3), (-0.2, wy, 1.2), 22, fstop=8.0, foco=(0.0, 3.0, 1.0))


@shot("3B", 15.50, 16.25, "comida", "28 mm, de frente para a estante, f/11, deslizando de lado", "as prateleiras cheias de latas", "travelling lateral lento",
      "A estante inteira, de frente e nítida: três prateleiras, duas fileiras de latas em cada, cada lata com o seu rótulo. A câmera desliza devagar de lado e o paralaxe mostra a profundidade. É a lista do que mantém todo mundo vivo; o mesmo quadro volta no 4A, esvaziando.")
def p3B():
    p, wy = abrigo3()
    cam((-2.55, wy - 1.75, 0.95), (-2.7, wy - 0.3, 0.88), 28, fstop=11.0, foco=(-2.7, wy - 0.45, 0.88))


@shot("3C", 16.25, 16.80, "água", "35 mm, baixo, colado nos galões", "a água por dentro do plástico", "parada",
      "Colado nos dois galões: o plástico azul translúcido, a água balançando por dentro, bolhas subindo, a luz da lâmpada atravessando. O segundo item da lista.")
def p3C():
    p, wy = abrigo3()
    for g in ("galao_a", "galao_b"):                                  # bolhas dentro da água (o anim3 faz subir)
        r = bpy.data.objects[g]
        for k in range(6):
            O3.esfera(f"{g}_bolha{k}", 0.006, 0.006, 0.006, O3.vidro("#e8f4fa", 0.5, 0.7), r, (-0.06 + 0.024 * k, -0.04 + 0.016 * (k % 3), 0.03 + 0.03 * k), contorno=0.0, seg=10, an=6)
    cam((-1.12, wy - 1.2, 0.42), (-1.32, wy - 0.3, 0.3), 35, fstop=2.8, foco=(-1.3, wy - 0.4, 0.3))


@shot("3D", 16.80, 17.50, "e luz", "16 mm, de baixo para cima, câmera deitada (as três lâmpadas em fila vertical), parada", "as três lâmpadas", "parada",
      "As três lâmpadas acesas em fila, vistas de baixo com a câmera deitada, o brilho âmbar enchendo a tela. O terceiro item da lista. Elas voltam nos planos 6G, 7C e 8C, queimadas, só uma acesa.")
def p3D():
    p, wy = abrigo3()
    for k, x in enumerate(LAMP_X):                               # o brilho de cada lâmpada, grande, para a luz encher o quadro
        halo(f"brilho{k}", x, 2.55, LAMP_Z - 0.05, 0.9, "#ffd98a", 0.4)
    cam((-3.3, 2.5, 1.5), (0.9, 2.6, 2.0), 20, fstop=5.6, foco=(-0.6, 2.6, 2.0))       # de baixo, em perspectiva: as três lâmpadas penduradas do teto em fila (antes pareciam pontos na parede)


def giz_macro(wy, S, riscado_ate):
    """o giz tocando o quadro de perto: a mão pinça o giz (só os dedos entram no quadro) e o risco que ele vai deixando, do alto até a ponta"""
    dC = Vector((-0.10, 0.94, 0.32)).normalized()
    giz = O3B.giz3d("giz_na_mao", tuple(S - dC * 0.03), 1.0); O3B.orienta(giz, dC)
    mao_segura("mao_giz", "dir", tuple(S), dC, (-0.80, 0.50, 0.30), flexao=4.0, pose="pinca", escala=1.0, roll=-10, aperto=0.045, manga_comp=1.9)
    topo = S.z + 0.09
    O3.caixa("risco_novo", (0.0085, 0.006, max(0.01, topo - S.z)), O3.M(O3B.GIZ, "#c8c2ae", "#ffffff"), None, (S.x, S.y + 0.003, (topo + S.z) / 2), chanfro=0.002, contorno=0.0)


@shot("3E", 17.50, 18.50, "Por uns dias", "35 mm, de lado, na altura do peito, junto do quadro", "quem conta riscando o segundo dia", "parada",
      "De lado, junto ao quadro de giz: quem conta, de blusa vermelha, estica o braço, encosta o toco de giz no alto e puxa o segundo risco ao lado do primeiro, de cima para baixo. A câmera vê o corpo inteiro dele e o risco nascendo: o gesto que vai marcar o tempo do filme inteiro.")
def p3E():
    p, wy = abrigo3(dia=1, mesa=False)
    H = quem_risca(wy, 1, "eu", "F")
    c = RISCO["c"]
    cam((c.x + 1.15, wy - 2.35, 1.5), (c.x - 0.12, wy - 0.1, 1.5), 35, fstop=8.0, foco=(c.x - 0.05, wy - 0.4, 1.5))


@shot("3F", 18.50, 19.74, "a gente se sentiu seguro", "28 mm, f/2, baixa, junto da mesa", "da Pipoca para a família", "foco passa da Pipoca para eles",
      "Em primeiro plano, a Pipoca de suéter vermelho cheira um prato; atrás, desfocados, o Zé, a Lu e a Rita comem e riem. A única cena quente do filme e a única cor viva (o suéter).")
def p3F():
    p, wy = abrigo3(cadeiras=False)
    for k, x in enumerate((-1.15, -0.55, 0.05)):
        O3.prato3d(f"pr{k}", (x, 2.7, 0.78), 1.3, "cheio")
    # a Pipoca come no chão, na tigela dela, ao pé da mesa (cachorro em cima da mesa parecia bicho gigante)
    PA_pip = E3.pipoca("pipoca_inv", (0.12, 1.7, 0), 1.35, rot=160)
    O3.prato3d("tigela", (0.24, 2.05, 0.0), 1.0, "cheio")
    feliz = dict(boca="sorriso", lid=0.25)
    for ch, nm, x, y, rot in (("ze", "ze", -1.45, 3.55, 0), ("eu", "eu", -0.95, 3.55, 0), ("lu", "lu", -0.45, 3.6, 0), ("rita", "rita", 0.1, 3.5, 0)):     # o narrador ("eu", de vermelho) também está à mesa
        SA.ator3(ch, nm, x, y, rot=rot, pose=dict(ombro=(-14, -12), cotovelo=(-60, -62)), rosto=feliz)
    cam((1.05, 0.55, 0.62), (-0.45, 3.2, 0.8), 28, fstop=2.4, foco=(0.15, 1.85, 0.15))


# ====================================================================== 4. A comida acaba (19,74 a 26,22 s)
@shot("4A", 19.74, 21.00, "Só que a comida foi acabando", "22 mm, o mesmo quadro do plano 3B, parada", "as latas", "parada",
      "Mesmo enquadramento do 3B, nítido: a estante começa cheia e, em saltos, as latas somem de baixo para cima enquanto a luz pisca a cada salto, até sobrarem três lá no alto.")
def p4A():
    p, wy = abrigo3(nivel=1.0, dia=14, dim=True)              # nasce cheia como no 3B e vai esvaziando (o anim3 tira as latas, de baixo para cima)
    cam((-2.55, wy - 1.75, 0.95), (-2.7, wy - 0.3, 0.88), 28, fstop=11.0, foco=(-2.7, wy - 0.45, 0.88))      # o mesmo quadro do 3B: rima


def mesa_prato(nivel, dia):
    p, wy = abrigo3(dia=dia, cadeiras=False, dim=True)
    O3.prato3d("prato", (-0.3, 2.6, 0.78), 1.7, nivel)
    return p, wy


def prato_de_cima(nivel, ferramenta="garfo", comida_no_garfo=False, levanta=0.0):
    """POV de quem come, a uns 40° de cima: a mão direita leva o garfo (ou a colher) à comida com o antebraço quase na horizontal e o pulso dobrado, a esquerda
    descansa na mesa; os dois braços entram pelos cantos de baixo, com o cotovelo fora do quadro. levanta = quanto a ponta do garfo sobe do prato (m)"""
    p, wy = mesa_prato(nivel, 18)
    if nivel == "colher":                                              # a colher da mão é outra: a que repousa no prato sai de cena
        for o in bpy.data.objects:
            if o.name.startswith("prato_colher"):
                o.hide_render = True
    T = Vector((-0.30, 2.60, 0.81 + levanta))                         # a ponta do garfo (ou da concha)
    yaw = math.radians(24.0); pit_dedos = math.radians(-33.0); flex = -27.0
    pit_braco = pit_dedos - math.radians(flex)                         # o antebraço é mais reto do que os dedos
    dA = Vector((-math.sin(yaw) * math.cos(pit_braco), math.cos(yaw) * math.cos(pit_braco), math.sin(pit_braco)))
    comp = 0.336 if ferramenta == "garfo" else 0.346                   # do pulso à ponta da ferramenta
    # direção dos dedos = antebraço girado pela flexão; o pulso fica a 'comp' atrás da ponta
    dF = Vector((-math.sin(yaw) * math.cos(pit_dedos), math.cos(yaw) * math.cos(pit_dedos), math.sin(pit_dedos)))
    pulso = T - dF * comp
    m, dedos = mao_braco("mao_g", "dir", tuple(pulso), dA, flexao=flex, pose="pinca", escala=1.0, roll=-12)
    obj = O3B.garfo3d("garfo", (0, 0, 0), 1.9) if ferramenta == "garfo" else O3B.colher3d("colher", (0, 0, 0), 1.9)
    obj.location = pulso + dedos * 0.10 + dedos * 0.076                # origem da ferramenta: o aperto dos dedos fica 7,6 cm atrás dela
    O3B.orienta(obj, dedos)
    if comida_no_garfo:
        O3.esfera("bocado", 0.014, 0.014, 0.01, O3.M("#f6f1e2", "#d8d0bb"), None, tuple(T + Vector((0, 0.012, 0.012))), contorno=0.0012, seg=14, an=8)
    mao_braco("mao_p", "esq", (-0.46, 2.36, 0.82), (0.36, 0.93, -0.05), flexao=-8.0, pose="segura", escala=1.0)
    cam((-0.28, 1.86, 1.28), (-0.28, 2.56, 0.80), 31, fstop=5.6, foco=(-0.3, 2.6, 0.8))


@shot("4B", 21.00, 21.90, "A gente comia", "28 mm, de lado, na altura da mesa", "os quatro comendo", "parada",
      "Os quatro em volta da mesa, cada um com o seu prato: o Zé e a Lu nas pontas, a Rita e quem conta do outro lado. Os garfos sobem e descem devagar; os pratos ainda estão cheios.")
def p4B():
    p, wy = abrigo3(dia=10, cadeiras=True, dim=False)
    O3.cadeira3d("cad3", (-0.95, 3.4, 0), rot=0); O3.cadeira3d("cad4", (-0.2, 3.4, 0), rot=0)
    for nm, x, y in (("pz", -1.32, 2.6), ("pl", 0.12, 2.6), ("pr", -0.95, 2.86), ("pe", -0.2, 2.86)):
        O3.prato3d(nm, (x, y, 0.78), 1.15, "cheio")
    SA.sentado("ze", "ze", -1.85, 2.6, rot=90, ombro=(-38, -30), cotovelo=(-62, -70))
    SA.sentado("lu", "lu", 0.65, 2.6, rot=-90, ombro=(-38, -30), cotovelo=(-62, -70))
    SA.sentado("rita", "rita", -0.95, 3.4, rot=0, ombro=(-36, -30), cotovelo=(-64, -70), alt=0.42)
    SA.sentado("eu", "eu", -0.2, 3.4, rot=0, ombro=(-36, -30), cotovelo=(-64, -70))
    cam((-2.45, 0.95, 1.75), (-0.45, 3.0, 0.82), 24, fstop=5.6, foco=(-0.6, 2.8, 0.9))     # na diagonal, de cima: a mesa inteira e os quatro


@shot("4C", 21.90, 22.90, "um pouco menos", "31 mm, POV de quem come, a uns 35° de cima", "o prato e o garfo", "parada",
      "Agora nos olhos de quem conta: o prato pela metade. O garfo afunda no arroz, junta o que dá e sobe até a boca, saindo do quadro; a outra mão segura a borda do prato.")
def p4C():
    prato_de_cima("metade", "garfo", comida_no_garfo=True, levanta=0.0)


@shot("4D", 22.90, 23.90, "a cada dia", "35 mm, baixa, de frente, junto da estante vazia", "a última lata vazia na pilha", "parada",
      "A estante já está vazia. Uma pilha de latas vazias e abertas no chão; o Zé, de frente, olha dentro da última lata, vê que não tem nada, deixa ela cair na pilha, que rola e para, e baixa a cabeça. Não precisa de texto: a comida acabou.")
def p4D():
    p, wy = abrigo3(nivel=0.0, dia=21, dim=True, mesa=False)
    pilha_de_latas()
    H = SA.ator3("ze", "ze", -2.72, 4.45, rot=0, pose=dict(ombro=(-8, -30), cotovelo=(-20, -60), abre=(4, 6), tronco=-2, cabeca=10), rosto=dict(boca="triste", lid=0.45))
    pega = H.punho["B"]
    ultima = O3.lata3d("ultima", (0, 0, 0), 1.4, "#7a3a30", None, aberta=True)
    j = empty("ultima_mao", H.punho["B"], (0.0, -0.05, -0.05))       # onde a mão segura a lata
    cc = ultima.constraints.new("COPY_LOCATION"); cc.target = j
    cam((-2.25, 2.55, 0.95), (-2.62, 4.2, 0.7), 28, fstop=8.0, foco=(-2.6, 4.1, 0.9))


@shot("4E", 23.90, 25.00, "e já dava pra ver que não ia", "50 mm, por cima do ombro do Zé, f/2", "do caderno para os olhos", "parada",
      "O Zé de costas conta no caderno as últimas latas, o lápis parado. Ao fundo, desfocadas, a Lu e a Rita olham para ele. A conta é feita na frente de todos.")
def p4E():
    p, wy = abrigo3(nivel=0.15, dia=21, cadeiras=False, dim=True)
    ze = SA.ator3("ze", "ze", -0.25, 1.82, rot=180, pose=dict(ombro=(-48, -44), cotovelo=(-62, -66), abre=(4, 4), cabeca=14))
    bpy.context.view_layer.update()
    m = (ze.punho["F"].matrix_world.translation + ze.punho["B"].matrix_world.translation) / 2
    cad = O3B.caderno3d("caderno", (m.x, m.y + 0.04, m.z - 0.03), 1.4); cad.rotation_euler = (math.radians(-60), 0, 0)
    O3.cadeira3d("cad3", (-0.75, 3.4, 0), rot=0); O3.cadeira3d("cad4", (0.0, 3.4, 0), rot=0)       # sentadas atrás da mesa, nada atravessa o tampo
    SA.sentado("lu", "lu", -0.75, 3.4, rot=0, ombro=(-34, -34), cotovelo=(-70, -70)).rosto(boca="reta", lid=0.35)
    SA.sentado("rita", "rita", 0.0, 3.4, rot=0, ombro=(-34, -34), cotovelo=(-70, -70), alt=0.42).rosto(boca="reta", lid=0.3)
    cam((0.32, 1.02, 1.8), (-0.3, 3.4, 1.0), 40, fstop=2.2, foco=(m.x, m.y + 0.06, m.z))


@shot("4F", 25.00, 26.22, "pra todo mundo", "50 mm, de frente, a altura do peito", "os olhares", "parada",
      "A Lu olha para a Rita e a Rita olha para o chão: as duas já fizeram a mesma conta. Os dois olhares dizem quem é que vai sobrar.")
def p4F():
    p, wy = abrigo3(dia=21, cadeiras=False, dim=True)
    O3.cadeira3d("cad3", (-0.36, 3.42, 0), rot=0); O3.cadeira3d("cad4", (0.36, 3.42, 0), rot=0)
    SA.sentado("lu", "lu", -0.36, 3.42, rot=0, ombro=(-34, -34), cotovelo=(-70, -70), cabeca=-4, olha=-24).rosto(boca="reta", lid=0.4)
    SA.sentado("rita", "rita", 0.36, 3.42, rot=0, ombro=(-36, -36), cotovelo=(-72, -72), cabeca=16, olha=22, alt=0.42).rosto(boca="triste", lid=0.5)
    cam((0.0, 0.85, 1.22), (0.0, 3.4, 1.02), 50, fstop=2.2, foco=(0.0, 3.3, 1.1))


# ====================================================================== 5. O banheiro (26,22 a 31,74 s)
@shot("5A", 26.22, 27.50, "Na terceira semana", "40 mm, de lado pela esquerda, junto do quadro", "o traço que fecha o quarto grupo", "parada",
      "O quadro já está cheio de grupos de cinco; quem conta, de lado, alcança o quarto grupo e puxa o traço que corta os quatro riscos em pé: fecha a terceira semana de giz. O mesmo gesto do 3E, agora mais lento e visto pelo outro lado.")
def p5A():
    p, wy = abrigo3(dia=19, mesa=False, dim=True, nivel=0.1)
    H = quem_risca(wy, 19, "eu", "B")
    c = RISCO["c"]
    H.rosto(boca="reta", lid=0.45)
    cam((c.x - 1.2, wy - 2.35, 1.45), (c.x + 0.1, wy - 0.1, 1.5), 35, fstop=8.0, foco=(c.x + 0.05, wy - 0.4, 1.5))


def banheiro3(wy=3.4):
    p = pal("banheiro"); mundo(p)
    CA.sala3d(p, wy=wy, x0=-1.5, x1=1.5, h=2.6, y0=-6.0, seed=6)
    O3.lampada3d("lamp_b", (0.35, wy - 1.0, 1.9), 1.4, acesa=True, fio=0.3)
    halo("lamp_b_hl", 0.35, wy - 1.0, 1.95, 1.2, "#b4c27a", 0.3)
    return p, wy


@shot("5B", 27.50, 28.50, "o banheiro", "16 mm, rente ao chão", "a água que chega", "parada",
      "Rente às lajotas, por baixo da porta do banheiro, uma água escura avança em direção à lente. Duas moscas no ar. O mau cheiro ainda é só uma sombra.")
def p5B():
    p, wy = banheiro3()
    O3B.porta_comum3d("pbanho", (-0.45, wy - 0.18, 0.0), 1.15, abre=26)
    import cena as _c
    from heroi3d import plano as _pl
    _c.poly_mesh("agua_a", O3B.blob(-0.4, wy - 1.0, 0.5, 0.75, z=0.004, seed=2), _pl("#33381e"))      # a água sai de baixo da porta e abre em leque
    _c.poly_mesh("agua_b", O3B.blob(-0.3, 1.5, 0.85, 0.95, z=0.004, seed=4), _pl("#33381e"))
    _c.poly_mesh("agua_br", O3B.blob(-0.25, 1.7, 0.35, 0.4, z=0.006, seed=7), _pl("#4a5028"))
    O3B.moscas3d("mosca", (-0.2, wy - 1.0, 0.45), n=3, raio=0.25, s=1.8)
    cam((0.1, 1.2, 0.14), (-0.35, wy - 0.3, 0.5), 16, fstop=4.0, foco=(-0.2, wy - 1.0, 0.2))


@shot("5C", 28.50, 29.50, "entupiu", "28 mm, alta, de dentro do banheiro", "a bacia", "parada",
      "A privada de louça suja transbordando: a água escura passa da borda, escorre pelos lados e abre uma poça no chão de lajota. Uma lâmpada só, moscas em volta.")
def p5C():
    p, wy = banheiro3()
    O3B.privada3d("vaso", (0.1, wy - 0.4, 0.0), 1.6, transborda=1.0)
    O3B.moscas3d("mosca", (0.3, wy - 1.1, 1.0), n=4, raio=0.3, s=1.6)
    cam((0.3, 1.1, 1.5), (0.1, wy - 0.4, 0.5), 28, fstop=4.0, foco=(0.1, wy - 0.5, 0.55))


@shot("5D", 29.50, 30.60, "e o cheiro ruim tomou", "28 mm, o abrigo inteiro, parada", "os três tapando o nariz", "parada",
      "Uma névoa verde-doente entra pela sala: o Zé puxa a camisa até o nariz, a Lu tapa a boca, a Rita fica parada no meio, de olhos arregalados. A luz da sala fica verde e doente.")
def p5D():
    p, wy = abrigo3(dia=21, nivel=0.1, cadeiras=False, dim=True)
    S.neblina(p, 1.4, 0.22, cor="#8aa83e", z1=3.0); S.neblina(p, 3.4, 0.18, cor="#7a9a3a", z1=3.0)
    nariz = dict(ombro=(-70, 6), cotovelo=(-140, -14))
    SA.ator3("ze", "ze", -1.25, 2.9, rot=20, pose=dict(ombro=(-72, 6), cotovelo=(-138, -14), cabeca=6), rosto=dict(boca="reta", lid=0.62))
    SA.ator3("lu", "lu", 0.85, 2.5, rot=-25, pose=dict(ombro=(6, -72), cotovelo=(-14, -138), cabeca=6), rosto=dict(boca="reta", lid=0.62))
    SA.ator3("rita", "rita", -0.2, 3.4, rot=0, pose=dict(ombro=(-6, -6), cotovelo=(-12, -12)), rosto=dict(boca="o", lid=0.0))
    SA.ator3("eu", "eu", -0.8, 3.5, rot=-15, pose=dict(ombro=(-72, 6), cotovelo=(-138, -14), cabeca=6), rosto=dict(boca="reta", lid=0.62))      # o narrador também tapa o nariz
    cam((0.0, -0.8, 1.45), (-0.2, 3.0, 1.15), 28, fstop=4.0, foco=(-0.2, 2.8, 1.2))


@shot("5E", 30.60, 31.74, "conta do abrigo", "50 mm, f/2, a altura do rosto da Rita", "a Rita", "parada",
      "A Rita, a menor, esconde o rosto nos braços no canto, com as moscas girando em volta da lâmpada. O cheiro vira a primeira coisa que o abrigo tira dos três.")
def p5E():
    p, wy = abrigo3(dia=21, nivel=0.1, cadeiras=False, dim=True)
    S.neblina(p, 2.0, 0.2, cor="#8aa83e", z1=3.0)
    SA.ator3("rita", "rita", -0.3, 3.4, rot=0, pose=dict(ombro=(-78, -78), cotovelo=(-150, -150), abre=(-26, -26), cabeca=24), rosto=dict(boca="triste", lid=0.7))
    O3B.moscas3d("mosca", (-0.6, 2.9, 2.2), n=4, raio=0.35, s=1.6)
    cam((0.05, 1.7, 1.15), (-0.3, 3.4, 1.15), 50, fstop=2.0, foco=(-0.3, 3.4, 1.15))


# ====================================================================== 6. A Pipoca (31,74 a 41,94 s)
def gaiola_mesinha(vazia=False, com_pipoca=True):
    O3.mesa3d("mesa_g", (1.45, 4.3, 0), (1.05, 0.72, 0.5))
    O3.gaiola3d("gaiola", (1.45, 4.3, 0.5), 1.7, vazia=vazia)
    if com_pipoca and not vazia:
        E3.pipoca("pip_inv", (1.53, 4.27, 0.64), 1.35, rot=-10)


@shot("6A", 31.74, 32.60, "Aí a Pipoca", "50 mm, de frente para a gaiola, parada", "a gaiola", "parada",
      "A Pipoca roendo feno na gaiola, de suéter vermelho de tricô: o único vermelho vivo do abrigo. O mesmo quadro volta no 6D, com a gaiola vazia.")
def p6A():
    p, wy = abrigo3(dia=60, mesa=False, dim=True, nivel=0.1)
    gaiola_mesinha()
    cam((1.45, 2.55, 0.98), (1.45, 4.3, 0.85), 50, fstop=2.8, foco=(1.4, 4.2, 0.85))


@shot("6B", 32.60, 33.50, "a nossa porquinha-da-índia", "85 mm, f/1,8, no nível da Pipoca", "os olhos dela", "parada",
      "O rosto dela de perto: o focinho, as orelhas, os olhos pretos. É o plano que faz a gente gostar dela antes de ela sumir.")
def p6B():
    p, wy = abrigo3(dia=60, mesa=False, dim=True, nivel=0.1)
    gaiola_mesinha()
    for o in bpy.data.objects:                                       # só no close: tira as grades da frente para ver o rosto
        if o.name.startswith("gaiola_b") and o.name.endswith("-0.19"):
            o.hide_render = True
    cam((1.36, 3.2, 0.82), (1.5, 4.2, 0.8), 85, fstop=1.8, foco=(1.51, 4.02, 0.8))     # segue a Pipoca, que saiu de dentro da casinha


@shot("6C", 33.50, 34.40, "(a Rita com ela no colo)", "50 mm, a altura do peito da Rita", "a Rita e a Pipoca", "parada",
      "A Rita, a menor, com a Pipoca nos braços, apertada contra o peito. Mostra de quem era o bichinho e o quanto ela gostava dele.")
def p6C():
    p, wy = abrigo3(dia=60, mesa=False, dim=True, nivel=0.1)
    ri = SA.ator3("rita", "rita", 0.5, 3.3, rot=0, pose=dict(ombro=(-38, -38), cotovelo=(-72, -72), abre=(-10, -10), cabeca=10), rosto=dict(boca="sorriso", lid=0.35))
    bpy.context.view_layer.update()
    m = (ri.punho["F"].matrix_world.translation + ri.punho["B"].matrix_world.translation) / 2
    E3.pipoca("pip_inv", (m.x, m.y - 0.03, m.z - 0.04), 0.95, rot=0)
    cam((0.5, 1.7, 1.0), (0.5, 3.3, 0.98), 50, fstop=2.2, foco=(0.5, 3.2, 0.98))


@shot("6D", 34.40, 35.50, "sumiu", "50 mm, o mesmo quadro do 6A, parada", "a gaiola vazia", "parada",
      "A mesma gaiola, no mesmo lugar: a portinha aberta, o feno revirado, o suéter vermelho dobrado no fundo. Ela sumiu e ficou só a roupa.")
def p6D():
    p, wy = abrigo3(dia=60, mesa=False, dim=True, nivel=0.1)
    gaiola_mesinha(vazia=True)
    cam((1.45, 2.55, 0.98), (1.45, 4.3, 0.85), 50, fstop=2.8, foco=(1.4, 4.2, 0.85))


@shot("6E", 35.50, 36.50, "Ninguém falou nada", "35 mm, baixa, na frente da portinha aberta", "a mão tirando o suéter da gaiola", "parada",
      "A mão de quem conta entra pela portinha aberta da gaiola vazia, pega o suéter dobrado pela gola e puxa para fora: ele se abre no ar, pendurado, e dá para ver que é uma roupinha de bicho, com as duas manguinhas. Ninguém diz nada.")
def p6E():
    p, wy = abrigo3(dia=60, mesa=False, dim=True, nivel=0.1)
    O3.mesa3d("mesa_g", (1.45, 4.3, 0), (1.05, 0.72, 0.5))
    O3.gaiola3d("gaiola", (1.45, 4.3, 0.5), 1.7, vazia=True)
    O3B.sueter_pendurado3d("sueter_pend", 1.5).scale = (0.0001,) * 3       # aparece quando a mão puxa
    alvo = Vector((1.586, 4.25, 0.67)); d = Vector((-0.36, 0.72, -0.30)).normalized()
    mao_braco("mao_su", "dir", tuple(alvo - d * 0.1), tuple(d), flexao=-8.0, pose="aberta", escala=1.0, roll=0, manga_comp=1.9)
    cam((0.95, 3.05, 1.05), (1.58, 4.15, 0.8), 28, fstop=4.0, foco=(1.56, 4.05, 0.75))


@shot("6F", 36.50, 37.50, "Mas, naquela", "85 mm, f/2, de frente, rosto do Zé", "os olhos desviando", "parada",
      "O Zé desvia o olhar da câmera, para o lado, sem saber onde pôr os olhos. A culpa ainda não foi dita, mas já está no rosto.")
def p6F():
    p, wy = abrigo3(dia=60, mesa=False, dim=True, nivel=0.1)
    SA.ator3("ze", "ze", -0.2, 3.0, rot=0, pose=dict(ombro=(-4, 6), cotovelo=(-12, -12), cabeca=6, olha=38), rosto=dict(boca="reta", lid=0.5))
    cam((0.1, 1.15, 1.62), (-0.2, 3.0, 1.6), 85, fstop=2.0, foco=(-0.2, 2.95, 1.6))


PRATO_ZE, PRATO_LU, PRATO_RITA, PRATO_EU = (-1.3, 2.6), (0.12, 2.6), (-0.6, 2.9), (-1.12, 2.93)        # onde cada um come (na mesa, nunca na borda)


def jantar_set(pal_nome="escuro"):
    p, wy = abrigo3(pal_nome=pal_nome, lamp=(0, 1, 0), dia=60, nivel=0.1, dim=True, cadeiras=False)
    O3.cadeira3d("cad1", (-1.75, 2.6, 0), rot=90); O3.cadeira3d("cad2", (0.65, 2.6, 0), rot=-90); O3.cadeira3d("cad3", (-0.6, 3.28, 0), rot=0); O3.cadeira3d("cad4", (-1.12, 3.28, 0), rot=0)
    return p, wy


@shot("6G", 37.50, 38.40, "noite", "28 mm, do canto, câmera parada", "a lâmpada única", "parada",
      "A noite no abrigo: uma lâmpada só acesa sobre a mesa, os três sentados nas pontas, sombra grande por todo lado. O jantar vai ser servido.")
def p6G():
    p, wy = jantar_set()
    for k, (x, y) in enumerate((PRATO_ZE, PRATO_RITA, PRATO_LU, PRATO_EU)):
        O3.prato3d(f"pr{k}", (x, y, 0.78), 1.2, "carne")
    SA.sentado("ze", "ze", -1.75, 2.6, rot=90, ombro=(-30, -28), cotovelo=(-70, -72))
    SA.sentado("lu", "lu", 0.65, 2.6, rot=-90, ombro=(-30, -28), cotovelo=(-70, -72))
    SA.sentado("rita", "rita", -0.6, 3.28, rot=0, ombro=(-30, -28), cotovelo=(-70, -72), alt=0.42)
    SA.sentado("eu", "eu", -1.12, 3.28, rot=0, ombro=(-30, -28), cotovelo=(-70, -72))                          # o narrador, de vermelho, também janta
    cam((1.7, 0.7, 1.45), (-0.7, 3.0, 0.95), 28, fstop=8.0, foco=(-0.6, 2.8, 0.9))


@shot("6H", 38.40, 39.60, "tinha carne no jantar", "85 mm, f/1,8, quase em cima do prato", "a carne", "parada",
      "Um pedaço de carne escura soltando vapor sob a única lâmpada. O garfo entra e para no ar. O filme não diz de quê; só mostra.")
def p6H():
    p, wy = jantar_set()
    O3.prato3d("prato_c", (-0.1, 2.6, 0.78), 2.2, "carne")
    O3B.vapor3d("vapor", (-0.12, 2.6, 0.86), n=3, alt=0.12, s=0.7)
    O3B.garfo3d("garfo", (0.1, 2.5, 0.95), 2.2, None, rot=(0, 30, 20))
    cam((-0.05, 1.55, 1.1), (-0.1, 2.6, 0.84), 70, fstop=2.0, foco=(-0.1, 2.6, 0.84))


@shot("6I", 39.60, 40.70, "e ninguém teve coragem", "50 mm, à altura do rosto, de frente", "a Lu", "parada",
      "A Lu come de cabeça baixa, sem olhar para ninguém. O rosto escondido pela cabeça inclinada.")
def p6I():
    p, wy = jantar_set()
    O3.prato3d("prato_l", (PRATO_LU[0], PRATO_LU[1], 0.78), 1.3, "carne")
    SA.sentado("lu", "lu", 0.65, 2.6, rot=-90, ombro=(-34, -30), cotovelo=(-76, -78), cabeca=34)
    cam((-0.55, 2.35, 1.2), (0.65, 2.6, 1.1), 50, fstop=2.0, foco=(0.62, 2.6, 1.15))


@shot("6J", 40.70, 41.70, "de perguntar", "35 mm, de lado, na altura do rosto", "o Zé", "parada",
      "O Zé come de cabeça baixa também. Um por vez, os três se fecham. A câmera de lado mostra que ninguém se olha.")
def p6J():
    p, wy = jantar_set()
    O3.prato3d("prato_z", (PRATO_ZE[0], PRATO_ZE[1], 0.78), 1.3, "carne")
    SA.sentado("ze", "ze", -1.75, 2.6, rot=90, ombro=(-34, -30), cotovelo=(-76, -78), cabeca=34)
    cam((-0.7, 2.0, 1.2), (-1.75, 2.6, 1.05), 35, fstop=2.2, foco=(-1.75, 2.6, 1.15))


@shot("6K", 41.70, 42.60, "de quê", "85 mm, f/2, de frente, rosto da Rita", "a lágrima", "parada",
      "A Rita empurra o prato para longe e chora sem som: uma lágrima desce. É o único rosto que reage; os outros fingem.")
def p6K():
    p, wy = jantar_set()
    O3.prato3d("prato_r", (PRATO_RITA[0], PRATO_RITA[1], 0.78), 1.3, "carne")
    SA.sentado("rita", "rita", -0.6, 3.28, rot=0, ombro=(-42, -40), cotovelo=(-30, -34), cabeca=8, alt=0.42)
    O3B.lagrima3d("lagr0", (-0.545, 3.12, 1.0)); O3B.lagrima3d("lagr1", (-0.56, 3.12, 0.95), 0.8)
    cam((-0.6, 1.75, 1.38), (-0.6, 3.28, 0.9), 55, fstop=2.2, foco=(-0.6, 3.2, 0.92))


# ====================================================================== 7. Os meses (41,94 a 50,12 s)
@shot("7A", 42.60, 43.80, "Os meses foram passando", "24 mm, de frente para o calendário, parada", "os riscos de giz", "parada",
      "O quadro de giz já está cheio (200 dias, riscos de cinco em cinco, linha atrás de linha) e um galão quase vazio ao pé da parede. É a passagem do tempo contada por objetos, sem texto.")
def p7A():
    p, wy = abrigo3(pal_nome="escuro", lamp=(0, 0, 1), dia=200, nivel=0.0, galao=0.15, dim=True, mesa=True)
    cam((-0.5, 3.6, 1.35), (-0.55, wy, GIZ_Z), 28, fstop=8.0, foco=(-0.55, wy - 0.2, GIZ_Z))


def cctv_sala(modo):
    """a sala vista do alto de um canto, para a câmera de segurança: CAM 01 (os meses, cada um no seu canto) e CAM 02 (a briga)"""
    p = pal("escuro"); wy = 5.5
    CA.sala3d(p, wy=wy)
    O3.estante3d("est", (-2.7, wy - 0.3, 0), 1.6, nivel=0.15)
    O3.galao3d("gal1", (-1.5, wy - 0.3, 0), 1.6, nivel=0.3); O3.galao3d("gal2", (-1.1, wy - 0.3, 0), 1.6, nivel=0.0)
    O3.mesa3d("mesa", (-0.6, 2.6, 0), (2.0, 0.9, 0.78))
    O3.cadeira3d("cad1", (-1.85, 2.6, 0), rot=90); O3.cadeira3d("cad2", (0.65, 2.6, 0), rot=-90)
    O3.cama3d("cama", (2.2, 4.3, 0), dobrada=False)
    if bpy.data.objects.get("caixote2"):                            # o caixote de cima ficava dentro da cama
        bpy.data.objects["caixote2"].hide_render = True; bpy.data.objects["caixote2"].scale = (0.0001,) * 3
    if modo == "cctv3":                                             # a Lu continua na cama, já esqueleto
        O3B.esqueleto_deitado("esq_lu", (2.92, 4.3), rumo=-90, z=0.6, cabeca=-8, queixo=18, ombro=(-8, -12), abre=(10, 14), cotovelo=(-30, -20))
    for kk in range(3):
        O3.caixa(f"cx{kk}", (0.6, 0.45, 0.4), O3.M("#6b5a3e", "#4e4130", "#a8916a"), None, (2.9, 0.6 + 0.5 * kk, 0.2 + 0.4 * (kk == 1)), chanfro=0.02)
    for kk, (x, ac) in enumerate(((-0.6, True), (0.9, False), (-2.1, False))):
        O3.lampada3d(f"lamp{kk}", (x, 2.6, LAMP_Z), LAMP_S, acesa=ac, fio=0.35)
    cena.ground_disc("poca_luz", 2.0, 1.6, cena.amat("poca_luz_m", "#d9b66a", 1.0, 0.22, ("radial", 1.2)), (-0.6, 2.6, 0.006), n=40)
    if modo == "cctv1":
        z = SA.sentado("ze", "ze", -1.78, 2.6, rot=90, ombro=(-30, -28), cotovelo=(-70, -72)); z.rosto(boca="reta", lid=0.75); z.cabeca.rotation_euler = (math.radians(22), 0, 0)
        SA.ator3("rita", "rita", -2.9, 3.6, rot=60, pose=dict(quadril=(-115, -115), joelho=(140, 140), ombro=(-60, -60), cotovelo=(-80, -80), alt=0.28, cabeca=20), rosto=dict(lid=0.8))
        lu = SA.ator3("lu_fraca", "lu", 2.3, 4.3, rot=0, pose=dict(ombro=(-6, 4), cotovelo=(-10, -10)), rosto=dict(lid=0.85))
        lu.raiz.rotation_euler = (math.radians(-90), 0, math.radians(-90)); lu.raiz.location = (1.35, 4.3, 0.6)
        SA.ator3("eu", "eu", -0.5, 5.0, rot=10, pose=dict(quadril=(-115, -115), joelho=(140, 140), ombro=(-60, -60), cotovelo=(-80, -80), alt=0.28, cabeca=24), rosto=dict(lid=0.8))     # o narrador, no canto dele
        return cam((-3.05, 1.25, 2.5), (-0.35, 3.95, 0.65), 16, fstop=16.0)
    if modo == "cctv3":
        O3B.jaqueta3d("jaq", (0.88, 2.6, 0.9), 1.15).rotation_euler.z = math.radians(-90)
        for k, (x, y, rot) in enumerate(((-0.9, 2.5, 20), (-0.5, 2.65, 70), (0.05, 2.55, 100), (0.3, 2.7, 160))):
            O3B.carta3d(f"carta{k}", (x, y, 0.79), 1.6, verso=(k % 2 == 0), rot=(0, 0, rot))
        z = SA.sentado("ze", "ze", -1.67, 2.6, rot=90, ombro=(-52, -44), cotovelo=(-48, -56)); z.rosto(boca="sorriso", lid=0.5)
        SA.ator3("rita", "rita", -2.9, 4.7, rot=40, pose=dict(quadril=(-115, -115), joelho=(140, 140), ombro=(-60, -60), cotovelo=(-80, -80), alt=0.28, cabeca=25), rosto=dict(lid=0.8))
        SA.ator3("eu", "eu", -0.5, 5.0, rot=10, pose=dict(quadril=(-115, -115), joelho=(140, 140), ombro=(-60, -60), cotovelo=(-80, -80), alt=0.28, cabeca=24), rosto=dict(lid=0.8))     # o narrador, no canto dele
        return cam((2.2, 1.3, 2.3), (-0.9, 2.9, 0.9), 20, fstop=16.0)
    # frente a frente, a 80 cm um do outro, no meio da sala (pedido de 25/10: "estão brigando, mas cada um está num canto")
    z = SA.ator3("ze", "ze", 0.35, 1.75, rot=95, pose=dict(ombro=(-70, 10), cotovelo=(-40, -12), abre=(20, 6), tronco=-8, cabeca=-4), rosto=dict(boca="o", lid=0.2))
    SA.ator3("lu_fraca", "lu", 1.15, 1.8, rot=-85, pose=dict(ombro=(-35, -40), cotovelo=(-60, -70), abre=(12, 12), tronco=-4), rosto=dict(boca="o", lid=0.3))
    SA.ator3("rita", "rita", -2.9, 4.7, rot=40, pose=dict(quadril=(-115, -115), joelho=(140, 140), ombro=(-60, -60), cotovelo=(-80, -80), alt=0.28, cabeca=25), rosto=dict(lid=0.8))
    SA.sentado("eu", "eu", 0.65, 2.6, rot=-90, ombro=(-50, -50), cotovelo=(-110, -110), cabeca=36)                 # o narrador na mesa, de cabeça baixa, tentando não ouvir a briga
    return cam((2.25, 1.05, 2.5), (-0.65, 3.45, 0.95), 16, fstop=16.0)


@shot("7B", 43.80, 45.10, "e todo mundo ficou calado", "16 mm, câmera de segurança CAM 01, do alto de um canto", "a sala inteira", "parada (câmera de segurança)",
      "A câmera de segurança vê os três: o Zé na mesa, a Rita encolhida no chão, a Lu na cama. Cada um no seu canto, ninguém olha ninguém. É a prova de que o silêncio virou o jeito de viver.",
      cctv=dict(cam="CAM 01", dia=200, hora="02:41:13"))
def p7B():
    cctv_sala("cctv1")


@shot("7C", 45.10, 46.30, "O Zé e a Lu viviam", "35 mm, de perfil, frente a frente", "os dois rostos", "câmera na mão leve",
      "O Zé e a Lu frente a frente, de perfil, com a lâmpada balançando entre os dois. Os gestos são duros; o mais velho aponta o dedo. Plano de dois, sem ninguém mais.")
def p7C():
    p, wy = abrigo3(pal_nome="escuro", lamp=(0, 1, 0), dia=200, nivel=0.0, galao=0.1, dim=True, mesa=False)
    SA.ator3("ze", "ze", -0.5, 3.4, rot=90, pose=dict(ombro=(-70, 8), cotovelo=(-40, -12), abre=(8, 8), tronco=-6), rosto=dict(boca="o", lid=0.3))
    SA.ator3("lu_fraca", "lu", 0.55, 3.4, rot=-90, pose=dict(ombro=(-30, -36), cotovelo=(-60, -64), abre=(8, 8), tronco=-4), rosto=dict(boca="o", lid=0.35))
    SA.ator3("eu", "eu", 1.15, 4.75, rot=170, pose=dict(quadril=(-115, -115), joelho=(140, 140), ombro=(-60, -60), cotovelo=(-80, -80), alt=0.28, cabeca=26), rosto=dict(lid=0.8))   # o narrador, calado, no canto
    cam((0.05, 0.9, 1.5), (0.0, 3.4, 1.62), 28, fstop=2.8, foco=(0.0, 3.4, 1.62), roll=1.5)


@shot("7D", 46.30, 47.50, "brigando", "16 mm, câmera de segurança CAM 02, do outro canto", "os dois em pé", "parada (câmera de segurança)",
      "O mesmo abrigo pelo outro canto: o Zé e a Lu de pé, frente a frente e perto um do outro, discutindo sem som; a Rita encolhida ao fundo. A câmera de segurança mostra a briga de cima.",
      cctv=dict(cam="CAM 02", dia=241, hora="21:07:55"))
def p7D():
    cctv_sala("cctv2")


def cama_cena(vazia=False, familia=True):
    """a cama da Lu. Antes ela só 'desaparecia'; agora o Zé e a Rita estão ajoelhados ao lado dela (pedido de 25/10: "tem que ser mais emocionante,
    a família junto"), o Zé de mão dada, a Rita com a mão no ombro dela. vazia = meses depois: no lugar da Lu o esqueleto, e a cadeira com a jaqueta dela"""
    p = pal("escuro"); wy = 5.5
    CA.sala3d(p, wy=wy)
    O3B.quadro_giz3d("giz_a", (-1.9, wy - 0.1, 1.55), 1.5, dias=200)
    luzes((0, 1, 0), pocas=True)
    O3.cama3d("cama", (1.3, 4.1, 0), manta="#6e6a4a", dobrada=False)
    O3.cadeira3d("cad", (0.55, 3.25, 0), rot=180)
    if bpy.data.objects.get("caixote2"):
        bpy.data.objects["caixote2"].hide_render = True; bpy.data.objects["caixote2"].scale = (0.0001,) * 3
    if vazia:                                                       # no lugar dela fica o esqueleto, deitado, a manta por cima das pernas
        jq = O3B.jaqueta3d("jaq", (0.55, 3.06, 0.86), 1.15); jq.rotation_euler.z = math.radians(180)
        O3B.esqueleto_deitado("esq_lu", (2.02, 4.1), rumo=-90, z=0.6, cabeca=-8, queixo=18, ombro=(-8, -12), abre=(10, 14), cotovelo=(-30, -20))
        return p, wy
    lu = SA.ator3("lu_fraca", "lu", 2.0, 4.1, rot=0, pose=dict(ombro=(-6, 4), cotovelo=(-10, -10)), rosto=dict(boca="reta", lid=0.85))
    lu.raiz.rotation_euler = (math.radians(-90), 0, math.radians(-90)); lu.raiz.location = (0.6, 4.1, 0.6)
    if familia:
        joelhos = dict(quadril=(0, 0), joelho=(88, 88), tornozelo=(-20, -20), alt=0.45)
        SA.ator3("ze", "ze", 1.45, 3.5, rot=180, pose=dict(joelhos, ombro=(-30, -30), cotovelo=(-40, -40), abre=(8, 8), tronco=10, cabeca=18), rosto=dict(boca="triste", lid=0.55))
        SA.ator3("rita", "rita", 1.97, 3.57, rot=180, pose=dict(joelhos, ombro=(-30, -30), cotovelo=(-40, -40), abre=(8, 8), tronco=20, cabeca=20), rosto=dict(boca="triste", lid=0.5))
        SA.ator3("eu", "eu", 2.62, 3.52, rot=180, pose=dict(joelhos, ombro=(-20, -20), cotovelo=(-30, -30), abre=(8, 8), tronco=14, cabeca=26), rosto=dict(boca="triste", lid=0.55))     # o narrador ajoelhado, na família
    return p, wy


@shot("7E", 47.50, 48.60, "mas a Lu foi ficando", "24 mm, do lado da parede, na altura da cama, o dolly entra", "a Lu e a família junto dela", "dolly lento",
      "Do outro lado da cama: a Lu deitada, magra, a cabeça no travesseiro; o Zé e a Rita ajoelhados ao lado dela, de frente para a câmera, ele segurando a mão dela, a Rita com a mão no seu ombro, os dois de cabeça baixa, chorando sem som. Este quadro volta no 7G, sem ninguém.")
def p7E():
    cama_cena(False)
    cam((1.0, 5.05, 1.35), (1.85, 3.85, 0.7), 24, fstop=4.0, foco=(1.75, 4.0, 0.7))


@shot("7F", 48.60, 49.50, "fraca e um dia", "50 mm, f/2, de cima, do pé da cama, no rosto da Lu, a família ao lado", "os olhos dela fechando", "parada",
      "O rosto da Lu no travesseiro, visto de cima, os olhos fechando devagar; ao fundo, desfocadas, as mãos do Zé e da Rita nela. O corpo desistindo diante de quem fica.")
def p7F():
    cama_cena(False)
    cam((1.2, 4.12, 1.3), (2.12, 4.1, 0.66), 50, fstop=2.0, foco=(2.1, 4.1, 0.68))


@shot("7G", 49.50, 50.50, "morreu.", "24 mm, o mesmo quadro do 7E, parada", "o esqueleto na cama e ninguém", "parada",
      "O mesmo quadro do 7E, meses depois: no lugar dela, o esqueleto deitado na mesma posição, a cabeça no travesseiro e a manta por cima das pernas; ninguém ao lado, só a cadeira com a jaqueta dela.")
def p7G():
    cama_cena(True)
    cam((1.0, 5.05, 1.35), (1.85, 3.85, 0.7), 24, fstop=4.0, foco=(1.75, 4.0, 0.7))


# ====================================================================== 8. O baralho (50,12 a 54,20 s)
@shot("8A", 50.50, 51.70, "Agora o Zé passa o dia", "28 mm, de cima, a pino, câmera deitada", "as cartas na mesa", "parada",
      "A mesa vista do teto: de um lado o Zé sentado com as cartas, do outro a cadeira vazia com a jaqueta jeans da Lu no encosto. As cartas já estão dadas para os dois lados.")
def p8A():
    p = pal("escuro"); wy = 5.5
    CA.sala3d(p, wy=wy)
    O3.mesa3d("mesa8", (0.2, 3.0, 0), (2.2, 1.0, 0.78))
    O3.cadeira3d("cad_ze", (-1.1, 3.0, 0), rot=90); O3.cadeira3d("cad_lu", (1.5, 3.0, 0), rot=-90)
    O3B.jaqueta3d("jaq", (1.74, 3.0, 0.9), 1.15).rotation_euler.z = math.radians(-90)
    SA.sentado("ze", "ze", -1.02, 3.0, rot=90, ombro=(-62, -58), cotovelo=(-38, -40))
    for k, (x, y, rot) in enumerate(((-0.55, 2.85, 12), (-0.5, 3.1, -20), (0.85, 2.85, 170), (0.92, 3.1, 195), (0.2, 3.0, 60))):
        O3B.carta3d(f"carta{k}", (x, y, 0.79), 2.4, verso=(k % 2 == 0), rot=(0, 0, rot))
    cam((-0.05, 2.95, 2.8), (-0.05, 3.0, 0.78), 28, fstop=8.0, foco=(-0.05, 3.0, 0.8), roll=90)


@shot("8B", 51.70, 52.90, "jogando baralho sozinho", "16 mm, câmera de segurança CAM 02, do canto", "o Zé sozinho", "parada (câmera de segurança)",
      "A câmera de segurança vê o que ninguém devia ver: o Zé joga cartas sozinho e dá uma para a cadeira vazia da Lu, com a jaqueta no encosto. A cama dela, arrumada, ao fundo. Dia 300.",
      cctv=dict(cam="CAM 02", dia=300, hora="16:22:40"))
def p8B():
    cctv_sala("cctv3")


@shot("8C", 52.90, 54.20, "pelos dois lados", "45 mm, f/2, por cima do encosto da cadeira da Lu", "o Zé sorrindo para ela", "parada",
      "Por trás da cadeira da Lu: a jaqueta dela desfocada em primeiro plano e, do outro lado da mesa, o Zé sorrindo de leve e pondo a carta para ela. Ele fala baixo com a jaqueta.")
def p8C():
    p = pal("escuro"); wy = 5.5
    CA.sala3d(p, wy=wy)
    O3B.quadro_giz3d("giz_a", (-1.2, wy - 0.1, 1.6), 1.5, dias=200)
    luzes((0, 1, 0))
    O3.mesa3d("mesa", (-0.6, 2.6, 0), (2.0, 0.9, 0.78))
    O3.cadeira3d("cad_ze", (-1.75, 2.6, 0), rot=90); O3.cadeira3d("cad_lu", (0.65, 2.6, 0), rot=-90)
    jq = O3B.jaqueta3d("jaq", (0.88, 2.6, 0.9), 1.15); jq.rotation_euler.z = math.radians(-90)
    SA.sentado("ze", "ze", -1.67, 2.6, rot=90, ombro=(-52, -44), cotovelo=(-48, -56), cabeca=6).rosto(boca="sorriso", lid=0.5)
    for k, (x, y, rot) in enumerate(((-0.9, 2.5, 20), (-0.45, 2.65, 70), (0.05, 2.55, 100))):
        O3B.carta3d(f"carta{k}", (x, y, 0.79), 1.8, verso=(k % 2 == 0), rot=(0, 0, rot))
    cam((1.45, 2.95, 1.2), (-1.7, 2.6, 1.1), 45, fstop=2.0, foco=(-1.7, 2.6, 1.15))


# ====================================================================== 9. A porta de novo (53,94 a 58,98 s)
def agua_de_nivel(g, phi=None, nome=None):
    """a água de um galão inclinado fica na horizontal (antes ela girava junto com o plástico e grudava em cima): troca a caixa de água por
    meio volume cortado por um plano de nível, no espaço do galão. phi = inclinação em graus (por padrão a do galão agora): dá para criar uma água
    para cada fase de um movimento e ligar uma de cada vez"""
    import bmesh
    from heroi3d import _objeto
    bpy.context.view_layer.update()
    velha = bpy.data.objects.get(g.name + "_agua")
    if velha is not None:
        velha.hide_render = True
    if phi is None:
        baixo = (g.matrix_world.to_3x3().inverted() @ Vector((0, 0, -1))).normalized()
    else:
        baixo = (Matrix.Rotation(math.radians(phi), 3, "X").inverted() @ Vector((0, 0, -1))).normalized()
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0); bmesh.ops.scale(bm, vec=(0.17, 0.13, 0.25), verts=bm.verts)
    bmesh.ops.translate(bm, vec=(0, 0, 0.14), verts=bm.verts)
    geo = list(bm.verts) + list(bm.edges) + list(bm.faces)
    res = bmesh.ops.bisect_plane(bm, geom=geo, plane_co=(0, 0, 0.14), plane_no=tuple(-baixo), clear_outer=True)
    corte = [e for e in res["geom_cut"] if isinstance(e, bmesh.types.BMEdge)]
    if corte:
        bmesh.ops.contextual_create(bm, geom=corte)
    return _objeto(nome or (g.name + "_agua_nivel"), bm, O3.M("#2f6f9e", "#24577c", "#8ec8ea"), g, (0, 0, 0), 0.0)


def abrigo_fim(dia=700, **k):
    return abrigo3(pal_nome="escuro", lamp=(0, 1, 0), dia=dia, nivel=0.0, dim=True, **k)


@shot("9A", 54.20, 55.30, "Quando só restava", "32 mm, de frente, baixa, o Zé agacha ao lado do último galão", "o Zé levantando o galão", "parada",
      "De frente e de corpo inteiro: o último galão no chão, com a água pela metade; o Zé agacha ao lado dele, agarra a alça com a mão do lado do galão e levanta, curvado pelo peso, o galão balançando na alça. O gesto simples e pesado, sem a mão solta no ar.")
def p9A():
    p, wy = abrigo_fim(galao=0.0, mesa=False)
    g = O3.galao3d("galao_z", (-1.0, 3.7, 0.0), 1.8, nivel=0.5)
    SA.ator3("ze", "ze", -0.5, 3.7, rot=0, pose=dict(ombro=(-6, -6), cotovelo=(-12, -12), abre=(8, 8), cabeca=12), rosto=dict(boca="reta", lid=0.5))
    cam((-0.7, 1.55, 1.12), (-0.72, 3.7, 0.86), 28, fstop=6.0, foco=(-0.7, 3.7, 0.8))


@shot("9B", 55.30, 56.50, "meio galão d'água", "40 mm, f/4, de três quartos, na altura do rosto", "o Zé bebendo e a linha da água", "parada",
      "De três quartos: o Zé de cabeça para trás e olhos fechados, o galão inclinado com a boca na boca dele, as duas mãos nele (uma na alça, a outra embaixo); a linha da água dentro do plástico azul fica na horizontal e bolhas sobem enquanto ele engole. Beber o que resta é decidir sair.")
def p9B():
    p, wy = abrigo_fim(galao=0.0, mesa=False)
    ze = SA.ator3("ze", "ze", -0.4, 3.4, rot=0, pose=dict(ombro=(-90, -90), cotovelo=(-60, -60), abre=(10, 10), tronco=-6, cabeca=-24), rosto=dict(boca="reta", lid=1.5))
    s_ = 1.5; phi = -112.0
    R = Matrix.Rotation(math.radians(phi), 3, "X")
    M_ = IK.boca_de(ze); fw = (ze.cabeca.matrix_world.to_3x3() @ Vector((0, -1, 0))).normalized()
    T = M_ + fw * 0.012                                                  # a boca do galão encosta nos lábios
    G0 = T - R @ Vector((0, 0, 0.318 * s_))
    g = O3.galao3d("galao_z", tuple(G0), s_, nivel=0.5); g.rotation_euler = (math.radians(phi), 0, 0)
    if bpy.data.objects.get("galao_z_tampa"):
        bpy.data.objects["galao_z_tampa"].hide_render = True              # sem a tampa: a boca aberta na boca dele
    FASES = (-112, -94, -76, -58, -40, -22, -6, 0)
    for ph in FASES:                                              # uma água de nível para cada fase do movimento (o 9B baixa o galão)
        agua_de_nivel(g, ph, f"agua_ph{abs(ph)}").hide_render = True
    bpy.data.objects["agua_ph112"].hide_render = False
    bpy.context.view_layer.update()
    alca = G0 + R @ Vector((0.15 * s_, 0.0, 0.2 * s_)); lado_f = G0 + R @ Vector((-0.1 * s_ - 0.04, 0.0, 0.1 * s_))
    d = IK.braco_pose(ze, "B", alca, None, nome="9B alca"); d = IK.braco_pose(ze, "F", lado_f, d, nome="9B lado")
    ze.pose(**d)
    cam((-1.55, 2.2, 1.5), (-0.38, 3.3, 1.35), 38, fstop=4.0, foco=(-0.4, 3.3, 1.45))


@shot("9C", 56.50, 57.70, "o Zé finalmente", "35 mm, f/2,8, baixa, de três quartos, andando junto", "ele atravessando o abrigo até a porta", "travelling lateral",
      "Pedido de 25/10/2026 (\"ele só levanta, vai lá e vai todo torto\"): agora há caminhada de verdade. Depois do último gole ele deixa o galão, olha a porta (9B) e anda decidido pela sala, passo firme e cabeça erguida, a Rita parada olhando, desfocada, sem tentar impedir; a câmera baixa anda junto, de três quartos, e a porta vai crescendo na frente, com um fio de luz pelas bordas e poeira brilhando no ar. Ao chegar ele para, respira e vira de frente para a roda.")
def p9C():
    p, wy = abrigo_fim(galao=0.0, mesa=False)
    O3.galao3d("galao_chao", (-0.2, 3.3, 0.0), 1.5, nivel=0.05)                # o galão deixado no chão no 9B
    SA.ator3("ze", "ze", 1.2, 3.95, rot=118, pose=dict(ombro=(-6, 8), cotovelo=(-12, -14), abre=(6, 6), tronco=-3, cabeca=2), rosto=dict(boca="reta", lid=0.38))
    SA.ator3("rita", "rita", -0.25, 2.55, rot=40, pose=dict(ombro=(-4, 4), cotovelo=(-14, -14)), rosto=dict(boca="triste", lid=0.45))
    for k, (x, z, sx, sz) in enumerate(((2.43, 1.1, 0.018, 2.2), (3.37, 1.1, 0.018, 2.2), (2.9, 2.2, 1.0, 0.018))):          # o fio de luz pelas bordas da porta
        O3.caixa(f"fio_luz{k}", (sx, 0.02, sz), O3.brilha("#fff1cc", 1.1), None, (x, wy - 0.27, z), chanfro=0.0, contorno=0.0)
    halo("luz_porta", 2.9, wy - 0.3, 1.15, 1.5, "#fffbe8", 0.0)
    cena.dust(p, 40, (1.2, 3.4), 30, seed=17, color="#fff6dc", alpha=0.75, y_range=(wy - 1.8, wy - 0.3), z_range=(0.4, 2.1), size=(0.005, 0.011))
    cam((0.3, 2.35, 1.0), (2.1, 4.7, 1.22), 35, fstop=2.8, foco=(1.6, 4.3, 1.2))


def porta_roda(angulo, aberta, branco=False):
    p, wy = foyer3(aberta=aberta, fora="branco", lamp=False)
    ze = SA.ator3("ze", "ze", 0.0, wy - 0.75, rot=180, pose=dict(ombro=(-92, -92), cotovelo=(-18, -18), abre=(12, 12), tronco=-4))
    ze.fecha_mao("F"); ze.fecha_mao("B")
    roda = bpy.data.objects["porta_roda"]; roda.rotation_euler = (0, math.radians(angulo), 0)
    bpy.context.view_layer.update()
    c = roda.matrix_world.translation
    SA.maos_em(ze, (c.x - 0.2 + 0.15, c.y - 0.06, c.z + 0.12), (c.x + 0.2 + 0.15, c.y - 0.06, c.z - 0.05))
    return p, wy, c


@shot("9D", 57.70, 58.40, "destrancou", "28 mm, f/4, por trás do ombro do Zé, na altura da cabeça", "ele girando a roda e a luz pelas bordas", "empurra devagar",
      "Por cima do ombro do Zé, ele inteiro de costas diante da porta: as duas mãos na roda de bronze, que gira com esforço e solta ferrugem; o corpo se joga junto; pelas bordas da porta a luz branca de fora aparece e cresce, com poeira brilhando no ar e uma mancha de luz no chão que chega até os pés dele. A folha começa a correr.")
def p9D():
    p, wy, c = porta_roda(60, 0.02)
    import random
    rnd = random.Random(3)
    for k in range(16):
        props.poly(f"ferrugem{k}", __import__("puppet2d").circle(0, 0, 0.008, 6), "#b8692e", 0.0, None).location = (c.x + rnd.uniform(-0.35, 0.35), c.y - 0.14, c.z + rnd.uniform(-0.4, 0.3))
    luz_da_porta(p, wy)
    cam((0.78, wy - 1.7, 1.78), (0.12, wy - 0.15, 1.35), 28, fstop=4.0, foco=(0.08, wy - 0.25, 1.3))


def luz_da_porta(p, wy, cx=0.0):
    """a luz de fora entrando pela folha: brilho em volta da fresta, mancha no chão que chega até o Zé, três cortinas de névoa luminosa e poeira no ar
    (o anim3_abrigo faz tudo crescer pelo tempo: alfa('luz_fresta_m'), alfa('luz_chao_m'), alfa('luz_nevoa{k}_m'))"""
    halo("luz_fresta", cx + 0.3, wy - 0.16, 1.2, 1.7, "#ffffff", 0.0)
    cena.ground_disc("luz_chao", 0.75, 1.9, cena.amat("luz_chao_m", "#ffffff", 1.0, 0.0, ("radial", 1.2)), (cx + 0.1, wy - 1.2, 0.012), n=48)
    for k, (dy, r) in enumerate(((0.35, 1.2), (0.8, 1.5), (1.3, 1.7))):
        halo(f"luz_nevoa{k}", cx + 0.12, wy - dy, 1.3, r, "#fffdf0", 0.0)
    cena.dust(p, 50, (cx - 0.7, cx + 0.7), 30, seed=19, color="#ffffff", alpha=0.7, y_range=(wy - 1.5, wy - 0.25), z_range=(0.2, 2.2), size=(0.005, 0.011))


@shot("9E", 58.40, 58.98, "a porta", "28 mm, f/4, o mesmo quadro por trás do ombro, a luz toma tudo", "o Zé em silhueta e a luz", "empurra devagar",
      "A folha corre, a fresta vira porta aberta e a luz de fora entra por trás do Zé até estourar: ele vira silhueta, protege os olhos com o braço, e a tela fica branca. O clarão do começo, só que ao contrário.")
def p9E():
    p, wy, c = porta_roda(96, 0.14)
    luz_da_porta(p, wy)
    cam((0.78, wy - 1.7, 1.78), (0.12, wy - 0.15, 1.35), 28, fstop=4.0, foco=(0.08, wy - 0.25, 1.3))


# ====================================================================== 10. Lá fora (58,98 a 66,54 s)
@shot("10A", 58.98, 60.20, "Lá fora, não tinha", "35 mm, de dentro da porta, o mesmo quadro do 1F", "a rua vazia", "parada",
      "O mesmo quadro do 1F, de dentro da porta: onde corriam o Zé e a Lu, agora não tem ninguém. A rua em ruínas, o céu branco sujo, a cinza caindo.")
def p10A():
    p, wy = foyer3(aberta=1.0, fora="morta", lamp=False)
    esqueletos_porta((0.0, wy), virado=180)
    cena.dust(p, 80, (-3, 3), 30, seed=5, color="#e8e2cc", alpha=0.85, y_range=(wy, wy + 12.0), z_range=(0.2, 4.0), size=(0.008, 0.02))
    cam((0.1, wy - 1.7, 1.25), (0.0, wy + 14.0, 1.7), 35, fstop=5.6, foco=(0.0, wy + 4.5, 1.4))


@shot("10B", 60.20, 61.30, "mais nada", "18 mm, do alto do bunker, o mesmo quadro do 1F", "a rua vazia", "parada",
      "O mesmo quadro do 1F, do alto do bunker, olhando a rua para onde todo mundo correu: onde vinha a multidão agora há prédios quebrados em dentes, postes tortos, um carro parado e cinza no chão. Nada se mexe.")
def p10B():
    p = rua3(morta=True, carros=True); sem_halo_do_bunker()
    esqueletos_porta()
    # do alto do bunker, o mesmo quadro do 1F: o 10A já olha a rua de dentro da porta, então este plano muda de lugar (regra: nunca dois planos seguidos iguais)
    cam((-2.0, BY + 0.9, 7.6), (0.3, BY - 11.0, -0.4), 18, fstop=8.0, foco=(0.0, BY - 6.0, 1.0))


@shot("10C", 61.30, 62.50, "Só cinza, poeira", "28 mm, rente ao chão, de lado, na soleira", "as botas do Zé pisando na cinza", "parada",
      "De lado, rente ao chão: o Zé sai do vão da porta, as botas cruzam a soleira e pisam na cinza escura, que levanta em nuvenzinhas e assenta; ao fundo, entre as colunas, a luz âmbar do abrigo, e na cinza, perto das botas, ossos de quem ficou. É a primeira coisa que ele toca lá fora.")
def p10C():
    p = rua3(morta=True, aberta=0.9, nevoa=False)
    SA.ator3("ze", "ze", 0.0, BY + 0.45, rot=0, pose=dict(quadril=(-24, 18), joelho=(30, 8), tornozelo=(10, -6), ombro=(10, -10), cotovelo=(-14, -14)), rosto=dict(boca="triste", lid=0.5))
    for r_ in esqueletos_porta()[:2]:                            # os dois mais perto da porta ficam fora deste plano (o osso gigante tapava a bota)
        for o in [r_] + list(r_.children_recursive):
            o.hide_render = True; o.hide_viewport = True
    rnd = __import__("random").Random(2)
    for k in range(26):                                          # cinza escura e rasa, em montinhos irregulares (branca e alta parecia neve)
        O3.esfera(f"cinza{k}", rnd.uniform(0.1, 0.26), rnd.uniform(0.08, 0.2), rnd.uniform(0.012, 0.03), O3.M("#5e5a53", "#47443f", "#77736a"), None,
                  (rnd.uniform(-1.0, 1.0), BY - rnd.uniform(0.35, 2.4), 0.0), contorno=0.0, seg=14, an=7)
    cena.dust(p, 60, (-1.0, BY - 1.6), 40, seed=4, color="#5a5650", alpha=0.85, y_range=(BY - 2.2, BY - 0.4), z_range=(0.02, 0.5), size=(0.004, 0.01))
    cam((1.5, BY - 1.15, 0.42), (0.0, BY - 0.5, 0.3), 28, fstop=5.6, foco=(0.0, BY - 0.5, 0.3))


@shot("10D", 62.50, 63.70, "e silêncio", "35 mm, no chão, câmera parada", "a sirene calada", "parada",
      "A sirene do começo caída no asfalto, as cornetas cheias de cinza, a luz apagada. O mesmo objeto que gritou agora não faz som nenhum.")
def p10D():
    p = rua3(morta=True, carros=False, nevoa=False)
    sirene(-6.2, 2.4, caida=True, poeira=0.9)
    cena.dust(p, 50, (-1.5, 2.0), 30, seed=9, color="#ece7d4", alpha=0.9, y_range=(0.6, 2.4), z_range=(0.05, 1.4), size=(0.006, 0.014))
    cam((1.2, 0.4, 0.55), (-0.9, 2.4, 0.5), 35, fstop=2.8, foco=(-0.9, 2.4, 0.5))


def bici_morta():
    b = O3.bicicleta3d("bici", (0.4, 2.6, 0.0), 1.0, cor="#6a665a", poeira=0.85); b.rotation_euler = (math.radians(55), 0, math.radians(-10))
    bpy.context.view_layer.update()
    return b


@shot("10E", 63.70, 64.80, "A minha bicicleta", "14 mm, o mesmo quadro do 1C, no chão", "a roda e o sino", "parada",
      "A bicicleta exatamente onde caiu, coberta de pó cinza, a roda da frente parada. O mesmo quadro do 1C, sem ninguém correndo ao fundo: a cidade que ela cruzava sumiu.")
def p10E():
    p = rua3(morta=True, carros=True)
    bici_morta()
    hub = bpy.data.objects["bici_cubo1"].matrix_world.translation.copy()
    cam((hub.x + 0.55, hub.y - 0.75, 0.16), (hub.x - 0.6, hub.y + 2.5, 0.35), 14, fstop=2.8, foco=(hub.x, hub.y, hub.z), roll=4)


def trocar_campainha(poeira=0.85, limpa=False):
    """põe no lugar da bolinha da bicicleta uma campainha de verdade (cúpula, base, pino e botão); devolve a campainha"""
    for n_ in ("bici_campainha", "bici_campainha_b"):
        o = bpy.data.objects.get(n_)
        if o is not None:
            o.hide_render = True
    return O3B.campainha3d("bici_sino", (0.33, -0.15, 1.0), 1.0, bpy.data.objects["bici"], poeira=poeira, limpa=limpa)


@shot("10F", 64.80, 65.90, "ainda estava lá, no mesmo", "35 mm, de lado, a mão magra com o relógio parado", "o sino", "parada",
      "A mão de quem conta, agora magra, com um relógio de ponteiros parados no pulso, desce sobre o sino e passa o polegar para tirar o pó. O braço entra de lado e sai do quadro.")
def p10F():
    p = rua3(morta=True, carros=False, nevoa=False)
    bici_morta()
    sino = trocar_campainha(0.85, limpa=False)
    bpy.context.view_layer.update()
    M3 = sino.matrix_world.to_3x3(); pos = sino.matrix_world.translation.copy()
    U = (M3 @ Vector((0, 0, 1))).normalized(); Fw = (bpy.data.objects["bici"].matrix_world.to_3x3() @ Vector((1, 0, 0))).normalized()
    Sd = (bpy.data.objects["bici"].matrix_world.to_3x3() @ Vector((0, 1, 0))).normalized()
    topo = pos + U * 0.032
    dA = (Fw * 0.75 - U * 0.45).normalized()
    mao_braco("mao_s", "dir", tuple(topo - dA * 0.10 + U * 0.01), dA, flexao=-12.0, pose="pinca", escala=1.0, roll=0, relogio=True, manga_comp=1.9)
    cam(tuple(pos + Sd * 0.42 + U * 0.22 - Fw * 0.12), tuple(pos + U * 0.03), 40, fstop=2.8, foco=tuple(pos + U * 0.03))


@shot("10G", 65.90, 66.54, "lugar.", "85 mm, o sino de perto, parada", "o sino", "parada",
      "O sino de perto, com uma faixa limpa e brilhante onde o polegar passou, o resto coberto de pó. É a única coisa que reluz no mundo cinza; ele toca, e o som não tem eco.")
def p10G():
    p = rua3(morta=True, carros=False, nevoa=False)
    bici_morta()
    sino = trocar_campainha(0.85, limpa=True)
    bpy.context.view_layer.update()
    M3 = sino.matrix_world.to_3x3(); pos = sino.matrix_world.translation.copy()
    U = (M3 @ Vector((0, 0, 1))).normalized(); Sd = (bpy.data.objects["bici"].matrix_world.to_3x3() @ Vector((0, 1, 0))).normalized()
    cam(tuple(pos + Sd * 0.30 + U * 0.16), tuple(pos + U * 0.02), 85, fstop=2.0, foco=tuple(pos + U * 0.02))


def _fim_do_filme():
    """o último plano segura a imagem até o fim da fala do fecho ("Quer continuação? Segue pra parte dois."), sem fade e sem plano novo (pedido de 25/10/2026)"""
    p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "roteiros", "voz-abrigo", "tempos_final.json")
    try:
        return round(json.load(open(p))["total"], 3)
    except Exception:
        return 71.40


# ====================================================================== 11. O preço (66,54 a 71,73 s)
def esqueletos_porta(porta=(0.0, BY), virado=0.0, poeira=0.55):
    """quem ficou do lado de fora (pedido de 25/10: "deveria ter os esqueletos das pessoas que ficaram lá, na frente da porta"): encostado no pilar,
    caído com o braço esticado para a porta, de lado, mais atrás na rua. Posições relativas à porta, com a rua para -y;
    virado = 180 para a cena de dentro (foyer3), em que a rua fica para +y"""
    P = empty("esqueletos", None, (porta[0], porta[1], 0)); P.rotation_euler.z = math.radians(virado)
    lst = [O3B.esqueleto3d("esq_a", (-1.02, -0.8, -0.8), (0, 0, 8), quadril=(-88, -84), joelho=(4, 14), ombro=(6, 10), abre=(14, 20), cotovelo=(-10, -30), cabeca=28, queixo=22, poeira=poeira),
           O3B.esqueleto_deitado("esq_b", (0.98, -0.62), rumo=8, de_lado=180, z=0.1, ombro=(-170, -20), abre=(10, 30), cotovelo=(-10, -40), poeira=poeira, seed=4),
           O3B.esqueleto_deitado("esq_c", (-0.35, -2.55), rumo=75, de_lado=90, z=0.11, ombro=(-30, -60), cotovelo=(-60, -40), quadril=(-30, 10), joelho=(50, 20), poeira=poeira, seed=5),
           O3B.esqueleto_deitado("esq_d", (0.35, -3.45), rumo=30, z=0.1, ombro=(-20, 30), cotovelo=(-20, -10), poeira=poeira, seed=6),
           O3B.esqueleto_deitado("esq_e", (-0.95, -4.3), rumo=20, de_lado=180, z=0.1, ombro=(-160, -150), cotovelo=(-10, -10), poeira=poeira, seed=7)]
    bpy.context.view_layer.update()
    M0 = P.matrix_world.copy()
    for o in lst:                                                   # cada esqueleto fica solto no mundo (o detector de colisão vê um por um)
        o.matrix_world = M0 @ o.matrix_world.copy()
    bpy.data.objects.remove(P, do_unlink=True)
    return lst


def ruina_final(y0=-8.0):
    p = rua3(morta=True, aberta=0.9, carros=True, y0=y0)
    ze = SA.ator3("ze", "ze", -0.6, BY - 1.1, rot=0, pose=dict(ombro=(-3, 5), cotovelo=(-10, -10), abre=(4, 4)), rosto=dict(boca="triste", lid=0.68))
    SA.ator3("eu", "eu", 0.05, BY - 1.1, rot=0, pose=dict(ombro=(-3, 5), cotovelo=(-10, -10), abre=(4, 4)), rosto=dict(boca="triste", lid=0.68))        # o narrador (de vermelho) sobreviveu junto
    ri = SA.ator3("rita", "rita", 0.7, BY - 1.1, rot=0, pose=dict(ombro=(5, -40), cotovelo=(-10, -60), abre=(4, 4)), rosto=dict(boca="triste", lid=0.68))
    bpy.context.view_layer.update()
    m = ri.punho["B"].matrix_world.translation                  # o suéter na mão de fora (longe do narrador)
    O3.sueter3d("sueter_fim", (m.x, m.y - 0.06, m.z - 0.06), 1.5)
    b = O3.bicicleta3d("bici", (-1.9, BY - 2.6, 0.0), 1.0, cor="#6a665a", poeira=0.85); b.rotation_euler.z = math.radians(80)
    esqueletos_porta()
    return p, ze, ri


@shot("11A", 66.54, 67.80, "A gente sobreviveu", "40 mm, de frente, na altura do peito", "os dois", "parada",
      "O Zé e a Rita de pé na porta do abrigo, cansados, apertando os olhos contra a luz suja. A Rita segura o suéter vermelho: é a única cor viva do quadro.")
def p11A():
    ruina_final()
    cam((0.05, BY - 5.0, 1.25), (0.0, BY - 1.1, 1.2), 40, fstop=2.8, foco=(0.0, BY - 1.1, 1.3))


@shot("11B", 67.80, 69.00, "Só pra ficar sozinho", "50 mm, f/2, no peito da Rita", "o suéter vermelho", "parada",
      "O suéter vermelho da Pipoca nas mãos da Rita, único ponto de cor no mundo cinza. A gente entende o que ela perdeu e o que ainda carrega.")
def p11B():
    p, ze, ri = ruina_final()
    cam((0.95, BY - 2.6, 1.0), (0.9, BY - 1.1, 0.95), 50, fstop=2.0, foco=(0.9, BY - 1.2, 0.95))


@shot("11C", 69.00, 70.20, "num mundo que acabou", "28 mm, grua alta que sobe e recua", "todo o lugar", "grua lenta",
      "A câmera sobe e recua: os dois, a bicicleta e o bunker ficam pequenos no meio do cinza, com os prédios quebrados dos dois lados da rua.")
def p11C():
    ruina_final()
    cam((0.0, BY - 13.0, 8.5), (0.0, BY - 1.0, 0.8), 28, fstop=11.0, foco=(0.0, BY - 1.2, 1.0))


@shot("11D", 70.20, _fim_do_filme(), "(fim) Quer continuação? Segue pra parte dois.", "50 mm, f/1,4, nos dois, algo desfocado bem perto", "o barulho, as cabeças que viram e o vulto", "parada",
      "Pedido de 25/10/2026 (suspense antes do CTA): os dois de frente no vão do abrigo, calados; ouvem um barulho fora do quadro, viram a cabeça para o mesmo lado e, bem perto da câmera, desfocado e no escuro, um vulto curvado se mexe e rosna como um zumbi. Dá para ver que tem alguma coisa, mas não o que é. Em cima desse último quadro entra a voz: Quer continuação? Segue pra parte dois.")
def p11D():
    p, ze, ri = ruina_final()
    for o in bpy.data.objects:                                       # só os dois no quadro: sem o osso e a bicicleta no meio da imagem
        if o.name.startswith(("esq_", "bici")) and o.parent is None:
            for c in [o] + list(o.children_recursive):
                c.hide_render = True
    import heroi3d as _h
    global ZUMBI
    zb = ZUMBI = _h.Heroi3D("zumbi", roupa="#0b0b0e", calca="#08080a", escura="#050507", gola="#050507", sapato="#050507", borda="#16161c", cabeca=0.82, body_w=1.1, arm_len=1.2)
    escuro = _h.estilo("#0b0b0e", "#050507", "#1c1c24")
    for o in [zb.raiz] + list(zb.raiz.children_recursive):
        if o.type == "MESH":
            o.data.materials.clear(); o.data.materials.append(escuro)
    zb.pose(ombro=(-52, -34), cotovelo=(-34, -58), abre=(14, 18), tronco=-34, cabeca=-22, quadril=(-8, 16), joelho=(18, 6), tornozelo=(0, 0), alt=0.84)
    # a câmera está escondida nos destroços, ao lado do abrigo, olhando os dois de lado (pedido de 25/10/2026: "nas destruições, na lateral, olhando eles de lado");
    # na frente dela entulho desfocado e, bem perto, no escuro, o vulto
    alvo = Vector((0.0, BY - 1.1, 1.18)); pc = Vector((3.35, BY - 2.75, 0.82))
    f = (alvo - pc); f.z = 0; f.normalize(); r = Vector((f.y, -f.x, 0.0))
    global ESQ
    ESQ = -r
    th = math.degrees(math.atan2(-f.x, f.y))                       # o vulto de frente para a câmera
    zb.raiz.location = tuple(pc + f * 1.1 + ESQ * 0.34); zb.raiz.location.z = 0.0
    zb.raiz.rotation_euler.z = math.radians(th); zb.raiz.scale = (1.0,) * 3
    rnd_ = __import__("random").Random(14)
    for k, (df, dr, tam, rz) in enumerate(((0.55, 0.38, (0.9, 0.5, 0.34), 25), (0.8, 0.05, (0.7, 0.42, 0.5), -18), (0.62, -0.22, (1.1, 0.3, 0.22), 52), (1.9, 0.9, (0.8, 0.6, 0.6), 10), (2.2, -0.5, (0.6, 0.7, 0.45), -40))):
        pos = pc + f * df + r * dr
        O3.caixa(f"entulho{k}", tam, O3.M("#4a4b45", "#33342f", "#6c6d64"), None, (pos.x, pos.y, tam[2] / 2), chanfro=0.03, rot=(rnd_.uniform(-6, 6), rnd_.uniform(-8, 8), rz))
    tubo_ = O3.cilindro("vergalhao", 0.015, 1.3, O3.M("#2c2b2a", "#1e1d1c", "#4a4846"), None, tuple(pc + f * 0.9 + r * 0.5 + Vector((0, 0, 0.35))), seg=10)
    tubo_.rotation_euler = (math.radians(70), math.radians(12), math.radians(th + 20))
    cam(tuple(pc), tuple(alvo), 40, fstop=1.6, foco=tuple(alvo))





# ---------------------------------------------------------------- main
def main():
    argv = sys.argv[sys.argv.index("--") + 1:]
    if "--list" in argv:
        for k, d in SHOTS.items():
            print(f"{k} | {d['t0']:.2f}-{d['t1']:.2f} | {d['lente']} | {d['palavras']}")
        return
    if "--json" in argv:                                                 # metadados para a prancha e para a decupagem em texto
        json.dump({k: {a: b for a, b in d.items() if a != "fn"} for k, d in SHOTS.items()}, open(argv[argv.index("--json") + 1], "w"), ensure_ascii=False, indent=1)
        return
    nome, out = argv[0], argv[1]
    k = float(argv[argv.index("--scale") + 1]) if "--scale" in argv else 0.5
    smp = int(argv[argv.index("--samples") + 1]) if "--samples" in argv else 16
    lib.reset(int(1080 * k), int(1920 * k), 24, smp)
    sc = bpy.context.scene; sc.frame_start, sc.frame_end = 1, 24
    SHOTS[nome]["fn"]()
    sc.frame_set(1)
    sc.render.filepath = out
    bpy.ops.render.render(write_still=True)
    c = SHOTS[nome]["cctv"]
    if c:                                                                # o visual de câmera de segurança é por cima do quadro (o Blender não tem PIL:
        json.dump(c, open(out + ".cctv", "w"))                           # o story3_rodar.py aplica o pos_cctv com o python do sistema)


if __name__ == "__main__":
    main()
