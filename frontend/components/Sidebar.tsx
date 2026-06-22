"use client";

export default function Sidebar({ sessions, activeId, onSelect, onNew, isOpen, toggle }: any) {
  if (!isOpen) return null;

  return (
    <aside className="w-[280px] flex-shrink-0 bg-[#1e1f22] h-full flex flex-col transition-all duration-300">
      <div className="p-4 mt-2">
        <button 
          onClick={onNew}
          className="flex items-center gap-3 bg-[#131314] hover:bg-[#282a2d] text-gray-300 px-4 py-3 rounded-full w-[150px] transition-colors"
        >
          <span className="text-xl leading-none">+</span>
          <span className="font-medium text-sm">New chat</span>
        </button>
      </div>

      <div className="flex-1 overflow-y-auto px-3 mt-6 space-y-1">
        <p className="text-xs font-semibold text-gray-500 px-3 mb-2">Recent</p>
        {sessions.map((s: any) => (
          <button
            key={s.id}
            onClick={() => onSelect(s.id)}
            className={`w-full text-left px-3 py-2.5 rounded-full text-sm truncate transition-colors
              ${s.id === activeId ? "bg-[#282a2d] text-gray-200" : "text-gray-400 hover:bg-[#282a2d] hover:text-gray-200"}`}
          >
            💬 {s.preview}
          </button>
        ))}
      </div>
    </aside>
  );
} 