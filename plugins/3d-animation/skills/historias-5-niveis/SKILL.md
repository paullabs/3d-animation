---
name: historias-5-niveis
description: Produz os Reels narrados do Canal 38 no formato "Você acabou de entrar no X" / "Você acabou de virar X": quanto cada degrau paga e o que cobra, em 2D falso dentro de cenários 3D de verdade, montado por script no Blender. Cobre o projeto inteiro, com aprovação do usuário em cada fase: roteiro com fontes em tom de conversa, voz grave da ElevenLabs com emoção por frase, ficha de elenco e objetos, plano de cenas com enquadramento conferido, paleta e contraste medidos, animação viva (respiração, onda, tremido de traço), transições escondidas no movimento, legendas que desviam dos rostos, detector de colisão, música orquestral tensa, um efeito sonoro por ação no quadro certo, mixagem com guarda de voz, render e entrega. Use SEMPRE que o pedido for um vídeo novo do Canal 38 ou da série (cartel, ditador, presidente corrupto, máfia, milícia, golpista, hacker, "5 níveis", "quanto ganha cada nível", "você acabou de entrar no…", "você acabou de virar…"), ou para continuar, ajustar ou corrigir um desses vídeos (voz, legenda, cor, cena, personagem, movimento, som, render), mesmo que o pedido não diga "skill" nem "Canal 38".
---

# Histórias "5 níveis" do Canal 38

Reels verticais (1080×1920, 24 qps, 60 a 85 s). Um narrador grave fala com você ("Você acabou de virar um presidente corrupto do Brasil…") e cada degrau mostra **o que ganha** e **o que cobra**. A imagem é 2D falso: bonecos e objetos recortados, com traço e sombra chapada, dentro de salas 3D de verdade com profundidade, câmera que anda e luz de cinema. Tudo é montado por script no Blender 5.2, sem abrir a interface.

**Referências aprovadas:**
- `personagem/pcc/pcc-v7c-final.mp4`: o primeiro, publicado.
- `personagem/presidente/presidente-final.mp4`: o mais completo, com elenco com rosto, cenários 3D, vida, sem colisões e som por ação. É o modelo atual.

Tudo nesta skill vem das correções que o usuário fez até chegar nelas. Cada regra tem um porquê; num caso novo, siga o porquê, não só a letra.

**Projeto:** `<pasta-do-projeto>`
**Kit:** `…/kit3d/`. O modelo de cenas é `prod_presidente.py` (14 cenas, uma por fala); o mais antigo é `prod_pcc6.py`.
**Scripts desta skill:** `scripts/sfx.py` (efeitos sintetizados) e `scripts/mixagem.py` (v2: mixagem com guarda de voz, efeitos pela energia).

## Como o usuário trabalha

- **Valida por fases.** Não pule a aprovação: roteiro, voz, ficha de elenco e objetos, rascunho de vídeo, som e render final. Render custa tempo e crédito custa dinheiro; trabalhar em cima de algo não aprovado é desperdício.
- **Vídeo primeiro, texto depois.** Ele assiste o arquivo que acabou de chegar; se o texto vem antes, ele confunde qual arquivo está avaliando.
- **Escreve curto e por voz.** "Tá bugando", "tá parado", "quase não dá para ouvir" são pistas reais. Meça, ache a causa e corrija na raiz (exemplos em `references/correcoes.md`, 1 a 29).
- **Ele é exigente com acabamento.** Antes de mostrar, faça a crítica que ele faria: folha de quadros a 3 qps, braço e rosto em quadros seguidos, detector de colisão e efeitos que podem sumir.
- **Resolução:** rascunho em meia resolução (`--scale 0.5 --samples 10`); resolução cheia (`--scale 1.0 --samples 32`) só depois do "pode renderizar" ou "aprovado".
- Responda em português do Brasil, com palavras simples.

## Fluxo

