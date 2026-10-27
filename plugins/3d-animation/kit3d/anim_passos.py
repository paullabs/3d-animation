"""Animação de "E se cada passo dobrasse a sua altura?" em cima do storyboard v2 (story_passos2.py; aprovado em 25/10/2026).
O cenário, a lente e o enquadramento de cada plano vêm de lá; aqui entra o tempo. Motor do abrigo (anim3_abrigo): todo boneco passa por Heroi3D.anima
(curva cúbica + mola por junta + respiração), a câmera nunca para (deriva lenta + mão suave), curvas suavizadas, desfoque de movimento ligado.
Regras específicas deste filme:
- o PASSO é o corte: o pé que pousa cai na palavra (poeira, tremor de câmera de 2 a 3 quadros); o plano seguinte nasce do mesmo pé;
- no PALCO o boneco CRESCE em curva (entrada e saída) enquanto o fantasma do tamanho anterior fica parado; a câmera ortográfica recua na mesma curva;
- tudo o que prova a fala nasce no tempo da palavra (ondas do som, ponteiro, régua, linha da distância).
blender -b -P anim_passos.py -- PLANO PASTA [--scale 0.5] [--samples 10] [--quadros 1,M,N] [--colisao]"""
import os, sys, math, random, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy
from mathutils import Vector, Euler
import anim3_abrigo as A                                  # (instala o registro de bonecos e traz suaviza, soco, camera_viva...)
import story_passos2 as S2
import story_passos as SP
import poses_passos as PP
import ficha_passos as FP
import objetos3d_passos as OP, objetos3d_passos_b as OB
import objetos3d_abrigo as O3
import lib
from lib import key
from poses_passos import _pe

FPS = 24
SIGMA = 0.85
DERIVA = 0.05                                             # no palco a câmera ortográfica nunca para: depois do crescimento ela continua recuando devagar
SH = S2.SHOTS
lerp, suave, suave5, faixa = A.lerp, A.suave, A.suave5, A.faixa
ANIM = {}

# o pé no alto, antes de pousar (a perna F vai à frente, joelho dobrado) e outras poses só da animação
PP.POSES["alta"] = dict(quadril=(-50, 14), joelho=(50, 22), tornozelo=(_pe(-50, 50, 25), _pe(14, 22, 10)), ombro=(22, -24), cotovelo=(-14, -28),
                        abre=(6, 6), tronco=-3, giro=-8, cabeca=-3)
PP.POSES["arranque"] = dict(quadril=(-8, 34), joelho=(8, 50), tornozelo=(_pe(-8, 8, 0), _pe(34, 50, 30)), ombro=(6, -8), cotovelo=(-14, -18), abre=(6, 6), tronco=2, cabeca=0)


def N_de(nome):
    d = SH[nome]
    return int(round(d["t1"] * FPS)) - int(round(d["t0"] * FPS))


def fq(nome, t):
    """quadro (1..N) do instante t (s, do filme) dentro do plano"""
    return max(1, min(N_de(nome), int(round((t - SH[nome]["t0"]) * FPS)) + 1))


# ---------------------------------------------------------------- bonecos
def humanos():
    return {k: h for k, h in A.REG.items() if not k.startswith("fant")}


def sombra_de(H):
    H.sombra = bpy.data.objects.get(H.nome + "_sb")
    return H


def estado(H, nome, dx=0.0, dy=0.0, dz=0.0, rot_z=None):
    """aplica a pose 'nome' (PP.POSES, com IK) e devolve o estado inteiro (ângulos, pos e rot) para virar chave de animação"""
    base = tuple(H.raiz.location), tuple(H.raiz.rotation_euler)
    sc0 = tuple(H.raiz.scale)
    H.raiz.location = (0, 0, 0); H.raiz.rotation_euler = (0, 0, 0)
    PP.aplica(H, nome, escala=sc0[0])
    P = dict(getattr(H, "_ultima", {}))
    loc = Vector(H.raiz.location)
    rot = tuple(math.degrees(v) for v in H.raiz.rotation_euler)
    P["pos"] = (base[0][0] + loc.x + dx, base[0][1] + loc.y + dy, loc.z + dz + base[0][2])
    P["rot"] = (rot[0], rot[1], rot[2] + (math.degrees(base[1][2]) if rot_z is None else rot_z))
    return P


def anima_estados(H, itens, N, vida=0.8, seed=3, molas=None, mola=True):
    """itens = [(quadro, estado)]; as chaves são ligadas em curva cúbica com mola por junta (Heroi3D.anima). mola=False: sem atraso, o pé chega no
    quadro da chave (a mola atrasava o pouso em 0,4 a 0,6 s: o pé pousava depois da palavra, 25/10/2026)"""
    sombra_de(H)
    H.anima(sorted(itens, key=lambda x: x[0]), 1, N, vida=vida, seed=seed, molas=molas, mola=mola)


def vivo(H, N, seed=3, vida=1.0):
    """parado, mas vivo: respira, o peso passa de um pé para o outro, o olhar passeia"""
    sombra_de(H)
    P = dict(getattr(H, "_ultima", {}))
    P["pos"] = tuple(H.raiz.location)
    P["rot"] = tuple(math.degrees(v) for v in H.raiz.rotation_euler)
    H.anima([(1, P), (N, P)], 1, N, vida=vida, seed=seed)


def escala_h(H, N, curva, base=None):
    """curva(f) -> fator de escala do boneco em relação ao tamanho do quadro (1 = o tamanho do storyboard); a sombra acompanha"""
    b = base if base is not None else H.raiz.scale[0]
    sb = bpy.data.objects.get(H.nome + "_sb")
    s0 = tuple(sb.scale) if sb else None
    for f in range(1, N + 1):
        s = curva(f)
        H.raiz.scale = (b * s,) * 3; key(H.raiz, "scale", f, "LINEAR")
        if sb:
            sb.scale = (s0[0] * s, s0[1] * s, s0[2]); key(sb, "scale", f, "LINEAR")


def cresce(f0, f1, de=0.5, para=1.0, p=0.0):
    """fator de crescimento em curva de entrada e saída (suave5); p = quanto passa do ponto (mola leve)"""
    def c(f):
        u = faixa(f, f0, f1)
        v = suave5(u)
        if p:
            v += p * math.sin(math.pi * u) * (1 - u)
        return lerp(de, para, v)
    return c


# ---------------------------------------------------------------- câmera
def cam():
    return bpy.context.scene.camera


