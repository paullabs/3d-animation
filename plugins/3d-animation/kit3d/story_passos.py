"""Storyboard de "E se cada passo dobrasse a sua altura?" (plano: personagem/passos/plano-de-cena-v1.md; voz: roteiros/voz-passos, 80,26 s).
Um quadro parado por plano, com lente em mm, posição e foco de verdade. A tabela SHOTS é a fonte única.

ESCALA: o boneco ("eu") tem SEMPRE 1,8 de altura na cena; quem encolhe é o mundo. No passo n o mundo é modelado em metros reais e entra num
empty com escala k = 2^-n (no_mundo). Por isso a lente em mm continua significando alguma coisa e nada estoura no Blender.
blender -b -P story_passos.py -- PLANO SAIDA.png [--scale 0.5] [--samples 16]      (--list mostra todos)"""
import os, sys, math, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy, lib
from lib import empty
from mathutils import Vector
import cena, props
import objetos3d_abrigo as O3, cidade3d as C3, elenco3d_abrigo as E3, story_abrigo as SA
import objetos3d_passos as OP
from heroi3d import esfera, tubo, _mix

SHOTS = {}
EU_ESC = 1.8 / 1.70                         # o boneco nativo tem 1,70: sobe para 1,8
H_EU = 1.8
CEU = dict(chao="#c9cfc6", horizonte="#dbe8ee", meio="#a9cde6", topo="#4f86c4")
E3.ESPEC["moca"] = dict(roupa="#3b6f94", calca="#2d3036", escura="#2c556f", gola="#2c556f", cabeca=0.78, body_w=0.96, arm_len=1.08, escala=0.96,
                        acess=[("cabelo", "solto", "#3a2418")])
E3.ESPEC["eu"]["roupa"] = "#8a2d2a"; E3.ESPEC["eu"]["escura"] = "#6a201e"; E3.ESPEC["eu"]["gola"] = "#6a201e"   # (o mundo7 troca isto por uma vermelha mais viva)          # a blusa vermelha escura, um pouco mais viva de dia
E3.BORDA = OP.BD

STAND = dict(ombro=(-4, 6), cotovelo=(-12, -10), abre=(6, 6))


def shot(nome, t0, t1, palavras, lente, nota):
    def deco(fn):
        SHOTS[nome] = dict(t0=t0, t1=t1, palavras=palavras, lente=lente, nota=nota, fn=fn)
        return fn
    return deco


# ---------------------------------------------------------------- câmera e peças comuns
def cam(loc, alvo, lens, fstop=5.6, foco=None, roll=0.0):
    c = SA.camera(loc, alvo, lens, fstop=fstop, foco=foco, roll=roll)
    c.data.clip_end = 3000.0
    O3.olha_camera(c)
    return c


def cam_v(alvo, vis, lente, az=0.0, el=0.0, dist=None, fstop=5.6, foco=None, roll=0.0):
    """posiciona a câmera para que 'vis' (u) caiba na altura do quadro em volta do alvo; az: 0 = de frente (câmera em -y), + para o lado +x; el: para cima"""
    d = dist or (vis / 2.0) / (21.333 / lente)
    a, e = math.radians(az), math.radians(el)
    pos = Vector(alvo) + Vector((d * math.sin(a) * math.cos(e), -d * math.cos(a) * math.cos(e), d * math.sin(e)))
    return cam(tuple(pos), tuple(alvo), lente, fstop=fstop, foco=foco if foco is not None else tuple(alvo), roll=roll)


def ceu_dia(p=CEU, cor_chao=None):
    bpy.context.scene.world.node_tree.nodes["Background"].inputs[0].default_value = (*lib.srgb(p["horizonte"]), 1)
    OP.domo([(-900, p["chao"]), (-1, p["chao"]), (0, p["horizonte"]), (140, p["meio"]), (520, p["topo"])])


def ceu_espaco():
    bpy.context.scene.world.node_tree.nodes["Background"].inputs[0].default_value = (0.004, 0.006, 0.014, 1)
    OP.domo([(-900, "#04060c"), (900, "#080c18")])
    OP.estrelas()


def no_mundo(n, fn, cont_u=0.004):
    """roda fn() (modela em METROS REAIS) e põe tudo que nasceu num empty com escala k = 2^-n; o contorno de tinta mantém a espessura em u"""
    k = 2.0 ** -n
    antes = {o.name for o in bpy.data.objects}
    fn()
    E = empty(f"mundo{n}", None, (0, 0, 0)); E.scale = (k,) * 3
    for o in list(bpy.data.objects):
        if o.name not in antes and o.parent is None and o.name != E.name:
            o.parent = E
    for o in bpy.data.objects:
        if o.name not in antes:
            for md in o.modifiers:
                if md.type == "SOLIDIFY" and md.thickness > 0:
                    md.thickness = max(md.thickness, cont_u / k)
    return E


def eu(pose=None, rosto=None, loc=(0, 0, 0), rot=0.0, nome="eu", sombra=True, pe=True):
    """o 'eu' (blusa vermelha escura, cabeça preta, olho branco) com 1,8 de altura, de frente para -y"""
    h = E3.faz("eu", nome)
    P = dict(STAND); P.update(pose or {})
    h.raiz.scale = (EU_ESC,) * 3
    h.pose(**(h.pe_no_chao(**P) if pe else P))
    h.raiz.location = loc; h.raiz.rotation_euler.z = math.radians(rot)
    r = dict(boca="reta", lid=0.0); r.update(rosto or {}); h.rosto(**r)
    if sombra:
        cena.ground_disc(nome + "_sb", 0.42 * EU_ESC, 0.26 * EU_ESC, cena.amat(nome + "_sb_m", "#000000", 1.0, 0.38, ("radial", 1.1)), (loc[0], loc[1] + 0.05, 0.004), n=32)
    return h


