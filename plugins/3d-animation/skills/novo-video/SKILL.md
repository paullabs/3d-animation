---
name: novo-video
description: Começa uma história nova em 3D animation do zero até o vídeo, por fases com aprovação (roteiro, voz, ficha, decupagem, animação, som, render), usando o kit pronto e sem gastar crédito até o fim.
argument-hint: "<ideia ou tema do vídeo>"
disable-model-invocation: true
---

# Novo vídeo em 3D animation

A ideia do usuário: $ARGUMENTS

Antes de qualquer coisa, leia as skills `regras-do-estilo`, `catalogo-do-kit` e a do formato escolhido (`historias-5-niveis` ou `animacao-3d-cinema`). O kit já está pronto em `kit3d/`: **copie e adapte o modelo mais parecido, não reescreva o motor.**

## Passo 0: pasta pronta
Se não existir `kit3d/` na pasta atual, rode `/3d-animation:iniciar` primeiro.

## Fases (uma aprovação por fase; não pule)
1. **Roteiro** em `roteiros/<slug>.json` (formato abaixo). Pesquise os fatos com fonte. Mostre o texto corrido e espere o OK.
2. **Voz de teste** grátis: `/3d-animation:voz-teste roteiros/<slug>.json`. Mande o áudio.
3. **Ficha de elenco e objetos** (imagem): quem aparece, de que roupa, e cada objeto 3D. Espere o OK.
4. **Decupagem e storyboard renderizado**: um plano por ideia, lente em mm, posição, foco, a mensagem; storyboard renderizado antes de animar. Espere o OK.
5. **Rascunho animado** em meia resolução (`--scale 0.5 --samples 10`), com a voz de teste. Confira colisão e movimento (`colisao.py`, `mede_mov.py`).
6. **Som** sintetizado (efeitos e trilha pelos scripts; mixagem com `ferramentas/mixagem.py`, que só passa com GUARDA OK).
7. **Render cheio** (`--scale 1.0 --samples 32`) e entrega 1080×1920, 24 qps.
8. **Só no fim e só com aprovação**, itens pagos: voz final (ElevenLabs, Lucas), trilha e imagem (Higgsfield). Se trocar a voz, os tempos mudam.

Regra de custo: até a fase 7 nada é pago. Render e crédito custam: nunca avance sem o OK da fase anterior.

## Formato do roteiro (`roteiros/<slug>.json`)
```json
{
  "titulo": "E se cada passo dobrasse a sua altura?",
  "tipo": "reel narrado, 9:16",
  "objetivo": "o que o vídeo prova, em uma frase",
  "voz": "Lucas (ElevenLabs) no final; voz de teste do Mac agora",
  "blocos": [
    {"nivel": 0, "nome": "O começo",
     "falas": [
       {"fala": "texto falado", "legenda": "texto da legenda (igual ou mais curto)",
        "selo_na_tela": "régua: 1,8 m → 3,6 m",
        "imagem": "o plano: lente, posição, o que a imagem prova na fala",
        "fonte": "de onde vem o fato ou número"}
     ]}
  ]
}
```
Modelo completo: `roteiros/passos-dobrando.json`.

## Como falar com o usuário
Português do Brasil, palavras simples. Mande o vídeo ou a imagem primeiro e o texto curto depois. Antes de mostrar, olhe os quadros, faça a crítica que o dono do canal faria e corrija sozinho. No fim de cada fase diga em uma linha o que está pronto e o que falta aprovar.
