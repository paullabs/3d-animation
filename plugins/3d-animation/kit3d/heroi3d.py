"""O herói em 3D de verdade, v2 (pedido de 23/10/2026: "tá muito low-poly, muito simplista; não aparece um boneco estilo nosso").
Agora é o MESMO desenho do boneco 2D (heroi.py, versão esguia de jaqueta), medido junta a junta e levado ao volume:
- proporções do 2D: quadril a 0,86 m, ombros largos a ±0,16 m, braços compridos e finos (0,34 + 0,32 m, raio 0,042 -> 0,035),
  pernas retas (0,41 + 0,38 m), pescoço curto e cabeça redonda de raio 0,16 m;
- torso moldado na silhueta da jaqueta bomber do 2D (barra canelada mais escura, gola, zíper e bolsos);
- membros afilados e contínuos (tubos varridos com tampa redonda, junta esférica para o cotovelo não aparecer), punho canelado;
- rosto no estilo: olhos brancos sem pupila grandes, sobrancelhas brancas finas e curvas, boca de traço branco;
- sombreado do estilo (chapado com uma faixa de sombra do lado oposto à luz e uma borda de luz pêssego do lado da luz), contorno de tinta fino
  (casco invertido), tudo sem lâmpada: o tom vem da normal contra LUZ.
Uso: H = Heroi3D("goleiro", roupa="#e0602a", calca="#1c2230", luvas=True); H.pose(...); H.rosto(boca="sorriso", lid=0.4)
O boneco olha para -Y; +x é a direita dele; juntas em graus; positivo = para trás (braço/perna) e para fora (abre)."""
import math
import bpy, bmesh
from mathutils import Vector
from lib import empty, srgb
import cena

LUZ = Vector((-0.42, -0.58, 0.7)).normalized()       # de onde vem a luz (esquerda, frente e alto), como no 2D
TINTA = "#0d1020"
PELE = "#0d1020"
BORDA = "#ffd2bc"
_MATS = {}


def _mix(a, b, t):
    pa = [int(a.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4)]; pb = [int(b.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4)]
    return "#%02x%02x%02x" % tuple(int(x + (y - x) * t) for x, y in zip(pa, pb))


# ---------------------------------------------------------------- materiais do estilo
def estilo(cor, sombra=None, borda=BORDA, limiar=0.50, rim=0.70, forca_rim=1.0):
    """tom chapado + faixa de sombra do lado oposto à luz + borda de luz no contorno do lado da luz (como o 2D)"""
    k = (cor, sombra, borda, limiar, rim, forca_rim)
    if k in _MATS:
        return _MATS[k]
    sombra = sombra or _mix(cor, "#000000", 0.30)
    m = bpy.data.materials.new("e3_" + cor); m.use_nodes = True
    nt = m.node_tree; nt.nodes.clear(); N = nt.nodes; L = nt.links
    geo = N.new("ShaderNodeNewGeometry")
    dot = N.new("ShaderNodeVectorMath"); dot.operation = "DOT_PRODUCT"; dot.inputs[1].default_value = tuple(LUZ)
    mp = N.new("ShaderNodeMapRange"); mp.inputs[1].default_value = -1.0; mp.inputs[2].default_value = 1.0
    cr = N.new("ShaderNodeValToRGB"); cr.color_ramp.interpolation = "CONSTANT"
    e = cr.color_ramp.elements
    e[0].position = 0.0; e[0].color = (*srgb(sombra), 1)
    e[1].position = limiar; e[1].color = (*srgb(cor), 1)
    lw = N.new("ShaderNodeLayerWeight"); lw.inputs["Blend"].default_value = 0.5
    cut = N.new("ShaderNodeMath"); cut.operation = "GREATER_THAN"; cut.inputs[1].default_value = rim
    ladoluz = N.new("ShaderNodeMath"); ladoluz.operation = "GREATER_THAN"; ladoluz.inputs[1].default_value = 0.56
    mul = N.new("ShaderNodeMath"); mul.operation = "MULTIPLY"; mul.inputs[1].default_value = forca_rim
    mulf = N.new("ShaderNodeMath"); mulf.operation = "MULTIPLY"
    mx = N.new("ShaderNodeMix"); mx.data_type = "RGBA"; mx.inputs[7].default_value = (*srgb(borda), 1)
    em = N.new("ShaderNodeEmission"); out = N.new("ShaderNodeOutputMaterial")
    L.new(geo.outputs["Normal"], dot.inputs[0]); L.new(dot.outputs["Value"], mp.inputs[0]); L.new(mp.outputs["Result"], cr.inputs[0])
    L.new(mp.outputs["Result"], ladoluz.inputs[0]); L.new(lw.outputs["Facing"], cut.inputs[0])
    L.new(cut.outputs["Value"], mulf.inputs[0]); L.new(ladoluz.outputs["Value"], mulf.inputs[1]); L.new(mulf.outputs["Value"], mul.inputs[0])
    L.new(mul.outputs["Value"], mx.inputs[0]); L.new(cr.outputs["Color"], mx.inputs[6])
    L.new(mx.outputs[2], em.inputs["Color"]); L.new(em.outputs["Emission"], out.inputs["Surface"])
    _MATS[k] = m
    return m


def tinta():
    if "tinta" in _MATS:
        return _MATS["tinta"]
    m = bpy.data.materials.new("e3_tinta"); m.use_nodes = True
    nt = m.node_tree; nt.nodes.clear()
    em = nt.nodes.new("ShaderNodeEmission"); em.inputs["Color"].default_value = (*srgb(TINTA), 1)
    out = nt.nodes.new("ShaderNodeOutputMaterial"); nt.links.new(em.outputs["Emission"], out.inputs["Surface"])
    m.use_backface_culling = True
    _MATS["tinta"] = m
    return m


