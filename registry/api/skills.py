"""Hermes Skill Registry — Skill CRUD endpoints"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from registry.database import (
    get_db, create_skill, get_skill, search_skills,
    update_skill, delete_skill, increment_downloads
)
from registry.schemas import SkillCreate, SkillUpdate, SkillResponse, SkillDetail, SearchResponse
from registry.auth import require_publish_key

router = APIRouter(prefix="/skills", tags=["skills"])


@router.get("/search", response_model=SearchResponse)
async def search(
    q: str = Query(default="", description="Search query"),
    category: str = Query(default=""),
    tags: str = Query(default=""),
    sort: str = Query(default="score", description="Sort: score, newest, popular, rating"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
):
    db = await get_db()
    skills, total = await search_skills(db, q, category, tags, sort, page, page_size)
    await db.close()
    return SearchResponse(skills=skills, total=total, page=page, page_size=page_size)


@router.get("/trending")
async def trending(limit: int = Query(default=10, ge=1, le=50)):
    from registry.database import get_trending
    db = await get_db()
    skills = await get_trending(db, limit=limit)
    await db.close()
    return {"skills": skills, "period": "week"}


@router.get("/{skill_id}", response_model=SkillDetail)
async def get_one(skill_id: int):
    db = await get_db()
    skill = await get_skill(db, skill_id)
    await db.close()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    return skill


@router.get("/{skill_id}/download")
async def download(skill_id: int):
    db = await get_db()
    skill = await get_skill(db, skill_id)
    if not skill:
        await db.close()
        raise HTTPException(status_code=404, detail="Skill not found")
    await increment_downloads(db, skill_id)
    await db.close()
    return {"skill_md": skill["skill_md"], "name": skill["name"], "version": skill["version"], "category": skill.get("category", "uncategorized")}


@router.post("/", response_model=SkillResponse, status_code=status.HTTP_201_CREATED)
async def publish(skill: SkillCreate, api_key=Depends(require_publish_key)):
    db = await get_db()
    try:
        skill_id = await create_skill(
            db,
            name=skill.name,
            description=skill.description,
            author=skill.author,
            category=skill.category,
            tags=skill.tags,
            version=skill.version,
            skill_md=skill.skill_md,
        )
    except Exception as e:
        await db.close()
        if "UNIQUE constraint" in str(e):
            raise HTTPException(status_code=409, detail=f"Skill '{skill.name}' v{skill.version} already exists. Use PUT to update.")
        raise HTTPException(status_code=400, detail=str(e))
    created = await get_skill(db, skill_id)
    await db.close()
    return created


@router.put("/{skill_id}", response_model=SkillResponse)
async def update(skill_id: int, update: SkillUpdate, api_key=Depends(require_publish_key)):
    db = await get_db()
    updated = await update_skill(db, skill_id, **update.model_dump(exclude_unset=True))
    if not updated:
        await db.close()
        raise HTTPException(status_code=404, detail="Skill not found or nothing to update")
    skill = await get_skill(db, skill_id)
    await db.close()
    return skill


@router.delete("/{skill_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove(skill_id: int, api_key=Depends(require_publish_key)):
    db = await get_db()
    skill = await get_skill(db, skill_id)
    if not skill:
        await db.close()
        raise HTTPException(status_code=404, detail="Skill not found")
    await delete_skill(db, skill_id)
    await db.close()
