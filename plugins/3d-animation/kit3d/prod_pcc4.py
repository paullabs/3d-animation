"""PCC, versão 4: roteiro "Você acabou de entrar no PCC" (roteiros/pcc3.json, voz em roteiros/voz-pcc3).
Mesmo padrão da v3: paleta petróleo e coral, curva S suave (curvas.py), uma câmera em movimento por cena e
transições em movimento (cortina). O herói usa a roupa de presidiário (uniforme.py).
blender -b -P prod_pcc4.py -- CENA OUT [--scale 1] [--samples 16] [--at t1,t2] [--list]"""
import sys, os, math, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy, lib
from lib import *
import cena, props, luz, curvas, frente, uniforme as U, balanca as BL, dinheiro as D, trono as T, grana as G, area, armas, transicao as TR
from anim import Timeline
from prod_pcc import F, finish, FPS
from prod_pcc3 import camera_movel, baked_slide, cortina, escada5, cresce, surge, _mix

VOZ = (__import__("canal38_env").RAIZ + "/roteiros/voz-pcc3")
PAL = json.load(open(VOZ + "/palavras.json"))
# As cenas foram escritas nos tempos da voz do Mac (voz-pcc3); VOZ_NOVA leva cada segundo para o mesmo ponto da narração nova.
VOZ_NOVA = os.environ.get("VOZ_NOVA", (__import__("canal38_env").RAIZ + "/roteiros/voz-pcc5"))
if VOZ_NOVA:
    import tempo, prod_pcc, prod_pcc3
    _WARP = tempo.mapa(VOZ, VOZ_NOVA); _F0 = prod_pcc.F

    def F(t):
        return _F0(_WARP(t))
    prod_pcc.F = prod_pcc3.F = F
P = T.PALETAS[os.environ.get("PALETA", "indigo")]          # escolhida pelo usuário (opção B)
CENAS = {}


def wt(frase, txt, nth=0):
    ws = [w for w in PAL if w["frase"] == frase and w["txt"].strip(".,:;!?…").lower() == txt.lower()]
    return ws[nth]["t0"]


def cena_(name, t0, t1):
    def deco(fn):
        CENAS[name] = (t0, t1, fn); return fn
    return deco


def fundo(p, wy, z_meio=2.0, x=(-20, 20), z=(-3, 14)):
    """parede em tom médio com degradê (claro no meio, escuro no alto) e chão"""
    bpy.context.scene.world.node_tree.nodes["Background"].inputs[0].default_value = (*lib.srgb(p["top"]), 1)
    props.skywall("parede_" + str(wy), wy, [(z[0], p["low"]), (z_meio, p["mid"]), (z_meio + 3.5, _mix(p["mid"], p["top"], 0.55)), (z[1], p["top"])], x[0], x[1], z[0], z[1])
    cena.poly_mesh("chao_" + str(wy), [(x[0], -30, -0.004), (x[1], -30, -0.004), (x[1], wy, -0.004), (x[0], wy, -0.004)], props.FM(p["chao"]))


def seguro(cam):
    """lente descentralizada fixa: o ponto mirado cai no centro da área segura do Reels (area.py)"""
    cd = cam.data
    if cd.animation_data:                       # apaga também a ação: senão o shift antigo volta quando o foco ganha chave
        act = cd.animation_data.action
        cd.animation_data_clear()
        if act:
            bpy.data.actions.remove(act)
    cd.shift_x, cd.shift_y = area.shift_padrao()


def pedestal(p, name, x, y, w, h, d=0.5):
    """bloco escuro e liso com aresta clara, onde o dinheiro fica (3D: frente e tampo)"""
    esc = _mix(p["top"], "#000000", 0.2)
    cena.poly_mesh(name + "_f", [(x - w / 2, y, 0), (x + w / 2, y, 0), (x + w / 2, y, h), (x - w / 2, y, h)], props.FM(esc))
    cena.poly_mesh(name + "_t", [(x - w / 2, y, h), (x + w / 2, y, h), (x + w / 2, y + d, h), (x - w / 2, y + d, h)], props.FM(_mix(esc, p["aresta"], 0.35)))
    cena.poly_mesh(name + "_a", [(x - w / 2, y - 0.001, h - 0.012), (x + w / 2, y - 0.001, h - 0.012), (x + w / 2, y - 0.001, h), (x - w / 2, y - 0.001, h)], props.FM(p["aresta"]))


