# 3D Animation (plugin para o Claude Code)

Reels verticais narrados em **3D animation**: bonecos de cabeça preta, olho branco e borda de luz, dentro de salas e cidades 3D de verdade, feitos no Blender por script. O plugin traz o kit pronto (cerca de 49 mil linhas de código em 225 módulos Python), as regras de cinema aprendidas com cada recusa, voz de teste grátis, efeitos e trilha sintetizados, mixagem com guarda de voz e render. Você instala e conta a história; não recria o motor.

## O que você precisa (uma vez)
- **macOS** (feito e testado no Mac com Apple Silicon: usa a voz `say` e as fontes da Apple)
- **Claude Code** (app desktop ou terminal)
- **Blender 5.x** ([blender.org/download](https://www.blender.org/download/))
- **ffmpeg** (`brew install ffmpeg`) e **Python 3.9+** com `pillow` e `numpy` (`pip3 install pillow numpy`)
- Opcional: `mlx-whisper` (`pipx install mlx-whisper`) para o tempo exato de cada palavra

## Instalar
No Claude Code:

```
/plugin marketplace add paullabs/3d-animation
/plugin install 3d-animation@3d-animation
```

Depois, numa pasta nova para o seu projeto, abra uma sessão do Claude e rode:

```
/3d-animation:iniciar
/3d-animation:testar
/3d-animation:novo-video uma ideia de história
```

## Comandos
| Comando | O que faz |
|---|---|
| `/3d-animation:iniciar [pasta] [--atualizar]` | Põe o kit, as ferramentas, os roteiros de referência e o `CLAUDE.md` com as regras na pasta de trabalho. Com `--atualizar`, pega a versão nova do plugin e guarda os arquivos antigos |
| `/3d-animation:testar` | Confere Blender, ffmpeg, Python e voz do Mac e renderiza 3 quadros de prova (grátis, ~1 min) |
| `/3d-animation:novo-video <ideia>` | Conduz a história por fases, com aprovação em cada uma: roteiro, voz, ficha, decupagem, animação, som, render |
| `/3d-animation:voz-teste roteiro.json` | Voz do Mac + tempo de cada frase e palavra, sem custo |

Skills que o Claude carrega sozinho quando o assunto aparece: `regras-do-estilo`, `catalogo-do-kit` (qual arquivo copiar para cada formato), `historias-5-niveis` e `animacao-3d-cinema`.

## O que vem dentro
- `kit3d/`: motor (boneco 3D com mola por junta e IK, câmera de operador, cenários, objetos, colisão, medidor de movimento, profundidade, efeito de filme) e os vídeos de referência prontos para copiar: **5 níveis**, **"e se…"**, **medição** ("Os passos"), **filme de suspense** ("O abrigo", partes 1 e 2) e **mapa 3D de trânsito**. Índice em `kit3d/INDICE.md`.
- `ferramentas/`: `mixagem.py` (só passa com GUARDA OK: a voz nunca some) e `sfx.py` (efeitos sintetizados).
- `roteiros/`: 14 roteiros e os tempos de voz dos vídeos de referência (o kit lê esses arquivos). Sem áudio nem imagem.
- Regras: roteiro, voz, imagem, cinema, som e entrega, cada uma com o porquê.

## Custo
- **Grátis:** voz de teste do Mac, efeitos e trilha sintetizados, render no seu Mac.
- **Pago e opcional, só no fim e só com a sua aprovação:** voz final (ElevenLabs, voz Lucas) e trilha ou imagem (Higgsfield).
- O Claude continua gastando tokens para escrever o roteiro, decupar e adaptar cenas. O que o plugin tira é o custo de reinventar o kit e de errar de novo o que já foi corrigido.

## Limites conhecidos
- Só macOS testado. Em outro sistema as fontes e a voz precisam de ajuste.
- O render cheio de um vídeo de 80 s leva cerca de 15 a 25 min num Mac com muitos núcleos; os quadros ocupam dezenas de GB (apague `render_*` depois).
- O kit usa a API do Blender 5.2; outras versões 5.x podem pedir ajuste.
- A série de trânsito vem com o mapa de São Paulo (Ponte Estaiada). Para outra cidade, baixe um `.osm` e converta com `kit3d/tb_osm.py`.

## Para quem mantém o plugin
Depois de evoluir o kit no projeto de trabalho, rode:

```bash
python3 tools/sincronizar_do_projeto.py "/caminho/do/projeto"
claude plugin validate plugins/3d-animation
```

O sincronizador copia o código sem backups, troca os caminhos do Mac do autor por `canal38_env` (`CANAL38_PROJETO`, `CANAL38_BLENDER`), gera o índice e atualiza skills, regras e roteiros de referência.

## Licença
MIT (veja `LICENSE`). Mapa: © colaboradores do OpenStreetMap (ODbL).
