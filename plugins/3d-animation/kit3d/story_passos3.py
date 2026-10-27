"""Storyboard v3 de "E se cada passo dobrasse a sua altura?" (plano: personagem/passos/plano-de-cena-v3.md; pedido de 25/10/2026:
"ele já começa grande, não dá para entender; tem que dar um passo e crescer dentro da cidade; a tela branca quebra a imersão;
quando dá o passo já dá um impacto, cresce quase na hora, num bounce não tão agressivo, faz cara de 'caramba, a cada passo eu cresço',
dá mais um passo e cresce de novo").
Sobrescreve os planos do story_passos2 que mudam (mesmos ids e tempos): a abertura, todas as medições (agora DENTRO do mundo, com lente
longa de longe e a régua de pé no chão), os planos de reação e as vistas pelos olhos dele. O resto vem do v2 sem mudança.
blender -b -P story_passos3.py -- PLANO SAIDA.png [--scale 0.5] | --list | --json ARQ | ... --colisao"""
import os, sys, math, json, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy, lib
from lib import empty
from mathutils import Vector
import cena, props
import objetos3d_abrigo as O3, cidade3d as C3, elenco3d_abrigo as E3
import objetos3d_passos as OP, objetos3d_passos_b as OB
import story_passos as SP
import story_passos2 as S2
import poses_passos as PP
import ik3_abrigo as IK
from heroi3d import esfera, tubo
from poses_passos import _pe

SHOTS = S2.SHOTS
H = S2.H
EU_X0 = -1.2                                              # na abertura ele está na faixa da esquerda, perto da calçada do ponto
S2.LUGAR.update(ponto=(-4.6, -2.6), moca=(-3.4, -3.3))

# a reação ("caramba, eu cresci"): as mãos sobem na frente do peito, palmas para cima, e ele olha para elas
PP.POSES["susto"] = dict(quadril=(-4, 6), joelho=(6, 10), tornozelo=(_pe(-4, 6, 0), _pe(6, 10, 0)), ombro=(-30, -30), cotovelo=(-64, -64),
                         abre=(20, 20), punho=(-20, -20), tronco=-4, cabeca=24, boca="o")
PP.POSES["olha_mao"] = dict(PP.POSES["susto"], cabeca=32, olha=-10, ombro=(-34, -26), cotovelo=(-70, -60))


def refaz(nome, palavras=None, modo="M", lente="", nota=""):
    """troca o desenho de um plano do v2 mantendo o tempo"""
    def deco(fn):
        d = SHOTS[nome]
        d.update(fn=fn, modo=modo, lente=lente, nota=nota)
        if palavras is not None:
            d["palavras"] = palavras
        return fn
    return deco


def tele(alvo=(0.1, 0.0, 0.98), vis=2.9, lente=135, dz=0.04):
    """lente longa de longe, de frente, na altura do meio do corpo: a régua e a cabeça batem (quase sem perspectiva), mas dentro da cidade"""
    d = (vis / 2.0) / (21.333 / lente)
    return S2.cam((alvo[0], alvo[1] - d, alvo[2] + dz), alvo, lente, fstop=16.0, foco=alvo)


def regua_mundo(n, x=-0.42, y=0.05, rotulo=None, marcas=None, cor=None):
    """a fita métrica de pé no chão, à esquerda dele: os números do lado de fora (esquerda) e o número do topo centrado em cima da fita"""
    OB.regua2(-0.42 if x is None else x, 1.8, S2.altura(n), marcas_m=marcas, lado=-1, y=y, rotulo=rotulo, cor_num=cor or OB.AMBAR_ESC, lado_rot=0)


def pov(alvo=(0.0, -1.15, 0.0), lente=12, recuo=0.3, z=1.62):
    """os olhos dele olhando para o próprio pé: a barriga e o tênis embaixo, a cidade em volta"""
    for o in bpy.data.objects:
        if o.name.startswith("eu_") and any(k in o.name for k in ("cranio", "olho", "palpebra", "sobr", "boca", "cabelo", "cab", "gola", "pesc")):
            o.hide_render = True
    S2.cam((0.0, -recuo, z), alvo, lente, fstop=11.0, foco=alvo, clip=0.01)


def rua_abertura(onibus_y=None, corredor_u=None, aberto=0):
    return S2.rua2(1, onibus_y=onibus_y, moca=True, ponto=True, eu_x=EU_X0, corredor_u=corredor_u, aberto=aberto)


