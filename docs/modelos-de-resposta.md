# Modelos de resposta do assistente

Código em `backend/assistant.py`, testes em `tests/test_assistant.py`. O módulo **não usa IA externa**: escolhe as orientações com a busca de `backend/search.py` e monta o texto com regras fixas. Toda frase sobre um serviço vem de um campo do registro (`steps`, `preparation`, `audience`, `agency`, `channel`, `source`).

Assinatura fixa: `answer_question(records, question, mode="direct") -> dict`, com `status`, `message`, `services` e `mode` (contrato em `backend/contracts.py`).

## Fluxo

1. **Validação da entrada.** Modo diferente de `direct`/`steps`, pergunta que não é texto ou pergunta com mais de 500 caracteres geram `ValueError` (o mesmo limite da API e do terminal).
2. **Vazia.** Se a pergunta, normalizada, não tem nenhum caractere útil (só espaços ou pontuação), o status é `empty`.
3. **Busca.** `score_services` ordena as orientações. Se nada passar, há uma segunda tentativa sem as palavras de intenção ("quanto custa", "tem direito", "prazo"...), que não existem nos registros e baixavam a cobertura mínima da busca. Exemplo: `quanto custa o passaporte?` só encontra o passaporte na segunda tentativa. `quanto custa?` sozinho continua sem resposta, porque não sobra palavra útil.
4. **Sem candidato:** `unsupported`.
5. **Empate:** `find_ties` devolve os resultados a até 20% da melhor pontuação. Com dois ou mais, o status é `ambiguous` e as três primeiras opções vão em `services`.
6. **Uma orientação clara:** `matched`, com a resposta montada conforme a **intenção** da pergunta.

## Os quatro status

| Status | `services` | O que a mensagem traz |
| --- | --- | --- |
| `empty` | vazio | Pede a pergunta e lista os temas disponíveis. |
| `unsupported` | vazio | Diz que não há base suficiente e que não vai inventar instruções; sugere os temas com exemplos de orientações e pede para reformular citando o serviço. |
| `ambiguous` | 2 ou 3 registros | Lista as opções pelo título e pergunta qual a pessoa procura. Repetir a pergunta com o título escolhido leva a `matched` (o título exato recebe bônus na busca). |
| `matched` | 1 registro | Responde ao que foi perguntado, cita a fonte (título, link e data de verificação) e traz o aviso de confirmação. |

## Intenção da pergunta

Encontrar o serviço certo não basta: a mensagem precisa responder à dúvida. Uma tabela curta de expressões (`INTENTS`) identifica o tipo de informação pedida. A primeira que aparecer, na ordem abaixo, decide.

| Intenção | Exemplos de expressão | Campo usado | Comportamento |
| --- | --- | --- | --- |
| `cost` | quanto custa, valor, taxa, gratuito | frases do registro com `R$` ou "gratuito" | Se a base traz o valor, cita até duas frases do registro ("A base informa: ...") e pede para confirmar o valor atual na fonte. Se não traz, diz isso explicitamente, não estima e indica o canal/órgão. |
| `deadline` | prazo, quanto tempo, demora | frases do registro com número + dias/horas/meses | Mesmo tratamento: cita o prazo da base quando existe (ex.: FGTS, "até 5 dias úteis") e avisa quando não existe. |
| `eligibility` | tenho direito, quem pode, requisitos | `audience` | Informa o público da orientação e avisa que o assistente não decide se a pessoa tem direito. |
| `documents` | quais documentos, o que levar | `preparation` | Lista o que separar e o primeiro passo. |
| `where` | onde, site, aplicativo, presencial | `channel`, `agency` | Informa o canal e o órgão responsável e o primeiro passo. |
| `how` (padrão) | demais perguntas | `steps`, `channel`, `agency` | Primeiro passo e canal. |

O resumo (`summary`), os passos completos e as limitações do registro **não são repetidos** em `message`: a interface React já mostra esses campos do registro enviado em `services`. A mensagem prioriza o que a pergunta pediu.

## Modelo 1: `direct` (resposta direta)

- **Papel:** orientador que responde em poucas frases à dúvida principal, usando apenas os campos da orientação selecionada.
- **Seleção do conteúdo:** só as frases da intenção detectada (tabela acima).
- **Formato:** um parágrafo, `Título: resposta. Fonte: ... Aviso: ...`.
- **Citação:** obrigatória em `matched`: `Fonte: <título> (<link>), verificada em DD/MM/AAAA` ou `data de verificação pendente` quando `reviewedAt` é nulo.
- **Exemplo** (`Onde faço o CadÚnico?`):
  > Cadastro Único: O atendimento é feito presencialmente. Órgão responsável: Ministério do Desenvolvimento e Assistência Social. Para começar: Leia a página oficial de inscrição no Cadastro Único. Fonte: GOV.BR · Inscrever-se no Cadastro Único (https://www.gov.br/...), verificada em 19/11/2026. Aviso: este assistente é um projeto acadêmico, não é canal oficial; confirme os requisitos atualizados na fonte antes de ir ao atendimento.

## Modelo 2: `steps` (passo a passo)

- **Papel:** orientador que organiza a mesma informação em etapas numeradas, para a pessoa se preparar e saber por onde seguir.
- **Seleção do conteúdo:** sempre as mesmas etapas, nesta ordem: (limite sobre valor/prazo ou público, quando a intenção pede) → o que separar → canal e órgão → quantos passos seguir e por qual começar → confirmar na fonte.
- **Formato:** `Título, em etapas: 1) ... 2) ... Fonte: ... Aviso: ...`. A numeração fica na mesma linha para funcionar tanto no terminal (JSON) quanto no parágrafo da interface web.
- **Citação:** igual ao modelo direto.
- **Exemplo** (`quanto custa o passaporte?`):
  > Passaporte brasileiro, em etapas: 1) A base informa: Segundo a página oficial (versão de 07/10/2026), a taxa comum é de R$ 257,25 (R$ 334,42 na urgência), ... Confirme o valor atual na fonte oficial. 2) Separe antes: Conferir a lista de documentos originais no link da página oficial; ... 3) O atendimento é feito por canais digitais e presenciais. Órgão responsável: Polícia Federal. 4) Siga os 4 passos da orientação, começando por: Preencha o formulário de solicitação no site da Polícia Federal (gov.br/pf). 5) Confira na fonte se os requisitos continuam os mesmos. Fonte: ... Aviso: ...

