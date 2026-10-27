"""Movimento do protagonista com conceitos clássicos de animação.
- Caminhada pelo método do contato (contato, descida, passagem, subida), 2 passos/s a 24 qps.
- Pernas por cinemática inversa: o pé de apoio fica cravado no chão (não escorrega, não "anda de ré").
- Braço oposto à perna do mesmo lado, antebraço atrasado (follow-through), cabeça com defasagem.
- Começo com meio passo acelerando e fim com meio passo freando + assentamento (ease in/out).
- Gestos com antecipação, passagem do ponto e assentamento; pausas que nunca congelam.
Regra de ângulo: positivo = para onde ele olha. Feito para as vistas q (3/4) e side (perfil)."""
import math, random
from lib import key
from heroi import Heroi, VIEW

L1, L2 = 0.41, 0.38          # coxa, canela
ANK = 0.07                   # altura do tornozelo com o pé no chão
HIP_STAND = 0.86
BODY = ("torso", "chest", "head", "neck", "shF", "elF", "wrF", "shB", "elB", "wrB",
        "hipF", "knF", "anF", "hipB", "knB", "anB")


def smoothstep(u):
    u = max(0.0, min(1.0, u)); return u * u * (3 - 2 * u)


def set_body(h, f, d, interp="LINEAR"):
    """grava os ângulos do corpo (graus) e posições num quadro"""
    J = h.j; r = h.root
    if "x" in d:
        r.location.x = d["x"]; key(r, "location", f, interp)
    if "hipz" in d:
        J["hips"].location.z = d["hipz"]; key(J["hips"], "location", f, interp)
    for n in BODY:
        if n in d:
            J[n].rotation_euler = (0, -math.radians(d[n]), 0); key(J[n], "rotation_euler", f, interp)


def leg_ik(dx, dz):
    """dx: tornozelo à frente do quadril; dz: altura relativa (negativa). Joelho dobra para frente.
    Retorna (coxa, joelho relativo, canela absoluta) em graus."""
    d = math.hypot(dx, dz)
    d = max(abs(L1 - L2) + 1e-4, min(d, L1 + L2 - 1e-4))
    alpha = math.degrees(math.atan2(dx, -dz))
    beta = math.degrees(math.acos((L1 * L1 + d * d - L2 * L2) / (2 * L1 * d)))
    gamma = math.degrees(math.acos((L2 * L2 + d * d - L1 * L1) / (2 * L2 * d)))
    thigh = alpha + beta
    shin_abs = alpha - gamma
    return thigh, shin_abs - thigh, shin_abs


def _hip_curve(u):
    """altura do quadril dentro de um passo (u 0..1): contato .815, descida .797, passagem .83, subida .842"""
    pts = [(0.0, 0.815), (0.17, 0.797), (0.5, 0.83), (0.75, 0.842), (1.0, 0.815)]
    for (u0, z0), (u1, z1) in zip(pts, pts[1:]):
        if u <= u1:
            k = (u - u0) / (u1 - u0)
            return z0 + (z1 - z0) * (0.5 - 0.5 * math.cos(math.pi * k))
    return pts[-1][1]


