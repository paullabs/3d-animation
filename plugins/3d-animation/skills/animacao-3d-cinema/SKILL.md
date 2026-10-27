---
name: animacao-3d-cinema
description: Anima filmes narrados em 3D estilo IfverseTales no Blender por script (Canal 38), com continuidade de cinema e movimento de animador profissional. O método saiu do vídeo "O abrigo" (bunker, explosão de cogumelo, porta que fecha). A partir de uma decupagem plano a plano (tabela SHOTS), cada plano ganha tempo, com bonecos Heroi3D com mola por junta, corridas com fase própria, objetos que caem e quicam, câmera de operador sempre andando, desfoque de movimento, clarão que estoura e baixa, figurantes com horário único e cortes em que a ação começa num plano e termina no outro. Use SEMPRE para animar, refinar ou corrigir um rascunho 3D do Canal 38 ("anima", "deixa mais fluido", "mais orgânico", "corte sem sentido", "parece a mesma cena", "teletransporta", "buga quando…"), para revisar a continuidade de uma sequência, ou para continuar O abrigo. Não use para roteiro, voz ou som (isso é a historias-5-niveis), nem para colagem de papel (colagem-camadas).
---

# Animação 3D com sentido de cinema (Canal 38)

**Projeto:** `<pasta-do-projeto>` (o `CLAUDE.md` dessa pasta tem o estado de cada vídeo).
**Referência:** "O abrigo" inteiro, em `personagem/abrigo/anim/abrigo-filme-inteiro-rascunho-v1.mp4` (falas 1 e 2 refinadas em `abrigo-falas1-2-rascunho-v3.mp4`). Funções de exemplo em `anim3_abrigo.py`: `trilha` (objeto por chaves), `anda` (caminhada), `prende` (objeto na mão), `foco_passa`, `pisca_luz`, `moscas`, `vapor`, e câmera de segurança parada (`mao=0`).

## Como o Paulo avalia
- Ele assiste como espectador: **cada corte tem que ter sentido.** "Parece a mesma cena", "teletransporta", "não tem ninguém e depois aparece muita gente" e "buga" são falhas de continuidade, não de render.
- **Movimento:** leve, fluido, orgânico, "muito smooth". Nada de pose a pose, nada parado.
- **Vídeo primeiro, texto curto depois.** Antes de mostrar, faça a crítica que ele faria.
- **Crédito:** nada pago sem aprovação. **Resolução:** rascunho em meia resolução; a resolução cheia só depois do "pode".

## O fluxo
1. **Decupagem** (`kit3d/story3_<video>.py`): a tabela `SHOTS` (`@shot(id, t0, t1, palavras, lente, foco, mov, vemos)`) é a fonte única. Cada plano monta o cenário, os bonecos e a câmera do quadro-chave.
2. **Antes de animar, escreva a linha de ação da sequência** (quem está onde, em que segundo):
   - quem aparece depois já existia antes;
   - quem corre na frente chega primeiro;
   - quem fica para trás é quem bate na porta.
   Os figurantes têm uma tabela única de horário e velocidade (como `ATRASADOS` / `atrasados(t)`), e cada plano chama `atrasados(t0)`.
3. **Animação** (`kit3d/anim3_<video>.py`, molde: `anim3_abrigo.py`):
   - Ele registra os bonecos (`E3.faz`) e as mãos POV (`Mao3D`) criados no plano.
   - Cada plano tem uma função `aID(N)` que põe o tempo:
     - `corre(H, N, dy, fase, ciclo, freia, arranque, v0, dx)`: corrida com fase própria; lugar e giro seguem quase sem mola, para quem já entra correndo não nascer parado;
     - `parado(H, N)`: a pose do storyboard, viva;
     - `pedala`;
     - `acena`;
     - `rodas` e `gira_rodas`;
     - `alfa(material, chaves)`: transparência de um halo;
     - `exposicao(chaves)`: clarão;
     - `mao_mix`: troca de pose de mão em curva;
     - `camera_viva(N, vel, frente, mao, centro, extra)`: câmera que anda em velocidade constante e tem balanço de mão suave;
     - `soco(f, quadros)`: tranco curto na pancada.
   - Objetos que crescem pelo tempo do filme (como `cogumelo_em(r, T, f)`) são chaveados pelo `t0` do plano.
