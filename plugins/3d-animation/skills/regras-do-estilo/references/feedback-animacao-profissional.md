---
name: feedback-animacao-profissional
description: "travado, duro, amador" = pose a pose que para em cada chave e câmera que entra/sai parada; usar mola por junta, câmera de operador e medir com mede_mov.py
metadata:
  type: feedback
---

O usuário recusou a cena 1 do reflexo v2 em 23/10/2026: "movimentos muito travados, muito duros; a câmera sem as ondas in, out; anime como um animador profissional".

**Why:** a medição mostrou duas causas:
- o boneco ia de pose a pose em smoothstep, parando em cada chave e com todas as juntas mexendo juntas;
- todo plano de câmera entrava e saía a 0 m/s, então os cortes juntavam duas paradas.

A skill já proibia smoothstep, mas o código novo (heroi3d.anima) caiu nele de novo.

**How to apply:**
- **Boneco:** `Heroi3D.anima` com curva monótona e mola por junta, com atraso. O quadril lidera; braço e cabeça chegam depois e assentam. Gesto seco usa `molas=` mais duras.
- **Câmera:** `camera_cine` com v_in/v_out. O corte acontece com a câmera andando, e a chegada passa do ponto e assenta. A mira segue a ação.
- **Objeto pego:** vai junto com a mão, que amortece.
- **Desfoque de movimento:** ligado nas cenas 3D.
- **Antes de mostrar:** rodar `kit3d/mede_mov.py` e conferir zero PARADA no meio do gesto e zero TRANCO.

**Reforço de 23/10/2026 ("animações porcas"):**
- Golpe rápido = antecipação pequena e parada, depois 3 a 4 quadros de ida, com o cotovelo puxando e mola dura (~12 Hz).
- O objeto pego some no quadro em que a mão *de verdade* (já com a mola) passa por ele, nunca no quadro da chave.
- Criança no colo vai de lado, no quadril: antebraços deitados sob as pernas, luvas longe do rosto, as duas cabeças à vista. Não soltar no chão sem precisar.

Ver [[feedback-cinema-acao]] e [[feedback-transicoes]].

**Animação (25/10/2026, "seja um animador profissional: leve, fluida, muito smooth"):** vale para todo o rascunho animado de "O abrigo" e para os próximos vídeos.
- Curvas de entrada e saída em tudo (nada de pose a pose nem velocidade que zera em cada chave); mola por junta com atraso (`Heroi3D.anima`, `camera_cine`); antecipação, passa do ponto e assenta; ação sobreposta (o quadril lidera, braço e cabeça chegam depois); arcos em vez de linhas retas; respiração e balanço nas pausas; desfoque de movimento ligado.
- Mão e braço de POV: o pulso lidera e o antebraço acompanha, o objeto pego vai junto com a mão (sem "colar" no quadro da chave); câmera com velocidade contínua, sem tranco no corte.
- Antes de mostrar: `mede_mov.py` (zero PARADA no meio de um gesto e zero TRANCO), folha de quadros seguidos de cada braço e mão, e rever em 24 qps como espectador.
**Cena de mão "amadora" (25/10/2026, prato 4B a 4D):** braço-tubo sobre a comida, mão esquerda boiando sem braço, garfo espetado de pé. Regra: a câmera fica ao lado da linha do antebraço (nunca atrás dele, senão a manga esconde a mão); os dois braços entram pelos cantos de baixo; o antebraço é quase horizontal e o pulso dobra para pegar a ferramenta (`mao_braco`, `mao_segura` no `story3_abrigo.py`); para giz e gestos pequenos, plano de perto só com os dedos e o início do braço.

**Sentido do corte (25/10/2026):** "tem muito corte sem sentido".
- Dois planos seguidos do mesmo lugar contam como "a mesma cena".
- O clarão todo branco "perde o sentido".
- Cortar de fora para dentro sem mostrar a pessoa entrando é "teletransporte".
- A ameaça (o cogumelo da explosão) precisa estar à vista desde o primeiro plano.

**Regra:** toda ação começa num plano e termina no seguinte, e cada corte muda o ponto de vista. Detalhes em `personagem/abrigo/regras-animacao.md`, seção 4b.
