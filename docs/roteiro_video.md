# Roteiro do vídeo: Citizen Assist AI (máx. 5 min)

Vídeo de tela narrado: a gravação mostra o portal web conectado à API Python, o menu de terminal (`python src/sistema.py`) e os indicadores medidos. A narração foi gravada por Caetano lendo as falas abaixo; a gravação de tela foi sincronizada com cada trecho da fala. Os números vêm de `results/evaluation.json` (execução de 19/11/2026).

| # | Trecho | Tela | Itens do enunciado |
|---|---|---|---|
| 1 | Abertura | Capa com equipe e página inicial do portal | Problema, público, temas, aviso não oficial |
| 2 | Base de conhecimento | Catálogo e página de uma orientação | 15 registros, 3 temas, campos, fonte e data |
| 3 | Busca e navegação | Orientação → assuntos relacionados | Listas/dicionários, hierarquia, grafo, ranking, empates |
| 4 | Pergunta direta | Assistente: "fui demitido sem justa causa" | Fluxo completo com fonte e aviso |
| 5 | Dúvida específica e modelos | Custo do passaporte (direto) e documentos do FGTS (passo a passo) | Dois modelos de resposta |
| 6 | Limitações | "documento" (ambígua), "carteira de motorista" (fora da base) | Ambiguidade e ausência de resposta |
| 7 | Terminal | `python src/sistema.py` | Menu, opção inexistente, entrada vazia |
| 8 | Avaliação | Indicadores | 56 perguntas, acerto, tempo, usabilidade |
| 9 | Fechamento | Capa final | Privacidade, IA, limitações e melhorias |

## Falas

1. **Abertura.** "Este é o Citizen Assist AI, do Grupo 404 da FIAP, feito por Caetano, Fernando, Joedson e Mylena. Quem procura orientação sobre documentos, trabalho ou benefícios sociais costuma encontrar informação espalhada e difícil de entender. O nosso assistente organiza orientações conferidas em fontes oficiais, responde em linguagem simples, sempre mostra a fonte e avisa quando não sabe. É um projeto acadêmico: ele não é um canal oficial do governo e não realiza nenhum serviço."

2. **Base de conhecimento.** "A base é um arquivo JSON com quinze orientações em três temas: documentos, trabalho e assistência social, cinco em cada. Cada registro tem identificador, tema, palavras-chave, resumo, público, passos, o que separar, limitações e a referência oficial com a data de verificação. O Python lê o arquivo, valida os campos obrigatórios e recusa com mensagens claras um arquivo ausente, vazio, malformado, com identificadores duplicados ou com relações quebradas. Para corrigir uma orientação, basta editar o JSON, sem mexer nas regras do programa."

3. **Busca e navegação.** "Os registros ficam em listas e dicionários, com acesso por identificador e por tema. Os temas formam uma hierarquia, e as orientações relacionadas formam um grafo: cada orientação aponta para pelo menos três outras, e a navegação percorre esse grafo em largura, como aqui, do seguro-desemprego para o FGTS. A busca normaliza acentos e maiúsculas, usa sinônimos e dá mais peso ao título e às palavras-chave. Ela exige que a maior parte da pergunta seja coberta, para não responder por uma palavra solta. Quando duas orientações empatam, a pergunta é tratada como ambígua."

4. **Pergunta direta.** "Vamos ao assistente. Uma pessoa escreve com as próprias palavras: fui demitido sem justa causa, o que eu faço? A resposta identifica o seguro-desemprego, diz por onde pedir, cita o órgão responsável, a fonte oficial com a data de verificação e o aviso de que é preciso confirmar no canal oficial. Abaixo, aparecem o resumo, as limitações e o link da fonte."

5. **Dúvida específica e modelos.** "O assistente também identifica o tipo de dúvida. Para o custo do passaporte, ele cita o valor que está na base, de duzentos e cinquenta e sete reais e vinte e cinco centavos, e pede para confirmar na Polícia Federal. Quando a base não tem o dado, ele diz isso, em vez de inventar. Temos dois modelos de instrução de resposta: o direto, curto, e o passo a passo, que organiza o que separar, o canal e os passos. Aqui, os documentos para sacar o FGTS no modo passo a passo."

6. **Limitações.** "Agora, os limites. Se a pessoa escreve só documento, a pergunta combina com mais de um assunto, então o assistente pede para escolher uma opção e leva até a orientação escolhida. Se a pergunta está fora da base, como tirar a carteira de motorista, ele não inventa instruções: avisa que não encontrou informação suficiente e sugere os temas disponíveis."

7. **Terminal.** "A mesma lógica roda no terminal, com python src barra sistema ponto py. O menu permite escolher um tema, abrir uma orientação com a fonte, seguir para assuntos relacionados ou fazer uma pergunta. Entrada vazia e opção inexistente recebem mensagens explicativas. O terminal e a interface web usam a mesma base e o mesmo código de resposta."

8. **Avaliação.** "Para avaliar, rodamos cinquenta e seis perguntas de teste nos dois modelos: diretas, reformulações, dúvidas específicas, perguntas fora da base, entradas vazias, ambíguas e inválidas. A taxa de acerto foi de noventa e seis vírgula quatro por cento nos dois modelos, com tempo médio abaixo de dois milissegundos por consulta. Os dois erros foram um erro de digitação e uma pergunta longa, e nos dois o assistente recusou, em vez de indicar uma orientação errada. No roteiro de usabilidade, executado por tarefas, encontramos e corrigimos um defeito no seletor de modo e respostas de custo que ignoravam dados da base."

9. **Fechamento.** "O assistente não pede dados pessoais, não decide quem tem direito a benefícios e não usa inteligência artificial externa: as respostas saem das regras e da base verificada, e o uso de IA no desenvolvimento está documentado no repositório. As principais melhorias são tolerar erros de digitação, entender perguntas longas e ampliar a base. Obrigado!"
