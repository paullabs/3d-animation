"""Animação de verdade da parte 2 de "O abrigo" (v3, 26/10/2026), plano a plano, por cima dos cenários do story_abrigo2.py.
Crítica do Paulo ao v2: "o take quando a coisa sai do escuro não tem nada a ver; tem que pegar de novo uma câmera deles lá com o bicho aparecendo;
mostrar o bicho de uma vez não é legal; ele pula de forma escrota e do nada o clima muda; aos 12, 13, 15 e 20 s não tem nada acontecendo;
a câmera de 1:20 está desfocada; já animar de fato; pensar como artista".
Cada função ACAO[id](N) monta o cenário, os bonecos e a câmera e grava as chaves de todos os quadros (o anim_abrigo2.py só renderiza).
- os três ficam no vão do abrigo; o monstro sobe DEVAGAR de trás do entulho à direita, visto primeiro desfocado atrás deles, depois por cima do ombro;
- o pulo tem agachamento (antecipação), impulso, arco e queda; o Zé se protege e cai para trás;
- a fuga tem passada de corrida de verdade e sempre alguém atrás (o monstro sobre o Zé, os outros saindo)."""
import math, random
import bpy
from mathutils import Vector
import lib
from lib import key, empty
import cena
import story_abrigo2 as S
import story3_abrigo as S3
import story_abrigo as SA
import objetos3d_abrigo as O3, objetos3d_abrigo2 as O2, ambiente_noite as AN
from heroi3d import corrida, _monotona

BY = S.BY
FPS = 24
ACAO = {}


def acao(ids):
    def deco(fn):
        for i in ids.split():
            ACAO[i] = fn
        return fn
    return deco


# ---------------------------------------------------------------- curvas
def lerp(a, b, u):
    return a + (b - a) * u


def suave(u):
    u = min(max(u, 0.0), 1.0); return u * u * (3 - 2 * u)


def faixa(f, fa, fb):
    return min(max((f - fa) / max(1e-6, fb - fa), 0.0), 1.0)


def costas(u):
    """easeOutBack: passa um pouco do ponto e assenta"""
    c1 = 1.4; c3 = c1 + 1; u = min(max(u, 0.0), 1.0)
    return 1 + c3 * (u - 1) ** 3 + c1 * (u - 1) ** 2


def ruido(t, seed, amp):
    r = random.Random(seed)
    return amp * sum(a * math.sin(2 * math.pi * fr * t + r.uniform(0, 6.28)) for fr, a in ((0.37, 0.55), (0.71, 0.3), (1.13, 0.15)))


def sombra(h):
    h.sombra = bpy.data.objects.get(h.nome[:-4] + "_sb") if h.nome.endswith("_inv") else None
    return h


# ---------------------------------------------------------------- câmera
def camera(N, chaves, mao=1.0, seed=1, tranco=(), passo_corrida=0.0, creep=0.045):
    """chaves = [(quadro, loc, alvo, lente, ponto_de_foco, fstop[, roll])]: a câmera passa pelas chaves numa curva contínua (cúbica monótona, sem parar);
    o foco segue o ponto (distância real), a mão balança devagar; tranco = quadros de impacto; passo_corrida = altura do balanço de quem corre (m)"""
    mao = mao * 0.4                                                        # v5 (27/10): "movimento amador, nada tenso": menos tremor de mão, a câmera é firme e a tensão vem do ritmo
    c0 = chaves[0]
    cam = S.C(c0[1], c0[2], c0[3], c0[5], foco=c0[4], roll=(c0[6] if len(c0) > 6 else 0.0))
    def canal(i, k=None):
        return [(ch[0], (ch[i][k] if k is not None else ch[i])) for ch in chaves]
    L = [canal(1, k) for k in range(3)]; A = [canal(2, k) for k in range(3)]; F = [canal(4, k) for k in range(3)]
    LE, FS = canal(3), canal(5)
    RO = [(ch[0], ch[6] if len(ch) > 6 else 0.0) for ch in chaves]
    for f in range(1, N + 1):
        t = (f - 1) / FPS
        loc = Vector([_monotona(L[k], f) for k in range(3)])
        alvo = Vector([_monotona(A[k], f) for k in range(3)])
        fp = Vector([_monotona(F[k], f) for k in range(3)])
        dirv = (alvo - loc)
        if dirv.length > 0.2 and creep:                                    # espreita: a câmera avança devagar em direção ao assunto durante o plano todo
            loc = loc + dirv.normalized() * creep * dirv.length * ((f - 1) / max(1, N - 1))
        loc += Vector((ruido(t, seed, 0.004 * mao), ruido(t, seed + 1, 0.003 * mao), ruido(t, seed + 2, 0.004 * mao)))
        if passo_corrida:
            loc.z += passo_corrida * abs(math.sin(math.pi * t * 2.6)); loc.x += passo_corrida * 0.5 * math.sin(math.pi * t * 1.3)
        d = 0.0
        for fi in tranco:
            u = f - fi
            if 0 <= u < 10:
                d += 0.02 * math.exp(-u / 2.4) * math.cos(u * 1.5)
        loc.z += d
        q = (alvo - loc).to_track_quat("-Z", "Y")
        e = q.to_euler()
        roll = math.radians(_monotona(RO, f)) + math.radians(ruido(t, seed + 3, 0.25 * mao)) + d * 2.0
        from mathutils import Matrix
        m = q.to_matrix() @ Matrix.Rotation(roll, 3, "Z")
        cam.rotation_euler = m.to_euler()
        cam.location = loc
        cam.data.lens = _monotona(LE, f)
        cam.data.dof.focus_distance = max(0.05, (fp - loc).length)
        cam.data.dof.aperture_fstop = _monotona(FS, f)
        key(cam, "location", f, "LINEAR"); key(cam, "rotation_euler", f, "LINEAR")
        cam.data.keyframe_insert("lens", frame=f); cam.data.dof.keyframe_insert("focus_distance", frame=f); cam.data.dof.keyframe_insert("aperture_fstop", frame=f)
    return cam


# ---------------------------------------------------------------- o Sem-Osso vivo (molas, membros moles que dobram, esticar e achatar, gosma que pulsa)
MOLAS_SO = dict(cabeca=(3, 2.4, 0.42), tronco=(2, 2.6, 0.5), ombro=(3, 3.2, 0.45), cotovelo=(4, 3.6, 0.4), pos=(1, 2.6, 0.8), quadril=(2, 3.0, 0.55), rot=(1, 2.6, 0.8))


def membros_moles(h):
    out = []
    for s in ("bracomoleF", "bracomoleB", "pernamoleF", "pernamoleB"):
        o = bpy.data.objects.get(f"{h.nome}_{s}")
        if o is None:
            continue
        if "dobra" not in o.modifiers:
            sub = o.modifiers.new("sub", "SUBSURF"); sub.levels = 1; sub.render_levels = 2
            d = o.modifiers.new("dobra", "SIMPLE_DEFORM"); d.deform_method = "BEND"; d.deform_axis = "Z"; d.angle = 0.0
            o.modifiers.move([m for m in o.modifiers].index(sub), 0); o.modifiers.move([m for m in o.modifiers].index(d), 1)
        out.append(o.modifiers["dobra"])
    return out


