"""Gera a voz de cada linha (macOS say), mede a duração e escreve timing.json.
A duração de cada plano = duração da fala + pad. Uso: python3 make_voice.py cartel_script.json"""
import json, subprocess, sys, os
src = sys.argv[1]
cfg = json.load(open(src))
fps, pad = cfg["fps"], cfg["pad_s"]
os.makedirs("audio", exist_ok=True)
t = 0.0; shots = []
for i, line in enumerate(cfg["lines"], 1):
    aiff = f"audio/l{i:02d}.aiff"
    subprocess.run(["say", "-v", cfg["voice"], "-r", str(cfg["rate"]), "-o", aiff, line], check=True)
    d = float(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",aiff]).decode())
    dur = d + pad
    f0 = round(t*fps)+1; t += dur; f1 = round(t*fps)
    shots.append({"i": i, "text": line, "voice_s": round(d,3), "start": t-dur, "dur": dur, "f0": f0, "f1": f1, "audio": aiff})
json.dump({"fps": fps, "total_s": t, "total_frames": shots[-1]["f1"], "shots": shots}, open("timing.json","w"), ensure_ascii=False, indent=1)
print(f"total {t:.1f}s, {shots[-1]['f1']} frames")
for s in shots: print(s["i"], s["f0"], s["f1"], f"{s['dur']:.2f}s", s["text"])
