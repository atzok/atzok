# ÄTZØK — Agenda Dez 26 → Jan 27 · Brief de direção de arte

> Prompt de direção para o vídeo motion da agenda. Frame-chave: `design/keyframe-v3-anton.png` (título) · lista igual à v2.

## O pedido, em uma frase

Um cartaz de clube impresso em risograph, dobrado em quatro e colado num poste, que **se imprime na frente de quem assiste** e entrega a agenda do ÄTZØK em 15 segundos, sem um frame de "template de Instagram".

## Referências e o que tiramos de cada uma

- **"All Dogs Go To Heaven" (rosa/verde):** é a direção principal. Papel preto com vincos de dobra, duas tintas chapadas (verde riso e rosa flúor), grotesca pesada empilhada e colada à esquerda, um bloco rosa com retícula no canto superior direito e uma área de contorno verde ocupando a metade de baixo. Datas em rosa embaixo.
- **APEX:** dela só levamos a disciplina, não a paleta: grid técnico, hierarquia line-up (nome grande, detalhe pequeno em mono) e o ritmo de "carimbo" das informações.

## Especificação

| Item | Valor |
|---|---|
| Formato | 1080×1920, 9:16 (Reels/Stories), 30 fps, ~15 s, último frame casando com o primeiro para fazer loop |
| Papel | `#171717` + grão (`assets/grain.png`) + 3 vincos (1 vertical em x 540, 2 horizontais em y 640/1280) |
| Tinta 1 | Verde riso `#2BAE4C`: nome ÄTZØK, kicker, detalhes mono, risco, curvas de nível |
| Tinta 2 | Rosa flúor `#EE3C98`: "AGENDA", datas, nomes das festas, bloco de retícula |
| Passado | `#707070` + risco verde de 12 px (cinza da marca clareado para passar contraste 3:1 no papel `#171717`) |
| Display | **Anton** (`assets/fonts/Anton.ttf`), caixa alta, 226 px, entrelinha 0.8, linhas coladas como no pôster; a barra do Ø invade o AGENDA de propósito (sobreposição de tinta) |
| Lista | Data Inter 800 62 px · Festa Inter 800 46 px · Detalhe Space Mono 700 28 px, tracking 0.14em |
| Safe area | Todo texto em x 130–888, y 288–1248. Abaixo de 1248 só decoração (curvas de nível) |
| Proibido | Gradiente, glow, sombra projetada, 3D, emoji, transições de template (zoom-blur, slide genérico), qualquer cor fora das duas tintas |

## Conteúdo (textos exatos)

```
ÄTZØK
AGENDA
DEZ 26 → JAN 27 ✶ DATAS

15.11  DESISTÊNCIA CLUBBER   JÁ FOI            ← riscada (já passou)
09.12  LUCI BAR              LONG SET
18.12  LHAMA TAKEOVER        HANKY PANKY
27.12  UNIVERSO PARALELO     CHILLOUT STAGE
11.01  FESTA NO BARCO        LHAMA BOOKINGS · BAHIA
```

## Linguagem de movimento

O movimento é **de impressão, não de interface**. Nada desliza, nada "faz bounce". As coisas aparecem como tinta que bate no papel:

1. **Registro desalinhado (misregistration):** cada bloco de texto entra com a tinta deslocada 6–10 px e encaixa no lugar em 2 frames. É a assinatura do vídeo.
2. **Carimbo:** opacidade 0 → 1 em 1–2 frames, com uma escala que cai de 1.06 para 1 (`expo.out`, 0.25 s). Sem fade longo.
3. **Flicker de fotocópia** (assinatura da marca): queda de opacidade para 0.55 por 2 frames, em downbeat. No máximo 3 vezes no vídeo.
4. **Retícula viva:** o bloco rosa troca o padrão de pontos a 6–8 fps, como um xerox ruim. É só textura, nunca chama mais atenção do que o texto.
5. **Curvas de nível desenhadas:** as linhas verdes se traçam de baixo para cima (stroke-dashoffset), como uma plotter.

## Roteiro (15 s, timing em segundos)

| Tempo | Ação |
|---|---|
| 0.0 | Frame 0 já é a capa/gancho: **ÄTZØK** verde + retícula rosa viva na tela (nunca abrir em preto no Reels). |
| 0.4 | **AGENDA** bate em rosa com a tinta verde fora de registro, que encaixa em 2 frames. Flicker #1 em 1.0. |
| 1.2–2.7 | O kicker mono digita letra a letra (2 frames por caractere). |
| 3.0–4.2 | **15.11** entra normal em rosa, segura 0.4 s e então o **risco verde corta da esquerda para a direita** (0.3 s, `power3.out`). A linha desbota para cinza `#5E5E5E` junto com o risco. Esse é o momento de humor do vídeo: a data foi, ficou para trás. |
| 4.2–9.0 | 09.12 → 18.12 → 27.12 → 11.01, uma a cada ~1.2 s, na batida: a data carimba, a festa carimba 3 frames depois e o detalhe mono digita. |
| 9.0–11.0 | As curvas de nível se desenham de baixo para cima e a borda serrilhada fecha a composição. |
| 11.0–13.5 | Respiro: o pôster inteiro parado, só grão e retícula vivos. Flicker #2 no 11.01 (o destaque: a única data de 2027, o barco). |
| 13.6–15.0 | Saída: curvas descem, a tinta some na ordem inversa em blocos (2 frames cada) até sobrar ÄTZØK + retícula = frame 0, para o loop. |

## Critérios de aprovação

- Pausado em qualquer frame depois de 11 s, o vídeo é um pôster imprimível.
- Cada data fica legível por pelo menos 1.5 s antes da próxima entrar.
- Fora o papel, só existem duas cores na tela.
- Nenhum texto fica atrás da UI do Instagram (header em cima, legenda e botões embaixo).
