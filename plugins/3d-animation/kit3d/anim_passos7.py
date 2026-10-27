"""Animação do plano v7 de "os passos" (aprovado em 25/10/2026). Planos em story_passos6.py (falas 1 a 7); da fala 8 em diante vale o v6 (anim_passos3/4).
Regras desta animação:
  - o pé pisa EXATAMENTE na palavra (sem mola nas pernas; `--sync` mede) e ele dobra em 13 quadros a partir da pisada;
  - de frente = o impacto (pé alto, pisada, poeira, rosto de susto); de lado = a medida (a fita sobe, a pílula acende na palavra do número);
  - nada fica parado: cada plano tem um gesto, uma fita que sobe, uma onda que desce ou um coração que pulsa, e a câmera anda.
blender -b -P anim_passos6.py -- PLANO PASTA [--scale 0.5] [--samples 10] [--quadros 1,M,N] [--colisao] [--mede] [--sync]"""
import os, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy
from mathutils import Vector
import story_passos7 as S6                                 # o mundo fixo (mundo7.py) + as falas 1 a 7 (o resto vem do v3)
import story_passos4 as S4
import anim_passos4 as A4                                   # a caminhada, o 1A de frente e os auxiliares
import anim_passos3 as A3
import anim_passos as AP
from anim_passos import A, key, lerp, suave, faixa, fq, estado, anima_estados, vivo, aparece, poeira_anim, tremor, soco_suave, pouso, cada, FPS
from anim_passos3 import cresce_pouso, susto
from anim_passos4 import em, mostra, objs, camera_olhando, trilha_y, liso

ANIM = AP.ANIM
AP.PROFUNDIDADE = True                                      # desfoque pela distância, névoa pelo mapa de profundidade e vinheta (profundidade.py)


def r(nome):
    def deco(fn):
        ANIM[nome] = fn
        return fn
    return deco


def cara(H, N, boca="o", forca=0.7, relaxa=None):
    """a expressão: olhos arregalados e sobrancelha alta que relaxam até o fim do plano (relaxa = quadro em que volta ao normal)"""
    ks = [(1, dict(boca=boca, olhos=1.0 + 0.16 * forca, brow=forca))]
    if relaxa:
        ks.append((relaxa, dict(boca="reta", olhos=1.0, brow=0.0)))
    ks.append((N, ks[-1][1]))
    H.expressao(ks, 1, N, piscar=True)


def sobe_fita(N, f0, f1, fracao=1.0, f_base=None):
    """a fita métrica de pé cresce do chão até 'fracao' da altura dela entre os quadros f0 e f1 (curva de entrada e saída); marcas e números acendem
    quando a fita chega nelas. Antes de f0 ela fica com altura zero."""
    fita = bpy.data.objects.get("rl_fita")
    if fita is None:
        return
    h = fita.dimensions.z; z0 = fita.location.z - h / 2; sz = fita.scale.z; loc0 = fita.location.z
    base_s = fita.scale.z
    for f in range(1, N + 1):
        s = fracao * suave(faixa(f, f0, f1))
        fita.scale.z = max(base_s * s, 1e-4); fita.location.z = z0 + h * s / 2
        key(fita, "scale", f, "LINEAR"); key(fita, "location", f, "LINEAR")
    for o in [o for o in bpy.data.objects if o.name.startswith(("rl_m", "rl_t")) and not o.name.startswith("rl_topo")]:
        zo = o.location.z + (0.03 if o.name.startswith("rl_t") else 0.0)
        alvo = (zo - z0) / h                                   # fração da fita em que a marca fica
        f_ac = next((f for f in range(1, N + 1) if fracao * suave(faixa(f, f0, f1)) >= alvo), None)
        if f_ac is None:
            b = Vector(o.scale)
            for f in range(1, N + 1):
                o.scale = b * 0.0001; key(o, "scale", f, "LINEAR")
        else:
            aparece([o], f_ac, f_ac + 3, N=N)


def camera_lateral(N, vel=(0.0, -0.035, 0.0), frente=0.015, mao=0.3):
    A.camera_viva(N, vel=vel, frente=frente, mao=mao, centro=0.5)


