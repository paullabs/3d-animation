"""Canal 38: "O abrigo" (nossa versão de um vídeo de bunker; voz do Lucas, 71,7 s). Roteiro: roteiros/abrigo.json; ficha aprovada em 24/10/2026.
Onze cenas, uma por fala, vistas pelos olhos de quem conta (POV: só as mãos aparecem, coladas na câmera). Elenco 2D (traço do canal) dentro
de salas 3D de verdade, e em 3D com volume (heroi3d) nos planos em que a câmera gira, anda atrás ou fica perto do rosto. Paleta apagada
estilo Walking Dead (elenco_abrigo.PAL): o único vermelho vivo é o suéter da Pipoca; a luz é âmbar fraca de lâmpada.
blender -b -P prod_abrigo.py -- CENA OUT [--scale 0.5] [--samples 10] [--at t1,t2] [--list]"""
import os, sys, json, math, random
os.environ["VOZ_NOVA"] = ""
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy, lib
from lib import *
import cena, props, luz, curvas, frente, sets4 as S, unidades as UN, ambiente3d as AM, transicao as TR
import elenco as EL, elenco_abrigo as EA, elenco3d_abrigo as E3, objetos_abrigo as OA, heroi3d as H3
from heroi3d import corrida
import prod_pcc4 as P4
import prod_pcc6 as P6
from prod_pcc4 import F, FPS, finish, Timeline, P, _mix
from char2d import rrect
from puppet2d import circle, stroke, smooth
import vida, rostos
T = lambda f: (f - 1) / FPS
P4.CENAS.clear()
_finish = finish
props.DESAT = 0.55; props.DESAT_TO = "#8a8a78"                              # objetos apagados (a mesma régua da ficha)
props.ACCENT |= {"#8e3a30", "#a8342c", "#8e302b", "#ffe3a0", "#ffd77a", "#fff8dc", "#64211f", "#b65048", "#d9b66a"}


def finish(H, tl, f0, f1, boil=True):
    """todo boneco 2D respira, balança o peso e mexe a cabeça em onda por cima do que a cena animou (nunca fica parado)"""
    vida.vida_ator(tl, f0, f1, seed=sum(map(ord, H.name)))
    _finish(H, tl, f0, f1, boil)


VOZ = (__import__("canal38_env").RAIZ + "/roteiros/voz-abrigo")
PAL = json.load(open(VOZ + "/palavras.json")); TEMPOS = json.load(open(VOZ + "/tempos.json"))
FALAS = [(f["inicio"], f["inicio"] + f["duracao"]) for f in TEMPOS["falas"]]
TOT = TEMPOS["total"]
B = [0.0] + [FALAS[k][0] - 0.12 for k in range(1, len(FALAS))] + [TOT]      # cortes: logo antes de cada fala


def wt(frase, txt, nth=0):
    ws = [w for w in PAL if w["frase"] == frase and w["txt"].strip(".,:;!?…").lower() == txt.lower()]
    return ws[nth]["t0"]


def wt1(frase, txt, nth=0):
    ws = [w for w in PAL if w["frase"] == frase and w["txt"].strip(".,:;!?…").lower() == txt.lower()]
    return ws[nth]["t1"]


def cena_(k):
    return P4.cena_(f"s{k:02d}", B[k - 1], B[k])


V = dict(
    rua=dict(top="#79806f", mid="#aaa896", low="#7a7a6c", chao="#43463f", halo="#e6dfc4", luz="#f0e8cc", pedra="#6d7064", aresta="#cfc9b0", borda="#d9c08a"),
    abrigo=dict(top="#0d1411", mid="#46584c", low="#222e27", chao="#1d261f", halo="#d9b66a", luz="#f2d89c", pedra="#52665a", aresta="#b8a878", borda="#d9c08a"),
    escuro=dict(top="#070b09", mid="#27332b", low="#111a15", chao="#0e130f", halo="#d9b66a", luz="#e8cf94", pedra="#33433a", aresta="#8f8460", borda="#c9ae72"),
    banheiro=dict(top="#0d1411", mid="#5f6e58", low="#2c372b", chao="#242b22", halo="#9fb36a", luz="#d4dc9c", pedra="#6f8060", aresta="#b4bc84", borda="#c9d08a"),
    cinza=dict(top="#4a4c47", mid="#a9a698", low="#7d7b6e", chao="#6d6a5d", halo="#e6e0cc", luz="#f2ecd6", pedra="#8c8977", aresta="#d9d3bc", borda="#d9cfaa"),
    branco=dict(top="#d8d6cc", mid="#f4f1e6", low="#e0ddd0", chao="#c8c5b8", halo="#ffffff", luz="#ffffff", pedra="#e6e3d6", aresta="#ffffff", borda="#fff4d8"),
)


def pal(nome):
    return S.var(P, **V[nome])


def mundo(p):
    bpy.context.scene.world.node_tree.nodes["Background"].inputs[0].default_value = (*lib.srgb(p["top"]), 1)


def halo(nome, x, y, z, r=1.0, cor="#d9b66a", alfa=0.5):
    return cena.disc(nome, r, cena.amat(nome + "_m", cor, 1.0, alfa, ("radial", 1.3)), (x, y, z))


def ator(fn, nome, view, x, y, A, END, espelho=False, escala=1.0, p=None, z=0.0, **kw):
    """um personagem 2D da ficha (elenco_abrigo.py) em cena: rosto vivo e Timeline como o herói; espelho vira o boneco para a esquerda"""
    p = p or P
    H = fn(nome, view, rim=p["borda"], **kw)
    w = empty(nome + "_inv", None, (x, y, z)); H.root.parent = w
    e = escala * EA.ESCALA.get(nome, 1.0)
    w.scale = (-e if espelho else e, e, e)
    tl = Timeline(H, A, END, FPS); tl.stand(A, END, 0.0)
    cena.contact_shadow(H, dict(shadow=_mix(p["chao"], "#000000", 0.4)))
    return H, tl, w


def fim_ator(H, tl, A, END):
    finish(H, tl, A, END)
    if H.view == "front":
        frente.bracos(H, A, END, [(A, dict(shF=5, elF=0, shB=5, elB=0))])


def ator3(chave, nome, x, y, p, escala=None, rot=0.0):
    """o personagem em 3D de verdade (elenco3d_abrigo); o nome termina em _inv (fora do tremido de cena); com sombra no chão"""
    H = E3.faz(chave, nome + "_inv")
    if escala:
        H.raiz.scale = (escala,) * 3
    H.raiz.location = (x, y, 0); H.raiz.rotation_euler.z = math.radians(rot)
    H.sombra = cena.ground_disc(nome + "_sb", 0.42, 0.26, cena.amat(nome + "_sb_m", "#000000", 1.0, 0.38, ("radial", 1.1)), (x, y + 0.05, 0.003), n=32)
    return H


def pipoca3(nome, x, y, escala=1.0, rot=0.0):
    r = E3.pipoca(nome + "_inv", (x, y, 0), escala, rot=rot)
    return r


# ---------------------------------------------------------------- câmeras
def camera_livre(c, nome, t0, t1, p0, p1, alvo0, alvo1=None, lens=28, fstop=5.6, curva="easy", bob=0.0, bob_hz=2.0, roll=0.0):
    """câmera que anda e gira (POV e 3D): desliza de p0 a p1 olhando de alvo0 a alvo1; bob = balanço vertical de quem corre (m), roll = inclinação máxima (graus)"""
    from mathutils import Vector
    sc = c["sc"]
    cd = bpy.data.cameras.new(nome); cam = bpy.data.objects.new(nome, cd); sc.collection.objects.link(cam)
    cd.lens = lens; cd.sensor_fit = "HORIZONTAL"; cd.sensor_width = 24
    cd.dof.use_dof = True; cd.dof.aperture_fstop = fstop
    fa, fb = F(t0), F(t1)
    alvo1 = alvo1 or alvo0
    for f in range(fa - 1, fb + 2):
        u = curvas.s(curva, min(1.0, max(0.0, (f - fa) / max(1, fb - fa))))
        pos = Vector(tuple(a + (b - a) * u for a, b in zip(p0, p1)))
        al = Vector(tuple(a + (b - a) * u for a, b in zip(alvo0, alvo1)))
        if bob:
            ph = 2 * math.pi * bob_hz * (f - fa) / FPS
            pos.z += bob * abs(math.sin(ph / 2 * 2)) * 1.0 - bob * 0.5
            al.x += 0.0
        cam.location = pos
        e = (al - pos).to_track_quat("-Z", "Y").to_euler()
        if roll:
            e.y += math.radians(roll) * math.sin(2 * math.pi * bob_hz * (f - fa) / FPS / 2)
        cam.rotation_euler = e
        key(cam, "location", f, "LINEAR"); key(cam, "rotation_euler", f, "LINEAR")
        cd.dof.focus_distance = max(0.3, (al - pos).length); cd.dof.keyframe_insert("focus_distance", frame=f)
    m = sc.timeline_markers.new(nome, frame=fa); m.camera = cam
    return cam


def maos(cam, nome, escala=0.55, d=0.5, y=-0.30, guidao=False):
    """as mãos de quem conta, coladas na câmera (POV): elas entram na tela por baixo; guidao = o guidão da bicicleta atrás delas. Devolve (raiz, esq, dir)"""
    r = OA.maos_pov(nome + "_inv", (0, 0, 0), escala, parent=cam)
    r.location = (0, y, -d); r.rotation_euler = (math.radians(-90), 0, 0)
    g = None
    if guidao:
        g = OA.guidao_pov(nome + "_guid_inv", (0, 0.02, 0.17), 1.0, parent=r)
        troca_mao(nome, "esq", F(-1.0), "fechada"); troca_mao(nome, "dir", F(-1.0), "fechada")
    return r, bpy.data.objects[nome + "_inv_esq"], bpy.data.objects[nome + "_inv_dir"], g


def troca_mao(nome, lado, f, para):
    """a mão do lado (esq/dir) vira 'aberta' ou 'fechada' no quadro f (troca por escala, sem transição)"""
    for v in ("aberta", "fechada"):
        o = bpy.data.objects[f"{nome}_inv_{lado}_{v}"]
        o.scale = (1, 1, 1) if v == para else (0.0001,) * 3
        key(o, "scale", f, "CONSTANT")


def camera_planos(c, lista, entra="h", sai="h"):
    """lista de câmeras já criadas (marcadores por plano); aplica a rampa de entrada e de saída (corte invisível) nas pontas"""
    k = 0.32
    if entra:
        cam, t0, d = lista[0]
        TR.rampa_inicio(cam, F(t0), P6.DIRS[entra], k * d, 4)
    if sai:
        cam, t1, d = lista[-1]
        TR.rampa_fim(cam, F(t1), P6.DIRS[sai], k * d, 4)


