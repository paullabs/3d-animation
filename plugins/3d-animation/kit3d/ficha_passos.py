"""Ficha de elenco, objetos e poses de "E se cada passo dobrasse a sua altura?" (plano de cena v2, 25/10/2026).
Um item por processo do Blender (o kit guarda materiais entre cenas):
blender -b -P ficha_passos.py -- ITEM SAIDA.png [--scale 1.0]     (--list mostra os itens)
Depois: python3 ficha_passos_montar.py PASTA (renderiza em paralelo e monta as pranchas)."""
import os, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy, lib
from lib import empty, srgb
from mathutils import Vector
import cena, props
import objetos3d_abrigo as O3, objetos3d_abrigo_b as O3B, cidade3d as C3, elenco3d_abrigo as E3
import objetos3d_passos as OP, objetos3d_passos_b as OB
import story_passos as SP
import poses_passos as PP
from heroi3d import esfera, tubo

ITENS = {}
EU_ESC = SP.EU_ESC
E3.ESPEC["zelador"] = dict(roupa="#5f7464", calca="#33382f", escura="#46574a", gola="#46574a", cabeca=0.78, body_w=1.1, arm_len=1.12,
                           acess=[("cabelo", "recuado", "#b8b4a8"), ("bigode", "#b8b4a8")])
E3.ESPEC["limpador"] = dict(roupa="#d9772b", calca="#3a3f46", escura="#a85a1e", gola="#a85a1e", cabeca=0.78, body_w=1.06, arm_len=1.12,
                            acess=[("bone", "#e8c040")])


def item(nome, titulo, w=540, h=960):
    def deco(fn):
        ITENS[nome] = dict(titulo=titulo, fn=fn, w=w, h=h)
        return fn
    return deco


def estudio(cor="#dfe3e4", chao="#cfd3d2"):
    bpy.context.scene.world.node_tree.nodes["Background"].inputs[0].default_value = (*srgb(cor), 1)
    OP.domo([(-900, chao), (-1, chao), (0, cor), (300, "#b9c6cf")])
    cena.poly_mesh("chao_est", [(-400, -400, 0), (400, -400, 0), (400, 400, 0), (-400, 400, 0)], props.FM(chao))


def bbox(objs):
    bpy.context.view_layer.update()
    pts = []
    for o0 in objs:
        for o in [o0] + list(o0.children_recursive):
            if o.type in ("MESH", "FONT"):
                pts += [o.matrix_world @ Vector(c) for c in o.bound_box]
    lo = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    hi = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    return lo, hi


def enquadra(objs, lente=85, az=0.0, el=4.0, folga=1.25, fstop=11.0, dz=0.0):
    """câmera que enquadra a caixa dos objetos inteira (altura ou largura, a que pedir mais), de frente (az = 0) ou girada"""
    lo, hi = bbox(objs)
    c = (lo + hi) / 2; c.z += dz
    tam = hi - lo
    larg = max(tam.x * abs(math.cos(math.radians(az))) + tam.y * abs(math.sin(math.radians(az))), 0.01)
    vis = max(tam.z, larg * 16 / 9) * folga
    return SP.cam_v(tuple(c), vis, lente, az=az, el=el, fstop=fstop, foco=tuple(c))


def eu_em(pose=None, loc=(0, 0, 0), rot=0.0, nome="eu", boca="reta"):
    h = E3.faz("eu", nome); h.raiz.scale = (EU_ESC,) * 3
    if pose:
        PP.aplica(h, pose, escala=EU_ESC)
    else:
        h.pose(**h.pe_no_chao(**SP.STAND)); h.rosto(boca=boca, lid=0.0)
    h.raiz.location.x += loc[0]; h.raiz.location.y += loc[1]; h.raiz.location.z += loc[2]
    h.raiz.rotation_euler.z = math.radians(rot)
    cena.ground_disc(nome + "_sb", 0.42 * EU_ESC, 0.3 * EU_ESC, cena.amat(nome + "_sb_m", "#000000", 1.0, 0.3, ("radial", 1.1)), (loc[0], loc[1] + 0.05, 0.004), n=32)
    return h