def camera_caminho(N, pontos, lente=None):
    """câmera por um caminho: pontos = [(quadro, loc, alvo)]; spline suave pelos pontos (Catmull-Rom), o foco segue o alvo"""
    c = cam()
    fs = [p[0] for p in pontos]
    L = [Vector(p[1]) for p in pontos]; T = [Vector(p[2]) for p in pontos]
    def cr(P, f):
        if f <= fs[0]:
            return P[0].copy()
        if f >= fs[-1]:
            return P[-1].copy()
        i = max(k for k in range(len(fs)) if fs[k] <= f)
        u = (f - fs[i]) / (fs[i + 1] - fs[i]); u = suave(u) if len(fs) == 2 else u
        p0 = P[max(0, i - 1)]; p1 = P[i]; p2 = P[i + 1]; p3 = P[min(len(P) - 1, i + 2)]
        return 0.5 * ((2 * p1) + (-p0 + p2) * u + (2 * p0 - 5 * p1 + 4 * p2 - p3) * u * u + (-p0 + 3 * p1 - 3 * p2 + p3) * u ** 3)
    for f in range(1, N + 1):
        loc, alvo = cr(L, f), cr(T, f)
        c.location = loc
        c.rotation_euler = (alvo - loc).to_track_quat("-Z", "Y").to_euler()
        c.data.dof.focus_distance = max(0.05, (alvo - loc).length)
        key(c, "location", f, "LINEAR"); key(c, "rotation_euler", f, "LINEAR"); key(c.data.dof, "focus_distance", f, "LINEAR")


def ortho_curva(N, curva):
    c = cam()
    for f in range(1, N + 1):
        c.data.ortho_scale = curva(f); key(c.data, "ortho_scale", f, "LINEAR")


def soco_suave(f, fs, m=0.02, dur=26, osc=0.38):
    """o impacto do pé como um balanço de mola amortecido: entra em 3 quadros (curva de entrada), passa do ponto uma vez e assenta em ~1 s.
    Sem tranco: a velocidade da câmera sobe e desce em curva (pedido de 25/10/2026: bem fluido, bem suave)"""
    d = 0.0
    for fi in fs:
        u = f - fi
        if 0 <= u < dur:
            r = min(1.0, u / 5.0); r = r * r * (3 - 2 * r)
            fim = min(1.0, (dur - u) / 6.0)
            d += m * r * fim * math.exp(-u / 6.0) * math.cos(u * osc)
    return d


def tremor(N, fs, m=0.02, vel=(0, 0, 0), frente=0.0, mao=0.8, seed=1):
    """câmera de operador com um balanço amortecido (m, em u) nos quadros fs: o pé que pousa"""
    A.camera_viva(N, vel=vel, frente=frente, mao=mao, centro=0.5, seed=seed,
                  extra=lambda f: ((0.0, 0.0, soco_suave(f, fs, m, osc=0.0)), (soco_suave(f, fs, 0.35, osc=0.0), 0.0, 0.0)))


def camera_vagar(N, frente=0.06, mao=0.7, vel=(0, 0, 0), seed=1):
    A.camera_viva(N, vel=vel, frente=frente, mao=mao, centro=0.5, seed=seed)


# ---------------------------------------------------------------- efeitos
def cada(prefixo):
    return [o for o in bpy.data.objects if o.name.startswith(prefixo)]


def aparece(objs, f0, f1=None, s_ini=0.0, N=None):
    """o objeto nasce no quadro f0 (escala s_ini até 1 em curva até f1); antes disso fica sem escala"""
    f1 = f1 or f0 + 4
    for o in objs:
        base = Vector(o.scale)
        for f in range(1, (N or f1 + 1) + 1):
            u = faixa(f, f0, f1)
            s = s_ini + (1 - s_ini) * suave(u) if f >= f0 else 0.0001
            o.scale = base * max(s, 0.0001); key(o, "scale", f, "LINEAR")


def some(objs, f0, f1=None, N=None):
    f1 = f1 or f0 + 4
    for o in objs:
        base = Vector(o.scale)
        for f in range(1, (N or f1 + 1) + 1):
            u = 1 - faixa(f, f0, f1)
            o.scale = base * max(suave(u), 0.0001); key(o, "scale", f, "LINEAR")


def revela_por_altura(objs, f0, f1, N):
    """régua que sobe: cada peça aparece quando a 'subida' chega na sua altura"""
    zs = [(o.matrix_world.translation.z, o) for o in objs]
    z0, z1 = min(z for z, _ in zs), max(z for z, _ in zs)
    for z, o in zs:
        fq_ = f0 + (f1 - f0) * suave((z - z0) / max(1e-6, z1 - z0))
        base = Vector(o.scale)
        for f in range(1, N + 1):
            o.scale = base * (1.0 if f >= fq_ else 0.0001); key(o, "scale", f, "CONSTANT")


def poeira_anim(N, f_land, raio=1.0):
    """poeira do pouso: o disco do chão abre em anel e as bolinhas sobem e se afastam; antes do pouso não existe"""
    chao = bpy.data.objects.get("poeira_chao")
    centro = Vector(chao.location) if chao else Vector((0, 0, 0))
    if chao:
        b = Vector(chao.scale)
        for f in range(1, N + 1):
            u = faixa(f, f_land, f_land + 9); v = faixa(f, f_land + 9, f_land + 40)
            s = 0.0001 if f < f_land else 0.12 + 0.88 * suave(u) + 0.35 * v
            chao.scale = (b.x * s, b.y * s, b.z); key(chao, "scale", f, "LINEAR")
    rnd = random.Random(4)
    for o in cada("poeira_") :
        if o.name == "poeira_chao":
            continue
        b = Vector(o.scale); p0 = Vector(o.location)
        d = Vector((p0.x - centro.x, p0.y - centro.y, 0)); d = d.normalized() if d.length > 1e-6 else Vector((1, 0, 0))
        v = rnd.uniform(0.6, 1.4) * raio
        for f in range(1, N + 1):
            t = max(0, f - f_land)
            if f < f_land:
                o.scale = b * 0.0001
            else:
                u = faixa(f, f_land, f_land + 5); fade = 1 - faixa(f, f_land + 18, f_land + 42)
                o.scale = b * max(0.0001, suave(u) * (0.6 + 0.8 * (1 - math.exp(-t / 8))) * fade)
                o.location = p0 + d * (0.10 * v * (1 - math.exp(-t / 7))) + Vector((0, 0, 0.12 * v * (1 - math.exp(-t / 10))))
            key(o, "scale", f, "LINEAR"); key(o, "location", f, "LINEAR")


def pombos_voam(N, f_land):
    rnd = random.Random(6)
    for o in cada("pombo"):
        p0 = Vector(o.location); r0 = Vector(o.rotation_euler)
        dx, dz = rnd.uniform(-0.25, 0.25), rnd.uniform(0.25, 0.5)
        fase = rnd.uniform(0, 6.28)
        for f in range(1, N + 1):
            t = max(0, f - f_land)
            if f < f_land - 1:
                o.location = p0; o.rotation_euler = r0
            else:
                k = 1 - math.exp(-t / 9)
                o.location = p0 + Vector((dx * k, -0.12 * k, dz * k + 0.02 * math.sin(t * 0.9 + fase)))
                o.rotation_euler = (r0.x, r0.y + 0.6 * math.sin(t * 1.3 + fase), r0.z)
            key(o, "location", f, "LINEAR"); key(o, "rotation_euler", f, "LINEAR")


