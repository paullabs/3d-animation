"""Personagem 2D recortado, versão 2 (estilo IfverseTales).
- 4 vistas desenhadas: front (frente), q (3/4), side (perfil), back (costas). Cada vista é um boneco
  próprio; Character troca a vista visível (como um rig de recorte profissional).
- Pescoço visível, tronco em duas partes (cintura e peito), pulsos e tornozelos, mãos com polegar
  (descanso, punho, apontando, aberta, joinha), tênis com sola, moletom com barra, punhos, bolso e cordões.
- Rosto: olhos com formas por chave (sono, esperto, bravo, triste, apertado, sorriso, arregalado),
  bocas por chave (traço: reta, sorriso, triste, de lado, nervosa, pequena; cheia: o, grito, sorrisão,
  dentes, falando), pupilas, extras (suor, lágrima, vergonha, raiva, ! e ?).
- Rabisco vivo: olhos e boca tremem como traço feito à mão, trocando a 3 quadros por segundo.
Tudo é plano no XZ, de frente para a câmera; a câmera só desliza. Z cima, X direita, câmera em -Y."""
import bpy, bmesh, math, random
from mathutils import Vector
import lib
from lib import srgb, key, empty
from puppet2d import flatmat, circle, capsule, smooth, offset, stroke

LAYER = 0.004
OUT = 0.0085
RIM = (0.009, 0.007)
PAL = dict(hoodie="#d8432f", dark="#a52c20", band="#b9351f", skin="#0d1020", white="#f3efe6",
           sole="#ece6d8", rim="#ffb070", blush="#8a2a3a", sweat="#9ad8ff", anger="#ff5a45")


# ---------------------------------------------------------------- formas
def taper(x0, z0, r0, x1, z1, r1, n=12):
    """cápsula afinando de r0 (início) para r1 (fim)"""
    a = math.atan2(z1 - z0, x1 - x0); L = math.hypot(x1 - x0, z1 - z0)
    phi = math.asin(max(-0.95, min(0.95, (r0 - r1) / max(L, 1e-6))))
    h = math.pi / 2 - phi
    pts = []
    for i in range(n + 1):
        t = a - h + 2 * h * i / n
        pts.append((x1 + r1 * math.cos(t), z1 + r1 * math.sin(t)))
    for i in range(n + 1):
        t = a + h + (2 * math.pi - 2 * h) * i / n
        pts.append((x0 + r0 * math.cos(t), z0 + r0 * math.sin(t)))
    return pts


def rrect(x0, z0, x1, z1, r, n=6):
    r = min(r, (x1 - x0) / 2, (z1 - z0) / 2)
    pts = []
    for cx, cz, a0 in ((x1 - r, z0 + r, -90), (x1 - r, z1 - r, 0), (x0 + r, z1 - r, 90), (x0 + r, z0 + r, 180)):
        for i in range(n + 1):
            t = math.radians(a0 + 90 * i / n)
            pts.append((cx + r * math.cos(t), cz + r * math.sin(t)))
    return pts


def ellipse(cx, cz, rx, rz, n=48, a0=0.0):
    return [(cx + rx * math.cos(a0 + 2 * math.pi * i / n), cz + rz * math.sin(a0 + 2 * math.pi * i / n)) for i in range(n)]


def mirror(pts):
    return [(-x, z) for x, z in pts][::-1]


def mesh_multi(name, polys, m, parent, y):
    bm = bmesh.new()
    for pts in polys:
        vs = [bm.verts.new((x, y, z)) for x, z in pts]
        bm.faces.new(vs)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free(); me.materials.append(m)
    o = bpy.data.objects.new(name, me); bpy.context.scene.collection.objects.link(o)
    o.parent = parent
    return o


def mesh_pts(name, pts, m, parent, y, keys=None):
    bm = bmesh.new()
    vs = [bm.verts.new((x, y, z)) for x, z in pts]
    try:
        bm.faces.new(vs)
    except ValueError:
        pass
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free(); me.materials.append(m)
    o = bpy.data.objects.new(name, me); bpy.context.scene.collection.objects.link(o)
    o.parent = parent
    if keys:
        o.shape_key_add(name="Basis", from_mix=False)
        for kn, kp in keys.items():
            sk = o.shape_key_add(name=kn, from_mix=False)
            for i, (x, z) in enumerate(kp):
                sk.data[i].co = (x, y, z)
    return o