# ======================================================================== 1A: de frente, o 1º impacto (0 a 3,58 s)
@r("1A")
def a1A(N):
    """0,30 s pé B toca | 0,90 "passo" pé F toca | 1,2 a 1,9 s ("que você desse") o joelho B sobe e fica no ar | 2,08 "dobrasse": pisa e dobra (0,55 s)"""
    H = A.REG["eu"]; M = A.REG["amigo"]
    q = lambda t: fq("1A", t)
    xe, xa, y0 = S4.X_EU, S4.X_AM, S4.Y0
    fl = q(2.08); AP.POUSOS.append(fl)
    ye = 0.0
    y1, y2 = ye + 0.28 + 0.34, ye + 0.28
    ch = A4.caminhada(H, [(q(0.30), "B"), (q(0.90), "F")], xe, [y1, y2])
    Pp = A4.com_pos(estado(H, "passagem"), xe, y2 - 0.1)
    Pa = A4.mir(A4.com_pos(estado(H, "alta"), xe, y2 - 0.16))
    Pa2 = dict(Pa, ombro=(-26, 30), abre=(26, 30), cotovelo=(-20, -26), tronco=-4)
    Pc = A4.mir(A4.com_pos(estado(H, "contato"), xe, ye))
    ch += [(q(1.22), A4.mir(Pp)), (q(1.60), Pa), (q(1.88), Pa2), (fl, Pc),
           (fl + 9, em(H, "descida", xe, ye, cabeca=6)),
           (q(2.45), em(H, "olha_baixo", xe, ye, cabeca=20, olha=-22)),
           (q(3.1), em(H, "olha_mao", xe, ye)),
           (N, em(H, "olha_baixo", xe, ye, cabeca=22, olha=-24))]
    ch = [c for c in ch if c[0] <= N]; ch.sort(key=lambda k: k[0])
    AP.sombra_de(H).anima(ch, 1, N, vida=0.3, seed=5, mola=False)
    cresce_pouso(H, N, fl, dur=13)
    susto(H, fl + 5, N, forte=1.0)
    ax, ay = S4.AM_FIM
    cm = A4.caminhada(M, [(q(0.36), "F"), (q(0.96), "B")], xa, [y1 + 0.08, y2 + 0.08])
    cm += [(q(1.3), A4.com_pos(estado(M, "passagem"), xa, y2 + 0.04)),
           (q(1.55), em(M, "respira", xa, y2 + 0.02, cabeca=-16, olha=-22)),
           (q(1.95), em(M, "respira", xa, y2 + 0.02, cabeca=-22, olha=-26)),
           (fl + 8, em(M, "susto", ax + 0.04, ay - 0.03, cabeca=-14, olha=-10)),
           (fl + 16, em(M, "olha_baixo", ax, ay, cabeca=-30, olha=-24)),
           (N, em(M, "olha_baixo", ax, ay, cabeca=-32, olha=-24))]
    cm = [c for c in cm if c[0] <= N]; cm.sort(key=lambda k: k[0])
    AP.sombra_de(M).anima(cm, 1, N, vida=0.3, seed=9, mola=False)
    susto(M, fl + 5, N, forte=0.8)
    poeira_anim(N, fl, raio=0.9)
    yh, ya = trilha_y(H, N), trilha_y(M, N)
    yc = liso([(a + b) / 2 for a, b in zip(yh, ya)], 6)
    rec = lambda f: suave(faixa(f, fl - 5, fl + 12))
    ent = lambda f: suave(faixa(f, q(3.0), N))
    pos = lambda f: (lerp(-0.02, 0.04, rec(f)), yc[f - 1] - lerp(1.7, 3.0, rec(f)) + 0.2 * ent(f), lerp(0.47, 0.62, rec(f)))
    alvo = lambda f: (lerp(-0.02, 0.04, rec(f)), yc[f - 1], lerp(0.49, 1.0, rec(f)))
    camera_olhando(N, pos, alvo, extra=lambda f: (soco_suave(f, [fl], 0.03, osc=0.0), soco_suave(f, [fl], 0.6, osc=0.0)), mao=0.5)


