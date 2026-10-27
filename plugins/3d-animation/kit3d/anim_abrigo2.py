"""Animação da parte 2 de "O abrigo" (26/10/2026) por cima do storyboard (story_abrigo2.py): cada plano é montado duas vezes, no estado de início (FIM=False)
e no de fim (FIM=True), e o que mudou (câmera, lente, foco, bonecos, objetos) é interpolado quadro a quadro com uma curva suave (mistura de linear e smoothstep,
para a câmera nunca parar); a câmera ganha um tremor de mão bem leve. Objetos cuja malha muda (gosma, poças) ficam no estado de início.
blender -b -P anim_abrigo2.py -- PLANO PASTA [--scale 0.5] [--samples 10] [--n N] [--f0 a --f1 b]      (grava PASTA/<PLANO>/0001.png ...)"""
import os, sys, math, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy, lib
from mathutils import Vector, Euler
import story_abrigo2 as S

RAIZ = S.RAIZ


def snap():
    d = {}
    for o in bpy.data.objects:
        d[o.name] = (tuple(o.location), tuple(o.rotation_euler), tuple(o.scale), o.hide_render)
    cam = bpy.context.scene.camera
    c = dict(nome=cam.name, loc=tuple(cam.location), rot=tuple(cam.rotation_euler), lens=cam.data.lens,
             foco=cam.data.dof.focus_distance, f=cam.data.dof.aperture_fstop)
    return d, c


def constroi(plano, fim, k, smp):
    lib.reset(int(1080 * k), int(1920 * k), 24, smp)
    sc = bpy.context.scene; sc.frame_start, sc.frame_end = 1, 24
    S.FIM = fim
    S.BUILD[plano]()
    bpy.context.view_layer.update()


def unwrap(a, b):
    return tuple(y + 2 * math.pi * round((x - y) / (2 * math.pi)) for x, y in zip(a, b))


REVELA = {"1D", "1E", "1F", "1F2", "1G", "1H", "2A", "3C", "3C2", "4B", "11D", "11E"}


def curva(u):
    s = u * u * (3 - 2 * u)
    return 0.5 * u + 0.5 * s


