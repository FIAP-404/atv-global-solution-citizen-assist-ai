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

Arquivo JSON em `data/services.demo.json` (caminho definido em `backend/config.py`). A leitura e a validação ficam em `backend/knowledge.py`, sem depender da camada HTTP.

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
python -m backend.knowledge                      # valida data/services.demo.json
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

**Plano de testes:** `data/demo-test-cases.json` traz 56 perguntas, executadas nos dois modelos de resposta (112 consultas):

| Tipo | Casos | Exemplos |
|---|---|---|
| Direta | 14 | `Bolsa Família`, `Como consultar FGTS?` |
| Reformulação | 19 | `fui mandado embora`, `CTPS`, `benefício idoso`, `cadunco` |
| Dúvida específica | 8 | `quanto custa o passaporte?`, `Quem tem direito ao BPC?` |
| Fora da base | 7 | `Qual a previsão do tempo?`, `Como tirar carteira de motorista?` |
| Limite | 5 | entrada vazia, `?!`, `como`, `documento`, `carteira` |
| Entrada inválida | 3 | texto com mais de 500 caracteres, modo inexistente, `opção 4` |

```bash
python -m src.main --evaluate --output results/evaluation.json
```

Uma resposta é considerada correta quando o status e a orientação são os esperados **e** a mensagem traz o que precisa (fonte, aviso e fatos esperados; opções; limite e temas; ou pedido da pergunta). Critérios e campos em [`docs/avaliacao.md`](docs/avaliacao.md).

| Indicador | `direct` | `steps` |
|---|---|---|
| Perguntas testadas | 56 | 56 |
| Acertos | 54 | 54 |
| Taxa de acerto | 96,4% | 96,4% |
| Tempo médio de consulta | 1,54 ms | 1,49 ms |

Os 2 erros são os mesmos nos dois modelos: erro de digitação (`cadunco`) e uma pergunta longa. Nos dois, o assistente recusou em vez de indicar uma orientação errada.

**Teste de usabilidade:** o roteiro de tarefas está em [`docs/teste-usabilidade.md`](docs/teste-usabilidade.md). [PREENCHER após a sessão: quem testou, dificuldades e resultados.]

**Interpretação e limitações da avaliação:** em [`docs/avaliacao.md`](docs/avaliacao.md). Em resumo, as perguntas diretas, fora da base e de limite acertam 100%; o ponto fraco são as reformulações (89%). Os casos foram escritos pela equipe, e a verificação de fatos é literal e baseada na própria base, então não mede a utilidade percebida.

## 6. Como executar

Requer **Python 3.11 ou superior**. Na raiz do projeto (no macOS/Linux, use `.venv/bin/python`):

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

**Menu interativo (comando do enunciado):**

```powershell
.\.venv\Scripts\python.exe src/sistema.py
```

O menu permite escolher um tema, abrir uma orientação (resumo, passos, fonte, data de verificação e aviso), seguir para assuntos relacionados, fazer uma pergunta em texto e alternar entre os modos direto e passo a passo. Entrada vazia, opção inexistente, pergunta ambígua e pergunta sem correspondência recebem mensagens explicativas.

**Pergunta única (JSON, usado nos exemplos e na avaliação):**

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

Respostas reais do terminal (`python -m src.main --question "..." --mode direct`), com a base `data/services.demo.json`. Os links das fontes foram abreviados aqui; a resposta traz o link completo.

