"""Animação do replanejamento v15 (aprovado em 26/10/2026). Planos em story_passos9.py; o resto vem do v14 (anim_passos8).
  8E  as caixas acendem em "Burj" e "oitocentos"; a câmera chega ao topo da agulha em "...oito metros"; a linha tracejada corre da agulha até ele;
  9A  ele pisa em "décimo" (44,40 s) e dobra de 922 m a 1,8 km; o Burj passa a bater no quadril; a caixa 'ele: 1,8 km' em "dois quilômetros";
  9C  o fio de cabelo desce do céu e para ao lado da lata; a caixa do cabelo em "cabelo" (47,38 s), a da lata em "lata" (48,54 s);
  10A ele pisa em "doze" (53,20 s) e dobra; as nuvens ficam no joelho; o avião cruza o céu em "sete quilômetros"; a caixa 'ele: 7,4 km';
  13A o tênis desce e para em cima da Terra em "vigésimo" (72,68 s); a caixa 'a Terra' acende em "oitavo";
  13B a linha amarela desenha da Terra à Lua em "distância" (74,54 s) e, em "quilômetros" (77,96 s), gira até ficar de pé ao lado dele.
blender -b -P anim_passos9.py -- PLANO PASTA [--scale 0.5] [--samples 10] [--quadros 1,M,N] [--colisao] [--mede] [--espaco] [--sync]"""
import os, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy
from mathutils import Vector
import story_passos9 as S9
import anim_passos8 as A8                                   # as cinco animações do v14 (e o resto, via anim_passos7)
import anim_passos4 as A4
import anim_passos as AP
import lib
from anim_passos import A, key, lerp, suave, faixa, fq, estado, anima_estados, vivo, escala_h, aparece, poeira_anim, soco_suave, cada, camera_caminho, FPS
from anim_passos4 import mostra, objs, camera_olhando
from anim_passos8 import pose_parado, z_com_escala
import profundidade as PF

ANIM = AP.ANIM
PF.ABERTURA.update({"8E": 22.0, "9A": 22.0, "9C": 5.0, "10A": 8.0})
PF.ENEVOA_POR.update({"8E": 0.12, "9A": 0.12, "9C": 0.25, "10A": 0.25})


def r(nome):
    def deco(fn):
        ANIM[nome] = fn
        return fn
    return deco


def pisa_e_cresce(H, N, fl, de, para=1.0):
    """o pé desce e pisa no quadro fl; o corpo cresce de 'de' a 'para' em 13 quadros a partir daí"""
    AP.POUSOS.append(fl)
    AP.pouso(H, N, fl)
    c = AP.cresce(fl, fl + 13, de=de, para=para, p=0.06)
    escala_h(H, N, c)
    z_com_escala(H, c)


# ======================================================================== 8E: o Burj ao lado dele
@r("8E")
def a8E(N):
    H = A.REG["eu"]; q = lambda t: fq("8E", t)
    vivo(H, N, vida=0.5)
    H.expressao([(1, dict(boca="o", olhos=1.15, brow=0.8)), (N, dict(boca="o", olhos=1.15, brow=0.8))], 1, N, piscar=True)
    mostra(objs("p_ele_pil", "p_ele_txt"), 1, 6, q(42.9), q(42.9) + 4, N=N)
    mostra(objs("p_burj_pil", "p_burj_txt"), q(40.64), q(40.64) + 5, q(42.9), q(42.9) + 4, N=N)                          # "Khalifa"
    c = AP.cam()
    L0 = Vector(c.location); fw = (c.rotation_euler.to_matrix() @ Vector((0, 0, -1))).normalized()
    # a câmera chega ao topo: sobe da altura do peito até a ponta da agulha, chegando perto (de 1,0 a 1,68 de altura, de 2,5 a 1,05 de campo)
    f_ini, f_fim = q(42.4), q(43.4)
    T0 = Vector((0.375, 0.5 * 512 * 0.0 + (S9.P8.BURJ_M[1] * 2.0 ** -9) * 0.5, 1.0)); T1 = Vector((0.375, (S9.P8.BURJ_M[1] * 2.0 ** -9) * 0.45, 1.68))
    for f in range(1, N + 1):
        u = suave(faixa(f, f_ini, f_fim))
        Tg = T0.lerp(T1, u)
        loc = Vector(L0).lerp(Vector(L0) + fw * (L0 - Vector((Tg.x, Tg.y, L0.z))).length * 0.0, 0.0)
        loc.z = lerp(L0.z, 1.68, u)
        c.location = loc
        c.rotation_euler = (Tg - loc).to_track_quat("-Z", "Y").to_euler()
        c.data.lens = lerp(300.0, 300.0 * 1.5, u)
        key(c, "location", f, "LINEAR"); key(c, "rotation_euler", f, "LINEAR"); key(c.data, "lens", f, "LINEAR")
    mostra(objs("nivel0", "nivel2", "nivel4", "nivel6"), q(43.2), q(43.2) + 5, N=N)
    mostra(objs("p_burj_pil", "p_burj_txt", "p_ele_pil", "p_ele_txt"), 1, 6, q(42.9), q(42.9) + 4, N=N)                       # as caixas grandes saem quando a câmera chega perto
    mostra(objs("p_burj_topo_pil", "p_burj_topo_txt", "p_ele_topo_pil", "p_ele_topo_txt"), q(43.0), q(43.0) + 5, N=N)         # e entram as do topo


