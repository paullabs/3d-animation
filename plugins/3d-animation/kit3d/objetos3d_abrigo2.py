"""Peças novas da parte 2 de "O abrigo" (26/10/2026), no mesmo estilo do kit (heroi3d.estilo: tom chapado, faixa de sombra, borda de luz, contorno):
- sem_osso(): o Sem-Osso. Gente que derreteu numa gosma preta e se juntou de novo: corpo de óleo com brilho frio na borda, braços e pernas
  que dobram onde não tem junta (tubos moles, em S), sem pé (a base escorre no chão), olho cinza APAGADO (os vivos têm o olho branco aceso),
  pingos, e pedaços da roupa de quem foi grudados (o avental da padeira, o boné do rapaz do mercado);
- gosma(): poças e corpos de gosma (metaballs convertidas em malha, com contorno);
- pano_rosto(), pano_pescoco(), fone(): o pano no nariz e na boca do grupo (eles respiraram o ar), e o fone da mulher do rádio;
- GRUPO e faz_grupo(): os 9 do galpão, cada um com uma roupa (nada de clone);
- radio3d, mapa3d, lanterna3d, taco3d, tambor_fogo3d, escada3d, portao3d, galpao3d, torre3d.
A frente dos objetos olha para -y, z para cima (como no kit)."""
import math, random
import bpy
from mathutils import Vector
from lib import empty, srgb
import heroi3d as H3
from heroi3d import esfera, tubo, estilo, plano, _objeto
import elenco3d_abrigo as E3
import objetos3d_abrigo as O3
import objetos3d_abrigo_b as O3B

OLEO, OLEO_S, OLEO_BORDA = "#15161b", "#08080b", "#8fa3ad"    # a gosma: preto de óleo com brilho frio
OLHO_APAGADO = "#6b6d66"


def M_oleo():
    return estilo(OLEO, OLEO_S, OLEO_BORDA, limiar=0.46, rim=0.62)


# ---------------------------------------------------------------- gosma (metaball -> malha)
def gosma(nome, bolhas, pai=None, loc=(0, 0, 0), mat=None, res=0.02, contorno=0.004, brilhos=0, seed=1):
    """bolhas = [(x, y, z, raio, (sx, sy, sz))]: elipsoides que se fundem como líquido grosso. Vira malha com o contorno do estilo.
    brilhos = quantos pontinhos claros de reflexo de óleo espalhar por cima"""
    mb = bpy.data.metaballs.new(nome + "_mb"); mb.resolution = res; mb.render_resolution = res; mb.threshold = 0.22
    ob = bpy.data.objects.new(nome + "_mb", mb); bpy.context.scene.collection.objects.link(ob)
    for x, y, z, r, s in bolhas:
        e = mb.elements.new(); e.type = "ELLIPSOID"; e.co = (x, y, z); e.radius = r
        e.size_x, e.size_y, e.size_z = s
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(ob.evaluated_get(dg)); me.name = nome
    bpy.data.objects.remove(ob, do_unlink=True)
    for p in me.polygons:
        p.use_smooth = True
    o = bpy.data.objects.new(nome, me); bpy.context.scene.collection.objects.link(o)
    o.parent = pai; o.location = loc
    me.materials.append(mat or M_oleo())
    if contorno:
        me.materials.append(H3.tinta())
        md = o.modifiers.new("contorno", "SOLIDIFY"); md.thickness = contorno; md.offset = 1.0; md.use_flip_normals = True; md.material_offset = 1
    if brilhos and len(me.vertices):
        rnd = random.Random(seed); vs = [v for v in me.vertices if v.normal.z > 0.35 and v.normal.y < 0.2]
        for k in range(min(brilhos, len(vs))):
            v = rnd.choice(vs); p = v.co + v.normal * 0.004
            esfera(f"{nome}_br{k}", 0.006, 0.006, 0.004, plano("#dfe7ea"), o, tuple(p), contorno=0.0, seg=10, an=6)
    return o


def poca(nome, cx, cy, rx, ry, pai=None, seed=1, gotas=5, alt=0.025):
    """poça de gosma no chão: uma bolha larga e baixa com gotas em volta"""
    rnd = random.Random(seed)
    b = [(cx, cy, 0.0, 1.0, (rx * 0.7, ry * 0.7, alt))]
    for k in range(gotas):
        a = rnd.uniform(0, 2 * math.pi); d = rnd.uniform(0.9, 1.25)
        b.append((cx + rx * 0.8 * d * math.cos(a), cy + ry * 0.8 * d * math.sin(a), 0.0, 1.0, (rx * rnd.uniform(0.15, 0.3), ry * rnd.uniform(0.15, 0.3), alt * 0.8)))
    return gosma(nome, b, pai, brilhos=4, seed=seed)


def mancha(nome, pontos, larg=0.12, seed=1, pai=None):
    """rastro chato de gosma no chão (por onde ela escorreu): manchas irregulares que se sobrepõem ao longo de 'pontos' [(x, y)],
    sem contorno entre elas (uma mancha só), com pontinhos de brilho"""
    import cena, props
    r = empty(nome, pai, (0, 0, 0)); rnd = random.Random(seed)
    chapado = props.FM("#121318")                                    # chato no chão: sem borda de luz (senão vira azul-claro)
    for k, (x, y) in enumerate(pontos):
        w = larg * rnd.uniform(0.8, 1.2)
        pts = O3B.blob(x, y, w, w * 0.75, z=0.004 + 0.0004 * k, seed=seed + k, ruido=0.25)
        o = cena.poly_mesh(f"{nome}_{k}", pts, chapado); o.parent = r
        if k % 2 == 0:
            esfera(f"{nome}_br{k}", 0.008, 0.005, 0.002, plano("#dfe7ea"), r, (x + w * 0.3, y - w * 0.2, 0.008), contorno=0.0, seg=10, an=6)
    return r


