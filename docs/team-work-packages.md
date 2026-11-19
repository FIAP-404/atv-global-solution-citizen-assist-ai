# Python team work packages

Five-person arrangement: the coordinator owns React and integration; four colleagues own the Python packages below. Names and RMs must be confirmed by the coordinator before the final README is completed.

Work on separate branches. Keep the contract in `api-contract.md` stable; propose changes before altering public JSON fields. Suggested file names below are new English identifiers, not existing implemented modules.

## Package 1: Knowledge base and content

Owner: colleague 1.

- Implement `backend/knowledge.py` to load JSON/CSV into lists and dictionaries, validate required fields and report missing, empty or inconsistent files.
- Review all 15 draft records in `data/services.demo.json` against identifiable official sources. Correct URLs, scope, audience, channel and content; record actual review dates only after checking them.
- Keep at least five orientations in each of the three themes. Review at least three relationships per service with the search owner.
- Produce `data/services.json` for the final verified base and explain the schema and update procedure.

Suggested interface: `load_services(path) -> list[dict]`. Fail clearly on invalid content; never convert an empty or broken file into apparent success.

Acceptance: missing file, empty file, malformed JSON, missing source, duplicate IDs, invalid dates and broken relationships are handled and tested. Supply accurate metadata, not invented fees or eligibility rules.

## Package 2: Search and navigation

Owner: colleague 2. Depends on package 1's record format; can begin with the demo file.

- Implement `backend/search.py` with accent/case normalization, keyword aliases and a justified ranking strategy.
- Represent themes/subthemes or relations as a hierarchy/graph and expose related orientations.
- Implement query and theme filtering for `GET /services` using the shared contract.
- Explain and demonstrate tie handling, empty search and unmatched queries.

Suggested interface: `search_services(records, query, topic="all") -> list[dict]`. Keep the optional HTTP layer separate from the algorithm so the terminal entry point can reuse it.

Acceptance: variations of CPF, CTPS and CadÚnico work; topic filtering works; out-of-scope queries do not return arbitrary guidance. Use the 12 starter scenarios as a baseline, adding reformulations and adversarial inputs.

## Package 3: Responses and HTTP integration

Owner: colleague 3. Depends on package 2's search result format; coordinate the API boundary with the frontend owner.

- Implement `backend/assistant.py` with the four response statuses and two documented response instructions: direct and step-by-step.
- Ask for clarification on ambiguity. Always include sources and limitations. Do not pretend to perform official operations or decide eligibility.
- Add a small Python HTTP application in `backend/api.py` consuming packages 1 and 2. Match `GET /services` and `POST /assistant/query` exactly, including field casing, status codes, limits and CORS.
- Provide an English-named terminal entry point such as `src/main.py` that reuses the same logic. The assignment example `src/sistema.py` must be reconciled explicitly with the coordinator before submission; the project coding rule requires English names for new code.
- Document both instruction templates and the decision on using an external model. Paid APIs and an LLM are not mandatory.

Acceptance: empty/ambiguous/unsupported/matched inputs, 500-character limit, both modes, errors and an end-to-end browser request work. API and terminal consult the same base and logic.

## Package 4: Evaluation and evidence

Owner: colleague 4. Can define expected outcomes before Python implementation, then execute against packages 1–3.

- Extend `data/demo-test-cases.json` into a final evaluation set with at least 12 questions: direct questions, reformulations and out-of-scope questions.
- Include at least three limitation cases: empty input, ambiguity and no reliable answer.
- Implement `backend/evaluation.py` to record expected/actual response, correct/incorrect classification and measured query duration. Calculate accuracy and a simple mean time.
- Compare both response instruction models and justify clarity/consistency conclusions using recorded evidence.
- Run a usability session with at least one test user or task script; record difficulties, outcomes, at least two improvements and evaluation limits.
- Save reproducible evidence and a final interpretation. Do not substitute browser demo test results for measured Python results.

Acceptance: reproducible command, saved actual results, metric calculation and interpretation, response-model comparison and usability evidence.

## Coordinator: Frontend and final assembly

- Integrate the Python adapter and verify loading/error/empty/success states.
- Confirm the team's names/RMs and review content/official status messaging.
- Complete README, AI usage documentation, final evidence, video and the two-link TXT required by the assignment.
- Check the coordination template and reconcile submission layout. Its public README currently describes a portfolio hierarchy with separate Global Solution folders; it does not recover the two missing tables in the PDF capture.
- Demonstrate the complete integrated consultation flow before claiming the assignment is finished.
