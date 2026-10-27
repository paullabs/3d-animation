"""PROFUNDIDADE (crítica de 25/10/2026: "não tem contraste nem ponto de foco; precisa ter depthmap").
O fundo estava tão nítido e tão claro quanto os personagens. Agora cada plano ganha:
  1. desfoque pela distância: abertura grande (f/2) com o foco no boneco (a câmera de cada plano já tem o ponto de foco);
  2. névoa pelo MAPA DE PROFUNDIDADE (o passe 'mist' do render): quanto mais longe do ponto de foco, mais o prédio some no tom do céu
     (perde contraste e cor), então o boneco, que está no foco, é o que tem mais contraste do quadro;
  3. uma vinheta leve, que escurece os cantos e leva o olho para o centro.
Uso: depois de montar a cena e a câmera: profundidade.aplica()   (idempotente)."""
import bpy, math
from mathutils import Vector

HAZE = (0.80, 0.90, 0.98)           # o tom do céu no horizonte
ENEVOA, DEPTH_X, VIGNETA = 0.80, 14.0, 0.30
ENEVOA_POR = {"7B": 0.2, "7C": 0.2, "6E": 0.5}                 # o raio X (corpo translúcido) precisa de contraste: pouca névoa
ABERTURA = {"7B": 8.0, "7C": 8.0, "6E": 4.0, "5C": 2.8, "6A": 4.5, "2A": 3.0, "5A": 3.0}               # planos de perto: abertura menos aberta (o rosto e o macro precisam de mais foco)


def _math(N, op, a=None, b=None, loc=(0, 0)):
    n = N.new("ShaderNodeMath"); n.operation = op; n.location = loc
    if a is not None:
        n.inputs[0].default_value = a
    if b is not None:
        n.inputs[1].default_value = b
    return n


def aplica(abertura=2.0, enevoa=ENEVOA, vinheta=VIGNETA, foco=None):
    sc = bpy.context.scene
    cam = sc.camera
    if cam is None:
        return
    cd = cam.data
    cd.dof.use_dof = True
    cd.dof.aperture_fstop = abertura
    d_foco = cd.dof.focus_distance if foco is None else foco
    if d_foco <= 0:
        d_foco = 3.0
    vl = bpy.context.view_layer
    vl.use_pass_mist = True
    ms = sc.world.mist_settings
    ms.start = d_foco * 0.9
    ms.depth = d_foco * DEPTH_X
    ms.falloff = "LINEAR"
    nt = bpy.data.node_groups.get("profundidade")
    if nt is not None:
        bpy.data.node_groups.remove(nt)
    nt = bpy.data.node_groups.new("profundidade", "CompositorNodeTree")
    sc.compositing_node_group = nt
    nt.interface.new_socket("Image", in_out="OUTPUT", socket_type="NodeSocketColor")
    N, L = nt.nodes, nt.links
    rl = N.new("CompositorNodeRLayers"); rl.location = (-700, 0)
    cor = N.new("CompositorNodeRGB"); cor.location = (-700, -300); cor.outputs[0].default_value = (*HAZE, 1.0)
    esc = _math(N, "MULTIPLY", None, enevoa, (-450, -150))
    mix = N.new("ShaderNodeMix"); mix.data_type = "RGBA"; mix.blend_type = "MIX"; mix.location = (-200, 0)
    L.new(rl.outputs["Mist"], esc.inputs[0])
    L.new(esc.outputs[0], mix.inputs[0])
    L.new(rl.outputs["Image"], mix.inputs[6])
    L.new(cor.outputs[0], mix.inputs[7])
    ultimo = mix.outputs[2]
    if vinheta > 0:
        el = N.new("CompositorNodeEllipseMask"); el.location = (-450, 300)
        el.inputs["Position"].default_value = (0.5, 0.5); el.inputs["Size"].default_value = (0.95, 0.80); el.inputs["Rotation"].default_value = 0.0
        bl = N.new("CompositorNodeBlur"); bl.location = (-250, 300)
        try:
            bl.inputs["Size"].default_value = (260.0, 260.0)
        except Exception:
            bl.inputs["Size"].default_value = 260.0
        sub = _math(N, "SUBTRACT", 1.0, None, (-50, 300))
        mul = _math(N, "MULTIPLY", None, vinheta, (100, 300))
        res = _math(N, "SUBTRACT", 1.0, None, (250, 300))
        comb = N.new("CompositorNodeCombineColor"); comb.location = (400, 200)
        m2 = N.new("ShaderNodeMix"); m2.data_type = "RGBA"; m2.blend_type = "MULTIPLY"; m2.location = (600, 0)
        m2.inputs[0].default_value = 1.0
        L.new(el.outputs[0], bl.inputs["Image"])
        L.new(bl.outputs[0], sub.inputs[1])
        L.new(sub.outputs[0], mul.inputs[0])
        L.new(mul.outputs[0], res.inputs[1])
        for k in range(3):
            L.new(res.outputs[0], comb.inputs[k])
        comb.inputs[3].default_value = 1.0
        L.new(ultimo, m2.inputs[6])
        L.new(comb.outputs[0], m2.inputs[7])
        ultimo = m2.outputs[2]
    out = N.new("NodeGroupOutput"); out.location = (800, 0)
    L.new(ultimo, out.inputs[0])
