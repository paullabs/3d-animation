"""Cena do rei: trono simétrico no alto de um estrado, o herói sentado DE FRENTE, uma luz de cima e um halo atrás,
e a multidão de costas dos dois lados de um corredor (o tapete leva o olho até o trono).
Todas as cores vêm de uma paleta (PALETAS): fundo em tom médio (nunca preto), luz e borda numa cor só, um acento."""
import bpy, math, random
import lib
from lib import empty, key, srgb
import cena, sets, props, dinheiro as D
from char2d import rrect
from puppet2d import circle

PALETAS = {
    # azul-petróleo com luz coral (complementar do vermelho da jaqueta; a cabeça preta recorta no fundo médio)
    "petroleo": dict(top="#18303a", mid="#3d6872", low="#2a4f59", halo="#f4b597", luz="#ffdcc8", chao="#1f3a43", poca="#5d8a8e",
                     pedra="#2c4d56", aresta="#8db5b5", tapete="#7c1f2c", tapete_ar="#a8343f", trono="#1b2e35", friso="#f0c1a8",
                     almofada="#e8d4c2", povo_longe="#4a7680", povo_perto="#1a3038", borda="#ffd2bc", coluna="#244550", coluna_luz="#4f7f86",
                     neblina="#5f8f96", grade="#0f2026"),
    # ardósia azulada com luz rosada (fria e elegante; o vermelho do herói vira o ponto quente)
    "ardosia": dict(top="#2a3142", mid="#6b7690", low="#46506a", halo="#f2b8ae", luz="#ffe4dc", chao="#30374a", poca="#7e849c",
                    pedra="#3f475c", aresta="#b3b9cc", tapete="#6a2334", tapete_ar="#93374a", trono="#262b3a", friso="#ecc9c1",
                    almofada="#c9cedd", povo_longe="#68728c", povo_perto="#232a3a", borda="#ffd9d1", coluna="#3a4258", coluna_luz="#7a84a0",
                    neblina="#8a93ad", grade="#151a26"),
    # areia quente com azul-tinta (luz de fim de tarde; o tapete e o trono em azul fazem o contraste)
    "areia": dict(top="#4a3a30", mid="#b08c6c", low="#7c614c", halo="#fff0d8", luz="#fff6e8", chao="#5c4637", poca="#b8946f",
                  pedra="#6e5443", aresta="#e3c39f", tapete="#22406a", tapete_ar="#3a5f92", trono="#24304a", friso="#f5e3c6",
                  almofada="#2f5590", povo_longe="#9c7d62", povo_perto="#3a2c23", borda="#fff1dc", coluna="#6a5242", coluna_luz="#c9a882",
                  neblina="#c7a684", grade="#1e1814"),
    # vinho escuro com luz âmbar: o verde do dinheiro é o oposto do vinho e salta; listras do uniforme recortam no escuro
    "vinho": dict(top="#14070e", mid="#5a1834", low="#330c1e", halo="#ffae4a", luz="#ffd59a", chao="#1c0912", poca="#6e2a2c",
                  pedra="#4a1a30", aresta="#ff9fb4", tapete="#2c5f45", tapete_ar="#4c9a62", trono="#1a0a12", friso="#ffc46a",
                  almofada="#2f6b48", povo_longe="#6a2a44", povo_perto="#1e0a14", borda="#ffc77a", coluna="#260b19", coluna_luz="#8a3a58",
                  neblina="#7a2848", grade="#0d0408"),
    # índigo profundo com luz laranja: frio contra quente, o mais "cinema"
    "indigo": dict(top="#090b26", mid="#2a2f86", low="#171b55", halo="#ff8a3a", luz="#ffc488", chao="#0b0d2c", poca="#4b3f8f",
                   pedra="#2a2f78", aresta="#a8b0ff", tapete="#b5322f", tapete_ar="#e2534c", trono="#0d1033", friso="#ffb066",
                   almofada="#e8d4c2", povo_longe="#3c4294", povo_perto="#0f1238", borda="#ffb36e", coluna="#12154a", coluna_luz="#5058c4",
                   neblina="#3b40a8", grade="#05061a"),
    # petróleo bem escuro com laranja forte: a mesma família de antes, só que com contraste de verdade
    "petroleo_laranja": dict(top="#04161b", mid="#0e4651", low="#082b33", halo="#ff7b2e", luz="#ffb877", chao="#051114", poca="#2f5a5a",
                             pedra="#0f4a55", aresta="#7fe3e3", tapete="#b5322f", tapete_ar="#e2534c", trono="#06181d", friso="#ff9a50",
                             almofada="#e8d4c2", povo_longe="#1b5a64", povo_perto="#061418", borda="#ff9e5a", coluna="#072027", coluna_luz="#2f8a94",
                             neblina="#1b6a74", grade="#020a0c"),
}


