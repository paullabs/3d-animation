"""Objetos novos do plano de cena v2 de "E se cada passo dobrasse a sua altura?" (25/10/2026):
ônibus, ponto de ônibus, relógio de rua, poça, prédio alto com terraço, caixa d'água e balancim, fio de cabelo com escamas, régua de macro,
avião de cruzeiro, órbita, o Burj Khalifa fiel (planta em Y, 27 recuos em espiral, aletas verticais, agulha) com o centro de Dubai,
e o PALCO DE MEDIDA (fundo limpo, régua nova com número ao lado, fantasmas dos tamanhos anteriores).
Tudo em metros reais, mesmo acabamento do herói (tom chapado, sombra, borda de luz, contorno). A frente olha para -y."""
import math, random
import bpy, bmesh
from mathutils import Vector, Matrix
import lib
from lib import empty, srgb
import heroi3d as H3
from heroi3d import esfera, tubo, _objeto, estilo, plano, _mix
import objetos3d_abrigo as O3
import cidade3d as C3
import cena, props
import objetos3d_passos as OP

M = OP.M
AMBAR = OP.AMBAR
AMBAR_ESC = "#a8560a"                        # o mesmo número em âmbar escuro, para fundo claro (palco de dia, céu, Dubai)


def caixa(nome, tam, mat, loc, cont=0.02, chanfro=0.0, pai=None, rot=None):
    return O3.caixa(nome, tam, mat, pai, loc, chanfro=chanfro, contorno=cont, rot=rot)


# ---------------------------------------------------------------- rua
def onibus(nome, loc=(0, 0, 0), rot=0.0, cor="#e9e4d8", faixa="#d0452c"):
    """ônibus urbano (12 x 2,5 x 3,2 m): carroceria clara com faixa, janelas, para-brisa, portas, rodas e ar-condicionado; comprimento ao longo de y"""
    r = empty(nome, None, loc); r.rotation_euler.z = math.radians(rot)
    mc, mf, mv, mp = M(cor, "#bdb7a8"), M(faixa, "#8e2c1c"), M("#1d2a32", "#121a20", "#7a9aa8"), M("#2a2a2e", "#1a1a1e")
    caixa(nome + "_corpo", (2.5, 12.0, 2.65), mc, (0, 0, 1.68), cont=0.02, chanfro=0.12, pai=r)
    caixa(nome + "_faixa", (2.52, 11.9, 0.32), mf, (0, 0, 1.02), cont=0.0, pai=r)
    for s in (-1, 1):
        caixa(f"{nome}_jan{s}", (0.04, 9.4, 1.0), mv, (s * 1.26, 0.6, 2.15), cont=0.0, pai=r)
        for k in range(6):
            caixa(f"{nome}_col{s}{k}", (0.05, 0.08, 1.0), mc, (s * 1.27, -4.0 + 1.6 * k + 0.6, 2.15), cont=0.0, pai=r)
    caixa(nome + "_parabrisa", (2.3, 0.04, 1.35), mv, (0, -6.01, 2.0), cont=0.0, pai=r)
    caixa(nome + "_letreiro", (1.8, 0.05, 0.28), M("#1a1a1a"), (0, -6.02, 2.85), cont=0.0, pai=r)
    t = lib.text(nome + "_dest", "CENTRO", 0.2, O3.brilha("#ffb340", 1.6), r, (0, -6.05, 2.83), lib.font()); t.rotation_euler = (math.pi / 2, 0, 0)
    caixa(nome + "_porta1", (0.04, 1.1, 2.1), mv, (-1.27, -4.6, 1.4), cont=0.0, pai=r)
    caixa(nome + "_porta2", (0.04, 1.1, 2.1), mv, (-1.27, 1.2, 1.4), cont=0.0, pai=r)
    caixa(nome + "_ac", (1.6, 2.4, 0.3), M("#cfcac0"), (0, 1.0, 3.1), cont=0.01, chanfro=0.05, pai=r)
    for s in (-1, 1):
        for y in (-3.9, 3.6):
            O3.cilindro(f"{nome}_roda{s}{y}", 0.5, 0.32, mp, r, (s * 1.1, y, 0.5), seg=28, eixo="X", contorno=0.01)
            O3.cilindro(f"{nome}_calota{s}{y}", 0.26, 0.34, M("#9aa0a4"), r, (s * 1.1, y, 0.5), seg=20, eixo="X", contorno=0.0)
    for s in (-1, 1):
        caixa(f"{nome}_farol{s}", (0.4, 0.05, 0.18), O3.brilha("#fff4d8", 1.2), (s * 0.85, -6.02, 0.75), cont=0.0, pai=r)
    return r


