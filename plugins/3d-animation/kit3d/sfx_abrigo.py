"""Efeitos sonoros sintetizados de "O abrigo" (sem custo, só numpy): um som próprio para cada ação que a imagem mostra, no mesmo timbre.
Pedido de 25/10/2026: "colocar efeitos sonoros". Cada função devolve um estéreo float (48 kHz); python3 sfx_abrigo.py PASTA grava todos em PASTA/*.wav.
O plano de som (plano_som_abrigo.py) escolhe a variante (seed) para nenhum arquivo se repetir. Filtros por FFT (rápidos e sem fase estranha)."""
import os, sys, wave
import numpy as np

SR = 48000


def _n(dur):
    return int(dur * SR)


def _t(dur):
    return np.arange(_n(dur)) / SR


def _rng(seed):
    return np.random.default_rng(1000 + seed)


def _ruido(dur, seed=0):
    return _rng(seed).standard_normal(_n(dur))


def _bp(x, lo, hi):
    """passa-faixa por FFT (bordas suaves); lo=0 vira passa-baixa, hi>=SR/2 vira passa-alta. hi pode ser um vetor (corte que varre no tempo)"""
    if isinstance(hi, np.ndarray):
        pts = np.geomspace(max(30.0, float(hi.min())), max(31.0, float(hi.max())), 6)
        vs = [_bp(x, lo, float(p)) for p in pts]
        pos = np.interp(np.log(np.clip(hi, pts[0], pts[-1])), np.log(pts), np.arange(len(pts)))
        i0 = np.clip(pos.astype(int), 0, len(pts) - 2); fr = pos - i0
        out = np.zeros_like(x)
        for k in range(len(pts)):
            w = np.where(i0 == k, 1 - fr, 0.0) + np.where(i0 + 1 == k, fr, 0.0)
            out += vs[k] * w
        return out
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR)
    m = np.ones_like(f)
    if lo > 0:
        m *= 1 / (1 + (lo / np.maximum(f, 1e-3)) ** 6)
    if hi < SR / 2:
        m *= 1 / (1 + (f / hi) ** 6)
    return np.fft.irfft(X * m, len(x))


def _env(n, ataque=0.005, queda=6.0, fim=0.01):
    t = np.arange(n) / SR
    e = np.minimum(1.0, t / max(ataque, 1e-4)) ** 1.5 * np.exp(-t * queda)
    k = max(1, int(fim * SR)); e[-k:] *= np.linspace(1, 0, k)
    return e


def _est(m, larg=0.0, pan=0.0):
    d = int(larg * 0.012 * SR)
    l = m.copy(); r = np.concatenate([np.zeros(d), m[:len(m) - d]]) if d else m.copy()
    gl, gr = np.sqrt(0.5 * (1 - pan)), np.sqrt(0.5 * (1 + pan))
    return np.stack([l * gl * 1.414, r * gr * 1.414], 1)


def _norm(a, pico=0.8):
    return a * (pico / (np.abs(a).max() + 1e-9))


def _reverb(x, rt=0.6, mix=0.25, seed=5):
    """sala de concreto: resposta ao impulso de ruído que morre, aplicada por FFT"""
    n = _n(rt); r = _rng(seed).standard_normal(n) * np.exp(-np.arange(n) / SR * (6.9 / rt)); r = _bp(r, 150, 7000)
    m = x.shape[0] if x.ndim == 2 else len(x)
    tam = 1 << int(np.ceil(np.log2(m + n)))
    if x.ndim == 2:
        out = np.stack([np.fft.irfft(np.fft.rfft(x[:, c], tam) * np.fft.rfft(r, tam), tam)[:m + n] for c in range(2)], 1)
        x2 = np.pad(x, ((0, n), (0, 0)))
    else:
        out = np.fft.irfft(np.fft.rfft(x, tam) * np.fft.rfft(r, tam), tam)[:m + n]; x2 = np.pad(x, (0, n))
    out = out / (np.abs(out).max() + 1e-9) * np.abs(x2).max()
    return x2 * (1 - mix) + out * mix * 1.6


