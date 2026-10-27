"""Storyboard v2 de "E se cada passo dobrasse a sua altura?" (plano: personagem/passos/plano-de-cena-v2.md; ficha v2 aprovada em 25/10/2026).
Dois modos de imagem:
- MUNDO: onde ele está e o que sente. A rua é UMA só, em metros reais: ele anda por ela (a posição do boneco no passo n é EU_Y[n]) e passa
  pelo ponto de ônibus, pelo poste, pelo prédio de 5, de 10 e de 18 andares. O mundo entra num empty com escala 2^-n e é deslocado para o
  boneco ficar na origem com 1,8 de altura (no_mundo + E.location). Nada de texto, exceto as marcas de tempo da cronofotografia.
- PALCO: câmera ortográfica (sem perspectiva), régua à esquerda com o número ao lado, fantasmas dos tamanhos anteriores, a referência à direita.
blender -b -P story_passos2.py -- PLANO SAIDA.png [--scale 0.5] [--samples 16] | --list | --json ARQ"""
import os, sys, math, json, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy, lib
from lib import empty, srgb
from mathutils import Vector
import cena, props
import objetos3d_abrigo as O3, objetos3d_abrigo_b as O3B, cidade3d as C3, elenco3d_abrigo as E3
import objetos3d_passos as OP, objetos3d_passos_b as OB
import story_passos as SP
import ficha_passos as FP
import poses_passos as PP
import ik3_abrigo as IK
from heroi3d import esfera, tubo

SHOTS = {}
EU_ESC = SP.EU_ESC
H = SP.H_EU


def shot(nome, t0, t1, palavras, modo, lente, nota):
    def deco(fn):
        SHOTS[nome] = dict(t0=t0, t1=t1, palavras=palavras, modo=modo, lente=lente, nota=nota, fn=fn)
        return fn
    return deco


# ---------------------------------------------------------------- a rua (uma só, em metros reais)
def altura(n):
    return H * 2 ** n


def eu_y(n):
    """onde o boneco está (y, em metros) no passo n: cada passada tem 0,7 da altura do passo"""
    return -sum(0.7 * altura(i) for i in range(1, int(math.floor(n)) + 1))


LUGAR = dict(ponto=(-4.4, -0.6), moca=(-3.95, -1.25), onibus=(-1.9, -1.5),
             poste=(3.85, eu_y(2) + 2.5), relogio=(-4.3, eu_y(3) - 14.0),
             p5=(5.2 + 5.5 + 3.0, eu_y(3) + 5.0, 11.0), p10=(5.2 + 7.5 + 6.0, eu_y(4) + 8.0, 15.0), p18=(26.0, eu_y(5) + 18.0, 20.0),
             poca=(4.2, eu_y(4) - 3.0))


def limpa(caixas, prefixos=("pr", "arv", "poste", "carro", "lixeira", "fio")):
    """apaga as peças da rua (prédios, árvores, postes, carros, lixeiras) que entram nas áreas (xmin, xmax, ymin, ymax) em metros.
    O prédio do kit é feito de várias malhas soltas (uma por material: parede, claro, vidro...): se uma entra na área, sai o prédio inteiro
    (antes sobrava a caixa d'água flutuando)"""
    bpy.context.view_layer.update()
    grupos = {}
    for o in bpy.data.objects:
        if o.parent is None and o.name.startswith(prefixos):
            partes = o.name.split("_")
            chave = "_".join(partes[:2]) if o.name.startswith("pr") else o.name
            grupos.setdefault(chave, []).append(o.name)
    for chave, nomes in grupos.items():
        objs = []
        for nm in nomes:
            o = bpy.data.objects.get(nm)
            if o is not None:
                objs += [o] + list(o.children_recursive)
        pts = [ob.matrix_world @ Vector(c) for ob in objs if ob.type in ("MESH", "FONT") for c in ob.bound_box]
        if not pts:
            continue
        x0, x1 = min(p.x for p in pts), max(p.x for p in pts); y0, y1 = min(p.y for p in pts), max(p.y for p in pts)
        if any(x0 < c[1] and x1 > c[0] and y0 < c[3] and y1 > c[2] for c in caixas):
            for ob in list(reversed(objs)):
                if ob.name in bpy.data.objects:
                    bpy.data.objects.remove(ob, do_unlink=True)


def rua2(n, onibus_y=None, moca=None, extras=(), aberto=0, sem_carros_perto=True, ponto=None, livre_u=None, corredor_u=None, eu_x=0.0):
    """a rua do filme no passo n, com o boneco na origem da cena. extras: 'poste', 'p5', 'p10', 'p18', 'relogio', 'poca'"""
    k = 2.0 ** -n
    ey = eu_y(n)
    SP.ceu_dia()
    def build():
        cena.poly_mesh("chao_largo", [(-6000, -6000, -0.03), (6000, -6000, -0.03), (6000, 6000, -0.03), (-6000, 6000, -0.03)], props.FM("#8d9187"))
        C3.rua3d(dict(chao="#8d9187"), ey - max(60.0, 6.0 / k), ey + min(700.0, 70.0 / k), carros=True)
        if n >= 2:                                                     # o bairro em volta da rua (quarteirões), para a cidade não ser só uma rua
            OP.cidade_maquete(min(4000.0, 40.0 / k), passo=38.0, altura_max=20.0, altura_min=4.0, larg=(16, 30), ox=0.0, oy=ey, corredor=22.0, vazio=((aberto, 7.0 / k) if aberto else None), seed=11)
        for o in [o for o in bpy.data.objects if o.name.startswith("fio_cruza")]:
            bpy.data.objects.remove(o, do_unlink=True)
        areas = []
        if sem_carros_perto:
            r = 0.35 * altura(n) + 4.0
            areas.append((eu_x - r, eu_x + r, ey - r, ey + r))
            if livre_u:
                areas.append((-0.7 / k, 0.7 / k, ey - livre_u / k, ey + livre_u / k))
            if corredor_u:                                             # a frente dele livre até a câmera de lente longa (postes, árvores e carros saem)
                areas.append((eu_x - 5.0, eu_x + 5.0, ey - corredor_u / k, ey))
        com_ponto = (n <= 1) if ponto is None else ponto
        if com_ponto:
            OB.ponto_onibus("ponto", (LUGAR["ponto"][0], LUGAR["ponto"][1], 0.15), rot=90)
            areas.append((LUGAR["ponto"][0] - 2.2, LUGAR["ponto"][0] + 1.2, LUGAR["ponto"][1] - 2.2, LUGAR["ponto"][1] + 2.2))
        if (n <= 1 if moca is None else moca):
            h = E3.faz("moca", "moca"); h.raiz.scale = (EU_ESC * 0.97,) * 3
            h.pose(**h.pe_no_chao(**dict(SP.STAND, ombro=(-8, 10), cotovelo=(-20, -14)))); h.rosto(boca="reta", lid=0.0)
            h.raiz.location = (LUGAR["moca"][0], LUGAR["moca"][1], 0.15); h.raiz.rotation_euler.z = math.radians(-70)
        if onibus_y is not None:
            OB.onibus("onibus", (LUGAR["onibus"][0], onibus_y, 0.0), rot=0)
            areas.append((LUGAR["onibus"][0] - 1.6, LUGAR["onibus"][0] + 1.6, onibus_y - 7, onibus_y + 7))
        for ex in extras:
            if ex == "poste":
                px, py = LUGAR["poste"]
                C3.poste_luz("cmp_poste", (px, py, 0.15), lado=1)
                areas.append((px - 1.5, px + 1.5, py - 2.0, py + 2.0))
            elif ex in ("p5", "p10", "p18"):
                x, y, w = LUGAR[ex]
                andares = int(ex[1:])
                OB.predio_alto(ex, x, y, andares, w=w, cor={"p5": "#a59a86", "p10": "#9aa2a8", "p18": "#8f98a6"}[ex], balancim=(ex == "p18"), face_balancim="esq")
                areas.append((x - w / 2 - 1.0, x + w / 2 + 1.0, y - w * 0.45 - 1.0, y + w * 0.45 + 1.0))
            elif ex == "relogio":
                OB.relogio_rua("relogio", (LUGAR["relogio"][0], LUGAR["relogio"][1], 0.15), hora=(10, 8), seg=0.0)
                areas.append((LUGAR["relogio"][0] - 1, LUGAR["relogio"][0] + 1, LUGAR["relogio"][1] - 1, LUGAR["relogio"][1] + 1))
            elif ex == "poca":
                OB.poca("poca", (LUGAR["poca"][0], LUGAR["poca"][1], 0.0), rx=2.4, ry=1.6)
        limpa(areas)
    E = SP.no_mundo(n, build, cont_u=0.0035)
    E.location = (-eu_x * k, -ey * k, 0.0)
    if aberto:
        SP.abre_lado(E, aberto)
    return E