def pingo(nome, pai, p0, comp=0.08, r=0.012):
    """um pingo pendurado: fio que afina e a gota na ponta"""
    x, y, z = p0
    tubo(nome, [(x, y, z), (x, y - 0.004, z - comp * 0.6), (x, y - 0.006, z - comp)], [r, r * 0.55, r * 0.4], M_oleo(), pai, seg=12, tampa=4, contorno=0.0025)
    esfera(nome + "_gota", r * 1.15, r * 1.15, r * 1.5, M_oleo(), pai, (x, y - 0.006, z - comp - r), contorno=0.0025, seg=14, an=10)


# ---------------------------------------------------------------- o Sem-Osso
_GUARDA = ("olho", "boca", "_av", "_cab", "coque", "bone", "_aba", "colete", "palpebra", "sobr", "_br")


def sem_osso(nome, chave="padeira", loc=(0, 0, 0), rot=0.0, curva=1.0, seed=2, bracos_frente=True):
    """o Sem-Osso que foi a 'chave' do elenco do ep. 1 (padeira, mercado, viz1...): mesma silhueta e acessórios, corpo de gosma.
    curva (0 a 1): quanto ele está curvado e mole. Devolve o Heroi3D (com .raiz, .tronco, .cabeca)."""
    e = dict(E3.ESPEC[chave]); acess = e.pop("acess")
    for k in ("roupa", "calca", "escura", "gola"):
        e[k] = OLEO
    h = H3.Heroi3D(nome, sapato=OLEO, borda=OLEO_BORDA, **e)
    h.bw = e.get("body_w", 1.0)
    sujo = {"#c9c6ba": "#5e5c56", "#8a5a4a": "#5b4034", E3.PAL["musgo"]: "#33433a"}
    for a in acess:
        a = list(a)
        if len(a) > 1 and isinstance(a[-1], str) and a[-1].startswith("#"):
            a[-1] = sujo.get(a[-1], a[-1])
        {"cabelo": E3.cabelo, "barba": E3.barba, "bigode": E3.bigode, "bone": E3.bone, "tiara": E3.tiara, "tranca": E3.tranca,
         "avental": E3.avental, "colete": E3.colete}[a[0]](h, *a[1:])
    go = M_oleo()
    for o in [h.raiz] + list(h.raiz.children_recursive):
        if o.type != "MESH":
            continue
        n = o.name[len(nome):]
        if any(g in n for g in _GUARDA):
            continue
        if o.data.materials:
            o.data.materials[0] = go
    # rosto: olho cinza apagado, sem sobrancelha, boca torta e aberta
    for s in ("F", "B"):
        h.olhos[s].data.materials[0] = plano(OLHO_APAGADO)
        h.sobrancelhas[s].scale = (0.0001,) * 3
    h.rosto(boca="o", lid=0.25)
    h.boca.data.materials[0] = plano("#2a2c2a"); h.boca.scale = (1.4, 1.0, 1.9)
    # sem pé e sem os membros duros: some com braço, perna e sapato do boneco; põe tubos moles no lugar
    for o in list(h.raiz.children_recursive):
        if o.type == "MESH" and any(k in o.name for k in ("_braco", "_antebraco", "_cot", "_deltoide", "_punhoc", "_pulso", "_mao", "_coxa",
                                                            "_joelho", "_canela", "_sapato", "_sola")):
            o.hide_render = True; o.hide_viewport = True
    alt = 0.86 - 0.09 * curva                                              # afunda: a gosma não segura o peso
    h.pose(tronco=26 * curva, cabeca=-14 * curva, alt=alt)
    h.tronco.rotation_euler.y = math.radians(9 * curva)                    # desaba para um lado
    h.cabeca.rotation_euler.y = math.radians(-24 * curva)                  # cabeça tombada, como se o pescoço não aguentasse
    for s, sx in (("F", -1), ("B", 1)):
        h.ombro[s].rotation_euler = (math.radians((-18 if bracos_frente else 10) * curva), math.radians(sx * -6), 0)
    av = bpy.data.objects.get(nome + "_av")
    if av:
        av.scale = (0.82, 1.0, 0.74); av.location.z += 0.05
    bpy.context.view_layer.update()
    rnd = random.Random(seed)
    for s, sx in (("F", -1), ("B", 1)):
        # braço mole: sai do ombro e cai em S, dobrando no meio do antebraço (onde não tem junta)
        o = h.ombro[s]
        dob = 0.13 * curva
        pts = [(0, 0, 0), (sx * 0.03, -0.04 - dob * 0.3, -0.17), (sx * 0.06, -0.08 - dob, -0.35), (sx * 0.04, -0.02 - dob * 0.4, -0.52),
               (sx * 0.0, 0.07, -0.64), (sx * -0.01, 0.06, -0.78)]
        tubo(f"{nome}_bracomole{s}", pts, [0.046, 0.043, 0.04, 0.036, 0.032, 0.028], go, o, seg=28, tampa=8, contorno=0.005)
        mao = Vector(pts[-1])
        gosma(f"{nome}_maomole{s}", [(mao.x, mao.y, mao.z - 0.03, 1.0, (0.05, 0.045, 0.07)), (mao.x + sx * 0.01, mao.y - 0.01, mao.z - 0.1, 1.0, (0.022, 0.02, 0.05))],
              o, contorno=0.004)
        pingo(f"{nome}_pingo{s}", o, (sx * 0.03, -0.065 - dob, -0.36), comp=0.07 + 0.04 * rnd.random(), r=0.011)
        # perna mole: coxa e canela num tubo só, que entorta para fora no joelho e escorre até o chão
        q = h.perna[s]
        L = alt - 0.02
        lp = [(0, 0, 0), (sx * 0.03, -0.04, -0.26 * L / 0.84), (sx * (0.1 * curva + 0.01), -0.09 * curva, -0.45 * L / 0.84),
              (sx * 0.05, 0.0, -0.66 * L / 0.84), (sx * 0.03, 0.03, -L)]
        tubo(f"{nome}_pernamole{s}", lp, [0.046, 0.042, 0.04, 0.042, 0.05], go, q, seg=28, tampa=8, contorno=0.005)
    # a base escorrida: poça larga embaixo, que liga os dois pés
    b = [(0.0, 0.0, 0.0, 1.0, (0.2, 0.17, 0.03))]
    for k in range(7):
        a = 2 * math.pi * k / 7 + rnd.uniform(-0.3, 0.3); d = rnd.uniform(0.8, 1.2)
        b.append((0.16 * d * math.cos(a), 0.13 * d * math.sin(a), 0.0, 1.0, (0.1, 0.085, 0.022)))
    b += [(-0.07, 0.0, 0.04, 1.0, (0.06, 0.06, 0.06)), (0.07, 0.0, 0.04, 1.0, (0.06, 0.06, 0.06))]
    gosma(f"{nome}_base", b, h.raiz, brilhos=5, seed=seed)
    pingo(f"{nome}_queixo", h.cabeca, (0.02, -h.R * 0.85, h.R * 0.35), comp=0.06, r=0.01)
    # o tronco empelota (gosma que ainda escorre)
    j = bpy.data.objects.get(nome + "_jaqueta")
    if j:
        tx = bpy.data.textures.new(nome + "_tx", "CLOUDS"); tx.noise_scale = 0.09
        d = j.modifiers.new("pelota", "DISPLACE"); d.texture = tx; d.strength = 0.03 * curva; d.mid_level = 0.5
        j.modifiers.move(len(j.modifiers) - 1, 0)
    for k in range(6):
        p = Vector((rnd.uniform(-0.09, 0.09), -0.09, rnd.uniform(0.15, 0.4)))
        esfera(f"{nome}_br{k}", 0.006, 0.004, 0.006, plano("#dfe7ea"), h.tronco, tuple(p), contorno=0.0, seg=10, an=6)
    deforma_cabeca(h, nome, curva, seed)
    h.raiz.location = loc; h.raiz.rotation_euler.z = math.radians(rot)
    return h



