"""Monta as 3 pranchas da ficha da parte 2 de "O abrigo" a partir dos renders do ficha_abrigo2.py.
python3 ficha_abrigo2_montar.py PASTA   ->  personagem/abrigo/ficha2-{semosso,grupo,lugares}.png"""
import os, sys, textwrap
from PIL import Image, ImageDraw, ImageFont

P = sys.argv[1]
SAI = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "personagem", "abrigo"))
F = "/System/Library/Fonts/Avenir Next.ttc"
fT, fS, fL = (ImageFont.truetype(F, n, index=i) for n, i in ((48, 0), (26, 2), (21, 0)))
BG, INK, SUB, AMB, BOR = (34, 38, 34), (236, 232, 218), (170, 168, 152), (217, 182, 106), (70, 74, 66)
M, G = 44, 22


def prancha(nome, titulo, sub, linhas, notas, largura):
    """linhas = [[(arquivo, legenda, largura_px), ...], ...] (altura 900 por linha)"""
    H = 150 + len(linhas) * (900 + 70) + 40 + 30 * sum(len(textwrap.wrap(n, 150)) + 0.3 for n in notas) + 40
    im = Image.new("RGB", (largura, int(H)), BG); d = ImageDraw.Draw(im)
    d.text((M, 30), titulo, font=fT, fill=INK)
    for k, ln in enumerate(textwrap.wrap(sub, 170)):
        d.text((M, 96 + 26 * k), ln, font=fL, fill=SUB)
    y = 150
    for linha in linhas:
        x = M
        for arq, leg, w in linha:
            if arq:
                im.paste(Image.open(os.path.join(P, arq + ".png")).convert("RGB").resize((w, 900)), (x, y))
                d.rectangle((x - 1, y - 1, x + w, y + 900), outline=BOR)
                for j, ln in enumerate(textwrap.wrap(leg, int(w / 12.5))):
                    d.text((x, y + 910 + 32 * j), ln, font=fS, fill=AMB)
            else:                                                    # coluna de texto
                yy = y
                for par in leg:
                    for ln in textwrap.wrap(par, int(w / 11)):
                        d.text((x, yy), ln, font=fL, fill=INK); yy += 28
                    yy += 12
            x += w + G
        y += 900 + 70 + 32 * max(0, max((len(textwrap.wrap(l[1], int(l[2] / 12.5))) for l in linha if l[0]), default=1) - 1)
    for n in notas:
        for ln in textwrap.wrap(n, 150):
            d.text((M, y), ln, font=fL, fill=INK); y += 28
        y += 8
    out = os.path.join(SAI, nome); im.save(out); print("ok", out, im.size)


W1 = M * 2 + 4 * 600 + 3 * G
prancha("ficha2-semosso.png", "O abrigo, parte 2 · os Sem-Osso",
        "Quem respirou o ar lá fora depois do céu branco derreteu numa gosma. A gosma sai do corpo, deixa o esqueleto e se junta de novo: vira um Sem-Osso. "
        "É o povo que batia na porta no ep. 1, com pedaços da roupa de quem foi.",
        [[("cabeca_f", "A cabeça de perto: crânio comprido e torto, um olho grande afundado e outro pequeno alto", 600),
          ("cabeca_3q", "Três quartos: lóbulo de gosma derretida caindo, sem nariz, mandíbula pendurada", 600),
          ("cabeca_p", "Perfil: o crânio alongado para cima e para trás", 600), ("cabeca_m", "O rapaz do mercado, com o boné torto", 600)],
         [("semosso_frente", "A padeira (avental do ep. 1)", 600), ("semosso_lado", "De lado: dobra onde não tem junta", 600),
          ("semosso_bone", "O rapaz do mercado (boné e colete)", 600), ("olhos", "Vivo x Sem-Osso: o olho", 600)],
         [("gosma", "Da poça ao corpo: escorre, se junta, sobe, vira gente torta", 1200 + G + 600 - 600 - G), ("esqueleto", "O que fica: o esqueleto no pilar e o rastro", 600),
          (None, ["Corpo de gosma preta com brilho frio de óleo na borda (o único brilho frio do filme).",
                  "Sem pé: a base escorre no chão e deixa poça. Braço e perna são moles e dobram no meio.",
                  "Cabeça deformada (v2, 26/10: \"mais deformada, de inspiração em monstros do Fallout, sem ficar igual ao Stranger Things\"): crânio comprido e torto com caroços e uma rachadura, olhos desiguais (um grande e afundado, um pequeno e alto), sem nariz, lóbulo de gosma derretida caindo de um lado, mandíbula pendurada com dentes tortos, baba e lágrima escorrendo. Nada de rosto aberto em pétalas.",
                  "Olho cinza APAGADO, sem sobrancelha. O vivo tem o olho branco aceso: o exame do grupo olha isso.",
                  "Sem sangue e sem nada nojento: só a forma cedendo (regra do Instagram)."], 600)]],
        ["Na animação: o corpo nunca fica parado (a gosma escorre e pinga), e o Sem-Osso cai e se refaz em vez de andar como gente."], W1)