def grava(a, path):
    a = np.clip(a, -1, 1)
    with wave.open(path, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((a * 32767).astype("<i2").tobytes())


# ============================================================ rua e explosão
def sirene(dur=8.0, seed=0, longe=0.35):
    """sirene de alerta de bairro: duas frequências que sobem e descem (uma onda de 3 s), harmônicos, eco de rua e abafada pela distância"""
    t = _t(dur)
    f = 520 + 230 * np.sin(2 * np.pi * t / 3.2 - 1.2)
    ph = 2 * np.pi * np.cumsum(f) / SR
    x = np.sin(ph) + 0.5 * np.sin(2 * ph) + 0.28 * np.sin(3 * ph) + 0.14 * np.sin(5 * ph)
    x *= np.minimum(1, t / 0.4) * np.minimum(1, (dur - t) / 0.9)
    x = _bp(x, 200, 3400 * (1 - 0.6 * longe))
    return _norm(_reverb(_est(x, 1.2, 0.2), 1.4, 0.35, seed), 0.7)


def rumor(dur=7.0, seed=0, cresce=True):
    """a explosão lá longe: um rumor grave que cresce (ruído de 25 a 160 Hz com estalos fundos); termina onde o clarão começa"""
    t = _t(dur); u = t / dur
    x = _bp(_ruido(dur, seed), 22, 150) * (0.25 + 0.9 * u ** 1.6 if cresce else 1)
    x += 0.5 * np.sin(2 * np.pi * np.cumsum(32 + 8 * np.sin(2 * np.pi * t * 0.4)) / SR) * (0.3 + u)
    est = _bp(_ruido(dur, seed + 1), 60, 380) * (np.abs(_ruido(dur, seed + 2)) > 3.1) * 4
    x += est * u
    return _norm(_est(x, 0.3), 0.8)


def clarao(dur=6.0, seed=0):
    """o céu estoura em branco: estampido largo de 40 ms, boom grave que desce, zumbido agudo nos ouvidos que some devagar e vento que entra"""
    t = _t(dur); n = len(t)
    est = _ruido(dur, seed) * np.exp(-t * 40) * 1.2
    f = 28 + 50 * np.exp(-t * 5)
    boom = np.sin(2 * np.pi * np.cumsum(f) / SR) * _env(n, 0.006, 1.1)
    onda = _bp(_ruido(dur, seed + 1), 40, 900) * np.exp(-t * 2.2) * 0.8
    zumbido = np.sin(2 * np.pi * 3950 * t) * 0.07 * np.exp(-t * 0.55) * np.minimum(1, t / 0.25) + np.sin(2 * np.pi * 6100 * t) * 0.03 * np.exp(-t * 0.8)
    return _norm(_est(est + boom * 1.2 + onda + zumbido, 0.6), 0.9)


def zumbido_ouvido(dur=3.0):
    t = _t(dur)
    x = (np.sin(2 * np.pi * 3950 * t) * 0.5 + np.sin(2 * np.pi * 5200 * t) * 0.18) * np.exp(-t * 0.9) * np.minimum(1, t / 0.4)
    return _norm(_est(x, 0.2), 0.5)


def subida(dur=1.6, seed=0):
    t = _t(dur); u = t / dur
    r = _bp(_ruido(dur, seed), 300, 400 + 8000 * u ** 2) * u ** 2.5
    tom = np.sin(2 * np.pi * np.cumsum(110 + 700 * u ** 2.2) / SR) * u ** 3 * 0.35
    baixo = np.sin(2 * np.pi * np.cumsum(38 + 40 * u) / SR) * u ** 2 * 0.5
    return _norm(_est(r + tom + baixo, 0.6), 0.7)


def vento(dur=8.0, seed=0, forca=1.0):
    """vento que passa por ruína: ruído de 120 a 1100 Hz que sobe e desce devagar e um assobio fino que passeia"""
    t = _t(dur)
    rajada = 0.45 + 0.55 * (0.5 + 0.5 * np.sin(2 * np.pi * t / 5.3 + seed) * np.sin(2 * np.pi * t / 2.7 + 2 * seed))
    x = _bp(_ruido(dur, seed), 110, 1100) * rajada
    fa = 700 + 420 * np.sin(2 * np.pi * t / 6.1 + seed)
    ass = _bp(_ruido(dur, seed + 3), 500, 1300) * 0.15 * (0.4 + 0.6 * np.sin(2 * np.pi * t / 4.3) ** 2)
    x = (x + ass) * forca * np.minimum(1, t / 1.0) * np.minimum(1, (dur - t) / 1.5)
    return _norm(_est(x, 1.4, 0.15 * np.sin(seed)), 0.6)


# ============================================================ bicicleta e corrida
def freio_bici(dur=0.4, seed=0):
    t = _t(dur); u = t / dur
    f = 2300 - 650 * u + 40 * np.sin(2 * np.pi * 31 * t)
    x = np.sin(2 * np.pi * np.cumsum(f) / SR)
    x = (x + 0.5 * np.sign(x) * 0.3) * (0.5 + 0.5 * (_ruido(dur, seed) > 0)) * _env(len(t), 0.02, 4.0)
    x = _bp(x, 1500, 5200) + 0.25 * _bp(_ruido(dur, seed + 1), 2000, 6000) * _env(len(t), 0.02, 5)
    return _norm(_est(x, 0.5), 0.55)


def raspa_pe(dur=0.22, seed=0):
    x = _bp(_ruido(dur, seed), 400, 3500) * _env(_n(dur), 0.012, 12.0)
    return _norm(_est(x, 0.3), 0.55)


def sino(dur=1.6, seed=0, eco=True, duas=True):
    """sino de bicicleta: o 'trim' (duas batidas de martelinho), parciais agudas inarmônicas que batem entre si"""
    n = _n(dur); t = np.arange(n) / SR; x = np.zeros(n)
    for t0 in ((0.0, 0.085) if duas else (0.0,)):
        tt = np.maximum(t - t0, 0); on = (t >= t0).astype(float)
        for f, a, d in ((2870, 1.0, 5.5), (2913, 0.8, 5.0), (4470, 0.55, 7.5), (6120, 0.34, 10.0), (7750, 0.2, 14.0)):
            x += a * np.sin(2 * np.pi * f * (1 + 0.003 * seed) * tt) * np.exp(-tt * d) * on
    x += _bp(_ruido(dur, seed), 3000, 9000) * np.exp(-t * 90) * 0.3
    x = _norm(x, 0.7)
    return _norm(_reverb(_est(x, 0.4), 0.9, 0.3, seed) if eco else _est(x, 0.2), 0.7)


def queda_bici(dur=1.5, seed=0):
    """a bicicleta cai no asfalto: pancada de ferro, aro que tilinta, cesta de vime estalando e a corrente chacoalhando"""
    n = _n(dur); t = np.arange(n) / SR; x = np.zeros(n)
    for t0, g in ((0.0, 1.0), (0.11, 0.55), (0.2, 0.3), (0.29, 0.16)):
        tt = np.maximum(t - t0, 0); on = (t >= t0)
        for f, a, d in ((196, 1.0, 9), (433, 0.7, 11), (787, 0.5, 14), (1290, 0.35, 18), (2100, 0.2, 24)):
            x += g * a * np.sin(2 * np.pi * f * tt * (1 + 0.04 * np.sin(seed + f))) * np.exp(-tt * d) * on
        x += g * _bp(_ruido(dur, seed + int(t0 * 100)), 500, 6000) * np.exp(-tt * 38) * on
    corr = _bp(_ruido(dur, seed + 9), 2500, 9000) * (np.abs(_ruido(dur, seed + 10)) > 1.7) * np.exp(-t * 3.2) * 0.6
    vime = _bp(_ruido(dur, seed + 11), 700, 2500) * (np.abs(_ruido(dur, seed + 12)) > 2.6) * np.exp(-t * 6) * 1.2
    return _norm(_est(x + corr + vime, 0.7), 0.85)


def roda_gira(dur=1.6, seed=0, w0=22.0, w1=3.0):
    """roda no ar: o clique dos raios cai de ritmo (w0 a w1 estalos por segundo) e um sopro de ar que perde força"""
    n = _n(dur); x = np.zeros(n); tt = 0.0; k = 0
    while tt < dur:
        w = w0 + (w1 - w0) * (tt / dur) ** 0.7
        i = int(tt * SR); m = min(n - i, int(0.012 * SR))
        if m > 0:
            x[i:i + m] += _bp(_rng(seed + k).standard_normal(m), 2200, 7500) * np.exp(-np.arange(m) / SR * 280) * (0.5 + 0.5 * (1 - tt / dur))
        tt += 1.0 / w; k += 1
    t = _t(dur)
    x += _bp(_ruido(dur, seed + 3), 200, 1500) * 0.06 * (1 - t / dur)
    return _norm(_est(x, 0.5), 0.5)


def passos(dur=1.0, passo=0.25, seed=0, peso=1.0, solo="asfalto", fase=0.0, jitter=0.012):
    """passos de corrida/caminhada: baque grave + areia/asfalto; 'peso' muda o grave; ritmo com leve desencontro"""
    n = _n(dur); x = np.zeros(n); r = _rng(seed); k = 0; tt = fase
    while tt < dur:
        i = int((tt + r.uniform(-jitter, jitter)) * SR)
        if 0 <= i < n:
            m = min(n - i, int(0.18 * SR)); a = np.arange(m) / SR
            g = r.uniform(0.75, 1.0)
            grave = np.sin(2 * np.pi * (95 + 30 * peso) * a * (1 - 0.8 * a)) * np.exp(-a * 38) * (0.8 * peso)
            if solo == "cinza":
                gr = _bp(r.standard_normal(m), 400, 3200) * np.exp(-a * 24) * 0.7 + _bp(r.standard_normal(m), 3500, 9000) * np.exp(-a * 60) * 0.15
            elif solo == "concreto":
                gr = _bp(r.standard_normal(m), 600, 4500) * np.exp(-a * 55) * 0.55 + grave * 0.2
            else:
                gr = _bp(r.standard_normal(m), 700, 5200) * np.exp(-a * 48) * 0.6
            x[i:i + m] += (grave + gr) * g
        tt += passo; k += 1
    return _norm(_est(x, 0.5, 0.0), 0.65)


def multidao_corre(dur=1.4, n_pessoas=8, seed=0):
    """muita gente correndo: vários passos desencontrados, o roçar das roupas, o ritmo irregular"""
    x = np.zeros((_n(dur), 2)); r = _rng(seed)
    for k in range(n_pessoas):
        p = passos(dur, r.uniform(0.2, 0.3), seed + 10 + k, r.uniform(0.7, 1.2), fase=r.uniform(0, 0.25))
        pan = r.uniform(-0.8, 0.8); x += _est(p[:, 0], 0.5, pan) * r.uniform(0.35, 0.8)
    roupa = _est(_bp(_ruido(dur, seed + 3), 600, 3000) * 0.08 * (0.6 + 0.4 * np.sin(2 * np.pi * 3.6 * _t(dur))), 1.0)
    return _norm(x + roupa, 0.7)


def ofegar(dur=1.2, seed=0, ritmo=2.2):
    """respiração de quem corre: sopro de 700 a 3500 Hz que sobe e desce no ritmo da corrida"""
    t = _t(dur)
    ciclo = 0.5 + 0.5 * np.sin(2 * np.pi * ritmo * t + seed)
    x = _bp(_ruido(dur, seed), 600, 3600) * ciclo ** 1.7 * 0.8 + _bp(_ruido(dur, seed + 1), 120, 450) * ciclo ** 2.5 * 0.4
    x *= np.minimum(1, t / 0.1) * np.minimum(1, (dur - t) / 0.2)
    return _norm(_est(x, 0.3), 0.5)


def _voz(dur, f0, vogal=(750, 1250), seed=0, vib=5.5, fv=0.012):
    """voz sintética (fonte dente de serra + dois formantes): vogal 'ah' para gritos longe"""
    t = _t(dur); r = _rng(seed)
    f = f0 * (1 + fv * np.sin(2 * np.pi * vib * t + r.uniform(0, 6)))
    ph = np.cumsum(f) / SR
    fonte = (2 * (ph % 1.0) - 1) + 0.3 * r.standard_normal(len(t)) * 0.3
    return _bp(fonte, vogal[0] * 0.6, vogal[0] * 1.5) * 1.0 + 0.7 * _bp(fonte, vogal[1] * 0.7, vogal[1] * 1.4)


def gritos_longe(dur=2.0, n_vozes=6, seed=0, longe=0.7):
    """gente gritando de longe, em pânico: vozes de 220 a 520 Hz com vibrato, entradas desencontradas, abafadas e com eco de rua"""
    x = np.zeros(_n(dur)); r = _rng(seed); t = _t(dur)
    for k in range(n_vozes):
        d = r.uniform(0.7, 1.5); t0 = r.uniform(0, max(0.01, dur - d))
        v = _voz(d, r.uniform(230, 520), (r.uniform(650, 850), r.uniform(1100, 1500)), seed + k)
        v *= _env(len(v), 0.12, 1.2, 0.1) ** 0.5; i = int(t0 * SR); x[i:i + len(v)] += v[:len(x) - i] * r.uniform(0.5, 1.0)
    x = _bp(x, 200, 3200 * (1 - 0.6 * longe))
    return _norm(_reverb(_est(x, 1.4, 0.1), 1.1, 0.4, seed), 0.55)


def gritos_perto(dur=1.4, n_vozes=4, seed=0):
    """o povo na porta, por fora: vozes mais fechadas, com esforço, pedindo (sem palavra, só som de gente gritando)"""
    x = np.zeros(_n(dur)); r = _rng(seed)
    for k in range(n_vozes):
        d = r.uniform(0.5, 0.9); t0 = r.uniform(0, max(0.01, dur - d))
        v = _voz(d, r.uniform(180, 420), (r.uniform(500, 700), r.uniform(1000, 1400)), seed + k, vib=r.uniform(4.5, 7), fv=0.03)
        v = _bp(v + 0.5 * _ruido(d, seed + k) * 0.2, 200, 3800) * _env(len(v), 0.05, 2.5, 0.08)
        i = int(t0 * SR); x[i:i + len(v)] += v[:len(x) - i] * r.uniform(0.6, 1.0)
    return _norm(_reverb(_est(x, 0.8), 0.5, 0.2, seed), 0.6)


# ============================================================ a porta
def porta_corre(dur=0.7, seed=0):
    """a folha de aço corre no trilho: raspão grave de metal contra metal, vibrando"""
    t = _t(dur); u = t / dur
    x = _bp(_ruido(dur, seed), 80, 900) * (0.6 + 0.4 * np.sin(2 * np.pi * 37 * t))
    f = 130 + 60 * u
    x += 0.5 * (np.sin(2 * np.pi * np.cumsum(f) / SR) + 0.5 * np.sin(4 * np.pi * np.cumsum(f) / SR)) * (0.5 + 0.5 * np.sin(2 * np.pi * 19 * t))
    x += _bp(_ruido(dur, seed + 1), 1500, 5000) * 0.25 * (0.5 + 0.5 * np.sin(2 * np.pi * 53 * t))
    x *= np.minimum(1, t / 0.08) * (0.5 + 0.5 * u)
    return _norm(_reverb(_est(x, 0.8), 0.7, 0.2, seed), 0.7)


def porta_bate(dur=2.2, seed=0):
    """a folha bate no batente: pancada de aço (cofre), boom grave que dura e o metal que ressoa e some"""
    t = _t(dur); n = len(t); x = np.zeros(n)
    for f, a, d in ((88, 1.0, 5.0), (176, 0.75, 6.5), (231, 0.6, 8), (412, 0.5, 9), (690, 0.4, 12), (1170, 0.3, 16)):
        x += a * np.sin(2 * np.pi * f * t + _rng(seed + int(f)).uniform(0, 6)) * np.exp(-t * d)
    x += _bp(_ruido(dur, seed), 120, 5000) * np.exp(-t * 55) * 1.2
    sub = np.sin(2 * np.pi * np.cumsum(42 + 40 * np.exp(-t * 8)) / SR) * _env(n, 0.004, 1.6)
    return _norm(_reverb(_est(x + sub * 1.1, 0.5), 1.4, 0.3, seed), 0.95)


def soca_aco(dur=0.9, seed=0, peso=1.0):
    """punho na porta de aço, por fora: pancada seca, um som oco de chapa que balança e o estalo da pele no metal"""
    t = _t(dur); n = len(t); r = _rng(seed); x = np.zeros(n)
    for f, a, d in ((130 + 20 * r.uniform(-1, 1), 1.0, 18), (260, 0.55, 22), (471, 0.4, 28), (860, 0.25, 36)):
        x += a * np.sin(2 * np.pi * f * t) * np.exp(-t * d)
    x += _bp(_ruido(dur, seed), 200, 3000) * np.exp(-t * 90) * 0.7
    x += np.sin(2 * np.pi * np.cumsum(70 + 40 * np.exp(-t * 30)) / SR) * np.exp(-t * 14) * 0.7 * peso
    return _norm(_reverb(_est(x, 0.4, r.uniform(-0.4, 0.4)), 0.6, 0.18, seed), 0.8)


def tapa_vidro(dur=0.4, seed=0):
    """mão aberta no vidro grosso: baque abafado e o guincho da palma que escorrega"""
    t = _t(dur)
    x = _bp(_ruido(dur, seed), 180, 1400) * np.exp(-t * 40) * 1.0 + np.sin(2 * np.pi * 240 * t) * np.exp(-t * 30) * 0.5
    gu = _bp(_ruido(dur, seed + 1), 1200, 3500) * np.exp(-t * 7) * 0.12 * (0.5 + 0.5 * np.sin(2 * np.pi * 90 * t))
    return _norm(_est(x + gu, 0.3), 0.6)


def tranca_roda(dur=1.3, seed=0, reversa=False):
    """a roda de bronze gira (estala no mecanismo, em saltinhos) e trava com um 'clac' de ferrolho que cai"""
    n = _n(dur); x = np.zeros(n); r = _rng(seed); k = 0; tt = 0.02
    while tt < dur * 0.72:
        i = int(tt * SR); m = min(n - i, int(0.05 * SR)); a = np.arange(m) / SR
        x[i:i + m] += (_bp(r.standard_normal(m), 600, 4200) * np.exp(-a * 90) * 0.6 + np.sin(2 * np.pi * (900 + 80 * k % 5) * a) * np.exp(-a * 80) * 0.2) * (0.6 + 0.4 * r.uniform())
        tt += 0.07 - 0.03 * (tt / (dur * 0.72)); k += 1
    ranger = _bp(_ruido(dur, seed + 1), 300, 1800) * 0.12 * np.minimum(1, _t(dur) / 0.1) * (_t(dur) < dur * 0.72)
    x += ranger
    i = int(dur * 0.76 * SR); m = n - i; a = np.arange(m) / SR
    clac = (np.sin(2 * np.pi * 180 * a) * np.exp(-a * 14) + 0.6 * np.sin(2 * np.pi * 412 * a) * np.exp(-a * 20) + 0.4 * np.sin(2 * np.pi * 1050 * a) * np.exp(-a * 34)
            + _bp(r.standard_normal(m), 400, 5000) * np.exp(-a * 90) * 1.0)
    x[i:] += clac * 1.3
    if reversa:                                                    # destranca: o ferrolho sai primeiro, depois a roda gira e estala solta
        i = int(dur * 0.76 * SR); clac = x[i:].copy(); resto = x[:i].copy()[::-1] * np.linspace(0.3, 1.0, i)
        x = np.zeros(n); x[:len(clac)] += clac; j = int(0.12 * SR); x[j:j + i] += resto[:n - j] * 0.8
    return _norm(_reverb(_est(x, 0.5), 0.8, 0.25, seed), 0.85)


def porta_range(dur=2.6, seed=0):
    """a folha pesada abre: gemido grave de dobradiça seca, o metal estala e um rumor de poeira que cai"""
    t = _t(dur); u = t / dur
    f = 74 + 60 * u ** 0.7 + 7 * np.sin(2 * np.pi * 6.1 * t)
    ph = np.cumsum(f) / SR
    x = (2 * (ph % 1) - 1) * 0.6 + np.sin(2 * np.pi * ph * 2) * 0.4
    x = _bp(x, 60, 700 + 600 * u) * (0.45 + 0.55 * np.abs(np.sin(2 * np.pi * (7 + 5 * u) * t)))
    x += _bp(_ruido(dur, seed), 700, 4000) * 0.25 * (np.abs(_ruido(dur, seed + 1)) > 1.9) * 2
    x += _bp(_ruido(dur, seed + 2), 40, 220) * 0.5
    x *= np.minimum(1, t / 0.15) * np.minimum(1, (dur - t) / 0.5)
    return _norm(_reverb(_est(x, 1.0), 1.0, 0.3, seed), 0.8)


def ferrugem(dur=1.0, seed=0):
    """flocos de ferrugem caindo no chão: tilintar seco, desencontrado, que rareia"""
    n = _n(dur); x = np.zeros(n); r = _rng(seed)
    for k in range(26):
        t0 = (r.uniform() ** 1.7) * (dur - 0.05); i = int(t0 * SR); m = int(0.03 * SR); a = np.arange(m) / SR
        x[i:i + m] += np.sin(2 * np.pi * r.uniform(3000, 8000) * a) * np.exp(-a * r.uniform(120, 260)) * r.uniform(0.3, 1.0) * (1 - t0 / dur * 0.7)
    return _norm(_est(x, 0.8), 0.45)


# ============================================================ dentro do abrigo
def lata_tinir(dur=0.5, seed=0):
    r = _rng(seed); t = _t(dur); f0 = r.uniform(900, 1500)
    x = sum(a * np.sin(2 * np.pi * f0 * k * t) * np.exp(-t * d) for k, a, d in ((1, 1.0, 22), (2.31, 0.5, 30), (3.7, 0.3, 40), (5.2, 0.15, 55)))
    x += _bp(_ruido(dur, seed), 2000, 8000) * np.exp(-t * 180) * 0.4
    return _norm(_est(x, 0.3, r.uniform(-0.3, 0.3)), 0.55)


def lata_cai_rola(dur=1.5, seed=0, rola=True):
    """lata vazia cai na pilha e rola: batida de metal fino, tilintar e depois o 'rrr' que fica mais lento e para"""
    t = _t(dur); n = len(t)
    x = np.zeros(n)
    for f, a, d in ((410, 1.0, 14), (900, 0.7, 20), (1730, 0.5, 28), (2650, 0.3, 40)):
        x += a * np.sin(2 * np.pi * f * t) * np.exp(-t * d)
    x += _bp(_ruido(dur, seed), 500, 6500) * np.exp(-t * 70) * 0.9
    if rola:
        w = 36 * np.exp(-t / 0.55) + 5
        ph = np.cumsum(w) / SR; rr = _bp(_ruido(dur, seed + 1), 250, 2800) * (0.5 + 0.5 * np.sin(2 * np.pi * ph * 2.0)) ** 2 * np.exp(-t / 0.5) * 0.55
        x += rr * (t > 0.12)
        for k in range(4):
            i = int((0.18 + 0.23 * k ** 1.3) * SR); m = min(n - i, int(0.1 * SR))
            if m > 0:
                a = np.arange(m) / SR; x[i:i + m] += np.sin(2 * np.pi * (1500 - 120 * k) * a) * np.exp(-a * 50) * 0.35 * (0.8 ** k)
    return _norm(_reverb(_est(x, 0.5), 0.6, 0.18, seed), 0.8)


def lata_some(dur=0.35, seed=0):
    """lata levantada da prateleira: raspão curto e o aço da prateleira que ecoa"""
    t = _t(dur)
    x = _bp(_ruido(dur, seed), 1200, 6000) * _env(len(t), 0.02, 10) * 0.7 + np.sin(2 * np.pi * 1180 * t) * np.exp(-t * 26) * 0.25
    return _norm(_est(x, 0.3), 0.5)


def agua_balanco(dur=1.2, seed=0, forca=1.0):
    """água balançando dentro do garrafão: ondas de 250 a 1800 Hz que sobem e descem e bolhas que estouram"""
    t = _t(dur); n = len(t)
    ondas = _bp(_ruido(dur, seed), 250, 1800) * (0.35 + 0.65 * np.abs(np.sin(2 * np.pi * (1.7 + 0.5 * seed % 2) * t + seed))) ** 1.6
    x = ondas * 0.7 * forca
    r = _rng(seed + 4)
    for k in range(int(10 * dur)):
        i = int(r.uniform(0, dur - 0.06) * SR); m = int(r.uniform(0.02, 0.05) * SR); a = np.arange(m) / SR
        f = r.uniform(380, 900); x[i:i + m] += np.sin(2 * np.pi * (f + 900 * a / 0.03 * 0.4) * a) * np.exp(-a * 90) * r.uniform(0.15, 0.5) * forca
    x *= np.minimum(1, t / 0.08) * np.minimum(1, (dur - t) / 0.12)
    return _norm(_est(x, 0.8), 0.5)


def gole(dur=0.5, seed=0):
    """um gole: o 'glup' que desce de 380 para 120 Hz com água, e a garganta"""
    t = _t(dur)
    f = 120 + 280 * np.exp(-t * 9)
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * _env(len(t), 0.01, 7) * 0.9 + _bp(_ruido(dur, seed), 300, 1600) * np.exp(-t * 14) * 0.5
    return _norm(_est(x, 0.2), 0.5)


def glug_garrafao(dur=1.4, seed=0):
    """água saindo do gargalo: 'glug glug' (a bolha de ar entra, a água sai), um depois do outro"""
    t = _t(dur); n = len(t); x = np.zeros(n); k = 0; tt = 0.0
    while tt < dur - 0.1:
        i = int(tt * SR); m = min(n - i, int(0.16 * SR)); a = np.arange(m) / SR
        x[i:i + m] += (np.sin(2 * np.pi * (230 + 120 * (k % 2)) * a * (1 + 2 * a)) * np.exp(-a * 18) * 0.9 + _bp(_rng(seed + k).standard_normal(m), 400, 2200) * np.exp(-a * 22) * 0.5)
        tt += 0.19 + 0.02 * (k % 3); k += 1
    return _norm(_est(x, 0.4), 0.5)


def plastico(dur=0.8, seed=0):
    """o plástico do garrafão estalando ao ser levantado: estalos agudos soltos, o gargalo apertado"""
    n = _n(dur); x = np.zeros(n); r = _rng(seed)
    for k in range(18):
        i = int(r.uniform(0, dur - 0.05) * SR); m = int(0.012 * SR)
        x[i:i + m] += _bp(r.standard_normal(m), 1800, 9000) * np.exp(-np.arange(m) / SR * 250) * r.uniform(0.3, 1.0)
    x += _bp(_ruido(dur, seed + 1), 800, 3200) * 0.06
    return _norm(_est(x, 0.6), 0.45)


def giz_risca(dur=0.7, seed=0, bate=True):
    """giz no quadro: o 'toc' de encostar e depois o chiado seco da linha, que treme"""
    t = _t(dur); n = len(t)
    x = _bp(_ruido(dur, seed), 1800, 7000) * (0.45 + 0.55 * (0.5 + 0.5 * np.sin(2 * np.pi * 46 * t + 4 * np.sin(2 * np.pi * 7 * t)))) * 0.45
    x *= np.minimum(1, t / 0.04) * np.minimum(1, (dur - t) / 0.06)
    if bate:
        m = int(0.02 * SR); x[:m] += _bp(_ruido(0.02, seed + 1), 800, 5000) * np.exp(-np.arange(m) / SR * 150) * 1.1
    return _norm(_est(x, 0.3), 0.5)


def lapis(dur=0.6, seed=0):
    t = _t(dur)
    x = _bp(_ruido(dur, seed), 2500, 8000) * (0.4 + 0.6 * (0.5 + 0.5 * np.sin(2 * np.pi * 28 * t))) * 0.4 * np.minimum(1, t / 0.03) * np.minimum(1, (dur - t) / 0.05)
    return _norm(_est(x, 0.3), 0.4)


def garfo_prato(dur=0.35, seed=0):
    """garfo no prato de louça: o 'tling' e a batida abafada"""
    r = _rng(seed); t = _t(dur); f0 = r.uniform(2600, 3600)
    x = sum(a * np.sin(2 * np.pi * f0 * k * t) * np.exp(-t * d) for k, a, d in ((1, 1.0, 26), (1.52, 0.5, 38), (2.4, 0.3, 55))) * 0.7
    x += np.sin(2 * np.pi * 320 * t) * np.exp(-t * 60) * 0.5 + _bp(_ruido(dur, seed), 800, 5000) * np.exp(-t * 120) * 0.5
    return _norm(_est(x, 0.3, r.uniform(-0.4, 0.4)), 0.5)


def garfo_raspa(dur=0.7, seed=0):
    t = _t(dur)
    x = _bp(_ruido(dur, seed), 2500, 7500) * (0.5 + 0.5 * np.sin(2 * np.pi * (3 + seed % 2) * t)) ** 1.4 * 0.4 + np.sin(2 * np.pi * 3100 * t) * 0.03 * np.sin(2 * np.pi * 3 * t) ** 2
    x *= np.minimum(1, t / 0.05) * np.minimum(1, (dur - t) / 0.08)
    return _norm(_est(x, 0.3), 0.45)


def mastigar(dur=1.2, seed=0, ritmo=2.6):
    """mastigar devagar: baques molhados e abafados no ritmo de quem come (sem mostrar a boca)"""
    n = _n(dur); x = np.zeros(n); r = _rng(seed); tt = 0.05
    while tt < dur - 0.1:
        i = int(tt * SR); m = int(0.09 * SR); a = np.arange(m) / SR
        x[i:i + m] += (_bp(r.standard_normal(m), 150, 1600) * np.exp(-a * 38) * 0.8 + np.sin(2 * np.pi * (140 + r.uniform(-20, 20)) * a) * np.exp(-a * 50) * 0.4)
        tt += (1 / ritmo) * r.uniform(0.85, 1.2)
    return _norm(_est(x, 0.3), 0.4)


def moscas(dur=2.5, seed=0, n_moscas=3):
    """moscas no ar: zumbidos de 160 a 240 Hz que passeiam de um ouvido para o outro, chegam perto e se afastam"""
    x = np.zeros((_n(dur), 2)); r = _rng(seed); t = _t(dur)
    for k in range(n_moscas):
        f = r.uniform(150, 250) + 20 * np.sin(2 * np.pi * r.uniform(2, 5) * t + k) + 14 * np.sin(2 * np.pi * r.uniform(7, 11) * t)
        ph = np.cumsum(f) / SR
        m = (2 * (ph % 1) - 1) + 0.5 * np.sin(4 * np.pi * ph)
        m = _bp(m, 160, 2800) * (0.15 + 0.85 * (0.5 + 0.5 * np.sin(2 * np.pi * r.uniform(0.4, 1.1) * t + 2 * k)) ** 2)
        pan = 0.85 * np.sin(2 * np.pi * r.uniform(0.3, 0.8) * t + k)
        x += np.stack([m * np.sqrt(0.5 * (1 - pan)) * 1.4, m * np.sqrt(0.5 * (1 + pan)) * 1.4], 1) * 0.5
    x *= np.minimum(1, t / 0.2)[:, None] * np.minimum(1, (dur - t) / 0.3)[:, None]
    return _norm(x, 0.35)


def agua_chega(dur=1.2, seed=0):
    """água escura se espalhando no piso: chapinhar abafado e um fiozinho que escorre"""
    t = _t(dur)
    x = _bp(_ruido(dur, seed), 200, 1500) * (0.3 + 0.7 * (t / dur)) * 0.5 + _bp(_ruido(dur, seed + 1), 1800, 5500) * (np.abs(_ruido(dur, seed + 2)) > 2.4) * 0.25
    x *= np.minimum(1, t / 0.15) * np.minimum(1, (dur - t) / 0.2)
    return _norm(_est(x, 0.7), 0.4)


def vaso_borbulha(dur=1.2, seed=0):
    """o vaso transbordando: borbulhar grave que sobe, água escorrendo pelas bordas e um gotejar"""
    t = _t(dur); n = len(t); r = _rng(seed); x = np.zeros(n)
    for k in range(int(14 * dur)):
        i = int(r.uniform(0, dur - 0.1) * SR); m = int(r.uniform(0.04, 0.09) * SR); a = np.arange(m) / SR
        x[i:i + m] += np.sin(2 * np.pi * r.uniform(110, 300) * a * (1 + 6 * a)) * np.exp(-a * 45) * r.uniform(0.3, 1.0)
    x += _bp(_ruido(dur, seed + 1), 300, 2400) * (0.25 + 0.5 * t / dur) * 0.5
    return _norm(_est(x, 0.5), 0.5)


def pingo(dur=0.4, seed=0):
    r = _rng(seed); t = _t(dur); f = r.uniform(900, 1400)
    x = np.sin(2 * np.pi * np.cumsum(f * (1 + 2.2 * np.exp(-t * 40))) / SR) * np.exp(-t * 30)
    return _norm(_est(x, 0.2, r.uniform(-0.3, 0.3)), 0.4)


def gas_chia(dur=2.0, seed=0):
    """o cheiro ruim virando uma névoa que entra: chiado macio e grave, um sopro enjoado, sem agudo"""
    t = _t(dur)
    x = _bp(_ruido(dur, seed), 600, 3200) * 0.18 + _bp(_ruido(dur, seed + 1), 60, 240) * 0.5
    x *= np.minimum(1, t / 0.5) * np.minimum(1, (dur - t) / 0.7) * (0.7 + 0.3 * np.sin(2 * np.pi * 0.8 * t))
    return _norm(_est(x, 1.0), 0.4)


def soluco(dur=0.35, seed=0):
    """soluço de choro: um 'hic' voz de peito, que sobe e quebra rápido, com o ar que sai"""
    r = _rng(seed); t = _t(dur)
    f = 330 - 80 * t / dur + 30 * np.sin(2 * np.pi * 14 * t)
    v = _bp(2 * ((np.cumsum(f) / SR) % 1) - 1, 420, 1500) * 0.7 + _bp(_ruido(dur, seed), 900, 3600) * 0.25
    v *= _env(len(t), 0.02, 9.0, 0.02)
    return _norm(_est(v, 0.2, r.uniform(-0.3, 0.3)), 0.4)


def choro_baixo(dur=1.4, seed=0):
    """chorar baixinho, sem palavra: soluços em fila, cada vez mais separados, com fungada"""
    x = np.zeros(_n(dur)); r = _rng(seed); tt = 0.05
    while tt < dur - 0.3:
        s = soluco(0.3, seed + int(tt * 10))[:, 0]; i = int(tt * SR); x[i:i + len(s)] += s[:len(x) - i] * r.uniform(0.6, 1.0); tt += r.uniform(0.28, 0.5)
    return _norm(_est(x, 0.3), 0.4)


def fungar(dur=0.4, seed=0):
    t = _t(dur)
    x = _bp(_ruido(dur, seed), 500, 3500) * np.exp(-((t - 0.12) / 0.07) ** 2) * 0.8 + _bp(_ruido(dur, seed + 1), 300, 2600) * np.exp(-((t - 0.28) / 0.05) ** 2) * 0.5
    return _norm(_est(x, 0.2), 0.35)


def pano(dur=0.9, seed=0, forca=1.0):
    """tecido roçando (blusa, suéter, jaqueta): ruído de 700 a 4500 Hz em ondas curtas e irregulares"""
    t = _t(dur); r = _rng(seed)
    mod = np.clip(0.3 + 0.7 * _bp(r.standard_normal(len(t)), 0, 9) * 5, 0, 1.0)
    x = _bp(_ruido(dur, seed + 1), 700, 4500) * mod * 0.5 * forca
    x *= np.minimum(1, t / 0.08) * np.minimum(1, (dur - t) / 0.15)
    return _norm(_est(x, 0.5), 0.4)


def pia(dur=0.7, seed=0):
    """porquinho-da-índia: assobio curto que sobe (uíp, uíp)"""
    n = _n(dur); x = np.zeros(n); r = _rng(seed)
    for t0 in (0.02, 0.27):
        i = int(t0 * SR); m = int(0.18 * SR); a = np.arange(m) / SR; u = a / 0.18
        f = r.uniform(1700, 2100) * (1 + 0.55 * u) * (1 + 0.02 * np.sin(2 * np.pi * 28 * a))
        x[i:i + m] += np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * u) ** 1.2 * 0.8 + 0.2 * np.sin(4 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * u)
    return _norm(_est(x, 0.3, r.uniform(-0.3, 0.3)), 0.4)


