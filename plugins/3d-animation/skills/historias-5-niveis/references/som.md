# Som

## O que ele recusou e por quê
1. **Trilha eletrônica/trap:** "não combinou".
2. **Música clássica, mas alta:** numa subida "quase não deu para escutar a voz". A causa medida: a subida depois de "morte" durava 0,9 s, mas a frase seguinte começava 0,26 s depois, então a música inteira subiu em cima dela.
3. **Efeitos altos, competindo com a voz.** No primeiro mix, o martelo em cima de "morte" e a coroa em cima de "líder" apagaram as palavras (o Whisper não as ouviu).

## Correção forte de 23/10/2026 (presidente)
"Os efeitos sonoros quase não dá para ouvir. Só tá repetindo o mesmo efeito. Não tá tão profissional. A música não tá tensa."
- **Um som próprio para cada ação**, nunca o mesmo boom/papel/whoosh repetido. No presidente foram 31 efeitos da ElevenLabs, cerca de 17 créditos cada (`roteiros/som-presidente/el/`): braam, título de metal, moedas, algemas, envelope, pilha de notas, notas voando, grade, rasgo de papel, bloco saindo, alarme, seis impactos, calendário, caixa registradora, cofre, doze whooshes, viaturas, destroços, riser, jorro de moedas, fita arrancada, joias, raio-x, batidas na porta, quatro grades, cela, faixa e dois swishes de transição alternados.
- **Volume pela energia, não pelo pico** (`mixagem.py` v2). Um envelope ou uma nota curta com pico alto soava fraquíssimo. Agora `vol` 1 = tão forte quanto a voz: impactos na pausa 0,8 a 1,0, foley de ação 0,45 a 0,6, swish 0,4, tique 0,3. Enquanto a voz fala, um limitador abaixa só o efeito para 12 dB abaixo dela. O começo mudo do arquivo é cortado e `dur` limita o tamanho.
- **Confira cada arquivo baixado** com `volumedetect`: as duas marteladas vieram quase mudas (pico −30 dB) e foi preciso usar a do PCC. Alguns vêm com 14 s (caixa registradora), então corte com `dur`.
- **Música tensa de verdade:** o prompt "underscore sutil de quarteto" ficou morno. O que funcionou: "Intense dark suspense orchestral score for a crime and corruption thriller, relentless driving staccato low strings ostinato, fast ticking pulse like a clock, dissonant violin clusters and nervous tremolo, menacing low brass swells, deep timpani heartbeat pulses, constant dread rising in three waves… like a Sicario or Dark Knight underscore but purely orchestral, no vocals, no electronic synths, no rock drums".
- **"A música pode aumentar um pouco"** (com a trilha tensa e os efeitos novos): `"musica_db": 3.0` no `plano_som.json` sobe a música inteira 3 dB e a guarda acompanha. Ficou −22,8 dB sob a fala, −18 dB nas pausas e, no pior instante, −16,4 dB, e o Whisper ouviu todas as palavras. Para a trilha tensa, esse é o ponto de partida.
- **O som cai no QUADRO da ação, não na palavra.** "Quando bate o martelo na mesa, não faz o barulho do martelo; vários efeitos não estão acontecendo." O martelo tocava 0,2 s antes da batida (s04) e 0,6 s depois (s10, preso ao fim da palavra), e por cair em cima da voz descia a quase nada. No plano, use a mesma conta do prod: `F(t) = 1 + round(t*24)`, `T(f) = (f-1)/24`. A batida do martelo é 2 quadros depois de `martelada_juiz(f)` (medido no Blender pela cabeça do martelo), a grade bate em `fc`, os cubos brotam em `sobe_do_chao(f)` e a faixa cai de `fp-7` até `fp`. Na dúvida, meça a posição do objeto quadro a quadro.
- **Golpe atravessa a voz:** `golpe: true` (martelo, grade, impacto, cubo, raio-x) fica 5 dB abaixo da voz, e o resto, 8 dB abaixo. Antes eram 12 dB e sumiam.
- **O limitador só age onde a voz está soando** (fala + 50 ms). A v2 limitava também o respiro de 0,3 s antes de cada palavra, com piso baixo, e um efeito numa pausa curta caía a −28 dB. O relatório agora lista "efeitos que podem sumir"; abaixo de −12 dB em relação à voz, suba o `vol` ou marque como golpe.
- **Não achatar a trilha inteira:** a v1 dividia pela envoltória e apagava as ondas de tensão. Agora a compressão é 2:1 (env^0,25) e a guarda cuida da voz. Cama: −26 dB sob a fala, −16 dB nas pausas, subidas a −11 dB.

