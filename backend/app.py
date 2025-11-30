# backend/app.py

from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from routers.polls import router as polls_router  # polls API routes


# Main FastAPI app
app = FastAPI(title="Would You Rather API")

# Attach polls router (/polls endpoints)
app.include_router(polls_router)


@app.get("/")
def root():
    """Simple health check/root message."""
    return {"message": "Would You Rather API is running"}


# Static files (frontend)
static_path = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=str(static_path)), name="static")


@app.get("/play")
def play():
    """Serve the simple UI that talks to the polls API."""
    index_path = static_path / "index.html"
    return FileResponse(index_path)
