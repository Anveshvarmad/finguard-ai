import asyncio
from datetime import datetime, timezone

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi.encoders import jsonable_encoder

from app.database import SessionLocal
from app.models import RiskAlert, Transaction


router = APIRouter(prefix="/ws", tags=["WebSocket"])


@router.websocket("/live-feed")
async def live_feed(websocket: WebSocket):
    await websocket.accept()

    try:
        while True:
            db = SessionLocal()

            try:
                recent_transactions = (
                    db.query(Transaction)
                    .order_by(Transaction.timestamp.desc())
                    .limit(20)
                    .all()
                )

                recent_alerts = (
                    db.query(RiskAlert)
                    .order_by(RiskAlert.created_at.desc())
                    .limit(10)
                    .all()
                )

                open_alert_count = (
                    db.query(RiskAlert)
                    .filter(RiskAlert.status == "Open")
                    .count()
                )

                critical_alert_count = (
                    db.query(RiskAlert)
                    .filter(RiskAlert.risk_level == "Critical")
                    .count()
                )

                payload = {
                    "type": "live_feed",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "transactions": jsonable_encoder(recent_transactions),
                    "alerts": jsonable_encoder(recent_alerts),
                    "metrics": {
                        "open_alerts": open_alert_count,
                        "critical_alerts": critical_alert_count,
                        "transaction_count": len(recent_transactions),
                        "alert_count": len(recent_alerts),
                    },
                }

                await websocket.send_json(payload)

            finally:
                db.close()

            await asyncio.sleep(3)

    except WebSocketDisconnect:
        return
