"""Objetos de "O abrigo" modelados em 3D de verdade (pedido de 24/10/2026: "tem muitos objetos meio planos; a mão parece um papel;
o vidro da porta precisa ser vidro de verdade e dá para ver do outro lado; modelar mais os objetos").
Mesmo acabamento do herói 3D (heroi3d.estilo): tom chapado, uma faixa de sombra do lado oposto à luz, borda de luz âmbar e contorno de tinta
(casco invertido). Vidro e plástico têm material próprio (transparente com brilho na borda).
Convenção: z para cima, a frente dos objetos olha para -y (como a câmera padrão do kit)."""
import math, random
import bpy, bmesh
from mathutils import Vector, Matrix
from lib import empty, srgb, key
import heroi3d as H3
from heroi3d import esfera, tubo, _objeto, plano

BORDA = "#d9c08a"
PELE = "#0d1020"
MANGA = "#6e2422"                     # a blusa de frio vermelha escura de quem conta (o contraste que faltava)
MANGA_S = "#4a1616"
_M = {}


def M(cor, sombra=None, borda=BORDA):
    return H3.estilo(cor, sombra, borda)


def vidro(cor="#d8ece8", alfa=0.18, brilho=0.55, nome=None):
    """vidro: quase transparente no meio, mais opaco e claro na borda (fresnel), com uma leve cor"""
    k = ("vidro", cor, alfa, brilho)
    if k in _M:
        return _M[k]
    m = bpy.data.materials.new(nome or f"vidro_{cor}_{alfa}"); m.use_nodes = True
    if hasattr(m, "surface_render_method"):
        m.surface_render_method = "BLENDED"
    nt = m.node_tree; N = nt.nodes; L = nt.links; N.clear()
    out = N.new("ShaderNodeOutputMaterial"); em = N.new("ShaderNodeEmission"); em.inputs[0].default_value = (*srgb(cor), 1)
    tr = N.new("ShaderNodeBsdfTransparent"); mix = N.new("ShaderNodeMixShader")
    lw = N.new("ShaderNodeLayerWeight"); lw.inputs["Blend"].default_value = 0.35
    mul = N.new("ShaderNodeMath"); mul.operation = "MULTIPLY_ADD"; mul.inputs[1].default_value = brilho; mul.inputs[2].default_value = alfa
    cl = N.new("ShaderNodeClamp")
    L.new(lw.outputs["Facing"], mul.inputs[0]); L.new(mul.outputs[0], cl.inputs[0]); L.new(cl.outputs[0], mix.inputs[0])
    L.new(tr.outputs[0], mix.inputs[1]); L.new(em.outputs[0], mix.inputs[2]); L.new(mix.outputs[0], out.inputs[0])
    _M[k] = m
    return m


def brilha(cor, forca=2.2):
    """emissão forte (lâmpada acesa, luz da sirene)"""
    k = ("brilha", cor, forca)
    if k in _M:
        return _M[k]
    m = bpy.data.materials.new(f"brilha_{cor}"); m.use_nodes = True
    nt = m.node_tree; nt.nodes.clear()
    em = nt.nodes.new("ShaderNodeEmission"); em.inputs[0].default_value = (*srgb(cor), 1); em.inputs[1].default_value = forca
    out = nt.nodes.new("ShaderNodeOutputMaterial"); nt.links.new(em.outputs[0], out.inputs[0])
    _M[k] = m
    return m


def halo_cam(nome, loc, r, cor, alfa, pai=None):
    """brilho redondo que sempre olha para a câmera ativa (ligar com olha_camera depois de criar a câmera)"""
    import cena
    o = cena.disc(nome, r, cena.amat(nome + "_m", cor, 1.0, alfa, ("radial", 1.4)), loc)
    if pai:
        o.parent = pai; o.location = loc
    o["halo_cam"] = True
    return o


def olha_camera(cam):
    """todos os halos (halo_cam) giram para encarar a câmera"""
    for o in bpy.data.objects:
        if o.get("halo_cam"):
            c = o.constraints.new("DAMPED_TRACK"); c.target = cam; c.track_axis = "TRACK_NEGATIVE_Y"


# ---------------------------------------------------------------- primitivas
def caixa(nome, tam, mat, pai=None, loc=(0, 0, 0), chanfro=0.006, contorno=0.004, rot=None):
    """caixa com as quinas arredondadas (chanfro), tam = (x, y, z), origem no centro"""
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=tam, verts=bm.verts)
    if chanfro:
        bmesh.ops.bevel(bm, geom=list(bm.edges) + list(bm.verts), offset=min(chanfro, min(tam) * 0.45), segments=2, affect="EDGES", profile=0.5)
    o = _objeto(nome, bm, mat, pai, loc, contorno)
    for p in o.data.polygons:
        p.use_smooth = False
    if rot:
        o.rotation_euler = tuple(math.radians(a) for a in rot)
    return o


def cilindro(nome, r, h, mat, pai=None, loc=(0, 0, 0), seg=32, eixo="Z", r2=None, contorno=0.004, tampa=True):
    """cilindro (ou cone, com r2) centrado em loc, ao longo do eixo"""
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=tampa, cap_tris=False, segments=seg, radius1=r, radius2=r if r2 is None else r2, depth=h)
    if eixo == "X":
        bmesh.ops.rotate(bm, verts=bm.verts, cent=(0, 0, 0), matrix=Matrix.Rotation(math.radians(90), 3, "Y"))
    elif eixo == "Y":
        bmesh.ops.rotate(bm, verts=bm.verts, cent=(0, 0, 0), matrix=Matrix.Rotation(math.radians(90), 3, "X"))
    o = _objeto(nome, bm, mat, pai, loc, contorno)
    return o


def anel(nome, R, r, mat, pai=None, loc=(0, 0, 0), eixo="Y", seg=48, a0=0.0, a1=360.0, contorno=0.004):
    """toro (ou arco) de raio R e espessura r, no plano perpendicular ao eixo"""
    pts = []
    n = max(8, int(seg * (a1 - a0) / 360.0))
    for k in range(n + 1):
        a = math.radians(a0 + (a1 - a0) * k / n)
        c, s = R * math.cos(a), R * math.sin(a)
        pts.append((c, 0, s) if eixo == "Y" else (c, s, 0) if eixo == "Z" else (0, c, s))
    return tubo(nome, pts, [r] * len(pts), mat, pai, loc, seg=16, tampa=4, contorno=contorno)


