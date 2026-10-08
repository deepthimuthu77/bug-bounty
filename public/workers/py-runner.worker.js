importScripts("https://cdn.jsdelivr.net/pyodide/v0.25.0/full/pyodide.js");

let pyodideReadyPromise;

async function initPyodide() {
  self.pyodide = await loadPyodide();
  self.postMessage({ type: 'READY' });
}

pyodideReadyPromise = initPyodide();

self.onmessage = async function(e) {
  await pyodideReadyPromise;
  
  const { code, tests, runId } = e.data;
  
  try {
    const results = [];
    for (const test of tests) {
      self.pyodide.runPython(`
import sys
import io
sys.stdout = io.StringIO()
sys.stderr = io.StringIO()
      `);
      
      let actual = "";
      let error = "";
      try {
        self.pyodide.runPython(code + "\n" + test.input);
        actual = self.pyodide.runPython("sys.stdout.getvalue()");
      } catch (err) {
        error = err.toString();
        actual = error;
      }
      
      results.push({
        input: test.input,
        expected: test.expected,
        actual: actual,
        passed: error === "" && actual.trim() === test.expected.trim()
      });
    }
    
    self.postMessage({ runId, results });
  } catch (err) {
    self.postMessage({ runId, error: err.toString() });
  }
};
