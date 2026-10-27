"""Ficha do personagem: cada página vira uma grade de células renderizadas (com legenda) + faixa de título.
blender -b -P ficha.py -- --page giro|expressoes|poses|detalhes --out DIR
Depois: python3 ficha_montar.py DIR  (junta as células em páginas PNG com ffmpeg)"""
import sys, os, math, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy, lib
from lib import *
from puppet2d import flatmat
from char2d import Toon, PAL, rrect, ellipse, mesh_pts

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
arg = lambda n, d=None: argv[argv.index(n) + 1] if n in argv else d
PAGE = arg("--page", "giro"); OUT = arg("--out", "/tmp/ficha")
os.makedirs(os.path.join(OUT, PAGE), exist_ok=True)
reset(600, 600, 24, 16)
sc = lib.scene
w = sc.world.node_tree.nodes["Background"]; w.inputs[0].default_value = (*srgb("#221c30"), 1); w.inputs[1].default_value = 1.0
FB = bpy.data.fonts.load("/System/Library/Fonts/Supplemental/Arial Black.ttf")
FR = bpy.data.fonts.load("/System/Library/Fonts/Supplemental/Arial Bold.ttf")
WHITE = flatmat("lbl_white", "#f3efe6"); SUB = flatmat("lbl_sub", "#9d92b8"); CARD = flatmat("card", "#2d2541")
LINE = flatmat("line", "#3d3456")
cd = bpy.data.cameras.new("cam"); cd.type = "ORTHO"
cam = bpy.data.objects.new("cam", cd); sc.collection.objects.link(cam); sc.camera = cam
cam.rotation_euler = (math.radians(90), 0, 0)
CELLS = []
SLOT = [0]


def label(text, x, z, size=0.08, m=WHITE, font=FB):
    t = lib.text(f"lbl{len(CELLS)}_{text[:6]}", text, size, m, None, (x, -0.3, z), font)
    t.rotation_euler = (math.pi / 2, 0, 0)
    return t


def card(x, z0, z1, w):
    mesh_pts(f"card{len(CELLS)}", rrect(x - w / 2, z0, x + w / 2, z1, 0.001), CARD, None, 0.5)


def cell(name, view, pose, cx_off, cz, span_w, span_h, px_w, px_h, title, sub=None, scale=1.0, extra=None, label_z=None):
    """cria um personagem num lugar próprio e registra a câmera da célula"""
    x0 = SLOT[0] * 12.0; SLOT[0] += 1
    t = Toon(f"{PAGE}{len(CELLS)}", view)
    t.root.scale = (scale,) * 3
    p = dict(pose); p["x"] = x0 + p.get("x", 0.0)
    t.pose(1, p, "CONSTANT")
    cx = x0 + cx_off
    card(cx, cz - span_h / 2 - 0.3, cz + span_h / 2 + 0.3, span_w * 1.3)
    zl = label_z if label_z is not None else cz - span_h / 2 + 0.11 * span_h
    if span_h < 1.2:
        mesh_pts(f"band{len(CELLS)}", rrect(cx - span_w * 0.47, zl - 0.075 * span_h, cx + span_w * 0.47, zl + 0.07 * span_h, 0.03),
                 flatmat("bandm", "#1a1526"), None, -0.25)
    label(title, cx, zl, 0.075 * span_h if span_h < 1.2 else 0.085)
    if sub:
        label(sub, cx, cz - span_h / 2 + 0.06 * span_h, 0.04 * span_h if span_h < 1.2 else 0.05, SUB, FR)
    if extra:
        extra(x0)
    CELLS.append(dict(name=name, cx=cx, cz=cz, w=span_w, h=span_h, px=(px_w, px_h)))
    return t


def render_cells():
    for i, c in enumerate(CELLS):
        sc.render.resolution_x, sc.render.resolution_y = c["px"]
        cd.ortho_scale = max(c["w"], c["h"])
        cam.location = (c["cx"], -10, c["cz"])
        sc.frame_set(1)
        sc.render.filepath = os.path.join(OUT, PAGE, f"{i:03d}_{c['name']}.png")
        bpy.ops.render.render(write_still=True)


