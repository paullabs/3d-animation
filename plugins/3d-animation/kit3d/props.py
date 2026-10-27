"""Objetos e cenários 2D chapados das histórias (mesmo estilo do protagonista: forma chapada, contorno fino de
tinta, faixa de sombra e de luz por dentro da borda). Tudo no plano XZ, de frente para a câmera; a profundidade
vem do Y de cada peça. A câmera só desliza.
Convenção: cada objeto devolve uma raiz (empty) que pode ser movida, escalada e animada."""
import bpy, bmesh, math, random
import numpy as np
import lib
from lib import srgb, key, empty
from puppet2d import flatmat, circle, smooth, offset, stroke, area, capsule
from char2d import rrect, ellipse, taper, mesh_pts, mesh_multi
from heroi import clip, shift, heart, star5
import cena, sets
from sets import fogmat
import semantico as S

INK = "#0d1020"
LIGHT = (0.8, 0.6)
PI = math.pi

# ---------------------------------------------------------------- paletas extras (usam as mesmas chaves do cena.PAL)
def _mix(a, b, t):
    ca, cb = srgb(a), srgb(b)
    lin = [x + (y - x) * t for x, y in zip(ca, cb)]
    return "#" + "".join(f"{int(round(255 * (c * 12.92 if c <= 0.0031308 else 1.055 * c ** (1 / 2.4) - 0.055))):02x}" for c in lin)


cena.PAL["alvorada"] = dict(cena.PAL["drama"], sky_top="#1d2a55", sky_mid="#6b5a8e", horizon="#ffb98a", haze="#8f7aa0",
                            sun="#fff1d2", sun_glow="#ffb27a", far="#4b4268", city="#3a3355", bld="#2c2a47", bld_lit="#6a5a86",
                            bld_top="#221f3a", ground="#2a2a40", walk="#35354e", curb="#4b4a68", mist="#8f7aa0", rim="#ffc58a",
                            win_on="#ffd8a0", shadow="#12122a", dust="#ffe6c8")
cena.PAL["dourado"] = dict(cena.PAL["manha"], sky_top="#f3b36a", sky_mid="#ffd18f", horizon="#fff0c8", haze="#ffe0a8",
                           sun="#ffffff", sun_glow="#ffd07a", far="#e7a77a", city="#d6926a", bld="#b8736a", bld_lit="#ffd08a",
                           bld_top="#8e5a62", ground="#c98f6a", walk="#d9a37a", curb="#f0c096", mist="#ffe6b8", rim="#fff0c0",
                           shadow="#6a4040", dust="#fff6d8", shaft="#fff0c0")


# ---------------------------------------------------------------- materiais e formas básicas
DESAT = 0.0                      # 0 = cores originais; 0.6 = objetos apagados (estilo limpo)
DESAT_TO = "#7d818c"
ACCENT = {"#e2364b", "#ffd24a", "#c62f35", "#ffffff", "#0d1020", "#f6f1e4", "#ff3b4f"}


def FM(color, strength=1.0):
    """emissão chapada sem névoa (mesmo material do protagonista). Com DESAT > 0 as cores dos objetos ficam apagadas,
    exceto as de destaque (vermelho, amarelo, branco, tinta)."""
    if DESAT and color.lower() not in ACCENT:
        color = _mix(color, DESAT_TO, DESAT)
    return flatmat(f"fm_{color}_{strength:g}", color, strength)


def poly(name, pts, color, y=0.0, parent=None, strength=1.0, mat=None):
    if area(pts) < 0:
        pts = pts[::-1]
    return mesh_pts(name, pts, mat or FM(color, strength), parent, y)


def inked(name, pts, color, parent=None, loc=(0, 0, 0), ink=INK, w=0.012, shade=0.0, shade_color=None,
          rim=0.0, rim_color=None, strength=1.0):
    """forma com contorno de tinta; sombra (do lado oposto à luz) e brilho (do lado da luz) por dentro da silhueta.
    Devolve a raiz; as camadas ficam separadas em Y por frações de milímetro (nada pisca)."""
    if area(pts) < 0:
        pts = pts[::-1]
    root = empty(name, parent, loc)
    if w:
        mesh_pts(name + "_o", offset(pts, w), FM(ink), root, 0.0012)
    body = pts
    if shade and shade_color:
        mesh_pts(name + "_s", pts, FM(shade_color, strength), root, 0.0008)
        body = clip(shift(pts, LIGHT[0] * shade, LIGHT[1] * shade), pts)
    if rim and rim_color:
        mesh_pts(name + "_r", body, FM(rim_color, strength), root, 0.0004)
        body = clip(shift(body, -LIGHT[0] * rim, -LIGHT[1] * rim), body)
    mesh_pts(name + "_f", body, FM(color, strength), root, 0.0)
    return root


def txt(name, s, size, color="#ffffff", loc=(0, 0, 0), parent=None, align="CENTER", ink=INK, ow=0.07, y=0.0):
    """texto plano de frente para a câmera, com contorno escuro (lê em qualquer fundo)"""
    root = empty(name, parent, loc)
    t = lib.text(name + "_t", s, size, FM(color), root, (0, y - 0.0016, 0), lib.font())
    t.rotation_euler = (PI / 2, 0, 0); t.data.align_x = align
    if ink:
        o = lib.text(name + "_o", s, size, FM(ink), root, (0, y, 0), lib.font())
        o.rotation_euler = (PI / 2, 0, 0); o.data.offset = size * ow; o.data.align_x = align
    return root


def bgflat(name, pts, color, y, strength=1.0, fog=True):
    """camada de fundo (com névoa por distância)"""
    return cena.flat(name, pts, color, y, strength, fog)


def mat_fog(name, color):
    return fogmat(f"{name}__{color}", color)


# ---------------------------------------------------------------- animação utilitária
def drop(o, f, z_to, z_from, frames=9, bounce=0.18):
    """cai de z_from até z_to com um quique"""
    o.location.z = z_from; key(o, "location", f - 1, "BEZIER")
    for ff, z in ((f + frames * 0.55, z_to), (f + frames * 0.8, z_to + (z_from - z_to) * bounce), (f + frames, z_to)):
        o.location.z = z; key(o, "location", int(round(ff)), "BEZIER")


def slide(o, f0, f1, p0, p1, interp="BEZIER"):
    o.location = p0; key(o, "location", f0, interp)
    o.location = p1; key(o, "location", f1, interp)


def appear(o, f, s=1.0, frames=7, over=0.16):
    S.pop(o, f, s, frames, over)


def vanish(o, f, frames=4):
    o.scale = o.scale.copy(); key(o, "scale", f, "BEZIER")
    o.scale = (0.0001,) * 3; key(o, "scale", f + frames, "BEZIER")


def blink_vis(o, frames, on_off=True):
    """liga/desliga por escala em quadros dados: frames = lista de (quadro, ligado). Mantém a escala original (ex.: raio de um disco)."""
    base = tuple(o.scale)
    for f, on in frames:
        o.scale = base if on else (0.0001, 0.0001, 0.0001)
        key(o, "scale", f, "CONSTANT")
    o.scale = base


