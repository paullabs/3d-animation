"""Abertura v4 de "os passos" (aprovada em 25/10/2026; plano em personagem/passos/abertura-v4.md, provas em provas_passos4.py).
As falas 1 a 3 (0 a 11,48 s) viram 3 planos no lugar dos 11 do v3:
  1A (0,00-7,69 s)  os dois andam de frente (ele e o amigo, do mesmo tamanho); em "dobrasse" (2,08 s) o pé pousa e só ele dobra, dentro do plano (v5: antes era aos 6,5 s e demorava);
  1B (7,69-8,80 s)  a reação de perto ("caramba, eu cresci"), a cabeça do amigo embaixo;
  1C (8,80-11,48 s) o segundo passo: 7,2 m, o poste e o amigo na altura da canela.
Da fala 4 em diante continua o v3 (story_passos3). Mesmo uso do story_passos3: blender -b -P story_passos4.py -- PLANO x.png | --list"""
import os, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy
from mathutils import Vector
import story_passos3 as S3                                 # o v3 inteiro (as poses "susto" e "olha_mao" e os planos da fala 4 em diante)
import story_passos2 as S2
import objetos3d_passos as OP, objetos3d_passos_b as OB
import objetos3d_abrigo as O3
import elenco3d_abrigo as E3
import poses_passos as PP
import cena

SHOTS = S2.SHOTS
X_EU, X_AM = -0.12, -0.5           # na cena do passo 1 (u): ele à direita, o amigo à esquerda (1 m entre os dois)
Y0 = 0.9                           # onde os dois estão no primeiro quadro (u, atrás do ponto do pouso): o primeiro pouso é em 2,08 s
AM_FIM = (-0.36, 0.12)              # onde o amigo para depois do susto (deu um passinho para trás e para o lado)

for _k in [k for k, d in SHOTS.items() if d["t0"] < 11.47]:
    del SHOTS[_k]


def novo(nome, t0, t1, palavras, lente, nota):
    def deco(fn):
        SHOTS[nome] = dict(t0=t0, t1=t1, palavras=palavras, modo="M", lente=lente, nota=nota, fn=fn)
        _ordena()
        return fn
    return deco


def _ordena():
    it = sorted(SHOTS.items(), key=lambda kv: kv[1]["t0"])
    SHOTS.clear(); SHOTS.update(it)


def rua_vazia(n, extras=()):
    """a rua sem carro, sem ponto e sem a moça: o asfalto, a calçada, os postes, as árvores e o céu"""
    E = S2.rua2(n, moca=False, ponto=False, extras=extras, corredor_u=14.0, livre_u=4.0)
    for o in list(bpy.data.objects):
        if o.name.startswith("carro") or o.name.endswith("_toldo"):         # o toldo vermelho encostava no ombro e parecia um braço solto
            bpy.data.objects.remove(o, do_unlink=True)
    return E


def amigo(n, x_u, y_u=0.0, pose="contato", rosto=None, cabeca=None, olha=None):
    """o amigo (blusa cinza-azulada), que fica sempre com 1,8 m: no passo n ele mede 1,8 x 2^-n na cena"""
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
    h.raiz.location.x = x_u; h.raiz.location.y = y_u
    h.rosto(**(rosto or dict(boca="reta", lid=0.0)))
    e = S2.EU_ESC * k                                                  # a sombra no chão (anda com ele: anima() move H.sombra)
    cena.ground_disc("amigo_sb", 0.42 * e, 0.28 * e, cena.amat("amigo_sb_m", "#000000", 1.0, 0.32, ("radial", 1.1)), (x_u, y_u + 0.05 * k, 0.004), n=32)
    return h


