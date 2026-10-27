"""Ficha de personagens e objetos do Canal 38 (model sheet). Três pranchas renderizadas e montadas com os nomes:
  elenco_frente  -> o elenco de frente, lado a lado, na mesma escala (a régua é o herói, 1,75 m)
  elenco_q       -> o elenco de 3/4 com a expressão de cada um
  objetos        -> a mesa de objetos vista de cima em 3/4 (pode girar: não há boneco)
blender -b -P ficha_elenco.py -- MODO SAIDA.png"""
import os, sys, json, math
os.environ["VOZ_NOVA"] = ""
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy, lib
from lib import *
import cena, props, frente, uniforme as U, elenco as EL, objetos as OB, unidades as UN, sets4 as S
from anim import Timeline
from prod_pcc import finish
from bpy_extras.object_utils import world_to_camera_view

argv = sys.argv[sys.argv.index("--") + 1:]
MODO, SAIDA = argv[0], argv[1]
FUNDO, CHAO = "#c9c2b4", "#a99f8e"

EXPR = {"presidente": dict(lid="esperto", lidv=0.45, brow=-16, browtilt=0.022, mouth="sorriso"),
        "juiz": dict(lid="bravo", brow=-22, mouth="reta"), "juiza": dict(lid="apertado", lidv=0.7, browtilt=-0.012, brow=-8, mouth="lado"),
        "deputado": dict(eye="cifrao", mouth="sorrisao", browup=0.015), "empreiteiro": dict(lid="esperto", lidv=0.5, brow=-12, mouth="sorriso"),
        "policial": dict(lid="apertado", lidv=0.6, brow=-12, mouth="reta"), "fiscal": dict(wide=0.6, browup=0.02, mouth="o"),
        "diplomata": dict(eye="feliz", mouth="sorriso", browup=0.01), "trabalhador": dict(lid="sono", lidv=0.6, brow=16, mouth="triste"),
        "contador": dict(lid="triste", lidv=0.35, brow=20, mouth="nervosa", extras=("suor",))}


def fundo_neutro(w=40):
    bpy.context.scene.world.node_tree.nodes["Background"].inputs[0].default_value = (*srgb(FUNDO), 1)
    cena.poly_mesh("parede", [(-w, 3.0, -1), (w, 3.0, -1), (w, 3.0, 12), (-w, 3.0, 12)], props.FM(FUNDO))
    cena.poly_mesh("chao", [(-w, -20, 0), (w, -20, 0), (w, 3.0, 0), (-w, 3.0, 0)], props.FM(CHAO))


def elenco(view):
    nomes = []
    for i, (nome, fn) in enumerate(EL.ELENCO):
        x = -5.4 + i * 1.2
        H = U.heroi_presidente(nome, view, rim="#ffe4c8")[0] if fn is None else fn(nome, view)
        w = empty(nome + "_inv", None, (x, 0, 0)); H.root.parent = w
        tl = Timeline(H, 1, 12, 24); tl.stand(1, 12, 0.0)
        if view == "q":
            tl.face(1, 1.0, **EXPR[nome])
        else:
            tl.face(1, 1.0, lid="esperto", lidv=0.55, mouth="pequena")
        finish(H, tl, 1, 12)
        if view == "front":
            frente.bracos(H, 1, 12, [(1, dict(shF=5, elF=0, shB=5, elB=0))])
        cena.contact_shadow(H, dict(shadow="#8a8070"))
        nomes.append((nome, (x, 0, -0.12)))
    return nomes