def roer(dur=1.0, seed=0):
    """a Pipoca roendo feno: estalinhos secos e miúdos, bem rápidos"""
    n = _n(dur); x = np.zeros(n); r = _rng(seed); tt = 0.03
    while tt < dur - 0.03:
        i = int(tt * SR); m = int(0.012 * SR)
        x[i:i + m] += _bp(r.standard_normal(m), 1500, 7000) * np.exp(-np.arange(m) / SR * 280) * r.uniform(0.4, 1.0)
        tt += r.uniform(0.045, 0.085) if r.uniform() > 0.2 else r.uniform(0.15, 0.3)
    return _norm(_est(x, 0.5), 0.4)


def ranger_grade(dur=0.6, seed=0):
    """portinha de arame da gaiola: guincho fino de dobradiça que treme"""
    t = _t(dur); u = t / dur
    f = 780 + 380 * u + 25 * np.sin(2 * np.pi * 21 * t)
    x = _bp(np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)) * 0.4 + np.sin(2 * np.pi * np.cumsum(f) / SR), 500, 3600) * (0.5 + 0.5 * np.sin(2 * np.pi * 14 * t)) ** 0.6
    x *= np.minimum(1, t / 0.05) * np.minimum(1, (dur - t) / 0.12) * 0.5
    return _norm(_est(x, 0.4), 0.4)


