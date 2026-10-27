"""Animação de "O abrigo" em cima do storyboard v3 (story3_abrigo.py): o cenário, a lente e o enquadramento de cada plano vêm de lá;
aqui entra o tempo. Regras em personagem/abrigo/regras-animacao.md (pedido de 25/10/2026: "seja um animador profissional: leve, fluido, muito smooth").
- todo boneco passa por Heroi3D.anima (curva cúbica + mola por junta + respiração); corrida com fase própria (ninguém corre em sincronia);
- objetos caem acelerando e quicam uma vez; o que é empurrado entra e sai em curva;
- a câmera nunca para: deriva lenta em velocidade constante (corta andando) + mão suavizada (senos lentos), desfoque de movimento ligado.
blender -b -P anim3_abrigo.py -- PLANO PASTA [--scale 0.5] [--samples 10] [--quadros 1,15,29]
Sem --quadros, renderiza o plano inteiro em PASTA/PLANO/0001.png ..."""
import os, sys, math, random, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy
from mathutils import Vector, Euler
import heroi3d, elenco3d_abrigo as E3, objetos3d_abrigo as O3

# ---------------------------------------------------------------- registro: quem foi criado no plano
REG, MAOS = {}, {}
_pose0 = heroi3d.Heroi3D.pose


def _pose_reg(self, **kw):
    self._ultima = dict(kw)
    return _pose0(self, **kw)


heroi3d.Heroi3D.pose = _pose_reg
_faz0 = E3.faz


def _faz_reg(chave, nome, *a, **k):
    h = _faz0(chave, nome, *a, **k)
    REG[nome[:-4] if nome.endswith("_inv") else nome] = h
    return h


E3.faz = _faz_reg
_mao0 = O3.Mao3D.__init__


def _mao_reg(self, nome, *a, **k):
    _mao0(self, nome, *a, **k); MAOS[nome] = self


O3.Mao3D.__init__ = _mao_reg

import story3_abrigo as ST
import ik3_abrigo as IK
import objetos3d_abrigo_b as O3B
from heroi3d import corrida
from lib import key, empty
from mathutils import Matrix
BY = ST.BY
FPS = 24
SIGMA = 0.85                                                      # suavização das curvas (quadros)


# ---------------------------------------------------------------- curvas
def lerp(a, b, u):
    return a + (b - a) * u


def suave(u):
    u = min(max(u, 0.0), 1.0); return u * u * (3 - 2 * u)


def suave5(u):
    u = min(max(u, 0.0), 1.0); return u ** 3 * (u * (6 * u - 15) + 10)


def entra(u, p=2.2):
    u = min(max(u, 0.0), 1.0); return u ** p


def faixa(f, fa, fb):
    return min(max((f - fa) / max(1e-6, fb - fa), 0.0), 1.0)


def mao_ruido(t, seed, amp=1.0):
    """balanço de mão de operador: soma de senos lentos (nunca aleatório quadro a quadro)"""
    r = random.Random(seed)
    return amp * sum(a * math.sin(2 * math.pi * fr * t + r.uniform(0, 6.28)) for fr, a in ((0.37, 0.55), (0.71, 0.3), (1.13, 0.15)))


def sombra(H):
    H.sombra = bpy.data.objects.get(H.nome[:-4] + "_sb") if H.nome.endswith("_inv") else None
    return H


# ---------------------------------------------------------------- bonecos
def parado(H, N, vida=1.0, seed=3, **troca):
    """mantém a pose do storyboard, mas viva (respira, o peso passa de um pé para o outro, o olhar passeia)"""
    P = dict(getattr(H, "_ultima", {})); P.update(troca)
    if "pos" not in P:
        P["pos"] = tuple(H.raiz.location)
    if "rot" not in P or abs(H.raiz.rotation_euler.x) > 1e-3 or abs(H.raiz.rotation_euler.y) > 1e-3:
        P["rot"] = tuple(math.degrees(v) for v in H.raiz.rotation_euler)     # o giro inteiro: quem está deitado continua deitado
    sombra(H).anima([(1, P), (N, P)], 1, N, vida=vida, seed=seed)


def corre(H, N, dy, fase=0, ciclo=12, inclina=13, v0=None, freia=0.0, arranque=0.0, dx=0.0, rot=None):
    """o boneco corre do lugar do storyboard (ou de v0) dy metros em y; fase = em que quadro do ciclo ele entra (ninguém corre em sincronia)"""
    P = getattr(H, "_ultima", {})
    x, y, z = v0 if v0 is not None else tuple(H.raiz.location)
    rot = P.get("rot", 180.0) if rot is None else rot
    por_q = dy / max(1, N - 1); por_qx = dx / max(1, N - 1)
    de = (x - por_qx * fase, y - por_q * fase, 0.0); ate = (x + dx, y + dy, 0.0)
    ch = corrida(1 - fase, N, de, ate, rot=rot, ciclo=ciclo, inclina=inclina, arranque=arranque, freia=freia)
    # quem já entra correndo não pode nascer parado: o lugar e o giro seguem o alvo quase sem mola (só as juntas têm mola)
    sombra(H).anima(ch, 1, N, vida=0.4, seed=int(abs(x * 7 + y * 3)) % 97, molas=dict(pos=(0, 24.0, 1.0), rot=(0, 24.0, 1.0)))


def corre_atrasados(N):
    """os vizinhos que não vão entrar: todos no mesmo ritmo (ST.ATRASO_V), cada um com a sua fase e o seu jeito de correr"""
    for ch, nm, x, dy, fase in ST.ATRASADOS:
        H = REG.get(nm)
        if H is not None:
            k = sum(map(ord, nm))
            corre(H, N, ST.ATRASO_V * N / FPS, fase=fase, ciclo=13 + k % 3, inclina=10 + k % 5)


def pedala(H, N, y0, v, rpm=70, extra=None, **pose):
    """quem conta pedalando: o pedivela gira a rpm, as pernas sobem e descem em oposição, o tronco balança com a pedalada"""
    ch = []
    for f in range(1, N + 1, 2):
        t = (f - 1) / FPS; th = 2 * math.pi * rpm / 60 * t
        sF, sB = math.sin(th), math.sin(th + math.pi)
        d = dict(pose)
        d.update(quadril=(-36 - 20 * sF, -36 - 20 * sB), joelho=(62 + 34 * sF, 62 + 34 * sB), tornozelo=(8 - 8 * math.cos(th), 8 + 8 * math.cos(th)),
                 tronco=pose.get("tronco", -12) - 1.2 * abs(sF), inclina=3.0 * sF, pos=(0.0, y0 + v * t - 0.27, 0.0), rot=180)
        if extra:
            d.update(extra(f))
        ch.append((f, d))
    sombra(H).anima(ch, 1, N, vida=0.5, mola=False)


# ---------------------------------------------------------------- objetos
def rodas(n, R=0.33):
    """separa cada roda da bicicleta num eixo próprio para ela girar (pneu, aro, raios e cubo)"""
    b = bpy.data.objects[n]; bpy.context.view_layer.update()
    hubs = []
    for k, x in enumerate((-0.5, 0.5)):
        h = empty(f"{n}_eixo{k}", b, (x, 0, R)); bpy.context.view_layer.update()
        for o in list(b.children):
            if o.name.startswith((f"{n}_pneu{k}", f"{n}_aro{k}", f"{n}_raio{k}_", f"{n}_cubo{k}")):
                mw = o.matrix_world.copy(); o.parent = h; o.matrix_world = mw
        hubs.append(h)
    return hubs


def gira_rodas(hubs, N, w0, w1=None, R=0.33):
    """w = rad/s no começo e no fim (perde velocidade aos poucos)"""
    w1 = w0 if w1 is None else w1
    for h in hubs:
        a = 0.0
        for f in range(1, N + 1):
            u = (f - 1) / max(1, N - 1); a += lerp(w0, w1, u) / FPS
            h.rotation_euler.y = a; key(h, "rotation_euler", f, "LINEAR")


def alfa(mat_nome, chaves):
    """transparência de um halo (cena.amat) em curva: chaves = [(quadro, alfa)]"""
    for m in [m for m in bpy.data.materials if m.name == mat_nome or m.name.startswith(mat_nome + ".")]:
        n = next(n for n in m.node_tree.nodes if n.type == "MATH" and n.operation == "MULTIPLY")
        for f, a in chaves:
            n.inputs[1].default_value = a; n.inputs[1].keyframe_insert("default_value", frame=f)


def exposicao(chaves):
    sc = bpy.context.scene
    for f, v in chaves:
        sc.view_settings.exposure = v; sc.keyframe_insert("view_settings.exposure", frame=f)


def mao_mix(m, a, b, u, f):
    """a mão passa de uma pose para outra (aberta, fechada, segura, pinca, relaxada) em curva"""
    A, B = O3.POSES[a], O3.POSES[b]
    m.pose(a, f=f, dedos=tuple(lerp(x, y, u) for x, y in zip(A["dedos"], B["dedos"])),
           polegar=tuple(lerp(x, y, u) for x, y in zip(A["polegar"], B["polegar"])), abre=lerp(A["abre"], B["abre"], u))


# ---------------------------------------------------------------- câmera
def camera_viva(N, vel=(0, 0, 0), frente=0.0, mao=1.0, centro=0.5, seed=1, extra=None):
    """a câmera do storyboard vira câmera de operador: anda em velocidade constante (vel em m/s no mundo, frente = m/s para onde olha),
    com o quadro do storyboard em 'centro' (fração do plano), e balança de mão suave (mao = 1 é 4 mm e 0,3°). extra(f) -> (dloc, drot em graus)"""
    c = bpy.context.scene.camera
    L0, R0 = c.location.copy(), c.rotation_euler.copy()
    fw = (R0.to_matrix() @ Vector((0, 0, -1))).normalized()
    for f in range(1, N + 1):
        t = (f - 1 - centro * (N - 1)) / FPS; tt = (f - 1) / FPS
        loc = L0 + Vector(vel) * t + fw * frente * t
        loc += Vector((mao_ruido(tt, seed, 0.004 * mao), mao_ruido(tt, seed + 1, 0.003 * mao), mao_ruido(tt, seed + 2, 0.004 * mao)))
        rot = Euler((R0.x + math.radians(mao_ruido(tt, seed + 3, 0.3 * mao)), R0.y + math.radians(mao_ruido(tt, seed + 4, 0.25 * mao)), R0.z + math.radians(mao_ruido(tt, seed + 5, 0.3 * mao))))
        if extra:
            dl, dr = extra(f)
            loc += Vector(dl); rot = Euler((rot.x + math.radians(dr[0]), rot.y + math.radians(dr[1]), rot.z + math.radians(dr[2])))
        c.location = loc; c.rotation_euler = rot
        key(c, "location", f, "LINEAR"); key(c, "rotation_euler", f, "LINEAR")


def soco(f, fs, m=0.006):
    """tranco curto de câmera na pancada: 2 quadros para lá, volta em onda"""
    d = 0.0
    for fi in fs:
        u = f - fi
        if 0 <= u < 8:
            d += m * math.exp(-u / 2.2) * math.cos(u * 1.4)
    return d


# ====================================================================== animação por plano
def a1A(N):
    by = 2.0; v = 3.4
    H = REG["eu"]; b = bpy.data.objects["bici"]
    hubs = rodas("bici")
    y_ini = by - v * (N - 1) / 2 / FPS                                # o quadro do storyboard fica no meio do plano
    for f in range(1, N + 1):
        b.location.y = y_ini + v * (f - 1) / FPS; key(b, "location", f, "LINEAR")
    # pedala e, no meio do plano, olha para trás por cima do ombro (para o cogumelo) e volta
    olhar = lambda f: dict(olha=-18 + 78 * math.sin(math.pi * faixa(f, 9, 27)) ** 2, giro=14 * math.sin(math.pi * faixa(f, 9, 27)) ** 2)
    pedala(H, N, y_ini, v, rpm=72, extra=olhar, ombro=(-50, -50), cotovelo=(-6, -6), abre=(12, 12), cabeca=-8, alt=0.93)
    gira_rodas(hubs, N, v / 0.33)
    corre_atrasados(N)
    for k in range(3):                                               # as ondas da sirene pulsam (cada uma no seu tempo)
        o = bpy.data.objects.get(f"onda_{k}")
        if o:
            for f in range(1, N + 1, 2):
                s_ = 1.0 + 0.12 * math.sin(2 * math.pi * (2.2 * (f - 1) / FPS) - k * 2.1); o.scale = (s_, s_, s_); key(o, "scale", f)
    camera_viva(N, vel=(0, v - 0.45, 0), mao=1.2, seed=11)            # recua junto, um pouco mais devagar: quem pedala se aproxima


