from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import relationship

from app.database import Base


def utc_now():
    return datetime.now(timezone.utc)


class Vendor(Base):
    __tablename__ = "vendors"

    id = Column(Integer, primary_key=True, index=True)
    vendor_id = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(255), unique=True, index=True, nullable=False)
    industry = Column(String(120), nullable=True)
    country = Column(String(120), nullable=False, default="United States")
    risk_rating = Column(String(50), nullable=False, default="Low")
    status = Column(String(50), nullable=False, default="Active")
    total_payment_volume = Column(Float, nullable=False, default=0.0)
    average_risk_score = Column(Float, nullable=False, default=0.0)

    created_at = Column(DateTime(timezone=True), default=utc_now)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    transactions = relationship("Transaction", back_populates="vendor")


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(String(80), unique=True, index=True, nullable=False)

    vendor_id = Column(Integer, ForeignKey("vendors.id"), nullable=True)
    vendor_name = Column(String(255), index=True, nullable=False)

    department = Column(String(120), index=True, nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String(20), nullable=False, default="USD")
    payment_method = Column(String(80), index=True, nullable=False)
    country = Column(String(120), index=True, nullable=False)
    category = Column(String(120), index=True, nullable=False)
    description = Column(Text, nullable=False)

    invoice_id = Column(String(100), nullable=True, index=True)
    approved_by = Column(String(120), nullable=True)
    approval_status = Column(String(80), nullable=False, default="Approved")

    risk_score = Column(Integer, nullable=False, default=0)
    risk_level = Column(String(50), index=True, nullable=False, default="Low")
    risk_flags = Column(JSON, nullable=False, default=list)

    review_status = Column(String(80), nullable=False, default="Not Reviewed")
    timestamp = Column(DateTime(timezone=True), default=utc_now, index=True)
    created_at = Column(DateTime(timezone=True), default=utc_now)

    vendor = relationship("Vendor", back_populates="transactions")
    alerts = relationship("RiskAlert", back_populates="transaction")


class RiskAlert(Base):
    __tablename__ = "risk_alerts"

    id = Column(Integer, primary_key=True, index=True)
    alert_id = Column(String(80), unique=True, index=True, nullable=False)

    transaction_db_id = Column(Integer, ForeignKey("transactions.id"), nullable=False)
    transaction_id = Column(String(80), index=True, nullable=False)

    risk_level = Column(String(50), index=True, nullable=False)
    risk_score = Column(Integer, nullable=False)
    risk_flags = Column(JSON, nullable=False, default=list)
    alert_reason = Column(Text, nullable=False)

    status = Column(String(80), index=True, nullable=False, default="Open")
    assigned_to = Column(String(120), nullable=True)

    created_at = Column(DateTime(timezone=True), default=utc_now)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    transaction = relationship("Transaction", back_populates="alerts")


class RiskRule(Base):
    __tablename__ = "risk_rules"

    id = Column(Integer, primary_key=True, index=True)
    rule_code = Column(String(80), unique=True, index=True, nullable=False)
    name = Column(String(180), nullable=False)
    description = Column(Text, nullable=False)
    score_weight = Column(Integer, nullable=False)
    enabled = Column(String(20), nullable=False, default="true")

    created_at = Column(DateTime(timezone=True), default=utc_now)


class SearchLog(Base):
    __tablename__ = "search_logs"

    id = Column(Integer, primary_key=True, index=True)
    query = Column(Text, nullable=False)
    filters = Column(JSON, nullable=True)
    result_count = Column(Integer, nullable=False, default=0)

    created_at = Column(DateTime(timezone=True), default=utc_now)


class InvestigationNote(Base):
    __tablename__ = "investigation_notes"

    id = Column(Integer, primary_key=True, index=True)

    alert_id = Column(String(80), index=True, nullable=False)
    transaction_id = Column(String(80), index=True, nullable=False)

    author = Column(String(120), nullable=False, default="Compliance Analyst")
    note = Column(Text, nullable=False)

    created_at = Column(DateTime(timezone=True), default=utc_now)