def torno(nome, perfil, mat, pai=None, loc=(0, 0, 0), seg=48, contorno=0.004):
    """sólido de revolução em torno de z: perfil = [(raio, z), ...] de baixo para cima"""
    bm = bmesh.new(); aneis = []
    for r, z in perfil:
        aneis.append([bm.verts.new((max(r, 1e-4) * math.cos(2 * math.pi * k / seg), max(r, 1e-4) * math.sin(2 * math.pi * k / seg), z)) for k in range(seg)])
    for a, b in zip(aneis, aneis[1:]):
        for k in range(seg):
            k2 = (k + 1) % seg
            bm.faces.new((a[k], a[k2], b[k2], b[k]))
    if perfil[0][0] > 1e-3:
        bm.faces.new(aneis[0][::-1])
    if perfil[-1][0] > 1e-3:
        bm.faces.new(aneis[-1])
    return _objeto(nome, bm, mat, pai, loc, contorno)


# ---------------------------------------------------------------- as mãos de quem conta (POV)
DEDOS = [(-0.028, 0.096, (0.033, 0.022, 0.018), 0.0092), (-0.0095, 0.104, (0.037, 0.025, 0.02), 0.0096),
         (0.0095, 0.102, (0.035, 0.024, 0.019), 0.0094), (0.027, 0.093, (0.028, 0.019, 0.016), 0.0084)]
POSES = {"aberta": dict(dedos=(8, 10, 6), polegar=(-10, 10), abre=6),
         "fechada": dict(dedos=(88, 100, 70), polegar=(35, 40), abre=0),
         "segura": dict(dedos=(62, 70, 45), polegar=(25, 25), abre=2),
         "pinca": dict(dedos=(40, 60, 40), polegar=(30, 30), abre=2),
         "relaxada": dict(dedos=(25, 30, 20), polegar=(5, 15), abre=4)}


class Mao3D:
    """antebraço (blusa vermelha escura com punho canelado) e mão preta com dedos articulados.
    Local: o antebraço vai do cotovelo (y negativo, perto do olho) até o pulso na origem; os dedos apontam para +y; o dorso olha para +z.
    lado = "esq" ou "dir" (o polegar fica para dentro). pose() troca a mão (aberta, fechada, segura, pinca, relaxada); gira() mexe o pulso."""

    def __init__(self, nome, lado="dir", pai=None, loc=(0, 0, 0), escala=1.0, manga=MANGA, relogio=False, manga_comp=0.42):
        """manga_comp = comprimento da manga atrás do pulso (m). 0,42 é o antebraço curto das provas; 1,1 deixa a manga sair do quadro (POV:
        pedido de 25/10/2026, "o braço parece solto": a ponta redonda do braço não pode aparecer no meio da imagem)"""
        self.nome = nome; self.sg = 1 if lado == "dir" else -1
        sg = self.sg
        self.raiz = empty(nome, pai, loc); self.raiz.scale = (escala,) * 3
        mp, mm, mms = M(PELE, borda="#e8cfa8"), M(manga), M(MANGA_S)
        # antebraço: manga de lã que afina para o punho, com dobras e o punho canelado
        L = manga_comp; k = min(L / 0.42, 1.6)
        if L <= 0.43:
            tubo(nome + "_manga", [(0, -0.42, -0.07), (0, -0.22, -0.035), (0, -0.05, -0.005)], [0.058, 0.05, 0.045], mm, self.raiz, seg=28, tampa_fim=False)
        else:                                                              # manga comprida e mais fina: continua até fora do quadro, sem a ponta redonda
            tubo(nome + "_manga", [(0, -L, -0.07 * k), (0, -L * 0.55, -0.04 * k), (0, -0.22, -0.03), (0, -0.05, -0.005)], [0.05, 0.05, 0.048, 0.045], mm, self.raiz, seg=28, tampa_ini=False, tampa_fim=False)
        for k, y in enumerate((-0.33, -0.25, -0.17)):
            tubo(f"{nome}_dobra{k}", [(-0.03 * sg, y, 0.03 - 0.1 * (y + 0.05) * 0.2), (0.02 * sg, y + 0.03, 0.035)], [0.0045, 0.0045], mms, self.raiz, seg=8, tampa=3, contorno=0.0)
        cilindro(nome + "_punho_c", 0.047, 0.05, M("#5a1c1a"), self.raiz, (0, -0.04, -0.004), seg=28, eixo="Y")
        for k in range(10):
            a = 2 * math.pi * k / 10
            tubo(f"{nome}_cana{k}", [(0.0475 * math.cos(a), -0.064, -0.004 + 0.0475 * math.sin(a)), (0.0475 * math.cos(a), -0.016, -0.004 + 0.0475 * math.sin(a))], [0.003, 0.003], mms, self.raiz, seg=6, tampa=2, contorno=0.0)
        self.pulso = empty(nome + "_pulso", self.raiz, (0, 0, 0))
        esfera(nome + "_pulso_m", 0.036, 0.03, 0.022, mp, self.pulso, (0, 0.0, 0.0), contorno=0.0035, seg=28, an=16)
        # palma: um bloco arredondado, mais largo nos nós dos dedos
        esfera(nome + "_palma", 0.047, 0.055, 0.02, mp, self.pulso, (0, 0.05, 0.002), contorno=0.0035, seg=36, an=20)
        for k, (x, y, _, r) in enumerate(DEDOS):
            esfera(f"{nome}_no{k}", r * 1.12, r * 1.05, r * 1.0, mp, self.pulso, (x * sg, y - 0.006, 0.006), contorno=0.003, seg=16, an=10)
        if relogio:
            cilindro(nome + "_rel_pulseira", 0.04, 0.016, M("#2a2a26"), self.pulso, (0, -0.012, 0.0), seg=24, eixo="Y", contorno=0.003)
            cilindro(nome + "_rel_caixa", 0.017, 0.008, M("#aab6c8"), self.pulso, (0, -0.012, 0.027), seg=24, eixo="Z", contorno=0.003)
            cilindro(nome + "_rel_vidro", 0.013, 0.002, plano("#d8d0bb"), self.pulso, (0, -0.012, 0.032), seg=24, eixo="Z", contorno=0.0)
        # dedos: três falanges em cadeia (gira em x para dobrar)
        self.falanges = []
        for k, (x, y, Ls, r) in enumerate(DEDOS):
            pai_ = empty(f"{nome}_d{k}_0", self.pulso, (x * sg, y, 0.006)); cadeia = [pai_]
            for j, Lj in enumerate(Ls):
                rr = r * (1.0 - 0.1 * j)
                tubo(f"{nome}_d{k}_{j}_t", [(0, 0, 0), (0, Lj, 0)], [rr, rr * 0.95], mp, pai_, seg=14, tampa=5, contorno=0.003)
                if j < 2:
                    pai_ = empty(f"{nome}_d{k}_{j + 1}", pai_, (0, Lj, 0)); cadeia.append(pai_)
            self.falanges.append(cadeia)
        # polegar: sai do lado de dentro, para a frente e para cima
        p0 = empty(f"{nome}_pol0", self.pulso, (-0.04 * sg, 0.028, -0.004)); p0.rotation_euler = (0, 0, math.radians(38 * sg))
        tubo(f"{nome}_pol0_t", [(0, 0, 0), (0, 0.036, 0)], [0.0115, 0.0105], mp, p0, seg=14, tampa=5, contorno=0.003)
        p1 = empty(f"{nome}_pol1", p0, (0, 0.036, 0))
        tubo(f"{nome}_pol1_t", [(0, 0, 0), (0, 0.028, 0)], [0.0102, 0.0095], mp, p1, seg=14, tampa=5, contorno=0.003)
        self.polegar = [p0, p1]
        self.pose("relaxada")

    def pose(self, nome="aberta", f=None, **kw):
        P = dict(POSES[nome]); P.update(kw)
        for k, cadeia in enumerate(self.falanges):
            for j, o in enumerate(cadeia):
                o.rotation_euler = (math.radians(-P["dedos"][j] * (1.0 + 0.06 * (k - 1.5) * (j == 0))), 0, math.radians(P["abre"] * (k - 1.5) * 0.6 * self.sg) if j == 0 else 0)
                if f is not None:
                    key(o, "rotation_euler", f, "BEZIER")
        p0, p1 = self.polegar
        p0.rotation_euler = (math.radians(-P["polegar"][0] * 0.6), math.radians(-P["polegar"][0] * self.sg), math.radians(38 * self.sg))
        p1.rotation_euler = (math.radians(-P["polegar"][1]), 0, 0)
        if f is not None:
            key(p0, "rotation_euler", f, "BEZIER"); key(p1, "rotation_euler", f, "BEZIER")
        return self

    def gira(self, dobra=0.0, torce=0.0, f=None):
        self.pulso.rotation_euler = (math.radians(dobra), math.radians(torce), 0)
        if f is not None:
            key(self.pulso, "rotation_euler", f, "BEZIER")


