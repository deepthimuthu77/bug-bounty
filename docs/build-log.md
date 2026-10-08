# Build Log

## Stage 0
- Initialized Next.js (TypeScript, Tailwind, App Router) and cleared boilerplate.
- Added Python Bug Factory package (`factory/`) and database (`db/`) directories.
- Authored `docs/requirements.md` to map problems and criteria to observable features.
- Configured GitHub Actions CI (`.github/workflows/ci.yml`) and `npm run check`.
- Built an accessible and dynamic landing page in `src/app/page.tsx` with all 6 required languages and mock loading/error states.
- Initialized security, environment, and README documentation.

## Stage 1
- Implemented the `Problem` and `Attempt` schemas in `src/lib/schemas.ts`.
- Set up `BrowserExecutor` using Web Workers for sandboxed code evaluation.
- Added `js-runner.worker.js` with output intercepting and loop timeouts.
- Added `py-runner.worker.js` utilizing `pyodide` for in-browser Python execution.
- Created `ArenaClient` UI component leveraging `@uiw/react-codemirror` and custom hacking aesthetics.
- Added seeded problems for JavaScript and Python designed to fail specific tests initially.

## Stage 2
- Added the `factory` Python package with a deterministic fake provider, optional Google Gen AI provider, structured-response validation, and bounded retry handling.
- Added deterministic Python and JavaScript mutation operators plus a verification gate for correct-answer tests, mixed buggy results, three-run determinism, single-hunk diffs, and hint rules. C++, Go, Rust, and Java currently receive compile checks only and are not accepted as runnable game problems.
- Added `generate`, `verify`, `build-bank`, and `stats` CLI commands. Public problems are in `bank/public.json`; answer keys and hidden tests are in ignored `bank/private.json`; `bank/audit.json` records generated, accepted, and rejected counts.
- Wired the public bank into the app's problem list. The deterministic fake-provider run produced 5 candidates, accepted 3, and rejected 2 duplicate fingerprints (2 Python and 1 JavaScript unique problems).
- Verified with `python3 -m unittest factory.test_factory -v` (11 tests), `npm run lint`, `npx tsc --noEmit`, and `npx next build --webpack`.
- Gemini was not smoke-tested and the 40-problem bank target was not met because no `GEMINI_API_KEY` is configured. The checked-in bank is explicitly fake-provider content, not AI-generated content.