# ======================================================================== FALA 1
@refaz("1A", lente="24 mm, na calçada, baixa", nota="Ele no ponto, de tamanho normal, ao lado da moça. Dá um passo e, quando o pé pousa (na palavra 'passo'), cresce na hora, num pulinho: 1,8 m vira 3,6 m. Poeira e tremor.")
def p1A():
    rua_abertura(onibus_y=S2.eu_y(1) + 14.0)
    S2.eu("contato")
    S2.cam((0.55, -1.45, 0.3), (-0.2, 0.0, 0.98), 20, fstop=5.6, foco=(0.0, 0.0, 0.9))


@refaz("1B", lente="50 mm, da altura da moça, de baixo", nota="A reação: ele olha para as próprias mãos, os olhos arregalados, a boca em O: 'caramba, eu cresci'. A câmera está na altura dos olhos da moça.")
def p1B():
    rua_abertura()
    S2.eu("olha_mao")
    S2.cam((0.55, -2.2, 0.82), (0.0, -0.1, 1.32), 50, fstop=2.8, foco=(0.0, -0.1, 1.45))


@refaz("1C", lente="12 mm, pelos olhos dele", nota="Pelos olhos dele: a barriga, o tênis, a moça e o ponto de ônibus agora pequenos ao lado do pé.")
def p1C():
    rua_abertura()
    S2.eu("olha_baixo")
    pov(alvo=(-0.6, -1.7, 0.0), lente=16)


# ======================================================================== FALA 2
@refaz("2A", "Você começa", lente="135 mm, de longe, na rua", nota="Lente longa na rua: ele (3,6 m) ao lado do ponto e da moça, a régua de pé no asfalto.")
def p2A():
    rua_abertura(corredor_u=12.0)
    S2.eu(dict(cabeca=6, olha=-14))
    regua_mundo(1, x=-0.42, marcas=[])
    tele(alvo=(-0.25, 0.0, 0.98), vis=3.0)


@refaz("2B", "com um metro e oitenta", lente="135 mm, na régua", nota="A régua de perto: a marca de 1,8 m acende em âmbar, na altura da moça. Era o tamanho dele antes do passo.")
def p2B():
    rua_abertura(corredor_u=12.0)
    S2.eu(dict(cabeca=6, olha=-14))
    regua_mundo(1, x=-0.42, marcas=[])
    k = 0.5
    OB.caixa("marca18", (0.2, 0.012, 0.01), O3.brilha(OB.AMBAR_ESC, 1.0), (-0.57, 0.02, 1.8 * k), cont=0.0)
    OP.texto("t18", "1,8 m", 0.075, (-0.57, 0.02, 1.8 * k + 0.05), cor=OB.AMBAR_ESC, forca=1.0, alinha="CENTER")
    tele(alvo=(-0.3, 0.0, 1.0), vis=2.4)


@refaz("2C", "Depois do primeiro passo,", lente="135 mm, sobe pela régua", nota="A câmera sobe pela régua, da marca de 1,8 m até a cabeça dele.")
def p2C():
    rua_abertura(corredor_u=12.0)
    S2.eu(dict(cabeca=6, olha=-14))
    regua_mundo(1, x=-0.42, marcas=[])
    OB.caixa("marca18", (0.2, 0.012, 0.01), O3.brilha(OB.AMBAR_ESC, 1.0), (-0.57, 0.02, 0.9), cont=0.0)
    OP.texto("t18", "1,8 m", 0.075, (-0.57, 0.02, 0.95), cor=OB.AMBAR_ESC, forca=1.0, alinha="CENTER")
    tele(alvo=(-0.25, 0.0, 1.35), vis=2.0)


@refaz("2D", "são três", lente="50 mm, de lado", nota="De lado: o ônibus chega no ponto e a cabeça dele fica acima do teto (3,2 m).")
def p2D():
    rua_abertura(onibus_y=S2.eu_y(1) + 7.0, aberto=1)
    S2.eu(dict(cabeca=10, olha=40))
    S2.cam((3.0, -0.6, 0.95), (-0.3, 0.6, 0.95), 35, fstop=8.0, foco=(0.0, 0.0, 1.0))


