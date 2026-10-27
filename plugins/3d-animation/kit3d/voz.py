"""Voz do narrador com a voz do Mac (comando say), frase por frase.
python3 voz.py roteiro.json PASTA_SAIDA [--voz "Luciana"] [--taxa 185]
Gera: frases/fNN.aiff, narracao.wav (frases com pausas), tempos.json (início e duração de cada frase, para animar)."""
import json, subprocess, sys, os


def dur(path):
    return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path]).decode())


def falar(texto, voz, taxa, out):
    subprocess.run(["say", "-v", voz, "-r", str(taxa), "-o", out, texto], check=True)


def gerar(roteiro, pasta, voz="Luciana", taxa=195, pausa_frase=0.14, pausa_bloco=0.32):
    os.makedirs(os.path.join(pasta, "frases"), exist_ok=True)
    R = json.load(open(roteiro))
    t = 0.35; itens = []; lista = []
    sil = os.path.join(pasta, "frases", "sil.wav")
    for bi, bloco in enumerate(R["blocos"]):
        for li, frase in enumerate(bloco["falas"]):
            n = len(itens) + 1
            legenda = frase.get("legenda", frase["fala"]) if isinstance(frase, dict) else frase
            frase = frase["fala"] if isinstance(frase, dict) else frase
            a = os.path.join(pasta, "frases", f"f{n:02d}.aiff")
            falar(frase, voz, taxa, a)
            d = dur(a)
            itens.append(dict(n=n, bloco=bi, nivel=bloco.get("nivel"), texto=frase, legenda=legenda, inicio=round(t, 3), duracao=round(d, 3), arquivo=a))
            t += d + (pausa_bloco if li == len(bloco["falas"]) - 1 else pausa_frase)
    total = t + 0.6
    # monta a narração inteira com as pausas certas
    cmd = ["ffmpeg", "-loglevel", "error", "-y"]
    fl = []
    for i, it in enumerate(itens):
        cmd += ["-i", it["arquivo"]]
        ms = int(it["inicio"] * 1000)
        fl.append(f"[{i}:a]aresample=44100,adelay={ms}|{ms}[a{i}]")
    fl.append("".join(f"[a{i}]" for i in range(len(itens))) + f"amix=inputs={len(itens)}:normalize=0,loudnorm=I=-16:TP=-1.5:LRA=11[out]")
    cmd += ["-filter_complex", ";".join(fl), "-map", "[out]", "-t", f"{total:.2f}", "-ar", "44100", os.path.join(pasta, "narracao.wav")]
    subprocess.run(cmd, check=True)
    json.dump(dict(titulo=R["titulo"], voz=voz, taxa=taxa, total=round(total, 2), falas=itens),
              open(os.path.join(pasta, "tempos.json"), "w"), ensure_ascii=False, indent=1)
    return total, itens


if __name__ == "__main__":
    a = sys.argv[1:]
    voz = a[a.index("--voz") + 1] if "--voz" in a else "Luciana"
    taxa = int(a[a.index("--taxa") + 1]) if "--taxa" in a else 185
    total, itens = gerar(a[0], a[1], voz, taxa)
    print(f"{a[0]}: {len(itens)} frases, {total:.1f} s, voz {voz}")