def tilintar_grade(dur=0.5, seed=0):
    t = _t(dur)
    x = sum(a * np.sin(2 * np.pi * f * t) * np.exp(-t * d) for f, a, d in ((1900, 1.0, 20), (2860, 0.6, 28), (4120, 0.35, 40))) + _bp(_ruido(dur, seed), 2500, 9000) * np.exp(-t * 140) * 0.3
    return _norm(_est(x, 0.5), 0.4)


def ranger_cama(dur=0.7, seed=0):
    """mola da cama velha: dois guinchos graves de ferro"""
    t = _t(dur); n = len(t); x = np.zeros(n)
    for t0, f0 in ((0.0, 260), (0.3, 330)):
        a = np.maximum(t - t0, 0); on = (t >= t0)
        f = f0 + 90 * a / 0.25
        x += _bp(2 * ((np.cumsum(f) / SR) % 1) - 1, 150, 1800) * np.sin(np.pi * np.clip(a / 0.26, 0, 1)) * on * (0.6 + 0.4 * np.sin(2 * np.pi * 18 * a))
    return _norm(_est(x * 0.7, 0.4), 0.4)


def respiro_lento(dur=3.0, seed=0, ritmo=0.3):
    """respiração de quem está morrendo: sopros longos e finos, com um chiado no peito, cada vez mais fundos"""
    t = _t(dur)
    c = (0.5 + 0.5 * np.sin(2 * np.pi * ritmo * t - 1.2)) ** 1.5
    x = _bp(_ruido(dur, seed), 300, 2800) * c * 0.6 + _bp(_ruido(dur, seed + 1), 90, 400) * c * 0.35
    x += _bp(2 * (((np.cumsum(120 + 12 * c) / SR)) % 1) - 1, 150, 700) * c * 0.12
    x *= np.minimum(1, t / 0.4) * np.minimum(1, (dur - t) / 0.4)
    return _norm(_est(x, 0.4), 0.45)


