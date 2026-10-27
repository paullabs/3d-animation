"""Kit 3D para histórias curtas. Roda dentro do Blender (blender -b -P ...).
Tudo é primitivas + juntas (empties) + keyframes; sem rig externo, sem assets.
Convenções: Z para cima, metros, personagem olha para -Y, lado A = +X, lado B = -X."""
import bpy, bmesh, math, random
from mathutils import Vector

D2R = math.pi / 180.0
scene = bpy.context.scene
_mats = {}


# ---------------------------------------------------------------- cena
def reset(w=1080, h=1920, fps=30, samples=24):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    global scene
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x, scene.render.resolution_y = w, h
    scene.render.resolution_percentage = 100
    scene.render.fps = fps
    scene.eevee.taa_render_samples = samples
    for attr, val in (("use_raytracing", True), ("use_shadows", True)):
        if hasattr(scene.eevee, attr):
            setattr(scene.eevee, attr, val)
    scene.view_settings.view_transform = "Standard"
    scene.view_settings.look = "None"
    scene.render.film_transparent = False
    w_ = bpy.data.worlds.new("W"); scene.world = w_
    w_.use_nodes = True
    bg = w_.node_tree.nodes["Background"]
    bg.inputs[0].default_value = (0.6, 0.65, 0.75, 1); bg.inputs[1].default_value = 0.35
    return scene


def srgb(hexstr):
    h = hexstr.lstrip("#")
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple((x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4) for x in c)


def mat(name, color, rough=0.55, emit=0.0):
    if name in _mats:
        return _mats[name]
    m = bpy.data.materials.new(name); m.use_nodes = True
    p = m.node_tree.nodes["Principled BSDF"]
    c = srgb(color) if isinstance(color, str) else color
    p.inputs["Base Color"].default_value = (*c, 1)
    p.inputs["Roughness"].default_value = rough
    if emit:
        p.inputs["Emission Color"].default_value = (*c, 1)
        p.inputs["Emission Strength"].default_value = emit
    _mats[name] = m
    return m


def link(o, parent=None, loc=(0, 0, 0)):
    scene.collection.objects.link(o)
    if parent is not None:
        o.parent = parent
    o.location = loc
    return o


def empty(name, parent=None, loc=(0, 0, 0)):
    return link(bpy.data.objects.new(name, None), parent, loc)


def _finish(name, bm, m, parent, loc, smooth=True, bevel=0):
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    if smooth:
        for p in me.polygons:
            p.use_smooth = True
    me.materials.append(m)
    o = link(bpy.data.objects.new(name, me), parent, loc)
    if bevel:
        b = o.modifiers.new("bev", "BEVEL"); b.width = bevel; b.segments = 3
    return o


def sphere(name, r, m, parent=None, loc=(0, 0, 0), scale=(1, 1, 1)):
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=24, v_segments=14, radius=r)
    for v in bm.verts:
        v.co.x *= scale[0]; v.co.y *= scale[1]; v.co.z *= scale[2]
    return _finish(name, bm, m, parent, loc)


def capsule(name, r, length, m, parent=None, loc=(0, 0, 0), scale=(1, 1, 1)):
    """cápsula vertical centrada na origem; length = trecho reto"""
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=20, v_segments=12, radius=r)
    for v in bm.verts:
        v.co.z += length / 2 if v.co.z > 1e-5 else -length / 2
        v.co.x *= scale[0]; v.co.y *= scale[1]
    return _finish(name, bm, m, parent, loc)


def box(name, size, m, parent=None, loc=(0, 0, 0), bevel=0.02, smooth=False):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co.x *= size[0]; v.co.y *= size[1]; v.co.z *= size[2]
    return _finish(name, bm, m, parent, loc, smooth=smooth, bevel=bevel)