def objetos(modo):
    itens = []
    def add(nome, loc):
        itens.append((nome, loc))
    if modo == "obj_dinheiro":
        UN.notinha("nota", (-5.6, -0.6, 0.25), 2.4); add("notinha = 1 salário mínimo", (-5.6, -0.6, -0.15))
        UN.maco("maco", (-4.7, -0.6, 0.0)); add("maço = R$ 1 milhão", (-4.7, -0.6, -0.15))
        cb, bl = UN.cubo_mil("cubo_mil", (-2.0, 1.4, 0.0), tirar=3); bl.location = (0.0, 0.0, 0.9)
        add("1 bilhão = 1.000 maços", (-2.0, 0.2, -0.2)); add("30 milhões = 30 maços (3%)", (-2.0, 0.2, 3.7))
        OB.maletinha_dinheiro("malet", (0.6, -0.6, 0.0), 1.6); add("maleta de dinheiro", (0.6, -0.6, -0.15))
        OB.mala_dinheiro("mala", (2.2, -0.4, 0.0), 1.4); add("mala de rodinhas", (2.2, -0.4, -0.15))
        OB.caixa_papelao("cxp", (3.7, -0.5, 0.0), 1.4); add("caixa de papelão", (3.7, -0.5, -0.15))
        OB.cofre("cofre", (5.3, 0.2, 0.0), 1.5); add("cofre", (5.3, -0.2, -0.15))
        OB.carrinho_dinheiro("carr", (0.9, 2.2, 0.0), 1.5); add("carrinho de mão", (0.9, 2.2, -0.15))
    elif modo == "obj_poder":
        OB.cadeira_presidencial("cad", (-5.4, 0.0, 0.0), 1.0); add("cadeira presidencial", (-5.4, 0.0, -0.15))
        OB.bandeira_brasil("band", (-4.3, 0.4, 0.0), 1.0); add("bandeira", (-3.85, 0.4, -0.15))
        OB.tribuna("trib", (-2.4, 0.0, 0.0), 1.0); add("tribuna com microfones", (-2.4, 0.0, -0.15))
        OB.camera_tv("cam_tv", (-1.0, 0.0, 0.0), 1.0); add("câmera de TV", (-0.95, 0.0, -0.15))
        tl, segs = OB.telao_bolsa("telao", (1.4, 1.2, 0.0), s=0.6); add("telão da bolsa", (1.4, 1.2, -0.15))
        vt, vr, vb = S.viatura(dict(borda="#ffffff"), "vtr", 4.4, 0.6, s=0.7); add("viatura", (4.4, 0.6, -0.15))
        OB.jatinho("jato", (-1.6, 2.4, 1.7), 1.1); add("jatinho", (-1.6, 2.4, 1.45))
        OB.congresso("cong", (1.4, 2.8, 2.2), 0.55); add("Congresso (silhueta)", (1.4, 2.8, 3.95))
    else:
        pecas = [("envelope", lambda x: OB.envelope("env", (x, 0, 0.0), 1.6)), ("contrato", lambda x: OB.contrato("contr", (x, 0, 0.0), 1.0)),
                 ("pasta confidencial", lambda x: OB.pasta_confidencial("pc", (x, 0, 0.0), 1.2)), ("carimbo", lambda x: OB.carimbo("car", (x - 0.1, 0, 0.0), 1.4)),
                 ("celular", lambda x: OB.celular("cel", (x, 0, 0.0), 1.4)), ("notebook", lambda x: OB.notebook("nb", (x, 0, 0.0), 1.0)),
                 ("relógio de ouro", lambda x: OB.relogio_luxo("rel", (x, 0, 0.25), 1.8)), ("champanhe", lambda x: OB.champanhe("ch", (x, 0, 0.0), 1.3)),
                 ("charuto", lambda x: OB.charuto("cht", (x, 0, 0.0), 1.6)), ("martelo", lambda x: props.martelo("martelo", (x + 0.25, 0, 0.25), s=0.3)),
                 ("algemas", lambda x: OB.algemas("alg", (x, 0, 0.0), 1.6)), ("tornozeleira", lambda x: OB.tornozeleira("torn", (x, 0, 0.05), 1.6)),
                 ("estojo de joias", lambda x: OB.estojo_joias("est", (x, 0, 0.0), 1.2)), ("mochila", lambda x: OB.mochila("moch", (x, 0, 0.0), 1.0)),
                 ("calendário", lambda x: OB.calendario("cal", (x, 0, 0.0), 0.6)), ("livro do orçamento", lambda x: OB.livro("livro", (x, 0, 0.0), 0.7)),
                 ("retrato", lambda x: OB.retrato("ret", (x, 0, 0.55), 0.8)), ("faixa presidencial", lambda x: OB.faixa_presidencial("faixa", (x, 0, 1.0), 1.0))]
        for i, (nome, fn) in enumerate(pecas):
            r_, c_ = divmod(i, 9)
            x = -3.2 + c_ * 0.8; y = -0.4 + r_ * 1.6
            fnx = fn
            import types
            obj_x = x
            # cada peça na sua linha (a segunda linha mais ao fundo)
            def coloca(f=fn, xx=x, yy=y):
                antes = set(bpy.data.objects.keys())
                f(xx)
                for nm_ in set(bpy.data.objects.keys()) - antes:
                    o = bpy.data.objects[nm_]
                    if o.parent is None:
                        o.location.y += yy
            coloca()
            add(nome, (x, y, -0.16))
    return itens


lib.reset(4800 if MODO.startswith("elenco") else 3600, 1400 if MODO.startswith("elenco") else 2000, 24, 32)
sc = bpy.context.scene
fundo_neutro()
cam_d = bpy.data.cameras.new("cam"); cam = bpy.data.objects.new("cam", cam_d); sc.collection.objects.link(cam); sc.camera = cam
if MODO.startswith("elenco"):
    rotulos = elenco("front" if MODO == "elenco_frente" else "q")
    cam_d.type = "ORTHO"; cam_d.ortho_scale = 12.4
    cam.location = (0.0, -10.0, 0.95); cam.rotation_euler = (math.radians(90), 0, 0)
else:
    rotulos = objetos(MODO)
    cam_d.lens = 32
    CAMS = {"obj_dinheiro": ((0.0, -10.5, 5.6), 66), "obj_poder": ((-0.6, -10.5, 5.2), 70), "obj_pequenos": ((0.0, -6.0, 3.4), 66)}
    loc_, rx = CAMS[MODO]
    cam.location = loc_; cam.rotation_euler = (math.radians(rx), 0, 0)
sc.frame_set(1); bpy.context.view_layer.update()
pos = []
for nome, loc in rotulos:
    co = world_to_camera_view(sc, cam, Vector(loc))
    pos.append((nome, co.x, 1 - co.y))
json.dump(pos, open(SAIDA + ".json", "w"), ensure_ascii=False)
sc.render.filepath = SAIDA
bpy.ops.render.render(write_still=True)
