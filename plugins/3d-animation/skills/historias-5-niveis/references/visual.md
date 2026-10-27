# Imagem: identidade, planos, cor, animação

## Identidade
- **Estilo:** 2D falso no estilo @IfverseTales. Boneco recortado (cabeça redonda preta, membros finos, contorno escuro e borda de luz) em cenário de cor chapada com profundidade. A câmera só desliza ou avança, sem girar, com rotação fixa em 90° no X. Se girar, o boneco "vira papel".
- **Herói da série:** preto, uniforme listrado de presidiário com um **X vermelho** no peito, sem número (`uniforme.heroi_preso`). Ele mostra o rosto: olho branco sem pupila, sobrancelha fina, muitas bocas e extras (suor, !, brilho, cifrão nos olhos).
- **Escala única:** herói e figurantes com 1,75 m. Ele já foi recusado com escala 1,32: "ficou o maior de todos".
- **Dinheiro sempre verde e com volume:** `grana.bloco(..., zk=3)`. Nunca placa fina.

## Número vira proporção, simples como desenho para criança (regra de 23/10/2026)
Falar muito número confunde: a pessoa não entende o que aquilo representa. **Todo número aparece como proporção**, e o reconhecimento é visual e auditivo ao mesmo tempo.

Use um **sistema de unidades fixo**, o mesmo em todos os vídeos, para o cérebro aprender uma vez e reconhecer sempre:

| Unidade | Desenho | Som | Escala |
|---|---|---|---|
| **1 salário mínimo** | uma notinha verde pequena | `tique` | — |
| **R$ 1 milhão** | um maço (cubo de cerca de 23 cm em notas de R$ 100) | toque de papel | — |
| **R$ 1 bilhão** | um cubo de cerca de 2,3 m | `boom` grave | o herói (1,75 m) fica do lado, como régua |

- **Comparações do dia a dia:** um trabalhador com 1 notinha ao lado de alguém com 100; "1 milhão por dia" é um calendário que vira e solta um maço por folha; "800 anos" é uma fila de vidas de trabalho ou uma ampulheta.
- **Cada número tem uma imagem e um som.** O som da unidade se repete quando ela aparece, conta ou enche, para quem só está ouvindo também "ver" o tamanho.
- **Simples como livro infantil, mas pensado com cuidado:** formas grandes e chapadas, poucas cores e um objeto principal por plano. Corte os detalhes específicos que não ajudam a entender (carimbos, papéis, mapas cheios, objetos decorativos de sobra). O desenho não é didático demais; ele mostra a ideia de um jeito que se entende de primeira.
- **Quantidade de verdade:** se a fala diz 25, aparecem 25; se diz 45 bilhões, aparecem 45 cubos. A proporção tem de ser honesta.

## Direção cinematográfica (correção forte de 23/10/2026, presidente v1)
Ele recusou a v1 do presidente: "abstrata demais", "tela vazia", "demora para acontecer", "sem dinamismo", "a direção de cena não está legal". As proporções certas não bastam; elas precisam acontecer **dentro de uma cena dramática que representa o fato**.
- **Cena que representa a ação:** suborno é uma negociação numa sala escura, com uma luz só pendurada sobre a mesa entre duas pessoas, gente em silhueta ao fundo olhando, e o envelope deslizando para a luz. Não é dois bonecos num fundo liso.
- **Luz dramática:** uma fonte principal (lâmpada, janela, sirene), sombra funda, borda de luz nas silhuetas, feixe com poeira.
- **3 a 5 planos por cena:** close do rosto, inserto das mãos ou do objeto, por cima do ombro, de baixo. A câmera está **sempre andando** (empurra, desliza, sobe).
- **Primeiro plano desfocado** passando na frente: ombro, coluna, encosto, garrafa.
- **Algo acontece a cada 1 s, preso à palavra.** Nada de tela vazia esperando a palavra-chave: o objeto já está em cena e reage ao que a voz diz.
- **O herói atua:** gestos (empurrar o envelope, esfregar as mãos, apontar, se encolher) e expressão a cada frase.
- **Ambiente 3D de verdade, não fundo chapado** (crítica do segundo teste): use `ambiente3d.py`.
  - `sala`: chão de tábuas ou lajotas em perspectiva, paredes laterais com pilastras, teto com vigas.
  - Peças: `colunata`, `tapete`, `janela_lateral`, `persiana`.
  - A câmera entra no espaço e anda em profundidade:
    - avanço atravessando cabeças em primeiro plano;
    - grua descendo da lâmpada até a mesa (alt0 alto → alt1 baixo);
    - deslize lateral no close;
    - recuo que sobe revelando o lugar (sem afastar demais, para os bonecos não ficarem minúsculos).
  - Contraste de luz quente e fria: lâmpada quente na frente e janela fria atrás, com as silhuetas contra a luz.
  - Vinheta escura no chão perto da câmera.
  - Colunas e enfeites em tom apagado, para não poluir.
