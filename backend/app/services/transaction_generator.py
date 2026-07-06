import random
import time
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import RiskAlert, Transaction, Vendor


VENDOR_TEMPLATES = [
    {
        "name": "Northstar Logistics",
        "industry": "Logistics",
        "country": "United States",
        "base_risk": "High",
    },
    {
        "name": "BluePeak Consulting",
        "industry": "Consulting",
        "country": "United States",
        "base_risk": "Low",
    },
    {
        "name": "Apex Imports",
        "industry": "International Trade",
        "country": "Singapore",
        "base_risk": "Critical",
    },
    {
        "name": "Silverline Office Supply",
        "industry": "Office Supplies",
        "country": "United States",
        "base_risk": "Low",
    },
    {
        "name": "Quantum Advisory Group",
        "industry": "Advisory",
        "country": "United Kingdom",
        "base_risk": "Medium",
    },
    {
        "name": "Cobalt Freight Partners",
        "industry": "Freight",
        "country": "Mexico",
        "base_risk": "Medium",
    },
    {
        "name": "Vertex Offshore Services",
        "industry": "Offshore Services",
        "country": "Cayman Islands",
        "base_risk": "Critical",
    },
    {
        "name": "Evergreen IT Systems",
        "industry": "Technology",
        "country": "United States",
        "base_risk": "Low",
    },
]

DEPARTMENTS = [
    "Finance",
    "Procurement",
    "Operations",
    "Legal",
    "Administration",
    "IT",
    "Sales",
]

PAYMENT_METHODS = [
    "ACH",
    "Wire",
    "Card",
    "Check",
]

CATEGORIES = [
    "Vendor Payment",
    "Consulting Fee",
    "International Transfer",
    "Office Supplies",
    "Legal Advisory",
    "Software Subscription",
    "Freight Payment",
    "Employee Reimbursement",
]

SIMULATION_PATTERNS = [
    "normal_payment",
    "large_vendor_payment",
    "critical_wire_transfer",
    "missing_approval",
    "weekend_approval",
    "duplicate_invoice",
    "round_number_transfer",
    "high_risk_country_payment",
]


