"""Provas do plano v7 de "os passos" (crítica de 25/10/2026: "dos 5 aos 7 s não acontece nada; ao sair da cena dos 10 s parece outro cenário e o amigo some;
aos 16 s não parece que ele cresceu; aos 22 e 25 s é a mesma cena, sem dimensão; aos 28 s é abstrato; o cabelo é só um risco; textos amarelos sem contraste;
aos 33 s a mão dele está dentro do peito").
IDEIA: A AVENIDA DA MEDIDA. Uma rua só, de lado (câmera lateral, passos legíveis), com as referências em ordem: o amigo (1,8 m), o poste (7 m), o prédio de 5 andares (15 m),
o de 10 (30 m), o de 18 (55 m). A cada passo ele pousa ao lado da referência seguinte e a câmera recua. O amigo fica para trás no mesmo chão.
Rótulos: pílula escura com texto branco (contraste), régua de pé no chão e linha na altura da cabeça.
blender -b -P provas_passos5.py -- PROVA SAIDA.png [--scale 0.5]  |  --list"""
import os, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy, lib
from mathutils import Vector, Matrix
import story_passos4 as S4                                 # (traz story_passos2/3 e o amigo)
import story_passos2 as S2
import objetos3d_passos as OP, objetos3d_passos_b as OB
import objetos3d_abrigo as O3
import poses_passos as PP
import elenco3d_abrigo as E3
import cena

PROVAS = {}
SENSOR = 36.0                                               # o quadro vertical (9:16) vê distância x 36 / lente


def prova(nome, titulo):
    def d(fn):
        PROVAS[nome] = (titulo, fn); return fn
    return d


def altura(n):
    return 1.8 * 2 ** n


def avenida(n, extras=()):
    """a rua do passo n (o mundo em metros, escalado), vista de lado: o lado -x (da câmera) sem prédio, sem carro, sem ponto, sem a moça"""
    E = S2.rua2(n, extras=extras, moca=False, ponto=False, aberto=-1, livre_u=3.0)
    for o in list(bpy.data.objects):
        if o.name.startswith("carro") or o.name.endswith("_toldo"):
            bpy.data.objects.remove(o, do_unlink=True)
    return E


def lateral(vis, alvo, lente=35, fstop=11.0, d=None):
    """câmera de lado (em -x, olhando para +x): 'vis' u cabem na altura do quadro em volta do alvo (x, y, z)"""
    d = d or vis * lente / SENSOR
    return S2.cam((alvo[0] - d, alvo[1], alvo[2]), alvo, lente, fstop=fstop, foco=alvo)


ROT_LAT = (math.pi / 2, 0, -math.pi / 2)                    # o texto de pé, de frente para a câmera lateral (em -x)


def pilula(nome, texto, centro, tam, cor_txt="#ffffff"):
    """o rótulo legível: caixa escura atrás de um texto claro, de frente para a câmera lateral (contraste; o amarelo sobre o céu não se lia)"""
    larg = max(0.4, len(texto) * tam * 0.58 + tam * 0.9)
    x, y, z = centro
    OB.caixa(nome + "_pil", (tam * 0.08, larg, tam * 1.5), OP.M("#15181d", "#15181d"), (x + tam * 0.05, y, z), cont=0.0)
    OP.texto(nome + "_txt", texto, tam, (x - tam * 0.02, y, z), cor=cor_txt, forca=1.0, rot=ROT_LAT, alinha="CENTER")


def pilula_y(nome, texto, centro, tam, cor_txt="#ffffff"):
    """a mesma pílula, de frente para uma câmera em -y"""
    larg = max(0.4 * tam, len(texto) * tam * 0.58 + tam * 0.9)
    x, y, z = centro
    OB.caixa(nome + "_pil", (larg, tam * 0.08, tam * 1.5), OP.M("#15181d", "#15181d"), (x, y + tam * 0.05, z), cont=0.0)
    OP.texto(nome + "_txt", texto, tam, (x, y - tam * 0.02, z), cor=cor_txt, forca=1.0, alinha="CENTER")


REGUA_COR = "#ffd21f"                                         # amarelo vivo: a régua tem que aparecer sobre o ônibus branco e sobre os prédios


