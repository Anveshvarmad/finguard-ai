import redis
from fastapi import APIRouter

from app.config import settings
from app.database import SessionLocal, check_database_connection
from app.models import RiskAlert, Transaction, Vendor
from app.services.vector_store import VectorStoreService


router = APIRouter(prefix="/system", tags=["System"])


@router.get("/status")
def system_status():
    db_connected = check_database_connection()

    redis_connected = False
    redis_error = None

    try:
        client = redis.from_url(settings.redis_url)
        client.ping()
        redis_connected = True
    except Exception as exc:
        redis_error = str(exc)

    vector_count = 0
    vector_status = "unavailable"

    try:
        vector_stats = VectorStoreService().get_collection_stats()
        vector_count = vector_stats["vector_count"]
        vector_status = "ready"
    except Exception as exc:
        vector_status = f"error: {str(exc)}"

    db = SessionLocal()

    try:
        transaction_count = db.query(Transaction).count()
        vendor_count = db.query(Vendor).count()
        alert_count = db.query(RiskAlert).count()
        open_alert_count = db.query(RiskAlert).filter(RiskAlert.status == "Open").count()
    finally:
        db.close()

    openai_configured = (
        bool(settings.openai_api_key)
        and settings.openai_api_key != "your_openai_api_key_here"
    )

    return {
        "service": "FinGuard AI",
        "environment": settings.environment,
        "status": "ready" if db_connected and redis_connected else "degraded",
        "dependencies": {
            "postgresql": {
                "connected": db_connected,
            },
            "redis": {
                "connected": redis_connected,
                "error": redis_error,
            },
            "openai": {
                "configured": openai_configured,
                "embedding_model": settings.openai_embedding_model,
                "chat_model": settings.openai_chat_model,
            },
            "chroma": {
                "status": vector_status,
                "collection_name": settings.chroma_collection_name,
                "vector_count": vector_count,
            },
        },
        "data": {
            "transactions": transaction_count,
            "vendors": vendor_count,
            "alerts": alert_count,
            "open_alerts": open_alert_count,
        },
    }


@router.get("/version")
def system_version():
    return {
        "name": "FinGuard AI",
        "version": "1.0.0",
        "description": "Real-time AI compliance intelligence platform",
        "stack": [
            "FastAPI",
            "React",
            "PostgreSQL",
            "Redis",
            "ChromaDB",
            "OpenAI APIs",
            "Docker",
        ],
    }
