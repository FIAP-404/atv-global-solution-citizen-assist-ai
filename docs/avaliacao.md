# Avaliação do assistente

Código em `backend/evaluation.py`, testes em `tests/test_evaluation.py`, casos em `data/demo-test-cases.json` e resultado medido em `results/evaluation.json`.

## Como reproduzir

```bash
python -m src.main --evaluate --output results/evaluation.json
python -m unittest tests.test_evaluation -v
```

A avaliação chama `backend.assistant.answer_question`, a mesma função usada pela API e pelo terminal, nos modos `direct` e `steps`. Nenhuma lógica de resposta é copiada e nenhuma IA externa é usada.

## Conjunto de casos

São 56 perguntas, cada uma executada nos dois modos (112 consultas).

| Categoria (`category`) | Casos | O que testa |
| --- | --- | --- |
| `direct` | 14 | Nome do serviço ou pergunta direta, uma para cada orientação da base (a de CPF tem uma reformulação à parte) |
| `reformulation` | 19 | A mesma dúvida dita de outro jeito: sinônimos (`CTPS`, `fundo de garantia`), linguagem do dia a dia (`fui mandado embora`, `benefício idoso`) e 3 limitações conhecidas |
| `intent` | 8 | Dúvidas específicas: documentos, custo, prazo, direito e local |
| `out-of-scope` | 7 | Assuntos fora da base: tempo, CNH, CNPJ, imposto de renda, SUS, futebol, receita |
| `limit` | 5 | Entrada vazia, só pontuação, só palavras comuns e duas ambiguidades (`documento`, `carteira`) |
| `invalid` | 3 | Texto acima de 500 caracteres, modo de resposta inexistente (`audio`) e opção inexistente (`opção 4`) |

Campos de cada caso:

| Campo | Uso |
| --- | --- |
| `id`, `question`, `category` | Identificação |
| `expectedStatus` | `matched`, `ambiguous`, `unsupported`, `empty` ou `error` (a função deve recusar a entrada) |
| `expectedServiceId` | Orientação esperada em `matched` |
| `expectedServiceIds` | Opções esperadas em `ambiguous` |
| `expectedFacts` | Informações que a mensagem precisa conter, tiradas dos campos revisados da base (órgão, canal, documentos) ou do aviso de limite (`não informa valores`, `não decide se você tem direito`) |
| `requestMode` | Força um modo na chamada; usado para testar modo inexistente |
| `knownLimitation` | Marca casos que **devem** falhar hoje. Continuam contando como erro na taxa de acerto; a marca só tira esses casos dos testes unitários |

## Critérios de acerto

Cada consulta recebe duas classificações:

1. **`retrievalCorrect` (recuperação):** o status é o esperado; em `matched`, a orientação é a esperada; em `ambiguous`, as opções são as esperadas; em `error`, a função recusou a entrada com `ValueError`. A resposta também precisa passar no contrato `AnswerResponse`.
2. **`responseCorrect` (resposta):** a recuperação está correta **e** a mensagem tem o que esse tipo de resposta exige:

| Status | A mensagem precisa ter |
| --- | --- |
| `matched` | Link da fonte, aviso de confirmação e todos os `expectedFacts` (comparação sem acento e sem maiúsculas) |
| `ambiguous` | O título de cada opção e um pedido de escolha |
| `unsupported` | A frase de que não encontrou informação e ao menos um tema sugerido |
| `empty` | Um pedido da pergunta ou da dúvida |

**Taxa de acerto** = consultas com `responseCorrect` ÷ total de consultas, por modo. **Tempo médio** = média simples do tempo de `answer_question` (`time.perf_counter`), em milissegundos. Em `results/evaluation.json`, cada consulta registra a pergunta, o esperado, o obtido (status, ids e mensagem), as duas classificações, os problemas encontrados e o tempo.

## Resultados (execução de 19/11/2026, após completar as 10 orientações que estavam genéricas e citar valores e prazos da base; base `services.demo.json` com 15 orientações)

| Indicador | `direct` | `steps` |
| --- | --- | --- |
| Perguntas testadas | 56 | 56 |
| Acertos (resposta) | 54 | 54 |
| **Taxa de acerto** | **96,4%** | **96,4%** |
| Taxa de recuperação | 96,4% | 96,4% |
| **Tempo médio de consulta** | **1,86 ms** | **1,84 ms** |
| Tempo máximo | 3,66 ms | 3,53 ms |
| Tamanho médio da mensagem `matched` | 585 caracteres | 954 caracteres |

Por categoria (iguais nos dois modos): diretas 14/14, dúvidas específicas 8/8, fora da base 7/7, limites 5/5, inválidas 3/3, reformulações 17/19.

Erros (os mesmos nos dois modos):

| Caso | Pergunta | Obtido | Causa |
| --- | --- | --- | --- |
| `reform-registry-typo` | `cadunco` | `unsupported` | A busca não tolera erro de digitação |
| `reform-registry-long` | Pergunta longa sobre o cadastro único | `unsupported` | Muitas palavras fora da base derrubam a cobertura mínima |