def sem_osso_vivo(h, N, chaves, estica=None, dobra=None, base_pulso=None, tomba=(9.0, -24.0), seed=7, molas=None):
    """chaves no formato do Heroi3D.anima; estica(f) -> fator vertical (1 = normal); dobra(f) -> 4 ângulos (graus) dos membros moles;
    base_pulso(f) -> 0..1 (a base de gosma alonga quando ele arrasta); tomba = (tronco caído de lado, cabeça tombada) em graus"""
    h.nome = h.nome if hasattr(h, "nome") else h.raiz.name
    mm = membros_moles(h)
    m = dict(MOLAS_SO); m.update(molas or {})
    h.anima(chaves, 1, N, vida=1.5, seed=seed, mola=True, molas=m)
    base = bpy.data.objects.get(h.nome + "_base")
    gotas = [bpy.data.objects.get(h.nome + n) for n in ("_pingoF", "_pingoB", "_queixo_gota")]
    gotas = [g for g in gotas if g]
    sc = bpy.context.scene
    rnd = random.Random(seed)
    ph = rnd.uniform(0, 6.28)
    for f in range(1, N + 1):
        sc.frame_set(f)
        t = f / FPS
        h.tronco.rotation_euler.y = math.radians(tomba[0] + 3 * math.sin(t * 1.7 + ph)); key(h.tronco, "rotation_euler", f, "LINEAR")
        h.cabeca.rotation_euler.y = math.radians(tomba[1] + 6 * math.sin(t * 1.1 + ph)); key(h.cabeca, "rotation_euler", f, "LINEAR")
        sz = estica(f) if estica else 1.0 + 0.03 * math.sin(t * 3.1 + ph)
        sx = 1.0 / math.sqrt(max(0.2, sz))
        h.raiz.scale = (sx, sx, sz); key(h.raiz, "scale", f, "LINEAR")
        ang = dobra(f) if dobra else [18 * math.sin(t * 2.2 + ph) + 6, -18 * math.sin(t * 2.0 + ph) - 6, 12 * math.sin(t * 1.6 + ph), -12 * math.sin(t * 1.8 + ph)]
        for d, a in zip(mm, ang):
            d.angle = math.radians(a); d.keyframe_insert("angle", frame=f)
        p = base_pulso(f) if base_pulso else 0.0
        if base:
            base.scale = (1.0 + 0.25 * p, 1.0 + 0.5 * p, 1.0); key(base, "scale", f, "LINEAR")
        for k, g in enumerate(gotas):
            g.scale = (1, 1, 1.0 + 0.25 * math.sin(f / 4.0 + k * 2.0) + 0.2 * p); key(g, "scale", f, "LINEAR")
    return h


def boca_abre(h, N, chaves):
    """a boca (mandíbula pendurada) abre e fecha: chaves = [(quadro, fator)]"""
    b = h.boca
    s0 = tuple(b.scale)
    for f in range(1, N + 1):
        k = _monotona(chaves, f)
        b.scale = (s0[0], s0[1], s0[2] * k); key(b, "scale", f, "LINEAR")


def pos_cabeca(h):
    bpy.context.view_layer.update()
    return h.cabeca.matrix_world.translation.copy()


# ---------------------------------------------------------------- bonecos
def vivo(h, N, pose, seed=3, vida=1.0, **extra):
    """parado, mas vivo (a pose de agora em todos os quadros, com respiração do anima)"""
    P = dict(pose); P.update(extra)
    sombra(h).anima([(1, P), (N, P)], 1, N, vida=vida, seed=seed)


def corre(h, N, de, ate, rot, fase=0, ciclo=12, inclina=13, arranque=0.0, freia=0.0, f0=1, f1=None):
    f1 = N if f1 is None else f1
    por = [(b - a) / max(1, f1 - f0) for a, b in zip(de, ate)]
    d0 = tuple(a - p * fase for a, p in zip(de, por))
    ch = corrida(f0 - fase, f1, d0, ate, rot=rot, ciclo=ciclo, inclina=inclina, arranque=arranque, freia=freia)
    sombra(h).anima(ch, 1, N, vida=0.4, seed=int(abs(de[0] * 7 + de[1] * 3)) % 97, molas=dict(pos=(0, 24.0, 1.0), rot=(0, 24.0, 1.0)))


PARADO = dict(ombro=(-3, 5), cotovelo=(-10, -10), abre=(4, 4))
RITA_SUETER = dict(ombro=(5, -40), cotovelo=(-10, -60), abre=(4, 4))


def trio_vivo(olhar=0.0, ze_x=-0.6, ze_y=None):
    p, ze, eu, ri = S.trio(olhar=olhar, ze_x=ze_x, ze_y=ze_y)
    return ze, eu, ri


def segue_sueter(ri, N):
    """o suéter que a Rita aperta acompanha a mão dela (foi posto no lugar da mão no quadro 1)"""
    su = bpy.data.objects.get("sueter_fim")
    if su is None:
        return
    sc = bpy.context.scene; sc.frame_set(1); bpy.context.view_layer.update()
    m0 = ri.punho["B"].matrix_world.translation.copy(); l0 = su.location.copy()
    for f in range(1, N + 1):
        sc.frame_set(f); bpy.context.view_layer.update()
        su.location = l0 + (ri.punho["B"].matrix_world.translation - m0); key(su, "location", f, "LINEAR")


def rua_aberta(bici=True):
    """a mesma rua do trio (porta aberta, luz âmbar, esqueletos na porta, a bicicleta caída): o ataque e a fuga não podem trocar de cenário"""
    p = S3.rua3(morta=True, aberta=0.9, carros=True)
    S3.esqueletos_porta()
    if bici:
        b = O3.bicicleta3d("bici", (-1.9, BY - 2.6, 0.0), 1.0, cor="#6a665a", poeira=0.85); b.rotation_euler.z = math.radians(80)
    return p


# ====================================================================== 1. a coisa sai do escuro
@acao("1C")
def a1C(N):
    """eles ouvem: os três viram a cabeça para a direita, um depois do outro (o Zé primeiro), e o corpo vem atrás"""
    ze, eu, ri = trio_vivo(0.0)
    for h, atraso, sd, base in ((ze, 2, 1, PARADO), (eu, 5, 2, PARADO), (ri, 7, 3, RITA_SUETER)):
        a = dict(base, olha=0.0, giro=0.0); b = dict(base, olha=34.0, giro=10.0, tronco=3.0)
        sombra(h).anima([(1, a), (1 + atraso, a), (min(N, 9 + atraso), b), (N, b)], 1, N, vida=0.8, seed=sd)
    for h, ex in ((ze, dict(boca="triste", lid=0.68)), (eu, dict(boca="triste", lid=0.68)), (ri, dict(boca="triste", lid=0.68))):
        h.expressao([(1, ex), (8, dict(boca="o", lid=0.05, brow=0.6, olhos=1.12))], 1, N, piscar=False)
    segue_sueter(ri, N)
    camera(N, [(1, (0.0, BY - 4.6, 1.4), (0.05, BY - 1.1, 1.35), 60, (0.05, BY - 1.1, 1.35), 2.8), (N, (0.0, BY - 4.35, 1.4), (0.08, BY - 1.1, 1.35), 60, (0.05, BY - 1.1, 1.35), 2.8)], mao=0.6)


