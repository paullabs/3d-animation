"""Plano de som de "O abrigo" (pedido de 25/10/2026: "colocar efeitos sonoros"): um efeito por ação, no QUADRO da ação (não na palavra).
Os tempos saem do mesmo mapa de tempo da animação: t = (round(t0 * 24) + quadro - 1) / 24, com o quadro contado de 1 dentro do plano.
Um som próprio para cada ação, sem repetir arquivo (a variante vem do seed). Volume: 1 = tão forte quanto a voz.
python3 plano_som_abrigo.py   -> roteiros/som-abrigo/plano_som.json (depois: mixagem.py plano_som.json)"""
import os, sys, json, subprocess
AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.abspath(os.path.join(AQUI, ".."))
SOM = os.path.join(RAIZ, "roteiros", "som-abrigo")
SINT = os.path.join(SOM, "sint")
sys.path.insert(0, AQUI)
import sfx_abrigo as SX

META = json.load(open(os.path.join(SOM, "shots.json"))) if os.path.exists(os.path.join(SOM, "shots.json")) else None
if META is None:
    BL = __import__("canal38_env").BLENDER
    subprocess.run([BL, "-b", "-P", os.path.join(AQUI, "story3_abrigo.py"), "--", "--json", os.path.join(SOM, "shots.json")], capture_output=True, cwd=AQUI)
    META = json.load(open(os.path.join(SOM, "shots.json")))

EV, GERADOS = [], {}


def T(shot, f):
    return (round(META[shot]["t0"] * 24) + f - 1) / 24.0


def som(nome, seed=0, **kw):
    """gera (uma vez) a variante pedida e devolve o caminho"""
    chave = f"{nome}_{seed}_" + "_".join(f"{k}{v}" for k, v in sorted(kw.items()))
    if chave not in GERADOS:
        p = os.path.join(SINT, "v_" + chave.replace(".", "p").replace("-", "m") + ".wav")
        import inspect
        f = SX.ALL[nome]
        if "seed" in inspect.signature(f).parameters:
            kw = dict(kw, seed=seed)
        SX.grava(f(**kw), p); GERADOS[chave] = p
    return GERADOS[chave]


def E(shot, f, nome, vol=0.4, seed=0, golpe=False, dur=None, **kw):
    e = dict(som=som(nome, seed, **({"dur": kw["dur_som"]} if "dur_som" in kw else {}), **{k: v for k, v in kw.items() if k != "dur_som"}), t=round(T(shot, f), 3), vol=vol, shot=shot, nome=nome)
    if golpe:
        e["golpe"] = True
    if dur:
        e["dur"] = dur
    EV.append(e)


