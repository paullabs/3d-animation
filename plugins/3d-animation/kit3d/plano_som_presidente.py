"""Plano de som do presidente corrupto (mesma régua do PCC v7): cada efeito preso à palavra e à ação que a imagem mostra,
forte só na pausa depois da palavra; música clássica tensa nova (sonilo_music, 88 s); efeitos da ElevenLabs reaproveitados do PCC.
python3 plano_som_presidente.py  -> roteiros/som-presidente/plano_som.json
Depois: python3 ferramentas/mixagem.py ../roteiros/som-presidente/plano_som.json"""
import json, os
import overlay_presidente as O

R = (__import__("canal38_env").RAIZ + "/roteiros")
VOZ = R + "/voz-presidente"; SOM = R + "/som-presidente"
PAL = json.load(open(VOZ + "/palavras.json"))
PLANOS = json.load(open(R + "/../render_presidente/v6/planos.json"))
sint = R + "/som-pcc7/sint/"                 # ferramentas/sfx.py
el = lambda n: f"{R}/som-pcc7/{n}.mp3"       # ElevenLabs (já aprovados no PCC)


def w(frase, txt, fim=False, nth=0):
    p = [x for x in PAL if x["frase"] == frase and x["txt"].strip(".,:;!?…").lower() == txt.lower()][nth]
    return p["t1"] if fim else p["t0"]


elv = lambda n: f"{SOM}/el/{n}.mp3"         # ElevenLabs, um som próprio para cada ação (v2: nada repetido)
# v3 ("quando bate o martelo, não faz o barulho; vários efeitos não estão acontecendo"): cada som cai no QUADRO da ação,
# com a mesma conta de prod_presidente.py (não na palavra), e golpes curtos atravessam a voz (golpe=True: 5 dB abaixo dela).
F = lambda t: 1 + round(t * 24)              # mesmo F de prod_pcc.py
T = lambda f: (f - 1) / 24                   # quadro -> segundo do vídeo
ft4 = F(w(4, "terminou")) + 2; fi10 = F(w(10, "inconstitucional")) + 2       # martelada_juiz: a cabeça bate 2 quadros depois (medido)
fp = F(w(1, "presidente")) + 2; fc = F(w(4, "condenados")); f30_5 = F(w(5, "30"))
ef = [
    # 1. a faixa cai (fp-7 -> fp), o título quica, o salário pequeno, o cubo de 1 bilhão sobe
    dict(som=elv("faixa"), t=T(fp - 6), vol=0.5),
    dict(som=elv("titulo"), t=T(F(w(1, "corrupto")) + 1), vol=0.6, golpe=True),
    dict(som=elv("moedas"), t=T(F(w(1, "salário")) - 2), vol=0.55),
    dict(som=elv("braam"), t=T(F(w(1, "dinheiro"))), vol=1.0, dur=2.5, golpe=True),
    # 2. a escada do risco: a sirene acende em "risco"; algemas na pausa de "pego"
    dict(som=el("sirene"), t=T(F(w(2, "risco") - 0.2)), vol=0.7),
    dict(som=elv("algemas"), t=w(2, "pego", True) + 0.02, vol=0.85),
    # 3. o envelope desliza, a pilha dos 30 mil, as 100 notinhas voam, o segundo envelope
    dict(som=elv("envelope"), t=T(F(w(3, "pagar")) - 5), vol=1.0),
    dict(som=elv("pilha"), t=T(F(w(3, "30"))), vol=0.65, golpe=True),
    dict(som=elv("notas_voando"), t=T(F(w(3, "100"))), vol=0.6),
    dict(som=elv("envelope"), t=T(F(w(3, "todo")) - 5), vol=0.9),
    # 4. o martelo do Supremo (quadro da batida) e a grade dos 25 (bate no chão em fc)
    dict(som=el("martelo"), t=T(ft4 + 2) - 0.01, vol=1.0, golpe=True),
    dict(som=elv("grade"), t=T(fc) - 0.02, vol=1.0, golpe=True),
    # 5. o contrato perde 3 peças, o cubo de 1 bilhão brota, o bloco de 30 maços sai
    dict(som=elv("rasgo"), t=T(F(w(5, "3%"))), vol=0.6, dur=1.6),
    dict(som=elv("destrocos"), t=T(F(w(5, "1")) - 4), vol=0.85, dur=1.8, golpe=True),
    dict(som=elv("bloco"), t=T(f30_5 + 2), vol=0.65),
    # 6. o telão despenca, os 6 cubos sobem um a um, as folhas do calendário
    dict(som=elv("alarme"), t=T(F(w(6, "tona"))), vol=0.65, dur=1.8),
    dict(som=elv("seis_cubos"), t=T(F(w(6, "6") - 0.15)), vol=1.0, golpe=True),
    dict(som=elv("calendario"), t=T(F(w(6, "É")) + 2), vol=0.9),
    # 7. a propina contada, os 4 cubos no cofre, os 12 maços voando
    dict(som=elv("caixa_reg"), t=w(7, "propina"), vol=0.6, dur=1.4),
    dict(som=elv("cofre"), t=T(F(w(7, "4") - 0.3)), vol=0.9, golpe=True),
    dict(som=elv("doze"), t=T(F(w(7, "12"))), vol=0.7),
    # 8. as viaturas na sede e os 17 cubos da multa
    dict(som=elv("viaturas"), t=w(8, "Até") - 0.1, vol=0.75, dur=2.4),
    dict(som=elv("braam"), t=T(F(w(8, "17") - 0.6)), vol=1.0, dur=2.5, golpe=True),
    # 9. a torre de 45 cubos sobe; o jorro dos 40 milhões
    dict(som=elv("riser"), t=T(F(w(9, "45") - 0.3)), vol=0.55),
    dict(som=elv("destrocos"), t=T(F(w(9, "45") - 0.3) + 36), vol=0.75, dur=1.6, golpe=True),
    dict(som=elv("moedas_jorro"), t=T(F(w(9, "40"))), vol=0.55),
    # 10. o martelo do inconstitucional (quadro da batida) e as tarjas arrancadas
    dict(som=el("martelo"), t=T(fi10 + 2) - 0.01, vol=1.0, golpe=True),
    dict(som=elv("fita"), t=T(F(w(10, "revelar"))), vol=0.6),
    # 11. o estojo de joias aparece, o fiscal barra (mão levantada)
    dict(som=elv("joias"), t=T(F(w(11, "presente")) - 2), vol=0.5),
    dict(som=elv("raiox"), t=T(F(w(11, "barradas")) - 2), vol=0.65, golpe=True),
    # 12. as viaturas chegam ao palácio; batidas na porta na pausa
    dict(som=elv("viaturas"), t=T(F(w(12, "investigação")) - 6), vol=0.5, dur=2.4),
    dict(som=elv("porta"), t=w(12, "época", True) + 0.02, vol=0.9),
    # 13. as 4 grades caem nos retratos (a primeira bate 6 quadros depois)
    dict(som=elv("grades4"), t=T(F(w(13, "4")) + 5), vol=0.7, golpe=True),
    # 14. a cela fecha e o impacto final
    dict(som=elv("riser"), t=w(14, "faixa", True) - 1.0, vol=0.45),
    dict(som=elv("cela"), t=w(14, "faixa", True) + 0.02, vol=1.0, golpe=True),
    dict(som=elv("braam"), t=w(14, "faixa", True) + 0.06, vol=0.9, dur=2.5, golpe=True),
]
for k, (a0, ic, txt, cor) in enumerate(O._entradas()):          # tique discreto quando um número aparece no canto
    ef.append(dict(som=sint + "tique.wav", t=a0, vol=0.3))
