"""FastAPI backend — GovtScheme AI Copilot
LLM: Groq (llama-3.1-8b-instant) — FREE 14,400 req/day"""
import uuid
import logging
import json
from contextlib import asynccontextmanager
from typing import Any, List, Optional

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from groq import Groq
from config import config
from rag_pipeline import retrieve, format_context
from memory import add_turn, get_history, get_context_summary, clear_session
from auth import sign_up, sign_in, get_current_user
from database import (
    create_session, get_user_sessions, update_session_title,
    delete_session as db_delete_session, save_message,
    get_session_messages, get_recent_messages_for_memory
)
from web_search import search_web, format_search_results, should_search_web

# ── Logging ────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

# ── Lifespan ───────────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting GovtScheme AI Copilot...")
    if not config.GROQ_API_KEY:
        logger.error("❌ GROQ_API_KEY not set in .env file!")
        raise RuntimeError("GROQ_API_KEY is required")

    from rag_pipeline import load_artifacts
    load_artifacts()

    logger.info("✅ GovtScheme AI Copilot is ready!")
    logger.info(f"   LLM    : Groq {config.LLM_MODEL} (FREE)")
    logger.info("   RAG    : FAISS + SentenceTransformers")
    logger.info("   Memory : Firestore persistent + session rolling window")
    logger.info(f"   Search : Serper web search {'✅' if config.SERPER_API_KEY else '❌ key not set'}")
    yield
    logger.info("Shutting down...")

# ── FastAPI App ────────────────────────────────────────────────────────────
app = FastAPI(
    title="GovtScheme AI Copilot",
    description="RAG-powered chatbot for Indian Government schemes (Groq)",
    version="3.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Groq Setup ─────────────────────────────────────────────────────────────
groq_client = Groq(api_key=config.GROQ_API_KEY)

SYSTEM_PROMPT = """You are **Sarkari Yojana AI** — an expert, friendly AI assistant specialized exclusively in Indian Government welfare schemes, policies, and programs.

## STRICT RULES
1. ALWAYS respond strictly in ENGLISH. Even if the retrieved context contains Hindi, you must translate and explain it in English.
2. ONLY answer questions about Indian government schemes. For unrelated topics, say: "I'm specialized in Indian government schemes. Please ask me about schemes, eligibility, benefits, or application processes."
3. BASE every answer strictly on the [RETRIEVED SCHEMES CONTEXT] provided. Never invent scheme names, amounts, or eligibility criteria.
4. If context says "NO_RELEVANT_SCHEMES_FOUND", respond: "I couldn't find a specific scheme matching your query. Could you provide more details?"
5. REMEMBER previous conversation — the user may refer back to earlier topics.
6. Never output raw JSON or code blocks.
7. When [LIVE WEB SEARCH RESULTS] are provided, prioritize them for recent or current information and always mention the source URL so users can verify.

## RESPONSE FORMAT
For each relevant scheme:
### 🏛️ [Scheme Name]
**What it is:** [1-2 sentence summary]
**✅ Eligibility:**
- [point 1]
- [point 2]
**💰 Key Benefits:**
- [benefit 1]
- [benefit 2]
**📍 Available In:** [State / All India]
**🏢 Ministry:** [Ministry name]
**📝 How to Apply:** [brief process or website]
---
End every response with one helpful tip OR a follow-up question.

## TONE
- Simple, accessible, and professional English.
- Warm and helpful — like a knowledgeable government welfare officer.
- Concise — summarize intelligently, do not dump raw text.
"""

# ── Topic classifier ───────────────────────────────────────────────────────
def is_off_topic(query: str) -> bool:
    try:
        result = groq_client.chat.completions.create(
            model=config.LLM_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a topic classifier. Reply with ONLY one word: "
                        "'relevant' if the question is about Indian government schemes, "
                        "subsidies, welfare programs, eligibility, benefits, or related topics. "
                        "Reply 'offtopic' if it is about anything else."
                    )
                },
                {"role": "user", "content": query}
            ],
            max_tokens=5,
            temperature=0.0,
        )
        label = result.choices[0].message.content.strip().lower()
        return label == "offtopic"
    except Exception:
        return False

