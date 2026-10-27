"""Animação de verdade das sequências 4C a 17C da parte 2 de "O abrigo" (v4, 27/10/2026), por cima dos builders v5 do story_abrigo2.py.
Pedido do Paulo: "agora vai ter que ajustar toda a animação; muita animação defeituosa, muita cena nada a ver" (o v3 só animou do 1C ao 4B).
Método: cada plano roda o builder do storyboard (cenário, bonecos e objetos no estado do quadro 1), as funções abaixo registram quem foi criado
(bonecos, Sem-Osso, mãos) e a ação de cada plano põe chaves de verdade: olhar que vira, corpo que reage, gesto, objeto na mão (preso ao punho), câmera
planejada (acoes_abrigo2.camera) e foco que passa de um ponto ao outro. Nada aparece do nada e nada fica parado: todo plano tem uma coisa acontecendo,
com antecipação, a ação e a reação."""
import math, random
import bpy
from mathutils import Vector
import lib
from lib import key, empty
import cena
import acoes_abrigo2 as AC
from acoes_abrigo2 import camera, sem_osso_vivo, boca_abre, sombra, suave, faixa, costas, ruido, lerp, FPS, BY, SUSTO_R, pos_cabeca
import story_abrigo2 as S
import story_abrigo as SA
import story3_abrigo as S3
import objetos3d_abrigo as O3, objetos3d_abrigo2 as O2, ambiente_noite as AN, elenco3d_abrigo as E3
import heroi3d as H3
from heroi3d import corrida, _monotona

ACAO = AC.ACAO
acao = AC.acao
class _Reg(dict):
    def __missing__(self, k):
        for c in (k + "_inv", "g_" + k):
            if c in self:
                return dict.__getitem__(self, c)
        raise KeyError(k)


REG = _Reg()      # nome -> Heroi3D criado pelo builder (aceita 'eu' para 'eu_inv' e 'lider' para 'g_lider')
MAOS = {}         # nome -> Mao3D
CAMS = []         # [a, b] do último CM() do builder (início e fim da câmera do storyboard)

# ---------------------------------------------------------------- ganchos: registram o que o builder cria
_pose0 = H3.Heroi3D.pose
_rosto0 = H3.Heroi3D.rosto


def _pose(self, *a, **k):
    self._P = dict(k)
    return _pose0(self, *a, **k)


def _rosto(self, boca="reta", lid=0.0, brow=0.0):
    self._R = dict(boca=boca, lid=lid, brow=brow)
    return _rosto0(self, boca=boca, lid=lid, brow=brow)


H3.Heroi3D.pose = _pose
H3.Heroi3D.rosto = _rosto


def _reg_fn(mod, nome):
    o = getattr(mod, nome)
    def f(*a, **k):
        h = o(*a, **k)
        try:
            REG[h.nome] = h
        except Exception:
            pass
        return h
    setattr(mod, nome, f)


for _m, _n in ((O2, "faz_grupo"), (SA, "ator3"), (O2, "sem_osso"), (E3, "faz")):
    _reg_fn(_m, _n)
POV = []
_pov0 = O3.maos_pov3d


def _pov(*a, **k):
    r = _pov0(*a, **k)
    POV.append(r)
    return r


O3.maos_pov3d = _pov
_mao0 = O3.Mao3D.__init__


def _mao_init(self, nome, *a, **k):
    _mao0(self, nome, *a, **k)
    MAOS[nome] = self


O3.Mao3D.__init__ = _mao_init
_CM0 = S.CM


def _cm(a, b):
    CAMS[:] = [a, b]
    return _CM0(a, b)


S.CM = _cm


def prepara(plano):
    """roda o builder do storyboard no estado do quadro 1 e devolve (REG, MAOS)"""
    REG.clear(); MAOS.clear(); CAMS.clear(); POV.clear()
    S.FIM = False
    S.BUILD[plano]()
    bpy.context.view_layer.update()
    return REG


def O(nome):
    return bpy.data.objects.get(nome)


def wrap(a):
    return (a + 180.0) % 360.0 - 180.0


def graus(r):
    return math.degrees(r)


# ---------------------------------------------------------------- bonecos
def estado(h):
    P = dict(getattr(h, "_P", {}) or {})
    r = h.raiz.rotation_euler
    P["pos"] = tuple(h.raiz.location)
    P["rot"] = (graus(r.x), graus(r.y), graus(r.z))
    return P


