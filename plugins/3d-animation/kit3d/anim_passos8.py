"""Animação do replanejamento v14 (aprovado em 26/10/2026). Planos em story_passos8.py; o resto do filme vem do v7 (anim_passos7).
  7C  o sangue enche o tubo em três pulsos do coração, a seta vai na frente; a chave e a caixa acendem em "cabeça";
  8A  quatro pisadas na palavra (uma a cada 0,42 s), quatro crescidas em curva; a caixa troca o número; a câmera recua mais devagar que ele cresce;
  9D  ele levanta os olhos; a linha tracejada corre dos olhos ao horizonte em "cento e cinquenta"; a caixa acende em "quilômetros";
  10C a câmera começa na boca e desce até o chão; as caixas acendem em "pressão" e "chão";
  11B a Lua entra pela direita e para ao lado dele; a chave dele em "mais alto", a dela em "Lua é larga", a linha do topo em "larga".
blender -b -P anim_passos8.py -- PLANO PASTA [--scale 0.5] [--samples 10] [--quadros 1,M,N] [--colisao] [--mede] [--espaco] [--sync]"""
import os, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy
from mathutils import Vector
import story_passos8 as S8                                  # troca os cinco trechos (e traz o v7)
import anim_passos7 as A7                                   # as animações do v7 (e liga a profundidade)
import anim_passos4 as A4
import anim_passos as AP
import lib
from anim_passos import A, key, lerp, suave, faixa, fq, estado, anima_estados, vivo, escala_h, aparece, poeira_anim, soco_suave, cada, camera_caminho, FPS
from anim_passos3 import susto
from anim_passos4 import mostra, objs, camera_olhando
import profundidade as PF

ANIM = AP.ANIM
PF.ABERTURA.update({"9D": 16.0, "11B": 11.0, "8A": 11.0})                # a vista: o horizonte e a caixa no céu têm de ficar nítidos
PF.ENEVOA_POR.update({"9D": 0.08, "8A": 0.12})              # a névoa usa a distância de foco do 1º quadro: no 8A ela é curta e lavava tudo                          # (a névoa forte apagava a caixa a 150 km)


def r(nome):
    def deco(fn):
        ANIM[nome] = fn
        return fn
    return deco


def pose_parado(H, **troca):
    P = dict(getattr(H, "_ultima", {})); P.update(troca)
    P["pos"] = tuple(H.raiz.location); P["rot"] = tuple(math.degrees(v) for v in H.raiz.rotation_euler)
    return P


def z_com_escala(H, curva):
    """a altura do corpo (z da raiz) foi calculada para o tamanho cheio: com o boneco menor, os pés ficariam no ar; z acompanha a escala"""
    for fc in lib._fcs(H.raiz):
        if fc.data_path == "location" and fc.array_index == 2:
            for kp in fc.keyframe_points:
                kp.co.y *= curva(int(round(kp.co.x)))
                kp.handle_left.y = kp.handle_right.y = kp.co.y
            fc.update()


# ======================================================================== 7C: o sangue sobe
@r("7C")
def a7C(N):
    H = A.REG["eu"]; vivo(H, N, vida=0.3)
    q = lambda t: fq("7C", t)
    batidas = [q(37.0), q(37.4), q(37.8)]
    frac = lambda f: sum(suave(faixa(f, b - 1, b + 5)) for b in batidas) / 3.0
    segs = sorted(cada("sg"), key=lambda o: o.name)
    for i, o in enumerate(segs):                                       # cada pedaço acende quando o sangue chega nele
        f_on = next((f for f in range(1, N + 1) if frac(f) >= (i + 1) / len(segs) - 1e-6), N)
        aparece([o], f_on, f_on + 1, N=N)
    _, amostra = S8.caminho_vaso(0.72 * S8.S2.H)
    seta = bpy.data.objects.get("seta")
    if seta is not None:                                                # a seta vai na frente do sangue e some quando ele chega
        b0 = Vector(seta.scale)
        for f in range(1, N + 1):
            u = frac(f) * (len(amostra) - 1); i = min(len(amostra) - 2, int(u)); p = amostra[i].lerp(amostra[i + 1], u - i)
            seta.location = p + Vector((0.0, -0.03, 0.045)); key(seta, "location", f, "LINEAR")
            s = 1.0 - suave(faixa(f, q(37.86), q(37.86) + 4))
            seta.scale = b0 * max(s, 1e-4); key(seta, "scale", f, "LINEAR")
    for o in cada("cor"):                                               # o coração bate junto com os pulsos
        b = Vector(o.scale)
        for f in range(1, N + 1):
            s = 1.0 + sum(0.25 * math.exp(-((f - bt) / 1.6) ** 2) for bt in batidas)
            o.scale = b * s; key(o, "scale", f, "LINEAR")
    mostra(objs("pcor_pil", "pcor_txt"), 1, 6, N=N)
    mostra(objs("chave16", "chave16_p0", "chave16_p1", "p16_pil", "p16_txt"), q(37.86), q(37.86) + 5, N=N)
    A.camera_viva(N, frente=0.03, mao=0.2)


