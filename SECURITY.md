# Security Policy

## Reporting a Vulnerability

Please do not report security vulnerabilities through public GitHub issues.

If you believe you have found a security vulnerability, please report it to us by email.

## Scope

- Private problem data (solutions, hidden tests, hints) must never reach the client bundle.
- Score, streak, and XP are computed on the server only.
- Learner code runs only in a sandboxed worker or remote runner.
- Secrets (`GEMINI_API_KEY`, `DATABASE_URL`) are never exposed in the browser bundle or committed to git.