def maos_pov3d(cam, nome="maos", d=0.5, escala=1.0, relogio=False, manga_comp=1.1):
    """as duas mãos 3D coladas na câmera (POV): saem de baixo do quadro, os antebraços apontando para a frente.
    Devolve (raiz, mao_esq, mao_dir); cada mão anda pela raiz (location em metros, no espaço da câmera girado: x direita, y frente, z cima)"""
    r = empty(nome + "_inv", cam, (0, 0, 0)); r.rotation_euler = (math.radians(-90), 0, 0)
    me = Mao3D(nome + "_esq", "esq", r, (-0.13 * escala, d, -0.21 * escala), escala, relogio=False, manga_comp=manga_comp)
    md = Mao3D(nome + "_dir", "dir", r, (0.13 * escala, d, -0.21 * escala), escala, relogio=relogio, manga_comp=manga_comp)
    for m in (me, md):
        m.raiz.rotation_euler = (math.radians(14), 0, math.radians(-8 * m.sg))
    return r, me, md


# ---------------------------------------------------------------- a porta do abrigo com vidro de verdade
def _placa_com_furo(nome, w, h, t, cx, cz, r, mat, pai, loc=(0, 0, 0), n=64, contorno=0.004):
    """placa w x h x t (base em z = 0, centrada em x) com um furo redondo de raio r em (cx, cz): frente, verso, laterais e a parede do furo"""
    cantos = [math.atan2(zc - cz, xc - cx) for xc, zc in ((w / 2, 0), (w / 2, h), (-w / 2, h), (-w / 2, 0))]
    angs = sorted(set([2 * math.pi * k / n - math.pi for k in range(n)] + cantos))
    def borda(a):
        dx, dz = math.cos(a), math.sin(a)
        ts = []
        if abs(dx) > 1e-9:
            ts += [(w / 2 - cx) / dx, (-w / 2 - cx) / dx]
        if abs(dz) > 1e-9:
            ts += [(h - cz) / dz, (0 - cz) / dz]
        t_ = min(t for t in ts if t > 0 and -w / 2 - 1e-6 <= cx + dx * t <= w / 2 + 1e-6 and -1e-6 <= cz + dz * t <= h + 1e-6)
        return cx + dx * t_, cz + dz * t_
    bm = bmesh.new()
    lados = {}
    for y in (-t / 2, t / 2):
        fora = [bm.verts.new((*(lambda p: (p[0], y, p[1]))(borda(a)),)) for a in angs]
        dentro = [bm.verts.new((cx + r * math.cos(a), y, cz + r * math.sin(a))) for a in angs]
        lados[y] = (fora, dentro)
    m = len(angs)
    for y, (fora, dentro) in lados.items():
        for k in range(m):
            k2 = (k + 1) % m
            f = (fora[k], fora[k2], dentro[k2], dentro[k])
            bm.faces.new(f if y > 0 else f[::-1])
    (f0, d0), (f1, d1) = lados[-t / 2], lados[t / 2]
    for k in range(m):
        k2 = (k + 1) % m
        bm.faces.new((f0[k], f0[k2], f1[k2], f1[k]))
        bm.faces.new((d0[k2], d0[k], d1[k], d1[k2]))
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-6)
    o = _objeto(nome, bm, mat, pai, loc, contorno)
    for p in o.data.polygons:
        p.use_smooth = False
    return o