def pilula_amarela(nome, texto, centro, tam):
    """o rótulo amarelo com texto escuro (contraste sobre o céu, o branco do ônibus e os prédios)"""
    larg = max(0.4, len(texto) * tam * 0.58 + tam * 0.9)
    x, y, z = centro
    OB.caixa(nome + "_pil", (tam * 0.08, larg, tam * 1.5), OP.M(REGUA_COR, "#e0a800"), (x + tam * 0.05, y, z), cont=0.0)
    OP.texto(nome + "_txt", texto, tam, (x - tam * 0.02, y, z), cor="#1a1400", forca=1.4, rot=ROT_LAT, alinha="CENTER")


def regua_lateral(x, y, topo_u, topo_m, tam, nome="rl"):
    """a fita métrica de pé, de lado: fita creme, marcas escuras e números pretos legíveis ao lado; a altura no topo numa pílula (nome = prefixo dos objetos)"""
    OB.caixa(nome + "_fita", (0.02 * tam / 0.11, 0.08 * tam / 0.11, topo_u), OP.M(REGUA_COR, "#e0a800"), (x, y, topo_u / 2), cont=0.003)
    b = OP.bonito(topo_m / 4.0)
    k = topo_u / topo_m
    m = b
    e = tam / 0.11
    while m < topo_m * 0.9:
        OB.caixa(f"{nome}_m{m}", (0.03 * e, 0.12 * e, 0.012 * e), OP.M("#3a2a00", "#3a2a00"), (x - 0.01 * e, y, m * k), cont=0.0)
        OP.texto(f"{nome}_t{m}", OB.OP_fmt(m), tam * 0.9, (x - 0.02 * e, y - 0.1 * e, m * k - tam * 0.28), cor="#1a1400", forca=1.4, rot=ROT_LAT, alinha="RIGHT")
        m += b
    pilula_amarela(nome + "_topo", OB.OP_fmt(topo_m), (x, y, topo_u + tam * 1.25), tam * 1.15)


def linha_altura(nome, z, y0, y1, tam, texto, x=0.0):
    """a linha fina na altura de uma cabeça (de y0 a y1), com a pílula na ponta"""
    OB.caixa(nome, (tam * 0.05, abs(y1 - y0), tam * 0.07), O3.brilha(OP.AMBAR, 1.6), (x, (y0 + y1) / 2, z), cont=0.0)
    pilula(nome + "_p", texto, (x, min(y0, y1) - len(texto) * tam * 0.3 - tam * 0.4, z), tam)


def amigo(n, y_u, x_u=-0.05, pose="passagem", cabeca=None, olha=None, rosto=None):
    h = S4.amigo(n, x_u, y_u, pose, cabeca=cabeca, olha=olha, rosto=rosto)
    return h


def eu(n_pose, y_u=0.0, rosto=None):
    return S2.eu(n_pose, loc=(0, y_u, 0), rosto=rosto, sombra=True)


# ------------------------------------------------------------------ a avenida, passo a passo (câmera de lado)
def cena_passo(n, extras, pose_eu, y_amigo, pose_am, nota=None, cab_am=None, regua_y=-0.85):
    """o passo n, de lado: ele (1,8 u, sempre), o mundo escalado por 2^-n, a régua de pé à frente dele (à direita) e a pílula com a altura dele"""
    avenida(n, extras)
    eu(pose_eu)
    if y_amigo is not None:
        amigo(n, y_amigo, pose=pose_am, cabeca=cab_am)
    H = 1.8
    tam = 0.11
    regua_lateral(0.3, regua_y, H, altura(n), tam)
    if y_amigo is not None and n <= 2:
        k = 2.0 ** -n
        linha_altura("l_am", 1.8 * k, y_amigo - 0.25, y_amigo + 0.15, tam * 0.8, "1,8 m", x=-0.3)
    lateral(3.7, (0.0, -0.1, 0.95))


@prova("A0", "0 a 2 s · os dois andam de lado, do mesmo tamanho (1,8 m), na rua do ponto; o poste ao fundo")
def a0():
    avenida(0, ("poste",))
    eu("contato"); S4.amigo(0, 0.0, 1.35, "subida")
    lateral(3.4, (0.0, 0.7, 0.95))


