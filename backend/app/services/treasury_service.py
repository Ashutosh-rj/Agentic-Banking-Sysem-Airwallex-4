"""Treasury service — accounts, positions, obligations, forecast."""
from __future__ import annotations

from datetime import datetime, timezone, timedelta
from decimal import Decimal
from typing import Optional, List, Tuple
import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models.base import Account, PaymentObligation, Beneficiary
from app.schemas.schemas import TreasuryPosition, ForecastPoint, ObligationCreate


def _uuid() -> str:
    return str(uuid.uuid4())


async def get_accounts(
    db: AsyncSession,
    org_id: str,
    page: int = 1,
    page_size: int = 20,
) -> Tuple[List[Account], int]:
    query = select(Account).where(Account.org_id == org_id, Account.is_active == True)
    count_q = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_q)).scalar_one()
    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    return list(result.scalars().all()), total


async def get_positions(db: AsyncSession, org_id: str) -> List[TreasuryPosition]:
    res = await db.execute(
        select(Account).where(Account.org_id == org_id, Account.is_active == True)
    )
    accounts = list(res.scalars().all())

    positions: dict[str, dict] = {}
    for acc in accounts:
        ccy = acc.currency
        if ccy not in positions:
            positions[ccy] = {
                "currency": ccy,
                "available": Decimal("0"),
                "reserved": Decimal("0"),
                "total": Decimal("0"),
                "accounts": [],
            }
        positions[ccy]["available"] += Decimal(acc.available_balance)
        positions[ccy]["reserved"] += Decimal(acc.reserved_balance)
        positions[ccy]["total"] += Decimal(acc.total_balance)
        positions[ccy]["accounts"].append({
            "id": acc.id,
            "name": acc.name,
            "account_number": acc.account_number,
            "currency": acc.currency,
            "available_balance": acc.available_balance,
            "reserved_balance": acc.reserved_balance,
            "total_balance": acc.total_balance,
            "provider": acc.provider,
        })

    return [
        TreasuryPosition(
            currency=v["currency"],
            available=str(v["available"]),
            reserved=str(v["reserved"]),
            total=str(v["total"]),
            accounts=v["accounts"],
        )
        for v in positions.values()
    ]


async def get_obligations(
    db: AsyncSession,
    org_id: str,
    status: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
) -> Tuple[List[PaymentObligation], int]:
    query = select(PaymentObligation).where(PaymentObligation.org_id == org_id)
    if status:
        query = query.where(PaymentObligation.status == status)

    count_q = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_q)).scalar_one()
    query = query.order_by(PaymentObligation.due_date.asc()).offset(
        (page - 1) * page_size
    ).limit(page_size)
    result = await db.execute(query)
    return list(result.scalars().all()), total


async def create_obligation(
    db: AsyncSession, data: ObligationCreate
) -> PaymentObligation:
    ob = PaymentObligation(
        id=_uuid(),
        org_id=data.org_id,
        beneficiary_id=data.beneficiary_id,
        account_id=data.account_id,
        amount=data.amount,
        currency=data.currency,
        due_date=data.due_date,
        priority=data.priority,
        status="PENDING",
        description=data.description,
        created_at=datetime.now(timezone.utc),
    )
    db.add(ob)
    await db.commit()
    await db.refresh(ob)
    return ob


async def get_forecast(
    db: AsyncSession, org_id: str, days: int = 14
) -> List[ForecastPoint]:
    positions = await get_positions(db, org_id)
    res = await db.execute(
        select(PaymentObligation).where(
            PaymentObligation.org_id == org_id,
            PaymentObligation.status == "PENDING",
        )
    )
    obligations = list(res.scalars().all())

    # Build a day-by-day forecast
    forecast = []
    base_date = datetime.now(timezone.utc).date()

    # Use USD position as primary (fallback 0)
    balances: dict[str, Decimal] = {}
    for pos in positions:
        balances[pos.currency] = Decimal(pos.available)

    for i in range(days):
        day = base_date + timedelta(days=i)
        day_str = day.isoformat()

        # Sum obligations due on this day per currency
        day_obs: dict[str, Decimal] = {}
        for ob in obligations:
            ob_date = ob.due_date.date() if hasattr(ob.due_date, "date") else ob.due_date
            if ob_date == day:
                ccy = ob.currency
                day_obs[ccy] = day_obs.get(ccy, Decimal("0")) + Decimal(ob.amount)

        # Deduct from balances
        for ccy, amt in day_obs.items():
            balances[ccy] = balances.get(ccy, Decimal("0")) - amt

        primary_ccy = "USD" if "USD" in balances else (list(balances.keys())[0] if balances else "USD")
        forecast.append(
            ForecastPoint(
                date=day_str,
                projected_balance=str(balances.get(primary_ccy, Decimal("0"))),
                currency=primary_ccy,
                obligations_due=str(day_obs.get(primary_ccy, Decimal("0"))),
            )
        )
    return forecast
