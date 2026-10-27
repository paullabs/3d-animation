"""Mixagem com guarda de voz: a voz manda; música e efeitos nunca competem com ela.

python3 mixagem.py plano_som.json
plano_som.json:
{
  "voz": "…/narracao.wav", "palavras": "…/palavras.json", "tempos": "…/tempos.json",
  "musica": "…/musica.m4a",
  "efeitos": [{"som": "…/portao.mp3", "t": 1.98, "vol": 0.8}, …],      # vol de 0 a 1 (1 = pico a 25% do pico da voz)
  "momentos": [{"t": 35.95, "nivel": 1.0}, …],                          # subida da música numa pausa (depois de "morte", "líder"…)
  "saida": "…/mix.wav"
}

Camadas da música (relativas ao RMS da voz; a música é achatada antes, então nenhum trecho dela é mais alto que outro):
  - debaixo da fala: -27 dB, subindo devagar até -25 dB no fim (a tensão cresce sem aparecer);
  - pausa entre frases: -18 dB;
  - momento forte: -14 dB, e SÓ dentro da pausa — termina 0,3 s antes da próxima palavra;
  - abertura e cauda final: -13 dB.
Guarda de voz (por cima da curva): em janelas de 300 ms, com voz, a música fica 20 dB abaixo da voz daquele instante;
sem voz, nunca passa de -12 dB da voz média. O relatório no fim mostra os números medidos e acusa qualquer violação.
Efeitos (v2, 23/10/2026 — "os efeitos quase não dá para ouvir"): o volume é medido pela ENERGIA do som, não pelo pico
(um envelope ou uma nota curta com pico alto soava fraquíssimo). vol 1 = tão forte quanto a voz; nas pausas eles soam
cheios (0,6 a 1,0) e, enquanto a voz fala, um limitador abaixa só o efeito para ficar 12 dB abaixo dela.
O começo mudo de cada arquivo é cortado (o golpe cai no tempo certo) e cada efeito tem duração máxima (dur, padrão 3 s)."""
import json, subprocess, sys
import numpy as np

SR = 48000
DB = lambda x: 20 * np.log10(max(float(x), 1e-12))
G = lambda db: 10 ** (db / 20)
CAMA_FALA, CAMA_FIM, CAMA_PAUSA, SUBIDA, PONTAS = G(-26), G(-24), G(-16), G(-11), G(-11)
GUARDA_FALA, GUARDA_PAUSA = G(-20), G(-12)
EF_FALA = G(-8)                  # efeito enquanto a voz fala: 8 dB abaixo dela (a -12 sumiam: "vários efeitos não estão acontecendo")
EF_GOLPE = G(-5)                 # golpe curto (martelo, grade, impacto) em cima da fala: 5 dB abaixo


def carrega(path):
    raw = subprocess.check_output(["ffmpeg", "-v", "error", "-i", path, "-ar", str(SR), "-ac", "2", "-f", "f32le", "-"])
    return np.frombuffer(raw, np.float32).reshape(-1, 2).copy()


def suave(x, tau):
    a = np.exp(-1.0 / (tau * SR)); y = np.empty_like(x); s = x[0]
    for i in range(len(x)):
        s = a * s + (1 - a) * x[i]; y[i] = s
    return y


def antes(x, tau):
    """suaviza sem atrasar a descida: o mínimo entre suavizar para a frente e para trás.
    Assim a música já está baixa quando a voz entra e só volta a subir depois que a voz sai."""
    return np.minimum(suave(x, tau), suave(x[::-1], tau)[::-1])


