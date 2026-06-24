# 🏛️ Sarkari Yojana AI — India's Intelligent Government Scheme Assistant

<div align="center">

![Sarkari Yojana AI](https://img.shields.io/badge/Sarkari%20Yojana-AI%20Chatbot-orange?style=for-the-badge)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111.0-009688?style=for-the-badge&logo=fastapi)
![Next.js](https://img.shields.io/badge/Next.js-14-black?style=for-the-badge&logo=next.js)
![Groq](https://img.shields.io/badge/Groq-LLaMA%203.1-red?style=for-the-badge)
![Firebase](https://img.shields.io/badge/Firebase-Firestore-orange?style=for-the-badge&logo=firebase)
![Supabase](https://img.shields.io/badge/Supabase-Auth-3ECF8E?style=for-the-badge&logo=supabase)
![Vercel](https://img.shields.io/badge/Vercel-Deployed-black?style=for-the-badge&logo=vercel)
![Render](https://img.shields.io/badge/Render-Backend-blue?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)

**A production-grade AI chatbot for discovering and understanding Indian government welfare schemes — powered by RAG, real-time web search, persistent chat history, and JWT authentication.**

[🌐 Live Demo](https://sarkari-yojana-two.vercel.app) · [🐛 Report Bug](https://github.com/Kunal-Pramanik/Sarkari_yojana_ai/issues) · [💡 Request Feature](https://github.com/Kunal-Pramanik/Sarkari_yojana_ai/issues)

</div>

---

## 📋 Table of Contents

- [📖 About the Project](#-about-the-project)
- [✨ Features](#-features)
- [🏗️ System Architecture](#️-system-architecture)
- [🛠️ Tech Stack](#️-tech-stack)
- [🚀 Live Demo](#-live-demo)
- [⚙️ How It Works](#️-how-it-works)
  - [RAG Pipeline](#rag-pipeline)
  - [Web Search Fallback](#web-search-fallback)
  - [Authentication Flow](#authentication-flow)
  - [Chat History & Memory](#chat-history--memory)
  - [Off-Topic Guard](#off-topic-guard)
- [📁 Project Structure](#-project-structure)
- [🔧 Local Setup & Installation](#-local-setup--installation)
  - [Prerequisites](#prerequisites)
  - [Backend Setup](#backend-setup)
  - [Frontend Setup](#frontend-setup)
  - [Environment Variables](#environment-variables)
- [🌍 Deployment Guide](#-deployment-guide)
  - [Deploy Backend on Render](#deploy-backend-on-render)
  - [Deploy Frontend on Vercel](#deploy-frontend-on-vercel)
- [📡 API Reference](#-api-reference)
- [🗄️ Database Schema](#️-database-schema)
- [🔒 Security](#-security)
- [🧠 AI & ML Details](#-ai--ml-details)
- [📊 Performance & Limits](#-performance--limits)
- [🗺️ Roadmap](#️-roadmap)
- [🤝 Contributing](#-contributing)
- [👨‍💻 Author](#-author)
- [📄 License](#-license)

---

## 📖 About the Project

**Sarkari Yojana AI** is a full-stack conversational AI application that helps Indian citizens discover, understand, and apply for government welfare schemes. India has thousands of central and state government schemes covering agriculture, education, healthcare, employment, and more — but most citizens are unaware of the schemes they are eligible for.

This project solves that problem by combining:

- A curated dataset of **4,644+ Indian government schemes** indexed with vector embeddings
- A **RAG (Retrieval-Augmented Generation)** pipeline for accurate, hallucination-free answers
- **Real-time web search** via Serper API to fetch the latest scheme updates from official government websites
- A **ChatGPT-style interface** with persistent chat history, user authentication, and session management

The bot answers questions about eligibility criteria, required documents, benefit amounts, application processes, and ministry contacts — all in simple, accessible English.

---

## ✨ Features

### 🤖 AI & Intelligence
- **RAG Pipeline** — retrieves the most relevant schemes from a 4,644-scheme FAISS index before answering, ensuring accuracy
- **Live Web Search** — when dataset confidence is low, automatically searches official government sites (myscheme.gov.in, india.gov.in, epfindia.gov.in) via Serper API
- **Off-Topic Guard** — classifies every query before answering; unrelated questions receive a polite redirect with suggested scheme topics
- **Streaming Responses** — answers stream token-by-token, just like ChatGPT
- **Context Memory** — remembers the last 4 conversation turns for follow-up questions

### 👤 User Management
- **Sign Up / Sign In** — email and password authentication via Supabase Auth
- **JWT Token Auth** — every API request is protected with JSON Web Tokens
- **Auto Login** — returning users are automatically logged in from saved tokens
- **Logout** — single-click logout clears all session data

### 💬 Chat Experience
- **Persistent Chat History** — all conversations saved to Firebase Firestore forever
- **Session Sidebar** — ChatGPT-style sidebar showing all past conversations
- **Auto-generated Titles** — session titles are auto-generated from the first message
- **Load Past Chats** — click any session to reload its full message history
- **Delete Sessions** — remove unwanted conversations
- **Source Cards** — every response shows which schemes were retrieved (with confidence scores) and which web sources were used

### 🎨 UI/UX
- **Dark-themed sidebar** with orange branding
- **Markdown rendering** — responses render with headings, bullet points, and bold text
- **Typing indicator** — animated dots while the AI is thinking
- **Mobile responsive** layout
- **System Online** status indicator

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    USER (Browser)                        │
│              Next.js Frontend (Vercel)                   │
└──────────────────────┬──────────────────────────────────┘
                       │ HTTPS + JWT
          ┌────────────▼────────────┐
          │   FastAPI Backend        │
          │   (Render)               │
          └──┬──────┬──────┬────────┘
             │      │      │
    ┌────────▼─┐ ┌──▼───┐ ┌▼──────────────┐
    │ Supabase │ │Groq  │ │  Firebase      │
    │   Auth   │ │LLaMA │ │  Firestore     │
    │  (JWT)   │ │  3.1 │ │  (Chat DB)     │
    └──────────┘ └──┬───┘ └───────────────┘
                    │
          ┌─────────▼──────────┐
          │   RAG Pipeline      │
          │  FAISS Index        │
          │  4,644 Schemes      │
          └─────────┬──────────┘
                    │ Low confidence?
          ┌─────────▼──────────┐
          │   Serper API        │
          │   Web Search        │
          │   (gov.in sites)    │
          └────────────────────┘
```

---

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Frontend** | Next.js 14, TypeScript, Tailwind CSS | Chat UI, routing, streaming |
| **Backend** | FastAPI, Python 3.11 | REST API, RAG pipeline, auth |
| **LLM** | Groq (LLaMA 3.1 8B Instant) | Language generation, classification |
| **Vector Search** | FAISS (Facebook AI) | Semantic similarity search |
| **Embeddings** | paraphrase-multilingual-MiniLM-L12-v2 | Multilingual scheme embeddings |
| **Authentication** | Supabase Auth | JWT-based user auth |
| **Database** | Firebase Firestore | Persistent chat history |
| **Web Search** | Serper API | Real-time government data |
| **Frontend Deploy** | Vercel | CDN, auto-deploy from GitHub |
| **Backend Deploy** | Render | Python web service hosting |

---

## 🚀 Live Demo

| Service | URL |
|---------|-----|
| 🌐 Frontend | [https://sarkari-yojana-two.vercel.app](https://sarkari-yojana-two.vercel.app) |
| ⚙️ Backend API | [https://sarkari-yojana-cli0.onrender.com](https://sarkari-yojana-cli0.onrender.com) |
| 📚 API Docs | [https://sarkari-yojana-cli0.onrender.com/docs](https://sarkari-yojana-cli0.onrender.com/docs) |

> **Note:** The Render free tier spins down after 15 minutes of inactivity. The first request after inactivity may take ~30 seconds to wake up.

---

## ⚙️ How It Works

### RAG Pipeline

RAG (Retrieval-Augmented Generation) ensures the bot never hallucinates scheme details. Here's the exact flow for every user message:

1. **Query enrichment** — the user's message is combined with recent conversation context to form an enriched query
2. **Vector embedding** — the enriched query is embedded using the multilingual MiniLM model via HuggingFace Inference API
3. **FAISS search** — the embedding is compared against 4,644 pre-indexed scheme vectors using cosine similarity
4. **Top-K retrieval** — the 3 most relevant schemes are retrieved along with their confidence scores
5. **Context injection** — retrieved scheme details are injected into the LLM prompt as `[RETRIEVED SCHEMES CONTEXT]`
6. **LLM generation** — Groq's LLaMA 3.1 8B generates a structured response based strictly on the retrieved context

The FAISS index was pre-built locally using `build_index.py` and committed as a static file (`schemes.index`, 7MB), meaning the server doesn't need to load heavy ML models at runtime — keeping memory usage under 512MB.

### Web Search Fallback

When RAG confidence is low (raw dot-product score below 16.0) OR when the query contains scheme-specific keywords but no strong dataset match is found, the bot automatically triggers a web search:

1. **Confidence check** — `should_search_web()` evaluates confidence score AND keyword overlap with retrieved schemes
2. **Serper API call** — searches Google filtered to government domains (`site:gov.in`, `site:myscheme.gov.in`)
3. **Result formatting** — top 2 results (title, snippet, URL) are injected as `[LIVE WEB SEARCH RESULTS]`
4. **Priority instruction** — the system prompt instructs the LLM to prioritize live results and cite source URLs

This means the bot always has access to the latest scheme updates, new launches, and recent policy changes — without requiring manual dataset updates.

### Authentication Flow

```
User visits app
      ↓
Token in localStorage? → YES → Verify with Supabase → Load chat → Done
      ↓ NO
Login page
      ↓
Email + Password → POST /auth/signin → Supabase validates
      ↓
JWT access token returned → Saved to localStorage
      ↓
Every API request → Authorization: Bearer <token> header
      ↓
FastAPI → get_current_user() → Supabase verifies token → Returns user_id
```

### Chat History & Memory

Every message exchange is saved to Firebase Firestore in two collections:

**`sessions` collection:**
```json
{
  "user_id": "uuid",
  "title": "PM Kisan Eligibility",
  "created_at": "timestamp",
  "updated_at": "timestamp"
}
```

**`messages` collection:**
```json
{
  "session_id": "firestore_doc_id",
  "user_id": "uuid",
  "role": "user" | "assistant",
  "content": "message text",
  "timestamp": "timestamp"
}
```

Session titles are auto-generated by asking Groq to summarize the first user message in 5 words or fewer.

For in-context memory, the last 4 message turns are injected into every prompt as `[RECENT CONVERSATION CONTEXT]`, enabling natural follow-up questions like "tell me more about the second one."

### Off-Topic Guard

Before every query reaches the RAG pipeline, a fast single-token classifier checks if it's relevant:

```python
# Classifier prompt (uses max_tokens=5 to minimize cost)
"Reply ONLY 'relevant' or 'offtopic'"
```

If classified as off-topic, the bot returns a friendly redirect message suggesting relevant scheme categories — without consuming RAG or web search resources.

---

## 📁 Project Structure

```
Sarkari_yojana_ai/
├── backend/
│   ├── main.py                 # FastAPI app, all routes
│   ├── auth.py                 # Supabase auth functions
│   ├── database.py             # Firebase Firestore operations
│   ├── rag_pipeline.py         # FAISS search, embedding, retrieval
│   ├── web_search.py           # Serper API integration
│   ├── memory.py               # In-session rolling memory
│   ├── config.py               # Environment config
│   ├── build_index.py          # One-time script to build FAISS index
│   ├── schemes.index           # Pre-built FAISS index (7MB)
│   ├── schemes_meta.json       # 4,644 scheme metadata
│   ├── schemes_embeddings.npy  # Pre-computed embeddings (7MB)
│   ├── requirements.txt        # Python dependencies
│   ├── .python-version         # Python 3.11.9 for Render
│   └── .env                    # Local env vars (not committed)
│
├── frontend/
│   ├── app/
│   │   ├── page.tsx            # Main chat page (auth-protected)
│   │   ├── login/page.tsx      # Sign up / Sign in page
│   │   └── layout.tsx          # Root layout
│   ├── components/
│   │   ├── ChatWindow.tsx      # Main chat interface + sidebar
│   │   ├── MessageBubble.tsx   # Individual message rendering
│   │   └── InputBar.tsx        # Message input component
│   ├── lib/
│   │   ├── api.ts              # Backend API calls with JWT
│   │   ├── auth.ts             # Auth helpers (login, logout, token)
│   │   └── supabase.ts         # Supabase client
│   ├── .env.local              # Local env vars (not committed)
│   └── package.json
│
└── README.md
```

---

## 🔧 Local Setup & Installation

### Prerequisites

Make sure you have these installed:

- **Python 3.11+** — [download](https://www.python.org/downloads/)
- **Node.js 18+** — [download](https://nodejs.org/)
- **Git** — [download](https://git-scm.com/)

You'll also need free accounts on:
- [Supabase](https://supabase.com) — for authentication
- [Firebase](https://console.firebase.google.com) — for Firestore database
- [Groq](https://console.groq.com) — for LLM API
- [Serper](https://serper.dev) — for web search
- [HuggingFace](https://huggingface.co) — for embedding API

### Backend Setup

```bash
# 1. Clone the repository
git clone https://github.com/Kunal-Pramanik/Sarkari_yojana_ai.git
cd Sarkari_yojana_ai

# 2. Create and activate virtual environment
cd backend
python -m venv venv

# Windows
venv\Scripts\activate
# Mac/Linux
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Add your environment variables (see below)
# Create a .env file in the backend folder

# 5. Add your Firebase service account key
# Download firebase_key.json from Firebase Console
# Place it in the backend/ folder

# 6. Build the FAISS index (first time only)
python build_index.py

# 7. Start the backend server
uvicorn main:app --reload --port 8001
```

The backend will be available at `http://localhost:8001`
API documentation at `http://localhost:8001/docs`

### Frontend Setup

```bash
# From the project root
cd frontend

# 1. Install dependencies
npm install

# 2. Add your environment variables
# Create a .env.local file (see below)

# 3. Start the development server
npm run dev
```

The frontend will be available at `http://localhost:3000`

### Environment Variables

**Backend `.env`:**
```env
GROQ_API_KEY=your_groq_api_key
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your_supabase_anon_key
SUPABASE_SERVICE_KEY=your_supabase_service_role_key
SERPER_API_KEY=your_serper_api_key
HF_TOKEN=your_huggingface_token
```

**Frontend `.env.local`:**
```env
NEXT_PUBLIC_API_URL=http://localhost:8001
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
```

**Getting your API keys:**

| Key | Where to get it |
|-----|----------------|
| `GROQ_API_KEY` | [console.groq.com](https://console.groq.com) → API Keys |
| `SUPABASE_URL` | Supabase Dashboard → Settings → API |
| `SUPABASE_ANON_KEY` | Supabase Dashboard → Settings → API |
| `SUPABASE_SERVICE_KEY` | Supabase Dashboard → Settings → API → service_role |
| `SERPER_API_KEY` | [serper.dev](https://serper.dev) → Dashboard |
| `HF_TOKEN` | [huggingface.co](https://huggingface.co) → Settings → Access Tokens |
| `FIREBASE_KEY_JSON` | Firebase Console → Project Settings → Service Accounts → Generate Key |

---

## 🌍 Deployment Guide

### Deploy Backend on Render

1. Go to [render.com](https://render.com) and sign up with GitHub
2. Click **New + → Web Service**
3. Connect your GitHub repository
4. Configure the service:

| Setting | Value |
|---------|-------|
| Root Directory | `backend` |
| Runtime | Python 3 |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `uvicorn main:app --host 0.0.0.0 --port $PORT` |
| Plan | Free |

5. Add all environment variables from the backend `.env` file
6. For `FIREBASE_KEY_JSON` — paste the entire contents of your `firebase_key.json` file as the value
7. Click **Create Web Service**

> **Important:** Add a `.python-version` file in the backend folder containing `3.11.9` to ensure Render uses Python 3.11 instead of 3.14.

### Deploy Frontend on Vercel

1. Go to [vercel.com](https://vercel.com) and sign up with GitHub
2. Click **Add New Project**
3. Import your repository
4. Set **Root Directory** to `frontend`
5. Add environment variables:

| Variable | Value |
|----------|-------|
| `NEXT_PUBLIC_API_URL` | Your Render backend URL |
| `NEXT_PUBLIC_SUPABASE_URL` | Your Supabase project URL |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | Your Supabase anon key |

6. Click **Deploy**

After deployment, update Supabase:
- Go to **Authentication → URL Configuration**
- Set Site URL to your Vercel URL
- Add `https://your-app.vercel.app/**` to Redirect URLs

---

## 📡 API Reference

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/auth/signup` | Create new account |
| `POST` | `/auth/signin` | Login and get JWT token |
| `GET` | `/auth/me` | Get current user info |

**Sign up request:**
```json
{
  "email": "user@example.com",
  "password": "securepassword",
  "full_name": "Rahul Sharma"
}
```

**Sign in response:**
```json
{
  "access_token": "eyJhbGc...",
  "user_id": "uuid",
  "email": "user@example.com",
  "full_name": "Rahul Sharma"
}
```

### Sessions

All session routes require `Authorization: Bearer <token>` header.

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/sessions/new` | Create new chat session |
| `GET` | `/sessions` | List all user sessions |
| `GET` | `/sessions/{id}/messages` | Get messages for a session |
| `DELETE` | `/sessions/{id}` | Delete a session |

### Chat

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/chat` | Non-streaming chat |
| `POST` | `/chat/stream` | Streaming chat (SSE) |

**Chat request:**
```json
{
  "message": "What schemes are available for farmers?",
  "session_id": "firestore_session_id"
}
```

**Chat response:**
```json
{
  "response": "Here are the relevant schemes...",
  "session_id": "firestore_session_id",
  "sources": [...],
  "confidence": 18.42,
  "found_schemes": true,
  "off_topic": false,
  "web_search_used": false
}
```

**Streaming events (SSE):**
```
data: {"type": "sources", "sources": [...], "confidence": 18.42}
data: {"type": "text", "delta": "Here"}
data: {"type": "text", "delta": " are"}
data: {"type": "done"}
```

---

## 🗄️ Database Schema

### Firebase Firestore

**Collection: `sessions`**
```
sessions/
  {session_id}/
    user_id: string
    title: string
    created_at: timestamp
    updated_at: timestamp
```

**Collection: `messages`**
```
messages/
  {message_id}/
    session_id: string
    user_id: string
    role: "user" | "assistant"
    content: string
    timestamp: timestamp
```

**Required Firestore Indexes (Composite):**

| Collection | Fields | Order |
|-----------|--------|-------|
| `sessions` | `user_id` ASC, `updated_at` DESC | Descending |
| `messages` | `session_id` ASC, `timestamp` ASC | Ascending |

> Create these indexes in Firebase Console → Firestore → Indexes, or click the auto-generated links from error messages.

---

## 🔒 Security

- **JWT Authentication** — all chat and session endpoints require a valid Supabase JWT token
- **Token verification** — every request calls Supabase to verify the token server-side
- **Session ownership** — users can only access their own sessions; ownership is verified before every read/write
- **Firebase key** — stored as environment variable on Render, never committed to GitHub
- **Service role key** — used only server-side, never exposed to the frontend
- **CORS** — configured to allow requests only from the frontend domain in production

---

## 🧠 AI & ML Details

### Embedding Model
- **Model:** `paraphrase-multilingual-MiniLM-L12-v2`
- **Dimensions:** 384
- **Languages:** Supports Hindi, English, and 50+ languages
- **Why this model:** Lightweight (90MB), multilingual support for Indian language queries, good semantic understanding

### FAISS Index
- **Index type:** `IndexFlatIP` (Inner Product / Cosine Similarity)
- **Vectors:** 4,644 scheme embeddings
- **Index size:** ~7MB (pre-built, committed to repo)
- **Search speed:** <10ms per query

### Confidence Scoring
- Raw dot-product scores (not normalized 0-1)
- Empirically, scores above 16.0 indicate a strong dataset match
- Scores below 16.0 trigger web search fallback
- Named scheme queries with <50% word overlap with retrieved schemes also trigger web search

### LLM Configuration
- **Model:** `llama-3.1-8b-instant` via Groq API
- **Max tokens:** 800 (response) + 5 (classifier)
- **Temperature:** 0.3 (focused, consistent answers)
- **Context window:** System prompt + 4 history turns + RAG context + optional web results

---

## 📊 Performance & Limits

| Resource | Free Tier Limit | Usage |
|----------|----------------|-------|
| Groq API | 14,400 requests/day | ~3 calls per chat message |
| Serper API | 2,500 searches/month | Only triggered on low-confidence queries |
| Firebase Firestore | 50K reads, 20K writes/day | ~4 reads + 2 writes per message |
| Supabase Auth | Unlimited | Per request token verification |
| Render RAM | 512MB | ~300MB used (no torch at runtime) |
| Vercel | 100GB bandwidth/month | Static Next.js frontend |

---

## 🗺️ Roadmap

- [x] RAG pipeline with FAISS vector search
- [x] Groq LLaMA 3.1 integration
- [x] Supabase JWT authentication
- [x] Firebase Firestore persistent chat history
- [x] Serper API web search fallback
- [x] Off-topic query guard
- [x] Streaming responses
- [x] Session management with auto-titles
- [x] Deployment on Render + Vercel
- [ ] Hindi language interface
- [ ] Cross-session long-term memory (pgvector)
- [ ] Voice input support
- [ ] Scheme eligibility checker (form-based)
- [ ] Push notifications for new schemes
- [ ] Mobile app (React Native)
- [ ] Admin dashboard for scheme dataset updates

---

## 🤝 Contributing

Contributions are welcome! Here's how to get started:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

Please make sure your code follows the existing style and includes appropriate comments.

---

## 👨‍💻 Author

**Kunal Pramanik**

MSc Data Science student at DA-IICT Gandhinagar (Dhirubhai Ambani University)

[![GitHub](https://img.shields.io/badge/GitHub-Kunal--Pramanik-black?style=flat&logo=github)](https://github.com/Kunal-Pramanik)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-kunal--pramanik-blue?style=flat&logo=linkedin)](https://linkedin.com/in/kunal-pramanik-5aa131267)

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

<div align="center">

**Built with ❤️ for making Indian government schemes accessible to every citizen**

⭐ Star this repo if you found it helpful!

</div>