def sway(o, f0, f1, amp_deg=1.2, period=70, phase=0.0, axis=1):
    """balanço leve de quem está parado (rotação em torno do pé)"""
    f = f0
    while f <= f1:
        ang = amp_deg * math.sin(2 * PI * (f - f0) / period + phase)
        r = list(o.rotation_euler); r[axis] = math.radians(ang); o.rotation_euler = tuple(r)
        key(o, "rotation_euler", f, "BEZIER")
        f += max(2, period // 6)


def shake_rig(rig, f0, frames, amp=0.06, seed=3):
    """tremida de câmera com decaimento (no empty-pai da câmera)"""
    rnd = random.Random(seed)
    rig.location = (0, 0, 0); key(rig, "location", f0 - 1, "LINEAR")
    for i in range(frames):
        k = (1 - i / frames) ** 2
        rig.location = (rnd.uniform(-1, 1) * amp * k, 0, rnd.uniform(-1, 1) * amp * k); key(rig, "location", f0 + i, "LINEAR")
    rig.location = (0, 0, 0); key(rig, "location", f0 + frames, "LINEAR")


# ---------------------------------------------------------------- roupa do protagonista (cinza -> vermelho)
GRAY = dict(hoodie="#8f95a3", hoodie_sh="#737987", hoodie_far="#5b6170", hoodie_sh_ink="#5b6170", dark="#6a7080",
            pants="#6d7487", pants_sh="#565c6d", pants_far="#464c5c")
RED = dict(hoodie="#c62f35", hoodie_sh="#9a2329", hoodie_far="#741820", hoodie_sh_ink="#741820", dark="#8f1f27",
           pants="#2b64c0", pants_sh="#1f4a92", pants_far="#173a75")
BLACK = dict(hoodie="#2c2f3b", hoodie_sh="#1f212b", hoodie_far="#14161e", hoodie_sh_ink="#14161e", dark="#1b1d27",
             pants="#23252f", pants_sh="#191b23", pants_far="#101219")


def _emis(m):
    for n in m.node_tree.nodes:
        if n.type == "EMISSION":
            return n.inputs[0]


def tint(H, colors, f=None):
    """pinta as roupas do protagonista; com f, grava a cor naquele quadro (para transições)"""
    for k, c in colors.items():
        m = H.M.get(k)
        if m is None:
            continue
        s = _emis(m); s.default_value = (*srgb(c), 1)
        if f is not None:
            s.keyframe_insert("default_value", frame=f)


# ---------------------------------------------------------------- sombra de contato em qualquer objeto
def sombra(root, P, w=0.3, depth=0.15):
    m = cena.amat("cshadow_m", P["shadow"], 1.0, 0.6, ("radial", 1.2))
    o = cena.ground_disc(root.name + "_cs", w, depth, m, (0, 0, 0.002))
    o.parent = root; o.location = (0, 0, 0.002)
    return o


# ---------------------------------------------------------------- pessoas (silhuetas) e objetos de mão
def pessoa(name, x, y, color="#2b2f45", h=1.0, flip=1, accent=None, P=None, head_c="#0d1020", z=0.0, rim=None):
    """pessoa de silhueta (cabeça escura, roupa de cor única), 1,75 m x h. Sem rosto: é só 'gente'."""
    root = empty(name, None, (x, y, z)); root.scale = (h * flip, h, h)
    def part(nm, pts, col, w=0.007):
        if rim:
            return inked(f"{name}_{nm}", pts, col, root, w=w, rim=0.012, rim_color=rim)
        return inked(f"{name}_{nm}", pts, col, root, w=w)
    part("legB", taper(0.07, 0.86, 0.058, 0.075, 0.07, 0.04), _mix(color, "#000000", 0.35))
    part("shoeB", ellipse(0.1, 0.03, 0.075, 0.03, 20), "#0b0c14")
    part("legF", taper(-0.07, 0.86, 0.06, -0.075, 0.07, 0.042), color)
    part("shoeF", ellipse(-0.04, 0.03, 0.075, 0.03, 20), "#0b0c14")
    part("armB", taper(0.2, 1.4, 0.05, 0.22, 0.86, 0.04), _mix(color, "#000000", 0.35))
    part("body", rrect(-0.2, 0.82, 0.2, 1.48, 0.09, 6), accent or color)
    part("armF", taper(-0.2, 1.4, 0.052, -0.215, 0.84, 0.042), color)
    part("neck", rrect(-0.04, 1.44, 0.04, 1.56, 0.02, 3), head_c, w=0.004)
    part("head", circle(0, 1.64, 0.13, 40), head_c)
    if P:
        sombra(root, P, 0.32 * h, 0.14 * h)
    return root


def caixa(name, parent=None, loc=(0, 0, 0), s=1.0, color="#c99a5b"):
    """caixa de papelão com fita e etiqueta (0,36 x 0,26 m)"""
    root = empty(name, parent, loc); root.scale = (s, s, s)
    W, Hh = 0.36, 0.26
    inked(name + "_b", rrect(-W / 2, -Hh / 2, W / 2, Hh / 2, 0.012, 3), color, root, shade=0.035, shade_color=_mix(color, "#000000", 0.28),
          rim=0.012, rim_color=_mix(color, "#ffffff", 0.35), w=0.008)
    poly(name + "_tape", [(-0.03, -Hh / 2), (0.03, -Hh / 2), (0.03, Hh / 2), (-0.03, Hh / 2)], _mix(color, "#ffffff", 0.45), -0.0006, root)
    poly(name + "_tag", rrect(0.07, -0.085, 0.15, -0.015, 0.008, 2), "#f4efe2", -0.0008, root)
    return root


# ---------------------------------------------------------------- giz no chão
def ring(name, cx, cy, rx, ry, w, color="#f3efe6", n=96, wob=0.18, seed=2, gaps=((0.0, 0.0),), z=0.003):
    """anel deitado no chão (giz), com espessura irregular e pequenos vazios. Devolve a raiz."""
    rnd = random.Random(seed)
    m = fogmat(f"{name}__{color}", color)
    bm = bmesh.new()
    ph = [rnd.uniform(0, 6.28) for _ in range(3)]
    def wid(a):
        return w * (1 + wob * (math.sin(3 * a + ph[0]) * 0.6 + math.sin(7 * a + ph[1]) * 0.4))
    prev = None
    for i in range(n + 1):
        a = 2 * PI * i / n
        wi = wid(a)
        o_ = bm.verts.new(((rx + wi / 2) * math.cos(a), (ry + wi / 2) * math.sin(a), 0.0))
        i_ = bm.verts.new(((rx - wi / 2) * math.cos(a), (ry - wi / 2) * math.sin(a), 0.0))
        if prev is not None:
            u = (i - 0.5) / n
            if not any(g0 <= u <= g1 for g0, g1 in gaps):
                bm.faces.new((prev[0], prev[1], i_, o_))
        prev = (o_, i_)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free(); me.materials.append(m)
    o = bpy.data.objects.new(name, me); bpy.context.scene.collection.objects.link(o)
    o.location = (cx, cy, z)
    return o


# ---------------------------------------------------------------- cenário: céu por altura, nuvens, chão, horizonte
def skywall(name, y, stops, x0=-900, x1=900, z0=-300, z1=600, strength=1.0):
    """parede de céu com degradê pela ALTURA no mundo (a câmera sobe e o céu muda). stops = [(z, cor), ...]"""
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; N = nt.nodes; L = nt.links; N.clear()
    out = N.new("ShaderNodeOutputMaterial"); em = N.new("ShaderNodeEmission"); em.inputs[1].default_value = strength
    geo = N.new("ShaderNodeNewGeometry"); sep = N.new("ShaderNodeSeparateXYZ")
    mr = N.new("ShaderNodeMapRange"); mr.clamp = True
    mr.inputs[1].default_value = stops[0][0]; mr.inputs[2].default_value = stops[-1][0]
    mr.inputs[3].default_value = 0.0; mr.inputs[4].default_value = 1.0
    ramp = N.new("ShaderNodeValToRGB")
    els = ramp.color_ramp.elements
    zs = [s_[0] for s_ in stops]
    while len(els) > 1:
        els.remove(els[-1])
    els[0].position = 0.0; els[0].color = (*srgb(stops[0][1]), 1)
    for z, col in stops[1:]:
        e = els.new((z - zs[0]) / (zs[-1] - zs[0])); e.color = (*srgb(col), 1)
    L.new(geo.outputs["Position"], sep.inputs[0]); L.new(sep.outputs["Z"], mr.inputs[0])
    L.new(mr.outputs[0], ramp.inputs["Fac"]); L.new(ramp.outputs["Color"], em.inputs[0]); L.new(em.outputs[0], out.inputs[0])
    o = cena.poly_mesh(name, [(x0, y, z0), (x1, y, z0), (x1, y, z1), (x0, y, z1)], m)
    return o


def cloud(name, x, z, y, s, color, shade_color=None, fog=True):
    """nuvem chapada (blob de bolhas) com base mais escura"""
    root = empty(name, None, (x, y, z)); root.scale = (s, 1, s)
    pts = smooth([(-1.5, 0.0), (-1.3, 0.38), (-0.8, 0.62), (-0.3, 0.95), (0.35, 0.9), (0.8, 0.55), (1.35, 0.4), (1.5, 0.0), (0.7, -0.12), (-0.7, -0.12)], 8)
    mk = (lambda c, nm: mesh_pts(f"{name}_{nm}", pts, mat_fog(f"{name}{nm}", c), root, 0.0)) if fog else (lambda c, nm: mesh_pts(f"{name}_{nm}", pts, FM(c), root, 0.0))
    if shade_color:
        mesh_pts(f"{name}_sh", [(px, pz - 0.08) for px, pz in pts], mat_fog(f"{name}sh", shade_color) if fog else FM(shade_color), root, 0.002)
    mk(color, "f")
    return root


def skyline(P, rnd, a, b, layers=((6.0, 120.0, 14, 34), (3.0, 55.0, 10, 24)), win=True, lit=0.1, sun_side=-1):
    """prédios de fundo (camadas com névoa). layers = [(escala_x, y, altura_min, altura_max)]"""
    for li, (sx, y, hmin, hmax) in enumerate(layers):
        x = a * sx
        while x < b * sx:
            w = rnd.uniform(4, 9) * (1.0 if li == 0 else 0.8); h = rnd.uniform(hmin, hmax)
            if li == 0:
                cena.flat(f"far{li}_{x:.0f}", cena.rect(x, 0, x + w, h), P["far"], y + rnd.uniform(0, 30))
            else:
                cena.building(f"city{li}_{x:.0f}", x + w / 2, y + rnd.uniform(0, 10), w, h, P, rnd, win=win, lit=lit, sun_side=sun_side, top=True)
            x += w + rnd.uniform(0.3, 2.5)


def chao(P, color=None, y0=-40.0, y1=900.0):
    gm = fogmat("chao_m", color or P["ground"])
    cena.poly_mesh("chao", [(-900, y0, -0.004), (900, y0, -0.004), (900, y1, -0.004), (-900, y1, -0.004)], gm)


def sol(P, loc, r=9.0, glow=160, rays=True):
    cena.disc("sol", r, cena.amat("sol_m", P["sun"], 4.0, 1.0), loc)
    sets.glow("sol_glow", P["sun_glow"], glow, (loc[0], loc[1] - 5, loc[2]), power=2.0, strength=0.95)
    if rays:
        cena.sets2d_rays(P, (loc[0], loc[1] - 8, loc[2]), glow * 1.6)


# ---------------------------------------------------------------- a escada dos 5 níveis (vista de lado, sobe para a direita)
STEP = dict(X0=0.6, SW=1.6, SH=1.15, N=5, TERR=6.0)
STEP_COLORS = ["#5b6f94", "#6a73a0", "#8577a8", "#b07fa0", "#e0a23f"]


def tread_top(k):
    return k * STEP["SH"]


def tread_x(k, frac=0.5):
    return STEP["X0"] + (k - 1 + frac) * STEP["SW"]


def escada(y=0.6, colors=None, numbers=True, gray=False, P=None, gray_to="#2c3146"):
    """degraus 1..5 (1 embaixo, 5 no alto) com um terraço largo no topo. Devolve a raiz e o dicionário das peças."""
    X0, SW, SH, N, TERR = (STEP[k] for k in ("X0", "SW", "SH", "N", "TERR"))
    cols = colors or STEP_COLORS
    root = empty("escada", None, (0, y, 0)); parts = {}
    for k in range(1, N + 1):
        x0 = X0 + (k - 1) * SW; x1 = x0 + SW + (TERR if k == N else 0.0); top = k * SH
        c = cols[k - 1] if not gray else _mix(cols[k - 1], gray_to, 0.8)
        face = inked(f"deg{k}", cena.rect(x0, -3.0, x1, top), c, root, w=0.02, shade=0.05, shade_color=_mix(c, "#000000", 0.32),
                     rim=0.0, rim_color=None)
        poly(f"deg{k}_topo", cena.rect(x0, top - 0.09, x1, top), _mix(c, "#ffffff", 0.38), -0.0016, root)
        poly(f"deg{k}_topo2", cena.rect(x0, top - 0.026, x1, top), _mix(c, "#ffffff", 0.7), -0.0022, root)
        parts[f"deg{k}"] = face
        if numbers:
            t = txt(f"deg{k}_n", str(k), 0.62, "#ffffff", (x0 + SW / 2, -0.004, top - 0.55), root, ow=0.08)
            parts[f"num{k}"] = t
    return root, parts


# ---------------------------------------------------------------- grades (celas) e câmeras de vigilância
def grade(name, x0, x1, z0, z1, y, color="#10131d", n=None, w=0.05, rails=2, strength=1.0, parent=None, x_off=0.0):
    """grade de barras verticais com trilhos horizontais (x_off desloca o desenho para alinhar um vão com o personagem)"""
    root = empty(name, parent, (x_off, y, 0))
    n = n or max(3, int((x1 - x0) / 0.3))
    for i in range(n):
        xc = x0 + (x1 - x0) * (i + 0.5) / n
        poly(f"{name}_b{i}", cena.rect(xc - w / 2, z0, xc + w / 2, z1), color, 0.0, root, strength)
    for r in range(rails):
        zc = z0 + (z1 - z0) * (r + 0.5) / rails if rails > 1 else (z0 + z1) / 2
        zc = z0 + (z1 - z0) * (0.12 + 0.76 * r / max(1, rails - 1)) if rails > 1 else (z0 + z1) / 2
        poly(f"{name}_r{r}", cena.rect(x0, zc - w * 0.6, x1, zc + w * 0.6), color, -0.001, root, strength)
    return root


def arbusto(name, x, z, s, P, y=-1.7):
    """moita escura em primeiro plano (desfocada pela câmera): dá profundidade sem esconder a cena"""
    pts = smooth([(x - 0.6 * s, z - 0.4 * s), (x - 0.75 * s, z + 0.3 * s), (x - 0.1 * s, z + 0.75 * s),
                  (x + 0.6 * s, z + 0.45 * s), (x + 0.7 * s, z - 0.3 * s), (x, z - 0.6 * s)], 10)
    return cena.flat(name, pts, P["fg"], y, fog=False)


def piso_giz(cx, cy, rx, ry, P, w=0.1):
    """círculo de giz no chão com o piso de dentro mais claro (dentro x fora do grupo)"""
    m = cena.amat("giz_piso_m", "#fff4dc", 1.0, 0.16)
    cena.ground_disc("giz_piso", rx, ry, m, (cx, cy, 0.0025), n=72)
    return ring("giz", cx, cy, rx, ry, w, "#f3efe6", gaps=((0.30, 0.36), (0.78, 0.82)))


# ---------------------------------------------------------------- acessórios do protagonista e peças de cena (nível 2)
def chapeu(parent, color="#1c1e29", band="#8f1f27", s=1.0):
    """chapéu de abas (fedora) preso à cabeça (junta 'face': raio da cabeça 0,2)"""
    root = empty("chapeu", parent, (0.015, -0.034, 0.0)); root.scale = (s, 1, s)
    inked("chapeu_aba", ellipse(0.0, 0.158, 0.31, 0.05, 40), color, root, w=0.008, shade=0.02, shade_color=_mix(color, "#000000", 0.5))
    inked("chapeu_copa", rrect(-0.15, 0.165, 0.15, 0.37, 0.06, 5), color, root, loc=(0, -0.0012, 0), w=0.008, shade=0.025, shade_color=_mix(color, "#000000", 0.5))
    poly("chapeu_faixa", cena.rect(-0.15, 0.17, 0.15, 0.225), band, -0.0026, root)
    return root


def ficha(name, parent=None, loc=(0, 0, 0), s=1.0):
    """ficha de cadastro: cartão branco com a silhueta da pessoa, linhas de texto e um carimbo vermelho"""
    root = empty(name, parent, loc); root.scale = (s, s, s)
    inked(name + "_c", rrect(-0.14, -0.19, 0.14, 0.19, 0.014, 3), "#f6f1e4", root, w=0.008, shade=0.02, shade_color="#cfc6b2")
    poly(name + "_h", circle(-0.05, 0.08, 0.05, 20), INK, -0.0014, root)
    poly(name + "_b", rrect(-0.1, -0.03, 0.0, 0.04, 0.03, 3), INK, -0.0014, root)
    for i in range(3):
        poly(f"{name}_l{i}", cena.rect(0.01 if i == 0 else -0.1, 0.1 - 0.075 * i - 0.12 if i else 0.07, 0.1, (0.09 - 0.075 * i - 0.12 if i else 0.09)), "#8a8fa0", -0.0014, root)
    poly(name + "_stamp", circle(0.07, -0.13, 0.05, 24), "#e2364b", -0.0018, root)
    poly(name + "_stampi", circle(0.07, -0.13, 0.034, 24), "#f6f1e4", -0.0022, root)
    return root


def tag_erro(name, loc, s=1.0, text="ERRO!"):
    """plaquinha vermelha 'ERRO!' (estoura na tela e depois voa)"""
    root = empty(name, None, loc); root.scale = (s, s, s)
    inked(name + "_p", rrect(-0.34, -0.15, 0.34, 0.15, 0.06, 5), "#e2364b", root, w=0.018, shade=0.03, shade_color="#a82336", rim=0.012, rim_color="#ff8a96")
    txt(name + "_t", text, 0.19, "#ffffff", (0, -0.006, 0), root, ink="#7a1626", ow=0.05)
    return root


def moeda(name, loc, r=0.13, parent=None, sym=True):
    root = empty(name, parent, loc)
    inked(name + "_o", circle(0, 0, r, 28), "#f2b83a", root, w=r * 0.1, shade=r * 0.28, shade_color="#c98a1c", rim=r * 0.14, rim_color="#ffe48a")
    poly(name + "_in", circle(0, 0, r * 0.66, 24), "#e0a02a", -0.002, root)
    if sym:
        txt(name + "_s", "$", r * 1.0, "#8a5a10", (0, -0.0035, 0), root, ink=None)
    return root


def estrelas(name, loc, n=7, r0=0.1, r1=0.34, color="#ffe066", s=1.0):
    """raios de impacto saindo de um ponto (batida)"""
    root = empty(name, None, loc); root.scale = (s, s, s)
    for i in range(n):
        a = 2 * PI * i / n + 0.3
        pts = [(math.cos(a) * r0 - math.sin(a) * 0.022, math.sin(a) * r0 + math.cos(a) * 0.022),
               (math.cos(a) * r1, math.sin(a) * r1),
               (math.cos(a) * r0 + math.sin(a) * 0.022, math.sin(a) * r0 - math.cos(a) * 0.022)]
        poly(f"{name}_r{i}", pts, color, -0.003, root)
    return root


def sala(P, top="#e6d3b8", bottom="#b99a80", floor="#7c5a4c", y=1.4, w=14.0, h=6.0):
    """ambiente fechado: parede com degradê, rodapé e piso em perspectiva (para as cenas de explicação)"""
    skywall("parede", y, [(0.0, bottom), (2.2, _mix(bottom, top, 0.6)), (h, top)], -w, w, 0.0, h)
    cena.flat("rodape", cena.rect(-w, 0.0, w, 0.16), _mix(bottom, "#000000", 0.35), y - 0.02, fog=False)
    cena.poly_mesh("piso", [(-w, -12, -0.004), (w, -12, -0.004), (w, y, -0.004), (-w, y, -0.004)], fogmat("piso_m", floor))
    return P


def calendario(name, x, z, w=1.7, h=2.15, parent=None):
    """calendário de 12 meses (3 x 4). Devolve (raiz, [centros das células], [raízes das células])"""
    root = empty(name, parent, (x, 0.0, z))
    inked(name + "_b", rrect(-w / 2, -h / 2, w / 2, h / 2, 0.05, 5), "#f6f1e4", root, w=0.025, shade=0.05, shade_color="#d3c9b2",
          rim=0.02, rim_color="#ffffff")
    inked(name + "_h", rrect(-w / 2 + 0.0, h / 2 - 0.34, w / 2, h / 2, 0.05, 5), "#e2364b", root, loc=(0, -0.002, 0), w=0.0)
    txt(name + "_t", "MENSALIDADE", 0.19, "#ffffff", (0, -0.006, h / 2 - 0.17), root, ink="#7a1626", ow=0.05)
    meses = ["JAN", "FEV", "MAR", "ABR", "MAI", "JUN", "JUL", "AGO", "SET", "OUT", "NOV", "DEZ"]
    cw, ch = (w - 0.16) / 3, (h - 0.5) / 4
    cells, centers = [], []
    for i, m in enumerate(meses):
        cx = -w / 2 + 0.08 + cw * (i % 3 + 0.5); cz = h / 2 - 0.42 - ch * (i // 3 + 0.5)
        inked(f"{name}_c{i}", rrect(cx - cw / 2 + 0.03, cz - ch / 2 + 0.03, cx + cw / 2 - 0.03, cz + ch / 2 - 0.03, 0.025, 3), "#fffaf0",
              root, loc=(0, -0.002, 0), w=0.007)
        txt(f"{name}_m{i}", m, 0.105, "#7b8094", (cx, -0.006, cz + ch * 0.27), root, ink=None)
        centers.append((cx, cz)); cells.append(None)
    return root, centers


def ballistic(o, f0, p0, v0, g=9.8, ground=0.0, e=0.35, rot0=0.0, spin=0.0, frames=60, fps=24, axis=1):
    """queda com quique (física simples, uma chave por quadro). v0 em m/s, spin em graus/s"""
    x, y, z = p0; vx, vy, vz = v0; dt = 1.0 / fps; rot = rot0
    for i in range(frames):
        o.location = (x, y, z)
        r = list(o.rotation_euler); r[axis] = math.radians(rot); o.rotation_euler = tuple(r)
        key(o, "location", f0 + i, "LINEAR"); key(o, "rotation_euler", f0 + i, "LINEAR")
        vz -= g * dt; x += vx * dt; y += vy * dt; z += vz * dt; rot += spin * dt
        if z < ground:
            z = ground; vz = -vz * e; vx *= 0.65; spin *= 0.6
            if abs(vz) < 0.5:
                vz = 0.0; vx *= 0.6; spin = 0.0
    return f0 + frames


def world_pos(o, frame):
    """posição no mundo de um objeto num quadro (depois de tudo animado)"""
    bpy.context.scene.frame_set(frame); bpy.context.view_layer.update()
    return o.matrix_world.translation.copy()


# ---------------------------------------------------------------- multidão (uma malha só, milhares de figuras)
def multidao(name, n, cam_z, d0, d1, v_bottom, v_top, colors, seed=7, spacing=0.68, head="#090b15", half_w=0.40, fog=True):
    """n figuras (busto: cabeça + ombros) em fileiras por distância (d0..d1) numa encosta tal que cada fileira
    ocupa uma faixa da tela (v_bottom..v_top, em tangente). Uma malha, uma cor por material. Devolve (objeto, lista de (x,y,z) das cabeças)."""
    rnd = np.random.default_rng(seed)
    R = max(40, int(n / (1.17 * (d0 + d1) / 2.0) * 1.0))
    ds = d0 + (d1 - d0) * (np.arange(R) / (R - 1)) ** 1.15
    vs = v_bottom + (v_top - v_bottom) * ((ds - d0) / (d1 - d0)) ** 0.7
    zs = cam_z + vs * ds
    w = ds * half_w * 2
    cnt = np.maximum(8, (w / spacing).astype(int))
    scale = n / cnt.sum()
    cnt = np.maximum(4, (cnt * scale).astype(int))
    heads = []
    P_ = []; C_ = []
    xs_all = []; ys_all = []; zs_all = []; sz_all = []; ci_all = []
    for r in range(R):
        k = cnt[r]
        x = (np.arange(k) + rnd.uniform(0.0, 1.0, k) * 0.6) / k * w[r] - w[r] / 2
        xs_all.append(x); ys_all.append(ds[r] + rnd.uniform(0, 1.5, k)); zs_all.append(zs[r] + rnd.uniform(-0.25, 0.1, k))
        sz_all.append(rnd.uniform(0.88, 1.14, k)); ci_all.append(rnd.integers(0, len(colors), k))
    X = np.concatenate(xs_all); Y = np.concatenate(ys_all); Z = np.concatenate(zs_all); SZ = np.concatenate(sz_all); CI = np.concatenate(ci_all)
    N = len(X)
    # gabarito do busto (m): cabeça octógono r=0.11 em z=0.62; ombros trapézio
    th = np.arange(10) * 2 * np.pi / 10
    head_t = np.stack([0.11 * np.cos(th), np.zeros(10), 0.60 + 0.11 * np.sin(th)], 1)
    body_t = np.array([(-0.26, 0, 0.0), (0.26, 0, 0.0), (0.27, 0, 0.30), (0.17, 0, 0.47), (-0.17, 0, 0.47), (-0.27, 0, 0.30)])
    V = np.zeros((N, 16, 3), dtype=np.float32)
    V[:, :6, :] = body_t[None] * SZ[:, None, None]
    V[:, 6:, :] = head_t[None] * SZ[:, None, None]
    V[:, :, 0] += X[:, None]; V[:, :, 1] = Y[:, None] + V[:, :, 1] * 0 + np.where(np.arange(16)[None, :] < 6, 0.0, -0.01); V[:, :, 2] += Z[:, None]
    faces = []
    base = np.arange(N) * 16
    for i in range(N):
        b = int(base[i]); faces.append(tuple(range(b, b + 6))); faces.append(tuple(range(b + 6, b + 16)))
    me = bpy.data.meshes.new(name)
    me.from_pydata(V.reshape(-1, 3).tolist(), [], faces)
    mats = []
    for i, col in enumerate(colors):
        mats.append(fogmat(f"{name}_c{i}", col)); me.materials.append(mats[-1])
    me.materials.append(fogmat(f"{name}_head", head))
    mi = np.empty(N * 2, dtype=np.int32); mi[0::2] = CI; mi[1::2] = len(colors)
    me.polygons.foreach_set("material_index", mi)
    me.update()
    o = bpy.data.objects.new(name, me); bpy.context.scene.collection.objects.link(o)
    prof = lambda d: cam_z + (v_bottom + (v_top - v_bottom) * np.clip((d - d0) / (d1 - d0), 0, None) ** 0.7) * d
    return o, np.stack([X, Y, Z + 0.6], 1), prof


def terreno(name, prof, d0, d1, color="#0b1222", w=900.0, n=70):
    """a encosta onde a multidão está (superfície com a mesma altura das fileiras)"""
    bm = bmesh.new(); prev = None
    for k in range(n + 1):
        d = d0 - 6 + (d1 - d0 + 40) * (k / n) ** 1.4
        z = float(prof(d)) - 0.2
        a = bm.verts.new((-w, d, z)); b = bm.verts.new((w, d, z))
        if prev:
            bm.faces.new((prev[0], prev[1], b, a))
        prev = (a, b)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free(); me.materials.append(fogmat(name + "_m", color))
    o = bpy.data.objects.new(name, me); bpy.context.scene.collection.objects.link(o)
    return o


def fio(name, p0, p1, w=0.3, color="#bfe6ff", strength=3.0, alpha=0.85):
    """linha fina entre dois pontos do mundo (origem em p0: a escala 0->1 'desenha' a linha)"""
    import mathutils
    d = mathutils.Vector((p1[0] - p0[0], p1[1] - p0[1], p1[2] - p0[2]))
    # largura perpendicular à direção de visão (câmera olhando +Y): usa o vetor lateral no plano XZ
    n = mathutils.Vector((-d.z, 0.0, d.x)); n.normalize(); n *= w / 2
    bm = bmesh.new()
    vs = [bm.verts.new(v) for v in ((n.x, n.y, n.z), (d.x + n.x, d.y + n.y, d.z + n.z), (d.x - n.x, d.y - n.y, d.z - n.z), (-n.x, -n.y, -n.z))]
    bm.faces.new(vs)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free(); me.materials.append(cena.amat(f"fio_{color}", color, strength, alpha))
    o = bpy.data.objects.new(name, me); bpy.context.scene.collection.objects.link(o)
    o.location = tuple(p0)
    return o


# ---------------------------------------------------------------- cela
def cela_interior(P, frames, y_wall=1.5, final=False, pcc_x=-0.45):
    """cela à noite, limpa: parede escura de uma cor, uma janela gradeada com luz fria (a única luz), chão escuro,
    grade desfocada na frente e 'PCC' riscado bem apagado na parede."""
    sets.FOG.update(color="#0a101c", near=6.0, far=60.0, max=0.3)
    skywall("parede_cela", y_wall, [(-0.5, "#090d16"), (1.2, "#121a2b"), (2.6, "#1b2540"), (4.4, "#0a0e18")], -4.5, 4.5, -1.0, 4.6)
    for z in (1.0, 3.3):
        bgflat(f"junta_h{z}", cena.rect(-4.5, z - 0.006, 4.5, z + 0.006), "#0b1019", y_wall - 0.012, fog=False)
    cena.poly_mesh("piso_cela", [(-9, -7, -0.004), (9, -7, -0.004), (9, y_wall, -0.004), (-9, y_wall, -0.004)], fogmat("piso_cela_m", "#080b13"))
    wx0, wx1, wz0, wz1 = 0.8, 1.8, 2.05, 2.95
    bgflat("jan_moldura", cena.rect(wx0 - 0.07, wz0 - 0.07, wx1 + 0.07, wz1 + 0.07), "#05070c", y_wall - 0.03, fog=False)
    bgflat("jan_ceu", cena.rect(wx0, wz0, wx1, wz1), "#3a5584", y_wall - 0.04, 1.2, fog=False)
    sets.glow("jan_lua", "#b9d6ff", 1.1, ((wx0 + wx1) / 2, y_wall - 0.06, (wz0 + wz1) / 2), power=2.2, strength=0.8)
    for i in range(4):
        xb = wx0 + (wx1 - wx0) * (i + 0.5) / 4
        bgflat(f"jan_barra{i}", cena.rect(xb - 0.02, wz0 - 0.07, xb + 0.02, wz1 + 0.07), "#05070c", y_wall - 0.07, fog=False)
    P2 = dict(P, shaft="#a9cdff")
    cena.shafts(P2, [(1.55, y_wall - 0.4, 1.0, 3.8, 0.16)], frames, top_z=2.55)
    cena.ground_disc("luz_chao", 1.0, 0.5, cena.amat("luz_chao_m", "#a9cdff", 1.0, 0.18, ("radial", 1.6)), (-0.3, 0.5, 0.004))
    g = txt("pcc_wall", "PCC", 0.62, "#26304a", (pcc_x, y_wall - 0.05, 2.0), None, ink=None)
    g.rotation_euler = (0, math.radians(-4), 0)
    grade("grade_frente", -3.2, 3.2, -1.0, 4.4, -1.1, "#04060b", n=20, w=0.035, rails=1, x_off=0.16)
    cena.dust(dict(dust="#ffffff"), 45, (-0.8, 2.2), frames, size=(0.004, 0.01), z_range=(0.3, 3.0), y_range=(-0.6, 1.2), alpha=0.45)
    led = cena.disc("vigia_led", 0.0001, cena.amat("vigia_led_m", "#ff2d3d", 1.0, 0.0), (0, 5, -5))
    return dict(led=led, cam=None, y_wall=y_wall)

# ---------------------------------------------------------------- a escada em cena (céu por altura, nuvens, cidade distante, chão)
STAIR_SKY = {
    "noite":    [(-8, "#05080f"), (3, "#0b1226"), (8, "#17214a"), (16, "#4a3d78"), (24, "#8a5f8e"), (40, "#ffb98a")],
    "alvorada": [(-8, "#0a1020"), (3, "#141d3d"), (8, "#323a78"), (14, "#8a6aa0"), (20, "#ffb98a"), (36, "#ffe3b8")],
    "dourado":  [(-8, "#e9a56e"), (2, "#f4b87a"), (8, "#ffd08f"), (16, "#ffe6b0"), (30, "#fff3d6")],
    "noite_fria": [(-8, "#03050b"), (4, "#070c18"), (10, "#0b1328"), (24, "#080d1d"), (60, "#03050b")],
}


def cena_escada(c, mood="noite", gray=False, f_end=None, numbers=True, sun_x=24.0, stars=True):
    """cenário da escada: devolve (P, dict com raiz da escada, posições úteis)"""
    f1 = f_end or c["f1"]
    P = dict(cena.PAL["alvorada"] if mood in ("noite", "alvorada") else (cena.PAL["dourado"] if mood == "dourado" else cena.PAL["drama"]))
    sets.FOG.update(color=P["haze"], near=10.0, far=520.0, max=0.85 if mood != "dourado" else 0.6)
    cena.sky(P, bpy.context.scene)
    rnd = random.Random(8)
    # sol (dourado/alvorada) ou lua (noite)
    if mood == "dourado":
        sol(P, (sun_x, 520, 95.0), r=34.0, glow=230, rays=True)
    elif mood in ("alvorada",):
        sol(P, (sun_x + 6, 520, 4.0), r=18.0, glow=120, rays=False)
    else:
        cena.disc("lua", 16.0, cena.amat("lua_m", "#dfe9ff", 2.2, 1.0), (-70, 600, 120))
        sets.glow("lua_g", "#7fa0d8", 110, (-70, 590, 120), power=2.3, strength=0.5)
    if stars and mood in ("noite", "alvorada", "noite_fria"):
        for i in range(70):
            cena.disc(f"estrela{i}", rnd.uniform(0.5, 1.3), cena.amat("estrela_m", "#ffffff", 3.0, 0.9), (rnd.uniform(-400, 400), 650, rnd.uniform(60, 340)))
    skyline(P, rnd, -14, 22, layers=((6.0, 260.0, 10, 28), (3.0, 110.0, 8, 20)), win=True, lit=0.12 if mood != "dourado" else 0.0, sun_side=-1)
    # nuvens em três profundidades
    cc = {"noite": ("#2a3560", "#1a2142"), "alvorada": ("#7a6a9e", "#4a4278"), "dourado": ("#fff1d8", "#f2c08a"), "noite_fria": ("#101a30", "#0a1224")}[mood]
    for i in range(16):
        y = rnd.choice((25.0, 60.0, 120.0)); x = rnd.uniform(-40, 70) * (y / 40) ** 0.5; z = rnd.uniform(1.0, 11.0) * (y / 25) ** 0.6
        cl = cloud(f"nuvem{i}", x, z, y, rnd.uniform(1.6, 3.4) * (y / 25) ** 0.9, cc[0], cc[1])
        cl.location.x = x; key(cl, "location", 1, "LINEAR"); cl.location.x = x - 0.5 * (f1 / 24.0) * (y / 30.0) ** 0.5; key(cl, "location", f1 + 30, "LINEAR")
    chao(P, color={"noite": "#0d1326", "alvorada": "#1c2040", "dourado": "#c98f6a", "noite_fria": "#080c18"}[mood], y0=-60.0, y1=700.0)
    cena.mist(P, [(1.5, 1.6, 0.45, 0.04), (8.0, 2.6, 0.4, -0.03), (22.0, 5.0, 0.4, 0.02)], f1 + 30)
    root, parts = escada(0.6, gray=gray, numbers=numbers)
    cena.dust(P, 70, (-4, 14), f1 + 30, size=(0.01, 0.026), z_range=(0.2, 8.0), y_range=(-4.0, 3.0), color=P["dust"], alpha=0.45)
    return P, dict(root=root, parts=parts)


def interrogacao(name, x, z, s=1.0, y=0.5):
    """o '?' dourado que pisca no alto da escada"""
    root = empty(name, None, (x, y, z)); root.scale = (s, s, s)
    sets.glow(name + "_g", "#ffd24a", 1.8, (x, y + 0.05, z), power=2.0, strength=1.2)
    txt(name + "_t", "?", 1.7, "#ffd24a", (0, -0.01, 0), root, ink="#5a3a00", ow=0.06)
    return root


def jaula(name, x, z, w=0.3, h=0.9, y=-0.2):
    """cela individual (grade) para colocar na frente de uma figura"""
    root = empty(name, None, (x, y, z))
    inked(name + "_t", cena.rect(-w / 2 - 0.02, h - 0.05, w / 2 + 0.02, h + 0.02), "#2a3040", root, w=0.008)
    inked(name + "_b", cena.rect(-w / 2 - 0.02, -0.03, w / 2 + 0.02, 0.04), "#2a3040", root, w=0.008)
    for i in range(4):
        xb = -w / 2 + w * (i + 0.5) / 4
        inked(f"{name}_g{i}", cena.rect(xb - 0.012, 0.0, xb + 0.012, h), "#6a7490", root, loc=(0, -0.002, 0), w=0.006)
    return root


# ================================================================ NÍVEL 3: mapa, regras, tribunal, régua da pena
def mapa(name, x, z, w=2.3, h=3.0, seed=4, area_blocks=((1, 1), (2, 1), (1, 2), (2, 2), (3, 2), (2, 3))):
    """mapa de bairro visto de cima (ruas, quarteirões, praça e rio) num cartaz de parede; devolve (raiz, área, bandeira)"""
    rnd = random.Random(seed)
    root = empty(name, None, (x, 0.0, z))
    inked(name + "_fundo", rrect(-w / 2, -h / 2, w / 2, h / 2, 0.05, 5), "#efe3c4", root, w=0.03, shade=0.05, shade_color="#d6c7a3")
    # rio (curva azul) e ruas
    rio = smooth([(-w / 2 + 0.04, -0.5), (-0.3, -0.35), (0.25, -0.62), (w / 2 - 0.04, -0.4), (w / 2 - 0.04, -0.62), (0.2, -0.85), (-0.35, -0.6), (-w / 2 + 0.04, -0.72)], 6)
    poly(name + "_rio", rio, "#8ec4e8", -0.002, root)
    cols, rows = 4, 5
    bw, bh = (w - 0.3) / cols, (h - 0.5) / rows
    centers = {}
    paleta = ["#d9a88f", "#c9b48a", "#e0c9a0", "#b9c79a", "#d4b4a0", "#cfc2a8"]
    for i in range(cols):
        for j in range(rows):
            cx = -w / 2 + 0.15 + bw * (i + 0.5); cz = -h / 2 + 0.25 + bh * (j + 0.5) + 0.0
            if cz < -0.35 and rnd.random() < 0.7:
                continue
            col = paleta[rnd.randrange(len(paleta))] if rnd.random() > 0.14 else "#a9cf8a"   # algumas praças verdes
            poly(f"{name}_q{i}_{j}", rrect(cx - bw / 2 + 0.035, cz - bh / 2 + 0.035, cx + bw / 2 - 0.035, cz + bh / 2 - 0.035, 0.02, 2), col, -0.003, root)
            centers[(i, j)] = (cx, cz)
    return root, centers, dict(bw=bw, bh=bh)


def anel_poly(name, pts, d, color, y, parent):
    """moldura: faixa de largura d em volta do polígono (sem preencher o miolo)"""
    if area(pts) < 0:
        pts = pts[::-1]
    out = offset(pts, d)
    bm = bmesh.new(); n = len(pts)
    a = [bm.verts.new((x, y, z)) for x, z in pts]; b = [bm.verts.new((x, y, z)) for x, z in out]
    for i in range(n):
        bm.faces.new((a[i], a[(i + 1) % n], b[(i + 1) % n], b[i]))
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free(); me.materials.append(FM(color))
    o = bpy.data.objects.new(name, me); bpy.context.scene.collection.objects.link(o); o.parent = parent
    return o


def area_realce(name, parent, centers, blocks, bw, bh, color="#e2364b"):
    """realce vermelho dos quarteirões da 'área' (preenchimento translúcido + contorno grosso)"""
    root = empty(name, parent, (0, -0.02, 0))
    xs0 = min(centers[b][0] for b in blocks) - bw / 2; xs1 = max(centers[b][0] for b in blocks) + bw / 2
    zs0 = min(centers[b][1] for b in blocks) - bh / 2; zs1 = max(centers[b][1] for b in blocks) + bh / 2
    pts = rrect(xs0, zs0, xs1, zs1, 0.05, 4)
    mesh_pts(name + "_fill", pts, cena.amat(name + "_fm", color, 1.4, 0.30), root, -0.004)
    anel_poly(name + "_o", pts, 0.05, color, -0.006, root)
    return root, ((xs0 + xs1) / 2, (zs0 + zs1) / 2)


def bandeira(name, loc, s=1.0, parent=None):
    """alfinete/bandeira vermelha que marca 'a sua área'"""
    root = empty(name, parent, loc); root.scale = (s, s, s)
    inked(name + "_m", cena.rect(-0.015, 0.0, 0.015, 0.6), "#3b3f55", root, w=0.008)
    inked(name + "_b", [(0.015, 0.6), (0.34, 0.5), (0.015, 0.4)], "#e2364b", root, loc=(0, -0.002, 0), w=0.012, shade=0.02, shade_color="#a82336")
    return root


def prancheta(name, loc, s=1.0):
    """prancheta com três regras (caixa + linha); devolve (raiz, [posições das caixas])"""
    root = empty(name, None, loc); root.scale = (s, s, s)
    inked(name + "_b", rrect(-0.62, -0.85, 0.62, 0.85, 0.05, 4), "#8a5a3a", root, w=0.025, shade=0.04, shade_color="#6a4228", rim=0.014, rim_color="#b98258")
    inked(name + "_p", rrect(-0.5, -0.74, 0.5, 0.66, 0.02, 3), "#f6f1e4", root, loc=(0, -0.002, 0), w=0.01)
    inked(name + "_c", rrect(-0.18, 0.66, 0.18, 0.84, 0.03, 3), "#b9bfce", root, loc=(0, -0.004, 0), w=0.012)
    txt(name + "_t", "REGRAS", 0.14, "#e2364b", (0, -0.008, 0.5), root, ink=None)
    boxes = []
    for i in range(3):
        zc = 0.2 - 0.34 * i
        inked(f"{name}_k{i}", rrect(-0.4, zc - 0.07, -0.26, zc + 0.07, 0.015, 2), "#ffffff", root, loc=(0, -0.004, 0), w=0.008)
        poly(f"{name}_l{i}", cena.rect(-0.18, zc - 0.022, 0.36, zc + 0.022), "#8a8fa0", -0.006, root)
        boxes.append((-0.33, zc))
    return root, boxes


def xis(name, loc, s=1.0, color="#e2364b"):
    """X grosso (carimbo de 'quebrou')"""
    root = empty(name, None, loc); root.scale = (s, s, s)
    for k, sg in enumerate((1, -1)):
        poly(f"{name}_{k}", stroke([(-0.16 * sg, -0.16), (0.16 * sg, 0.16)], 0.035), color, -0.01, root)
    return root


def tribunal(name, loc, s=1.0):
    """fachada de tribunal (frontão, colunas, degraus)"""
    root = empty(name, None, loc); root.scale = (s, s, s)
    inked(name + "_base", rrect(-1.3, -0.05, 1.3, 0.18, 0.02, 3), "#b9bfce", root, w=0.018, shade=0.03, shade_color="#8b92a6")
    inked(name + "_deg", rrect(-1.15, 0.18, 1.15, 0.34, 0.02, 3), "#cdd2de", root, w=0.018)
    for i in range(5):
        xc = -0.9 + 0.45 * i
        inked(f"{name}_col{i}", rrect(xc - 0.09, 0.34, xc + 0.09, 1.3, 0.03, 3), "#e9ecf4", root, w=0.014, shade=0.025, shade_color="#b3b9cb")
    inked(name + "_arq", rrect(-1.15, 1.3, 1.15, 1.46, 0.02, 3), "#cdd2de", root, w=0.018)
    inked(name + "_front", [(-1.25, 1.46), (1.25, 1.46), (0.0, 2.05)], "#e9ecf4", root, w=0.02, shade=0.04, shade_color="#b3b9cb")
    poly(name + "_balanca", circle(0.0, 1.72, 0.1, 18), "#8b92a6", -0.006, root)
    return root


def martelo(name, loc, s=1.0):
    """martelo de juiz com o pivô no cabo (gira em torno do ponto 'loc'); cabo para a esquerda, cabeça no fim.
    Devolve (pivô, bloco). Em rotação 0 a cabeça encosta no bloco."""
    pivo = empty(name, None, loc); pivo.scale = (s, s, s)
    inked(name + "_cabo", rrect(-1.25, -0.045, 0.0, 0.045, 0.04, 3), "#a06b42", pivo, w=0.015, shade=0.015, shade_color="#7a4c2c", rim=0.01, rim_color="#d09a6a")
    inked(name + "_cab", rrect(-1.78, -0.3, -1.22, 0.3, 0.07, 4), "#8a5a3a", pivo, loc=(0, -0.002, 0), w=0.02, shade=0.03, shade_color="#5e3b22", rim=0.015, rim_color="#c88f60")
    for xb in (-1.7, -1.3):
        poly(f"{name}_cinta{xb}", cena.rect(xb - 0.03, -0.3, xb + 0.03, 0.3), "#d8c27e", -0.006, pivo)
    bloco = empty(name + "_bloco", None, (loc[0] - 1.5 * s, loc[1], loc[2] - 0.3 * s - 0.15 * s))
    inked(name + "_bl", rrect(-0.62 * s, -0.15 * s, 0.62 * s, 0.15 * s, 0.05 * s, 4), "#5e3b22", bloco, w=0.02, shade=0.02, shade_color="#3f2616")
    return pivo, bloco


def caveira(name, loc, s=1.0):
    """caveira chapada (osso claro, olhos e nariz pretos)"""
    root = empty(name, None, loc); root.scale = (s, s, s)
    inked(name + "_cr", circle(0, 0.12, 0.5, 40), "#f1ecde", root, w=0.03, shade=0.07, shade_color="#cbc4ae", rim=0.03, rim_color="#ffffff")
    inked(name + "_mand", rrect(-0.3, -0.52, 0.3, -0.14, 0.08, 4), "#f1ecde", root, loc=(0, -0.002, 0), w=0.025, shade=0.04, shade_color="#cbc4ae")
    for sx in (-1, 1):
        poly(f"{name}_o{sx}", ellipse(0.2 * sx, 0.1, 0.14, 0.17, 24), "#0d1020", -0.008, root)
    poly(name + "_n", [(-0.05, -0.08), (0.05, -0.08), (0.0, 0.02)], "#0d1020", -0.008, root)
    for k in range(4):
        poly(f"{name}_d{k}", cena.rect(-0.2 + 0.133 * k - 0.012, -0.5, -0.2 + 0.133 * k + 0.012, -0.2), "#0d1020", -0.008, root)
    return root


def regua_pena(name, loc, w=2.9):
    """régua da pena: do verde (advertência) ao vermelho (morte). Devolve (raiz, marcador, x_ini, x_fim)"""
    root = empty(name, None, loc)
    segs = ["#4cc38a", "#a6d65a", "#ffd24a", "#ff8a3d", "#e2364b"]
    x0 = -w / 2
    inked(name + "_fundo", rrect(-w / 2 - 0.05, -0.2, w / 2 + 0.05, 0.2, 0.2, 7), "#0d1020", root, w=0.0)
    for i, c in enumerate(segs):
        xa = x0 + w * i / 5; xb = x0 + w * (i + 1) / 5
        pts = rrect(xa + 0.012, -0.16, xb - 0.012, 0.16, 0.14 if i in (0, 4) else 0.02, 6)
        poly(f"{name}_s{i}", pts, c, -0.004, root)
    txt(name + "_adv", "ADVERTÊNCIA", 0.13, "#ffffff", (x0 + 0.0, -0.006, -0.46), root, align="LEFT", ink=INK, ow=0.08)
    marc = empty(name + "_marc", root, (x0 + 0.1, -0.012, 0.44))
    inked(name + "_mk", [(-0.15, 0.0), (0.15, 0.0), (0.0, -0.24)], "#ffffff", marc, w=0.025)
    return root, marc, x0 + 0.1, w / 2 - 0.1


def dim(cam, name, color="#000000", dist=0.6):
    """plano de lavagem preso à câmera (escurece, clareia ou pinta a tela); a opacidade se anima com wash()"""
    cam_d = cam.data
    m = cena.amat(name + "_m", color, 1.0, 0.0)
    w, h = dist * 24 / 35 * 1.15, dist * 24 / 35 * 16 / 9 * 1.15
    o = cena.poly_mesh(name, [(-w / 2, 0, -h / 2), (w / 2, 0, -h / 2), (w / 2, 0, h / 2), (-w / 2, 0, h / 2)], m)
    o.parent = cam; o.location = (0, 0, -dist); o.rotation_euler = (PI / 2, 0, 0)
    node = [n for n in m.node_tree.nodes if n.type == "MATH" and n.operation == "MULTIPLY"][0]
    return o, node.inputs[1]


def wash(sock, keys, interp="LINEAR"):
    """anima a opacidade do plano de lavagem: keys = [(quadro, alfa)]"""
    for f, a in keys:
        sock.default_value = a; sock.keyframe_insert("default_value", frame=f)


# ================================================================ NÍVEL 4: organograma
def icone_pacote(name, parent, loc, s=1.0):
    root = empty(name, parent, loc); root.scale = (s, s, s)
    inked(name + "_b", rrect(-0.2, -0.15, 0.2, 0.15, 0.015, 3), "#c99a5b", root, w=0.012, shade=0.03, shade_color="#9a6f3a", rim=0.012, rim_color="#e8c58e")
    poly(name + "_t", cena.rect(-0.035, -0.15, 0.035, 0.15), "#f0dcae", -0.004, root)
    return root


def icone_maleta(name, parent, loc, s=1.0):
    root = empty(name, parent, loc); root.scale = (s, s, s)
    poly(name + "_al", stroke([(-0.09, 0.14), (-0.09, 0.22), (0.09, 0.22), (0.09, 0.14)], 0.02), "#2a2f45", 0.0012, root)
    inked(name + "_b", rrect(-0.22, -0.15, 0.22, 0.15, 0.03, 3), "#4a4f6a", root, w=0.012, shade=0.03, shade_color="#2f3348", rim=0.012, rim_color="#8088b0")
    poly(name + "_l", cena.rect(-0.22, -0.01, 0.22, 0.01), "#2a2f45", -0.004, root)
    poly(name + "_f", rrect(-0.03, -0.045, 0.03, 0.04, 0.01, 2), "#d8c27e", -0.006, root)
    return root


def icone_curtir(name, parent, loc, s=1.0):
    """coração dentro de um balão de notificação (rede social)"""
    root = empty(name, parent, loc); root.scale = (s, s, s)
    inked(name + "_b", rrect(-0.2, -0.14, 0.2, 0.14, 0.07, 5), "#3d7bff", root, w=0.012, shade=0.03, shade_color="#2a57c4", rim=0.012, rim_color="#8fb4ff")
    poly(name + "_tail", [(-0.1, -0.12), (-0.02, -0.12), (-0.12, -0.25)], "#3d7bff", 0.0012, root)
    poly(name + "_h", [(x * 4.2, z * 4.2 + 0.0) for x, z in heart(0.034)], "#ffffff", -0.005, root)
    return root


def orgcard(name, loc, w, h, label, color, icon, size=0.13, fill="#ffffff", txt_c="#1a1f35", shade_c="#d9dce8", rim_c="#ffffff"):
    """cartão do organograma: faixa colorida à esquerda, ícone e nome"""
    root = empty(name, None, loc)
    inked(name + "_c", rrect(-w / 2, -h / 2, w / 2, h / 2, 0.06, 5), fill, root, w=0.018, shade=0.03, shade_color=shade_c, rim=0.012, rim_color=rim_c)
    inked(name + "_f", rrect(-w / 2, -h / 2, -w / 2 + 0.2, h / 2, 0.06, 5), color, root, loc=(0, -0.002, 0), w=0.0)
    ic = icon(name + "_i", root, (-w / 2 + 0.55, -0.01, 0.0), 1.15)
    txt(name + "_t", label, size, txt_c, (-w / 2 + 0.95, -0.006, 0.0), root, align="LEFT", ink=None)
    return root


# ================================================================ NÍVEL 5: postos, pilha de dinheiro e Everests
BOMBA = [  # (polígono local em m, cor)  — bomba de combustível de 0,9 m de altura, centrada na base
    (rrect(-0.2, 0.0, 0.2, 0.08, 0.02, 2), "#2b2f45"),
    (rrect(-0.17, 0.08, 0.17, 0.82, 0.04, 3), "#e2364b"),
    (rrect(-0.12, 0.5, 0.12, 0.74, 0.02, 2), "#cfeaff"),
    (cena.rect(-0.17, 0.4, 0.17, 0.44), "#a82336"),
    (rrect(0.17, 0.3, 0.27, 0.6, 0.03, 2), "#2b2f45"),
    (cena.rect(-0.17, 0.78, 0.17, 0.82), "#ffd24a"),
]


def campo_icones(name, template, pos, scale=1.0, jitter=0.0, seed=1):
    """uma malha com muitas cópias de um desenho (template = [(polígono, cor)]) nas posições (x, z)"""
    rnd = np.random.default_rng(seed)
    verts, faces, mats = [], [], []
    colors = []
    for poly_, col in template:
        if col not in colors:
            colors.append(col)
    for (x, z) in pos:
        sc = scale * (1 + jitter * (rnd.random() - 0.5))
        for poly_, col in template:
            b = len(verts)
            for (px, pz) in poly_:
                verts.append((x + px * sc, 0.0, z + pz * sc))
            faces.append(tuple(range(b, b + len(poly_)))); mats.append(colors.index(col))
    me = bpy.data.meshes.new(name); me.from_pydata(verts, [], faces)
    for col in colors:
        me.materials.append(FM(col))
    me.polygons.foreach_set("material_index", np.array(mats, dtype=np.int32)); me.update()
    o = bpy.data.objects.new(name, me); bpy.context.scene.collection.objects.link(o)
    return o


def montanha_cel(name, loc, w, h, n, tone):
    """célula 'Everest' da régua de altura: montanha com neve e o número"""
    root = empty(name, None, loc)
    inked(name + "_c", cena.rect(-w / 2, 0, w / 2, h), tone, root, w=0.0)
    mt = [(-w * 0.45, 0.04 * h), (-w * 0.1, 0.78 * h), (0.0, 0.9 * h), (w * 0.12, 0.7 * h), (w * 0.45, 0.04 * h)]
    inked(name + "_m", mt, "#7f8ba8", root, w=0.1, shade=0.4, shade_color="#5b6785", rim=0.2, rim_color="#a7b3cf")
    poly(name + "_neve", [(-w * 0.09, 0.78 * h * 0.92), (0.0, 0.9 * h), (w * 0.115, 0.7 * h), (w * 0.05, 0.66 * h), (-w * 0.01, 0.72 * h), (-w * 0.06, 0.66 * h)], "#ffffff", -0.02, root)
    txt(name + "_n", str(n), h * 0.22, "#ffffff", (-w * 0.33, -0.05, h * 0.82), root, ink=INK, ow=0.08)
    return root


def pasta_investigacao(name, loc, s=1.0):
    """pasta de processo com lupa por cima"""
    root = empty(name, None, loc); root.scale = (s, s, s)
    inked(name + "_asp", rrect(-0.6, -0.5, 0.6, 0.5, 0.05, 4), "#c99a4a", root, loc=(0, 0.002, 0), w=0.02)
    inked(name + "_aba", rrect(-0.6, 0.44, -0.12, 0.62, 0.05, 4), "#c99a4a", root, loc=(0, 0.002, 0), w=0.02)
    inked(name + "_pap", rrect(-0.5, -0.4, 0.5, 0.42, 0.02, 3), "#f6f1e4", root, loc=(0, 0.0, 0.04), w=0.012)
    for i in range(4):
        poly(f"{name}_lin{i}", cena.rect(-0.38, 0.22 - 0.16 * i, 0.38 - 0.1 * (i % 2), 0.255 - 0.16 * i), "#8a8fa0", -0.004, root)
    inked(name + "_fr", rrect(-0.55, -0.48, 0.55, -0.22, 0.04, 3), "#e2364b", root, loc=(0, -0.002, 0), w=0.0)
    txt(name + "_t", "INVESTIGAÇÃO", 0.1, "#ffffff", (0, -0.008, -0.35), root, ink=None)
    lupa = empty(name + "_lupa", root, (0.45, -0.02, -0.15))
    poly(name + "_cabo", stroke([(0.2, -0.2), (0.5, -0.5)], 0.055), "#2a2f45", -0.004, lupa)
    inked(name + "_aro", circle(0, 0, 0.36, 36), "#2a2f45", lupa, w=0.012)
    poly(name + "_vid", circle(0, 0, 0.29, 36), "#bfe3ff", -0.006, lupa)
    poly(name + "_br", stroke([(-0.16, 0.08), (-0.08, 0.17)], 0.025), "#ffffff", -0.008, lupa)
    return root, lupa


def etiqueta(name, texto, loc, s=1.0, cor="#e2364b", size=0.15, w=0.5):
    """pílula de texto (ex.: PCC)"""
    root = empty(name, None, loc); root.scale = (s, s, s)
    inked(name + "_p", rrect(-w, -size * 0.95, w, size * 0.95, size * 0.8, 6), cor, root, w=0.02, shade=0.03, shade_color=_mix(cor, "#000000", 0.35), rim=0.012, rim_color=_mix(cor, "#ffffff", 0.45))
    txt(name + "_t", texto, size, "#ffffff", (0, -0.008, 0), root, ink=_mix(cor, "#000000", 0.55), ow=0.05)
    return root


def pilha_notas(name, x, w, n, h=0.5, z0=0.0, y=0.3):
    """pilha de maços de notas de R$ 100 (azul), de baixo para cima, numa malha só"""
    tmpl = [(cena.rect(-w / 2, 0.0, w / 2, h), "#3f7fc2"), (cena.rect(-w / 2, h - 0.045, w / 2, h), "#2b5c95"),
            (cena.rect(-w * 0.07, 0.0, w * 0.07, h - 0.045), "#f3e9c9"), (cena.rect(-w / 2, 0.0, -w / 2 + w * 0.05, h), "#6aa6e0")]
    pos = [(0.0, z0 + h * k) for k in range(n)]
    o = campo_icones(name, tmpl, pos, 1.0)
    o.location = (x, y, 0.0)
    return o
