"""Animação suave do protagonista: movimento primário + movimento secundário por molas.

Primário (exato): posição do corpo, altura do quadril e pernas (cinemática inversa, pé cravado).
Secundário (molas com amortecimento): tronco, peito, cabeça, ombros, cotovelos, punhos, capuz e cordões.
Cada parte persegue o seu alvo com atraso, inércia e um leve "passar do ponto", e reage à aceleração do
corpo (arrasto, quebra sucessiva, follow-through). Assim nada é puxado em bloco.
Rosto: trocas de expressão com antecipação, passagem do ponto e assentamento (bounce suave).

Uso: tl = Timeline(heroi, 1, quadro_final); tl.stand(...); tl.walk(...); tl.intent(...); tl.face(...); tl.bake()"""
import math, json, random
from lib import key
from heroi import Heroi, VIEW
from motion import leg_ik, smoothstep, ANK, HIP_STAND

UPPER = ("torso", "chest", "head", "shF", "elF", "wrF", "shB", "elB", "wrB", "hood", "str0", "str1", "shupF", "shupB")
REST = dict(torso=0.0, chest=0.0, head=0.0, shF=4.0, elF=10.0, wrF=0.0, shB=-4.0, elB=10.0, wrB=0.0, hood=0.0, str0=0.0, str1=0.0,
            shupF=0.0, shupB=0.0)
# frequência (Hz) e amortecimento de cada parte: menor frequência = mais pesado/atrasado; menor amortecimento = mais balanço
SPRING = dict(torso=(1.7, 0.7), chest=(2.2, 0.6), head=(2.4, 0.55), shF=(2.0, 0.52), shB=(2.0, 0.52),
              elF=(2.8, 0.55), elB=(2.8, 0.55), wrF=(3.4, 0.5), wrB=(3.4, 0.5), hood=(2.2, 0.42),
              str0=(2.8, 0.32), str1=(2.9, 0.32), chestz=(3.4, 0.6), shupF=(3.0, 0.6), shupB=(3.0, 0.6))


def smoother(u):
    u = max(0.0, min(1.0, u)); return u * u * u * (u * (u * 6 - 15) + 10)


def spring(target, fps, f, zeta, x0=None, sub=6):
    w = 2 * math.pi * f; k = w * w; c = 2 * zeta * w; dt = 1.0 / fps / sub
    x = target[0] if x0 is None else x0; v = 0.0; out = []
    for T in target:
        for _ in range(sub):
            v += (k * (T - x) - c * v) * dt
            x += v * dt
        out.append(x)
    return out


def deriv(arr, fps):
    n = len(arr); out = [0.0] * n
    for i in range(n):
        a = arr[max(0, i - 1)]; b = arr[min(n - 1, i + 1)]
        out[i] = (b - a) * fps / (2 if 0 < i < n - 1 else 1)
    return out


def gauss(arr, sigma):
    if sigma <= 0:
        return list(arr)
    r = int(3 * sigma); w = [math.exp(-0.5 * (i / sigma) ** 2) for i in range(-r, r + 1)]
    n = len(arr); out = []
    for i in range(n):
        acc = ws = 0.0
        for j, wj in zip(range(i - r, i + r + 1), w):
            acc += arr[min(n - 1, max(0, j))] * wj; ws += wj
        out.append(acc / ws)
    return out


def shift(arr, d):
    n = len(arr); return [arr[min(n - 1, max(0, i - d))] for i in range(n)]


def blur(arr, r=2):
    n = len(arr); out = []
    for i in range(n):
        lo, hi = max(0, i - r), min(n, i + r + 1)
        out.append(sum(arr[lo:hi]) / (hi - lo))
    return out


