import os
"""Peças 3D para planos de cinema (pedido de 23/10/2026: "câmera de 12 mm na ponta da mão, mostrando a cabeça da mosca que ele pegou;
quando o copo cai, a câmera vem para baixo; o ar do ambiente tem de ter o efeito de que ele conseguiu pegar").
Tudo com o mesmo sombreado do herói 3D (heroi3d.estilo) e visível de qualquer ângulo:
- mosca: corpo, cabeça com olhos vermelhos grandes, asas claras que batem (rápido no tempo normal, devagar em câmera lenta) e patas;
- copo3d: copo de vidro com água (a parte cheia azul, a vazia clara), borda branca, e gotas que sobem e voltam;
- poeira: grãos de poeira 3D suspensos no ar, que andam em câmera lenta e são empurrados pela onda do acerto;
- rastro: risco de luz no caminho da mão (some em poucos quadros);
- onda: anel de partículas que se abre no instante do acerto (o "ar" reagindo)."""
import math, random
import bpy
from mathutils import Vector
from lib import empty, key
from heroi3d import estilo, plano, esfera, tubo, loft


def tempo_lento(f_ini, lento=0.1, dur=8):
    """velocidade do tempo que cai de 1 para 'lento' em curva in/out (dur quadros a partir de f_ini), em vez de um degrau"""
    def v(f):
        u = min(1.0, max(0.0, (f - f_ini) / dur)); u = u * u * u * (u * (6 * u - 15) + 10)   # smootherstep: entra e sai sem quina
        return 1.0 + (lento - 1.0) * u
    return v


def mosca(nome, loc, escala=2.0, pai=None):
    """mosca (1 cm x escala): devolve (raiz, [asa esquerda, asa direita]); a frente é -Y"""
    r = empty(nome, pai, loc); r.scale = (escala,) * 3
    corpo, olho, asa = estilo("#525b6e", "#2a2f3a"), estilo("#ea4038", "#9a221c"), estilo("#d8ecf6", "#a8c4d4")
    esfera(nome + "_torax", 0.0045, 0.005, 0.0042, corpo, r, (0, 0, 0), contorno=0.0006, seg=20, an=12)
    esfera(nome + "_abd", 0.0038, 0.0062, 0.0034, corpo, r, (0, 0.0068, -0.0006), contorno=0.0006, seg=20, an=12)
    esfera(nome + "_cab", 0.0034, 0.003, 0.0032, corpo, r, (0, -0.0052, 0.0004), contorno=0.0005, seg=18, an=10)
    for k, x in enumerate((-0.0024, 0.0024)):
        esfera(f"{nome}_olho{k}", 0.0022, 0.0022, 0.0026, olho, r, (x, -0.0058, 0.001), contorno=0.0004, seg=16, an=10)
        esfera(f"{nome}_brilho{k}", 0.0006, 0.0006, 0.0006, plano("#ffffff"), r, (x * 1.15, -0.0078, 0.0022), contorno=0.0, seg=8, an=6)
    asas = []
    for k, sg in enumerate((-1, 1)):
        j = empty(f"{nome}_asaj{k}", r, (sg * 0.0012, 0.0005, 0.0036))
        a = esfera(f"{nome}_asa{k}", 0.0035, 0.0062, 0.0004, asa, j, (sg * 0.0036, 0.0035, 0), contorno=0.0003, seg=16, an=8)
        a.rotation_euler = (0, 0, math.radians(sg * 18)); asas.append(j)
    for k in range(6):
        sg = -1 if k < 3 else 1; yy = -0.002 + 0.0025 * (k % 3)
        tubo(f"{nome}_pata{k}", [(sg * 0.003, yy, -0.002), (sg * 0.0065, yy - 0.001, -0.0045), (sg * 0.0075, yy, -0.007)], [0.0005] * 3, corpo, r, seg=6, tampa=2, contorno=0.0)
    return r, asas