OFF_TOPIC_RESPONSE = """I'm **Sarkari Yojana AI** — I'm specialized in Indian government schemes and welfare programs. I'm not able to help with that topic.

Here's what I *can* help you with:
- 🔍 Finding schemes you're eligible for
- 📋 Eligibility criteria and required documents
- 💰 Benefits and subsidy amounts
- 📝 How to apply for any scheme
- 🏛️ State-wise and central government programs

Try asking me something like:
- *"What schemes are available for farmers?"*
- *"Education scholarships for SC/ST students"*
- *"PM Kisan eligibility criteria"*"""

# ── Helpers ────────────────────────────────────────────────────────────────
def build_user_message(query: str, context: str, session_id: str, web_context: str = "") -> str:
    conv_summary = get_context_summary(session_id)
    parts = [f"User Question: {query}"]
    if conv_summary:
        # Truncate summary to save tokens
        summary_short = conv_summary[:200]
        parts.append(f"\n[RECENT CONTEXT]\n{summary_short}")
    # Truncate RAG context to save tokens
    context_short = context[:1500] if len(context) > 1500 else context
    parts.append(f"\n[RETRIEVED SCHEMES CONTEXT]\n{context_short}")
    if web_context:
        parts.append(f"\n{web_context}")
    return "\n".join(parts)


def build_groq_history(session_id: str) -> list:
    history = get_history(session_id)
    # Only keep last 4 turns (2 user + 2 assistant) to save tokens
    recent = history[-4:] if len(history) > 4 else history
    return [
        {"role": "user" if msg["role"] == "user" else "assistant",
         "content": msg["content"][:300]}  # Truncate old messages to 300 chars
        for msg in recent
    ]

def generate_session_title(first_message: str) -> str:
    try:
        result = groq_client.chat.completions.create(
            model=config.LLM_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Generate a very short title (max 5 words) for a chat "
                        "that starts with this message. Reply with ONLY the title, nothing else."
                    )
                },
                {"role": "user", "content": first_message}
            ],
            max_tokens=15,
            temperature=0.3,
        )
        return result.choices[0].message.content.strip()
    except Exception:
        return first_message[:40]

def call_groq(history: list, user_msg: str) -> str:
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.extend(history)
    messages.append({"role": "user", "content": user_msg})
    response = groq_client.chat.completions.create(
        model=config.LLM_MODEL,
        messages=messages,
        max_tokens=800,
        temperature=0.3,
        top_p=0.8,
    )
    return response.choices[0].message.content

# ── Pydantic Models ────────────────────────────────────────────────────────
class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=1000)
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    session_id: str
    sources: List[Any]
    confidence: float
    found_schemes: bool
    off_topic: bool = False
    web_search_used: bool = False

class NewSessionResponse(BaseModel):
    session_id: str

class SignUpRequest(BaseModel):
    email: str
    password: str
    full_name: str

class SignInRequest(BaseModel):
    email: str
    password: str

# ── Routes ─────────────────────────────────────────────────────────────────
@app.get("/")
async def root():
    return {
        "status": "ok",
        "service": "Sarkari Yojana AI",
        "llm": f"Groq {config.LLM_MODEL}",
        "schemes_indexed": "4644+",
        "web_search": "enabled" if config.SERPER_API_KEY else "disabled"
    }

@app.get("/health")
async def health():
    return {"status": "healthy", "model": config.LLM_MODEL}

@app.get("/debug/search")
async def debug_search(q: str):
    results = search_web(q)
    return {"count": len(results), "results": results}

# ── Auth routes ────────────────────────────────────────────────────────────
@app.post("/auth/signup")
async def signup(data: SignUpRequest):
    return sign_up(data)

@app.post("/auth/signin")
async def signin(data: SignInRequest):
    return sign_in(data)

@app.get("/auth/me")
async def get_me(current_user: dict = Depends(get_current_user)):
    return current_user

# ── Session routes ─────────────────────────────────────────────────────────
@app.post("/sessions/new", response_model=NewSessionResponse)
async def new_session(current_user: dict = Depends(get_current_user)):
    session_id = create_session(current_user["user_id"])
    logger.info(f"New session: {session_id[:8]} for user {current_user['user_id'][:8]}")
    return {"session_id": session_id}