# ====================================================================== A1. Você acabou de entrar (0 - 5,73)
@cena_("a1", 0.0, 5.73)
def a1(c):
    """ele de frente sob uma luz só; a grade fecha atrás em "PCC"; em "salário" as notas verdes caem uma a uma
    numa pilha sobre o pedestal à direita (12 notas de R$ 100 = R$ 1.200), no ritmo do número na tela"""
    sc = c["sc"]; A, END = F(-0.5), F(6.1)
    p = P; wy = 1.6
    pe = dict(p, mid=_mix(p["mid"], p["top"], 0.45), low=_mix(p["low"], p["top"], 0.35))      # fundo escuro: ele e o dinheiro recortam
    fundo(pe, wy, z_meio=1.4, x=(-9, 9), z=(-2, 8))
    cena.disc("halo_a1", 2.2, cena.amat("halo_a1_m", p["halo"], 1.0, 0.45, ("radial", 1.5)), (0.15, wy - 0.05, 1.3))
    luz.feixe("feixe_a1", 0.15, wy - 0.4, 0.0, 4.4, 1.9, 0.35, p["luz"], forca=1.3, frames=END, poeira=40, seed=21)
    gr = props.grade("porta_a1", -1.7, 1.7, 0.0, 3.2, 1.1, p["grade"], n=7, w=0.05, rails=0)
    for z in (0.03, 3.1):
        props.poly(f"porta_a1_t{z}", cena.rect(-1.7, z, 1.7, z + 0.07), p["grade"], -0.001, gr)
    t_f = wt(1, "pcc")
    for f in range(F(t_f) - 10, F(t_f) + 1):                       # corre acelerando e bate
        u = (f - (F(t_f) - 10)) / 10; gr.location.x = 3.6 * (1 - u * u); key(gr, "location", f, "LINEAR")
    H = U.heroi_preso("heroi", "front", rim=p["borda"])
    tl = Timeline(H, A, END, FPS); tl.stand(A, END, -0.42)
    tl.face(A, 0.0, lid="sono", lidv=0.6, brow=-4, mouth="reta", look=(0.0, 0.0))
    tl.face(F(t_f) + 1, 1.0, lid="esperto", lidv=0.45, brow=-18, browtilt=0.024, mouth="sorriso", look=(0.0, 0.0))   # "PCC": o fuzil cai na mão, cara de malvado
    tl.face(F(wt(1, "salário")), 1.0, lid="esperto", lidv=0.5, brow=-14, browtilt=0.02, mouth="sorriso", look=(1.0, -0.3))   # olha o dinheiro caindo
    tl.face(F(wt(1, "dia") - 0.25), 1.0, eye="cifrao", mouth="sorrisao", browup=0.015, extras=("brilho",))
    finish(H, tl, A, END)
    segura = dict(shF=30, elF=-110, wrF=0, shB=40, elB=-80, wrB=0)
    ft = F(t_f)                                                    # o fuzil bate na mão em "PCC"
    ant = dict(shF=-3, elF=6, wrF=0, shB=3, elB=0, wrB=0)           # antecipação: o braço cede um pouco antes de subir
    passa = dict(shF=36, elF=-120, wrF=-4, shB=46, elB=-88, wrB=0)   # sobe passando do ponto...
    frente.bracos(H, A, END, [(A, dict(shF=5, elF=0, shB=5, elB=0)), (ft - 22, dict(shF=5, elF=0, shB=5, elB=0)), (ft - 17, ant),
                              (ft - 8, passa), (ft - 2, segura)],                                  # ...e assenta na pegada
                  extras=[(ft, "shF", -9, 2.8, 0.28), (ft, "elF", -12, 2.8, 0.28), (ft + 1, "shB", -6, 2.8, 0.3), (ft + 1, "elB", -8, 2.8, 0.3)])
    ak = armas.ak47("ak", H.j["wrF"], (0.0, -0.06, -0.045), 1.0, rim=p["borda"])
    ak.rotation_euler = (0, math.radians(-30), 0)
    armas.cai_na_mao(ak, ft, altura=1.6, frames=11, afunda=0.09)
    cena.contact_shadow(H, dict(shadow=_mix(p["chao"], "#000000", 0.4)))
    # pedestal baixo e a pilha de notas verdes que sobe nota a nota (12 notas de R$ 100 = R$ 1.200); espessura exagerada
    # para a pilha ter volume e ser lida de longe
    px, py, ph = 0.3, -1.3, 0.66                                   # perto da câmera: maior no quadro, em outra camada de profundidade
    pedestal(p, "ped_a1", px, py - 0.2, 0.7, ph)
    t0 = wt(1, "salário") + 0.15; t1 = wt(1, "dia") - 0.05
    s_ = 2.6
    for k in range(12):
        n = G.maco(f"nota{k}", (px, py, ph + k * G.T * s_), n=1, s=s_)
        fk = F(t0 + (t1 - t0) * curvas.s("easy", k / 11))
        z_ = n.location.z
        props.blink_vis(n, [(A, False), (fk - 1, False), (fk, True)], True)
        for i in range(6):                                          # cai de 30 cm e assenta (acelerando)
            u = i / 5; n.location.z = z_ + 0.3 * (1 - u * u); key(n, "location", fk + i, "LINEAR")
    cam, rig = camera_movel(c, [(0.0, (-0.42, -2.0, 1.45), 0.0)], lens=40, focus=2.0, fstop=2.0)
    seguro(cam)
    baked_slide(cam, F(0.0), F(5.73), (-0.42, -2.0, 1.45), (-0.05, -5.4, 1.29))     # ele no 2/3 de baixo da área segura; o valor fica no alto
    cd = cam.data
    for t_, d_ in ((0.0, 2.0), (5.73, 5.4)):
        cd.dof.focus_distance = d_; cd.dof.keyframe_insert("focus_distance", frame=F(t_))
    TR.rampa_fim(cam, F(5.73), (0, 0, 1), CORTE_A1_A2[0], CORTE_A1_A2[1])     # sobe acelerando e corta no pico


