# Teste de usabilidade

> **Situação:** roteiro pronto; **sessão com usuário ainda não realizada.** As tabelas de resultado abaixo devem ser preenchidas por quem conduzir o teste, com o que foi observado. Não preencher com resultados estimados.

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

[PREENCHER após a sessão: taxa de conclusão das tarefas, principais dificuldades, modelo preferido e relação com os indicadores de `docs/avaliacao.md`.]

## Pontos de atenção levantados antes da sessão

Estes pontos vêm da revisão da equipe e da avaliação automática, **não** de usuário. Servem para orientar o que observar:

- Na avaliação automática, perguntas com erro de digitação ou muito longas não foram respondidas. Observar se o participante escreve assim e se, ao receber "não encontrei", consegue reformular.
- Na T6, `onde fica o CRAS?` é respondida, mas `onde fica o CRAS da minha cidade?` não: "cidade" derruba a cobertura mínima da busca (melhoria 2 de `docs/avaliacao.md`). É provável que o participante escreva assim.
- O modelo `steps` gera mensagens de até ~1.600 caracteres. Observar se a pessoa lê até a fonte e o aviso.
- Na pergunta ambígua, a pessoa precisa clicar em uma opção ou reescrever; observar se isso fica claro.
