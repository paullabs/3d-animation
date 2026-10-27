#!/usr/bin/env python3
"""Atualiza o plugin a partir da pasta de trabalho do Canal 38 (o autor roda isto depois de evoluir o kit).
Uso: python3 tools/sincronizar_do_projeto.py "/caminho/do/projeto" [--skills ~/.claude/skills]

O que faz:
- kit3d/: copia o código do projeto sem backups (_antes_, _vN, _backup), testes soltos, renders e logs; mantém o que
  os scripts mantidos importam, mesmo que o nome pareça backup;
- troca os caminhos fixos do Mac do autor por canal38_env (RAIZ e BLENDER);
- gera kit3d/INDICE.md (uma linha por módulo, tirada do docstring);
- skills: copia historias-5-niveis e animacao-3d-cinema da pasta de skills e troca os caminhos pessoais;
- regras: copia a memória de regras (feedback, estilo, pipeline) para a skill regras-do-estilo;
- exemplos: roteiros prontos de vídeos já feitos (só o formato, sem áudio nem imagem).
Depois: claude plugin validate plugins/3d-animation"""
import ast, os, re, shutil, sys, textwrap

AQUI = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(AQUI)
PLUGIN = os.path.join(REPO, "plugins", "3d-animation")

# arquivos que NÃO entram (a não ser que um script mantido os importe)
EXCLUI = re.compile(r"(_antes_|backup|_v\d+[a-z]?(_|\.py$)|_test\.py$|^test_|^debug|_debug\.py$|_demo\.py$|\.log$|^rtest|\.pyc$)")
# roteiros e dados de tempo dos vídeos já feitos: os módulos do kit leem isto na hora de importar
EXEMPLOS = ["pcc.json", "pcc2.json", "pcc3.json", "pcc4.json", "pcc5.json", "presidente.json", "reflexo.json", "abrigo.json",
            "abrigo2.json", "abrigo2_planos.json", "passos-dobrando.json", "transito-ep1.json",
            "decupagem-pcc.md", "decupagem-presidente.md"]
RE_TEMPOS = re.compile(r"^(tempos|palavras)[a-z_]*\.json$")

RE_RAIZ = re.compile(r"""(["'])/Users/paul/Downloads/Canal/38 - 3D ANIMATION(/[^"']*)?\1""")
RE_BLENDER = re.compile(r'"/Applications/Blender\.app/Contents/MacOS/Blender"')
RE_PY = re.compile(r"\b([A-Za-z0-9_]+)\.py\b")


def troca_raiz(m):
    q, suf = m.group(1), m.group(2)
    if suf:
        return f'(__import__("canal38_env").RAIZ + {q}{suf}{q})'
    return '__import__("canal38_env").RAIZ'


# ajustes de portabilidade que o projeto original não precisa (cada um falha alto se o trecho mudar)
AJUSTES = {
    "palavras.py": [(
        '            ww = whisper_words(f["arquivo"], tmp)\n',
        '            try:\n'
        '                ww = whisper_words(f["arquivo"], tmp)\n'
        '            except (OSError, subprocess.CalledProcessError, KeyError):\n'
        '                ww = []        # sem mlx_whisper: a palavra é distribuída pelo tamanho dentro da fala\n')],
}


def ajusta(nome, texto):
    for velho, novo in AJUSTES.get(nome, []):
        if velho not in texto:
            sys.exit(f"ajuste não casa em {nome}: o original mudou; atualize AJUSTES em tools/sincronizar_do_projeto.py")
        texto = texto.replace(velho, novo)
    return texto


def reescreve_py(texto):
    texto = RE_RAIZ.sub(troca_raiz, texto)
    texto = RE_BLENDER.sub('__import__("canal38_env").BLENDER', texto)
    texto = texto.replace('os.path.expanduser("~/.claude/skills/historias-5-niveis/scripts")',
                          'os.path.join(__import__("canal38_env").RAIZ, "ferramentas")')
    texto = texto.replace("~/.claude/skills/historias-5-niveis/scripts/", "ferramentas/")
    return texto


def reescreve_sh(texto):
    texto = re.sub(r'cd "/Users/paul/Downloads/Canal/38 - 3D ANIMATION"', 'cd "$(cd "$(dirname "$0")/.." && pwd)"', texto)
    return texto


