# Guia de estilo do perfil: cannabis medicinal

Este guia vale para todo post, story e capa de destaque do perfil. Ele foi tirado do primeiro carrossel (`01-um-milhao`), que deu certo.

## Tom de voz

- **Opinião com dado.** O perfil é a favor do acesso à cannabis medicinal e diz isso sem rodeio. Toda opinião vem apoiada num número ou num fato com fonte.
- **Fala como gente.** Usa minúsculas, frases curtas e o jeito de falar do dia a dia: "salva", "manda pra quem precisa", "gostoso demais!".
- **Um título que dá um soco.** É uma frase curta com uma palavra de destaque em laranja ("quem cobra menos é quem mais **apanha.**").
- **Uma frase em itálico que vira a chave.** Vem logo depois do título, em tom de comentário ("falta o Estado *acompanhar.*").
- **Alvo certo.** A crítica vai para o Estado, o Congresso e o preconceito. Nunca para o paciente, a família ou o médico.
- **Nada de "liberou geral".** Falamos de saúde, acesso e direito. Não fazemos apologia ao uso recreativo.
- **Sem conselho médico.** Explicamos as regras e os caminhos de acesso, mas dose e tratamento são sempre com o médico. Posts sobre saúde levam o aviso "este post informa, não substitui consulta médica".
- **Números com fonte.** Todo número tem a fonte no rodapé do slide e na legenda. Se o dado for incerto, ele fica de fora.

### Frases da casa
- "salva · compartilha · manda pra quem precisa": encerramento padrão
- "perspectiva crítica", "precisamos lembrar sua história", "mas afinal, o que é…?": selos de série
- "defenda o acesso, gostoso demais!"

## Paleta

| Nome | Hex | Uso |
|---|---|---|
| verde fundo | `#304E3C` | fundo principal |
| tinta | `#1E3227` | texto escuro, fundo dos slides sérios |
| musgo | `#3C5B37` | apoio |
| mata | `#4E6F59` | linhas divisórias |
| laranja | `#E86D3C` | destaque, estrela, palavra-chave |
| sálvia | `#B9C6AF` | fundo claro, itálicos sobre verde |
| creme | `#F5E7D6` | papel rasgado, texto claro |
| lilás | `#C8B2F0` | acento (no xadrez, em capas e em séries) |

Regra: no máximo **três cores por slide**. O laranja é sempre o destaque.

## Tipografia

- **Títulos:** Bricolage Grotesque 800, em minúsculas e com espaçamento entre letras apertado. Siglas e nomes próprios (CBD, THC, STF, Anvisa, Brasil) usam `class="sigla"` para manter a maiúscula.
- **Comentário:** Fraunces itálico, que aparece no selo arredondado, na frase-chave e no rodapé de fontes.
- **Corpo:** Bricolage 600, com no mínimo 36px no slide.

## Elementos gráficos

Os elementos estão em `base/decor.js` e são ativados por uma classe ou um `data-` no HTML:

- `.burst` → selo em formato de estrela (`data-points`, `data-inner`)
- `.torn` → papel rasgado (bordas irregulares)
- `.leafrow` → faixa de folhas no topo ou no rodapé
- `.leaf.halftone` → folha com efeito de retícula
- `.checker` → faixa xadrez de duas cores (`data-a`, `data-b`)
- `.pill` → selo arredondado em itálico
- `mark` → marca-texto laranja
- `.linha` → linha do tempo ou lista com rótulo em laranja

Não usamos foto de pessoa real sem autorização. Quando a referência pedir retrato, usamos a folha com retícula ou um recorte de papel.

## Estrutura do carrossel

1. **Capa:** selo de série + título-soco + frase em itálico no papel rasgado + "arrasta →"
2. **Dado principal:** um número gigante em laranja
3–N. **Um argumento por slide.** Se o texto não couber em 3 linhas, vira outro slide
4. **Último slide:** a estrela, a frase-manifesto e "salva · compartilha · manda pra quem precisa"

Todo slide leva `@seuperfil` no canto esquerdo e `n/total` no canto direito.

## Formatos

| Formato | Tamanho | Classe | Área segura |
|---|---|---|---|
| Feed (carrossel) | 1080×1350 | `.slide` | margem de 72px |
| Story | 1080×1920 | `.story` | deixar livres os 250px do topo e os 340px de baixo |
| Capa de destaque | 1080×1920 | `.story` | símbolo dentro do círculo central de ~600px |

## Como fazer um post novo

1. Copie uma pasta parecida (por exemplo `02-cbd-thc`) para `NN-tema`.
2. Edite o `carrossel.html`, que já usa `../base/estilo.css` e `../base/decor.js`.
3. Renderize os PNGs:
   ```bash
   node render.js NN-tema
   ```
4. Escreva o `legenda.txt`: gancho, 2 ou 3 parágrafos curtos, chamada para ação, fontes e hashtags.
