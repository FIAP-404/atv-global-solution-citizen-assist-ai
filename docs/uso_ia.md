# AI assistance record

## Current phase

Codex assisted with transcribing the supplied assignment capture, researching public design references, proposing the interface, implementing React screens, writing draft service records and preparing the Python integration contract and team handoff.

On 2026-11-19 the user approved FastAPI, JSON data and no external AI, with module ownership to be selected by the group. Codex prepared the coordinator's HTTP/terminal wiring, fixed signatures, pending module bodies and transport tests. The four algorithms remain for the colleagues to implement; no successful real consultation or final evaluation is claimed by the scaffold tests.

The FIAP logo and reference images were supplied by the user. They were preserved unchanged; the UI uses the original assets. GOV.BR layout references come from its official portal and design-system documentation.

## Critical validation

- TypeScript and production bundling are checked using `npm run build`.
- Search and limitation behavior are checked using `npm test`.
- Navigation and representative states are inspected in the browser, including mobile widths.
- All service records remain marked as draft, with null review dates. The full set has not received content verification.
- The browser assistant selects draft knowledge-base records and formats them. It does not call an external language model or official service APIs.

## Work still required

The team must understand and review the generated code, verify source content and URLs, implement the Python modules, compare the response instructions and record actual evaluation and usability results. No final accuracy, timing or user-study outcome is claimed here.

This file is at `docs/uso_ia.md`, the path required by the assignment.

## Packages 3 and 4 (responses and evaluation), 2026-11-19/20

Claude Code (Anthropic) assisted Joedson da Silva Souza in implementing `backend/assistant.py` and `backend/evaluation.py`, writing `tests/test_assistant.py` and `tests/test_evaluation.py`, expanding `data/demo-test-cases.json`, and drafting `docs/modelos-de-resposta.md`, `docs/avaliacao.md`, `docs/teste-usabilidade.md` and the README sections on results and examples. It also updated two package 1 tests that depended on outdated base values.

The assistant itself still uses no external AI: answers are built by fixed rules from the knowledge-base fields.

Critical validation:

- Every rule was checked against real outputs in the terminal and through a running API server, and is covered by unit tests.
- The evaluation results in `results/evaluation.json` come from an actual run, not from estimates. Three expected failures (typo, distant rewording, long question) were kept to show real limits instead of reporting 100%.
- The usability session was **not** simulated: `docs/teste-usabilidade.md` contains only the task script and blank tables to be filled in by the team after a session with a real participant.
- The team must still read and understand the generated code and review the wording of the answers before delivery.

Note: the service records now have review dates (package 1). The earlier statement in this file that all records are drafts with null dates refers to the previous phase.

## Final assembly, 2026-11-19

Claude Code (Anthropic) assisted Caetano de Medeiros Bona in adding `src/sistema.py` (the text menu run with `python src/sistema.py`, reusing `backend.knowledge`, `backend.search` and `backend.assistant` without new response logic), renaming this file to the required path and updating the API description. The menu was checked manually in the terminal for theme navigation, related subjects, matched, empty, ambiguous and unsupported questions, invalid options and both response modes; the existing test suite still passes.

Later the same day, Claude Code helped replace the redirect-only guidance in the `cpf`, `social-registry` and `youth-id` records. The new text uses only facts read from each record's official gov.br page (audience, steps, documents, cost and time frames). The assistant also aligned `frontend/tests/catalog.test.ts` with the reviewed base: it now requires review dates and limits the browser fallback search to its 12 starter scenarios. The evaluation was rerun at 54/56 (96.4%), and `docs/avaliacao.md` and the README were updated with the new numbers. The team should still reread the three rewritten records against their sources before delivery.