# ---------------------------------------------------------------- cenário comum
def fachada(nome, x, y0, y1, h, cor, lado, seed=1, acesas=0.0, janela="#1d201c", acesa="#d9b66a"):
    """parede lateral de prédio (plano YZ em x), vista de dentro da rua: janelas em grade, porta no térreo e uma beirada mais escura em cima.
    lado = +1 (prédio à direita da rua, a face olha para -x) ou -1 (à esquerda)"""
    rnd = random.Random(seed)
    q = lambda nm, ya, yb, za, zb, col, dx=0.0: cena.poly_mesh(nm, [(x + dx, ya, za), (x + dx, yb, za), (x + dx, yb, zb), (x + dx, ya, zb)], props.FM(col))
    q(nome, y0, y1, 0.0, h, cor)
    q(nome + "_topo", y0, y1, h - 0.35, h, _mix(cor, "#000000", 0.3), -0.01 * lado)
    q(nome + "_rodape", y0, y1, 0.0, 0.5, _mix(cor, "#000000", 0.22), -0.01 * lado)
    n = max(1, int((y1 - y0) / 2.2))
    for i in range(n):
        yc = y0 + (i + 0.5) * (y1 - y0) / n
        for j, z in enumerate([1.2 + 1.45 * k for k in range(int((h - 1.5) / 1.45))]):
            col = acesa if rnd.random() < acesas else janela
            q(f"{nome}_j{i}_{j}", yc - 0.45, yc + 0.45, z, z + 0.95, col, -0.012 * lado)
            q(f"{nome}_p{i}_{j}", yc - 0.5, yc + 0.5, z - 0.05, z, _mix(cor, "#000000", 0.35), -0.013 * lado)
        if i % 2 == 0:
            q(f"{nome}_porta{i}", yc - 0.5, yc + 0.5, 0.0, 2.1, _mix(cor, "#000000", 0.5), -0.012 * lado)


def rua(p, y0, y1, larg=3.2, seed=3, acesas=0.0):
    """rua de bairro: asfalto com faixa tracejada, calçadas, prédios dos dois lados (alturas e tons diferentes), vãos entre eles e postes"""
    rnd = random.Random(seed)
    cena.poly_mesh("asfalto", [(-larg, y0, 0), (larg, y0, 0), (larg, y1, 0), (-larg, y1, 0)], props.FM(p["chao"]))
    for s in (-1, 1):
        cena.poly_mesh(f"calcada{s}", [(s * larg, y0, 0.002), (s * (larg + 1.3), y0, 0.002), (s * (larg + 1.3), y1, 0.002), (s * larg, y0, 0.002 + 0.0)], props.FM(_mix(p["chao"], p["pedra"], 0.45)))
        cena.poly_mesh(f"meiofio{s}", [(s * larg - 0.06, y0, 0.003), (s * larg + 0.06, y0, 0.003), (s * larg + 0.06, y1, 0.003), (s * larg - 0.06, y1, 0.003)], props.FM(p["aresta"]))
    y = y0
    while y < y1:
        cena.poly_mesh(f"faixa_{int(y * 10)}", [(-0.05, y, 0.003), (0.05, y, 0.003), (0.05, y + 1.1, 0.003), (-0.05, y + 1.1, 0.003)], props.FM(_mix(p["aresta"], p["chao"], 0.35)))
        y += 2.6
    tons = ["#6f6c5e", "#7d7a68", "#5f6657", "#827a66", "#6a6f6a", "#756a58"]
    for s in (-1, 1):
        y = y0
        k = 0
        while y < y1:
            comp = rnd.choice((5.0, 6.5, 8.0)); alt = rnd.choice((4.2, 5.4, 6.8, 8.2))
            fachada(f"fach{s}_{k}", s * (larg + 1.3), y, y + comp, alt, rnd.choice(tons), s, seed=seed + k * 7 + s, acesas=acesas)
            y += comp + rnd.choice((0.0, 0.0, 2.2)); k += 1
    for s in (-1, 1):
        y = y0 + 3.0
        while y < y1:
            props.inked(f"poste{s}_{int(y)}", rrect(s * (larg + 0.5) - 0.05, 0.0, s * (larg + 0.5) + 0.05, 4.4, 0.01, 2), "#4f4f46", None, w=0.01, shade=0.02, shade_color="#35352e")
            ob = bpy.data.objects[f"poste{s}_{int(y)}"]; ob.location = (0, y, 0)
            y += 8.0


def ceu(p, y, topo="#5a6058", meio="#aaa896"):
    props.skywall("ceu", y, [(-2.0, meio), (6.0, _mix(meio, topo, 0.4)), (14.0, topo), (120.0, topo)], -160, 160, -2.0, 120.0)


def morro_abrigo(p, y, s=1.0):
    """o abrigo no fim da rua: morro de terra, a porta redonda de cofre com a luz amarela por dentro e um vão escuro em volta"""
    cena.poly_mesh("morro", [(-14 * s, y + 0.5, 0), (-9 * s, y + 0.5, 2.0 * s), (-4 * s, y + 0.5, 3.6 * s), (0, y + 0.5, 4.2 * s), (5 * s, y + 0.5, 3.4 * s), (10 * s, y + 0.5, 1.8 * s), (15 * s, y + 0.5, 0)], props.FM("#3b4235"))
    cena.poly_mesh("morro_sombra", [(-6 * s, y + 0.4, 0), (-3 * s, y + 0.4, 2.8 * s), (0, y + 0.4, 3.3 * s), (3.5 * s, y + 0.4, 2.7 * s), (7 * s, y + 0.4, 0)], props.FM("#2f352a"))
    halo("morro_gl", 0.0, y, 1.3 * s, 3.2 * s, "#d9b66a", 0.55)
    OA.porta_abrigo("porta_morro", (0, y - 0.1, 0), 1.0 * s, aberta=0.4, luz_fora="#e8c470")


# ====================================================================== 1. A corrida (fala 1)
@cena_(1)
def s01(c):
    """POV na bicicleta, rua de bairro cinza e o abrigo no fim; larga a bicicleta e corre atrás do Zé e da Lu (em 3D, correndo) -> câmera baixa de lado, seguindo os dois
    -> POV de novo, a porta cada vez maior e o céu estoura em branco"""
    A, END = F(-0.4), F(B[1] + 0.4)
    p = pal("rua"); mundo(p)
    yf = 46.0
    ceu(p, yf + 6, topo="#7f857b", meio="#b6b4a2")
    rua(p, -8.0, yf, acesas=0.04)
    for yv in (14.0, 28.0, 40.0):
        S.neblina(p, yv, 0.10, z1=40.0)
    morro_abrigo(p, yf)
    t_l, t_c, t_b = wt(1, "larguei"), wt(1, "corri"), wt(1, "branco")
    # os dois, em 3D, correndo até a porta
    ze = ator3("ze", "ze", -0.7, 4.5, p, rot=180); lu = ator3("lu", "lu", 0.8, 2.2, p, rot=180)
    for H, (x0, y0), (x1, y1), pad in ((ze, (-0.7, 4.5), (-0.3, 42.0), 0.0), (lu, (0.8, 2.2), (0.3, 40.2), 0.0)):
        ch = corrida(F(0.2), F(B[1] - 0.2), (x0, y0, 0), (x1, y1, 0), rot=180, ciclo=12, inclina=10, arranque=0.12, freia=0.1)
        ch = [(A, dict(ch[0][1]))] + ch
        H.anima(ch, A, END, vida=0.3)
        H.rosto(boca="reta", lid=0.4)
    ze.expressao([(A, dict(lid=0.4))], A, END, seed=1); lu.expressao([(A, dict(lid=0.35, brow=-0.3))], A, END, seed=2)
    # câmeras: POV na bicicleta -> lateral baixa -> POV correndo
    y_pov0, y_pov1 = -4.0, 8.0
    c1 = camera_livre(c, "pov1", B[0], t_c, (0.0, y_pov0, 1.12), (0.0, y_pov0 + 4.6 * t_c, 1.12), (0.0, 30.0, 1.5), (0.0, 34.0, 1.5), lens=24, bob=0.015, bob_hz=2.2)
    r, mE, mD, g = maos(c1, "maos1", guidao=True)
    # larga a bicicleta: as duas mãos abrem e o guidão cai para trás
    fl = F(t_l)
    troca_mao("maos1", "esq", fl, "aberta"); troca_mao("maos1", "dir", fl + 1, "aberta")
    for o, bx, dx in ((mE, -0.2, -0.05), (mD, 0.2, 0.05)):
        o.location = (bx, 0, 0); key(o, "location", fl - 2, "BEZIER")
        o.location = (bx + dx, 0.0, 0.18); key(o, "location", fl + 5, "BEZIER")
        o.location = (bx + dx * 0.6, 0.0, 0.05); key(o, "location", fl + 18, "BEZIER")
    g.location = (0, 0.02, 0.17); key(g, "location", fl - 2, "BEZIER"); g.location = (0, 0.02, -0.45); key(g, "location", fl + 8, "BEZIER")
    g.rotation_euler = (0, 0, 0); key(g, "rotation_euler", fl - 2, "BEZIER"); g.rotation_euler = (0, math.radians(25), 0); key(g, "rotation_euler", fl + 8, "BEZIER")
    def yz(t):                                                       # onde o Zé está no tempo t (mesma conta da corrida: arranque 12%, freada 10%)
        u = min(1.0, max(0.0, (t - 0.2) / (B[1] - 0.4))); a_, b_ = 0.12, 0.1; V_ = 1.0 / (1.0 - a_ / 2 - b_ / 2)
        w_ = u - (1 - b_)
        d = V_ * u * u / (2 * a_) if u < a_ else V_ * (a_ / 2 + u - a_) if u <= 1 - b_ else V_ * (a_ / 2 + (1 - b_ - a_) + w_ - w_ * w_ / (2 * b_))
        return 4.5 + (42.0 - 4.5) * d
    c2 = camera_livre(c, "lat1", t_c, t_b - 0.35, (2.3, yz(t_c) - 3.2, 0.62), (2.0, yz(t_b - 0.35) - 3.0, 0.8), (-0.6, yz(t_c) + 2.0, 1.0), (-0.4, yz(t_b - 0.35) + 2.5, 1.2), lens=18, fstop=6.0, bob=0.0)
    c3 = camera_livre(c, "pov3", t_b - 0.35, B[1], (0.0, 24.0, 1.55), (0.0, 38.0, 1.6), (0.0, 44.0, 1.5), (0.0, 46.0, 1.4), lens=24, bob=0.035, bob_hz=3.6, roll=1.2)
    r3, mE3, mD3, _ = maos(c3, "maos3")
    troca_mao("maos3", "esq", F(t_b - 0.35), "fechada"); troca_mao("maos3", "dir", F(t_b - 0.35), "fechada")
    for o, bx in ((mE3, -0.2), (mD3, 0.2)):                         # correndo: as mãos fechadas balançam
        for f in range(F(t_b - 0.35), F(B[1]) + 1, 3):
            ph = 2 * math.pi * 1.8 * (f - F(t_b)) / FPS
            o.location = (bx * 0.8, 0.0, 0.05 + 0.04 * math.sin(ph if bx < 0 else ph + math.pi)); key(o, "location", f, "LINEAR")
    # o céu estoura
    flash = cena.quad("flash", -1, 1, -1, 1, cena.amat("flash_m", "#fffaf0", 1.6, 1.0), 0.0, norm=False)
    flash.parent = c3; flash.location = (0, 0, -0.3); flash.rotation_euler = (math.radians(90), 0, 0); flash.scale = (0.6, 0.6, 1.0)
    # (o plano é um quadrado de 0,6 m a 0,3 m da câmera: cobre o quadro 9:16)
    flash.scale = (0.9, 1.0, 1.8)
    mat = flash.data.materials[0]
    mul = [n for n in mat.node_tree.nodes if n.type == "MATH" and n.operation == "MULTIPLY"][0].inputs[1]
    tb = F(t_b)
    for f_, a_ in ((tb - 3, 0.0), (tb + 3, 0.85), (F(B[1]) + 1, 1.0)):
        mul.default_value = a_; mul.keyframe_insert("default_value", frame=f_)
    camera_planos(c, [(c1, B[0], 3.0)], entra="h", sai=None)
    camera_planos(c, [(c3, B[1], 3.0)], entra=None, sai="h")


