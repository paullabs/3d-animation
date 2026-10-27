"""Animação da abertura v4 de "os passos" (aprovada em 25/10/2026: "anima a abertura v4"). Planos em story_passos4.py; da fala 4 em diante
vale a animação do v3 (anim_passos3.py).
  1A: os dois andam de frente (caminhada do kit, cada um com o seu ritmo); a câmera anda para trás no ritmo deles; a linha de 1,8 m vai junto
      sobre as duas cabeças; ele levanta o pé (antecipação), pousa no "passo" e dobra num pulinho (cresce_pouso), com poeira e o chão
      tremendo; a câmera recua e sobe no impacto (curva, sem tranco); o amigo se assusta, dá um passinho para trás e olha para cima.
  1B: a reação de perto: do olhar para o amigo ao olhar para as mãos, cara de "caramba".
  1C: o segundo passo: levanta, pousa no "passo" e dobra de novo; as linhas de 7,2 m e de 1,8 m.
blender -b -P anim_passos4.py -- PLANO PASTA [--scale 0.5] [--samples 10] [--quadros 1,M,N] [--colisao] [--mede]"""
import os, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy
from mathutils import Vector, Euler
import story_passos4 as S4                                 # troca as falas 1 a 3 (e mantém o v3 do resto)
import anim_passos3 as A3                                  # as animações do v3 (fala 4 em diante), cresce_pouso e susto
import anim_passos as AP
from anim_passos import A, key, lerp, suave, faixa, fq, estado, anima_estados, vivo, aparece, some, poeira_anim, tremor, soco_suave, FPS
from anim_passos3 import cresce_pouso, susto

ANIM = AP.ANIM


def r(nome):
    def deco(fn):
        ANIM[nome] = fn
        return fn
    return deco


def em(H, nome, x, y, **extra):
    """o estado da pose 'nome' com o boneco em (x, y); extra troca ângulos (cabeça, olhar...)"""
    H.raiz.location.x, H.raiz.location.y = x, y
    P = estado(H, nome); P.update(extra)
    return P


def mostra(objs, f0, f1, f2=None, f3=None, N=None):
    """aparece em curva de f0 a f1 e, se f2/f3, some de f2 a f3 (escala), sem pular"""
    for o in objs:
        b = Vector(o.scale)
        for f in range(1, N + 1):
            s = suave(faixa(f, f0, f1))
            if f2 is not None:
                s *= 1 - suave(faixa(f, f2, f3))
            o.scale = b * max(s, 0.0001); key(o, "scale", f, "LINEAR")


def objs(*nomes):
    return [o for o in (bpy.data.objects.get(n) for n in nomes) if o]


def camera_olhando(N, pos, alvo, extra=None, seed=21, mao=0.5):
    """câmera quadro a quadro: posição e alvo (funções do quadro), balanço de mão em senos lentos e, se houver, um balanço de impacto"""
    c = bpy.context.scene.camera
    for f in range(1, N + 1):
        t = (f - 1) / FPS
        L = Vector(pos(f)); T = Vector(alvo(f))
        L += Vector((A.mao_ruido(t, seed, 0.004 * mao), A.mao_ruido(t, seed + 1, 0.003 * mao), A.mao_ruido(t, seed + 2, 0.004 * mao)))
        rot = (T - L).to_track_quat("-Z", "Y").to_euler()
        dz, drx = extra(f) if extra else (0.0, 0.0)
        L.z += dz
        rot = Euler((rot.x + math.radians(drx + A.mao_ruido(t, seed + 3, 0.25 * mao)), rot.y, rot.z + math.radians(A.mao_ruido(t, seed + 5, 0.25 * mao))))
        c.location = L; c.rotation_euler = rot
        key(c, "location", f, "LINEAR"); key(c, "rotation_euler", f, "LINEAR")


