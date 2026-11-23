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
- **Regra permanente (2026-11-23):** todo post sai em **duas opções**.
  - **A, "Lhama cheia":** segue o `guia-visual.md`, baseado nas referências reais.
  - **B, "Lhama clean":** segue o sistema do carrossel "Onde o clube", que o usuário elogiou por equilibrar o clean com a ID.
  - As duas têm o mesmo texto; só muda o visual. Os detalhes estão em `docs/lhama/guia-visual.md`.

## 3. Entregas feitas

| Data | Entrega | Onde está |
|---|---|---|
| 2026-11-22 | Carrossel "Onde o clube encontra a rave", 6 cards (Houghton, MoDem, Pulsar, Veludo, "Pra ouvir"). Primeira versão em estética própria, feita em outra conversa. | Conversa "Club meets rave movement" |
| 2026-11-23 | Mesmo carrossel refeito na ID da Lhama, 2160×2700, com a mesma legenda | Fonte: `docs/lhama/carrossel-onde-o-clube/`. Pra gerar os PNGs: `node render.js out 2` |
| 2026-11-23 | Reels do carrossel, 1080×1920, 37 s, sem som. HyperFrames, com transições ligando as cenas. | `videos/onde-o-clube/` (edite `gen.py`, rode `python3 gen.py`, renderize). O MP4 não vai pro git. |

| 2026-11-23 | **20 formas da Lhama**, prévia em baixa pra aprovação: topográficas, linhas menta, minhocas 3D, manchas com anéis, rabisco de órbita, pílula e moldura em arco. Vêm da referência `referencias/05-formas-topograficas-minhocas.jpg`. Junto, 3 aplicações: "Quem lhama com a gente?", story "Pra conhecer no UP" e capa "Sabia que o UP…". | Código em `docs/lhama/formas/`. Formas: `python3 gen_formas.py`; PNG: `node render_formas.js <saida> <px>`; grão: `python3 grao.py <in> <out>`; mockups: `node render_aplicacoes.js <pngs> <saida> 0.5`. **Aguardando aprovação.** Depois sai em 4000 px, com e sem grão. |

| 2026-11-23 | **Formas v2**: 10 formas novas (21 a 30) e variações de cor, 96 PNGs no total, em prévia baixa. O usuário tinha gostado da v1 ("tem um bom caminho") e pediu mais cores e mais formas. | Mesmo gerador; paletas em `TOPO_PAL`, `WORM_PAL` e `LINE_PAL`; variações em `VARIANTS` (arquivos `NN-nome--cor.svg`). Aprovado. |

| 2026-11-23 | **Formas em alta, entregues:** o usuário aprovou tudo ("quero tudo"). São 96 PNGs transparentes, 4000 px, 300 dpi, sem grão, em 4 zips por família, mais `textura-grao-4000px.png` (cinza 50% pra usar no modo Sobrepor, com máscara de corte). Com grão embutido, cada PNG passaria de 10 MB e o pacote de 1 GB, por isso o grão foi separado. | Pra gerar de novo: `node render_formas.js <saida> 4000` |

| 2026-11-23 | **PDF de direcionamento visual**, 18 páginas em 16:9, pra apresentar à dona da Lhama. Páginas: capa, o que é a Lhama, logo, mascote, paleta, tipografia, DNA, linguagens A e B, formas, cores das formas, grão, carrossel, celular, merch pequeno (adesivos, bottons, chaveiro), merch de festival (copo, boné, ecobag), vestir (camiseta, pulseiras), regras e próximos passos. Prévia em baixa enviada. **Versão final entregue no mesmo dia:** a pedido do usuário, saiu tudo de merch e da série do UP, e ficou só a identidade visual. São 15 páginas, 1920×1080, 43 MB. A página 2 usa os serviços do post "O que fazemos?". Cópia leve no repositório: `docs/lhama/direcionamento/lhama-direcionamento-visual.pdf` (3,6 MB). | `docs/lhama/direcionamento/` (`deck.html`, `prep_merch.py`, `render_deck.js`). A pasta de build precisa das formas em 1000 px, dos adesivos, dos cards, dos frames do reels e dos mockups. |