def deforma_cabeca(h, nome, curva=1.0, seed=2):
    """cabeça de Sem-Osso (pedido de 26/10: mais deformada, inspirada em monstros do Fallout (os ghouls: pele derretida, sem nariz, olhos desiguais,
    mandíbula caída) e NÃO como o Demogorgon do Stranger Things (sem rosto aberto em pétalas, sem cabeça lisa e fina): crânio alongado e torto,
    um olho grande afundado e outro pequeno alto, um lóbulo de gosma caído sobre o lado, a mandíbula pendurada com a boca preta aberta e dentes tortos,
    sem nariz, sem cabelo (só um tufo ralo), e escorridos de gosma da órbita ao queixo."""
    r = h.R; C = h.cabeca; rnd = random.Random(seed); go = M_oleo()
    for n in ("_cab", "_massa", "_boca"):                              # o 'capacete' de cabelo some; fica só um tufo
        o = bpy.data.objects.get(nome + n)
        if o:
            o.hide_render = True; o.hide_viewport = True
    if h.boca is not None:
        bpy.data.objects.remove(h.boca, do_unlink=True); h.boca = None
    cr = bpy.data.objects[nome + "_cranio"]
    # crânio: comprido para cima e achatado dos lados, torto
    zc = r * 1.08; rx, ry, rz = r * 0.9, r * 0.98, r * 1.16
    cr.location.z = zc; cr.scale = (0.9, 0.98, 1.16); cr.rotation_euler = (0, math.radians(7 * curva), 0)
    tx = bpy.data.textures.new(nome + "_txc", "CLOUDS"); tx.noise_scale = 0.07; tx.noise_depth = 2
    d = cr.modifiers.new("derrete", "DISPLACE"); d.texture = tx; d.strength = r * 0.12 * curva; d.mid_level = 0.5
    cr.modifiers.move(len(cr.modifiers) - 1, 0)

    def na_casca(x, z, k=0.996):
        """ponto na frente do crânio deformado (elipsoide) para pôr olhos e boca"""
        v = 1.0 - (x / rx) ** 2 - ((z - zc) / rz) ** 2
        return (x, -ry * math.sqrt(max(v, 0.02)) * k, z)
    # olhos desiguais: o esquerdo (F) grande, baixo e afundado; o direito (B) pequeno e alto
    for s, x, z, esc in (("F", -r * 0.40, r * 0.62, 1.5), ("B", r * 0.42, r * 1.22, 0.62)):
        e = h.olhos[s]; e.location = na_casca(x, z, 1.07); e.scale = (esc, 2.2, esc * 1.05)
        n = Vector((e.location.x * 0.4, e.location.y, e.location.z - zc)).normalized()
        e.rotation_mode = "QUATERNION"; e.rotation_quaternion = n.to_track_quat("Y", "Z"); e.rotation_mode = "XYZ"
        lid = h.olhos[s + "_lid"]; lid.location = na_casca(x, z + (0.012 if s == "F" else 0.006), 1.06); lid.scale = (esc, 2.2, 0.0001)
        lid.rotation_mode = "QUATERNION"; lid.rotation_quaternion = n.to_track_quat("Y", "Z"); lid.rotation_mode = "XYZ"
        o = h.olhos[s]; o.data.materials[0] = plano(OLHO_APAGADO)
    # órbita funda: anel de gosma em volta do olho grande
    px, py, pz = na_casca(-r * 0.40, r * 0.62, 1.0)
    gosma(nome + "_orbita", [(px, py + r * 0.05, pz, 1.0, (r * 0.34, r * 0.1, r * 0.4))], C, mat=estilo("#2a3138", "#161a1e", OLEO_BORDA), res=0.006, contorno=0.003)
    # lóbulo de gosma derretida caindo do lado direito do crânio, por cima do olho pequeno, até a bochecha
    lb = [(r * 0.62, -r * 0.55, r * (1.42 - 0.2 * k), 1.0, (r * (0.3 - 0.02 * k), r * 0.26, r * 0.26)) for k in range(5)]
    lb.append((r * 0.7, -r * 0.35, r * 0.4, 1.0, (r * 0.2, r * 0.22, r * 0.3)))
    gosma(nome + "_lobulo", lb, C, mat=estilo("#222830", "#121519", OLEO_BORDA), res=0.006, contorno=0.003, brilhos=3, seed=seed)
    # sem nariz: só dois furinhos
    for sx in (-1, 1):
        px, py, pz = na_casca(sx * r * 0.07, r * 0.62)
        esfera(f"{nome}_narina{sx}", r * 0.04, r * 0.03, r * 0.07, plano("#5a2424"), C, (px, py + r * 0.01, pz), contorno=0.0, seg=10, an=8)
    # mandíbula caída: a boca preta aberta no meio do rosto (abaixo do 'nariz'), dentes tortos em cima e embaixo, e a bolha mole da mandíbula pendurada atrás
    mx, my, mz = na_casca(0.0, r * 0.2)
    gosma(nome + "_mandibula", [(mx, my + r * 0.3, mz - r * 0.15 - r * 0.2 * k, 1.0, (r * (0.46 - 0.07 * k), r * 0.3, r * 0.26)) for k in range(3)],
          C, res=0.006, contorno=0.003, brilhos=3, seed=seed + 1)
    esfera(nome + "_boca", r * 0.36, r * 0.05, r * 0.4, plano("#5a2424"), C, (mx, my - r * 0.1, mz - r * 0.05), contorno=0.0, seg=24, an=16)
    h.boca = bpy.data.objects[nome + "_boca"]
    dm = estilo("#cfc9b6", "#8a8472", OLEO_BORDA)
    for k in range(7):                                                # dentes tortos e desiguais: em cima, curtos
        a = (k - 3) * r * 0.1
        esfera(f"{nome}_dentec{k}", r * 0.035, r * 0.03, r * rnd.uniform(0.05, 0.1), dm, C, (mx + a + rnd.uniform(-0.008, 0.008), my - r * 0.15, mz + r * 0.3 - r * rnd.uniform(0.0, 0.03)),
               contorno=0.002, seg=8, an=6)
    for k in range(5):                                                # embaixo, longos e para fora (a mandíbula caiu)
        a = (k - 2) * r * 0.12
        esfera(f"{nome}_denteb{k}", r * 0.035, r * 0.03, r * rnd.uniform(0.08, 0.17), dm, C, (mx + a + rnd.uniform(-0.01, 0.01), my - r * 0.15, mz - r * 0.3 + r * rnd.uniform(0.0, 0.04)),
               contorno=0.002, seg=8, an=6)
    pingo(nome + "_baba", C, (mx + r * 0.1, my - r * 0.12, mz - r * 0.42), comp=0.12, r=0.01)
    # pele arruinada (ghoul): caroços de gosma cinza no alto do crânio e uma rachadura da testa até a órbita grande
    cinza = estilo("#2c333b", "#171b20", OLEO_BORDA)
    for k, (x, z, rr) in enumerate(((-0.45, 1.75, 0.2), (0.2, 1.95, 0.16), (0.55, 1.6, 0.14), (-0.1, 1.45, 0.12))):
        px, py, pz = na_casca(x * r, z * r, 1.0)
        gosma(f"{nome}_caroco{k}", [(px, py + r * 0.04, pz, 1.0, (r * rr, r * 0.1, r * rr * 0.8))], C, mat=cinza, res=0.006, contorno=0.003)
    rach = [na_casca(x * r, z * r, 1.012) for x, z in ((-0.1, 2.0), (-0.22, 1.7), (-0.15, 1.45), (-0.34, 1.12), (-0.38, 0.85))]
    tubo(nome + "_rachadura", rach, [r * 0.018, r * 0.014, r * 0.02, r * 0.014, r * 0.012], estilo("#07080a", "#07080a", "#07080a"), C, seg=8, tampa=3, contorno=0.0)
    pingo(nome + "_lagrima", C, na_casca(-r * 0.4, r * 0.45), comp=0.17, r=0.009)
    pingo(nome + "_lagrima2", C, na_casca(-r * 0.46, r * 0.42), comp=0.1, r=0.007)
    # cabelo: sobra um tufo ralo e caído (coque da padeira) ou o boné torto (rapaz do mercado)
    cq = bpy.data.objects.get(nome + "_coque")
    if cq:
        cq.location = (r * 0.55, r * 0.75, r * 1.45); cq.scale = (0.45, 0.45, 0.8); cq.rotation_euler = (0.4, math.radians(30), 0)
    for n in ("_bone", "_aba"):
        o = bpy.data.objects.get(nome + n)
        if o:
            o.rotation_euler = (math.radians(14), math.radians(20), math.radians(10)); o.location.x += r * 0.12; o.location.z += r * 0.1
    # o pescoço fica mole: a cabeça pende para a frente e para o lado
    h.cabeca.rotation_euler = (math.radians(-18 * curva), math.radians(-14 * curva), math.radians(6 * curva))


