---
name: voz-teste
description: Gera de graça a voz de teste (voz do Mac) de um roteiro, com o tempo de cada frase e de cada palavra, para animar e sincronizar sem gastar crédito.
argument-hint: "roteiros/<video>.json [--voz Luciana] [--taxa 185]"
disable-model-invocation: true
---

# Voz de teste, sem custo

> **Raiz do plugin (Claude Code e Codex).** Os comandos abaixo precisam da pasta do plugin, que o Claude Code chama de CLAUDE_PLUGIN_ROOT. O Claude Code troca a variável pelo caminho antes de você ler este texto. O Codex e outros agentes não trocam: lá a variável sai vazia, e o comando falha com "can't open file" ou "No such file". Se os comandos abaixo ainda mostram a variável escrita com cifrão e chaves, em vez de um caminho de pasta, **pare antes de rodar qualquer um**: a raiz do plugin é a pasta duas acima da pasta desta skill, a que tem o arquivo `scripts/animacao3d.py`. Confirme que o arquivo existe lá e use esse caminho absoluto no lugar da variável em todos os comandos. Nunca rode um comando com a raiz vazia.

Pré-requisito: projeto iniciado (`/3d-animation:iniciar`) e um roteiro no formato de `roteiros/passos-dobrando.json`.

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/animacao3d.py" voz-teste $ARGUMENTS
```

Isto gera, em `roteiros/voz-<video>/teste/` (ou na pasta indicada): `narracao.wav`, `tempos.json` (início e duração de cada frase) e `palavras.json` (tempo de cada palavra; exato com `mlx_whisper`, aproximado pelo tamanho da palavra sem ele).

Depois:
1. Diga a duração total e a voz usada.
2. Lembre que é voz de teste: serve para decupar, animar e aprovar. A voz final (ElevenLabs, voz Lucas) é paga e só entra no fim, com aprovação. Ao trocá-la, os tempos mudam: rode `kit3d/decupagem_tempos_abrigo2.py` (ou o equivalente do vídeo) e refaça o que depende de tempo.
3. Regra da voz: nunca mudar o tom (pitch); só EQ, nível e `atempo`.