def moca_k(n, du=(-0.47, -0.2), pose=None, rot=10.0):
    """a moça de referência (1,64 m de verdade); fica sempre no mesmo lugar do quadro (du em u), então sua posição em metros muda com n"""
    k = 2.0 ** -n
    h = E3.faz("moca", "moca")
    h.raiz.scale = (EU_ESC * 0.97 * k,) * 3
    P = dict(STAND); P.update(pose or dict(ombro=(-8, 10), cotovelo=(-20, -14)))
    h.pose(**h.pe_no_chao(**P)); h.raiz.location = (du[0], du[1], 0); h.raiz.rotation_euler.z = math.radians(rot)
    h.rosto(boca="reta", lid=0.0)
    cena.ground_disc("moca_sb", 0.4 * EU_ESC * k, 0.25 * EU_ESC * k, cena.amat("moca_sb_m", "#000000", 1.0, 0.38, ("radial", 1.1)), (du[0], du[1] + 0.05 * k, 0.004), n=24)
    return h


def passo_n(n):
    return H_EU * 2 ** n


def fmt_m(m):
    """1,8 m | 57,6 m | 922 m | 1,8 km | 3.775 km (vírgula decimal, ponto de milhar)"""
    if m < 100:
        return f"{m:.1f}".replace(".", ",") + " m"
    if m < 1000:
        return f"{m:.0f} m"
    km = m / 1000.0
    return (f"{km:.1f}".replace(".", ",") if km < 100 else f"{km:,.0f}".replace(",", ".")) + " km"


def regua_eu(n, x=-0.36, y=0.15, rotulo=None, altura=None, passo_m=None, lado=-1):
    """a régua do filme: fita métrica ao lado do boneco, riscos nos metros REAIS (por isso mudam com n) e o número em âmbar na altura da cabeça"""
    k = 2.0 ** -n
    alt_m = passo_n(n)
    pm = passo_m or OP.bonito(alt_m / 9.0)
    if lado > 0:
        x = abs(x)
    OP.fita(x, altura or H_EU, pm * k, y=y, rotulo=rotulo if rotulo is not None else fmt_m(alt_m), linha_ate=(0.17 if lado > 0 else -0.17, altura or H_EU), rot_dx=-0.12 if lado > 0 else 0.12)


# ---------------------------------------------------------------- mundos
def abre_lado(E, lado=1):
    """tira os prédios, a calçada, os postes e as árvores de um lado da rua para a câmera lateral caber"""
    pref = (f"pr{lado}_", f"calcada{lado}", f"meiofio{lado}", f"poste{lado}_", f"arv{lado}_", f"fio{lado}_", "fio_cruza", f"carro_{lado}")
    for o in list(bpy.data.objects):
        if o.name.startswith(pref) or (o.parent and o.parent.name.startswith("poste") and False):
            bpy.data.objects.remove(o, do_unlink=True)


def mundo_rua(n, y0_u=-4.0, y1_u=60.0, carros=True, moca=True, aberto=False):
    """a rua de bairro (n = 0 a 5), com a moça de referência; escalada por k"""
    k = 2.0 ** -n
    ceu_dia()
    def build():
        cena.poly_mesh("chao_largo", [(-4000, -4000, -0.03), (4000, -4000, -0.03), (4000, 4000, -0.03), (-4000, 4000, -0.03)], props.FM("#8d9187"))
        C3.rua3d(dict(chao="#8d9187"), max(-300.0, y0_u / k), min(520.0, y1_u / k), carros=carros)
    E = no_mundo(n, build, cont_u=0.0035)
    if aberto:
        abre_lado(E, 1)
    if moca:
        moca_k(n)


def predio_ao_lado(n, andares, x_u=0.42, y_u=0.8, lado=1, w_m=None, cor="#8a93a0"):
    """prédio de comparação de 'andares' andares (3 m cada), ao lado do boneco; o centro fica a x_u do eixo dele e y_u à frente"""
    k = 2.0 ** -n
    h = andares * 3.0
    w = w_m or max(8.0, h * 0.42)
    cx = lado * (x_u / k + w / 2); cy = y_u / k
    no_mundo(n, lambda: OP.torre("cmp", cx, cy, w, w * 0.9, h, cor=cor), cont_u=0.0035)
    return h, cx, cy, w


def mundo_cidade(n, burj_em=None, clareira=None, raio_u=22.0, altura_max=130.0, y_burj=None, livre=0.6):
    kk = 2.0 ** -n
    cl = [(0.0, 0.0, livre / kk)] + ([clareira] if clareira else [])
    """a cidade de longe (n = 6 a 10): quarteirões de caixas; o Burj Khalifa em burj_em = (x_u, y_u)"""
    k = 2.0 ** -n
    ceu_dia()
    def build():
        OP.chao("#8f9a8a", None, 40000.0, nome="chao_largo")
        OP.cidade_maquete(min(raio_u / k, 5200.0), passo=95.0, altura_max=altura_max, clareira=cl, seed=4)
        if burj_em:
            OP.burj("burj", burj_em[0] / k, burj_em[1] / k)
    return no_mundo(n, build, cont_u=0.0012)


def mundo_ar(n, nuvens_z=(1400.0, 2600.0), raio_u=22.0, n_nuv=26, tam=(1400, 2800)):
    """acima da cidade (n = 11, 12): chão de campos, nuvens, ar azul"""
    k = 2.0 ** -n
    ceu_dia(dict(chao="#b9c8cf", horizonte="#d6e6f0", meio="#8fbbe0", topo="#2f68b4"))
    def build():
        cena.poly_mesh("chao_largo", [(-60000, -60000, -0.03), (60000, -60000, -0.03), (60000, 60000, -0.03), (-60000, 60000, -0.03)], OP.mat_planeta("campo_m", "#7e9a6a", "#a9a58a", escala=0.00012, limiar=0.5, sombra=0.9))
        for z in nuvens_z:
            OP.nuvens(z, min(raio_u / k, 90000.0), n=n_nuv, seed=int(z), tam=tam)
    return no_mundo(n, build, cont_u=0.002)


# ---------------------------------------------------------------- desenho dos planos
# ======================================================================== FALA 1
@shot("1A", 0.00, 1.10, "E se cada passo", "16 mm, rente ao chão, de baixo para cima", "O tênis do boneco enorme na frente da lente, a rua de bairro de dia e o rosto lá em cima olhando para o próprio pé.")
def p1A():
    mundo_rua(0)
    eu(dict(cabeca=18), dict(boca="reta"))
    cam((0.18, -0.95, 0.14), (0.0, 0.0, 0.75), 16, fstop=4.0, foco=(0.0, -0.05, 0.12))


