"""Cenários com profundidade (estilo 2D chapado com parallax real), em duas atmosferas:
- manha(): luz dourada da manhã (sol baixo, raios, feixes de luz, névoa quente, poeira no ar)
- drama(): noite dramática (céu frio, néon vermelho, poste de sódio com cone de luz, chuva, vapor, chão molhado)
Camadas do fundo para a frente: céu (fundo do mundo) -> sol/lua -> horizonte -> cidade -> prédios -> árvores
-> casas -> postes/cerca -> calçada (personagem) -> primeiro plano desfocado. Névoa por distância separa as camadas.
A câmera deve só deslizar/avançar (nunca girar)."""
import bpy, bmesh, math, random
import lib
from lib import srgb, link, empty, key, _fcs
import sets
from sets import fogmat
from puppet2d import circle, smooth
from char2d import rrect, mesh_pts

PAL = {
    "manha": dict(sky_top="#6f9bd0", sky_mid="#b9cbe0", horizon="#ffd6a4", haze="#f4cba6", sun="#fff4da", sun_glow="#ffc382",
                  far="#e7b9a4", city="#d3a091", bld="#b57b78", bld_lit="#eeb090", bld_top="#9a6468",
                  house="#8a5d68", house_lit="#d69480", roof="#5a3a4b", trim="#4a3040", door="#3d2836",
                  win_on="#ffe4bb", win_off="#4a3446", tree="#5f6447", tree_lit="#a7a06c", trunk="#4a3a3d",
                  ground="#a27c72", walk="#bf9585", curb="#d9ab95", shadow="#4b3a4e", pole="#3b2c3a",
                  dust="#fff2d2", shaft="#ffe3b6", mist="#ffe9d2", fg="#2a1e2b", rim="#ffc58a"),
    "drama": dict(sky_top="#03050b", sky_mid="#0a1222", horizon="#1a2842", haze="#18253d", sun="#dfeeff", sun_glow="#6f8fbf",
                  far="#1d2a44", city="#16223a", bld="#111a2b", bld_lit="#2d4a72", bld_top="#0c1322",
                  house="#0e1626", house_lit="#294468", roof="#090f1a", trim="#070b14", door="#05080f",
                  win_on="#9fd6ff", win_off="#0a101c", tree="#0b111d", tree_lit="#1d2c46", trunk="#080c15",
                  ground="#0a0f18", walk="#111a28", curb="#1f2d45", shadow="#03060c", pole="#070b13",
                  dust="#a9c7e6", shaft="#ffcf8f", mist="#2a3c5c", fg="#02040a", rim="#8fd3ff",
                  neon="#ff2d55", lamp="#ffb35c", rain="#a8c4e0", warmwin="#ffb35c"),
}