# v2 (25/10/2026, noite): "os efeitos ficaram altos, muitos barulhos aleatórios, a explosão tem que ser um som grave de distorção do espaço-tempo e a
# porta outro som grave, sem repetir": menos eventos (só o que a imagem mostra e que ajuda a contar), mais baixos, cada um com timbre próprio.
# ------------------------------------------------------------ 1. a corrida
E("1A", 1, "sirene", .2, 0, dur=6.0, dur_som=8.0)
E("1A", 1, "espaco_tempo", .75, 0, golpe=True, dur=9.5, dur_som=9.5)          # a dobra do espaço-tempo: cresce até o clarão (6,5 s) e some
E("1B", 4, "freio_bici", .28, 0)
E("1B", 8, "raspa_pe", .22, 0)
E("1C", 6, "queda_bici", .55, 0, golpe=True)
E("1C", 7, "sino", .22, 1, dur=1.4, dur_som=1.6)
E("1D", 1, "passos", .34, 3, dur=1.1, dur_som=1.1, passo=0.25, peso=1.0)
E("1D", 1, "ofegar", .28, 1, dur=1.1, dur_som=1.1, ritmo=2.4)
E("1E", 1, "multidao_corre", .3, 0, dur=1.3, dur_som=1.3)
E("1F", 3, "multidao_corre", .22, 1, dur=1.1, dur_som=1.2, n_pessoas=5)
# ------------------------------------------------------------ 2. a porta
E("2A", 14, "zumbido_ouvido", .1, 0, dur=2.5)
E("2B", 1, "porta_cofre", .75, 0, golpe=True, dur=2.4, dur_som=2.3)          # a folha corre, bate e os três ferrolhos caem (grave diferente da explosão)
E("2B", 26, "soca_aco", .34, 1)
E("2C", 1, "tranca_roda", .5, 0, dur=.75, dur_som=.72)
E("2D", 3, "soca_aco", .3, 3)
E("2D", 11, "soca_aco", .34, 5)
E("2D", 19, "soca_aco", .3, 7)
E("2D", 1, "gritos_perto", .22, 1, dur=1.8, dur_som=1.9)
E("2E", 6, "soca_aco", .42, 8)
E("2E", 12, "soca_aco", .4, 9)
E("2E", 20, "soca_aco", .42, 11)
E("2F", 3, "tapa_vidro", .24, 0)
E("2F", 16, "tapa_vidro", .22, 2)
E("2G", 7, "coracao", .22, 0, dur=1.0)
# ------------------------------------------------------------ 3. o abrigo antes
E("3A", 1, "tom_sala", .1, 1, dur=5.2, dur_som=5.2)
E("3B", 3, "lata_tinir", .2, 0)
E("3B", 11, "lata_tinir", .18, 1)
E("3C", 1, "agua_balanco", .26, 0, dur=0.6, dur_som=0.6)
E("3D", 1, "zumbido_luz", .18, 1, dur=1.0, dur_som=1.0)
E("3E", 7, "giz_risca", .3, 0, dur=.55, dur_som=.55)
E("3F", 1, "roer", .22, 0, dur=1.2, dur_som=1.2)
# ------------------------------------------------------------ 4. a comida acaba
for k, f in enumerate((4, 8, 12, 16, 20)):
    E("4A", f, "lata_some", .26, k)
for k, f in enumerate((4, 12, 20)):
    E("4A", f, "lampada_pisca", .3, k)
