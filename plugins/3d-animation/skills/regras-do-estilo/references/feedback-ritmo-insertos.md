---
name: feedback-ritmo-insertos
description: "Ritmo e diagramação: poucas cenas bem planejadas com fio narrativo; algo novo a cada ~1 s DENTRO da cena; câmera suave; objetos limpos e alinhados à grade"
metadata:
  node_type: memory
  type: feedback
  originSessionId: d1b4e7f8-2ddb-474e-b1af-385450f86c74
  modified: 2026-10-22T16:30:31.118Z
---

Em 22/10/2026 o usuário pediu "uma coisa nova a cada 1 segundo" e dinheiro com contraste. Fiz um teste com um corte a cada ~1 s (55 planos, cada trecho num lugar diferente: celular, contador, depósito). Ele recusou: "muito estranho", "muitas cenas", "sem sentido". Pediu:
- cenas bem planejadas;
- movimentos suaves;
- diagramação e ordem de design (como e quando cada objeto entra);
- objeto limpo;
- nada fora de esquadro.

**Why:** "algo novo a cada segundo" quer dizer um elemento novo entrando numa cena composta, não um corte novo. Cortes demais e lugares soltos quebram o sentido.

**How to apply:**
- Fazer ~12–14 cenas de 3–8 s com um fio que liga tudo (multidão → prisão → cela → escada dos 5 níveis → cada nível → topo → preço → volta à escada).
- Um movimento de câmera suave por cena, com aceleração e desaceleração.
- Dentro da cena, os elementos entram em ordem planejada, alinhados à grade (eixo central e terços; zona do título no alto, legenda a 65%).
- Entrada limpa: sem quique e sem inclinação aleatória.
- Mostrar storyboard antes de animar.

Do teste recusado, continuam valendo:
- o estúdio liso para o objeto em foco (`limpo.estudio`);
- o maço de R$ 100 legível (`dinheiro.py`);
- `sets.glow` com raio < 1 vira um quadrado opaco: usar `cena.disc` com `amat` radial.

Ver [[feedback-cenario-limpo]] e [[pipeline-historias]].

**Um cenário diferente por cena (23/10/2026):** o usuário pediu que cada cena tenha o seu próprio lugar, de acordo com o que a fala diz. No PCC v4: esquina com estante de dinheiro, avenida com viatura, sala dos fundos, delegacia com painel de fichas, salão com a caixa, tribunal com faixas de pena, escritório com a cidade, rua com casas e olhos de inveja, cobertura ao pôr do sol, sala da cúpula com a coroa, bloco de celas e a escada de volta.

**How to apply:**
- Peças em `kit3d/sets4.py`; cenas em `prod_pcc5.py`.
- Variar a cor de fundo por lugar dentro da paleta índigo (`VARIACOES`), com a cor de luz também diferente.
- Herói com escala 1,32 (`heroi()` com invólucro) e lente de 30 mm, que dá cerca de 4,6 m de largura a 5,8 m.
- Guia da área segura: `area.guia()`.
- Dinheiro com volume: `G.bloco(..., zk=3)` engrossa o maço.

**Profundidade, escala e planos (23/10/2026):** o usuário criticou duas coisas:
- tudo numa linha, como num palco, sem perto e longe;
- o herói maior que todos (escala 1,32).

Também pediu close no rosto e "outras dimensões" (outros ângulos).

**How to apply:**
- Escala única: herói e figurantes com 1,75 m.
- Três camadas:
  - primeiro plano desfocado perto da lente (`S.ombro`, `S.planta`, `S.coluna_fg`, cerca, hidrante, grade);
  - assunto em foco;
  - fundo com véus de névoa (`S.neblina`) e luzes desfocadas (`S.bokeh_fundo`).
- 2–3 planos por cena com `planos()` em `prod_pcc6.py` (uma câmera por plano, troca por marcador na palavra):
  - aberto;
  - close no rosto (lente 50);
  - inserto do objeto (lente 45);
  - por cima do ombro;
  - de costas em contraplano (rig "back" + `S.mostra` para trocar de rig);
  - de baixo ou de cima (altura da câmera + shift).
- Esconder o que atravessa a lente com `S.mostra`.