def a1B(N):
    """freia, põe o pé no chão, pula para o lado e sai correndo; a bicicleta segue sozinha e começa a tombar"""
    by = 5.0; H = REG["eu"]; b = bpy.data.objects["bici"]; hubs = rodas("bici")
    ys, y, vv = [], by - 0.8, 3.0
    for f in range(1, N + 1):
        ys.append(y); y += vv / FPS; vv = max(0.5, vv - 0.16)
        b.location.y = ys[-1]
        tomb = -12 * suave(faixa(f, 6, 11)) - 30 * entra(faixa(f, 11, N), 2.0)
        b.rotation_euler = (math.radians(tomb), 0, math.radians(90)); key(b, "location", f, "LINEAR"); key(b, "rotation_euler", f, "LINEAR")
    gira_rodas(hubs, N, 3.0 / 0.33, 0.6 / 0.33)
    sent = dict(quadril=(-46, 14), joelho=(78, 30), tornozelo=(10, -6), ombro=(-50, -50), cotovelo=(-6, -6), abre=(12, 12), tronco=-12, cabeca=-6, alt=0.93, rot=180)
    yb = lambda f: ys[min(f, N) - 1]
    ch = [(1, dict(sent, pos=(0.0, yb(1) - 0.27, 0))),
          (4, dict(sent, pos=(0.0, yb(4) - 0.27, 0), tronco=-20, cabeca=-2)),                                     # freia: o corpo vai para a frente
          (8, dict(quadril=(-55, 6), joelho=(62, 14), tornozelo=(10, 0), ombro=(-44, 10), cotovelo=(-20, -30), abre=(14, 18), tronco=-14, alt=0.95,
                   rot=180, pos=(0.25, yb(8) - 0.18, 0))),                                                              # pé no chão, passa a perna
          (11, dict(quadril=(-30, 20), joelho=(40, 20), tornozelo=(10, 0), ombro=(-40, 20), cotovelo=(-30, -40), abre=(14, 20), tronco=-16, cabeca=-4,
                    alt=0.98, rot=180, pos=(0.45, yb(11) - 0.1, 0)))]
    x0, y0 = 0.45, yb(11) - 0.1
    ch += corrida(11, N + 4, (x0, y0, 0), (x0 + 0.1, y0 + 2.2, 0), rot=180, ciclo=12, inclina=14, arranque=0.6)[1:]
    sombra(H).anima(ch, 1, N, vida=0.4)
    corre_atrasados(N)
    camera_viva(N, mao=1.2, seed=17)


def a1C(N):
    b = bpy.data.objects["bici"]; hubs = rodas("bici")
    for f in range(1, N + 1):                                         # termina de tombar acelerando, bate, quica uma vez e assenta
        if f <= 6:
            a = lerp(-42, -62, entra(faixa(f, 1, 6), 1.6))
        else:
            u = f - 6; a = -62 + 6.0 * math.exp(-u / 2.5) * abs(math.sin(u * 0.95))
        b.rotation_euler = (math.radians(a), 0, math.radians(90)); key(b, "rotation_euler", f, "LINEAR")
    for k, h in enumerate(hubs):                                      # as rodas seguem girando e perdem força
        a = 0.0; w = (8.0 if k == 1 else 5.0)
        for f in range(1, N + 1):
            a += w / FPS; w *= 0.94
            h.rotation_euler.y = a; key(h, "rotation_euler", f, "LINEAR")
    eu = REG["eu"]; x, y, _ = eu.raiz.location
    corre(eu, N, 4.6 * N / FPS, fase=3, v0=(-0.6, y - 0.8, 0), dx=0.3)   # do lado livre da bicicleta, para as pernas aparecerem indo embora           # ele já saiu correndo: as pernas vão embora para o bunker
    for nm, fa in (("ze", 3), ("lu", 6)):
        corre(REG[nm], N, 4.2 * N / FPS, fase=fa)
    camera_viva(N, mao=0.8, seed=31, extra=lambda f: ((0, 0, soco(f, [6], 0.006)), (0, 0, 0)))


def a1D(N):
    v = 5.2
    for nm, fa, vv in (("ze", 3, 4.1), ("lu", 6, 4.0), ("rita", 2, 3.8)):
        corre(REG[nm], N, vv * N / FPS, fase=fa)
    # POV: a passada (2 passos a cada 12 quadros) sobe e desce a câmera e rola de leve; os punhos balançam em oposição
    def passo(f):
        th = 2 * math.pi * (f - 1) / 12
        return ((0.006 * math.sin(th), 0, 0.016 * abs(math.sin(th)) - 0.008), (1.2 * math.cos(2 * th) * 0.4, 1.1 * math.sin(th), 0))
    camera_viva(N, vel=(0, v, 0), mao=1.0, centro=0.0, seed=41, extra=passo)
    me, md = MAOS["maos_esq"], MAOS["maos_dir"]
    b_e, b_d = me.raiz.location.copy(), md.raiz.location.copy()
    for f in range(1, N + 1):
        th = 2 * math.pi * (f - 1) / 12
        for m, base, sg in ((me, b_e, 1), (md, b_d, -1)):
            s_ = sg * math.sin(th)
            m.raiz.location = (base.x - sg * 0.012 * s_, 0.53 + 0.09 * s_, -0.235 + 0.05 * s_)
            m.raiz.rotation_euler = (math.radians(10 + 14 * s_), 0, math.radians(6 * sg))
            key(m.raiz, "location", f, "BEZIER"); key(m.raiz, "rotation_euler", f, "BEZIER")


def a1E(N):
    corre(REG["rita"], N, 4.2 * N / FPS, fase=2, dx=-0.1)              # passam por nós e entram (a porta fica atrás da câmera)
    corre(REG["lu"], N, 4.3 * N / FPS, fase=6, dx=0.1)
    corre(REG["ze"], N, 2.3, fase=3, dx=0.35, freia=0.55)              # o Zé chega e para do lado da porta
    corre(REG["eu"], N, 3.6 * N / FPS, fase=5)
    corre_atrasados(N)
    camera_viva(N, mao=1.0, seed=51, frente=0.15)


def acena(z, N, f1=None, per=15):
    """o Zé acena para a rua: o braço vai e volta em arco, o tronco acompanha (até f1)"""
    P = dict(z._ultima); f1 = f1 or N
    ch = []
    for f in range(1, f1 + 1, 2):
        th = 2 * math.pi * (f - 1) / per
        d = dict(P); d["ombro"] = (-148 + 16 * math.sin(th), 8); d["cotovelo"] = (-24 - 22 * (0.5 + 0.5 * math.sin(th + 0.9)), -12)
        d["giro"] = 4 * math.sin(th); d["cabeca"] = 4 + 3 * math.sin(th + 1.5)
        d["pos"] = tuple(z.raiz.location); d["rot"] = math.degrees(z.raiz.rotation_euler.z)
        ch.append((f, d))
    return ch


def a1F(N):
    z = REG["ze"]; sombra(z).anima(acena(z, N), 1, N, vida=0.8)
    corre(REG["eu"], N, 2.4, fase=5, ciclo=13, inclina=11)
    corre_atrasados(N)
    # o céu vai ficando branco: a luz do cogumelo cresce em curva e a exposição sobe por último
    alfa("clarao_m", [(1, 0.0), (8, 0.06), (18, 0.4), (26, 0.8), (N, 0.92)])
    alfa("cogumelo_gl_m", [(1, 0.35), (N, 0.8)])
    exposicao([(1, 0.0), (14, 0.05), (22, 0.3), (N, 0.75)])
    camera_viva(N, mao=0.8, seed=61, frente=0.4)


def a2A(N):
    # o clarão estoura e vai baixando: a imagem volta (o olho se acostuma) e dá para ver quem entra
    exposicao([(1, 2.6), (3, 2.2), (8, 1.0), (14, 0.45), (N, 0.3)])
    eu = REG["eu"]; x, y, _ = eu.raiz.location
    corre(eu, N, 3.0 * N / FPS, fase=3, ciclo=13, inclina=10, dx=0.2)  # passa pela porta e some na luz de dentro
    corre_atrasados(N)
    z = REG["ze"]; zx, zy, _ = z.raiz.location
    ch = acena(z, N, 19)                                               # acena mais uma vez, desiste, vira e entra por último
    P = dict(z._ultima)
    ch.append((23, dict(P, pos=(zx - 0.05, zy + 0.05, 0), rot=120, ombro=(-20, 6), cotovelo=(-30, -20), tronco=-6, cabeca=6)))
    ch += corrida(25, N + 6, (zx - 0.15, zy + 0.15, 0), (0.05, BY + 1.8, 0), rot=168, ciclo=13, inclina=10, arranque=0.5)
    sombra(z).anima(ch, 1, N, vida=0.6)
    camera_viva(N, vel=(0.1, 0.05, 0), mao=1.0, seed=81)


def a2B(N):
    """de fora e de lado: a folha corre e fecha o vão (empurrada pelo Zé lá dentro) antes de o rapaz do mercado chegar; ele estica o braço,
    a porta bate na frente dele e ele só consegue bater no aço; a padaria e os vizinhos chegam atrás"""
    folha = bpy.data.objects["bunker_porta_folha"]
    ab = lambda f: max(0.0, 0.55 - 0.55 * suave5(faixa(f, 1, 17))) + 0.012 * math.exp(-max(0, f - 17) / 1.6) * math.sin(max(0, f - 17) * 1.6) * (f > 17)
    for f in range(1, N + 1):
        folha.location.x = ab(f) * 1.1; key(folha, "location", f, "LINEAR")
    alfa("bunker_luz_dentro_m", [(f, 0.4 * min(1.0, ab(f) / 0.3)) for f in range(1, N + 1, 2)])     # a luz de dentro some com o vão
    luz = bpy.data.objects.get("bunker_luz_dentro")
    m = REG["mercado"]; mx, my, _ = m.raiz.location
    alvo = (0.32, BY - 0.42, 0)
    ch = corrida(1 - 5, 19, (mx, my - ST.ATRASO_V * 5 / FPS, 0), alvo, rot=180, ciclo=13, inclina=13, freia=0.35)
    estica = dict(ombro=(-100, -40), cotovelo=(-6, -30), abre=(4, 14), tronco=-14, cabeca=-6, rot=180, pos=alvo)
    bate1 = dict(ombro=(-128, -100), cotovelo=(-70, -14), abre=(-4, -6), tronco=-6, cabeca=-4, rot=180, pos=(alvo[0], alvo[1] - 0.03, 0))
    bate2 = dict(ombro=(-100, -128), cotovelo=(-14, -70), abre=(-6, -4), tronco=-6, cabeca=-4, rot=180, pos=(alvo[0], alvo[1] - 0.03, 0))
    junto = dict(ombro=(-98, -96), cotovelo=(-8, -10), abre=(-6, -6), tronco=-4, cabeca=-2, rot=180, pos=(alvo[0], alvo[1] + 0.02, 0))
    ch += [(17, estica), (20, junto), (23, bate1), (26, junto), (29, bate2), (N, junto)]
    sombra(m).anima(ch, 1, N, vida=0.4, molas=dict(pos=(0, 9.0, 1.0), ombro=(0, 6.5, 0.8), cotovelo=(0, 7.0, 0.8)))
    m.expressao([(1, dict(boca="o", lid=0.0)), (18, dict(boca="o", lid=0.0, brow=0.6))], 1, N, piscar=False)
    for ch_, nm, x, dy, fase in ST.ATRASADOS[1:4]:                    # os outros chegam correndo atrás dele (e freiam na porta)
        H = REG.get(nm)
        if H is None:
            continue
        hx, hy, _ = H.raiz.location
        andou = min(ST.ATRASO_V * N / FPS, (BY - 0.9 + 0.25 * fase % 3) - hy)
        corre(H, N, andou, fase=fase, ciclo=13, inclina=12, freia=0.45 if andou < ST.ATRASO_V * N / FPS else 0.0)
    camera_viva(N, mao=1.3, seed=93, extra=lambda f: ((0, 0, soco(f, [17], 0.009) + soco(f, [23, 29], 0.004)), (0, 0, 0)))


def a2C(N):
    roda = bpy.data.objects["porta_roda"]
    ang = lambda f: (-40 + 7 * math.sin(math.pi * faixa(f, 1, 5)) - 34 * suave5(faixa(f, 4, 13))
                     - 3 * math.exp(-max(0, f - 13) / 2) * math.sin(max(0, f - 13) * 1.3))
    for f in range(1, N + 1):
        roda.rotation_euler = (0, math.radians(ang(f)), 0); key(roda, "rotation_euler", f, "LINEAR")
    z = REG["ze"]; P = dict(z._ultima)
    ch = []
    for f in range(1, N + 1, 2):                                      # os braços seguem a roda: um sobe e o outro desce
        d = ang(f) + 40
        q = dict(P); q["ombro"] = (-92 + 0.28 * d, -92 - 0.28 * d); q["giro"] = 0.08 * d; q["tronco"] = -4 - 0.06 * abs(d)
        ch.append((f, q))
    sombra(z).anima(ch, 1, N, vida=0.3, mola=False)
    camera_viva(N, mao=1.0, seed=101, extra=lambda f: ((0, soco(f, [13], 0.006), 0), (0, 0, 0)))


def a2D(N):
    for k, nm in enumerate(("pv0", "pv1", "pv2", "pv3", "pv4", "pv5")):
        H = REG.get(nm)
        if H is None:
            continue
        P = dict(H._ultima); x, y, _ = H.raiz.location; per = 11 + 2 * (k % 3); ph = 1.7 * k
        ch = []
        for f in range(1, N + 1, 2):                                  # batem na porta, cada um no seu tempo; o corpo vai junto com o soco
            th = 2 * math.pi * (f - 1) / per + ph; s = 0.5 + 0.5 * math.sin(th)
            q = dict(P); o0, o1 = P["ombro"]; c0, c1 = P["cotovelo"]
            q["ombro"] = (o0 - 12 * s, o1 - 12 * (1 - s)); q["cotovelo"] = (c0 - 26 * s, c1 - 26 * (1 - s))
            q["pos"] = (x, y + 0.03 * s, 0); q["rot"] = math.degrees(H.raiz.rotation_euler.z); q["giro"] = 5 * (s - 0.5)
            ch.append((f, q))
        sombra(H).anima(ch, 1, N, vida=0.6, seed=k)
    camera_viva(N, frente=0.22, mao=1.0, seed=111)


