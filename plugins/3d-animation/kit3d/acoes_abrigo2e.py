"""Animação de verdade das sequências 13 a 17 da parte 2 (o rádio e o giz, a voz na torre, "só eu", o portão, o ferrolho). Ver acoes_abrigo2b.py."""
import math, random
import bpy
from mathutils import Vector
from lib import key
from acoes_abrigo2b import REG, MAOS, CAMS, POV, O, prepara, estado, mov_h, cara, pega, anda, trilha, visivel, mao_mix, rota, cam_ab, semi, grupo, fogo_vivo, mira_mao
from acoes_abrigo2b import pov_para, centra, vento, poeira_cai, figurante, gosma_dedos
from acoes_abrigo2 import camera, suave, faixa, pos_cabeca, acao, lerp, FPS, BY
import story_abrigo2 as S
import objetos3d_abrigo as O3, objetos3d_abrigo2 as O2


def olham(N, alvo, atraso=3, ordem=None, **kw):
    for k, h in enumerate(grupo()):
        t = 3 + atraso * (k % 9)
        mov_h(h, N, [(min(N - 2, t), dict(ver=alvo)), (N, dict(tronco=6))], seed=100 + k, vida=1.1)


# ====================================================================== 13. o rádio e o quadro de giz
@acao("13A")
def a13A(N):
    """a mão do líder gira o botão do rádio e a agulha do mostrador corre; o mostrador acende"""
    prepara("13A"); fogo_vivo(N)
    piv = O("hL_piv"); m = MAOS["hL"]; ag = O("radio_agulha")
    p0 = Vector(piv.location); r0 = Vector(piv.rotation_euler)
    for f in range(1, N + 1):
        u = suave(faixa(f, 3, N - 3))
        piv.rotation_euler = (r0.x + math.radians(40 * u), r0.y, r0.z); key(piv, "rotation_euler", f, "LINEAR")
        piv.location = (p0.x, p0.y + 0.004 * math.sin(f * 1.3), p0.z); key(piv, "location", f, "LINEAR")
    if ag is not None:
        l0 = Vector(ag.location)
        for f in range(1, N + 1):
            ag.location = (l0.x + 0.06 * suave(faixa(f, 4, N)), l0.y, l0.z); key(ag, "location", f, "LINEAR")
    cam_ab(N, mao=0.5)


@acao("13B")
def a13B(N):
    """a mulher de fone gira a sintonia com as duas mãos e escuta, inclinando a cabeça; a vela e o telefone ao lado tremem de leve"""
    prepara("13B"); fogo_vivo(N)
    h = REG["radio"]
    ks = []
    for k in range(0, N, 5):
        ks.append((2 + k, dict(ombro=(-40, -46), cotovelo=(-60, -54), cabeca=8, olha=6)))
        ks.append((4 + k, dict(ombro=(-48, -40), cotovelo=(-52, -62), cabeca=10, olha=-4)))
    mov_h(h, N, ks, seed=4, vida=0.8)
    cara(h, N, [(1, dict(boca="reta", lid=0.4)), (8, dict(boca="reta", lid=0.55)), (N, dict(boca="o", lid=0.3, brow=0.5))], piscar=True)
    cam_ab(N, mao=0.7)


@acao("13C")
def a13C(N):
    """a mão risca o quadro de giz: o risco desce enquanto a mão desce com ele"""
    prepara("13C"); fogo_vivo(N)
    mp, mg, rk = O("mao_giz_piv"), O("giz_na_mao"), O("risco_novo")
    p0, g0, k0 = Vector(mp.location), Vector(mg.location), Vector(rk.location)
    topo = 1.39; b0 = 1.30
    for f in range(1, N + 1):
        u = suave(faixa(f, 3, N - 3)); dz = -0.13 * u
        mp.location = (p0.x, p0.y, p0.z + dz); key(mp, "location", f, "LINEAR")
        mg.location = (g0.x, g0.y, g0.z + dz); key(mg, "location", f, "LINEAR")
        b = b0 + dz; h = topo - b
        rk.scale = (1, 1, h / 0.09); rk.location = (k0.x, k0.y, (topo + b) / 2); key(rk, "scale", f, "LINEAR"); key(rk, "location", f, "LINEAR")
    cam_ab(N, mao=0.5)


