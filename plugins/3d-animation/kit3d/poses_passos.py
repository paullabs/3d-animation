"""As poses do "eu" para "E se cada passo dobrasse a sua altura?" (ficha de poses, plano de cena v2).
Convenção do Heroi3D (graus): ombro/quadril negativos = para a frente; joelho positivo = dobra (canela para trás); cotovelo negativo = dobra para a frente;
tornozelo positivo = ponta do pé para baixo (pé chapado quando quadril + joelho + tornozelo = 0); tronco e cabeça positivos = para a frente/para baixo;
abre = braço para fora; giro = torção do tronco; olha = cabeça para o lado.
Regras (pedido de 25/10/2026, "trabalhar melhor as articulações"): joelho de 5 a 120 graus e nunca travado reto; cotovelo no mínimo 4 graus;
no passo, ombro e quadril em sentidos opostos e o peso em cima do pé de apoio; a mão que toca alguma coisa vai até o ponto por IK."""
import math
import bpy
from mathutils import Vector
import ik3_abrigo as IK


def _pe(q, j, total):
    """ângulo do tornozelo para o pé ficar com 'total' graus em relação ao chão (0 = chapado; + = ponta para baixo)"""
    return total - (q + j)


POSES = {
    # o passo em quatro fases (perna F à frente)
    "contato": dict(quadril=(-28, 20), joelho=(5, 14), tornozelo=(_pe(-28, 5, -12), _pe(20, 14, 32)),
                    ombro=(20, -22), cotovelo=(-12, -26), abre=(6, 6), tronco=-2, giro=-7, cabeca=-2),
    "descida": dict(quadril=(-18, 24), joelho=(22, 30), tornozelo=(_pe(-18, 22, 0), _pe(24, 30, 38)),
                    ombro=(14, -16), cotovelo=(-14, -24), abre=(6, 6), tronco=3, giro=-5, cabeca=2),
    "passagem": dict(quadril=(2, -14), joelho=(6, 50), tornozelo=(_pe(2, 6, 0), _pe(-14, 50, 18)),
                     ombro=(3, -4), cotovelo=(-14, -16), abre=(6, 6), tronco=1, giro=0, cabeca=0),
    "subida": dict(quadril=(16, -30), joelho=(6, 24), tornozelo=(_pe(16, 6, 26), _pe(-30, 24, -8)),
                   ombro=(-18, 18), cotovelo=(-22, -12), abre=(6, 6), tronco=-1, giro=6, cabeca=-2),
    # o tropeço: a ponta do pé de trás presa, o tronco vai à frente e os braços abrem de contrapeso
    "tropeco": dict(quadril=(28, -42), joelho=(36, 34), tornozelo=(_pe(28, 36, 60), _pe(-42, 34, -6)),
                    ombro=(-62, -84), cotovelo=(-26, -18), abre=(34, 28), tronco=26, giro=-8, cabeca=-14, boca="o"),
    # a queda (o corpo inteiro gira em volta dos pés: rot_x) e as mãos chegando ao chão
    "queda1": dict(quadril=(12, -16), joelho=(18, 26), tornozelo=(10, 0), ombro=(-82, -96), cotovelo=(-22, -16), abre=(22, 18),
                   tronco=6, cabeca=-16, rot_x=24, boca="o"),
    "queda2": dict(quadril=(14, 4), joelho=(26, 14), tornozelo=(20, 16), ombro=(-118, -126), cotovelo=(-14, -10), abre=(16, 14),
                   tronco=2, cabeca=-24, rot_x=50, boca="o"),
    "queda3": dict(quadril=(6, 10), joelho=(14, 22), tornozelo=(30, 26), ombro=(-110, -110), cotovelo=(-8, -8), abre=(12, 12),
                   tronco=0, cabeca=-26, rot_x=68, maos_no_chao=True, boca="o"),
    # apoio: agachado depois da queda, as duas mãos no chão e um joelho quase encostando
    "apoio": dict(quadril=(-96, 34), joelho=(118, 112), tornozelo=(_pe(-96, 118, 0), _pe(34, 112, 70)),
                  ombro=(-40, -40), cotovelo=(-8, -8), abre=(10, 10), tronco=48, cabeca=-30, maos_no_chao=True),
    # levantar: um pé à frente, a mão no joelho
    "levanta": dict(quadril=(-74, 22), joelho=(84, 64), tornozelo=(_pe(-74, 84, 0), _pe(22, 64, 58)),
                    ombro=(-30, 8), cotovelo=(-30, -16), abre=(8, 8), tronco=30, cabeca=-10, mao_no_joelho=True),
    # grito para baixo: cabeça baixa, mãos em concha em volta da boca
    "grito": dict(quadril=(-6, 6), joelho=(6, 8), tornozelo=(0, -14), ombro=(-40, -40), cotovelo=(-110, -110), abre=(30, 30),
                  tronco=10, cabeca=6, boca="o", maos_na_boca=True),
    # respiração funda: peito para cima, ombros subindo, a mão no peito
    "respira": dict(quadril=(-4, 4), joelho=(6, 6), tornozelo=(-2, -10), ombro=(-10, 6), cotovelo=(-90, -12), abre=(10, 8),
                    tronco=-7, cabeca=-12, boca="o", mao_no_peito=True),
    # olhares e o braço esticado
    "olha_baixo": dict(quadril=(-4, 4), joelho=(6, 6), tornozelo=(-2, -10), ombro=(-4, 6), cotovelo=(-14, -12), abre=(6, 6),
                       tronco=10, cabeca=34),
    "olha_lado": dict(quadril=(-4, 4), joelho=(6, 6), tornozelo=(-2, -10), ombro=(-4, 6), cotovelo=(-14, -12), abre=(6, 6),
                      tronco=-3, cabeca=-14, olha=48, giro=10),
    "estica": dict(quadril=(-8, 8), joelho=(8, 10), tornozelo=(0, -18), ombro=(-80, 8), cotovelo=(-8, -14), abre=(14, 6),
                   tronco=4, cabeca=-6, olha=-14, giro=-8, alvo_mao=(-0.34, -0.44, 1.46)),
}

