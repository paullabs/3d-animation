"""Junta os quadros PNG + a voz de cada linha num mp4 final. Uso: python3 mux.py render out.mp4"""
import json, subprocess, sys
d, out = sys.argv[1], sys.argv[2]
T = json.load(open("timing.json")); fps = T["fps"]
cmd = ["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(fps), "-i", f"{d}/f_%04d.png"]
for s in T["shots"]:
    cmd += ["-i", s["audio"]]
fl = []
for k, s in enumerate(T["shots"], 1):
    ms = int(s["start"] * 1000)
    fl.append(f"[{k}:a]aresample=44100,adelay={ms}|{ms}[a{k}]")
fl.append("".join(f"[a{k}]" for k in range(1, len(T["shots"]) + 1)) + f"amix=inputs={len(T['shots'])}:normalize=0,volume=1.6[aout]")
cmd += ["-filter_complex", ";".join(fl), "-map", "0:v", "-map", "[aout]", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "17",
        "-c:a", "aac", "-b:a", "192k", "-t", f"{T['total_s']:.2f}", out]
subprocess.run(cmd, check=True)
print("ok", out)