def text(name, body, size, m, parent=None, loc=(0, 0, 0), font=None, extrude=0.0, outline=0.0):
    cu = bpy.data.curves.new(name, "FONT")
    cu.body = body; cu.size = size; cu.align_x = "CENTER"; cu.align_y = "CENTER"
    cu.extrude = extrude; cu.offset = outline
    if font:
        cu.font = font
    cu.materials.append(m)
    return link(bpy.data.objects.new(name, cu), parent, loc)


_font = None
def font():
    global _font
    if _font is None:
        _font = bpy.data.fonts.load("/System/Library/Fonts/Supplemental/Arial Black.ttf")
    return _font


# ---------------------------------------------------------------- animação
def _fcs(idb):
    ad = getattr(idb, "animation_data", None)
    if not ad or not ad.action:
        return
    a = ad.action
    for layer in a.layers:
        for strip in layer.strips:
            cb = strip.channelbag(ad.action_slot)
            if cb:
                yield from cb.fcurves


def key(o, path, frame, interp="BEZIER"):
    o.keyframe_insert(path, frame=frame)
    for fc in _fcs(o):
        if fc.data_path == path:
            for kp in fc.keyframe_points:
                if abs(kp.co.x - frame) < 1e-3:
                    kp.interpolation = interp


def all_interp(idb, interp="LINEAR"):
    for fc in _fcs(idb):
        for kp in fc.keyframe_points:
            kp.interpolation = interp


def setkey(o, path, value, frame, interp="BEZIER"):
    setattr(o, path, value)
    key(o, path, frame, interp)


def show(o, frame, on=True):
    """esconde/mostra um objeto-raiz (escala ~0 se escondido; filhos acompanham)"""
    s = 1.0 if on else 0.0001
    o.scale = (s, s, s) if not hasattr(o, "_s") else o.scale
    setkey(o, "scale", (s, s, s), frame, "CONSTANT")


def set_visible(root, frame, on, base=1.0):
    s = base if on else 0.0001
    setkey(root, "scale", (s, s, s), frame, "CONSTANT")


# ---------------------------------------------------------------- personagem
NEUTRAL = dict(
    loc=(0, 0, 0), rz=0, rx=0, pelvis_z=0.92, pelvis_rx=0,
    torso=(0, 0, 0), head=(0, 0, 0),
    armA=(0, 0, 8), armB=(0, 0, -8), foreA=0, foreB=0,
    legA=0, legB=0, shinA=0, shinB=0, legA_y=0, legB_y=0,
    brow=0, browup=0, mouth=(1.1, 0.25), eye=1.0, look=(0, 0),
)


