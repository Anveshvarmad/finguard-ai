from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import InvestigationNote, RiskAlert, Transaction
from app.schemas import (
    AlertExplanationResponse,
    AlertInvestigationResponse,
    AlertResponse,
    AlertStatusUpdate,
    InvestigationNoteCreate,
    InvestigationNoteResponse,
    TransactionResponse,
)
from app.services.investigation_service import InvestigationService


router = APIRouter(prefix="/alerts", tags=["Alerts"])


def get_alert_or_404(db: Session, alert_id: str) -> RiskAlert:
    alert = db.query(RiskAlert).filter(RiskAlert.alert_id == alert_id).first()

    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    return alert


def get_transaction_or_404(db: Session, transaction_id: str) -> Transaction:
    transaction = (
        db.query(Transaction)
        .filter(Transaction.transaction_id == transaction_id)
        .first()
    )

    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    return transaction


@router.get("", response_model=list[AlertResponse])
def list_alerts(
    status: str | None = None,
    risk_level: str | None = None,
    limit: int = Query(default=50, le=200),
    db: Session = Depends(get_db),
):
    query = db.query(RiskAlert)

    if status:
        query = query.filter(RiskAlert.status == status)

    if risk_level:
        query = query.filter(RiskAlert.risk_level == risk_level)

    return query.order_by(RiskAlert.created_at.desc()).limit(limit).all()


@router.get("/recent/feed", response_model=list[AlertResponse])
def get_recent_alert_feed(
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return (
        db.query(RiskAlert)
        .order_by(RiskAlert.created_at.desc())
        .limit(limit)
        .all()
    )


@router.get("/{alert_id}/notes", response_model=list[InvestigationNoteResponse])
def list_investigation_notes(
    alert_id: str,
    db: Session = Depends(get_db),
):
    get_alert_or_404(db, alert_id)

    return (
        db.query(InvestigationNote)
        .filter(InvestigationNote.alert_id == alert_id)
        .order_by(InvestigationNote.created_at.desc())
        .all()
    )


@router.post("/{alert_id}/notes", response_model=InvestigationNoteResponse)
def create_investigation_note(
    alert_id: str,
    payload: InvestigationNoteCreate,
    db: Session = Depends(get_db),
):
    alert = get_alert_or_404(db, alert_id)

    note = InvestigationNote(
        alert_id=alert.alert_id,
        transaction_id=alert.transaction_id,
        author=payload.author,
        note=payload.note,
    )

    db.add(note)
    db.commit()
    db.refresh(note)

    return note


@router.get("/{alert_id}/related-transactions", response_model=list[TransactionResponse])
def get_related_transactions(
    alert_id: str,
    limit: int = Query(default=8, ge=1, le=25),
    db: Session = Depends(get_db),
):
    alert = get_alert_or_404(db, alert_id)
    transaction = get_transaction_or_404(db, alert.transaction_id)

    service = InvestigationService()

    return service.get_related_transactions(
        db=db,
        transaction=transaction,
        limit=limit,
    )


@router.post("/{alert_id}/ai-explanation", response_model=AlertExplanationResponse)
def generate_alert_ai_explanation(
    alert_id: str,
    db: Session = Depends(get_db),
):
    alert = get_alert_or_404(db, alert_id)
    transaction = get_transaction_or_404(db, alert.transaction_id)

    service = InvestigationService()
    result = service.generate_ai_explanation(alert, transaction)

    return AlertExplanationResponse(
        alert_id=alert.alert_id,
        transaction_id=transaction.transaction_id,
        mode=result["mode"],
        explanation=result["explanation"],
        evidence=result["evidence"],
    )


@router.get("/{alert_id}/investigation", response_model=AlertInvestigationResponse)
def get_alert_investigation(
    alert_id: str,
    db: Session = Depends(get_db),
):
    alert = get_alert_or_404(db, alert_id)
    transaction = get_transaction_or_404(db, alert.transaction_id)

    notes = (
        db.query(InvestigationNote)
        .filter(InvestigationNote.alert_id == alert_id)
        .order_by(InvestigationNote.created_at.desc())
        .all()
    )

    service = InvestigationService()
    related_transactions = service.get_related_transactions(db, transaction)
    timeline = service.build_timeline(alert, transaction, notes)
    ai_result = service.generate_ai_explanation(alert, transaction)

    return AlertInvestigationResponse(
        alert=alert,
        transaction=transaction,
        notes=notes,
        timeline=timeline,
        related_transactions=related_transactions,
        ai_mode=ai_result["mode"],
        ai_explanation=ai_result["explanation"],
        evidence=ai_result["evidence"],
    )


@router.get("/{alert_id}", response_model=AlertResponse)
def get_alert(alert_id: str, db: Session = Depends(get_db)):
    return get_alert_or_404(db, alert_id)


@router.patch("/{alert_id}/status", response_model=AlertResponse)
def update_alert_status(
    alert_id: str,
    payload: AlertStatusUpdate,
    db: Session = Depends(get_db),
):
    alert = get_alert_or_404(db, alert_id)

    previous_status = alert.status
    alert.status = payload.status

    if payload.assigned_to is not None:
        alert.assigned_to = payload.assigned_to

    status_note = InvestigationNote(
        alert_id=alert.alert_id,
        transaction_id=alert.transaction_id,
        author=payload.assigned_to or "Compliance Analyst",
        note=(
            f"Alert status changed from {previous_status} to {payload.status}."
        ),
    )

    db.add(status_note)
    db.commit()
    db.refresh(alert)

    return alert