def plano(cor):
    """branco do rosto: emissão chapada sem sombra nem borda"""
    if ("plano", cor) in _MATS:
        return _MATS[("plano", cor)]
    m = bpy.data.materials.new("e3_p_" + cor); m.use_nodes = True
    nt = m.node_tree; nt.nodes.clear()
    em = nt.nodes.new("ShaderNodeEmission"); em.inputs["Color"].default_value = (*srgb(cor), 1)
    out = nt.nodes.new("ShaderNodeOutputMaterial"); nt.links.new(em.outputs["Emission"], out.inputs["Surface"])
    _MATS[("plano", cor)] = m
    return m


# ---------------------------------------------------------------- malhas
def _objeto(nome, bm, mat, pai, loc, contorno):
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(nome); bm.to_mesh(me); bm.free()
    for p in me.polygons:
        p.use_smooth = True
    ob = bpy.data.objects.new(nome, me); bpy.context.scene.collection.objects.link(ob)
    ob.parent = pai; ob.location = loc
    me.materials.append(mat)
    if contorno:
        me.materials.append(tinta())
        md = ob.modifiers.new("contorno", "SOLIDIFY")
        md.thickness = contorno; md.offset = 1.0; md.use_flip_normals = True; md.material_offset = 1
    return ob


def tubo(nome, pts, raios, mat, pai, loc=(0, 0, 0), seg=36, tampa=10, contorno=0.005, tampa_ini=True, tampa_fim=True):
    """tubo varrido por uma polilinha (pts) com raio por ponto e tampas redondas: um membro inteiro numa peça só"""
    P = [Vector(p) for p in pts]; n = len(P)
    T = []
    for i in range(n):
        a = P[max(0, i - 1)]; b = P[min(n - 1, i + 1)]
        T.append((b - a).normalized())
    base = Vector((1, 0, 0)) if abs(T[0].x) < 0.9 else Vector((0, 1, 0))
    nrm = [(base - T[0] * base.dot(T[0])).normalized()]
    for i in range(1, n):
        v = nrm[-1] - T[i] * nrm[-1].dot(T[i]); nrm.append(v.normalized())
    bin_ = [T[i].cross(nrm[i]).normalized() for i in range(n)]
    bm = bmesh.new()
    def anel(c, i, r):
        return [bm.verts.new(c + (nrm[i] * math.cos(2 * math.pi * k / seg) + bin_[i] * math.sin(2 * math.pi * k / seg)) * r) for k in range(seg)]
    aneis = []
    polo_ini = polo_fim = None
    if tampa_ini:
        polo_ini = bm.verts.new(P[0] - T[0] * raios[0])
        for j in range(1, tampa):
            th = math.pi / 2 * j / tampa
            aneis.append(anel(P[0] - T[0] * raios[0] * math.cos(th), 0, raios[0] * math.sin(th)))
    for i in range(n):
        aneis.append(anel(P[i], i, raios[i]))
    if tampa_fim:
        polo_fim = bm.verts.new(P[-1] + T[-1] * raios[-1])
        for j in range(tampa - 1, 0, -1):
            th = math.pi / 2 * j / tampa
            aneis.append(anel(P[-1] + T[-1] * raios[-1] * math.cos(th), n - 1, raios[-1] * math.sin(th)))
    for k in range(seg):
        k2 = (k + 1) % seg
        if polo_ini is not None:
            bm.faces.new((polo_ini, aneis[0][k2], aneis[0][k]))
        if polo_fim is not None:
            bm.faces.new((polo_fim, aneis[-1][k], aneis[-1][k2]))
        for a, b in zip(aneis, aneis[1:]):
            bm.faces.new((a[k], a[k2], b[k2], b[k]))
    return _objeto(nome, bm, mat, pai, loc, contorno)


def esfera(nome, rx, ry, rz, mat, pai, loc=(0, 0, 0), contorno=0.005, seg=48, an=28):
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=seg, v_segments=an, radius=1.0)
    bmesh.ops.scale(bm, vec=(rx, ry, rz), verts=bm.verts)
    return _objeto(nome, bm, mat, pai, loc, contorno)


def superelipse(t, hw, hd, expo):
    c, s = math.cos(t), math.sin(t)
    return (hw * math.copysign(abs(c) ** (2 / expo), c), hd * math.copysign(abs(s) ** (2 / expo), s))


def loft(nome, perfil, mat, pai, loc=(0, 0, 0), expo=2.6, seg=56, contorno=0.005, fechar=True, dx=0.0):
    """sólido moldado pela silhueta: perfil = [(z, meia_largura, meia_profundidade)] de baixo para cima; cada corte é uma superelipse"""
    bm = bmesh.new(); aneis = []
    for z, hw, hd in perfil:
        aneis.append([bm.verts.new((dx + superelipse(2 * math.pi * k / seg, max(hw, 1e-4), max(hd, 1e-4), expo)[0],
                                    superelipse(2 * math.pi * k / seg, max(hw, 1e-4), max(hd, 1e-4), expo)[1], z)) for k in range(seg)])
    if fechar:
        ba = bm.verts.new((dx, 0, perfil[0][0])); to = bm.verts.new((dx, 0, perfil[-1][0]))
    for k in range(seg):
        k2 = (k + 1) % seg
        if fechar:
            bm.faces.new((ba, aneis[0][k2], aneis[0][k])); bm.faces.new((to, aneis[-1][k], aneis[-1][k2]))
        for a, b in zip(aneis, aneis[1:]):
            bm.faces.new((a[k], a[k2], b[k2], b[k]))
    return _objeto(nome, bm, mat, pai, loc, contorno)


def junta(nome, pai, loc=(0, 0, 0)):
    return empty(nome, pai, loc)


def _interp(tab, z):
    for (z0, w0), (z1, w1) in zip(tab, tab[1:]):
        if z0 <= z <= z1:
            u = (z - z0) / (z1 - z0); u = u * u * (3 - 2 * u)
            return w0 + (w1 - w0) * u
    return tab[0][1] if z < tab[0][0] else tab[-1][1]


# silhueta da jaqueta do 2D (heroi._jacket, vista de frente): z relativo ao quadril, metade da largura
JAQUETA = [(-0.055, 0.135), (0.02, 0.168), (0.14, 0.172), (0.37, 0.176), (0.44, 0.158), (0.468, 0.1), (0.474, 0.0)]


