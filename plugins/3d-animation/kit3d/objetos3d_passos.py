"""Objetos 3D de "E se cada passo dobrasse a sua altura?" (plano de cena: personagem/passos/plano-de-cena-v1.md).
Mesmo acabamento do herói (tom chapado, faixa de sombra, borda de luz, contorno de tinta). Tudo em metros REAIS; quem escala o mundo é o
story_passos.no_mundo (k = 2^-n), então um prédio de 55 m é modelado com 55 m e o boneco continua com 1,8 de altura.
Convenção do kit: z para cima, a frente dos objetos olha para -y (a câmera), a rua corre ao longo de +y."""
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

BD = "#fff0d8"                                              # borda de luz de dia (quente e clara)
AMBAR = "#f2b441"                                           # a cor da régua e dos números
CREME = "#efe8d6"


def M(cor, sombra=None, borda=BD):
    return estilo(cor, sombra, borda)


# ---------------------------------------------------------------- céu, chão e estrelas
def mat_ceu(nome, stops):
    """degradê pela altura no mundo (emissão). stops = [(z, cor), ...]"""
    m = bpy.data.materials.new(nome); m.use_nodes = True
    nt = m.node_tree; N = nt.nodes; L = nt.links; N.clear()
    out = N.new("ShaderNodeOutputMaterial"); em = N.new("ShaderNodeEmission")
    geo = N.new("ShaderNodeNewGeometry"); sep = N.new("ShaderNodeSeparateXYZ"); mr = N.new("ShaderNodeMapRange"); mr.clamp = True
    mr.inputs[1].default_value = stops[0][0]; mr.inputs[2].default_value = stops[-1][0]
    ramp = N.new("ShaderNodeValToRGB"); els = ramp.color_ramp.elements
    while len(els) > 1:
        els.remove(els[-1])
    zs = [s[0] for s in stops]
    els[0].position = 0.0; els[0].color = (*srgb(stops[0][1]), 1)
    for z, c in stops[1:]:
        e = els.new((z - zs[0]) / (zs[-1] - zs[0])); e.color = (*srgb(c), 1)
    L.new(geo.outputs["Position"], sep.inputs[0]); L.new(sep.outputs["Z"], mr.inputs[0]); L.new(mr.outputs[0], ramp.inputs["Fac"])
    L.new(ramp.outputs["Color"], em.inputs[0]); L.new(em.outputs[0], out.inputs[0])
    return m


def domo(stops, raio=900.0):
    """céu em volta de tudo (esfera vista por dentro); a cor muda pela altura z"""
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=48, v_segments=24, radius=raio)
    me = bpy.data.meshes.new("domo"); bm.to_mesh(me); bm.free()
    me.materials.append(mat_ceu("domo_m", stops))
    o = bpy.data.objects.new("domo", me); bpy.context.scene.collection.objects.link(o)
    return o


def estrelas(n=260, raio=700.0, seed=2, tam=(0.35, 1.1)):
    rnd = random.Random(seed)
    m = O3.brilha("#ffffff", 1.6)
    for i in range(n):
        v = Vector((rnd.gauss(0, 1), rnd.gauss(0, 1), rnd.gauss(0, 1))).normalized() * raio
        r = rnd.uniform(*tam)
        bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=1, radius=r)
        me = bpy.data.meshes.new(f"est{i}"); bm.to_mesh(me); bm.free(); me.materials.append(m)
        o = bpy.data.objects.new(f"est{i}", me); bpy.context.scene.collection.objects.link(o); o.location = v


def chao(cor, meio, tam, z=-0.02, nome="chao_largo"):
    """plano enorme (tam em metros reais) que vai ao horizonte"""
    return cena.poly_mesh(nome, [(-tam, -tam, z), (tam, -tam, z), (tam, tam, z), (-tam, tam, z)], props.FM(cor))