@refaz("2E", "metros e meio", lente="16 mm, no asfalto, no pé", nota="A câmera no asfalto, colada no tênis: ele levanta o pé para o segundo passo.")
def p2E():
    rua_abertura()
    h = S2.eu("alta")
    f = S2.pe_de(h, "B")
    S2.cam((0.35, -0.75, 0.04), (-0.05, 0.1, 0.9), 16, fstop=4.0, foco=(0.0, -0.1, 0.3), clip=0.003)


# ======================================================================== FALA 3: segundo passo
@refaz("3A", lente="14 mm, no asfalto, ao lado do pé", nota="O pé pousa ao lado da câmera e, no impacto, ele cresce de novo (3,6 m vira 7,2 m), num pulinho. Poeira.")
def p3A():
    S2.rua2(2, extras=("poste",), aberto=1)
    h = S2.eu("contato")
    f = S2.pe_de(h, "F")
    OP.poeira_pouso(f.x, f.y - 0.05, r=0.4)
    S2.cam((f.x + 0.22, f.y - 0.32, 0.02), (f.x - 0.05, f.y + 0.25, 1.4), 14, fstop=4.0, foco=(f.x, f.y, 0.1), clip=0.002)


@refaz("3B", lente="35 mm, rosto, a luminária ao lado", nota="Ele dá de cara com a luminária do poste: olha para ela, surpreso de novo.")
def p3B():
    S2.rua2(2, extras=("poste",), moca=False)
    S2.eu(dict(cabeca=-8, olha=-30), dict(boca="o"))
    S2.cam((-0.6, -1.4, 1.5), (0.35, 0.3, 1.55), 35, fstop=4.0, foco=(0.0, -0.05, 1.6))


@refaz("3C", "sete metros.", lente="135 mm, de longe, na rua", nota="Lente longa: ele de 7,2 m ao lado do poste de 7,2 m, com a régua de pé no asfalto.")
def p3C():
    S2.rua2(2, extras=("poste",), moca=False, corredor_u=12.0)
    S2.eu(dict(cabeca=2))
    regua_mundo(2, marcas=[2.0, 4.0, 6.0])
    tele(alvo=(0.1, 0.0, 0.98), vis=3.1)


# ======================================================================== FALA 4
@refaz("4B", "são quinze metros.", lente="135 mm, de longe, na rua", nota="Lente longa: 14,4 m ao lado do prédio de 5 andares (15 m), com a régua de pé no asfalto.")
def p4B():
    S2.rua2(3, extras=("p5",), corredor_u=12.0)
    S2.eu(dict(cabeca=2))
    regua_mundo(3, marcas=[5.0, 10.0])
    tele(alvo=(0.1, 0.0, 0.98), vis=3.1)


# ======================================================================== FALA 5
@refaz("5B", "são quase trinta metros.", lente="135 mm, de longe, na rua", nota="Lente longa: 28,8 m ao lado do prédio de 10 andares (30 m), com a régua.")
def p5B():
    S2.rua2(4, extras=("p10",), corredor_u=12.0)
    S2.eu(dict(cabeca=2))
    regua_mundo(4, marcas=[10.0, 20.0])
    tele(alvo=(0.15, 0.0, 0.98), vis=3.1)


# ======================================================================== FALA 6
@refaz("6B", "são quase sessenta metros.", lente="135 mm, de longe, na rua", nota="Lente longa: 57,6 m ao lado do prédio de 18 andares (55 m); a linha âmbar no topo do prédio; a cabeça passa.")
def p6B():
    S2.rua2(5, extras=("p18",), corredor_u=12.0)
    S2.eu(dict(cabeca=2))
    regua_mundo(5, marcas=[20.0, 40.0])
    x, y, w = S2.LUGAR["p18"]; k = 2.0 ** -5
    OB.caixa("linha_topo", (0.95, 0.01, 0.008), O3.brilha(OB.AMBAR_ESC, 1.0), (0.3, 0.1, 54.0 * k), cont=0.0)
    tele(alvo=(0.15, 0.0, 0.98), vis=3.1)