@shot("1B", 1.10, 2.30, "que você desse", "28 mm, de frente, no peito", "Corpo inteiro, de frente, parado na rua; a moça ao lado na mesma altura que ele e o poste atrás: este é o tamanho de partida.")
def p1B():
    mundo_rua(0)
    eu(dict(cabeca=4), dict(boca="reta"))
    cam_v((0.0, 0.0, 0.95), 2.35, 28, fstop=5.6, foco=(0.0, 0.0, 1.2))


@shot("1C", 2.30, 3.58, "dobrasse a sua altura?", "85 mm, close do rosto", "O olho branco olhando para baixo, para o pé: a pergunta fica no ar.")
def p1C():
    mundo_rua(0)
    eu(dict(cabeca=22), dict(boca="reta", lid=0.1))
    cam_v((0.0, 0.0, 1.6), 0.62, 85, az=8, el=-6, fstop=2.8, foco=(0.0, -0.04, 1.62))


# ======================================================================== FALA 2
@shot("2A", 3.58, 5.00, "Você começa com um metro e oitenta", "28 mm, três quartos", "A régua nasce ao lado do corpo com 1,8 m; a moça está do lado, quase da mesma altura.")
def p2A():
    mundo_rua(0)
    eu(dict(cabeca=2))
    regua_eu(0, lado=1)
    cam_v((0.1, 0.0, 0.95), 2.4, 28, az=-14, fstop=5.6, foco=(0.0, 0.0, 1.0))


@shot("2B", 5.00, 6.40, "Depois do primeiro passo,", "16 mm, rente ao chão, no pé que sobe", "O pé de trás sai do chão e sobe: o passo começa. O outro pé é o que fica no asfalto.")
def p2B():
    mundo_rua(0)
    eu(dict(quadril=(-62, 0), joelho=(78, 4), tornozelo=(24, 0), ombro=(14, -14), cotovelo=(-20, -20), tronco=-2))
    cam((0.55, -1.15, 0.16), (0.0, -0.1, 0.45), 16, fstop=4.0, foco=(0.0, -0.3, 0.4))


@shot("2C", 6.40, 7.50, "são três metros e meio", "16 mm, rente ao chão, no pé que pousa", "O pé pousa e levanta poeira. O corte vem aqui: o plano seguinte nasce deste pé.")
def p2C():
    mundo_rua(1)
    eu(dict(quadril=(-34, 20), joelho=(12, 26), tornozelo=(8, -8), ombro=(14, -14), cotovelo=(-20, -20)), pe=True)
    OP.poeira_pouso(0.0, -0.2, r=0.8)
    cam((0.55, -1.2, 0.14), (0.0, -0.15, 0.4), 16, fstop=4.0, foco=(0.0, -0.2, 0.2))


@shot("2D", 7.50, 8.80, "três metros e meio", "28 mm, corpo inteiro, recuando", "Agora com 3,6 m: ele passa o toldo da loja e a moça chega na cintura. A régua marca o número novo.")
def p2D():
    mundo_rua(1)
    eu(dict(cabeca=4))
    regua_eu(1)
    cam_v((0.0, 0.0, 0.95), 2.4, 28, az=10, fstop=5.6, foco=(0.0, 0.0, 1.0))


# ======================================================================== FALA 3
@shot("3A", 8.80, 9.70, "No segundo passo,", "16 mm, rente ao chão, no pé", "Outro pé pousando, a poeira maior. A rua já está menor em volta.")
def p3A():
    mundo_rua(2)
    eu(dict(quadril=(-34, 20), joelho=(12, 26), tornozelo=(8, -8), ombro=(-14, 14), cotovelo=(-20, -20)))
    OP.poeira_pouso(0.0, -0.2, r=0.8)
    cam((-0.55, -1.2, 0.14), (0.0, -0.15, 0.4), 16, fstop=4.0, foco=(0.0, -0.2, 0.2))


@shot("3B", 9.70, 10.70, "são sete metros", "28 mm, de frente", "7,2 m: a altura de um sobrado de dois andares, ao lado dele, no mesmo tamanho. A régua marca o número.")
def p3B():
    mundo_rua(2)
    no_mundo(2, lambda: OP.sobrado("sobrado", (0.34 + 0.65) / 0.25, 1.0 / 0.25, w=5.2, d=6.0))
    eu(dict(cabeca=2))
    regua_eu(2)
    cam_v((0.2, 0.0, 0.95), 2.5, 24, az=6, fstop=5.6, foco=(0.0, 0.0, 1.0))


@shot("3C", 10.70, 11.48, "sete metros", "24 mm, de cima para baixo", "Ele olha para baixo: a moça virou uma figura pequena, do tamanho da mão dele.")
def p3C():
    mundo_rua(2)
    eu(dict(cabeca=38, ombro=(-10, 12)), dict(boca="reta", lid=0.1))
    cam((0.55, -1.35, 2.05), (-0.25, -0.2, 0.55), 24, fstop=5.6, foco=(-0.47, -0.2, 0.2))


# ======================================================================== FALA 4
@shot("4A", 11.48, 12.70, "No terceiro, são quinze metros.", "28 mm, de frente", "14,4 m: ao lado dele um prédio de cinco andares, da mesma altura.")
def p4A():
    mundo_rua(3)
    predio_ao_lado(3, 5, x_u=0.5, y_u=1.0)
    eu(dict(cabeca=2))
    regua_eu(3)
    cam_v((0.12, 0.0, 0.95), 2.4, 28, az=-7, fstop=5.6, foco=(0.0, 0.0, 1.0))


@shot("4B", 12.70, 13.90, "Se você tropeçar,", "24 mm, lateral, no meio-fio", "O pé da frente enrosca no meio-fio e o corpo vai para a frente, os braços abrindo para se segurar.")
def p4B():
    mundo_rua(3, aberto=True)
    eu(dict(quadril=(-28, 24), joelho=(46, 10), tornozelo=(8, 0), tronco=24, cabeca=10, ombro=(-70, -55), cotovelo=(-22, -22), abre=(18, 18)), dict(boca="o"))
    cam_v((0.0, -0.2, 0.9), 2.3, 24, az=78, fstop=5.6, foco=(0.0, -0.1, 0.9))