# ======================================================================== 1B: de lado, a fita sobe (3,58 a 8,80 s)
@r("1B")
def a1B(N):
    """3,6 s "Você": olha o amigo | 4,0 a 5,2 s a fita sobe até a cabeça do amigo; 4,58 "um": pílula 1,8 m; o amigo estica o braço (mostra a altura) |
    5,76 a 7,3 s a fita continua até a cabeça dele; 7,32 "três": pílula 3,6 m; ele olha para o amigo e o amigo olha para cima"""
    H = A.REG["eu"]; M = A.REG["amigo"]
    q = lambda t: fq("1B", t)
    ch = [(1, estado(H, "olha_baixo")), (q(4.3), dict(estado(H, "olha_baixo"), cabeca=26, olha=-26)), (q(5.6), dict(estado(H, "olha_baixo"), cabeca=14, olha=-10)),
          (q(6.6), dict(estado(H, "olha_baixo"), cabeca=30, olha=-28)), (N, dict(estado(H, "olha_baixo"), cabeca=28, olha=-26))]
    AP.sombra_de(H).anima(ch, 1, N, vida=0.5, seed=11, mola=False)
    cara(H, N, "o", 0.5, relaxa=q(5.0))
    est = estado(M, "olha_baixo")
    cm = [(1, dict(est, cabeca=-30, olha=-24)), (q(4.2), dict(est, cabeca=-26, olha=-20)), (q(4.6), dict(est, ombro=(-165, 8), cotovelo=(-6, -12), cabeca=-34, olha=-26)), (q(5.5), dict(est, ombro=(-165, 8), cotovelo=(-6, -12), cabeca=-34, olha=-26)),
          (q(5.95), dict(est, cabeca=-30, olha=-24)), (q(7.1), dict(est, cabeca=-38, olha=-30)), (N, dict(est, cabeca=-36, olha=-28))]
    AP.sombra_de(M).anima(cm, 1, N, vida=0.4, seed=13, mola=False)
    cara(M, N, "o", 0.5, relaxa=q(6.0))
    # a fita: até a cabeça do amigo (metade da altura dela) e depois até a cabeça dele
    fita = bpy.data.objects.get("rl_fita")
    if fita is not None:
        h = fita.dimensions.z; z0 = fita.location.z - h / 2; base = fita.scale.z
        f_a0, f_a1, f_b0, f_b1 = q(4.0), q(5.15), q(5.8), q(7.3)
        frac = lambda f: 0.5 * suave(faixa(f, f_a0, f_a1)) + 0.5 * suave(faixa(f, f_b0, f_b1))
        for f in range(1, N + 1):
            s = frac(f); fita.scale.z = max(base * s, 1e-4); fita.location.z = z0 + h * s / 2
            key(fita, "scale", f, "LINEAR"); key(fita, "location", f, "LINEAR")
        for o in [o for o in bpy.data.objects if o.name.startswith(("rl_m", "rl_t")) and not o.name.startswith("rl_topo")]:
            zo = o.location.z + (0.03 if o.name.startswith("rl_t") else 0.0)
            alvo_ = (zo - z0) / h
            f_ac = next((f for f in range(1, N + 1) if frac(f) >= alvo_), None)
            if f_ac is None:
                b = Vector(o.scale)
                for f in range(1, N + 1):
                    o.scale = b * 0.0001; key(o, "scale", f, "LINEAR")
            else:
                aparece([o], f_ac, f_ac + 3, N=N)
    mostra(objs("l_am", "l_am_p_pil", "l_am_p_txt"), q(4.58), q(4.58) + 6, N=N)          # "um": 1,8 m no amigo
    mostra(objs("rl_topo_pil", "rl_topo_txt"), q(7.32), q(7.32) + 6, N=N)               # "três": 3,6 m nele
    camera_lateral(N, vel=(0.0, -0.03, 0.0), frente=0.02)


# ======================================================================== passos de frente (2A, 3A, 6A): o pé alto, a pisada na palavra, o susto
def impacto_frente(nome, t_pisada, raio=1.0, m=0.022, rosto_forca=0.9):
    def f(N):
        H = A.REG["eu"]
        fl = max(3, fq(nome, t_pisada))
        pouso(H, N, fl)
        cresce_pouso(H, N, fl)
        susto(H, fl + 3, N, forte=rosto_forca)
        poeira_anim(N, fl, raio=raio)
        M = A.REG.get("amigo")
        if M is not None:
            est = estado(M, "olha_baixo")
            AP.sombra_de(M).anima([(1, dict(est, cabeca=-26, olha=-20)), (fl + 4, dict(est, cabeca=-26, olha=-20)), (fl + 14, dict(est, cabeca=-38, olha=-30)), (N, dict(est, cabeca=-38, olha=-30))],
                                  1, N, vida=0.5, seed=15, mola=False)
            cara(M, N, "o", 0.8)
        tremor(N, [fl], m=m, frente=0.04, mao=0.5)
        t = bpy.data.objects.get("n_pe")
    ANIM[nome] = f


impacto_frente("2A", 9.38, raio=0.9)                        # "passo," (o 2º)
impacto_frente("3A", 11.82)                                 # "terceiro,"
impacto_frente("6A", 23.92, raio=1.2, m=0.03)               # "quinto"


