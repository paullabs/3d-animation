"""Animação v3 de "os passos" (plano v3; pedido de 25/10/2026: "quando ele dá um passo já dá um impacto, cresce quase na hora, num bounce
não tão agressivo; faz cara de 'caramba, a cada passo eu cresço'; dá mais um passo e cresce de novo").
Usa o motor do v2 (anim_passos.py) com os planos do story_passos3.py (tudo dentro do mundo). Regra nova:
- CRESCE NO POUSO: no quadro em que o pé toca o chão, o boneco vai do tamanho anterior (metade) ao novo em 6 quadros, passa uns 5% do ponto
  e volta (cresce_pouso); o tremor de câmera e a poeira acontecem no mesmo quadro;
- REAÇÃO: depois do primeiro e do segundo crescimento, ele olha para o próprio corpo, olhos arregalados e boca em O (expressao).
blender -b -P anim_passos3.py -- PLANO PASTA [--scale 0.5] [--samples 10] [--quadros 1,M,N] [--colisao]"""
import os, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy
from mathutils import Vector
import story_passos3 as S3                                 # troca os planos do v2 pelos do v3 (mesmo dicionário SHOTS)
import anim_passos as AP
from anim_passos import A, key, lerp, suave, suave5, faixa, fq, estado, anima_estados, vivo, escala_h, cam, camera_caminho, tremor, aparece, poeira_anim, pouso, FPS
import story_passos2 as S2

ANIM = AP.ANIM


def de_volta(u, c1=1.15):
    """easeOutBack: chega, passa um pouco do ponto (uns 5%) e volta"""
    c3 = c1 + 1.0
    return 1 + c3 * (u - 1) ** 3 + c1 * (u - 1) ** 2


def cresce_pouso(H, N, fl, de=0.5, dur=None):
    """no quadro do pouso o boneco dobra de tamanho em curva de entrada e saída, passa uns 6% do ponto e assenta: 13 quadros (0,55 s), para dar para
    VER ele crescer (pedido de 25/10/2026: "tem que mostrar ele crescendo"); nos planos curtos usa o que sobra do plano. O easeOutBack antigo
    chegava a 95% em 4 quadros (0,17 s): parecia um estalo"""
    dur = dur or max(5, min(13, N - fl - 1))
    c = AP.cresce(fl, fl + dur, de=de, para=1.0, p=0.06)
    escala_h(H, N, c)
    # a altura do corpo (z da raiz) foi calculada para o tamanho inteiro: com o boneco menor os pés ficavam no ar; z acompanha a escala
    import lib
    for fc in lib._fcs(H.raiz):
        if fc.data_path == "location" and fc.array_index == 2:
            for kp in fc.keyframe_points:
                kp.co.y *= c(int(round(kp.co.x)))
                kp.handle_left.y = kp.handle_right.y = kp.co.y
            fc.update()


def susto(H, f0, N, forte=1.0):
    """a cara de 'caramba': olhos crescem, sobrancelhas sobem, boca em O, depois relaxa um pouco"""
    H.expressao([(1, dict(boca="reta", olhos=1.0, brow=0.0)), (f0, dict(boca="o", olhos=1.0 + 0.16 * forte, brow=1.0 * forte)),
                 (min(N, f0 + 30), dict(boca="o", olhos=1.0 + 0.1 * forte, brow=0.6 * forte))], 1, N, piscar=True)


def r(nome):
    def deco(fn):
        ANIM[nome] = fn
        return fn
    return deco


# ======================================================================== FALA 1
@r("1A")
def a1A(N):
    H = A.REG["eu"]; fl = fq("1A", 0.90)
    pouso(H, N, fl, dx=0.0, dy=0.0)
    cresce_pouso(H, N, fl)
    poeira_anim(N, fl, raio=0.9)
    susto(H, fl + 3, N, forte=0.8)
    m = A.REG.get("moca")
    if m:
        P0 = dict(getattr(m, "_ultima", {})); P0["pos"] = tuple(m.raiz.location); P0["rot"] = tuple(math.degrees(v) for v in m.raiz.rotation_euler)
        P1 = dict(P0, cabeca=-26, olha=30, tronco=-4)
        AP.sombra_de(m); m.anima([(1, P0), (fl + 2, P0), (fl + 12, P1), (N, P1)], 1, N, vida=0.8)
    tremor(N, [fl], m=0.02, mao=0.5)


