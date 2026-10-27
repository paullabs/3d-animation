---
name: feedback-transicoes
description: "Transições têm que ser imperceptíveis: corte no pico de uma rampa de velocidade com a mesma velocidade de tela dos dois lados; nada de cortina ou tela coberta"
metadata:
  node_type: memory
  type: feedback
  originSessionId: d1b4e7f8-2ddb-474e-b1af-385450f86c74
  modified: 2026-10-22T18:45:30.594Z
---

Em 22/10/2026, o usuário reprovou a "cortina" (coluna escura que passa na lente entre as cenas). Achou estranha e longa demais. Ele quer um movimento de câmera que já corta para a próxima cena, contínuo e imperceptível, com velocidade suave "de acordo com os gráficos" (curvas do After Effects).

**Why:** a cortina deixa ~0,4 s de tela coberta e parece transição de slide. O corte escondido no movimento mantém o vídeo andando sem emenda visível.

**How to apply:**
- Usar `kit3d/transicao.py`: `rampa_fim` na câmera da cena A e `rampa_inicio` na da cena B, na mesma direção.
- Usar cerca de 4 quadros de cada lado, com pico de ~15% da tela por quadro.
- Manter a mesma velocidade de tela dos dois lados: `delta_B = delta_A × dist_B / dist_A`.
- Na montagem, aplicar borrão de movimento só nesses quadros: `montar_teste.py --borrao "a1:fim:v:300:4,a2:inicio:v:300:4"`.
- A direção do corte acompanha a história (subir quando é "subir de nível").
- Não usar cortina, fade nem tela escura.

Ver [[feedback-ritmo-insertos]].

**Movimento dos personagens e objetos (23/10/2026):** o usuário reprovou o braço que sobe e o fuzil que cai por não terem a "onda" suave do editor de gráficos do After Effects.

**How to apply (animação):**
- Nunca interpolar pose a pose com smoothstep, porque a velocidade zera em cada chave e vira "foto colada". Usar `curvas.spline` (Catmull-Rom, velocidade contínua) e `frente.bracos(keys, extras=...)`.
- Todo gesto tem antecipação (cede antes), passa do ponto e assenta.
- Impacto é mola amortecida (`curvas.pancada` e `curvas.mola`), com ação sobreposta: a mão afunda, o objeto quica, o giro assenta, o squash segue o deslocamento (nada de valores fixos).
- Queda em ease-in (`curvas.s("queda")`).
- Mostrar o gráfico de velocidade de cada curva junto com o vídeo (`personagem/pcc/grafico-movimento.png`).
