"""Animação de verdade das sequências 8 a 12 da parte 2 (Cadê a Rita; o líder conta o ar e a gosma; os esqueletos; os Sem-Osso; os ossos na porta). Ver acoes_abrigo2b.py."""
import math, random
import bpy
from mathutils import Vector
from lib import key
from acoes_abrigo2b import REG, MAOS, CAMS, POV, O, prepara, estado, mov_h, cara, pega, anda, trilha, visivel, mao_mix, rota, cam_ab, semi, grupo, fogo_vivo, mira_mao
from acoes_abrigo2b import pov_para, centra, vento, poeira_cai, figurante, gosma_dedos
from acoes_abrigo2 import camera, sem_osso_vivo, boca_abre, suave, faixa, costas, pos_cabeca, acao, lerp, FPS, BY
import story_abrigo2 as S
import story3_abrigo as S3
import objetos3d_abrigo as O3, objetos3d_abrigo2 as O2, ambiente_noite as AN
import cena


# ====================================================================== 8. "Cadê a Rita? Cadê o Zé? Ninguém ali sabia."
@acao("8A")
def a8A(N):
    """sento de um pulo: o chão, o teto, e o olhar varre o círculo (esquerda e depois direita); as mãos de primeira pessoa empurram o chão; o círculo recua um passo"""
    prepara("8A"); fogo_vivo(N)
    G = grupo()
    for j, h in enumerate(G):
        mov_h(h, N, [(5 + j % 4, dict(tronco=-6, cabeca=-4, ombro=(-14, 14))), (N, dict(tronco=-2, cabeca=0))], seed=60 + j, vida=1.0)
    Fs = max(8, int(N * 0.42))
    c = camera(N, [(1, (0.0, -0.9, 0.22), (0.0, 0.6, 2.0), 28, (0.0, 1.2, 1.5), 4.0),
                   (Fs, (0.0, -0.93, 0.78), (0.0, 1.2, 1.3), 28, (0.0, 1.5, 1.3), 4.0),
                   (Fs + 6, (0.0, -0.95, 1.0), (-1.7, 1.0, 1.3), 28, (-1.8, 1.3, 1.3), 4.0, -2.0),
                   (N, (0.0, -0.95, 1.0), (1.6, 1.1, 1.3), 28, (1.7, 1.3, 1.3), 4.0, 2.0)], mao=1.2)
    pov_para(c)
    r, me, md = POV[0]
    for f in range(1, N + 1):
        u = suave(faixa(f, 1, Fs)); v = faixa(f, Fs, N)
        me.raiz.location = (-0.17, 0.62 - 0.1 * u, -0.26 - 0.3 * u - 0.05 * v); key(me.raiz, "location", f, "LINEAR")
        md.raiz.location = (0.17, 0.40 - 0.1 * u, -0.19 - 0.3 * u - 0.05 * v); key(md.raiz, "location", f, "LINEAR")
        mao_mix(me, "aberta", "relaxada", v, f); mao_mix(md, "aberta", "relaxada", v, f)


@acao("8B")
def a8B(N):
    """câmera baixa: um casaco verde de costas, parado; a câmera chega perto; ele ouve, vira a cabeça e depois o corpo, e não é o Zé; os outros olham"""
    prepara("8B"); fogo_vivo(N)
    z = REG["zeverde"]
    mov_h(z, N, [(7, dict()), (12, dict(rot=140, ver=(0.2, -0.9))), (18, dict(rot=40, olha=0)), (N, dict(rot=25, tronco=2))], seed=3, vida=1.0)
    cara(z, N, [(1, dict(boca="reta", lid=0.35)), (14, dict(boca="reta", lid=0.35)), (20, dict(boca="triste", lid=0.2, brow=0.4))], piscar=True)
    for nome in ("lider", "radio", "cochicho", "careca"):
        mov_h(REG[nome], N, [(6, dict(ver=(1.6, 0.9))), (N, dict(ver=(0.3, -0.9)))], seed=sum(map(ord, nome)) % 30, vida=1.0)
    camera(N, [(1, (0.2, -0.9, 1.45), (1.6, 0.9, 1.4), 35, (1.7, 0.9, 1.4), 4.0),
               (12, (0.3, -0.85, 1.45), (1.6, 0.9, 1.4), 35, (1.7, 0.9, 1.4), 4.0),
               (N, (0.55, -0.75, 1.45), (1.6, 0.9, 1.4), 35, (1.7, 0.9, 1.55), 4.0)], mao=0.9)