PROFUNDIDADE = False                                          # ligado por anim_passos7 (o v7 em diante)
POUSOS = []                                                   # os quadros de pouso planejados no plano (a conferência --sync mede o pé nesses quadros)


def pouso(H, N, f_land, de="alta", para="contato", depois="descida", f_depois=None, dx=0.0, dy=0.0, seed=3):
    """o pé desce e pousa no quadro f_land (acelerando, como peso), assenta e o corpo segue o impulso"""
    POUSOS.append(f_land)
    S0 = estado(H, de, dy=dy + 0.0, dx=dx)
    S1 = estado(H, para, dx=dx, dy=dy)
    S2_ = estado(H, depois, dx=dx, dy=dy)
    ch = [(1, S0), (max(2, f_land - 4), dict(S0, **{k: S1[k] for k in ("quadril", "joelho", "tornozelo")}, **{"pos": tuple(a + (b - a) * 0.5 for a, b in zip(S0["pos"], S1["pos"]))})),
          (f_land, S1), (max(f_land + 7, f_depois or min(N, f_land + 12)), S2_), (N, S2_)]
    anima_estados(H, ch, N, vida=0.5, seed=seed, mola=False)                    # o pé pousa EXATAMENTE em f_land (a conferência --sync mede)


# ======================================================================== FALA 1
def a1A(N):
    H = A.REG["eu"]; fl = fq("1A", 0.90)
    pouso(H, N, fl)
    poeira_anim(N, fl, raio=1.2); pombos_voam(N, fl)
    tremor(N, [fl], m=0.03, frente=0.05, mao=0.4)


def a1B(N):
    H = A.REG["eu"]; vivo(H, N)
    camera_caminho(N, [(1, (0.3, -1.15, 0.12), (0.0, 0.0, 1.35)), (N, (0.5, -2.1, 1.0), (0.0, 0.0, 1.55))])


def a1C(N):
    H2 = A.REG["eu2"]; H1 = A.REG["eu1"]
    vivo(H1, N, seed=2); vivo(H2, N, seed=5)
    escala_h(H2, N, cresce(8, 26, de=0.5, para=1.0, p=0.04))
    OBJ = cada("r2_")


# ======================================================================== FALA 2
def a2A(N):
    H = A.REG["eu"]; vivo(H, N)
    b = bpy.data.objects.get("onibus")
    if b:
        y0 = b.location.y
        for f in range(1, N + 1):
            u = faixa(f, 1, N); b.location.y = lerp(y0, y0 - 12.0, 1 - (1 - u) ** 2); key(b, "location", f, "LINEAR")
    camera_vagar(N, frente=0.18, mao=0.5)


def a2B(N):
    for k, H in humanos().items():
        vivo(H, N, seed=sum(map(ord, k)) % 11)
    objs = [o for o in bpy.data.objects if o.name.startswith("r2_") and o.type in ("MESH", "FONT")]
    revela_por_altura(objs, 4, 24, N)
    A.camera_viva(N, mao=0.0)


def a2C(N):
    H = A.REG["eu"]
    itens = [(1, estado(H, "contato", dy=0.0)), (9, estado(H, "descida", dy=-0.25)), (17, estado(H, "passagem", dy=-0.55)), (25, estado(H, "subida", dy=-0.85)), (N, estado(H, "contato", dy=-1.15))]
    anima_estados(H, itens, N, vida=0.5)
    escala_h(H, N, cresce(1, N, de=1.0 / 2 ** 0.5, para=1.0))
    camera_vagar(N, vel=(0, -1.15 * FPS / N, 0), mao=0.5)


def a2D(N):
    H = A.REG["eu"]; fl = 5
    pouso(H, N, fl); poeira_anim(N, fl, raio=0.9)
    tremor(N, [fl], m=0.025, mao=0.5)


def a2E(N):
    palco_cresce("eu", N, 1, 14, de=0.5)


def palco_cresce(nome, N, f0, f1, de=0.5, ortho=(0.93, 1.0)):
    """no palco o boneco cresce do tamanho anterior (o fantasma, parado) até o do passo, em curva; a câmera recua na mesma curva"""
    H = A.REG[nome]; vivo(H, N)
    escala_h(H, N, cresce(f0, f1, de=de, para=1.0, p=0.03))
    c = cam()
    if c.data.type == "ORTHO":
        o = c.data.ortho_scale
        ortho_curva(N, lambda f: o * lerp(ortho[0], ortho[1], suave5(faixa(f, f0, f1))) * (1 + DERIVA * suave(faixa(f, f1, N))))
        A.camera_viva(N, mao=0.0, centro=0.5)


# ======================================================================== FALA 3
def a3A(N):
    H = A.REG["eu"]; fl = 4
    pouso(H, N, fl); poeira_anim(N, fl, raio=1.0); tremor(N, [fl], m=0.025, mao=0.5)


def a3B(N):
    H = A.REG["eu"]
    P0 = dict(getattr(H, "_ultima", {})); P0["pos"] = tuple(H.raiz.location); P0["rot"] = (0, 0, 0)
    P1 = dict(P0, cabeca=-14, olha=-30, tronco=0)
    P0 = dict(P0, cabeca=14, olha=0)
    anima_estados(H, [(1, P0), (12, P0), (22, P1), (N, P1)], N, vida=0.8)
    camera_vagar(N, frente=0.1, mao=0.7)


def a3C(N):
    palco_cresce("eu", N, 1, 12, de=0.5)


# ======================================================================== FALA 4
def a4A(N):
    H = A.REG["eu"]; fl = 4
    pouso(H, N, fl); poeira_anim(N, fl, raio=1.1); tremor(N, [fl], m=0.025, mao=0.5)


def a4B(N):
    palco_cresce("eu", N, 1, 14, de=0.5)


def a4C(N):
    H = A.REG["eu"]
    itens = [(1, estado(H, "passagem", dy=0.0)), (7, estado(H, "subida", dy=-0.2)), (13, estado(H, "tropeco", dy=-0.4)), (N, estado(H, "tropeco", dy=-0.55))]
    anima_estados(H, itens, N, vida=0.3, molas=dict(ombro=(0, 5.0, 0.55), abre=(0, 5.0, 0.55)))
    camera_vagar(N, vel=(0, -0.55 * FPS / N, 0), mao=0.6)


def a4D(N):
    """cronofotografia: o boneco sólido atravessa as três poses da queda (começo, meio e fim), os fantasmas marcam onde ele esteve"""
    H = A.REG["eu"]
    q1 = estado(H, "queda1", dy=0.95); q2 = estado(H, "queda2", dy=0.05); q3 = estado(H, "queda3", dy=-0.95)
    anima_estados(H, [(1, q1), (int(N * 0.5), q2), (N, q3)], N, vida=0.0, molas=dict(pos=(0, 6.0, 0.9), rot=(0, 6.0, 0.9)))
    textos = [o for o in bpy.data.objects if o.type == "FONT" and o.name.startswith("tt")]
    for o, f in zip(sorted(textos, key=lambda o: -o.location.y), (1, int(N * 0.5) - 3, N - 6)):
        aparece([o], f, f + 4, N=N)
    camera_vagar(N, frente=0.05, mao=0.4)