# ------------------------------------------------------------------------------------------ páginas
if PAGE == "giro":
    def lines(x0):
        for z, nm in ((0.0, "chão"), (0.45, "joelho"), (0.86, "quadril"), (1.3, "ombro"), (1.62, "cabeça"), (1.82, "topo")):
            mesh_pts(f"ln{x0}{nm}", [(x0 - 0.75, z - 0.003), (x0 + 0.75, z - 0.003), (x0 + 0.75, z + 0.003), (x0 - 0.75, z + 0.003)], LINE, None, 0.3)
    for nm, v, tt in (("frente", "front", "FRENTE"), ("tres_quartos", "q", "3/4"), ("perfil", "side", "PERFIL"), ("costas", "back", "COSTAS")):
        cell(nm, v, {}, 0.0, 0.84, 1.5, 2.4, 700, 1120, tt, None, 1.0, lines, -0.17)
    # paleta
    x0 = SLOT[0] * 12.0; SLOT[0] += 1
    sw = [("hoodie", "MOLETOM"), ("dark", "SOMBRA / CAPUZ"), ("band", "BARRA / PUNHO"), ("skin", "CABEÇA / PELE"),
          ("white", "OLHOS / BOCA"), ("sole", "SOLA"), ("rim", "BORDA DE LUZ")]
    card(x0, 0.84 - 1.5, 0.84 + 1.5, 1.9)
    label("PALETA", x0, 1.8, 0.1)
    for k, (key_, nm) in enumerate(sw):
        z = 1.55 - k * 0.27
        mesh_pts(f"sw{k}", ellipse(x0 - 0.45, z, 0.09, 0.09, 40), flatmat("swm" + key_, PAL[key_]), None, 0.2)
        mesh_pts(f"swo{k}", ellipse(x0 - 0.45, z, 0.1, 0.1, 40), flatmat("swo", "#0b0d16"), None, 0.25)
        t = lib.text(f"swt{k}", nm, 0.055, WHITE, None, (x0 + 0.12, -0.3, z + 0.03), FB); t.rotation_euler = (math.pi / 2, 0, 0)
        t = lib.text(f"swh{k}", PAL[key_].upper(), 0.045, SUB, None, (x0 + 0.12, -0.3, z - 0.05), FR); t.rotation_euler = (math.pi / 2, 0, 0)
    CELLS.append(dict(name="paleta", cx=x0, cz=0.84, w=1.5, h=2.4, px=(700, 1120)))

elif PAGE == "expressoes":
    EX = [
        ("neutro", {}, None),
        ("feliz", dict(eye="feliz", mouth="sorriso"), None),
        ("rindo", dict(eye="feliz", mouth="sorrisao", head=-8), None),
        ("esperto", dict(lid="esperto", mouth="lado"), None),
        ("confiante", dict(lid="esperto", lidv=0.55, mouth="sorriso", head=-5), None),
        ("curioso", dict(pupils=True, look=(0.7, 0.4), mouth="pequena", head=7), None),
        ("surpreso", dict(wide=0.6, pupils=True, mouth="o"), None),
        ("choque", dict(wide=1.0, pupils=True, mouth="grito", extras=("!",)), None),
        ("assustado", dict(wide=0.8, pupils=True, look=(-0.7, 0.1), mouth="nervosa", extras=("suor",)), None),
        ("nervoso", dict(lid="triste", lidv=0.5, mouth="nervosa", extras=("suor",)), None),
        ("triste", dict(lid="triste", mouth="triste", head=9), None),
        ("chorando", dict(lid="triste", mouth="triste", head=6, extras=("lagrima",)), None),
        ("bravo", dict(lid="bravo", mouth="triste"), None),
        ("furioso", dict(lid="bravo", mouth="dentes", extras=("raiva",)), None),
        ("desconfiado", dict(lid="apertado", lidv=0.8, mouth="lado", head=-3), None),
        ("entediado", dict(lid="sono", mouth="reta", head=6), None),
        ("pensativo", dict(pupils=True, look=(0.6, 0.9), mouth="pequena", head=-7), None),
        ("envergonhado", dict(lid="sorriso", pupils=True, look=(0.0, -0.8), mouth="nervosa", extras=("vergonha",), head=8), None),
        ("confuso", dict(pupils=True, look=(-0.5, 0.8), mouth="lado", extras=("?",), head=-6), None),
        ("nocaute", dict(eye="x", mouth="o", mouthv=0.5, head=10), None),
    ]
    for nm, p, _ in EX:
        cell(nm, "q", p, 0.06, 1.47, 0.95, 1.02, 520, 560, nm.upper())

