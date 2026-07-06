from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import IndexTransactionsResponse, VectorStatsResponse
from app.services.vector_store import VectorStoreService


router = APIRouter(prefix="/index", tags=["Vector Index"])


@router.post("/transactions", response_model=IndexTransactionsResponse)
def index_transactions(
    limit: int = Query(default=500, ge=1, le=2000),
    db: Session = Depends(get_db),
):
    service = VectorStoreService()
    result = service.index_transactions(db=db, limit=limit)

    return IndexTransactionsResponse(
        status="success",
        indexed_count=result["indexed_count"],
        indexed_ids=result["indexed_ids"],
    )


@router.get("/stats", response_model=VectorStatsResponse)
def get_vector_index_stats():
    service = VectorStoreService()
    return service.get_collection_stats()


@router.delete("/reset")
def reset_vector_index():
    service = VectorStoreService()
    return service.reset_collection()