- **Contraste medido, não no olho** (crítica de 23/10/2026: "problemas de contraste para identificar os objetos").
  - A cabeça e o corpo do herói são escuros. Se o fundo atrás deles também é escuro, eles somem: no Mensalão deu 1,2:1.
  - Meta: **3:1 ou mais** entre cada objeto-chave e o que está atrás dele. Meça com `kit3d/contraste.py`: liste os pares e ajuste até dar OK.
  - Receita que funcionou (o palácio aprovado tem 4,6:1):
    - parede de fundo em tom médio, não preta;
    - halo de luz quente atrás de quem fala (`cena.disc` radial, alfa 0,75);
    - silhuetas do fundo contra uma janela clara;
    - frente da mesa mais clara que o chão;
    - contorno escuro em objeto claro sobre superfície clara (envelope).
  - O clima continua escuro nas bordas (teto, chão perto da câmera); o tom médio fica só atrás do assunto.
- **Título 3D do episódio** no ambiente, acima do herói, na abertura: letras em 3D que caem com bounce, uma a uma e rápido. O título some na transição (`titulo3d.py`).

## Ficha de elenco e objetos antes de animar (pedido de 23/10/2026)
Ele achou os juízes "simplificados demais" e os figurantes "sem rosto, sem vida". Por isso, todo vídeo novo começa por uma **ficha (model sheet)** aprovada:
- **Elenco** (`kit3d/elenco.py`): todos usam o MESMO boneco do herói, com rosto vivo e expressões. A identidade vem da roupa, do cabelo, do chapéu e dos acessórios, sempre com o mesmo traço (`H.P`).
  - Personagens prontos: juiz e juíza (toga com cetim e gola branca, óculos, cabelo branco ou coque), deputado (terno cinza, grisalho, bigode), empreiteiro (capacete), policial (quepe e colete), fiscal, diplomata (faixa estrangeira, barba), trabalhador (macacão e boné), contador (viseira e colete).
  - Silhueta sem rosto só serve para multidão ao fundo.
- **Objetos** (`kit3d/objetos.py`): envelope com selo, contrato com assinatura e selo, estojo de joias aberto, mochila, calendário, livro do orçamento, retrato sem rosto, telão da bolsa, faixa presidencial.
- **Ficha:** gere com `kit3d/ficha_elenco.py` nos modos `elenco_frente`, `elenco_q`, `obj_dinheiro`, `obj_poder` e `obj_pequenos`. Monte com `kit3d/ficha_montar.py` e mande para aprovação.
- **Mente de ilustrador** (ele pediu "enriquecer de detalhes, mente artística, mais props"):
  - cada personagem tem **silhueta própria** (proporção do corpo, altura, cabeça; `prop` em `_base`);
  - **figurino em camadas**: lapela, botões, lenço, broche, cinto com fivela, distintivo, rádio, dragonas, ligas, colete;
  - **marca no rosto ou corpo**: rugas, brinco, colar, lápis na orelha, barba, bigode;
  - **um objeto na mão** que conta quem ele é (`mao(H, tipo)`).
- **Objetos de dinheiro e cena** (`objetos.py`, ficha v2): maleta e mala de dinheiro, caixa de papelão, cofre, carrinho de mão, tornozeleira, algemas, tribuna com microfones, câmera de TV, celular, carimbo, relógio de ouro, champanhe, charuto, cadeira presidencial, bandeira, notebook com planilha, pasta confidencial, jatinho e a silhueta do Congresso.
- **Marcas reais:** escreva o nome da empresa em texto, como em notícia ("PETROBRAS"). O logotipo oficial só entra se o usuário mandar o arquivo.
- **Dinheiro com tamanho legível:** 1 bilhão é `UN.cubo_mil` (1.000 maços, 10 × 10 × 10, com a grade). Uma porcentagem sai como um bloco de verdade (3% = `tirar=3` → 30 maços).
  - Para entender o tamanho, mostre de cima em 3/4. A câmera **pode girar** quando o plano só tem objetos, sem boneco.
- **Dinheiro nunca "cai do céu"** (ele achou estranho): ele surge do chão, é empilhado, desliza ou chega carregado.

## Uma cena por fala, cada uma num lugar
São 2 ou 3 planos por cena, trocados por marcador (`planos()` em `prod_pcc6.py`):
- **aberto** (lente 28 a 32): situa o lugar;
- **inserto do objeto** (lente 40 a 45): dinheiro, ficha, envelope;
- **close no rosto** (lente 50): a emoção da frase;
- **por cima do ombro**, **de costas** (rig "back", trocado com `S.mostra`), **de baixo** ou **de cima** (`alt0`/`alt1`).

Cada plano tem uma ideia só. Corte **depois** que a ação foi vista.

### Enquadramento (correção forte)
Ele recusou planos com o assunto cortado ("não está mostrando nada", "cortou a cena"). Por isso o plano nasce da **caixa do assunto**:
```python
dict(t0=..., t1=..., caixa0=(x0, x1, z0, z1, y), caixa1=(...), lens=45, preenche=0.82, fstop=1.8, chaves=["obj1", "obj2"])
```
- `quadro.enquadra` calcula a câmera para a caixa caber na área segura (x de 65 a 960, y de 270 a 1250), com 15 a 20% de respiro.
- Rode com `VERIFICA=1`: cada plano imprime "QUADRO plano i: ok" ou FORA, com o lado e os pixels.
- Para um corpo inteiro, a caixa vai de z0 = −0,1 até a cabeça, com `preenche` entre 0,8 e 0,82.
- O que atravessa a lente (ombro, grade) some fora do plano dele com `S.mostra`.

### Profundidade e riqueza
São três camadas:
1. **primeiro plano desfocado:** `S.ombro`, `S.planta`, `S.coluna_fg`, cerca, hidrante, grade;
2. **assunto em foco;**
3. **fundo com névoa:** `S.neblina` e luzes desfocadas (`S.bokeh_fundo`).

