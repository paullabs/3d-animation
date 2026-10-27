"""Cenários em camadas planas (estilo IfverseTales). Cada elemento é uma forma de frente para a câmera
(fachada sem lateral), colocada numa profundidade. A câmera só desliza, então as camadas andam em
velocidades diferentes (parallax) e nada revela que é plano. Névoa por distância separa as camadas."""
import bpy, bmesh, math, random
import lib
from lib import srgb, link
import sets
from sets import fogmat, glow
from puppet2d import circle, capsule, smooth, mesh2d


def flat(name, pts, color, y, strength=1.0, fog=True, parent=None):
    return mesh2d(name, pts, fogmat(f"{name}_{color}", color, strength, fog=fog), parent, y)


def rect(x0, z0, x1, z1):
    return [(x0, z0), (x1, z0), (x1, z1), (x0, z1)]


def rays(name, loc, size, color="#ffd2a0", n=11, power=3.0, strength=0.7, sharp=6.0):
    """raios de sol num plano só: brilho radial x listras angulares"""
    m = bpy.data.materials.new(name); m.use_nodes = True
    if hasattr(m, "surface_render_method"):
        m.surface_render_method = "BLENDED"
    nt = m.node_tree; N = nt.nodes; L = nt.links; N.clear()
    out = N.new("ShaderNodeOutputMaterial")
    tc = N.new("ShaderNodeTexCoord")
    sep = N.new("ShaderNodeSeparateXYZ"); L.new(tc.outputs["Object"], sep.inputs[0])
    at = N.new("ShaderNodeMath"); at.operation = "ARCTAN2"
    L.new(sep.outputs["Z"], at.inputs[0]); L.new(sep.outputs["X"], at.inputs[1])
    mul = N.new("ShaderNodeMath"); mul.operation = "MULTIPLY"; mul.inputs[1].default_value = n
    L.new(at.outputs[0], mul.inputs[0])
    sn = N.new("ShaderNodeMath"); sn.operation = "SINE"; L.new(mul.outputs[0], sn.inputs[0])
    ab = N.new("ShaderNodeMath"); ab.operation = "ABSOLUTE"; L.new(sn.outputs[0], ab.inputs[0])
    pw = N.new("ShaderNodeMath"); pw.operation = "POWER"; pw.inputs[1].default_value = sharp
    L.new(ab.outputs[0], pw.inputs[0])
    grad = N.new("ShaderNodeTexGradient"); grad.gradient_type = "SPHERICAL"
    mp = N.new("ShaderNodeMapping"); L.new(tc.outputs["Object"], mp.inputs[0]); L.new(mp.outputs[0], grad.inputs[0])
    fall = N.new("ShaderNodeMath"); fall.operation = "POWER"; fall.inputs[1].default_value = power
    L.new(grad.outputs["Fac"], fall.inputs[0])
    tot = N.new("ShaderNodeMath"); tot.operation = "MULTIPLY"; L.new(pw.outputs[0], tot.inputs[0]); L.new(fall.outputs[0], tot.inputs[1])
    tot2 = N.new("ShaderNodeMath"); tot2.operation = "MULTIPLY"; tot2.inputs[1].default_value = 0.55; L.new(tot.outputs[0], tot2.inputs[0])
    em = N.new("ShaderNodeEmission"); em.inputs[0].default_value = (*srgb(color), 1); em.inputs[1].default_value = strength
    tr = N.new("ShaderNodeBsdfTransparent"); ms = N.new("ShaderNodeMixShader")
    L.new(tot2.outputs[0], ms.inputs[0]); L.new(tr.outputs[0], ms.inputs[1]); L.new(em.outputs[0], ms.inputs[2])
    L.new(ms.outputs[0], out.inputs[0])
    bm = bmesh.new(); bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=size)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free(); me.materials.append(m)
    o = link(bpy.data.objects.new(name, me), None, loc); o.rotation_euler = (math.pi / 2, 0, 0)
    return o


def house(name, x, y, w, h, col, roof=True, rnd=None, lit=0.6, win="#ffb766", trim="#2a1f33"):
    rnd = rnd or random.Random(1)
    flat(name, rect(x - w / 2, 0, x + w / 2, h), col, y)
    if roof:
        flat(name + "_roof", [(x - w / 2 - 0.25, h), (x + w / 2 + 0.25, h), (x, h + w * 0.32)], trim, y - 0.01)
    cols = max(2, int(w / 1.3)); rows = max(1, int((h - 1.2) / 1.6))
    for i in range(cols):
        for j in range(rows):
            wx = x - w / 2 + (i + 0.5) * w / cols; wz = 1.6 + j * 1.6 + 0.6
            if wz + 0.5 > h:
                continue
            on = rnd.random() < lit
            flat(f"{name}_w{i}{j}", rect(wx - 0.32, wz - 0.42, wx + 0.32, wz + 0.42), win if on else "#241a30", y - 0.02, 1.4 if on else 1.0)
            flat(f"{name}_wf{i}{j}", rect(wx - 0.36, wz - 0.46, wx + 0.36, wz + 0.46), trim, y - 0.015)
            flat(f"{name}_wm{i}{j}", rect(wx - 0.02, wz - 0.42, wx + 0.02, wz + 0.42), trim, y - 0.025)
    dx = x + rnd.uniform(-w / 4, w / 4)
    flat(name + "_door", rect(dx - 0.42, 0.25, dx + 0.42, 2.25), "#1c1426", y - 0.02)
    flat(name + "_doorwin", rect(dx - 0.18, 1.5, dx + 0.18, 1.95), win, y - 0.03, 1.2)
    for k in range(3):
        flat(f"{name}_step{k}", rect(dx - 0.6 - k * 0.12, 0.08 * k, dx + 0.6 + k * 0.12, 0.08 * (k + 1)), "#3a2d45", y - 0.04 - 0.05 * (3 - k))


