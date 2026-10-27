"""Plano de som de "os passos" (pedido de 26/10/2026: "faz o som, trilha e um efeito por ação"). Um efeito por ação que a imagem mostra, no instante da ação
(os tempos são os da animação v15: a pisada cai na palavra do número, a caixa acende na palavra da medida). Nenhum arquivo se repete (cada variante é única).
Volume: 1 = tão forte quanto a voz. Golpe (pisada, mãos no chão) atravessa a voz 5 dB abaixo dela.
python3 plano_som_passos.py   -> roteiros/som-passos/plano_som.json (depois: mixagem.py plano_som.json)"""
import os, sys, json, inspect
AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.abspath(os.path.join(AQUI, ".."))
SOM = os.path.join(RAIZ, "roteiros", "som-passos")
SINT = os.path.join(SOM, "sint")
sys.path.insert(0, AQUI)
os.makedirs(SINT, exist_ok=True)
import sfx_abrigo as SA
import sfx_passos as SP

TODOS = dict(SA.ALL); TODOS.update(SP.ALL)
EV, GERADOS = [], {}


def som(nome, seed=0, **kw):
    chave = f"{nome}_{seed}_" + "_".join(f"{k}{v}" for k, v in sorted(kw.items()))
    if chave not in GERADOS:
        p = os.path.join(SINT, "v_" + chave.replace(".", "p").replace("-", "m") + ".wav")
        f = TODOS[nome]
        if "seed" in inspect.signature(f).parameters:
            kw = dict(kw, seed=seed)
        SA.grava(f(**kw), p); GERADOS[chave] = p
    return GERADOS[chave]


def E(t, nome, vol=0.4, seed=0, golpe=False, dur=None, dur_som=None, **kw):
    """dur_som = a duração do som gerado; dur = o corte máximo na mixagem"""
    if dur_som is not None:
        kw = dict(kw, dur=dur_som)
    e = dict(som=som(nome, seed, **kw), t=round(t, 3), vol=vol, nome=nome)
    if golpe:
        e["golpe"] = True
    if dur:
        e["dur"] = dur
    EV.append(e)