### 1. Roteiro (aprovação)
Leia `references/roteiro.md`. Pesquise os fatos com fonte e escreva `roteiros/<tema>.json`; mostre o texto corrido.
- **Abertura e fecho:** gancho direto na 1ª frase e fecho com uma pergunta ("Ainda quer a faixa?").
- **Tom:** de conversa, sem enrolar.
- **Contexto para o brasileiro:** diga quem é quem e de onde na primeira vez.
- **Ligação entre os níveis:** pontes entre um nível e outro ("Até que foi descoberta…", "Depois vêm…").
- **Números:** todo número vira proporção (unidades fixas, regra 9b).
- **Política:** ficção montada com casos reais dos dois lados, sem alfinetada velada em candidato real (ver `references/roteiro.md`).
- **Duração:** 60 a 85 s. Clareza vale mais que segundos.

### 2. Voz (aprovação)
Leia `references/voz.md`.
- **Geração:** ElevenLabs eleven_v4, voz **Lucas**, com uma tag de emoção por frase, acelerada com `atempo`.
- **Arquivos:** `kit3d/voz_eleven.py` gera `narracao.wav`, `tempos.json` e `palavras.json`.
- **Conferência:** leitura transcrita no Whisper.
- **Entrega:** mande o mp3.

### 3. Ficha de elenco e objetos (aprovação)
Antes de animar, mostre a ficha: `kit3d/ficha_elenco.py` (modos `elenco_frente`, `elenco_q`, `obj_dinheiro`, `obj_poder`, `obj_pequenos`) e `ficha_montar.py`.
- **Elenco:** todo personagem tem rosto e acessórios do papel (`elenco.py`), e nunca é silhueta genérica.
- **Objetos:** ricos, com detalhes de artista (`objetos.py`).
- **Marcas reais:** nome escrito; o logo oficial entra só se o usuário mandar o arquivo.

### 4. Plano de cenas e rascunho (aprovação)
Leia `references/visual.md`. Uma cena por fala, cada uma num lugar 3D diferente (`ambiente3d.py`), com 2 a 5 planos de cinema (close, por cima do ombro, inserto, aberto, de cima).
- **Enquadramento:** cada plano nasce da caixa do assunto (`P6.planos`, `quadro.enquadra`) e é conferido com `VERIFICA=1`.
- **Câmera livre:** `camera_livre` gira, então use só em plano sem boneco.
- **Contraste:** medido com `contraste.py`, ≥ 3:1, com parede em tom médio, halo atrás de figura escura e silhueta contra janela clara.
- **Vida:** já vem embutida no `prod_presidente.py` (`finish` com `vida.vida_ator` e `com_vida` em cada cena).
- **Antes do render:** rode a lista do checklist abaixo.
- **Legendas e montagem:** legendas com `overlay_presidente.py --rostos PASTA`; montagem com `montar_teste.py --borrao`.
- **Conferência:** folha de quadros a 3 qps do vídeo inteiro **antes** de mostrar.

### 5. Som (aprovação)
Leia `references/som.md`. Modelo: `kit3d/plano_som_presidente.py`.
- **Música:** orquestral tensa de thriller (`sonilo_music` no Higgsfield, 4 s mais longa que a voz, prompt em `som.md`), com `"musica_db": 3.0` no plano.
- **Efeitos:** um som próprio para cada ação, gerado na ElevenLabs (cerca de 17 créditos cada). Confira cada arquivo com `volumedetect`, porque às vezes vem mudo.
- **Tempo:** cada efeito no **quadro da ação**, com a mesma conta do prod (`F(t) = 1 + round(t*24)`, `T(f) = (f-1)/24`), nunca na palavra. Golpes curtos levam `golpe: true`.
- **Mixagem:** `scripts/mixagem.py plano_som.json` só passa com GUARDA OK. Leia a linha "efeitos que podem sumir".
- **Conferência:** transcreva o áudio final; todas as palavras têm de aparecer.

### 6. Render final e entrega
Leia `references/render-entrega.md`.
- Renderize em resolução cheia, gere o overlay com `--rostos` da pasta `s1` e monte com `--scale 1.0`.
- Confira e envie o vídeo primeiro e o texto curto depois.

## Checklist antes de mostrar qualquer rascunho

