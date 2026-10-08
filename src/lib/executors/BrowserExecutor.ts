import { Test } from '../schemas';

export interface TestResult {
  input: string;
  expected: string;
  actual: string;
  passed: boolean;
}

export interface ExecutionResponse {
  results?: TestResult[];
  error?: string;
}

export class BrowserExecutor {
  static async runPython(code: string, tests: Test[]): Promise<ExecutionResponse> {
    return this.runWorker('/workers/py-runner.worker.js', code, tests);
  }

  static async runJavaScript(code: string, tests: Test[]): Promise<ExecutionResponse> {
    return this.runWorker('/workers/js-runner.worker.js', code, tests);
  }
  
  static async runCompiledStub(): Promise<ExecutionResponse> {
    return { error: "Execution for this language is not available in the browser." };
  }

  private static runWorker(workerUrl: string, code: string, tests: Test[]): Promise<ExecutionResponse> {
    return new Promise((resolve) => {
      const worker = new Worker(workerUrl);
      const runId = Math.random().toString(36).substring(7);
      
      const timeoutId = setTimeout(() => {
        worker.terminate();
        resolve({ error: "Execution timed out (infinite loop detected or took > 3s)." });
      }, 3000);

      worker.onmessage = (e) => {
        if (e.data.type === 'READY') return;
        
        if (e.data.runId === runId) {
          clearTimeout(timeoutId);
          worker.terminate();
          if (e.data.error) {
            resolve({ error: e.data.error });
          } else {
            resolve({ results: e.data.results });
          }
        }
      };
      
      worker.onerror = (err) => {
        clearTimeout(timeoutId);
        worker.terminate();
        resolve({ error: err.message });
      };
      
      worker.postMessage({ runId, code, tests });
    });
  }
}
