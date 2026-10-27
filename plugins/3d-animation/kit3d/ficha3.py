"""Ficha do protagonista v3 (rosto como foco). Cada página = grade de células com legenda + faixa de título.
blender -b -P ficha3.py -- --page expressoes|giro|poses|detalhes --out DIR ; depois ficha_montar.py"""
import sys, os, math, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy, lib
from lib import *
from puppet2d import flatmat
from char2d import rrect, ellipse, mesh_pts
from heroi import Heroi, PAL

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
arg = lambda n, d=None: argv[argv.index(n) + 1] if n in argv else d
PAGE = arg("--page", "expressoes"); OUT = arg("--out", "/tmp/ficha3")
os.makedirs(os.path.join(OUT, PAGE), exist_ok=True)
reset(600, 600, 24, 16)
sc = lib.scene
sc.world.node_tree.nodes["Background"].inputs[0].default_value = (*srgb("#221c30"), 1)
sc.world.node_tree.nodes["Background"].inputs[1].default_value = 1.0
FB = bpy.data.fonts.load("/System/Library/Fonts/Supplemental/Arial Black.ttf")
FR = bpy.data.fonts.load("/System/Library/Fonts/Supplemental/Arial Bold.ttf")
WHITE = flatmat("lbl_white", "#f3efe6"); SUB = flatmat("lbl_sub", "#9d92b8"); CARD = flatmat("card", "#2d2541")
LINE = flatmat("line", "#3d3456"); BAND = flatmat("bandm", "#1a1526")
cd = bpy.data.cameras.new("cam"); cd.type = "ORTHO"
cam = bpy.data.objects.new("cam", cd); sc.collection.objects.link(cam); sc.camera = cam
cam.rotation_euler = (math.radians(90), 0, 0)
CELLS = []; SLOT = [0]


NICE = {"AMEACADOR": "AMEAÇADOR", "PARANOICO": "PARANOICO", "SARCASTICO": "SARCÁSTICO", "PANICO": "PÂNICO", "SORRISAO": "SORRISÃO", "TRISTEABERTA": "TRISTE ABERTA", "CORACAO": "CORAÇÃO", "ALIVIO": "ALÍVIO", "CETICA": "CÉTICA"}


def label(text, x, z, size, m=WHITE, font=FB):
    text = NICE.get(text, text)
    t = lib.text(f"lbl{len(CELLS)}_{abs(hash(text)) % 9999}", text, size, m, None, (x, -0.3, z), font)
    t.rotation_euler = (math.pi / 2, 0, 0)


def cell(name, view, pose, cx_off, cz, w, h, px, title, label_z=None, extra=None):
    x0 = SLOT[0] * 12.0; SLOT[0] += 1
    t = Heroi(f"{PAGE}{len(CELLS)}", view)
    p = dict(pose); p["x"] = x0 + p.get("x", 0.0)
    t.pose(1, p, "CONSTANT")
    cx = x0 + cx_off
    mesh_pts(f"card{len(CELLS)}", rrect(cx - w * 0.65, cz - h / 2 - 0.3, cx + w * 0.65, cz + h / 2 + 0.3, 0.001), CARD, None, 0.5)
    zl = label_z if label_z is not None else cz - h / 2 + 0.11 * h
    if h < 1.2:
        mesh_pts(f"band{len(CELLS)}", rrect(cx - w * 0.47, zl - 0.075 * h, cx + w * 0.47, zl + 0.07 * h, 0.03), BAND, None, -0.25)
    label(title, cx, zl, 0.075 * h if h < 1.2 else 0.085)
    if extra:
        extra(x0)
    CELLS.append(dict(name=name, cx=cx, cz=cz, w=w, h=h, px=px))


def render_cells():
    for i, c in enumerate(CELLS):
        sc.render.resolution_x, sc.render.resolution_y = c["px"]
        cd.ortho_scale = max(c["w"], c["h"]); cam.location = (c["cx"], -10, c["cz"])
        sc.frame_set(1); sc.render.filepath = os.path.join(OUT, PAGE, f"{i:03d}_{c['name']}.png")
        bpy.ops.render.render(write_still=True)


HEAD = (0.06, 1.47, 0.82, 0.88, (520, 560))     # enquadramento de rosto: cx, cz, w, h, px