def a4E(N):
    H = A.REG["eu"]
    q2 = estado(H, "queda2"); q3 = estado(H, "queda3"); ap = estado(H, "apoio")
    anima_estados(H, [(1, q2), (8, q3), (N, q3)], N, vida=0.4)
    poeira_anim(N, 8, raio=0.7)
    tremor(N, [8], m=0.018, mao=0.4)


# ======================================================================== FALA 5
def a5A(N):
    H = A.REG["eu"]
    itens = [(1, estado(H, "apoio")), (11, estado(H, "levanta")), (N, estado(H, "contato"))]
    anima_estados(H, itens, N, vida=0.5)
    camera_vagar(N, frente=0.12, mao=0.7)


def a5B(N):
    palco_cresce("eu", N, 1, 14, de=0.5)


def a5C(N):
    H = A.REG["eu"]
    anima_estados(H, [(1, estado(H, "respira")), (9, estado(H, "grito")), (N, estado(H, "grito"))], N, vida=0.5)
    arcos = sorted(cada("arco"), key=lambda o: o.name)
    for i, o in enumerate(arcos):
        aparece([o], 9 + i * 4, 9 + i * 4 + 6, s_ini=0.5, N=N)
    A.camera_viva(N, frente=0.05, mao=0.5)


def a5D(N):
    H = A.REG["eu"]
    anima_estados(H, [(1, estado(H, "grito")), (N, estado(H, "grito"))], N, vida=0.5)
    sons = sorted(cada("som"), key=lambda o: o.name); tt = sorted([o for o in cada("tt")], key=lambda o: -o.location.z)
    for i, o in enumerate(sons):
        aparece([o], 1 + i * 11, 1 + i * 11 + 8, s_ini=0.93, N=N)
    for i, o in enumerate(tt):
        aparece([o], 3 + i * 11, 8 + i * 11, N=N)
    A.camera_viva(N, frente=0.05, mao=0.5)


def a5E(N):
    H = A.REG["eu"]
    anima_estados(H, [(1, estado(H, "grito")), (N, estado(H, "grito"))], N, vida=0.5)
    ondas = sorted(cada("onda_"), key=lambda o: o.name)
    for i, o in enumerate(ondas):
        aparece([o], 8 + i * 5, 8 + i * 5 + 9, s_ini=0.3, N=N)
    A.camera_viva(N, frente=0.05, mao=0.5)


# ======================================================================== FALA 6
def a6A(N):
    H = A.REG["eu"]; fl = 8
    pouso(H, N, fl); poeira_anim(N, fl, raio=1.2)
    s = bpy.data.objects.get("sombra_fachada")
    if s:
        aparece([s], fl, fl + 8, N=N)
    tremor(N, [fl], m=0.03, mao=0.5)


def a6B(N):
    palco_cresce("eu", N, 1, 15, de=0.5)


def a6C(N):
    for k, H in humanos().items():
        vivo(H, N, seed=sum(map(ord, k)) % 13)
    c = cam(); L0 = Vector(c.location); fw = (c.rotation_euler.to_matrix() @ Vector((0, 0, -1))).normalized()
    d = max(8.0, c.data.dof.focus_distance); T0 = L0 + fw * 20.0
    camera_caminho(N, [(1, tuple(L0), tuple(T0)), (N, tuple(L0 + Vector((2.2, 1.2, 1.2))), tuple(T0 + Vector((0, 0, 2.2))))])


def a6D(N):
    for k, H in humanos().items():
        vivo(H, N, seed=sum(map(ord, k)) % 13)
    c = cam(); L0 = Vector(c.location); fw = (c.rotation_euler.to_matrix() @ Vector((0, 0, -1))).normalized()
    T0 = L0 + fw * max(1.0, c.data.dof.focus_distance)
    camera_caminho(N, [(1, tuple(L0), tuple(T0)), (N, tuple(L0 + Vector((0.55, 0.45, 0.12))), tuple(T0 + Vector((0.0, 0.0, 0.02))))])


def a6E(N):
    A.camera_viva(N, mao=0.3, vel=(0.05, 0, 0))
    for i, nm in enumerate(("t_fio", "t_pal")):
        o = bpy.data.objects.get(nm)
        if o:
            aparece([o], 10 + i * 12, 20 + i * 12, N=N)


# ======================================================================== FALA 7
def a7A(N):
    H = A.REG["eu"]
    r = estado(H, "respira")
    r2 = dict(r, tronco=r.get("tronco", 0) + 5, cabeca=r.get("cabeca", 0) + 6)
    r1 = dict(r, tronco=r.get("tronco", 0) - 1)
    anima_estados(H, [(1, r1), (11, r2), (21, r1), (N, r2)], N, vida=0.5)
    A.camera_viva(N, frente=0.04, mao=0.6, vel=(0.05, 0, 0))


def a7B(N):
    H = A.REG["eu"]; vivo(H, N, vida=0.3)
    for o in cada("cor_"):                                    # o coração bate: dois toques por segundo e meio
        b = Vector(o.scale)
        for f in range(1, N + 1):
            t = (f - 1) / FPS; ph = (t * 1.25) % 1.0
            s = 1 + 0.22 * math.exp(-((ph - 0.08) / 0.05) ** 2) + 0.12 * math.exp(-((ph - 0.28) / 0.06) ** 2)
            o.scale = b * s; key(o, "scale", f, "LINEAR")
    pv = bpy.data.objects.get("man_pivo")
    if pv:
        a0, a1 = math.radians(-135), pv.rotation_euler.y
        for f in range(1, N + 1):
            u = faixa(f, 8, 36); v = suave5(u) + 0.06 * math.sin(math.pi * u) * (1 - u) * 3
            if f > 36:
                v = 1.0 + 0.012 * math.sin((f - 36) * 1.1) * math.exp(-(f - 36) / 8)
            pv.rotation_euler.y = a0 + (a1 - a0) * v; key(pv, "rotation_euler", f, "LINEAR")
    contas(N, rapido=1.0)
    A.camera_viva(N, mao=0.0)


def contas(N, rapido=1.0):
    """as bolinhas de luz sobem pelo vaso do coração à cabeça, em pulsos"""
    for o in cada("pulso"):
        p0 = Vector(o.location); i = int(o.name[5:])
        for f in range(1, N + 1):
            t = (f - 1) / FPS
            u = (t * 0.9 * rapido + i / 6.0) % 1.0
            o.location = Vector((p0.x + 0.05 * (1 - u) * 0 , p0.y, lerp(0.72 * 1.8 + 0.06, 1.62, u)))
            o.location.x = lerp(0.05, 0.0, u)
            key(o, "location", f, "LINEAR")