Ponha adereços do lugar (`adereco.py`: fios, cartazes, semáforo, relógio, calendário, quadro de avisos, velas, cortinas, lustre, garrafas, árvore, varal de luzes, placas de andar…). O cenário deve ser rico, sem virar "joguinho": uma luz principal e poucos objetos grandes.

## Cor (correção forte)
Recusado:
- "escuro demais";
- "mais do mesmo, sem contraste";
- amarelo + preto;
- tudo azul.

O que vale:
- **Roteiro de cor:** cada lugar numa família diferente, com a luz na cor oposta à da parede (`VAR` em `prod_pcc6.py`):

  | Lugar | Parede / clima | Luz ou destaque |
  |---|---|---|
  | Esquina | azul-noite | poste laranja |
  | Avenida | azul | sirene vermelha e azul |
  | Sala do gerente | madeira quente | o dinheiro verde salta |
  | Delegacia | aço frio | alarme vermelho; fichas creme com faixa vermelha |
  | Salão | roxo | velas |
  | Tribunal | vinho | — |
  | Escritório | petróleo | abajur laranja |
  | Rua | noite | janela quente e olhos amarelos |
  | Cobertura | pôr do sol | — |
  | Cúpula | vinho e dourado | — |
  | Celas | cinza frio | uma luz quente |

- O assunto fica mais claro que o fundo. A cabeça do herói é preta e some em fundo quase preto, então o fundo é de tom médio, com halo atrás dele.
- Não ponha vermelho atrás do herói: ele se confunde com o X e a borda.
- Tratamento final (`montar_teste.py`): curva em S leve, saturação 1,08, vinheta e grão.
- Teste a cor antes do render completo: `blender … prod_X.py -- b3 OUT --scale 0.3 --samples 8 --at 19.0,21.8`, e veja a folha.

## Rostos livres e cena viva (correção de 23/10/2026, presidente v3)
O usuário mostrou o contador "30 mil" em cima da cara do deputado, com a cabeça cortada no alto do quadro, e disse: "cuidado para as coisas não ficarem na frente do rosto, texto e tudo mais; trazer o displacement dos rostos para os objetos; está tudo muito parado; mais smooth, trabalhar na onda".
- **Rosto livre.** `rostos.exporta` (chamado no render de cada cena) grava a caixa de cada cabeça (`*_head`) quadro a quadro em `rostos.json` e avisa `CABEÇA CORTADA`. O overlay (`--rostos PASTA`) põe cada trecho de legenda, rótulo e contador no primeiro lugar livre durante todo o tempo em que fica na tela: legenda embaixo, um pouco acima ou no alto; contador nos quatro cantos.
- **Cabeça inteira ou nenhuma.** Inserto de objeto perto de alguém: ou enquadra o rosto inteiro (melhor, porque a expressão conta a história), ou desce até a cabeça sair toda. Em 9:16 uma caixa larga mostra muita altura, então conte com isso.
- **Tremido de traço em todas as bordas** (`vida.boil_cena`): Displace com ruído, BEM pouquinho (AMP 0,0016 m, menos de 1 px num plano médio), redesenhado 3 vezes por segundo e parado entre um passo e outro, em toda malha menor que 6 m. É o mesmo "boil" dos olhos e da boca.
  - **O ruído fica preso a cada objeto, nunca ao mundo.** No v4/v5 ele estava preso ao mundo (um controle só). Braço, faixa e objeto que se mexiam atravessavam o ruído, e a forma mudava a CADA quadro: "tá bugando os braços, os elementos, tudo". Além disso, 0,006 m era forte demais.
  - **Como prender:** cada malha ganha um controle filho (`bc_<nome>`), e todos seguem a mesma sequência de passos, então contorno e preenchimento continuam juntos.
  - **Conferir:** recorte 8 quadros seguidos de um braço que se mexe. A borda só pode mudar nos passos de 3 qps.
  - **Bonecos ficam FORA do tremido de cena** (já tremem nos olhos e na boca). O braço do boneco é refeito a cada quadro a partir das juntas (geometry nodes, sem pai), então não dá para prender o ruído nele. No v5 a mão soltava do braço e o cabelo e a cabeça do deputado tremiam. `boil_cena` pula tudo que pende de um `*_inv` ou tem modificador NODES.
- **Cotovelo nunca 100% reto.** Com ombro, cotovelo e punho em linha, o arredondado do braço (`limbs.rubber_limb`) perde a direção em alguns quadros: o antebraço dobra para dentro e a mão some. Era o "braço bugando" do v5 (`bracos_parados` com `elF=0`). Agora `frente.bracos` e `anim.bake` seguram o cotovelo em pelo menos 4°.
- **Ninguém parado** (`vida.vida_ator`, embutido no `finish` do prod): tronco, peito e cabeça em ondas sobrepostas de períodos diferentes e o quadril trocando o peso, sempre SOMADO ao que a cena animou. Figurantes de silhueta balançam cada um no seu tempo (`vida.balanca_figurantes`).
- **Câmera na mão** (`vida.camera_na_mao`): deriva lenta (soma de senos) proporcional à distância de foco, sem girar a câmera, para manter o 2D falso.
- **Onda.** O que voa ou desliza usa a curva "onda" do After Effects e passa um pouco do ponto antes de assentar (`unidades.onda_mola`, `unidades.voa`). Lâmpada pendurada balança em pêndulo com o feixe (`vida.pendulo`).

