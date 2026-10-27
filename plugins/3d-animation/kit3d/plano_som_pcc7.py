"""Plano de som do PCC v7 (modelo para os próximos temas): cada efeito preso a uma palavra ou a um corte, e as subidas da música.
python3 plano_som_pcc7.py  -> roteiros/som-pcc7/plano_som.json
Depois: python3 ferramentas/mixagem.py ../roteiros/som-pcc7/plano_som.json"""
import json
import mix_pcc7 as M, overlay_pcc4 as O

SOM = M.SOM; w = M.w
sint = SOM + "/sint/"                       # gerados por ferramentas/sfx.py
el = lambda n: f"{SOM}/{n}.mp3"             # ElevenLabs: só os sons muito específicos

# efeitos fortes na pausa logo depois da palavra (t1 + 0,02); leves (papel, tique) podem cair em cima
ef = [dict(som=el("portao"), t=w(1, "PCC", True) + 0.02, vol=0.75),
      dict(som=el("notas"), t=w(1, "salário") + 0.1, vol=0.45),
      dict(som=el("sirene"), t=w(4, "polícia") - 0.1, vol=0.45),
      dict(som=el("notas"), t=w(5, "700") - 0.05, vol=0.4),
      dict(som=sint + "papel.wav", t=O._t(6, "42") - 0.3, vol=0.4),
      dict(som=el("grade"), t=w(6, "isso", True) + 0.02, vol=0.7),
      dict(som=el("fenda"), t=w(7, "paga") + 0.1, vol=0.45),
      dict(som=el("martelo"), t=w(8, "crime", True) + 0.02, vol=0.6),
      dict(som=el("martelo"), t=w(8, "morte", True) + 0.03, vol=0.75),
      dict(som=sint + "boom.wav", t=w(8, "morte", True) + 0.05, vol=0.55),
      dict(som=el("notas"), t=w(9, "passando"), vol=0.4),
      dict(som=el("tiro"), t=w(10, "casa", True) + 0.03, vol=0.65),
      dict(som=el("notas"), t=w(11, "80%"), vol=0.35),
      dict(som=el("coroa"), t=w(12, "líder", True) + 0.02, vol=0.6),
      dict(som=el("cela"), t=w(13, "solto", True) + 0.03, vol=0.65),
      dict(som=sint + "subida.wav", t=w(14, "subir", True) - 1.55, vol=0.35),
      dict(som=sint + "boom.wav", t=w(14, "subir", True) + 0.05, vol=0.9)]
for a0, ic, txt, cor in O._entradas():                          # tique discreto quando um número aparece no canto
    ef.append(dict(som=sint + "tique.wav", t=a0, vol=0.22))
for nome, (f0, f1) in sorted(M.PLANOS.items(), key=lambda kv: kv[1][0])[1:]:   # whoosh em cada corte em movimento
    ef.append(dict(som=sint + "whoosh.wav", t=(f0 - 1) / 24 - 0.3, vol=0.3))
mom = [dict(t=w(2, "caro", True) + 0.05, nivel=0.7), dict(t=w(8, "morte", True) + 0.05, nivel=1.0), dict(t=w(10, "casa", True) + 0.05, nivel=0.8),
       dict(t=w(12, "líder", True) + 0.05, nivel=1.0), dict(t=w(13, "solto", True) + 0.05, nivel=1.0)]
P = dict(voz=M.VOZ + "/narracao.wav", palavras=M.VOZ + "/palavras.json", tempos=M.VOZ + "/tempos.json", musica=SOM + "/musica2.m4a",
         efeitos=ef, momentos=mom, saida=SOM + "/mix_guarda.wav")

if __name__ == "__main__":
    json.dump(P, open(SOM + "/plano_som.json", "w"), ensure_ascii=False, indent=1)
    print(len(ef), "efeitos ->", SOM + "/plano_som.json")