def a2E(N):
    batidas = []
    for k, nm in enumerate(("pad", "mer")):
        H = REG[nm]; P = dict(H._ultima); x, y, _ = H.raiz.location; rot = math.degrees(H.raiz.rotation_euler.z)
        o0, o1 = P["ombro"]; c0, c1 = P["cotovelo"]
        ch = [(1, dict(P, pos=(x, y, 0), rot=rot))]
        f = 2 + 5 * k
        lado = 0
        while f < N + 8:                                              # recolhe (antecipação), vai rápido, bate, um punho de cada vez
            ob = dict(P, pos=(x, y - 0.03, 0), rot=rot)
            if lado == 0:
                ob["ombro"] = (o0 - 26, o1); ob["cotovelo"] = (c0 - 70, c1)
            else:
                ob["ombro"] = (o0, o1 - 26); ob["cotovelo"] = (c0, c1 - 70)
            ch.append((f, ob)); ch.append((f + 4, dict(P, pos=(x, y + 0.02, 0), rot=rot)))
            batidas.append(f + 4); f += 7 + (k + lado) % 2; lado = 1 - lado
        sombra(H).anima(ch, 1, N, vida=0.4, molas=dict(ombro=(0, 7.0, 0.85), cotovelo=(0, 8.0, 0.85), abre=(0, 7.0, 0.85)))
    for k, nm in enumerate(("vizA", "vizB", "vizC", "vizD")):            # atrás, os outros empurram e acenam por cima
        H = REG.get(nm)
        if H is None:
            continue
        P = dict(H._ultima); x, y, _ = H.raiz.location; rot = math.degrees(H.raiz.rotation_euler.z)
        per = 13 + 3 * k; ch = []
        for f in range(1, N + 1, 2):
            th = 2 * math.pi * (f - 1) / per + 1.3 * k
            q = dict(P, pos=(x + 0.04 * math.sin(th * 0.6), y + 0.05 * math.sin(th), 0), rot=rot)
            q["ombro"] = (-120 - 22 * math.sin(th), -60 - 18 * math.sin(th + 1.2)); q["cotovelo"] = (-30 - 20 * math.sin(th + 0.5), -50)
            q["giro"] = 6 * math.sin(th); q["cabeca"] = -8 + 5 * math.sin(th + 0.7)
            ch.append((f, q))
        sombra(H).anima(ch, 1, N, vida=0.6, seed=k + 20)
    camera_viva(N, mao=1.2, seed=121, extra=lambda f: ((0, -soco(f, batidas, 0.005), 0), (0, 0, 0)))


def a2F(N):
    for k, nm in enumerate(("padeira", "mercado")):
        H = REG[nm]; P = dict(H._ultima); x, y, z = H.raiz.location; rot = math.degrees(H.raiz.rotation_euler.z)
        ch = []
        for f in range(1, N + 1, 2):                                  # colados no vidro: empurram, a cabeça procura o Zé, as mãos escorregam
            th = 2 * math.pi * (f - 1) / (16 + 4 * k) + 1.3 * k
            q = dict(P, pos=(x + 0.025 * math.sin(th * 0.5), y - 0.015 * math.sin(th), z + 0.012 * math.sin(th * 1.3)), rot=rot)
            q["cabeca"] = P.get("cabeca", 0) + 8 * math.sin(th); q["olha"] = 13 * math.sin(th * 0.7)              # procuram o Zé lá dentro
            o0, o1 = P["ombro"]; q["ombro"] = (o0 + 7 * math.sin(th), o1 - 7 * math.sin(th + 0.8))
            c0, c1 = P["cotovelo"]; q["cotovelo"] = (c0 + 6 * math.sin(th + 0.4), c1 - 6 * math.sin(th + 1.1))   # as mãos escorregam no vidro
            ch.append((f, q))
        sombra(H).anima(ch, 1, N, vida=0.5, seed=k + 5)
    parado(REG["ze"], N, vida=1.0, seed=9)
    camera_viva(N, frente=0.1, mao=0.8, seed=131)


def a2G(N):
    z = REG["ze"]; P = dict(z._ultima)
    sombra(z).anima([(1, dict(P, cabeca=10, olha=0)), (8, dict(P, cabeca=11, olha=-3)), (N, dict(P, cabeca=19, olha=-4))], 1, N, vida=0.7)
    z.expressao([(1, dict(boca="triste", lid=0.42)), (9, dict(boca="triste", lid=0.48)), (17, dict(boca="triste", lid=0.78))], 1, N, piscar=False)
    camera_viva(N, frente=0.12, mao=0.6, seed=141)


# ====================================================================== falas 3 a 11
def trilha(nome, N, chaves, interp="LINEAR"):
    """move um objeto pelo caminho das chaves [(quadro, (dx, dy, dz), (rx, ry, rz em graus))], relativas à posição do storyboard,
    em curva cúbica monótona (passa pelas chaves sem parar nelas)"""
    from heroi3d import _monotona
    o = bpy.data.objects.get(nome) if isinstance(nome, str) else nome
    if o is None:
        return None
    L0, R0 = o.location.copy(), o.rotation_euler.copy()
    for f in range(1, N + 1):
        d = [_monotona([(k[0], k[1][i]) for k in chaves], f) for i in range(3)]
        r = [_monotona([(k[0], (k[2] if len(k) > 2 else (0, 0, 0))[i]) for k in chaves], f) for i in range(3)]
        o.location = L0 + Vector(d); o.rotation_euler = Euler([R0[i] + math.radians(r[i]) for i in range(3)])
        key(o, "location", f, interp); key(o, "rotation_euler", f, interp)
    return o


def anda(H, N, de, ate, rot, ciclo=22, arranque=0.3, freia=0.3, f0=1, f1=None):
    """caminhada: a corrida do kit com a passada pequena (quadril, joelho e braço reduzidos), sem descer o corpo"""
    ch = corrida(f0, f1 or N, de, ate, rot=rot, ciclo=ciclo, inclina=3, arranque=arranque, freia=freia)
    out = []
    for f, d in ch:
        q0, q1 = d["quadril"]; j0, j1 = d["joelho"]; o0, o1 = d["ombro"]
        out.append((f, dict(d, quadril=(0.42 * q0, 0.42 * q1), joelho=(6 + 0.38 * (j0 - 14), 6 + 0.38 * (j1 - 14)), tornozelo=(4, 4),
                            ombro=(0.3 * o0, 0.3 * o1), cotovelo=(-16, -16), abre=(6, 6), tronco=-3, giro=0.4 * d["giro"], alt=None)))
    for _, d in out:
        d.pop("alt")
    return out


def prende(obj_nome, H, lado="F"):
    """prende um objeto na mão do boneco (o suéter, a Pipoca), para ele não descolar quando o corpo respira"""
    o = bpy.data.objects.get(obj_nome)
    if o is None:
        return
    bpy.context.view_layer.update(); mw = o.matrix_world.copy(); o.parent = H.punho[lado]; o.matrix_world = mw


def foco_passa(N, de, para, fa, fb):
    """o foco passa de um ponto para outro em curva (f/fb em quadros)"""
    c = bpy.context.scene.camera; cd = c.data
    for f in range(1, N + 1):
        u = suave(faixa(f, fa, fb)); p = Vector(de).lerp(Vector(para), u)
        cd.dof.focus_distance = (p - c.matrix_world.translation).length; cd.dof.keyframe_insert("focus_distance", frame=f)


def pisca_luz(N, quedas, fundo=-0.9):
    """a luz falha: a exposição cai e volta em 2 a 3 quadros nos quadros dados"""
    ks = [(1, 0.0)]
    for f in quedas:
        ks += [(f - 1, 0.0), (f, fundo), (f + 1, fundo * 0.4), (f + 3, 0.0)]
    ks.append((N, 0.0))
    exposicao(sorted(dict(ks).items()))



def riscar(N, f_toca, f_fim, f_sobe, quem="eu"):
    """o personagem risca o dia no quadro: o braço sobe até o começo do risco, encosta o giz, puxa até o fim (o risco nasce atrás da ponta do giz),
    afasta o giz e o braço desce. Cada ponto do caminho é resolvido por cinemática inversa (a ponta do giz fica no plano do quadro)"""
    R = ST.RISCO; H = REG[quem]; s = R["lado"]; a, b, off = R["a"], R["b"], R["off"]
    P = dict(H._ultima); P["pos"] = tuple(H.raiz.location); P["rot"] = 180.0
    rec = lambda p, r, dz=0.0: ST.ponta_giz(p) + Vector((0.0, -r, dz))
    ik = lambda p: IK.braco_pose(H, s, p, P, off=off, nome="risca")
    chaves = [(1, ik(rec(a, 0.17, 0.09))), (f_toca - 3, ik(rec(a, 0.05, 0.03))), (f_toca, ik(rec(a, 0.0)))]
    for k in range(1, 5):
        u = k / 4; chaves.append((int(round(f_toca + (f_fim - f_toca) * u)), ik(rec(a.lerp(b, u), 0.0))))
    chaves += [(f_fim + 3, ik(rec(b, 0.1, -0.03))), (f_sobe, dict(P, abre=(8, 8), ombro=(-30, -6) if s == "F" else (-6, -30), cotovelo=(-60, -16) if s == "F" else (-16, -60), tronco=-3)), (N, dict(P, abre=(8, 8), ombro=(-12, -6) if s == "F" else (-6, -12), cotovelo=(-34, -16) if s == "F" else (-16, -34)))]
    chaves = [(f, dict(d, pos=P["pos"], rot=180.0)) for f, d in chaves]
    sombra(H).anima(chaves, 1, N, vida=0.35, molas=dict(ombro=(1, 6.5, 0.95), cotovelo=(1, 7.0, 0.95), abre=(1, 6.5, 0.95), tronco=(1, 4.0, 0.9)))
    r = bpy.data.objects["risco_novo"]; dire = (b - a).normalized()
    for f in range(1, N + 1):                                         # o risco nasce atrás da ponta do giz
        u = suave(faixa(f, f_toca, f_fim))
        r.scale = (1.0, 1.0, max(0.0001, u)); r.location = a + dire * (R["L"] * u / 2); r.hide_render = False
        key(r, "scale", f, "LINEAR"); key(r, "location", f, "LINEAR")
    dados = [o for o in bpy.data.objects if o.name.startswith("giz_na_mao")]
    camera_viva(N, vel=(0.0, 0.0, 0.0), frente=0.06, mao=0.5, seed=305)



def mistura_pose(a, b, u):
    """pose entre duas poses (dicts de tuplas/números), em linha reta nos ângulos"""
    out = dict(a)
    for k, v in b.items():
        if k in a and isinstance(v, (tuple, list)) and isinstance(a[k], (tuple, list)) and len(v) == len(a[k]):
            out[k] = tuple(x + (y - x) * u for x, y in zip(a[k], v))
        elif k in a and isinstance(v, (int, float)) and isinstance(a[k], (int, float)):
            out[k] = a[k] + (v - a[k]) * u
        else:
            out[k] = v
    return out


def garfo_na_mao(H, lado, nome=None):
    """um garfo preso ao punho, com os dentes apontando para a frente (como o antebraço) e um pouco para dentro; devolve (garfo, ponta dos dentes
    no sistema do punho): a ponta é o ponto que a cinemática inversa leva até a comida e até a boca"""
    import objetos3d_abrigo_b as O3B
    g = O3B.garfo3d(nome or f"garfo_{H.nome}", (0, 0, 0), 1.5, H.punho[lado], rot=(-107, 0, 0))
    R = Matrix.Rotation(math.radians(-107), 3, "X")
    g.location = Vector((0.002, 0.0, -0.045)) - R @ Vector((0, -0.045, 0))
    return g, g.location + R @ Vector((0, 0.1 * 1.5, 0))


def come(N, nome, lado, prato, per=30, fase=0, topo=0.86, outra=None, base=None, tronco=16, cabeca=8, mordida_f=None):
    """o personagem sentado come: o garfo espeta a comida (ponto 'prato' + topo), sobe até a boca, mastiga (a cabeça balança), volta ao prato.
    Tudo por cinemática inversa: a ponta do garfo vai ao ponto, então a mão nunca atravessa a mesa. A outra mão descansa em cima da mesa.
    base = pose de partida (por padrão a do storyboard); fase = em que quadro do ciclo o plano começa"""
    H = REG[nome]; P = dict(H._ultima) if base is None else dict(base)
    P["pos"] = tuple(H.raiz.location); P["rot"] = tuple(math.degrees(v) for v in H.raiz.rotation_euler) if (abs(H.raiz.rotation_euler.x) > 1e-3) else math.degrees(H.raiz.rotation_euler.z)
    P["tronco"] = tronco; P["cabeca"] = cabeca                       # inclina o corpo para o prato (com a cabeça muito baixa a boca afunda no peito)
    H.pose(**{k: v for k, v in P.items() if k not in ("pos", "rot")})
    bpy.context.view_layer.update()
    g, tip = garfo_na_mao(H, lado)
    A = Vector((prato[0], prato[1], topo)); B = IK.boca_de(H)
    fw = (H.cabeca.matrix_world.to_3x3() @ Vector((0, -1, 0))).normalized()
    B = B + fw * 0.045 + Vector((0, 0, 0.012))
    L = A + Vector((0, 0, 0.075)); Mi = A.lerp(B, 0.55) + Vector((0, 0, 0.07))
    ik = lambda p, nm: IK.braco_pose(H, lado, p, P, off=tip, nome=nm, faixa_abre=(-70, 70))
    pa, pl, pm, pb = ik(A, "come:prato"), ik(L, "come:levanta"), ik(Mi, "come:meio"), ik(B, "come:boca")
    if outra is not None:
        o = "B" if lado == "F" else "F"
        pa, pl, pm, pb = [IK.braco_pose(H, o, outra, d, nome="outra mao", faixa_abre=(-70, 70)) for d in (pa, pl, pm, pb)]
    cicl = [(0, pa), (4, pl), (10, pm), (15, pb), (21, dict(pb, cabeca=P.get("cabeca", 0) + 3)), (27, pm), (per, pa)]
    ks = {}
    for c0 in range(-per, N + per, per):
        for dt, pose in cicl:
            f = c0 + dt - fase + 1
            if 1 <= f <= N:
                ks[f] = dict(pose, pos=P["pos"], rot=P["rot"])
    for f in (1, N):                                                  # as pontas: entre dois pontos do ciclo
        if f not in ks:
            ts = sorted(set(ks) | {f}); i = ts.index(f)
            ant = ks[ts[i - 1]] if i > 0 else None; prx = ks[ts[i + 1]] if i + 1 < len(ts) else None
            if ant and prx:
                ks[f] = mistura_pose(ant, prx, (f - ts[i - 1]) / max(1, ts[i + 1] - ts[i - 1]))
            else:
                ks[f] = ant or prx
    sombra(H).anima(sorted(ks.items()), 1, N, vida=0.3, molas=dict(ombro=(1, 6.0, 0.88), cotovelo=(1, 6.5, 0.88), abre=(1, 6.0, 0.88)))
    return g