class Heroi3D:
    def __init__(self, nome, roupa="#c62f35", calca="#2b64c0", luvas=False, sapato="#17171d", escura=None, gola=None,
                 escala=1.0, cabeca=0.8, body_w=1.06, arm_len=1.18, bone=None, borda=BORDA, camisa=None):
        self.nome = nome; self.cabeca_k = cabeca; self.borda = borda
        escura = escura or _mix(roupa, "#000000", 0.38); gola = gola or escura
        M = lambda c, s=None: estilo(c, s, borda)
        mj, md, mc, ms, mp_, mt = M(roupa), M(escura), M(calca), M(sapato), M(PELE), M(gola)
        R = self.raiz = empty(nome, None, (0, 0, 0)); R.scale = (escala,) * 3
        Q = self.quadril = junta(nome + "_quadril", R, (0, 0, 0.86))
        bw = body_w
        # pernas: tubo contínuo coxa + canela (quadril -> joelho -> tornozelo) com joelho redondo
        self.perna, self.joelho, self.tornozelo = {}, {}, {}
        for s, x in (("F", -0.07 * bw), ("B", 0.07 * bw)):
            q = junta(f"{nome}_q{s}", Q, (x, 0, 0)); self.perna[s] = q
            k = junta(f"{nome}_k{s}", q, (0, 0, -0.41)); self.joelho[s] = k
            a = junta(f"{nome}_a{s}", k, (0, 0, -0.38)); self.tornozelo[s] = a
            tubo(f"{nome}_coxa{s}", [(0, 0, 0), (0, 0, -0.41)], [0.0425, 0.036], mc, q, seg=40, tampa_ini=False)
            esfera(f"{nome}_joelho{s}", 0.036, 0.036, 0.036, mc, k, contorno=0.005, seg=36, an=20)
            tubo(f"{nome}_canela{s}", [(0, 0, 0), (0, 0, -0.38)], [0.036, 0.031], mc, k, seg=40, tampa_fim=False)
            # sapato: bico para a frente (-Y), sola clara
            esfera(f"{nome}_sapato{s}", 0.052, 0.115, 0.05, ms, a, (0, -0.055, -0.04), contorno=0.005, seg=40, an=22)
            esfera(f"{nome}_sola{s}", 0.054, 0.117, 0.013, M("#d8d3c6"), a, (0, -0.055, -0.083), contorno=0.004, seg=40, an=14)
        esfera(nome + "_pelve", 0.122 * bw, 0.1, 0.065, mc, Q, (0, 0, 0.0), contorno=0.005, seg=48, an=24)
        # tronco: jaqueta moldada na silhueta do 2D, barra e gola canelada mais escuras, zíper e bolsos
        T = self.tronco = junta(nome + "_tronco", Q, (0, 0, 0))
        zs = [-0.055 + (0.474 + 0.055) * i / 40 for i in range(41)]
        prof = [(z, _interp([(a, b * bw) for a, b in JAQUETA], z), 0.6 * _interp([(a, b * bw) for a, b in JAQUETA], z) + 0.025) for z in zs]
        prof[-1] = (prof[-1][0], 0.001, 0.001)
        loft(nome + "_jaqueta", prof, mj, T, expo=2.7, seg=64, contorno=0.006)
        barra = [(-0.09 + 0.05 * i / 6, 0.138 * bw, 0.6 * 0.135 * bw + 0.028) for i in range(7)]
        loft(nome + "_barra", barra, md, T, expo=2.7, seg=56, contorno=0.005)
        col = [(0.43, 0.082 * bw, 0.07), (0.455, 0.092 * bw, 0.078), (0.488, 0.088 * bw, 0.074), (0.505, 0.07 * bw, 0.06)]
        loft(nome + "_gola", col, mt, T, expo=2.2, seg=40, contorno=0.005, fechar=False)
        zp = lambda z: 0.6 * _interp([(a, b * bw) for a, b in JAQUETA], z) + 0.025
        tubo(nome + "_ziper", [(0, -zp(0.43) - 0.002, 0.43), (0.002, -zp(0.2) - 0.003, 0.2), (0.004, -zp(-0.03) - 0.002, -0.03)], [0.0035] * 3, md, T, seg=10, tampa=4, contorno=0.0)
        for s, sg in (("F", -1), ("B", 1)):
            tubo(f"{nome}_bolso{s}", [(sg * 0.075, -zp(0.07) - 0.003, 0.16), (sg * 0.1, -zp(0.07) - 0.003, 0.07)], [0.0035] * 2, md, T, seg=10, tampa=4, contorno=0.0)
        # pescoço e cabeça (raio 0,16 m: a cabeça do 2D é 0,2 x 0,8)
        P = self.pescoco = junta(nome + "_pescoco", T, (0, 0, 0.46))
        tubo(nome + "_pesc", [(0, 0, 0.0), (0, 0, 0.1)], [0.038, 0.034], mp_, P, seg=28, tampa_ini=False, contorno=0.004)
        C = self.cabeca = junta(nome + "_cabeca", P, (0, 0, 0.055))
        r = 0.2 * cabeca; self.R = r
        esfera(nome + "_cranio", r, r, r, mp_, C, (0, 0, r), contorno=0.0055, seg=72, an=44)
        self._rosto(C, r, M)
        # braços: tubo afilado ombro -> cotovelo -> punho, junta esférica nos dois lados, punho canelado
        self.ombro, self.cotovelo, self.punho = {}, {}, {}
        al = arm_len
        for s, x in (("F", -0.15 * bw), ("B", 0.15 * bw)):
            o = junta(f"{nome}_o{s}", T, (x, 0, 0.465 - 0.055 - 0.12 + 0.12)); self.ombro[s] = o
            o.location = (x, 0, 0.405)
            c = junta(f"{nome}_c{s}", o, (0, 0, -0.29 * al)); self.cotovelo[s] = c
            w = junta(f"{nome}_w{s}", c, (0, 0, -0.27 * al)); self.punho[s] = w
            esfera(f"{nome}_deltoide{s}", 0.045, 0.045, 0.045, mj, o, contorno=0.005, seg=36, an=20)
            tubo(f"{nome}_braco{s}", [(0, 0, 0), (0, 0, -0.29 * al)], [0.042, 0.039], mj, o, seg=36)   # tampa nos dois lados: com o braço lá em cima, a boca do tubo aparecia clara
            esfera(f"{nome}_cot{s}", 0.039, 0.039, 0.039, mj, c, contorno=0.005, seg=32, an=18)
            tubo(f"{nome}_antebraco{s}", [(0, 0, 0), (0, 0, -0.27 * al)], [0.039, 0.035], mj, c, seg=36, tampa_fim=False)
            tubo(f"{nome}_punhoc{s}", [(0, 0, -0.27 * al + 0.045), (0, 0, -0.27 * al + 0.005)], [0.038, 0.038], md, c, seg=32, tampa_ini=False, tampa_fim=False, contorno=0.004)
            esfera(f"{nome}_pulso{s}", 0.034, 0.034, 0.03, mp_, w, (0, 0, 0.012), contorno=0.0, seg=24, an=12)   # tampa a boca da manga (vista de perto, o oco aparecia claro)
            if luvas:
                esfera(f"{nome}_luva{s}", 0.068, 0.06, 0.085, M("#f4f1ea"), w, (0, 0, -0.06), contorno=0.005, seg=36, an=20)
                for i, dx in enumerate((-0.045, -0.015, 0.015, 0.045)):
                    tubo(f"{nome}_dedo{s}{i}", [(dx, 0, -0.1), (dx, 0, -0.145)], [0.0125, 0.0125], M("#f4f1ea"), w, seg=14, tampa=5, contorno=0.003)
                esfera(f"{nome}_pol{s}", 0.022, 0.022, 0.04, M("#f4f1ea"), w, (-0.06 if s == "F" else 0.06, -0.02, -0.07), contorno=0.003, seg=16, an=10)
            else:
                esfera(f"{nome}_mao{s}", 0.041, 0.04, 0.043, mp_, w, (0.002, 0, -0.042), contorno=0.004, seg=36, an=20)

    def fecha_mao(self, s="F", cor=PELE, em=None):
        """troca a mão redonda por um punho fechado (palma, quatro dedos dobrados com os nós, polegar por cima): para close de mão.
        em = quadro em que a mão fecha (antes dele fica a mão redonda); sem 'em', fica fechada o tempo todo.
        Devolve a junta 'pega' (entre o polegar e o indicador), onde se prende o que ele pegou (a mosca)"""
        from lib import key
        m = bpy.data.objects.get(f"{self.nome}_mao{s}")
        w = self.punho[s]; antes = set(w.children)
        if m is not None:
            m.scale = (0.0001,) * 3
            if em is not None:
                m.scale = (1, 1, 1); key(m, "scale", em - 1, "CONSTANT"); m.scale = (0.0001,) * 3; key(m, "scale", em, "CONSTANT")
        M = estilo(cor, borda=self.borda)
        esfera(f"{self.nome}_palma{s}", 0.047, 0.04, 0.05, M, w, (0, 0.004, -0.048), contorno=0.004, seg=32, an=18)
        for i, x in enumerate((-0.033, -0.011, 0.011, 0.033)):
            tubo(f"{self.nome}_dedo{s}{i}", [(x, -0.012, -0.088), (x, -0.04, -0.08), (x, -0.046, -0.052)], [0.0158, 0.0158, 0.0152], M, w, seg=16, tampa=6, contorno=0.0035)
            esfera(f"{self.nome}_no{s}{i}", 0.0165, 0.0165, 0.0165, M, w, (x, -0.02, -0.09), contorno=0.0035, seg=16, an=10)
        sx = -1 if s == "F" else 1
        tubo(f"{self.nome}_polegar{s}", [(sx * 0.05, -0.008, -0.03), (sx * 0.035, -0.045, -0.035), (sx * 0.012, -0.056, -0.042)], [0.016, 0.0155, 0.0145], M, w, seg=16, tampa=6, contorno=0.0035)
        if em is not None:
            for o in set(w.children) - antes:
                o.scale = (0.0001,) * 3; key(o, "scale", em - 1, "CONSTANT"); o.scale = (1, 1, 1); key(o, "scale", em, "CONSTANT")
        return junta(f"{self.nome}_pega{s}", w, (sx * 0.004, -0.062, -0.03))

    def espalma(self, s="B", cor=PELE, em=None):
        """mão aberta em concha (palma larga, quatro dedos juntos levemente dobrados, polegar aberto): para receber algo por baixo.
        A palma olha para -Y do pulso (com o braço estendido e ombro + cotovelo + punho = -90, ela fica virada para cima).
        em = quadro em que a mão abre (antes fica a mão redonda). Devolve a junta 'palma' no centro da palma, onde o objeto pousa"""
        from lib import key
        m = bpy.data.objects.get(f"{self.nome}_mao{s}")
        w = self.punho[s]; antes = set(w.children)
        if m is not None:
            m.scale = (0.0001,) * 3
            if em is not None:
                m.scale = (1, 1, 1); key(m, "scale", em - 1, "CONSTANT"); m.scale = (0.0001,) * 3; key(m, "scale", em, "CONSTANT")
        M = estilo(cor, borda=self.borda)
        esfera(f"{self.nome}_palmaA{s}", 0.05, 0.02, 0.052, M, w, (0, 0.006, -0.058), contorno=0.004, seg=32, an=18)
        for i, x in enumerate((-0.033, -0.011, 0.011, 0.033)):
            ln = 0.06 if i in (1, 2) else 0.052
            tubo(f"{self.nome}_dedoA{s}{i}", [(x, 0.0, -0.098), (x, -0.006, -0.098 - ln * 0.6), (x, -0.02, -0.098 - ln)], [0.0145, 0.014, 0.013], M, w, seg=16, tampa=6, contorno=0.0035)
        sx = -1 if s == "F" else 1
        tubo(f"{self.nome}_polegarA{s}", [(sx * 0.045, 0.0, -0.045), (sx * 0.068, -0.012, -0.07), (sx * 0.075, -0.024, -0.09)], [0.016, 0.015, 0.014], M, w, seg=16, tampa=6, contorno=0.0035)
        if em is not None:
            for o in set(w.children) - antes:
                o.scale = (0.0001,) * 3; key(o, "scale", em - 1, "CONSTANT"); o.scale = (1, 1, 1); key(o, "scale", em, "CONSTANT")
        return junta(f"{self.nome}_palma{s}", w, (0, -0.016, -0.07))

    def pe_no_chao(self, **pose):
        """acerta 'alt' (altura do quadril) para que o pé mais baixo fique no chão nessa pose (agachar sem afundar nem flutuar)"""
        if getattr(self, "_z_pe", None) is None:                                  # altura do tornozelo de pé, medida uma vez
            self.pose(alt=0.86); bpy.context.view_layer.update()
            self._z_pe = min(self.tornozelo[s].matrix_world.translation.z for s in "FB")
        z0 = self._z_pe
        P = dict(pose); P.setdefault("alt", 0.86)
        self.pose(**P); bpy.context.view_layer.update()
        pe = min(self.tornozelo[s].matrix_world.translation.z for s in "FB")
        P["alt"] = P["alt"] - (pe - z0)
        return P

    # ---------------------------------------------------------------- rosto
    def _sobre_cabeca(self, x, z, k=1.0):
        """ponto na casca da cabeça (frente = -Y) para um traço do rosto 2D: x e z em unidades do 2D (raio 0,2); k afasta da casca"""
        r = self.R; xx = x * r / 0.2; zz = z * r / 0.2
        y = -math.sqrt(max(r * r - xx * xx - zz * zz, 1e-6))
        return Vector((0, 0, r)) + Vector((xx, y, zz)) * k

    def _rosto(self, C, r, M):
        br = plano("#f3efe6"); self._br = br; self._C = C
        self.olhos, self.sobrancelhas = {}, {}
        s2 = r / 0.2
        for s, x in (("F", -0.074), ("B", 0.074)):
            p = self._sobre_cabeca(x, 0.012, 0.995)
            e = esfera(f"{self.nome}_olho{s}", 0.050 * s2, 0.012 * s2, 0.062 * s2, br, C, p, contorno=0.0, seg=32, an=18)
            n = Vector((p.x, p.y, p.z - r)).normalized()
            e.rotation_mode = "QUATERNION"; e.rotation_quaternion = n.to_track_quat("Y", "Z")
            e.rotation_mode = "XYZ"; self.olhos[s] = e
            # pálpebra (meia casca preta) que desce do alto do olho para o "esperto", "bravo" e "sono"
            lid = esfera(f"{self.nome}_palpebra{s}", 0.054 * s2, 0.014 * s2, 0.064 * s2, M(PELE, PELE), C, self._sobre_cabeca(x, 0.012 + 0.04, 0.99), contorno=0.0, seg=32, an=18)
            lid.rotation_mode = "QUATERNION"; lid.rotation_quaternion = n.to_track_quat("Y", "Z"); lid.rotation_mode = "XYZ"
            lid.scale.z = 0.0001; self.olhos[s + "_lid"] = lid
            # sobrancelha: tubo branco fino e curvo logo acima do olho
            pts = []
            for i in range(9):
                u = i / 8; xx = x + (-0.032 + 0.064 * u); zz = 0.118 + 0.012 * (1 - (u * 2 - 1) ** 2)
                pts.append(self._sobre_cabeca(xx, zz, 1.004))
            b = tubo(f"{self.nome}_sobr{s}", pts, [0.0058 * s2] * 9, br, C, seg=10, tampa=4, contorno=0.0)
            self.sobrancelhas[s] = b
        self.boca = None
        self.rosto(boca="reta")

    def rosto(self, boca="reta", lid=0.0, brow=0.0):
        """expressão simples: boca = reta | sorriso | triste | o ; lid = 0..1 (pálpebra descendo) ; brow = graus de inclinação da sobrancelha"""
        if self.boca is not None:
            bpy.data.objects.remove(self.boca, do_unlink=True)
        s2 = self.R / 0.2; pts = []
        for i in range(11):
            u = i / 10; x = -0.04 + 0.08 * u; v = (u * 2 - 1) ** 2
            z = -0.098 + (0.028 * v if boca == "sorriso" else 0.02 * (1 - v) if boca == "triste" else 0.0)
            pts.append(self._sobre_cabeca(x, z, 1.004))
        if boca == "o":
            p = self._sobre_cabeca(0.0, -0.098, 0.995)
            self.boca = esfera(f"{self.nome}_boca", 0.018 * s2, 0.01 * s2, 0.024 * s2, self._br, self._C, p, contorno=0.0, seg=24, an=14)
            n = Vector((p.x, p.y, p.z - self.R)).normalized(); self.boca.rotation_mode = "QUATERNION"; self.boca.rotation_quaternion = n.to_track_quat("Y", "Z"); self.boca.rotation_mode = "XYZ"
        else:
            self.boca = tubo(f"{self.nome}_boca", pts, [0.0048 * s2] * 11, self._br, self._C, seg=10, tampa=4, contorno=0.0)
        for s in ("F", "B"):
            self.olhos[s + "_lid"].scale.z = max(0.0001, lid)
            self.sobrancelhas[s].rotation_euler = (0, 0, 0)
        return self

    def expressao(self, chaves, f0, f1, piscar=True, seed=7):
        """o rosto muda com a história. chaves = [(quadro, dict(boca=reta|sorriso|triste|o, lid=0..1, brow=-1..1, olhos=1.0)), ...]
        lid = pálpebra baixa (foco, sono); brow = sobrancelha (+ sobe no susto, - desce na raiva/foco); olhos = tamanho (1,15 no susto).
        Pisca sozinho a cada 2 a 4 s (3 quadros), e pisca também logo depois de cada troca forte de expressão"""
        import random
        from lib import key
        rnd = random.Random(seed); s2 = self.R / 0.2
        ks = sorted(chaves, key=lambda k: k[0])
        base = dict(boca="reta", lid=0.0, brow=0.0, olhos=1.0)
        def em(f):
            ant = [k for k in ks if k[0] <= f]; prx = [k for k in ks if k[0] > f]
            A_ = dict(base, **(ant[-1][1] if ant else (ks[0][1] if ks else {})))
            if not prx or not ant:
                return A_, A_, 0.0
            B_ = dict(base, **prx[0][1]); fa_, fb_ = ant[-1][0], prx[0][0]
            u = min(1.0, (f - fa_) / max(1, min(6, fb_ - fa_))); u = u * u * (3 - 2 * u)      # muda em até 6 quadros, não de uma vez
            return A_, B_, u
        # as bocas: uma de cada, trocadas por visibilidade
        if self.boca is not None:
            self.boca.scale = (0.0001,) * 3
        bocas = {}
        for tipo in ("reta", "sorriso", "triste", "o"):
            antes = self.boca; self.boca = None; self.rosto(boca=tipo); bocas[tipo] = self.boca; self.boca = antes
            bocas[tipo].name = f"{self.nome}_boca_{tipo}"
        piscadas = []
        f = f0 + rnd.randint(10, 40)
        while f < f1:
            piscadas.append(f); f += rnd.randint(48, 96)
        for fk, _ in ks:
            piscadas.append(fk + 3)
        olhos_base = {s: tuple(self.olhos[s].scale) for s in ("F", "B")}
        sob_base = {s: self.sobrancelhas[s].location.z for s in ("F", "B")}
        ultimo = None
        for f in range(f0, f1 + 1):
            A_, B_, u = em(f)
            tipo = B_["boca"] if u >= 0.5 else A_["boca"]
            if tipo != ultimo:
                for t, o in bocas.items():
                    o.scale = (1, 1, 1) if t == tipo else (0.0001,) * 3; key(o, "scale", f, "CONSTANT")
                ultimo = tipo
            lid = A_["lid"] + (B_["lid"] - A_["lid"]) * u
            if piscar:
                for fp in piscadas:
                    d = f - fp
                    if 0 <= d <= 3:
                        lid = max(lid, (1.0, 1.7, 1.7, 0.6)[d] if d < 4 else lid)
            brow = A_["brow"] + (B_["brow"] - A_["brow"]) * u
            ol = A_["olhos"] + (B_["olhos"] - A_["olhos"]) * u
            for s in ("F", "B"):
                L = self.olhos[s + "_lid"]; L.scale.z = max(0.0001, lid); key(L, "scale", f, "LINEAR")
                E = self.olhos[s]; E.scale = tuple(v * ol for v in olhos_base[s]); key(E, "scale", f, "LINEAR")
                b = self.sobrancelhas[s]; b.location.z = sob_base[s] + 0.018 * s2 * brow; key(b, "location", f, "LINEAR")
        return self

    def pose(self, ombro=(0, 0), cotovelo=(0, 0), abre=(0, 0), quadril=(0, 0), joelho=(0, 0), tornozelo=(0, 0), tronco=0.0, cabeca=0.0, giro=0.0,
             inclina=0.0, pos=None, rot=None, alt=None, olha=0.0, punho=(0, 0)):
        """ângulos em graus. Braços/pernas: (F, B). Positivo = para trás; negativo = para a frente (o boneco olha para -Y).
        abre = abertura lateral do braço (positivo = para fora); punho = dobra do pulso (mesmo sentido do cotovelo).
        Palma para cima com o braço estendido: ombro + cotovelo + punho = -90"""
        for i, s in enumerate("FB"):
            sg = 1 if s == "F" else -1
            self.ombro[s].rotation_euler = (math.radians(ombro[i]), math.radians(abre[i] * sg), 0)
            self.cotovelo[s].rotation_euler = (math.radians(cotovelo[i]), 0, 0)
            self.punho[s].rotation_euler = (math.radians(punho[i]), 0, 0)
            self.perna[s].rotation_euler = (math.radians(quadril[i]), 0, 0)
            self.joelho[s].rotation_euler = (math.radians(joelho[i]), 0, 0)
            self.tornozelo[s].rotation_euler = (math.radians(tornozelo[i]), 0, 0)
        self.tronco.rotation_euler = (math.radians(tronco), 0, math.radians(giro))
        self.cabeca.rotation_euler = (math.radians(cabeca), 0, math.radians(olha))
        self.quadril.rotation_euler = (math.radians(inclina), 0, 0)
        if pos is not None:
            self.raiz.location = pos
        if rot is not None:
            r = rot if isinstance(rot, (tuple, list)) else (0, 0, rot)
            self.raiz.rotation_euler = tuple(math.radians(v) for v in r)
        if alt is not None:
            self.quadril.location.z = alt
        return self

    def _juntas(self):
        j = [self.tronco, self.cabeca, self.quadril, self.raiz]
        for d in (self.ombro, self.cotovelo, self.punho, self.perna, self.joelho, self.tornozelo):
            j += list(d.values())
        return j

    def grava(self, f, interp="LINEAR"):
        from lib import key
        for o in self._juntas():
            key(o, "rotation_euler", f, interp)
        key(self.quadril, "location", f, interp); key(self.raiz, "location", f, interp)
        sb = getattr(self, "sombra", None)
        if sb is not None:                                   # a sombra no chão acompanha o boneco (não gira nem sobe com ele)
            sb.location = (self.raiz.location.x, self.raiz.location.y + 0.05, 0.003); key(sb, "location", f, interp)

    # como cada parte reage (atraso em quadros, frequência da mola em Hz, amortecimento): o quadril puxa, o tronco vem logo,
    # o braço atrasa um pouco, o antebraço e a cabeça mais um pouco e passam do ponto antes de assentar (sobreposição e acompanhamento)
    # (23/10/2026, "mais leve, mais fluida"): amortecimento um pouco maior nas pontas; passam do ponto uma vez e assentam, sem o vai-e-volta de gelatina
    MOLAS = dict(pos=(0, 3.2, 0.8), rot=(0, 3.0, 0.75), alt=(0, 3.4, 0.7), inclina=(0, 3.0, 0.7), quadril=(0, 4.0, 0.66), joelho=(1, 4.2, 0.64),
                 tornozelo=(1, 4.2, 0.64), tronco=(1, 3.0, 0.64), giro=(1, 2.8, 0.64), ombro=(1, 4.6, 0.62), abre=(1, 4.6, 0.62),
                 cotovelo=(2, 5.0, 0.6), punho=(3, 5.5, 0.58), cabeca=(2, 3.2, 0.58), olha=(2, 3.0, 0.6))

    def anima(self, chaves, f0=None, f1=None, vida=1.0, seed=3, passo=1, mola=True, molas=None):
        """chaves = [(quadro, dict(pose...)), ...]. Animação de animador, não de robô:
        1) entre as chaves a curva é cúbica monótona: a velocidade passa pelas poses sem parar a cada uma (nada de anda-para-anda);
        2) cada parte segue esse alvo por uma mola própria (MOLAS): o quadril lidera, o braço e a cabeça chegam depois,
           passam um pouco do ponto e assentam; numa pose mantida o corpo continua vivo;
        3) por cima, respiração e balanço lento (vida).
        Qualquer parâmetro de pose() vale (tuplas item a item); pos = (x, y, z) e rot = giro em z (graus) também.
        A antecipação (recuar antes de ir) e a pose de chegada continuam sendo chaves: o motor cuida do caminho entre elas.
        molas = troca a mola de algumas partes (gesto seco, como pegar algo no ar: braço mais duro, chega e trava)."""
        import random
        chaves = sorted(dict((k[0], k) for k in chaves).values(), key=lambda k: k[0])      # duas chaves no mesmo quadro: vale a última
        f0 = chaves[0][0] if f0 is None else f0; f1 = chaves[-1][0] if f1 is None else f1
        rnd = random.Random(seed); fa, fb, fc = rnd.uniform(0, 6.28), rnd.uniform(0, 6.28), rnd.uniform(3.6, 5.0)
        base = dict(ombro=(0, 0), cotovelo=(0, 0), abre=(0, 0), quadril=(0, 0), joelho=(0, 0), tornozelo=(0, 0), tronco=0.0, cabeca=0.0, giro=0.0, inclina=0.0, olha=0.0,
                    punho=(0, 0))
        # canais escalares: nome -> [(quadro, valor)]; o que falta numa chave repete a chave anterior (ou a seguinte)
        nomes = set(base) | {k_ for _, d in chaves for k_ in d}
        canais = {}
        for nm in nomes:
            vals = []
            for fr, d in chaves:
                v = d.get(nm, base.get(nm))
                if isinstance(v, (int, float)) and nm == "rot":
                    v = (0.0, 0.0, float(v))
                vals.append((fr, v))
            if all(v is None for _, v in vals):
                continue
            ult = next(v for _, v in vals if v is not None)
            cheio = []
            for fr, v in vals:
                ult = v if v is not None else ult; cheio.append((fr, ult))
            if isinstance(cheio[0][1], (tuple, list)):
                for k in range(len(cheio[0][1])):
                    canais[(nm, k)] = [(fr, float(v[k])) for fr, v in cheio]
            else:
                canais[(nm, None)] = [(fr, float(v)) for fr, v in cheio]
        fs = list(range(f0, f1 + 1))
        saida = {}
        for ch, pts in canais.items():
            alvo = [_monotona(pts, f) for f in fs]
            tab = dict(self.MOLAS, **(molas or {}))
            if mola and ch[0] in tab:
                atr, hz, z = tab[ch[0]]
                alvo = [alvo[max(0, i - atr)] for i in range(len(alvo))]
                alvo = _segue_mola(alvo, hz, z)
            saida[ch] = alvo
        for i, f in enumerate(fs):
            P = {}
            for (nm, k), serie in saida.items():
                if k is None:
                    P[nm] = serie[i]
                else:
                    P.setdefault(nm, [0.0] * len([c for c in saida if c[0] == nm]))[k] = serie[i]
            P = {nm: (tuple(v) if isinstance(v, list) else v) for nm, v in P.items()}
            t = (f - f0) / 24.0
            P["tronco"] = P.get("tronco", 0.0) + vida * 1.3 * math.sin(2 * math.pi * t / fc + fa)
            P["cabeca"] = P.get("cabeca", 0.0) + vida * 1.8 * math.sin(2 * math.pi * t / (fc * 0.7) + fb)
            P["inclina"] = P.get("inclina", 0.0) + vida * 1.2 * math.sin(2 * math.pi * t / (fc * 1.6) + fb)        # o peso vai de um pé para o outro
            P["giro"] = P.get("giro", 0.0) + vida * 2.0 * math.sin(2 * math.pi * t / (fc * 1.3) + fa)            # o tronco gira um pouco
            P["olha"] = P.get("olha", 0.0) + vida * 2.5 * math.sin(2 * math.pi * t / (fc * 0.9) + fa + 1.3)      # o olhar passeia
            if "alt" in P and P["alt"] is not None:
                P["alt"] = P["alt"] + vida * 0.004 * math.sin(2 * math.pi * t / fc + fa)
            self.pose(**P); self.grava(f)
        return self