@refaz("6E", lente="100 mm, no balancim, de perto", nota="Na mão do limpador, de perto: o palito de dente ao lado do fio solto do cabelo do gigante. A mesma grossura. A cidade desfocada lá embaixo.")
def p6E():
    S2.mundo_metros()
    x, y, w = 26.0, 18.0, 20.0
    estado = {}
    def limp(px, py, pz, rz):
        h = E3.faz("limpador", "limp"); h.raiz.scale = (S2.EU_ESC,) * 3
        h.pose(**h.pe_no_chao(**dict(SP.STAND))); h.raiz.location = (px, py, pz); h.raiz.rotation_euler.z = rz
        PP.assenta(h, pz); estado["h"] = h
    OB.predio_alto("p18", x, y, 18, w=w, cor="#8f98a6", balancim=True, face_balancim="esq", limpador=limp)
    g = S2.gigante(5, dict(cabeca=2, olha=24), dict(boca="reta"))
    bpy.context.view_layer.update()
    lh = estado["h"]
    ombro = lh.ombro["F"].matrix_world.translation
    ponta = Vector((ombro.x - 0.5, ombro.y - 0.05, ombro.z + 0.16))
    c = g.cabeca.matrix_world.translation + Vector((0, 0, g.R * 32 * S2.EU_ESC))
    raiz_fio = c + Vector((g.R * 32 * S2.EU_ESC * 0.92, 0.0, g.R * 32 * S2.EU_ESC * 0.25))
    P = IK.braco_pose(lh, "F", tuple(ponta + Vector((0.05, 0.0, -0.07))), dict(getattr(lh, "_ultima", {})), nome="limp")
    lh.pose(**P); lh.rosto(boca="o", lid=0.0); bpy.context.view_layer.update()
    m = lh.punho["F"].matrix_world.translation
    pc = Vector((m.x - 0.02, m.y - 0.055, m.z + 0.105))                   # o palito de pé acima do punho, na frente dele (o punho não cobre)
    OP.palito("palito", tuple(pc), 0.002, 0.065, eixo="Z")
    fim = pc + Vector((-0.0045, 0.0, 0.0))                                   # a ponta do fio solto fica colada ao lado do palito: mesma grossura
    tubo("fio_solto", [tuple(raiz_fio), tuple(raiz_fio.lerp(fim, 0.5) + Vector((0, 0, 0.6))), tuple(fim + Vector((-0.08, 0, 0.0))), tuple(fim)],
         [0.0012] * 4, OP.M("#2a1c16", "#120c09", "#6a4a3a"), None, seg=10, tampa=4, contorno=0.0)
    OP.texto("t_fio", "fio: 2,4 mm", 0.0065, (pc.x - 0.04, pc.y - 0.02, pc.z + 0.05), cor=OP.AMBAR, forca=1.6, alinha="CENTER")
    OP.texto("t_pal", "palito: 2 mm", 0.0065, (pc.x + 0.04, pc.y - 0.02, pc.z + 0.05), cor=OP.AMBAR, forca=1.6, alinha="CENTER")
    S2.cam((pc.x - 0.02, pc.y - 0.4, pc.z + 0.02), (pc.x - 0.0, pc.y, pc.z + 0.0), 65, fstop=4.0, foco=(pc.x - 0.02, pc.y, pc.z), clip=0.005)


# ======================================================================== FALA 7: o raio X acontece no corpo, na rua
def raio_x_rua(n=5):
    S2.rua2(n, extras=("p18",), moca=False)
    h = S2.eu(nome="eu"); OB.raio_x(h)
    zc = 0.72 * H
    OB.coracao("cor", (0.05, -0.02, zc), s=1.0)
    tubo("vaso", [(0.05, -0.02, zc + 0.05), (0.04, -0.01, zc + 0.2), (0.0, 0.0, 1.5), (0.0, 0.0, 1.66)], [0.014] * 4, O3.brilha("#ff4a3a", 1.6), None, seg=16, tampa=4, contorno=0.0)
    for i in range(6):
        u = (i + 0.5) / 6
        esfera(f"pulso{i}", 0.018, 0.018, 0.024, O3.brilha("#ffd0c0", 2.0), None, (0.05 - 0.05 * u, -0.015, zc + 0.06 + (1.62 - zc - 0.06) * u), contorno=0.0, seg=12, an=8)
    return h, zc