# ------------------------------------------------------------ 1. o começo: o primeiro passo (0 a 8,8 s)
E(0.30, "passos", .30, 0, dur=1.0, passo=0.6, peso=0.8, dur_som=1.0)            # os dois andam de frente (o dele)
E(0.36, "passos", .24, 1, dur=1.0, passo=0.6, peso=0.7, dur_som=1.0)            # (e o do amigo, 0,06 s depois)
E(1.22, "subida", .30, 0, dur=0.9, dur_som=0.9)                               # o pé sobe e fica no ar
E(2.08, "pisada", .85, 0, golpe=True, n=1)                                    # "dobrasse": pisa
E(2.10, "crescer", .5, 0, dur_som=0.55)                                       # e dobra de tamanho
E(2.45, "ofegar", .22, 5, dur=0.5, dur_som=0.5, ritmo=3.0)                    # o susto do amigo
E(4.00, "fita", .15, 0, dur=1.15, dur_som=1.15, ritmo0=14.0, ritmo1=22.0)     # a fita sobe até a cabeça do amigo
E(4.60, "ping", .30, 0, f=1400.0)                                             # "um" (1,8 m)
E(5.80, "fita", .15, 1, dur=1.5, dur_som=1.5, ritmo0=17.0, ritmo1=26.0)       # e continua até a dele
E(7.22, "ping", .30, 1, f=1750.0)                                             # "três" (3,6 m)
# ------------------------------------------------------------ 2 e 3. o segundo e o terceiro passo
E(9.38, "pisada", .85, 1, golpe=True, n=2)
E(9.40, "crescer", .5, 1, dur_som=0.55, grave=1.3)
E(10.40, "ping", .30, 2, f=1900.0)                                            # "sete" (7,2 m)
E(11.82, "pisada", .85, 2, golpe=True, n=3)
E(11.84, "crescer", .5, 2, dur_som=0.55, grave=1.6)
E(12.68, "ping", .30, 3, f=2050.0)                                            # "quinze" (14,4 m)
# ------------------------------------------------------------ 4. a queda
E(14.38, "tropeco", .50, 0)                                                   # "tropeçar"
E(15.12, "queda_vento", .35, 0, dur_som=1.7)                                  # "leva quase dois segundos": a queda em câmera lenta
E(16.76, "maos_chao", .75, 0, golpe=True)                                     # "cair": as mãos no asfalto
# ------------------------------------------------------------ 5. o quarto passo e o grito
E(17.88, "pisada", .85, 3, golpe=True, n=4)
E(17.90, "crescer", .5, 3, dur_som=0.55, grave=1.9)
E(18.90, "ping", .30, 4, f=2200.0)                                            # "trinta"
E(20.36, "grito", .55, 0, dur_som=1.0)                                        # ele grita para baixo
E(21.12, "desce", .50, 0, dur_som=1.8)                                        # a onda desce do rosto aos pés
E(22.92, "agua_balanco", .30, 0, dur=1.0, dur_som=1.0, forca=0.7)             # "pés": a poça balança
# ------------------------------------------------------------ 6. o quinto passo, o prédio e o cabelo
E(23.92, "pisada", .88, 4, golpe=True, n=5)
E(23.94, "crescer", .5, 4, dur_som=0.55, grave=2.2)
E(25.62, "ping", .30, 5, f=2350.0)                                            # "sessenta"
E(26.92, "ping", .28, 6, f=1250.0)                                            # "ele: 57,6 m"
E(28.20, "ping", .28, 7, f=1650.0)                                            # "prédio: 55 m"
E(29.10, "vento", .14, 3, dur=3.0, dur_som=3.0, forca=0.6)                    # no alto do prédio, o vento
E(30.32, "ping", .22, 8, f=2700.0)                                            # "cabelo: 2,4 mm"
E(31.44, "ping", .22, 9, f=3000.0)                                            # "palito: 2 mm"
# ------------------------------------------------------------ 7. o coração e o sangue
E(32.72, "coracao", .30, 0, dur=5.9, dur_som=6.0, lento=1.0)                  # o coração bate durante o raio X
E(34.50, "agulha", .32, 0, dur=1.2, dur_som=1.2)                              # o manômetro sobe a 1,65 atm
E(37.00, "sangue", .50, 0, dur_som=0.6)                                       # o 1º pulso do sangue
E(37.40, "sangue", .50, 1, dur_som=0.6)                                       # o 2º
E(37.80, "sangue", .55, 2, dur_som=0.6)                                       # o 3º: chega à cabeça
E(37.90, "ping", .35, 10, f=1100.0)                                           # "16 m"
# ------------------------------------------------------------ 8. os passos 6 a 9 (um plano só) e o Burj
E(38.94, "pisada", .70, 5, golpe=True, n=6, dur_som=1.0)
E(39.36, "pisada", .72, 6, golpe=True, n=7, dur_som=1.0)
E(39.78, "pisada", .75, 7, golpe=True, n=8, dur_som=1.0)
E(40.20, "pisada", .85, 8, golpe=True, n=9, dur_som=1.6)
E(40.22, "crescer", .45, 5, dur_som=0.55, grave=2.6)
E(40.66, "ping", .30, 11, f=1300.0)                                           # "Khalifa": a caixa do Burj
E(42.40, "subida", .30, 1, dur=1.0, dur_som=1.0)                              # a câmera sobe à agulha
E(43.02, "ping", .30, 12, f=2250.0)                                           # "828 m" / "922 m" no topo
# ------------------------------------------------------------ 9. o décimo passo, a lata, a vista
E(44.40, "pisada", .88, 9, golpe=True, n=10)
E(44.42, "crescer", .5, 6, dur_som=0.55, grave=3.0)
E(45.78, "ping", .30, 13, f=1500.0)                                           # "dois quilômetros"
E(47.10, "cabelo", .30, 0, dur_som=0.9)                                       # o fio desce do céu
E(48.04, "ping", .24, 14, f=2400.0)                                           # "cabelo: 7,7 cm"
E(48.56, "lata_tinir", .32, 0)                                                # "lata"
E(49.90, "vento", .17, 4, dur=2.5, dur_som=2.5, forca=0.8)                    # a vista, o ar aberto
E(50.94, "linha", .36, 0, dur_som=0.78, f0=500.0, f1=2400.0)                  # a linha dos olhos corre ao horizonte
E(52.04, "ping", .34, 15, f=1600.0)                                           # "horizonte: 150 km"
# ------------------------------------------------------------ 10. as nuvens, a boca e o ar
E(53.20, "pisada", .88, 10, golpe=True, n=12)
E(53.22, "crescer", .5, 7, dur_som=0.55, grave=3.4)
E(53.50, "vento", .15, 5, dur=2.4, dur_som=2.4, forca=0.7)                    # nas nuvens
E(54.50, "jato", .30, 0, dur_som=2.0)                                         # o avião passa
E(54.56, "ping", .26, 16, f=1000.0)                                           # "ele: 7,4 km"
E(56.10, "inala", .35, 0, dur_som=0.8)                                        # "altura da boca": puxa o ar
E(57.86, "ping", .30, 17, f=1250.0)                                           # "boca: 0,43 atm"
E(58.44, "ping", .30, 18, f=1000.0)                                           # "chão: 1,00 atm"
# ------------------------------------------------------------ 11. o espaço
E(59.72, "pisada", .90, 11, golpe=True, n=21, dur_som=2.8)                    # "vigésimo": pisa na Terra
E(59.74, "crescer", .5, 8, dur_som=0.55, grave=4.0)
E(60.20, "zumbido", .14, 0, dur=6.0, dur_som=6.0)                             # o silêncio do espaço
E(60.65, "rumor_lua", .45, 0, dur_som=1.5)                                    # a Lua desliza para o lado dele
E(61.70, "ping", .30, 19, f=900.0)                                            # "ele: 3.775 km"
E(62.28, "ping", .30, 20, f=1400.0)                                           # "Lua: 3.474 km"
E(66.78, "pisada", .90, 12, golpe=True, n=23, dur_som=3.0)                    # "terceiro": pisa de novo (a Terra, cada vez menor)
E(67.20, "zumbido", .12, 1, dur=5.0, dur_som=5.0, f=48.0)
# ------------------------------------------------------------ 12. o fim
E(72.68, "aterra", .40, 0, dur_som=0.5)                                       # o tênis para sobre a Terra, menor que ele
E(73.18, "ping", .26, 21, f=3000.0)                                           # "a Terra"
E(74.56, "linha", .40, 1, dur_som=0.86, f0=400.0, f1=1800.0)                  # a linha Terra–Lua desenha
E(75.42, "ping", .26, 22, f=1500.0)                                           # "Terra–Lua: 384.400 km"
E(76.50, "linha", .40, 2, dur_som=1.0, f0=700.0, f1=3000.0)                   # a linha gira e fica de pé ao lado dele
E(77.52, "ping", .30, 23, f=1900.0)                                           # "ele: 483.184 km"
E(78.00, "zumbido", .20, 2, dur=2.6, dur_som=2.6, f=40.0)                     # silêncio final: o tênis parado no ar