if PAGE == "expressoes":
    EX = [
        ("neutro", {}),
        ("feliz", dict(eye="feliz", mouth="sorriso", browup=0.01)),
        ("rindo", dict(eye="feliz", mouth="sorrisao", head=-8, browup=0.015)),
        ("esperto", dict(lid="esperto", mouth="lado", browtilt=0.012, brow=-6)),
        ("confiante", dict(lid="esperto", lidv=0.55, mouth="sorriso", brow=-8, head=-5)),
        ("curioso", dict(browtilt=0.016, mouth="pequena", head=7, look=(0.5, 0.3))),
        ("surpreso", dict(wide=0.6, browup=0.02, mouth="o")),
        ("choque", dict(eye="ponto", browup=0.03, mouth="grito", extras=("!",))),
        ("assustado", dict(wide=0.9, brow=18, browup=0.015, mouth="nervosa", extras=("suor",))),
        ("nervoso", dict(lid="triste", lidv=0.35, brow=20, mouth="nervosa", extras=("suor",))),
        ("triste", dict(lid="triste", brow=22, mouth="triste", head=9)),
        ("chorando", dict(lid="triste", lidv=0.9, brow=25, mouth="tristeaberta", extras=("lagrima",), head=6)),
        ("bravo", dict(lid="bravo", brow=-22, mouth="triste")),
        ("furioso", dict(lid="bravo", brow=-30, mouth="dentes", extras=("raiva",))),
        ("desconfiado", dict(lid="apertado", lidv=0.75, browtilt=-0.012, brow=-8, mouth="lado")),
        ("entediado", dict(lid="sono", browup=-0.012, mouth="reta", head=6)),
        ("pensativo", dict(look=(0.6, 0.8), browtilt=0.012, mouth="pequena", head=-7)),
        ("envergonhado", dict(lid="sorriso", brow=16, mouth="nervosa", extras=("vergonha",), look=(0.0, -0.6), head=8)),
        ("confuso", dict(browtilt=0.02, brow=8, mouth="lado", extras=("?",), look=(-0.5, 0.6))),
        ("nocaute", dict(eye="x", mouth="o", mouthv=0.5, brows=False, head=10)),
        ("apaixonado", dict(eye="coracao", mouth="sorriso", browup=0.015, extras=("vergonha",))),
        ("empolgado", dict(eye="estrela", mouth="sorrisao", browup=0.02, extras=("brilho",))),
        ("desanimado", dict(lid="sono", lidv=0.8, brow=18, mouth="triste", extras=("sombra",), head=10)),
        ("aliviado", dict(eye="alivio", mouth="sorriso", brow=10, head=-4)),
    ]
    for nm, p in EX:
        cx, cz, w, h, px = HEAD
        cell(nm, "q", p, cx, cz, w, h, px, nm.upper())

elif PAGE == "expressoes2":
    EX2 = [
        ("ganancioso", dict(eye="cifrao", mouth="sorrisao", browup=0.015, head=-5, extras=("brilho",))),
        ("arrogante", dict(lid="esperto", lidv=0.6, mouth="sorriso", brow=-6, browtilt=0.016, head=-10)),
        ("paranoico", dict(wide=0.5, look=(-0.9, 0.1), mouth="nervosa", brow=16, extras=("suor",))),
        ("ameacador", dict(lid="bravo", lidv=0.75, brow=-26, mouth="sorriso", head=8)),
        ("desesperado", dict(wide=1.0, brow=26, browup=0.02, mouth="tristeaberta", extras=("suor",), head=-4)),
        ("derrotado", dict(eye="fechado", brow=24, mouth="triste", head=14, extras=("sombra",))),
        ("culpado", dict(lid="triste", lidv=0.5, look=(0.5, -0.8), brow=18, mouth="lado", head=10)),
        ("determinado", dict(lid="bravo", lidv=0.45, brow=-14, mouth="reta", head=3)),
        ("sarcastico", dict(lid="sono", lidv=0.55, browtilt=0.02, brow=6, mouth="lado", head=-4)),
        ("sonhador", dict(eye="alivio", mouth="sorriso", head=-10, browup=0.012)),
        ("panico", dict(eye="ponto", brow=30, browup=0.03, mouth="grito", extras=("suor", "!"))),
        ("frio", dict(lid="sono", lidv=0.62, brow=-8, browup=-0.008, mouth="reta")),
    ]
    for nm, p in EX2:
        cx, cz, w, h, px = HEAD
        cell(nm, "q", p, cx, cz, w, h, px, nm.upper())

