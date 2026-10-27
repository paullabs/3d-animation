"""Vida contínua na cena (pedido de 23/10/2026: "as coisas estão muito paradas; trazer o displacement dos rostos para os objetos;
mais smooth, trabalhar na onda").
- tremido de traço (boil): todo objeto e figurante é redesenhado 3 vezes por segundo, como os olhos e a boca do boneco
  (Displace com ruído, mesma técnica de heroi.boil; amplitude pequena e proporcional ao tamanho);
- personagens: balanço lento de peso (tronco) e de cabeça em ondas sobrepostas, além da respiração e das piscadas;
- figurantes de silhueta: balanço leve, cada um no seu tempo;
- câmera na mão: deriva suave (soma de senos lentos), proporcional à distância do assunto;
- o que voa assenta com um quique curto (ver unidades.voa)."""
import math, random
import bpy
import lib
from lib import empty, key

AMP = 0.0016          # tremido (m): bem pouquinho, menos de 1 px num plano médio (0,006 bugava braços e objetos)


def boil_cena(f0, f1, rate=3, fps=24, seed=7, pular=6.0):
    """tremido de traço bem leve em todas as bordas, redesenhado 3 vezes por segundo e PARADO entre um passo e outro.
    v4/v5 (recusado: "tá bugando os braços, os elementos, tudo"): o ruído estava preso ao MUNDO; quando um braço ou um
    objeto se mexia, ele atravessava o ruído e a forma mudava a cada quadro (não 3 vezes por segundo), e forte demais.
    Agora cada objeto tem o seu controle pendurado nele (o ruído anda junto com ele), todos com a mesma sequência de passos:
    o contorno e o preenchimento do mesmo desenho continuam juntos, e o tremido só muda nos passos de 3 qps."""
    rnd = random.Random(seed)
    passos = []
    passo = max(1, round(fps / rate)); f = f0
    while f <= f1:
        passos.append((f, (rnd.uniform(-9, 9), rnd.uniform(-9, 9), rnd.uniform(-9, 9)))); f += passo
    tx = bpy.data.textures.get("boilc") or bpy.data.textures.new("boilc", "CLOUDS")
    tx.noise_scale = 0.3; tx.noise_depth = 0
    # bonecos ficam de fora (já tremem nos olhos e na boca): o braço é refeito a cada quadro a partir das juntas
    # (geometry nodes, sem pai) e com tremido a mão soltava do braço e a cabeça do deputado tremia (v5, recusado)
    bonecos = tuple(o.name[:-4] + "_" for o in bpy.data.objects if o.name.endswith("_inv"))
    def de_boneco(o):
        if o.name.startswith(bonecos) or any(m.type == "NODES" for m in o.modifiers):
            return True
        p = o.parent
        while p is not None:
            if p.name.endswith("_inv"):
                return True
            p = p.parent
        return False
    n = 0
    for o in list(bpy.data.objects):
        if o.type != "MESH" or any(m.name.startswith("boil") for m in o.modifiers) or de_boneco(o):
            continue
        dims = max(o.dimensions) if o.dimensions else 0.0
        if dims > pular or dims < 0.01:                       # paredes e chão enormes não tremem (não se nota e custa)
            continue
        ctl = bpy.data.objects.new("bc_" + o.name, None); bpy.context.scene.collection.objects.link(ctl)
        ctl.parent = o                                        # o ruído anda com o objeto: só muda nos passos
        for fk, loc in passos:
            ctl.location = loc; key(ctl, "location", fk, "CONSTANT")
        for eixo in ("X", "Z"):
            d = o.modifiers.new(f"boilc{eixo}", "DISPLACE")
            d.texture = tx; d.direction = eixo; d.strength = AMP * 2; d.mid_level = 0.5
            d.texture_coords = "OBJECT"; d.texture_coords_object = ctl
        n += 1
    return n


def onda(t, per, fase):
    """duas ondas sobrepostas (períodos que não batem): parece vivo, nunca um pêndulo"""
    return 0.7 * math.sin(2 * math.pi * t / per + fase) + 0.3 * math.sin(2 * math.pi * t / (per * 0.53) + fase * 1.7)