@shot("4C", 13.90, 15.40, "leva quase dois segundos para cair.", "24 mm, lateral, câmera lenta", "No ar, em câmera lenta, quase na horizontal. Uma fita ao lado marca a queda: 1,7 s.")
def p4C():
    mundo_rua(3, aberto=True, moca=False)
    h = eu(dict(ombro=(-110, -110), cotovelo=(-8, -8), abre=(12, 12), quadril=(-4, 4), joelho=(6, 6), tronco=-4, cabeca=-12), dict(boca="o"), pe=False)
    h.raiz.rotation_euler.x = math.radians(52); h.raiz.location = (0, 0.1, 0.12)
    OP.texto("t_queda", "1,7 s", 0.3, (0.0, -0.1, 2.0), forca=1.8, rot=(math.pi / 2, 0, math.pi / 2))
    cam_v((0.0, -0.5, 0.85), 2.9, 24, az=80, fstop=5.6, foco=(0.0, -0.4, 0.8))


@shot("4D", 15.40, 17.36, "para cair.", "16 mm, rente ao chão, nas mãos", "As mãos tocam o asfalto e seguram: ele se levanta. Ninguém se machuca; só um pouco de poeira.")
def p4D():
    mundo_rua(3, aberto=True, moca=False)
    h = eu(dict(ombro=(-110, -110), cotovelo=(-6, -6), abre=(8, 8), quadril=(0, 0), joelho=(0, 0), tronco=0, cabeca=-10), dict(boca="reta", lid=0.2), pe=False)
    h.raiz.rotation_euler.x = math.radians(78); h.raiz.location = (0, 0.5, 0.05)
    bpy.context.view_layer.update()
    m = h.punho["F"].matrix_world.translation
    OP.poeira_pouso(m.x, m.y, r=0.5)
    cam((m.x + 0.95, m.y - 0.5, 0.28), (m.x, m.y + 0.15, 0.3), 16, fstop=4.0, foco=(m.x, m.y, 0.1))


# ======================================================================== FALA 5
@shot("5A", 17.36, 18.80, "No quarto, são quase trinta metros.", "24 mm, de frente", "28,8 m: ao lado dele um prédio de dez andares, mais ou menos da mesma altura.")
def p5A():
    mundo_rua(4)
    predio_ao_lado(4, 10, x_u=0.5, y_u=1.0)
    eu(dict(cabeca=2))
    regua_eu(4)
    cam_v((0.3, 0.0, 0.95), 2.5, 24, az=10, fstop=5.6, foco=(0.0, 0.0, 1.0))


@shot("5B", 18.80, 20.40, "Sua voz leva um décimo de segundo", "85 mm, close da boca", "Ele fala 'olá': a boca em O e as primeiras ondas do som saindo para a frente.")
def p5B():
    mundo_rua(4)
    eu(dict(cabeca=2), dict(boca="o"))
    OP.arcos_som((0.0, -0.3, 1.5), n=3, r0=0.04, passo_r=0.03, abertura=48, r_tubo=0.0035)
    cam_v((0.0, 0.0, 1.52), 0.5, 85, az=0, el=0, fstop=2.8, foco=(0.0, -0.1, 1.52))


@shot("5C", 20.40, 22.00, "para chegar aos pés.", "16 mm, lateral, de baixo", "O som desce do rosto ao pé em anéis cada vez mais largos e mais fracos. A régua marca o caminho: 28,8 m.")
def p5C():
    mundo_rua(4, aberto=True, moca=False)
    eu(dict(cabeca=6), dict(boca="o"))
    OP.aneis_som((0.0, 0.0, 1.25), n=7, r0=0.34, passo_r=0.08, dz=-0.2, r_tubo=0.008)
    cam((1.15, -0.9, 0.3), (0.0, 0.0, 0.95), 16, fstop=5.6, foco=(0.0, 0.0, 0.9))


@shot("5D", 22.00, 23.58, "aos pés.", "28 mm, no pé", "Só agora o som chega no pé: o tênis levanta, atrasado em relação à boca.")
def p5D():
    mundo_rua(4, aberto=True, moca=False)
    eu(dict(quadril=(-2, 18), joelho=(0, 22), tornozelo=(-14, 0)), dict(boca="reta"))
    OP.aneis_som((0.0, 0.0, 0.2), n=3, r0=0.3, passo_r=0.1, dz=0.06, r_tubo=0.008)
    cam((0.9, -0.9, 0.2), (0.0, -0.05, 0.14), 28, fstop=4.0, foco=(0.0, -0.05, 0.1))


# ======================================================================== FALA 6
@shot("6A", 23.58, 25.20, "No quinto passo, são quase sessenta metros.", "20 mm, de baixo para cima", "A cabeça passa do topo do prédio de dezoito andares: uma linha âmbar marca o nível do topo dele.")
def p6A():
    mundo_rua(5)
    h, cx, cy, w = predio_ao_lado(5, 18, x_u=0.4, y_u=0.7)
    O3.caixa("linha_topo", (0.9, 0.012, 0.012), O3.brilha(OP.AMBAR, 1.4), None, (0.0, -0.12, 55.0 / 32), chanfro=0.0, contorno=0.0)
    eu(dict(cabeca=-4))
    regua_eu(5)
    cam((-0.7, -2.1, 0.06), (0.25, 0.0, 1.45), 20, fstop=5.6, foco=(0.0, 0.0, 1.0))


@shot("6B", 25.20, 26.90, "Isso é mais alto que um prédio de dezoito andares.", "35 mm, aberto, de frente", "Eles dois lado a lado: o prédio de 55 m e o boneco de 57,6 m. A rua e a moça viraram miniatura.")
def p6B():
    mundo_rua(5)
    predio_ao_lado(5, 18, x_u=0.4, y_u=0.7)
    O3.caixa("linha_topo", (0.9, 0.012, 0.012), O3.brilha(OP.AMBAR, 1.4), None, (0.0, -0.12, 55.0 / 32), chanfro=0.0, contorno=0.0)
    eu(dict(cabeca=2))
    regua_eu(5)
    cam_v((0.3, 0.0, 0.95), 2.7, 35, az=6, fstop=8.0, foco=(0.0, 0.0, 1.0))


