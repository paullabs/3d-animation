"""Replanejamento v14 de "os passos" (aprovado em 26/10/2026; personagem/passos/replanejo-v14.md, provas em provas_passos7.py).
Cinco trechos viram UM plano cada, com a ação na palavra:
  7C  (36,34-38,76)  o tubo do coração à cabeça enche de vermelho em três pulsos; a chave e a caixa "o sangue sobe 16 m";
  8A  (38,76-40,42)  os passos 6 a 9 num plano só (eram 8A, 8B, 8C e 8D): quatro pisadas, quatro crescidas, o Burj de referência;
  9D  (49,64-52,80)  a vista (eram 9D e 9E): por cima do ombro, a linha dos olhos até o horizonte, "horizonte: 150 km";
  10C (55,88-59,10)  a boca e o ar ralo (eram 10C e 10D): de lado perto da boca, a câmera desce e abre; 0,43 e 1,00 atm;
  11B (60,22-65,98)  a Lua AO LADO dele (eram 11B e 11C), as duas chaves e a linha do topo.
O resto do filme vem do v7 (story_passos7). Uso igual: blender -b -P story_passos8.py -- PLANO x.png | --list"""
import os, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy
from mathutils import Vector
import story_passos7 as S7
from story_passos7 import novo
import story_passos3 as S3
import story_passos2 as S2
import story_passos as SP
import provas_passos7 as P7
import objetos3d_passos as OP, objetos3d_passos_b as OB
import objetos3d_abrigo as O3
from heroi3d import tubo

SHOTS = S2.SHOTS
for _k in ("7C", "8A", "8B", "8C", "8D", "9D", "9E", "10C", "10D", "11B", "11C"):
    SHOTS.pop(_k, None)

def tubo_c(nome, pts, raios, mat, **kw):
    """tubo com o centro (origem) no meio dele: quando ele aparece por escala, cresce no lugar (com a origem no zero da cena, voava dos pés dele)"""
    P = [Vector(p) for p in pts]; mid = sum(P, Vector()) / len(P)
    return tubo(nome, [tuple(p - mid) for p in P], raios, mat, None, loc=tuple(mid), **kw)


N_SEG = 30                                                          # o tubo cheio em 30 pedaços, que acendem um a um quando o sangue passa


def caminho_vaso(zc):
    """o caminho do sangue (coração -> pescoço -> cabeça), amostrado em pedaços do mesmo tamanho"""
    pts = [Vector((0.05, -0.03, zc + 0.04)), Vector((0.04, -0.03, zc + 0.2)), Vector((0.0, -0.03, 1.48)), Vector((0.0, -0.03, 1.62))]
    seg = [(pts[i], pts[i + 1]) for i in range(len(pts) - 1)]
    tot = sum((b - a).length for a, b in seg)
    out = []
    for k in range(N_SEG + 1):
        d = tot * k / N_SEG
        for a, b in seg:
            L = (b - a).length
            if d <= L + 1e-9:
                out.append(a.lerp(b, d / L)); break
            d -= L
    return pts, out


@novo("7C", 36.34, 38.76, "de pressão para levar o sangue até a cabeça.", "50 mm, de frente, raio X",
      "O tubo do coração à cabeça enche de vermelho em três pulsos (37,0, 37,4 e 37,8 s); a chave e a caixa 'o sangue sobe 16 m' acendem em 'cabeça'.")
def p7C():
    h, zc = S3.raio_x_rua(5)
    for o in list(bpy.data.objects):
        if o.name.startswith(("vaso", "pulso")):
            bpy.data.objects.remove(o, do_unlink=True)
    pts, amostra = caminho_vaso(zc)
    tubo("vaso_vazio", [tuple(p) for p in pts], [0.03] * len(pts), O3.vidro("#ffd6d6", 0.25, 0.9), None, seg=20, tampa=4, contorno=0.0)
    m = O3.brilha("#e0262c", 1.6)
    for i in range(N_SEG):
        tubo_c(f"sg{i:02d}", [tuple(amostra[i]), tuple(amostra[i + 1])], [0.024, 0.024], m, seg=16, tampa=2, contorno=0.0)
    O3.cilindro("seta", 0.035, 0.06, O3.brilha("#ffe08a", 1.8), None, tuple(amostra[0] + Vector((0, -0.03, 0.045))), seg=20, eixo="Z", r2=0.0, contorno=0.0)
    P7.chave_v("chave16", -0.32, -0.05, zc, S2.H, 0.012)
    cam = (0.05, -2.7, 1.42)
    P7.pilula_cam("p16", "o sangue sobe 16 m", (0.05, -0.1, 1.98), 0.07, cam)
    P7.pilula_cam("pcor", "coração", (0.28, -0.45, zc - 0.1), 0.055, cam)
    S2.cam(cam, (0.05, 0.0, 1.42), 50, fstop=8.0, foco=(0.0, -0.05, 1.42))