def em_u(n, xm, ym, zm=0.0):
    """ponto do mundo (metros) na cena do passo n (o boneco na origem)"""
    k = 2.0 ** -n
    return (xm * k, (ym - eu_y(n)) * k, zm * k)


def eu(pose=None, rosto=None, rot=0.0, escala=1.0, nome="eu", sombra=True, loc=(0, 0, 0)):
    """o 'eu' com 1,8 de altura (x escala), numa pose da ficha (PP.POSES) ou num dict de ângulos"""
    h = E3.faz("eu", nome); h.raiz.scale = (EU_ESC * escala,) * 3
    if isinstance(pose, str):
        PP.aplica(h, pose, escala=EU_ESC * escala)
    else:
        P = dict(SP.STAND); P.update(pose or {})
        h.pose(**h.pe_no_chao(**P))
        PP.assenta(h, 0.0)
    if rosto:
        r = dict(boca="reta", lid=0.0); r.update(rosto); h.rosto(**r)
    h.raiz.location.x += loc[0]; h.raiz.location.y += loc[1]; h.raiz.location.z += loc[2]
    h.raiz.rotation_euler.z = math.radians(rot)
    if sombra:
        cena.ground_disc(nome + "_sb", 0.42 * EU_ESC * escala, 0.28 * EU_ESC * escala, cena.amat(nome + "_sb_m", "#000000", 1.0, 0.32, ("radial", 1.1)), (loc[0], loc[1] + 0.05, 0.004), n=32)
    return h


def pe_de(h, s="F"):
    bpy.context.view_layer.update()
    return h.tornozelo[s].matrix_world.translation.copy()


def cam(loc, alvo, lente, fstop=5.6, foco=None, clip=None):
    c = SP.cam(loc, alvo, lente, fstop=fstop, foco=foco)
    if clip:
        c.data.clip_start = clip
    return c


def pombos(centro, n=6, raio=0.3, s=0.02, seed=3):
    rnd = random.Random(seed); m = OP.M("#3a3d44", "#24262c")
    for i in range(n):
        x, y, z = centro[0] + rnd.uniform(-raio, raio), centro[1] + rnd.uniform(-raio, raio), centro[2] + rnd.uniform(0, raio)
        for sx in (-1, 1):
            OB.caixa(f"pombo{i}_{sx}", (s, s * 0.25, s * 0.12), m, (x + sx * s * 0.45, y, z + s * 0.12), cont=0.0, rot=(0, -sx * 25, 0))


# ---------------------------------------------------------------- palco
def palco(tipo, n, ghosts, regua_topo_m, marcas=None, rotulo=None, cor_num=None, cz=0.98, vis=3.25, cx=-0.02, estrelas=False, fmt=None):
    OB.palco(tipo, estrelas=estrelas)
    FP.fila(n, ghosts)
    OB.regua2(FP.X_REGUA, 1.8, regua_topo_m, marcas_m=marcas, lado=1, rotulo=rotulo, cor_num=cor_num or (OB.AMBAR if tipo == "preto" else OB.AMBAR_ESC),
              escuro=(tipo == "preto"), fmt=fmt)
    return FP.camera_palco(cx=cx, cz=cz, vis=vis)


# ======================================================================== FALA 1
@shot("1A", 0.00, 1.28, "E se cada passo", "M", "14 mm, no asfalto, entre carros",
      "Impacto: o tênis gigante (passo 4, quase 30 m) acaba de pousar na rua; sombra no asfalto, poeira em anel, os pombos voando e os carros pequenos perto da sola.")
def p1A():
    n = 4
    rua2(n, onibus_y=None, moca=False, extras=("p10",))
    h = eu("contato")
    f = pe_de(h, "F")
    OP.poeira_pouso(f.x, f.y - 0.05, r=0.32)
    pombos((f.x + 0.25, f.y - 0.55, 0.12), n=7, raio=0.18, s=0.012)
    cam((f.x + 0.22, f.y - 0.62, 0.025), (f.x - 0.02, f.y + 0.1, 0.16), 14, fstop=4.0, foco=(f.x, f.y - 0.05, 0.05), clip=0.002)


@shot("1B", 1.28, 2.08, "que você desse", "M", "18 mm, grua da sola ao rosto",
      "A câmera sobe pela perna até o rosto lá em cima, contra o céu: ele olha para baixo, para nós. Na rua, pequenos, os carros e o prédio de 10 andares.")
def p1B():
    n = 4
    rua2(n, moca=False, extras=("p10",), aberto=1)
    eu(dict(cabeca=22, tronco=4), dict(boca="reta"))
    cam((0.3, -1.15, 0.12), (0.0, 0.0, 1.35), 18, fstop=5.6, foco=(0.0, 0.0, 1.5))


@shot("1C", 2.08, 3.58, "dobrasse a sua altura?", "P", "ortográfica, palco de dia",
      "A regra do filme: o boneco e, ao lado, a cópia exata com o dobro do tamanho. A régua marca 1x e 2x.")
def p1C():
    OB.palco("dia")
    eu(loc=(-0.42, 0.0, 0.0), escala=0.5, nome="eu1")
    eu(loc=(0.22, 0.0, 0.0), escala=1.0, nome="eu2")
    OB.regua2(-0.86, 1.8, 2.0, marcas_m=[1.0], lado=1, rotulo="2x", cor_num=OB.AMBAR_ESC, fmt=lambda m: "1x")
    OB.caixa("linha_1x", (0.5, 0.01, 0.008), O3.brilha(OB.AMBAR_ESC, 1.0), (-0.6, -0.3, 0.9), cont=0.0)
    FP.camera_palco(cx=-0.12, cz=0.98, vis=3.1)


# ======================================================================== FALA 2
@shot("2A", 3.58, 4.36, "Você começa", "M", "35 mm, na altura do peito, de lado",
      "Tamanho normal: ele no ponto de ônibus ao lado da moça; o ônibus chegando ao fundo da rua.")
def p2A():
    n = 0
    rua2(n, onibus_y=28.0)
    eu(dict(cabeca=2, olha=-10), dict(boca="reta"), loc=em_u(0, -3.0, -0.4), rot=-70, sombra=True)
    cam((-0.6, -3.4, 1.35), (-3.0, 3.0, 1.2), 28, fstop=5.6, foco=(-3.0, -0.4, 1.2))


@shot("2B", 4.36, 5.76, "com um metro e oitenta", "P", "ortográfica, palco de dia",
      "1,8 m na régua; ao lado, a porta de 2,1 m e a moça de 1,64 m.")
def p2B():
    palco("dia", 0, [], 1.8, marcas=[0.5, 1.0, 1.5], rotulo="1,8 m", cx=0.1, vis=3.5)
    eu()
    O3B.porta_comum3d("porta", (0.85, 0.8, 0), 1.0, abre=0.0, cor="#4f6e8a")
    OB.caixa("parede", (1.7, 0.2, 2.6), OP.M("#c8b8a0", "#a39480"), (0.85, 0.98, 1.3), cont=0.006)
    OB.rotulo_ref(0.5, 2.1, "porta: 2,1 m", tam=0.085, y=-0.3, cor=OB.AMBAR_ESC)
    FP.ator("moca", "moca", loc=(0.62, -0.2, 0.0), esc=0.97, rot=-10)