**OmniRoute:** o usuário pediu pra usar o OmniRoute pra economizar. Ele roda em localhost:20128, mas o único provedor é o Gemini, com a chave desativada, e o host da API do Google dá 403. Por isso os mockups foram feitos em código.

**Formas novas (21 a 30):** mancha rasgada (Bad Lhama); lava do Badroom; argolas-confete; fita de ondas com o padrão LHAMAFUNDO; fita dupla; caleidoscópio de lhamas; mini-topos-confete; minhoca em onda longa; fundo de linhas (É booking); adesivo-blob 3D.

**Paletas:** lavanda, rosa, menta, amarelo, vinho, violeta, grafite. As fitas usam os fundos azul, amarelo e preto.

**Histórico das formas:**
- Numa conversa paralela, a v1 ficou "horrível" segundo o usuário, porque tinha formas genéricas, estrela, gota e contorno preto.
- A regra que valeu: seguir só a linguagem das artes (curvas de nível paralelas, minhoca gorda com fio amarelo e camadas deslocadas, manchas com anéis) e tirar as cores dos pixels.

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

## 5. Flyer "Lhama Takeover", 18.12 (em andamento)

**Pedido (2026-11-23):**
- Flyer da festa de 18/12, às 22h, a última do ano, com clima de confraternização.
- Local: Lhama Takeover no **Carmem Bar, Rua Silva Pinto, 429, Bom Retiro, SP**, CEP 01126-010, Instagram @bar.carmem. O endereço aparece igual no BaresSP, no Catraca Livre e numa agenda de jun/2026.
- O site do Atzok lista "Lhama Takeover · Hanky Panky · 18 dez".
- O line-up ainda não foi passado; nos flyers está "line-up em breve".

**3 opções em baixa (4:5) enviadas pra escolha:**
1. **Lhama cheia:** fundo topográfico lavanda, título amarelo com contorno, roda de lhamas num medalhão creme sobre a mancha rosa (a confraternização), argolas-confete e informações em pílulas.
2. **Cartaz Bad Lhama:** manchas rasgadas vinho sobre lavanda, letras creme gigantes com contorno rosa, data em grotesca fina, pílulas rosa e cabeça da lhama.
3. **Lhama clean (versão B):** papel creme, título "Confra da Lhama", grade quando / que horas / onde, lhama no arco nascendo da faixa de ondas e mini-topos-confete.

**Rodada 1 reprovada** ("nenhum ficou bom"). Motivos apontados pelo usuário: sem ideia central (parecia colagem de formas da biblioteca), tipografia e hierarquia confusas, muito igual ao que já tinha sido feito e cores e clima errados (não passava confraternização). **Lição: flyer de festa precisa de UM conceito forte, e não só de aplicar o kit.**

**Rodada 2, conceito "brinde e pista"** (escolhido pelo usuário junto com "foto + intervenção"). Paleta quente de noite, com vinho, ameixa, rosa e amarelo, e hierarquia fixa: chamada, título, data e hora, local, endereço, logo. Arquivo `takeover-1812/flyer-v2.html`.
1. **Disco Lhama:** bola espelhada com feixes de luz, serpentinas e confete, fundo ameixa.
2. **Tim-tim:** duas lhamas brindando, copos com respingo, sol listrado amarelo sobre rosa.
3. **Última pista:** a data gigante "18 / 12" é a imagem, com serpentinas passando pelos números e uma bola pequena.
- O caminho "foto + intervenção" depende de o usuário mandar fotos (do Carmem ou de festas anteriores).

