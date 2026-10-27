"""Canal 38: "Você acabou de virar um presidente corrupto do Brasil" (ficção com esquemas reais; voz do Lucas, 83 s).
Plano aprovado: roteiros/decupagem-presidente.md. Todo número vira proporção com as unidades fixas (unidades.py):
notinha = 1 salário mínimo, maço (0,229 m) = R$ 1 milhão, cubo (2,29 m) = R$ 1 bilhão; o herói (1,75 m) é a régua.
Desenho simples: fundo de uma cor e uma luz, um objeto principal por plano.
blender -b -P prod_presidente.py -- CENA OUT [--scale 0.5] [--samples 10] [--at t1,t2] [--list]"""
import os, sys, json, math
os.environ["VOZ_NOVA"] = ""                         # os tempos já são os da voz deste vídeo (sem mapa de outra voz)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy, lib
from lib import *
import cena, props, luz, curvas, frente, uniforme as U, grana as G, area, transicao as TR, sets4 as S, unidades as UN, titulo3d as T3, ambiente3d as AM, elenco as EL, objetos as OB
import prod_pcc4 as P4
import prod_pcc6 as P6
from prod_pcc4 import F, FPS, finish, Timeline, P, _mix
from prod_pcc3 import escada5, cresce, surge
from char2d import rrect
from acting import Actor
from puppet2d import circle, stroke
import vida, rostos
P4.CENAS.clear()                                    # só as cenas deste vídeo
_finish = finish


def finish(H, tl, f0, f1, boil=True):
    """todo boneco respira, balança o peso e mexe a cabeça em onda por cima do que a cena animou (nunca fica parado)"""
    vida.vida_ator(tl, f0, f1, seed=sum(map(ord, H.name)))
    _finish(H, tl, f0, f1, boil)

VOZ = (__import__("canal38_env").RAIZ + "/roteiros/voz-presidente")
PAL = json.load(open(VOZ + "/palavras.json")); TEMPOS = json.load(open(VOZ + "/tempos.json"))
FALAS = [(f["inicio"], f["inicio"] + f["duracao"]) for f in TEMPOS["falas"]]
TOT = TEMPOS["total"]
B = [0.0] + [FALAS[k][0] - 0.12 for k in range(1, len(FALAS))] + [TOT]      # cortes: logo antes de cada fala


def wt(frase, txt, nth=0):
    ws = [w for w in PAL if w["frase"] == frase and w["txt"].strip(".,:;!?…").lower() == txt.lower()]
    return ws[nth]["t0"]


def cena_(k):
    """cena k (1 a 14) = fala k, do corte antes dela até o corte da próxima"""
    return P4.cena_(f"s{k:02d}", B[k - 1], B[k])


V = dict(
    palacio=dict(top="#1d2742", mid="#c7b089", low="#8c7653", chao="#4a3d2c", halo="#ffd08a", luz="#fff0d2", pedra="#b79e74", aresta="#fff1d4", borda="#ffd9a8"),
    plenario=dict(top="#0b120a", mid="#46603e", low="#24331f", chao="#18221a", halo="#ffbf66", luz="#ffe3b0", pedra="#58744f", aresta="#ffd99a", borda="#ffc98a"),
    supremo=dict(top="#121418", mid="#8b909a", low="#4b5059", chao="#2a2d33", halo="#eef4ff", luz="#ffffff", pedra="#a2a8b2", aresta="#ffffff", borda="#ffe4d0"),
    refinaria=dict(top="#03141a", mid="#0f4e5a", low="#082d35", chao="#051114", halo="#ff7b2e", luz="#ffb877", pedra="#125560", aresta="#86ecec", borda="#ff9e5a"),
    aco=dict(top="#080e18", mid="#3e5272", low="#1c2a42", chao="#0d1522", halo="#ff4a52", luz="#ffd6d0", pedra="#4c6488", aresta="#d6e4ff", borda="#ff8a8a"),
    obra=dict(top="#1d0c06", mid="#9c4a2c", low="#5a2616", chao="#3a1a10", halo="#7fe6ff", luz="#d8f8ff", pedra="#b5603a", aresta="#ffd8bf", borda="#9ff0ff"),
    obra_verm=dict(top="#160604", mid="#7a2e1c", low="#44160c", chao="#2a100a", halo="#ff4a3a", luz="#ffd0c8", pedra="#8f3a24", aresta="#ffc0b0", borda="#ff9a8a"),
    gabinete=dict(top="#0f0620", mid="#5a2c86", low="#2b1450", chao="#12082a", halo="#ffb070", luz="#ffd8b0", pedra="#6a3c9a", aresta="#e0b8ff", borda="#ffc890"),
    branco=dict(top="#1a1d24", mid="#b3b8c2", low="#6c717c", chao="#3a3e46", halo="#ffffff", luz="#ffffff", pedra="#c4c9d2", aresta="#ffffff", borda="#ffe6d6"),
    aeroporto=dict(top="#081a21", mid="#3a7f93", low="#1d4553", chao="#123039", halo="#ffd27a", luz="#fff1c8", pedra="#4e95a8", aresta="#d8f7ff", borda="#ffe0a0"),
    noite=dict(top="#070a1c", mid="#242a80", low="#111550", chao="#0b0d2c", halo="#ffb04a", luz="#ffd9a0", pedra="#343a98", aresta="#9aa4ff", borda="#ffc890"),
    sala=dict(top="#050506", mid="#2b2620", low="#16120e", chao="#0e0c0a", halo="#ffb560", luz="#ffd9a0", pedra="#3a332c", aresta="#ffcf90", borda="#ffc070"),
    galeria=dict(top="#050f0b", mid="#24503f", low="#10281f", chao="#0f1d17", halo="#ffcf8a", luz="#ffe9c8", pedra="#2f5d4b", aresta="#ffe0b0", borda="#ffd9a0"),
)


def pal(nome):
    return S.var(P, **V[nome]) if nome in V else P6.pal(nome)


def heroi(p, view, x, A, END, y=0.0, name="heroi", roupa="terno"):
    """o herói no tamanho real; de terno com a faixa (presidente) ou de uniforme listrado com X (no fim)"""
    if roupa == "terno":
        H, faixa = U.heroi_presidente(name, view, rim=p["borda"])
    else:
        H, faixa = U.heroi_preso(name, view, rim=p["borda"]), None
    w = empty(name + "_inv", None, (x, y, 0)); H.root.parent = w
    tl = Timeline(H, A, END, FPS); tl.stand(A, END, 0.0)
    cena.contact_shadow(H, dict(shadow=_mix(p["chao"], "#000000", 0.4)))
    return H, tl, w, faixa


def bracos_parados(H, A, END):
    frente.bracos(H, A, END, [(A, dict(shF=5, elF=0, shB=5, elB=0))])


def palco(p, wy, z_meio=2.2, escuro=0.15, halo=(0.0, 1.6, 2.6), feixe=None, END=200, x=(-30, 30), z=(-4, 30)):
    """fundo de uma cor com degradê, chão, halo atrás do assunto e (opcional) um feixe de luz de cima"""
    S.fundo(p, wy, z_meio=z_meio, x=x, z=z, escuro=escuro)
    hx, hz, hr = halo
    cena.disc(f"halo_{wy}", hr, cena.amat(f"halo_{wy}_m", p["halo"], 1.0, 0.38, ("radial", 1.5)), (hx, wy - 0.1, hz))
    if feixe:
        fx, fy, fh = feixe
        luz.feixe(f"feixe_{wy}", fx, fy, 0.0, fh, 1.6, 0.3, p["luz"], forca=1.1, frames=END, poeira=30, seed=int(wy * 10))


def mundo(p):
    bpy.context.scene.world.node_tree.nodes["Background"].inputs[0].default_value = (*lib.srgb(p["top"]), 1)


def sombra_cubo(name, x, y, lado, p):
    cena.ground_disc(name, lado * 0.62, lado * 0.32, cena.amat(name + "_m", "#000000", 1.0, 0.35, ("radial", 1.1)), (x, y + 0.05, 0.003), n=40)


# ====================================================================== 1. Você acabou de virar presidente (fala 1)
@cena_(1)
def s01(c):
    """salão do palácio na penumbra, luz de janelas altas. Close no rosto -> de baixo: a faixa cai e o título 3D quica acima dele
    -> inserto do salário pequeno na mesa -> aberto de baixo: o cubo de 1 bilhão sobe atrás dele; o título some no corte"""
    A, END = F(-0.4), F(B[1] + 0.4)
    p = pal("palacio"); wy = 12.0
    mundo(p)
    AM.sala("hall", -4.2, 4.2, -16.0, wy, 7.0, dict(parede="#8f7a58", lateral="#6f5d42", teto="#211910", viga="#2e2318", chao="#9a8664",
            linha="#86734f", pilastra="#837051"), piso="lajotas", passo_pilastra=2.0, passo_viga=2.0)
    props.poly("porta_fundo", rrect(-1.6, 0.0, 1.0, 4.6, 0.08, 4), "#ffe7bd", wy - 0.02)          # o portal aceso no fim do salão
    cena.disc("porta_gl", 3.6, cena.amat("porta_gl_m", "#ffd9a0", 1.0, 0.35, ("radial", 1.5)), (-0.3, wy - 0.05, 2.3))
    for s in (-1, 1):
        AM.colunata(f"col{s}", s * 2.6, 1.6, wy - 1.0, 2.6, 6.8, "#d6c9ae")
        for k, yj in enumerate((2.0, 4.0, 6.0, 8.0, 10.0)):
            AM.janela_lateral(f"jan{s}_{k}", s * 4.2, yj, 2.6, 6.0, 0.9, "#fff0d2", lado=s)
    luz.feixe("feixe_j0", -1.6, 3.0, 0.0, 6.5, 2.0, 0.9, p["luz"], forca=0.8, rot=-0.4, frames=END, poeira=25, seed=31)
    luz.feixe("feixe_j1", 1.4, 5.0, 0.0, 6.5, 2.0, 0.9, p["luz"], forca=0.7, rot=0.4, frames=END, poeira=20, seed=32)
    AM.tapete("tapete1", -0.35, -16.0, wy - 0.5, 1.4, "#4e1820", borda="#a88a4e")
    for yv in (4.0, 8.0):
        S.neblina(p, yv, 0.14)
    S.coluna_fg(p, "col_fg1", -2.15, -1.9, w=0.18)
    OB.bandeira_brasil("band1", (-2.05, 2.6, 0.0), 1.1)
    OB.cadeira_presidencial("cad1", (-1.0, 4.4, 0.0), 1.05)
    cena.ground_disc("vinheta1", 6.0, 5.0, cena.amat("vinheta1_m", "#000000", 1.0, 0.45, ("radial", 0.8)), (-0.3, -8.0, 0.006), n=48)
    H, tl, w, faixa = heroi(p, "front", -0.35, A, END)
    fp = F(wt(1, "presidente")) + 2
    faixa.scale = (0.0001,) * 3; key(faixa, "scale", fp - 8, "CONSTANT")
    faixa.scale = (1, 1, 1); key(faixa, "scale", fp - 7, "CONSTANT")
    for k in range(20):
        z = 0.9 * (1 - curvas.s("queda", k / 7)) if k <= 7 else -0.03 * curvas.pancada((k - 7) / 24.0, 3.0, 0.32)
        faixa.location = (0, 0, z); key(faixa, "location", fp - 7 + k, "LINEAR")
    fd = F(wt(1, "dinheiro"))
    tl.face(A, 0.0, lid="sono", lidv=0.55, brow=-2, mouth="reta", look=(0.0, 0.0))
    tl.face(fp + 1, 1.0, lid="esperto", lidv=0.45, brow=-18, browtilt=0.024, mouth="sorriso", look=(0.0, 0.0))
    tl.face(F(wt(1, "salário")), 1.0, lid="esperto", lidv=0.5, brow=-6, mouth="lado", look=(-1.0, -0.5))
    tl.face(fd, 1.0, eye="cifrao", mouth="sorrisao", browup=0.015, extras=("brilho",), look=(0.3, 0.3))
    finish(H, tl, A, END)
    junta = dict(shF=30, elF=-100, wrF=0, shB=30, elB=-100, wrB=0)
    frente.bracos(H, A, END, [(A, dict(shF=5, elF=0, shB=5, elB=0)), (fd - 10, dict(shF=4, elF=4, shB=4, elB=4)), (fd - 4, dict(shF=-3, elF=8, shB=-3, elB=8)),
                              (fd + 6, dict(shF=36, elF=-108, shB=36, elB=-108)), (fd + 12, junta)],
                  extras=[(fd + 12, "shF", -5, 2.8, 0.3), (fd + 12, "shB", -5, 2.8, 0.3)])
    # título 3D do episódio acima dele: cai letra por letra com bounce em "corrupto" e some antes do corte
    letras = T3.titulo("tit", ["PRESIDENTE", "CORRUPTO"], (-0.35, 1.2, 2.75), tamanho=0.3, face="#f6efe2", lado="#5a2a1a")
    T3.bounce_in(letras, F(wt(1, "corrupto")) - 2, passo=1.3)
    T3.some(letras, F(B[1]) - 9)
    # o salário: pouco, numa mesa à esquerda
    S.caixa3d(p, "mesa1", -1.35, -0.45, 1.0, 0.78, d=0.5, cor="#3a2a1e", tampo="#7a5638", aresta=p["aresta"])
    pil = G.maco("salario", (-1.35, -0.3, 0.78), n=4, s=2.8, zk=2.0)
    UN.pop(pil, F(wt(1, "salário")) - 2, 7)
    # o dinheiro de verdade: o cubo de 1 bilhão sobe do chão atrás dele
    cb = UN.cubo("cubo1", (1.15, 3.1, 0.0)); sombra_cubo("cubo1_sb", 1.15, 3.1, UN.CUBO, p)
    UN.sobe_do_chao(cb, fd, 12)
    t1, t2, t3 = wt(1, "presidente") - 0.08, wt(1, "seu") - 0.05, wt(1, "o", 2) - 0.05
    P6.planos(c, [
        dict(t0=B[0], t1=t1, caixa0=(-0.75, 0.05, 1.35, 1.98, 0.0), caixa1=(-0.68, -0.02, 1.42, 1.95, 0.0), lens=55, fstop=1.6),
        dict(t0=t1, t1=t2, caixa0=(-1.0, 0.3, 0.5, 3.0, 0.0), caixa1=(-1.25, 0.55, -0.1, 3.1, 0.0), lens=32, fstop=2.2, alt0=0.6, alt1=1.1,
             chaves_fim=["tit_0_0", "tit_0_9"]),
        dict(t0=t2, t1=t3, caixa0=(-1.66, -1.04, 0.74, 1.06, -0.45), caixa1=(-1.62, -1.08, 0.75, 1.05, -0.45), lens=60, fstop=1.6, alt0=1.15, alt1=1.1),
        dict(t0=t3, t1=B[1], caixa0=(-1.3, 2.3, -0.1, 3.1, 0.4), caixa1=(-1.7, 2.5, -0.1, 3.5, 0.6), lens=30, fstop=3.0, preenche=0.86, alt0=0.5, alt1=1.8,
             chaves=["heroi_inv"]),
    ], sai="v")


