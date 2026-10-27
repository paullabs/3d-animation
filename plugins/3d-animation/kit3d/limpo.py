"""Palco limpo (estilo IfverseTales): parede e chão numa cor só, escuros e dessaturados, uma luz única
(cone de cima) com poça no chão e poeira no ar. O fundo fica quase vazio e desfocado; a cor saturada
fica só no personagem e num destaque. Tudo continua chapado; a câmera só desliza."""
import bpy, math, random
import lib
from lib import srgb, key, empty
import cena, sets, props

PALCOS = {
    "noite":  dict(top="#070a12", mid="#18203a", bottom="#0b0f1c", floor="#090c16", pool="#2b3758", spot="#cfe0ff", rim="#9fc4ff", shadow="#03050a", hint="#141b30"),
    "grafite": dict(top="#0b0b0e", mid="#26262d", bottom="#121216", floor="#0d0d10", pool="#3b3a3c", spot="#fff1dc", rim="#ffd7b0", shadow="#050506", hint="#1e1e24"),
    "quente": dict(top="#0e0907", mid="#38281f", bottom="#1a120e", floor="#120c09", pool="#4e3727", spot="#ffd6a3", rim="#ffb27a", shadow="#070403", hint="#2a1e17"),
    "roxo":   dict(top="#09070f", mid="#2a2142", bottom="#120e1e", floor="#0d0a16", pool="#3d3260", spot="#e6dcff", rim="#c9b6ff", shadow="#05030a", hint="#201a34"),
}


def P_de(nome):
    """paleta no formato que o resto do kit espera (rim, shadow, dust, mist...)"""
    p = PALCOS[nome]
    return dict(rim=p["rim"], shadow=p["shadow"], dust="#ffffff", mist=p["mid"], shaft=p["spot"], haze=p["bottom"],
                horizon=p["mid"], sky_mid=p["bottom"], sky_top=p["top"], fg="#020306", ground=p["floor"], walk=p["floor"], curb=p["hint"])


def palco(nome="noite", wall_y=2.6, spot_x=0.0, spot_w=1.3, frames=2000, chao=True, poeira=60, x_range=(-4, 4), janela=None,
          linhas=True, spot=True):
    """monta o palco: parede (degradê vertical de uma cor), chão escuro com poça de luz, cone de luz de cima, poeira.
    janela = (x0, x1, z0, z1) desenha um recorte de janela bem apagado na parede (opcional)."""
    p = PALCOS[nome]
    sc = bpy.context.scene
    sc.world.node_tree.nodes["Background"].inputs[0].default_value = (*srgb(p["top"]), 1)
    sc.world.node_tree.nodes["Background"].inputs[1].default_value = 1.0
    sets.FOG.update(color=p["bottom"], near=8.0, far=60.0, max=0.3)
    props.skywall("palco_parede", wall_y, [(-1.0, p["bottom"]), (0.6, p["bottom"]), (2.0, p["mid"]), (3.4, p["mid"]), (5.5, p["top"])], -30, 30, -2.0, 12.0)
    if linhas:                                   # duas juntas de parede quase invisíveis (só para a parede "existir")
        for z in (1.15, 2.85):
            props.poly(f"palco_junta{z}", cena.rect(-30, z - 0.008, 30, z + 0.008), p["hint"], wall_y - 0.01)
    if janela:
        x0, x1, z0, z1 = janela
        props.poly("palco_janela", cena.rect(x0, z0, x1, z1), p["hint"], wall_y - 0.02)
        props.poly("palco_janela_luz", cena.rect(x0 + 0.05, z0 + 0.05, x1 - 0.05, z1 - 0.05), props._mix(p["mid"], p["spot"], 0.18), wall_y - 0.03)
    if chao:
        cena.poly_mesh("palco_chao", [(-60, -12, -0.004), (60, -12, -0.004), (60, wall_y, -0.004), (-60, wall_y, -0.004)], props.FM(p["floor"]))
        cena.ground_disc("palco_poca", spot_w * 1.25, spot_w * 0.7, cena.amat("palco_poca_m", p["pool"], 1.0, 0.85, ("radial", 1.4)), (spot_x, 0.2, 0.003), n=64)
    if spot:
        cone = cena.poly_mesh("palco_cone", [(-1, 0, 0), (1, 0, 0), (0.22, 0, 1), (-0.22, 0, 1)], cena.amat("palco_cone_m", p["spot"], 1.0, 0.1, ("shaft", 1.3, 0.85)))
        cone.location = (spot_x, 0.9, 0.0); cone.scale = (spot_w, 1, 6.5)
        sets.glow("palco_spot_g", p["spot"], 2.2, (spot_x, wall_y - 0.1, 2.6), power=2.6, strength=0.25)
    if poeira:
        cena.dust(dict(dust="#ffffff"), poeira, (spot_x - spot_w, spot_x + spot_w), frames, size=(0.004, 0.011), z_range=(0.3, 3.2), y_range=(-1.2, 1.4), alpha=0.5)
    return p