def ponto_onibus(nome, loc=(0, 0, 0), rot=0.0):
    """abrigo de ponto de ônibus: duas colunas, cobertura, vidro de fundo, banco e a placa redonda"""
    r = empty(nome, None, loc); r.rotation_euler.z = math.radians(rot)
    mm = M("#5d6670", "#3e454c")
    for x in (-1.4, 1.4):
        O3.cilindro(f"{nome}_col{x}", 0.05, 2.5, mm, r, (x, 0.5, 1.25), seg=14, contorno=0.006)
    caixa(nome + "_teto", (3.2, 1.5, 0.08), M("#d9dcd8", "#aab0ae"), (0, 0.15, 2.52), cont=0.01, chanfro=0.02, pai=r)
    caixa(nome + "_vidro", (2.8, 0.03, 1.8), O3.vidro("#cfe6ee", 0.16, 0.5), (0, 0.6, 1.25), cont=0.0, pai=r)
    caixa(nome + "_banco", (2.2, 0.4, 0.06), M("#8a6a4a", "#5e4630"), (0, 0.38, 0.48), cont=0.006, chanfro=0.01, pai=r)
    O3.cilindro(nome + "_poste", 0.035, 2.6, mm, r, (1.9, 0.1, 1.3), seg=12, contorno=0.006)
    O3.cilindro(nome + "_placa", 0.28, 0.03, M("#1f5ea8", "#174680"), r, (1.9, 0.08, 2.45), seg=32, eixo="Y", contorno=0.006)
    t = lib.text(nome + "_pt", "ÔNIBUS", 0.09, plano("#ffffff"), r, (1.9, 0.06, 2.45), lib.font()); t.rotation_euler = (math.pi / 2, 0, 0)
    return r


def relogio_rua(nome, loc=(0, 0, 0), hora=(10, 8), seg=0.0):
    """relógio de praça num poste (3,6 m), mostrador de frente para -y, com ponteiro de segundos vermelho"""
    r = empty(nome, None, loc)
    mm = M("#2f4a3e", "#1f332a")
    O3.cilindro(nome + "_poste", 0.07, 3.0, mm, r, (0, 0, 1.5), seg=16, contorno=0.008)
    O3.cilindro(nome + "_caixa", 0.42, 0.22, mm, r, (0, 0, 3.35), seg=40, eixo="Y", contorno=0.008)
    O3.cilindro(nome + "_mostr", 0.36, 0.02, M("#f4efe2", "#d8d1bf"), r, (0, -0.115, 3.35), seg=48, eixo="Y", contorno=0.0)
    mk = M("#1d1d1d")
    for i in range(12):
        a = math.radians(i * 30)
        caixa(f"{nome}_h{i}", (0.02, 0.01, 0.06 if i % 3 else 0.09), mk, (0.3 * math.sin(a), -0.13, 3.35 + 0.3 * math.cos(a)), cont=0.0, pai=r, rot=(0, i * 30, 0))
    for nm, ang, comp, larg, cor in (("hora", (hora[0] % 12 + hora[1] / 60) * 30, 0.18, 0.026, "#1d1d1d"), ("min", hora[1] * 6, 0.27, 0.018, "#1d1d1d"),
                                     ("seg", seg * 6, 0.3, 0.008, "#c8302a")):
        pv = empty(f"{nome}_{nm}_pv", r, (0, -0.14, 3.35)); pv.rotation_euler = (0, math.radians(ang), 0)
        caixa(f"{nome}_{nm}", (larg, 0.008, comp), M(cor, cor), (0, 0, comp / 2 - 0.03), cont=0.0, pai=pv)
    return r


def poca(nome, loc, rx=0.9, ry=0.6, ceu="#9cc0d8"):
    """poça d'água no asfalto: o céu refletido, borda escura e um brilho"""
    x, y, z = loc
    cena.ground_disc(nome + "_borda", rx * 1.06, ry * 1.08, props.FM("#2a2e2c"), (x, y, z + 0.004), n=48)
    cena.ground_disc(nome, rx, ry, props.FM(ceu), (x, y, z + 0.006), n=48)
    cena.ground_disc(nome + "_brilho", rx * 0.35, ry * 0.12, props.FM("#e8f2f6"), (x - rx * 0.3, y - ry * 0.3, z + 0.008), n=24)