def _ver(cur, alvo, corpo=0.0):
    """vira a cabeça (e o corpo, quando passa de 70 graus) para um ponto do mundo"""
    px, py = cur["pos"][0], cur["pos"][1]
    d = Vector((alvo[0] - px, alvo[1] - py, 0))
    if d.length < 1e-4:
        return
    rz = cur["rot"][2]
    des = graus(math.atan2(d.x, -d.y))
    rel = wrap(des - rz)
    if abs(rel) <= 70:
        cur["olha"] = rel; cur["giro"] = rel * 0.25 + corpo
    else:
        s = 1 if rel > 0 else -1
        cur["rot"] = (cur["rot"][0], cur["rot"][1], rz + rel - 60 * s)
        cur["olha"] = 60 * s; cur["giro"] = 15 * s


def mov_h(h, N, passos, vida=1.0, seed=3, mola=True, molas=None):
    """passos = [(quadro, dict)]: cumulativos a partir do estado do builder. Chaves de pose do Heroi3D (ombro, cotovelo, abre, quadril, joelho, tronco, cabeca,
    olha, giro, alt, pos, rot...) mais ver=(x,y) (olha para o ponto) e dpos=(dx,dy,dz) (anda a partir do anterior)"""
    cur = estado(h)
    ks = [(1, dict(cur))]
    for f, d in passos:
        cur = dict(cur); d = dict(d)
        ver = d.pop("ver", None); dpos = d.pop("dpos", None); corpo = d.pop("corpo", 0.0)
        if "rot" in d and not isinstance(d["rot"], (tuple, list)):
            d["rot"] = (cur["rot"][0], cur["rot"][1], d["rot"])
        cur.update(d)
        if dpos:
            cur["pos"] = tuple(a + b for a, b in zip(cur["pos"], dpos))
        if ver is not None:
            _ver(cur, ver, corpo)
        ks.append((max(2, min(N, f)), cur))
    if ks[-1][0] < N:
        ks.append((N, dict(ks[-1][1])))
    sombra(h).anima(ks, 1, N, vida=vida, seed=seed, mola=mola, molas=molas)
    return h


def cara(h, N, chaves, piscar=True):
    base = dict(getattr(h, "_R", dict(boca="reta", lid=0.3, brow=0.0)))
    ks = list(chaves)
    if not ks or ks[0][0] > 1:
        ks = [(1, base)] + ks
    h.expressao(ks, 1, N, piscar=piscar)


def olhar(h, N, quando, pontos):
    """a cabeça passa por uma lista de pontos: quando = [quadros], pontos = [(x,y)] (curta e suave)"""
    return [(f, dict(ver=p)) for f, p in zip(quando, pontos)]


def pega(obj, h, lado="B"):
    """prende o objeto ao punho do boneco (o objeto acompanha o braço): mantém a posição do quadro 1"""
    bpy.context.view_layer.update()
    p = h.punho[lado]
    obj.parent = p
    obj.matrix_parent_inverse = p.matrix_world.inverted()
    return obj


def anda(h, N, de, ate, f0=1, f1=None, ciclo=18, inclina=3, rot=None, arranque=0.15, freia=0.15, vida=0.8, seed=3, antes=None, depois=None):
    """caminhada de verdade (ciclo longo, quase sem inclinar) entre dois pontos; fora de f0-f1 fica parado"""
    f1 = N if f1 is None else f1
    r = rot
    if r is None:
        d = Vector(ate) - Vector(de)
        r = graus(math.atan2(d.x, -d.y))
    ch = corrida(f0, f1, tuple(de), tuple(ate), rot=r, ciclo=ciclo, inclina=inclina, arranque=arranque, freia=freia)
    if f0 > 1:
        e0 = estado(h)
        if antes:
            e0.update(antes)
        e0["pos"] = tuple(de); e0["rot"] = (0.0, 0.0, r)
        ch = [(1, e0), (max(2, f0 - 1), dict(e0))] + ch
    if f1 < N:
        fim = dict(ch[-1][1])
        if depois:
            fim.update(depois)
        ch = ch + [(min(N, f1 + 6), fim), (N, dict(fim))]
    sombra(h).anima(ch, 1, N, vida=vida, seed=seed, molas=dict(pos=(0, 24.0, 1.0), rot=(0, 24.0, 1.0)))


# ---------------------------------------------------------------- objetos
def trilha(o, N, loc=None, rot=None, esc=None):
    """chaves por canal: loc/rot/esc = [(quadro, (x,y,z))] (rot em graus); curva cúbica monótona, uma chave por quadro"""
    if o is None:
        return
    for f in range(1, N + 1):
        if loc:
            o.location = tuple(_monotona([(q, v[k]) for q, v in loc], f) for k in range(3)); key(o, "location", f, "LINEAR")
        if rot:
            o.rotation_euler = tuple(math.radians(_monotona([(q, v[k]) for q, v in rot], f)) for k in range(3)); key(o, "rotation_euler", f, "LINEAR")
        if esc:
            o.scale = tuple(_monotona([(q, v[k]) for q, v in esc], f) for k in range(3)); key(o, "scale", f, "LINEAR")