## Música
- **Estilo:** clássica tensa. Gere no Higgsfield (`sonilo_music`, `--duration 60`). O prompt que funcionou: "Tense classical orchestral underscore, string quartet and low cellos, slow ostinato in minor key, sustained violin tremolo, soft timpani pulses, subtle and restrained, chamber music feel, gradual tension building in waves with quiet valleys, no drums, no electronic sounds, no vocals, ends on a low unresolved chord".
- **Nível:** de fundo, quase uma cama. A `mixagem.py` achata a dinâmica da trilha e aplica estas camadas:

  | Momento | Nível em relação à voz |
  |---|---|
  | debaixo da fala | −27 dB, subindo até −25 dB no fim |
  | pausas | −18 dB |
  | momentos fortes | −14 dB |
  | abertura e cauda | −13 dB |

  As subidas **só acontecem dentro da pausa** e terminam 0,3 s antes da próxima palavra. A música já desce 0,3 s antes de cada palavra.
- **Guarda de voz:** em qualquer janela de 300 ms com voz, a música fica pelo menos 20 dB abaixo da voz.
- **Subidas de verdade precisam de espaço.** Se a narração não tem pausa, a música não sobe, e está certo. Para ter um respiro dramático, deixe o espaço no roteiro ("..." na fala).

- **Presidente (23/10/2026):** 88 s com o mesmo modelo e prompt, mais "political thriller, slow pizzicato ostinato, sly and conspiratorial like a scheme unfolding, darker and heavier in the last third". Gere a trilha uns 4 s mais longa que a voz: ela termina numa cauda calma.

## Efeitos
- **Sintetizados por nós** (`scripts/sfx.py`, de graça e no mesmo timbre):

  | Efeito | Uso |
  |---|---|
  | `whoosh` | corte em movimento, volume 0,3 |
  | `boom` | impacto grave em "morte" e no final |
  | `impacto_metal` | grade, porta |
  | `subida` | antes do boom final |
  | `tique` | quando um contador aparece, volume 0,22 |
  | `bipe_mira` | mira travando |
  | `papel` | fichas no mural, notas caindo |

  Rode `python3 scripts/sfx.py PASTA` para gerar todos, ou importe as funções e mude os parâmetros.
- **ElevenLabs** (`creative_generate_in_flow`, `node_type="sfx"`, `eleven_text_to_sound_v2`, cerca de 17 créditos cada) só para som muito específico: sirene de viatura brasileira, martelo de juiz, tiro seco com eco, portão de prisão com fuzil, coroa caindo, porta de cela, notas contadas.
- **Reaproveite os efeitos da ElevenLabs já aprovados** (`roteiros/som-pcc7/*.mp3`: martelo, sirene, notas, grade, cela, portão, tiro, coroa, fenda): no presidente, nenhum efeito novo foi preciso. Modelo de plano por tema: `kit3d/plano_som_presidente.py`, com um efeito por ação que a imagem mostra, preso à palavra.
- **Onde colocar:** na **pausa logo depois da palavra** (`t1 + 0,02`). Em cima da palavra, só se for leve (papel, tique). O `mixagem.py` corta mais 40% de qualquer efeito que caia sobre a fala.
- **Volume:** `vol` de 0 a 1, onde 1 é pico de 25% do pico da voz. Use 0,3 a 0,5 para a maioria, até 0,75 para portão, martelo final e cela, e 0,9 para o boom final.

