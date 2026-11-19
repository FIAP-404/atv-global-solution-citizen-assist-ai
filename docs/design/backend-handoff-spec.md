# Python handoff decisions

Approved in conversation on 2026-11-19: FastAPI transport, a JSON knowledge base, no external AI or paid API, direct and step-by-step response instructions, and four module owners selected by the group itself.

The coordinator owns React, API/terminal wiring and final assembly. The handoff implements transport and fixes function signatures; it deliberately leaves knowledge loading/validation, search/relations, response logic and evaluation to the four colleagues. Unimplemented functions raise an explicit pending-module error. The server never substitutes demo answers for unfinished Python work.

Use Python 3.11+ and standard `unittest`. JSON bodies keep the existing frontend camelCase field names; Python functions use English snake_case. FastAPI owns request/response validation and CORS. Core algorithms consume and return ordinary lists and dictionaries so the API and terminal can share them. Tests use the HTTPX2 support expected by the installed Starlette version.

## Fixed interfaces

- `knowledge.load_services(path: Path) -> list[dict[str, Any]]`
- `search.search_services(records: list[dict[str, Any]], query: str, topic: str = "all") -> list[dict[str, Any]]`
- `assistant.answer_question(records: list[dict[str, Any]], question: str, mode: str = "direct") -> dict[str, Any]`
- `evaluation.evaluate_questions(records: list[dict[str, Any]], cases: list[dict[str, Any]], output_path: Path) -> dict[str, Any]`

The final base is `data/services.json`; it does not exist until the content owner verifies it. The existing demo file is study/test material. Response rules remain deterministic and source-bound. Two documented instruction models must be evaluated; having two UI formats alone is not final evidence.

## Acceptance

API tests use isolated test doubles to prove dispatch, serialization, body/query validation, CORS and explicit pending behavior. CLI tests prove dispatch and pending/error reporting. They do not prove any colleague's algorithm, verified content, final accuracy or usability. Existing frontend tests/build must still pass.
