"""Voz-TESTE da parte 2 do abrigo (pedido de 26/10/2026: "vozes-teste primeiro, a ElevenLabs só no final").
Usa a voz do Mac (say), trecho por trecho, com as pausas da decupagem (personagem/abrigo/decupagem-parte2.md):
1,2 s depois de "tudo apagou", 0,5 s dentro da fala 7, 0,6 s depois dos ossos e de "catorze", 1,2 s para as batidas
e 1,0 s para a voz atrás do portão. A fala da torre ("quem nunca respirou...") sai com EQ de rádio, sem mexer no tom.
python3 voz_teste_abrigo2.py [--voz "Reed (Português (Brasil))"] [--taxa 190]
Gera roteiros/voz-abrigo2/teste/: trechos/tNN.aiff, narracao.wav, tempos.json (formato do voz.py); depois
python3 palavras.py ../roteiros/voz-abrigo2/teste  ->  palavras.json"""
import json, os, subprocess, sys

RAIZ = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
ROTEIRO = os.path.join(RAIZ, "roteiros", "abrigo2.json")
PASTA = os.path.join(RAIZ, "roteiros", "voz-abrigo2", "teste")
PAUSA_DEPOIS = {5: 1.2, 12: 0.6, 13: 0.6, 15: 1.2, 16: 1.0}       # fala (1..17) -> silêncio depois dela
CORTE = {1: ("Até aquela coisa", 3.0),                         # buraco para a montagem com glitch da abertura
         7: ("E alguém falou baixinho:", 0.5),                    # fala -> (onde parte, silêncio antes da 2ª parte)
         14: ("quem nunca respirou", 0.0)}
RADIO = {14: 1}                                                   # fala -> qual parte sai como rádio
RADIO_EQ = "highpass=f=450,lowpass=f=3200,acompressor=threshold=-20dB:ratio=6,volume=1.6"


def dur(p):
    return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p]).decode())


def partes(n, fala, legenda):
    if n not in CORTE:
        return [(fala, legenda, 0.0)]
    marca, sil = CORTE[n]
    i = fala.index(marca); j = legenda.index(marca)
    return [(fala[:i].strip(), legenda[:j].strip(), 0.0), (fala[i:].strip(), legenda[j:].strip(), sil)]


def main(voz, taxa):
    os.makedirs(os.path.join(PASTA, "trechos"), exist_ok=True)
    R = json.load(open(ROTEIRO))
    t = 0.35; itens = []; n = 0
    for bi, bloco in enumerate(R["blocos"]):
        for li, f in enumerate(bloco["falas"]):
            n += 1
            for pi, (txt, leg, sil) in enumerate(partes(n, f["fala"], f["legenda"])):
                t += sil
                k = len(itens) + 1
                limpo = os.path.join(PASTA, "trechos", f"t{k:02d}.aiff")
                subprocess.run(["say", "-v", voz, "-r", str(taxa), "-o", limpo, txt], check=True)
                som = limpo
                if RADIO.get(n) == pi:
                    som = os.path.join(PASTA, "trechos", f"t{k:02d}_radio.wav")
                    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", limpo, "-af", RADIO_EQ, som], check=True)
                d = dur(limpo)
                itens.append(dict(n=n, parte=pi, bloco=bi, texto=txt, legenda=leg, inicio=round(t, 3), duracao=round(d, 3),
                                  arquivo=limpo, som=som, radio=som != limpo))
                t += d
            fim_bloco = li == len(bloco["falas"]) - 1
            t += PAUSA_DEPOIS.get(n, 0.32 if fim_bloco else 0.14)
    total = t + 0.6
    cmd = ["ffmpeg", "-loglevel", "error", "-y"]; fl = []
    for i, it in enumerate(itens):
        cmd += ["-i", it["som"]]
        ms = int(it["inicio"] * 1000)
        fl.append(f"[{i}:a]aresample=44100,adelay={ms}|{ms}[a{i}]")
    fl.append("".join(f"[a{i}]" for i in range(len(itens))) + f"amix=inputs={len(itens)}:normalize=0,loudnorm=I=-16:TP=-1.5:LRA=11[out]")
    cmd += ["-filter_complex", ";".join(fl), "-map", "[out]", "-t", f"{total:.2f}", "-ar", "44100", os.path.join(PASTA, "narracao.wav")]
    subprocess.run(cmd, check=True)
    json.dump(dict(titulo=R["titulo"], voz=voz, taxa=taxa, teste=True, total=round(total, 2), falas=itens),
              open(os.path.join(PASTA, "tempos.json"), "w"), ensure_ascii=False, indent=1)
    print(f"{len(itens)} trechos, {total:.1f} s, voz {voz}, taxa {taxa}")


if __name__ == "__main__":
    a = sys.argv[1:]
    main(a[a.index("--voz") + 1] if "--voz" in a else "Reed (Português (Brasil))",
         int(a[a.index("--taxa") + 1]) if "--taxa" in a else 190)