## Colisão e coerência (correção de 23/10/2026, presidente v4)
O usuário: "tá tendo uns bugs dos props, parece que tá se colidindo"; "quando a luz balança no teto, ela acaba bugando no chão"; "as animações não estão tão coerentes". O cenário rico foi aprovado ("já começou a ficar bom").
- **Detector antes do render:** `blender -b -P kit3d/colisao.py -- prod_X.py sNN` monta a cena sem renderizar, mede a caixa 3D de cada grupo (objeto sem pai + filhos) quadro a quadro e imprime `COLISÃO a x b` quando dois sólidos entram um no outro e um deles se mexe. Rode as 14 cenas em paralelo; só renderize com zero colisões.
- **O que ele achou no v4:** juiz batendo o martelo dentro do colega (ministros a 0,9 m) -> abrir espaço para o braço (±1,2 a 2,25 m) e recolher o braço depois da batida; réus a 0,6 m encostando no pop -> 0,68 m; 17 cubos nascendo dentro das viaturas e dos policiais -> cubos na frente deles; cubos em pilha passando do ponto para dentro do de cima -> `sobe_do_chao(..., passa=0)`.
- **O que o olho achou** (o detector ignora letreiro e cenário): cubo subindo no meio do título 3D -> atrás do título; câmera do dolly passando por dentro dos cavaletes -> cavaletes começam depois de onde a câmera para; fila de trabalhadores atravessando -> mais espaço de lado e no fundo; faixa da cela virou um palito verde -> larga, amarela com o verde no meio e dobrada na travessa.
- **Luz pendurada:** `vida.pendulo` gira o fio, a cúpula e o feixe; a poça de luz do chão NÃO gira (girar tira o disco do chão e ele corta o piso), só desliza de lado.
- **Folha de quadros a 3 qps do vídeo inteiro** (`ffmpeg -vf fps=3,scale=180:-1,tile=12x2`) antes de entregar: é onde aparecem os choques que o detector não vê.

## Partes em 3D de verdade (pedido de 23/10/2026)
"Dá para fazer algumas partes em literalmente 3D, esse personagem em 3D, não só em 2D." E depois: "o boneco 3D tá muito low-poly e simplista; não aparece um boneco estilo nosso." A primeira versão (cápsulas e bolas) foi recusada. A v2 (`heroi3d.Heroi3D`) copia o 2D medido junta a junta e funcionou.
- **Quando usar:** só nos planos que ganham com profundidade de verdade (órbita em volta do goleiro, câmera lenta, close da mão pegando a régua). O resto fica no 2D falso; o corte entre os dois estilos entra no pico de uma rampa de velocidade.
- **O que faz parecer "o nosso":** (1) as medidas do `heroi.py` (quadril 0,86 m, ombros ±0,16, braço 0,34 + 0,32 de raio 0,042, perna 0,41 + 0,38, cabeça de raio 0,16, pescoço curto); (2) o torso moldado na silhueta da jaqueta do 2D (`JAQUETA`), barra e gola mais escuras, zíper e bolsos; (3) membros em tubo afilado contínuo com tampa redonda e junta esférica; (4) rosto com olho branco grande sem pupila, sobrancelha branca fina e curva e boca de traço, todos colados na casca da cabeça (`_sobre_cabeca`); (5) sombreado chapado com UMA faixa de sombra do lado oposto à luz e uma borda de luz pêssego do lado da luz (Layer Weight Facing + normal contra `LUZ`); (6) contorno fino por casco invertido (Solidify com normais viradas e material de tinta com backface culling).
- **Não faça:** corpo de cápsulas e elipsoides soltas, sombreado em 3 degraus gordos sem borda de luz, olhos pequenos, torso redondo. Isso lê como "boneco articulado de brinquedo".
- **Armadilhas já resolvidas:** o sinal da abertura lateral do braço (F vai para a esquerda: Ry positivo); o tronco desce até o quadril; o pescoço entra no crânio; no nó Mix de cor use os soquetes por índice (6, 7 e saída 2), porque os nomes se repetem; o braço do menino não pode ficar fino.
- **Poses:** `pose(ombro, cotovelo, abre, quadril, joelho, tornozelo, tronco, cabeca, giro, inclina)` e `rosto(boca=reta|sorriso|triste|o, lid=0..1)`. A tabela completa de expressões do 2D ainda não existe no 3D.

## A câmera vai onde a ação acontece (correção forte de 23/10/2026, reflexo v1)
"Ficou extremamente confuso, não ficou profissional. Quando ele fala que a mente ficou extremamente rápida, já tinha que mostrar ele pegando uma mosca no ar. A câmera, de frente para o braço, com 12 mm, perto da ponta da mão, mostrando só a cabeça da mosca que ele pegou. Quando o copo vai caindo, a câmera já vem para baixo dele. O ar do ambiente tem de ter o efeito de que ele conseguiu pegar. Tem que ser cinematográfico, não simplista."
- **Cada fala tem um gesto que a prova** (pegar a mosca, o copo, a régua, a bola). Mostre o gesto, não o boneco inteiro parado num plano aberto.
- **Lente e lugar:** grande-angular de 12 a 16 mm a poucos centímetros do gesto (na ponta da mão, no chão debaixo do copo), com o rosto atrás e desfocado. Plano aberto só para situar, e curto.
- **O ar reage:** poeira 3D suspensa que anda em câmera lenta, rastro no caminho da mão, uma onda de partículas no instante do acerto, gotas de água que sobem do copo e voltam. Sem isso o "10 vezes mais rápido" não se sente.
- **Poucos planos, cada um com uma ideia.** Confuso = muitas coisas pequenas no quadro ao mesmo tempo.
- Isso exige o herói 3D e objetos 3D de verdade (`heroi3d.py`, `cinema3d.py`): o 2D chapado não aguenta câmera de 12 mm girando.

