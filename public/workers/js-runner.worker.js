self.onmessage = function(e) {
  const { code, tests, runId } = e.data;
  
  try {
    const results = tests.map((test) => {
      let output = "";
      const originalLog = console.log;
      console.log = (...args) => {
        output += args.join(" ") + "\n";
      };
      
      try {
        const execute = new Function(`
          ${code}
          ${test.input}
        `);
        execute();
        
        console.log = originalLog;
        return { 
          input: test.input, 
          expected: test.expected, 
          actual: output, 
          passed: output.trim() === test.expected.trim() 
        };
      } catch (err) {
        console.log = originalLog;
        return { 
          input: test.input, 
          expected: test.expected, 
          actual: err.toString() + "\n", 
          passed: false 
        };
      }
    });
    
    self.postMessage({ runId, results });
  } catch (err) {
    self.postMessage({ runId, error: err.toString() });
  }
};
