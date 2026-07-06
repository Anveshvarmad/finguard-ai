from datetime import datetime, timedelta, timezone
from typing import Any

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models import RiskRule, Transaction, Vendor


ELEVATED_REVIEW_COUNTRIES = {
    "Cayman Islands",
    "British Virgin Islands",
    "Panama",
}

DEFAULT_RISK_RULES = [
    {
        "rule_code": "LARGE_PAYMENT",
        "name": "Large Payment Threshold",
        "description": "Adds risk when a transaction exceeds 10,000 USD.",
        "score_weight": 15,
    },
    {
        "rule_code": "ENHANCED_REVIEW_AMOUNT",
        "name": "Enhanced Review Amount",
        "description": "Adds risk when a transaction exceeds 50,000 USD.",
        "score_weight": 25,
    },
    {
        "rule_code": "WIRE_TRANSFER",
        "name": "Wire Transfer",
        "description": "Adds risk for wire transfer payments.",
        "score_weight": 10,
    },
    {
        "rule_code": "ELEVATED_REVIEW_COUNTRY",
        "name": "Elevated Review Country",
        "description": "Adds risk when a payment is routed to a configured elevated-review country.",
        "score_weight": 20,
    },
    {
        "rule_code": "HIGH_RISK_VENDOR",
        "name": "High Risk Vendor Profile",
        "description": "Adds risk when the vendor profile is already rated High or Critical.",
        "score_weight": 20,
    },
    {
        "rule_code": "MISSING_APPROVAL",
        "name": "Missing Approval Metadata",
        "description": "Adds risk when approval information is missing or incomplete.",
        "score_weight": 30,
    },
    {
        "rule_code": "WEEKEND_AFTER_HOURS",
        "name": "Weekend or After-Hours Approval",
        "description": "Adds risk when a transaction occurs during weekends or outside business hours.",
        "score_weight": 15,
    },
    {
        "rule_code": "DUPLICATE_INVOICE",
        "name": "Duplicate Invoice Pattern",
        "description": "Adds risk when the same vendor has another transaction with the same invoice ID.",
        "score_weight": 35,
    },
    {
        "rule_code": "REPEATED_VENDOR_PAYMENT",
        "name": "Repeated Vendor Payment",
        "description": "Adds risk when the same vendor receives multiple payments within 24 hours.",
        "score_weight": 20,
    },
    {
        "rule_code": "ROUND_NUMBER_TRANSFER",
        "name": "Round Number Transfer",
        "description": "Adds risk for large round-number payment amounts.",
        "score_weight": 10,
    },
    {
        "rule_code": "DEPARTMENT_BASELINE_ANOMALY",
        "name": "Department Baseline Anomaly",
        "description": "Adds risk when a department transaction is far above its historical average.",
        "score_weight": 15,
    },
]