Os tempos variam um pouco a cada execução e de máquina para máquina; a ordem de grandeza (poucos milissegundos) se mantém.

Na execução anterior, com as orientações de CPF, Cadastro Único e ID Jovem ainda genéricas, o resultado foi 53/56 (94,6%): `reform-youth-id` (`carteirinha de estudante jovem baixa renda`) era recusada. Com o resumo e o público reais da Identidade Jovem ("jovens de baixa renda"), a busca passou a encontrá-la. O caso mostra que a qualidade do conteúdo da base afeta diretamente a taxa de acerto.

## Interpretação dos indicadores

- **Nenhuma resposta errada foi dada com confiança.** Os 2 erros são recusas (`unsupported`). O assistente preferiu dizer que não sabia e sugerir temas a apontar uma orientação errada. Para orientação cidadã, esse é o tipo de erro menos grave. As 7 perguntas fora da base também foram recusadas, inclusive `carteira de motorista`, que compartilha a palavra "carteira" com duas orientações.
- **O ponto fraco é a reformulação (89%)**, não as perguntas diretas (100%). Quem não conhece o nome do serviço ou escreve com erro é exatamente o público com menos familiaridade com portais públicos.
- **A taxa de resposta é igual à de recuperação.** Sempre que a orientação certa foi escolhida, a mensagem trouxe fonte, aviso e os fatos esperados. Isso mostra que as regras dos modelos são cumpridas, mas também que a verificação automática de fatos é pouco exigente (veja as limitações).
- **Os dois modelos acertam o mesmo.** Eles usam a mesma busca e as mesmas regras, então a escolha entre eles depende de clareza, não de acerto.
- **O tempo não é um problema:** menos de 2 ms em média, porque a base tem 15 registros e a busca é linear em memória.

## Comparação dos modelos de resposta

| Critério | `direct` | `steps` |
| --- | --- | --- |
| Acerto | 96,4% | 96,4% |
| Fonte e aviso nas respostas `matched` | 39/39 | 39/39 |
| Tamanho médio | 585 caracteres | 954 caracteres (+63%) |
| Estrutura | Varia conforme a dúvida (documentos, local, custo...) | Sempre as mesmas etapas: separar → canal → passos → confirmar |

- **Mais claro: `direct`.** A informação pedida aparece na primeira frase. No `steps`, uma pergunta de custo recebe também a preparação, o canal e os passos, que a pessoa não pediu. O texto é 63% maior e chega a quase 1.600 caracteres.
- **Mais consistente: `steps`.** A ordem das etapas nunca muda, o que ajuda quem quer se preparar para ir ao atendimento e facilita comparar duas orientações.
- **Decisão:** `direct` continua como padrão e `steps` como opção. A escolha deve ser confirmada no teste de usabilidade (`docs/teste-usabilidade.md`).

## Melhorias propostas

1. **Tolerância a erros de digitação:** comparar termos com distância de edição 1 (`cadunco` → `cadunico`) só quando a busca exata não encontra nada. Resolveria `reform-registry-typo` sem afrouxar a recusa de perguntas fora da base.
2. **Cobertura calculada sobre o vocabulário da base:** em perguntas longas, ignorar no cálculo dos 60% as palavras que não aparecem em nenhum registro, mas exigir pelo menos dois termos fortes. Resolveria `reform-registry-long`. Precisa ser testada contra os 7 casos fora da base para não gerar respostas arbitrárias.
3. **Enriquecer `keywords` (pacote 1):** incluir termos populares como `carteirinha` e `meia-entrada` na Identidade Jovem e `cadunico` com variações. Completar o conteúdo da Identidade Jovem já resolveu `reform-youth-id`.
4. **Encurtar o modelo `steps`:** omitir a etapa de preparação quando a dúvida é de custo ou prazo, aproximando o tamanho do `direct` sem perder a estrutura.

## Limitações da avaliação

- **Casos escritos pela própria equipe**, que conhece a base e a busca. Há viés a favor do sistema; perguntas de usuários reais tendem a ser mais variadas.
- **Verificação de fatos literal.** `expectedFacts` são trechos dos campos da base e a comparação é por substring normalizada. Ela aprova respostas que copiam os campos (o caso deste assistente determinístico), mas reprovaria paráfrases corretas e não mede se a resposta é **útil**. A utilidade percebida fica para o teste de usabilidade.
- **Fatos dependem da base.** Se um registro estiver desatualizado, o caso continua "correto". A avaliação mede a fidelidade à base, não a correção em relação ao órgão.
- **Base pequena** (15 registros, 56 perguntas). Os tempos e a taxa de acerto não se transferem para uma base maior.
- **Tempo medido** numa única execução, em uma máquina, sem rede. Na API somam-se HTTP e validação.
- **Clareza e consistência** foram comparadas por tamanho e estrutura das mensagens, não por avaliação humana sistemática.
