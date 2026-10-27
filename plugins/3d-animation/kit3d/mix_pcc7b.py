"""Mixagem do PCC v7b: voz na frente, música clássica sutil com camadas de volume, efeitos baixos.
Camadas da música (ganho relativo, voz = 1,0):
  - fala: 0,07 (quase só uma cama) e sobe devagar de 0,07 a 0,10 com o nível de tensão;
  - pausas entre falas (> 0,25 s): sobe para 0,20 em 0,25 s e desce de novo quando a voz volta;
  - momentos fortes ("morte", "líder", "só um tá solto", fim): sobe para 0,32 e cai antes da próxima palavra;
  - abertura (0 a 0,4 s) e cauda final: 0,34.
Efeitos: 25 a 40% do volume da primeira mixagem; nunca em cima da palavra.
python3 mix_pcc7b.py SAIDA.wav"""
import json, subprocess, sys
import numpy as np
import mix_pcc7 as M1

SR = 48000
R = M1.R; SOM = M1.SOM; VOZ = M1.VOZ; TOT = M1.TOT
PAL = M1.PAL; w = M1.w
T = json.load(open(VOZ + "/tempos.json"))


def carrega(path, mono=False):
    raw = subprocess.check_output(["ffmpeg", "-v", "error", "-i", path, "-ar", str(SR), "-ac", "2", "-f", "f32le", "-"])
    a = np.frombuffer(raw, np.float32).reshape(-1, 2)
    return a


def suave(x, tau):
    """filtro de um polo (ataque/queda suaves), tau em segundos"""
    a = np.exp(-1.0 / (tau * SR)); y = np.empty_like(x); s = x[0]
    for i in range(len(x)):
        s = a * s + (1 - a) * x[i]; y[i] = s
    return y


def main(out):
    n = int((TOT + 0.3) * SR)
    voz = carrega(VOZ + "/narracao.wav"); voz = np.pad(voz, ((0, max(0, n - len(voz))), (0, 0)))[:n]
    mus = carrega(SOM + "/musica2.m4a"); mus = np.pad(mus, ((0, max(0, n - len(mus))), (0, 0)))[:n]
    mus *= 0.1 / (np.sqrt((mus ** 2).mean()) + 1e-9) / 0.1 * np.sqrt((voz ** 2).mean() + 1e-12) * 1.0   # música com o mesmo RMS da voz; o ganho vem da curva
    t = np.arange(n) / SR
    env = suave((mus ** 2).mean(axis=1), 1.2); mus /= np.sqrt(np.maximum(env, np.percentile(env, 30)))[:, None]; mus *= np.sqrt((voz ** 2).mean() / ((mus ** 2).mean() + 1e-12))
    # máscara de fala por frase (da primeira à última palavra)
    fala = np.zeros(n)
    for f in T["falas"]:
        fala[int(f["inicio"] * SR):int((f["inicio"] + f["duracao"]) * SR)] = 1
    # pausas reais: dentro de uma frase, palavras separadas por mais de 0,25 s
    for a, b in zip(PAL, PAL[1:]):
        if b["t0"] - a["t1"] > 0.25:
            fala[int(a["t1"] * SR):int(b["t0"] * SR)] = 0
    fora = 1 - fala
    base = 0.07 + 0.03 * np.clip(t / TOT, 0, 1)                          # a tensão sobe devagar
    g = base + fora * (0.20 - base)                                       # sobe nas pausas
    for t0, t1, v in [(0.0, 0.4, 0.34), (w(8, "morte", True), w(8, "morte", True) + 0.9, 0.32), (w(12, "líder", True), w(12, "líder", True) + 0.8, 0.30),
                      (w(13, "solto", True), w(13, "solto", True) + 0.5, 0.30), (T["falas"][-1]["inicio"] + T["falas"][-1]["duracao"], TOT + 0.3, 0.34)]:
        g[int(t0 * SR):int(t1 * SR)] = np.maximum(g[int(t0 * SR):int(t1 * SR)], v)
    g = suave(g, 0.18)                                                    # sobe e desce sem degrau
    fade = np.clip((TOT + 0.2 - t) / 1.4, 0, 1)
    mus *= (g * fade)[:, None]
    mix = voz + mus
    MUS = mus.copy(); EFX = np.zeros_like(mix)
    # efeitos: curtos, baixos, ancorados nas pausas
    esc = 0.32
    for nome, ts, v in M1.EF:
        e = carrega(f"{SOM}/{nome}.mp3")
        e = e * (v * esc) * np.sqrt((voz ** 2).mean()) / (np.sqrt((e ** 2).mean()) + 1e-9) * 0.9
        lim = 0.3 * np.abs(voz).max()                                      # nenhum pico de efeito passa de 30% do pico da voz
        if np.abs(e).max() > lim:
            e = e * lim / np.abs(e).max()
        i = int(max(0, ts) * SR); j = min(n, i + len(e))
        mix[i:j] += e[:j - i]; EFX[i:j] += e[:j - i]
    db = lambda x: 20 * np.log10(np.sqrt((x ** 2).mean()) + 1e-12)
    fl = np.zeros(n, bool)
    for f in T['falas']:
        fl[int(f['inicio'] * SR):int((f['inicio'] + f['duracao']) * SR)] = True
    print('sob a fala: música %.1f dB, efeitos(pico) %.1f dB em relação à voz' % (db(MUS[fl]) - db(voz[fl]), 20 * np.log10(np.abs(EFX).max() / np.abs(voz).max())))
    print('música nas pausas: %.1f dB' % (db(MUS[~fl & (t < TOT)]) - db(voz[fl])), '| pico da música: %.1f dB' % (20 * np.log10(np.abs(MUS).max() / np.abs(voz).max())))
    pico = np.abs(mix).max()
    mix *= 0.89 / pico if pico > 0.89 else 1
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", "-", "-af", "loudnorm=I=-15:TP=-1.5:LRA=9", "-ar", str(SR), out],
                   input=mix.astype(np.float32).tobytes(), check=True)
    print("ok", out)


if __name__ == "__main__":
    main(sys.argv[1])
