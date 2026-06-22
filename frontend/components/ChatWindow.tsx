"use client";
import { useState, useRef, useEffect } from "react";
import MessageBubble from "./MessageBubble";
import InputBar from "./InputBar";
import { sendMessage, newSession, getUserSessions, deleteSession, type Session, type Source } from "@/lib/api";
import { getUser, signOut } from "@/lib/auth";

interface Message {
  role: "user" | "assistant";
  content: string;
  sources?: Source[];
}

interface LocalSession {
  id: string;
  title: string;
  messages: Message[];
  updated_at: string;
}

export default function ChatWindow() {
  const [sessions, setSessions] = useState<LocalSession[]>([]);
  const [activeId, setActiveId] = useState<string>("");
  const [loading, setLoading] = useState(false);
  const [loadingHistory, setLoadingHistory] = useState(true);
  const bottomRef = useRef<HTMLDivElement>(null);
  const user = getUser();

  const activeSession = sessions.find(s => s.id === activeId);
  const messages = activeSession?.messages || [];

 useEffect(() => {
  async function loadSessions() {
    try {
      const remoteSessions = await getUserSessions();
      if (remoteSessions.length > 0) {
        const mapped: LocalSession[] = remoteSessions.map(s => ({
          id: s.session_id,
          title: s.title,
          messages: [],
          updated_at: s.updated_at
        }));
        setSessions(mapped);
        setActiveId(mapped[0].id);
      } else {
        await createNewSession();
      }
    } catch (e) {
      console.error("Could not load sessions:", e);
      // Backend might be offline — start fresh local session
      const id = crypto.randomUUID();
      const welcome: Message = {
        role: "assistant",
        content: "Hello! I am **Sarkari Yojana AI**. Ask me about any Indian Government scheme."
      };
      setSessions([{ id, title: "New Chat", messages: [welcome], updated_at: new Date().toISOString() }]);
      setActiveId(id);
    } finally {
      setLoadingHistory(false);
    }
  }
  loadSessions();
}, []);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const createNewSession = async () => {
    const welcome: Message = {
      role: "assistant",
      content: `Hello${user.full_name ? ` ${user.full_name}` : ''}! 👋 I am **Sarkari Yojana AI**. Ask me about any Indian Government scheme, eligibility criteria, or benefits.`
    };
    try {
      const sessionId = await newSession();
      const newS: LocalSession = {
        id: sessionId,
        title: "New Chat",
        messages: [welcome],
        updated_at: new Date().toISOString()
      };
      setSessions(prev => [newS, ...prev]);
      setActiveId(sessionId);
    } catch (e) {
      console.error("Failed to create session", e);
    }
  };

  const handleSelectSession = async (sessionId: string) => {
    setActiveId(sessionId);
    // Load messages if not already loaded
    const session = sessions.find(s => s.id === sessionId);
    if (session && session.messages.length === 0) {
      try {
        const { getSessionMessages } = await import("@/lib/api");
        const msgs = await getSessionMessages(sessionId);
        setSessions(prev => prev.map(s =>
          s.id === sessionId ? { ...s, messages: msgs } : s
        ));
      } catch (e) {
        console.error("Failed to load messages", e);
      }
    }
  };

  const handleDeleteSession = async (e: React.MouseEvent, sessionId: string) => {
    e.stopPropagation();
    await deleteSession(sessionId);
    setSessions(prev => prev.filter(s => s.id !== sessionId));
    if (activeId === sessionId) {
      const remaining = sessions.filter(s => s.id !== sessionId);
      if (remaining.length > 0) {
        setActiveId(remaining[0].id);
      } else {
        await createNewSession();
      }
    }
  };

  const handleSend = async (text: string) => {
    if (loading || !activeId) return;

    // Add user message immediately
    const userMsg: Message = { role: "user", content: text };
    setSessions(prev => prev.map(s =>
      s.id === activeId
        ? { ...s, messages: [...s.messages, userMsg], title: s.title === "New Chat" ? text.slice(0, 30) : s.title }
        : s
    ));
    setLoading(true);

    // Prepare assistant message placeholder
    let assistantContent = "";
    const assistantMsg: Message = { role: "assistant", content: "" };
    setSessions(prev => prev.map(s =>
      s.id === activeId ? { ...s, messages: [...s.messages, assistantMsg] } : s
    ));

    try {
      await sendMessage(
        text,
        activeId,
        // onChunk — stream text token by token
        (delta) => {
          assistantContent += delta;
          setSessions(prev => prev.map(s => {
            if (s.id !== activeId) return s;
            const msgs = [...s.messages];
            msgs[msgs.length - 1] = { role: "assistant", content: assistantContent };
            return { ...s, messages: msgs };
          }));
        },
        // onSources
        (sources) => {
          setSessions(prev => prev.map(s => {
            if (s.id !== activeId) return s;
            const msgs = [...s.messages];
            msgs[msgs.length - 1] = { ...msgs[msgs.length - 1], sources };
            return { ...s, messages: msgs };
          }));
        },
        // onDone
        () => setLoading(false),
        // onError
        (err) => {
          setSessions(prev => prev.map(s => {
            if (s.id !== activeId) return s;
            const msgs = [...s.messages];
            msgs[msgs.length - 1] = { role: "assistant", content: `⚠️ ${err}` };
            return { ...s, messages: msgs };
          }));
          setLoading(false);
        }
      );
    } catch (e) {
      console.error(e);
      setLoading(false);
    }
  };

  return (
    <div className="flex h-screen w-full font-sans bg-white overflow-hidden">

      {/* LEFT SIDEBAR */}
      <aside className="w-64 flex-shrink-0 bg-[#0f172a] text-slate-300 flex flex-col border-r border-slate-800">

        {/* Brand */}
        <div className="p-5 flex items-center gap-3 border-b border-slate-800">
          <div className="w-8 h-8 rounded bg-orange-500 flex items-center justify-center text-white font-bold text-sm">
            स
          </div>
          <div>
            <h1 className="text-sm font-bold text-white tracking-wide">Sarkari Yojana AI</h1>
            <p className="text-[10px] text-slate-400 font-medium">GOVT SCHEME ASSISTANT</p>
          </div>
        </div>

        {/* User info */}
        <div className="px-4 py-3 border-b border-slate-800 flex items-center justify-between">
          <div>
            <p className="text-xs font-medium text-white truncate">{user.full_name || user.email}</p>
            <p className="text-[10px] text-slate-500 truncate">{user.email}</p>
          </div>
          <button
            onClick={signOut}
            className="text-slate-500 hover:text-red-400 transition-colors text-xs ml-2"
            title="Sign out"
          >
            ⏻
          </button>
        </div>

        {/* New Chat Button */}
        <div className="p-4">
          <button
            onClick={createNewSession}
            className="w-full flex items-center justify-center gap-2 bg-orange-500 hover:bg-orange-600 text-white py-2.5 rounded-lg text-sm font-medium transition-colors"
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/>
            </svg>
            New Chat
          </button>
        </div>

        {/* Sessions list */}
        <div className="flex-1 overflow-y-auto px-3 py-2 space-y-1">
          <p className="text-xs font-semibold text-slate-500 px-2 mb-3 uppercase tracking-wider">Recent Chats</p>
          {loadingHistory ? (
            <p className="text-xs text-slate-600 px-2">Loading...</p>
          ) : (
            sessions.map(s => (
              <button
                key={s.id}
                onClick={() => handleSelectSession(s.id)}
                className={`w-full text-left px-3 py-3 rounded-lg text-sm transition-colors flex items-center justify-between gap-2
                  ${s.id === activeId ? "bg-slate-800 text-white" : "text-slate-400 hover:bg-slate-800/50 hover:text-slate-200"}`}
              >
                <span className="truncate block font-medium flex-1">{s.title}</span>
                <span
                  onClick={(e) => handleDeleteSession(e, s.id)}
                  className="text-slate-600 hover:text-red-400 text-xs shrink-0 cursor-pointer"
                  title="Delete"
                >✕</span>
              </button>
            ))
          )}
        </div>
      </aside>

      {/* MAIN CHAT AREA */}
      <main className="flex-1 flex flex-col relative bg-[#f8fafc]">

        {/* Top bar */}
        <header className="h-14 flex items-center justify-between px-6 bg-white/80 backdrop-blur-md border-b border-slate-200 sticky top-0 z-10">
          <h2 className="text-sm font-semibold text-slate-700 truncate">
            {activeSession?.title || "Current Conversation"}
          </h2>
          <div className="text-xs font-medium text-emerald-600 bg-emerald-50 px-2.5 py-1 rounded-full border border-emerald-200 flex items-center gap-1.5">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"/>
            System Online
          </div>
        </header>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto px-4 py-8">
          <div className="max-w-3xl mx-auto space-y-8">
            {messages.map((m, i) => (
              <MessageBubble key={i} role={m.role} content={m.content} />
            ))}
            {loading && (
              <div className="flex gap-4 max-w-[85%] animate-in fade-in slide-in-from-bottom-2">
                <div className="w-9 h-9 rounded-xl bg-orange-500 flex items-center justify-center shrink-0 shadow-sm">
                  <span className="text-white text-sm font-bold">स</span>
                </div>
                <div className="bg-white border border-slate-200 px-5 py-4 rounded-2xl rounded-tl-sm shadow-sm flex items-center gap-1.5">
                  <div className="w-2 h-2 bg-slate-300 rounded-full animate-bounce"/>
                  <div className="w-2 h-2 bg-slate-300 rounded-full animate-bounce delay-100"/>
                  <div className="w-2 h-2 bg-slate-300 rounded-full animate-bounce delay-200"/>
                </div>
              </div>
            )}
            <div ref={bottomRef} className="h-20"/>
          </div>
        </div>

        {/* Input */}
        <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-[#f8fafc] via-[#f8fafc] to-transparent pt-12 pb-6 px-4">
          <InputBar onSend={handleSend} disabled={loading} />
        </div>
      </main>
    </div>
  );
}