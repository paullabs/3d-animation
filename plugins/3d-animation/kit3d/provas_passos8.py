"""Provas do replanejamento v15 de "os passos" (pedido de 26/10/2026: "segue para os planos que faltam, 8E em diante, no mesmo padrão").
Diagnóstico quadro a quadro do v14 (8E ao fim):
  8E/8F  régua em palco, texto âmbar pequeno; 8F corta o Burj e não diz 828 m           -> UM plano de lado, os dois na mesma rua, a câmera chega ao topo;
  9A/9B  chão cinza vazio, três bonecos borrados; 9B repete a composição do 8E            -> UM plano: a mesma vista de lado, ele pisa e dobra, o Burj fica no quadril;
  9C     o "cabelo" é uma pilha de discos marrons num fundo preto; não se lê              -> um homem de 1,8 m no telhado segura a lata ao lado do fio que desce do céu;
  10A/10B chão cinza vazio; depois palco com "avião: 10 km" ilegível                      -> UM plano de lado nas nuvens: pisa em "doze", as nuvens no joelho, o avião marcado;
  13A    ele minúsculo dentro de uma elipse: não se entende                                -> de perto: o tênis pousa em cima da Terra, que é menor que o tênis;
  13B/13C a Lua não aparece; uma régua e linhas soltas                                    -> UM plano de lado: a Terra e a Lua marcadas, a linha da distância desenha e
                                                                                              gira até ficar de pé ao lado dele: a cabeça passa a ponta.
Ficam como estão: 11A, 12A, 12B, 12C, 13D.
blender -b -P provas_passos8.py -- PROVA SAIDA.png [--scale 0.5]  |  --list"""
import os, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy, lib
from mathutils import Vector
import story_passos8 as S8                                  # o filme até aqui (v14)
import story_passos2 as S2
import story_passos as SP
import provas_passos7 as P7
import provas_passos5 as PV
import objetos3d_passos as OP, objetos3d_passos_b as OB
import objetos3d_abrigo as O3
import elenco3d_abrigo as E3
import poses_passos as PP
from heroi3d import tubo, esfera

PROVAS = {}
AM = P7.AMARELO
BURJ_M = (0.75 * 512, 1.6 * 512)                            # onde o Burj fica, em metros (o mesmo lugar do 8A)


def prova(nome, titulo):
    def d(fn):
        PROVAS[nome] = (titulo, fn); return fn
    return d


def lateral(alvo, vis, lente=135):
    """câmera de lado (em -x), lente longa: quase sem perspectiva, a altura de cada coisa no quadro é a verdadeira"""
    d = vis * lente / 36.0
    return S2.cam((alvo[0] - d, alvo[1], alvo[2]), alvo, lente, fstop=16.0, foco=alvo), (alvo[0] - d, alvo[1], alvo[2])


def cam_par(n, vis, z, lente=300, sep_deg=15.0, frac=0.5):
    """câmera de frente-esquerda ao longo da linha entre ele e o Burj, girada sep_deg: os dois ficam lado a lado no quadro, com o Burj atrás e à esquerda.
    Lente muito longa (300 mm, longe) para a diferença de distância quase não mudar o tamanho (menos de 5%)"""
    k = 2.0 ** -n
    B = Vector((BURJ_M[0] * k, BURJ_M[1] * k, 0.0))
    L = B.normalized()
    a = math.radians(sep_deg)
    v = Vector((L.x * math.cos(a) - L.y * math.sin(a), L.x * math.sin(a) + L.y * math.cos(a), 0.0))
    M = B * frac
    alvo = Vector((M.x, M.y, z))
    d = vis * lente / 36.0
    loc = alvo - v * d
    return S2.cam(tuple(loc), tuple(alvo), lente, fstop=22.0, foco=(0.0, 0.0, z)), tuple(loc)


def chave_y(nome, x, y0, y1, z, larg, cor=AM):
    """chave horizontal ao longo de y (para a câmera de lado)"""
    m = O3.brilha(cor, 1.5)
    OB.caixa(nome, (larg, abs(y1 - y0), larg), m, (x, (y0 + y1) / 2, z), cont=0.0)
    for k, y in enumerate((y0, y1)):
        OB.caixa(f"{nome}_p{k}", (larg, larg, larg * 6), m, (x, y, z - larg * 2.5), cont=0.0)


