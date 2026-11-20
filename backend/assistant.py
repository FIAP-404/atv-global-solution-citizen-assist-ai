"""Respostas do assistente, sem IA externa.

O módulo recebe a pergunta, usa a busca de ``backend.search`` para escolher as
orientações e monta a resposta com regras fixas (consulte
``docs/modelos-de-resposta.md``). Nenhum texto é gerado por modelo de linguagem:
toda frase sobre um serviço vem dos campos do próprio registro da base.

Status devolvidos (contrato em ``backend/contracts.py``):

* ``empty``: a pergunta está vazia ou só tem espaços e pontuação.
* ``unsupported``: nenhuma orientação confiável; informa o limite e sugere temas.
* ``ambiguous``: duas ou três orientações empatadas (``find_ties``); pede escolha.
* ``matched``: uma orientação clara; responde ao que foi perguntado, com fonte e aviso.
"""

import re
from datetime import date
from typing import Any

from backend import search
from backend.knowledge import TOPICS

MODES = ("direct", "steps")
MAX_QUESTION_LENGTH = 500
MAX_OPTIONS = 3
SUGGESTIONS_PER_TOPIC = 2

CHANNEL_LABELS = {
    "digital": "pelos canais digitais",
    "in-person": "presencialmente",
    "mixed": "por canais digitais e presenciais",
}

CONFIRMATION_WARNING = (
    "Aviso: este assistente é um projeto acadêmico, não é canal oficial; "
    "confirme os requisitos atualizados na fonte antes de ir ao atendimento."
)

# Os dois modelos de instrução. O texto de cada campo é o que está documentado em
# docs/modelos-de-resposta.md; o código abaixo segue essas regras.
INSTRUCTIONS: dict[str, dict[str, Any]] = {
    "direct": {
        "role": (
            "Orientador que responde em poucas frases à dúvida principal, usando "
            "apenas os campos da orientação selecionada."
        ),
        "format": "Um parágrafo: resposta, fonte citada e aviso de confirmação.",
        "rules": [
            "Citar sempre a fonte (título, link e data de verificação).",
            "Não alegar atendimento oficial nem decidir se a pessoa tem direito.",
            "Não inventar valores, prazos ou documentos que a base não traz.",
            "Avisar quando a informação pedida não estiver na base.",
        ],
    },
    "steps": {
        "role": (
            "Orientador que organiza a mesma informação em etapas numeradas para a "
            "pessoa se preparar e saber por onde seguir."
        ),
        "format": (
            "Etapas numeradas: o que separar, onde procurar, por onde começar e o "
            "que confirmar; depois a fonte citada e o aviso de confirmação."
        ),
        "rules": [
            "Citar sempre a fonte (título, link e data de verificação).",
            "Não alegar atendimento oficial nem decidir se a pessoa tem direito.",
            "Não inventar valores, prazos ou documentos que a base não traz.",
            "Avisar quando a informação pedida não estiver na base.",
        ],
    },
}

# Intenção da pergunta: expressões normalizadas (sem acento, minúsculas).
# A ordem define a prioridade quando mais de uma aparece.
INTENTS: dict[str, tuple[str, ...]] = {
    "cost": (
        "quanto custa", "custa", "custo", "valor", "preco", "taxa", "pagar",
        "gratis", "gratuito", "quanto recebo", "quanto vou receber",
    ),
    "deadline": (
        "prazo", "quanto tempo", "demora", "quando sai", "quando recebo",
        "dias uteis",
    ),
    "eligibility": (
        "tenho direito", "tem direito", "direito", "quem pode", "posso receber",
        "requisito", "requisitos", "elegivel",
    ),
    "documents": (
        "quais documentos", "que documentos", "documentos necessarios",
        "documentacao", "o que levar", "preciso levar", "levar",
    ),
    "where": (
        "onde fica", "onde", "local", "endereco", "site", "aplicativo", "app", "online",
        "presencial", "agencia", "posto",
    ),
}


def answer_question(
    records: list[dict[str, Any]], question: str, mode: str = "direct"
) -> dict[str, Any]:
    """Responde à pergunta usando só a base, no modelo ``direct`` ou ``steps``.

    Gera ``ValueError`` para modo desconhecido, pergunta que não seja texto ou
    pergunta com mais de 500 caracteres (mesmo limite da API e do terminal).
    """
    if mode not in MODES:
        raise ValueError(f"Modo de resposta inválido: {mode!r}. Use {list(MODES)}.")
    if not isinstance(question, str):
        raise ValueError("A pergunta deve ser um texto.")
    if len(question) > MAX_QUESTION_LENGTH:
        raise ValueError(
            f"A pergunta tem {len(question)} caracteres; o limite é {MAX_QUESTION_LENGTH}."
        )

    if not search.normalize(question):
        return _answer("empty", _empty_message(records, mode), [], mode)

    intent = detect_intent(question)
    ranked = _rank(records, question)
    if not ranked:
        return _answer("unsupported", _unsupported_message(records, mode), [], mode)

    ties = search.find_ties(ranked)
    if len(ties) > 1:
        options = [item.record for item in ties[:MAX_OPTIONS]]
        return _answer("ambiguous", _ambiguous_message(options, mode), options, mode)

    record = ranked[0].record
    return _answer("matched", _matched_message(record, intent, mode), [record], mode)


