"""Hermes Skill Registry — Pydantic request/response models"""
from __future__ import annotations
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class SkillBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=64, description="Skill name (lowercase, hyphens)")
    description: str = Field(..., min_length=1, max_length=1024)
    author: str = Field(default="anonymous", max_length=128)
    category: str = Field(default="uncategorized", max_length=64)
    tags: str = Field(default="", description="Comma-separated tags")
    version: str = Field(default="1.0.0")


class SkillCreate(SkillBase):
    skill_md: str = Field(..., description="Full SKILL.md content")


class SkillUpdate(BaseModel):
    description: Optional[str] = None
    tags: Optional[str] = None
    version: Optional[str] = None
    skill_md: Optional[str] = None


class SkillResponse(SkillBase):
    id: int
    downloads: int = 0
    stars: int = 0
    avg_rating: float = 0.0
    score: float = 0.0
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SkillDetail(SkillResponse):
    skill_md: str


class RatingCreate(BaseModel):
    score: int = Field(..., ge=1, le=5)
    review: Optional[str] = Field(default=None, max_length=2000)
    user_id: str = Field(default="anonymous", max_length=128)


class RatingResponse(BaseModel):
    id: int
    skill_id: int
    user_id: str
    score: int
    review: Optional[str]
    created_at: datetime


class SearchResponse(BaseModel):
    skills: list[SkillResponse]
    total: int
    page: int
    page_size: int


class TrendingResponse(BaseModel):
    skills: list[SkillResponse]
    period: str = "week"
