---
name: regras-do-estilo
description: Regras do estilo 3D animation em reels narrados (boneco de cabeça preta em salas 3D): roteiro, voz, imagem, cinema, som, entrega e custos. Leia antes de qualquer roteiro, cena, animação, voz ou som deste estilo.
---

# Regras do estilo 3D animation

Vieram de recusas reais do dono do canal. Cada uma tem o porquê em `references/` (índice: `references/INDICE.md`). Num caso novo, siga o porquê, não só a letra.

## O estilo
Reels verticais 1080×1920, 24 qps, 60 a 85 s, narrados. Boneco de cabeça preta, olho branco e borda de luz, em salas e cidades 3D de verdade, no Blender por script.

## Regras que valem para tudo
- **Roteiro:** gancho direto na primeira frase, tom de conversa, cada fala nasce da anterior (fio de causa e consequência), palavras fáceis (sem sigla nem metáfora rara), fecho que volta ao gancho. "Bem parecido" com uma referência = mesma sequência, palavras nossas. Instagram: terceira pessoa, sem violência explícita.
- **Voz:** uma emoção por frase, trechos de 3 a 8 s. **Nunca mudar o tom (pitch)**: só EQ, nível e `atempo`.
- **Imagem:** nada na frente de rosto; nada atravessa nada (`kit3d/colisao.py`, e a folga entre objetos em todos os quadros); tudo vivo (respira, balança); cenário limpo (uma cor, uma luz, personagem grande); cores vivas = saturar a paleta real, nunca colorir prédio de brinquedo.
- **Cinema:** decupagem antes de animar (lente em mm, posição, foco, a mensagem) e storyboard renderizado antes da animação; um plano por ideia, sem cortes repetidos da mesma cena; câmera no gesto que prova a fala; revelar o monstro em degraus e dar a reação antes da causa; início e fim de cada plano com movimento.
- **Movimento:** curvas de entrada e saída, mola por junta, nunca pose a pose; câmera sempre andando e planejada em ondas. "Travado", "duro" e "amador" são pistas reais: meça com `mede_mov.py`.
- **3D:** objeto plano em plano fechado "parece papel e perde a imersão": modele em 3D.
- **Texto na tela:** legenda grande em pílula (ou uma palavra por vez com bounce), poucos efeitos, número no objeto da cena.
- **Som:** trilha tensa e sutil, um efeito por ação no quadro da ação, sem repetir arquivo; mixagem com guarda de voz (`ferramentas/mixagem.py`, só passa com GUARDA OK).
- **Entrega:** 1080×1920, 24 qps, ~11 Mbps e AAC 256 kbps. Rascunho em meia resolução; resolução cheia só depois do OK.

## Fases e aprovação
Roteiro → voz → ficha de elenco e objetos → decupagem e storyboard → rascunho animado → som → render cheio → pós. **Uma aprovação por fase; não pule.** Vídeo ou imagem primeiro, texto curto depois; faça a crítica antes de mostrar.

## Custos
Grátis: voz de teste do Mac (`/3d-animation:voz-teste`), efeitos e trilha sintetizados, render no próprio Mac. Pagos e opcionais, só no fim e só com aprovação: voz final ElevenLabs (Lucas, eleven_v4), trilha e imagem no Higgsfield.

Leia o arquivo de `references/` do assunto em questão: `feedback-roteiros.md`, `feedback-cinema-acao.md`, `feedback-animacao-profissional.md`, `feedback-mixagem-som.md`, `feedback-direcao-de-cena-cinema.md` etc.
