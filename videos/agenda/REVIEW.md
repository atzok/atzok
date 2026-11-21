# Review — ÄTZØK Agenda (Dez 26 → Jan 27)

Render: `renders/atzok-agenda-dez26-jan27.mp4` (master, 81 MB) e `renders/atzok-agenda-dez26-jan27-ig.mp4` (H.264 CRF 25, 23 MB, para upload). 1080×1920, 30 fps, 15 s, sem áudio (pedido).

## Decisões
- Frame 0 = ÄTZØK + retícula (gancho/capa), e o vídeo termina nesse mesmo estado: loop sem corte. O brief original abria em preto; mudou para não ter capa vazia no Reels.
- Cinza do item passado clareado de #5E5E5E para #707070 para passar contraste 3:1 no papel #171717.
- Curvas de nível entram como scan de plotter (clip-path em 32 passos) em vez de traço por linha: o SVG tem milhares de segmentos curtos, e dashoffset neles não leria como desenho.
- Grão troca a cada 2 frames e retícula a cada 4; offsets vêm de um gerador com semente fixa (render determinístico).

## Medido
- `check --safe-zone reels`: ok. Avisos mantidos: topo do ÄTZØK acima da faixa segura do Reels (layout aprovado pelo usuário); 12 elementos na cena; sem áudio (pedido).
- Snapshots em 0, 0.43, 0.47, 3.2, 14.1 e 14.97 s: tinta fora de registro visível, risco no 15.11, saída em blocos, último frame = primeiro.

## Mais fraco
- 9–13.5 s: o pôster fica parado (respiro do brief, marcado com `data-hold`), só grão, retícula e 2 flickers. Se parecer longo no celular, encurtar o vídeo para 13 s.
