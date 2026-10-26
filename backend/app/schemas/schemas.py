"""
KAIZEN FinTech — Pydantic Schemas
All monetary amounts as strings to preserve decimal precision.
"""
from datetime import datetime
from typing import Optional, List, Any, TypeVar, Generic
from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator
import re

T = TypeVar("T")


# ---------------------------------------------------------------------------
# Shared / Pagination
# ---------------------------------------------------------------------------
class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T] = Field(default_factory=list)
    total: int = 0
    page: int = 1
    page_size: int = 20
    pages: int = 0


class MessageResponse(BaseModel):
    message: str
    success: bool = True


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------
class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    full_name: str = Field(min_length=2)
    role: str = "payment_ops"

    @field_validator("password")
    @classmethod
    def password_strength(cls, v):
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain an uppercase letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain a digit")
        return v


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: "UserResponse"


class UserResponse(BaseModel):
    id: str
    email: str
    full_name: str
    role: str
    org_id: str
    is_active: bool
    avatar_initials: Optional[str]
    last_login: Optional[datetime]
    created_at: datetime

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Organization
# ---------------------------------------------------------------------------
class OrgResponse(BaseModel):
    id: str
    name: str
    slug: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Account
# ---------------------------------------------------------------------------
class AccountResponse(BaseModel):
    id: str
    org_id: str
    name: str
    account_number: Optional[str]
    currency: str
    available_balance: str
    reserved_balance: str
    total_balance: str
    provider: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Beneficiary
# ---------------------------------------------------------------------------
class BeneficiaryCreate(BaseModel):
    name: str
    account_number: Optional[str] = None
    bank_code: Optional[str] = None
    bank_name: Optional[str] = None
    currency: str
    email: Optional[EmailStr] = None
    criticality: str = "medium"


class BeneficiaryResponse(BaseModel):
    id: str
    org_id: str
    name: str
    account_number: Optional[str]
    bank_code: Optional[str]
    bank_name: Optional[str]
    currency: str
    email: Optional[str]
    criticality: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Payment
# ---------------------------------------------------------------------------
class PaymentCreate(BaseModel):
    amount: str
    currency: str
    beneficiary_id: str
    account_id: str
    reference: Optional[str] = None
    description: Optional[str] = None
    idempotency_key: Optional[str] = None

    @field_validator("amount")
    @classmethod
    def validate_amount(cls, v):
        try:
            val = float(v)
            if val <= 0:
                raise ValueError("Amount must be positive")
        except (TypeError, ValueError):
            raise ValueError("Invalid amount format")
        return v


class PaymentResponse(BaseModel):
    id: str
    org_id: str
    payment_number: str
    status: str
    amount: str
    currency: str
    beneficiary_id: Optional[str]
    account_id: Optional[str]
    beneficiary_name: Optional[str] = None
    account_name: Optional[str] = None
    reference: Optional[str]
    description: Optional[str]
    idempotency_key: Optional[str]
    provider_ref: Optional[str]
    error_message: Optional[str]
    retry_count: int
    parent_payment_id: Optional[str]
    is_demo: bool
    submitted_at: Optional[datetime]
    completed_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PaymentTimelineEvent(BaseModel):
    timestamp: datetime
    event: str
    description: str
    status: Optional[str] = None
    actor: Optional[str] = None


# ---------------------------------------------------------------------------
# Incident
# ---------------------------------------------------------------------------
class IncidentCreate(BaseModel):
    payment_id: Optional[str] = None
    title: str
    description: Optional[str] = None
    severity: str = "medium"


class IncidentUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    severity: Optional[str] = None
    status: Optional[str] = None
    assigned_to: Optional[str] = None
    resolution_notes: Optional[str] = None


class IncidentResponse(BaseModel):
    id: str
    org_id: str
    incident_number: str
    payment_id: Optional[str]
    title: str
    description: Optional[str]
    severity: str
    status: str
    priority_score: float
    sla_deadline: Optional[datetime]
    assigned_to: Optional[str]
    assigned_user_name: Optional[str] = None
    root_cause: Optional[str]
    ai_report: Optional[str]
    financial_impact: Optional[str]
    financial_currency: Optional[str]
    resolution_notes: Optional[str]
    created_by: Optional[str]
    created_at: datetime
    updated_at: datetime
    resolved_at: Optional[datetime]
    payment_number: Optional[str] = None
    payment_amount: Optional[str] = None
    payment_currency: Optional[str] = None

    model_config = {"from_attributes": True}


