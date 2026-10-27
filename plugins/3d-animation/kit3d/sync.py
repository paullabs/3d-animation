"""mede o atraso do braço em relação à perna oposta durante a caminhada (quadros) e a amplitude do quadril"""
import json, sys
d = json.load(open("/tmp/anim_curves.json"))
a, b = int(sys.argv[1]), int(sys.argv[2])
def xc(u, v, lag):
    s = 0.0
    for k in range(a, b):
        s += u[k] * v[k - lag]
    return s
for arm, leg in (("shF", "legB"), ("shB", "legF")):
    u = d[arm]; v = d[leg]
    mu = sum(u[a:b]) / (b - a); mv = sum(v[a:b]) / (b - a)
    uu = [x - mu for x in u]; vv = [x - mv for x in v]
    best = max(range(-2, 12), key=lambda L: xc(uu, vv, L))
    print(f"{arm} segue {leg} com atraso de {best} quadros ({best / 24 * 1000:.0f} ms)")
z = d["hipz"][a:b]; print("quadril sobe e desce %.1f cm" % ((max(z) - min(z)) * 100))