# ---------------------------------------------------------------- o abrigo por dentro
SALA = dict(parede="#4a5c50", lateral="#364539", teto="#161e19", viga="#1f2a23", chao="#252d27", linha="#1c231e", pilastra="#55685a")


def sala_abrigo(p, wy=5.5, x0=-3.6, x1=3.6, h=2.9, y0=-10.0, pilastra=2.2, fundo=True):
    """o abrigo: sala de concreto verde-musgo, teto baixo com vigas, piso de lajotas; escurece em direção à câmera (vinheta no chão)"""
    mundo(p)
    AM.sala("sala", x0, x1, y0, wy, h, SALA, piso="lajotas", passo_pilastra=pilastra, passo_viga=1.8, fundo=fundo)
    cena.ground_disc("vinheta", 7.0, 6.0, cena.amat("vinheta_m", "#000000", 1.0, 0.5, ("radial", 0.8)), (0.0, -2.0, 0.006), n=48)


def lampadas(wy_lamp, ligadas, x=0.0, z_teto=2.9, s=1.7, nome="lamp", END=300):
    """as três lâmpadas do fio (as primeiras 'ligadas' acesas), com o brilho âmbar em volta de cada uma e a poça de luz no chão"""
    z0 = z_teto - 0.5 * s
    OA.lampadas(nome, (x, wy_lamp, z0), s, ligadas=ligadas)
    for k in range(ligadas):
        bx = x + (-0.4, 0.0, 0.4)[k] * s
        halo(f"{nome}_hl{k}", bx, wy_lamp + 0.05, z0 + 0.29 * s, 1.5, "#d9b66a", 0.34)
        cena.ground_disc(f"{nome}_pool{k}", 1.6, 1.1, cena.amat(f"{nome}_pool{k}_m", "#d9b66a", 1.0, 0.22, ("radial", 1.2)), (bx, wy_lamp - 0.5, 0.004), n=40)


def mostra_so(objs, janelas):
    """objs[i] só aparece nos quadros de janelas[i] = (f0, f1) (troca por escala, sem transição; guarda a escala original de cada objeto)"""
    for o, (f0, f1) in zip(objs, janelas):
        s0 = tuple(o.scale)
        o.scale = (0.0001,) * 3; key(o, "scale", f0 - 1, "CONSTANT")
        o.scale = s0; key(o, "scale", f0, "CONSTANT")
        if f1 is not None:
            o.scale = (0.0001,) * 3; key(o, "scale", f1, "CONSTANT")


# ====================================================================== 2. A porta (fala 2)
@cena_(2)
def s02(c):
    """o abrigo por dentro, perto da porta: o Zé entra por último em 3D contra a luz branca, vira, fecha a folha e gira a roda -> perto da janelinha: rostos e mãos batem no vidro, a
    porta treme e o BANG! estala -> o rosto do Zé, duro, olhando para quem conta: ele não abriu"""
    A, END = F(B[1] - 0.4), F(B[2] + 0.4)
    p = pal("abrigo"); wy = 4.6
    sala_abrigo(p, wy=wy, x0=-2.7, x1=2.7, pilastra=0)
    s_p = 1.15
    porta = OA.porta_abrigo("porta", (0, wy - 0.08, 0), s_p, aberta=1.0, luz_fora="#f4f1e6")
    folha = bpy.data.objects["porta_folha"]; roda = bpy.data.objects["porta_roda"]
    halo("porta_gl", 0.0, wy - 0.1, 1.2, 2.2, "#f4f1e6", 0.5)
    luz.feixe("feixe_porta", 0.0, wy - 0.5, 0.0, 2.6, 1.8, 0.9, "#f4f1e6", forca=0.9, frames=END, poeira=26, seed=12)
    lampadas(wy - 0.3, 1, x=-1.3, s=1.2, nome="lampA")
    # fechar a folha: corre da direita (aberta) até o vão
    t_f = wt(2, "trancou"); fa = F(t_f - 0.5)
    folha.location = (1.15 * s_p, 0, 0); key(folha, "location", fa - 1, "BEZIER")
    folha.location = (0.0, 0, 0); key(folha, "location", fa + 9, "BEZIER")
    for o in [o for o in bpy.data.objects if o.name.startswith(("feixe_porta", "porta_gl"))]:       # a luz de fora some quando a folha fecha
        o.scale = (1, 1, 1) if o.scale.x else o.scale; key(o, "scale", fa + 4, "CONSTANT")
        o.scale = (0.0001,) * 3; key(o, "scale", fa + 10, "CONSTANT")
    # a roda gira (trancando), e treme a cada batida
    t_p = wt(2, "porta"); fr = F(t_p - 0.2)
    roda.rotation_euler = (0, 0, 0); key(roda, "rotation_euler", fr, "BEZIER")
    roda.rotation_euler = (0, math.radians(-150), 0); key(roda, "rotation_euler", fr + 14, "BEZIER")
    # os rostos e as mãos na janelinha (só depois de fechada)
    rj = OA.rostos_janela("jan", folha, z=1.8)
    rj = [bpy.data.objects[n] for n in ("jan_rosto0", "jan_rosto1", "jan_mao0", "jan_mao1")]
    batidas = [wt(2, "povo"), wt(2, "batia"), wt(2, "gritava"), wt(2, "pedindo"), wt(2, "entrar", 1)]
    batidas.sort()
    t_b0 = wt(2, "povo")
    for o in rj:
        o.scale = (0.0001,) * 3; key(o, "scale", F(t_b0) - 2, "CONSTANT"); o.scale = (1, 1, 1); key(o, "scale", F(t_b0) - 1, "CONSTANT")
        o.scale = (1, 1, 1)
    for i, tb in enumerate(batidas):
        fb = F(tb)
        for o in rj:
            o.scale = (1, 1, 1); key(o, "scale", fb - 1, "BEZIER"); o.scale = (1.35, 1.35, 1.35); key(o, "scale", fb + 1, "BEZIER"); o.scale = (1, 1, 1); key(o, "scale", fb + 6, "BEZIER")
        folha.location = (0.0, 0, 0); key(folha, "location", fb - 1, "BEZIER")
        folha.location = (0.012 * (1 if i % 2 else -1), 0, 0); key(folha, "location", fb + 1, "BEZIER")
        folha.location = (0.0, 0, 0); key(folha, "location", fb + 5, "BEZIER")
        bang = lib.text(f"bang{i}", "BANG!", 0.2 + 0.03 * (i % 2), props.FM("#e8e0c4"), None, (-0.32 + 0.3 * (i % 3), wy - 0.3, 1.2 + 0.35 * (i % 2)), lib.font(), extrude=0.0, outline=0.01)
        bang.rotation_euler = (math.pi / 2, 0, math.radians(-9 + 7 * i))
        UN.esconde_ate(bang, fb); UN.some(bang, fb + 9, 3)
    # o Zé em 3D
    ze = ator3("ze", "ze", 0.1, wy - 0.45, p, rot=0)
    f_in, f_t, f_p = F(7.9), F(wt(2, "entrar")), F(t_f - 0.9)
    ch = [(A, dict(pos=(0.15, wy - 0.45, 0), rot=0, ombro=(-4, 6), cotovelo=(-10, -10))),
          (F(7.25), dict(pos=(0.15, wy - 0.6, 0), rot=0, ombro=(20, -25), cotovelo=(-20, -20), abre=(8, 8), tronco=-6, quadril=(-10, 10))),
          (f_in, dict(pos=(-0.3, wy - 1.75, 0), rot=0, ombro=(-8, 8), cotovelo=(-14, -12), tronco=-3)),
          (f_t, dict(pos=(-0.35, wy - 1.7, 0), rot=140, ombro=(-6, 8), cotovelo=(-14, -12))),
          (f_p, dict(pos=(-0.2, wy - 0.9, 0), rot=180, ombro=(-20, -20), cotovelo=(-14, -14))),
          (fa + 8, dict(pos=(-0.05, wy - 0.5, 0), rot=180, ombro=(-70, -62), cotovelo=(-26, -34), abre=(6, 6), tronco=-4)),
          (fr + 14, dict(pos=(-0.05, wy - 0.5, 0), rot=180, ombro=(-62, -58), cotovelo=(-20, -30), tronco=-6)),
          (F(wt(2, "Do") + 0.2), dict(pos=(0.0, wy - 0.9, 0), rot=180, ombro=(-14, -14), cotovelo=(-12, -12))),
          (F(12.3), dict(pos=(0.1, wy - 1.9, 0), rot=190, ombro=(-6, 8), cotovelo=(-14, -12))),
          (F(wt(2, "Ele") + 0.05), dict(pos=(0.2, wy - 2.1, 0), rot=0, ombro=(-4, 6), cotovelo=(-12, -12), cabeca=0)),
          (END, dict(pos=(0.2, wy - 2.1, 0), rot=0, ombro=(-4, 6), cotovelo=(-12, -12), cabeca=0))]
    ze.anima(ch, A, END, vida=0.4)
    ze.expressao([(A, dict(lid=0.2, brow=0.3)), (F(8.9), dict(lid=0.5, brow=-0.5)), (F(wt(2, "Ele")), dict(lid=0.55, brow=-0.6)), (F(wt(2, "abriu")) - 4, dict(lid=0.7, brow=-0.4)), (END, dict(lid=0.6))], A, END, seed=3)
    # a Lu e a Rita, de 3/4, olhando para a porta
    H1, tl1, w1 = ator(EA.rita, "rita", "q", -2.0, 2.9, A, END, p=p)
    H2, tl2, w2 = ator(EA.lu, "lu", "q", -1.35, 2.2, A, END, p=p)
    tl1.face(A, 0.0, lid="esperto", lidv=0.35, browup=0.02, mouth="reta", look=(1.0, 0.1)); tl2.face(A, 0.0, lid="esperto", lidv=0.4, brow=-8, mouth="reta", look=(1.0, 0.0))
    tl2.face(F(wt(2, "povo")), 1.0, wide=0.3, browup=0.015, mouth="pequena", look=(1.0, 0.1))
    fim_ator(H1, tl1, A, END); fim_ator(H2, tl2, A, END)
    # câmeras: aberta de lado -> janelinha -> rosto do Zé
    t1, t2 = wt(2, "povo") - 0.35, wt(2, "Ele") - 0.2
    c1 = camera_livre(c, "pl0", B[1], t1, (-0.9, -2.2, 1.5), (-0.5, -0.4, 1.5), (0.25, wy, 1.1), (0.1, wy, 1.2), lens=24, fstop=5.0)
    c2 = camera_livre(c, "pl1", t1, t2, (0.12, wy - 1.35, 2.0), (0.05, wy - 1.0, 2.04), (0.0, wy, 2.05), (0.0, wy, 2.07), lens=35, fstop=5.0)
    c3 = camera_livre(c, "pl2", t2, B[2], (0.45, wy - 4.1, 1.55), (0.3, wy - 3.5, 1.6), (0.2, wy - 2.1, 1.6), (0.2, wy - 2.1, 1.6), lens=38, fstop=3.2)
    camera_planos(c, [(c1, B[1], 3.0)], entra="h", sai=None); camera_planos(c, [(c3, B[2], 2.0)], entra=None, sai="h")


