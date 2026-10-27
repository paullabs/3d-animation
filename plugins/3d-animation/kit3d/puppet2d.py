"""Boneco 2D recortado (estilo IfverseTales) montado dentro do Blender.
Tudo é forma plana no plano XZ (desenho), com cor chapada, contorno escuro e borda de luz deslocada.
O boneco fica sempre de frente para a câmera; a câmera só desliza (nunca gira), então ele nunca
"vira papel": é sempre um desenho, e o fundo ganha parallax de verdade.
Convenções: X direita, Z cima, profundidade em Y (câmera em -Y olhando +Y). Ângulos em graus,
positivo = para frente (para onde o boneco olha)."""
import bpy, bmesh, math
from mathutils import Vector
import lib
from lib import srgb, key, empty

LAYER = 0.004          # distância entre camadas do boneco (em Y)
OUT = 0.009            # espessura do contorno
RIM = (0.010, 0.008)   # deslocamento da borda de luz (x, z)


def flatmat(name, color, strength=1.0):
    if name in bpy.data.materials:
        return bpy.data.materials[name]
    m = bpy.data.materials.new(name); m.use_nodes = True
    N = m.node_tree.nodes; N.clear()
    out = N.new("ShaderNodeOutputMaterial"); em = N.new("ShaderNodeEmission")
    em.inputs[0].default_value = (*srgb(color), 1); em.inputs[1].default_value = strength
    m.node_tree.links.new(em.outputs[0], out.inputs[0])
    return m


def set_color(m, color):
    for n in m.node_tree.nodes:
        if n.type == "EMISSION":
            n.inputs[0].default_value = (*srgb(color), 1)


# ---------------------------------------------------------------- formas 2D (lista de pontos x,z)
def circle(cx, cz, r, n=56, rz=None):
    rz = rz if rz is not None else r
    return [(cx + r * math.cos(2 * math.pi * i / n), cz + rz * math.sin(2 * math.pi * i / n)) for i in range(n)]


def capsule(x0, z0, x1, z1, r, n=14):
    a = math.atan2(z1 - z0, x1 - x0)
    pts = []
    for i in range(n + 1):
        t = a - math.pi / 2 + math.pi * i / n
        pts.append((x1 + r * math.cos(t), z1 + r * math.sin(t)))
    for i in range(n + 1):
        t = a + math.pi / 2 + math.pi * i / n
        pts.append((x0 + r * math.cos(t), z0 + r * math.sin(t)))
    return pts


def smooth(ctrl, k=10):
    """spline fechada (Catmull-Rom) passando pelos pontos de controle"""
    out = []; n = len(ctrl)
    for i in range(n):
        p0, p1, p2, p3 = [Vector(ctrl[(i + j - 1) % n]) for j in range(4)]
        for s in range(k):
            t = s / k; t2, t3 = t * t, t * t * t
            p = 0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2 + (-p0 + 3 * p1 - 3 * p2 + p3) * t3)
            out.append((p.x, p.y))
    return out


def area(pts):
    return 0.5 * sum(pts[i][0] * pts[(i + 1) % len(pts)][1] - pts[(i + 1) % len(pts)][0] * pts[i][1] for i in range(len(pts)))


def offset(pts, d):
    """engorda o contorno em d (polígono anti-horário)"""
    if area(pts) < 0:
        pts = pts[::-1]
    n = len(pts); out = []
    for i in range(n):
        a, b, c = Vector(pts[i - 1]), Vector(pts[i]), Vector(pts[(i + 1) % n])
        e1, e2 = (b - a), (c - b)
        if e1.length < 1e-9 or e2.length < 1e-9:
            out.append(tuple(b)); continue
        n1 = Vector((e1.y, -e1.x)).normalized(); n2 = Vector((e2.y, -e2.x)).normalized()
        m = (n1 + n2)
        if m.length < 1e-6:
            m = n1
        m.normalize()
        cosh = max(m.dot(n1), 0.35)
        p = b + m * (d / cosh)
        out.append((p.x, p.y))
    return out