# ---------------------------------------------------------------- materiais
def amat(name, color, strength=1.0, alpha=1.0, grad=None, fog=False):
    """emissão chapada com transparência. grad: None | ("radial", power) | ("band", power, soft) | ("shaft", power, soft)"""
    if name in bpy.data.materials:
        return bpy.data.materials[name]
    m = bpy.data.materials.new(name); m.use_nodes = True
    if hasattr(m, "surface_render_method"):
        m.surface_render_method = "BLENDED"
    nt = m.node_tree; N = nt.nodes; L = nt.links; N.clear()
    out = N.new("ShaderNodeOutputMaterial")
    em = N.new("ShaderNodeEmission"); em.inputs[0].default_value = (*srgb(color), 1); em.inputs[1].default_value = strength
    tr = N.new("ShaderNodeBsdfTransparent"); ms = N.new("ShaderNodeMixShader")
    fac = N.new("ShaderNodeMath"); fac.operation = "MULTIPLY"; fac.inputs[1].default_value = alpha
    if grad is None:
        fac.inputs[0].default_value = 1.0
    else:
        tc = N.new("ShaderNodeTexCoord"); sep = N.new("ShaderNodeSeparateXYZ"); L.new(tc.outputs["Object"], sep.inputs[0])
        kind = grad[0]
        if kind == "radial":            # círculo de raio 1 no plano XZ (objeto)
            vm = N.new("ShaderNodeVectorMath"); vm.operation = "LENGTH"; L.new(tc.outputs["Object"], vm.inputs[0])
            inv = N.new("ShaderNodeMapRange"); inv.inputs[1].default_value = 0.0; inv.inputs[2].default_value = 1.0
            inv.inputs[3].default_value = 1.0; inv.inputs[4].default_value = 0.0; inv.clamp = True
            L.new(vm.outputs["Value"], inv.inputs[0])
            pw = N.new("ShaderNodeMath"); pw.operation = "POWER"; pw.inputs[1].default_value = grad[1]
            L.new(inv.outputs[0], pw.inputs[0]); L.new(pw.outputs[0], fac.inputs[0])
        else:                           # faixa: z de 0 (base) a 1 (topo) e x de -1 a 1 (objeto, normalizado)
            zr = N.new("ShaderNodeMapRange"); zr.clamp = True
            if kind == "band":          # névoa: forte embaixo, some em cima
                zr.inputs[1].default_value = 0.0; zr.inputs[2].default_value = 1.0; zr.inputs[3].default_value = 1.0; zr.inputs[4].default_value = 0.0
            else:                       # feixe: forte em cima (perto da fonte), some embaixo
                zr.inputs[1].default_value = 0.0; zr.inputs[2].default_value = 1.0; zr.inputs[3].default_value = 0.0; zr.inputs[4].default_value = 1.0
            L.new(sep.outputs["Z"], zr.inputs[0])
            pz = N.new("ShaderNodeMath"); pz.operation = "POWER"; pz.inputs[1].default_value = grad[1]; L.new(zr.outputs[0], pz.inputs[0])
            ax = N.new("ShaderNodeMath"); ax.operation = "ABSOLUTE"; L.new(sep.outputs["X"], ax.inputs[0])
            xr = N.new("ShaderNodeMapRange"); xr.clamp = True; xr.interpolation_type = "SMOOTHSTEP"
            xr.inputs[1].default_value = 1.0 - grad[2]; xr.inputs[2].default_value = 1.0
            xr.inputs[3].default_value = 1.0; xr.inputs[4].default_value = 0.0
            L.new(ax.outputs[0], xr.inputs[0])
            mul = N.new("ShaderNodeMath"); mul.operation = "MULTIPLY"; L.new(pz.outputs[0], mul.inputs[0]); L.new(xr.outputs[0], mul.inputs[1])
            L.new(mul.outputs[0], fac.inputs[0])
    L.new(fac.outputs[0], ms.inputs[0]); L.new(tr.outputs[0], ms.inputs[1]); L.new(em.outputs[0], ms.inputs[2])
    L.new(ms.outputs[0], out.inputs[0])
    return m


def quad(name, x0, x1, z0, z1, m, y, rot_y=0.0, loc=(0, 0, 0), norm=True):
    """retângulo no plano XZ. norm=True: coordenadas do objeto normalizadas (x em -1..1, z em 0..1) para os degradês"""
    bm = bmesh.new()
    if norm:
        hw = (x1 - x0) / 2; cx = (x0 + x1) / 2; h = z1 - z0
        vs = [bm.verts.new(p) for p in ((-1, 0, 0), (1, 0, 0), (1, 0, 1), (-1, 0, 1))]
    else:
        vs = [bm.verts.new(p) for p in ((x0, 0, z0), (x1, 0, z0), (x1, 0, z1), (x0, 0, z1))]
    bm.faces.new(vs)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free(); me.materials.append(m)
    o = bpy.data.objects.new(name, me); bpy.context.scene.collection.objects.link(o)
    if norm:
        o.location = (cx + loc[0], y + loc[1], z0 + loc[2]); o.scale = (hw, 1, h)
    else:
        o.location = (loc[0], y + loc[1], loc[2])
    o.rotation_euler = (0, rot_y, 0)
    return o


def disc(name, r, m, loc, n=40):
    bm = bmesh.new()
    vs = [bm.verts.new((math.cos(2 * math.pi * i / n), 0, math.sin(2 * math.pi * i / n))) for i in range(n)]
    bm.faces.new(vs)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free(); me.materials.append(m)
    o = bpy.data.objects.new(name, me); bpy.context.scene.collection.objects.link(o)
    o.location = loc; o.scale = (r, 1, r)
    return o


def poly_mesh(name, verts, m):
    """malha a partir de vértices 3D (um polígono)"""
    bm = bmesh.new(); vs = [bm.verts.new(v) for v in verts]; bm.faces.new(vs)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free(); me.materials.append(m)
    o = bpy.data.objects.new(name, me); bpy.context.scene.collection.objects.link(o)
    return o


def ground_disc(name, rx, ry, m, loc, n=40):
    """elipse deitada no chão (plano XY), coordenadas do objeto normalizadas (raio 1)"""
    o = poly_mesh(name, [(math.cos(2 * math.pi * i / n), math.sin(2 * math.pi * i / n), 0.0) for i in range(n)], m)
    o.location = loc; o.scale = (rx, ry, 1)
    return o


