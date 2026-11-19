# Estratégia de busca e navegação 

Responsável: Pessoa A. Código em `backend/search.py`, testes em `tests/test_search.py`. O módulo só usa a biblioteca padrão do Python e não depende de HTTP.

## Funções

| Função | Para quê |
| --- | --- |
| `search_services(records, query, topic="all")` | Assinatura fixada pelo grupo. Devolve as orientações, da melhor para a pior. É o que `GET /services` chama. |
| `score_services(records, query, topic="all")` | Mesma busca, mas devolve `ScoredService(record, score, matched_terms, coverage)`. **O módulo de respostas deve usar esta**, para saber se há empate. |
| `find_ties(ranked)` | Resultados com pontuação a até 20% da melhor (candidatos a "ambíguo"). |
| `build_topic_tree`, `build_graph`, `related_services`, `navigation_path` | Hierarquia e grafo (seção "Navegação"). |

## Como a busca funciona

1. **Normalização**: minúsculas, sem acentos, pontuação vira espaço (`CadÚnico?` vira `cadunico`). A consulta e os campos da base passam pela mesma função, então maiúsculas e acentos não mudam o resultado.
2. **Palavras úteis**: saem palavras vazias ("como", "para", "preciso", "onde", "fui", "me"...) e palavras de uma letra. Os plurais são reduzidos (`vagas` vira `vaga`, `documentos` vira `documento`), dos dois lados.
3. **Sinônimos**: uma tabela curta (`ALIASES`) acrescenta termos quando uma expressão aparece na pergunta. Exemplos: `cad unico` leva a `cadunico`; `demitido` leva a `desemprego` e `demissao`; `titulo de eleitor` leva a `titulo` e `eleitoral`. Para um novo sinônimo, basta uma linha na tabela.
4. **Pontuação**: cada termo da pergunta vale o peso do **melhor campo** em que aparece: título 4, palavra-chave 3, órgão 1,5, resumo 1. Há bônus para expressões inteiras: palavra-chave com várias palavras presente na pergunta (+3), título completo na pergunta (+6) e título exatamente igual à pergunta (+20).
5. **Candidato válido**: a orientação só entra se pelo menos um termo aparecer no título, nas palavras-chave ou no órgão. Uma palavra que só existe no resumo nunca gera resposta sozinha.
6. **Cobertura mínima**: a orientação precisa cobrir pelo menos 60% das palavras úteis que a pessoa escreveu. Isso evita que "como tirar carteira de motorista" retorne a Carteira de Trabalho só por causa de "carteira". Os sinônimos só ajudam: a cobertura é medida contra as palavras escritas.

## Várias correspondências e empates

A ordenação é **determinística**: maior pontuação, depois mais termos encontrados, depois a ordem do arquivo. Em empate, a ordem do arquivo decide, mas o empate **não é escondido**: `find_ties` o revela, e o módulo de respostas deve tratá-lo como pergunta ambígua e oferecer as opções.

Exemplos reais com a base atual:

| Pergunta | Resultado (id, pontos) | Leitura |
| --- | --- | --- |
| `documento` | cpf 3, identity 3, voter 3 | Empate triplo: ambíguo. |
| `carteira` | identity 4, work-card 4 | Empate: ambíguo. |
| `Bolsa Família` | family-benefit 8 | Vencedor claro. |
| `fui demitido` | unemployment 10, fgts 3 | Vencedor claro; FGTS aparece como alternativa. |
| `Como tirar carteira de motorista?` | (vazio) | Fora da base. |
| `Qual a previsão do tempo?` | (vazio) | Fora da base. |

## Consulta vazia, tema e entradas inválidas

- **Consulta vazia** (ou só espaços e pontuação): devolve todas as orientações do tema, na ordem do arquivo, como o contrato da API pede (`topic=all` lista tudo).
- **Consulta só com palavras vazias** (por exemplo "como"): devolve lista vazia, porque não há o que procurar.
- **Sem correspondência**: lista vazia, nunca um erro e nunca uma orientação "aproximada".
- **Tema**: `all`, `documents`, `work` ou `social`. O filtro é feito dentro da função. Tema inválido ou consulta que não seja texto geram `ValueError`.

## Navegação (hierarquia e grafo)

- **Hierarquia de dois níveis**: tema (`documents`, `work`, `social`) e, abaixo, as orientações dele (`build_topic_tree`). Serve para o menu por tema.
- **Grafo simples**: cada orientação é um nó e cada `relatedIds` é uma aresta. O grafo é tratado como **não direcionado**: se A aponta para B, B também oferece A como continuação (`build_graph`).
- **Continuação da consulta**: `related_services(records, id, depth=1, limit=None)` faz uma busca em largura e devolve primeiro as relacionadas diretas e, com `depth=2`, as vizinhas das vizinhas. Como todas as orientações têm pelo menos 3 relacionadas, a navegação sempre oferece pelo menos 3 assuntos. Exemplo: de `work-card` saem `unemployment`, `jobs`, `salary-bonus`, `cpf` e `fgts`.
- **Caminho mais curto**: `navigation_path(records, origem, destino)` (também em largura). Exemplo: `cpf` até `fgts` passa por `work-card`. Devolve lista vazia se não houver caminho.

## Limitações conhecidas

- Os pesos e o limite de 60% foram escolhidos testando com as perguntas iniciais e as reformulações dos testes. Com mais perguntas, convém reajustar.
- Não há tratamento de erros de digitação (`cadunco`) nem de conjugação de verbos (`demitiram` não vira `demissao`); só plurais simples e a tabela de sinônimos.
- Perguntas longas e cheias de palavras fora da base podem cair abaixo da cobertura mínima e retornar vazio, mesmo com um assunto válido no meio.
- A qualidade das respostas depende de `keywords` bem escolhidas na base.

## Testes

`python -m unittest tests.test_search -v` cobre normalização, as 12 perguntas iniciais, reformulações e sinônimos, plurais, filtro por tema, consulta vazia, perguntas fora da base, empates, entradas inválidas, hierarquia, grafo, continuações e caminho. Os cenários iniciais e as perguntas concretas também rodam sobre `data/services.json`.