elif PAGE == "poses":
    PO = [
        ("parado", "q", {}),
        ("andando", "side", dict(legF=28, shinF=-6, footF=10, legB=-26, shinB=-30, armF=-24, armB=22, foreF=-18, foreB=-14, lean=4)),
        ("correndo", "side", dict(lean=16, chest=4, legF=55, shinF=-25, legB=-40, shinB=-85, armF=-65, foreF=-95, armB=55, foreB=-80,
                                    handF="punho", handB="punho", mouth="dentes", lid="bravo", lidv=0.6, z=0.05)),
        ("pulando", "front", dict(z=0.22, armF=150, foreF=10, armB=150, foreB=10, legF=25, shinF=-55, legB=25, shinB=-55,
                                   handF="aberta", handB="aberta", eye="feliz", mouth="sorrisao")),
        ("apontando", "q", dict(armF=95, foreF=4, handF="aponta", lid="esperto", lidv=0.7, mouth="lado", lean=-2)),
        ("pensando", "q", dict(armF=22, foreF=128, handF="punho", armB=12, foreB=78, head=-6, pupils=True, look=(0.6, 0.9), mouth="pequena")),
        ("ombros", "front", dict(armF=32, foreF=108, armB=32, foreB=108, wristF=20, wristB=20, handF="aberta", handB="aberta",
                                  head=6, lid="sono", lidv=0.4, mouth="lado")),
        ("comemorando", "front", dict(armF=160, foreF=5, armB=160, foreB=5, handF="punho", handB="punho", eye="feliz", mouth="sorrisao", z=0.08)),
        ("medo", "q", dict(lean=-14, chest=-6, armF=62, foreF=100, handF="aberta", armB=48, foreB=96, handB="aberta",
                           legF=10, legB=-18, shinB=-10, wide=1.0, pupils=True, mouth="grito", extras=("suor",))),
        ("sentado", "side", dict(z=-0.44, legF=-88, shinF=88, legB=-82, shinB=84, lean=4, armF=-30, foreF=-50, armB=-25, foreB=-45, mouth="reta")),
        ("cansado", "q", dict(lean=18, chest=10, head=18, armF=-18, foreF=6, armB=-22, lid="sono", mouth="triste")),
        ("acenando", "front", dict(armF=150, foreF=30, handF="aberta", eye="feliz", mouth="sorriso", head=-4)),
    ]
    for nm, v, p in PO:
        def seat(x0, nm=nm):
            if nm == "sentado":
                mesh_pts(f"seat{x0}", rrect(x0 - 0.32, 0.0, x0 + 0.12, 0.42, 0.03), flatmat("seatm", "#3f3358"), None, 0.2)
        cz = 1.02 if nm in ("pulando", "comemorando", "acenando") else 0.88
        cell(nm, v, p, 0.0, cz, 1.45, 2.45, 620, 1040, nm.upper(), None, 1.0, seat, cz - 1.05)

elif PAGE == "detalhes":
    for hk, tt in (("descanso", "DESCANSO"), ("punho", "PUNHO"), ("aponta", "APONTANDO"), ("aberta", "ABERTA"), ("joinha", "JOINHA")):
        p = dict(armF=90, foreF=0, handF=hk, armB=-4)
        x0 = SLOT[0] * 12.0
        cell("mao_" + hk, "q", p, 0.68, 1.29, 0.6, 0.6, 420, 420, tt)
    for mk in ("reta", "sorriso", "triste", "lado", "nervosa", "pequena", "o", "grito", "falando", "sorrisao", "dentes"):
        cell("boca_" + mk, "q", dict(mouth=mk), 0.07, 1.555, 0.62, 0.62, 330, 330, mk.upper())
    for ek, p in (("normal", {}), ("pupilas", dict(pupils=True)), ("sono", dict(lid="sono")), ("esperto", dict(lid="esperto")),
                  ("bravo", dict(lid="bravo")), ("triste", dict(lid="triste")), ("apertado", dict(lid="apertado")),
                  ("sorriso", dict(lid="sorriso")), ("arregalado", dict(wide=1.0, pupils=True)), ("feliz", dict(eye="feliz")),
                  ("fechado", dict(eye="fechado")), ("x", dict(eye="x"))):
        cell("olho_" + ek, "q", p, 0.07, 1.6, 0.62, 0.62, 330, 330, ek.upper())

TITLES = {"giro": ("PROTAGONISTA  ·  GIRO", "as 4 vistas desenhadas, proporções e paleta"),
          "expressoes": ("EXPRESSÕES", "olhos com pálpebra por forma, bocas trocáveis e extras (suor, lágrima, vergonha, raiva, ! e ?)"),
          "poses": ("POSES", "o mesmo boneco em ação; câmera só desliza, o boneco nunca gira em 3D"),
          "detalhes": ("MÃOS · BOCAS · OLHOS", "peças trocáveis do rosto e das mãos")}
WIDTH = {"giro": 5 * 700 + 4 * 16 + 64, "expressoes": 5 * 520 + 4 * 16 + 64, "poses": 6 * 620 + 5 * 16 + 64, "detalhes": 6 * 330 + 5 * 16 + 64}
hx = -200.0
tt, st = TITLES[PAGE]
t = lib.text("hdr_t", tt, 0.34, WHITE, None, (hx, -0.3, 0.12), FB); t.rotation_euler = (math.pi / 2, 0, 0)
t = lib.text("hdr_s", st, 0.13, SUB, None, (hx, -0.3, -0.22), FR); t.rotation_euler = (math.pi / 2, 0, 0)
mesh_pts("hdr_line", rrect(hx - 0.6, -0.45, hx + 0.6, -0.43, 0.005), flatmat("hdr_acc", PAL["hoodie"]), None, 0.0)
HW = WIDTH[PAGE]; HH = 260
render_cells()
sc.render.resolution_x, sc.render.resolution_y = HW, HH
cd.ortho_scale = HW / HH * 1.2; cam.location = (hx, -10, 0.0)
sc.render.filepath = os.path.join(OUT, PAGE, "zz_header.png"); bpy.ops.render.render(write_still=True)
json.dump([dict(name=c["name"], px=c["px"]) for c in CELLS], open(os.path.join(OUT, PAGE, "cells.json"), "w"))
