"""Trilha dramática de "O abrigo" (pedido de 25/10/2026: "não teve uma música dramática; troca de músicas, também dramáticas"):
costura TRECHOS das trilhas orquestrais que o Paulo já aprovou (Higgsfield sonilo_music, de graça porque já existem) e troca de música a cada cena,
com fusão curta nos cortes e silêncio onde o filme fica mudo ("Ele não abriu", "morreu."). A caixa de música do baralho é a sintetizada (musica_abrigo.py).
python3 musica_abrigo_mix.py SAIDA.wav [TOTAL_SEGUNDOS]"""
import sys, os, subprocess, wave
import numpy as np

SR = 48000
RAIZ = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
R = os.path.join(RAIZ, "roteiros")
FAIXAS = {
    "T": os.path.join(R, "som-presidente", "musica_tensa.m4a"),    # thriller orquestral, ostinato de cordas graves e tímpanos, três ondas
    "R": os.path.join(R, "som-reflexo", "musica.m4a"),             # orquestra romântica: pizzicato nervoso, tremolo escuro, nota suspensa, final nobre
    "C": os.path.join(R, "som-pcc7", "musica2.m4a"),               # quarteto de cordas, câmara, tensão em ondas
}
# (inicio no filme, fim no filme, faixa, inicio na faixa, ganho dB, fusão de entrada s, fusão de saída s)
CENAS = [
    (0.0, 6.55, "T", 11.0, 0, 0.0, 0.05),       # a explosão chega: o ostinato de cordas e tímpanos
    (7.6, 13.0, "T", 19.0, -2, 1.0, 0.3),       # a porta fecha: a tensão continua mais baixa (silêncio em 13,3: ele não abriu)
    (14.6, 19.7, "C", 3.0, -1, 1.2, 0.8),       # o abrigo "seguro": câmara, calma
    (19.7, 31.7, "R", 10.0, 0, 0.8, 0.0),       # a comida acaba e o cheiro: a orquestra cresce em ondas
    (31.7, 38.5, "R", 39.0, 0, 0.5, 0.5),       # a Pipoca some: a nota suspensa sobre o coração lento
    (38.5, 47.5, "C", 41.0, 0, 0.8, 1.0),       # o jantar sem coragem e os meses: câmara escura
    (47.5, 50.2, "R", 47.0, 0, 0.4, 0.6),       # a Lu morre: o final nobre das cordas
    (54.2, 59.0, "T", 51.0, 0, 0.8, 0.05),      # a porta se abre: a tensão sobe de novo
    (59.0, 66.5, "C", 48.0, 0, 0.1, 0.6),       # o mundo morto: câmara rarefeita
    (66.5, 70.7, "C", 55.0, 0, 0.6, 1.8),       # o fim: a corda baixa que fecha em acorde sem resolver; a música sai antes do fecho (só a voz)
]


def carrega(p):
    raw = subprocess.check_output(["ffmpeg", "-v", "error", "-i", p, "-ar", str(SR), "-ac", "2", "-f", "f32le", "-"])
    return np.frombuffer(raw, np.float32).reshape(-1, 2).copy()


def main(saida, total):
    n = int(total * SR); out = np.zeros((n, 2), np.float32); cache = {}
    for t0, t1, fx, ini, db, fi, fo in CENAS:
        if fx not in cache:
            cache[fx] = carrega(FAIXAS[fx])
        a = cache[fx]; i0 = int(ini * SR); m = int((t1 - t0) * SR)
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
    # a caixa de música do baralho (sintetizada, torta) por cima de 50,5 a 54,2
    cx = os.path.join(R, "som-abrigo", "musica_abrigo.wav")
    if os.path.exists(cx):
        b = carrega(cx); i0, i1 = int(50.4 * SR), int(54.4 * SR)
        seg = b[i0:i1] * 1.5; e = np.ones(len(seg)); k = int(0.4 * SR); e[:k] = np.linspace(0, 1, k); e[-k:] = np.linspace(1, 0, k)
        out[i0:i1] += seg * e[:, None]
    pk = np.abs(out).max(); out = out / pk * 0.8
    with wave.open(saida, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((np.clip(out, -1, 1) * 32767).astype("<i2").tobytes())
    print("ok", saida)


if __name__ == "__main__":
    main(sys.argv[1], float(sys.argv[2]) if len(sys.argv) > 2 else 73.2)
