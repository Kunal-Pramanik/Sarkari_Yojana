import os
import json
import faiss
import numpy as np
from config import config

_index = None
_chunks = None

def load_artifacts():
    global _index, _chunks

    index_file = "schemes.index"
    if config.INDEX_PATH != ".":
        index_file = os.path.join(config.INDEX_PATH, "schemes.index")

    print(f"Loading FAISS index from: {index_file}")
    _index = faiss.read_index(index_file)

    print(f"Loading chunks from: {config.CHUNKS_PATH}")
    with open(config.CHUNKS_PATH, "r", encoding="utf-8") as f:
        _chunks = json.load(f)

    print(f"✅ Loaded {_index.ntotal} vectors and {len(_chunks)} schemes.")

def get_query_embedding(query: str) -> np.ndarray:
    """Get embedding using Groq — no local model needed."""
    import httpx
    import os

    api_key = os.getenv("GROQ_API_KEY", "")

    try:
        # Use a tiny free embedding API — Hugging Face inference API
        hf_token = os.getenv("HF_TOKEN", "")
        if hf_token:
            with httpx.Client(timeout=10.0) as client:
                res = client.post(
                    "https://api-inference.huggingface.co/pipeline/feature-extraction/sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
                    headers={"Authorization": f"Bearer {hf_token}"},
                    json={"inputs": query, "options": {"wait_for_model": True}}
                )
                if res.status_code == 200:
                    embedding = np.array(res.json(), dtype="float32")
                    if embedding.ndim == 2:
                        embedding = embedding[0]
                    return embedding
    except Exception as e:
        print(f"HF embedding failed: {e}")

    # Fallback — keyword search using precomputed embeddings
    return None

def retrieve(query: str):
    global _index, _chunks

    if _index is None or _chunks is None:
        load_artifacts()

    # Try to get embedding from HuggingFace API
    query_vector = get_query_embedding(query)

    if query_vector is not None:
        # Normalize and search
        query_vector = query_vector.reshape(1, -1).astype("float32")
        faiss.normalize_L2(query_vector)
        k = config.TOP_K_RETRIEVAL
        distances, indices = _index.search(query_vector, k)

        schemes = []
        scores = []
        for i, idx in enumerate(indices[0]):
            if idx == -1:
                continue
            schemes.append(_chunks[idx])
            scores.append(float(distances[0][i]))
        return schemes, scores

    # Fallback — keyword matching if embedding API fails
    return keyword_search(query)

def keyword_search(query: str):
    """Simple keyword fallback when embedding API is unavailable."""
    global _chunks
    query_lower = query.lower()
    query_words = set(query_lower.split())

    scored = []
    for chunk in _chunks:
        text = f"{chunk.get('name','')} {chunk.get('category','')} {chunk.get('details','')[:200]}".lower()
        matches = sum(1 for w in query_words if w in text and len(w) > 3)
        if matches > 0:
            scored.append((chunk, float(matches * 5)))

    scored.sort(key=lambda x: x[1], reverse=True)
    top = scored[:config.TOP_K_RETRIEVAL]
    if not top:
        return [], []
    return [s[0] for s in top], [s[1] for s in top]

def format_context(schemes: list, scores: list) -> str:
    if not schemes:
        return "NO_RELEVANT_SCHEMES_FOUND"

    context_lines = []
    for i, scheme in enumerate(schemes):
        name = scheme.get("name", "Unknown Scheme")
        state = scheme.get("state", "All India")
        category = scheme.get("category", "")
        ministry = scheme.get("ministry", "Various")
        details = scheme.get("details", scheme.get("description", str(scheme)))

        text = f"--- Scheme {i+1} ---\nName: {name}\nState: {state}\nCategory: {category}\nMinistry: {ministry}\nDetails: {details}\n"
        context_lines.append(text)

    return "\n\n".join(context_lines)