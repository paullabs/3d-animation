#!/usr/bin/env python3
"""3D animation: ferramenta de linha de comando do plugin (sem custo, nada de API paga).
python3 animacao3d.py iniciar [PASTA] [--atualizar]   põe o kit, as ferramentas e os exemplos na pasta de trabalho
python3 animacao3d.py doctor [PASTA]                  confere Blender, ffmpeg, Python, fontes e a voz do Mac
python3 animacao3d.py exemplo [PASTA]                 renderiza 3 quadros de prova (grátis, cerca de 1 minuto)
python3 animacao3d.py voz-teste ROTEIRO.json [PASTA_SAIDA] [--voz NOME] [--taxa N]
                                                      voz do Mac + tempos + palavras de um roteiro (grátis)"""
import datetime, filecmp, glob, os, platform, re, shutil, subprocess, sys

PLUGIN = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PASTAS = ["roteiros", "personagem", "entregas", "referencias"]
GITIGNORE = "# quadros renderizados ocupam muito e dá para refazer\nrender_*/\nrender/\n*.blend1\n__pycache__/\n.DS_Store\n"


def ok(msg): print("  OK    " + msg)
def falta(msg): print("  FALTA " + msg)
def aviso(msg): print("  AVISO " + msg)


def blender_exe():
    sys.path.insert(0, os.path.join(PLUGIN, "kit3d"))
    import canal38_env
    return canal38_env.BLENDER


def copia_arvore(origem, destino, atualizar):
    """copia sem apagar nada do usuário; com --atualizar troca o que mudou e guarda o antigo"""
    novos = trocados = mantidos = 0
    guarda = os.path.join(destino, "_antes_da_atualizacao", datetime.datetime.now().strftime("%Y%m%d-%H%M%S"))
    for raiz, dirs, arqs in os.walk(origem):
        dirs[:] = [d for d in dirs if d != "__pycache__"]
        rel = os.path.relpath(raiz, origem)
        for a in arqs:
            if a == ".DS_Store":
                continue
            src = os.path.join(raiz, a)
            dst = os.path.normpath(os.path.join(destino, rel, a))
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            if not os.path.exists(dst):
                shutil.copy2(src, dst); novos += 1
            elif filecmp.cmp(src, dst, shallow=False):
                continue
            elif atualizar:
                os.makedirs(guarda, exist_ok=True)
                shutil.move(dst, os.path.join(guarda, a))
                shutil.copy2(src, dst); trocados += 1
            else:
                mantidos += 1
    return novos, trocados, mantidos


def iniciar(pasta, atualizar):
    pasta = os.path.abspath(os.path.expanduser(pasta or "."))
    if os.path.realpath(pasta).startswith(os.path.realpath(PLUGIN)):
        sys.exit("Escolha uma pasta de trabalho fora da pasta do plugin.")
    os.makedirs(pasta, exist_ok=True)
    print(f"Pasta de trabalho: {pasta}")
    n, t, m = copia_arvore(os.path.join(PLUGIN, "kit3d"), os.path.join(pasta, "kit3d"), atualizar)
    print(f"  kit3d: {n} novos, {t} atualizados, {m} mantidos como estavam (use --atualizar para trocar)")
    n, t, m = copia_arvore(os.path.join(PLUGIN, "ferramentas"), os.path.join(pasta, "ferramentas"), atualizar)
    print(f"  ferramentas (mixagem e efeitos): {n} novos, {t} atualizados")
    for p in PASTAS:
        os.makedirs(os.path.join(pasta, p), exist_ok=True)
    n, _, _ = copia_arvore(os.path.join(PLUGIN, "exemplos", "roteiros"), os.path.join(pasta, "roteiros"), False)
    print(f"  roteiros e tempos de voz dos vídeos de referência: {n} novos em roteiros/ (o kit lê estes arquivos)")
    if os.path.isdir(os.path.join(PLUGIN, "exemplos", "transito")):
        n, _, _ = copia_arvore(os.path.join(PLUGIN, "exemplos", "transito"), os.path.join(pasta, "transito"), False)
        print(f"  mapa de São Paulo para a série de trânsito: {n} novo em transito/dados_osm")
    modelo = os.path.join(PLUGIN, "modelo-projeto", "CLAUDE.md")
    alvo = os.path.join(pasta, "CLAUDE.md")
    if not os.path.exists(alvo):
        shutil.copy(modelo, alvo); print("  CLAUDE.md criado (as regras do estilo; ajuste ao seu gosto)")
    else:
        print("  CLAUDE.md já existe (mantido)")
    if not os.path.exists(os.path.join(pasta, ".gitignore")):
        open(os.path.join(pasta, ".gitignore"), "w").write(GITIGNORE)
    print("\nPronto. Abra uma sessão do Claude nesta pasta. Depois rode /3d-animation:testar e /3d-animation:novo-video")
    return pasta


def versao(cmd):
    try:
        return subprocess.run(cmd, capture_output=True, text=True, timeout=30).stdout.strip().splitlines()[0]
    except Exception:
        return ""


