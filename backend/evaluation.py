"""Avaliação dos dois modelos de resposta (pacote 4).

Roda cada caso de teste nos modos ``direct`` e ``steps`` chamando
``backend.assistant.answer_question`` (a mesma lógica da API e do terminal),
mede o tempo de cada consulta, classifica acerto ou erro e calcula a taxa de
acerto e o tempo médio. Critérios em ``docs/avaliacao.md``.

Cada caso é avaliado em dois níveis:

* ``retrievalCorrect``: o status e a orientação escolhida são os esperados.
* ``responseCorrect``: além disso, a mensagem tem o que a resposta precisa ter
  (fonte, aviso, fatos esperados, opções, limite ou pedido de pergunta).

A **taxa de acerto** usa ``responseCorrect``; a taxa de recuperação fica ao lado
para separar erro de busca de erro de resposta.
"""

import json
import time
from collections.abc import Callable
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from backend import assistant
from backend.contracts import AnswerResponse
from backend.knowledge import TOPICS
from backend.search import normalize

MODES = ("direct", "steps")
STATUSES = ("matched", "ambiguous", "unsupported", "empty", "error")


def validate_cases(cases: Any) -> None:
    """Gera ``ValueError`` se o conjunto de casos estiver malformado."""
    if not isinstance(cases, list) or not cases:
        raise ValueError("Os casos de avaliação devem ser uma lista não vazia.")
    seen: set[str] = set()
    for position, case in enumerate(cases, start=1):
        if not isinstance(case, dict):
            raise ValueError(f"Caso {position}: deve ser um objeto JSON.")
        case_id = case.get("id")
        if not isinstance(case_id, str) or not case_id.strip():
            raise ValueError(f"Caso {position}: 'id' ausente ou vazio.")
        if case_id in seen:
            raise ValueError(f"Caso {case_id}: id duplicado.")
        seen.add(case_id)
        if not isinstance(case.get("question"), str):
            raise ValueError(f"Caso {case_id}: 'question' deve ser texto.")
        if case.get("expectedStatus") not in STATUSES:
            raise ValueError(f"Caso {case_id}: 'expectedStatus' deve ser um de {list(STATUSES)}.")
        if case["expectedStatus"] == "matched" and not case.get("expectedServiceId"):
            raise ValueError(f"Caso {case_id}: 'matched' exige 'expectedServiceId'.")
        facts = case.get("expectedFacts", [])
        if not isinstance(facts, list) or not all(isinstance(f, str) for f in facts):
            raise ValueError(f"Caso {case_id}: 'expectedFacts' deve ser uma lista de textos.")


def _contains(message: str, text: str) -> bool:
    return normalize(text) in normalize(message)


def _check_response(case: dict[str, Any], answer: dict[str, Any]) -> list[str]:
    """Problemas da mensagem; lista vazia significa resposta adequada."""
    status, message, services = answer["status"], answer["message"], answer["services"]
    problems: list[str] = []
    if status == "matched":
        record = services[0]
        if record["source"]["url"] not in message:
            problems.append("mensagem sem o link da fonte")
        if "Aviso:" not in message:
            problems.append("mensagem sem aviso de confirmação")
        problems += [
            f"fato ausente: {fact}"
            for fact in case.get("expectedFacts", [])
            if not _contains(message, fact)
        ]
    elif status == "ambiguous":
        problems += [
            f"opção não citada: {s['title']}" for s in services if s["title"] not in message
        ]
        if "?" not in message and "escolha" not in message.lower():
            problems.append("não pede para a pessoa escolher")
    elif status == "unsupported":
        if not _contains(message, "nao encontrei"):
            problems.append("não informa que a base não tem a resposta")
        if not any(label in message for label in TOPICS.values()):
            problems.append("não sugere temas")
    elif status == "empty":
        if not (_contains(message, "pergunta") or _contains(message, "duvida")):
            problems.append("não pede a pergunta")
    return problems


def _check_retrieval(case: dict[str, Any], answer: dict[str, Any]) -> list[str]:
    expected = case["expectedStatus"]
    if answer["status"] != expected:
        return [f"status {answer['status']} (esperado {expected})"]
    ids = [s["id"] for s in answer["services"]]
    if expected == "matched" and ids[0] != case["expectedServiceId"]:
        return [f"orientação {ids[0]} (esperada {case['expectedServiceId']})"]
    wanted = case.get("expectedServiceIds")
    if expected == "ambiguous" and wanted and set(ids) != set(wanted):
        return [f"opções {ids} (esperadas {wanted})"]
    return []


