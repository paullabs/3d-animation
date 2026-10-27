"""Mixagem do PCC v7: narração (Lucas) + música tensa (abaixa sozinha quando ele fala) + efeitos presos às palavras e aos cortes.
python3 mix_pcc7.py SAIDA.wav"""
import json, subprocess, sys, os
R = (__import__("canal38_env").RAIZ + "/roteiros")
VOZ = R + "/voz-pcc5"; SOM = R + "/som-pcc7"
PAL = json.load(open(VOZ + "/palavras.json")); TOT = json.load(open(VOZ + "/tempos.json"))["total"]
PLANOS = json.load(open(R + "/../render_pcc7/s0.5/planos.json"))


def w(frase, txt, fim=False):
    p = [x for x in PAL if x["frase"] == frase and x["txt"].strip(".,:;!?…").lower() == txt.lower()][0]
    return p["t1"] if fim else p["t0"]


# (efeito, segundo, volume): cada som cai na palavra ou na ação que a imagem mostra
EF = [("portao", w(1, "PCC", True) + 0.02, 0.7), ("notas", w(1, "salário") + 0.1, 0.4),
      ("sirene", w(4, "polícia") - 0.1, 0.32),
      ("notas", w(5, "700") - 0.05, 0.32),
      ("fichas", w(6, "42"), 0.3), ("grade", w(6, "isso", True) + 0.02, 0.65),
      ("fenda", w(7, "paga") + 0.1, 0.38),
      ("martelo", w(8, "crime", True) + 0.02, 0.55), ("martelo", w(8, "morte", True) + 0.03, 0.7),
      ("notas", w(9, "passando"), 0.38),
      ("tiro", w(10, "casa", True) + 0.03, 0.6),
      ("notas", w(11, "80%"), 0.32),
      ("coroa", w(12, "líder", True) + 0.02, 0.55),
      ("cela", w(13, "solto", True) + 0.03, 0.6),
      ("final", w(14, "subir", fim=True) + 0.05, 0.8)]           # efeitos fortes nas pausas, logo depois da palavra: nunca em cima dela
for n, (f0, f1) in sorted(PLANOS.items(), key=lambda kv: kv[1][0])[1:]:   # um whoosh discreto em cada corte em movimento
    EF.append(("whoosh", (f0 - 1) / 24 - 0.3, 0.2))


def main(out):
    ins = ["-i", VOZ + "/narracao.wav", "-i", SOM + "/musica.m4a"]
    fc = [f"[1:a]atrim=0:{TOT},asetpts=PTS-STARTPTS,afade=t=in:d=0.4,afade=t=out:st={TOT - 1.6}:d=1.6,volume=0.34[mus]",
          "[0:a]asplit=2[voz][sc]", "[mus][sc]sidechaincompress=threshold=0.025:ratio=8:attack=10:release=300[musd]"]
    tags = ["[voz]", "[musd]"]
    for i, (nome, t, v) in enumerate(EF):
        ins += ["-i", f"{SOM}/{nome}.mp3"]; k = i + 2
        fc.append(f"[{k}:a]volume={v},adelay={int(max(0, t) * 1000)}:all=1[e{i}]"); tags.append(f"[e{i}]")
    fc.append("".join(tags) + f"amix=inputs={len(tags)}:normalize=0:duration=first,alimiter=limit=0.95,loudnorm=I=-14:TP=-1.0:LRA=11[out]")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *ins, "-filter_complex", ";".join(fc), "-map", "[out]", "-ar", "48000", "-ac", "2", out], check=True)
    print("ok", out, len(EF), "efeitos")


if __name__ == "__main__":
    main(sys.argv[1])
