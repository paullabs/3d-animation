"""Protagonista v3 (estilo IfverseTales), com foco no rosto.
Corpo simples: cabeça redonda, pescoço, moletom com capuz e cordões, membros de palito, pés simples.
Rosto: olhos brancos SEM pupila (a forma do olho faz a expressão), sobrancelhas brancas finas, boca com
muitas formas e extras (suor, lágrima, vergonha, raiva, sombra, brilho, ! e ?). Olhos e boca podem
"ferver" (tremer como traço feito à mão) a 3 quadros por segundo.

Regra única de pose: ângulo positivo = PARA ONDE ELE OLHA (na vista de frente/costas, positivo = para fora).
Tudo é desenho plano no XZ, de frente para a câmera; a câmera só desliza."""
import bpy, bmesh, math, random
import lib
from lib import srgb, key, empty
from puppet2d import flatmat, circle, smooth, offset, stroke, area
from char2d import taper, rrect, ellipse, mesh_pts, mesh_multi
from limbs import rubber_limb

LAYER = 0.004
OUT = 0.0055                       # contorno fino (só separa partes)
LIGHT = (0.8, 0.6)                  # luz vem de cima e da frente: brilho por dentro da borda desse lado
TONES = {"hoodie": ("#d8432f", "#a9301f"), "dark": ("#b8382a", "#8c2618"), "skin": ("#0d1020", None),
         "pants": ("#2f62c8", "#22489a"), "shoe": ("#17171d", None),
         "white": ("#f3efe6", None)}


def clip(subject, clipper):
    """recorte de polígono por polígono convexo (Sutherland-Hodgman); ambos anti-horários"""
    def inside(p, a, b):
        return (b[0] - a[0]) * (p[1] - a[1]) - (b[1] - a[1]) * (p[0] - a[0]) >= 0
    def inter(p, q, a, b):
        x1, y1 = p; x2, y2 = q; x3, y3 = a; x4, y4 = b
        d = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
        if abs(d) < 1e-12:
            return q
        t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / d
        return (x1 + t * (x2 - x1), y1 + t * (y2 - y1))
    out = list(subject); n = len(clipper)
    for i in range(n):
        a, b = clipper[i], clipper[(i + 1) % n]
        inp, out = out, []
        if not inp:
            break
        sp = inp[-1]
        for e in inp:
            if inside(e, a, b):
                if not inside(sp, a, b):
                    out.append(inter(sp, e, a, b))
                out.append(e)
            elif inside(sp, a, b):
                out.append(inter(sp, e, a, b))
            sp = e
    return out


def tube(radii, n_len=28, n_cap=10):
    """membro inteiro numa peça só: tubo vertical com raio variável. radii = [(z, r), ...] de cima para baixo"""
    zs = [z for z, _ in radii]
    def r_at(z):
        for (z0, r0), (z1, r1) in zip(radii, radii[1:]):
            if z1 <= z <= z0:
                u = (z0 - z) / max(1e-9, z0 - z1); return r0 + (r1 - r0) * u
        return radii[0][1] if z > zs[0] else radii[-1][1]
    ztop, zbot = zs[0], zs[-1]
    right = [(r_at(ztop - (ztop - zbot) * i / n_len), ztop - (ztop - zbot) * i / n_len) for i in range(n_len + 1)]
    pts = []
    rt, rb = radii[0][1], radii[-1][1]
    for i in range(n_cap + 1):                                    # tampa de cima (da esquerda p/ direita)
        a = math.pi - math.pi * i / n_cap
        pts.append((rt * math.cos(a), ztop + rt * math.sin(a)))
    pts += right[1:-1]
    for i in range(n_cap + 1):                                    # tampa de baixo (direita p/ esquerda)
        a = -math.pi * i / n_cap
        pts.append((rb * math.cos(a), zbot + rb * math.sin(a)))
    pts += [(-x, z) for x, z in right[1:-1][::-1]]
    return pts[::-1]


def glyph_mesh(name, char, size, mat, parent, y, font=None):
    """letra/símbolo como malha plana virada para a câmera (pode 'ferver' com o rabisco)"""
    t = lib.text(name + "_tmp", char, size, mat, None, (0, 0, 0), font or lib.font())
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(t.evaluated_get(dg))
    bpy.data.objects.remove(t)
    for v in me.vertices:                       # texto no plano XY -> desenho no plano XZ
        x, yy, z = v.co
        v.co = (x, 0.0, yy)
    me.materials.clear(); me.materials.append(mat)
    o = bpy.data.objects.new(name, me); bpy.context.scene.collection.objects.link(o)
    o.parent = parent; o.location = (0, y, 0)
    return o


def shift(pts, dx, dz):
    return [(x + dx, z + dz) for x, z in pts]
PAL = dict(hoodie="#d8432f", dark="#a52c20", skin="#0d1020", white="#f3efe6", rim="#ffb070",
           pants="#2f62c8", shoe="#17171d",
           blush="#ff8fa3", sweat="#9ad8ff", anger="#ff5a45", gloom="#8f86c9", gold="#ffd24a")

# ---------------------------------------------------------------- olho (forma por chave)
ERX, ERZ, EN = 0.045, 0.06, 96


def eye_shape(top=None, bottom=None, scale=1.0, inner=-1, sx=1.0):
    pts = []
    for i in range(EN):
        t = 2 * math.pi * i / EN - math.pi / 2
        x = ERX * scale * math.cos(t); z = ERZ * scale * math.sin(t)
        xi = x * (-inner)                  # >0 para fora, <0 para dentro
        if top is not None:
            h, s = top; z = min(z, h * ERZ + s * ERZ * (xi / ERX))
        if bottom is not None:
            h, s = bottom; z = max(z, h * ERZ + s * ERZ * (xi / ERX))
        pts.append((x * sx, z))
    return pts