ORDEM = ["contato", "descida", "passagem", "subida", "tropeco", "queda1", "queda2", "queda3", "apoio", "levanta",
         "grito", "respira", "olha_baixo", "olha_lado", "estica"]
NOMES = {"contato": "passo: contato", "descida": "passo: descida", "passagem": "passo: passagem", "subida": "passo: subida",
         "tropeco": "tropeço", "queda1": "queda: começo", "queda2": "queda: meio", "queda3": "queda: mãos chegando",
         "apoio": "apoio no chão", "levanta": "levantar", "grito": "grito para baixo", "respira": "respiração funda",
         "olha_baixo": "olhar para baixo", "olha_lado": "olhar para o lado", "estica": "esticar a mão"}


def assenta(h, z0=0.0):
    """põe a raiz para o ponto mais baixo dos sapatos (sola e bico) ficar em z0: com o pé em ponta ou em calcanhar o bico entrava no chão"""
    bpy.context.view_layer.update()
    zs = []
    for o in [h.raiz] + list(h.raiz.children_recursive):
        if o.type == "MESH" and ("sapato" in o.name or "sola" in o.name):
            mw = o.matrix_world
            zs += [(mw @ v.co).z for v in o.data.vertices]
    if zs:
        h.raiz.location.z += z0 - min(zs)
        bpy.context.view_layer.update()


def aplica(h, nome, escala=1.0):
    """põe a pose 'nome' no boneco h (raiz no chão, de frente para -y); devolve o dict usado"""
    P = dict(POSES[nome])
    extra = {k: P.pop(k) for k in ("rot_x", "maos_no_chao", "boca", "mao_no_joelho", "maos_na_boca", "mao_no_peito", "alvo_mao") if k in P}
    P = h.pe_no_chao(**P)
    h.pose(**P)
    if extra.get("rot_x"):
        h.raiz.rotation_euler.x = math.radians(extra["rot_x"])
        bpy.context.view_layer.update()
        zmin = min(h.tornozelo[s].matrix_world.translation.z for s in "FB")
        h.raiz.location.z += max(0.0, 0.07 * escala - zmin)                 # os pés não afundam no chão quando o corpo gira
    bpy.context.view_layer.update()
    if extra.get("maos_no_chao"):
        for s, sx in (("F", -1), ("B", 1)):
            o = h.ombro[s].matrix_world.translation
            alvo = (o.x + sx * 0.06 * escala, o.y - 0.06 * escala, 0.045 * escala)
            P = IK.braco_pose(h, s, alvo, P, nome=f"{nome}.{s}")
            h.pose(**P); bpy.context.view_layer.update()
            h.espalma(s)
    if extra.get("mao_no_joelho"):
        k = h.joelho["F"].matrix_world.translation
        P = IK.braco_pose(h, "F", (k.x - 0.02 * escala, k.y - 0.05 * escala, k.z + 0.04 * escala), P, nome=f"{nome}.F")
        h.pose(**P); bpy.context.view_layer.update()
    if extra.get("maos_na_boca"):
        b = IK.boca_de(h)
        for s, sx in (("F", -1), ("B", 1)):
            P = IK.braco_pose(h, s, (b.x + sx * 0.085 * escala, b.y - 0.02 * escala, b.z), P, nome=f"{nome}.{s}")
            h.pose(**P); bpy.context.view_layer.update()
    if extra.get("mao_no_peito"):
        t = h.tronco.matrix_world
        alvo = t @ Vector((0.04, -0.125, 0.3))
        P = IK.braco_pose(h, "F", tuple(alvo), P, nome=f"{nome}.F")
        h.pose(**P); bpy.context.view_layer.update()
        h.espalma("F")
    if extra.get("alvo_mao"):
        a = Vector(extra["alvo_mao"]) * escala + h.raiz.location
        P = IK.braco_pose(h, "F", tuple(a), P, nome=f"{nome}.F")
        h.pose(**P); bpy.context.view_layer.update()
        h.espalma("F")
    h.rosto(boca=extra.get("boca", "reta"), lid=0.0)
    if not extra.get("rot_x") and not extra.get("maos_no_chao"):
        assenta(h, 0.0)
    return P
