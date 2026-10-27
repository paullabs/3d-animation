# Texto na tela (`kit3d/overlay_pcc4.py`)

Ele recusou a legenda "muito invasiva": uma palavra grande em caixa alta por vez, com contorno grosso, e o rótulo do nível grande o tempo todo. O texto ajuda sem cobrir a cena.

## Legenda
- Trechos de até 3 palavras (ou até 18 caracteres), em letra normal, Avenir Next Demi Bold 54 px.
- Posição: centro da área segura, y = 1310.
- O trecho aparece apagado (42%) e **cada palavra acende quando é dita**.
- Cores: dinheiro ("1.200 reais", "700 mil", "5 milhões") em verde `#8EE59B`, outros números em âmbar, o resto em branco.
- Sombra macia sem contorno grosso, mais uma **mancha escura bem desfocada** atrás do trecho, para ler sobre a camisa branca listrada.
- Entra subindo 8 px em 0,14 s e sai em 0,08 s.

## Nível
Fica pequeno no canto de cima à esquerda (x de cerca de 92 a 350): "NÍVEL 1" em coral 24 px e o nome em branco 38 px. Aparece por **2,4 s** quando o nível começa e some. Garanta que começa junto com a cena do nível.

## Contadores (o "jogo")
Ícone desenhado mais número, **sem palavras**, pequenos (ícone 34 px, número 46 px), no canto de cima à direita (945, 318). Ficam **2,2 s** e somem. Ícones disponíveis:
- `icone_nota`: dinheiro;
- `icone_sirene`: polícia;
- `icone_cadeado`: presos.

O contador do salário sobe de 100 em 100 junto com as notas que caem no gancho.

## Para um tema novo
Copie `overlay_pcc4.py` e troque `VOZ`, `NIVEIS` (fala de início e nomes) e `_entradas()` (palavra que dispara cada contador). As palavras vêm de `palavras.json`. Teste com:
```
python3 overlay_X.py --preview DIR 10.4,19.9 --fundo quadro.png
```