# ---------------------------------------------------------------- o grupo do galpão
def pano_rosto(h, cor):
    """pano amarrado no nariz e na boca (eles respiraram o ar lá fora): frente do rosto abaixo dos olhos + faixa em volta + nó na nuca"""
    m = estilo(cor, None, h.borda)
    E3._casca(h.nome + "_pano", h, 1.05, lambda a: -0.14 - 0.08 * (1 - max(0.0, math.cos(a))), lambda a: -0.86 + 0.25 * (1 - max(0.0, math.cos(a))),
              m, contorno=0.004, phi=(-1.75, 1.75), colunas=110, linhas=14)
    E3._casca(h.nome + "_panofx", h, 1.05, lambda a: -0.16, lambda a: -0.3, m, contorno=0.003)
    r = h.R
    esfera(h.nome + "_no", r * 0.16, r * 0.12, r * 0.13, m, h.cabeca, (0, r * 1.02, r * 0.78), contorno=0.003, seg=16, an=10)
    for k, dx in enumerate((-0.03, 0.02)):
        tubo(f"{h.nome}_ponta{k}", [(dx, r * 1.05, r * 0.75), (dx * 1.6, r * 1.12, r * 0.45)], [0.012, 0.008], m, h.cabeca, seg=10, tampa=4, contorno=0.002)