def macro_fundo():
    ceu_dia(dict(chao="#c9cfc6", horizonte="#cfe0ea", meio="#b4d2e8", topo="#8db5da"))
    O3.caixa("fundo_macro", (4.0, 0.05, 6.0), OP.M("#a9c4d6", "#8aa8bc", "#d8e8f0"), None, (0.0, 1.4, 0.0), chanfro=0.0, contorno=0.0)


@shot("6C", 26.90, 28.50, "O seu cabelo", "85 mm, macro", "Um fio de cabelo do boneco, gigante, caindo da cabeça preta como um tronco de árvore.")
def p6C():
    macro_fundo()
    esfera("cabeca_macro", 1.7, 0.9, 0.9, OP.M("#0d1020", "#0d1020", "#5a6a8a"), None, (0.0, 0.3, 1.75), contorno=0.0, seg=48, an=24)
    OP.fio_cabelo("fio", (0.0, 0.0, 0.0), 0.5, 3.0, eixo="Z")
    OP.texto("t_fio", "fio: 2,4 mm", 0.2, (0.0, -0.4, -1.85), forca=1.8)
    cam((0.0, -5.2, 0.0), (0.0, 0.0, 0.0), 50, fstop=2.8, foco=(0.0, -0.2, 0.0))


@shot("6D", 28.50, 30.60, "tem a grossura de um palito de dente.", "85 mm, macro", "O fio de cabelo ao lado de um palito de dente de verdade: a mesma grossura.")
def p6D():
    macro_fundo()
    OP.fio_cabelo("fio", (-0.3, 0.0, 0.0), 0.5, 3.4, eixo="Z")
    OP.palito("palito", (0.3, 0.0, 0.0), 0.42, 3.4, eixo="Z")
    OP.texto("t_fio", "fio: 2,4 mm", 0.2, (-0.3, -0.4, -1.8), forca=1.8)
    OP.texto("t_pal", "palito: 2 mm", 0.2, (0.3, -0.4, -2.05), forca=1.8)
    cam((0.0, -5.2, 0.0), (0.0, 0.0, -0.2), 50, fstop=4.0, foco=(0.0, 0.0, 0.0))


@shot("6E", 30.60, 32.72, "de dente.", "50 mm, de baixo, o vento no cabelo", "A cabeça lá em cima com o céu atrás e as linhas do vento passando pelo cabelo.")
def p6E():
    mundo_rua(5)
    eu(dict(cabeca=-6), dict(boca="reta"))
    for i, (z, dx) in enumerate(((1.74, 0.42), (1.66, 0.55), (1.8, 0.62), (1.58, 0.5))):
        O3.caixa(f"vento{i}", (0.5 + 0.12 * i, 0.01, 0.012), O3.brilha("#ffffff", 1.4), None, (dx, 0.35, z), chanfro=0.0, contorno=0.0)
    cam_v((0.0, 0.0, 1.62), 0.9, 50, az=18, el=-16, fstop=2.8, foco=(0.0, -0.02, 1.62))


# ======================================================================== FALA 7
@shot("7A", 32.72, 34.30, "Nessa altura, o coração precisa de mais de uma atmosfera e meia", "50 mm, no peito", "Close no peito do boneco: o coração bate, e arcos vermelhos pulsam para fora da blusa.")
def p7A():
    mundo_rua(5)
    eu(dict(cabeca=2))
    OP.arcos_som((0.07, -0.2, 1.3), n=3, r0=0.1, passo_r=0.06, abertura=180, r_tubo=0.008, cor="#ff5a4a")
    cam_v((0.0, 0.0, 1.3), 0.9, 50, az=8, el=2, fstop=2.8, foco=(0.0, -0.1, 1.3))


@shot("7B", 34.30, 36.40, "de pressão para levar o sangue", "35 mm, corpo inteiro, em seção", "Um encanamento vermelho-escuro sobe do coração até a cabeça, com bolinhas de luz subindo. A fita ao lado mostra a distância: 16 m.")
def p7B():
    mundo_rua(5)
    eu(dict(cabeca=2))
    OP.coracao_tubo(1.6, 1.3, x=0.06, y=-0.2)
    OP.fita(-0.42, 0.5, 0.125, z0=1.3, y=-0.15, rotulo="16 m")
    cam_v((0.0, 0.0, 1.0), 2.4, 35, az=0, fstop=8.0, foco=(0.0, -0.1, 1.2))


@shot("7C", 36.40, 38.76, "até a cabeça.", "35 mm, no manômetro", "Um manômetro grande: o ponteiro sobe até 1,65 atmosfera. O boneco está atrás, desfocado.")
def p7C():
    mundo_rua(5)
    eu(dict(cabeca=2), pe=True)
    OP.manometro("man", (-0.58, -0.7, 1.2), 0.34, 1.65, "1,65 atm", sub="no coração", faixa=(0.0, 2.0), zona_vermelha=1.5)
    cam((-0.1, -2.6, 1.1), (-0.1, 0.0, 1.1), 35, fstop=2.0, foco=(-0.3, -0.35, 1.1))


# ======================================================================== FALA 8
def pe_cidade(n, rotulo, passo_pose, ox=0.0):
    mundo_cidade(n, raio_u=14.0)
    eu(passo_pose)
    OP.poeira_pouso(0.0, -0.2, r=0.8)
    OP.texto("n_pe", rotulo, 0.1, (0.32, -0.75, 0.06), forca=1.9)
    cam((0.7, -1.3, 0.16), (0.0, -0.1, 0.4), 20, fstop=4.0, foco=(0.0, -0.2, 0.2))


PASSO_POUSA = dict(quadril=(-34, 20), joelho=(12, 26), tornozelo=(8, -8), ombro=(14, -14), cotovelo=(-20, -20))


@shot("8A", 38.76, 39.36, "No nono,", "20 mm, rente ao chão, no pé", "Quarto pé numa montagem rápida (sexto passo): a cidade lá embaixo já é uma maquete. Número: 115 m.")
def p8A():
    pe_cidade(6, "115 m", PASSO_POUSA)


