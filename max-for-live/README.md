# Devices Max for Live (Live 9.2.7+)

Quatro devices `.amxd` feitos para o **Live 9 com Max 6.1**. Também devem abrir no Live 10, 11 e 12.

| Device | Tipo | O que faz |
|---|---|---|
| `Acordes.amxd` | MIDI Effect | Cada nota vira um acorde. 3 vozes com intervalo de -24 a +24 semitons, liga/desliga por voz e presets (Maior, Menor, 7ª, Sus4, Quinta, Diminuto). |
| `Escala.amxd` | MIDI Effect | Puxa qualquer nota para a escala escolhida: Maior, Menor, Harmônica, Dórico, Frígio, Mixolídio, Pentatônicas, Blues. Com 12 tônicas. |
| `Stutter Gate.amxd` | Audio Effect | Corta o som no ritmo do Live (1/4 até 1/32, com tercinas). Tem controle de duração e de profundidade. |
| `Modulador.amxd` | Audio Effect | **Hack de Live API:** um LFO que mexe sozinho em *qualquer* knob do Live, de qualquer device ou faixa. Formas: seno, triângulo, serra, quadrada e aleatória. |

## Como instalar

1. Copie a pasta `devices/` para a sua User Library, por exemplo `Documentos/Ableton/User Library/Max for Live/`.
2. No Live, arraste o `.amxd` para uma faixa:
   - **Acordes** e **Escala** vão numa faixa MIDI, **antes** do instrumento.
   - **Stutter Gate** e **Modulador** vão em qualquer faixa de áudio ou depois de um instrumento.

## Como usar o Modulador

1. Clique em qualquer knob do Live (um filtro, o volume de uma faixa, um send...).
2. Clique em **Map** no Modulador. O nome do parâmetro aparece no device e o knob fica cinza: agora quem controla é o LFO.
3. Ajuste **Hz** (velocidade), **Quant.** (quanto mexe) e **Centro** (em volta de que ponto mexe).
4. Clique em **Solta** para devolver o knob ao controle normal.

> Limitação: o mapeamento não fica salvo no set. Ao reabrir o projeto, faça o Map de novo.

## Se o Live recusar abrir algum arquivo

Os arquivos foram gerados por script e **não foram testados dentro do Live**. Se algum der erro:

1. Arraste o device mesmo assim e clique no botão **Edit** (abre o editor do Max).
2. No Max, salve com `Ctrl+S` / `Cmd+S`. O Max regrava o arquivo no formato dele e isso costuma resolver.
3. Se continuar com erro, copie a mensagem da janela **Max Window** e me mande.

## Gerar de novo / modificar

```bash
python3 gerar.py
```

Cada device é uma função em `gerar.py`. Dá para mudar presets, escalas, divisões rítmicas ou criar devices novos a partir dessas funções.
