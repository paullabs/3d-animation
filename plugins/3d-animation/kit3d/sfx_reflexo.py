"""Efeitos sintetizados do reflexo (o tempo que dobra), no mesmo timbre do sfx.py da skill:
- mosca: zumbido que desacelera junto com o tempo (a batida das asas cai de ~190 Hz para ~45 Hz) e para no tapa;
- tempo_desce: o mundo freia (ruído grave que desce, com um "vuuum" de fita perdendo a rotação);
- tempo_volta: o mundo volta (o contrário: sobe e abre);
- coracao: duas batidas graves (tum-tum) para a câmera lenta da final;
- bipe: o sinal do botão.
python3 sfx_reflexo.py PASTA"""
import os, sys
import numpy as np
sys.path.insert(0, os.path.join(__import__("canal38_env").RAIZ, "ferramentas"))
import sfx as S

SR = S.SR
rng = np.random.default_rng(7)


def mosca(dur=2.2, t_lento=1.38, t_fim=2.15):
    """zumbido de mosca: dente de serra com vibrato que passeia; a partir de t_lento a frequência cai em curva (o tempo freia) e corta no tapa"""
    t = S._t(dur)
    f = np.where(t < t_lento, 190 + 25 * np.sin(2 * np.pi * 3.1 * t) + 12 * np.sin(2 * np.pi * 7.3 * t),
                 45 + 145 * np.exp(-(t - t_lento) / 0.12))
    fase = 2 * np.pi * np.cumsum(f) / SR
    x = 2 * ((fase / (2 * np.pi)) % 1.0) - 1.0 + 0.4 * np.sin(2 * fase)
    x = S._passa_baixa(S._passa_alta(x, 120), 2600)
    perto = 0.55 + 0.45 * np.sin(2 * np.pi * 0.9 * t + 1.0) ** 2                 # chega perto e se afasta do ouvido
    env = perto * np.clip(t / 0.15, 0, 1) * np.clip((t_fim - t) / 0.02, 0, 1)
    pan = np.sin(2 * np.pi * 0.7 * t)
    m = x * env
    return S._norm(np.stack([m * np.sqrt(0.5 * (1 - 0.6 * pan)) * 1.4, m * np.sqrt(0.5 * (1 + 0.6 * pan)) * 1.4], 1), 0.6)


def tempo(dur=1.3, desce=True):
    """o tempo dobra: ruído com varredura (de agudo para grave quando desce) e um tom que perde a rotação"""
    t = S._t(dur); u = t / dur
    v = u if desce else 1 - u
    fc = 3800 * (1 - v) ** 2 + 160
    x = S._passa_baixa(S._passa_alta(rng.standard_normal(len(t)), 90), fc)
    f = 220 * (1 - 0.75 * v) if desce else 55 + 165 * (1 - v)
    tom = np.sin(2 * np.pi * np.cumsum(np.broadcast_to(f, t.shape)) / SR) * 0.5
    env = (np.sin(np.pi * np.clip(u * 1.05, 0, 1)) ** 1.6) if desce else (np.clip(u / 0.85, 0, 1) ** 2 * np.clip((1 - u) / 0.15, 0, 1))
    return S._norm(S._estereo((x * 0.8 + tom) * env, larg=1.0), 0.7)


def coracao(dur=0.9):
    """tum-tum grave, como no peito de quem espera"""
    out = np.zeros(int(dur * SR))
    for t0, g in ((0.0, 1.0), (0.26, 0.7)):
        a = S.boom(0.5, f0=62, f1=38)[:, 0] * g
        i = int(t0 * SR); out[i:i + len(a)] += a[:len(out) - i]
    return S._norm(S._estereo(out), 0.8)


def bipe(f=880, dur=0.16):
    t = S._t(dur)
    x = np.sin(2 * np.pi * f * t) * np.clip(t / 0.005, 0, 1) * np.clip((dur - t) / 0.03, 0, 1)
    return S._norm(S._estereo(x), 0.5)