def familia(N, ombro_rita=True):
    """o Zé e a Rita ajoelhados ao lado da cama: ele segura a mão dela (a mão dele vai até o pulso da Lu), a Rita põe a mão no ombro dela;
    os dois choram sem som (o peito sobe em soluços curtos); a Lu respira cada vez mais devagar"""
    lu, ze, ri = REG["lu"], REG["ze"], REG["rita"]
    bpy.context.view_layer.update()
    cand = [(lu.punho[s_].matrix_world.translation.copy(), s_) for s_ in "FB"]; pulso, _ = min(cand, key=lambda t: t[0].y)
    ombr = min([(lu.ombro[s_].matrix_world.translation.copy(), s_) for s_ in "FB"], key=lambda t: t[0].y)[0]
    PL = dict(lu._ultima); base = tuple(lu.raiz.location); rot = tuple(math.degrees(v) for v in lu.raiz.rotation_euler)
    lu_ch = []
    for f in range(1, N + 1, 2):                                     # respira cada vez mais devagar e mais fundo
        per = 20 + 0.8 * f
        lu_ch.append((f, dict(PL, pos=(base[0], base[1], base[2] + 0.006 * math.sin(2 * math.pi * f / per)), rot=rot, tronco=1.2 * math.sin(2 * math.pi * f / per))))
    sombra(lu).anima(lu_ch, 1, N, vida=0.0, mola=False)
    for nm, H, alvo_mao, lado, fase in (("ze", ze, pulso + Vector((0, -0.03, 0.05)), "F", 0.0), ("rita", ri, ombr + Vector((0, -0.04, 0.07)), "F", 1.6)):
        P = dict(H._ultima); P["pos"] = tuple(H.raiz.location); P["rot"] = 180.0
        pose = IK.braco_pose(H, lado, alvo_mao, P, nome=f"familia {nm}")
        pose2 = IK.braco_pose(H, "B" if lado == "F" else "F", Vector((H.raiz.location.x + (0.12 if lado == "F" else -0.12), 3.72, 0.60)), pose, nome=f"{nm} outra")
        ch = []
        for f in range(1, N + 1, 2):
            sol = max(0.0, math.sin(2 * math.pi * (f / 9.0) + fase)) ** 3                  # soluços: o tronco e a cabeça saltam um pouco
            ch.append((f, dict(pose2, pos=P["pos"], rot=180.0, tronco=P.get("tronco", 10) + 2.5 * sol, cabeca=P.get("cabeca", 18) + 3 * sol)))
        sombra(H).anima(ch, 1, N, vida=0.5, seed=hash(nm) % 50, molas=dict(ombro=(1, 6.0, 0.9), cotovelo=(1, 6.5, 0.9)))
    bpy.context.view_layer.update()
    for nm, H, lg in (("lagr0", ze, 0.0), ("lagr1", ri, 0.0)):       # uma lágrima escorre de cada um
        o = bpy.data.objects.get(nm)
        if o is None:
            o = O3B.lagrima3d(nm, (0, 0, 0), 1.0)
        olho = H.olhos["F"].matrix_world.translation.copy()
        o.location = olho + Vector((0.0, 0.05, -0.04)); o.scale = (1.0,) * 3
        trilha(o, N, [(1, (0, 0, 0)), (8, (0, 0, 0)), (N, (0.0, 0.004, -0.1))])



def veu_branco(N, chaves, cor="#ffffff", nome="veu"):
    """um véu da cor dada colado na frente da câmera, com transparência em curva (chaves = [(quadro, alfa)]): a transição do clarão para a rua"""
    import cena
    cam_ = bpy.context.scene.camera
    m = cena.amat(nome + "_m", cor, 1.0, 1.0)
    d = cena.disc(nome, 1.6, m, (0, 0, -0.5)); d.parent = cam_; d.location = (0, 0, -0.45); d.rotation_euler = (math.radians(90), 0, 0)
    alfa(nome + "_m", chaves)




def envoltoria_voz(wav, t_ini, N, fps=24):
    """energia da voz por quadro (0 a 1) a partir do wav de uma fala que começa em t_ini (s do filme): o plano começa em ST.SHOTS[...]['t0']"""
    import subprocess, numpy as np
    raw = subprocess.check_output(["ffmpeg", "-v", "error", "-i", wav, "-ar", "16000", "-ac", "1", "-f", "f32le", "-"])
    x = np.frombuffer(raw, np.float32)
    out = []
    for f in range(N):
        a = int((f / fps + t_ini) * 16000); b = int(((f + 1) / fps + t_ini) * 16000)
        seg = x[max(0, a):max(0, b)] if b > 0 else x[:0]
        out.append(float(np.sqrt((seg ** 2).mean())) if len(seg) else 0.0)
    m = max(out) if out else 1.0
    return [v / (m + 1e-9) for v in out]


def fala_na_boca(H, env, N, lim=0.16):
    """a boca do narrador abre e fecha no ritmo da voz (envoltória por quadro): 'o' aberta quando a voz passa do limite, 'reta' fechada;
    nunca troca em menos de 2 quadros; as pálpebras piscam sozinhas"""
    ks = []; estado = None; ultimo = -9
    for f in range(1, N + 1):
        e = env[f - 1] if f - 1 < len(env) else 0.0
        e2 = max(e, env[f - 2] * 0.55 if f >= 2 else 0.0)
        novo = "o" if e2 > lim else "reta"
        if novo != estado and f - ultimo >= 2:
            ks.append((f, dict(boca=novo, lid=0.28 + 0.1 * (1 - min(1, e)))))
            estado = novo; ultimo = f
    if not ks:
        ks = [(1, dict(boca="reta", lid=0.3))]
    H.expressao(ks, 1, N, piscar=True, seed=5)
    return ks



def fecha_olhos(H, N, f0, f1, ate=0.08):
    """fecha os olhos de verdade: o branco do olho achata até uma fresta (a pálpebra sozinha não cobria o olho com a câmera de frente); depois de expressao()"""
    for f in range(1, N + 1):
        u = suave(faixa(f, f0, f1))
        for s_ in ("F", "B"):
            E = H.olhos[s_]; E.scale = (1.0, 1.0, 1.0 - (1.0 - ate) * u); key(E, "scale", f, "LINEAR")


def a3A(N):
    camera_viva(N, frente=0.35, mao=0.8, seed=301)


def a3B(N):
    camera_viva(N, vel=(-0.28, 0.0, 0), mao=0.35, seed=302)           # desliza de lado, devagar (paralaxe entre as filas)

def a3C(N):
    for g in ("galao_a", "galao_b"):
        for k in range(6):                                           # bolhas sobem e somem no topo da água
            o = bpy.data.objects.get(f"{g}_bolha{k}")
            if o is None:
                continue
            z0 = o.location.z
            for f in range(1, N + 1):
                z = 0.03 + ((z0 - 0.03 + 0.012 * f) % 0.2); o.location.z = z; o.location.x += 0.0
                s_ = 1.0 if z < 0.21 else 0.0001; o.scale = (s_,) * 3
                key(o, "location", f, "LINEAR"); key(o, "scale", f, "CONSTANT")
        a = bpy.data.objects.get(g + "_agua")
        if a is not None:                                            # a superfície balança de leve
            trilha(a, N, [(f, (0, 0, 0), (1.5 * math.sin(f * 0.6), 1.0 * math.sin(f * 0.45), 0)) for f in range(1, N + 1, 2)])
    camera_viva(N, vel=(0.06, 0.05, 0.02), mao=0.5, seed=303)

def a3D(N):
    for k in range(3):                                               # as lâmpadas respiram (o filamento oscila)
        alfa(f"brilho{k}_m", [(f, 0.36 + 0.06 * math.sin(f * 0.5 + 2 * k)) for f in range(1, N + 1, 2)])
    camera_viva(N, mao=0.6, seed=304, extra=lambda f: ((0, 0, 0), (0, 0, -6 * (f - 1) / N)))   # gira devagar em volta do eixo


def a3E(N):
    riscar(N, 7, 18, 21)

def a3F(N):
    pip = bpy.data.objects.get("pipoca_inv")
    if pip:                                                          # a Pipoca come: a cabeça sobe e desce no ritmo de quem mastiga
        trilha(pip, N, [(f, (0, 0.006 * math.sin(f * 0.9), 0), (2.5 * math.sin(f * 1.1), 0, 3 * math.sin(f * 0.45))) for f in range(1, N + 1, 3)])
    for k, nm in enumerate(("ze", "lu", "rita", "eu")):              # comem e riem: o garfo sobe, a cabeça balança na risada
        H = REG[nm]; P = dict(H._ultima); ch = []
        for f in range(1, N + 1, 2):
            th = 2 * math.pi * (f - 1) / (18 + 4 * k) + k
            ch.append((f, dict(P, pos=tuple(H.raiz.location), rot=0, cotovelo=(-60 - 28 * max(0, math.sin(th)), -62), cabeca=-6 * abs(math.sin(th * 1.6)), tronco=3 * math.sin(th * 1.6))))
        sombra(H).anima(ch, 1, N, vida=0.8, seed=k)
        H.expressao([(1, dict(boca="sorriso", lid=0.25))], 1, N, piscar=True, seed=k + 3)
    foco_passa(N, (0.15, 1.85, 0.15), (-0.5, 3.55, 1.4), 10, 22)
    camera_viva(N, mao=0.6, seed=306, frente=0.06)


def a4A(N):
    """a estante esvazia em saltos, de baixo para cima; a luz falha a cada salto; sobram 3 latas lá no alto"""
    import re
    latas = []
    for o in bpy.data.objects:
        m = re.match(r"^est_lata(\d)_(\d)_(\d+)$", o.name)
        if m:
            latas.append((int(m.group(1)), int(m.group(2)), int(m.group(3)), o))
    r = random.Random(11); fica = set(r.sample([o.name for k, f, i, o in latas if k == 2], 3))
    saltos = [4, 8, 12, 16, 20]
    for k, f, i, o in sorted(latas):
        if o.name in fica:
            continue
        j = min(len(saltos) - 1, k * 2 + (0 if k < 2 else 0) + r.randint(0, 1) + (i > 4))        # de baixo para cima, as da frente e as do fundo misturadas
        fr = saltos[min(len(saltos) - 1, j)]
        o.scale = (1, 1, 1); key(o, "scale", fr - 1, "CONSTANT"); o.scale = (0.0001,) * 3; key(o, "scale", fr, "CONSTANT")
    pisca_luz(N, saltos, fundo=-0.7)
    camera_viva(N, vel=(-0.28, 0.0, 0), mao=0.35, seed=302)

