"""Trilha de rascunho de "O abrigo", sintetizada (sem custo): segue a história em ondas, com silêncios onde o filme fica sem som.
Pedido de 25/10/2026: "colocar efeitos sonoros" e música de tensão. É um rascunho para o ritmo da mixagem; a versão final pode vir do
Higgsfield (sonilo_music) só com a aprovação do Paulo (gasta crédito).
Mapa (segundos do filme): 0-6,5 a explosão chega (pulso e subida) | 6,5-7,6 zumbido, quase silêncio | 7,6-13,3 a porta fecha, tensão |
13,3-14,3 silêncio (ele não abriu) | 14,3-19,7 abrigo "seguro" (caixa de música em Ré menor, calmo) | 19,7-31,7 a comida acaba, o ar fica pesado
(segunda menor, a caixa desafina) | 31,7-42,6 a Pipoca some, notas soltas de piano | 42,6-47,5 os meses | 47,5-50,5 a Lu morre (cordas emocionais) |
50,5-54,2 baralho (caixa de música torta) | 54,2-58,98 a porta, tensão que sobe | 58,98-66,5 mundo morto (pedal grave, vento) | 66,5-72 o fim, uma nota alta que some.
python3 musica_abrigo.py SAIDA.wav"""
import sys, wave
import numpy as np

SR = 48000
TOT = 74.0
N = int(TOT * SR)
rng = np.random.default_rng(38)
T = np.arange(N) / SR


def nota(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def lp(x, fc):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR)
    return np.fft.irfft(X / (1 + (f / fc) ** 6), len(x))


def hp(x, fc):
    return x - lp(x, fc)


def janela(t0, t1, subida=0.6, descida=0.8):
    return np.clip((T - t0) / max(subida, 1e-3), 0, 1) * np.clip((t1 - T) / max(descida, 1e-3), 0, 1)


def pad(freqs, t0, t1, amp=0.2, brilho=900, det=0.004, subida=1.2, descida=1.5, vib=0.0):
    """acorde de dentes de serra desafinados e filtrados (cordas de longe)"""
    i0, i1 = int(t0 * SR), min(N, int(t1 * SR)); n = i1 - i0
    if n <= 0:
        return np.zeros(N)
    t = np.arange(n) / SR; x = np.zeros(n)
    for f in freqs:
        for d in (-det, 0.0, det):
            fv = f * (1 + d) * (1 + vib * np.sin(2 * np.pi * 5.2 * t + f))
            ph = np.cumsum(fv) / SR
            x += 2 * ((ph + rng.uniform()) % 1.0) - 1.0
    x = lp(x, brilho) * amp / max(1, len(freqs) * 3) ** 0.7
    x *= np.clip(t / subida, 0, 1) * np.clip((t[-1] - t) / descida, 0, 1)
    out = np.zeros(N); out[i0:i1] = x
    return out


def pluck(f, t0, amp=0.25, queda=3.0, brilho=3000, durm=3.0):
    """nota de caixa de música / piano seco: seno com harmônicos que somem"""
    i0 = int(t0 * SR); n = int(durm * SR)
    if i0 >= N:
        return np.zeros(N)
    n = min(n, N - i0); t = np.arange(n) / SR
    x = sum(a * np.sin(2 * np.pi * f * k * t) * np.exp(-t * (queda + 2.5 * k)) for k, a in ((1, 1.0), (2, 0.4), (3, 0.22), (4.01, 0.12), (5.97, 0.06)))
    x *= np.minimum(1, t / 0.004); x = lp(x, brilho) * amp
    out = np.zeros(N); out[i0:i0 + n] = x
    return out


def pulso(t0, t1, bpm, amp=0.3, f0=52):
    """batidas graves (coração/timpano)"""
    out = np.zeros(N); passo = 60.0 / bpm; t = t0
    while t < t1:
        i = int(t * SR); m = min(N - i, int(0.5 * SR))
        if m <= 0:
            break
        a = np.arange(m) / SR
        out[i:i + m] += (np.sin(2 * np.pi * np.cumsum(f0 * (1 + 0.8 * np.exp(-a * 14))) / SR) * np.exp(-a * 9) * amp)
        t += passo
    return out