**Rodada 3, retícula:** o usuário mandou 2 referências de design: `referencias/06-halftone-agua.jpg`, cáusticas de água em azul e lima com sombra preta, e `07-halftone-velas.jpg`, duas velas com chama lima e rosa sobre lilás. É uma estética de risografia e meio-tom, com cores azul `#4038C8`, lima `#C4EE6E`, rosa `#EC80DE`, preto e papel. Em `halftone.py`, as imagens são desenhadas por camadas de tinta e impressas com retícula girada por tinta. Em `flyer-v3.html`, a tipografia é enxuta (Adca e DM Mono) e as informações vão em tarjas.
1. **Velas:** "a última do ano, vem brindar", com uma faixa preta embaixo pras informações.
2. **Água:** "LHAMA TAKE OVER" em creme e as informações em tarjas preta, lima e creme.
3. **Bola espelhada em retícula:** "Confra na pista" e as informações em tarjas coloridas.

**Rodadas 3 e 4 reprovadas** ("horrível", "tá ruim"):
- A rodada 3 desenhava imagens novas em retícula, o que o usuário não queria.
- Na rodada 4, as imagens de referência foram recoloridas (`recolor.py`, que mantém os pontos da retícula), mas faltava conceito.

**Pedido do usuário:** "você é um diretor de arte absurdo, caça referências de flyers, usa as texturas que enviei, dica: **taça de martini**".

**Rodada 5, martini** (`martini.py` e `flyer-v5.html`):
- **Conceito:** uma taça de martini gigante como imagem central.
- **Texturas:** o líquido é a textura da água recolorida e o brilho atrás vem das velas recoloridas.
- **Detalhes:** sombra rosa de registro deslocada, azeitona rosa com miolo amarelo no palito, contorno de nanquim e tipografia editorial grande.

As três opções:
1. **"LHAMA":** taça frontal sobre lavanda, com o brilho das velas atrás.
2. **"A última dose do ano":** taça inclinada derramando a água sobre fundo preto.
3. **"Tim-tim":** duas taças brindando sobre rosa, com o líquido das velas nas duas versões de cor.

**Pesquisa de referência:** cartazes de riso com duas tintas e erro de registro, e o motivo da taça de martini com tipo editorial grande em campo de cor chapada.

**Rodada 6, "a saideira":** o usuário gostou da ideia da 1ª e da 3ª da rodada martini, mas "ainda não ama". Sugeriu o mote "a saideira". Arquivos: `flyer-v6.html` e as funções `s1` a `s3` em `martini.py`.
1. **"A saideira":** uma taça só com pouca bebida (a última dose), sobre lavanda com o brilho das velas.
2. **"Bora pra saideira?":** duas taças brindando sobre rosa.
3. **12 taças, uma por mês:** onze vazias e a de dezembro cheia, com a azeitona. Papel creme, na versão clean.

**Rodada 7, menos literal** (pedido: "não precisa ser tão literal, o design ainda não tá tão bom, você consegue mais"). Arquivo `flyer-v7.html`; as fontes novas (Instrument Serif itálico e Big Shoulders, licença OFL) estão em `flyers/fonts/`.
- **Princípios:** a textura é a imagem, a taça vira forma, e a tipografia combina Adca com uma serifa itálica, que dá voz de convite.
1. **Recorte:** a água ocupa o fundo inteiro e a taça é um vazio de papel creme recortado. "a saideira" em serifa itálica e as informações numa grade embaixo.
2. **Chama:** close abstrato das velas, recoloridas em tons de noite. "SAIDEIRA" gigante na vertical e o texto "a última do ano, com quem ficou até o fim".
3. **A invertido:** o A triangular da Adca virado de cabeça pra baixo com haste vira a taça em "SAIDEIRA". A textura da água vem rosa e vinho embaixo, e as informações num cartão creme.

**Rodada 8, refs novas.** O usuário mandou mais 3 referências:
- `referencias/08-glow-nuclear-blunt.jpg`: tipo verde em brilho com eco de movimento.
- `09-duotone-intended.jpg`: foto em duotone roxo e verde dentro de uma moldura, globo com o nome e código de barras.
- `10-halftone-tropic-session.jpg`: tipo gigante em retícula grossa amarela sobre preto, explosão de luz em spray no centro e tags contornadas.

