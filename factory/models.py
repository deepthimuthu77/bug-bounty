from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Literal

Language = Literal["python", "javascript", "cpp", "go", "rust", "java"]
Difficulty = Literal["easy", "medium", "hard"]


@dataclass(frozen=True)
class Spec:
    language: Language
    topic: str
    difficulty: Difficulty
    concept: str


@dataclass
class Candidate:
    language: Language
    topic: str
    difficulty: Difficulty
    concept: str
    title: str
    category: str
    correct_code: str
    buggy_code: str
    visible_tests: list[dict[str, str]]
    hidden_tests: list[dict[str, str]]
    bug_line_range: tuple[int, int]
    generator: Literal["mutation", "llm"]
    model: str
    prompt_version: str
    hints: list[str] = field(default_factory=list)
    explanation: str = ""
    real_code_example: str = ""
    fingerprint: str = ""
    rejection_reasons: list[str] = field(default_factory=list)
    difficulty_score: int = 0

    def to_dict(self) -> dict[str, Any]:
        value = asdict(self)
        value["bug_line_range"] = list(self.bug_line_range)
        return value


@dataclass
class Audit:
    generated: int = 0
    accepted: int = 0
    rejected: dict[str, int] = field(default_factory=dict)
    entries: list[dict[str, Any]] = field(default_factory=list)

    def reject(self, reason: str, candidate: Candidate) -> None:
        self.rejected[reason] = self.rejected.get(reason, 0) + 1
        self.entries.append({"status": "rejected", "reason": reason, "fingerprint": candidate.fingerprint, "generator": candidate.generator, "model": candidate.model})

    def accept(self, candidate: Candidate) -> None:
        self.accepted += 1
        self.entries.append({"status": "accepted", "fingerprint": candidate.fingerprint, "generator": candidate.generator, "model": candidate.model})
