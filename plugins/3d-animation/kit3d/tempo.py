"""Leva os tempos de uma narração antiga para uma nova (mesmas falas, outra voz/outro texto).
As âncoras são o começo de cada fala e as palavras iguais dentro da mesma fala; entre elas, interpolação linear.
Assim as cenas escritas em segundos da voz antiga caem no mesmo ponto da fala nova."""
import json, bisect, difflib
from palavras import norm


def mapa(voz_velha, voz_nova):
    tv = json.load(open(voz_velha + "/tempos.json")); tn = json.load(open(voz_nova + "/tempos.json"))
    pv = json.load(open(voz_velha + "/palavras.json")); pn = json.load(open(voz_nova + "/palavras.json"))
    anc = [(0.0, 0.0)]
    for fv, fn in zip(tv["falas"], tn["falas"]):
        anc.append((fv["inicio"], fn["inicio"]))
        a = [w for w in pv if w["frase"] == fv["n"]]; b = [w for w in pn if w["frase"] == fn["n"]]
        sm = difflib.SequenceMatcher(a=[norm(w["txt"]) for w in a], b=[norm(w["txt"]) for w in b], autojunk=False)
        for blk in sm.get_matching_blocks():
            for k in range(blk.size):
                anc.append((a[blk.a + k]["t0"], b[blk.b + k]["t0"]))
    anc.append((tv["total"], tn["total"]))
    anc.sort()
    lim = []                                               # só âncoras que andam para a frente nos dois tempos
    for x, y in anc:
        if not lim or (x > lim[-1][0] + 1e-3 and y > lim[-1][1] + 1e-3):
            lim.append((x, y))
    xs = [x for x, _ in lim]; ys = [y for _, y in lim]

    def w(t):
        if t <= xs[0]:
            return ys[0] + (t - xs[0])
        if t >= xs[-1]:
            return ys[-1] + (t - xs[-1])
        i = bisect.bisect_right(xs, t) - 1
        u = (t - xs[i]) / (xs[i + 1] - xs[i])
        return ys[i] + u * (ys[i + 1] - ys[i])
    return w
