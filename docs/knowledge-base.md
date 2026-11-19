# Base de conhecimento 

## Onde estão os dados

| Arquivo | Papel |
| --- | --- |
| `data/services.json` | **Base usada pelo sistema** (API e terminal leem este caminho, definido em `backend/config.py`). |
| `data/services.demo.json` | Cópia de demonstração original. Serve de referência e de base para os testes; não é a base final. |

O formato é um **array JSON** com uma orientação por objeto. Os campos usam `camelCase`, como no contrato da API (`docs/api-contract.md`).

## Campos de cada orientação

Todos são obrigatórios. Campos desconhecidos são rejeitados, para pegar erros de digitação (por exemplo `keyword` no lugar de `keywords`).

| Campo | Tipo | Regra |
| --- | --- | --- |
| `id` | texto | Único na base, estável (aparece na URL do portal). |
| `topic` | `documents`, `work` ou `social` | Tema de primeiro nível. |
| `title` | texto | Nome da orientação. |
| `summary` | texto | Resposta resumida à necessidade principal. |
| `keywords` | lista de textos | Pelo menos 1. Termos e reformulações que as pessoas usariam. Sem acento, em minúsculas. |
| `agency` | texto | Órgão responsável. |
| `channel` | `digital`, `in-person` ou `mixed` | Canal descrito na fonte. |
| `source.title` | texto | Nome da fonte consultada. |
| `source.url` | link `https` | Sem usuário e senha. Use a página específica do serviço, não a inicial do órgão. |
| `source.reviewedAt` | `AAAA-MM-DD` ou `null` | Data em que alguém **de fato conferiu a fonte**. `null` significa "ainda não verificado". Não pode estar no futuro. |
| `audience` | texto | Quem pode usar e condições, conforme a fonte. |
| `steps` | lista de textos | Pelo menos 1 passo prático. |
| `preparation` | lista de textos | Documentos ou providências (pode ser vazia). |
| `limitations` | texto | O que a orientação não cobre ou não confirma. |
| `relatedIds` | lista de ids | Pelo menos 3, todos existentes, sem repetir e sem apontar para si mesmo. |

## Como o código lê e valida

`load_services(path)` (assinatura fixada pelo grupo) devolve uma lista de dicionários e **nunca transforma arquivo quebrado em sucesso**:

| Situação | Resultado |
| --- | --- |
| Arquivo não existe | `FileNotFoundError` |
| Arquivo vazio ou só espaços | `KnowledgeBaseError` ("vazio") |
| JSON malformado | `KnowledgeBaseError` com linha e coluna |
| Raiz não é lista, ou lista vazia | `KnowledgeBaseError` |
| Campo ausente, vazio, desconhecido ou do tipo errado | `KnowledgeBaseError` |
| `id` duplicado, `topic`/`channel` inválidos | `KnowledgeBaseError` |
| URL sem `https`, com senha, ou data inválida/futura | `KnowledgeBaseError` |
| `relatedIds` inexistente, repetido, autorreferente ou com menos de 3 itens | `KnowledgeBaseError` |

`KnowledgeBaseError` herda de `ValueError` e traz `problems`, a lista com **todos** os problemas de uma vez (um por linha), em vez de parar no primeiro. O terminal (`src/main.py`) já captura `OSError` e `ValueError`.

Funções de apoio, usadas pela busca, pela resposta e pelos menus:

- `list_topics(records)`: temas disponíveis, com rótulo e quantidade.
- `group_by_topic(records)` e `index_by_id(records)`: acesso por tema e por identificador (dicionários).
- `unverified_ids(records)`: orientações ainda sem data de verificação.
- `check_coverage(records)`: confere os mínimos do enunciado (15 orientações, 5 por tema).
- `load_services(path, require_verified=True)`: falha se algum `reviewedAt` for `null`. Use na revisão final.

## Verificar a base pelo terminal

```bash
python -m backend.knowledge                 # valida data/services.json
python -m backend.knowledge outro.json      # valida outro arquivo
python -m backend.knowledge --require-verified   # exige data em todas as orientações
```

A saída mostra a contagem por tema e avisa quais orientações ainda não têm data de verificação.

## Como acrescentar ou corrigir uma orientação

Não é preciso mexer em código. Edite `data/services.json`:

1. Copie um registro existente do mesmo tema e troque o `id` por um novo e único.
2. Preencha todos os campos a partir de uma **fonte oficial específica**. Só preencha `reviewedAt` depois de abrir a fonte e conferir o conteúdo.
3. Em `relatedIds`, indique pelo menos 3 orientações existentes. Se quiser que a nova apareça como continuação de outra, inclua o `id` dela também na lista das relacionadas.
4. Rode `python -m backend.knowledge` e `python -m unittest discover -s tests -v`.

## Origem e estado de verificação do conteúdo

- **Tema Trabalho (5 orientações): verificado em 19/11/2026.** `work-card`, `unemployment`, `salary-bonus`, `fgts` e `jobs` foram reescritos a partir das páginas oficiais do gov.br indicadas em cada `source.url` (consultadas em 19/11/2026). Valores, limites e calendário do abono salarial valem para o pagamento de 2026 e mudam todo ano.
- **Temas Documentos e Assistência social (10 orientações): ainda sem verificação.** Mantêm o texto de demonstração e `reviewedAt: null`, e devem ser substituídos por quem pesquisar esses temas. O `python -m backend.knowledge` lista quais são.
- Não foram preenchidas taxas, prazos ou critérios de memória: o que a página oficial não informa está dito em `limitations`.

## Limites

- A validação confere **forma**, não **verdade**: uma data preenchida com a fonte errada passa. A conferência do conteúdo é humana.
- A base é um JSON pequeno lido por inteiro na memória a cada consulta. Para um protótipo é suficiente.
