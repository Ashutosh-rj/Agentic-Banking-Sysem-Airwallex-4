"""
KAIZEN FinTech — Dashboard API Routes
GET /api/v1/dashboard/summary
GET /api/v1/dashboard/activity
GET /api/v1/dashboard/trends
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from datetime import datetime, timezone, timedelta
from typing import List

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.base import (
    User, Payment, Incident, Account, ReconciliationRecord, Notification, RiskAlert, AuditLog
)
from app.schemas.schemas import (
    DashboardSummaryResponse, AccountResponse, ActivityItem, TrendPoint
)

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/summary", response_model=DashboardSummaryResponse)
async def get_summary(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    org_id = current_user.org_id
    now = datetime.now(timezone.utc)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

    # Accounts
    accts_result = await db.execute(
        select(Account).where(and_(Account.org_id == org_id, Account.is_active == True))
    )
    accounts = accts_result.scalars().all()

    # Total available in USD equivalent (simplified — no FX conversion for demo)
    fx_rates = {"USD": 1.0, "EUR": 1.08, "GBP": 1.27, "SGD": 0.74}
    total_usd = sum(
        float(a.available_balance) * fx_rates.get(a.currency, 1.0) for a in accounts
    )

    # Payments
    pay_count = await db.execute(select(func.count(Payment.id)).where(Payment.org_id == org_id))
    total_payments = pay_count.scalar_one()

    pending_result = await db.execute(
        select(func.count(Payment.id), func.sum(Payment.amount)).where(
            and_(Payment.org_id == org_id, Payment.status.in_(["PENDING", "SUBMITTED", "UNKNOWN", "REQUIRES_REVIEW"]))
        )
    )
    pending_row = pending_result.one()
    pending_count = pending_row[0] or 0
    pending_amount = f"{float(pending_row[1] or 0):.2f}"

    failed_today = await db.execute(
        select(func.count(Payment.id)).where(
            and_(Payment.org_id == org_id, Payment.status == "FAILED",
                 Payment.updated_at >= today_start)
        )
    )
    failed_count = failed_today.scalar_one()

    succeeded_today = await db.execute(
        select(func.count(Payment.id)).where(
            and_(Payment.org_id == org_id, Payment.status == "SUCCEEDED",
                 Payment.updated_at >= today_start)
        )
    )
    succeeded_count = succeeded_today.scalar_one()

    # Incidents
    open_inc = await db.execute(
        select(func.count(Incident.id)).where(
            and_(Incident.org_id == org_id, Incident.status.in_(["open", "investigating", "pending_action", "escalated"]))
        )
    )
    open_incidents = open_inc.scalar_one()

    critical_inc = await db.execute(
        select(func.count(Incident.id)).where(
            and_(Incident.org_id == org_id, Incident.severity == "critical",
                 Incident.status.not_in(["resolved", "closed"]))
        )
    )
    critical_incidents = critical_inc.scalar_one()

    sla_breach = await db.execute(
        select(func.count(Incident.id)).where(
            and_(Incident.org_id == org_id,
                 Incident.sla_deadline < now,
                 Incident.status.not_in(["resolved", "closed"]))
        )
    )
    sla_breach_count = sla_breach.scalar_one()

    # Reconciliation exceptions
    recon_exc = await db.execute(
        select(func.count(ReconciliationRecord.id)).where(
            ReconciliationRecord.match_status.in_(["unmatched", "conflict", "duplicate_candidate"])
        )
    )
    unresolved_exceptions = recon_exc.scalar_one()

    # Notifications
    notifs = await db.execute(
        select(func.count(Notification.id)).where(
            and_(Notification.user_id == current_user.id, Notification.is_read == False)
        )
    )
    unread_notifs = notifs.scalar_one()

    return DashboardSummaryResponse(
        total_available_usd_equivalent=f"{total_usd:.2f}",
        accounts=[AccountResponse.model_validate(a) for a in accounts],
        total_payments=total_payments,
        pending_payments=pending_count,
        pending_amount=pending_amount,
        failed_today=failed_count,
        succeeded_today=succeeded_count,
        open_incidents=open_incidents,
        critical_incidents=critical_incidents,
        sla_breach_count=sla_breach_count,
        unresolved_exceptions=unresolved_exceptions,
        unread_notifications=unread_notifs,
    )


@router.get("/activity", response_model=List[ActivityItem])
async def get_activity(
    limit: int = Query(20, le=50),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    org_id = current_user.org_id
    items = []

    # Recent payments
    pays = await db.execute(
        select(Payment).where(Payment.org_id == org_id)
        .order_by(Payment.created_at.desc()).limit(10)
    )
    for p in pays.scalars().all():
        items.append(ActivityItem(
            id=p.id, type="payment",
            title=f"Payment {p.payment_number}",
            description=f"{p.currency} {float(p.amount):,.2f} — {p.status}",
            timestamp=p.created_at, status=p.status,
            amount=p.amount, currency=p.currency,
        ))

    # Recent incidents
    incs = await db.execute(
        select(Incident).where(Incident.org_id == org_id)
        .order_by(Incident.created_at.desc()).limit(8)
    )
    for i in incs.scalars().all():
        items.append(ActivityItem(
            id=i.id, type="incident",
            title=f"Incident {i.incident_number}",
            description=i.title,
            timestamp=i.created_at, status=i.status,
            severity=i.severity,
            amount=i.financial_impact, currency=i.financial_currency,
        ))

    # Sort all by timestamp descending
    items.sort(key=lambda x: x.timestamp, reverse=True)
    return items[:limit]


@router.get("/trends", response_model=List[TrendPoint])
async def get_trends(
    days: int = Query(14, ge=7, le=90),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    org_id = current_user.org_id
    now = datetime.now(timezone.utc)
    trends = []

    for i in range(days - 1, -1, -1):
        day = now - timedelta(days=i)
        day_start = day.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=1)

        pay_count = await db.execute(
            select(func.count(Payment.id)).where(
                and_(Payment.org_id == org_id,
                     Payment.created_at >= day_start,
                     Payment.created_at < day_end)
            )
        )
        pay_amt = await db.execute(
            select(func.sum(Payment.amount)).where(
                and_(Payment.org_id == org_id, Payment.status == "SUCCEEDED",
                     Payment.completed_at >= day_start, Payment.completed_at < day_end)
            )
        )
        inc_count = await db.execute(
            select(func.count(Incident.id)).where(
                and_(Incident.org_id == org_id,
                     Incident.created_at >= day_start, Incident.created_at < day_end)
            )
        )

        trends.append(TrendPoint(
            date=day.strftime("%Y-%m-%d"),
            payments=pay_count.scalar_one(),
            incidents=inc_count.scalar_one(),
            amount=f"{float(pay_amt.scalar_one() or 0):.2f}",
        ))

    return trends