class Person:
    def __init__(self, name, skin="#f1c7a0", shirt="#444444", pants="#2b2b33", shoes="#151515",
                 hair=None, hair_color="#2a1a10", eye_dist=1.0, scale=1.0, sunglasses=False,
                 tie=None, belly=1.0):
        self.name = name
        M = lambda k, c, r=0.55: mat(f"{name}_{k}", c, r)
        skin_m, shirt_m, pants_m = M("skin", skin, 0.5), M("shirt", shirt), M("pants", pants)
        self.mats = dict(shirt=shirt_m, skin=skin_m, pants=pants_m)
        root = self.root = empty(name)
        self.base_scale = scale
        root.scale = (scale,) * 3
        pel = self.pelvis = empty(name + "_pelvis", root, (0, 0, 0.92))
        sphere(name + "_hips", 0.2, pants_m, pel, (0, 0, 0.0), (1.1, 0.8, 0.75))
        tj = self.torso = empty(name + "_torso", pel, (0, 0, 0.06))
        capsule(name + "_chest", 0.23, 0.26, shirt_m, tj, (0, 0, 0.26), (1.0, 0.72 * belly, 1.0))
        if tie:
            box(name + "_tie", (0.06, 0.02, 0.3), M("tie", tie), tj, (0, -0.172 * belly, 0.3), bevel=0.008)
        # braços
        self.sh, self.el = {}, {}
        for s, sx in (("A", 1), ("B", -1)):
            sh = self.sh[s] = empty(f"{name}_sh{s}", tj, (0.31 * sx, 0, 0.46))
            sphere(name + "_ball" + s, 0.085, shirt_m, sh)
            capsule(name + "_arm" + s, 0.072, 0.2, shirt_m, sh, (0, 0, -0.17))
            el = self.el[s] = empty(f"{name}_el{s}", sh, (0, 0, -0.34))
            capsule(name + "_fore" + s, 0.064, 0.2, shirt_m, el, (0, 0, -0.15))
            sphere(name + "_hand" + s, 0.08, skin_m, el, (0, 0, -0.34))
        # pernas
        self.hp, self.kn = {}, {}
        for s, sx in (("A", 1), ("B", -1)):
            hp = self.hp[s] = empty(f"{name}_hp{s}", pel, (0.12 * sx, 0, -0.02))
            capsule(name + "_thigh" + s, 0.1, 0.22, pants_m, hp, (0, 0, -0.22))
            kn = self.kn[s] = empty(f"{name}_kn{s}", hp, (0, 0, -0.45))
            capsule(name + "_shin" + s, 0.085, 0.2, pants_m, kn, (0, 0, -0.2))
            box(name + "_shoe" + s, (0.15, 0.3, 0.1), M("shoe", shoes, 0.4), kn, (0, -0.06, -0.43), bevel=0.04, smooth=True)
        # cabeça
        nk = self.head = empty(name + "_head", tj, (0, 0, 0.6)); nk.scale = (1.22, 1.22, 1.22)
        sphere(name + "_skull", 0.27, skin_m, nk, (0, 0, 0.27), (1.0, 0.95, 1.05))
        sphere(name + "_nose", 0.05, skin_m, nk, (0, -0.265, 0.2))
        for s, sx in (("A", 1), ("B", -1)):
            sphere(name + "_ear" + s, 0.06, skin_m, nk, (0.265 * sx, 0.0, 0.27), (0.5, 0.8, 1))
        self.eyes, self.pup, self.brows = {}, {}, {}
        white = mat("eye_white", "#ffffff", 0.3); black = mat("eye_black", "#0a0a0a", 0.3)
        brow_m = mat(name + "_brow", hair_color if hair_color else "#222222")
        for s, sx in (("A", 1), ("B", -1)):
            ex = 0.105 * eye_dist
            self.eyes[s] = sphere(f"{name}_eye{s}", 0.07, white, nk, (ex * sx, -0.222, 0.3), (1, 0.6, 1.0))
            self.pup[s] = sphere(f"{name}_pup{s}", 0.036, black, nk, (ex * sx, -0.262, 0.3), (1, 0.4, 1))
            bj = self.brows[s] = empty(f"{name}_brow{s}", nk, (ex * sx, -0.245, 0.4))
            box(f"{name}_browbar{s}", (0.11, 0.025, 0.03), brow_m, bj, bevel=0.01, smooth=True)
        self.mouth = sphere(name + "_mouth", 0.07, mat("mouth_dark", "#3a0d12", 0.4), nk, (0, -0.255, 0.1), (1.1, 0.3, 0.25))
        if sunglasses:
            box(name + "_shades", (0.34, 0.04, 0.09), black, nk, (0, -0.268, 0.3), bevel=0.015, smooth=True)
        if hair:
            hm = M("hair", hair_color)
            if hair == "cap":
                sphere(name + "_hair", 0.285, hm, nk, (0, 0.03, 0.31), (1.0, 1.0, 0.72))
            elif hair == "sides":
                for sx in (1, -1):
                    sphere(name + f"_hairs{sx}", 0.1, hm, nk, (0.24 * sx, 0.05, 0.3), (0.6, 0.9, 1.0))
            elif hair == "puff":
                sphere(name + "_hair", 0.3, hm, nk, (0, 0.05, 0.35), (1.0, 1.0, 0.8))
        self.mustache = None
        self.rest = {}
        self.pose(1, {}, "CONSTANT")

    # -- bigode gigante (pivô nas pontas para "descolar")
    def add_mustache(self, color="#1a1208", s=1.7):
        m = mat(self.name + "_must", color, 0.8)
        g = self.mustache = empty(self.name + "_mustache", self.head, (0, -0.262, 0.15))
        g.scale = (s, s, s)
        self.must_halves = {}
        for side, sx in (("A", 1), ("B", -1)):
            piv = empty(f"{self.name}_mpiv{side}", g, (0.02 * sx, 0, 0))
            c = capsule(f"{self.name}_must{side}", 0.034, 0.11, m, piv, (0.075 * sx, -0.005, -0.004))
            c.rotation_euler = (0, 90 * D2R + (-14 * D2R * sx), 0)
            tip = sphere(f"{self.name}_mtip{side}", 0.034, m, piv, (0.165 * sx, -0.012, 0.018))
            self.must_halves[side] = piv
        return g

    def add_badge(self, label, color="#ffffff", txt="#111111"):
        b = box(self.name + "_badge" + label, (0.19, 0.012, 0.11), mat("badge_" + color + label, color, 0.4), self.torso, (0.1, -0.2, 0.34), bevel=0.006)
        t = text(self.name + "_badget" + label, label, 0.062, mat("badge_txt" + txt, txt, 0.4), b, (0, -0.009, 0), font())
        t.rotation_euler = (90 * D2R, 0, 0)
        return b

    # -- pose
    def pose(self, frame, p, interp="BEZIER"):
        P = dict(NEUTRAL); P.update(p)
        r = self.root
        r.location = P["loc"]; r.rotation_euler = (P["rx"] * D2R, 0, P["rz"] * D2R)
        self.pelvis.location = (0, 0, P["pelvis_z"]); self.pelvis.rotation_euler = (P["pelvis_rx"] * D2R, 0, 0)
        self.torso.rotation_euler = tuple(a * D2R for a in P["torso"])
        self.head.rotation_euler = tuple(a * D2R for a in P["head"])
        for s in "AB":
            self.sh[s].rotation_euler = tuple(a * D2R for a in P["arm" + s])
            self.el[s].rotation_euler = (P["fore" + s] * D2R, 0, 0)
            self.hp[s].rotation_euler = (P["leg" + s] * D2R, 0, P["leg" + s + "_y"] * D2R)
            self.kn[s].rotation_euler = (P["shin" + s] * D2R, 0, 0)
            sx = 1 if s == "A" else -1
            self.brows[s].rotation_euler = (0, sx * P["brow"] * D2R, 0)
            self.brows[s].location.z = 0.4 + P["browup"]
            self.eyes[s].scale = (1, 0.6, P["eye"])
            self.pup[s].scale = (1, 0.4, min(P["eye"], 1.0))
            ex = self.eyes[s].location.x
            self.pup[s].location = (ex + P["look"][0] * 0.03, -0.262, 0.3 + P["look"][1] * 0.03)
        self.mouth.scale = (P["mouth"][0], 0.3, P["mouth"][1])
        for o, ps in self._targets():
            for pth in ps:
                key(o, pth, frame, interp)

    def _targets(self):
        if hasattr(self, "_tg"):
            return self._tg
        t = [(self.root, ["location", "rotation_euler"]),
             (self.pelvis, ["location", "rotation_euler"]), (self.torso, ["rotation_euler"]),
             (self.head, ["rotation_euler"]), (self.mouth, ["scale"])]
        for s in "AB":
            t += [(self.sh[s], ["rotation_euler"]), (self.el[s], ["rotation_euler"]),
                  (self.hp[s], ["rotation_euler"]), (self.kn[s], ["rotation_euler"]),
                  (self.brows[s], ["rotation_euler", "location"]), (self.eyes[s], ["scale"]),
                  (self.pup[s], ["scale", "location"])]
        self._tg = t
        return t

    def vis(self, frame, on):
        s = self.base_scale if on else 0.0001
        setkey(self.root, "scale", (s, s, s), frame, "CONSTANT")