@shot("2C", 5.76, 7.10, "Depois do primeiro passo,", "M", "50 mm, perfil, rente ao chão",
      "O passo de perfil: o pé de trás empurra e passa; no meio do passo o corpo já cresce (aqui com 2,5 m).")
def p2C():
    n = 0.5
    rua2(0, onibus_y=60.0, moca=True, aberto=-1)
    eu("passagem", escala=2 ** 0.5, rot=0)
    cam((-3.4, -0.4, 0.6), (0.0, -0.1, 1.0), 50, fstop=4.0, foco=(0.0, 0.0, 1.0))


@shot("2D", 7.10, 7.69, "são três", "M", "16 mm, no pé",
      "O pé pousa ao lado do ônibus parado no ponto; ele já é mais alto que o teto.")
def p2D():
    n = 1
    rua2(n, onibus_y=-1.5)
    h = eu("contato")
    f = pe_de(h, "F")
    OP.poeira_pouso(f.x, f.y - 0.05, r=0.4)
    cam((f.x + 0.35, f.y - 0.7, 0.05), (f.x - 0.3, f.y + 0.3, 0.45), 16, fstop=4.0, foco=(f.x, f.y, 0.1), clip=0.003)


@shot("2E", 7.69, 8.80, "metros e meio", "P", "ortográfica, palco de dia",
      "O fantasma de 1,8 m, o boneco de 3,6 m e o ônibus (3,2 m) à direita: a cabeça passa o teto.")
def p2E():
    n = 1; k = 2.0 ** -n
    palco("dia", n, [0], altura(n), marcas=[1.0, 2.0, 3.0])
    eu()
    OB.onibus("onibus", (1.2, 2.0, 0.0), rot=0).scale = (k,) * 3
    OB.rotulo_ref(0.3, 3.2 * k, "ônibus: 3,2 m", tam=0.085, y=-0.3, cor=OB.AMBAR_ESC)


# ======================================================================== FALA 3
@shot("3A", 8.80, 9.38, "No segundo", "M", "16 mm, no pé",
      "Outro pouso, pelo mesmo pé e no mesmo lugar do quadro: a rua menor em volta.")
def p3A():
    n = 2
    rua2(n)
    h = eu("contato")
    f = pe_de(h, "F")
    OP.poeira_pouso(f.x, f.y - 0.05, r=0.45)
    cam((f.x + 0.35, f.y - 0.7, 0.05), (f.x - 0.3, f.y + 0.3, 0.45), 16, fstop=4.0, foco=(f.x, f.y, 0.1), clip=0.003)


@shot("3B", 9.38, 10.40, "passo, são", "M", "28 mm, três quartos, baixa",
      "Ele ao lado do poste de luz da rua (7,2 m): a cabeça na altura da luminária, que ele olha de perto.")
def p3B():
    n = 2
    rua2(n, extras=("poste",), moca=False)
    eu(dict(cabeca=-10, olha=-18), dict(boca="o"))
    cam((-1.0, -1.9, 0.9), (0.55, 0.3, 1.5), 30, fstop=5.6, foco=(0.0, -0.05, 1.5))


@shot("3C", 10.40, 11.48, "sete metros.", "P", "ortográfica, palco de dia",
      "Fila: 1,8 e 3,6 em fantasma, o boneco de 7,2 m e o poste de 7,2 m à direita.")
def p3C():
    n = 2; k = 2.0 ** -n
    palco("dia", n, [1, 0], altura(n), marcas=[2.0, 4.0, 6.0])
    eu()
    p = C3.poste_luz("poste", (0, 0, 0), lado=1); p.scale = (k,) * 3; p.location = (0.48, 0.6, 0.0)
    OB.rotulo_ref(0.36, 7.2 * k + 0.08, "poste: 7,2 m", tam=0.085, y=-0.3, cor=OB.AMBAR_ESC)


# ======================================================================== FALA 4
@shot("4A", 11.48, 12.52, "No terceiro,", "M", "16 mm, no cruzamento",
      "O pé pousa no meio da rua; os carros freiam em volta, longe da sola.")
def p4A():
    n = 3
    rua2(n, extras=("p5",))
    h = eu("contato")
    f = pe_de(h, "F")
    OP.poeira_pouso(f.x, f.y - 0.05, r=0.45)
    cam((f.x - 0.4, f.y - 0.7, 0.05), (f.x + 0.2, f.y + 0.3, 0.45), 16, fstop=4.0, foco=(f.x, f.y, 0.1), clip=0.003)


@shot("4B", 12.52, 13.92, "são quinze metros.", "P", "ortográfica, palco de dia",
      "Fila até 14,4 m; o prédio de 5 andares (15 m) à direita.")
def p4B():
    n = 3; k = 2.0 ** -n
    palco("dia", n, [2, 1, 0], altura(n), marcas=[5.0, 10.0])
    eu()
    E = SP.no_mundo(n, lambda: OB.predio_alto("cmp", 0.0, 0.0, 5, w=8.0, cor="#a59a86", terraco=False)); E.location = (0.36 + 4.0 * k, 1.5, 0.0)
    OB.rotulo_ref(0.32, 15.0 * k + 0.13, "prédio: 15 m", tam=0.085, y=-0.3, cor=OB.AMBAR_ESC)


@shot("4C", 13.92, 15.12, "Se você tropeçar,", "M", "28 mm, lateral",
      "A ponta do tênis de trás prende no meio-fio: o tronco vai à frente, os braços abrem de contrapeso, a boca em O.")
def p4C():
    n = 3
    rua2(n, extras=("p5",), aberto=-1, moca=False)
    eu("tropeco")
    cam((-2.4, -0.35, 0.85), (0.0, -0.25, 0.85), 28, fstop=5.6, foco=(0.0, -0.2, 0.85))


@shot("4D", 15.12, 16.76, "leva quase dois segundos", "M", "35 mm, lateral, cronofotografia",
      "A queda em três tempos, da esquerda para a direita: começo (0 s), meio (0,85 s) e fim (1,7 s); o do meio é sólido e os outros dois são fantasmas.")
def p4D():
    n = 3
    rua2(n, extras=("p5",), aberto=-1, moca=False, livre_u=2.8)
    a = eu("queda1", nome="fq1", sombra=False, loc=(0, 0.95, 0)); OB.fantasma(a)
    eu("queda2", nome="eu", loc=(0, 0.05, 0))
    c = eu("queda3", nome="fq3", sombra=False, loc=(0, -0.95, 0)); OB.fantasma(c)
    for t, y, z in (("0 s", 0.95, 2.05), ("0,85 s", 0.05, 2.05), ("1,7 s", -0.95, 2.05)):
        OP.texto("tt" + t, t, 0.11, (-0.1, y, z), cor="#ffffff", forca=1.3, rot=(math.pi / 2, 0, -math.pi / 2))
    cam((-5.4, 0.0, 0.9), (0.0, 0.0, 0.85), 24, fstop=8.0, foco=(0.0, 0.0, 0.8))


@shot("4E", 16.76, 17.36, "para cair.", "M", "16 mm, rente ao chão, nas mãos",
      "As mãos espalmadas chegam ao asfalto e seguram o corpo, sem dano; poeira.")
def p4E():
    n = 3
    rua2(n, extras=("p5",), moca=False, aberto=-1)
    h = eu("queda3")
    bpy.context.view_layer.update()
    m = h.punho["F"].matrix_world.translation
    OP.poeira_pouso(m.x, m.y, r=0.35)
    cam((m.x - 0.55, m.y - 0.45, 0.06), (m.x + 0.1, m.y + 0.2, 0.18), 16, fstop=4.0, foco=(m.x, m.y, 0.05), clip=0.003)


