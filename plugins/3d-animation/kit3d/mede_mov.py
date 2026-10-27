"""Medidor de movimento (pedido de 23/10/2026: "movimento muito travado, muito duro; a câmera sem as ondas in/out").
Monta a cena sem renderizar e mede, quadro a quadro, a velocidade de cada peça escolhida e da câmera ativa:
- PARADA: a peça estava andando, cai a menos de 15% da velocidade e volta a andar (pose a pose: anda, para, anda = robô);
- TRANCO: a velocidade muda de uma vez entre dois quadros (sem in/out);
- câmera: velocidade de deslocamento e de giro; no corte compara a velocidade de tela dos dois lados.
blender -b -P mede_mov.py -- PROD CENA [peca1,peca2,...]   (peça = parte do nome do objeto; padrão: punhos do herói)"""
import sys, os, importlib, math
from mathutils import Vector

BARRA = " ▁▂▃▄▅▆▇█"


def linha(vs):
    m = max(vs) or 1.0
    return "".join(BARRA[min(8, int(round(8 * v / m)))] for v in vs)


def paradas(vs, ini=0):
    """quedas a quase zero no meio de um movimento: anda (pico) -> para -> anda (pico)"""
    out = []
    for i in range(2, len(vs) - 2):
        if vs[i] <= min(vs[i - 1], vs[i + 1]):
            antes = max(vs[max(0, i - 12):i]); depois = max(vs[i + 1:i + 13])
            if min(antes, depois) > 0 and vs[i] < 0.15 * min(antes, depois) and min(antes, depois) > 0.2 * max(vs):
                out.append(ini + i)
    return out


def trancos(vs, ini=0, lim=0.35):
    """a velocidade pula mais de 'lim' do pico do trecho num quadro só"""
    m = max(vs) or 1.0
    return [ini + i for i in range(1, len(vs)) if abs(vs[i] - vs[i - 1]) > lim * m]


if __name__ == "__main__":
    a = sys.argv[sys.argv.index("--") + 1:]
    prod, nome = a[0], a[1]
    pecas = a[2].split(",") if len(a) > 2 else ["_wF", "_wB", "_cabeca"]
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
    f0, f1 = c["f0"], c["f1"]
    obs = {p: [o for o in bpy.data.objects if p in o.name] for p in pecas}
    pos = {p: [] for p in pecas}; cams = []
    marks = sorted([(m.frame, m.camera) for m in sc.timeline_markers if m.camera], key=lambda q: q[0])
    for f in range(f0, f1 + 1):
        sc.frame_set(f)
        for p, os_ in obs.items():
            if os_:
                pos[p].append(os_[0].matrix_world.translation.copy())
        cam = [cm for fr, cm in marks if fr <= f]
        cam = cam[-1] if cam else sc.camera
        mw = cam.matrix_world
        cams.append((cam.name, mw.translation.copy(), (mw.to_3x3() @ Vector((0, 0, -1))).normalized(), max(0.05, cam.data.dof.focus_distance)))
    for p in pecas:
        if not pos[p]:
            print(f"{p}: não achei"); continue
        vs = [0.0] + [(pos[p][i] - pos[p][i - 1]).length * 24 for i in range(1, len(pos[p]))]
        print(f"\n{p}  (m/s, pico {max(vs):.2f})\n  {linha(vs)}")
        print(f"  PARADAS no meio do gesto: {paradas(vs, f0) or 'nenhuma'}")
        print(f"  TRANCOS: {trancos(vs, f0) or 'nenhum'}")
    # câmera por plano
    print("\nCÂMERA (deslocamento m/s | giro graus/s)")
    i = 0
    while i < len(cams):
        j = i
        while j < len(cams) and cams[j][0] == cams[i][0]:
            j += 1
        tr = [0.0] + [(cams[k][1] - cams[k - 1][1]).length * 24 for k in range(i + 1, j)]
        gi = [0.0] + [math.degrees(cams[k][2].angle(cams[k - 1][2], 0.0)) * 24 for k in range(i + 1, j)]
        tela = [0.0] + [math.degrees((cams[k][1] - cams[k - 1][1]).length / cams[k][3]) * 24 + gi[k - i] for k in range(i + 1, j)]
        if os.environ.get("DBG"):
            print("   ", [tuple(round(v, 3) for v in cams[k][1]) for k in range(i, min(j, i + 4))])
        print(f"  {cams[i][0]:8s} {f0 + i:4d}-{f0 + j - 1:4d}  desl {linha(tr)}  giro {linha(gi)}  "
              f"entra {tr[1] if len(tr) > 1 else 0:.2f} m/s, sai {tr[-1]:.2f} m/s; TELA entra {tela[1] if len(tela) > 1 else 0:.0f} °/s, sai {tela[-1]:.0f} °/s; "
              f"trancos {trancos(tr, f0 + i) or '-'}")
        i = j
    print("FIM", nome)
