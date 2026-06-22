const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8001";

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  sources?: Source[];
  confidence?: number;
}

export interface Source {
  name: string;
  category: string;
  state: string;
  ministry?: string;
  score: number;
}

export interface Session {
  session_id: string;
  title: string;
  updated_at: string;
}

// ── Auth header helper ─────────────────────────────────────────────────────
function authHeaders(): Record<string, string> {
  const token = localStorage.getItem("access_token");
  return {
    "Content-Type": "application/json",
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };
}

// ── Chat (streaming) ───────────────────────────────────────────────────────
export async function sendMessage(
  message: string,
  sessionId: string,
  onChunk: (text: string) => void,
  onSources: (sources: Source[]) => void,
  onDone: () => void,
  onError: (err: string) => void
): Promise<void> {
  const res = await fetch(`${API_BASE}/chat/stream`, {
    method: "POST",
    headers: authHeaders(),
    body: JSON.stringify({ message, session_id: sessionId }),
  });

  if (res.status === 401) {
    // Token expired — redirect to login
    localStorage.clear();
    window.location.href = "/login";
    return;
  }

  if (!res.ok) {
    onError(`Server error: ${res.status}`);
    return;
  }

  const reader = res.body!.getReader();
  const decoder = new TextDecoder();

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    const lines = decoder.decode(value).split("\n");
    for (const line of lines) {
      if (!line.startsWith("data: ")) continue;
      try {
        const data = JSON.parse(line.slice(6));
        if (data.type === "sources") onSources(data.sources);
        else if (data.type === "text") onChunk(data.delta);
        else if (data.type === "done") onDone();
        else if (data.type === "error") onError(data.message);
      } catch {}
    }
  }
}

// ── Sessions ───────────────────────────────────────────────────────────────
export async function newSession(): Promise<string> {
  const res = await fetch(`${API_BASE}/sessions/new`, {
    method: "POST",
    headers: authHeaders(),
  });
  if (res.status === 401) {
    localStorage.clear();
    window.location.href = "/login";
    return "";
  }
  const data = await res.json();
  return data.session_id;
}

export async function getUserSessions(): Promise<Session[]> {
  const res = await fetch(`${API_BASE}/sessions`, {
    headers: authHeaders(),
  });
  if (res.status === 401) {
    localStorage.clear();
    window.location.href = "/login";
    return [];
  }
  const data = await res.json();
  return data.sessions || [];
}

export async function getSessionMessages(sessionId: string): Promise<ChatMessage[]> {
  const res = await fetch(`${API_BASE}/sessions/${sessionId}/messages`, {
    headers: authHeaders(),
  });
  if (!res.ok) return [];
  const data = await res.json();
  return data.messages || [];
}

export async function deleteSession(sessionId: string): Promise<boolean> {
  const res = await fetch(`${API_BASE}/sessions/${sessionId}`, {
    method: "DELETE",
    headers: authHeaders(),
  });
  return res.ok;
}