from __future__ import annotations

import json
import os
import time
from typing import Any

from .models import Candidate, Spec

PROMPT_VERSION = "bug-factory-v1"

PROGRAM_SCHEMA = {
    "type": "OBJECT",
    "required": ["title", "category", "correct_code", "visible_tests", "hidden_tests", "buggy_code", "bug_line_range", "hints", "explanation", "real_code_example"],
    "properties": {
        "title": {"type": "STRING"}, "category": {"type": "STRING"},
        "correct_code": {"type": "STRING"}, "buggy_code": {"type": "STRING"},
        "visible_tests": {"type": "ARRAY", "items": {"type": "OBJECT", "required": ["input", "expected"], "properties": {"input": {"type": "STRING"}, "expected": {"type": "STRING"}}}},
        "hidden_tests": {"type": "ARRAY", "items": {"type": "OBJECT", "required": ["input", "expected"], "properties": {"input": {"type": "STRING"}, "expected": {"type": "STRING"}}}},
        "bug_line_range": {"type": "ARRAY", "items": {"type": "INTEGER"}},
        "hints": {"type": "ARRAY", "items": {"type": "STRING"}},
        "explanation": {"type": "STRING"}, "real_code_example": {"type": "STRING"},
    },
}
HINT_SCHEMA = {
    "type": "OBJECT", "required": ["hints", "explanation", "real_code_example"],
    "properties": {
        "hints": {"type": "ARRAY", "items": {"type": "STRING"}},
        "explanation": {"type": "STRING"}, "real_code_example": {"type": "STRING"},
    },
}


class FakeProvider:
    """Deterministic, offline provider used only for development and tests."""

    name = "deterministic-fake"
    model = "fake-v1"

    def generate(self, spec: Spec) -> dict[str, Any]:
        if spec.language == "python":
            correct = "def sum_to_n(n):\n    total = 0\n    for i in range(n + 1):\n        total += i\n    return total\n"
            buggy = correct.replace("range(n + 1)", "range(n)")
            visible = [{"input": "print(sum_to_n(0))", "expected": "0\n"}, {"input": "print(sum_to_n(3))", "expected": "6\n"}]
            hidden = [{"input": "print(sum_to_n(5))", "expected": "15\n"}]
        elif spec.language == "javascript":
            correct = "function isStrictlyEqual(a, b) {\n    return a === b;\n}\n"
            buggy = correct.replace("a === b", "a == b")
            visible = [{"input": "console.log(isStrictlyEqual(5, 5))", "expected": "true\n"}, {"input": "console.log(isStrictlyEqual(5, '5'))", "expected": "false\n"}]
            hidden = [{"input": "console.log(isStrictlyEqual(0, false))", "expected": "false\n"}]
        else:
            raise ValueError("Fake provider currently supports Python and JavaScript only")
        line = next(i for i, (a, b) in enumerate(zip(correct.splitlines(), buggy.splitlines()), 1) if a != b)
        return {
            "title": "Off-by-one Loop" if spec.language == "python" else "Loose Equality",
            "category": "off-by-one" if spec.language == "python" else "type-coercion",
            "correct_code": correct, "buggy_code": buggy,
            "visible_tests": visible, "hidden_tests": hidden, "bug_line_range": [line, line],
            "hints": ["Check the boundary of the iteration.", f"Look at line {line}.", "The final value is skipped by the current boundary."],
            "explanation": "The loop stops before including the requested final value." if spec.language == "python" else "Loose equality converts values before comparing them.",
            "real_code_example": "Boundary conditions often cause errors in pagination and array traversal.",
        }