# ======================================================================== 8A: quatro pisadas num plano só
PISADAS = [38.94, 39.36, 39.78, 40.20]
ROTULOS = ["57,6 m", "115 m", "230 m", "461 m", "922 m"]


@r("8A")
def a8A(N):
    H = A.REG["eu"]; q = lambda t: fq("8A", t)
    fs = [q(t) for t in PISADAS]
    for f in fs:
        AP.POUSOS.append(f)
    s0 = 1.0 / 16.0
    escala = lambda f: s0 * 2.0 ** sum(suave(faixa(f, fl, fl + 6)) for fl in fs)
    # as pernas: a cada pisada uma perna sobe (alta) e pisa (contato); a seguinte é a outra perna
    # cada pisada: a perna sobe (alta), pisa (contato), assenta (descida) e passa (passagem) antes da próxima subir; nada muda num quadro só
    ch = [(1, estado(H, "passagem"))]
    for i, fl in enumerate(fs):
        lado = (lambda P: A4.mir(P)) if i % 2 else (lambda P: P)
        ch += [(max(2, fl - 4), lado(estado(H, "alta"))), (fl, lado(estado(H, "contato"))), (min(N, fl + 2), lado(estado(H, "descida")))]
        if i + 1 < len(fs):
            ch.append((fl + 5, estado(H, "passagem")))
    ch.append((N, ch[-1][1]))
    ch = sorted({c[0]: c for c in ch}.values(), key=lambda c: c[0])
    AP.sombra_de(H).anima(ch, 1, N, vida=0.2, seed=6, mola=False)
    escala_h(H, N, escala, base=H.raiz.scale[0])
    z_com_escala(H, escala)
    H.expressao([(1, dict(boca="o", olhos=1.12, brow=0.7)), (N, dict(boca="o", olhos=1.18, brow=1.0))], 1, N, piscar=True)
    # a câmera: recua o tempo todo, mais devagar do que ele cresce (de 0,35 a 2,6: x7,4 contra x16 dele), um tranco leve em cada pisada
    D = lambda f: 0.2 * (2.2 / 0.2) ** suave(faixa(f, 1, N))          # de 0,2 a 2,2 (x11) contra x16 dele: ele cresce no quadro
    pos = lambda f: (-1.7 * D(f), -1.9 * D(f), 0.5 * D(f))
    alvo = lambda f: (0.35 * D(f), 0.5 * D(f), 0.42 * D(f))
    camera_olhando(N, pos, alvo, extra=lambda f: (soco_suave(f, fs, 0.012 * D(f), osc=0.0), 0.0), mao=0.3)      # só desce um pouco no impacto: o giro em cada pisada parecia travar
    # a caixa com a altura: uma por tamanho, em cima da cabeça, troca em cada pisada
    marcos = [1] + fs + [N + 8]
    cam_dir = (-1.7, -1.9, 0.0)
    for i, txt in enumerate(ROTULOS):
        f_in, f_out = marcos[i], marcos[i + 1]
        s_i = s0 * 2 ** i; Dm = D(min(N, f_in + 3))
        import provas_passos7 as P7
        P7.pilula_cam(f"cont{i}", txt, (0.0, 0.0, 1.8 * s_i + 0.14 * Dm), 0.09 * Dm, cam_dir)
        mostra(objs(f"cont{i}_pil", f"cont{i}_txt"), f_in, f_in + 2, f_out, f_out + 2, N=N)
    poeira_anim(N, fs[-1], raio=1.0)


