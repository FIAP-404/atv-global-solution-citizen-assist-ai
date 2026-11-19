# Citizen portal frontend

The user approved the FIAP-themed GOV.BR-inspired direction and authorized implementation of the screens. This is the React frontend phase; the four Python work packages remain for the team.

## Approach

Build a responsive React and TypeScript application in `frontend/`, with five routes: home, search, service detail, assistant and about. Use Vite, React Router, Lucide icons and plain CSS. Keep shared fixture content in `data/services.demo.json`. The adapter is a replaceable demo boundary, not a production Python implementation. No Sites registration or hosted publication: this phase targets the existing team repository and a local preview.

Alternatives considered: a static visual prototype lacks the interactions needed for the handoff; a full Python implementation would consume the teammates' work packages. The selected approach completes the frontend against a documented interface.

## Experience

- FIAP logo and supplied favicon; white portal shell, charcoal hero and pink accents.
- Search, topic filtering, clear results and an empty state.
- Guidance detail with source, content review status, preparation checklist and related services.
- Save service identifiers locally with a saved-only search filter; no personal data or chat history persisted.
- Compare two or three orientations from the result list.
- Assistant in explicit demo mode, with direct/step-by-step response modes, citations, ambiguity handling and unsupported questions.
- About page explains provenance, privacy, scope and academic status.
- Keyboard access, visible focus, mobile reflow, contrast control and reduced-motion support.

## Content and limits

Portuguese user-facing copy lives in localization resources or the Portuguese service data. Identifiers and documentation use English. The 15 fixture records are draft guidance across three topics; their review dates stay null pending the team's content verification. No invented eligibility decisions, fees, deadlines, official integrations or performance claims. Researching three example official service pages establishes the direction, not completed verification of the complete dataset.

## Completion gate

Production build, meaningful search/ambiguity tests and browser checks of navigation, search, detail, comparisons, assistant, mobile width and invalid route. Document the backend contract, four work packages and remaining assignment deliverables.