@shot("8B", 39.36, 39.96, "", "20 mm, rente ao chão, no pé", "Sétimo passo: 230 m.")
def p8B():
    pe_cidade(7, "230 m", dict(PASSO_POUSA, ombro=(-14, 14)))


@shot("8C", 39.96, 40.56, "", "20 mm, rente ao chão, no pé", "Oitavo passo: 461 m.")
def p8C():
    pe_cidade(8, "461 m", PASSO_POUSA)


@shot("8D", 40.56, 41.16, "", "20 mm, rente ao chão, no pé", "Nono passo: 922 m.")
def p8D():
    pe_cidade(9, "922 m", dict(PASSO_POUSA, ombro=(-14, 14)))


def cena_burj(com_regua=True):
    mundo_cidade(9, burj_em=(0.75, 1.5), clareira=(0.75 * 512, 1.5 * 512, 260.0), raio_u=11.0)
    eu(dict(cabeca=-2))
    O3.caixa("linha_burj", (1.2, 0.012, 0.012), O3.brilha(OP.AMBAR, 1.4), None, (0.35, -0.12, 828.0 / 512), chanfro=0.0, contorno=0.0)
    if com_regua:
        regua_eu(9)
        OP.fita(1.25, 828.0 / 512, 0.2, y=1.5, rotulo="828 m")


@shot("8E", 41.16, 42.80, "você passa o Burj Khalifa,", "35 mm, aberto", "A cidade vira maquete e a torre mais alta do mundo (828 m) aparece ao lado dele, com a régua. A cabeça passa do topo.")
def p8E():
    cena_burj()
    cam_v((0.4, 0.0, 1.0), 3.4, 28, az=2, fstop=8.0, foco=(0.0, 0.0, 1.0))


@shot("8F", 42.80, 44.10, "que tem oitocentos e vinte e oito metros.", "20 mm, grua de baixo", "Da base para o alto: a torre sobe e, depois dela, a cabeça do boneco ainda continua.")
def p8F():
    cena_burj(com_regua=False)
    cam((1.15, -1.4, 0.08), (0.45, 0.8, 1.55), 20, fstop=8.0, foco=(0.7, 1.0, 1.0))


# ======================================================================== FALA 9
@shot("9A", 44.10, 45.70, "No décimo, são quase dois quilômetros:", "20 mm, rente ao chão, no pé", "Décimo passo: o pé pousa e a cidade inteira cabe no chão em volta dele, como uma maquete.")
def p9A():
    mundo_cidade(10, raio_u=14.0)
    eu(PASSO_POUSA)
    OP.poeira_pouso(0.0, -0.2, r=0.8)
    OP.texto("n_pe", "1,8 km", 0.1, (0.32, -0.75, 0.06), forca=1.9)
    cam((0.7, -1.3, 0.16), (0.0, -0.1, 0.4), 20, fstop=4.0, foco=(0.0, -0.2, 0.2))


@shot("9B", 45.70, 47.70, "o cabelo tem a grossura de uma lata de refrigerante", "50 mm, macro", "O fio de cabelo, agora do tamanho de uma lata de refrigerante deitada ao lado dele: 7,7 cm e 6,6 cm.")
def p9B():
    macro_fundo()
    OP.fio_cabelo("fio", (-0.45, 0.0, 0.0), 0.5, 3.4, eixo="Z")
    OP.lata("lata", (0.45, 0.0, 0.0), 0.43, 0.8, eixo="Z")
    OP.texto("t_fio", "fio: 7,7 cm", 0.2, (-0.45, -0.4, -1.8), forca=1.8)
    OP.texto("t_lat", "lata: 6,6 cm", 0.2, (0.45, -0.4, -0.7), forca=1.8)
    cam((0.0, -5.2, 0.0), (0.0, 0.0, -0.2), 50, fstop=4.0, foco=(0.0, 0.0, 0.0))


@shot("9C", 47.70, 49.20, "e a vista chega", "85 mm, close do olho", "O olho branco olhando longe, a cidade pequena lá no fundo.")
def p9C():
    mundo_cidade(10, raio_u=14.0)
    eu(dict(cabeca=-4), dict(boca="reta", lid=0.1))
    cam_v((0.0, 0.0, 1.6), 0.6, 85, az=12, el=-4, fstop=2.8, foco=(0.0, -0.05, 1.62))


@shot("9D", 49.20, 52.80, "a cento e cinquenta quilômetros.", "16 mm, por cima do ombro, alto, giro lento", "O que ele enxerga: da cabeça dele para o horizonte, três anéis de 50, 100 e 150 km no chão, cidades pequenas bem longe.")
def p9D():
    k = 2.0 ** -10
    ceu_dia()
    def build():
        cena.poly_mesh("chao_largo", [(-400000, -400000, -0.03), (400000, -400000, -0.03), (400000, 400000, -0.03), (-400000, 400000, -0.03)],
                       OP.mat_planeta("campo_m", "#8aa37a", "#b9b08e", escala=0.00004, limiar=0.5, sombra=0.9))
        OP.cidade_maquete(2600.0, passo=95.0, altura_max=90.0, ox=0.0, oy=-34000.0, seed=2, clareira=None)
        OP.cidade_maquete(2200.0, passo=95.0, altura_max=70.0, ox=-30000.0, oy=-72000.0, seed=3)
        OP.cidade_maquete(2600.0, passo=95.0, altura_max=90.0, ox=26000.0, oy=-104000.0, seed=5)
        for r_km in (50, 100, 150):
            O3.anel(f"anel{r_km}", r_km * 1000.0, 1300.0, O3.brilha(OP.AMBAR, 1.3), None, (0, 0, 20.0), eixo="Z", seg=360, a0=235, a1=305, contorno=0.0)
    no_mundo(10, build, cont_u=0.0006)
    eu(dict(cabeca=0), sombra=False, loc=(0.0, 0.0, 0.0))
    for r_km, ang in ((50, 270), (100, 252), (150, 288)):
        ru = r_km * 1000.0 * k; a = math.radians(ang)
        OP.texto(f"t{r_km}", f"{r_km} km", 0.2 * r_km, (ru * math.cos(a), ru * math.sin(a) + 0.2 * r_km, 0.07 * r_km), forca=1.9, rot=(math.radians(62), 0, math.pi))
    cam((0.0, 12.0, 40.0), (0.0, -92.0, 0.0), 16, fstop=16.0, foco=100.0)