# ====================================================================== 3. Dentro do abrigo, dia 1 (fala 3)
def mesa_cena(p, x=-0.3, y=2.9, w=2.4):
    S.caixa3d(p, "mesa", x, y, w, 0.78, d=1.0, cor="#3a342a", tampo="#6b5a3e", aresta="#8a7650")


def abrigo_cheio(p, wy, END, dia=1, lamp=3, nivel=1.0, galao=1.0, estante=True):
    """o abrigo no dia 1: estante de latas à esquerda, calendário de giz, galões, a porta no canto, as lâmpadas e a mesa"""
    sala_abrigo(p, wy=wy)
    est = OA.prateleira("est", (-2.45, wy - 0.15, 0.0), 1.9, nivel=nivel) if estante else None
    OA.quadro_giz("giz", (-0.4, wy - 0.12, 1.45), 1.7, dias=dia, rotulo=f"DIA {dia}")
    OA.galao("galao_a", (1.55, wy - 0.4, 0.0), 1.7, nivel=galao); OA.galao("galao_b", (1.95, wy - 0.4, 0.0), 1.7, nivel=galao)
    OA.porta_abrigo("porta", (3.05, wy - 0.1, 0), 0.95, aberta=0.0)
    lampadas(wy - 1.6, lamp, x=-0.3, nome="lamp")
    mesa_cena(p)
    return est


@cena_(3)
def s03(c):
    """o abrigo no dia 1: a estante cheia de latas -> os galões azuis -> as três lâmpadas acendem em sequência -> a mesa, os três rindo e a Pipoca cheirando o prato"""
    A, END = F(B[2] - 0.4), F(B[3] + 0.4)
    p = pal("abrigo"); wy = 5.5
    abrigo_cheio(p, wy, END, dia=1, lamp=3)
    # a mesa: pratos, a Pipoca e os três atrás
    for k, x in enumerate((-1.0, -0.1, 0.75)):
        OA.mesa_prato(f"pr{k}", (x, 3.1, 0.78), 1.3, None, nivel="cheio")
    pip = OA.porquinha("pipoca", (0.3, 3.35, 0.78), 1.0, vista="lado"); pip.rotation_euler = (0, 0, 0)
    for f in range(A, END, 3):
        pip.rotation_euler = (0, math.radians(2.4 * math.sin(2 * math.pi * 2.2 * (f - A) / FPS)), 0); key(pip, "rotation_euler", f, "LINEAR")
    Hz, tz, wz = ator(EA.ze, "ze", "front", -1.0, 3.75, A, END, p=p, z=-0.3)
    Hl, tl_, wl = ator(EA.lu, "lu", "front", -0.1, 3.75, A, END, p=p, z=-0.3)
    Hr, tr, wr = ator(EA.rita, "rita", "front", 0.75, 3.75, A, END, p=p, z=-0.3)
    t_s = wt(3, "seguro")
    for H, tl, seed in ((Hz, tz, 0), (Hl, tl_, 1), (Hr, tr, 2)):
        tl.face(A, 0.0, lid="esperto", lidv=0.3, mouth="pequena", look=(0.0, 0.0))
        tl.face(F(wt(3, "gente")), 1.0, eye="feliz", mouth="sorriso", browup=0.012, look=(0.0, 0.0))
        tl.intent(F(wt(3, "gente")) + seed * 4, head=4 - 3 * seed, torso=2)
        fim_ator(H, tl, A, END)
    # as lâmpadas piscam e acendem em sequência na palavra "luz"
    t_luz = wt(3, "luz")
    for k in range(3):
        for nm in (f"lamp_hl{k}", f"lamp_pool{k}"):
            o = bpy.data.objects[nm]
            o.scale = (0.0001,) * 3; key(o, "scale", F(t_luz) - 2, "CONSTANT")
    t1, t2, t3, t4 = wt(3, "água") - 0.15, wt(3, "luz") - 0.1, wt(3, "Por") - 0.05, wt(3, "gente") + 0.1
    P6.planos(c, [
        dict(t0=B[2], t1=t1, caixa0=(-3.5, -1.4, 0.0, 2.1, wy - 0.3), caixa1=(-3.4, -1.5, 0.05, 2.0, wy - 0.3), lens=34, fstop=3.0, preenche=0.9, alt0=1.1, alt1=1.15),
        dict(t0=t1, t1=t2, caixa0=(1.0, 2.8, 0.0, 1.5, wy - 0.4), caixa1=(1.1, 2.7, 0.05, 1.4, wy - 0.4), lens=36, fstop=2.8, preenche=0.9, alt0=1.0, alt1=1.0),
        dict(t0=t2, t1=t3, caixa0=(-1.6, 1.0, 1.8, 2.9, wy - 1.6), caixa1=(-1.4, 0.8, 1.9, 2.9, wy - 1.6), lens=30, fstop=3.5, preenche=0.9, alt0=0.9, alt1=1.2),
        dict(t0=t3, t1=t4, caixa0=(-1.45, 0.2, 0.55, 1.75, 3.0), caixa1=(-1.3, 0.3, 0.6, 1.75, 3.0), lens=45, fstop=2.2, preenche=0.92, alt0=1.15, alt1=1.15),
        dict(t0=t4, t1=B[3], caixa0=(-0.35, 1.15, 0.5, 1.5, 3.0), caixa1=(0.05, 0.85, 0.7, 1.15, 3.0), lens=50, fstop=2.0, preenche=0.92, alt0=1.0, alt1=0.95, chaves=["pipoca"]),
    ], entra="h", sai="h")


# ====================================================================== 4. A comida acaba, dia 21 (fala 4)
def giz_estados(wy, dias, janelas, x=-0.4, z=1.45, s=1.7, rotulo=None):
    """o calendário de giz em vários estados no mesmo lugar (cada um só aparece na sua janela de quadros)"""
    objs = [OA.quadro_giz(f"giz{k}", (x, wy - 0.12, z), s, dias=d, rotulo=rotulo or f"DIA {d}") for k, d in enumerate(dias)]
    mostra_so(objs, janelas)
    return objs


@cena_(4)
def s04(c):
    """a estante esvazia em três tempos (cheia, pela metade, quase vazia) com o Zé riscando num caderno -> o prato do POV: cheio, metade, só uma colher
    -> os riscos de giz multiplicam e a Lu divide uma lata com a ponta da faca -> a estante quase vazia e os três olhando"""
    A, END = F(B[3] - 0.4), F(B[4] + 0.4)
    p = pal("abrigo"); wy = 5.5
    sala_abrigo(p, wy=wy)
    t_a, t_c, t_d, t_j, t_t = wt(4, "acabando"), wt(4, "comia"), wt(4, "dia"), wt(4, "já"), wt(4, "todo")
    ests = [OA.prateleira(f"est{k}", (-2.45, wy - 0.15, 0.0), 1.9, nivel=n) for k, n in enumerate((1.0, 0.5, 0.15))]
    mostra_so(ests, [(A, F(t_c)), (F(t_c), F(t_t) - 6), (F(t_t) - 6, None)])
    giz_estados(wy, (14, 18, 21), [(A, F(t_c)), (F(t_c), F(t_d)), (F(t_d), None)])
    OA.galao("galao_a", (1.55, wy - 0.4, 0.0), 1.7, nivel=0.8); OA.galao("galao_b", (1.95, wy - 0.4, 0.0), 1.7, nivel=0.7)
    OA.porta_abrigo("porta", (3.05, wy - 0.1, 0), 0.95, aberta=0.0)
    lampadas(wy - 1.6, 3, x=-0.3, nome="lamp")
    mesa_cena(p)
    # o prato do POV, de frente, ao lado: cheio, metade, vazio com colher
    t_p, t_cd, t_ja = wt(4, "pouco"), wt(4, "cada"), wt(4, "já")
    pratos = [OA.prato(f"prato_pov{k}", (-0.2, 2.2, 0.95), 4.4, nivel=n) for k, n in enumerate(("cheio", "metade", "vazio"))]
    mostra_so(pratos, [(F(t_c) - 8, F(t_p)), (F(t_p), F(t_cd)), (F(t_cd), F(t_ja))])
    fundo_p = cena.quad("fundo_prato", -2.2, 2.2, -0.5, 3.5, cena.amat("fundo_prato_m", "#070a08", 1.0, 0.86), 2.5, norm=False)
    mostra_so([fundo_p], [(F(t_c) - 8, F(t_ja))])
    # o Zé com o caderno, riscando, e a Lu com a lata e a faca
    Hz, tz, wz = ator(EA.ze, "ze", "q", -1.15, 4.6, A, END, p=p, espelho=True)
    cad = OA.caderno("caderno", (-1.5, 4.35, 1.05), 1.0); cad.rotation_euler = (0, math.radians(8), 0)
    Hl, tl_, wl = ator(EA.lu, "lu", "front", 0.05, 3.75, A, END, p=p, z=-0.3)
    OA.lata_aberta("lata_ab", (-0.35, 3.15, 0.78), 1.0); OA.faca("faca", (0.15, 3.1, 0.82), 1.0)
    for H, tl, seed in ((Hz, tz, 0), (Hl, tl_, 1)):
        tl.face(A, 0.0, lid="esperto", lidv=0.4, brow=-8, mouth="reta", look=(-1.0, 0.0) if seed == 0 else (0.0, 0.5))
    for k in range(8):                                                       # o Zé risca o caderno de tempos em tempos
        f = A + 8 + 18 * k
        tz.intent(f, shF=18, elF=60); tz.intent(f + 5, shF=26, elF=44); tz.intent(f + 10, shF=14, elF=62)
    for k in range(7):                                                       # a Lu corta com a faca (vai e vem do braço)
        f = F(t_d) + 6 * k
        tl_.intent(f, shF=26, elF=50); tl_.intent(f + 3, shF=10, elF=40)
    tz.face(F(t_t), 1.0, lid="esperto", lidv=0.55, browup=0.015, mouth="reta", look=(-1.0, 0.0))
    fim_ator(Hz, tz, A, END); fim_ator(Hl, tl_, A, END)
    t1, t2, t3 = t_c - 0.4, t_ja - 0.05, t_t - 0.2
    cams = P6.planos(c, [
        dict(t0=B[3], t1=t1, caixa0=(-3.4, -0.7, 0.0, 2.1, wy - 0.3), caixa1=(-3.3, -0.8, 0.05, 2.0, wy - 0.3), lens=34, fstop=3.0, preenche=0.9, alt0=1.1, alt1=1.15),
        dict(t0=t1, t1=t2, caixa0=(-0.85, 0.45, 0.45, 1.45, 2.2), caixa1=(-0.8, 0.4, 0.5, 1.4, 2.2), lens=45, fstop=11.0, preenche=0.9, alt0=0.95, alt1=0.95),
        dict(t0=t2, t1=t3, caixa0=(-1.6, 0.9, 0.7, 2.3, wy - 0.5), caixa1=(-1.4, 0.9, 0.7, 2.2, wy - 0.5), lens=36, fstop=2.8, preenche=0.9, alt0=1.3, alt1=1.3),
        dict(t0=t3, t1=B[4], caixa0=(-3.4, -0.2, 0.0, 2.2, wy - 0.3), caixa1=(-3.5, -0.1, 0.1, 2.3, wy - 0.3), lens=32, fstop=3.0, preenche=0.9, alt0=1.2, alt1=1.4),
    ], entra="h", sai="h")
    r_, mE, mD, _ = maos(cams[1][0], "maos4", escala=0.4, d=0.5, y=-0.3)          # no insert do prato, as mãos de quem conta seguram a borda
    troca_mao("maos4", "esq", F(-1.0), "fechada"); troca_mao("maos4", "dir", F(-1.0), "fechada")


