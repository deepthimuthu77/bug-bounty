from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

from . import PROMPT_VERSION
from .models import Audit, Candidate, Spec
from .operators import apply_mutations
from .providers import FakeProvider, GeminiProvider, candidate_from_response
from .verification import fingerprint, verify_candidate
from .verification import validate_hints

ROOT = Path(__file__).resolve().parents[1]
BANK = ROOT / "bank"


def _load_dotenv() -> None:
    path = ROOT / ".env"
    if not path.exists():
        return
    for line in path.read_text().splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip("\"'"))


def _provider(name: str):
    if name == "fake":
        return FakeProvider()
    if name == "gemini":
        return GeminiProvider()
    if name == "auto":
        if os.getenv("GEMINI_API_KEY"):
            return GeminiProvider()
        print("No GEMINI_API_KEY found; using deterministic fake provider (not AI-generated).", file=sys.stderr)
        return FakeProvider()
    raise ValueError(name)


def _new_specs(args: argparse.Namespace) -> list[Spec]:
    languages = args.languages or ["python", "javascript"]
    return [Spec(language=lang, topic=args.topic, difficulty=args.difficulty, concept=args.concept) for lang in languages for _ in range(args.count)]


def _candidate_pool(spec: Spec, provider: Any) -> list[Candidate]:
    raw = provider.generate(spec)
    source_kind = "llm" if provider.name == "google-genai" else "mutation"
    base = candidate_from_response(spec, raw, generator=source_kind, model=provider.model)
    # The LLM proposal itself enters the candidate pool.
    candidates = [base]
    # Deterministic mutation operators also enter the same frozen pool.
    for mutation in apply_mutations(spec.language, base.correct_code):
        mutated = Candidate(
            language=spec.language, topic=spec.topic, difficulty=spec.difficulty, concept=spec.concept,
            title=base.title, category=mutation.category, correct_code=base.correct_code,
            buggy_code=mutation.code, visible_tests=base.visible_tests, hidden_tests=base.hidden_tests,
            bug_line_range=mutation.line_range, generator="mutation", model=base.model,
            prompt_version=PROMPT_VERSION, hints=list(base.hints), explanation=base.explanation,
            real_code_example=base.real_code_example,
        )
        candidates.append(mutated)
    return candidates


def _load_audit() -> dict[str, Any]:
    path = BANK / "audit.json"
    if path.exists():
        try:
            return json.loads(path.read_text())
        except json.JSONDecodeError:
            return {"generated": 0, "accepted": 0, "rejected": {}, "entries": []}
    return {"generated": 0, "accepted": 0, "rejected": {}, "entries": []}


def _write_bank(candidates: list[Candidate], audit: Audit) -> None:
    BANK.mkdir(parents=True, exist_ok=True)
    public_path, private_path = BANK / "public.json", BANK / "private.json"
    public: list[dict[str, Any]] = json.loads(public_path.read_text()) if public_path.exists() else []
    private: list[dict[str, Any]] = json.loads(private_path.read_text()) if private_path.exists() else []
    known = {p["fingerprint"] for p in public}
    for candidate in candidates:
        if candidate.fingerprint in known:
            continue
        known.add(candidate.fingerprint)
        public.append({
            "id": f"factory-{candidate.fingerprint}", "language": candidate.language,
            "mode_support": ["classic"], "title": candidate.title,
            "difficulty": candidate.difficulty, "category": candidate.category,
            "concept": candidate.concept, "buggy_code": candidate.buggy_code,
            "visible_tests": candidate.visible_tests, "par_seconds": 60,
            "generator": candidate.generator, "fingerprint": candidate.fingerprint,
        })
        private.append({
            "id": f"factory-{candidate.fingerprint}", "correct_code": candidate.correct_code,
            "hidden_tests": candidate.hidden_tests, "bug_line_range": list(candidate.bug_line_range),
            "hints": candidate.hints, "explanation": candidate.explanation,
            "real_code_example": candidate.real_code_example, "difficulty_score": candidate.difficulty_score,
        })
    public_path.write_text(json.dumps(public, indent=2, ensure_ascii=False) + "\n")
    private_path.write_text(json.dumps(private, indent=2, ensure_ascii=False) + "\n")
    existing = _load_audit()
    existing["generated"] = existing.get("generated", 0) + audit.generated
    existing["accepted"] = existing.get("accepted", 0) + audit.accepted
    for reason, count in audit.rejected.items():
        existing["rejected"][reason] = existing["rejected"].get(reason, 0) + count
    existing.setdefault("entries", []).extend(audit.entries)
    existing["prompt_version"] = PROMPT_VERSION
    existing["unique_public_bank_count"] = len(public)
    existing["unique_private_bank_count"] = len(private)
    (BANK / "audit.json").write_text(json.dumps(existing, indent=2, ensure_ascii=False) + "\n")