@r("1B")
def a1B(N):
    H = A.REG["eu"]
    s0 = estado(H, "susto"); s1 = estado(H, "olha_mao")
    anima_estados(H, [(1, s0), (10, s1), (N, s1)], N, vida=0.6)
    susto(H, 2, N, forte=1.0)
    A.camera_viva(N, frente=0.06, mao=0.6)


@r("1C")
def a1C(N):
    H = A.REG["eu"]; vivo(H, N, vida=0.6)
    m = A.REG.get("moca")
    if m:
        P0 = dict(getattr(m, "_ultima", {})); P0["pos"] = tuple(m.raiz.location); P0["rot"] = tuple(math.degrees(v) for v in m.raiz.rotation_euler)
        AP.sombra_de(m); m.anima([(1, dict(P0, cabeca=-26, olha=30)), (N, dict(P0, cabeca=-30, olha=24))], 1, N, vida=0.8)
    A.camera_viva(N, frente=0.0, mao=0.8)


# ======================================================================== FALA 2
@r("2A")
def a2A(N):
    for k, h in AP.humanos().items():
        vivo(h, N, seed=sum(map(ord, k)) % 11)
    A.camera_viva(N, mao=0.3, vel=(0.03, 0, 0))


@r("2B")
def a2B(N):
    for k, h in AP.humanos().items():
        vivo(h, N, seed=sum(map(ord, k)) % 11)
    objs = [o for o in (bpy.data.objects.get("marca18"), bpy.data.objects.get("t18")) if o]
    aparece(objs, 10, 16, N=N)
    A.camera_viva(N, mao=0.3)


@r("2C")
def a2C(N):
    for k, h in AP.humanos().items():
        vivo(h, N, seed=sum(map(ord, k)) % 11)
    c = cam(); L0 = Vector(c.location); fw = (c.rotation_euler.to_matrix() @ Vector((0, 0, -1))).normalized()
    T1 = L0 + fw * 9.0
    T0 = Vector((T1.x, T1.y, 0.92)); L1 = L0; L_ini = Vector((L0.x, L0.y, 0.96))
    aparece([o for o in bpy.data.objects if o.name.startswith("r2_rot")], int(N * 0.5), int(N * 0.5) + 6, N=N)
    camera_caminho(N, [(1, tuple(L_ini), tuple(T0)), (N, tuple(L1), tuple(T1))])


@r("2D")
def a2D(N):
    H = A.REG["eu"]; vivo(H, N)
    b = bpy.data.objects.get("onibus")
    if b:
        y1 = b.location.y
        for f in range(1, N + 1):
            u = faixa(f, 1, N); b.location.y = lerp(y1 + 6.0, y1, 1 - (1 - u) ** 2); key(b, "location", f, "LINEAR")
    A.camera_viva(N, mao=0.4)


@r("2E")
def a2E(N):
    H = A.REG["eu"]
    anima_estados(H, [(1, estado(H, "contato")), (8, estado(H, "descida")), (20, estado(H, "alta")), (N, estado(H, "alta"))], N, vida=0.5)
    A.camera_viva(N, mao=0.4)


# ======================================================================== passos com crescimento
def passo_cresce(nome, fl=None, raio=1.0, m=0.022, reage=False, t=None):
    """o pé pousa e ele dobra no quadro da palavra do número (t, em s do filme) ou em fl; o pé toca EXATAMENTE aí (sem mola)"""
    fl0, t0_ = fl, t
    def f(N):
        H = A.REG["eu"]
        fl = max(3, fq(nome, t0_) if t0_ is not None else fl0)
        pouso(H, N, fl)
        cresce_pouso(H, N, fl)
        poeira_anim(N, fl, raio=raio)
        if reage:
            susto(H, fl + 4, N, forte=0.7)
        rot = bpy.data.objects.get("n_pe")
        if rot:
            aparece([rot], fl, fl + 3, N=N)
        tremor(N, [fl], m=m, mao=0.5)
    ANIM[nome] = f


passo_cresce("3A", 4, reage=True)
passo_cresce("4A", t=11.82)                          # "terceiro,"
passo_cresce("6A", t=23.92, raio=1.2, m=0.03)       # "quinto"
for _id in ("8A", "8B", "8C", "8D"):                    # os passos 6, 7, 8 e 9, um a cada 0,42 s: "No nono, você passa o"
    passo_cresce(_id, 3, m=0.03)
passo_cresce("9A", t=44.40, m=0.02)                       # "décimo,"