# ====================================================================== 5. O banheiro entope, dia 21 (fala 5)
def cheiro(nm, x, z0, n, f0, f1, cor="#7a9a3a", larg=0.5, alt=1.5, y=1.2):
    """linhas verdes onduladas de cheiro subindo (n fitas escalonadas, repetidas até f1): sobem, ondulam e somem"""
    mat = cena.amat(nm + "_m", cor, 1.0, 0.7)
    for k in range(n):
        pts = [(math.sin(t * 5.2 + k) * 0.05, t * 0.5) for t in [i / 8 for i in range(9)]]
        o = props.poly(f"{nm}_{k}", stroke(pts, 0.012), cor, 0.0, None, mat=mat)
        o.location = (x + (k - n / 2) * larg / n, y, z0)
        ciclo = 40; ini = f0 + (k * ciclo) // n
        o.scale = (0.0001,) * 3; key(o, "scale", f0 - 1, "CONSTANT")
        f = ini
        while f < f1:
            o.scale = (1.0, 1.0, 0.2); o.location.z = z0; key(o, "scale", f, "CONSTANT"); key(o, "location", f, "LINEAR")
            o.scale = (1.0, 1.0, 1.4); o.location.z = z0 + alt; key(o, "scale", f + ciclo - 8, "LINEAR"); key(o, "location", f + ciclo - 8, "LINEAR")
            o.scale = (0.0001,) * 3; key(o, "scale", f + ciclo - 7, "CONSTANT")
            f += ciclo


def moscas(nm, centro, n, f0, f1, raio=0.35, seed=4):
    rnd = random.Random(seed)
    for k in range(n):
        m = OA.mosca2d(f"{nm}{k}", (0, 0, 0), 2.2)
        ph, rr, vel = rnd.uniform(0, 6.28), raio * rnd.uniform(0.6, 1.2), rnd.uniform(0.8, 1.4)
        for f in range(f0, f1 + 1, 2):
            a = ph + 2 * math.pi * vel * (f - f0) / FPS * 1.3
            m.location = (centro[0] + rr * math.cos(a) + 0.04 * math.sin(7 * a), centro[1] - 0.05 - 0.01 * k, centro[2] + rr * 0.6 * math.sin(a * 1.7)); key(m, "location", f, "LINEAR")


@cena_(5)
def s05(c):
    """o calendário do dia 21 -> o banheiro: o vaso transborda e a poça cresce -> o cheiro verde sobe, o Zé e a Lu tapam o nariz e as moscas giram na lâmpada"""
    A, END = F(B[4] - 0.4), F(B[5] + 0.4)
    p = pal("banheiro"); wy = 3.6
    mundo(p)
    AM.sala("ban", -1.9, 1.9, -10.0, wy, 2.6, dict(parede="#5f6e58", lateral="#46543f", teto="#1a2018", viga="#232b21", chao="#2b3329", linha="#222a20", pilastra="#6a7a62"), piso="lajotas", passo_pilastra=0, passo_viga=0)
    cena.ground_disc("vinheta_b", 6.0, 5.0, cena.amat("vinheta_b_m", "#000000", 1.0, 0.5, ("radial", 0.8)), (0.0, -2.0, 0.006), n=40)
    for k in range(7):                                                     # azulejo: faixas horizontais mais claras na parede do fundo
        cena.poly_mesh(f"azul{k}", [(-1.9, wy - 0.02, 0.35 * k), (1.9, wy - 0.02, 0.35 * k), (1.9, wy - 0.02, 0.35 * k + 0.012), (-1.9, wy - 0.02, 0.35 * k + 0.012)], props.FM("#7b8a72"))
    giz_estados_s5 = OA.quadro_giz("giz21", (0.0, wy - 0.12, 1.6), 1.7, dias=21, rotulo="DIA 21")
    vaso = OA.privada("vaso", (0.65, wy - 0.3, 0.0), 1.5, transborda=0.05)
    poca = bpy.data.objects["vaso_poca"]
    t_e = wt(5, "entupiu"); fe = F(t_e)
    poca.scale = (0.05, 1, 0.05); key(poca, "scale", fe - 1, "LINEAR"); poca.scale = (1.6, 1, 1.6); key(poca, "scale", fe + 40, "BEZIER")
    lam = OA.lampadas("lamp_b", (-0.3, wy - 1.0, 2.05), 1.0, ligadas=1)
    halo("lamp_b_hl", -0.7, wy - 0.95, 2.3, 1.1, "#c8c27a", 0.3)
    t_c = wt(5, "cheiro")
    cheiro("fedor", 0.65, 0.85, 12, F(t_c) - 4, END, alt=1.6, y=wy - 0.6)
    cheiro("fedor2", -0.3, 0.2, 8, F(t_c) + 4, END, alt=1.8, y=wy - 1.2, cor="#8aa83e")
    moscas("mosca", (-0.7, wy - 1.0, 2.3), 6, F(t_c) - 6, END, raio=0.28)
    S.neblina(p, wy - 2.0, 0.0, cor="#7a9a3a")
    fog = [o for o in bpy.data.objects if o.name.startswith("neblina")]
    mat = fog[0].data.materials[0]
    mul = [n for n in mat.node_tree.nodes if n.type == "MATH" and n.operation == "MULTIPLY"][0].inputs[1]
    for f_, a_ in ((F(t_c) - 4, 0.0), (END, 0.28)):
        mul.default_value = a_; mul.keyframe_insert("default_value", frame=f_)
    Hz, tz, wz = ator(EA.ze, "ze", "q", -1.2, 1.6, A, END, p=p)
    Hl, tl_, wl = ator(EA.lu, "lu", "q", -0.5, 0.7, A, END, p=p)
    for H, tl in ((Hz, tz), (Hl, tl_)):
        tl.face(A, 0.0, lid="esperto", lidv=0.4, brow=-8, mouth="reta", look=(1.0, 0.0))
        tl.face(F(t_c), 1.0, lid="esperto", lidv=0.7, brow=14, mouth="nervosa", look=(1.0, 0.1))
        tl.intent(F(t_c) - 4, shF=10, elF=10); tl.intent(F(t_c) + 5, shF=104, elF=138, wrF=-20)            # a mão sobe até o nariz
        fim_ator(H, tl, A, END)
    t1, t2 = wt(5, "semana") + 0.2, wt(5, "entupiu") - 0.2
    P6.planos(c, [
        dict(t0=B[4], t1=t1, caixa0=(-0.6, 0.6, 1.2, 2.0, wy - 0.12), caixa1=(-0.5, 0.5, 1.25, 1.95, wy - 0.12), lens=45, fstop=2.2, preenche=0.9, alt0=1.6, alt1=1.6),
        dict(t0=t1, t1=wt(5, "cheiro") - 0.2, caixa0=(-0.3, 1.5, 0.0, 1.5, wy - 0.3), caixa1=(-0.1, 1.4, 0.05, 1.45, wy - 0.3), lens=40, fstop=2.5, preenche=0.9, alt0=0.9, alt1=0.9),
        dict(t0=wt(5, "cheiro") - 0.2, t1=B[5], caixa0=(-1.9, 1.5, 0.0, 2.6, wy - 0.3), caixa1=(-1.8, 1.4, 0.2, 2.6, wy - 0.3), lens=30, fstop=3.0, preenche=0.9, alt0=1.2, alt1=1.4, chaves=["ze_inv"]),
    ], entra="h", sai="h")


