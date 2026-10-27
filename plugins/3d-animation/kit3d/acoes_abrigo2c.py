"""Animação de verdade das sequências 6 e 7 da parte 2 (o galpão: acordar, a lanterna, o olho, o cochicho). Ver acoes_abrigo2b.py (framework)."""
import math, random
import bpy
from mathutils import Vector
from lib import key
from acoes_abrigo2b import *            # noqa
from acoes_abrigo2b import REG, MAOS, CAMS, O, prepara, estado, mov_h, cara, pega, anda, trilha, visivel, mao_mix, rota, cam_ab, semi, grupo, fogo_vivo, mira_mao
import acoes_abrigo2b as B
from acoes_abrigo2 import camera, sem_osso_vivo, suave, faixa, pos_cabeca, acao, lerp


# ====================================================================== 6. acordar no galpão
@acao("6A")
def a6A(N):
    """acordo no chão: o teto e as luzes em borrão, o foco sobe devagar; os rostos de pano entram pelas bordas, uns dão um passo para perto, todos se inclinam"""
    prepara("6A"); fogo_vivo(N)
    G = grupo()
    for j, h in enumerate(G):
        d0 = 3 + 2 * j
        cx, cy = h.raiz.location.x, h.raiz.location.y
        u = Vector((0.0 - cx, -0.8 - cy)).normalized()
        P = dict(getattr(h, "_P", {}))
        if j % 3 == 1:
            anda(h, N, (cx, cy, 0), (cx + u.x * 0.32, cy + u.y * 0.32, 0), f0=d0, f1=d0 + 9, ciclo=20, inclina=2, seed=10 + j, arranque=0.1, freia=0.3,
                 antes=dict(P), depois=dict(P, tronco=30, cabeca=26))
        else:
            mov_h(h, N, [(d0, dict(tronco=14)), (d0 + 10, dict(tronco=32, cabeca=26)), (N, dict(tronco=30, cabeca=24))], seed=10 + j, vida=1.0)
    camera(N, [(1, (0.0, -0.8, 0.17), (0.0, -0.7, 2.2), 24, (0.0, 6.0, 2.0), 1.2),
               (int(N * 0.45), (0.0, -0.8, 0.19), (0.0, -0.4, 2.0), 24, (0.0, 3.0, 2.0), 1.5),
               (N, (0.0, -0.8, 0.24), (0.0, 0.1, 1.7), 24, tuple(pos_cabeca(G[0])), 2.0)], mao=0.9)


