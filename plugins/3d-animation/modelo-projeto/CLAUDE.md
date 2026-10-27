# Projeto de animação 3D (plugin 3d-animation)

Este arquivo é lido sozinho quando uma sessão do Claude abre esta pasta. Ele resume o estilo, as regras e o caminho de trabalho.
As regras vieram do Canal 38 e foram aprendidas com recusas reais. Ajuste ao seu gosto, mas mude uma regra só sabendo o porquê dela (está em `regras-do-estilo` e nas skills `historias-5-niveis` e `animacao-3d-cinema`, que o plugin traz).

## O estilo
- Reels verticais 1080×1920, 24 qps, 60 a 85 s, narrados.
- Boneco de cabeça preta, olho branco e borda de luz, em salas e cidades 3D de verdade, feito no Blender por script.
- Filmado como cinema: decupagem plano a plano, câmera no gesto que prova a fala, movimento de animador (curvas de entrada e saída, nunca pose a pose).

## Como trabalhar
- Responda em português do Brasil, com palavras simples.
- **Valide por fases, sempre nesta ordem:** roteiro → voz → ficha de elenco e objetos → decupagem e storyboard → rascunho animado → som → render cheio → pós. Não pule uma aprovação: render e crédito custam.
- **Entregue o vídeo ou a imagem primeiro e o texto curto depois.** Antes de mostrar, olhe os quadros, faça a crítica que o dono do canal faria e corrija sozinho.
- **Custo zero por padrão:** voz de teste do Mac (`say`), efeitos e trilha sintetizados pelos scripts, render no seu Mac. ElevenLabs e Higgsfield só no fim e só com aprovação.

## Regras que valem para tudo
- **Roteiro:** gancho direto, tom de conversa, cada fala nasce da anterior, palavras fáceis (nada de sigla nem metáfora rara), fecho que volta ao gancho. Instagram: terceira pessoa, sem violência explícita.
- **Voz:** uma emoção por frase, trechos curtos de 3 a 8 s. Nunca mudar o tom (pitch): só EQ, nível e `atempo`.
- **Imagem:** nada na frente de rosto, nada atravessa nada (`kit3d/colisao.py`), tudo vivo (respira, balança).
- **Cinema:** decupagem antes de animar; plano aberto calculado por "caixa" é recusado; objeto plano em plano fechado perde a imersão, modele em 3D.
- **Som:** trilha tensa e sutil, um efeito por ação no quadro da ação, sem repetir arquivo, mixagem com guarda de voz (`ferramentas/mixagem.py`).
- **Entrega:** 1080×1920, 24 qps, ~11 Mbps e AAC 256 kbps.

## Mapa das pastas
| Pasta | O que tem |
|---|---|
| `kit3d/` | Todo o código (Blender por script). `kit3d/INDICE.md` diz o que cada arquivo faz |
| `ferramentas/` | `mixagem.py` (mixagem com guarda de voz) e `sfx.py` (efeitos sintetizados) |
| `roteiros/` | Roteiros (`<video>.json`), vozes (`voz-<video>/`) e som (`som-<video>/`). Exemplos em `roteiros/exemplos/` |
| `personagem/<video>/` | Fichas, decupagens, storyboards, provas e rascunhos de cada vídeo |
| `render_<video>/` | Quadros renderizados (descartáveis, ocupam muito) |
| `entregas/` | Vídeos finais |

**Não mova pastas depois de começar.** Se a pasta mudar de lugar, rode `/3d-animation:iniciar` de novo na nova pasta.

## Como rodar
- Blender: `python3 kit3d/<rodador>.py ...` (os rodadores chamam o Blender sozinhos). Para chamar à mão: `<Blender> -b -P kit3d/<script>.py -- <args>`. O caminho do Blender vem de `kit3d/canal38_env.py` (variável `CANAL38_BLENDER` para trocar).
- Modelos para copiar num vídeo novo: veja a skill `historias-5-niveis` (formato "5 níveis"), `animacao-3d-cinema` (filme com decupagem) e `kit3d/INDICE.md`.
- Teste do ambiente: `/3d-animation:testar`. Voz grátis de um roteiro: `/3d-animation:voz-teste roteiros/<video>.json`.

## Onde cada vídeo parou
(Anote aqui, por vídeo, o que foi aprovado, o que foi recusado e por quê. É o que a próxima sessão vai ler primeiro.)