def visivel(o, N, quando):
    """quando(f) -> bool: liga e desliga o objeto (e os filhos) quadro a quadro, sem interpolar"""
    if o is None:
        return
    alvo = [o] + list(o.children_recursive)
    ant = None
    for f in range(1, N + 1):
        on = bool(quando(f))
        if on == ant and f != N:
            continue
        for x in alvo:
            x.hide_render = not on; key(x, "hide_render", f, "CONSTANT")
        ant = on


def mao_mix(m, a, b, u, f):
    A, B = O3.POSES[a], O3.POSES[b]
    m.pose(a, f=f, dedos=tuple(lerp(x, y, u) for x, y in zip(A["dedos"], B["dedos"])),
           polegar=tuple(lerp(x, y, u) for x, y in zip(A["polegar"], B["polegar"])), abre=lerp(A["abre"], B["abre"], u))


# ---------------------------------------------------------------- câmera
def rota(a, b, N, nk=6, mix=0.0, foco=None, roll=None, warp=1.7):
    """chaves de câmera de a até b (formato do CM: (loc, alvo, lente, fstop, foco[, roll])): curva que não pára (mistura linear e suave)"""
    out = []
    ra = a[5] if len(a) > 5 else 0.0; rb = b[5] if len(b) > 5 else 0.0
    for i in range(nk + 1):
        u = i / nk; f = 1 + round(u * (N - 1)); uw = u ** warp; w = mix * uw + (1 - mix) * (0.35 * uw + 0.65 * suave(uw))     # espreita no começo, decide no meio, assenta no fim
        L = tuple(lerp(x, y, w) for x, y in zip(a[0], b[0])); A = tuple(lerp(x, y, w) for x, y in zip(a[1], b[1]))
        Fo = tuple(lerp(x, y, w) for x, y in zip(a[4], b[4]))
        out.append((f, L, A, math.exp(lerp(math.log(a[2]), math.log(b[2]), w)), Fo, lerp(a[3], b[3], w), lerp(ra, rb, w)))
    return out


def cam_ab(N, mao=0.8, seed=1, tranco=(), passo_corrida=0.0, **kw):
    camera(N, rota(CAMS[0], CAMS[1], N, **kw), mao=mao, seed=seed, tranco=tranco, passo_corrida=passo_corrida)


def semi(h, N, de, para, per=16.0, fase=0.0, seed=3, f0=1, f1=None, grande=1.0, rot=None, tomba=(9.0, -24.0), estica=None):
    """um Sem-Osso que vem aos trancos (desliza, para, desliza) entre dois pontos do chão"""
    f1 = N if f1 is None else f1
    x0, y0 = de; x1, y1 = para
    dx, dy = x1 - x0, y1 - y0
    r = rot if rot is not None else graus(math.atan2(dx, -dy))
    ch = []
    for f in range(1, N + 1, 2):
        u = faixa(f, f0, f1)
        s = math.sin(2 * math.pi * (f / per + fase))
        v = 0.65 * u + 0.35 * suave(u)
        v = max(0.0, min(1.0, v + 0.04 * max(0, s) * (1 if 0 < u < 1 else 0)))
        ch.append((f, dict(pos=(x0 + dx * v - 0.0, y0 + dy * v, 0), rot=r + 7 * s, tronco=24 + 11 * max(0, s) * grande, cabeca=-10 + 10 * s, alt=0.76,
                           ombro=(-28 + 26 * s, -28 - 26 * s), cotovelo=(-20, -24), quadril=(-22 * s, 22 * s), joelho=(10 + 32 * max(0, s), 10 + 32 * max(0, -s)))))
    sem_osso_vivo(h, N, ch, seed=seed, tomba=tomba, estica=estica, base_pulso=lambda f: max(0.0, math.sin(2 * math.pi * (f / per + fase))))


