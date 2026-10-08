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
