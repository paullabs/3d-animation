"""Provas do replanejamento de 25/10/2026 (crítica ao v13: "aos 39 s fica travando; a vista de 150 km bugou; na altura da boca a mão ficou dentro do peito;
a Lua ficou sem sentido; levar o sangue até a cabeça está confuso. Essas cenas precisam ser refeitas e replanejadas").
Cada cena vira UM plano com uma ideia só, e a ação acontece na palavra:
  S  7C  o sangue SOBE: o tubo do coração à cabeça enche de vermelho em pulsos, 16 m de subida (a chave e a pílula);
  P  8   os passos 6 a 9 num plano só (era 4 cortes de 0,42 s): ele pisa 4 vezes e cresce em cada uma, 115 > 230 > 461 > 922 m, a câmera recua;
  V  9   a vista: por cima do ombro, a Terra curva; a linha dos olhos encosta no horizonte a 150 km (é por isso que ele vê até lá);
  B  10  a boca: de lado, a coluna de pontinhos de ar (cheia no chão, rala na boca), os braços soltos; pílulas boca 0,43 atm e chão 1,00 atm;
  L  11  a Lua: ao LADO dele (não atrás), a mesma linha de base; a chave da altura dele (3.775 km) e a da largura dela (3.474 km).
blender -b -P provas_passos7.py -- PROVA SAIDA.png [--scale 0.5]  |  --list"""
import os, sys, math, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy, lib
from mathutils import Vector
import story_passos7 as S7                                  # o mundo fixo e as trocas do v7 em diante
import story_passos3 as S3
import story_passos2 as S2
import story_passos as SP
import provas_passos5 as PV
import objetos3d_passos as OP, objetos3d_passos_b as OB
import objetos3d_abrigo as O3
from heroi3d import tubo, esfera

PROVAS = {}
AMARELO, ESCURO = "#ffd21f", "#1a1400"


def prova(nome, titulo):
    def d(fn):
        PROVAS[nome] = (titulo, fn); return fn
    return d


def pilula_cam(nome, texto, centro, tam, cam_loc):
    """pílula amarela com texto escuro, virada para a câmera (gira em z); o texto centralizado na caixa"""
    c = Vector(centro); f = Vector((cam_loc[0] - c.x, cam_loc[1] - c.y, 0.0))
    f = f.normalized() if f.length > 1e-6 else Vector((0, -1, 0))
    a = math.atan2(f.x, -f.y)
    larg = len(texto) * tam * 0.58 + tam * 0.9
    b = OB.caixa(nome + "_pil", (larg, tam * 0.08, tam * 1.5), OP.M(AMARELO, "#e0a800"), tuple(c - f * tam * 0.05), cont=0.0)
    b.rotation_euler.z = a
    t = OP.texto(nome + "_txt", texto, tam, tuple(c + f * tam * 0.03), cor=ESCURO, forca=1.4, alinha="CENTER")
    t.rotation_euler = (math.pi / 2, 0, a)
    return b, t


def chave_v(nome, x, y, z0, z1, larg, cor=AMARELO):
    """chave vertical: a barra e as duas pontas"""
    m = O3.brilha(cor, 1.5)
    OB.caixa(nome, (larg, larg, z1 - z0), m, (x, y, (z0 + z1) / 2), cont=0.0)
    for k, z in enumerate((z0, z1)):
        OB.caixa(f"{nome}_p{k}", (larg * 6, larg, larg), m, (x + larg * 2.5, y, z), cont=0.0)


def chave_h(nome, x0, x1, y, z, larg, cor=AMARELO):
    m = O3.brilha(cor, 1.5)
    OB.caixa(nome, (x1 - x0, larg, larg), m, ((x0 + x1) / 2, y, z), cont=0.0)
    for k, x in enumerate((x0, x1)):
        OB.caixa(f"{nome}_p{k}", (larg, larg, larg * 6), m, (x, y, z - larg * 2.5), cont=0.0)


# ======================================================================== 7C: o sangue sobe 16 m
def sangue_sobe(fracao=0.6):
    h, zc = S3.raio_x_rua(5)
    for o in list(bpy.data.objects):                                   # sai a linha de bolinhas do v2: no lugar dela, um tubo que ENCHE
        if o.name.startswith(("vaso", "pulso")):
            bpy.data.objects.remove(o, do_unlink=True)
    H = S2.H
    pts = [Vector((0.05, -0.03, zc + 0.04)), Vector((0.04, -0.03, zc + 0.2)), Vector((0.0, -0.03, 1.48)), Vector((0.0, -0.03, 1.62))]
    tubo("vaso_vazio", [tuple(p) for p in pts], [0.03] * 4, O3.vidro("#ffd6d6", 0.25, 0.9), None, seg=20, tampa=4, contorno=0.0)
    z_top = zc + 0.04 + (1.62 - zc - 0.04) * fracao
    cheio = [p for p in pts if p.z <= z_top] + [Vector((0.0, -0.03, z_top))]
    tubo("vaso_cheio", [tuple(p) for p in cheio], [0.024] * len(cheio), O3.brilha("#e0262c", 1.6), None, seg=20, tampa=4, contorno=0.0)
    O3.cilindro("seta", 0.035, 0.06, O3.brilha("#ffe08a", 1.8), None, (0.0, -0.06, z_top + 0.045), seg=20, eixo="Z", r2=0.0, contorno=0.0)
    chave_v("chave16", -0.32, -0.05, zc, H, 0.012)
    return h, zc


