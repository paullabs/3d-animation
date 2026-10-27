# Críticas do Paulo que viraram regra (O abrigo, 24 e 25/10/2026)

Cada linha: o que ele disse → a causa → a regra.

## Storyboard
1. **"A primeira imagem já começa ruim; o braço está solto."**
   - Causa: a ponta redonda da manga do POV aparecia no meio da imagem.
   - Regra: manga comprida (`manga_comp` ≥ 1,1), saindo do quadro. A câmera fica ao lado do antebraço, nunca atrás dele.
2. **"Começa com a câmera de frente para quem pedala, depois a primeira pessoa; no fim, a câmera do lado oposto."**
   - Regra: primeiro o plano que mostra quem é o "eu", depois o POV. O plano reverso fica do outro lado (no destino), com a ação vindo de frente.
3. **"Cena totalmente amadora" (o prato visto de cima).**
   - Regra: objeto em plano fechado é 3D, com mão de verdade segurando a ferramenta (`mao_segura`), e o ângulo mantém a mão inteira no quadro.
4. **Cenas estranhas achadas na revisão:**
   - multidão clonada → um figurino por pessoa;
   - cachorro gigante na mesa → escala e lugar real;
   - cinza branca e alta → parece neve;
   - close de nuca → câmera do lado do rosto;
   - vapor em barras;
   - cabeça preta contra o clarão;
   - lâmpada na borda do quadro.

## Animação
5. **"Seja um animador profissional: leve, fluida, muito smooth."** Regras em `regras-animacao.md`:
   - curva de entrada e saída;
   - mola por junta;
   - corrida com fase própria para cada um;
   - câmera sempre andando;
   - desfoque de movimento.
6. **"Aos 4 e aos 5 s parece a mesma cena."**
   - Regra: dois planos seguidos nunca do mesmo lugar com a mesma lente.
7. **"Fica tudo branco e perde o sentido."**
   - Regra: o clarão estoura e baixa em menos de meio segundo, até a imagem voltar.
8. **"Do nada teletransporta para dentro, trancando."**
   - Regra: mostre a pessoa entrando. A ação começa num plano e termina no seguinte.
9. **"A primeira cena tem que mostrar a explosão de cogumelo lá no fundo, expandindo."**
   - Regra: a ameaça fica à vista desde o primeiro plano e cresce pelo tempo do filme. A cor muda: branco-amarelo, laranja, vermelho e, por fim, o céu branco. O reflexo quente aparece no asfalto.
10. **"Ele larga a bicicleta e não tem ninguém; depois aparece muita gente correndo."**
    - Regra: quem aparece depois já existia antes. Os figurantes têm um horário e um ritmo únicos (`ATRASADOS`, 2,9 m/s), e cada plano os coloca onde estariam naquele segundo.
11. **"Quando o Zé tranca a porta, buga: parece que o outro ia conseguir entrar. Faz uma cena lateral das pessoas tentando entrar e da porta fechando."**
    - Regra: o "por pouco" precisa ser claro. A porta já está quase fechada quando o primeiro chega, e ele só bate no aço.
    - O plano é de fora e de lado, com quem chega e a porta no mesmo quadro.
12. **"Parece que as pessoas estão do lado de dentro; causa confusão" (2E, os punhos na porta).**
    - Causa: um close só da porta, com o batente e o vidro âmbar, parece o lado de dentro.
    - Regra: todo plano do lado de fora mostra pelo menos uma prova de que é fora (placa, fachada, pilar, sacos de areia, céu ou rua). Porta sozinha em close não diz o lado.
    - O plano agora é de três quartos pela direita, com a placa ABRIGO e o povo atrás.