1. `blender -b -P kit3d/colisao.py -- prod_X.py sNN` nas cenas todas (em paralelo): **zero `COLISÃO`**.
2. `rostos.json` sem `CABEÇA CORTADA`. O overlay com `--rostos` tira o texto da frente das caras.
3. **Folha de quadros a 3 qps** (`ffmpeg -vf fps=3,scale=180:-1,tile=12x2`). Procure:
   - prop atravessando prop ou boneco;
   - braço quebrado ou mão solta;
   - luz cortando o chão;
   - câmera passando por dentro de objeto;
   - título embolado com outro objeto.
4. **8 quadros seguidos** de um braço e de um rosto em movimento: a borda só muda nos passos de 3 qps, e a mão continua presa ao braço.
5. **Movimento medido:** `blender -b -P kit3d/mede_mov.py -- prod_X.py sNN peca1,peca2` precisa dar:
   - nenhuma PARADA no meio de um gesto e nenhum TRANCO;
   - toda câmera do meio de uma sequência entrando e saindo andando.

   Ele chama de "travado, duro, amador" o que essa medida pega.
6. **No tempo da fala:** tire um quadro do vídeo montado em cada palavra-chave (pegada, aperto, chute, defesa, tiro, cartão, resgate) e confira contra a legenda. O que cai ou ameaça fica longe de quem está embaixo até o resgate: meça a altura quadro a quadro.
7. **Som:** GUARDA OK, nenhum efeito importante em "efeitos que podem sumir", e o Whisper com todas as palavras.

## Análise cirúrgica antes de mostrar (pedido de 23/10/2026: "tá tudo confuso, não dá para entender nada")
Faça isto com o vídeo montado, **antes** de entregar, e escreva o resultado:
1. Uma folha com **1 quadro por segundo** do vídeo inteiro (`ffmpeg -vf fps=1,scale=300:-1,tile=5x2`, de 10 em 10 s) e, para cada plano, **quadros grandes** (1080 px) dos momentos-chave.
2. Para cada fala, responda por escrito, como um espectador que nunca viu o vídeo: *quem é o "você"? o que acontece? o que prova a frase? o que aparece sem ser explicado?*
3. Os defeitos que mais aparecem, por ordem: (a) o personagem principal muda de roupa ou de papel entre cenas; (b) a prova da frase é pequena demais (mosca, 3 mm, defesa fora do quadro); (c) número sem dono (contagens e zeros no ar); (d) elemento fora do quadro (menino, goleiro que cai para fora); (e) cena com mais de uma ideia.
4. Corrija o que for (a) a (e) e reveja de novo em quadros grandes. Só então entregue, junto com a lista do que foi achado.

## As correções que valem para todos os vídeos

Cada linha foi uma reclamação real (o histórico completo, de 1 a 29, está em `references/correcoes.md`).

**Roteiro e texto**
1. **Roteiro em tom de conversa**, nada abstrato. Evite "droga" na fala (use "ponto"). Todo número tem fonte. O PCC v7 foi bloqueado pelo Instagram, então siga "Moderação do Instagram" em `references/roteiro.md`.
2. **Legenda legível (v2, 23/10/2026, no reflexo).** Ele achou a legenda pequena e apagada "horrível, não dá para entender". Agora: até 3 palavras, Avenir Next Heavy 80 px, em pílula escura translúcida, sempre no mesmo lugar (y ≈ 1390), o trecho inteiro legível desde o começo; a palavra dita fica amarela e volta ao branco, número em âmbar, dinheiro em verde. Nada de HUD de contadores nem rótulos no canto: o número vai no objeto da cena (cronômetro, régua) e na legenda. A montagem usa `--limpo` (sem bloom nem ruído).

**Imagem**

3. **Nada cortado no quadro:** área segura x de 65 a 960, y de 270 a 1250.
4. **Escala única** e profundidade em três camadas.
5. **Cada cena num lugar 3D diferente**, rico mas limpo.
6. **Cor com contraste medido** (≥ 3:1). Cada lugar numa família de cor, dinheiro sempre verde, nada de amarelo com preto.
7. **Movimento de animador, na curva "onda"**: antecipação, passa do ponto e assenta (`unidades.onda_mola`, `voa`); nunca pose a pose parada. Boneco 3D com mola por junta (`Heroi3D.anima`); câmera de operador que corta em movimento e chega assentando (`camera_cine`). Detalhes em `references/visual.md`.
8. **Transição invisível** no pico de uma rampa de velocidade, com borrão só no corte.
9. **Planos de cinema variados** (close, ombro, costas, de baixo, de cima), cada um com uma ideia só.

