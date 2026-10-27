"""Trilha de "os passos" (pedido de 26/10/2026: "faz o som, trilha e um efeito por ação"): costura TRECHOS das trilhas orquestrais que o Paulo já aprovou
(Higgsfield sonilo_music; de graça porque já existem), trocando de música quando a escala muda, com fusão curta:
  0 a 21,5 s   a orquestra romântica, pizzicato nervoso e curioso (ele cresce e não entende);
  21,5 a 38,8  o meio escuro da mesma peça: o corpo, o cabelo, o coração (as contas);
  38,8 a 52,8  o ostinato de cordas graves e tímpanos do thriller: os passos aceleram, a cidade encolhe;
  52,8 a 59,1  câmara rarefeita: o ar fica fino;
  59,1 a 72,2  a nota suspensa sobre o espaço (o terço final da orquestra romântica);
  72,2 a 83,0  o final nobre das cordas e a corda baixa que fecha em acorde sem resolver.
python3 musica_passos_mix.py SAIDA.wav [TOTAL_SEGUNDOS]"""
import sys, os, subprocess, wave
import numpy as np

SR = 48000
RAIZ = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
R = os.path.join(RAIZ, "roteiros")
FAIXAS = {
    "T": os.path.join(R, "som-presidente", "musica_tensa.m4a"),
    "R": os.path.join(R, "som-reflexo", "musica.m4a"),
    "C": os.path.join(R, "som-pcc7", "musica2.m4a"),
}
# (inicio no filme, fim no filme, faixa, inicio na faixa, ganho dB, fusão de entrada s, fusão de saída s)
CENAS = [
    (0.0, 21.5, "R", 0.0, 0, 0.0, 0.8),
    (21.5, 38.8, "R", 21.5, 0, 0.8, 0.5),
    (38.8, 52.8, "T", 12.0, -1, 0.5, 0.6),
    (52.8, 59.1, "C", 8.0, -1, 0.8, 0.8),
    (59.1, 72.2, "R", 36.0, 0, 1.0, 0.6),
    (72.2, 83.0, "R", 43.0, 0, 0.6, 0.0),
]


def carrega(p):
    raw = subprocess.check_output(["ffmpeg", "-v", "error", "-i", p, "-ar", str(SR), "-ac", "2", "-f", "f32le", "-"])
    return np.frombuffer(raw, np.float32).reshape(-1, 2).copy()


def main(saida, total):
    n = int(total * SR); out = np.zeros((n, 2), np.float32); cache = {}
    for t0, t1, fx, ini, db, fi, fo in CENAS:
        if fx not in cache:
            cache[fx] = carrega(FAIXAS[fx])
        a = cache[fx]; i0 = int(ini * SR); m = int((min(t1, total) - t0) * SR)
        seg = a[i0:i0 + m]
        if len(seg) < m:
            seg = np.pad(seg, ((0, m - len(seg)), (0, 0)))
        seg = seg * 10 ** (db / 20)
        env = np.ones(m)
        if fi > 0:
            k = min(m, int(fi * SR)); env[:k] = np.sin(np.linspace(0, np.pi / 2, k)) ** 2
        else:
            env[:int(0.01 * SR)] = np.linspace(0, 1, int(0.01 * SR))
        k = min(m, int(max(fo, 0.02) * SR)); env[-k:] *= np.cos(np.linspace(0, np.pi / 2, k)) ** 2
        j = int(t0 * SR); out[j:j + m] += seg * env[:, None]
    pk = np.abs(out).max(); out = out / pk * 0.8
    with wave.open(saida, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((out * 32767).astype("<i2").tobytes())


if __name__ == "__main__":
    main(sys.argv[1], float(sys.argv[2]) if len(sys.argv) > 2 else 83.0)
    print("ok", sys.argv[1])