## Animação de animador e câmera de operador (correção forte de 23/10/2026, reflexo cena 1 v2)
"Os movimentos ficaram muito ruins, muito travados. A câmera não está profissional, com aquelas ondas in, out. Tá tudo muito amador, movimento muito duro. Anime como um animador profissional."
Medido com `mede_mov.py`, o problema tinha duas causas:
- todo plano de câmera entrava a 0 m/s e saía a 0 m/s, então cada corte juntava duas paradas;
- o boneco 3D ia de pose a pose em smoothstep, parando em cada chave e com todas as juntas mexendo juntas.

O que vale agora:
- **Boneco (`Heroi3D.anima`):**
  - curva cúbica monótona entre as chaves, então a velocidade passa pelas poses sem parar;
  - cada junta segue o alvo por uma mola própria (`MOLAS`): o quadril lidera, o tronco vem 1 quadro depois, o braço 1 quadro e o antebraço e a cabeça 2. Elas chegam, passam um pouco do ponto e assentam;
  - gesto seco (pegar algo no ar, soco, defesa) leva `molas=dict(ombro=(0, 6.5, 0.72), abre=(0, 6.5, 0.72), cotovelo=(1, 7.0, 0.66))`: chega e trava, sem ficar mole;
  - antecipação continua sendo uma chave: recue ou abra o braço para o lado antes do golpe.
- **Mão que pega um objeto:** o objeto cai até onde a mão está de verdade naquele quadro (leia `matrix_world` com `frame_set`), e depois vai junto com a mão, que amortece descendo um pouco. Nada para seco.
- **Mão aberta e fechada:** `fecha_mao(s, em=quadro)`. A mão fica aberta até o quadro do gesto e só então vira punho.
- **Câmera (`camera_cine` no `prod_reflexo.py`):**
  - caminho e mira são curvas por vários pontos;
  - o tempo segue uma Hermite com `v_in`/`v_out`. Dentro de uma sequência, todo corte acontece com a câmera andando dos dois lados (v ≈ 1). Só o primeiro plano nasce devagar (v_in ≈ 0,3);
  - o plano que termina parado chega passando do ponto 4% e assenta (`assenta`), de preferência no quadro do acerto;
  - `segue=` faz a mira acompanhar o objeto que se mexe (mão, copo, cabeça) com atraso de operador.
  - `camera_livre` fica só para planos sem ação.
- **Desfoque de movimento:** ligado nas cenas 3D (`use_motion_blur`, obturador 0,5). O braço rápido borra e o anel de ar vira uma onda.
- **Medir antes de mostrar:** `blender -b -P kit3d/mede_mov.py -- prod_X.py sNN peca1,peca2` precisa dar:
  - nenhuma `PARADA` no meio de um gesto;
  - nenhum `TRANCO` no meio de um plano;
  - em toda câmera do meio da sequência, "entra" e "sai" acima de 0,1 m/s.

## O vídeo inteiro no estilo limpo (reflexo v5, 23/10/2026: "o teste da régua ficou muito confuso, revisa todas as animações")
Receita que valeu para as oito cenas (o que se repete é o que dá clareza):
- **Chão liso de uma cor por cena** (cozinha quente, azul-petróleo, roxo, verde, vermelho da pista, noite, quente) e nada de painel, relógio ou plateia detalhada; o gol é estreito (3,6 m) e a câmera fica a uns 6 m, para os bonecos lerem.
- **Um sinal por ação:** anel verde no botão; pinça que solta a régua; tiro com clarão; cartão vermelho; cabo que arrebenta. O sinal vem antes e a reação depois.
- **Número grande flutuando virado para a câmera** (`numero_flutuante`), com estados que mudam; nada de contador no canto.
- **Duas "tomadas" na mesma cena** (pênalti 1, 2 e 3): um corte seco com a mesma câmera mudando de lado, para mostrar "antes, depois, você".
- **Tempo do mundo `vt(f)`** comanda objetos que caem (câmera de TV, bola, copo, régua); o herói fica no tempo normal.
- **Uma sequência contínua em duas cenas** (6 e 7): `final_mundo` monta tudo e cada cena só põe as suas câmeras (a de TV cai o tempo todo, a torcida levanta depois).
- 3 a 5 câmeras por cena, todas lentas, com a mesma lente de 28 a 40 mm nos planos abertos.

