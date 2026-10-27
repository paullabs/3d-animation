"""Contraste entre o objeto-chave e o que está atrás dele (regra de 23/10/2026: "tem que dar para identificar os objetos").
Razão de luminância no padrão WCAG: (L_claro + 0,05) / (L_escuro + 0,05). Meta: 3:1 ou mais para o que a cena precisa mostrar;
abaixo disso, o objeto some (silhueta escura em fundo escuro, verde em verde). Se a cor não pode mudar, use borda de luz ou halo atrás.
python3 contraste.py  -> tabela dos pares de uma cena (edite PARES)"""


def lum(hexcor):
    h = hexcor.lstrip("#"); r, g, b = (int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
    f = lambda c: c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b)


def razao(a, b):
    la, lb = lum(a), lum(b)
    return (max(la, lb) + 0.05) / (min(la, lb) + 0.05)


def tabela(pares, meta=3.0):
    for nome, obj, fundo in pares:
        r = razao(obj, fundo)
        print(f"{'OK ' if r >= meta else 'BAIXO'} {r:4.1f}:1  {nome:42s} {obj} sobre {fundo}")


if __name__ == "__main__":
    import sys
    print("== Mensalão (antes)")
    tabela([("terno do herói x parede", "#22305a", "#2a2119"), ("terno do herói x silhuetas", "#22305a", "#0c0a08"),
            ("terno do deputado x parede", "#2f3a55", "#2a2119"), ("silhuetas x parede lateral", "#0c0a08", "#211a14"),
            ("silhuetas x persiana", "#0c0a08", "#7fa8d8"), ("frente da mesa x chão", "#24180f", "#1b1510"),
            ("tampo da mesa x parede", "#9a6a3c", "#2a2119"), ("envelope x tampo", "#f4efe6", "#9a6a3c"),
            ("maço verde x tampo", "#b9dcb4", "#9a6a3c"), ("cabeça do herói x parede", "#0d1020", "#2a2119")])
    print("== Escada (antes)")
    tabela([("terno do herói x fundo índigo", "#22305a", "#1b1f5c"), ("cabeça do herói x fundo", "#0d1020", "#1b1f5c")])
    print("== Palácio (aprovado)")
    tabela([("terno do herói x tapete", "#22305a", "#4e1820"), ("cabeça x parede do salão", "#0d1020", "#8f7a58"), ("terno x lajota", "#22305a", "#9a8664")])