def ondas_poca(nome, loc, n=3, r0=0.15, passo=0.15):
    for i in range(n):
        O3.anel(f"{nome}_{i}", r0 + i * passo, 0.008, props.FM("#e8f2f6"), None, (loc[0], loc[1], loc[2] + 0.012), eixo="Z", seg=48, contorno=0.0)


def predio_alto(nome, cx, cy, andares, w=None, cor="#8a93a0", terraco=True, balancim=False, limpador=None, face_balancim="frente"):
    """prédio de 'andares' andares (3 m cada) com terraço (parapeito), caixa d'água e antena; balancim de limpeza pendurado na fachada da frente,
    perto do topo, com os cabos e a grade; 'limpador' = função que põe o boneco do limpador em (x, y, z do piso do balancim)"""
    h = andares * 3.0
    w = w or max(9.0, h * 0.36)
    d = w * 0.85
    OP.torre(nome, cx, cy, w, d, h, cor=cor)
    if terraco:
        mp = M(_mix(cor, "#ffffff", 0.2), _mix(cor, "#000000", 0.2))
        for k, (tx, ty, sx, sy) in enumerate(((0, -d / 2, w, 0.25), (0, d / 2, w, 0.25), (-w / 2, 0, 0.25, d), (w / 2, 0, 0.25, d))):
            caixa(f"{nome}_parap{k}", (sx, sy, 1.1), mp, (cx + tx, cy + ty, h + 0.8 + 0.55), cont=0.03)
        caixa(nome + "_caixa", (3.2, 2.6, 2.4), M("#c9c6bc", "#9a978e"), (cx + w * 0.22, cy + d * 0.15, h + 0.8 + 1.2), cont=0.03)
        O3.cilindro(nome + "_antena", 0.06, 4.0, M("#5a5e62"), None, (cx - w * 0.3, cy + d * 0.2, h + 2.8), seg=10, contorno=0.0)
    if balancim:
        zb = h - 4.6
        mb = M("#c9a23a", "#8e7024")
        piv = empty(nome + "_bal", None, (cx, cy, 0.0))
        if face_balancim == "esq":                                         # na fachada que olha para -x (para a rua)
            piv.rotation_euler.z = math.radians(-90); dist = w / 2
        else:
            dist = d / 2
        yb = -dist - 0.75
        caixa(nome + "_bal_piso", (5.0, 0.8, 0.12), M("#7a7e80", "#55585a"), (0, yb, zb), cont=0.02, pai=piv)
        for k, (zz, hh) in enumerate(((zb + 1.0, 0.06), (zb + 0.55, 0.05))):
            caixa(f"{nome}_bal_grade{k}", (5.0, 0.05, hh), mb, (0, yb - 0.38, zz), cont=0.01, pai=piv)
        for x in (-2.45, 0.0, 2.45):
            caixa(f"{nome}_bal_pe{x}", (0.06, 0.06, 1.0), mb, (x, yb - 0.38, zb + 0.5), cont=0.01, pai=piv)
        for x in (-2.2, 2.2):
            O3.cilindro(f"{nome}_cabo{x}", 0.025, h + 1.2 - zb, M("#2a2a2a"), piv, (x, yb, (h + 1.2 + zb) / 2), seg=8, contorno=0.0)
            caixa(f"{nome}_braco{x}", (0.2, 1.6, 0.2), M("#5a5e62"), (x, -dist - 0.3, h + 1.6), cont=0.01, pai=piv)
        if limpador:
            bpy.context.view_layer.update()
            p = piv.matrix_world @ Vector((-1.0, yb + 0.05, zb + 0.09))
            limpador(p.x, p.y, p.z, piv.rotation_euler.z)
    return h, w, d


def estacionamento(nome, cx, cy, comp=40.0, larg=30.0):
    cena.poly_mesh(nome, [(cx - larg / 2, cy - comp / 2, 0.01), (cx + larg / 2, cy - comp / 2, 0.01), (cx + larg / 2, cy + comp / 2, 0.01), (cx - larg / 2, cy + comp / 2, 0.01)], props.FM("#4a4d4a"))
    for i in range(int(larg / 2.6)):
        x = cx - larg / 2 + 1.3 + i * 2.6
        cena.poly_mesh(f"{nome}_v{i}", [(x - 0.06, cy - comp / 2 + 1, 0.015), (x + 0.06, cy - comp / 2 + 1, 0.015), (x + 0.06, cy - comp / 2 + 6, 0.015), (x - 0.06, cy - comp / 2 + 6, 0.015)], props.FM("#d8d3c4"))