@acao("13D")
def a13D(N):
    """travelling lateral do quadro de riscos ao mapa do mundo; alguém atravessa o fundo andando e as luzes oscilam"""
    prepara("13D"); fogo_vivo(N)
    figurante("menino", (-4.2, 0.5, 0), (-0.8, 0.6, 0), N, ciclo=20, seed=3, rot=-90 + 180)
    cam_ab(N, mao=0.8, warp=1.0, mix=1.0, nk=4)


@acao("13E")
def a13E(N):
    """dolly-in no quadro: o último risco é feito (a mão entra, risca e sai), a luz da vela oscila"""
    prepara("13E"); fogo_vivo(N)
    from acoes_abrigo2b import mao_mix
    giz = O3  # noqa
    S.giz_cor(Vector((-3.3, 3.80, 1.30)), S.manga_de("radio"), riscado=0.0)
    mp, mg, rk = O("mao_giz_piv"), O("giz_na_mao"), O("risco_novo")
    p0, g0, k0 = Vector(mp.location), Vector(mg.location), Vector(rk.location)
    for f in range(1, N + 1):
        u = suave(faixa(f, 8, N - 6)); dz = -0.12 * u; ent = suave(faixa(f, 1, 8)); sai = suave(faixa(f, N - 5, N))
        off = Vector((-0.25 * (1 - ent) - 0.25 * sai, 0.0, 0.05 * sai))
        mp.location = p0 + Vector((0, 0, dz)) + off; key(mp, "location", f, "LINEAR")
        mg.location = g0 + Vector((0, 0, dz)) + off; key(mg, "location", f, "LINEAR")
        b = 1.30 + dz; rk.scale = (1, 1, max(0.01, (1.39 - b)) / 0.09); rk.location = (k0.x + off.x, k0.y, (1.39 + b) / 2); key(rk, "scale", f, "LINEAR"); key(rk, "location", f, "LINEAR")
    cam_ab(N, mao=0.5)


@acao("13F")
def a13F(N):
    """os nove em fila atrás da fogueira se olham devagar, abaixam a cabeça e a levantam para a câmera, um depois do outro; o fogo estala"""
    prepara("13F"); fogo_vivo(N)
    for k, h in enumerate(grupo()):
        t = 4 + 2 * k
        mov_h(h, N, [(t, dict(cabeca=14, tronco=4)), (min(N - 1, t + 8), dict(cabeca=-2, tronco=0)), (N, dict(cabeca=0))], seed=110 + k, vida=1.2)
    cam_ab(N, mao=0.5)


# ====================================================================== 14. a voz na torre
@acao("14A")
def a14A(N):
    """macro do alto-falante de pano: a tela vibra no ritmo da voz e a poeira acesa dança no ar"""
    prepara("14A"); fogo_vivo(N)
    tela = O("radio_tela")
    if tela is not None:
        s0 = Vector(tela.scale); l0 = Vector(tela.location)
        for f in range(1, N + 1):
            v = 0.02 * math.sin(f * 2.9) + 0.012 * math.sin(f * 5.3)
            tela.location = (l0.x, l0.y - 0.002 - 0.004 * abs(math.sin(f * 1.4)), l0.z); key(tela, "location", f, "LINEAR")
            tela.scale = (s0.x * (1 + v), s0.y, s0.z * (1 - v)); key(tela, "scale", f, "LINEAR")
    for k in range(16):
        p = O(f"pz{k}")
        if p is None:
            continue
        l0 = Vector(p.location); ph = k * 1.3
        for f in range(1, N + 1):
            p.location = (l0.x + 0.02 * math.sin(f * 0.5 + ph), l0.y - 0.03 * abs(math.sin(f * 0.35 + ph)), l0.z + 0.025 * math.sin(f * 0.4 + ph * 1.7)); key(p, "location", f, "LINEAR")
    cam_ab(N, mao=0.4)


