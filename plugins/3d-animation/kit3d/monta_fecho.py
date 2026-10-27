"""Junta a fala do fecho (a pergunta do narrador 3D) à narração aprovada: narracao_final.wav, palavras_final.json e tempos_final.json.
python3 monta_fecho.py FECHO.wav [PALAVRAS_DO_FECHO.json]     (o json vem do mlx_whisper --word-timestamps; sem ele, usa as pausas do áudio)
O fecho entra em INICIO_FECHO (s) depois do último quadro da corrida, com meio segundo de silêncio depois do "(fim)" escuro."""
import sys, os, json, subprocess, wave
import numpy as np

SR = 48000
RAIZ = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
V = os.path.join(RAIZ, "roteiros", "voz-abrigo")
INICIO_FECHO = 72.45                                  # depois do barulho, das cabeças que viram e do rosnado (25/10/2026)


def carrega(p):
    raw = subprocess.check_output(["ffmpeg", "-v", "error", "-i", p, "-ar", str(SR), "-ac", "2", "-f", "f32le", "-"])
    return np.frombuffer(raw, np.float32).reshape(-1, 2).copy()


def main(fecho, jpal=None):
    base = carrega(os.path.join(V, "narracao.wav")); f = carrega(fecho)
    # tira o silêncio do começo e do fim do fecho
    amp = np.abs(f).max(axis=1); idx = np.where(amp > amp.max() * 0.03)[0]
    f = f[max(0, idx[0] - int(0.05 * SR)): idx[-1] + int(0.15 * SR)]
    # a voz do fecho no mesmo nível da narração (RMS de fala)
    def rms_fala(x):
        a = np.abs(x).max(axis=1); return np.sqrt((x[a > a.max() * 0.05] ** 2).mean())
    f = f * (rms_fala(base) / rms_fala(f))
    i0 = int(INICIO_FECHO * SR); n = i0 + len(f) + int(0.12 * SR)
    out = np.zeros((n, 2), np.float32); out[:len(base)] += base; out[i0:i0 + len(f)] += f
    with wave.open(os.path.join(V, "narracao_final.wav"), "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(out, -1, 1) * 32767).astype("<i2").tobytes())
    pal = json.load(open(os.path.join(V, "palavras.json")))
    ini_f = idx[0] - max(0, idx[0] - int(0.05 * SR))                               # onde o 1º som cai dentro do trecho cortado (s)
    cortado0 = max(0, idx[0] - int(0.05 * SR)) / SR
    novas = []
    if jpal and os.path.exists(jpal):
        d = json.load(open(jpal))
        for seg in d["segments"]:
            for w in seg.get("words", []):
                novas.append(dict(txt=w["word"].strip(), t0=round(INICIO_FECHO + w["start"] - cortado0, 3), t1=round(INICIO_FECHO + w["end"] - cortado0, 3), frase=99))
    else:
        novas.append(dict(txt="fecho", t0=INICIO_FECHO, t1=INICIO_FECHO + len(f) / SR, frase=99))
    json.dump(pal + novas, open(os.path.join(V, "palavras_final.json"), "w"), ensure_ascii=False, indent=1)
    json.dump(dict(titulo="O abrigo (com o fecho)", voz="narracao_final.wav", total=round(n / SR, 3), fecho_t0=INICIO_FECHO, fecho_dur=round(len(f) / SR, 3)),
              open(os.path.join(V, "tempos_final.json"), "w"), indent=1)
    print("ok: total", round(n / SR, 2), "s; fecho de", round(INICIO_FECHO, 2), "a", round(INICIO_FECHO + len(f) / SR, 2))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
