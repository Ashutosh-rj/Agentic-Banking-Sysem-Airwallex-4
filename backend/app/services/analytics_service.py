"""Analytics service."""
from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone, timedelta
from decimal import Decimal
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models.base import Payment, Incident, RiskAlert, AuditLog
from app.schemas.schemas import (
    AnalyticsOverview, IncidentPerformance, BusinessImpact, TrendPoint,
)


async def get_overview(
    db: AsyncSession, org_id: str, period_days: int = 30
) -> AnalyticsOverview:
    since = datetime.now(timezone.utc) - timedelta(days=period_days)
    res = await db.execute(
        select(Payment).where(
            Payment.org_id == org_id, Payment.created_at >= since
        )
    )
    payments = list(res.scalars().all())

    total = len(payments)
    succeeded = sum(1 for p in payments if p.status == "SUCCEEDED")
    failed = sum(1 for p in payments if p.status == "FAILED")

    total_volume = sum(
        Decimal(p.amount)
        for p in payments
        if p.currency == "USD"  # only USD for simplicity
    )

    # Avg processing time
    times = []
    for p in payments:
        if p.created_at and p.completed_at:
            times.append((p.completed_at - p.created_at).total_seconds())
    avg_time = sum(times) / len(times) if times else 0.0

    by_status: dict = defaultdict(int)
    by_ccy: dict = defaultdict(Decimal)
    for p in payments:
        by_status[p.status] += 1
        by_ccy[p.currency] += Decimal(p.amount)

    top_currencies = [
        {"currency": k, "volume": str(v)} for k, v in sorted(by_ccy.items(), key=lambda x: -x[1])[:5]
    ]

    return AnalyticsOverview(
        period_days=period_days,
        total_payments=total,
        total_volume=str(total_volume),
        avg_processing_time_seconds=round(avg_time, 2),
        success_rate=round(succeeded / total, 4) if total else 0.0,
        failure_rate=round(failed / total, 4) if total else 0.0,
        top_currencies=top_currencies,
        payments_by_status=dict(by_status),
    )


async def get_incident_performance(
    db: AsyncSession, org_id: str
) -> IncidentPerformance:
    res = await db.execute(
        select(Incident).where(Incident.org_id == org_id)
    )
    incidents = list(res.scalars().all())

    total = len(incidents)
    resolved = [i for i in incidents if i.status == "RESOLVED"]
    resolution_times = []
    for i in resolved:
        if i.created_at and i.resolved_at:
            resolution_times.append((i.resolved_at - i.created_at).total_seconds() / 60)

    by_severity: dict = defaultdict(int)
    by_root_cause: dict = defaultdict(int)
    for i in incidents:
        by_severity[i.severity] += 1
        if i.root_cause:
            by_root_cause[i.root_cause] += 1

    return IncidentPerformance(
        total_incidents=total,
        resolved_incidents=len(resolved),
        avg_resolution_minutes=round(sum(resolution_times) / len(resolution_times), 2) if resolution_times else 0.0,
        by_severity=dict(by_severity),
        by_root_cause=dict(by_root_cause),
    )


async def get_business_impact(
    db: AsyncSession, org_id: str
) -> BusinessImpact:
    res = await db.execute(
        select(Incident).where(
            Incident.org_id == org_id,
            Incident.financial_impact.isnot(None),
        )
    )
    incidents = list(res.scalars().all())

    total_impact = Decimal("0")
    for i in incidents:
        try:
            total_impact += Decimal(i.financial_impact)
        except Exception:
            pass

    count = len(incidents)
    avg = total_impact / count if count else Decimal("0")

    # Payment failure cost from failed payments
    res2 = await db.execute(
        select(func.count()).where(Payment.org_id == org_id, Payment.status == "FAILED")
    )
    failed_count = res2.scalar_one()
    failure_cost = Decimal(str(failed_count)) * Decimal("150")  # estimated $150 per failed payment

    return BusinessImpact(
        total_financial_impact=str(total_impact),
        incidents_with_impact=count,
        avg_impact_per_incident=str(avg),
        payment_failure_cost=str(failure_cost),
    )


async def get_trends(
    db: AsyncSession, org_id: str, days: int = 14
) -> List[TrendPoint]:
    since = datetime.now(timezone.utc) - timedelta(days=days)

    res_p = await db.execute(
        select(Payment).where(Payment.org_id == org_id, Payment.created_at >= since)
    )
    payments = list(res_p.scalars().all())

    res_i = await db.execute(
        select(Incident).where(Incident.org_id == org_id, Incident.created_at >= since)
    )
    incidents = list(res_i.scalars().all())

    res_a = await db.execute(
        select(RiskAlert).where(RiskAlert.org_id == org_id, RiskAlert.created_at >= since)
    )
    alerts = list(res_a.scalars().all())

    # Group by date
    pay_by_day: dict = defaultdict(lambda: {"count": 0, "volume": Decimal("0")})
    for p in payments:
        d = p.created_at.date().isoformat()
        pay_by_day[d]["count"] += 1
        pay_by_day[d]["volume"] += Decimal(p.amount)

    inc_by_day: dict = defaultdict(int)
    for i in incidents:
        inc_by_day[i.created_at.date().isoformat()] += 1

    alert_by_day: dict = defaultdict(int)
    for a in alerts:
        alert_by_day[a.created_at.date().isoformat()] += 1

    base_date = datetime.now(timezone.utc).date()
    points = []
    for i in range(days):
        d = (base_date - timedelta(days=days - 1 - i)).isoformat()
        pdata = pay_by_day.get(d, {"count": 0, "volume": Decimal("0")})
        points.append(
            TrendPoint(
                date=d,
                payments=pdata["count"],
                incidents=inc_by_day.get(d, 0),
                alerts=alert_by_day.get(d, 0),
                volume=str(pdata["volume"]),
            )
        )
    return points