def subida_ruido(t0, t1, amp=0.25):
    i0, i1 = int(t0 * SR), int(t1 * SR); n = i1 - i0; u = np.arange(n) / n
    r = rng.standard_normal(n)
    x = lp(r, 400) * 0.0
    for k, fc in enumerate((300, 800, 2000, 5000)):
        x += lp(r, fc * (0.5 + 1.5 * u).mean()) * 0.0
    x = lp(r, 6000) * (u ** 2.4) * 0.6 + np.sin(2 * np.pi * np.cumsum(90 + 600 * u ** 2) / SR) * u ** 3 * 0.35
    out = np.zeros(N); out[i0:i1] = x * amp * np.minimum(1, (n - np.arange(n)) / (0.02 * SR))
    return out


def drone(t0, t1, f0, amp=0.25, brilho=240):
    return pad([f0, f0 * 1.5, f0 * 2.0], t0, t1, amp, brilho, 0.003, 2.0, 2.5)


m = np.zeros(N)
D1, A1, D2, F2, A2, D3 = nota(26), nota(33), nota(38), nota(41), nota(45), nota(50)
Eb2, Bb2, Gb2, C3 = nota(39), nota(46), nota(42), nota(48)

# 1. a explosão chega (0 a 6,5): pedal grave, pulso que acelera, subida
m += drone(0.0, 6.5, D1, 0.45, 220)
m += pulso(0.8, 6.4, 78, 0.22)
m += pulso(4.0, 6.4, 156, 0.12)
m += pad([D2, A2, nota(53)], 2.0, 6.5, 0.12, 1400, 0.006, 3.0, 0.4)
m += subida_ruido(3.6, 6.5, 0.5)
# 2. depois do clarão (6,5 a 7,6): quase silêncio, só um sopro
m += pad([nota(86), nota(91)], 6.5, 8.0, 0.02, 9000, 0.001, 0.2, 1.3)
# 3. a porta fecha (7,6 a 13,3): tensão baixa e pulsos
m += drone(7.6, 13.3, D1, 0.5, 200)
m += pulso(8.0, 13.2, 66, 0.2)
m += pad([D2, F2, A2], 8.8, 13.3, 0.14, 700, 0.005, 2.0, 0.3)
# 4. 13,3 a 14,3: silêncio (ele não abriu) — só o pedal que some
m += drone(13.3, 14.9, D1, 0.18, 150) * np.clip((14.9 - T) / 1.6, 0, 1) ** 0.001
# 5. abrigo "seguro" (14,3 a 19,7): caixa de música em Ré menor, calma, e um pad quente
m += pad([D2, A2, F2 * 2], 14.6, 20.2, 0.16, 800, 0.004, 1.5, 1.8)
cx = [D3 * 2, nota(65 + 12), nota(69 + 12), nota(65 + 12), D3 * 2, nota(60 + 12), nota(65 + 12), nota(62 + 12)]
for k, t0 in enumerate(np.arange(14.9, 19.7, 0.6)):
    m += pluck(nota([74, 77, 81, 77, 74, 72, 77, 74][k % 8]), t0, 0.12, 2.6, 2800)
# 6. a comida acaba (19,7 a 31,7): o pad cai, a caixa desafina e o pulso volta; 5D (29,5): aglomerado
m += pad([D2, nota(39), A2], 20.0, 29.8, 0.14, 600, 0.008, 1.5, 0.8)
for k, t0 in enumerate(np.arange(20.2, 29.4, 1.2)):
    m += pluck(nota([74, 77, 74, 72][k % 4]) * (1 + 0.004 * k), t0, 0.08 * (1 - 0.04 * k), 3.2, 2400)
m += pulso(23.9, 29.4, 54, 0.16)
m += pad([D2, nota(39), nota(44), nota(51)], 29.4, 31.9, 0.2, 1200, 0.012, 1.0, 0.5, vib=0.004)
# 7. a Pipoca some (31,7 a 42,6): notas soltas de piano, um pedal frio, 34,4 uma nota só
m += pad([A1, E := nota(40)], 31.8, 42.8, 0.12, 380, 0.004, 2.0, 2.0)
for t0, mid in ((32.4, 69), (33.7, 65), (35.0, 64), (36.8, 62), (38.7, 57), (41.0, 60)):
    m += pluck(nota(mid), t0, 0.16, 1.5, 2200)
