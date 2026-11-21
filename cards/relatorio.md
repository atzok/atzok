# Relatório: carrossel "A pista é de quem?"

## Atenção: a resenha não estava no repositório
`./resenha.md` não existe (procurei na raiz, no repositório inteiro e nas outras branches). Escrevi os cards **só com os fatos do seu briefing**, card a card, sem acrescentar nada. Se a resenha tiver detalhes que mudam algum card (datas, nomes, o que o SoundCloud fez de fato), me manda que eu ajusto.

## Fontes
As que o briefing cita, repetidas em `legenda.txt`: Resident Advisor, DJ Mag, CDM, Billboard, We Rave You e OkayAfrica. Não abri essas matérias: tudo veio do briefing. Falta conferir os links.

Pontos para conferir:
- **Card 8 (97%)**: o briefing diz que a IA fica com 1–3% das execuções, então a parte humana vai de 97 a 99%. Usei 97%, que é o piso, como você pediu.
- **Card 7**: "o SoundCloud já reagiu". O briefing não diz como, então não detalhei.
- **Card 3**: a única citação é "grave erro de julgamento" (4 palavras, do briefing). O resto é paráfrase.

## Placeholders e o que trocar
- **Logo**: usei o **wordmark pichado real** (`videos/apresentacao/assets/wordmark-branco.png`, copiado para `cards/src/img/`). Não é placeholder. Se existir uma versão vetorial ou em amarelo, dá pra trocar.
- **Fontes**: são provisórias, porque a fonte oficial ainda não foi definida e não existe `./assets/fonts`. Escolhi três do Google Fonts e salvei os arquivos em `cards/src/fonts/`:
  - **Anton**: títulos (condensada e pesada, com cara de lambe-lambe).
  - **Big Shoulders Stencil Display 900**: números (90 mil, 97%) e o carimbo, puxando pro estêncil.
  - **Space Mono 400/700**: kicker, corpo e rodapé. Já aparece nas peças web do Ätzøk.
- **Fotos**: nenhuma, o carrossel é só tipográfico. Uma foto de pista xerocada na capa ou no card 2 cairia bem, se você tiver.
- **Cor de destaque**: `#F2E300`. O design system do repositório (`docs/figma-design-system-rules.md`) usa ember (`#BC6D21`) como destaque, mas o briefing pediu amarelo ácido (L4/AMARELA). Se o amarelo virar oficial, vale registrar como token.

## Decisões de design
- **Grid fixo**: 1080×1350, margem de 88px. O kicker com a paginação ("02/10 · DETROIT") fica sempre no mesmo lugar, no topo. A assinatura (logo + @_atzok) e o "arrasta →" ficam sempre no rodapé, acima de um fio.
- **Textura**: granulação e manchas de fotocópia (ruído SVG), listras de toner nas laterais, retícula e, na capa, tira de papel rasgado com fita adesiva.
- **Escorridos**: gerados por script, saindo só das letras da última linha de cada título. O comprimento para antes do próximo bloco de texto, com 28px de folga. O `render.js` confere se algum escorrido passa por cima de texto e se algo sai da área segura.
- **Uma cor de destaque por card**: o amarelo aparece num único elemento por card (tira da capa, data, carimbo, risco dos clubes, número ou palavras-chave).
- **Ritmo**: o card 5 inverte as cores (papel claro, texto preto) para quebrar a sequência no meio. O card 8 é só o número.
- **Texto**: segui a skill `voz-atzok` (que está na branch `claude/confident-knuth-0jsaa1`). Sem travessão, sem moral no fim de cada card, e opinião só no card 9, tirada do seu briefing. A frase do card 6 ("o som da pista virou trilha de carro roubado") é comentário editorial meu; se não soar como você, eu corto.
- **Legibilidade**: o corpo de texto tem 35px (uns 12–13px na tela do celular). Kicker e rodapé têm 25–28px. Revisei os 10 PNGs no tamanho real: nenhum texto vazando, nenhum acento colidindo e nenhum escorrido cobrindo letra.

## Como regerar
```
cd cards/src && node render.js && python3 contact.py
```
O texto se edita direto em `cards/src/cards.html`.

## Não publicado
Nada foi postado nem agendado em nenhuma rede. Os arquivos também não foram commitados no git.