def pegada(dur=0.7):
    """o punho fecha na mosca: tapa de ar (ruído médio-agudo, 30 ms), corpo de 140 a 70 Hz que SE OUVE em caixa de celular
    (o grave puro de 46 Hz da v13 não aparecia) e um estalo curtinho dos dedos fechando 8 ms depois"""
    t = S._t(dur); n = len(t)
    ruido = rng.standard_normal(n)
    tapa = S._passa_baixa(S._passa_alta(ruido, 700), 5200) * np.exp(-t / 0.035) * np.clip(t / 0.001, 0, 1)
    f = 70 + 70 * np.exp(-t / 0.05)
    corpo = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.13) * 0.9
    corpo += 0.35 * np.sin(2 * np.pi * np.cumsum(2 * f) / SR) * np.exp(-t / 0.07)
    estalo = np.roll(S._passa_alta(rng.standard_normal(n), 2600) * np.exp(-t / 0.008), int(0.008 * SR)) * 0.7
    return S._norm(S._estereo(tapa * 1.1 + corpo + estalo, larg=0.4), 0.9)


def ar(dur=0.6, grave=70):
    """a onda de ar que sai do anel: um sopro (ruído que varre de agudo para grave) com um "uum" de pressão por baixo; sobe em 12 ms e esvazia devagar"""
    t = S._t(dur); n = len(t); u = t / dur
    ruido = S._passa_alta(rng.standard_normal(n), 120)
    fc = 250 + 3200 * np.exp(-u * 5.0)
    sopro = S._passa_baixa(ruido, fc) * np.clip(t / 0.012, 0, 1) * np.exp(-u * 4.2)
    f = grave * (1.0 + 0.9 * np.exp(-u * 6))
    pressao = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.clip(t / 0.02, 0, 1) * np.exp(-u * 3.5) * 0.8
    return S._norm(S._estereo(sopro * 0.9 + pressao, larg=1.2), 0.75)


def mosca_presa(dur=3.2):
    """a mosca se debatendo dentro do punho fechado: o zumbido abafado (passa-baixa), a força vai e volta como quem luta, e vai cansando"""
    t = S._t(dur); u = t / dur
    f = 205 + 20 * np.sin(2 * np.pi * 5.0 * t) + 10 * np.sin(2 * np.pi * 11 * t)
    fase = 2 * np.pi * np.cumsum(f) / SR
    x = S._passa_baixa(2 * ((fase / (2 * np.pi)) % 1.0) - 1.0 + 0.3 * np.sin(2 * fase), 680)
    luta = S._passa_baixa(rng.standard_normal(len(t)), 7.0); luta = 0.55 + 0.45 * np.clip(luta / (np.abs(luta).max() + 1e-9) * 2.2 + 0.2, -1, 1)
    env = luta * (1 - 0.65 * u) * np.clip(t / 0.03, 0, 1) * np.clip((dur - t) / 0.8, 0, 1)
    return S._norm(S._estereo(x * env, larg=0.3, pan=0.15), 0.55)


def _reverb(x, cauda=0.7, mistura=0.28):
    """cauda de ambiente: o som convolvido com ruído que morre em exponencial (a sala grande onde o tempo parou)"""
    n = int(cauda * SR); t = np.arange(n) / SR
    ir = S._passa_baixa(rng.standard_normal(n), 2200) * np.exp(-t / (cauda * 0.32))
    L = len(x) + n; F = 1 << (L - 1).bit_length()
    y = np.fft.irfft(np.fft.rfft(x, F) * np.fft.rfft(ir, F), F)[:len(x)]
    return x + mistura * y / (np.abs(y).max() + 1e-9) * np.abs(x).max()


def vrum(dur=1.4, f0=240, f1=38, cauda=0.7):
    """impacto de "o tempo parou" (pedido de 23/10/2026: "efeitos de impacto, como se tivesse parado no tempo, tipo vrum"):
    baque seco no quadro 0, um "vruuum" de motor que despenca de f0 para f1 (serra distorcida, com os harmônicos no médio que o celular reproduz),
    sub de 110 a 32 Hz, rumor grave que fica e uma cauda de sala"""
    t = S._t(dur); n = len(t)
    f = f1 + (f0 - f1) * np.exp(-t / 0.17)
    fase = np.cumsum(f) / SR
    serra = np.tanh(3.2 * (2 * (fase % 1.0) - 1.0))
    corpo = S._passa_baixa(serra, 1100) * (1 - 0.4 * (0.5 + 0.5 * np.sin(2 * np.pi * 24 * t))) * np.exp(-t / 0.5) * np.clip(t / 0.003, 0, 1)
    sub = np.sin(2 * np.pi * np.cumsum(32 + 80 * np.exp(-t / 0.07)) / SR) * np.exp(-t / 0.4) * 1.1
    baque = S._passa_baixa(S._passa_alta(rng.standard_normal(n), 250), 3200) * np.exp(-t / 0.045) * 1.2
    rumor = S._passa_baixa(rng.standard_normal(n), 170) * np.exp(-t / 0.8) * 0.55
    x = _reverb(np.tanh(1.5 * (corpo * 0.9 + sub + baque + rumor)), cauda)
    return S._norm(S._estereo(x, larg=1.0), 0.95)