# ---------------------------------------------------------------- prédios e torres
def torre(nome, cx, cy, w, d, h, cor="#8a93a0", andar=3.2, cont=0.02, fachadas=("f", "e", "d"), janela="#1d3340"):
    """prédio-caixa com fitas de janela (face da frente -y e as duas laterais). h em metros reais."""
    L = C3.Lote(nome)
    L.caixa("parede", (cx, cy, h / 2), (w, d, h))
    L.caixa("escuro", (cx, cy, h + 0.4), (w * 1.02, d * 1.02, 0.8))
    n = max(1, int((h - 2.0) / andar))
    ncol = max(2, int(w / 3.2)); ncold = max(2, int(d / 3.2))
    for i in range(n):
        z = 2.2 + i * andar + 0.9
        if "f" in fachadas:
            for c in range(ncol):
                x = cx - w / 2 + (c + 0.5) * w / ncol
                L.caixa("vidro", (x, cy - d / 2 - 0.03, z), (w / ncol * 0.62, 0.06, andar * 0.42))
        for lado, sx in (("e", -1), ("d", 1)):
            if lado in fachadas:
                for c in range(ncold):
                    y = cy - d / 2 + (c + 0.5) * d / ncold
                    L.caixa("vidro", (cx + sx * (w / 2 + 0.03), y, z), (0.06, d / ncold * 0.62, andar * 0.42))
    mats = {"parede": M(cor), "escuro": M(_mix(cor, "#000000", 0.45)), "vidro": M(janela, _mix(janela, "#000000", 0.4), "#7aa0b0")}
    return L.fecha(mats, contorno=cont)


def sobrado(nome, cx, cy, w=8.0, d=7.0, cor="#c9a888"):
    """casa de dois andares, 7 m de altura com o telhado"""
    L = C3.Lote(nome)
    L.caixa("parede", (cx, cy, 2.7), (w, d, 5.4))
    for sx in (-1, 1):
        L.caixa("vidro", (cx + sx * w * 0.25, cy - d / 2 - 0.03, 4.0), (1.3, 0.06, 1.3))
        L.caixa("escuro", (cx + sx * w * 0.25, cy - d / 2 - 0.02, 4.0), (1.5, 0.05, 1.5))
    L.caixa("porta", (cx, cy - d / 2 - 0.03, 1.1), (1.2, 0.06, 2.2))
    L.caixa("vidro", (cx - w * 0.3, cy - d / 2 - 0.03, 1.5), (1.3, 0.06, 1.3))
    L.caixa("telhado", (cx, cy, 6.2), (w + 0.6, d + 0.6, 0.9))
    L.caixa("telhado", (cx, cy, 6.85), (w * 0.6, d * 0.6, 0.5))
    mats = {"parede": M(cor), "vidro": M("#1d3340", "#142530", "#7aa0b0"), "escuro": M("#e8e0d0"), "porta": M("#6a4a3a"), "telhado": M("#9a4a38", "#6e3326")}
    return L.fecha(mats, contorno=0.03)


def burj(nome, cx, cy, H=828.0):
    """a torre mais alta do mundo, em degraus afinando (segmentos de 6 lados, claro e escuro alternados) com a agulha no topo"""
    cores = ("#aebccb", "#8d9db0")
    secoes = [(0, 150, 46, 38), (150, 290, 36, 30), (290, 430, 28, 22), (430, 560, 21, 16), (560, 660, 15, 9), (660, 740, 8, 3.2), (740, H, 2.4, 0.5)]
    out = []
    for i, (z0, z1, r0, r1) in enumerate(secoes):
        out.append(O3.cilindro(f"{nome}_s{i}", r0, z1 - z0, M(cores[i % 2], _mix(cores[i % 2], "#000000", 0.3)), None, (cx, cy, (z0 + z1) / 2), seg=6, r2=r1, contorno=0.4))
    return out