# ======================================================================== 9A: o décimo passo
@r("9A")
def a9A(N):
    H = A.REG["eu"]; q = lambda t: fq("9A", t)
    fl = q(44.40)
    AP.POUSOS.append(fl)
    ch = [(1, estado(H, "passagem")), (max(2, fl - 5), estado(H, "alta")), (fl, estado(H, "contato")), (fl + 5, estado(H, "descida")), (N, estado(H, "descida"))]
    ch = sorted({c[0]: c for c in ch}.values(), key=lambda c: c[0])
    AP.sombra_de(H).anima(ch, 1, N, vida=0.3, seed=6, mola=False)
    c = AP.cresce(fl, fl + 13, de=0.5, para=1.0, p=0.06)
    escala_h(H, N, c, base=H.raiz.scale[0])
    z_com_escala(H, c)
    H.expressao([(1, dict(boca="o", olhos=1.12, brow=0.7)), (fl + 3, dict(boca="o", olhos=1.2, brow=1.0)), (N, dict(boca="o", olhos=1.12, brow=0.7))], 1, N, piscar=True)
    mostra(objs("p_burj_pil", "p_burj_txt"), 1, 6, N=N)
    mostra(objs("p_ele_pil", "p_ele_txt"), q(45.76), q(45.76) + 5, N=N)                           # "dois"
    A.camera_viva(N, frente=0.04, mao=0.25)


# ======================================================================== 9C: o fio de cabelo e a lata
@r("9C")
def a9C(N):
    q = lambda t: fq("9C", t)
    H = AP.humanos().get("homem")
    if H is not None:                                                    # o homem olha para o fio que desce e depois para a lata
        P0 = pose_parado(H); P1 = dict(P0, cabeca=-26, olha=-18); P2 = dict(P0, cabeca=14, olha=10)
        anima_estados(H, [(1, P0), (q(47.2), P0), (q(47.9), P1), (q(48.5), P2), (N, P2)], N, vida=0.5, mola=False)
        H.expressao([(1, dict(boca="reta", olhos=1.0, brow=0.0)), (q(47.6), dict(boca="o", olhos=1.15, brow=0.8)), (N, dict(boca="o", olhos=1.15, brow=0.8))], 1, N, piscar=True)
    for k, h in AP.humanos().items():
        if k != "homem":
            vivo(h, N, seed=sum(map(ord, k)) % 11, vida=0.4)
    fio = bpy.data.objects.get("fio"); brilho = bpy.data.objects.get("fio_brilho")
    f0, f1 = q(47.38), q(48.0)
    for o in [x for x in (fio, brilho) if x is not None]:               # o fio desce do céu: de cima (sobe 3 m) até o lugar
        z1 = o.location.z
        for f in range(1, N + 1):
            u = suave(faixa(f, f0 - 6, f1))
            o.location.z = z1 + 3.2 * (1 - u); key(o, "location", f, "LINEAR")
    mostra(objs("p_fio_pil", "p_fio_txt"), f1, f1 + 5, N=N)                                        # "cabelo"
    mostra(objs("p_lata_pil", "p_lata_txt"), q(48.54), q(48.54) + 5, N=N)                           # "lata"
    c = AP.cam(); L0 = Vector(c.location); T0 = Vector((L0.x, L0.y + 1.7, L0.z))
    for f in range(1, N + 1):                                            # a câmera chega perto da lata (de 1,7 m a 1,2 m)
        u = suave(faixa(f, q(47.0), q(48.8)))
        loc = L0 + Vector((0.0, 0.5 * u, 0.0))
        c.location = loc; c.rotation_euler = (T0 - loc).to_track_quat("-Z", "Y").to_euler()
        key(c, "location", f, "LINEAR"); key(c, "rotation_euler", f, "LINEAR")