## Plano de som e mixagem
Escreva `roteiros/som-<tema>/plano_som.json`:
```json
{"voz": ".../narracao.wav", "palavras": ".../palavras.json", "tempos": ".../tempos.json",
 "musica": ".../musica.m4a",
 "efeitos": [{"som": ".../sint/whoosh.wav", "t": 8.62, "vol": 0.3}],
 "momentos": [{"t": 35.97, "nivel": 1.0}],
 "saida": ".../mix.wav"}
```
Use `kit3d/mix_pcc7.py` e o gerador do `plano_som.json` do PCC como modelo: os tempos saem de `palavras.json` e os cortes de `planos.json`. Depois rode:
```
python3 ferramentas/mixagem.py plano_som.json
```
O script imprime a música sob a fala, nas pausas, no pior instante e o pico dos efeitos, e só passa com **GUARDA OK**: música sob a fala ≤ −24 dB, pior instante ≤ −18 dB, efeitos ≤ −10 dB.

Na conferência do Whisper, "cem/sem", "vir à/vira" e "três/3" são o mesmo som (normalização), e "Não, não…" na cauda da música é alucinação. O resto tem de bater.

Depois de montar o vídeo, transcreva o áudio final com o Whisper: **todas** as palavras do roteiro têm de aparecer. Se uma sumir, algo está em cima dela.

## Reflexo (23/10/2026): trilha clássica e efeitos novos baratos
- **Trilha "de preferência clássica"** (`sonilo_music`, 54 s para 49,7 s de voz), escrita em ondas que seguem a história: "Cinematic classical orchestral score, purely acoustic symphony orchestra, late-romantic concert style. Opens with a light nervous pizzicato strings ostinato ticking like a clock and curious woodwinds, the tension slowly building in waves; in the middle the cellos and violas turn darker in a minor key with sustained violin tremolo and soft timpani pulses; in the final third a suspended moment where time stands still, high strings holding a long note over a slow timpani heartbeat, then a noble heroic swell with full strings and warm French horns, then it calms down to a quiet unresolved chord. No vocals, no drums kit, no electronic sounds, no synths." Com `musica_db: 2.0`, ficou em −24,4 dB sob a fala e −19 dB nas pausas, com GUARDA OK.
- **Efeitos novos no Higgsfield, baratos:**
  - `mirelo_text_to_audio` (0,5 crédito, `--duration`): ambiências e sons longos (torcida, aplauso, rede, cabo, câmera caindo).
  - `seed_audio` (0,2 crédito, `--sample_rate 48000`, prompt começando por "Sound effect only:"): golpes curtos (botão, chute, luva, régua, copo).
  - Confira cada arquivo com `volumedetect`: 4 de 13 vieram com pico entre −31 e −54 dB e foram refeitos.
  - Confira com o Whisper que nenhum tem fala de verdade. "Thanks for watching" em som sem fala é alucinação do Whisper.
