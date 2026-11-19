# Python handoff implementation plan

> **For agentic workers:** Use inline execution for this coordinator scaffold. Do not implement the colleagues' four core algorithms.

**Goal:** Leave a runnable transport scaffold and exact module contracts for the team.

**Architecture:** FastAPI and a terminal entry point delegate to four module functions. Pending functions fail explicitly. Shared response models preserve the React JSON contract.

**Tech Stack:** Python 3.11+, FastAPI, Uvicorn, Pydantic, HTTPX2 for tests, unittest.

**Spec:** `docs/design/backend-handoff-spec.md`

## Global constraints

- No external AI, paid service, credentials or automatic source verification.
- Group members choose their own module ownership.
- Preserve lists/dictionaries in core algorithm interfaces.
- Pending modules must never produce fake successful consultations.
- Code identifiers and help/error strings use English.

## Review focus

- Unimplemented modules return explicit errors, not demo records.
- Invalid questions, response modes and topics are rejected at the API boundary.
- CamelCase source metadata survives serialization.
- CLI and HTTP call the same core functions and final data path.
- Passing scaffold tests must not be reported as completed coursework evaluation.

### Task 1: Transport tests and environment

- [x] Add requirements and API/CLI tests for the stated boundaries.
- [x] Install into the ignored `.venv` and observe the missing implementation fail.

### Task 2: Coordinator scaffold

- [x] Add four pending modules with fixed signatures, response models, FastAPI endpoints and terminal wiring.
- [x] Pass the transport tests without implementing the four algorithms.

### Task 3: Handoff documentation

- [x] Record the approved no-external-AI decision and group-selected ownership.
- [x] Document setup, individual responsibilities, exact commands and remaining evidence.
- [x] Run Python tests, frontend tests/build, dependency checks and diff checks.