# ---------------------------------------------------------------- olhos e bocas (mesmo nº de pontos)
EYE_RX, EYE_RZ, EYE_N = 0.031, 0.041, 44


def eye_shape(top=None, bottom=None, scale=1.0, inner=-1):
    """elipse cortada por uma linha de pálpebra. top/bottom = (altura relativa, inclinação p/ dentro)"""
    pts = []
    for i in range(EYE_N):
        t = 2 * math.pi * i / EYE_N - math.pi / 2
        x = EYE_RX * scale * math.cos(t); z = EYE_RZ * scale * math.sin(t)
        if top is not None:
            h, s = top; zl = h * EYE_RZ + s * EYE_RZ * (x / EYE_RX) * (-inner)
            z = min(z, zl)
        if bottom is not None:
            h, s = bottom; zl = h * EYE_RZ + s * EYE_RZ * (x / EYE_RX) * (-inner)
            z = max(z, zl)
        pts.append((x, z))
    return pts


def eye_keys(inner):
    return {
        "sono":    eye_shape(top=(0.05, 0.0), inner=inner),
        "esperto": eye_shape(top=(0.1, 0.22), inner=inner),
        "bravo":   eye_shape(top=(0.3, 0.8), inner=inner),
        "triste":  eye_shape(top=(0.42, -0.6), inner=inner),
        "apertado": eye_shape(top=(0.28, 0.0), bottom=(-0.28, 0.0), inner=inner),
        "sorriso": eye_shape(bottom=(-0.15, 0.0), inner=inner),
        "arregalado": eye_shape(scale=1.28, inner=inner),
    }


MOUTH_W, MOUTH_N = 0.078, 15


def mouth_path(kind):
    pts = []
    for i in range(MOUTH_N):
        u = -1 + 2 * i / (MOUTH_N - 1); x = u * MOUTH_W / 2
        if kind == "reta":
            z = 0.0
        elif kind == "sorriso":
            z = 0.024 * u * u - 0.012
        elif kind == "triste":
            z = -0.022 * u * u + 0.011
        elif kind == "lado":
            z = 0.026 * ((u + 1) / 2) ** 2.2 - 0.008
        elif kind == "nervosa":
            z = 0.008 * math.sin(3 * math.pi * u)
        elif kind == "pequena":
            x *= 0.45; z = 0.0
        pts.append((x, z))
    return stroke(pts, 0.0075)


FILL_N = 48


def fill_shape(kind):
    if kind == "o":
        return ellipse(0, -0.004, 0.019, 0.025, FILL_N, -math.pi / 2)
    if kind == "grito":
        return ellipse(0, -0.02, 0.036, 0.052, FILL_N, -math.pi / 2)
    if kind == "falando":
        return ellipse(0, -0.006, 0.026, 0.014, FILL_N, -math.pi / 2)
    if kind == "sorrisao":
        top = 14; pts = []
        for i in range(top):
            pts.append((0.042 - 0.084 * i / (top - 1), 0.006))
        for i in range(FILL_N - top):
            t = math.pi + math.pi * (i + 1) / (FILL_N - top + 1)
            pts.append((0.042 * math.cos(t), 0.006 + 0.036 * math.sin(t)))
        return pts[::-1] if False else pts
    if kind == "dentes":
        rr = rrect(-0.04, -0.02, 0.04, 0.016, 0.012, 11)
        while len(rr) < FILL_N:
            rr.append(rr[-1])
        return rr[:FILL_N]
    return ellipse(0, 0, 0.001, 0.001, FILL_N)


def shrink(pts, d):
    cx = sum(p[0] for p in pts) / len(pts); cz = sum(p[1] for p in pts) / len(pts)
    return [(cx + (x - cx) * (1 - d), cz + (z - cz) * (1 - d)) for x, z in pts]


