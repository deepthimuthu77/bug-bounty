import { Problem } from './schemas';
import factoryProblems from '../../bank/public.json';

export const seededProblems: Problem[] = [
  {
    id: "seed-py-1",
    language: "python",
    mode_support: ["classic"],
    title: "Off-by-one Loop",
    difficulty: "easy",
    category: "off-by-one",
    concept: "loops",
    generator: "mutation",
    fingerprint: "seeded-py-1",
    par_seconds: 60,
    buggy_code: `def sum_to_n(n):\n    total = 0\n    for i in range(n):\n        total += i\n    return total\n`,
    visible_tests: [
      { input: "print(sum_to_n(3))", expected: "6\n" },
      { input: "print(sum_to_n(5))", expected: "15\n" }
    ]
  },
  {
    id: "seed-js-1",
    language: "javascript",
    mode_support: ["classic"],
    title: "Loose Equality",
    difficulty: "easy",
    category: "type-coercion",
    concept: "equality",
    generator: "mutation",
    fingerprint: "seeded-js-1",
    par_seconds: 60,
    buggy_code: `function isStrictlyEqual(a, b) {\n    return a == b;\n}\n`,
    visible_tests: [
      { input: "console.log(isStrictlyEqual(5, 5))", expected: "true\n" },
      { input: "console.log(isStrictlyEqual(5, '5'))", expected: "false\n" }
    ]
  },
  ...(factoryProblems as Problem[]),
];
