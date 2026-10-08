from __future__ import annotations

import unittest
from unittest.mock import patch

from factory.models import Candidate, Spec
from factory.operators import apply_mutations
from factory.providers import FakeProvider, candidate_from_response
from factory.verification import _small_single_hunk, fingerprint, validate_hints, verify_candidate


def sample(language: str = "python") -> Candidate:
    spec = Spec(language, "loops", "easy", "boundaries")
    return candidate_from_response(spec, FakeProvider().generate(spec), generator="mutation", model="fake-v1")


class FactoryTests(unittest.TestCase):
    def test_fake_python_candidate_passes_gate(self):
        self.assertTrue(verify_candidate(sample()).accepted)

    def test_fake_javascript_candidate_passes_gate(self):
        self.assertTrue(verify_candidate(sample("javascript")).accepted)

    def test_mutation_operator_applies(self):
        changes = apply_mutations("python", "def f(n):\n    for i in range(n + 1):\n        pass\n")
        self.assertTrue(changes)
        self.assertNotEqual(changes[0].code, "def f(n):\n    for i in range(n + 1):\n        pass\n")

    def test_rejects_correct_program_that_fails(self):
        candidate = sample()
        candidate.correct_code = candidate.buggy_code
        result = verify_candidate(candidate)
        self.assertFalse(result.accepted)
        self.assertIn("correct program failed tests", result.reasons)

    def test_rejects_nondeterministic_code(self):
        candidate = sample()
        candidate.correct_code = candidate.correct_code.replace("def sum_to_n(n):", "import time\ndef sum_to_n(n):")
        candidate.buggy_code = candidate.buggy_code.replace("def sum_to_n(n):", "import time\ndef sum_to_n(n):")
        self.assertFalse(verify_candidate(candidate).accepted)

    def test_rejects_unsafe_io(self):
        candidate = sample()
        candidate.correct_code = "def sum_to_n(n):\n    open('bad', 'w')\n    return n\n"
        self.assertIn("unsafe", " ".join(verify_candidate(candidate).reasons))

    def test_hint_validator_rejects_code_fence_and_bad_location(self):
        candidate = sample()
        candidate.hints = ["```python not answer", "Look at line 99 for a clue.", "Follow the final iteration."]
        errors = validate_hints(candidate)
        self.assertTrue(any("code fence" in error for error in errors))
        self.assertTrue(any("location hint" in error for error in errors))

    def test_fingerprint_is_stable_and_different_for_code(self):
        candidate = sample()
        self.assertEqual(fingerprint(candidate), fingerprint(candidate))
        candidate.buggy_code += "# changed\n"
        self.assertNotEqual(fingerprint(candidate), fingerprint(sample()))

    def test_invalid_provider_json_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "missing fields"):
            candidate_from_response(Spec("python", "x", "easy", "x"), {}, generator="mutation", model="fake")

    def test_rejects_multiple_diff_hunks(self):
        candidate = sample()
        candidate.buggy_code = candidate.correct_code.replace("range(n + 1)", "range(n)").replace("return total", "return total\n\n\n\n\n# extra distant edit")
        self.assertFalse(_small_single_hunk(candidate.correct_code, candidate.buggy_code))

    def test_rejects_flaky_results(self):
        candidate = sample()
        real_run = __import__("factory.verification", fromlist=["run_program"]).run_program
        calls = {"buggy": 0}

        def varying(language, program, tests):
            if program == candidate.buggy_code:
                calls["buggy"] += 1
                return [False, True] if calls["buggy"] % 2 else [True, True]
            return [True, True]

        with patch("factory.verification.run_program", side_effect=varying):
            result = verify_candidate(candidate)
        self.assertFalse(result.accepted)
        self.assertIn("buggy results differ across 3 runs", result.reasons)


if __name__ == "__main__":
    unittest.main()