@prova("S", "7C · 37,4 s \"...levar o SANGUE até a cabeça\": o tubo enche de vermelho em pulsos, do coração à cabeça; a chave mostra a subida: 16 m")
def p_s():
    h, zc = sangue_sobe(0.6)
    cam = (0.05, -2.7, 1.42)
    pilula_cam("p16", "o sangue sobe 16 m", (0.05, -0.1, 1.98), 0.07, cam)
    pilula_cam("pcor", "coração", (0.28, -0.45, zc - 0.1), 0.055, cam)
    S2.cam(cam, (0.05, 0.0, 1.42), 50, fstop=8.0, foco=(0.0, -0.05, 1.42))


# ======================================================================== 8: quatro passos num plano só
ESCALAS = [(1 / 8, "115 m"), (1 / 4, "230 m"), (1 / 2, "461 m"), (1.0, "922 m")]


def passos_continuos(i):
    S3.cidade_burj(9, burj=(0.75, 1.6))
    s, rot = ESCALAS[i]
    S2.eu("contato", escala=s, rosto=dict(boca="o"))
    D = [0.55, 0.95, 1.6, 2.6][i]                                     # a câmera recua devagar: ele cresce mais rápido do que ela recua
    cam = (-1.7 * D, -1.9 * D, 0.5 * D)
    pilula_cam("cont", rot, (0.0, 0.0, 1.8 * s + 0.12 * D), 0.09 * D, cam)
    S2.cam(cam, (0.35 * D, 0.5 * D, 0.42 * D), 28, fstop=11.0, foco=(0.0, 0.0, 0.9 * s))


for _i in range(4):
    PROVAS[f"P{_i + 1}"] = (f"8 · passo {_i + 6}: {ESCALAS[_i][1]} (o mesmo plano; a câmera recua)", (lambda i=_i: passos_continuos(i)))


# ======================================================================== 9: a vista até o horizonte
R_TERRA = 6371.0                                                     # no passo 10, 1 u = 1 km


def terra_curva():
    SP.ceu_dia()
    m = OP.mat_planeta("campo_curvo", "#5f9a4e", "#b8a46e", escala=0.03, limiar=0.5, sombra=0.95, seed=4)
    esfera("terra_curva", R_TERRA, R_TERRA, R_TERRA, m, None, (0.0, 0.0, -R_TERRA - 0.02), contorno=0.0, seg=256, an=128)
    def b():
        OP.cidade_maquete(2600.0, passo=105.0, altura_max=90.0, altura_min=10.0, clareira=[(0.0, 0.0, 500.0)], larg=(70, 105), seed=9)          # a cidade: uma mancha densa em volta dos pés (o tabuleiro largo parecia defeito)
    SP.no_mundo(10, b, cont_u=0.0012)


def chao(s):
    """o ponto do chão curvo a s km dos pés dele, para a frente (-y)"""
    return Vector((0.0, -s, math.sqrt(R_TERRA ** 2 - s ** 2) - R_TERRA))


@prova("V1", "9 · 49,6 s \"e a vista chega\": por cima do ombro, ele levanta os olhos para o horizonte; a Terra já se vê curva")
def p_v1():
    terra_curva()
    S2.eu(dict(cabeca=-8))
    S2.cam((0.35, 0.9, 2.05), (0.0, -146.0, 0.0), 24, fstop=11.0, foco=(0.0, 0.0, 1.6))


