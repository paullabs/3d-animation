"""Efeitos sonoros sintetizados (sem custo, sem rede): whoosh, impacto grave, subida, tique, toque de papel/fichas, bipe de mira.
Ficam limpos, curtos e no mesmo timbre do canal; a ElevenLabs só entra para som muito específico (sirene, martelo de juiz, tiro, portão).

python3 sfx.py PASTA            -> grava todos os efeitos padrão em PASTA/*.wav (48 kHz, estéreo)
python3 sfx.py PASTA whoosh boom -> só os escolhidos
Uso em código: import sfx; a = sfx.whoosh(); sfx.grava(a, "x.wav")"""
import sys, os, wave
import numpy as np

SR = 48000
rng = np.random.default_rng(38)


def _t(dur):
    return np.arange(int(dur * SR)) / SR


def _env(n, ataque, queda, forma=3.0):
    """envelope: sobe em 'ataque' s e cai exponencialmente até o fim"""
    e = np.ones(n); a = max(1, int(ataque * SR))
    e[:a] = np.linspace(0, 1, a) ** 2
    q = np.arange(n - a) / max(1, (n - a))
    e[a:] = np.exp(-forma * q * (queda if queda else 1))
    return e


def _passa_baixa(x, fc):
    """filtro de um polo; fc pode ser vetor (varre a frequência)"""
    fc = np.broadcast_to(np.asarray(fc, float), x.shape)
    a = np.exp(-2 * np.pi * fc / SR); y = np.empty_like(x); s = 0.0
    for i in range(len(x)):
        s = a[i] * s + (1 - a[i]) * x[i]; y[i] = s
    return y


def _passa_alta(x, fc):
    return x - _passa_baixa(x, fc)


def _estereo(m, larg=0.0, pan=0.0):
    """mono -> estéreo; 'larg' afasta um atraso pequeno entre os canais; 'pan' de -1 a 1"""
    d = int(larg * 0.012 * SR)
    l = m.copy(); r = np.concatenate([np.zeros(d), m[:len(m) - d]]) if d else m.copy()
    gl, gr = np.sqrt(0.5 * (1 - pan)), np.sqrt(0.5 * (1 + pan))
    return np.stack([l * gl * 1.414, r * gr * 1.414], 1)


def _norm(a, pico=0.9):
    return a * (pico / (np.abs(a).max() + 1e-9))


def whoosh(dur=0.55, sobe=True):
    """ar passando pela câmera: ruído filtrado com varredura de frequência, pico perto do meio (bom para corte em movimento)"""
    t = _t(dur); n = len(t); u = t / dur
    ruido = rng.standard_normal(n)
    fc = 300 + 3200 * (np.sin(np.pi * u) ** 1.5) * (1.0 if sobe else 0.7)
    x = _passa_baixa(_passa_alta(ruido, 180), fc)
    env = np.sin(np.pi * np.clip(u * 1.1, 0, 1)) ** 2.2
    return _norm(_estereo(x * env, larg=0.8), 0.7)


def boom(dur=1.6, f0=72, f1=34):
    """impacto grave de cinema: seno que desce + clique de ataque; sem distorção"""
    t = _t(dur); n = len(t)
    f = f1 + (f0 - f1) * np.exp(-t * 6)
    fase = 2 * np.pi * np.cumsum(f) / SR
    corpo = np.sin(fase) * _env(n, 0.004, 1.0, 4.5)
    clique = _passa_baixa(rng.standard_normal(n), 2500) * np.exp(-t * 60) * 0.5
    return _norm(_estereo(corpo + clique, larg=0.2), 0.85)


def impacto_metal(dur=1.2):
    """batida metálica seca (grade, porta de ferro): parciais inarmônicas que somem rápido + ruído de choque"""
    t = _t(dur); n = len(t)
    x = np.zeros(n)
    for f, a, d in [(180, 1.0, 7), (412, 0.7, 9), (733, 0.5, 12), (1210, 0.35, 16), (1980, 0.2, 22)]:
        x += a * np.sin(2 * np.pi * f * t + rng.uniform(0, 6)) * np.exp(-t * d)
    choque = _passa_alta(rng.standard_normal(n), 900) * np.exp(-t * 45) * 0.6
    return _norm(_estereo(x + choque, larg=0.4), 0.8)


def subida(dur=1.6):
    """riser curto: ruído que abre e tom que sobe, termina seco (pede o boom depois)"""
    t = _t(dur); n = len(t); u = t / dur
    ruido = _passa_baixa(rng.standard_normal(n), 400 + 6000 * u ** 2) * u ** 2.5
    tom = np.sin(2 * np.pi * np.cumsum(220 + 660 * u ** 2) / SR) * u ** 3 * 0.35
    return _norm(_estereo(ruido + tom, larg=0.6), 0.6)


def tique(f=2400, dur=0.09):
    """tique de interface (número que aparece no contador): curto e agudo, sem incomodar"""
    t = _t(dur); n = len(t)
    x = np.sin(2 * np.pi * f * t) * np.exp(-t * 70) + 0.3 * np.sin(2 * np.pi * f * 1.5 * t) * np.exp(-t * 90)
    return _norm(_estereo(x), 0.5)


def bipe_mira(dur=0.5):
    """bipe de mira travando: dois bipes curtos"""
    t = _t(dur); x = np.zeros(len(t))
    for t0 in (0.0, 0.16):
        m = (t >= t0) & (t < t0 + 0.08)
        x[m] = np.sin(2 * np.pi * 1760 * (t[m] - t0)) * np.exp(-(t[m] - t0) * 20)
    return _norm(_estereo(x), 0.5)


def papel(n_toques=12, dur=1.3, intervalo=None):
    """toques de papel (fichas batendo no mural, notas caindo): rajadas curtas de ruído agudo, ritmo levemente irregular"""
    t = _t(dur); x = np.zeros(len(t))
    passo = intervalo or dur / (n_toques + 1)
    for k in range(n_toques):
        i = int((k * passo + rng.uniform(-0.01, 0.01)) * SR)
        if i < 0 or i >= len(x):
            continue
        m = min(len(x) - i, int(0.06 * SR)); tt = np.arange(m) / SR
        burst = _passa_alta(rng.standard_normal(m), 1500) * np.exp(-tt * 70) * rng.uniform(0.6, 1.0)
        x[i:i + m] += burst
    return _norm(_estereo(x, larg=0.5), 0.55)


def grava(a, path):
    a = np.clip(a, -1, 1)
    with wave.open(path, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((a * 32767).astype("<i2").tobytes())


PADRAO = dict(whoosh=whoosh, boom=boom, impacto_metal=impacto_metal, subida=subida, tique=tique, bipe_mira=bipe_mira, papel=papel)

if __name__ == "__main__":
    pasta = sys.argv[1]; os.makedirs(pasta, exist_ok=True)
    nomes = sys.argv[2:] or list(PADRAO)
    for k in nomes:
        grava(PADRAO[k](), os.path.join(pasta, k + ".wav")); print("ok", k)
