"""Efeito Fuji (filme) de "O abrigo", a pós do fim da fila (pedido de 24/10/2026): olhar de negativo de cinema colorido (Fujifilm Eterna):
pretos levantados e esverdeados, sombras frias, realces quentes e macios, cor um pouco mais fosca, halação avermelhada nos pontos de luz,
grão fino que muda a cada quadro, vinheta leve. Tudo no ffmpeg (sem Blender, sem crédito).
python3 pos_fuji.py ENTRADA.mp4 SAIDA.mp4 [--forca 1.0] [--so-quadro T SAIDA.png]     (forca 0 a 1,5; --so-quadro tira só um quadro para ver o efeito)"""
import sys, subprocess


def grafo(f=1.0):
    lift = 0.022 * f
    return (
        # 1) curva de filme: pretos levantados (verde-azulado), meios-tons quentes, realces que não estouram (tudo em RGB)
        f"[0:v]format=gbrp,curves=r='0/{lift:.3f} 0.25/0.24 0.5/0.505 0.8/0.81 1/0.975':g='0/{lift * 1.5:.3f} 0.25/0.26 0.5/0.515 0.8/0.80 1/0.985':b='0/{lift * 2.2:.3f} 0.25/0.27 0.5/0.5 0.8/0.77 1/0.95',"
        f"eq=contrast={1 - 0.05 * f:.3f}:saturation={1 - 0.09 * f:.3f}:gamma=1.015,"
        f"colorbalance=rs={-0.035 * f:.3f}:gs={0.02 * f:.3f}:bs={0.05 * f:.3f}:rm={0.03 * f:.3f}:bm={-0.025 * f:.3f}:rh={0.05 * f:.3f}:gh={0.01 * f:.3f}:bh={-0.05 * f:.3f},"
        f"split=2[base][lum];"
        # 2) halação: os pontos claros vazam um brilho laranja-avermelhado (a mistura é em RGB, 'screen')
        f"[lum]format=gray,lutyuv=y='clip((val-190)*4.2,0,255)',gblur=sigma={9 * f + 1:.1f},format=gbrp,colorchannelmixer=rr=1.0:gg=0.36:bb=0.1[hal];"
        f"[base][hal]blend=all_mode=screen:all_opacity={0.32 * f:.3f},"
        # 3) grão fino que muda a cada quadro e vinheta leve
        f"noise=alls={int(6 * f + 1)}:allf=t+u,vignette=angle=PI/{6 - 0.8 * min(f, 1.5):.2f}:mode=forward,"
        f"format=yuv420p"
    )


def main():
    a = sys.argv[1:]
    entrada, saida = a[0], a[1]
    f = float(a[a.index("--forca") + 1]) if "--forca" in a else 1.0
    if "--so-quadro" in a:
        i = a.index("--so-quadro"); t, png = a[i + 1], a[i + 2]
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", t, "-i", entrada, "-frames:v", "1", "-filter_complex", grafo(f).replace("format=yuv420p", "format=rgb24"), png], check=True)
        print("ok", png); return
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", entrada, "-filter_complex", grafo(f), "-r", "24", "-c:v", "libx264", "-preset", "slow", "-b:v", "11M", "-maxrate", "14M",
                    "-bufsize", "22M", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "256k", saida], check=True)
    print("ok", saida)


if __name__ == "__main__":
    main()