SUSTO = dict(boca="o", lid=0.0, brow=0.7, olhos=1.15)
SUSTO_R = dict(boca="o", lid=0.0, brow=0.7)


@acao("1D")
def a1D(N):
    """os três de frente, ainda olhando para a direita; ATRÁS deles, no entulho desfocado, uma cabeça escura sobe devagar (ninguém a vê ainda)"""
    ze, eu, ri = trio_vivo(34.0)
    S.entulho_dir()
    for h, sd, base in ((ze, 1, PARADO), (eu, 2, PARADO), (ri, 3, RITA_SUETER)):
        a = dict(base, olha=34.0, giro=10.0, tronco=3.0)
        b = dict(a, tronco=6.0, olha=38.0)
        sombra(h).anima([(1, a), (N, b)], 1, N, vida=1.0, seed=sd)
        h.expressao([(1, SUSTO), (N, SUSTO)], 1, N, piscar=False)
    segue_sueter(ri, N)
    so = S.monstro(3.35, BY - 1.55, rot=-110, curva=1.4)
    sem_osso_vivo(so, N, [(1, dict(pos=(3.35, BY - 1.55, -1.25), rot=-110, tronco=30, cabeca=-20, alt=0.75)),
                          (N, dict(pos=(3.35, BY - 1.55, -0.6), rot=-112, tronco=24, cabeca=-8, alt=0.75))],
                  estica=lambda f: 1.0 + 0.12 * suave(f / N))
    camera(N, [(1, (-1.3, BY - 4.3, 1.3), (1.0, BY - 1.45, 1.05), 24, (0.05, BY - 1.1, 1.3), 2.8),
               (N, (-1.15, BY - 4.05, 1.3), (1.1, BY - 1.45, 1.05), 24, (0.05, BY - 1.1, 1.3), 2.8)], mao=0.7)


@acao("1E")
def a1E(N):
    """por cima do ombro deles: o monstro sai de trás do entulho, esticado e mole; o foco passa da cabeça do narrador para ele"""
    ze, eu, ri = trio_vivo(34.0)
    S.entulho_dir()
    try:
        S3.sem_halo_do_bunker()
    except Exception:
        pass
    for h, sd, base in ((ze, 1, PARADO), (eu, 2, PARADO), (ri, 3, RITA_SUETER)):
        a = dict(base, olha=38.0, giro=10.0, tronco=6.0)
        b = dict(a, tronco=-4.0, olha=40.0)                                  # recuam um pouco
        sombra(h).anima([(1, a), (10, a), (N, b)], 1, N, vida=1.0, seed=sd)
    so = S.monstro(3.35, BY - 1.55, rot=-110, curva=1.4)
    F1 = N - 2
    sem_osso_vivo(so, N, [(1, dict(pos=(3.35, BY - 1.55, -0.6), rot=-112, tronco=24, cabeca=-8, alt=0.75, ombro=(-10, -10))),
                          (F1, dict(pos=(3.3, BY - 1.6, -0.12), rot=-108, tronco=16, cabeca=4, alt=0.77, ombro=(-40, -8), cotovelo=(-20, -10))),
                          (N, dict(pos=(3.3, BY - 1.6, -0.1), rot=-108, tronco=16, cabeca=6, alt=0.77, ombro=(-44, -8), cotovelo=(-24, -10)))],
                  estica=lambda f: 1.0 + 0.28 * math.sin(math.pi * faixa(f, 1, F1)) * (1 - 0.3 * faixa(f, 1, F1)),
                  dobra=lambda f: [40 * (1 - faixa(f, 1, N)) * math.sin(f / 3.0), -40 * (1 - faixa(f, 1, N)) * math.sin(f / 2.6 + 1), 20, -20])
    boca_abre(so, N, [(1, 1.0), (N - 6, 1.0), (N, 1.35)])
    fp = [(1, (0.05, BY - 1.1, 1.45)), (8, (0.05, BY - 1.1, 1.45)), (16, (3.3, BY - 1.6, 1.0)), (N, (3.3, BY - 1.6, 1.1))]
    camera(N, [(f, (-0.55, BY - 0.25, 1.62), (3.1, BY - 1.85, 0.95), 35, p, 2.8) for f, p in fp[:1]] +
           [(f, (-0.55 + 0.06 * (f / N), BY - 0.25 - 0.08 * (f / N), 1.62), (3.1, BY - 1.85, 0.95 + 0.15 * (f / N)), 35, p, 2.8) for f, p in fp[1:]], mao=0.6)


@acao("1F")
def a1F(N):
    """ele desce do entulho em direção a eles, aos trancos (desliza, para); câmera na altura deles, avançando devagar"""
    ze, eu, ri = trio_vivo(34.0)
    S.entulho_dir()
    for h in (ze, eu, ri):
        h.raiz.hide_render = False
    so = S.monstro(3.2, BY - 1.7, rot=-105, curva=1.0)
    ch = []
    for f in range(1, N + 1, 2):
        u = faixa(f, 1, N); s = math.sin(2 * math.pi * u * 1.3)
        v = suave(u) * 0.55 + 0.1 * max(0, s)
        ch.append((f, dict(pos=(3.2 - 0.75 * v, BY - 1.7 - 0.25 * v, 0.28 * (1 - suave(faixa(f, 1, N * 0.7)))), rot=-105 - 6 * s, tronco=16 + 10 * max(0, s),
                           cabeca=6 - 10 * s, alt=0.77, ombro=(-40 + 25 * s, -10 - 25 * s), cotovelo=(-20, -24), quadril=(-20 * s, 20 * s), joelho=(10 + 30 * max(0, s), 10 + 30 * max(0, -s)))))
    sem_osso_vivo(so, N, ch, base_pulso=lambda f: max(0.0, math.sin(2 * math.pi * faixa(f, 1, N) * 1.3)))
    v = O3.cilindro("verg_fg", 0.012, 1.0, O3.M("#2c2b2a", "#1e1d1c", "#4a4846"), None, (1.15, BY - 4.6, 1.15), seg=10)
    v.rotation_euler = (math.radians(80), math.radians(-14), math.radians(10))
    camera(N, [(1, (1.0, BY - 5.6, 1.3), (2.9, BY - 1.8, 1.2), 50, (2.95, BY - 1.75, 1.2), 4.0),
               (N, (1.1, BY - 5.25, 1.3), (2.7, BY - 1.85, 1.2), 50, (2.6, BY - 1.9, 1.2), 4.0)], mao=0.7)


