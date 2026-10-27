#!/bin/bash
# renderiza o rascunho v3 do ep. 1 do trânsito em 4 partes paralelas (meia resolução)
cd "$(cd "$(dirname "$0")/.." && pwd)"
OUT=render_transito/ep1c_v1
mkdir -p $OUT
for i in 0 1 2 3; do
  /Applications/Blender.app/Contents/MacOS/Blender -b -P kit3d/anim_ep1c.py -- render $OUT --escala 0.5 --parte $i/4 > render_transito/ep1c_log_$i.txt 2>&1 &
done
wait
echo feito
