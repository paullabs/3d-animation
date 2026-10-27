---
name: pipeline-historias
description: "Fluxo combinado para produzir as histórias \"5 níveis\" do Canal 38 e onde está cada peça do kit"
metadata:
  node_type: memory
  type: project
  originSessionId: d1b4e7f8-2ddb-474e-b1af-385450f86c74
  modified: 2026-10-22T07:44:44.840Z
---

Fluxo pedido pelo usuário (2026-10-22): roteiro → voz do Mac → ELE VALIDA → só então anima os vídeos.
Primeiras 3 histórias: PCC (5 níveis até o topo), chefão de cartel, ditador — formato 5 níveis, palavras fáceis, visuais simbólicos/semânticos (escala física real, ex.: R$1 milhão = cubo de 23 cm, R$1 bilhão = cubo de 2,29 m), gancho forte (≤5 s), tom documental sem glamourizar nem ensinar crime.

Peças em kit3d/: heroi.py (personagem; membros "mangueira" via limbs.py), anim.py (Timeline com molas), acting.py (Actor: point, shrug, think, facepalm, cross_arms, celebrate, take, slump, angry, look_around, rub_hands, wave, sit, stand_up, straighten), cena.py (manha() e drama(), câmera, POST de cor), semantico.py (money_block, label, level_badge, pyramid), voz.py (say → narracao.wav + tempos.json), roteiro_doc.py (gera roteiros/ROTEIROS.md). Roteiros em roteiros/*.json.

**Why:** ele quer validar texto e voz antes de gastar render; e já recusou várias versões visuais, então tudo novo passa por teste curto antes.
**How to apply:** selos/legendas presos à câmera saem borrados pelo desfoque — renderizar numa passada separada sem DOF e sobrepor. Fatos só com fonte (roteiros/fontes.json; relato de alguém vai atribuído na fala). Nomes estrangeiros: grafia fonética em "fala" e a correta em "legenda" (El Tchapo, Tchauchéscu, Kadáfi). Voz Luciana a 200 palavras/min, pausas 0,14 s entre frases e 0,32 s entre blocos. Evitar listas "o X, o Y" (soam como "ou") e "quer o" no fim de frase. Regras de texto em [[feedback-roteiros]]. Para conferir a voz: mlx_whisper com mlx-community/whisper-large-v3-turbo (já em cache) transcreve narracao.wav; "os" depois de -am/-ão e a última frase repetida no silêncio final são erros do Whisper, não da voz. Ver [[estilo-ifversetales-2d-falso]] e [[feedback-estilo-personagem]].