def bate_asas(asas, f0, f1, periodo=2.0, amp=55):
    """as asas sobem e descem: período em quadros (2 = borrão de tão rápido; 10 = câmera lenta).
    periodo pode ser uma função do quadro (a fase é somada quadro a quadro: a batida desacelera em curva, sem pulo)"""
    fase = 0.0
    for f in range(f0, f1 + 1):
        fase += 2 * math.pi / (periodo(f) if callable(periodo) else periodo)
        a = math.radians(amp * math.sin(fase))
        for j, sg in zip(asas, (-1, 1)):
            j.rotation_euler = (0, sg * a, 0); key(j, "rotation_euler", f, "LINEAR")


def voo(r, f0, f1, centro, raio=(0.25, 0.2, 0.15), seed=3, vel=1.0, ate=None, f_ate=None):
    """voo em zigue-zague em volta de 'centro' (vel = velocidade do tempo: 1 normal, 0,1 câmera lenta);
    se 'ate' for dado, termina indo em linha reta até esse ponto no quadro f_ate"""
    rnd = random.Random(seed); fases = [rnd.uniform(0, 6.28) for _ in range(6)]; t = 0.0
    pts = {}
    for f in range(f0, f1 + 1):
        v = vel(f) if callable(vel) else vel
        t += v / 24.0
        p = Vector((centro[0] + raio[0] * (0.7 * math.sin(7.3 * t + fases[0]) + 0.3 * math.sin(17.1 * t + fases[1])),
                    centro[1] + raio[1] * (0.7 * math.sin(5.9 * t + fases[2]) + 0.3 * math.sin(13.7 * t + fases[3])),
                    centro[2] + raio[2] * (0.7 * math.sin(6.7 * t + fases[4]) + 0.3 * math.sin(15.3 * t + fases[5]))))
        pts[f] = p
    for f in range(f0, f1 + 1):
        p = pts[f]
        if ate is not None and f_ate is not None and f >= f_ate - 8:
            u = min(1.0, (f - (f_ate - 8)) / 8.0); u = u * u * (3 - 2 * u)
            p = p.lerp(Vector(ate), u)
        r.location = p
        d = (pts.get(f + 1, p) - pts.get(f - 1, p))
        if d.length > 1e-6:
            r.rotation_euler = (-d).to_track_quat("-Y", "Z").to_euler()
        key(r, "location", f, "LINEAR"); key(r, "rotation_euler", f, "LINEAR")


def copo3d(nome, loc, escala=1.0, pai=None, cheio=0.62):
    """copo de vidro com água (raio 0,032 embaixo, 0,04 em cima, 0,11 de altura); origem no centro do fundo"""
    r = empty(nome, pai, loc); r.scale = (escala,) * 3
    h = 0.11; zc = h * cheio
    agua = [(0.0, 0.032, 0.032), (0.004, 0.0326, 0.0326)] + [(zc * k / 6, 0.032 + 0.008 * (zc * k / 6) / h, 0.032 + 0.008 * (zc * k / 6) / h) for k in range(1, 7)]
    loft(nome + "_agua", agua, estilo("#5fb0e0", "#3a86b8", limiar=0.42), r, expo=2.0, seg=40, contorno=0.0012)
    vazio = [(zc + (h - zc) * k / 6, 0.032 + 0.008 * (zc + (h - zc) * k / 6) / h, 0.032 + 0.008 * (zc + (h - zc) * k / 6) / h) for k in range(0, 7)]
    loft(nome + "_vidro", vazio, estilo("#d6eef7", "#a9cfe0", limiar=0.42), r, expo=2.0, seg=40, contorno=0.0012, fechar=False)
    tubo(nome + "_borda", [(0.04 * math.cos(2 * math.pi * k / 40), 0.04 * math.sin(2 * math.pi * k / 40), h) for k in range(41)], [0.0022] * 41, plano("#ffffff"), r, seg=8, tampa=2, contorno=0.0)
    esfera(nome + "_nivel", 0.0368, 0.0368, 0.0012, plano("#b9e4f8"), r, (0, 0, zc), contorno=0.0, seg=40, an=6)
    tubo(nome + "_brilho", [(-0.026, -0.03, 0.02), (-0.03, -0.033, 0.095)], [0.0024, 0.0024], plano("#ffffff"), r, seg=8, tampa=3, contorno=0.0)
    return r


