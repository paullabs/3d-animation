# Índice do kit3d

Uma linha por arquivo, tirada do docstring. Gerado por `tools/sincronizar_do_projeto.py`; não edite à mão.

| arquivo | o que faz |
|---|---|
| `acoes_abrigo2.py` | Animação de verdade da parte 2 de "O abrigo" (v3, 26/10/2026), plano a plano, por cima dos cenários do story_abrigo2.py. |
| `acoes_abrigo2b.py` | Animação de verdade das sequências 4C a 17C da parte 2 de "O abrigo" (v4, 27/10/2026), por cima dos builders v5 do story_abrigo2.py. |
| `acoes_abrigo2c.py` | Animação de verdade das sequências 6 e 7 da parte 2 (o galpão: acordar, a lanterna, o olho, o cochicho). Ver acoes_abrigo2b.py (framework). |
| `acoes_abrigo2d.py` | Animação de verdade das sequências 8 a 12 da parte 2 (Cadê a Rita; o líder conta o ar e a gosma; os esqueletos; os Sem-Osso; os ossos na porta). Ver acoes_abrigo2b.py. |
| `acoes_abrigo2e.py` | Animação de verdade das sequências 13 a 17 da parte 2 (o rádio e o giz, a voz na torre, "só eu", o portão, o ferrolho). Ver acoes_abrigo2b.py. |
| `acting.py` | Atuação corporal do protagonista: um repertório de ações prontas, todas com as regras do guia |
| `adereco.py` | Objetos de cena (riqueza de detalhe) no mesmo traço chapado: cada lugar ganha 3 a 5 peças que contam onde estamos. |
| `ambiente3d.py` | Ambientes 3D de verdade (crítica de 23/10/2026: "o ambiente é um fundo chapado, falta o 3D"). |
| `ambiente_galpao.py` | O galpão do grupo, rico (26/10/2026, storyboard v5 das sequências 6 a 17 de "O abrigo, parte 2"; guia: personagem/abrigo/guia-luz-e-suspense.md). |
| `ambiente_noite.py` | Kit de cenário rico da noite de "O abrigo" parte 2 (26/10/2026, guia: personagem/abrigo/guia-luz-e-suspense.md). |
| `anim.py` | Animação suave do protagonista: movimento primário + movimento secundário por molas. |
| `anim3_abrigo.py` | Animação de "O abrigo" em cima do storyboard v3 (story3_abrigo.py): o cenário, a lente e o enquadramento de cada plano vêm de lá; |
| `anim3_rodar.py` | Renderiza a animação de "O abrigo" (anim3_abrigo.py) em paralelo, um plano por processo, e monta o vídeo com a voz. |
| `anim_abrigo2.py` | Animação da parte 2 de "O abrigo" (26/10/2026) por cima do storyboard (story_abrigo2.py): cada plano é montado duas vezes, no estado de início (FIM=False) |
| `anim_abrigo2_rodar.py` | Renderiza a animação da parte 2 de "O abrigo" em paralelo e monta o vídeo com a voz-teste. |
| `anim_ep1.py` | Trânsito Brasil 3D, ep. 1: RASCUNHO ANIMADO (meia resolução, com a voz; sem efeitos sonoros). Câmera PLANEJADA de cada plano (pré-passagem da simulação, filtrada), |
| `anim_ep1_planos.py` | Trânsito Brasil 3D, ep. 1: planos do RASCUNHO ANIMADO (python puro). Parte da decupagem aprovada (story_ep1_planos.PLANOS) e acrescenta: |
| `anim_ep1b.py` | Trânsito Brasil 3D, ep. 1, v2 (TUDO DE CIMA, 1080x1920 sem painel): RASCUNHO ANIMADO (meia resolução, com a voz; sem efeitos sonoros). Câmera PLANEJADA de cada plano (pré |
| `anim_ep1b_planos.py` | Trânsito Brasil 3D, ep. 1, rascunho v2 (26/10, depois de "tem que ser visto do alto, sem barra branca, takes demais, mais contraste"): |
| `anim_ep1c.py` | Trânsito Brasil 3D, ep. 1, v2 (TUDO DE CIMA, 1080x1920 sem painel): RASCUNHO ANIMADO (meia resolução, com a voz; sem efeitos sonoros). Câmera PLANEJADA de cada plano (pré |
| `anim_ep1c_planos.py` | Trânsito Brasil 3D, ep. 1, rascunho v3 (27/10/2026), roteiro curto de 8 falas (~43 s), depois de "prolixo, repete, a parada tem que aparecer já": |
| `anim_passos.py` | Animação de "E se cada passo dobrasse a sua altura?" em cima do storyboard v2 (story_passos2.py; aprovado em 25/10/2026). |
| `anim_passos3.py` | Animação v3 de "os passos" (plano v3; pedido de 25/10/2026: "quando ele dá um passo já dá um impacto, cresce quase na hora, num bounce |
| `anim_passos3_rodar.py` | Renderiza a animação de "os passos" (anim_passos.py) em paralelo, um plano por processo, e monta o vídeo com a voz. |
| `anim_passos4.py` | Animação da abertura v4 de "os passos" (aprovada em 25/10/2026: "anima a abertura v4"). Planos em story_passos4.py; da fala 4 em diante |
| `anim_passos4_rodar.py` | Renderiza a animação de "os passos" (anim_passos.py) em paralelo, um plano por processo, e monta o vídeo com a voz. |
| `anim_passos6.py` | Animação do plano v7 de "os passos" (aprovado em 25/10/2026). Planos em story_passos6.py (falas 1 a 7); da fala 8 em diante vale o v6 (anim_passos3/4). |
| `anim_passos6_rodar.py` | Renderiza a animação de "os passos" (anim_passos.py) em paralelo, um plano por processo, e monta o vídeo com a voz. |
| `anim_passos7.py` | Animação do plano v7 de "os passos" (aprovado em 25/10/2026). Planos em story_passos6.py (falas 1 a 7); da fala 8 em diante vale o v6 (anim_passos3/4). |
| `anim_passos7_rodar.py` | Renderiza a animação de "os passos" (anim_passos.py) em paralelo, um plano por processo, e monta o vídeo com a voz. |
| `anim_passos8.py` | Animação do replanejamento v14 (aprovado em 26/10/2026). Planos em story_passos8.py; o resto do filme vem do v7 (anim_passos7). |
| `anim_passos8_rodar.py` | Renderiza a animação de "os passos" (anim_passos.py) em paralelo, um plano por processo, e monta o vídeo com a voz. |
| `anim_passos9.py` | Animação do replanejamento v15 (aprovado em 26/10/2026). Planos em story_passos9.py; o resto vem do v14 (anim_passos8). |
| `anim_passos9_rodar.py` | Renderiza a animação de "os passos" (anim_passos.py) em paralelo, um plano por processo, e monta o vídeo com a voz. |
| `anim_passos_rodar.py` | Renderiza a animação de "os passos" (anim_passos.py) em paralelo, um plano por processo, e monta o vídeo com a voz. |
| `anim_semosso_teste.py` | Teste de animação do Sem-Osso (26/10/2026: "melhorar a animação do monstro para não ficar duro e sem graça"). |
| `area.py` | Área segura do Reels (1080 x 1920). Medidas mais citadas para Meta em 2025–2026: livre 270 px em cima, |
| `armas.py` | Armas de desenho (chapadas, com contorno e borda de luz), para cenas narradas. Nada realista: só a silhueta que se reconhece. |
| `audita_elenco.py` | Auditoria de direção de cena de "O abrigo" (pedido de 25/10/2026: "revise se eu apareço nas cenas ou em primeira pessoa; mais direções de cena quebradas"): |
| `balanca.py` | A balança GANHO × RISCO que acompanha a subida: coluna, travessão que inclina, dois pratos pendurados. |
| `cartel.py` | História: Primeiro dia no cartel. blender -b -P cartel.py -- [--still N:SEG] [--out DIR] [--scale 0.5] [--samples 16] |
| `cena.py` | Cenários com profundidade (estilo 2D chapado com parallax real), em duas atmosferas: |
| `cenario3d_abrigo.py` | O abrigo por dentro em 3D de verdade (pedido de 24/10/2026: "modelar mais, tudo muito flat"). |
| `char2d.py` | Personagem 2D recortado, versão 2 (estilo IfverseTales). |
| `character_sheet.py` | Ficha de personagem: vistas (frente, 3/4, lado, costas), expressões e poses. |
| `cidade3d.py` | A rua do bairro de "O abrigo" em 3D de verdade (pedido de 24/10/2026: "deixar a cidade um pouco mais viva, ela está muito flat"). |
| `cinema3d.py` | (sem descrição) |
| `closeup.py` | (sem descrição) |
| `colisao.py` | Detector de colisão entre objetos e personagens (pedido de 23/10/2026: "bugs dos props, parece que tá se colidindo"). |
| `colisao_passos.py` | Conferência de colisão do storyboard v2 de "os passos" (pedido de 25/10/2026: "melhorar as colisões"). |
| `compoe_ep1.py` | Trânsito Brasil 3D, ep. 1: compõe o rascunho (system python, PIL). Cada quadro: a cena (1080x1350 x escala) em cima e o painel embaixo (570 px x escala): |
| `compoe_ep1b.py` | Trânsito Brasil 3D, ep. 1, v2: compõe o rascunho em TELA CHEIA (sem painel, sem legenda de cores): a cena de cima, as pílulas de texto no alto e a legenda |
| `compoe_ep1c.py` | Trânsito Brasil 3D, ep. 1, v2: compõe o rascunho em TELA CHEIA (sem painel, sem legenda de cores): a cena de cima, as pílulas de texto no alto e a legenda |
| `contraste.py` | Contraste entre o objeto-chave e o que está atrás dele (regra de 23/10/2026: "tem que dar para identificar os objetos"). |
| `curvas.py` | Curvas de movimento no estilo do editor de gráficos do After Effects: o progresso s(u) de 0 a 1 vem de uma |
| `decupagem_tempos_abrigo2.py` | Acerta os tempos da decupagem da parte 2 do abrigo nas palavras da voz. |
| `dinheiro.py` | Dinheiro que se reconhece de longe: nota de R$ 100 (azul) com o "100" e a cinta de papel, maço visto de frente, |
| `elenco.py` | Elenco do canal (pedido de 23/10/2026: "os outros personagens ficam sem rosto, simplificados demais; dar vida a eles"). |
| `elenco3d_abrigo.py` | O elenco de "O abrigo" em 3D de verdade (mesmo desenho do 2D, com volume e câmera livre), para as cenas em que a gente mescla: |
| `elenco_abrigo.py` | Elenco do vídeo "O abrigo" (pedido de 24/10/2026: "mais seriedade, personagens mais maduros, paleta de The Walking Dead"). |
| `elenco_reflexo.py` | Elenco do vídeo "E se o seu cérebro fosse 10 vezes mais rápido?" (mesmo boneco, mesmo traço do elenco do presidente). |
| `esguio_view.py` | (sem descrição) |
| `ficha.py` | Ficha do personagem: cada página vira uma grade de células renderizadas (com legenda) + faixa de título. |
| `ficha3.py` | Ficha do protagonista v3 (rosto como foco). Cada página = grade de células com legenda + faixa de título. |
| `ficha3_montar.py` | Junta as células renderizadas em páginas. python3 ficha_montar.py DIR_DAS_CELULAS DIR_SAIDA |
| `ficha_3d.py` | Prancha do herói em 3D: quatro ângulos (de frente, 3/4, de lado e de costas) de um figurino. |
| `ficha_abrigo.py` | Ficha do vídeo "O abrigo": elenco de frente, elenco de 3/4, objetos pequenos (a e b) e cenário, cada prancha num PNG com os rótulos em JSON. |
| `ficha_abrigo2.py` | Ficha da parte 2 de "O abrigo" (26/10/2026): o Sem-Osso, a gosma, o esqueleto que fica, o grupo de 9, o galpão, os objetos e a torre. |
| `ficha_abrigo2_montar.py` | Monta as 3 pranchas da ficha da parte 2 de "O abrigo" a partir dos renders do ficha_abrigo2.py. |
| `ficha_elenco.py` | Ficha de personagens e objetos do Canal 38 (model sheet). Três pranchas renderizadas e montadas com os nomes: |
| `ficha_ep1_montar.py` | Monta a prancha da ficha do ep. 1 do Trânsito Brasil 3D a partir de ficha-{tipo,objetos,topo}.png (system python, PIL). |
| `ficha_montar.py` | Monta a prancha da ficha (elenco + objetos) com os nomes, a partir das renderizações de ficha_elenco.py. |
| `ficha_montar_3d.py` | Monta a prancha do herói em 3D (3 figurinos x 4 ângulos). python3 ficha_montar_3d.py PASTA SAIDA.png |
| `ficha_montar_abrigo.py` | Monta a ficha de "O abrigo" (elenco + objetos) com os nomes. python3 ficha_montar_abrigo.py PASTA SAIDA.png |
| `ficha_montar_reflexo.py` | Monta a ficha do reflexo (elenco + objetos) com os nomes. python3 ficha_montar_reflexo.py PASTA SAIDA.png |
| `ficha_narrador.py` | Ficha do narrador ("eu") de "O abrigo": de frente, de três quartos e pedalando de lado. |
| `ficha_narrador_montar.py` | python3 ficha_narrador_montar.py PASTA SAIDA.png |
| `ficha_passos.py` | Ficha de elenco, objetos e poses de "E se cada passo dobrasse a sua altura?" (plano de cena v2, 25/10/2026). |
| `ficha_passos_montar.py` | Renderiza a ficha de "os passos" em paralelo e monta as pranchas (elenco, poses, objetos, Burj e palco). |
| `ficha_reflexo.py` | Ficha do vídeo do reflexo: elenco de frente, elenco de 3/4 e objetos (pequenos e de cenário), cada prancha num PNG com os rótulos em JSON. |
| `frente.py` | O herói de frente de verdade (view="front"): braços espelhados e a pose sentada vista de frente. |
| `grana.py` | Dinheiro verde em volume (pedido do usuário: "o dinheiro tem que ser verde" e "mostrar em volume"). |
| `heroi.py` | Protagonista v3 (estilo IfverseTales), com foco no rosto. |
| `heroi3d.py` | O herói em 3D de verdade, v2 (pedido de 23/10/2026: "tá muito low-poly, muito simplista; não aparece um boneco estilo nosso"). |
| `human.py` | Humano de malha contínua (Skin modifier) + esqueleto + pesos calculados + roupa por região + rosto. |
| `ik3_abrigo.py` | Cinemática inversa dos braços do Heroi3D (dois ossos, em matemática pura: sem atualizar a cena a cada tentativa). |
| `insertos.py` | Objetos dos insertos (o objeto em foco em tela cheia): celular na mão, contador de dígitos girando. |
| `legenda_passos.py` | Legenda de "os passos" (pedido de 26/10/2026: "bota a legenda palavra por palavra no centro, apenas uma palavra por vez, com efeito de bounce"). |
| `lib.py` | Kit 3D para histórias curtas. Roda dentro do Blender (blender -b -P ...). |
| `limbs.py` | Membros "mangueira" (método RubberHose): o braço/perna é uma curva que passa por 3 juntas |
| `limpo.py` | Palco limpo (estilo IfverseTales): parede e chão numa cor só, escuros e dessaturados, uma luz única |
| `luz.py` | Luz de cinema em 2D falso: facho volumétrico em camadas (miolo forte, borda que some aos poucos), |
| `make_voice.py` | Gera a voz de cada linha (macOS say), mede a duração e escreve timing.json. |
| `mapa_topo.py` | VISÃO AMPLA do mundo fixo, de cima (pedido de 25/10/2026: "você precisa ter uma visão ampla para os objetos não colidirem; tem que dar um espaço"). |
| `measure.py` | mede a trajetória da cabeça vs quadril a partir de /tmp/anim_curves.json e desenha num PNG. |
| `mede_mov.py` | Medidor de movimento (pedido de 23/10/2026: "movimento muito travado, muito duro; a câmera sem as ondas in/out"). |
| `mix_pcc7.py` | Mixagem do PCC v7: narração (Lucas) + música tensa (abaixa sozinha quando ele fala) + efeitos presos às palavras e aos cortes. |
| `mix_pcc7b.py` | Mixagem do PCC v7b: voz na frente, música clássica sutil com camadas de volume, efeitos baixos. |
| `mixagem_abrigo.py` | Mixagem com guarda de voz: a voz manda; música e efeitos nunca competem com ela. |
| `monta_fecho.py` | Junta a fala do fecho (a pergunta do narrador 3D) à narração aprovada: narracao_final.wav, palavras_final.json e tempos_final.json. |
| `montar_pcc.py` | Monta o vídeo PCC: cor de cada plano, emenda, selos/legendas por cima e áudio. |
| `montar_teste.py` | Monta só os trechos já renderizados (para aprovar um pedaço antes do vídeo todo): cor de cada plano, texto por cima e a |
| `motion.py` | Movimento do protagonista com conceitos clássicos de animação. |
| `mundo7.py` | O MUNDO FIXO de "os passos" (crítica de 25/10/2026: "o prédio some; a cada hora o cenário muda; está sempre mostrando as mesmas cenas; tem que ser o mesmo |
| `mundo7_v8_colorido.py` | O MUNDO FIXO de "os passos" (crítica de 25/10/2026: "o prédio some; a cada hora o cenário muda; está sempre mostrando as mesmas cenas; tem que ser o mesmo |
| `musica_abrigo.py` | Trilha de rascunho de "O abrigo", sintetizada (sem custo): segue a história em ondas, com silêncios onde o filme fica sem som. |
| `musica_abrigo_mix.py` | Trilha dramática de "O abrigo" (pedido de 25/10/2026: "não teve uma música dramática; troca de músicas, também dramáticas"): |
| `musica_passos_mix.py` | Trilha de "os passos" (pedido de 26/10/2026: "faz o som, trilha e um efeito por ação"): costura TRECHOS das trilhas orquestrais que o Paulo já aprovou |
| `mux.py` | Junta os quadros PNG + a voz de cada linha num mp4 final. Uso: python3 mux.py render out.mp4 |
| `objetos.py` | Objetos do canal com acabamento de ficha (contorno de tinta, sombra e brilho por dentro, como o boneco). |
| `objetos3d_abrigo.py` | Objetos de "O abrigo" modelados em 3D de verdade (pedido de 24/10/2026: "tem muitos objetos meio planos; a mão parece um papel; |
| `objetos3d_abrigo2.py` | Peças novas da parte 2 de "O abrigo" (26/10/2026), no mesmo estilo do kit (heroi3d.estilo: tom chapado, faixa de sombra, borda de luz, contorno): |
| `objetos3d_abrigo_b.py` | Objetos 3D de "O abrigo", parte 2 (decupagem v3, 25/10/2026): o que faltava em 3D para os planos fechados de até 1,3 s. |
| `objetos3d_passos.py` | Objetos 3D de "E se cada passo dobrasse a sua altura?" (plano de cena: personagem/passos/plano-de-cena-v1.md). |
| `objetos3d_passos_b.py` | Objetos novos do plano de cena v2 de "E se cada passo dobrasse a sua altura?" (25/10/2026): |
| `objetos_abrigo.py` | Objetos do vídeo "O abrigo" (mesmo acabamento de ficha: tinta, sombra e brilho por dentro). |
| `objetos_reflexo.py` | Objetos do vídeo "E se o seu cérebro fosse 10 vezes mais rápido?" (mesmo acabamento de ficha: tinta, sombra e brilho por dentro). |
| `overlay_abrigo.py` | Camada de texto do vídeo "O abrigo" (mesma régua do presidente: legenda em trechos curtos que acendem por palavra; no lugar do nível, o selo DIA n): textos discretos, que |
| `overlay_pcc.py` | Camada de selos de nível, legendas e números do vídeo PCC (feita em PIL, sem desfoque de câmera). |
| `overlay_pcc3.py` | Camada de texto do PCC v4 ("Você acabou de entrar no PCC"): legendas e rótulo do nível, com entrada suave. |
| `overlay_pcc4.py` | Camada de texto do PCC v7 (voz da ElevenLabs): textos discretos, que entram, dizem e saem. |
| `overlay_presidente.py` | Camada de texto do vídeo do presidente corrupto (mesma régua do PCC v7): textos discretos, que entram, dizem e saem. |
| `overlay_reflexo.py` | Camada de texto do vídeo do reflexo (derivada do overlay do presidente, sem níveis e com os contadores do reflexo) (mesma régua do PCC v7): textos discretos, que entram,  |
| `palavras.py` | Tempo de cada palavra da narração (para sincronizar gestos, selos e legendas). |
| `plano_som_abrigo.py` | Plano de som de "O abrigo" (pedido de 25/10/2026: "colocar efeitos sonoros"): um efeito por ação, no QUADRO da ação (não na palavra). |
| `plano_som_passos.py` | Plano de som de "os passos" (pedido de 26/10/2026: "faz o som, trilha e um efeito por ação"). Um efeito por ação que a imagem mostra, no instante da ação |
| `plano_som_pcc7.py` | Plano de som do PCC v7 (modelo para os próximos temas): cada efeito preso a uma palavra ou a um corte, e as subidas da música. |
| `plano_som_presidente.py` | Plano de som do presidente corrupto (mesma régua do PCC v7): cada efeito preso à palavra e à ação que a imagem mostra, |
| `plano_som_reflexo.py` | Plano de som do reflexo: um som por ação, no QUADRO da ação (a mesma conta do prod: F(t) = 1 + round(t*24), T(f) = (f-1)/24). |
| `plot_curves.py` | desenha as curvas de /tmp/anim_curves.json num PNG (sem bibliotecas): python3 plot_curves.py saida.png canal1,canal2,... |
| `pos_cctv.py` | Visual de câmera de segurança (pedido de 24/10/2026: "aquela câmera de segurança, com aquele feitinho de câmera de segurança"). |
| `pos_fuji.py` | Efeito Fuji (filme) de "O abrigo", a pós do fim da fila (pedido de 24/10/2026): olhar de negativo de cinema colorido (Fujifilm Eterna): |
| `poses_passos.py` | As poses do "eu" para "E se cada passo dobrasse a sua altura?" (ficha de poses, plano de cena v2). |
| `prod_abrigo.py` | Canal 38: "O abrigo" (nossa versão de um vídeo de bunker; voz do Lucas, 71,7 s). Roteiro: roteiros/abrigo.json; ficha aprovada em 24/10/2026. |
| `prod_pcc.py` | Produção do vídeo PCC (5 níveis). Cada plano é um cenário próprio, renderizado à parte e montado depois. |
| `prod_pcc2.py` | PCC, versão 2: um acontecimento a cada ~1 s (roteiros/decupagem-pcc.md). |
| `prod_pcc3.py` | PCC, versão 3: 15 cenas planejadas (roteiros/decupagem-pcc.md e personagem/pcc/storyboard). |
| `prod_pcc4.py` | PCC, versão 4: roteiro "Você acabou de entrar no PCC" (roteiros/pcc3.json, voz em roteiros/voz-pcc3). |
| `prod_pcc5.py` | PCC v4, cenas dos níveis (a partir de 8,89 s): um cenário próprio por cena, cortes em movimento (transicao.py), |
| `prod_pcc6.py` | PCC v4, cenas dos níveis refeitas com linguagem de cinema (a partir de 8,89 s): |
| `prod_presidente.py` | Canal 38: "Você acabou de virar um presidente corrupto do Brasil" (ficção com esquemas reais; voz do Lucas, 83 s). |
| `prod_reflexo.py` | Canal 38: "E se o seu cérebro fosse 10 vezes mais rápido?" (voz do Lucas, 50 s). Roteiro: roteiros/reflexo.json. |
| `profundidade.py` | PROFUNDIDADE (crítica de 25/10/2026: "não tem contraste nem ponto de foco; precisa ter depthmap"). |
| `prop_compare.py` | (sem descrição) |
| `props.py` | Objetos e cenários 2D chapados das histórias (mesmo estilo do protagonista: forma chapada, contorno fino de |
| `proto2d.py` | Prova do estilo IfverseTales: boneco 2D andando, fundo em camadas, câmera que só desliza. |
| `proto_ifv.py` | Protótipo de cena no estilo IfverseTales: rua ao entardecer, personagem andando, câmera com parallax e desfoque. |
| `provas_passos3.py` | Provas do plano de cena v3 de "os passos" (pedido de 25/10/2026: "a primeira cena não dá para entender, ele já começa grande; |
| `provas_passos4.py` | Provas da abertura v4 de "os passos" (crítica de 25/10/2026 ao v3: "em 5 segundos deu 3 cortes da mesma cena; a primeira cena tem que ser |
| `provas_passos5.py` | Provas do plano v7 de "os passos" (crítica de 25/10/2026: "dos 5 aos 7 s não acontece nada; ao sair da cena dos 10 s parece outro cenário e o amigo some; |
| `provas_passos7.py` | Provas do replanejamento de 25/10/2026 (crítica ao v13: "aos 39 s fica travando; a vista de 150 km bugou; na altura da boca a mão ficou dentro do peito; |
| `provas_passos8.py` | Provas do replanejamento v15 de "os passos" (pedido de 26/10/2026: "segue para os planos que faltam, 8E em diante, no mesmo padrão"). |
| `puppet2d.py` | Boneco 2D recortado (estilo IfverseTales) montado dentro do Blender. |
| `quadro.py` | Planejamento de quadro: a câmera é calculada a partir do que PRECISA aparecer (a "caixa do assunto"), e um conferente |
| `render_kling.py` | Renderiza UM plano do blockout para o Kling 4.0 (pedido de 23/10/2026: "o vídeo vira o esqueleto da versão realista"): |
| `render_pcc.py` | Renderiza os planos do PCC em paralelo. |
| `rostos.py` | Onde estão os rostos na tela, quadro a quadro (pedido de 23/10/2026: "cuidado para as coisas não ficarem na frente do rosto, |
| `roteiro_doc.py` | Gera roteiros/ROTEIROS.md a partir dos JSON dos roteiros + tempos da voz + fontes. |
| `semantico.py` | Recursos semânticos (o que a pessoa entende sem pensar): tamanho real das coisas, comparação de escala, |
| `sets.py` | Cenários chapados com profundidade (estilo IfverseTales): cor plana + névoa por distância da câmera. |
| `sets2d.py` | Cenários em camadas planas (estilo IfverseTales). Cada elemento é uma forma de frente para a câmera |
| `sets4.py` | Peças de cenário do PCC v4: cada cena tem um lugar próprio. Tudo chapado, com borda de luz, na paleta índigo. |
| `sfx_abrigo.py` | Efeitos sonoros sintetizados de "O abrigo" (sem custo, só numpy): um som próprio para cada ação que a imagem mostra, no mesmo timbre. |
| `sfx_passos.py` | Efeitos sonoros sintetizados de "os passos" (pedido de 26/10/2026: "faz o som, trilha e um efeito por ação"). Só numpy, sem custo, no mesmo timbre do abrigo |
| `sfx_reflexo.py` | Efeitos sintetizados do reflexo (o tempo que dobra), no mesmo timbre do sfx.py da skill: |
| `sheet.py` | junta os quadros de teste de uma cena numa tira: python3 sheet.py PASTA PREFIXO SAIDA.jpg |
| `so_rostos.py` | Grava só o rostos.json das cenas (monta cada cena sem renderizar), para quando o render já existe. |
| `stick.py` | Personagem no estilo IfverseTales: boneco de cabeça redonda, moletom, membros finos, |
| `stick_sheet.py` | Ficha do personagem estilo IfverseTales. |
| `story3_abrigo.py` | Storyboard v3 de "O abrigo" (decupagem v3: personagem/abrigo/decupagem-cinema-v3.md): 67 planos de no máximo 1,3 s, um quadro parado por plano, |
| `story3_doc.py` | Escreve a decupagem v3 de "O abrigo" em texto a partir do SHOTS (a mesma tabela que renderiza o storyboard). |
| `story3_montar.py` | Monta as pranchas do storyboard v3 de "O abrigo": uma faixa por fala (título, tempo, fala e mensagem) com um quadro por plano e, embaixo de |
| `story3_rodar.py` | Renderiza planos do storyboard v3 em paralelo e monta uma folha de contato para conferir. |
| `story_abrigo.py` | Storyboard renderizado de "O abrigo" (decupagem: personagem/abrigo/decupagem-cinema.md): um quadro parado por plano, com a lente, |
| `story_abrigo2.py` | Storyboard da parte 2 de "O abrigo" (26/10/2026): um quadro parado por plano da decupagem (personagem/abrigo/decupagem-parte2.md, tabela em roteiros/abrigo2_planos.json), |
| `story_abrigo2_folha.py` | Folha de contato de revisão do storyboard da parte 2: python3 story_abrigo2_folha.py PASTA SAIDA.png ID [ID ...] [--cols 4] [--w 270] |
| `story_abrigo2_rodar.py` | Renderiza o storyboard da parte 2 de "O abrigo" (story_abrigo2.py) em paralelo, aplica a luz do pós (fim de tarde, noite, flashback, galpão), |
| `story_ep1_montar.py` | Monta as pranchas do storyboard do ep. 1 e a decupagem em texto a partir dos quadros de personagem/transito/story-ep1 e da tabela story_ep1_planos.py. |
| `story_ep1_planos.py` | Trânsito Brasil 3D, ep. 1: tabela dos planos (python puro). Usada pelo storyboard (tb_story_ep1.py), pela decupagem em texto e, depois, pela animação. |
| `story_montar_abrigo.py` | Monta as pranchas do storyboard de "O abrigo": uma faixa por cena (título, fala e mensagem) com os quadros de cada plano e, |
| `story_passos.py` | Storyboard de "E se cada passo dobrasse a sua altura?" (plano: personagem/passos/plano-de-cena-v1.md; voz: roteiros/voz-passos, 80,26 s). |
| `story_passos2.py` | Storyboard v2 de "E se cada passo dobrasse a sua altura?" (plano: personagem/passos/plano-de-cena-v2.md; ficha v2 aprovada em 25/10/2026). |
| `story_passos2_montar.py` | Monta as pranchas do storyboard de "os passos": 10 planos por prancha (5 x 2), com o id, o tempo, a lente e as palavras de cada plano. |
| `story_passos2_rodar.py` | Renderiza planos do storyboard de "os passos" em paralelo e monta uma folha de contato para conferir. |
| `story_passos3.py` | Storyboard v3 de "E se cada passo dobrasse a sua altura?" (plano: personagem/passos/plano-de-cena-v3.md; pedido de 25/10/2026: |
| `story_passos4.py` | Abertura v4 de "os passos" (aprovada em 25/10/2026; plano em personagem/passos/abertura-v4.md, provas em provas_passos4.py). |
| `story_passos6.py` | Plano v7 de "os passos" (aprovado em 25/10/2026: "anima o plano v7 com os dois ângulos"; personagem/passos/plano-v7.md). |
| `story_passos7.py` | Plano v7 de "os passos" (aprovado em 25/10/2026: "anima o plano v7 com os dois ângulos"; personagem/passos/plano-v7.md). |
| `story_passos8.py` | Replanejamento v14 de "os passos" (aprovado em 26/10/2026; personagem/passos/replanejo-v14.md, provas em provas_passos7.py). |
| `story_passos9.py` | Replanejamento v15 de "os passos" (aprovado em 26/10/2026; personagem/passos/replanejo-v15.md, provas em provas_passos8.py). |
| `story_passos_montar.py` | Monta as pranchas do storyboard de "os passos": 10 planos por prancha (5 x 2), com o id, o tempo, a lente e as palavras de cada plano. |
| `story_passos_rodar.py` | Renderiza planos do storyboard de "os passos" em paralelo e monta uma folha de contato para conferir. |
| `storyboard_pcc.py` | Storyboard do PCC (versão 3): 15 cenas, cada uma com o quadro final diagramado na grade 9:16, a ordem em que os |
| `sync.py` | mede o atraso do braço em relação à perna oposta durante a caminhada (quadros) e a amplitude do quadril |
| `tb_assets.py` | Trânsito Brasil 3D: biblioteca de veículos e objetos de via (Blender por script). |
| `tb_brilho.py` | Trânsito Brasil 3D: brilho (bloom) das luzes, fora do Blender. Para o estilo noite. |
| `tb_camera_suave.py` | Trânsito Brasil 3D: curvas de câmera suaves (python puro, sem Blender). |
| `tb_cena.py` | Trânsito Brasil 3D: cena, luz, câmera e render (EEVEE por padrão, Cycles opcional). |
| `tb_colisao.py` | Trânsito Brasil 3D: conferidor de colisão e de profundidade (roda sem renderizar). |
| `tb_compoe_sanfona.py` | Trânsito Brasil 3D: monta os quadros finais da cena do efeito sanfona (1080x1920): cena em cima, legenda em pílula com linha até o carro, |
| `tb_ficha.py` | Trânsito Brasil 3D: ficha de veículos e objetos de via, numa pista de estúdio vista de cima em 3/4. |
| `tb_ficha_ep1.py` | Trânsito Brasil 3D, ep. 1: ficha de elenco e objetos no visual didático (mapa claro, pista escura, carros brilhantes). |
| `tb_mapa.py` | Trânsito Brasil 3D: monta o mapa 3D a partir do JSON do OpenStreetMap (tb_osm.py), em um dos estilos. |
| `tb_mede_camera.py` | Trânsito Brasil 3D: mede o movimento da câmera (roda no python do sistema). |
| `tb_osm.py` | Trânsito Brasil 3D: converte um recorte do OpenStreetMap (.osm em XML, da API 0.6) num JSON limpo em metros. |
| `tb_sanfona.py` | Trânsito Brasil 3D: cena didática do EFEITO SANFONA na Marginal Pinheiros (expressa). |
| `tb_story_ep1.py` | Trânsito Brasil 3D, ep. 1: STORYBOARD RENDERIZADO das 13 falas, nas quatro vistas, sobre os tempos reais da voz (roteiros/voz-transito/tempos.json). |
| `tb_teste.py` | Trânsito Brasil 3D: testes de estilo do mapa. |
| `tb_trafego.py` | Trânsito Brasil 3D: faixas de rodagem e simulação de tráfego (modelo IDM: cada motorista acelera até a sua velocidade |
| `tb_xt.py` | Trânsito Brasil 3D: desenha o diagrama espaço-tempo (roda no python do sistema, que tem matplotlib). |
| `tempo.py` | Leva os tempos de uma narração antiga para uma nova (mesmas falas, outra voz/outro texto). |
| `teste3d_abrigo.py` | Provas dos objetos 3D de "O abrigo". blender -b -P teste3d_abrigo.py -- MODO SAIDA.png [--scale 0.5] |
| `titulo3d.py` | Título 3D do episódio dentro do ambiente (pedido de 23/10/2026): letras em 3D com volume, acima do herói, |
| `transicao.py` | Transição invisível: corte em movimento (match cut por velocidade). |
| `trono.py` | Cena do rei: trono simétrico no alto de um estrado, o herói sentado DE FRENTE, uma luz de cima e um halo atrás, |
| `unidades.py` | Unidades de dinheiro do canal (regra de 23/10/2026: todo número vira proporção, simples como livro infantil). |
| `uniforme.py` | Roupa de presidiário para o herói: camisa listrada (listras horizontais recortadas na silhueta da jaqueta), |
| `vida.py` | Vida contínua na cena (pedido de 23/10/2026: "as coisas estão muito paradas; trazer o displacement dos rostos para os objetos; |
| `voz.py` | Voz do narrador com a voz do Mac (comando say), frase por frase. |
| `voz_eleven.py` | Narração da ElevenLabs (um arquivo só) → narracao.wav + tempos.json + palavras.json no mesmo formato da voz do Mac. |
| `voz_medida.py` | Mede um trecho de voz: duração, nível (rms) e tom mediano (autocorrelação). O tom do Lucas não pode afundar (< ~110 Hz) nem mudar entre trechos. |
| `voz_monta_transito.py` | Trânsito Brasil 3D, ep. 1: monta a narração a partir dos 13 trechos do Lucas (roteiros/voz-transito/curtos/cNN.mp3), SEM mexer no tom: |
| `voz_monta_transito2.py` | Trânsito Brasil 3D, ep. 1: monta a narração a partir dos 9 trechos do Lucas (roteiros/voz-transito/curtos/cNN.mp3), SEM mexer no tom: |
| `voz_teste_abrigo2.py` | Voz-TESTE da parte 2 do abrigo (pedido de 26/10/2026: "vozes-teste primeiro, a ElevenLabs só no final"). |
| `canal38_env.py` | caminhos do projeto e do Blender (variáveis `CANAL38_PROJETO` e `CANAL38_BLENDER`) |