def ator(chave, nome, loc=(0, 0, 0), rot=0.0, esc=1.0, pose=None, rosto=None):
    h = E3.faz(chave, nome); h.raiz.scale = (EU_ESC * esc,) * 3
    P = dict(SP.STAND); P.update(pose or {})
    h.pose(**h.pe_no_chao(**P)); h.raiz.location = loc; h.raiz.rotation_euler.z = math.radians(rot)
    PP.assenta(h, loc[2])
    r = dict(boca="reta", lid=0.0); r.update(rosto or {}); h.rosto(**r)
    cena.ground_disc(nome + "_sb", 0.4 * EU_ESC * esc, 0.28 * EU_ESC * esc, cena.amat(nome + "_sb_m", "#000000", 1.0, 0.3, ("radial", 1.1)), (loc[0], loc[1] + 0.05, loc[2] + 0.004), n=32)
    return h


# ======================================================================== ELENCO
for _az, _nm, _tt in ((0, "eu_frente", "eu · de frente"), (-38, "eu_3q", "eu · três quartos"), (90, "eu_lado", "eu · de lado"), (180, "eu_costas", "eu · de costas")):
    def _f(az=_az):
        estudio(); h = eu_em(); enquadra([h.raiz], 85, az=az, el=3, folga=1.18)
    item(_nm, _tt)(_f)


@item("moca", "a moça do ponto (1,64 m)")
def i_moca():
    estudio(); h = ator("moca", "moca", esc=0.97, pose=dict(ombro=(-8, 10), cotovelo=(-20, -14))); enquadra([h.raiz], 85, az=-20, el=3, folga=1.18)


@item("zelador", "o zelador do terraço")
def i_zelador():
    estudio(); h = ator("zelador", "zel", pose=dict(cabeca=-28, tronco=-4, ombro=(-6, 8), cotovelo=(-18, -14)), rosto=dict(boca="o"))
    enquadra([h.raiz], 85, az=-24, el=3, folga=1.18)


@item("limpador", "o limpador no balancim, com o palito")
def i_limpador():
    estudio()
    OB.caixa("fachada", (4.0, 0.3, 4.0), OP.M("#8a93a0"), (0, 0.7, 1.4), cont=0.01)
    for x in (-1.0, 1.0):
        OB.caixa(f"jan{x}", (1.3, 0.05, 1.2), OP.M("#1d3340", "#142530", "#7aa0b0"), (x, 0.53, 1.8), cont=0.0)
    OB.caixa("bal_piso", (3.4, 0.8, 0.12), OP.M("#7a7e80", "#55585a"), (0, 0.0, -0.06), cont=0.01)
    for k, (zz, hh) in enumerate(((1.0, 0.06), (0.55, 0.05))):
        OB.caixa(f"bal_g{k}", (3.4, 0.05, hh), OP.M("#c9a23a", "#8e7024"), (0, -0.38, zz), cont=0.01)
    for x in (-1.65, 0.0, 1.65):
        OB.caixa(f"bal_p{x}", (0.06, 0.06, 1.0), OP.M("#c9a23a", "#8e7024"), (x, -0.38, 0.5), cont=0.01)
    for x in (-1.5, 1.5):
        O3.cilindro(f"cabo{x}", 0.02, 3.0, OP.M("#2a2a2a"), None, (x, 0.0, 1.6), seg=8, contorno=0.0)
    h = E3.faz("limpador", "limp"); h.raiz.scale = (EU_ESC,) * 3
    PP.aplica(h, "estica", escala=EU_ESC); h.rosto(boca="reta", lid=0.0)
    bpy.context.view_layer.update()
    m = h.punho["F"].matrix_world.translation
    OP.palito("palito", (m.x, m.y - 0.02, m.z + 0.045), 0.006, 0.065, eixo="Z")
    SP.cam_v((0.0, -0.2, 0.95), 2.7, 50, az=-22, el=6, fstop=8.0, foco=(0.0, 0.0, 1.0))


