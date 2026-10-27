"""Cenários chapados com profundidade (estilo IfverseTales): cor plana + névoa por distância da câmera.
Tudo é 3D de verdade (parallax real), mas sem luz/sombra realista, então parece ilustração 2D."""
import bpy, bmesh, math, random
from mathutils import Vector
import lib
from lib import srgb, link, empty

FOG = {"color": "#c98a72", "near": 4.0, "far": 60.0, "max": 0.85}


def fogmat(name, color, strength=1.0, fog=True, alpha=None):
    """emissão plana que vai se misturando na cor da névoa conforme a distância"""
    key = f"{name}"
    if key in bpy.data.materials:
        return bpy.data.materials[key]
    m = bpy.data.materials.new(key); m.use_nodes = True
    nt = m.node_tree; N = nt.nodes; L = nt.links; N.clear()
    out = N.new("ShaderNodeOutputMaterial"); em = N.new("ShaderNodeEmission"); em.inputs[1].default_value = strength
    base = N.new("ShaderNodeRGB"); base.outputs[0].default_value = (*srgb(color), 1)
    if fog:
        cam = N.new("ShaderNodeCameraData")
        mr = N.new("ShaderNodeMapRange"); mr.inputs[1].default_value = FOG["near"]; mr.inputs[2].default_value = FOG["far"]
        mr.inputs[3].default_value = 0.0; mr.inputs[4].default_value = FOG["max"]; mr.clamp = True
        L.new(cam.outputs["View Distance"], mr.inputs[0])
        mix = N.new("ShaderNodeMix"); mix.data_type = "RGBA"
        mix.inputs[7].default_value = (*srgb(FOG["color"]), 1)
        L.new(mr.outputs[0], mix.inputs[0]); L.new(base.outputs[0], mix.inputs[6])
        L.new(mix.outputs[2], em.inputs[0])
    else:
        L.new(base.outputs[0], em.inputs[0])
    if alpha is not None:
        tr = N.new("ShaderNodeBsdfTransparent"); ms = N.new("ShaderNodeMixShader")
        ms.inputs[0].default_value = alpha
        L.new(tr.outputs[0], ms.inputs[1]); L.new(em.outputs[0], ms.inputs[2]); L.new(ms.outputs[0], out.inputs[0])
        m.blend_method = "BLEND" if hasattr(m, "blend_method") else None
    else:
        L.new(em.outputs[0], out.inputs[0])
    return m


def glow(name, color, radius, loc, rot=(math.pi / 2, 0, 0), power=2.0, strength=1.5):
    """disco de brilho com degradê radial transparente (sol, luz de poste)"""
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; N = nt.nodes; L = nt.links; N.clear()
    out = N.new("ShaderNodeOutputMaterial")
    tc = N.new("ShaderNodeTexCoord"); grad = N.new("ShaderNodeTexGradient"); grad.gradient_type = "SPHERICAL"
    mp = N.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (1, 1, 1)
    L.new(tc.outputs["Object"], mp.inputs[0]); L.new(mp.outputs[0], grad.inputs[0])
    pw = N.new("ShaderNodeMath"); pw.operation = "POWER"; pw.inputs[1].default_value = power
    L.new(grad.outputs["Fac"], pw.inputs[0])
    em = N.new("ShaderNodeEmission"); em.inputs[0].default_value = (*srgb(color), 1); em.inputs[1].default_value = strength
    if hasattr(m, "surface_render_method"):
        m.surface_render_method = "BLENDED"
    tr = N.new("ShaderNodeBsdfTransparent"); ms = N.new("ShaderNodeMixShader")
    L.new(pw.outputs[0], ms.inputs[0]); L.new(tr.outputs[0], ms.inputs[1]); L.new(em.outputs[0], ms.inputs[2])
    L.new(ms.outputs[0], out.inputs[0])
    bm = bmesh.new(); bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=radius)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free(); me.materials.append(m)
    o = link(bpy.data.objects.new(name, me), None, loc); o.rotation_euler = rot
    return o


def _box(name, size, m, loc):
    return lib.box(name, size, m, None, loc, 0.0, False)


def sky(top="#2f2450", bottom="#e2956a"):
    """céu em degradê (caixa emissiva grande)"""
    room = lib.Room(); room.color(1, top, bottom)
    for n in room.m.node_tree.nodes:
        if n.type == "MAP_RANGE":
            n.inputs[1].default_value = 2.0; n.inputs[2].default_value = 34.0
    fl = bpy.data.objects["floor"]; fl.hide_render = True
    return room