# ---------------------------------------------------------------- cidade de longe (maquete) e nuvens
def cidade_maquete(raio, passo=95.0, seed=4, clareira=None, altura_max=160.0, ox=0.0, oy=0.0, corredor=0.0, altura_min=8.0, larg=(34, 64), vazio=None, cor=("#8c93a0", "#a39c8c", "#7d8794", "#b2ab9a")):
    """quarteirões de caixas com altura sortida; clareira = (cx, cy, r) onde fica vazio (a base do Burj, a rua do boneco)"""
    rnd = random.Random(seed)
    L = C3.Lote("cid")
    n = int(raio / passo)
    for i in range(-n, n + 1):
        for j in range(-n, n + 1):
            cx, cy = i * passo + ox, j * passo + oy
            if clareira and any((cx - c[0]) ** 2 + (cy - c[1]) ** 2 < c[2] ** 2 for c in (clareira if isinstance(clareira[0], (tuple, list)) else [clareira])):
                continue
            if corredor and abs(cx) < corredor:
                continue
            if vazio and cx * vazio[0] > 0 and abs(cx) < vazio[1] + 40.0:       # o lado aberto da rua: nada de quarteirão entre a câmera lateral e o boneco
                continue
            d = math.hypot(cx - ox, cy - oy)
            hmax = altura_max * (1.0 - 0.7 * min(1.0, d / raio))
            h = max(altura_min, rnd.random() ** 2.2 * hmax + altura_min)
            L.caixa(f"p{rnd.randrange(len(cor))}", (cx + rnd.uniform(-6, 6), cy + rnd.uniform(-6, 6), h / 2), (rnd.uniform(*larg), rnd.uniform(*larg), h))
    mats = {f"p{k}": M(c) for k, c in enumerate(cor)}
    return L.fecha(mats, contorno=1.2)


def nuvens(z, raio, n=22, seed=3, tam=(500, 1100), cor="#f4f6f8", sombra="#b4c2d2"):
    """nuvens fofas (grupos de elipsoides achatados) a uma altura z (metros reais), espalhadas num raio"""
    rnd = random.Random(seed)
    m = M(cor, sombra, "#ffffff")
    for k in range(n):
        cx, cy = rnd.uniform(-raio, raio), rnd.uniform(-raio, raio)
        s = rnd.uniform(*tam)
        for b in range(rnd.randint(4, 7)):
            esfera(f"nuv{k}_{b}", s * rnd.uniform(0.35, 0.6), s * rnd.uniform(0.3, 0.5), s * rnd.uniform(0.18, 0.3), m, None,
                   (cx + rnd.uniform(-0.6, 0.6) * s, cy + rnd.uniform(-0.5, 0.5) * s, z + rnd.uniform(-0.1, 0.12) * s), contorno=s * 0.01, seg=18, an=10)


# ---------------------------------------------------------------- planetas
def mat_planeta(nome, base, manchas, escala=2.2, limiar=0.5, sombra=0.42, seed=1):
    """esfera de tom chapado com manchas (ruído em degraus) e faixa de sombra do lado oposto à luz"""
    m = bpy.data.materials.new(nome); m.use_nodes = True
    nt = m.node_tree; N = nt.nodes; L = nt.links; N.clear()
    out = N.new("ShaderNodeOutputMaterial"); em = N.new("ShaderNodeEmission")
    tc = N.new("ShaderNodeTexCoord"); no = N.new("ShaderNodeTexNoise"); no.inputs["Scale"].default_value = escala; no.inputs["Detail"].default_value = 4.0
    no.noise_dimensions = "3D"; no.inputs["Scale"].default_value = escala * (1.0 + 0.07 * seed)
    rp = N.new("ShaderNodeValToRGB"); rp.color_ramp.interpolation = "CONSTANT"
    e = rp.color_ramp.elements; e[0].position = 0.0; e[0].color = (*srgb(base), 1)
    e[1].position = limiar; e[1].color = (*srgb(manchas), 1)
    geo = N.new("ShaderNodeNewGeometry"); dot = N.new("ShaderNodeVectorMath"); dot.operation = "DOT_PRODUCT"; dot.inputs[1].default_value = tuple(H3.LUZ)
    mp = N.new("ShaderNodeMapRange"); mp.inputs[1].default_value = -1.0; mp.inputs[2].default_value = 1.0
    sh = N.new("ShaderNodeValToRGB"); sh.color_ramp.interpolation = "CONSTANT"; s = sh.color_ramp.elements
    s[0].position = 0.0; s[0].color = (sombra, sombra, sombra * 1.1, 1); s[1].position = 0.47; s[1].color = (1, 1, 1, 1)
    mx = N.new("ShaderNodeMix"); mx.data_type = "RGBA"; mx.blend_type = "MULTIPLY"; mx.inputs[0].default_value = 1.0
    L.new(tc.outputs["Object"], no.inputs["Vector"]); L.new(no.outputs["Fac"], rp.inputs[0])
    L.new(geo.outputs["Normal"], dot.inputs[0]); L.new(dot.outputs["Value"], mp.inputs[0]); L.new(mp.outputs["Result"], sh.inputs[0])
    L.new(rp.outputs["Color"], mx.inputs[6]); L.new(sh.outputs["Color"], mx.inputs[7]); L.new(mx.outputs[2], em.inputs[0]); L.new(em.outputs[0], out.inputs[0])
    return m