@refaz("7B", modo="M", lente="50 mm, raio X na rua", nota="Ali mesmo na rua, o corpo dele fica translúcido: o coração vermelho bate e um manômetro ao lado sobe até 1,65 atm.")
def p7B():
    h, zc = raio_x_rua()
    OP.manometro("man", (0.5, -0.25, zc), 0.2, 1.65, "1,65 atm", faixa=(0.0, 2.0), zona_vermelha=1.5)
    tubo("mangueira", [(0.08, -0.04, zc), (0.22, -0.14, zc - 0.06), (0.33, -0.22, zc)], [0.007] * 3, OP.M("#3a3f46"), None, seg=10, tampa=4, contorno=0.002)
    S2.cam((0.35, -2.4, 1.25), (0.22, 0.0, 1.2), 50, fstop=5.6, foco=(0.1, -0.1, 1.25))


@refaz("7C", modo="M", lente="85 mm, raio X na rua", nota="O sangue sobe em pulsos do coração até a cabeça; a chave âmbar ao lado mostra a distância: 16 m.")
def p7C():
    h, zc = raio_x_rua()
    OB.caixa("chave_16", (0.012, 0.012, H - zc), O3.brilha(OP.AMBAR, 1.5), (-0.3, -0.05, (H + zc) / 2), cont=0.0)
    for z in (zc, H):
        OB.caixa(f"chave_p{z:.2f}", (0.06, 0.012, 0.012), O3.brilha(OP.AMBAR, 1.5), (-0.27, -0.05, z), cont=0.0)
    OP.texto("t16", "16 m", 0.09, (-0.34, -0.05, (H + zc) / 2), alinha="RIGHT")
    S2.cam((-0.14, -2.6, 1.42), (-0.14, 0.0, 1.42), 50, fstop=5.6, foco=(0.0, -0.1, 1.5))


# ======================================================================== FALA 8: o Burj de pé na cidade, ao lado dele
def cidade_burj(n=9, burj=(0.75, 1.6)):
    k = 2.0 ** -n
    SP.ceu_dia()
    def b():
        OP.chao("#8f9a8a", None, 40000.0, nome="chao_largo")
        OP.cidade_maquete(4200.0, passo=95.0, altura_max=130.0, clareira=[(0, 0, 0.35 / k), (burj[0] / k, burj[1] / k, 300.0)], seed=4)
        OB.burj("burj", burj[0] / k, burj[1] / k)
    SP.no_mundo(n, b, cont_u=0.0012)
    return k


@refaz("8E", "Burj Khalifa,", lente="135 mm, de longe, na cidade", nota="Na cidade, de longe: o Burj Khalifa (828 m) de pé ao lado dele (922 m), a linha âmbar no topo da agulha; a cabeça passa.")
def p8E():
    k = cidade_burj()
    S2.eu(dict(cabeca=0, olha=24))
    regua_mundo(9, marcas=[300, 600])
    OB.caixa("linha_burj", (0.55, 0.01, 0.008), O3.brilha(OB.AMBAR_ESC, 1.0), (0.45, 0.4, 828.0 * k), cont=0.0)
    OB.rotulo_ref(0.45, 828.0 * k + 0.05, "Burj: 828 m", tam=0.08, y=0.38, cor=OB.AMBAR_ESC)
    tele(alvo=(0.1, 0.0, 0.98), vis=3.1)


@refaz("8F", "que tem oitocentos e vinte e oito metros.", lente="85 mm, sobe pela torre até a agulha", nota="A câmera sobe pela torre, na cidade, até a ponta da agulha, que fica na altura do rosto dele; ele olha para ela.")
def p8F():
    k = cidade_burj(burj=(0.42, 1.6))
    S2.eu(dict(olha=34, cabeca=6), dict(boca="reta"))
    z = 828.0 * k
    S2.cam((0.18, -5.2, z), (0.2, 0.0, z), 85, fstop=5.6, foco=(0.1, 0.0, z))


# ======================================================================== FALA 9
@refaz("9B", "são quase dois quilômetros:", lente="135 mm, de longe, na cidade", nota="Lente longa: 1,8 km, de pé na cidade; o Burj agora na altura do joelho; a régua.")
def p9B():
    k = cidade_burj(n=10, burj=(0.55, 1.2))
    S2.eu(dict(cabeca=2))
    regua_mundo(10, marcas=[500, 1000, 1500])
    OB.rotulo_ref(0.45, 828.0 * k + 0.04, "Burj: 828 m", tam=0.07, y=0.8, cor=OB.AMBAR_ESC)
    tele(alvo=(0.1, 0.0, 0.98), vis=3.1)


