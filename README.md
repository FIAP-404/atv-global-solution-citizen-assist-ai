# Citizen Assist AI

**Global Solution 2026.2 | FIAP | Grupo 404**

Projeto acadêmico para desenvolver um assistente digital introdutório de orientação cidadã, com consultas a uma base de informações verificadas, respostas acompanhadas de fontes e tratamento explícito de limitações.

## Front-end

Portal React com identidade FIAP e estrutura inspirada no GOV.BR. As telas de início, catálogo, orientação, assistente e apresentação do projeto já estão implementadas.

- Busca e filtros por documentos, trabalho e assistência social.
- Comparação de até três orientações.
- Orientações salvas apenas neste navegador, sem cadastro.
- Fontes, limitações, assuntos relacionados e checklist de preparação.
- Assistente demonstrativo com resposta direta ou em passos e tratamento de perguntas vazias, ambíguas e fora da base.
- Layout responsivo, navegação por teclado, alto contraste e impressão da orientação.

**Esta é a etapa de front-end.** A API Python ainda será implementada pela equipe. Os 15 registros são dados de demonstração e têm verificação de conteúdo pendente; as datas de revisão não foram preenchidas artificialmente. Os testes do navegador não substituem a avaliação final do sistema em Python.

### Como executar

Requer **Node.js 24 ou superior** e npm. Na raiz do repositório:

```bash
cd frontend
npm ci
npm run dev
```

Abra o endereço local informado pelo Vite. A navegação usa rotas com `#`, permitindo abrir páginas internas sem configurar redirecionamento no servidor de arquivos estáticos.

### Verificações e build

Na pasta `frontend`:

```bash
npm test
npm run build
npm run preview
```

O build é gerado em `frontend/dist/`. A suíte inclui 12 cenários de consulta da demonstração, além de testes de busca e integridade do catálogo.

### Conexão com Python

Sem configuração, a interface usa o adaptador de demonstração. Para conectar o backend, copie `frontend/.env.example` para `frontend/.env.local`, configure `VITE_API_BASE_URL` e reinicie o Vite.

Os endpoints consumidos e seus formatos estão no [contrato de integração](docs/api-contract.md). A [divisão de trabalho](docs/team-work-packages.md) separa quatro entregas: base e conteúdo; busca e navegação; respostas e integração HTTP; avaliação e evidências.

## Organização

| Caminho | Conteúdo |
|---|---|
| `frontend/` | Aplicação React, componentes, estilos e testes |
| `data/services.demo.json` | Quinze orientações iniciais, ainda em revisão |
| `data/demo-test-cases.json` | Doze cenários iniciais para a demonstração |
| `docs/assignment.md` | Enunciado transcrito |
| `docs/api-contract.md` | Contrato da futura API Python |
| `docs/team-work-packages.md` | Responsabilidades e critérios para os colegas |
| `docs/ai-usage.md` | Registro do apoio de IA e validação crítica |
| `docs/design/` | Especificação, direção visual e referências de marca |

## Conteúdo, privacidade e limites

O portal é um projeto acadêmico independente. Não representa um canal oficial de atendimento do governo ou da FIAP, não solicita documentos e não realiza serviços públicos. Cada orientação aponta para uma referência externa e explicita suas limitações.

No modo de demonstração, as consultas usam dados locais e não chamam um modelo de IA externo. Apenas identificadores de orientações salvas são persistidos no navegador; mensagens e checklists não são gravados. A opção de apagar os salvos fica na página sobre o projeto.

## O que falta para a entrega acadêmica

- Confirmar integrantes e RMs.
- Revisar as 15 orientações, suas fontes, relações e datas de verificação.
- Implementar e integrar o backend Python e a execução por terminal.
- Documentar e comparar os dois modelos de instrução da resposta.
- Executar a avaliação em Python, registrar acertos e tempos, interpretar os resultados e realizar o teste de usabilidade.
- Concluir a documentação, o vídeo e o TXT com os dois links exigidos.
- Conferir a estrutura de submissão e os caminhos de arquivos citados literalmente no enunciado, incluindo `src/sistema.py` e `docs/uso_ia.md`; o código novo deste repositório segue nomes em inglês.

Ainda não há vídeo de apresentação nem métricas finais de desempenho.

## Enunciado

O [enunciado da atividade](docs/assignment.md) foi transcrito da captura em PDF fornecida em 18/11/2026. As duas tabelas sem conteúdo visível na captura estão sinalizadas no documento.

- **Prazo exibido na plataforma:** 19/11/2026, às 23h59.
- **Organização no GitHub:** [FIAP-404](https://github.com/FIAP-404).
- **Repositório:** [atv-global-solution-citizen-assist-ai](https://github.com/FIAP-404/atv-global-solution-citizen-assist-ai).

O enunciado é material de referência da atividade. Os requisitos nele transcritos descrevem a futura entrega; não indicam funcionalidades já implementadas.