class TransactionGenerator:
    def generate_transaction(self, db: Session) -> Transaction:
        pattern = random.choices(
            SIMULATION_PATTERNS,
            weights=[35, 15, 10, 10, 10, 8, 7, 5],
            k=1,
        )[0]

        vendor_template = self._select_vendor(pattern)
        vendor = self._get_or_create_vendor(db, vendor_template)

        payload = self._build_payload(pattern, vendor)
        risk_score, risk_level, risk_flags = self._score_payload(payload, vendor, pattern)

        transaction = Transaction(
            transaction_id=f"TXN-{uuid4().hex[:10].upper()}",
            vendor_id=vendor.id,
            vendor_name=vendor.name,
            department=payload["department"],
            amount=payload["amount"],
            currency="USD",
            payment_method=payload["payment_method"],
            country=payload["country"],
            category=payload["category"],
            description=payload["description"],
            invoice_id=payload["invoice_id"],
            approved_by=payload["approved_by"],
            approval_status=payload["approval_status"],
            risk_score=risk_score,
            risk_level=risk_level,
            risk_flags=risk_flags,
            review_status="Not Reviewed",
            timestamp=payload["timestamp"],
        )

        db.add(transaction)
        db.flush()

        self._create_alert_if_needed(db, transaction)
        self._update_vendor_metrics(db, vendor, transaction)

        db.commit()
        db.refresh(transaction)

        return transaction

    def generate_batch(self, db: Session, count: int) -> list[Transaction]:
        transactions = []

        for _ in range(count):
            transaction = self.generate_transaction(db)
            transactions.append(transaction)

        return transactions

    def run_background_stream(self, count: int, delay_seconds: float) -> None:
        db = SessionLocal()

        try:
            for _ in range(count):
                self.generate_transaction(db)
                time.sleep(delay_seconds)
        finally:
            db.close()

    def _select_vendor(self, pattern: str) -> dict:
        if pattern in ["critical_wire_transfer", "high_risk_country_payment"]:
            risky_vendors = [
                vendor for vendor in VENDOR_TEMPLATES
                if vendor["base_risk"] in ["High", "Critical"]
            ]
            return random.choice(risky_vendors)

        return random.choice(VENDOR_TEMPLATES)

    def _get_or_create_vendor(self, db: Session, template: dict) -> Vendor:
        vendor = db.query(Vendor).filter(Vendor.name == template["name"]).first()

        if vendor:
            return vendor

        vendor = Vendor(
            vendor_id=f"VEN-{uuid4().hex[:8].upper()}",
            name=template["name"],
            industry=template["industry"],
            country=template["country"],
            risk_rating=template["base_risk"],
            status="Active",
        )

        db.add(vendor)
        db.flush()

        return vendor

    def _build_payload(self, pattern: str, vendor: Vendor) -> dict:
        department = random.choice(DEPARTMENTS)
        payment_method = random.choice(PAYMENT_METHODS)
        category = random.choice(CATEGORIES)
        country = vendor.country
        invoice_id = f"INV-{random.randint(10000, 99999)}"
        approved_by = random.choice(
            [
                "Alicia Reed",
                "Maya Chen",
                "Daniel Brooks",
                "Rachel Adams",
                "Marcus Lee",
                "Priya Shah",
                "Jordan Smith",
            ]
        )
        approval_status = "Approved"
        timestamp = datetime.now(timezone.utc)

        if pattern == "normal_payment":
            amount = round(random.uniform(350, 7500), 2)
            description = (
                f"Routine {category.lower()} from {department} department "
                f"to {vendor.name}."
            )

        elif pattern == "large_vendor_payment":
            amount = round(random.uniform(12000, 48000), 2)
            description = (
                f"Large vendor payment from {department} department to {vendor.name} "
                f"requiring enhanced compliance review."
            )

        elif pattern == "critical_wire_transfer":
            amount = round(random.uniform(55000, 135000), 2)
            payment_method = "Wire"
            category = "International Transfer"
            description = (
                f"High-value wire transfer to {vendor.name} with elevated review priority."
            )

        elif pattern == "missing_approval":
            amount = round(random.uniform(9000, 60000), 2)
            approved_by = None
            approval_status = "Missing Approval"
            description = (
                f"Payment to {vendor.name} is missing approval metadata in the workflow."
            )

        elif pattern == "weekend_approval":
            amount = round(random.uniform(8000, 35000), 2)
            days_until_saturday = (5 - timestamp.weekday()) % 7
            timestamp = timestamp + timedelta(days=days_until_saturday)
            timestamp = timestamp.replace(hour=21, minute=random.randint(0, 59))
            description = (
                f"Weekend approval detected for payment from {department} "
                f"department to {vendor.name}."
            )

        elif pattern == "duplicate_invoice":
            amount = round(random.uniform(4500, 22000), 2)
            invoice_id = random.choice(["INV-DUP-1001", "INV-DUP-1002", "INV-DUP-1003"])
            description = (
                f"Possible duplicate invoice payment to {vendor.name} using invoice {invoice_id}."
            )

        elif pattern == "round_number_transfer":
            amount = random.choice([10000, 15000, 25000, 50000, 75000, 100000])
            payment_method = random.choice(["Wire", "ACH"])
            description = (
                f"Round-number transfer to {vendor.name} detected for compliance review."
            )

        elif pattern == "high_risk_country_payment":
            amount = round(random.uniform(18000, 95000), 2)
            payment_method = "Wire"
            country = vendor.country
            category = "International Transfer"
            description = (
                f"International payment to {vendor.name} in a higher-risk vendor profile."
            )

        else:
            amount = round(random.uniform(500, 5000), 2)
            description = f"Standard payment to {vendor.name}."

        return {
            "pattern": pattern,
            "department": department,
            "amount": amount,
            "payment_method": payment_method,
            "country": country,
            "category": category,
            "description": description,
            "invoice_id": invoice_id,
            "approved_by": approved_by,
            "approval_status": approval_status,
            "timestamp": timestamp,
        }

    def _score_payload(
        self,
        payload: dict,
        vendor: Vendor,
        pattern: str,
    ) -> tuple[int, str, list[str]]:
        score = 0
        flags = []

        amount = payload["amount"]

        if amount >= 10000:
            score += 20
            flags.append("Large transaction amount")

        if amount >= 50000:
            score += 20
            flags.append("Amount exceeds enhanced review threshold")

        if payload["payment_method"] == "Wire":
            score += 10
            flags.append("Wire transfer")

        if vendor.risk_rating in ["High", "Critical"]:
            score += 20
            flags.append("High-risk vendor profile")

        if payload["approval_status"] == "Missing Approval":
            score += 30
            flags.append("Missing approval metadata")

        if pattern == "weekend_approval":
            score += 15
            flags.append("Weekend or after-hours approval")

        if pattern == "duplicate_invoice":
            score += 35
            flags.append("Potential duplicate invoice pattern")

        if pattern == "round_number_transfer":
            score += 15
            flags.append("Round-number transfer amount")

        if pattern == "critical_wire_transfer":
            score += 20
            flags.append("Critical wire transfer pattern")

        if pattern == "high_risk_country_payment":
            score += 20
            flags.append("International high-risk payment pattern")

        score = min(score, 100)

        if score >= 81:
            level = "Critical"
        elif score >= 61:
            level = "High"
        elif score >= 31:
            level = "Medium"
        else:
            level = "Low"

        return score, level, flags

    def _create_alert_if_needed(
        self,
        db: Session,
        transaction: Transaction,
    ) -> RiskAlert | None:
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

    def _update_vendor_metrics(
        self,
        db: Session,
        vendor: Vendor,
        transaction: Transaction,
    ) -> None:
        vendor.total_payment_volume += transaction.amount

        transaction_count = (
            db.query(Transaction)
            .filter(Transaction.vendor_id == vendor.id)
            .count()
        )

        existing_average = vendor.average_risk_score or 0

        if transaction_count <= 1:
            vendor.average_risk_score = transaction.risk_score
        else:
            previous_count = transaction_count - 1
            vendor.average_risk_score = round(
                ((existing_average * previous_count) + transaction.risk_score)
                / transaction_count,
                2,
            )

        if transaction.risk_score >= 81:
            vendor.risk_rating = "Critical"
        elif transaction.risk_score >= 61 and vendor.risk_rating != "Critical":
            vendor.risk_rating = "High"
        elif transaction.risk_score >= 31 and vendor.risk_rating not in ["High", "Critical"]:
            vendor.risk_rating = "Medium"
