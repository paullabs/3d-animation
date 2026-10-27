#!/bin/zsh
# confere colisão em todos os planos do abrigo (não renderiza): ./colisao_todos.sh [IDs...]
cd "$(dirname "$0")"
IDS=${@:-$(/Applications/Blender.app/Contents/MacOS/Blender -b -P story3_abrigo.py -- --list 2>/dev/null | grep -E "^[0-9]+[A-Z]+ \|" | cut -d' ' -f1)}
for i in ${=IDS}; do echo $i; done | xargs -P 8 -I{} sh -c '/Applications/Blender.app/Contents/MacOS/Blender -b -P anim3_abrigo.py -- {} /tmp/x --scale 0.1 --colisao 2>/dev/null | grep -E "COLISÃO|ATRAVESSA|CONFERIDO|Error"'
