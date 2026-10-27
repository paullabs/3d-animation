"""Recursos semânticos (o que a pessoa entende sem pensar): tamanho real das coisas, comparação de escala,
níveis e hierarquia.
- money_block(): pilha de dinheiro com o TAMANHO FÍSICO REAL (calculado pelo valor e pelas medidas da cédula)
- label(): número/palavra grande que "estoura" na tela (passa do ponto e assenta)
- level_badge(): selo "NÍVEL X" + barra de 5 níveis presa à câmera
- pyramid(): pirâmide da hierarquia com o andar atual destacado
Tudo plano, de frente para a câmera (estilo 2D), com leve "face de cima" para dar volume."""
import bpy, math
import lib
from lib import srgb, key, empty
from char2d import rrect, mesh_pts
import cena

# medidas das cédulas (m). Cédula de R$100 da 2ª família: 156 x 70 mm; US$100: 156 x 66,3 mm; espessura ~0,11 mm
NOTES = {
    "BRL100": dict(w=0.156, h=0.070, t=0.00011, value=100, body="#3f7fc2", line="#2b5c95", band="#f3e9c9", top="#7fb0e0", side="#2f639c"),
    "USD100": dict(w=0.156, h=0.0663, t=0.00011, value=100, body="#4f9a5f", line="#367443", band="#f3e9c9", top="#8cc792", side="#3a7a49"),
}


def money_volume(amount, note="BRL100"):
    n = NOTES[note]; count = amount / n["value"]
    return count * n["w"] * n["h"] * n["t"], count


def cube_side(amount, note="BRL100"):
    vol, _ = money_volume(amount, note)
    return vol ** (1.0 / 3.0)


def pop(o, f, s=1.0, frames=7, over=0.16):
    """aparece com estouro: 0 -> passa do ponto -> assenta"""
    for ff, v in ((f - 1, 0.0001), (f, 0.0001), (f + int(frames * 0.55), s * (1 + over)), (f + int(frames * 0.8), s * (1 - over * 0.35)), (f + frames, s)):
        o.scale = (v, v, v); key(o, "scale", ff, "BEZIER")


def grow_up(o, f, frames=10, over=0.08):
    """cresce de baixo para cima (a pilha "sobe"), com leve passar do ponto"""
    for ff, v in ((f - 1, 0.0001), (f, 0.0001), (f + int(frames * 0.7), 1 + over), (f + frames, 1.0)):
        o.scale = (1, 1, v); key(o, "scale", ff, "BEZIER")


def money_block(name, amount, x, y, note="BRL100", side=None, f_in=None, mode="grow"):
    """bloco de dinheiro com tamanho real (cubo do volume das cédulas), base em (x, y, 0).
    Desenhado com frente, topo e lateral (oblíquo), grade de maços e cintas."""
    N = NOTES[note]
    s = side or cube_side(amount, note)
    root = empty(name, None, (x, y, 0))
    def m(k, col, st=1.0):
        return cena.amat(f"money_{note}_{k}", col, st, 1.0)
    dx, dz = 0.38 * s, 0.26 * s                      # deslocamento oblíquo da face de cima/lateral
    mesh_pts(name + "_front", [(-s / 2, 0), (s / 2, 0), (s / 2, s), (-s / 2, s)], m("body", N["body"]), root, 0.0)
    mesh_pts(name + "_top", [(-s / 2, s), (s / 2, s), (s / 2 + dx, s + dz), (-s / 2 + dx, s + dz)], m("top", N["top"]), root, 0.004)
    mesh_pts(name + "_side", [(s / 2, 0), (s / 2 + dx, dz), (s / 2 + dx, s + dz), (s / 2, s)], m("side", N["side"]), root, 0.004)
    # maços: grade de linhas + cintas claras no meio de cada maço
    rows = max(3, min(14, int(s / 0.025)))
    cols = max(2, min(10, int(s / 0.05)))
    lw = max(0.0015, s * 0.006)
    for r in range(1, rows):
        z = s * r / rows
        mesh_pts(f"{name}_r{r}", [(-s / 2, z - lw), (s / 2, z - lw), (s / 2, z + lw), (-s / 2, z + lw)], m("line", N["line"]), root, -0.002)
    for c in range(cols):
        xc = -s / 2 + s * (c + 0.5) / cols; bw = s / cols * 0.16
        mesh_pts(f"{name}_b{c}", [(xc - bw, 0), (xc + bw, 0), (xc + bw, s), (xc - bw, s)], m("band", N["band"]), root, -0.003)
    if f_in is not None:
        (grow_up if mode == "grow" else pop)(root, f_in)
    return root, s


