from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes import health, ai


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


@app.get("/")
def root():
    return {
        "message": "FinGuard AI backend is running",
        "docs": "/docs",
    }
