"""Curvas de movimento no estilo do editor de gráficos do After Effects: o progresso s(u) de 0 a 1 vem de uma
bezier cúbica (x1, y1, x2, y2), como o "cubic-bezier" do CSS. x1/x2 altos = mais "influência" (sai e chega mais devagar)."""

CURVAS = {
    "easy":    ((0.60, 0.00, 0.40, 1.00), "S suave: sai devagar, acelera no meio, assenta"),
    "impacto": ((0.70, 0.00, 0.85, 0.70), "sai devagar e o impacto vem perto do fim (entra correndo na próxima cena)"),
    "onda":    ((0.85, 0.00, 0.15, 1.00), "S forte (influência 85%): quase parado, onda rápida no meio, assenta longo"),
    "queda":   ((0.55, 0.00, 0.90, 0.55), "ease-in de queda: sai devagar e chega rápido, sem parar no fim"),
}


def bezier(u, x1, y1, x2, y2):
    """s(u) da bezier cúbica com pontas (0,0) e (1,1); resolve x(t) = u por bissecção"""
    if u <= 0:
        return 0.0
    if u >= 1:
        return 1.0
    bx = lambda t: 3 * (1 - t) ** 2 * t * x1 + 3 * (1 - t) * t ** 2 * x2 + t ** 3
    by = lambda t: 3 * (1 - t) ** 2 * t * y1 + 3 * (1 - t) * t ** 2 * y2 + t ** 3
    lo, hi = 0.0, 1.0
    for _ in range(40):
        mid = (lo + hi) / 2
        if bx(mid) < u:
            lo = mid
        else:
            hi = mid
    return by((lo + hi) / 2)


def s(nome, u):
    return bezier(u, *CURVAS[nome][0])


import math


def mola(t, freq=3.0, zeta=0.28):
    """resposta ao degrau de uma mola amortecida (t em s): 0 -> passa de 1 -> oscila -> assenta em 1. É a "onda" do AE"""
    if t <= 0:
        return 0.0
    w = 2 * math.pi * freq; wd = w * math.sqrt(1 - zeta * zeta)
    return 1 - math.exp(-zeta * w * t) * (math.cos(wd * t) + zeta * w / wd * math.sin(wd * t))


def pancada(t, freq=2.8, zeta=0.28):
    """deslocamento de uma mola atingida por um impacto (t em s), normalizado para o primeiro pico valer 1:
    afunda até 1, volta passando de 0 (~ -0,5), oscila e assenta em 0."""
    if t <= 0:
        return 0.0
    w = 2 * math.pi * freq; wd = w * math.sqrt(1 - zeta * zeta)
    tp = math.atan2(wd, zeta * w) / wd
    pico = math.exp(-zeta * w * tp) * math.sin(wd * tp)
    return math.exp(-zeta * w * t) * math.sin(wd * t) / pico


def spline(pontos, f, tens=1.0):
    """interpola [(quadro, valor)] com Catmull-Rom: a velocidade é contínua nas chaves (nada para a cada pose).
    As pontas começam e terminam com velocidade zero."""
    ks = sorted(pontos)
    if f <= ks[0][0]:
        return ks[0][1]
    if f >= ks[-1][0]:
        return ks[-1][1]
    n = len(ks)
    for i in range(n - 1):
        fa, pa = ks[i]; fb, pb = ks[i + 1]
        if fa <= f <= fb:
            def tang(j):
                if j == 0 or j == n - 1:
                    return 0.0
                return tens * (ks[j + 1][1] - ks[j - 1][1]) / (ks[j + 1][0] - ks[j - 1][0])
            dt = fb - fa; u = (f - fa) / dt
            h00 = 2 * u ** 3 - 3 * u ** 2 + 1; h10 = u ** 3 - 2 * u ** 2 + u; h01 = -2 * u ** 3 + 3 * u ** 2; h11 = u ** 3 - u ** 2
            return h00 * pa + h10 * dt * tang(i) + h01 * pb + h11 * dt * tang(i + 1)
    return ks[-1][1]