def terra(nome, r, loc, pai=None):
    """a Terra: oceano azul, continentes verdes e areia, um véu azul de atmosfera na borda"""
    m = mat_planeta(nome + "_m", "#2a67b0", "#5f9a4e", escala=2.4, limiar=0.52, seed=3)
    o = esfera(nome, r, r, r, m, pai, loc, contorno=r * 0.004, seg=72, an=40)
    esfera(nome + "_nuv", r * 1.012, r * 1.012, r * 1.012, mat_planeta(nome + "_nm", "#ffffff", "#ffffff", escala=3.6, limiar=0.62, seed=8), pai, loc, contorno=0.0, seg=60, an=32)
    nuv = bpy.data.objects[nome + "_nuv"]; nuv.data.materials.clear(); nuv.data.materials.append(_nuvem_mat(nome))
    esfera(nome + "_atm", r * 1.022, r * 1.022, r * 1.022, O3.vidro("#7fb8ff", 0.0, 0.95), pai, loc, contorno=0.0, seg=60, an=32)
    return o


def _nuvem_mat(nome):
    """nuvens da Terra: manchas brancas sobre transparente"""
    m = bpy.data.materials.new(nome + "_nuvm"); m.use_nodes = True
    if hasattr(m, "surface_render_method"):
        m.surface_render_method = "BLENDED"
    nt = m.node_tree; N = nt.nodes; L = nt.links; N.clear()
    out = N.new("ShaderNodeOutputMaterial"); em = N.new("ShaderNodeEmission"); tr = N.new("ShaderNodeBsdfTransparent"); mix = N.new("ShaderNodeMixShader")
    tc = N.new("ShaderNodeTexCoord"); no = N.new("ShaderNodeTexNoise"); no.inputs["Scale"].default_value = 3.4; no.inputs["Detail"].default_value = 3.0
    no.noise_dimensions = "3D"
    rp = N.new("ShaderNodeValToRGB"); rp.color_ramp.interpolation = "CONSTANT"; e = rp.color_ramp.elements
    e[0].position = 0.0; e[0].color = (0, 0, 0, 1); e[1].position = 0.6; e[1].color = (1, 1, 1, 1)
    geo = N.new("ShaderNodeNewGeometry"); dot = N.new("ShaderNodeVectorMath"); dot.operation = "DOT_PRODUCT"; dot.inputs[1].default_value = tuple(H3.LUZ)
    mp = N.new("ShaderNodeMapRange"); mp.inputs[1].default_value = -1.0; mp.inputs[2].default_value = 1.0
    sh = N.new("ShaderNodeValToRGB"); sh.color_ramp.interpolation = "CONSTANT"; s = sh.color_ramp.elements
    s[0].position = 0.0; s[0].color = (0.55, 0.62, 0.74, 1); s[1].position = 0.47; s[1].color = (1, 1, 1, 1)
    L.new(tc.outputs["Object"], no.inputs["Vector"]); L.new(no.outputs["Fac"], rp.inputs[0]); L.new(rp.outputs["Color"], mix.inputs[0])
    L.new(geo.outputs["Normal"], dot.inputs[0]); L.new(dot.outputs["Value"], mp.inputs[0]); L.new(mp.outputs["Result"], sh.inputs[0]); L.new(sh.outputs["Color"], em.inputs[0])
    L.new(tr.outputs[0], mix.inputs[1]); L.new(em.outputs[0], mix.inputs[2]); L.new(mix.outputs[0], out.inputs[0])
    return m