def vida_ator(tl, f0, f1, seed=3, tronco=1.6, cabeca=2.4, peso=0.008):
    """balanço lento de peso e de cabeça, SOMADO ao que a cena animou (tl.add): o boneco nunca fica parado.
    O tronco balança, a cabeça faz a sua onda (mais rápida) e o quadril transfere o peso de um lado ao outro."""
    rnd = random.Random(seed)
    pt, pc, pp = rnd.uniform(3.6, 4.6), rnd.uniform(2.4, 3.2), rnd.uniform(5.0, 6.5)
    ft, fc, fp = rnd.uniform(0, 6.28), rnd.uniform(0, 6.28), rnd.uniform(0, 6.28)
    entra = 12                                                   # sobe do zero (sem salto no primeiro quadro)
    for f in range(tl.f0, tl.f1 + 1):
        k = tl.i(f); t = (f - tl.f0) / tl.fps; m = min(1.0, (f - tl.f0) / entra)
        tl.add["torso"][k] += m * tronco * onda(t, pt, ft)
        tl.add["head"][k] += m * cabeca * onda(t, pc, fc)
        tl.add["chest"][k] += m * 0.6 * onda(t, pt * 0.8, ft + 1.0)
        if tl.walkw[k] == 0 and tl.prim["x"][k] is not None:
            tl.prim["x"][k] += m * peso * onda(t, pp, fp)


def pendulo(prefixos, piv, f0, f1, amp_deg=1.8, periodo=3.4, fase=0.0, chao=("poca",)):
    """lâmpada pendurada (e o feixe e o halo dela) balançando devagar em torno do ponto do fio.
    O que está no CHÃO (a poça de luz) não gira junto (girar tira o disco do chão e ele corta o piso):
    só desliza de lado, acompanhando onde o feixe bate (x = altura do fio x tangente do ângulo)."""
    p = empty("pend_" + prefixos[0], None, piv)
    bpy.context.view_layer.update()
    inv = p.matrix_world.inverted()
    no_chao = []
    for o in list(bpy.data.objects):
        if o is not p and o.parent is None and any(o.name == x or o.name.startswith(x + "_") for x in prefixos):
            if any(c in o.name for c in chao):
                no_chao.append((o, o.location.x)); continue
            o.parent = p; o.matrix_parent_inverse = inv
    for f in range(f0, f1 + 1, 3):
        t = (f - f0) / 24.0; ang = math.radians(amp_deg * onda(t, periodo, fase))
        p.rotation_euler = (0, ang, 0); key(p, "rotation_euler", f, "BEZIER")
        for o, x0 in no_chao:
            o.location.x = x0 - piv[2] * math.tan(ang); key(o, "location", f, "BEZIER")
    return p


def balanca_figurantes(f0, f1, seed=11):
    """silhuetas (props.pessoa) balançam de leve, cada uma no seu tempo"""
    import props
    rnd = random.Random(seed)
    for o in list(bpy.data.objects):
        if (o.type == "EMPTY" and bpy.data.objects.get(o.name + "_head") is not None and not o.name.endswith("_inv")
                and not (o.animation_data and o.animation_data.action)):          # quem já anda ou é boneco fica como está
            props.sway(o, f0, f1, amp_deg=rnd.uniform(0.6, 1.3), period=rnd.randint(60, 96), phase=rnd.uniform(0, 6.28))


def camera_na_mao(f0, f1, seed=5, k=0.006):
    """deriva suave nas câmeras (já gravadas quadro a quadro): soma de senos lentos, amplitude = k x distância de foco"""
    rnd = random.Random(seed)
    for cam in [o for o in bpy.data.objects if o.type == "CAMERA"]:
        ad = cam.animation_data
        if not ad or not ad.action:
            continue
        fx = [fc for fc in lib._fcs(cam) if fc.data_path == "location"]
        if len(fx) < 3:
            continue
        d = cam.data.dof.focus_distance or 4.0
        fases = [rnd.uniform(0, 6.28) for _ in range(4)]
        for fc in fx:
            if fc.array_index == 1:
                continue
            for kp in fc.keyframe_points:
                t = kp.co[0] / 24.0
                if fc.array_index == 0:
                    off = k * d * (0.6 * math.sin(2 * math.pi * 0.19 * t + fases[0]) + 0.4 * math.sin(2 * math.pi * 0.41 * t + fases[1]))
                else:
                    off = k * d * 0.7 * (0.6 * math.sin(2 * math.pi * 0.23 * t + fases[2]) + 0.4 * math.sin(2 * math.pi * 0.37 * t + fases[3]))
                kp.co[1] += off; kp.handle_left[1] += off; kp.handle_right[1] += off
            fc.update()
