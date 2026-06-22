import { Source } from "@/lib/api";

const CATEGORY_ICONS: Record<string, string> = {
  "Education": "📚", "Agriculture": "🌾", "Health": "🏥",
  "Women": "👩", "Business": "💼", "Housing": "🏠",
  "Social": "🤝", "Skills": "🛠️", "Banking": "🏦",
  "Rural": "🌱", "Sports": "⚽", "Science": "🔬",
};

function getIcon(category: string): string {
  for (const [key, icon] of Object.entries(CATEGORY_ICONS)) {
    if (category.includes(key)) return icon;
  }
  return "📋";
}

export default function SourceCards({ sources }: { sources: Source[] }) {
  if (!sources.length) return null;
  return (
    <div className="mt-3">
      <p className="text-xs text-slate-500 font-semibold uppercase tracking-wider mb-2">
        📎 Retrieved Schemes ({sources.length})
      </p>
      <div className="flex flex-wrap gap-2">
        {sources.map((s, i) => (
          <div key={i}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-full
                       bg-white/5 border border-white/10 text-slate-400
                       text-xs hover:border-brand-500/40 hover:text-slate-300
                       transition-all cursor-default"
            title={`Relevance: ${(s.score * 100).toFixed(0)}% | ${s.ministry || s.category}`}
          >
            <span>{getIcon(s.category)}</span>
            <span className="max-w-[140px] truncate">{s.name}</span>
            <span className="text-slate-600 text-[10px]">{(s.score * 100).toFixed(0)}%</span>
          </div>
        ))}
      </div>
    </div>
  );
}