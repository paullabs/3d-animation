"""Junta as células renderizadas em páginas. python3 ficha_montar.py DIR_DAS_CELULAS DIR_SAIDA"""
import subprocess, sys, os, glob
src, dst = sys.argv[1], sys.argv[2]
os.makedirs(dst, exist_ok=True)
BG = "0x221c30"
def run(*a):
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", *a], check=True)
def grid(files, cols, rows, out):
    w, h = map(int, subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "stream=width,height", "-of", "csv=p=0", files[0]]).decode().strip().split(","))
    files = list(files)
    while len(files) < cols * rows:
        blank = out + f".blank{len(files)}.png"
        run("-i", files[0], "-vf", f"drawbox=x=0:y=0:w=iw:h=ih:color={BG}:t=fill", "-frames:v", "1", blank); files.append(blank)
    lst = out + ".txt"
    with open(lst, "w") as f:
        for p in files:
            f.write(f"file '{os.path.abspath(p)}'\n")
    run("-f", "concat", "-safe", "0", "-i", lst, "-vf", f"tile={cols}x{rows}:padding=16:margin=32:color={BG}", "-frames:v", "1", out)
    os.remove(lst)
    for p in files:
        if ".blank" in p:
            os.remove(p)
    return out
def stack(parts, out):
    ins = []
    for p in parts:
        ins += ["-i", p]
    W = max(int(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "stream=width", "-of", "csv=p=0", p]).decode()) for p in parts)
    fl = ";".join(f"[{i}]pad={W}:ih:(ow-iw)/2:0:color={BG}[p{i}]" for i in range(len(parts)))
    fl += ";" + "".join(f"[p{i}]" for i in range(len(parts))) + f"vstack=inputs={len(parts)}"
    run(*ins, "-filter_complex", fl, "-frames:v", "1", out)
pages = {"giro": [("", 5, 1)], "expressoes": [("", 6, 4)], "expressoes2": [("", 6, 2)], "poses": [("", 6, 2)],
         "detalhes": [("boca_", 7, 2), ("olho_", 5, 3), ("sobr_", 6, 1)]}
order = ["giro", "expressoes", "poses", "detalhes", "expressoes2"]
for n, (page) in enumerate(order):
    d = os.path.join(src, page)
    if not os.path.isdir(d):
        continue
    parts = [os.path.join(d, "zz_header.png")]
    for pref, c, r in pages[page]:
        fs = sorted(f for f in glob.glob(os.path.join(d, "[0-9]*.png")) if (pref in os.path.basename(f)))
        parts.append(grid(fs, c, r, os.path.join(d, f"_grid_{pref or 'all'}.png")))
    out = os.path.join(dst, f"ficha-{n + 1:02d}-{page}.png")
    stack(parts, out)
    print(out)