## Regras comuns aos dois modelos

1. Citar sempre a fonte em respostas `matched`.
2. Trazer sempre o aviso de que o projeto não é canal oficial e de que os requisitos devem ser confirmados.
3. Não alegar que realiza o serviço nem decidir se a pessoa tem direito.
4. Não inventar valores, prazos ou documentos: se a base não tem o dado, dizer isso.
5. Em pergunta ambígua, pedir esclarecimento em vez de escolher sozinho.
6. Fora da base, informar o limite e sugerir os temas disponíveis.

## Limites

- **Só sabe o que está na base.** Valores e prazos aparecem apenas quando o registro os traz (passaporte, CPF em conveniadas, abono, FGTS, seguro-desemprego, CIN); nos demais, e para endereços de unidades e critérios legais detalhados, o assistente avisa e manda conferir na fonte. A detecção é por padrão de texto (`R$`, "gratuito", número + unidade de tempo) e pode trazer uma frase próxima do assunto, não exatamente a pedida.
- **Intenção por palavras.** A tabela de intenções é curta e não entende frases indiretas ("vou ter que pagar alguma coisa?" não é reconhecida como custo). Nesses casos a resposta cai no padrão `how`, que continua correta, mas menos focada.
- **Uma intenção por pergunta.** "Quanto custa e onde faço o passaporte?" responde só ao custo (primeira na ordem de prioridade); o canal aparece mesmo assim, porque a resposta de custo também o inclui.
- **Herda os limites da busca:** sem tolerância a erros de digitação e com cobertura mínima de 60% (consulte `docs/search-strategy.md`).
- **Ambiguidade limitada a 3 opções.** Se mais de três orientações empatarem, só as três primeiras (pela ordem da busca) aparecem.
- **Pergunta só com palavras comuns** (por exemplo, `como`) é tratada como `unsupported`, e não como `empty`, porque há texto, mas nada a buscar.
- **Qualidade depende do conteúdo.** Se `preparation` ou `steps` de um registro forem genéricos ("consultar a documentação na fonte oficial"), a resposta também será genérica. Isso é responsabilidade do pacote 1 (base).

## Comparação dos dois modelos

Executado com `data/services.demo.json` sobre as 12 perguntas de `data/demo-test-cases.json` e mais 6 perguntas de intenção (documentos, custo, direito, prazo, `fui demitido` e `carteira`).

| Indicador | `direct` | `steps` |
| --- | --- | --- |
| Status e orientação corretos (12 casos) | 12/12 | 12/12 |
| Respostas `matched` com fonte e aviso | 14/14 | 14/14 |
| Tamanho médio da mensagem `matched` | ~555 caracteres | ~900 caracteres |
| Faixa de tamanho | 455–876 | 698–1097 |
| Tempo médio por consulta | < 1 ms | < 1 ms |

**Leitura:**

- A **seleção é idêntica** nos dois modelos: os dois chamam a mesma busca e o mesmo tratamento de empate. A taxa de acerto de status/orientação, portanto, não separa os modelos; a diferença está na forma.
- **Clareza:** o modelo `direct` é mais claro para perguntas de um ponto só (onde, quanto custa, tenho direito). A resposta aparece na primeira frase e a mensagem tem cerca de 40% menos texto. No `steps`, a resposta ao custo fica na etapa 1, mas vem acompanhada de preparação e canal, que a pessoa não pediu.
- **Consistência:** o modelo `steps` é mais consistente na estrutura: toda resposta `matched` tem as mesmas etapas na mesma ordem (separar → canal → passos → confirmar), o que ajuda quem quer se preparar para ir ao atendimento. O `direct` muda de conteúdo conforme a intenção.
- **Escolha:** mantivemos `direct` como padrão, por responder primeiro ao que foi perguntado e com menos texto. `steps` fica como opção para quem quer o roteiro de preparação. Os dois cumprem igualmente as regras de fonte e aviso.

Esses números medem formato e regras, não a utilidade percebida. A avaliação final (pacote 4: `backend/evaluation.py`, conjunto ampliado e teste de usabilidade) deve confirmar ou rever essa conclusão com usuários.

## Como rodar

```bash
python -m unittest tests.test_assistant -v
python -m src.main --question "Quanto custa o passaporte?" --mode direct
python -m src.main --question "Quanto custa o passaporte?" --mode steps
```
