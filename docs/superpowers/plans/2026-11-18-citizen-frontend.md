# Citizen portal frontend implementation plan

> **For agentic workers:** Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Complete the agreed React screens and leave a clear integration boundary for the Python team.

**Architecture:** React Router renders five screens. Shared typed service data and a replaceable adapter provide demo queries and responses. Browser-local state stores only saved service identifiers.

**Tech Stack:** React, TypeScript, Vite, React Router, Lucide, CSS, Node test runner.

**Spec:** `docs/design/frontend-spec.md`

## Global constraints

- Use the supplied FIAP logo and favicon.
- All code identifiers and comments use English; Portuguese copy is localized.
- Clearly identify draft demo data and the academic portal.
- Leave Python responsibilities to the four team work packages.

## Review focus

- Empty and unsupported questions never produce invented guidance.
- Accent variations and ambiguous document questions yield useful results.
- Mobile layouts and long titles do not overflow.
- Missing service identifiers and invalid routes have a recovery path.
- Saved state failures do not prevent consultation; comparisons hold at most three services.

### Task 1: Data and demo adapter

- [x] Add search tests for accents, filters, unsupported input and ambiguity; run and observe failure.
- [x] Implement `searchServices(records, query, topic?)` and `classifyQuestion(records, question)` in `frontend/src/domain/search.ts`; add typed fixtures and adapter.
- [x] Run `npm test` in `frontend` and confirm passing.

### Task 2: Responsive screens

- [x] Build shared shell and five screens from the spec, consuming the adapter and localized copy.
- [x] Add bookmarks, comparisons and a preparation checklist without collecting identity data.
- [x] Run `npm run build`; inspect browser behavior on desktop and mobile.

### Task 3: Team handoff

- [x] Document exact HTTP contracts and four independent Python work packages.
- [x] Update README commands, AI usage and remaining deliverables.
- [x] Run tests, production build and diff checks; report implementation and verification limits.