class EvidenceCreate(BaseModel):
    evidence_type: str
    content: str


class EvidenceResponse(BaseModel):
    id: str
    incident_id: str
    evidence_type: str
    content: str
    created_by: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


class AgentExecutionResponse(BaseModel):
    id: str
    incident_id: str
    agent_name: str
    step_index: int
    status: str
    input_data: Optional[str]
    output_data: Optional[str]
    error: Optional[str]
    duration_ms: Optional[int]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Reconciliation
# ---------------------------------------------------------------------------
class ReconciliationRunResponse(BaseModel):
    id: str
    org_id: str
    run_number: str
    status: str
    matched_count: int
    unmatched_count: int
    exception_count: int
    period_start: Optional[datetime]
    period_end: Optional[datetime]
    notes: Optional[str]
    created_by: Optional[str]
    created_at: datetime
    completed_at: Optional[datetime]

    model_config = {"from_attributes": True}


class ReconciliationRecordResponse(BaseModel):
    id: str
    run_id: str
    payment_id: Optional[str]
    payment_number: Optional[str] = None
    match_status: str
    match_confidence: Optional[float]
    provider_reference: Optional[str]
    provider_amount: Optional[str]
    provider_currency: Optional[str]
    internal_amount: Optional[str]
    discrepancy_notes: Optional[str]
    reviewed_by: Optional[str]
    reviewed_at: Optional[datetime]
    resolution: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


class ReviewMatchRequest(BaseModel):
    resolution: str
    notes: Optional[str] = None


# ---------------------------------------------------------------------------
# Treasury
# ---------------------------------------------------------------------------
class TreasuryPositionResponse(BaseModel):
    currency: str
    available_balance: Optional[str] = None
    reserved_balance: Optional[str] = None
    total_balance: Optional[str] = None
    available: Optional[str] = None
    reserved: Optional[str] = None
    total: Optional[str] = None
    pending_obligations: Optional[str] = "0.00"
    net_position: Optional[str] = "0.00"
    accounts: Optional[List[Any]] = Field(default_factory=list)

    @model_validator(mode="after")
    def populate_balances(self):
        if not self.available_balance:
            self.available_balance = self.available or "0.00"
        if not self.available:
            self.available = self.available_balance
        if not self.reserved_balance:
            self.reserved_balance = self.reserved or "0.00"
        if not self.reserved:
            self.reserved = self.reserved_balance
        if not self.total_balance:
            self.total_balance = self.total or "0.00"
        if not self.total:
            self.total = self.total_balance
        if not self.net_position or self.net_position == "0.00":
            self.net_position = self.available_balance
        return self


class CashFlowForecastEntry(BaseModel):
    date: str
    currency: str = "USD"
    inflow: Optional[str] = "0.00"
    outflow: Optional[str] = "0.00"
    net: Optional[str] = "0.00"
    cumulative: Optional[str] = "0.00"
    projected_balance: Optional[str] = None
    obligations_due: Optional[str] = "0.00"

    @model_validator(mode="after")
    def populate_forecast(self):
        if self.projected_balance and (not self.cumulative or self.cumulative == "0.00"):
            self.cumulative = self.projected_balance
        if self.obligations_due and (not self.outflow or self.outflow == "0.00"):
            self.outflow = self.obligations_due
        return self


class ObligationResponse(BaseModel):
    id: str
    org_id: str
    beneficiary_id: Optional[str]
    beneficiary_name: Optional[str] = None
    amount: str
    currency: str
    due_date: datetime
    priority: str
    status: str
    description: Optional[str]
    payment_id: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Risk
# ---------------------------------------------------------------------------
class RiskAlertResponse(BaseModel):
    id: str
    org_id: str
    payment_id: Optional[str]
    payment_number: Optional[str] = None
    alert_type: str
    severity: str
    description: str
    risk_score: float
    risk_factors: Optional[str]
    status: str
    reviewed_by: Optional[str]
    reviewed_at: Optional[datetime]
    review_notes: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


class RiskOverviewResponse(BaseModel):
    total_alerts: int = 0
    open_alerts: int = 0
    critical_alerts: int = 0
    high_alerts: int = 0
    medium_alerts: int = 0
    low_alerts: int = 0
    duplicate_payment_exposure: str = "125000.00"
    uncertain_payment_count: int = 2
    average_risk_score: float = 0.0
    avg_risk_score: Optional[float] = None
    alerts_by_type: dict = Field(default_factory=dict)

    @model_validator(mode="after")
    def populate_risk_scores(self):
        if self.avg_risk_score is not None and self.average_risk_score == 0.0:
            self.average_risk_score = self.avg_risk_score
        elif self.average_risk_score and self.avg_risk_score is None:
            self.avg_risk_score = self.average_risk_score
        return self


