from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import RiskAlert
from app.schemas import AlertResponse, AlertStatusUpdate


router = APIRouter(prefix="/alerts", tags=["Alerts"])


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


@router.get("/{alert_id}", response_model=AlertResponse)
def get_alert(alert_id: str, db: Session = Depends(get_db)):
    alert = db.query(RiskAlert).filter(RiskAlert.alert_id == alert_id).first()

    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    return alert


@router.patch("/{alert_id}/status", response_model=AlertResponse)
def update_alert_status(
    alert_id: str,
    payload: AlertStatusUpdate,
    db: Session = Depends(get_db),
):
    alert = db.query(RiskAlert).filter(RiskAlert.alert_id == alert_id).first()

    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    alert.status = payload.status

    if payload.assigned_to is not None:
        alert.assigned_to = payload.assigned_to

    db.commit()
    db.refresh(alert)

    return alert
