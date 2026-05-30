"""Hermes Skill Registry — Search and discovery endpoints"""
from fastapi import APIRouter, Query
from registry.database import get_db, search_skills, get_trending
from registry.schemas import SearchResponse

router = APIRouter(tags=["search"])


@router.get("/search", response_model=SearchResponse, tags=["search"])
async def search(
    q: str = Query(default="", description="Search in name, description, author"),
    category: str = Query(default="", description="Filter by category"),
    tags: str = Query(default="", description="Comma-separated tags to filter"),
    sort: str = Query(
        default="score",
        regex="^(score|newest|popular|rating)$",
        description="Sort order: score, newest, popular, rating"
    ),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
):
    db = await get_db()
    skills, total = await search_skills(db, q, category, tags, sort, page, page_size)
    await db.close()
    return SearchResponse(skills=skills, total=total, page=page, page_size=page_size)


@router.get("/trending", tags=["search"])
async def trending(
    days: int = Query(default=7, ge=1, le=30),
    limit: int = Query(default=10, ge=1, le=50),
):
    from registry.database import get_trending
    db = await get_db()
    skills = await get_trending(db, days=days, limit=limit)
    await db.close()
    return {"skills": skills, "period": f"{days}d"}