# ====================================================================== 2. Quanto mais dinheiro, maior o risco (fala 2)
@cena_(2)
def s02(c):
    A, END = F(B[1] - 0.4), F(B[2] + 0.4)
    p = P; wy = 3.5
    pe = dict(p, mid=_mix(p["mid"], p["top"], 0.4), low=_mix(p["low"], p["top"], 0.3))
    P4.fundo(pe, wy, z_meio=3.0, x=(-30, 30), z=(-4, 20))
    cena.disc("halo_s2", 5.0, cena.amat("halo_s2_m", p["halo"], 1.0, 0.35, ("radial", 1.5)), (2.4, wy - 0.1, 5.0))
    pd = dict(p, pedra=_mix(p["pedra"], p["aresta"], 0.28), mid=p["aresta"])
    degs = escada5(pd)
    for k, (r, n0, n1) in enumerate(degs):
        cresce(r, A + 1 + 2 * k, 6)
        surge(n1, A + 6 + 2 * k, 6)
        n0.scale = (0.0001,) * 3; key(n0, "scale", A, "CONSTANT")
    lados = [0.38, 0.52, 0.66, 0.8, 0.94]                       # um cubo por degrau, cada vez maior
    t_d = wt(2, "dinheiro")
    for k, l in enumerate(lados):
        xb = k * 0.95 + 0.475 if k < 4 else 4 * 0.95 + 0.95
        cb = UN.cubo(f"cdeg{k}", (xb, 0.75, (k + 1) * 1.2), l)
        UN.sobe_do_chao(cb, F(t_d + 0.1 * k), 7)
    sir = cena.disc("sirene", 3.0, cena.amat("sirene_m", "#ff3b4a", 1.0, 0.0, ("radial", 1.4)), (4.4, 0.95, 6.6))
    sk = [n for n in sir.data.materials[0].node_tree.nodes if n.type == "MATH" and n.operation == "MULTIPLY"][0].inputs[1]
    tr = F(wt(2, "risco") - 0.2)
    for f_, a_ in ((tr - 1, 0.0), (tr + 3, 0.55), (tr + 7, 0.1), (tr + 10, 0.55), (tr + 16, 0.25), (END, 0.25)):
        sk.default_value = a_; sk.keyframe_insert("default_value", frame=f_)
    cena.disc("halo_heroi2", 1.0, cena.amat("halo_heroi2_m", "#9a86c8", 1.0, 0.8, ("radial", 1.3)), (-0.75, 0.5, 1.2))
    H, tl, w, faixa = heroi(p, "q", -0.75, A, END)
    tl.intent(A, head=-12, torso=-2)
    tl.face(A, 0.0, lid="esperto", lidv=0.5, mouth="sorriso", look=(0.7, 0.7))
    tl.face(F(t_d), 1.0, eye="cifrao", mouth="sorrisao", browup=0.015, look=(0.7, 0.8))
    tl.face(F(wt(2, "risco")), 1.0, wide=0.7, brow=22, browup=0.02, mouth="nervosa", look=(0.8, 0.8), extras=("suor",))
    finish(H, tl, A, END)
    P6.planos(c, [
        dict(t0=B[1], t1=B[2], caixa0=(-1.3, 6.3, -0.1, 7.1, 0.6), caixa1=(-1.2, 6.3, 0.0, 7.2, 0.6), lens=32, fstop=4.0, preenche=0.9,
             alt0=1.6, alt1=4.2, chaves=["heroi_inv", "cdeg4"]),
    ], entra="v", sai="h")


# ====================================================================== 3. Comprar o Congresso (fala 3)
@cena_(3)
def s03(c):
    """negociação numa sala escura: uma luz só pendurada sobre a mesa entre ele e o deputado; gente em silhueta ao fundo olhando.
    Aberto por cima do ombro -> inserto do envelope deslizando para a luz -> close no rosto dele -> inserto dos 30 mil ->
    as 100 notinhas (100 salários mínimos) sobem e formam a grade sobre a mesa; em "todo mês", outro envelope desliza"""
    A, END = F(B[2] - 0.4), F(B[3] + 0.4)
    p = pal("sala"); wy = 4.5
    mundo(p)
    AM.sala("sala3", -3.6, 3.6, -14.0, wy, 4.0, dict(parede="#7a6450", lateral="#6a5644", teto="#120e0b", viga="#1e1812", chao="#120e0b",
            linha="#0a0806", pilastra="#7e6852"), piso="tabuas", passo_pilastra=1.5, passo_viga=1.2)
    cena.ground_disc("vinheta3", 6.0, 5.0, cena.amat("vinheta3_m", "#000000", 1.0, 0.5, ("radial", 0.8)), (0.0, -7.5, 0.004), n=48)
    AM.persiana("persiana", 0.0, wy, 1.2, 3.0, 2.6, "#7fa8d8", "#141a24")          # luz fria lá fora: as silhuetas vêm contra ela
    cena.disc("persiana_gl", 2.4, cena.amat("persiana_gl_m", "#7fa8d8", 1.0, 0.22, ("radial", 1.5)), (0.0, wy - 0.05, 2.1))
    props.poly("fio_lampada", cena.rect(-0.012, 3.55, 0.012, 4.0), "#0a0908", 0.74)
    props.inked("cupula", [(-0.32, 3.38), (0.32, 3.38), (0.16, 3.62), (-0.16, 3.62)], "#1a1612", None, (0, 0.74, 0), w=0.0)
    props.poly("cupula_luz", cena.rect(-0.3, 3.36, 0.3, 3.4), p["luz"], 0.735)
    luz.feixe("feixe_mesa", 0.0, 0.76, 0.0, 3.38, 2.2, 0.55, p["luz"], forca=1.7, frames=END, poeira=45, seed=53)
    cena.disc("halo_lamp", 0.9, cena.amat("halo_lamp_m", p["halo"], 1.2, 0.5, ("radial", 1.4)), (0.0, 0.72, 3.4))
    vida.pendulo(["fio_lampada", "cupula", "cupula_luz", "halo_lamp", "feixe_mesa"], (0.0, 0.74, 4.0), A, END, amp_deg=1.8, periodo=3.4)
    S.caixa3d(p, "mesa3", 0.0, 0.35, 1.5, 0.78, d=0.8, cor="#8a6240", tampo="#e0aa6c", aresta="#fff0d8")
    for i, (x, y) in enumerate(((-2.4, 2.4), (-1.6, 3.0), (-0.7, 3.7), (0.15, 3.85), (0.95, 3.6), (1.7, 3.0), (2.45, 2.4))):
        props.pessoa(f"olha{i}", x, y, "#0c0a08", 1.0, flip=1 if x < 0 else -1, head_c="#070605", rim=_mix(p["borda"], p["top"], 0.55))
    S.neblina(p, 2.2, 0.16)
    # halo de luz atrás dos dois (contraste: figura escura sobre fundo claro, como no palácio; medido em contraste.py, >= 3:1)
    cena.disc("halo_heroi3", 1.1, cena.amat("halo_heroi3_m", "#a07c56", 1.0, 0.75, ("radial", 1.3)), (-1.0, 1.6, 1.35))
    cena.disc("halo_dep3", 1.1, cena.amat("halo_dep3_m", "#c19468", 1.0, 0.75, ("radial", 1.3)), (1.0, 1.6, 1.35))
    H, tl, w, faixa = heroi(p, "q", -1.0, A, END, y=0.75)
    Hd, tld, dep = ator(EL.deputado, "deputado", "q", 1.0, 0.75, A, END, espelho=True, p=p, objeto=None)
    OB.charuto("charuto3", (-0.48, 0.55, 0.78), 1.3)
    omb = S.ombro(p, "ombro3", -1.35, -2.6, 1.4, s=1.25)
    omb2 = S.ombro(p, "ombro3b", 1.45, -2.9, 1.45, s=1.25, flip=-1)
    t_b = wt(3, "começa") - 0.1
    S.mostra(omb, [(A, F(t_b))]); S.mostra(omb2, [(A, F(t_b))])
    def envelope(nome, f, p0, p1):
        e = OB.envelope(nome, p0, 0.95)
        UN.esconde_ate(e, f - 8)
        for ff in range(f - 8, f + 20):
            u = UN.onda_mola((ff - f) / 11)
            e.location = tuple(a + (b - a) * u for a, b in zip(p0, p1)); key(e, "location", ff, "LINEAR")
        return e
    fpg = F(wt(3, "pagar"))
    envelope("envelope", fpg, (-0.62, 0.6, 0.79), (0.45, 0.6, 0.79))
    ftd = F(wt(3, "todo"))
    envelope("envelope2", ftd, (-0.62, 0.62, 0.79), (0.3, 0.62, 0.79))
    # ele empurra o envelope (antecipa, estica e volta), sorri; no close, cara de quem compra
    tl.face(A, 0.0, lid="esperto", lidv=0.5, brow=-10, mouth="reta", look=(1.0, -0.1))
    tl.face(fpg - 4, 1.0, lid="esperto", lidv=0.45, brow=-14, browtilt=0.02, mouth="sorriso", look=(1.0, -0.4))
    tl.face(F(wt(3, "Mensalão")), 1.0, lid="esperto", lidv=0.4, brow=-18, browtilt=0.026, mouth="lado", look=(1.0, 0.0))
    tl.face(F(wt(3, "100")), 1.0, eye="cifrao", mouth="sorrisao", browup=0.015, extras=("brilho",), look=(0.6, 0.6))
    for f0 in (fpg, ftd):
        tl.intent(f0 - 10, shF=-6, elF=70, wrF=0); tl.intent(f0 - 2, shF=58, elF=28, wrF=8); tl.intent(f0 + 14, shF=12, elF=60, wrF=0)
    tl.intent(F(wt(3, "Mensalão")), head=4, torso=3)
    finish(H, tl, A, END)
    tld.face(A, 0.0, lid="esperto", lidv=0.5, brow=-8, mouth="reta", look=(1.0, -0.2))
    tld.face(fpg + 10, 1.0, lid="esperto", lidv=0.45, brow=-14, browtilt=0.02, mouth="sorriso", look=(1.0, -0.5))
    tld.face(F(wt(3, "30")), 1.0, eye="cifrao", mouth="sorrisao", browup=0.015, extras=("brilho",), look=(0.6, -0.5))
    tld.face(F(wt(3, "todo")), 1.0, lid="esperto", lidv=0.4, brow=-16, mouth="lado", look=(1.0, -0.4))
    tld.intent(fpg + 6, shF=40, elF=50, wrF=6); tld.intent(fpg + 18, shF=10, elF=70, wrF=0)
    fim_ator(Hd, tld, A, END)
    # os 30 mil na mesa, do lado do deputado
    f30 = F(wt(3, "30"))
    pilha = G.maco("pilha30", (0.42, 0.55, 0.78), n=3, s=2.6, zk=3.0)
    UN.pop(pilha, f30, 7)
    # 100 salários mínimos: as 100 notinhas sobem da pilha e formam a grade na luz, uma a uma (100 tiques)
    f100 = F(wt(3, "100"))
    for k in range(100):
        r, i = divmod(k, 10)
        alvo = (-0.81 + i * 0.18, 0.62, 2.78 - r * 0.092)
        nt = UN.notinha(f"n100_{k}", (0.42, 0.6, 0.86), 1.0)
        fk = f100 + int(k * 0.3)
        UN.esconde_ate(nt, fk)
        UN.voa(nt, fk, fk + 8, (0.42, 0.6, 0.86), alvo, alt=0.15)
    t2, t3, t4, t5 = t_b, wt(3, "Mensalão") - 0.1, wt(3, "30") - 0.1, wt(3, "100") - 0.12
    P6.planos(c, [
        dict(t0=B[2], t1=t2, caixa0=(-2.6, 2.6, -0.1, 3.8, 0.75), caixa1=(-1.45, 1.45, 0.2, 2.9, 0.75), lens=32, fstop=2.0, chaves_fim=["heroi_inv", "deputado_inv"]),
        dict(t0=t2, t1=t3, caixa0=(-0.9, 0.9, 0.55, 1.35, 0.35), caixa1=(-0.75, 0.8, 0.6, 1.3, 0.35), lens=50, fstop=1.6, alt0=3.0, alt1=1.4),
        dict(t0=t3, t1=t4, caixa0=(-1.5, -0.68, 1.2, 1.98, 0.75), caixa1=(-1.32, -0.5, 1.28, 1.95, 0.75), lens=55, fstop=1.6),
        # os 30 mil com o deputado inteiro (rosto inteiro no quadro, nunca cortado no meio): o olho vira cifrão olhando a pilha
        dict(t0=t4, t1=t5, caixa0=(0.05, 1.6, 0.62, 2.0, 0.75), caixa1=(0.15, 1.55, 0.66, 1.98, 0.75), lens=55, fstop=1.6),
        dict(t0=t5, t1=B[3], caixa0=(-1.2, 1.2, 0.7, 2.95, 0.75), caixa1=(-1.65, 1.65, 0.2, 3.3, 0.75), lens=35, fstop=2.6, alt0=1.6, alt1=2.3,
             chaves_fim=["n100_0", "n100_99"]),
    ], entra="h", sai="h")


