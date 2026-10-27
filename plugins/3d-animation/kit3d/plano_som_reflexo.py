"""Plano de som do reflexo: um som por ação, no QUADRO da ação (a mesma conta do prod: F(t) = 1 + round(t*24), T(f) = (f-1)/24).
Os quadros vêm do prod_reflexo (medidos no Blender em 23/10/2026: pegada da mosca no 53, botão no 218, régua no 293/346, chutes 450/517/548,
luva no 565, tiro no 642, cartão no 667, cabo no 846, chute da final no 907, bola na rede no 993, o tempo volta no 1020, a câmera de TV bate no 1029,
a torcida levanta no 1063). Trilha: clássica (Higgsfield sonilo_music), em camadas pela mixagem.py da skill.
python3 plano_som_reflexo.py  ->  roteiros/som-reflexo/plano_som.json"""
import json, os

R = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "roteiros")
R = os.path.abspath(R)
SOM = os.path.join(R, "som-reflexo"); EL, EL2, SI = (os.path.join(SOM, d) for d in ("el", "el2", "sint"))
T = lambda f: (f - 1) / 24.0


def ef(som, t, vol, golpe=False, dur=None, livre=False):
    e = dict(som=som, t=round(t, 3), vol=vol)
    if livre:
        e["livre"] = True
    if golpe:
        e["golpe"] = True
    if dur:
        e["dur"] = dur
    return e