## Cena 2 do reflexo, a versão que ficou clara (v3, 23/10/2026)
Depois de duas versões que ele não entendeu ("recria de outro ângulo, mais clean"):
- **Um plano só, alto e de frente** (câmera a 2,7 m descendo devagar, 32 mm, elevação de uns 50°), sobre uma mesa lisa e um fundo liso. Nada de relógio, painel, consoles nem poeira.
- **O sinal é um anel em volta de cada botão** (vermelho → verde): quem tem o anel verde pode apertar. Dá para ler quem recebeu o sinal sem nenhum texto.
- **O número é texto grande flutuando acima da cabeça de cada um**, virado para a câmera (`rotation_euler.x = 90° − elevação`), em verde-claro; o do mundo lento se arrasta (0,000 → 0,250 em seis passos).
- A distorção do tempo fica mínima: um anel de ar deitado na mesa, filtro frio leve, o mundo a 1/10 (a mão dela lenta) e o eco da mão rápida.
- Descida da mão lida de cima: com câmera a 90° a mão só cresce e ninguém vê o aperto; use a vista alta oblíqua.

## Personagem vivo (reflexo v9, "aperfeiçoar as animações do personagem")
- **Rosto que muda com a história:** `Heroi3D.expressao([(quadro, dict(boca=reta|sorriso|triste|o, lid, brow, olhos)), ...], A, END)`. Pisca sozinho a cada 2 a 4 s (3 quadros) e logo depois de cada troca forte; a troca leva até 6 quadros. Use foco (`lid` 0,35, `brow` −0,6) antes da ação, susto (`o`, `brow` +0,9, `olhos` 1,15) no imprevisto e sorriso no acerto.
- **Parado não é estátua:** além da respiração, o peso passa de um pé para o outro (`inclina`), o tronco gira um pouco (`giro`) e o olhar passeia (`olha`), tudo em ondas lentas.
- **Corrida com peso** (`corrida`, oito chaves por ciclo): braço à frente com o cotovelo mais fechado, o tronco gira com os ombros e a cabeça compensa, o calcanhar sobe na recuperação, e o corpo desce no apoio e sobe no voo.

## Bugs de cenário que já aconteceram (confira antes de entregar)
- **Piscar no chão:** duas superfícies no mesmo plano (chão + faixas + linhas) brigam na profundidade. Base a −0,03 m, faixas em 0, linhas e marcas em +0,015 m, e `clip_start` da câmera em 0,3 m. Teste: diferença entre quadros seguidos num trecho de chão sem nada em cima deve ser quase zero.
- **Ninguém deita em cima de outro:** o mergulho deitado atravessava o menino e a câmera de TV. Se a cena tem objeto caindo, o herói corre e leva o outro para fora da queda, e ambos terminam de pé.
- **O menino "morre":** pose de joelhos ou inclinada em um personagem pequeno parece desmaio. Pequenos ficam de pé, de braços levantados ou soltos.
- **Mosca balançando:** nada de rotação e de asas rápidas na mosca presa; 3° de balanço e asas a 8 quadros.

## Calma e clareza (reflexo, vídeo inteiro v2)
- **Uma ideia por tela.** Se o espectador não consegue dizer em um segundo o que está vendo, tire coisas: poeira, anéis, ecos e HUD, tudo junto, viram ruído. Regra prática: no máximo dois efeitos de ar por plano, e a poeira só serve para mostrar o tempo parado (pouca e visível).
- **Menos cortes, mais lentos.** Uma fala de 5 a 7 s tem no máximo 3 a 4 planos. O primeiro situa os dois lados (médio, com os números legíveis); depois um close do gesto; o último fecha.
- **Mesmo assim cada plano tem de ser lido sozinho:** o que ele faz (pessoa), o que acontece (botão, luz, número), e a legenda por baixo.

## Tudo em curva in / meio / out (reflexo cena 1 v6, "refinar com transições suaves in, out, middle")
Nada pode mudar de velocidade de uma vez. Onde havia degrau:
- **Câmera lenta:** liga com `cinema3d.tempo_lento(f, lento, 8)`, uma smootherstep de 1 até o lento em 8 quadros. Vale para o voo, a poeira e a batida das asas (`bate_asas(periodo=função)` soma a fase quadro a quadro).
- **Gotas:** saem em ease out, voltam em ease in-out e nascem/somem crescendo em 3 quadros, sem pop.
- **Objeto preso que se debate:** começa em curva de 4 quadros, depois cansa.
- **Corte entre planos: take normal.** Ele recusou a rampa de velocidade nos cortes da cena ("transições agressivas, prefiro o take de câmera normal"). Dentro da cena, corte com as duas câmeras andando na curva in/out (`v_out` de um plano ≈ `v_in` do seguinte), sem rampa e sem borrão. A rampa só vale para a passagem de uma cena para outra, quando ele pedir. Referência técnica da rampa (`camera_cine(..., rampa_out=(direção, k), rampa_in=(direção, k))`):
  - nos últimos 5 quadros a câmera acelera em u³ na direção (in);
  - o pico fica no último quadro visível (meio);
  - o plano seguinte nasce deslocado e freia em (1-u)³ (out);
  - a direção é da própria câmera (direita, esquerda, cima, baixo, frente), então os dois lados andam para o mesmo lado da tela;
  - use o mesmo k dos dois lados (fração da distância de foco);
  - o desfoque de movimento borra só no corte.
- Sequência testada e recusada no reflexo v6:
  - médio → 3/4: direita;
  - pegada → close no punho: frente (mergulho);
  - close → copo: baixo;
  - copo → olhar dele: frente, curto.
- **Conferir:** `mede_mov.py` mostra `TELA entra/sai` em °/s. Nos dois lados de cada corte, a diferença deve ser menor que cerca de 30%.