@prova("A1", "2,6 s · depois do 1º passo (3,6 m): a régua de pé, a linha de 1,8 m no amigo, que ficou para trás")
def a1():
    cena_passo(1, (), "passagem", 1.05, "passagem")


@prova("A2", "9,9 s · 2º passo (7,2 m): ao lado do poste de 7 m; o amigo lá atrás, do tamanho do tornozelo")
def a2():
    cena_passo(2, ("poste",), "passagem", 1.1, "passagem")


@prova("A3", "12,5 s · 3º passo (14,4 m): ao lado do prédio de 5 andares (15 m)")
def a3():
    cena_passo(3, ("p5",), "passagem", None, "passagem")


@prova("A4", "19 s · 4º passo (28,8 m): ao lado do prédio de 10 andares (30 m)")
def a4():
    cena_passo(4, ("p10",), "passagem", None, "passagem")


@prova("A5", "25 s · 5º passo (57,6 m): a cabeça passa o terraço do prédio de 18 andares (55 m)")
def a5():
    cena_passo(5, ("p18",), "passagem", None, "passagem")


# ------------------------------------------------------------------ o cabelo (cena em metros reais, de perto no alto do prédio)
def cena_cabelo(com_fio=True):
    """o gigante (57,6 m) de pé ao lado do prédio de 18 andares, com a cabeça colada no balancim; o limpador no balancim, de frente para ele"""
    import story_passos3 as S3
    import ik3_abrigo as IK
    from heroi3d import tubo
    S2.mundo_metros()
    x, y, w = 26.0, 18.0, 20.0
    est = {}
    def limp(px, py, pz, rz):
        h = E3.faz("limpador", "limp"); h.raiz.scale = (S2.EU_ESC,) * 3
        h.pose(**h.pe_no_chao(**dict(S3.SP.STAND))); h.raiz.location = (px, py, pz); h.raiz.rotation_euler.z = rz
        PP.assenta(h, pz); est["h"] = h
    OB.predio_alto("p18", x, y, 18, w=w, cor="#8f98a6", balancim=True, face_balancim="esq", limpador=limp)
    g = S2.eu(dict(cabeca=-4, olha=0), loc=(8.3, y, 0), rot=90, escala=32, nome="eu", sombra=False)
    for o in list(bpy.data.objects):
        pass
    bpy.context.view_layer.update()
    return g, est["h"]


@prova("H1", "29 s · \"O seu cabelo\": o gigante de perfil, colado no prédio, olhando o limpador; o balancim na altura da cabeça dele (de longe)")
def h1():
    g, lh = cena_cabelo()
    S2.cam((13.5, -22.0, 51.5), (13.5, 18.0, 51.5), 85, fstop=8.0, foco=(14.0, 18.0, 51.0), clip=0.5)