@refaz("9C", "o cabelo tem a grossura de uma lata de refrigerante", lente="85 mm, no ombro dele", nota="No ombro dele, de perto: uma lata de refrigerante de verdade ao lado de um fio de cabelo da mesma grossura; a cidade desfocada lá embaixo.")
def p9C():
    SP.ceu_dia(dict(chao="#c9cfc6", horizonte="#d6e6f0", meio="#a9cde6", topo="#4f86c4"))
    OP.chao("#8f9a8a", None, 40000.0, nome="chao_largo")
    esfera("ombro", 4.0, 2.2, 1.4, OP.M(E3.ESPEC["eu"]["roupa"], E3.ESPEC["eu"]["escura"], OP.BD), None, (0.0, 0.6, -1.25), contorno=0.0, seg=64, an=32)
    esfera("nuca", 1.9, 1.9, 1.9, OP.M("#0d1020", "#0d1020", "#5a6a8a"), None, (-1.6, 1.6, 1.4), contorno=0.0, seg=64, an=32)
    OB.fio_escamas("fio", (-0.42, 0.0, 0.85), 0.62, 2.6, eixo="Z", n=9)
    OP.lata("lata", (0.42, 0.0, 0.62), 0.53, 1.0, eixo="Z")
    OP.texto("t_fio", "fio: 7,7 cm", 0.13, (-0.04, -0.4, 2.3), cor=OP.AMBAR, forca=1.6, alinha="RIGHT")
    OP.texto("t_lat", "lata: 6,6 cm", 0.13, (0.08, -0.4, 1.3), cor=OP.AMBAR, forca=1.6, alinha="LEFT")
    S2.cam((0.0, -5.4, 1.0), (0.0, 0.0, 1.0), 50, fstop=4.0, foco=(0.0, -0.1, 1.0))


@refaz("9D", lente="12 mm, pelos olhos dele", nota="Pelos olhos dele, com 1,8 km: a barriga, o tênis e a cidade inteira em volta, até o horizonte.")
def p9D():
    SP.mundo_cidade(10, raio_u=30.0, clareira=None, livre=0.3)
    S2.eu("olha_baixo")
    pov(alvo=(0.0, -1.2, 0.0), lente=12)


@refaz("9E", lente="24 mm, por cima do ombro", nota="Do alto, por cima do ombro: uma linha âmbar sai dos olhos dele e vai até o horizonte: 150 km.")
def p9E():
    n = 10; k = 2.0 ** -n
    SP.mundo_cidade(n, raio_u=30.0, clareira=None)
    S2.eu(dict(cabeca=4))
    dist = 150000.0 * k
    alvo = Vector((0.0, -dist, 0.0))
    tubo("visao", [(0.0, -0.32, 1.64), tuple(alvo)], [0.012, 0.6], O3.brilha(OP.AMBAR, 1.6), None, seg=10, tampa=2, contorno=0.0)
    OP.texto("t150", "150 km", 2.4, (0.0, -dist * 0.5, 4.0), cor=OP.AMBAR, forca=1.8, rot=(math.radians(70), 0, math.pi))
    S2.cam((0.55, 0.8, 2.6), (-0.4, -30.0, -0.8), 24, fstop=11.0, foco=(0.0, 0.0, 1.5))


# ======================================================================== FALA 10
@refaz("10B", "são sete quilômetros.", lente="135 mm, de longe, no céu", nota="Lente longa no céu: 7,4 km, as nuvens na altura do joelho, um avião de cruzeiro (10 km) acima da cabeça, a régua.")
def p10B():
    n = 12; k = 2.0 ** -n
    SP.mundo_ar(n, nuvens_z=(1500.0, 2900.0), raio_u=10.0, n_nuv=60)
    S2.eu(dict(cabeca=2))
    regua_mundo(n, marcas=[2000, 4000, 6000], rotulo="7,4 km")
    OB.aviao("av", (0.5, 1.0, 10000.0 * k), s=0.004, rot=-90)
    OB.rotulo_ref(0.22, 10000.0 * k - 0.13, "avião: 10 km", tam=0.075, y=0.9, cor=OB.AMBAR_ESC)
    tele(alvo=(0.15, 0.0, 1.15), vis=3.2)


