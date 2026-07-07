from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import Base, engine
from app import models
from app.routes import (
    ai,
    alerts,
    analytics,
    health,
    indexing,
    risk,
    search,
    seed,
    simulate,
    system,
    transactions,
    vendors,
    websocket_feed,
)


Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="FinGuard AI",
    description="Real-time AI compliance intelligence platform using FastAPI, PostgreSQL, Redis, ChromaDB, React, and OpenAI APIs.",
    version="1.0.0",
)

cors_origins = [
    origin.strip()
    for origin in settings.cors_origins.split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(ai.router)
app.include_router(vendors.router)
app.include_router(transactions.router)
app.include_router(alerts.router)
app.include_router(seed.router)
app.include_router(simulate.router)
app.include_router(risk.router)
app.include_router(indexing.router)
app.include_router(search.router)
app.include_router(analytics.router)
app.include_router(websocket_feed.router)
app.include_router(system.router)


@app.get("/")
def root():
    return {
        "message": "FinGuard AI backend is running",
        "docs": "/docs",
        "system_status": "/system/status",
    }