# ---------------------------------------------------------------- macro e instrumentos
def fio_escamas(nome, loc, diam, comp, eixo="Z", cor="#3a2618", n=None):
    """fio de cabelo visto de perto: as escamas da cutícula são anéis cônicos encaixados uns nos outros"""
    x, y, z = loc
    n = n or max(6, int(comp / (diam * 1.1)))
    passo = comp / n
    m = M(cor, _mix(cor, "#000000", 0.5), "#8a6a50")
    for i in range(n):
        c = -comp / 2 + (i + 0.5) * passo
        pos = (x, y, z + c) if eixo == "Z" else (x + c, y, z)
        O3.cilindro(f"{nome}_e{i}", diam * 0.485, passo * 1.01, m, None, pos, seg=28, eixo=eixo, r2=diam * 0.515, contorno=diam * 0.02)


def regua_macro(nome, loc, comp, divisao, rotulos, unidade, larg=None, eixo="X"):
    """régua de mesa (creme, riscos pretos): comp = tamanho na cena; divisao = espaço entre riscos; rotulos = a cada quantos riscos vai um número"""
    x, y, z = loc
    larg = larg or comp * 0.12
    caixa(nome, (comp, 0.02, larg), M("#efe6cc", "#cfc4a4"), (x, y, z), cont=0.004)
    n = int(round(comp / divisao))
    for i in range(n + 1):
        xx = x - comp / 2 + i * divisao
        grande = i % rotulos == 0
        caixa(f"{nome}_r{i}", (divisao * 0.08, 0.03, larg * (0.42 if grande else 0.22)), M("#1d1d1d", "#1d1d1d"), (xx, y - 0.012, z + larg / 2 - larg * (0.21 if grande else 0.11)), cont=0.0)
        if grande:
            OP.texto(f"{nome}_n{i}", f"{i // rotulos}", larg * 0.26, (xx, y - 0.015, z - larg * 0.12), cor="#1d1d1d", forca=0.0)
    OP.texto(nome + "_u", unidade, larg * 0.22, (x + comp / 2 - larg * 1.3, y - 0.015, z - larg * 0.3), cor="#1d1d1d", forca=0.0)


def aviao(nome, loc, s=1.0, rot=0.0):
    """avião de passageiros (38 m de envergadura) visto de lado/baixo: fuselagem, asas enflechadas, motores e cauda"""
    r = empty(nome, None, loc); r.scale = (s,) * 3; r.rotation_euler.z = math.radians(rot)
    mb, mg, ma = M("#f2f2ee", "#c4c6c4"), M("#9aa2a8", "#6e767c"), M("#1f5ea8", "#174680")
    tubo(nome + "_fus", [(-19, 0, 0.6), (-16, 0, 0), (14, 0, 0), (17.5, 0, -0.2)], [0.45, 1.95, 1.95, 1.25], mb, r, seg=32, tampa=8, contorno=0.08)
    for s_ in (-1, 1):                                                       # asas enflechadas e profundores (caixas giradas)
        caixa(f"{nome}_asa{s_}", (5.5, 17.5, 0.5), M("#c9ced2", "#8e969c"), (-2.5, s_ * 9.8, -0.5), cont=0.08, pai=r, rot=(s_ * 4, 0, s_ * 18))
        O3.cilindro(f"{nome}_mot{s_}", 1.1, 4.0, mg, r, (0.8, s_ * 6.0, -1.5), seg=24, eixo="X", contorno=0.06)
        caixa(f"{nome}_ept{s_}", (2.6, 6.0, 0.3), mg, (-17.0, s_ * 3.6, 0.8), cont=0.05, pai=r, rot=(0, 0, s_ * 22))
    bm = bmesh.new()
    v = [bm.verts.new(p) for p in ((-13, 0, 1.6), (-18.5, 0, 1.6), (-19.5, 0, 8.0), (-17.5, 0, 8.0))]
    bm.faces.new(v); bmesh.ops.solidify(bm, geom=bm.faces[:], thickness=0.3)
    _objeto(nome + "_leme", bm, ma, r, (0, -0.15, 0), 0.05)
    caixa(nome + "_faixa_e", (30.0, 0.05, 0.35), ma, (-1.0, -1.93, 0.2), cont=0.0, pai=r)
    caixa(nome + "_faixa_d", (30.0, 0.05, 0.35), ma, (-1.0, 1.93, 0.2), cont=0.0, pai=r)
    return r


def raio_x(h, cor="#2b4f86", alfa=0.32):
    """o boneco vira silhueta translúcida azul (corte de raio X): troca o material de tudo e tira o contorno"""
    m = O3.vidro(cor, alfa, 0.75)
    for o in [h.raiz] + list(h.raiz.children_recursive):
        if o.type == "MESH":
            o.data.materials.clear(); o.data.materials.append(m)
            for md in list(o.modifiers):
                o.modifiers.remove(md)


