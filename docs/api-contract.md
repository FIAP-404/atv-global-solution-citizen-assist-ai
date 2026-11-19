# Python API integration contract

Status: proposed interface implemented by the frontend adapter. There is no Python server in this phase.

## Running modes

The React application runs against the local JSON fixture when `VITE_API_BASE_URL` is absent. To connect a Python server, copy `frontend/.env.example` to `frontend/.env.local`, configure the address and restart Vite. Example base URL: `http://127.0.0.1:8000/api/v1`.

The only frontend network boundary is `frontend/src/api/client.ts`. Set CORS on the Python server to allow the actual frontend origin, usually `http://127.0.0.1:5173`. Do not embed secrets in any `VITE_` variable: these values are public in the browser bundle.

## Service record

See `frontend/src/domain/types.ts` for the TypeScript contract and `data/services.demo.json` for all examples. JSON field names are case-sensitive and use camelCase for the HTTP interface. Python internal identifiers can use snake_case.

| Field | Type | Meaning |
| --- | --- | --- |
| `id` | string | Stable unique URL identifier |
| `topic` | `documents`, `work`, `social` | Top-level theme |
| `title`, `summary`, `audience` | string | Portuguese display content |
| `keywords` | string array | Search terms and aliases |
| `agency` | string | Responsible public authority |
| `channel` | `digital`, `in-person`, `mixed` | Reference service channel, subject to content verification |
| `source.title`, `source.url` | string | Source label and HTTPS official reference |
| `source.reviewedAt` | ISO date string or null | Actual review date; null means pending |
| `steps`, `preparation` | string arrays | Guidance steps and consultation preparation |
| `limitations` | string | Explicit scope and uncertainty |
| `relatedIds` | string array | At least three related service identifiers |

Keep metadata and requirements grounded in the official source. The current fixture is a draft and must not be presented as fully verified guidance.

## Endpoints consumed now

### `GET /services`

Return `200` with `{ "items": [Service] }`. This loads the complete small catalog used by detail pages, related services and comparisons. Every `relatedIds` entry must resolve inside this catalog.

### `GET /services?query=cpf&topic=documents`

Return `200` with `{ "items": [Service], "query": "cpf" }`, ordered by relevance. Empty query lists the selected topic; `topic=all` lists all topics. No result is `{ "items": [], "query": "..." }`, not an HTTP error. Search is accent- and case-insensitive. Explain the Python algorithm, scoring and tie handling in the implementation documentation.

### `POST /assistant/query`

Request:

```json
{ "question": "Como acessar a Carteira de Trabalho Digital?", "mode": "steps" }
```

Response:

```json
{
  "status": "matched",
  "message": "Encontrei uma orientação relacionada à sua pergunta.",
  "services": [],
  "mode": "steps"
}
```

The example omits service bodies for brevity. For `matched`, `services` MUST contain exactly one full `Service` record, not an empty array. The frontend renders that record's summary, source, limitations and (for `steps`) its steps.

| Status | Services | Expected behavior |
| --- | --- | --- |
| `empty` | empty | Ask the person to enter a question |
| `unsupported` | empty | State the limitation and offer another consultation path |
| `ambiguous` | two or three candidates | Ask which service the person intended |
| `matched` | exactly one | Present source-backed guidance |

`mode` is `direct` or `steps`. Both formats must retain sources and limitations. The current browser version is a deterministic demonstration, not an external language model. The Python owner must document two instructions and compare their usefulness on the test questions.

For malformed payloads, unsupported modes or questions above 500 characters, return an appropriate `4xx` JSON error. Technical failures return `5xx`. The frontend displays a retry message without inventing an answer. Requests time out after 12 seconds; the adapter does not silently fall back to demo content when a configured server fails.

The frontend cancels obsolete requests when filters change or a requesting page unmounts. Simple GET requests do not send a JSON content type; JSON POST requests do.

The adapter validates service fields, array shapes, unique identifiers, HTTPS source URLs, response modes and status/cardinality consistency before passing responses to React. Malformed successful responses produce the same recoverable error UI as a failed request.

## Frontend-owned behavior

Routing, filters, comparisons (up to three records), printing, share-link copying and ephemeral preparation checklists stay in React. Saved state stores only service IDs under `citizen-assist:saved` in localStorage. Chat text and checklist state are not persisted. The browser demo search is temporary scaffolding for screen development; it is not a substitute for Python coursework.

## Integration acceptance

- Load the catalog and open every returned service identifier.
- Query accented terms, aliases, multiple matches and no matches.
- Submit empty, ambiguous, direct and unsupported questions in both response modes.
- Disconnect the server and confirm error/retry UI without stale fabricated answers.
- Complete the coursework tests against Python separately; frontend demo checks do not prove backend correctness.
