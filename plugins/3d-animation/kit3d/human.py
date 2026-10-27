"""Humano de malha contínua (Skin modifier) + esqueleto + pesos calculados + roupa por região + rosto.
Mesmo vocabulário de pose do kit antigo (lib_v1.Person.pose). Roda dentro do Blender.
Eixos: Z para cima, personagem olha para -Y, lado A = +X, lado B = -X, metros."""
import bpy, bmesh, math
from mathutils import Vector
import lib
from lib import D2R, srgb, mat, link, key, _fcs, text, font

SCALE_ID = lambda s: (s, s, s)
HS = 1.3                                  # tamanho da cabeça (1.0 = realista)
HC = (0.0, 0.0, 1.64)                     # topo do pescoço = centro da escala da cabeça
def HP(p):
    return tuple(HC[i] + (p[i] - HC[i]) * HS for i in range(3))


def _sc():
    return bpy.context.scene


def seg_dist(p, a, b):
    ab = b - a
    t = max(0.0, min(1.0, (p - a).dot(ab) / max(ab.length_squared, 1e-9)))
    return (p - (a + ab * t)).length, t


# ---------------------------------------------------------------- esqueleto
def skeleton(belly=1.0, build=1.0):
    """vértices da malha 'skin': nome -> (pos, rx, ry).  build>1 = mais largo."""
    V = {}
    def v(n, p, rx, ry=None):
        V[n] = (Vector(p), rx, ry if ry is not None else rx)
    b, w = belly, build
    v("pelvis", (0, 0, .96), .158 * w * b ** .5, .118 * b)
    v("waist",  (0, 0, 1.12), .138 * w * b, .104 * b)
    v("chest",  (0, 0, 1.33), .178 * w, .124)
    v("neck",   (0, 0, 1.53), .056)
    v("neck2",  (0, 0, 1.63), .05)
    for s, sx in (("A", 1), ("B", -1)):
        v("sh" + s,   (.27 * sx, 0, 1.40), .066)
        v("el" + s,   (.29 * sx, 0, 1.09), .05)
        v("wr" + s,   (.30 * sx, 0, .85), .038)
        v("palm" + s, (.30 * sx, 0, .78), .043, .043)
        for fi, fy in enumerate((-.03, -.01, .01, .03)):
            ln = (.082, .09, .086, .072)[fi]
            v(f"f{fi}" + s, (.30 * sx, fy, .775 - ln), .0105)
        v("thumb" + s, (.298 * sx, -.055, .73), .014)
        v("hip" + s,  (.095 * sx, 0, .94), .094)
        v("kn" + s,   (.098 * sx, 0, .50), .066)
        v("an" + s,   (.1 * sx, 0, .11), .05)
        v("heel" + s, (.1 * sx, -.015, .055), .055)
        v("toe" + s,  (.1 * sx, -.19, .045), .056, .045)
    E = [("pelvis", "waist", "pelvis"), ("waist", "chest", "spine"), ("chest", "neck", "chest"),
         ("neck", "neck2", "neck")]
    for s in "AB":
        E += [("chest", "sh" + s, "clav" + s), ("sh" + s, "el" + s, "upper" + s), ("el" + s, "wr" + s, "fore" + s),
              ("wr" + s, "palm" + s, "hand" + s), ("palm" + s, "f0" + s, "hand" + s), ("palm" + s, "f1" + s, "hand" + s),
              ("palm" + s, "f2" + s, "hand" + s), ("palm" + s, "f3" + s, "hand" + s), ("palm" + s, "thumb" + s, "hand" + s),
              ("pelvis", "hip" + s, "pelvis"), ("hip" + s, "kn" + s, "thigh" + s), ("kn" + s, "an" + s, "shin" + s),
              ("an" + s, "heel" + s, "foot" + s), ("heel" + s, "toe" + s, "foot" + s)]
    return V, E


