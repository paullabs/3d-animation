"""Acerta os tempos da decupagem da parte 2 do abrigo nas palavras da voz.
Lê personagem/abrigo/decupagem-parte2.md (seção "### N." = fala N do roteiro) e roteiros/voz-abrigo2/<voz>/palavras.json,
e reescreve a coluna Tempo de cada plano: o corte cai 2 quadros antes da 1ª palavra do plano (regra do ep. 1: ±2 quadros);
pausa "(pausa)" vai do fim da última palavra (+0,1 s) até o próximo corte. Também reescreve o tempo no título da seção.
python3 decupagem_tempos_abrigo2.py [teste]   (a pasta da voz; padrão: teste)"""
import json, os, re, sys, unicodedata

RAIZ = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
DOC = os.path.join(RAIZ, "personagem", "abrigo", "decupagem-parte2.md")
LEAD = 2 / 24


NUM = {"catorze": "14", "tres": "3"}
LEAD_MAX = 0.35                                   # a imagem chega no máximo 0,35 s antes da palavra


def norm(w):
    w = unicodedata.normalize("NFD", w.lower())
    w = re.sub(r"[^a-z0-9]", "", "".join(c for c in w if unicodedata.category(c) != "Mn"))
    return NUM.get(w, w)


def br(x):
    return f"{x:.1f}".replace(".", ",")


def main(voz="teste"):
    pasta = os.path.join(RAIZ, "roteiros", "voz-abrigo2", voz)
    P = json.load(open(os.path.join(pasta, "palavras.json")))
    total = json.load(open(os.path.join(pasta, "tempos.json")))["total"]
    por_fala = {}
    for w in P:
        por_fala.setdefault(w["frase"], []).append(w)
    linhas = open(DOC).read().split("\n")
    # 1ª passada: junta as linhas de plano de cada seção
    secoes = []; cur = None
    for i, l in enumerate(linhas):
        m = re.match(r"### (\d+)\. ", l)
        if m:
            cur = dict(n=int(m.group(1)), titulo=i, rows=[]); secoes.append(cur); continue
        if cur and l.startswith("| ") and not l.startswith("| Plano") and not l.startswith("|---"):
            cel = [c.strip() for c in l.strip().strip("|").split("|")]
            if len(cel) >= 3 and re.search(r"\d+,\d+ a \d+,\d+", cel[1]):
                cur["rows"].append(dict(i=i, cel=cel))
        if l.startswith("## ") and cur:
            cur = None
    # 2ª passada: começo de cada plano
    inicio = []                                     # (linha, t_inicio, é_pausa, fim_da_fala_anterior)
    for s in secoes:
        ws = por_fala[s["n"]]; ptr = 0
        for r in s["rows"]:
            pal = r["cel"][2]
            if "(pausa)" in pal or "(montagem)" in pal or pal in ("—", "-"):
                t = ws[ptr - 1]["t1"] + 0.1 if ptr else ws[0]["t0"] - 0.6
                inicio.append([r["i"], t, s, True])
                continue
            toks = [norm(x) for x in re.findall(r"[\wÀ-ú-]+", pal)]
            toks = [x for x in toks if x]
            alvo = toks[0]
            j = ptr
            while j < len(ws) and norm(ws[j]["txt"]) != alvo:
                j += 1
            if j == len(ws):
                raise SystemExit(f"plano da linha {r['i']+1}: não achei '{pal}' na fala {s['n']}")
            t = max(0.0, ws[j]["t0"] - LEAD)
            # se antes da palavra há silêncio (entre falas ou dentro da fala), o corte vai para o meio dele (a imagem
            # chega antes da voz, no máximo 0,35 s), senão o plano anterior engole o silêncio e passa de 1,3 s.
            # Depois de uma linha de pausa, não: a pausa é o plano dela.
            antes_pausa = inicio and inicio[-1][3]
            fim_ant = ws[j - 1]["t1"] if j else (por_fala[s["n"] - 1][-1]["t1"] if s["n"] - 1 in por_fala else None)
            if fim_ant is not None and not antes_pausa and ws[j]["t0"] - fim_ant > 0.3:
                t = max(min(t, (fim_ant + ws[j]["t0"]) / 2), ws[j]["t0"] - LEAD_MAX)
            ptr = j + len(toks)
            inicio.append([r["i"], t, s, False])
    inicio[0][1] = 0.0
    # 3ª passada: escreve
    for k, (li, t0, s, _) in enumerate(inicio):
        t1 = inicio[k + 1][1] if k + 1 < len(inicio) else total
        cel = [c.strip() for c in linhas[li].strip().strip("|").split("|")]
        cel[1] = f"{br(t0)} a {br(t1)}"
        linhas[li] = "| " + " | ".join(cel) + " |"
    fim_de = {li: (inicio[k + 1][1] if k + 1 < len(inicio) else total) for k, (li, *_r) in enumerate(inicio)}
    ini_de = {li: t for li, t, *_r in inicio}
    for s in secoes:
        ws = por_fala[s["n"]]
        a, b = ws[0]["t0"], ws[-1]["t1"]
        base = linhas[s["titulo"]].split(" (")[0]
        pz = [r for r in s["rows"] if "(pausa)" in r["cel"][2] or r["cel"][2] in ("—", "-")]
        extra = ""
        if pz and pz[-1] is s["rows"][-1]:
            extra = f" + pausa ({br(ini_de[pz[-1]['i']])} a {br(fim_de[pz[-1]['i']])} s)"
        elif pz:
            extra = f", com uma pausa de {br(fim_de[pz[0]['i']] - ini_de[pz[0]['i']])} s"
        linhas[s["titulo"]] = f"{base} ({br(a)} a {br(b)} s{extra})" if extra.startswith(",") else f"{base} ({br(a)} a {br(b)} s){extra}"
    open(DOC, "w").write("\n".join(linhas))
    durs = [(inicio[k + 1][1] if k + 1 < len(inicio) else total) - inicio[k][1] for k in range(len(inicio))]
    print(f"{len(inicio)} planos, total {total:.1f} s; menor {min(durs):.2f} s, maior {max(durs):.2f} s")
    for k, d in enumerate(durs):
        if d > 1.6 or d < 0.4:
            print("  atenção:", linhas[inicio[k][0]][:80], f"{d:.2f} s")


if __name__ == "__main__":
    main(*(sys.argv[1:2] or ["teste"]))
