from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Load Bible text
with open("bible_kjv.txt", "r", encoding="utf-8") as f:
    bible_text = f.read()

app = FastAPI()

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def search_scriptures(transcript, max_results=5):
    results = []
    transcript_words = set(transcript.lower().split())
    for line in bible_text.splitlines():
        line_words = set(line.lower().split())
        if transcript_words & line_words:
            results.append(line)
        if len(results) >= max_results:
            break
    return results

@app.post("/analyze")
async def analyze_transcript(request: Request):
    data = await request.json()
    transcript = data.get("text", "")
    matches = search_scriptures(transcript)
    return {"matches": matches}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
