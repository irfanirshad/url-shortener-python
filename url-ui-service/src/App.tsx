import React, { useState } from 'react';
import { URLForm } from './components/URLForm';
import { Dashboard } from './components/Dashboard';
import { Link } from 'lucide-react';

function App() {
  const [isCustomMode, setIsCustomMode] = useState(false);

  return (
    <div className="min-h-screen bg-custom-black text-white relative overflow-hidden">
      {/* Gradient Bars */}
      <div
        className={`h-1 w-full transition-all duration-500 ${
          isCustomMode
            ? 'bg-gradient-to-r from-custom-blue via-custom-dark-grey to-custom-blue' // Yellow gradient for active mode
            : 'bg-gradient-to-r from-custom-light-gray via-custom-dark-gray to-custom-dark-gray' // Dark gray gradient
        }`}
      />

      <main className="container mx-auto px-6 py-12 relative z-10">
        <div className="glass-card rounded-2xl p-8 mb-12 bg-opacity-60 backdrop-blur-lg">
          <div className="text-center space-y-6 mb-12">
            {/* Header */}
            <div className="inline-flex items-center justify-center gap-3 mb-6">
              <Link
                size={40}
                className={`${
                  isCustomMode ? 'text-custom-blue' : 'text-custom-grey'
                } transition-colors duration-500`}
              />
              <h1 className="text-5xl font-bold text-custom-white glow-text">
          URL Shortener
        </h1>
            </div>

            {/* Custom Mode Toggle */}
            <label className="inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={isCustomMode}
                onChange={(e) => setIsCustomMode(e.target.checked)}
                className="sr-only peer"
              />
              <div
                className={`relative w-14 h-7 rounded-full transition-all duration-300 ${
                  isCustomMode ? 'bg-custom-blue' : 'bg-custom-grey'
                } peer-focus:ring-2 peer-focus:ring-white peer-focus:ring-opacity-20
                after:content-[''] after:absolute after:top-[2px] after:left-[2px]
                after:bg-white after:rounded-full after:h-6 after:w-6 after:transition-all
                peer-checked:after:translate-x-7`}
              />
              <span className="ms-3 text-sm font-medium text-custom-light-gray">
                Custom URL Mode
              </span>
            </label>
          </div>

          {/* URL Form */}
          <URLForm isCustomMode={isCustomMode} />
        </div>

        {/* Dashboard */}
        <Dashboard />
      </main>

      {/* Bottom Gradient Bar */}
      <div
        className={`h-1 w-full transition-all duration-500 fixed bottom-0 ${
          isCustomMode
            ? 'bg-gradient-to-r from-custom-blue via-custom-blue to-custom-blue'
            : 'bg-gradient-to-r from-custom-dark-gray via-custom-dark-gray to-custom-dark-gray'
        }`}
      />
    </div>
  );
}

export default App;