def _mix(a, b, t):
    return props._mix(a, b, t)


def salao(p, frames, wall_y=7.0, halo_z=6.0):
    """parede em tom médio com degradê, halo atrás do trono, cone de luz, colunas simétricas e duas faixas de neblina"""
    sc = bpy.context.scene
    sc.world.node_tree.nodes["Background"].inputs[0].default_value = (*srgb(p["top"]), 1)
    props.skywall("salao_parede", wall_y, [(-2, p["low"]), (5, p["mid"]), (13, _mix(p["mid"], p["top"], 0.55)), (24, p["top"])], -80, 80, -10, 60)
    cena.disc("halo_trono", 7.0, cena.amat("halo_trono_m", p["halo"], 1.0, 0.55, ("radial", 1.5)), (0.0, wall_y - 0.1, halo_z))
    cena.poly_mesh("chao_salao", [(-80, -80, -0.004), (80, -80, -0.004), (80, wall_y, -0.004), (-80, wall_y, -0.004)], props.FM(p["chao"]))
    cena.ground_disc("poca_estrado", 10.0, 5.0, cena.amat("poca_estrado_m", p["poca"], 1.0, 0.8, ("radial", 1.3)), (0.0, -3.5, 0.003), n=72)
    for x in (-9.0, -5.6, 5.6, 9.0):                       # colunas simétricas, borda de luz do lado do trono
        sg = 1 if x < 0 else -1
        props.poly(f"coluna{x}", cena.rect(x - 0.6, -1, x + 0.6, 30), p["coluna"], wall_y - 0.3)
        xa = x + 0.6 * sg
        props.poly(f"coluna{x}_luz", cena.rect(min(xa, xa - 0.14 * sg), -1, max(xa, xa - 0.14 * sg), 30), p["coluna_luz"], wall_y - 0.31)
    import luz                                             # luz de palco: facho em camadas com poeira dentro
    luz.feixe("feixe_trono", 0.0, 0.8, 2.5, 26.0, 3.0, 0.45, p["luz"], forca=1.4, frames=frames, poeira=110, seed=2)
    for x, sg in ((-1.7, 1), (1.7, -1)):
        luz.feixe(f"feixe_lado{x}", x, 5.4, 1.5, 24.0, 1.4, 0.35, p["halo"], forca=0.8, rot=-sg * 20, poca=False, frames=frames, poeira=35, seed=7 + sg)
    for i, y in enumerate((-9.0, -18.0)):                  # neblina entre as fileiras: o fundo clareia, a profundidade aparece
        cena.poly_mesh(f"neblina{i}", [(-60, y, -1), (60, y, -1), (60, y, 12), (-60, y, 12)], cena.amat(f"neblina{i}_m", p["neblina"], 1.0, 0.1, ("band", 1.4, 0.0)))


def estrado(p, z_top=2.5, degraus=4, w_top=4.4, prof=3.0):
    """degraus de pedra vistos de frente, tapete no meio; o tapete continua no chão pelo corredor até a câmera"""
    h = z_top / degraus
    for k in range(degraus):
        w = w_top + (degraus - 1 - k) * 1.6
        y = -prof * (degraus - k) / degraus
        z1 = (k + 1) * h
        props.poly(f"degrau{k}", cena.rect(-w / 2, 0.0, w / 2, z1), p["pedra"], y)
        props.poly(f"degrau{k}_aresta", cena.rect(-w / 2, z1 - 0.05, w / 2, z1), p["aresta"], y - 0.002)
        props.poly(f"tapete{k}", cena.rect(-0.8, 0.0, 0.8, z1), p["tapete"], y - 0.004)
        props.poly(f"tapete{k}_aresta", cena.rect(-0.8, z1 - 0.05, 0.8, z1), p["tapete_ar"], y - 0.006)
    cena.poly_mesh("tapete_chao", [(-0.8, -60, 0.004), (0.8, -60, 0.004), (0.8, -prof, 0.004), (-0.8, -prof, 0.004)], props.FM(p["tapete"]))
    for x in (-0.8, 0.74):
        cena.poly_mesh(f"tapete_chao_b{x}", [(x, -60, 0.005), (x + 0.06, -60, 0.005), (x + 0.06, -prof, 0.005), (x, -prof, 0.005)], props.FM(p["tapete_ar"]))
    return z_top


