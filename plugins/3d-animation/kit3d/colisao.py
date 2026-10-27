"""Detector de colisão entre objetos e personagens (pedido de 23/10/2026: "bugs dos props, parece que tá se colidindo").
Cada grupo = um objeto sem pai e tudo que está pendurado nele (um boneco, um cubo, uma viatura, uma mesa).
Quadro a quadro, mede a caixa 3D de cada grupo no mundo; se dois grupos sólidos entram um no outro (volume em comum)
e pelo menos um deles se mexe, confere peça com peça (o braço esticado de um boneco não conta como o boneco inteiro): se alguma
peça de um entra numa peça do outro, é colisão. Cenário grande (paredes, chão, fundo) e luz (halo, feixe, névoa) não contam.
blender -b -P colisao.py -- PROD CENA   (monta a cena sem renderizar e imprime COLISÃO a ... b)"""
import sys, os, importlib
from mathutils import Vector

FORA = ("halo", "feixe", "neblina", "vinheta", "sombra", "spot", "_gl", "poca", "chao", "parede", "fundo", "luz", "bokeh", "nevoa",
        "boil", "puff", "pend_", "cam", "fio_", "faixa_e", "tapete", "alarme", "fach_", "porta", "jan", "col", "persiana", "tit_", "ombro")
MAX_LADO = 6.0


def grupos(bpy):
    def malhas(o, acc):
        if o.type == "MESH":
            acc.append(o)
        for ch in o.children:
            malhas(ch, acc)
        return acc
    out = {}
    for o in bpy.data.objects:
        if o.parent is None and not any(x in o.name.lower() for x in FORA):
            ms = malhas(o, [])
            if ms:
                out[o.name] = ms
    return out


def caixa(ms):
    lo = [1e9] * 3; hi = [-1e9] * 3; ok = False
    for m in ms:
        if m.hide_render or any(x in m.name.lower() for x in FORA):
            continue
        mw = m.matrix_world
        if min(abs(v) for v in mw.to_scale()) < 1e-3:
            continue
        for c in m.bound_box:
            p = mw @ Vector(c)
            for i in range(3):
                lo[i] = min(lo[i], p[i]); hi[i] = max(hi[i], p[i])
        ok = True
    return (lo, hi) if ok else None


def comum(a, b, folga=0.02):
    v = 1.0
    for i in range(3):
        d = min(a[1][i], b[1][i]) - max(a[0][i], b[0][i]) - folga
        if d <= 0:
            return 0.0
        v *= d
    return v


def verifica(bpy, sc, f0, f1, passo=3, minimo=0.004):
    gs = grupos(bpy)
    hist, pecas = {}, {}
    for f in range(f0, f1 + 1, passo):
        sc.frame_set(f)
        cx = {n: caixa(ms) for n, ms in gs.items()}
        cx = {n: b for n, b in cx.items() if b and max(b[1][i] - b[0][i] for i in range(3)) < MAX_LADO
              and (b[1][2] - b[0][2]) > 0.03}
        hist[f] = cx
        pecas[f] = {n: [b for b in (caixa([m]) for m in gs[n]) if b] for n in cx}
    move = set()
    fs = sorted(hist)
    for n in gs:
        bs = [hist[f].get(n) for f in fs]
        bs = [b for b in bs if b]
        if len(bs) > 1 and any(abs(bs[0][k][i] - b[k][i]) > 0.01 for b in bs for k in (0, 1) for i in range(3)):
            move.add(n)
    achados = {}
    for f in fs:
        cx = hist[f]; ns = sorted(cx)
        for i, a in enumerate(ns):
            for b in ns[i + 1:]:
                if a not in move and b not in move:
                    continue
                v = comum(cx[a], cx[b])
                if v > minimo:                                                # as caixas dos grupos se cruzam: confere peça com peça
                    v = max((comum(pa, pb) for pa in pecas[f][a] for pb in pecas[f][b]), default=0.0)   # (braço esticado não vira "colisão")
                if v > minimo * 0.05:
                    k = (a, b)
                    achados.setdefault(k, []).append((f, v))
    # só o que muda: se já estavam encostados desde o primeiro quadro (objeto apoiado na mesa) e o volume não cresce, não é colisão
    out = []
    for (a, b), lst in achados.items():
        v0 = lst[0][1] if lst[0][0] == fs[0] else 0.0
        vmax = max(v for _, v in lst)
        if vmax > v0 * 1.5 + minimo:
            out.append((a, b, lst[0][0], lst[-1][0], vmax))
    return sorted(out, key=lambda q: -q[4])


if __name__ == "__main__":
    a = sys.argv[sys.argv.index("--") + 1:]
    prod, nome = a[0], a[1]
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import bpy, lib
    os.environ["SEM_VIDA"] = "1"
    sys.argv = [sys.argv[0], "--", "x", "x", "--list"]
    importlib.import_module(prod.replace(".py", ""))                   # o prod primeiro: ele acerta o VOZ_NOVA antes do prod_pcc4 carregar
    import prod_pcc4 as P4                                              # (ao contrário, o F ganhava a régua de tempo do PCC)
    t0, t1, fn = P4.CENAS[nome]
    lib.reset(108, 192, P4.FPS, 1); sc = lib.scene
    c = dict(sc=sc, f0=P4.F(t0), f1=P4.F(t1) - 1, t0=t0, t1=t1, F=P4.F)
    fn(c)
    for a_, b_, fa, fb, v in verifica(bpy, sc, c["f0"], c["f1"]):
        print(f"COLISÃO {nome}: {a_} x {b_}  quadros {fa}-{fb}  volume {v:.3f} m3")
    print("FIM", nome)