def _monotona(pts, f):
    """cúbica monótona (Fritsch-Carlson) por [(quadro, valor)]: velocidade contínua nas chaves, sem passar do valor da chave
    (quem passa do ponto é a mola, de propósito); nas pontas e onde a curva vira, a tangente é zero"""
    ks = pts
    if f <= ks[0][0]:
        return ks[0][1]
    if f >= ks[-1][0]:
        return ks[-1][1]
    n = len(ks)
    d = [(ks[i + 1][1] - ks[i][1]) / max(1e-6, ks[i + 1][0] - ks[i][0]) for i in range(n - 1)]
    m = [0.0] * n
    for i in range(1, n - 1):
        if d[i - 1] * d[i] > 0:
            w1 = 2 * (ks[i + 1][0] - ks[i][0]) + (ks[i][0] - ks[i - 1][0]); w2 = (ks[i + 1][0] - ks[i][0]) + 2 * (ks[i][0] - ks[i - 1][0])
            m[i] = (w1 + w2) / (w1 / d[i - 1] + w2 / d[i])
    for i in range(n - 1):
        fa_, pa = ks[i]; fb_, pb = ks[i + 1]
        if fa_ <= f <= fb_:
            h = fb_ - fa_
            if h <= 0:
                return pb
            u = (f - fa_) / h
            h00 = 2 * u ** 3 - 3 * u ** 2 + 1; h10 = u ** 3 - 2 * u ** 2 + u; h01 = -2 * u ** 3 + 3 * u ** 2; h11 = u ** 3 - u ** 2
            return h00 * pa + h10 * h * m[i] + h01 * pb + h11 * h * m[i + 1]
    return ks[-1][1]


