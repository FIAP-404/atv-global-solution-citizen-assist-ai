# Teste de usabilidade

> **Situação (19/11/2026):** o roteiro foi executado por **roteiro de tarefas, conduzido por um agente de IA (Claude Code) operando o navegador**, na interface web conectada à API Python. **Não houve participante humano.** O enunciado aceita "usuário de teste ou roteiro de tarefas"; os resultados abaixo são o que foi observado de fato nessa execução, sem notas de satisfação inventadas. A sessão com uma pessoa real continua recomendada (tabela em branco mais abaixo).

## Objetivo

Verificar se uma pessoa sem familiaridade com o projeto consegue: (1) achar a orientação certa perguntando com as próprias palavras, (2) entender a resposta e onde confirmá-la e (3) lidar com perguntas sem resposta ou ambíguas. Também queremos saber qual modelo de resposta (`direct` ou `steps`) ela acha mais claro.

## Participantes

- Pelo menos 1 pessoa de fora do grupo; idealmente alguém com pouca familiaridade com portais públicos.
- Registrar apenas um apelido, a faixa etária e a familiaridade com o gov.br (baixa, média ou alta). **Não coletar** CPF, nome completo nem dados pessoais (a mesma regra de privacidade do projeto).

## Preparação

- Interface web conectada à API Python (`uvicorn backend.api:app` + `npm run dev` com `.env.local`). Na falta dela, usar o terminal (`python -m src.main --question "..." --mode ...`).
- Um observador anota; quem conduz não ajuda, salvo se a pessoa travar por mais de 2 minutos (registrar como "precisou de ajuda").
- Pedir que a pessoa pense em voz alta.

## Tarefas

| # | Tarefa dada à pessoa (não ler o nome do serviço) | Modo | Sucesso quando |
| --- | --- | --- | --- |
| T1 | "Você foi demitido sem justa causa. Descubra o que pedir e por onde." | `direct` | Chega ao Seguro-desemprego e diz qual canal usar |
| T2 | "Descubra quais documentos separar para sacar o FGTS." | `steps` | Cita ao menos 2 documentos da resposta |
| T3 | "Descubra quanto custa tirar o passaporte." | `direct` | Entende que o valor **não** está no assistente e onde confirmar |
| T4 | "Pergunte só 'documento' e chegue à orientação do título de eleitor." | `direct` | Escolhe a opção na pergunta ambígua e abre a orientação |
| T5 | "Pergunte como tirar a carteira de motorista." | `steps` | Entende que não há orientação e identifica os temas sugeridos |
| T6 | "Encontre onde fica o CRAS da sua cidade." | à escolha | Entende que o atendimento é presencial/municipal e acha a fonte |
| T7 | Repetir T1 no outro modo e responder: "Qual das duas respostas foi mais fácil de entender? Por quê?" | os dois | Preferência e motivo registrados |

## Perguntas finais (escala de 1 a 5)

1. Foi fácil fazer a pergunta?
2. Entendi a resposta.
3. Ficou claro que preciso confirmar a informação no canal oficial.
4. Confiaria nesta orientação como primeiro passo.
5. Comentário livre: o que mais atrapalhou?

## Registro da sessão

**Data:** ______ **Condutor:** ______ **Participante:** ______ (faixa etária ____, familiaridade com o gov.br ____) **Canal:** web / terminal

| Tarefa | Concluiu? (sim / com ajuda / não) | Tempo | Pergunta digitada | Dificuldades observadas |
| --- | --- | --- | --- | --- |
| T1 | | | | |
| T2 | | | | |
| T3 | | | | |
| T4 | | | | |
| T5 | | | | |
| T6 | | | | |
| T7 | Preferência: ______ | | | Motivo: |

| Pergunta final | Nota (1–5) |
| --- | --- |
| Facilidade de perguntar | |
| Entendimento da resposta | |
| Clareza do aviso de confirmação | |
| Confiança como primeiro passo | |

**Comentários:**

## Resultados e dificuldades

### Execução do roteiro por agente (19/11/2026)

**Ambiente:** `uvicorn backend.api:app` + `npm run dev` (Vite), navegador embutido, janela de 1024×768. As perguntas foram escritas como uma pessoa leiga escreveria, sem usar o nome exato do serviço quando a tarefa não o dava.

