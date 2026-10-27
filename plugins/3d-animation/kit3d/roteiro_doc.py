"""Gera roteiros/ROTEIROS.md a partir dos JSON dos roteiros + tempos da voz + fontes.
python3 roteiro_doc.py"""
import json, os

R = (__import__("canal38_env").RAIZ + "/roteiros")
ORDEM = [("pcc", "1"), ("cartel", "2"), ("ditador", "3")]


def mmss(t):
    return f"{int(t // 60)}:{t % 60:04.1f}"


def main():
    fontes = json.load(open(os.path.join(R, "fontes.json"))) if os.path.exists(os.path.join(R, "fontes.json")) else {}
    out = ["# Roteiros: 3 histórias em 5 níveis", "",
           "Narração em português com a voz do Mac (Luciana). Como cada roteiro é montado:", "",
           "- **Gancho** (11 a 13 s): a primeira frase fala com quem assiste (\"Imagina...\") e traz a surpresa. A segunda diz de quem se trata. "
           "A terceira deixa uma dúvida que só o último nível responde.",
           "- **Cinco níveis**, cada um em uma ou duas frases completas, falando em \"você\": o papel, o que você faz e um detalhe concreto. "
           "O nome técnico fica na tela e na tabela; na fala usamos a palavra simples.",
           "- **Desfecho**: o preço do topo, em números que se enxergam, e uma pergunta para o público.",
           "- Sem frase solta, sem repetir o que a tela já mostra e sem termo difícil. A direção visual de cada bloco traduz a ideia em imagem.", "",
           "Tom: documental, sem glamourizar e sem ensinar a cometer crime.", "",
           "Fatos checados em 22/10/2026. A coluna Fonte mostra de onde vem cada fato; a lista com links fica no fim de cada roteiro. "
           "O que é relato de alguém aparece atribuído na própria fala (\"segundo o irmão dele\").", "",
           "Amostras de outras vozes do Mac para comparar: `roteiros/vozes-amostra/` (Luciana, Eddy, Reed, Rocko, Flo).", ""]
    for nome, num in ORDEM:
        S = json.load(open(os.path.join(R, f"{nome}.json")))
        T = json.load(open(os.path.join(R, f"voz-{nome}", "tempos.json")))
        out += [f"## {num}. {S['titulo']}", "",
                f"**Objetivo:** {S.get('objetivo', '')}", "",
                f"Duração da narração: **{T['total']:.0f} s** · áudio: `roteiros/voz-{nome}/narracao.wav` · clima: {S.get('clima', '')}", ""]
        k = 0
        for b in S["blocos"]:
            if b["nivel"] == 0:
                titulo = "Gancho"
            elif b["nivel"] == 6:
                titulo = "Desfecho: " + b["nome"]
            else:
                titulo = f"Nível {b['nivel']}: {b['nome']}" + (f" (nome técnico: {b['termo']})" if b.get("termo") else "")
            out += [f"### {titulo}", "", "| Tempo | Fala | Fonte |", "|---|---|---|"]
            for f in b["falas"]:
                it = T["falas"][k]; k += 1
                txt = f.get("legenda", f["fala"]) if isinstance(f, dict) else f
                fonte = f.get("fonte", "") if isinstance(f, dict) else ""
                out.append(f"| {mmss(it['inicio'])} | {txt} | {fonte} |")
            out += ["", "Imagem:"] + [f"- {v}" for v in b.get("visual", [])] + [""]
        fs = fontes.get(nome, [])
        if fs:
            out += ["**Fontes dos fatos citados**", ""] + [f"- {x}" for x in fs] + [""]
    open(os.path.join(R, "ROTEIROS.md"), "w").write("\n".join(out))
    print("ok", os.path.join(R, "ROTEIROS.md"))


if __name__ == "__main__":
    main()