@prova("H2", "30,4 s · \"...grossura de um palito de dente\": o fio do cabelo ao lado do palito, mesma grossura; pílulas legíveis (de perto, 85 mm)")
def h2():
    from heroi3d import tubo
    import ik3_abrigo as IK
    S2.mundo_metros()
    base = Vector((0.0, 0.0, 20.0))                                      # um ponto no ar, longe de tudo (o fundo é o céu)
    h = E3.faz("limpador", "limp"); h.raiz.scale = (S2.EU_ESC,) * 3
    h.pose(**h.pe_no_chao(**dict(S2.SP.STAND))); h.raiz.location = (base.x + 0.55, base.y + 0.05, base.z); h.raiz.rotation_euler.z = math.radians(-90)
    PP.assenta(h, base.z)
    bpy.context.view_layer.update()
    ombro = h.ombro["F"].matrix_world.translation
    alvo = Vector((base.x - 0.05, base.y - 0.02, base.z + 1.12))         # a mão levantada na altura do rosto
    P = IK.braco_pose(h, "F", tuple(alvo), dict(getattr(h, "_ultima", {})), nome="limp")
    h.pose(**P); bpy.context.view_layer.update()
    m = h.punho["F"].matrix_world.translation
    pc = Vector((m.x - 0.02, m.y - 0.055, m.z + 0.105))                           # o palito de pé, saindo do punho
    OP.palito("palito", tuple(pc), 0.002, 0.065, eixo="Z")
    fim = pc + Vector((0.0046, 0.0, 0.0))                                # o fio logo ao lado do palito (2,4 mm contra 2 mm)
    tubo("fio_solto", [(fim.x + 0.03, fim.y, pc.z + 0.34), (fim.x + 0.012, fim.y, pc.z + 0.21), (fim.x + 0.0075, fim.y, pc.z + 0.1), (fim.x, fim.y, pc.z + 0.03), (fim.x, fim.y, pc.z - 0.01)],
         [0.0012] * 5, OP.M("#2a1c16", "#120c09", "#6a4a3a"), None, seg=12, tampa=4, contorno=0.0)
    for q, (dx, dz, esp) in enumerate(((-0.05, 0.30, 0.0008), (0.045, 0.28, 0.0009), (0.075, 0.31, 0.0008))):     # outros fios lá no alto: dá para saber que é cabelo
        tubo(f"fio_ao_fundo{q}", [(fim.x + dx, fim.y + 0.04, pc.z + 0.34), (fim.x + dx * 0.9, fim.y + 0.04, pc.z + dz * 0.8), (fim.x + dx * 0.85, fim.y + 0.04, pc.z + dz * 0.55)],
             [esp] * 3, OP.M("#2a1c16", "#120c09", "#6a4a3a"), None, seg=10, tampa=4, contorno=0.0)
    tam = 0.0075
    pilula_y("t_fio", "cabelo: 2,4 mm", (fim.x + 0.022, fim.y - 0.01, pc.z + 0.165), tam)
    pilula_y("t_pal", "palito: 2 mm", (pc.x - 0.046, pc.y - 0.01, pc.z + 0.06), tam)
    S2.cam((pc.x - 0.02, pc.y - 0.5, pc.z + 0.07), (pc.x - 0.012, pc.y, pc.z + 0.07), 65, fstop=4.0, foco=(pc.x, pc.y, pc.z), clip=0.005)


# ------------------------------------------------------------------ o impacto, de frente (3/4), no MESMO mundo da avenida
def impacto_frente(n, extras, y_amigo=None):
    """a pisada vista de frente, em 3/4: o rosto dele (susto), a poeira, a referência do passo ao fundo e o amigo (quando cabe)"""
    avenida(n, extras)
    h = S2.eu("contato", loc=(0, 0, 0), rosto=dict(boca="o"))
    f = S2.pe_de(h, "F")
    OP.poeira_pouso(f.x, f.y - 0.05, r=0.45)
    if y_amigo is not None:
        amigo(n, y_amigo, x_u=-0.6, pose="olha_baixo", cabeca=-28, olha=-24, rosto=dict(boca="o"))
    S2.cam((-1.2, -3.4, 0.62), (0.15, 0.0, 1.0), 28, fstop=8.0, foco=(0.0, 0.0, 1.0))


@prova("B1", "2,1 s · o 1º impacto, de frente (3/4): o rosto de susto, a poeira, o amigo assustado")
def b1():
    impacto_frente(1, (), 0.45)


@prova("B3", "11,8 s · o 3º impacto, de frente (3/4): o prédio de 5 andares ao fundo")
def b3():
    impacto_frente(3, ("p5",))


@prova("B5", "23,9 s · o 5º impacto, de frente (3/4): o prédio de 18 andares ao fundo")
def b5():
    impacto_frente(5, ("p18",))


def main():
    argv = sys.argv[sys.argv.index("--") + 1:]
    if "--list" in argv:
        for k, (t, _) in PROVAS.items():
            print(f"{k} | {t}")
        return
    nome, out = argv[0], argv[1]
    k = float(argv[argv.index("--scale") + 1]) if "--scale" in argv else 0.5
    lib.reset(int(1080 * k), int(1920 * k), 24, 20)
    PROVAS[nome][1]()
    bpy.context.scene.render.filepath = out
    bpy.ops.render.render(write_still=True)


if __name__ == "__main__":
    main()
