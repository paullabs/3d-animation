"""Canal 38: "E se o seu cérebro fosse 10 vezes mais rápido?" (voz do Lucas, 50 s). Roteiro: roteiros/reflexo.json.
Oito cenas, uma por fala; o herói em 2D no dia a dia e em 3D de verdade (heroi3d.py) nos planos de câmera livre (a régua, o pênalti, a largada,
a final). Mesmas regras do presidente: rostos livres, vida, nada atravessa nada, número vira proporção.
blender -b -P prod_reflexo.py -- CENA OUT [--scale 0.5] [--samples 10] [--at t1,t2] [--list]"""
import os, sys, json, math
os.environ["VOZ_NOVA"] = ""
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy, lib
from lib import *
import cena, props, luz, curvas, frente, uniforme as U, sets4 as S, unidades as UN, titulo3d as T3, ambiente3d as AM, transicao as TR
import elenco as EL, elenco_reflexo as ER, objetos as OB, objetos_reflexo as OR, heroi3d as H3
from heroi3d import corrida
import prod_pcc4 as P4
import prod_pcc6 as P6
from prod_pcc4 import F, FPS, finish, Timeline, P, _mix
T = lambda f: (f - 1) / FPS
LIMPO = bool(os.environ.get("LIMPO"))                                       # passe limpo para o Kling 4.0: sem números, rótulos, anéis, ecos, poeira nem filtro                                                # quadro -> segundos (inverso de F)
from heroi import Heroi
from char2d import rrect
from puppet2d import circle, stroke
import vida, rostos
P4.CENAS.clear()
_finish = finish


def finish(H, tl, f0, f1, boil=True):
    """todo boneco 2D respira, balança o peso e mexe a cabeça em onda por cima do que a cena animou"""
    vida.vida_ator(tl, f0, f1, seed=sum(map(ord, H.name)))
    _finish(H, tl, f0, f1, boil)


VOZ = (__import__("canal38_env").RAIZ + "/roteiros/voz-reflexo")
PAL = json.load(open(VOZ + "/palavras.json")); TEMPOS = json.load(open(VOZ + "/tempos.json"))
FALAS = [(f["inicio"], f["inicio"] + f["duracao"]) for f in TEMPOS["falas"]]
TOT = TEMPOS["total"]
DT = TEMPOS.get("corte", {}).get("dur", 0.0)                  # segundos tirados do áudio (a frase dos músculos): os tempos absolutos das cenas 4 em diante recuam isso
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
    cozinha=dict(top="#2a1d12", mid="#d8b988", low="#a8875a", chao="#8a6a48", halo="#fff0c8", luz="#fff4d8", pedra="#cbb088", aresta="#fff1d4", borda="#ffe0b8"),
    lab=dict(top="#0e2128", mid="#6fa0aa", low="#3d6770", chao="#2c4a52", halo="#d8f7ff", luz="#eaffff", pedra="#7fb0ba", aresta="#e8ffff", borda="#ffe4c8"),
    reguas=dict(top="#1a1430", mid="#7a68b0", low="#43386e", chao="#2a2148", halo="#ffe8c8", luz="#fff0d8", pedra="#8a78c0", aresta="#f0e6ff", borda="#ffd9b8"),
    estadio_dia=dict(top="#2f6ea8", mid="#a8d4ee", low="#5aa0c8", chao="#3f8a4a", halo="#fff7d8", luz="#ffffff", pedra="#8fb0a0", aresta="#ffffff", borda="#ffe4c8"),
    pista=dict(top="#2a3a7a", mid="#e8a070", low="#b45a40", chao="#b5503a", halo="#fff0c8", luz="#fff4d8", pedra="#d8885c", aresta="#fff0e0", borda="#ffd9b0"),
    estadio_noite=dict(top="#070a22", mid="#26307a", low="#141a50", chao="#1f6a3a", halo="#fff4d0", luz="#ffffff", pedra="#3a448f", aresta="#e8eeff", borda="#ffd9b0"),
    final=dict(top="#2a1810", mid="#9a5a30", low="#5a3018", chao="#3a2214", halo="#ffd890", luz="#ffe8b8", pedra="#b06a38", aresta="#ffe8c8", borda="#ffd9a8"),
)


def pal(nome):
    return S.var(P, **V[nome])


def mundo(p):
    bpy.context.scene.world.node_tree.nodes["Background"].inputs[0].default_value = (*lib.srgb(p["top"]), 1)


def halo(nome, x, y, z, r=1.0, cor="#a07c56", alfa=0.75):
    return cena.disc(nome, r, cena.amat(nome + "_m", cor, 1.0, alfa, ("radial", 1.3)), (x, y, z))


def heroi2d(p, view, x, A, END, y=0.0, name="voce"):
    """o herói 2D de sempre (jaqueta vermelha, cabeça lisa), no tamanho real"""
    H = Heroi(name, view, pal=dict(rim=p["borda"]))
    w = empty(name + "_inv", None, (x, y, 0)); H.root.parent = w
    tl = Timeline(H, A, END, FPS); tl.stand(A, END, 0.0)
    cena.contact_shadow(H, dict(shadow=_mix(p["chao"], "#000000", 0.4)))
    return H, tl, w


def ator(fn, nome, view, x, y, A, END, espelho=False, escala=1.0, p=None, **kw):
    H = fn(nome, view, **kw)
    w = empty(nome + "_inv", None, (x, y, 0)); H.root.parent = w
    w.scale = (-escala if espelho else escala, escala, escala)
    tl = Timeline(H, A, END, FPS); tl.stand(A, END, 0.0)
    cena.contact_shadow(H, dict(shadow=_mix((p or P)["chao"], "#000000", 0.4)))
    return H, tl, w


def heroi3(nome, x, y, p, **kw):
    """o herói em 3D de verdade; o nome termina em _inv (fica fora do tremido de cena e conta como boneco nos detectores)"""
    H = H3.Heroi3D(nome + "_inv", borda=p["borda"], **kw)
    H.raiz.location = (x, y, 0)
    H.sombra = cena.ground_disc(nome + "_sb", 0.42, 0.26, cena.amat(nome + "_sb_m", "#000000", 1.0, 0.38, ("radial", 1.1)), (x, y + 0.05, 0.003), n=32)
    return H


def camera_livre(c, nome, t0, t1, p0, p1, alvo, lens=40, fstop=4.0, alvo1=None, entra=None, sai=None):
    """câmera que gira (planos com o herói 3D e objetos): olha para 'alvo' (e vai para 'alvo1'), desliza de p0 a p1 na curva easy"""
    from mathutils import Vector
    sc = c["sc"]
    cd = bpy.data.cameras.new(nome); cam = bpy.data.objects.new(nome, cd); sc.collection.objects.link(cam)
    cd.lens = lens; cd.sensor_fit = "HORIZONTAL"; cd.sensor_width = 24
    cd.dof.use_dof = True; cd.dof.aperture_fstop = fstop
    fa, fb = F(t0), F(t1)
    alvo1 = alvo1 or alvo
    for f in range(fa - 1, fb + 2):
        u = curvas.s("easy", min(1.0, max(0.0, (f - fa) / max(1, fb - fa))))
        pos = Vector(tuple(a + (b - a) * u for a, b in zip(p0, p1)))
        al = Vector(tuple(a + (b - a) * u for a, b in zip(alvo, alvo1)))
        cam.location = pos
        cam.rotation_euler = (al - pos).to_track_quat("-Z", "Y").to_euler()
        key(cam, "location", f, "LINEAR"); key(cam, "rotation_euler", f, "LINEAR")
        cd.dof.focus_distance = (al - pos).length; cd.dof.keyframe_insert("focus_distance", frame=f)
    m = sc.timeline_markers.new(nome, frame=fa); m.camera = cam
    d = 0.3 * (Vector(alvo) - Vector(p0)).length
    if entra:
        TR.rampa_inicio(cam, fa, P6.DIRS[entra], d, 4)
    if sai:
        TR.rampa_fim(cam, fb, P6.DIRS[sai], d, 4)
    return cam


def _cr(pts, s_):
    """Catmull-Rom por uma lista de pontos, s_ de 0 a 1 (passa por todos os pontos, sem quina)"""
    from mathutils import Vector
    P = [Vector(p) for p in pts]
    if len(P) == 1:
        return P[0].copy()
    n = len(P) - 1; x = min(max(s_, 0.0), 1.0) * n; i = min(int(x), n - 1); u = x - i
    p0 = P[max(0, i - 1)]; p1, p2 = P[i], P[i + 1]; p3 = P[min(n, i + 2)]
    return 0.5 * ((2 * p1) + (-p0 + p2) * u + (2 * p0 - 5 * p1 + 4 * p2 - p3) * u * u + (-p0 + 3 * p1 - 3 * p2 + p3) * u ** 3)


def _mola_vec(alvos, hz, zeta, v0=None, sub=8):
    """o operador de câmera: persegue a trajetória com um pouco de atraso, acelera e freia em onda e assenta (passa de leve do ponto)"""
    from mathutils import Vector
    w = 2 * math.pi * hz; dt = 1.0 / (24 * sub)
    v = v0.copy() if v0 is not None else Vector((0, 0, 0))
    x = alvos[0] - v * (2 * zeta / w); out = []                                # entrando em movimento: já no atraso de regime, sem tranco
    for i, a in enumerate(alvos):
        a0 = alvos[i - 1] if i else a
        for k in range(sub):
            at = a0.lerp(a, (k + 1) / sub)
            v += (w * w * (at - x) - 2 * zeta * w * v) * dt; x += v * dt
        out.append(x.copy())
    return out


def camera_cine(c, nome, t0, t1, caminho, alvos, lens=16, fstop=4.0, v_in=0.0, v_out=0.0, segue=None, peso=0.6, hz=1.7, zeta=0.8, assenta=0.04, impacto=None, rampa_in=None, rampa_out=None, lens_keys=None, filtro=None, clip=0.3):
    """câmera de operador (pedido de 23/10/2026: "movimento duro, câmera sem as ondas in/out"):
    - anda por uma curva (caminho, vários pontos) e mira numa curva de alvos;
    - o tempo vai na curva in/out: v_in/v_out = velocidade na entrada/saída do plano (0 = sai/para em onda; 1 = velocidade média).
      Dentro de uma sequência, corte com a câmera andando dos dois lados (v_out de um plano = v_in do seguinte);
    - segue = objeto (ou lista de objetos) que a mira acompanha de verdade, com atraso de operador (peso = quanto puxa a mira);
    - a mira passa por uma mola (hz, zeta): o operador reage ao que se mexe com um pouco de atraso;
    - assenta = quando o plano termina parado (v_out = 0), a câmera passa esse tanto do ponto e volta (a onda de chegada);
    - impacto = (t, metros): o soco do acerto (junto com o grave): a câmera avança esse tanto em 3 quadros e volta em onda, sem tremer;
    - lens_keys = [(quadro, lente), ...]: a lente muda em curva suave (o dolly zoom: câmera entra e a lente abre ao mesmo tempo);
    - filtro = [(quadro, tinta 0..1, vinheta 0..1), ...]: o efeito de tempo distorcido preso à câmera (tinta fria + bordas escuras), em curva;
    - rampa_out / rampa_in = (direção, k[, n]): o corte em rampa de velocidade (in, meio, out). Nos últimos n quadros a câmera acelera
      (ease in, u³) na direção dada; no plano seguinte ela nasce deslocada e freia (ease out, (1-u)³). O pico de velocidade fica no corte,
      e o desfoque de movimento borra só ali. A direção é da própria câmera ("direita", "esquerda", "cima", "baixo", "frente"),
      então os dois lados andam para o mesmo lado da tela. k = fração da distância de foco (k igual = mesma velocidade de tela)"""
    from mathutils import Vector
    sc = c["sc"]
    cd = bpy.data.cameras.new(nome); cam = bpy.data.objects.new(nome, cd); sc.collection.objects.link(cam)
    cd.lens = lens; cd.sensor_fit = "HORIZONTAL"; cd.sensor_width = 24
    cd.clip_start = clip; cd.clip_end = 150.0                                  # perto demais = a profundidade perde a precisão e o chão pisca; só os macros usam 0,02
    cd.dof.use_dof = True; cd.dof.aperture_fstop = fstop
    fa, fb = F(t0), F(t1)
    fr = list(range(fa - 1, fb + 2)); n = max(1, fb - fa)

    def herm(t, a0, a1, m0, m1):
        return (2 * t ** 3 - 3 * t ** 2 + 1) * a0 + (t ** 3 - 2 * t ** 2 + t) * m0 + (-2 * t ** 3 + 3 * t ** 2) * a1 + (t ** 3 - t ** 2) * m1

    def tempo(f):
        t = min(max((f - fa) / n, 0.0), 1.0)
        if v_out or not assenta:
            return herm(t, 0.0, 1.0, v_in, v_out)
        if t <= 0.78:                                                             # chega passando do ponto...
            return herm(t / 0.78, 0.0, 1.0 + assenta, v_in * 0.78, 0.0)
        u = (t - 0.78) / 0.22                                                     # ...e volta assentando
        return 1.0 + assenta * (1 - u * u * (3 - 2 * u))
    segs = segue if isinstance(segue, (list, tuple)) else ([segue] if segue else [])
    pos, mira = [], []
    for f in fr:
        u = tempo(f)
        pos.append(_cr(caminho, u)); al = _cr(alvos, u)
        if segs:
            sc.frame_set(min(max(f, fa), fb))                                     # fora do plano não conta: a bola que volta ao ponto no corte puxava a mira (60°/s na entrada)
            m = sum((o.matrix_world.translation for o in segs), Vector((0, 0, 0))) / len(segs)
            al = al.lerp(m, peso)
        mira.append(al)
    sc.frame_set(fa)
    if impacto:
        ti, amp = impacto; fi = 1 + round(ti * 24)
        for k, f in enumerate(fr):
            dt = (f - fi) / 24.0
            if dt > 0:
                b = (1 - math.exp(-dt / 0.07)) * math.exp(-dt / 0.28) / 0.5           # sobe em ~3 quadros, volta devagar em onda (pico ~1)
                pos[k] = pos[k] + (mira[k] - pos[k]).normalized() * amp * b
    m0 = (mira[2] - mira[1]) * 24.0 if v_in else None                        # entra já andando (corte em movimento)
    mira = _mola_vec(mira, hz * 1.3, zeta, m0)
    EIXO = dict(direita=(1, 0, 0), esquerda=(-1, 0, 0), cima=(0, 1, 0), baixo=(0, -1, 0), frente=(0, 0, -1))
    for f, p_, a_ in zip(fr, pos, mira):
        rq = (a_ - p_).to_track_quat("-Z", "Y"); dist = (a_ - p_).length
        for rp, saindo in ((rampa_out, True), (rampa_in, False)):
            if not rp:
                continue
            nr = rp[2] if len(rp) > 2 else 5; d_ = rq @ Vector(EIXO[rp[0]]) * rp[1] * dist
            if saindo and f > fb - 1 - nr:                                   # o pico (u = 1) cai no último quadro visível, não no escondido pelo corte
                u = (f - (fb - 1 - nr)) / nr; p_ = p_ + d_ * (u ** 3 if u <= 1 else 1 + 3 * (u - 1))
            if not saindo and f < fa + nr:
                u = max(0.0, (f - fa) / nr); p_ = p_ - d_ * (1 - u) ** 3
        cam.location = p_; cam.rotation_euler = rq.to_euler()
        key(cam, "location", f, "LINEAR"); key(cam, "rotation_euler", f, "LINEAR")
        cd.dof.focus_distance = (a_ - p_).length; cd.dof.keyframe_insert("focus_distance", frame=f)
    lente = lambda f: _chaves(lens_keys, f) if lens_keys else lens
    if lens_keys:
        for f in fr:
            cd.lens = lente(f); cd.keyframe_insert("lens", frame=f)
    if filtro and not LIMPO:
        filtro_camera(cam, [f for f in fr], lente, lambda f: _chaves([(q, t) for q, t, v in filtro], f), lambda f: _chaves([(q, v) for q, t, v in filtro], f),
                      dist=max(0.3, clip * 1.25 + 0.02))                    # no mesmo plano do corte da câmera o filtro era cortado na diagonal (triângulo azul)
    m = sc.timeline_markers.new(nome, frame=fa); m.camera = cam
    return cam