def flat(name, pts, color, y, strength=1.0, fog=True):
    return mesh_pts(name, pts, fogmat(f"{name}__{color}_{strength}", color, strength, fog=fog), None, y)


def rect(x0, z0, x1, z1):
    return [(x0, z0), (x1, z0), (x1, z1), (x0, z1)]


def cycle_fcurves(ob):
    for fc in _fcs(ob):
        if not fc.modifiers:
            fc.modifiers.new("CYCLES")


# ---------------------------------------------------------------- céu
def sky(P, sc):
    w = sc.world; w.use_nodes = True
    nt = w.node_tree; N = nt.nodes; L = nt.links; N.clear()
    out = N.new("ShaderNodeOutputWorld"); bg = N.new("ShaderNodeBackground")
    tc = N.new("ShaderNodeTexCoord"); sep = N.new("ShaderNodeSeparateXYZ")
    L.new(tc.outputs["Generated"], sep.inputs[0])
    mr = N.new("ShaderNodeMapRange"); mr.inputs[1].default_value = -0.02; mr.inputs[2].default_value = 0.75; mr.clamp = True
    L.new(sep.outputs["Z"], mr.inputs[0])
    ramp = N.new("ShaderNodeValToRGB")
    els = ramp.color_ramp.elements
    els[0].position = 0.0; els[0].color = (*srgb(P["horizon"]), 1)
    els[1].position = 1.0; els[1].color = (*srgb(P["sky_top"]), 1)
    e = els.new(0.22); e.color = (*srgb(P["sky_mid"]), 1)
    L.new(mr.outputs[0], ramp.inputs["Fac"]); L.new(ramp.outputs["Color"], bg.inputs["Color"])
    bg.inputs["Strength"].default_value = 1.0
    L.new(bg.outputs[0], out.inputs["Surface"])


# ---------------------------------------------------------------- peças
def building(name, x, y, w, h, P, rnd, win=True, lit=0.3, sun_side=1, top=True):
    flat(name, rect(x - w / 2, 0, x + w / 2, h), P["bld"], y)
    lw = w * 0.13                                    # lado iluminado (ou recortado pelo néon na noite)
    xs = x + w / 2 - lw if sun_side > 0 else x - w / 2
    flat(name + "_lit", rect(xs, 0, xs + lw, h), P["bld_lit"], y - 0.01)
    if top:
        flat(name + "_cor", rect(x - w / 2 - 0.12, h - 0.18, x + w / 2 + 0.12, h), P["bld_top"], y - 0.02)
    if win:
        cols = max(2, int(w / 1.0)); rows = max(2, int((h - 1.0) / 1.3))
        for i in range(cols):
            for j in range(rows):
                wx = x - w / 2 + (i + 0.5) * w / cols; wz = 1.0 + j * 1.3 + 0.45
                if wz + 0.45 > h - 0.2:
                    continue
                on = rnd.random() < lit
                col = P["win_on"] if on else P["win_off"]
                if on and "warmwin" in P and rnd.random() < 0.4:
                    col = P["warmwin"]
                flat(f"{name}_w{i}_{j}", rect(wx - 0.22, wz - 0.32, wx + 0.22, wz + 0.32), col, y - 0.02, 1.3 if on else 1.0)


def house(name, x, y, w, h, P, rnd, lit=0.3, sun_side=1):
    flat(name, rect(x - w / 2, 0, x + w / 2, h), P["house"], y)
    lw = w * 0.12
    xs = x + w / 2 - lw if sun_side > 0 else x - w / 2
    flat(name + "_lit", rect(xs, 0, xs + lw, h), P["house_lit"], y - 0.01)
    flat(name + "_roof", [(x - w / 2 - 0.3, h), (x + w / 2 + 0.3, h), (x + w * 0.18, h + w * 0.34), (x - w * 0.18, h + w * 0.34)], P["roof"], y - 0.015)
    flat(name + "_chim", rect(x + w * 0.22, h + w * 0.1, x + w * 0.22 + 0.35, h + w * 0.42), P["roof"], y + 0.01)
    cols = max(2, int(w / 1.4))
    for i in range(cols):
        for j in range(2):
            wx = x - w / 2 + (i + 0.5) * w / cols; wz = 1.55 + j * 1.75
            if wz + 0.5 > h:
                continue
            on = rnd.random() < lit
            flat(f"{name}_w{i}{j}", rect(wx - 0.3, wz - 0.42, wx + 0.3, wz + 0.42), P["win_on"] if on else P["win_off"], y - 0.03, 1.3 if on else 1.0)
            flat(f"{name}_wf{i}{j}", rect(wx - 0.36, wz - 0.48, wx + 0.36, wz + 0.48), P["trim"], y - 0.02)
            flat(f"{name}_ws{i}{j}", rect(wx - 0.4, wz - 0.52, wx + 0.4, wz - 0.46), P["house_lit"], y - 0.035)
    dx = x + rnd.uniform(-w / 4, w / 4)
    flat(name + "_door", rect(dx - 0.42, 0.18, dx + 0.42, 2.2), P["door"], y - 0.03)
    for k in range(3):
        flat(f"{name}_st{k}", rect(dx - 0.62 - k * 0.12, 0.06 * k, dx + 0.62 + k * 0.12, 0.06 * (k + 1)), P["trim"], y - 0.06 - 0.03 * (3 - k))


