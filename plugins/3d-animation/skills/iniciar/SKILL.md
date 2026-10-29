---
name: iniciar
description: Prepara a pasta de trabalho do projeto com o kit 3D, as ferramentas de mixagem, as regras e os roteiros de referência. Rodar uma vez por projeto (e de novo com --atualizar para pegar uma versão nova do plugin).
argument-hint: "[pasta] [--atualizar]"
disable-model-invocation: true
---

# Iniciar um projeto de animação 3D

## Antes de começar: o plugin está instalado para todas as pastas?

Se a pessoa instalou o plugin só para uma pasta, ele some quando ela abre o Claude Code em outra. Confira isto primeiro, sem instalar nada ainda:

1. **Claude Code:** rode `claude plugin list --json` e procure o item `3d-animation@3d-animation`.
   - Existe um item com `"scope": "user"` e `"enabled": true`: está **global**. Siga.
   - Só existe com `"scope": "project"` ou `"local"` (vem junto o `projectPath`): **não está global**, vale só para aquela pasta. Diga isso numa frase e ofereça `claude plugin install 3d-animation@3d-animation --scope user`. Só rode com o sim da pessoa.
   - Não aparece: o plugin foi carregado de uma pasta avulsa, ou o `claude` do terminal não é o da pessoa. Diga que **não está instalado**, mostre os comandos de instalação do `README.md` e siga só se ela quiser.
2. **Codex:** rode `codex plugin list` e procure `3d-animation@3d-animation`: tem de dizer `installed, enabled`. Se não disser, ofereça `codex plugin add 3d-animation@3d-animation`.
3. Se o comando `claude` ou `codex` não existir, ignore aquele item: a pessoa pode usar só um dos dois.

> **Raiz do plugin (Claude Code e Codex).** Os comandos abaixo precisam da pasta do plugin, que o Claude Code chama de CLAUDE_PLUGIN_ROOT. O Claude Code troca a variável pelo caminho antes de você ler este texto. O Codex e outros agentes não trocam: lá a variável sai vazia, e o comando falha com "can't open file" ou "No such file". Se os comandos abaixo ainda mostram a variável escrita com cifrão e chaves, em vez de um caminho de pasta, **pare antes de rodar qualquer um**: a raiz do plugin é a pasta duas acima da pasta desta skill, a que tem o arquivo `scripts/animacao3d.py`. Confirme que o arquivo existe lá e use esse caminho absoluto no lugar da variável em todos os comandos. Nunca rode um comando com a raiz vazia.

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
