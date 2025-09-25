from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

# ==========================
# Load Bible Text
# ==========================
BASE_DIR = os.path.dirname(__file__)
with open(os.path.join(BASE_DIR, "bible_kjv.txt"), "r", encoding="utf-8") as f:
    bible_text = f.read()

# Split into verses
verses = [line.strip() for line in bible_text.splitlines() if line.strip()]

# ==========================
# Load Embedding Model
# ==========================
# Small but effective model; can swap for larger models for better semantic understanding
model = SentenceTransformer('all-MiniLM-L6-v2')

# Compute embeddings for all verses
print("Computing verse embeddings...")
verse_embeddings = model.encode(verses, convert_to_numpy=True, show_progress_bar=True)

# Build FAISS index
embedding_dim = verse_embeddings.shape[1]
index = faiss.IndexFlatL2(embedding_dim)
index.add(verse_embeddings)
print(f"FAISS index built with {len(verses)} verses.")

# ==========================
# FastAPI App
# ==========================
app = FastAPI()

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"status": "ok"}

# ==========================
# RAG-style search function
# ==========================
def search_scriptures(query, max_results=5):
    # Step 1: Embed query
    query_vec = model.encode([query], convert_to_numpy=True)

    # Step 2: Search FAISS index
    distances, indices = index.search(query_vec, max_results)

    # Step 3: Return top results
    results = []
    for i, idx in enumerate(indices[0]):
        verse = verses[idx]
        results.append({"verse": verse, "score": float(distances[0][i])})
    return results

# ==========================
# API Endpoint
# ==========================
@app.post("/analyze")
async def analyze_transcript(request: Request):
    data = await request.json()
    transcript = data.get("text", "")
    matches = search_scriptures(transcript)
    return {"matches": matches}

# ==========================
# Run the app
# ==========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