# osso: (head, tail, parent, roll)   roll: vetor mundial para onde aponta o eixo Z local
UP = (0, -1, 0)      # ossos que sobem  -> X local = +X mundo
DOWN = (0, 1, 0)     # ossos que descem -> X local = +X mundo
def bone_defs():
    B = {
        "pelvis": ((0, 0, .95), (0, 0, 1.13), None, UP),
        "spine":  ((0, 0, 1.13), (0, 0, 1.33), "pelvis", UP),
        "chest":  ((0, 0, 1.33), (0, 0, 1.50), "spine", UP),
        "neck":   ((0, 0, 1.50), (0, 0, 1.64), "chest", UP),
        "head":   ((0, 0, 1.64), HP((0, 0, 1.90)), "neck", UP),
    }
    for s, sx in (("A", 1), ("B", -1)):
        B["upper" + s] = ((.27 * sx, 0, 1.40), (.29 * sx, 0, 1.09), "chest", DOWN)
        B["fore" + s] = ((.29 * sx, 0, 1.09), (.30 * sx, 0, .85), "upper" + s, DOWN)
        B["hand" + s] = ((.30 * sx, 0, .85), (.30 * sx, 0, .69), "fore" + s, DOWN)
        B["thigh" + s] = ((.095 * sx, 0, .94), (.098 * sx, 0, .50), "pelvis", DOWN)
        B["shin" + s] = ((.098 * sx, 0, .50), (.1 * sx, 0, .11), "thigh" + s, DOWN)
        B["foot" + s] = ((.1 * sx, 0, .11), (.1 * sx, -.19, .045), "shin" + s, (0, 0, 1))
        # rosto: ossos curtos que sobem, filhos da cabeça
        B["brow" + s] = (HP((.07 * sx, -.15, 1.862)), HP((.07 * sx, -.15, 1.89)), "head", UP)
        B["eye" + s] = (HP((.07 * sx, -.14, 1.765)), HP((.07 * sx, -.14, 1.795)), "head", UP)
        B["pup" + s] = (HP((.07 * sx, -.16, 1.765)), HP((.07 * sx, -.16, 1.795)), "head", UP)
        B["must" + s] = (HP((.015 * sx, -.16, 1.69)), HP((.015 * sx, -.16, 1.72)), "head", UP)
    B["mouth"] = (HP((0, -.15, 1.625)), HP((0, -.15, 1.655)), "head", UP)
    return B


CHAINS = {
    "torso": ["pelvis", "spine", "chest", "neck", "head"],
    "armA": ["chest", "upperA", "foreA", "handA"], "armB": ["chest", "upperB", "foreB", "handB"],
    "legA": ["pelvis", "thighA", "shinA", "footA"], "legB": ["pelvis", "thighB", "shinB", "footB"],
}
def chain_of(label):
    if label in ("pelvis", "spine", "chest", "neck", "head"):
        return "torso"
    return ("arm" if label.rstrip("AB")[-1:] != "" and label.rstrip("AB") in ("clav", "upper", "fore", "hand") else "leg") + label[-1]


def make_armature(name):
    sc = _sc()
    arm = bpy.data.armatures.new(name)
    ob = bpy.data.objects.new(name, arm); sc.collection.objects.link(ob)
    bpy.context.view_layer.objects.active = ob
    for o in bpy.context.view_layer.objects:
        o.select_set(False)
    ob.select_set(True)
    bpy.ops.object.mode_set(mode="EDIT")
    B = bone_defs()
    for n, (h, t, par, roll) in B.items():
        eb = arm.edit_bones.new(n)
        eb.head = Vector(h); eb.tail = Vector(t)
        eb.align_roll(Vector(roll))
        if par:
            eb.parent = arm.edit_bones[par]
    bpy.ops.object.mode_set(mode="OBJECT")
    for pb in ob.pose.bones:
        pb.rotation_mode = "XYZ"
    ob.show_in_front = False
    ob.hide_render = False
    return ob, B