# ======================================================================== POSES
for _p in PP.ORDEM:
    for _vista, _az in (("lado", 90.0), ("3q", -36.0)):
        def _f(p=_p, az=_az):
            estudio()
            h = eu_em(p)
            enquadra([h.raiz], 85, az=az, el=4, folga=1.2)
        item(f"pose_{_p}_{_vista}", f"{PP.NOMES[_p]} · {'de lado' if _vista == 'lado' else '3/4'}", 540, 960)(_f)


# ======================================================================== OBJETOS
@item("onibus", "ônibus (3,2 m de altura)")
def i_onibus():
    estudio(); o = OB.onibus("bus", (0, 0, 0), rot=-62); h = eu_em(loc=(-2.6, -2.2, 0))
    enquadra([o, h.raiz], 35, az=0, el=8, folga=1.1)


@item("ponto", "ponto de ônibus e a moça")
def i_ponto():
    estudio(); o = OB.ponto_onibus("pt", (0, 0, 0), rot=-14); h = ator("moca", "moca", loc=(-0.5, -0.4, 0), esc=0.97, rot=-10)
    enquadra([o, h.raiz], 35, az=0, el=6, folga=1.15)


@item("poste", "poste de luz (7,2 m)")
def i_poste():
    estudio(); o = C3.poste_luz("poste", (0, 0, 0), lado=1); h = eu_em(loc=(0.9, -0.5, 0))
    enquadra([o, h.raiz], 35, az=0, el=5, folga=1.08)


@item("porta", "porta (2,1 m)")
def i_porta():
    estudio(); OB.caixa("parede", (3.2, 0.25, 2.8), OP.M("#c8b8a0", "#a39480"), (0, 0.14, 1.4), cont=0.01)
    o = O3B.porta_comum3d("porta", (0, 0.0, 0), 1.0, abre=0.0, cor="#4f6e8a"); h = eu_em(loc=(-1.0, -0.6, 0))
    enquadra([o, h.raiz], 50, az=0, el=4, folga=1.15)


@item("relogio", "relógio de rua (a queda: 1,7 s)")
def i_relogio():
    estudio(); o = OB.relogio_rua("rel", (0, 0, 0), hora=(10, 8), seg=1.7)
    SP.cam((0.6, -2.6, 2.6), (0.0, 0.0, 2.6), 50, fstop=8.0, foco=(0.0, -0.1, 3.3))


@item("poca", "poça (a voz chega aos pés)")
def i_poca():
    estudio(chao="#4a4d48"); OB.poca("poca", (0, 0, 0)); OB.ondas_poca("onda", (0.0, 0.0, 0.0))
    h = eu_em(loc=(0.6, 0.55, 0))
    SP.cam((0.3, -2.0, 0.9), (0.2, 0.2, 0.2), 28, fstop=8.0, foco=(0.1, 0.1, 0.1))


@item("predios", "prédios de 5, 10 e 18 andares (15, 30 e 55 m)")
def i_predios():
    estudio()
    OB.predio_alto("p5", -26.0, 0.0, 5, w=12.0)
    OB.predio_alto("p10", 0.0, 0.0, 10, w=14.0, cor="#9aa2a8")
    OB.predio_alto("p18", 30.0, 0.0, 18, w=18.0, cor="#8f98a6", balancim=True)
    OB.estacionamento("est", 0.0, -30.0, comp=24, larg=80)
    h = eu_em(loc=(-8.0, -14.0, 0))
    SP.cam((0.0, -150.0, 28.0), (2.0, 0.0, 26.0), 50, fstop=16.0, foco=150.0)


@item("predio18_topo", "18º andar: terraço, caixa d'água e balancim")
def i_topo():
    estudio("#c6d8e6")
    def limp(x, y, z, rz=0.0):
        h = E3.faz("limpador", "limp"); h.raiz.scale = (EU_ESC,) * 3; PP.aplica(h, "estica", escala=EU_ESC); h.raiz.location = (x, y, z); h.raiz.rotation_euler.z = rz
    OB.predio_alto("p18", 0.0, 0.0, 18, w=18.0, cor="#8f98a6", balancim=True, limpador=limp)
    ator("zelador", "zel", loc=(-3.0, -2.0, 54.8), pose=dict(cabeca=-28, tronco=-4), rosto=dict(boca="o"))
    SP.cam((-14.0, -26.0, 60.0), (0.0, -6.0, 53.0), 35, fstop=11.0, foco=(0.0, -7.0, 53.0))