def dependencias(caminho, existentes):
    """nomes de módulos locais que o arquivo importa ou cita como .py"""
    texto = open(caminho, encoding="utf-8", errors="replace").read()
    achados = set()
    if caminho.endswith(".py"):
        try:
            arv = ast.parse(texto)
            for no in ast.walk(arv):
                if isinstance(no, ast.Import):
                    achados.update(a.name.split(".")[0] for a in no.names)
                elif isinstance(no, ast.ImportFrom) and no.module:
                    achados.add(no.module.split(".")[0])
                elif isinstance(no, ast.Constant) and isinstance(no.value, str):
                    achados.update(m.group(1) for m in RE_PY.finditer(no.value))
                elif isinstance(no, ast.Call) and no.args and isinstance(no.args[0], ast.Constant) and isinstance(no.args[0].value, str):
                    f = no.func
                    nome = f.attr if isinstance(f, ast.Attribute) else getattr(f, "id", "")
                    if nome in ("import_module", "__import__"):
                        achados.add(no.args[0].value.split(".")[0])
        except SyntaxError:
            pass
    achados.update(m.group(1) for m in RE_PY.finditer(texto))
    return {a for a in achados if a + ".py" in existentes}


def sincroniza_kit(origem):
    src = os.path.join(origem, "kit3d")
    dst = os.path.join(PLUGIN, "kit3d")
    todos = sorted(f for f in os.listdir(src) if os.path.isfile(os.path.join(src, f)) and f.endswith((".py", ".sh", ".json")))
    existentes = set(todos)
    manter = {f for f in todos if not EXCLUI.search(f)}
    fila = list(manter)
    trazidos = set()
    while fila:
        f = fila.pop()
        for d in dependencias(os.path.join(src, f), existentes):
            if d + ".py" not in manter:
                manter.add(d + ".py"); trazidos.add(d + ".py"); fila.append(d + ".py")
    shutil.rmtree(dst, ignore_errors=True)
    os.makedirs(dst)
    for f in sorted(manter):
        texto = open(os.path.join(src, f), encoding="utf-8", errors="replace").read()
        if f.endswith(".py"):
            texto = ajusta(f, reescreve_py(texto))
        elif f.endswith(".sh"):
            texto = reescreve_sh(texto)
        with open(os.path.join(dst, f), "w", encoding="utf-8") as o:
            o.write(texto)
        if f.endswith((".py", ".sh")):
            os.chmod(os.path.join(dst, f), 0o755 if f.endswith(".sh") else 0o644)
    shutil.copy(os.path.join(AQUI, "canal38_env.py"), os.path.join(dst, "canal38_env.py"))
    fora = sorted(set(todos) - manter)
    print(f"kit3d: {len(manter)} arquivos ({len(trazidos)} puxados por importação: {', '.join(sorted(trazidos)) or '-'})")
    print(f"       {len(fora)} ficaram de fora")
    gera_indice(dst)
    return fora


def gera_indice(dst):
    linhas = ["# Índice do kit3d", "",
              "Uma linha por arquivo, tirada do docstring. Gerado por `tools/sincronizar_do_projeto.py`; não edite à mão.", "",
              "| arquivo | o que faz |", "|---|---|"]
    for f in sorted(os.listdir(dst)):
        if not f.endswith(".py") or f == "canal38_env.py":
            continue
        try:
            doc = ast.get_docstring(ast.parse(open(os.path.join(dst, f), encoding="utf-8").read())) or ""
        except SyntaxError:
            doc = ""
        primeira = " ".join(doc.strip().splitlines()[0:1]).replace("|", "/")[:170] if doc.strip() else "(sem descrição)"
        linhas.append(f"| `{f}` | {primeira} |")
    linhas.append("| `canal38_env.py` | caminhos do projeto e do Blender (variáveis `CANAL38_PROJETO` e `CANAL38_BLENDER`) |")
    open(os.path.join(dst, "INDICE.md"), "w", encoding="utf-8").write("\n".join(linhas) + "\n")


def troca_texto(t):
    t = t.replace("/Users/paul/Downloads/Canal/38 - 3D ANIMATION", "<pasta-do-projeto>")
    t = t.replace("~/.claude/skills/historias-5-niveis/scripts/", "ferramentas/")
    t = t.replace("~/.claude/skills/historias-5-niveis", "a skill historias-5-niveis")
    return t