# ====================================================================== 4. o beco: a mão que escorrega
@acao("4C")
def a4C(N):
    """macro das duas mãos: as duas se agarram e tremem; a da Rita é puxada, os dedos escorregam um a um e ela sai do quadro; a do narrador fecha no ar"""
    prepara("4C")
    pa, pb = O("pa"), O("pb"); mn, mr = MAOS["mn"], MAOS["mr"]
    xa, za = pa.location.x, pa.location.z
    Fs = max(4, int(N * 0.35)); Ff = max(Fs + 4, int(N * 0.78))
    for f in range(1, N + 1):
        tr = 0.0035 * math.sin(f * 2.3) + 0.002 * math.sin(f * 5.1)
        u = faixa(f, Fs, N); pull = u ** 1.7
        pb.location = (xa + 0.10 * pull, 6.4 - 0.30 * pull + tr * 0.5, za + 0.012 - 0.025 * pull)
        pb.rotation_euler.z = math.radians(-24 * pull); key(pb, "location", f, "LINEAR"); key(pb, "rotation_euler", f, "LINEAR")
        v = faixa(f, Fs + 3, N); chase = suave(v) * 0.5
        pa.location = (xa + 0.0 + 0.03 * v, 6.6 - 0.10 * chase + tr, za + 0.03 * math.sin(f * 0.9) * (1 - v)); pa.rotation_euler.z = math.radians(180 - 10 * v)
        key(pa, "location", f, "LINEAR"); key(pa, "rotation_euler", f, "LINEAR")
        mao_mix(mr, "segura", "aberta", faixa(f, Fs - 1, Ff), f)
        mao_mix(mn, "segura", "fechada", faixa(f, Ff - 3, N), f)
    camera(N, [(1, (-9.95, 6.5, 1.2), (-9.0, 6.5, 1.2), 85, (-9.0, 6.5, 1.2), 2.0),
               (Fs, (-9.94, 6.47, 1.2), (-9.0, 6.48, 1.2), 85, (-9.0, 6.48, 1.2), 2.0),
               (N, (-9.88, 6.38, 1.19), (-9.0, 6.46, 1.22), 85, (-9.0, 6.6, 1.24), 2.0)], mao=0.7)


@acao("4D")
def a4D(N):
    """câmera lenta rente ao chão: o suéter cai girando devagar e pousa na poça; os anéis abrem na água e uns pingos saltam"""
    prepara("4D")
    su = O("sue"); z0 = 0.42; z1 = 0.03
    Fi = max(8, int(N * 0.62))
    rz = [(1, 0.0), (Fi, 38.0), (N, 41.0)]
    zs = []
    for f in range(1, N + 1):
        u = faixa(f, 1, Fi)
        z = lerp(z0, z1, u * u) if f <= Fi else z1 + 0.012 * math.exp(-(f - Fi) / 3.0) * math.cos((f - Fi) * 1.2)
        zs.append((f, (-9.3 + 0.04 * u, 6.4 - 0.03 * u, z)))
    trilha(su, N, loc=zs, rot=[(1, (0, 0, 0)), (Fi - 3, (18, -12, 22)), (Fi, (4, -3, 38)), (N, (0, 0, 41))],
           esc=[(1, (2.6, 2.6, 2.6)), (Fi - 1, (2.6, 2.6, 2.6)), (Fi + 1, (2.9, 2.9, 2.2)), (N, (2.6, 2.6, 2.6))])
    rng = random.Random(4)
    for k, R in enumerate((0.25, 0.45, 0.7)):
        a = O3.anel(f"onda{k}", R, 0.006, O3.brilha("#b8c8dc", 0.8), None, (-9.3, 6.4, 0.014), eixo="Z", seg=36, contorno=0.0)
        a = O(f"onda{k}") or a
        d0 = Fi + 2 * k
        esc = [(1, (0.001, 0.001, 0.001)), (d0, (0.001, 0.001, 0.001)), (min(N, d0 + 11), (1.0, 1.0, 0.5)), (N, (1.12, 1.12, 0.3))]
        trilha(a, N, esc=esc)
    for k in range(7):
        g = O2.esfera(f"gota{k}", 0.012, 0.012, 0.014, O3.M("#9fb0c8", "#6c7c94", "#ffffff"), None, (-9.3, 6.4, 0.03), contorno=0.0, seg=10, an=6)
        g = O(f"gota{k}") or g
        ang = rng.uniform(0, 6.28); vel = rng.uniform(0.25, 0.5); vz = rng.uniform(0.7, 1.2)
        ks = []
        for f in range(1, N + 1):
            t = max(0, f - Fi) / FPS
            if f < Fi:
                ks.append((f, (-9.3, 6.4, -1.0))); continue
            z = 0.03 + vz * t - 4.9 * t * t
            ks.append((f, (-9.3 + math.cos(ang) * vel * t * 0.5, 6.4 + math.sin(ang) * vel * t * 0.5, max(-1.0, z) if z > 0.025 else -1.0)))
        trilha(g, N, loc=ks)
    camera(N, [(1, (-10.4, 6.0, 0.34), (-9.3, 6.4, 0.38), 50, (-9.3, 6.4, 0.36), 2.8),
               (Fi - 2, (-10.36, 6.02, 0.25), (-9.3, 6.4, 0.16), 50, (-9.3, 6.4, 0.1), 2.8),
               (N, (-10.2, 6.1, 0.17), (-9.3, 6.4, 0.07), 50, (-9.3, 6.4, 0.04), 2.8)], mao=0.5)