# ======================================================================== FALA 5
@shot("5A", 17.36, 18.30, "No quarto,", "M", "20 mm, três quartos",
      "Ele se levanta, uma mão no joelho, e já vai dar o passo.")
def p5A():
    n = 4
    rua2(n, extras=("p10",), moca=False, aberto=-1)                  # (a poça fica para o 5E: a mão dele encostava na borda dela)
    eu("levanta")
    cam((-1.3, -1.6, 0.5), (0.0, -0.1, 0.6), 20, fstop=5.6, foco=(0.0, -0.1, 0.6))


@shot("5B", 18.30, 20.06, "são quase trinta metros.", "P", "ortográfica, palco de dia",
      "Fila até 28,8 m; o prédio de 10 andares (30 m) à direita.")
def p5B():
    n = 4; k = 2.0 ** -n
    palco("dia", n, [3, 2, 1], altura(n), marcas=[10.0, 20.0])
    eu()
    E = SP.no_mundo(n, lambda: OB.predio_alto("cmp", 0.0, 0.0, 10, w=14.0, cor="#9aa2a8", terraco=False)); E.location = (0.36 + 7.0 * k, 1.5, 0.0)
    OB.rotulo_ref(0.32, 30.0 * k + 0.13, "prédio: 30 m", tam=0.085, y=-0.3, cor=OB.AMBAR_ESC)


@shot("5C", 20.06, 21.12, "Sua voz leva", "M", "85 mm, close de lado",
      "Ele grita para baixo com as mãos em volta da boca; as ondas saem para baixo e para a frente, longe do rosto.")
def p5C():
    n = 4
    rua2(n, extras=("p10",), moca=False)
    h = eu("grito")
    b = IK.boca_de(h)
    for i in range(3):
        O3.anel(f"arco{i}", 0.07 + 0.05 * i, 0.004, O3.brilha("#ffffff", 1.6 - 0.3 * i), None, (b.x, b.y - 0.12 - 0.07 * i, b.z - 0.04 - 0.07 * i), eixo="X", seg=48, a0=-60, a1=60, contorno=0.0)
    SP.cam_v((0.07, -0.05, 1.5), 0.8, 85, az=-40, el=-16, fstop=2.8, foco=(b.x, b.y, b.z))


@shot("5D", 21.12, 22.48, "um décimo de segundo", "M", "35 mm, perfil do corpo inteiro",
      "A frente da onda desce em volta do corpo, marcada em três tempos: 0, 0,04 e 0,08 s.")
def p5D():
    n = 4
    rua2(n, extras=("p10",), aberto=-1, moca=False)
    eu("grito")
    for i, (z, t) in enumerate(((1.45, "0 s"), (0.85, "0,04 s"), (0.18, "0,08 s"))):
        O3.anel(f"som{i}", 0.42 + 0.08 * i, 0.007, O3.brilha("#ffffff", 1.6 - 0.35 * i), None, (0.0, -0.05, z), eixo="Z", seg=64, contorno=0.0)
        OP.texto(f"tt{i}", t, 0.09, (-0.0, 0.5, z + 0.04), cor="#ffffff", forca=1.3, rot=(math.pi / 2, 0, -math.pi / 2), alinha="RIGHT")
    cam((-3.1, -0.05, 0.85), (0.0, 0.05, 0.85), 35, fstop=8.0, foco=(0.0, 0.0, 0.85))


@shot("5E", 22.48, 23.58, "para chegar aos pés.", "M", "20 mm, rente ao chão",
      "Só agora a onda chega à poça ao lado do tênis e a água treme em círculos.")
def p5E():
    n = 4
    rua2(n, extras=("p10", "poca"), moca=False)
    eu("grito")
    px, py, _ = em_u(n, *LUGAR["poca"])
    OB.ondas_poca("onda", (px, py, 0.0), n=3, r0=0.03, passo=0.03)
    cam((px + 0.3, py - 0.5, 0.2), (px - 0.08, py + 0.1, 0.02), 20, fstop=4.0, foco=(px, py, 0.0), clip=0.003)


# ======================================================================== FALA 6
@shot("6A", 23.58, 24.96, "No quinto passo,", "M", "20 mm, de baixo",
      "O pé pousa na rua ao lado do prédio de 18 andares; a sombra dele cobre a fachada.")
def p6A():
    n = 5
    rua2(n, extras=("p18",), moca=False, aberto=-1)
    h = eu("contato")
    f = pe_de(h, "F")
    OP.poeira_pouso(f.x, f.y - 0.05, r=0.4)
    x, y, w = LUGAR["p18"]; k = 2.0 ** -n
    xs, ys, _ = em_u(n, x - w / 2 - 0.3, y)
    cena.poly_mesh("sombra_fachada", [(xs, ys - w * 0.45 * k, 0.0), (xs, ys + w * 0.2 * k, 0.0), (xs, ys + w * 0.2 * k, 1.5), (xs, ys - w * 0.45 * k, 1.3)],
                   cena.amat("sombra_f_m", "#101418", 1.0, 0.35))
    cam((f.x - 0.95, f.y - 0.55, 0.05), (f.x + 0.2, f.y + 0.35, 0.75), 20, fstop=5.6, foco=(f.x, f.y, 0.1), clip=0.003)


@shot("6B", 24.96, 26.76, "são quase sessenta metros.", "P", "ortográfica, palco de dia",
      "Fila até 57,6 m; o prédio de 18 andares (55 m) com a linha âmbar no topo: a cabeça passa a linha.")
def p6B():
    n = 5; k = 2.0 ** -n
    palco("dia", n, [4, 3, 2], altura(n), marcas=[20.0, 40.0])
    eu()
    E = SP.no_mundo(n, lambda: OB.predio_alto("cmp", 0.0, 0.0, 18, w=20.0, cor="#8f98a6", terraco=True)); E.location = (0.36 + 10.0 * k, 1.5, 0.0)
    OB.caixa("linha_topo", (0.72, 0.01, 0.008), O3.brilha(OB.AMBAR_ESC, 1.0), (0.1, -0.3, 54.0 * k), cont=0.0)
    OB.rotulo_ref(0.32, 57.0 * k + 0.13, "prédio: 55 m", tam=0.085, y=-0.3, cor=OB.AMBAR_ESC)


def mundo_metros(ceu=True):
    """cena em METROS reais (k = 1), para os planos de perto no alto do prédio: o boneco entra com a escala do passo"""
    if ceu:
        SP.ceu_dia()
    cena.poly_mesh("chao_largo", [(-3000, -3000, -0.03), (3000, -3000, -0.03), (3000, 3000, -0.03), (-3000, 3000, -0.03)], props.FM("#8d9187"))


def gigante(n, pose=None, rosto=None, nome="eu"):
    """o boneco com a altura real do passo n, numa cena em metros"""
    return eu(pose, rosto, escala=2 ** n, nome=nome, sombra=False)


@shot("6C", 26.76, 29.02, "Isso é mais alto que um prédio de dezoito andares.", "M", "28 mm, no terraço do 18º andar",
      "Do terraço: o parapeito, a caixa d'água e o zelador olhando para cima; acima do parapeito aparece o alto da cabeça do gigante, com o cabelo.")
def p6C():
    mundo_metros()
    x, y, w = 26.0, 18.0, 20.0                                   # o prédio na rua (em relação ao boneco, que está na origem)
    OB.predio_alto("p18", x, y, 18, w=w, cor="#8f98a6", balancim=False)
    gigante(5, dict(cabeca=4, olha=30), dict(boca="reta"))
    FP.ator("zelador", "zel", loc=(x - 6.6, y - 8.0, 54.86), rot=-125, pose=dict(cabeca=-30, tronco=-6, ombro=(2, 2), cotovelo=(-8, -8), abre=(4, 4)), rosto=dict(boca="o"))
    cam((x - 4.0, y - 8.0, 58.4), (2.0, 0.0, 52.5), 24, fstop=8.0, foco=(x - 6.6, y - 8.0, 55.6), clip=0.05)


