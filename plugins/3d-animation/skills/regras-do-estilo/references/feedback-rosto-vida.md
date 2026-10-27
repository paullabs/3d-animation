---
name: feedback-rosto-vida
description: "texto/objeto nunca na frente de rosto, cabeça nunca cortada; tudo treme e balança; nada atravessa nada (colisão)"
metadata:
  node_type: memory
  type: feedback
  originSessionId: d1b4e7f8-2ddb-474e-b1af-385450f86c74
  modified: 2026-10-23T01:27:46.742Z
---

Nada (legenda, rótulo, contador, objeto) pode ficar na frente de um rosto, e nenhuma cabeça pode aparecer cortada pela borda do quadro: ou o rosto inteiro, ou nenhum. A cena nunca fica parada: tremido de traço (boil/displacement) também nos objetos e no cenário, bonecos balançando o peso e a cabeça, câmera na mão, movimentos na curva "onda" com assentamento. E nada atravessa nada: objeto não nasce dentro de boneco ou carro, boneco não invade o vizinho, câmera não passa por dentro de prop; a luz pendurada balança, mas a poça no chão só desliza.

**Why:** no presidente v3, o contador "30 mil" caiu na cara do deputado, com a cabeça cortada, e ele achou tudo "muito parado". No v4 ("já começou a ficar bom, cenário bem rico") reclamou de props colidindo, da luz que balança "bugando no chão" e de animações incoerentes (23/10/2026).

**How to apply:** em todo prod novo, usar kit3d/rostos.py + overlay `--rostos`, kit3d/vida.py e rodar kit3d/colisao.py nas cenas até dar zero COLISÃO antes do render. Ver [[feedback-ritmo-insertos]] e [[pipeline-historias]].