def pano_pescoco(h, cor):
    """o pano abaixado no pescoço (o líder fala de cara limpa)"""
    m = estilo(cor, None, h.borda)
    E3._casca(h.nome + "_pano", h, 1.07, lambda a: -0.72, lambda a: -1.0, m, contorno=0.004)


def fone(h, cor="#2e3236"):
    m = estilo(cor, None, h.borda); r = h.R
    O3.anel(h.nome + "_arco", r * 1.12, 0.009, m, h.cabeca, (0, 0, r), eixo="Y", a0=10, a1=170)
    for s, x in (("F", -1), ("B", 1)):
        esfera(f"{h.nome}_conc{s}", 0.022, 0.05, 0.055, m, h.cabeca, (x * r * 1.08, 0, r * 0.95), contorno=0.003, seg=20, an=12)


# chave -> (Heroi3D, acessórios, pano)
GRUPO = {
    "lider": dict(roupa="#6a5844", calca="#33302b", escura="#4e4132", gola="#4e4132", cabeca=0.78, body_w=1.14, arm_len=1.12,
                  acess=[("cabelo", "recuado", "#a9a499"), ("barba", "#7e7a72"), ("bigode", "#a9a499")], pano=("pescoco", "#6d6a52")),
    "radio": dict(roupa="#56656e", calca="#2f3236", escura="#434f57", gola="#434f57", cabeca=0.76, body_w=1.0, arm_len=1.12, luvas=True,
                  acess=[("cabelo", "coque", "#2a1e18")], pano=("rosto", "#a89f86"), fone=True),
    "cochicho": dict(roupa="#7a6a58", calca="#3a3631", escura="#5e5244", gola="#5e5244", cabeca=0.76, body_w=1.02, arm_len=1.1,
                     acess=[("cabelo", "recuado", "#bdb9ad"), ("bigode", "#bdb9ad")], pano=("rosto", "#8c8d84")),
    "taco": dict(roupa="#46604f", calca="#2e332c", escura="#354a3c", gola="#354a3c", cabeca=0.8, body_w=1.22, arm_len=1.14,
                 acess=[("cabelo", "curto", "#1e1a18"), ("barba", "#2a2826")], pano=("rosto", "#59603f")),
    "jovem": dict(roupa="#8a7d5e", calca="#3e3a30", escura="#6e6448", gola="#6e6448", cabeca=0.8, body_w=1.0, arm_len=1.14,
                  acess=[("cabelo", "curto", "#3a2418")], pano=("rosto", "#4f6275")),
    "solto": dict(roupa="#6c5866", calca="#33302f", escura="#54434f", gola="#54434f", cabeca=0.76, body_w=0.98, arm_len=1.12,
                  acess=[("cabelo", "solto", "#3a2a22")], pano=("rosto", "#8e8c84")),
    "careca": dict(roupa="#5e6a5a", calca="#2f342e", escura="#465046", gola="#465046", cabeca=0.82, body_w=1.16, arm_len=1.12,
                   acess=[("barba", "#3a3a36")], pano=("rosto", "#a89f86")),
    "trancas": dict(roupa="#7d6a62", calca="#3a3431", escura="#5e504a", gola="#5e504a", cabeca=0.78, body_w=0.96, arm_len=1.1,
                    acess=[("cabelo", "curto", "#2a1c16"), ("tranca", "#2a1c16")], pano=("rosto", "#6e6a4a")),
    "menino": dict(roupa="#4a5560", calca="#2a2e33", escura="#3a434c", gola="#3a434c", cabeca=0.92, body_w=0.9, arm_len=1.0, escala=0.84,
                   acess=[("cabelo", "curto", "#1e1a18")], pano=("rosto", "#9a8a6a")),
}


def faz_grupo(chave, nome):
    e = dict(GRUPO[chave]); acess = e.pop("acess"); pano = e.pop("pano"); fon = e.pop("fone", False)
    h = H3.Heroi3D(nome, sapato="#1e2420", borda=E3.BORDA, **e)
    h.bw = e.get("body_w", 1.0)
    for a in acess:
        {"cabelo": E3.cabelo, "barba": E3.barba, "bigode": E3.bigode, "tranca": E3.tranca}[a[0]](h, *a[1:])
    (pano_rosto if pano[0] == "rosto" else pano_pescoco)(h, pano[1])
    if fon:
        fone(h)
    return h