def coracao(nome, loc, s=1.0):
    mc = M("#d02a30", "#7a1418", "#ff9a8a")
    x, y, z = loc
    for sx in (-1, 1):
        esfera(f"{nome}_l{sx}", 0.04 * s, 0.04 * s, 0.042 * s, mc, None, (x + sx * 0.03 * s, y, z + 0.015 * s), contorno=0.004 * s, seg=24, an=14)
    O3.cilindro(nome + "_ponta", 0.004 * s, 0.07 * s, mc, None, (x, y, z - 0.025 * s), seg=20, r2=0.068 * s, contorno=0.004 * s)


def orbita(nome, centro, raio, r_tubo=0.004, cor="#cfd8e8", eixo="Z"):
    return O3.anel(nome, raio, r_tubo, O3.brilha(cor, 1.2), None, centro, eixo=eixo, seg=180, contorno=0.0)


# ---------------------------------------------------------------- o Burj Khalifa
def mat_burj():
    """vidro prateado-azulado com aletas verticais: listras finas que giram em volta do eixo da torre (anéis no plano xy), com a sombra do estilo"""
    m = bpy.data.materials.new("burj_vidro"); m.use_nodes = True
    nt = m.node_tree; N = nt.nodes; L = nt.links; N.clear()
    out = N.new("ShaderNodeOutputMaterial"); em = N.new("ShaderNodeEmission")
    tc = N.new("ShaderNodeTexCoord"); mul = N.new("ShaderNodeVectorMath"); mul.operation = "MULTIPLY"; mul.inputs[1].default_value = (1.0, 1.0, 0.0)
    wv = N.new("ShaderNodeTexWave"); wv.wave_type = "RINGS"; wv.inputs["Scale"].default_value = 0.55; wv.inputs["Distortion"].default_value = 0.0
    sp = N.new("ShaderNodeTexWave"); sp.wave_type = "BANDS"; sp.bands_direction = "Z"; sp.inputs["Scale"].default_value = 0.09
    rp = N.new("ShaderNodeValToRGB"); rp.color_ramp.interpolation = "CONSTANT"; e = rp.color_ramp.elements
    e[0].position = 0.0; e[0].color = (*srgb("#7e93a8"), 1); e[1].position = 0.78; e[1].color = (*srgb("#dfe8ef"), 1)
    rp2 = N.new("ShaderNodeValToRGB"); rp2.color_ramp.interpolation = "CONSTANT"; e2 = rp2.color_ramp.elements
    e2[0].position = 0.0; e2[0].color = (0.62, 0.66, 0.72, 1); e2[1].position = 0.12; e2[1].color = (1, 1, 1, 1)
    geo = N.new("ShaderNodeNewGeometry"); dot = N.new("ShaderNodeVectorMath"); dot.operation = "DOT_PRODUCT"; dot.inputs[1].default_value = tuple(H3.LUZ)
    mp = N.new("ShaderNodeMapRange"); mp.inputs[1].default_value = -1.0; mp.inputs[2].default_value = 1.0
    sh = N.new("ShaderNodeValToRGB"); sh.color_ramp.interpolation = "CONSTANT"; s = sh.color_ramp.elements
    s[0].position = 0.0; s[0].color = (0.55, 0.58, 0.66, 1); s[1].position = 0.47; s[1].color = (1, 1, 1, 1)
    lw = N.new("ShaderNodeLayerWeight"); lw.inputs["Blend"].default_value = 0.4
    m1 = N.new("ShaderNodeMix"); m1.data_type = "RGBA"; m1.blend_type = "MULTIPLY"; m1.inputs[0].default_value = 1.0
    m2 = N.new("ShaderNodeMix"); m2.data_type = "RGBA"; m2.blend_type = "MULTIPLY"; m2.inputs[0].default_value = 1.0
    m3 = N.new("ShaderNodeMix"); m3.data_type = "RGBA"; m3.blend_type = "SCREEN"; m3.inputs[7].default_value = (*srgb("#fff1d8"), 1)
    L.new(tc.outputs["Object"], mul.inputs[0]); L.new(mul.outputs[0], wv.inputs["Vector"]); L.new(wv.outputs["Fac"], rp.inputs[0])
    L.new(tc.outputs["Object"], sp.inputs["Vector"]); L.new(sp.outputs["Fac"], rp2.inputs[0])
    L.new(geo.outputs["Normal"], dot.inputs[0]); L.new(dot.outputs["Value"], mp.inputs[0]); L.new(mp.outputs["Result"], sh.inputs[0])
    L.new(rp.outputs["Color"], m1.inputs[6]); L.new(rp2.outputs["Color"], m1.inputs[7])
    L.new(m1.outputs[2], m2.inputs[6]); L.new(sh.outputs["Color"], m2.inputs[7])
    L.new(lw.outputs["Fresnel"], m3.inputs[0]); L.new(m2.outputs[2], m3.inputs[6])
    L.new(m3.outputs[2], em.inputs[0]); L.new(em.outputs[0], out.inputs[0])
    return m