def a7C(N):
    H = A.REG["eu"]; vivo(H, N, vida=0.3)
    for o in cada("cor_"):
        b = Vector(o.scale)
        for f in range(1, N + 1):
            t = (f - 1) / FPS; ph = (t * 1.25) % 1.0
            s = 1 + 0.22 * math.exp(-((ph - 0.08) / 0.05) ** 2) + 0.12 * math.exp(-((ph - 0.28) / 0.06) ** 2)
            o.scale = b * s; key(o, "scale", f, "LINEAR")
    contas(N, rapido=1.3)
    for o in cada("chave_") + [bpy.data.objects.get("t16")]:
        if o:
            aparece([o], 8, 16, N=N)
    A.camera_viva(N, mao=0.0)


# ======================================================================== FALA 8
def landing_curto(nome_plano):
    def f(N):
        H = A.REG["eu"]; fl = 3
        pouso(H, N, fl, f_depois=min(N, fl + 6)); poeira_anim(N, fl, raio=1.0)
        t = bpy.data.objects.get("n_pe")
        if t:
            aparece([t], fl, fl + 3, N=N)
        tremor(N, [fl], m=0.03, mao=0.4)
    return f


a8A = landing_curto("8A"); a8B = landing_curto("8B"); a8C = landing_curto("8C"); a8D = landing_curto("8D")


def a8E(N):
    palco_cresce("eu", N, 1, 14, de=0.5)
    for nm in ("linha_burj",):
        o = bpy.data.objects.get(nm)
        if o:
            aparece([o], 12, 20, N=N)


def a8F(N):
    H = A.REG["eu"]; vivo(H, N)
    c = cam(); z = c.location.z
    camera_caminho(N, [(1, (0.18, -5.2, 0.3), (0.2, 0.0, 0.35)), (N, (0.18, -5.2, z), (0.2, 0.0, z))])


# ======================================================================== FALA 9
def a9A(N):
    H = A.REG["eu"]; fl = 3
    pouso(H, N, fl); poeira_anim(N, fl, raio=1.0)
    t = bpy.data.objects.get("n_pe")
    if t:
        aparece([t], fl, fl + 3, N=N)
    tremor(N, [fl], m=0.03, mao=0.4)


def a9B(N):
    palco_cresce("eu", N, 1, 16, de=0.5)


def a9C(N):
    lat = [o for o in bpy.data.objects if o.name.startswith("lata")]
    for o in lat:
        if o.parent is None:
            p0 = Vector(o.location)
            for f in range(1, N + 1):
                u = suave5(faixa(f, 4, 34)); o.location = p0 + Vector((0.9 * (1 - u), 0, 0)); o.rotation_euler.z = 2.2 * (1 - u)
                key(o, "location", f, "LINEAR"); key(o, "rotation_euler", f, "LINEAR")
    for i, nm in enumerate(("t_fio", "t_lat")):
        o = bpy.data.objects.get(nm)
        if o:
            aparece([o], 30 + i * 8, 38 + i * 8, N=N)
    A.camera_viva(N, mao=0.3, vel=(0.05, 0, 0))


def a9D(N):
    H = A.REG["eu"]; vivo(H, N)
    c = cam(); R0 = Euler(c.rotation_euler)
    for f in range(1, N + 1):
        u = suave(faixa(f, 1, N)); c.rotation_euler = (R0.x, R0.y, R0.z + math.radians(-10) * u); key(c, "rotation_euler", f, "LINEAR")
    A.camera_viva(N, mao=0.5, centro=0.0) if False else None


def a9E(N):
    H = A.REG["eu"]; vivo(H, N)
    for nm, f0 in (("visao", 10), ("ponto_h", 24), ("t150", 26), ("t_fora", 4)):
        o = bpy.data.objects.get(nm)
        if o:
            aparece([o], f0, f0 + 8, N=N)
    A.camera_viva(N, mao=0.0)


# ======================================================================== FALA 10
def a10A(N):
    H = A.REG["eu"]; fl = 6
    pouso(H, N, fl)
    for o in [o for o in bpy.data.objects if o.name.startswith("mundo")]:
        p0 = Vector(o.location)
        for f in range(1, N + 1):
            o.location = p0 + Vector((0.12 * (f - 1) / N, 0, 0)); key(o, "location", f, "LINEAR")
    tremor(N, [fl], m=0.012, mao=0.5)


def a10B(N):
    palco_cresce("eu", N, 1, 14, de=0.5)
    pv = [o for o in bpy.data.objects if o.name.startswith("mundo")]
    for o in pv:
        p0 = Vector(o.location)
        for f in range(1, N + 1):
            o.location = p0 + Vector((0.05 * (f - 1) / N, 0, 0)); key(o, "location", f, "LINEAR")


def a10C(N):
    H = A.REG["eu"]
    r = estado(H, "respira"); r2 = dict(r, tronco=r.get("tronco", 0) + 5)
    anima_estados(H, [(1, dict(r, tronco=r.get("tronco", 0) - 3)), (8, r2), (N, r2)], N, vida=0.5)
    sopros = sorted(cada("sopro"), key=lambda o: o.name)
    for i, o in enumerate(sopros):
        p0 = Vector(o.location); b = Vector(o.scale)
        f0 = 8 + i * 3
        for f in range(1, N + 1):
            t = max(0, f - f0)
            o.scale = b * (0.0001 if f < f0 else min(1.0, t / 4) * (1 + 0.5 * t / 20))
            o.location = p0 + Vector((0.05 * t / 24, -0.1 * t / 24, 0.04 * t / 24)); key(o, "scale", f, "LINEAR"); key(o, "location", f, "LINEAR")
    A.camera_viva(N, mao=0.6, frente=0.04)


def a10D(N):
    H = A.REG["eu"]; vivo(H, N, vida=0.5)
    pv = bpy.data.objects.get("m_boca_pivo")
    if pv:
        a1 = pv.rotation_euler.y; a0 = math.radians(-135 + 270 * (1.0 / 1.2))
        for f in range(1, N + 1):
            u = suave5(faixa(f, 10, 40)); pv.rotation_euler.y = lerp(a0, a1, u); key(pv, "rotation_euler", f, "LINEAR")
    for o in [o for o in bpy.data.objects if o.name.startswith("ar") and o.name[2:].isdigit()]:
        p0 = Vector(o.location)
        for f in range(1, N + 1):
            o.location = p0 + Vector((0.01 * math.sin((f + p0.z * 40) * 0.2), 0, 0.01 * math.sin((f + p0.x * 90) * 0.15))); key(o, "location", f, "LINEAR")
    A.camera_viva(N, mao=0.0)