@shot("6D", 29.02, 30.26, "O seu cabelo", "M", "85 mm, no balancim",
      "No balancim do alto do prédio, o limpador de janela estica o braço e segura um palito de dente ao lado de um fio solto do cabelo do gigante.")
def p6D():
    mundo_metros()
    x, y, w = 26.0, 18.0, 20.0
    estado = {}
    def limp(px, py, pz, rz):
        h = E3.faz("limpador", "limp"); h.raiz.scale = (EU_ESC,) * 3
        h.pose(**h.pe_no_chao(**dict(SP.STAND))); h.raiz.location = (px, py, pz); h.raiz.rotation_euler.z = rz
        PP.assenta(h, pz)
        estado["h"] = h
    OB.predio_alto("p18", x, y, 18, w=w, cor="#8f98a6", balancim=True, face_balancim="esq", limpador=limp)
    g = gigante(5, dict(cabeca=2, olha=24), dict(boca="reta"))
    bpy.context.view_layer.update()
    lh = estado["h"]
    c = g.cabeca.matrix_world.translation + Vector((0, 0, g.R * 32 * EU_ESC))
    raiz_fio = c + Vector((g.R * 32 * EU_ESC * 0.92, 0.0, g.R * 32 * EU_ESC * 0.25))
    ombro = lh.ombro["F"].matrix_world.translation
    ponta = Vector((ombro.x - 0.55, ombro.y - 0.05, ombro.z + 0.12))
    tubo("fio_solto", [tuple(raiz_fio), tuple(raiz_fio.lerp(ponta, 0.5) + Vector((0, 0, 0.6))), tuple(ponta + Vector((-0.02, 0, 0.0)))], [0.0012] * 3,
         OP.M("#2a1c16", "#120c09", "#6a4a3a"), None, seg=10, tampa=4, contorno=0.0)
    P = IK.braco_pose(lh, "F", tuple(ponta + Vector((0.05, 0.0, -0.07))), dict(lh._ultima) if hasattr(lh, "_ultima") else None, nome="limp")
    lh.pose(**P); lh.rosto(boca="o", lid=0.0); bpy.context.view_layer.update()
    m = lh.punho["F"].matrix_world.translation
    OP.palito("palito", (m.x - 0.02, m.y - 0.01, m.z + 0.035), 0.002, 0.065, eixo="Z")
    cam((m.x - 1.3, m.y - 0.8, m.z + 0.25), (m.x, m.y, m.z + 0.05), 35, fstop=5.6, foco=(m.x, m.y, m.z + 0.04), clip=0.01)


@shot("6E", 30.26, 32.72, "tem a grossura de um palito de dente.", "P", "macro 100 mm, régua em mm",
      "O fio (com as escamas) e o palito lado a lado sobre a régua em mm: 2,4 mm e 2 mm.")
def p6E():
    FP.estudio("#e6e8e4", "#d9dcd6")
    OB.fio_escamas("fio", (-0.32, 0.0, 0.25), 0.48, 3.0, eixo="Z")
    OP.palito("palito", (0.32, 0.0, 0.25), 0.4, 3.0, eixo="Z")
    OB.regua_macro("reg", (0.0, -0.3, -1.55), 2.0, 0.2, 5, "mm", larg=0.32)
    OP.texto("t_fio", "fio: 2,4 mm", 0.15, (-0.04, -0.3, 1.95), cor=OB.AMBAR_ESC, forca=1.0, alinha="RIGHT")
    OP.texto("t_pal", "palito: 2 mm", 0.15, (0.04, -0.3, 1.95), cor=OB.AMBAR_ESC, forca=1.0, alinha="LEFT")
    bpy.data.objects["chao_est"].location.z = -4.0
    cam((0.0, -5.0, 0.0), (0.0, 0.0, 0.1), 50, fstop=8.0, foco=(0.0, -0.1, 0.0))


# ======================================================================== FALA 7
@shot("7A", 32.72, 33.96, "Nessa altura,", "M", "35 mm, três quartos",
      "Ele cansado: a mão no peito, a respiração funda, a cidade lá embaixo.")
def p7A():
    n = 5
    rua2(n, extras=("p18",), moca=False)
    eu("respira")
    cam((-0.8, -1.5, 1.35), (0.0, 0.0, 1.35), 35, fstop=4.0, foco=(0.0, -0.1, 1.4))


def raio_x_base(cz=0.98, vis=3.25, cx=-0.02):
    OB.palco("preto")
    h = eu(nome="eu"); OB.raio_x(h)
    zc = 0.72 * H
    OB.coracao("cor", (0.05, -0.02, zc), s=1.0)
    tubo("vaso", [(0.05, -0.02, zc + 0.05), (0.04, -0.01, zc + 0.2), (0.0, 0.0, 1.5), (0.0, 0.0, 1.66)], [0.014] * 4, O3.brilha("#ff4a3a", 1.6), None, seg=16, tampa=4, contorno=0.0)
    for i in range(6):
        u = (i + 0.5) / 6
        esfera(f"pulso{i}", 0.018, 0.018, 0.024, O3.brilha("#ffd0c0", 2.0), None, (0.05 - 0.05 * u, -0.015, zc + 0.06 + (1.62 - zc - 0.06) * u), contorno=0.0, seg=12, an=8)
    return h, zc


@shot("7B", 33.96, 36.34, "o coração precisa de mais de uma atmosfera e meia", "P", "ortográfica, raio X",
      "O corpo vira silhueta translúcida; o coração vermelho bate e um manômetro ligado a ele marca 1,65 atm.")
def p7B():
    h, zc = raio_x_base()
    OP.manometro("man", (0.62, -0.2, zc), 0.22, 1.65, "1,65 atm", faixa=(0.0, 2.0), zona_vermelha=1.5)
    tubo("mangueira", [(0.08, -0.04, zc), (0.25, -0.12, zc - 0.06), (0.4, -0.2, zc)], [0.008] * 3, OP.M("#3a3f46"), None, seg=10, tampa=4, contorno=0.002)
    FP.camera_palco(cx=0.28, cz=1.15, vis=2.2)


@shot("7C", 36.34, 38.76, "de pressão para levar o sangue até a cabeça.", "P", "ortográfica, raio X, vertical",
      "O vaso do coração até a cabeça com o sangue subindo em pulsos; a chave âmbar ao lado marca a distância: 16 m.")
def p7C():
    h, zc = raio_x_base()
    OB.caixa("chave_16", (0.012, 0.012, H - zc), O3.brilha(OP.AMBAR, 1.5), (-0.3, -0.05, (H + zc) / 2), cont=0.0)
    for z in (zc, H):
        OB.caixa(f"chave_p{z:.2f}", (0.06, 0.012, 0.012), O3.brilha(OP.AMBAR, 1.5), (-0.27, -0.05, z), cont=0.0)
    OP.texto("t16", "16 m", 0.09, (-0.34, -0.05, (H + zc) / 2), alinha="RIGHT")
    FP.camera_palco(cx=-0.22, cz=1.4, vis=1.6)


# ======================================================================== FALA 8
def pe_cidade(n, rotulo):
    SP.mundo_cidade(n, raio_u=14.0, livre=3.0)
    h = eu("contato")
    f = pe_de(h, "F")
    OP.poeira_pouso(f.x, f.y - 0.05, r=0.45)
    OP.texto("n_pe", rotulo, 0.13, (f.x - 0.78, f.y + 0.15, 0.55), cor=OP.AMBAR, forca=1.8, rot=(math.pi / 2, 0, math.radians(27)), alinha="CENTER")
    cam((f.x + 0.35, f.y - 0.7, 0.05), (f.x - 0.3, f.y + 0.3, 0.45), 16, fstop=4.0, foco=(f.x, f.y, 0.1), clip=0.003)


@shot("8A", 38.76, 39.18, "No nono,", "M", "16 mm, no pé", "Sexto passo: o pé pousa, a cidade vira maquete. 115 m.")
def p8A():
    pe_cidade(6, "115 m")