def ultimo_suspiro(dur=2.2, seed=0):
    """o último sopro: sai o ar, desce o tom e acaba sem voltar"""
    t = _t(dur); u = t / dur
    c = np.exp(-u * 3.6) * np.minimum(1, t / 0.12)
    f = 190 - 90 * u
    x = _bp(_ruido(dur, seed), 250, 2200 * (1 - 0.7 * u)) * c * 0.8 + _bp(2 * ((np.cumsum(f) / SR) % 1) - 1, 120, 900) * c * 0.25
    return _norm(_est(x, 0.5), 0.45)


def coracao(dur=1.0, seed=0, lento=1.0):
    """tum-tum de coração: duas batidas graves de 55 Hz, a segunda mais fraca; 'lento' alarga o tempo"""
    n = _n(dur); x = np.zeros(n)
    for t0, g in ((0.02, 1.0), (0.02 + 0.26 * lento, 0.62)):
        i = int(t0 * SR); m = min(n - i, int(0.45 * SR)); a = np.arange(m) / SR
        if m > 0:
            x[i:i + m] += (np.sin(2 * np.pi * np.cumsum(62 - 20 * np.minimum(1, a / 0.2)) / SR) * np.exp(-a * 11) + 0.35 * _bp(_rng(seed).standard_normal(m), 40, 400) * np.exp(-a * 40)) * g
    return _norm(_est(x, 0.2), 0.85)


