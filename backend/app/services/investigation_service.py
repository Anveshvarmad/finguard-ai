from sqlalchemy.orm import Session

from app.models import InvestigationNote, RiskAlert, Transaction
from app.services.openai_service import OpenAIService


class InvestigationService:
    def build_alert_evidence(
        self,
        alert: RiskAlert,
        transaction: Transaction,
    ) -> str:
        flags = ", ".join(alert.risk_flags or [])

        return f"""
Alert ID: {alert.alert_id}
Transaction ID: {transaction.transaction_id}
Vendor: {transaction.vendor_name}
Department: {transaction.department}
Amount: {transaction.amount} {transaction.currency}
Payment Method: {transaction.payment_method}
Country: {transaction.country}
Category: {transaction.category}
Description: {transaction.description}
Invoice ID: {transaction.invoice_id}
Approved By: {transaction.approved_by}
Approval Status: {transaction.approval_status}
Risk Level: {alert.risk_level}
Risk Score: {alert.risk_score}
Risk Flags: {flags}
Alert Reason: {alert.alert_reason}
Review Status: {alert.status}
""".strip()

    def generate_ai_explanation(
        self,
        alert: RiskAlert,
        transaction: Transaction,
    ) -> dict:
        evidence = self.build_alert_evidence(alert, transaction)

        try:
            openai_service = OpenAIService()
            explanation = openai_service.generate_alert_investigation_explanation(evidence)

            return {
                "mode": "openai",
                "explanation": explanation,
                "evidence": evidence,
            }

        except Exception:
            return {
                "mode": "fallback",
                "explanation": self.generate_fallback_explanation(alert, transaction),
                "evidence": evidence,
            }

    def generate_fallback_explanation(
        self,
        alert: RiskAlert,
        transaction: Transaction,
    ) -> str:
        flags = alert.risk_flags or []

        if not flags:
            return (
                f"Transaction {transaction.transaction_id} is currently marked "
                f"{alert.risk_level} risk with a score of {alert.risk_score}, but no specific "
                f"risk flags were attached."
            )

        top_flags = "; ".join(flags[:4])

        return (
            f"Transaction {transaction.transaction_id} was marked {alert.risk_level} risk "
            f"with a score of {alert.risk_score}. The main indicators are: {top_flags}. "
            f"The transaction involved {transaction.vendor_name}, amount "
            f"{transaction.amount} {transaction.currency}, using {transaction.payment_method}."
        )

    def get_related_transactions(
        self,
        db: Session,
        transaction: Transaction,
        limit: int = 8,
    ) -> list[Transaction]:
        return (
            db.query(Transaction)
            .filter(Transaction.transaction_id != transaction.transaction_id)
            .filter(
                (Transaction.vendor_name == transaction.vendor_name)
                | (Transaction.department == transaction.department)
                | (Transaction.invoice_id == transaction.invoice_id)
            )
            .order_by(Transaction.timestamp.desc())
            .limit(limit)
            .all()
        )

    def build_timeline(
        self,
        alert: RiskAlert,
        transaction: Transaction,
        notes: list[InvestigationNote],
    ) -> list[dict]:
        timeline = [
            {
                "type": "transaction_created",
                "timestamp": transaction.created_at,
                "title": "Transaction ingested",
                "description": (
                    f"Transaction {transaction.transaction_id} was recorded for "
                    f"{transaction.vendor_name}."
                ),
            },
            {
                "type": "alert_created",
                "timestamp": alert.created_at,
                "title": "Risk alert created",
                "description": (
                    f"Alert {alert.alert_id} was created with {alert.risk_level} "
                    f"risk and score {alert.risk_score}."
                ),
            },
            {
                "type": "current_status",
                "timestamp": alert.updated_at,
                "title": f"Current status: {alert.status}",
                "description": (
                    f"Alert is currently assigned to "
                    f"{alert.assigned_to or 'Unassigned'}."
                ),
            },
        ]

        for note in notes:
            timeline.append(
                {
                    "type": "investigation_note",
                    "timestamp": note.created_at,
                    "title": f"Note by {note.author}",
                    "description": note.note,
                }
            )

        timeline.sort(key=lambda item: item["timestamp"], reverse=True)

        return timeline
