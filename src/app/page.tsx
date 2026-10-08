"use client";

import React, { useState } from 'react';

export default function Home() {
  const [loading, setLoading] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleLanguageSelect = (lang: string) => {
    setError(null);
    setLoading(lang);
    
    // Simulate API call for Stage 0 mockup
    setTimeout(() => {
      if (lang === 'Java') {
        setError('Failed to load problems for Java. Please try another language.');
        setLoading(null);
      } else {
        // In later stages, this would route to the game mode
        setError(`Environment for ${lang} is currently in preview mode.`);
        setLoading(null);
      }
    }, 1500);
  };

  const languages = ['Python', 'JavaScript', 'C++', 'Go', 'Rust', 'Java'];

  return (
    <main className="min-h-screen bg-gray-950 text-gray-50 flex flex-col items-center py-20 px-4">
      <div className="max-w-4xl w-full text-center space-y-6">
        <h1 className="text-6xl md:text-8xl font-black tracking-tighter text-transparent bg-clip-text bg-gradient-to-br from-indigo-400 via-purple-400 to-pink-400 drop-shadow-sm pb-2">
          Bug Hunt Arena
        </h1>
        <p className="text-2xl md:text-4xl text-gray-400 font-light tracking-wide">
          Break it. <span className="font-semibold text-white">Find it.</span> Fix it.
        </p>
        
        <div className="mt-20 bg-gray-900/50 backdrop-blur-md border border-gray-800 rounded-3xl p-8 shadow-2xl relative overflow-hidden">
          {/* Decorative glow */}
          <div className="absolute top-0 left-1/2 -translate-x-1/2 w-3/4 h-32 bg-indigo-500/20 blur-[100px] rounded-full pointer-events-none" />
          
          <h2 className="text-2xl font-bold mb-8 text-gray-200">Select Your Language</h2>
          
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4 relative z-10">
            {languages.map((lang) => (
              <button 
                key={lang}
                onClick={() => handleLanguageSelect(lang)}
                disabled={loading !== null}
                className={`py-5 px-6 rounded-2xl border transition-all duration-300 font-semibold text-xl flex items-center justify-center
                  ${loading === lang 
                    ? 'bg-indigo-600 border-indigo-400 text-white animate-pulse' 
                    : 'bg-gray-800/80 border-gray-700 hover:bg-gray-700 hover:border-gray-500 text-gray-300 hover:text-white hover:-translate-y-1 hover:shadow-[0_8px_30px_rgb(0,0,0,0.12)]'
                  }
                  ${loading !== null && loading !== lang ? 'opacity-50 cursor-not-allowed' : ''}
                `}
              >
                {loading === lang ? (
                  <span className="flex items-center gap-2">
                    <svg className="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Loading...
                  </span>
                ) : (
                  lang
                )}
              </button>
            ))}
          </div>
          
          <div className="mt-8 min-h-[60px] flex items-center justify-center">
            {error ? (
              <div className="text-red-400 bg-red-950/30 px-6 py-3 rounded-xl border border-red-900/50 text-sm font-medium">
                {error}
              </div>
            ) : (
              <div className="text-gray-500 text-sm font-medium">
                Select a language to fetch a bug from the arena.
              </div>
            )}
          </div>
        </div>
      </div>
    </main>
  );
}