# ---------------------------------------------------------------- câmera
class Cam:
    def __init__(self):
        self.n = 0
        self.rigs = []

    def shot(self, f0, f1, p0, p1, t0, t1, lens=22, shake=0.0, interp="BEZIER", name=None, roll=0.0):
        self.n += 1
        cd = bpy.data.cameras.new(f"cam{self.n}")
        cd.sensor_fit = "HORIZONTAL"; cd.sensor_width = 24; cd.lens = lens
        cd.clip_start = 0.05; cd.clip_end = 200
        co = link(bpy.data.objects.new(name or f"cam{self.n}", cd))
        tg = empty(f"tgt{self.n}")
        c = co.constraints.new("TRACK_TO"); c.target = tg
        c.track_axis = "TRACK_NEGATIVE_Z"; c.up_axis = "UP_Y"
        setkey(co, "location", p0, f0, interp); setkey(co, "location", p1, f1, interp)
        setkey(tg, "location", t0, f0, interp); setkey(tg, "location", t1, f1, interp)
        if shake:
            rnd = random.Random(self.n)
            for f in range(f0 + 2, f1, 2):
                a = f1 - f0
                k = (f - f0) / a
                base = Vector(t0).lerp(Vector(t1), k)
                tg.location = base + Vector((rnd.uniform(-1, 1), 0, rnd.uniform(-1, 1))) * shake
                key(tg, "location", f, "LINEAR")
        m = scene.timeline_markers.new(f"S{self.n}", frame=f0)
        m.camera = co
        co.data.dof.use_dof = False
        return co