def anel_marca(nome, centro, r, cor="#ffffff"):
    """um anel em volta de algo pequeno demais para se ver (a Terra e a Lua ao lado dele, o avião), virado para a câmera de lado"""
    return O3.anel(nome, r, r * 0.06, O3.brilha(cor, 1.8), None, centro, eixo="X", seg=64, contorno=0.0)


def cidade(n, livre_m):
    """a cidade e o Burj no mesmo lugar do 8A; a clareira em volta dele cresce com a passada"""
    k = 2.0 ** -n
    SP.ceu_dia()
    def b():
        OP.chao("#8f9a8a", None, 40000.0, nome="chao_largo")
        OP.cidade_maquete(4200.0, passo=95.0, altura_max=130.0, clareira=[(0, 0, livre_m), (BURJ_M[0], BURJ_M[1], 300.0)], seed=4)
        OB.burj("burj", BURJ_M[0], BURJ_M[1])
    SP.no_mundo(n, b, cont_u=0.0012)
    return k


# ======================================================================== 8E: ele (922 m) e o Burj (828 m), de lado
def ele_e_burj(n=9):
    k = cidade(n, 0.75 / 2 ** -9)
    S2.eu(dict(cabeca=-4, olha=-30), rosto=dict(boca="o"))
    zb = 828.0 * k
    return k, zb


@prova("E1", "8E · 40,6 s \"Burj Khalifa,\": de lado, os dois na mesma rua; a caixa do Burj (828 m) e a dele (922 m)")
def p_e1():
    k, zb = ele_e_burj()
    yb = BURJ_M[1] * k
    c, cl = cam_par(9, 2.5, 1.0, sep_deg=24.0)
    P7.pilula_cam("p_burj", "Burj Khalifa: 828 m", (0.75, yb, zb + 0.13), 0.07, cl)
    P7.pilula_cam("p_ele", "ele: 922 m", (0.0, -0.05, 1.8 + 0.13), 0.07, cl)


@prova("E2", "8E · 43,4 s \"...oitocentos e vinte e oito metros\": a câmera chega ao topo: a ponta da agulha fica abaixo do queixo dele")
def p_e2():
    k, zb = ele_e_burj()
    yb = BURJ_M[1] * k
    c, cl = cam_par(9, 1.05, 1.68, sep_deg=10.0, frac=0.45)
    xb = 0.75
    for j in range(8):                                                  # a linha tracejada na altura da ponta do Burj, da agulha até ele
        if j % 2 == 0:
            p = Vector((xb, yb, zb)).lerp(Vector((0.0, 0.0, zb)), (j + 0.5) / 8)
            OB.caixa(f"nivel{j}", (0.025, 0.025, 0.006), O3.brilha("#ffffff", 1.6), tuple(p), cont=0.0)
    P7.pilula_cam("p_burj", "828 m", (xb, yb, zb + 0.07), 0.04, cl)
    P7.pilula_cam("p_ele", "922 m", (0.0, -0.05, 1.86), 0.04, cl)


# ======================================================================== 9A: o décimo passo, a mesma vista
@prova("D", "9A · 45,9 s \"...quase dois quilômetros\": a mesma vista de lado; ele pisou e dobrou: 1,8 km; o Burj agora bate no quadril dele")
def p_d():
    n = 10
    k = cidade(n, 0.85 / 2 ** -10)
    S2.eu(dict(cabeca=-14, olha=-20), rosto=dict(boca="o"))
    yb = BURJ_M[1] * k
    c, cl = cam_par(10, 2.5, 1.0, sep_deg=30.0)
    P7.pilula_cam("p_burj", "Burj: 828 m", (BURJ_M[0] * k, yb, 828.0 * k + 0.12), 0.07, cl)
    P7.pilula_cam("p_ele", "ele: 1,8 km", (0.0, -0.05, 1.8 + 0.13), 0.075, cl)


# ======================================================================== 9C: o fio de cabelo e a lata
def fio_cabelo(nome, base, raio, alto=3.0):
    """o fio de cabelo dele (7,7 cm de grossura) descendo do céu: castanho escuro com um brilho comprido de um lado e a ponta afinando"""
    pts = [base + Vector((0.18, 0.0, alto)), base + Vector((0.08, 0.0, alto * 0.5)), base + Vector((0.01, 0.0, 0.35)), base]
    tubo(nome, [tuple(p) for p in pts], [raio, raio, raio, raio * 0.8], OP.M("#3b2418", "#1e120b", "#8a6248"), None, seg=28, tampa=6, contorno=0.004)
    tubo(nome + "_brilho", [tuple(p + Vector((-raio * 0.55, -raio * 0.55, 0))) for p in pts[:3]], [raio * 0.16] * 3, O3.brilha("#b48a6a", 1.1), None, seg=10, tampa=2, contorno=0.0)