| Tarefa | Pergunta digitada | Modo | Resultado na 1ª passada | Observação |
| --- | --- | --- | --- | --- |
| T1 | `fui demitido sem justa causa, o que eu faço?` | direto | **Concluída** | Chega ao Seguro-desemprego, com canais (Portal, app, 158, FACILITA) na primeira frase. Os canais se repetem na mensagem e no resumo. |
| T2 | `quais documentos preciso pra sacar o fgts` | passo a passo | **Concluída** | Os documentos aparecem na etapa 1. A resposta também traz o procedimento inteiro e repete os passos abaixo, então fica longa. |
| T3 | `quanto custa tirar passaporte?` | direto (pretendido) | **Não concluída** | (a) O clique em "Resposta direta" não funcionava, porque o rótulo ficava com largura 0 ao lado da legenda flutuante (defeito de CSS). (b) A pergunta foi recusada: "tirar" não está nas palavras-chave e a cobertura caiu para 50%. |
| T4 | `documento` → clicar em "Título e situação eleitoral" | direto | **Concluída** | A pergunta ambígua mostra 3 opções clicáveis, e a escolhida abre a página da orientação. O conteúdo do título de eleitor era genérico. |
| T5 | `como tirar a carteira de motorista?` | passo a passo | **Concluída** | A pergunta é recusada sem inventar nada, com sugestões de temas e o link "Explorar todos os serviços". |
| T6 | `onde fica o CRAS da minha cidade?` | passo a passo | **Concluída só após reformular** | A pergunta original foi recusada ("cidade" derruba a cobertura). `onde fica o CRAS?` funciona e explica que o atendimento é municipal e presencial. |
| T7 | T1 repetida no modo passo a passo | os dois | Registrada | Passo a passo: cerca de 1.500 caracteres, com documentos do requerimento, gov.br e conta bancária; mais completo, mas longo. Direto: responde "o que pedir e por onde" logo no início. |

**Taxa de conclusão na 1ª passada:** 4 de 6 tarefas objetivas (T1, T2, T4 e T5); T3 falhou e T6 precisou de reformulação.

**Correções feitas a partir da sessão** (mesmo dia, com os testes refeitos):

1. **Seletor de modo:** `clear: both` nos rótulos de `.response-mode` (`frontend/src/styles.css`). As duas opções voltam a aparecer e a funcionar.
2. **"tirar passaporte":** a palavra-chave foi adicionada ao passaporte. Tratar "tirar" como palavra ignorada foi testado e descartado, porque fazia "Como tirar o CPF?" virar ambígua.
3. **Custo e prazo:** antes, o assistente dizia "a base não informa valores" mesmo quando o registro trazia o valor (passaporte, abono, CPF em conveniadas) ou o prazo (FGTS, seguro-desemprego). Agora ele cita a frase do registro e pede confirmação na fonte; só diz "não informa" quando não há dado.
4. **Conteúdo:** 7 orientações ainda tinham resumo genérico ("Encontre…", "Localize…"): situação do CPF, CIN, passaporte, título de eleitor, Bolsa Família, BPC e CRAS. Elas foram reescritas com informações das páginas oficiais. A do TSE foi lida no navegador, porque bloqueia leitura automatizada.
5. **Textos da interface:** o rodapé e a página "Sobre" ainda diziam que as orientações "passam por revisão" e que as datas "serão exibidas"; foram atualizados.

**Depois das correções:** T3 é concluída ("A base informa: ... a taxa comum é de R$ 257,25 ..."). T6 com "da minha cidade" continua recusada; é a melhoria 2 de `docs/avaliacao.md`, não implementada.

**Modelo preferido:** não registrado, porque preferência é uma opinião humana. Pelo critério objetivo do roteiro, o modo **direto** respondeu à pergunta mais cedo em T1 e T3, e o **passo a passo** deu mais apoio de preparação em T2. Isso é coerente com `docs/avaliacao.md`, onde o passo a passo tem 63% mais texto.

**Limites desta execução:** o agente conhece a base e o código, não lê "em voz alta", não tem dificuldade de leitura nem de navegação e não pode responder às perguntas de 1 a 5. A sessão mede se o fluxo **funciona** com perguntas de leigo, não se ele é **fácil** para uma pessoa. Por isso a tabela de registro com participante humano ficou em branco.

## Pontos de atenção levantados antes da sessão

Estes pontos vêm da revisão da equipe e da avaliação automática, **não** de usuário. Servem para orientar o que observar:

- Na avaliação automática, perguntas com erro de digitação ou muito longas não foram respondidas. Observar se o participante escreve assim e se, ao receber "não encontrei", consegue reformular.
- Na T6, `onde fica o CRAS?` é respondida, mas `onde fica o CRAS da minha cidade?` não: "cidade" derruba a cobertura mínima da busca (melhoria 2 de `docs/avaliacao.md`). É provável que o participante escreva assim.
- O modelo `steps` gera mensagens de até ~1.600 caracteres. Observar se a pessoa lê até a fonte e o aviso.
- Na pergunta ambígua, a pessoa precisa clicar em uma opção ou reescrever; observar se isso fica claro.