@item("macro_palito", "fio de cabelo (2,4 mm) e palito (2 mm), régua em mm")
def i_macro_palito():
    estudio("#e6e8e4", "#d9dcd6")
    OB.fio_escamas("fio", (-0.32, 0.0, 0.25), 0.48, 3.0, eixo="Z")
    OP.palito("palito", (0.32, 0.0, 0.25), 0.4, 3.0, eixo="Z")
    OB.regua_macro("reg", (0.0, -0.3, -1.55), 2.0, 0.2, 5, "mm", larg=0.32)
    SP.cam((0.0, -6.5, 0.0), (0.0, 0.0, -0.05), 50, fstop=8.0, foco=(0.0, -0.1, 0.0))


@item("macro_lata", "fio de cabelo (7,7 cm) e lata (6,6 cm), régua em cm")
def i_macro_lata():
    estudio("#e6e8e4", "#d9dcd6")
    OB.fio_escamas("fio", (-0.42, 0.0, 0.25), 0.62, 3.0, eixo="Z", n=12)
    OP.lata("lata", (0.45, 0.0, -0.45), 0.53, 1.0, eixo="Z")
    OB.regua_macro("reg", (0.0, -0.3, -1.55), 2.4, 0.08, 10, "cm", larg=0.32)
    SP.cam((0.0, -6.5, 0.0), (0.0, 0.0, -0.05), 50, fstop=8.0, foco=(0.0, -0.1, 0.0))


@item("manometro", "manômetro (o coração: 1,65 atm)")
def i_man():
    estudio(); OP.manometro("man", (0.0, 0.0, 1.0), 0.5, 1.65, "1,65 atm", faixa=(0.0, 2.0), zona_vermelha=1.5)
    SP.cam((0.0, -3.0, 1.0), (0.0, 0.0, 1.0), 50, fstop=8.0, foco=(0.0, -0.1, 1.0))


@item("raiox", "raio X: o coração e o vaso até a cabeça")
def i_raiox():
    estudio("#1b2433", "#141b26")
    h = eu_em(boca="reta"); OB.raio_x(h)
    z_c = 0.72 * 1.8
    OB.coracao("cor", (0.05, -0.02, z_c), s=1.0)
    tubo("vaso", [(0.05, -0.02, z_c + 0.05), (0.04, -0.01, z_c + 0.2), (0.0, 0.0, 1.5), (0.0, 0.0, 1.62)], [0.014] * 4, O3.brilha("#ff4a3a", 1.6), None, seg=16, tampa=4, contorno=0.0)
    for i in range(6):
        u = (i + 0.5) / 6
        esfera(f"pulso{i}", 0.018, 0.018, 0.024, O3.brilha("#ffd0c0", 2.0), None, (0.05 - 0.05 * u, -0.015, z_c + 0.06 + (1.62 - z_c - 0.06) * u), contorno=0.0, seg=12, an=8)
    OB.regua2(-0.42, 1.8, 1.8, marcas_m=[], lado=-1, rotulo=" ", escuro=True)
    OB.caixa("chave_16", (0.012, 0.012, 1.8 - z_c), O3.brilha(OP.AMBAR, 1.5), (-0.3, -0.05, (1.8 + z_c) / 2), cont=0.0)
    OP.texto("t16", "16 m", 0.11, (-0.38, -0.05, (1.8 + z_c) / 2), alinha="RIGHT")
    SP.cam_v((0.0, 0.0, 1.0), 2.3, 85, az=0, el=2, fstop=11.0, foco=(0.0, 0.0, 1.2))


@item("aviao", "avião de cruzeiro (voa a 10 km)")
def i_aviao():
    estudio("#b9d2ea"); a = OB.aviao("av", (0, 0, 0), rot=-25)
    SP.cam((26.0, -46.0, -30.0), (-1.0, 0.0, 0.0), 35, fstop=16.0, foco=60.0)


