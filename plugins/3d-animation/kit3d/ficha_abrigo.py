"""Ficha do vídeo "O abrigo": elenco de frente, elenco de 3/4, objetos pequenos (a e b) e cenário, cada prancha num PNG com os rótulos em JSON.
blender -b -P ficha_abrigo.py -- MODO SAIDA.png     MODO = elenco_frente | elenco_q | pequenos_a | pequenos_b | cenario"""
import os, sys, json, math
os.environ["VOZ_NOVA"] = ""
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy, lib
from lib import *
import cena, props, frente
import elenco_abrigo as EA, objetos_abrigo as OA, elenco3d_abrigo as E3
from anim import Timeline
from prod_pcc import finish
from bpy_extras.object_utils import world_to_camera_view

argv = sys.argv[sys.argv.index("--") + 1:]
MODO, SAIDA = argv[0], argv[1]
FUNDO, CHAO = "#9a9c8e", "#7a7c6e"
props.DESAT = 0.5; props.DESAT_TO = "#8a8a78"
props.ACCENT |= {"#8e3a30", "#a8342c", "#8e302b", "#ffe3a0", "#ffd77a", "#fff8dc", "#64211f", "#b65048"}

EXPR = {"ze": dict(lid="esperto", lidv=0.45, brow=-14, mouth="reta", look=(1.0, -0.1)),
        "lu": dict(lid="esperto", lidv=0.4, brow=-8, mouth="reta", look=(1.0, -0.2)),
        "lu_fraca": dict(lid="esperto", lidv=0.6, browup=0.01, mouth="reta", look=(1.0, 0.1)),
        "rita": dict(lid="esperto", lidv=0.4, browup=0.012, mouth="reta", look=(1.0, 0.2)),
        "padeira": dict(lid="esperto", lidv=0.3, browup=0.02, mouth="reta", look=(1.0, 0.0)),
        "mercado": dict(lid="esperto", lidv=0.5, brow=-8, mouth="reta", look=(1.0, -0.1))}
NOMES = {"ze": "Zé\n(tranca a porta)", "lu": "Lu\n(jaqueta jeans)", "lu_fraca": "Lu meses depois\n(cinza, magra)", "rita": "Rita\n(a menor)",
         "padeira": "Dona da padaria\n(lá fora)", "mercado": "Rapaz do mercado\n(lá fora)", "pipoca": "Pipoca\n(porquinha-da-índia)"}


def fundo_neutro(w=40):
    bpy.context.scene.world.node_tree.nodes["Background"].inputs[0].default_value = (*srgb(FUNDO), 1)
    cena.poly_mesh("parede", [(-w, 3.0, -1), (w, 3.0, -1), (w, 3.0, 12), (-w, 3.0, 12)], props.FM(FUNDO))
    cena.poly_mesh("chao", [(-w, -20, 0), (w, -20, 0), (w, 3.0, 0), (-w, 3.0, 0)], props.FM(CHAO))


def elenco(view):
    rot = []
    nomes = [n for n, _ in EA.ELENCO] + ["pipoca"]
    esp = 1.3
    for i, nome in enumerate(nomes):
        x = (i - (len(nomes) - 1) / 2) * esp
        if nome == "pipoca":
            OA.porquinha("pipoca", (x, 0, 0.0), 3.8, vista="frente" if view == "front" else "lado")
            rot.append((NOMES[nome], (x, 0, -0.12)))
            continue
        fn = dict(EA.ELENCO)[nome]
        H = fn(nome, view, rim=EA.RIM)
        w = empty(nome + "_inv", None, (x, 0, 0)); H.root.parent = w
        e = EA.ESCALA.get(nome, 1.0); w.scale = (e, e, e)
        tl = Timeline(H, 1, 12, 24); tl.stand(1, 12, 0.0)
        if view == "q":
            tl.face(1, 1.0, **EXPR[nome])
        else:
            tl.face(1, 1.0, lid="esperto", lidv=0.45, brow=-8, mouth="reta")
        finish(H, tl, 1, 12)
        if view == "front":
            frente.bracos(H, 1, 12, [(1, dict(shF=5, elF=0, shB=5, elB=0))])
        cena.contact_shadow(H, dict(shadow="#8a8070"))
        rot.append((NOMES[nome], (x, 0, -0.12)))
    return rot, 1.3 * len(nomes) + 1.0


def elenco3d(angulo):
    """o mesmo elenco em 3D de verdade, girado em 'angulo' (0 de frente, 40 de 3/4)"""
    rot = []
    nomes = [n for n, _ in EA.ELENCO] + ["pipoca"]
    for i, nome in enumerate(nomes):
        x = (i - (len(nomes) - 1) / 2) * 1.3
        if nome == "pipoca":
            E3.pipoca("pipoca3d", (x, 0, 0.0), 3.8, rot=angulo)
            rot.append((NOMES[nome], (x, 0, -0.12)))
            continue
        h = E3.faz(nome, nome + "3d")
        h.pose(ombro=(-5, 7), cotovelo=(-14, -10), abre=(5, 5))
        ex = EXPR[nome]
        h.rosto(boca="reta", lid=ex.get("lidv", 0.4))
        h.raiz.location = (x, 0, 0); h.raiz.rotation_euler.z = math.radians(angulo)
        cena.ground_disc(f"sombra{i}", 0.4, 0.25, cena.amat(f"sombra{i}_m", "#000000", 1.0, 0.35, ("radial", 1.1)), (x, 0.05, 0.003), n=32)
        rot.append((NOMES[nome], (x, 0, -0.12)))
    return rot, 1.3 * len(nomes) + 1.0