# ====================================================================== 6. A Pipoca some, dia 60 (fala 6)
@cena_(6)
def s06(c):
    """a gaiola, a Pipoca e o suéter: ela some -> a mão de quem conta levanta o suéter dobrado -> a mesa: pratos com carne, ninguém olha ninguém e a Rita empurra o prato"""
    A, END = F(B[5] - 0.4), F(B[6] + 0.4)
    p = pal("abrigo"); wy = 5.5
    sala_abrigo(p, wy=wy)
    giz_estados(wy, (60,), [(A, None)], x=-1.7, z=1.7, s=1.9, rotulo="DIA 60")
    OA.galao("galao_a", (2.4, wy - 0.4, 0.0), 1.7, nivel=0.5)
    lampadas(wy - 1.6, 3, x=0.2, nome="lamp")
    S.caixa3d(p, "caixote", 1.45, 4.3, 0.9, 0.5, d=0.7, cor="#3a342a", tampo="#6b5a3e", aresta="#8a7650")
    t_s = wt(6, "sumiu"); fs = F(t_s)
    g1 = OA.gaiola("gaiola", (1.45, 4.35, 0.5), 1.7); g2 = OA.gaiola_vazia("gaiola_v", (1.45, 4.35, 0.5), 1.7)
    pip = OA.porquinha("pip_g", (1.35, 4.28, 0.58), 1.5, vista="lado")
    g1.scale = (1.7,) * 3
    mostra_so([g1, pip, g2], [(A, fs), (A, fs), (fs, None)])
    # a mesa do jantar (a carne) mais adiante, fora do quadro até o corte
    ox = 8.0
    sala_abrigo(p, wy=wy, x0=ox - 3.6, x1=ox + 3.6) if False else None
    S.caixa3d(p, "mesa6", ox, 2.9, 2.6, 0.78, d=1.0, cor="#3a342a", tampo="#6b5a3e", aresta="#8a7650")
    AM.sala("sala6", ox - 3.6, ox + 3.6, -10.0, wy, 2.9, SALA, piso="lajotas", passo_pilastra=0, passo_viga=1.8)
    lampadas(wy - 1.6, 3, x=ox, nome="lamp6")
    xs = (ox - 0.95, ox, ox + 0.95)
    pratos = [OA.mesa_prato(f"p6_{k}", (x, 3.1, 0.78), 1.3, None, nivel="carne") for k, x in enumerate(xs)]
    Hz, tz, wz = ator(EA.ze, "ze", "front", xs[0], 3.75, A, END, p=p, z=-0.3)
    Hl, tl_, wl = ator(EA.lu, "lu", "front", xs[1], 3.75, A, END, p=p, z=-0.3)
    Hr, tr, wr = ator(EA.rita, "rita", "front", xs[2], 3.75, A, END, p=p, z=-0.3)
    t_n, t_p = wt(6, "jantar"), wt(6, "perguntar")
    for H, tl, olha in ((Hz, tz, (-0.6, -0.4)), (Hl, tl_, (0.6, -0.4)), (Hr, tr, (0.0, -0.8))):
        tl.face(A, 0.0, lid="esperto", lidv=0.5, brow=-8, mouth="reta", look=olha)
        tl.intent(F(wt(6, "noite")), head=14, torso=3)
        fim_ator(H, tl, A, END)
    tr.face(F(t_p) - 14, 1.0, lid="esperto", lidv=0.7, browup=0.02, mouth="reta", look=(0.0, -0.9))
    fp = F(t_p) - 10                                                       # a Rita empurra o prato e chora sem som
    pr = pratos[2]
    pr.location = (xs[2], 3.1, 0.78); key(pr, "location", fp, "BEZIER"); pr.location = (xs[2] + 0.28, 3.1, 0.78); key(pr, "location", fp + 10, "BEZIER")
    for j in range(5):
        ls = [OA.mosca2d(f"lag{j}", (0, 0, 0), 1.0)] if False else None
        t = props.poly(f"lagrima{j}", circle(0, 0, 0.012, 8), "#cfd6d0", 0.0, None)
        for f in range(fp + 8 + 7 * j, END, 30):
            t.location = (xs[2] - 0.035 + 0.07 * (j % 2), 3.55, 1.1); key(t, "location", f, "LINEAR"); t.scale = (1, 1, 1); key(t, "scale", f, "CONSTANT")
            t.location = (xs[2] - 0.035 + 0.07 * (j % 2), 3.55, 0.8); key(t, "location", f + 14, "LINEAR"); t.scale = (0.0001,) * 3; key(t, "scale", f + 14, "CONSTANT")
    mostra_so([bpy.data.objects[n] for n in ()], [])
    t1, t2 = wt(6, "Ninguém") - 0.1, wt(6, "Mas") - 0.1
    cams = P6.planos(c, [
        dict(t0=B[5], t1=t1, caixa0=(0.6, 2.3, 0.45, 1.5, 4.2), caixa1=(0.8, 2.1, 0.5, 1.4, 4.2), lens=40, fstop=2.4, preenche=0.9, alt0=0.95, alt1=0.95, chaves=["gaiola"]),
        dict(t0=t1, t1=t2, caixa0=(0.7, 2.2, 0.35, 1.35, 4.2), caixa1=(0.9, 2.0, 0.45, 1.3, 4.2), lens=50, fstop=11.0, preenche=0.9, alt0=0.85, alt1=0.9),
        dict(t0=t2, t1=t2 + 1.7, caixa0=(ox - 1.5, ox - 0.45, 0.62, 1.55, 3.0), caixa1=(ox - 1.45, ox - 0.5, 0.65, 1.52, 3.0), lens=50, fstop=2.0, preenche=0.9, alt0=1.0, alt1=1.0),
        dict(t0=t2 + 1.7, t1=t2 + 3.4, caixa0=(ox - 0.55, ox + 0.45, 0.62, 1.55, 3.0), caixa1=(ox - 0.5, ox + 0.5, 0.65, 1.52, 3.0), lens=50, fstop=2.0, preenche=0.9, alt0=1.0, alt1=1.0),
        dict(t0=t2 + 3.4, t1=B[6], caixa0=(ox + 0.25, ox + 1.4, 0.55, 1.5, 3.0), caixa1=(ox + 0.4, ox + 1.2, 0.65, 1.35, 3.0), lens=50, fstop=2.0, preenche=0.9, alt0=0.95, alt1=0.95),
    ], entra="h", sai="h")
    cam_pov = cams[1][0]
    r_, mE, mD, _ = maos(cam_pov, "maos6", escala=0.34, d=0.5, y=-0.3)
    troca_mao("maos6", "esq", F(-1.0), "fechada"); troca_mao("maos6", "dir", F(-1.0), "fechada")
    fl = F(t1) + 6
    sw = OA.sueter_dobrado("sw_mao", (0.0, -0.02, 0.27), 1.0, parent=bpy.data.objects["maos6_inv_dir"]); sw.scale = (1.0,) * 3
    mostra_so([sw], [(fl, None)])
    swm = bpy.data.objects.get("gaiola_v_su")
    if swm:
        swm.scale = (1, 1, 1); key(swm, "scale", fl - 1, "CONSTANT"); swm.scale = (0.0001,) * 3; key(swm, "scale", fl, "CONSTANT")
    mD.location = (0.2, 0, -0.3); key(mD, "location", F(t1), "BEZIER"); mD.location = (0.2, 0, 0.12); key(mD, "location", fl, "BEZIER"); mD.location = (0.2, 0, 0.3); key(mD, "location", fl + 22, "BEZIER")


# ====================================================================== 7. Os meses, dia 200 e 300 (fala 7)
def carta(nome, loc, s=3.0, verso=True):
    r = empty(nome, None, loc); r.scale = (s, s, s)
    props.inked(nome + "_f", rrect(-0.032, 0.0, 0.032, 0.089, 0.005, 2), "#d8d0bb" if not verso else "#34506e", r, w=0.0014, shade=0.002, shade_color="#1c3042")
    if verso:
        props.poly(nome + "_v", rrect(-0.024, 0.008, 0.024, 0.081, 0.003, 1), "#d8d0bb", -0.003, r)
        props.poly(nome + "_v2", rrect(-0.018, 0.013, 0.018, 0.076, 0.003, 1), "#34506e", -0.004, r)
    return r


@cena_(7)
def s07(c):
    """o abrigo no escuro, só uma lâmpada acesa e o calendário de giz cobrindo a parede -> o Zé e a Lu brigam sem som, a Rita ao fundo -> a Lu na cama, fraca, e o dia em que ela morre:
    a manta dobrada, a jaqueta pendurada na cadeira"""
    A, END = F(B[6] - 0.4), F(B[7] + 0.4)
    p = pal("escuro"); wy = 5.5
    sala_abrigo(p, wy=wy)
    OA.quadro_giz("giz_a", (-1.9, wy - 0.12, 1.45), 2.3, dias=90, rotulo="DIA 200")
    OA.quadro_giz("giz_b", (0.45, wy - 0.12, 1.45), 2.3, dias=90, rotulo="")
    lampadas(wy - 1.6, 1, x=-1.0, nome="lamp")
    t_m, t_z, t_f, t_mo = wt(7, "meses"), wt(7, "Zé"), wt(7, "fraca"), wt(7, "morreu")
    fm = F(t_mo)
    # a cama da Lu à direita; a Lu deitada (só a cabeça e os ombros acima da manta) até o "morreu"
    cm1 = OA.cama("cama1", (1.15, 4.0, 0.0), 1.15); cm2 = OA.cama("cama2", (1.15, 4.0, 0.0), 1.15, manta="#6e6a4a", dobrada=True)
    cad = OA.cadeira("cad", (-1.15, 4.3, 0.0), 1.3); jaq = OA.jaqueta_pendurada("jaq", (-1.15, 4.22, 0.62), 1.3)
    mostra_so([cm1, cm2, jaq], [(A, fm), (fm, None), (fm, None)])
    Hl, tl_, wl = ator(EA.lu_fraca, "lu_fraca", "front", 1.4, 4.45, A, END, p=p, z=-0.78)
    tl_.face(A, 0.0, lid="esperto", lidv=0.75, browup=0.01, mouth="reta", look=(-1.0, 0.2))
    tl_.face(F(t_z), 1.0, lid="esperto", lidv=0.55, brow=-6, mouth="nervosa", look=(-1.0, 0.1))
    tl_.face(F(t_f), 1.0, lid="esperto", lidv=0.85, browup=0.012, mouth="reta", look=(0.0, 0.5))
    fim_ator(Hl, tl_, A, END)
    wl.scale = (wl.scale.x, wl.scale.y, wl.scale.z)
    wl.scale = (wl.scale.x,) * 3; key(wl, "scale", fm - 1, "CONSTANT"); wl.scale = (0.0001,) * 3; key(wl, "scale", fm, "CONSTANT")
    Hz, tz, wz = ator(EA.ze, "ze", "q", -0.3, 3.6, A, END, p=p)
    tz.face(A, 0.0, lid="esperto", lidv=0.55, brow=-6, mouth="reta", look=(0.2, 0.6))
    tz.face(F(t_z), 1.0, lid="esperto", lidv=0.4, brow=-12, mouth="nervosa", look=(1.0, 0.0))
    for k in range(8):                                                      # discutem sem som: a boca alterna, o braço sobe e desce
        f = F(t_z) + 10 + 16 * k
        tz.face(f, 1.0, lid="esperto", lidv=0.4, brow=-12, mouth="nervosa" if k % 2 == 0 else "reta", look=(1.0, 0.0))
        tz.intent(f, shF=20 + 30 * (k % 2), elF=40 + 20 * (k % 3))
    tz.face(fm, 1.0, lid="esperto", lidv=0.75, browup=0.02, mouth="reta", look=(0.8, 0.8))
    tz.intent(fm, head=18, torso=4, shF=6, elF=8)
    fim_ator(Hz, tz, A, END)
    S.caixa3d(p, "cx_r", -2.1, 3.5, 0.8, 0.42, d=0.6, cor="#2a2a24", tampo="#4a4a3c", aresta="#6a6a52")
    Hr, tr, wr = ator(EA.rita, "rita", "front", -2.1, 3.9, A, END, p=p, z=-0.34)
    tr.face(A, 0.0, lid="esperto", lidv=0.8, browup=0.014, mouth="reta", look=(0.4, 0.6))
    fim_ator(Hr, tr, A, END)
    t1, t2 = wt(7, "O") - 0.1, wt(7, "mas") - 0.1
    P6.planos(c, [
        dict(t0=B[6], t1=t1, caixa0=(-3.0, 2.4, 0.1, 2.9, wy - 0.3), caixa1=(-2.7, 2.3, 0.15, 2.8, wy - 0.3), lens=28, fstop=3.5, preenche=0.92, alt0=1.3, alt1=1.35),
        dict(t0=t1, t1=t2, caixa0=(-1.0, 2.1, 0.5, 2.0, 3.8), caixa1=(-0.8, 2.0, 0.55, 1.9, 3.8), lens=40, fstop=2.4, preenche=0.92, alt0=1.15, alt1=1.15),
        dict(t0=t2, t1=B[7], caixa0=(-0.6, 2.0, 0.2, 1.8, 3.9), caixa1=(0.1, 1.9, 0.3, 1.4, 3.9), lens=45, fstop=2.2, preenche=0.92, alt0=1.0, alt1=0.9),
    ], entra="h", sai="h")


