# O abrigo: regras de animação, movimento e transição

Valem para todos os 68 planos. Nasceram dos pedidos de 24 e 25/10/2026:
- "seja um animador profissional: animação leve, fluida, muito smooth";
- "cena bugada, totalmente amadora";
- "o braço parece solto".

O motor é `kit3d/anim3_abrigo.py`, em cima do `story3_abrigo.py`. O plano de câmera e o cenário continuam lá; o motor só põe o tempo.

## 1. Corpo (bonecos 3D)
1. **Nada de pose a pose.** Todo boneco passa por `Heroi3D.anima`, que faz três coisas:
   - curva cúbica entre as chaves;
   - mola por junta: o quadril lidera, o braço e a cabeça chegam depois, passam um pouco do ponto e assentam;
   - respiração e balanço por cima.
2. **Toda ação tem três tempos: antecipação, ação e assentamento.**
   - Antes de bater: o punho recua.
   - Antes de largar o guidão: os dedos apertam.
   - Depois de parar: o corpo passa do ponto e volta.
3. **Corrida com `corrida()`,** sempre com arranque e freada quando o boneco nasce ou para dentro do plano. Quem cruza o plano inteiro corre com `arranque=0` e `freia=0`, para entrar e sair já em velocidade.
4. **Ninguém congela.** Até no plano "parado", o boneco respira (`vida=1`) e o olhar passeia. Figurante de fundo leva `vida=0.6`.
5. **Cotovelo nunca 100% reto** (mínimo 4°).
6. **Mão presa ao braço:**
   - a mão POV sai de fora do quadro (`manga_comp` ≥ 1,1);
   - o pulso fica de lado para a câmera, nunca atrás da linha do antebraço;
   - os dedos fecham e abrem em 4 a 6 quadros, com um quadro de folga entre eles.
7. **Rosto:** a pálpebra desce em curva (6 a 10 quadros) e não pisca de estalo, a não ser o piscar normal, de 3 quadros.

## 2. Objetos
1. **O que cai acelera (ease in) e quica uma vez, pequeno.**
   - A bicicleta tomba de 0 a 82° em uns 10 quadros e quica 6°.
   - A roda segue girando e perde velocidade aos poucos.
2. **O que é empurrado começa devagar e para em onda.** A folha da porta corre em ease in e out e treme 1 cm quando bate no batente.
3. **A roda de giro gira com antecipação:**
   - meia volta para trás de 5°;
   - 1,2 volta para a frente;
   - trava com um tranco curto.
4. **O que é luz** (sirene, clarão) **sobe em curva,** nunca em degrau. A exceção é o corte para o branco de 1G, que é de propósito.

## 3. Câmera
1. **Câmera nunca morta.**
   - Plano "parado" = deriva lenta de 2 a 4 cm no plano e respiração de mão de 0,3°.
   - POV correndo = balanço de passada, 2 ciclos por segundo, 1,5 cm de altura, com rolagem de 1°.
2. **Movimento em curva in/out.** Dentro de uma sequência, corte com a câmera andando (velocidade de saída de um plano ≈ velocidade de entrada do seguinte).
3. **Ruído de mão sempre suavizado:** soma de senos lentos (0,3 a 1,1 Hz), nunca aleatório quadro a quadro.
4. **Desfoque de movimento** ligado em todo plano (obturador 0,5): borra o rápido e deixa o lento nítido.

## 4. Transições (corte)
1. **Corte em movimento:** a ação começa num plano e termina no outro (a mão larga o guidão no 1B, a bicicleta cai no 1C).
2. **Corte por rima:**
   - o branco do clarão (1G) vira a fresta branca da porta (2B);
   - a roda da bicicleta (1C) rima com a roda de giro (2C).
3. **Sem fusão nem efeito de transição.** O único "efeito" é o clarão, que é parte da história.
4. **Direção de tela:**
   - quem corre para o bunker vai sempre para o fundo, nos planos da rua;
   - nos planos do bunker, vem para a câmera.
   Não inverter no meio de uma sequência.

## 4b. Sentido do corte (pedido de 25/10/2026: "tem muito corte sem sentido")
1. **Dois planos seguidos nunca do mesmo lugar com a mesma lente.** Cada corte muda o ponto de vista: de frente, de lado, de cima, de dentro.
2. **Toda ação começa num plano e termina no seguinte:**
   - pula da bicicleta (1B) → a bicicleta bate no chão e ele sai correndo (1C);
   - o Zé entra pela porta (2A) → o Zé atravessa a porta por dentro (2B).
   Ninguém se teletransporta.
3. **Quem está em cada plano bate com o plano anterior.**
   - Quem corre na frente no POV é quem chega primeiro no bunker.
   - Quem fica para trás é quem bate na porta depois.
4. **A ameaça fica à vista.** O cogumelo da explosão aparece desde o primeiro plano e cresce pelo tempo do filme (`cogumelo_em`).
6. **Dentro ou fora tem que estar claro.** Plano de fora mostra placa, fachada, céu ou rua; porta sozinha em close não diz o lado.
5. **O clarão não apaga a história.** Ele estoura e baixa em menos de meio segundo, até dar para ver quem entra.

## 5. Conferência antes de mostrar
1. **Folha de quadros** a 6 qps de cada plano: braço quebrado, mão solta, câmera dentro de objeto, boneco atravessando boneco.
2. **8 quadros seguidos** de uma mão e de um rosto em movimento: a mão continua presa, o rosto não salta.
3. **Movimento medido:** o vídeo não pode ter salto de posição maior que 3% do quadro entre dois quadros sem desfoque, fora dos cortes.
4. **Corte no tempo da fala:** o quadro do corte bate com a palavra da decupagem (±2 quadros).
5. **Rascunho** em meia resolução e 10 amostras. Resolução cheia só depois do "pode renderizar".