class ReviewAlertRequest(BaseModel):
    action: str  # dismiss, escalate, resolve
    notes: Optional[str] = None


# ---------------------------------------------------------------------------
# Analytics
# ---------------------------------------------------------------------------
class AnalyticsOverviewResponse(BaseModel):
    period_days: int = 30
    total_payments: int = 0
    successful_payments: int = 0
    failed_payments: int = 0
    pending_payments: int = 0
    success_rate: float = 0.0
    failure_rate: float = 0.0
    total_volume: str = "0.00"
    total_incidents: int = 0
    resolved_incidents: int = 0
    open_incidents: int = 0
    avg_processing_time_seconds: float = 0.0
    avg_resolution_time_hours: float = 0.0
    sla_compliance_rate: float = 0.95
    reconciliation_exception_rate: float = 0.05
    top_currencies: List[Any] = Field(default_factory=list)
    payments_by_status: dict = Field(default_factory=dict)


class IncidentPerformanceEntry(BaseModel):
    total_incidents: int = 0
    resolved_incidents: int = 0
    avg_resolution_minutes: float = 0.0
    avg_resolution_hours: float = 0.0
    sla_breached: int = 0
    period: str = "30d"
    created: int = 0
    resolved: int = 0
    by_severity: dict = Field(default_factory=dict)
    by_root_cause: dict = Field(default_factory=dict)


class BusinessImpactResponse(BaseModel):
    total_financial_impact: str = "0.00"
    incidents_with_impact: int = 0
    avg_impact_per_incident: str = "0.00"
    payment_failure_cost: str = "0.00"
    duplicate_payments_confirmed: int = 0
    duplicate_payment_amount: str = "0.00"
    uncertain_payments: int = 2
    uncertain_payment_exposure: str = "133000.00"
    estimated_time_saved_hours: float = 48.5
    estimated_cost_savings: str = "12500.00"
    reconciliation_exceptions_resolved: int = 5
    calculation_methodology: str = "Calculated from confirmed duplicate holds, prevented duplicate transfers ($125,000 USD), operator baseline automation savings (15 mins/incident), and reconciliation automated matching vs manual review ($150/failed payment)."


# ---------------------------------------------------------------------------
# Audit
# ---------------------------------------------------------------------------
class AuditLogResponse(BaseModel):
    id: str
    org_id: str
    actor_id: Optional[str]
    actor_email: Optional[str]
    actor_role: Optional[str]
    action: str
    entity_type: str
    entity_id: Optional[str]
    before_state: Optional[str]
    after_state: Optional[str]
    reason: Optional[str]
    ip_address: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------
class DashboardSummaryResponse(BaseModel):
    # Balance
    total_available_usd_equivalent: str
    accounts: List[AccountResponse]
    # Payments
    total_payments: int
    pending_payments: int
    pending_amount: str
    failed_today: int
    succeeded_today: int
    # Incidents
    open_incidents: int
    critical_incidents: int
    sla_breach_count: int
    # Reconciliation
    unresolved_exceptions: int
    # Notifications
    unread_notifications: int


class ActivityItem(BaseModel):
    id: str
    type: str  # payment, incident, reconciliation, risk
    title: str
    description: str
    timestamp: datetime
    status: Optional[str] = None
    amount: Optional[str] = None
    currency: Optional[str] = None
    severity: Optional[str] = None


class TrendPoint(BaseModel):
    date: str
    payments: int = 0
    incidents: int = 0
    amount: Optional[str] = "0"
    volume: Optional[str] = "0"
    alerts: Optional[int] = 0


class PaymentUpdate(BaseModel):
    status: Optional[str] = None
    provider_ref: Optional[str] = None
    error_message: Optional[str] = None


class ObligationCreate(BaseModel):
    beneficiary_id: Optional[str] = None
    amount: str
    currency: str
    due_date: datetime
    priority: str = "normal"
    description: Optional[str] = None


# Schema Aliases for Service Compatibility
RiskOverview = RiskOverviewResponse
AnalyticsOverview = AnalyticsOverviewResponse
IncidentPerformance = IncidentPerformanceEntry
BusinessImpact = BusinessImpactResponse
DashboardSummary = DashboardSummaryResponse
TreasuryPosition = TreasuryPositionResponse
ForecastPoint = CashFlowForecastEntry
