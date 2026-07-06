from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import InvestigationNote, RiskAlert, RiskRule, Transaction, Vendor
from app.schemas import SeedResponse


router = APIRouter(prefix="/seed", tags=["Seed Data"])


@router.post("/sample-data", response_model=SeedResponse)
def seed_sample_data(force: bool = False, db: Session = Depends(get_db)):
    existing_transactions = db.query(Transaction).count()

    if existing_transactions > 0 and not force:
        return SeedResponse(
            status="skipped",
            message="Sample data already exists. Use ?force=true to reset and seed again.",
            created_vendors=0,
            created_transactions=0,
            created_alerts=0,
            created_rules=0,
        )

    if force:
        db.query(InvestigationNote).delete()
        db.query(RiskAlert).delete()
        db.query(Transaction).delete()
        db.query(RiskRule).delete()
        db.query(Vendor).delete()
        db.commit()

    rules = [
        RiskRule(
            rule_code="LARGE_PAYMENT",
            name="Large Payment Threshold",
            description="Flags transactions above normal approval thresholds.",
            score_weight=25,
        ),
        RiskRule(
            rule_code="WIRE_TRANSFER",
            name="Wire Transfer Risk",
            description="Adds risk for wire-based transfers.",
            score_weight=10,
        ),
        RiskRule(
            rule_code="HIGH_RISK_COUNTRY",
            name="High Risk Country",
            description="Flags payments routed through high-risk jurisdictions.",
            score_weight=30,
        ),
        RiskRule(
            rule_code="MISSING_APPROVAL",
            name="Missing Approval Metadata",
            description="Flags records without complete approval metadata.",
            score_weight=35,
        ),
        RiskRule(
            rule_code="DUPLICATE_INVOICE",
            name="Duplicate Invoice Pattern",
            description="Detects repeated invoice identifiers or duplicate payment behavior.",
            score_weight=40,
        ),
    ]

    db.add_all(rules)

    vendors = [
        Vendor(
            vendor_id="VEN-NORTHSTAR",
            name="Northstar Logistics",
            industry="Logistics",
            country="United States",
            risk_rating="High",
        ),
        Vendor(
            vendor_id="VEN-BLUEPEAK",
            name="BluePeak Consulting",
            industry="Consulting",
            country="United States",
            risk_rating="Low",
        ),
        Vendor(
            vendor_id="VEN-APEXIMPORTS",
            name="Apex Imports",
            industry="International Trade",
            country="Singapore",
            risk_rating="Critical",
        ),
        Vendor(
            vendor_id="VEN-SILVERLINE",
            name="Silverline Office Supply",
            industry="Office Supplies",
            country="United States",
            risk_rating="Low",
        ),
        Vendor(
            vendor_id="VEN-QUANTUM",
            name="Quantum Advisory Group",
            industry="Advisory",
            country="United Kingdom",
            risk_rating="Medium",
        ),
    ]

    db.add_all(vendors)
    db.flush()

    vendor_map = {vendor.name: vendor for vendor in vendors}

    transactions = [
        Transaction(
            transaction_id="TXN-10001",
            vendor_id=vendor_map["Northstar Logistics"].id,
            vendor_name="Northstar Logistics",
            department="Finance",
            amount=18500.00,
            currency="USD",
            payment_method="Wire",
            country="United States",
            category="Vendor Payment",
            description="Large vendor payment approved outside the normal invoice review window.",
            invoice_id="INV-88420",
            approved_by="Alicia Reed",
            approval_status="Approved",
            risk_score=74,
            risk_level="High",
            risk_flags=[
                "Large transaction amount",
                "Wire transfer",
                "Approval outside standard review window",
            ],
        ),
        Transaction(
            transaction_id="TXN-10002",
            vendor_id=vendor_map["BluePeak Consulting"].id,
            vendor_name="BluePeak Consulting",
            department="Operations",
            amount=2400.00,
            currency="USD",
            payment_method="ACH",
            country="United States",
            category="Consulting Fee",
            description="Monthly consulting retainer for operational process review.",
            invoice_id="INV-22018",
            approved_by="Maya Chen",
            approval_status="Approved",
            risk_score=18,
            risk_level="Low",
            risk_flags=[],
        ),
        Transaction(
            transaction_id="TXN-10003",
            vendor_id=vendor_map["Apex Imports"].id,
            vendor_name="Apex Imports",
            department="Procurement",
            amount=72000.00,
            currency="USD",
            payment_method="Wire",
            country="Singapore",
            category="International Transfer",
            description="Large international wire transfer to import vendor with missing approval metadata.",
            invoice_id="INV-73001",
            approved_by=None,
            approval_status="Missing Approval",
            risk_score=96,
            risk_level="Critical",
            risk_flags=[
                "Large transaction amount",
                "International wire transfer",
                "Missing approval metadata",
                "High-risk vendor profile",
            ],
        ),
        Transaction(
            transaction_id="TXN-10004",
            vendor_id=vendor_map["Silverline Office Supply"].id,
            vendor_name="Silverline Office Supply",
            department="Administration",
            amount=9800.00,
            currency="USD",
            payment_method="ACH",
            country="United States",
            category="Office Supplies",
            description="Office equipment purchase with invoice ID similar to previous payment.",
            invoice_id="INV-44119",
            approved_by="Daniel Brooks",
            approval_status="Approved",
            risk_score=42,
            risk_level="Medium",
            risk_flags=[
                "Potential duplicate invoice pattern",
            ],
        ),
        Transaction(
            transaction_id="TXN-10005",
            vendor_id=vendor_map["Quantum Advisory Group"].id,
            vendor_name="Quantum Advisory Group",
            department="Legal",
            amount=14200.00,
            currency="USD",
            payment_method="Card",
            country="United Kingdom",
            category="Legal Advisory",
            description="Weekend approval for advisory payment above department baseline.",
            invoice_id="INV-91082",
            approved_by="Rachel Adams",
            approval_status="Approved",
            risk_score=66,
            risk_level="High",
            risk_flags=[
                "Weekend approval",
                "Amount above department baseline",
            ],
        ),
    ]

    db.add_all(transactions)
    db.flush()

    alerts = []

    for transaction in transactions:
        if transaction.risk_score >= 61:
            alerts.append(
                RiskAlert(
                    alert_id=f"ALT-{transaction.transaction_id.replace('TXN-', '')}",
                    transaction_db_id=transaction.id,
                    transaction_id=transaction.transaction_id,
                    risk_level=transaction.risk_level,
                    risk_score=transaction.risk_score,
                    risk_flags=transaction.risk_flags,
                    alert_reason=", ".join(transaction.risk_flags),
                    status="Open",
                )
            )

    db.add_all(alerts)

    for vendor in vendors:
        vendor_transactions = [
            transaction for transaction in transactions if transaction.vendor_id == vendor.id
        ]

        if vendor_transactions:
            vendor.total_payment_volume = sum(
                transaction.amount for transaction in vendor_transactions
            )
            vendor.average_risk_score = round(
                sum(transaction.risk_score for transaction in vendor_transactions)
                / len(vendor_transactions),
                2,
            )

    db.commit()

    return SeedResponse(
        status="success",
        message="Sample compliance data created successfully.",
        created_vendors=len(vendors),
        created_transactions=len(transactions),
        created_alerts=len(alerts),
        created_rules=len(rules),
    )