def gotas(nome, pai, n=9, seed=4, z0=0.07):
    """gotas de água (esferas) em volta da boca do copo, filhas dele; animar com sobe_volta"""
    rnd = random.Random(seed); g = []
    for k in range(n):
        rr = rnd.uniform(0.004, 0.009)
        o = esfera(f"{nome}_{k}", rr, rr, rr * 1.15, estilo("#7cc6ee", "#4a98c8"), pai, (0, 0, z0), contorno=0.0008, seg=14, an=10)
        o["dir"] = (rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(0.6, 1.4)); g.append(o)
    return g


def sobe_volta(gs, f0, f_pico, f1, alcance=0.09, z0=0.07):
    """as gotas saem do copo em câmera lenta (f0 -> f_pico) e voltam para dentro (f_pico -> f1)"""
    for o in gs:
        dx, dy, dz = o["dir"]
        for f in range(f0 - 1, f1 + 2):
            if f < f0 or f > f1:
                u = 0.0
            elif f <= f_pico:                                                 # sai rápido e freia no alto (ease out)
                x = (f - f0) / max(1, f_pico - f0); u = 1 - (1 - x) ** 3
            else:                                                             # volta acelerando e entra suave no copo (ease in-out)
                x = (f - f_pico) / max(1, f1 - f_pico); u = 1 - x * x * x * (x * (6 * x - 15) + 10)
            o.location = (dx * alcance * 0.45 * u, dy * alcance * 0.45 * u, z0 + dz * alcance * u)
            n_ = 3                                                            # nasce e some crescendo/encolhendo em 3 quadros
            k_ = min(1.0, max(0.0, (f - f0 + 1) / n_), max(0.0, (f1 + 1 - f) / n_)) if f0 <= f <= f1 else 0.0
            s_ = max(0.0001, 1 - (1 - k_) ** 2)
            o.scale = (s_,) * 3
            key(o, "location", f, "LINEAR"); key(o, "scale", f, "LINEAR")


def poeira(nome, centro, caixa=(1.4, 1.0, 1.2), n=90, f0=0, f1=200, vel=None, seed=8, empurra=None, cor="#fff2d0", longe=(), tam=(0.0025, 0.007)):
    """grãos de poeira 3D (pequenas esferas claras) que flutuam devagar; vel(f) = velocidade do tempo;
    empurra = (quadro, centro, força): no instante do acerto os grãos perto do centro fogem para fora (a onda de ar)"""
    if os.environ.get("LIMPO"):                                             # passe limpo: a poeira de partículas vira ruído no Kling
        return None
    rnd = random.Random(seed); m = plano(cor); out = []
    for k in range(n):
        p0 = Vector((centro[0] + rnd.uniform(-caixa[0], caixa[0]) / 2, centro[1] + rnd.uniform(-caixa[1], caixa[1]) / 2, centro[2] + rnd.uniform(-caixa[2], caixa[2]) / 2))
        rr = rnd.uniform(*tam)
        if any((p0 - Vector(pt)).length < r_ for pt, r_ in longe):      # nada de grão colado na lente (vira um disco borrado)
            continue
        o = esfera(f"{nome}{k}", rr, rr, rr, m, None, tuple(p0), contorno=0.0, seg=8, an=6)
        dv = Vector((rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(-0.6, 0.4))) * 0.05
        t = 0.0; p = p0.copy()
        for f in range(f0, f1 + 1, 2):
            v = vel(f) if vel else 1.0
            p = p + dv * (2 * v / 24.0)
            q = p.copy()
            if empurra:
                fe, ce, forca = empurra; ce = Vector(ce)
                if f >= fe:
                    d = q - ce; dist = max(0.05, d.length)
                    if dist < 0.6:
                        q = q + d.normalized() * forca * (1 - dist / 0.6) * (1 - math.exp(-(f - fe) / 4.0))
            o.location = q; key(o, "location", f, "LINEAR")
        out.append(o)
    return out