def stroke(path, r, n_cap=10):
    """traço aberto com pontas redondas (boca, cordão)"""
    left, right = [], []
    for i, (x, z) in enumerate(path):
        a = Vector(path[max(i - 1, 0)]); b = Vector(path[min(i + 1, len(path) - 1)])
        t = (b - a).normalized(); nrm = Vector((-t.y, t.x))
        left.append((x + nrm.x * r, z + nrm.y * r)); right.append((x - nrm.x * r, z - nrm.y * r))
    pts = left[:]
    ex, ez = path[-1]; a0 = math.atan2(left[-1][1] - ez, left[-1][0] - ex)
    for k in range(1, n_cap):
        t = a0 - math.pi * k / n_cap
        pts.append((ex + r * math.cos(t), ez + r * math.sin(t)))
    pts += right[::-1]
    sx, sz = path[0]; a1 = math.atan2(right[0][1] - sz, right[0][0] - sx)
    for k in range(1, n_cap):
        t = a1 - math.pi * k / n_cap
        pts.append((sx + r * math.cos(t), sz + r * math.sin(t)))
    return pts


def mesh2d(name, pts, m, parent, y):
    bm = bmesh.new()
    vs = [bm.verts.new((x, y, z)) for x, z in pts]
    try:
        bm.faces.new(vs)
    except ValueError:
        pass
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    me.materials.append(m)
    o = bpy.data.objects.new(name, me); bpy.context.scene.collection.objects.link(o)
    o.parent = parent
    return o