def generate(args: argparse.Namespace) -> int:
    _load_dotenv()
    provider = _provider(args.provider)
    audit = Audit()
    accepted: list[Candidate] = []
    known: set[str] = set()
    for spec in _new_specs(args):
        try:
            pool = _candidate_pool(spec, provider)  # Freeze pool before applying acceptance-only gates.
        except Exception as exc:
            audit.generated += 1
            placeholder = Candidate(spec.language, spec.topic, spec.difficulty, spec.concept, "provider error", "unknown", "", "", [], [], (0, 0), "llm", getattr(provider, "model", "unknown"), PROMPT_VERSION)
            audit.reject(f"provider error: {exc}", placeholder)
            continue
        for candidate in pool:
            audit.generated += 1
            if hasattr(provider, "regenerate_hints") and validate_hints(candidate):
                for _attempt in range(2):
                    try:
                        hints = provider.regenerate_hints(candidate)
                        candidate.hints = list(hints.get("hints", []))
                        candidate.explanation = str(hints.get("explanation", ""))
                        candidate.real_code_example = str(hints.get("real_code_example", ""))
                    except Exception:
                        break
                    if not validate_hints(candidate):
                        break
            result = verify_candidate(candidate)
            if not result.accepted:
                candidate.rejection_reasons = result.reasons
                for reason in sorted(set(result.reasons)):
                    audit.reject(reason, candidate)
                continue
            if candidate.fingerprint in known:
                audit.reject("duplicate fingerprint", candidate)
                continue
            known.add(candidate.fingerprint)
            accepted.append(candidate)
            audit.accept(candidate)
    _write_bank(accepted, audit)
    print(format_stats(audit.generated, audit.accepted, audit.rejected))
    print(f"Accepted this run: {len(accepted)}; provider: {provider.name} ({provider.model})")
    return 0


def verify(args: argparse.Namespace) -> int:
    path = Path(args.path)
    if not path.is_absolute():
        path = ROOT / path
    data = json.loads(path.read_text())
    candidates = data if isinstance(data, list) else [data]
    failed = 0
    for record in candidates:
        candidate = candidate_from_response(
            Spec(record["language"], record.get("topic", ""), record.get("difficulty", "easy"), record.get("concept", "")),
            {key: record[key] for key in ("title", "category", "correct_code", "buggy_code", "visible_tests", "hidden_tests", "bug_line_range", "hints", "explanation", "real_code_example")},
            generator=record.get("generator", "mutation"), model=record.get("model", "offline"),
        )
        result = verify_candidate(candidate)
        print(f"{candidate.language} {fingerprint(candidate)}: {'ACCEPT' if result.accepted else 'REJECT'}")
        for reason in result.reasons:
            print(f"  - {reason}")
        failed += not result.accepted
    return 1 if failed else 0


def stats() -> int:
    audit = _load_audit()
    print(format_stats(audit.get("generated", 0), audit.get("accepted", 0), audit.get("rejected", {})))
    print(f"Bank entries: {audit.get('unique_public_bank_count', 0)} public / {audit.get('unique_private_bank_count', 0)} private")
    return 0


def build_bank(args: argparse.Namespace) -> int:
    path = Path(args.path)
    if not path.is_absolute():
        path = ROOT / path
    data = json.loads(path.read_text())
    candidates: list[Candidate] = []
    audit = Audit()
    for record in data if isinstance(data, list) else [data]:
        candidate = candidate_from_response(
            Spec(record["language"], record.get("topic", ""), record.get("difficulty", "easy"), record.get("concept", "")),
            {key: record[key] for key in ("title", "category", "correct_code", "buggy_code", "visible_tests", "hidden_tests", "bug_line_range", "hints", "explanation", "real_code_example")},
            generator=record.get("generator", "mutation"), model=record.get("model", "offline"),
        )
        result = verify_candidate(candidate)
        audit.generated += 1
        if result.accepted:
            audit.accept(candidate)
            candidates.append(candidate)
        else:
            for reason in sorted(set(result.reasons)):
                audit.reject(reason, candidate)
    _write_bank(candidates, audit)
    print(format_stats(audit.generated, audit.accepted, audit.rejected))
    return 0 if not audit.rejected else 1


def format_stats(generated: int, accepted: int, rejected: dict[str, int]) -> str:
    reasons = ", ".join(f"{key}: {value}" for key, value in sorted(rejected.items())) or "none"
    return f"Factory stats — generated: {generated}; accepted: {accepted}; rejected by reason: {reasons}"


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(prog="python -m factory.cli", description="Generate, verify, and audit execution-verified bug candidates")
    sub = root.add_subparsers(dest="command", required=True)
    gen = sub.add_parser("generate", help="generate candidates and add verified problems to the bank")
    gen.add_argument("--provider", choices=("auto", "gemini", "fake"), default="auto")
    gen.add_argument("--languages", nargs="+", choices=("python", "javascript", "cpp", "go", "rust", "java"), default=["python", "javascript"])
    gen.add_argument("--count", type=int, default=1, help="generation rounds per language")
    gen.add_argument("--topic", default="beginner programming")
    gen.add_argument("--difficulty", choices=("easy", "medium", "hard"), default="easy")
    gen.add_argument("--concept", default="loops and equality")
    gen.set_defaults(func=generate)
    check = sub.add_parser("verify", help="verify candidate JSON")
    check.add_argument("path", help="JSON candidate file")
    check.set_defaults(func=verify)
    bank = sub.add_parser("build-bank", help="verify candidate JSON and add accepted entries to the split bank")
    bank.add_argument("path", help="JSON candidate file or array")
    bank.set_defaults(func=build_bank)
    summary = sub.add_parser("stats", help="show accumulated generation and rejection counts")
    summary.set_defaults(func=lambda _args: stats())
    return root


def main() -> int:
    args = parser().parse_args()
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