W2 = M * 2 + 1800
prancha("ficha2-grupo.png", "O abrigo, parte 2 · o grupo do galpão (9) e o narrador",
        "Os nove que sobraram, com pano no nariz e na boca: eles respiraram o ar e se protegem do que ainda está no ar. Cada um com uma roupa (nada de clone). "
        "O narrador (de vermelho, à direita) é o único de rosto limpo: ele veio de um abrigo.",
        [[("grupo", "Da esquerda: o líder, a mulher do rádio, o velho do cochicho, o homem do taco, o jovem, a moça de cabelo solto, o careca, a moça de tranças, o menino; e o narrador", 1800)]],
        ["O líder: o mais velho, barba e cabelo grisalhos, o pano abaixado no pescoço (é quem conta tudo, de cara limpa, na fogueira).",
         "A mulher do rádio: luvas e fone; é ela que risca o quadro de giz (14 riscos) e que examina o olho do narrador.",
         "O velho do cochicho: \"ele veio de um abrigo\". O homem do taco: foi ele que deu a pancada (5B) e segura o taco no 6D.",
         "Panos em tons da paleta apagada; nenhum vermelho no grupo: o vermelho continua sendo do narrador, do suéter da Rita e da luz da torre."], W2)

W3 = M * 2 + 1200 + G + 600
prancha("ficha2-lugares.png", "O abrigo, parte 2 · o galpão, os objetos e a torre",
        "O galpão do grupo (fundo com o portão de aço e o ferrolho, panos nas janelas, fogueira no tambor, escada para o telhado, parede de teorias a carvão), "
        "os objetos de perto e a torre vista do telhado, de noite.",
        [[("galpao", "O galpão: portão de aço com ferrolho, parede de teorias, quadro de giz, mapa, rádio, fogueira", 1200), ("torre", "Do telhado: a torre e a luz vermelha", 600)],
         [("objetos", "Rádio de válvula, fone, lanterna, taco; quadro de giz com 14 riscos; mapa com poucos alfinetes", 1200),
          (None, ["Rádio: caixa de madeira, tela de pano do alto-falante, mostrador âmbar que acende, dois botões e antena.",
                  "Quadro de giz: o mesmo do calendário do ep. 1, agora com 14 riscos (um por pessoa viva no mundo).",
                  "Parede de teorias: \"QUEM FEZ OS ABRIGOS SABIA?\", \"A TORRE >\", \"O AR MUDA\" (o tipo de teoria de Fallout, sem nada do jogo).",
                  "A torre: treliça no alto do morro, depois da cidade em ruínas; a luz vermelha é a única luz elétrica do mundo e pisca."], 600)]],
        ["O portão é a rima com a porta do ep. 1: no fim, a nuca do narrador fica a um palmo dele, no lugar do Zé."], W3)