| Entrada | Status | Resposta obtida (`message`) |
|---|---|---|
| `Onde faço o CadÚnico?` | `matched` (`social-registry`) | Cadastro Único: O atendimento é feito presencialmente. Órgão responsável: Ministério do Desenvolvimento e Assistência Social. Para começar: Leia a página oficial de inscrição no Cadastro Único. Fonte: GOV.BR · Inscrever-se no Cadastro Único (gov.br/pt-br/servicos/inscrever-se-no-cadastro-unico-...), verificada em 19/11/2026. Aviso: este assistente é um projeto acadêmico, não é canal oficial; confirme os requisitos atualizados na fonte antes de ir ao atendimento. |
| `quanto custa o passaporte?` | `matched` (`passport`) | Passaporte brasileiro: A base não informa valores ou taxas para Passaporte brasileiro, então não vou estimar; esse dado precisa ser conferido na fonte oficial. O atendimento é feito por canais digitais e presenciais. Órgão responsável: Polícia Federal. Fonte: Polícia Federal · Passaporte (gov.br/pt-br/servicos/obter-passaporte-comum-para-brasileiro), verificada em 19/11/2026. Aviso: (...) |
| `documento` | `ambiguous` (`cpf`, `identity`, `voter`) | Sua pergunta pode se referir a mais de um assunto: Inscrição no CPF, Carteira de Identidade Nacional ou Título e situação eleitoral. Qual deles você procura? Escolha uma opção para ver a orientação com a fonte. |
| `Qual a previsão do tempo?` | `unsupported` | Não encontrei informação suficiente na base para orientar sobre essa dúvida e não vou inventar instruções. Posso ajudar com: Documentos (Inscrição no CPF, Situação cadastral do CPF); Trabalho (Carteira de Trabalho Digital, Seguro-desemprego); Assistência social (Cadastro Único, Programa Bolsa Família). Tente reformular citando o serviço que procura. |
| `   ` (vazia) | `empty` | Digite sua pergunta ou escolha um dos temas (Documentos, Trabalho, Assistência social). |

Mesma consulta no modelo passo a passo (`--mode steps`), para `Quais documentos preciso levar para o seguro-desemprego?`:

> Seguro-desemprego, em etapas: 1) Separe antes: Ter o Documento do Requerimento do Seguro-Desemprego, entregue pelo empregador no momento da dispensa sem justa causa; Ter o número do CPF; Ter conta gov.br de nível Bronze, Prata ou Ouro; (...) 2) O atendimento é feito por canais digitais e presenciais. Órgão responsável: Ministério do Trabalho e Emprego. 3) Siga os 4 passos da orientação, começando por: Peça o benefício pelo Portal de Serviços, pelo aplicativo da Carteira de Trabalho Digital, pelo telefone 158 ou pela Plataforma FACILITA (...). 4) Confira na fonte se os requisitos continuam os mesmos. Fonte: GOV.BR · Solicitar o Seguro-Desemprego (gov.br/pt-br/servicos/solicitar-o-seguro-desemprego), verificada em 19/11/2026. Aviso: (...)

Na API e no terminal, a resposta `matched` também inclui o registro completo em `services` (resumo, passos, preparação e limitações), que a interface web exibe abaixo da mensagem.

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
| `src/` | Entrada por terminal: `sistema.py` (menu interativo) e `main.py` (pergunta única e avaliação) |
| `backend/` | Base de conhecimento, busca, assistente, avaliação e API |
| `data/` | Base de orientações e casos de teste |
| `tests/` | Testes Python |
| `frontend/` | Interface web opcional (React) |
| `docs/` | Enunciado, contrato da API, base, busca e registro de uso de IA |

## 11. Conclusões, limitações e melhorias

O assistente responde com fonte e aviso em todas as orientações encontradas e não respondeu nenhuma pergunta fora da base (96,4% de acerto nos dois modelos). O modelo `direct` foi mantido como padrão, por ser mais curto e responder primeiro ao que foi perguntado.

Limitações já conhecidas da busca:

- Não trata erros de digitação (`cadunco`) nem conjugações de verbos.
- Perguntas longas, com muitas palavras fora da base, podem cair abaixo da cobertura mínima.
- A qualidade depende de `keywords` bem escolhidas e de revisão periódica das fontes.

Melhorias possíveis (detalhes em [`docs/avaliacao.md`](docs/avaliacao.md)): tolerância a erros de digitação, cobertura calculada só sobre o vocabulário da base em perguntas longas, `keywords` com termos populares, mais temas e orientações, revisão periódica automática dos links e comparação com um modelo de linguagem confrontado com a base verificada.