class Timeline:
    def __init__(self, h, f0, f1, fps=24):
        self.h = h; self.fps = fps; self.f0 = f0; self.f1 = f1
        self.n = f1 - f0 + 1
        self.prim = {c: [None] * self.n for c in ("x", "hipz", "hipF", "knF", "anF", "hipB", "knB", "anB", "yaw")}
        self.keys = {c: [] for c in UPPER}
        self.add = {c: [0.0] * self.n for c in UPPER}
        self.faces = []
        self.walkw = [0.0] * self.n            # 1 enquanto anda (regras de caminhada só valem aí)
        self.post = {c: [0.0] * self.n for c in UPPER}     # somado DEPOIS das molas (tremores rápidos)
        self.extra_looks = []                               # olhares dirigidos (paranoia, procurar algo)
        self.rnd = random.Random(7)

    def i(self, f):
        return max(0, min(self.n - 1, f - self.f0))

    # ---------------------------------------------------------------- primário
    def stand(self, fa, fb, x):
        for f in range(fa, fb + 1):
            k = self.i(f)
            self.prim["x"][k] = x; self.prim["hipz"][k] = HIP_STAND; self.prim["yaw"][k] = 0.0
            for c in ("hipF", "knF", "anF", "hipB", "knB", "anB"):
                self.prim[c][k] = 0.0

    def walk(self, fs, steps, x0, face=1, step=12, stride=0.40, lift=0.065, swing=14.0, lean=3.5, lead="F",
             bob=0.013, yaw=0.008, seed=11):
        """Caminhada pelo método do contato (Richard Williams), 12 quadros por passo = 2 passos/s.
        Contato (pernas retas) -> descida em T/4 (o peso cai na perna da frente, que dobra) -> passagem em T/2 ->
        subida em 3T/4 (empurrão) -> contato. Quadril gira (a raiz da perna da frente avança no contato), braços
        balançam 1/3 para frente e 2/3 para trás com o extremo na descida, pé sai devagar e pousa rápido,
        cada passo levemente diferente do outro (sem gêmeos). Termina com o corpo passando do ponto e assentando."""
        V = VIEW[self.h.view]; T = step; S = stride; N = max(2, steps)
        hipoff = {"F": V["hipF"], "B": V["hipB"]}
        rnd = random.Random(seed)
        amp = [1.0 + 0.06 * (1 if i % 2 else -1) + rnd.uniform(-0.05, 0.05) for i in range(N + 2)]   # assimetria por passo
        A = 0.004 * S / 0.42
        def base_x(tau):
            k = tau / T
            if k <= 1:
                return x0 + (S / 2) * k * k
            if k <= N - 1:
                u = k - int(k)
                return x0 + S / 2 + S * (k - 1) + A * (math.sin(2 * math.pi * (u - 0.55)) - math.sin(-2 * math.pi * 0.55))
            u = min(1.0, k - (N - 1))
            return x0 + S / 2 + S * (N - 2) + (S / 2) * (1 - (1 - u) ** 2)
        def base_z(tau):
            k = tau / T; i = int(min(k, N - 1e-6)); u = k - i
            z = 0.822 + bob * amp[i] * math.cos(2 * math.pi * (u - 0.75))        # baixo em T/4, alto em 3T/4
            if i == 0:
                return HIP_STAND + (z - HIP_STAND) * smoother(u)
            if i == N - 1:
                return z + (HIP_STAND - z) * smoother(u)
            return z
        plant = {"F": x0 + hipoff["F"], "B": x0 + hipoff["B"]}
        events = {"F": [], "B": []}; other = {"F": "B", "B": "F"}; sw = lead; landing = []
        for i in range(N):
            a = i * T + (0.0 if i == 0 else 0.2 * T); b = (i + 1) * T
            tgt = base_x(b) + hipoff[sw] + (0.0 if i == N - 1 else S / 2)
            events[sw].append((a, b, plant[sw], tgt)); plant[sw] = tgt; landing.append((b, sw)); sw = other[sw]
        def yaw_at(tau):
            """+1 = raiz da perna F à frente; extremo em cada contato, cruza o zero na passagem"""
            pts = [(0.0, 0.0)] + [(b, (1.0 if s_ == "F" else -1.0) * (0.0 if j == N - 1 else 1.0)) for j, (b, s_) in enumerate(landing)]
            for (ta, ya), (tb, yb) in zip(pts, pts[1:]):
                if tau <= tb:
                    q = (tau - ta) / max(1e-6, tb - ta); return ya + (yb - ya) * (0.5 - 0.5 * math.cos(math.pi * q))
            return 0.0
        def foot(side, tau):
            evs = events[side]; x = x0 + hipoff[side]; landed = None; nxt = None
            for e in evs:
                a, b, xa, xb = e
                if tau < a:
                    nxt = e; break
                if tau <= b:
                    s_ = (tau - a) / (b - a)
                    se = 0.5 * smoother(s_) + 0.5 * s_ * s_                      # sai devagar, pousa rápido
                    z = ANK + lift * math.sin(math.pi * s_ ** 0.85) ** 0.9 + 0.03 * (1 - s_) ** 3
                    ang = -38 * (1 - s_) ** 2 + 18 * smoothstep((s_ - 0.6) / 0.4) - 5 * math.sin(math.pi * s_)
                    return xa + (xb - xa) * se, z, ang
                x = xb; landed = b
            z, ang = ANK, 0.0
            if landed is not None and tau - landed < 0.25 * T:                    # calcanhar pousa, pé assenta até a descida
                ang = 18 * (1 - smoothstep((tau - landed) / (0.25 * T)))
            if nxt is not None and nxt[0] > 0 and nxt[0] - tau < 0.3 * T:          # o pé de trás sai do chão o mais tarde possível
                q = smoothstep(1 - (nxt[0] - tau) / (0.3 * T)); z = ANK + 0.036 * q; ang = -38 * q
            return x, z, ang
        total = N * T
        for d_ in range(1, 9):                        # antecipação: o peso vai para trás e desce antes do 1º passo
            kk_ = self.i(fs - d_); w_ = math.sin(math.pi * (8 - d_) / 8) if d_ > 1 else 0.0
            if self.prim["x"][kk_] is not None:
                self.prim["x"][kk_] = x0 - 0.012 * face * w_
                self.prim["hipz"][kk_] = HIP_STAND - 0.008 * w_
        def legs(k, bx, bz, yv, feet):
            th = {}
            for side in "FB":
                ax, az, fang = feet[side]
                hx = bx + hipoff[side] + (yv if side == "F" else -yv)
                dx, dz = ax - hx, az - bz
                t_, kn, shin_abs = leg_ik(dx, dz)
                self.prim["hip" + side][k] = t_; self.prim["kn" + side][k] = kn; self.prim["an" + side][k] = fang - shin_abs
                th[side] = math.degrees(math.atan2(dx, -dz))
            return th
        for tf in range(total + 1):
            tau = float(tf); f = fs + tf; k = self.i(f)
            bx = base_x(tau); bz = base_z(tau)
            kk = tau / T; i = int(min(kk, N - 1e-6)); u = kk - i
            ramp = smoothstep(min(1.0, kk * 1.1)) * (1 - smoothstep(kk - (N - 1)) if kk > N - 1 else 1.0)
            yv = yaw * yaw_at(tau) * ramp
            self.prim["x"][k] = x0 + (bx - x0) * face; self.prim["hipz"][k] = bz; self.prim["yaw"][k] = yv
            self.walkw[k] = ramp
            th = legs(k, bx, bz, yv, {s_: foot(s_, tau) for s_ in "FB"})
            ga = amp[i] * swing / 14.0
            # braço oposto à perna: 1/3 para frente, 2/3 para trás (alvo; o atraso até a descida vem do baking)
            self.add["shF"][k] += (-ga * th["F"] - 6.0) * ramp
            self.add["shB"][k] += (-ga * th["B"] - 6.0) * ramp
            self.add["torso"][k] += lean * ramp
            self.add["chest"][k] += 0.8 * ramp
        # parada: o corpo passa do ponto para frente e assenta; pés cravados
        endb = base_x(total); fin = {s_: (plant[s_], ANK, 0.0) for s_ in "FB"}
        for t in range(1, 13):
            k = self.i(fs + total + t); w = math.exp(-t / 4.5) * math.sin(math.pi * t / 7.0)
            bx = endb + 0.02 * w; bz = HIP_STAND - 0.01 * max(0.0, math.sin(math.pi * t / 10.0)) * (1 - t / 12)
            self.prim["x"][k] = x0 + (bx - x0) * face; self.prim["hipz"][k] = bz; self.prim["yaw"][k] = 0.0
            legs(k, bx, bz, 0.0, fin)
        end_x = x0 + (endb - x0) * face
        return fs + total + 12, end_x

    # ---------------------------------------------------------------- intenções (poses-alvo) e rosto
    def intent(self, f, **vals):
        for c, v in vals.items():
            self.keys[c].append((f, v))

    def bump(self, ch, f, amount, width=4):
        """empurrão suave num canal (ex.: cabeça acena ao mudar a expressão)"""
        for d in range(-width, width + 1):
            k = self.i(f + d)
            self.add[ch][k] += amount * (0.5 + 0.5 * math.cos(math.pi * d / (width + 1)))

    def face(self, f, strength=1.0, **expr):
        self.faces.append((f, strength, expr))

    def _curve(self, c):
        ks = sorted(self.keys[c]); out = []
        for k in range(self.n):
            f = self.f0 + k
            if not ks:
                out.append(REST[c]); continue
            if f <= ks[0][0]:
                out.append(ks[0][1]); continue
            if f >= ks[-1][0]:
                out.append(ks[-1][1]); continue
            for (fa, va), (fb, vb) in zip(ks, ks[1:]):
                if fa <= f <= fb:
                    u = (f - fa) / max(1, fb - fa)
                    out.append(va + (vb - va) * smoother(u)); break
        return out

    # ---------------------------------------------------------------- assar
    def bake(self, breathe=True, dump=None):
        n, fps = self.n, self.fps
        for c, arr in self.prim.items():
            last = None
            for k in range(n):
                if arr[k] is None:
                    arr[k] = last if last is not None else (HIP_STAND if c == "hipz" else 0.0)
                last = arr[k]
        X, Z = self.prim["x"], self.prim["hipz"]
        face_sign = 1.0
        vx = deriv(X, fps); ax = blur(deriv(blur(vx, 1), fps), 2)
        vz = deriv(Z, fps); az = blur(deriv(blur(vz, 1), fps), 2)
        axf = [a * face_sign for a in ax]
        res = {}
        t = [k / fps for k in range(n)]
        def breath_curve():
            rb = random.Random(5); out = []; ph = 0.0; per = rb.uniform(3.5, 5.0)
            for _ in range(n):
                p = ph % 1.0
                out.append(-math.cos(math.pi * p / 0.6) if p < 0.6 else math.cos(math.pi * (p - 0.6) / 0.4))
                ph += 1.0 / (per * fps)
                if ph % 1.0 < 1.0 / (per * fps):
                    per = rb.uniform(3.5, 5.0)
            return gauss(out, 1.5)
        br = breath_curve() if breathe else [0.0] * n
        br2 = shift(br, 6)
        def target(c, extra):
            cur = self._curve(c)
            return [cur[k] + self.add[c][k] + extra[k] for k in range(n)]
        def run(c, extra):
            fz = SPRING[c]
            res[c] = spring(target(c, extra), fps, fz[0], fz[1])
            return res[c]
        for f, st, _ in self.faces:                      # a cabeça reage depois do olhar e da sobrancelha
            self.bump("head", f + 2, 1.2 * st, 3)
        # (a) trajetória própria do peito: sem os surtos do quadril, sobe e desce menos e um pouco depois
        LT = 0.45                                         # quadril -> ombros
        Xs = gauss(X, 6.0)
        Zm = gauss(Z, 10.0)
        Zs = gauss([Zm[k] + 0.85 * (v - Zm[k]) for k, v in enumerate(shift(Z, 2))], 1.2)
        dx = [Xs[k] - X[k] for k in range(n)]
        cz_t = [max(-0.015, min(0.015, Zs[k] - Z[k])) for k in range(n)]
        lean_t = target("torso", [math.degrees(math.asin(max(-0.3, min(0.3, dx[k] / LT)))) * face_sign + 0.25 * br[k] for k in range(n)])
        res["torso"] = T_ = spring(lean_t, fps, 2.6, 0.85)
        cz = gauss(cz_t, 0.8)                             # a coluna absorve exatamente a diferença
        # (b) parte de cima da coluna faz o contrário da de baixo (contrapeso), atrasada
        base_lean = gauss(self.add["torso"], 3.0)
        chest_t = target("chest", [-0.35 * (T_[k] - base_lean[k]) + 0.5 * br[k] for k in range(n)])
        res["chest"] = C_ = spring(shift(chest_t, 1), fps, 2.2, 0.7)
        # (c) cabeça estabilizada: compensa a inclinação do corpo e só acena de leve, sempre atrasada
        azs = shift(gauss(az, 2.0), 3)
        head_t = target("head", [-0.95 * (T_[k] + C_[k]) + 0.25 * azs[k] + 0.5 * br2[k] for k in range(n)])
        nz = gauss([self.rnd.uniform(-1, 1) for _ in range(n)], 9.0); nz = [v * 2.2 for v in nz]
        res["head"] = spring([head_t[k] + 0.9 * nz[k] for k in range(n)], fps, 2.2, 0.78)
        # (d) braços pendurados: o balanço vem das pernas, atrasado, e descontando a inclinação do corpo
        for s_ in "FB":
            sw_ = shift(self.add["sh" + s_], 1)                 # extremo do braço ~3 quadros após o contato (na descida)
            cur = self._curve("sh" + s_)
            sh_t = [cur[k] + sw_[k] + 0.75 * (T_[k] + C_[k]) - 3.0 * axf[k] + 0.8 * br2[k] for k in range(n)]
            sh = res["sh" + s_] = spring(sh_t, fps, 3.6, 0.62)
            dsh = deriv(sh, fps)
            ww = gauss(self.walkw, 3.0)
            fwd = [max(0.0, v - (T_[k] + C_[k])) * ww[k] for k, v in enumerate(sh)]
            # cotovelo: 25-35° indo para frente, 5-10° atrás; "quebra" na troca de direção (o segredo de Williams)
            el = run("el" + s_, [0.06 * shift(dsh, 1)[k] + min(30.0, 2.2 * shift(fwd, 1)[k]) + 3.0 for k in range(n)])
            el = res["el" + s_] = [max(4.0, min(150.0, v)) for v in el]        # cotovelo nunca dobra ao contrário nem fica 100% reto (o braço arredondado se perde)
            de = deriv(el, fps)
            run("wr" + s_, [-0.03 * shift(de, 1)[k] for k in range(n)])
        run("shupF", [0.0] * n); run("shupB", [0.0] * n)
        for c in res:
            if c in self.post:
                res[c] = [v + self.post[c][k] for k, v in enumerate(res[c])]
        run("hood", [-3.2 * axf[k] - 1.6 * az[k] for k in range(n)])
        run("str0", [-5.0 * axf[k] + 1.0 * az[k] for k in range(n)])
        run("str1", [-4.6 * axf[k] + 0.9 * az[k] for k in range(n)])
        Y = self.prim["yaw"]
        CY = spring(shift([-1.3 * v for v in Y], 2), fps, 3.0, 0.7)            # ombros contra o quadril, 2 quadros depois
        V = VIEW[self.h.view]
        # gravar
        h = self.h; J = h.j
        for k in range(n):
            f = self.f0 + k
            r = h.root; r.location.x = X[k]; r.keyframe_insert("location", frame=f)
            J["hips"].location.z = Z[k]; J["hips"].keyframe_insert("location", frame=f)
            J["chest"].location.z = 0.2 + cz[k]; J["chest"].keyframe_insert("location", frame=f)
            bw = h.prop.get("body_w", 1.0)
            side_view = h.view in ("q", "side")
            if side_view:
                J["hipF"].location.x = V["hipF"] + Y[k]; J["hipF"].keyframe_insert("location", frame=f)
                J["hipB"].location.x = V["hipB"] - Y[k]; J["hipB"].keyframe_insert("location", frame=f)
            for s_, sgn in (("F", 1), ("B", -1)):
                J["sh" + s_].location.x = V["sh" + s_][0] * bw + (sgn * CY[k] if side_view else 0.0)
                J["sh" + s_].location.z = V["sh" + s_][1] + res["shup" + s_][k]
                J["sh" + s_].keyframe_insert("location", frame=f)
            hf, hb = Heroi.hem_from_legs(self.prim["hipF"][k], self.prim["hipB"][k])
            if "hemF" in J:
                for jn, v in (("hemF", hf), ("hemB", hb)):
                    J[jn].rotation_euler = (0, -math.radians(v), 0); J[jn].keyframe_insert("rotation_euler", frame=f)
            for c in ("hipF", "knF", "anF", "hipB", "knB", "anB"):
                jn = {"hipF": "hipF", "knF": "knF", "anF": "anF", "hipB": "hipB", "knB": "knB", "anB": "anB"}[c]
                J[jn].rotation_euler = (0, -math.radians(self.prim[c][k]), 0); J[jn].keyframe_insert("rotation_euler", frame=f)
            for c in UPPER:
                if c not in J:
                    continue
                v = res[c][k] * (0.7 if c == "head" else 1.0)
                sg = 1 if c in ("torso", "chest", "head", "hood") else -1          # + = para frente nos dois casos
                J[c].rotation_euler = (0, sg * math.radians(v), 0); J[c].keyframe_insert("rotation_euler", frame=f)
            J["neck"].rotation_euler = (0, math.radians(res["head"][k] * 0.3), 0); J["neck"].keyframe_insert("rotation_euler", frame=f)
        self._bake_faces()
        if self.extra_looks and hasattr(h, "eyegrp"):
            prev = (0.0, 0.0)
            for f, lk in sorted(self.extra_looks):          # olho pula em 2 quadros e segura
                h.eyegrp.location = (prev[0] * 0.016, 0, prev[1] * 0.016); h.eyegrp.keyframe_insert("location", frame=f)
                h.eyegrp.location = (lk[0] * 0.016, 0, lk[1] * 0.016); h.eyegrp.keyframe_insert("location", frame=f + 2)
                prev = lk
            self._look_at = sorted(getattr(self, "_look_at", []) + list(self.extra_looks))
        if dump:
            json.dump({"hipz": Z, "x": X, **{c: res[c] for c in res}, "ax": ax, "az": az, "chestz": cz,
                       "legF": self.prim["hipF"], "legB": self.prim["hipB"]}, open(dump, "w"))
        return res

    @staticmethod
    def _stage(t, start, rise=3, settle=4, over=0.12):
        """peso de uma parte do rosto t quadros após a troca: começa em 'start', passa do ponto e assenta"""
        if t <= start:
            return 0.0
        if t <= start + rise:
            u = (t - start) / rise; return (1 + over) * (u * u * (3 - 2 * u))
        if t <= start + rise + settle:
            u = (t - start - rise) / settle; return 1 + over * (1 - u * u * (3 - 2 * u))
        return 1.0

    @staticmethod
    def _mix(prev, new, wb, wl, wm, wlook, blink):
        """mistura duas expressões com pesos separados: sobrancelhas (wb), olhos (wl), boca (wm), olhar (wlook)"""
        P = dict(new)
        lerp = lambda a, b, w: a + (b - a) * w
        for c in ("brow", "browup", "browtilt"):
            P[c] = lerp(prev.get(c, 0.0), new.get(c, 0.0), wb)
        P["brows"] = new.get("brows", True) if wb >= 0.5 else prev.get("brows", True)
        def swap(name_k, val_k, w):
            pn, nn = prev.get(name_k), new.get(name_k)
            pv, nv = prev.get(val_k, 1.0), new.get(val_k, 1.0)
            if pn == nn:
                return nn, lerp(pv, nv, w)
            if pn is None:
                return nn, nv * w
            if nn is None:
                return pn, pv * max(0.0, 1 - w)
            return (pn, pv * (1 - 2 * w)) if w < 0.5 else (nn, nv * (2 * w - 1))
        P["lid"], P["lidv"] = swap("lid", "lidv", min(wl, 1.2))
        P["mouth"], P["mouthv"] = swap("mouth", "mouthv", min(wm, 1.2))
        P["wide"] = lerp(prev.get("wide", 0.0), new.get("wide", 0.0), wl)
        P["eye"] = new.get("eye", "normal") if wl >= 0.5 else prev.get("eye", "normal")
        pl, nl = prev.get("look", (0.0, 0.0)), new.get("look", (0.0, 0.0))
        P["look"] = (lerp(pl[0], nl[0], wlook), lerp(pl[1], nl[1], wlook))
        P["blink"] = blink
        P["extras"] = new.get("extras", ()) if wl >= 0.5 else prev.get("extras", ())
        return P

    def _bake_faces(self):
        """troca de expressão como animadores profissionais: o olhar dispara primeiro (2 quadros antes),
        sobrancelha começa no quadro 0, pálpebras +1, boca +2; cada parte passa ~12% do ponto e assenta;
        na troca de pensamento há uma piscada (fecha 2, segura 1, abre 3) que esconde a troca do olho"""
        h = self.h; prev = dict(Heroi.NEUTRAL); self._look_at = []
        for f, st, expr in sorted(self.faces, key=lambda e: e[0]):
            new = dict(Heroi.NEUTRAL); new.update(expr)
            if f <= self.f0 + 2 or st <= 0.0:
                h._pose_face(f, new, "BEZIER"); prev = new; self._look_at.append((f, new.get("look", (0.0, 0.0)))); continue
            changed_eye = new.get("eye") != prev.get("eye") or new.get("lid") != prev.get("lid")
            do_blink = st >= 0.6 and changed_eye
            for t in range(-3, 12):
                wb = self._stage(t, 0, 3, 4, 0.12 * st)
                wl = self._stage(t, 1, 3, 4, 0.12 * st)
                wm = self._stage(t, 2, 3, 4, 0.12 * st)
                wlook = self._stage(t, -3, 2, 1, 0.0)
                bl = 1.0
                if do_blink:
                    bl = {-1: 1.0, 0: 0.5, 1: 0.08, 2: 0.08, 3: 0.45, 4: 0.85, 5: 1.06, 6: 1.02}.get(t, 1.0)
                h._pose_face(f + t, self._mix(prev, new, wb, wl, wm, wlook, bl), "BEZIER")
            # balanço: a cabeça inteira comprime e estica de leve na troca (quique), proporcional à intensidade
            sq = 0.045 * st
            for t, (sx, sz) in ((-1, (1, 1)), (1, (1 + sq, 1 - sq)), (3, (1 - 0.7 * sq, 1 + 0.7 * sq)), (5, (1 + 0.25 * sq, 1 - 0.25 * sq)), (8, (1, 1))):
                h.face.scale = (sx, 1, sz); h.face.keyframe_insert("scale", frame=f + t)
            for kn, g in h.extras.items():
                show = kn in new.get("extras", ())
                g.scale = (0.0001,) * 3 if not (kn in prev.get("extras", ())) else (1, 1, 1); g.keyframe_insert("scale", frame=f + 1)
                g.scale = (1.18,) * 3 if show else (0.0001,) * 3; g.keyframe_insert("scale", frame=f + 3)
                g.scale = (1, 1, 1) if show else (0.0001,) * 3; g.keyframe_insert("scale", frame=f + 7)
            self._look_at.append((f - 1, new.get("look", (0.0, 0.0))))
            prev = new

    def darts(self, every=(2.0, 3.4), size=0.22, seed=9):
        """pausa viva com o olhar: olhos pulam rápido (2 quadros), seguram, voltam; nunca durante trocas de expressão"""
        h = self.h; rnd = random.Random(seed); fps = self.fps
        busy = [f for f, _, _ in self.faces] + [f for f, _ in self.extra_looks]
        looks = sorted(getattr(self, "_look_at", []))
        def base(f):
            v = (0.0, 0.0)
            for ff, lk in looks:
                if ff <= f:
                    v = lk
            return v
        f = self.f0 + int(rnd.uniform(*every) * fps)
        while f < self.f1 - 40:
            if all(abs(f - b) > 14 and abs(f + 30 - b) > 14 for b in busy):
                b0 = base(f); d = (rnd.uniform(-1, 1) * size, rnd.uniform(-0.6, 0.6) * size)
                for ff, lk in ((f, b0), (f + 2, (b0[0] + d[0], b0[1] + d[1])), (f + 26, (b0[0] + d[0], b0[1] + d[1])), (f + 28, b0)):
                    h.eyegrp.location = (lk[0] * 0.016, 0, lk[1] * 0.016); h.eyegrp.keyframe_insert("location", frame=ff)
            f += int(rnd.uniform(*every) * fps)

    def blinks(self, every=(3.0, 5.0), seed=4):
        h = self.h; rnd = random.Random(seed); fps = self.fps
        busy = [f for f, _, _ in self.faces]
        f = self.f0 + int(rnd.uniform(*every) * fps)
        while f < self.f1 - 6:
            if all(abs(f - b) > 8 for b in busy):
                for ej in h.eyes.values():
                    for ff, v in ((f - 1, 1.0), (f + 1, 0.08), (f + 2, 0.08), (f + 5, 1.0)):
                        ej.scale = (1, 1, v); ej.keyframe_insert("scale", frame=ff)
            f += int(rnd.uniform(*every) * fps)