def lua(nome, r, loc, pai=None):
    m = mat_planeta(nome + "_m", "#c2c0b8", "#8f8d86", escala=3.0, limiar=0.55, sombra=0.4, seed=5)
    return esfera(nome, r, r, r, m, pai, loc, contorno=r * 0.004, seg=64, an=36)


# ---------------------------------------------------------------- régua (fita métrica 3D), textos e números
def mat_ambar(forca=1.5):
    return O3.brilha(AMBAR, forca)


def texto(nome, corpo, tam, loc, cor=AMBAR, forca=1.6, rot=(math.pi / 2, 0, 0), alinha="CENTER"):
    t = lib.text(nome, corpo, tam, O3.brilha(cor, forca), None, loc, lib.font())
    t.data.align_x = alinha
    t.rotation_euler = rot
    return t


def bonito(m):
    """número 'bonito' mais próximo (1, 2, 5 x 10^n) para o espaçamento dos riscos da régua"""
    e = 10 ** math.floor(math.log10(m)); f = m / e
    return e * (1 if f < 1.5 else 2 if f < 3.5 else 5 if f < 7.5 else 10)


def fita(x, altura_u, passo_u, z0=0.0, y=0.0, larg=0.1, rotulo=None, tam_rot=0.16, lado=-1, linha_ate=None, rot_dx=None):
    """régua vertical de verdade: placa creme com riscos a cada passo_u e o número em âmbar no topo.
    altura_u = o quanto ela sobe (u da cena); passo_u = espaçamento dos riscos; linha_ate = (x, z) para onde corre uma linha âmbar até a cabeça"""
    m = M(CREME, "#cdc4ae")
    O3.caixa("fita", (larg, 0.03, altura_u), m, None, (x, y, z0 + altura_u / 2), chanfro=0.0, contorno=0.004)
    n = int(altura_u / passo_u + 1e-6)
    mk = M("#2a2620", "#2a2620")
    for i in range(n + 1):
        z = z0 + i * passo_u
        comp = larg * (0.78 if i % 5 == 0 else 0.4)
        O3.caixa(f"risco{i}", (comp, 0.05, 0.006), mk, None, (x + lado * (larg / 2 - comp / 2) * -1, y - 0.02, z), chanfro=0.0, contorno=0.0)
    if rotulo:
        dx = rot_dx if rot_dx is not None else 0.0
        texto("rot_fita", rotulo, tam_rot, (x + dx, y - 0.05, z0 + altura_u + tam_rot * 0.85), forca=1.8)
    if linha_ate:
        xa, za = linha_ate
        O3.caixa("linha_ambar", (abs(xa - x), 0.012, 0.012), O3.brilha(AMBAR, 1.4), None, ((x + xa) / 2, y - 0.03, za), chanfro=0.0, contorno=0.0)
    return n