def sucao(dur=0.45):
    """o ar sendo puxado para dentro antes do impacto (ao contrário): ruído que sobe de grave a agudo, cada vez mais forte, e um tom que sobe; corta seco no baque"""
    t = S._t(dur); u = t / dur
    ruido = S._passa_alta(rng.standard_normal(len(t)), 100)
    x = S._passa_baixa(ruido, 180 + 5200 * u ** 2.2) * u ** 2.4
    tom = np.sin(2 * np.pi * np.cumsum(55 + 420 * u ** 2) / SR) * u ** 3 * 0.35
    return S._norm(S._estereo(x + tom, larg=0.8), 0.8)


def chute(dur=0.45):
    """o pé na bola: estalo de couro (ruído médio, 12 ms) e um "tum" curto de 120 a 70 Hz"""
    t = S._t(dur); n = len(t)
    couro = S._passa_baixa(S._passa_alta(rng.standard_normal(n), 900), 4500) * np.exp(-t / 0.012)
    tum = np.sin(2 * np.pi * np.cumsum(70 + 50 * np.exp(-t / 0.03)) / SR) * np.exp(-t / 0.09)
    return S._norm(S._estereo(couro * 0.8 + tum, larg=0.3), 0.9)


def tiro(dur=1.2):
    """a pistola de largada: estalo seco (ruído largo, 20 ms) e o eco do estádio aberto"""
    t = S._t(dur); n = len(t)
    estalo = S._passa_alta(rng.standard_normal(n), 600) * np.exp(-t / 0.02)
    corpo = S._passa_baixa(rng.standard_normal(n), 900) * np.exp(-t / 0.06) * 0.8
    x = estalo + corpo
    eco = np.zeros(n); d = int(0.21 * SR); eco[d:] = x[:n - d] * 0.3
    return S._norm(S._estereo(_reverb(x + eco, 1.0, 0.35), larg=0.9), 0.95)


def queda(dur=1.6):
    """a câmera de TV batendo no gramado: baque pesado, metal amassando e pedaços"""
    a = S.boom(dur, f0=90, f1=36)[:, 0]
    b = S.impacto_metal(min(dur, 1.2))[:, 0]
    x = a.copy(); x[:len(b)] += 0.55 * b
    return S._norm(S._estereo(x, larg=0.8), 0.95)


def bum(dur=2.8):
    """a pegada da mosca (24/10/2026: "precisa ser um bass, bum, que para no ar"): um BUM grave e cheio que fica suspenso.
    sub que cai de 60 para 38 Hz e morre devagar (~0,9 s), saturação suave para os harmônicos de 80-160 Hz aparecerem no celular,
    ataque macio de 6 ms (sem tapa nem estalo), cauda grave de sala e um fio agudo bem baixo que fica pendurado (o tempo congelado)"""
    t = S._t(dur); n = len(t)
    f = 38 + 22 * np.exp(-t / 0.35)
    sub = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.9) * np.clip(t / 0.006, 0, 1)
    corpo = np.tanh(6.0 * sub)                                                  # saturação forte: 3º, 5º e 7º harmônicos (135, 225, 315 Hz) que celular e notebook tocam
    kick = np.sin(2 * np.pi * np.cumsum(70 + 130 * np.exp(-t / 0.045)) / SR) * np.exp(-t / 0.22) * 0.9      # o "bum" do corpo, de 200 a 70 Hz
    pancada = S._passa_baixa(S._passa_alta(rng.standard_normal(n), 100), 700) * np.exp(-t / 0.06) * 0.6
    fio = np.sin(2 * np.pi * 3150 * t) * 0.018 * np.clip(t / 0.25, 0, 1) * np.exp(-t / 1.4)   # o ar parado
    x = _reverb(corpo * 0.8 + kick + pancada, 1.6, 0.32) + fio
    x *= np.clip((dur - t) / 0.6, 0, 1)
    return S._norm(S._estereo(x, larg=0.6), 0.95)