@acao("1F2")
def a1F2(N):
    """o rosto, devagar: a cabeça tomba, a mandíbula pendura e abre; aproximação de poucos centímetros (nada de zoom rápido)"""
    ze, eu, ri = trio_vivo(36.0)
    so = S.monstro(2.4, BY - 1.95, rot=-98, curva=1.0)
    sem_osso_vivo(so, N, [(1, dict(pos=(2.4, BY - 1.95, 0.0), rot=-98, tronco=18, cabeca=-4, alt=0.77, ombro=(-30, -10), cotovelo=(-20, -20))),
                          (N, dict(pos=(2.33, BY - 1.97, 0.0), rot=-96, tronco=22, cabeca=8, alt=0.76, ombro=(-34, -12), cotovelo=(-24, -20)))],
                  tomba=(9.0, -30.0))
    boca_abre(so, N, [(1, 1.0), (6, 1.0), (N, 1.45)])
    cz = pos_cabeca(so)
    camera(N, [(1, (cz.x - 1.55, cz.y - 0.55, cz.z + 0.02), tuple(cz), 85, tuple(cz), 2.8),
               (N, (cz.x - 1.4, cz.y - 0.5, cz.z + 0.0), tuple(cz + Vector((0, 0, -0.02))), 85, tuple(cz), 2.8)], mao=0.5)


@acao("1G")
def a1G(N):
    """o Zé dá dois passos para a frente e abre o braço na frente dos outros dois; o monstro, ao fundo, continua vindo"""
    ze, eu, ri = trio_vivo(36.0)
    S.entulho_dir()
    a = dict(PARADO, pos=(-0.6, BY - 1.1, 0), rot=0, olha=36.0, giro=10.0)
    m = dict(pos=(0.0, BY - 1.45, 0), rot=50, quadril=(-30, 20), joelho=(40, 10), ombro=(-20, 20), cotovelo=(-20, -10), tronco=8, abre=(10, 10))
    b = dict(pos=(0.6, BY - 1.75, 0), rot=80, quadril=(10, -10), joelho=(12, 12), ombro=(-5, -70), cotovelo=(-10, -14), abre=(8, 62), tronco=4, olha=0.0)
    sombra(ze).anima([(1, a), (3, a), (7, m), (11, b), (N, b)], 1, N, vida=0.6, seed=1, mola=True)
    ze.expressao([(1, SUSTO), (N, dict(boca="reta", lid=0.0, brow=-0.6))], 1, N, piscar=False)
    for h, sd, base in ((eu, 2, PARADO), (ri, 3, RITA_SUETER)):
        vivo(h, N, dict(base, olha=36.0, giro=10.0, tronco=-3.0), seed=sd)
    segue_sueter(ri, N)
    so = S.monstro(2.4, BY - 1.98, rot=-96, curva=1.0)
    sem_osso_vivo(so, N, [(1, dict(pos=(2.33, BY - 1.97, 0.0), rot=-96, tronco=22, cabeca=8, alt=0.76, ombro=(-34, -12), cotovelo=(-24, -20))),
                          (N, dict(pos=(2.2, BY - 2.0, 0.0), rot=-94, tronco=26, cabeca=12, alt=0.74, ombro=(-40, -18), cotovelo=(-28, -24)))])
    camera(N, [(1, (-2.0, BY - 3.9, 1.45), (1.0, BY - 1.75, 1.15), 35, (0.6, BY - 1.75, 1.2), 4.0),
               (N, (-1.85, BY - 3.75, 1.45), (1.1, BY - 1.8, 1.15), 35, (0.6, BY - 1.75, 1.2), 4.0)], mao=0.8)


@acao("1H")
def a1H(N):
    """rente ao chão, atrás das botas do Zé: o monstro se agacha, abre os braços e a base de gosma se espalha (a mola antes do pulo)"""
    ze, eu, ri = trio_vivo(30.0, ze_x=0.6, ze_y=BY - 1.75)
    S.entulho_dir()
    b = dict(pos=(0.6, BY - 1.75, 0), rot=80, quadril=(10, -10), joelho=(12, 12), ombro=(-5, -70), cotovelo=(-10, -14), abre=(8, 62), tronco=4)
    vivo(ze, N, b, seed=1, vida=0.6)
    for h, sd, base in ((eu, 2, PARADO), (ri, 3, RITA_SUETER)):
        vivo(h, N, dict(base, olha=30.0, giro=8.0, tronco=-3.0), seed=sd)
    so = S.monstro(2.2, BY - 2.0, rot=-94, curva=1.0)
    sem_osso_vivo(so, N, [(1, dict(pos=(2.2, BY - 2.0, 0.0), rot=-94, tronco=26, cabeca=12, alt=0.74, ombro=(-40, -18), cotovelo=(-28, -24))),
                          (N, dict(pos=(2.15, BY - 2.0, 0.0), rot=-92, tronco=52, cabeca=-34, alt=0.5, ombro=(-20, -20), abre=(48, 48), cotovelo=(-40, -40),
                                   quadril=(-50, -50), joelho=(80, 80)))],
                  estica=lambda f: 1.0 - 0.12 * suave(f / N), base_pulso=lambda f: 0.8 * suave(f / N))
    boca_abre(so, N, [(1, 1.3), (N, 1.6)])
    camera(N, [(1, (-0.05, BY - 1.2, 0.17), (1.9, BY - 2.15, 0.45), 18, (2.0, BY - 2.0, 0.5), 5.6),
               (N, (0.12, BY - 1.32, 0.17), (1.95, BY - 2.12, 0.5), 18, (2.0, BY - 2.0, 0.5), 5.6)], mao=0.6)


