from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, Query
from sqlalchemy import case, func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import RiskAlert, Transaction, Vendor
from app.schemas import (
    AlertResponse,
    AnalyticsBucket,
    DashboardOverview,
    DashboardSummary,
    TopVendorRisk,
    TransactionResponse,
    TrendPoint,
)


router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/summary", response_model=DashboardSummary)
def get_dashboard_summary(db: Session = Depends(get_db)):
    total_transactions = db.query(Transaction).count()
    total_vendors = db.query(Vendor).count()
    total_alerts = db.query(RiskAlert).count()

    open_alerts = (
        db.query(RiskAlert)
        .filter(RiskAlert.status == "Open")
        .count()
    )

    critical_alerts = (
        db.query(RiskAlert)
        .filter(RiskAlert.risk_level == "Critical")
        .count()
    )

    high_risk_transactions = (
        db.query(Transaction)
        .filter(Transaction.risk_level.in_(["High", "Critical"]))
        .count()
    )

    amount_stats = (
        db.query(
            func.coalesce(func.sum(Transaction.amount), 0),
            func.coalesce(func.avg(Transaction.amount), 0),
            func.coalesce(func.avg(Transaction.risk_score), 0),
        )
        .first()
    )

    total_payment_volume = round(float(amount_stats[0] or 0), 2)
    average_transaction_amount = round(float(amount_stats[1] or 0), 2)
    average_risk_score = round(float(amount_stats[2] or 0), 2)

    return DashboardSummary(
        total_transactions=total_transactions,
        total_vendors=total_vendors,
        total_alerts=total_alerts,
        open_alerts=open_alerts,
        critical_alerts=critical_alerts,
        high_risk_transactions=high_risk_transactions,
        total_payment_volume=total_payment_volume,
        average_transaction_amount=average_transaction_amount,
        average_risk_score=average_risk_score,
    )


@router.get("/risk-by-department", response_model=list[AnalyticsBucket])
def get_risk_by_department(db: Session = Depends(get_db)):
    rows = (
        db.query(
            Transaction.department,
            func.count(Transaction.id),
            func.avg(Transaction.risk_score),
            func.sum(Transaction.amount),
        )
        .group_by(Transaction.department)
        .order_by(func.avg(Transaction.risk_score).desc())
        .all()
    )

    return [
        AnalyticsBucket(
            name=row[0],
            count=int(row[1]),
            average_risk_score=round(float(row[2] or 0), 2),
            total_amount=round(float(row[3] or 0), 2),
        )
        for row in rows
    ]


@router.get("/risk-by-payment-method", response_model=list[AnalyticsBucket])
def get_risk_by_payment_method(db: Session = Depends(get_db)):
    rows = (
        db.query(
            Transaction.payment_method,
            func.count(Transaction.id),
            func.avg(Transaction.risk_score),
            func.sum(Transaction.amount),
        )
        .group_by(Transaction.payment_method)
        .order_by(func.avg(Transaction.risk_score).desc())
        .all()
    )

    return [
        AnalyticsBucket(
            name=row[0],
            count=int(row[1]),
            average_risk_score=round(float(row[2] or 0), 2),
            total_amount=round(float(row[3] or 0), 2),
        )
        for row in rows
    ]


@router.get("/risk-by-category", response_model=list[AnalyticsBucket])
def get_risk_by_category(db: Session = Depends(get_db)):
    rows = (
        db.query(
            Transaction.category,
            func.count(Transaction.id),
            func.avg(Transaction.risk_score),
            func.sum(Transaction.amount),
        )
        .group_by(Transaction.category)
        .order_by(func.avg(Transaction.risk_score).desc())
        .all()
    )

    return [
        AnalyticsBucket(
            name=row[0],
            count=int(row[1]),
            average_risk_score=round(float(row[2] or 0), 2),
            total_amount=round(float(row[3] or 0), 2),
        )
        for row in rows
    ]


@router.get("/risk-by-country", response_model=list[AnalyticsBucket])
def get_risk_by_country(db: Session = Depends(get_db)):
    rows = (
        db.query(
            Transaction.country,
            func.count(Transaction.id),
            func.avg(Transaction.risk_score),
            func.sum(Transaction.amount),
        )
        .group_by(Transaction.country)
        .order_by(func.avg(Transaction.risk_score).desc())
        .all()
    )

    return [
        AnalyticsBucket(
            name=row[0],
            count=int(row[1]),
            average_risk_score=round(float(row[2] or 0), 2),
            total_amount=round(float(row[3] or 0), 2),
        )
        for row in rows
    ]


@router.get("/alert-severity-distribution", response_model=list[AnalyticsBucket])
def get_alert_severity_distribution(db: Session = Depends(get_db)):
    rows = (
        db.query(
            RiskAlert.risk_level,
            func.count(RiskAlert.id),
            func.avg(RiskAlert.risk_score),
        )
        .group_by(RiskAlert.risk_level)
        .order_by(func.count(RiskAlert.id).desc())
        .all()
    )

    return [
        AnalyticsBucket(
            name=row[0],
            count=int(row[1]),
            average_risk_score=round(float(row[2] or 0), 2),
        )
        for row in rows
    ]