def _come(N, sobe):
    for nm in ("mao_g_piv", "garfo", "colher", "bocado"):
        o = bpy.data.objects.get(nm)
        if o is not None:
            trilha(o, N, sobe)
    trilha("mao_p_piv", N, [(1, (0, 0, 0), (0, 0, 0)), (N // 2, (0.004, 0.002, 0), (0, 0, 2)), (N, (0, 0, 0), (0, 0, 0))])


def a4B(N):
    for k, nm in enumerate(("ze", "lu", "rita", "eu")):              # os quatro comem, cada um no seu tempo: o garfo sobe até a boca e desce
        H = REG.get(nm)
        if H is None:
            continue
        P = dict(H._ultima); ch = []
        for f in range(1, N + 1, 2):
            th = 2 * math.pi * (f - 1) / (17 + 3 * k) + 1.7 * k; u = max(0.0, math.sin(th)) ** 1.5
            o0, o1 = P["ombro"]; c0, c1 = P["cotovelo"]
            ch.append((f, dict(P, pos=tuple(H.raiz.location), rot=math.degrees(H.raiz.rotation_euler.z), ombro=(o0 - 14 * u, o1), cotovelo=(c0 - 58 * u, c1), cabeca=6 - 6 * u)))
        sombra(H).anima(ch, 1, N, vida=0.6, seed=k + 30)
    camera_viva(N, frente=0.1, mao=0.5, seed=402)

def a4C(N):
    """o garfo afunda no arroz, junta o bocado e sobe até a boca (sai do quadro por baixo); a cabeça desce um pouco ao encontro dele"""
    sobe = [(1, (0.012, 0.03, 0.03), (0, 0, 0)), (4, (0.008, 0.025, 0.02)), (8, (0.0, 0.006, -0.012), (-6, 0, 0)), (10, (0.0, 0.0, -0.008), (-4, 0, 0)),
            (17, (0.01, -0.3, 0.14), (16, 0, 4)), (N, (0.02, -0.62, 0.3), (24, 0, 6))]     # vem para a lente e sai por baixo: a boca fica logo abaixo dos olhos
    for nm in ("mao_g_piv", "garfo", "bocado"):
        o = bpy.data.objects.get(nm)
        if o is not None:
            trilha(o, N, sobe)
    b = bpy.data.objects.get("bocado")
    if b is not None:                                                # o bocado só aparece quando o garfo junta a comida
        for f in range(1, N + 1):
            s_ = 0.0001 if f < 9 else 1.0; b.scale = (s_,) * 3; key(b, "scale", f, "CONSTANT")
    a = bpy.data.objects.get("prato_arroz")
    if a is not None:
        for f in range(1, N + 1):
            k = 1.0 - 0.18 * suave(faixa(f, 8, 11)); a.scale = (k, k, 1.0); key(a, "scale", f, "LINEAR")
    trilha("mao_p_piv", N, [(1, (0, 0, 0)), (12, (0.004, 0.006, 0.002)), (N, (0.002, 0.004, 0))])
    camera_viva(N, mao=0.4, seed=402, extra=lambda f: ((0, 0.02 * suave(faixa(f, 10, 20)), -0.03 * suave(faixa(f, 10, 20))), (-3 * suave(faixa(f, 10, 20)), 0, 0)))

def a4D(N):
    """o Zé olha dentro da última lata, vê que está vazia e deixa ela cair na pilha: ela quica, rola e para; ele baixa a cabeça"""
    H = REG["ze"]; P = dict(H._ultima); P["pos"] = tuple(H.raiz.location); P["rot"] = 0.0
    u = bpy.data.objects["ultima"]; j = bpy.data.objects["ultima_mao"]
    f_rel = 13
    P1 = IK.braco_pose(H, "B", Vector((-2.46, 4.15, 1.2)), P, nome="olha a lata")         # a lata na frente do rosto
    P2 = IK.braco_pose(H, "B", Vector((-2.4, 4.1, 0.95)), P, nome="estende")              # estende o braço sobre a pilha
    ch = [(1, dict(P, ombro=(-8, -50), cotovelo=(-20, -80), abre=(4, 8), cabeca=6)),
          (6, dict(P1, cabeca=22)), (11, dict(P1, cabeca=20)),
          (f_rel - 1, dict(P2, cabeca=14)), (f_rel + 6, dict(P2, cabeca=16)), (N, dict(P, ombro=(-6, -14), cotovelo=(-14, -24), abre=(4, 6), cabeca=30, tronco=3))]
    sombra(H).anima(ch, 1, N, vida=0.4, molas=dict(ombro=(1, 6.0, 0.9), cotovelo=(1, 6.5, 0.9)))
    bpy.context.view_layer.update()
    # onde a lata estava na mão no quadro da soltura (a posição vem da constraint: o objeto fica no ponto da mão)
    sc = bpy.context.scene; sc.frame_set(f_rel)
    x0, y0, z0 = j.matrix_world.translation
    alvo = Vector((ST.PILHA[0] + 0.03, ST.PILHA[1] - 0.02, 0.145 + 0.05 * 1.4))                  # em cima da pilha (centro da lata deitada)
    c = u.constraints[0]
    for f in range(1, N + 1):
        c.influence = 1.0 if f < f_rel else 0.0; c.keyframe_insert("influence", frame=f)
        t = (f - f_rel) / FPS
        if f < f_rel:
            u.location = (0, 0, 0); u.rotation_euler = (0, 0, 0)
        else:
            z = max(alvo.z, z0 - 4.9 * t * t) if t < 0.5 else alvo.z
            q = (f - f_rel) / 9.0
            if q <= 1.0:
                zz = z0 + (alvo.z - z0) * q * q                                    # cai acelerando
                xx = x0 + (alvo.x - x0) * q; yy = y0 + (alvo.y - y0) * q
                rot_x = 90 * q * q + 15 * math.sin(q * 3)
            else:
                b = (f - f_rel - 9)                                                # quica uma vez e assenta
                zz = alvo.z + 0.05 * math.exp(-b / 2.5) * abs(math.sin(b * 0.9)); xx = alvo.x + 0.02 * (1 - math.exp(-b / 3)); yy = alvo.y - 0.015 * (1 - math.exp(-b / 3))
                rot_x = 90 + 6 * math.exp(-b / 3) * math.sin(b * 0.9)
            u.location = (xx - alvo.x, yy - alvo.y, zz - alvo.z) if False else (xx, yy, zz)
            u.rotation_euler = (math.radians(rot_x), 0, math.radians(18 * min(1.0, (f - f_rel) / 10.0)))
        key(u, "location", f, "LINEAR"); key(u, "rotation_euler", f, "LINEAR")
    camera_viva(N, vel=(-0.03, 0.14, 0.0), mao=0.45, seed=404)

def a4E(N):
    z = REG["ze"]; P = dict(z._ultima); ch = []
    for f in range(1, N + 1, 2):                                     # o lápis anda e para; a cabeça acompanha a conta
        ch.append((f, dict(P, pos=tuple(z.raiz.location), rot=180, cotovelo=(-62 + 4 * math.sin(f * 0.9) * (f < 16), -66), cabeca=14 + 3 * math.sin(f * 0.3))))
    sombra(z).anima(ch, 1, N, vida=0.5)
    cad = bpy.data.objects.get("caderno")
    if cad:
        prende("caderno", z, "B")
    foco_passa(N, tuple(cad.matrix_world.translation) if cad else (-0.25, 2.2, 1.1), (-0.15, 3.5, 1.45), 12, 24)
    camera_viva(N, mao=0.6, seed=405)


def a4F(N):
    lu, ri = REG["lu"], REG["rita"]
    P = dict(lu._ultima); sombra(lu).anima([(1, dict(P, olha=0, pos=tuple(lu.raiz.location), rot=0)), (6, dict(P, olha=-4, pos=tuple(lu.raiz.location), rot=0)),
                                           (14, dict(P, olha=-26, pos=tuple(lu.raiz.location), rot=0)), (N, dict(P, olha=-24, pos=tuple(lu.raiz.location), rot=0))], 1, N)
    P = dict(ri._ultima); sombra(ri).anima([(1, dict(P, cabeca=2, olha=8, pos=tuple(ri.raiz.location), rot=0)), (10, dict(P, cabeca=3, olha=10, pos=tuple(ri.raiz.location), rot=0)),
                                           (20, dict(P, pos=tuple(ri.raiz.location), rot=0)), (N, dict(P, pos=tuple(ri.raiz.location), rot=0))], 1, N)
    camera_viva(N, frente=0.1, mao=0.6, seed=406)


def a5A(N):
    riscar(N, 9, 25, 28)

def moscas(N):
    for o in [o for o in bpy.data.objects if o.name.startswith("mosca") and o.name[5:].isdigit()]:
        k = int(o.name[5:]); L0 = o.location.copy(); r = random.Random(k + 7)
        a, b, w = r.uniform(0.08, 0.16), r.uniform(0.05, 0.12), r.uniform(4.0, 6.5)
        for f in range(1, N + 1):
            t = f / FPS
            o.location = L0 + Vector((a * math.sin(w * t + k), b * math.sin(1.7 * w * t + 2 * k), 0.04 * math.sin(2.3 * w * t)))
            o.rotation_euler.z = w * t + k; key(o, "location", f, "LINEAR"); key(o, "rotation_euler", f, "LINEAR")


def a5B(N):
    for nm, d in (("agua_b", 0.55), ("agua_a", 0.3), ("agua_br", 0.45)):    # a água avança para a lente
        trilha(nm, N, [(1, (0, d, 0)), (N, (0, 0, 0))])
    moscas(N); camera_viva(N, mao=0.4, seed=502)


def a5C(N):
    moscas(N); camera_viva(N, frente=0.12, mao=0.6, seed=503)


def a5D(N):
    for o in [o for o in bpy.data.objects if "neblina" in o.name or o.name.startswith("nev")]:
        trilha(o, N, [(1, (-0.15, 0, 0)), (N, (0.15, 0, 0))])
    for nm, f0 in (("ze", 2), ("lu", 6)):                            # puxa a camisa / tapa a boca, um depois do outro
        H = REG[nm]; P = dict(H._ultima); x, y, _ = H.raiz.location; rot = math.degrees(H.raiz.rotation_euler.z)
        o0, o1 = P["ombro"]; c0, c1 = P["cotovelo"]
        baixo = dict(P, ombro=(o0 * 0.3, o1) if nm == "ze" else (o0, o1 * 0.3), cotovelo=(c0 * 0.25, c1) if nm == "ze" else (c0, c1 * 0.25), cabeca=0, pos=(x, y, 0), rot=rot)
        sombra(H).anima([(1, baixo), (f0, baixo), (f0 + 9, dict(P, pos=(x, y, 0), rot=rot, cabeca=8)), (N, dict(P, pos=(x, y, 0), rot=rot, cabeca=10))], 1, N)
    ri = REG["rita"]; P = dict(ri._ultima)
    sombra(ri).anima([(f, dict(P, pos=tuple(ri.raiz.location), rot=0, olha=22 * math.sin(f * 0.18), cabeca=-4)) for f in range(1, N + 1, 3)], 1, N)
    camera_viva(N, frente=0.12, mao=0.8, seed=504)


def a5E(N):
    ri = REG["rita"]; P = dict(ri._ultima)                          # soluça escondida: o tronco treme curto
    sombra(ri).anima([(f, dict(P, pos=tuple(ri.raiz.location), rot=0, tronco=2.5 * math.sin(f * 1.3), cabeca=24 + 2 * math.sin(f * 1.3 + 0.5))) for f in range(1, N + 1)], 1, N, vida=0.4)
    moscas(N); camera_viva(N, frente=0.06, mao=0.5, seed=505)


def _pipoca_come(N, nome="pip_inv"):
    trilha(nome, N, [(f, (0, 0.004 * math.sin(f * 1.4), 0), (3 * max(0, math.sin(f * 1.4)), 0, 2 * math.sin(f * 0.25))) for f in range(1, N + 1, 2)])
    fo = bpy.data.objects.get(nome + "_focinho")
    if fo:
        for f in range(1, N + 1):
            s_ = 1 + 0.12 * max(0, math.sin(f * 1.9)); fo.scale = (s_, s_, s_); key(fo, "scale", f, "LINEAR")


def a6A(N):
    _pipoca_come(N); camera_viva(N, frente=0.08, mao=0.5, seed=601)


def a6B(N):
    _pipoca_come(N)
    for s_, sg in (("F", 1), ("B", -1)):                             # as orelhas mexem
        trilha(f"pip_inv_orelha{s_}", N, [(1, (0, 0, 0), (0, 0, 0)), (8, (0, 0, 0), (0, sg * 12, 0)), (14, (0, 0, 0), (0, 0, 0)), (N, (0, 0, 0), (0, sg * 6, 0))])
    camera_viva(N, frente=0.03, mao=0.35, seed=602)


def a6C(N):
    ri = REG["rita"]; prende("pip_inv", ri, "F"); P = dict(ri._ultima)
    sombra(ri).anima([(f, dict(P, pos=tuple(ri.raiz.location), rot=0, giro=3.5 * math.sin(f * 0.22), tronco=1.2 * math.sin(f * 0.22 + 1), cabeca=10 + 3 * math.sin(f * 0.22 + 0.6)))
                      for f in range(1, N + 1, 2)], 1, N, vida=0.5)     # embala a Pipoca
    camera_viva(N, frente=0.08, mao=0.5, seed=603)


def a6D(N):
    camera_viva(N, frente=0.06, mao=0.4, seed=601)                   # o mesmo quadro do 6A, mais lento


def a6E(N):
    """a mão entra pela portinha, pega o suéter pela gola e puxa para fora: ele se abre pendurado e balança"""
    piv = bpy.data.objects["mao_su_piv"]; m = MAOS["mao_su"]
    d = (piv.rotation_euler.to_quaternion() @ Vector((0, 1, 0))).normalized()
    G = piv.location.copy()
    caminho = [(1, -d * 0.5 + Vector((0.0, 0.0, 0.06))), (5, -d * 0.22 + Vector((0, 0, 0.03))), (10, Vector((0, 0, 0))), (12, Vector((0, 0, 0.004))),
               (19, -d * 0.24 + Vector((0, 0, 0.05))), (N, -d * 0.32 + Vector((0, 0, 0.09)))]
    from heroi3d import _monotona
    pos = {}
    for f in range(1, N + 1):
        v = Vector([_monotona([(k, p_[i]) for k, p_ in caminho], f) for i in range(3)])
        piv.location = G + v; key(piv, "location", f, "LINEAR"); pos[f] = piv.location.copy()
        u = suave(faixa(f, 9, 12))
        if u <= 0:
            m.pose("aberta", f=f)
        else:
            mao_mix(m, "aberta", "pinca", u, f)
    dob = bpy.data.objects["gaiola_su"]; pend = bpy.data.objects["sueter_pend"]
    dob_s = dob.scale.copy()
    for f in range(1, N + 1):                                        # troca o dobrado pelo pendurado quando a mão fecha
        dob.scale = dob_s if f < 12 else Vector((0.0001,) * 3); key(dob, "scale", f, "CONSTANT")
        if f < 12:
            pend.scale = (0.0001,) * 3
        else:
            ab = suave(faixa(f, 12, 17))                             # abre do dobrado até cair inteiro
            pend.scale = (1.5, 1.5, 1.5 * (0.35 + 0.65 * ab))
        pend.location = pos[f] + d * 0.1 + Vector((0, 0, -0.01))
        vel = (pos[f] - pos[max(1, f - 1)])
        pend.rotation_euler = (math.radians(-260 * vel.y + 4 * math.sin(f * 0.7) * (f > 14)), math.radians(260 * vel.x), math.radians(-20))
        key(pend, "scale", f, "LINEAR"); key(pend, "location", f, "LINEAR"); key(pend, "rotation_euler", f, "LINEAR")
    camera_viva(N, mao=0.4, seed=605)

def a6F(N):
    z = REG["ze"]; P = dict(z._ultima)
    sombra(z).anima([(1, dict(P, olha=2, cabeca=2, pos=tuple(z.raiz.location), rot=0)), (5, dict(P, olha=4, cabeca=3, pos=tuple(z.raiz.location), rot=0)),
                     (14, dict(P, pos=tuple(z.raiz.location), rot=0)), (N, dict(P, pos=tuple(z.raiz.location), rot=0, cabeca=9))], 1, N)
    z.expressao([(1, dict(boca="reta", lid=0.3)), (10, dict(boca="reta", lid=0.55))], 1, N, piscar=False)
    camera_viva(N, frente=0.04, mao=0.4, seed=606)


def _comem_devagar(N, nomes):
    for k, nm in enumerate(nomes):
        H = REG.get(nm)
        if H is None:
            continue
        P = dict(H._ultima); ch = []
        for f in range(1, N + 1, 2):
            th = 2 * math.pi * (f - 1) / (30 + 6 * k) + k
            c0, c1 = P["cotovelo"]
            ch.append((f, dict(P, pos=tuple(H.raiz.location), rot=math.degrees(H.raiz.rotation_euler.z), cotovelo=(c0 - 16 * max(0, math.sin(th)), c1))))
        sombra(H).anima(ch, 1, N, vida=0.5, seed=k + 9)


def a6G(N):
    for nm, lado, pr, fase, rest in (("ze", "B", ST.PRATO_ZE, 3, None), ("lu", "B", ST.PRATO_LU, 14, None), ("rita", "B", ST.PRATO_RITA, 22, None), ("eu", "B", ST.PRATO_EU, 8, None)):
        pz = Vector((pr[0], pr[1], 0.835)); ho = REG[nm]
        outra = Vector((pr[0], pr[1], 0.835)) + (ho.raiz.location - Vector((pr[0], pr[1], ho.raiz.location.z))).normalized().cross(Vector((0, 0, 1))) * 0.3
        come(N, nm, lado, pr, per=34, fase=fase, outra=outra)
    camera_viva(N, frente=0.12, mao=0.5, seed=607)

def vapor(N):
    for o in [o for o in bpy.data.objects if o.name.startswith("vapor") and o.name[5:].isdigit()]:
        k = int(o.name[5:]); L0 = o.location.copy()
        for f in range(1, N + 1):
            o.location = L0 + Vector((0.006 * math.sin(f * 0.21 + k), 0, 0.02 * ((f * 0.02 + k * 0.33) % 1.0)))
            o.rotation_euler.z = 0.3 * math.sin(f * 0.13 + k); s_ = 1 + 0.15 * math.sin(f * 0.17 + k); o.scale = (s_, s_, 1)
            key(o, "location", f, "LINEAR"); key(o, "rotation_euler", f, "LINEAR"); key(o, "scale", f, "LINEAR")


def a6H(N):
    trilha("garfo", N, [(1, (0.22, -0.05, 0.16)), (4, (0.2, -0.045, 0.15)), (14, (0, 0, 0)), (16, (0, 0, 0.003)), (N, (0, 0, 0.002))])   # entra e para no ar
    vapor(N); camera_viva(N, mao=0.4, seed=608)


def a6I(N):
    pr = ST.PRATO_LU; ho = REG["lu"]
    outra = Vector((pr[0], pr[1], 0.835)) + (ho.raiz.location - Vector((pr[0], pr[1], ho.raiz.location.z))).normalized().cross(Vector((0, 0, 1))) * 0.3
    come(N, "lu", "B", pr, per=34, fase=4, outra=outra, tronco=16, cabeca=10)
    camera_viva(N, mao=0.5, seed=609)

def a6J(N):
    pr = ST.PRATO_ZE; ho = REG["ze"]
    outra = Vector((pr[0], pr[1], 0.835)) + (ho.raiz.location - Vector((pr[0], pr[1], ho.raiz.location.z))).normalized().cross(Vector((0, 0, 1))) * 0.3
    come(N, "ze", "B", pr, per=34, fase=9, outra=outra, tronco=16, cabeca=10)
    camera_viva(N, mao=0.5, seed=610)


def a6K(N):
    """a Rita empurra o prato para o lado com a mão (a mão encosta na borda e vai junto com ele) e chora; as mãos nunca entram na mesa"""
    ri = REG["rita"]; P = dict(ri._ultima); P["pos"] = tuple(ri.raiz.location); P["rot"] = 0.0
    P["tronco"] = 3; P["cabeca"] = 2
    ri.pose(**{k: v for k, v in P.items() if k not in ("pos", "rot")}); bpy.context.view_layer.update()
    pr = ST.PRATO_RITA; pr0 = Vector((pr[0], pr[1], 0.0)); fim = Vector((0.32, -0.14, 0.0))
    ik = lambda s_, p, nm: IK.braco_pose(ri, s_, p, None, nome=nm) if False else None
    def duas(pl, pr_):                                               # esquerda e direita, uma por vez sobre a base
        d = IK.braco_pose(ri, "F", pl, P, nome="rita esq"); return IK.braco_pose(ri, "B", pr_, d, nome="rita dir")
    descanso = duas(Vector((pr[0] - 0.2, 3.02, 0.835)), Vector((pr[0] + 0.2, 3.02, 0.835)))
    contato0 = pr0 + Vector((-0.12, 0.1, 0.84)); contato1 = pr0 + fim + Vector((-0.12, 0.1, 0.84))
    p0 = duas(contato0 + Vector((0, 0.05, 0.0)), Vector((pr[0] + 0.2, 3.02, 0.835)))
    p1 = duas(contato1 + Vector((0, 0.05, 0.0)), Vector((pr[0] + 0.2, 3.02, 0.835)))
    ch = [(1, dict(descanso, cabeca=2)), (4, dict(p0, cabeca=3)), (14, dict(p1, cabeca=6)), (20, dict(p1, cabeca=7)),
          (N, dict(descanso, cabeca=9, ombro=(-20, -20), cotovelo=(-60, -60)))]
    sombra(ri).anima([(f, dict(d, pos=P["pos"], rot=0.0)) for f, d in ch], 1, N, vida=0.4, molas=dict(ombro=(1, 6.0, 0.9), cotovelo=(1, 6.5, 0.9)))
    trilha("prato_r", N, [(1, (0, 0, 0)), (5, (0, 0, 0)), (15, (fim.x, fim.y, 0), (0, 0, 22)), (N, (fim.x + 0.02, fim.y - 0.01, 0), (0, 0, 24))])
    bpy.context.view_layer.update()
    olho = ri.olhos["F"].matrix_world.translation.copy()
    for nm, dz0, f0 in (("lagr0", 0.0, 6), ("lagr1", 0.02, 14)):
        o = bpy.data.objects.get(nm)
        if o:
            o.location = olho + Vector((0.0, -0.06, -0.05 - dz0)); o.scale = (1.7, 1.7, 1.7)
            trilha(o, N, [(1, (0, 0, 0)), (f0, (0, 0, 0)), (N, (0.003, -0.006, -0.07 + 0.002 * f0))])
    camera_viva(N, frente=0.03, mao=0.4, seed=611)

def a7A(N):
    pisca_luz(N, [17], fundo=-0.6); camera_viva(N, frente=0.15, mao=0.6, seed=701)


def a7B(N):
    camera_viva(N, mao=0.0, seed=702)                                # câmera de segurança: parada de verdade
    ri = REG.get("rita")
    if ri:
        P = dict(ri._ultima); sombra(ri).anima([(f, dict(P, pos=tuple(ri.raiz.location), rot=math.degrees(ri.raiz.rotation_euler.z), tronco=4 * math.sin(f * 0.25))) for f in range(1, N + 1, 2)], 1, N, vida=0.3)


def _briga(N, z, l, lamp=None):
    Pz, Pl = dict(z._ultima), dict(l._ultima)
    rz, rl = math.degrees(z.raiz.rotation_euler.z), math.degrees(l.raiz.rotation_euler.z)
    chz, chl = [], []
    for f in range(1, N + 1, 2):                                     # ele aponta o dedo em golpes; ela rebate com os dois braços, meio tempo depois
        a = max(0.0, math.sin(2 * math.pi * f / 11)) ** 2; b = max(0.0, math.sin(2 * math.pi * (f - 5) / 13)) ** 2
        o0, o1 = Pz["ombro"]; chz.append((f, dict(Pz, pos=tuple(z.raiz.location), rot=rz, ombro=(o0 - 22 * a, o1), cotovelo=(-40 + 30 * a, -12), tronco=-6 - 5 * a, cabeca=-3 * a)))
        q0, q1 = Pl["ombro"]; chl.append((f, dict(Pl, pos=tuple(l.raiz.location), rot=rl, ombro=(q0 - 18 * b, q1 - 14 * b), cotovelo=(-60 + 20 * b, -64 + 16 * b), tronco=-4 + 4 * b)))
    sombra(z).anima(chz, 1, N, vida=0.6, molas=dict(ombro=(0, 6.0, 0.7), cotovelo=(0, 6.5, 0.7)))
    sombra(l).anima(chl, 1, N, vida=0.6, seed=2)


def a7C(N):
    _briga(N, REG["ze"], REG["lu"])
    o = bpy.data.objects.get("lamp1")
    if o:                                                            # a lâmpada balança entre os dois
        trilha(o, N, [(f, (0.03 * math.sin(f * 0.35), 0, 0), (0, 2.5 * math.sin(f * 0.35), 0)) for f in range(1, N + 1, 2)])
    camera_viva(N, mao=1.6, seed=703)


def a7D(N):
    _briga(N, REG["ze"], REG["lu"]); camera_viva(N, mao=0.0, seed=704)


def a7E(N):
    familia(N, ombro_rita=True)
    camera_viva(N, vel=(0.05, -0.08, 0.0), mao=0.5, seed=705)

def a7F(N):
    familia(N, ombro_rita=False)
    l = REG["lu"]
    l.expressao([(1, dict(boca="reta", lid=0.8)), (10, dict(boca="reta", lid=1.0)), (N, dict(boca="reta", lid=1.0))], 1, N, piscar=False)
    fecha_olhos(l, N, 8, N - 2)                                      # os olhos vão fechando até ficar só uma fresta
    camera_viva(N, frente=0.04, mao=0.3, seed=706)

def a7G(N):
    camera_viva(N, frente=0.18, mao=0.3, seed=705)


def _da_carta(N, carta, de, H, f0=3, f1=16):
    trilha(carta, N, [(1, de, (0, 0, -40)), (f0, de, (0, 0, -40)), (f1, (0, 0, 0)), (f1 + 2, (0, 0, 0)), (N, (0, 0, 0))])
    P = dict(H._ultima); x, y, z_ = H.raiz.location; rot = math.degrees(H.raiz.rotation_euler.z)
    o0, o1 = P["ombro"]; c0, c1 = P["cotovelo"]
    sombra(H).anima([(1, dict(P, pos=(x, y, z_), rot=rot)), (f0, dict(P, pos=(x, y, z_), rot=rot, ombro=(o0 - 8, o1))),
                     ((f0 + f1) // 2, dict(P, pos=(x + 0.08 * math.sin(math.radians(rot)), y - 0.08 * math.cos(math.radians(rot)), z_), rot=rot,
                                         ombro=(o0 - 26, o1), cotovelo=(c0 + 30, c1), tronco=-5)),      # inclina vindo para a frente (não para trás, na cadeira)
                     (f1 + 3, dict(P, pos=(x, y, z_), rot=rot)), (N, dict(P, pos=(x, y, z_), rot=rot))], 1, N)


def a8A(N):
    _da_carta(N, "carta4", (-0.75, 0.0, 0.0), REG["ze"]); camera_viva(N, mao=0.3, seed=801, extra=lambda f: ((0, 0, 0), (0, 0, 3 * (f - 1) / N)))


def a8B(N):
    _da_carta(N, "carta3", (-1.1, -0.1, 0.0), REG["ze"]); camera_viva(N, mao=0.0, seed=802)


def a8C(N):
    _da_carta(N, "carta2", (-1.25, 0.05, 0.0), REG["ze"], 4, 20); camera_viva(N, mao=0.4, seed=803, frente=0.05)


def a9A(N):
    """o Zé agacha ao lado do galão, agarra a alça e levanta; o galão acompanha a mão quadro a quadro (pesa: o corpo se curva e ele balança)"""
    H = REG["ze"]; g = bpy.data.objects["galao_z"]; s_ = 1.8
    P = dict(H._ultima); P["pos"] = tuple(H.raiz.location); P["rot"] = 0.0
    alca_l = Vector((0.15 * s_, 0.0, 0.2 * s_)); G0 = g.location.copy()
    agacha = H.pe_no_chao(quadril=(-78, -78), joelho=(128, 128), tornozelo=(36, 36), tronco=24, cabeca=18, ombro=(-6, -6), cotovelo=(-12, -12), abre=(8, 8))
    H.pose(**agacha); bpy.context.view_layer.update()
    pega = IK.braco_pose(H, "F", G0 + alca_l, dict(agacha, pos=P["pos"], rot=0.0), nome="9A alca")
    sobe = H.pe_no_chao(quadril=(-14, -14), joelho=(26, 26), tornozelo=(6, 6), tronco=6, cabeca=8, ombro=pega["ombro"], cotovelo=pega["cotovelo"], abre=pega["abre"])
    H.pose(**sobe); bpy.context.view_layer.update()
    alto = IK.braco_pose(H, "F", Vector((H.ombro["F"].matrix_world.translation.x - 0.02, H.ombro["F"].matrix_world.translation.y, H.ombro["F"].matrix_world.translation.z - 0.55)),
                         dict(sobe, pos=P["pos"], rot=0.0), nome="9A levantado")
    ch = [(1, dict(P)), (5, dict(agacha, pos=P["pos"], rot=0.0)), (9, dict(pega, pos=P["pos"], rot=0.0)), (12, dict(pega, pos=P["pos"], rot=0.0, tronco=26)),
          (22, dict(alto, pos=P["pos"], rot=0.0)), (N, dict(alto, pos=P["pos"], rot=0.0, tronco=8))]
    sombra(H).anima(ch, 1, N, vida=0.3, molas=dict(ombro=(1, 6.0, 0.9), cotovelo=(1, 6.5, 0.9), quadril=(1, 5.0, 0.85), joelho=(1, 5.0, 0.85), tronco=(1, 4.0, 0.85)))
    sc = bpy.context.scene
    for f in range(1, N + 1):                                         # depois de agarrar, o galão vai preso na alça
        sc.frame_set(f)
        if f < 9:
            g.location = G0; g.rotation_euler = (0, 0, 0)
        else:
            u = suave(faixa(f, 12, 22)); ry = math.radians(-14 * u + 5 * math.sin(f * 0.5) * faixa(f, 18, N))
            R = Matrix.Rotation(ry, 3, "Y")
            hand = H.punho["F"].matrix_world @ Vector(IK.OFF_MAO)
            g.rotation_euler = (0, ry, 0); g.location = hand - R @ alca_l
        key(g, "location", f, "LINEAR"); key(g, "rotation_euler", f, "LINEAR")
    camera_viva(N, vel=(0.0, 0.0, 0.03), mao=0.5, seed=901)

def a9B(N):
    """o Zé bebe (os goles), baixa o galão com as duas mãos até a altura do quadril, solta o ar e vira a cabeça para a porta; o galão acompanha as mãos
    (cinemática inversa em cada estado) e a água fica sempre de nível (uma água pronta para cada inclinação)"""
    from heroi3d import _monotona
    z = REG["ze"]; g = bpy.data.objects["galao_z"]; s_ = 1.5
    P0 = {k: v for k, v in z._ultima.items() if k not in ("pos", "rot")}
    G0 = g.location.copy(); L2 = Vector((-0.425, 3.0, 0.5))
    L1 = G0.lerp(L2, 0.55) + Vector((0.0, -0.06, 0.0))
    estados = [(1, -112.0, G0, -6, -24, 0.0), (12, -112.0, G0, -6, -26, 0.0), (17, -58.0, L1, -2, -8, 0.0), (23, -4.0, L2, 2, 2, 8.0), (N, 0.0, L2 + Vector((0, 0, -0.1)), 0.0, 4, 60.0)]
    chaves, gal = [], []
    for f, phi, L, tr, cb, ol in estados:
        z.pose(**dict(P0, tronco=tr, cabeca=cb, olha=ol)); bpy.context.view_layer.update()
        R = Matrix.Rotation(math.radians(phi), 3, "X")
        alca = L + R @ Vector((0.15 * s_, 0.0, 0.2 * s_)); lado = L + R @ Vector((-0.1 * s_ - 0.04, 0.0, 0.1 * s_))
        d = IK.braco_pose(z, "B", alca, dict(P0, tronco=tr, cabeca=cb, olha=ol), nome=f"9B alça f{f}")
        d = IK.braco_pose(z, "F", lado, d, nome=f"9B lado f{f}")
        chaves.append((f, dict(d, tronco=tr, cabeca=cb, olha=ol, pos=tuple(z.raiz.location), rot=0.0)))
        gal.append((f, phi, L))
    sombra(z).anima(chaves, 1, N, vida=0.2, mola=False)
    FASES = (-112, -94, -76, -58, -40, -22, -6, 0)
    for f in range(1, N + 1):
        phi = _monotona([(k, v) for k, v, _ in gal], f)
        L = Vector([_monotona([(k, l[i]) for k, _, l in gal], f) for i in range(3)])
        g.location = L; g.rotation_euler = (math.radians(phi), 0, 0)
        key(g, "location", f, "LINEAR"); key(g, "rotation_euler", f, "LINEAR")
        mais_perto = min(FASES, key=lambda a: abs(a - phi))
        for ph in FASES:
            o = bpy.data.objects.get(f"agua_ph{abs(ph)}")
            if o is not None:
                o.hide_render = False; o.scale = (1, 1, 1) if ph == mais_perto else (0.0001,) * 3; key(o, "scale", f, "CONSTANT")
    z.expressao([(1, dict(boca="reta", lid=1.5)), (13, dict(boca="reta", lid=1.5)), (19, dict(boca="reta", lid=0.35))], 1, N, piscar=False)
    camera_viva(N, vel=(-0.02, 0.0, 0.0), mao=0.4, seed=902)

def a9C(N):
    """ele anda de verdade até a porta: passo firme, braços balançando, cabeça erguida; pára e vira de frente para a roda; a Rita só olha"""
    z, ri = REG["ze"], REG["rita"]; x, y, _ = z.raiz.location
    ch = anda(z, N - 7, (x, y, 0), (2.62, 4.62, 0), rot=118, ciclo=24, arranque=0.2, freia=0.55)
    ch = [(f, dict(d, ombro=(d["ombro"][0] * 1.4, d["ombro"][1] * 1.4), cotovelo=(-26, -26), cabeca=0, tronco=-2)) for f, d in ch]
    for f, rot_ in ((N - 5, 150.0), (N - 1, 178.0), (N, 180.0)):                                            # chega, respira e vira de frente para a roda
        ch.append((f, dict(ch[-1][1], pos=(2.9, 4.62, 0.0), rot=rot_, ombro=(-6, 8), cotovelo=(-14, -14), tronco=-4)))
    sombra(z).anima(ch, 1, N, vida=0.3, molas=dict(pos=(0, 9.0, 1.0), rot=(0, 6.0, 0.85)))
    P = dict(ri._ultima)
    sombra(ri).anima([(1, dict(P, pos=tuple(ri.raiz.location), rot=40.0, olha=0)), (12, dict(P, pos=tuple(ri.raiz.location), rot=40.0, olha=36)), (N, dict(P, pos=tuple(ri.raiz.location), rot=40.0, olha=48))], 1, N, vida=0.5)
    alfa("luz_porta_m", [(1, 0.0), (N, 0.55)])
    camera_viva(N, vel=(0.5, 0.45, 0.0), mao=0.45, seed=903, centro=0.0)

def _roda_ze(N, ang, a0):
    roda = bpy.data.objects["porta_roda"]
    for f in range(1, N + 1):
        roda.rotation_euler = (0, math.radians(ang(f)), 0); key(roda, "rotation_euler", f, "LINEAR")
    z = REG["ze"]; P = dict(z._ultima); ch = []
    for f in range(1, N + 1, 2):
        d = ang(f) - a0
        ch.append((f, dict(P, ombro=(-92 + 0.28 * d, -92 - 0.28 * d), giro=0.08 * d, tronco=-4 - 0.06 * abs(d))))
    sombra(z).anima(ch, 1, N, vida=0.3, mola=False)


def a9D(N):
    """por cima do ombro: o Zé gira a roda (o corpo se joga), ferrugem cai, a folha destranca e a luz de fora cresce pelas bordas"""
    _roda_ze(N, lambda f: 60 - 6 * math.sin(math.pi * faixa(f, 1, 5)) + 36 * suave5(faixa(f, 4, 14)), 60)    # gira ao contrário do 2C
    rnd = random.Random(5)
    for o in [o for o in bpy.data.objects if o.name.startswith("ferrugem")]:
        vx, f0 = rnd.uniform(-0.1, 0.1), rnd.randint(4, 12)
        trilha(o, N, [(1, (0, 0, 0)), (f0, (0, 0, 0))] + [(f, (vx * (f - f0) / FPS, 0, -4.9 * ((f - f0) / FPS) ** 2), (0, 0, 40 * (f - f0) / FPS)) for f in range(f0 + 2, N + 1, 2)])
    folha = bpy.data.objects["porta_folha"]
    for f in range(1, N + 1):
        folha.location.x = (0.02 + 0.12 * entra(faixa(f, 11, N), 2)) * 1.1; key(folha, "location", f, "LINEAR")
    alfa("luz_fresta_m", [(1, 0.05), (10, 0.12), (N, 0.45)]); alfa("luz_chao_m", [(1, 0.0), (10, 0.15), (N, 0.5)])
    for k in range(3):
        alfa(f"luz_nevoa{k}_m", [(1, 0.0), (12, 0.04), (N, 0.14 + 0.03 * k)])
    camera_viva(N, vel=(-0.05, 0.2, 0.0), mao=0.6, seed=904, centro=0.0)

def a9E(N):
    """a porta abre: o Zé empurra a folha andando junto com ela (o corpo acompanha a roda, então as mãos não soltam), a luz entra por trás dele e a tela
    estoura em branco só nos últimos quadros (antes o braço ficava no ar quando a roda saía da mão)"""
    folha = bpy.data.objects["porta_folha"]; roda = bpy.data.objects["porta_roda"]; sc = bpy.context.scene
    for f in range(1, N + 1):
        folha.location.x = (0.14 + 0.5 * suave5(faixa(f, 1, N - 2))) * 1.1; key(folha, "location", f, "LINEAR")
    z = REG["ze"]; P = dict(z._ultima); x0, y0 = z.raiz.location.x, z.raiz.location.y
    sc.frame_set(1); c0 = roda.matrix_world.translation.copy()
    ch = []
    for f in sorted(set(list(range(1, N + 1, 2)) + [N])):
        sc.frame_set(f); c = roda.matrix_world.translation.copy()
        u = suave(faixa(f, 1, N))
        ch.append((f, dict(P, ombro=(-82 - 6 * u, -102 + 4 * u), cotovelo=(-18, -18), tronco=-6 - 8 * u, cabeca=2 + 4 * u, pos=(x0 + (c.x - c0.x), y0, 0.0), rot=180.0)))
    sombra(z).anima(ch, 1, N, vida=0.15, mola=False)
    alfa("luz_fresta_m", [(1, 0.45), (6, 0.8), (N, 1.0)]); alfa("luz_chao_m", [(1, 0.5), (N, 1.0)])
    for k in range(3):
        alfa(f"luz_nevoa{k}_m", [(1, 0.17), (8, 0.4), (N, 0.9)])
    veu_branco(N, [(1, 0.0), (N - 7, 0.0), (N - 1, 1.0), (N, 1.0)], cor="#ffffff", nome="veu_luz")          # o clarão que cega, só nos últimos quadros
    camera_viva(N, vel=(0.2, 0.25, 0), mao=0.8, seed=905, centro=0.0)

def a10A(N):
    veu_branco(N, [(1, 1.0), (3, 1.0), (8, 0.55), (14, 0.2), (20, 0.0), (N, 0.0)])     # sai do branco do 9E para a rua, em curva
    camera_viva(N, frente=0.55, mao=0.5, seed=1001)                                    # e o olhar avança devagar pela porta

def a10B(N):
    camera_viva(N, frente=0.1, mao=0.4, seed=1002)


def a10C(N):
    """o Zé sai do vão: o passo atravessa a soleira e o pé de apoio levanta uma nuvem de cinza que assenta"""
    H = REG["ze"]; x, y, _ = H.raiz.location
    ch = anda(H, N, (x, y, 0), (x, y - 1.35, 0), rot=0, ciclo=20, arranque=0.25, freia=0.55)
    sombra(H).anima(ch, 1, N, vida=0.3)
    import cena
    m = cena.amat("puff_m", "#6a655c", 1.0, 0.9, ("radial", 1.2))
    sc = bpy.context.scene
    toques = []
    for f in range(2, N + 1):                                         # o pé encosta no chão quando o tornozelo chega perto da cinza
        pass
    # nuvenzinhas nos pontos onde o pé pisa (de passada em passada, depois da soleira)
    for k, (fr, px) in enumerate(((9, -0.07), (15, 0.07), (21, -0.07))):
        yp = (y - 1.35 * suave(faixa(fr, 1, N))) - 0.05
        for j in range(3):
            d = cena.disc(f"puff{k}_{j}", 0.06, m, (px + 0.05 * (j - 1), yp, 0.06)); d.rotation_euler = (0, 0, math.radians(20 * j))
            for f in range(1, N + 1):
                u = faixa(f, fr, fr + 12)
                sz = 0.0001 if f < fr else (0.4 + 3.2 * u) * (1 + 0.3 * j)
                d.scale = (sz, 1.0, sz); d.location = (px + 0.05 * (j - 1) + 0.04 * u * (j - 1), yp - 0.03 * u, 0.05 + 0.18 * u)
                key(d, "scale", f, "LINEAR"); key(d, "location", f, "LINEAR")
        alfa(f"puff_m", [(fr - 1, 0.0), (fr + 1, 0.85), (fr + 12, 0.0)]) if k == 0 else None
    camera_viva(N, vel=(0.0, -0.1, 0.0), mao=0.4, seed=1003)

def a10D(N):
    camera_viva(N, vel=(-0.08, 0.05, 0), mao=0.4, seed=1004)


def a10E(N):
    camera_viva(N, frente=0.06, mao=0.4, seed=1005)


def a10F(N):
    trilha("mao_s_piv", N, [(1, (0.0, -0.06, 0.12)), (4, (0.0, -0.055, 0.11)), (12, (0, 0, 0)), (18, (0.0, 0.035, -0.004)), (24, (0, 0.0, 0)), (N, (0, 0.03, -0.003))])   # desce e passa o polegar
    camera_viva(N, mao=0.4, seed=1006)


def a10G(N):
    trilha("bici_sino", N, [(f, (0, 0, 0), (0, 0, 2.5 * math.exp(-(f - 3) / 4) * math.sin(f * 2.4) if f >= 3 else 0)) for f in range(1, N + 1)])   # o sino vibra ao tocar
    camera_viva(N, mao=0.3, seed=1007)


def _final(N, **cam):
    z, ri = REG["ze"], REG["rita"]
    prende("sueter_fim", ri, "B")
    parado(z, N, vida=0.8, seed=11); parado(ri, N, vida=0.6, seed=12)
    if "eu" in REG:
        parado(REG["eu"], N, vida=0.7, seed=13)
    camera_viva(N, **cam)


def a11A(N):
    _final(N, frente=0.15, mao=0.5, seed=1101)


def a11B(N):
    _final(N, frente=0.06, mao=0.4, seed=1102)


def a11C(N):
    _final(N, vel=(0, -1.6, 1.9), mao=0.4, seed=1103, centro=0.0)    # a grua sobe e recua


def a11D(N):
    """suspense antes do CTA (25/10/2026): os dois parados, um barulho fora do quadro (quadro 19), as cabeças viram para o mesmo lado, e um vulto
    desfocado bem perto da câmera, no escuro, entra devagar e rosna (quadro 31). A voz do fecho entra por cima do último quadro, sem fade"""
    z, ri, zb = REG["ze"], REG["rita"], ST.ZUMBI
    prende("sueter_fim", ri, "B")
    F_BARULHO = 19
    for H, f_ini, giro, seed, lid0 in ((ri, F_BARULHO + 2, 24, 13, 0.62), (REG["eu"], F_BARULHO + 3, 21, 15, 0.64), (z, F_BARULHO + 4, 18, 14, 0.68)):
        P = dict(H._ultima); P["pos"] = tuple(H.raiz.location); P["rot"] = 0.0
        ch = [(1, dict(P)), (f_ini - 1, dict(P)),
              (f_ini + 1, dict(P, olha=-7, giro=-4, cabeca=P.get("cabeca", 0) + 2)),                                            # recua um tiquinho (susto) antes de virar
              (f_ini + 6, dict(P, olha=74, giro=giro, cabeca=P.get("cabeca", 0) - 2, tronco=P.get("tronco", 0) + 2)),         # vira para o lado do barulho
              (f_ini + 14, dict(P, olha=72, giro=giro * 1.1, cabeca=P.get("cabeca", 0) - 2, tronco=P.get("tronco", 0) + 3)),
              (N, dict(P, olha=70, giro=giro * 1.2, cabeca=P.get("cabeca", 0) - 3, tronco=P.get("tronco", 0) + 4))]
        sombra(H).anima(ch, 1, N, vida=0.5, seed=seed, molas=dict(olha=(0, 7.0, 0.82), giro=(0, 5.0, 0.8), cabeca=(0, 6.0, 0.8)))
        H.expressao([(1, dict(boca="triste", lid=lid0)), (f_ini, dict(boca="triste", lid=lid0)), (f_ini + 3, dict(boca="o", lid=0.0, brow=0.8, olhos=1.12)),
                     (N, dict(boca="o", lid=0.0, brow=0.6, olhos=1.1))], 1, N, piscar=False)
    # o vulto: parado fora do quadro, entra devagar pela esquerda da câmera, balança e se estica quando rosna
    Pz = dict(zb._ultima); b0 = Vector(zb.raiz.location); e = Vector(ST.ESQ)
    ch = [(1, dict(Pz, pos=tuple(b0 + e * 1.0), rot=zb.raiz.rotation_euler.z * 57.2958)),
          (F_BARULHO + 6, dict(Pz, pos=tuple(b0 + e * 0.95), rot=zb.raiz.rotation_euler.z * 57.2958)),
          (F_BARULHO + 22, dict(Pz, pos=tuple(b0 + e * 0.45), tronco=-38, cabeca=-26, rot=zb.raiz.rotation_euler.z * 57.2958 - 4)),
          (F_BARULHO + 40, dict(Pz, pos=tuple(b0 + e * 0.12), tronco=-46, cabeca=-30, ombro=(-46, -30), cotovelo=(-30, -52), rot=zb.raiz.rotation_euler.z * 57.2958 - 8)),
          (N, dict(Pz, pos=tuple(b0), tronco=-48, cabeca=-32, ombro=(-50, -32), cotovelo=(-32, -54), rot=zb.raiz.rotation_euler.z * 57.2958 - 10))]
    sombra(zb).anima(ch, 1, N, vida=1.6, seed=21, molas=dict(pos=(0, 2.4, 0.9), rot=(0, 2.4, 0.9)))
    camera_viva(N, frente=0.035, mao=0.4, seed=1104, extra=lambda f: ((0, 0, soco(f, [F_BARULHO + 12], 0.006)), (0, 0, 0)))



def a12A(N):
    """o narrador fala para a câmera: a boca segue a voz, a cabeça acompanha as sílabas fortes, o corpo respira e na última frase ele abre a mão para nós;
    a câmera empurra devagar; no começo o preto sai (véu) e no fim a tela escurece"""
    H = REG["eu"]; P = dict(H._ultima); P["pos"] = tuple(H.raiz.location); P["rot"] = 0.0
    V = os.path.join(ST.__file__.rsplit("/kit3d/", 1)[0], "roteiros", "voz-abrigo")
    wav = os.path.join(V, "narracao_final.wav")                      # a mistura da voz com o fecho: o tempo do arquivo é o tempo do filme
    t0 = ST.SHOTS["12A"]["t0"]
    env = envoltoria_voz(wav, t0, N)
    # a fala começa depois do corte: o envoltório é por quadro do plano, com o wav deslocado
    fala_na_boca(H, env, N)
    ch = []
    suav = [0.0] * N
    for f in range(N):
        suav[f] = max(env[max(0, f - 2):f + 1])
    ult = max(i for i, v in enumerate(suav) if v > 0.2) if any(v > 0.2 for v in suav) else N - 1
    for f in range(1, N + 1, 2):
        e = suav[f - 1]; th = 2 * math.pi * f / 70
        gest = suave(faixa(f, ult - 26, ult - 12)) * (1 - suave(faixa(f, ult - 1, ult + 8)))                  # abre a mão na última frase
        d = dict(P, cabeca=P["cabeca"] + 2.5 + 3.5 * e + 2 * math.sin(th), olha=1.5 * math.sin(th * 0.7), tronco=-2 - 2.5 * e + 1.2 * math.sin(th * 0.8),
                 ombro=(-4 - 40 * gest, -4 - 40 * gest), cotovelo=(-14 - 70 * gest, -14 - 70 * gest), abre=(6 + 22 * gest, 6 + 22 * gest))
        ch.append((f, d))
    sombra(H).anima(ch, 1, N, vida=0.5, seed=12)
    veu_branco(N, [(1, 1.0), (10, 1.0), (24, 0.0), (N - 16, 0.0), (N, 1.0)], cor="#000000", nome="veu_preto")      # sai do preto do 11D e volta ao preto
    camera_viva(N, frente=0.045, mao=0.5, seed=1201, centro=0.0)


ANIM = {k[1:]: v for k, v in dict(globals()).items() if k.startswith("a") and k[1:] in ST.SHOTS}


# ---------------------------------------------------------------- suavidade das curvas (pedido de 25/10/2026: "deixar os gráficos de movimento mais suaves")
def _canais(so_camera=False):
    """(objeto, fcurve) de tudo que se move por rotação ou posição (junta, câmera, objeto)"""
    out = []
    for o in bpy.data.objects:
        ad = o.animation_data
        if ad is None or ad.action is None:
            continue
        if so_camera and o.type != "CAMERA":
            continue
        for fc in lib_fcurves(o):
            if fc.data_path in ("rotation_euler", "location") and len(fc.keyframe_points) > 4:
                out.append((o, fc))
    return out


def lib_fcurves(o):
    try:
        return list(o.animation_data.action.fcurves)
    except Exception:
        act = o.animation_data.action
        fcs = []
        for layer in getattr(act, "layers", []):
            for strip in layer.strips:
                for cb in strip.channelbags:
                    fcs += list(cb.fcurves)
        return fcs


def _amostras(fc, N):
    return [fc.evaluate(f) for f in range(1, N + 1)]


def tranco(N, limiar_rot=0.10, limiar_pos=0.03):
    """acha trancos (aceleração que salta de um quadro para o outro) em todas as juntas e objetos: devolve [(objeto, canal, quadro, valor)]"""
    achados = []
    for o, fc in _canais():
        v = _amostras(fc, N)
        lim = limiar_rot if fc.data_path == "rotation_euler" else limiar_pos
        for i in range(2, N - 1):
            a1 = v[i + 1] - 2 * v[i] + v[i - 1]; a0 = v[i] - 2 * v[i - 1] + v[i - 2]
            if abs(a1 - a0) > lim * 1.6 and abs(a1) > lim:                      # a aceleração muda de repente e é grande
                achados.append((o.name, fc.array_index, i + 1, abs(a1 - a0)))
    return achados


def suaviza(N, sigma=0.9, so_camera=False, nao=("soco",)):
    """passa um filtro gaussiano curto (sigma em quadros) por cada canal de rotação e posição e regrava as chaves quadro a quadro:
    tira o tremido de mola e de IK sem borrar o gesto (sigma < 1 quadro). As pontas do plano ficam como estão"""
    import math as m_
    pesos = [m_.exp(-(k * k) / (2 * sigma * sigma)) for k in range(-3, 4)]; soma = sum(pesos); pesos = [p / soma for p in pesos]
    n_ = 0
    for o, fc in _canais(so_camera):
        v = _amostras(fc, N)
        if max(v) - min(v) < 1e-5:
            continue
        w = []
        for i in range(N):
            acc = 0.0
            for k, pk in zip(range(-3, 4), pesos):
                acc += pk * v[min(N - 1, max(0, i + k))]
            w.append(acc)
        w[0], w[-1] = v[0], v[-1]
        idx = fc.array_index; path = fc.data_path
        kps = fc.keyframe_points
        kps.clear() if hasattr(kps, "clear") else [kps.remove(kps[i]) for i in range(len(kps) - 1, -1, -1)]
        kps.add(N)
        for i in range(N):
            kps[i].co = (i + 1, w[i]); kps[i].interpolation = "LINEAR"
            kps[i].handle_left_type = kps[i].handle_right_type = "VECTOR"
        fc.update(); n_ += 1
    return n_


def confere(sc, N, nome, minimo=0.0025):
    """1) o que se mexe e entra em outra coisa (colisao.verifica); 2) boneco atravessando móvel ou outro boneco já parado (mesmo sem mexer)"""
    import colisao as CO
    OK = (("bici", "eu_inv"), ("eu_inv", "bici"))                  # quem está sentado na bicicleta
    for a_, b_, fa, fb, v in CO.verifica(bpy, sc, 1, N, passo=2):
        if (a_, b_) in OK:
            continue
        print(f"COLISÃO {nome}: {a_} x {b_}  quadros {fa}-{fb}  volume {v * 1000:.1f} L")
    gs = CO.grupos(bpy)
    for f in sorted({1, (N + 1) // 2, N}):
        sc.frame_set(f)
        pecas = {n: [b for b in (CO.caixa([m]) for m in ms) if b and max(b[1][i] - b[0][i] for i in range(3)) < CO.MAX_LADO] for n, ms in gs.items()}
        bonecos = [n for n in gs if n.endswith("_inv") or n.startswith("esq_")]
        for a_ in bonecos:
            for b_ in gs:
                if b_ == a_ or (b_ in bonecos and b_ < a_):
                    continue
                v, na_, nb_ = 0.0, "", ""
                for ia, pa in enumerate(pecas[a_]):
                    for ib, pb in enumerate(pecas[b_]):
                        vv = CO.comum(pa, pb)
                        if vv > v:
                            v, na_, nb_ = vv, gs[a_][ia].name if len(gs[a_]) == len(pecas[a_]) else "?", gs[b_][ib].name if len(gs[b_]) == len(pecas[b_]) else "?"
                if v > minimo and not (na_.endswith("jaqueta") and "assento" in nb_) and not ("galao_z" in b_ and "cranio" in na_) and not ("galao_z" in a_ and "cranio" in nb_):
                    print(f"ATRAVESSA {nome} q{f}: {a_} x {b_}  volume {v * 1000:.1f} L  ({na_} x {nb_})")
    print("CONFERIDO", nome)


def quadros(nome):
    d = ST.SHOTS[nome]; return int(round(d["t1"] * FPS)) - int(round(d["t0"] * FPS))


def main():
    import lib
    argv = sys.argv[sys.argv.index("--") + 1:]
    nome, pasta = argv[0], argv[1]
    k = float(argv[argv.index("--scale") + 1]) if "--scale" in argv else 0.5
    smp = int(argv[argv.index("--samples") + 1]) if "--samples" in argv else 10
    N = quadros(nome)
    lib.reset(int(1080 * k), int(1920 * k), FPS, smp)
    sc = bpy.context.scene; sc.frame_start, sc.frame_end = 1, N
    ST.SHOTS[nome]["fn"]()
    if nome in ANIM:
        ANIM[nome](N)
    for H in list(REG.values()):                                     # quem o plano não animou continua vivo
        if H.raiz.animation_data is None:
            parado(H, N)
    if sc.camera.animation_data is None:
        camera_viva(N, frente=0.08, mao=0.5)
    cg = bpy.data.objects.get("cogumelo")
    if cg is not None:
        import objetos3d_abrigo_b as O3B
        t0 = int(round(ST.SHOTS[nome]["t0"] * FPS)) / FPS
        for f in range(1, N + 1, 2):
            O3B.cogumelo_em(cg, t0 + (f - 1) / FPS, f)
    if "--mede" in argv:
        t = tranco(N)
        por = {}
        for nm, i, f, v in t:
            por.setdefault(nm, []).append(f)
        print(f"TRANCO {nome}: {len(t)} em {len(por)} canais" + ("  " + ", ".join(f"{k}:{len(v)}" for k, v in sorted(por.items(), key=lambda q: -len(q[1]))[:4]) if por else ""))
        if "--suaviza" in argv:
            suaviza(N); t2 = tranco(N); print(f"   depois de suavizar: {len(t2)}")
        return
    if "--sem-suaviza" not in argv:
        suaviza(N, sigma=SIGMA)
    if "--colisao" in argv:                                          # pedido de 25/10: "não pode ficar um objeto entrando no outro"
        confere(sc, N, nome); return
    sc.render.use_motion_blur = True; sc.render.motion_blur_shutter = 0.5
    sc.render.image_settings.file_format = "PNG"
    out = os.path.join(pasta, nome); os.makedirs(out, exist_ok=True)
    if "--quadros" in argv:
        for f in [N if x == "N" else (N + 1) // 2 if x == "M" else int(x) for x in argv[argv.index("--quadros") + 1].split(",")]:
            sc.frame_set(f); sc.render.filepath = os.path.join(out, f"q{f:04d}.png"); bpy.ops.render.render(write_still=True)
    else:
        sc.render.filepath = out + "/"
        bpy.ops.render.render(animation=True)
    print("OK", nome, N)


if __name__ == "__main__":
    main()