# ====================================================================== 8. O baralho, sozinho (fala 8)
@cena_(8)
def s08(c):
    """o Zé joga baralho sozinho: de um lado a mão dele, do outro a cadeira com a jaqueta da Lu; ele joga uma carta para ele e outra para a cadeira"""
    A, END = F(B[7] - 0.4), F(B[8] + 0.4)
    p = pal("escuro"); wy = 5.5
    sala_abrigo(p, wy=wy)
    OA.quadro_giz("giz_a", (-1.7, wy - 0.12, 1.5), 2.2, dias=90, rotulo="DIA 300")
    OA.quadro_giz("giz_b", (0.6, wy - 0.12, 1.5), 2.2, dias=90, rotulo="")
    lampadas(wy - 1.6, 1, x=0.0, nome="lamp")
    S.caixa3d(p, "mesa8", 0.2, 3.0, 2.2, 0.78, d=1.0, cor="#3a342a", tampo="#6b5a3e", aresta="#8a7650")
    cad = OA.cadeira("cad", (1.65, 3.7, 0.0), 1.5); jaq = OA.jaqueta_pendurada("jaq", (1.65, 3.62, 0.72), 1.5)
    OA.mesa_prato("pr8", (0.9, 3.15, 0.78), 1.2, None, nivel="vazio") if False else None
    Hz, tz, wz = ator(EA.ze, "ze", "front", -0.5, 3.75, A, END, p=p, z=-0.3)
    tz.face(A, 0.0, lid="esperto", lidv=0.6, brow=-6, mouth="reta", look=(0.0, 0.7))
    tz.face(F(wt(8, "pelos")), 1.0, lid="esperto", lidv=0.45, browup=0.012, mouth="pequena", look=(0.9, 0.2))
    tz.intent(A + 6, head=14, torso=3)
    fim_ator(Hz, tz, A, END)
    # as cartas: uma para o lado dele, outra para o lado da cadeira, de tempos em tempos
    t_j, t_s, t_p = wt(8, "jogando"), wt(8, "sozinho"), wt(8, "pelos")
    k = 0
    for f in range(F(t_j) - 6, F(B[8]), 14):
        lado = k % 2
        cd = carta(f"carta{k}", (-0.5, 3.4, 1.0), 2.8, verso=(k % 3 != 0))
        UN.esconde_ate(cd, f)
        alvo = (-0.15, 3.2, 0.79) if lado == 0 else (1.15, 3.2, 0.79)
        UN.voa(cd, f, f + 9, (-0.45, 3.45, 1.0), alvo, alt=0.25, assenta=4)
        cd.rotation_euler = (math.radians(90) * 0, 0, 0)
        k += 1
    t1 = t_s - 0.1
    P6.planos(c, [
        dict(t0=B[7], t1=t1, caixa0=(-1.3, 0.6, 0.6, 1.7, 3.0), caixa1=(-1.1, 0.8, 0.65, 1.7, 3.0), lens=45, fstop=2.2, preenche=0.9, alt0=1.15, alt1=1.15),
        dict(t0=t1, t1=B[8], caixa0=(-0.9, 2.5, 0.4, 1.8, 3.2), caixa1=(0.0, 2.4, 0.45, 1.6, 3.4), lens=42, fstop=2.2, preenche=0.9, alt0=1.15, alt1=1.15),
    ], entra="h", sai="h")


# ====================================================================== 9. A porta, dia 700 (fala 9)
@cena_(9)
def s09(c):
    """o último galão: o Zé bebe do gargalo (3D) -> vai até a porta, gira a roda com as duas mãos, a folha corre e faíscas de ferrugem saltam -> a luz branca entra e cega a câmera"""
    A, END = F(B[8] - 0.4), F(B[9] + 0.4)
    p = pal("escuro"); wy = 5.5
    sala_abrigo(p, wy=wy)
    OA.quadro_giz("giz_a", (-1.7, wy - 0.12, 1.5), 2.2, dias=90, rotulo="DIA 700")
    OA.quadro_giz("giz_b", (0.6, wy - 0.12, 1.5), 2.2, dias=90, rotulo="")
    OA.prateleira("est", (-2.55, wy - 0.15, 0.0), 1.9, nivel=0.1)
    lampadas(wy - 1.6, 1, x=0.2, nome="lamp")
    porta = OA.porta_abrigo("porta", (2.8, wy - 0.1, 0), 1.0, aberta=0.0, luz_fora="#f4f1e6")
    folha = bpy.data.objects["porta_folha"]; roda = bpy.data.objects["porta_roda"]
    halo("porta_gl", 2.8, wy - 0.12, 1.2, 2.4, "#f4f1e6", 0.0)
    t_g, t_z, t_d, t_p = wt(9, "galão"), wt(9, "Zé"), wt(9, "destrancou"), wt(9, "porta")
    jar = OA.galao("jarro", (1.2, 4.3, 0.0), 1.7, nivel=0.14)
    ze = ator3("ze", "ze", 1.25, 4.05, p, rot=-10)
    f_b, f_d, f_walk = F(t_g) - 6, F(t_z) + 2, F(t_d) - 20
    f_roda = F(t_d)
    ch = [(A, dict(pos=(1.25, 4.05, 0), rot=-10, ombro=(-4, 6), cotovelo=(-10, -10))),
          (f_b, dict(pos=(1.25, 4.05, 0), rot=-10, ombro=(-70, -66), cotovelo=(-50, -52), abre=(6, 6), tronco=-4, cabeca=0)),     # pega o jarro
          (f_b + 10, dict(pos=(1.25, 4.05, 0), rot=-10, ombro=(-95, -88), cotovelo=(-70, -72), abre=(6, 6), tronco=-6, cabeca=-12)),   # leva à boca
          (f_d, dict(pos=(1.25, 4.05, 0), rot=-10, ombro=(-70, -66), cotovelo=(-50, -52), tronco=-3, cabeca=0)),
          (f_d + 8, dict(pos=(1.25, 4.05, 0), rot=-10, ombro=(-6, 8), cotovelo=(-12, -12))),
          (f_walk, dict(pos=(1.45, 4.0, 0), rot=-40, ombro=(10, -10), cotovelo=(-12, -12), quadril=(-25, 25), joelho=(18, 4))),
          (f_roda - 6, dict(pos=(2.75, wy - 1.1, 0), rot=-180, ombro=(-70, -62), cotovelo=(-20, -30), abre=(6, 6), tronco=-5, quadril=(0, 0))),
          (f_roda + 20, dict(pos=(2.75, wy - 1.1, 0), rot=-180, ombro=(-62, -60), cotovelo=(-24, -26), tronco=-8)),
          (END, dict(pos=(2.75, wy - 1.1, 0), rot=-180, ombro=(-62, -60), cotovelo=(-24, -26), tronco=-8))]
    ze.anima(ch, A, END, vida=0.4)
    ze.expressao([(A, dict(lid=0.5, brow=-0.3)), (f_b + 10, dict(lid=0.7)), (f_roda, dict(lid=0.4, brow=-0.5)), (END, dict(lid=0.3))], A, END, seed=2)
    # o jarro sobe até a boca e volta
    jar.location = (1.2, 4.3, 0.0); key(jar, "location", f_b, "BEZIER"); jar.rotation_euler = (0, 0, 0); key(jar, "rotation_euler", f_b, "BEZIER")
    jar.location = (1.18, 3.95, 1.45); key(jar, "location", f_b + 10, "BEZIER"); jar.rotation_euler = (0, math.radians(-100), 0); key(jar, "rotation_euler", f_b + 10, "BEZIER")
    jar.location = (1.18, 3.95, 1.45); key(jar, "location", f_d - 4, "BEZIER"); jar.rotation_euler = (0, math.radians(-100), 0); key(jar, "rotation_euler", f_d - 4, "BEZIER")
    jar.location = (1.2, 4.3, 0.0); key(jar, "location", f_d + 8, "BEZIER"); jar.rotation_euler = (0, 0, 0); key(jar, "rotation_euler", f_d + 8, "BEZIER")
    # a roda gira e a folha corre
    roda.rotation_euler = (0, 0, 0); key(roda, "rotation_euler", f_roda, "BEZIER"); roda.rotation_euler = (0, math.radians(160), 0); key(roda, "rotation_euler", f_roda + 16, "BEZIER")
    folha.location = (0, 0, 0); key(folha, "location", f_roda + 14, "BEZIER"); folha.location = (-1.1, 0, 0); key(folha, "location", f_roda + 34, "BEZIER")
    for o in [o for o in bpy.data.objects if o.name == "porta_gl"]:
        mat = o.data.materials[0]; mul = [n for n in mat.node_tree.nodes if n.type == "MATH" and n.operation == "MULTIPLY"][0].inputs[1]
        for f_, a_ in ((f_roda + 14, 0.0), (f_roda + 40, 0.9)):
            mul.default_value = a_; mul.keyframe_insert("default_value", frame=f_)
    # faíscas de ferrugem saltando da roda
    rnd = random.Random(5)
    for k in range(14):
        sp = props.poly(f"fagulha{k}", circle(0, 0, 0.012, 8), "#c8782e", 0.0, None)
        f0 = f_roda + rnd.randint(0, 14); vx, vz = rnd.uniform(-0.8, 0.8), rnd.uniform(0.2, 1.2)
        UN.esconde_ate(sp, f0)
        for j in range(0, 14, 2):
            t = j / FPS
            sp.location = (2.8 + 0.1 + vx * t * 0.6, wy - 0.3, 1.15 + vz * t - 2.2 * t * t); key(sp, "location", f0 + j, "LINEAR")
        UN.some(sp, f0 + 14, 2)
    t1, t2 = wt(9, "meio") - 0.1 + 0.9, wt(9, "finalmente") + 0.0
    c1 = camera_livre(c, "pl0", B[8], t2 - 0.2, (2.9, 0.4, 1.5), (2.4, 1.3, 1.5), (1.2, 4.0, 1.25), (1.2, 4.0, 1.3), lens=32, fstop=4.0)
    c2 = camera_livre(c, "pl1", t2 - 0.2, t_p + 0.1, (0.7, 1.4, 1.55), (1.9, 2.6, 1.5), (2.5, wy - 0.4, 1.3), (2.8, wy - 0.3, 1.25), lens=30, fstop=4.0)
    c3 = camera_livre(c, "pl2", t_p + 0.1, B[9], (2.4, 2.4, 1.55), (2.75, 3.9, 1.5), (2.8, wy, 1.4), (2.8, wy + 1.0, 1.4), lens=28, fstop=5.6)
    flash = cena.quad("flash", -1, 1, -1, 1, cena.amat("flash_m", "#fffaf0", 1.6, 1.0), 0.0, norm=False)
    flash.parent = c3; flash.location = (0, 0, -0.3); flash.rotation_euler = (math.radians(90), 0, 0); flash.scale = (0.9, 1.0, 1.8)
    mul = [n for n in flash.data.materials[0].node_tree.nodes if n.type == "MATH" and n.operation == "MULTIPLY"][0].inputs[1]
    for f_, a_ in ((F(t_p) - 2, 0.0), (F(B[9]) - 4, 0.9), (F(B[9]) + 2, 1.0)):
        mul.default_value = a_; mul.keyframe_insert("default_value", frame=f_)
    camera_planos(c, [(c1, B[8], 3.0)], entra="h", sai=None); camera_planos(c, [(c3, B[9], 3.0)], entra=None, sai="h")


