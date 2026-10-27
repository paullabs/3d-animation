---
name: feedback-tom-conversa-legendas
description: Roteiro em tom de conversa (sem ficar abstrato nem seco) e textos na tela discretos; voz final pela ElevenLabs com efeitos e música tensa
metadata:
  node_type: memory
  type: feedback
  originSessionId: d1b4e7f8-2ddb-474e-b1af-385450f86c74
  modified: 2026-10-22T20:52:20.564Z
---

Em 22/10/2026, depois da v6 do PCC, o usuário pediu:
- **Roteiro:** mais natural, como uma conversa. A versão anterior era direta demais e às vezes abstrata. Não deve ficar mais longo nem enrolar.
- **Legendas e textos:** estavam muito invasivos (uma palavra por vez em caixa alta, grossa; rótulo do nível grande o tempo todo).
- **Visual:** mexer mais nas cores, no contraste e no reposicionamento das cenas.
- **Som:** voz da ElevenLabs com efeitos sonoros e música tensa.

**Why:** ele quer que soe como alguém contando a história para você, e que o texto ajude sem cobrir a cena.

**How to apply:**
- Roteiro: frases curtas faladas ("Aí você vira gerente.", "O problema? ...", "tá", "pra"), uma pergunta de vez em quando e as mesmas fontes. Exemplo: `roteiros/pcc4.json`.
- Voz: a voz "Victor" (jovem e leve) foi RECUSADA. Ele quer:
  - narrador grave e um pouco mais rápido, para segurar a retenção;
  - uma emoção diferente em cada frase, combinando com a cena.
- Como fazer: eleven_v4 com tags por frase ([intrigued], [ominous], [tense], [excited], [disgusted], [sarcastic], [menacing], [grim], [suspicious], [shocked], [quietly]), com [fast-paced] no começo, e depois ffmpeg atempo de 1,07 a 1,10.
- ESCOLHIDA em 22/10/2026: **Lucas** (GIuLCSVfgJaUuh7hYOY8), com atempo 1,10. A voz e os tempos estão em `roteiros/voz-pcc5`.
  - O Whisper escreve "está/para" quando ele diz "tá/pra"; confira pela duração da palavra (cerca de 0,1 s = "tá").
- Mixagem: `kit3d/mix_pcc7.py`.
  - Música do Higgsfield sonilo_music, com sidechain na voz.
  - Efeitos da ElevenLabs (eleven_text_to_sound_v2) sempre na pausa logo DEPOIS da palavra. Em cima da palavra eles a apagam: o Whisper deixou de ouvir "morte" e "líder".
- Cenas escritas para outra voz: `kit3d/tempo.py` leva os tempos antigos para os novos (VOZ_NOVA em prod_pcc4).
- Candidatas testadas em 22/10/2026:
  - Mauricio Nocce (bEYEuRWlSrSpweXZIhwF), grave e dramático;
  - Lucas - Deep & Profound Narrator (GIuLCSVfgJaUuh7hYOY8). `kit3d/voz_eleven.py` gera narracao.wav, tempos.json e palavras.json a partir do mp3.
- Textos: `kit3d/overlay_pcc4.py`.
  - Legenda em trechos de até 3 palavras, caixa normal, Demi Bold 54 px, sombra macia; cada palavra acende quando é dita; dinheiro em verde.
  - Rótulo do nível pequeno no canto, só por 2,4 s.
  - Contadores pequenos, só por 2,2 s.

Ver [[feedback-roteiros]] e [[pipeline-historias]].
