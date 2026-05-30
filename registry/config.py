"""Hermes Skill Registry - Configuration"""
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./skills_registry.db")

# Use /tmp for Vercel (read-only filesystem)
if os.getenv("VERCEL"):
    DATABASE_URL = "sqlite+aiosqlite:////tmp/skills_registry.db"
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))
REGISTRY_URL = os.getenv("REGISTRY_URL", "http://localhost:8000")
PUBLISH_API_KEY = os.getenv("PUBLISH_API_KEY", "hermes-dev-key-2026")
