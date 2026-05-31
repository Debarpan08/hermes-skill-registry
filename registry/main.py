"""Hermes Skill Registry — FastAPI main application"""
import os
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from registry.database import init_db
from registry.seed import seed_database
from registry.api.skills import router as skills_router
from registry.api.ratings import router as ratings_router
from registry.api.search import router as search_router


# Path to static files directory — works from both root and Vercel deployment
STATIC_DIR = Path(__file__).parent / "static"
if not STATIC_DIR.exists():
    # Fallback for Vercel where cwd may differ
    STATIC_DIR = Path(__file__).parent.parent / "registry" / "static"


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    await seed_database()
    print("Database initialized and seeded")
    yield


app = FastAPI(
    title="Hermes Skill Registry",
    description="npm for Hermes skills — publish, discover, install, rate",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(skills_router, prefix="/api/v1")
app.include_router(ratings_router, prefix="/api/v1")
app.include_router(search_router, prefix="/api/v1")

# Mount static assets
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/health")
async def health():
    return {"status": "ok", "service": "hermes-skill-registry"}


@app.get("/")
async def root():
    """Serve the web UI."""
    index_path = STATIC_DIR / "index.html"
    if index_path.exists():
        return FileResponse(str(index_path), media_type="text/html")
    return {
        "service": "Hermes Skill Registry",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "search": "/api/v1/search?q=&category=&tags=&sort=",
            "trending": "/api/v1/trending",
            "skills": "/api/v1/skills",
            "ratings": "/api/v1/skills/{id}/ratings",
            "publish": "POST /api/v1/skills",
            "install": "GET /api/v1/skills/{id}/download",
        }
    }


if __name__ == "__main__":
    import uvicorn
    from registry.config import API_HOST, API_PORT
    uvicorn.run(app, host=API_HOST, port=API_PORT)