# ---------------------------------------------------------------- corpo
def build_body(name, arm_ob, B, V, E, mats):
    sc = _sc()
    names = list(V)
    me = bpy.data.meshes.new(name + "_skel")
    me.from_pydata([V[n][0] for n in names], [(names.index(a), names.index(b)) for a, b, _ in E], [])
    tmp = bpy.data.objects.new(name + "_tmp", me); sc.collection.objects.link(tmp)
    bpy.context.view_layer.objects.active = tmp
    sk = tmp.modifiers.new("skin", "SKIN"); sk.use_smooth_shade = True
    layer = me.skin_vertices[0]
    for i, n in enumerate(names):
        layer.data[i].radius = (V[n][1], V[n][2])
    layer.data[0].use_root = True
    sub = tmp.modifiers.new("sub", "SUBSURF"); sub.levels = 2; sub.render_levels = 2
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    me2 = bpy.data.meshes.new_from_object(tmp.evaluated_get(dg))
    me2.name = name + "_body"
    bpy.data.objects.remove(tmp); bpy.data.meshes.remove(me)

    segs = [(V[a][0], V[b][0], lab, V[a][1], V[b][1]) for a, b, lab in E]
    bseg = {n: (Vector(h), Vector(t)) for n, (h, t, _, _) in B.items()}
    ob = bpy.data.objects.new(name + "_body", me2); sc.collection.objects.link(ob)
    ob.parent = arm_ob

    vlabel = []
    wts = []
    for v in me2.vertices:
        p = v.co
        best, lab = 1e9, None
        for a, b, l, ra, rb in segs:
            d, t = seg_dist(p, a, b)
            r = ra + (rb - ra) * t
            sd = d / max(r, 1e-3)
            if sd < best:
                best, lab = sd, l
        vlabel.append(lab)
        chain = CHAINS[chain_of(lab)]
        ws = []
        for bn in chain:
            d, _ = seg_dist(p, *bseg[bn])
            ws.append((1.0 / (d + 0.012) ** 3.0, bn))
        ws.sort(reverse=True)
        ws = ws[:4]
        tot = sum(w for w, _ in ws)
        wts.append([(bn, w / tot) for w, bn in ws])
    groups = {}
    for i, ws in enumerate(wts):
        for bn, w in ws:
            groups.setdefault(bn, []).append((i, w))
    for bn in B:
        ob.vertex_groups.new(name=bn)
    for bn, lst in groups.items():
        vg = ob.vertex_groups[bn]
        for i, w in lst:
            vg.add([i], w, "REPLACE")
    # material por região (slots: 0 camisa, 1 pele, 2 calça, 3 sapato, 4 contorno)
    for m in mats:
        me2.materials.append(m)
    for poly in me2.polygons:
        c = poly.center
        l = vlabel[poly.vertices[0]]
        base = l.rstrip("AB")
        if base == "head" or base == "neck" or base == "hand":
            s = 1
        elif base == "foot":
            s = 3
        elif base in ("pelvis", "spine"):
            s = 2 if c.z < 1.05 else 0
        elif base in ("thigh", "shin"):
            s = 2
        else:
            s = 0
        poly.material_index = s
        poly.use_smooth = True
    mod = ob.modifiers.new("Armature", "ARMATURE"); mod.object = arm_ob
    return ob


def outline(ob, mat_black, thickness=0.011, slot=4):
    if len(ob.data.materials) <= slot:
        while len(ob.data.materials) < slot:
            ob.data.materials.append(ob.data.materials[0])
        ob.data.materials.append(mat_black)
    s = ob.modifiers.new("ink", "SOLIDIFY")
    s.thickness = thickness; s.offset = 1.0; s.use_flip_normals = True; s.material_offset = slot
    s.use_rim = False


# ---------------------------------------------------------------- acessórios presos a um osso
def skin_to(ob, arm_ob, bone):
    ob.parent = arm_ob
    vg = ob.vertex_groups.new(name=bone)
    vg.add(list(range(len(ob.data.vertices))), 1.0, "REPLACE")
    m = ob.modifiers.new("Armature", "ARMATURE"); m.object = arm_ob
    return ob


def ring(name, a, b, z, r, m, n=48, k=8):
    """toro elíptico (cinto/barra da camisa): semi-eixos a (x) e b (y), altura z, raio do tubo r"""
    bm = bmesh.new()
    rows = []
    for i in range(n):
        th = 2 * math.pi * i / n
        cx, cy = a * math.cos(th), b * math.sin(th)
        nx, ny = math.cos(th), math.sin(th)
        row = []
        for j in range(k):
            ph = 2 * math.pi * j / k
            row.append(bm.verts.new((cx + nx * r * math.cos(ph), cy + ny * r * math.cos(ph), z + r * math.sin(ph))))
        rows.append(row)
    for i in range(n):
        for j in range(k):
            bm.faces.new((rows[i][j], rows[(i + 1) % n][j], rows[(i + 1) % n][(j + 1) % k], rows[i][(j + 1) % k]))
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    for p in me.polygons:
        p.use_smooth = True
    me.materials.append(m)
    o = bpy.data.objects.new(name, me); _sc().collection.objects.link(o)
    return o


