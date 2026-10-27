"""O herói de frente de verdade (view="front"): braços espelhados e a pose sentada vista de frente.
A Timeline grava os membros como se fosse de perfil; aqui, depois do bake, os braços e as pernas são regravados
quadro a quadro. Sentado de frente: a coxa aponta para a câmera (fica curta), aparecem o colo e os joelhos, a canela desce reta."""
import math
from lib import key
from char2d import rrect, ellipse


def bracos(H, f0, f1, keys, extras=()):
    """keys = [(quadro, dict(shF, elF, wrF, shB, elB, wrB))]; ângulo + = o braço abre para fora do corpo.
    Os ângulos seguem uma spline contínua pelas chaves (curvas.spline): sem parar em cada pose.
    extras = [(quadro, canal, amplitude em graus, freq, zeta)]: mola amortecida somada a partir do quadro (ação sobreposta,
    ex.: a mão afunda quando o fuzil bate e volta passando do ponto)."""
    import curvas
    J = H.j
    canais = ("shF", "elF", "wrF", "shB", "elB", "wrB")
    for f in range(f0, f1 + 1):
        for s_, sg in (("F", 1), ("B", -1)):
            for j in ("sh", "el", "wr"):
                c = j + s_
                pts = [(fk, d.get(c, 0.0)) for fk, d in keys]
                a = curvas.spline(pts, f)
                for fe, ce, amp, fr, ze in extras:
                    if ce == c and f > fe:
                        a += amp * curvas.pancada((f - fe) / 24.0, fr, ze)
                if j == "el" and abs(a) < 4.0:
                    # cotovelo nunca 100% reto: com ombro, cotovelo e punho em linha, o arredondado do braço (limbs.rubber_limb)
                    # perde a direção em alguns quadros, o antebraço dobra para dentro e a mão some (presidente v5)
                    a = 4.0 if a >= 0 else -4.0
                J[c].rotation_euler = (0, -sg * math.radians(a), 0); key(J[c], "rotation_euler", f, "LINEAR")


def sentado(H, f0, f1, seat=0.64, coxa=0.21, abre=22.0, respira=0.004):   # coxa à mostra, na proporção dos braços
    """senta de frente (sem animação de sentar: já está sentado). Devolve as peças do colo para quem quiser escondê-las."""
    J = H.j
    for f in range(f0, f1 + 1):
        J["hips"].location.z = seat + respira * math.sin(f / 24.0 * 2 * math.pi / 3.2); key(J["hips"], "location", f, "BEZIER")
        for s, sg in (("F", 1), ("B", -1)):
            J["kn" + s].location = (0, 0, -coxa); key(J["kn" + s], "location", f, "BEZIER")
            J["hip" + s].rotation_euler = (0, -sg * math.radians(abre), 0); key(J["hip" + s], "rotation_euler", f, "BEZIER")
            J["kn" + s].rotation_euler = (0, sg * math.radians(abre), 0); key(J["kn" + s], "rotation_euler", f, "BEZIER")
            J["an" + s].rotation_euler = (0, 0, 0); key(J["an" + s], "rotation_euler", f, "BEZIER")
    L = H._layers()
    return [H.P("colo", rrect(-0.14, -0.075, 0.14, 0.03, 0.05, 6), "pants", J["hips"], L["legF"] + 0.45, rimw=0.008)]   # sem bolas nos joelhos (o usuário achou estranho)