E("4B", 3, "garfo_prato", .2, 3)
E("4B", 14, "garfo_prato", .18, 4)
E("4C", 6, "garfo_raspa", .24, 0, dur=.5, dur_som=.5)
E("4D", 13, "lata_cai_rola", .5, 0, golpe=True, dur=1.5, dur_som=1.5)
E("4E", 2, "lapis", .2, 0, dur=.55, dur_som=.55)
# ------------------------------------------------------------ 5. o banheiro
E("5A", 9, "giz_risca", .3, 1, dur=.7, dur_som=.7)
E("5B", 1, "agua_chega", .28, 0, dur=1.0, dur_som=1.0)
E("5B", 1, "moscas", .16, 0, dur=1.0, dur_som=1.0)
E("5C", 1, "vaso_borbulha", .3, 0, dur=1.0, dur_som=1.0)
E("5D", 1, "gas_chia", .2, 0, dur=1.9, dur_som=1.9)
E("5E", 1, "choro_baixo", .22, 0, dur=1.1, dur_som=1.1)
# ------------------------------------------------------------ 6. o bichinho
E("6A", 1, "roer", .24, 1, dur=.85, dur_som=.9)
E("6A", 12, "pia", .24, 1)
E("6D", 5, "ranger_grade", .26, 0, dur=.5, dur_som=.5)
E("6E", 10, "pano", .24, 5, dur=.9, dur_som=.9, forca=1.2)
E("6F", 3, "coracao", .2, 1, dur=1.0)
E("6I", 5, "mastigar", .2, 3, dur=.9, dur_som=.9)
E("6J", 9, "mastigar", .2, 4, dur=.9, dur_som=.9)
E("6K", 6, "choro_baixo", .26, 1, dur=1.2, dur_som=1.2)
E("6K", 19, "pingo", .18, 1)
# ------------------------------------------------------------ 7. os meses e a morte
E("7A", 1, "relogio", .24, 0, dur=2.5, dur_som=2.5)
E("7A", 17, "lampada_pisca", .4, 4, golpe=True)
E("7B", 1, "estatica_cctv", .1, 0, dur=1.3, dur_som=1.3)
E("7D", 1, "estatica_cctv", .1, 1, dur=1.2, dur_som=1.2)
E("7E", 1, "coracao_para", .28, 0, dur=4.6, dur_som=4.5)
E("7F", 1, "respiro_lento", .24, 0, dur=.9, dur_som=3.0)
E("7F", 12, "ultimo_suspiro", .32, 0, dur=1.6, dur_som=2.2)
E("7G", 1, "tum", .45, 0, golpe=True, dur=2.0, dur_som=2.5)
# ------------------------------------------------------------ 8. o baralho
E("8A", 16, "carta", .3, 0)
E("8B", 16, "carta", .24, 1)
E("8C", 20, "carta", .28, 2)
# ------------------------------------------------------------ 9. a porta
E("9A", 9, "plastico", .22, 0, dur=.8, dur_som=.8)
E("9A", 10, "agua_balanco", .26, 1, dur=1.0, dur_som=1.0)
E("9B", 4, "gole", .26, 0, golpe=True)
E("9B", 10, "gole", .26, 1, golpe=True)
E("9B", 20, "pano", .16, 21, dur=.5, dur_som=.5)
E("9C", 1, "passos_botas", .4, 0, dur=1.3, dur_som=3.0)
E("9D", 1, "tranca_roda", .45, 1, dur=.9, dur_som=.8, reversa=True)
E("9D", 6, "ferrugem", .22, 0, dur=.8, dur_som=1.0)
E("9D", 12, "porta_range", .42, 0, dur=2.6, dur_som=2.6)
# ------------------------------------------------------------ 10. lá fora
E("10A", 1, "vento", .2, 0, dur=7.4, dur_som=8.0)
E("10C", 1, "passos_cinza", .3, 0, dur=1.2, dur_som=1.2)
E("10C", 9, "puff", .18, 0)
E("10D", 2, "sirene_range", .22, 0, dur=2.4, dur_som=2.4)
E("10F", 9, "escovar_po", .2, 0, dur=.9, dur_som=1.0)
E("10G", 3, "sino_seco", .42, 0, golpe=True, dur=2.0, dur_som=2.2)
E("11A", 1, "vento", .18, 1, dur=5.4, dur_som=8.0)
E("11D", 19, "escombro", .42, 0, dur=1.4, dur_som=1.4)                  # o barulho fora do quadro
E("11D", 31, "rosnado", .78, 0, golpe=True, dur=0.95, dur_som=2.0)     # o vulto desfocado rosna; acaba antes da voz do fecho (72,45 s)

EV.sort(key=lambda e: e["t"])
for e in EV:                                           # nenhum arquivo repetido: cada variante é única (nome + seed + parâmetros)
    pass
usados = [e["som"] for e in EV]
rep = {x for x in usados if usados.count(x) > 1}
assert not rep, f"efeito repetido: {sorted(os.path.basename(r) for r in rep)}"

plano = {
    "voz": os.path.join(RAIZ, "roteiros", "voz-abrigo", "narracao_final.wav"),
    "palavras": os.path.join(RAIZ, "roteiros", "voz-abrigo", "palavras_final.json"),
    "tempos": os.path.join(RAIZ, "roteiros", "voz-abrigo", "tempos_final.json"),
    "musica": os.path.join(SOM, "musica_dramatica.wav"),
    "musica_db": 0.0,
    "efeitos": [{k: v for k, v in e.items() if k not in ("shot", "nome")} for e in EV],
    "momentos": [{"t": 9.55, "nivel": 0.8}, {"t": 13.0, "nivel": 0.5}, {"t": 58.62, "nivel": 1.0}, {"t": 66.1, "nivel": 0.9}],
    "saida": os.path.join(SOM, "mix.wav"),
}
json.dump(plano, open(os.path.join(SOM, "plano_som.json"), "w"), ensure_ascii=False, indent=1)
json.dump([{k: e[k] for k in ("t", "shot", "nome", "vol")} for e in EV], open(os.path.join(SOM, "plano_som_lista.json"), "w"), ensure_ascii=False, indent=1)
print(len(EV), "efeitos,", len(set(usados)), "arquivos distintos; último em", EV[-1]["t"], "s")