class GeminiProvider:
    """Provider backed by Google's official google-genai SDK."""

    def __init__(self, api_key: str | None = None, model: str | None = None, retries: int = 2):
        self.name = "google-genai"
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise RuntimeError("GEMINI_API_KEY is not set")
        self.model = model or os.getenv("GEMINI_MODEL") or "gemini-2.5-flash"
        self.retries = retries
        try:
            from google import genai
            from google.genai import types
        except ImportError as exc:
            raise RuntimeError("Install factory/requirements.txt to use Gemini") from exc
        self._client = genai.Client(api_key=self.api_key)
        self._types = types

    def _json(self, prompt: str, schema: dict[str, Any] = PROGRAM_SCHEMA) -> dict[str, Any]:
        last_error: Exception | None = None
        for attempt in range(self.retries + 1):
            try:
                response = self._client.models.generate_content(
                    model=self.model,
                    contents=prompt,
                    config=self._types.GenerateContentConfig(response_mime_type="application/json", response_json_schema=schema),
                )
                raw = response.text
                value = json.loads(raw or "")
                if not isinstance(value, dict):
                    raise ValueError("model response must be an object")
                return value
            except Exception as exc:
                last_error = exc
                if attempt == self.retries or not _is_retryable(exc):
                    break
                time.sleep(2 ** attempt)
        raise RuntimeError(f"Gemini generation failed: {last_error}") from last_error

    def generate(self, spec: Spec) -> dict[str, Any]:
        prompt = (
            "Create one short, deterministic educational programming exercise. "
            "Return the canonical correct program, visible and hidden tests, and one small buggy version. "
            "The correct program must pass every test; the buggy version must fail at least one and pass at least one. "
            "Use no network, filesystem, clock, or randomness. Include three progressive hints and an explanation.\n"
            f"Language: {spec.language}; topic: {spec.topic}; difficulty: {spec.difficulty}; concept: {spec.concept}."
        )
        result = self._json(prompt)
        result["generator"] = "llm"
        return result

    def regenerate_hints(self, candidate: Candidate) -> dict[str, Any]:
        prompt = (
            "Write exactly three progressive learner hints, a short explanation, and one real-world use example. "
            "Hint 1 names the concept without giving the answer. Hint 2 points to the exact buggy line range. "
            "Hint 3 describes the behavior that should be checked. Do not include code fences or the fix itself.\n"
            f"Language={candidate.language}; category={candidate.category}; concept={candidate.concept}; "
            f"bug line range={candidate.bug_line_range}; buggy program:\n{candidate.buggy_code}\n"
            f"Known correct program for validation context:\n{candidate.correct_code}"
        )
        return self._json(prompt, HINT_SCHEMA)


def _is_retryable(exc: Exception) -> bool:
    text = str(exc).lower()
    return any(term in text for term in ("429", "quota", "rate", "temporar", "503", "timeout"))


def candidate_from_response(spec: Spec, response: dict[str, Any], *, generator: str, model: str) -> Candidate:
    required = {"title", "category", "correct_code", "buggy_code", "visible_tests", "hidden_tests", "bug_line_range", "hints", "explanation", "real_code_example"}
    if not isinstance(response, dict) or required - response.keys():
        missing = sorted(required - response.keys()) if isinstance(response, dict) else sorted(required)
        raise ValueError(f"invalid provider JSON; missing fields: {', '.join(missing)}")
    for key in ("visible_tests", "hidden_tests"):
        if not isinstance(response[key], list) or any(not isinstance(t, dict) or not isinstance(t.get("input"), str) or not isinstance(t.get("expected"), str) for t in response[key]):
            raise ValueError(f"invalid {key}")
    lines = response["bug_line_range"]
    if not isinstance(lines, list) or len(lines) != 2 or not all(isinstance(n, int) for n in lines):
        raise ValueError("invalid bug_line_range")
    return Candidate(
        language=spec.language, topic=spec.topic, difficulty=spec.difficulty, concept=spec.concept,
        title=str(response["title"]), category=str(response["category"]), correct_code=str(response["correct_code"]),
        buggy_code=str(response["buggy_code"]), visible_tests=response["visible_tests"], hidden_tests=response["hidden_tests"],
        bug_line_range=(lines[0], lines[1]), generator="llm" if generator == "llm" else "mutation", model=model,
        prompt_version=PROMPT_VERSION, hints=list(response["hints"]), explanation=str(response["explanation"]),
        real_code_example=str(response["real_code_example"]),
    )
