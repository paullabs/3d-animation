"""Provas da abertura v4 de "os passos" (crítica de 25/10/2026 ao v3: "em 5 segundos deu 3 cortes da mesma cena; a primeira cena tem que ser
mais vazia: a pessoa andando de frente, dá um passo e cresce, com outra pessoa do lado para comparar; idealizar a cena antes").
Um plano longo por ideia: os dois andam de frente para a câmera, lado a lado, do mesmo tamanho; no passo, só ele dobra.
blender -b -P provas_passos4.py -- PROVA SAIDA.png [--scale 0.5]   |   --list"""
import os, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy, lib
from mathutils import Vector
import story_passos2 as S2
import objetos3d_passos as OP, objetos3d_passos_b as OB
import objetos3d_abrigo as O3
import elenco3d_abrigo as E3
import poses_passos as PP
import story_passos3                                     # (as poses "susto" e "olha_mao")

PROVAS = {}
X_EU, X_AM = 0.42, -0.42            # lado a lado (u, no passo 0): ele à direita, o amigo à esquerda


def prova(nome, titulo):
    def d(fn):
        PROVAS[nome] = (titulo, fn); return fn
    return d


def rua_vazia(n, extras=()):
    """a rua sem carro, sem ponto e sem a moça: só o asfalto, a calçada, os postes e as árvores (escala) e o céu"""
    E = S2.rua2(n, moca=False, ponto=False, extras=extras, corredor_u=14.0, livre_u=4.0)
    for o in list(bpy.data.objects):
        if o.name.startswith("carro"):
            bpy.data.objects.remove(o, do_unlink=True)
    return E


def amigo(n, x_u, pose="contato", rosto=None, rot=0.0, cabeca=None, olha=None):
    """o amigo, do mesmo tamanho que ele no começo (1,8 m): no passo n ele fica com 1,8 x 2^-n na cena"""
    k = 2.0 ** -n
    h = E3.faz("viz2", "amigo"); h.raiz.scale = (S2.EU_ESC * k,) * 3
    P = dict(PP.POSES[pose]) if isinstance(pose, str) else dict(pose)
    for kk in ("rot_x", "maos_no_chao", "boca", "mao_no_joelho", "maos_na_boca", "mao_no_peito", "alvo_mao"):
        P.pop(kk, None)
    if cabeca is not None:
        P["cabeca"] = cabeca
    if olha is not None:
        P["olha"] = olha
    h.pose(**h.pe_no_chao(**P)); PP.assenta(h, 0.0)
    h.raiz.location.x = x_u; h.raiz.rotation_euler.z = math.radians(rot)
    h.rosto(**(rosto or dict(boca="reta", lid=0.0)))
    return h


def linha(nome, z, x0, x1, rotulo, lado=1):
    """a linha âmbar na altura da cabeça, de um boneco ao outro, com o número na ponta"""
    OB.caixa(nome, (abs(x1 - x0), 0.012, 0.014), O3.brilha(OB.AMBAR_ESC, 1.2), ((x0 + x1) / 2, 0.0, z), cont=0.0)   # no plano das cabeças: a altura é a de verdade
    xr = x1 + 0.04 if lado > 0 else x0 - 0.04
    OP.texto(nome + "_t", rotulo, 0.13 if z > 1.0 else 0.11, (xr, 0.0, z - 0.045), cor=OB.AMBAR_ESC, forca=1.2, alinha="LEFT" if lado > 0 else "RIGHT")


@prova("P1", "0,4 s · \"E se cada passo...\": os dois andam de frente, lado a lado, do mesmo tamanho (travelling para trás, 35 mm)")
def p1():
    rua_vazia(0)
    S2.eu("contato", loc=(X_EU, 0, 0))
    amigo(0, X_AM, "subida", olha=-6)
    S2.cam((0.0, -3.4, 0.95), (0.0, 0.0, 0.98), 35, fstop=8.0, foco=(0.0, 0.0, 1.0))


@prova("P2", "5,2 s · \"...com um metro e oitenta\": a linha âmbar passa pelas duas cabeças")
def p2():
    rua_vazia(0)
    S2.eu("passagem", loc=(X_EU, 0, 0))
    amigo(0, X_AM, "passagem", olha=8)
    linha("l18", 1.8, X_AM - 0.25, X_EU + 0.25, "1,8 m")
    S2.cam((0.0, -3.4, 0.95), (0.0, 0.0, 0.98), 35, fstop=8.0, foco=(0.0, 0.0, 1.0))


@prova("P3", "6,3 s · \"Depois do primeiro passo\": ele levanta o pé (antecipação); o amigo segue andando")
def p3():
    rua_vazia(0)
    S2.eu("subida", loc=(X_EU, 0, 0))
    amigo(0, X_AM, "contato", olha=8)
    S2.cam((0.0, -3.4, 0.95), (0.0, 0.0, 0.98), 35, fstop=8.0, foco=(0.0, 0.0, 1.0))


@prova("P4", "6,6 s · \"passo,\": o pé pousa e só ele dobra (3,6 m), com poeira; o amigo para e olha para cima. A câmera recua e sobe")
def p4():
    rua_vazia(1)
    h = S2.eu("contato", loc=(X_EU * 0.5, 0, 0), rosto=dict(boca="o"))
    f = S2.pe_de(h, "F"); OP.poeira_pouso(f.x, f.y - 0.05, r=0.35)
    amigo(1, X_AM * 0.5 - 0.12, "olha_baixo", cabeca=-30, olha=-30, rosto=dict(boca="o", lid=0.0))
    linha("l18", 0.9, -0.62, -0.42, "1,8 m", lado=-1)
    linha("l36", 1.8, 0.36, 0.62, "3,6 m")
    S2.cam((0.0, -2.45, 0.6), (0.0, 0.0, 1.0), 28, fstop=8.0, foco=(0.0, 0.0, 1.0))


@prova("P5", "7,7 s · \"metros e meio\": a reação, de perto (50 mm): ele olha para as mãos e para baixo, \"caramba, cresci\"")
def p5():
    rua_vazia(1)
    S2.eu("olha_mao", loc=(X_EU * 0.5, 0, 0), rosto=dict(boca="o"))
    amigo(1, X_AM * 0.5 - 0.12, "olha_baixo", cabeca=-30, olha=-30, rosto=dict(boca="o"))
    S2.cam((0.55, -2.3, 1.2), (0.15, 0.0, 1.45), 50, fstop=4.0, foco=(0.2, 0.0, 1.5))


@prova("P6", "10,4 s · \"No segundo passo, são sete metros\": o segundo pouso; ele passa o poste (7 m); o amigo, na altura da canela")
def p6():
    rua_vazia(2, extras=("poste",))
    h = S2.eu("contato", rosto=dict(boca="reta"))
    f = S2.pe_de(h, "F"); OP.poeira_pouso(f.x, f.y - 0.05, r=0.22)
    amigo(2, -0.55, "olha_baixo", cabeca=-34, olha=-34, rosto=dict(boca="o"))
    linha("l18", 0.45, -0.78, -0.62, "1,8 m", lado=-1)
    linha("l72", 1.8, 0.16, 0.45, "7,2 m")
    S2.cam((-0.4, -1.75, 0.3), (0.25, 0.2, 1.05), 20, fstop=8.0, foco=(0.0, 0.0, 1.0))


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
