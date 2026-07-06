from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class VendorCreate(BaseModel):
    name: str
    industry: str | None = None
    country: str = "United States"
    risk_rating: str = "Low"
    status: str = "Active"


class VendorResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    vendor_id: str
    name: str
    industry: str | None
    country: str
    risk_rating: str
    status: str
    total_payment_volume: float
    average_risk_score: float
    created_at: datetime


class TransactionCreate(BaseModel):
    transaction_id: str | None = None
    vendor_name: str
    department: str
    amount: float
    currency: str = "USD"
    payment_method: str
    country: str
    category: str
    description: str
    invoice_id: str | None = None
    approved_by: str | None = None
    approval_status: str = "Approved"
    risk_score: int = 0
    risk_level: str = "Low"
    risk_flags: list[str] = Field(default_factory=list)
    review_status: str = "Not Reviewed"
    timestamp: datetime | None = None


class TransactionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    transaction_id: str
    vendor_name: str
    department: str
    amount: float
    currency: str
    payment_method: str
    country: str
    category: str
    description: str
    invoice_id: str | None
    approved_by: str | None
    approval_status: str
    risk_score: int
    risk_level: str
    risk_flags: list[str]
    review_status: str
    timestamp: datetime
    created_at: datetime


class AlertResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    alert_id: str
    transaction_id: str
    risk_level: str
    risk_score: int
    risk_flags: list[str]
    alert_reason: str
    status: str
    assigned_to: str | None
    created_at: datetime
    updated_at: datetime


class AlertStatusUpdate(BaseModel):
    status: str
    assigned_to: str | None = None


class InvestigationNoteCreate(BaseModel):
    author: str = "Compliance Analyst"
    note: str


class InvestigationNoteResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    alert_id: str
    transaction_id: str
    author: str
    note: str
    created_at: datetime


class InvestigationTimelineItem(BaseModel):
    type: str
    timestamp: datetime
    title: str
    description: str


class AlertInvestigationResponse(BaseModel):
    alert: AlertResponse
    transaction: TransactionResponse
    notes: list[InvestigationNoteResponse]
    timeline: list[InvestigationTimelineItem]
    related_transactions: list[TransactionResponse]
    ai_mode: str
    ai_explanation: str
    evidence: str


class AlertExplanationResponse(BaseModel):
    alert_id: str
    transaction_id: str
    mode: str
    explanation: str
    evidence: str


class RiskRuleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    rule_code: str
    name: str
    description: str
    score_weight: int
    enabled: str
    created_at: datetime


class RiskEvaluationResponse(BaseModel):
    risk_score: int
    risk_level: str
    risk_flags: list[str]
    triggered_rules: list[str]
    alert_reason: str
    evidence_fields: dict[str, Any]


class SearchRequest(BaseModel):
    query: str
    top_k: int = Field(default=10, ge=1, le=50)
    risk_level: str | None = None
    department: str | None = None
    vendor: str | None = None
    payment_method: str | None = None
    category: str | None = None
    country: str | None = None
    min_amount: float | None = None
    max_amount: float | None = None


class SemanticSearchResult(BaseModel):
    transaction: TransactionResponse
    similarity_score: float
    distance: float
    evidence_text: str
    metadata: dict[str, Any]
    matched_reason: str


class SemanticSearchResponse(BaseModel):
    query: str
    top_k: int
    result_count: int
    results: list[SemanticSearchResult]


class IndexTransactionsResponse(BaseModel):
    status: str
    indexed_count: int
    indexed_ids: list[str]


class VectorStatsResponse(BaseModel):
    collection_name: str
    persist_path: str
    vector_count: int


class DashboardSummary(BaseModel):
    total_transactions: int
    total_vendors: int
    total_alerts: int
    open_alerts: int
    critical_alerts: int
    high_risk_transactions: int
    average_risk_score: float


class SeedResponse(BaseModel):
    status: str
    message: str
    created_vendors: int
    created_transactions: int
    created_alerts: int
    created_rules: int
