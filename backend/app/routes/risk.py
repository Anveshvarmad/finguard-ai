from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import RiskRule, Vendor
from app.schemas import RiskEvaluationResponse, RiskRuleResponse, TransactionCreate
from app.services.risk_engine import RiskScoringEngine


router = APIRouter(prefix="/risk", tags=["Risk Engine"])


@router.post("/rules/seed")
def seed_risk_rules(db: Session = Depends(get_db)):
    engine = RiskScoringEngine()
    result = engine.seed_default_rules(db)

    return {
        "status": "success",
        "message": "Default risk rules are ready.",
        **result,
    }


@router.get("/rules", response_model=list[RiskRuleResponse])
def list_risk_rules(db: Session = Depends(get_db)):
    return db.query(RiskRule).order_by(RiskRule.id.asc()).all()


@router.post("/evaluate", response_model=RiskEvaluationResponse)
def evaluate_transaction_risk(
    payload: TransactionCreate,
    db: Session = Depends(get_db),
):
    vendor = db.query(Vendor).filter(Vendor.name == payload.vendor_name).first()

    engine = RiskScoringEngine()

    result = engine.evaluate(
        db=db,
        payload=payload.model_dump(),
        vendor=vendor,
        exclude_transaction_id=payload.transaction_id,
    )

    return result