# ====================================================================== elenco e câmera livre (v3: ficha aprovada)
def ator(fn, nome, view, x, y, A, END, espelho=False, escala=1.0, p=None, **kw):
    """um personagem da ficha (elenco.py) em cena: rosto vivo, expressões e Timeline como o herói.
    espelho=True vira o boneco para a esquerda (o de 3/4 olha para a direita)"""
    H = fn(nome, view, **kw)
    w = empty(nome + "_inv", None, (x, y, 0)); H.root.parent = w
    w.scale = (-escala if espelho else escala, escala, escala)
    tl = Timeline(H, A, END, FPS); tl.stand(A, END, 0.0)
    cena.contact_shadow(H, dict(shadow=_mix((p or P)["chao"], "#000000", 0.4)))
    return H, tl, w


def fim_ator(H, tl, A, END):
    finish(H, tl, A, END)
    if H.view == "front":
        bracos_parados(H, A, END)


def camera_livre(c, nome, t0, t1, p0, p1, alvo, lens=40, fstop=4.0):
    """câmera que pode girar (só para planos sem boneco: objetos vistos de cima em 3/4).
    Olha sempre para 'alvo'; desliza de p0 a p1 na curva easy; entra por marcador em t0"""
    from mathutils import Vector
    sc = c["sc"]
    cd = bpy.data.cameras.new(nome); cam = bpy.data.objects.new(nome, cd); sc.collection.objects.link(cam)
    cd.lens = lens; cd.sensor_fit = "HORIZONTAL"; cd.sensor_width = 24
    cd.dof.use_dof = True; cd.dof.aperture_fstop = fstop
    fa, fb = F(t0), F(t1)
    for f in range(fa - 1, fb + 2):
        u = curvas.s("easy", min(1.0, max(0.0, (f - fa) / max(1, fb - fa))))
        pos = Vector(tuple(a + (b - a) * u for a, b in zip(p0, p1)))
        cam.location = pos
        cam.rotation_euler = (Vector(alvo) - pos).to_track_quat("-Z", "Y").to_euler()
        key(cam, "location", f, "LINEAR"); key(cam, "rotation_euler", f, "LINEAR")
        cd.dof.focus_distance = (Vector(alvo) - pos).length; cd.dof.keyframe_insert("focus_distance", frame=f)
    m = sc.timeline_markers.new(nome, frame=fa); m.camera = cam
    return cam


def martelada_juiz(tl, f):
    """o juiz levanta o martelo (antecipação), bate e assenta: o braço da frente faz o arco"""
    tl.intent(f - 12, shF=20, elF=50, wrF=0)
    tl.intent(f - 5, shF=128, elF=70, wrF=-10)
    tl.intent(f, shF=52, elF=22, wrF=12)
    tl.intent(f + 8, shF=58, elF=30, wrF=6); tl.intent(f + 24, shF=22, elF=55, wrF=0)   # bate e recolhe o braço


# ====================================================================== peças de cena comuns (v2: ambientes 3D, contraste medido)
def halo(nome, x, y, z, r=1.0, cor="#a07c56", alfa=0.75):
    """luz atrás de quem precisa aparecer: figura escura sobre fundo claro (contraste >= 3:1, contraste.py)"""
    return cena.disc(nome, r, cena.amat(nome + "_m", cor, 1.0, alfa, ("radial", 1.3)), (x, y, z))


def martelada(piv, f, ang=38):
    """o martelo do juiz levanta (antecipação) e bate, com mola no impacto"""
    for k in range(-9, 14):
        if k < 0:
            a = ang * curvas.s("easy", (k + 9) / 9)
        elif k <= 3:
            a = ang * (1 - curvas.s("queda", k / 3))
        else:
            a = -4 * curvas.pancada((k - 3) / 24.0, 3.2, 0.35)
        piv.rotation_euler = (0, math.radians(a), 0); key(piv, "rotation_euler", f + k, "LINEAR")


def tribunal(nm, p, A, END, ox=0.0, wy=6.0):
    """o plenário do Supremo: salão de pedra em tom médio, janelão de luz fria atrás da bancada alta e os ministros
    (juízes e juízas da ficha, com rosto) contra a luz. Devolve o presidente da corte (de 3/4, com o martelo na mão)."""
    AM.sala(nm, ox - 4.5, ox + 4.5, -14.0, wy, 7.0, dict(parede="#8a909c", lateral="#6e7480", teto="#16181d", viga="#22252b", chao="#3a3e46",
            linha="#2c3036", pilastra="#a2a8b4"), piso="lajotas", passo_pilastra=2.2, passo_viga=0)
    props.poly(nm + "_janelao", rrect(ox - 2.6, 1.7, ox + 2.6, 6.2, 0.06, 3), "#eef3fb", wy - 0.02)
    for k in range(1, 4):
        props.poly(f"{nm}_mul{k}", cena.rect(ox - 2.6 + k * 1.3 - 0.04, 1.7, ox - 2.6 + k * 1.3 + 0.04, 6.2), "#8a909c", wy - 0.03)
    cena.disc(nm + "_gl", 3.4, cena.amat(nm + "_gl_m", "#eef3fb", 1.0, 0.3, ("radial", 1.5)), (ox, wy - 0.05, 3.8))
    luz.feixe(nm + "_fx", ox, wy - 1.5, 0.0, 6.0, 3.0, 1.6, "#eef3fb", forca=0.7, frames=END, poeira=25, seed=61)
    OB.bandeira_brasil(nm + "_band", (ox - 3.6, wy - 0.6, 0.0), 1.1)
    S.caixa3d(p, nm + "_banc", ox, 3.6, 4.8, 1.45, d=0.9, cor="#4a3020", tampo="#8a6040", aresta="#ffe4c8")
    S.caixa3d(p, nm + "_bloco", ox + 0.55, 3.62, 0.22, 0.06, d=0.15, base=1.45, cor="#3a2416", tampo="#6a4228", aresta="#ffe4c8")
    tipos = [EL.juiza, EL.juiz, None, EL.juiza, EL.juiz]
    for i, fn in enumerate(tipos):
        x = ox + (-2.1, -1.2, 0.0, 1.45, 2.25)[i]                          # o presidente da corte bate o martelo no meio: espaço para o braço
        if fn is None:
            continue
        Hj, tlj, wj = ator(fn, f"{nm}_min{i}", "front", x, 4.15, A, END, p=p, objeto=None)
        wj.location.z = 0.6                                                  # no estrado: o tronco aparece acima da bancada
        tlj.face(A, 0.0, lid="apertado", lidv=0.6, brow=-10, mouth="reta", look=(0.6 if x < ox else -0.6, -0.3))
        fim_ator(Hj, tlj, A, END)
    Hp, tlp, wp = ator(EL.juiz, nm + "_pres", "q", ox, 4.15, A, END, p=p, objeto="martelo")
    wp.location.z = 0.6
    S.caixa3d(p, nm + "_estrado", ox, 3.95, 4.8, 0.6, d=0.8, cor="#3a2416", tampo="#5a3a22")
    tlp.face(A, 0.0, lid="bravo", brow=-18, mouth="reta", look=(1.0, -0.4))
    return Hp, tlp


def salao_palacio(nm, p, ox=0.0, wy=12.0, END=200):
    """o mesmo salão do palácio da abertura (colunas, janelas altas, tapete), para as cenas que voltam ao palácio"""
    AM.sala(nm, ox - 4.2, ox + 4.2, -16.0, wy, 7.0, dict(parede="#8f7a58", lateral="#6f5d42", teto="#211910", viga="#2e2318", chao="#9a8664",
            linha="#86734f", pilastra="#837051"), piso="lajotas", passo_pilastra=2.0, passo_viga=2.0)
    props.poly(nm + "_porta", rrect(ox - 1.6, 0.0, ox + 1.0, 4.6, 0.08, 4), "#ffe7bd", wy - 0.02)
    for s in (-1, 1):
        AM.colunata(f"{nm}_col{s}", ox + s * 2.6, 1.6, wy - 1.0, 2.6, 6.8, "#d6c9ae")
    AM.tapete(nm + "_tap", ox - 0.35, -16.0, wy - 0.5, 1.4, "#4e1820", borda="#a88a4e")
    for yv in (4.0, 8.0):
        S.neblina(p, yv, 0.14)


def viga_obra(nm, x, y, h, cor):
    props.poly(nm, cena.rect(x - 0.1, 0, x + 0.1, h), cor, y)