def linha(nome, z, x0, x1, rotulo, lado=1, y=0.0, tam=None):
    """a linha âmbar na altura de uma cabeça, no plano do boneco (a altura no quadro é a de verdade), com o número na ponta de fora"""
    OB.caixa(nome, (abs(x1 - x0), 0.012, 0.014), O3.brilha(OP.AMBAR, 1.5), ((x0 + x1) / 2, y, z), cont=0.0)
    t = tam or (0.13 if z > 1.0 else 0.1)
    if lado == 0:                                                      # o número centrado em cima da linha
        OP.texto(nome + "_t", rotulo, t, ((x0 + x1) / 2, y, z + 0.025), cor=OP.AMBAR, forca=1.8, alinha="CENTER")
        return
    xr = x1 + 0.04 if lado > 0 else x0 - 0.04
    OP.texto(nome + "_t", rotulo, t, (xr, y, z - 0.045), cor=OP.AMBAR, forca=1.8, alinha="LEFT" if lado > 0 else "RIGHT")


@novo("1A", 0.00, 7.69, "E se cada passo que você desse dobrasse a sua altura? Você começa com um metro e oitenta. Depois do primeiro passo, são três",
      "35 mm, de frente, travelling para trás",
      "Os dois andam de frente, do mesmo tamanho; a linha de 1,8 m passa pelas duas cabeças; no 'passo' o pé pousa e só ele dobra (3,6 m); o amigo se assusta e olha para cima.")
def p1A():
    rua_vazia(1)
    h = S2.eu("passagem", loc=(X_EU, Y0, 0), sombra=True)
    amigo(1, X_AM, Y0, "passagem")
    linha("m18", 0.9, AM_FIM[0] - 0.24, AM_FIM[0] - 0.12, "1,8 m", lado=-1, y=AM_FIM[1], tam=0.085)   # "um metro e oitenta": o amigo, que não cresceu
    linha("l36", 1.8, X_EU - 0.42, X_EU - 0.17, "3,6 m", lado=-1)                                   # "são três metros e meio": ele
    OP.poeira_pouso(X_EU + 0.02, -0.12, r=0.3)
    S2.cam((0.0, Y0 - 1.7, 0.47), (-0.02, Y0, 0.49), 35, fstop=8.0, foco=(0.0, Y0, 0.5))


@novo("1B", 7.69, 8.80, "metros e meio.", "50 mm, de perto, um pouco de baixo",
      "A reação: ele olha as mãos, olhos arregalados ('caramba, eu cresci'); a cabeça do amigo, olhando para cima, no canto de baixo.")
def p1B():
    rua_vazia(1)
    S2.eu("olha_mao", loc=(X_EU, 0, 0), rosto=dict(boca="o"))
    amigo(1, AM_FIM[0], AM_FIM[1], "olha_baixo", cabeca=-30, olha=-24, rosto=dict(boca="o"))
    S2.cam((0.55, -2.3, 1.2), (0.17, 0.0, 1.45), 50, fstop=4.0, foco=(0.22, 0.0, 1.5))


@novo("1C", 8.80, 11.48, "No segundo passo, são sete metros.", "20 mm, baixa, à esquerda",
      "O segundo passo: o pé pousa no 'passo' e ele vai a 7,2 m, passa o poste (7 m); o amigo, lá atrás, na altura da canela; as duas linhas.")
def p1C():
    rua_vazia(2, extras=("poste",))
    S2.eu("olha_baixo", loc=(0.06, 0.0, 0), rosto=dict(boca="o"))
    amigo(2, -0.34, 0.3, "olha_baixo", cabeca=-34, olha=-20, rosto=dict(boca="o"))
    linha("l72", 1.8, 0.2, 0.46, "7,2 m")
    linha("m18", 0.45, -0.5, -0.39, "1,8 m", lado=0, y=0.3, tam=0.06)
    OP.poeira_pouso(0.08, -0.1, r=0.25)
    S2.cam((-0.32, -1.25, 0.25), (0.14, 0.2, 0.92), 20, fstop=8.0, foco=(0.06, 0.1, 0.9))


def main():
    S2.main()


if __name__ == "__main__":
    main()