13. **"Faltou refinar: comida sem detalhe, comer feio, gente atravessando a mesa, suéter que não se entende, briga com cada um num canto, a Lu só some, a água bugada no galão, faltam os esqueletos lá fora, objeto entrando no outro" (25/10/2026).**
    - **Close de objeto:** precisa de detalhe de verdade (rótulo desenhado na lata, tampa, foco correndo) e câmera colada, deslizando.
    - **A ação conta a fala:** "a gente comia" mostra os quatro comendo à mesa; o POV mostra o garfo juntando o bocado e vindo para a boca (sai por baixo da lente), não só o prato diminuindo.
    - **Sentado é sentado:** quem está à mesa senta numa cadeira atrás do tampo. Ninguém de pé "dentro" da mesa.
    - **Objeto pequeno e importante:** precisa de gesto claro. A mão entra pela portinha aberta, pega pela gola e puxa, e o suéter se abre pendurado e mostra que é roupinha.
    - **Briga:** frente a frente, a menos de 1 m. Na câmera de segurança também.
    - **Morte e tempo:** quem morre vira esqueleto no mesmo lugar e na mesma pose (`esqueleto3d`, `esqueleto_deitado`). Quem ficou lá fora fica como esqueleto na frente da porta (`esqueletos_porta`).
    - **Líquido em recipiente inclinado:** fica de nível (`agua_de_nivel`, corte de meio volume por um plano horizontal).
    - **Antes de renderizar:** `kit3d/colisao_todos.sh` (modo `--colisao` do `anim3_abrigo.py`) em todos os planos.
      - COLISÃO: o que se mexe e entra em outra coisa.
      - ATRAVESSA: boneco ou esqueleto dentro de móvel, mesmo parado.
      - Só se aceita o que é de propósito (gente entrando pela porta do bunker).
14. **Rodada de 25/10/2026 (à noite): "comida desfocada; giz bugado; nos 23 s não dá para entender que a comida acabou; o braço atravessa a mesa; aos 47 s não tem emoção; o galão errado; lá fora a animação bugou".**
    - **Foco:** close de objeto com f/2 e câmera colada deixa tudo borrado. Para mostrar "a comida", use frente nítida (28 mm, f/11) e deslize a câmera de lado.
    - **Gesto de mão = personagem inteiro.** A mão preta solta no quadro de giz virou "bugado". Quem risca aparece de corpo inteiro, de lado, e o braço alcança o quadro por cinemática inversa (`ik3_abrigo.py`); o risco nasce atrás da ponta do giz. O quadro foi baixado (`GIZ_Z`) para o braço alcançar.
    - **Uma ideia que o espectador entenda sozinho:** "a comida acabou" = estante vazia + pilha de latas vazias abertas + o personagem olha dentro da última lata e deixa ela cair. Esvaziar a estante aos poucos (latas somem de baixo para cima, luz falhando) dá o "foi acabando".
    - **Comer:** a ponta do garfo vai à comida e à boca por cinemática inversa (`come` em `anim3_abrigo.py`). A mão fica sempre em cima da mesa; o corpo inclina para a frente (tronco **positivo** = para a frente; cabeça muito baixa afunda a boca no peito).
    - **Cinemática inversa no Heroi3D:** a ordem dos ângulos (ombro, depois abre) faz o `abre` não mexer no braço esticado para a frente; alvos lateral e à frente exigem `abre` grande. Prefira posicionar a pessoa de frente para o alvo.
    - **Cena emocional (morte):** a família junto, ajoelhada ao lado da cama (Zé de mão dada, Rita com a mão no ombro), câmera do outro lado da cama para ver os rostos; no plano seguinte, close do rosto de cima pelo pé da cama. Pálpebra: 1,0 não fecha o olho, 1,5 a 1,6 fecha.
    - **Líquido e galão:** o galão é levantado pela alça (agachar, agarrar, subir) e o galão segue a mão quadro a quadro; beber = boca do galão nos lábios (calculado pela posição da boca), duas mãos nele, água de nível.
    - **Saída para o mundo morto:** o clarão do plano anterior vira um véu branco colado na câmera que baixa em curva (não mexer na exposição, que mostra a borda do cenário). A saída da porta é filmada de lado, rente ao chão, com nuvens de cinza onde o pé pisa.
    - **Bug de edição:** ao reescrever planos por expressão regular, nomes de função com número (ex.: `p5A`, `banheiro3`) não casam em `[a-z_]+` e o recorte engole a função seguinte. Conferir sempre as funções que sumiram (comparar com o backup).