# ======================================================================== FALA 11
def a11A(N):
    H = A.REG["eu"]
    S0 = estado(H, "alta"); S0["pos"] = (S0["pos"][0], S0["pos"][1], S0["pos"][2] + 0.12)
    S1 = estado(H, "contato")
    anima_estados(H, [(1, S0), (16, S1), (N, estado(H, "descida"))], N, vida=0.5, mola=False)               # pisa em "vigésimo" (59,72 s)
    A.camera_viva(N, frente=0.03, mao=0.5, vel=(0.04, 0, 0))


def a11B(N):
    H = A.REG["eu"]
    s0 = estado(H, "olha_baixo"); s1 = estado(H, "olha_lado")
    anima_estados(H, [(1, dict(s0, cabeca=0, tronco=0)), (14, s1), (N, s1)], N, vida=0.6)
    A.camera_viva(N, frente=0.04, mao=0.6)


def a11C(N):
    H = A.REG["eu"]; vivo(H, N)
    escala_h(H, N, cresce(1, 20, de=0.5, para=1.0, p=0.03))
    c = cam()
    if c.data.type == "ORTHO":
        o = c.data.ortho_scale
        ortho_curva(N, lambda f: o * lerp(0.93, 1.0, suave5(faixa(f, 1, 20))) * (1 + DERIVA * suave(faixa(f, 20, N))))
    lua = bpy.data.objects.get("lua")
    if lua:
        p0 = Vector(lua.location)
        for f in range(1, N + 1):
            u = 1 - suave5(faixa(f, 20, 70)); lua.location = p0 + Vector((1.6 * u, 0, 0)); lua.rotation_euler.z = 3.0 * u
            key(lua, "location", f, "LINEAR"); key(lua, "rotation_euler", f, "LINEAR")
    for nm in ("ref_t_Lua: 3.474 km", "ref_traco_Lua: 3.474 km"):
        o = bpy.data.objects.get(nm)
        if o:
            aparece([o], 66, 74, N=N)
    A.camera_viva(N, mao=0.0)


# ======================================================================== FALA 12
def a12A(N):
    H = A.REG["eu"]
    S = estado(H, "passagem"); S0 = dict(S, pos=(S["pos"][0], S["pos"][1], S["pos"][2] + 0.18))
    anima_estados(H, [(1, S0), (20, S), (N, S)], N, vida=0.4, mola=False)                                   # pisa em "terceiro" (66,78 s)
    A.camera_viva(N, frente=0.04, mao=0.5, vel=(0.03, 0, 0))


def a12B(N):
    palco_cresce("eu", N, 1, 20, de=0.5)
    for o in [bpy.data.objects.get("terra")]:
        if o:
            p0 = Vector(o.location)
            for f in range(1, N + 1):
                o.rotation_euler.z = 0.4 * (f - 1) / FPS; key(o, "rotation_euler", f, "LINEAR")


def a12C(N):
    H = A.REG["eu"]; vivo(H, N, vida=0.5)
    for s in "FB":
        lid = H.olhos[s + "_lid"]
        for f in range(1, N + 1):
            u = faixa(f, 18, 24) - faixa(f, 26, 32)
            lid.scale.z = max(0.0001, 0.92 * suave(u) + 0.1); key(lid, "scale", f, "LINEAR")
    A.camera_viva(N, frente=0.03, mao=0.5)


# ======================================================================== FALA 13
def a13A(N):
    H = A.REG["eu"]; vivo(H, N, vida=0.6)
    c = cam(); p = Vector(c.location); alvo = Vector((0.0, 0.0, 0.9))
    r = Vector((p.x - alvo.x, p.y - alvo.y)).length; a0 = math.atan2(p.y - alvo.y, p.x - alvo.x)
    pts = []
    for k in range(5):
        f = 1 + int((N - 1) * k / 4); a = a0 + math.radians(75) * (k / 4)
        pts.append((f, (alvo.x + r * math.cos(a), alvo.y + r * math.sin(a), p.z), tuple(alvo)))
    camera_caminho(N, pts)


def a13B(N):
    H = A.REG["eu"]; vivo(H, N)
    escala_h(H, N, cresce(1, 18, de=0.5, para=1.0, p=0.03))
    c = cam()
    o = c.data.ortho_scale
    ortho_curva(N, lambda f: o * lerp(0.93, 1.0, suave5(faixa(f, 1, 18))) * (1 + DERIVA * suave(faixa(f, 18, N))))
    dist = bpy.data.objects.get("dist"); lua = bpy.data.objects.get("lua"); D = None
    if dist:
        D = dist.dimensions.z; z0 = dist.location.z - D / 2
        for f in range(1, N + 1):
            s = suave5(faixa(f, 16, 44)); dist.scale.z = max(s, 0.0001); dist.location.z = z0 + D * s / 2
            key(dist, "scale", f, "LINEAR"); key(dist, "location", f, "LINEAR")
    for nm, f0 in (("lua", 40), ("t_lua", 42), ("t_dist", 30), ("t_terra", 16)):
        ob = bpy.data.objects.get(nm)
        if ob:
            aparece([ob], f0, f0 + 6, N=N)
    A.camera_viva(N, mao=0.0)


def a13C(N):
    H = A.REG["eu"]
    s0 = estado(H, "olha_baixo"); s1 = estado(H, "olha_lado")
    anima_estados(H, [(1, dict(s0, cabeca=0, tronco=0)), (16, s1), (N, s1)], N, vida=0.6)
    lua = bpy.data.objects.get("lua"); aro = bpy.data.objects.get("aro_lua")
    piv = bpy.data.objects.get("orbita_piv")
    if lua and piv:
        p = Vector(lua.location); D = SP_D()
        for f in range(1, N + 1):
            t = 1.19 + 0.0 + 0.5 * (suave(faixa(f, 1, N)) - 0.5)
            q = piv.matrix_world @ Vector((D * math.cos(t), D * math.sin(t), 0.0))
            lua.location = q; key(lua, "location", f, "LINEAR")
            if aro:
                aro.location = q; key(aro, "location", f, "LINEAR")
    A.camera_viva(N, frente=0.03, mao=0.5)


def SP_D():
    return S2.D_LUA


def a13D(N):
    H = A.REG["eu"]
    S = estado(H, "passagem"); S0 = dict(S, pos=(S["pos"][0], S["pos"][1], S["pos"][2] + 0.22))
    anima_estados(H, [(1, S0), (N - 8, S), (N, S)], N, vida=0.3, molas=dict(quadril=(0, 2.4, 0.9), joelho=(0, 2.4, 0.9)))
    c = cam(); p = Vector(c.location)
    for f in range(1, N + 1):
        u = 1 - (1 - faixa(f, 1, N)) ** 2
        c.location = p + Vector((0.12 * u, -0.1 * u, 0.0)); key(c, "location", f, "LINEAR")


for _k, _f in list(globals().items()):
    if _k.startswith("a") and _k[1:2].isdigit() and callable(_f):
        ANIM[_k[1:]] = _f