@shot("8B", 39.18, 39.60, "", "M", "16 mm, no pé", "Sétimo passo: 230 m.")
def p8B():
    pe_cidade(7, "230 m")


@shot("8C", 39.60, 40.02, "você", "M", "16 mm, no pé", "Oitavo passo: 461 m.")
def p8C():
    pe_cidade(8, "461 m")


@shot("8D", 40.02, 40.42, "passa o", "M", "16 mm, no pé", "Nono passo: 922 m.")
def p8D():
    pe_cidade(9, "922 m")


def dubai_palco(n=9, burj_x=0.55):
    k = 2.0 ** -n
    OB.palco("dubai")
    E = SP.no_mundo(n, lambda: (OB.dubai(0.0, 0.0, raio=420.0, n_torres=40), OB.burj("burj", 0.0, 0.0)), cont_u=0.0012); E.location = (burj_x, 1.6, 0.0)
    return k


@shot("8E", 40.42, 41.48, "Burj Khalifa,", "P", "ortográfica, Dubai",
      "O Burj Khalifa de verdade (828 m) no centro de Dubai; o boneco de 922 m ao lado; linha âmbar no topo da agulha, e a cabeça passa.")
def p8E():
    k = dubai_palco()
    eu()
    FP.fila(9, [8, 7, 6])
    OB.caixa("linha_burj", (0.5, 0.01, 0.008), O3.brilha(OB.AMBAR_ESC, 1.0), (0.5, -0.3, 828.0 * k), cont=0.0)
    OB.rotulo_ref(0.3, 828.0 * k + 0.05, "Burj: 828 m", tam=0.085, y=-0.3, cor=OB.AMBAR_ESC)
    OB.regua2(FP.X_REGUA, 1.8, 921.6, marcas_m=[300, 600], lado=1, rotulo="922 m", cor_num=OB.AMBAR_ESC)
    FP.camera_palco()


@shot("8F", 41.48, 43.90, "que tem oitocentos e vinte e oito metros.", "P", "85 mm, na altura da ponta da agulha",
      "A câmera na altura da ponta da agulha: a ponta fica na altura do rosto dele, que olha para ela.")
def p8F():
    k = dubai_palco(burj_x=0.42)
    eu(dict(olha=34, cabeca=6), dict(boca="reta"))
    z = 828.0 * k
    cam((0.18, -5.2, z), (0.2, 0.0, z), 85, fstop=5.6, foco=(0.1, 0.0, z))


# ======================================================================== FALA 9
@shot("9A", 43.90, 45.28, "No décimo,", "M", "16 mm, no pé", "O pé pousa; a cidade inteira cabe em volta do tênis, como uma maquete.")
def p9A():
    pe_cidade(10, "1,8 km")


@shot("9B", 45.28, 46.96, "são quase dois quilômetros:", "P", "ortográfica, palco de dia",
      "Fila até 1,8 km (os primeiros tamanhos já são pontos) e o Burj em fantasma, na altura do joelho.")
def p9B():
    n = 10; k = 2.0 ** -n
    palco("dia", n, [9, 8, 7, 6, 5], altura(n), marcas=[500, 1000, 1500])
    eu()
    E = SP.no_mundo(n, lambda: OB.burj("burj", 0.0, 0.0)); E.location = (0.45, 1.0, 0.0)
    OB.fantasma_obj([o for o in bpy.data.objects if o.name.startswith("burj") and o.parent is not None and o.parent.name.startswith("mundo")])
    OB.rotulo_ref(0.3, 828.0 * k + 0.05, "Burj: 828 m", tam=0.085, y=-0.3, cor=OB.AMBAR_ESC)


@shot("9C", 46.96, 49.64, "o cabelo tem a grossura de uma lata de refrigerante", "P", "macro 100 mm, régua em cm",
      "O fio e a lata lado a lado sobre a régua em cm: 7,7 cm e 6,6 cm.")
def p9C():
    FP.estudio("#e6e8e4", "#d9dcd6")
    OB.fio_escamas("fio", (-0.42, 0.0, 0.25), 0.62, 3.0, eixo="Z", n=10)
    OP.lata("lata", (0.45, 0.0, -0.45), 0.53, 1.0, eixo="Z")
    OB.regua_macro("reg", (0.0, -0.3, -1.55), 2.4, 0.08, 10, "cm", larg=0.32)
    OP.texto("t_fio", "fio: 7,7 cm", 0.15, (-0.04, -0.3, 1.95), cor=OB.AMBAR_ESC, forca=1.0, alinha="RIGHT")
    OP.texto("t_lat", "lata: 6,6 cm", 0.15, (0.08, -0.3, 0.2), cor=OB.AMBAR_ESC, forca=1.0, alinha="LEFT")
    bpy.data.objects["chao_est"].location.z = -4.0
    cam((0.0, -5.0, 0.0), (0.0, 0.0, 0.1), 50, fstop=8.0, foco=(0.0, -0.1, 0.0))


@shot("9D", 49.64, 50.72, "e a vista chega", "M", "24 mm, por cima do ombro",
      "O que ele vê da cabeça: o chão de campos e cidades, o mar de um lado e a serra do outro, até o horizonte.")
def p9D():
    n = 10; k = 2.0 ** -n
    SP.ceu_dia()
    def build():
        cena.poly_mesh("chao_largo", [(-400000, -400000, -0.03), (400000, -400000, -0.03), (400000, 400000, -0.03), (-400000, 400000, -0.03)],
                       OP.mat_planeta("campo_m", "#8aa37a", "#b9b08e", escala=0.00004, limiar=0.5, sombra=0.9))
        cena.poly_mesh("mar", [(-400000, -400000, 0.0), (-25000, -400000, 0.0), (-45000, 0, 0.0), (-400000, 0, 0.0)], props.FM("#3f7fb0"))
        rnd = random.Random(5)
        for i in range(14):
            x = rnd.uniform(20000, 90000); y = rnd.uniform(-160000, -70000)
            O3.cilindro(f"serra{i}", rnd.uniform(14000, 26000), rnd.uniform(5000, 9000), OP.M("#7c8a74", "#5e6a58"), None, (x, y, 2500.0), seg=7, r2=900.0, contorno=0.0)
        for ox, oy in ((0, -8000), (-12000, -42000), (15000, -60000)):
            OP.cidade_maquete(2400.0, passo=95.0, altura_max=80.0, ox=ox, oy=oy, seed=abs(oy) % 97)
    SP.no_mundo(n, build, cont_u=0.0006)
    eu(dict(cabeca=6), sombra=False)
    cam((0.5, 0.55, 2.05), (-0.8, -40.0, 1.0), 20, fstop=11.0, foco=(0.0, 0.0, 1.5))


@shot("9E", 50.72, 52.80, "a cento e cinquenta quilômetros.", "P", "ortográfica, diagrama de perfil",
      "Diagrama (curva exagerada): a Terra de lado, ele em pé sobre ela e a linha de visão saindo do olho até tocar o horizonte: 150 km.")
def p9E():
    OB.palco("dia")
    R = 3.0
    OP.terra("terra_d", R, (0.0, 0.6, -R - 0.03))
    eu()
    th = math.acos(R / (R + 1.66))
    hx, hz = R * math.sin(th), R * math.cos(th) - R
    tubo("visao", [(0.04, -0.4, 1.66), (hx, -0.4, hz)], [0.008, 0.008], O3.brilha(OB.AMBAR_ESC, 1.0), None, seg=8, tampa=2, contorno=0.0)
    esfera("ponto_h", 0.03, 0.03, 0.03, O3.brilha(OB.AMBAR_ESC, 1.0), None, (hx, -0.4, hz), contorno=0.0, seg=12, an=8)
    OP.texto("t150", "150 km", 0.16, ((0.04 + hx) / 2 + 0.1, -0.45, (1.66 + hz) / 2 + 0.16), cor=OB.AMBAR_ESC, forca=1.0, rot=(math.pi / 2, math.atan2(1.66 - hz, hx - 0.04), 0))
    OP.texto("t_fora", "curva fora de escala", 0.07, (1.9, -0.45, 1.95), cor="#5a5e60", forca=1.0)
    FP.camera_palco(cx=1.0, cz=0.55, vis=5.2)