@acao("4E")
def a4E(N):
    """POV do narrador no beco: as três silhuetas entram contra a luz da boca da rua, aos trancos; ele gira a cabeça num chicote (câmera torta) para a parede"""
    prepara("4E")
    alvos = [(-6.4, 6.5), (-5.4, 7.6), (-7.6, 5.4)]
    for k, nome in enumerate(("so0", "so1", "so2")):
        h = REG[nome]; x, y = alvos[k]
        semi(h, N, (x, y), (x - 1.5 + 0.2 * k, y - 0.6 * (1 if k == 1 else -0.5 * k)), per=15 + 2 * k, fase=0.25 * k, seed=3 + k, rot=-90 + 6 * (k - 1))
    Fw = int(N * 0.45)
    camera(N, [(1, (-13.0, 6.5, 1.5), (-4.5, 6.5, 1.3), 24, (-6.0, 6.5, 1.3), 8.0, -3.0),
               (Fw, (-12.98, 6.5, 1.5), (-4.7, 6.5, 1.3), 24, (-6.2, 6.5, 1.3), 8.0, -3.0),
               (Fw + 5, (-12.9, 6.52, 1.5), (-7.5, 8.5, 1.35), 24, (-8.5, 8.5, 1.3), 8.0, -9.0),
               (Fw + 9, (-12.85, 6.55, 1.5), (-9.5, 9.5, 1.3), 24, (-9.5, 9.0, 1.3), 8.0, -14.0),
               (N, (-12.82, 6.56, 1.5), (-9.55, 9.6, 1.32), 24, (-9.5, 9.0, 1.3), 8.0, -15.0)], mao=1.2)


@acao("4F")
def a4F(N):
    """de cima, a grua sobe: ele sozinho no meio da praça gira devagar, e os quatro Sem-Osso fecham o cerco, cada um no seu ritmo"""
    prepara("4F")
    eu = REG["eu"]
    mov_h(eu, N, [(int(N * 0.3), dict(ver=(-10.5, 6.5), tronco=6, cotovelo=(-30, -30))), (int(N * 0.55), dict(ver=(-17.5, 0.5), tronco=8)),
                  (int(N * 0.8), dict(ver=(-24.0, 6.5))), (N, dict(ver=(-17.5, 12.5), tronco=10))], vida=1.5)
    cara(eu, N, [(1, dict(boca="o", lid=0.0)), (N, dict(boca="triste", lid=0.0, brow=0.8))])
    pts = {"so0": (-24.0, 6.5), "so1": (-17.5, 0.5), "so2": (-17.5, 12.5), "so3": (-10.5, 6.5)}
    for k, (nome, (x, y)) in enumerate(pts.items()):
        h = REG[nome]; cx, cy = -17.5, 6.5
        d = math.hypot(cx - x, cy - y); ux, uy = (cx - x) / d, (cy - y) / d
        semi(h, N, (x, y), (x + ux * 3.0, y + uy * 3.0), per=14 + 2.5 * k, fase=0.23 * k, seed=3 + k)
    camera(N, [(1, (-17.5, -1.0, 4.0), (-17.5, 6.5, 0.8), 24, (-17.5, 6.5, 0.8), 11.0),
               (int(N * 0.5), (-17.5, -1.4, 7.0), (-17.5, 6.5, 0.7), 24, (-17.5, 6.5, 0.7), 11.0),
               (N, (-17.5, -1.8, 10.0), (-17.5, 6.5, 0.5), 24, (-17.5, 6.5, 0.5), 11.0)], mao=0.5)


