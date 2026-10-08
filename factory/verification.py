from __future__ import annotations

import ast
import difflib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass

from .models import Candidate

TIMEOUT_SECONDS = 2
RUNS = 3
MAX_CHANGED_LINES = 4


@dataclass
class GateResult:
    accepted: bool
    reasons: list[str]
    results: list[list[bool]]


def _unsafe_source(language: str, source: str) -> str | None:
    lowered = source.lower()
    patterns = {
        "python": [r"\b(open|exec|eval|__import__)\s*\(", r"\b(import|from)\s+(os|sys|socket|subprocess|pathlib|urllib|requests|time|random)\b", r"\bwhile\s+true\s*:"],
        "javascript": [r"\b(require|import)\s*\(?\s*['\"](?:fs|net|http|https|child_process|os|crypto|timers?)\b", r"\b(fetch|settimeout|setinterval)\s*\(", r"\bwhile\s*\(\s*true\s*\)"],
    }
    for pattern in patterns.get(language, []):
        if re.search(pattern, lowered):
            return "unsafe operation detected (file, network, clock, process, or unbounded loop)"
    return None


def _python_results(program: str, tests: list[dict[str, str]]) -> list[str]:
    try:
        tree = ast.parse(program)
    except SyntaxError as exc:
        raise ValueError(f"parse error: {exc.msg} at line {exc.lineno}") from exc
    forbidden_calls = {"open", "exec", "eval", "compile", "__import__", "input"}
    forbidden_modules = {"os", "sys", "socket", "subprocess", "pathlib", "urllib", "requests", "time", "random"}
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in forbidden_calls:
            raise ValueError(f"unsafe call: {node.func.id}")
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            names = [alias.name.split(".")[0] for alias in node.names] if isinstance(node, ast.Import) else [str(node.module or "").split(".")[0]]
            if forbidden_modules.intersection(names):
                raise ValueError("unsafe import")
    outputs = []
    for test in tests:
        runner = program + "\n" + test["input"] + "\n"
        proc = subprocess.run([sys.executable, "-I", "-S", "-c", runner], capture_output=True, text=True, timeout=TIMEOUT_SECONDS, env={"PATH": os.environ.get("PATH", "")})
        if proc.returncode != 0:
            outputs.append("!ERROR!" + proc.stderr[-500:])
        else:
            outputs.append(proc.stdout)
    return outputs


def _javascript_results(program: str, tests: list[dict[str, str]]) -> list[str]:
    node = shutil.which("node")
    if not node:
        raise ValueError("toolchain missing: node")
    outputs = []
    for test in tests:
        proc = subprocess.run([node, "--disable-proto=throw", "-e", program + "\n" + test["input"]], capture_output=True, text=True, timeout=TIMEOUT_SECONDS, env={"PATH": os.environ.get("PATH", "")})
        if proc.returncode != 0:
            outputs.append("!ERROR!" + proc.stderr[-500:])
        else:
            outputs.append(proc.stdout)
    return outputs


def _compile_only(language: str, source: str) -> None:
    tools = {"cpp": "g++", "go": "go", "rust": "rustc", "java": "javac"}
    if language not in tools:
        raise ValueError(f"unsupported language: {language}")
    if not shutil.which(tools[language]):
        raise ValueError(f"toolchain missing: {language}")
    extensions = {"cpp": ".cpp", "go": ".go", "rust": ".rs", "java": ".java"}
    with tempfile.TemporaryDirectory(prefix="bug-factory-") as directory:
        path = os.path.join(directory, "Candidate" + extensions[language])
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(source)
        if language == "cpp":
            command = [tools[language], "-fsyntax-only", path]
        elif language == "go":
            command = [tools[language], "test", path]
        elif language == "rust":
            command = [tools[language], "--emit=metadata", "-o", os.path.join(directory, "candidate.rmeta"), path]
        else:
            command = [tools[language], "-d", directory, path]
        proc = subprocess.run(command, capture_output=True, text=True, timeout=TIMEOUT_SECONDS)
        if proc.returncode:
            raise ValueError(f"compile error: {(proc.stderr or proc.stdout)[-500:]}")