15. **"Desenvolver a história, refinar, colocar efeitos sonoros, deixar os gráficos de movimento mais suaves" (25/10/2026, noite).**
    - **Curvas suaves:** `anim3_abrigo.py` agora filtra todo canal de posição e rotação (gaussiana de 0,85 quadro, `SIGMA`) antes de renderizar; `--sem-suaviza` desliga. `--mede` conta os "trancos" (aceleração que salta) por plano; corrida de figurante sempre acusa muitos (a perna é periódica), o que importa é o antes e depois.
    - **Som sintetizado, sem crédito:** `kit3d/sfx_abrigo.py` (70 sons de numpy, filtros por FFT) + `kit3d/musica_abrigo.py` (trilha de rascunho que segue a história, com silêncios) + `kit3d/plano_som_abrigo.py` (um efeito por ação, no QUADRO: `t = (round(t0*24) + quadro - 1) / 24`; o plano trava se um arquivo se repetir). Mixagem pelo `mixagem.py` da skill historias-5-niveis, com `musica_db` 3. Em `roteiros/som-abrigo/`.
    - **Voz quase contínua:** quase não há pausa no abrigo, então efeito sobre a fala é limitado (golpe −5 dB, resto −8 dB). Efeito importante precisa de `golpe: true`. O relatório "efeitos que podem sumir" mostra o que ficou fraco.
    - **Conferir:** Whisper (`mlx_whisper ... --model mlx-community/whisper-large-v3-turbo`) no áudio final: todas as palavras do roteiro têm de aparecer.
    - **Crédito:** efeitos prontos de Higgsfield/ElevenLabs (ou a trilha do Higgsfield) só com aprovação; o rascunho usa só som sintetizado.

16. **Som v2 (25/10/2026, noite): "efeitos altos (mais depois), muitos barulhos aleatórios, a explosão com som grave de distorção do espaço-tempo, a porta com outro grave, nada repetido, a música não foi dramática, trocar de música, e no fim perguntar se querem continuação com o narrador 3D".**
    - **Menos é mais:** de 173 para 87 efeitos, com volumes ~40% menores. Só entra o que a imagem mostra e ajuda a contar; sem "ambiência" aleatória (gritos longe, moscas soltas, pano, fungar, pia, tilintar).
    - **Cada grave com timbre próprio:** a explosão é `espaco_tempo` (sub que oscila e fecha o ar, queda de tom 150 a 22 Hz com fase girando, vácuo curto e rumor; sem estampido e sem agudo). A porta é `porta_cofre` (raspão abafado, "tum" curto e seco de 48 Hz, três ferrolhos em fila e chiado da vedação). O "morreu" é `tum`. Os três não se parecem.
    - **Música dramática de verdade:** `kit3d/musica_abrigo_mix.py` costura trechos das trilhas orquestrais já aprovadas (presidente, reflexo, pcc7), trocando de música a cada cena e deixando silêncio em "Ele não abriu" e depois do clarão. Sem crédito. O `kit3d/mixagem_abrigo.py` (cópia do mixagem.py) deixa a música em −21 dB sob a fala, −12 nas pausas e −8 nos momentos, e a guarda de voz continua valendo. Trilha nova no Higgsfield só com aprovação.
    - **Fecho com o narrador 3D:** plano 12A, o "eu" de frente para a câmera, a boca no ritmo da voz (`fala_na_boca`, `envoltoria_voz`), a mão se abre na última frase, preto no começo e no fim. Voz: `roteiros/voz-abrigo/fecho_rascunho.wav` é voz de rascunho do macOS (grátis); a final é a voz Lucas da ElevenLabs (crédito, depende de aprovação do texto). `kit3d/monta_fecho.py FECHO.wav PALAVRAS.json` junta à narração (`narracao_final.wav`, `palavras_final.json`, `tempos_final.json`) e a boca se refaz sozinha ao renderizar o 12A.

17. **Fecho (25/10/2026): "o CTA demorou demais; não pode ter fade out; só a voz; não precisa de animação nova; o narrador já fala quando o vídeo termina: 'Quer continuação? Segue para a parte 2.'"**
    - **Fecho curto e sem plano novo:** a fala (voz Lucas, `[concerned]`, 2,6 s, 51 créditos, 1 take) entra 0,27 s depois da última frase ("num mundo que acabou") por cima do último plano (11D), que passa a segurar a imagem até o fim da fala. Nada de plano novo do narrador (o 12A foi tirado), nada de fade, nada de cartão: o filme termina cortando seco 0,12 s depois da última palavra.
    - **Só a voz:** a trilha termina com acorde sem resolver antes do fecho (cai em 70,7 s) e os efeitos acabam antes; no fecho só se ouve a voz.
    - **Como refazer:** `python3 kit3d/monta_fecho.py roteiros/voz-abrigo/fecho_lucas.wav roteiros/voz-abrigo/fecho_lucas_palavras.json` (gera `narracao_final.wav`, `palavras_final.json`, `tempos_final.json`; o 11D lê o total do `tempos_final.json`). Depois `musica_abrigo_mix.py`, `plano_som_abrigo.py`, `mixagem_abrigo.py` e render do 11D.
    - **Regra geral:** CTA no fim de vídeo é uma frase de 2 a 3 s dita sobre a última imagem, sem animação e sem fade.