@r("5A")
def a5A(N):
    """17,36 s ele está de joelhos com as mãos no chão (fim da queda); levanta e PISA em 'quarto' (17,78 s): dobra para 28,8 m"""
    H = A.REG["eu"]; fl = fq("5A", 17.88); AP.POUSOS.append(fl)
    itens = [(1, dict(estado(H, "apoio"))), (5, estado(H, "levanta")), (fl - 4, estado(H, "alta")), (fl, estado(H, "contato")), (fl + 9, estado(H, "descida")), (N, estado(H, "descida"))]
    anima_estados(H, itens, N, vida=0.5, mola=False)
    cresce_pouso(H, N, fl)
    susto(H, fl + 3, N, forte=0.9)
    poeira_anim(N, fl, raio=1.0)
    tremor(N, [fl], m=0.025, frente=0.04, mao=0.6)


# ======================================================================== passos de lado (a medida): 2B, 3B, 5B, 6B
def medida(nome, t_numero, y_amigo_vis=False, vel=(0.0, -0.035, 0.0)):
    """o pé assenta (descida -> de pé olhando para baixo); a fita sobe do chão até o topo dele e a pílula acende na palavra do número (t_numero)"""
    def f(N):
        H = A.REG["eu"]
        fn = fq(nome, t_numero)
        anima_estados(H, [(1, estado(H, "descida")), (9, estado(H, "olha_baixo")), (N, dict(estado(H, "olha_baixo"), cabeca=24, olha=-18))], N, vida=0.5, mola=False)
        cara(H, N, "o", 0.6, relaxa=max(10, N // 2))
        M = A.REG.get("amigo")
        if M is not None:
            est = estado(M, "olha_baixo")
            AP.sombra_de(M).anima([(1, dict(est, cabeca=-38, olha=-30)), (N, dict(est, cabeca=-38, olha=-30))], 1, N, vida=0.5, seed=17, mola=False)
        sobe_fita(N, 1, max(6, fn), 1.0)
        mostra(objs("rl_topo_pil", "rl_topo_txt"), fn, fn + 5, N=N)
        mostra(objs("l_am", "l_am_p_pil", "l_am_p_txt"), 3, 9, N=N)
        camera_lateral(N, vel=vel)
    ANIM[nome] = f


medida("2B", 10.40)                                         # "sete"
medida("3B", 12.68)                                         # "quinze"
medida("5B", 18.88)                                         # "trinta"
medida("6B", 25.58)                                         # "sessenta"


# ======================================================================== 5C e 5D: o grito e a onda que desce
@r("5C")
def a5C(N):
    H = A.REG["eu"]
    anima_estados(H, [(1, estado(H, "olha_baixo")), (9, estado(H, "grito")), (N, estado(H, "grito"))], N, vida=0.6, mola=False)
    H.expressao([(1, dict(boca="reta", olhos=1.0, brow=0.0)), (8, dict(boca="o", olhos=1.1, brow=0.5)), (N, dict(boca="o", olhos=1.1, brow=0.5))], 1, N, piscar=False)
    A.camera_viva(N, frente=0.12, mao=0.5)


@r("5D")
def a5D(N):
    """21,12 s "um": a onda sai da boca; 22,92 s "pés": chega aos pés (câmera lenta); os três tempos e a linha de 25 m; a poça balança no fim"""
    H = A.REG["eu"]; q = lambda t: fq("5D", t)
    anima_estados(H, [(1, estado(H, "grito")), (N, estado(H, "grito"))], N, vida=0.5, mola=False)
    f1 = q(22.92)
    onda = bpy.data.objects.get("onda_desce")
    if onda is not None:
        b = Vector(onda.scale)
        for f in range(1, N + 1):
            u = suave(faixa(f, 1, f1))
            onda.location.z = lerp(1.5, 0.08, u) if f <= f1 else 0.08
            s = lerp(1.0, 1.9, u) if f <= f1 else lerp(1.9, 2.1, faixa(f, f1, N))
            onda.scale = (b.x * s, b.y * s, b.z)
            if f > f1 + 4:
                onda.scale = (b.x * 0.0001, b.y * 0.0001, b.z)
            for p in ("location", "scale"):
                key(onda, p, f, "LINEAR")
    # os três tempos (0, 0,05 e 0,1 s) acendem quando a onda passa; a linha de 25 m aparece logo no começo
    marcos = [(1.5, "som0", "p_t0"), (0.8, "som1", "p_t1"), (0.1, "som2", "p_t2")]
    for z, anel, pil in marcos:
        u = (1.5 - z) / 1.42
        f_m = next((f for f in range(1, N + 1) if suave(faixa(f, 1, f1)) >= u), f1)
        mostra(objs(anel, pil + "_pil", pil + "_txt"), f_m, f_m + 4, N=N)
    mostra(objs("mede_vert", "p_29_pil", "p_29_txt"), 3, 9, N=N)
    ondas = sorted(cada("onda_"), key=lambda o: o.name)
    for i, o in enumerate([o for o in ondas if o.name != "onda_desce"]):
        aparece([o], f1 + i * 4, f1 + i * 4 + 9, s_ini=0.3, N=N)
    camera_lateral(N, vel=(0.0, -0.02, 0.0), frente=0.02)


# ======================================================================== 6C: o prédio de 55 m e a cabeça de 57,6 m
@r("6C")
def a6C(N):
    H = A.REG["eu"]; q = lambda t: fq("6C", t)
    anima_estados(H, [(1, estado(H, "olha_baixo")), (N, dict(estado(H, "olha_baixo"), cabeca=14, olha=-6))], N, vida=0.5, mola=False)
    mostra(objs("p_ele_pil", "p_ele_txt"), q(26.9), q(26.9) + 6, N=N)                   # "Isso" / "é": ele, 57,6 m
    mostra(objs("topo_pred", "topo_pred_p_pil", "topo_pred_p_txt"), q(28.18), q(28.18) + 6, N=N)   # "prédio": a linha e a pílula de 55 m
    c = AP.cam()
    L0 = Vector(c.location)
    for f in range(1, N + 1):
        u = suave(faixa(f, 1, N))
        pos = L0 + Vector((0.0, -0.1 * u, 0.5 * u)); pos.x = L0.x + 0.35 * u              # sobe e chega um pouco mais perto, até o topo
        alvo = Vector((0.0, 0.0, lerp(1.0, 1.7, u)))
        c.location = pos; c.rotation_euler = (alvo - pos).to_track_quat("-Z", "Y").to_euler()
        key(c, "location", f, "LINEAR"); key(c, "rotation_euler", f, "LINEAR")


# ======================================================================== 6D e 6E: o cabelo
@r("6D")
def a6D(N):
    for k, h in AP.humanos().items():
        vivo(h, N, seed=sum(map(ord, k)) % 11, vida=0.4)
    A.camera_viva(N, frente=0.02, mao=0.1)


@r("6E")
def a6E(N):
    for k, h in AP.humanos().items():
        vivo(h, N, seed=sum(map(ord, k)) % 11, vida=0.2)
    q = lambda t: fq("6E", t)
    mostra(objs("t_fio_pil", "t_fio_txt"), 1, 6, N=N)                                    # "cabelo"
    mostra(objs("t_pal_pil", "t_pal_txt"), q(31.40), q(31.40) + 6, N=N)                  # "palito"
    for q_, o in enumerate(cada("fio_ao_fundo")):
        b = o.rotation_euler.copy()
        for f in range(1, N + 1):
            o.rotation_euler = (b.x, b.y + 0.02 * math.sin(2 * math.pi * (f / 24.0) * 0.4 + q_), b.z); key(o, "rotation_euler", f, "LINEAR")
    A.camera_viva(N, frente=0.01, mao=0.1)


# ======================================================================== 7A, 7B, 7C: o coração
@r("7A")
def a7A(N):
    H = A.REG["eu"]
    anima_estados(H, [(1, estado(H, "olha_baixo")), (N, dict(estado(H, "olha_baixo"), cabeca=10, olha=0))], N, vida=1.4, mola=False)       # o peito respira fundo (vida maior)
    for i, o in enumerate(cada("pulso")):
        b = Vector(o.scale)
        for f in range(1, N + 1):
            t = (f - 1) / FPS; ph = (t * 1.25 + 0.5 * i * 0.3) % 1.0
            s = (0.4 + 0.9 * ph) if ph < 0.45 else 0.0001
            o.scale = (b.x * s, b.y * s, b.z * s) if s > 0.0001 else (0.0001, 0.0001, 0.0001); key(o, "scale", f, "LINEAR")
    camera_lateral(N, vel=(0.0, -0.03, 0.0), frente=0.02)


@r("7B")
def a7B(N):
    AP.a7B(N)


@r("7C")
def a7C(N):
    AP.a7C(N)
    q = lambda t: fq("7C", t)
    mostra(objs("t16_pil", "t16_txt"), 8, 16, N=N)


if __name__ == "__main__":
    AP.main()
