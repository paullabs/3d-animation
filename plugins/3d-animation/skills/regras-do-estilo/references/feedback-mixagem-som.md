---
name: feedback-mixagem-som
description: "Mixagem aprovada na direção: música clássica tensa bem sutil, camadas de volume que sobem e descem, efeitos baixos que nunca competem com a voz"
metadata:
  node_type: memory
  type: feedback
  originSessionId: d1b4e7f8-2ddb-474e-b1af-385450f86c74
  modified: 2026-10-22T21:04:59.495Z
---

Em 22/10/2026 o usuário recusou a primeira mixagem do PCC v7: a música eletrônica/trap "não combinou", estava alta, e alguns efeitos competiam com a voz.

**Why:** a voz é o que retém; música e efeitos só dão clima.

**How to apply:**
- Música: clássica tensa (cordas, violoncelos, tímpano suave), gerada no Higgsfield sonilo_music, sem batida eletrônica.
- Volume em camadas, em `kit3d/mix_pcc7b.py`:
  - cama de cerca de -17 dB sob a fala;
  - sobe nas pausas entre as falas;
  - swell nos momentos fortes e na abertura e no final.
- Efeitos: cerca de um terço do volume da primeira mixagem, com pico limitado a 30% do pico da voz, sempre na pausa logo depois da palavra.
- Conferir transcrevendo o áudio final com o Whisper: todas as palavras têm de aparecer.

**Resultado:** a v7b (música em camadas, `mix2.wav`, guardada como `roteiros/som-pcc7/mix_aprovado.wav`) foi APROVADA. A reclamação seguinte de "ainda alto" era sobre outro vídeo que ele tinha aberto por engano. Antes de baixar mais o som, confirmar qual arquivo ele ouviu.

**Ordem da entrega:** mandar o vídeo primeiro e o texto depois, para ele não confundir qual arquivo está avaliando.

Ver [[feedback-tom-conversa-legendas]].

**Atualização de 24/10/2026 (reflexo v15 → v16):** "os efeitos estão todos confusos; use mais os efeitos do próprio Claude; a pegada de antes era melhor".
- A v15 tinha 60 efeitos empilhados.
- A v16 tem 22: um som por momento, quase todos sintetizados (`kit3d/sfx_reflexo.py`). Sons gerados fora, só a torcida.
- A pegada da mosca é o tapa + o grave da v14.

**Pegada da mosca (24/10/2026):** o efeito aprovado é o do v11: o grave `roteiros/som-reflexo/grave_pegada.wav` cru, ~+14 dB acima da voz.
- Todo som feito depois dele (tapa, vrum, BUM sintetizado abaixo de 70 Hz) foi recusado com "faltou o efeito".
- A causa era o limitador de golpe da mixagem e a falta de energia em 70-200 Hz.
- Hoje ele sai com `livre: true` no plano.
- **Se ele mandar uma versão antiga dizendo que um efeito estava certo, meça o áudio dela primeiro.**

**Voz do Lucas afunda no fim (24/10/2026):** numa geração longa o tom cai de ~176 para ~90 Hz e a voz fica "para dentro". Solução: trechos curtos com `[concerned]`/`[worried]`, +2 semitons, presença e nivelamento (skill `voz.md`). Sempre medir tom e volume por fala antes de entregar.

**Nunca mude o tom da voz clonada/escolhida (24/10/2026):** o pitch shift de +2 semitons mudou o timbre e o ritmo, e o usuário notou na hora. Use etiquetas, trechos curtos, EQ, nível e `atempo` (só ritmo).