# ====================================================================== 5. a lanterna, a pancada, o apagão
@acao("5A")
def a5A(N):
    """macro: o polegar de pano verde aperta o botão vermelho, o facho pisca duas vezes e acende; a mão gira a lanterna e o facho varre a poça"""
    prepara("5A")
    lan = O("lant"); mao = O("pm")
    Fo = max(4, int(N * 0.3))
    visivel(O("lant_facho"), N, lambda f: f >= Fo and not (f == Fo + 1))
    visivel(O("lant_bloom"), N, lambda f: f >= Fo and not (f == Fo + 1))
    m = MAOS["mt"]
    x, y, z = lan.location
    for f in range(1, N + 1):
        u = faixa(f, Fo + 2, N); rz = 30.0 * suave(u)
        pre = faixa(f, 1, Fo) * (1 - faixa(f, Fo, Fo + 3))
        lan.rotation_euler = (math.radians(-4 * pre), 0, math.radians(rz)); key(lan, "rotation_euler", f, "LINEAR")
        lan.location = (x, y, z + 0.006 * math.sin(f * 0.8)); key(lan, "location", f, "LINEAR")
        mao.rotation_euler.z = math.radians(180 + rz); mao.location = (x, y + 0.16 + 0.04 - 0.02 * pre, z); key(mao, "rotation_euler", f, "LINEAR"); key(mao, "location", f, "LINEAR")
        mao_mix(m, "pinca", "segura", faixa(f, Fo - 2, Fo + 2), f)
    camera(N, [(1, (-21.6, 5.55, 1.1), (-22.5, 4.9, 1.0), 50, (-22.5, 5.0, 1.0), 2.8),
               (Fo + 2, (-21.55, 5.5, 1.1), (-22.5, 4.9, 1.0), 50, (-22.5, 5.0, 1.0), 2.8),
               (N, (-21.35, 5.3, 1.12), (-22.55, 4.7, 0.9), 50, (-22.5, 4.2, 0.4), 2.8)], mao=0.5)


@acao("5B")
def a5B(N):
    """POV: o vulto de pano no rosto levanta o taco, recua o corpo, dá um passo e desce a pancada na minha direção; o quadro dá o tranco e cai"""
    prepara("5B")
    t = REG["taco"]
    bat = O("taco_obj")
    t.raiz.rotation_euler.z = math.radians(90)           # o vulto olha para o narrador (a câmera), que está a +x dele
    pega(bat, t, "B")
    Fi = max(8, int(N * 0.62))
    alto = dict(ombro=(-172, -152), cotovelo=(-20, -30), abre=(8, 10), tronco=0)
    mov_h(t, N, [(4, dict(alto, tronco=-14, cabeca=-10, ombro=(-182, -166))), (Fi - 3, dict(alto, tronco=-14, cabeca=-10, ombro=(-186, -170))),
                 (Fi, dict(ombro=(-52, -44), cotovelo=(-10, -14), tronco=36, cabeca=18, dpos=(0.55, 0, 0))), (N, dict(ombro=(-40, -36), tronco=40, cabeca=20, dpos=(0.2, 0, 0)))],
          vida=0.4, seed=5, molas=dict(ombro=(0, 9.0, 0.8), cotovelo=(0, 9.0, 0.8), tronco=(0, 6.0, 0.8)))
    cara(t, N, [(1, dict(boca="reta", lid=0.3)), (Fi - 4, dict(boca="o", lid=0.0, brow=-0.6))])
    fl = O3.halo_cam("pancada_flash", (-17.9, 6.5, 1.55), 0.8, "#ffffff", 0.95)
    visivel(O("pancada_flash"), N, lambda f: Fi <= f <= Fi + 1)
    camera(N, [(1, (-17.6, 6.5, 1.55), (-20.5, 6.5, 1.7), 24, (-20.5, 6.5, 1.7), 5.6, 6.0),
               (Fi - 2, (-17.62, 6.5, 1.56), (-20.4, 6.5, 1.68), 24, (-20.2, 6.5, 1.5), 5.6, 7.0),
               (Fi + 2, (-17.5, 6.4, 1.32), (-20.0, 6.5, 2.2), 24, (-19.5, 6.5, 1.5), 3.2, -10.0),
               (N, (-17.2, 6.3, 0.85), (-19.0, 6.4, 3.0), 24, (-19.0, 6.4, 1.0), 2.4, -34.0)], mao=1.0, tranco=(Fi,))