# ---------------------------------------------------------------- objetos do galpão
def radio3d(nome, loc=(0, 0, 0), s=1.0, pai=None, aceso=True):
    """rádio de válvula numa caixa de madeira (0,46 x 0,26 x 0,32 m): tela de pano do alto-falante, mostrador âmbar, dois botões, antena"""
    r = empty(nome, pai, loc); r.scale = (s,) * 3
    mad = O3.M("#6b4a2e", "#4a321e")
    O3.caixa(nome + "_caixa", (0.46, 0.26, 0.32), mad, r, (0, 0, 0.16), chanfro=0.02)
    O3.caixa(nome + "_tela", (0.2, 0.01, 0.2), O3.M("#8a7d5e", "#6e6448"), r, (-0.1, -0.13, 0.17), chanfro=0.004, contorno=0.002)
    for k in range(6):
        O3.caixa(f"{nome}_fresta{k}", (0.18, 0.004, 0.006), O3.M("#5a5040"), r, (-0.1, -0.137, 0.09 + 0.032 * k), chanfro=0.0, contorno=0.0)
    O3.caixa(nome + "_most", (0.15, 0.008, 0.06), O3.brilha("#f0b45a", 1.6 if aceso else 0.2), r, (0.12, -0.132, 0.22), chanfro=0.003, contorno=0.002)
    O3.caixa(nome + "_agulha", (0.004, 0.004, 0.05), O3.M("#2a1c14"), r, (0.1, -0.138, 0.22), chanfro=0.0, contorno=0.0)
    for k, x in enumerate((0.08, 0.16)):
        O3.cilindro(f"{nome}_botao{k}", 0.022, 0.025, O3.M("#2a2420", "#18140f"), r, (x, -0.14, 0.1), eixo="Y")
    tubo(nome + "_antena", [(0.18, 0.05, 0.32), (0.26, 0.08, 0.62)], [0.004, 0.003], O3.M("#9a968a"), r, seg=8, tampa=3, contorno=0.0015)
    return r


def fone_mesa3d(nome, loc, pai=None):
    r = empty(nome, pai, loc); m = O3.M("#2e3236")
    O3.anel(nome + "_arco", 0.09, 0.008, m, r, (0, 0, 0.02), eixo="Z", a0=200, a1=340)
    for k, x in enumerate((-0.085, 0.085)):
        esfera(f"{nome}_c{k}", 0.045, 0.045, 0.02, m, r, (x, -0.03, 0.02), contorno=0.003, seg=20, an=10)
    return r


def mapa3d(nome, loc=(0, 0, 0), s=1.0, pai=None, alfinetes=6, seed=5):
    """mapa do mundo pregado na parede (1,2 x 0,7 m): papel amarelado, continentes em manchas, pouquíssimos alfinetes, longe uns dos outros"""
    import cena
    r = empty(nome, pai, loc); r.scale = (s,) * 3
    O3.caixa(nome + "_papel", (1.2, 0.006, 0.7), O3.M("#cbbf9a", "#a89c78"), r, (0, 0, 0), chanfro=0.0, contorno=0.003)
    cont = [(-0.38, 0.14, 0.13, 0.12), (-0.3, -0.14, 0.07, 0.15), (0.02, 0.15, 0.08, 0.08), (0.05, -0.08, 0.1, 0.16), (0.32, 0.12, 0.22, 0.13),
            (0.42, -0.2, 0.08, 0.06)]
    for k, (cx, cz, rx, rz) in enumerate(cont):
        pts = O3B.blob(cx, cz, rx, rz, z=0.0, seed=seed + k, ruido=0.28)
        me = cena.poly_mesh(f"{nome}_cont{k}", [(x, -0.005, y) for x, y, _ in pts], O3.M("#8e8a6a", "#7a7658"))
        me.parent = r
    rnd = random.Random(seed)
    for k in range(alfinetes):
        cx, cz, rx, rz = rnd.choice(cont)
        p = (cx + rnd.uniform(-rx, rx) * 0.6, -0.02, cz + rnd.uniform(-rz, rz) * 0.6)
        esfera(f"{nome}_alf{k}", 0.012, 0.012, 0.012, O3.M("#ece6d4", "#c8c0aa"), r, p, contorno=0.002, seg=12, an=8)
        tubo(f"{nome}_haste{k}", [p, (p[0], p[1] + 0.02, p[2])], [0.002, 0.002], O3.M("#9a968a"), r, seg=6, tampa=2, contorno=0.0)
    return r


def lanterna3d(nome, loc=(0, 0, 0), s=1.0, pai=None, rot=(0, 0, 0), facho=True, comp=1.6):
    """lanterna de mão que SE LÊ como lanterna (26/10: "parece que é uma lanterna ali, não dá para identificar"): corpo grosso com anéis de pegada,
    faixa amarela, botão vermelho, cabeça em cone com refletor e lente que estoura em brilho, cordão, e o facho em cone com brilho na ponta.
    Olha para -y (a lente); o corpo vai para +y."""
    r = empty(nome, pai, loc); r.scale = (s,) * 3; r.rotation_euler = tuple(math.radians(a) for a in rot)
    metal, metal2 = O3.M("#34393e", "#1e2226", "#8a929a"), O3.M("#4a5057", "#2a2e33", "#9aa2aa")
    O3.cilindro(nome + "_corpo", 0.034, 0.2, metal, r, (0, 0.10, 0), eixo="Y", seg=24)
    for k in range(6):
        O3.anel(nome + "_grip" + str(k), 0.035, 0.004, metal2, r, (0, 0.04 + 0.03 * k, 0), eixo="X")
    O3.cilindro(nome + "_faixa", 0.0355, 0.03, O3.M("#e0b030", "#a07818", "#ffe08a"), r, (0, -0.02, 0), eixo="Y", seg=24)
    O3.cilindro(nome + "_botao", 0.011, 0.016, O3.M("#c0392b", "#7a1f16", "#ff8a7a"), r, (0, 0.0, 0.038), eixo="Z", seg=14)
    O3.cilindro(nome + "_cabeca", 0.056, 0.075, metal, r, (0, -0.075, 0), eixo="Y", r2=0.038, seg=28)
    O3.cilindro(nome + "_refletor", 0.046, 0.012, O3.M("#c8ccd2", "#8a9096", "#ffffff"), r, (0, -0.108, 0), eixo="Y", seg=28, contorno=0.002)
    O3.cilindro(nome + "_vidro", 0.042, 0.008, O3.brilha("#fff6d8", 4.0), r, (0, -0.116, 0), eixo="Y", seg=28, contorno=0.0)
    tubo(nome + "_cordao", [(0.0, 0.2, 0.0), (0.05, 0.24, -0.05), (0.08, 0.2, -0.1), (0.04, 0.16, -0.05)], [0.004] * 4, O3.M("#2a2a2c"), r, seg=6, tampa=2, contorno=0.0)
    if facho:
        O3.cilindro(nome + "_facho", 0.04, comp, O3.vidro("#fff0c8", 0.10, 0.25), r, (0, -0.12 - comp / 2, 0), eixo="Y", r2=0.32 * comp, contorno=0.0, tampa=False)
        O3.halo_cam(nome + "_bloom", (0, -0.13, 0), 0.32, "#fff2c8", 0.7, pai=r)
    return r