## Distorção do tempo: o mundo lento e você rápido (reflexo cena 2 v2, "não parece que para o tempo")
Mostrar duas mãos descendo em rodadas não faz o tempo parar. O que faz:
- **Uma relógio mundial de tempo:** uma função `vt(f)` (1 = normal; cai a 0,1 em 5 quadros, smootherstep, e volta em 8) que comanda tudo que é do mundo: a poeira (`vel=vt`), o ponteiro do relógio de parede, o cronômetro dela, e as ações da outra pessoa (o quadro da tela em que passaram N quadros de tempo real = acumular `vt`).
- **Você fica no tempo normal:** o mesmo gesto de 4 quadros que a outra pessoa faz em 40. Eco da mão (cópias de luz que encolhem em 10 a 20 quadros) em você e em cada 3 quadros na mão lenta dela.
- **No sinal:** onda de tempo (três anéis grossos e frios saindo da lâmpada, de frente para a câmera), dolly zoom (a câmera entra e a lente abre de 24 para 13 mm em 14 quadros), e o filtro frio com vinheta.
- **Filtro de câmera (`camera_cine(..., filtro=[(quadro, tinta, vinheta)])`):** um plano de emissão azul-petróleo translúcido colado na lente (o alfa soma tinta e vinheta radial); ele acompanha a lente e **some fora do plano da própria câmera** (senão aparece nas outras).
- **No fim, o tempo volta:** um anel quente e o filtro sai em 10 quadros.
- Cronômetro com leitura que muda: texto por estado (`cronometro(nm, x, estados)`); no mundo lento ele se arrasta de 0,000 a 0,250.

## Duas pessoas lado a lado em quadro vertical (reflexo cena 2)
- No quadro 9:16, uma cena que é larga (dois bonecos, dois botões) não cabe com a mão grande: a 16 mm ela aparece com a mão de 7% da largura. Faça **uma câmera por pessoa**, a cerca de 0,5 m da mão e 18 a 22 mm, com o botão, o cronômetro e o rosto na mesma foto, e use um plano aberto curto (1 s) só para situar.
- Cada pessoa usa a mão de dentro e o botão fica no X da mão pronta (resolva a pose primeiro com `_braco_ate`, depois ponha o botão e a bancada onde a mão cai). O botão afunda no quadro do toque.
- A mesma descida (6 quadros) nas três rodadas, para que "os músculos são os mesmos" seja literal; o que muda é o quadro em que a mão sai.
- Os números ficam nos cronômetros da própria cena (`OR.cronometro`, que dá pop no toque); tire o mesmo número do overlay para não repetir.

## A batida do acerto (reflexo cena 1 v3)
- Depois de um acerto que prova a fala (a mosca presa), **o tempo para**. Para isso, abra um silêncio de cerca de 0,6 s na voz logo depois da palavra e desloque `palavras.json` e `tempos.json`. O original fica em `voz-*/sem_pausa/`. Com 1,5 s ele achou que "demorou demais"; o close inteiro dura cerca de 1 s.
- Na pausa entram três coisas:
  - um grave com estalo no quadro do acerto;
  - um tranco amortecido na câmera (`camera_cine(..., impacto=(t, 0.02))`), que continua no plano seguinte;
  - o close que gira devagar enquanto o objeto pego se debate.
- **Pegar algo que cai:** quem é rápido chega antes. A mão espalmada (`espalma`) já espera embaixo; o objeto cai nela e os dois descem juntos amortecendo.
  - Resolva a pose pela altura da mão, com `pe_no_chao` e o pulso que nivela a palma.
  - O ombro desconta a inclinação do tronco; sem isso a mão sobe junto com o corpo.
  - Nunca deixe o objeto cair "para cima" nem pousar numa mão redonda.
  - A mão chega por baixo junto com o objeto e desce com ele: contato no meio de uma palavra ("já") e amortece em cerca de 6 quadros.
- **No contato, corte para os olhos dele** (`olhoF`/`olhoB` do herói 3D, 10 cm à frente do rosto, lente de 26 mm). Quadro de cima para baixo: o próprio braço entrando, o objeto na palma, as gotas voltando e o anel de ar de frente para esse olhar.
- O "soco" do acerto (`impacto=`) é um avanço suave de 3 quadros, nunca um tremido, e nunca no último quadro antes de um corte.

## Misturar 2D e 3D numa cena (reflexo, 23/10/2026)
- O 2D usa a câmera fixa (`P6.planos`: a câmera só desliza); o 3D usa `camera_livre` (gira e olha para um alvo). As duas põem marcadores de câmera na linha do tempo, então o corte entre elas é um marcador. Dê `entra`/`sai` ("h") nas pontas para a transição borrada.
- O herói 3D se chama `nome_inv` (fica fora do tremido de cena, conta como boneco no detector de colisão e a cabeça `_cranio` entra no `rostos.json`). A sombra no chão acompanha o boneco (`H.sombra`, gravada em `grava`), e não sobe nem gira quando ele mergulha.
- Animar o 3D: `H.anima([(quadro, pose + pos/rot), ...])` (curva contínua entre as chaves, mola por junta e respiração por cima; ver a seção abaixo), `corrida(f0, f1, de, ate, rot)` para correr, e `pos`, `rot` (giro em z ou (x, y, z)), `alt` (altura do quadril) e `olha` (a cabeça vira) na pose. Mergulho de goleiro: `rot=(0, ±82, 0)` e `pos` levantando.
- Quando a cena precisa acontecer duas vezes (replay), reaproveite os mesmos objetos: chaves CONSTANT para "voltar" no corte, e esconda/mostre com `UN.esconde_ate` e `UN.some`.
- Cenário de estádio: gramado listrado + linhas, gol com profundidade (`gol3d`), arquibancada inclinada com pontos de cor colados NA inclinação (nunca bokeh solto: parece neve), placas só em cores, refletores. A torcida (`plateia`) senta e levanta por fileira.