def porta3d(nome, loc=(0, 0, 0), s=1.0, aberta=0.0, pai=None, lado="dentro", placa=False):
    """A MESMA porta de cofre em todas as cenas (dentro e fora do abrigo): batente de aço, folha verde-musgo grossa (8 cm) com a janelinha de vidro
    de verdade (dá para ver o outro lado), três trincos, três dobradiças e rebites.
    A roda de giro de bronze fica do lado de DENTRO (é de dentro que se tranca); do lado de fora a folha tem o aro da janelinha, rebites e um puxador.
    lado = "dentro": a câmera está dentro do abrigo (a roda olha para -y); "fora": a câmera está na rua (a porta gira 180°, a roda fica para dentro).
    placa: a placa ABRIGO fica no pórtico de fora (cidade3d.entrada_bunker), não na porta.
    '<nome>_folha' corre em x (aberta = fração da largura; vista de fora, corre para o outro lado); '<nome>_roda' gira em y."""
    import lib
    r = empty(nome, pai, loc); r.scale = (s,) * 3
    if lado == "fora":
        r.rotation_euler.z = math.pi
    aco, aco_e, musgo, musgo_e, bronze, bronze_c = M("#3a4650"), M("#2a333b"), M("#5d7a64", "#455e4c"), M("#4d6754"), M("#b88a52", "#8a6234"), M("#e0b378")
    W, Hh, T = 1.04, 2.17, 0.08
    # batente (moldura grossa)
    for k, (x, z, sx, sz) in enumerate(((-0.58, 1.15, 0.12, 2.3), (0.58, 1.15, 0.12, 2.3), (0.0, 2.27, 1.28, 0.1))):
        caixa(f"{nome}_bat{k}", (sx, 0.24, sz), aco, r, (x, 0.02, z), chanfro=0.012)
    f = empty(nome + "_folha", r, (aberta * 1.1, 0, 0.05))
    _placa_com_furo(nome + "_placa", W, Hh, T, 0.0, 1.75, 0.15, musgo, f, (0, -0.03, 0))
    for k, (z0, z1) in enumerate(((0.12, 0.9), (1.36, 1.55))):          # painéis em relevo
        caixa(f"{nome}_painel{k}", (0.82, 0.012, z1 - z0), musgo_e, f, (0, -0.076, (z0 + z1) / 2), chanfro=0.004, contorno=0.003)
    cilindro(nome + "_vidro", 0.15, 0.012, vidro("#e8f2ee", 0.06, 0.45), f, (0, -0.03, 1.75), seg=48, eixo="Y", contorno=0.0)
    anel(nome + "_aro", 0.158, 0.022, bronze, f, (0, -0.08, 1.75), eixo="Y", seg=48)
    for k in range(8):
        a = 2 * math.pi * k / 8
        esfera(f"{nome}_paraf{k}", 0.009, 0.009, 0.009, bronze_c, f, (0.19 * math.cos(a), -0.085, 1.75 + 0.19 * math.sin(a)), contorno=0.002, seg=12, an=8)
    for k, (x, z) in enumerate([(sx, sz) for sx in (-0.46, 0.46) for sz in (0.12, 0.55, 1.0, 1.4, 2.06)]):
        esfera(f"{nome}_rebite{k}", 0.012, 0.008, 0.012, M("#9bbd9f"), f, (x, -0.075, z), contorno=0.002, seg=12, an=8)
    for k, z in enumerate((0.35, 1.1, 1.95)):
        caixa(f"{nome}_trinco{k}", (0.22, 0.04, 0.07), M("#aab4bb", "#7e8a92"), f, (0.5, -0.09, z), chanfro=0.01)
        cilindro(f"{nome}_trinco_p{k}", 0.012, 0.12, M("#aab4bb", "#7e8a92"), f, (0.6, -0.09, z), seg=16, eixo="X", contorno=0.003)
        caixa(f"{nome}_dobr{k}", (0.07, 0.07, 0.2), aco_e, f, (-0.55, -0.04, z), chanfro=0.01)
        cilindro(f"{nome}_dobr_p{k}", 0.022, 0.24, aco, f, (-0.585, -0.06, z), seg=20, eixo="Z", contorno=0.003)
    ro = empty(nome + "_roda", f, (0, -0.12, 1.1))
    cilindro(nome + "_eixo", 0.03, 0.08, bronze, f, (0, -0.08, 1.1), seg=20, eixo="Y")
    anel(nome + "_roda_aro", 0.29, 0.024, bronze, ro, (0, 0, 0), eixo="Y", seg=56)
    for k in range(6):
        a = math.radians(60 * k + 15)
        tubo(f"{nome}_raio{k}", [(0, 0, 0), (0.29 * math.cos(a), 0, 0.29 * math.sin(a))], [0.016, 0.014], bronze, ro, seg=12, tampa=3)
        esfera(f"{nome}_pino{k}", 0.026, 0.026, 0.026, bronze_c, ro, (0.32 * math.cos(a), 0, 0.32 * math.sin(a)), contorno=0.003, seg=16, an=10)
    esfera(nome + "_cubo", 0.07, 0.045, 0.07, bronze, ro, (0, -0.01, 0), contorno=0.004, seg=24, an=14)
    # o lado de fora da folha (+y): aro da janelinha, puxador e rebites (sem roda)
    anel(nome + "_aro_fora", 0.158, 0.02, bronze, f, (0, 0.015, 1.75), eixo="Y", seg=48)
    tubo(nome + "_puxador", [(0.38, 0.015, 0.95), (0.38, 0.08, 0.98), (0.38, 0.08, 1.22), (0.38, 0.015, 1.25)], [0.018] * 4, M("#aab4bb", "#7e8a92"), f, seg=12, tampa=3)
    for k, (x, z) in enumerate([(sx, sz) for sx in (-0.46, 0.46) for sz in (0.12, 0.55, 1.0, 1.4, 2.06)]):
        esfera(f"{nome}_rebite_f{k}", 0.012, 0.008, 0.012, M("#9bbd9f"), f, (x, 0.015, z), contorno=0.002, seg=12, an=8)
    if placa:
        caixa(nome + "_placa_abrigo", (0.62, 0.03, 0.16), bronze, r, (0, -0.11, 2.45), chanfro=0.01)
        t = lib.text(nome + "_placa_t", "ABRIGO", 0.1, plano("#2a1c0e"), r, (0.0, -0.128, 2.43), lib.font()); t.rotation_euler = (math.pi / 2, 0, 0)
    return r


