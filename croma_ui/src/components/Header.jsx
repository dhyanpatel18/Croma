import React from "react";

export default function Header({ value, onChange, onSearch }) {
  return (
    <header className="bg-black sticky top-0 z-30">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex items-center gap-4">
        <div className="text-2xl font-bold text-emerald-300">croma</div>

        <div className="flex-1">
          <div className="relative">
            <input
              value={value}
              onChange={(e) => onChange(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && onSearch()}
              placeholder="What are you looking for?"
              className="w-full rounded-full py-2 px-4 bg-gray-800 text-gray-100 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-emerald-400"
            />
            <button onClick={onSearch} className="absolute right-1 top-1/2 -translate-y-1/2 bg-emerald-400 text-black px-3 py-1 rounded-full">Search</button>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <div className="text-sm">Mumbai, 400049</div>
          <div className="w-10 h-10 rounded-full bg-gray-800 grid place-items-center">👤</div>
        </div>
      </div>
    </header>
  );
}
