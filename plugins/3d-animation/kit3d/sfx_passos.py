"""Efeitos sonoros sintetizados de "os passos" (pedido de 26/10/2026: "faz o som, trilha e um efeito por ação"). Só numpy, sem custo, no mesmo timbre do abrigo
(reaproveita os auxiliares de sfx_abrigo). Cada função devolve um estéreo float (48 kHz); python3 sfx_passos.py PASTA grava todos.
Ideia: a PISADA cresce com o passo (grave cada vez mais fundo e cauda cada vez mais longa); a medida é um tique de vidro que sobe de tom; o espaço é quase mudo,
só um zumbido grave. Pegada precisa de médio (tapa de ar de 700 Hz a 5 kHz e corpo de 140 a 70 Hz), porque o grave puro some em caixa de celular."""
import os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sfx_abrigo as SX
from sfx_abrigo import SR, _n, _t, _rng, _ruido, _bp, _env, _est, _norm, _reverb, grava


def pisada(n=1, dur=None, seed=0):
    """o pé enorme pisa: estalo de asfalto + tapa de ar + corpo + sub que desce; n = o número do passo (1 a 28): quanto maior, mais fundo e mais longa a cauda"""
    dur = dur or min(3.2, 1.1 + 0.07 * n)
    N = _n(dur); t = _t(dur); r = _rng(seed)
    f_fim = max(24.0, 78.0 * 0.9 ** n)
    f0 = f_fim + 70.0
    fase = np.cumsum(f_fim + (f0 - f_fim) * np.exp(-t * 9.0)) / SR
    sub = np.sin(2 * np.pi * fase) * np.exp(-t * (3.2 / (1 + 0.04 * n))) * 0.95
    corpo = np.sin(2 * np.pi * np.cumsum(70 + 85 * np.exp(-t * 30)) / SR) * np.exp(-t * 14) * 0.75
    tapa = _bp(_ruido(dur, seed), 700, 5200) * np.exp(-t * 55) * 0.8
    estalo = _bp(_ruido(dur, seed + 1), 2200, 9000) * np.exp(-t * 160) * 0.45
    areia = _bp(_ruido(dur, seed + 2), 250, 1800) * np.exp(-t * (7.0 / (1 + 0.1 * n))) * 0.28
    m = (sub + corpo + tapa + estalo + areia) * np.minimum(1, t / 0.003)
    m = np.tanh(m * 1.3)
    s = _est(m, 0.4 + 0.02 * n, 0.0)
    return _norm(_reverb(s, rt=min(2.6, 0.5 + 0.08 * n), mix=min(0.45, 0.12 + 0.012 * n), seed=5 + n), 0.9)[:N + _n(min(2.6, 0.5 + 0.08 * n))]


def crescer(dur=0.55, seed=0, grave=1.0):
    """o corpo dobra de tamanho: um 'uuum' que sobe de tom em curva de entrada e saída, com o ar empurrado; termina num pop leve"""
    t = _t(dur); u = np.clip(t / dur, 0, 1); cur = u * u * (3 - 2 * u)
    f = (110 / grave) * (1 + 2.6 * cur)
    tom = np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.6 + np.sin(2 * np.pi * np.cumsum(f * 2.01) / SR) * 0.2
    ar = _bp(_ruido(dur, seed), 300, 1600 + 3000 * cur) * (0.25 + 0.5 * cur)
    env = np.sin(np.pi * np.clip(u * 0.96, 0, 1)) ** 0.7
    m = (tom + ar) * env
    pop = np.zeros_like(m); k = int(0.04 * SR)
    pop[-k:] = _bp(_ruido(0.04, seed + 3), 600, 3500)[:k] * np.exp(-np.arange(k) / SR * 90) * 0.5
    return _norm(_est(m + pop, 0.4), 0.55)


def ping(f=1500.0, dur=0.32, seed=0):
    """o tique de vidro de uma caixa de medida que acende: dois parciais e um clique; f varia para nenhum se repetir"""
    t = _t(dur)
    m = (np.sin(2 * np.pi * f * t) * 0.7 + np.sin(2 * np.pi * f * 2.76 * t) * 0.22 + np.sin(2 * np.pi * f * 5.4 * t) * 0.08) * np.exp(-t * 17)
    m += _bp(_ruido(dur, seed), 3000, 9000) * np.exp(-t * 300) * 0.25
    return _norm(_est(m, 0.2, 0.0), 0.5)


def fita(dur=1.2, seed=0, ritmo0=16.0, ritmo1=26.0):
    """a fita métrica sendo puxada e subindo: catraca de cliques que acelera e depois assenta, com um fio metálico fino"""
    N = _n(dur); x = np.zeros(N); r = _rng(seed); tt = 0.0
    while tt < dur:
        u = tt / dur; ritmo = ritmo0 + (ritmo1 - ritmo0) * np.sin(np.pi * u) ** 0.8
        i = int(tt * SR); m = min(N - i, int(0.03 * SR)); a = np.arange(m) / SR
        x[i:i + m] += (_bp(r.standard_normal(m), 1800, 7500) * np.exp(-a * 220) * 0.7 + np.sin(2 * np.pi * (1300 + 500 * u) * a) * np.exp(-a * 90) * 0.35) * r.uniform(0.7, 1.0)
        tt += 1.0 / ritmo
    fio = _bp(_ruido(dur, seed + 1), 2500, 6000) * 0.05 * np.minimum(1, _t(dur) / 0.1)
    return _norm(_est(x + fio, 0.5), 0.5)


