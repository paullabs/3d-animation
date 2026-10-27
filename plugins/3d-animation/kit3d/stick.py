"""Personagem no estilo IfverseTales: boneco de cabeça redonda, moletom, membros finos,
sombreamento toon (parece 2D) com borda de luz. Usa o mesmo esqueleto/pose de human.Person.
Eixos: Z para cima, olha para -Y, lado A = +X."""
import bpy, bmesh, math
from mathutils import Vector
import lib
import human
from human import Person, skin_to, outline, ring, make_armature, build_body
from lib import D2R, srgb

HEAD_C = (0.0, 0.0, 1.80)     # centro da cabeça
HEAD_R = 0.205


# ---------------------------------------------------------------- material toon
def toon(name, base, shadow=None, rim="#ffc58a", rim_w=0.62, rim_side=(1.0, 0.7), emit=1.0):
    """cor chapada + sombra em degrau + borda de luz só de um lado (fica com cara de 2D)"""
    if name in bpy.data.materials:
        return bpy.data.materials[name]
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; N = nt.nodes; L = nt.links
    N.clear()
    out = N.new("ShaderNodeOutputMaterial")
    dif = N.new("ShaderNodeBsdfDiffuse")
    s2r = N.new("ShaderNodeShaderToRGB")
    ramp = N.new("ShaderNodeValToRGB"); ramp.color_ramp.interpolation = "CONSTANT"
    b = srgb(base); sh = srgb(shadow) if shadow else tuple(c * 0.55 for c in b)
    ramp.color_ramp.elements[0].color = (*sh, 1)
    ramp.color_ramp.elements[1].position = 0.18
    ramp.color_ramp.elements[1].color = (*b, 1)
    L.new(dif.outputs[0], s2r.inputs[0]); L.new(s2r.outputs[0], ramp.inputs[0])
    # borda: fresnel (facing) x lado da câmera
    lw = N.new("ShaderNodeLayerWeight"); lw.inputs[0].default_value = 0.5
    gt = N.new("ShaderNodeMath"); gt.operation = "GREATER_THAN"; gt.inputs[1].default_value = rim_w
    L.new(lw.outputs["Facing"], gt.inputs[0])
    geo = N.new("ShaderNodeNewGeometry")
    vt = N.new("ShaderNodeVectorTransform"); vt.vector_type = "NORMAL"; vt.convert_from = "WORLD"; vt.convert_to = "CAMERA"
    L.new(geo.outputs["Normal"], vt.inputs[0])
    dot = N.new("ShaderNodeVectorMath"); dot.operation = "DOT_PRODUCT"
    dot.inputs[1].default_value = (rim_side[0], rim_side[1], 0.0)
    L.new(vt.outputs[0], dot.inputs[0])
    side = N.new("ShaderNodeMath"); side.operation = "GREATER_THAN"; side.inputs[1].default_value = 0.2
    L.new(dot.outputs["Value"], side.inputs[0])
    mask = N.new("ShaderNodeMath"); mask.operation = "MULTIPLY"
    L.new(gt.outputs[0], mask.inputs[0]); L.new(side.outputs[0], mask.inputs[1])
    mix = N.new("ShaderNodeMix"); mix.data_type = "RGBA"
    L.new(mask.outputs[0], mix.inputs[0]); L.new(ramp.outputs[0], mix.inputs[6])
    mix.inputs[7].default_value = (*srgb(rim), 1)
    em = N.new("ShaderNodeEmission"); em.inputs[1].default_value = emit
    L.new(mix.outputs[2], em.inputs[0]); L.new(em.outputs[0], out.inputs[0])
    return m


def flat(name, color, strength=1.0):
    if name in bpy.data.materials:
        return bpy.data.materials[name]
    m = bpy.data.materials.new(name); m.use_nodes = True
    N = m.node_tree.nodes; N.clear()
    out = N.new("ShaderNodeOutputMaterial"); em = N.new("ShaderNodeEmission")
    em.inputs[0].default_value = (*srgb(color), 1); em.inputs[1].default_value = strength
    m.node_tree.links.new(em.outputs[0], out.inputs[0])
    return m


def ink(color="#0b0d18"):
    m = flat("stick_ink", color)
    m.use_backface_culling = True
    return m