@acao("2A")
def a2A(N):
    """o pulo, de lado e aberto: agacha mais (antecipação), estica no impulso, voa num arco com os braços à frente e as pernas moles para trás;
    o Zé recua o corpo e levanta os braços"""
    rua_aberta()
    ze = SA.ator3("ze", "ze", 0.6, BY - 1.75, rot=80, rosto=SUSTO_R)
    eu = SA.ator3("eu", "eu", 0.05, BY - 1.1, rot=50, rosto=SUSTO_R); ri = SA.ator3("rita", "rita", 0.7, BY - 1.1, rot=40, rosto=SUSTO_R)
    S.entulho_dir()
    FL = int(round((8.64 - 8.2) * FPS)) + 1                                  # o impulso cai na palavra "pulou"
    za = dict(pos=(0.6, BY - 1.75, 0), rot=80, quadril=(10, -10), joelho=(12, 12), ombro=(-5, -70), cotovelo=(-10, -14), abre=(8, 62), tronco=4)
    zb = dict(pos=(0.5, BY - 1.72, 0), rot=80, quadril=(-14, 18), joelho=(26, 10), ombro=(-120, -125), cotovelo=(-70, -64), abre=(18, 14), tronco=-16, cabeca=-14)
    sombra(ze).anima([(1, za), (FL, za), (N, zb)], 1, N, vida=0.5, seed=1)
    for h, sd in ((eu, 2), (ri, 3)):
        vivo(h, N, dict(PARADO, olha=10.0, tronco=-6.0), seed=sd)
    so = S.monstro(2.15, BY - 2.0, rot=-92, curva=1.0)
    agacha = dict(pos=(2.15, BY - 2.0, 0.0), rot=-92, tronco=58, cabeca=-38, alt=0.46, ombro=(-16, -16), abre=(52, 52), cotovelo=(-44, -44), quadril=(-55, -55), joelho=(88, 88))
    impulso = dict(pos=(1.95, BY - 1.95, 0.25), rot=-92, tronco=40, cabeca=-20, alt=0.8, ombro=(-150, -150), abre=(20, 20), cotovelo=(-10, -10), quadril=(30, 30), joelho=(10, 10))
    voo = dict(pos=(1.35, BY - 1.85, 0.62), rot=-92, tronco=42, cabeca=-24, alt=0.8, ombro=(-125, -135), abre=(40, 36), cotovelo=(-34, -40), quadril=(-55, -40), joelho=(95, 85))
    ch = [(1, dict(agacha, alt=0.5, tronco=52)), (FL - 1, agacha), (FL + 2, impulso), (N, voo)]
    sem_osso_vivo(so, N, ch, molas=dict(pos=(0, 6.0, 0.9), rot=(0, 6.0, 0.9)),
                  estica=lambda f: 0.86 if f < FL else (1.22 if f < FL + 3 else 1.06),
                  dobra=lambda f: [10, -10, 20 * faixa(f, FL, N), -25 * faixa(f, FL, N)],
                  base_pulso=lambda f: 0.9 if f < FL else 0.0)
    boca_abre(so, N, [(1, 1.6), (FL, 1.6), (N, 2.0)])
    camera(N, [(1, (1.5, BY - 4.6, 0.9), (1.5, BY - 1.9, 0.95), 28, (1.7, BY - 1.9, 1.0), 5.6),
               (N, (1.35, BY - 4.45, 0.95), (1.2, BY - 1.85, 1.0), 28, (1.2, BY - 1.85, 1.0), 5.6)], mao=0.8)


@acao("2B")
def a2B(N):
    """o impacto, de perto e do lado de quem conta: ela chega do ar, bate no Zé e os dois caem para trás, para fora do quadro; a câmera treme"""
    rua_aberta(); S.entulho_dir()
    ze = SA.ator3("ze", "ze", 0.5, BY - 1.72, rot=80, rosto=SUSTO_R)
    FI = 5
    zb = dict(pos=(0.5, BY - 1.72, 0), rot=80, quadril=(-14, 18), joelho=(26, 10), ombro=(-120, -125), cotovelo=(-70, -64), abre=(18, 14), tronco=-16, cabeca=-14)
    zc = dict(zb, pos=(-0.15, BY - 1.62, 0.05), rot=(-82, 0, 80), quadril=(-40, -20), joelho=(50, 30), ombro=(-150, -100), cabeca=10)
    sombra(ze).anima([(1, zb), (FI, zb), (FI + 9, zc), (N, zc)], 1, N, vida=0.3, seed=1, molas=dict(rot=(0, 4.0, 0.7), pos=(0, 4.0, 0.7)))
    so = S.monstro(1.4, BY - 1.82, z=0.55, rot=-92, curva=1.0)
    voo = dict(pos=(1.3, BY - 1.82, 0.55), rot=-92, tronco=42, cabeca=-24, alt=0.8, ombro=(-125, -135), abre=(40, 36), cotovelo=(-34, -40), quadril=(-55, -40), joelho=(95, 85))
    bate = dict(voo, pos=(0.85, BY - 1.75, 0.35), tronco=60, ombro=(-120, -110))
    caiu = dict(bate, pos=(0.05, BY - 1.62, 0.25), rot=(62, 0, -92), tronco=30, ombro=(-90, -80), quadril=(10, 20))
    sem_osso_vivo(so, N, [(1, voo), (FI, bate), (FI + 10, caiu), (N, caiu)], molas=dict(pos=(0, 5.0, 0.8), rot=(0, 5.0, 0.8)),
                  estica=lambda f: 0.82 if FI <= f < FI + 3 else 1.0)
    boca_abre(so, N, [(1, 2.0), (N, 1.6)])
    camera(N, [(1, (2.0, BY - 3.7, 1.35), (1.0, BY - 1.75, 1.1), 35, (0.8, BY - 1.75, 1.1), 4.0),
               (FI + 6, (1.9, BY - 3.6, 1.3), (0.7, BY - 1.7, 0.8), 35, (0.5, BY - 1.7, 0.8), 4.0),
               (N, (1.85, BY - 3.55, 1.25), (0.45, BY - 1.65, 0.55), 35, (0.3, BY - 1.65, 0.5), 4.0)], mao=1.4, tranco=(FI, FI + 9))


# ====================================================================== 2. a fuga (corrida de verdade; sempre alguém atrás)
def ze_no_chao(x=0.0, y=BY - 1.62):
    """o Zé caído na frente do abrigo e o monstro por cima dele (o que fica para trás na fuga)"""
    ze = SA.ator3("ze", "ze", x, y, rot=80, rosto=SUSTO_R)
    ze.pose(quadril=(-40, -20), joelho=(50, 30), ombro=(-150, -100), cotovelo=(-60, -60), abre=(20, 20), rot=(-82, 0, 80), pos=(x, y, 0.05))
    so = O2.sem_osso("sz", "padeira", (x + 0.2, y, 0.25), rot=-92, curva=1.0, seed=2)
    so.pose(pos=(x + 0.2, y, 0.25), rot=(62, 0, -92), tronco=30, cabeca=-30, alt=0.8, ombro=(-90, -80), abre=(26, 26), cotovelo=(-14, -20), quadril=(10, 20), joelho=(30, 40))
    return ze, so


def pulsa_sobre(so, N, seed=4):
    """o monstro sobre o Zé se mexe (cabeça que mergulha, ombros que pulsam)"""
    P = dict(getattr(so, "_ultima", {}) or {})
    ch = []
    for f in range(1, N + 1, 3):
        s = math.sin(f / 3.2)
        ch.append((f, dict(pos=tuple(so.raiz.location), rot=(62, 0, -92), tronco=30 + 8 * s, cabeca=-30 + 12 * s, alt=0.8, ombro=(-90 + 15 * s, -80 - 12 * s),
                           abre=(26, 26), cotovelo=(-14, -20), quadril=(10, 20), joelho=(30, 40))))
    sem_osso_vivo(so, N, ch, seed=seed)


@acao("2D")
def a2D(N):
    """de trás: eles disparam rua abaixo (para baixo na tela); o narrador puxa a Rita pela mão"""
    rua_aberta(); S.entulho_dir()
    ze, so = ze_no_chao()
    pulsa_sobre(so, N)
    eu = SA.ator3("eu", "eu", 0.1, BY - 2.0, rot=0, rosto=SUSTO_R); ri = SA.ator3("rita", "rita", 0.9, BY - 2.2, rot=0, rosto=SUSTO_R)
    corre(eu, N, (0.1, BY - 2.2, 0), (0.15, BY - 5.6, 0), 0, fase=3, arranque=0.35)
    corre(ri, N, (0.95, BY - 2.0, 0), (0.95, BY - 5.2, 0), 0, fase=7, arranque=0.45, ciclo=13)
    camera(N, [(1, (0.4, BY - 0.2, 1.7), (0.5, BY - 6.0, 1.0), 16, (0.5, BY - 3.0, 1.0), 8.0),
               (N, (0.4, BY - 2.4, 1.6), (0.5, BY - 8.5, 1.0), 16, (0.5, BY - 5.2, 1.0), 8.0)], mao=1.5, passo_corrida=0.02)


