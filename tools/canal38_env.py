"""Onde está cada coisa: pasta do projeto, kit e Blender, num lugar só.
O plugin Canal 38 troca os caminhos fixos do autor por estas constantes.
- CANAL38_PROJETO: pasta de trabalho (padrão: a pasta que contém kit3d/)
- CANAL38_BLENDER: executável do Blender 5.x (padrão: acha sozinho)"""
import glob, os, shutil

KIT = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.environ.get("CANAL38_PROJETO") or os.path.dirname(KIT)
PADRAO_MAC = "/Applications/Blender.app/Contents/MacOS/Blender"


def _blender():
    env = os.environ.get("CANAL38_BLENDER")
    if env:
        return env
    achados = [PADRAO_MAC, os.path.expanduser("~/Applications/Blender.app/Contents/MacOS/Blender")]
    achados += sorted(glob.glob("/Applications/Blender*.app/Contents/MacOS/Blender"), reverse=True)
    achados += [shutil.which("blender") or ""]
    for c in achados:
        if c and os.path.exists(c):
            return c
    return PADRAO_MAC


BLENDER = _blender()