elif PAGE == "giro":
    def lines(x0):
        for z in (0.0, 0.45, 0.86, 1.3, 1.62, 1.82):
            mesh_pts(f"ln{x0}{z}", [(x0 - 0.75, z - 0.003), (x0 + 0.75, z - 0.003), (x0 + 0.75, z + 0.003), (x0 - 0.75, z + 0.003)], LINE, None, 0.3)
    for nm, v, tt in (("frente", "front", "FRENTE"), ("tres_quartos", "q", "3/4"), ("perfil", "side", "PERFIL"), ("costas", "back", "COSTAS")):
        cell(nm, v, {}, 0.0, 0.84, 1.5, 2.4, (700, 1120), tt, -0.17, lines)
    x0 = SLOT[0] * 12.0; SLOT[0] += 1
    mesh_pts("cardp", rrect(x0 - 1.0, 0.84 - 1.5, x0 + 1.0, 0.84 + 1.5, 0.001), CARD, None, 0.5)
    label("PALETA", x0, 1.86, 0.1)
    sw = [("hoodie", "MOLETOM"), ("dark", "CAPUZ / SOMBRA"), ("skin", "CABEÇA / CORPO"), ("white", "OLHOS / BOCA"),
          ("rim", "BORDA DE LUZ"), ("blush", "VERGONHA"), ("sweat", "SUOR / LÁGRIMA"), ("anger", "RAIVA")]
    for k, (k2, nm) in enumerate(sw):
        z = 1.6 - k * 0.235
        mesh_pts(f"swo{k}", ellipse(x0 - 0.45, z, 0.095, 0.095, 40), flatmat("swo", "#0b0d16"), None, 0.25)
        mesh_pts(f"sw{k}", ellipse(x0 - 0.45, z, 0.085, 0.085, 40), flatmat("swm" + k2, PAL[k2]), None, 0.2)
        label(nm, x0 + 0.12, z + 0.03, 0.05)
        label(PAL[k2].upper(), x0 + 0.12, z - 0.05, 0.042, SUB, FR)
    CELLS.append(dict(name="paleta", cx=x0, cz=0.84, w=1.5, h=2.4, px=(700, 1120)))

elif PAGE == "poses":
    PO = [
        ("parado", "q", {}),
        ("andando", "side", dict(legF=26, shinF=-6, footF=8, legB=-24, shinB=-28, armF=-22, foreF=14, armB=20, foreB=18, lean=4)),
        ("correndo", "side", dict(lean=16, chest=4, legF=55, shinF=-25, legB=-42, shinB=-85, armF=-60, foreF=95, armB=55, foreB=80,
                                    handF="punho", handB="punho", mouth="dentes", lid="bravo", lidv=0.5, brow=-12, z=0.05)),
        ("pulando", "front", dict(z=0.22, armF=150, foreF=10, armB=150, foreB=10, legF=25, shinF=-55, legB=25, shinB=-55,
                                   handF="aberta", handB="aberta", eye="feliz", mouth="sorrisao", browup=0.02)),
        ("apontando", "q", dict(armF=95, foreF=4, handF="aponta", lid="esperto", lidv=0.7, mouth="lado", brow=-8)),
        ("pensando", "q", dict(armF=70, foreF=135, handF="punho", armB=30, foreB=80, head=-6, look=(0.5, 0.8), browtilt=0.012, mouth="pequena")),
        ("ombros", "front", dict(armF=32, foreF=108, armB=32, foreB=108, wristF=20, wristB=20, handF="aberta", handB="aberta",
                                  head=6, lid="sono", lidv=0.4, mouth="lado", browup=0.02)),
        ("comemorando", "front", dict(armF=160, foreF=5, armB=160, foreB=5, handF="punho", handB="punho", eye="feliz", mouth="sorrisao", z=0.08)),
        ("medo", "q", dict(lean=-14, chest=-6, armF=45, foreF=125, handF="aberta", armB=35, foreB=120, handB="aberta",
                           legF=10, legB=-18, shinB=-10, wide=1.0, brow=20, browup=0.02, mouth="grito", extras=("suor",))),
        ("sentado", "side", dict(z=-0.44, legF=88, shinF=-88, legB=84, shinB=-86, lean=4, armF=40, foreF=30, armB=35, foreB=30, mouth="reta")),
        ("cansado", "q", dict(lean=12, chest=6, head=10, armF=16, foreF=4, armB=12, foreB=4, lid="sono", mouth="triste", brow=15, extras=("sombra",))),
        ("acenando", "front", dict(armF=150, foreF=30, handF="aberta", eye="feliz", mouth="sorriso", head=-4, browup=0.01)),
    ]
    for nm, v, p in PO:
        def seat(x0, nm=nm):
            if nm == "sentado":
                mesh_pts(f"seat{x0}", rrect(x0 - 0.34, 0.0, x0 + 0.1, 0.42, 0.03), flatmat("seatm", "#3f3358"), None, 0.2)
        cz = 1.02 if nm in ("pulando", "comemorando", "acenando") else 0.88
        cell(nm, v, p, 0.0, cz, 1.45, 2.45, (620, 1040), nm.upper(), cz - 1.05, seat)