# corte em movimento a1 -> a2: (delta em m na câmera de a1, quadros). Distâncias ao assunto: a1 5,4 m; a2 6,0 m
CORTE_A1_A2 = (1.75, 4)          # pico ~15% da tela por quadro, só 4 quadros de cada lado


# ====================================================================== A2. Cada degrau paga mais, mas tem mais risco (5,73 - 8,89)
@cena_("a2", 5.73, 8.89)
def a2(c):
    """a escada clara no fundo escuro; em "paga mais" cada degrau recebe um bloco de dinheiro verde, cada um maior
    que o anterior (o volume sobe); em "risco" o topo fica vermelho, piscando como sirene"""
    sc = c["sc"]; A, END = F(5.4), F(9.3)
    p = P; wy = 3.5
    pe = dict(p, mid=_mix(p["mid"], p["top"], 0.45), low=_mix(p["low"], p["top"], 0.35))
    fundo(pe, wy, z_meio=3.0, x=(-30, 30), z=(-4, 20))
    cena.disc("halo_a2", 5.0, cena.amat("halo_a2_m", p["halo"], 1.0, 0.4, ("radial", 1.5)), (2.4, wy - 0.1, 5.0))
    pd = dict(p, pedra=_mix(p["pedra"], p["aresta"], 0.28), mid=p["aresta"])
    degs = escada5(pd)
    for k, (r, n0, n1) in enumerate(degs):
        t = wt(2, "degrau") - 0.15 + 0.08 * k
        cresce(r, F(t), 7)
        surge(n1, F(t) + 5, 6)
        n0.scale = (0.0001,) * 3; key(n0, "scale", A, "CONSTANT")
    # um bloco de dinheiro por degrau, cada vez maior (cols x fundo x camadas), assentado na beira do degrau
    tam = [(1, 1, 3), (2, 1, 6), (2, 2, 12), (3, 2, 20), (4, 3, 32)]
    for k, (cc, ff, ll) in enumerate(tam):
        sw, sh = 0.95, 1.2
        xb = 0.0 + k * sw + sw * 0.5 if k < 4 else 4 * sw + 0.95
        b, larg = G.bloco(f"grana{k}", (xb, 0.35 - 0.01 * k, (k + 1) * sh), cc, ff, ll, s=2.6)
        G.cresce_bloco(b, F(wt(2, "paga") + 0.09 * k), F(wt(2, "paga") + 0.09 * k) + 7)
    # "risco": luz vermelha no topo, duas piscadas
    sir = cena.disc("sirene", 3.0, cena.amat("sirene_m", "#ff3b4a", 1.0, 0.0, ("radial", 1.4)), (4.4, 0.95, 6.6))
    sk = [n for n in sir.data.materials[0].node_tree.nodes if n.type == "MATH" and n.operation == "MULTIPLY"][0].inputs[1]
    tr = F(wt(2, "risco") - 0.25)
    for f_, a_ in ((tr - 1, 0.0), (tr + 3, 0.55), (tr + 7, 0.1), (tr + 10, 0.55), (tr + 16, 0.25), (END, 0.25)):
        sk.default_value = a_; sk.keyframe_insert("default_value", frame=f_)
    H = U.heroi_preso("heroi", "q", rim=p["borda"])
    tl = Timeline(H, A, END, FPS); tl.stand(A, END, -0.55)
    tl.intent(A, head=-12, torso=-2)
    tl.face(A, 0.0, browtilt=0.016, mouth="pequena", look=(0.7, 0.7))
    tl.face(F(wt(2, "paga")), 1.0, eye="cifrao", mouth="sorriso", browup=0.015, look=(0.7, 0.8))
    tl.face(F(wt(2, "risco")), 1.0, wide=0.7, brow=22, browup=0.02, mouth="nervosa", look=(0.8, 0.8), extras=("suor",))
    finish(H, tl, A, END)
    cena.contact_shadow(H, dict(shadow=_mix(p["chao"], "#000000", 0.4)))
    cam, rig = camera_movel(c, [(5.73, (0.4, -6.0, 2.4), 0.0)], lens=40, focus=6.0, fstop=4.0)
    seguro(cam)
    baked_slide(cam, F(5.73), F(8.89), (0.4, -6.0, 2.4), (2.6, -15.5, 3.4))
    TR.rampa_fim(cam, F(8.89), (1, 0, 0), 0.32 * 15.5, 4)                       # corte em movimento para b1 (lateral)
    TR.rampa_inicio(cam, F(5.73), (0, 0, 1), CORTE_A1_A2[0] * 6.0 / 5.4, CORTE_A1_A2[1])   # chega subindo, na mesma velocidade de tela