# --- seleção --------------------------------------------------------------


def _phrase_in(text: str, phrase: str) -> bool:
    return f" {phrase} " in f" {text} "


def detect_intent(question: str) -> str:
    """Tipo de informação pedida: cost, deadline, eligibility, documents, where ou how."""
    text = search.normalize(question)
    for intent, phrases in INTENTS.items():
        if any(_phrase_in(text, phrase) for phrase in phrases):
            return intent
    return "how"


def _strip_intent_words(question: str) -> str:
    text = search.normalize(question)
    for phrases in INTENTS.values():
        for phrase in sorted(phrases, key=len, reverse=True):
            text = f" {text} ".replace(f" {phrase} ", " ").strip()
    return text


def _rank(records: list[dict[str, Any]], question: str) -> list[search.ScoredService]:
    """Busca a pergunta original; se nada passar, tenta sem as palavras de intenção.

    Palavras como "quanto custa" ou "tem direito" não aparecem nos registros e
    baixam a cobertura mínima da busca. A segunda tentativa só acontece se ainda
    restar alguma palavra útil, então "quanto custa?" sozinho continua sem resposta.
    """
    ranked = search.score_services(records, question)
    if ranked:
        return ranked
    reduced = _strip_intent_words(question)
    if reduced and search.tokens(reduced):
        return search.score_services(records, reduced)
    return []


# --- montagem das mensagens ------------------------------------------------


def _answer(
    status: str, message: str, services: list[dict[str, Any]], mode: str
) -> dict[str, Any]:
    return {"status": status, "message": message, "services": services, "mode": mode}


def _numbered(items: list[str]) -> str:
    return " ".join(f"{n}) {item}" for n, item in enumerate(items, start=1))


def _sentence(text: str) -> str:
    text = text.strip()
    return text if text.endswith((".", "!", "?")) else text + "."


def _lower_first(text: str) -> str:
    return text[:1].lower() + text[1:] if text else text


def _join_options(titles: list[str]) -> str:
    if len(titles) == 1:
        return titles[0]
    return ", ".join(titles[:-1]) + " ou " + titles[-1]


def cite_source(record: dict[str, Any]) -> str:
    """Citação da fonte: título, link e data de verificação (ou aviso de pendência)."""
    source = record["source"]
    reviewed = source.get("reviewedAt")
    when = (
        f"verificada em {date.fromisoformat(reviewed).strftime('%d/%m/%Y')}"
        if reviewed
        else "data de verificação pendente"
    )
    return f"Fonte: {source['title']} ({source['url']}), {when}."


def _where(record: dict[str, Any]) -> str:
    channel = CHANNEL_LABELS.get(record["channel"], "pelo canal indicado na fonte")
    return f"O atendimento é feito {channel}. Órgão responsável: {record['agency']}."


def _preparation(record: dict[str, Any]) -> str:
    items = record["preparation"]
    if not items:
        return "A base não lista o que separar para esta orientação; confira na fonte."
    return "Separe antes: " + "; ".join(item.rstrip(".") for item in items) + "."


def _missing(record: dict[str, Any], what: str) -> str:
    return (
        f"A base não informa {what} para {record['title']}, então não vou estimar; "
        "esse dado precisa ser conferido na fonte oficial."
    )


# Marcas, no texto normalizado (sem "$", acentos ou pontuação), de que uma
# frase da base fala de custo ou de prazo.
COST_PATTERN = re.compile(r"\br \d|\bgratuit")
DEADLINE_PATTERN = re.compile(r"\b\d+ (?:a \d+ )?(?:dia|dias|hora|horas|mes|meses)\b")
INTENT_EVIDENCE = {
    "cost": (COST_PATTERN, "valores ou taxas", "o valor"),
    "deadline": (DEADLINE_PATTERN, "prazos", "o prazo"),
}


def _evidence(record: dict[str, Any], pattern: re.Pattern[str], limit: int = 2) -> list[str]:
    """Frases do próprio registro que tratam do assunto pedido (custo ou prazo)."""
    found: list[str] = []
    fields = (record["summary"], *record["steps"], *record["preparation"], record["limitations"])
    for text in fields:
        for piece in re.split(r"(?<=[.;])\s+", text):
            sentence = _sentence(piece.rstrip(";"))
            sentence = sentence[:1].upper() + sentence[1:]
            if pattern.search(search.normalize(sentence)) and sentence not in found:
                found.append(sentence)
    return found[:limit]