@prova("V2", "9 · 51,4 s \"...cento e cinquenta quilômetros\": a linha dos olhos vai até onde a Terra some: 150 km (marcas de 50 e 100 km no chão)")
def p_v2():
    terra_curva()
    S2.eu(dict(cabeca=-2))
    olho = Vector((0.0, -0.12, 1.66))
    T = chao(146.3)
    n = 40
    for k in range(n):                                                # a linha tracejada dos olhos até o horizonte (encosta na curva)
        if k % 2:
            continue
        a, b = olho.lerp(T, k / n), olho.lerp(T, (k + 1) / n)
        tubo(f"visao{k}", [tuple(a), tuple(b)], [0.006 + 0.03 * k / n] * 2, O3.brilha(AMARELO, 1.8), None, seg=8, tampa=2, contorno=0.0)
    cam = (0.35, 0.9, 2.05)
    esfera("horizonte_ponto", 1.6, 1.6, 0.5, O3.brilha(AMARELO, 1.8), None, tuple(T), contorno=0.0, seg=24, an=8)
    alto = Vector((T.x, T.y, T.z + 22.0))                              # a pílula no céu, em cima do ponto do horizonte, com um fio até ele
    tubo("fio_pilula", [tuple(T), tuple(alto)], [0.25, 0.25], O3.brilha(AMARELO, 1.6), None, seg=8, tampa=2, contorno=0.0)
    pilula_cam("km150", "horizonte: 150 km", (alto.x, alto.y, alto.z + 5.0), 7.0, cam)
    S2.cam(cam, (0.0, -146.0, 0.0), 24, fstop=11.0, foco=(0.0, 0.0, 1.6))


# ======================================================================== 10: a boca e o ar ralo
def ar_ralo():
    n = 12
    SP.mundo_ar(n, nuvens_z=(1500.0, 2900.0), raio_u=10.0, n_nuv=60)
    h = S2.eu("olha_baixo", rosto=dict(boca="o"))
    rnd = random.Random(3); m = O3.brilha("#ffffff", 1.4)
    Hs = 8000.0 * 2.0 ** -n
    for i in range(520):                                              # a coluna de ar na frente dele: cheia embaixo, rala em cima
        z = -Hs * math.log(1.0 - rnd.random() * (1.0 - math.exp(-1.8 / Hs)))
        esfera(f"ar{i}", 0.006, 0.006, 0.006, m, None, (rnd.uniform(-0.12, 0.12), rnd.uniform(-0.78, -0.56), z), contorno=0.0, seg=6, an=4)
    PV.pilula_amarela("p_boca", "boca: 0,43 atm", (-0.2, -0.67, 1.86), 0.06)
    PV.pilula_amarela("p_chao", "chão: 1,00 atm", (-0.2, -0.95, 0.16), 0.07)
    return h


@prova("B1", "10 · 55,9 s \"Na altura da boca\": de lado, a boca dele abre para puxar o ar; poucos pontinhos de ar na frente dela; os braços soltos")
def p_b1():
    ar_ralo()
    S2.cam((-1.7, -0.32, 1.52), (0.0, -0.32, 1.52), 40, fstop=5.6, foco=(0.0, -0.3, 1.5))


@prova("B2", "10 · 58,4 s \"...menos da metade da pressão do chão\": a câmera desce e abre: a coluna cheia no chão e rala na boca; 1,00 atm e 0,43 atm")
def p_b2():
    ar_ralo()
    S2.cam((-3.9, -0.45, 0.95), (0.0, -0.45, 0.95), 50, fstop=8.0, foco=(0.0, -0.3, 0.95))


# ======================================================================== 11: ele e a Lua lado a lado
@prova("L", "11 · 62,5 s \"...mais alto que a Lua é larga\": a Lua ao LADO dele, na mesma linha; a chave dele (3.775 km) passa a largura dela (3.474 km)")
def p_l():
    n = 21; k = 2.0 ** -n
    SP.ceu_espaco()
    SP.terra_sob_o_pe(n, folga=0.025)
    S2.eu(dict(cabeca=-6, olha=40), rosto=dict(boca="o"))
    r = 1737400.0 * k
    xl = 0.32 + 0.12 + r
    OP.lua("lua", r, (xl, 0.0, r + 0.02))
    cam = (0.85, -11.5, 1.0)
    chave_v("ch_ele", -0.45, -0.1, 0.0, 1.8, 0.014)
    pilula_cam("p_ele", "ele: 3.775 km", (-0.22, -0.12, 2.0), 0.07, cam)
    chave_h("ch_lua", xl - r, xl + r, -r - 0.05, r + 0.02, 0.014)
    pilula_cam("p_lua", "Lua: 3.474 km de largura", (xl, -r - 0.08, r + 0.02 - 0.16), 0.075, cam)
    for j in range(12):                                               # a linha tracejada no topo da cabeça dele, passando por cima da Lua
        if j % 2 == 0:
            x0 = 0.0 + j * 0.2
            OB.caixa(f"topo{j}", (0.12, 0.01, 0.01), O3.brilha("#ffffff", 1.5), (x0, -r - 0.05, 1.8), cont=0.0)
    S2.cam(cam, (0.85, 0.0, 1.0), 85, fstop=11.0, foco=(0.4, 0.0, 1.0))


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