class RiskScoringEngine:
    def seed_default_rules(self, db: Session) -> dict[str, int]:
        created = 0
        updated = 0

        for rule_data in DEFAULT_RISK_RULES:
            existing = (
                db.query(RiskRule)
                .filter(RiskRule.rule_code == rule_data["rule_code"])
                .first()
            )

            if existing:
                existing.name = rule_data["name"]
                existing.description = rule_data["description"]
                existing.score_weight = rule_data["score_weight"]
                existing.enabled = "true"
                updated += 1
            else:
                db.add(RiskRule(**rule_data, enabled="true"))
                created += 1

        db.commit()

        return {
            "created": created,
            "updated": updated,
        }

    def evaluate(
        self,
        db: Session,
        payload: dict[str, Any],
        vendor: Vendor | None = None,
        exclude_transaction_id: str | None = None,
    ) -> dict[str, Any]:
        amount = float(payload.get("amount") or 0)
        payment_method = payload.get("payment_method") or ""
        country = payload.get("country") or ""
        approval_status = payload.get("approval_status") or ""
        approved_by = payload.get("approved_by")
        invoice_id = payload.get("invoice_id")
        vendor_name = payload.get("vendor_name") or payload.get("vendor") or ""
        department = payload.get("department") or ""
        category = payload.get("category") or ""
        timestamp = payload.get("timestamp") or datetime.now(timezone.utc)

        if isinstance(timestamp, str):
            timestamp = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))

        score = 0
        flags: list[str] = []
        triggered_rules: list[str] = []

        def add_rule(rule_code: str, message: str, points: int):
            nonlocal score

            score += points
            flags.append(message)
            triggered_rules.append(rule_code)

        if amount >= 10000:
            add_rule(
                "LARGE_PAYMENT",
                "Transaction amount exceeds standard review threshold",
                15,
            )

        if amount >= 50000:
            add_rule(
                "ENHANCED_REVIEW_AMOUNT",
                "Transaction amount exceeds enhanced review threshold",
                25,
            )

        if payment_method.lower() == "wire":
            add_rule(
                "WIRE_TRANSFER",
                "Payment method is wire transfer",
                10,
            )

        if country in ELEVATED_REVIEW_COUNTRIES:
            add_rule(
                "ELEVATED_REVIEW_COUNTRY",
                "Payment country is configured for elevated review",
                20,
            )

        if vendor and vendor.risk_rating in ["High", "Critical"]:
            add_rule(
                "HIGH_RISK_VENDOR",
                f"Vendor profile is rated {vendor.risk_rating}",
                20 if vendor.risk_rating == "High" else 25,
            )

        if approval_status == "Missing Approval" or not approved_by:
            add_rule(
                "MISSING_APPROVAL",
                "Approval metadata is missing or incomplete",
                30,
            )

        if self._is_weekend_or_after_hours(timestamp):
            add_rule(
                "WEEKEND_AFTER_HOURS",
                "Transaction occurred during weekend or outside business hours",
                15,
            )

        if invoice_id and self._has_duplicate_invoice(
            db=db,
            vendor_name=vendor_name,
            invoice_id=invoice_id,
            exclude_transaction_id=exclude_transaction_id,
        ):
            add_rule(
                "DUPLICATE_INVOICE",
                "Same vendor has another transaction with this invoice ID",
                35,
            )

        repeated_payment_count = self._recent_vendor_payment_count(
            db=db,
            vendor_name=vendor_name,
            timestamp=timestamp,
            exclude_transaction_id=exclude_transaction_id,
        )

        if repeated_payment_count >= 2:
            add_rule(
                "REPEATED_VENDOR_PAYMENT",
                "Vendor has multiple payments within the last 24 hours",
                20,
            )

        if self._is_large_round_number(amount):
            add_rule(
                "ROUND_NUMBER_TRANSFER",
                "Large transaction uses a round-number amount",
                10,
            )

        department_average = self._department_average_amount(db, department)

        if department_average and amount > max(10000, department_average * 3):
            add_rule(
                "DEPARTMENT_BASELINE_ANOMALY",
                "Transaction amount is significantly above department baseline",
                15,
            )

        if country != "United States" and (
            "international" in category.lower() or payment_method.lower() == "wire"
        ):
            add_rule(
                "INTERNATIONAL_PAYMENT_REVIEW",
                "International payment requires additional review",
                10,
            )

        score = min(score, 100)
        risk_level = self._risk_level(score)

        return {
            "risk_score": score,
            "risk_level": risk_level,
            "risk_flags": flags,
            "triggered_rules": triggered_rules,
            "alert_reason": self._build_alert_reason(flags, score, risk_level),
            "evidence_fields": {
                "amount": amount,
                "payment_method": payment_method,
                "country": country,
                "vendor_name": vendor_name,
                "vendor_risk_rating": vendor.risk_rating if vendor else None,
                "approval_status": approval_status,
                "invoice_id": invoice_id,
                "department": department,
                "department_average_amount": department_average,
                "recent_vendor_payment_count": repeated_payment_count,
                "timestamp": timestamp.isoformat(),
            },
        }

    def _risk_level(self, score: int) -> str:
        if score >= 81:
            return "Critical"

        if score >= 61:
            return "High"

        if score >= 31:
            return "Medium"

        return "Low"

    def _is_weekend_or_after_hours(self, timestamp: datetime) -> bool:
        weekday = timestamp.weekday()
        hour = timestamp.hour

        is_weekend = weekday >= 5
        is_after_hours = hour < 8 or hour >= 18

        return is_weekend or is_after_hours

    def _has_duplicate_invoice(
        self,
        db: Session,
        vendor_name: str,
        invoice_id: str,
        exclude_transaction_id: str | None = None,
    ) -> bool:
        query = (
            db.query(Transaction)
            .filter(Transaction.vendor_name == vendor_name)
            .filter(Transaction.invoice_id == invoice_id)
        )

        if exclude_transaction_id:
            query = query.filter(Transaction.transaction_id != exclude_transaction_id)

        return query.first() is not None

    def _recent_vendor_payment_count(
        self,
        db: Session,
        vendor_name: str,
        timestamp: datetime,
        exclude_transaction_id: str | None = None,
    ) -> int:
        since = timestamp - timedelta(hours=24)

        query = (
            db.query(Transaction)
            .filter(Transaction.vendor_name == vendor_name)
            .filter(Transaction.timestamp >= since)
            .filter(Transaction.timestamp <= timestamp)
        )

        if exclude_transaction_id:
            query = query.filter(Transaction.transaction_id != exclude_transaction_id)

        return query.count()

    def _department_average_amount(
        self,
        db: Session,
        department: str,
    ) -> float | None:
        if not department:
            return None

        average = (
            db.query(func.avg(Transaction.amount))
            .filter(Transaction.department == department)
            .scalar()
        )

        if average is None:
            return None

        return round(float(average), 2)

    def _is_large_round_number(self, amount: float) -> bool:
        if amount < 10000:
            return False

        return amount % 5000 == 0

    def _build_alert_reason(
        self,
        flags: list[str],
        score: int,
        risk_level: str,
    ) -> str:
        if not flags:
            return "No major risk indicators were detected."

        top_reasons = "; ".join(flags[:4])

        return (
            f"{risk_level} risk transaction with score {score}. "
            f"Primary indicators: {top_reasons}."
        )