def taco3d(nome, loc=(0, 0, 0), s=1.0, pai=None, rot=(0, 0, 0)):
    r = empty(nome, pai, loc); r.scale = (s,) * 3; r.rotation_euler = tuple(math.radians(a) for a in rot)
    tubo(nome + "_t", [(0, 0, 0), (0, 0, 0.3), (0, 0, 0.62), (0, 0, 0.84)], [0.016, 0.02, 0.032, 0.034], O3.M("#9a7a52", "#6e5434"), r, seg=24, tampa=6, contorno=0.003)
    tubo(nome + "_fita", [(0, 0, 0.02), (0, 0, 0.2)], [0.018, 0.018], O3.M("#2e3236"), r, seg=20, tampa=2, contorno=0.002)
    esfera(nome + "_pomo", 0.024, 0.024, 0.012, O3.M("#6e5434"), r, (0, 0, -0.005), contorno=0.002, seg=16, an=8)
    return r


def tambor_fogo3d(nome, loc=(0, 0, 0), pai=None, seed=3):
    """tambor de óleo cortado com fogo dentro: chamas em cones de emissão e um halo laranja"""
    r = empty(nome, pai, loc)
    O3.torno(nome + "_t", [(0.29, 0.0), (0.3, 0.02), (0.3, 0.86), (0.29, 0.88)], O3.M("#5a4636", "#3e3024"), r)
    for k, z in enumerate((0.25, 0.6)):
        O3.anel(f"{nome}_aro{k}", 0.305, 0.01, O3.M("#4a3a2e"), r, (0, 0, z), eixo="Z")
    rnd = random.Random(seed)
    for k in range(7):
        a = rnd.uniform(0, 2 * math.pi); d = rnd.uniform(0, 0.15); h = rnd.uniform(0.18, 0.4)
        cor = ["#ffd27a", "#ff9a3c", "#ffb44e"][k % 3]
        O3.cilindro(f"{nome}_ch{k}", rnd.uniform(0.05, 0.09), h, O3.brilha(cor, 2.6), r, (d * math.cos(a), d * math.sin(a), 0.86 + h / 2), r2=0.004, contorno=0.0, seg=16)
    O3.halo_cam(nome + "_halo", (0, 0, 1.15), 0.9, "#ff9a3c", 0.32, pai=r)
    return r


def escada3d(nome, loc=(0, 0, 0), alt=3.6, pai=None, rot=0.0):
    r = empty(nome, pai, loc); r.rotation_euler.z = math.radians(rot)
    m = O3.M("#7c7a72", "#5a5852")
    for x in (-0.22, 0.22):
        O3.caixa(f"{nome}_trilho{x}", (0.04, 0.05, alt), m, r, (x, 0, alt / 2), chanfro=0.006)
    for k in range(int(alt / 0.3)):
        O3.cilindro(f"{nome}_degrau{k}", 0.014, 0.44, m, r, (0, 0, 0.3 + 0.3 * k), eixo="X")
    return r


def portao3d(nome, loc=(0, 0, 0), W=3.6, H=3.1, pai=None, ferrolho=1.0):
    """portão de aço de enrolar/correr: chapa ondulada (nervuras verticais), trilho em cima, ferrolho grosso na direita (ferrolho 1 = fechado)"""
    r = empty(nome, pai, loc)
    m, m2 = O3.M("#6e6f68", "#4e4f4a"), O3.M("#5a5b55", "#3e3f3a")
    O3.caixa(nome + "_chapa", (W, 0.05, H), m, r, (0, 0, H / 2), chanfro=0.01)
    n = int(W / 0.14)
    for k in range(n):
        O3.caixa(f"{nome}_nerv{k}", (0.05, 0.03, H - 0.06), m2, r, (-W / 2 + 0.07 + k * W / n, -0.035, H / 2), chanfro=0.008, contorno=0.002)
    O3.caixa(nome + "_trilho", (W + 0.3, 0.16, 0.14), O3.M("#3e3f3a"), r, (0, -0.02, H + 0.07), chanfro=0.01)
    # ferrolho: suportes presos na chapa e a barra que corre para a parede
    for k, x in enumerate((W / 2 - 0.42, W / 2 - 0.12)):
        O3.caixa(f"{nome}_sup{k}", (0.07, 0.07, 0.11), O3.M("#3a3632"), r, (x, -0.08, 1.15), chanfro=0.006)
    O3.cilindro(nome + "_barra", 0.022, 0.52, O3.M("#8e8a80", "#5e5a52"), r, (W / 2 - 0.27 + 0.2 * ferrolho, -0.1, 1.15), eixo="X")
    tubo(nome + "_alca", [(W / 2 - 0.3, -0.1, 1.15), (W / 2 - 0.3, -0.12, 1.06)], [0.012, 0.012], O3.M("#8e8a80"), r, seg=10, tampa=4, contorno=0.002)
    return r


