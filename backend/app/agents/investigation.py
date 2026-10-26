"""
KAIZEN FinTech - Deterministic AI Investigation Pipeline.

Pipeline stages:
  1. IntakeAgent          → validates & classifies incident
  2. PaymentInvestigationAgent → analyzes payment state & timeline
  3. ReconciliationAgent  → checks reconciliation status
  4. RootCauseAgent       → classifies root cause
  5. TreasuryDecisionAgent→ evaluates financial impact & liquidity
  6. ActionPlanningAgent  → generates recommended actions
  7. BusinessImpactAgent  → calculates operational/financial impact
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional, List, Dict, Any


# ---------------------------------------------------------------------------
# Shared Data Structures
# ---------------------------------------------------------------------------
@dataclass
class AgentResult:
    agent_name: str
    status: str  # SUCCESS / FAILED / SKIPPED
    output: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None


@dataclass
class PipelineContext:
    incident_id: str
    org_id: str
    incident_title: str
    incident_description: str
    severity: str
    payment: Optional[Dict[str, Any]] = None
    reconciliation_records: List[Dict[str, Any]] = field(default_factory=list)
    accounts: List[Dict[str, Any]] = field(default_factory=list)
    obligations: List[Dict[str, Any]] = field(default_factory=list)
    agent_results: List[AgentResult] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Individual Agents
# ---------------------------------------------------------------------------

class IntakeAgent:
    """Validates and classifies the incident."""

    NAME = "IntakeAgent"

    def run(self, ctx: PipelineContext) -> AgentResult:
        try:
            # Classify severity from title/description keywords
            text = f"{ctx.incident_title} {ctx.incident_description}".lower()

            severity_override = ctx.severity
            if any(k in text for k in ["critical", "outage", "total loss", "breach"]):
                severity_override = "CRITICAL"
            elif any(k in text for k in ["major", "significant", "large amount"]):
                severity_override = "HIGH"
            elif any(k in text for k in ["minor", "small", "low"]):
                severity_override = "LOW"

            category = "PAYMENT_FAILURE"
            if "reconcil" in text:
                category = "RECONCILIATION"
            elif "duplicate" in text:
                category = "DUPLICATE_PAYMENT"
            elif "timeout" in text or "latency" in text:
                category = "PROVIDER_TIMEOUT"
            elif "compliance" in text or "aml" in text or "kyc" in text:
                category = "COMPLIANCE"
            elif "fraud" in text:
                category = "FRAUD"
            elif "liquidity" in text or "balance" in text:
                category = "LIQUIDITY"

            output = {
                "category": category,
                "severity_override": severity_override,
                "has_payment": ctx.payment is not None,
                "validation_passed": True,
                "classification_confidence": 0.87,
            }
            return AgentResult(agent_name=self.NAME, status="SUCCESS", output=output)
        except Exception as e:
            return AgentResult(agent_name=self.NAME, status="FAILED", error=str(e))


class PaymentInvestigationAgent:
    """Analyzes payment state and timeline."""

    NAME = "PaymentInvestigationAgent"

    def run(self, ctx: PipelineContext, intake_result: AgentResult) -> AgentResult:
        try:
            payment = ctx.payment
            if not payment:
                return AgentResult(
                    agent_name=self.NAME,
                    status="SKIPPED",
                    output={"reason": "No associated payment"},
                )

            status = payment.get("status", "UNKNOWN")
            amount = payment.get("amount", "0")
            currency = payment.get("currency", "USD")
            retry_count = payment.get("retry_count", 0)
            error_message = payment.get("error_message")

            anomalies = []
            if retry_count > 2:
                anomalies.append(f"High retry count: {retry_count}")
            if status == "UNKNOWN":
                anomalies.append("Payment in UNKNOWN state — provider did not confirm")
            if status == "REQUIRES_REVIEW":
                anomalies.append("Payment flagged for manual review")
            if error_message:
                anomalies.append(f"Error recorded: {error_message}")

            # Determine processing time
            created_at = payment.get("created_at")
            completed_at = payment.get("completed_at")
            processing_seconds = None
            if created_at and completed_at:
                try:
                    if isinstance(created_at, str):
                        created_at = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
                    if isinstance(completed_at, str):
                        completed_at = datetime.fromisoformat(completed_at.replace("Z", "+00:00"))
                    processing_seconds = (completed_at - created_at).total_seconds()
                except Exception:
                    pass

            output = {
                "payment_status": status,
                "amount": amount,
                "currency": currency,
                "retry_count": retry_count,
                "anomalies": anomalies,
                "processing_seconds": processing_seconds,
                "provider_ref": payment.get("provider_ref"),
                "has_provider_ref": bool(payment.get("provider_ref")),
                "terminal_state": status in ("SUCCEEDED", "FAILED", "CANCELLED"),
                "requires_action": status in ("FAILED", "UNKNOWN", "REQUIRES_REVIEW"),
            }
            return AgentResult(agent_name=self.NAME, status="SUCCESS", output=output)
        except Exception as e:
            return AgentResult(agent_name=self.NAME, status="FAILED", error=str(e))


class ReconciliationAgent:
    """Checks if payment is reconciled."""

    NAME = "ReconciliationAgent"

    def run(self, ctx: PipelineContext, payment_result: AgentResult) -> AgentResult:
        try:
            records = ctx.reconciliation_records
            if not records:
                return AgentResult(
                    agent_name=self.NAME,
                    status="SUCCESS",
                    output={
                        "reconciled": False,
                        "reason": "No reconciliation records found",
                        "discrepancies": [],
                    },
                )

            matched = [r for r in records if r.get("match_status") == "MATCHED"]
            unmatched = [r for r in records if r.get("match_status") == "UNMATCHED"]
            exceptions = [r for r in records if r.get("match_status") == "EXCEPTION"]

            discrepancies = []
            for r in unmatched + exceptions:
                if r.get("discrepancy_notes"):
                    discrepancies.append(r["discrepancy_notes"])

            output = {
                "reconciled": len(matched) > 0 and len(unmatched) == 0,
                "matched_count": len(matched),
                "unmatched_count": len(unmatched),
                "exception_count": len(exceptions),
                "discrepancies": discrepancies,
                "avg_confidence": (
                    sum(r.get("match_confidence", 0) or 0 for r in records) / len(records)
                    if records else 0
                ),
            }
            return AgentResult(agent_name=self.NAME, status="SUCCESS", output=output)
        except Exception as e:
            return AgentResult(agent_name=self.NAME, status="FAILED", error=str(e))


class RootCauseAgent:
    """Classifies root cause from accumulated evidence."""

    NAME = "RootCauseAgent"

    CAUSE_RULES = [
        ("PROVIDER_TIMEOUT", ["timeout", "timed out", "gateway", "503", "504"]),
        ("INSUFFICIENT_FUNDS", ["insufficient", "balance", "funds", "liquidity"]),
        ("DUPLICATE_PAYMENT", ["duplicate", "idempotency", "already processed"]),
        ("INVALID_BENEFICIARY", ["invalid account", "beneficiary", "wrong iban", "rejected"]),
        ("COMPLIANCE_HOLD", ["compliance", "aml", "kyc", "sanctions", "hold"]),
        ("SYSTEM_ERROR", ["system error", "internal", "500", "database", "exception"]),
        ("FRAUD_SUSPECTED", ["fraud", "suspicious", "unauthorized"]),
        ("DATA_DISCREPANCY", ["mismatch", "discrepancy", "reconcil"]),
        ("NETWORK_ISSUE", ["network", "connection", "unreachable"]),
    ]

    def run(
        self,
        ctx: PipelineContext,
        intake_result: AgentResult,
        payment_result: AgentResult,
        recon_result: AgentResult,
    ) -> AgentResult:
        try:
            text_corpus = " ".join([
                ctx.incident_title,
                ctx.incident_description or "",
                str(ctx.payment.get("error_message") or "") if ctx.payment else "",
                str(payment_result.output.get("anomalies", [])),
                str(recon_result.output.get("discrepancies", [])),
            ]).lower()

            detected_causes = []
            for cause, keywords in self.CAUSE_RULES:
                if any(k in text_corpus for k in keywords):
                    detected_causes.append(cause)

            primary_cause = detected_causes[0] if detected_causes else "UNKNOWN"
            confidence = 0.9 if detected_causes else 0.3

            # Boost confidence if reconciliation confirms
            if recon_result.output.get("unmatched_count", 0) > 0:
                if "DATA_DISCREPANCY" not in detected_causes:
                    detected_causes.append("DATA_DISCREPANCY")

            output = {
                "primary_root_cause": primary_cause,
                "all_causes": detected_causes,
                "confidence": confidence,
                "analysis_text": (
                    f"Root cause identified as {primary_cause} based on pattern matching. "
                    f"Confidence: {confidence:.0%}."
                ),
            }
            return AgentResult(agent_name=self.NAME, status="SUCCESS", output=output)
        except Exception as e:
            return AgentResult(agent_name=self.NAME, status="FAILED", error=str(e))


class TreasuryDecisionAgent:
    """Evaluates financial impact and liquidity."""

    NAME = "TreasuryDecisionAgent"

    def run(
        self,
        ctx: PipelineContext,
        payment_result: AgentResult,
    ) -> AgentResult:
        try:
            payment = ctx.payment
            amount = Decimal("0")
            currency = "USD"
            if payment:
                try:
                    amount = Decimal(str(payment.get("amount", "0")))
                    currency = payment.get("currency", "USD")
                except Exception:
                    pass

            # Find matching account balance
            available_balance = Decimal("0")
            for acc in ctx.accounts:
                if acc.get("currency") == currency:
                    try:
                        available_balance = Decimal(str(acc.get("available_balance", "0")))
                        break
                    except Exception:
                        pass

            # Count upcoming obligations
            pending_obligations_amount = Decimal("0")
            for ob in ctx.obligations:
                if ob.get("currency") == currency and ob.get("status") == "PENDING":
                    try:
                        pending_obligations_amount += Decimal(str(ob.get("amount", "0")))
                    except Exception:
                        pass

            liquidity_ratio = (
                float(available_balance / (amount + pending_obligations_amount))
                if (amount + pending_obligations_amount) > 0
                else 999.0
            )

            liquidity_status = "ADEQUATE"
            if liquidity_ratio < 1.0:
                liquidity_status = "CRITICAL"
            elif liquidity_ratio < 1.5:
                liquidity_status = "LOW"
            elif liquidity_ratio < 2.0:
                liquidity_status = "MODERATE"

            output = {
                "payment_amount": str(amount),
                "currency": currency,
                "available_balance": str(available_balance),
                "pending_obligations": str(pending_obligations_amount),
                "liquidity_ratio": round(liquidity_ratio, 2),
                "liquidity_status": liquidity_status,
                "financial_impact": str(amount),
                "recommendation": (
                    "Retry payment — liquidity adequate."
                    if liquidity_status in ("ADEQUATE", "MODERATE")
                    else "Escalate — insufficient liquidity for retry."
                ),
            }
            return AgentResult(agent_name=self.NAME, status="SUCCESS", output=output)
        except Exception as e:
            return AgentResult(agent_name=self.NAME, status="FAILED", error=str(e))


class ActionPlanningAgent:
    """Generates recommended actions based on all prior findings."""

    NAME = "ActionPlanningAgent"

    ACTION_MAP = {
        "PROVIDER_TIMEOUT": [
            "Retry payment after 15 minutes",
            "Contact payment provider support",
            "Check provider status page",
        ],
        "INSUFFICIENT_FUNDS": [
            "Transfer funds from reserve account",
            "Delay lower-priority obligations",
            "Notify treasury team immediately",
        ],
        "DUPLICATE_PAYMENT": [
            "Cancel duplicate payment",
            "Verify idempotency key logic",
            "Review deduplication middleware",
        ],
        "INVALID_BENEFICIARY": [
            "Verify beneficiary account details",
            "Contact beneficiary for correct information",
            "Update beneficiary record",
        ],
        "COMPLIANCE_HOLD": [
            "Escalate to compliance team",
            "Gather KYC/AML documentation",
            "Do not retry until cleared",
        ],
        "SYSTEM_ERROR": [
            "Check system logs for stack trace",
            "Restart affected service if needed",
            "Retry payment after system stabilizes",
        ],
        "FRAUD_SUSPECTED": [
            "Freeze payment immediately",
            "Escalate to fraud team",
            "Notify compliance officer",
        ],
        "DATA_DISCREPANCY": [
            "Run reconciliation report",
            "Compare internal records with provider statement",
            "Escalate discrepancy to finance team",
        ],
        "NETWORK_ISSUE": [
            "Check network connectivity",
            "Retry with exponential backoff",
            "Switch to backup provider if available",
        ],
        "UNKNOWN": [
            "Gather additional evidence",
            "Escalate to senior engineer",
            "Monitor for 24 hours",
        ],
    }

    def run(
        self,
        ctx: PipelineContext,
        root_cause_result: AgentResult,
        treasury_result: AgentResult,
    ) -> AgentResult:
        try:
            primary_cause = root_cause_result.output.get("primary_root_cause", "UNKNOWN")
            actions = self.ACTION_MAP.get(primary_cause, self.ACTION_MAP["UNKNOWN"])

            # Add treasury-specific action
            if treasury_result.output.get("liquidity_status") in ("CRITICAL", "LOW"):
                actions = ["URGENT: Address liquidity shortage first"] + actions

            priority = "HIGH"
            if ctx.severity == "CRITICAL":
                priority = "CRITICAL"
            elif ctx.severity == "LOW":
                priority = "NORMAL"

            output = {
                "priority": priority,
                "actions": actions,
                "immediate_actions": actions[:2],
                "defer_actions": actions[2:],
                "escalate": ctx.severity in ("CRITICAL", "HIGH"),
                "auto_retry_safe": primary_cause not in (
                    "FRAUD_SUSPECTED", "COMPLIANCE_HOLD", "INSUFFICIENT_FUNDS"
                ),
            }
            return AgentResult(agent_name=self.NAME, status="SUCCESS", output=output)
        except Exception as e:
            return AgentResult(agent_name=self.NAME, status="FAILED", error=str(e))


class BusinessImpactAgent:
    """Calculates operational and financial impact."""

    NAME = "BusinessImpactAgent"

    def run(
        self,
        ctx: PipelineContext,
        treasury_result: AgentResult,
        action_result: AgentResult,
    ) -> AgentResult:
        try:
            amount = Decimal(treasury_result.output.get("financial_impact", "0"))
            currency = treasury_result.output.get("currency", "USD")

            # Estimate operational cost (staff time)
            severity_hours = {
                "CRITICAL": 8,
                "HIGH": 4,
                "MEDIUM": 2,
                "LOW": 0.5,
            }
            resolution_hours = severity_hours.get(ctx.severity, 2)
            hourly_rate = Decimal("150")  # USD per hour average ops cost
            operational_cost = Decimal(str(resolution_hours)) * hourly_rate

            # Reputational risk score
            reputational_risk = {
                "CRITICAL": "SEVERE",
                "HIGH": "HIGH",
                "MEDIUM": "MODERATE",
                "LOW": "LOW",
            }.get(ctx.severity, "MODERATE")

            total_impact = amount + operational_cost

            output = {
                "payment_amount": str(amount),
                "currency": currency,
                "operational_cost_usd": str(operational_cost),
                "estimated_resolution_hours": resolution_hours,
                "total_financial_impact_usd": str(total_impact),
                "reputational_risk": reputational_risk,
                "sla_risk": ctx.severity in ("CRITICAL", "HIGH"),
                "customer_impact": ctx.severity in ("CRITICAL", "HIGH"),
                "summary": (
                    f"Estimated total impact: {currency} {amount} in payment value, "
                    f"plus ${operational_cost} in operational costs. "
                    f"Reputational risk: {reputational_risk}."
                ),
            }
            return AgentResult(agent_name=self.NAME, status="SUCCESS", output=output)
        except Exception as e:
            return AgentResult(agent_name=self.NAME, status="FAILED", error=str(e))


# ---------------------------------------------------------------------------
# Pipeline Orchestrator
# ---------------------------------------------------------------------------

class InvestigationPipeline:
    """
    Runs the full deterministic investigation pipeline and returns
    a structured report dictionary.
    """

    def run(self, ctx: PipelineContext) -> Dict[str, Any]:
        results: List[AgentResult] = []

        # Stage 1: Intake
        intake = IntakeAgent().run(ctx)
        results.append(intake)

        # Stage 2: Payment Investigation
        payment_inv = PaymentInvestigationAgent().run(ctx, intake)
        results.append(payment_inv)

        # Stage 3: Reconciliation
        recon = ReconciliationAgent().run(ctx, payment_inv)
        results.append(recon)

        # Stage 4: Root Cause
        root_cause = RootCauseAgent().run(ctx, intake, payment_inv, recon)
        results.append(root_cause)

        # Stage 5: Treasury Decision
        treasury = TreasuryDecisionAgent().run(ctx, payment_inv)
        results.append(treasury)

        # Stage 6: Action Planning
        actions = ActionPlanningAgent().run(ctx, root_cause, treasury)
        results.append(actions)

        # Stage 7: Business Impact
        impact = BusinessImpactAgent().run(ctx, treasury, actions)
        results.append(impact)

        ctx.agent_results = results

        # Compose final report
        report = self._compose_report(ctx, results)
        return report

    def _compose_report(
        self, ctx: PipelineContext, results: List[AgentResult]
    ) -> Dict[str, Any]:
        def _get(name: str) -> Dict[str, Any]:
            for r in results:
                if r.agent_name == name:
                    return r.output
            return {}

        intake_out = _get("IntakeAgent")
        payment_out = _get("PaymentInvestigationAgent")
        recon_out = _get("ReconciliationAgent")
        rc_out = _get("RootCauseAgent")
        treasury_out = _get("TreasuryDecisionAgent")
        action_out = _get("ActionPlanningAgent")
        impact_out = _get("BusinessImpactAgent")

        report = {
            "incident_id": ctx.incident_id,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "pipeline_stages": [
                {
                    "agent": r.agent_name,
                    "status": r.status,
                    "output": r.output,
                    "error": r.error,
                }
                for r in results
            ],
            "summary": {
                "category": intake_out.get("category", "UNKNOWN"),
                "severity": intake_out.get("severity_override", ctx.severity),
                "root_cause": rc_out.get("primary_root_cause", "UNKNOWN"),
                "root_cause_confidence": rc_out.get("confidence", 0),
                "reconciled": recon_out.get("reconciled", False),
                "liquidity_status": treasury_out.get("liquidity_status", "UNKNOWN"),
                "financial_impact": treasury_out.get("financial_impact", "0"),
                "total_impact_usd": impact_out.get("total_financial_impact_usd", "0"),
                "reputational_risk": impact_out.get("reputational_risk", "UNKNOWN"),
            },
            "recommended_actions": action_out.get("actions", []),
            "immediate_actions": action_out.get("immediate_actions", []),
            "escalate": action_out.get("escalate", False),
            "auto_retry_safe": action_out.get("auto_retry_safe", False),
            "payment_anomalies": payment_out.get("anomalies", []),
            "reconciliation": {
                "matched": recon_out.get("matched_count", 0),
                "unmatched": recon_out.get("unmatched_count", 0),
                "exceptions": recon_out.get("exception_count", 0),
                "discrepancies": recon_out.get("discrepancies", []),
            },
        }
        return report


def build_pipeline_context(
    incident: Any,
    payment: Optional[Any] = None,
    reconciliation_records: Optional[List[Any]] = None,
    accounts: Optional[List[Any]] = None,
    obligations: Optional[List[Any]] = None,
) -> PipelineContext:
    """
    Helper to build PipelineContext from ORM model instances.
    """
    def _model_to_dict(obj: Any) -> Dict[str, Any]:
        if obj is None:
            return {}
        d = {}
        for col in obj.__class__.__table__.columns:
            val = getattr(obj, col.name, None)
            if isinstance(val, datetime):
                val = val.isoformat()
            d[col.name] = val
        return d

    return PipelineContext(
        incident_id=incident.id,
        org_id=incident.org_id,
        incident_title=incident.title,
        incident_description=incident.description or "",
        severity=incident.severity,
        payment=_model_to_dict(payment) if payment else None,
        reconciliation_records=[_model_to_dict(r) for r in (reconciliation_records or [])],
        accounts=[_model_to_dict(a) for a in (accounts or [])],
        obligations=[_model_to_dict(o) for o in (obligations or [])],
    )