def linha(dur=1.0, seed=0, f0=500.0, f1=2400.0):
    """uma linha de luz sendo traçada: tom que sobe com tremolo leve e um chiado fino; termina seco"""
    t = _t(dur); u = np.clip(t / dur, 0, 1)
    f = f0 * (f1 / f0) ** u
    m = np.sin(2 * np.pi * np.cumsum(f) / SR) * (0.55 + 0.25 * np.sin(2 * np.pi * 14 * t))
    m += _bp(_ruido(dur, seed), 3500, 10000) * 0.1
    env = np.minimum(1, t / 0.03) * np.minimum(1, (dur - t) / 0.02) * (0.3 + 0.7 * u)
    return _norm(_est(m * env, 0.3), 0.45)


def desce(dur=1.8, seed=0):
    """a onda do grito descendo do rosto aos pés: um sopro cujo tom cai de 3 kHz a 300 Hz, com um fiapo de eco"""
    t = _t(dur); u = np.clip(t / dur, 0, 1)
    fc = 3000 * (0.1) ** u
    x = _bp(_ruido(dur, seed), 200, fc) * (0.2 + 0.8 * np.sin(np.pi * np.clip(u * 0.98, 0, 1)) ** 0.8)
    x += np.sin(2 * np.pi * np.cumsum(900 * (0.28) ** u) / SR) * 0.12 * np.sin(np.pi * u)
    return _norm(_est(x, 0.8), 0.5)


def grito(dur=1.0, seed=0):
    """o grito dele para baixo, com as mãos em volta da boca: voz aberta e grave, com sala"""
    v = SX._voz(dur, 190.0, vogal=(800, 1200), seed=seed, vib=5.0, fv=0.03)
    t = _t(dur)
    env = np.minimum(1, t / 0.05) * np.exp(-np.maximum(0, t - 0.5) * 3.0) * np.minimum(1, (dur - t) / 0.08)
    return _norm(_reverb(_est(v * env, 0.5), rt=0.7, mix=0.3, seed=9), 0.6)


def agulha(dur=1.0, seed=0):
    """o ponteiro de um manômetro subindo: cliques metálicos que desaceleram e uma batidinha no fim"""
    N = _n(dur); x = np.zeros(N); r = _rng(seed); tt = 0.0; k = 0
    while tt < dur * 0.85:
        i = int(tt * SR); m = min(N - i, int(0.025 * SR)); a = np.arange(m) / SR
        x[i:i + m] += _bp(r.standard_normal(m), 1500, 6000) * np.exp(-a * 200) * (0.6 + 0.4 * (1 - tt / dur))
        tt += 0.045 + 0.03 * (tt / dur) ** 2; k += 1
    i = int(dur * 0.9 * SR); m = min(N - i, int(0.12 * SR)); a = np.arange(m) / SR
    x[i:i + m] += np.sin(2 * np.pi * 380 * a) * np.exp(-a * 38) * 0.5
    return _norm(_est(x, 0.4), 0.45)


def sangue(dur=0.6, seed=0):
    """o pulso do sangue subindo pelo tubo: um 'ssshump' molhado, grave que sobe de tom"""
    t = _t(dur); u = np.clip(t / dur, 0, 1)
    m = _bp(_ruido(dur, seed), 80, 500 + 900 * u) * (np.sin(np.pi * u) ** 1.2) * 0.9
    m += np.sin(2 * np.pi * np.cumsum(70 + 90 * u) / SR) * 0.55 * np.exp(-t * 3.5)
    return _norm(_est(m, 0.5), 0.6)


def jato(dur=2.0, seed=0):
    """um avião a jato passando longe, no alto: ruído de 300 a 2,5 kHz que sobe e desce com a passagem e cai de tom"""
    t = _t(dur); u = np.clip(t / dur, 0, 1)
    ampl = np.sin(np.pi * u) ** 1.4
    f_hi = 3200 - 1800 * u
    x = _bp(_ruido(dur, seed), 250, f_hi) * ampl * 0.9 + np.sin(2 * np.pi * np.cumsum(240 - 80 * u) / SR) * 0.12 * ampl
    return _norm(_est(x, 1.2, 0.3 - 0.6 * u * 0), 0.45)


def inala(dur=0.8, seed=0):
    """ele puxa o ar pela boca: sopro de 800 a 4 kHz que sobe e se estrangula, ar fino"""
    t = _t(dur); u = np.clip(t / dur, 0, 1)
    x = _bp(_ruido(dur, seed), 700, 2500 + 2200 * u) * np.sin(np.pi * np.clip(u * 0.9, 0, 1)) ** 1.1
    x += np.sin(2 * np.pi * np.cumsum(2200 + 900 * u) / SR) * 0.06 * u
    return _norm(_est(x, 0.3), 0.45)