@refaz("10D", "o ar tem menos da metade da pressão do chão.", lente="85 mm, no céu", nota="No céu, ao lado dele: pontinhos de ar densos embaixo e ralos na altura da boca; dois manômetros: no chão 1,00 atm, na boca 0,47 atm.")
def p10D():
    n = 12
    SP.mundo_ar(n, nuvens_z=(1500.0, 2900.0), raio_u=10.0, n_nuv=60)
    S2.eu()
    rnd = random.Random(3); m = O3.brilha("#ffffff", 1.3)
    Hs = 8000.0 * 2.0 ** -n
    for i in range(420):
        z = -Hs * math.log(1.0 - rnd.random() * (1.0 - math.exp(-1.8 / Hs)))
        esfera(f"ar{i}", 0.008, 0.008, 0.008, m, None, (rnd.uniform(0.42, 0.62), rnd.uniform(-0.2, 0.2), z), contorno=0.0, seg=6, an=4)
    zb = 0.85 * H
    OP.manometro("m_chao", (0.7, -0.25, 0.3), 0.17, 1.0, "1,00", sub="chão", faixa=(0.0, 1.2), zona_vermelha=9)
    OP.manometro("m_boca", (0.7, -0.25, zb), 0.17, 0.47, "0,47", sub="boca", faixa=(0.0, 1.2), zona_vermelha=9)
    OB.caixa("linha_boca", (0.5, 0.01, 0.008), O3.brilha(OB.AMBAR_ESC, 1.0), (0.4, -0.3, zb), cont=0.0)
    tele(alvo=(0.25, 0.0, 0.98), vis=2.6, lente=85)


# ======================================================================== FALA 11-13: comparações no espaço de verdade
def espaco_sobre_terra(n, folga=0.03):
    SP.ceu_espaco()
    return SP.terra_sob_o_pe(n, folga=folga)


@refaz("11C", "que a Lua é larga: três mil quatrocentos e setenta quilômetros.", lente="135 mm, no espaço", nota="No espaço, em pé sobre a Terra: a Lua trazida para o lado dele para comparar; o topo dele passa o topo dela; a régua.")
def p11C():
    n = 21; k = 2.0 ** -n
    espaco_sobre_terra(n)
    S2.eu()
    r = 1737400.0 * k
    OP.lua("lua", r, (0.62, 2.2, r))
    regua_mundo(n, marcas=[], rotulo="3.775 km", cor=OP.AMBAR)
    OB.rotulo_ref(0.36, 2 * r, "Lua: 3.474 km", tam=0.085, y=0.3, cor=OP.AMBAR)
    tele(alvo=(0.1, 0.0, 0.95), vis=3.1)


@refaz("12B", "é a vez da Terra: doze mil setecentos e quarenta e dois", lente="135 mm, no espaço", nota="No espaço, de lado: ele em pé em cima da Terra inteira; a régua da Terra (12.742 km) e a dele (15.099 km).")
def p12B():
    n = 23
    r = espaco_sobre_terra(n)
    S2.eu(dict(cabeca=2), sombra=False)
    OP.fita(0.95, 2 * r, 2 * r / 6, z0=-2 * r - 0.03, y=0.0, rotulo="Terra: 12.742 km", tam_rot=0.17, rot_dx=-0.15)
    regua_mundo(n, marcas=[5000000, 10000000], rotulo="15.099 km", cor=OP.AMBAR)
    tele(alvo=(0.3, 0.0, 0.1), vis=4.4)


@refaz("13B", "você passa da distância entre a Terra e a Lua,", lente="135 mm, no espaço", nota="De longe, de lado: ele em pé sobre a Terra minúscula, a Lua na órbita na altura do peito; a linha âmbar da Terra até a Lua: 384.400 km.")
def p13B():
    SP.ceu_espaco()
    p = S2.terra_lua_orbita(lua_t=1.19)
    S2.eu(sombra=False)
    regua_mundo(28, marcas=[], rotulo="483.184 km", cor=OP.AMBAR)
    tubo("dist", [(0.0, -0.01, -0.03), tuple(p)], [0.004, 0.004], O3.brilha(OP.AMBAR, 1.4), None, seg=8, tampa=2, contorno=0.0)
    OP.texto("t_dist", "384.400 km", 0.07, (p.x + 0.04, p.y - 0.02, p.z / 2), cor=OP.AMBAR, forca=1.6, alinha="LEFT")
    tele(alvo=(0.0, 0.0, 0.95), vis=3.3)


def main():
    S2.main()


if __name__ == "__main__":
    main()