# ---------------------------------------------------------------- main
BARRA = " ▁▂▃▄▅▆▇█"


def _linha(vs):
    m = max(vs) or 1.0
    return "".join(BARRA[min(8, int(round(8 * v / m)))] for v in vs)


def mede(nome, N, fpb=1):
    """análise de movimento e de enquadramento do plano já animado (sem renderizar):
    câmera: velocidade de deslocamento e de giro, quadro a quadro; TRANCO = a velocidade muda de uma vez; PARADA = anda, para, anda;
    enquadramento: a cabeça dele dentro do quadro (margem de 5%), fora da faixa da legenda (y de 22% a 34% da altura) e com tamanho legível"""
    from bpy_extras.object_utils import world_to_camera_view
    sc = bpy.context.scene; cam_ = sc.camera
    P, F, cab = [], [], []
    for f in range(1, N + 1):
        sc.frame_set(f); bpy.context.view_layer.update()
        P.append(Vector(cam_.matrix_world.translation)); F.append((cam_.matrix_world.to_3x3() @ Vector((0, 0, -1))).normalized())
        r = None
        for h in [x for k, x in humanos().items() if k == "eu"]:
            c = bpy.data.objects.get(h.nome + "_cranio")
            if c is not None and not c.hide_render:
                pts = [world_to_camera_view(sc, cam_, c.matrix_world @ Vector(b)) for b in c.bound_box]
                if min(p.z for p in pts) > 0:
                    r = (min(p.x for p in pts), min(p.y for p in pts), max(p.x for p in pts), max(p.y for p in pts))
                    break
        cab.append(r)
    # o corpo: cabeça, mãos e pés em relação à raiz (tira o crescimento e o passeio do corpo inteiro)
    corpo = {}
    H_ = humanos().get("eu")
    if H_ is not None:
        pecas = [o for o in (bpy.data.objects.get(H_.nome + s) for s in ("_cranio", "_maoF", "_maoB", "_sapatoF", "_sapatoB")) if o and not o.hide_render]
        for o in pecas:
            ps = []
            for f in range(1, N + 1):
                sc.frame_set(f); bpy.context.view_layer.update()
                ps.append((o.matrix_world.translation - H_.raiz.matrix_world.translation) / max(1e-6, H_.raiz.scale.x))
            corpo[o.name] = [(ps[i + 1] - ps[i]).length for i in range(N - 1)]
    ortho = cam_.data.type == "ORTHO"
    vel = [(P[i + 1] - P[i]).length for i in range(N - 1)]
    giro = [math.degrees(F[i].angle(F[i + 1])) for i in range(N - 1)]
    avisos = []
    for rot, vs in (("deslocamento", vel), ("giro", giro)):
        m = max(vs) or 1.0
        if rot == "giro" and m < 0.05:
            continue
        if rot == "deslocamento" and m < 0.004:                         # abaixo de 0,004 u por quadro (0,2% da altura dele) ninguém vê: não é tranco
            continue
        for i in range(2, N - 3):
            if abs(vs[i] - vs[i - 1]) > 0.40 * m and m > (0.4 if rot == "giro" else 0):
                avisos.append(f"TRANCO {rot} q{i + 1} ({vs[i - 1]:.3g}->{vs[i]:.3g})")
        for i in range(2, N - 4):
            if vs[i] <= min(vs[i - 1], vs[i + 1]):
                antes = max(vs[max(0, i - 12):i]); depois = max(vs[i + 1:i + 13])
                if min(antes, depois) > 0.35 * m and vs[i] < 0.15 * min(antes, depois):
                    avisos.append(f"PARADA {rot} q{i + 1}")
    for nm, vs in corpo.items():
        m = max(vs) or 1.0
        if m < 0.02:
            continue
        for i in range(2, N - 3):
            if abs(vs[i] - vs[i - 1]) > 0.45 * m:
                avisos.append(f"TRANCO corpo {nm[3:]} q{i + 1}")
                break
    fora = [f + 1 for f, r in enumerate(cab) if r and (r[0] < 0.05 or r[2] > 0.95 or r[1] < 0.05 or r[3] > 0.95)]
    legenda = [f + 1 for f, r in enumerate(cab) if r and 0.22 < (r[1] + r[3]) / 2 < 0.34]
    pequena = [f + 1 for f, r in enumerate(cab) if r and (r[3] - r[1]) < 0.025]
    if fora:
        avisos.append(f"CABEÇA FORA/NA BORDA q{fora[0]}..q{fora[-1]} ({len(fora)} quadros)")
    if len(legenda) > N * 0.5:
        avisos.append(f"CABEÇA NA FAIXA DA LEGENDA em {len(legenda)}/{N} quadros")
    if pequena and len(pequena) > N * 0.5:
        avisos.append(f"CABEÇA MUITO PEQUENA em {len(pequena)}/{N} quadros")
    if "--serie" in sys.argv: print("SERIE", [round(v * 1000, 2) for v in vel])
    print(f"{nome} N={N} desl {_linha(vel[::fpb])} giro {_linha(giro[::fpb])}" + ("  [ortográfica]" if ortho else ""))
    for t in avisos[:8]:
        print(f"  {nome}: {t}")
    if not avisos:
        print(f"  OK {nome}")


