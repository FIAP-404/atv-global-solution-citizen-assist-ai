# O que falta e como dividir a entrega

## Escopo fechado

O projeto entrega **orientação cidadã dentro do próprio portal**. Não precisa emitir documentos, consultar cadastros de cidadãos, receber pedidos oficiais ou recriar os sistemas da Receita Federal e de outros órgãos.

O enunciado pede um fluxo de consulta completo: receber a pergunta, consultar a base e apresentar a orientação com a referência. Isso exige conteúdo útil; uma sequência de frases como “entre no site e confira os requisitos” não é suficiente como resposta final.

As telas, os campos JSON, a API e a entrada por terminal já estão preparados. **Este detalhamento não exige novas telas nem alteração do contrato da API.** A base de demonstração permanece provisória; os exemplos atuais não devem ser confundidos com o conteúdo final.

## Como enriquecer cada orientação usando os campos existentes

| Campo | O que entregar | O que evitar |
| --- | --- | --- |
| `summary` | Explicação concreta do serviço e resposta resumida à necessidade principal | Apenas “acesse o órgão responsável” |
| `audience` | Público atendido e condições relevantes, conforme a fonte | Público genérico ou garantia de elegibilidade |
| `preparation` | Documentos ou providências concretas para preparar a consulta/solicitação, quando aplicáveis e confirmados | Checklist inteiro dizendo apenas para pesquisar em outro site |
| `steps` | Sequência prática: como começar, qual procedimento/canal usar e como continuar, com detalhes conferidos | Todas as etapas resumidas a “abra”, “leia” e “siga o site” |
| `limitations` | Limites específicos: diferenças estaduais/municipais, casos que dependem de análise e informações não confirmadas | Aviso genérico usado no lugar da explicação |
| `agency`, `channel` | Órgão e canal correspondentes ao serviço descrito | Canal inventado ou promessa de integração |
| `source` | Fonte oficial específica, título e data real da conferência | Página inicial genérica quando existe referência específica, ou data preenchida sem verificação |
| `keywords` | Termos e reformulações que as pessoas usariam para perguntar sobre a orientação | Somente o nome formal do serviço |
| `relatedIds` | Orientações relacionadas e existentes na base | Relações aleatórias apenas para completar uma quantidade |

As listas de preparação e os passos já são exibidos na página de orientação. A resposta do assistente já aceita texto em `message`, além do registro completo em `services`. Não é necessário acrescentar formulários de CPF, login ou solicitação oficial para completar a experiência.

O enunciado exige ao menos **15 orientações em 3 temas**, conteúdo resumido, fonte e data de verificação. O preenchimento detalhado dos demais campos é o nosso critério de qualidade para aproveitar o portal que já foi construído; não significa implementar todas as etapas operacionais do serviço público.

## Regra simples para aprovar o conteúdo

Para cada registro, escolham uma pergunta concreta que aquela orientação deve responder. Uma pessoa deve conseguir entender a resposta e preparar o próximo passo lendo o nosso portal. A fonte externa serve para comprovar, confirmar atualização e executar o que depende do órgão.

Por exemplo, uma pergunta sobre documentação necessária exige os documentos e condições aplicáveis na própria orientação. Responder apenas “confira a documentação no site oficial” não resolve essa pergunta. Os documentos específicos precisam ser pesquisados e conferidos pelo grupo; este guia não inventa a lista.

Não é necessário cobrir todas as exceções de cada serviço. Delimitem os casos contemplados e expliquem o que ficou fora. Não preencham taxas, prazos ou critérios legais de memória.

## Entregas dos quatro módulos

O grupo escolhe os responsáveis. Cada pessoa entrega código, testes e uma explicação curta. A pesquisa dos 15 conteúdos pode ser dividida entre o grupo; o responsável pelo módulo 1 consolida e valida o arquivo final.