## Animação (correção forte)
Ele quer a "onda" do editor de gráficos do After Effects. Recusou o braço e o fuzil "sem smooth".
- Nada de pose a pose com smoothstep, porque a velocidade zera em cada chave. Use `curvas.spline` (Catmull-Rom) e `frente.bracos(keys, extras=...)`.
- Todo gesto tem **antecipação**, **passa do ponto** e **assenta**. Impacto é mola amortecida (`curvas.pancada` ou `mola`, com pico normalizado em 1). Queda em ease-in (`curvas.s("queda")`).
- Câmera em curva A ("easy"). Ele recusou a câmera que "sobe muito" ao se afastar.
- **Reações** no ritmo das emoções da voz (`tl.face` e `Actor`):
  - susto: `take`;
  - cifrão nos olhos e sorrisão no dinheiro;
  - suor e boca nervosa no risco;
  - `slump` depois de perder;
  - a cabeça inclina na pergunta final.

## Transições (correção forte)
Ele recusou a cortina escura ("estranha, fica muito tempo na tela").
- O corte fica escondido no pico de uma rampa de velocidade: `transicao.rampa_fim` numa cena e `rampa_inicio` na outra, na mesma direção, com cerca de 4 quadros de cada lado e k = 0,32 para manter a mesma velocidade de tela.
- Na montagem, aplique borrão direcional só nos quadros do corte (`--borrao`).
- A direção acompanha a história: vertical na subida de nível, horizontal no resto.
- A cena nunca para.

## Gancho
Na palavra-chave do gancho, algo cai com bounce. No PCC, o AK-47 cai na mão dele (`armas.cai_na_mao`) e ele faz cara de malvado, sem quebrar a cena. O contador do salário sobe junto com notas caindo.

## Um plano colado por fala, no lugar certo (reflexo v10-v11, 23/10/2026)
"Tem que ter essas coisas dinâmicas para todas as cenas, só que extremamente estratégica."
- **Molde:** aberto calmo que situa → UM plano colado no gesto, na palavra que prova a fala → volta ao aberto ou à reação. Mais que isso vira confusão (correção 38).
- **Onde pôr a câmera:**

  | Ação | Plano |
  |---|---|
  | apertar | 12 mm rente ao tampo, colada no botão, o rosto aparecendo em cima |
  | chutar | 12 mm no chão ao lado da bola, a mira vai atrás da bola até a rede (`segue=bola`) |
  | goleiro | de dentro da rede, atrás dele, olhando a bola; o mesmo ângulo nos dois goleiros vira comparação |
  | defender | 16 mm na luva, soco suave (`impacto`) no quadro do contato |
  | largada | 14 mm no chão, na diagonal entre as raias (de lado, o vizinho tapa o herói) |
  | pergunta | empurrão lento no rosto; os olhos fazem a dúvida |
  | abertura de cena grande | grua descendo |
  | fecho | meia volta que termina no rosto |

- **Armadilhas medidas:**
  - Câmera rente ao chão precisa de `clip` de 0,03 a 0,05, senão o chão some numa faixa reta.
  - O filtro de tempo não pode ficar no plano de corte da câmera (`dist = clip × 1,25 + 0,02`), senão vira um triângulo azul.
  - Macro a menos de ~15 cm tira o objeto de foco: use f/5,6.
  - `segue=` de algo que teleporta no corte (a bola volta ao ponto) puxa a mira: amostre só dentro do plano.

## Perigo que cai e resgate (reflexo v11, "o menino ainda morre")
- O que cai em câmera lenta obedece ao tempo do mundo (`real(f)`). Meça a altura dele quadro a quadro contra a cabeça de quem está embaixo.
- Até o resgate, o perigo fica pelo menos 1 m acima da cabeça. Ele bate no chão vazio depois, de preferência quando o tempo volta.
- Se não couber, deixe o mundo mais lento (0,07) e acelere o que precisa chegar na palavra (a bola: 6 quadros reais).

## Mais leve e fluido (reflexo v12, "de acordo com os especialistas")
- **Corrida:** sai do zero e freia (`corrida(..., arranque=0.3, freia=0.3)`), com passadas mais curtas no começo e no fim. Parar seco depois de correr a toda é um tranco.
- **Molas:** amortecimento 0,58 a 0,66 nas pontas (braço, antebraço, cabeça): passam do ponto UMA vez e assentam. Abaixo de 0,55 vira gelatina.
- **Ondas de ar:** abrem em curva exponencial, a espessura nasce em 3 quadros e afina devagar, 35% mais longas, com um eco mais fino logo atrás (`cinema3d.onda`).
- **Tomadas repetidas na mesma cena** (três cobranças): as chaves de uma não podem passar do corte da seguinte. Filtre por quadro.
- **Antes de mostrar:** `mede_mov.py` em todas as cenas. Tranco que sobra só no gesto seco de propósito (o tapa, o chute) ou num corte.