def rms_janela(x, jan=0.3):
    """RMS em janela deslizante (mono)"""
    m = (x ** 2).mean(axis=1) if x.ndim == 2 else x ** 2
    k = int(jan * SR); c = np.cumsum(np.concatenate([[0], m]))
    r = (c[k:] - c[:-k]) / k
    r = np.concatenate([np.full(k // 2, r[0]), r, np.full(len(m) - len(r) - k // 2, r[-1])])
    return np.sqrt(np.maximum(r, 0))


def mascara_fala(pal, n, junta=0.25):
    """1 onde há fala (palavras, juntando buracos menores que 'junta' s)"""
    m = np.zeros(n, bool); ws = sorted((w["t0"], w["t1"]) for w in pal)
    a0, a1 = ws[0]
    for b0, b1 in ws[1:] + [(1e9, 1e9)]:
        if b0 - a1 <= junta:
            a1 = max(a1, b1); continue
        m[int(a0 * SR):int(a1 * SR)] = True; a0, a1 = b0, b1
    return m


def main(plano_path):
    P = json.load(open(plano_path))
    md = G(P.get("musica_db", 0.0))          # ajuste da música inteira (ex.: +3 = "a música pode aumentar um pouco")
    pal = json.load(open(P["palavras"])); T = json.load(open(P["tempos"])); TOT = T["total"]
    voz = carrega(P["voz"]); n = int((TOT + 0.3) * SR)
    voz = np.pad(voz, ((0, max(0, n - len(voz))), (0, 0)))[:n]
    mus = carrega(P["musica"]); mus = np.pad(mus, ((0, max(0, n - len(mus))), (0, 0)))[:n]
    t = np.arange(n) / SR
    fala = mascara_fala(pal, n)
    pre = fala.copy()
    for w in pal:
        pre[max(0, int((w["t0"] - 0.3) * SR)):int(w["t0"] * SR)] = True     # pré-fala: a música já desce antes
    v_rms = np.sqrt((voz[fala] ** 2).mean())

    # 1) música meio achatada (2:1): o crescendo não atropela a voz, mas a onda de tensão continua lá; a guarda faz o resto
    env = suave((mus ** 2).mean(axis=1), 1.0)
    mus = mus / np.maximum(env, np.percentile(env, 25))[:, None] ** 0.25     # meio achatada: as ondas de tensão ficam (v1 achatava tudo)
    mus *= v_rms / (np.sqrt((mus ** 2).mean()) + 1e-12)

    # 2) curva de camadas
    g = md * np.where(pre, CAMA_FALA + (CAMA_FIM - CAMA_FALA) * np.clip(t / TOT, 0, 1), CAMA_PAUSA)
    inicios = np.array(sorted(w["t0"] for w in pal))
    primeira, ultima = inicios[0], max(w["t1"] for w in pal)
    g[t < primeira - 0.15] = md * PONTAS; g[t > ultima + 0.1] = md * PONTAS
    for m in P.get("momentos", []):
        prox = inicios[inicios > m["t"] + 0.05]
        fim = (prox[0] - 0.3) if len(prox) else TOT
        if fim > m["t"]:
            i0, i1 = int(m["t"] * SR), int(fim * SR)
            g[i0:i1] = np.maximum(g[i0:i1], md * (CAMA_PAUSA + (SUBIDA - CAMA_PAUSA) * m.get("nivel", 1.0)))
    g = antes(g, 0.15)                                   # desce ANTES da palavra, sobe depois dela

    # 3) guarda de voz: limite instantâneo, com ataque rápido e soltura lenta
    v_env = rms_janela(voz, 0.3)
    lim = np.where(pre, np.maximum(v_env, 0.3 * v_rms) * GUARDA_FALA * min(md, G(3)), v_rms * GUARDA_PAUSA * md)
    m_env = rms_janela(mus * g[:, None], 0.3) + 1e-9
    k = np.minimum(1.0, lim / m_env)
    k = antes(k, 0.12)
    fade = np.clip((TOT + 0.2 - t) / 1.4, 0, 1)
    mus_f = mus * (g * k * fade)[:, None]

    # 4) efeitos: volume pela energia, começo mudo cortado, duração máxima e limitador só enquanto a voz fala
    # dois barramentos: "golpe" (martelo, grade, impacto: curto, atravessa a voz a 5 dB abaixo dela) e o resto (12 dB abaixo)
    barr = {False: np.zeros_like(voz), True: np.zeros_like(voz), 2: np.zeros_like(voz)}; vpk = np.abs(voz).max()
    for e in P.get("efeitos", []):
        a = carrega(e["som"])
        amp = np.abs(a).max(axis=1); ini = int(np.argmax(amp > amp.max() * 0.06))
        a = a[max(0, ini - int(0.004 * SR)):]
        dur = int(e.get("dur", 3.0) * SR)
        if len(a) > dur:
            a = a[:dur]; fo = min(len(a), int(0.35 * SR)); a[-fo:] *= np.linspace(1, 0, fo)[:, None]
        energia = rms_janela(np.pad(a, ((0, max(0, int(0.4 * SR) - len(a))), (0, 0))), 0.15).max() + 1e-9   # som curtinho: mede com folga
        a = a * (e.get("vol", 0.6) * v_rms / energia)
        i = int(max(0, e["t"]) * SR); j = min(n, i + len(a))
        barr[2 if e.get("livre") else bool(e.get("golpe"))][i:j] += a[:j - i]       # "livre": sem limitador (o golpe de câmera lenta, com a voz abaixando junto: duck_voz)
    v_env15 = rms_janela(voz, 0.15)
    kd = int(0.05 * SR); fala_d = fala | np.roll(fala, kd) | np.roll(fala, -kd)
    def limita(x, teto):
        # só onde a voz está soando de fato (fala + 50 ms): no respiro antes da palavra o efeito toca inteiro
        # (a v2 limitava também a pré-fala e com piso 0,3 x voz: um efeito na pausa de 0,2 s caía a -28 dB e sumia)
        lim_e = np.where(fala_d, np.maximum(v_env15, 0.6 * v_rms) * teto, 1e9)
        k_raw = np.minimum(1.0, lim_e / (rms_janela(x, 0.15) + 1e-9))
        b = SR // 100; nb = len(k_raw) // b                        # mínimo em blocos de 10 ms com folga de ±80 ms
        kb = k_raw[:nb * b].reshape(nb, b).min(axis=1)
        kb = np.min(np.stack([np.roll(kb, d) for d in range(-8, 9)]), axis=0)
        k_e = antes(np.interp(np.arange(len(k_raw)), np.arange(nb) * b + b / 2, kb), 0.02)
        return x * k_e[:, None]
    efx_lim = limita(barr[False], EF_FALA) + limita(barr[True], EF_GOLPE)
    efx = efx_lim + barr[2]
    # duck_voz: [{"t": 2.14, "dur": 0.3, "db": -6}]: a voz abaixa só nesse trecho (ataque/solta de ~25 ms) para o golpe grave aparecer em qualquer caixa
    duck = np.ones(n)
    for d in P.get("duck_voz", []):
        duck[int(d["t"] * SR):int((d["t"] + d.get("dur", 0.3)) * SR)] = G(d.get("db", -6))
    duck = 1 - suave(1 - duck, 0.025)

    mix = voz * duck[:, None] + mus_f + efx
    pk = np.abs(mix).max(); mix *= 0.89 / pk if pk > 0.89 else 1

    # 5) relatório medido
    me = rms_janela(mus_f, 0.3); ve = rms_janela(voz, 0.3)
    sob = DB(np.sqrt((mus_f[fala] ** 2).mean())) - DB(v_rms)
    pausa = DB(np.sqrt((mus_f[~fala & (t < TOT)] ** 2).mean())) - DB(v_rms)
    difs = [(DB(me[i]) - DB(v_rms), i / SR) for i in range(0, n, SR // 20) if fala[i]]          # contra o volume médio da voz
    pior, t_pior = max(difs)
    print("piores instantes:", ", ".join(f"{d:.1f} dB em {tt:.2f} s" for d, tt in sorted(difs)[-4:]))
    ee = rms_janela(efx_lim, 0.15); ee_all = rms_janela(efx, 0.15)           # o guarda mede só o que o limitador segura; o "livre" é de propósito
    kk = int(0.08 * SR); miolo = fala & np.roll(fala, kk) & np.roll(fala, -kk)      # sem a borda da palavra (a janela vaza)
    ef_fala = DB((ee[miolo] / np.maximum(v_env15[miolo], 0.6 * v_rms)).max()) if efx.any() else -99
    ef_pausa = DB(ee_all[~pre].max()) - DB(v_rms) if efx.any() else -99
    print(f"música sob a fala: {sob:.1f} dB | nas pausas: {pausa:.1f} dB | pior instante com voz: {pior:.1f} dB")
    print(f"efeitos: mais forte numa pausa {ef_pausa:+.1f} dB | mais forte com voz {ef_fala:+.1f} dB (rel. à voz)")
    fracos = []
    for e in P.get("efeitos", []):                       # cada efeito tem de se ouvir: contra a voz que toca na mesma hora
        i = int(max(0, e["t"]) * SR); j = min(n, i + int(0.6 * SR))
        d = DB(ee_all[i:j].max()) - DB(v_rms)
        if d < -11 and e.get("vol", 0.6) >= 0.45:
            fracos.append(f"{e['som'].split('/')[-1]} @{e['t']:.2f}s {d:+.0f} dB")
    print("efeitos que podem sumir:", ", ".join(fracos) if fracos else "nenhum")
    if efx.any():
        rr = ee / np.maximum(v_env15, 0.6 * v_rms); rr[~miolo] = 0; ip = int(np.argmax(rr))
        print(f"  efeito mais forte sobre a voz em {ip / SR:.2f} s")
    for m in P.get("momentos", []):
        i0 = int(m["t"] * SR); print(f"  subida em {m['t']:.2f} s: {DB(me[i0:i0 + int(0.6 * SR)].max()) - DB(v_rms):.1f} dB")
    folga = min(P.get("musica_db", 0.0), 3.0)
    ok = sob <= -23 + folga and pior <= -17 + folga and ef_fala <= -3.0
    print("GUARDA OK" if ok else "GUARDA FALHOU: algo compete com a voz")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", "-",
                    "-af", "loudnorm=I=-15:TP=-1.5:LRA=9", "-ar", str(SR), P["saida"]], input=mix.astype(np.float32).tobytes(), check=True)
    print("ok", P["saida"])
    return ok


if __name__ == "__main__":
    sys.exit(0 if main(sys.argv[1]) else 1)