def eye_keys(inner, sx):
    E = lambda **k: eye_shape(inner=inner, sx=sx, **k)
    return {"sono": E(top=(0.0, 0.0)), "esperto": E(top=(0.12, 0.28)), "bravo": E(top=(0.28, 0.95)),
            "triste": E(top=(0.4, -0.75)), "apertado": E(top=(0.3, 0.0), bottom=(-0.3, 0.0)),
            "sorriso": E(bottom=(-0.22, 0.0)), "arregalado": E(scale=1.3)}


def heart(r=0.034, n=40):
    pts = []
    for i in range(n):
        t = 2 * math.pi * i / n
        x = 16 * math.sin(t) ** 3; z = 13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)
        pts.append((x * r / 17, z * r / 17))
    return pts


def star5(R=0.05, k=0.46):
    """estrela clássica de 5 pontas"""
    return [((R if i % 2 == 0 else R * k) * math.cos(math.pi / 2 + math.pi * i / 5),
             (R if i % 2 == 0 else R * k) * math.sin(math.pi / 2 + math.pi * i / 5)) for i in range(10)]


def star(r=0.046, ri=0.016, n=4, rot=0.0, k=12, p=5.0):
    """brilho de n pontas: corpo arredondado + pontas finas (lados côncavos)"""
    pts = []
    N = n * k * 2
    for i in range(N):
        a = rot + 2 * math.pi * i / N
        w = abs(math.cos(n * (a - rot) / 2))
        rr = ri + (r - ri) * w ** p
        pts.append((rr * math.cos(a), rr * math.sin(a)))
    return pts


# ---------------------------------------------------------------- bocas
MW, MN = 0.082, 25


def mouth_path(kind):
    pts = []
    for i in range(MN):
        u = -1 + 2 * i / (MN - 1); x = u * MW / 2
        z = {"reta": 0.0, "sorriso": 0.026 * u * u - 0.013, "triste": -0.024 * u * u + 0.012,
             "lado": 0.028 * ((u + 1) / 2) ** 2.2 - 0.009, "nervosa": 0.008 * math.sin(3 * math.pi * u),
             "pequena": 0.0, "gato": 0.008 * math.cos(2 * math.pi * u)}[kind]
        if kind == "pequena":
            x *= 0.42
        if kind == "gato":
            x *= 0.7
        pts.append((x, z))
    return stroke(pts, 0.0078)


FN = 64


def fill_shape(kind):
    def dshape(w, h, up=False):
        top = 14; pts = []
        for i in range(top):
            pts.append((w - 2 * w * i / (top - 1), 0.0))
        for i in range(FN - top):
            t = math.pi + math.pi * (i + 1) / (FN - top + 1)
            pts.append((w * math.cos(t), h * math.sin(t)))
        if up:
            pts = [(x, -z) for x, z in pts][::-1]
        return pts
    if kind == "o":
        return ellipse(0, -0.004, 0.02, 0.027, FN, -math.pi / 2)
    if kind == "grito":
        return ellipse(0, -0.022, 0.038, 0.056, FN, -math.pi / 2)
    if kind == "falando":
        return ellipse(0, -0.006, 0.028, 0.015, FN, -math.pi / 2)
    if kind == "sorrisao":
        return [(x, z + 0.008) for x, z in dshape(0.045, 0.04)]
    if kind == "tristeaberta":
        return [(x, z - 0.028) for x, z in dshape(0.034, 0.028, up=True)]
    if kind == "dentes":
        rr = rrect(-0.042, -0.02, 0.042, 0.017, 0.012, 11)
        return (rr + [rr[-1]] * FN)[:FN]
    return ellipse(0, 0, 0.0008, 0.0008, FN)


def shrink(pts, d):
    cx = sum(p[0] for p in pts) / len(pts); cz = sum(p[1] for p in pts) / len(pts)
    return [(cx + (x - cx) * (1 - d), cz + (z - cz) * (1 - d)) for x, z in pts]


STROKES = ("reta", "sorriso", "triste", "lado", "nervosa", "pequena", "gato")
FILLS = ("o", "grito", "falando", "sorrisao", "tristeaberta", "dentes")

# ---------------------------------------------------------------- vistas
VIEW = {
    "front": dict(shF=(0.15, 0.2), shB=(-0.15, 0.2), hipF=0.07, hipB=-0.07, nx=0.0,
                  eyes=((-0.074, 1.0), (0.074, 1.0)), mx=0.0),
    "q":     dict(shF=(0.08, 0.215), shB=(-0.085, 0.215), hipF=0.035, hipB=-0.035, nx=0.02,
                  eyes=((0.004, 0.82), (0.112, 1.0)), mx=0.07),
    "side":  dict(shF=(0.005, 0.215), shB=(-0.012, 0.22), hipF=0.01, hipB=-0.01, nx=0.03,
                  eyes=(None, (0.098, 0.88)), mx=0.122),
    "back":  dict(shF=(0.15, 0.2), shB=(-0.15, 0.2), hipF=0.07, hipB=-0.07, nx=0.0,
                  eyes=(None, None), mx=None),
}