def trilha_y(H, N):
    """onde o boneco está em y, quadro a quadro (depois da animação)"""
    sc = bpy.context.scene; ys = []
    for f in range(1, N + 1):
        sc.frame_set(f); ys.append(H.raiz.matrix_world.translation.y)
    return ys


def liso(v, r_=6):
    """média móvel (tira o vaivém da passada do caminho da câmera)"""
    n = len(v)
    return [sum(v[max(0, i - r_):min(n, i + r_ + 1)]) / (min(n, i + r_ + 1) - max(0, i - r_)) for i in range(n)]


# ---------------------------------------------------------------- a caminhada com o pé tocando no quadro certo
LADO_ESP = ("quadril", "joelho", "tornozelo", "ombro", "cotovelo", "abre", "punho")


def mir(P):
    """o mesmo estado com as pernas e os braços trocados (F <-> B): a perna que estava à frente passa a ser a de trás"""
    Q = dict(P)
    for k in LADO_ESP:
        if k in Q and isinstance(Q[k], (tuple, list)) and len(Q[k]) == 2:
            Q[k] = (Q[k][1], Q[k][0])
    if "giro" in Q:
        Q["giro"] = -Q["giro"]
    return Q


def com_pos(P, x, y):
    Q = dict(P); Q["pos"] = (x, y, P["pos"][2]); return Q


def caminhada(H, contatos, x, ys, grande=None):
    """chaves de uma caminhada em que o pé toca o chão EXATAMENTE nos quadros 'contatos' (a conferência --sync mede). contatos = [(quadro, lado)], lado
    'F' ou 'B' = o pé que pousa; ys = o y do corpo em cada contato; grande = (lado, quadro_do_pico) põe um joelho alto (pose 'alta') antes do último contato.
    Entre dois contatos vem a passagem (a perna de trás passa pela de apoio). Retorna [(quadro, estado)] para H.anima(..., mola=False): sem mola não
    há atraso, o pé chega no quadro da chave (com mola o pouso atrasava 0,6 s)"""
    ch = []
    base = em(H, "contato", x, ys[0])
    for n, ((fc, lado), y) in enumerate(zip(contatos, ys)):
        P = com_pos(estado(H, "contato"), x, y)
        ch.append((fc, P if lado == "F" else mir(P)))
        if n + 1 < len(contatos):
            f2, l2 = contatos[n + 1]; ym = (y + ys[n + 1]) / 2
            Pm = com_pos(estado(H, "passagem"), x, ym)
            fm = (fc + f2) // 2
            if grande and n + 2 == len(contatos):                     # o passo grande: a perna sobe alto antes de pousar
                fm = fc + (f2 - fc) // 3
                ch.append((fm, Pm if lado == "F" else mir(Pm)))
                Pa = com_pos(estado(H, "alta"), x, ym + (ys[n + 1] - ym) * 0.4)
                ch.append((f2 - max(5, int((f2 - fc) * 0.4)), Pa if l2 == "F" else mir(Pa)))
            else:
                ch.append((fm, Pm if lado == "F" else mir(Pm)))
    return ch


