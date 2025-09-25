from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
import hnswlib
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
model = SentenceTransformer('all-MiniLM-L6-v2')

# Compute embeddings for all verses
print("Computing verse embeddings...")
verse_embeddings = model.encode(verses, convert_to_numpy=True, show_progress_bar=True)

# ==========================
# Build hnswlib index
# ==========================
embedding_dim = verse_embeddings.shape[1]
num_elements = len(verse_embeddings)

# Create index
index = hnswlib.Index(space='l2', dim=embedding_dim)
index.init_index(max_elements=num_elements, ef_construction=200, M=16)
index.add_items(verse_embeddings)
index.set_ef(50)  # query time parameter
print(f"hnswlib index built with {num_elements} verses.")

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

    # Step 2: Search hnswlib index
    indices, distances = index.knn_query(query_vec, k=max_results)

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
