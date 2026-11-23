# Memória — Lhama Bookings

Arquivo de memória de tudo o que envolve a Lhama Bookings. O usuário é booker da Lhama e concentra os assuntos da Lhama numa conversa só, onde os temas se misturam. **Leia este arquivo antes de qualquer trabalho da Lhama e atualize-o ao fim de cada entrega ou decisão.**

Dados pessoais e comerciais dos artistas (CPF, endereço, e-mail, cachê) ficam só nas planilhas do Drive, nunca aqui.

---

## 1. Contexto

- **Lhama Bookings:** agência de booking da cena eletrônica underground (psy, prog dark, forest, techno, house, downtempo). Opera com artistas de SP, BH, RJ, Campinas, Itacaré, Brasília.
- **Usuário:** booker da Lhama. Também trabalha com o Ätzøk (Caio Costa), artista da Lhama e dono deste repositório (`atzok/atzok`).
- **Fontes no Drive** (compartilhadas com o usuário, somente leitura):
  - `ID VISUAL`, pasta da identidade (id `1D1g3CvxoUFjGb6R5Jvr4ah_l6mo-1c6k`).
  - `ARTISTAS LHAMA`, planilha com projetos, nomes, coletivos, estilos e cidades (id `1M3BMNo0arG6qDhxapik6aZKGx_dk4lys_EkJ-zUCjWc`).
  - `BOOKINGS LHAMA`, planilha de bookings, cachês, presskits e "coisas para pensar" (id `1KkSHAiBCExORtKeKfBh49d40wtEi5Bw-JaLKP60DyDE`).
  - `[release] brand new whirled`, presskit do Brand New Whirled, projeto de prog dark do Luiz Inaimo (Trippy Jungle Records).

## 2. Identidade visual da Lhama

Arquivos da pasta ID VISUAL: os logos `LHAMA-CT`, `-CCT`, `-P` e `-PB`; a cabeça `LHAMA-HEAD` (também em `-P`); a lhama no arco sem texto `LHAMA-SOLTA`; os nomes `LHAMA-NOMECC` e `-NOMEPB`; a `lhama espiral`; os fundos `LHAMAFUNDO-AMARELO`, `-AZUL` e `-PRETO` (padrão de ondas espelhadas); `LHAMA-WAVES1`, de 29 MB; o selo "Música Psicodélica Brasileira" e seu card expandido com linhas topográficas; e a fonte `Adca.ttf`.

- **Mascote:** lhama desenhada à mão com fone de ouvido azul, coleiras rosa e azul, bandana preta e branca e arco-íris psicodélico atrás.
- **Logo:** "LHAMA" em letras de bloco com A triangular, lavanda com sombra rosa deslocada (efeito de erro de registro), e "BOOKINGS" escrito à mão.
- **Paleta:**

| Cor | Hex |
|---|---|
| Lavanda | `#6A75F2` |
| Lilás | `#BCC2F6` |
| Rosa | `#EE69DA` |
| Amarelo | `#EDF06F` |
| Menta | `#9EDAA3` |
| Azul-céu | `#74B4D4` |
| Bege-lã | `#E6DFCD` |
| Papel/creme | `#F4EFE2` |
| Tinta | `#151515` |

- **Tipografia:** Adca nos títulos. Ela não tem travessão (–), então datas usam hífen. DM Mono nos rótulos.
- **Sistema de card que funcionou** (aprovado pelo usuário com "amei"):
  - papel creme com grão;
  - cabeçalho em mono com bolinha rosa, contador "n / 6" e linha preta;
  - títulos em Adca com a palavra de destaque em lavanda e sombra rosa de 0,045 em;
  - faixas de ondas da marca na base;
  - ilustrações da lhama no lugar das ilustrações genéricas;
  - cor de fundo alternando por card: creme, lavanda, amarelo, preto.
- Filosofia escrita: `docs/lhama/carrossel-onde-o-clube/filosofia.md` ("Fanzine Tropodélico").

## 3. Entregas feitas

| Data | Entrega | Onde está |
|---|---|---|
| 2026-11-22 | Carrossel "Onde o clube encontra a rave", 6 cards (Houghton, MoDem, Pulsar, Veludo, "Pra ouvir"). Primeira versão em estética própria, feita em outra conversa. | Conversa "Club meets rave movement" |
| 2026-11-23 | Mesmo carrossel refeito na ID da Lhama, 2160×2700, com a mesma legenda | Fonte: `docs/lhama/carrossel-onde-o-clube/`. Pra gerar os PNGs: `node render.js out 2` |
| 2026-11-23 | Reels do carrossel, 1080×1920, 37 s, sem som. HyperFrames, com transições ligando as cenas. | `videos/onde-o-clube/` (edite `gen.py`, rode `python3 gen.py`, renderize). O MP4 não vai pro git. |

