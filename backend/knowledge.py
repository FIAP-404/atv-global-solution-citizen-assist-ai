"""Funções para carregar, validar e consultar a base de conhecimento.

A base é uma lista JSON de orientações (consulte ``docs/knowledge-base.md``).
Este módulo não depende da camada HTTP, então a API, o terminal e os testes
reutilizam o mesmo carregador.
"""

import json
import sys
from collections import Counter
from datetime import date
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

TOPICS: dict[str, str] = {
    "documents": "Documentos",
    "work": "Trabalho",
    "social": "Assistência social",
}
CHANNELS = ("digital", "in-person", "mixed")
TEXT_FIELDS = ("id", "title", "summary", "agency", "audience", "limitations")
LIST_FIELDS = ("keywords", "steps", "preparation", "relatedIds")
REQUIRED_FIELDS = (
    "id",
    "topic",
    "title",
    "summary",
    "keywords",
    "agency",
    "channel",
    "source",
    "audience",
    "steps",
    "preparation",
    "limitations",
    "relatedIds",
)
SOURCE_FIELDS = ("title", "url", "reviewedAt")
MIN_RELATED = 3
MIN_RECORDS = 15
MIN_PER_TOPIC = 5


class KnowledgeBaseError(ValueError):
    """O arquivo da base está ausente, vazio ou inconsistente. ``problems`` lista os problemas encontrados."""

    def __init__(self, message: str, problems: list[str] | None = None):
        self.problems = problems or [message]
        super().__init__(
            message
            if problems is None
            else message + "\n" + "\n".join(f"  - {p}" for p in problems)
        )


def _is_text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _check_text_list(label: str, value: Any, problems: list[str], minimum: int) -> None:
    if not isinstance(value, list):
        problems.append(f"{label}: deve ser uma lista de textos.")
        return
    if len(value) < minimum:
        problems.append(f"{label}: precisa ter pelo menos {minimum} item(ns).")
    for position, item in enumerate(value, start=1):
        if not _is_text(item):
            problems.append(f"{label}: o item {position} está vazio ou não é texto.")


def _check_source(label: str, source: Any, problems: list[str]) -> None:
    if not isinstance(source, dict):
        problems.append(f"{label}: deve ser um objeto com title, url e reviewedAt.")
        return
    for name in SOURCE_FIELDS:
        if name not in source:
            problems.append(f"{label}.{name}: campo obrigatório ausente.")
    extra = sorted(set(source) - set(SOURCE_FIELDS))
    if extra:
        problems.append(f"{label}: campos desconhecidos {extra}.")
    if "title" in source and not _is_text(source["title"]):
        problems.append(f"{label}.title: título da fonte vazio.")
    if "url" in source:
        url = source["url"]
        parsed = urlparse(url) if isinstance(url, str) else None
        if (
            parsed is None
            or parsed.scheme != "https"
            or not parsed.hostname
            or parsed.username
            or parsed.password
            or any(ch.isspace() for ch in url)
        ):
            problems.append(f"{label}.url: use um link https válido, sem credenciais.")
    reviewed = source.get("reviewedAt")
    if reviewed is not None:
        try:
            parsed_date = date.fromisoformat(reviewed)
            if parsed_date.isoformat() != reviewed:
                raise ValueError
        except (TypeError, ValueError):
            problems.append(f"{label}.reviewedAt: use a data AAAA-MM-DD ou null.")
        else:
            if parsed_date > date.today():
                problems.append(f"{label}.reviewedAt: a data de verificação está no futuro.")


def validate_records(
    records: Any, *, require_verified: bool = False
) -> list[str]:
    """Retorna os problemas encontrados em ``records``."""
    if not isinstance(records, list):
        return ["A base deve ser uma lista (array JSON) de orientações."]
    if not records:
        return ["A base está vazia: nenhuma orientação cadastrada."]
    problems: list[str] = []
    ids: Counter[str] = Counter()
    for record in records:
        if isinstance(record, dict) and _is_text(record.get("id")):
            ids[record["id"]] += 1
    known_ids = set(ids)
    for position, record in enumerate(records, start=1):
        if not isinstance(record, dict):
            problems.append(f"Registro {position}: deve ser um objeto JSON.")
            continue
        label = f"Registro {position} ({record.get('id') or 'sem id'})"
        sub: list[str] = []
        for name in REQUIRED_FIELDS:
            if name not in record:
                sub.append(f"campo obrigatório ausente: {name}.")
        extra = sorted(set(record) - set(REQUIRED_FIELDS))
        if extra:
            sub.append(f"campos desconhecidos (erro de digitação?): {extra}.")
        for name in TEXT_FIELDS:
            if name in record and not _is_text(record[name]):
                sub.append(f"{name}: está vazio ou não é texto.")
        if "id" in record and _is_text(record["id"]) and ids[record["id"]] > 1:
            sub.append("id duplicado na base.")
        if "topic" in record and record["topic"] not in TOPICS:
            sub.append(f"topic: use um destes valores {list(TOPICS)}.")
        if "channel" in record and record["channel"] not in CHANNELS:
            sub.append(f"channel: use um destes valores {list(CHANNELS)}.")
        if "keywords" in record:
            _check_text_list("keywords", record["keywords"], sub, 1)
        if "steps" in record:
            _check_text_list("steps", record["steps"], sub, 1)
        if "preparation" in record:
            _check_text_list("preparation", record["preparation"], sub, 0)
        if "relatedIds" in record:
            related = record["relatedIds"]
            _check_text_list("relatedIds", related, sub, MIN_RELATED)
            if isinstance(related, list):
                if len(set(map(str, related))) != len(related):
                    sub.append("relatedIds: há ids repetidos.")
                for target in related:
                    if target == record.get("id"):
                        sub.append("relatedIds: uma orientação não pode apontar para si mesma.")
                    elif _is_text(target) and target not in known_ids:
                        sub.append(f"relatedIds: '{target}' não existe na base.")
        if "source" in record:
            _check_source("source", record["source"], sub)
            if (
                require_verified
                and isinstance(record["source"], dict)
                and record["source"].get("reviewedAt") is None
            ):
                sub.append("source.reviewedAt: orientação ainda não verificada.")
        problems.extend(f"{label}: {item}" for item in sub)
    return problems