def coracao_para(dur=4.5, seed=0):
    """o coração que falha: batidas cada vez mais espaçadas e fracas, até a última"""
    n = _n(dur); x = np.zeros((n, 2)); tt = 0.0; k = 0; esp = 0.8
    while tt < dur - 0.6:
        b = coracao(0.6, seed + k, 1.0 + 0.2 * k) * (0.95 ** (k * 2) * 0.9)
        i = int(tt * SR); x[i:i + len(b)] += b[:n - i]
        tt += esp; esp *= 1.28; k += 1
    return _norm(x, 0.7)


def carta(dur=0.3, seed=0):
    """carta jogada na mesa: o tapa seco da cartolina e o baque da mesa"""
    r = _rng(seed); t = _t(dur)
    x = _bp(_ruido(dur, seed), 900, 7500) * np.exp(-t * 95) * 0.9 + np.sin(2 * np.pi * (170 + 25 * r.uniform()) * t) * np.exp(-t * 55) * 0.55
    return _norm(_est(x, 0.3, r.uniform(-0.3, 0.3)), 0.5)


def baralho(dur=0.7, seed=0):
    """cartas sendo embaralhadas: rajada de tapinhas rápidos"""
    n = _n(dur); x = np.zeros(n); r = _rng(seed); tt = 0.0
    while tt < dur - 0.05:
        i = int(tt * SR); m = int(0.02 * SR)
        x[i:i + m] += _bp(r.standard_normal(m), 1500, 8000) * np.exp(-np.arange(m) / SR * 160) * r.uniform(0.4, 1.0)
        tt += r.uniform(0.018, 0.04)
    return _norm(_est(x, 0.5), 0.45)


def lampada_pisca(dur=0.5, seed=0):
    """a luz falha: estalos de arco, o zumbido que cai e volta"""
    t = _t(dur); r = _rng(seed); x = np.zeros(len(t))
    for k in range(5):
        i = int(r.uniform(0, dur * 0.5) * SR); m = int(0.015 * SR)
        x[i:i + m] += _bp(r.standard_normal(m), 1500, 9000) * np.exp(-np.arange(m) / SR * 150) * r.uniform(0.4, 1.0)
    zz = np.sin(2 * np.pi * 100 * t) * 0.3 * np.exp(-((t - dur * 0.35) / 0.12) ** 2) + np.sin(2 * np.pi * 300 * t) * 0.12
    return _norm(_est(x + zz * np.exp(-t * 3), 0.3), 0.5)


def zumbido_luz(dur=2.0, seed=0):
    """lâmpada de filamento acesa: zumbido de 100 Hz com harmônicos, bem baixinho"""
    t = _t(dur)
    x = np.sin(2 * np.pi * 100 * t) * 0.5 + np.sin(2 * np.pi * 200 * t) * 0.3 + np.sin(2 * np.pi * 300 * t) * 0.15 + _bp(_ruido(dur, seed), 3000, 9000) * 0.03
    x *= np.minimum(1, t / 0.3) * np.minimum(1, (dur - t) / 0.3)
    return _norm(_est(x, 0.3), 0.3)


def estatica_cctv(dur=2.0, seed=0):
    """câmera de segurança: chiado de vídeo, estalos soltos e um bipe baixo de gravação"""
    t = _t(dur); n = len(t); r = _rng(seed)
    x = _bp(_ruido(dur, seed), 2500, 9500) * 0.1 + _bp(_ruido(dur, seed + 1), 80, 300) * 0.05
    for k in range(int(4 * dur)):
        i = int(r.uniform(0, dur - 0.02) * SR); m = int(0.008 * SR); x[i:i + m] += _bp(r.standard_normal(m), 1000, 9000) * np.exp(-np.arange(m) / SR * 400) * r.uniform(0.2, 0.7)
    x += np.sin(2 * np.pi * 1000 * t) * 0.08 * ((t % 1.0) < 0.07)
    return _norm(_est(x, 0.3), 0.3)