# ====================================================================== 10. Lá fora (fala 10)
def ruinas_rua(p, y0, y1, seed=7):
    """a rua depois: ruínas dos dois lados em alturas diferentes, postes tortos, chão de cinza com rachaduras e névoa de poeira em camadas"""
    rnd = random.Random(seed)
    cena.poly_mesh("chao_cinza", [(-60, y0, 0), (60, y0, 0), (60, y1, 0), (-60, y1, 0)], props.FM(p["chao"]))
    for k in range(18):
        xr = rnd.uniform(-3, 3); yr = rnd.uniform(y0 + 2, y1 - 2)
        pts = [(xr, yr, 0.002)]
        for j in range(1, 5):
            pts.append((pts[-1][0] + rnd.uniform(-0.5, 0.5), pts[-1][1] + rnd.uniform(0.3, 1.2), 0.002))
        for j in range(len(pts) - 1):
            a, b = pts[j], pts[j + 1]
            cena.poly_mesh(f"rach{k}_{j}", [(a[0] - 0.02, a[1], 0.002), (a[0] + 0.02, a[1], 0.002), (b[0] + 0.02, b[1], 0.002), (b[0] - 0.02, b[1], 0.002)], props.FM("#2a2820"))
    y = y0 + 4.0; k = 0
    while y < y1:
        for s_ in (-1, 1):
            OA.ruina(f"ru{s_}_{k}", (s_ * rnd.uniform(5.0, 8.5), y + rnd.uniform(-1, 1), 0.0), rnd.uniform(0.9, 1.6) * (-1 if rnd.random() < 0.5 else 1) if False else rnd.uniform(0.9, 1.6), cor=rnd.choice(("#6a665a", "#5f5c50", "#76705f")), seed=k * 3 + s_)
        if k % 2 == 0:
            OA.poste_torto(f"pt{k}", (rnd.choice((-1, 1)) * rnd.uniform(3.2, 4.4), y + 2.0, 0.0), 1.0, ang=rnd.choice((-20, 14, 22, -12)))
        y += 7.5; k += 1


@cena_(10)
def s10(c):
    """de dentro da porta: a rua em ruínas, cinza e poeira caindo -> o chão rachado, o silêncio -> a bicicleta, cinza de pó, ao pé da porta; a mão (magra, com relógio sem ponteiros) toca a campainha"""
    A, END = F(B[9] - 0.4), F(B[10] + 0.4)
    p = pal("cinza"); mundo(p)
    ceu(p, 60.0, topo="#a9a597", meio="#cfc9b4")
    ruinas_rua(p, -6.0, 60.0)
    for yv, al in ((6.0, 0.12), (14.0, 0.18), (26.0, 0.26), (40.0, 0.34)):
        S.neblina(p, yv, al, z1=40.0)
    cena.dust(p, 90, (-6, 6), END, seed=3, color="#e8e2cc", alpha=0.8, y_range=(0.0, 16.0), z_range=(0.2, 5.0), size=(0.008, 0.02))
    bici = OA.bicicleta("bici", (1.2, 2.3, 0.0), 1.2, cor="#6a665a")
    t_c, t_s, t_b = wt(10, "cinza"), wt(10, "silêncio"), wt(10, "bicicleta")
    c1 = camera_livre(c, "pl0", B[9], t_c - 0.1, (0.0, -0.6, 1.55), (0.0, 0.8, 1.55), (-3.0, 24.0, 1.6), (3.0, 24.0, 1.5), lens=24, fstop=8.0, bob=0.01, bob_hz=1.4)
    c2 = camera_livre(c, "pl1", t_c - 0.1, t_b - 0.1, (0.0, 0.8, 1.2), (0.0, 1.6, 0.55), (0.0, 8.0, 0.1), (0.0, 5.0, 0.0), lens=28, fstop=6.0)
    c3 = camera_livre(c, "pl2", t_b - 0.1, B[10], (0.1, 0.0, 1.05), (0.55, 0.9, 0.95), (1.2, 2.3, 0.7), (1.15, 2.3, 0.75), lens=28, fstop=11.0)
    r3, mE3, mD3, _ = maos(c3, "maos10", escala=0.4, d=0.5, y=-0.3)
    troca_mao("maos10", "esq", F(-1.0), "fechada"); troca_mao("maos10", "dir", F(-1.0), "fechada")
    props.inked("relogio", circle(0, 0, 0.06, 20), "#aab6c8", bpy.data.objects["maos10_inv_dir"], loc=(0.0, -0.012, 0.04), w=0.006, shade=0.01, shade_color="#6a7a8a")
    props.poly("relogio_mostrador", circle(0.0, 0.04, 0.045, 20), "#d8d0bb", -0.02, bpy.data.objects["relogio"])
    fs = F(wt(10, "ainda"))
    mD3.location = (0.2, 0, 0.0); key(mD3, "location", fs - 4, "BEZIER"); mD3.location = (-0.05, 0, 0.3); key(mD3, "location", fs + 30, "BEZIER")
    mD3.location = (-0.05, 0, 0.3); key(mD3, "location", F(wt(10, "mesmo")), "BEZIER"); mD3.location = (-0.03, 0, 0.27); key(mD3, "location", F(wt(10, "mesmo")) + 4, "BEZIER")
    mD3.location = (-0.05, 0, 0.3); key(mD3, "location", F(wt(10, "mesmo")) + 8, "BEZIER")
    for j in range(3):                                                       # o 'trim' sem eco: três anéis de ar que abrem e somem
        rg = props.poly(f"trim{j}", stroke([(0.05 * math.cos(math.radians(a)), 0.05 * math.sin(math.radians(a)) + 0.0) for a in range(0, 361, 15)], 0.004), "#e8e2cc", 0.0, None)
        rg.location = (1.28, 2.2, 0.68); f0 = F(wt(10, "mesmo")) + 4 + 3 * j
        UN.esconde_ate(rg, f0)
        for k in range(8):
            u = k / 7; rg.scale = (0.4 + 2.4 * u, 1, 0.4 + 2.4 * u); key(rg, "scale", f0 + k, "LINEAR")
        UN.some(rg, f0 + 8, 2)
    luzb = cena.quad("luz_ini", -1, 1, -1, 1, cena.amat("luz_ini_m", "#fffaf0", 1.6, 1.0), 0.0, norm=False)       # a luz da porta ainda cega no começo e vai baixando
    luzb.parent = c1; luzb.location = (0, 0, -0.3); luzb.rotation_euler = (math.radians(90), 0, 0); luzb.scale = (0.9, 1.0, 1.8)
    mul = [n for n in luzb.data.materials[0].node_tree.nodes if n.type == "MATH" and n.operation == "MULTIPLY"][0].inputs[1]
    for f_, a_ in ((A, 1.0), (F(B[9]) + 6, 0.9), (F(B[9]) + 30, 0.0)):
        mul.default_value = a_; mul.keyframe_insert("default_value", frame=f_)
    camera_planos(c, [(c1, B[9], 3.0)], entra=None, sai=None); camera_planos(c, [(c3, B[10], 3.0)], entra=None, sai="h")


# ====================================================================== 11. O preço (fala 11)
@cena_(11)
def s11(c):
    """de fora: o Zé e a Rita (em 3D), magros e rasgados, lado a lado diante da porta aberta com a luz amarela, a bicicleta entre eles -> a câmera recua devagar até o abrigo virar um ponto; escurece"""
    A, END = F(B[10] - 0.4), F(B[11] + 0.4)
    p = pal("cinza"); mundo(p)
    ceu(p, 140.0, topo="#8d8a7c", meio="#c4bea8")
    ruinas_rua(p, -80.0, 120.0, seed=11)
    cena.poly_mesh("morro11", [(-30, 40.0, 0), (-18, 40.0, 5.0), (-6, 40.0, 8.0), (0, 40.0, 8.6), (10, 40.0, 7.2), (22, 40.0, 3.6), (34, 40.0, 0)], props.FM("#3b4235"))
    halo("morro_gl", 0.0, 39.8, 1.5, 3.4, "#d9b66a", 0.55)
    OA.porta_abrigo("porta_morro", (0, 39.7, 0), 1.0, aberta=0.8, luz_fora="#e8c470")
    bici = OA.bicicleta("bici", (0.0, 36.0, 0.0), 1.0, cor="#6a665a")
    ze = ator3("ze", "ze", -0.75, 35.5, p, rot=0); ri = ator3("rita", "rita", 0.75, 35.5, p, rot=0)
    for H, seed in ((ze, 1), (ri, 2)):
        H.pose(ombro=(-3, 5), cotovelo=(-10, -10), abre=(4, 4)); H.rosto(boca="reta", lid=0.55)
        H.anima([(A, dict(pos=(H.raiz.location.x, 35.5, 0), rot=0, ombro=(-3, 5), cotovelo=(-10, -10))), (END, dict(pos=(H.raiz.location.x, 35.5, 0), rot=0, ombro=(-3, 5), cotovelo=(-10, -10)))], A, END, vida=0.5, seed=seed)
        H.expressao([(A, dict(lid=0.55, brow=-0.2))], A, END, seed=seed)
    for yv, al in ((20.0, 0.10), (30.0, 0.16), (38.0, 0.2)):
        S.neblina(p, yv, al, z1=40.0)
    cena.dust(p, 70, (-5, 5), END, seed=5, color="#e8e2cc", alpha=0.7, y_range=(10.0, 36.0), z_range=(0.2, 4.0), size=(0.01, 0.025))
    # a câmera recua do rosto deles até virarem pontos; no fim a tela escurece
    c1 = camera_livre(c, "pl0", B[10], B[11], (0.1, 31.0, 1.55), (0.0, -70.0, 9.0), (0.0, 35.5, 1.35), (0.0, 39.7, 2.2), lens=30, fstop=6.0, curva="easy")
    camera_planos(c, [(c1, B[10], 3.0)], entra="h", sai=None)
    noite = cena.quad("noite", -1, 1, -1, 1, cena.amat("noite_m", "#050606", 1.0, 1.0), 0.0, norm=False)
    noite.parent = c1; noite.location = (0, 0, -0.3); noite.rotation_euler = (math.radians(90), 0, 0); noite.scale = (0.9, 1.0, 1.8)
    mul = [n for n in noite.data.materials[0].node_tree.nodes if n.type == "MATH" and n.operation == "MULTIPLY"][0].inputs[1]
    for f_, a_ in ((F(B[11]) - 36, 0.0), (F(B[11]) - 2, 1.0)):
        mul.default_value = a_; mul.keyframe_insert("default_value", frame=f_)


def com_vida(fn):
    """depois de montar a cena: tremido de traço em tudo, figurantes balançando, câmera na mão; e grava onde estão os rostos"""
    def g(c):
        fn(c)
        for pre in [x for x in os.environ.get("HIDE", "").split(",") if x]:       # depuração: esconde objetos pelo prefixo do nome
            for o in bpy.data.objects:
                if o.name.startswith(pre):
                    o.hide_render = True
        f0, f1 = c["f0"] - 12, c["f1"] + 12
        n = vida.boil_cena(f0, f1)
        vida.balanca_figurantes(f0, f1)
        vida.camera_na_mao(f0, f1)
        print(f"VIDA tremido em {n} objetos")
        argv = sys.argv[sys.argv.index("--") + 1:]
        if "--at" not in argv and "--list" not in argv and len(argv) > 1:
            os.makedirs(argv[1], exist_ok=True)
            rostos.exporta(c, os.path.join(argv[1], "rostos.json"))
    return g


for _k, (_a, _b, _fn) in list(P4.CENAS.items()):
    P4.CENAS[_k] = (_a, _b, com_vida(_fn))

if __name__ == "__main__":
    P4.main()
