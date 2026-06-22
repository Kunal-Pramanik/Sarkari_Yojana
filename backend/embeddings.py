"""
Embedding model wrapper.
Uses paraphrase-multilingual-MiniLM (supports Hindi + English).
"""
from sentence_transformers import SentenceTransformer
import numpy as np
from config import config

_model = None

def get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        print(f"Loading embedding model: {config.EMBEDDING_MODEL}")
        _model = SentenceTransformer(config.EMBEDDING_MODEL)
    return _model

def embed_texts(texts: list[str]) -> np.ndarray:
    """Batch encode a list of strings. Returns (N, dim) float32 array."""
    model = get_model()
    embeddings = model.encode(
        texts,
        batch_size=64,
        show_progress_bar=True,
        normalize_embeddings=True,   # cosine similarity via dot product
        convert_to_numpy=True,
    )
    return embeddings.astype(np.float32)

def embed_query(query: str) -> np.ndarray:
    """Encode a single query string."""
    model = get_model()
    vec = model.encode(
        query,
        normalize_embeddings=True,
        convert_to_numpy=True,
    )
    return vec.astype(np.float32).reshape(1, -1)