# Render, conferência e entrega

## Comandos
Rode tudo de dentro de `kit3d/`.
```
# lista das cenas e quadros (já com os tempos da voz nova)
/Applications/Blender.app/Contents/MacOS/Blender -b --factory-startup --python prod_X.py -- x x --list

# conferir o enquadramento de uma cena
VERIFICA=1 Blender -b --factory-startup --python prod_X.py -- b3 OUT --scale 0.3 --samples 8 --at 19.0

# rascunho (cerca de 6 min com 4 jobs)
python3 render_pcc.py --prod prod_X.py --scale 0.5 --samples 10 --jobs 4 --force --out ../render_X/s0.5

# final (cerca de 25 min)
python3 render_pcc.py --prod prod_X.py --scale 1.0 --samples 32 --jobs 4 --force --out ../render_X/s1

# antes do render: zero colisões em todas as cenas
for k in 01 02 …; do Blender -b --factory-startup --python colisao.py -- prod_X.py s$k | grep COLISÃO & done; wait

# legendas (sempre em 1080x1920), desviando dos rostos gravados no render
python3 overlay_X.py ../render_X/s1/overlay.mov --rostos ../render_X/s1

# montagem: cortes com borrão; a1>a2 vertical (subida), os demais horizontais
python3 montar_teste.py --dir ../render_X/s1 --scale 1.0 --ov ../render_X/overlay.mov --audio ../roteiros/som-X/mix.wav \
  --borrao "a1:fim:v:300:4,a2:inicio:v:300:4,a2:fim:h:300:4,b1:inicio:h:300:4,…" --out ../personagem/X/X-final.mp4
```
Rode renders longos em segundo plano e espere a notificação.

**Atenção:** o shell do Bash é zsh, e lá a lista começa em 1. Para montar a lista do `--borrao`, use Python.

## Conferência antes de mostrar (sempre)
1. **Folha de quadros:** cerca de 25 quadros espalhados (`ffmpeg -ss t …`, colados numa imagem). Procure:
   - assunto cortado ou fora da área segura;
   - parede vazia ou momento morto;
   - rótulo de nível na cena errada;
   - legenda ilegível;
   - cor repetida entre cenas seguidas;
   - herói sumindo no fundo.
2. **Áudio:** transcreva com o Whisper. Todas as palavras têm de aparecer, e a mixagem tem de dar GUARDA OK.
3. Se achou erro, corrija e renderize só a cena afetada (`--only b10`, ou o Blender direto na pasta da cena), depois monte de novo.

## Entrega
- `SendUserFile` com o **vídeo primeiro**, legenda curta. O texto vem **depois**: o que mudou, em tópicos curtos, e o que não foi conferido.
- Na versão final em resolução cheia, diga as especificações: 1080×1920, 24 qps, duração.
- Guarde os arquivos de cada versão (`-v7`, `-v7b`, `-v7c-final`): ele compara versões.

## Qualidade do arquivo final (reflexo, 24/10/2026: "tá em alta qualidade e alto bitrate?")
- O rascunho do v19 era 1080×1920 só na embalagem: a imagem foi renderizada em 540×960 (`--scale 0.5`) e ampliada, a 2,6 Mbps. **Nunca chame de final um arquivo montado de um render em meia resolução.**
- Em imagem limpa (`--limpo`, sem ruído), o `crf` 19 do `montar_teste.py` entrega só 3 a 4 Mbps no 1080×1920. Para o final use `--crf-seg 8 --crf-final 8 --preset-final slow --audio-kbps 256` (11,5 Mbps, 73 MB, 50 s). O final aprovado do presidente tinha 23 Mbps porque tem grão.
- Receita completa:

```
python3 render_pcc.py --prod prod_X.py --scale 1.0 --samples 32 --jobs 3 --force --out ../render_X/final     # ~13 min
python3 overlay_X.py ../render_X/final/overlay.mov --rostos ../render_X/final
python3 montar_teste.py --dir ../render_X/final --ov ../render_X/final/overlay.mov --audio ../roteiros/som-X/mix.wav --scale 1.0 --limpo \
  --crf-seg 8 --crf-final 8 --preset-final slow --audio-kbps 256 --out ../personagem/X/X-final.mp4
```
- **Conferir no arquivo final:** `ffprobe` (largura, altura, bitrate), Whisper sobre o áudio extraído, e a correlação do áudio com o `mix.wav` (sem subamostrar: 7 em 7 amostras dá 0,07 e parece erro; o certo dá 0,98).