# ---------------------------------------------------------------- boneco
class Puppet:
    """boneco de moletom (vista 3/4 olhando para a direita; espelhe com face=-1)"""

    def __init__(self, name, hoodie="#d8432f", hoodie_dark="#a52c20", skin="#0d1020", white="#f3efe6",
                 rim="#ffb070", scale=1.0, depth=0.0):
        self.name = name
        self.m = dict(
            hood=flatmat(name + "_hood", hoodie), dark=flatmat(name + "_dark", hoodie_dark),
            skin=flatmat(name + "_skin", skin), ink=flatmat(name + "_ink", skin),
            white=flatmat(name + "_white", white), rim=flatmat(name + "_rim", rim),
        )
        R = self.root = empty(name, None, (0, depth, 0)); R.scale = (scale,) * 3
        J = self.j = {}
        def joint(n, parent, loc):
            J[n] = empty(f"{name}_{n}", parent, loc); J[n].rotation_mode = "XYZ"; return J[n]
        hips = joint("hips", R, (0, 0, 0.86))
        torso = joint("torso", hips, (0, 0, 0))
        joint("shF", torso, (0.035, 0, 0.45)); joint("shB", torso, (-0.045, 0, 0.45))
        joint("elF", J["shF"], (0, 0, -0.3)); joint("elB", J["shB"], (0, 0, -0.3))
        joint("neck", torso, (0.01, 0, 0.5)); joint("head", J["neck"], (0, 0, 0.05))
        joint("hipF", hips, (0.03, 0, 0)); joint("hipB", hips, (-0.03, 0, 0))
        joint("knF", J["hipF"], (0, 0, -0.4)); joint("knB", J["hipB"], (0, 0, -0.4))
        joint("anF", J["knF"], (0, 0, -0.4)); joint("anB", J["knB"], (0, 0, -0.4))
        hc = joint("face", J["head"], (0, 0, 0.215))           # centro da cabeça (rosto desliza aqui)
        self.parts = []
        P = self._part
        # pernas (traço fino escuro) e pés
        for s, lay in (("B", 1.0), ("F", 2.0)):
            P(f"thigh{s}", capsule(0, 0, 0, -0.4, 0.026), "skin", J["hip" + s], lay)
            P(f"shin{s}", capsule(0, 0, 0, -0.4, 0.026), "skin", J["kn" + s], lay + 0.1)
            P(f"foot{s}", capsule(-0.01, -0.01, 0.12, -0.03, 0.036), "skin", J["an" + s], lay + 0.2)
        # braço de trás (atrás do corpo)
        self._arm("B", 3.0)
        # capuz caído (atrás da cabeça), pescoço
        P("hoodback", smooth([(-0.17, 0.40), (-0.05, 0.38), (0.06, 0.45), (0.0, 0.58), (-0.16, 0.6), (-0.21, 0.5)], 8), "dark", torso, 4.0)
        P("neck", capsule(0, 0, 0, 0.12, 0.022), "skin", J["neck"], 4.2, rim=False)
        # tronco do moletom (barra mais larga, ombro arredondado, leve barriga para frente)
        body = smooth([(-0.15, -0.17), (0.0, -0.19), (0.16, -0.17), (0.165, 0.08), (0.15, 0.32), (0.11, 0.47),
                       (0.02, 0.52), (-0.1, 0.5), (-0.145, 0.4), (-0.155, 0.12)], 10)
        P("body", body, "hood", torso, 5.0)
        P("pocket", smooth([(-0.02, -0.1), (0.14, -0.1), (0.14, 0.0), (0.07, 0.03), (-0.02, 0.0)], 6), "dark", torso, 5.3, outline=False, rim=False)
        for k, dx in enumerate((0.06, 0.1)):
            P(f"string{k}", stroke([(dx, 0.42), (dx + 0.004, 0.32)], 0.006), "white", torso, 5.4, outline=False, rim=False)
        # cabeça + rosto
        P("head", circle(0, 0, 0.225), "skin", hc, 7.0)
        fc = self.fc = empty(f"{name}_facegrp", hc, (0, 0, 0))
        self.eyes, self.lids, self.pups, self.eyeobjs = {}, {}, {}, {}
        for s_, ex in (("B", 0.03), ("F", 0.115)):
            ej = empty(f"{name}_eye{s_}", fc, (ex, 0, 0.01))
            self.eyes[s_] = ej
            objs = {}
            objs["open"] = mesh2d(f"{name}_eyew{s_}", circle(0, 0, 0.034, 32, 0.044), self.m["white"], ej, -8.0 * LAYER)
            arcp = [(-0.03 + 0.06 * i / 10, 0.026 * (1 - ((i / 10) * 2 - 1) ** 2) - 0.008) for i in range(11)]
            objs["happy"] = mesh2d(f"{name}_eyeh{s_}", stroke(arcp, 0.011), self.m["white"], ej, -8.0 * LAYER)
            objs["closed"] = mesh2d(f"{name}_eyec{s_}", stroke([(-0.03, -0.005), (0.03, -0.005)], 0.007), self.m["white"], ej, -8.0 * LAYER)
            self.eyeobjs[s_] = objs
            pj = empty(f"{name}_pup{s_}", ej, (0, 0, 0)); self.pups[s_] = pj
            mesh2d(f"{name}_pupm{s_}", circle(0, 0, 0.014, 20), self.m["skin"], pj, -8.3 * LAYER)
            lj = empty(f"{name}_lid{s_}", ej, (0, 0, 0)); self.lids[s_] = lj
            mesh2d(f"{name}_lidm{s_}", [(-0.046, 0.0), (0.046, 0.0), (0.046, 0.05), (-0.046, 0.05)], self.m["skin"], lj, -8.6 * LAYER)
        mj = self.mouth = empty(f"{name}_mouthj", fc, (0.08, 0, -0.085))
        self.mouth_objs = {}
        for kind, crv in (("smile", 1), ("flat", 0), ("frown", -1)):
            path = [(-0.035 + 0.07 * i / 12, -crv * 0.022 * (1 - ((i / 12) * 2 - 1) ** 2)) for i in range(13)]
            path = [(x, z + crv * 0.011) for x, z in path]
            o = mesh2d(f"{name}_mouth_{kind}", stroke(path, 0.0075), self.m["white"], mj, -8.8 * LAYER)
            self.mouth_objs[kind] = o
        o = mesh2d(f"{name}_mouth_o", circle(0, 0, 0.018, 24, 0.024), self.m["white"], mj, -8.8 * LAYER)
        self.mouth_objs["o"] = o
        # braço da frente (na frente de tudo)
        self._arm("F", 10.0)
        self.pose(1, {}, "CONSTANT")

    def _arm(self, s, lay):
        J = self.j; P = self._part
        P("upper" + s, capsule(0, 0, 0, -0.3, 0.043), "hood", J["sh" + s], lay)
        P("fore" + s, capsule(0, 0, 0, -0.29, 0.04), "hood", J["el" + s], lay)
        P("hand" + s, circle(0.004, -0.325, 0.046, 32, 0.052), "skin", J["el" + s], lay + 0.3)

    def _part(self, name, pts, mk, parent, lay, outline=True, rim=True):
        y = -lay * LAYER
        o = mesh2d(f"{self.name}_{name}", pts, self.m[mk], parent, y)
        if outline:
            mesh2d(f"{self.name}_{name}_o", offset(pts, OUT), self.m["ink"], parent, y + 0.3 * LAYER)
        if rim:
            rp = [(x + RIM[0], z + RIM[1]) for x, z in offset(pts, OUT * 0.8)]
            mesh2d(f"{self.name}_{name}_r", rp, self.m["rim"], parent, y + 0.6 * LAYER)
        self.parts.append(o)
        return o

    # ---------------------------------------------------------------- pose
    NEUTRAL = dict(x=0.0, z=0.0, face=1, bob=0.0, lean=0, head=0, armF=4, foreF=-8, armB=-4, foreB=-6,
                   legF=0, shinF=0, legB=0, shinB=0, footF=0, footB=0,
                   eye="open", eyes=1.0, lidopen=1.0, lid=0.0, pupils=False, look=(0.0, 0.0), mouth="flat", turn=1.0)

    def pose(self, frame, p, interp="BEZIER"):
        P = dict(self.NEUTRAL); P.update(p)
        J = self.j; r = self.root
        r.location.x = P["x"]; r.location.z = P["z"]
        r.scale.x = abs(r.scale.x) * (1 if P["face"] >= 0 else -1)
        key(r, "location", frame, interp); key(r, "scale", frame, "CONSTANT")
        J["hips"].location.z = 0.86 + P["bob"]; key(J["hips"], "location", frame, interp)
        def rot(n, a):
            J[n].rotation_euler = (0, -math.radians(a), 0); key(J[n], "rotation_euler", frame, interp)
        rot("torso", P["lean"]); rot("head", P["head"])
        for s in "FB":
            rot("sh" + s, P["arm" + s]); rot("el" + s, P["fore" + s])
            rot("hip" + s, P["leg" + s]); rot("kn" + s, P["shin" + s]); rot("an" + s, P["foot" + s])
        # rosto: turn 1 = 3/4 olhando para frente do corpo, 0 = de frente para a câmera
        self.fc.location.x = -0.0725 * (1 - P["turn"])
        key(self.fc, "location", frame, interp)
        for s_ in "FB":
            ej = self.eyes[s_]
            ej.scale = (1, 1, max(P["eyes"], 0.05)); key(ej, "scale", frame, interp)
            for kind, o in self.eyeobjs[s_].items():
                o.hide_render = kind != P["eye"]; o.keyframe_insert("hide_render", frame=frame)
            lj = self.lids[s_]
            lj.location.z = 0.044 * (2 * P["lidopen"] - 1)
            lj.scale = (1, 1, 1.0 if (P["lidopen"] < 0.98 and P["eye"] == "open") else 0.0001)
            sgn = 1 if s_ == "F" else -1
            lj.rotation_euler = (0, math.radians(P["lid"]) * sgn, 0)
            key(lj, "location", frame, interp); key(lj, "rotation_euler", frame, interp); key(lj, "scale", frame, "CONSTANT")
            pj = self.pups[s_]; pj.location = (P["look"][0] * 0.014, 0, P["look"][1] * 0.014)
            pj.scale = (1, 1, 1) if (P["pupils"] and P["eye"] == "open") else (0.0001,) * 3
            key(pj, "location", frame, interp); key(pj, "scale", frame, "CONSTANT")
        for kind, o in self.mouth_objs.items():
            o.hide_render = kind != P["mouth"]
            o.keyframe_insert("hide_render", frame=frame)

    def walk(self, t0, t1, x0, x1, fps, step=0.45, face=1, extra=None):
        """caminhada 2D de perfil de t0 a t1 (segundos), de x0 a x1"""
        n = max(2, int(round((t1 - t0) / (step / 2))))
        for i in range(n + 1):
            u = i / n; t = t0 + (t1 - t0) * u
            ph = i % 4
            sw = (28, 0, -28, 0)[ph]
            d = dict(x=x0 + (x1 - x0) * u, face=face, lean=4,
                     legF=sw, legB=-sw, shinF=(-6, -35, -10, -5)[ph], shinB=(-10, -5, -6, -35)[ph],
                     armF=-sw * 0.8, armB=sw * 0.8, foreF=-18, foreB=-14,
                     bob=(0.0, 0.025, 0.0, 0.025)[ph], footF=(10, 0, -12, 0)[ph], footB=(-12, 0, 10, 0)[ph])
            if extra:
                d.update(extra)
            self.pose(1 + round(t * fps), d, "BEZIER")