def tree2d(name, x, y, s, col):
    flat(name + "_t", rect(x - 0.07 * s, 0, x + 0.07 * s, 1.8 * s), col, y)
    blob = smooth([(x - 1.0 * s, 1.9 * s), (x - 0.7 * s, 2.9 * s), (x, 3.3 * s), (x + 0.8 * s, 2.95 * s), (x + 1.05 * s, 2.0 * s), (x, 1.55 * s)], 10)
    flat(name + "_c", blob, col, y - 0.01)


def lamp2d(name, x, y, h=3.4, col="#1a1323", light="#ffd08a"):
    flat(name + "_p", rect(x - 0.05, 0, x + 0.05, h), col, y)
    flat(name + "_a", rect(x, h - 0.06, x + 0.45, h), col, y)
    flat(name + "_b", circle(x + 0.42, h - 0.12, 0.09, 24), light, y - 0.01, 3.0, fog=False)
    glow(name + "_g", light, 1.3, (x + 0.42, y - 0.05, h - 0.12), power=2.6, strength=1.0)


def fence(name, x0, x1, y, col="#21182b", h=0.9):
    flat(name + "_r1", rect(x0, h - 0.05, x1, h), col, y)
    flat(name + "_r2", rect(x0, 0.35, x1, 0.39), col, y)
    x = x0
    while x < x1:
        flat(f"{name}_p{x:.1f}", rect(x - 0.025, 0, x + 0.025, h + 0.06), col, y)
        x += 0.32


def dusk_street2d(seed=5, x_range=(-14, 18)):
    rnd = random.Random(seed)
    sets.FOG.update(color="#b07a8c", near=3.0, far=70.0, max=0.8)
    room = sets.sky("#2c2350", "#ee9c6c")
    for n in room.m.node_tree.nodes:
        if n.type == "MAP_RANGE":
            n.inputs[1].default_value = 0.0; n.inputs[2].default_value = 30.0
    a, b = x_range
    # chão (faixas horizontais vistas de frente: calçada, grama)
    lib.box("walk", (80, 3.2, 0.02), fogmat("walk_m", "#3b2b45"), None, (8, 0.4, -0.01), 0, False)
    lib.box("lawn", (80, 6.0, 0.02), fogmat("lawn_m", "#2a2038"), None, (8, 5.0, -0.012), 0, False)
    lib.box("far_ground", (300, 200, 0.02), fogmat("farg_m", "#3a2a48"), None, (0, 108, -0.02), 0, False)
    # sol, brilho e raios
    flat("sun", circle(4, 22, 3.2, 64), "#fff0d0", 120, 2.2, fog=False)
    glow("sun_glow", "#ffb27a", 45, (4, 119, 22), power=2.0, strength=0.9)
    rays("sun_rays", (4, 118, 22), 110, "#ffd7a8", n=9, power=1.6, strength=0.6)
    # cidade distante (silhuetas)
    x = a * 4
    while x < b * 4:
        w = rnd.uniform(3, 8); h = rnd.uniform(6, 20)
        flat(f"sky{x:.0f}", rect(x, 0, x + w, h), "#5a3e66", 45 + rnd.uniform(0, 10))
        x += w + rnd.uniform(0, 2)
    # segunda fileira de casas (mais névoa)
    x = a * 1.6
    while x < b * 1.6:
        w = rnd.uniform(3.5, 6); h = rnd.uniform(4, 7)
        house(f"h2_{x:.0f}", x + w / 2, 17 + rnd.uniform(0, 2), w, h, rnd.choice(["#4a3556", "#523b5e"]), rnd=rnd, lit=0.4)
        x += w + rnd.uniform(0.6, 2.0)
    # árvores do meio
    for k in range(int((b - a) / 4)):
        tree2d(f"tm{k}", a + k * 4.2 + rnd.uniform(-1, 1), 10.5, rnd.uniform(1.2, 1.6), "#30223e")
    # primeira fileira de casas
    x = a
    while x < b:
        w = rnd.uniform(4.0, 6.5); h = rnd.uniform(4.2, 6.2)
        house(f"h1_{x:.0f}", x + w / 2, 7.0, w, h, rnd.choice(["#3a2a48", "#412f50", "#36283f"]), rnd=rnd)
        x += w + rnd.uniform(1.0, 2.5)
    # cerca, postes
    fence("fence", a, b, 1.9)
    for k, lx in enumerate(range(int(a), int(b), 6)):
        lamp2d(f"lamp{k}", lx + 2.0, 2.2)
    # primeiro plano desfocado
    for k, fx in enumerate(range(int(a), int(b), 5)):
        flat(f"fg{k}", rect(fx - 0.09, -0.5, fx + 0.09, 5.0), "#120d18", -1.6, fog=False)
    return room