def _chaves(ks, f):
    """valor em curva suave (smoothstep) entre as chaves [(quadro, valor), ...]; fora delas, o da ponta"""
    ks = sorted(ks)
    if f <= ks[0][0]:
        return ks[0][1]
    for (fa_, va), (fb_, vb) in zip(ks, ks[1:]):
        if fa_ <= f <= fb_:
            u = (f - fa_) / max(1, fb_ - fa_); u = u * u * (3 - 2 * u)
            return va + (vb - va) * u
    return ks[-1][1]


def filtro_camera(cam, frames, lente, tinta, vinheta, cor="#0a3f5a", dist=0.3):
    """efeito de tempo distorcido, colado na câmera: um plano de emissão azul-petróleo, translúcido, logo na frente da lente. O alfa soma
    uma tinta fria (a imagem inteira) e uma vinheta (bordas escuras que fecham, como a visão em túnel de quem acelera).
    O plano acompanha a lente (o plano sempre cobre o quadro), então a vinheta fica no lugar mesmo com a lente mudando"""
    me = bpy.data.meshes.new(cam.name + "_fm")
    me.from_pydata([(-1, -16 / 9, 0), (1, -16 / 9, 0), (1, 16 / 9, 0), (-1, 16 / 9, 0)], [], [(0, 1, 2, 3)])
    uv = me.uv_layers.new(name="UVMap")
    for k, q in enumerate(((0, 0), (1, 0), (1, 1), (0, 1))):
        uv.data[k].uv = q
    o = bpy.data.objects.new(cam.name + "_filtro", me); bpy.context.scene.collection.objects.link(o)
    o.parent = cam; o.location = (0, 0, -dist); o.visible_shadow = False
    m = bpy.data.materials.new(cam.name + "_fm"); m.use_nodes = True; m.surface_render_method = "BLENDED"
    nt = m.node_tree; nt.nodes.clear(); N = nt.nodes.new
    tc = N("ShaderNodeTexCoord"); sub = N("ShaderNodeVectorMath"); sub.operation = "SUBTRACT"; sub.inputs[1].default_value = (0.5, 0.5, 0)
    ln = N("ShaderNodeVectorMath"); ln.operation = "LENGTH"
    mr = N("ShaderNodeMapRange"); mr.inputs["From Min"].default_value = 0.26; mr.inputs["From Max"].default_value = 0.72; mr.clamp = True
    mv = N("ShaderNodeMath"); mv.operation = "MULTIPLY"; mv.use_clamp = True
    mt = N("ShaderNodeMath"); mt.operation = "ADD"; mt.use_clamp = True
    em = N("ShaderNodeEmission"); em.inputs["Color"].default_value = (*lib.srgb(cor), 1)
    tr = N("ShaderNodeBsdfTransparent"); mx = N("ShaderNodeMixShader"); out = N("ShaderNodeOutputMaterial")
    L = nt.links.new
    L(tc.outputs["UV"], sub.inputs[0]); L(sub.outputs[0], ln.inputs[0]); L(ln.outputs["Value"], mr.inputs["Value"])
    L(mr.outputs["Result"], mv.inputs[0]); L(mv.outputs[0], mt.inputs[0]); L(mt.outputs[0], mx.inputs[0])
    L(tr.outputs[0], mx.inputs[1]); L(em.outputs[0], mx.inputs[2]); L(mx.outputs[0], out.inputs["Surface"])
    m.node_tree.nodes.active = out
    o.data.materials.append(m)
    for f in frames:
        t_, v_ = tinta(f), vinheta(f)
        mv.inputs[1].default_value = 0.5 * v_; mv.inputs[1].keyframe_insert("default_value", frame=f)
        mt.inputs[1].default_value = 0.13 * t_; mt.inputs[1].keyframe_insert("default_value", frame=f)
        e = dist * 12.0 / max(1.0, lente(f)) * 1.06
        o.scale = (e, e, 1.0); key(o, "scale", f, "LINEAR")
    for f_ in (frames[0] - 1, frames[-1] + 1):                                  # fora do plano dela o filtro some (senão aparece nas outras câmeras)
        o.scale = (0.0001, 0.0001, 1.0); key(o, "scale", f_, "CONSTANT")
    return o


def mostra_ate(o, f0, f1):
    """aparece em f0 e some em f1 (para o que só existe numa parte da cena)"""
    UN.esconde_ate(o, f0)
    if f1:
        UN.some(o, f1, 2)


def objs_novos(antes):
    return [o for o in bpy.data.objects if o.name not in antes and o.parent is None]