def walk(h, f0, steps, x0, face=1, step=12, stride=0.42, lift=0.085, arm=25.0, lean=5.0, lead="F", extra=None):
    """anda 'steps' passos a partir do quadro f0 e da posição x0 (de pé). Retorna (quadro_final, x_final).
    1º passo = meio passo acelerando; último = meio passo freando com os pés juntos."""
    V = VIEW[h.view]; T = step; S = stride
    hipoff = {"F": V["hipF"], "B": V["hipB"]}
    N = max(2, steps)
    # posição do corpo (quadril) ao longo do tempo, com aceleração e frenagem
    def body_x(tau):
        k = tau / T
        if k <= 1:
            return x0 + (S / 2) * k * k
        if k <= N - 1:
            return x0 + S / 2 + S * (k - 1)
        u = min(1.0, k - (N - 1))
        return x0 + S / 2 + S * (N - 2) + (S / 2) * (1 - (1 - u) ** 2)
    def body_z(tau):
        k = tau / T; i = int(min(k, N - 1e-6)); u = k - i
        z = _hip_curve(u)
        if i == 0:
            return HIP_STAND + (z - HIP_STAND) * smoothstep(u * 1.4)
        if i == N - 1:
            return z + (HIP_STAND - z) * smoothstep(u)
        return z
    # plano de pisadas (posição do tornozelo de cada pé, no eixo "para frente")
    plant = {"F": x0 + hipoff["F"], "B": x0 + hipoff["B"]}
    events = {"F": [], "B": []}      # (inicio_balanço, fim_balanço, de, para)
    other = {"F": "B", "B": "F"}
    sw = lead
    for i in range(N):
        t_start = i * T + (0.0 if i == 0 else 0.2 * T)
        t_end = (i + 1) * T
        bx_end = body_x(t_end)
        if i == N - 1:
            target = bx_end + hipoff[sw]             # para do lado do outro pé
        else:
            target = bx_end + S / 2 + hipoff[sw]
        events[sw].append((t_start, t_end, plant[sw], target))
        plant[sw] = target
        sw = other[sw]
    final_plant = dict(plant)
    def foot(side, tau):
        """(x do tornozelo, z do tornozelo, ângulo absoluto do pé: + bico para cima)"""
        evs = events[side]
        x = x0 + hipoff[side]; landed = None; nxt = None
        for e in evs:
            a, b, xa, xb = e
            if tau < a:
                nxt = e; break
            if tau <= b:                                   # balançando
                s_ = (tau - a) / (b - a); se = smoothstep(s_)
                xs = xa + (xb - xa) * se
                z = ANK + lift * math.sin(math.pi * s_) ** 0.9 + 0.03 * (1 - s_) ** 3
                ang = -22 * (1 - s_) ** 2 + 18 * smoothstep((s_ - 0.55) / 0.45) - 8 * math.sin(math.pi * s_)
                return xs, z, ang
            x = xb; landed = b
        z, ang = ANK, 0.0
        if landed is not None and tau - landed < 0.2 * T:          # calcanhar pousa e o pé assenta
            ang = 18 * (1 - smoothstep((tau - landed) / (0.2 * T)))
        if nxt is not None and nxt[0] > 0 and nxt[0] - tau < 0.25 * T:   # impulso: calcanhar sobe
            k = 1 - (nxt[0] - tau) / (0.25 * T)
            z = ANK + 0.03 * k; ang = -22 * k
        return x, z, ang
    total = N * T
    rows = []
    for tf in range(0, total + 1):
        tau = float(tf)
        bx = body_x(tau); bz = body_z(tau)
        d = {"x": x0 + (bx - x0) * face, "hipz": bz}
        thighs = {}
        for side in "FB":
            ax, az, fang = foot(side, tau)
            hx = bx + hipoff[side]
            th, kn, shin_abs = leg_ik(ax - hx, az - bz)
            d["hip" + side] = th; d["kn" + side] = kn; d["an" + side] = fang - shin_abs
            thighs[side] = th
        k = tau / T; i = int(min(k, N - 1e-6)); u = k - i
        ramp = smoothstep(min(1.0, k * 1.2)) * (1 - smoothstep((k - (N - 1)) * 1.0) if k > N - 1 else 1.0)
        d["torso"] = lean * ramp + 1.2 * math.sin(2 * math.pi * u) * ramp
        d["chest"] = 1.5 * ramp
        rows.append((tf, d, thighs, ramp))
    # braços opostos às pernas, com atraso (follow-through) e cabeça com defasagem
    lag = 2
    for idx, (tf, d, thighs, ramp) in enumerate(rows):
        j = max(0, idx - lag)
        thF, thB = rows[j][2]["F"], rows[j][2]["B"]
        aF = -arm / 22.0 * thF * 0.9 * ramp; aB = -arm / 22.0 * thB * 0.9 * ramp
        d["shF"] = aF; d["shB"] = aB
        jj = max(0, idx - lag - 1)
        aF2 = -arm / 22.0 * rows[jj][2]["F"] * 0.9 * rows[jj][3]; aB2 = -arm / 22.0 * rows[jj][2]["B"] * 0.9 * rows[jj][3]
        d["elF"] = 10 + 0.55 * max(0.0, aF2) + 4 * ramp; d["elB"] = 10 + 0.55 * max(0.0, aB2) + 4 * ramp
        d["wrF"] = 4; d["wrB"] = 4
        prev = rows[max(0, idx - 3)][1]
        d["head"] = -0.6 * prev.get("torso", 0.0) + 1.0 * ramp
        d["neck"] = d["head"] * 0.3
        if extra:
            d.update(extra)
        set_body(h, f0 + tf, d, "LINEAR")
    return f0 + total, x0 + (body_x(total) - x0) * face