# ======================================================================== FALA 10
def pe_nuvens(n=12, z=(1500.0, 2900.0)):
    mundo_ar(n, nuvens_z=z, n_nuv=34, raio_u=14.0)


@shot("10A", 52.80, 54.30, "Com doze passos,", "16 mm, rente ao chão, atravessando as nuvens", "O pé pousa e as nuvens passam em volta das pernas: ele já está acima delas.")
def p10A():
    pe_nuvens()
    eu(PASSO_POUSA)
    cam((0.6, -1.1, 0.1), (0.0, -0.1, 0.65), 16, fstop=4.0, foco=(0.0, -0.2, 0.3))


@shot("10B", 54.30, 56.20, "são sete quilômetros.", "24 mm, de frente, nuvens em volta", "7,4 km: o boneco de pé acima de duas camadas de nuvens; a régua marca 7,4 km.")
def p10B():
    pe_nuvens()
    eu(dict(cabeca=2))
    regua_eu(12)
    cam_v((0.0, 0.0, 0.95), 2.6, 24, az=8, fstop=8.0, foco=(0.0, 0.0, 1.0))


@shot("10C", 56.20, 57.90, "Na altura da boca,", "50 mm, no rosto", "Ele respira fundo: o ar sai da boca em fumaça branca. Atrás, só céu e nuvens.")
def p10C():
    pe_nuvens()
    eu(dict(cabeca=-2), dict(boca="o"))
    mp = cena.amat("sopro_m", "#ffffff", 1.0, 0.85, ("radial", 1.1))
    for i, (dx, dy, dz, r) in enumerate(((0.01, -0.15, -0.02, 0.02), (0.02, -0.2, -0.03, 0.03), (0.04, -0.26, -0.04, 0.045), (0.06, -0.32, -0.05, 0.06))):
        cena.disc(f"sopro{i}", r, mp, (dx, dy, 1.46 + dz))
    cam_v((0.1, 0.0, 1.5), 0.9, 50, az=0, el=2, fstop=2.8, foco=(0.0, -0.1, 1.5))


@shot("10D", 57.90, 59.10, "o ar tem menos da metade da pressão do chão.", "35 mm, dois manômetros", "Dois manômetros lado a lado: no chão 1,00 atmosfera, na altura da boca 0,47.")
def p10D():
    ceu_dia(dict(chao="#b9c8cf", horizonte="#d6e6f0", meio="#8fbbe0", topo="#2f68b4"))
    OP.manometro("man_a", (-0.5, 0.0, 1.0), 0.42, 1.0, "1,00 atm", sub="no chão", faixa=(0.0, 1.2), zona_vermelha=9)
    OP.manometro("man_b", (0.5, 0.0, 1.0), 0.42, 0.47, "0,47 atm", sub="na boca", faixa=(0.0, 1.2), zona_vermelha=9)
    cam((0.0, -2.8, 0.95), (0.0, 0.0, 0.95), 35, fstop=8.0, foco=(0.0, 0.0, 1.0))


# ======================================================================== FALA 11
def terra_sob_o_pe(n, y0=0.0, folga=0.0):
    """a Terra de tamanho verdadeiro (raio 6371 km) com o boneco em pé no topo dela"""
    k = 2.0 ** -n
    r = 6371000.0 * k
    OP.terra("terra", r, (0.0, y0, -r - folga))
    return r


@shot("11A", 59.10, 60.90, "No vigésimo primeiro,", "24 mm, de lado, a Terra embaixo", "Vigésimo primeiro passo: ele está em pé em cima da curva da Terra, com a atmosfera fina azul e o céu preto.")
def p11A():
    ceu_espaco()
    terra_sob_o_pe(21)
    eu(dict(cabeca=2))
    cam((2.1, -2.7, 0.7), (0.0, 0.0, 0.5), 24, fstop=8.0, foco=(0.0, 0.0, 0.9))


@shot("11B", 60.90, 63.00, "você já é mais alto que a Lua é larga:", "16 mm, de baixo", "De baixo para cima: a Lua trazida para perto, ao lado dele (comparação fora de escala de distância); ela cabe na altura do corpo.")
def p11B():
    ceu_espaco()
    terra_sob_o_pe(21)
    eu(dict(cabeca=-4))
    OP.lua("lua", 0.83, (1.25, 0.2, 1.1))
    cam((0.5, -1.0, 0.12), (0.4, 0.2, 1.1), 16, fstop=5.6, foco=(0.0, 0.0, 1.0))


@shot("11C", 63.00, 65.98, "três mil quatrocentos e setenta quilômetros.", "35 mm, lado a lado", "O boneco (3.775 km) e a Lua (3.474 km) lado a lado, cada um com a sua régua; o topo dele passa do topo dela.")
def p11C():
    ceu_espaco()
    terra_sob_o_pe(21)
    eu(dict(cabeca=0), sombra=False)
    OP.lua("lua", 0.8685, (1.15, 0.0, 0.8685))
    OP.fita(-0.36, 1.8, 0.2, y=0.0, rotulo="3.775 km", tam_rot=0.2, rot_dx=0.35)
    OP.texto("t_lua_km", "Lua: 3.474 km", 0.2, (1.15, -0.1, 2.0), forca=1.8)
    O3.caixa("linha_lua", (1.3, 0.012, 0.012), O3.brilha(OP.AMBAR, 1.4), None, (0.5, -0.1, 1.737), chanfro=0.0, contorno=0.0)
    cam_v((0.8, 0.0, 1.0), 4.8, 35, az=0, fstop=8.0, foco=(0.5, 0.0, 0.9))


# ======================================================================== FALA 12
@shot("12A", 65.98, 67.60, "No vigésimo terceiro,", "35 mm, rente ao chão, no pé", "O pé quase toca a Terra, que agora cabe inteira embaixo dele.")
def p12A():
    ceu_espaco()
    terra_sob_o_pe(23, folga=0.05)
    eu(dict(quadril=(-30, 22), joelho=(30, 20), tornozelo=(10, -6)), pe=False)
    cam((1.0, -1.0, 0.1), (0.0, -0.05, -0.2), 35, fstop=5.6, foco=(0.0, -0.1, 0.0))