@acao("5C")
def a5C(N):
    """rente à cinza: o narrador caído mal respira; as botas de dois do grupo chegam andando e o facho da lanterna vai varrendo até o rosto dele"""
    prepara("5C")
    n = REG["eu"]
    mov_h(n, N, [(N // 2, dict(cabeca=-4, tronco=-2)), (N, dict(cabeca=-8))], vida=2.2, seed=2)
    cara(n, N, [(1, dict(boca="o", lid=1.15)), (N // 2, dict(boca="o", lid=0.9)), (N, dict(boca="triste", lid=1.15))], piscar=False)
    lan = O("lant")
    for k, nome in enumerate(("g0", "g1")):
        h = REG[nome]
        y = 7.4 if k == 0 else 5.4
        anda(h, N, (-21.3, y, 0), (-19.5 - 0.1 * k, 6.7 if k == 0 else 6.2, 0), rot=90, ciclo=19, inclina=3, seed=4 + k, arranque=0.0, freia=0.25)
    pega(lan, REG["g0"], "F")
    camera(N, [(1, (-17.3, 5.6, 0.16), (-18.8, 6.5, 0.18), 18, (-18.5, 6.2, 0.15), 2.8),
               (int(N * 0.6), (-17.35, 5.55, 0.15), (-18.9, 6.5, 0.2), 18, (-19.4, 6.5, 0.15), 2.8),
               (N, (-17.4, 5.5, 0.15), (-19.0, 6.5, 0.28), 18, (-19.6, 6.5, 0.3), 2.8)], mao=0.5)


@acao("5D")
def a5D(N):
    """a lanterna chega na cara dele (clarão), o vulto de pano se inclina sobre ele, a imagem pisca e escurece (o fecho em íris vai no pós)"""
    prepara("5D")
    n = REG["eu"]
    cara(n, N, [(1, dict(boca="o", lid=1.15)), (N, dict(boca="o", lid=1.2))], piscar=False)
    lan = O("lant"); g0, g1 = REG["g0"], REG["g1"]
    g0.raiz.location = (-19.7, 6.8, 0); g1.raiz.location = (-19.9, 5.9, 0)
    for h in (g0, g1):
        h.raiz.rotation_euler.z = math.radians(90)
    mov_h(g0, N, [(8, dict(tronco=28, cabeca=14)), (N, dict(tronco=48, cabeca=22, ver=(-18.5, 6.5), dpos=(0.35, -0.1, 0)))], vida=0.6, seed=3)
    mov_h(g1, N, [(10, dict(tronco=10)), (N, dict(tronco=30, cabeca=10, dpos=(0.2, 0.1, 0)))], vida=0.6, seed=4)
    pega(lan, g0, "F")
    camera(N, [(1, (-17.3, 5.6, 0.16), (-18.8, 6.5, 0.2), 18, (-19.6, 6.8, 0.5), 2.8),
               (int(N * 0.5), (-17.3, 5.6, 0.17), (-18.9, 6.5, 0.3), 18, (-19.5, 6.7, 0.6), 2.4),
               (N, (-17.3, 5.6, 0.17), (-18.8, 6.4, 0.35), 18, (-19.4, 6.7, 0.7), 2.0)], mao=0.5)


# ---------------------------------------------------------------- galpão: o que vale para todos os planos de dentro
def grupo():
    return [h for n, h in REG.items() if n.startswith("g_") or n in O2.GRUPO]


def fogo_vivo(N, seed=2):
    """as chamas do tambor tremem (escala em z, cada uma no seu ritmo): o fogo nunca fica parado"""
    rnd = random.Random(seed)
    for o in bpy.data.objects:
        if o.name.startswith("tambor_ch"):
            s0 = tuple(o.scale); ph = rnd.uniform(0, 6.28); fr = rnd.uniform(0.35, 0.6)
            for f in range(1, N + 1):
                a = 1.0 + 0.22 * math.sin(f * fr + ph) + 0.12 * math.sin(f * fr * 2.3 + ph * 1.7)
                o.scale = (s0[0] * (1 + 0.1 * math.sin(f * 0.8 + ph)), s0[1], s0[2] * a); key(o, "scale", f, "LINEAR")


def mira_mao(h, lado, ponto, base=None):
    """pose do braço 'lado' com a mão no ponto do mundo (cinemática inversa, pelo estado atual do boneco)"""
    import ik3_abrigo as IK
    b = dict(base if base is not None else getattr(h, "_P", {}))
    return IK.braco_pose(h, lado, ponto, b, aviso=0.08)


def pov_para(cam=None):
    """as mãos de primeira pessoa do builder ficam presas à câmera nova (a do builder não renderiza)"""
    cam = cam or bpy.context.scene.camera
    for r in POV:
        root = r[0] if isinstance(r, (tuple, list)) else r
        root.parent = cam; root.matrix_parent_inverse = root.matrix_parent_inverse.__class__()
    return POV


def centra(o):
    """põe a origem de uma malha no centro dela (para escalar e girar sobre si mesma, não sobre a origem do mundo)"""
    from mathutils import Matrix
    if o is None or o.type != "MESH":
        return o
    vs = [Vector(v.co) for v in o.data.vertices]
    c = sum(vs, Vector()) / max(1, len(vs))
    o.data.transform(Matrix.Translation(-c))
    o.location = o.location + c
    return o


def vento(N, n=8, de=(-4.0, 2.0, 0.3), ate=(4.0, 2.0, 1.2), caixa=(3.0, 3.0, 1.2), seed=1, tam=0.12, cor="#d8d2bc", prefixo="papel"):
    """folhas de papel arrastadas pelo vento: cada uma segue o vetor de->ate com a sua fase, balança e gira"""
    rnd = random.Random(seed)
    d = Vector(ate) - Vector(de)
    for k in range(n):
        o0 = Vector((rnd.uniform(-caixa[0], caixa[0]), rnd.uniform(-caixa[1], caixa[1]), rnd.uniform(0, caixa[2])))
        ob = O3.caixa(f"{prefixo}{k}_{seed}", (tam, tam * 0.7, 0.004), O3.M(cor, "#a8a290"), None, tuple(Vector(de) + o0), chanfro=0.0, contorno=0.0)
        ob = O(f"{prefixo}{k}_{seed}") or ob
        ph = rnd.uniform(0, 6.28); w = rnd.uniform(0.7, 1.3)
        for f in range(1, N + 1):
            u = (f - 1) / max(1, N - 1) * w
            ob.location = tuple(Vector(de) + o0 + d * u + Vector((0.0, 0.2 * math.sin(f * 0.3 + ph), 0.15 * math.sin(f * 0.37 + ph * 1.3) + 0.1)))
            ob.rotation_euler = (f * 0.21 + ph, f * 0.17, f * 0.13 + ph)
            key(ob, "location", f, "LINEAR"); key(ob, "rotation_euler", f, "LINEAR")


def poeira_cai(N, x=(-1.0, 1.0), y=(0.0, 1.0), z=(0.5, 3.0), n=14, seed=1, vel=0.35, tam=0.008, cor="#d8d0b8", prefixo="cai"):
    """grãos de poeira que descem devagar (um por um, cada um no seu ritmo)"""
    rnd = random.Random(seed)
    for k in range(n):
        x0, y0 = rnd.uniform(*x), rnd.uniform(*y); z0 = rnd.uniform(z[0], z[1]); v = vel * rnd.uniform(0.6, 1.4)
        ob = O2.esfera(f"{prefixo}{k}_{seed}", tam, tam, tam, O3.brilha(cor, 1.2), None, (x0, y0, z0), contorno=0.0, seg=8, an=6)
        ob = O(f"{prefixo}{k}_{seed}") or ob
        ph = rnd.uniform(0, 6.28)
        for f in range(1, N + 1):
            zz = z0 - v * (f - 1) / FPS
            if zz < z[0] - 0.3:
                zz = z[1] - (z[0] - 0.3 - zz) % (z[1] - z[0] + 0.3)
            ob.location = (x0 + 0.02 * math.sin(f * 0.2 + ph), y0, zz); key(ob, "location", f, "LINEAR")


def figurante(chave, de, ate, N, f0=1, f1=None, ciclo=19, nome=None, rot=None, seed=5):
    """alguém do grupo atravessa o fundo andando (cria o boneco e a caminhada)"""
    h = O2.faz_grupo(chave, nome or ("fig_" + chave))
    h.raiz.location = tuple(de)
    h.pose(ombro=(-4, 4), cotovelo=(-12, -12), abre=(6, 6)); h.rosto(boca="reta", lid=0.3)
    anda(h, N, de, ate, f0=f0, f1=f1, ciclo=ciclo, inclina=2, seed=seed, arranque=0.1, freia=0.1, rot=rot)
    return h


def gosma_dedos(prefixo, N, k0=0.5, k1=1.0, n=5, cai=0.12):
    """as pontas dos dedos viram gosma: os blobs crescem (cada um sobre o próprio centro) e os pingos descem em ciclo"""
    for j in range(n):
        for nome in (f"{prefixo}gd{j}", f"{prefixo}_gd{j}"):
            g = O(nome)
            if g is not None:
                centra(g)
                trilha(g, N, esc=[(1, (1.0, 1.0, 1.0)), (N, (1.0 + (k1 - k0) * 1.2, 1.0 + (k1 - k0) * 1.2, 1.0 + (k1 - k0) * 2.4))])
        for nome in (f"{prefixo}pg{j}", f"{prefixo}_pg{j}"):
            p = O(nome)
            if p is not None:
                l0 = Vector(p.location); per = 14 + 3 * j
                for f in range(1, N + 1):
                    u = ((f + 2 * j) % per) / per
                    p.location = (l0.x, l0.y, l0.z - cai * u); key(p, "location", f, "LINEAR")
                    p.scale = (1, 1, 0.4 + 1.4 * u); key(p, "scale", f, "LINEAR")


try:
    import acoes_abrigo2c  # noqa  (6 e 7)
    import acoes_abrigo2d  # noqa  (8 a 12)
    import acoes_abrigo2e  # noqa  (13 a 17)
except ImportError as e:
    print("acoes_abrigo2 (c/d/e):", e)
