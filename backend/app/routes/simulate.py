from fastapi import APIRouter, BackgroundTasks, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import TransactionResponse
from app.services.transaction_generator import SIMULATION_PATTERNS, TransactionGenerator


router = APIRouter(prefix="/simulate", tags=["Simulation"])


@router.get("/patterns")
def get_simulation_patterns():
    return {
        "patterns": SIMULATION_PATTERNS,
        "description": "Available fake transaction patterns used by the simulator.",
    }


@router.post("/transaction", response_model=TransactionResponse)
def simulate_single_transaction(db: Session = Depends(get_db)):
    generator = TransactionGenerator()
    transaction = generator.generate_transaction(db)

    return transaction


@router.post("/batch", response_model=list[TransactionResponse])
def simulate_batch_transactions(
    count: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    generator = TransactionGenerator()
    transactions = generator.generate_batch(db, count)

    return transactions


@router.post("/live")
def start_live_simulation(
    background_tasks: BackgroundTasks,
    count: int = Query(default=20, ge=1, le=500),
    delay_seconds: float = Query(default=1.0, ge=0.2, le=10.0),
):
    generator = TransactionGenerator()

    background_tasks.add_task(
        generator.run_background_stream,
        count,
        delay_seconds,
    )

    return {
        "status": "started",
        "message": "Background transaction simulation started.",
        "count": count,
        "delay_seconds": delay_seconds,
    }