def trono(p, name, loc, s=1.0):
    """trono simétrico de espaldar alto. Origem: chão do assento; assento a 0,64 (altura do quadril sentado de frente)."""
    root = empty(name, None, loc); root.scale = (s, s, s)
    props.inked(name + "_esp", rrect(-0.46, 0.0, 0.46, 2.55, 0.22, 8), p["trono"], root, loc=(0, 0.12, 0), w=0.022, rim=0.035, rim_color=p["friso"])
    props.poly(name + "_alm", rrect(-0.31, 0.74, 0.31, 2.3, 0.15, 8), _mix(p["almofada"], "#000000", 0.25), 0.115, root)
    props.poly(name + "_alm2", rrect(-0.26, 0.79, 0.26, 2.25, 0.12, 8), p["almofada"], 0.114, root)
    for x in (-0.46, 0.46):
        props.inked(f"{name}_bola{x}", circle(x, 2.6, 0.09, 24), p["friso"], root, loc=(0, 0.1, 0), w=0.02)
    props.inked(name + "_assento", rrect(-0.52, 0.0, 0.52, 0.64, 0.04, 4), p["trono"], root, loc=(0, 0.08, 0), w=0.02, rim=0.022, rim_color=p["friso"])
    for x in (-0.52, 0.52):
        props.inked(f"{name}_braco{x}", rrect(x - 0.07, 0.64, x + 0.07, 0.92, 0.03, 3), p["trono"], root, loc=(0, 0.07, 0), w=0.02)
        props.inked(f"{name}_braco{x}_t", rrect(x - 0.12, 0.9, x + 0.12, 0.98, 0.03, 3), p["friso"], root, loc=(0, 0.069, 0), w=0.018)
    return root


def multidao_costas(p, y0=-3.4, y1=-40.0, half_w=13.0, dx=0.5, dy=0.62, banda=5, corredor=1.15, seed=4):
    """pessoas de costas (ombros + cabeça) com borda de luz vinda do trono, dos dois lados do corredor do tapete.
    Mais perto do trono = mais claro. Devolve [(corpos, cabeças, y)] por faixa, do trono para a câmera."""
    rnd = random.Random(seed)
    th = [(0.12 * math.cos(2 * math.pi * i / 18), 0.12 * math.sin(2 * math.pi * i / 18)) for i in range(18)]
    corpo = [(-0.25, 0.0), (0.25, 0.0), (0.26, 0.3), (0.19, 0.44), (0.07, 0.48), (-0.07, 0.48), (-0.19, 0.44), (-0.26, 0.3)]
    linhas = int((y0 - y1) / dy)
    faixas = []
    for b0 in range(0, linhas, banda):
        u = (b0 + banda / 2) / linhas
        cor = _mix(p["povo_longe"], p["povo_perto"], u ** 0.7); rim = _mix(p["borda"], _mix(p["borda"], p["povo_perto"], 0.6), u ** 0.6)
        pc, ph = [], []
        for r in range(b0, min(linhas, b0 + banda)):
            y = y0 - r * dy
            n = int(2 * half_w / dx)
            for i in range(n):
                x = -half_w + (i + 0.5 + (0.5 if r % 2 else 0.0) + rnd.uniform(-0.15, 0.15)) * dx
                if abs(x) < corredor:
                    continue
                s = rnd.uniform(0.93, 1.07)
                z = 1.12 * s + rnd.uniform(-0.03, 0.03)
                pc.append((x, z, y)); ph.append((x, z + 0.6 * s, y))
        mc = [([(q[0], q[1] + 0.025) for q in corpo], rim), (corpo, cor)]
        mh = [([(q[0] * 1.08, q[1] + 0.03) for q in th], rim), (th, cor)]
        bc = D.malha(f"povo_c{b0}", mc, pc, dy=0.0015)
        bh = D.malha(f"povo_h{b0}", mh, ph, dy=0.0015)
        faixas.append((bc, bh, y0 - (b0 + banda / 2) * dy))
    return faixas