# ---------------------------------------------------------------- proporções de boneco
def skeleton():
    V = {}
    def v(n, p, rx, ry=None):
        V[n] = (Vector(p), rx, ry if ry is not None else rx)
    v("pelvis", (0, 0, .93), .13, .092)
    v("waist",  (0, 0, 1.0), .128, .09)
    v("belly",  (0, 0, 1.16), .112, .08)
    v("chest",  (0, 0, 1.36), .118, .084)
    v("neck",   (0, 0, 1.52), .03)
    v("neck2",  (0, 0, 1.62), .032)
    for s, sx in (("A", 1), ("B", -1)):
        v("sh" + s,   (.135 * sx, 0, 1.44), .046)
        v("el" + s,   (.15 * sx, 0, 1.15), .04)
        v("wr" + s,   (.155 * sx, 0, .90), .035)
        v("palm" + s, (.155 * sx, 0, .845), .036, .036)
        for fi, fy in enumerate((-.02, 0.0, .02)):
            v(f"f{fi}" + s, (.155 * sx, fy, .79), .012)
        v("thumb" + s, (.152 * sx, -.038, .82), .012)
        v("hip" + s,  (.06 * sx, 0, .91), .055)
        v("kn" + s,   (.065 * sx, 0, .5), .045)
        v("an" + s,   (.067 * sx, 0, .1), .04)
        v("heel" + s, (.067 * sx, -.01, .045), .045)
        v("toe" + s,  (.067 * sx, -.15, .04), .045, .038)
    E = [("pelvis", "waist", "pelvis"), ("waist", "belly", "spine"), ("belly", "chest", "spine"), ("chest", "neck", "chest"), ("neck", "neck2", "neck")]
    for s in "AB":
        E += [("chest", "sh" + s, "clav" + s), ("sh" + s, "el" + s, "upper" + s), ("el" + s, "wr" + s, "fore" + s),
              ("wr" + s, "palm" + s, "hand" + s), ("palm" + s, "f0" + s, "hand" + s), ("palm" + s, "f1" + s, "hand" + s),
              ("palm" + s, "f2" + s, "hand" + s), ("palm" + s, "thumb" + s, "hand" + s),
              ("pelvis", "hip" + s, "pelvis"), ("hip" + s, "kn" + s, "thigh" + s), ("kn" + s, "an" + s, "shin" + s),
              ("an" + s, "heel" + s, "foot" + s), ("heel" + s, "toe" + s, "foot" + s)]
    return V, E


def bone_defs():
    UP, DOWN = human.UP, human.DOWN
    hx, hy, hz = HEAD_C
    B = {
        "pelvis": ((0, 0, .93), (0, 0, 1.12), None, UP),
        "spine":  ((0, 0, 1.12), (0, 0, 1.36), "pelvis", UP),
        "chest":  ((0, 0, 1.36), (0, 0, 1.52), "spine", UP),
        "neck":   ((0, 0, 1.52), (0, 0, 1.64), "chest", UP),
        "head":   ((0, 0, 1.64), (0, 0, 2.05), "neck", UP),
    }
    fy = hy - HEAD_R * 0.93
    for s, sx in (("A", 1), ("B", -1)):
        B["upper" + s] = ((.135 * sx, 0, 1.44), (.15 * sx, 0, 1.15), "chest", DOWN)
        B["fore" + s] = ((.15 * sx, 0, 1.15), (.155 * sx, 0, .90), "upper" + s, DOWN)
        B["hand" + s] = ((.155 * sx, 0, .90), (.155 * sx, 0, .78), "fore" + s, DOWN)
        B["thigh" + s] = ((.06 * sx, 0, .91), (.065 * sx, 0, .5), "pelvis", DOWN)
        B["shin" + s] = ((.065 * sx, 0, .5), (.067 * sx, 0, .1), "thigh" + s, DOWN)
        B["foot" + s] = ((.067 * sx, 0, .1), (.067 * sx, -.15, .04), "shin" + s, (0, 0, 1))
        B["brow" + s] = ((.072 * sx, fy, hz + .055), (.072 * sx, fy, hz + .085), "head", UP)
        B["eye" + s] = ((.072 * sx, fy, hz + .015), (.072 * sx, fy, hz + .045), "head", UP)
        B["pup" + s] = ((.072 * sx, fy - .012, hz + .015), (.072 * sx, fy - .012, hz + .045), "head", UP)
        B["must" + s] = ((.01 * sx, fy, hz - .05), (.01 * sx, fy, hz - .02), "head", UP)
    B["mouth"] = ((0, fy, hz - .07), (0, fy, hz - .04), "head", UP)
    return B


