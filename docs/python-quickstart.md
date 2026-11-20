# Comece por aqui: Python

O projeto está na branch `main`. Atualizem a cópia local antes de criar a branch do próprio módulo:

```powershell
git switch main
git pull --ff-only origin main
```

Escolham entre vocês quem implementa cada um dos quatro módulos descritos em [team-work-packages.md](team-work-packages.md).

**O assistente não usa IA externa.** Ele consulta a base verificada e aplica dois modelos de instrução de resposta. FastAPI conecta as funções ao React; a execução por terminal reutiliza as mesmas funções.

Antes de implementar, leiam [o mapa de conteúdo e entregas](content-and-handoff.md): as orientações finais precisam responder dentro do portal, e não apenas mandar o usuário pesquisar em outro site. As telas e o formato dos dados já comportam esse conteúdo.

## Instalar

Requer Python 3.11 ou superior; a estrutura foi testada em Python 3.13.9. Na raiz do repositório, usando PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
```

No macOS/Linux, use `.venv/bin/python` no lugar de `.\.venv\Scripts\python.exe`.

## Verificar a estrutura

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Os testes iniciais verificam API e terminal usando funções substitutas nos testes. Eles continuam úteis quando os módulos forem implementados, mas não comprovam a busca real, a revisão das fontes ou as métricas finais.

## Iniciar a API

```powershell
.\.venv\Scripts\python.exe -m uvicorn backend.api:app --host 127.0.0.1 --port 8000 --reload
```

- Documentação interativa: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).
- Verificação do transporte: [http://127.0.0.1:8000/api/v1/health](http://127.0.0.1:8000/api/v1/health).
- Catálogo: [http://127.0.0.1:8000/api/v1/services](http://127.0.0.1:8000/api/v1/services).

Os quatro módulos (base, busca, respostas e avaliação) estão implementados, e as consultas retornam respostas reais da base. A resposta **HTTP 503** com `error="module_pending"` só aparece se algum módulo voltar a levantar `ModuleNotReadyError`. Um retorno positivo de `/health` confirma apenas o servidor HTTP.

## Terminal

```powershell
.\.venv\Scripts\python.exe -m src.main --question "CPF" --mode direct
.\.venv\Scripts\python.exe -m src.main --question "Carteira de Trabalho Digital" --mode steps
.\.venv\Scripts\python.exe -m src.main --evaluate --output results/evaluation.json
```

A base usada é a definida em `backend/config.py` (`data/services.demo.json`, com as orientações revisadas pelo pacote 1). Erros de entrada, como uma pergunta acima de 500 caracteres, encerram o comando com código 2 e uma mensagem explícita.

`--evaluate` usa por padrão o conjunto de avaliação `data/demo-test-cases.json` (56 perguntas) e grava `results/evaluation.json`. Critérios e resultados em [`avaliacao.md`](avaliacao.md).

## Conectar o front-end

```powershell
Copy-Item frontend/.env.example frontend/.env.local
cd frontend
npm ci
npm run dev
```

O arquivo de exemplo já aponta para `http://127.0.0.1:8000/api/v1`. Reinicie o Vite quando alterar variáveis de ambiente.

Os modos são separados: sem `.env.local`, a interface usa a demonstração em JavaScript; com o endereço configurado, ela usa Python e exibe erro se o servidor falhar. Não ocorre retorno silencioso à demonstração quando o backend falha.

## Entregar a própria parte

1. Criar a branch do módulo a partir da versão atual do projeto.
2. Implementar a função com a assinatura definida, adicionando os testes da própria lógica em `tests/`.
3. Executar a suíte Python e corrigir falhas.
4. Documentar como a parte funciona e suas limitações, incluindo evidências quando aplicável.
5. Enviar a branch ou pull request para o coordenador integrar. Não alterar o contrato sem combinar.

O enunciado cita os caminhos `src/sistema.py` e `docs/uso_ia.md`. Os arquivos novos usam inglês conforme a regra do projeto; o coordenador deve conferir os nomes finais exigidos antes da submissão.