# ======================================================================== 9D: a vista até o horizonte
@r("9D")
def a9D(N):
    H = A.REG["eu"]; q = lambda t: fq("9D", t)
    P0 = pose_parado(H, cabeca=-22); P1 = pose_parado(H, cabeca=-2)
    anima_estados(H, [(1, P0), (q(49.9), P0), (q(50.4), P1), (N, P1)], N, vida=0.4, mola=False)
    segs = sorted(cada("visao"), key=lambda o: o.name)
    for i, o in enumerate(segs):                                       # a linha corre dos olhos até o horizonte
        f_on = int(round(lerp(q(50.94), q(51.7), i / max(1, len(segs) - 1))))
        aparece([o], f_on, f_on + 2, N=N)
    mostra(objs("horizonte_ponto", "fio_pilula", "km150_pil", "km150_txt"), q(52.02), q(52.02) + 5, N=N)
    A.camera_viva(N, frente=0.04, mao=0.25)


# ======================================================================== 10C: da boca ao chão
@r("10C")
def a10C(N):
    H = A.REG["eu"]; q = lambda t: fq("10C", t)
    vivo(H, N, vida=0.6)
    H.expressao([(1, dict(boca="reta", olhos=1.0, brow=0.0)), (q(56.1), dict(boca="o", olhos=1.05, brow=0.3)), (N, dict(boca="o", olhos=1.05, brow=0.3))], 1, N, piscar=True)
    perto = ((-1.7, -0.32, 1.52), (0.0, -0.32, 1.52))
    longe = ((-3.12, -0.45, 0.95), (0.0, -0.45, 0.95))
    camera_caminho(N, [(1, perto[0], perto[1]), (q(56.98), (perto[0][0] - 0.05, perto[0][1], perto[0][2] - 0.02), perto[1]),
                       (q(58.2), longe[0], longe[1]), (N, (longe[0][0] + 0.08, longe[0][1], longe[0][2]), longe[1])])
    mostra(objs("p_boca_pil", "p_boca_txt"), q(57.84), q(57.84) + 5, N=N)          # "metade"
    mostra(objs("p_chao_pil", "p_chao_txt"), q(58.42), q(58.42) + 5, N=N)          # "pressão" (as duas ficam no quadro até o corte)


# ======================================================================== 11B: ele e a Lua lado a lado
@r("11B")
def a11B(N):
    H = A.REG["eu"]; q = lambda t: fq("11B", t)
    P0 = pose_parado(H, cabeca=0, olha=0); P1 = pose_parado(H, cabeca=-6, olha=40)
    anima_estados(H, [(1, P0), (q(60.6), P0), (q(61.2), P1), (N, P1)], N, vida=0.4, mola=False)
    lua = bpy.data.objects.get("lua")
    if lua is not None:                                                # a Lua chega pela direita e assenta ao lado dele
        x1 = lua.location.x; x0 = x1 + 3.2
        for f in range(1, N + 1):
            u = suave(faixa(f, 1, q(61.3)))
            lua.location.x = lerp(x0, x1, u); key(lua, "location", f, "LINEAR")
            lua.rotation_euler.z = 0.25 * (f - 1) / FPS; key(lua, "rotation_euler", f, "LINEAR")
    mostra(objs("ch_ele", "ch_ele_p0", "ch_ele_p1", "p_ele_pil", "p_ele_txt"), q(61.68), q(61.68) + 5, N=N)
    mostra(objs("ch_lua", "ch_lua_p0", "ch_lua_p1", "p_lua_pil", "p_lua_txt"), q(62.26), q(62.26) + 5, N=N)
    for j, o in enumerate(sorted(cada("topo"), key=lambda o: o.location.x)):
        f_on = q(62.54) + 2 * j
        aparece([o], f_on, f_on + 2, N=N)
    A.camera_viva(N, frente=0.06, mao=0.2)


if __name__ == "__main__":
    AP.main()