def galpao3d(nome="galpao", W=10.0, D=8.0, H=4.2):
    """o galpão do grupo: chão de concreto, paredes de bloco, portão de aço no fundo (+y), janelas altas tapadas com panos,
    parede de teorias a carvão (à esquerda do portão), quadro de giz e mapa. Devolve a raiz; o centro do chão é (0, 0, 0)."""
    r = empty(nome, None, (0, 0, 0))
    import props
    parede = props.FM("#8e8a7e"); chao = props.FM("#66645c")
    O3.caixa(nome + "_chao", (W, D, 0.1), chao, r, (0, 0, -0.05), chanfro=0.0, contorno=0.0)
    O3.caixa(nome + "_fundo", (W, 0.25, H), parede, r, (0, D / 2, H / 2), chanfro=0.0, contorno=0.0)
    for s, x in (("E", -W / 2), ("D", W / 2)):
        O3.caixa(f"{nome}_lado{s}", (0.25, D, H), parede, r, (x, 0, H / 2), chanfro=0.0, contorno=0.0)
        for k in range(3):                                                   # janelas altas tapadas com pano
            y = -D / 2 + 1.6 + k * 2.2
            O3.caixa(f"{nome}_jan{s}{k}", (0.05, 1.2, 0.8), O3.M(["#a89f86", "#6e6a4a", "#8c8d84"][k], None), r, (x - math.copysign(0.13, x), y, H - 0.9), chanfro=0.0, contorno=0.003)
    O3.caixa(nome + "_teto", (W, D, 0.15), props.FM("#2c2d2a"), r, (0, 0, H + 0.075), chanfro=0.0, contorno=0.0)
    for k in range(5):
        O3.caixa(f"{nome}_viga{k}", (W, 0.18, 0.25), O3.M("#3a3b37", "#2a2b28"), r, (0, -D / 2 + 0.8 + k * 1.6, H - 0.12), chanfro=0.0, contorno=0.002)
    # linhas de bloco no fundo
    for k in range(1, int(H / 0.4)):
        O3.caixa(f"{nome}_junta{k}", (W, 0.01, 0.012), O3.M("#86827a"), r, (0, D / 2 - 0.13, 0.4 * k), chanfro=0.0, contorno=0.0)
    portao3d(nome + "_portao", (0.6, D / 2 - 0.14, 0), pai=r)
    # parede de teorias a carvão (esquerda do portão)
    carv = O3.M("#2a2826", "#2a2826", "#2a2826")
    import lib
    for k, (txt, z, sz) in enumerate((("QUEM FEZ OS ABRIGOS SABIA?", 2.95, 0.15), ("A TORRE >", 2.62, 0.12), ("O AR MUDA", 2.36, 0.12))):
        t = lib.text(f"{nome}_tx{k}", txt, sz, carv, r, (-2.5, D / 2 - 0.13, z))
        t.rotation_euler.x = math.radians(90); t.data.font = lib.font()
    for k in range(4):                                                     # setas e riscos a carvão
        x0 = -4.3 + 0.7 * k
        tubo(f"{nome}_seta{k}", [(x0, D / 2 - 0.13, 1.85), (x0 + 0.45, D / 2 - 0.13, 1.75 + 0.1 * (k % 2))], [0.008, 0.008], carv, r, seg=6, tampa=2, contorno=0.0)
    O3B.quadro_giz3d(nome + "_giz", (-3.3, D / 2 - 0.16, 1.35), 0.9, dias=14, pai=r, colunas=4)
    mapa3d(nome + "_mapa", (-1.6, D / 2 - 0.14, 2.1), 0.9, pai=r)
    escada3d(nome + "_escada", (W / 2 - 0.4, 1.2, 0), H, pai=r, rot=90)
    return r


# ---------------------------------------------------------------- a torre
def torre3d(nome, loc=(0, 0, 0), H=60.0, pai=None, acesa=True):
    """torre de rádio de treliça no alto do morro: quatro pernas que afinam, travessas em X e a luz vermelha piscando no topo"""
    r = empty(nome, pai, loc)
    m = O3.M("#2a2d33", "#1c1e22", "#4a4e58")
    b, t = H * 0.09, H * 0.015
    cantos = [(-1, -1), (1, -1), (1, 1), (-1, 1)]
    for k, (sx, sy) in enumerate(cantos):
        tubo(f"{nome}_perna{k}", [(sx * b, sy * b, 0), (sx * t, sy * t, H)], [H * 0.006, H * 0.003], m, r, seg=8, tampa=2, contorno=0.0)
    n = 9
    for i in range(n):
        z0, z1 = H * i / n, H * (i + 1) / n
        w0, w1 = b + (t - b) * i / n, b + (t - b) * (i + 1) / n
        for k in range(4):
            a, c = cantos[k], cantos[(k + 1) % 4]
            tubo(f"{nome}_x{i}{k}", [(a[0] * w0, a[1] * w0, z0), (c[0] * w1, c[1] * w1, z1)], [H * 0.0025] * 2, m, r, seg=6, tampa=2, contorno=0.0)
            tubo(f"{nome}_h{i}{k}", [(a[0] * w1, a[1] * w1, z1), (c[0] * w1, c[1] * w1, z1)], [H * 0.0025] * 2, m, r, seg=6, tampa=2, contorno=0.0)
    if acesa:
        esfera(nome + "_luz", H * 0.018, H * 0.018, H * 0.018, O3.brilha("#ff2a1a", 5.0), r, (0, 0, H + H * 0.02), contorno=0.0, seg=16, an=10)
        O3.halo_cam(nome + "_halo", (0, 0, H + H * 0.02), H * 0.12, "#ff3a22", 0.45, pai=r)
    return r