# v19 (24/10/2026, "preenche com efeitos sonoros: cada movimento, cada cena; não deixe repetir o mesmo efeito"):
# cada ação tem o SEU som e nenhum arquivo toca duas vezes (conferido no fim do script). Os golpes têm graves próprios, diferentes entre si;
# só a pegada da mosca usa o grave do v11 (cru, +14 dB, "livre"). Foley gerado em el2/ e el3/, o resto sintetizado em sint/ (sfx_reflexo.py).
EL3 = os.path.join(SOM, "el3")
E = [
    # 1. a mosca e o copo
    ef(f"{SI}/mosca.wav", 0.0, 0.18, dur=2.3),                            # a mosca zumbe em volta da cabeça e desacelera
    ef(f"{SI}/tempo_desce.wav", 1.25, 0.22, dur=0.7),                     # o tempo freia no "10 vezes"
    ef(f"{SI}/swish_a.wav", T(50), 0.3, dur=0.22),                         # o braço corta o ar
    ef(f"{SOM}/grave_pegada.wav", T(53), 6.0, livre=True, dur=1.8),       # a pegada (o grave do v11)
    ef(f"{SI}/mosca_presa.wav", 2.3, 0.12, dur=3.0),                      # ela se debate presa na mão
    ef(f"{EL3}/copo_desliza.wav", 3.62, 0.45, dur=1.2),                   # o copo desliza e tomba na borda
    ef(f"{SI}/swish_b.wav", T(105), 0.35, dur=0.5),                       # a mão passa por baixo do copo
    ef(f"{EL2}/copo_palma.wav", T(121), 0.6, golpe=True),                  # o vidro encosta na palma
    ef(f"{SI}/golpe_copo.wav", T(121), 4.0, livre=True, dur=0.9),         # o peso do copo na mão
    # 2. o botão
    ef(f"{SI}/bipe.wav", T(158), 0.3),                                    # sinal 1
    ef(f"{EL2}/botao.wav", T(168), 0.6, golpe=True),                      # ela aperta (0,25 s)
    ef(f"{SI}/sucao.wav", T(213) - 0.45, 0.4, dur=0.5),                   # o ar é puxado: o tempo vai parar
    ef(f"{SI}/bipe_b.wav", T(213), 0.3),                                  # sinal 2
    ef(f"{SI}/golpe_botao.wav", T(218), 1.0, golpe=True),                 # você aperta (0,025 s)
    # 3. a régua
    ef(f"{EL2}/pinca.wav", T(286), 0.4, dur=0.5),                         # a pinça dela solta
    ef(f"{EL2}/regua.wav", T(293), 0.6, golpe=True, dur=0.8),             # ela pega lá embaixo (30 cm)
    ef(f"{SI}/vrum_m.wav", T(331), 1.1, golpe=True, dur=0.7),             # o tempo se dobra em volta de você
    ef(f"{SI}/tic_3mm.wav", T(349), 0.8, golpe=True),                     # você pega no 3 mm
    ef(f"{SI}/flutuar.wav", 15.5, 0.35, dur=2.4),                         # o mundo parado no ar
    # 4. o pênalti
    ef(f"{SI}/chute.wav", T(450), 0.9, golpe=True),                       # o pé na bola, câmera no chão
    ef(f"{EL}/rede.mp3", T(459), 0.5, dur=1.2),                           # a bola na rede
    ef(f"{SI}/swish_d.wav", T(463), 0.3, dur=0.45),                       # o goleiro comum pula (tarde)
    ef(f"{SI}/swish_c.wav", T(504), 0.3, dur=0.3),                        # ele pula antes, no lado errado
    ef(f"{EL2}/chute.wav", T(517), 0.6, golpe=True, dur=0.6),             # o segundo chute
    ef(f"{SI}/rede_seca.wav", T(526), 0.4, dur=0.8),                      # a bola entra de novo
    ef(f"{SI}/tempo_desce_b.wav", T(545), 0.3, dur=0.9),                  # o tempo freia: você espera a bola sair
    ef(f"{SI}/chute_seco.wav", T(548), 0.7, golpe=True),                  # a bola sai ("sair")
    ef(f"{EL3}/deslize_grama.wav", T(552), 0.5, dur=1.5),                 # você mergulha
    ef(f"{EL2}/luva.wav", T(565), 0.9, golpe=True, dur=0.8),              # a luva segura ("defende")
    # 5. a largada
    ef(f"{EL3}/engatilha.wav", T(631), 0.5),                              # o juiz levanta e engatilha a pistola
    ef(f"{SI}/tiro.wav", T(642), 1.0, golpe=True, dur=1.2),               # o tiro
    ef(f"{EL3}/arranca_bloco.wav", T(644), 0.6, dur=1.0),                 # você explode do bloco
    ef(f"{EL3}/passos_pista.wav", T(651), 0.5, dur=1.5),                  # a corrida (os outros só agora saem)
    ef(f"{EL3}/cartao.wav", T(667), 1.0, golpe=True),                                 # o cartão vermelho aparece
    ef(f"{EL3}/derrapa.wav", T(673), 0.9, golpe=True, dur=1.2),                       # você para
    ef(f"{SI}/derrota.wav", 31.25, 0.9, golpe=True, dur=1.7),                         # "eliminado"
    # 6. a final
    ef(f"{SI}/grua.wav", 31.75, 0.3, dur=2.4),                            # a grua desce sobre o estádio
    ef(f"{SI}/torcida_amb_curta.wav", 32.0, 0.35, dur=4.2),               # o estádio à noite
    ef(f"{EL3}/cabo_range.wav", 34.2, 0.4, dur=1.4),                      # o cabo range sob tensão
    ef(f"{SI}/estala_cabo.wav", T(846), 0.9, golpe=True, dur=1.2),        # o cabo arrebenta
    ef(f"{SI}/vrum_g.wav", T(846), 1.3, golpe=True, dur=1.9),             # o tempo para
    ef(f"{EL3}/faisca.wav", T(850), 0.5, dur=1.0),                        # as faíscas
    ef(f"{EL3}/vento_queda.wav", T(856), 0.3, dur=3.0),                   # a câmera de TV despenca devagar
    ef(f"{SI}/coracao_longo.wav", 36.6, 0.3, dur=3.0),                    # o coração na câmera lenta
    ef(f"{SI}/chute_lento.wav", T(907), 0.4, dur=1.2),                    # o chute da final, abafado
    ef(f"{SI}/tique_relogio.wav", 38.45, 0.3),                            # "meio segundo"
    ef(f"{SI}/olhar_a.wav", 39.1, 0.3, dur=0.35),                         # o olhar vai para a bola
    ef(f"{SI}/olhar_b.wav", 39.85, 0.3, dur=0.35),                        # e para o menino
    # 7. o menino
    ef(f"{EL3}/passos_grama.wav", T(979), 0.9, golpe=True, dur=1.6),                  # você dispara para o menino
    ef(f"{SI}/pega_menino.wav", T(995), 0.7, golpe=True, dur=0.7),        # você o levanta
    ef(f"{SI}/rede_lenta.wav", T(993), 0.35, dur=1.4),                    # a bola entra (abafada: o mundo está lento)
    ef(f"{SI}/tempo_volta.wav", T(1000), 1.0, golpe=True, dur=1.0),                   # o tempo volta
    ef(f"{EL}/tv_queda.mp3", T(1029), 0.9, golpe=True, dur=1.6),          # a câmera de TV bate no chão vazio
    ef(f"{EL3}/levanta.wav", T(1063), 0.4, dur=3.0),                      # 80 mil se levantam
    ef(f"{EL}/aplauso.mp3", 45.3, 0.4, dur=3.5),                          # o aplauso
    # 8. a pergunta
    ef(f"{EL3}/taca.wav", 47.01, 0.35, dur=2.0),                          # a taça
    ef(f"{SI}/boom.wav", 48.2, 0.6, dur=1.6),                             # o último grave
]
_sons = [e["som"] for e in E]
_rep = sorted({x for x in _sons if _sons.count(x) > 1})
assert not _rep, f"efeito repetido: {_rep}"                                 # regra do usuário: nenhum som toca duas vezes

plano = dict(voz=f"{R}/voz-reflexo/narracao.wav", palavras=f"{R}/voz-reflexo/palavras.json", tempos=f"{R}/voz-reflexo/tempos.json",
             musica=f"{SOM}/musica.m4a", efeitos=E,
             momentos=[dict(t=24.0, nivel=0.8), dict(t=31.6, nivel=0.8), dict(t=40.15, nivel=1.0), dict(t=48.2, nivel=1.0)],
             saida=f"{SOM}/mix.wav", musica_db=2.0,
             duck_voz=[dict(t=round(T(53) - 0.03, 3), dur=0.4, db=-3)])       # a voz abaixa 3 dB por 0,4 s no golpe da pegada (o v11 não abaixava nada)
json.dump(plano, open(os.path.join(SOM, "plano_som.json"), "w"), indent=1, ensure_ascii=False)
print("ok", len(E), "efeitos")
