"""Teste de animação do Sem-Osso (26/10/2026: "melhorar a animação do monstro para não ficar duro e sem graça").
O Sem-Osso sobe de uma poça esticando (alongado e fino), assenta com um balanço, e depois vem aos trancos para a câmera: pulso de velocidade (arrasta, desliza, para),
tronco que estica e achata (squash e stretch), braços e pernas MOLES que dobram (SimpleDeform animado), cabeça que atrasa e passa do ponto (molas do Heroi3D.anima),
base de gosma que alonga atrás, gotas que pulsam e a respiração. Câmera baixa com dolly-in lento e tremor de mão.
blender -b -P anim_semosso_teste.py -- PASTA [--scale 0.5] [--samples 10] [--quadros 1,120] [--n 120]      depois: ffmpeg (ver anim_semosso_rodar.sh)"""
import os, sys, math, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy, lib
from lib import *
from mathutils import Vector
import cena, props
import story3_abrigo as S3
import story_abrigo2 as SB
import objetos3d_abrigo2 as O2, objetos3d_abrigo as O3, ambiente_noite as AN, story_abrigo as SA

a = sys.argv[sys.argv.index("--") + 1:]
OUT = a[0]; os.makedirs(OUT, exist_ok=True)
opt = lambda n, d: a[a.index(n) + 1] if n in a else d
ESC, SMP, N = float(opt("--scale", "0.5")), int(opt("--samples", "10")), int(opt("--n", "120"))
q0, q1 = [int(x) for x in opt("--quadros", f"1,{N}").split(",")]


def suave(u):
    u = max(0.0, min(1.0, u)); return u * u * (3 - 2 * u)


def costas(u):
    """easeOutBack: passa do ponto e assenta"""
    c1 = 1.70158; c3 = c1 + 1; u = max(0.0, min(1.0, u))
    return 1 + c3 * (u - 1) ** 3 + c1 * (u - 1) ** 2


lib.reset(int(1080 * ESC), int(1920 * ESC), 24, SMP)
sc = bpy.context.scene; sc.frame_start, sc.frame_end = 1, N

# --- cenário: noite com poste (luz âmbar atrás), poça, névoa, partículas
SB.noite_rica()
AN.poste("pt", 1.8, 9.5, acesa=True, rot=180)
AN.carro("cc", -3.5, 8.0, rot=70, queimado=True); AN.lixeira("lx", 2.8, 5.0); AN.caixote("cx", -2.2, 4.5, 20, 2); AN.papeis("pp", 0, 5.5, 3.5, 12)
O3.halo_cam("contraluz", (0.6, 9.8, 2.2), 3.6, "#f2e2b0", 0.4)
AN.poca_agua("pq", 0.0, 6.0, 1.7, 1.0, brilho=("#ffcf7a", 0.35), seed=3)
poca = O2.poca("poca", 0.0, 6.0, 0.7, 0.5, seed=3)

# --- o Sem-Osso (de frente para a câmera, que fica em y menor)
h = O2.sem_osso("sm", "padeira", (0.0, 6.0, 0.0), rot=0.0, curva=1.0, seed=2)
membros = {}
for nome in ("sm_bracomoleF", "sm_bracomoleB", "sm_pernamoleF", "sm_pernamoleB"):
    o = bpy.data.objects[nome]
    sub = o.modifiers.new("sub", "SUBSURF"); sub.levels = 1; sub.render_levels = 2
    d = o.modifiers.new("dobra", "SIMPLE_DEFORM"); d.deform_method = "BEND"; d.deform_axis = "Z"; d.angle = 0.0
    mods = [m for m in o.modifiers]
    o.modifiers.move(mods.index(sub), 0); o.modifiers.move([m for m in o.modifiers].index(d), 1)
    membros[nome] = d
base = bpy.data.objects["sm_base"]
gotas = [bpy.data.objects.get(n) for n in ("sm_pingoF", "sm_pingoB", "sm_queixo_gota", "sm_queixo")]
gotas = [g for g in gotas if g]