4. **Teste:** `python3 kit3d/anim3_rodar.py PASTA IDs --scale 0.3 --samples 6 --teste` (primeiro, meio e último quadro numa folha). Para quadros escolhidos: `blender -b -P kit3d/anim3_abrigo.py -- 2B PASTA --quadros 1,9,15,23`.
5. **Rascunho:** `anim3_rodar.py PASTA IDs --scale 0.5 --samples 10 --video saida.mp4 --t0 0 --t1 14.3` (todos os quadros e a voz). Para trocar um plano, renderize só ele e remonte com a lista dos outros.
5b. **Colisão (obrigatório):** `kit3d/colisao_todos.sh [IDs]`; só se aceita o que é de propósito (quem entra pela porta).
6. **Revisão antes de mostrar:**
   - folha a 6 qps do vídeo inteiro (`ffmpeg -vf fps=6,scale=135:-1,tile=12x8`);
   - 8 quadros seguidos de mão e de rosto;
   - leia a sequência como espectador: de onde veio cada pessoa? Dois planos seguidos parecem o mesmo? Alguém some ou aparece do nada?

## Cinemática inversa (braços)
`kit3d/ik3_abrigo.py` põe a mão (ou a ponta do garfo, do giz, a alça do galão) num ponto do mundo: `IK.braco_pose(H, "F", ponto, base, off=...)` devolve a pose; `IK.boca_de(H)` dá a boca. Use em tudo que a mão toca: mesa, prato, boca, quadro, galão, mão de outra pessoa. Funções prontas em `anim3_abrigo.py`: `riscar`, `come`, `familia`, `veu_branco`. Alvo fora do alcance sai no terminal como `IK ...: falta N cm`.

## Som e suavidade
Som sintetizado do filme: `kit3d/sfx_abrigo.py` (`ALL[nome](seed, ...)`), `kit3d/musica_abrigo.py`, `kit3d/plano_som_abrigo.py` (tabela `E(plano, quadro, som, vol, seed, golpe, dur)`), depois `python3 ferramentas/mixagem.py roteiros/som-abrigo/plano_som.json` e o Whisper. Curvas: `suaviza()` roda sozinha ao renderizar; `--mede` lista trancos por plano.

## Entrega final
Render cheio: `python3 kit3d/anim3_rodar.py PASTA IDs --scale 1.0 --samples 32 --jobs 8` (cada quadro leva poucos segundos; 1805 quadros em ~25 min). Monta com `ffmpeg` (concat + `mix.wav`, 11 Mbps, AAC 256) e depois a pós `kit3d/pos_fuji.py ENTRADA.mp4 SAIDA.mp4 [--forca 1.0]` (curva de filme, halação em RGB, grão, vinheta; nunca misturar a halação em YUV, fica rosa). Entregar também a versão sem a pós.

## Regras
Estão em `references/regras-animacao.md`: corpo, objetos, câmera, transição, sentido do corte e conferência. As críticas que geraram cada regra estão em `references/criticas.md`. Leia as duas antes de animar.

As mais cobradas:
- **Corte:** dois planos seguidos nunca do mesmo lugar com a mesma lente, e a ação começa num plano e termina no seguinte. Ninguém se teletransporta.
- **A ameaça fica à vista e muda com o tempo:** o cogumelo cresce e muda de cor, e o reflexo quente aparece no asfalto.
- **O clarão estoura e baixa;** a imagem nunca fica branca e sem história.
- **O "por pouco" precisa ser claro:** a porta fecha antes de o primeiro chegar, e ele bate no aço. Use um plano lateral, com a porta e quem chega no mesmo quadro.
- **POV:** manga comprida saindo do quadro e antebraço em diagonal, vindo do canto (nunca uma coluna vertical).
- **Corrida de figurante:** todos no mesmo ritmo do horário, cada um com fase, ciclo e inclinação próprios.

## Armadilhas técnicas
- Um render por processo do Blender: o kit guarda materiais entre cenas.
- `Heroi3D.anima` usa mola; quem entra correndo precisa de `molas=dict(pos=(0, 24, 1), rot=(0, 24, 1))`, senão nasce parado e patina.
- Material de halo (`cena.amat`): a transparência é o nó MULTIPLY (`alfa()`). Para o reflexo no chão, o disco é deitado (`rotation_euler.x = 90°`).
- A porta de fora (`entrada_bunker`) é girada 180°: `bunker_porta_folha.location.x = aberta * 1.1`.
- Quem atravessa a porta some dentro da caixa de luz `bunker_dentro`, que é opaca.
- A câmera no pórtico fica atrás do halo âmbar: `sem_halo_do_bunker()`.