def fatia(name, loc, esp, lado):
    """a fatia fina de um cubo de dinheiro (3% = 30 milhões): frente com as folhas, lateral e tampo"""
    h = lado / 2; Pp = []
    Pp.append(([(0, -h, 0), (esp, -h, 0), (esp, -h, lado), (0, -h, lado)], UN.FRENTE))
    Pp.append(([(esp, -h, 0), (esp, h, 0), (esp, h, lado), (esp, -h, lado)], UN.LADO))
    Pp.append(([(0, -h, lado), (esp, -h, lado), (esp, h, lado), (0, h, lado)], UN.TAMPO))
    Pp.append(([(0, -h - 0.002, lado - 0.03), (esp, -h - 0.002, lado - 0.03), (esp, -h - 0.002, lado), (0, -h - 0.002, lado)], UN.ARESTA))
    root = empty(name, None, loc)
    o = G._malha(name + "_m", Pp, None); o.parent = root
    return root


def guindaste(p, name, x, y, h=7.0, braco=4.0, flip=1):
    cor = _mix(p["top"], p["mid"], 0.35)
    props.poly(name + "_t", cena.rect(x - 0.12, 0, x + 0.12, h), cor, y)
    props.poly(name + "_b", cena.rect(x - 0.6 * flip if flip > 0 else x, h - 0.15, x + braco * flip if flip > 0 else x + 0.6, h + 0.05) if flip > 0 else
               cena.rect(x - braco, h - 0.15, x + 0.6, h + 0.05), cor, y)
    props.poly(name + "_c", cena.rect(x + braco * 0.8 * flip - 0.01, h - 1.6, x + braco * 0.8 * flip + 0.01, h - 0.15), cor, y)