# --- chaves de pose (a cada 4 quadros) e o motor de molas do Heroi3D
F_SOBE = 36
P = 40.0                                                         # período do passo (quadros)
rnd = random.Random(5)
chaves = []
x = 0.0; y = 6.0
for f in range(1, N + 1, 3):
    t = f
    if f <= F_SOBE:
        u = f / F_SOBE
        z = -1.05 + 1.05 * costas(u)
        pose = dict(pos=(0.0, 6.0, z), rot=0.0, tronco=26 - 18 * suave(u) + 10 * (1 - suave(u)), cabeca=-18 * u, alt=0.77 - 0.06 * math.sin(math.pi * u),
                    ombro=(-8 - 20 * u, -8 - 20 * u), cotovelo=(-10, -10), abre=(8 * u, 8 * u), quadril=(0, 0), joelho=(6, 6))
    else:
        ph = ((f - F_SOBE) / P)
        s = math.sin(2 * math.pi * ph)
        v = max(0.0, s) ** 1.4                                    # pulso: só avança na metade do ciclo (arrasta, desliza, para)
        y -= 0.115 * v * (3.0 / 24.0) * 12.0 * 0.9
        x = 0.35 * math.sin(2 * math.pi * ph / 2.0)
        pose = dict(pos=(x, y, 0.0), rot=-8 * s, tronco=22 + 14 * v, cabeca=-12 + 16 * math.sin(2 * math.pi * (ph - 0.22)), alt=0.77 - 0.05 * abs(s),
                    ombro=(-14 + 30 * math.sin(2 * math.pi * (ph - 0.1)), -14 - 30 * math.sin(2 * math.pi * (ph - 0.1))), cotovelo=(-16, -22),
                    abre=(10 + 6 * s, 10 - 6 * s), quadril=(-26 * s, 26 * s), joelho=(10 + 40 * max(0, s), 10 + 40 * max(0, -s)), olha=10 * math.sin(2 * math.pi * (ph - 0.3)))
    chaves.append((f, pose))
h.anima(chaves, 1, N, vida=1.6, seed=7, mola=True, molas=dict(cabeca=(3, 2.4, 0.42), tronco=(2, 2.6, 0.5), ombro=(3, 3.2, 0.45), cotovelo=(4, 3.6, 0.4), pos=(1, 2.4, 0.75), quadril=(2, 3.0, 0.55)))

# --- o que o motor não cobre: esticar e achatar, braços e pernas que dobram, base, gotas, poça
for f in range(1, N + 1):
    if f <= F_SOBE:
        u = f / F_SOBE
        sz = 1.0 + 0.32 * math.sin(math.pi * min(1, u * 1.1)) * (1 - 0.4 * u) + (0.07 * math.sin(10 * u * math.pi) * (1 - u) if u > 0.6 else 0)
        dob = [70 * (1 - u) * math.sin(6 * u), -70 * (1 - u) * math.sin(5 * u + 1), 40 * (1 - u), -40 * (1 - u)]
        pulso = 0.0
    else:
        ph = ((f - F_SOBE) / P); s = math.sin(2 * math.pi * ph); v = max(0.0, s) ** 1.4
        sz = 1.0 + 0.09 * math.sin(2 * math.pi * (ph + 0.2)) + 0.03 * math.sin(2 * math.pi * ph * 3)
        dob = [32 * math.sin(2 * math.pi * (ph - 0.25)) + 8, -32 * math.sin(2 * math.pi * (ph - 0.25)) - 8, 28 * math.sin(2 * math.pi * (ph - 0.05)), -34 * math.sin(2 * math.pi * (ph - 0.05)) + 10]
        pulso = v
    sx = 1.0 / math.sqrt(sz)
    h.raiz.scale = (sx, sx, sz); h.raiz.keyframe_insert("scale", frame=f)
    for d, ang in zip(membros.values(), dob):
        d.angle = math.radians(ang); d.keyframe_insert("angle", frame=f)
    base.scale = (1.0 + 0.25 * pulso, 1.0 + 0.55 * pulso, 1.0); base.keyframe_insert("scale", frame=f)
    for k, g in enumerate(gotas):
        g.scale = (1, 1, 1.0 + 0.5 * math.sin(f / 5.0 + k * 2.0) * 0.5 + 0.2 * pulso); g.keyframe_insert("scale", frame=f)
    k0 = 1.0 + 0.5 * (1 - min(1, f / F_SOBE)) if f <= F_SOBE else 1.0 + 0.04 * math.sin(f / 7.0)
    poca.scale = (k0, k0, 1.0); poca.keyframe_insert("scale", frame=f)

# --- câmera: baixa, dolly-in lento e tremor de mão
cam = S3.cam((0.2, 1.2, 0.85), (0.0, 6.0, 1.15), 35, fstop=5.6, foco=(0.0, 5.0, 1.1))
rn = random.Random(3)
for f in range(1, N + 1):
    u = (f - 1) / (N - 1)
    cam.location = (0.2 + 0.25 * u + 0.012 * math.sin(f / 3.1), 1.2 + 1.6 * u * u + 0.01 * math.sin(f / 2.3), 0.85 + 0.25 * u + 0.012 * math.sin(f / 2.7))
    cam.keyframe_insert("location", frame=f)
    tgt = Vector((0.0, 6.0 + (y if f > F_SOBE else 6.0) * 0.0, 1.15 - 0.15 * u))
    d = (tgt - Vector(cam.location)); e = d.to_track_quat("-Z", "Y").to_euler()
    cam.rotation_euler = (e.x + 0.004 * math.sin(f / 3.7), e.y, e.z + 0.004 * math.sin(f / 4.3)); cam.keyframe_insert("rotation_euler", frame=f)

for f in range(q0, q1 + 1):
    sc.frame_set(f)
    sc.render.filepath = f"{OUT}/f{f:04d}.png"
    bpy.ops.render.render(write_still=True)