# ---------------------------------------------------------------- legenda
def captions(cam_obj, f0, f1, text_line, size=0.34, y=-1.05, dist=3.0, hi=None, lens=22):
    """quebra a fala em pedaços de 2-3 palavras e reparte o tempo pelo número de letras.
    A legenda é filha da câmera do plano e fica a 0,5 m dela (nenhum objeto da cena passa na frente)."""
    k = 0.5 / dist * 22.0 / lens; size, y, dist = size * k, y * k, 0.5
    words = text_line.split()
    chunks, cur = [], []
    for w in words:
        if cur and len(" ".join(cur + [w])) > 15:
            chunks.append(" ".join(cur)); cur = []
        cur.append(w)
        if len(cur) >= 3 or (len(" ".join(cur)) >= 12) or w.endswith((",", ".", "?", ":")):
            chunks.append(" ".join(cur)); cur = []
    if cur:
        if chunks and len(cur) == 1 and len(chunks[-1]) + len(cur[0]) < 15 and not chunks[-1].endswith((",", ".", "?", ":")):
            chunks[-1] += " " + cur[0]
        else:
            chunks.append(" ".join(cur))
    weights = [len(c) + 2 for c in chunks]
    tot = sum(weights)
    span = (f1 - f0) * 0.9
    t = f0
    white = mat("cap_w", (1, 1, 1), 1.0, emit=1.0)
    yellow = mat("cap_y", srgb("#ffd43b"), 1.0, emit=1.0)
    black = mat("cap_k", (0, 0, 0), 1.0)
    objs = []
    for c, wt in zip(chunks, weights):
        dur = span * wt / tot
        a, b = round(t), round(t + dur); t += dur
        is_hi = hi and any(h.lower() in c.lower() for h in hi)
        o = text("cap", c.upper(), size, yellow if is_hi else white, cam_obj, (0, y, -dist), font())
        sh = text("capk", c.upper(), size, black, o, (0.0, -size * 0.09, -0.003), font())
        sh.data.offset = size * 0.08
        o.scale = (0.0001,) * 3
        setkey(o, "scale", (0.0001,) * 3, max(f0 - 1, 1), "CONSTANT")
        setkey(o, "scale", (1, 1, 1), a, "CONSTANT")
        setkey(o, "scale", (0.0001,) * 3, b, "CONSTANT")
        objs.append(o)
    return objs