def run_case(
    records: list[dict[str, Any]],
    case: dict[str, Any],
    mode: str,
    clock: Callable[[], float] = time.perf_counter,
) -> dict[str, Any]:
    """Executa um caso em um modo e devolve o registro esperado/obtido/acerto/tempo."""
    request_mode = case.get("requestMode", mode)
    start = clock()
    try:
        answer = assistant.answer_question(records, case["question"], request_mode)
        error = None
    except ValueError as exc:
        answer, error = None, str(exc)
    duration_ms = (clock() - start) * 1000

    expected = {
        "status": case["expectedStatus"],
        "serviceId": case.get("expectedServiceId"),
        "serviceIds": case.get("expectedServiceIds"),
        "facts": case.get("expectedFacts", []),
    }
    if answer is None:
        actual = {"status": "error", "serviceIds": [], "message": error}
        retrieval = [] if case["expectedStatus"] == "error" else [f"erro inesperado: {error}"]
        response: list[str] = []
    else:
        actual = {
            "status": answer["status"],
            "serviceIds": [s["id"] for s in answer["services"]],
            "message": answer["message"],
        }
        if case["expectedStatus"] == "error":
            retrieval = [f"esperava erro, obteve {answer['status']}"]
            response = []
        else:
            try:
                AnswerResponse.model_validate(answer)
                retrieval = _check_retrieval(case, answer)
                response = [] if retrieval else _check_response(case, answer)
            except ValueError as exc:
                retrieval, response = [f"fora do contrato: {exc}"], []

    return {
        "caseId": case["id"],
        "category": case.get("category", "uncategorized"),
        "mode": mode,
        "requestMode": request_mode,
        "question": case["question"],
        "expected": expected,
        "actual": actual,
        "retrievalCorrect": not retrieval,
        "responseCorrect": not retrieval and not response,
        "problems": retrieval + response,
        "durationMs": round(duration_ms, 4),
    }


def _rate(part: int, total: int) -> float:
    return round(part / total, 4) if total else 0.0


def summarize(results: list[dict[str, Any]]) -> dict[str, Any]:
    """Taxa de acerto, taxa de recuperação e tempo médio por modo e por categoria."""
    summary: dict[str, Any] = {}
    for mode in dict.fromkeys(r["mode"] for r in results):
        rows = [r for r in results if r["mode"] == mode]
        correct = sum(r["responseCorrect"] for r in rows)
        retrieved = sum(r["retrievalCorrect"] for r in rows)
        categories: dict[str, dict[str, Any]] = {}
        for row in rows:
            bucket = categories.setdefault(row["category"], {"total": 0, "correct": 0})
            bucket["total"] += 1
            bucket["correct"] += row["responseCorrect"]
        for bucket in categories.values():
            bucket["accuracy"] = _rate(bucket["correct"], bucket["total"])
        summary[mode] = {
            "total": len(rows),
            "correct": correct,
            "accuracy": _rate(correct, len(rows)),
            "retrievalCorrect": retrieved,
            "retrievalAccuracy": _rate(retrieved, len(rows)),
            "meanDurationMs": round(sum(r["durationMs"] for r in rows) / len(rows), 4),
            "maxDurationMs": max(r["durationMs"] for r in rows),
            "failedCases": [r["caseId"] for r in rows if not r["responseCorrect"]],
            "byCategory": categories,
        }
    return summary


def evaluate_questions(
    records: list[dict[str, Any]],
    cases: list[dict[str, Any]],
    output_path: Path,
) -> dict[str, Any]:
    """Avalia os casos nos dois modos, salva o relatório em ``output_path`` e o devolve."""
    validate_cases(cases)
    results = [run_case(records, case, mode) for mode in MODES for case in cases]
    report = {
        "generatedAt": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "externalAi": False,
        "records": len(records),
        "criteria": {
            "accuracy": "respostas corretas (responseCorrect) ÷ perguntas, por modo",
            "retrievalAccuracy": "status e orientação corretos ÷ perguntas, por modo",
            "meanDurationMs": "média simples do tempo de answer_question, em milissegundos",
        },
        "summary": summarize(results),
        "cases": results,
    }
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return report
