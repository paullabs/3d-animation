---
name: iniciar
description: Prepara a pasta de trabalho do projeto com o kit 3D, as ferramentas de mixagem, as regras e os roteiros de referência. Rodar uma vez por projeto (e de novo com --atualizar para pegar uma versão nova do plugin).
argument-hint: "[pasta] [--atualizar]"
disable-model-invocation: true
---

# Iniciar um projeto de animação 3D

Rode, na pasta que o usuário indicar (sem argumento, a pasta atual):

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/animacao3d.py" iniciar $ARGUMENTS
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/animacao3d.py" doctor $ARGUMENTS
```

(Se `$ARGUMENTS` trouxer `--atualizar`, tire-o do segundo comando; o `doctor` só recebe a pasta.)

Depois:
1. Diga em português simples o que foi criado: `kit3d/` (código), `ferramentas/` (mixagem e efeitos), `roteiros/` (roteiros e tempos de voz dos vídeos de referência), `CLAUDE.md` (as regras do estilo) e as pastas de trabalho.
2. Se o `doctor` marcou `FALTA`, explique o que falta e o comando de instalação, e **pergunte antes** de instalar qualquer coisa (brew, pip). Blender 5.x e ffmpeg são obrigatórios; `mlx_whisper` é opcional.
3. Termine dizendo o próximo passo: `/3d-animation:testar` para provar que renderiza e `/3d-animation:novo-video` para começar uma história.

Com `--atualizar`, os arquivos do kit que mudaram são trocados e os antigos ficam em `kit3d/_antes_da_atualizacao/`. Nunca apague nada do usuário.