**Direção que essas refs apontam:** fundo escuro, UMA tinta luminosa, tipo como imagem e informação pequena e técnica. Tudo é renderizado em `noite.py`, sem HTML.
1. **Amarelo:** "SAIDEIRA" e "LHAMA TAKEOVER" em retícula grossa amarela, explosão de luz no meio, tags 18.12 e 22H, seta e Carmem Bar.
2. **Rosa:** brilho rosa com eco de movimento, como numa tela de TV, e as informações empilhadas.
3. **Velas:** a foto das velas em duotone lavanda e menta dentro de uma moldura, "SAIDEIRA" em lavanda, o globo com "LHAMA TAKEOVER", o código de barras "LT-1812" e as informações nos cantos.

**Rodada 9:**
- O mote "saideira" foi **abandonado** a pedido do usuário ("gastou demais nisso, não ficou bom"). O título é só **LHAMA TAKEOVER**.
- O usuário gosta dos 3 estilos da rodada 8, mas "falta o martini". Por isso a taça entrou nos três (`noite.py`):
  1. **Amarelo:** a taça em retícula na frente da explosão de luz.
  2. **Rosa:** a taça em neon no meio.
  3. **Velas:** a foto das velas em duotone dentro de uma taça gigante com contorno menta.

**Rodada 10:**
- O usuário escolheu a **opção amarela** (tipo em retícula com explosão de luz) e pediu variações com uma **taça mais realista e detalhada**. Também achou feio o efeito de antes, a taça chapada.
- A nova taça é renderizada de verdade e depois impressa em retícula fina. Arquivo: `martini_real.py`.
- Detalhes da taça: vidro com bordas claras e reflexos, líquido com menisco, azeitona com pimentão, palito, haste e pé.

As três variações:
1. **t1:** taça grande de frente, com "LHAMA" em cima, "TAKEOVER" embaixo e tags nos cantos.
2. **t2:** taça inclinada e grande à direita, com o tipo empilhado à esquerda e tags embaixo.
3. **t3:** duas tintas (amarelo e rosa no líquido, deslocado como erro de registro), com "LHAMA TAKEOVER" numa linha e data grande.

**Arquivos:** `docs/lhama/flyers/takeover-1812/flyer.html`, da rodada 1. Pra renderizar: `node docs/lhama/flyers/render_flyer.js <flyer.html> <formas-png> <saida> <escala>`, com as formas geradas em 1000 px.

## 6. Merch "anúncio clássico" (paródia de maço de cigarro dos anos 90), em andamento

**Pedido (2026-11-23):**
- Brincar com o logo de uma marca de cigarros: palavra em arco e o desenho do animal embaixo, só que com a lhama.
- Fazer ilustrações no estilo airbrush dos anúncios dos anos 90, com o personagem de smoking branco.
- As referências estão em `referencias/11` a `14-merch-camel-ref`.

**Decisões pra não copiar marca registrada:**
- O lettering é o da própria Lhama (Adca em arco), não a fonte deles.
- A silhueta da lhama foi desenhada do zero.
- Sem "since 1913" e **sem cigarro**: no lugar entram a taça de martini e o DJ.

**Rascunho em `docs/lhama/merch/lhama-camel/merch.html`:**
- **l1:** logo amarelo sobre azul-noite.
- **l2:** logo marrom sobre mostarda, com "Música psicodélica brasileira".
- **i1:** a cabeça da lhama da marca sobre um smoking branco, com sombra de palmeira e uma taça na mão.
- **i2:** "LHAMA" em arco sobre céu roxo, a lhama de smoking na cabine de DJ.

**Limitação:**
- A ilustração airbrush de verdade precisa de um gerador de imagem ou de um ilustrador.
- O Canva está sem crédito ("credit quota exceeded").
- No Figma, a conta tem só um assento de visualização, no plano Starter.

## 7. Outras ideias e anotações soltas

- O "COISAS PARA PENSAR" da planilha BOOKINGS: lugares em SP, agenda de dezembro, festas de fim de ano (inclusive de lojas), raves fora de SP no ano que vem.
- Conversas anteriores relacionadas ao Atzok, que são outras sessões: "DJ booking na cena underground", "Carrossel Instagram Ätzøk", "Agenda motion video", "Conteúdo de produção musical em cards".