@prova("C", "9C · 48,6 s \"o cabelo tem a grossura de uma lata\": no telhado, um homem segura a lata ao lado do fio que desce do céu; 7,7 cm e 6,6 cm")
def p_c():
    import ik3_abrigo as IK
    S2.mundo_metros()
    OB.caixa("telhado", (6.0, 6.0, 0.4), OP.M("#c9c2b0", "#9e978a"), (0.0, 1.5, 19.8), cont=0.01)
    OB.caixa("parapeito", (6.0, 0.25, 1.0), OP.M("#d8d2c2", "#aaa394"), (0.0, -1.35, 20.5), cont=0.01)
    h = E3.faz("viz1", "homem"); h.raiz.scale = (S2.EU_ESC,) * 3
    h.pose(**h.pe_no_chao(**dict(SP.STAND))); h.raiz.location = (-0.45, 0.4, 20.0); h.raiz.rotation_euler.z = math.radians(-20)      # de frente para a câmera (o boneco nasce olhando para -y)
    PP.assenta(h, 20.0); bpy.context.view_layer.update()
    alvo = Vector((-0.12, 0.05, 21.3))
    P = IK.braco_pose(h, "F", tuple(alvo), dict(getattr(h, "_ultima", {})), nome="homem")
    h.pose(**P); h.rosto(boca="o", lid=0.0); bpy.context.view_layer.update()
    m = h.punho["F"].matrix_world.translation
    lata = Vector((m.x + 0.02, m.y - 0.03, m.z + 0.075))
    OP.lata("lata", tuple(lata), 0.033, 0.122, eixo="Z")
    fio_cabelo("fio", Vector((lata.x + 0.12, lata.y, lata.z - 0.32)), 0.0385)
    cam = (lata.x + 0.02, lata.y - 1.7, lata.z - 0.05)
    P7.pilula_cam("p_fio", "cabelo dele: 7,7 cm", (lata.x + 0.1, lata.y - 0.1, lata.z + 0.5), 0.04, cam)
    P7.pilula_cam("p_lata", "lata: 6,6 cm", (lata.x + 0.02, lata.y - 0.12, lata.z - 0.16), 0.04, cam)
    S2.cam(cam, (lata.x + 0.02, lata.y, lata.z - 0.05), 50, fstop=4.0, foco=tuple(lata), clip=0.01)


# ======================================================================== 10A: doze passos, nas nuvens
@prova("N", "10A · 54,6 s \"...são sete quilômetros\": de lado, as nuvens no joelho; o avião (10 km) marcado acima da cabeça; caixa 7,4 km")
def p_n():
    n = 12; k = 2.0 ** -n
    SP.mundo_ar(n, nuvens_z=(1500.0, 2900.0), raio_u=10.0, n_nuv=60)
    S2.eu(dict(cabeca=-10, olha=-10), rosto=dict(boca="o"))
    za = 10000.0 * k
    av = Vector((0.0, -0.55, za))
    OB.aviao("aviao", tuple(av), s=1.0 * k * 1.0, rot=90)
    c, cl = lateral((0.0, -0.15, 1.3), 3.1)
    anel_marca("anel_av", (av.x - 0.02, av.y, av.z), 0.06)
    tubo("rastro", [(0.0, av.y + 0.02, za), (0.0, av.y + 0.9, za + 0.02)], [0.0035, 0.0012], O3.brilha("#ffffff", 1.4), None, seg=8, tampa=2, contorno=0.0)   # o rastro branco do avião
    P7.pilula_cam("p_av", "avião: 10 km", (0.0, av.y, za + 0.16), 0.07, cl)
    P7.pilula_cam("p_ele", "ele: 7,4 km", (0.0, 0.3, 1.8 + 0.1), 0.07, cl)