def _asa(bm, ang, r0, comp, larg, z0, z1, seg=12):
    """uma asa da planta em Y: caixa do núcleo até 'comp' e ponta arredondada (meio cilindro), entre z0 e z1, girada 'ang'"""
    R = Matrix.Rotation(math.radians(ang), 4, "Z")
    hz = (z1 - z0)
    mid = (z0 + z1) / 2
    L = comp - larg / 2
    if L > r0:
        bmesh.ops.create_cube(bm, size=1.0, matrix=R @ Matrix.Translation(((r0 + L) / 2, 0, mid)) @ Matrix.Diagonal(((L - r0) + 0.01, larg, hz, 1.0)))
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=seg, radius1=larg / 2, radius2=larg / 2, depth=hz,
                          matrix=R @ Matrix.Translation((max(L, r0), 0, mid)))


def burj(nome, cx, cy, H=828.0, s=1.0):
    """o Burj Khalifa: núcleo hexagonal e três asas a 120 graus (planta em Y); 27 recuos que giram em espiral (cada recuo encurta uma asa,
    na ordem A, B, C, A...), aletas verticais no vidro, faixas técnicas mais escuras, pódio baixo em Y, e a agulha de ~585 m até 828 m"""
    mv = mat_burj()
    mf = M("#5d6a78", "#424c58", "#c8d4e0")
    L0, Lmin, larg, nucleo = 82.0, 20.0, 36.0, 21.0
    n = 27; zt = 594.0
    dz = zt / n
    objs = []
    for i in range(n):
        bm = bmesh.new()
        z0, z1 = i * dz, (i + 1) * dz
        for w, ang in enumerate((90.0, 210.0, 330.0)):
            passos = 0 if i < w else (i - w) // 3 + 1
            comp = L0 - (L0 - Lmin) * min(1.0, passos / 9.0)
            _asa(bm, ang, 0.0, comp, larg * (1.0 - 0.25 * passos / 9.0), z0, z1)
        bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=6, radius1=nucleo, radius2=nucleo, depth=z1 - z0, matrix=Matrix.Translation((0, 0, (z0 + z1) / 2)))
        bmesh.ops.scale(bm, vec=(s, s, s), verts=bm.verts)
        o = _objeto(f"{nome}_t{i}", bm, mv, None, (cx, cy, 0), 0.0)
        for p in o.data.polygons:
            p.use_smooth = False
        objs.append(o)
        if i % 4 == 3:                                                      # faixa técnica (andares de máquinas)
            bm = bmesh.new()
            for w, ang in enumerate((90.0, 210.0, 330.0)):
                passos = 0 if i < w else (i - w) // 3 + 1
                comp = L0 - (L0 - Lmin) * min(1.0, passos / 9.0)
                _asa(bm, ang, 0.0, comp + 0.4, larg * (1.0 - 0.25 * passos / 9.0) + 0.8, z1 - 3.0, z1 - 0.2)
            bmesh.ops.scale(bm, vec=(s, s, s), verts=bm.verts)
            _objeto(f"{nome}_f{i}", bm, mf, None, (cx, cy, 0), 0.0)
    # o núcleo continua e vira a agulha
    O3.cilindro(nome + "_nucleo", nucleo * 0.9 * s, 60 * s, mv, None, (cx, cy, (zt + 30) * s), seg=6, r2=nucleo * 0.55 * s, contorno=0.0)
    O3.cilindro(nome + "_agulha", nucleo * 0.5 * s, (H - zt - 60) * s, mv, None, (cx, cy, (zt + 60 + (H - zt - 60) / 2) * s), seg=8, r2=0.4 * s, contorno=0.0)
    for k, zz in enumerate((680, 730, 770)):
        O3.cilindro(f"{nome}_anel{k}", (6.5 - k * 1.6) * s, 3.0 * s, mf, None, (cx, cy, zz * s), seg=10, contorno=0.0)
    esfera(nome + "_ponta", 0.9 * s, 0.9 * s, 1.6 * s, O3.brilha("#fff4d8", 2.0), None, (cx, cy, H * s), contorno=0.0, seg=12, an=8)
    # pódio baixo em Y
    bm = bmesh.new()
    for ang in (90.0, 210.0, 330.0):
        _asa(bm, ang, 0.0, 150.0, 60.0, 0.0, 14.0)
    bmesh.ops.scale(bm, vec=(s, s, s), verts=bm.verts)
    _objeto(nome + "_podio", bm, M("#b7b2a2", "#8e897a"), None, (cx, cy, 0), 0.6)
    return objs


