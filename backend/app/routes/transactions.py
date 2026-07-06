from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import RiskAlert, Transaction, Vendor
from app.schemas import TransactionCreate, TransactionResponse


router = APIRouter(prefix="/transactions", tags=["Transactions"])


def get_or_create_vendor(db: Session, vendor_name: str, country: str) -> Vendor:
    vendor = db.query(Vendor).filter(Vendor.name == vendor_name).first()

    if vendor:
        return vendor

    vendor = Vendor(
        vendor_id=f"VEN-{uuid4().hex[:8].upper()}",
        name=vendor_name,
        country=country,
        industry="Financial Services",
        risk_rating="Low",
    )

    db.add(vendor)
    db.flush()

    return vendor


def create_alert_for_transaction(db: Session, transaction: Transaction) -> RiskAlert | None:
    if transaction.risk_score < 61:
        return None

    alert = RiskAlert(
        alert_id=f"ALT-{uuid4().hex[:10].upper()}",
        transaction_db_id=transaction.id,
        transaction_id=transaction.transaction_id,
        risk_level=transaction.risk_level,
        risk_score=transaction.risk_score,
        risk_flags=transaction.risk_flags,
        alert_reason=", ".join(transaction.risk_flags)
        if transaction.risk_flags
        else "Transaction exceeded risk threshold",
        status="Open",
    )

    db.add(alert)

    return alert


@router.post("", response_model=TransactionResponse)
def create_transaction(payload: TransactionCreate, db: Session = Depends(get_db)):
    external_id = payload.transaction_id or f"TXN-{uuid4().hex[:10].upper()}"

    existing = db.query(Transaction).filter(Transaction.transaction_id == external_id).first()

    if existing:
        raise HTTPException(status_code=409, detail="Transaction already exists")

    vendor = get_or_create_vendor(db, payload.vendor_name, payload.country)

    data = payload.model_dump(exclude_none=True)
    data["transaction_id"] = external_id
    data["vendor_id"] = vendor.id

    transaction = Transaction(**data)

    db.add(transaction)
    db.flush()

    create_alert_for_transaction(db, transaction)

    vendor.total_payment_volume += transaction.amount

    vendor_transactions = db.query(Transaction).filter(Transaction.vendor_id == vendor.id).all()
    if vendor_transactions:
        total_risk = sum(item.risk_score for item in vendor_transactions) + transaction.risk_score
        vendor.average_risk_score = round(total_risk / (len(vendor_transactions) + 1), 2)

    if transaction.risk_score >= 81:
        vendor.risk_rating = "Critical"
    elif transaction.risk_score >= 61 and vendor.risk_rating not in ["Critical"]:
        vendor.risk_rating = "High"
    elif transaction.risk_score >= 31 and vendor.risk_rating not in ["High", "Critical"]:
        vendor.risk_rating = "Medium"

    db.commit()
    db.refresh(transaction)

    return transaction


@router.get("", response_model=list[TransactionResponse])
def list_transactions(
    risk_level: str | None = None,
    department: str | None = None,
    vendor: str | None = None,
    payment_method: str | None = None,
    category: str | None = None,
    min_amount: float | None = None,
    max_amount: float | None = None,
    limit: int = Query(default=50, le=200),
    db: Session = Depends(get_db),
):
    query = db.query(Transaction)

    if risk_level:
        query = query.filter(Transaction.risk_level == risk_level)

    if department:
        query = query.filter(Transaction.department == department)

    if vendor:
        query = query.filter(Transaction.vendor_name.ilike(f"%{vendor}%"))

    if payment_method:
        query = query.filter(Transaction.payment_method == payment_method)

    if category:
        query = query.filter(Transaction.category == category)

    if min_amount is not None:
        query = query.filter(Transaction.amount >= min_amount)

    if max_amount is not None:
        query = query.filter(Transaction.amount <= max_amount)

    return query.order_by(Transaction.timestamp.desc()).limit(limit).all()


@router.get("/recent/feed", response_model=list[TransactionResponse])
def get_recent_transaction_feed(
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return (
        db.query(Transaction)
        .order_by(Transaction.timestamp.desc())
        .limit(limit)
        .all()
    )


@router.get("/{transaction_id}", response_model=TransactionResponse)
def get_transaction(transaction_id: str, db: Session = Depends(get_db)):
    transaction = (
        db.query(Transaction)
        .filter(Transaction.transaction_id == transaction_id)
        .first()
    )

    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    return transaction