def swish(seed, dur, lo, hi, pan=0.0, sobe=True):
    """sopro de movimento (braço, corpo, mergulho): cada chamada com 'seed', banda e pan diferentes soa como um movimento diferente"""
    r = np.random.default_rng(seed); t = S._t(dur); n = len(t); u = t / dur
    x = S._passa_baixa(S._passa_alta(r.standard_normal(n), lo), np.linspace(hi * (0.35 if sobe else 1.0), hi * (1.0 if sobe else 0.35), n))
    env = np.sin(np.pi * np.clip(u * 1.05, 0, 1)) ** 2.0
    return S._norm(S._estereo(x * env, larg=0.6, pan=pan), 0.7)


def golpe_copo(dur=0.9):
    """o copo pousando na palma: tum mais agudo e curto que o da mosca (95 a 55 Hz) e o tilintar do vidro"""
    t = S._t(dur); n = len(t)
    tum = np.tanh(2.5 * np.sin(2 * np.pi * np.cumsum(55 + 45 * np.exp(-t / 0.05)) / SR)) * np.exp(-t / 0.16)
    vidro = (np.sin(2 * np.pi * 3100 * t) + 0.5 * np.sin(2 * np.pi * 4700 * t)) * np.exp(-t / 0.09) * 0.25
    return S._norm(S._estereo(tum + vidro, larg=0.4), 0.9)


def golpe_botao(dur=0.5):
    """o seu aperto: clique de plástico seco e um "tum" de mesa de madeira (120 a 80 Hz)"""
    t = S._t(dur); n = len(t)
    clique = S._passa_baixa(S._passa_alta(rng.standard_normal(n), 1500), 6500) * np.exp(-t / 0.008) * 1.1
    tum = np.sin(2 * np.pi * np.cumsum(80 + 40 * np.exp(-t / 0.03)) / SR) * np.exp(-t / 0.1)
    return S._norm(S._estereo(clique + tum, larg=0.3), 0.9)


def tic_3mm(dur=0.35):
    """os dedos fechando na régua no 3 mm: um tic minúsculo e um pingo de grave"""
    t = S._t(dur); n = len(t)
    tic = S._passa_alta(rng.standard_normal(n), 3000) * np.exp(-t / 0.004)
    tom = np.sin(2 * np.pi * 1800 * t) * np.exp(-t / 0.02) * 0.4 + np.sin(2 * np.pi * 70 * t) * np.exp(-t / 0.06) * 0.6
    return S._norm(S._estereo(tic + tom, larg=0.2), 0.8)


def estala_cabo(dur=1.2):
    """o cabo de aço arrebentando: estalo de metal e um "tâng" que despenca de 420 Hz"""
    t = S._t(dur); n = len(t)
    estalo = S._passa_alta(rng.standard_normal(n), 800) * np.exp(-t / 0.012) * 1.2
    f = 300 + 120 * np.exp(-t / 0.25)
    tang = (np.sin(2 * np.pi * np.cumsum(f) / SR) + 0.45 * np.sin(2 * np.pi * np.cumsum(2.76 * f) / SR)) * np.exp(-t / 0.35) * 0.55
    return S._norm(S._estereo(_reverb(estalo + tang, 0.6, 0.2), larg=0.7), 0.9)


def derrota(dur=1.7):
    """"eliminado": três notas que descem (A4, E4, A3) e somem devagar"""
    t = S._t(dur); out = np.zeros(len(t))
    for k, (f, t0) in enumerate(((440, 0.0), (330, 0.32), (220, 0.64))):
        m = t >= t0; tt = (t - t0)[m]
        out[m] += (np.sin(2 * np.pi * f * tt) + 0.3 * np.sin(2 * np.pi * 2 * f * tt)) * np.exp(-tt / 0.5) * np.clip(tt / 0.01, 0, 1) * 0.6
    return S._norm(S._estereo(_reverb(out, 0.8, 0.25), larg=0.5), 0.7)


def flutuar(dur=2.6):
    """o mundo parado no ar: acorde de vidro (880, 1320, 1760 Hz) com tremolo lento, que entra e sai macio"""
    t = S._t(dur); u = t / dur
    x = sum(np.sin(2 * np.pi * f * t + k) * (0.6 + 0.4 * np.sin(2 * np.pi * (0.7 + 0.2 * k) * t)) for k, f in enumerate((880, 1320, 1760, 2640)))
    env = np.sin(np.pi * u) ** 1.6
    return S._norm(S._estereo(_reverb(x * env, 0.9, 0.3), larg=1.0), 0.55)