def main():
    argv = sys.argv[sys.argv.index("--") + 1:]
    arg = lambda n, d=None: argv[argv.index(n) + 1] if n in argv else d
    if "--list" in argv:
        for k, (a, b, _) in CENAS.items():
            print(f"{k:6s} {a:6.2f}-{b:6.2f}  quadros {F(a)}-{F(b) - 1}")
        return
    name, out = argv[0], argv[1]
    t0, t1, fn = CENAS[name]
    k = float(arg("--scale", "1.0"))
    reset(int(1080 * k), int(1920 * k), FPS, int(arg("--samples", "16")))
    sc = lib.scene
    c = dict(sc=sc, f0=F(t0), f1=F(t1) - 1, t0=t0, t1=t1, F=F)
    sc.frame_start, sc.frame_end = c["f0"], c["f1"]
    fn(c)
    os.makedirs(out, exist_ok=True)
    if "--at" in argv:
        for t in arg("--at").split(","):
            f = F(float(t)); sc.frame_set(f); sc.render.filepath = f"{out}/{name}_{f:04d}.png"; bpy.ops.render.render(write_still=True)
    else:
        sc.render.image_settings.file_format = "PNG"; sc.render.filepath = f"{out}/f_"
        bpy.ops.render.render(animation=True)


if __name__ == "__main__":
    main()
