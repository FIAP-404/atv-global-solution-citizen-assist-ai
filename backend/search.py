"""Busca, classificação e navegação pela base de conhecimento.

Estratégia (detalhes em ``docs/search-strategy.md``):

* A consulta e cada campo do registro são generalizados (letras minúsculas, sem acentos,
  pontuação removida, palavras comuns descartadas e plurais reduzidos).
* Cada termo da consulta é ranqueado pelos campos: title 4, keyword 3,
  agency 1.5, summary 1. Uma palavra que aparece apenas no summary não gera resultado. 
* Os candidatos precisam corresponder a pelo menos 60% das palavras digitadas na consulta; isso
  evita que perguntas fora do escopo correspondam por causa de uma palavra genérica.
* A ordem segue uma sequência de prioridade: pontuação, quantidade de termos correspondentes e ordem no arquivo.

"""

import re
import unicodedata
from collections import deque
from typing import Any, NamedTuple

from backend.knowledge import TOPICS

TITLE_WEIGHT = 4.0
KEYWORD_WEIGHT = 3.0
AGENCY_WEIGHT = 1.5
SUMMARY_WEIGHT = 1.0
PHRASE_BONUS = 3.0
TITLE_PHRASE_BONUS = 6.0
EXACT_TITLE_BONUS = 20.0
MIN_COVERAGE = 0.6

STOP_WORDS = frozenset(
    """a o os as e de do da dos das em no na nos nas um uma uns umas ao aos
    me te meu minha meus minhas seu sua vou vai para por pra que qual quais quem quando como
    eu se com sobre onde mais muito ser ter tenho tem sou estou esta sao foi
    fui faco fazer faz posso pode preciso precisa quero queria gostaria saber
    funciona acessar achar consultar solicitar servico servicos antes depois
    ajuda informacao informacoes""".split()
)

# Curated synonyms: a normalized phrase in the question adds these terms.
ALIASES: dict[str, tuple[str, ...]] = {
    "cad unico": ("cadunico",),
    "cadastro unico": ("cadunico",),
    "cad": ("cadunico",),
    "carteira de trabalho": ("ctps",),
    "trabalho": ("ctps",),
    "carteira profissional": ("ctps",),
    "carteira de identidade": ("rg", "cin"),
    "cin": ("rg", "cin"),
    "identidade": ("rg", "cin"),
    "rg": ("cin", "identidade"),
    "titulo de eleitor": ("titulo", "eleitoral"),
    "titulo": ("titulo", "eleitoral"),
    "fundo de garantia": ("fgts",),
    "fgts": ("fgts",),
    "pis": ("abono",),
    "pasep": ("abono",),
    "demitido": ("desemprego", "demissao"),
    "demitida": ("desemprego", "demissao"),
    "perdi o emprego": ("desemprego",),
    "mandado embora": ("desemprego", "demissao"),
    "procurar emprego": ("vaga", "sine"),
    "buscar emprego": ("vaga", "sine"),
    "viajar para o exterior": ("passaporte",),
    "viajar": ("passaporte",),
    "viagem": ("passaporte",),
    "passaporte": ("passaporte",),
    "bolsa familia": ("bolsa",),
    "auxilio": ("bolsa", "desemprego", ),
}


class ScoredService(NamedTuple):
    """A ranked record with the evidence the response module needs."""

    record: dict[str, Any]
    score: float
    matched_terms: int
    coverage: float


def normalize(value: str) -> str:
    """Lower case, no accents, punctuation turned into single spaces."""
    text = unicodedata.normalize("NFD", value)
    text = "".join(ch for ch in text if not unicodedata.combining(ch)).lower()
    return re.sub(r"[^a-z0-9]+", " ", text).strip()


def _stem(word: str) -> str:
    if len(word) > 4 and word.endswith("oes"):
        return word[:-3] + "ao"
    if len(word) > 4 and word.endswith("ais"):
        return word[:-3] + "al"
    if len(word) > 3 and word.endswith("s"):
        return word[:-1]
    return word


def tokens(value: str) -> list[str]:
    """Meaningful stemmed words of ``value`` (stop words and 1-letter words removed)."""
    return [
        _stem(word)
        for word in normalize(value).split()
        if len(word) > 1 and word not in STOP_WORDS
    ]


def _contains_phrase(text: str, phrase: str) -> bool:
    return bool(phrase) and f" {phrase} " in f" {text} "


def query_terms(query: str) -> list[str]:
    """Unique search terms: question words plus alias expansions."""
    text = normalize(query)
    terms = tokens(query)
    for phrase, extra in ALIASES.items():
        if _contains_phrase(text, phrase):
            terms.extend(_stem(word) for word in extra)
    return list(dict.fromkeys(terms))


def _check_inputs(query: Any, topic: Any) -> None:
    if not isinstance(query, str):
        raise ValueError("A consulta deve ser um texto.")
    if topic != "all" and topic not in TOPICS:
        raise ValueError(f"Tema inválido: {topic!r}. Use 'all' ou {list(TOPICS)}.")