def silhueta(name, x, y, P, h=1.0, flip=1, cor="#1a1f2e", z=0.0):
    """pessoa escura com borda de luz (como os figurantes do IfverseTales): forma única, sem rosto"""
    return props.pessoa(name, x, y, cor, h, flip=flip, P=P, z=z)


# ---------------------------------------------------------------- estúdio para o objeto em foco (inserto)
ESTUDIOS = {   # fundo (borda, centro), mesa, luz. A cor do fundo é a oposta à do objeto.
    "cofre": dict(edge="#120c09", center="#4a3324", table="#1d140f", table_hi="#3a281c", light="#ffd9a8"),   # dinheiro azul
    "papel": dict(edge="#8d877d", center="#ece6dc", table="#b8b0a3", table_hi="#d8d1c4", light="#ffffff"),   # objeto escuro
    "aco":   dict(edge="#07090f", center="#26324a", table="#0d121c", table_hi="#1f2a40", light="#dfe9ff"),   # objeto claro/quente
}


def estudio(nome="cofre", cx=0.0, cz=1.0, raio=2.2, table_z=None, wall_y=1.2, frames=2000, poeira=30):
    """fundo infinito liso para um objeto: degradê radial atrás do objeto (cx, cz), quase preto nas bordas,
    tampo de mesa opcional (table_z) e um cone de luz de cima. Nada mais em cena."""
    e = ESTUDIOS[nome]
    sc = bpy.context.scene
    sc.world.node_tree.nodes["Background"].inputs[0].default_value = (*srgb(e["edge"]), 1)
    cena.poly_mesh("est_fundo", [(-60, wall_y + 0.5, -40), (60, wall_y + 0.5, -40), (60, wall_y + 0.5, 60), (-60, wall_y + 0.5, 60)], props.FM(e["edge"]))
    cena.disc("est_halo", raio, cena.amat("est_halo_m", e["center"], 1.0, 1.0, ("radial", 1.6)), (cx, wall_y, cz), n=72)
    if table_z is not None:
        cena.poly_mesh("est_mesa", [(-30, -8, table_z), (30, -8, table_z), (30, wall_y, table_z), (-30, wall_y, table_z)], props.FM(e["table"]))
        cena.ground_disc("est_mesa_luz", raio * 0.9, 0.9, cena.amat("est_mesa_luz_m", e["table_hi"], 1.0, 0.9, ("radial", 1.5)), (cx, 0.15, table_z + 0.002), n=64)
        props.poly("est_mesa_borda", cena.rect(-30, table_z - 0.01, 30, table_z + 0.004), e["table_hi"], wall_y - 0.02)
    cone = cena.poly_mesh("est_cone", [(-1, 0, 0), (1, 0, 0), (0.18, 0, 1), (-0.18, 0, 1)], cena.amat("est_cone_m", e["light"], 1.0, 0.07, ("shaft", 1.4, 0.8)))
    cone.location = (cx, wall_y - 0.3, (table_z if table_z is not None else cz - raio * 0.6)); cone.scale = (raio * 0.75, 1, raio * 2.2)
    if poeira:
        cena.dust(dict(dust="#ffffff"), poeira, (cx - raio * 0.6, cx + raio * 0.6), frames, size=(0.003, 0.008),
                  z_range=(cz - raio * 0.4, cz + raio * 0.9), y_range=(-0.6, wall_y - 0.2), alpha=0.4)
    return e


# ---------------------------------------------------------------- vários enquadramentos na mesma cena
def cortes(c, planos):
    """planos = [(t_inicio, keys, opções)], keys = [(t, (x, y, z))] em segundos; opções: lens, focus, fstop, dof, shift.
    Cria uma câmera por plano e troca na hora do corte (marcadores da linha do tempo). A câmera só desliza.
    Devolve a lista de (câmera, rig) na ordem dos planos."""
    sc = c["sc"]; F = c["F"]
    out = []
    for i, (t0, keys, op) in enumerate(planos):
        cam = cena.camera(sc, [(F(t), p) for t, p in keys], lens=op.get("lens", 35), focus=op.get("focus", 3.0), fstop=op.get("fstop", 0.9))
        cam.name = f"cam{i}"
        cam.data.dof.use_dof = op.get("dof", True)
        cam.data.shift_x, cam.data.shift_y = op.get("shift", (0.0, 0.0))
        if op.get("interp"):
            lib.all_interp(cam, op["interp"])
        rig = empty(f"camrig{i}"); cam.parent = rig
        m = sc.timeline_markers.new(f"corte{i}", frame=F(t0)); m.camera = cam
        out.append((cam, rig))
    sc.camera = out[0][0]
    return out
