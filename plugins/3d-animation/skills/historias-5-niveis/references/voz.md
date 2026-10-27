# Voz

## Escolha aprovada
Use a ElevenLabs (conector `creative_generate_speech`) com o modelo **eleven_v4**.

A voz é **Lucas - Deep & Profound Narrator** (`GIuLCSVfgJaUuh7hYOY8`): grave, de documentário. Recusadas:
- "Victor" (jovem e leve: "ficou ruim");
- Luciana do Mac (era só para validar o texto);
- Mauricio Nocce (boa, mas o Lucas ganhou).

## Emoção por frase
Ele quer que cada frase "comunique" a cena. Ponha uma tag por frase e `[fast-paced]` no começo:
```
[fast-paced] [intrigued] Você acabou de entrar no PCC. [impressed] E o seu salário pode chegar a mil e duzentos reais por dia.
[ominous] Só que cada degrau paga mais... e cobra mais caro.
[tense] … [excited] … [disgusted] … [sarcastic] … [menacing] … [grim] … [suspicious] … [shocked] … [confident] …
[quietly] Ainda quer subir?
```
Use "..." para pausa dramática, só onde a imagem precisa respirar.

## Geração e custo
- Uma geração da narração inteira custa cerca de 1.300 créditos.
- Para comparar vozes, gere 1 take de cada (`generations_count=1`). Não repita para "tentar de novo": cada chamada cobra.
- Baixe o mp3 pela URL de `creative_get_flow_run_status`, que expira em 2 h.

## Velocidade
Acelere sem mudar o tom:
```
ffmpeg -i lucas.mp3 -af atempo=1.10 voz.mp3
```
A meta é 55 a 60 s. Ele pediu "um pouco mais rápido para a retenção".

## Tempos de palavra
```
cd kit3d && python3 voz_eleven.py ../roteiros/voz-<tema> ../roteiros/<tema>.json voz.mp3
```
O script gera `narracao.wav` (0,3 s de respiro antes e 1,4 s de cauda depois), `tempos.json` (início e duração de cada fala) e `palavras.json` (cada palavra da legenda com t0 e t1).

## Conferência
Transcreva com `mlx_whisper` (`mlx-community/whisper-large-v3-turbo`) e compare com o roteiro.

O Whisper às vezes escreve "está/para" quando a voz disse "tá/pra". Confira pela duração da palavra em `<take>.json`: cerca de 0,1 s é "tá". A legenda segue o que foi falado.

São alucinações do Whisper, não erros da voz:
- "E aí" no silêncio final;
- "mais" no lugar de "mas".

## Narrativa em primeira pessoa (O abrigo, 24/10/2026)
Para uma história triste ou de suspense (não a série "Você acabou de..."):
- **Sem `[fast-paced]` e sem `atempo`:** o Lucas fala ~3 palavras por segundo no ritmo natural, e 211 palavras deram 69,84 s. Acelerar tira o peso.
- **Uma emoção por frase**, calma: `[urgent]`, `[shocked]`, `[tense]`, `[quietly]`, `[relieved]`, `[ominous]`, `[disgusted]`, `[grim]`, `[somber]`. Nenhuma foi falada em voz alta (conferido no Whisper).
- **Um take só** (`generations_count=1`): cada geração custa ~1.230 créditos da ElevenLabs.
- **Pegar o link:** `creative_get_flow_run_status` volta "generating" nos primeiros segundos; espere uns 30 s e consulte de novo (não chame a geração outra vez).
- **Conferência:** o Whisper escreve "para" por "pra" e "Lú" por "Lu"; é normalização, não erro.

### A voz afunda no fim (O abrigo v1, 24/10/2026: "ele falava para dentro; voz muito grave e baixa; tem que ser clara, não entusiasmada")
**Causa medida:** o Lucas tem registro natural de ~90 Hz. Numa geração longa o tom começa em ~176 Hz (com `[urgent]`/`[shocked]`) e cai para ~85 a 95 Hz já na fala 4 (e o volume cai 4 a 5 dB). Etiquetas como `[quietly]`, `[somber]`, `[grim]`, `[ominous]` pioram, e mesmo `[serious]` e `[tense]` ficam em ~90 Hz.
**Etiquetas que seguram o tom** (teste de 5 s, mesma frase): `[concerned]` 126 Hz, `[worried]` 116 Hz, `[matter-of-fact]` 103 Hz (instável), `[tense]` 92 Hz, sem etiqueta 86 Hz. Para história triste, mas clara, use `[concerned]` e `[worried]`.
**Receita que resolveu:**
1. Gere **trechos curtos (3 a 8 s)**, cada um com a sua etiqueta, e não uma narração só: o tom não tem tempo de cair. O custo é o mesmo (cobra por caractere).
2. Cada trecho: corte o silêncio das pontas, `highpass=70`, `equalizer` +2,5 dB a 3,2 kHz (consoantes) e -1,5 dB a 180 Hz, `acompressor` 2,5:1. **NÃO suba o tom** (veja o erro abaixo). Só acerte o ritmo: trechos curtos saem mais lentos (2,72 palavras/s contra 3,4 no começo); aplique `atempo` (só velocidade, não mexe no tom) até ~3,0 palavras/s, o ritmo do começo (`atempo=1.125`).
3. **Nivele o volume** de todos os trechos no rms do começo (ganho medido por trecho) e monte com pausas controladas de 0,35 a 0,45 s entre falas e 0,16 s dentro da mesma fala.
4. Rode `voz_eleven.py` no resultado. Antes e depois: tom das falas 4-11 de 94 para 105 Hz (só pelas etiquetas e trechos curtos), volume de −22,7 para −19,4 dB, ritmo igual ao do começo (3,0 palavras/s).
**Meça sempre:** tom mediano por fala (autocorrelação) e rms por fala; se a diferença entre a fala 1 e a última passa de 3 dB ou o tom cai abaixo de ~110 Hz, refaça.

**ERRO que custou uma rodada (24/10/2026): não mude o tom da voz.** Levantei +2 semitons com `asetrate`+`atempo` só nas falas 4 a 11. O timbre ficou mais fino (formantes sobem junto), as falas 4-11 ficaram ~7% mais rápidas que o trecho original e destoaram das falas 1-3; o usuário percebeu na hora: "a voz mudou, o pitch ficou mais rápido". A mesma voz do começo ao fim vale mais que alguns Hz: use só etiquetas (`[concerned]`/`[worried]`), trechos curtos, nivelamento e acerto de ritmo por `atempo`. Se precisar de mais tom, regere com etiqueta mais viva; não processe o tom.
