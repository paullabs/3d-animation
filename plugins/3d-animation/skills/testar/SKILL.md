---
name: testar
description: Confere o ambiente (Blender, ffmpeg, Python, voz do Mac) e renderiza 3 quadros de prova para mostrar que o plugin funciona. Grátis, cerca de 1 minuto.
argument-hint: "[pasta-do-projeto]"
disable-model-invocation: true
---

# Testar o plugin

> **Raiz do plugin (Claude Code e Codex).** Os comandos abaixo precisam da pasta do plugin, que o Claude Code chama de CLAUDE_PLUGIN_ROOT. O Claude Code troca a variável pelo caminho antes de você ler este texto. O Codex e outros agentes não trocam: lá a variável sai vazia, e o comando falha com "can't open file" ou "No such file". Se os comandos abaixo ainda mostram a variável escrita com cifrão e chaves, em vez de um caminho de pasta, **pare antes de rodar qualquer um**: a raiz do plugin é a pasta duas acima da pasta desta skill, a que tem o arquivo `scripts/animacao3d.py`. Confirme que o arquivo existe lá e use esse caminho absoluto no lugar da variável em todos os comandos. Nunca rode um comando com a raiz vazia.

Na pasta do projeto (já preparada com `/3d-animation:iniciar`):

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/animacao3d.py" doctor $ARGUMENTS
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/animacao3d.py" exemplo $ARGUMENTS
```

O segundo comando renderiza 3 quadros do plano 1A do vídeo "Os passos" em resolução pequena e grava a folha em `render_teste/exemplo/teste1.png`.

Depois:
1. Abra a folha com Read e mostre a imagem ao usuário primeiro. Deve ter dois bonecos (um de blusa vermelha e outro verde) andando numa rua, com um ônibus à direita, e no último quadro o vermelho maior com poeira no chão.
2. Diga em uma ou duas frases se funcionou. Se não funcionou, leia o erro, ache a causa (quase sempre Blender fora da versão 5.x, ffmpeg ou módulo Python faltando) e diga o conserto; não tente consertar instalando coisas sem perguntar.
