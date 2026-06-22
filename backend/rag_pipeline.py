import os
import json
import faiss
from sentence_transformers import SentenceTransformer
from config import config

_index = None
_chunks = None
_embedding_model = None

def load_artifacts():
    global _index, _chunks, _embedding_model
    
    # 1. Safely locate and load the FAISS index
    index_file = "schemes.index"
    if config.INDEX_PATH != ".":
        index_file = os.path.join(config.INDEX_PATH, "schemes.index")
        
    print(f"Loading FAISS index from: {index_file}")
    _index = faiss.read_index(index_file)
    
    # 2. Load the JSON chunks metadata
    print(f"Loading chunks from: {config.CHUNKS_PATH}")
    with open(config.CHUNKS_PATH, "r", encoding="utf-8") as f:
        _chunks = json.load(f)
        
    # 3. Load the SentenceTransformer embedding model
    print(f"Loading embedding model: {config.EMBEDDING_MODEL}")
    _embedding_model = SentenceTransformer(config.EMBEDDING_MODEL)
        
    print(f"Successfully loaded {_index.ntotal} vectors and {len(_chunks)} schemes.")

def retrieve(query: str):
    global _index, _chunks, _embedding_model
    
    # Ensure artifacts are loaded before searching
    if _index is None or _chunks is None or _embedding_model is None:
        load_artifacts()
        
    # Generate numerical embedding for the user's text
    query_vector = _embedding_model.encode([query])
    
    # Search the FAISS index for the top K closest matches
    k = config.TOP_K_RETRIEVAL
    distances, indices = _index.search(query_vector, k)
    
    schemes = []
    scores = []
    
    # Map the numerical indices back to the actual JSON data
    for i, idx in enumerate(indices[0]):
        if idx == -1:
            continue
        
        score = float(distances[0][i])
        schemes.append(_chunks[idx])
        scores.append(score)
        
    return schemes, scores

def format_context(schemes: list, scores: list) -> str:
    if not schemes:
        return "NO_RELEVANT_SCHEMES_FOUND"
        
    context_lines = []
    for i, scheme in enumerate(schemes):
        # Extract fields safely (works even if some JSON fields are missing)
        name = scheme.get("name", "Unknown Scheme")
        state = scheme.get("state", "All India")
        category = scheme.get("category", "")
        ministry = scheme.get("ministry", "Various")
        details = scheme.get("details", scheme.get("description", str(scheme)))
        
        text = f"--- Scheme {i+1} ---\nName: {name}\nState: {state}\nCategory: {category}\nMinistry: {ministry}\nDetails: {details}\n"
        context_lines.append(text)
        
    return "\n\n".join(context_lines)