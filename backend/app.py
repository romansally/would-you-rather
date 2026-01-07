# backend/app.py

from pathlib import Path
from dotenv import load_dotenv

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from routers.polls import router as polls_router
from db import init_db

# Load environment variables from .env file
# CRITICAL: This must happen BEFORE any code tries to access os.getenv()
load_dotenv()

# Main FastAPI app
app = FastAPI(title="Would You Rather API")

@app.on_event("startup")
def on_startup():
    init_db()

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
    """Serve the public voting UI."""
    index_path = static_path / "index.html"
    return FileResponse(index_path)


@app.get("/admin")
def admin():
    """Serve the admin UI (to be created in Step 2)."""
    admin_path = static_path / "admin.html"
    return FileResponse(admin_path)