@item("nuvens", "nuvens (1,5 a 3 km de altura)")
def i_nuv():
    estudio("#c8dcee", "#a9c0d4"); OP.nuvens(10.0, 30.0, n=8, seed=4, tam=(8, 16))
    SP.cam((0.0, -70.0, 18.0), (0.0, 0.0, 10.0), 35, fstop=16.0, foco=70.0)


@item("espaco", "Terra, Lua e a órbita (fora de escala de distância)")
def i_espaco():
    SP.ceu_espaco()
    OP.terra("terra", 0.6, (-0.5, 0.0, 1.0)); OP.lua("lua", 0.16, (0.75, -0.2, 1.4))
    OB.orbita("orb", (-0.5, 0.0, 1.0), 1.32, r_tubo=0.004)
    SP.cam((0.0, -4.0, 2.0), (0.0, 0.0, 1.05), 50, fstop=11.0, foco=(0.0, 0.0, 1.0))


# ======================================================================== BURJ KHALIFA
def burj_cena(raio=1600.0):
    OB.palco("dubai")
    SP.no_mundo(9, lambda: (OB.dubai(0.0, 0.0, raio=raio), OB.burj("burj", 0.0, 0.0)), cont_u=0.0012)


@item("burj_dubai", "Burj Khalifa: 828 m, no centro de Dubai")
def i_burj_dubai():
    burj_cena()
    SP.cam((1.9, -3.6, 0.75), (0.0, 0.0, 0.7), 50, fstop=16.0, foco=(0.0, 0.0, 0.8))


@item("burj_planta", "Burj Khalifa de cima: planta em Y e recuos em espiral")
def i_burj_planta():
    burj_cena()
    SP.cam((0.45, -0.7, 2.6), (0.0, 0.0, 0.3), 50, fstop=16.0, foco=(0.0, 0.0, 0.8))


@item("burj_agulha", "Burj Khalifa: os últimos recuos e a agulha")
def i_burj_agulha():
    burj_cena()
    SP.cam((0.4, -1.05, 1.05), (0.0, 0.0, 1.22), 85, fstop=16.0, foco=(0.0, 0.0, 1.1))


# ======================================================================== PALCO DE MEDIDA
def fila(n_atual, passos_fantasma, x0=-0.32, gap=0.05, y=0.2):
    """os tamanhos anteriores em fila à esquerda do boneco (cada um com a sua altura verdadeira); um tamanho menor que 2% vira um ponto"""
    k = 2.0 ** -n_atual
    x = x0
    for n in sorted(passos_fantasma, reverse=True):
        alt = SP.H_EU * 2 ** n * k
        e = alt / SP.H_EU
        larg = 0.42 * e
        if alt > 0.036:
            x -= larg / 2
            h = E3.faz("eu", f"fant{n}"); h.raiz.scale = (EU_ESC * e,) * 3; h.pose(**h.pe_no_chao(**SP.STAND)); h.rosto(boca="reta", lid=0.0)
            h.raiz.location = (x, y, 0.0); OB.fantasma(h)
            x -= larg / 2 + gap
        else:
            x -= 0.02
            esfera(f"fant_pt{n}", 0.012, 0.012, 0.012, cena.amat("fant_pt_m", "#ffffff", 1.0, 0.7), None, (x, y, 0.012), contorno=0.0, seg=10, an=6)
            x -= 0.03
    return x


X_REGUA = -0.76


def camera_palco(cx=-0.02, cz=0.98, vis=3.25):
    """palco: câmera ortográfica de frente (sem perspectiva): a altura no quadro é a altura de verdade, esteja o objeto na frente ou atrás"""
    c = SP.cam((cx, -30.0, cz), (cx, 0.0, cz), 135, fstop=22.0, foco=30.0)
    c.data.type = "ORTHO"; c.data.ortho_scale = vis * 9 / 16
    c.data.dof.use_dof = False
    return c