def load_services(
    path: Path, *, require_verified: bool = False
) -> list[dict[str, Any]]:
    """Carrega a base JSON, valida e retorna os registros como uma lista de dicionários.

    Gera ``FileNotFoundError`` se o arquivo não existir e ``KnowledgeBaseError``
    (um ``ValueError``) se o conteúdo estiver vazio, malformado ou inconsistente. Nunca
    trata um arquivo inválido como se tivesse sido carregado com sucesso.
    """
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(f"Arquivo da base de conhecimento não encontrado: {path}")
    text = path.read_text(encoding="utf-8")
    if not text.strip():
        raise KnowledgeBaseError(f"O arquivo da base está vazio: {path}")
    try:
        records = json.loads(text)
    except json.JSONDecodeError as error:
        raise KnowledgeBaseError(
            f"JSON inválido em {path} (linha {error.lineno}, coluna {error.colno}): {error.msg}"
        ) from error
    problems = validate_records(records, require_verified=require_verified)
    if problems:
        raise KnowledgeBaseError(f"Base de conhecimento inválida: {path}", problems)
    return records


def index_by_id(records: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    """Dictionary lookup by identifier."""
    return {record["id"]: record for record in records}


def group_by_topic(records: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    """Records grouped by topic, keeping the file order inside each group."""
    groups: dict[str, list[dict[str, Any]]] = {topic: [] for topic in TOPICS}
    for record in records:
        groups.setdefault(record["topic"], []).append(record)
    return groups


def list_topics(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Available themes with their label and record count (for menus)."""
    groups = group_by_topic(records)
    return [
        {"id": topic, "label": TOPICS.get(topic, topic), "count": len(items)}
        for topic, items in groups.items()
        if items
    ]


def unverified_ids(records: list[dict[str, Any]]) -> list[str]:
    """Identifiers whose source still has no verification date."""
    return [r["id"] for r in records if r["source"].get("reviewedAt") is None]


def check_coverage(records: list[dict[str, Any]]) -> list[str]:
    """Assignment minimums: 15 records, 3 themes, 5 per theme."""
    problems: list[str] = []
    if len(records) < MIN_RECORDS:
        problems.append(f"Há {len(records)} orientações; o mínimo é {MIN_RECORDS}.")
    counts = Counter(record["topic"] for record in records)
    for topic in TOPICS:
        if counts[topic] < MIN_PER_TOPIC:
            problems.append(
                f"Tema '{topic}' tem {counts[topic]} orientações; o planejado é {MIN_PER_TOPIC}."
            )
    return problems


def main(argv: list[str] | None = None) -> int:
    """Validate a base file: ``python -m backend.knowledge [path] [--require-verified]``."""
    from backend.config import DATA_PATH

    args = list(sys.argv[1:] if argv is None else argv)
    strict = "--require-verified" in args
    paths = [a for a in args if not a.startswith("--")]
    path = Path(paths[0]) if paths else DATA_PATH
    try:
        records = load_services(path, require_verified=strict)
    except (OSError, ValueError) as error:
        print(f"ERRO: {error}", file=sys.stderr)
        return 2
    print(f"OK: {len(records)} orientações válidas em {path}")
    for topic in list_topics(records):
        print(f"  - {topic['label']} ({topic['id']}): {topic['count']}")
    pending = unverified_ids(records)
    if pending:
        print(f"ATENÇÃO: {len(pending)} sem data de verificação: {', '.join(pending)}")
    for problem in check_coverage(records):
        print(f"ATENÇÃO: {problem}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