# ======================================================================== 13A: a Terra menor que o tênis
R28 = 6371000.0 * 2.0 ** -28                                 # o raio da Terra no 28º passo, em u (0,024)
RL28 = 1737400.0 * 2.0 ** -28
DL28 = 384400000.0 * 2.0 ** -28                              # a distância da Terra à Lua (1,43 u)


def espaco_28(xt=0.0, yt=0.0):
    SP.ceu_espaco()
    OP.terra("terra", R28, (xt, yt, -R28 - 0.03))                          # 3 cm abaixo do chão: a sola chata dele não toca a esfera (a de 2,4 cm de raio)
    OP.lua("lua", RL28, (0.0, DL28, -R28 - 0.03))


@prova("T", "13A · 73,3 s \"...no vigésimo oitavo\": de perto: o tênis pousa em cima da Terra, que é menor que o tênis")
def p_t():
    h = S2.eu(None, sombra=False)                                      # de pé, o pé chato (no "contato" a ponta subia e o tênis flutuava)
    bpy.context.view_layer.update()
    f0 = S2.pe_de(h, "F")
    espaco_28(f0.x, f0.y - 0.035)                                       # a Terra embaixo do pé que pousa
    bpy.context.view_layer.update()
    f = S2.pe_de(h, "F")
    alvo = Vector((f.x, f.y - 0.05, -0.015))
    cam = (alvo.x - 0.75, alvo.y - 0.12, -0.01)
    S2.cam(cam, tuple(alvo), 50, fstop=8.0, foco=tuple(alvo), clip=0.002)
    P7.pilula_cam("p_terra", "a Terra", (0.0, -0.06, -0.075), 0.014, cam)


# ======================================================================== 13B: a distância Terra-Lua vira régua ao lado dele
def terra_lua_lado(fase):
    espaco_28()
    S2.eu(dict(cabeca=-8, olha=30), sombra=False, rosto=dict(boca="o"))
    zc = -R28 - 0.03
    c, cl = lateral((0.0, 0.62, 0.9), 3.05)
    anel_marca("anel_t", (-0.03, -0.01, zc - 0.02), 0.045)
    anel_marca("anel_l", (-0.03, DL28, zc), 0.04)
    P7.pilula_cam("p_t", "Terra", (0.0, -0.22, zc - 0.02), 0.05, cl)
    P7.pilula_cam("p_l", "Lua", (0.0, DL28, zc + 0.13), 0.05, cl)
    if fase == 0:                                                     # a linha deitada, da Terra à Lua
        tubo("dist", [(-0.05, 0.0, zc), (-0.05, DL28, zc)], [0.006, 0.006], O3.brilha(AM, 1.6), None, seg=10, tampa=2, contorno=0.0)
        P7.pilula_cam("p_d", "Terra–Lua: 384.400 km", (-0.05, DL28 / 2, zc + 0.11), 0.055, cl)
    else:                                                             # a mesma linha, de pé ao lado dele: a cabeça passa a ponta
        y = 0.38
        tubo("dist", [(-0.05, y, zc), (-0.05, y, zc + DL28)], [0.006, 0.006], O3.brilha(AM, 1.6), None, seg=10, tampa=2, contorno=0.0)
        P7.pilula_cam("p_d", "384.400 km", (-0.05, y + 0.2, zc + DL28), 0.05, cl)
        P7.pilula_cam("p_ele", "ele: 483.184 km", (-0.05, -0.12, 1.94), 0.055, cl)


@prova("M1", "13B · 75,8 s \"...entre a Terra e a Lua\": de lado: a Terra (sob o pé) e a Lua marcadas; a linha da distância entre as duas")
def p_m1():
    terra_lua_lado(0)


@prova("M2", "13B · 77,6 s \"...quatrocentos mil quilômetros\": a linha gira e fica de pé ao lado dele: a cabeça dele passa a ponta")
def p_m2():
    terra_lua_lado(1)


def main():
    argv = sys.argv[sys.argv.index("--") + 1:]
    if "--list" in argv:
        for k_, (t, _) in PROVAS.items():
            print(f"{k_} | {t}")
        return
    nome, out = argv[0], argv[1]
    k_ = float(argv[argv.index("--scale") + 1]) if "--scale" in argv else 0.5
    lib.reset(int(1080 * k_), int(1920 * k_), 24, 16)
    PROVAS[nome][1]()
    bpy.context.scene.render.filepath = out
    bpy.ops.render.render(write_still=True)


if __name__ == "__main__":
    main()
