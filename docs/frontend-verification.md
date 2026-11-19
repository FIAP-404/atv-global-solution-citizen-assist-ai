# Frontend verification

Date: 2026-11-18. Scope: the React frontend with local demo data, not the Python coursework implementation.

## Automated checks

- `npm test`: 21 passing tests, including 12 starter consultation scenarios, accent/alias matching, filtering, empty/ambiguous/unsupported behavior, catalog integrity and rejection of malformed API responses.
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

No real Python API, network failure integration test, external LLM, production deployment, physical phone or full screen-reader audit was exercised. The share action and print stylesheet are implemented but were not exercised through the operating system dialogs. Service references and requirements remain subject to content review. Performance and usability metrics for the final assignment have not been measured.

## Coordination template

The public coordination repository's root directory and README were read through GitHub. The README describes a portfolio organized by course year, phases and Global Solution folders. This does not recover the content of the two invisible tables in the assignment capture; exact submission packaging remains a final team check.
