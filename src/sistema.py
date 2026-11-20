"""Menu textual do Citizen Assist AI: ``python src/sistema.py``.

Reúne em um só fluxo o que o enunciado pede: escolher um tema no menu ou
digitar uma pergunta, ver orientação + fonte + aviso, navegar por assuntos
relacionados e receber mensagens claras para entradas inválidas.
Usa a mesma base e a mesma lógica da API (sem IA externa).
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend import assistant, knowledge, search  # noqa: E402
from backend.config import DATA_PATH  # noqa: E402

AVISO = (
    "Projeto acadêmico, não é canal oficial. Não informe dados pessoais. "
    "Confirme os requisitos atualizados na fonte oficial."
)
MODOS = {"direct": "direto", "steps": "passo a passo"}


def ler(prompt: str) -> str | None:
    try:
        return input(prompt).strip()
    except EOFError:
        return None


def escolher(opcoes: list[str], titulo: str) -> int | None:
    """Mostra opções numeradas; devolve o índice escolhido ou None para voltar."""
    print(f"\n{titulo}")
    for i, texto in enumerate(opcoes, 1):
        print(f"  {i}. {texto}")
    print("  0. Voltar")
    while True:
        valor = ler("Opção: ")
        if valor is None or valor == "0":
            return None
        if not valor:
            print("Entrada vazia. Digite o número de uma opção.")
        elif not valor.isdigit() or not 1 <= int(valor) <= len(opcoes):
            print(f"Opção inexistente. Escolha entre 0 e {len(opcoes)}.")
        else:
            return int(valor) - 1


def mostrar_orientacao(record: dict) -> None:
    fonte = record["source"]
    print(f"\n=== {record['title']} ===")
    print(record["summary"])
    print(f"Para quem: {record['audience']}")
    print("Passos:")
    for i, passo in enumerate(record["steps"], 1):
        print(f"  {i}. {passo}")
    print(f"Órgão: {record['agency']}")
    print(f"Fonte: {fonte['title']} - {fonte['url']} (verificada em {fonte.get('reviewedAt') or 'sem data'})")
    print(f"Aviso: {record['limitations']}")


def navegar(records: list[dict], record: dict) -> None:
    """Mostra a orientação e oferece assuntos relacionados para continuar."""
    while record is not None:
        mostrar_orientacao(record)
        relacionados = search.related_services(records, record["id"])
        if not relacionados:
            return
        idx = escolher([r["title"] for r in relacionados], "Assuntos relacionados:")
        record = relacionados[idx] if idx is not None else None


def menu_temas(records: list[dict]) -> None:
    temas = knowledge.list_topics(records)
    grupos = knowledge.group_by_topic(records)
    idx = escolher([f"{t['label']} ({t['count']})" for t in temas], "Temas disponíveis:")
    if idx is None:
        return
    itens = grupos[temas[idx]["id"]]
    escolha = escolher([r["title"] for r in itens], f"Orientações de {temas[idx]['label']}:")
    if escolha is not None:
        navegar(records, itens[escolha])


def perguntar(records: list[dict], modo: str) -> None:
    pergunta = ler("\nDigite sua pergunta (sem dados pessoais): ")
    if pergunta is None:
        return
    try:
        resposta = assistant.answer_question(records, pergunta, modo)
    except ValueError as erro:
        print(f"Não foi possível consultar: {erro}")
        return
    print(f"\n[{resposta['status']}] {resposta['message']}")
    servicos = resposta["services"]
    if resposta["status"] == "matched" and servicos:
        navegar(records, servicos[0])
    elif resposta["status"] == "ambiguous" and servicos:
        idx = escolher([r["title"] for r in servicos], "Qual destas você procura?")
        if idx is not None:
            navegar(records, servicos[idx])


def main() -> int:
    for stream in (sys.stdin, sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    try:
        records = knowledge.load_services(DATA_PATH)
    except (OSError, ValueError) as erro:
        print(f"Erro ao carregar a base de conhecimento: {erro}", file=sys.stderr)
        return 2

    print("Citizen Assist AI - orientação cidadã")
    print(AVISO)
    modo = "direct"
    while True:
        print(f"\nMenu principal (modo de resposta: {MODOS[modo]})")
        print("  1. Escolher um tema")
        print("  2. Fazer uma pergunta")
        print("  3. Trocar modo de resposta")
        print("  0. Sair")
        opcao = ler("Opção: ")
        if opcao is None or opcao == "0":
            print("Até logo.")
            return 0
        if opcao == "1":
            menu_temas(records)
        elif opcao == "2":
            perguntar(records, modo)
        elif opcao == "3":
            modo = "steps" if modo == "direct" else "direct"
            print(f"Modo alterado para {MODOS[modo]}.")
        elif not opcao:
            print("Entrada vazia. Digite 1, 2, 3 ou 0.")
        else:
            print("Opção inexistente. Digite 1, 2, 3 ou 0.")


if __name__ == "__main__":
    raise SystemExit(main())