def zumbido(dur=6.0, seed=0, f=55.0):
    """o silêncio do espaço: dois tons graves batendo devagar (uns 0,6 Hz) e um fiapo de ar muito agudo; entra e sai devagar"""
    t = _t(dur)
    m = np.sin(2 * np.pi * f * t) * 0.5 + np.sin(2 * np.pi * (f * 1.012) * t) * 0.45 + np.sin(2 * np.pi * f * 2.0 * t) * 0.35 + np.sin(2 * np.pi * f * 3.0 * t) * 0.18
    m += _bp(_ruido(dur, seed), 5000, 12000) * 0.01
    e = np.minimum(1, t / (dur * 0.35)) * np.minimum(1, (dur - t) / (dur * 0.35))
    return _norm(_est(m * e, 0.6), 0.5)


def tropeco(dur=0.35, seed=0):
    """a ponta do tênis raspa e prende no meio-fio: um ruge curto, um arranhão de borracha e um 'tum' surdo"""
    t = _t(dur)
    x = _bp(_ruido(dur, seed), 400, 3800) * np.exp(-t * 14) * 0.7
    x[int(0.18 * SR):] += (np.sin(2 * np.pi * 110 * t[int(0.18 * SR):]) * np.exp(-(t[int(0.18 * SR):] - 0.18) * 30)) * 0.5
    return _norm(_est(x, 0.5), 0.55)


def maos_chao(dur=0.9, seed=0):
    """as duas mãos espalmadas no asfalto: dois tapas surdos, uma nuvem de poeira e o ar que sai do peito"""
    t = _t(dur); x = np.zeros_like(t)
    for d in (0.0, 0.05):
        i = int(d * SR); m = _n(0.25); a = np.arange(m) / SR
        x[i:i + m] += (_bp(_ruido(0.25, seed + int(d * 100)), 300, 2800) * np.exp(-a * 38) * 0.8 + np.sin(2 * np.pi * 85 * a) * np.exp(-a * 22) * 0.7)
    x += _bp(_ruido(dur, seed + 4), 1500, 7000) * np.exp(-t * 6) * 0.15
    return _norm(_est(x, 0.5), 0.7)


def queda_vento(dur=1.7, seed=0):
    """a queda em câmera lenta: um vento que desce de tom e engrossa; nada de aceleração, só peso"""
    t = _t(dur); u = np.clip(t / dur, 0, 1)
    x = _bp(_ruido(dur, seed), 120, 2200 * (0.35) ** u) * (0.25 + 0.75 * u ** 1.3) * np.minimum(1, t / 0.2)
    return _norm(_est(x, 0.8), 0.5)


def rumor_lua(dur=1.5, seed=0):
    """a Lua desliza para o lado dele: um rumor grave longo que sobe de tom e some, com um brilho de metal no alto"""
    t = _t(dur); u = np.clip(t / dur, 0, 1)
    m = np.sin(2 * np.pi * np.cumsum(38 + 60 * u * u) / SR) * 0.8 * np.sin(np.pi * u) ** 0.9
    m += _bp(_ruido(dur, seed), 100, 600) * 0.35 * np.sin(np.pi * u)
    return _norm(_est(m, 0.9), 0.6)


def cabelo(dur=0.9, seed=0):
    """um fio fino descendo do céu: um assobio agudo e leve que desce de tom e para; um tinido quase imperceptível no fim"""
    t = _t(dur); u = np.clip(t / dur, 0, 1)
    m = np.sin(2 * np.pi * np.cumsum(4200 * (0.55) ** u) / SR) * 0.35 * np.sin(np.pi * u) ** 1.2 + _bp(_ruido(dur, seed), 3000, 9000) * 0.06 * np.sin(np.pi * u)
    return _norm(_est(m, 0.4), 0.4)


def aterra(dur=0.5, seed=0):
    """o tênis para a um fio da Terra minúscula: um ping de vidro pequeno, com um zumbido que cede"""
    t = _t(dur)
    m = np.sin(2 * np.pi * 2900 * t) * np.exp(-t * 12) * 0.6 + np.sin(2 * np.pi * 7800 * t) * np.exp(-t * 28) * 0.15
    m += np.sin(2 * np.pi * 55 * t) * np.exp(-t * 6) * 0.35
    return _norm(_est(m, 0.3), 0.5)


ALL = {k: v for k, v in dict(globals()).items() if callable(v) and not k.startswith("_") and k not in ("grava",) and getattr(v, "__module__", None) == __name__}

if __name__ == "__main__":
    pasta = sys.argv[1]; os.makedirs(pasta, exist_ok=True)
    for nome in (sys.argv[2:] or sorted(ALL)):
        grava(ALL[nome](), os.path.join(pasta, nome + ".wav")); print("ok", nome)