# ---------------------------------------------------------------- bicicleta, sirene, galão, latas, estante, lâmpada, gaiola, prato, móveis
def bicicleta3d(nome, loc=(0, 0, 0), s=1.0, cor="#8e3a30", pai=None, poeira=0.0, boneca=True):
    """bicicleta de cesta em 3D (1,6 m): rodas com raios, quadro de tubo, guidão com punhos, campainha prateada, cesta de vime com a boneca.
    Ao longo de x, rodas no plano xz. poeira (0 a 1) mistura tudo com cinza."""
    from props import _mix
    pc = lambda c: _mix(c, "#9a968a", poeira)
    r = empty(nome, pai, loc); r.scale = (s,) * 3
    R = 0.33
    for k, x in enumerate((-0.5, 0.5)):
        anel(f"{nome}_pneu{k}", R, 0.022, M(pc("#1c1c22")), r, (x, 0, R), eixo="Y", seg=64)
        anel(f"{nome}_aro{k}", R - 0.027, 0.007, M(pc("#c8ccd6")), r, (x, 0, R), eixo="Y", seg=64, contorno=0.002)
        for a in range(0, 360, 20):
            ar = math.radians(a)
            tubo(f"{nome}_raio{k}_{a}", [(x, 0, R), (x + (R - 0.03) * math.cos(ar), 0.0, R + (R - 0.03) * math.sin(ar))], [0.0018, 0.0018], M(pc("#aab0ba")), r, seg=5, tampa=1, contorno=0.0)
        cilindro(f"{nome}_cubo{k}", 0.022, 0.07, M(pc("#c8ccd6")), r, (x, 0, R), seg=16, eixo="Y", contorno=0.002)
    A, B_, C, D, F_ = (-0.5, 0, R), (-0.08, 0, 0.32), (-0.22, 0, 0.8), (0.36, 0, 0.76), (0.5, 0, R)
    mq = M(pc(cor))
    for k, (a, b) in enumerate(((A, B_), (B_, C), (A, C), (C, D), (B_, (0.34, 0, 0.7)))):
        tubo(f"{nome}_tubo{k}", [a, b], [0.017, 0.017], mq, r, seg=14, tampa=4)
    for sgy in (-1, 1):
        tubo(f"{nome}_garfo{sgy}", [(0.38, 0, 0.78), (0.49, sgy * 0.03, R)], [0.012, 0.011], mq, r, seg=12, tampa=3)
    tubo(nome + "_canote", [C, (-0.23, 0, 0.86)], [0.011, 0.011], M(pc("#9aa3b0")), r, seg=12, tampa=3)
    esfera(nome + "_selim", 0.12, 0.055, 0.03, M(pc("#3a2a20")), r, (-0.25, 0, 0.88), contorno=0.003, seg=24, an=12)
    tubo(nome + "_mesa", [(0.37, 0, 0.78), (0.33, 0, 0.96)], [0.011, 0.011], M(pc("#9aa3b0")), r, seg=12, tampa=3)
    tubo(nome + "_guidao", [(0.33, -0.28, 0.98), (0.31, -0.12, 0.97), (0.33, 0.0, 0.96), (0.31, 0.12, 0.97), (0.33, 0.28, 0.98)], [0.011] * 5, M(pc("#9aa3b0")), r, seg=12, tampa=3)
    for sgy in (-1, 1):
        tubo(f"{nome}_punho{sgy}", [(0.33, sgy * 0.2, 0.98), (0.33, sgy * 0.3, 0.98)], [0.017, 0.017], M(pc("#1c1c22")), r, seg=14, tampa=4)
    esfera(nome + "_campainha", 0.028, 0.028, 0.02, M(pc("#c8ccd6"), "#8a909c", "#ffffff"), r, (0.33, -0.15, 1.005), contorno=0.002, seg=20, an=12)
    cilindro(nome + "_campainha_b", 0.008, 0.02, M(pc("#5a626e")), r, (0.33, -0.15, 1.03), seg=10, contorno=0.0)
    cilindro(nome + "_coroa", 0.075, 0.012, M(pc("#9aa3b0")), r, (-0.08, -0.04, 0.32), seg=28, eixo="Y", contorno=0.002)
    tubo(nome + "_pedivela", [(-0.08, -0.06, 0.32), (-0.02, -0.08, 0.2)], [0.009, 0.009], M(pc("#5a626e")), r, seg=10, tampa=3)
    caixa(nome + "_pedal", (0.08, 0.06, 0.015), M(pc("#1c1c22")), r, (-0.01, -0.12, 0.19), chanfro=0.004)
    tubo(nome + "_corrente", [(-0.5, -0.04, R + 0.03), (-0.08, -0.04, 0.39), (-0.08, -0.04, 0.25), (-0.5, -0.04, R - 0.03)], [0.004] * 4, M(pc("#3a3d46")), r, seg=6, tampa=2, contorno=0.0)
    # cesta de vime na frente do guidão
    cx = 0.52; mc = M(pc("#c9a26a"), pc("#a07e4a"), "#ecd09a")
    caixa(nome + "_cesta_fundo", (0.3, 0.32, 0.015), mc, r, (cx, 0, 0.8), chanfro=0.004)
    for k in range(4):
        z = 0.82 + 0.055 * k
        for sx, sy, lx, ly in ((0, -0.16, 0.3, 0.012), (0, 0.16, 0.3, 0.012), (-0.15, 0, 0.012, 0.32), (0.15, 0, 0.012, 0.32)):
            caixa(f"{nome}_vime{k}_{sx}_{sy}", (lx, ly, 0.02), mc, r, (cx + sx, sy, z), chanfro=0.003, contorno=0.002)
    for sx in (-0.15, 0.15):
        for sy in (-0.16, 0.16):
            tubo(f"{nome}_cesta_m{sx}{sy}", [(cx + sx, sy, 0.8), (cx + sx, sy, 1.0)], [0.006, 0.006], mc, r, seg=8, tampa=2, contorno=0.002)
    if boneca:
        esfera(nome + "_boneca_cab", 0.05, 0.05, 0.05, M(PELE, borda="#e8cfa8"), r, (cx, 0, 1.07), contorno=0.003, seg=24, an=14)
        for sgy in (-1, 1):
            esfera(f"{nome}_boneca_olho{sgy}", 0.012, 0.012, 0.014, plano("#f3efe6"), r, (cx - 0.044, sgy * 0.017, 1.08), contorno=0.0, seg=12, an=8)
        torno(nome + "_boneca_vest", [(0.06, 0.82), (0.05, 0.95), (0.03, 1.02)], M(pc("#a8786f")), r, (cx, 0, 0), seg=24)
    return r


def sirene3d(nome, loc=(0, 0, 0), s=1.0, pai=None, acesa=True, poeira=0.0):
    """sirene de bairro em 3D: poste de concreto, braço, duas cornetas de metal e a luz vermelha no topo"""
    from props import _mix
    pc = lambda c: _mix(c, "#9a968a", poeira)
    r = empty(nome, pai, loc); r.scale = (s,) * 3
    cilindro(nome + "_poste", 0.07, 3.3, M(pc("#8a9096"), pc("#6a7076")), r, (0, 0, 1.65), seg=20, r2=0.05)
    caixa(nome + "_braco", (1.0, 0.08, 0.08), M(pc("#6a7076")), r, (0, 0, 2.82), chanfro=0.01)
    for k, sg in enumerate((-1, 1)):
        c = cilindro(f"{nome}_corneta{k}", 0.07, 0.5, M(pc("#8a4a36"), pc("#5e3022")), r, (sg * 0.55, 0, 2.82), seg=28, eixo="X", r2=0.24, tampa=False)
        if sg < 0:
            c.rotation_euler = (0, math.radians(180), 0)
        cilindro(f"{nome}_boca{k}", 0.22, 0.01, M("#2a1410"), r, (sg * 0.79, 0, 2.82), seg=28, eixo="X", contorno=0.0)
        cilindro(f"{nome}_caixa{k}", 0.09, 0.14, M(pc("#5a5048")), r, (sg * 0.24, 0, 2.82), seg=20, eixo="X")
    cilindro(nome + "_farol", 0.07, 0.14, brilha("#e2443a", 2.4) if acesa else M(pc("#6e2a26")), r, (0, 0, 3.38), seg=24, contorno=0.004)
    cilindro(nome + "_farol_tampa", 0.075, 0.02, M(pc("#3a3d46")), r, (0, 0, 3.46), seg=24)
    if acesa:
        halo_cam(nome + "_halo", (0, -0.08, 3.38), 0.9, "#e2443a", 0.45, pai=r)
    return r