@app.get("/sessions")
async def list_sessions(current_user: dict = Depends(get_current_user)):
    sessions = get_user_sessions(current_user["user_id"])
    return {"sessions": sessions}

@app.get("/sessions/{session_id}/messages")
async def list_messages(session_id: str, current_user: dict = Depends(get_current_user)):
    messages = get_session_messages(session_id, current_user["user_id"])
    return {"messages": messages}

@app.delete("/sessions/{session_id}")
async def remove_session(session_id: str, current_user: dict = Depends(get_current_user)):
    success = db_delete_session(session_id, current_user["user_id"])
    if not success:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"message": "Session deleted"}

# ── Chat route ─────────────────────────────────────────────────────────────
@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest, current_user: dict = Depends(get_current_user)):
    user_id = current_user["user_id"]
    session_id = req.session_id or create_session(user_id)
    logger.info(f"[{session_id[:8]}] Query: {req.message[:80]}")

    try:
        # 1. Off-topic guard
        if is_off_topic(req.message):
            save_message(session_id, user_id, "user", req.message)
            save_message(session_id, user_id, "assistant", OFF_TOPIC_RESPONSE)
            return ChatResponse(
                response=OFF_TOPIC_RESPONSE,
                session_id=session_id,
                sources=[],
                confidence=0.0,
                found_schemes=False,
                off_topic=True,
                web_search_used=False
            )

        # 2. RAG Retrieve
        conv_context = get_context_summary(session_id)
        enriched_query = f"{conv_context}\n{req.message}" if conv_context else req.message
        schemes, scores = retrieve(enriched_query)
        context_str = format_context(schemes, scores)
        confidence = max(scores) if scores else 0.0
        found_schemes = len(schemes) > 0

        # 3. Web search if RAG confidence is low
        web_context = ""
        web_results = []
        web_search_used = False
        logger.info(f"[{session_id[:8]}] Confidence: {confidence:.3f}, checking web search...")
        if should_search_web(confidence, req.message, schemes):
            logger.info(f"[{session_id[:8]}] Triggering web search")
            web_results = search_web(req.message)
            web_context = format_search_results(web_results)
            if web_results:
                found_schemes = True
                web_search_used = True
                logger.info(f"[{session_id[:8]}] Web search returned {len(web_results)} results")
        else:
            logger.info(f"[{session_id[:8]}] Web search skipped — good dataset match found")

        # 4. Build Groq inputs
        user_msg = build_user_message(req.message, context_str, session_id, web_context)
        groq_history = build_groq_history(session_id)

        # 5. Call Groq LLM
        ai_text = call_groq(groq_history, user_msg)

        # 6. Save to in-memory session memory
        add_turn(session_id, "user", req.message)
        add_turn(session_id, "assistant", ai_text)

        # 7. Save to Firestore permanently
        save_message(session_id, user_id, "user", req.message)
        save_message(session_id, user_id, "assistant", ai_text)

        # 8. Auto-generate session title from first message
        existing = get_session_messages(session_id, user_id)
        if len(existing) <= 2:
            title = generate_session_title(req.message)
            update_session_title(session_id, title)

        # 9. Format sources — RAG + web combined
        source_cards = [
            {
                "name": s.get("name", "Unknown Scheme"),
                "category": s.get("category", "Uncategorized"),
                "state": s.get("state", "All India"),
                "ministry": s.get("ministry", "Various"),
                "score": round(sc, 3),
                "url": ""
            }
            for s, sc in zip(schemes, scores)
        ]
        web_source_cards = [
            {
                "name": r["title"],
                "category": "Live Web Result",
                "state": "All India",
                "ministry": r["source"],
                "score": 0.99,
                "url": r["link"]
            }
            for r in web_results
        ]
        source_cards = source_cards + web_source_cards

        return ChatResponse(
            response=ai_text,
            session_id=session_id,
            sources=source_cards,
            confidence=round(confidence, 3),
            found_schemes=found_schemes,
            off_topic=False,
            web_search_used=web_search_used
        )

    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# ── Streaming chat ─────────────────────────────────────────────────────────