@acao("8C")
def a8C(N):
    """duas cabeças de pano balançando que não, em contratempo; atrás, um terceiro baixa os olhos"""
    prepara("8C"); fogo_vivo(N)
    a, b = REG["trancas"], REG["solto"]
    ka = [(2 + 2 * k, dict(olha=(20 if k % 2 == 0 else -20))) for k in range(max(2, N // 2))]
    kb = [(2 + 2 * k, dict(olha=(-20 if k % 2 == 0 else 20))) for k in range(max(2, N // 2))]
    mov_h(a, N, ka, seed=2, vida=0.5, molas=dict(olha=(0, 7.0, 0.7)))
    mov_h(b, N, kb, seed=3, vida=0.5, molas=dict(olha=(0, 7.0, 0.7)))
    for nome in ("jovem", "careca"):
        mov_h(REG[nome], N, [(4, dict(cabeca=14)), (N, dict(cabeca=22, tronco=8))], seed=9, vida=1.0)
    camera(N, [(1, (-2.0, -1.7, 1.58), (-2.0, 1.0, 1.58), 85, (-2.0, 1.05, 1.62), 2.0),
               (N, (-2.0, -1.5, 1.58), (-2.0, 1.0, 1.58), 85, (-2.0, 1.05, 1.62), 2.0)], mao=0.5)


@acao("8D")
def a8D(N):
    """dolly atrás de mim, sentado: o líder sai do fundo, atravessa o corredor de gente (que vira a cabeça atrás dele) e vem até mim; eu viro devagar"""
    prepara("8D"); fogo_vivo(N)
    n = REG["eu"]; L = REG["lider"]
    mov_h(n, N, [(10, dict(olha=-12, cabeca=4)), (N, dict(olha=6, cabeca=2))], vida=1.8, seed=2)
    x, y = L.raiz.location.x, L.raiz.location.y
    P = dict(getattr(L, "_P", {}))
    anda(L, N, (x, y, 0), (0.5, -0.35, 0), f0=3, f1=N - 3, ciclo=20, inclina=2, seed=4, arranque=0.12, freia=0.35, antes=dict(P), depois=dict(P))
    for k, nome in enumerate(("radio", "cochicho", "jovem", "taco")):
        h = REG[nome]; t = 6 + 4 * k
        mov_h(h, N, [(t, dict(ver=(0.8, 1.0))), (t + 8, dict(ver=(0.5, 0.1), tronco=4)), (N, dict(ver=(0.5, -0.2)))], seed=70 + k, vida=1.0)
    camera(N, [(1, (0.05, -3.0, 0.95), (0.3, 0.8, 1.35), 35, (0.8, 1.4, 1.5), 2.8),
               (N // 2, (0.05, -2.95, 0.92), (0.35, 0.3, 1.38), 35, (0.7, 0.7, 1.5), 2.8),
               (N, (0.05, -2.9, 0.9), (0.4, -0.2, 1.4), 35, (0.5, -0.35, 1.5), 2.8)], mao=0.9)


# ====================================================================== 9. o líder conta: o ar, a gosma
@acao("9A")
def a9A(N):
    """por cima do meu ombro, através do fogo: o líder olha a caneca, levanta os olhos para mim devagar e começa a falar; o fogo treme no rosto dele"""
    prepara("9A"); fogo_vivo(N)
    L = REG["lider"]; caneca = O("caneca")
    pega(caneca, L, "F")
    mov_h(L, N, [(8, dict(cabeca=20, tronco=4)), (20, dict(cabeca=-2, tronco=0, ombro=(-54, -54))), (N, dict(cabeca=-4, tronco=-2, ombro=(-58, -58)))], seed=3, vida=1.0)
    cara(L, N, [(1, dict(boca="triste", lid=0.6)), (16, dict(boca="triste", lid=0.35)), (20, dict(boca="o", lid=0.3)), (24, dict(boca="reta", lid=0.3)),
                (28, dict(boca="o", lid=0.3)), (32, dict(boca="reta", lid=0.3))], piscar=True)
    n = REG["eu"]
    mov_h(n, N, [(N, dict(olha=-4, cabeca=3))], vida=1.8, seed=2)
    camera(N, [(1, (-0.7, -1.95, 1.0), (0.1, 1.9, 1.5), 85, (0.0, 0.5, 1.2), 2.0),
               (14, (-0.66, -1.85, 1.02), (0.1, 1.9, 1.5), 85, (0.0, 0.8, 1.2), 2.0),
               (22, (-0.62, -1.75, 1.04), (0.1, 1.9, 1.5), 85, (0.0, 1.9, 1.55), 2.0),
               (N, (-0.55, -1.6, 1.05), (0.1, 1.9, 1.5), 85, (0.0, 1.9, 1.55), 2.0)], mao=0.6)


@acao("9B")
def a9B(N):
    """flashback, rua morta de céu branco: os vizinhos olham o alto, depois cobrem a boca e o nariz e recuam, um tosse; a câmera sobe com a poeira e a nuvem ao longe"""
    prepara("9B")
    for k, h in enumerate(REG.values()):
        if not h.nome.startswith("v"):
            continue
        t = 6 + 4 * k
        mov_h(h, N, [(t, dict(cabeca=-24, tronco=-8)), (t + 8, dict(cabeca=-8, tronco=6, ombro=(-132, -90), cotovelo=(-70, -60))), (N, dict(tronco=14, cabeca=6, dpos=(0, 0.25, 0)))],
              seed=80 + k, vida=1.2)
        cara(h, N, [(1, dict(boca="o", lid=0.0)), (t + 8, dict(boca="triste", lid=0.4, brow=0.6))], piscar=False)
    vento(N, n=10, de=(-4.0, BY - 12.0, 0.4), ate=(4.0, BY - 6.0, 2.5), caixa=(3.0, 3.0, 2.5), seed=3, tam=0.06, cor="#f4f1e6", prefixo="cinza")
    cam_ab(N, mao=1.0)


@acao("9C")
def a9C(N):
    """a padeira contra a porta, o óleo brilha nela: ela escorrega devagar pela porta, o corpo amolece e pinga; a câmera aproxima"""
    prepara("9C")
    so = REG["so"]
    ch = []
    for f in range(1, N + 1, 2):
        u = faixa(f, 1, N)
        ch.append((f, dict(pos=(0.0, BY - 0.9 + 0.02 * u, -0.05 * suave(u)), rot=0, tronco=8 + 22 * suave(u), cabeca=-6 - 12 * suave(u), alt=0.78 - 0.12 * suave(u),
                           ombro=(-60 + 25 * u, -60 + 25 * u), cotovelo=(-30, -30), quadril=(-4 * u, 4 * u), joelho=(12 + 24 * u, 12 + 24 * u))))
    sem_osso_vivo(so, N, ch, estica=lambda f: 1.0 - 0.18 * suave(faixa(f, 1, N)), base_pulso=lambda f: 0.8 * suave(faixa(f, 4, N)),
                  dobra=lambda f: [14 + 30 * faixa(f, 1, N), -14 - 30 * faixa(f, 1, N), 10, -10])
    boca_abre(so, N, [(1, 1.0), (N, 1.7)])
    cam_ab(N, mao=0.6)


@acao("9D")
def a9D(N):
    """macro: a mão aberta treme; as pontas dos dedos incham em gosma e começam a pingar, cada pingo no seu ritmo"""
    prepara("9D")
    mao = O("mao_piv"); m = MAOS["mao"]
    p0 = Vector(mao.location)
    for f in range(1, N + 1):
        tr = 0.004 * math.sin(f * 2.1) * faixa(f, 3, N)
        mao.location = (p0.x + tr, p0.y, p0.z + 0.5 * tr); key(mao, "location", f, "LINEAR")
        mao_mix(m, "aberta", "relaxada", faixa(f, 4, N) * 0.5, f)
    gosma_dedos("", N, 0.0, 1.0, n=5, cai=0.1)
    pal = O("palma"); centra(pal)
    trilha(pal, N, esc=[(1, (1.0, 1.0, 1.0)), (N, (1.5, 1.2, 2.2))])
    cam_ab(N, mao=0.5)


@acao("9E")
def a9E(N):
    """rente à soleira: o avental cai no chão e a poça preta cresce debaixo dele; o avental afunda e se amassa"""
    prepara("9E")
    pc = O("p"); av = O("av")
    trilha(pc, N, esc=[(1, (1.0, 1.0, 1.0)), (int(N * 0.5), (1.5, 1.5, 1.0)), (N, (2.1, 2.1, 1.0))])
    trilha(av, N, loc=[(1, (0.2, BY - 0.8, 0.08)), (int(N * 0.5), (0.17, BY - 0.8, 0.06)), (N, (0.1, BY - 0.8, 0.04))],
           rot=[(1, (0, 0, 14)), (N, (4, -3, 25))], esc=[(1, (1, 1, 1)), (N, (1.0, 0.9, 0.6))])
    vento(N, n=5, de=(-1.0, BY - 1.8, 0.1), ate=(1.5, BY - 1.4, 0.4), caixa=(1.0, 0.5, 0.1), seed=4, tam=0.05, cor="#f4f1e6", prefixo="cinza")
    cam_ab(N, mao=0.6)


# ====================================================================== 10. os esqueletos
@acao("10A")
def a10A(N):
    """a gosma sai do avental e escorre pelo chão deixando um rastro; a câmera segue, baixa; ela vai em ondas (acelera, para, acelera)"""
    prepara("10A")
    g = O("g")
    for f in range(1, N + 1):
        u = faixa(f, 1, N); s = 0.7 * u + 0.3 * suave(u); onda = 0.03 * math.sin(f * 0.9)
        g.location = (1.6 * s, -0.75 * s + onda, 0.0); key(g, "location", f, "LINEAR")
    cam_ab(N, mao=0.8)


@acao("10B")
def a10B(N):
    """dolly-in no esqueleto sentado contra o pilar: a poeira cai, a cabeça tomba um pouco e a mandíbula cai; o foco passa do avental para o crânio"""
    prepara("10B")
    cab = O("esq_a_cab"); mand = O("esq_a_mand")
    r0 = Vector(cab.rotation_euler); m0 = Vector(mand.rotation_euler)
    for f in range(1, N + 1):
        u = suave(faixa(f, 8, N - 4))
        cab.rotation_euler = (r0.x + math.radians(8 * u), r0.y + math.radians(5 * u), r0.z); key(cab, "rotation_euler", f, "LINEAR")
        mand.rotation_euler = (m0.x + math.radians(14 * u), m0.y, m0.z); key(mand, "rotation_euler", f, "LINEAR")
    poeira_cai(N, x=(-0.3, 0.3), y=(BY - 0.8, BY - 0.4), z=(0.0, 1.4), n=12, seed=5, vel=0.15)
    camera(N, [(1, (1.8, BY - 3.6, 1.15), (0.1, BY - 0.6, 0.6), 50, (-0.2, BY - 0.9, 0.04), 4.0),
               (int(N * 0.5), (1.4, BY - 2.9, 0.98), (0.05, BY - 0.6, 0.65), 50, (0.0, BY - 0.6, 0.6), 4.0),
               (N, (0.9, BY - 2.2, 0.8), (0.0, BY - 0.6, 0.68), 50, (0.0, BY - 0.6, 0.7), 4.0)], mao=0.7)


@acao("10C")
def a10C(N):
    """grua descendo sobre a rua cheia de ossos: o vento arrasta a cinza e uns papéis de um lado a outro; a câmera gira devagar"""
    prepara("10C")
    vento(N, n=14, de=(-6.0, 5.0, 0.2), ate=(6.0, 9.0, 1.2), caixa=(5.0, 5.0, 0.6), seed=6, tam=0.25)
    cam_ab(N, mao=0.5)


@acao("10D")
def a10D(N):
    """travelling lateral baixo: passam os esqueletos sentados nos degraus e deitados na calçada; o vento levanta cinza entre eles"""
    prepara("10D")
    vento(N, n=8, de=(-4.0, 3.0, 0.1), ate=(4.0, 4.0, 0.5), caixa=(3.0, 2.0, 0.4), seed=8, tam=0.1, cor="#cfc9b0")
    cab = O("esq_s_cab")
    if cab is not None:
        r0 = Vector(cab.rotation_euler)
        for f in range(1, N + 1):
            cab.rotation_euler = (r0.x + math.radians(2.5 * math.sin(f * 0.4)), r0.y, r0.z); key(cab, "rotation_euler", f, "LINEAR")
    cam_ab(N, mao=0.8, warp=1.0, mix=1.0, nk=4)


@acao("10E")
def a10E(N):
    """macro: um crânio na cinza e o facho da lanterna varre sobre ele; a luz passa, a sombra das órbitas anda; a cinza assenta"""
    prepara("10E")
    lan = O("lant")
    for f in range(1, N + 1):
        u = suave(faixa(f, 1, N)); lan.rotation_euler.z = math.radians(15 + 70 * u); key(lan, "rotation_euler", f, "LINEAR")
        lan.location = (1.5 - 0.5 * u, 4.7 + 0.2 * u, 0.55 + 0.03 * math.sin(f * 0.6)); key(lan, "location", f, "LINEAR")
    poeira_cai(N, x=(-0.3, 0.3), y=(5.8, 6.2), z=(0.1, 0.7), n=14, seed=2, vel=0.1)
    cam_ab(N, mao=0.5)


# ====================================================================== 11. os Sem-Osso
@acao("11A")
def a11A(N):
    """o líder fala, o fogo treme no rosto: balança a cabeça, olha para baixo e para mim, fecha os olhos por um instante; os de trás escutam"""
    prepara("11A"); fogo_vivo(N)
    L = REG["lider"]
    mov_h(L, N, [(6, dict(cabeca=10)), (14, dict(cabeca=-4, tronco=2)), (22, dict(cabeca=6)), (N, dict(cabeca=0))], seed=3, vida=1.0)
    cara(L, N, [(1, dict(boca="reta", lid=0.55)), (4, dict(boca="o", lid=0.5)), (8, dict(boca="reta", lid=0.5)), (12, dict(boca="o", lid=0.4)), (16, dict(boca="reta", lid=0.4)),
                (20, dict(boca="o", lid=0.5)), (N, dict(boca="reta", lid=0.7))], piscar=True)
    for nome in ("radio", "taco"):
        mov_h(REG[nome], N, [(8, dict(cabeca=12)), (N, dict(cabeca=18, tronco=6))], seed=sum(map(ord, nome)) % 30, vida=1.0)
    cam_ab(N, mao=0.5)


@acao("11B")
def a11B(N):
    """meus olhos arregalados: o choque (a cabeça recua), a respiração curta, a câmera inclina cada vez mais"""
    prepara("11B"); fogo_vivo(N)
    n = REG["eu"]
    cara(n, N, [(1, dict(boca="o", lid=0.0, olhos=1.0)), (6, dict(boca="o", lid=0.0, brow=0.9, olhos=1.22)), (N, dict(boca="triste", lid=0.0, brow=0.9, olhos=1.25))], piscar=False)
    mov_h(n, N, [(4, dict(cabeca=-8)), (14, dict(cabeca=-4)), (N, dict(cabeca=-6, olha=5))], seed=2, vida=2.4)
    camera(N, [(1, (0.0, -1.6, 1.56), (0.0, -0.8, 1.56), 85, (0.0, -1.0, 1.56), 2.0, -6.0),
               (N, (0.0, -1.4, 1.56), (0.0, -0.8, 1.56), 85, (0.0, -1.0, 1.56), 2.0, -11.0)], mao=0.7)


@acao("11C")
def a11C(N):
    """sob o poste que pisca, as três poças escorrem uma para a outra e se juntam; a do meio incha quando as outras chegam"""
    prepara("11C")
    p1, p2, p3, m2 = O("p1"), O("p2"), O("p3"), O("m2")
    centra(p2); centra(p3)
    l1 = Vector(p1.location); l2 = Vector(p2.location); l3 = Vector(p3.location)
    for f in range(1, N + 1):
        u = faixa(f, 1, N * 0.85); e = u * u * (3 - 2 * u); w = 0.02 * math.sin(f * 0.8)
        p1.location = (l1.x + 1.7 * e, l1.y + w, l1.z); key(p1, "location", f, "LINEAR")
        p3.location = (l3.x - 1.3 * e, l3.y - w, l3.z); key(p3, "location", f, "LINEAR")
    trilha(p2, N, esc=[(1, (1.0, 1.0, 1.0)), (int(N * 0.6), (1.1, 1.1, 1.2)), (N, (1.7, 1.5, 2.4))])
    lamp = O("pz11_l")
    if lamp is not None:
        visivel(lamp, N, lambda f: (f % 7) not in (3, 4) and (f % 11) != 8)
        h = O("pz11_halo")
        if h is not None:
            visivel(h, N, lambda f: (f % 7) not in (3, 4) and (f % 11) != 8)
    cam_ab(N, mao=0.8)


@acao("11D")
def a11D(N):
    """a gosma sobe numa coluna e vira um corpo curvado que se ergue, esticado e fino, assenta com um balanço; a coluna afunda enquanto ele sobe"""
    prepara("11D")
    so = REG["so"]; p3 = O("p3")
    FS = N - 4
    ch = []
    for f in range(1, N + 1, 2):
        u = faixa(f, 1, FS)
        ch.append((f, dict(pos=(1.5 - 0.1 * u, 7.2, -1.1 + 1.1 * costas(u)), rot=-100 + 10 * u, tronco=34 - 16 * suave(u), cabeca=-32 + 24 * u, alt=0.76,
                           ombro=(-8 - 24 * u, -6 - 22 * u), cotovelo=(-12, -16), abre=(8 * u, 8 * u))))
    sem_osso_vivo(so, N, ch, estica=lambda f: 1.0 + 0.45 * math.sin(math.pi * min(1, faixa(f, 1, FS) * 1.1)) * (1 - 0.4 * faixa(f, 1, FS)),
                  dobra=lambda f: [60 * (1 - faixa(f, 1, N)) * math.sin(f / 2.0), -60 * (1 - faixa(f, 1, N)) * math.sin(f / 2.3 + 1), 30 * (1 - faixa(f, 1, N)), -30 * (1 - faixa(f, 1, N))])
    boca_abre(so, N, [(1, 0.8), (N, 1.6)])
    if p3 is not None:
        for f in range(1, N + 1):
            p3.location = (0.0, 0.0, -1.2 * suave(faixa(f, 4, FS))); key(p3, "location", f, "LINEAR")
    camera(N, [(1, (-0.9, 5.0, 0.3), (0.6, 7.0, 0.8), 35, (0.8, 7.0, 0.5), 4.0),
               (int(N * 0.6), (-0.8, 5.1, 0.28), (0.8, 7.1, 1.1), 35, (1.2, 7.1, 1.0), 4.0),
               (N, (-0.7, 5.2, 0.25), (1.0, 7.2, 1.2), 35, (1.3, 7.2, 1.2), 4.0)], mao=0.8)


@acao("11E")
def a11E(N):
    """três Sem-Osso na rua com o poste ao fundo; o da frente, de avental, vem a trancos até a lente e os outros avançam mais devagar de cada lado"""
    prepara("11E")
    semi(REG["so"], N, (0.1, 5.6), (0.1, 3.5), per=15, fase=0.0, seed=3, rot=0)
    semi(REG["so1"], N, (-1.5, 8.5), (-1.3, 6.4), per=17, fase=0.3, seed=4, rot=-5)
    semi(REG["so2"], N, (1.3, 7.4), (1.2, 5.6), per=19, fase=0.6, seed=5, rot=5)
    camera(N, [(1, (0.2, 1.8, 1.0), (0.0, 5.6, 1.15), 35, (0.0, 5.6, 1.2), 2.8),
               (N, (0.2, 1.1, 1.0), (0.0, 4.4, 1.15), 35, (0.0, 3.5, 1.2), 2.8)], mao=0.9)


# ====================================================================== 12. os ossos na frente da nossa porta
@acao("12A")
def a12A(N):
    """aproximação no crânio do esqueleto do pilar: poeira cai, a mandíbula afrouxa e a cabeça tomba um pouco"""
    prepara("12A")
    cab = O("esq_a_cab"); mand = O("esq_a_mand")
    r0 = Vector(cab.rotation_euler); m0 = Vector(mand.rotation_euler)
    for f in range(1, N + 1):
        u = suave(faixa(f, 3, N))
        cab.rotation_euler = (r0.x + math.radians(7 * u), r0.y, r0.z); key(cab, "rotation_euler", f, "LINEAR")
        mand.rotation_euler = (m0.x + math.radians(12 * u), m0.y, m0.z); key(mand, "rotation_euler", f, "LINEAR")
    poeira_cai(N, x=(-0.2, 0.2), y=(BY - 0.7, BY - 0.4), z=(0.4, 1.4), n=10, seed=3, vel=0.1)
    cam_ab(N, mao=0.4)


@acao("12B")
def a12B(N):
    """travelling baixo até a porta de fora, os esqueletos na frente: a cinza voa ao nível do chão e um papel passa; a câmera avança entre os ossos"""
    prepara("12B")
    vento(N, n=8, de=(-3.0, BY - 5.0, 0.1), ate=(3.0, BY - 3.0, 0.5), caixa=(2.0, 1.5, 0.3), seed=7, tam=0.1)
    cam_ab(N, mao=0.8)


@acao("12C")
def a12C(N):
    """flashback, a padeira e o rapaz do mercado batem no aço com os dois punhos, em ritmo, gritando; os vizinhos atrás gesticulam; a câmera treme em cada golpe"""
    prepara("12C")
    quedas = []
    for nome, d0 in (("pad", 0), ("mer", 3)):
        h = REG[nome]
        ks = []
        for k in range(0, N, 6):
            ks.append((2 + k + d0, dict(ombro=(-122, -84), tronco=-8)))
            ks.append((5 + k + d0, dict(ombro=(-92, -108), tronco=4)))
        mov_h(h, N, ks, seed=3 + d0, vida=0.3, molas=dict(ombro=(0, 8.0, 0.7), tronco=(0, 6.0, 0.7)))
        cara(h, N, [(1, dict(boca="o", lid=0.0)), (N, dict(boca="o", lid=0.0))], piscar=False)
    for k, nome in enumerate(("vizA", "vizB", "vizC", "vizD")):
        h = REG.get(nome)
        if h is not None:
            mov_h(h, N, [(6 + 3 * k, dict(ombro=(-140, -90), tronco=-4)), (14 + 3 * k, dict(ombro=(-110, -140))), (N, dict(ombro=(-130, -100)))], seed=90 + k, vida=1.5)
    camera(N, [(1, (1.75, BY - 2.05, 1.5), (-0.2, BY - 0.15, 1.6), 24, (0.2, BY - 0.5, 1.5), 4.0, -2.0),
               (N, (1.15, BY - 1.5, 1.5), (-0.2, BY - 0.15, 1.6), 24, (0.2, BY - 0.5, 1.5), 4.0, -2.0)], mao=1.0, tranco=tuple(range(4, N, 6)))


@acao("12D")
def a12D(N):
    """pela janelinha redonda da porta: os rostos pedindo se apertam contra o vidro, a boca abre e fecha gritando; as mãos batem; o vidro embaça"""
    prepara("12D")
    for nome, h in list(REG.items()):
        ks = [(5, dict(tronco=-6)), (10, dict(tronco=2))]
        mov_h(h, N, ks, seed=sum(map(ord, nome)) % 70, vida=1.6)
        cara(h, N, [(1, dict(boca="o", lid=0.0, brow=0.6)), (5, dict(boca="reta", lid=0.0, brow=0.6)), (9, dict(boca="o", lid=0.0, brow=0.6)), (13, dict(boca="reta", lid=0.0, brow=0.6))],
             piscar=False)
    cam_ab(N, mao=0.8)


@acao("12E")
def a12E(N):
    """a Sem-Osso de avental com as mãos escorrendo na porta: as mãos sobem e descem arrastando, o corpo cai pesado de encontro ao aço"""
    prepara("12E")
    so = REG["so"]
    ch = []
    for f in range(1, N + 1, 2):
        u = faixa(f, 1, N); s = math.sin(f * 0.55)
        ch.append((f, dict(pos=(0.0, BY - 0.62 + 0.02 * s, 0), rot=180, tronco=20 + 10 * suave(u), cabeca=-10 + 6 * s, alt=0.76,
                           ombro=(-150 + 70 * u + 10 * s, -140 + 60 * u - 10 * s), cotovelo=(-20, -20), abre=(4, 4))))
    sem_osso_vivo(so, N, ch, base_pulso=lambda f: 0.5 + 0.4 * math.sin(f * 0.55), estica=lambda f: 1.0 - 0.1 * suave(faixa(f, 1, N)))
    boca_abre(so, N, [(1, 1.2), (N, 1.7)])
    cam_ab(N, mao=0.6)


@acao("12F")
def a12F(N):
    """eu, de frente, a ficha caindo: os olhos paradas, depois arregalam e baixam; a mão sobe devagar até a boca; o corpo cede"""
    prepara("12F"); fogo_vivo(N)
    n = REG["eu"]
    cara(n, N, [(1, dict(boca="triste", lid=0.3)), (8, dict(boca="triste", lid=0.1, brow=0.8, olhos=1.18)), (16, dict(boca="o", lid=0.25, brow=0.5)), (N, dict(boca="triste", lid=0.55, brow=0.2))], piscar=True)
    import ik3_abrigo as IK
    boca = IK.boca_de(n)
    pose = mira_mao(n, "F", (boca.x - 0.0, boca.y - 0.06, boca.z - 0.02), base=getattr(n, "_P", {}))
    mov_h(n, N, [(10, dict(cabeca=-4)), (17, dict(ombro=pose["ombro"], cotovelo=pose["cotovelo"], abre=pose["abre"], cabeca=2, tronco=4)),
                 (N, dict(ombro=pose["ombro"], cotovelo=pose["cotovelo"], abre=pose["abre"], cabeca=10, tronco=8))], vida=1.5, seed=2)
    camera(N, [(1, (0.0, -2.6, 1.5), (0.0, -0.8, 1.5), 50, (0.0, -1.0, 1.5), 2.0),
               (N, (0.0, -2.0, 1.5), (0.0, -0.8, 1.5), 50, (0.0, -1.0, 1.5), 2.0)], mao=0.5)