@acao("2E")
def a2E(N):
    """de frente, teleobjetiva: os dois vêm correndo para a câmera; ATRÁS, no vão iluminado do abrigo, o monstro sobre o Zé e um segundo saindo do entulho"""
    rua_aberta(); S.entulho_dir()
    ze, so = ze_no_chao()
    pulsa_sobre(so, N)
    s2 = S.monstro(3.1, BY - 1.6, rot=-150, curva=1.2)
    sem_osso_vivo(s2, N, [(1, dict(pos=(3.1, BY - 1.6, -0.5), rot=-150, tronco=30, cabeca=-20, alt=0.75)), (N, dict(pos=(3.0, BY - 1.75, 0.0), rot=-160, tronco=20, cabeca=0, alt=0.77))],
                  estica=lambda f: 1.0 + 0.2 * math.sin(math.pi * f / N), seed=9)
    eu = SA.ator3("eu", "eu", 0.0, BY - 5.0, rot=0, rosto=SUSTO_R); ri = SA.ator3("rita", "rita", 0.9, BY - 5.3, rot=0, rosto=SUSTO_R)
    corre(eu, N, (0.0, BY - 5.0, 0), (0.05, BY - 11.2, 0), 0, fase=2)
    corre(ri, N, (0.9, BY - 5.4, 0), (0.85, BY - 11.4, 0), 0, fase=6, ciclo=13)
    camera(N, [(1, (0.4, BY - 10.5, 1.4), (0.4, BY - 5.0, 1.2), 85, (0.45, BY - 5.2, 1.2), 4.0),
               (N, (0.4, BY - 16.0, 1.4), (0.4, BY - 11.0, 1.15), 85, (0.45, BY - 11.3, 1.2), 4.0)], mao=1.2)


@acao("3A")
def a3A(N):
    """do alto: os dois descendo a rua; atrás, longe, duas formas escuras já vêm atrás deles"""
    rua_aberta(bici=False)
    eu = SA.ator3("eu", "eu", 0.2, 11.0, rot=0); ri = SA.ator3("rita", "rita", 1.0, 11.3, rot=0)
    corre(eu, N, (0.2, 11.0, 0), (0.25, 6.0, 0), 0, fase=3)
    corre(ri, N, (1.0, 11.3, 0), (0.95, 6.3, 0), 0, fase=7, ciclo=13)
    for k, (x, y) in enumerate(((0.6, 15.6), (-1.6, 14.4))):
        h = O2.sem_osso(f"sa{k}", ("padeira", "mercado")[k], (x, y, 0), rot=0.0, curva=1.0, seed=3 + k)
        ch = []
        for f in range(1, N + 1, 2):
            s = math.sin(2 * math.pi * (f / 18.0 + 0.3 * k)); v = f / N
            ch.append((f, dict(pos=(x + 0.15 * s, y - 2.6 * v - 0.2 * max(0, s), 0), rot=-8 * s, tronco=24 + 10 * max(0, s), cabeca=-10, alt=0.76,
                               ombro=(-20 + 25 * s, -20 - 25 * s), cotovelo=(-20, -20), quadril=(-24 * s, 24 * s), joelho=(10 + 30 * max(0, s), 10 + 30 * max(0, -s)))))
        sem_osso_vivo(h, N, ch, seed=5 + k)
    camera(N, [(1, (2.8, 1.5, 6.5), (0.4, 10.5, 0.6), 24, (0.4, 10.5, 0.8), 11.0),
               (N, (2.8, 3.0, 8.0), (0.4, 8.5, 0.6), 24, (0.4, 8.5, 0.8), 11.0)], mao=0.6)


@acao("3B")
def a3B(N):
    """baixo, atrás deles: os dois correm para dentro do sol que se põe; viram silhueta e as sombras compridas vêm até a câmera"""
    rua_aberta(bici=False); S.halo("sol", 0.5, -20.0, 2.4, 4.0, "#f6e2a8", 0.95)
    rnd = random.Random(11)
    for k in range(16):
        x = -16 + 2.2 * k + rnd.uniform(-0.6, 0.6); hh = rnd.uniform(2.5, 8)
        O3.caixa(f"sil{k}", (rnd.uniform(2.5, 4.5), 3.0, hh), O3.M("#14110e", "#14110e", "#14110e"), None, (x, -18.5, hh / 2), chanfro=0.0, contorno=0.0, rot=(0, rnd.uniform(-5, 5), 0))
    eu = SA.ator3("eu", "eu", 0.1, 5.2, rot=0); ri = SA.ator3("rita", "rita", 0.9, 5.4, rot=0)
    for h in (eu, ri):
        sb = cena.poly_mesh(h.nome + "_longa", [(-0.16, 0.0, 0.004), (0.16, 0.0, 0.004), (0.1, 4.2, 0.004), (-0.1, 4.2, 0.004)], cena.amat(h.nome + "_lm", "#0d0b09", 1.0, 0.55, None))
        sb.parent = h.raiz
    corre(eu, N, (0.1, 5.2, 0), (0.15, 0.4, 0), 0, fase=3)
    corre(ri, N, (0.9, 5.5, 0), (0.85, 0.8, 0), 0, fase=7, ciclo=13)
    camera(N, [(1, (0.45, 8.6, 0.55), (0.4, -20.0, 2.3), 50, (0.5, 4.5, 1.0), 4.0),
               (N, (0.45, 7.4, 0.6), (0.4, -20.0, 2.2), 50, (0.5, 1.5, 1.0), 4.0)], mao=0.6)


@acao("3C")
def a3C(N):
    """a padaria da padeira: os dois passam correndo na frente da câmera (borrados) e revelam a fachada com a vitrine escura"""
    S.noite_rica("tarde"); AN.padaria("pad", 3.4, 11.0); AN.poste("pl3", -1.2, 11.5, acesa=False)
    AN.carro("c3", -2.5, 7.0, rot=8, queimado=True); AN.lixeira("lx3", 0.2, 9.5); AN.caixote("cx4", 7.2, 9.6, 15, 2)
    AN.poca_agua("pq6", 3.0, 9.4, 2.0, 0.8, brilho=("#ffcf7a", 0.4), seed=4)
    eu = SA.ator3("eu", "eu", 5.6, 7.6, rot=-60); ri = SA.ator3("rita", "rita", 6.2, 8.2, rot=-60)
    corre(eu, N, (6.0, 7.2, 0), (1.2, 4.6, 0), -62, fase=2)
    corre(ri, N, (6.8, 7.9, 0), (2.0, 5.2, 0), -62, fase=6, ciclo=13)
    camera(N, [(1, (3.4, 3.4, 1.6), (3.6, 11.0, 1.8), 28, (3.4, 11.0, 1.8), 5.6),
               (N, (3.4, 4.3, 1.55), (3.4, 11.0, 1.75), 28, (3.4, 11.0, 1.75), 5.6)], mao=0.6)