def doctor(pasta):
    pasta = os.path.abspath(os.path.expanduser(pasta or "."))
    essencial = True
    print("Conferindo o ambiente\n")
    if platform.system() == "Darwin":
        ok(f"macOS ({platform.machine()})")
    else:
        aviso(f"{platform.system()}: o kit foi feito e testado no macOS (voz say, fontes da Apple). Pode precisar de ajustes.")
    if sys.version_info >= (3, 9):
        ok("Python " + platform.python_version())
    else:
        falta("Python 3.9 ou mais novo"); essencial = False
    for mod, pip in (("PIL", "pillow"), ("numpy", "numpy")):
        try:
            __import__(mod); ok(f"módulo {mod}")
        except ImportError:
            falta(f"módulo {mod}  ->  pip3 install {pip}"); essencial = False
    bl = blender_exe()
    if os.path.exists(bl):
        v = versao([bl, "--version"])
        if re.search(r"Blender 5\.", v):
            ok(f"{v} ({bl})")
        else:
            aviso(f"{v or 'versão desconhecida'}: o kit usa o Blender 5.x (API do 5.2). Baixe em blender.org/download")
    else:
        falta(f"Blender 5.x não encontrado. Instale (blender.org/download) ou aponte: export CANAL38_BLENDER=/caminho/Blender"); essencial = False
    for f in ("ffmpeg", "ffprobe"):
        if shutil.which(f):
            ok(f)
        else:
            falta(f"{f}  ->  brew install ffmpeg"); essencial = False
    if shutil.which("say"):
        vozes = subprocess.run(["say", "-v", "?"], capture_output=True, text=True).stdout
        pt = [l.split()[0] for l in vozes.splitlines() if "pt_BR" in l]
        ok("voz do Mac (say), vozes em português: " + (", ".join(pt[:5]) or "nenhuma; instale em Ajustes > Acessibilidade > Conteúdo falado"))
    else:
        aviso("comando say ausente: sem voz de teste grátis; use outra voz e passe o .wav")
    if shutil.which("mlx_whisper") or os.path.exists(os.path.expanduser("~/.local/bin/mlx_whisper")):
        ok("mlx_whisper (tempo exato de cada palavra)")
    else:
        aviso("mlx_whisper ausente (opcional): sem ele a legenda por palavra usa o tamanho da palavra  ->  pipx install mlx-whisper")
    for nome, caminho in (("Avenir Next", "/System/Library/Fonts/Avenir Next.ttc"), ("Arial Black", "/System/Library/Fonts/Supplemental/Arial Black.ttf")):
        (ok if os.path.exists(caminho) else aviso)(f"fonte {nome}" + ("" if os.path.exists(caminho) else " ausente (legendas e títulos podem sair com outra fonte)"))
    if os.path.isdir(os.path.join(pasta, "kit3d")):
        ok(f"kit3d na pasta de trabalho ({pasta})")
    else:
        aviso(f"sem kit3d em {pasta}  ->  /3d-animation:iniciar")
    pagos = [("ElevenLabs", "voz final do Lucas"), ("Higgsfield", "música e imagem")]
    print("\nOpcionais e pagos (não são necessários): " + "; ".join(f"{a} ({b})" for a, b in pagos))
    print("\nResultado:", "tudo certo para renderizar." if essencial else "falta instalar o que está marcado FALTA.")
    return 0 if essencial else 1


def exemplo(pasta):
    pasta = os.path.abspath(os.path.expanduser(pasta or "."))
    kit = os.path.join(pasta, "kit3d")
    if not os.path.isdir(kit):
        sys.exit("Rode primeiro: /3d-animation:iniciar")
    saida = os.path.join(pasta, "render_teste", "exemplo")
    shutil.rmtree(saida, ignore_errors=True)
    cmd = [sys.executable, os.path.join(kit, "anim_passos9_rodar.py"), saida, "1A", "--scale", "0.25", "--samples", "4", "--jobs", "1", "--teste"]
    print("Renderizando 3 quadros do plano 1A (vídeo 'Os passos'), meia da meia resolução...")
    r = subprocess.run(cmd, cwd=kit, capture_output=True, text=True)
    print(r.stdout[-800:])
    folhas = sorted(glob.glob(os.path.join(saida, "teste*.png")))
    if r.returncode == 0 and folhas:
        print("FUNCIONOU. Folha de prova:", folhas[0])
        return 0
    print(r.stderr[-1500:])
    print("NÃO FUNCIONOU. Rode: python3 animacao3d.py doctor")
    return 1


def voz_teste(args):
    if not args:
        sys.exit("Uso: voz-teste ROTEIRO.json [PASTA_SAIDA] [--voz NOME] [--taxa N]")
    roteiro = os.path.abspath(args[0])
    resto = [a for a in args[1:] if not a.startswith("--")]
    opts = {a: args[args.index(a) + 1] for a in ("--voz", "--taxa") if a in args}
    resto = [a for a in resto if a not in opts.values()]
    saida = os.path.abspath(resto[0]) if resto else os.path.join(os.getcwd(), "roteiros", "voz-" + os.path.splitext(os.path.basename(roteiro))[0], "teste")
    kit = os.path.join(os.getcwd(), "kit3d")
    if not os.path.isdir(kit):
        kit = os.path.join(PLUGIN, "kit3d")
    cmd = [sys.executable, os.path.join(kit, "voz.py"), roteiro, saida, "--voz", opts.get("--voz", "Luciana"), "--taxa", opts.get("--taxa", "185")]
    subprocess.run(cmd, check=True)
    subprocess.run([sys.executable, os.path.join(kit, "palavras.py"), saida], check=True)
    print("voz de teste em", saida, "(narracao.wav, tempos.json, palavras.json)")


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a or a[0] in ("-h", "--help"):
        sys.exit(__doc__)
    cmd, resto = a[0], a[1:]
    pos = [x for x in resto if not x.startswith("--")]
    if cmd == "iniciar":
        iniciar(pos[0] if pos else ".", "--atualizar" in resto)
    elif cmd == "doctor":
        sys.exit(doctor(pos[0] if pos else "."))
    elif cmd == "exemplo":
        sys.exit(exemplo(pos[0] if pos else "."))
    elif cmd == "voz-teste":
        voz_teste(resto)
    else:
        sys.exit(__doc__)