def score_services(
    records: list[dict[str, Any]], query: str, topic: str = "all"
) -> list[ScoredService]:
    """Rank records for ``query`` and return the evidence behind each position.

    An empty query returns every record of the topic in file order with score
    0. A non-empty query with no usable match returns an empty list.
    """
    _check_inputs(query, topic)
    pool = [r for r in records if topic == "all" or r["topic"] == topic]
    text = normalize(query)
    if not text:
        return [ScoredService(r, 0.0, 0, 1.0) for r in pool]
    terms = query_terms(query)
    if not terms:
        return []
    # Alias expansions can only help: coverage is measured against the words
    # the person actually wrote.
    wanted = max(1, len(tokens(query)))
    scored: list[tuple[int, ScoredService]] = []
    for order, record in enumerate(pool):
        title_words = set(tokens(record["title"]))
        keyword_words = {w for k in record["keywords"] for w in tokens(k)}
        agency_words = set(tokens(record["agency"]))
        summary_words = set(tokens(record["summary"]))
        score, matched, strong = 0.0, 0, False
        for term in terms:
            if term in title_words:
                weight, is_strong = TITLE_WEIGHT, True
            elif term in keyword_words:
                weight, is_strong = KEYWORD_WEIGHT, True
            elif term in agency_words:
                weight, is_strong = AGENCY_WEIGHT, True
            elif term in summary_words:
                weight, is_strong = SUMMARY_WEIGHT, False
            else:
                continue
            score += weight
            matched += 1
            strong = strong or is_strong
        if not strong:
            continue
        for keyword in record["keywords"]:
            phrase = normalize(keyword)
            if " " in phrase and _contains_phrase(text, phrase):
                score += PHRASE_BONUS
        title = normalize(record["title"])
        if title == text:
            score += EXACT_TITLE_BONUS
        elif _contains_phrase(text, title):
            score += TITLE_PHRASE_BONUS
        coverage = min(1.0, matched / wanted)
        if coverage >= MIN_COVERAGE:
            scored.append((order, ScoredService(record, score, matched, coverage)))
    scored.sort(key=lambda item: (-item[1].score, -item[1].matched_terms, item[0]))
    return [item for _, item in scored]


def search_services(
    records: list[dict[str, Any]], query: str, topic: str = "all"
) -> list[dict[str, Any]]:
    """Return the records matching ``query``/``topic``, best match first."""
    return [item.record for item in score_services(records, query, topic)]


def find_ties(ranked: list[ScoredService]) -> list[ScoredService]:
    """Results whose score is within 20% of the best one (possible ambiguity)."""
    if not ranked:
        return []
    best = ranked[0].score
    return [item for item in ranked if item.score >= best * 0.8]


# --- hierarchy and graph -------------------------------------------------


def build_topic_tree(records: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    """Level 1 = theme, level 2 = services of that theme (file order)."""
    tree: dict[str, dict[str, Any]] = {
        topic: {"label": label, "services": []} for topic, label in TOPICS.items()
    }
    for record in records:
        tree[record["topic"]]["services"].append(record["id"])
    return tree


def build_graph(records: list[dict[str, Any]]) -> dict[str, list[str]]:
    """Undirected adjacency lists built from ``relatedIds``.

    Declared links come first (in the order written), then links that only the
    other side declared, so neighbours are stable between runs.
    """
    graph: dict[str, list[str]] = {r["id"]: list(r["relatedIds"]) for r in records}
    for record in records:
        for target in record["relatedIds"]:
            if target in graph and record["id"] not in graph[target]:
                graph[target].append(record["id"])
    return graph


def _require_known(graph: dict[str, list[str]], service_id: str) -> None:
    if service_id not in graph:
        raise ValueError(f"Orientação desconhecida: {service_id!r}.")


def related_services(
    records: list[dict[str, Any]],
    service_id: str,
    depth: int = 1,
    limit: int | None = None,
) -> list[dict[str, Any]]:
    """Breadth-first walk: nearest related guidance first, up to ``depth`` links."""
    graph = build_graph(records)
    _require_known(graph, service_id)
    by_id = {r["id"]: r for r in records}
    seen, queue, found = {service_id}, deque([(service_id, 0)]), []
    while queue:
        current, distance = queue.popleft()
        if distance == depth:
            continue
        for neighbour in graph[current]:
            if neighbour not in seen:
                seen.add(neighbour)
                found.append(by_id[neighbour])
                queue.append((neighbour, distance + 1))
    return found[:limit] if limit is not None else found


def navigation_path(
    records: list[dict[str, Any]], start_id: str, goal_id: str
) -> list[str]:
    """Shortest chain of related guidance from ``start_id`` to ``goal_id`` ([] if none)."""
    graph = build_graph(records)
    _require_known(graph, start_id)
    _require_known(graph, goal_id)
    previous: dict[str, str | None] = {start_id: None}
    queue = deque([start_id])
    while queue:
        current = queue.popleft()
        if current == goal_id:
            path = []
            while current is not None:
                path.append(current)
                current = previous[current]
            return path[::-1]
        for neighbour in graph[current]:
            if neighbour not in previous:
                previous[neighbour] = current
                queue.append(neighbour)
    return []
