"use client";
import { useState } from "react";

export default function InputBar({ onSend, disabled }: { onSend: (v: string) => void; disabled: boolean }) {
  const [val, setVal] = useState("");

  const handleSend = () => {
    if (val.trim() && !disabled) {
      onSend(val);
      setVal("");
    }
  };

  return (
    <div className="max-w-3xl mx-auto w-full">
      <div className="relative flex items-end bg-white border border-slate-300 rounded-2xl shadow-[0_8px_30px_rgb(0,0,0,0.04)] focus-within:border-blue-500 focus-within:ring-4 focus-within:ring-blue-500/10 transition-all p-2">
        <textarea
          rows={1}
          value={val}
          onChange={(e) => setVal(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault();
              handleSend();
            }
          }}
          placeholder="Message GovtScheme AI..."
          className="flex-1 bg-transparent border-none focus:ring-0 resize-none px-4 py-3 min-h-[48px] max-h-[200px] text-slate-700 placeholder-slate-400 outline-none"
        />
        
        <button 
          onClick={handleSend}
          disabled={!val.trim() || disabled}
          className="w-10 h-10 mb-1 mr-1 flex items-center justify-center bg-blue-600 text-white rounded-xl hover:bg-blue-700 disabled:opacity-40 disabled:hover:bg-blue-600 transition-colors shrink-0"
        >
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><line x1="12" y1="19" x2="12" y2="5"></line><polyline points="5 12 12 5 19 12"></polyline></svg>
        </button>
      </div>
      <div className="text-center mt-3 flex justify-center gap-4 text-[11px] text-slate-400 font-medium">
        <span>Powered by Groq</span>
        <span>•</span>
        <span>Verify data on official portals</span>
      </div>
    </div>
  );
}