# ======================================================================== FALA 10
@shot("10A", 52.80, 54.28, "Com doze passos,", "M", "16 mm, no pé, nas nuvens", "O pé atravessa a camada de nuvens e pousa; as nuvens se abrem em volta da canela.")
def p10A():
    SP.mundo_ar(12, nuvens_z=(1500.0, 2900.0), raio_u=14.0, n_nuv=34)
    h = eu("contato")
    f = pe_de(h, "F")
    cam((f.x + 0.6, f.y - 1.1, 0.1), (f.x, f.y - 0.1, 0.65), 16, fstop=4.0, foco=(f.x, f.y - 0.2, 0.3))


@shot("10B", 54.28, 55.88, "são sete quilômetros.", "P", "ortográfica, palco alto",
      "Régua até 7,4 km; a faixa de nuvens na altura do joelho; um avião de cruzeiro (10 km) acima da cabeça.")
def p10B():
    n = 12; k = 2.0 ** -n
    palco("azul", n, [11, 10, 9], 7373.0, marcas=[2000, 4000, 6000], rotulo="7,4 km", cz=1.2)
    eu()
    E = SP.no_mundo(n, lambda: OP.nuvens(1800.0, 9000.0, n=9, seed=6, tam=(1400, 2600))); E.location = (0.0, 2.5, 0.0)
    OB.aviao("av", (0.5, 1.0, 10000.0 * k), s=0.004, rot=-90)
    OB.rotulo_ref(0.22, 10000.0 * k - 0.13, "avião: 10 km", tam=0.085, y=-0.3, cor=OB.AMBAR_ESC)


@shot("10C", 55.88, 56.98, "Na altura da boca,", "M", "50 mm, rosto de lado", "Ele puxa o ar com a boca aberta; o hálito sai para a frente em fumaça de frio.")
def p10C():
    SP.mundo_ar(12, nuvens_z=(1500.0, 2900.0), raio_u=14.0, n_nuv=34)
    h = eu("respira")
    b = IK.boca_de(h)
    mp = cena.amat("sopro_m", "#ffffff", 1.0, 0.75, ("radial", 1.1))
    for i, (dy, dz, r) in enumerate(((-0.12, 0.0, 0.025), (-0.19, 0.01, 0.035), (-0.27, 0.025, 0.05), (-0.37, 0.04, 0.065))):
        d = cena.disc(f"sopro{i}", r, mp, (b.x, b.y + dy, b.z + dz)); d.rotation_euler.z = math.radians(90)
    SP.cam_v((0.0, -0.15, 1.46), 1.2, 50, az=55, el=-14, fstop=2.8, foco=(b.x, b.y, b.z))


@shot("10D", 56.98, 59.10, "o ar tem menos da metade da pressão do chão.", "P", "ortográfica, palco alto",
      "Ao lado da régua, uma coluna de ar: pontinhos densos no chão e ralos na boca; dois manômetros: chão 1,00 atm e boca 0,47 atm.")
def p10D():
    n = 12
    palco("azul", n, [], 7373.0, marcas=[2000, 4000, 6000], rotulo="7,4 km", cz=1.0)
    eu()
    rnd = random.Random(3); m = O3.brilha("#ffffff", 1.3)
    Hs = 8000.0 * 2.0 ** -n
    for i in range(420):
        z = -Hs * math.log(1.0 - rnd.random() * (1.0 - math.exp(-1.8 / Hs)))
        esfera(f"ar{i}", 0.008, 0.008, 0.008, m, None, (rnd.uniform(0.42, 0.62), rnd.uniform(-0.2, 0.2), z), contorno=0.0, seg=6, an=4)
    zb = 0.85 * H
    OP.manometro("m_chao", (0.7, -0.25, 0.26), 0.17, 1.0, "1,00", sub="chão", faixa=(0.0, 1.2), zona_vermelha=9)
    OP.manometro("m_boca", (0.7, -0.25, zb), 0.17, 0.47, "0,47", sub="boca", faixa=(0.0, 1.2), zona_vermelha=9)
    OB.caixa("linha_boca", (0.5, 0.01, 0.008), O3.brilha(OB.AMBAR_ESC, 1.0), (0.4, -0.3, zb), cont=0.0)
    FP.camera_palco(cx=0.0, cz=1.0)


# ======================================================================== FALA 11
@shot("11A", 59.10, 60.22, "No vigésimo primeiro,", "M", "24 mm, de lado", "O pé pousa na curva da Terra; a atmosfera inteira é uma faixa azul fina na altura do tornozelo.")
def p11A():
    SP.ceu_espaco()
    SP.terra_sob_o_pe(21, folga=0.03)
    eu("contato")
    cam((2.0, -2.5, 0.55), (0.0, 0.0, 0.45), 24, fstop=8.0, foco=(0.0, 0.0, 0.6))


@shot("11B", 60.22, 61.46, "você já é mais alto", "M", "35 mm, de frente", "Ele vira a cabeça para a Lua, que aparece no céu preto atrás dele, na direção de verdade.")
def p11B():
    SP.ceu_espaco()
    SP.terra_sob_o_pe(21, folga=0.03)
    eu("olha_lado")
    P = Vector((-1.7, -2.1, 1.25)); T = Vector((0.15, 0.0, 1.45))
    fw = (T - P).normalized(); rt = fw.cross(Vector((0, 0, 1))).normalized(); up = rt.cross(fw).normalized()
    M = P + 100.0 * (fw + 0.34 * rt + 0.16 * up)
    OP.lua("lua", 8.0, tuple(M))
    cam(tuple(P), tuple(T), 35, fstop=8.0, foco=(0.0, 0.0, 1.45))


@shot("11C", 61.46, 65.98, "que a Lua é larga: três mil quatrocentos e setenta quilômetros.", "P", "ortográfica, palco do espaço",
      "O boneco de 3.775 km e a Lua de 3.474 km lado a lado, apoiada no chão do palco; a cabeça passa o topo dela.")
def p11C():
    n = 21; k = 2.0 ** -n
    palco("preto", n, [20, 19, 18], 3774873.0, marcas=[1000000, 2000000, 3000000], rotulo="3.775 km", estrelas=True,
          fmt=lambda m: f"{m / 1000:,.0f}".replace(",", ".") + " km")
    eu()
    r = 1737400.0 * k
    OP.lua("lua", r, (0.58, 2.0, r))
    OB.rotulo_ref(0.36, 2 * r, "Lua: 3.474 km", tam=0.085, y=-0.3, cor=OP.AMBAR)


# ======================================================================== FALA 12
@shot("12A", 65.98, 67.52, "No vigésimo terceiro,", "M", "35 mm, rente", "O pé desce e para logo acima da Terra inteira, uma bola sob a sola.")
def p12A():
    SP.ceu_espaco()
    SP.terra_sob_o_pe(23, folga=0.05)
    eu("passagem", sombra=False)
    # enquadramento: o corpo inteiro no quadro (a câmera antes apontava para baixo e cortava a cabeça)
    cam((1.2, -1.4, 1.0), (0.0, 0.0, 0.9), 35, fstop=5.6, foco=(0.0, -0.1, 0.9))


@shot("12B", 67.52, 70.52, "é a vez da Terra: doze mil setecentos e quarenta e dois", "P", "ortográfica, palco do espaço",
      "A Terra (12.742 km) no palco ao lado do boneco de 15.099 km; a Lua em fantasma ao lado dela.")
