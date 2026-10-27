---
name: feedback-espaco-entre-objetos
description: Dar folga entre o boneco e o cenário em TODOS os quadros (inclusive durante o crescimento); conferir em vista ampla, não só malha dentro de malha
metadata:
  type: feedback
---
Entre o boneco e qualquer objeto do cenário tem que haver espaço de sobra, em todos os quadros do plano, não só nos quadros de teste. Antes de entregar, conferir a folga (distância mínima) e olhar o mapa de cima.

**Why:** em 25/10/2026, em "os passos", o braço do boneco entrava na lateral do ônibus quando ele crescia. O `colisao_passos` só olhava 5 quadros e só pegava malha dentro de malha, então não viu. O Paulo disse: "precisa de uma visão ampla para os objetos não se colidirem; tem que dar um espaço".

**How to apply:** rodar `anim_passos7.py -- ID x --espaco` (folga em todos os quadros, margem 0,10 u) e gerar `mapa_topo.py` quando mexer no cenário. O corpo cresce e abre os braços: contar a largura máxima, não a de pé. Relacionado: [[feedback-rosto-vida]], [[project-passos]].