@item("palco_dia", "palco de medida (dia): 3º passo, 14,4 m", 540, 960)
def i_palco_dia():
    OB.palco("dia")
    n = 3; k = 2.0 ** -n
    eu_em()
    fila(n, [2, 1, 0])
    def b():
        OB.predio_alto("cmp", 0.0, 0.0, 5, w=6.0, cor="#8f98a6", terraco=False)
    E = SP.no_mundo(n, b); E.location = (0.62, 1.5, 0.0)
    OB.rotulo_ref(0.32, 15.0 * k + 0.13, "prédio: 15 m", lado=1, tam=0.085, y=-0.3, cor=OB.AMBAR_ESC)
    OB.regua2(X_REGUA, 1.8, 14.4, lado=1, cor_num=OB.AMBAR_ESC)
    camera_palco()


@item("palco_azul", "palco de medida (alto): 12º passo, 7,4 km", 540, 960)
def i_palco_azul():
    OB.palco("azul")
    n = 12; k = 2.0 ** -n
    eu_em()
    fila(n, [11, 10, 9])
    def b():
        OP.nuvens(1800.0, 9000.0, n=9, seed=6, tam=(1400, 2600))
    E = SP.no_mundo(n, b); E.location = (0.0, 2.5, 0.0)
    OB.aviao("av", (0.5, 1.0, 10000.0 * k), s=0.004, rot=-90)
    OB.rotulo_ref(0.22, 10000.0 * k - 0.13, "avião: 10 km", lado=1, tam=0.085, y=-0.3, cor=OB.AMBAR_ESC)
    OB.regua2(X_REGUA, 1.8, 7373.0, marcas_m=[2000, 4000, 6000], lado=1, rotulo="7,4 km", cor_num=OB.AMBAR_ESC)
    camera_palco(cz=1.2)


@item("palco_preto", "palco de medida (espaço): 21º passo e a Lua", 540, 960)
def i_palco_preto():
    OB.palco("preto", estrelas=True)
    n = 21; k = 2.0 ** -n
    eu_em()
    fila(n, [20, 19, 18])
    r = 1737400.0 * k
    OP.lua("lua", r, (0.58, 2.0, r))
    OB.rotulo_ref(0.36, 2 * r, "Lua: 3.474 km", lado=1, tam=0.085, y=-0.3)
    OB.regua2(X_REGUA, 1.8, 3774873.0, marcas_m=[1000000, 2000000, 3000000], lado=1, escuro=True, rotulo="3.775 km",
              fmt=lambda m: f"{m / 1000:,.0f}".replace(",", ".") + " km")
    camera_palco()


@item("palco_dubai", "palco em Dubai: 9º passo (922 m) e o Burj (828 m)", 540, 960)
def i_palco_dubai():
    n = 9; k = 2.0 ** -n
    OB.palco("dubai")
    def b():
        OB.dubai(0.0, 0.0, raio=420.0, n_torres=40); OB.burj("burj", 0.0, 0.0)
    E = SP.no_mundo(n, b, cont_u=0.0012); E.location = (0.55, 1.6, 0.0)
    eu_em()
    fila(n, [8, 7, 6])
    OB.caixa("linha_burj", (0.5, 0.01, 0.008), O3.brilha(OB.AMBAR_ESC, 1.0), (0.5, -0.3, 828.0 * k), cont=0.0)
    OB.rotulo_ref(0.3, 828.0 * k + 0.05, "Burj: 828 m", lado=1, tam=0.085, y=-0.3, cor=OB.AMBAR_ESC)
    OB.regua2(X_REGUA, 1.8, 921.6, marcas_m=[300, 600], lado=1, rotulo="922 m", cor_num=OB.AMBAR_ESC)
    camera_palco()


# ---------------------------------------------------------------- main
def main():
    argv = sys.argv[sys.argv.index("--") + 1:]
    if "--list" in argv:
        for k, d in ITENS.items():
            print(f"{k} | {d['titulo']}")
        return
    nome, out = argv[0], argv[1]
    esc = float(argv[argv.index("--scale") + 1]) if "--scale" in argv else 1.0
    d = ITENS[nome]
    lib.reset(int(d["w"] * esc), int(d["h"] * esc), 24, 20)
    sc = bpy.context.scene; sc.frame_start = sc.frame_end = 1
    d["fn"]()
    sc.frame_set(1); sc.render.filepath = out
    bpy.ops.render.render(write_still=True)


if __name__ == "__main__":
    main()
