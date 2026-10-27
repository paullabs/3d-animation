"""Escreve a decupagem v3 de "O abrigo" em texto a partir do SHOTS (a mesma tabela que renderiza o storyboard).
python3 story3_doc.py META.json SAIDA.md"""
import json, re, sys
S = json.load(open(sys.argv[1])); OUT = sys.argv[2]
R = json.load(open((__import__("canal38_env").RAIZ + "/roteiros/abrigo.json")))
T = json.load(open((__import__("canal38_env").RAIZ + "/roteiros/voz-abrigo/tempos.json")))
FAL = [f["fala"] for b in R["blocos"] for f in b["falas"]]
TIT = {1: "A corrida", 2: "A porta", 3: "Os primeiros dias", 4: "A comida acaba", 5: "O banheiro", 6: "A Pipoca", 7: "Os meses", 8: "O baralho", 9: "A porta de novo", 10: "Lá fora", 11: "O preço"}
MSG = {1: "um dia comum que acaba de uma vez; só existe um lugar para ir.", 2: "a escolha do Zé. A porta vira um muro entre quem vive e quem fica.",
       3: "alívio. A lista do que garante a vida, que depois vai acabar.", 4: "a conta não fecha, e todo mundo percebe.", 5: "o abrigo começa a apodrecer.",
       6: "o horror fica sugerido, não mostrado. A culpa é de todos, pelo silêncio.", 7: "o tempo gasta as pessoas. A morte é contada por uma ausência.",
       8: "a solidão vira loucura mansa.", 9: "não dá mais para ficar. A porta abre.", 10: "o mundo acabou; só um objeto da vida antes resistiu.", 11: "sobreviver não foi ganhar."}
ids = list(S)
dur = {k: round(S[k]["t1"] - S[k]["t0"], 2) for k in ids}
assert max(dur.values()) <= 1.3001, "tem plano acima de 1,3 s"
total = S[ids[-1]]["t1"]
mm = lambda k: int(re.match(r"(\d+) mm", S[k]["lente"]).group(1)) if re.match(r"(\d+) mm", S[k]["lente"]) else None
lentes = {k: mm(k) for k in ids}
def faixa(a, b):
    return sum(1 for k in ids if lentes[k] is not None and a <= lentes[k] <= b)
