"""Replanejamento v15 de "os passos" (aprovado em 26/10/2026; personagem/passos/replanejo-v15.md, provas em provas_passos8.py).
Sobre o v14 (story_passos8), seis trechos viram UM plano cada:
  8E  (40,42-43,90)  ele (922 m) e o Burj (828 m) lado a lado, de frente, lente de 300 mm; a câmera chega ao topo da agulha (eram 8E e 8F);
  9A  (43,90-46,96)  a mesma vista: ele pisa em "décimo" e dobra; o Burj bate no quadril (eram 9A e 9B);
  9C  (46,96-49,64)  o homem de 1,8 m no telhado com a lata; o fio do cabelo desce do céu ao lado dela;
  10A (52,80-55,88)  de lado, nas nuvens: pisa em "doze"; o avião passa acima da cabeça (eram 10A e 10B);
  13A (72,22-74,00)  o tênis desce e para em cima da Terra, menor que o tênis;
  13B (74,00-77,96)  de lado: a Terra e a Lua; a linha da distância desenha e gira até ficar de pé ao lado dele (eram 13B e 13C).
Fica como está: 9D, 10C, 11A, 11B, 12A, 12B, 12C, 13D e o resto. Mesmo uso: blender -b -P story_passos9.py -- PLANO x.png | --list"""
import os, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy
from mathutils import Vector
import story_passos8 as S8
from story_passos7 import novo
import story_passos2 as S2
import story_passos as SP
import provas_passos7 as P7
import provas_passos8 as P8
import objetos3d_passos as OP, objetos3d_passos_b as OB
import objetos3d_abrigo as O3
import elenco3d_abrigo as E3
import poses_passos as PP
from heroi3d import tubo

SHOTS = S2.SHOTS
for _k in ("8E", "8F", "9A", "9B", "9C", "10A", "10B", "13A", "13B", "13C"):
    SHOTS.pop(_k, None)

AM = P7.AMARELO


@novo("8E", 40.42, 43.90, "Burj Khalifa, que tem oitocentos e vinte e oito metros.", "300 mm, de frente, o Burj ao lado",
      "Ele (922 m) e o Burj (828 m) lado a lado; as caixas acendem em 'Burj' e 'oitocentos'; a câmera chega ao topo da agulha, que fica abaixo do queixo dele.")
def p8E():
    k, zb = P8.ele_e_burj()
    P8.cam_par(9, 2.5, 1.0, sep_deg=24.0)
    yb = P8.BURJ_M[1] * k
    c = bpy.context.scene.camera
    cl = tuple(c.location)
    P7.pilula_cam("p_burj", "Burj Khalifa: 828 m", (0.75, yb, zb + 0.13), 0.07, cl)
    P7.pilula_cam("p_ele", "ele: 922 m", (0.0, -0.05, 1.8 + 0.13), 0.07, cl)
    for j in range(8):                                                  # a linha tracejada na altura da ponta do Burj, da agulha até ele
        p = Vector((0.75, yb, zb)).lerp(Vector((0.0, 0.0, zb)), (j + 0.5) / 8)
        if j % 2 == 0:
            OB.caixa(f"nivel{j}", (0.025, 0.025, 0.006), O3.brilha("#ffffff", 1.6), tuple(p), cont=0.0)
    P7.pilula_cam("p_burj_topo", "828 m", (0.75, yb, zb + 0.07), 0.04, cl)
    P7.pilula_cam("p_ele_topo", "922 m", (0.0, -0.05, 1.86), 0.04, cl)


@novo("9A", 43.90, 46.96, "No décimo, são quase dois quilômetros:", "300 mm, de frente, a mesma vista",
      "Ele pisa em 'décimo' e dobra (de 922 m a 1,8 km); o Burj, quase da altura dele, passa a bater no quadril; a caixa 'ele: 1,8 km'.")
def p9A():
    n = 10
    k = P8.cidade(n, 0.85 / 2 ** -10)
    S2.eu("subida", rosto=dict(boca="o"))
    P8.cam_par(n, 2.5, 1.0, sep_deg=30.0)
    cl = tuple(bpy.context.scene.camera.location)
    yb = P8.BURJ_M[1] * k
    P7.pilula_cam("p_burj", "Burj: 828 m", (P8.BURJ_M[0] * k, yb, 828.0 * k + 0.12), 0.07, cl)
    P7.pilula_cam("p_ele", "ele: 1,8 km", (0.0, -0.05, 1.8 + 0.13), 0.075, cl)


@novo("9C", 46.96, 49.64, "o cabelo tem a grossura de uma lata de refrigerante", "50 mm, de frente, no telhado",
      "No telhado, o homem de 1,8 m segura a lata ao lado do fio de cabelo que desce do céu; 'cabelo dele: 7,7 cm' e 'lata: 6,6 cm'.")
def p9C():
    P8.PROVAS["C"][1]()


@novo("10A", 52.80, 55.88, "Com doze passos, são sete quilômetros.", "135 mm, de lado, nas nuvens",
      "Ele pisa em 'doze'; as nuvens ficam no joelho; em 'sete quilômetros' o avião passa acima da cabeça (10 km) e a caixa 'ele: 7,4 km' acende.")
def p10A():
    P8.PROVAS["N"][1]()


@novo("13A", 72.22, 74.00, "E no vigésimo oitavo,", "50 mm, de perto, rente à Terra",
      "O tênis desce e para em cima da Terra, que é menor que o tênis; a caixa 'a Terra'.")
def p13A():
    P8.PROVAS["T"][1]()


@novo("13B", 74.00, 77.96, "você passa da distância entre a Terra e a Lua, que é de quase quatrocentos mil quilômetros.", "135 mm, de lado, no espaço",
      "A Terra e a Lua marcadas; a linha amarela desenha entre as duas e gira até ficar de pé ao lado dele: a cabeça passa a ponta.")
def p13B():
    P8.terra_lua_lado(0)
    # a linha de pé (a de 13B fase 1) já está na cena abaixo, escondida até o giro
    zc = -P8.R28 - 0.03
    y = 0.38
    P8.tubo("dist_pe", [(-0.05, y, zc), (-0.05, y, zc + P8.DL28)], [0.006, 0.006], O3.brilha(AM, 1.6), None, seg=10, tampa=2, contorno=0.0)
    cl = tuple(bpy.context.scene.camera.location)
    P7.pilula_cam("p_d_pe", "384.400 km", (-0.05, y + 0.2, zc + P8.DL28), 0.05, cl)
    P7.pilula_cam("p_ele", "ele: 483.184 km", (-0.05, -0.12, 1.94), 0.055, cl)


def main():
    S2.main()


if __name__ == "__main__":
    main()
