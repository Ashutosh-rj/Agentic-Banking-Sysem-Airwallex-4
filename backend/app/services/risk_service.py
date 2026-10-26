"""Risk management service."""
from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone
from typing import Optional, List, Tuple
import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models.base import RiskAlert, Payment
from app.schemas.schemas import RiskOverview
import app.services.audit_service as audit_svc


def _uuid() -> str:
    return str(uuid.uuid4())


async def get_overview(db: AsyncSession, org_id: str) -> RiskOverview:
    res = await db.execute(
        select(RiskAlert).where(RiskAlert.org_id == org_id)
    )
    alerts = list(res.scalars().all())

    by_type: dict = defaultdict(int)
    open_alerts = critical = high = medium = low = 0
    total_score = 0.0
    scored_count = 0

    for a in alerts:
        if a.status == "OPEN":
            open_alerts += 1
        sev = a.severity.upper()
        if sev == "CRITICAL":
            critical += 1
        elif sev == "HIGH":
            high += 1
        elif sev == "MEDIUM":
            medium += 1
        elif sev == "LOW":
            low += 1
        by_type[a.alert_type] += 1
        if a.risk_score is not None:
            total_score += a.risk_score
            scored_count += 1

    return RiskOverview(
        total_alerts=len(alerts),
        open_alerts=open_alerts,
        critical_alerts=critical,
        high_alerts=high,
        medium_alerts=medium,
        low_alerts=low,
        avg_risk_score=round(total_score / scored_count, 2) if scored_count else 0.0,
        alerts_by_type=dict(by_type),
    )


async def get_alerts(
    db: AsyncSession,
    org_id: Optional[str] = None,
    status: Optional[str] = None,
    severity: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
) -> Tuple[List[RiskAlert], int]:
    from sqlalchemy.orm import selectinload
    query = select(RiskAlert).options(selectinload(RiskAlert.payment))
    if org_id:
        query = query.where(RiskAlert.org_id == org_id)
    if status:
        query = query.where(RiskAlert.status == status)
    if severity:
        query = query.where(RiskAlert.severity == severity)

    count_q = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_q)).scalar_one()

    query = query.order_by(RiskAlert.created_at.desc()).offset(
        (page - 1) * page_size
    ).limit(page_size)
    result = await db.execute(query)
    return list(result.scalars().all()), total


async def review_alert(
    db: AsyncSession,
    alert: RiskAlert,
    action: str,
    reviewer_id: str,
    actor_role: Optional[str] = None,
    notes: Optional[str] = None,
) -> RiskAlert:
    status_map = {"APPROVE": "CLEARED", "REJECT": "ESCALATED", "ESCALATE": "ESCALATED"}
    alert.status = status_map.get(action, "REVIEWED")
    alert.reviewed_by = reviewer_id
    alert.reviewed_at = datetime.now(timezone.utc)
    await audit_svc.log_event(
        db,
        "RISK_ALERT_REVIEWED",
        org_id=alert.org_id,
        actor_id=reviewer_id,
        actor_role=actor_role,
        entity_type="RiskAlert",
        entity_id=alert.id,
        after_state={"action": action, "status": alert.status},
    )
    await db.commit()
    await db.refresh(alert)
    return alert


async def check_duplicate_payment(
    db: AsyncSession, org_id: str, amount: str, beneficiary_id: str
) -> List[Payment]:
    res = await db.execute(
        select(Payment).where(
            Payment.org_id == org_id,
            Payment.amount == amount,
            Payment.beneficiary_id == beneficiary_id,
            Payment.status.in_(["SUCCEEDED", "PENDING", "SUBMITTED"]),
        ).limit(5)
    )
    return list(res.scalars().all())


async def create_alert(
    db: AsyncSession,
    org_id: str,
    alert_type: str,
    severity: str,
    description: str,
    risk_score: float,
    payment_id: Optional[str] = None,
) -> RiskAlert:
    alert = RiskAlert(
        id=_uuid(),
        org_id=org_id,
        payment_id=payment_id,
        alert_type=alert_type,
        severity=severity,
        description=description,
        risk_score=risk_score,
        status="OPEN",
        created_at=datetime.now(timezone.utc),
    )
    db.add(alert)
    await db.commit()
    await db.refresh(alert)
    return alert