def reverencia(faixas, F, t0, passo=0.05, desce=0.11, dura=0.35, volta=0.5):
    """onda de reverência: as cabeças baixam (e os ombros um pouco), da frente do trono para trás"""
    for k, (bc, bh, y) in enumerate(faixas):
        t = t0 + k * passo
        for o, d in ((bh, desce), (bc, desce * 0.35)):
            z0 = o.location.z
            o.location.z = z0; key(o, "location", F(t), "BEZIER")
            o.location.z = z0 - d; key(o, "location", F(t + dura), "BEZIER")
            o.location.z = z0 - d; key(o, "location", F(t + dura + volta), "BEZIER")
            o.location.z = z0 - d * 0.6; key(o, "location", F(t + dura + volta + 0.4), "BEZIER")

# ---------------------------------------------------------------- o povo que se acende na contagem ("40 mil", um a um)
def _mat_contado(name, base, hi, flash, relogio):
    """emissão que troca de 'base' para 'hi' quando o tempo (relogio, em s) passa do atributo 'tcont' de cada pessoa;
    no instante da troca dá um clarão rápido ('flash') e assenta"""
    m = bpy.data.materials.new(name); m.use_nodes = True
    N = m.node_tree.nodes; L = m.node_tree.links; N.clear()
    out = N.new("ShaderNodeOutputMaterial"); em = N.new("ShaderNodeEmission")
    at = N.new("ShaderNodeAttribute"); at.attribute_type = "GEOMETRY"; at.attribute_name = "tcont"
    tv = N.new("ShaderNodeValue"); tv.name = "relogio"
    sub = N.new("ShaderNodeMath"); sub.operation = "SUBTRACT"; L.new(tv.outputs[0], sub.inputs[0]); L.new(at.outputs["Fac"], sub.inputs[1])
    on = N.new("ShaderNodeMapRange"); on.clamp = True; on.inputs[1].default_value = 0.0; on.inputs[2].default_value = 0.06
    L.new(sub.outputs[0], on.inputs[0])
    fl = N.new("ShaderNodeMapRange"); fl.clamp = True; fl.inputs[1].default_value = 0.04; fl.inputs[2].default_value = 0.26
    fl.inputs[3].default_value = 1.0; fl.inputs[4].default_value = 0.0; L.new(sub.outputs[0], fl.inputs[0])
    flm = N.new("ShaderNodeMath"); flm.operation = "MULTIPLY"; L.new(on.outputs[0], flm.inputs[0]); L.new(fl.outputs[0], flm.inputs[1])
    c1 = N.new("ShaderNodeMix"); c1.data_type = "RGBA"; c1.inputs[6].default_value = (*srgb(base), 1); c1.inputs[7].default_value = (*srgb(hi), 1)
    L.new(on.outputs[0], c1.inputs[0])
    c2 = N.new("ShaderNodeMix"); c2.data_type = "RGBA"; c2.inputs[7].default_value = (*srgb(flash), 1)
    L.new(c1.outputs[2], c2.inputs[6]); L.new(flm.outputs[0], c2.inputs[0])
    L.new(c2.outputs[2], em.inputs[0]); L.new(em.outputs[0], out.inputs[0])
    for f, t in relogio:
        tv.outputs[0].default_value = t; tv.outputs[0].keyframe_insert("default_value", frame=f)
    lib.all_interp(m.node_tree, "LINEAR")
    return m