@acao("14B")
def a14B(N):
    """todos inclinados para o rádio, as caras acesas de âmbar: se aproximam um pouco, prendem a respiração e se imobilizam; um leva a mão ao pano"""
    prepara("14B"); fogo_vivo(N)
    for k, h in enumerate(grupo()):
        t = 3 + k
        mov_h(h, N, [(t + 6, dict(tronco=22, cabeca=14)), (N, dict(tronco=26, cabeca=12))], seed=120 + k, vida=0.7)
    cam_ab(N, mao=0.6)


@acao("14C")
def a14C(N):
    """subindo a escada para o telhado: o líder na frente, eu logo atrás; mãos e pés alternam degrau a degrau; a câmera sobe com eles em direção à luz azul"""
    prepara("14C"); fogo_vivo(N)
    L = REG["lider"]; n = REG["eu"]
    for h, z0, atraso in ((L, 2.3, 0), (n, 0.9, 5)):
        ks = []
        for k in range(0, N, 8):
            ks.append((1 + k + atraso, dict(ombro=(-150, -125), quadril=(-55, -10), joelho=(65, 10), dpos=(0, 0, 0.0))))
            ks.append((5 + k + atraso, dict(ombro=(-125, -150), quadril=(-10, -55), joelho=(10, 65))))
        h.raiz.location = (4.25, 1.2, z0)
        ks2 = [(f, dict(d, pos=(4.25, 1.2, z0 + 1.25 * faixa(f, 1, N)))) for f, d in ks]
        mov_h(h, N, ks2, seed=130 + atraso, vida=0.5)
    camera(N, [(1, (4.3, -1.7, 1.2), (4.4, 1.2, 2.3), 28, (4.4, 1.2, 2.0), 4.0),
               (N // 2, (4.3, -1.6, 1.7), (4.4, 1.2, 2.8), 28, (4.4, 1.2, 2.6), 4.0),
               (N, (4.3, -1.5, 2.2), (4.4, 1.2, 3.4), 28, (4.4, 1.2, 3.2), 4.0)], mao=0.8)


@acao("14D")
def a14D(N):
    """no telhado: o vento levanta a cinza no facho da lanterna; o líder varre o facho pela cidade e eu olho o horizonte, a roupa balançando"""
    prepara("14D")
    L = REG["lid"]; n = REG["eu"]; lan = O("lant")
    pega(lan, L, "F")
    mov_h(L, N, [(8, dict(ver=(-8.0, 20.0), ombro=(-80, 5))), (16, dict(ver=(8.0, 20.0), ombro=(-64, 5))), (N, dict(ver=(0.0, 30.0)))], seed=3, vida=1.2)
    mov_h(n, N, [(6, dict(ver=(-6.0, 30.0))), (N, dict(ver=(4.0, 40.0), cabeca=-6))], seed=4, vida=1.4)
    vento(N, n=18, de=(-4.0, -3.0, 14.0), ate=(4.0, -1.0, 15.5), caixa=(2.5, 1.5, 1.2), seed=9, tam=0.03, cor="#cfd4de", prefixo="cin")
    cam_ab(N, mao=1.0)


@acao("14E")
def a14E(N):
    """minha nuca em primeiro plano; a cabeça e a câmera sobem juntas até a torre com a luz vermelha, que pisca devagar; a cinza passa voando"""
    prepara("14E")
    n = REG["eu"]
    mov_h(n, N, [(8, dict(cabeca=-4)), (N, dict(cabeca=-24, tronco=-4))], vida=1.4, seed=2)
    for nm in ("torre_luz", "torre_l", "torre_lamp"):
        o = O(nm)
        if o is not None:
            visivel(o, N, lambda f: (f // 5) % 3 != 2)
    vento(N, n=14, de=(-3.0, -3.0, 14.5), ate=(3.0, -2.0, 16.0), caixa=(2.0, 1.0, 1.0), seed=4, tam=0.025, cor="#cfd4de", prefixo="cin")
    camera(N, [(1, (0.0, -2.9, 15.7), (0.0, -1.6, 15.7), 50, (0.0, -1.6, 15.7), 2.8),
               (int(N * 0.4), (0.0, -3.0, 15.8), (0.0, 20.0, 18.0), 50, (0.0, 20.0, 18.0), 8.0),
               (N, (0.0, -3.0, 15.6), (36.0, 520.0, 115.0), 85, (36.0, 520.0, 100.0), 8.0)], mao=0.7)


# ====================================================================== 15. só eu
@acao("15A")
def a15A(N):
    """travelling lateral rápido pela fila: cada rosto de pano vira para a câmera à medida que ela passa; o peito de cada um sobe e desce"""
    prepara("15A"); fogo_vivo(N)
    for k, h in enumerate(grupo()):
        x = h.raiz.location.x; t = max(2, int(1 + (x + 3.2) / 6.4 * (N - 6)))
        mov_h(h, N, [(t - 2, dict(ver=(x, 6.0))), (min(N - 1, t + 3), dict(ver=(x, -0.7), cabeca=-2)), (N, dict(tronco=2))], seed=140 + k, vida=1.2)
    cam_ab(N, mao=0.6, warp=1.0, mix=1.0, nk=4)


@acao("15B")
def a15B(N):
    """o líder baixa os olhos para o fogo: a cabeça desce devagar, a pálpebra cai, os ombros cedem; os outros atrás desviam o olhar"""
    prepara("15B"); fogo_vivo(N)
    L = REG["lider"]
    mov_h(L, N, [(6, dict(cabeca=18)), (N, dict(cabeca=30, tronco=8))], seed=3, vida=0.8)
    cara(L, N, [(1, dict(boca="triste", lid=0.78)), (N, dict(boca="triste", lid=0.95))], piscar=False)
    for nome in ("taco", "cochicho"):
        mov_h(REG[nome], N, [(8, dict(cabeca=18, ver=(-1.0, 0.0))), (N, dict(cabeca=22))], seed=sum(map(ord, nome)) % 20, vida=1.0)
    cam_ab(N, mao=0.4)


@acao("15B2")
def a15B2(N):
    """macro: as pontas dos dedos do líder pretas e pingando: a gosma cresce e os pingos caem; a mão treme"""
    prepara("15B2")
    gosma_dedos("hL_", N, 0.5, 1.0, n=5, cai=0.1)
    pv = O("hL_piv"); p0 = Vector(pv.location)
    for f in range(1, N + 1):
        pv.location = (p0.x, p0.y + 0.003 * math.sin(f * 2.2), p0.z + 0.002 * math.sin(f * 3.1)); key(pv, "location", f, "LINEAR")
    cam_ab(N, mao=0.4)


@acao("15C")
def a15C(N):
    """pan subjetivo: todos os olhos em mim; o círculo se fecha um passo, cada um no seu tempo, enquanto a câmera gira"""
    prepara("15C"); fogo_vivo(N)
    for k, h in enumerate(grupo()):
        x, y = h.raiz.location.x, h.raiz.location.y
        u = Vector((0.0 - x, -1.0 - y)).normalized(); P = dict(getattr(h, "_P", {}))
        if k % 3 == 0:
            anda(h, N, (x, y, 0), (x + u.x * 0.3, y + u.y * 0.3, 0), f0=3 + k, f1=min(N - 4, 11 + k), ciclo=20, inclina=2, seed=150 + k, arranque=0.1, freia=0.3, antes=dict(P), depois=dict(P))
        else:
            mov_h(h, N, [(4 + k, dict(cabeca=-3, tronco=3)), (N, dict(tronco=5))], seed=150 + k, vida=1.0)
    cam_ab(N, mao=0.9)


@acao("15D")
def a15D(N):
    """o suéter da Rita aberto na cinza, de noite: o vento mexe nas mangas, a cinza passa, a câmera desce devagar sobre ele"""
    prepara("15D")
    for nm in ("sue_m-1", "sue_m1"):
        o = O(nm)
        if o is not None:
            r0 = Vector(o.rotation_euler); l0 = Vector(o.location); s = -1 if "-1" in nm else 1
            for f in range(1, N + 1):
                o.rotation_euler = (r0.x, r0.y + math.radians(3 * math.sin(f * 0.5 + s)), r0.z + math.radians(4 * math.sin(f * 0.35 + s))); key(o, "rotation_euler", f, "LINEAR")
                o.location = (l0.x, l0.y, l0.z + 0.004 * abs(math.sin(f * 0.5 + s))); key(o, "location", f, "LINEAR")
    vento(N, n=12, de=(-3.0, 7.0, 0.1), ate=(3.0, 8.0, 1.0), caixa=(1.5, 1.0, 0.6), seed=11, tam=0.05, cor="#c8ccd8", prefixo="cin")
    cam_ab(N, mao=0.6)


@acao("15E")
def a15E(N):
    """a mão aperta o pano até o nó dos dedos; a câmera sobe da mão ao meu rosto e eu decido: o olhar firma, a sobrancelha desce"""
    prepara("15E"); fogo_vivo(N)
    n = REG["eu"]; pano = O("pano_m")
    cara(n, N, [(1, dict(boca="reta", lid=0.4)), (14, dict(boca="reta", lid=0.35)), (24, dict(boca="reta", lid=0.05, brow=-0.6)), (N, dict(boca="reta", lid=0.0, brow=-0.7))], piscar=True)
    mov_h(n, N, [(14, dict(cabeca=6)), (26, dict(cabeca=-2, tronco=-2)), (N, dict(cabeca=-4))], vida=1.3, seed=2)
    if pano is not None:
        trilha(pano, N, esc=[(1, (1, 1, 1)), (12, (0.8, 0.8, 1.4)), (N, (0.75, 0.75, 1.5))])
    cam_ab(N, mao=0.6)


@acao("15F")
def a15F(N):
    """três batidas no portão: a cada uma o grupo se sobressalta e vira a cabeça mais para lá; na terceira, todos olham fixo; poeira cai e a câmera treme"""
    prepara("15F"); fogo_vivo(N)
    b = [6, 15, 24]
    for k, h in enumerate(grupo()):
        mov_h(h, N, [(b[0] + k % 3, dict(ver=(0.6, 3.8), tronco=-4, ombro=(-20, -20))), (b[1] + k % 2, dict(tronco=-8, ombro=(-34, -34))), (b[2], dict(tronco=-2, ombro=(-50, -44)))],
              seed=160 + k, vida=0.6, molas=dict(tronco=(0, 8.0, 0.7)))
        cara(h, N, [(1, dict(boca="reta", lid=0.3)), (b[0] + 1, dict(boca="o", lid=0.0, brow=0.8)), (N, dict(boca="o", lid=0.0, brow=0.8))], piscar=False)
    n = REG["eu"]
    mov_h(n, N, [(b[0] + 1, dict(ver=(0.6, 3.8))), (b[2], dict(tronco=-4))], vida=1.0, seed=2)
    cara(n, N, [(1, dict(boca="reta", lid=0.3)), (b[0] + 1, dict(boca="o", lid=0.0))], piscar=False)
    poeira_cai(N, x=(-1.0, 1.0), y=(1.5, 3.0), z=(1.0, 3.0), n=14, seed=3, vel=0.3)
    camera(N, [(1, (1.3, 3.4, 1.55), (0.0, -0.5, 1.35), 28, (0.0, -0.3, 1.4), 5.6),
               (N, (1.2, 3.1, 1.55), (0.0, -0.5, 1.35), 28, (0.0, -0.3, 1.4), 5.6)], mao=0.8, tranco=tuple(b))


# ====================================================================== 16. o portão
@acao("16A")
def a16A(N):
    """dolly-in pelo galpão até o portão: as luzes e o varal passam em primeiro plano; o fogo treme; três batidas fazem a poeira cair do portão"""
    prepara("16A"); fogo_vivo(N)
    poeira_cai(N, x=(-1.0, 2.4), y=(3.0, 3.7), z=(1.0, 3.1), n=16, seed=7, vel=0.3)
    cam_ab(N, mao=0.8, tranco=(5, 11, 17) if N > 17 else ())


@acao("16B")
def a16B(N):
    """a fresta de luz azul no pé do portão: uma sombra passa do outro lado, para, se aproxima da fresta e outra aparece; a luz azul pulsa"""
    prepara("16B"); fogo_vivo(N)
    for k in range(3):
        o = O(f"sombra{k}")
        if o is None:
            continue
        l0 = Vector(o.location); s0 = Vector(o.scale)
        for f in range(1, N + 1):
            u = faixa(f, 2 + 3 * k, N); e = u * u * (3 - 2 * u)
            para = 0.5 + 0.5 * math.sin(f * 0.6 + k)
            o.location = (l0.x + (0.5 + 0.2 * k) * e * (0.7 + 0.3 * para), l0.y, l0.z); key(o, "location", f, "LINEAR")
            o.scale = (s0.x * (1 + 0.3 * math.sin(f * 0.9 + k)), s0.y, s0.z); key(o, "scale", f, "LINEAR")
    cam_ab(N, mao=0.7)


@acao("16C")
def a16C(N):
    """o ferrolho pula no trilho a cada batida (três), a poeira cai do portão; a câmera dá um tranco em cada uma"""
    prepara("16C"); fogo_vivo(N)
    b = O("galpao_portao_barra")
    bat = [4, 10, 16]
    if b is not None:
        l0 = Vector(b.location)
        for f in range(1, N + 1):
            d = 0.0
            for q, fb in enumerate(bat):
                u = f - fb
                if 0 <= u < 6:
                    d += (0.035 + 0.02 * q) * math.exp(-u / 1.6) * math.cos(u * 1.8)
            b.location = (l0.x - 0.07 * faixa(f, 4, N) - d, l0.y, l0.z + abs(d) * 0.3); key(b, "location", f, "LINEAR")
    poeira_cai(N, x=(1.5, 2.8), y=(3.6, 3.78), z=(1.2, 3.0), n=14, seed=8, vel=0.4)
    cam_ab(N, mao=0.7, tranco=tuple(bat))


@acao("16D")
def a16D(N):
    """eu vou para o portão, de passo em passo; o líder me alcança, põe a mão no meu ombro e me segura; eu paro, inclinado para a frente"""
    prepara("16D"); fogo_vivo(N)
    n = REG["eu"]; L = REG["lider"]
    P = dict(getattr(n, "_P", {}))
    anda(n, N, (0.5, 1.7, 0), (0.6, 2.3, 0), f0=1, f1=8, ciclo=17, inclina=3, rot=180, seed=2, arranque=0.0, freia=0.3, antes=dict(P),
         depois=dict(P, tronco=10, olha=0))
    x, y = L.raiz.location.x, L.raiz.location.y
    PL = dict(getattr(L, "_P", {}))
    anda(L, N, (x, y, 0), (0.75, 2.0, 0), f0=1, f1=9, ciclo=15, inclina=3, rot=180, seed=3, arranque=0.0, freia=0.3, antes=dict(PL),
         depois=dict(PL, ombro=(-100, 4), cotovelo=(-20, -12), tronco=6))
    cara(n, N, [(1, dict(boca="reta", lid=0.2)), (10, dict(boca="triste", lid=0.1, brow=0.6))], piscar=False)
    cam_ab(N, mao=0.6)


@acao("16E")
def a16E(N):
    """o meu rosto ouvindo o próprio nome: os olhos se abrem devagar, a boca perde o ar, a cabeça vira um pouco para o portão; o fogo treme atrás"""
    prepara("16E"); fogo_vivo(N)
    n = REG["eu"]
    cara(n, N, [(1, dict(boca="reta", lid=0.2)), (6, dict(boca="o", lid=0.0, brow=0.7, olhos=1.15)), (N, dict(boca="o", lid=0.0, brow=0.9, olhos=1.22))], piscar=False)
    mov_h(n, N, [(5, dict(olha=-8)), (N, dict(olha=6, cabeca=-3))], vida=2.0, seed=2)
    cam_ab(N, mao=0.5)


@acao("16F")
def a16F(N):
    """minha nuca ao portão: eu ando devagar até ficar a um palmo do aço, no lugar onde o Zé ficou; os ombros sobem e descem; a câmera vem atrás"""
    prepara("16F"); fogo_vivo(N)
    n = REG["eu"]; P = dict(getattr(n, "_P", {}))
    anda(n, N, (0.6, 3.1, 0), (0.6, 3.52, 0), f0=4, f1=22, ciclo=24, inclina=2, rot=180, seed=2, arranque=0.2, freia=0.4, antes=dict(P), depois=dict(P, tronco=4, cabeca=-4))
    cam_ab(N, mao=0.5)


# ====================================================================== 17. o ferrolho
@acao("17A")
def a17A(N):
    """a minha mão de manga vermelha chega ao ferrolho, abre, fecha os dedos nele e treme"""
    prepara("17A"); fogo_vivo(N)
    pv = O("mao_piv"); m = MAOS["mao"]
    p0 = Vector(pv.location)
    for f in range(1, N + 1):
        u = suave(faixa(f, 1, N * 0.6)); tr = 0.003 * math.sin(f * 2.4) * faixa(f, N * 0.5, N)
        pv.location = (p0.x + 0.1 * (1 - u) + tr, p0.y - 0.16 * (1 - u), p0.z + 0.04 * (1 - u)); key(pv, "location", f, "LINEAR")
        mao_mix(m, "aberta", "segura", faixa(f, N * 0.5, N), f)
    cam_ab(N, mao=0.5)


@acao("17B")
def a17B(N):
    """o meu rosto encostado no aço, os olhos fechados, respirando: o peito sobe e desce, o bafo embaça e some, e no fim os olhos abrem decididos"""
    prepara("17B"); fogo_vivo(N)
    n = REG["eu"]
    cara(n, N, [(1, dict(boca="reta", lid=1.2)), (int(N * 0.8), dict(boca="reta", lid=1.2)), (N, dict(boca="reta", lid=0.35, brow=-0.3))], piscar=False)
    mov_h(n, N, [(8, dict(tronco=3)), (16, dict(tronco=1)), (24, dict(tronco=3)), (N, dict(tronco=0))], vida=2.4, seed=2)
    bf = O("bafo")
    if bf is not None:
        s0 = Vector(bf.scale)
        for f in range(1, N + 1):
            k = 0.4 + 0.6 * max(0.0, math.sin(f * 2 * math.pi / 14.0)); bf.scale = (s0.x * k, s0.y * k, s0.z * k); key(bf, "scale", f, "LINEAR")
    cam_ab(N, mao=0.4)


@acao("17C")
def a17C(N):
    """o ferrolho começa a correr com a minha mão, devagar e depois mais rápido; a luz azul da fresta cresce e a poeira cai; o plano termina no preto (fecho no pós)"""
    prepara("17C"); fogo_vivo(N)
    b = O("galpao_portao_barra"); pv = O("mao_piv")
    l0 = Vector(b.location); p0 = Vector(pv.location)
    for f in range(1, N + 1):
        u = faixa(f, 14, N - 8); e = u * u
        b.location = (l0.x - 0.3 * e, l0.y, l0.z); key(b, "location", f, "LINEAR")
        pv.location = (p0.x - 0.3 * e + 0.002 * math.sin(f * 1.7), p0.y, p0.z); key(pv, "location", f, "LINEAR")
    poeira_cai(N, x=(1.8, 2.6), y=(3.6, 3.78), z=(1.2, 3.0), n=10, seed=9, vel=0.25)
    cam_ab(N, mao=0.4)