def linha(itens, gap=0.55):
    """itens = [(rótulo, construtor(x), largura_na_ficha)] -> posiciona lado a lado, centrado em x = 0"""
    total = sum(w for _, _, w in itens) + gap * (len(itens) - 1)
    x = -total / 2; rot = []
    for rotulo, f, w in itens:
        cx = x + w / 2
        f(cx); rot.append((rotulo, (cx, 0, -0.12)))
        x += w + gap
    return rot, total + 1.0


def pequenos_a():
    return linha([("Gaiola da Pipoca", lambda x: OA.gaiola("gaiola", (x, 0, 0.0), 2.4), 1.45),
                  ("Galão de água\n(5 litros, cheio)", lambda x: OA.galao("galao1", (x, 0, 0.0), 3.4, nivel=1.0), 0.7),
                  ("Galão: sobrou\nmeio (dia 700)", lambda x: OA.galao("galao2", (x, 0, 0.0), 3.4, nivel=0.5), 0.7),
                  ("Lata de comida", lambda x: OA.lata("lata", (x, 0, 0.0), 7.5), 0.6),
                  ("Prato no dia 1", lambda x: OA.prato("prato1", (x, 0, 0.0), 5.0, nivel="cheio"), 1.2),
                  ("Prato na 3ª semana", lambda x: OA.prato("prato2", (x, 0, 0.0), 5.0, nivel="pouco"), 1.2),
                  ("O jantar com carne\n(dia 60)", lambda x: OA.prato("prato3", (x, 0, 0.0), 5.0, nivel="carne"), 1.2)])


def pequenos_b():
    return linha([("Baralho do Zé", lambda x: OA.baralho("baralho", (x + 0.05 * 6, 0, 0.0), 6.5), 2.1),
                  ("Lâmpadas no dia 1\n(três acesas)", lambda x: OA.lampadas("lamp3", (x, 0, 0.0), 1.7, ligadas=3), 1.55),
                  ("Lâmpadas no dia 700\n(só uma acesa)", lambda x: OA.lampadas("lamp1", (x, 0, 0.0), 1.7, ligadas=1), 1.55),
                  ("Calendário de giz\n(dia 200)", lambda x: OA.quadro_giz("giz", (x, 0, 0.0), 1.7, dias=27, rotulo="DIA 200"), 1.6),
                  ("Eu, o narrador:\nsó as mãos aparecem", lambda x: OA.maos_pov("maos", (x, 0, 0.3 * 2.6), 2.6), 1.7)])


def cenario():
    rot, tot = linha([("Bicicleta com cesta,\nboneca e campainha", lambda x: OA.bicicleta("bici", (x - 0.05, 0, 0.0), 1.5), 2.3),
                      ("Sirene do bairro", lambda x: OA.sirene("sirene", (x, 0, 0.0), 0.72), 1.3),
                      ("Porta do abrigo\n(roda de giro)", lambda x: OA.porta_abrigo("porta", (x, 0.3, 0.0), 0.95), 1.3),
                      ("O povo batendo\nna porta (silhuetas)", lambda x: OA.multidao("povo", (x, 0, 0.0), 0.78, n=5), 2.6),
                      ("Cadeira de balanço\ndo Zé", lambda x: OA.cadeira_balanco("cadeira", (x, 0, 0.0), 1.5), 1.45),
                      ("Estante de latas\n(dia 1)", lambda x: OA.prateleira("est1", (x, 0.2, 0.0), 1.45, nivel=1.0), 1.5),
                      ("Estante meses\ndepois", lambda x: OA.prateleira("est2", (x, 0.2, 0.0), 1.45, nivel=0.15), 1.5)], gap=0.7)
    return rot, tot


DIM = {"elenco3d_frente": (3100, 1400, 0.95), "elenco3d_q": (3100, 1400, 0.95), "elenco_frente": (3100, 1400, 0.95), "elenco_q": (3100, 1400, 0.95), "pequenos_a": (3300, 1300, 0.6), "pequenos_b": (3300, 1300, 0.6), "cenario": (4300, 1500, 1.15)}
W_, H_, CZ = DIM[MODO]
lib.reset(W_, H_, 24, 32)
sc = bpy.context.scene
fundo_neutro()
cam_d = bpy.data.cameras.new("cam"); cam = bpy.data.objects.new("cam", cam_d); sc.collection.objects.link(cam); sc.camera = cam
if MODO.startswith("elenco3d"):
    rotulos, LARG = elenco3d(0 if MODO.endswith("frente") else 40)
elif MODO.startswith("elenco"):
    rotulos, LARG = elenco("front" if MODO == "elenco_frente" else "q")
elif MODO == "pequenos_a":
    rotulos, LARG = pequenos_a()
elif MODO == "pequenos_b":
    rotulos, LARG = pequenos_b()
else:
    rotulos, LARG = cenario()
cam_d.type = "ORTHO"; cam_d.ortho_scale = max(LARG, 6.0)
cam.location = (0.0, -10.0, CZ); cam.rotation_euler = (math.radians(90), 0, 0)
sc.frame_set(1); bpy.context.view_layer.update()
pos = []
for nome, loc in rotulos:
    co = world_to_camera_view(sc, cam, Vector(loc))
    pos.append((nome, co.x, 1 - co.y))
json.dump(pos, open(SAIDA + ".json", "w"), ensure_ascii=False)
sc.render.filepath = SAIDA
bpy.ops.render.render(write_still=True)