parados = sum(1 for k in ids if S[k]["mov"].startswith("parada"))
cctv = [k for k in ids if S[k]["cctv"]]
fala_de = lambda k: int(re.match(r"(\d+)", k).group(1))
L = []
w = L.append
w("# O abrigo: decupagem de cinema (v3)\n")
w("Feita em 25/10/2026 sobre a voz, o roteiro e a ficha já aprovados. Cada plano abaixo foi renderizado como quadro parado (lente, posição e foco de verdade) e está na prancha `storyboard3-1..4.png`; o código de cada quadro está em `kit3d/story3_abrigo.py`, e esta decupagem sai da mesma tabela.\n")
w("## O que o Paulo pediu (24 e 25/10) e como a v3 responde\n")
w("| Pedido | Resposta nesta decupagem |\n|---|---|")
w("| 25/10: \"o filme já tem que começar com a câmera de frente para a pessoa pedalando; depois, a primeira pessoa\" | **1A** abre de frente para o narrador (\"eu\", de blusa vermelha escura) pedalando para a câmera, de cabeça erguida para a sirene; **1B** e **1D** entram nos olhos dele (primeira pessoa). O narrador é personagem novo: ficha em `narrador-eu.png`. |")
w("| 25/10: \"no fim da corrida a câmera tem que ser a oposta: do lado do bunker, todo mundo correndo de frente\" | **1E, 1F e 1G**: a câmera está no bunker, sob o pórtico, olhando a rua de volta; a multidão vem correndo para nós e o céu estoura em branco atrás dela. |")
w("| 25/10: \"as pessoas entram na porta; o Zé tenta fechar e, por pouco, tranca todo mundo do lado de fora\" | **2A** mostra o povo entrando (a Lu, o narrador, a Rita já dentro) e o Zé no batente chamando o resto; **2B** o Zé empurra a porta pela roda e a mão de quem chegou tarde ainda está na fresta; **2C** a roda gira e a porta tranca; **2D, 2E e 2F** o povo do lado de fora, no aço e na janelinha; **2G** o rosto do Zé. |")
w("| 25/10: \"o braço da primeira pessoa parece solto, bugado\" | A manga agora é comprida e sai do quadro em todos os planos com a mão de quem conta (1B, 1D, 3E, 4B a 4D, 5A, 6E, 9A, 10F e 10G): nunca aparece a ponta redonda do braço no meio da imagem. A mão 3D e a blusa vermelha escura continuam as mesmas. |")
w(f"| \"Cortes bem rápidos; nenhum plano pode passar de 1,3 s\" | **{len(ids)} planos em {total:.1f} s** (média de {total / len(ids):.2f} s); o maior tem **{max(dur.values()):.2f} s** e o menor {min(dur.values()):.2f} s. Os cortes caem nas palavras da voz. |")
w(f"| \"Mas a câmera não pode ficar toda hora se movimentando\" | **{parados} dos {len(ids)} planos são de câmera parada**; só se mexem os que a história pede (dolly até a cama, grua do final, câmera na mão na corrida). |")
w("| \"Objetos planos; a mão parece papel\" | Tudo em 3D: mãos com dedos articulados e a blusa vermelha escura, porta com vidro de verdade, bicicleta, sirene, estante, galões, gaiola, prato, mesa, cadeira, cama, lâmpadas, quadro de giz com riscos de cinco em cinco, privada, caderno, baralho, jaqueta jeans. |")
w("| \"A cidade está muito flat\" | Rua em 3D (prédios com varanda, toldo, fios, postes, árvores, carros) e a mesma rua em ruínas no fim. |")
w("| \"Câmeras mais próximas do rosto, de baixo, e uma câmera de segurança\" | " + f"{faixa(50, 200)} planos de 50 mm ou mais (rostos e detalhes de perto), {faixa(1, 20)} de 20 mm ou menos (rente ao chão e ao objeto), e a **câmera de segurança em {len(cctv)} planos** ({', '.join(cctv)}), com profundidade e o visual de CAM/DIA/REC. |")
w("| \"O bunker tem que aparecer na corrida\" | Nos planos 1B, 1C e 1D o bunker está no fim da rua, com a porta aberta e a luz âmbar; em 1E, 1F e 1G a câmera está nele, e em 2A fica ao lado da porta. O vão tem 1,5 m para ninguém atravessar o batente quando a animação entrar. |")
w("| \"A porta do bunker é a mesma\" | Uma peça só (`porta3d`): de fora nos planos 2A, 2D, 2E e 11A; de dentro nos planos 2B, 2C, 2F, 2G, 9D, 9E e 10A. |")
w("| \"Efeito Fuji (filme) por último\" | Não entra aqui: é pós, depois do render cheio. |\n")
w("## O que não mudou\n")
w("- A voz (`roteiros/voz-abrigo/narracao.wav`, 71,7 s), o roteiro (`roteiros/abrigo.json`) e a ficha v2 (Walking Dead).\n- A legenda de até 3 palavras e o selo \"DIA n\" (1, 21, 60, 200, 300 e 700) entram só na montagem, por cima dos quadros; ficam fora dos rostos.\n- Moderação do Instagram: terceira pessoa, nenhum plano mostra violência; a carne, a morte e o que há lá fora são sugeridos por objeto e ausência.\n")
w("## A linguagem do filme\n")
w("**A história em uma frase:** uma porta se fecha para salvar quem está dentro e, quando abre de novo, não há mais nada lá fora. O filme é feito de **rimas**: o que aparece no começo volta no fim, mudado.\n")
w("| Rima | Começo | Fim |\n|---|---|---|")
w("| A sirene | 1A: soa no alto do poste, vermelha, com as ondas | 10D: caída no asfalto, cheia de cinza, apagada |")
w("| A bicicleta | 1C: tomba para a lente, a roda gira, o sino bate | 10E: no mesmo lugar e no mesmo ângulo, coberta de pó; 10F e 10G: a mão magra limpa o sino |")
w("| A rua vista do bunker | 1E: a câmera sob o pórtico, a multidão correndo de frente para nós | 10B: o mesmo quadro, ninguém, cinza no chão |")
w("| A roda da porta | 2C: as mãos giram e a porta fecha; a fresta some | 9D e 9E: o mesmo quadro, a roda gira ao contrário e a luz entra e cega |")
w("| A estante | 3B: cheia, grande na tela | 4A: o mesmo quadro, quase vazia |")
w("| O quadro de giz | 3E: o primeiro risco | 5A: a terceira semana; 7A: a parede coberta; 9A: já passa da moldura |")
w("| As lâmpadas | 3D: as três acesas | 6G, 7C, 8C: só uma; as outras, queimadas |")
w("| A cama | 7E: a Lu deitada | 7G: o mesmo quadro, a manta dobrada e a jaqueta na cadeira |")
w("| O suéter vermelho | 3F e 6A: na Pipoca | 6D e 6E: dobrado na gaiola vazia; 11A e 11B: na mão da Rita, a única cor do mundo cinza |\n")
w("### De que lado fica a câmera\n")
w("A rua corre ao longo de um eixo e o bunker fica no fim dela. Há três lados, e o filme não mistura sem motivo:\n\n- **Câmera da rua**, olhando para o bunker (o rumo da corrida): 1B, 1C, 1D e a bicicleta caída do fim. É onde estamos quando corremos.\n- **Câmera do bunker**, olhando a rua de volta (a multidão vem para nós): 1E, 1F, 1G e, no fim, 10B. É o lado de quem espera.\n- **Câmera de dentro**: de 2B em diante, olhando a porta, e a sala; a porta é sempre a mesma peça.\n")
w("### Lentes e o que cada uma diz\n")
w("- **14 a 20 mm, a centímetros do objeto:** o gesto que prova a fala (a roda, a bicicleta, o galão, a água no chão, as botas na cinza).\n- **22 a 35 mm:** o espaço com as pessoas (a mesa, a briga, a rua, a sala).\n- **40 a 50 mm:** quem fala ou sente (por cima do ombro, o caderno, o povo na janelinha).\n- **70 a 85 mm, foco curto:** os rostos e a comida; é onde a pergunta moral acontece (\"Ele não abriu\", a carne no prato, a lágrima da Rita).\n- **Câmera de segurança (16 a 20 mm, do alto de um canto):** só para o que ninguém devia ver: o silêncio dos meses, a briga e o Zé jogando sozinho.\n")
w(f"No total: {faixa(1, 20)} planos de até 20 mm, {faixa(21, 35)} de 21 a 35 mm, {faixa(36, 60)} de 36 a 60 mm e {faixa(61, 200)} de 70 mm ou mais.\n")
w("### Luz e cor\n")
w("Uma fonte de luz por cena: o céu nublado da rua, as lâmpadas âmbar do abrigo (só uma, no fim), o branco do clarão e o branco sujo da cinza. O único vermelho vivo é o suéter da Pipoca (e a manga de quem conta, mais escura). A cor do mundo morto é a mesma da rua viva, só apagada.\n")
w("## Plano a plano\n")
w("Os tempos são os da voz aprovada; o corte cai na palavra que o plano prova. `Dur.` é a duração do plano; a legenda fica na faixa de baixo e o assunto no terço de cima ou no meio.\n")
for n in range(1, 12):
    ks = [k for k in ids if fala_de(k) == n]
    f = T["falas"][n - 1]
    w(f"### {n}. {TIT[n]} ({S[ks[0]]['t0']:.1f} a {S[ks[-1]]['t1']:.1f} s)")
    w(f"*\"{FAL[n - 1]}\"*\n")
    w(f"**Mensagem:** {MSG[n]}\n")
    w("| Plano | Tempo | Dur. | Palavras | Lente e câmera | Foco | Movimento | O que se vê |\n|---|---|---|---|---|---|---|---|")
    for k in ks:
        s = S[k]
        w(f"| {k} | {s['t0']:.2f} a {s['t1']:.2f} | {dur[k]:.2f} s | \"{s['palavras']}\" | {s['lente']} | {s['foco']} | {s['mov']} | {s['vemos']} |")
    w("")
