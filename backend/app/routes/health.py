import redis
from fastapi import APIRouter

from app.config import settings
from app.database import check_database_connection


router = APIRouter(prefix="/health", tags=["Health"])


@router.get("")
def health_check():
    return {
        "status": "healthy",
        "service": "finguard-ai-backend",
        "environment": settings.environment,
    }


@router.get("/database")
def database_health_check():
    is_connected = check_database_connection()

    return {
        "service": "postgresql",
        "connected": is_connected,
    }


@router.get("/redis")
def redis_health_check():
    try:
        client = redis.from_url(settings.redis_url)
        client.ping()

        return {
            "service": "redis",
            "connected": True,
        }
    except Exception as exc:
        return {
            "service": "redis",
            "connected": False,
            "error": str(exc),
        }