def _malha_contada(name, camadas, pos, tcs, dy=0.0015):
    """camadas = [(polígono, material)] de trás para a frente; pos = [(x, z, y)]; tcs = hora da contagem de cada pessoa"""
    import numpy as np
    verts, faces, mats, tco = [], [], [], []
    n = 0
    for (x, z, y), tc in zip(pos, tcs):
        for li, (pts, _) in enumerate(camadas):
            for px, pz in pts:
                verts.append((x + px, y - li * dy, z + pz)); tco.append(tc)
            faces.append(tuple(range(n, n + len(pts)))); mats.append(li); n += len(pts)
    me = bpy.data.meshes.new(name); me.from_pydata(verts, [], faces)
    for _, m in camadas:
        me.materials.append(m)
    me.polygons.foreach_set("material_index", np.array(mats, dtype=np.int32))
    at = me.attributes.new("tcont", "FLOAT", "POINT"); at.data.foreach_set("value", np.array(tco, dtype=np.float32))
    me.update()
    o = bpy.data.objects.new(name, me); bpy.context.scene.collection.objects.link(o)
    return o


def multidao_contada(p, F, t0=1.30, dur=0.9, hi="#ecd09c", hi_rim="#fff3dc", flash="#ffffff", y0=-3.4, y1=-40.0, half_w=13.0,
                     dx=0.5, dy=0.62, banda=5, corredor=1.15, seed=4):
    """o povo de costas (como multidao_costas), mas cada pessoa se acende quando o contador '40.000' passa por ela:
    a contagem começa junto ao trono e se espalha para trás, no mesmo ritmo do número (1 - (1-u)^3)."""
    rnd = random.Random(seed)
    th = [(0.12 * math.cos(2 * math.pi * i / 18), 0.12 * math.sin(2 * math.pi * i / 18)) for i in range(18)]
    corpo = [(-0.25, 0.0), (0.25, 0.0), (0.26, 0.3), (0.19, 0.44), (0.07, 0.48), (-0.07, 0.48), (-0.19, 0.44), (-0.26, 0.3)]
    linhas = int((y0 - y1) / dy)
    gente = []
    for r in range(linhas):
        y = y0 - r * dy
        for i in range(int(2 * half_w / dx)):
            x = -half_w + (i + 0.5 + (0.5 if r % 2 else 0.0) + rnd.uniform(-0.15, 0.15)) * dx
            if abs(x) < corredor:
                continue
            s = rnd.uniform(0.93, 1.07)
            gente.append(dict(r=r, x=x, y=y, z=1.12 * s + rnd.uniform(-0.03, 0.03), s=s,
                              ordem=(y0 - y) * 1.0 + abs(x) * 0.7 + rnd.uniform(0, 5.0)))
    gente.sort(key=lambda g: g["ordem"])
    N = len(gente)
    for k, g in enumerate(gente):
        q = (k + 0.5) / N
        g["tc"] = t0 + dur * (1 - (1 - q) ** (1 / 3))
    relogio = [(F(-5.0), -5.0), (F(20.0), 20.0)]
    faixas = []
    for b0 in range(0, linhas, banda):
        u = (b0 + banda / 2) / linhas
        cor = _mix(p["povo_longe"], p["povo_perto"], u ** 0.7); rim = _mix(p["borda"], _mix(p["borda"], p["povo_perto"], 0.6), u ** 0.6)
        hi_c = _mix(hi, cor, 0.38 + u * 0.4); hi_r = _mix(hi_rim, hi, u * 0.5)            # acende e assenta num tom mais calmo
        m_rim = _mat_contado(f"povo_rim{b0}", rim, hi_r, flash, relogio)
        m_cor = _mat_contado(f"povo_cor{b0}", cor, hi_c, flash, relogio)
        gs = [g for g in gente if b0 <= g["r"] < b0 + banda]
        cam_c = [([(q_[0], q_[1] + 0.025) for q_ in corpo], m_rim), (corpo, m_cor)]
        cam_h = [([(q_[0] * 1.08, q_[1] + 0.03) for q_ in th], m_rim), (th, m_cor)]
        bc = _malha_contada(f"povo_c{b0}", cam_c, [(g["x"], g["z"], g["y"]) for g in gs], [g["tc"] for g in gs])
        bh = _malha_contada(f"povo_h{b0}", cam_h, [(g["x"], g["z"] + 0.6 * g["s"], g["y"]) for g in gs], [g["tc"] for g in gs])
        faixas.append((bc, bh, y0 - (b0 + banda / 2) * dy))
    return faixas
