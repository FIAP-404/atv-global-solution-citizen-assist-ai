# Python team work packages

Five-person arrangement: the coordinator owns React and integration; four colleagues own the Python packages below. Names and RMs must be confirmed by the coordinator before the final README is completed.

Approved decisions (2026-11-19): FastAPI, a JSON base, deterministic source-bound responses and **no external AI**. The group chooses the owner of each module; no individual has been assigned. Start with [the Python quickstart](python-quickstart.md).

Work on separate branches. Keep the contract in `api-contract.md` stable; propose changes before altering public JSON fields. All four module files now exist with fixed signatures and explicitly pending bodies. Replace only your module's pending body, add your tests and document the decisions. The API and terminal wiring are already coordinator-owned.

Read [content-and-handoff.md](content-and-handoff.md) before implementing. It maps existing fields to substantive citizen guidance, names each package's deliverables and distinguishes matching a service from actually answering the question. No new government-service execution screens are needed.

## Package 1: Knowledge base and content

Owner: to be chosen by the group.

- Implement `backend/knowledge.py` to load JSON/CSV into lists and dictionaries, validate required fields and report missing, empty or inconsistent files.
- Review all 15 draft records in `data/services.demo.json` against identifiable official sources. Correct URLs, scope, audience, channel and content; record actual review dates only after checking them.
- Keep at least five orientations in each of the three themes. Review at least three relationships per service with the search owner.
- Produce `data/services.json` for the final verified base and explain the schema and update procedure.
- Replace redirect-only draft content with concrete, source-checked guidance in the existing summary, audience, preparation and steps fields. Do not merely rename the demo file. Research may be shared by the group; this owner consolidates and validates it. Deliver `tests/test_knowledge.py` and `docs/knowledge-base.md`.

Fixed interface: `load_services(path: Path) -> list[dict[str, Any]]`. Fail clearly on invalid content; never convert an empty or broken file into apparent success.

Acceptance: missing file, empty file, malformed JSON, missing source, duplicate IDs, invalid dates and broken relationships are handled and tested. Supply accurate metadata, not invented fees or eligibility rules.

## Package 2: Search and navigation

Owner: to be chosen by the group. Depends on package 1's record format; can begin with the demo file.

- Implement `backend/search.py` with accent/case normalization, keyword aliases and a justified ranking strategy.
- Represent themes/subthemes or relations as a hierarchy/graph and expose related orientations.
- Implement query and theme filtering in the core function; the coordinator's `GET /services` already delegates to it.
- Explain and demonstrate tie handling, empty search and unmatched queries.
- Deliver `tests/test_search.py` and `docs/search-strategy.md`, including how the hierarchy/graph and related IDs support navigation.

Fixed interface: `search_services(records: list[dict[str, Any]], query: str, topic: str = "all") -> list[dict[str, Any]]`. Keep HTTP separate from the algorithm. The response owner reuses this search and must agree on how ranking/ambiguity work.

Acceptance: variations of CPF, CTPS and CadÚnico work; topic filtering works; out-of-scope queries do not return arbitrary guidance. Use the 12 starter scenarios as a baseline, adding reformulations and adversarial inputs.

## Package 3: Responses without external AI

Owner: to be chosen by the group. Depends on package 2's search result format. Fixed interface: `answer_question(records: list[dict[str, Any]], question: str, mode: str = "direct") -> dict[str, Any]`.

- Implement `backend/assistant.py` with the four response statuses and two documented response instructions: direct and step-by-step.
- Ask for clarification on ambiguity. Always include sources and limitations. Do not pretend to perform official operations or decide eligibility.
- Return `status`, `message`, `services` and `mode` according to `backend/contracts.py`. Do not duplicate full guidance in `message`: React already renders the selected record's summary, steps, source and limitations.
- Use `message` to address the person's actual question with supported facts; it must not always be a generic match announcement. Do not treat a matching title as sufficient evidence for information the base does not contain. Deliver `tests/test_assistant.py` and `docs/response-instructions.md`.
- HTTP and terminal integration are already implemented by the coordinator. Leave `backend/api.py` and `src/main.py` unchanged unless coordinated.
- Document both instruction templates, including role, selection criteria, response structure, citations and limitations. The decision is closed: do not add an external model, API key or paid service. Two visual formats alone are not evaluation evidence.

Acceptance: empty/ambiguous/unsupported/matched inputs, 500-character limit, both modes, errors and an end-to-end browser request work. API and terminal consult the same base and logic.

## Package 4: Evaluation and evidence

Owner: to be chosen by the group. Can define expected outcomes before Python implementation, then execute against packages 1–3. Fixed interface: `evaluate_questions(records: list[dict[str, Any]], cases: list[dict[str, Any]], output_path: Path) -> dict[str, Any]`.

- Extend `data/demo-test-cases.json` into a final evaluation set with at least 12 questions: direct questions, reformulations and out-of-scope questions.
- Include at least three limitation cases: empty input, ambiguity and no reliable answer.
- Implement `backend/evaluation.py` to record expected/actual response, correct/incorrect classification and measured query duration. Calculate accuracy and a simple mean time.
- Compare both response instruction models and justify clarity/consistency conclusions using recorded evidence.
- Run a usability session with at least one test user or task script; record difficulties, outcomes, at least two improvements and evaluation limits.
- Save reproducible evidence and a final interpretation. Do not substitute browser demo test results for measured Python results.
- Call `backend.assistant.answer_question` for both modes instead of copying response logic. Save the report to `output_path` (creating its parent directory if needed) and return the same report dictionary, using `summary` and `cases` as its main keys. Document the result fields and correctness criteria.
- Add source-checked `expectedFacts` to final cases as appropriate; evaluate whether the actual answer resolves the question, not only whether it selected the expected service ID. Distinguish retrieval correctness from response correctness and document any human assessment. Deliver `data/test-cases.json`, `tests/test_evaluation.py`, `docs/evaluation.md` and `docs/usability.md`, plus the measured report.

Acceptance: reproducible command, saved actual results, metric calculation and interpretation, response-model comparison and usability evidence.

## Coordinator: Frontend and final assembly

- Own the prepared FastAPI transport, request/response schemas, configuration and terminal wiring. See `backend/api.py`, `backend/contracts.py`, `backend/config.py` and `src/main.py`.

- Integrate the Python adapter and verify loading/error/empty/success states.
- Confirm the team's names/RMs and review content/official status messaging.
- Complete README, AI usage documentation, final evidence, video and the two-link TXT required by the assignment.
- Check the coordination template and reconcile submission layout. Its public README currently describes a portfolio hierarchy with separate Global Solution folders; it does not recover the two missing tables in the PDF capture.
- Demonstrate the complete integrated consultation flow before claiming the assignment is finished.
