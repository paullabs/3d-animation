---
name: estilo-ifversetales-2d-falso
description: Canal 38 (reels de histórias narradas) segue o estilo do @IfverseTales — 2D falso com parallax feito em Blender; regras visuais já aprovadas/recusadas
metadata:
  node_type: memory
  type: project
  originSessionId: d1b4e7f8-2ddb-474e-b1af-385450f86c74
  modified: 2026-10-22T06:24:51.365Z
---

O Canal 38 (pasta "38 - 3D ANIMATION") faz reels de histórias narradas no estilo do canal @IfverseTales: boneco 2D recortado (cabeça redonda azul-marinho, moletom vermelho, membros de palito, contorno escuro e borda de luz deslocada) em cenário chapado com parallax. Tudo é montado por script em Blender 5.2 (sem abrir a interface), em `kit3d/` (personagem atual: `heroi.py`; ficha: `ficha3.py` + `ficha3_montar.py`).

Regras firmadas em 2026-10-22:
- O boneco é desenho plano de frente para a câmera; a câmera só desliza ou avança, nunca gira nem dá a volta (senão "vira papel").
- Cenário pode ser camadas planas ou sala 3D, mas sempre chapado (cor plana, névoa por distância, desfoque).
- Rosto é o foco: olho branco SEM pupila preta, sobrancelha branca fina, boca com muitas formas e um elemento extra (suor, lágrima, vergonha, raiva, sombra, brilho, ! e ?).
- Olhos e boca tremem como rabisco a 3 quadros por segundo (displace no Blender).
- Corpo simples (sem bolso, punho, barra, sola).
- Regra de pose: ângulo positivo = para onde ele olha.

Protagonista DEFINITIVO (escolhido em 2026-10-22): conceito 3 "esguio" na combinação de cores 2 SEM cachecol — corpo/cabeça/mãos pretos, jaqueta bomber vermelha (#c62f35) com gola/barra/punhos canelados, calça azul (#2b64c0), sapato preto, cabeça menor (0.8), braços longos. É o padrão em heroi.py (Heroi.ESGUIO); o moletom antigo continua com prop outfit="hoodie". Conceitos em personagem/conceitos/.

**Why:** o usuário recusou modelo 3D com volume, manequim realista, cartoon de olho grande e versões em que poses ficavam incoerentes.
**How to apply:** qualquer cena ou história nova parte do `heroi.py` e dessas regras; ver [[feedback-estilo-personagem]].
