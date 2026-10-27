"""Atuação corporal do protagonista: um repertório de ações prontas, todas com as regras do guia
(TECNICAS-ANIMACAO.md): antecipação (3-6 quadros, 10-20% para o lado contrário), ação (4-8 quadros),
passar do ponto e assentar (as molas do bake fazem isso), quebra sucessiva (ombro -> cotovelo -> punho),
nada termina no mesmo quadro, e a pose nunca congela (pausa viva).

Uso:
    tl = Timeline(heroi, 1, fim); tl.stand(1, fim, x)
    a = Actor(tl, x)
    f = a.point(30); a.release(f + 30)
    ...
    tl.bake()
Cada ação devolve o quadro em que a pose principal "chegou"; release() volta ao descanso.
O rosto continua com tl.face(...): o pensamento (olhar/sobrancelha) deve vir ~4 quadros antes do corpo."""
import math, random
from anim import REST, smoother
from heroi import VIEW
from motion import leg_ik, ANK, HIP_STAND

ARMS = ("shF", "elF", "wrF", "shB", "elB", "wrB")
BODY = ("torso", "chest", "head", "shupF", "shupB")


def ease(u, kind):
    u = max(0.0, min(1.0, u))
    if kind == "in":
        return u * u
    if kind == "out":
        return 1 - (1 - u) * (1 - u)
    if kind == "lin":
        return u
    return smoother(u)