def label(name, text, x, y, z, size, f_in=None, color="#ffffff", outline="#0d1020", parent=None, align="CENTER"):
    """texto grande com contorno escuro (lê em qualquer fundo) que estoura ao aparecer"""
    root = empty(name, parent, (x, y, z))
    t = lib.text(name + "_t", text, size, cena.amat(f"lbl_{color}", color, 1.0, 1.0), root, (0, -0.002, 0), lib.font())
    t.rotation_euler = (math.pi / 2, 0, 0); t.data.align_x = align
    o = lib.text(name + "_o", text, size, cena.amat(f"lbl_{outline}", outline, 1.0, 1.0), root, (0, 0.0, 0), lib.font())
    o.rotation_euler = (math.pi / 2, 0, 0); o.data.offset = size * 0.07; o.data.align_x = align
    if f_in is not None:
        pop(root, f_in)
    return root


def hide_at(o, f):
    o.scale = o.scale.copy(); key(o, "scale", f - 1, "BEZIER")
    o.scale = (0.0001, 0.0001, 0.0001); key(o, "scale", f + 4, "BEZIER")


def level_badge(cam, level, total, f_in, f_out=None, title="NÍVEL", accent="#ff3b4f", dist=1.0, top=0.47):
    """selo 'NÍVEL X' no alto da tela + barra de níveis (os já alcançados acesos). Preso à câmera (lente 35, sensor 24)."""
    k = dist * 0.5
    root = empty(f"badge{level}", cam, (0, top * dist, -dist))
    def flat_xy(name, pts, color, z):
        o = mesh_pts(name, pts, cena.amat(f"badge_{color}", color, 1.0, 1.0), root, 0.0)
        o.rotation_euler = (-math.pi / 2, 0, 0); o.location = (0, 0, z)
        return o
    flat_xy(f"badge{level}_bg", rrect(-0.24 * k, -0.06 * k, 0.24 * k, 0.06 * k, 0.03 * k), "#0d1020", 0.0)
    flat_xy(f"badge{level}_acc", rrect(-0.24 * k, -0.06 * k, -0.205 * k, 0.06 * k, 0.012 * k), accent, 0.001)
    t = lib.text(f"badge{level}_t", f"{title} {level}", 0.07 * k, cena.amat("badge_txt", "#ffffff", 1.0, 1.0), root,
                 (0.015 * k, -0.002 * k, 0.002), lib.font())
    segw = 0.085 * k; gap = 0.014 * k; tot = total * segw + (total - 1) * gap
    for i in range(total):
        x0 = -tot / 2 + i * (segw + gap)
        col = accent if i < level else "#3a3550"
        flat_xy(f"badge{level}_seg{i}", rrect(x0, -0.115 * k, x0 + segw, -0.093 * k, 0.009 * k), col, 0.001)
    pop(root, f_in, 1.0, 8, 0.12)
    if f_out:
        hide_at(root, f_out)
    return root


def pyramid(name, x, y, base_w, height, labels, colors=None, f_in=None):
    """pirâmide da hierarquia: andares de baixo (largo) para cima (estreito). Devolve os andares (para destacar)."""
    root = empty(name, None, (x, y, 0))
    n = len(labels); tiers = []
    colors = colors or ["#5b5470", "#6a5f82", "#7c6b95", "#9278a8", "#c8a24a"]
    gap = 0.04
    for i, txt in enumerate(labels):
        z0 = height * i / n; z1 = height * (i + 1) / n - gap
        w0 = base_w * (1 - i / n); w1 = base_w * (1 - (i + 1) / n)
        o = mesh_pts(f"{name}_t{i}", [(-w0 / 2, z0), (w0 / 2, z0), (w1 / 2, z1), (-w1 / 2, z1)],
                     cena.amat(f"{name}_c{i}", colors[i % len(colors)], 1.0, 1.0), root, 0.0)
        lb = lib.text(f"{name}_l{i}", txt, min(0.16, height / n * 0.38), cena.amat("pyr_txt", "#ffffff", 1.0, 1.0), root,
                      (0, -0.004, (z0 + z1) / 2), lib.font())
        lb.rotation_euler = (math.pi / 2, 0, 0)
        tiers.append(o)
    if f_in is not None:
        grow_up(root, f_in, 14)
    return root, tiers


def highlight(o, f, frames=8, color="#ffd24a"):
    """acende um andar (troca para a cor de destaque com um pequeno pulo)"""
    m = cena.amat("hl_" + color, color, 1.4, 1.0)
    for ff, s in ((f - 1, 1.0), (f + 3, 1.08), (f + frames, 1.0)):
        o.scale = (s, 1, s); key(o, "scale", ff, "BEZIER")
    # troca de material via slot ativo não anima; usamos uma cópia por cima que aparece
    hi = o.copy(); hi.data = o.data.copy(); hi.data.materials.clear(); hi.data.materials.append(m)
    bpy.context.scene.collection.objects.link(hi); hi.parent = o.parent; hi.location = (o.location.x, o.location.y - 0.002, o.location.z)
    hi.scale = (0.0001, 1, 0.0001); key(hi, "scale", f - 1, "CONSTANT")
    hi.scale = (1, 1, 1); key(hi, "scale", f, "CONSTANT")
    return hi
