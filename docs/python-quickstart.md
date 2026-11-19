# Comece por aqui: Python

O projeto está na branch `feat/citizen-portal-frontend`. Escolham entre vocês quem implementa cada um dos quatro módulos descritos em [team-work-packages.md](team-work-packages.md).

**O assistente não usa IA externa.** Ele consulta a base verificada e aplica dois modelos de instrução de resposta. FastAPI conecta as funções ao React; a execução por terminal reutiliza as mesmas funções.

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

Enquanto os módulos estiverem pendentes, consultas retornam **HTTP 503**, com `error="module_pending"` e o módulo que falta implementar. Um retorno positivo de `/health` confirma apenas o servidor HTTP, não a conclusão do trabalho.

## Terminal

```powershell
.\.venv\Scripts\python.exe -m src.main --question "CPF" --mode direct
.\.venv\Scripts\python.exe -m src.main --question "Carteira de Trabalho Digital" --mode steps
.\.venv\Scripts\python.exe -m src.main --evaluate --output results/evaluation.json
```

Esses comandos também informam erro explícito enquanto a função necessária estiver pendente. A base final esperada é `data/services.json`. Não renomeiem a base de demonstração como se o conteúdo já tivesse sido verificado.

Para usar o conjunto final de perguntas, especifiquem `--cases data/test-cases.json` depois de criarem esse arquivo. Sem esse argumento, o comando começa pelos 12 cenários iniciais.

## Conectar o front-end

```powershell
Copy-Item frontend/.env.example frontend/.env.local
cd frontend
npm ci
npm run dev
```

O arquivo de exemplo já aponta para `http://127.0.0.1:8000/api/v1`. Reinicie o Vite quando alterar variáveis de ambiente.

Os modos são separados: sem `.env.local`, a interface usa a demonstração em JavaScript; com o endereço configurado, ela usa Python e exibe erro se uma função estiver pendente. Não ocorre retorno silencioso à demonstração quando o backend falha.

## Entregar a própria parte

1. Criar a branch do módulo a partir da versão atual do projeto.
2. Implementar a função com a assinatura definida, adicionando os testes da própria lógica em `tests/`.
3. Executar a suíte Python e corrigir falhas.
4. Documentar como a parte funciona e suas limitações, incluindo evidências quando aplicável.
5. Enviar a branch ou pull request para o coordenador integrar. Não alterar o contrato sem combinar.

O enunciado cita os caminhos `src/sistema.py` e `docs/uso_ia.md`. Os arquivos novos usam inglês conforme a regra do projeto; o coordenador deve conferir os nomes finais exigidos antes da submissão.
