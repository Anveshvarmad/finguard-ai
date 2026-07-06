from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.openai_service import OpenAIService


router = APIRouter(prefix="/ai", tags=["AI"])


class EmbeddingRequest(BaseModel):
    text: str


class ExplanationRequest(BaseModel):
    evidence: str


@router.post("/embedding-test")
def embedding_test(request: EmbeddingRequest):
    try:
        service = OpenAIService()
        embedding = service.generate_embedding(request.text)

        return {
            "status": "success",
            "model": "text-embedding-3-small",
            "embedding_dimensions": len(embedding),
            "sample_values": embedding[:8],
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"OpenAI embedding test failed: {str(exc)}",
        )


@router.post("/explanation-test")
def explanation_test(request: ExplanationRequest):
    try:
        service = OpenAIService()
        explanation = service.generate_compliance_explanation(request.evidence)

        return {
            "status": "success",
            "explanation": explanation,
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"OpenAI explanation test failed: {str(exc)}",
        )