def arc(name, R, span_deg, r, m, n=24, k=8):
    """arco (sorriso) no plano XZ, centro na origem, abre para baixo; tubo de raio r"""
    bm = bmesh.new(); rows = []
    for i in range(n + 1):
        th = math.radians(-90 - span_deg / 2 + span_deg * i / n)
        cx, cz = R * math.cos(th), R * math.sin(th) + R
        nx, nz = math.cos(th), math.sin(th)
        row = []
        for j in range(k):
            ph = 2 * math.pi * j / k
            row.append(bm.verts.new((cx + nx * r * math.cos(ph), r * math.sin(ph), cz + nz * r * math.cos(ph))))
        rows.append(row)
    for i in range(n):
        for j in range(k):
            bm.faces.new((rows[i][j], rows[i + 1][j], rows[i + 1][(j + 1) % k], rows[i][(j + 1) % k]))
    for row in (rows[0], rows[-1]):
        bm.faces.new(row)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    for p in me.polygons:
        p.use_smooth = True
    me.materials.append(m)
    o = bpy.data.objects.new(name, me); bpy.context.scene.collection.objects.link(o)
    return o


class Stick(Person):
    def __init__(self, name, hoodie="#e2462c", hoodie_shadow="#a8291b", skin="#151a2e", pants=None,
                 rim="#ffc58a", scale=1.0, hood=True, strings=True):
        self.name = name; self.base_scale = scale
        pants = pants or hoodie
        m_h = toon(name + "_hoodie", hoodie, hoodie_shadow, rim)
        m_p = toon(name + "_pants", pants, None if pants != hoodie else hoodie_shadow, rim)
        m_s = toon(name + "_skin", skin, "#0c0f1d", rim, rim_w=0.55)
        black = ink()
        old = human.bone_defs
        human.bone_defs = bone_defs
        try:
            arm, B = make_armature(name)
        finally:
            human.bone_defs = old
        self.root = arm; self.B = B
        arm.scale = (scale,) * 3
        V, E = skeleton()
        body = build_body(name, arm, B, V, E, [m_h, m_s, m_p, m_s])
        outline(body, black, 0.007)
        self.body = body
        self.mats = dict(shirt=m_h, skin=m_s, pants=m_p)
        parts = []
        head = lib.sphere(name + "_head", HEAD_R, m_s, None, HEAD_C, (1.0, 0.95, 1.0))
        skin_to(head, arm, "head"); outline(head, black, 0.007, slot=1); parts.append(head)
        white = flat("stick_white", "#f4f1ea", 1.0)
        navy = flat("stick_navy", "#151a2e", 1.0)
        fy = HEAD_C[1] - HEAD_R * 0.93
        for s, sx in (("A", 1), ("B", -1)):
            e = lib.sphere(f"{name}_eye{s}", .036, white, None, (.072 * sx, fy + .006, HEAD_C[2] + .015), (1.0, .35, 1.0))
            parts.append(skin_to(e, arm, "eye" + s))
            p = lib.sphere(f"{name}_pup{s}", .017, navy, None, (.072 * sx, fy - .008, HEAD_C[2] + .012), (1.0, .4, 1.0))
            parts.append(skin_to(p, arm, "pup" + s))
            # pálpebra (cor da cabeça) presa à sobrancelha: desce = olhar bravo/cansado
            lid = lib.box(f"{name}_lid{s}", (.1, .03, .05), navy, None, (.072 * sx, fy - .004, HEAD_C[2] + .075), .01, True)
            parts.append(skin_to(lid, arm, "brow" + s))
        mo = arc(name + "_mouth", .05, 110, .007, white)
        mo.location = (0, fy - .004, HEAD_C[2] - .085)
        parts.append(skin_to(mo, arm, "mouth"))
        if hood:
            h = ring(name + "_hood", .085, .075, 1.53, .035, m_h)
            h.location = (0, .03, 0)
            parts.append(skin_to(h, arm, "chest"))
        pk = lib.box(name + "_pocket", (.15, .02, .085), toon(name + "_pocket", hoodie_shadow, hoodie_shadow, rim), None, (0, -.093, 1.04), .015, True)
        parts.append(skin_to(pk, arm, "spine"))
        if strings:
            for sx in (1, -1):
                c = lib.capsule(f"{name}_str{sx}", .005, .09, white, None, (.03 * sx, -.088, 1.4))
                parts.append(skin_to(c, arm, "chest"))
        self.parts = parts
        self.mustache = None
        self.pose(1, {}, "CONSTANT")