# ====================================================================== 1. a mosca e o copo (fala 1) — v2 cinematográfica, em 3D
@cena_(1)
def s01(c):
    """v2 ("tem que ser cinematográfico"): cozinha em 3D. Uma mosca zumbe em volta da cabeça dele; no "10 vezes mais rápido" o tempo desacelera
    (a poeira para no ar, a mosca bate as asas devagar) e ele pega a mosca com um tapa; close de 12 mm no punho, só a cabeça da mosca para fora.
    "Um copo cai da mesa": câmera no chão, o copo cai em câmera lenta soltando gotas; "e sua mão já está embaixo": a mão entra, o copo pousa,
    as gotas voltam e o ar se abre numa onda"""
    import cinema3d as C3
    from mathutils import Vector, Matrix
    A, END = F(-0.4), F(B[1] + 0.4)
    p = pal("cozinha"); mundo(p); wy = 3.2
    AM.sala("coz", -3.0, 3.0, -6.0, wy, 3.0, dict(parede="#d8b988", lateral="#c4a374", teto="#9a7650", viga="#7a5a3c", chao="#9a7a54",
            linha="#7a5c3c", pilastra="#cbb088"), piso="tabuas", passo_pilastra=0, passo_viga=0)
    props.poly("jan_luz", rrect(-2.2, 1.2, -0.7, 2.6, 0.04, 3), "#fff6dc", wy - 0.02)
    props.poly("jan_mx", cena.rect(-1.465, 1.2, -1.435, 2.6), p["pedra"], wy - 0.03)
    props.poly("jan_mz", cena.rect(-2.2, 1.88, -0.7, 1.92), p["pedra"], wy - 0.03)
    cena.disc("jan_gl", 2.4, cena.amat("jan_gl_m", "#fff0c8", 1.0, 0.3, ("radial", 1.5)), (-1.45, wy - 0.05, 1.9))
    S.caixa3d(p, "armario", 1.9, 2.4, 1.6, 0.92, d=0.7, cor="#7a5a3a", tampo="#b38f5f", aresta=p["aresta"])
    props.poly("relogio_p", circle(0.9, 2.35, 0.22, 32), "#f6efe0", wy - 0.02)
    props.poly("relogio_h", stroke([(0.9, 2.35), (0.9, 2.5)], 0.012), "#2a2018", wy - 0.03)
    for k in range(3):
        props.poly(f"prat{k}", rrect(-0.3 + k * 0.33, 1.55, -0.06 + k * 0.33, 1.8, 0.03, 3), ["#c8323e", "#2a7a5a", "#e8c76a"][k], wy - 0.03)
    H = heroi3("voce1", 0.0, 0.6, p)
    H.rosto(boca="reta", lid=0.0)
    sc = c["sc"]
    # tempos: a pegada da mosca no "10 vezes mais rápido", a pausa (a voz tem 1,5 s de silêncio aqui: o tempo para e a mosca se debate no punho),
    # e então o copo: inclina no "copo", cai no "cai", a mão já chega embaixo no "sua" e o copo pousa nela no "embaixo"
    f_10, f_c = F(wt(1, "10")), F(2.22)
    f_tomba, f_cai = F(wt(1, "copo")), F(wt(1, "cai"))
    f_mao0, f_mao = F(wt(1, "e")), F(wt(1, "mão"))                           # a mão sai no "e" e chega por baixo do copo no "mão"
    f_pousa = F(wt(1, "já"))                                                  # o copo encosta na palma no "já": corte para o olhar dele
    lento = C3.tempo_lento(f_10 - 3, 0.12, 8)                                # o tempo freia em curva (não de uma vez)
    # poses. Mosca: a mão direita (F) varre de lado e fecha no ar, esticada para a frente e para cima
    pega_p = dict(PARADO, ombro=(-112, 6), cotovelo=(-14, -10), abre=(10, 6))
    H.pose(**pega_p); bpy.context.view_layer.update()
    H.fecha_mao("F", em=f_c); bpy.context.view_layer.update()
    mw = H.punho["F"].matrix_world
    p_f = mw @ Vector((0, 0, -0.06))                                          # centro do punho fechado
    a = (mw.to_3x3() @ Vector((0, 0, -1))).normalized()                       # direção do braço (para onde o punho aponta)
    cima = (mw.to_3x3() @ Vector((0, -1, 0))).normalized()                   # lado dos nós dos dedos
    d = p_f - (H.cabeca.matrix_world.translation + Vector((0, 0, 0.16)))
    olhar = dict(olha=math.degrees(math.atan2(d.x, -d.y)) * 0.8, cabeca=-math.degrees(math.atan2(d.z, Vector((d.x, d.y)).length)) * 0.8)
    pega_p.update(olhar)
    H.pose(**pega_p); bpy.context.view_layer.update()
    mw = H.punho["F"].matrix_world; R3 = mw.to_3x3()
    buraco = Vector((-0.04, -0.026, -0.07))                                   # o furo do punho do lado do polegar (F: polegar em -X)
    p_pega = mw @ (buraco + Vector((-0.016, 0, 0)))                            # onde fica a cabeça da mosca
    ext = (R3 @ Vector((-1, 0, 0))).normalized()                              # para fora do furo
    # segura a mosca junto ao peito enquanto olha o copo
    segura = dict(PARADO, ombro=(-48, 6), cotovelo=(-78, -10), abre=(16, 6), olha=26, cabeca=14)
    # copo: agacha de verdade (pés no chão), a mão esquerda (B) espalmada para cima, à frente e ao lado; o pulso deixa a palma de nível
    palma = H.espalma("B", em=f_mao0 + 2)

    def agachado(k, pu):
        """k = 0 (de pé) a 1 (agachamento fundo); a mão esquerda vai à frente e ao lado, espalmada (pulso pu)"""
        tr = -14 - 16 * k                                                     # o tronco inclina e leva o braço junto: o ombro desconta isso
        return H.pe_no_chao(**dict(PARADO, quadril=(-30 - 52 * k, -20 - 50 * k), joelho=(40 + 80 * k, 30 + 78 * k), tornozelo=(-14 - 26 * k, -12 - 26 * k),
                                   tronco=tr, ombro=(-48 - tr, -42 - tr), cotovelo=(-78, -12), abre=(16, 30), olha=30, cabeca=20 + 10 * k, punho=(0, pu)))

    def mede(P):
        H.pose(**P); bpy.context.view_layer.update()
        return palma.matrix_world.translation.copy(), (H.punho["B"].matrix_world.to_3x3() @ Vector((0, -1, 0))).normalized().z
    Z_MAO = 0.47                                                              # a mão bem abaixo do tampo (0,745): o copo cai uns 27 cm até ela
    kk = min((abs(mede(agachado(k / 20, -40))[0].z - Z_MAO), k / 20) for k in range(21))[1]
    pu = max((mede(agachado(kk, u))[1], u) for u in range(-80, 32, 2))[1]    # dobra do pulso que deixa a palma virada para cima
    recebe = agachado(kk, pu)
    P_ = mede(recebe)[0]
    chega = agachado(kk * 0.93, pu)
    H.pose(**recebe); bpy.context.view_layer.update()
    oF, oB = bpy.data.objects[H.nome + "_olhoF"].matrix_world.translation, bpy.data.objects[H.nome + "_olhoB"].matrix_world.translation
    cab = bpy.data.objects[H.nome + "_cranio"].matrix_world.translation
    meio = (oF + oB) / 2; ff = (meio - cab).normalized()
    olho = meio + ff * 0.1 + Vector((0, 0, 0.03))                             # os olhos dele (10 cm à frente do rosto: o ombro não encosta na lente)                                            # a mão entra um pouco mais alta e desce junto com o copo
    print("QUADRO agachado", kk, "pulso", pu, "alt", round(recebe["alt"], 3), "palma", tuple(round(v, 2) for v in P_))
    amortece = dict(recebe, ombro=(-48, recebe["ombro"][1] + 3), cotovelo=(-78, -9))             # o copo pousa e a mão desce um pouco junto
    # a mosca: voa rápido em volta da cabeça; em câmera lenta vai até a mão e some dentro do punho
    m1, asas1 = C3.mosca("mosca1", (0.2, 0.25, 1.6), escala=3.0)
    C3.voo(m1, A, f_c, (0.0, 0.25, 1.55), raio=(0.32, 0.22, 0.18), seed=5, vel=C3.tempo_lento(f_10 - 3, 0.1, 8), ate=tuple(p_pega), f_ate=f_c)
    C3.bate_asas(asas1, A, f_c, periodo=lambda f: 2.0 + 9.0 * (1.0 - lento(f)) / 0.88)   # a batida das asas desacelera junto com o tempo
    # ele acompanha a mosca com a cabeça (a mola dá o atraso natural) e balança o peso de um pé para o outro
    H.pose(**PARADO); bpy.context.view_layer.update(); olho0 = H.cabeca.matrix_world.translation + Vector((0, 0, 0.16))
    segue_mosca = []
    for k_, f in enumerate(range(A, f_10 + 3, 5)):
        sc.frame_set(f); d_ = m1.matrix_world.translation - olho0
        segue_mosca.append((f, dict(PARADO, olha=max(-40, min(40, math.degrees(math.atan2(d_.x, -d_.y)) * 0.75)),
                                    cabeca=max(-20, min(14, -math.degrees(math.atan2(d_.z, Vector((d_.x, d_.y)).length)) * 0.7)),
                                    inclina=1.5 * math.sin(k_ * 0.9), giro=3 * math.sin(k_ * 0.6))))
    sc.frame_set(A)
    ch = segue_mosca + [
          (f_c - 9, dict(PARADO, ombro=(-14, 6), cotovelo=(-34, -10), abre=(12, 6), tronco=3, alt=0.83, **olhar)),                  # antecipa pouco: dobra os joelhos, a mão sobe solta ao lado do corpo
          (f_c - 4, dict(PARADO, ombro=(-20, 6), cotovelo=(-48, -10), abre=(12, 6), tronco=4, alt=0.825, **olhar)),                 # segura parado (olho na mosca): o tapa vem do nada
          (f_c - 2, dict(pega_p, ombro=(-74, 6), cotovelo=(-62, -10), tronco=-2, alt=0.84)),                                           # o cotovelo puxa, o antebraço vem atrasado
          (f_c, dict(pega_p, tronco=-6)),                                                                                              # o golpe fecha em 4 quadros
          (f_c + 3, dict(pega_p, ombro=(-116, 6), cotovelo=(-10, -10), tronco=-8)),                                                     # passa um pouco do ponto, o corpo vai junto
          (f_c + 12, dict(pega_p, tronco=-3)), (f_tomba - 6, dict(pega_p, ombro=(-106, 6))),                                          # assenta onde o macro mira
          (f_tomba + 8, segura), (f_mao0, dict(segura, ombro=(-48, 10), abre=(16, 0), cabeca=18)),
          (f_mao, chega), (f_pousa, recebe), (f_pousa + 6, amortece), (f_pousa + 18, recebe), (END, dict(recebe, cabeca=16))]
    H.anima(ch, A, END, vida=0.6, molas=dict(ombro=(0, 12.0, 0.55), abre=(0, 10.0, 0.6), cotovelo=(1, 13.0, 0.5), punho=(1, 12.0, 0.5), tronco=(0, 5.0, 0.6), cabeca=(1, 4.0, 0.55)))
    H.rosto(boca="reta", lid=0.0)
    # a mosca some no quadro em que o furo do punho (que chega com a mola) passa por ela: nada de mosca ao lado do punho
    furo = lambda f: (sc.frame_set(f), H.punho["F"].matrix_world @ (buraco + Vector((-0.016, 0, 0))))[1]
    f_pg = min(range(f_c - 1, f_c + 6), key=lambda f: (furo(f) - p_pega).length); sc.frame_set(A)
    print("PEGA quadro", f_pg, "(f_c", f_c, ")")
    UN.some(m1, f_pg - 1, 1)                                                  # no quadro f_pg só a presa (dentro do punho) aparece
    # a mosca presa: só a cabeça para fora do furo do punho; na pausa ela se debate (a cabeça vira e as asas batem presas)
    piv = empty("mosca2_piv", H.punho["F"], tuple(buraco))
    m2, asas2 = C3.mosca("mosca2", (0, 0, 0), escala=6.0, pai=piv)
    yy, up = Vector((1, 0, 0)), Vector((0, -1, 0))                            # a frente da mosca (-Y dela) sai pelo furo; o dorso para o lado dos nós
    base_rot = Matrix((yy.cross(up), yy, up)).transposed()
    for f in range(f_c, END + 1, 4):                                           # a mosca presa fica firme: só balança um pouquinho (3°), sem tremer
        t = (f - f_c) / 24.0
        piv.rotation_euler = (Matrix.Rotation(math.radians(3 * math.sin(2 * math.pi * 0.8 * t)), 3, "Z") @ base_rot).to_euler()
        key(piv, "rotation_euler", f, "LINEAR")
    UN.esconde_ate(m2, f_pg); C3.bate_asas(asas2, f_c + 1, END, periodo=8.0, amp=12)
    # o ar: poeira suspensa que desacelera; a pegada empurra a poeira e abre um anel de ar de frente para a câmera de 12 mm
    C3.poeira("po1", (0.0, 0.0, 1.5), (1.0, 0.9, 0.7), 14, A, END, vel=lento, seed=8, empurra=(f_c, tuple(p_f), 0.16), cor="#f3dcb0",
              longe=((tuple(p_pega + a * 0.12 + ext * 0.1 + cima * 0.07), 0.38),))
    C3.onda("onda1", tuple(p_f), F(2.3), normal=tuple(a), raio=0.42, dur=22, esp=0.005)
    # o balcão e o copo: a borda do balcão fica logo à direita de onde a mão espalmada vai estar
    xe = P_.x + 0.075; ty = P_.y - 0.3
    OB.caixa("balcao_c", xe + 0.58, ty + 0.04, 0.0, 1.04, 0.70, 0.58, "#8a6440", tampo="#a67c52", lado="#74522f", aresta="#b48a5e")
    OB.caixa("balcao_t", xe + 0.55, ty, 0.70, 1.1, 0.045, 0.66, "#a67c52", tampo="#c89868", lado="#946a44", aresta="#e8c898")
    OB.caixa("balcao_r", xe + 0.58, ty + 0.035, 0.0, 1.04, 0.08, 0.02, "#4a3420", tampo="#4a3420", lado="#4a3420")
    for k in range(2):
        OB.caixa(f"balcao_g{k}", xe + 0.32 + 0.52 * k, ty + 0.02, 0.56, 0.16, 0.022, 0.02, "#e8c898", tampo="#f4dcb0", lado="#c8a878")
    H3.esfera("prato", 0.12, 0.12, 0.012, H3.estilo("#f4f1ea", "#cfcabd"), None, (xe + 0.75, ty + 0.35, 0.752), contorno=0.003)
    H3.esfera("maca", 0.04, 0.04, 0.04, H3.estilo("#c8323e", "#8a1f27"), None, (xe + 0.73, ty + 0.35, 0.8), contorno=0.003)
    G = Vector((xe + 0.045, P_.y, 0.745))
    cp = C3.copo3d("copo1", tuple(G), 1.25)
    gs = C3.gotas("gota", cp, n=10, z0=0.075)
    na_palma = lambda f: (sc.frame_set(f), palma.matrix_world.translation.copy())[1]
    p_pousa = na_palma(f_pousa)
    borda = Vector((xe + 0.004, P_.y, 0.745))
    for f in range(A, END + 1):
        if f < f_tomba:
            loc, ry = G.copy(), 0.0
        elif f < f_cai:                                                       # escorrega para a borda e tomba
            u = (f - f_tomba) / max(1, f_cai - f_tomba); u = u * u * (3 - 2 * u)
            loc = G.lerp(borda, u); ry = -20 * u
        elif f < f_pousa:                                                     # cai (câmera lenta, acelerando) girando, e endireita perto da mão
            u = (f - f_cai) / max(1, f_pousa - f_cai); v = 0.7 * u * u + 0.3 * u
            loc = borda.lerp(p_pousa, v); loc.z = borda.z + (p_pousa.z - borda.z) * v
            ry = -20 - 18 * math.sin(min(1.0, u / 0.7) * math.pi / 2) if u < 0.7 else -38 * (1 - ((u - 0.7) / 0.3) ** 0.8)
        else:                                                                 # pousou: vai junto com a palma, que amortece
            loc, ry = na_palma(f), 0.0
        cp.location = loc; cp.rotation_euler = (0, math.radians(ry), 0)
        key(cp, "location", f, "LINEAR"); key(cp, "rotation_euler", f, "LINEAR")
    sc.frame_set(A)
    C3.sobe_volta(gs, f_cai + 3, (f_cai + f_pousa) // 2, f_pousa + 8, alcance=0.1, z0=0.075)
    C3.poeira("po2", (P_.x + 0.02, P_.y - 0.1, 0.55), (0.6, 0.5, 0.5), 6, A, END, vel=lambda f: 0.12, seed=9, empurra=(f_pousa, tuple(P_), 0.12),
              cor="#f3dcb0", longe=(((P_.x - 0.32, P_.y - 0.55, 0.6), 0.3), ((G.x - 0.4, G.y - 0.4, 0.8), 0.3), (tuple(olho), 0.3)), tam=(0.0015, 0.0035))
    C3.onda("onda2", tuple(P_ + Vector((0, 0, 0.05))), f_pousa, normal=tuple(olho - P_), raio=0.3, dur=18, esp=0.005)   # de frente para o olhar dele
    # o rosto: atento na mosca, sorri quando pega; susto quando o copo tomba; foco na mão; alívio no fim
    H.expressao([(A, dict()), (f_10, dict(lid=0.35, brow=-0.6)), (f_c + 2, dict(boca="sorriso", brow=0.5)), (f_tomba, dict(boca="o", brow=0.8, olhos=1.12)),
                 (f_mao0, dict(lid=0.35, brow=-0.6)), (f_pousa + 4, dict(boca="sorriso", brow=0.4))], A, END, seed=3)
    # câmeras de operador, cortando sempre em movimento:
    # médio que se aproxima -> 3/4 que gira com a mão (tranco no acerto) -> 12 mm que gira devagar em volta do punho na pausa
    # -> lateral no balcão: o copo tomba -> de baixo: a mão já está lá e o copo pousa nela
    tB, tC, tD, tE = wt(1, "10") - 0.06, 2.3, wt(1, "um", 1) - 0.1, wt(1, "e") - 0.08
    tc_ = T(f_c)
    camera_cine(c, "cam1a", B[0], tC, [(0.42, -1.6, 1.62), (0.05, -1.2, 1.6), (-0.55, -0.72, 1.55), (-0.8, -0.42, 1.52)], [(0.0, 0.5, 1.5), (0.0, 0.4, 1.5)], lens=26, fstop=2.4,
                v_in=0.3, v_out=1.0, segue=H.cabeca, peso=0.35)                # um plano só, devagar: do médio de frente ao 3/4, até o tapa
    eixo = a.cross(cima).normalized()
    # o macro fica a ~17 cm (a 8 cm a mosca saía do foco e sumia: "a mosca fica muito próxima que acaba sumindo"); a mosca e o punho inteiros no quadro
    orb = [p_pega + (Matrix.Rotation(math.radians(g), 3, a) @ (a * 0.05 + ext * 0.15 + cima * 0.06)) for g in (-14, 0, 14)]
    camera_cine(c, "cam1c", tC, tD, orb + [p_pega + (Matrix.Rotation(math.radians(24), 3, a) @ (a * 0.05 + ext * 0.135 + cima * 0.055))],
                [p_pega + ext * 0.01 - a * 0.02], lens=18, fstop=5.6, clip=0.02, v_in=1.4, v_out=0.8, segue=H.punho["F"], peso=0.7, hz=3.0, impacto=(tc_, 0.02))
    # o copo: um plano só que começa na altura do balcão e desce junto com ele; a mão entra no quadro e encontra o copo
    camera_cine(c, "cam1d", tD, T(f_pousa), [(G.x - 0.44, G.y - 0.42, 0.86), (P_.x - 0.38, P_.y - 0.52, 0.66), (P_.x - 0.3, P_.y - 0.58, P_.z + 0.12)],
                [(G.x - 0.02, G.y, 0.8), (P_.x, P_.y, P_.z + 0.16)], lens=18, fstop=4.0, v_in=0.8, v_out=1.0, segue=cp, peso=0.35)
    # o copo bate na palma: corte para os olhos dele, olhando o copo na própria mão (a outra mão, com a mosca, entra no canto)
    camera_cine(c, "cam1f", T(f_pousa), B[1] + 0.4, [olho, olho + (P_ - olho) * 0.22], [P_ + Vector((0, 0, 0.06))], lens=26, fstop=2.8,
                v_in=0.5, v_out=0.0, segue=cp, peso=0.3, impacto=(T(f_pousa), 0.012))
    sc.render.use_motion_blur = True; sc.render.motion_blur_shutter = 0.5      # o gesto rápido borra como numa câmera de verdade


# ====================================================================== 2. um quarto de segundo contra 25 milésimos (fala 2)
def _braco_ate(z_baixo, y_mao, y0=0.86, z_ombro=1.265):
    """ângulos (ombro, cotovelo) de um braço esticado para a frente que leva a parte de baixo da mão (esfera de 4,1 cm) a (y_mao, z_baixo):
    resolvido no plano do braço (sem abrir), com preferência por um cotovelo dobrado de forma natural"""
    L1, L2, d, r = 0.29 * 1.18, 0.27 * 1.18, 0.042, 0.041
    melhor = None
    for t1 in range(-125, -4):
        for t2 in range(-130, -3):
            a1, a2 = math.radians(t1), math.radians(t1 + t2)
            y = y0 + L1 * math.sin(a1) + (L2 + d) * math.sin(a2); z = z_ombro - L1 * math.cos(a1) - (L2 + d) * math.cos(a2)
            err = 4 * (z - r - z_baixo) ** 2 + (y - y_mao) ** 2 + 2e-5 * (t2 + 55) ** 2 + 1e-5 * (t1 + 50) ** 2
            if melhor is None or err < melhor[0]:
                melhor = (err, t1, t2)
    return melhor[1], melhor[2]


def botao(nm, x, y, z0):
    """botão de reação (grande, vermelho, de arcade): base de aço e cúpula que afunda. Devolve (raiz, cúpula)"""
    r = empty(nm, None, (x, y, z0))
    H3.loft(nm + "_base", [(0.0, 0.11, 0.11), (0.012, 0.105, 0.105), (0.028, 0.09, 0.09)], H3.estilo("#3a4356", "#232a37"), r, expo=2.0, seg=40, contorno=0.003)
    cup = empty(nm + "_cup", r, (0, 0, 0.026))
    H3.loft(nm + "_dome", [(0.0, 0.074, 0.074), (0.012, 0.08, 0.08), (0.03, 0.07, 0.07), (0.046, 0.045, 0.045), (0.054, 0.012, 0.012)], H3.estilo("#e2364b", "#a8202f", limiar=0.4), cup,
            expo=2.0, seg=40, contorno=0.003)
    return r, cup


def lampada(nm, x, y, z, verdes, r=0.05, A=1, END=400):
    """lâmpada de largada sobre um poste: vermelha, mas verde nos intervalos de 'verdes' = [(quadro_ini, quadro_fim ou None), ...]"""
    H3.tubo(nm + "_poste", [(x, y, z - 0.12), (x, y, z)], [0.008, 0.008], H3.estilo("#3a4356", "#232a37"), None, contorno=0.002, seg=12, tampa=3)
    ve = H3.esfera(nm + "_ve", r, r, r, H3.plano("#e2364b"), None, (x, y, z + r), contorno=0.003, seg=28, an=16)
    vd = H3.esfera(nm + "_vd", r, r, r, H3.plano("#4fd18b"), None, (x, y, z + r), contorno=0.003, seg=28, an=16)
    verde = lambda f: any(a <= f and (b is None or f < b) for a, b in verdes)
    marcas = sorted({A, END} | {q for a, b in verdes for q in (a, b) if q is not None})
    for f in marcas:
        for o, vis in ((ve, not verde(f)), (vd, verde(f))):
            o.scale = (1, 1, 1) if vis else (0.0001,) * 3; key(o, "scale", f, "CONSTANT")
    return ve, vd


# ====================================================================== 2. um quarto de segundo contra 25 milésimos (fala 2)
@cena_(2)
def s02(c):
    """v3 ("não dá para entender; recriar de outro ângulo, mais clean"): vista alta, de frente e de cima, sobre uma mesa lisa com dois botões e um fundo liso.
    Cada botão tem um anel de sinal (vermelho -> verde) em volta. A pessoa normal (casaco claro) à esquerda e você (jaqueta vermelha) à direita; o número de cada um
    flutua em letras grandes acima da cabeça. 1º sinal: só o anel dela fica verde, ela aperta e aparece 0,250 s. 2º sinal: o tempo se dobra (anel de ar na mesa, o mundo
    a 1/10): você aperta na hora (0,025 s) e espera; a mão e o número dela se arrastam até apertar. Um plano só, lento, sem nada além disso"""
    import cinema3d as C3
    from mathutils import Vector
    A, END = F(B[1] - 0.4), F(B[2] + 0.4)
    mundo(dict(top="#1b4756")); sc = c["sc"]; y0 = 0.9
    cena.poly_mesh("piso2", [(-60, -60, 0), (60, -60, 0), (60, 60, 0), (-60, 60, 0)], props.FM("#1b4756"))
    # tempos do mundo: 1 normal; no 2º sinal cai a 0,1 em curva (5 quadros) e volta ao normal no fim
    f_l1 = F(6.55); f_s = F(8.85); f_r = F(12.35)
    suave = lambda u: 0.0 if u <= 0 else 1.0 if u >= 1 else u * u * u * (u * (6 * u - 15) + 10)
    def vt(f):
        return 1.0 - 0.9 * suave((f - f_s) / 5.0) + 0.9 * suave((f - f_r) / 8.0)
    def tela(f0, real):
        acc, f = 0.0, f0
        while acc < real:
            acc += vt(f); f += 1
        return f
    DESC = 4
    XN = 0.42
    Hn = heroi3("normal", -XN, y0, p_ := pal("lab"), roupa="#f1ece0", calca="#4a5468", escura="#c9c2b0", gola="#f1ece0")
    Hv = heroi3("voce2", XN, y0, p_)
    PAR = dict(PARADO, ombro=(-4, -4), cotovelo=(-14, -14), abre=(6, 6))
    z_tampo = 0.82; z_dn = z_tampo + 0.03 + 0.02
    t1d, t2d = _braco_ate(z_dn, y0 - 0.46); t1u, t2u = _braco_ate(z_dn + 0.17, y0 - 0.46)
    def pose(i, ombro, cot, **kw):
        o, ct, ab = [-4, -4], [-14, -14], [6, 6]
        o[i], ct[i], ab[i] = ombro, cot, 0
        return dict(PAR, ombro=tuple(o), cotovelo=tuple(ct), abre=tuple(ab), tronco=-3, **kw)
    pron_v, bate_v = pose(0, t1u, t2u, olha=-12, cabeca=22), pose(0, t1d, t2d, olha=-12, cabeca=26)
    pron_n, bate_n = pose(1, t1u, t2u, olha=12, cabeca=22), pose(1, t1d, t2d, olha=12, cabeca=26)
    Hv.pose(**bate_v); Hn.pose(**bate_n); bpy.context.view_layer.update()
    mao_v = Hv.punho["F"].matrix_world @ Vector((0.002, 0, -0.042)); mao_n = Hn.punho["B"].matrix_world @ Vector((0.002, 0, -0.042))
    xb_v, xb_n, yb = mao_v.x, mao_n.x, mao_v.y
    # a mesa: lisa, quente, com a borda clara (nada em cima além dos botões)
    OB.caixa("mesa_c", 0.0, 0.1, 0.0, 1.7, z_tampo - 0.04, 0.64, "#7a583a", tampo="#946a44", lado="#5e4329", aresta="#c9a06a")
    OB.caixa("mesa_t", 0.0, 0.08, z_tampo - 0.04, 1.74, 0.04, 0.68, "#c9a06a", tampo="#ead7b0", lado="#b08a58", aresta="#fff0cc")
    bt_v, cup_v = botao("bot_v", xb_v, yb, z_tampo); bt_n, cup_n = botao("bot_n", xb_n, yb, z_tampo)
    DOWN = -0.03
    def afunda(cup, intervalos):
        for ini, fim in intervalos:
            cup.location = (0, 0, 0.026); key(cup, "location", ini - 1, "LINEAR")
            cup.location = (0, 0, 0.026 + DOWN); key(cup, "location", ini + 1, "LINEAR")
            if fim:
                key(cup, "location", fim, "LINEAR"); cup.location = (0, 0, 0.026); key(cup, "location", fim + 3, "LINEAR")
    f_n1a = f_l1 + 6; f_n1p = f_n1a + DESC
    f_sol1 = F(8.0)
    f_v2a = f_s + 1; f_v2p = f_v2a + DESC
    f_n2a = tela(f_s, 6); f_n2p = tela(f_s, 6 + DESC)
    f_sol2 = f_r + 6
    afunda(cup_n, [(f_n1p, f_sol1), (f_n2p, None)]); afunda(cup_v, [(f_v2p, f_sol2)])
    # anel de sinal em volta de cada botão: vermelho, e verde nos intervalos (a luz da largada)
    def anel(nm, x, verdes):
        pts = [(x + 0.135 * math.cos(2 * math.pi * k / 40), yb + 0.135 * math.sin(2 * math.pi * k / 40), z_tampo + 0.008) for k in range(41)]
        v_ = H3.tubo(nm + "_v", pts, [0.012] * 41, H3.plano("#e2364b"), None, contorno=0.0, seg=10, tampa=2)
        g_ = H3.tubo(nm + "_g", pts, [0.012] * 41, H3.plano("#4fd18b"), None, contorno=0.0, seg=10, tampa=2)
        verde = lambda f: any(a_ <= f and (b_ is None or f < b_) for a_, b_ in verdes)
        for f in sorted({A, END} | {q for a_, b_ in verdes for q in (a_, b_) if q is not None}):
            for o, vis in ((v_, not verde(f)), (g_, verde(f))):
                o.scale = (1, 1, 1) if vis else (0.0001,) * 3; key(o, "scale", f, "CONSTANT")
    anel("sn", xb_n, [(f_l1, f_sol1), (f_s, None)]); anel("sv", xb_v, [(f_s, None)])
    # os números: letras grandes acima da cabeça de cada um, viradas para a câmera
    mt_ = props.FM("#c9ffd8", 1.7); mb_ = props.FM("#ffffff", 1.2)
    from lib import text as _text
    def numeros(nm, x, estados):
        if LIMPO:
            return
        for k, (tx, ini, fim) in enumerate(estados):
            t = _text(f"{nm}{k}", tx, 0.16, mt_, None, (x, y0 + 0.05, 1.9), lib.font()); t.rotation_euler = (math.radians(42), 0, 0)
            for fr_, vis in ((A, ini <= A and (fim is None or fim > A)), (ini, True), (fim, False)):
                if fr_ is None:
                    continue
                t.scale = (1, 1, 1) if vis else (0.0001,) * 3; key(t, "scale", fr_, "CONSTANT")
    est_n = [("0,250 s", f_n1p, f_sol1 + 6)]                                  # só o número medido: nada de zeros nem de contagem
    numeros("num_n", -XN, est_n); numeros("num_v", XN, [("0,025 s", f_v2p, None)])
    # ---- animação
    ch_v = [(A, pron_v), (f_v2a - 1, pron_v), (f_v2p, bate_v), (f_v2p + 14, dict(bate_v, olha=-38, cabeca=18)), (f_r, dict(bate_v, olha=-38, cabeca=18)),
            (f_r + 14, dict(pron_v, olha=-14, cabeca=20)), (END, dict(pron_v, olha=-14, cabeca=20))]
    ch_n = [(A, pron_n), (f_n1a - 1, pron_n), (f_n1p, bate_n), (f_sol1 - 8, bate_n), (f_sol1 + 6, pron_n), (f_n2a - 1, pron_n), (f_n2p, bate_n), (END, bate_n)]
    seco = dict(ombro=(0, 6.2, 0.7), cotovelo=(1, 6.8, 0.66), punho=(1, 7.0, 0.6))
    Hv.anima(ch_v, A, END, vida=0.4, molas=seco, seed=4); Hn.anima(ch_n, A, END, vida=0.5, molas=dict(ombro=(0, 4.6, 0.72), cotovelo=(1, 5.0, 0.68), punho=(1, 5.0, 0.62)), seed=9)
    Hv.rosto(boca="sorriso", lid=0.0); Hn.rosto(boca="reta", lid=0.0)
    Hv.expressao([(A, dict(boca="sorriso", lid=0.15)), (f_s, dict(lid=0.4, brow=-0.6)), (f_v2p + 3, dict(boca="sorriso", brow=0.3))], A, END, seed=4)
    Hn.expressao([(A, dict()), (f_l1, dict(lid=0.3, brow=-0.4)), (f_n1p + 3, dict(brow=0.2)), (f_v2p + 6, dict(boca="o", brow=0.8, olhos=1.15))], A, END, seed=9)
    # ---- o ar: um anel de tempo deitado na mesa no 2º sinal e um quente quando volta; um anel pequeno em cada aperto
    ctr = (0.0, yb, z_tampo + 0.01)
    C3.onda("tw0", ctr, f_s, normal=(0, 0, 1), raio=1.1, dur=30, esp=0.02, cor="#a8ecff")
    C3.onda("tr0", ctr, f_r, normal=(0, 0, 1), raio=0.9, dur=22, esp=0.016, cor="#ffe6b0")
    for nm, x, fp in (("an1", xb_n, f_n1p), ("an2", xb_v, f_v2p), ("an3", xb_n, f_n2p)):
        C3.onda(nm, (x, yb, z_tampo + 0.05), fp, normal=(0, 0, 1), raio=0.3, dur=16, esp=0.006)
    def eco(nm, H_, s_, f_i, f_p, passo, vida, r_):
        if LIMPO:
            return
        k = 0
        for f in range(f_i, f_p + 1, passo):
            sc.frame_set(f); pos_ = H_.punho[s_].matrix_world @ Vector((0.002, 0, -0.042))
            g = H3.esfera(f"{nm}{k}", r_, r_, r_, H3.plano("#a8ecff"), None, tuple(pos_), contorno=0.0, seg=16, an=10)
            g.scale = (0.0001,) * 3; key(g, "scale", f - 1, "CONSTANT")
            g.scale = (1, 1, 1); key(g, "scale", f, "LINEAR"); g.scale = (0.0001,) * 3; key(g, "scale", f + vida, "LINEAR")
            k += 1
    eco("ecoV", Hv, "F", f_v2a, f_v2p, 1, 8, 0.03)
    sc.frame_set(A)
    # ---- três planos (pedido de 23/10/2026: "câmera de 12 mm quando ele aperta o botão"):
    # alto e de frente (os dois e os botões) -> no "Você", 12 mm rente ao tampo, colada no botão dele: a mão desce do alto e bate, a câmera entra -> volta ao alto: 0,025 s e ela ainda descendo
    kf = [(A, 0, 0), (f_s - 1, 0, 0), (f_s + 8, 1, 0.5), (f_r, 1, 0.5), (f_r + 10, 0, 0), (END, 0, 0)]
    t2b, t2c = wt(2, "Você") + 0.3, wt(2, "milésimos") + 0.2
    camera_cine(c, "cam2a", B[1], t2b, [(0.0, -1.05, 2.75), (0.0, -1.0, 2.68)], [(0.0, 0.52, 1.18)], lens=32, fstop=3.5, v_in=0.2, v_out=0.8, filtro=kf)
    camera_cine(c, "cam2b", t2b, t2c, [(xb_v + 0.16, yb - 0.4, z_tampo + 0.075), (xb_v + 0.13, yb - 0.31, z_tampo + 0.07), (xb_v + 0.11, yb - 0.25, z_tampo + 0.068)],
                [(xb_v, yb, z_tampo + 0.32), (xb_v, yb, z_tampo + 0.24)], lens=12, fstop=2.8, v_in=0.8, v_out=0.8, segue=Hv.punho["F"], peso=0.2, clip=0.02,
                impacto=(T(f_v2p), 0.02), filtro=kf)
    camera_cine(c, "cam2c", t2c, B[2] + 0.4, [(0.0, -0.93, 2.56), (0.0, -0.85, 2.45)], [(0.0, 0.5, 1.16)], lens=32, fstop=3.5, v_in=0.8, v_out=0.0, filtro=kf)
    sc.render.use_motion_blur = True; sc.render.motion_blur_shutter = 0.5


def pinca(nm, x, y, z_topo):
    """pinça de laboratório que segura a régua pelo topo; as garras abrem na hora de soltar. Devolve (raiz, garraE, garraD)"""
    r = empty(nm, None, (x, y, z_topo))
    props.inked(nm + "_haste", rrect(-0.012, 0.0, 0.012, 0.3, 0.004, 2), "#2a2d36", r, w=0.006)
    props.inked(nm + "_corpo", rrect(-0.1, -0.02, 0.1, 0.12, 0.02, 3), "#3a4356", r, w=0.008, shade=0.012, shade_color="#232a37", rim=0.006, rim_color="#9aa3b0")
    gs = []
    for k, sg in enumerate((-1, 1)):
        g = empty(f"{nm}_g{k}", r, (sg * 0.05, -0.004, 0.0))
        props.inked(f"{nm}_gar{k}", rrect(-0.018, -0.14, 0.018, 0.0, 0.006, 2), "#c8ccd6", g, w=0.005)
        gs.append(g)
    return r, gs


def numero_flutuante(nm, x, y, z, estados, A, END, cor="#c9ffd8", tam=0.16, rx=60, pop=True):
    """número grande flutuando, virado para a câmera (rx = 90° - elevação da câmera): estados = [(texto, quadro_ini, quadro_fim ou None), ...]"""
    if LIMPO:                                                                  # passe limpo para o Kling: o texto volta no passe de efeitos
        return
    from lib import text as _text
    mt = props.FM(cor, 1.7)
    for k, (tx, ini, fim) in enumerate(estados):
        t = _text(f"{nm}{k}", tx, tam, mt, None, (x, y, z), lib.font()); t.rotation_euler = (math.radians(rx), 0, 0)
        for fr_, vis in ((A, ini <= A and (fim is None or fim > A)), (ini, True), (fim, False)):
            if fr_ is None:
                continue
            t.scale = (1, 1, 1) if vis else (0.0001,) * 3; key(t, "scale", fr_, "CONSTANT")


def piso_liso(cor, lado=60):
    """chão liso 3 cm abaixo do zero: tudo o que é desenhado no chão (faixas, linhas) fica acima dele, sem brigar na profundidade (o campo piscava)"""
    cena.poly_mesh("piso_l", [(-lado, -lado, -0.03), (lado, -lado, -0.03), (lado, lado, -0.03), (-lado, lado, -0.03)], props.FM(cor))


# ====================================================================== 3. a régua: 30 centímetros contra 3 milímetros (fala 3)
@cena_(3)
def s03(c):
    """v2 (limpa): chão liso roxo, os dois de frente, cada um com uma régua de 30 cm presa numa pinça. 1) a pessoa normal: a pinça solta e a régua cai quase
    toda (30 cm) antes de ela pegar; aparece 30 cm. 2) o tempo se dobra (anel de ar e filtro frio) e você pega a sua no 3 mm; aparece 3 mm. 3) o mundo em câmera lenta:
    um copo e uma bola flutuam devagar atrás de vocês"""
    import cinema3d as C3
    from mathutils import Vector
    A, END = F(B[2] - 0.4), F(B[3] + 0.4)
    p = pal("reguas"); mundo(dict(top="#2c2660")); sc = c["sc"]; y0 = 1.0
    piso_liso("#4a4090")
    Hn = heroi3("normal3", -0.62, y0, p, roupa="#d9d4c4", calca="#4a5468", escura="#b5ae9a", gola="#d9d4c4")
    Hv = heroi3("voce3", 0.62, y0, p)
    Hn.rosto(boca="reta"); Hv.rosto(boca="sorriso")
    pronto = dict(ombro=(-30, 6), cotovelo=(-98, -10), abre=(8, 6), tronco=-2, olha=0, cabeca=14)
    for H in (Hn, Hv):
        H.pose(**pronto)
    bpy.context.view_layer.update()
    f_rn = F(wt(3, "deixa") - 0.2); f_cn = f_rn + 7                           # a pessoa normal: a régua cai 7 quadros (30 cm) e ela pega
    f_w = F(wt(3, "Você") + 0.04)                                              # o tempo se dobra em volta de você
    suave = lambda u: 0.0 if u <= 0 else 1.0 if u >= 1 else u * u * u * (u * (6 * u - 15) + 10)
    vt = lambda f: 1.0 - 0.88 * suave((f - f_w) / 6.0)
    def tela(f0, real):
        acc, f = 0.0, f0
        while acc < real:
            acc += vt(f); f += 1
        return f
    f_rv = F(wt(3, "3") - 0.45); f_cv = tela(f_rv, 1.5)                        # a sua: solta, e você pega 1,5 quadro (reais) depois
    ESC = 2.4
    maos = {}
    for H, nome, f_solta, f_pega, D in ((Hn, "n", f_rn, f_cn, 0.30 * ESC), (Hv, "v", f_rv, f_cv, 0.0066 * ESC * 0.5)):
        hand = H.punho["F"].matrix_world.translation.copy(); maos[nome] = hand
        pega = dict(pronto, cotovelo=(-104, -10), ombro=(-32, 6))
        H.anima([(A, pronto), (f_solta - 4, pronto), (f_pega + 1, pega), (END, dict(pega, cabeca=10))], A, END, vida=0.4, molas=dict(ombro=(0, 6.2, 0.7), cotovelo=(1, 6.8, 0.66)))
        rg = OR.regua("regua_" + nome, (hand.x - 0.02, hand.y - 0.1, hand.z - 0.02), ESC)
        pc, gs = pinca("pinca_" + nome, hand.x - 0.02, hand.y - 0.1, hand.z - 0.02 + 0.66)
        for f in range(A, END + 1):
            u = min(1.0, max(0.0, (f - f_solta) / max(1, f_pega - f_solta)))
            d = D * (u * u if u < 1 else 1.0)
            rg.location.z = hand.z - 0.02 - d; key(rg, "location", f, "LINEAR")
        for g, sg in zip(gs, (-1, 1)):
            g.rotation_euler = (0, 0, 0); key(g, "rotation_euler", f_solta - 3, "LINEAR")
            g.rotation_euler = (0, math.radians(35 * sg), 0); key(g, "rotation_euler", f_solta, "LINEAR")
    # números grandes acima de cada um
    hn, hv = maos["n"], maos["v"]
    # a prova fica na régua: uma faixa clara marca a parte que passou pelos dedos (a régua toda, 30 cm; ou só 3 mm) e o número fica ao lado dela
    def faixa(nm, hand, D, f_pop, cor):
        if LIMPO:
            return
        z0 = hand.z - 0.02 - D
        o = props.inked(nm, rrect(-0.03, 0.0, 0.03, D, 0.004, 2), cor, None, (hand.x - 0.02 + 0.075, hand.y - 0.13, hand.z - 0.02 - D), w=0.003, shade=0.0, shade_color=cor, rim=0.0, rim_color=cor)
        UN.pop(o, f_pop, 6)
    faixa("faixa_n", hn, 0.30 * ESC, f_cn, "#ffd24a"); faixa("faixa_v", hv, 0.0066 * ESC * 0.5, f_cv, "#7dff9d")
    numero_flutuante("n3n", hn.x + 0.2, hn.y - 0.14, hn.z - 0.02 - 0.30 * ESC / 2, [("30 cm", f_cn, None)], A, END, cor="#ffe27a", tam=0.15, rx=88)
    numero_flutuante("n3v", hv.x + 0.09, hv.y - 0.14, hv.z - 0.02 - 0.012, [("3 mm", f_cv, None)], A, END, cor="#a8ffc0", tam=0.034, rx=88)
    # o tempo se dobra: um anel deitado no chão e outro de frente; objetos flutuando devagar atrás
    C3.onda("tw3a", (0.0, y0 - 0.3, 1.3), f_w, normal=(0, -1, 0.1), raio=1.6, dur=30, esp=0.02, cor="#a8ecff")
    cop = OR.copo("copo3", (0.0, 2.1, 2.3), 3.2); bol = H3.bola3d("bola3_inv", (1.3, 2.3, 2.5))
    UN.esconde_ate(cop, f_w + 2); UN.esconde_ate(bol, f_w + 2)
    for f in range(f_w, END + 1):
        u = sum(vt(q) for q in range(f_w, f)) / 24.0
        cop.location = (0.0, 2.1, 2.3 - 0.35 * u); cop.rotation_euler = (0, math.radians(40 * u), 0); key(cop, "location", f, "LINEAR"); key(cop, "rotation_euler", f, "LINEAR")
        bol.location = (1.3 - 0.2 * u, 2.3, 2.5 - 0.3 * u); bol.rotation_euler = (0.6 * u, 0.8 * u, 0); key(bol, "location", f, "LINEAR"); key(bol, "rotation_euler", f, "LINEAR")
    Hn.expressao([(A, dict(lid=0.3, brow=-0.4)), (f_rn + 2, dict(boca="o", brow=0.7, olhos=1.12)), (f_cn + 6, dict(boca="triste", brow=0.2))], A, END, seed=5)
    Hv.expressao([(A, dict(boca="sorriso")), (f_w, dict(lid=0.35, brow=-0.5)), (f_cv + 3, dict(boca="sorriso", brow=0.4))], A, END, seed=6)
    kf = [(A, 0, 0), (f_w - 1, 0, 0), (f_w + 8, 1, 0.5), (END, 1, 0.5)]
    # câmeras (take normal, devagar): os dois de frente -> macro na sua mão -> mais aberto, o mundo parado
    t1, t2 = wt(3, "Você") - 0.1, wt(3, "O") - 0.1
    camera_cine(c, "cam3a", B[2], t1, [(hn.x + 0.2, hn.y - 1.7, hn.z - 0.1), (hn.x + 0.16, hn.y - 1.6, hn.z - 0.1), (hn.x + 0.12, hn.y - 1.5, hn.z - 0.1)], [(hn.x + 0.04, hn.y, hn.z - 0.16)], lens=36, fstop=3.0, v_in=0.2, v_out=0.8)
    xr = hv.x - 0.02                                                           # a régua dela: centrada, os dedos dela na ponta de baixo e a faixa dos 3 mm ao lado
    camera_cine(c, "cam3b", t1, t2, [(xr + 0.03, hv.y - 0.78, hv.z - 0.02), (xr + 0.03, hv.y - 0.72, hv.z - 0.02), (xr + 0.03, hv.y - 0.66, hv.z - 0.02)], [(xr + 0.04, hv.y - 0.1, hv.z - 0.022)], lens=60, fstop=2.8, v_in=0.8, v_out=0.8, filtro=kf, clip=0.05)
    camera_cine(c, "cam3c", t2, B[3] + 0.4, [(1.15, -1.7, 0.85), (0.6, -2.05, 0.95), (0.05, -2.25, 1.05)], [(0.2, 1.4, 1.55), (0.0, 1.4, 1.65)], lens=20, fstop=3.5, v_in=0.8, v_out=0.0, filtro=kf)   # baixa, em arco: o copo e a bola parados no ar por cima deles
    sc.render.use_motion_blur = True; sc.render.motion_blur_shutter = 0.5


# ====================================================================== peças do estádio e poses do herói 3D
GUARDA = dict(ombro=(-38, -38), cotovelo=(-62, -62), abre=(18, 18), quadril=(-22, -22), joelho=(44, 44), tornozelo=(-22, -22), inclina=-8, tronco=-4, alt=0.78)
PARADO = dict(ombro=(-4, 6), cotovelo=(-14, -10), abre=(6, 6), alt=0.86)
BRANCO, ADS = "#f4f1ea", ["#2a5acb", "#e0602a", "#f4f1ea", "#1f9d55", "#e2364b", "#f2c94c"]


def _lin(nm, x0, y0, x1, y1, w=0.1, cor=BRANCO, z=0.015):
    AM._quad(nm, [(x0, y0 - w / 2, z), (x1, y0 - w / 2, z), (x1, y1 + w / 2, z), (x0, y1 + w / 2, z)] if y0 == y1 else
             [(x0 - w / 2, y0, z), (x0 + w / 2, y0, z), (x1 + w / 2, y1, z), (x1 - w / 2, y1, z)], cor)


def gol3d(nm, Yg, W=7.32, H=2.44, D=2.0):
    """gol com profundidade: traves e travessão brancos, rede no fundo, nas laterais e no teto (grade de fios claros)"""
    rede, fio = "#3f5361", "#b9c8d0"
    def q(n, pts, cor):
        AM._quad(f"{nm}_{n}", pts, cor)
    q("fundo", [(-W / 2, Yg + D, 0), (W / 2, Yg + D, 0), (W / 2, Yg + D, H), (-W / 2, Yg + D, H)], rede)
    q("ladoE", [(-W / 2, Yg, 0), (-W / 2, Yg + D, 0), (-W / 2, Yg + D, H), (-W / 2, Yg, H)], _mix(rede, "#000000", 0.2))
    q("ladoD", [(W / 2, Yg, 0), (W / 2, Yg + D, 0), (W / 2, Yg + D, H), (W / 2, Yg, H)], _mix(rede, "#000000", 0.2))
    q("teto", [(-W / 2, Yg, H), (W / 2, Yg, H), (W / 2, Yg + D, H), (-W / 2, Yg + D, H)], _mix(rede, "#ffffff", 0.08))
    for k in range(1, 18):
        x = -W / 2 + k * W / 18
        q(f"fv{k}", [(x - 0.008, Yg + D - 0.004, 0), (x + 0.008, Yg + D - 0.004, 0), (x + 0.008, Yg + D - 0.004, H), (x - 0.008, Yg + D - 0.004, H)], fio)
    for k in range(1, 7):
        z = k * H / 7
        q(f"fh{k}", [(-W / 2, Yg + D - 0.004, z - 0.008), (W / 2, Yg + D - 0.004, z - 0.008), (W / 2, Yg + D - 0.004, z + 0.008), (-W / 2, Yg + D - 0.004, z + 0.008)], fio)
    for sg, nmx in ((-1, "E"), (1, "D")):
        for k in range(1, 5):
            y = Yg + k * D / 5
            q(f"fl{nmx}{k}", [(sg * W / 2 + sg * 0.004, y - 0.008, 0), (sg * W / 2 + sg * 0.004, y + 0.008, 0), (sg * W / 2 + sg * 0.004, y + 0.008, H), (sg * W / 2 + sg * 0.004, y - 0.008, H)], fio)
    for k in range(1, 5):
        y = Yg + k * D / 5
        q(f"ft{k}", [(-W / 2, y - 0.008, H + 0.004), (W / 2, y - 0.008, H + 0.004), (W / 2, y + 0.008, H + 0.004), (-W / 2, y + 0.008, H + 0.004)], fio)
    for k, x in enumerate((-W / 2, W / 2)):
        props.inked(f"{nm}_tr{k}", rrect(x - 0.06, 0.0, x + 0.06, H + 0.06, 0.02, 3), BRANCO, None, (0, Yg - 0.02, 0), w=0.012, shade=0.015, shade_color="#cfcabd", rim=0.008, rim_color="#ffffff")
    props.inked(nm + "_tv", rrect(-W / 2 - 0.06, H, W / 2 + 0.06, H + 0.12, 0.02, 3), BRANCO, None, (0, Yg - 0.02, 0), w=0.012, shade=0.015, shade_color="#cfcabd", rim=0.008, rim_color="#ffffff")


def estadio(nm, p, Yg=12.0, noite=False):
    """gramado listrado com as linhas do campo, o gol, placas de publicidade (só cores), arquibancada inclinada com a torcida em bokeh e refletores"""
    S.fundo(p, Yg + 30, z_meio=5.0, x=(-70, 70), z=(-4, 40), escuro=0.12 if noite else 0.0)
    base = p["chao"]; claro = _mix(base, "#ffffff", 0.09)
    for i in range(0, 15):
        AM._quad(f"{nm}_gr{i}", [(-45, -20 + i * 3.6, 0), (45, -20 + i * 3.6, 0), (45, -20 + (i + 1) * 3.6, 0), (-45, -20 + (i + 1) * 3.6, 0)], claro if i % 2 else base)
    _lin(nm + "_lg", -30, Yg, 30, Yg); _lin(nm + "_la", -20.15, Yg - 16.5, 20.15, Yg - 16.5); _lin(nm + "_lp", -9.16, Yg - 5.5, 9.16, Yg - 5.5)
    _lin(nm + "_lv1", -20.15, Yg - 16.5, -20.15, Yg); _lin(nm + "_lv2", 20.15, Yg - 16.5, 20.15, Yg)
    _lin(nm + "_lv3", -9.16, Yg - 5.5, -9.16, Yg); _lin(nm + "_lv4", 9.16, Yg - 5.5, 9.16, Yg)
    cena.disc(nm + "_marca", 0.16, props.FM(BRANCO), (0.0, Yg - 11.0, 0.004)) if False else AM._quad(nm + "_marca", [(-0.16, Yg - 11.16, 0.004), (0.16, Yg - 11.16, 0.004), (0.16, Yg - 10.84, 0.004), (-0.16, Yg - 10.84, 0.004)], BRANCO)
    gol3d(nm + "_gol", Yg)
    for i in range(-12, 12):
        AM._quad(f"{nm}_ad{i}", [(i * 3.2, Yg + 5.0, 0.0), (i * 3.2 + 3.1, Yg + 5.0, 0.0), (i * 3.2 + 3.1, Yg + 5.0, 1.0), (i * 3.2, Yg + 5.0, 1.0)], _mix(ADS[i % 6], "#000000", 0.25 if noite else 0.0))
    AM._quad(nm + "_arq", [(-45, Yg + 7, 1.0), (45, Yg + 7, 1.0), (45, Yg + 24, 11.0), (-45, Yg + 24, 11.0)], _mix(p["pedra"], "#000000", 0.35))
    for k in range(7):
        z = 1.6 + k * 1.3; y = Yg + 7 + (z - 1.0) * 1.7
        AM._quad(f"{nm}_deg{k}", [(-45, y, z), (45, y, z), (45, y, z + 0.1), (-45, y, z + 0.1)], _mix(p["pedra"], "#000000", 0.55))
    import random
    rnd = random.Random(7); cores = ["#f2c94c", "#e2364b", "#f4f1ea", "#2a5acb", "#1f9d55", "#e0602a"]
    mats = [cena.amat(f"{nm}_pt{k}_m", _mix(cor, "#000000", 0.3 if noite else 0.0), 1.0, 0.95, ("radial", 1.3)) for k, cor in enumerate(cores)]
    for k in range(260):                                                     # a torcida: pontos de cor colados na arquibancada inclinada
        y = rnd.uniform(Yg + 8, Yg + 23); z = 1.0 + 0.588 * (y - (Yg + 7)) + rnd.uniform(0.1, 0.5)
        cena.disc(f"{nm}_pt{k}", 0.1 + 0.012 * (y - Yg - 8), mats[rnd.randrange(6)], (rnd.uniform(-40, 40), y - 0.05, z), n=12)
    for sx in (-26, 26):
        AM._quad(f"{nm}_pole{sx}", [(sx - 0.12, Yg + 14, 0), (sx + 0.12, Yg + 14, 0), (sx + 0.12, Yg + 14, 13), (sx - 0.12, Yg + 14, 13)], "#2a2d36")
        cena.disc(f"{nm}_ref{sx}", 1.6, cena.amat(f"{nm}_ref{sx}_m", "#fff4d0", 1.6, 0.95 if noite else 0.5, ("radial", 1.4)), (sx, Yg + 13.9, 13))


def plateia(nm, x0, x1, y, z0, linhas, n, seed, noite=False):
    """torcida em silhueta (cabeça + tronco chapados) em fileiras; devolve a lista de (cabeça, corpo, linha) para a gente poder levantar depois"""
    import random
    rnd = random.Random(seed); cores = ["#1f9d55", "#f2c94c", "#2a5acb", "#e0602a", "#f4f1ea", "#e2364b", "#6a7f9a"]
    out = []
    for r in range(linhas):
        for i in range(n):
            x = x0 + (x1 - x0) * (i + rnd.uniform(0.1, 0.9)) / n; zz = z0 + r * 1.3; yy = y + (zz - z0) * 1.7
            cor = _mix(rnd.choice(cores), "#000000", 0.35 if noite else 0.1)
            g = empty(f"{nm}_{r}_{i}", None, (x, yy, zz))
            props.poly(f"{nm}_{r}_{i}_c", circle(0.0, 0.62, 0.11, 12), "#0d1020", 0.0, g)
            props.poly(f"{nm}_{r}_{i}_t", rrect(-0.2, 0.0, 0.2, 0.52, 0.07, 3), cor, 0.0, g)
            out.append((g, r))
    return out


def bola_voa(b, f0, f1, p0, p1, alt=0.6, passo=1):
    """a bola da cobrança: arco até p1; gira enquanto voa"""
    for f in range(f0, f1 + 1, passo):
        u = (f - f0) / max(1, f1 - f0)
        b.location = tuple(a + (c_ - a) * u for a, c_ in zip(p0, p1)); b.location.z += alt * 4 * u * (1 - u)
        b.rotation_euler = (u * 8, u * 5, 0); key(b, "location", f, "LINEAR"); key(b, "rotation_euler", f, "LINEAR")


def chute_chaves(f_chute, pos, ante=10, depois=14):
    """o batedor de costas para a câmera: perna de trás recua, a de frente vem, e ele termina o movimento"""
    return [(f_chute - ante, dict(PARADO, pos=pos, rot=180, quadril=(0, 25), joelho=(5, 40), ombro=(10, -10), tronco=2)),
            (f_chute - 3, dict(PARADO, pos=pos, rot=180, quadril=(0, 45), joelho=(5, 70), ombro=(25, -25), tronco=4)),
            (f_chute, dict(PARADO, pos=pos, rot=180, quadril=(0, -70), joelho=(5, 10), ombro=(-30, 35), tronco=-6)),
            (f_chute + depois, dict(PARADO, pos=(pos[0], pos[1] + 0.4, pos[2]), rot=180, quadril=(0, -20), joelho=(5, 20), ombro=(-10, 10), tronco=0))]


def campo(p, Yg=6.0, W=4.4, Hg=1.9, D=1.4, noite=False, ys=2.8):
    """campo limpo: gramado de duas cores em faixas, a linha do gol, a marca do pênalti e o gol com rede (estilizado: mais estreito, para os goleiros ficarem grandes)"""
    base = p["chao"]; claro = _mix(base, "#ffffff", 0.07)
    cena.poly_mesh("cp_base", [(-60, -60, -0.03), (60, -60, -0.03), (60, 60, -0.03), (-60, 60, -0.03)], props.FM(base))
    for i in range(-3, 8):
        AM._quad(f"cp_gr{i}", [(-40, i * 2.5, 0), (40, i * 2.5, 0), (40, (i + 1) * 2.5, 0), (-40, (i + 1) * 2.5, 0)], claro if i % 2 else base)
    _lin("cp_lg", -9, Yg, 9, Yg, 0.12)
    AM._quad("cp_marca", [(-0.12, ys - 0.12, 0.018), (0.12, ys - 0.12, 0.018), (0.12, ys + 0.12, 0.018), (-0.12, ys + 0.12, 0.018)], BRANCO)
    gol3d("cp_gol", Yg, W=W, H=Hg, D=D)


def mergulho(f0, lado, dx, dur, ypos, dy=0.2):
    """chaves de um mergulho de goleiro para o lado (lado = +1 direita da tela, -1 esquerda): em guarda, o corpo deita no ar e cai com os braços para cima"""
    g = GUARDA
    return [(f0, dict(g, pos=(0.0, ypos, 0), rot=(0, 0, 0))),
            (f0 + int(dur * 0.45), dict(ombro=(-150, -150), cotovelo=(-8, -8), abre=(12, 12), quadril=(-12, 8), joelho=(30, 6), tornozelo=(-10, -10), tronco=0, alt=0.86,
                                        pos=(dx * 0.45, ypos - 0.1, 0.3), rot=(0, 38 * lado, 0))),
            (f0 + dur, dict(ombro=(-165, -165), cotovelo=(-6, -6), abre=(10, 10), quadril=(-8, 8), joelho=(18, 5), tornozelo=(-8, -8), tronco=0, alt=0.86,
                            pos=(dx, ypos - dy, 0.55), rot=(0, 82 * lado, 0)))]


# ====================================================================== 4. o pênalti (fala 4)
@cena_(4)
def s04(c):
    """v2 (limpa): gramado liso com um gol estreito. Três cobranças vistas de trás do batedor, com um corte entre elas:
    1) o pênalti chega em 0,36 s (o contador sobe até a bola entrar); 2) o goleiro comum aposta no lado errado antes do chute;
    3) você espera a bola sair, o tempo se dobra (anel de ar, tela fria), você mergulha para o lado certo e pega"""
    import cinema3d as C3
    from mathutils import Vector
    A, END = F(B[3] - 0.4), F(B[4] + 0.4)
    p = pal("estadio_dia"); mundo(dict(top="#6ec3ff")); sc = c["sc"]
    Yg, ys = 5.2, 2.0
    campo(p, Yg=Yg, ys=ys, W=3.6, Hg=1.8, D=1.2)
    bola = H3.bola3d("bola4_inv", (0.0, ys, 0.11))
    S1 = heroi3("batedor", -1.5, 0.0, p, roupa="#2a5acb", calca="#e8e8ee", escura="#f4f1ea")
    K1 = heroi3("comum", 0.0, Yg - 0.3, p, roupa="#e8e2d2", calca="#4a5468", luvas=True, escura="#bdb7a6", gola="#e8e2d2")
    K2 = heroi3("voce4", 0.0, Yg - 0.3, p, luvas=True)
    S1.rosto(boca="reta"); K1.rosto(boca="o"); K2.rosto(boca="reta", lid=0.4)
    yk = Yg - 0.3
    # cortes entre as três cobranças e o tempo de cada uma
    T2, T3 = F(22.92 - DT), F(24.66 - DT)
    k1 = F(21.45 - DT); k2 = F(24.24 - DT); k3 = F(wt(4, "sair") - 0.08)                 # a 3ª bola sai no "sair"
    VOO = 9                                                                    # a bola leva 9 quadros (0,36 s) do pé ao canto
    f_w = k3 + 1
    suave = lambda u: 0.0 if u <= 0 else 1.0 if u >= 1 else u * u * u * (u * (6 * u - 15) + 10)
    vt = lambda f: 1.0 - 0.6 * suave((f - f_w) / 5.0)                          # a 0,4: a bola chega na luva no "defende"
    def tela(f0, real):
        acc, f = 0.0, f0
        while acc < real:
            acc += vt(f); f += 1
        return f
    a3 = tela(k3, VOO)                                                         # a bola da 3ª cobrança chega depois (câmera lenta)
    # o batedor: corre em arco pela esquerda e chuta com a perna direita; reaparece no começo de cada cobrança
    def cobranca(fk, n):
        ch = corrida(fk - 14, fk - 3, (-1.5, 0.1, 0), (-0.25, ys - 0.45, 0), rot=180, ciclo=12, inclina=8)
        ch += chute_chaves(fk, (-0.25, ys - 0.4, 0), ante=3, depois=16)
        return ch
    # cada cobrança só vale até o corte da seguinte (o fim do chute 2 invadia o 3: ele andava até a bola e pulava de volta)
    ch = [(A, dict(PARADO, pos=(-1.5, 0.1, 0), rot=180))] + [q for q in cobranca(k1, 1) if q[0] < T2 - 1]
    ch += [(T2 - 1, dict(PARADO, pos=(-1.5, 0.1, 0), rot=180))] + [q for q in cobranca(k2, 2) if q[0] < T3 - 1]
    ch += [(T3 - 1, dict(PARADO, pos=(-1.5, 0.1, 0), rot=180))] + cobranca(k3, 3) + [(END, dict(PARADO, pos=(-0.2, ys, 0), rot=180))]
    ch.sort(key=lambda q: q[0]); S1.anima(ch, A, END, vida=0.3)
    # goleiro comum: 1ª cobrança, mergulha tarde (depois de a bola passar); 2ª, aposta cedo no lado errado
    gd = dict(GUARDA, pos=(0.0, yk, 0), rot=(0, 0, 0))
    kk = [(A, gd), (k1 + VOO + 1, gd)] + mergulho(k1 + VOO + 2, -1, -0.9, 14, yk)[1:] + [(T2 - 2, dict(mergulho(0, -1, -0.9, 14, yk)[-1][1])), (T2 - 1, gd)]
    kk += [(k2 - 14, gd)] + mergulho(k2 - 13, -1, -1.1, 13, yk)[1:] + [(T3 - 2, dict(mergulho(0, -1, -1.1, 13, yk)[-1][1])), (T3 - 1, gd), (END, gd)]
    kk.sort(key=lambda q: q[0]); K1.anima(kk, A, END, vida=0.3)
    UN.some(K1.raiz, T3 - 1, 1); UN.some(K1.sombra, T3 - 1, 1)
    UN.esconde_ate(K2.raiz, T3); UN.esconde_ate(K2.sombra, T3)
    # você: em guarda, espera a bola sair; só então mergulha (no tempo normal) e chega antes dela
    f_dv = k3 + 3
    kv = [(T3, gd), (f_dv, gd)] + mergulho(f_dv, 1, 1.15, 13, yk)[1:] + [(END, dict(mergulho(0, 1, 1.15, 13, yk)[-1][1]))]
    K2.anima(kv, T3, END, vida=0.3)
    sc.frame_set(END); mao_f = sum((K2.punho[q].matrix_world.translation for q in "FB"), Vector((0, 0, 0))) / 2; sc.frame_set(A)
    # a bola: três voos; as duas primeiras entram no canto direito (a goleiro comum está no lado errado); a terceira para na luva
    alvo = (1.2, Yg + 0.8, 0.9)
    for f in range(A, END + 1):
        if f < k1:
            loc = (0.0, ys, 0.11)
        elif f <= k1 + VOO:
            u = (f - k1) / VOO; loc = tuple(a_ + (b_ - a_) * u for a_, b_ in zip((0.0, ys, 0.11), alvo)); loc = (loc[0], loc[1], loc[2] + 0.5 * 4 * u * (1 - u))
        elif f < T2:
            loc = alvo
        elif f < k2:
            loc = (0.0, ys, 0.11)
        elif f <= k2 + VOO:
            u = (f - k2) / VOO; loc = tuple(a_ + (b_ - a_) * u for a_, b_ in zip((0.0, ys, 0.11), alvo)); loc = (loc[0], loc[1], loc[2] + 0.5 * 4 * u * (1 - u))
        elif f < T3:
            loc = alvo
        elif f < k3:
            loc = (0.0, ys, 0.11)
        elif f <= a3:
            u = sum(vt(q) for q in range(k3, f)) / VOO; u = min(1.0, u)
            alvo3 = (mao_f.x, mao_f.y, max(0.25, mao_f.z))
            loc = tuple(a_ + (b_ - a_) * u for a_, b_ in zip((0.0, ys, 0.11), alvo3)); loc = (loc[0], loc[1], loc[2] + 0.5 * 4 * u * (1 - u))
        else:
            loc = (mao_f.x, mao_f.y, max(0.25, mao_f.z))
        bola.location = loc; bola.rotation_euler = (f * 0.3, f * 0.2, 0); key(bola, "location", f, "LINEAR"); key(bola, "rotation_euler", f, "LINEAR")
    # contador do voo na 1ª cobrança e o 'tempo parado' na 3ª
    est = [("0,00 s", k1, k1 + 3), ("0,12 s", k1 + 3, k1 + 6), ("0,24 s", k1 + 6, k1 + VOO), ("0,36 s", k1 + VOO, T2)]
    numero_flutuante("n4a", 0.0, Yg, 2.45, est, A, END, cor="#ffffff", tam=0.34, rx=78)
    C3.onda("tw4", (0.0, ys + 0.8, 1.0), f_w, normal=(0, -1, 0.1), raio=2.4, dur=34, esp=0.05, cor="#a8ecff")
    kf = [(A, 0, 0), (T3 - 1, 0, 0), (f_w + 8, 1, 0.5), (END, 1, 0.5)]
    # câmeras: de trás do batedor, uma por cobrança (um corte seco entre elas)
    S1.expressao([(A, dict(lid=0.3, brow=-0.4))], A, END, seed=1)
    K1.expressao([(A, dict(lid=0.2)), (k1 + VOO, dict(boca="o", brow=0.8, olhos=1.12)), (T2, dict(lid=0.25, brow=-0.3)), (k2 + VOO, dict(boca="triste", brow=0.3))], A, END, seed=2)
    K2.expressao([(A, dict(lid=0.35, brow=-0.6)), (a3 + 2, dict(boca="sorriso", brow=0.4))], A, END, seed=3)
    # câmeras (pedido de 23/10/2026: "a câmera vem para o pé dele chutando a bola; depois para trás do goleiro, olhando a bola"):
    # 1) 12 mm no chão, ao lado da bola: o pé entra e chuta, a mira vai atrás da bola até a rede (o "chega em menos de meio segundo");
    # 2) dentro da rede, atrás do goleiro comum: ele pula antes e a bola entra do outro lado, na nossa direção;
    # 3) o mesmo lugar atrás de você (a comparação); 4) 16 mm na luva no "e defende": a bola para na mão
    tA, tB, tC = T(T2), T(T3), T(a3 - 6)
    camera_cine(c, "cam4a", B[3], tA, [(0.52, ys - 0.64, 0.13), (0.46, ys - 0.56, 0.125), (0.42, ys - 0.5, 0.12)], [(0.0, ys, 0.16)], lens=12, fstop=2.8,
                v_in=0.2, v_out=0.8, segue=bola, peso=0.75, clip=0.02, impacto=(T(k1), 0.02))
    camera_cine(c, "cam4b", tA, tB, [(-0.48, Yg + 1.02, 1.02), (-0.42, Yg + 0.92, 1.0)], [(0.1, ys, 0.85)], lens=16, fstop=3.2, v_in=0.8, v_out=0.8, segue=bola, peso=0.3, clip=0.05)
    camera_cine(c, "cam4c", tB, tC, [(-0.48, Yg + 1.02, 1.02), (-0.42, Yg + 0.92, 1.0)], [(0.1, ys, 0.85)], lens=16, fstop=3.2, v_in=0.8, v_out=0.8, segue=bola, peso=0.3, clip=0.05, filtro=kf)
    camera_cine(c, "cam4d", tC, B[4] + 0.4, [mao_f + Vector((0.36, -0.68, 0.14)), mao_f + Vector((0.3, -0.56, 0.12))], [mao_f + Vector((-0.1, 0, 0))], lens=16, fstop=2.8,
                v_in=0.8, v_out=0.0, segue=bola, peso=0.3, clip=0.02, impacto=(T(a3), 0.025), filtro=kf)
    sc.render.use_motion_blur = True; sc.render.motion_blur_shutter = 0.5


# ====================================================================== 5. os 100 metros e a falsa largada (fala 5)
LARGADA = dict(ombro=(-5, -5), cotovelo=(-8, -8), abre=(8, 8), quadril=(-70, -105), joelho=(105, 125), tornozelo=(-40, -55), tronco=-48, alt=0.55, cabeca=38, olha=0)


@cena_(5)
def s05(c):
    """v2 (limpa): pista vermelha lisa, três corredores nos blocos vistos de frente (a pista vem na direção da câmera) e o juiz com a pistola ao lado.
    No tiro, só você sai (0,025 s, em vermelho): os outros ainda nem se mexeram. Um cartão vermelho grande aparece no ar, você para, olha e volta caminhando"""
    import cinema3d as C3
    from mathutils import Vector
    A, END = F(B[4] - 0.4), F(B[5] + 0.4)
    p = pal("pista"); mundo(dict(top="#2a3a7a")); sc = c["sc"]
    piso_liso("#b5503a")
    Y0 = 3.0
    for k in range(-2, 3):                                                     # raias brancas
        _lin(f"raia{k}", k * 0.9 + 0.45, -8, k * 0.9 + 0.45, 12, 0.06, BRANCO)
    _lin("linha_chegada", -2.6, -2.2, 2.6, -2.2, 0.12, BRANCO)
    vm = [(-0.9, "#2a5acb", "#e8e8ee", "#f4f1ea"), (0.9, "#e2b83a", "#2b3a5a", "#f6e9b0")]
    runners = []
    for k, (x, rj, cal, esc) in enumerate(vm):
        Hr = heroi3(f"corr{k}", x, Y0, p, roupa=rj, calca=cal, escura=esc); Hr.rosto(boca="reta"); runners.append(Hr)
    Hv = heroi3("voce5", 0.0, Y0, p); Hv.rosto(boca="reta", lid=0.0)
    for k, x in enumerate((-0.9, 0.0, 0.9)):                                   # blocos de largada
        AM._quad(f"bloco{k}", [(x - 0.15, Y0 - 0.45, 0.01), (x + 0.15, Y0 - 0.45, 0.01), (x + 0.15, Y0 - 0.25, 0.1), (x - 0.15, Y0 - 0.25, 0.1)], "#3a4356")
    # o juiz com a pistola, no canto, de lado
    Hj = heroi3("juiz", -2.0, Y0 + 0.3, p, roupa="#f4f1ea", calca="#1c2230", escura="#bdb7a6", gola="#f4f1ea"); Hj.rosto(boca="reta")
    f_gun = F(wt(5, "décimo") - 0.2)                                            # o tiro
    f_card = F(wt(5, "falsa"))
    f_up = f_gun - 14
    pis = H3.esfera("pistola", 0.04, 0.12, 0.05, H3.estilo("#2a2d36", "#14161c"), None, (0, 0, 0), contorno=0.003, seg=16, an=10)
    pis.parent = Hj.punho["F"]; pis.location = (0, -0.05, -0.1)
    ch_j = [(A, dict(PARADO, ombro=(-4, -4), cotovelo=(-14, -14))), (f_up, dict(PARADO, ombro=(-4, -4), cotovelo=(-14, -14))), (f_up + 12, dict(PARADO, ombro=(-170, -4), cotovelo=(-6, -14), olha=0)),
            (f_gun + 2, dict(PARADO, ombro=(-176, -4), cotovelo=(-4, -14))), (f_gun + 14, dict(PARADO, ombro=(-170, -4), cotovelo=(-6, -14))), (END, dict(PARADO, ombro=(-170, -4), cotovelo=(-6, -14)))]
    Hj.anima(ch_j, A, END, vida=0.3)
    # corredores: nos blocos até o tiro; os outros saem 0,25 s depois; você sai 0,025 s depois (1 quadro) e é o único que passa a linha, depois para
    for Hr, atraso in ((runners[0], 6), (runners[1], 7)):
        x = Hr.raiz.location.x
        ch = [(A, dict(LARGADA, pos=(x, Y0, 0), rot=0)), (f_gun + atraso - 1, dict(LARGADA, pos=(x, Y0, 0), rot=0))]
        ch += corrida(f_gun + atraso, END, (x, Y0, 0), (x, -6.5, 0), rot=0, ciclo=12, inclina=14)
        Hr.anima(ch, A, END, vida=0.3)
    x = 0.0; f_v = f_gun + 1; f_stop = f_card + 6
    chv = [(A, dict(LARGADA, pos=(x, Y0, 0), rot=0)), (f_v - 1, dict(LARGADA, pos=(x, Y0, 0), rot=0))]
    chv += corrida(f_v, f_stop, (x, Y0, 0), (x, Y0 - 3.4, 0), rot=0, ciclo=12, inclina=14, arranque=0.2, freia=0.3)
    chv += [(f_stop + 10, dict(PARADO, pos=(x, Y0 - 3.6, 0), rot=0, cabeca=18, olha=0)), (f_stop + 40, dict(PARADO, pos=(x, Y0 - 3.6, 0), rot=0, cabeca=26, olha=0)),
            (END, dict(PARADO, pos=(x, Y0 - 3.6, 0), rot=0, cabeca=30, olha=0))]
    Hv.anima(chv, A, END, vida=0.4)
    # o tiro: clarão e anel de fumaça na ponta da pistola
    sc.frame_set(f_gun + 2); pt = pis.matrix_world.translation.copy(); sc.frame_set(A)
    fl = H3.esfera("clarao", 0.16, 0.16, 0.16, H3.plano("#fff2b0"), None, tuple(pt), contorno=0.0, seg=16, an=10)
    UN.esconde_ate(fl, f_gun + 1); UN.some(fl, f_gun + 3, 2)
    C3.onda("fumaca", tuple(pt), f_gun + 1, normal=(1, 0, 0.2), raio=0.7, dur=20, esp=0.025, cor="#ffffff")
    C3.onda("ar_t", (0.0, Y0 - 0.3, 0.9), f_gun + 1, normal=(0, 1, 0.2), raio=1.8, dur=26, esp=0.02, cor="#a8ecff")
    # o número em vermelho acima de você e o cartão vermelho no ar
    numero_flutuante("n5v", 0.0, Y0 - 3.0, 2.2, [("0,025 s", f_v + 2, None)], A, END, cor="#ff8a7a", tam=0.34, rx=62)
    cartao = props.inked("cartao", rrect(-0.28, -0.4, 0.28, 0.4, 0.03, 3), "#e2364b", None, (0.0, Y0 - 3.0, 2.9), w=0.014, shade=0.02, shade_color="#a8202f", rim=0.01, rim_color="#ff9a9a")
    cartao.hide_render = LIMPO                                                  # o cartão no ar é desenho: no passe limpo ele sai
    UN.pop(cartao, f_card, 8)
    Hv.expressao([(A, dict(lid=0.45, brow=-0.6)), (f_v + 2, dict(boca="sorriso", brow=0.2)), (f_card + 2, dict(boca="o", brow=0.9, olhos=1.15)), (f_card + 16, dict(boca="triste", brow=0.2, lid=0.2))], A, END, seed=8)
    for k_, Hr in enumerate(runners):
        Hr.expressao([(A, dict(lid=0.4, brow=-0.5)), (f_card + 4, dict(boca="o", brow=0.6))], A, END, seed=20 + k_)
    Hj.expressao([(A, dict()), (f_card, dict(brow=-0.6, lid=0.25))], A, END, seed=30)
    kf = [(A, 0, 0), (f_gun - 1, 0, 0), (f_gun + 8, 1, 0.35), (END, 1, 0.35)]
    # câmeras: os corredores de frente; depois você, grande, e o cartão
    t_a = wt(5, "falsa") - 0.1
    # câmeras: 1) 14 mm no chão, na diagonal entre as raias: você nos blocos, os outros e o juiz ao fundo levantando a pistola; no tiro você já saiu e eles nem se mexeram;
    # 2) de frente: o 0,025 s e o cartão ("falsa largada"); 3) no "você seria eliminado", entra devagar no seu rosto, com o cartão em cima
    t_c = wt(5, "Você", 1) - 0.1
    camera_cine(c, "cam5a", B[4], t_a, [(0.36, Y0 - 2.15, 0.15), (0.34, Y0 - 2.0, 0.16), (0.33, Y0 - 1.9, 0.17)], [(-0.4, Y0 + 0.3, 0.62)], lens=14, fstop=3.2, v_in=0.2, v_out=0.8, filtro=kf, clip=0.03)
    camera_cine(c, "cam5b", t_a, t_c, [(0.8, -3.3, 1.9), (0.5, -3.45, 1.9), (0.3, -3.55, 1.9)], [(0.0, Y0 - 3.0, 1.2)], lens=32, fstop=3.6, v_in=0.8, v_out=0.8, filtro=kf)
    camera_cine(c, "cam5c", t_c, B[5] + 0.4, [(0.28, Y0 - 5.05, 1.62), (0.14, Y0 - 4.8, 1.66), (0.06, Y0 - 4.62, 1.68)], [(0.0, Y0 - 3.6, 1.95)], lens=24, fstop=2.8, v_in=0.8, v_out=0.0,
                segue=Hv.cabeca, peso=0.4, filtro=kf)
    sc.render.use_motion_blur = True; sc.render.motion_blur_shutter = 0.5


# ====================================================================== 6. a final da Copa e o cabo que arrebenta (fala 6) e 7. você escolhe o menino
def final_mundo(c, A, END):
    """o mundo das cenas 6 e 7 (uma só sequência, montada inteira em cada cena; cada cena só põe as suas câmeras):
    noite, gol estreito, torcida sentada atrás; você no gol, o batedor no ponto; à esquerda do gol um menino pegador de bolas sob uma câmera de TV pendurada
    por um cabo. No 'arrebentar' o cabo rompe e o MUNDO cai a 1/8 da velocidade (você continua no tempo normal): o chute, o voo da bola e a queda da câmera
    levam 6 segundos de tela. Você mergulha para o menino, a câmera de TV cai no lugar dele e a bola entra; o tempo volta e a torcida se levanta"""
    import cinema3d as C3
    from mathutils import Vector
    sc = c["sc"]; p = pal("estadio_noite"); mundo(dict(top="#0b1030"))
    Yg, ys = 5.2, 2.0; yk = Yg - 0.3
    campo(dict(p, chao="#1c5a3a"), Yg=Yg, ys=ys, W=3.6, Hg=1.8, D=1.2)
    f_cab = F(37.94 - DT); f_k = F(40.5 - DT); f_dv = F(43.5 - DT); f_ret = F(45.2 - DT)
    suave = lambda u: 0.0 if u <= 0 else 1.0 if u >= 1 else u * u * u * (u * (6 * u - 15) + 10)
    vt = lambda f: 1.0 - 0.93 * suave((f - f_cab) / 6.0) + 0.93 * suave((f - f_ret) / 8.0)   # a 0,07: a câmera de TV ainda está a 1 m da cabeça do menino quando você chega
    acum = {}
    def real(f):
        """quadros de tempo do mundo desde o cabo até o quadro f (acumulado)"""
        if f not in acum:
            acum[f] = sum(vt(q) for q in range(f_cab, f)) if f > f_cab else 0.0
        return acum[f]
    # torcida sentada atrás do gol (silhuetas) e o número de 80 mil
    pl = plateia("tor", -7.5, 7.5, Yg + 4.0, 0.5, 4, 14, 5, noite=True)
    import random
    rr = random.Random(3)
    f_up = F(47.0 - DT)
    for g, r in pl:
        d = int(rr.uniform(0, 14)); g.scale = (1, 1, 0.55); key(g, "scale", f_up + d - 1, "LINEAR")
        g.scale = (1, 1, 1.0); key(g, "scale", f_up + d + 7, "LINEAR")
    # personagens
    S1 = heroi3("batedor", 1.7, 0.2, p, roupa="#2a5acb", calca="#e8e8ee", escura="#f4f1ea")
    K = heroi3("voce6", 0.0, yk, p, luvas=True)
    M = heroi3("menino", -2.15, Yg - 0.4, p, roupa="#f2c94c", calca="#2a3a5a", escura="#c8962a", gola="#f2c94c", escala=0.72, cabeca=0.95, body_w=0.92, arm_len=0.95)
    S1.rosto(boca="reta"); K.rosto(boca="reta", lid=0.0); M.rosto(boca="o")
    bola = H3.bola3d("bola6_inv", (0.0, ys, 0.11))
    # batedor: chega ao ponto, espera, e chuta devagar (o mundo está lento): corre antes do cabo, chuta a 40,9 s
    ch = [(A, dict(PARADO, pos=(1.7, 0.2, 0), rot=180))]
    ch += corrida(F(36.2 - DT), F(37.7 - DT), (1.7, 0.2, 0), (0.3, ys - 0.5, 0), rot=180, ciclo=12, inclina=8, freia=0.35)
    ch += [(F(38.2 - DT), dict(PARADO, pos=(0.3, ys - 0.5, 0), rot=180, tronco=2)), (f_k - 20, dict(PARADO, pos=(0.3, ys - 0.5, 0), rot=180, quadril=(0, 25), joelho=(5, 40), ombro=(10, -10), tronco=2)),
           (f_k - 8, dict(PARADO, pos=(0.3, ys - 0.5, 0), rot=180, quadril=(0, 45), joelho=(5, 75), ombro=(25, -25), tronco=4)),
           (f_k, dict(PARADO, pos=(0.3, ys - 0.5, 0), rot=180, quadril=(0, -70), joelho=(5, 10), ombro=(-30, 35), tronco=-6)),
           (f_k + 28, dict(PARADO, pos=(0.3, ys - 0.1, 0), rot=180, quadril=(0, -20), joelho=(5, 20), ombro=(-10, 10), tronco=0)), (END, dict(PARADO, pos=(0.3, ys - 0.1, 0), rot=180))]
    ch.sort(key=lambda q: q[0]); S1.anima(ch, A, END, vida=0.3)
    # você: em guarda; olha para o cabo, depois para a bola e o menino; mergulha para o menino
    gd = dict(GUARDA, pos=(0.0, yk, 0), rot=(0, 0, 0))
    f_olha = F(36.9 - DT)
    kk = [(A, dict(gd, olha=0, cabeca=0)), (f_olha, dict(gd, olha=0, cabeca=0)), (f_olha + 8, dict(gd, olha=-38, cabeca=-18)), (f_cab + 18, dict(gd, olha=-38, cabeca=-18)),
          (f_k - 10, dict(gd, olha=10, cabeca=4)), (F(41.95 - DT), dict(gd, olha=26, cabeca=4)), (F(42.5 - DT), dict(gd, olha=-36, cabeca=-6)), (f_dv - 3, dict(gd, olha=-36, cabeca=-6))]
    COLO = dict(ombro=(-22, -22), cotovelo=(-54, -54), abre=(18, 18))          # antebraços deitados sob as pernas dele (as luvas nunca no rosto do menino)
    corre1 = corrida(f_dv, f_dv + 10, (0.0, yk, 0), (-1.66, Yg - 0.64, 0), rot=-90, ciclo=10, inclina=16, arranque=0.25, freia=0.2)
    freia = dict(PARADO, pos=(-1.78, Yg - 0.62, 0), rot=-90, tronco=-30, alt=0.72, quadril=(-48, -18), joelho=(72, 36), tornozelo=(-26, -18),
                 ombro=(-72, -72), cotovelo=(-48, -48), abre=(26, 26), cabeca=14, olha=0)                    # planta o pé, abaixa e abre os braços
    pega = dict(PARADO, pos=(-1.8, Yg - 0.64, 0), rot=-90, tronco=-8, alt=0.84, cabeca=4, olha=0, **COLO)          # levanta o menino junto ao peito
    vira = dict(PARADO, pos=(-1.78, Yg - 0.8, 0), rot=-25, tronco=-6, alt=0.83, cabeca=0, olha=0, **COLO)
    corre2 = corrida(f_dv + 21, f_dv + 33, (-1.76, Yg - 0.9, 0), (-1.62, Yg - 2.25, 0), rot=0, ciclo=10, inclina=10, bracos=COLO, arranque=0.3, freia=0.3)
    # chega em segurança e NÃO solta o menino: freia com o peso para trás, olha para ele no colo e os dois viram a cabeça para o gol
    P_fim = (-1.6, Yg - 2.32, 0)
    freia2 = dict(PARADO, pos=P_fim, rot=30, tronco=8, alt=0.8, quadril=(-28, -4), joelho=(38, 16), tornozelo=(-10, -4), cabeca=4, olha=0, **COLO)
    abraca = dict(PARADO, pos=P_fim, rot=58, tronco=-4, alt=0.84, cabeca=16, olha=0, **dict(COLO, cotovelo=(-62, -62)))   # aperta o menino e olha para ele
    ve_gol = dict(PARADO, pos=P_fim, rot=88, tronco=-2, alt=0.85, cabeca=-2, olha=48, **dict(COLO, cotovelo=(-58, -58)))   # o gol onde a bola entrou
    kk += [(f_dv - 1, dict(gd, olha=-36, cabeca=-6))] + corre1 + [(f_dv + 12, freia), (f_dv + 16, pega), (f_dv + 20, vira)] + corre2 + \
          [(f_dv + 37, freia2), (f_dv + 47, abraca), (f_dv + 58, abraca), (f_dv + 72, ve_gol), (END, dict(ve_gol, cabeca=-4))]
    kk.sort(key=lambda q: q[0]); K.anima(kk, A, END, vida=0.3, molas=dict(pos=(0, 6.0, 0.8), rot=(0, 5.0, 0.8)))
    # o menino: olha para cima (para o cabo); quando você chega, é empurrado para a direita e cai
    f_emp = f_dv + 9
    pm = dict(PARADO, pos=(-2.15, Yg - 0.4, 0), rot=0)
    # o menino: assusta-se com o cabo; quando você chega ele levanta os braços, vai para o seu colo (preso ao seu peito, quadro a quadro), e você o põe no chão
    CARGA = dict(PARADO, ombro=(-30, -30), abre=(10, 10), cotovelo=(-58, -58), quadril=(-74, -74), joelho=(86, 86), tornozelo=(-22, -22))   # sentado no seu colo, as mãos no seu antebraço
    em_pe = (-2.15, Yg - 0.4, 0)
    km = [(A, dict(pm, cabeca=0)), (F(36.9 - DT), dict(pm, cabeca=0)), (F(37.4 - DT), dict(pm, cabeca=-24)), (f_dv + 6, dict(pm, cabeca=-24)),
          (f_dv + 11, dict(pm, cabeca=0, ombro=(-120, -120), cotovelo=(-24, -24)))]
    sobe = (f_dv + 12, f_dv + 16)
    suav = lambda u: 0.0 if u <= 0 else 1.0 if u >= 1 else u * u * (3 - 2 * u)
    for f in range(sobe[0], END + 1):                                          # preso ao seu peito quadro a quadro até o fim
        sc.frame_set(f)
        T_ = K.tronco.matrix_world; peito = T_ @ Vector((0.24, -0.24, 0.2))        # no quadril, de lado: os dois rostos aparecem
        yaw = math.degrees(K.raiz.matrix_world.to_euler().z)
        no_colo = tuple(peito + Vector((0, 0, -0.84)))      # baixo: as duas cabeças não se encostam
        u = suav((f - sobe[0]) / (sobe[1] - sobe[0]))
        pos_ = tuple(a_ + (b_ - a_) * u for a_, b_ in zip(em_pe, no_colo))
        pz = dict(CARGA) if u > 0.5 else dict(pm, ombro=(-110, -110), cotovelo=(-30, -30))
        g = suav((f - (f_dv + 60)) / 14.0)                                      # olha para a frente (rosto para a câmera) e depois para o gol, junto com você
        pz.update(olha=48 * g, cabeca=-4 - 4 * g)
        pz.pop("pos", None); pz.pop("rot", None)
        km.append((f, dict(pz, pos=pos_, rot=yaw)))
    sc.frame_set(A)
    M.anima(km, A, END, vida=0.4, molas=dict(pos=(0, 14.0, 0.95), rot=(0, 10.0, 0.9)))
    K.expressao([(A, dict(lid=0.2)), (f_cab, dict(boca="o", brow=0.9, olhos=1.15)), (f_cab + 30, dict(lid=0.35, brow=-0.6)), (f_dv, dict(lid=0.4, brow=-0.7)),
                 (f_dv + 40, dict(boca="sorriso", brow=0.3))], A, END, seed=11)
    M.expressao([(A, dict(boca="sorriso")), (F(37.4 - DT), dict(boca="o", brow=0.9, olhos=1.15)), (f_dv + 32, dict(boca="sorriso", brow=0.4))], A, END, seed=12)
    S1.expressao([(A, dict(lid=0.3, brow=-0.4))], A, END, seed=13)
    # a câmera de TV pendurada: caixa escura com lente, um cabo que segura por cima e um pedaço de cabo que cai junto
    tv = empty("tvcam", None, (-2.15, Yg - 0.4, 3.7))
    H3.loft("tv_corpo", [(0.0, 0.3, 0.2), (0.32, 0.3, 0.2)], H3.estilo("#3a4356", "#1c2230"), tv, loc=(0, 0, -0.16), expo=5.0, seg=32, contorno=0.004)
    H3.loft("tv_lente", [(0.0, 0.1, 0.1), (0.22, 0.12, 0.12)], H3.estilo("#14161c", "#0a0b0f"), tv, loc=(0, -0.26, -0.05), expo=2.0, seg=24, contorno=0.003, dx=0.0).rotation_euler = (math.radians(90), 0, 0)
    H3.esfera("tv_luz", 0.035, 0.02, 0.035, H3.plano("#e2364b"), tv, (-0.2, -0.21, 0.12), contorno=0.0, seg=12, an=8)
    H3.tubo("tv_cabo_b", [(0, 0, 0.16), (0, 0, 0.7)], [0.012, 0.012], H3.estilo("#14161c", "#0a0b0f"), tv, contorno=0.002, seg=10, tampa=2)
    H3.tubo("cabo_alto", [(-2.15, Yg - 0.4, 4.4), (-2.15, Yg - 0.4, 8.0)], [0.012, 0.012], H3.estilo("#14161c", "#0a0b0f"), None, contorno=0.002, seg=10, tampa=2)
    z_topo = 3.7; z_pouso = 0.33
    for f in range(A, END + 1):
        t = real(f) / 24.0
        z = z_topo - 0.5 * 9.8 * t * t if f > f_cab else z_topo
        if z <= z_pouso:
            z = z_pouso + 0.0
        tv.location = (-2.15, Yg - 0.4, z)
        tv.rotation_euler = (0, math.radians(14 * min(1.0, t * 3)) if f > f_cab else 0.0, math.radians(-10 * min(1.0, t * 2)) if f > f_cab else 0.0)
        key(tv, "location", f, "LINEAR"); key(tv, "rotation_euler", f, "LINEAR")
    f_crash = next((f for f in range(f_cab, END + 1) if z_topo - 0.5 * 9.8 * (real(f) / 24.0) ** 2 <= z_pouso), None)
    # a bola: no ponto; chutada em f_k; voa 6 quadros de tempo do mundo até o canto direito (entra no "A bola entra") e fica na rede
    alvo = (1.25, Yg + 0.8, 0.9); k0 = real(f_k)
    for f in range(A, END + 1):
        if f < f_k:
            loc = (0.0, ys, 0.11)
        else:
            u = min(1.0, (real(f) - k0) / 6.0)
            loc = tuple(a_ + (b_ - a_) * u for a_, b_ in zip((0.0, ys, 0.11), alvo)); loc = (loc[0], loc[1], loc[2] + 0.55 * 4 * u * (1 - u))
        bola.location = loc; bola.rotation_euler = (f * 0.15, f * 0.1, 0); key(bola, "location", f, "LINEAR"); key(bola, "rotation_euler", f, "LINEAR")
    f_gol = next((f for f in range(f_k, END + 1) if (real(f) - k0) / 6.0 >= 1.0), END)
    # o cabo arrebenta: anel e faíscas no ponto; o tempo se dobra
    C3.onda("cabo_a", (-2.15, Yg - 0.4, 4.4), f_cab, normal=(0, -1, 0.2), raio=0.5, dur=18, esp=0.012, cor="#ffe6b0")
    C3.onda("tempo6", (0.0, ys + 0.8, 1.0), f_cab, normal=(0, -1, 0.1), raio=2.8, dur=34, esp=0.04, cor="#a8ecff")
    if f_crash:
        C3.onda("poeira_c", (-2.15, Yg - 0.4, 0.05), f_crash, normal=(0, 0, 1), raio=1.0, dur=20, esp=0.03, cor="#e8e0c8")
    C3.onda("gol_a", (alvo[0], alvo[1], alvo[2]), f_gol, normal=(0, -1, 0.1), raio=0.6, dur=18, esp=0.02, cor="#ffffff")
    C3.onda("volta7", (0.0, Yg, 1.0), f_ret, normal=(0, -1, 0.1), raio=1.4, dur=22, esp=0.015, cor="#ffe6b0")   # no gol, atrás deles (não passa na frente da câmera)
    numero_flutuante("n6", 0.0, Yg, 2.5, [("0,5 s", F(41.15 - DT), F(41.62 - DT))], A, END, cor="#ffffff", tam=0.36, rx=78)
    numero_flutuante("rot_b", 1.2, Yg - 0.2, 2.35, [("BOLA", F(41.75 - DT), F(43.1 - DT))], A, END, cor="#ffffff", tam=0.42, rx=78)
    numero_flutuante("rot_m", -1.9, Yg - 0.5, 2.55, [("MENINO", F(42.35 - DT), F(43.1 - DT))], A, END, cor="#ffe27a", tam=0.42, rx=78)
    numero_flutuante("n7", 0.0, Yg + 3.0, 3.6, [("80 mil", F(45.6 - DT), None)], A, END, cor="#ffffff", tam=0.55, rx=76)
    kf = [(A, 0, 0), (f_cab - 1, 0, 0), (f_cab + 8, 1, 0.45), (f_ret, 1, 0.45), (f_ret + 10, 0, 0), (END, 0, 0)]
    return dict(Yg=Yg, ys=ys, yk=yk, kf=kf, f_cab=f_cab, f_dv=f_dv, f_crash=f_crash, f_gol=f_gol, K=K, M=M, tv=tv)


@cena_(6)
def s06(c):
    """final da Copa: o gol estreito à noite, o batedor no ponto, o menino e a câmera de TV à esquerda. O cabo arrebenta (close), o mundo cai a 1/8 da velocidade,
    a câmera de TV cai devagar sobre o menino e a bola sai; no fim, o seu rosto: a bola ou o menino?"""
    A, END = F(34.2 - DT), F(48.7 - DT)
    m = final_mundo(c, A, END); Yg = m["Yg"]; kf = m["kf"]
    t1, t2, t3, t4 = 36.6 - DT, 37.55 - DT, 38.75 - DT, 41.65 - DT
    # "Final da Copa": a grua desce do alto sobre o estádio até as costas do batedor
    camera_cine(c, "cam6a", B[5], t1, [(-1.0, -3.0, 5.6), (-0.75, -2.2, 3.9), (-0.5, -1.55, 2.6), (-0.4, -1.3, 2.3)], [(-0.3, Yg + 1.5, 0.4), (-0.3, Yg, 0.95), (-0.3, Yg, 1.15)],
                lens=26, fstop=4.0, v_in=0.2, v_out=0.8)
    camera_cine(c, "cam6b", t1, t2, [(-1.6, -0.6, 1.6), (-1.55, -0.4, 1.8), (-1.5, -0.2, 2.0)], [(-2.15, Yg - 0.4, 2.7), (-2.15, Yg - 0.4, 3.7)], lens=28, fstop=3.2, v_in=0.8, v_out=0.8)
    camera_cine(c, "cam6c", t2, t3, [(-1.3, Yg - 2.0, 3.6), (-1.5, Yg - 1.8, 3.7), (-1.7, Yg - 1.6, 3.8)], [(-2.15, Yg - 0.4, 4.0)], lens=22, fstop=2.4, v_in=0.8, v_out=0.8, filtro=kf)
    t5 = wt(6, "A") - 0.12
    camera_cine(c, "cam6d", t3, t5, [(-0.5, -1.45, 2.2), (-0.45, -1.35, 2.15), (-0.4, -1.25, 2.1)], [(-0.7, Yg, 1.2)], lens=30, fstop=4.0, v_in=0.8, v_out=0.8, filtro=kf)   # BOLA e MENINO nos dois lados do quadro
    # "A bola... ou o menino?": entra devagar no seu rosto; os olhos vão de um lado para o outro
    yk = m["yk"]
    camera_cine(c, "cam6e", t5, B[6] + 0.4, [(0.22, yk - 1.05, 1.5), (0.14, yk - 0.9, 1.5), (0.08, yk - 0.78, 1.5)], [(0.0, yk, 1.38)], lens=22, fstop=2.8, v_in=0.8, v_out=0.8,
                segue=m["K"].cabeca, peso=0.7, filtro=kf)
    c["sc"].render.use_motion_blur = True; c["sc"].render.motion_blur_shutter = 0.5


@cena_(7)
def s07(c):
    """você escolhe o menino: mergulha para ele, a câmera de TV cai onde ele estava, a bola entra, o tempo volta, 80 mil se calam e se levantam"""
    A, END = F(34.2 - DT), F(48.7 - DT)
    m = final_mundo(c, A, END); Yg = m["Yg"]; kf = m["kf"]
    t1, t2 = 44.75 - DT, 46.7 - DT
    # 14 mm no chão, perto do menino: você vem correndo da direita, a câmera de TV despenca do alto do quadro, você o pega e sai com ele
    camera_cine(c, "cam7a", B[6], t1, [(-3.0, Yg - 2.0, 0.28), (-2.95, Yg - 1.9, 0.3), (-2.9, Yg - 1.82, 0.32)], [(-1.4, Yg - 0.3, 1.15)], lens=14, fstop=3.2, v_in=0.8, v_out=0.8,
                segue=m["K"].tronco, peso=0.25, filtro=kf, clip=0.05)
    camera_cine(c, "cam7b", t1, t2, [(0.2, Yg - 4.6, 1.5), (0.15, Yg - 4.4, 1.5), (0.1, Yg - 4.2, 1.5)], [(-1.6, Yg - 1.3, 0.9)], lens=26, fstop=3.2, v_in=0.8, v_out=0.8, filtro=kf)
    # por cima do ombro deles: os dois olham o gol onde a bola entrou e a torcida inteira se levanta (o que eles veem); sobe e recua devagar
    camera_cine(c, "cam7c", t2, B[7] + 0.4, [(-2.3, 1.5, 1.45), (-2.35, 1.3, 1.62), (-2.4, 1.1, 1.82)], [(-0.6, Yg + 3.5, 1.9), (-0.4, Yg + 3.5, 2.5)], lens=24, fstop=3.2, v_in=0.8, v_out=0.0)
    c["sc"].render.use_motion_blur = True; c["sc"].render.motion_blur_shutter = 0.5


# ====================================================================== 8. e você? (fala 8)
@cena_(8)
def s08(c):
    """a pergunta: você entre a taça (esquerda, num pedestal, dourada) e o menino (direita), num palco liso e quente; o seu olhar vai de um a outro e fica de frente"""
    A, END = F(B[7] - 0.4), F(B[8] + 0.4)
    p = pal("final"); mundo(dict(top="#4a2c14")); sc = c["sc"]
    piso_liso("#6a3d1e")
    y0 = 1.4
    Hv = heroi3("voce8", 0.0, y0, p); Hv.rosto(boca="reta", lid=0.0)
    M = heroi3("menino8", 1.35, y0, p, roupa="#f2c94c", calca="#2a3a5a", escura="#c8962a", gola="#f2c94c", escala=0.72, cabeca=0.95, body_w=0.92, arm_len=0.95); M.rosto(boca="reta")
    OB.caixa("pedestal", -1.35, y0 - 0.25, 0.0, 0.5, 0.75, 0.5, "#8a6440", tampo="#c9a06a", lado="#6d4e30", aresta="#e8c898")
    ouro = H3.estilo("#f2c94c", "#c8962a", limiar=0.45)
    taca = empty("taca_c", None, (-1.35, y0, 0.78))
    H3.loft("taca_base", [(0.0, 0.14, 0.14), (0.05, 0.14, 0.14), (0.07, 0.05, 0.05), (0.28, 0.04, 0.04)], ouro, taca, expo=2.0, seg=32, contorno=0.004)
    H3.loft("taca_copa", [(0.28, 0.05, 0.05), (0.34, 0.13, 0.13), (0.5, 0.2, 0.2), (0.6, 0.21, 0.21), (0.62, 0.19, 0.19)], ouro, taca, expo=2.0, seg=32, contorno=0.004)
    for sg in (-1, 1):
        H3.tubo(f"taca_al{sg}", [(sg * 0.2, 0, 0.56), (sg * 0.3, 0, 0.5), (sg * 0.28, 0, 0.4), (sg * 0.15, 0, 0.36)], [0.014] * 4, ouro, taca, contorno=0.003, seg=10, tampa=3)
    ch = [(A, dict(PARADO, olha=0, cabeca=6)), (F(48.9 - DT), dict(PARADO, olha=0, cabeca=6)), (F(49.6 - DT), dict(PARADO, olha=-34, cabeca=4)), (F(50.1 - DT), dict(PARADO, olha=-34, cabeca=4)),
          (F(50.6 - DT), dict(PARADO, olha=34, cabeca=4)), (F(51.0 - DT), dict(PARADO, olha=30, cabeca=4)), (END, dict(PARADO, olha=0, cabeca=2))]
    Hv.anima(ch, A, END, vida=0.5)
    M.anima([(A, dict(PARADO, cabeca=4, olha=-18)), (END, dict(PARADO, cabeca=4, olha=-18))], A, END, vida=0.4)
    Hv.expressao([(A, dict(lid=0.2)), (F(49.6 - DT), dict(brow=0.3)), (F(50.6 - DT), dict(boca="triste", brow=0.4, lid=0.15))], A, END, seed=14)
    M.expressao([(A, dict(boca="sorriso"))], A, END, seed=15)
    # meia volta lenta: começa atrás da taça (a taça grande em primeiro plano), passa de frente e termina no seu rosto
    camera_cine(c, "cam8a", B[7], B[8] + 0.4, [(-2.1, 0.15, 1.2), (-1.0, -0.3, 1.35), (-0.25, 0.05, 1.45), (0.0, 0.3, 1.47)], [(-0.9, y0, 1.0), (0.0, y0, 1.3), (0.0, y0, 1.42)],
                lens=20, fstop=2.8, v_in=0.2, v_out=0.0, segue=Hv.cabeca, peso=0.35)
    sc.render.use_motion_blur = True; sc.render.motion_blur_shutter = 0.5


def com_vida(fn):
    """depois de montar a cena: tremido leve nos objetos (bonecos de fora), figurantes balançando, câmera na mão; grava onde estão os rostos"""
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


def _fim():
    for _k, (_a, _b, _fn) in list(P4.CENAS.items()):
        P4.CENAS[_k] = (_a, _b, com_vida(_fn))


if __name__ == "__main__":
    _fim()
    P4.main()