def sync(nome, N):
    """auditoria de sincronia com a voz (sem renderizar): em que instante (s do filme) cada sapato dele toca o chão depois de ter saído, e quando
    ele cresce (de 10% a 95% do salto de escala); compara com as palavras da fala mais próximas"""
    sc = bpy.context.scene; H_ = humanos().get("eu")
    if H_ is None:
        return
    t0 = SH[nome]["t0"]
    pal = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "roteiros", "voz-passos", "palavras.json")))
    perto = lambda t: min(pal, key=lambda w: abs(w["t0"] - t))
    sol = {s: bpy.data.objects.get(f"{H_.nome}_sola{s}") or bpy.data.objects.get(f"{H_.nome}_sapato{s}") for s in "FB"}
    zs = {s: [] for s in "FB"}; esc = []
    for f in range(1, N + 1):
        sc.frame_set(f); bpy.context.view_layer.update()
        k = max(1e-6, H_.raiz.scale.x); esc.append(k)
        for s, o in sol.items():
            if o is not None:
                zs[s].append(min((o.matrix_world @ Vector(c)).z for c in o.bound_box) / k)
    out = []
    chao = min(min(z) for z in zs.values() if z)
    for fl in sorted(set(POUSOS)):
        if 1 <= fl <= N:
            t = t0 + (fl - 1) / FPS; w = perto(t)
            h0 = min(zs[s][fl - 1] for s in zs if zs[s]) - chao; h1 = min(zs[s][max(0, fl - 7)] for s in zs if zs[s]) - chao
            # (o pé que pousa é o mais baixo no quadro do pouso; seis quadros antes ele estava mais alto)
            out.append((t, f"POUSO planejado em {t:.2f} s: pé a {h0:.2f} do chão no quadro (6 quadros antes: {h1:.2f}); palavra \"{w['txt']}\" {w['t0']:.2f} s, diferença {t - w['t0']:+.2f} s"))                      # o chão = o ponto mais baixo que o sapato alcança
    for s, z in zs.items():
        no_ar = 0
        for i, v in enumerate(z):
            if v > chao + 0.045:
                no_ar += 1
            elif no_ar >= 2 and v < chao + 0.03:
                t = t0 + i / FPS; w = perto(t)
                out.append((t, f"PÉ {s} toca o chão em {t:.2f} s  (palavra mais perto: \"{w['txt']}\" {w['t0']:.2f} s, diferença {t - w['t0']:+.2f} s)"))
                no_ar = 0
            elif v <= chao + 0.03:
                no_ar = 0
    if "--serie" in sys.argv:
        for s in zs:
            print("ZSERIE", s, [round(v, 2) for v in zs[s]])
    e0, e1 = esc[0], esc[-1]
    if abs(e1 - e0) > 0.2 * e0:
        a_ = next(i for i, v in enumerate(esc) if abs(v - e0) > 0.1 * abs(e1 - e0)); b_ = next(i for i, v in enumerate(esc) if abs(v - e0) > 0.95 * abs(e1 - e0))
        ta, tb = t0 + a_ / FPS, t0 + b_ / FPS
        out.append((ta, f"CRESCE de {ta:.2f} s a {tb:.2f} s  ({e0 / e1:.0%} -> 100%; palavra no começo: \"{perto(ta)['txt']}\" {perto(ta)['t0']:.2f} s)"))
    for _, l in sorted(out):
        print(f"SYNC {nome}: {l}")


def espaco(nome, N, margem=0.10, mostrar=6):
    """FOLGA em TODOS os quadros (pedido de 25/10/2026: "ele ficou bugando com o ônibus; tem que ter uma visão ampla e dar espaço"): o conferidor de colisão só olha
    5 quadros e só pega malha dentro de malha. Aqui, em cada quadro, a menor distância entre cada peça grande do corpo e cada sólido do cenário (caixa de cada
    peça, em u); abaixo da margem (padrão 0,10 u, uns 6% da altura dele) é aviso, mesmo sem encostar."""
    import colisao_passos as CP
    sc = bpy.context.scene
    ignora = CP.FORA + ("cid", "terra", "ar", "rl", "rf", "som", "onda", "mede", "l_am", "p_", "t_", "topo", "pulso", "cor", "vaso", "man", "mangueira", "chave", "praca", "ponto", "fio", "pil", "txt", "ac", "teto")
    grupos = ("eu", "amigo", "limp", "eu1", "eu2")
    partes_grandes = ("jaqueta", "cranio", "coxa", "canela", "braco", "antebraco", "sapato", "mao", "pelve")
    def caixa(o):
        pts = [o.matrix_world @ Vector(c) for c in o.bound_box]
        return (Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts))), Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts))))
    sc.frame_set(1); bpy.context.view_layer.update()
    solidos = []
    for o in bpy.data.objects:
        if o.type != "MESH" or o.hide_render or o.name.split("_")[0] in grupos or o.name.endswith("_sb") or o.name.startswith(("fq", "eu")):
            continue
        if any(o.name.lower().startswith(k) or ("_" + k) in o.name.lower() for k in ignora):
            continue
        c0, c1 = caixa(o)
        if (c1 - c0).length > 400 or c0.length > 60:             # o céu, o chão e o que está longe demais para importar
            continue
        solidos.append((o.name, c0, c1))
    corpo = [o for o in bpy.data.objects if o.type == "MESH" and o.name.split("_")[0] in grupos and any(k in o.name for k in partes_grandes) and not o.name.endswith("_sb")]
    pior = {}
    for f in range(1, N + 1):
        sc.frame_set(f); bpy.context.view_layer.update()
        for p in corpo:
            if p.hide_render:
                continue
            p0, p1 = caixa(p)
            for nm, c0, c1 in solidos:
                if p.name.split("_")[0] == nm.split("_")[0]:
                    continue
                g = Vector((max(c0.x - p1.x, p0.x - c1.x, 0.0), max(c0.y - p1.y, p0.y - c1.y, 0.0), max(c0.z - p1.z, p0.z - c1.z, 0.0))).length
                if g < margem:
                    k = (p.name, nm)
                    if k not in pior or g < pior[k][0]:
                        pior[k] = (g, f)
    linhas = sorted(pior.items(), key=lambda kv: kv[1][0])
    if not linhas:
        print(f"OK folga {nome}")
    for (pn, sn), (g, f) in linhas[:mostrar]:
        print(f"{nome}: FOLGA {pn} ~ {sn}: {g:.3f} u no quadro {f}")


def main():
    argv = sys.argv[sys.argv.index("--") + 1:]
    nome, pasta = argv[0], argv[1]
    k = float(argv[argv.index("--scale") + 1]) if "--scale" in argv else 0.5
    smp = int(argv[argv.index("--samples") + 1]) if "--samples" in argv else 10
    N = N_de(nome)
    lib.reset(int(1080 * k), int(1920 * k), FPS, smp)
    sc = bpy.context.scene; sc.frame_start, sc.frame_end = 1, N
    SH[nome]["fn"]()
    if nome in ANIM:
        ANIM[nome](N)
    for H in list(humanos().values()):
        if H.raiz.animation_data is None:
            vivo(H, N, seed=sum(map(ord, H.nome)) % 17)
    if sc.camera.animation_data is None:
        A.camera_viva(N, frente=0.06, mao=0.5)
    c_ = sc.camera
    if c_.data.type == "ORTHO" and (c_.data.animation_data is None or c_.data.animation_data.action is None):
        o_ = c_.data.ortho_scale
        ortho_curva(N, lambda f: o_ * (1 + DERIVA * suave(faixa(f, 1, N))))
    if "--sem-suaviza" not in argv:
        A.suaviza(N, sigma=SIGMA)
    if "--mede" in argv:
        mede(nome, N); return
    if "--sync" in argv:
        sync(nome, N); return
    if "--espaco" in argv:
        espaco(nome, N, margem=float(argv[argv.index("--margem") + 1]) if "--margem" in argv else 0.10); return
    if "--colisao" in argv:
        import colisao_passos
        for f in sorted(set([1, max(1, N // 4), max(1, N // 2), max(1, 3 * N // 4), N])):
            sc.frame_set(f); colisao_passos.confere(f"{nome}@{f}", mostrar=6)
        return
    if PROFUNDIDADE and nome[:2] not in ("11", "12", "13"):
        import profundidade as PF
        PF.aplica(abertura=PF.ABERTURA.get(nome, 2.0), enevoa=PF.ENEVOA_POR.get(nome, PF.ENEVOA))
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