9b. **Todo número vira proporção visual e sonora**, com unidades fixas, simples como livro infantil:
   - notinha = 1 salário mínimo;
   - maço = R$ 1 milhão;
   - cubo de 2,3 m = R$ 1 bilhão;
   - `cubo_mil` com bloco que sai = porcentagem;
   - o herói é sempre a régua. Dinheiro nunca cai do céu.

9c. **Rosto é sagrado e nada fica parado.**
   - **Rosto:** texto e objeto nunca na frente de um rosto; cabeça nunca cortada (`rostos.py` + overlay `--rostos`).
   - **Tremido:** bem leve (menos de 1 px) em todas as bordas de objetos e cenário, 3 vezes por segundo, com o ruído **preso a cada objeto**. Bonecos ficam de fora do tremido de cena, porque já tremem nos olhos e na boca.
   - **Movimento contínuo:** boneco balança o peso e a cabeça em onda, figurantes balançam, câmera na mão, lâmpada em pêndulo (`vida.py`).

9d. **Nada atravessa nada:**
   - objeto não nasce dentro de boneco ou carro;
   - boneco não invade o vizinho;
   - câmera não atravessa prop;
   - em pilha, o cubo de baixo cresce sem passar do ponto (`passa=0`);
   - o que pende gira, mas o que está no chão (poça de luz) só desliza;
   - `colisao.py` antes de renderizar.

9e. **Cotovelo nunca 100% reto** (mínimo 4°). Com ombro, cotovelo e punho em linha, o braço arredondado se perde: o antebraço dobra e a mão some.

**Som**

10. **Voz grave, um pouco rápida, com emoção por frase** (Lucas). A voz "Victor" foi recusada.
11. **Música orquestral tensa de thriller, presente mas abaixo da voz.** A trilha eletrônica e o "quarteto sutil" foram recusados ("a música não tá tensa"). Use −23 dB sob a fala, −18 dB nas pausas e subidas só dentro da pausa. Não achate a trilha.
12. **Efeitos presentes, variados e no quadro da ação.**
   - Cada ação tem o seu som, nada repetido.
   - Na pausa, o efeito soa tão forte quanto a voz.
   - Sobre a fala: o golpe (martelo, grade, impacto) fica 5 dB abaixo da voz, e o resto 8 dB abaixo.
   - Recusados: "quase não dá para ouvir", "só repete o mesmo efeito", "quando bate o martelo não faz o barulho".

**Entrega**

13. **Vídeo primeiro, texto depois.**

## Mapa do kit (o que usar para quê)