| Módulo | Código e arquivos da entrega | Critério para considerar pronto |
| --- | --- | --- |
| **1. Base e conteúdo** | `backend/knowledge.py`, `data/services.json`, `tests/test_knowledge.py`, `docs/knowledge-base.md` | Quinze orientações úteis e conferidas, cinco por tema; leitura e validação dos arquivos funcionando; campos e relações válidos |
| **2. Busca e relações** | `backend/search.py`, `tests/test_search.py`, `docs/search-strategy.md` | Perguntas diretas e reformuladas encontram orientações; filtros funcionam; múltiplas correspondências e grafo/hierarquia são explicados |
| **3. Respostas** | `backend/assistant.py`, `tests/test_assistant.py`, `docs/response-instructions.md` | A pergunta recebe uma resposta útil baseada nos campos disponíveis, com fontes e limites; os dois modelos de instrução estão documentados e funcionam |
| **4. Avaliação** | `backend/evaluation.py`, `tests/test_evaluation.py`, `data/test-cases.json`, `results/evaluation.json`, `docs/evaluation.md`, `docs/usability.md` | Pelo menos 12 perguntas executadas nos dois modelos, acertos e tempos reais, avaliação da utilidade da resposta, usabilidade e melhorias registradas |

Os caminhos acima são entregas a criar pelos responsáveis, não documentos ou resultados que já existem. As assinaturas das funções continuam as de [team-work-packages.md](team-work-packages.md).

## Detalhes importantes para quem assume as respostas

- `message` deve responder à pergunta, e não se limitar a anunciar “encontrei uma orientação”. Pode usar os campos relevantes do registro selecionado para explicar documentação, público ou próximos passos.
- O React já apresenta o resumo do registro e, no modo `steps`, a lista de passos. Evitem repetir todo o guia em `message`; priorizem a informação que a pergunta pediu.
- Os modelos `direct` e `steps` devem ter instruções documentadas sobre seleção do conteúdo, estrutura, fonte e limites. Não são modelos de IA externos.
- Se a base não sustenta a informação pedida, informem a limitação. Não usem uma correspondência pelo título como justificativa para responder algo que o conteúdo não explica.
- Se houver mais de um serviço possível, peçam esclarecimento. O registro completo em `services` permite ao usuário continuar no detalhe da orientação.

## Detalhes importantes para quem assume a avaliação

Os 12 cenários atuais verificam principalmente seleção de serviço e tratamento de estados. **Encontrar o ID correto não prova que a pergunta foi respondida.**

No conjunto final, mantenham os campos existentes (`id`, `question`, `expectedStatus` e, quando aplicável, `expectedServiceId`) e acrescentem `expectedFacts`: uma lista das informações essenciais esperadas para aquela pergunta, conferidas na fonte. Para os casos de limitação, registrem o aviso ou pedido de esclarecimento esperado.

O responsável pelo módulo 4 define e documenta como verificar esses fatos nas respostas; uma comparação textual literal isolada pode rejeitar paráfrases corretas ou aprovar respostas incompletas. A avaliação pode combinar verificações programadas com conferência humana documentada, sem acrescentar IA externa.

Registrem separadamente:

- se a orientação/status encontrado está correto;
- se a resposta resolve a pergunta e inclui os fatos essenciais, a fonte e os limites;
- quanto tempo a consulta levou;
- em qual modelo de instrução o resultado foi obtido.

Expliquem qual critério compõe a taxa de acerto das respostas e comparem clareza e consistência dos modelos. Não apresentem somente a taxa de IDs encontrados como se fosse avaliação completa das respostas.

## Como trabalhar em paralelo

1. Todos partem do formato de `data/services.demo.json`; ninguém precisa esperar uma alteração de front-end.
2. O módulo 1 revisa conteúdo e implementa o carregamento. O módulo 2 pode começar testando buscas com a base de demonstração.
3. O módulo 3 pode desenvolver os estados e as instruções com registros controlados de teste e depois conectar a busca real do módulo 2.
4. O módulo 4 pode montar perguntas e respostas esperadas desde já; as medições e conclusões finais só acontecem com a implementação real.
5. Quando as partes estiverem prontas, o coordenador conecta a base final e confere o fluxo completo no navegador e no terminal.

## O que fica com o coordenador

A preparação das telas e da integração está concluída para esse escopo. Depois das entregas dos colegas, ainda há a conferência final de integração, os ajustes que essa conferência revelar, integrantes/RMs, documentação consolidada, vídeo e TXT com os links de entrega. Isso não deve ser confundido com necessidade de criar novas páginas dos órgãos públicos.