@acao("3D")
def a3D(N):
    """do toldo rasgado pinga gosma na poça; a poça incha e sobe em corpo, esticada e fina, e assenta com um balanço (de boné grudado)"""
    S.noite_rica("tarde"); AN.poste("pl4", 1.6, 9.0, acesa=True)
    O3.caixa("toldo", (3.0, 1.4, 0.06), O3.M("#6a5a46", "#4a3e30"), None, (-1.5, 10.8, 2.4), chanfro=0.0, rot=(24, 0, 4))
    AN.caixote("cx3", -2.6, 9.6, 30, 2); AN.carro("c4", 4.5, 14.0, rot=-30)
    AN.poca_agua("pq4", -0.4, 9.2, 1.0, 0.6, brilho=("#ffcf7a", 0.4))
    pc = O2.poca("p", -0.1, 10.4, 0.55, 0.38, seed=3)
    O2.pingo("pg", None, (-1.2, 11.0, 2.2), comp=0.9, r=0.025)
    so = S.sem("so", "mercado", -0.1, 10.4, rot=0, curva=1.2, seed=8)
    FS = N - 4
    ch = []
    for f in range(1, N + 1, 2):
        u = faixa(f, 1, FS)
        ch.append((f, dict(pos=(-0.1, 10.4 - 0.15 * u, -1.15 + 1.15 * costas(u)), rot=10 * u, tronco=30 - 14 * suave(u), cabeca=-30 + 22 * u, alt=0.75,
                           ombro=(-10 - 20 * u, -6 - 20 * u), cotovelo=(-10, -14), abre=(10 * u, 10 * u))))
    sem_osso_vivo(so, N, ch, estica=lambda f: 1.0 + 0.4 * math.sin(math.pi * min(1, faixa(f, 1, FS) * 1.1)) * (1 - 0.4 * faixa(f, 1, FS)),
                  dobra=lambda f: [60 * (1 - faixa(f, 1, N)) * math.sin(f / 2.0), -60 * (1 - faixa(f, 1, N)) * math.sin(f / 2.3 + 1), 30 * (1 - faixa(f, 1, N)), -30 * (1 - faixa(f, 1, N))])
    for f in range(1, N + 1):
        k = 1.0 + 0.5 * (1 - faixa(f, 1, FS)); pc.scale = (k, k, 1.0); key(pc, "scale", f, "LINEAR")
    camera(N, [(1, (2.6, 6.2, 0.9), (-0.1, 10.4, 0.6), 28, (-0.1, 10.4, 0.8), 5.6),
               (N, (2.3, 6.0, 1.1), (-0.05, 10.3, 1.2), 28, (-0.1, 10.3, 1.2), 5.6)], mao=0.6)


@acao("3E")
def a3E(N):
    """eles correm para a câmera; atrás, cinco Sem-Osso vindo aos trancos, cada um no seu ritmo, do mais perto ao mais longe"""
    rua_aberta(bici=False)
    eu = SA.ator3("eu", "eu", 0.0, 7.0, rot=0, rosto=SUSTO_R); ri = SA.ator3("rita", "rita", 0.9, 7.3, rot=0, rosto=SUSTO_R)
    corre(eu, N, (0.0, 7.4, 0), (0.0, 4.4, 0), 0, fase=2)
    corre(ri, N, (0.9, 7.8, 0), (0.85, 4.9, 0), 0, fase=6, ciclo=13)
    for k, (x, y, chv) in enumerate(((-1.8, 10.0, "padeira"), (1.9, 12.0, "mercado"), (-0.4, 13.5, "viz1"), (2.4, 15.0, "viz2"), (-2.2, 16.0, "viz3"))):
        h = O2.sem_osso(f"so{k}", chv, (x, y, 0), rot=0.0, curva=1.0, seed=3 + k)
        per = 14.0 + 3 * k; ch = []
        for f in range(1, N + 1, 2):
            s = math.sin(2 * math.pi * (f / per + 0.21 * k)); v = f / N
            ch.append((f, dict(pos=(x + 0.12 * s, y - (2.0 - 0.2 * k) * v - 0.25 * max(0, s), 0), rot=-10 * s, tronco=24 + 12 * max(0, s), cabeca=-10 + 10 * s, alt=0.76,
                               ombro=(-26 + 28 * s, -26 - 28 * s), cotovelo=(-20, -24), quadril=(-24 * s, 24 * s), joelho=(10 + 34 * max(0, s), 10 + 34 * max(0, -s)))))
        sem_osso_vivo(h, N, ch, seed=6 + k, base_pulso=lambda f, per=per, k=k: max(0, math.sin(2 * math.pi * (f / per + 0.21 * k))))
    camera(N, [(1, (-0.6, 2.4, 1.4), (0.5, 9.5, 1.2), 50, (0.0, 7.2, 1.2), 5.6),
               (N, (-0.6, 0.2, 1.4), (0.5, 7.0, 1.2), 50, (0.0, 4.6, 1.2), 5.6)], mao=1.0)


@acao("3F")
def a3F(N):
    """o POV correndo: a câmera balança com o passo; no cruzamento à frente outra Sem-Osso entra na rua; ele puxa a Rita para o beco à esquerda"""
    rua_aberta(bici=False)
    so = S.sem("so", "padeira", 1.8, -1.0, rot=-120, curva=1.0, seed=2)
    ch = []
    for f in range(1, N + 1, 2):
        s = math.sin(2 * math.pi * f / 15.0); v = f / N
        ch.append((f, dict(pos=(1.8 - 1.3 * v, -1.0 - 0.1 * s, 0), rot=-120 + 30 * v, tronco=24 + 10 * max(0, s), cabeca=-8, alt=0.76, ombro=(-30 + 25 * s, -30 - 25 * s),
                           cotovelo=(-20, -20), quadril=(-24 * s, 24 * s), joelho=(10 + 30 * max(0, s), 10 + 30 * max(0, -s)))))
    sem_osso_vivo(so, N, ch)
    c = camera(N, [(1, (0.0, 5.0, 1.55), (0.1, -4.0, 1.2), 20, (0.6, -1.0, 1.2), 8.0),
                   (int(N * 0.55), (0.0, 3.6, 1.5), (-0.1, -4.0, 1.2), 20, (0.4, -1.0, 1.2), 8.0),
                   (N, (-0.25, 3.0, 1.5), (-5.0, -1.0, 1.2), 20, (-3.0, 0.0, 1.2), 8.0, -6.0)], mao=1.5, passo_corrida=0.035)
    S.pov_maos(c)