**Pendência do reels:** falta trilha. A ElevenLabs recusa a chave porque o proxy envia `Authorization: Bearer` e ela espera `xi-api-key`. O usuário precisa ajustar o header do segredo em Network secrets. Também pode mandar uma faixa própria.

**Card 5 do carrossel:** a Dona Sinistrus e a Diza aparecem com sets, não com faixas lançadas. O usuário decidiu deixar assim.

## 4. Série Universo Paralello (brainstorm de 2026-11-23, em andamento)

**Ideia do usuário** (áudio transcrito):
- Contar por que o Universo Paralello (UP) é importante pra cultura raver e como ele vai além da rave: tem pista de tudo.
- O ponto de vista é que **misturar é legal**: um festival com várias opções e vários públicos é bom pra cena e bom pros artistas da Lhama, porque um público diverso conhece gente nova.
- O usuário acha que o UP é dominado pelo psytrance ("low", nas palavras dele, sentido ainda a confirmar), mas valoriza que tem de tudo.
- **Não pode parecer que a Lhama fechou todo mundo.** O tom é "conheça", e não "nossos artistas".

**Estrutura combinada:**

| Dia | Post |
|---|---|
| 1 | **Post geral:** a importância do UP e a mistura de pistas. No fim, os artistas da Lhama que tocam lá, só com o nome e a pista, sem descrição. Carrossel e reels. |
| 2 a 6 | **Um post por artista, em collab no Instagram**, pra usar o público de cada um. Conteúdo vem do próprio artista: o que vai tocar (gêneros e clima), a importância pra carreira, o que acha do UP e se já foi. Carrossel de 3 a 4 cards. |
| 7 | **Guia da Lhama no UP:** quem toca, quando e onde. |

- Uma semana inteira só sobre o UP, valorizando quem toca lá.

**Mensagem pros artistas** (rascunho entregue ao usuário):
1. O que você vai tocar: gêneros e clima.
2. O que essa apresentação significa pra sua carreira.
3. O que o UP representa pra você, se já foi e alguma história de lá.
4. Seu set em uma frase.
- Pedir também 2 ou 3 fotos e confirmar pista, dia e horário. Pode responder em áudio.

**Fluxo de trabalho proposto pelo usuário:**
1. O usuário monta um quadro de referências visuais.
2. Claude analisa o quadro e escreve um guia visual da série, com um modelo de card reaproveitável na ID da Lhama.
3. A cada post, o usuário manda o texto ou as ideias, e Claude melhora o texto e o design a partir das referências.

**Quadro de referências:**
- 2026-11-23: o usuário mandou 4 posts reais da Lhama ("O que fazemos?", "Bad Lhama in the Veludo Room", "Badroom", "Sabia que as lhamas não gostam de andar sozinhas?").
- As imagens estão em `docs/lhama/referencias/`.
- A análise e as regras da série estão em **`docs/lhama/guia-visual.md`**, que vale mais que o sistema do carrossel "Onde o clube".
- Resumo da análise: fundo cheio de padrão, grão forte, texto com contorno, texto sobre pílulas e barras de marca-texto, mascote usado como brinquedo (caleidoscópio) e voz com pergunta-gancho.

**Line-up da Lhama no UP:**

| Artista | Pista | Data | Status |
|---|---|---|---|
| Ätzøk | Chillout Stage | 27 dez | Está no site do Atzok |
| "Tropicalin" | ? | ? | Nome pouco claro na transcrição |
| Mavie (Veludo, BH) | "UP Club"? | ? | A confirmar |
| Outros | ? | ? | ? |

- **Pelas planilhas, já tocaram no UP:** At Work / Quirky Cabronz / Nutella Volcano (Guilherme, Random Records: "3 Universo Paralello") e Hongos Longos / Nutella Volcano (Jonas Coutinho: "UP").

**Perguntas em aberto pro usuário:**
1. Line-up completo da Lhama no UP, com pista e dia.
2. O que quis dizer com "low".
3. Datas de publicação da série. Sugestão: até meados de dezembro.
4. ~~O quadro de referências~~ (recebido).

**Próximo passo de Claude:** pesquisar a história do UP com fontes (edições, local em Pratigi/Ituberá-BA, pistas) e rascunhar o texto do post geral.

## 5. Outras ideias e anotações soltas

- O "COISAS PARA PENSAR" da planilha BOOKINGS: lugares em SP, agenda de dezembro, festas de fim de ano (inclusive de lojas), raves fora de SP no ano que vem.
- Conversas anteriores relacionadas ao Atzok, que são outras sessões: "DJ booking na cena underground", "Carrossel Instagram Ätzøk", "Agenda motion video", "Conteúdo de produção musical em cards".