def _curva(nome, pts, cor, ciclo=False, raios=None):
    cu = bpy.data.curves.new(nome, "CURVE"); cu.dimensions = "3D"; cu.fill_mode = "FULL"; cu.bevel_resolution = 3
    sp = cu.splines.new("POLY"); sp.points.add(len(pts) - 1); sp.use_cyclic_u = ciclo
    for k, q in enumerate(pts):
        sp.points[k].co = (q[0], q[1], q[2], 1.0)
        if raios:
            sp.points[k].radius = raios[k]
    o = bpy.data.objects.new(nome, cu); bpy.context.scene.collection.objects.link(o); cu.materials.append(plano(cor))
    return o


def rastro(nome, pts, f0, dur=7, raio=0.006, cor="#fffaf0"):
    """risco de luz no caminho da mão (pts = posições reais da mão quadro a quadro): fino no começo, grosso na mão;
    aparece em f0 e afina até sumir em 'dur' quadros, sem sair do lugar"""
    n = len(pts)
    o = _curva(nome, pts, cor, raios=[0.15 + 0.85 * (k / (n - 1)) ** 1.5 for k in range(n)])
    cu = o.data
    for f in range(f0 - 1, f0 + dur + 1):
        u = (f - f0) / dur
        cu.bevel_depth = 0.0 if f < f0 else raio * max(0.0, 1 - u) ** 1.4
        cu.keyframe_insert("bevel_depth", frame=f)
    return o


def onda(nome, centro, f0, normal=(0, 1, 0), raio=0.45, dur=14, esp=0.006, cor="#fff6dc", n=None, eixo=None, eco=True):
    """onda de ar: um anel fino que se abre a partir do centro no instante do acerto e afina até sumir.
    O anel fica de frente para 'normal' (use a direção da câmera)"""
    if eixo == "Z":
        normal = (0, 0, 1)
    if eco:
        print(f"RING {nome} {f0} {raio}")                                   # o plano de som lê daqui: cada onda tem o seu som no mesmo quadro
    if os.environ.get("LIMPO"):                                             # passe limpo para o Kling: nada de anel desenhado
        return None
    pts = [(math.cos(2 * math.pi * k / 72), math.sin(2 * math.pi * k / 72), 0.0) for k in range(72)]
    o = _curva(nome, pts, cor, ciclo=True)
    o.location = centro; o.rotation_euler = Vector(normal).normalized().to_track_quat("Z", "Y").to_euler()
    cu = o.data
    # (23/10/2026, "ondas mais fluidas"): dura 35% mais; abre em curva exponencial (sai rápido e desacelera como ar de verdade);
    # a espessura nasce em 3 quadros (não aparece já grossa) e afina devagar; um eco mais fino e menor vem logo atrás
    dur = int(round(dur * 1.35)); na = max(2.0, dur * 0.14)
    for f in range(f0 - 1, f0 + dur + 2):
        u = min(1.0, max(0.0, (f - f0) / dur)); e = (1 - 2 ** (-7 * u)) / (1 - 2 ** -7)
        sc_ = raio * (0.04 + 0.96 * e) if f >= f0 else 0.001
        o.scale = (sc_,) * 3; key(o, "scale", f, "BEZIER")
        a_ = min(1.0, (f - f0 + 1) / na); a_ = a_ * a_ * (3 - 2 * a_)
        cu.bevel_depth = 0.0 if f < f0 or u >= 1.0 else esp * a_ * (1 - u) ** 1.6 / sc_
        cu.keyframe_insert("bevel_depth", frame=f)
    if eco:
        onda(nome + "_eco", centro, f0 + 3, normal=normal, raio=raio * 0.7, dur=int(round(dur / 1.35 * 0.9)), esp=esp * 0.5, cor=cor, eco=False)
    return o