def galao3d(nome, loc=(0, 0, 0), s=1.0, nivel=1.0, pai=None):
    """galão de água de 5 L em 3D: plástico azul translúcido (dá para ver o nível), a água por dentro, tampa, alça e rótulo"""
    r = empty(nome, pai, loc); r.scale = (s,) * 3
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0); bmesh.ops.scale(bm, vec=(0.2, 0.16, 0.28), verts=bm.verts)
    bmesh.ops.bevel(bm, geom=list(bm.edges) + list(bm.verts), offset=0.035, segments=4, affect="EDGES", profile=0.5)
    _objeto(nome + "_corpo", bm, vidro("#9fc8e0", 0.3, 0.5), r, (0, 0, 0.14), 0.003)
    if nivel > 0.02:
        caixa(nome + "_agua", (0.18, 0.14, 0.26 * nivel), M("#2f6f9e", "#24577c", "#8ec8ea"), r, (0, 0, 0.012 + 0.13 * nivel), chanfro=0.025, contorno=0.0)
    cilindro(nome + "_gargalo", 0.035, 0.05, vidro("#9fc8e0", 0.35, 0.5), r, (0, 0, 0.3), seg=20, contorno=0.002)
    cilindro(nome + "_tampa", 0.042, 0.03, M("#1f4f8a"), r, (0, 0, 0.335), seg=20)
    tubo(nome + "_alca", [(0.1, 0, 0.24), (0.14, 0, 0.23), (0.14, 0, 0.16), (0.1, 0, 0.15)], [0.012] * 4, vidro("#9fc8e0", 0.4, 0.5), r, seg=10, tampa=3, contorno=0.002)
    caixa(nome + "_rotulo", (0.14, 0.004, 0.1), M("#e8e2d0"), r, (0, -0.082, 0.13), chanfro=0.0, contorno=0.0)
    return r


def lata3d(nome, loc=(0, 0, 0), s=1.0, cor="#8e5a3a", pai=None, rot=0.0, aberta=False):
    r = empty(nome, pai, loc); r.scale = (s,) * 3; r.rotation_euler.z = math.radians(rot)
    cilindro(nome + "_c", 0.037, 0.1, M("#b4b8c0", "#80868e"), r, (0, 0, 0.05), seg=24, contorno=0.002)
    cilindro(nome + "_rot", 0.0375, 0.064, M(cor), r, (0, 0, 0.05), seg=24, contorno=0.0)
    cilindro(nome + "_faixa", 0.038, 0.012, M("#d8d0bb"), r, (0, 0, 0.05), seg=24, contorno=0.0)
    esfera(nome + "_selo", 0.017, 0.006, 0.017, M("#f0e6c8", "#d8ccaa"), r, (0, -0.036, 0.062), contorno=0.0008, seg=16, an=8)   # o desenho do rótulo
    icone = {"#8e5a3a": "#4a2e22", "#59603f": "#e8c040", "#4f6275": "#6a9a4a", "#a89f86": "#9aa3b0", "#7a3a30": "#c8402e"}.get(cor, "#4a2e22")
    for k, (dx, dz) in enumerate(((-0.004, 0.064), (0.005, 0.059), (0.0, 0.066))):
        esfera(f"{nome}_grao{k}", 0.0045, 0.003, 0.0045, M(icone), r, (dx, -0.041, dz), contorno=0.0, seg=10, an=6)
    for k, z in enumerate((0.03, 0.026)):
        caixa(f"{nome}_letra{k}", (0.03 - 0.01 * k, 0.002, 0.0025), M("#2a2622"), r, (0, -0.038, z), chanfro=0.0, contorno=0.0)
    if aberta:                                                       # lata vazia: aberta, escura por dentro, a tampa torta pendurada
        cilindro(nome + "_vazio", 0.033, 0.004, M("#14120f", "#14120f", "#14120f"), r, (0, 0, 0.1), seg=24, contorno=0.0)
        cilindro(nome + "_tampa_t", 0.02, 0.002, M("#c8ccd4", "#9aa0a8", "#ffffff"), r, (0.03, 0, 0.108), seg=16, contorno=0.0008)
        return r
    cilindro(nome + "_tampa_l", 0.034, 0.004, M("#c8ccd4", "#9aa0a8", "#ffffff"), r, (0, 0, 0.1), seg=24, contorno=0.001)
    anel(nome + "_borda", 0.035, 0.003, M("#d0d4da"), r, (0, 0, 0.1), eixo="Z", seg=24, contorno=0.0)
    return r


def estante3d(nome, loc=(0, 0, 0), s=1.0, nivel=1.0, pai=None, seed=2):
    """estante de madeira em 3D (1 x 0,35 x 1 m), três prateleiras com latas em duas fileiras; nivel = quanto da comida sobrou"""
    rnd = random.Random(seed)
    r = empty(nome, pai, loc); r.scale = (s,) * 3
    mad, mad_e = M("#8a5a34", "#6a4228"), M("#6a4228")
    for sx in (-0.5, 0.5):
        for sy in (-0.16, 0.16):
            caixa(f"{nome}_mont{sx}{sy}", (0.04, 0.04, 1.05), mad_e, r, (sx, sy, 0.525), chanfro=0.005)
    caixa(nome + "_fundo", (1.0, 0.015, 1.0), M("#3c4a40"), r, (0, 0.17, 0.5), chanfro=0.0)
    cores = ["#8e5a3a", "#59603f", "#4f6275", "#a89f86", "#7a3a30"]
    n_total = 9; ocupa = int(round(nivel * n_total))
    for k, z in enumerate((0.03, 0.36, 0.69)):
        caixa(f"{nome}_tab{k}", (1.04, 0.36, 0.03), mad, r, (0, 0, z), chanfro=0.006)
        for fila, y in enumerate((0.06, -0.06)):
            idx = list(range(n_total))
            quais = idx[:ocupa] if nivel > 0.5 else [i for i in idx if rnd.random() < nivel * 1.4][:max(0, ocupa)]
            for i in quais:
                lata3d(f"{nome}_lata{k}_{fila}_{i}", (-0.44 + 0.11 * i, y, z + 0.015), 1.0, cores[(i + k + fila) % len(cores)], r, rot=rnd.uniform(0, 360))
    return r