for k, (nome, (f0, f1)) in enumerate(sorted(PLANOS.items(), key=lambda kv: kv[1][0])[1:]):   # swish em cada corte, alternando dois
    ef.append(dict(som=elv("swish_a" if k % 2 else "swish_b"), t=(f0 - 1) / 24 - 0.35, vol=0.4, dur=1.0))
mom = [dict(t=w(2, "pego", True) + 0.05, nivel=0.8), dict(t=w(4, "condenados", True) + 0.05, nivel=0.9),
       dict(t=w(6, "anos", True) + 0.05, nivel=0.8), dict(t=w(8, "multas", True) + 0.05, nivel=1.0),
       dict(t=w(12, "época", True) + 0.05, nivel=0.8), dict(t=w(14, "faixa", True) + 0.05, nivel=1.0)]
P = dict(voz=VOZ + "/narracao.wav", palavras=VOZ + "/palavras.json", tempos=VOZ + "/tempos.json", musica=SOM + "/musica_tensa.m4a",
         efeitos=ef, momentos=mom, saida=SOM + "/mix_guarda.wav", musica_db=3.0)   # "a música pode aumentar um pouco"

if __name__ == "__main__":
    for e in ef:
        assert os.path.exists(e["som"]), e["som"]
    json.dump(P, open(SOM + "/plano_som.json", "w"), ensure_ascii=False, indent=1)
    print(len(ef), "efeitos ->", SOM + "/plano_som.json")
