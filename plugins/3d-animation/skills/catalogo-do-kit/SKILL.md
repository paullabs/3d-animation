---
name: catalogo-do-kit
description: Mapa do kit 3D (kit3d/): qual arquivo copiar para cada formato de vídeo (5 níveis, "e se...", medição, filme POV com suspense, mapa de trânsito), o motor comum e os comandos de render. Leia antes de criar ou adaptar um vídeo.
---

# Catálogo do kit3d

Lista completa, uma linha por arquivo: `kit3d/INDICE.md`. Este mapa diz **qual modelo copiar**. Num vídeo novo, copie o modelo mais parecido para `prod_<tema>.py` (ou `story_<tema>.py` + `anim_<tema>.py`), troque as cenas e mantenha os ajudantes: eles carregam todas as correções.

## Escolha do formato
| Formato | Modelo para copiar | Skill |
|---|---|---|
| **5 níveis** ("Você acabou de virar/entrar…": quanto ganha e o que cobra cada degrau; 2D falso em salas 3D) | `prod_presidente.py` (14 cenas, uma por fala), `overlay_presidente.py` (legenda), `plano_som_presidente.py` | `historias-5-niveis` |
| **"E se…"** com comparação e régua | `prod_reflexo.py`, `overlay_reflexo.py`, `plano_som_reflexo.py`, `elenco_reflexo.py`, `objetos_reflexo.py` | `historias-5-niveis` |
| **Medição e escala** (o corpo cresce, cada fato tem prova ao lado) | `story_passos9.py` + `anim_passos9.py` + `anim_passos9_rodar.py`; mundo fixo em `mundo7.py`, poses em `poses_passos.py`, objetos em `objetos3d_passos_b.py` | `animacao-3d-cinema` |
| **Filme narrado em 3D com suspense** (POV, bunker, monstro; decupagem de cinema) | parte 1: `story3_abrigo.py` (tabela `SHOTS`) → `story3_rodar.py` → `anim3_abrigo.py` → `anim3_rodar.py`; parte 2: `story_abrigo2.py`, `acoes_abrigo2*.py`, `anim_abrigo2_rodar.py` | `animacao-3d-cinema` |
| **Série de mapa 3D de trânsito** (cidade vista de cima, simulação de carros) | `tb_sanfona.py` (cena), `tb_trafego.py` (simulação), `tb_mapa.py`, `tb_assets.py`, `anim_ep1c.py`; mapa de São Paulo já em `transito/dados_osm/`; outra cidade: `tb_osm.py` converte um `.osm` | `animacao-3d-cinema` |

## Motor comum (não reescrever)
- **Boneco 3D** com mola por junta e IK: `heroi3d.py` (`Heroi3D.anima`, `.pose`, `.expressao`), `ik3_abrigo.py`; elenco: `elenco3d_abrigo.py`, `elenco.py`; mãos: `objetos3d_abrigo.py` (`Mao3D`).
- **Cenários e objetos 3D:** `ambiente3d.py`, `cidade3d.py`, `ambiente_noite.py`, `ambiente_galpao.py`, `objetos3d_abrigo*.py`, `objetos3d_passos*.py`.
- **Câmera e movimento:** `anim3_abrigo.py` (`camera_viva`, `suaviza`), `curvas.py`, `tb_camera_suave.py` (câmera planejada em ondas).
- **Conferências:** `colisao.py`, `colisao_todos.sh`, `mede_mov.py`, `contraste.py`, `rostos.py`, `audita_elenco.py`.
- **Imagem final:** `profundidade.py` (desfoque, névoa, vinheta), `pos_fuji.py` (efeito de filme), `pos_cctv.py`, legendas `legenda_passos.py` (uma palavra por vez) e `overlay_*.py`.
- **Voz e tempo:** `voz.py` (voz do Mac, grátis), `voz_eleven.py` (ElevenLabs, pago), `palavras.py` (tempo por palavra), `voz_medida.py`.
- **Som:** `sfx_abrigo.py`, `sfx_passos.py`, `sfx_reflexo.py` (efeitos sintetizados), `musica_abrigo.py`, `musica_passos_mix.py`, `ferramentas/sfx.py` e `ferramentas/mixagem.py`.
- **Montagem:** `render_pcc.py` (render em paralelo), `montar_teste.py`, `mux.py`.

## Comandos de render
- Rodadores de cada vídeo já chamam o Blender sozinhos: `python3 kit3d/anim_passos9_rodar.py PASTA [IDs] --scale 0.5 --samples 10 --jobs 8 [--teste] [--video saida.mp4]`.
- Série "prod" (5 níveis e "e se"): `python3 kit3d/render_pcc.py --prod prod_<video>.py --scale 0.5 --samples 10 --jobs 6 --out ../render_<video>/v1`, depois `overlay_<video>.py` e `montar_teste.py`.
- Um plano à mão: `<Blender> -b -P kit3d/<script>.py -- <args>` (o caminho do Blender está em `kit3d/canal38_env.py`).
- Rascunho em `--scale 0.5 --samples 10`; resolução cheia (`--scale 1.0 --samples 32`) só depois do OK.

## Armadilhas que já custaram caro
- Um render por processo do Blender: o kit guarda materiais entre cenas.
- Os módulos leem na importação `roteiros/voz-<video>/tempos.json` e `palavras.json`: um vídeo novo precisa dos dele antes de listar ou renderizar planos.
- O kit foi feito para o Blender 5.2 (API de ações e compositor mudou no 5.x).
- Mais armadilhas por vídeo estão nas skills `historias-5-niveis` e `animacao-3d-cinema`.
