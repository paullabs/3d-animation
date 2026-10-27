"""Membros "mangueira" (método RubberHose): o braço/perna é uma curva que passa por 3 juntas
(ombro-cotovelo-punho ou quadril-joelho-tornozelo), com o canto arredondado (fillet) e espessura que afina
suavemente. Gerado por geometry nodes a cada quadro a partir das posições das juntas, então dobra em qualquer
ângulo sem esticar, sem emenda e sem triângulos. Faixas: sombra | cor | brilho, e contorno por trás."""
import bpy, math

_NG = {}


def _sock(ng, name, kind, default=None, inp=True):
    s = ng.interface.new_socket(name=name, in_out="INPUT" if inp else "OUTPUT", socket_type=kind)
    if default is not None and hasattr(s, "default_value"):
        s.default_value = default
    return s


def node_group():
    if "g" in _NG:
        return _NG["g"]
    ng = bpy.data.node_groups.new("RubberLimb", "GeometryNodeTree")
    _sock(ng, "Geometry", "NodeSocketGeometry")
    for nm in ("A", "B", "C"):
        _sock(ng, nm, "NodeSocketObject")
    for nm, d in (("r0", 0.04), ("r2", 0.03), ("ink", 0.16), ("y", 0.0), ("fillet", 0.07),
                  ("shade_a", -1.0), ("shade_b", -0.4), ("rim_a", 0.82), ("rim_b", 1.0)):
        _sock(ng, nm, "NodeSocketFloat", d)
    for nm in ("mat_main", "mat_shade", "mat_rim", "mat_ink"):
        _sock(ng, nm, "NodeSocketMaterial")
    _sock(ng, "cap", "NodeSocketBool", True)
    _sock(ng, "Geometry", "NodeSocketGeometry", inp=False)
    N = ng.nodes; L = ng.links
    gi = N.new("NodeGroupInput"); go = N.new("NodeGroupOutput")
    # posições das 3 juntas (em relação ao objeto do membro, que fica na origem)
    info = {}
    for nm in ("A", "B", "C"):
        o = N.new("GeometryNodeObjectInfo"); o.transform_space = "RELATIVE"
        L.new(gi.outputs[nm], o.inputs["Object"]); info[nm] = o
    sep = N.new("ShaderNodeSeparateXYZ"); L.new(info["A"].outputs["Scale"], sep.inputs[0])
    sabs = N.new("ShaderNodeMath"); sabs.operation = "ABSOLUTE"; L.new(sep.outputs["Z"], sabs.inputs[0])
    def scaled(name):
        m = N.new("ShaderNodeMath"); m.operation = "MULTIPLY"
        L.new(gi.outputs[name], m.inputs[0]); L.new(sabs.outputs[0], m.inputs[1]); return m.outputs[0]
    R0, R2, FIL = scaled("r0"), scaled("r2"), scaled("fillet")
    line = N.new("GeometryNodeMeshLine"); line.inputs["Count"].default_value = 3
    idx = N.new("GeometryNodeInputIndex")
    sw = N.new("GeometryNodeIndexSwitch"); sw.data_type = "VECTOR"; sw.index_switch_items.new()
    L.new(idx.outputs[0], sw.inputs["Index"])
    for i, nm in enumerate(("A", "B", "C")):
        L.new(info[nm].outputs["Location"], sw.inputs[str(i)])
    sp = N.new("GeometryNodeSetPosition")
    L.new(line.outputs[0], sp.inputs["Geometry"]); L.new(sw.outputs[0], sp.inputs["Position"])
    m2c = N.new("GeometryNodeMeshToCurve"); L.new(sp.outputs[0], m2c.inputs["Mesh"])
    fil = N.new("GeometryNodeFilletCurve")
    fil.inputs["Mode"].default_value = "Poly"; fil.inputs["Count"].default_value = 8
    fil.inputs["Limit Radius"].default_value = True
    L.new(m2c.outputs[0], fil.inputs["Curve"]); L.new(FIL, fil.inputs["Radius"])
    # espessura afinando do início para o fim
    par = N.new("GeometryNodeSplineParameter")
    mr = N.new("ShaderNodeMapRange")
    L.new(par.outputs["Factor"], mr.inputs["Value"]); L.new(R0, mr.inputs[3]); L.new(R2, mr.inputs[4])
    scr = N.new("GeometryNodeSetCurveRadius"); L.new(fil.outputs[0], scr.inputs["Curve"]); L.new(mr.outputs[0], scr.inputs["Radius"])
    nrm = N.new("GeometryNodeSetCurveNormal"); nrm.inputs["Mode"].default_value = "Free"
    nrm.inputs["Normal"].default_value = (0.0, 1.0, 0.0)
    L.new(scr.outputs[0], nrm.inputs["Curve"])
    rad = N.new("GeometryNodeInputRadius")
    join = N.new("GeometryNodeJoinGeometry")

    def strip(a_src, b_src, mat_name, dy, neg_ink=False):
        prof = N.new("GeometryNodeCurvePrimitiveLine")
        # o perfil vai no eixo Y local, que vira a direção "de lado" do membro (no plano da tela)
        AX = 1
        ca = N.new("ShaderNodeCombineXYZ"); L.new(gi.outputs[a_src] if isinstance(a_src, str) else a_src, ca.inputs[AX]); L.new(ca.outputs[0], prof.inputs["Start"])
        cb = N.new("ShaderNodeCombineXYZ"); L.new(gi.outputs[b_src] if isinstance(b_src, str) else b_src, cb.inputs[AX]); L.new(cb.outputs[0], prof.inputs["End"])
        c2m = N.new("GeometryNodeCurveToMesh")
        L.new(nrm.outputs[0], c2m.inputs["Curve"]); L.new(prof.outputs[0], c2m.inputs["Profile Curve"]); L.new(rad.outputs[0], c2m.inputs["Scale"])
        sm = N.new("GeometryNodeSetMaterial"); L.new(c2m.outputs[0], sm.inputs["Geometry"]); L.new(gi.outputs[mat_name], sm.inputs["Material"])
        off = N.new("ShaderNodeCombineXYZ"); add = N.new("ShaderNodeMath"); add.operation = "ADD"
        L.new(gi.outputs["y"], add.inputs[0]); add.inputs[1].default_value = dy
        L.new(add.outputs[0], off.inputs[1])
        mv = N.new("GeometryNodeSetPosition"); L.new(sm.outputs[0], mv.inputs["Geometry"]); L.new(off.outputs[0], mv.inputs["Offset"])
        L.new(mv.outputs[0], join.inputs[0])

    # contorno: de -(1+ink) a +(1+ink), atrás de tudo
    neg = N.new("ShaderNodeMath"); neg.operation = "SUBTRACT"; neg.inputs[0].default_value = -1.0
    L.new(gi.outputs["ink"], neg.inputs[1])                                    # -1 - ink
    pos = N.new("ShaderNodeMath"); pos.operation = "ADD"; pos.inputs[0].default_value = 1.0
    L.new(gi.outputs["ink"], pos.inputs[1])                                    # 1 + ink
    strip(neg.outputs[0], pos.outputs[0], "mat_ink", 0.0012)
    strip("shade_a", "shade_b", "mat_shade", -0.0004)
    strip("shade_b", "rim_a", "mat_main", -0.0004)
    strip("rim_a", "rim_b", "mat_rim", -0.0004)

    # tampa redonda no começo (ombro), para o membro nunca terminar "cortado"
    for rk, mat_name, dy, extra in (("r0", "mat_ink", 0.0011, True), ("r0", "mat_main", -0.0002, False)):
        circ = N.new("GeometryNodeMeshCircle"); circ.fill_type = "NGON"; circ.inputs["Vertices"].default_value = 32
        if extra:
            r_ink = N.new("ShaderNodeMath"); r_ink.operation = "MULTIPLY_ADD"
            L.new(gi.outputs["ink"], r_ink.inputs[0]); L.new(R0, r_ink.inputs[1]); L.new(R0, r_ink.inputs[2])
            L.new(r_ink.outputs[0], circ.inputs["Radius"])
        else:
            L.new(R0, circ.inputs["Radius"])
        tr = N.new("GeometryNodeTransform")
        tr.inputs["Rotation"].default_value = (math.pi / 2, 0.0, 0.0)
        offv = N.new("ShaderNodeCombineXYZ"); add = N.new("ShaderNodeMath"); add.operation = "ADD"
        L.new(gi.outputs["y"], add.inputs[0]); add.inputs[1].default_value = dy; L.new(add.outputs[0], offv.inputs[1])
        vadd = N.new("ShaderNodeVectorMath"); vadd.operation = "ADD"
        L.new(info["A"].outputs["Location"], vadd.inputs[0]); L.new(offv.outputs[0], vadd.inputs[1])
        L.new(vadd.outputs[0], tr.inputs["Translation"])
        L.new(circ.outputs[0], tr.inputs["Geometry"])
        sm = N.new("GeometryNodeSetMaterial"); L.new(tr.outputs[0], sm.inputs["Geometry"]); L.new(gi.outputs[mat_name], sm.inputs["Material"])
        sel = N.new("GeometryNodeSwitch"); sel.input_type = "GEOMETRY"
        L.new(gi.outputs["cap"], sel.inputs["Switch"]); L.new(sm.outputs[0], sel.inputs["True"])
        L.new(sel.outputs[0], join.inputs[0])
    L.new(join.outputs[0], go.inputs["Geometry"])
    _NG["g"] = ng
    return ng


def rubber_limb(name, a, b, c, r0, r2, y, mats, ink=0.16, fillet=0.07, cap=True, shade=(-1.0, -0.4), rim=(0.82, 1.0)):
    """cria o objeto do membro. a,b,c = juntas (empties). mats = dict(main, shade, rim, ink). y = profundidade"""
    me = bpy.data.meshes.new(name)
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    mod = ob.modifiers.new("limb", "NODES"); mod.node_group = node_group()
    ids = {it.name: it.identifier for it in mod.node_group.interface.items_tree if getattr(it, "in_out", "") == "INPUT"}
    vals = dict(A=a, B=b, C=c, r0=r0, r2=r2, ink=ink, y=y, fillet=fillet, shade_a=shade[0], shade_b=shade[1],
                rim_a=rim[0], rim_b=rim[1], mat_main=mats["main"], mat_shade=mats["shade"], mat_rim=mats["rim"],
                mat_ink=mats["ink"], cap=cap)
    ins = mod.properties.inputs
    for k, v in vals.items():
        getattr(ins, ids[k]).value = v
    for m in (mats["main"], mats["shade"], mats["rim"], mats["ink"]):
        if m.name not in [s.name for s in me.materials if s]:
            me.materials.append(m)
    return ob