m += pluck(nota(45), 34.5, 0.25, 0.7, 1200)
m += pulso(38.4, 42.2, 48, 0.12)
# 8. os meses (42,6 a 47,5): pedal pesado, frases cada vez mais baixas
m += drone(42.6, 47.7, nota(31), 0.4, 180)
for t0, mid in ((43.2, 62), (44.2, 60), (45.2, 57), (46.3, 55)):
    m += pluck(nota(mid), t0, 0.12, 1.2, 1500)
# 9. a Lu morre (47,5 a 50,5): cordas emocionais em Ré menor que sobem e caem; 49,5 uma nota só
m += pad([D2, A2, F2 * 2], 47.5, 49.6, 0.34, 1800, 0.003, 0.8, 0.6, vib=0.004)
m += pad([nota(81), nota(77)], 47.9, 49.6, 0.17, 4500, 0.002, 0.9, 0.7, vib=0.006)
m += pad([D2, A2], 49.6, 51.8, 0.1, 500, 0.003, 0.6, 1.8)
m += pluck(nota(62), 49.7, 0.3, 0.7, 1600)
# 10. baralho (50,5 a 54,2): caixa de música torta, valsa lenta, desafinada
for k, t0 in enumerate(np.arange(51.0, 54.0, 0.55)):
    m += pluck(nota([69, 72, 76, 72, 69, 71][k % 6]) * (1 + 0.012 * np.sin(k * 1.7)), t0, 0.11, 2.2, 3400)
m += drone(50.8, 54.4, nota(33), 0.22, 170)
# 11. a porta (54,2 a 58,98): pedal, pulso que acelera, riser
m += drone(54.2, 59.0, D1, 0.5, 220)
m += pulso(54.4, 58.4, 70, 0.22) + pulso(57.0, 58.8, 140, 0.14)
m += pad([D2, F2, Gb2], 55.5, 58.9, 0.14, 900, 0.006, 1.2, 0.2)
m += subida_ruido(56.0, 58.4, 0.45)
# 12. mundo morto (58,98 a 66,5): pedal oco, quase nada, uma nota longe
m += pad([D2, A2], 59.0, 66.8, 0.1, 360, 0.002, 2.0, 2.0)
m += pad([nota(45), nota(52)], 60.0, 66.6, 0.06, 500, 0.003, 2.5, 2.0)
for t0, mid in ((61.0, 62), (63.2, 57), (65.3, 65)):
    m += pluck(nota(mid), t0, 0.12, 1.2, 1800)
# 13. o fim (66,5 a 72): cordas tristes, uma nota alta que some
m += pad([D2, A2, F2 * 2], 66.5, 72.0, 0.22, 1300, 0.003, 1.2, 2.5, vib=0.003)
m += pad([nota(86)], 68.0, 72.8, 0.07, 6000, 0.001, 1.5, 2.8, vib=0.008)
m += pluck(nota(74), 67.0, 0.2, 0.8, 2000) + pluck(nota(69), 69.2, 0.18, 0.8, 1800)

m *= np.clip(T / 0.05, 0, 1) * np.clip((TOT - T) / 1.5, 0, 1)
m = m / (np.abs(m).max() + 1e-9) * 0.7
# estéreo: um ar pequeno entre os lados e brilho de sala
d = int(0.009 * SR)
L = m + 0.15 * np.concatenate([np.zeros(d), m[:-d]]); R = m + 0.15 * np.concatenate([np.zeros(2 * d), m[:-2 * d]])
out = np.stack([L, R], 1); out = out / (np.abs(out).max() + 1e-9) * 0.8
if __name__ == "__main__":
    with wave.open(sys.argv[1], "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((np.clip(out, -1, 1) * 32767).astype("<i2").tobytes())
    print("ok", sys.argv[1], TOT)
