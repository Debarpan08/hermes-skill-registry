"""Hermes Skill Registry — Database setup and queries"""
from __future__ import annotations
import os
import aiosqlite
from datetime import datetime, timezone
from typing import Optional

# Use /tmp for Vercel (read-only filesystem except /tmp)
if os.getenv("VERCEL"):
    DATABASE = "/tmp/skills_registry.db"
else:
    DATABASE = "skills_registry.db"


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


async def get_db() -> aiosqlite.Connection:
    db = await aiosqlite.connect(DATABASE)
    db.row_factory = aiosqlite.Row
    await db.execute("PRAGMA journal_mode=WAL")
    await db.execute("PRAGMA foreign_keys=ON")
    return db


async def init_db():
    db = await get_db()
    await db.executescript("""
        CREATE TABLE IF NOT EXISTS skills (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT NOT NULL,
            author TEXT NOT NULL DEFAULT 'anonymous',
            category TEXT NOT NULL DEFAULT 'uncategorized',
            tags TEXT NOT NULL DEFAULT '',
            version TEXT NOT NULL DEFAULT '1.0.0',
            skill_md TEXT NOT NULL,
            downloads INTEGER NOT NULL DEFAULT 0,
            stars INTEGER NOT NULL DEFAULT 0,
            avg_rating REAL NOT NULL DEFAULT 0.0,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            UNIQUE(name, version)
        );

        CREATE TABLE IF NOT EXISTS ratings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            skill_id INTEGER NOT NULL,
            user_id TEXT NOT NULL DEFAULT 'anonymous',
            score INTEGER NOT NULL CHECK(score BETWEEN 1 AND 5),
            review TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY (skill_id) REFERENCES skills(id) ON DELETE CASCADE
        );

        CREATE INDEX IF NOT EXISTS idx_skills_category ON skills(category);
        CREATE INDEX IF NOT EXISTS idx_skills_tags ON skills(tags);
        CREATE INDEX IF NOT EXISTS idx_skills_author ON skills(author);
        CREATE INDEX IF NOT EXISTS idx_ratings_skill ON ratings(skill_id);
    """)
    await db.commit()
    await db.close()


async def create_skill(db, name, description, author, category, tags, version, skill_md) -> int:
    now = utcnow()
    cursor = await db.execute(
        """INSERT INTO skills (name, description, author, category, tags, version, skill_md, created_at, updated_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (name, description, author, category, tags, version, skill_md, now, now)
    )
    await db.commit()
    return cursor.lastrowid


async def get_skill(db, skill_id: int) -> Optional[dict]:
    async with db.execute("SELECT * FROM skills WHERE id = ?", (skill_id,)) as cursor:
        row = await cursor.fetchone()
        return dict(row) if row else None


async def get_skill_by_name(db, name: str, version: str = None) -> Optional[dict]:
    if version:
        async with db.execute(
            "SELECT * FROM skills WHERE name = ? AND version = ?", (name, version)
        ) as cursor:
            row = await cursor.fetchone()
            return dict(row) if row else None
    async with db.execute(
        "SELECT * FROM skills WHERE name = ? ORDER BY created_at DESC LIMIT 1", (name,)
    ) as cursor:
        row = await cursor.fetchone()
        return dict(row) if row else None


async def search_skills(db, query: str = "", category: str = "", tags: str = "",
                        sort: str = "score", page: int = 1, page_size: int = 20) -> tuple[list[dict], int]:
    where_clauses = []
    params = []

    if query:
        where_clauses.append("(name LIKE ? OR description LIKE ? OR author LIKE ?)")
        q = f"%{query}%"
        params.extend([q, q, q])
    if category:
        where_clauses.append("category = ?")
        params.append(category)
    if tags:
        for tag in tags.split(","):
            where_clauses.append("tags LIKE ?")
            params.append(f"%{tag.strip()}%")

    where = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""

    sort_col = {"score": "downloads + stars * 3 + avg_rating * 10",
                "newest": "created_at",
                "popular": "downloads",
                "rating": "avg_rating"}.get(sort, "downloads + stars * 3 + avg_rating * 10")
    order = "DESC"

    count_query = f"SELECT COUNT(*) FROM skills {where}"
    async with db.execute(count_query, params) as cursor:
        total = (await cursor.fetchone())[0]

    offset = (page - 1) * page_size
    data_query = f"SELECT * FROM skills {where} ORDER BY {sort_col} {order} LIMIT ? OFFSET ?"
    params.extend([page_size, offset])

    async with db.execute(data_query, params) as cursor:
        rows = await cursor.fetchall()

    return [dict(r) for r in rows], total


async def increment_downloads(db, skill_id: int):
    await db.execute("UPDATE skills SET downloads = downloads + 1 WHERE id = ?", (skill_id,))
    await db.commit()


async def add_rating(db, skill_id: int, user_id: str, score: int, review: str) -> int:
    now = utcnow()
    cursor = await db.execute(
        "INSERT INTO ratings (skill_id, user_id, score, review, created_at) VALUES (?, ?, ?, ?, ?)",
        (skill_id, user_id, score, review, now)
    )
    # Update avg_rating on skill
    await db.execute(
        """UPDATE skills SET avg_rating = (SELECT AVG(score) FROM ratings WHERE skill_id = ?)
           WHERE id = ?""",
        (skill_id, skill_id)
    )
    await db.commit()
    return cursor.lastrowid


async def get_ratings(db, skill_id: int, limit: int = 20) -> list[dict]:
    async with db.execute(
        "SELECT * FROM ratings WHERE skill_id = ? ORDER BY created_at DESC LIMIT ?",
        (skill_id, limit)
    ) as cursor:
        rows = await cursor.fetchall()
    return [dict(r) for r in rows]


async def toggle_star(db, skill_id: int) -> int:
    """Toggle star for demo — in production this needs per-user tracking."""
    await db.execute("UPDATE skills SET stars = stars + 1 WHERE id = ?", (skill_id,))
    await db.commit()
    async with db.execute("SELECT stars FROM skills WHERE id = ?", (skill_id,)) as cursor:
        row = await cursor.fetchone()
    return row[0] if row else 0


async def get_trending(db, days: int = 7, limit: int = 10) -> list[dict]:
    """Skills with most activity in the last N days."""
    async with db.execute(
        """SELECT s.*, COUNT(r.id) as recent_ratings
           FROM skills s
           LEFT JOIN ratings r ON r.skill_id = s.id
             AND r.created_at >= datetime('now', ?)
           GROUP BY s.id
           ORDER BY recent_ratings DESC, s.downloads DESC
           LIMIT ?""",
        (f"-{days} days", limit)
    ) as cursor:
        rows = await cursor.fetchall()
    return [dict(r) for r in rows]


async def update_skill(db, skill_id: int, **fields):
    allowed = {"description", "tags", "version", "skill_md"}
    updates = {k: v for k, v in fields.items() if k in allowed and v is not None}
    if not updates:
        return False
    updates["updated_at"] = utcnow()
    set_clause = ", ".join(f"{k} = ?" for k in updates)
    values = list(updates.values()) + [skill_id]
    await db.execute(f"UPDATE skills SET {set_clause} WHERE id = ?", values)
    await db.commit()
    return True


async def delete_skill(db, skill_id: int):
    await db.execute("DELETE FROM ratings WHERE skill_id = ?", (skill_id,))
    await db.execute("DELETE FROM skills WHERE id = ?", (skill_id,))
    await db.commit()