class Actor:
    def __init__(self, tl, x=0.0):
        self.tl = tl; self.x = x
        V = VIEW[tl.h.view]
        self.hipoff = {"F": V["hipF"], "B": V["hipB"]}
        self.feet = {"F": x + self.hipoff["F"], "B": x + self.hipoff["B"]}
        self.rnd = random.Random(21)

    # ---------------------------------------------------------------- utilidades
    def cur(self, c, f):
        """valor do canal no quadro f segundo as intenções já marcadas"""
        ks = sorted(self.tl.keys[c])
        if not ks:
            return REST[c]
        if f <= ks[0][0]:
            return ks[0][1]
        if f >= ks[-1][0]:
            return ks[-1][1]
        for (fa, va), (fb, vb) in zip(ks, ks[1:]):
            if fa <= f <= fb:
                return va + (vb - va) * smoother((f - fa) / max(1, fb - fa))
        return ks[-1][1]

    def hold_from(self, f, chans):
        """fixa o valor atual dos canais no quadro f (a ação começa daqui, não antes)"""
        for c in chans:
            self.tl.intent(f, **{c: self.cur(c, f)})

    def keys(self, f0, plan):
        """plan = [(dt, {canal: valor}), ...] relativo a f0"""
        for dt, vals in plan:
            self.tl.intent(f0 + dt, **vals)

    def release(self, f, frames=14, chans=ARMS + BODY):
        """volta ao descanso devagar (saída lenta, nada para de uma vez)"""
        self.hold_from(f, chans)
        for i, c in enumerate(chans):
            self.tl.intent(f + frames + (i % 3), **{c: REST[c]})
        return f + frames + 2

    def tremble(self, f0, f1, amp=1.2, chans=("head", "shF", "shB", "torso")):
        """tremor rápido (somado depois das molas), alterna a cada 2 quadros"""
        tl = self.tl
        for f in range(f0, f1):
            k = tl.i(f); env = math.sin(math.pi * (f - f0) / max(1, f1 - f0))
            for j, c in enumerate(chans):
                s = 1 if ((f // 2) + j) % 2 else -1
                tl.post[c][k] += s * amp * env * (0.6 + 0.4 * self.rnd.random())

    def osc(self, f0, cycles, period, chan, amp, base=None):
        """oscilação (acenar, esfregar as mãos, bater o dedo)"""
        base = self.cur(chan, f0) if base is None else base
        for i in range(cycles * 2 + 1):
            v = base + (amp if i % 2 else -amp) * (0.0 if i == 0 else 1.0)
            self.tl.intent(f0 + i * period // 2, **{chan: v})
        self.tl.intent(f0 + cycles * period + 2, **{chan: base})
        return f0 + cycles * period + 2

    # ---------------------------------------------------------------- corpo (quadril e pernas, com pé cravado)
    def body(self, f0, plan, move_to=None):
        """plan = [(dt, dict(dx, dz, fF=(dx,dz,ang), fB=(dx,dz,ang), e="io"|"in"|"out"|"lin")), ...]
        dx/dz: deslocamento do quadril; fF/fB: deslocamento dos pés (pulo). move_to: nova posição de apoio no fim"""
        tl = self.tl
        plan = [(0, dict(dx=0.0, dz=0.0, fF=(0.0, 0.0, 0.0), fB=(0.0, 0.0, 0.0)))] + plan
        x0 = self.x; feet0 = dict(self.feet)
        def get(d, k, default):
            return d.get(k, default)
        for (ta, a), (tb, b) in zip(plan, plan[1:]):
            kind = b.get("e", "io")
            for t in range(ta, tb + 1):
                u = ease((t - ta) / max(1, tb - ta), kind)
                dx = get(a, "dx", 0.0) + (get(b, "dx", 0.0) - get(a, "dx", 0.0)) * u
                dz = get(a, "dz", 0.0) + (get(b, "dz", 0.0) - get(a, "dz", 0.0)) * u
                k = tl.i(f0 + t)
                bx = x0 + dx; bz = HIP_STAND + dz
                tl.prim["x"][k] = bx; tl.prim["hipz"][k] = bz; tl.prim["yaw"][k] = 0.0
                for s in "FB":
                    fa, fb_ = get(a, "f" + s, (0.0, 0.0, 0.0)), get(b, "f" + s, (0.0, 0.0, 0.0))
                    fdx = fa[0] + (fb_[0] - fa[0]) * u; fdz = fa[1] + (fb_[1] - fa[1]) * u; fang = fa[2] + (fb_[2] - fa[2]) * u
                    ax = feet0[s] + fdx; az = ANK + fdz
                    th, kn, shin_abs = leg_ik(ax - (bx + self.hipoff[s]), az - bz)
                    tl.prim["hip" + s][k] = th; tl.prim["kn" + s][k] = kn; tl.prim["an" + s][k] = fang - shin_abs
        end = plan[-1][1]
        if move_to is not None:
            self.x = move_to
            self.feet = {s: feet0[s] + end.get("f" + s, (0.0, 0.0, 0.0))[0] for s in "FB"}
        last = f0 + plan[-1][0]
        # depois do plano, o corpo fica parado na última pose (até outra ação)
        bx = x0 + end.get("dx", 0.0); bz = HIP_STAND + end.get("dz", 0.0)
        for f in range(last + 1, tl.f1 + 1):
            k = tl.i(f)
            tl.prim["x"][k] = bx; tl.prim["hipz"][k] = bz; tl.prim["yaw"][k] = 0.0
            for s in "FB":
                fe = end.get("f" + s, (0.0, 0.0, 0.0))
                th, kn, shin_abs = leg_ik(self.feet[s] - (bx + self.hipoff[s]) if move_to is not None else feet0[s] + fe[0] - (bx + self.hipoff[s]),
                                          ANK + fe[1] - bz)
                tl.prim["hip" + s][k] = th; tl.prim["kn" + s][k] = kn; tl.prim["an" + s][k] = fe[2] - shin_abs
        return last

    # ---------------------------------------------------------------- ações
    def point(self, f, up=0.0):
        """apontar: recua (antecipação), o ombro lidera, o cotovelo vem dobrado e estica por último"""
        self.hold_from(f, ("shF", "elF", "wrF", "torso", "head", "shB"))
        a = self.cur("shF", f)
        self.keys(f, [(5, dict(shF=a - 18, elF=36, torso=-3, head=-2)),
                      (10, dict(elF=46)),
                      (12, dict(shF=95 + up, torso=3, head=2, shB=-10)),
                      (16, dict(elF=6, wrF=-8)),
                      (22, dict(torso=1.5, head=0.5))])
        return f + 16

    def shrug(self, f, hold=18):
        """dar de ombros: ombros descem um pouco, sobem rápido, palmas para cima, cabeça tomba; segura e solta"""
        self.hold_from(f, ARMS + ("shupF", "shupB", "head"))
        self.keys(f, [(4, dict(shupF=-0.008, shupB=-0.008)),
                      (10, dict(shupF=0.035, shupB=0.032, shF=18, elF=100, wrF=-25, shB=14, elB=96, wrB=-25)),
                      (12, dict(head=8)),
                      (10 + hold, dict(shupF=0.03, shupB=0.028, head=7))])
        return f + 12

    def think(self, f, taps=2):
        """mão no queixo: sobe devagar, o outro braço apoia o cotovelo; batidinhas do dedo"""
        self.hold_from(f, ARMS + ("head", "torso"))
        self.keys(f, [(5, dict(shF=self.cur("shF", f) - 6)),
                      (16, dict(shF=70, elF=138, wrF=15, shB=28, elB=88, torso=-2)),
                      (18, dict(head=-7))])
        if taps:
            self.osc(f + 28, taps, 10, "wrF", 6)
        return f + 18

    def facepalm(self, f):
        """mão na cara: a cabeça sobe um pouco (antecipação) e cai na mão"""
        self.hold_from(f, ("shF", "elF", "wrF", "head", "torso"))
        self.keys(f, [(4, dict(head=-5, shF=self.cur("shF", f) - 8)),
                      (10, dict(shF=82, elF=150, wrF=12)),
                      (12, dict(head=14)),
                      (14, dict(torso=8))])
        return f + 14

    def cross_arms(self, f):
        """braços cruzados, corpo para trás (postura de poder)"""
        self.hold_from(f, ARMS + ("torso", "head", "shupF", "shupB"))
        self.keys(f, [(4, dict(shupF=0.01, shupB=0.01)),
                      (10, dict(shF=8, elF=96, wrF=6, shB=4, elB=92, wrB=6, shupF=0.0, shupB=0.0)),
                      (12, dict(torso=-3, head=-5))])
        return f + 12

    def celebrate(self, f):
        """comemorar com pulo: agacha (antecipação), salta com os braços para cima, pousa amortecendo"""
        self.hold_from(f, ARMS + ("torso", "head"))
        self.keys(f, [(6, dict(shF=-25, shB=-25, elF=30, elB=30, torso=8, head=4)),
                      (11, dict(shF=165, shB=160, elF=10, elB=12, torso=-4, head=-6)),
                      (26, dict(torso=0, head=-2))])
        self.body(f, [(6, dict(dz=-0.06, e="out")),
                      (10, dict(dz=0.08, fF=(0.0, 0.12, -20), fB=(0.0, 0.12, -20), e="out")),
                      (14, dict(dz=0.09, fF=(0.0, 0.14, -15), fB=(0.0, 0.14, -15), e="io")),
                      (18, dict(dz=-0.01, fF=(0.0, 0.0, 0.0), fB=(0.0, 0.0, 0.0), e="in")),
                      (20, dict(dz=-0.05, e="out")),
                      (28, dict(dz=0.0, e="io"))])
        return f + 18

    def take(self, f, back=-0.14):
        """susto (take): encolhe e aperta os olhos (devagar), depois ESTOURA para trás em 3 quadros, segura e treme"""
        self.hold_from(f, ARMS + ("torso", "head", "shupF", "shupB"))
        self.keys(f, [(5, dict(torso=5, head=6, shF=self.cur("shF", f) + 5, shB=self.cur("shB", f) + 5, shupF=-0.01, shupB=-0.01)),
                      (8, dict(torso=-14, head=-8, shF=60, elF=115, shB=50, elB=115, shupF=0.03, shupB=0.03)),
                      (20, dict(torso=-8, head=-4))])
        self.body(f, [(5, dict(dz=-0.03, e="io")),
                      (8, dict(dx=back * 0.6, dz=0.05, fF=(back, 0.06, -10), fB=(back, 0.07, -10), e="out")),
                      (12, dict(dx=back, dz=-0.04, fF=(back, 0.0, 0.0), fB=(back, 0.0, 0.0), e="in")),
                      (20, dict(dx=back, dz=-0.01, fF=(back, 0.0, 0.0), fB=(back, 0.0, 0.0), e="io"))],
                  move_to=self.x + back)
        self.tremble(f + 12, f + 34, amp=1.4)
        return f + 12

    def slump(self, f, frames=18):
        """desânimo: tudo cai devagar (tronco, cabeça, ombros), joelhos cedem um pouco"""
        self.hold_from(f, ("torso", "chest", "head", "shupF", "shupB") + ARMS)
        self.keys(f, [(frames, dict(torso=14, chest=8, head=20, shupF=-0.015, shupB=-0.015, shF=-6, shB=-8, elF=6, elB=6))])
        self.body(f, [(frames, dict(dz=-0.025, e="io"))])
        return f + frames

    def angry(self, f, hold=20):
        """raiva: recua (antecipação), avança com ombros erguidos e braços tensos, treme"""
        self.hold_from(f, ARMS + ("torso", "head", "shupF", "shupB"))
        self.keys(f, [(4, dict(torso=-3, head=-3)),
                      (10, dict(torso=10, head=8, shupF=0.02, shupB=0.02, shF=-12, elF=32, shB=-14, elB=30))])
        self.tremble(f + 10, f + 10 + hold, amp=1.0, chans=("shF", "shB", "head"))
        return f + 10

    def look_around(self, f, beats=((0, (-0.9, 0.0)), (14, (0.9, 0.05)), (28, (-0.8, 0.2)), (42, (0.0, 0.0)))):
        """paranoia: os olhos pulam de um lado para o outro, a cabeça e o tronco acompanham atrasados"""
        tl = self.tl
        self.hold_from(f, ("head", "torso", "shupF", "shupB"))
        for dt, lk in beats:
            tl.intent(f + dt + 3, head=-4 * lk[0] + 2, torso=1.5 * lk[0])
            tl.intent(f + dt + 3, shupF=0.012, shupB=0.012)
        tl.extra_looks += [(f + dt, lk) for dt, lk in beats]
        return f + beats[-1][0] + 6

    def rub_hands(self, f, cycles=4):
        """ganância: mãos se encontram na frente do peito e se esfregam"""
        self.hold_from(f, ARMS + ("shupF", "shupB", "head"))
        self.keys(f, [(8, dict(shF=28, elF=82, shB=34, elB=78, shupF=0.012, shupB=0.012)), (10, dict(head=-4))])
        self.osc(f + 10, cycles, 6, "elF", 7)
        self.osc(f + 11, cycles, 6, "elB", -7)
        return f + 10 + cycles * 6

    def wave(self, f, cycles=3):
        """acenar: braço sobe, o antebraço balança (o punho atrasa)"""
        self.hold_from(f, ("shF", "elF", "wrF"))
        self.keys(f, [(4, dict(shF=self.cur("shF", f) - 8)), (10, dict(shF=150, elF=35))])
        self.osc(f + 12, cycles, 8, "elF", 14, base=35)
        self.osc(f + 13, cycles, 8, "wrF", -10, base=0)
        return f + 12 + cycles * 8

    def sit(self, f, depth=0.36, back=-0.16):
        """sentar: inclina para frente, o quadril vai para trás e desce, o tronco volta quando pousa; quica de leve"""
        self.hold_from(f, ARMS + ("torso", "head"))
        self.keys(f, [(5, dict(torso=6)), (10, dict(torso=25, head=-6, shF=20, elF=20, shB=15, elB=20)),
                      (18, dict(torso=4, head=0, shF=32, elF=42, shB=26, elB=40))])
        self.body(f, [(5, dict(dz=-0.01)), (16, dict(dx=back, dz=-depth - 0.012, e="io")), (22, dict(dx=back, dz=-depth, e="io"))])
        self.seated = (back, depth)
        return f + 22

    def straighten(self, f, frames=12):
        """volta o corpo à postura neutra (depois de desânimo, raiva etc.)"""
        self.hold_from(f, ("torso", "chest", "head", "shupF", "shupB"))
        self.keys(f, [(frames, dict(torso=0.0, chest=0.0, head=0.0, shupF=0.0, shupB=0.0))])
        self.body(f, [(frames, dict(dz=0.0, e="io"))])
        return f + frames

    def stand_up(self, f):
        """levantar: inclina para frente (o peso vai para os pés), o quadril sobe e avança, o tronco endireita por último"""
        back, depth = getattr(self, "seated", (-0.16, 0.36))
        self.hold_from(f, ARMS + ("torso", "head"))
        self.keys(f, [(6, dict(torso=28, head=-4)), (16, dict(torso=6)), (22, dict(torso=0, head=0)),
                      (14, dict(shF=REST["shF"], elF=REST["elF"], shB=REST["shB"], elB=REST["elB"]))])
        self.body(f, [(0, dict(dx=back, dz=-depth)), (6, dict(dx=back + 0.02, dz=-depth)), (16, dict(dx=0.0, dz=0.01, e="io")),
                      (22, dict(dx=0.0, dz=0.0))])
        return f + 22