@acao("4A")
def a4A(N):
    """no beco: ele entra correndo com a Rita, freia, encosta e vira o corpo para trás, ofegante, ouvindo o Zé (a boca da rua acesa ao fundo)"""
    S.noite_rica(); AN.beco_rico(); S.praca_noite(-17.5, 6.5); O3.halo_cam("contraluz2", (-2.6, 6.5, 1.8), 2.6, "#f2e2b0", 0.22)
    eu = SA.ator3("eu", "eu", -5.4, 6.4, rot=-90, rosto=SUSTO_R); ri = SA.ator3("rita", "rita", -5.0, 6.9, rot=-90, rosto=SUSTO_R)
    FP = int(N * 0.5)
    ch = corrida(1, FP, (-5.0, 6.4, 0), (-7.6, 6.35, 0), rot=-90, ciclo=12, inclina=13, arranque=0.0, freia=0.45)
    para = dict(pos=(-7.75, 6.35, 0), rot=-60, tronco=12, ombro=(-10, 10), cotovelo=(-30, -20), abre=(8, 8), quadril=(-6, 6), joelho=(14, 18), olha=0.0)
    vira = dict(para, rot=70, tronco=8, olha=-20, cabeca=-4, giro=-10)
    sombra(eu).anima(ch + [(FP + 4, para), (N - 6, vira), (N, dict(vira, tronco=10))], 1, N, vida=1.6, seed=2, molas=dict(pos=(0, 6.0, 0.9), rot=(0, 3.0, 0.75)))
    chr_ = corrida(1, FP + 3, (-4.4, 6.95, 0), (-7.0, 6.95, 0), rot=-90, ciclo=13, inclina=12, arranque=0.0, freia=0.5)
    pr = dict(pos=(-7.15, 6.95, 0), rot=80, tronco=16, ombro=(-20, 0), cotovelo=(-40, -20), abre=(8, 8), quadril=(-6, 6), joelho=(16, 20), olha=10)
    sombra(ri).anima(chr_ + [(FP + 8, pr), (N, dict(pr, tronco=20))], 1, N, vida=1.6, seed=3, molas=dict(pos=(0, 6.0, 0.9), rot=(0, 3.0, 0.75)))
    camera(N, [(1, (-10.2, 5.7, 1.5), (-6.0, 6.5, 1.3), 50, (-6.0, 6.4, 1.3), 4.0),
               (FP, (-10.0, 5.75, 1.5), (-7.6, 6.45, 1.35), 50, (-7.7, 6.4, 1.35), 4.0),
               (N, (-9.7, 5.8, 1.5), (-7.7, 6.5, 1.4), 50, (-7.75, 6.4, 1.4), 4.0)], mao=0.9)


@acao("4B")
def a4B(N):
    """por cima do ombro dele, na boca do beco contra a luz: uma Sem-Osso entra cambaleando; a sombra dela chega antes, na parede e na poça"""
    S.noite_rica(); AN.beco_rico(); AN.poste("pb4", -2.5, 3.6, acesa=True, rot=180)
    O3.halo_cam("contraluz", (-2.0, 6.5, 2.0), 4.2, "#f2e2b0", 0.55)
    AN.poca_agua("pqm", -5.6, 6.5, 1.7, 0.9, cor="#4a5a78", brilho=("#fff2c8", 0.5), seed=6)
    eu = SA.ator3("eu", "eu", -7.75, 6.35, rot=70, rosto=SUSTO_R); ri = SA.ator3("rita", "rita", -7.15, 6.95, rot=80, rosto=SUSTO_R)
    vivo(eu, N, dict(rot=70, tronco=10, ombro=(-10, 10), cotovelo=(-30, -20), abre=(8, 8), olha=-20, pos=(-7.75, 6.35, 0)), seed=2, vida=1.8)
    vivo(ri, N, dict(rot=80, tronco=18, ombro=(-20, 0), cotovelo=(-40, -20), abre=(8, 8), olha=10, pos=(-7.15, 6.95, 0)), seed=3, vida=1.8)
    AN.mancha_parede("sombraM", -5.4, 1.7, 1.0, 3.4, 5.25, +1, cor="#08080a", alfa=0.6); som = bpy.data.objects.get("sombraM")
    so = S.sem("so", "padeira", -3.2, 5.6, rot=-60, curva=1.0, seed=2)
    ch = []
    for f in range(1, N + 1, 2):
        s = math.sin(2 * math.pi * f / 16.0); v = suave(f / N)
        ch.append((f, dict(pos=(-3.2 - 1.3 * v, 5.6 + 0.8 * v, 0), rot=-60 - 30 * v - 8 * s, tronco=26 + 10 * max(0, s), cabeca=-12 + 12 * s, alt=0.76,
                           ombro=(-30 + 25 * s, -10 - 25 * s), cotovelo=(-20, -24), quadril=(-24 * s, 24 * s), joelho=(10 + 34 * max(0, s), 10 + 34 * max(0, -s)))))
    sem_osso_vivo(so, N, ch, base_pulso=lambda f: max(0, math.sin(2 * math.pi * f / 16.0)))
    if som is not None:
        x0 = som.location.x
        for f in range(1, N + 1):
            som.location.x = x0 - 1.3 * suave(f / N); key(som, "location", f, "LINEAR")
    camera(N, [(1, (-9.3, 6.0, 1.55), (-4.2, 6.2, 1.2), 35, (-3.4, 5.8, 1.2), 4.0),
               (N, (-9.05, 6.05, 1.5), (-4.4, 6.3, 1.2), 35, (-4.5, 6.3, 1.2), 4.0)], mao=0.8)


# ====================================================================== 15B3 (1:20): as duas mãos lado a lado, nítidas, e o foco passando de uma à outra
@acao("15B3")
def a15B3(N):
    S.galpao(grupo=False)
    ox, oy = -3.0, -0.6
    S.mao_cor("mn", "dir", (ox - 0.07, oy - 0.02, 1.0), (0.85, 0.5, 0.05), "#b02a22", pose="aberta")
    S.mao_pingando("hL", "esq", (ox + 0.1, oy + 0.32, 1.02), (-0.85, 0.45, 0.0), S.manga_de("lider"), k=1.0, pose="relaxada")
    camera(N, [(1, (ox + 0.05, oy - 0.95, 1.32), (ox + 0.03, oy + 0.15, 1.0), 50, (ox + 0.1, oy + 0.32, 1.02), 4.0),
               (int(N * 0.35), (ox + 0.05, oy - 0.93, 1.31), (ox + 0.03, oy + 0.15, 1.0), 50, (ox + 0.1, oy + 0.32, 1.02), 4.0),
               (int(N * 0.7), (ox + 0.05, oy - 0.9, 1.3), (ox + 0.03, oy + 0.15, 1.0), 50, (ox - 0.07, oy - 0.02, 1.0), 4.0),
               (N, (ox + 0.05, oy - 0.88, 1.3), (ox + 0.03, oy + 0.15, 1.0), 50, (ox - 0.07, oy - 0.02, 1.0), 4.0)], mao=0.4)


try:
    import acoes_abrigo2b  # noqa  (4C em diante)
except ImportError:
    pass