def lampada3d(nome, loc=(0, 0, 0), s=1.0, acesa=True, pai=None, fio=0.5):
    """lâmpada pendurada: fio, soquete preto, bulbo de vidro e o filamento (acesa = âmbar forte com brilho em volta)"""
    r = empty(nome, pai, loc); r.scale = (s,) * 3
    cilindro(nome + "_fio", 0.004, fio, M("#1c1c22"), r, (0, 0, fio / 2 + 0.06), seg=8, contorno=0.0)
    cilindro(nome + "_soquete", 0.022, 0.05, M("#2a2d34"), r, (0, 0, 0.04), seg=20)
    if acesa:
        esfera(nome + "_bulbo", 0.036, 0.036, 0.045, brilha("#ffd98a", 1.8), r, (0, 0, -0.03), contorno=0.0, seg=24, an=16)
        halo_cam(nome + "_halo", (0, 0, -0.03), 0.55, "#d9b66a", 0.42, pai=r)
    else:
        esfera(nome + "_bulbo", 0.036, 0.036, 0.045, vidro("#c8ccc0", 0.3, 0.5), r, (0, 0, -0.03), contorno=0.0, seg=24, an=16)
        tubo(nome + "_fila", [(-0.01, 0, -0.03), (0.0, 0, -0.01), (0.01, 0, -0.03)], [0.002] * 3, M("#3a3a34"), r, seg=6, tampa=2, contorno=0.0)
    return r


def gaiola3d(nome, loc=(0, 0, 0), s=1.0, vazia=False, pai=None):
    """gaiola da Pipoca em 3D (0,6 x 0,4 x 0,45 m): bandeja, grade de arame, casinha, feno, bebedouro; vazia = porta aberta e o suéter dobrado no fundo"""
    r = empty(nome, pai, loc); r.scale = (s,) * 3
    caixa(nome + "_bandeja", (0.6, 0.4, 0.07), M("#5a6a72", "#3f4d54"), r, (0, 0, 0.035), chanfro=0.012)
    rnd = random.Random(4)
    for k in range(40):
        esfera(f"{nome}_feno{k}", 0.03, 0.006, 0.005, M("#d9c27a", "#b8a060"), r, (rnd.uniform(-0.27, 0.27), rnd.uniform(-0.17, 0.17), 0.075), contorno=0.0, seg=8, an=4).rotation_euler.z = rnd.uniform(0, 3.14)
    ma = M("#aab4bb", "#7e8a92")
    for x in [i * 0.05 - 0.275 for i in range(12)]:
        for y in (-0.19, 0.19):
            if vazia and y < 0 and -0.03 < x < 0.13:                 # o vão da portinha aberta (a mão entra por aqui no 6E)
                cilindro(f"{nome}_b{x:.3f}{y}_cima", 0.0025, 0.14, ma, r, (x, y, 0.38), seg=6, contorno=0.0)
                continue
            cilindro(f"{nome}_b{x:.3f}{y}", 0.0025, 0.38, ma, r, (x, y, 0.26), seg=6, contorno=0.0)
    for y in [i * 0.05 - 0.175 for i in range(8)]:
        for x in (-0.29, 0.29):
            cilindro(f"{nome}_c{y:.3f}{x}", 0.0025, 0.38, ma, r, (x, y, 0.26), seg=6, contorno=0.0)
    caixa(nome + "_topo", (0.6, 0.4, 0.02), M("#5a6a72"), r, (0, 0, 0.455), chanfro=0.005)
    anel(nome + "_alca", 0.06, 0.006, M("#5a6a72"), r, (0, 0, 0.465), eixo="X", seg=24, a0=0, a1=180)
    caixa(nome + "_casa", (0.18, 0.16, 0.13), M("#8a5a34", "#6a4228"), r, (-0.17, 0.05, 0.135), chanfro=0.008)
    bm = bmesh.new()
    vs = [bm.verts.new(v) for v in ((-0.27, -0.03, 0.2), (-0.07, -0.03, 0.2), (-0.17, -0.03, 0.27), (-0.27, 0.13, 0.2), (-0.07, 0.13, 0.2), (-0.17, 0.13, 0.27))]
    for f in ((0, 1, 2), (3, 5, 4), (0, 2, 5, 3), (1, 4, 5, 2), (0, 3, 4, 1)):
        bm.faces.new([vs[i] for i in f])
    _objeto(nome + "_telhado", bm, M("#7a4a36", "#5a3426"), r, (0, 0, 0), 0.003)
    cilindro(nome + "_porta_casa", 0.035, 0.01, M("#1c1410"), r, (-0.17, -0.032, 0.12), seg=16, eixo="Y", contorno=0.0)
    cilindro(nome + "_bebe", 0.025, 0.2, vidro("#bfe2f2", 0.35), r, (0.25, -0.22, 0.28), seg=16, contorno=0.002)
    cilindro(nome + "_bebe_a", 0.022, 0.12, M("#6fb7e0"), r, (0.25, -0.22, 0.25), seg=16, contorno=0.0)
    if vazia:
        sueter3d(nome + "_su", (0.08, -0.02, 0.075), 1.0, pai=r)
        dob = empty(nome + "_portinha", r, (0.05, -0.19, 0.075)); dob.rotation_euler.x = math.radians(-118)    # a portinha caída para fora
        for k in range(4):
            cilindro(f"{nome}_porta_b{k}", 0.0025, 0.23, ma, dob, (-0.075 + 0.05 * k, 0, 0.115), seg=6, contorno=0.0)
        for z in (0.0, 0.23):
            cilindro(f"{nome}_porta_t{z}", 0.003, 0.16, ma, dob, (0, 0, z), seg=6, eixo="X", contorno=0.0)
        caixa(nome + "_aro_porta", (0.17, 0.008, 0.008), ma, r, (0.05, -0.19, 0.31), chanfro=0.0, contorno=0.0)
    return r


def sueter3d(nome, loc=(0, 0, 0), s=1.0, pai=None, dobrado=True):
    """o suéter de tricô vermelho da Pipoca: dobrado, em camadas, com a listra creme e as nervuras do tricô"""
    r = empty(nome, pai, loc); r.scale = (s,) * 3
    for k in range(3):
        caixa(f"{nome}_cam{k}", (0.17 - 0.01 * k, 0.11 - 0.008 * k, 0.022), M("#8e302b", "#64211f", "#d08070"), r, (0, 0, 0.011 + 0.021 * k), chanfro=0.009)
    caixa(nome + "_lista", (0.172, 0.112, 0.008), M("#a89f86"), r, (0, 0, 0.034), chanfro=0.003, contorno=0.0)
    for k in range(9):
        caixa(f"{nome}_nerv{k}", (0.004, 0.1, 0.004), M("#64211f"), r, (-0.075 + 0.019 * k, 0, 0.066), chanfro=0.0, contorno=0.0)
    return r