# ====================================================================== 4. Chegou ao Supremo: 25 condenados (fala 4)
@cena_(4)
def s04(c):
    """avanço pelo plenário até a bancada (juízes contra a luz) -> martelo bate em "terminou" -> as 25 pessoas em degraus, a grade desce"""
    A, END = F(B[3] - 0.4), F(B[4] + 0.4)
    p = pal("supremo"); mundo(p)
    Hp, tlp = tribunal("trib", p, A, END)
    ft = F(wt(4, "terminou")) + 2
    martelada_juiz(tlp, ft)
    tlp.face(ft - 5, 1.0, lid="bravo", brow=-26, mouth="dentes", look=(1.0, -0.6))
    fim_ator(Hp, tlp, A, END)
    ox = 14.0
    AM.sala("ala", ox - 4.0, ox + 4.0, -8.0, 4.5, 6.0, dict(parede="#9aa0aa", lateral="#7c828e", teto="#16181d", viga="#22252b", chao="#3a3e46",
            linha="#2c3036", pilastra="#b0b6c0"), piso="lajotas", passo_pilastra=2.0, passo_viga=0)
    t25 = wt(4, "25"); k = 0
    for r in range(5):
        for i in range(5):
            x = ox - 1.36 + i * 0.68 + (0.34 if r % 2 else 0.0) - 0.17
            y = 0.6 + r * 0.55; z = r * 0.32
            if r > 0:
                S.caixa3d(p, f"degrau{r}_{i}", x, y - 0.1, 0.7, z, d=0.55, cor="#5a606c", tampo="#8a909c")
            fn = (EL.deputado, EL.empreiteiro, EL.contador)[(r + i) % 3]
            Hr, tlr, g = ator(fn, f"reu{r}_{i}", "front", x, y, A, END, escala=0.82, p=p, objeto=None)
            g.location.z = z
            tlr.face(A, 0.0, lid="triste", lidv=0.35, brow=18, mouth="triste", look=(0.0, -0.3))
            tlr.face(F(wt(4, "condenados")), 1.0, eye="ponto", brow=26, browup=0.02, mouth="o", look=(0.0, 0.3))
            fim_ator(Hr, tlr, A, END)
            UN.pop(g, F(t25 - 0.25) + k // 2, 5, 0.82); k += 1
    gr = props.grade("grade25", ox - 1.9, ox + 1.9, 0.0, 3.4, 0.25, "#0d0f12", n=12, w=0.05, rails=0)
    for z in (0.0, 3.3):
        props.poly(f"grade25_t{z}", cena.rect(ox - 1.9, z, ox + 1.9, z + 0.1), "#0d0f12", -0.001, gr)
    fc = F(wt(4, "condenados"))
    UN.esconde_ate(gr, fc - 9)
    gr.location.z = 4.5; key(gr, "location", fc - 9, "LINEAR")
    for f in range(fc - 8, fc + 1):
        gr.location.z = 4.5 * (1 - curvas.s("queda", (f - (fc - 8)) / 8)); key(gr, "location", f, "LINEAR")
    for kk in range(8):
        gr.location.z = 0.05 * curvas.pancada(kk / 24.0, 3.0, 0.35); key(gr, "location", fc + 1 + kk, "LINEAR")
    t1, t2 = wt(4, "Supremo") - 0.05, wt(4, "com") - 0.1
    P6.planos(c, [
        dict(t0=B[3], t1=t1, caixa0=(-3.2, 3.2, -0.1, 6.3, 3.6), caixa1=(-2.3, 2.3, 0.9, 5.4, 3.6), lens=30, fstop=4.0, alt0=1.0, alt1=1.9),
        dict(t0=t1, t1=t2, caixa0=(-0.6, 0.95, 1.55, 3.05, 4.15), caixa1=(-0.5, 0.85, 1.65, 3.0, 4.15), lens=50, fstop=1.8, alt0=2.35, alt1=2.3),
        dict(t0=t2, t1=B[4], caixa0=(ox - 1.95, ox + 1.95, -0.1, 3.45, 0.4), caixa1=(ox - 1.8, ox + 1.8, 0.0, 3.4, 0.4), lens=35, fstop=3.2, chaves_fim=["grade25"]),
    ], entra="h", sai="h")


# ====================================================================== 5. A estatal: aliados, 1% a 3%, 30 milhões de 1 bilhão (fala 5)
def capacete(nm, raiz):
    props.poly(nm, [(-0.15 + 0.3 * k / 12 - 0.0, 1.74 + 0.13 * math.sin(math.pi * k / 12)) for k in range(13)], "#f2f2ee", -0.004, raiz)


@cena_(5)
def s05(c):
    """refinaria à noite em profundidade (torres e luzes recuando, chama ao fundo). Ele põe aliados de capacete ->
    inserto do contrato: de 100 partes, 3 saem pelo lado -> close: "parece pouco?" -> o cubo de 1 bilhão cai e a fatia de 3% vai para o bolso"""
    A, END = F(B[4] - 0.4), F(B[5] + 0.4)
    p = pal("refinaria"); mundo(p); wy = 18.0
    S.fundo(p, wy, z_meio=3.5, x=(-40, 40), z=(-4, 34), escuro=0.0)
    AM.patio("pat5", -9.0, 9.0, -16.0, wy, "#123a42", "#0c2a31", 1.4)
    for s in (-1, 1):
        AM.colunata(f"tor{s}", s * 3.8, 2.0, 16.0, 3.2, 8.5, "#0a2329", w=0.8)
    import random
    rnd = random.Random(5)
    for k in range(26):
        x = rnd.choice((-1, 1)) * (3.4 + rnd.random() * 0.2); y = 2.0 + rnd.random() * 14; z = 1.5 + rnd.random() * 6.5
        cena.disc(f"luzt{k}", 0.05, cena.amat(f"luzt{k}_m", "#ffc070", 1.5, 1.0), (x, y - 0.05, z))
    props.poly("chamine", cena.rect(-0.4, 0, -0.1, 11.0), "#0a2329", 15.0)
    cena.disc("chama", 0.7, cena.amat("chama_m", p["halo"], 1.5, 0.95, ("radial", 1.2)), (-0.25, 14.9, 11.4))
    cena.disc("chama_gl", 3.0, cena.amat("chama_gl_m", p["halo"], 1.0, 0.35, ("radial", 1.6)), (-0.25, 14.8, 11.2))
    for yv in (5.0, 10.0):
        S.neblina(p, yv, 0.14)
    halo("halo5", -1.1, 1.0, 1.3, 1.15, "#c98a5a")
    H, tl, w, faixa = heroi(p, "q", -1.1, A, END)
    a = Actor(tl, 0.0)
    aliados = []
    for j, x in enumerate((0.25, 0.95)):
        Ha, tla, al = ator(EL.empreiteiro if j == 0 else EL.deputado, f"aliado{j}", "q", x, 0.3, A, END, espelho=True, p=p, objeto=None)
        tla.face(A, 0.0, lid="esperto", lidv=0.5, brow=-8, mouth="sorriso", look=(1.0, 0.0))
        fim_ator(Ha, tla, A, END)
        UN.pop(al, F(wt(5, "aliados")) + 3 * j, 6); aliados.append(al)
    t_b = wt(5, "Em") - 0.08
    for al in aliados:
        S.mostra(al, [(A, F(t_b))])
    a.point(F(wt(5, "põe")) - 4)
    tl.face(A, 0.0, lid="esperto", lidv=0.5, brow=-10, mouth="sorriso", look=(1.0, 0.0))
    tp = F(wt(5, "Parece"))
    a.shrug(tp)
    tl.face(tp, 1.0, lid="esperto", lidv=0.45, brow=-12, browtilt=0.02, mouth="lado", look=(0.0, 0.0))
    f30 = F(wt(5, "30"))
    tl.face(f30 + 16, 1.0, eye="cifrao", mouth="sorrisao", browup=0.015, extras=("brilho",), look=(0.4, -0.3))
    finish(H, tl, A, END)
    # inserto do contrato (na mesa da obra, sob a luminária): de 100 partes, 3 vão por fora
    ox = 10.0
    S.caixa3d(p, "mesa5", ox, 0.3, 1.6, 0.8, d=0.7, cor="#5a4a3a", tampo="#c9a87e", aresta="#fff0d8")
    halo("halo_mesa5", ox, 1.4, 1.3, 1.4, "#5f8f96", 0.8)
    props.inked("contrato", rrect(-0.32, 0.0, 0.32, 0.42, 0.01, 2), "#f6f1e6", None, (ox - 0.45, 0.28, 0.8), w=0.006)
    for li in range(6):
        props.poly(f"contrato_l{li}", cena.rect(-0.24, 0.08 + li * 0.05, 0.2 - 0.05 * (li % 2), 0.095 + li * 0.05), "#9aa3b0", -0.004, bpy.data.objects["contrato"])
    f3 = F(wt(5, "3%"))
    for k in range(100):
        r, i = divmod(k, 10)
        q = UN.cubo(f"parte{k}", (ox + 0.05 + i * 0.075, 0.3, 0.8 + r * 0.075), 0.068, linhas=3)
        UN.pop(q, F(wt(5, "contrato")) + k // 6, 4)
        if k >= 97:                                                              # as 3 últimas (3%) saem pelo lado
            p0 = tuple(q.location); p1 = (ox + 0.95 + (k - 97) * 0.05, 0.2, 0.85 + (k - 97) * 0.08)
            UN.voa(q, f3 + 2 * (k - 97), f3 + 2 * (k - 97) + 9, p0, p1, alt=0.12)
    # o cubo de 1 bilhão (mil maços) brota do chão ao lado dele
    cb, _ = UN.cubo_mil("cubo5", (1.0, 0.9, 0.0))
    UN.sobe_do_chao(cb, F(wt(5, "1")) - 4, 12)
    sombra_cubo("cubo5_sb", 1.0, 0.9, UN.CUBO, p)
    # visto de cima, em 3/4 (plano sem boneco: a câmera pode girar): os 30 maços do topo (3%) levantam e vão embora
    o2 = 40.0
    AM.patio("pat5b", o2 - 8.0, o2 + 8.0, -8.0, 10.0, "#123a42", "#0c2a31", 1.0)
    for k in range(4):
        props.poly(f"tor5b{k}", cena.rect(o2 - 6 + k * 3.6, 0, o2 - 5.4 + k * 3.6, 7.5), "#0a2329", 9.0)
    cb2, bl2 = UN.cubo_mil("cubo5b", (o2, 0.0, 0.0), tirar=3)
    sombra_cubo("cubo5b_sb", o2, 0.0, UN.CUBO, p)
    for f in range(f30 - 2, f30 + 24):
        u = curvas.s("easy", min(1.0, max(0.0, (f - f30) / 8)))
        v = curvas.s("easy", min(1.0, max(0.0, (f - f30 - 9) / 13)))
        bl2.location = (-3.2 * v, -1.6 * v, 0.9 * u + 0.6 * v); key(bl2, "location", f, "LINEAR")
    tsao = wt(5, "são") - 0.05
    camera_livre(c, "cam_cima5", tsao, B[5], (o2 + 3.6, -4.8, 4.6), (o2 + 3.0, -4.2, 4.1), (o2 - 0.5, 0.0, 1.5), lens=30)
    t4 = wt(5, "Num") - 0.06
    P6.planos(c, [
        dict(t0=B[4], t1=t_b, caixa0=(-3.0, 3.0, -0.1, 5.0, 0.4), caixa1=(-1.7, 1.4, -0.1, 2.3, 0.3), lens=32, fstop=2.6, alt0=1.4, alt1=1.0,
             chaves_fim=["heroi_inv", "aliado1_inv"]),
        dict(t0=t_b, t1=wt(5, "Parece") - 0.1, caixa0=(ox - 0.85, ox + 1.05, 0.7, 1.65, 0.3), caixa1=(ox - 0.7, ox + 1.15, 0.72, 1.6, 0.3), lens=50, fstop=1.8,
             alt0=1.5, alt1=1.35),
        dict(t0=wt(5, "Parece") - 0.1, t1=t4, caixa0=(-1.55, -0.65, 1.2, 1.98, 0.0), caixa1=(-1.45, -0.72, 1.28, 1.95, 0.0), lens=55, fstop=1.6),
        dict(t0=t4, t1=tsao, caixa0=(-1.7, 2.25, -0.1, 2.6, 0.5), caixa1=(-1.6, 2.6, -0.1, 2.75, 0.6), lens=32, fstop=2.6, alt0=0.6, alt1=0.9,
             chaves=["heroi_inv"]),
    ], entra="h", sai="h")


# ====================================================================== 6. Petrobras: 6 bilhões; 1 milhão por dia, 17 anos (fala 6)
@cena_(6)
def s06(c):
    """sala de crise: ele de costas diante do telão em que o gráfico despenca, alarme vermelho -> 6 cubos caem na sala, entre ele e o telão ->
    o calendário na parede solta um maço a cada folha -> close dele suando em "17 anos" """
    A, END = F(B[5] - 0.4), F(B[6] + 0.4)
    p = pal("aco"); mundo(p); wy = 6.0
    AM.sala("crise", -4.2, 4.2, -14.0, wy, 4.0, dict(parede="#5a6a82", lateral="#4a5870", teto="#0c1018", viga="#141a24", chao="#141a24",
            linha="#0c1018", pilastra="#64748e"), piso="lajotas", passo_pilastra=2.0, passo_viga=1.6)
    tel, segs = OB.telao_bolsa("telao", (0.0, wy - 0.05, 1.2), "PETROBRAS", 1.0)
    cena.disc("telao_gl", 2.6, cena.amat("telao_gl_m", "#ff4a52", 1.0, 0.25, ("radial", 1.5)), (0, wy - 0.06, 2.4))
    ft = F(wt(6, "tona"))
    for k, seg in enumerate(segs):
        UN.pop(seg, ft + 2 * k, 3)
    S.luz_cor("alarme", "#ff3b4a", 0.0, 1.0, 3.6, 3.0, A, END, per=18, fase=0, alfa=0.22)
    H, tl, w, faixa = heroi(p, "back", -0.5, A, END, y=-0.8)
    tl.bake()
    L = UN.CUBO; t6 = wt(6, "6")
    for k in range(6):
        r, i = divmod(k, 3)
        cb = UN.cubo(f"c6_{k}", (0.7 + (i - 1) * (L + 0.06), 2.6, r * L), L)
        UN.sobe_do_chao(cb, F(t6 - 0.15) + 5 * k, 9, passa=0.0)
    sombra_cubo("c6_sb", 0.7, 2.6, 3 * L, p)
    # o calendário (em outra parede da sala) e ele de frente, ao lado
    ox = 14.0
    AM.sala("cal", ox - 3.0, ox + 3.0, -8.0, 3.0, 3.6, dict(parede="#5a6a82", lateral="#4a5870", teto="#0c1018", viga="#141a24", chao="#141a24",
            linha="#0c1018", pilastra="#64748e"), piso="lajotas", passo_pilastra=0, passo_viga=0)
    cal = empty("calendario6", None, (ox - 0.55, 2.95, 1.75))
    props.inked("cal_base", rrect(-0.42, -0.5, 0.42, 0.5, 0.04, 4), "#f6f1e4", cal, (0, 0.0, 0), w=0.012)
    props.inked("cal_topo", rrect(-0.42, 0.3, 0.42, 0.5, 0.04, 4), "#e2364b", cal, (0, -0.005, 0), w=0.0)
    halo("halo_h2", ox + 0.75, 2.5, 1.3, 1.1, "#9fb0c8")
    H2, tl2, w2, f2_ = heroi(p, "front", ox + 0.75, A, END, y=0.6, name="heroi2")
    t_e = wt(6, "É"); fa_ = F(t_e) + 2; fb_ = F(wt(6, "17")) + 4; n_f = 18
    for k in range(n_f):
        fk = fa_ + int((fb_ - fa_) * k / (n_f - 1))
        pg = empty(f"folha{k}", cal, (0, -0.006 - 0.0004 * k, 0))
        props.inked(f"folha{k}_f", rrect(-0.38, -0.46, 0.38, 0.26, 0.03, 3), "#fffaf0", pg, w=0.006)
        props.poly(f"folha{k}_n", rrect(-0.12, -0.2, 0.12, 0.04, 0.03, 3), "#c9c2b2", -0.002, pg)
        if k:
            UN.esconde_ate(pg, fk - 1)
        if k < n_f - 1:
            UN.some(pg, fk + 2, 2)
        m = UN.maco(f"m6_{k}", (ox - 0.4, 2.8, 1.45))
        UN.esconde_ate(m, fk)
        UN.voa(m, fk, fk + 9, (ox - 0.4, 2.8, 1.45), (ox - 1.6 + (k % 6) * 0.24, 2.6, (k // 6) * UN.MACO), alt=0.4)
    f17 = F(wt(6, "17"))
    tl2.face(A, 0.0, lid="esperto", lidv=0.5, brow=-4, mouth="reta", look=(-1.0, 0.3))
    tl2.face(fa_ + 6, 1.0, wide=0.4, brow=14, browup=0.015, mouth="nervosa", look=(-1.0, 0.2))
    tl2.face(f17, 1.0, eye="ponto", brow=26, browup=0.025, mouth="o", extras=("!", "suor"), look=(0.0, 0.0))
    finish(H2, tl2, A, END)
    bracos_parados(H2, A, END)
    t1, t2, t3 = wt(6, "reconheceu") - 0.1, t_e - 0.08, wt(6, "17") - 0.1
    P6.planos(c, [
        dict(t0=B[5], t1=t1, caixa0=(-1.5, 2.2, 0.0, 3.8, 1.5), caixa1=(-1.2, 1.9, 0.4, 3.7, 1.5), lens=35, fstop=2.2, alt0=1.5, alt1=1.6),
        dict(t0=t1, t1=t2, caixa0=(-3.0, 4.0, -0.1, 4.8, 1.4), caixa1=(-3.4, 4.2, -0.1, 4.9, 1.4), lens=30, fstop=3.5, alt0=0.6, alt1=1.2, chaves=["heroi_inv"]),
        dict(t0=t2, t1=t3, caixa0=(ox - 1.9, ox + 1.35, -0.1, 2.35, 1.5), caixa1=(ox - 1.8, ox + 1.4, 0.0, 2.3, 1.5), lens=35, fstop=2.4, chaves=["calendario6"]),
        dict(t0=t3, t1=B[6], caixa0=(ox + 0.35, ox + 1.15, 1.25, 2.0, 0.6), caixa1=(ox + 0.4, ox + 1.1, 1.32, 1.98, 0.6), lens=55, fstop=1.6),
    ], entra="h", sai="h")


# ====================================================================== 7. A empreiteira: o departamento de propina; 4 bilhões em 12 países (fala 7)
@cena_(7)
def s07(c):
    """grua descendo sobre o canteiro ao entardecer -> avanço por um corredor escuro até a porta acesa do "departamento"
    (um homem contando dinheiro contra a luz) -> no cofre, 4 cubos caem e 12 maços voam até 12 pontos acesos"""
    A, END = F(B[6] - 0.4), F(B[7] + 0.4)
    p = pal("obra"); mundo(p); wy = 16.0
    S.fundo(dict(p, low="#e08a5a", mid="#b85a36", top="#3a1810"), wy, z_meio=4.0, x=(-40, 40), z=(-4, 34), escuro=0.0)   # céu de fim de tarde claro: o esqueleto recorta
    AM.patio("pat7", -9.0, 9.0, -16.0, wy, "#4a2214", "#381a0f", 1.5)
    esq = "#2a120a"
    for j in range(5):                                              # o esqueleto do prédio em obra: lajes e pilares
        props.poly(f"laje{j}", cena.rect(-3.5, j * 2.6, 3.5, j * 2.6 + 0.22), esq, 9.0)
    for i in range(6):
        viga_obra(f"pilar{i}", -3.3 + i * 1.32, 9.02, 10.6, esq)
    guindaste(p, "gu1", -5.0, 11.0, 13.0, 5.0, 1)
    guindaste(p, "gu2", 5.5, 13.0, 15.0, 4.0, -1)
    S.neblina(p, 6.0, 0.12)
    # o corredor do "departamento"
    ox = 22.0
    AM.sala("corr", ox - 1.5, ox + 1.5, -14.0, 8.0, 3.0, dict(parede="#3a2a20", lateral="#8a6a50", teto="#1e140e", viga="#2a1c14", chao="#2a1c14",
            linha="#1e140e", pilastra="#9a7a5e"), piso="tabuas", passo_pilastra=1.8, passo_viga=1.4)
    props.poly("porta7", rrect(ox - 0.55, 0.0, ox + 0.55, 2.2, 0.03, 3), "#ffd9a8", 7.97)
    cena.ground_disc("porta7_luz", 1.0, 3.2, cena.amat("porta7_luz_m", "#ffd9a8", 1.0, 0.45, ("radial", 1.2)), (ox, 6.0, 0.003), n=40)
    Hc, tlc, wc = ator(EL.contador, "contador", "q", ox + 0.2, 7.75, A, END, espelho=True, p=p)
    tlc.face(A, 0.0, lid="triste", lidv=0.35, brow=18, mouth="nervosa", look=(1.0, -0.5), extras=("suor",))
    fim_ator(Hc, tlc, A, END)
    S.caixa3d(p, "mesa7", ox - 0.15, 7.45, 0.8, 0.72, d=0.35, cor="#3a2416", tampo="#8a5a34", aresta="#ffd9a8")
    for k in range(4):
        G.maco(f"pilha7_{k}", (ox - 0.4 + k * 0.17, 7.6, 0.72), n=3, s=1.6, zk=2.0)
    # o cofre: 4 bilhões e 12 países
    o2 = 44.0
    AM.sala("cofre", o2 - 4.5, o2 + 4.5, -14.0, 5.0, 8.0, dict(parede="#3a2418", lateral="#2e1c12", teto="#140c08", viga="#1e120c", chao="#22150e",
            linha="#180e09", pilastra="#4a2e20"), piso="lajotas", passo_pilastra=2.2, passo_viga=0)
    L = UN.CUBO; t4 = wt(7, "4")
    for k in range(4):
        r, i = divmod(k, 2)
        cb = UN.cubo(f"c7_{k}", (o2 + (i - 0.5) * (L + 0.06), 2.0, r * L), L)
        UN.sobe_do_chao(cb, F(t4 - 0.3) + 5 * k, 9, passa=0.0)
    OB.cofre("cofre7", (o2 - 3.4, 0.6, 0.0), 1.5)
    OB.caixa_papelao("cx7", (o2 + 3.3, 0.4, 0.0), 1.4)
    f12 = F(wt(7, "12"))
    for k in range(12):
        a = math.pi * (0.1 + 0.8 * k / 11)
        px, pz = o2 - math.cos(a) * 3.1, 5.2 + math.sin(a) * 2.0
        pt = cena.disc(f"pais{k}", 0.16, cena.amat(f"pais{k}_m", p["halo"], 1.4, 1.0), (px, 4.9, pz))
        gl = cena.disc(f"pais{k}_gl", 0.5, cena.amat(f"pais{k}_gl_m", p["halo"], 1.0, 0.35, ("radial", 1.3)), (px, 4.92, pz))
        fk = f12 - 4 + k
        for o in (pt, gl):
            UN.pop(o, fk + 9, 5, o.scale.x)
        m = UN.maco(f"m7_{k}", (o2, 1.9, 2 * L))
        UN.esconde_ate(m, fk)
        UN.voa(m, fk, fk + 9, (o2, 1.9, 2 * L), (px, 4.85, pz - 0.1), alt=0.6)
        UN.some(m, fk + 10, 3)
    t1, t2 = wt(7, "A") - 0.08, wt(7, "quase") - 0.08
    P6.planos(c, [
        dict(t0=B[6], t1=t1, caixa0=(-4.5, 4.5, -0.1, 13.0, 9.0), caixa1=(-3.8, 3.8, -0.1, 11.0, 9.0), lens=28, fstop=6.0, alt0=8.0, alt1=2.0),
        dict(t0=t1, t1=t2, caixa0=(ox - 1.5, ox + 1.5, -0.1, 3.0, 8.0), caixa1=(ox - 0.75, ox + 0.75, -0.05, 2.4, 8.0), lens=35, fstop=2.4, chaves_fim=["contador_inv"]),
        dict(t0=t2, t1=B[7], caixa0=(o2 - 3.3, o2 + 3.3, -0.1, 7.4, 1.0), caixa1=(o2 - 3.2, o2 + 3.2, -0.1, 7.3, 1.0), lens=30, fstop=4.0, preenche=0.9),
    ], entra="h", sai="h")


# ====================================================================== 8. A conta voltou: 17 bilhões em multas (fala 8)
@cena_(8)
def s08(c):
    """a sede da empreiteira à noite, viaturas chegando com a sirene batendo na fachada -> 17 cubos caem do céu na frente da sede, um a um"""
    A, END = F(B[7] - 0.4), F(B[8] + 0.4)
    p = pal("obra_verm"); mundo(p); wy = 20.0
    S.fundo(p, wy, z_meio=4.0, x=(-40, 40), z=(-4, 34), escuro=0.1)
    AM.patio("pat8", -10.0, 10.0, -16.0, wy, "#2a120c", "#1e0c08", 1.5)
    AM.predio("sede", 0.0, 7.5, 10.0, 13.0, 5.0, "#3a2a2a", "#2a1c1c", janelas=("#22161a", "#ffd9a0"), acesas=0.4, seed=3)
    vs = []
    for j, (x, fl) in enumerate(((-3.2, 1), (3.0, -1))):
        vt, vr, vb = S.viatura(p, f"vtr8_{j}", x, 3.5, s=0.9, flip=fl)
        S.pisca_sirene(vr, vb, A, END, per=8)
        Hpo, tlpo, wpo = ator(EL.policial, f"pol8_{j}", "front", x + (1.9 if fl > 0 else -1.9), 2.6, A, END, p=p)
        tlpo.face(A, 0.0, lid="apertado", lidv=0.6, brow=-12, mouth="reta", look=(-0.5 * fl, 0.3))
        fim_ator(Hpo, tlpo, A, END)
    S.luz_cor("fach_v", "#ff3b4a", -2.0, 7.4, 4.0, 4.0, A, END, per=16, fase=0, alfa=0.3)
    S.luz_cor("fach_b", "#3d7bff", 2.0, 7.4, 4.0, 4.0, A, END, per=16, fase=8, alfa=0.3)
    L = UN.CUBO; t17 = wt(8, "17")
    yc = -1.9                                                          # na frente das viaturas (y 3,5) e dos policiais (y 2,6)
    pos = [((i - 1) * (L + 0.05), yc, r * L) for r in range(3) for i in range(3)]
    pos += [((i - 1.5) * (L + 0.05), yc + L + 0.08, r * L) for r in range(2) for i in range(4)]
    pos.sort(key=lambda q: (q[2], -q[1]))
    for k, q in enumerate(pos):
        cb = UN.cubo(f"c8_{k}", q, L)
        UN.sobe_do_chao(cb, F(t17 - 0.6) + 3 * k, 8, passa=0.0)
    t1 = wt(8, "conta") - 0.1
    P6.planos(c, [
        dict(t0=B[7], t1=t1, caixa0=(-5.5, 5.5, -0.1, 13.0, 3.5), caixa1=(-4.6, 4.6, -0.1, 11.0, 3.5), lens=30, fstop=6.0, alt0=1.0, alt1=2.0),
        dict(t0=t1, t1=B[8], caixa0=(-3.9, 3.9, -0.1, 7.6, -1.9), caixa1=(-4.3, 4.3, -0.1, 8.2, -1.9), lens=30, fstop=5.0, preenche=0.9, alt0=0.8, alt1=1.6),
    ], entra="h", sai="h")


# ====================================================================== 9. Orçamento secreto: 45 bilhões em 3 anos; 40 milhões por dia (fala 9)
@cena_(9)
def s09(c):
    """gabinete roxo: ele vira as páginas do livro do orçamento sob o abajur -> grua subindo pela torre de 45 cubos com tarja preta ->
    close das tarjas -> ele ao lado dos 40 maços de um dia"""
    A, END = F(B[8] - 0.4), F(B[9] + 0.4)
    p = pal("gabinete"); mundo(p); wy = 4.0
    AM.sala("gab", -3.6, 3.6, -12.0, wy, 3.6, dict(parede="#8a6aa8", lateral="#6a4f86", teto="#140a22", viga="#1e1030", chao="#1a0e2a",
            linha="#120a1e", pilastra="#9a7ab8"), piso="tabuas", passo_pilastra=1.6, passo_viga=1.3)
    halo("halo9", 0.0, 1.8, 1.4, 1.2, "#c8a8e0")
    H, tl, w, faixa = heroi(p, "front", 0.0, A, END, y=1.0)
    S.caixa3d(p, "mesa9", 0.0, 0.4, 1.8, 0.85, d=0.6, cor="#3a2450", tampo="#b48ad0", aresta="#f0e0ff")
    livro = empty("livro9", None, (0.0, 0.38, 0.86))
    props.inked("livro9_e", rrect(-0.46, 0.0, 0.0, 0.42, 0.01, 2), "#f6efe0", livro, w=0.008)
    props.inked("livro9_d", rrect(0.0, 0.0, 0.46, 0.42, 0.01, 2), "#f6efe0", livro, w=0.008)
    for li in range(6):
        for s in (-1, 1):
            props.poly(f"livro9_l{li}{s}", cena.rect(min(0.05 * s, 0.4 * s), 0.07 + li * 0.055, max(0.05 * s, 0.4 * s), 0.085 + li * 0.055), "#8a7f9a", -0.004, livro)
    fo = F(wt(9, "orçamento"))
    for j in range(3):                                                           # as páginas viram (gira em torno da lombada)
        pg = empty(f"pag9_{j}", livro, (0, -0.002 - 0.001 * j, 0))
        props.inked(f"pag9_{j}_f", rrect(0.0, 0.0, 0.46, 0.42, 0.01, 2), "#fffaf0", pg, w=0.006)
        f0 = fo + 6 * j
        for k in range(9):
            pg.rotation_euler = (0, 0, math.radians(180 * curvas.s("easy", k / 8))); key(pg, "rotation_euler", f0 + k, "LINEAR")
    OB.bandeira_brasil("band9", (1.7, 3.2, 0.0), 1.0)
    OB.notebook("nb9", (-0.68, 0.55, 0.86), 0.55)
    props.inked("abajur9", [(-0.2, 1.2), (0.2, 1.2), (0.13, 1.36), (-0.13, 1.36)], "#1f6b4a", None, (0.75, 0.6, 0), w=0.0)
    luz.feixe("feixe9", 0.75, 0.6, 0.86, 1.2, 0.9, 0.3, "#ffe6b0", forca=1.3, frames=END, poeira=15, seed=91)
    tl.face(A, 0.0, lid="esperto", lidv=0.5, brow=-10, mouth="sorriso", look=(0.0, -0.8))
    tl.face(fo, 1.0, lid="esperto", lidv=0.42, brow=-16, browtilt=0.024, mouth="lado", look=(0.0, -0.8))
    finish(H, tl, A, END)
    bracos_parados(H, A, END)
    # a torre de 45 cubos no cofre do Congresso
    ox = 20.0
    AM.sala("cofre9", ox - 7.5, ox + 7.5, -40.0, 5.0, 26.0, dict(parede="#4a3466", lateral="#3a2852", teto="#0f0620", viga="#1a0e2a", chao="#1a0e2a",
            linha="#120a1e", pilastra="#5a4278"), piso="lajotas", passo_pilastra=3.0, passo_viga=0)
    L = UN.CUBO; t45 = wt(9, "45")
    for k in range(45):
        r, i = divmod(k, 5)
        cb = UN.cubo(f"c9_{k}", (ox + (i - 2) * (L + 0.04), 3.5, r * L), L, tarja=True)
        UN.sobe_do_chao(cb, F(t45 - 0.3) + int(k * 0.8), 5, passa=0.0)
    halo("halo9b", ox - 0.6, 1.6, 1.3, 1.0, "#c8a8e0")
    H2, tl2, w2, f2_ = heroi(p, "front", ox - 0.6, A, END, name="heroi2")
    t40 = wt(9, "40")
    tl2.face(A, 0.0, lid="esperto", lidv=0.5, brow=-10, mouth="sorriso", look=(0.6, 0.9))
    tl2.face(F(t40), 1.0, eye="cifrao", mouth="sorrisao", browup=0.015, extras=("brilho",), look=(1.0, -0.3))
    finish(H2, tl2, A, END)
    bracos_parados(H2, A, END)
    f40 = F(t40)
    for k in range(40):
        cam_, rest = divmod(k, 10); fy, i = divmod(rest, 5)
        m = UN.maco(f"m9_{k}", (ox + 0.25 + i * 0.235, -0.1 + fy * 0.235, cam_ * UN.MACO))
        UN.pop(m, f40 + k // 3, 4)
    t1, t2, t3 = wt(9, "45") - 0.1, wt(9, "sem") - 0.08, wt(9, "Uns") - 0.08
    P6.planos(c, [
        dict(t0=B[8], t1=t1, caixa0=(-0.75, 0.75, 0.75, 1.95, 0.4), caixa1=(-0.6, 0.6, 0.8, 1.9, 0.4), lens=45, fstop=1.8, alt0=1.6, alt1=1.5),
        dict(t0=t1, t1=t2, caixa0=(ox - 6.2, ox + 6.2, -0.1, 21.0, 3.0), caixa1=(ox - 6.2, ox + 6.2, -0.1, 21.0, 3.0), lens=30, fstop=6.0, preenche=0.92,
             alt0=1.0, alt1=13.0),
        dict(t0=t2, t1=t3, caixa0=(ox - 2.6, ox + 0.2, 0.2, 2.6, 2.355), caixa1=(ox - 2.3, ox + 0.3, 0.3, 2.5, 2.355), lens=40, fstop=2.4),
        dict(t0=t3, t1=B[9], caixa0=(ox - 1.15, ox + 1.6, -0.1, 2.05, 0.0), caixa1=(ox - 1.1, ox + 1.55, 0.0, 2.0, 0.0), lens=40, fstop=2.2, chaves=["heroi2_inv"]),
    ], entra="h", sai="h")


# ====================================================================== 10. O Supremo manda revelar os nomes (fala 10)
@cena_(10)
def s10(c):
    """de volta ao plenário: o martelo bate em "inconstitucional" -> no cofre, as tarjas pretas descolam dos cubos e voam"""
    A, END = F(B[9] - 0.4), F(B[10] + 0.4)
    p = pal("supremo"); mundo(p)
    Hp, tlp = tribunal("trib10", p, A, END)
    fi = F(wt(10, "inconstitucional")) + 2
    martelada_juiz(tlp, fi)
    tlp.face(fi - 5, 1.0, lid="bravo", brow=-26, mouth="dentes", look=(1.0, -0.6))
    fim_ator(Hp, tlp, A, END)
    ox = 20.0
    AM.sala("cofre10", ox - 5.0, ox + 5.0, -14.0, 5.0, 7.0, dict(parede="#4a505c", lateral="#3a3f4a", teto="#12141a", viga="#1c1f26", chao="#2a2d34",
            linha="#1e2026", pilastra="#5a606c"), piso="lajotas", passo_pilastra=2.0, passo_viga=0)
    luz.feixe("feixe10", ox, 2.0, 0.0, 7.0, 4.0, 1.4, "#eef3fb", forca=0.9, frames=END, poeira=25, seed=101)
    L = UN.CUBO; tr = wt(10, "revelar")
    for k in range(6):
        r, i = divmod(k, 3)
        x = ox + (i - 1) * (L + 0.05); z = r * L
        UN.cubo(f"c10_{k}", (x, 2.5, z), L)
        for j, zz in enumerate((0.47, 0.53)):
            props.poly(f"nome10_{k}_{j}", cena.rect(x - L * 0.3, z + L * zz - 0.03, x + L * (0.18 if j else 0.3), z + L * zz + 0.03), "#24402a",
                       2.5 - L / 2 - 0.004)
        tj = empty(f"tarja10_{k}", None, (x, 2.5 - L / 2 - 0.02, z + L * 0.5))
        props.poly(f"tarja10_{k}_f", cena.rect(-L * 0.4, -L * 0.08, L * 0.4, L * 0.08), "#0b0b10", 0.0, tj)
        f0 = F(tr) + 3 * k
        p0 = tuple(tj.location); p1 = (x + 1.2 * (1 if i >= 1 else -1), p0[1] - 0.6, p0[2] + 3.5)
        key(tj, "location", f0 - 1, "LINEAR"); key(tj, "rotation_euler", f0 - 1, "LINEAR")
        for f in range(f0, f0 + 14):
            u = curvas.s("queda", (f - f0) / 13)
            tj.location = tuple(a + (b - a) * u for a, b in zip(p0, p1)); tj.rotation_euler = (0, math.radians(-160 * u * (1 if i else -1)), 0)
            key(tj, "location", f, "LINEAR"); key(tj, "rotation_euler", f, "LINEAR")
        UN.some(tj, f0 + 12, 3)
    t1 = wt(10, "e") - 0.08
    P6.planos(c, [
        dict(t0=B[9], t1=t1, caixa0=(-2.6, 2.6, 0.6, 5.6, 3.6), caixa1=(-0.65, 1.0, 1.55, 3.05, 4.15), lens=35, fstop=2.4, alt0=1.4, alt1=2.3),
        dict(t0=t1, t1=B[10], caixa0=(ox - 3.6, ox + 3.6, -0.1, 4.7, 1.3), caixa1=(ox - 3.3, ox + 3.3, 0.0, 4.6, 1.3), lens=35, fstop=4.0, preenche=0.9),
    ], entra="h", sai="h")


# ====================================================================== 11. Joias de 16 milhões = 800 anos de salário mínimo (fala 11)
def mochila(name, loc):
    r = empty(name, None, loc)
    props.inked(name + "_c", rrect(-0.2, 0.0, 0.2, 0.48, 0.09, 6), "#2b3240", r, w=0.012, shade=0.03, shade_color="#1c2230", rim=0.012, rim_color="#d8f7ff")
    tampa = empty(name + "_tampa", r, (0, -0.004, 0.48))
    props.inked(name + "_t", rrect(-0.2, -0.16, 0.2, 0.02, 0.07, 5), "#3a4356", tampa, w=0.012)
    props.poly(name + "_bolso", rrect(-0.12, 0.06, 0.12, 0.22, 0.04, 4), "#232a37", -0.006, r)
    return r, tampa


@cena_(11)
def s11(c):
    """no salão do palácio, um enviado estrangeiro dá a ele um estojo de presente que brilha -> no raio-x do aeroporto, a mochila para,
    o fiscal levanta a mão, a tela mostra as joias; 16 maços ao lado -> na estrada ao entardecer, 20 trabalhadores em fila até o horizonte
    (20 vidas de 40 anos = 800 anos de salário mínimo)"""
    A, END = F(B[10] - 0.4), F(B[11] + 0.4)
    p = pal("palacio"); mundo(p)
    salao_palacio("hall11", p, 0.0, 12.0, END)
    H, tl, w, faixa = heroi(p, "q", -0.75, A, END)
    He, tle, env = ator(EL.diplomata, "enviado", "q", 0.8, 0.2, A, END, espelho=True, p=p, objeto=None)
    est = OB.estojo_joias("presente", (0.25, 0.0, 0.92), 0.6)
    gl = bpy.data.objects["presente_gl"]; gl.parent = est; gl.location = (0.0, 0.03, 0.25)
    fpr = F(wt(11, "presente"))
    UN.pop(est, fpr - 2, 6, 0.6)
    tle.face(A, 0.0, eye="feliz", mouth="sorriso", browup=0.01, look=(1.0, 0.0))
    tle.intent(fpr - 6, shF=10, elF=60); tle.intent(fpr, shF=60, elF=35, wrF=8); tle.intent(fpr + 18, shF=12, elF=60, wrF=0)
    fim_ator(He, tle, A, END)
    UN.voa(est, fpr + 6, fpr + 16, (0.25, 0.0, 0.92), (-0.35, -0.05, 0.88), alt=0.08)
    fpb = F(wt(11, "problema"))
    for k in range(8):                                                           # "vira problema": o estojo treme
        est.rotation_euler = (0, math.radians(8 * math.sin(k * 2.2) * (1 - k / 8)), 0); key(est, "rotation_euler", fpb + k, "LINEAR")
    tl.face(A, 0.0, lid="esperto", lidv=0.5, brow=-8, mouth="sorriso", look=(1.0, -0.2))
    tl.face(fpr + 4, 1.0, eye="cifrao", mouth="sorrisao", browup=0.015, extras=("brilho",), look=(1.0, -0.4))
    tl.face(fpb, 1.0, wide=0.5, brow=18, browup=0.02, mouth="nervosa", look=(0.6, -0.4), extras=("suor",))
    tl.intent(fpr + 2, shF=58, elF=40, wrF=6); tl.intent(fpr + 16, shF=30, elF=70, wrF=0)
    finish(H, tl, A, END)
    # o raio-x do aeroporto
    ox = 24.0
    AM.sala("aero", ox - 4.0, ox + 4.0, -12.0, 4.5, 3.6, dict(parede="#5a9aae", lateral="#3a7f93", teto="#0c1e26", viga="#12303a", chao="#1a3a44",
            linha="#123039", pilastra="#6aaabd"), piso="lajotas", passo_pilastra=1.8, passo_viga=1.4)
    S.caixa3d(p, "esteira", ox, 0.2, 4.0, 0.75, d=0.6, cor="#1c2a33", tampo="#2a3c48", aresta="#d8f7ff")
    props.inked("arco_rx", [(-0.75, 0.75), (-0.75, 2.0), (0.75, 2.0), (0.75, 0.75), (0.6, 0.75), (0.6, 1.85), (-0.6, 1.85), (-0.6, 0.75)],
                "#cfe8ef", None, (ox + 0.4, 0.35, 0), w=0.0)
    props.inked("monitor", rrect(-0.45, -0.3, 0.45, 0.3, 0.03, 3), "#0a1418", None, (ox - 1.6, 0.9, 1.75), w=0.02)
    fj = F(wt(11, "joias"))
    for j, (x, z, r_, cor) in enumerate(((-0.12, 0.02, 0.06, "#ffe08a"), (0.02, 0.04, 0.07, "#ffffff"), (0.14, 0.0, 0.055, "#ffd27a"), (-0.02, -0.1, 0.045, "#fff4c8"))):
        jo = props.poly(f"joia_tela{j}", circle(ox - 1.6 + x, 1.75 + z, r_, 18), cor, 0.88)
        UN.pop(jo, fj + j, 5)
    Hf, tlf, fiscal = ator(EL.fiscal, "fiscal", "q", ox + 1.5, 0.9, A, END, espelho=True, p=p)
    moc, tampa = mochila("mochila", (ox - 1.6, 0.05, 0.75))
    fb = F(wt(11, "barradas"))
    for f in range(A, fb):
        u = curvas.s("easy", min(1.0, max(0.0, (f - (fj - 10)) / max(1, fb - (fj - 10))))); moc.location.x = ox - 1.6 + 1.9 * u; key(moc, "location", f, "LINEAR")
    tlf.face(A, 0.0, lid="apertado", lidv=0.6, brow=-8, mouth="reta", look=(1.0, -0.3))
    tlf.face(fb - 2, 1.0, lid="bravo", brow=-22, mouth="o", look=(1.0, -0.3), extras=("!",))
    tlf.intent(fb - 8, shF=20, elF=60); tlf.intent(fb - 2, shF=150, elF=12, wrF=-25); tlf.intent(fb + 30, shF=148, elF=14, wrF=-25)
    fim_ator(Hf, tlf, A, END)
    f16 = F(wt(11, "16"))
    for k in range(16):
        r, i = divmod(k, 4)
        m = UN.maco(f"m11_{k}", (ox + 0.95 + i * 0.235, 0.15, 0.75 + r * UN.MACO))
        UN.pop(m, f16 + k, 4)
    # a estrada: 20 vidas de trabalho em fila até o horizonte
    o2 = 50.0
    S.fundo(dict(p, top="#2a1a3a", mid="#e08a5a", low="#ffb87a"), 60.0, z_meio=2.0, x=(o2 - 60, o2 + 60), z=(-4, 40), escuro=0.0)
    AM.patio("estrada", o2 - 2.2, o2 + 2.2, -10.0, 60.0, "#8a7880", "#8a7880", 50)
    for k in range(30):
        cena.poly_mesh(f"faixa_e{k}", [(o2 - 0.06, -8 + k * 2.2, 0.002), (o2 + 0.06, -8 + k * 2.2, 0.002), (o2 + 0.06, -7 + k * 2.2, 0.002), (o2 - 0.06, -7 + k * 2.2, 0.002)], props.FM("#f2e6c8"))
    t800 = wt(11, "800")
    for k in range(20):
        x = o2 + (0.7 if k % 2 else -0.7); y = 0.5 + k * 2.1
        if k < 6:                                                     # os da frente são trabalhadores da ficha, com rosto cansado
            Hw, tlw, g = ator(EL.trabalhador, f"vida{k}", "front", x, y, A, END, p=p)
            tlw.face(A, 0.0, lid="sono", lidv=0.6, brow=16, mouth="triste", look=(0.0, -0.3))
            fim_ator(Hw, tlw, A, END)
        else:
            g = props.pessoa(f"vida{k}", x, y, "#1a141e", 1.0, flip=1 if k % 2 else -1, rim="#ffd0a0")
        UN.pop(g, F(t800 - 0.35) + 2 * k, 4)
    t1, t2 = wt(11, "joias") - 0.1, wt(11, "Mais") - 0.08
    P6.planos(c, [
        dict(t0=B[10], t1=t1, caixa0=(-1.5, 1.4, -0.1, 2.3, 0.0), caixa1=(-1.2, 1.15, 0.5, 2.1, 0.0), lens=35, fstop=2.2, chaves=["heroi_inv"]),
        dict(t0=t1, t1=t2, caixa0=(ox - 2.2, ox + 2.0, 0.0, 2.4, 0.2), caixa1=(ox - 2.0, ox + 2.0, 0.2, 2.3, 0.2), lens=35, fstop=2.4, chaves=["mochila", "monitor"]),
        dict(t0=t2, t1=B[11], caixa0=(o2 - 1.2, o2 + 1.2, -0.1, 2.3, 0.5), caixa1=(o2 - 2.0, o2 + 2.0, -0.1, 3.4, 0.5), lens=35, fstop=8.0, alt0=1.0, alt1=2.6),
    ], entra="h", sai="h")


# ====================================================================== 12. A investigação chega no presidente (fala 12)
@cena_(12)
def s12(c):
    """a fachada do palácio à noite, colunas brancas; duas viaturas chegam e a sirene bate na fachada -> close dele na porta, suando"""
    A, END = F(B[11] - 0.4), F(B[12] + 0.4)
    p = pal("noite"); mundo(p); wy = 30.0
    S.fundo(p, wy, z_meio=3.0, x=(-40, 40), z=(-4, 30), escuro=0.0)
    AM.patio("pat12", -12.0, 12.0, -16.0, wy, "#1a1e3a", "#121530", 1.6)
    props.poly("fachada", cena.rect(-7.0, 0.0, 7.0, 5.2), "#2c3270", 7.0)
    props.poly("laje12", cena.rect(-7.5, 5.0, 7.5, 5.5), "#e8e2d4", 6.9)
    for k in range(12):
        x = -6.6 + k * 1.2
        props.inked(f"col12_{k}", [(-0.05, 0.0), (0.05, 0.0), (0.22, 4.4), (0.3, 5.0), (-0.3, 5.0), (-0.22, 4.4)], "#e8e2d4", None, (x, 6.0, 0), w=0.0)
    props.poly("porta12", rrect(-0.7, 0.0, 0.7, 2.6, 0.03, 3), "#ffd9a0", 6.95)
    vts = []
    for j, (x0, x1, fl) in enumerate(((-12.0, -3.0, 1), (12.0, 3.2, -1))):
        vt, vr, vb = S.viatura(p, f"vtr12_{j}", x0, 3.0, s=1.0, flip=fl)
        S.pisca_sirene(vr, vb, A, END, per=8)
        fa = F(wt(12, "investigação")) - 6 + 4 * j
        for f in range(fa, fa + 18):
            u = curvas.s("easy", (f - fa) / 17); vt.location.x = x0 + (x1 - x0) * u; key(vt, "location", f, "LINEAR")
        vt.location.x = x0; key(vt, "location", A, "CONSTANT")
        Hpo, tlpo, wpo = ator(EL.policial, f"pol12_{j}", "front", x1 + (1.6 if fl > 0 else -1.6), 1.6, A, END, p=p)
        tlpo.face(A, 0.0, lid="apertado", lidv=0.6, brow=-14, mouth="reta", look=(0.0, 0.4))
        fim_ator(Hpo, tlpo, A, END)
        UN.pop(wpo, F(wt(12, "chegou")) + 3 * j, 6)
    S.luz_cor("f12_v", "#ff3b4a", -2.5, 6.8, 2.8, 4.5, A, END, per=16, fase=0, alfa=0.35)
    S.luz_cor("f12_b", "#3d7bff", 2.5, 6.8, 2.8, 4.5, A, END, per=16, fase=8, alfa=0.35)
    halo("halo12", 0.0, 6.5, 1.3, 1.1, "#ffd9a0")
    H, tl, w, faixa = heroi(p, "front", 0.0, A, END, y=5.6)
    S.luz_cor("rosto_v", "#ff3b4a", -0.6, 5.7, 1.6, 1.0, A, END, per=14, fase=0, alfa=0.3)
    S.luz_cor("rosto_b", "#3d7bff", 0.6, 5.7, 1.6, 1.0, A, END, per=14, fase=7, alfa=0.3)
    fpol = F(wt(12, "polícia"))
    tl.face(A, 0.0, lid="esperto", lidv=0.5, brow=-6, mouth="reta", look=(0.0, -0.3))
    tl.face(fpol, 1.0, eye="ponto", brow=26, browup=0.025, mouth="o", extras=("!",), look=(-0.9, -0.2))
    tl.face(fpol + 8, 1.0, wide=0.6, brow=20, browup=0.02, mouth="nervosa", look=(0.9, -0.2), extras=("suor",))
    finish(H, tl, A, END)
    bracos_parados(H, A, END)
    t1 = wt(12, "chegou") - 0.08
    P6.planos(c, [
        dict(t0=B[11], t1=t1, caixa0=(-5.5, 5.5, -0.1, 6.2, 5.0), caixa1=(-4.5, 4.5, -0.1, 5.8, 5.0), lens=30, fstop=5.0, alt0=0.8, alt1=1.4),
        dict(t0=t1, t1=B[12], caixa0=(-0.7, 0.7, 0.9, 2.0, 5.6), caixa1=(-0.45, 0.45, 1.1, 1.95, 5.6), lens=50, fstop=1.6),
    ], entra="h", sai="h")


# ====================================================================== 13. O preço: 7 presidentes, 4 presos (fala 13)
def icone(name, tipo, loc, cor="#2b2f45"):
    """ícone simples num distintivo branco: martelo (corrupção), punho (golpe), balança (absolvido ou anulado)"""
    r = empty(name, None, loc)
    props.inked(name + "_b", circle(0, 0, 0.17, 32), "#fffaf0", r, w=0.01)
    if tipo == "martelo":
        props.poly(name + "_1", rrect(-0.09, 0.02, 0.05, 0.08, 0.015, 2), cor, -0.003, r)
        props.poly(name + "_2", rrect(-0.01, -0.1, 0.02, 0.04, 0.01, 2), cor, -0.003, r)
    elif tipo == "punho":
        props.poly(name + "_1", rrect(-0.08, -0.06, 0.08, 0.07, 0.03, 4), cor, -0.003, r)
        for j in range(3):
            props.poly(f"{name}_d{j}", cena.rect(-0.04 + j * 0.04, 0.0, -0.035 + j * 0.04, 0.07), "#fffaf0", -0.005, r)
        props.poly(name + "_2", rrect(-0.05, -0.12, 0.05, -0.05, 0.02, 2), cor, -0.003, r)
    else:
        props.poly(name + "_1", cena.rect(-0.008, -0.1, 0.008, 0.09), cor, -0.003, r)
        props.poly(name + "_2", cena.rect(-0.11, 0.075, 0.11, 0.09), cor, -0.003, r)
        for j, x in enumerate((-0.09, 0.09)):
            props.poly(f"{name}_p{j}", [(x - 0.05, 0.0), (x + 0.05, 0.0), (x, 0.06)], cor, -0.004, r)
    return r


def retrato(nm, x, y, z, w=0.84, h=1.04):
    return OB.retrato(nm, (x, y, z), 1.0)


@cena_(13)
def s13(c):
    """avanço por uma galeria comprida: retratos sem rosto em cavaletes, alternando os lados -> a parede com os 7 retratos:
    4 recebem grade e aparecem os ícones (corrupção, golpe, absolvido ou anulado)"""
    A, END = F(B[12] - 0.4), F(B[13] + 0.4)
    p = pal("galeria"); mundo(p)
    AM.sala("gal", -3.2, 3.2, -14.0, 16.0, 4.2, dict(parede="#5a8a76", lateral="#3f6a58", teto="#0a1610", viga="#12221a", chao="#14241c",
            linha="#0c1812", pilastra="#6a9a86"), piso="tabuas", passo_pilastra=2.0, passo_viga=1.6)
    t7 = wt(13, "7")
    for k in range(7):
        lado = -1 if k % 2 == 0 else 1
        y = 5.2 + k * 1.5
        S.caixa3d(p, f"cav{k}", lado * 1.5, y + 0.05, 0.08, 1.15, d=0.06, cor="#2a1c12", tampo="#2a1c12")
        fr = retrato(f"cavr{k}", lado * 1.5, y, 1.75)
        cena.disc(f"cav_spot{k}", 0.7, cena.amat(f"cav_spot{k}_m", "#ffe2b0", 1.0, 0.3, ("radial", 1.4)), (lado * 1.5, y + 0.1, 1.9))
        UN.pop(fr, F(t7) - 6 + 3 * k, 5)
    ox = 20.0
    AM.sala("gal2", ox - 3.4, ox + 3.4, -10.0, 3.2, 4.2, dict(parede="#5a8a76", lateral="#3f6a58", teto="#0a1610", viga="#12221a", chao="#14241c",
            linha="#0c1812", pilastra="#6a9a86"), piso="tabuas", passo_pilastra=2.0, passo_viga=0)
    wy = 3.2
    pos = [(ox - 1.65 + 1.1 * i, 2.75) for i in range(4)] + [(ox - 1.1 + 1.1 * i, 1.4) for i in range(3)]
    t4 = wt(13, "4")
    presos = (1, 2, 4, 6)
    for k, (x, z) in enumerate(pos):
        retrato(f"quadro{k}", x, wy - 0.2, z)
        cena.disc(f"spot{k}", 0.6, cena.amat(f"spot{k}_m", "#ffe2b0", 1.0, 0.25, ("radial", 1.4)), (x, wy - 0.15, z + 0.35))
        if k in presos:
            j = presos.index(k)
            gr = props.grade(f"gq{k}", x - 0.38, x + 0.38, z - 0.5, z + 0.5, wy - 0.35, "#0d0f12", n=4, w=0.035, rails=0)
            fg = F(t4) + 3 * j
            UN.esconde_ate(gr, fg)
            gr.location.z = 1.2; key(gr, "location", fg - 1, "LINEAR")
            for f in range(fg, fg + 7):
                gr.location.z = 1.2 * (1 - curvas.s("queda", (f - fg) / 6)); key(gr, "location", f, "LINEAR")
    for nome, tipo, k_, palavra in (("ic_corr", "martelo", 1, "corrupção"), ("ic_golpe", "punho", 4, "golpe"),
                                    ("ic_abs1", "balanca", 2, "absolvidas"), ("ic_abs2", "balanca", 6, "absolvidas")):
        x, z = pos[k_]
        ic = icone(nome, tipo, (x + 0.33, wy - 0.45, z + 0.43))
        UN.pop(ic, F(wt(13, palavra)) + (3 if nome == "ic_abs2" else 0), 6)
    t1 = wt(13, "4") - 0.3
    P6.planos(c, [
        dict(t0=B[12], t1=t1, caixa0=(-2.4, 2.4, -0.1, 3.6, 1.5), caixa1=(-1.8, 1.8, 0.6, 3.0, 6.0), lens=32, fstop=2.8, alt0=1.6, alt1=1.7),
        dict(t0=t1, t1=B[13], caixa0=(ox - 2.2, ox + 2.2, 0.75, 3.35, wy - 0.2), caixa1=(ox - 2.05, ox + 2.05, 0.8, 3.3, wy - 0.2), lens=35, fstop=4.0, preenche=0.9,
             chaves=[f"quadro{k}" for k in range(7)]),
    ], entra="h", sai="h")


# ====================================================================== 14. Ainda quer a faixa? (fala 14)
@cena_(14)
def s14(c):
    A, END = F(B[13] - 0.4), F(B[14] + 0.4)
    p = pal("celas"); wy = 3.0
    pe = dict(p, mid=_mix(p["mid"], p["top"], 0.5), low=_mix(p["low"], p["top"], 0.4))
    S.fundo(pe, wy, z_meio=1.8, x=(-10, 10), z=(-3, 10))
    luz.feixe("feixe_s14", 0.0, 0.6, 0.0, 5.0, 1.3, 0.3, p["luz"], forca=1.4, frames=END, poeira=40, seed=77)
    cena.disc("halo_s14", 1.6, cena.amat("halo_s14_m", p["halo"], 1.0, 0.45, ("radial", 1.5)), (0.0, wy - 0.1, 1.6))
    gr = props.grade("grade_fim", -1.4, 1.4, 0.0, 3.0, -0.55, p["grade"], n=8, w=0.05, rails=0)
    props.poly("grade_fim_trave", cena.rect(-1.4, 1.62, 1.4, 1.7), p["grade"], -0.551)
    # a faixa do lado de fora, pendurada na travessa da grade
    fx = 0.62
    props.poly("faixa_fora_a", [(fx - 0.1, 1.74), (fx + 0.1, 1.74), (fx + 0.15, 0.95), (fx - 0.04, 0.92)], U.FAIXA_AMARELA, -0.6)
    props.poly("faixa_fora_v", [(fx - 0.05, 1.74), (fx + 0.05, 1.74), (fx + 0.1, 0.94), (fx + 0.005, 0.93)], U.FAIXA_VERDE, -0.602)
    props.poly("faixa_fora_dobra", [(fx - 0.1, 1.74), (fx + 0.1, 1.74), (fx + 0.09, 1.6), (fx - 0.09, 1.6)], _mix(U.FAIXA_AMARELA, "#000000", 0.25), -0.53)
    H, tl, w, faixa = heroi(p, "front", 0.0, A, END, roupa="preso")
    tl.intent(A, head=-8, torso=0)
    tl.face(A, 0.0, wide=0.3, brow=8, browup=0.012, mouth="pequena", look=(0.2, 0.8))
    fq = F(wt(14, "quer"))
    tl.face(fq, 1.0, lid="esperto", lidv=0.6, brow=-10, browtilt=0.018, mouth="lado", look=(0.0, 0.0))
    tl.intent(fq - 4, head=6, torso=2)
    finish(H, tl, A, END)
    bracos_parados(H, A, END)
    P6.planos(c, [
        dict(t0=B[13], t1=B[14], caixa0=(-0.75, 0.95, 0.65, 2.0, 0.0), caixa1=(-0.55, 0.8, 0.85, 1.95, 0.0), lens=50, fstop=1.8),
    ], entra="h", sai=None)


def com_vida(fn):
    """depois de montar a cena: tremido de traço em tudo, figurantes balançando, câmera na mão; e grava onde estão os rostos"""
    def g(c):
        fn(c)
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