def tree(name, x, y, s, P, sun_side=1):
    flat(name + "_t", rect(x - 0.08 * s, 0, x + 0.08 * s, 1.9 * s), P["trunk"], y)
    pts = smooth([(x - 1.1 * s, 2.0 * s), (x - 0.8 * s, 3.0 * s), (x, 3.45 * s), (x + 0.85 * s, 3.05 * s), (x + 1.15 * s, 2.1 * s), (x, 1.65 * s)], 10)
    flat(name + "_c", pts, P["tree"], y - 0.01)
    o = 0.28 * s * sun_side
    pts2 = smooth([(x - 0.45 * s + o, 2.6 * s), (x - 0.2 * s + o, 3.25 * s), (x + 0.5 * s + o, 3.1 * s), (x + 0.75 * s + o, 2.45 * s), (x + 0.15 * s + o, 2.2 * s)], 8)
    flat(name + "_cl", pts2, P["tree_lit"], y - 0.015)


def lamp(name, x, y, P, on=False, h=3.6):
    flat(name + "_p", rect(x - 0.05, 0, x + 0.05, h), P["pole"], y)
    flat(name + "_a", rect(x, h - 0.06, x + 0.5, h), P["pole"], y)
    flat(name + "_h", rect(x + 0.32, h - 0.16, x + 0.62, h - 0.04), P["pole"], y - 0.01)
    if on:
        col = P.get("lamp", "#ffcf8a")
        flat(name + "_b", rect(x + 0.36, h - 0.2, x + 0.58, h - 0.15), col, y - 0.02, 4.0, fog=False)
        sets.glow(name + "_g", col, 1.2, (x + 0.47, y - 0.06, h - 0.2), power=2.4, strength=1.2)
        # cone de luz até o chão + poça de luz
        cone = poly_mesh(name + "_cone", [(-1, 0, 0), (1, 0, 0), (0.12, 0, 1), (-0.12, 0, 1)],
                         amat(name + "_conem", col, 1.0, 0.16, ("shaft", 1.1, 0.9)))
        cone.location = (x + 0.47, y - 0.08, 0.0); cone.scale = (1.25, 1, h - 0.2)
        ground_disc(name + "_pool", 1.5, 0.9, amat(name + "_poolm", col, 0.9, 0.4, ("radial", 2.0)), (x + 0.47, y - 0.3, 0.003))


def fence(name, x0, x1, y, P, h=0.95):
    c = P["pole"]
    flat(name + "_r1", rect(x0, h - 0.05, x1, h), c, y)
    flat(name + "_r2", rect(x0, 0.38, x1, 0.42), c, y)
    x = x0
    while x < x1:
        flat(f"{name}_p{x:.2f}", rect(x - 0.022, 0, x + 0.022, h + 0.07), c, y)
        x += 0.3


def ground(P):
    gm = fogmat("ground_m", P["ground"])
    poly_mesh("ground", [(-900, -20, -0.004), (900, -20, -0.004), (900, 900, -0.004), (-900, 900, -0.004)], gm)
    # calçada (onde o personagem pisa) e meio-fio
    flat("walk", rect(-60, -0.002, 60, 0.0), P["walk"], 0.0)
    w = bpy.data.objects["walk"]
    for v in w.data.vertices:          # transforma o retângulo numa faixa deitada no chão (y de -2.5 a 2.2)
        v.co = (v.co.x, -20.0 if v.co.z < -0.001 else 2.2, -0.002)
    flat("curb", rect(-60, 0, 60, 0.12), P["curb"], 2.25)