# ---------------------------------------------------------------- cenário
class Room:
    """caixa grande emissiva com degradê (topo/base) + piso. Cor keyada por plano."""
    def __init__(self):
        m = self.m = bpy.data.materials.new("room"); m.use_nodes = True
        nt = m.node_tree; nt.nodes.clear()
        out = nt.nodes.new("ShaderNodeOutputMaterial")
        em = nt.nodes.new("ShaderNodeEmission")
        mix = self.mix = nt.nodes.new("ShaderNodeMix"); mix.data_type = "RGBA"
        geo = nt.nodes.new("ShaderNodeNewGeometry")
        sep = nt.nodes.new("ShaderNodeSeparateXYZ")
        mr = nt.nodes.new("ShaderNodeMapRange")
        mr.inputs[1].default_value = 0.0; mr.inputs[2].default_value = 7.0
        nt.links.new(geo.outputs["Position"], sep.inputs[0])
        nt.links.new(sep.outputs["Z"], mr.inputs[0])
        nt.links.new(mr.outputs[0], mix.inputs[0])
        nt.links.new(mix.outputs[2], em.inputs[0])
        nt.links.new(em.outputs[0], out.inputs[0])
        bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0)
        for v in bm.verts:
            v.co.x *= 40; v.co.y *= 40; v.co.z *= 14; v.co.z += 6.9
        bmesh.ops.reverse_faces(bm, faces=bm.faces)
        me = bpy.data.meshes.new("roombox"); bm.to_mesh(me); bm.free(); me.materials.append(m)
        link(bpy.data.objects.new("room", me))
        fm = self.fm = bpy.data.materials.new("floor"); fm.use_nodes = True
        self.fp = fm.node_tree.nodes["Principled BSDF"]
        self.fp.inputs["Roughness"].default_value = 0.28
        self.fp.inputs["Specular IOR Level"].default_value = 0.9
        bm = bmesh.new(); bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=20)
        me = bpy.data.meshes.new("floor"); bm.to_mesh(me); bm.free(); me.materials.append(fm)
        link(bpy.data.objects.new("floor", me))

    def color(self, frame, top, bottom, floor=None):
        t, b = srgb(top), srgb(bottom)
        fl = srgb(floor) if floor else tuple(c * 1.6 + 0.004 for c in b)
        if getattr(self, "last", None) and frame > 1:
            self._k(frame - 1, *self.last)
        self._k(frame, t, b, fl)
        self.last = (t, b, fl)

    def _k(self, frame, t, b, fl):
        self.mix.inputs[6].default_value = (*b, 1)
        self.mix.inputs[7].default_value = (*t, 1)
        for i in (6, 7):
            self.mix.inputs[i].keyframe_insert("default_value", frame=frame)
        self.fp.inputs["Base Color"].default_value = (*fl, 1)
        self.fp.inputs["Base Color"].keyframe_insert("default_value", frame=frame)


def lights():
    def area(name, loc, energy, size, color=(1, 1, 1), tgt=(0, 0.6, 1.0)):
        ld = bpy.data.lights.new(name, "AREA"); ld.energy = energy; ld.size = size; ld.color = color
        o = link(bpy.data.objects.new(name, ld), None, loc)
        t = empty(name + "_t", None, tgt)
        c = o.constraints.new("TRACK_TO"); c.target = t; c.track_axis = "TRACK_NEGATIVE_Z"; c.up_axis = "UP_Y"
        return o
    area("key", (2.8, -4.0, 4.6), 420, 4.0, (1.0, 0.95, 0.88))
    area("fill", (-4, -3, 2.5), 160, 6.0, (0.8, 0.88, 1.0))
    area("rimB", (-1.5, 4.5, 3.6), 900, 3.0, (0.75, 0.88, 1.0), (0, 0.6, 1.3))
    area("rimC", (2.8, 3.8, 3.4), 700, 3.0, (1.0, 0.82, 0.7), (0, 0.6, 1.3))
    area("rimF", (0, -6, 3.0), 120, 6.0)