def dubai(cx, cy, seed=7, raio=1600.0, n_torres=70):
    """o centro de Dubai em volta do Burj: torres de 150 a 400 m (vidro e concreto claro), o lago da Dubai Fountain ao sul,
    a avenida Sheikh Zayed a oeste, areia do deserto"""
    rnd = random.Random(seed)
    OP.chao("#d6c196", None, 60000.0, nome="areia")
    cena.poly_mesh("cidade_chao", [(cx - raio, cy - raio, 0.02), (cx + raio, cy - raio, 0.02), (cx + raio, cy + raio, 0.02), (cx - raio, cy + raio, 0.02)], props.FM("#b9b3a2"))
    lago = [(cx + 260 * math.cos(a) * (1.35 if math.cos(a) > 0 else 1.0), cy - 330 + 120 * math.sin(a), 0.05) for a in [i * 2 * math.pi / 40 for i in range(40)]]
    cena.poly_mesh("lago", lago, props.FM("#3f86b0"))
    cena.poly_mesh("avenida", [(cx - 900, cy - raio, 0.04), (cx - 860, cy - raio, 0.04), (cx - 860, cy + raio, 0.04), (cx - 900, cy + raio, 0.04)], props.FM("#4a4c4e"))
    L = C3.Lote("dubai")
    tons = ["vidro", "claro", "azul", "areia"]
    for k in range(n_torres):
        a = rnd.uniform(0, 2 * math.pi); d = rnd.uniform(260, raio)
        x, y = cx + d * math.cos(a), cy + d * math.sin(a)
        if (x - cx) ** 2 / 360 ** 2 + (y - (cy - 330)) ** 2 / 170 ** 2 < 1.0 or abs(x - (cx - 880)) < 60:
            continue
        h = rnd.uniform(60, 180) if d > 0.6 * raio else rnd.uniform(140, 380)
        w = rnd.uniform(28, 55)
        L.caixa(rnd.choice(tons), (x, y, h / 2), (w, w * rnd.uniform(0.7, 1.2), h))
    mats = {"vidro": M("#6f8aa0", "#4e6476", "#cfe0ea"), "claro": M("#cfc9b8", "#a39d8c"), "azul": M("#4f7a9a", "#36566e", "#cfe0ea"), "areia": M("#c2ae88", "#958463")}
    return L.fecha(mats, contorno=0.8)


# ---------------------------------------------------------------- o palco de medida
PALCO = {
    "dia": dict(chao="#e6e2d8", hor="#eef0ec", meio="#d6e2ea", topo="#a9c4da", linha="#cfcabc"),
    "azul": dict(chao="#c9d6e2", hor="#dbe6f0", meio="#7fa8d4", topo="#1f4f96", linha="#a9bccd"),
    "preto": dict(chao="#1a1d26", hor="#20242e", meio="#0d1018", topo="#05070c", linha="#3a4050"),
    "dubai": dict(chao="#d6c196", hor="#f2dcc0", meio="#e8b98a", topo="#7fa0c4", linha="#c2ac84"),
}


def palco(tipo="dia", estrelas=False):
    """o palco: chão liso até o horizonte e o céu em degradê pela altura (nada além do que se mede)"""
    p = PALCO[tipo]
    bpy.context.scene.world.node_tree.nodes["Background"].inputs[0].default_value = (*srgb(p["hor"]), 1)
    OP.domo([(-900, p["chao"]), (-1, p["chao"]), (0, p["hor"]), (60, p["meio"]), (420, p["topo"])])
    cena.poly_mesh("palco_chao", [(-600, -600, 0), (600, -600, 0), (600, 600, 0), (-600, 600, 0)], O3.brilha(p["chao"], 1.0))
    if estrelas:
        OP.estrelas(n=180)