# ---------------------------------------------------------------- ar: poeira, feixes, névoa, chuva, vapor
def dust(P, n, x_range, sc_frames, seed=3, color=None, alpha=0.75, size=(0.006, 0.016), z_range=(0.2, 3.6), y_range=(-2.6, 7.0)):
    rnd = random.Random(seed)
    m = amat("dust_m" + str(seed), color or P["dust"], 1.6, alpha, ("radial", 1.6))
    objs = []
    for i in range(n):
        x = rnd.uniform(*x_range); z = rnd.uniform(*z_range); y = rnd.uniform(*y_range)
        r = rnd.uniform(*size) * (1.0 + 0.6 * max(0.0, -y) / 2.6)
        o = disc(f"dust{seed}_{i}", r, m, (x, y, z), n=16)
        f = 1; dx = rnd.uniform(0.03, 0.09); dz = rnd.uniform(-0.03, 0.05)
        ph = rnd.uniform(0, 6.28)
        while f <= sc_frames + 48:
            o.location = (x + dx * f / 24.0, y, z + dz * f / 24.0 + 0.04 * math.sin(ph + f / 30.0))
            key(o, "location", f, "BEZIER")
            s = r * (0.55 + 0.45 * (0.5 + 0.5 * math.sin(ph * 1.7 + f / 13.0)))
            o.scale = (s, 1, s); key(o, "scale", f, "BEZIER")
            f += 24
        objs.append(o)
    return objs


def shafts(P, specs, frames, seed=5, top_z=9.0):
    """feixes de luz diagonais (vindos do sol): specs = [(x_topo, y, largura, comprimento, alpha)]"""
    rnd = random.Random(seed); objs = []
    ang = math.radians(33)
    for i, (x, y, w, L, a) in enumerate(specs):
        m = amat(f"shaft_m{i}", P["shaft"], 1.6, a, ("shaft", 1.1, 0.9))
        o = quad(f"shaft{i}", -1, 1, 0, 1, m, y)
        o.scale = (w / 2, 1, L); o.rotation_euler = (0, ang, 0)
        o.location = (x - L * math.sin(ang), y, top_z - L * math.cos(ang))
        x0 = o.location.x
        f = 1
        while f <= frames + 48:      # o feixe "respira": desliza e varia a largura devagar
            o.location.x = x0 + 0.25 * math.sin(f / 70.0 + i)
            key(o, "location", f, "BEZIER")
            o.scale.x = (w / 2) * (0.85 + 0.15 * math.sin(f / 45.0 + 2 * i)); key(o, "scale", f, "BEZIER")
            f += 24
        objs.append(o)
    return objs


def mist(P, specs, frames):
    """faixas de névoa rente ao chão: specs = [(y, altura, alpha, deriva_por_seg)]"""
    for i, (y, h, a, drift) in enumerate(specs):
        m = amat(f"mist_m{i}", P["mist"], 1.0, a, ("band", 1.6, 0.25))
        o = quad(f"mist{i}", -1, 1, 0, 1, m, y)
        o.scale = (70, 1, h); o.location = (0, y, -0.05)
        o.location.x = 0; key(o, "location", 1, "LINEAR")
        o.location.x = drift * frames / 24.0; key(o, "location", frames, "LINEAR")


def rain(P, n, x_range, frames, seed=8):
    rnd = random.Random(seed)
    m = amat("rain_m", P["rain"], 1.4, 0.38)
    for i in range(n):
        y = rnd.uniform(-2.4, 14.0); x = rnd.uniform(*x_range)
        L = rnd.uniform(0.18, 0.34) * (1.0 + max(0.0, -y) * 0.3); w = 0.0045 * (1.0 + max(0.0, -y) * 0.5)
        o = quad(f"rain{i}", -1, 1, 0, 1, m, y)
        o.scale = (w, 1, L); o.rotation_euler = (0, math.radians(10), 0)
        per = rnd.randint(9, 13); z_top = 6.0; ph = rnd.randint(0, per - 1)
        o.location = (x, y, z_top); key(o, "location", 1 - ph, "LINEAR")
        o.location = (x - 0.9, y, -0.6); key(o, "location", 1 - ph + per, "LINEAR")
        cycle_fcurves(o)


