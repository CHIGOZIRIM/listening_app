# Continuous Bible Reference Finder

This is a full-stack web app that:

- Captures speech from the browser continuously
- Converts speech to text
- Sends transcript every 60 seconds to backend
- Backend searches the KJV Bible for relevant scriptures
- Returns and displays possible scripture matches in real-time

## Deployment

### Backend (FastAPI)

1. Deploy on Render.com, Railway, or Fly.io.
2. Install dependencies:

pip install -r backend/requirements.txt


3. Start server:



uvicorn backend.main:app --host 0.0.0.0 --port 8000


4. Get public URL and use it in `frontend/index.html`.

### Frontend

1. Host on Netlify, GitHub Pages, or Vercel.
2. Open `index.html` in browser. Ensure backend URL is correctly set.

### Usage

- Click **Start Recording** in the browser
- Speak continuously
- Every 60 seconds, the app will check for Bible references and display them