def main():
    a = sys.argv[sys.argv.index("--") + 1:]
    plano, pasta = a[0], a[1]
    opt = lambda n, d: a[a.index(n) + 1] if n in a else d
    k = float(opt("--scale", "0.5")); smp = int(opt("--samples", "10"))
    meta = json.load(open(f"{RAIZ}/roteiros/abrigo2_planos.json"))["planos"][plano]
    N = int(opt("--n", max(2, round(meta["t1"] * 24) - round(meta["t0"] * 24))))
    f0, f1 = int(opt("--f0", 1)), int(opt("--f1", N))
    import acoes_abrigo2 as AC                                                   # v3: planos com animação de verdade (acoes_abrigo2.py) não usam a interpolação início-fim
    if plano in AC.ACAO and "--generico" not in a:
        lib.reset(int(1080 * k), int(1920 * k), 24, smp)
        sc = bpy.context.scene; sc.frame_start, sc.frame_end = 1, N
        S.FIM = False
        AC.ACAO[plano](N)
        sc.render.use_motion_blur = True; sc.render.motion_blur_shutter = 0.5
        qs = [int(x) for x in opt("--quadros", "").split(",") if x] or list(range(f0, f1 + 1))
        os.makedirs(f"{pasta}/{plano}", exist_ok=True)
        for f in qs:
            sc.frame_set(min(N, max(1, f)))
            sc.render.filepath = f"{pasta}/{plano}/{f:04d}.png"
            bpy.ops.render.render(write_still=True)
        return
    mov = plano in S.MOV
    fim_d = fim_c = None
    dump = opt("--dump", None)
    if dump:                                                                     # processo só para o estado de fim (o kit guarda materiais: uma cena por processo)
        constroi(plano, True, k, smp); d, c = snap()
        json.dump(dict(d=d, c=c), open(dump, "w")); return
    if mov:
        import subprocess, tempfile
        tmp = tempfile.mktemp(suffix=".json")
        subprocess.run([__import__("canal38_env").BLENDER, "-b", "-P", os.path.abspath(__file__), "--", plano, pasta, "--dump", tmp, "--scale", str(k), "--samples", str(smp)],
                       capture_output=True)
        J = json.load(open(tmp)); os.remove(tmp)
        fim_d = {n: (tuple(v[0]), tuple(v[1]), tuple(v[2]), v[3]) for n, v in J["d"].items()}; fim_c = J["c"]
    constroi(plano, False, k, smp)
    ini_d, ini_c = snap()
    sc = bpy.context.scene; sc.frame_start, sc.frame_end = 1, N
    cam = sc.camera
    mudam = []
    if mov:
        for nome, (loc, rot, esc, hid) in ini_d.items():
            o = bpy.data.objects.get(nome)
            if o is None or nome == cam.name or nome not in fim_d:
                continue
            l2, r2, e2, h2 = fim_d[nome]
            if max(abs(x - y) for x, y in zip(loc, l2)) > 1e-4 or max(abs(x - y) for x, y in zip(rot, r2)) > 1e-4 or max(abs(x - y) for x, y in zip(esc, e2)) > 1e-4:
                mudam.append((o, loc, rot, esc, l2, unwrap(r2, rot), e2))
    import random
    rnd = random.Random(sum(map(ord, plano)))
    ph = [rnd.uniform(0, 6.28) for _ in range(6)]
    dist = max(0.3, (Vector(ini_c["loc"]) - Vector(cam.matrix_world.to_quaternion() @ Vector((0, 0, -1)) * ini_c["foco"] + Vector(ini_c["loc"]))).length)
    amp = 0.0015 * max(1.0, min(6.0, ini_c["foco"]))
    fator = 1.0                                                                  # limite de velocidade da câmera: o zoom e o giro não podem ser rápidos (o susto do monstro vai ainda mais devagar)
    if mov:
        dur = N / 24.0
        c1, c2 = ini_c, fim_c
        path = (Vector(c1["loc"]) - Vector(c2["loc"])).length + sum(abs(x - y) for x, y in zip(c1["rot"], unwrap(c2["rot"], c1["rot"]))) * max(1.0, c1["foco"]) * 0.6 \
            + abs(math.log(c2["lens"] / c1["lens"])) * 2.0
        vmax = 0.4 if plano in REVELA else 1.3
        fator = min(1.0, vmax * dur / max(path, 1e-6))
    vida = []                                                                    # respiração e balanço de cabeça de todo boneco (cada um com a sua fase)
    for o in bpy.data.objects:
        if o.name.endswith("_tronco") or o.name.endswith("_cabeca"):
            vida.append((o, tuple(o.rotation_euler), rnd.uniform(0, 6.28), rnd.uniform(0, 6.28)))
    for f in range(1, N + 1):
        u = curva((f - 1) / (N - 1)) if mov else 0.0
        for o, l1, r1, e1, l2, r2, e2 in mudam:
            o.location = tuple(x + (y - x) * u for x, y in zip(l1, l2))
            o.rotation_euler = tuple(x + (y - x) * u for x, y in zip(r1, r2))
            o.scale = tuple(x + (y - x) * u for x, y in zip(e1, e2))
            o.keyframe_insert("location", frame=f); o.keyframe_insert("rotation_euler", frame=f); o.keyframe_insert("scale", frame=f)
        t = f / 24.0
        mud = {id(m[0]) for m in mudam}
        for o, r0, p1, p2 in vida:
            r = o.rotation_euler if id(o) in mud else r0
            if o.name.endswith("_tronco"):
                o.rotation_euler = (r[0] + 0.014 * math.sin(t * 2 * math.pi / 3.3 + p1), r[1], r[2] + 0.01 * math.sin(t * 0.8 + p2))
            else:
                o.rotation_euler = (r[0] + 0.02 * math.sin(t * 0.9 + p2), r[1], r[2] + 0.035 * math.sin(t * 1.3 + p1))
            o.keyframe_insert("rotation_euler", frame=f)
        if mov:
            c2, c1 = fim_c, ini_c
            u = u * fator
            cam.location = tuple(x + (y - x) * u for x, y in zip(c1["loc"], c2["loc"]))
            cam.rotation_euler = tuple(x + (y - x) * u for x, y in zip(c1["rot"], unwrap(c2["rot"], c1["rot"])))
            cam.data.lens = c1["lens"] + (c2["lens"] - c1["lens"]) * u
            cam.data.dof.focus_distance = c1["foco"] + (c2["foco"] - c1["foco"]) * u
        else:
            cam.location = ini_c["loc"]; cam.rotation_euler = ini_c["rot"]
        t = f / 24.0
        cam.location = Vector(cam.location) + Vector((amp * math.sin(t * 2.1 + ph[0]), amp * math.sin(t * 1.7 + ph[1]), amp * 0.7 * math.sin(t * 2.6 + ph[2])))
        cam.rotation_euler = (cam.rotation_euler[0] + 0.0012 * math.sin(t * 1.9 + ph[3]), cam.rotation_euler[1] + 0.0012 * math.sin(t * 2.3 + ph[4]), cam.rotation_euler[2] + 0.0012 * math.sin(t * 1.5 + ph[5]))
        cam.keyframe_insert("location", frame=f); cam.keyframe_insert("rotation_euler", frame=f)
        cam.data.keyframe_insert("lens", frame=f); cam.data.dof.keyframe_insert("focus_distance", frame=f)
    for ob in bpy.data.objects:                                                  # curvas lineares: os quadros já têm a curva suave
        ad = ob.animation_data
        if ad and ad.action:
            try:
                for fc in ad.action.fcurves:
                    for kp in fc.keyframe_points:
                        kp.interpolation = "LINEAR"
            except Exception:
                pass
    os.makedirs(f"{pasta}/{plano}", exist_ok=True)
    for f in range(f0, f1 + 1):
        sc.frame_set(f)
        sc.render.filepath = f"{pasta}/{plano}/{f:04d}.png"
        bpy.ops.render.render(write_still=True)


main()