# ---------------------------------------------------------------- manômetro, tubo do coração, ondas
def manometro(nome, loc, R, valor, rotulo, sub=None, faixa=(0.0, 2.0), zona_vermelha=1.5):
    """mostrador redondo de verdade: aro, fundo claro, 21 riscos num arco de 270 graus, ponteiro e o número em âmbar embaixo"""
    x0, y0, z0 = loc
    O3.cilindro(nome + "_corpo", R, R * 0.28, M("#3a3f46", "#23272c"), None, (x0, y0 + R * 0.1, z0), seg=64, eixo="Y", contorno=0.006)
    O3.cilindro(nome + "_fundo", R * 0.92, R * 0.05, M("#f2eee2", "#d5cfbd"), None, (x0, y0 - R * 0.06, z0), seg=64, eixo="Y", contorno=0.0)
    O3.anel(nome + "_aro", R * 0.97, R * 0.07, M("#9aa3ad", "#6e757d"), None, (x0, y0 - R * 0.05, z0), eixo="Y", seg=64, contorno=0.005)
    lo, hi = faixa
    for i in range(21):
        u = i / 20; th = math.radians(-135 + 270 * u)
        rr = R * 0.8; maior = i % 5 == 0
        v = lo + (hi - lo) * u
        cor = "#b03030" if v >= zona_vermelha else "#23211d"
        b = O3.caixa(f"{nome}_r{i}", (R * 0.035, R * 0.02, R * (0.15 if maior else 0.08)), M(cor, cor), None, (x0 + rr * math.sin(th), y0 - R * 0.1, z0 + rr * math.cos(th)), chanfro=0.0, contorno=0.0)
        b.rotation_euler = (0, th, 0)
    u = (valor - lo) / (hi - lo); th = math.radians(-135 + 270 * max(0.0, min(1.0, u)))
    pv = empty(nome + "_pivo", None, (x0, y0 - R * 0.14, z0)); pv.rotation_euler = (0, th, 0)
    O3.caixa(nome + "_agulha", (R * 0.04, R * 0.02, R * 0.78), M("#d03a2c", "#8a2018", "#ff9a8a"), pv, (0, 0, R * 0.3), chanfro=0.0, contorno=0.003)
    O3.cilindro(nome + "_eixo", R * 0.07, R * 0.04, M("#2a2d32"), None, (x0, y0 - R * 0.17, z0), seg=24, eixo="Y", contorno=0.003)
    texto(nome + "_num", rotulo, R * 0.27, (x0, y0 - R * 0.13, z0 - R * 0.52), forca=0.0, cor="#23211d")
    if sub:
        texto(nome + "_sub", sub, R * 0.24, (x0, y0 - R * 0.13, z0 - R * 1.22), cor=AMBAR)
    return pv


def arcos_som(centro, n=3, r0=0.12, passo_r=0.08, abertura=55.0, r_tubo=0.006, forca=1.8, cor="#ffffff"):
    """ondas de som saindo para a câmera: arcos (((  em volta da boca, no plano do quadro"""
    for i in range(n):
        O3.anel(f"arco{i}", r0 + i * passo_r, r_tubo, O3.brilha(cor, max(0.5, forca - 0.35 * i)), None, centro, eixo="Y", seg=64, a0=-abertura, a1=abertura, contorno=0.0)


def aneis_som(base, n=5, r0=0.3, passo_r=0.12, dz=-0.25, r_tubo=0.006, forca=1.6, cor="#ffffff", eixo="Z"):
    """ondas de som: anéis de verdade em volta do boneco, cada vez maiores e mais abaixo"""
    for i in range(n):
        O3.anel(f"som{i}", r0 + i * passo_r, r_tubo * (1.0 + 0.1 * i), O3.brilha(cor, max(0.3, forca - 0.25 * i)), None, (base[0], base[1], base[2] + dz * i), eixo=eixo, seg=64, contorno=0.0)


def poeira_pouso(x, y, r=0.7, cor="#d8cfb8", alfa=0.55):
    """nuvem de poeira do pé que pousa: elipses translúcidas no chão e bolinhas que sobem"""
    m = cena.amat(f"poeira_{cor}", cor, 1.0, alfa, ("radial", 1.2))
    cena.ground_disc("poeira_chao", r, r * 0.8, m, (x, y, 0.012), n=48)
    rnd = random.Random(2)
    for i in range(14):
        a = rnd.uniform(0, 6.28); d = rnd.uniform(0.12, r)
        cena.disc(f"poeira_{i}", rnd.uniform(0.05, 0.14), m, (x + d * math.cos(a), y + d * math.sin(a) * 0.8 - 0.05, rnd.uniform(0.04, 0.3)))