@acao("6B")
def a6B(N):
    """a roda de rostos de pano olhando para baixo, a câmera gira (roll) e sobe; uma mão desce para ver se estou vivo"""
    prepara("6B"); fogo_vivo(N)
    G = grupo()
    for j, h in enumerate(G):
        mov_h(h, N, [(4 + j, dict(cabeca=26, tronco=18)), (14 + j % 4, dict(tronco=26, cabeca=18, olha=8 * (1 if j % 2 else -1))), (N, dict(tronco=22, cabeca=24, olha=-6))],
              seed=20 + j, vida=1.2)
    rd = REG["radio"]
    mov_h(rd, N, [(8, dict(tronco=24)), (N - 4, dict(tronco=30, ombro=(-95, -4), cotovelo=(-40, -12), abre=(4, 6)))], seed=7, vida=0.8)
    camera(N, [(1, (-0.12, -0.8, 0.17), (0.05, -0.6, 2.0), 14, (0.5, 0.3, 1.7), 2.8, 5.0),
               (N // 2, (0.0, -0.8, 0.2), (0.03, -0.55, 2.0), 14, (0.5, 0.3, 1.7), 2.8, 0.0),
               (N, (0.12, -0.8, 0.26), (0.0, -0.5, 2.0), 14, (0.5, 0.3, 1.7), 2.8, -4.0)], mao=0.8)


@acao("6C")
def a6C(N):
    """grua descendo sobre o galpão: ele deitado no centro respira e vira o rosto; o grupo se mexe (um chega perto, o líder se volta para o rádio); o fogo tremendo"""
    prepara("6C"); fogo_vivo(N)
    n = REG["eu"]
    mov_h(n, N, [(10, dict(cabeca=10)), (N, dict(cabeca=-12))], vida=2.2, seed=2)
    cara(n, N, [(1, dict(boca="triste", lid=1.0)), (N, dict(boca="triste", lid=0.7))], piscar=False)
    for nome, d in (("lider", [(8, dict(ver=(-2.6, 2.25))), (N, dict(ver=(0.0, -0.8), tronco=6))]),
                    ("radio", [(6, dict(tronco=10)), (N, dict(tronco=0, ver=(0.0, 1.75)))]),
                    ("taco", [(12, dict(ver=(0.0, -0.8), tronco=8)), (N, dict(tronco=14, cabeca=20))]),
                    ("jovem", [(5, dict(ver=(1.8, 0.0))), (N, dict(ver=(0.0, -0.8)))]),
                    ("trancas", [(N, dict(tronco=16, cabeca=20))]), ("careca", [(10, dict(ver=(0.8, 0.5))), (N, dict(ver=(0.0, -0.8)))]),
                    ("cochicho", [(4, dict(ver=(0.0, -0.8))), (N, dict(tronco=10))]), ("solto", [(N, dict(tronco=12, cabeca=20))])):
        if nome in REG:
            mov_h(REG[nome], N, d, vida=1.1, seed=sum(map(ord, nome)) % 50)
    me = REG["menino"]; x, y = me.raiz.location.x, me.raiz.location.y
    P = dict(getattr(me, "_P", {}))
    anda(me, N, (x, y, 0), (x - 0.45, y - 0.55, 0), f0=4, f1=18, ciclo=21, inclina=2, seed=8, arranque=0.1, freia=0.3, antes=dict(P), depois=dict(P, tronco=14, cabeca=20))
    camera(N, [(1, (0.5, -3.4, 3.5), (0.0, -0.6, 0.2), 24, (0.0, -0.8, 0.3), 8.0),
               (N // 2, (0.38, -2.75, 3.0), (0.0, -0.6, 0.2), 26, (0.0, -0.8, 0.3), 8.0),
               (N, (0.25, -2.1, 2.5), (0.0, -0.6, 0.2), 28, (0.0, -0.8, 0.3), 8.0)], mao=0.7)


@acao("6D")
def a6D(N):
    """de baixo: a mulher do rádio, com as duas mãos na lanterna, inclina o corpo sobre mim e vira o facho para o meu rosto"""
    prepara("6D"); fogo_vivo(N)
    rd = REG["radio"]; lan = O("lant")
    pega(lan, rd, "F")
    mov_h(rd, N, [(4, dict(tronco=8)), (N, dict(tronco=30, cabeca=22, ombro=(-62, -62), cotovelo=(-48, -48), ver=(0.0, -0.8)))], seed=6, vida=0.7)
    for h in grupo():
        if h is not rd:
            mov_h(h, N, [(N, dict(ver=(0.0, -0.8)))], vida=1.0, seed=sum(map(ord, h.nome)) % 40)
    camera(N, [(1, (0.0, -0.9, 0.3), (-0.45, -0.2, 1.1), 35, (-0.5, -0.2, 1.1), 4.0),
               (N, (0.0, -0.85, 0.5), (-0.35, -0.3, 1.15), 35, (-0.35, -0.3, 1.1), 4.0)], mao=0.9)


@acao("6E")
def a6E(N):
    """85 mm no meu rosto: o clarão da lanterna chega perto, eu aperto os olhos e viro a cara; o foco passa da lanterna borrada para o meu olho"""
    prepara("6E")
    n = REG["eu"]; lan = O("lant")
    cara(n, N, [(1, dict(boca="o", lid=0.55)), (8, dict(boca="triste", lid=0.9, brow=-0.5)), (N, dict(boca="triste", lid=0.8, brow=-0.3))], piscar=False)
    mov_h(n, N, [(6, dict(olha=-14, cabeca=6)), (N, dict(olha=-6, cabeca=3))], vida=1.6, seed=3)
    for f in range(1, N + 1):
        u = faixa(f, 1, N)
        lan.location = (-0.5 + 0.18 * u, -1.05 + 0.2 * u, 1.58 - 0.05 * u + 0.012 * math.sin(f * 0.7)); key(lan, "location", f, "LINEAR")
        lan.rotation_euler.z = math.radians(18 + 16 * u + 2 * math.sin(f * 0.9)); key(lan, "rotation_euler", f, "LINEAR")
    camera(N, [(1, (0.05, -1.7, 1.45), (0.0, 0.0, 1.42), 85, (-0.5, -1.05, 1.58), 2.0),
               (int(N * 0.35), (0.05, -1.68, 1.45), (0.0, 0.0, 1.42), 85, (-0.5, -1.0, 1.55), 2.0),
               (int(N * 0.6), (0.05, -1.65, 1.45), (0.0, 0.0, 1.42), 85, (0.0, -0.2, 1.45), 2.0),
               (N, (0.05, -1.6, 1.45), (0.0, 0.0, 1.42), 85, (0.0, -0.18, 1.45), 2.0)], mao=0.6)


# ====================================================================== 7. "eles tavam esperando eu virar uma daquelas coisas"
def canos_na_mao(G):
    for h in G:
        c = O("cano" + h.nome)
        if c is not None:
            pega(c, h, "F")


@acao("7A")
def a7A(N):
    """por cima do meu ombro: nove em arco com canos e tacos esperando; eu respiro fundo; eles apertam as armas, se inclinam em ondas, um dá um passo"""
    prepara("7A"); fogo_vivo(N)
    n = REG["eu"]
    mov_h(n, N, [(10, dict(olha=-18, cabeca=4)), (20, dict(olha=14)), (N, dict(olha=0))], vida=2.0, seed=2)
    G = grupo(); canos_na_mao(G)
    for j, h in enumerate(G):
        if h.nome == "g_jovem":
            continue
        P = dict(getattr(h, "_P", {}))
        arma = P.get("ombro", (0, 0))[0] <= -50
        d0 = 5 + 2 * (j % 5)
        if arma:
            mov_h(h, N, [(d0, dict(ombro=(-62, -62), tronco=4)), (d0 + 8, dict(ombro=(-78, -74), cotovelo=(-60, -60), tronco=10, ver=(0.0, -1.9))), (N, dict(tronco=14))],
                  seed=30 + j, vida=1.0)
        else:
            mov_h(h, N, [(d0, dict(tronco=4)), (N, dict(tronco=10, ver=(0.0, -1.9)))], seed=30 + j, vida=1.0)
    j = REG["jovem"]; x, y = j.raiz.location.x, j.raiz.location.y
    P = dict(getattr(j, "_P", {}))
    anda(j, N, (x, y, 0), (x - 0.12, y - 0.4, 0), f0=14, f1=24, ciclo=22, inclina=2, seed=7, arranque=0.1, freia=0.3, antes=dict(P), depois=dict(P, ombro=(-78, -74), tronco=12))
    camera(N, [(1, (0.35, -3.5, 0.8), (0.0, 0.3, 1.3), 22, (0.0, 0.2, 1.4), 2.8),
               (N // 2, (0.3, -3.35, 0.85), (0.0, 0.3, 1.3), 22, (0.0, 0.2, 1.4), 2.8),
               (N, (0.2, -3.2, 0.9), (0.0, 0.3, 1.3), 22, (0.0, 0.2, 1.4), 2.8)], mao=0.9)


@acao("7B")
def a7B(N):
    """macro em câmera lenta: duas mãos apertam o cano até os nós dos dedos; o cano estremece; o grupo borrado ao fundo se inclina"""
    prepara("7B"); fogo_vivo(N)
    ma, mb = MAOS["mA"], MAOS["mB"]; cano = O("cano")
    for f in range(1, N + 1):
        u = suave(faixa(f, 1, N * 0.7))
        mao_mix(ma, "segura", "fechada", u, f); mao_mix(mb, "segura", "fechada", u * 0.95, f)
    r0 = cano.rotation_euler.copy()
    for f in range(1, N + 1):
        tr = 0.6 * math.sin(f * 3.1) * faixa(f, 4, N)
        cano.rotation_euler = (r0.x, r0.y + math.radians(tr), r0.z); key(cano, "rotation_euler", f, "LINEAR")
    for j, h in enumerate(grupo()):
        mov_h(h, N, [(N, dict(tronco=12))], seed=40 + j, vida=1.0)
    ox, oy = -2.8, -1.4
    camera(N, [(1, (ox + 0.3, oy - 1.5, 1.3), (ox, oy - 0.1, 0.95), 50, (ox, oy - 0.3, 1.0), 2.8),
               (N, (ox + 0.22, oy - 1.3, 1.2), (ox, oy - 0.1, 0.95), 50, (ox, oy - 0.3, 1.0), 2.8)], mao=0.5)


@acao("7C")
def a7C(N):
    """a mulher abre o meu olho com o polegar: o braço sobe até a minha cara, o olho abre a contragosto, a lanterna acima; solta e eu me encolho"""
    prepara("7C"); fogo_vivo(N)
    n = REG["eu"]; rd = REG["radio"]; lan = O("lant")
    pega(lan, rd, "B")
    olho = Vector((0.07, -0.19, 1.55))
    p_ate = mira_mao(rd, "F", (olho.x - 0.02, olho.y - 0.07, olho.z - 0.01), base=getattr(rd, "_P", {}))
    mov_h(rd, N, [(6, dict(tronco=10)), (13, dict(ombro=p_ate["ombro"], cotovelo=p_ate["cotovelo"], abre=p_ate["abre"], tronco=12)),
                  (21, dict(ombro=p_ate["ombro"], cotovelo=p_ate["cotovelo"], abre=p_ate["abre"], tronco=12)),
                  (N, dict(ombro=(-82, 4), cotovelo=(-62, -12), tronco=6))], seed=9, vida=0.6)
    cara(n, N, [(1, dict(boca="o", lid=1.15)), (13, dict(boca="o", lid=1.1)), (15, dict(boca="triste", lid=0.1, brow=0.8, olhos=1.15)),
                (22, dict(boca="triste", lid=0.1, brow=0.8, olhos=1.15)), (N, dict(boca="o", lid=0.7, brow=-0.3))], piscar=False)
    mov_h(n, N, [(13, dict(cabeca=0)), (16, dict(cabeca=-9, olha=-8)), (24, dict(cabeca=-9)), (N, dict(cabeca=2, olha=0))], vida=1.0, seed=3)
    camera(N, [(1, (0.9, -1.0, 1.5), (-0.15, -0.2, 1.5), 50, (0.0, -0.19, 1.5), 2.0),
               (14, (0.82, -0.95, 1.5), (-0.12, -0.2, 1.5), 50, (0.05, -0.19, 1.55), 2.0),
               (N, (0.7, -0.85, 1.52), (-0.1, -0.2, 1.52), 50, (0.06, -0.19, 1.55), 2.0)], mao=0.7)


@acao("7D")
def a7D(N):
    """extremo close do olho: a pálpebra abre, o olho branco e a borda de luz acesa; o facho da lanterna passa por cima e o olho encolhe, firme, sem desviar"""
    prepara("7D"); fogo_vivo(N)
    n = REG["eu"]; lan = O("lant")
    cara(n, N, [(1, dict(boca="reta", lid=0.55)), (8, dict(boca="reta", lid=0.0, brow=0.3, olhos=1.05)), (N, dict(boca="reta", lid=0.0, brow=0.1, olhos=1.0))], piscar=True)
    for f in range(1, N + 1):
        u = faixa(f, 1, N); lan.rotation_euler.z = math.radians(150 - 70 * suave(u)); key(lan, "rotation_euler", f, "LINEAR")
        lan.location = (0.45 - 0.5 * u, -0.6 + 0.03 * u, 1.62); key(lan, "location", f, "LINEAR")
    camera(N, [(1, (0.0, -0.78, 1.5), (-0.07, 0.0, 1.5), 85, (-0.07, -0.19, 1.5), 1.8),
               (N, (0.0, -0.6, 1.5), (-0.07, 0.0, 1.5), 85, (-0.07, -0.19, 1.5), 1.8)], mao=0.4)


@acao("7E")
def a7E(N):
    """através do fogo: os cinco do grupo atrás das chamas se olham, trocam um aceno e um vira para o outro; o fogo estala"""
    prepara("7E"); fogo_vivo(N)
    ordem = (("lider", (-1.1, 1.9), 4), ("radio", (0.0, 2.2), 10), ("cochicho", (-0.65, 1.3), 16), ("taco", (1.1, 1.9), 22), ("jovem", (0.0, 2.2), 8))
    for nome, alvo, d0 in ordem:
        if nome in REG:
            mov_h(REG[nome], N, [(min(N - 2, d0), dict(ver=alvo, cabeca=-6)), (min(N - 1, d0 + 8), dict(tronco=6, ver=alvo)), (N, dict(tronco=2))], seed=sum(map(ord, nome)) % 60, vida=1.2)
    camera(N, [(1, (0.25, -1.1, 1.85), (0.0, 2.0, 1.3), 35, (0.0, 1.9, 1.5), 2.0),
               (N, (0.05, -0.9, 1.8), (0.0, 2.0, 1.3), 35, (0.0, 1.9, 1.5), 2.0)], mao=0.8)


@acao("7F")
def a7F(N):
    """perfil duplo: o velho cochicha no ouvido do homem do taco, que escuta de cabeça baixa e levanta os olhos para mim no fim; o líder e o careca olham"""
    prepara("7F"); fogo_vivo(N)
    a = REG["cochicho"]; b = REG["taco"]
    mov_h(a, N, [(8, dict(tronco=22, cabeca=12)), (N - 6, dict(tronco=26, cabeca=14)), (N, dict(tronco=14, cabeca=6))], seed=4, vida=1.0)
    cara(a, N, [(1, dict(boca="o", lid=0.4)), (10, dict(boca="reta", lid=0.4)), (16, dict(boca="o", lid=0.4)), (24, dict(boca="reta", lid=0.4))], piscar=False)
    mov_h(b, N, [(6, dict(cabeca=14, tronco=4)), (N - 8, dict(cabeca=10)), (N, dict(cabeca=-4, ver=(0.0, -0.9)))], seed=5, vida=1.0)
    cara(b, N, [(1, dict(boca="reta", lid=0.55)), (N - 8, dict(boca="reta", lid=0.55)), (N, dict(boca="reta", lid=0.15, brow=0.4))], piscar=True)
    for nome in ("lider", "careca"):
        mov_h(REG[nome], N, [(8, dict(ver=(1.3, 0.7))), (N, dict(ver=(0.0, -0.9)))], seed=sum(map(ord, nome)) % 30, vida=1.0)
    camera(N, [(1, (1.5, -1.0, 1.55), (1.5, 0.7, 1.55), 50, (1.5, 0.7, 1.56), 2.0),
               (N, (1.52, -0.7, 1.56), (1.5, 0.7, 1.55), 50, (1.55, 0.7, 1.56), 2.0)], mao=0.6)


@acao("7G")
def a7G(N):
    """pan por uma fila de rostos: sete viram a cabeça para a câmera, um depois do outro em onda, acompanhando o pan"""
    prepara("7G"); fogo_vivo(N)
    ordem = ("lider", "radio", "cochicho", "taco", "jovem", "careca", "solto")
    for k, nome in enumerate(ordem):
        h = REG[nome]; x = h.raiz.location.x
        t = 1 + int((x + 3.0) / 6.0 * (N - 8))
        mov_h(h, N, [(max(2, t - 3), dict(ver=(x, 6.0))), (min(N - 1, t + 4), dict(ver=(0.0, -0.8), cabeca=-3)), (N, dict(tronco=4))], seed=50 + k, vida=1.0)
        cara(h, N, [(1, dict(boca="reta", lid=0.5)), (min(N, t + 4), dict(boca="reta", lid=0.0, brow=0.3))], piscar=False)
    camera(N, [(1, (0.0, -0.8, 1.45), (-1.8, 1.7, 1.55), 28, (-2.0, 1.7, 1.55), 4.0),
               (N // 2, (0.0, -0.8, 1.45), (0.0, 1.7, 1.55), 28, (0.0, 1.7, 1.55), 4.0),
               (N, (0.0, -0.8, 1.45), (1.8, 1.7, 1.55), 28, (2.0, 1.7, 1.55), 4.0)], mao=0.6)


@acao("7H")
def a7H(N):
    """macro 3/4 das mãos: a mão da mulher entrega o pano cinza e a minha, de manga vermelha, recebe e aperta"""
    prepara("7H"); fogo_vivo(N)
    mR, mE = MAOS["mR"], MAOS["mE"]; pano = O("pano")
    pR, pE = O("mR_piv"), O("mE_piv")
    ox, oy = -1.6, -0.2
    pR0, pE0 = Vector(pR.location), Vector(pE.location); pn0 = Vector(pano.location)
    for f in range(1, N + 1):
        u = suave(faixa(f, 3, N * 0.55)); v = suave(faixa(f, N * 0.4, N * 0.9))
        pR.location = pR0 + Vector((0.0, -0.05 * u + 0.03 * v, 0.0)); key(pR, "location", f, "LINEAR")
        pE.location = pE0 + Vector((0.0, 0.03 * u + 0.02 * v, 0.07 * u)); key(pE, "location", f, "LINEAR")
        mao_mix(mR, "segura", "aberta", v, f); mao_mix(mE, "aberta", "fechada", suave(faixa(f, N * 0.5, N)), f)
        pano.location = pn0 + Vector((0.0, 0.02 * u - 0.01 * v, 0.05 * u * (1 - v) - 0.04 * v)); key(pano, "location", f, "LINEAR")
    camera(N, [(1, (ox + 0.7, oy - 0.6, 1.4), (ox, oy, 1.08), 35, (ox, oy, 1.1), 2.8),
               (N, (ox + 0.55, oy - 0.45, 1.28), (ox, oy, 1.08), 35, (ox, oy, 1.1), 2.8)], mao=0.5)
