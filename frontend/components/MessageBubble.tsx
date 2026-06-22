"use client";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

export default function MessageBubble({ role, content }: { role: string; content: string }) {
  const isUser = role === "user";

  if (isUser) {
    return (
      <div className="flex w-full justify-end animate-in fade-in slide-in-from-bottom-2 duration-300">
        <div className="bg-slate-800 text-white px-5 py-3.5 rounded-2xl rounded-tr-sm max-w-[75%] text-[15px] leading-relaxed shadow-sm">
          {content}
        </div>
      </div>
    );
  }

  return (
    <div className="flex w-full justify-start animate-in fade-in slide-in-from-bottom-2 duration-300">
      <div className="flex gap-4 w-full max-w-[85%]">
        {/* AI Avatar */}
        <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-blue-500 to-blue-700 flex items-center justify-center shrink-0 shadow-sm mt-1">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect x="3" y="11" width="18" height="10" rx="2"/><circle cx="12" cy="5" r="2"/><path d="M12 7v4"/><line x1="8" y1="16" x2="8.01" y2="16"/><line x1="16" y1="16" x2="16.01" y2="16"/></svg>
        </div>
        
        {/* AI Content */}
        <div className="bg-white border border-slate-200 px-6 py-4 rounded-2xl rounded-tl-sm shadow-sm w-full">
          <div className="prose prose-slate max-w-none text-[15px] leading-relaxed
            prose-p:mb-4 prose-p:last:mb-0 
            prose-headings:text-slate-800 prose-headings:font-bold prose-headings:mb-3 prose-headings:mt-4
            prose-strong:text-slate-900 prose-strong:font-semibold
            prose-ul:list-disc prose-ul:ml-4 prose-ul:mb-4 prose-li:mb-1 prose-li:marker:text-blue-500
            prose-a:text-blue-600 prose-a:no-underline hover:prose-a:underline">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>
              {content}
            </ReactMarkdown>
          </div>
        </div>
      </div>
    </div>
  );
}