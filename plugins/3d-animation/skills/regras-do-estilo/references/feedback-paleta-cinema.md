---
name: feedback-paleta-cinema
description: "Cor e pose: paleta de cinema planejada por vídeo, fundo em tom médio (nada de quase preto), sem amarelo+escuro+preto; herói de frente quando a cena pede"
metadata:
  node_type: memory
  type: feedback
  originSessionId: d1b4e7f8-2ddb-474e-b1af-385450f86c74
  modified: 2026-10-22T18:35:09.590Z
---

Em 22/10/2026 o usuário achou a cena do trono "muito escura" e "pouco profissional". Também reprovou o par amarelo-dourado + escuro + preto e o herói de lado no trono.

O que ele pediu:
- uma paleta de cinema planejada para cada vídeo, com cores que contrastem;
- luz profissional, pré-composição e bom enquadramento;
- o personagem "literalmente de frente", criando as poses que faltam.

**Why:** a cabeça do herói é preta. Em fundo quase preto ela some e tudo fica pesado. E dourado com preto deixa o visual barato.

**How to apply:**
- Fundo em tom médio, com degradê e halo atrás do assunto.
- A cor da luz e da borda complementa o vermelho da jaqueta.
- Nada de assento ou fundo vermelho atrás do herói: ele se confunde com a jaqueta.
- Paletas de teste em `kit3d/trono.py` (`PALETAS`): petróleo + coral, ardósia + rosa, areia + azul-tinta.
- A escolhida vale para o vídeo inteiro, variando só o clima por ato.
- Pose de frente: `kit3d/frente.py`. A Timeline grava de perfil; depois do bake, `bracos()` espelha os braços e `sentado()` monta joelhos e colo de frente.

Depois o usuário achou o petróleo "mais do mesmo, sem contraste de cor" e escolheu índigo + laranja (`PALETAS["indigo"]`, padrão de `prod_pcc4.py`).
- Preferir pares de cores opostas: fundo frio e profundo, luz quente.
- O dinheiro sempre verde (`grana.py`).
- Legenda de uma palavra por vez, baixa e estreita (`overlay_pcc3.py`).
- Valores como contador de jogo (ícone + número, sem palavras).
- Composição pela área segura do Reels (`area.py`).

Ver [[feedback-cenario-limpo]] e [[feedback-ritmo-insertos]].