def _intent_answer(record: dict[str, Any], intent: str) -> str:
    """Cita a base quando ela traz custo/prazo; senão, avisa que não traz."""
    pattern, missing, noun = INTENT_EVIDENCE[intent]
    evidence = _evidence(record, pattern)
    if not evidence:
        return _missing(record, missing)
    return f"A base informa: {' '.join(evidence)} Confirme {noun} atual na fonte oficial."


def _facts(record: dict[str, Any], intent: str) -> list[str]:
    """Frases que respondem à intenção, todas tiradas de campos do registro."""
    first_step = _sentence(record["steps"][0])
    if intent in {"cost", "deadline"}:
        return [_intent_answer(record, intent), _where(record)]
    if intent == "eligibility":
        return [
            f"Pela base, esta orientação é para: {_lower_first(_sentence(record['audience']))}",
            "O assistente não decide se você tem direito; isso depende da análise do órgão.",
        ]
    if intent == "documents":
        return [_preparation(record), f"Para começar: {first_step}"]
    if intent == "where":
        return [_where(record), f"Para começar: {first_step}"]
    return [f"Para começar: {first_step}", _where(record)]


def _matched_message(record: dict[str, Any], intent: str, mode: str) -> str:
    title = record["title"]
    if mode == "direct":
        body = " ".join(_facts(record, intent))
        return f"{title}: {body} {cite_source(record)} {CONFIRMATION_WARNING}"

    stages = []
    if intent in {"cost", "deadline"}:
        stages.append(_facts(record, intent)[0])
    if intent == "eligibility":
        stages.extend(_facts(record, intent))
    stages.append(_preparation(record))
    stages.append(_where(record))
    count = len(record["steps"])
    stages.append(
        f"Siga {'o passo' if count == 1 else f'os {count} passos'} da orientação, "
        f"começando por: {_sentence(record['steps'][0])}"
    )
    stages.append("Confira na fonte se os requisitos continuam os mesmos.")
    return (
        f"{title}, em etapas: {_numbered(stages)} "
        f"{cite_source(record)} {CONFIRMATION_WARNING}"
    )


def _ambiguous_message(options: list[dict[str, Any]], mode: str) -> str:
    titles = [record["title"] for record in options]
    if mode == "direct":
        return (
            f"Sua pergunta pode se referir a mais de um assunto: {_join_options(titles)}. "
            "Qual deles você procura? Escolha uma opção para ver a orientação com a fonte."
        )
    return (
        "Sua pergunta combina com mais de um assunto. Para continuar: "
        + _numbered(
            [
                f"escolha uma das opções: {_join_options(titles)};",
                "abra a orientação escolhida ou refaça a pergunta com o nome do assunto;",
                "confira a fonte indicada na orientação.",
            ]
        )
    )


def topic_suggestions(records: list[dict[str, Any]]) -> list[str]:
    """Temas disponíveis com exemplos de orientações, para sugerir outra consulta."""
    groups: dict[str, list[str]] = {}
    for record in records:
        groups.setdefault(record["topic"], []).append(record["title"])
    return [
        f"{TOPICS.get(topic, topic)} ({', '.join(titles[:SUGGESTIONS_PER_TOPIC])})"
        for topic, titles in groups.items()
    ]


def _unsupported_message(records: list[dict[str, Any]], mode: str) -> str:
    base = (
        "Não encontrei informação suficiente na base para orientar sobre essa dúvida "
        "e não vou inventar instruções."
    )
    suggestions = topic_suggestions(records)
    if mode == "direct":
        hint = f" Posso ajudar com: {'; '.join(suggestions)}." if suggestions else ""
        return base + hint + " Tente reformular citando o serviço que procura."
    stages = ["reformule citando o nome do serviço (por exemplo, CPF ou FGTS);"]
    if suggestions:
        stages.append(f"ou escolha um tema: {'; '.join(suggestions)};")
    stages.append("para outros assuntos, procure o canal oficial do órgão responsável.")
    return f"{base} Para continuar: {_numbered(stages)}"


def _empty_message(records: list[dict[str, Any]], mode: str) -> str:
    themes = ", ".join(TOPICS.get(t, t) for t in dict.fromkeys(r["topic"] for r in records))
    themes_text = f" ({themes})" if themes else ""
    if mode == "direct":
        return f"Digite sua pergunta ou escolha um dos temas{themes_text}."
    return "Para começar: " + _numbered(
        [
            "digite sua dúvida em poucas palavras (por exemplo, como tirar o CPF);",
            f"ou escolha um dos temas{themes_text}.",
        ]
    )