elif PAGE == "detalhes":
    for mk in ("reta", "sorriso", "triste", "lado", "nervosa", "pequena", "gato", "o", "grito", "falando", "sorrisao", "tristeaberta", "dentes"):
        cell("boca_" + mk, "q", dict(mouth=mk, brows=False), 0.085, 1.56, 0.62, 0.62, (330, 330), mk.upper())
    for ek, p in (("normal", {}), ("sono", dict(lid="sono")), ("esperto", dict(lid="esperto")), ("bravo", dict(lid="bravo")),
                  ("triste", dict(lid="triste")), ("apertado", dict(lid="apertado")), ("sorriso", dict(lid="sorriso")),
                  ("arregalado", dict(wide=1.0)), ("feliz", dict(eye="feliz")), ("alivio", dict(eye="alivio")),
                  ("fechado", dict(eye="fechado")), ("ponto", dict(eye="ponto")), ("x", dict(eye="x")),
                  ("coracao", dict(eye="coracao")), ("estrela", dict(eye="estrela"))):
        cell("olho_" + ek, "q", dict(p, brows=False), 0.085, 1.6, 0.62, 0.62, (330, 330), ek.upper())
    for bk, p in (("neutra", {}), ("levantada", dict(browup=0.025)), ("brava", dict(brow=-26)), ("preocupada", dict(brow=24)),
                  ("cetica", dict(browtilt=0.02)), ("baixa", dict(browup=-0.015))):
        cell("sobr_" + bk, "q", p, 0.085, 1.62, 0.62, 0.62, (330, 330), bk.upper().replace("CETICA", "CÉTICA"))

TITLES = {"giro": ("PROTAGONISTA  ·  GIRO", "corpo simples; o rosto é quem atua"),
          "expressoes2": ("EXPRESSÕES · HISTÓRIAS", "ganância, poder, paranoia, ameaça, desespero, derrota, culpa e frieza"),
          "expressoes": ("EXPRESSÕES", "olho sem pupila + sobrancelha + boca + um elemento (suor, lágrima, vergonha, raiva, sombra, brilho)"),
          "poses": ("POSES", "regra única: ângulo positivo = para onde ele olha"),
          "detalhes": ("PEÇAS DO ROSTO", "bocas, olhos e sobrancelhas trocáveis (a mão é sempre arredondada)")}
WIDTH = {"giro": 5 * 700 + 4 * 16 + 64, "expressoes": 6 * 520 + 5 * 16 + 64, "expressoes2": 6 * 520 + 5 * 16 + 64, "poses": 6 * 620 + 5 * 16 + 64, "detalhes": 7 * 330 + 6 * 16 + 64}
hx = -200.0
tt, st = TITLES[PAGE]
label(tt, hx, 0.12, 0.34); label(st, hx, -0.22, 0.13, SUB, FR)
mesh_pts("hdr_line", rrect(hx - 0.6, -0.45, hx + 0.6, -0.43, 0.005), flatmat("hdr_acc", PAL["hoodie"]), None, 0.0)
render_cells()
sc.render.resolution_x, sc.render.resolution_y = WIDTH[PAGE], 260
cd.ortho_scale = WIDTH[PAGE] / 260 * 1.2; cam.location = (hx, -10, 0.0)
sc.render.filepath = os.path.join(OUT, PAGE, "zz_header.png"); bpy.ops.render.render(write_still=True)
