"""Hermes Skill Registry — Rating endpoints"""
from fastapi import APIRouter, Depends, HTTPException, Query
from registry.database import get_db, add_rating, get_ratings, toggle_star, get_skill
from registry.schemas import RatingCreate
from registry.auth import require_publish_key

router = APIRouter(prefix="/skills", tags=["ratings"])


@router.post("/{skill_id}/rate")
async def rate_skill(
    skill_id: int,
    rating: RatingCreate,
    api_key=Depends(require_publish_key)
):
    db = await get_db()
    skill = await get_skill(db, skill_id)
    if not skill:
        await db.close()
        raise HTTPException(status_code=404, detail="Skill not found")
    rating_id = await add_rating(
        db, skill_id, rating.user_id, rating.score, rating.review
    )
    await db.close()
    return {
        "id": rating_id,
        "skill_id": skill_id,
        "score": rating.score,
        "review": rating.review
    }


@router.get("/{skill_id}/ratings")
async def list_ratings(skill_id: int, limit: int = Query(default=20, ge=1, le=100)):
    db = await get_db()
    ratings = await get_ratings(db, skill_id, limit)
    await db.close()
    return {"ratings": ratings, "count": len(ratings)}


@router.post("/{skill_id}/star")
async def star_skill(skill_id: int):
    db = await get_db()
    skill = await get_skill(db, skill_id)
    if not skill:
        await db.close()
        raise HTTPException(status_code=404, detail="Skill not found")
    stars = await toggle_star(db, skill_id)
    await db.close()
    return {"skill_id": skill_id, "stars": stars}
