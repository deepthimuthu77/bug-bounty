# Requirements: Bug Hunt Arena

## Problem Statement Mapping

| Feature | Description | Status | Evidence |
|---|---|---|---|
| AI Creates Bugs | Pipeline to generate bugs using AI via Gemini | Planned | Factory logs & verified bug bank |
| Learner Hunts Bugs | Core loop where users fix broken code | Planned | Editor UI & test runner |
| Language Picker | Users select from Python, JS, C++, Go, Rust, Java | Planned | UI Language picker on landing page |
| Short Program | The generated code is short (8-40 lines) | Planned | Game layout & factory rules |
| Fair & Fun | Bugs verified deterministically and pass gate rules | Planned | Factory acceptance criteria |
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