def fantasma(h, cor="#ffffff", alfa=0.34):
    """o tamanho anterior: o mesmo boneco em silhueta clara translúcida, sem contorno"""
    m = cena.amat(f"fantasma_{cor}_{alfa}", cor, 1.0, alfa)
    for o in [h.raiz] + list(h.raiz.children_recursive):
        if o.type == "MESH":
            o.data.materials.clear(); o.data.materials.append(m)
            for md in list(o.modifiers):
                o.modifiers.remove(md)


def fantasma_obj(objs, cor="#ffffff", alfa=0.34):
    m = cena.amat(f"fantasma_{cor}_{alfa}", cor, 1.0, alfa)
    for o0 in objs:
        for o in [o0] + list(o0.children_recursive):
            if o.type in ("MESH", "FONT"):
                o.data.materials.clear(); o.data.materials.append(m)
                for md in list(o.modifiers):
                    o.modifiers.remove(md)


def regua2(x, topo_u, topo_m, marcas_m=None, lado=-1, larg=0.07, y=0.0, tam=0.13, rotulo=None, fmt=None, escuro=False, cor_num=AMBAR, lado_rot=1):
    """régua nova do palco: fita creme fina; número âmbar AO LADO do topo (lado = -1: à esquerda da fita); 3 ou 4 marcas numeradas no meio;
    traço âmbar curto saindo do topo para dentro (na direção do boneco)"""
    k = topo_u / topo_m
    cor_txt = "#e8e4d8" if escuro else "#3a3a36"
    caixa("r2_fita", (larg, 0.02, topo_u), M("#f4eedc", "#d8cfb4"), (x, y, topo_u / 2), cont=0.003)
    if marcas_m is None:
        b = OP.bonito(topo_m / 4.0)
        marcas_m = [b * i for i in range(1, 10) if b * i < topo_m * 0.93]
    passo_fino = OP.bonito(topo_m / 20.0)
    i = 1
    while passo_fino * i < topo_m * 0.995:
        z = passo_fino * i * k
        caixa(f"r2_f{i}", (larg * 0.4, 0.03, 0.004), M("#2a2620", "#2a2620"), (x - lado * larg * 0.3, y - 0.012, z), cont=0.0)
        i += 1
    for j, mm in enumerate(marcas_m):
        z = mm * k
        caixa(f"r2_m{j}", (larg * 0.9, 0.03, 0.006), M("#2a2620", "#2a2620"), (x, y - 0.013, z), cont=0.0)
        OP.texto(f"r2_t{j}", (fmt or OP_fmt)(mm), tam * 0.62, (x + lado * (larg / 2 + 0.03), y - 0.02, z), cor=cor_txt, forca=1.0,
                 alinha="RIGHT" if lado < 0 else "LEFT")
    caixa("r2_topo", (0.12, 0.012, 0.01), O3.brilha(AMBAR, 1.5), (x + 0.06, y - 0.015, topo_u), cont=0.0)
    if lado_rot == 0:                                                     # o número centrado em cima da fita (não invade o boneco nem a moça)
        OP.texto("r2_rot", rotulo or (fmt or OP_fmt)(topo_m), tam, (x, y - 0.02, topo_u + tam * 0.9), cor=cor_num, forca=1.8 if cor_num == AMBAR else 1.0, alinha="CENTER")
    else:
        OP.texto("r2_rot", rotulo or (fmt or OP_fmt)(topo_m), tam, (x + lado_rot * (larg / 2 + 0.03), y - 0.02, topo_u + tam * 0.55), cor=cor_num,
                 forca=1.8 if cor_num == AMBAR else 1.0, alinha="LEFT" if lado_rot > 0 else "RIGHT")


def OP_fmt(m):
    if m < 100:
        return (f"{m:.1f}".replace(".", ",").replace(",0", "")) + " m"
    if m < 1000:
        return f"{m:.0f} m"
    km = m / 1000.0
    return (f"{km:.1f}".replace(".", ",").replace(",0", "") if km < 100 else f"{km:,.0f}".replace(",", ".")) + " km"


def rotulo_ref(x, topo_u, texto_, lado=1, tam=0.1, y=0.0, escuro=False, cor=AMBAR):
    """o tamanho da referência: traço âmbar fino no topo dela e o texto logo acima, começando no traço"""
    caixa(f"ref_traco_{texto_}", (0.12, 0.01, 0.008), O3.brilha(AMBAR, 1.3), (x + 0.06, y - 0.02, topo_u), cont=0.0)
    OP.texto(f"ref_t_{texto_}", texto_, tam, (x, y - 0.02, topo_u + tam * 0.75), cor=cor, forca=1.5 if cor == AMBAR else 1.0, alinha="LEFT")