class Heroi:
    PROP = dict(leg=1.0, arm=1.0, neck=1.0, hand=1.0, body_w=1.0, head=1.0, neck_len=1.0, arm_len=1.0, outfit="hoodie")
    # protagonista definitivo (conceito 3 · cores 2 sem cachecol): esguio, jaqueta bomber vermelha, calça azul
    ESGUIO = dict(outfit="bomber", head=0.8, neck=1.3, arm=1.1, hand=0.95, body_w=1.06, arm_len=1.18, neck_len=0.55, leg=0.85)
    ESGUIO_PAL = dict(hoodie="#c62f35", dark="#8f1f27", hoodie_sh_ink="#741820", pants="#2b64c0")
    ESGUIO_TONES = {"hoodie": ("#c62f35", "#9a2329"), "dark": ("#8f1f27", "#6e161d"), "pants": ("#2b64c0", "#1f4a92")}
    PROP = dict(PROP, **ESGUIO)          # o protagonista padrão agora é o esguio de jaqueta

    def __init__(self, name, view="q", pal=None, mats=None, prop=None):
        self.prop = dict(self.PROP, **(prop or {}))
        self.name = name; self.view = view
        self.tones = dict(TONES)
        if self.prop["outfit"] == "bomber":
            pal = dict(self.ESGUIO_PAL, **(pal or {})); self.tones.update(self.ESGUIO_TONES)
        pal = dict(PAL, **(pal or {}))
        M = self.M = mats if mats is not None else {}
        def fm(k):
            if k not in M:
                M[k] = flatmat(f"{name}_{k}", pal[k])
            return M[k]
        self.fm = fm
        pal.setdefault("hoodie_sh_ink", "#8a2417"); pal.setdefault("hoodie_sh", "#a9301f"); pal.setdefault("dark_sh", "#8c2618")
        for k in ("hoodie", "dark", "skin", "white", "rim", "hoodie_sh_ink", "pants", "shoe"):
            fm(k)
        if "ink" not in M:
            M["ink"] = flatmat(f"{name}_ink", pal["skin"])
        V = VIEW[view]
        R = self.root = empty(name)
        J = self.j = {}
        def joint(n, parent, loc):
            J[n] = empty(f"{name}_{n}", parent, loc); J[n].rotation_mode = "XYZ"; return J[n]
        hips = joint("hips", R, (0, 0, 0.86))
        torso = joint("torso", hips, (0, 0, 0))
        chest = joint("chest", torso, (0, 0, 0.2))
        for s in "FB":
            joint("sh" + s, chest, (V["sh" + s][0] * self.prop["body_w"], 0, V["sh" + s][1]))
            al = self.prop["arm_len"]
            joint("el" + s, J["sh" + s], (0, 0, -0.29 * al)); joint("wr" + s, J["el" + s], (0, 0, -0.27 * al))
            joint("hip" + s, hips, (V["hip" + s], 0, 0)); joint("kn" + s, J["hip" + s], (0, 0, -0.41))
            joint("an" + s, J["kn" + s], (0, 0, -0.38))
        joint("neck", chest, (V["nx"], 0, 0.26)); joint("head", J["neck"], (0, 0, 0.1 * self.prop["neck_len"]))
        joint("hemF", hips, (0, 0, 0)); joint("hemB", hips, (0, 0, 0))     # deformadores da barra do moletom
        hsz = joint("hsz", J["head"], (0, 0, 0)); hsz.scale = (self.prop["head"],) * 3      # tamanho da cabeça
        self.face = joint("face", hsz, (0, 0, 0.2))
        self.boilers = []; self.handsets = {"F": {}, "B": {}}
        L = self._layers()
        bomber = self.prop["outfit"] == "bomber"
        self._bends = []; self.limbs = []
        for s in "FB":
            lg = self.prop["leg"]
            # perna "mangueira": uma curva quadril-joelho-tornozelo, joelho arredondado, sem emenda em nenhum ângulo
            far = s == "B" and self.view in ("q", "side")
            if bomber:      # calça azul com sombra; a perna do lado de lá fica na cor da sombra, sem brilho
                psh = self._mat("pants_sh", self.tones["pants"][1])
                mats = dict(main=psh if far else self.M["pants"], shade=self._mat("pants_far", "#173a75") if far else psh,
                            rim=psh if far else self.M["rim"], ink=self.M["ink"])
                r0, r2, ink = 0.05 * lg, 0.036 * lg, 0.12
            else:
                mats = dict(main=self.M["skin"], shade=self.M["skin"], rim=self.M["rim"], ink=self.M["ink"])
                r0, r2, ink = 0.031 * lg, 0.021 * lg, 0.2
            self.limbs.append(rubber_limb(f"{self.name}_leg{s}", J["hip" + s], J["kn" + s], J["an" + s], r0, r2,
                                          -L["leg" + s] * LAYER, mats, ink=ink, fillet=0.08, cap=False, rim=(0.86, 1.0)))
            self._foot(s, L["leg" + s] + 0.6)
            self._arm(s, L["arm" + s])
        if bomber:
            self.P("pelvis", ellipse(0, 0.0, 0.115 * self.prop["body_w"], 0.065, 40), "pants", J["hips"], L["legF"] - 0.5, rimw=0.0)
        else:
            self._hood(L["hood"])
        nk = self.prop["neck"]
        self.P("neck", taper(0, -0.02, 0.029 * nk, 0, 0.14, 0.026 * nk), "skin", J["neck"], L["neck"])
        self._jacket(L["torso"]) if bomber else self._torso(L["torso"])
        self.P("head", circle(0, 0, 0.2, 72), "skin", self.face, L["head"], rimw=0.016)
        if view != "back":
            self._face(L["head"] + 0.5)
        self._extras(L["head"] + 1.6)
        self._deform_hoodie()
        self._apply_bends()
        self.pose(1, {}, "CONSTANT")

    def _apply_bends(self):
        """membros contínuos: a parte abaixo do cotovelo/joelho segue a junta de baixo, com transição suave
        (o equivalente ao 'bone deformer' da animação de recorte profissional)"""
        import bpy
        bpy.context.view_layer.update()
        def sstep(u):
            u = max(0.0, min(1.0, u)); return u * u * (3 - 2 * u)
        for objs, child, zj, b in self._bends:
            for o in objs:
                vg = o.vertex_groups.new(name="bend")
                for v in o.data.vertices:
                    w = sstep(((zj + b) - v.co.z) / (2 * b))
                    if w > 1e-4:
                        vg.add([v.index], w, "REPLACE")
                m = o.modifiers.new("bend", "HOOK")
                m.object = child; m.vertex_group = "bend"; m.falloff_type = "NONE"
                m.matrix_inverse = child.matrix_world.inverted() @ o.matrix_world

    # ---------------------------------------------------------------- deformador do moletom (como o "bone deformer" do Harmony)
    def _deform_hoodie(self):
        """o moletom é uma peça só, mas: de 0.10 a 0.25 de altura passa a seguir o peito (ombros e braços vêm junto);
        abaixo do quadril, a frente segue a junta hemF e as costas a hemB, que são guiadas pelas coxas"""
        import bpy
        J = self.j; tor = J["torso"]
        bpy.context.view_layer.update()
        frontal = self.view in ("front", "back")
        objs = [o for o in tor.children if o.type == "MESH"]
        xs = [v.co.x for o in objs for v in o.data.vertices]
        xmin, xmax = min(xs), max(xs)
        def sstep(u):
            u = max(0.0, min(1.0, u)); return u * u * (3 - 2 * u)
        for o in objs:
            me = o.data
            groups = {}
            for nm, hook in (("dc", J["chest"]), ("dF", J["hemF"]), ("dB", J["hemB"])):
                groups[nm] = (o.vertex_groups.new(name=nm), hook)
            for v in me.vertices:
                x, z = v.co.x, v.co.z
                wc = sstep((z - 0.10) / 0.15)
                wl = 0.0 if frontal else sstep((0.03 - z) / 0.2)
                fx = sstep((x - xmin) / max(1e-6, xmax - xmin))
                for nm, w in (("dc", wc), ("dF", wl * fx), ("dB", wl * (1 - fx))):
                    if w > 1e-4:
                        groups[nm][0].add([v.index], w, "REPLACE")
            for nm, (vg, hook) in groups.items():
                m = o.modifiers.new("hk_" + nm, "HOOK")
                m.object = hook; m.vertex_group = vg.name; m.falloff_type = "NONE"
                m.matrix_inverse = hook.matrix_world.inverted() @ o.matrix_world

    @staticmethod
    def hem_from_legs(legF, legB):
        """frente da barra sobe com a coxa que vai para frente; costas acompanham a que vai para trás"""
        fwd = max(legF, legB, 0.0); back = min(legF, legB, 0.0)
        return 0.75 * max(0.0, fwd - 6.0), 0.55 * min(0.0, back + 6.0)

    def _layers(self):
        v = self.view
        if v in ("q", "side"):
            return dict(legB=1, armB=2, hood=3, neck=3.6, legF=4, torso=5, head=7, armF=9)
        if v == "front":
            return dict(legB=1, legF=1.4, hood=2, neck=2.6, torso=3, armB=4.2, armF=4.6, head=6)
        return dict(legB=1, legF=1.4, armB=2, armF=2.4, neck=3, torso=4, hood=4.6, head=5.5)

    def P(self, name, pts, mk, parent, lay, outline=True, rim=True, shade=0.0, rimw=0.01):
        """forma chapada com sombra (faixa escura do lado oposto à luz) e brilho (faixa clara do lado da luz),
        ambos por DENTRO da silhueta; contorno fino por trás. self.last = todas as malhas criadas"""
        y = -lay * LAYER
        made = []
        if area(pts) < 0:
            pts = pts[::-1]
        base, dark = self.tones.get(mk, (None, None))
        mat = self.M[mk] if mk in self.M else self.fm(mk)
        lx, lz = LIGHT
        body = pts
        if shade and dark:
            made.append(mesh_pts(f"{self.name}_{name}_s", pts, self.M[mk + "_sh"] if (mk + "_sh") in self.M else self._mat(mk + "_sh", dark), parent, y))
            body = clip(shift(pts, lx * shade, lz * shade), pts)
        if rim and rimw > 0:
            sh0 = (shade if (shade and dark) else 0.0) + 0.004      # o brilho começa depois da borda da sombra (sem fio claro)
            made.append(mesh_pts(f"{self.name}_{name}_r", clip(shift(pts, lx * sh0, lz * sh0), pts), self.M["rim"], parent, y - 0.08 * LAYER))
            top = clip(shift(pts, -lx * rimw, -lz * rimw), body)
            o = mesh_pts(f"{self.name}_{name}", top, mat, parent, y - 0.16 * LAYER)
        else:
            o = mesh_pts(f"{self.name}_{name}", body, mat, parent, y - 0.08 * LAYER)
        made.append(o)
        if outline:
            made.append(mesh_pts(f"{self.name}_{name}_o", offset(pts, OUT), self.M["ink"], parent, y + 0.12 * LAYER))
        self.last = made
        return o

    def _mat(self, k, color):
        if k not in self.M:
            self.M[k] = flatmat(f"{self.name}_{k}", color)
        return self.M[k]

    # ---------------------------------------------------------------- corpo
    def _foot(self, s, lay):
        an = self.j["an" + s]
        mk = "shoe" if self.prop["outfit"] == "bomber" else "skin"
        if self.view in ("q", "side"):
            self.P(f"foot{s}", smooth([(-0.035, -0.072), (0.13, -0.074), (0.15, -0.05), (0.11, -0.015), (0.03, 0.012), (-0.035, 0.008)], 8), mk, an, lay, rimw=0.006)
        else:
            self.P(f"foot{s}", smooth([(-0.046, -0.072), (0.046, -0.072), (0.048, -0.02), (0.0, 0.016), (-0.048, -0.02)], 8), mk, an, lay, rimw=0.006)

    def _arm(self, s, lay):
        J = self.j
        am = self.prop["arm"]
        al = self.prop["arm_len"]
        # braço "mangueira" (manga inteira): curva ombro-cotovelo-punho, cotovelo arredondado, tampa redonda no ombro
        far = s == "B" and self.view in ("q", "side")
        hsh = self._mat("hoodie_sh", self.tones["hoodie"][1])
        mats = dict(main=hsh if far else self.M["hoodie"], shade=self._mat("hoodie_far", "#741820") if far else hsh,
                    rim=hsh if far else self.M["rim"], ink=self.M["ink"])
        self.limbs.append(rubber_limb(f"{self.name}_arm{s}", J["sh" + s], J["el" + s], J["wr" + s], 0.038 * am, 0.032 * am,
                                      -lay * LAYER, mats, ink=0.15, fillet=0.07, cap=True, rim=(0.86, 1.0)))
        if self.prop["outfit"] == "bomber":
            self.P("cuff" + s, rrect(-0.033 * am, -0.27 * al + 0.002, 0.033 * am, -0.27 * al + 0.04, 0.01), "dark", J["el" + s], lay + 0.4, rimw=0.005)
        else:
            self.P("cuff" + s, stroke([(-0.028, -0.236 * al), (0.028, -0.236 * al)], 0.0035), "dark", J["el" + s], lay + 0.55, outline=False, rim=False)
        # mão arredondada (sem dedos), como no estilo
        hd = self.prop["hand"]
        self.P("hand" + s, ellipse(0.002, -0.042 * hd, 0.043 * hd, 0.048 * hd, 40), "skin", J["wr" + s], lay + 0.7, rimw=0.007)

    def _hood(self, lay):
        ch = self.j["chest"]; v = self.view
        pts = {"front": [(-0.15, 0.2), (0.15, 0.2), (0.15, 0.27), (0.1, 0.33), (0.0, 0.35), (-0.1, 0.33), (-0.15, 0.27)],
               "q": [(-0.16, 0.2), (-0.02, 0.2), (0.03, 0.27), (0.0, 0.34), (-0.1, 0.36), (-0.165, 0.3)],
               "side": [(-0.17, 0.2), (-0.03, 0.2), (0.02, 0.28), (-0.03, 0.35), (-0.12, 0.36), (-0.18, 0.3)],
               "back": [(-0.15, 0.06), (0.15, 0.06), (0.16, 0.26), (0.1, 0.33), (-0.1, 0.33), (-0.16, 0.26)]}[v]
        piv = {"front": (0.0, 0.26), "q": (-0.06, 0.27), "side": (-0.07, 0.27), "back": (0.0, 0.29)}[v]
        hj = empty(f"{self.name}_hoodj", ch, (piv[0], 0, piv[1])); hj.rotation_mode = "XYZ"; self.j["hood"] = hj
        bw = self.prop["body_w"]
        P_ = [((x - piv[0]) * bw, z - piv[1]) for x, z in smooth(pts, 6)]
        self.P("hood", P_, "dark", hj, lay, shade=0.018, rimw=0.01)
        fold = {"front": [(-0.09, 0.24), (0.0, 0.215), (0.09, 0.24)], "q": [(-0.13, 0.24), (-0.07, 0.3), (-0.02, 0.31)],
                "side": [(-0.14, 0.24), (-0.09, 0.31), (-0.03, 0.32)], "back": [(-0.1, 0.12), (0.0, 0.1), (0.1, 0.12)]}[v]
        self.P("hoodfold", stroke([(x - piv[0], z - piv[1]) for x, z in fold], 0.004), "hoodie_sh_ink", hj, lay + 0.3, outline=False, rim=False)

    def _torso(self, lay):
        J = self.j; v = self.view
        if v in ("front", "back"):
            body = [(-0.15, -0.2), (0.15, -0.2), (0.156, 0.1), (0.152, 0.37), (0.115, 0.455), (0.0, 0.48), (-0.115, 0.455), (-0.152, 0.37), (-0.156, 0.1)]
            strings = (-0.033, 0.033); x0, x1 = -0.15, 0.15
            pocket = [[(-0.085, -0.03), (0.085, -0.03)], [(-0.085, -0.03), (-0.1, -0.14)], [(0.085, -0.03), (0.1, -0.14)]]
        elif v == "q":
            body = [(-0.105, -0.2), (0.125, -0.2), (0.132, 0.1), (0.128, 0.37), (0.095, 0.45), (0.01, 0.478), (-0.07, 0.465), (-0.112, 0.38), (-0.112, 0.1)]
            strings = (0.05, 0.088); x0, x1 = -0.105, 0.125
            pocket = [[(0.0, -0.03), (0.11, -0.03)], [(0.11, -0.03), (0.122, -0.14)]]
        else:
            body = [(-0.095, -0.2), (0.105, -0.2), (0.112, 0.1), (0.106, 0.37), (0.075, 0.45), (-0.01, 0.478), (-0.075, 0.455), (-0.1, 0.37), (-0.1, 0.1)]
            strings = (0.07,); x0, x1 = -0.095, 0.105
            pocket = [[(0.03, -0.03), (0.098, -0.03)], [(0.098, -0.03), (0.108, -0.14)]]
        bw = self.prop["body_w"]
        body = [(x * bw, z) for x, z in body]; x0, x1 = x0 * bw, x1 * bw
        pocket = [[(x * bw, z) for x, z in ln] for ln in pocket]; strings = tuple(x * bw for x in strings)
        self.P("torso", smooth(body, 6), "hoodie", J["torso"], lay, shade=0.03, rimw=0.012)
        self.P("hem", stroke([(x0 + 0.012, -0.165), (x1 - 0.012, -0.165)], 0.0035), "hoodie_sh_ink", J["torso"], lay + 0.35, outline=False, rim=False)
        if v != "back":
            for k, ln in enumerate(pocket):
                self.P(f"pk{k}", stroke(ln, 0.0035), "hoodie_sh_ink", J["torso"], lay + 0.35, outline=False, rim=False)
            for k, x in enumerate(strings):
                sj = empty(f"{self.name}_strj{k}", J["chest"], (x, 0, 0.255)); sj.rotation_mode = "XYZ"; J[f"str{k}"] = sj
                self.P(f"str{k}", stroke([(0.0, 0.0), (0.003, -0.115)], 0.005), "white", sj, lay + 0.5, outline=False, rim=False)
                self.P(f"strt{k}", circle(0.003, -0.118, 0.0075, 12), "white", sj, lay + 0.5, outline=False, rim=False)

    def _jacket(self, lay):
        """jaqueta bomber: curta (até o quadril), um pouco bufante, gola e barra caneladas, zíper"""
        J = self.j; v = self.view; bw = self.prop["body_w"]
        if v in ("front", "back"):      # ombros largos e arredondados: a manga nasce de dentro da jaqueta
            body = [(-0.135, -0.055), (0.135, -0.055), (0.168, 0.02), (0.172, 0.14), (0.176, 0.37), (0.158, 0.44), (0.1, 0.468),
                    (0.0, 0.474), (-0.1, 0.468), (-0.158, 0.44), (-0.176, 0.37), (-0.172, 0.14), (-0.168, 0.02)]
            zip_x = 0.0; col = (-0.075, 0.075)
            folds = [[(-0.15, 0.02), (-0.118, 0.05), (-0.1, 0.035)], [(0.15, 0.02), (0.118, 0.05), (0.1, 0.035)]]
        elif v == "q":
            body = [(-0.1, -0.055), (0.125, -0.055), (0.15, 0.02), (0.152, 0.14), (0.142, 0.33), (0.105, 0.435), (0.02, 0.468),
                    (-0.075, 0.455), (-0.118, 0.38), (-0.13, 0.14), (-0.125, 0.02)]
            zip_x = 0.06; col = (-0.035, 0.085)
            folds = [[(0.135, 0.015), (0.105, 0.05), (0.085, 0.035)], [(-0.11, 0.015), (-0.085, 0.045)]]
        else:
            body = [(-0.09, -0.055), (0.1, -0.055), (0.125, 0.02), (0.128, 0.14), (0.118, 0.34), (0.08, 0.44), (0.0, 0.468),
                    (-0.072, 0.452), (-0.102, 0.37), (-0.112, 0.14), (-0.108, 0.02)]
            zip_x = None; col = (-0.03, 0.08)
            folds = [[(0.11, 0.015), (0.085, 0.05), (0.065, 0.035)]]
        body = [(x * bw, z) for x, z in body]
        bx0 = min(x for x, z in body if z < 0); bx1 = max(x for x, z in body if z < 0)
        self.P("torso", smooth(body, 6), "hoodie", J["torso"], lay, shade=0.03, rimw=0.01)
        # barra canelada (um pouco mais estreita: a jaqueta "cai" sobre ela)
        self.P("band", rrect(bx0 + 0.006, -0.088, bx1 - 0.006, -0.04, 0.016), "dark", J["torso"], lay - 0.2, rimw=0.005)
        for k, fl in enumerate(folds):           # pregas do tecido sobre a barra
            self.P(f"fold{k}", stroke([(x * bw, z) for x, z in fl], 0.003), "hoodie_sh_ink", J["torso"], lay + 0.35, outline=False, rim=False)
        # gola canelada em volta do pescoço
        c0, c1 = col[0] * bw, col[1] * bw
        self.P("collar", smooth([(c0, 0.44), (c1, 0.44), (c1 + 0.012, 0.485), ((c0 + c1) / 2, 0.5), (c0 - 0.012, 0.485)], 6), "dark", J["chest"], lay + 0.3, rimw=0.006)
        if zip_x is not None and v != "back":
            self.P("zip", stroke([(zip_x * bw, 0.43), (zip_x * bw + 0.004, -0.035)], 0.0032), "hoodie_sh_ink", J["torso"], lay + 0.4, outline=False, rim=False)
            self.P("pocketL", stroke([((zip_x + 0.035) * bw, 0.07), ((zip_x + 0.065) * bw, 0.16)], 0.003), "hoodie_sh_ink", J["torso"], lay + 0.4, outline=False, rim=False)

    # ---------------------------------------------------------------- rosto
    def _face(self, lay):
        V = VIEW[self.view]; fc = self.face; y = -lay * LAYER
        self.eyegrp = empty(f"{self.name}_eyegrp", fc, (0, 0, 0))
        self.eyes, self.eyekeys, self.eyealt, self.brows = {}, {}, {}, {}
        W = self.M["white"]
        for s, spec in (("B", V["eyes"][0]), ("F", V["eyes"][1])):
            if spec is None:
                continue
            ex, sx = spec
            inner = -1 if s == "F" else 1
            ej = empty(f"{self.name}_eye{s}", self.eyegrp, (ex, 0, 0.012)); self.eyes[s] = ej
            o = mesh_pts(f"{self.name}_ew{s}", eye_shape(inner=inner, sx=sx), W, ej, y, keys=eye_keys(inner, sx))
            self.eyekeys[s] = o; self.boilers.append(o)
            arcp = [(sx * (-0.04 + 0.08 * i / 10), 0.036 * (1 - ((i / 10) * 2 - 1) ** 2) - 0.01) for i in range(11)]
            alt = {
                "feliz": mesh_pts(f"{self.name}_eh{s}", stroke(arcp, 0.0125), W, ej, y),
                "alivio": mesh_pts(f"{self.name}_ea{s}", stroke([(x, -z) for x, z in arcp], 0.0115), W, ej, y),
                "fechado": mesh_pts(f"{self.name}_ec{s}", stroke([(-0.038 * sx, -0.004), (0.038 * sx, -0.004)], 0.0095), W, ej, y),
                "ponto": mesh_pts(f"{self.name}_ep{s}", circle(0, 0.004, 0.02, 24), W, ej, y),
                "x": mesh_multi(f"{self.name}_ex{s}", [stroke([(-0.03 * sx, -0.034), (0.03 * sx, 0.034)], 0.0088),
                                                       stroke([(-0.03 * sx, 0.034), (0.03 * sx, -0.034)], 0.0088)], W, ej, y),
                "coracao": mesh_pts(f"{self.name}_eco{s}", [(x * sx, z) for x, z in heart(0.047)], self.fm("blush"), ej, y),
                "estrela": mesh_pts(f"{self.name}_est{s}", [(x * sx, z) for x, z in star5(0.066)], W, ej, y),
                "cifrao": glyph_mesh(f"{self.name}_cif{s}", "$", 0.13, self.fm("gold"), ej, y),
            }
            self.eyealt[s] = alt
            self.boilers += list(alt.values())
            bj = empty(f"{self.name}_brow{s}", self.eyegrp, (ex, 0, 0.012 + 0.094)); bj.rotation_mode = "XYZ"
            bp = [(sx * (-0.032 + 0.064 * i / 8), 0.01 * (1 - ((i / 8) * 2 - 1) ** 2)) for i in range(9)]
            b = mesh_pts(f"{self.name}_bw{s}", stroke(bp, 0.0075), W, bj, y)
            self.brows[s] = bj; self.boilers.append(b)
        if V["mx"] is None:
            return
        mj = self.mouth = empty(f"{self.name}_mouth", fc, (V["mx"], 0, -0.098))
        self.mstroke = mesh_pts(f"{self.name}_ms", mouth_path("reta"), W, mj, y, keys={k: mouth_path(k) for k in STROKES[1:]})
        self.mfill = mesh_pts(f"{self.name}_mf", fill_shape("none"), W, mj, y, keys={k: fill_shape(k) for k in FILLS})
        inner = {k: (shrink(fill_shape(k), 0.42) if k in ("o", "grito", "falando") else fill_shape("none")) for k in FILLS}
        self.minner = mesh_pts(f"{self.name}_mi", fill_shape("none"), self.M["skin"], mj, y - 0.3 * LAYER, keys=inner)
        self.mteeth = mesh_pts(f"{self.name}_mt", stroke([(-0.038, -0.0015), (0.038, -0.0015)], 0.0034), self.M["skin"], mj, y - 0.3 * LAYER)
        self.boilers += [self.mstroke, self.mfill, self.minner, self.mteeth]

    def _extras(self, lay):
        fc = self.face; y = -lay * LAYER; V = VIEW[self.view]
        fx = V["eyes"][1][0] if V["eyes"][1] else 0.0
        E = self.extras = {}
        def grp(n, loc):
            g = empty(f"{self.name}_x_{n}", fc, loc); E[n] = g; return g
        g = grp("suor", (0.175, 0, 0.12))
        drop = [(0, 0.05)] + [(0.026 * math.cos(math.radians(a)), -0.005 + 0.028 * math.sin(math.radians(a))) for a in range(150, 391, 12)]
        mesh_pts(f"{self.name}_suor", drop, self.fm("sweat"), g, y)
        g = grp("lagrima", (fx, 0, -0.03))
        mesh_pts(f"{self.name}_lag", rrect(-0.012, -0.13, 0.012, 0.0, 0.012), self.fm("sweat"), g, y)
        g = grp("vergonha", (0, 0, 0))
        for s, spec in (("B", V["eyes"][0]), ("F", V["eyes"][1])):
            if spec:
                ex = spec[0]
                for k in range(3):
                    x0 = ex - 0.03 + k * 0.026
                    mesh_pts(f"{self.name}_vg{s}{k}", stroke([(x0, -0.062), (x0 + 0.013, -0.046)], 0.005), self.fm("blush"), g, y)
        g = grp("raiva", (0.13, 0, 0.16))
        for k in range(4):
            a = math.radians(45 + 90 * k); c = (0.022 * math.cos(a), 0.022 * math.sin(a))
            arcp = [(c[0] + 0.018 * math.cos(a + math.pi + t), c[1] + 0.018 * math.sin(a + math.pi + t)) for t in [(-0.9 + 1.8 * i / 6) for i in range(7)]]
            mesh_pts(f"{self.name}_rv{k}", stroke(arcp, 0.0055), self.fm("anger"), g, y)
        g = grp("sombra", (fx * 0.45, 0, 0.085))
        for k in range(4):
            x0 = -0.054 + k * 0.036
            mesh_pts(f"{self.name}_sb{k}", stroke([(x0, 0.075), (x0, 0.075 - (0.055 + 0.018 * (k % 2)))], 0.0055), self.fm("gloom"), g, y)
        g = grp("brilho", (0.19, 0, 0.17))
        mesh_pts(f"{self.name}_br1", star(0.045, 0.013, 4, 0.0, 16, 4.0), self.M["white"], g, y)
        mesh_pts(f"{self.name}_br2", [(x + 0.055, z - 0.065) for x, z in star(0.026, 0.008, 4, 0.0, 16, 4.0)], self.M["white"], g, y)
        for sym in ("!", "?"):
            g = grp(sym, (0.0, 0, 0.31))
            t = lib.text(f"{self.name}_sym{sym}", sym, 0.18, self.M["white"], g, (0, y, 0), lib.font())
            t.rotation_euler = (math.pi / 2, 0, 0)
        for g in E.values():
            g.scale = (0.0001,) * 3

    # ---------------------------------------------------------------- pose
    NEUTRAL = dict(x=0.0, z=0.0, face=1, bob=0.0, lean=0, chest=0, head=0,
                   armF=4, foreF=10, wristF=0, armB=-4, foreB=10, wristB=0, handF="descanso", handB="descanso",
                   legF=0, shinF=0, footF=0, legB=0, shinB=0, footB=0,
                   eye="normal", lid=None, lidv=1.0, wide=0.0, blink=1.0, look=(0.0, 0.0),
                   brows=True, brow=0.0, browup=0.0, browtilt=0.0,
                   mouth="reta", mouthv=1.0, extras=())

    def pose(self, frame, p, interp="BEZIER"):
        P = dict(self.NEUTRAL); P.update(p)
        J = self.j; r = self.root
        r.location.x = P["x"]; r.location.z = P["z"]
        r.scale.x = abs(r.scale.x) * (1 if P["face"] >= 0 else -1)
        key(r, "location", frame, interp); key(r, "scale", frame, "CONSTANT")
        J["hips"].location.z = 0.86 + P["bob"]; key(J["hips"], "location", frame, interp)
        frontal = self.view in ("front", "back")
        def rot(n, a):
            # ossos que apontam para cima (tronco, peito, pescoço, cabeça) têm o sinal oposto aos que apontam para baixo
            sg = 1 if n in ("torso", "chest", "head", "neck", "hood") else -1
            J[n].rotation_euler = (0, sg * math.radians(a), 0); key(J[n], "rotation_euler", frame, interp)
        rot("torso", P["lean"]); rot("chest", P["chest"]); rot("head", P["head"] * 0.7); rot("neck", P["head"] * 0.3)
        for s in "FB":
            sg = (1 if s == "F" else -1) if frontal else 1
            rest_out = 5.0 if frontal else 0.0          # de frente o braço não fica "colado" na jaqueta
            rot("sh" + s, (P["arm" + s] + rest_out) * sg); rot("el" + s, P["fore" + s] * sg); rot("wr" + s, P["wrist" + s] * sg)
            rot("hip" + s, P["leg" + s] * sg); rot("kn" + s, P["shin" + s] * sg); rot("an" + s, P["foot" + s] * sg)
        hf, hb = (0.0, 0.0) if frontal else self.hem_from_legs(P["legF"], P["legB"])
        rot("hemF", hf); rot("hemB", hb)
        if self.view != "back":
            self._pose_face(frame, P, interp)
        for kn, g in self.extras.items():
            g.scale = (1, 1, 1) if kn in P["extras"] else (0.0001,) * 3
            key(g, "scale", frame, "CONSTANT")

    def _pose_face(self, frame, P, interp):
        st = P["eye"]
        self.eyegrp.location = (P["look"][0] * 0.016, 0, P["look"][1] * 0.016); key(self.eyegrp, "location", frame, interp)
        for s, ej in self.eyes.items():
            ej.scale = (1, 1, max(P["blink"], 0.06)); key(ej, "scale", frame, interp)
            o = self.eyekeys[s]
            o.hide_render = st != "normal"; o.keyframe_insert("hide_render", frame=frame)
            for kb in o.data.shape_keys.key_blocks[1:]:
                v = P["lidv"] if kb.name == P["lid"] else 0.0
                if kb.name == "arregalado":
                    v = max(v, P["wide"])
                kb.value = v; kb.keyframe_insert("value", frame=frame)
            for kind, a in self.eyealt[s].items():
                a.hide_render = kind != st; a.keyframe_insert("hide_render", frame=frame)
            bj = self.brows[s]
            sgn = 1 if s == "F" else -1
            tilt = P["browtilt"] * (1 if s == "F" else -1)
            bj.location.z = 0.012 + 0.094 + P["browup"] + tilt + max(P["wide"], 0) * 0.024
            bj.rotation_euler = (0, math.radians(P["brow"]) * sgn, 0)
            bj.scale = (1, 1, 1) if P["brows"] else (0.0001,) * 3
            key(bj, "location", frame, interp); key(bj, "rotation_euler", frame, interp); key(bj, "scale", frame, "CONSTANT")
        if not hasattr(self, "mouth"):
            return
        mk = P["mouth"]; is_stroke = mk in STROKES
        for o, show in ((self.mstroke, is_stroke), (self.mfill, not is_stroke), (self.minner, not is_stroke), (self.mteeth, mk == "dentes")):
            o.hide_render = not show; o.keyframe_insert("hide_render", frame=frame)
        for o in (self.mstroke, self.mfill, self.minner):
            for kb in o.data.shape_keys.key_blocks[1:]:
                kb.value = P["mouthv"] if kb.name == mk else 0.0
                kb.keyframe_insert("value", frame=frame)

    def vis(self, frame, on, size=None):
        """mostra/esconde o personagem (escala ~0 quando escondido) mantendo o espelhamento"""
        if size is not None:
            self.base_scale = size
        s = getattr(self, "base_scale", 1.0) if on else 0.0001
        sx = s * (1 if self.root.scale.x >= 0 else -1)
        self.root.scale = (sx, s, s); key(self.root, "scale", frame, "CONSTANT")

    # ---------------------------------------------------------------- vida
    def boil(self, f0, f1, fps=24, rate=3, eye_amp=(0.0024, 0.0015), mouth_amp=(0.0015, 0.0008), seed=1):
        """rabisco vivo: a borda de olhos, sobrancelhas e boca é redesenhada 'rate' vezes por segundo,
        como traço feito à mão. Duas camadas de ruído: ondulação larga + aspereza fina. O preenchimento continua."""
        rnd = random.Random(seed)
        layers = []
        for li, scale in enumerate((0.05, 0.011)):
            ctl = empty(f"{self.name}_boilctl{li}", self.face, (0, 0, 0))
            for axis in ("X", "Z"):
                nm = f"boil{li}_{axis}"
                tx = bpy.data.textures.get(nm) or bpy.data.textures.new(nm, "CLOUDS")
                tx.noise_scale = scale; tx.noise_depth = 1 if li == 0 else 0
                layers.append((li, axis, tx, ctl))
        for o in self.boilers:
            tag = o.name[len(self.name):]
            amps = mouth_amp if tag.startswith("_m") else eye_amp
            for li, axis, tx, ctl in layers:
                d = o.modifiers.new(f"boil{li}{axis}", "DISPLACE")
                d.texture = tx; d.direction = axis; d.strength = amps[li] * 2; d.mid_level = 0.5
                d.texture_coords = "OBJECT"; d.texture_coords_object = ctl
        step = max(1, round(fps / rate)); f = f0
        while f <= f1:
            for li, axis, tx, ctl in layers[::2]:
                ctl.location = (rnd.uniform(-5, 5), rnd.uniform(-5, 5), rnd.uniform(-5, 5)); key(ctl, "location", f, "CONSTANT")
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