def relogio(dur=2.5, seed=0):
    """o tempo passando: tique-taque que acelera, abafado, com uma batida grave no fim"""
    n = _n(dur); x = np.zeros(n); tt = 0.05; k = 0
    while tt < dur - 0.25:
        i = int(tt * SR); m = int(0.04 * SR); a = np.arange(m) / SR
        x[i:i + m] += (np.sin(2 * np.pi * (1900 if k % 2 == 0 else 1500) * a) * np.exp(-a * 140) + _bp(_rng(seed + k).standard_normal(m), 1500, 6000) * np.exp(-a * 200) * 0.5) * 0.7
        tt += max(0.07, 0.42 - 0.34 * (tt / dur) ** 1.3); k += 1
    return _norm(_reverb(_est(x, 0.4), 0.6, 0.2, seed), 0.45)


def tum(dur=2.5, seed=0, f0=48):
    """batida grave de transição (o corte para a ausência): sub que desce e some"""
    t = _t(dur)
    x = np.sin(2 * np.pi * np.cumsum(f0 * (1 + 0.5 * np.exp(-t * 7))) / SR) * _env(len(t), 0.006, 1.7) + _bp(_ruido(dur, seed), 40, 300) * np.exp(-t * 14) * 0.5
    return _norm(_est(x, 0.2), 0.85)


# ============================================================ lá fora, depois
def passos_botas(dur=3.0, seed=0):
    """botas largas no concreto do abrigo: poucos passos lentos, pesados, com o eco da sala"""
    return _norm(_reverb(passos(dur, 0.62, seed, 1.3, "concreto", fase=0.1, jitter=0.03), 0.9, 0.25, seed), 0.7)


def passos_cinza(dur=1.2, seed=0):
    """botas na cinza: o farelo que afunda e estala (poucos, devagar)"""
    return _norm(passos(dur, 0.5, seed, 0.6, "cinza", fase=0.05, jitter=0.02), 0.6)


def puff(dur=0.5, seed=0):
    """a nuvenzinha de cinza que o pé levanta: um 'fff' macio e fosco"""
    t = _t(dur)
    x = _bp(_ruido(dur, seed), 250, 2400) * np.exp(-((t - 0.06) / 0.1) ** 2) * 0.8 + _bp(_ruido(dur, seed + 1), 2500, 7000) * np.exp(-t * 18) * 0.08
    return _norm(_est(x, 0.4), 0.35)


def escovar_po(dur=1.0, seed=0):
    """o polegar tirando o pó do sino: fricção macia e curta"""
    t = _t(dur)
    x = _bp(_ruido(dur, seed), 900, 4200) * (0.4 + 0.6 * (0.5 + 0.5 * np.sin(2 * np.pi * 7 * t))) * 0.3 * np.minimum(1, t / 0.1) * np.minimum(1, (dur - t) / 0.2)
    return _norm(_est(x, 0.3), 0.4)


def sino_seco(dur=2.2, seed=0):
    """o único 'trim' do mundo morto, sem eco: seco e curto, deixa o silêncio depois dele"""
    return sino(dur, seed + 3, eco=False, duas=True)


def sirene_range(dur=2.4, seed=0):
    """a sirene caída, enferrujada, estalando ao esfriar: um gemido fino e lento de ferro"""
    t = _t(dur); u = t / dur
    f = 330 - 110 * u + 6 * np.sin(2 * np.pi * 5 * t)
    x = _bp(2 * ((np.cumsum(f) / SR) % 1) - 1, 150, 1400) * (0.3 + 0.7 * np.sin(np.pi * u) ** 2) * 0.3
    for k in range(5):
        i = int(_rng(seed + k).uniform(0, dur - 0.1) * SR); m = int(0.02 * SR)
        x[i:i + m] += _bp(_rng(seed + 20 + k).standard_normal(m), 300, 3500) * np.exp(-np.arange(m) / SR * 160) * 0.6
    return _norm(_reverb(_est(x, 0.8), 1.2, 0.35, seed), 0.4)


def tom_sala(dur=8.0, seed=0, f0=55):
    """o 'silêncio' do abrigo: um zumbido muito grave de ventilação, sem melodia"""
    t = _t(dur)
    x = np.sin(2 * np.pi * f0 * t) * 0.5 + np.sin(2 * np.pi * f0 * 2 * t + 1) * 0.25 + _bp(_ruido(dur, seed), 60, 700) * 0.18
    x *= np.minimum(1, t / 1.0) * np.minimum(1, (dur - t) / 1.0)
    return _norm(_est(x, 1.0), 0.3)


def gaveta_vazia(dur=0.9, seed=0):
    """a estante vazia ecoando: um 'ploc' oco de madeira e o aço da prateleira que vibra"""
    t = _t(dur)
    x = np.sin(2 * np.pi * 140 * t) * np.exp(-t * 18) + _bp(_ruido(dur, seed), 200, 2500) * np.exp(-t * 90) * 0.6 + np.sin(2 * np.pi * 1020 * t) * np.exp(-t * 12) * 0.08
    return _norm(_reverb(_est(x, 0.4), 0.8, 0.3, seed), 0.5)


def cadeira(dur=0.7, seed=0):
    """cadeira de madeira arrastada no concreto: um raspão curto com tremor"""
    t = _t(dur)
    x = _bp(_ruido(dur, seed), 120, 2000) * (0.5 + 0.5 * np.sin(2 * np.pi * 33 * t)) * 0.5 * _env(len(t), 0.03, 3.5)
    return _norm(_est(x, 0.4), 0.5)


def tecido_joelho(dur=0.6, seed=0):
    return pano(dur, seed, 0.9)


# ============================================================ v2 (25/10/2026, noite): explosão = distorção do espaço-tempo; porta = cofre
def espaco_tempo(dur=9.5, seed=0, t_hit=6.5):
    """a explosão vista de longe como uma dobra do espaço-tempo, um som GRAVE: um zumbido de sub que oscila cada vez mais fundo e mais rápido
    (a dobra se formando), uma sucção que fecha o ar (ruído que desce de 6 kHz a 60 Hz) e, no clarão, uma queda de tom de 140 para 22 Hz com
    fase girando, um vácuo curto e a cauda grave que balança e se desfaz. Sem agudo de explosão, sem estampido."""
    t = _t(dur); n = len(t)
    u = np.clip(t / t_hit, 0, 1)
    # 1) a dobra se formando: sub 34 a 52 Hz com tremolo que acelera (1 a 9 Hz) e profundidade que cresce
    f = 34 + 18 * u ** 2 + 2.5 * np.sin(2 * np.pi * (0.5 + 3 * u) * t)
    ph = np.cumsum(f) / SR
    trem = 1 - (0.15 + 0.6 * u) * (0.5 + 0.5 * np.sin(2 * np.pi * np.cumsum(1 + 8 * u ** 1.5) / SR))
    build = (np.sin(2 * np.pi * ph) + 0.35 * np.sin(4 * np.pi * ph + 1.0)) * trem * (0.08 + 0.92 * u ** 2.2) * (t < t_hit)
    # a trama de dentro: ruído grave que se afunila (passa-faixa que desce)
    ar = _bp(_ruido(dur, seed), 30, 200 + 700 * (1 - u) ** 2) * (0.1 + 0.9 * u ** 2) * (t < t_hit) * 0.7
    # 2) a sucção no último segundo: ruído de 6 kHz a 60 Hz, ficando mais forte e depois fechando em silêncio
    tt = np.clip((t - (t_hit - 0.9)) / 0.9, 0, 1)
    suc = _bp(_ruido(dur, seed + 1), 40, 6000 * (1 - tt) ** 2 + 70) * tt ** 1.5 * (t < t_hit) * 0.5
    suc *= np.clip((t_hit - t) / 0.06, 0, 1)
    # 3) o estouro silencioso: queda de tom de 150 a 22 Hz, fase que gira (FM lenta) e cauda que balança
    th = np.maximum(t - t_hit, 0); on = (t >= t_hit).astype(float)
    ff = 22 + 128 * np.exp(-th / 0.42)
    fm = 1.8 * np.sin(2 * np.pi * np.cumsum(5.5 * np.exp(-th / 2.2) + 0.7) / SR)
    drop = np.sin(2 * np.pi * np.cumsum(ff) / SR + fm * np.exp(-th / 1.8)) * np.exp(-th / 2.8) * on * np.minimum(1, th / 0.012)
    sub2 = np.sin(2 * np.pi * np.cumsum(27 + 6 * np.exp(-th / 1.5) + 1.4 * np.sin(2 * np.pi * 0.9 * t)) / SR) * np.exp(-th / 4.0) * on * np.clip((th - 0.25) / 0.5, 0, 1) * 0.7
    vacuo = 1 - 0.85 * np.exp(-((th - 0.13) / 0.07) ** 2) * on                           # um instante em que tudo fica sem ar
    cor = _bp(_ruido(dur, seed + 2), 25, 130) * np.exp(-th / 1.1) * on * 0.8              # o ar que volta como um rumor de 25 a 130 Hz
    # um fiapo de "rasgo" no grave médio (150 a 380 Hz) que gira no estéreo, para dar a ideia de dobra sem agudo
    rasgo = _bp(_ruido(dur, seed + 3), 120, 380) * np.exp(-th / 0.5) * on * 0.35 * np.sin(2 * np.pi * 11 * np.exp(-th / 1.0) * th)
    x = (build + ar + suc) + (drop * 1.0 + sub2 + cor + rasgo) * vacuo
    pan = np.sin(2 * np.pi * 0.35 * t)
    out = np.stack([x * (1 + 0.25 * pan), x * (1 - 0.25 * pan)], 1)
    out *= np.minimum(1, t / 0.5)[:, None] * np.minimum(1, (dur - t) / 1.2)[:, None]
    return _norm(out, 0.92)