def steam(P, x, y, frames, n=7, color=None, seed=12):
    rnd = random.Random(seed)
    m = amat("steam_m", color or P["mist"], 1.0, 0.22, ("radial", 1.8))
    for i in range(n):
        o = disc(f"steam{i}", 1.0, m, (x, y, 0.0), n=24)
        per = 72; ph = int(i * per / n)
        for f, z, s in ((1 - ph, 0.05, 0.12), (1 - ph + per // 2, 1.3, 0.55), (1 - ph + per, 2.8, 1.1)):
            o.location = (x + rnd.uniform(-0.2, 0.2), y, z); key(o, "location", f, "LINEAR")
            o.scale = (s, 1, s); key(o, "scale", f, "LINEAR")
        cycle_fcurves(o)


def neon(name, text, x, z, y, P, size=0.42):
    col = P["neon"]
    box = mesh_pts(name + "_box", rrect(x - size * 1.5, z - size * 0.55, x + size * 1.5, z + size * 0.55, 0.06),
                   fogmat(name + "_boxm", "#0b0f19"), None, y)
    t = lib.text(name + "_t", text, size, amat(name + "_tm", col, 6.0, 1.0), None, (x, y - 0.02, z), lib.font())
    t.rotation_euler = (math.pi / 2, 0, 0)
    sets.glow(name + "_g", col, 2.4, (x, y - 0.03, z), power=2.6, strength=0.9)



def ground_shadow(name, x0, y0, dx, dy, w, P, alpha=0.32):
    """sombra longa deitada no chão: começa em (x0, y0) e se estende por (dx, dy), largura w"""
    m = amat("lshadow_m", P["shadow"], 1.0, alpha)
    ln = math.hypot(dx, dy); nx, ny = -dy / ln * w / 2, dx / ln * w / 2
    return poly_mesh(name, [(x0 - nx, y0 - ny, 0.003), (x0 + nx, y0 + ny, 0.003),
                            (x0 + dx + nx * 0.6, y0 + dy + ny * 0.6, 0.003), (x0 + dx - nx * 0.6, y0 + dy - ny * 0.6, 0.003)], m)


def tiles(P, x0, x1, y0, y1, step=0.9, color=None):
    m = fogmat("tile_m", color or P["shadow"])
    x = x0
    while x < x1:
        poly_mesh(f"tile{x:.1f}", [(x - 0.008, y0, 0.001), (x + 0.008, y0, 0.001), (x + 0.008, y1, 0.001), (x - 0.008, y1, 0.001)], m)
        x += step
    for yy in (y0 + (y1 - y0) * 0.5,):
        poly_mesh(f"tiley{yy:.1f}", [(x0, yy - 0.01, 0.001), (x1, yy - 0.01, 0.001), (x1, yy + 0.01, 0.001), (x0, yy + 0.01, 0.001)], m)


def wet_ground(P):
    """chão molhado: reflete de verdade as luzes da cena (néon, poste, janelas)"""
    m = bpy.data.materials.new("wet_ground"); m.use_nodes = True
    p = m.node_tree.nodes["Principled BSDF"]
    p.inputs["Base Color"].default_value = (*srgb(P["walk"]), 1)
    p.inputs["Roughness"].default_value = 0.22
    p.inputs["Specular IOR Level"].default_value = 0.55
    poly_mesh("wetground", [(-60, -20, 0.0005), (60, -20, 0.0005), (60, 2.3, 0.0005), (-60, 2.3, 0.0005)], m)


def contact_shadow(h, P, w=0.32):
    """sombra de contato sob os pés (segue o personagem)"""
    m = amat("cshadow_m", P["shadow"], 1.0, 0.6, ("radial", 1.2))
    o = ground_disc(h.name + "_cshadow", w, 0.16, m, (0, 0, 0.002))
    o.parent = h.root; o.location = (0.0, 0.0, 0.002)
    return o


def long_shadow(h, P, dx=-0.9, dy=-1.3, alpha=0.3):
    """sombra longa do personagem (luz baixa da manhã), presa aos pés"""
    o = ground_shadow(h.name + "_lshadow", 0.0, 0.0, dx, dy, 0.26, P, alpha)
    o.parent = h.root
    return o


# ---------------------------------------------------------------- cenas
def manha(frames, x_range=(-12.0, 14.0), seed=4, foreground=True):
    P = PAL["manha"]; sc = bpy.context.scene; rnd = random.Random(seed)
    sets.FOG.update(color=P["haze"], near=4.0, far=110.0, max=0.9)
    sky(P, sc)
    a, b = x_range
    # sol mais alto à direita, aparecendo acima dos telhados, com brilho e raios
    disc("sun", 9.0, amat("sun_m", P["sun"], 4.0, 1.0), (60, 300, 120))
    sets.glow("sun_glow", P["sun_glow"], 160, (60, 295, 120), power=2.0, strength=0.95)
    sets2d_rays(P, (60, 292, 120), 260)
    # horizonte e cidade (silhuetas com névoa)
    x = a * 6
    while x < b * 6:
        w = rnd.uniform(5, 11); h = rnd.uniform(9, 22)
        flat(f"far{x:.0f}", rect(x, 0, x + w, h), P["far"], 130 + rnd.uniform(0, 30))
        x += w + rnd.uniform(0, 3)
    x = a * 3
    while x < b * 3:
        w = rnd.uniform(3.5, 7); h = rnd.uniform(7, 16)
        building(f"city{x:.0f}", x + w / 2, 60 + rnd.uniform(0, 10), w, h, P, rnd, win=False, top=True)
        x += w + rnd.uniform(0.5, 2.5)
    x = a * 1.8
    while x < b * 1.8:
        w = rnd.uniform(4, 6.5); h = rnd.uniform(6, 10)
        building(f"bld{x:.0f}", x + w / 2, 28 + rnd.uniform(0, 4), w, h, P, rnd, lit=0.22)
        x += w + rnd.uniform(0.6, 2.0)
    for k in range(int((b - a) / 3.6) + 2):
        tree(f"tm{k}", a - 2 + k * 3.6 + rnd.uniform(-0.8, 0.8), 15.0, rnd.uniform(1.2, 1.5), P)
    x = a - 2
    while x < b + 2:
        w = rnd.uniform(4.2, 6.0); h = rnd.uniform(3.4, 4.4)
        house(f"h_{x:.0f}", x + w / 2, 9.5, w, h, P, rnd, lit=0.25)
        x += w + rnd.uniform(1.6, 3.0)
    for k in range(int((b - a) / 5.0) + 2):
        tree(f"tn{k}", a - 1 + k * 5.0 + rnd.uniform(-0.6, 0.6), 6.0, rnd.uniform(0.9, 1.1), P)
    fence("fence", a - 3, b + 3, 2.6, P)
    for k, lx in enumerate(range(int(a) - 2, int(b) + 3, 6)):
        lamp(f"lamp{k}", lx + 1.5, 2.45, P, on=False)
    ground(P)
    tiles(P, a - 3, b + 3, -12.0, 2.2)
    # sombras longas da manhã (o sol está atrás e à direita: as sombras vêm para a frente e para a esquerda)
    x = a - 3
    while x < b + 3:
        ground_shadow(f"fsh{x:.2f}", x, 2.55, -0.55, -1.05, 0.05, P, 0.22)
        x += 0.3
    ground_shadow("fsh_rail", (a + b) / 2, 2.4, -0.4, -0.8, b - a + 6, P, 0.12)
    # luz: feixes diagonais na frente das casas, névoa rente ao chão e poeira no ar
    shafts(P, [(7.5, 4.5, 1.4, 9.0, 0.24), (4.0, 5.5, 2.2, 9.5, 0.2), (1.2, 3.8, 0.9, 8.5, 0.22),
               (-2.0, 6.0, 1.8, 9.5, 0.18), (-5.5, 4.2, 1.2, 9.0, 0.2), (10.5, 6.5, 2.4, 9.5, 0.18),
               (2.6, -1.0, 1.0, 8.0, 0.07)], frames, top_z=7.5)
    mist(P, [(8.5, 1.4, 0.32, 0.05), (20.0, 3.0, 0.40, -0.04), (45.0, 6.0, 0.45, 0.03)], frames)
    dust(P, 220, (a, b), frames, size=(0.009, 0.024))
    for k, (fx, fz, s) in enumerate(((-1.55, 0.25, 0.9), (1.75, 0.15, 0.8), (-1.9, 2.9, 0.6)) if foreground else ()):
        pts = smooth([(fx - 0.6 * s, fz - 0.4 * s), (fx - 0.75 * s, fz + 0.3 * s), (fx - 0.1 * s, fz + 0.75 * s),
                      (fx + 0.6 * s, fz + 0.45 * s), (fx + 0.7 * s, fz - 0.3 * s), (fx, fz - 0.6 * s)], 10)
        flat(f"fg{k}", pts, P["fg"], -1.7, fog=False)
    return P


def drama(frames, x_range=(-12.0, 14.0), seed=6, foreground=True):
    P = PAL["drama"]; sc = bpy.context.scene; rnd = random.Random(seed)
    sets.FOG.update(color=P["haze"], near=3.0, far=80.0, max=0.92)
    sky(P, sc)
    a, b = x_range
    disc("moon", 2.2, amat("moon_m", P["sun"], 2.0, 1.0), (-18, 240, 40))
    sets.glow("moon_glow", P["sun_glow"], 26, (-18, 236, 40), power=2.6, strength=0.6)
    x = a * 6
    while x < b * 6:
        w = rnd.uniform(5, 11); h = rnd.uniform(14, 34)
        flat(f"far{x:.0f}", rect(x, 0, x + w, h), P["far"], 120 + rnd.uniform(0, 30))
        x += w + rnd.uniform(0, 3)
    x = a * 3
    while x < b * 3:
        w = rnd.uniform(3.5, 7); h = rnd.uniform(10, 24)
        building(f"city{x:.0f}", x + w / 2, 55 + rnd.uniform(0, 10), w, h, P, rnd, win=True, lit=0.08, sun_side=-1)
        x += w + rnd.uniform(0.5, 2.5)
    x = a * 1.8
    while x < b * 1.8:
        w = rnd.uniform(4, 6.5); h = rnd.uniform(9, 16)
        building(f"bld{x:.0f}", x + w / 2, 18 + rnd.uniform(0, 4), w, h, P, rnd, lit=0.12, sun_side=-1)
        x += w + rnd.uniform(0.4, 1.4)
    x = a - 2
    while x < b + 2:
        w = rnd.uniform(4.2, 6.2); h = rnd.uniform(6.0, 8.0)
        building(f"near{x:.0f}", x + w / 2, 6.5, w, h, P, rnd, lit=0.1, sun_side=-1)
        x += w + rnd.uniform(0.2, 0.8)
    neon("neon1", "BAR", 2.6, 3.9, 6.3, P)
    for k, lx in enumerate(range(int(a) - 2, int(b) + 3, 7)):
        lamp(f"lamp{k}", lx + 0.8, 2.4, P, on=True)
    ground(P)
    wet_ground(P)
    mist(P, [(4.0, 1.4, 0.45, 0.05), (12.0, 3.0, 0.5, -0.04), (30.0, 6.0, 0.55, 0.03)], frames)
    rain(P, 260, (a, b + 3), frames)
    steam(P, 1.4, 1.2, frames)
    dust(P, 60, (a, b), frames, color=P["dust"], alpha=0.35, size=(0.004, 0.01))
    for k, (fx, fz, s) in enumerate(((-1.55, 0.25, 0.9), (1.8, 0.15, 0.8)) if foreground else ()):
        pts = smooth([(fx - 0.6 * s, fz - 0.4 * s), (fx - 0.75 * s, fz + 0.3 * s), (fx - 0.1 * s, fz + 0.75 * s),
                      (fx + 0.6 * s, fz + 0.45 * s), (fx + 0.7 * s, fz - 0.3 * s), (fx, fz - 0.6 * s)], 10)
        flat(f"fg{k}", pts, P["fg"], -1.7, fog=False)
    return P


def sets2d_rays(P, loc, size=160):
    import sets2d
    sets2d.rays("sun_rays", loc, size, P["sun_glow"], n=11, power=1.4, strength=0.5)


# ---------------------------------------------------------------- câmera e acabamento
def camera(sc, keys, lens=35, focus=3.4, fstop=0.8):
    """keys = [(quadro, (x, y, z)), ...] — só translação"""
    cd = bpy.data.cameras.new("cam"); cd.sensor_fit = "HORIZONTAL"; cd.sensor_width = 24; cd.lens = lens
    cd.clip_end = 3000; cd.clip_start = 0.05
    cam = bpy.data.objects.new("cam", cd); sc.collection.objects.link(cam); sc.camera = cam
    cam.rotation_euler = (math.radians(90), 0, 0)
    cd.dof.use_dof = True; cd.dof.focus_distance = focus; cd.dof.aperture_fstop = fstop
    for f, p in keys:
        cam.location = p; key(cam, "location", f, "BEZIER")
    return cam


POST = {
    "manha": "format=gbrp,split[a][b];[b]curves=all='0/0 0.62/0 1/1',gblur=sigma=26[g];[a][g]blend=all_mode=screen:all_opacity=0.5,"
             "colorbalance=rs=0.02:bs=-0.03:rh=0.03:bh=-0.04,vignette=angle=PI/5,noise=alls=4:allf=t,format=yuv420p",
    "drama": "format=gbrp,split[a][b];[b]curves=all='0/0 0.5/0 1/1',gblur=sigma=22[g];[a][g]blend=all_mode=screen:all_opacity=0.6,"
             "colorbalance=bs=0.05:bm=0.02:rh=0.03,curves=all='0/0 0.25/0.18 0.75/0.8 1/1',vignette=angle=PI/4,noise=alls=6:allf=t,format=yuv420p",
}
