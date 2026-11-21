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
- **Fontes**: são provisórias, porque a fonte oficial ainda não foi definida e não existe `./assets/fonts`. Escolhi duas do Google Fonts e salvei os arquivos em `cards/src/fonts/`:
  - **Archivo** (variável, condensada a 62%, peso 800–900): títulos e números. Grotesca condensada e pesada, com acentos bem desenhados e vários pesos.
  - **Archivo** em largura normal, peso 400–500: texto de apoio.
  - **Space Mono 400/700**: kicker, rótulos e rodapé. Já aparece nas peças web do Ätzøk.
- **Fotos**: nenhuma, o carrossel é só tipográfico. Uma foto de pista xerocada na capa ou no card 2 cairia bem, se você tiver.
- **Cor de destaque**: `#F2E300`. O design system do repositório (`docs/figma-design-system-rules.md`) usa ember (`#BC6D21`) como destaque, mas o briefing pediu amarelo ácido (L4/AMARELA). Se o amarelo virar oficial, vale registrar como token.

## Decisões de design
**Versão 2 (minimalista).** A primeira versão (estilo zine, com escorridos gerados por script) foi reprovada. Os escorridos pareciam palitos e o conjunto ficou carregado. Nesta versão:
- **Grid fixo**: 1080×1350, margem de 96px. No topo, o kicker com a paginação ("02/10 · DETROIT") e um dado à direita, acima de um fio. No rodapé, também acima de um fio, a assinatura (logo + @_atzok) e o "arrasta →". O título fica sempre no alto e o texto de apoio sempre embaixo.
- **Sem escorridos gerados**: a única tinta que escorre é a do próprio logo pichado, no rodapé de todos os cards e grande no card 10.
- **Textura**: só uma granulação leve de papel. Tirei as manchas de xerox, as listras de toner, a retícula, a fita e o papel rasgado.
- **Uma cor de destaque por card**: o amarelo aparece num único elemento por card ("quem?" na capa, a data, a citação, o risco dos clubes, o ponteiro do rádio, o número ou as palavras-chave).
- **Ritmo**: o card 5 inverte as cores (papel claro, texto preto) para quebrar a sequência no meio. O card 8 é só o número.
- **Texto (versão 3)**: a versão anterior só repetia as notícias e soava como IA. Antes de reescrever, perguntei a sua opinião em 4 pontos:
  - **Detroit** e **Helsing**: você preferiu deixar sem opinião. Esses cards ficaram só no fato.
  - **"O público segue marcas e DJs"**: "vejo, e é foda". Virou o bloco assinado do card 5.
  - **GTA e IA**: GTA tudo bem, IA não. Virou os blocos assinados dos cards 6 e 7.
  - A opinião aparece num bloco com o logo e uma borda amarela, separado da notícia.
  - Saíram as frases que eu tinha inventado, como a do "carro roubado".
  - O card 9 agora amarra as notícias: Detroit é memória; Berlim, os clubes e o GTA são capital; o Deezer é máquina.
  - Os textos dos blocos usam as opções que você marcou, que eu mesmo escrevi. Se quiser, troca pelas suas palavras.
- **Legibilidade**: o texto de apoio tem 38px (uns 14px na tela do celular). O kicker tem 26px e o rodapé 22px. Revisei os 10 PNGs no tamanho real: nenhum texto vazando e nenhum acento colidindo. O `render.js` confere automaticamente se o conteúdo estoura o card ou se dois blocos ficam colados.

## Como regerar
```
cd cards/src && node render.js && python3 contact.py
```
O texto se edita direto em `cards/src/cards.html`.

## Não publicado
Nada foi postado nem agendado em nenhuma rede. Os arquivos estão só na branch `claude/youthful-tesla-9k7yfz`.
