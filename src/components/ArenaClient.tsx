"use client";

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import CodeMirror from '@uiw/react-codemirror';
import { vscodeDark } from '@uiw/codemirror-theme-vscode';
import { python } from '@codemirror/lang-python';
import { javascript } from '@codemirror/lang-javascript';
import { cpp } from '@codemirror/lang-cpp';
import { java } from '@codemirror/lang-java';
import { rust } from '@codemirror/lang-rust';
import { go } from '@codemirror/lang-go';
import { BrowserExecutor, TestResult } from '@/lib/executors/BrowserExecutor';
import { seededProblems } from '@/lib/seededProblems';
import { Problem } from '@/lib/schemas';

export default function ArenaClient({ lang }: { lang: string }) {
  const router = useRouter();
  const langStr = lang.toLowerCase();
  
  const found = seededProblems.find(p => p.language.toLowerCase() === langStr) || null;
  const [problem] = useState<Problem | null>(found);
  const [code, setCode] = useState(found?.buggy_code || "");
  const [results, setResults] = useState<TestResult[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isRunning, setIsRunning] = useState(false);
  
  const handleRun = async () => {
    if (!problem) return;
    setIsRunning(true);
    setError(null);
    setResults(null);
    
    let res;
    if (langStr === 'python') {
      res = await BrowserExecutor.runPython(code, problem.visible_tests);
    } else if (langStr === 'javascript') {
      res = await BrowserExecutor.runJavaScript(code, problem.visible_tests);
    } else {
      res = await BrowserExecutor.runCompiledStub();
    }
    
    if (res.error) {
      setError(res.error);
    } else if (res.results) {
      setResults(res.results);
    }
    
    setIsRunning(false);
  };

  const getLanguageExtension = () => {
    switch (langStr) {
      case 'python': return python();
      case 'javascript': return javascript();
      case 'cpp': return cpp();
      case 'java': return java();
      case 'rust': return rust();
      case 'go': return go();
      default: return [];
    }
  };

  if (!problem) {
    return (
      <div className="min-h-screen bg-[#09090b] text-gray-300 font-mono flex flex-col items-center justify-center p-4">
        <h2 className="text-2xl text-white mb-4">Runtime initialization failed.</h2>
        <p className="text-gray-500 mb-8">No seeded problem available for {langStr}.</p>
        <button 
          onClick={() => router.push('/')}
          className="border border-gray-700 px-4 py-2 hover:bg-gray-800 transition"
        >
          &lt; Return to Hub
        </button>
      </div>
    );
  }

  const allPassed = results?.every(r => r.passed);

  return (
    <div className="min-h-screen bg-[#09090b] text-gray-300 font-mono flex flex-col">
      <header className="border-b border-gray-800 p-4 flex justify-between items-center bg-[#050505]">
        <div className="flex items-center gap-4">
          <button onClick={() => router.push('/')} className="text-gray-500 hover:text-white transition uppercase text-sm tracking-widest">
            &lt; SYS_HUB
          </button>
          <span className="text-white font-bold tracking-widest uppercase text-sm">Arena // {langStr}</span>
        </div>
        <div className="text-xs text-gray-500 font-mono">
          SEED: {problem.fingerprint}
        </div>
      </header>
      
      <div className="flex-1 grid grid-cols-1 lg:grid-cols-2 gap-px bg-gray-800">
        
        {/* Left Panel: Context & Results */}
        <div className="bg-[#0a0a0c] flex flex-col h-[calc(100vh-65px)] overflow-y-auto">
          <div className="p-6 border-b border-gray-800">
            <div className="flex justify-between items-start mb-4">
              <h1 className="text-2xl text-white font-bold tracking-tight">{problem.title}</h1>
              <span className="px-2 py-1 bg-gray-800 text-xs rounded border border-gray-700 uppercase">
                {problem.difficulty}
              </span>
            </div>
            
            <div className="text-sm text-gray-400 mb-6">
              Category: <span className="text-emerald-400">{problem.category}</span>
            </div>
            
            <p className="text-gray-300 text-sm leading-relaxed">
              Find the bug in the provided code. The code currently fails one or more test cases. 
              Modify it so it passes all tests. Execution is limited to {problem.par_seconds}s (server time).
            </p>
          </div>
          
          <div className="p-6 flex-1 flex flex-col">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-gray-100 uppercase tracking-widest text-xs font-bold">Execution Output</h2>
              {allPassed && (
                <span className="text-emerald-400 text-xs font-bold animate-pulse">✓ ALL TESTS PASSED</span>
              )}
            </div>
            
            <div className="bg-[#050505] border border-gray-800 flex-1 p-4 rounded-sm overflow-y-auto font-mono text-xs">
              {error && (
                <div className="text-red-400 whitespace-pre-wrap">{error}</div>
              )}
              
              {!error && !results && !isRunning && (
                <div className="text-gray-600 italic">Awaiting execution...</div>
              )}
              
              {isRunning && (
                <div className="text-emerald-500 animate-pulse">Running test suite...</div>
              )}
              
              {results && (
                <div className="space-y-4">
                  {results.map((r, i) => (
                    <div key={i} className={`p-3 border-l-2 ${r.passed ? 'border-emerald-500 bg-emerald-900/10' : 'border-red-500 bg-red-900/10'}`}>
                      <div className="flex justify-between mb-2">
                        <span className="text-gray-400">Test {i + 1}</span>
                        <span className={r.passed ? 'text-emerald-400 font-bold' : 'text-red-400 font-bold'}>
                          {r.passed ? 'PASS' : 'FAIL'}
                        </span>
                      </div>
                      <div className="text-gray-500">Input:</div>
                      <div className="text-gray-300 mb-2">{r.input}</div>
                      
                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <div className="text-gray-500">Expected:</div>
                          <div className="text-gray-300 whitespace-pre-wrap">{r.expected}</div>
                        </div>
                        <div>
                          <div className="text-gray-500">Actual:</div>
                          <div className="text-gray-300 whitespace-pre-wrap">{r.actual}</div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
        
        {/* Right Panel: Editor */}
        <div className="bg-[#1e1e1e] flex flex-col h-[calc(100vh-65px)] relative">
          <div className="flex justify-between items-center bg-[#252526] px-4 py-2 border-b border-[#333]">
            <span className="text-xs text-gray-400">{problem.fingerprint}{langStr === 'python' ? '.py' : langStr === 'javascript' ? '.js' : ''}</span>
            <button 
              onClick={handleRun}
              disabled={isRunning}
              className={`px-4 py-1.5 text-xs font-bold uppercase tracking-widest transition ${
                isRunning 
                  ? 'bg-gray-700 text-gray-500 cursor-not-allowed' 
                  : 'bg-emerald-600 text-white hover:bg-emerald-500'
              }`}
            >
              {isRunning ? 'Executing...' : 'Run Tests'}
            </button>
          </div>
          
          <div className="flex-1 overflow-y-auto">
            <CodeMirror
              value={code}
              height="100%"
              theme={vscodeDark}
              extensions={[getLanguageExtension()]}
              onChange={(value) => setCode(value)}
              className="h-full text-sm font-mono"
            />
          </div>
        </div>
        
      </div>
    </div>
  );
}