@r("3B")
def a3B(N):
    H = A.REG["eu"]
    P0 = dict(getattr(H, "_ultima", {})); P0["pos"] = tuple(H.raiz.location); P0["rot"] = (0, 0, 0)
    anima_estados(H, [(1, dict(P0, cabeca=10, olha=0)), (8, P0), (N, P0)], N, vida=0.8)
    susto(H, 7, N, forte=0.8)
    A.camera_viva(N, frente=0.06, mao=0.6)


@r("5A")
def a5A(N):
    H = A.REG["eu"]; fl = fq("5A", 17.98); AP.POUSOS.append(fl)                                   # "quarto,": levanta e pisa dentro da palavra (17,68 a 18,30 s)
    itens = [(1, estado(H, "apoio")), (fl - 9, estado(H, "levanta")), (fl - 4, estado(H, "alta")), (fl, estado(H, "contato")), (fl + 9, estado(H, "descida")), (N, estado(H, "descida"))]
    anima_estados(H, itens, N, vida=0.5, mola=False)
    cresce_pouso(H, N, fl)
    tremor(N, [fl], m=0.02, mao=0.6)


@r("10A")
def a10A(N):
    H = A.REG["eu"]; fl = fq("10A", 53.20)                                   # "doze"
    pouso(H, N, fl); cresce_pouso(H, N, fl)
    tremor(N, [fl], m=0.012, mao=0.5)


@r("11A")
def a11A(N):
    AP.a11A(N)
    cresce_pouso(A.REG["eu"], N, 16)


@r("12A")
def a12A(N):
    AP.a12A(N)
    cresce_pouso(A.REG["eu"], N, fq("12A", 66.78))


@r("13A")
def a13A(N):
    AP.a13A(N)
    cresce_pouso(A.REG["eu"], N, fq("13A", 73.16))


# ======================================================================== medições dentro do mundo (lente longa)
def tele_vivo(N):
    for k, h in AP.humanos().items():
        vivo(h, N, seed=sum(map(ord, k)) % 11)
    A.camera_viva(N, mao=0.25, frente=0.03)


for _id in ("3C", "4B", "5B", "6B", "9B", "10B", "12B"):
    ANIM[_id] = tele_vivo


@r("8E")
def a8E(N):
    tele_vivo(N)
    o = bpy.data.objects.get("linha_burj")
    if o:
        aparece([o], 8, 14, N=N)


@r("9E")
def a9E(N):
    H = A.REG["eu"]; vivo(H, N)
    for nm, f0 in (("visao", 6), ("t150", 22)):
        o = bpy.data.objects.get(nm)
        if o:
            aparece([o], f0, f0 + 10, N=N)
    A.camera_viva(N, mao=0.4, frente=0.05)


@r("11C")
def a11C(N):
    H = A.REG["eu"]; vivo(H, N)
    lua = bpy.data.objects.get("lua")
    if lua:
        p0 = Vector(lua.location)
        for f in range(1, N + 1):
            u = 1 - suave5(faixa(f, 10, 60)); lua.location = p0 + Vector((1.8 * u, 0, 0)); lua.rotation_euler.z = 3.0 * u
            key(lua, "location", f, "LINEAR"); key(lua, "rotation_euler", f, "LINEAR")
    for nm in ("ref_t_Lua: 3.474 km", "ref_traco_Lua: 3.474 km"):
        o = bpy.data.objects.get(nm)
        if o:
            aparece([o], 58, 66, N=N)
    A.camera_viva(N, mao=0.25)


@r("13B")
def a13B(N):
    H = A.REG["eu"]; vivo(H, N)
    for nm, f0 in (("dist", 8), ("t_dist", 26)):
        o = bpy.data.objects.get(nm)
        if o:
            aparece([o], f0, f0 + 12, N=N)
    A.camera_viva(N, mao=0.25)


@r("6E")
def a6E(N):
    for k, h in AP.humanos().items():
        vivo(h, N, seed=sum(map(ord, k)) % 11, vida=0.4)
    for i, nm in enumerate(("t_fio", "t_pal")):
        o = bpy.data.objects.get(nm)
        if o:
            aparece([o], 12 + i * 10, 20 + i * 10, N=N)
    A.camera_viva(N, mao=0.15, frente=0.002)


@r("7B")
def a7B(N):
    AP.a7B(N)


@r("7C")
def a7C(N):
    AP.a7C(N)


if __name__ == "__main__":
    AP.main()