w(f"Depois do último plano ({total:.1f} s) a tela fica preta até o fim da faixa de voz (71,73 s).\n")
w("## Ritmo\n")
curtos = [k for k in ids if dur[k] < 0.8]
w(f"- **{len(ids)} planos, média de {total / len(ids):.2f} s.** Os mais curtos (menos de 0,8 s: {', '.join(curtos)}) caem nas listas e nos golpes: \"comida, água e luz\" (3B, 3C, 3D), \"eu larguei\" (1B), o clarão (1G), a roda que gira (9D, 9E) e o sino (10G).\n- **Os mais longos (1,2 a 1,3 s)** são os que precisam pesar: \"Ele não abriu\" (2F), o silêncio dos meses (7B), o Zé sorrindo para a jaqueta (8C) e o fim (11A).\n- **Câmera parada em {parados} planos;** a ideia é que o corte faça o movimento e a câmera só ande quando andar significa alguma coisa (a corrida, a briga, a aproximação da cama, o Zé andando até a porta e a grua do final).\n")
w("## Próximos passos, se aprovar\n")
w("1. **Rascunho animado**, em meia resolução, em cima destes quadros: movimento de animador (mola por junta, câmera com entrada e saída), colisão e movimento medidos antes de mostrar (`colisao.py`, `mede_mov.py`).\n2. **Som:** trilha clássica tensa e sutil, um efeito por ação no quadro certo, sem repetir arquivo, e o toque do sino sem eco no 10G.\n3. **Render cheio** e, só por último, o **efeito Fuji** (filme).\n")
txt = re.sub(r"(?<=\d)\.(?=\d)", ",", "\n".join(L))                       # vírgula decimal
open(OUT, "w").write(txt)
print("ok", OUT, len(L), "linhas")