def prato3d(nome, loc=(0, 0, 0), s=1.0, nivel="cheio", pai=None):
    """prato fundo de louça (0,24 m) torneado, com a comida em volume: arroz, feijão, ervilhas e carne; ou 'pouco', 'colher', 'carne'"""
    r = empty(nome, pai, loc); r.scale = (s,) * 3
    torno(nome + "_prato", [(0.0, 0.0), (0.07, 0.0), (0.085, 0.012), (0.11, 0.022), (0.12, 0.026), (0.118, 0.03), (0.1, 0.026), (0.07, 0.016), (0.0, 0.014)],
          M("#ece7d8", "#c8c2b0", "#ffffff"), r, (0, 0, 0), seg=48)
    if nivel in ("cheio", "metade"):
        k = 1.0 if nivel == "cheio" else 0.55
        esfera(nome + "_arroz", 0.05 * k + 0.01, 0.045 * k + 0.01, 0.022 * k, M("#f6f1e2", "#d8d0bb"), r, (-0.03, -0.01, 0.022), contorno=0.002, seg=20, an=10)
        esfera(nome + "_feijao", 0.04 * k, 0.04 * k, 0.016 * k, M("#4a2e22", "#2e1c14"), r, (0.035, 0.02, 0.02), contorno=0.002, seg=20, an=10)
        for i in range(int(7 * k)):
            esfera(f"{nome}_erv{i}", 0.008, 0.008, 0.008, M("#6a9a4a", "#4a7a32"), r, (0.0 + 0.03 * math.cos(i), -0.05 + 0.02 * math.sin(i * 1.7), 0.024), contorno=0.001, seg=10, an=6)
        if nivel == "cheio":
            esfera(nome + "_carne", 0.035, 0.03, 0.016, M("#9a5a36", "#6e3e24"), r, (0.03, -0.045, 0.024), contorno=0.002, seg=20, an=10)
    elif nivel == "colher":
        esfera(nome + "_resto", 0.016, 0.014, 0.008, M("#f6f1e2", "#d8d0bb"), r, (0.0, 0.0, 0.017), contorno=0.001, seg=14, an=8)
        tubo(nome + "_colher", [(-0.02, -0.01, 0.02), (0.1, 0.09, 0.03)], [0.004, 0.004], M("#c8ccd6"), r, seg=8, tampa=2, contorno=0.002)
        esfera(nome + "_colher_c", 0.02, 0.013, 0.004, M("#c8ccd6"), r, (-0.03, -0.02, 0.019), contorno=0.002, seg=16, an=8)
    elif nivel == "carne":
        bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=24, v_segments=14, radius=1.0)
        rnd = random.Random(7)
        for v in bm.verts:
            v.co = Vector((v.co.x * 0.06 * (1 + 0.15 * rnd.uniform(-1, 1)), v.co.y * 0.045 * (1 + 0.15 * rnd.uniform(-1, 1)), max(v.co.z, -0.3) * 0.028))
        _objeto(nome + "_carne", bm, M("#6e3a22", "#4a2414", "#c88a5a"), r, (0, 0, 0.03), 0.002)
        esfera(nome + "_gordura", 0.02, 0.014, 0.008, M("#d9b48a", "#b08a62"), r, (0.025, -0.01, 0.052), contorno=0.0, seg=14, an=8)
    return r


def mesa3d(nome, loc=(0, 0, 0), tam=(2.2, 1.0, 0.78), pai=None):
    r = empty(nome, pai, loc)
    w, d, h = tam
    caixa(nome + "_tampo", (w, d, 0.05), M("#6b5a3e", "#4e4130", "#a8916a"), r, (0, 0, h - 0.025), chanfro=0.012)
    for sx in (-1, 1):
        for sy in (-1, 1):
            caixa(f"{nome}_perna{sx}{sy}", (0.06, 0.06, h - 0.05), M("#4e4130"), r, (sx * (w / 2 - 0.08), sy * (d / 2 - 0.08), (h - 0.05) / 2), chanfro=0.006)
    caixa(nome + "_travessa", (w - 0.2, 0.04, 0.06), M("#4e4130"), r, (0, 0, 0.18), chanfro=0.005)
    return r


def cadeira3d(nome, loc=(0, 0, 0), rot=0.0, pai=None):
    r = empty(nome, pai, loc); r.rotation_euler.z = math.radians(rot)
    mad, mad_e = M("#8a5a34", "#6a4228"), M("#6a4228")
    caixa(nome + "_assento", (0.44, 0.42, 0.04), mad, r, (0, 0, 0.45), chanfro=0.008)
    for sx in (-1, 1):
        for sy in (-1, 1):
            caixa(f"{nome}_perna{sx}{sy}", (0.04, 0.04, 0.45), mad_e, r, (sx * 0.19, sy * 0.18, 0.225), chanfro=0.005)
        caixa(f"{nome}_mont{sx}", (0.04, 0.04, 0.48), mad_e, r, (sx * 0.19, 0.18, 0.69), chanfro=0.005)
    for k, z in enumerate((0.66, 0.84)):
        caixa(f"{nome}_ripa{k}", (0.42, 0.03, 0.07), mad, r, (0, 0.18, z), chanfro=0.006)
    return r


def cama3d(nome, loc=(0, 0, 0), dobrada=False, manta="#6e6a4a", pai=None):
    """cama de ferro em 3D: cabeceira e pé de tubo, colchão, travesseiro e a manta (embolada por cima, ou dobrada no pé)"""
    r = empty(nome, pai, loc)
    ferro = M("#3a4046", "#2a3036", "#8a9298")
    for x in (-0.95, 0.95):
        for y in (-0.42, 0.42):
            cilindro(f"{nome}_pe{x}{y}", 0.02, 0.7 if x > 0 else 0.55, ferro, r, (x, y, 0.35 if x > 0 else 0.275), seg=12)
        tubo(f"{nome}_trav{x}", [(x, -0.42, 0.7 if x > 0 else 0.55), (x, 0.42, 0.7 if x > 0 else 0.55)], [0.018, 0.018], ferro, r, seg=12, tampa=3)
        for k in range(4):
            cilindro(f"{nome}_grade{x}{k}", 0.008, 0.25 if x > 0 else 0.12, ferro, r, (x, -0.27 + 0.18 * k, 0.56 if x > 0 else 0.48), seg=8, contorno=0.002)
    caixa(nome + "_estrado", (1.9, 0.86, 0.06), M("#4a5258"), r, (0, 0, 0.26), chanfro=0.01)
    caixa(nome + "_colchao", (1.86, 0.82, 0.14), M("#b8b19a", "#8f8a76", "#e8e2c8"), r, (0, 0, 0.36), chanfro=0.04)
    caixa(nome + "_trav", (0.4, 0.6, 0.1), M("#d8d0bb", "#aaa28c"), r, (0.68, 0, 0.47), chanfro=0.045)
    if dobrada:
        caixa(nome + "_manta", (0.42, 0.78, 0.09), M(manta), r, (-0.68, 0, 0.47), chanfro=0.03)
    else:
        caixa(nome + "_manta", (1.32, 0.84, 0.1), M(manta), r, (-0.25, 0, 0.475), chanfro=0.045, rot=(2, -1.5, 0))
        caixa(nome + "_manta_dobra", (0.25, 0.86, 0.12), M(manta), r, (0.38, 0, 0.49), chanfro=0.05, rot=(0, -8, 0))
    return r