def run_program(language: str, program: str, tests: list[dict[str, str]]) -> list[bool]:
    if language in ("python", "javascript"):
        unsafe = _unsafe_source(language, program)
        if unsafe:
            raise ValueError(unsafe)
        output = _python_results(program, tests) if language == "python" else _javascript_results(program, tests)
        return [actual == test["expected"] for actual, test in zip(output, tests)]
    _compile_only(language, program)
    return [True for _test in tests]


def _small_single_hunk(correct: str, buggy: str) -> bool:
    diff = list(difflib.unified_diff(correct.splitlines(), buggy.splitlines(), lineterm=""))[2:]
    changed = [line for line in diff if line.startswith(("+", "-")) and not line.startswith(("+++", "---"))]
    hunks = sum(1 for line in diff if line.startswith("@@"))
    return hunks == 1 and 0 < len(changed) <= MAX_CHANGED_LINES


def fingerprint(candidate: Candidate) -> str:
    import hashlib
    canonical = "\0".join((candidate.language, candidate.buggy_code.strip(), json.dumps(candidate.visible_tests, sort_keys=True)))
    return hashlib.sha256(canonical.encode()).hexdigest()[:20]


def rate_difficulty(candidate: Candidate, failing: int) -> int:
    changed = sum(1 for a, b in zip(candidate.correct_code.splitlines(), candidate.buggy_code.splitlines()) if a != b)
    length = len(candidate.buggy_code.splitlines())
    return min(100, max(1, {"easy": 15, "medium": 35, "hard": 55}[candidate.difficulty] + min(length, 30) + changed * 5 + failing * 3))


def validate_hints(candidate: Candidate) -> list[str]:
    errors = []
    if len(candidate.hints) != 3 or any(not isinstance(h, str) or not h.strip() for h in candidate.hints):
        errors.append("hints must contain exactly three non-empty strings")
    for hint in candidate.hints:
        if "```" in hint:
            errors.append("hint contains a code fence")
        if len(hint.strip()) < 8:
            errors.append("hint is too short")
    diff_text = "\n".join(line[1:].strip() for line in difflib.ndiff(candidate.correct_code.splitlines(), candidate.buggy_code.splitlines()) if line.startswith("- "))
    tokens = set(re.findall(r"\w+", diff_text.lower()))
    for hint in candidate.hints:
        overlap = tokens.intersection(re.findall(r"\w+", hint.lower()))
        if len(overlap) >= 3:
            errors.append("hint overlaps too much with the fix diff")
            break
    lines = candidate.buggy_code.splitlines()
    start, end = candidate.bug_line_range
    if start < 1 or end < start or end > len(lines):
        errors.append("location hint range is outside the buggy program")
    elif not re.search(rf"\b{start}\b", candidate.hints[1]):
        errors.append("location hint must name a line in the bug range")
    if not candidate.explanation.strip():
        errors.append("missing explanation")
    if not candidate.real_code_example.strip():
        errors.append("missing real-code example")
    return errors


def verify_candidate(candidate: Candidate) -> GateResult:
    reasons: list[str] = []
    all_tests = candidate.visible_tests + candidate.hidden_tests
    if not candidate.visible_tests or not candidate.hidden_tests:
        reasons.append("visible and hidden tests are both required")
    if not all_tests:
        return GateResult(False, reasons or ["no tests"], [])
    try:
        correct_runs = [run_program(candidate.language, candidate.correct_code, all_tests) for _ in range(RUNS)]
        if not all(all(result) for result in correct_runs):
            reasons.append("correct program failed tests")
        if any(result != correct_runs[0] for result in correct_runs[1:]):
            reasons.append("correct program is nondeterministic")
        runs = [run_program(candidate.language, candidate.buggy_code, all_tests) for _ in range(RUNS)]
    except subprocess.TimeoutExpired:
        return GateResult(False, ["execution timed out"], [])
    except (ValueError, OSError) as exc:
        return GateResult(False, [str(exc)], [])
    if any(result != runs[0] for result in runs[1:]):
        reasons.append("buggy results differ across 3 runs")
    if not any(runs[0]) or all(runs[0]):
        reasons.append("buggy program must pass at least one test and fail at least one")
    if not _small_single_hunk(candidate.correct_code, candidate.buggy_code):
        reasons.append("diff is not one small hunk")
    reasons.extend(validate_hints(candidate))
    candidate.fingerprint = fingerprint(candidate)
    candidate.difficulty_score = rate_difficulty(candidate, sum(not result for result in runs[0]))
    return GateResult(not reasons, reasons, runs)