def head_mesh(name, r, m, center):
    """crânio oval com mandíbula: uma malha só (sem emenda)"""
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=40, v_segments=28, radius=r)
    for v in bm.verts:
        x, y, z = v.co
        k = max(0.0, -z / r)                    # 0 no meio, 1 no queixo
        v.co.x = x * 0.9 * (1 - 0.22 * k * k)
        v.co.y = y * (1 - 0.1 * k) - 0.012 * k * (1 if y < 0 else 0)
        v.co.z = z * (1.12 if z < 0 else 1.08)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    for p in me.polygons:
        p.use_smooth = True
    me.materials.append(m)
    o = bpy.data.objects.new(name, me); _sc().collection.objects.link(o)
    o.location = center
    return o


def _only(*objs):
    for o in bpy.context.view_layer.objects:
        o.select_set(False)
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]


def to_mesh_obj(txt_obj, name):
    me = bpy.data.meshes.new_from_object(txt_obj)
    o = bpy.data.objects.new(name, me)
    _sc().collection.objects.link(o)
    o.matrix_world = txt_obj.matrix_world.copy()
    bpy.data.objects.remove(txt_obj)
    return o


NEUTRAL = dict(
    loc=(0, 0, 0), rz=0, rx=0, pelvis_z=0.95, pelvis_rx=0,
    torso=(0, 0, 0), head=(0, 0, 0),
    armA=(0, 0, 6), armB=(0, 0, 6), foreA=0, foreB=0,
    legA=0, legB=0, shinA=0, shinB=0, legA_y=0, legB_y=0,
    brow=0, browup=0, mouth=(1.0, 1.0), eye=1.0, look=(0, 0),
)


