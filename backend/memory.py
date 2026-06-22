"""
Session-based conversation memory with rolling window.
In-memory store (use Redis for production scale).
"""
import time
from collections import defaultdict
from config import config

# session_id -> list of {"role": "user"|"assistant", "content": str, "ts": float}
_sessions: dict[str, list[dict]] = defaultdict(list)
_session_meta: dict[str, dict] = defaultdict(dict)

def add_turn(session_id: str, role: str, content: str):
    """Add a message turn to the session."""
    _sessions[session_id].append({
        "role": role,
        "content": content,
        "ts": time.time()
    })
    # Keep rolling window
    if len(_sessions[session_id]) > config.MAX_HISTORY_TURNS * 2:
        _sessions[session_id] = _sessions[session_id][-(config.MAX_HISTORY_TURNS * 2):]

def get_history(session_id: str) -> list[dict]:
    """Return the conversation history as list of {role, content}."""
    return [{"role": m["role"], "content": m["content"]}
            for m in _sessions[session_id]]

def get_context_summary(session_id: str) -> str:
    """Build a text summary of recent conversation for query enrichment."""
    history = _sessions[session_id]
    if not history:
        return ""
    # Grab last 4 turns
    recent = history[-4:]
    lines = []
    for m in recent:
        prefix = "User" if m["role"] == "user" else "Assistant"
        lines.append(f"{prefix}: {m['content'][:200]}")
    return "\n".join(lines)

def clear_session(session_id: str):
    _sessions.pop(session_id, None)
    _session_meta.pop(session_id, None)

def update_meta(session_id: str, key: str, value):
    _session_meta[session_id][key] = value

def get_meta(session_id: str, key: str, default=None):
    return _session_meta[session_id].get(key, default)