def _segue_mola(alvo, hz, zeta, fps=24, sub=8):
    """a peça persegue o alvo como uma mola amortecida: começa devagar, acelera, passa um pouco do ponto e assenta"""
    w = 2 * math.pi * hz; x = alvo[0]; v = 0.0; out = []
    dt = 1.0 / (fps * sub)
    for i, a in enumerate(alvo):
        a0 = alvo[i - 1] if i else a
        for s_ in range(sub):
            at = a0 + (a - a0) * (s_ + 1) / sub
            v += (w * w * (at - x) - 2 * zeta * w * v) * dt; x += v * dt
        out.append(x)
    return out

def corrida(f0, f1, de, ate, rot=180.0, ciclo=12, inclina=14, alt=0.84, bracos=None, arranque=0.3, freia=0.0):
    """chaves de uma corrida de 'de' a 'ate' (x, y, z), oito por ciclo (duas passadas):
    pernas e braços contrários, o cotovelo fecha quando o braço vai à frente e abre quando vai atrás, o tronco gira com os ombros e a cabeça
    compensa (o olhar fica firme), a perna de trás chuta para cima na recuperação e o corpo desce no apoio e sobe no voo.
    arranque / freia = fração do tempo acelerando do zero / freando até parar (velocidade em trapézio): as primeiras e as últimas passadas
    são curtas, o corpo não sai nem chega a toda (pedido de 23/10/2026: "mais leve, mais fluido"; antes saía parado já em velocidade máxima)"""
    ch = []; n = max(2, int((f1 - f0) / (ciclo / 8)))
    a_, b_ = max(1e-3, arranque), max(1e-3, freia); V = 1.0 / (1.0 - a_ / 2 - b_ / 2)
    def andou(u):
        if u < a_:
            return V * u * u / (2 * a_)
        if u <= 1 - b_:
            return V * (a_ / 2 + u - a_)
        w = u - (1 - b_)
        return V * (a_ / 2 + (1 - b_ - a_) + w - w * w / (2 * b_))
    for i in range(n + 1):
        u = i / n; f = f0 + int(round((f1 - f0) * u)); th = 2 * math.pi * i / 8
        pos = tuple(a + (b - a) * andou(u) for a, b in zip(de, ate))
        k = min(1.0, 0.45 + 0.55 * u / a_, 0.45 + 0.55 * (1 - u) / b_) if (arranque or freia) else 1.0   # passada curta no arranque e na freada
        sF, sB = k * math.sin(th), -k * math.sin(th); cF, cB = math.cos(th), -math.cos(th)
        joF = 14 + k * 95 * max(0.0, cF) ** 1.3; joB = 14 + k * 95 * max(0.0, cB) ** 1.3         # recuperação: o calcanhar sobe
        coF = -78 - 22 * max(0.0, -sF); coB = -78 - 22 * max(0.0, -sB)                           # braço à frente: cotovelo mais fechado
        ch.append((f, dict(pos=pos, rot=rot, quadril=(-55 * sF, -55 * sB), joelho=(joF, joB), tornozelo=(10 + k * 18 * max(0.0, -cF), 10 + k * 18 * max(0.0, -cB)),
                           ombro=(60 * sF, 60 * sB), cotovelo=(coF, coB), abre=(12, 12), tronco=-inclina * (0.6 + 0.4 * k), giro=-9 * sF, olha=6 * sF, inclina=0.0,
                           alt=alt - 0.035 * k * abs(math.cos(th)))))
        if bracos:                                                       # correr carregando algo: os braços ficam no colo, o tronco gira menos
            ch[-1][1].update(bracos); ch[-1][1]["giro"] = -3 * sF; ch[-1][1]["olha"] = 2 * sF
    return ch

def bola3d(nome, loc, r=0.11, pai=None):
    """bola de futebol em 3D: esfera branca com manchas escuras achatadas na casca (vale de qualquer ângulo)"""
    raiz = empty(nome, pai, loc)
    esfera(nome + "_b", r, r, r, estilo("#f4f1ea", "#bdb8aa"), raiz, (0, 0, 0), contorno=0.004, seg=40, an=24)
    dirs = [Vector(v).normalized() for v in ((0, -1, 0), (0, 1, 0), (1, 0, 0), (-1, 0, 0), (0, 0, 1), (0, 0, -1), (0.7, -0.7, 0.7), (-0.7, -0.7, -0.7), (-0.7, 0.7, 0.7), (0.7, 0.7, -0.7))]
    for i, d in enumerate(dirs):
        e = esfera(f"{nome}_m{i}", r * 0.34, r * 0.07, r * 0.34, estilo("#1c2230"), raiz, d * r * 0.985, contorno=0.0, seg=14, an=8)
        e.rotation_mode = "QUATERNION"; e.rotation_quaternion = d.to_track_quat("Y", "Z"); e.rotation_mode = "XYZ"
    return raiz