@novo("8A", 38.76, 40.42, "No nono, você passa o", "28 mm, três quartos, a câmera recua",
      "Um plano só: quatro pisadas (38,94 / 39,36 / 39,78 / 40,20 s) e quatro crescidas, 115 > 230 > 461 > 922 m; o Burj atrás, que ele passa no último passo.")
def p8A():
    k = 2.0 ** -9
    SP.ceu_dia()
    def b():                                                           # a cidade do 8E, com a clareira maior: no 9º passo a passada dele tem quase 1 u
        OP.chao("#8f9a8a", None, 40000.0, nome="chao_largo")
        OP.cidade_maquete(4200.0, passo=95.0, altura_max=130.0, clareira=[(0, 0, 0.75 / k), (0.75 / k, 1.6 / k, 300.0)], seed=4)
        OB.burj("burj", 0.75 / k, 1.6 / k)
    SP.no_mundo(9, b, cont_u=0.0012)
    S2.eu("passagem", rosto=dict(boca="o"))
    S2.cam((-0.6, -0.67, 0.18), (0.12, 0.18, 0.15), 28, fstop=11.0, foco=(0.0, 0.0, 0.1))


@novo("9D", 49.64, 52.80, "e a vista chega a cento e cinquenta quilômetros.", "24 mm, por cima do ombro",
      "Ele levanta os olhos para o horizonte; a linha tracejada sai dos olhos e vai até onde a Terra some; 'horizonte: 150 km' acende no céu.")
def p9D():
    P7.terra_curva()
    S2.eu(dict(cabeca=-2))
    olho = Vector((0.0, -0.3, 1.66))                                  # a linha nasce na frente dos olhos (dentro da cabeça era colisão)
    T = P7.chao(146.3)
    n = 40
    for k in range(0, n, 2):
        a, b = olho.lerp(T, k / n), olho.lerp(T, (k + 1) / n)
        tubo_c(f"visao{k:02d}", [tuple(a), tuple(b)], [0.006 + 0.03 * k / n] * 2, O3.brilha(P7.AMARELO, 1.8), seg=8, tampa=2, contorno=0.0)
    cam = (0.35, 0.9, 2.05)
    from heroi3d import esfera
    esfera("horizonte_ponto", 1.6, 1.6, 0.5, O3.brilha(P7.AMARELO, 1.8), None, tuple(T), contorno=0.0, seg=24, an=8)
    alto = Vector((T.x, T.y, T.z + 22.0))
    tubo_c("fio_pilula", [tuple(T), tuple(alto)], [0.25, 0.25], O3.brilha(P7.AMARELO, 1.6), seg=8, tampa=2, contorno=0.0)
    P7.pilula_cam("km150", "horizonte: 150 km", (alto.x, alto.y, alto.z + 5.0), 7.0, cam)
    S2.cam(cam, (0.0, -146.0, 0.0), 24, fstop=16.0, foco=(0.0, 0.0, 1.6))


@novo("10C", 55.88, 59.10, "Na altura da boca, o ar tem menos da metade da pressão do chão.", "40 mm, de lado: da boca ao chão",
      "De lado, perto da boca (o ar ralo na frente dela, os braços soltos); a câmera desce e abre até o chão; 'boca: 0,43 atm' e 'chão: 1,00 atm'.")
def p10C():
    P7.ar_ralo()
    S2.cam((-1.7, -0.32, 1.52), (0.0, -0.32, 1.52), 40, fstop=5.6, foco=(0.0, -0.3, 1.5))


@novo("11B", 60.22, 65.98, "você já é mais alto que a Lua é larga: três mil quatrocentos e setenta quilômetros.", "85 mm, de frente, no espaço",
      "A Lua chega pela direita e para AO LADO dele; a chave dele (3.775 km) e a chave da largura dela (3.474 km); a linha do topo da cabeça passa por cima da Lua.")
def p11B():
    P7.PROVAS["L"][1]()


def main():
    S2.main()


if __name__ == "__main__":
    main()