@app.post("/chat/stream")
async def chat_stream(req: ChatRequest, current_user: dict = Depends(get_current_user)):
    user_id = current_user["user_id"]
    session_id = req.session_id or create_session(user_id)
    logger.info(f"[{session_id[:8]}] Stream query: {req.message[:80]}")

    # Off-topic check
    if is_off_topic(req.message):
        save_message(session_id, user_id, "user", req.message)
        save_message(session_id, user_id, "assistant", OFF_TOPIC_RESPONSE)
        def off_topic_stream():
            yield f"data: {json.dumps({'type': 'sources', 'sources': [], 'found': False, 'confidence': 0.0, 'off_topic': True, 'web_search_used': False})}\n\n"
            yield f"data: {json.dumps({'type': 'text', 'delta': OFF_TOPIC_RESPONSE})}\n\n"
            yield f"data: {json.dumps({'type': 'done'})}\n\n"
        return StreamingResponse(
            off_topic_stream(),
            media_type="text/event-stream",
            headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"}
        )

    # RAG Retrieve
    conv_context = get_context_summary(session_id)
    enriched_query = f"{conv_context}\n{req.message}" if conv_context else req.message
    schemes, scores = retrieve(enriched_query)
    context_str = format_context(schemes, scores)
    confidence = max(scores) if scores else 0.0
    found_schemes = len(schemes) > 0

    # Web search if confidence low
    
    web_context = ""
    web_results = []
    web_search_used = False
    logger.info(f"[{session_id[:8]}] Confidence: {confidence:.3f}, checking web search...")
    if should_search_web(confidence, req.message, schemes):
        logger.info(f"[{session_id[:8]}] Triggering web search")
        web_results = search_web(req.message)
        web_context = format_search_results(web_results)
        if web_results:
            found_schemes = True
            web_search_used = True
            logger.info(f"[{session_id[:8]}] Web search returned {len(web_results)} results")
    else:
        logger.info(f"[{session_id[:8]}] Web search skipped — good dataset match found")

    # Build inputs
    user_msg = build_user_message(req.message, context_str, session_id, web_context)
    groq_history = build_groq_history(session_id)

    # Format sources
    source_cards = [
        {
            "name": s.get("name", "Unknown Scheme"),
            "category": s.get("category", "Uncategorized"),
            "state": s.get("state", "All India"),
            "ministry": s.get("ministry", "Various"),
            "score": round(sc, 3),
            "url": ""
        }
        for s, sc in zip(schemes, scores)
    ]
    web_source_cards = [
        {
            "name": r["title"],
            "category": "Live Web Result",
            "state": "All India",
            "ministry": r["source"],
            "score": 0.99,
            "url": r["link"]
        }
        for r in web_results
    ]
    all_source_cards = source_cards + web_source_cards

    def generate():
        full_text = ""
        yield f"data: {json.dumps({'type': 'sources', 'sources': all_source_cards, 'found': found_schemes, 'confidence': round(confidence, 3), 'off_topic': False, 'web_search_used': web_search_used})}\n\n"
        try:
            messages = [{"role": "system", "content": SYSTEM_PROMPT}]
            messages.extend(groq_history)
            messages.append({"role": "user", "content": user_msg})
            stream_response = groq_client.chat.completions.create(
                model=config.LLM_MODEL,
                messages=messages,
                max_tokens=800,
                temperature=0.3,
                top_p=0.8,
                stream=True,
            )
            for chunk in stream_response:
                delta = chunk.choices[0].delta.content
                if delta:
                    full_text += delta
                    yield f"data: {json.dumps({'type': 'text', 'delta': delta})}\n\n"
        except Exception as e:
            logger.error(f"Streaming error: {e}", exc_info=True)
            yield f"data: {json.dumps({'type': 'error', 'message': f'❌ Error: {str(e)}'})}\n\n"
        finally:
            if full_text:
                add_turn(session_id, "user", req.message)
                add_turn(session_id, "assistant", full_text)
                save_message(session_id, user_id, "user", req.message)
                save_message(session_id, user_id, "assistant", full_text)
                existing = get_session_messages(session_id, user_id)
                if len(existing) <= 2:
                    title = generate_session_title(req.message)
                    update_session_title(session_id, title)
            yield f"data: {json.dumps({'type': 'done'})}\n\n"
            logger.info(f"[{session_id[:8]}] Stream complete, {len(full_text)} chars")

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"}
    )