18. **Suspense antes do CTA e a cena da porta (25/10/2026, noite):**
    - **Suspense:** depois de "num mundo que acabou", o 11D vira o plano do susto: a câmera está ESCONDIDA NOS DESTROÇOS, ao lado do abrigo e baixa, olhando o Zé e a Rita de lado (não de frente, nem de perfil puro); entulho desfocado na frente, um barulho fora do quadro (`escombro`, quadro 19), os dois viram a cabeça para o lado da câmera e, bem perto dela, no escuro e desfocado, um vulto curvado entra e rosna (`rosnado`, quadro 31). A voz do fecho começa em 72,45 s. O vulto é um `Heroi3D` com todos os materiais trocados por um tom quase preto (nunca se vê o que é).
    - **Bebendo e indo à porta:** nada de "levanta e vai torto". Ele bebe, baixa o galão com as duas mãos (cinemática inversa em cada estado; uma água de nível para cada inclinação, ligada no quadro certo), solta o ar e vira a cabeça para a porta, que aparece atrás; depois anda de verdade (rot 118°, passo firme, freando e virando de frente para a roda) com a câmera baixa andando junto e a Rita só olhando.
    - **A luz cresce, não "só brilha":** fio de luz pelas bordas da porta (9C), depois por trás do ombro do Zé o brilho em volta da fresta, a mancha no chão, três cortinas de névoa luminosa e poeira que crescem em curva (9D), a folha corre com o Zé andando junto (o corpo acompanha a roda, senão a mão fica no ar) e o branco só toma a tela nos últimos 7 quadros por um véu (nunca por exposição, que apaga a silhueta).
    - **Armadilha de edição:** ao reescrever um plano com `bloco()`, o texto novo não pode conter o plano seguinte (o 9E ficou duplicado e o antigo ganhou). Depois de editar, conferir `--list`, `grep '@shot("ID"'` e a posição da câmera lida no Blender.

19. **O narrador some (25/10/2026, depois do render cheio): "cadê eu, o personagem de vermelho? sumiu da cena?" e "revise se eu apareço nas cenas ou em primeira pessoa; mais direções de cena quebradas".**
    - **Regra:** o narrador ("eu", blusa vermelha escura) é personagem do filme, não só mãos. Em todo plano com o grupo (mesa, banheiro, briga, morte da Lu, final) ele aparece de corpo, ou entra em primeira pessoa (mãos de manga vermelha) quando a câmera é ele. Plano de objeto sozinho não precisa dele.
    - **Auditoria automática:** `blender -b -P kit3d/audita_elenco.py -- PLANO` lista quem está no quadro (cabeça dentro da imagem), se há mãos de POV e se o "eu" é CORPO, MÃOS ou ausente. Rode nos 67 planos antes do render cheio.
    - **Corrigido nesta rodada:** 3F e 4B (à mesa), 5D (tapa o nariz), 6G (janta), 7B e 7D (CCTV, no canto e de cabeça baixa), 7C (calado, no canto), 7E (ajoelhado com a família), 8B (CCTV) e o final 11A/11C/11D (sobreviveu junto, de vermelho, no meio dos dois). O suéter da Pipoca na 11A/11B passou para a mão de fora da Rita (longe do narrador).
    - **Outras direções quebradas achadas:** 3D (três lâmpadas giradas 90° pareciam pontos na parede: agora de baixo, em perspectiva, penduradas do teto); 7F (olhos nunca fechavam: o branco do olho achata até uma fresta, `fecha_olhos`).
    - **Armadilha:** pálpebra (`lid`) sozinha não fecha o olho com a câmera de frente; só serve para meio fechado.
