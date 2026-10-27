"""Título 3D do episódio dentro do ambiente (pedido de 23/10/2026): letras em 3D com volume, acima do herói,
que caem com bounce uma a uma e bem rápido, e somem na transição.
Cada letra é um objeto de texto próprio (para animar separado). Face clara de frente, lateral (extrusão) mais escura."""
import math
import bpy
from lib import key, srgb
import curvas

FONTE = "/System/Library/Fonts/Supplemental/Arial Black.ttf"


def _material(nome, face, lado, brilho=1.0):
    """face de frente clara e extrusão escura: decide pela normal (frente = normal apontando para a câmera, -Y)"""
    m = bpy.data.materials.new(nome); m.use_nodes = True
    nt = m.node_tree; nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial"); em = nt.nodes.new("ShaderNodeEmission")
    geo = nt.nodes.new("ShaderNodeNewGeometry"); sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    lt = nt.nodes.new("ShaderNodeMath"); lt.operation = "LESS_THAN"; lt.inputs[1].default_value = -0.6
    mix = nt.nodes.new("ShaderNodeMix"); mix.data_type = "RGBA"
    nt.links.new(geo.outputs["Normal"], sep.inputs[0]); nt.links.new(sep.outputs[1], lt.inputs[0])
    nt.links.new(lt.outputs[0], mix.inputs[0])
    mix.inputs[6].default_value = (*srgb(lado), 1); mix.inputs[7].default_value = (*srgb(face), 1)
    nt.links.new(mix.outputs[2], em.inputs["Color"]); em.inputs["Strength"].default_value = brilho
    nt.links.new(em.outputs[0], out.inputs["Surface"])
    return m


def titulo(nome, linhas, centro, tamanho=0.36, extrude=0.06, entre_linhas=1.15, face="#f6efe2", lado="#7a5a3a", espaco=0.03):
    """linhas = ["PRESIDENTE", "CORRUPTO"]; centro = (x, y, z) do centro do bloco. Devolve a lista de letras na ordem de leitura."""
    fonte = bpy.data.fonts.load(FONTE, check_existing=True)
    mat = _material(nome + "_m", face, lado)
    letras = []
    cx, cy, cz = centro
    n = len(linhas)
    for li, txt in enumerate(linhas):
        z = cz + (n - 1) / 2 * tamanho * entre_linhas - li * tamanho * entre_linhas
        objs, larg = [], 0.0
        for k, ch in enumerate(txt):
            if ch == " ":
                larg += tamanho * 0.35; objs.append(None); continue
            cu = bpy.data.curves.new(f"{nome}_{li}_{k}", "FONT")
            cu.body = ch; cu.font = fonte; cu.size = tamanho; cu.extrude = extrude; cu.bevel_depth = extrude * 0.25
            cu.align_x = "CENTER"; cu.align_y = "CENTER"
            ob = bpy.data.objects.new(f"{nome}_{li}_{k}", cu); bpy.context.scene.collection.objects.link(ob)
            ob.data.materials.append(mat)
            ob.rotation_euler = (math.radians(90), 0, 0)
            bpy.context.view_layer.update()
            w = ob.dimensions.x
            objs.append((ob, larg + w / 2)); larg += w + espaco
        larg -= espaco
        for item in objs:
            if item:
                ob, xo = item
                ob.location = (cx - larg / 2 + xo, cy, z)
                letras.append(ob)
    return letras


def bounce_in(letras, f0, passo=1.5, altura=0.5):
    """cada letra cai de 'altura' e quica (mola), uma depois da outra, rápido"""
    for i, ob in enumerate(letras):
        f = f0 + int(round(i * passo))
        z0 = ob.location.z
        ob.scale = (0.0001,) * 3; key(ob, "scale", f - 1, "CONSTANT")
        for k in range(14):
            t = k / 24.0
            ob.location.z = z0 + altura * (1 - curvas.mola(t, 3.4, 0.38)); key(ob, "location", f + k, "LINEAR")
            s = min(1.0, 0.3 + k / 4) if k < 4 else 1.0
            sq = 1 + 0.18 * curvas.pancada(max(0, t - 0.08), 3.4, 0.38)       # achata um pouco no pouso
            ob.scale = (s * sq, s, s / sq); key(ob, "scale", f + k, "LINEAR")


def some(letras, f0, passo=0.6):
    """somem rápido, uma atrás da outra, subindo um pouco (na transição)"""
    for i, ob in enumerate(letras):
        f = f0 + int(round(i * passo))
        z0 = ob.location.z
        key(ob, "scale", f, "LINEAR"); key(ob, "location", f, "LINEAR")
        for k in range(1, 6):
            u = curvas.s("easy", k / 5)
            ob.scale = (max(0.0001, 1 - u),) * 3; ob.location.z = z0 + 0.25 * u
            key(ob, "scale", f + k, "LINEAR"); key(ob, "location", f + k, "LINEAR")
