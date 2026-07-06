from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app import models
from app.routes import ai, alerts, health, indexing, risk, search, seed, simulate, transactions, vendors


Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="FinGuard AI",
    description="Real-time AI compliance intelligence platform using FastAPI, PostgreSQL, Redis, ChromaDB, React, and OpenAI APIs.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
    ],
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


@app.get("/")
def root():
    return {
        "message": "FinGuard AI backend is running",
        "docs": "/docs",
    }
