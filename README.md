# Citizen Assist AI

**Global Solution 2026.2 | FIAP | Grupo 404**

Assistente digital introdutório de orientação cidadã: consulta uma base de informações verificadas sobre documentos, trabalho e assistência social, responde em linguagem clara, **sempre cita a fonte** e avisa quando não há base suficiente para orientar.

## Equipe

| Integrante | RM |
|---|---|
| Caetano de Medeiros Bona | RM569262 |
| Fernando dos Santos Motta | RM570046 |
| Joedson da Silva Souza | RM573981 |
| Mylena Ramalho da Silva Torquato | RM572383 |

- **Vídeo de apresentação (YouTube, não listado):** [PREENCHER: link]
- **Repositório:** [FIAP-404/atv-global-solution-citizen-assist-ai](https://github.com/FIAP-404/atv-global-solution-citizen-assist-ai)

## 1. Problema, público e temas

Encontrar o canal oficial certo para um serviço público costuma exigir navegar por vários sites. O assistente ajuda quem precisa de **orientação inicial** (qual serviço procurar, quais documentos separar, onde fazer) e indica a referência oficial para confirmar os requisitos atualizados.

**Público:** cidadãos em geral, incluindo quem tem pouca familiaridade com portais públicos.

**Temas (3, com 5 orientações cada, 15 no total):**

| Tema (`topic`) | Exemplos |
|---|---|
| Documentos (`documents`) | CPF, RG/CIN, passaporte, título eleitoral |
| Trabalho (`work`) | Carteira de Trabalho Digital, FGTS, seguro-desemprego, vagas no SINE |
| Assistência social (`social`) | CadÚnico, Bolsa Família, BPC, CRAS |

> O assistente é um projeto acadêmico independente. **Não é um canal oficial** do governo nem da FIAP, não realiza serviços e não se integra a órgãos públicos.

## 2. Base de conhecimento

Arquivo JSON em `data/services.json` (caminho definido em `backend/config.py`). A leitura e a validação ficam em `backend/knowledge.py`, sem depender da camada HTTP.

| Campo | Descrição |
|---|---|
| `id` | Identificador único (ex.: `cpf`) |
| `topic` | `documents`, `work` ou `social` |
| `title` | Nome da orientação |
| `summary` | Orientação resumida |
| `keywords` | Palavras-chave usadas na busca |
| `agency` | Órgão responsável |
| `channel` | `digital`, `in-person` ou `mixed` |
| `source` | Referência consultada: `title`, `url` (https) e `reviewedAt` (data de verificação, AAAA-MM-DD) |
| `audience` | A quem se destina |
| `steps` | Passos da orientação |
| `preparation` | O que separar antes |
| `limitations` | Limites e aviso de confirmação |
| `relatedIds` | Pelo menos 3 orientações relacionadas (navegação) |

**Validações:** arquivo ausente, vazio ou com JSON inválido; campos obrigatórios ausentes ou desconhecidos; ids duplicados; tema/canal inválidos; URL fora de https ou com credenciais; data inválida ou futura; `relatedIds` inexistentes ou apontando para o próprio registro.

**Manutenção:** acrescentar ou corrigir uma orientação exige editar apenas o JSON. Para validar:

```bash
python -m backend.knowledge                      # valida data/services.json
python -m backend.knowledge --require-verified   # exige data de verificação em todas
```

Detalhes em [`docs/knowledge-base.md`](docs/knowledge-base.md).

## 3. Estruturas e estratégia de busca (`backend/search.py`)

- **Listas e dicionários:** registros em lista; acesso por id (`index_by_id`) e por tema (`group_by_topic`).
- **Hierarquia:** tema → orientações (`build_topic_tree`), usada no menu por tema.
- **Grafo simples:** cada orientação é um nó e cada `relatedIds` é uma aresta (não direcionada). A navegação usa busca em largura (`related_services`) e `navigation_path` devolve o caminho mais curto entre duas orientações.
- **Busca:** a pergunta e os campos são normalizados (minúsculas, sem acentos, sem pontuação, sem palavras comuns, plurais reduzidos), com tabela curta de sinônimos. Pontuação por campo: título 4, palavra-chave 3, órgão 1,5, resumo 1, com bônus para expressões inteiras.
- **Cobertura mínima de 60%** das palavras úteis da pergunta, para evitar respostas por uma palavra genérica.
- **Várias correspondências:** ordem determinística (pontuação, termos encontrados, ordem no arquivo). Empates são detectados por `find_ties` e tratados como **pergunta ambígua**, com opções para a pessoa escolher.

Detalhes em [`docs/search-strategy.md`](docs/search-strategy.md).

## 4. Regras de resposta, modelos de instrução e limitações

O assistente **não usa IA externa**: ele seleciona o registro da base e o formata de forma determinística, com condicionais sobre o resultado da busca.

| Status | Quando | Comportamento |
|---|---|---|
| `matched` | Uma orientação clara | Resposta + fonte + aviso de confirmação |
| `ambiguous` | 2 a 3 orientações empatadas | Lista as opções para escolha |
| `unsupported` | Sem correspondência confiável | Informa o limite, sem inventar instruções, e sugere temas relacionados |
| `empty` | Entrada vazia | Mensagem pedindo a pergunta ou a escolha de um tema |

**Dois modelos de instrução de resposta** (comparados na avaliação):

| Modelo (`mode`) | Papel e formato |
|---|---|
| `direct` | Resposta curta e direta, em um parágrafo, com fonte e aviso |
| `steps` | Resposta em passos numerados, com preparação, fonte e aviso |

Ambos têm as mesmas regras: citar a fonte, não alegar atendimento oficial, não inventar valores nem prazos e avisar quando a informação não estiver na base.

A mensagem responde ao tipo de dúvida (documentos, onde fazer, quem tem direito, custo ou prazo). Quando a base não tem o dado pedido, como valores e prazos, o assistente diz isso em vez de estimar. Regras, intenções e limites estão em [`docs/modelos-de-resposta.md`](docs/modelos-de-resposta.md).

**Comparação dos modelos:** nas 12 perguntas de teste, os dois acertam status e orientação (12/12), porque usam a mesma busca. O `direct` é mais claro para dúvidas pontuais: a resposta vem na primeira frase, com cerca de 40% menos texto. O `steps` é mais consistente na estrutura: separar, canal, passos e confirmar, sempre na mesma ordem. `direct` é o padrão; a avaliação com usuários (pacote 4) deve confirmar essa escolha.

## 5. Testes, indicadores e resultados

**Plano de testes:** `data/demo-test-cases.json` traz 12 perguntas, incluindo consultas diretas, reformulações e casos-limite:

| Tipo | Casos |
|---|---|
| Direta | CadÚnico, RG, passaporte, título eleitoral, FGTS, seguro-desemprego, Bolsa Família, SINE, Carteira de Trabalho Digital |
| Limite | entrada vazia, consulta ambígua (`documento`), pergunta fora da base (`Qual a previsão do tempo?`) |

Para o conjunto final, acrescentar reformulações e mais perguntas fora do tema.

```bash
python -m src.main --evaluate --output results/evaluation.json
```

Indicadores: **taxa de acerto** (respostas corretas ÷ perguntas) e **tempo médio de consulta**, por modelo de resposta.

| Indicador | `direct` | `steps` |
|---|---|---|
| Perguntas testadas | [PREENCHER] | [PREENCHER] |
| Acertos | [PREENCHER] | [PREENCHER] |
| Taxa de acerto | [PREENCHER] | [PREENCHER] |
| Tempo médio de consulta | [PREENCHER] | [PREENCHER] |

**Teste de usabilidade:** [PREENCHER: roteiro de tarefas, quem testou, dificuldades e resultados.]

**Interpretação e limitações da avaliação:** [PREENCHER após a execução.]

## 6. Como executar

Requer **Python 3.11 ou superior**. Na raiz do projeto (no macOS/Linux, use `.venv/bin/python`):

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

**Terminal:**

```powershell
.\.venv\Scripts\python.exe -m src.main --question "CPF" --mode direct
.\.venv\Scripts\python.exe -m src.main --question "Carteira de Trabalho Digital" --mode steps
```

**API (opcional):**

```powershell
.\.venv\Scripts\python.exe -m uvicorn backend.api:app --host 127.0.0.1 --port 8000 --reload
```

Documentação interativa em <http://127.0.0.1:8000/docs>. Contrato em [`docs/api-contract.md`](docs/api-contract.md).

**Interface web (opcional):** requer Node.js 24 ou superior.

```bash
cd frontend
npm ci
npm run dev
```

Para conectar ao backend, copie `frontend/.env.example` para `frontend/.env.local` e reinicie o Vite. Testes e build: `npm test` e `npm run build`.

## 7. Exemplos

| Entrada | Resultado esperado |
|---|---|
| `Onde faço o CadÚnico?` | Orientação do CadÚnico, com fonte (GOV.BR) e aviso para confirmar requisitos |
| `passaporte brasileiro` | Orientação do passaporte, com fonte |
| `documento` | Pergunta ambígua: oferece CPF, identidade e título eleitoral |
| `Qual a previsão do tempo?` | Aviso de que não há orientação na base, com temas disponíveis |
| `   ` (vazia) | Mensagem pedindo uma pergunta ou a escolha de um tema |

[PREENCHER: substituir pelas respostas reais obtidas na execução, com as fontes.]

## 8. Clareza, acessibilidade, privacidade e informação não oficial

- **Clareza:** linguagem simples, passos numerados e checklist de preparação.
- **Acessibilidade (interface web):** layout responsivo, navegação por teclado, alto contraste e impressão da orientação.
- **Privacidade:** não coleta dados pessoais nem pede documentos. Na interface web, só os identificadores das orientações salvas ficam no navegador; mensagens não são gravadas.
- **Informação não oficial:** o projeto não representa nenhum órgão público. Toda orientação traz a fonte e um aviso para confirmar os requisitos atualizados no canal oficial.

## 9. Uso de inteligência artificial

O uso de IA e a validação crítica feita pela equipe estão registrados em [`docs/uso_ia.md`](docs/uso_ia.md). O protótipo não chama nenhum modelo externo.

## 10. Organização do repositório

| Caminho | Conteúdo |
|---|---|
| `src/` | Entrada por terminal |
| `backend/` | Base de conhecimento, busca, assistente, avaliação e API |
| `data/` | Base de orientações e casos de teste |
| `tests/` | Testes Python |
| `frontend/` | Interface web opcional (React) |
| `docs/` | Enunciado, contrato da API, base, busca e registro de uso de IA |

## 11. Conclusões, limitações e melhorias

[PREENCHER após a avaliação final.]

Limitações já conhecidas da busca:

- Não trata erros de digitação (`cadunco`) nem conjugações de verbos.
- Perguntas longas, com muitas palavras fora da base, podem cair abaixo da cobertura mínima.
- A qualidade depende de `keywords` bem escolhidas e de revisão periódica das fontes.

Melhorias possíveis: tolerância a erros de digitação, mais temas e orientações, revisão periódica automática dos links e comparação com um modelo de linguagem confrontado com a base verificada.
