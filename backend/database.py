import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
import os

# Initialize Firebase
cred = credentials.Certificate("firebase_key.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

# ─────────────────────────────────────────
# SESSION FUNCTIONS
# ─────────────────────────────────────────

def create_session(user_id: str, title: str = "New Chat") -> str:
    """Create a new chat session and return its ID"""
    session_ref = db.collection("sessions").document()
    session_ref.set({
        "user_id": user_id,
        "title": title,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    })
    return session_ref.id

def get_user_sessions(user_id: str) -> list:
    """Get all sessions for a user, sorted by latest first"""
    sessions = (
        db.collection("sessions")
        .where("user_id", "==", user_id)
        .order_by("updated_at", direction=firestore.Query.DESCENDING)
        .limit(50)
        .stream()
    )
    result = []
    for s in sessions:
        data = s.to_dict()
        result.append({
            "session_id": s.id,
            "title": data.get("title", "New Chat"),
            "updated_at": data.get("updated_at").isoformat() if data.get("updated_at") else ""
        })
    return result

def update_session_title(session_id: str, title: str):
    """Update session title based on first message"""
    db.collection("sessions").document(session_id).update({
        "title": title,
        "updated_at": datetime.utcnow()
    })

def delete_session(session_id: str, user_id: str):
    """Delete a session and all its messages"""
    # Verify ownership first
    session = db.collection("sessions").document(session_id).get()
    if not session.exists or session.to_dict().get("user_id") != user_id:
        return False
    
    # Delete all messages in session
    messages = db.collection("messages").where("session_id", "==", session_id).stream()
    for msg in messages:
        msg.reference.delete()
    
    # Delete session
    db.collection("sessions").document(session_id).delete()
    return True

# ─────────────────────────────────────────
# MESSAGE FUNCTIONS
# ─────────────────────────────────────────

def save_message(session_id: str, user_id: str, role: str, content: str):
    """Save a single message to Firestore"""
    db.collection("messages").add({
        "session_id": session_id,
        "user_id": user_id,
        "role": role,  # "user" or "assistant"
        "content": content,
        "timestamp": datetime.utcnow()
    })
    # Update session's updated_at
    db.collection("sessions").document(session_id).update({
        "updated_at": datetime.utcnow()
    })

def get_session_messages(session_id: str, user_id: str) -> list:
    """Get all messages for a session"""
    # Verify ownership
    session = db.collection("sessions").document(session_id).get()
    if not session.exists or session.to_dict().get("user_id") != user_id:
        return []
    
    messages = (
        db.collection("messages")
        .where("session_id", "==", session_id)
        .order_by("timestamp")
        .stream()
    )
    result = []
    for msg in messages:
        data = msg.to_dict()
        result.append({
            "role": data.get("role"),
            "content": data.get("content"),
            "timestamp": data.get("timestamp").isoformat() if data.get("timestamp") else ""
        })
    return result

def get_recent_messages_for_memory(session_id: str, limit: int = 10) -> list:
    """Get last N messages for context injection into LLM"""
    messages = (
        db.collection("messages")
        .where("session_id", "==", session_id)
        .order_by("timestamp", direction=firestore.Query.DESCENDING)
        .limit(limit)
        .stream()
    )
    result = []
    for msg in messages:
        data = msg.to_dict()
        result.append({
            "role": data.get("role"),
            "content": data.get("content")
        })
    return list(reversed(result))  # Return in chronological order