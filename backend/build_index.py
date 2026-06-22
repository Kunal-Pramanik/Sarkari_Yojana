"""
Run this ONCE to build the FAISS index from the CSV.
Usage: python build_index.py
"""
import faiss
import pickle
import numpy as np
import os
from preprocess import load_and_preprocess
from embeddings import embed_texts
from config import config

def build_faiss_index():
    # 1. Load & preprocess
    schemes = load_and_preprocess(config.DATA_PATH)

    # 2. Save schemes
    with open(config.CHUNKS_PATH, 'wb') as f:
        pickle.dump(schemes, f)
    print(f"Saved {len(schemes)} schemes.")

    # 3. Embed all schemes
    print("Embedding all schemes (this takes ~2-3 minutes first time)...")
    texts = [s['embed_text'] for s in schemes]
    embeddings = embed_texts(texts)
    print(f"Embeddings shape: {embeddings.shape}")

    # 4. Build FAISS index (Inner Product = cosine since normalized)
    dim = embeddings.shape[1]
    index = faiss.IndexFlatIP(dim)   # exact cosine similarity
    index.add(embeddings)
    print(f"FAISS index built with {index.ntotal} vectors.")

    # 5. Save index
    os.makedirs(config.INDEX_PATH, exist_ok=True)
    faiss.write_index(index, f"{config.INDEX_PATH}/schemes.index")
    print(f"Index saved to {config.INDEX_PATH}/schemes.index")
    print("\n✅ Done! You can now run the backend server.")

if __name__ == "__main__":
    build_faiss_index()