# ======================================================================== 10A: doze passos, nas nuvens
@r("10A")
def a10A(N):
    H = A.REG["eu"]; q = lambda t: fq("10A", t)
    fl = q(53.20)
    AP.POUSOS.append(fl)
    ch = [(1, estado(H, "passagem")), (max(2, fl - 5), estado(H, "alta")), (fl, estado(H, "contato")), (fl + 6, estado(H, "descida")),
          (fl + 14, estado(H, "olha_baixo")), (N, estado(H, "olha_baixo"))]
    ch = sorted({c[0]: c for c in ch}.values(), key=lambda c: c[0])
    AP.sombra_de(H).anima(ch, 1, N, vida=0.3, seed=6, mola=False)
    c = AP.cresce(fl, fl + 13, de=0.5, para=1.0, p=0.06)
    escala_h(H, N, c, base=H.raiz.scale[0])
    z_com_escala(H, c)
    H.expressao([(1, dict(boca="reta", olhos=1.0, brow=0.0)), (fl + 3, dict(boca="o", olhos=1.15, brow=0.9)), (N, dict(boca="o", olhos=1.1, brow=0.7))], 1, N, piscar=True)
    poeira_anim(N, fl, raio=1.0)
    av = bpy.data.objects.get("aviao"); anel = bpy.data.objects.get("anel_av"); rastro = bpy.data.objects.get("rastro")
    grupo = [o for o in (av, anel, rastro) if o is not None]
    f_a, f_b = q(54.52), q(55.8)
    for o in grupo:                                                       # o avião cruza de um lado ao outro do céu, devagar
        y1 = o.location.y
        for f in range(1, N + 1):
            u = suave(faixa(f, f_a - 10, f_b))
            o.location.y = y1 + 1.1 * (0.5 - u); key(o, "location", f, "LINEAR")
    mostra(grupo, f_a - 10, f_a - 4, N=N)
    mostra(objs("p_av_pil", "p_av_txt"), f_a + 4, f_a + 9, N=N)
    mostra(objs("p_ele_pil", "p_ele_txt"), f_a, f_a + 5, N=N)                                       # "sete quilômetros"
    A.camera_viva(N, frente=0.03, mao=0.25)


# ======================================================================== 13A: o tênis sobre a Terra
@r("13A")
def a13A(N):
    H = A.REG["eu"]; q = lambda t: fq("13A", t)
    fl = q(72.68)
    base = pose_parado(H)
    P0 = dict(base); P0["pos"] = (base["pos"][0], base["pos"][1], base["pos"][2] + 0.1)
    anima_estados(H, [(1, P0), (fl, base), (N, base)], N, vida=0.2, mola=False)
    for t in objs("p_terra_pil", "p_terra_txt"):
        pass
    mostra(objs("p_terra_pil", "p_terra_txt"), q(73.16), q(73.16) + 5, N=N)                          # "oitavo"
    A.camera_viva(N, frente=0.02, mao=0.15)


# ======================================================================== 13B: a Terra, a Lua, a distância
@r("13B")
def a13B(N):
    H = A.REG["eu"]; q = lambda t: fq("13B", t)
    vivo(H, N, vida=0.4)
    f0, f1 = q(74.54), q(75.4)
    f_g0, f_g1 = q(76.5), q(77.5)
    dist = bpy.data.objects.get("dist")
    if dist is not None:                                                  # a linha deitada desenha da Terra à Lua
        b = Vector(dist.scale)
        for f in range(1, N + 1):
            u = suave(faixa(f, f0, f1)) * (1 - suave(faixa(f, f_g0, f_g0 + 4)))
            dist.scale = (b.x * max(u, 1e-4), b.y * max(u, 1e-4), b.z * max(u, 1e-4)); key(dist, "scale", f, "LINEAR")
    mostra(objs("p_d_pil", "p_d_txt"), f1, f1 + 5, f_g0, f_g0 + 3, N=N)
    pe = bpy.data.objects.get("dist_pe")
    if pe is not None:                                                    # a mesma linha, de pé ao lado dele
        b = Vector(pe.scale)
        for f in range(1, N + 1):
            u = suave(faixa(f, f_g0, f_g1))
            pe.scale = (b.x * max(u, 1e-4), b.y * max(u, 1e-4), b.z * max(u, 1e-4)); key(pe, "scale", f, "LINEAR")
    mostra(objs("p_d_pe_pil", "p_d_pe_txt", "p_ele_pil", "p_ele_txt"), f_g1, f_g1 + 5, N=N)
    A.camera_viva(N, frente=0.02, mao=0.2)


if __name__ == "__main__":
    AP.main()