# ---------------------------------------------------------------- macro: fio de cabelo, palito, lata
def fio_cabelo(nome, loc, diam, comp, cor="#2a1c16", eixo="X"):
    """fio de cabelo (cilindro comprido) ao longo do eixo"""
    return O3.cilindro(nome, diam / 2, comp, M(cor, "#120c09", "#6a4a3a"), None, loc, seg=20, eixo=eixo, contorno=diam * 0.05)


def palito(nome, loc, diam, comp, eixo="X"):
    """palito de dente: madeira clara, com as duas pontas afinando"""
    m = M("#e0c288", "#b89a5c", "#fff0c8")
    x, y, z = loc
    O3.cilindro(nome, diam / 2, comp * 0.84, m, None, loc, seg=18, eixo=eixo, contorno=diam * 0.05)
    for s in (-1, 1):
        d = s * comp * 0.46
        pos = (x + d, y, z) if eixo == "X" else (x, y, z + d) if eixo == "Z" else (x, y + d, z)
        c = O3.cilindro(f"{nome}_p{s}", diam / 2, comp * 0.08, m, None, pos, seg=18, eixo=eixo, r2=diam * 0.12, contorno=diam * 0.04)
        if s < 0:
            c.rotation_euler = (math.pi, 0, 0) if eixo == "Z" else (0, math.pi, 0) if eixo == "X" else (0, 0, math.pi)


def lata(nome, loc, r, h, eixo="X"):
    """lata de refrigerante deitada: corpo vermelho, faixa branca, tampa e fundo de alumínio"""
    x, y, z = loc
    O3.cilindro(nome + "_c", r, h * 0.86, M("#c4302b", "#8a1f1c", "#ffb0a0"), None, loc, seg=48, eixo=eixo, contorno=r * 0.03)
    O3.cilindro(nome + "_f", r * 1.003, h * 0.22, M("#f4f0e6", "#cfc8b4"), None, loc, seg=48, eixo=eixo, contorno=0.0)
    for s in (-1, 1):
        d = h * 0.465 * s
        pos = (x + d, y, z) if eixo == "X" else (x, y, z + d) if eixo == "Z" else (x, y + d, z)
        O3.cilindro(f"{nome}_t{s}", r * 0.9, h * 0.07, M("#c4c8cc", "#8e9498", "#ffffff"), None, pos, seg=48, eixo=eixo, contorno=r * 0.02)


def coracao_tubo(altura_cabeca, z_coracao, x=0.0, y=-0.2, r=0.022, n_bolas=9):
    """encanamento do coração à cabeça, na frente do corpo: tubo vermelho-escuro com bolas de luz subindo"""
    pts = [(x, y, z_coracao), (x + 0.05, y, z_coracao + 0.06), (x + 0.08, y + 0.03, z_coracao + 0.17), (x + 0.1, y + 0.1, altura_cabeca - 0.02)]
    tubo("encanamento", pts, [r] * len(pts), M("#b02a30", "#6e1418", "#ff9a8a"), None, seg=24, tampa=6, contorno=0.004)
    mc = M("#c0282e", "#7a1418", "#ff9a8a")
    for sx in (-1, 1):                                   # coração: dois lóbulos e a ponta para baixo
        esfera(f"coracao_l{sx}", 0.04, 0.04, 0.042, mc, None, (x + sx * 0.03, y, z_coracao + 0.015), contorno=0.004, seg=24, an=14)
    O3.cilindro("coracao_ponta", 0.004, 0.07, mc, None, (x, y, z_coracao - 0.025), seg=20, r2=0.068, contorno=0.004)
    for i in range(n_bolas):
        u = (i + 0.5) / n_bolas
        z = z_coracao + (altura_cabeca - z_coracao) * u
        esfera(f"fluxo{i}", r * 0.7, r * 0.7, r * 0.7, O3.brilha("#ff6a5a", 1.8), None, (x + 0.1 * u, y + 0.1 * u - 0.01, z), contorno=0.0, seg=12, an=8)