@router.get("/alert-status-distribution", response_model=list[AnalyticsBucket])
def get_alert_status_distribution(db: Session = Depends(get_db)):
    rows = (
        db.query(
            RiskAlert.status,
            func.count(RiskAlert.id),
            func.avg(RiskAlert.risk_score),
        )
        .group_by(RiskAlert.status)
        .order_by(func.count(RiskAlert.id).desc())
        .all()
    )

    return [
        AnalyticsBucket(
            name=row[0],
            count=int(row[1]),
            average_risk_score=round(float(row[2] or 0), 2),
        )
        for row in rows
    ]


@router.get("/top-risky-vendors", response_model=list[TopVendorRisk])
def get_top_risky_vendors(
    limit: int = Query(default=10, ge=1, le=50),
    db: Session = Depends(get_db),
):
    rows = (
        db.query(
            Transaction.vendor_name,
            func.count(Transaction.id).label("transaction_count"),
            func.sum(Transaction.amount).label("total_amount"),
            func.avg(Transaction.risk_score).label("average_risk_score"),
            func.max(Transaction.risk_score).label("max_risk_score"),
        )
        .group_by(Transaction.vendor_name)
        .order_by(func.avg(Transaction.risk_score).desc())
        .limit(limit)
        .all()
    )

    response = []

    for row in rows:
        alert_count = (
            db.query(RiskAlert)
            .join(Transaction, RiskAlert.transaction_id == Transaction.transaction_id)
            .filter(Transaction.vendor_name == row.vendor_name)
            .count()
        )

        response.append(
            TopVendorRisk(
                vendor_name=row.vendor_name,
                transaction_count=int(row.transaction_count or 0),
                alert_count=int(alert_count or 0),
                total_amount=round(float(row.total_amount or 0), 2),
                average_risk_score=round(float(row.average_risk_score or 0), 2),
                max_risk_score=int(row.max_risk_score or 0),
            )
        )

    return response


@router.get("/transaction-volume-trend", response_model=list[TrendPoint])
def get_transaction_volume_trend(
    days: int = Query(default=14, ge=1, le=90),
    db: Session = Depends(get_db),
):
    start_date = datetime.now(timezone.utc) - timedelta(days=days)

    rows = (
        db.query(
            func.date(Transaction.timestamp).label("date"),
            func.count(Transaction.id).label("count"),
            func.sum(Transaction.amount).label("total_amount"),
            func.avg(Transaction.risk_score).label("average_risk_score"),
        )
        .filter(Transaction.timestamp >= start_date)
        .group_by(func.date(Transaction.timestamp))
        .order_by(func.date(Transaction.timestamp).asc())
        .all()
    )

    return [
        TrendPoint(
            date=str(row.date),
            count=int(row.count or 0),
            total_amount=round(float(row.total_amount or 0), 2),
            average_risk_score=round(float(row.average_risk_score or 0), 2),
        )
        for row in rows
    ]


@router.get("/alert-trend", response_model=list[TrendPoint])
def get_alert_trend(
    days: int = Query(default=14, ge=1, le=90),
    db: Session = Depends(get_db),
):
    start_date = datetime.now(timezone.utc) - timedelta(days=days)

    rows = (
        db.query(
            func.date(RiskAlert.created_at).label("date"),
            func.count(RiskAlert.id).label("count"),
            func.avg(RiskAlert.risk_score).label("average_risk_score"),
        )
        .filter(RiskAlert.created_at >= start_date)
        .group_by(func.date(RiskAlert.created_at))
        .order_by(func.date(RiskAlert.created_at).asc())
        .all()
    )

    return [
        TrendPoint(
            date=str(row.date),
            count=int(row.count or 0),
            average_risk_score=round(float(row.average_risk_score or 0), 2),
        )
        for row in rows
    ]


@router.get("/recent-high-risk", response_model=list[TransactionResponse])
def get_recent_high_risk_transactions(
    limit: int = Query(default=10, ge=1, le=50),
    db: Session = Depends(get_db),
):
    return (
        db.query(Transaction)
        .filter(Transaction.risk_level.in_(["High", "Critical"]))
        .order_by(Transaction.timestamp.desc())
        .limit(limit)
        .all()
    )


@router.get("/recent-alerts", response_model=list[AlertResponse])
def get_recent_alerts(
    limit: int = Query(default=10, ge=1, le=50),
    db: Session = Depends(get_db),
):
    return (
        db.query(RiskAlert)
        .order_by(RiskAlert.created_at.desc())
        .limit(limit)
        .all()
    )


@router.get("/overview", response_model=DashboardOverview)
def get_dashboard_overview(db: Session = Depends(get_db)):
    summary = get_dashboard_summary(db)
    risk_by_department = get_risk_by_department(db)
    alert_severity_distribution = get_alert_severity_distribution(db)
    alert_status_distribution = get_alert_status_distribution(db)
    top_risky_vendors = get_top_risky_vendors(limit=5, db=db)

    recent_transactions = (
        db.query(Transaction)
        .order_by(Transaction.timestamp.desc())
        .limit(8)
        .all()
    )

    recent_alerts = (
        db.query(RiskAlert)
        .order_by(RiskAlert.created_at.desc())
        .limit(8)
        .all()
    )

    return DashboardOverview(
        summary=summary,
        risk_by_department=risk_by_department,
        alert_severity_distribution=alert_severity_distribution,
        alert_status_distribution=alert_status_distribution,
        top_risky_vendors=top_risky_vendors,
        recent_transactions=recent_transactions,
        recent_alerts=recent_alerts,
    )
