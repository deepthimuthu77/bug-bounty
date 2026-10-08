# Requirements: Bug Hunt Arena

## Problem Statement Mapping

| Feature | Description | Status | Evidence |
|---|---|---|---|
| AI Creates Bugs | Optional Gemini-backed pipeline; deterministic fake-provider content is currently banked | Partial | Factory audit and bank; Gemini run requires a configured key |
| Learner Hunts Bugs | Core loop uses browser execution for Python/JavaScript and a verified public bank | Partial | Editor UI, test runner, and `bank/public.json` |
| Language Picker | Users select from Python, JS, C++, Go, Rust, Java | Planned | UI Language picker on landing page |
| Short Program | The generated code is short (8-40 lines) | Planned | Game layout & factory rules |
| Fair & Fun | Python/JavaScript problems pass the deterministic factory gate; compiled languages are compile-only | Partial | Factory gate and audit; compiled-language execution is not implemented |
| Hints that Teach | Metered hints with points penalty & explanations | Planned | Scoring logic & hint UI |
| Retention & Habit | Daily streak, XP, combo, leaderboard, weakness bias | Planned | Streaks, Leaderboard, Bug Dex |

## Judging Criteria Evidence

| Criterion | What to Show / Measure | Status | Evidence |
|---|---|---|---|
| Problem Alignment | Walk the three "Make it yours" questions to features | Planned | Live feature demo |
| Innovation | Execution-verified bug pipeline, metered hints | Planned | Factory audit log: generated vs accepted vs rejected |
| Learning Design | Tiered hints, explanations, weakness-aware picks | Planned | Hint penalty demo, Bug Dex |
| Engagement | Streaks, daily, Rush Hour, Vault, leaderboard | Planned | Live demo of two modes |
| Code Quality | Typed schemas, modules, tests, CI | Planned | Architecture doc, passing CI |
| Security | Server-side scoring, private bank data, sandboxed execution | Planned | Threat model, tamper tests |
| Accessibility | Keyboard play, text status labels, reduced motion | Planned | Keyboard walkthrough |
| Google Tooling | Built with Antigravity; Gemini API in the factory | Planned | Task, plan, and walkthrough artifacts; factory audit log |
| Completeness | Honest per-tier language support | Planned | Requirements matrix with real status |