def building(name, x, y, w, d, h, col, win="#ffb35c", lit=0.55, rnd=None, face=-1, wcol=None):
    rnd = rnd or random.Random(1)
    m = fogmat(name + "_m", col)
    b = _box(name, (w, d, h), m, (x, y, h / 2))
    wm = fogmat(name + "_win", win, 1.6)
    dark = fogmat(name + "_wdark", wcol or "#20182c")
    cols = max(2, int(w / 0.9)); rows = max(2, int(h / 1.1))
    for i in range(cols):
        for j in range(rows):
            if j == 0:
                continue
            wx = x - w / 2 + (i + 0.5) * w / cols
            wz = (j + 0.45) * h / rows
            on = rnd.random() < lit
            _box(f"{name}_w{i}_{j}", (w / cols * 0.5, 0.02, h / rows * 0.5), wm if on else dark,
                 (wx, y + face * (d / 2 + 0.011), wz))
    return b


def tree(name, x, y, s=1.0, col="#2a2036"):
    m = fogmat(name + "_m", col)
    lib.box(name + "_trunk", (0.12 * s, 0.12 * s, 1.6 * s), m, None, (x, y, 0.8 * s), 0.0, False)
    rnd = random.Random(hash(name) & 0xffff)
    for k in range(5):
        lib.sphere(f"{name}_c{k}", (0.55 + rnd.random() * 0.3) * s, m, None,
                   (x + rnd.uniform(-0.5, 0.5) * s, y + rnd.uniform(-0.3, 0.3) * s, (1.9 + rnd.uniform(-0.2, 0.5)) * s))


def lamp(name, x, y, h=3.2, col="#1d1626", light="#ffcf8a"):
    m = fogmat(name + "_m", col)
    lib.box(name + "_post", (0.07, 0.07, h), m, None, (x, y, h / 2), 0.0, False)
    lib.box(name + "_arm", (0.5, 0.06, 0.06), m, None, (x + 0.22, y, h), 0.0, False)
    lib.sphere(name + "_bulb", 0.09, fogmat(name + "_b", light, 3.0), None, (x + 0.45, y, h - 0.08))
    glow(name + "_glow", light, 0.9, (x + 0.45, y - 0.15, h - 0.1), power=2.5, strength=1.2)


def dusk_street(seed=3):
    """rua de cidade ao entardecer: calçada no eixo X, prédios atrás (y+), céu roxo/laranja, sol baixo"""
    rnd = random.Random(seed)
    sky("#2d2350", "#e8a072")
    # chão: calçada (perto) e rua (atrás)
    _box("sidewalk", (80, 4.0, 0.12), fogmat("sidewalk_m", "#3d2c44"), (0, 0.0, -0.06))
    _box("curb", (80, 0.18, 0.16), fogmat("curb_m", "#584060"), (0, 2.0, 0.0))
    _box("street", (80, 7.0, 0.1), fogmat("street_m", "#291d31"), (0, 5.5, -0.08))
    for k in range(-12, 13):
        _box(f"stripe{k}", (1.2, 0.12, 0.02), fogmat("stripe_m", "#6b5470"), (k * 3.0, 5.5, -0.02))
    _box("sidewalk2", (80, 3.0, 0.12), fogmat("sidewalk2_m", "#3a2a42"), (0, 10.5, -0.06))
    _box("ground_back", (160, 120, 0.1), fogmat("groundb_m", "#2f2238"), (0, 70, -0.1))
    _box("ground_front", (80, 20, 0.1), fogmat("groundf_m", "#2b1f33"), (0, -12, -0.1))
    # sol e brilho
    lib.sphere("sun", 4.0, fogmat("sun_m", "#ffe9c2", 2.0, fog=False), None, (-10, 95, 19))
    glow("sun_glow", "#ffb27a", 40, (-10, 94, 19), power=2.2, strength=0.9)
    # prédios do meio (frente da rua, fachadas viradas para -Y)
    x = -26
    i = 0
    while x < 26:
        w = rnd.uniform(3.0, 5.5); h = rnd.uniform(4.0, 9.0)
        col = rnd.choice(["#3b2b49", "#43304f", "#35273f", "#4a3452"])
        building(f"bld{i}", x + w / 2, 14.0 + rnd.uniform(0, 0.8), w, 4.0, h * 1.3, col, rnd=rnd)
        x += w + rnd.uniform(0.1, 0.6); i += 1
    # skyline distante
    x = -60
    while x < 60:
        w = rnd.uniform(3, 7); h = rnd.uniform(8, 22)
        _box(f"far{x:.0f}", (w, 3, h * 1.5), fogmat("far_m", "#5b3f66"), (x, 45 + rnd.uniform(0, 8), h * 0.75))
        x += w + rnd.uniform(0, 1.5)
    # árvores e postes na calçada
    for k, tx in enumerate((-9, -3.5, 4.5, 11)):
        tree(f"tree{k}", tx, 11.0, rnd.uniform(1.1, 1.4))
    for k, lx in enumerate((-6.5, 1.0, 8.0)):
        lamp(f"lamp{k}", lx, 1.7)
    # primeiro plano (perto da câmera -> desfocado), fora do centro
    tree("fg_bush", -4.2, -3.6, 0.55, "#140f1c")
    return dict(ground_z=0.0)
