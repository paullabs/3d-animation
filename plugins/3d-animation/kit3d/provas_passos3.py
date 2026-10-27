"""Provas do plano de cena v3 de "os passos" (pedido de 25/10/2026: "a primeira cena não dá para entender, ele já começa grande;
ele tem que dar um passo e crescer dentro da cidade; a tela branca quebra a imersão; ter a visão de baixo para cima e a de olhar para o
próprio pé e ver a cidade inteira"). Tudo dentro do mundo: nada de palco branco.
blender -b -P provas_passos3.py -- PROVA SAIDA.png [--scale 0.5]"""
import os, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy, lib
from mathutils import Vector
import story_passos2 as S2
import story_passos as SP
import objetos3d_passos as OP, objetos3d_passos_b as OB
import objetos3d_abrigo as O3
import poses_passos as PP
import cena

PROVAS = {}


def prova(nome, titulo):
    def d(fn):
        PROVAS[nome] = (titulo, fn); return fn
    return d


def pov(alvo_pe=(0.0, -1.0, 0.0), lente=16, recuo=0.3, z_olho=1.62):
    """a câmera nos olhos dele, olhando para o próprio pé: vê o peito, as pernas, o tênis e a cidade inteira lá embaixo"""
    for o in bpy.data.objects:                                     # a cabeça dele some (a câmera está dentro dos olhos)
        if o.name.startswith("eu_") and any(k in o.name for k in ("cranio", "olho", "palpebra", "sobr", "boca", "cabelo", "cab", "gola", "pesc", "rosto")):
            o.hide_render = True
    S2.cam((0.0, -recuo, z_olho), alvo_pe, lente, fstop=11.0, foco=alvo_pe, clip=0.01)


def regua_mundo(n, x=-0.55, y=0.0, lado=1):
    """a régua dentro da rua: uma fita métrica de pé no asfalto, afastada do corpo, com o número âmbar ao lado do topo"""
    OB.regua2(x, 1.8, S2.altura(n), lado=lado, y=y, cor_num=OB.AMBAR_ESC)


# 1A: tamanho normal, no ponto de ônibus, dá o passo... (antes e depois)
@prova("1A_antes", "1A · 0,0 s: ele no ponto, tamanho normal (1,8 m), começa o passo")
def p1a0():
    S2.rua2(0, onibus_y=30.0)
    S2.eu("subida", rot=0)
    S2.cam((0.55, -2.2, 0.55), (-0.2, 0.0, 1.0), 24, fstop=5.6, foco=(0.0, 0.0, 1.0))


@prova("1A_depois", "1A · 1,0 s: o pé pousa e ele cresce ali mesmo: 3,6 m (a moça olha para cima)")
def p1a1():
    S2.rua2(1, onibus_y=60.0)
    S2.eu("contato", rot=0)
    S2.cam((0.28, -1.1, 0.28), (-0.1, 0.0, 0.95), 24, fstop=5.6, foco=(0.0, 0.0, 1.0))


@prova("1B", "1B · de baixo para cima: a câmera no asfalto, ao lado do pé que pousa; ele passa o poste (7,2 m)")
def p1b():
    S2.rua2(2, extras=("poste",), aberto=1)
    h = S2.eu("contato")
    f = S2.pe_de(h, "F")
    OP.poeira_pouso(f.x, f.y - 0.05, r=0.35)
    S2.cam((f.x + 0.22, f.y - 0.32, 0.02), (f.x - 0.05, f.y + 0.25, 1.4), 14, fstop=4.0, foco=(f.x, f.y, 0.1), clip=0.002)


@prova("1C", "1C · os olhos dele olhando para o próprio pé: 57 m, a rua e os prédios lá embaixo")
def p1c():
    S2.rua2(5, extras=("p18", "p10"))
    S2.eu("olha_baixo")
    pov(alvo_pe=(0.0, -1.15, 0.0), lente=12)


@prova("4B", "medida dentro da cidade: lente longa de longe, a régua de pé na rua e o prédio de 5 andares ao lado")
def p4b():
    S2.rua2(3, extras=("p5",), corredor_u=12.0)
    S2.eu(dict(cabeca=2))
    regua_mundo(3, x=-0.5, y=0.1)
    S2.cam((0.25, -10.0, 1.05), (0.25, 0.0, 0.98), 135, fstop=11.0, foco=(0.0, 0.0, 1.0))


@prova("8E", "Burj Khalifa ao lado dele, dentro da cidade (comparação), de longe com lente longa")
def p8e():
    n = 9; k = 2.0 ** -n
    SP.ceu_dia()
    def b():
        OP.chao("#8f9a8a", None, 40000.0, nome="chao_largo")
        OP.cidade_maquete(4200.0, passo=95.0, altura_max=130.0, clareira=[(0, 0, 1.6 / k), (0.75 / k, 1.6 / k, 300.0)], seed=4)
        OB.burj("burj", 0.75 / k, 1.6 / k)
    SP.no_mundo(n, b, cont_u=0.0012)
    S2.eu(dict(cabeca=0, olha=24))
    regua_mundo(9, x=-0.55, y=0.1)
    OB.caixa("linha_burj", (0.55, 0.01, 0.008), O3.brilha(OB.AMBAR_ESC, 1.0), (0.45, 0.4, 828.0 * k), cont=0.0)
    OB.rotulo_ref(0.45, 828.0 * k + 0.05, "Burj Khalifa: 828 m", tam=0.07, y=0.38, cor=OB.AMBAR_ESC)
    S2.cam((0.3, -10.5, 0.95), (0.3, 0.0, 0.95), 135, fstop=16.0, foco=(0.0, 0.0, 1.0))


@prova("9", "os olhos dele no 10º passo (1,8 km): a cidade inteira cabe em volta do tênis")
def p9():
    SP.mundo_cidade(10, raio_u=30.0, clareira=None)
    S2.eu("olha_baixo")
    pov(alvo_pe=(0.0, -1.2, 0.0), lente=12)


@prova("10", "os olhos dele com 7 km: as nuvens passam na altura do joelho")
def p10():
    SP.mundo_ar(12, nuvens_z=(1500.0, 2900.0), raio_u=10.0, n_nuv=70)
    S2.eu("olha_baixo")
    pov(alvo_pe=(0.0, -1.2, 0.0), lente=12)


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
