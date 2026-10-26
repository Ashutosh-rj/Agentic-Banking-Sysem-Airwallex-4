"""Dashboard service."""
from __future__ import annotations

from datetime import datetime, timezone, timedelta
from decimal import Decimal
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models.base import Payment, Incident, RiskAlert, AuditLog
from app.schemas.schemas import DashboardSummary, ActivityItem, TrendPoint


async def get_summary(db: AsyncSession, org_id: str) -> DashboardSummary:
    res_p = await db.execute(select(Payment).where(Payment.org_id == org_id))
    payments = list(res_p.scalars().all())

    res_i = await db.execute(select(Incident).where(Incident.org_id == org_id))
    incidents = list(res_i.scalars().all())

    res_ra = await db.execute(select(RiskAlert).where(RiskAlert.org_id == org_id))
    alerts = list(res_ra.scalars().all())

    total = len(payments)
    succeeded = sum(1 for p in payments if p.status == "SUCCEEDED")
    failed = sum(1 for p in payments if p.status == "FAILED")
    pending = sum(1 for p in payments if p.status in ("PENDING", "SUBMITTED", "VALIDATING"))
    unknown = sum(1 for p in payments if p.status == "UNKNOWN")

    open_incidents = sum(1 for i in incidents if i.status != "RESOLVED")
    critical_incidents = sum(1 for i in incidents if i.severity == "CRITICAL" and i.status != "RESOLVED")
    open_alerts = sum(1 for a in alerts if a.status == "OPEN")

    # Total volume in USD (approximate)
    total_volume = sum(
        Decimal(p.amount) for p in payments if p.currency == "USD" and p.status == "SUCCEEDED"
    )

    success_rate = round(succeeded / total, 4) if total else 0.0

    return DashboardSummary(
        total_payments=total,
        succeeded_payments=succeeded,
        failed_payments=failed,
        pending_payments=pending,
        unknown_payments=unknown,
        open_incidents=open_incidents,
        critical_incidents=critical_incidents,
        open_risk_alerts=open_alerts,
        total_volume_usd=str(total_volume),
        success_rate=success_rate,
    )


async def get_activity(db: AsyncSession, org_id: str, limit: int = 20) -> List[ActivityItem]:
    # Combine recent payments + incidents as activity
    res_p = await db.execute(
        select(Payment)
        .where(Payment.org_id == org_id)
        .order_by(Payment.created_at.desc())
        .limit(limit // 2)
    )
    payments = list(res_p.scalars().all())

    res_i = await db.execute(
        select(Incident)
        .where(Incident.org_id == org_id)
        .order_by(Incident.created_at.desc())
        .limit(limit // 2)
    )
    incidents = list(res_i.scalars().all())

    items: List[ActivityItem] = []
    for p in payments:
        items.append(
            ActivityItem(
                id=p.id,
                type="payment",
                title=f"Payment {p.payment_number}",
                description=f"{p.currency} {p.amount} — {p.status}",
                severity=None,
                timestamp=p.created_at,
            )
        )
    for i in incidents:
        items.append(
            ActivityItem(
                id=i.id,
                type="incident",
                title=i.title,
                description=i.description or "",
                severity=i.severity,
                timestamp=i.created_at,
            )
        )
    items.sort(key=lambda x: x.timestamp, reverse=True)
    return items[:limit]


async def get_trends(db: AsyncSession, org_id: str, days: int = 7) -> List[TrendPoint]:
    from app.services.analytics_service import get_trends as _get_trends
    return await _get_trends(db, org_id, days)