| Precisa de | Arquivo |
|---|---|
| Modelo de vídeo inteiro (14 cenas, helpers `heroi`, `ator`, `camera_livre`, `tribunal`, `martelada_juiz`) | `prod_presidente.py` |
| Herói (terno com faixa, ou uniforme listrado) | `uniforme.heroi_presidente`, `uniforme.heroi_preso`, `heroi.py`, `frente.py` |
| Elenco com rosto (juiz, juíza, deputado, empreiteiro, policial, fiscal, diplomata, trabalhador, contador) | `elenco.py` |
| Objetos de artista (envelope, maleta, cofre, telão da bolsa, tribuna, estojo de joias…) | `objetos.py` |
| Ficha de elenco e objetos | `ficha_elenco.py`, `ficha_montar.py` |
| Herói em 3D de verdade (cápsulas e elipsoides numa hierarquia de juntas, sombreado em 3 degraus por normal contra a luz e contorno por casco invertido, sem lâmpada) para planos de câmera livre: órbita, câmera lenta, close de mão | `heroi3d.py` (classe `Heroi3D`, `.pose(...)`), `ficha_3d.py`, `ficha_montar_3d.py` |
| Cenas do vídeo "e se…" (8 cenas: cozinha 2D, laboratório 2D, régua com o herói 3D, pênalti, 100 m, final à noite, escolha, pergunta), com estádio, gol com rede, torcida e câmera de TV por cabos | `prod_reflexo.py` (`estadio`, `gol3d`, `plateia`, `cena_final`, `camera_livre`), `overlay_reflexo.py` |
| Vídeo "e se…" do reflexo: elenco (você em casa/goleiro/velocista, atacante, menino de criança com `ESCALA`, torcedor) e objetos (copo, régua 30 cm, bola, luvas, medidor, bloco de largada, taça, gol, câmera de TV por cabos, telão de replay, mesa, torcida) | `elenco_reflexo.py`, `objetos_reflexo.py`, `ficha_reflexo.py`, `ficha_montar_reflexo.py` (modelo de ficha com câmera ortográfica) |
| Salas 3D (sala, colunata, tapete, janela, persiana, pátio, prédio) | `ambiente3d.py` |
| Título 3D que quica e some | `titulo3d.py` |
| Unidades de dinheiro e movimentos (`pop`, `sobe_do_chao`, `voa`, `onda_mola`, `cubo_mil`) | `unidades.py`, `grana.py` |
| Câmera que enquadra a caixa e área segura | `quadro.py`, `planos()` em `prod_pcc6.py`, `area.py` |
| Contraste medido | `contraste.py` |
| Vida: tremido de traço, balanço, câmera na mão, pêndulo | `vida.py` |
| Onde estão os rostos; cabeça cortada | `rostos.py` (e `so_rostos.py` para render já feito) |
| Detector de colisão | `colisao.py` |
| Medidor de movimento (paradas, trancos, câmera parada no corte) | `mede_mov.py` |
| Herói 3D com mola por junta, punho que fecha no quadro do gesto | `heroi3d.py` (`anima`, `fecha_mao(em=)`) |
| Câmera de operador (in/out, corte em movimento, segue a ação) | `camera_cine` em `prod_reflexo.py` |
| Peças de cinema 3D (mosca, copo, gotas, poeira, onda de ar) | `cinema3d.py` |
| Curvas e molas | `curvas.py` (`onda`, `easy`, `mola`, `pancada`), `anim.Timeline` |
| Transição em movimento | `transicao.py` + `--borrao` na montagem |
| Voz em tempos de palavra | `voz_eleven.py`, `palavras.py`, `tempo.py` |
| Legendas, nível e contadores que desviam dos rostos | `overlay_presidente.py` |
| Render em paralelo e montagem | `render_pcc.py`, `montar_teste.py` |
| Plano de som por ação e efeitos já gerados | `plano_som_presidente.py`, `roteiros/som-presidente/el/*.mp3` (31 efeitos), `roteiros/som-pcc7/*.mp3` |
| Efeitos sintetizados e mixagem | `scripts/sfx.py` e `scripts/mixagem.py` (desta skill) |
| Herói 3D com mola por junta, corrida com arranque e freada, expressão | `kit3d/heroi3d.py` (`anima`, `corrida(arranque=, freia=)`, `expressao`, `espalma`, `pe_no_chao`) |
| Câmera de operador (in/out, segue, soco, filtro de tempo) e o molde de um plano colado por fala | `camera_cine` em `kit3d/prod_reflexo.py` |
| Ondas de ar fluidas, câmera lenta, poeira, mosca, gotas | `kit3d/cinema3d.py` |
| Medir movimento (paradas, trancos, velocidade de tela no corte) | `kit3d/mede_mov.py` |
| Som do reflexo (sintetizados do tema e plano por quadro) | `kit3d/sfx_reflexo.py`, `kit3d/plano_som_reflexo.py` |

Para um tema novo, copie `prod_presidente.py` para `prod_<tema>.py` e `overlay_presidente.py` / `plano_som_presidente.py` para o tema, troque as cenas e mantenha os helpers. Não reescreva o kit do zero: ele carrega todas as correções acima. Reaproveite os efeitos já gerados quando a ação for a mesma (martelo, grade, cela, viaturas, braam) e gere só os novos.