@shot("12B", 67.60, 70.00, "é a vez da Terra:", "24 mm, aberto", "A Terra inteira (12.742 km) com o boneco de pé em cima dela (15.099 km): a cabeça sai do quadro de tão alto.")
def p12B():
    ceu_espaco()
    r = terra_sob_o_pe(23)
    eu(dict(cabeca=2), sombra=False)
    OP.fita(0.95, 2 * r, 2 * r / 6, z0=-2 * r, y=0.0, rotulo="12.742 km", tam_rot=0.2, rot_dx=-0.05)
    OP.fita(-0.36, 1.8, 0.2, y=0.0, rotulo="15.099 km", tam_rot=0.2, rot_dx=0.25)
    cam_v((0.3, 0.0, 0.0), 4.6, 24, az=0, fstop=8.0, foco=(0.0, 0.0, 0.4))


@shot("12C", 70.00, 72.22, "doze mil setecentos e quarenta e dois quilômetros de largura.", "85 mm, close do olho", "A Terra azul refletida no olho branco dele.")
def p12C():
    ceu_espaco()
    terra_sob_o_pe(23)
    h = eu(dict(cabeca=0), dict(boca="reta", lid=0.1), sombra=False)
    bpy.context.view_layer.update()
    pe = h.olhos["F"].matrix_world.translation
    OP.terra("refl", 0.022, (pe.x + 0.0, pe.y - 0.006, pe.z + 0.01))
    cam_v((0.0, 0.0, 1.6), 0.5, 85, az=6, el=-2, fstop=2.8, foco=(pe.x, pe.y, pe.z))


# ======================================================================== FALA 13
def lua_terra_fio(y=-0.5, z=1.25):
    """Terra e Lua na distância verdadeira (384.400 km) com um fio de luz entre elas; o boneco (483.183 km) está atrás"""
    k = 2.0 ** -28
    d = 384400000.0 * k
    OP.terra("terra", 6371000.0 * k, (-d / 2, y, z))
    OP.lua("lua", 1737400.0 * k, (d / 2, y, z))
    O3.caixa("fio_luz", (d, 0.006, 0.006), O3.brilha(OP.AMBAR, 1.5), None, (0.0, y, z), chanfro=0.0, contorno=0.0)
    for i in range(1, 8):
        O3.caixa(f"fio_risco{i}", (0.004, 0.006, 0.05), O3.brilha(OP.AMBAR, 1.5), None, (-d / 2 + i * d / 8, y, z), chanfro=0.0, contorno=0.0)
    return d


@shot("13A", 72.22, 74.40, "E no vigésimo oitavo,", "24 mm, aberto, de frente", "Terra e Lua minúsculas, com um fio de luz entre elas (384.400 km). O boneco, atrás, é maior que a distância.")
def p13A():
    ceu_espaco()
    lua_terra_fio()
    eu(dict(cabeca=0), sombra=False, loc=(0.0, 0.6, 0.0))
    OP.texto("t_dist", "384.400 km", 0.1, (0.0, -0.5, 1.4), forca=1.8)
    for nm, x in (("Terra", -0.716), ("Lua", 0.716)):
        O3.anel(f"mk_{nm}", 0.07, 0.004, O3.brilha("#ffffff", 1.6), None, (x, -0.5, 1.25), eixo="Y", seg=48, contorno=0.0)
        OP.texto(f"t_{nm}", nm, 0.1, (x, -0.5, 1.05), forca=1.6)
    cam_v((0.0, 0.0, 0.9), 3.1, 24, az=0, fstop=11.0, foco=(0.0, 0.0, 1.0))


@shot("13B", 74.40, 76.40, "você passa da distância entre a Terra e a Lua,", "14 mm, colado na mão", "A mão do boneco, de perto, atravessa o fio de luz que liga a Terra à Lua.")
def p13B():
    ceu_espaco()
    d = lua_terra_fio()
    h = eu(dict(ombro=(-92, 12), cotovelo=(-6, -30), abre=(6, 6), cabeca=8), sombra=False)
    cam((0.55, -1.2, 1.35), (0.0, -0.45, 1.22), 14, fstop=8.0, foco=(0.0, -0.45, 1.22))


@shot("13C", 76.40, 78.60, "que é de quase quatrocentos mil quilômetros.", "28 mm, de frente", "Ele de pé, a Terra de um lado dos ombros e a Lua do outro, o fio de luz passando na frente do peito.")
def p13C():
    ceu_espaco()
    lua_terra_fio()
    eu(dict(cabeca=2), sombra=False)
    regua_eu(28, x=-0.42)
    cam_v((0.0, 0.0, 1.0), 2.9, 28, az=0, fstop=11.0, foco=(0.0, 0.0, 1.2))


@shot("13D", 78.60, 80.26, "(fim)", "16 mm, rente ao chão, no pé", "O último plano: o pé pousa no vazio, em silêncio, com a Terra e a Lua pequenas ao fundo. Rima com o primeiro plano.")
def p13D():
    ceu_espaco()
    lua_terra_fio(y=2.0, z=0.6)
    eu(dict(quadril=(-34, 20), joelho=(12, 26), tornozelo=(8, -8), ombro=(14, -14), cotovelo=(-20, -20)), sombra=False)
    OP.texto("n_pe", "483.184 km", 0.075, (0.22, -0.75, -0.04), forca=1.9)
    cam((0.7, -1.3, 0.16), (0.0, -0.1, 0.4), 16, fstop=4.0, foco=(0.0, -0.2, 0.2))


# ---------------------------------------------------------------- main
def main():
    argv = sys.argv[sys.argv.index("--") + 1:]
    if "--list" in argv:
        for k, d in SHOTS.items():
            print(f"{k} | {d['t0']:.2f}-{d['t1']:.2f} | {d['lente']} | {d['palavras']}")
        return
    if "--json" in argv:
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


if __name__ == "__main__":
    main()