# ======================================================================== 1A
@r("1A")
def a1A(N):
    """Plano de sincronia (palavra -> ação), medido por --sync:
    0,30 s  pé B toca (caminhada normal)            | 0,90 s "passo": pé F toca (cada passo)
    1,28-1,66 "que você desse": o pé B sobe, joelho alto  | 1,66-1,95 o pé fica no ar (tensão); ele abre os braços de equilíbrio
    2,08 "dobrasse": o pé B PISA com força e ele DOBRA (13 quadros, 0,55 s); poeira; a câmera recua; o amigo se assusta
    2,66-2,84 "a sua altura?": olha as mãos | 3,58 "Você": olha o amigo | 4,58 "um metro e oitenta": linha 1,8 m no amigo | 7,2 "três": linha 3,6 m nele
    (De frente o passo curto quase não se vê: o que se lê é o joelho alto e o pé suspenso, por isso o passo é um joelho alto, não vários passinhos.)"""
    H = A.REG["eu"]; M = A.REG["amigo"]
    q = lambda t: fq("1A", t)
    xe, xa, y0 = S4.X_EU, S4.X_AM, S4.Y0
    fl = q(2.08); AP.POUSOS.append(fl)
    ye = 0.0
    y1, y2 = ye + 0.28 + 0.34, ye + 0.28                              # onde o corpo está nos dois toques da caminhada; o pouso é em y = 0
    ch = caminhada(H, [(q(0.30), "B"), (q(0.90), "F")], xe, [y1, y2])
    Pp = com_pos(estado(H, "passagem"), xe, y2 - 0.1)
    Pa = mir(com_pos(estado(H, "alta"), xe, y2 - 0.16))               # B no alto (a pose "alta" tem o F no alto)
    Pa2 = dict(Pa, ombro=(-26, 30), abre=(26, 30), cotovelo=(-20, -26), tronco=-4)   # o pé suspenso: os braços abrem de equilíbrio
    Pc = mir(com_pos(estado(H, "contato"), xe, ye))
    ch += [(q(1.22), mir(Pp)),                                        # o pé B começa a subir ("que")
           (q(1.60), Pa),                                              # joelho alto ("desse")
           (q(1.88), Pa2),                                             # suspenso
           (fl, Pc),                                                   # pisa em "dobrasse"
           (fl + 9, em(H, "descida", xe, ye, cabeca=6)),
           (q(2.45), em(H, "olha_baixo", xe, ye, cabeca=20, olha=-22)),   # "a": olha o próprio corpo
           (q(3.0), em(H, "olha_mao", xe, ye)),                        # "altura?": olha as mãos
           (q(3.55), em(H, "olha_mao", xe, ye, cabeca=30)),
           (q(3.9), em(H, "olha_baixo", xe, ye, cabeca=22, olha=-24)),   # "Você começa": olha o amigo
           (q(5.9), em(H, "olha_baixo", xe, ye, cabeca=24, olha=-24)),
           (N, em(H, "olha_baixo", xe, ye, cabeca=22, olha=-24))]
    ch.sort(key=lambda k: k[0])
    AP.sombra_de(H).anima(ch, 1, N, vida=0.3, seed=5, mola=False)
    cresce_pouso(H, N, fl, dur=13)                                    # a partir do pouso: 0,55 s de crescimento visível
    susto(H, fl + 5, N, forte=1.0)
    # o amigo anda no mesmo ritmo, para de andar e fica olhando para ele (vira a cabeça quando o pé sobe), e se assusta quando ele pisa
    ax, ay = S4.AM_FIM
    cm = caminhada(M, [(q(0.36), "F"), (q(0.96), "B")], xa, [y1 + 0.08, y2 + 0.08])
    cm += [(q(1.3), com_pos(estado(M, "passagem"), xa, y2 + 0.04)),
           (q(1.55), em(M, "respira", xa, y2 + 0.02, cabeca=-16, olha=-22)),     # parou e olha para ele
           (q(1.95), em(M, "respira", xa, y2 + 0.02, cabeca=-22, olha=-26)),
           (fl + 8, em(M, "susto", ax + 0.04, ay - 0.03, cabeca=-14, olha=-10)),
           (fl + 16, em(M, "olha_baixo", ax, ay, cabeca=-30, olha=-24)),
           (N, em(M, "olha_baixo", ax, ay, cabeca=-32, olha=-24))]
    cm.sort(key=lambda k: k[0])
    AP.sombra_de(M).anima(cm, 1, N, vida=0.3, seed=9, mola=False)
    susto(M, fl + 5, N, forte=0.8)
    poeira_anim(N, fl, raio=0.9)
    # a câmera: travelling para trás na velocidade deles; antes do pouso começa a recuar e subir (cabe o corpo todo enquanto ele cresce);
    # depois, um empurrão lento para dentro até o fim (a cena não fica parada)
    yh, ya = trilha_y(H, N), trilha_y(M, N)
    yc = liso([(a + b) / 2 for a, b in zip(yh, ya)], 6)
    rec = lambda f: suave(faixa(f, fl - 5, fl + 12))
    ent = lambda f: suave(faixa(f, q(3.2), N))
    pos = lambda f: (lerp(-0.02, 0.04, rec(f)), yc[f - 1] - lerp(1.7, 3.0, rec(f)) + 0.25 * ent(f), lerp(0.47, 0.62, rec(f)))
    alvo = lambda f: (lerp(-0.02, 0.04, rec(f)), yc[f - 1], lerp(0.49, 1.0, rec(f)))
    camera_olhando(N, pos, alvo, extra=lambda f: (soco_suave(f, [fl], 0.03, osc=0.0), soco_suave(f, [fl], 0.6, osc=0.0)), mao=0.5)
    mostra(objs("m18", "m18_t"), q(4.58), q(4.58) + 6, N=N)           # "um metro e oitenta": a linha no amigo
    mostra(objs("l36", "l36_t"), q(7.2), q(7.2) + 6, N=N)             # "três": a linha nele