# ---------------------------------------------------------------- um boneco (uma vista)
VIEW = {
    #           ombroF        ombroB        quadrilF   quadrilB   pescoço x  rosto x  olhos (B, F)       boca x
    "front": dict(shF=(0.17, 0.235), shB=(-0.17, 0.235), hipF=0.075, hipB=-0.075, nx=0.0, fx=0.0, eyes=(-0.066, 0.066), mx=0.0),
    "q":     dict(shF=(0.05, 0.245), shB=(-0.075, 0.245), hipF=0.035, hipB=-0.04, nx=0.02, fx=0.0, eyes=(0.03, 0.112), mx=0.078),
    "side":  dict(shF=(0.005, 0.245), shB=(-0.015, 0.25), hipF=0.012, hipB=-0.012, nx=0.035, fx=0.0, eyes=(None, 0.135), mx=0.15),
    "back":  dict(shF=(0.17, 0.235), shB=(-0.17, 0.235), hipF=0.075, hipB=-0.075, nx=0.0, fx=0.0, eyes=(None, None), mx=None),
}


class Toon:
    def __init__(self, name, view="q", pal=None, mats=None):
        self.name = name; self.view = view
        pal = dict(PAL, **(pal or {}))
        self.pal = pal
        M = mats or {}
        def fm(k):
            if k not in M:
                M[k] = flatmat(f"{name}_{k}", pal[k] if k in pal else k)
            return M[k]
        self.fm = fm; self.M = M
        fm("hoodie"); fm("dark"); fm("band"); fm("skin"); fm("white"); fm("sole"); fm("rim")
        M["ink"] = M.get("ink") or flatmat(f"{name}_ink", pal["skin"])
        V = VIEW[view]
        R = self.root = empty(name)
        J = self.j = {}
        def joint(n, parent, loc):
            J[n] = empty(f"{name}_{n}", parent, loc); J[n].rotation_mode = "XYZ"; return J[n]
        hips = joint("hips", R, (0, 0, 0.86))
        torso = joint("torso", hips, (0, 0, 0))
        chest = joint("chest", torso, (0, 0, 0.2))
        joint("shF", chest, (V["shF"][0], 0, V["shF"][1])); joint("shB", chest, (V["shB"][0], 0, V["shB"][1]))
        for s in "FB":
            joint("el" + s, J["sh" + s], (0, 0, -0.29)); joint("wr" + s, J["el" + s], (0, 0, -0.27))
            joint("hip" + s, hips, (V["hip" + s], 0, 0)); joint("kn" + s, J["hip" + s], (0, 0, -0.41)); joint("an" + s, J["kn" + s], (0, 0, -0.375))
        joint("neck", chest, (V["nx"], 0, 0.26))
        joint("head", J["neck"], (0, 0, 0.1))
        fc = self.face = joint("face", J["head"], (V["fx"], 0, 0.2))     # centro da cabeça
        self.parts = []
        self.handsets = {"F": {}, "B": {}}
        self.boilers = []
        L = self._layers()
        # pernas e tênis
        for s in "FB":
            if view == "back" or view == "front":
                pass
            lay = L["leg" + s]
            self.P(f"thigh{s}", taper(0, 0.01, 0.034, 0, -0.41, 0.026), "skin", J["hip" + s], lay)
            self.P(f"shin{s}", taper(0, 0.0, 0.026, 0, -0.375, 0.021), "skin", J["kn" + s], lay + 0.1)
            self._shoe(s, lay + 0.2)
        # braços
        for s in "FB":
            self._arm(s, L["arm" + s])
        # capuz, pescoço
        self._hood(L["hood"])
        self.P("neck", taper(0, -0.02, 0.03, 0, 0.14, 0.027), "skin", J["neck"], L["neck"])
        # moletom
        self._torso(L["torso"])
        # cabeça e rosto
        self.P("head", circle(0, 0, 0.2, 72), "skin", fc, L["head"])
        if view != "back":
            self._face(L["head"] + 0.5)
        self._extras(L["head"] + 1.5)
        self.pose(1, {}, "CONSTANT")

    # ---------------------------------------------------------------- camadas por vista
    def _layers(self):
        v = self.view
        if v in ("q", "side"):
            return dict(legB=1, armB=2, hood=3, neck=3.6, legF=4, torso=5, head=7, armF=9)
        if v == "front":
            return dict(legB=1, legF=1.4, hood=2, neck=2.6, torso=3, armB=4.2, armF=4.6, head=6)
        return dict(legB=1, legF=1.4, armB=2, armF=2.4, neck=3, torso=4, hood=4.6, head=5.5)   # back

    def P(self, name, pts, mk, parent, lay, outline=True, rim=True):
        y = -lay * LAYER
        o = mesh_pts(f"{self.name}_{name}", pts, self.M[mk] if mk in self.M else self.fm(mk), parent, y)
        if outline:
            mesh_pts(f"{self.name}_{name}_o", offset(pts, OUT), self.M["ink"], parent, y + 0.3 * LAYER)
        if rim:
            rp = [(x + RIM[0], z + RIM[1]) for x, z in offset(pts, OUT * 0.8)]
            mesh_pts(f"{self.name}_{name}_r", rp, self.M["rim"], parent, y + 0.6 * LAYER)
        self.parts.append(o)
        return o

    # ---------------------------------------------------------------- partes
    def _shoe(self, s, lay):
        J = self.j; an = J["an" + s]
        if self.view in ("q", "side"):
            body = smooth([(-0.045, -0.035), (-0.04, 0.01), (0.02, 0.02), (0.1, -0.005), (0.155, -0.03), (0.15, -0.058), (-0.04, -0.06)], 8)
            self.P(f"shoe{s}", body, "skin", an, lay)
            self.P(f"sole{s}", rrect(-0.05, -0.075, 0.16, -0.052, 0.01, 4), "sole", an, lay + 0.05, rim=False)
        else:
            self.P(f"shoe{s}", smooth([(-0.05, -0.06), (-0.052, -0.01), (0.0, 0.015), (0.052, -0.01), (0.05, -0.06)], 8), "skin", an, lay)
            self.P(f"sole{s}", rrect(-0.056, -0.077, 0.056, -0.056, 0.01, 4), "sole", an, lay + 0.05, rim=False)

    def _arm(self, s, lay):
        J = self.j
        self.P("upper" + s, taper(0, 0.015, 0.042, 0, -0.29, 0.036), "hoodie", J["sh" + s], lay)
        self.P("fore" + s, taper(0, 0.0, 0.036, 0, -0.25, 0.033), "hoodie", J["el" + s], lay)
        self.P("cuff" + s, rrect(-0.037, -0.275, 0.037, -0.235, 0.014), "band", J["el" + s], lay + 0.05, rim=False)
        wr = J["wr" + s]
        th = 1 if (self.view != "front" or s == "B") else -1   # lado do polegar
        if self.view == "front":
            th = -1 if s == "F" else 1
        if self.view == "back":
            th = 1 if s == "F" else -1
        hs = self.handsets[s]
        def hand(kind, parts):
            g = empty(f"{self.name}_hand{s}_{kind}", wr, (0, 0, 0))
            for k, (pts, extra) in enumerate(parts):
                self.P(f"hand{s}_{kind}{k}", pts, "skin", g, lay + 0.3 + extra)
            hs[kind] = g
        palm = ellipse(0, -0.055, 0.04, 0.052, 32)
        hand("descanso", [(palm, 0), (taper(0.018 * th, -0.03, 0.015, 0.046 * th, -0.07, 0.012), 0.01)])
        hand("punho", [(ellipse(0, -0.045, 0.043, 0.045, 32), 0), (taper(0.03 * th, -0.025, 0.015, 0.012 * th, -0.07, 0.012), 0.01)])
        hand("aponta", [(ellipse(0, -0.045, 0.042, 0.044, 32), 0), (taper(0.0, -0.06, 0.014, 0.0, -0.15, 0.012), 0.01),
                        (taper(0.03 * th, -0.025, 0.014, 0.04 * th, -0.06, 0.012), 0.02)])
        fing = [(ellipse(0, -0.05, 0.042, 0.042, 32), 0)]
        for k, ang in enumerate((-28, -9, 9, 27)):
            a = math.radians(ang) + math.pi / 2
            fx, fz = 0.03 * math.cos(a) * (-1), -0.07 - 0.03 * math.sin(a)
            tx, tz = 0.11 * math.cos(a) * (-1), -0.05 - 0.11 * math.sin(a)
            fing.append((taper(fx * 0.4, fz, 0.012, tx, tz, 0.0105), 0.005 * k))
        fing.append((taper(0.03 * th, -0.035, 0.014, 0.075 * th, -0.05, 0.012), 0.03))
        hand("aberta", fing)
        hand("joinha", [(ellipse(0, -0.045, 0.043, 0.045, 32), 0), (taper(0.03 * th, -0.035, 0.015, 0.085 * th, -0.03, 0.012), 0.02)])

    def _hood(self, lay):
        J = self.j; v = self.view; ch = J["chest"]
        if v == "front":
            pts = smooth([(-0.16, 0.2), (-0.13, 0.31), (-0.05, 0.34), (0.05, 0.34), (0.13, 0.31), (0.16, 0.2), (0.0, 0.25)], 8)
            self.P("hood", pts, "dark", ch, lay)
        elif v == "q":
            self.P("hood", smooth([(-0.17, 0.21), (-0.06, 0.2), (0.07, 0.27), (0.02, 0.37), (-0.15, 0.39), (-0.2, 0.31)], 8), "dark", ch, lay)
        elif v == "side":
            self.P("hood", smooth([(-0.19, 0.2), (-0.05, 0.22), (0.02, 0.32), (-0.08, 0.38), (-0.2, 0.33)], 8), "dark", ch, lay)
        else:
            self.P("hood", smooth([(-0.15, 0.3), (0.15, 0.3), (0.13, 0.12), (0.0, 0.04), (-0.13, 0.12)], 8), "dark", ch, lay)

    def _torso(self, lay):
        J = self.j; v = self.view; tr = J["torso"]; ch = J["chest"]
        if v in ("front", "back"):
            low = smooth([(-0.165, -0.08), (0.0, -0.095), (0.165, -0.08), (0.155, 0.12), (0.14, 0.24), (-0.14, 0.24), (-0.155, 0.12)], 8)
            up = smooth([(-0.15, -0.06), (0.15, -0.06), (0.17, 0.08), (0.17, 0.2), (0.12, 0.27), (0.0, 0.29), (-0.12, 0.27), (-0.17, 0.2), (-0.17, 0.08)], 8)
        elif v == "q":
            low = smooth([(-0.14, -0.08), (0.02, -0.095), (0.165, -0.08), (0.17, 0.1), (0.15, 0.24), (-0.12, 0.24), (-0.14, 0.1)], 8)
            up = smooth([(-0.13, -0.06), (0.15, -0.06), (0.165, 0.1), (0.13, 0.25), (0.04, 0.29), (-0.08, 0.28), (-0.14, 0.2), (-0.145, 0.05)], 8)
        else:
            low = smooth([(-0.1, -0.08), (0.04, -0.095), (0.125, -0.07), (0.13, 0.1), (0.1, 0.24), (-0.09, 0.24), (-0.105, 0.1)], 8)
            up = smooth([(-0.1, -0.06), (0.11, -0.06), (0.12, 0.1), (0.09, 0.25), (0.0, 0.29), (-0.08, 0.27), (-0.11, 0.18), (-0.11, 0.04)], 8)
        self.P("torso", low, "hoodie", tr, lay)
        self.P("chestp", up, "hoodie", ch, lay)
        # barra do moletom
        if v in ("front", "back"):
            band = rrect(-0.168, -0.098, 0.168, -0.055, 0.02)
        elif v == "q":
            band = rrect(-0.142, -0.098, 0.168, -0.055, 0.02)
        else:
            band = rrect(-0.102, -0.098, 0.128, -0.055, 0.02)
        self.P("band", band, "band", tr, lay + 0.1, outline=False, rim=False)
        if v == "back":
            return
        # bolso e cordões
        if v == "front":
            pk = smooth([(-0.1, -0.035), (0.1, -0.035), (0.085, 0.07), (0.0, 0.085), (-0.085, 0.07)], 6); sx = (-0.035, 0.035)
        elif v == "q":
            pk = smooth([(-0.02, -0.035), (0.15, -0.035), (0.14, 0.07), (0.07, 0.085), (-0.01, 0.07)], 6); sx = (0.06, 0.1)
        else:
            pk = smooth([(0.03, -0.035), (0.125, -0.035), (0.125, 0.07), (0.07, 0.08)], 6); sx = (0.085,)
        self.P("pocket", pk, "dark", tr, lay + 0.15, outline=False, rim=False)
        for k, x in enumerate(sx):
            self.P(f"str{k}", stroke([(x, 0.25), (x + 0.004, 0.13)], 0.006), "white", ch, lay + 0.2, outline=False, rim=False)
            self.P(f"strt{k}", circle(x + 0.004, 0.125, 0.01, 12), "white", ch, lay + 0.2, outline=False, rim=False)

    def _face(self, lay):
        fc = self.face; V = VIEW[self.view]
        y = -lay * LAYER
        self.eyes = {}; self.eyekeys = {}; self.eyealt = {}; self.pups = {}
        for s, ex in (("B", V["eyes"][0]), ("F", V["eyes"][1])):
            if ex is None:
                continue
            inner = -1 if (s == "F") else 1
            if self.view == "side":
                inner = -1
            ej = empty(f"{self.name}_eye{s}", fc, (ex, 0, 0.02))
            self.eyes[s] = ej
            base = eye_shape(inner=inner)
            o = mesh_pts(f"{self.name}_eyew{s}", base, self.M["white"], ej, y, keys=eye_keys(inner))
            self.eyekeys[s] = o; self.boilers.append(o)
            # olhos alternativos: feliz (arco) e fechado (linha)
            arcp = [(-0.029 + 0.058 * i / 10, 0.026 * (1 - ((i / 10) * 2 - 1) ** 2) - 0.008) for i in range(11)]
            alt = {"feliz": mesh_pts(f"{self.name}_eyeh{s}", stroke(arcp, 0.0105), self.M["white"], ej, y),
                   "fechado": mesh_pts(f"{self.name}_eyec{s}", stroke([(-0.028, -0.004), (0.028, -0.004)], 0.0075), self.M["white"], ej, y),
                   "x": mesh_multi(f"{self.name}_eyex{s}", [stroke([(-0.022, -0.026), (0.022, 0.026)], 0.007),
                                                            stroke([(-0.022, 0.026), (0.022, -0.026)], 0.007)], self.M["white"], ej, y)}
            for a in alt.values():
                self.boilers.append(a)
            self.eyealt[s] = alt
            pj = empty(f"{self.name}_pup{s}", ej, (0, 0, 0)); self.pups[s] = pj
            po = mesh_pts(f"{self.name}_pupm{s}", circle(0, 0, 0.0135, 20), self.M["skin"], pj, y - 0.3 * LAYER)
            self.boilers.append(po)
        if V["mx"] is None:
            return
        mj = self.mouth = empty(f"{self.name}_mouth", fc, (V["mx"], 0, -0.085))
        kinds = ["sorriso", "triste", "lado", "nervosa", "pequena"]
        self.mstroke = mesh_pts(f"{self.name}_mstroke", mouth_path("reta"), self.M["white"], mj, y,
                                keys={k: mouth_path(k) for k in kinds})
        fk = ["o", "grito", "falando", "sorrisao", "dentes"]
        self.mfill = mesh_pts(f"{self.name}_mfill", fill_shape("none"), self.M["white"], mj, y,
                              keys={k: fill_shape(k) for k in fk})
        inner = {k: (shrink(fill_shape(k), 0.38) if k in ("o", "grito", "falando") else fill_shape("none")) for k in fk}
        self.minner = mesh_pts(f"{self.name}_minner", fill_shape("none"), self.M["skin"], mj, y - 0.3 * LAYER, keys=inner)
        self.mteeth = mesh_pts(f"{self.name}_mteeth", stroke([(-0.036, -0.002), (0.036, -0.002)], 0.0035), self.M["skin"], mj, y - 0.3 * LAYER)
        for o in (self.mstroke, self.mfill, self.minner, self.mteeth):
            self.boilers.append(o)

    def _extras(self, lay):
        fc = self.face; y = -lay * LAYER; fx = 1 if self.view != "front" else 0
        E = self.extras = {}
        g = empty(f"{self.name}_x_suor", fc, (0.17 if fx else 0.17, 0, 0.1))
        drop = [(0, 0.05)] + [(0.026 * math.cos(math.radians(a)), -0.005 + 0.028 * math.sin(math.radians(a))) for a in range(150, 391, 12)]
        mesh_pts(f"{self.name}_suor", drop, self.fm("sweat"), g, y); E["suor"] = g
        g = empty(f"{self.name}_x_lagrima", fc, (VIEW[self.view]["eyes"][1] or 0.1, 0, -0.03))
        mesh_pts(f"{self.name}_lagrima", rrect(-0.012, -0.12, 0.012, 0.0, 0.012), self.fm("sweat"), g, y); E["lagrima"] = g
        g = empty(f"{self.name}_x_vergonha", fc, (0, 0, 0))
        for s, ex in (("B", VIEW[self.view]["eyes"][0]), ("F", VIEW[self.view]["eyes"][1])):
            if ex is not None:
                mesh_pts(f"{self.name}_blush{s}", ellipse(ex, -0.045, 0.03, 0.013, 24), self.fm("blush"), g, y + 0.2 * LAYER)
        E["vergonha"] = g
        g = empty(f"{self.name}_x_raiva", fc, (0.13, 0, 0.16))
        for k in range(4):
            a = math.radians(45 + 90 * k)
            c = (0.022 * math.cos(a), 0.022 * math.sin(a))
            arcp = [(c[0] + 0.018 * math.cos(a + math.pi + t), c[1] + 0.018 * math.sin(a + math.pi + t)) for t in [(-0.9 + 1.8 * i / 6) for i in range(7)]]
            mesh_pts(f"{self.name}_raiva{k}", stroke(arcp, 0.0055), self.fm("anger"), g, y)
        E["raiva"] = g
        for sym in ("!", "?"):
            g = empty(f"{self.name}_x_{sym}", fc, (0.0, 0, 0.32))
            t = lib.text(f"{self.name}_sym{sym}", sym, 0.18, self.M["white"], g, (0, y, 0), lib.font())
            t.rotation_euler = (math.pi / 2, 0, 0)
            E[sym] = g
        for g in E.values():
            g.scale = (0.0001,) * 3

    # ---------------------------------------------------------------- pose
    NEUTRAL = dict(x=0.0, z=0.0, face=1, bob=0.0, lean=0, chest=0, head=0,
                   armF=6, foreF=-8, wristF=0, armB=-4, foreB=-6, wristB=0, handF="descanso", handB="descanso",
                   legF=0, shinF=0, footF=0, legB=0, shinB=0, footB=0,
                   eye="normal", lid=None, lidv=1.0, wide=0.0, blink=1.0, pupils=False, look=(0.0, 0.0),
                   mouth="reta", mouthv=1.0, extras=())

    def pose(self, frame, p, interp="BEZIER"):
        P = dict(self.NEUTRAL); P.update(p)
        J = self.j; r = self.root
        r.location.x = P["x"]; r.location.z = P["z"]
        r.scale.x = abs(r.scale.x) * (1 if P["face"] >= 0 else -1)
        key(r, "location", frame, interp); key(r, "scale", frame, "CONSTANT")
        J["hips"].location.z = 0.86 + P["bob"]; key(J["hips"], "location", frame, interp)
        front = self.view in ("front", "back")
        def rot(n, a):
            J[n].rotation_euler = (0, -math.radians(a), 0); key(J[n], "rotation_euler", frame, interp)
        rot("torso", P["lean"]); rot("chest", P["chest"]); rot("head", P["head"]); rot("neck", P["head"] * 0.3)
        for s in "FB":
            sg = (1 if s == "F" else -1) if front else 1
            rot("sh" + s, P["arm" + s] * sg); rot("el" + s, P["fore" + s] * sg); rot("wr" + s, P["wrist" + s] * sg)
            rot("hip" + s, P["leg" + s] * sg); rot("kn" + s, P["shin" + s] * sg); rot("an" + s, P["foot" + s] * sg)
            for kind, g in self.handsets[s].items():
                g.scale = (1, 1, 1) if kind == P["hand" + s] else (0.0001,) * 3
                key(g, "scale", frame, "CONSTANT")
        if self.view != "back":
            self._pose_face(frame, P, interp)
        for kname, g in self.extras.items():
            g.scale = (1, 1, 1) if kname in P["extras"] else (0.0001,) * 3
            key(g, "scale", frame, "CONSTANT")

    def _pose_face(self, frame, P, interp):
        style = P["eye"]
        for s, ej in self.eyes.items():
            ej.scale = (1, 1, max(P["blink"], 0.06)); key(ej, "scale", frame, interp)
            o = self.eyekeys[s]
            o.hide_render = style != "normal"; o.keyframe_insert("hide_render", frame=frame)
            for kb in o.data.shape_keys.key_blocks[1:]:
                v = 0.0
                if kb.name == P["lid"]:
                    v = P["lidv"]
                if kb.name == "arregalado":
                    v = max(v, P["wide"])
                kb.value = v; kb.keyframe_insert("value", frame=frame)
            for kind, a in self.eyealt[s].items():
                a.hide_render = kind != style; a.keyframe_insert("hide_render", frame=frame)
            pj = self.pups[s]
            pj.location = (P["look"][0] * 0.013, 0, P["look"][1] * 0.013)
            show = P["pupils"] and style == "normal"
            pj.scale = (1, 1, 1) if show else (0.0001,) * 3
            key(pj, "location", frame, interp); key(pj, "scale", frame, "CONSTANT")
        if not hasattr(self, "mouth"):
            return
        mk = P["mouth"]
        is_stroke = mk in ("reta", "sorriso", "triste", "lado", "nervosa", "pequena")
        for o, show in ((self.mstroke, is_stroke), (self.mfill, not is_stroke), (self.minner, not is_stroke), (self.mteeth, mk == "dentes")):
            o.hide_render = not show; o.keyframe_insert("hide_render", frame=frame)
        for o in (self.mstroke, self.mfill, self.minner):
            for kb in o.data.shape_keys.key_blocks[1:]:
                kb.value = P["mouthv"] if kb.name == mk else 0.0
                kb.keyframe_insert("value", frame=frame)

    # ---------------------------------------------------------------- vida: rabisco, piscar, respirar
    def boil(self, f0, f1, fps=24, rate=3, eye_amp=0.0035, mouth_amp=0.0022, seed=1):
        """treme o contorno de olhos e boca como traço à mão, trocando 'rate' vezes por segundo"""
        rnd = random.Random(seed)
        texs = []
        for axis in ("X", "Z"):
            tx = bpy.data.textures.get("boil_" + axis) or bpy.data.textures.new("boil_" + axis, "CLOUDS")
            tx.noise_scale = 0.025; tx.noise_depth = 1
            texs.append((axis, tx))
        ctl = empty(f"{self.name}_boilctl", self.face, (0, 0, 0))
        for o in self.boilers:
            amp = mouth_amp if "_m" in o.name.split(self.name)[-1][:3] else eye_amp
            for axis, tx in texs:
                d = o.modifiers.new("boil" + axis, "DISPLACE")
                d.texture = tx; d.direction = axis; d.strength = amp * 2; d.mid_level = 0.5
                d.texture_coords = "OBJECT"; d.texture_coords_object = ctl
        step = max(1, round(fps / rate))
        f = f0
        while f <= f1:
            ctl.location = (rnd.uniform(-5, 5), rnd.uniform(-5, 5), rnd.uniform(-5, 5))
            key(ctl, "location", f, "CONSTANT")
            f += step

    def blinks(self, f0, f1, fps=24, seed=2, every=(2.2, 4.0)):
        rnd = random.Random(seed); t = f0 + int(rnd.uniform(*every) * fps)
        while t < f1 - 4:
            for s, ej in self.eyes.items():
                for ff, v in ((t - 1, 1.0), (t, 0.08), (t + 2, 0.08), (t + 4, 1.0)):
                    ej.scale = (1, 1, v); key(ej, "scale", ff, "LINEAR")
            t += int(rnd.uniform(*every) * fps)

    def breathe(self, f0, f1, fps=24, period=3.2, amp=0.006):
        f = f0; ch = self.j["chest"]
        while f <= f1:
            ph = (f - f0) / (period * fps) * 2 * math.pi
            ch.location.z = 0.2 + amp * math.sin(ph); key(ch, "location", f, "BEZIER")
            f += int(period * fps / 4)


class Character:
    """o mesmo personagem nas 4 vistas; pose(view=...) mostra só a vista pedida"""
    def __init__(self, name, views=("front", "q", "side", "back"), pal=None):
        self.name = name; self.mats = {}
        self.v = {}
        for v in views:
            t = Toon(f"{name}_{v}", v, pal, self.mats)
            self.v[v] = t
        self.cur = views[0]

    def pose(self, frame, p, interp="BEZIER"):
        view = p.get("view", self.cur)
        for vn, t in self.v.items():
            t.pose(frame, p, interp)
            t.root.scale.y = t.root.scale.z = 1.0 if vn == view else 0.0001
            t.root.scale.x = (1.0 if vn == view else 0.0001) * (1 if p.get("face", 1) >= 0 else -1)
            key(t.root, "scale", frame, "CONSTANT")
        self.cur = view
