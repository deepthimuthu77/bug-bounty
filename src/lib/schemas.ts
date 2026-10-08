export type Language = "python" | "javascript" | "cpp" | "go" | "rust" | "java";

export interface Test {
  input: string;
  expected: string;
}

export interface Problem {
  id: string;
  language: Language;
  mode_support: ("classic" | "daily" | "rush" | "vault" | "spot")[];
  title: string;
  difficulty: "easy" | "medium" | "hard";
  category: string;
  concept: string;
  buggy_code: string;
  visible_tests: Test[];
  par_seconds: number;
  generator: "mutation" | "llm";
  fingerprint: string;
}

export interface Attempt {
  id: string;
  user_id: string;
  problem_id: string;
  mode: string;
  started_at: string;
  hints_used: 0 | 1 | 2 | 3;
  failed_runs: number;
  status: "open" | "solved" | "revealed" | "expired";
  verification: "server_verified" | "client_run";
  score: number | null;
}
