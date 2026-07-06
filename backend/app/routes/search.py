from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import SearchRequest, SemanticSearchResponse
from app.services.vector_store import VectorStoreService


router = APIRouter(prefix="/search", tags=["Semantic Search"])


@router.post("/semantic", response_model=SemanticSearchResponse)
def semantic_search(
    payload: SearchRequest,
    db: Session = Depends(get_db),
):
    service = VectorStoreService()

    return service.semantic_search(
        db=db,
        query=payload.query,
        top_k=payload.top_k,
        risk_level=payload.risk_level,
        department=payload.department,
        vendor=payload.vendor,
        payment_method=payload.payment_method,
        category=payload.category,
        country=payload.country,
        min_amount=payload.min_amount,
        max_amount=payload.max_amount,
    )
