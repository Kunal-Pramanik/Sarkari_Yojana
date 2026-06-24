"""Run this ONCE locally to pre-build the FAISS index with embeddings saved."""
import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from config import config

print("Loading chunks...")
with open(config.CHUNKS_PATH, "r", encoding="utf-8") as f:
    chunks = json.load(f)

print(f"Loaded {len(chunks)} schemes. Building embeddings...")
model = SentenceTransformer(config.EMBEDDING_MODEL)

texts = []
for chunk in chunks:
    text = f"{chunk.get('name','')} {chunk.get('category','')} {chunk.get('details', chunk.get('description',''))}"
    texts.append(text[:512])

print("Encoding all schemes (this may take a few minutes)...")
embeddings = model.encode(texts, batch_size=64, show_progress_bar=True)
embeddings = np.array(embeddings).astype("float32")

print("Building FAISS index...")
dimension = embeddings.shape[1]
index = faiss.IndexFlatIP(dimension)
faiss.normalize_L2(embeddings)
index.add(embeddings)

print("Saving index and embeddings...")
faiss.write_index(index, "schemes.index")
np.save("schemes_embeddings.npy", embeddings)

print(f"Done! {index.ntotal} vectors saved.")
print(f"schemes.index size: {os.path.getsize('schemes.index') / 1024 / 1024:.1f} MB")