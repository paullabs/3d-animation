"""Ficha do vídeo do reflexo: elenco de frente, elenco de 3/4 e objetos (pequenos e de cenário), cada prancha num PNG com os rótulos em JSON.
blender -b -P ficha_reflexo.py -- MODO SAIDA.png     MODO = elenco_frente | elenco_q | pequenos | cenario"""
import os, sys, json, math
os.environ["VOZ_NOVA"] = ""
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy, lib
from lib import *
import cena, props, frente
import elenco_reflexo as ER, objetos_reflexo as OR
from anim import Timeline
from prod_pcc import finish
from bpy_extras.object_utils import world_to_camera_view

argv = sys.argv[sys.argv.index("--") + 1:]
MODO, SAIDA = argv[0], argv[1]
FUNDO, CHAO = "#c9c2b4", "#a99f8e"

EXPR = {"voce_casa": dict(lid="esperto", lidv=0.55, wide=0.3, mouth="pequena", look=(1.0, -0.3)),
        "goleiro": dict(lid="esperto", lidv=0.4, brow=-14, mouth="reta", look=(1.0, -0.1)),
        "velocista": dict(lid="apertado", lidv=0.55, brow=-10, mouth="reta", look=(1.0, 0.0)),
        "atacante": dict(lid="bravo", brow=-22, mouth="reta", look=(1.0, -0.2)),
        "menino": dict(wide=0.6, browup=0.02, mouth="o", look=(1.0, 0.3)),
        "torcedor": dict(eye="feliz", mouth="sorrisao", browup=0.012)}
NOMES = {"voce_casa": "Você (em casa)", "goleiro": "Você (goleiro)", "velocista": "Você (velocista)", "atacante": "Atacante",
         "menino": "Menino pegador\nde bolas", "torcedor": "Torcedor"}


def fundo_neutro(w=40):
    bpy.context.scene.world.node_tree.nodes["Background"].inputs[0].default_value = (*srgb(FUNDO), 1)
    cena.poly_mesh("parede", [(-w, 3.0, -1), (w, 3.0, -1), (w, 3.0, 12), (-w, 3.0, 12)], props.FM(FUNDO))
    cena.poly_mesh("chao", [(-w, -20, 0), (w, -20, 0), (w, 3.0, 0), (-w, 3.0, 0)], props.FM(CHAO))


def elenco(view):
    rot = []
    for i, (nome, fn) in enumerate(ER.ELENCO):
        x = -3.25 + i * 1.3
        H = fn(nome, view, rim="#ffe4c8")
        w = empty(nome + "_inv", None, (x, 0, 0)); H.root.parent = w
        e = ER.ESCALA.get(nome, 1.0); w.scale = (e, e, e)
        tl = Timeline(H, 1, 12, 24); tl.stand(1, 12, 0.0)
        if view == "q":
            tl.face(1, 1.0, **EXPR[nome])
        else:
            tl.face(1, 1.0, lid="esperto", lidv=0.55, mouth="pequena")
        finish(H, tl, 1, 12)
        if view == "front":
            frente.bracos(H, 1, 12, [(1, dict(shF=5, elF=0, shB=5, elB=0))])
        cena.contact_shadow(H, dict(shadow="#8a8070"))
        rot.append((NOMES[nome], (x, 0, -0.12)))
    return rot


def pequenos():
    lista = [("Copo com água\n(0,11 m)", lambda x: OR.copo("copo", (x, 0, 0.2), 7.0), -4.5),
             ("Régua de 30 cm\n(azul = 30 cm, vermelho = 3 mm)", lambda x: OR.regua("regua", (x, 0, 0.1), 4.6), -3.0),
             ("Bola de futebol", lambda x: OR.bola("bola", (x, 0, 0.1), 4.2), -1.5),
             ("Luvas de goleiro", lambda x: OR.luvas("luvas", (x, 0, 0.1), 2.8), 0.15),
             ("Medidor de reação", lambda x: OR.cronometro("cron", (x, 0, 0.25), 2.4), 1.85),
             ("Bloco de largada", lambda x: OR.bloco_largada("bloco", (x, 0, 0.3), 2.3), 3.55),
             ("Taça (a Copa)", lambda x: OR.taca("taca", (x, 0, 0.1), 2.3), 5.1)]
    rot = []
    for nome, f, x in lista:
        f(x); rot.append((nome, (x, 0, -0.12)))
    return rot


def cenario():
    rot = []
    OR.mesa_cozinha("mesa", (-7.0, 0.4, 0.0), 1.7); OR.copo("copo_mesa", (-7.5, 0.45, 0.7 * 1.7 + 0.045 * 1.7), 3.0); rot.append(("Mesa de cozinha", (-7.0, 0, -0.12)))
    OR.gol("gol", (-3.6, 1.2, 0.0), 0.42); rot.append(("Gol (7,32 x 2,44 m)", (-3.6, 0, -0.12)))
    OR.camera_cabo("camcabo", (0.0, 0.8, 0.15), 1.5); rot.append(("Câmera de TV\npendurada por cabos", (0.0, 0, -0.12)))
    OR.telao_replay("telao", (3.2, 1.3, 0.1), 1.05); rot.append(("Telão do estádio\n(repetição)", (3.2, 0, -0.12)))
    OR.torcida("torc", (6.7, 1.0, 0.0), 1.15, n=5); rot.append(("Torcida (silhuetas)", (6.7, 0, -0.12)))
    return rot


if MODO.startswith("elenco"):
    W_, H_, ORT = 3100, 1400, 8.0
elif MODO == "pequenos":
    W_, H_, ORT = 3300, 1300, 12.5
else:
    W_, H_, ORT = 4300, 1400, 17.0
lib.reset(W_, H_, 24, 32)
sc = bpy.context.scene
fundo_neutro()
cam_d = bpy.data.cameras.new("cam"); cam = bpy.data.objects.new("cam", cam_d); sc.collection.objects.link(cam); sc.camera = cam
rotulos = elenco("front" if MODO == "elenco_frente" else "q") if MODO.startswith("elenco") else (pequenos() if MODO == "pequenos" else cenario())
cam_d.type = "ORTHO"; cam_d.ortho_scale = ORT
cam.location = (0.0 if MODO != "pequenos" else 0.3, -10.0, 0.95 if MODO.startswith("elenco") else 0.9); cam.rotation_euler = (math.radians(90), 0, 0)
sc.frame_set(1); bpy.context.view_layer.update()
pos = []
for nome, loc in rotulos:
    co = world_to_camera_view(sc, cam, Vector(loc))
    pos.append((nome, co.x, 1 - co.y))
json.dump(pos, open(SAIDA + ".json", "w"), ensure_ascii=False)
sc.render.filepath = SAIDA
bpy.ops.render.render(write_still=True)