def sincroniza_skills(pasta_skills):
    for nome in ("historias-5-niveis", "animacao-3d-cinema"):
        src = os.path.join(pasta_skills, nome)
        dst = os.path.join(PLUGIN, "skills", nome)
        shutil.rmtree(dst, ignore_errors=True)
        for raiz, _, arqs in os.walk(src):
            for a in arqs:
                if re.search(r"(_antes_|_v\d+\.py$|\.pyc$|\.DS_Store)", a):
                    continue
                p = os.path.join(raiz, a)
                rel = os.path.relpath(p, src)
                alvo = os.path.join(dst, rel)
                os.makedirs(os.path.dirname(alvo), exist_ok=True)
                if a.endswith((".md", ".py", ".json")):
                    open(alvo, "w", encoding="utf-8").write(troca_texto(open(p, encoding="utf-8").read()))
                else:
                    shutil.copy(p, alvo)
        print("skill", nome, "ok")
    # ferramentas que o iniciar põe em <projeto>/ferramentas
    fer = os.path.join(PLUGIN, "ferramentas")
    shutil.rmtree(fer, ignore_errors=True)
    os.makedirs(fer)
    for a in ("mixagem.py", "sfx.py"):
        p = os.path.join(pasta_skills, "historias-5-niveis", "scripts", a)
        open(os.path.join(fer, a), "w", encoding="utf-8").write(troca_texto(open(p, encoding="utf-8").read()))


def sincroniza_regras(origem):
    mem = os.path.join(origem, "_contexto", "memoria")
    dst = os.path.join(PLUGIN, "skills", "regras-do-estilo", "references")
    shutil.rmtree(dst, ignore_errors=True)
    os.makedirs(dst)
    linhas = ["# Índice das regras do canal", ""]
    for f in sorted(os.listdir(mem)):
        if not f.endswith(".md") or not re.match(r"(feedback-|estilo-|pipeline-)", f):
            continue
        texto = open(os.path.join(mem, f), encoding="utf-8").read()
        open(os.path.join(dst, f), "w", encoding="utf-8").write(troca_texto(texto))
        m = re.search(r"^description:\s*(.+)$", texto, re.M)
        linhas.append(f"- [{f[:-3]}]({f}): {m.group(1).strip().strip(chr(34)) if m else ''}")
    open(os.path.join(dst, "INDICE.md"), "w", encoding="utf-8").write("\n".join(linhas) + "\n")
    print("regras:", len(linhas) - 2, "arquivos")


def copia_limpa(src, dst):
    """copia um dado de exemplo sem o caminho absoluto do Mac do autor (fica relativo à pasta do projeto)"""
    t = open(src, encoding="utf-8").read().replace("/Users/paul/Downloads/Canal/38 - 3D ANIMATION/", "")
    open(dst, "w", encoding="utf-8").write(t)


def sincroniza_exemplos(origem):
    dst = os.path.join(PLUGIN, "exemplos", "roteiros")
    shutil.rmtree(dst, ignore_errors=True)
    os.makedirs(dst)
    for f in EXEMPLOS:
        p = os.path.join(origem, "roteiros", f)
        if os.path.exists(p):
            copia_limpa(p, os.path.join(dst, f))
    n = 0
    base = os.path.join(origem, "roteiros")
    for pasta in sorted(os.listdir(base)):
        if not pasta.startswith("voz-") or not os.path.isdir(os.path.join(base, pasta)):
            continue
        for raiz, dirs, arqs in os.walk(os.path.join(base, pasta)):
            rel = os.path.relpath(raiz, base)
            if rel.count(os.sep) > 1 or ("teste" in rel.split(os.sep) and pasta != "voz-abrigo2"):
                continue
            for a in arqs:
                if RE_TEMPOS.match(a) and os.path.getsize(os.path.join(raiz, a)) < 400_000:
                    os.makedirs(os.path.join(dst, rel), exist_ok=True)
                    copia_limpa(os.path.join(raiz, a), os.path.join(dst, rel, a)); n += 1
    osm = os.path.join(origem, "transito", "dados_osm", "estaiada.json")      # mapa de São Paulo (OpenStreetMap, ODbL)
    if os.path.exists(osm):
        d = os.path.join(PLUGIN, "exemplos", "transito", "dados_osm")
        shutil.rmtree(os.path.join(PLUGIN, "exemplos", "transito"), ignore_errors=True)
        os.makedirs(d)
        shutil.copy(osm, d)
    print("exemplos:", len(EXEMPLOS), "roteiros,", n, "arquivos de tempo de voz e o mapa do trânsito")


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a:
        sys.exit(__doc__)
    origem = os.path.abspath(os.path.expanduser(a[0]))
    skills = os.path.expanduser(a[a.index("--skills") + 1]) if "--skills" in a else os.path.expanduser("~/.claude/skills")
    fora = sincroniza_kit(origem)
    sincroniza_skills(skills)
    sincroniza_regras(origem)
    sincroniza_exemplos(origem)
    open(os.path.join(REPO, "tools", "ficaram_de_fora.txt"), "w").write("\n".join(fora) + "\n")
    print("pronto. Lista do que ficou de fora: tools/ficaram_de_fora.txt")