def coracao_longo(dur=3.0):
    """o coração na câmera lenta: três "tum-tum" num só arquivo, cada um mais baixo que o anterior"""
    out = np.zeros(int(dur * SR))
    for t0, g in ((0.0, 1.0), (0.26, 0.7), (1.1, 0.8), (1.36, 0.55), (2.2, 0.6), (2.46, 0.4)):
        a = S.boom(0.45, f0=64, f1=40)[:, 0] * g
        i = int(t0 * SR); out[i:i + len(a)] += a[:len(out) - i]
    return S._norm(S._estereo(out), 0.8)


def chute_seco(dur=0.35):
    """o pé na bola de perto, mais agudo e curto que o primeiro chute"""
    t = S._t(dur); n = len(t)
    couro = S._passa_baixa(S._passa_alta(rng.standard_normal(n), 1400), 6000) * np.exp(-t / 0.008)
    tum = np.sin(2 * np.pi * np.cumsum(110 + 40 * np.exp(-t / 0.02)) / SR) * np.exp(-t / 0.05)
    return S._norm(S._estereo(couro + 0.7 * tum, larg=0.2), 0.9)


def rede_seca(dur=0.8):
    """a bola na rede, rápida: farfalhar de corda"""
    t = S._t(dur); n = len(t)
    x = S._passa_baixa(S._passa_alta(rng.standard_normal(n), 500), 5000) * np.exp(-t / 0.2) * (0.6 + 0.4 * np.sin(2 * np.pi * 14 * t))
    return S._norm(S._estereo(x, larg=0.8), 0.7)


def pega_menino(dur=0.7):
    """o goleiro levantando o menino: baque de tecido no corpo (110 a 60 Hz) e um sopro curto"""
    t = S._t(dur); n = len(t)
    baque = np.sin(2 * np.pi * np.cumsum(60 + 50 * np.exp(-t / 0.04)) / SR) * np.exp(-t / 0.12)
    pano = S._passa_baixa(S._passa_alta(rng.standard_normal(n), 250), 2200) * np.exp(-t / 0.15) * np.clip(t / 0.02, 0, 1) * 0.6
    return S._norm(S._estereo(baque + pano, larg=0.5), 0.85)


def extras():
    return dict(tempo_desce_b=tempo(1.0, True), swish_a=swish(11, 0.22, 400, 5200, -0.3, True), swish_b=swish(12, 0.5, 220, 2600, 0.4, False),
                swish_c=swish(13, 0.3, 300, 3800, -0.5, True), swish_d=swish(14, 0.45, 180, 2200, 0.6, False), grua=swish(15, 2.4, 150, 3000, 0.0, False),
                olhar_a=swish(16, 0.35, 500, 4200, -0.8, True), olhar_b=swish(17, 0.35, 500, 4200, 0.8, False),
                golpe_copo=golpe_copo(), golpe_botao=golpe_botao(), tic_3mm=tic_3mm(), estala_cabo=estala_cabo(), derrota=derrota(), flutuar=flutuar(),
                coracao_longo=coracao_longo(), chute_seco=chute_seco(), rede_seca=rede_seca(), pega_menino=pega_menino(), bipe_b=bipe(1175, 0.22),
                tique_relogio=S.tique(2000, 0.05))


if __name__ == "__main__":
    pasta = sys.argv[1]; os.makedirs(pasta, exist_ok=True)
    for nm, a in dict(mosca=mosca(), tempo_desce=tempo(1.3, True), tempo_volta=tempo(1.0, False), coracao=coracao(), bipe=bipe(),
                      whoosh=S.whoosh(), whoosh_curto=S.whoosh(0.35), boom=S.boom(), pegada=pegada(), ar_p=ar(0.38, 90), ar_m=ar(0.65, 70),
                      ar_g=ar(1.1, 55), mosca_presa=mosca_presa(), vrum_p=vrum(0.8, 190, 50, 0.5), vrum_m=vrum(1.2, 230, 42, 0.7),
                      vrum_g=vrum(1.9, 260, 34, 1.0), sucao=sucao(0.45), sucao_curta=sucao(0.28),
                      chute=chute(), tiro=tiro(), queda=queda(), clique=S.tique(1500, 0.06), bum=bum()).items():
        S.grava(a, os.path.join(pasta, nm + ".wav")); print("ok", nm)
    for nm, a in extras().items():
        S.grava(a, os.path.join(pasta, nm + ".wav")); print("ok", nm)
