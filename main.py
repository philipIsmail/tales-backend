from fastapi import FastAPI, Query
import requests
import os
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

app = FastAPI()

# Enable CORS so frontend can call backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://tales-frontend.onrender.com",  # future frontend
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

TMDB_V4_TOKEN = os.getenv("TMDB_V4_TOKEN")

HEADERS = {
    "Authorization": f"Bearer {TMDB_V4_TOKEN}",
    "accept": "application/json"
}

GENRE_MAP = {
    "happy": ["35", "16", "10751"],
    "sad": ["18"],
    "adventurous": ["12", "14", "878"],
    "romantic": ["10749", "18"],
    "nostalgic": ["16", "35", "10751"],
    "intense": ["53", "28", "80"],
    "fear": ["27", "9648"],
}

@app.get("/")
def home():
    return {"status": "ok"}

@app.get("/health")
def health():
    return {"status": "ok"}

# -------------------------
# Mood-based recommendations
# -------------------------
@app.get("/recommend/{mood}")
def recommend(mood: str):
    if mood not in GENRE_MAP:
        return {"error": "Mood not supported"}

    genre_ids = ",".join(GENRE_MAP[mood])

    url = (
        "https://api.themoviedb.org/3/discover/movie"
        f"?with_genres={genre_ids}"
        "&sort_by=popularity.desc"
        "&language=en-US"
        "&page=1"
    )

    response = requests.get(url, headers=HEADERS).json()

    return {
        "mood": mood,
        "results": response.get("results", [])[:10]
    }

# -------------------------
# Search endpoint (NEW)
# -------------------------
@app.get("/search")
def search_tales(q: str = Query(..., min_length=1)):
    url = "https://api.themoviedb.org/3/search/multi"
    params = {
        "query": q,
        "include_adult": False,
        "language": "en-US",
        "page": 1,
    }

    response = requests.get(url, headers=HEADERS, params=params).json()

    # Only return movies + TV shows
    results = [
        item for item in response.get("results", [])
        if item.get("media_type") in ["movie", "tv"]
    ]

    return {
        "query": q,
        "results": results[:10]
    }