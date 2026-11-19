# Frontend verification

Date: 2026-11-18. Scope: the React frontend with local demo data, not the Python coursework implementation.

## Automated checks

- `npm test`: 25 passing tests, including 12 starter consultation scenarios, accent/alias matching, filtering, empty/ambiguous/unsupported behavior, catalog integrity, rejection of malformed API responses and HTTP cancellation.
- `npm run build`: TypeScript checking and a Vite production build passed.
- Runtime dependencies were installed with npm and recorded in `frontend/package-lock.json`.

## Browser observations

Checked in the in-app browser using the local Vite server:

- Home page: actual supplied FIAP logo, topic navigation and service cards rendered.
- CPF search returned the two corresponding orientations.
- Two-service comparison displayed source, authority, channel and summary.
- Three-service selection displayed four table columns (one field column and three service columns); a fourth service selection was refused with the intended message.
- Saving a service updated the count; the saved filter returned it; clearing saved records removed it.
- A preparation checkbox updated the progress from zero to one.
- Empty assistant input displayed a validation error.
- An ambiguous document question returned candidate services.
- An out-of-scope weather question displayed a limitation instead of guidance.
- Step-by-step mode returned the work-card orientation with steps, limitations and source.
- Mobile menu, topic filtering and empty results worked.
- Layout inspected at desktop width 1440 and mobile widths 375 and 320; no page-level horizontal overflow was observed in the inspected home, service detail, assistant and about layouts.
- Mobile search and saved controls received explicit accessible names after the browser check found an icon-only label issue.
- High contrast was toggled through the mobile navigation.
- An unknown service identifier displayed a recovery path.
- Browser console inspection returned no errors after the representative checks.
- Independent review identified two integration issues: trusting malformed successful API responses and restoring focus while the composer was disabled. Both were fixed. Adapter tests now reject malformed payloads, duplicate identifiers, unsafe source URL schemes and inconsistent answer cardinality; a browser recheck confirmed focus returns to `citizen-question` after a suggestion receives an answer.

## Verification limits

No real Python API, external LLM, production deployment, physical phone or full screen-reader audit was exercised. A controlled HTTP failure fixture was exercised during the simplification review below. The share action and print stylesheet are implemented but were not exercised through the operating system dialogs. Service references and requirements remain subject to content review. Performance and usability metrics for the final assignment have not been measured.

## Simplification review

Three read-only reviewers examined reuse, quality and efficiency. Confirmed fixes:

- Reject array/object values for string-enum fields instead of coercing them with `String`, preventing accepted malformed API records from crashing service cards.
- Abort catalog, search and assistant requests when they become obsolete or their page unmounts. Keep the 12-second timeout and suppress state updates from cancelled requests.
- Add JSON content type only for requests with a body, avoiding unnecessary preflight for simple catalog GET requests.
- Show an error in the results toolbar when a search fails, instead of showing the previous query's count.
- Derive the saved flag once per service card and format TypeScript/JSX for team readability.

Regression evidence: the new enum test failed before the fix and passed afterwards. Transport tests cover headers, HTTP failures and cancellation of an in-flight request. A temporary local HTTP fixture returned two CPF results and then a controlled 503 for a new query; the browser displayed the error without the old result count. The fixture was only a test aid, not an implementation of the Python backend. The assistant demo was rechecked with its response source and restored composer focus.

No caching, indexing or additional component layers were added for the 15-record catalog. Conversation history remains in memory for the current page lifetime; arbitrary truncation was deferred because it would change behavior.

## Coordination template

The public coordination repository's root directory and README were read through GitHub. The README describes a portfolio organized by course year, phases and Global Solution folders. This does not recover the content of the two invisible tables in the assignment capture; exact submission packaging remains a final team check.