def settle(h, f, x, frames=10, face=1, rest=None):
    """assentar depois de parar: quadril afunda um pouco e volta, braços passam do ponto e voltam"""
    base = rest_pose(x)
    if rest:
        base.update(rest)
    dip = dict(base, hipz=HIP_STAND - 0.018, shF=-6, shB=5, elF=16, elB=14, torso=2.5, head=-1.5)
    over = dict(base, hipz=HIP_STAND + 0.004, shF=3, shB=-3, elF=6, elB=6, torso=-0.6, head=0.8)
    set_body(h, f + int(frames * 0.35), dip, "BEZIER")
    set_body(h, f + int(frames * 0.7), over, "BEZIER")
    set_body(h, f + frames, base, "BEZIER")
    return f + frames


def rest_pose(x):
    return dict(x=x, hipz=HIP_STAND, torso=0.0, chest=0.0, head=0.0, neck=0.0, shF=4, elF=8, wrF=0, shB=-4, elB=8, wrB=0,
                hipF=0, knF=0, anF=0, hipB=0, knB=0, anB=0)


def gesture(h, f, frames, frm, to, antic=0.18, over=0.1):
    """movimento com antecipação (vai um pouco para trás), passa do ponto e assenta"""
    keys = set(frm) | set(to)
    def mix(a, b, k):
        out = {}
        for n in keys:
            va, vb = frm.get(n, to.get(n)), to.get(n, frm.get(n))
            out[n] = va + (vb - va) * k if isinstance(va, (int, float)) else (vb if k >= 0.5 else va)
        return out
    set_body(h, f, mix(frm, to, 0.0), "BEZIER")
    set_body(h, f + int(frames * 0.3), mix(frm, to, -antic), "BEZIER")
    set_body(h, f + int(frames * 0.75), mix(frm, to, 1 + over), "BEZIER")
    set_body(h, f + frames, mix(frm, to, 1.0), "BEZIER")
    return f + frames


def hold(h, f0, f1, base, seed=3, amp=1.0):
    """pausa viva: pequenas oscilações a cada ~14 quadros (nunca congela)"""
    rnd = random.Random(seed); f = f0
    while f <= f1:
        d = dict(base)
        for n, a in (("head", 1.6), ("chest", 0.9), ("shF", 1.8), ("shB", 1.4), ("elF", 2.0), ("torso", 0.6)):
            d[n] = base.get(n, 0.0) + rnd.uniform(-a, a) * amp
        set_body(h, f, d, "BEZIER")
        f += 14
    set_body(h, f1, base, "BEZIER")


def face(h, f, **expr):
    """troca a expressão no quadro f (o corpo não é tocado)"""
    P = dict(Heroi.NEUTRAL); P.update(expr)
    h._pose_face(f, P, "BEZIER")
    for kn, g in h.extras.items():
        g.scale = (1, 1, 1) if kn in P["extras"] else (0.0001,) * 3
        key(g, "scale", f, "CONSTANT")