EV.sort(key=lambda e: e["t"])
usados = [e["som"] for e in EV]
rep = {x for x in usados if usados.count(x) > 1}
assert not rep, f"efeito repetido: {sorted(os.path.basename(r) for r in rep)}"
for a, b in zip(EV, EV[1:]):                                                  # dois sons no mesmo instante embolam: afasta 0,05 s
    if b["t"] - a["t"] < 0.05 and a["nome"] != "pisada" and b["nome"] != "crescer":
        print("aviso: muito perto", a["t"], a["nome"], b["t"], b["nome"])

plano = {
    "voz": os.path.join(RAIZ, "roteiros", "voz-passos", "narracao.wav"),
    "palavras": os.path.join(RAIZ, "roteiros", "voz-passos", "palavras.json"),
    "tempos": os.path.join(RAIZ, "roteiros", "voz-passos", "tempos.json"),
    "musica": os.path.join(SOM, "musica_passos.wav"),
    "musica_db": 3.5,                                  # a música 1,4 dB mais alta que a voz (pedido de 26/10/2026)
    "efeitos": [{k: v for k, v in e.items() if k != "nome"} for e in EV],
    "momentos": [{"t": 23.1, "nivel": 0.5}, {"t": 38.2, "nivel": 0.8}, {"t": 52.3, "nivel": 0.7}, {"t": 65.4, "nivel": 0.9}, {"t": 71.7, "nivel": 0.8}],
    "saida": os.path.join(SOM, "mix_v3_pre.wav"),
}
json.dump(plano, open(os.path.join(SOM, "plano_som.json"), "w"), ensure_ascii=False, indent=1)
json.dump([{k: e[k] for k in ("t", "nome", "vol")} for e in EV], open(os.path.join(SOM, "plano_som_lista.json"), "w"), ensure_ascii=False, indent=1)
print(len(EV), "efeitos,", len(set(usados)), "arquivos distintos; último em", EV[-1]["t"], "s")
