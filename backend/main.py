from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
from openai import OpenAI

BASE_DIR = os.path.dirname(__file__)
with open(os.path.join(BASE_DIR, "bible_kjv.txt"), "r", encoding="utf-8") as f:
    bible_text = f.read()

# Load verses (string)
verses = [line.strip() for line in bible_text.splitlines() if line.strip()]

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/analyze")
async def analyze_transcript(request: Request):
    data = await request.json()
    query = data.get("text", "")

    # Construct a system prompt with all verses (may need truncation if too big)
    # For 31k verses, you can instead load just book/chapter indexes dynamically
    system_prompt = (
        "You are a Bible assistant. "
        "Given a user query, select the top 5 most relevant bible verses and output them to the user\n\n"
        # + "\n".join(verses[:5000])  # ⚠️ truncate for context window
    )

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Find the 5 most relevant bible verses for: {query}"}
        ]
    )

    return {"answer": completion.choices[0].message.content}