# ======================================================================== 1B
@r("1B")
def a1B(N):
    H = A.REG["eu"]; M = A.REG["amigo"]
    x = S4.X_EU
    anima_estados(H, [(1, em(H, "olha_baixo", x, 0.0, cabeca=22, olha=-24)), (9, em(H, "olha_mao", x, 0.0)), (N, em(H, "olha_mao", x, 0.0, cabeca=34))], N, vida=0.6, seed=4)
    H.expressao([(1, dict(boca="o", olhos=1.1, brow=0.6)), (8, dict(boca="o", olhos=1.18, brow=1.0)), (N, dict(boca="o", olhos=1.14, brow=0.8))], 1, N, piscar=False)
    vivo(M, N, seed=6, vida=0.6)
    M.expressao([(1, dict(boca="o", olhos=1.12, brow=0.8)), (N, dict(boca="o", olhos=1.12, brow=0.8))], 1, N, piscar=False)
    A.camera_viva(N, frente=0.1, mao=0.4)


# ======================================================================== 1C
@r("1C")
def a1C(N):
    """8,80 s "No": pé F toca; sobe o pé B (joelho alto) e PISA em "passo," (9,38 s) dobrando de novo; 10,12 "são": olha o amigo; 10,40 "sete": linha 7,2 m"""
    H = A.REG["eu"]; M = A.REG["amigo"]
    q = lambda t: fq("1C", t)
    fl = q(9.38); x = 0.06; AP.POUSOS.append(fl)
    ch = caminhada(H, [(1, "F"), (fl, "B")], x, [0.4, 0.0], grande=True)
    ch += [(fl + 9, em(H, "descida", x, -0.02, cabeca=6)),
           (fl + 14, em(H, "olha_baixo", x, -0.02, cabeca=24, olha=-16)),
           (q(10.12), em(H, "olha_baixo", x, -0.02, cabeca=28, olha=-20)),
           (N, em(H, "olha_baixo", x, -0.02, cabeca=26, olha=-18))]
    ch.sort(key=lambda k: k[0])
    AP.sombra_de(H).anima(ch, 1, N, vida=0.4, seed=7, mola=False)
    cresce_pouso(H, N, fl, dur=13)
    H.expressao([(1, dict(boca="o", olhos=1.12, brow=0.8)), (fl + 3, dict(boca="o", olhos=1.2, brow=1.0)), (N, dict(boca="o", olhos=1.14, brow=0.8))], 1, N, piscar=True)
    vivo(M, N, seed=8, vida=0.6)
    poeira_anim(N, fl, raio=0.8)
    tremor(N, [fl], m=0.02, mao=0.4)
    mostra(objs("l72", "l72_t", "m18", "m18_t"), q(10.4), q(10.4) + 6, N=N)


if __name__ == "__main__":
    AP.main()