- **Sintetizados do tema** (`kit3d/sfx_reflexo.py`): zumbido de mosca que desacelera junto com o tempo, tempo descendo e voltando, coração na câmera lenta, bipe de sinal.
- **Plano por quadro** (`kit3d/plano_som_reflexo.py`): cada som no quadro medido da ação. O som de "tempo voltando" começa 20 quadros antes, para o pico cair na volta. As versões lentas (chute, rede) levam passa-baixa e o tom 15 a 20% mais grave.
- **Cada anel de ar na imagem tem o seu sopro** (reflexo v14): rode a cena e leia as linhas `RING nome quadro raio` que a `cinema3d.onda` imprime; um `ar_p` (raio < 0,6), `ar_m` ou `ar_g` (raio > 1) no mesmo quadro, e `golpe: true` nos que são impacto (pegada, tiro, cabo, bola, queda). Anel que cai fora do vídeo (num trecho que nenhuma câmera mostra) não ganha som.
- **Pegada ou golpe precisa de médio:** um grave sintetizado abaixo de 80 Hz some em caixa de celular. Faça tapa de ar (700 Hz a 5 kHz), corpo de 140 a 70 Hz e um estalo; o grave puro vai por baixo, só como reforço.
- **Nada longo antes do golpe:** um "tempo descendo" de 1,3 s por cima do golpe o cobria. Termine o ruído de preparação antes dele (`dur`) para o golpe ser o efeito mais forte daquele instante.
- **Medir o efeito de verdade:** a saída da mixagem passa por `loudnorm` e não dá para subtrair a voz dela. Salve os "stems" (`efx`, `mus_f`, `voz`) numa cópia do script e compare os níveis quadro a quadro.
- **Impacto de tempo parado = "vrum"** (reflexo v15, "efeitos de impacto, como se tivesse parado no tempo"): troca do sopro de ar. Receita (`kit3d/sfx_reflexo.py`: `vrum`, `sucao`):
  - baque seco de ruído (250 Hz a 3 kHz, 45 ms) no quadro da ação;
  - serra distorcida (tanh) com a frequência despencando de 190-260 Hz para ~40 Hz em 0,17 s, filtrada a 1,1 kHz e com tremolo de 24 Hz;
  - sub de 110 a 32 Hz, um rumor de ruído grave que fica e cauda de sala (convolução com ruído que morre);
  - antes do grande, `sucao`: ruído filtrado que sobe de 180 Hz a 5 kHz, cada vez mais forte, com um tom subindo, que corta seco no baque.
  - Tamanhos: `vrum_p` (anéis pequenos), `vrum_m` (tiro, bola, queda), `vrum_g` (quando o tempo para: pegada, régua, pênalti, cabo, volta).
  - Volumes: na pausa, o "vrum" pode soar tão forte quanto a voz (`vol` ~1,4); sobre a fala o limitador de golpe segura em −5 dB.
- **Menos é mais (reflexo v16):** cada momento leva UM efeito (no máximo um corpo + um grave do mesmo golpe), com pelo menos ~0,5 s até o próximo. Empilhar sucção, tapa, grave, impacto e cauda no mesmo quadro, ou dar som a cada anel desenhado, vira "tudo confuso". Prefira os efeitos sintetizados aqui (`sfx_reflexo.py`, `scripts/sfx.py`); gere fora só o que não dá para sintetizar (torcida, multidão).
- **Golpe que "para no ar" = BUM, não tapa** (reflexo v17): para um acerto em câmera lenta (a mosca, o tempo parando), use um BUM grave e longo (`sfx_reflexo.bum`), com ataque macio e cauda suspensa; ponha logo antes de uma pausa da fala, onde ele floresce. Tapa, estalo e sucção deixam o golpe seco ou confuso.
- **Golpe de câmera lenta que o usuário quer ouvir de verdade** (reflexo v18): marque o efeito com `"livre": true` (passa por cima do limitador, a +12 a +15 dB sobre a voz média) e, se preciso, `"duck_voz": [{"t": ..., "dur": 0.4, "db": -3}]` no plano. O guarda de voz continua valendo para o resto. O som precisa ter energia em 70-200 Hz (aparece em caixa pequena), não só abaixo de 70 Hz. **Compare sempre com uma versão que ele aprovou, medindo os dois áudios.**
- **Preencher sem repetir** (reflexo v19): liste cada movimento da cena com o quadro, dê a cada um um som próprio e rode o plano com um `assert` de que nenhum arquivo aparece duas vezes. O que se repete ganha variante de verdade (outra semente, banda e pan; outro timbre), não só outro volume. Só entra um som por movimento, e eles nunca ficam no mesmo quadro (afaste ~0,1 s). Geração barata para foley (passos, mergulho, derrapada, cabo, multidão): `seed_audio` com "Sound effect only: ..., close microphone, no voice, no music" (0,2 crédito cada); confira com `volumedetect` e o Whisper (alucina "E aí" e "Thanks for watching" em ruído).
