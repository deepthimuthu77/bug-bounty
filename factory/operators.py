from __future__ import annotations

from dataclasses import dataclass
from typing import Callable


@dataclass(frozen=True)
class Mutation:
    code: str
    category: str
    description: str
    line_range: tuple[int, int]


def _replace_once(code: str, old: str, new: str, category: str, description: str) -> Mutation | None:
    if code.count(old) != 1:
        return None
    updated = code.replace(old, new, 1)
    line = code[:code.index(old)].count("\n") + 1
    return Mutation(updated, category, description, (line, line))


def mutate_python(code: str) -> list[Mutation]:
    result = []
    for args in (("range(n + 1)", "range(n)", "off-by-one", "shorten inclusive loop"),
                 ("range(n)", "range(n - 1)", "off-by-one", "skip final iteration"),
                 ("<=", "<", "boundary", "exclude boundary"),
                 (" + ", " - ", "operator", "swap addition for subtraction")):
        mutation = _replace_once(code, *args)
        if mutation:
            result.append(mutation)
    return result


def mutate_javascript(code: str) -> list[Mutation]:
    result = []
    for args in (("===", "==", "type-coercion", "use coercing equality"),
                 ("!==", "!=", "type-coercion", "use coercing inequality"),
                 ("<=", "<", "boundary", "exclude boundary"),
                 (" + ", " - ", "operator", "swap addition for subtraction")):
        mutation = _replace_once(code, *args)
        if mutation:
            result.append(mutation)
    return result


def apply_mutations(language: str, correct_code: str) -> list[Mutation]:
    operators: dict[str, Callable[[str], list[Mutation]]] = {"python": mutate_python, "javascript": mutate_javascript}
    if language not in operators:
        return []
    return operators[language](correct_code)