def p12B():
    n = 23; k = 2.0 ** -n
    palco("preto", n, [22, 21, 20], 15099494.0, marcas=[5000000, 10000000], rotulo="15.099 km", estrelas=True,
          fmt=lambda m: f"{m / 1000:,.0f}".replace(",", ".") + " km")
    eu()
    r = 6371000.0 * k
    OP.terra("terra", r, (0.62, 2.0, r))
    lua = OP.lua("lua_f", 1737400.0 * k, (0.62 + r + 0.25, 1.5, 1737400.0 * k))
    OB.fantasma_obj([lua])
    OB.rotulo_ref(0.2, 2 * r + 0.02, "Terra: 12.742 km", tam=0.085, y=-0.3, cor=OP.AMBAR)


@shot("12C", 70.52, 72.22, "quilômetros de largura.", "M", "85 mm, close do olho", "A Terra azul refletida no olho branco.")
def p12C():
    SP.ceu_espaco()
    SP.terra_sob_o_pe(23, folga=0.03)
    h = eu(dict(cabeca=4), dict(boca="reta", lid=0.1), sombra=False)
    bpy.context.view_layer.update()
    pe = h.olhos["F"].matrix_world.translation
    OP.terra("refl", 0.022, (pe.x, pe.y - 0.006, pe.z - 0.01))
    SP.cam_v((0.0, 0.0, 1.6), 0.5, 85, az=6, el=-2, fstop=2.8, foco=(pe.x, pe.y, pe.z))


# ======================================================================== FALA 13
K28 = 2.0 ** -28
D_LUA = 384400000.0 * K28


def terra_lua_orbita(lua_t=1.2):
    """a Terra minúscula sob o pé e a órbita da Lua num anel inclinado (60 graus) em volta dele, sem cruzar o corpo; a Lua no anel"""
    rT = 6371000.0 * K28
    OP.terra("terra", rT, (0.0, -0.01, -rT - 0.03))
    piv = empty("orbita_piv", None, (0.0, 0.0, 0.0)); piv.rotation_euler.x = math.radians(60)
    O3.anel("orbita", D_LUA, 0.0025, O3.brilha("#cfd8e8", 1.2), piv, (0, 0, 0), eixo="Z", seg=240, contorno=0.0)
    bpy.context.view_layer.update()
    p = piv.matrix_world @ Vector((D_LUA * math.cos(lua_t), D_LUA * math.sin(lua_t), 0.0))
    OP.lua("lua", 1737400.0 * K28, tuple(p))
    return p


@shot("13A", 72.22, 74.00, "E no vigésimo oitavo,", "M", "24 mm, meia volta", "Ele em pé sobre a Terra, um grão azul sob o tênis; a órbita da Lua é um anel fino em volta dele.")
def p13A():
    SP.ceu_espaco()
    terra_lua_orbita(lua_t=-1.9)
    eu(dict(cabeca=10), sombra=False)
    cam((1.9, -2.1, 1.1), (0.0, 0.0, 0.9), 24, fstop=11.0, foco=(0.0, 0.0, 0.9))


@shot("13B", 74.00, 76.20, "você passa da distância entre a Terra e a Lua,", "P", "ortográfica, palco do espaço",
      "Régua do pé à cabeça (483.184 km); a Terra no chão e a Lua a 384.400 km, na altura do peito; linha âmbar da distância.")
def p13B():
    palco("preto", 28, [27, 26, 25], 483183820.0, marcas=[100000000, 200000000, 300000000, 400000000], rotulo="483.184 km", estrelas=True,
          fmt=lambda m: f"{m / 1000:,.0f}".replace(",", ".") + " km")
    eu()
    rT, rL = 6371000.0 * K28, 1737400.0 * K28
    OP.terra("terra", max(rT, 0.02), (0.45, 0.0, max(rT, 0.02)))
    OP.lua("lua", max(rL, 0.012), (0.45, 0.0, D_LUA))
    OB.caixa("dist", (0.006, 0.006, D_LUA), O3.brilha(OP.AMBAR, 1.4), (0.45, -0.05, D_LUA / 2), cont=0.0)
    OP.texto("t_dist", "384.400 km", 0.055, (0.52, -0.06, D_LUA / 2), cor=OP.AMBAR, forca=1.6, alinha="LEFT")
    OP.texto("t_terra", "Terra", 0.07, (0.5, -0.06, 0.03), cor="#cfd8e8", forca=1.2, alinha="LEFT")
    OP.texto("t_lua", "Lua", 0.07, (0.5, -0.06, D_LUA + 0.04), cor="#cfd8e8", forca=1.2, alinha="LEFT")


@shot("13C", 76.20, 77.96, "que é de quase quatrocentos mil", "M", "50 mm, no peito", "A Lua passa na órbita ao lado do peito dele, do tamanho de um botão da blusa (marcada com um aro); ele a olha de perto.")
def p13C():
    SP.ceu_espaco()
    p = terra_lua_orbita(lua_t=1.19)
    eu(dict(cabeca=14, olha=-30, tronco=3), dict(boca="o"), sombra=False)
    O3.anel("aro_lua", 0.045, 0.0018, O3.brilha("#ffffff", 1.6), None, tuple(p), eixo="Y", seg=48, contorno=0.0)
    cam((1.7, -1.9, 1.35), (0.2, 0.2, 1.2), 40, fstop=5.6, foco=tuple(p))


@shot("13D", 77.96, 80.26, "quilômetros.", "M", "16 mm, rente, rima com o 1A", "O tênis parado no ar logo acima da Terra minúscula, sem pisar; silêncio; fim.")
def p13D():
    SP.ceu_espaco()
    h = eu("passagem", sombra=False)
    bpy.context.view_layer.update()
    f = h.tornozelo["B"].matrix_world.translation
    rT = 6371000.0 * K28
    zmin = min(bpy.data.objects[o.name].matrix_world.translation.z for o in [h.raiz] + list(h.raiz.children_recursive) if o.type == "MESH")
    OP.terra("terra", rT, (f.x, f.y - 0.06, zmin - 0.07 - rT))
    piv = empty("orbita_piv", None, (f.x, f.y - 0.06, zmin - 0.07 - rT)); piv.rotation_euler.x = math.radians(60)
    O3.anel("orbita", D_LUA, 0.0025, O3.brilha("#cfd8e8", 1.2), piv, (0, 0, 0), eixo="Z", seg=240, contorno=0.0)
    # enquadramento: o tênis e o corpo inteiro (antes a cabeça saía pelo alto); a lente um pouco mais aberta para caber
    cam((f.x + 0.9, f.y - 1.2, f.z + 0.8), (f.x, f.y, f.z + 0.85), 24, fstop=5.6, foco=(f.x, f.y - 0.06, f.z + 0.6), clip=0.003)


# ---------------------------------------------------------------- main
def monta(nome, k=0.5, smp=16):
    lib.reset(int(1080 * k), int(1920 * k), 24, smp)
    sc = bpy.context.scene; sc.frame_start, sc.frame_end = 1, 24
    SHOTS[nome]["fn"]()
    sc.frame_set(1)


def main():
    argv = sys.argv[sys.argv.index("--") + 1:]
    if "--list" in argv:
        for k, d in SHOTS.items():
            print(f"{k} | {d['t0']:.2f}-{d['t1']:.2f} | {d['modo']} | {d['lente']} | {d['palavras']}")
        return
    if "--json" in argv:
        json.dump({k: {a: b for a, b in d.items() if a != "fn"} for k, d in SHOTS.items()}, open(argv[argv.index("--json") + 1], "w"), ensure_ascii=False, indent=1)
        return
    nome, out = argv[0], argv[1]
    k = float(argv[argv.index("--scale") + 1]) if "--scale" in argv else 0.5
    smp = int(argv[argv.index("--samples") + 1]) if "--samples" in argv else 16
    monta(nome, k, smp)
    if "--colisao" in argv:
        import colisao_passos
        colisao_passos.confere(nome)
        return
    bpy.context.scene.render.filepath = out
    bpy.ops.render.render(write_still=True)


if __name__ == "__main__":
    main()
