"use client";

import React, { useState, useEffect } from 'react';

const GridBackground = () => (
  <svg className="absolute inset-0 w-full h-full opacity-[0.04] pointer-events-none" xmlns="http://www.w3.org/2000/svg">
    <defs>
      <pattern id="grid-pattern" width="32" height="32" patternUnits="userSpaceOnUse">
        <path d="M 32 0 L 0 0 0 32" fill="none" stroke="white" strokeWidth="1"/>
      </pattern>
    </defs>
    <rect width="100%" height="100%" fill="url(#grid-pattern)" />
  </svg>
);

export default function Home() {
  const [loading, setLoading] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [terminalText, setTerminalText] = useState("");
  
  useEffect(() => {
    const text = "> Break it. Find it. Fix it.";
    let i = 0;
    const timer = setInterval(() => {
      setTerminalText(text.slice(0, i + 1));
      i++;
      if (i === text.length) clearInterval(timer);
    }, 50);
    return () => clearInterval(timer);
  }, []);

  const handleLanguageSelect = (lang: string) => {
    setError(null);
    setLoading(lang);
    
    setTimeout(() => {
      if (lang === 'Java') {
        setError(`Exception in thread "main" java.lang.RuntimeException: Module offline`);
        setLoading(null);
      } else {
        setError(`[WARN] Arena for ${lang} is locked. Requires clearance.`);
        setLoading(null);
      }
    }, 1200);
  };

  const languages = [
    { id: 'python', name: 'Python', ext: '.py', color: 'hover:border-yellow-400', active: 'border-yellow-400 bg-yellow-400/10 text-yellow-400' },
    { id: 'javascript', name: 'JavaScript', ext: '.js', color: 'hover:border-yellow-300', active: 'border-yellow-300 bg-yellow-300/10 text-yellow-300' },
    { id: 'cpp', name: 'C++', ext: '.cpp', color: 'hover:border-blue-400', active: 'border-blue-400 bg-blue-400/10 text-blue-400' },
    { id: 'go', name: 'Go', ext: '.go', color: 'hover:border-cyan-400', active: 'border-cyan-400 bg-cyan-400/10 text-cyan-400' },
    { id: 'rust', name: 'Rust', ext: '.rs', color: 'hover:border-orange-400', active: 'border-orange-400 bg-orange-400/10 text-orange-400' },
    { id: 'java', name: 'Java', ext: '.java', color: 'hover:border-red-400', active: 'border-red-400 bg-red-400/10 text-red-400' }
  ];

  return (
    <main className="min-h-screen bg-[#09090b] text-gray-300 font-mono relative overflow-hidden selection:bg-emerald-500/30">
      <GridBackground />
      
      <div className="max-w-6xl mx-auto px-6 py-12 md:py-24 relative z-10 flex flex-col min-h-screen">
        {/* Header */}
        <header className="w-full flex flex-col md:flex-row items-start md:items-end justify-between border-b border-gray-800 pb-8 mb-12">
          <div>
            <h1 className="text-4xl md:text-5xl font-bold text-white tracking-tighter mb-4 flex items-center gap-4">
              <span className="w-4 h-4 bg-emerald-500 block animate-pulse"></span>
              BUG_HUNT_ARENA
            </h1>
            <p className="text-emerald-400 h-6 text-sm md:text-base">
              {terminalText}<span className="animate-pulse">_</span>
            </p>
          </div>
          <div className="hidden md:flex flex-col items-end text-xs text-gray-500 uppercase tracking-widest space-y-1 mt-6 md:mt-0">
            <span>Server: local_dev_01</span>
            <span>Status: Awaiting Input</span>
          </div>
        </header>
        
        <div className="w-full grid grid-cols-1 lg:grid-cols-12 gap-8 lg:gap-12 flex-1">
          {/* Sidebar */}
          <aside className="lg:col-span-4 flex flex-col gap-6">
            <div className="bg-[#0f0f11] border border-gray-800 p-6">
              <h2 className="text-gray-100 uppercase tracking-widest text-xs font-bold mb-4 border-b border-gray-800 pb-3 flex justify-between">
                <span>Mission Brief</span>
                <span className="text-emerald-500">v1.0.0</span>
              </h2>
              <p className="text-sm text-gray-400 leading-relaxed mb-6">
                The generator creates verified broken code. Your objective is to hunt down the bugs, patch them, and pass the deterministic execution gates.
              </p>
              
              <div className="space-y-3 font-mono text-xs">
                <div className="flex justify-between border-b border-gray-800/50 pb-2">
                  <span className="text-gray-500">ACTIVE HUNTERS</span>
                  <span className="text-white">0,024</span>
                </div>
                <div className="flex justify-between border-b border-gray-800/50 pb-2">
                  <span className="text-gray-500">BUGS SQUASHED</span>
                  <span className="text-white">8,201</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500">SYSTEM HEALTH</span>
                  <span className="text-emerald-500">OPTIMAL</span>
                </div>
              </div>
            </div>
            
            {/* Terminal Console */}
            <div className="bg-[#050505] border border-gray-800 flex flex-col h-48 lg:flex-1 min-h-[12rem]">
              <div className="bg-[#111113] px-4 py-2 border-b border-gray-800 flex items-center gap-2">
                <div className="flex gap-1.5">
                  <div className="w-2 h-2 bg-red-500/50"></div>
                  <div className="w-2 h-2 bg-yellow-500/50"></div>
                  <div className="w-2 h-2 bg-green-500/50"></div>
                </div>
                <span className="text-[10px] text-gray-500 ml-3 uppercase tracking-widest">Sys_Console</span>
              </div>
              <div className="p-4 text-xs text-gray-400 font-mono flex-1 overflow-y-auto leading-relaxed">
                <div>[SYSTEM] Boot sequence complete.</div>
                <div>[SYSTEM] Bug factory loaded.</div>
                {error ? (
                  <div className="text-red-400 mt-2">{error}</div>
                ) : loading ? (
                  <div className="text-emerald-500 mt-2">
                    [INFO] Provisioning container for {loading}...<span className="animate-pulse">_</span>
                  </div>
                ) : (
                  <div className="text-gray-500 mt-2 animate-pulse">[WAIT] Please select a target runtime...</div>
                )}
              </div>
            </div>
          </aside>
          
          {/* Main Content */}
          <section className="lg:col-span-8 flex flex-col">
            <h3 className="text-gray-400 text-sm uppercase tracking-widest mb-6 flex items-center gap-3">
              <span className="w-1.5 h-1.5 bg-gray-600"></span>
              Initialize Target Runtime
            </h3>
            
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {languages.map((lang) => {
                const isLoading = loading === lang.name;
                const isOtherLoading = loading !== null && !isLoading;
                
                return (
                  <button 
                    key={lang.id}
                    onClick={() => handleLanguageSelect(lang.name)}
                    disabled={loading !== null}
                    className={`group relative p-6 text-left border bg-[#0f0f11] transition-all duration-300
                      ${isLoading ? lang.active : 'border-gray-800 text-gray-300'}
                      ${!isLoading && !isOtherLoading ? lang.color : ''}
                      ${isOtherLoading ? 'opacity-30 cursor-not-allowed' : ''}
                      overflow-hidden
                    `}
                  >
                    {/* Background Extension text */}
                    <span className="absolute -right-2 -bottom-2 text-6xl font-black text-gray-900 group-hover:text-gray-800/80 transition-colors pointer-events-none select-none">
                      {lang.ext}
                    </span>
                    
                    <div className="relative z-10">
                      <div className="flex justify-between items-start mb-4">
                        <h4 className={`text-xl font-bold tracking-tight transition-colors
                          ${isLoading ? '' : 'group-hover:text-white'}
                        `}>
                          {lang.name}
                        </h4>
                        
                        {/* Status box */}
                        <div className={`w-3 h-3 border transition-all duration-300
                          ${isLoading ? 'border-current bg-current animate-ping' : 'border-gray-700'}
                        `}></div>
                      </div>
                      
                      <div className="text-xs uppercase tracking-widest opacity-60">
                        {isLoading ? 'Booting...' : 'Select'}
                      </div>
                    </div>
                  </button>
                );
              })}
            </div>
          </section>
        </div>
      </div>
    </main>
  );
}
