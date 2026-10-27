---
name: feedback-modelagem-3d
description: "O abrigo": objetos planos (mão de papel) quebram a imersão; modelar em 3D, cidade viva, vidro de verdade, cortes de até 1,3 s, câmera de segurança, efeito Fuji no fim
metadata:
  type: feedback
---
Em 24/10/2026, sobre o storyboard v2 de "O abrigo", o usuário pediu:
- refazer em 3D os objetos que estão planos: "a mão não pode ser toda flat, parecendo um papel; perde a imersão";
- a porta com vidro de verdade, que deixa ver o outro lado;
- a blusa de frio de quem conta em vermelho escuro, para dar contraste;
- a cidade mais viva;
- câmeras mais perto do rosto, de baixo, e uma câmera de segurança;
- cortes rápidos: nenhum plano passa de 1,3 s, mas sem a câmera mexer o tempo todo;
- efeito Fuji (filme) na pós, por último.

**Why:** o 2D chapado aguenta personagem, mas objeto e mão em plano fechado parecem recorte de papel.

**How to apply:**
- Usar `kit3d/objetos3d_abrigo.py`: `Mao3D` com dedos articulados, `porta3d` com o furo e o vidro, bicicleta, sirene, galão, estante, gaiola, prato, cama, cadeira, mesa e lâmpada.
- Usar `kit3d/cidade3d.py` (`rua3d`, com `ruina=True` para depois da bomba) e `kit3d/cenario3d_abrigo.py` (sala com canos e o vão da porta aberto).
- Na câmera de segurança, aplicar `kit3d/pos_cctv.py`.
- Halos de luz em 3D giram para a câmera (`O3.olha_camera`).

Ver [[feedback-cinema-acao]].

**Braço de primeira pessoa (25/10/2026, "o braço parece solto, bugado"):** a manga de quem conta tem de sair do quadro (nunca mostrar a ponta redonda do braço no meio da imagem).
- Use `Mao3D(..., manga_comp=1.1)` (padrão em `maos_pov3d` e em `mao_em` do `story3_abrigo.py`); o POV da bicicleta e da corrida usa as mãos coladas na câmera (`maos_pov3d`), com os braços saindo dos cantos de baixo.
- Antes de renderizar uma pose com a mão num objeto (guidão, giz, garfo), meça a posição dos punhos: o ângulo do ombro soma com a inclinação do tronco e a mão fica no ar.