def porta_cofre(dur=2.3, seed=0, t_bate=0.68):
    """a porta de cofre fecha: a folha corre abafada (raspão de 60 a 500 Hz), bate com um 'tum' curto e seco de 48 Hz (não é o grave da explosão),
    a pressão que sobe do batente, três ferrolhos que caem em fila (tchac, tchac, tchac) e o chiado da vedação"""
    t = _t(dur); n = len(t); r = _rng(seed)
    u = np.clip(t / t_bate, 0, 1)
    escorre = _bp(_ruido(dur, seed), 60, 520) * (0.6 + 0.4 * np.sin(2 * np.pi * 29 * t)) * (t < t_bate) * (0.25 + 0.75 * u) * 0.8
    escorre += _bp(_ruido(dur, seed + 1), 900, 2600) * 0.12 * (0.5 + 0.5 * np.sin(2 * np.pi * 47 * t)) * (t < t_bate) * u
    th = np.maximum(t - t_bate, 0); on = (t >= t_bate).astype(float)
    tum = np.sin(2 * np.pi * np.cumsum(48 + 70 * np.exp(-th / 0.035)) / SR) * np.exp(-th / 0.11) * on * 1.15
    pressao = _bp(_ruido(dur, seed + 2), 60, 420) * np.exp(-th / 0.09) * on * 1.0
    chapa = sum(a * np.sin(2 * np.pi * f * th) * np.exp(-th * d) for f, a, d in ((210, 0.35, 16), (340, 0.2, 22), (590, 0.12, 30))) * on
    x = escorre + tum + pressao + chapa
    for k, tl in enumerate((0.2, 0.34, 0.5)):                                           # os três ferrolhos
        i = int((t_bate + tl) * SR); m = min(n - i, int(0.18 * SR)); a = np.arange(m) / SR
        if m > 0:
            x[i:i + m] += (np.sin(2 * np.pi * (260 + 70 * k) * a) * np.exp(-a * 26) * 0.5 + _bp(r.standard_normal(m), 500, 6500) * np.exp(-a * 130) * 0.8
                           + np.sin(2 * np.pi * (1500 + 160 * k) * a) * np.exp(-a * 60) * 0.18)
    chia = _bp(_ruido(dur, seed + 3), 2200, 7500) * np.exp(-((th - 0.7) / 0.45) ** 2) * on * 0.08
    x = x + chia
    return _norm(_reverb(_est(x, 0.5), 0.45, 0.07, seed), 0.9)


# ============================================================ suspense antes do CTA (25/10/2026)
def escombro(dur=1.4, seed=0):
    """o barulho fora do quadro: uma chapa de metal que cede, uma pedra que rola e o entulho que assenta (som seco, de longe, sem grave de explosão)"""
    n = _n(dur); t = np.arange(n) / SR; r = _rng(seed); x = np.zeros(n)
    for t0, g, f0 in ((0.0, 1.0, 330), (0.16, 0.6, 520), (0.27, 0.45, 760), (0.44, 0.25, 910)):
        tt = np.maximum(t - t0, 0); on = (t >= t0)
        for f, a, d in ((f0, 1.0, 11), (f0 * 2.31, 0.5, 17), (f0 * 3.77, 0.3, 26)):
            x += g * a * np.sin(2 * np.pi * f * tt) * np.exp(-tt * d) * on
        x += g * _bp(r.standard_normal(n), 400, 5500) * np.exp(-tt * 42) * on * 0.9
    pedra = _bp(r.standard_normal(n), 250, 2200) * (0.4 + 0.6 * (0.5 + 0.5 * np.sin(2 * np.pi * 17 * t))) * np.exp(-np.maximum(t - 0.35, 0) / 0.32) * (t > 0.3) * 0.55
    return _norm(_reverb(_est(x + pedra, 0.8, -0.4), 1.0, 0.3, seed), 0.8)


def rosnado(dur=2.0, seed=0):
    """o rosnado do vulto: voz de peito que não é de gente (fonte de 55 a 95 Hz que tropeça, dois formantes de 'u', vibração de garganta de 25 a 35 Hz
    e sopro rouco), que sobe, se arrasta e quebra em um grunhido; sem palavra, sem agudo de grito"""
    t = _t(dur); n = len(t); r = _rng(seed); u = t / dur
    base = 92 - 28 * u + 7 * np.sin(2 * np.pi * 3.1 * t) + 14 * np.convolve(r.standard_normal(n), np.ones(int(0.05 * SR)) / (0.05 * SR), "same") * 6
    ph = np.cumsum(base) / SR
    fonte = 2 * (ph % 1.0) - 1 + 0.6 * np.sign(np.sin(2 * np.pi * ph * 0.5))
    garganta = 0.35 + 0.65 * (np.sin(2 * np.pi * np.cumsum(27 + 9 * np.sin(2 * np.pi * 1.7 * t)) / SR) > -0.1)
    f1 = _bp(fonte, 300, 620) * 1.0 + 0.8 * _bp(fonte, 700, 1250) + 0.4 * _bp(fonte, 1800, 2900) * (0.4 + 0.6 * u)
    corpo = _bp(fonte, 40, 160) * 0.9
    sopro = _bp(r.standard_normal(n), 500, 3800) * 0.28 * (0.5 + 0.5 * np.sin(2 * np.pi * 2.2 * t + 1)) ** 1.5
    x = (f1 * garganta + corpo + sopro)
    env = np.minimum(1, t / 0.28) ** 1.5 * np.exp(-np.maximum(t - 0.95, 0) / 0.5) * (1 + 0.25 * np.sin(2 * np.pi * 4.4 * t))
    quebra = np.zeros(n); i = int(1.12 * SR); m = min(n - i, int(0.22 * SR))
    if m > 0:
        a = np.arange(m) / SR; quebra[i:i + m] = np.sin(2 * np.pi * np.cumsum(150 - 400 * a) / SR) * np.exp(-a * 9) * 0.5              # o grunhido final que cai
    x = np.tanh(2.2 * x * env) * 0.8 + quebra
    x *= np.minimum(1, (dur - t) / 0.35)
    pan = np.clip(-0.6 + 0.9 * u, -1, 1)
    return _norm(_reverb(np.stack([x * np.sqrt(0.5 * (1 - pan)) * 1.4, x * np.sqrt(0.5 * (1 + pan)) * 1.4], 1), 0.9, 0.22, seed), 0.9)


def fala_boca_dummy():
    return None

ALL = {k: v for k, v in dict(globals()).items() if callable(v) and not k.startswith("_") and k not in ("grava", "main") and v.__module__ == __name__}

if __name__ == "__main__":
    pasta = sys.argv[1]; os.makedirs(pasta, exist_ok=True)
    for nome in (sys.argv[2:] or sorted(ALL)):
        try:
            grava(ALL[nome](), os.path.join(pasta, nome + ".wav")); print("ok", nome)
        except Exception as e:
            print("ERRO", nome, e)
