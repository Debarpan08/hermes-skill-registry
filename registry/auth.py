"""Hermes Skill Registry — Simple API key auth"""
from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader
from registry.config import PUBLISH_API_KEY

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def require_publish_key(api_key: str = Security(api_key_header)):
    if api_key != PUBLISH_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid or missing X-API-Key for publish operations"
        )
    return api_key