class Person:
    def __init__(self, name, skin="#f1c7a0", shirt="#444444", pants="#2b2b33", shoes="#151515",
                 hair=None, hair_color="#2a1a10", eye_dist=1.0, scale=1.0, sunglasses=False,
                 tie=None, belly=1.0, build=1.0, ink=True, collar=None, face=True, belt=True, ink_w=0.011, gloss=None):
        sc = _sc()
        self.name = name
        self.base_scale = scale
        M = lambda k, c, r=0.5: mat(f"{name}_{k}", c, gloss if gloss is not None else r)
        m_shirt, m_skin, m_pants, m_shoe = M("shirt", shirt, .55), M("skin", skin, .5), M("pants", pants, .6), M("shoe", shoes, .35)
        self.mats = dict(shirt=m_shirt, skin=m_skin, pants=m_pants)
        black = mat("ink_black", (0, 0, 0), 1.0, emit=0.0)
        black.use_backface_culling = True
        arm, B = make_armature(name)
        self.root = arm; self.B = B
        arm.scale = SCALE_ID(scale)
        V, E = skeleton(belly, build)
        body = build_body(name, arm, B, V, E, [m_shirt, m_skin, m_pants, m_shoe])
        if ink:
            outline(body, black, ink_w)
        self.body = body
        skull = head_mesh(name + "_skull", .118 * HS, m_skin, HP((0, -.004, 1.735)))
        skin_to(skull, arm, "head")
        if ink:
            outline(skull, black, ink_w, slot=1)
        white = mat("eye_white", "#fbfbfb", 0.25); dark = mat("eye_black", "#0b0b0d", 0.2)
        hc = mat(name + "_hair", hair_color, 0.6)
        brow_m = mat(name + "_brow", hair_color if hair else "#2b2118", 0.7)
        S = lib.sphere; Bx = lib.box
        parts = []
        for s, sx in ((("A", 1), ("B", -1)) if face else ()):
            ex = .07 * eye_dist
            parts.append(skin_to(S(f"{name}_eye{s}", .037 * HS, white, None, HP((ex * sx, -.138, 1.765)), (1, .55, 1.2)), arm, "eye" + s))
            parts.append(skin_to(S(f"{name}_pup{s}", .021 * HS, dark, None, HP((ex * sx, -.158, 1.765)), (1, .45, 1.1)), arm, "pup" + s))
            parts.append(skin_to(Bx(f"{name}_brow{s}", (.075 * HS, .02 * HS, .022 * HS), brow_m, None, HP((ex * sx, -.153, 1.862)), .008, True), arm, "brow" + s))
            parts.append(skin_to(S(f"{name}_ear{s}", .038 * HS, m_skin, None, HP((.14 * sx, .01, 1.735)), (.45, .8, 1.0)), arm, "head"))
        if face:
          parts.append(skin_to(S(name + "_nose", .034 * HS, m_skin, None, HP((0, -.162, 1.71))), arm, "head"))
          parts.append(skin_to(S(name + "_mouth", .05 * HS, mat("mouth_dark", "#3a0d12", .4), None, HP((0, -.152, 1.627)), (1.1, .3, .22)), arm, "mouth"))
        if sunglasses:
            parts.append(skin_to(Bx(name + "_shades", (.27 * HS, .035 * HS, .06 * HS), dark, None, HP((0, -.16, 1.765)), .012, True), arm, "head"))
        if belt:
          belt = ring(name + "_belt", .178 * build * belly ** .5, .136 * belly, 1.05, .022, M("belt", "#0f0f12", .35))
          parts.append(skin_to(belt, arm, "spine"))
        if collar:
            parts.append(skin_to(ring(name + "_collar", .098, .092, 1.525, .032, M("collar", collar, .6)), arm, "chest"))
        if tie:
            tm = M("tie", tie, .4)
            parts.append(skin_to(S(name + "_knot", .028, tm, None, (0, -.158, 1.43), (1, .7, .9)), arm, "chest"))
            tb = Bx(name + "_tie", (.05, .014, .26), tm, None, (0, -.152, 1.27), .006, True)
            tb.rotation_euler = (-4 * D2R, 0, 0)
            parts.append(skin_to(tb, arm, "chest"))
        if hair == "cap":
            parts.append(skin_to(S(name + "_hair", .18 * HS, hc, None, HP((0, .04, 1.865)), (1.0, 1.0, .5)), arm, "head"))
        elif hair == "sides":
            for sx in (1, -1):
                parts.append(skin_to(S(name + f"_hs{sx}", .05 * HS, hc, None, HP((.125 * sx, .05, 1.76)), (.55, .9, 1.0)), arm, "head"))
        elif hair == "puff":
            parts.append(skin_to(S(name + "_hair", .185 * HS, hc, None, HP((0, .04, 1.875)), (1.0, 1.0, .62)), arm, "head"))
        self.parts = parts
        if ink and hair:
            for p in parts:
                if p.name.startswith(name + "_hair"):
                    p.data.materials.append(black)
                    s_ = p.modifiers.new("ink", "SOLIDIFY"); s_.thickness = .008; s_.offset = 1.0; s_.use_flip_normals = True; s_.material_offset = 1; s_.use_rim = False
        self.mustache = None
        self._chan = self._channels()
        self.pose(1, {}, "CONSTANT")

    # ---- bigode: duas metades, cada uma presa ao seu osso (pivô no centro do rosto)
    def add_mustache(self, color="#1a1208", s=1.5):
        m = mat(self.name + "_must", color, 0.8)
        for side, sx in (("A", 1), ("B", -1)):
            c = lib.capsule(f"{self.name}_must{side}", .026 * HS, .075 * HS, m, None, HP((.075 * sx, -.167, 1.69)))
            c.rotation_euler = (0, 90 * D2R + (-16 * D2R * sx), 0)
            t = lib.sphere(f"{self.name}_mtip{side}", .026 * HS, m, None, HP((.135 * sx, -.169, 1.709)))
            # junta a ponta na cápsula (mesma malha) para pivotar junto
            _only(c, t)
            bpy.ops.object.join()
            c.name = f"{self.name}_must{side}"
            skin_to(c, self.root, "must" + side)
        self.mustache = True
        self.must_scale(1, s * 0.0001 / s, "CONSTANT")
        self.must_s = s
        self.must_scale(1, 0.0001, "CONSTANT")

    def must_scale(self, frame, s, interp="BEZIER"):
        for sd in "AB":
            pb = self.root.pose.bones["must" + sd]
            pb.scale = (s, s, s)
            self._kb(pb, "scale", frame, interp)

    def must_peel(self, frame, deg, interp="BEZIER"):
        pb = self.root.pose.bones["mustA"]
        pb.rotation_euler = (0, 0, -deg * D2R)
        self._kb(pb, "rotation_euler", frame, interp)

    def add_badge(self, label, color="#ffffff", txt="#111111"):
        bm = lib.box(self.name + "_badge" + label, (.16, .012, .095), mat("badge_" + color + label, color, .4), None, (.09, -.168, 1.27), .004, False)
        t = text(self.name + "_bt" + label, label, .052, mat("badge_txt" + txt, txt, .4), None, (.09, -.178, 1.27), font())
        t.rotation_euler = (90 * D2R, 0, 0)
        bpy.context.view_layer.update()
        tm = to_mesh_obj(t, self.name + "_btm" + label)
        # junta texto + placa
        _only(bm, tm)
        bpy.ops.object.join()
        skin_to(bm, self.root, "chest")
        return bm

    # ---- pose
    def _channels(self):
        rot = ["spine", "chest", "head", "pelvis", "upperA", "upperB", "foreA", "foreB", "thighA", "thighB", "shinA", "shinB",
               "browA", "browB", "neck"]
        return rot

    def _kb(self, pb, path, frame, interp):
        pb.keyframe_insert(path, frame=frame)
        self._fix = getattr(self, "_fix", [])
        self._fix.append((f'pose.bones["{pb.name}"].{path}', frame, interp))

    def _flush(self):
        want = {}
        for dp, fr, ip in self._fix:
            want[(dp, fr)] = ip
        for fc in _fcs(self.root):
            for kp in fc.keyframe_points:
                ip = want.get((fc.data_path, round(kp.co.x)))
                if ip:
                    kp.interpolation = ip
        self._fix = []

    def pose(self, frame, p, interp="BEZIER"):
        P = dict(NEUTRAL); P.update(p)
        pb = self.root.pose.bones
        r = self.root
        r.location = P["loc"]; r.rotation_euler = (P["rx"] * D2R, 0, P["rz"] * D2R)
        key(r, "location", frame, interp); key(r, "rotation_euler", frame, interp)
        # tronco (eixo X mundo = X local; Y local = Z mundo; Z local = -Y mundo)
        up = lambda t: (t[0] * D2R, t[2] * D2R, -t[1] * D2R)
        pb["pelvis"].location = (0, P["pelvis_z"] - 0.95, 0)
        pb["pelvis"].rotation_euler = (P["pelvis_rx"] * D2R, 0, 0)
        tx, ty, tz = P["torso"]
        pb["spine"].rotation_euler = up((tx * .5, ty * .5, tz * .5))
        pb["chest"].rotation_euler = up((tx * .5, ty * .5, tz * .5))
        pb["neck"].rotation_euler = up([a * .35 for a in P["head"]])
        pb["head"].rotation_euler = up([a * .65 for a in P["head"]])
        for s, sx in (("A", 1), ("B", -1)):
            rx, tw, ab = P["arm" + s]
            pb["upper" + s].rotation_euler = (rx * D2R, tw * D2R * -1, -sx * ab * D2R)
            pb["fore" + s].rotation_euler = (P["fore" + s] * D2R, 0, 0)
            pb["thigh" + s].rotation_euler = (P["leg" + s] * D2R, 0, -sx * P["leg" + s + "_y"] * D2R)
            pb["shin" + s].rotation_euler = (P["shin" + s] * D2R, 0, 0)
            pb["brow" + s].rotation_euler = (0, 0, -sx * P["brow"] * D2R * -1)
            pb["brow" + s].location = (0, P["browup"] + max(P["eye"] - 1.0, 0) * 0.03, 0)
            pb["eye" + s].scale = (1, P["eye"], 1)
            pb["pup" + s].scale = (1, min(P["eye"], 1.0), 1)
            pb["pup" + s].location = (P["look"][0] * .02, P["look"][1] * .02, 0)
        pb["mouth"].scale = (P["mouth"][0], P["mouth"][1], 1)
        for n in ("pelvis", "spine", "chest", "neck", "head", "upperA", "upperB", "foreA", "foreB", "thighA", "thighB",
                  "shinA", "shinB", "browA", "browB"):
            self._kb(pb[n], "rotation_euler", frame, interp)
        self._kb(pb["pelvis"], "location", frame, interp)
        for s in "AB":
            self._kb(pb["brow" + s], "location", frame, interp)
            self._kb(pb["eye" + s], "scale", frame, interp)
            self._kb(pb["pup" + s], "scale", frame, interp)
            self._kb(pb["pup" + s], "location", frame, interp)
        self._kb(pb["mouth"], "scale", frame, interp)
        self._flush()

    def vis(self, frame, on):
        s = self.base_scale if on else 0.0001
        lib.setkey(self.root, "scale", (s, s, s), frame, "CONSTANT")
