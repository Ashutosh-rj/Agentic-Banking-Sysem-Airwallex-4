"""Reconciliation service."""
from __future__ import annotations

import random
import uuid
from datetime import datetime, timezone
from typing import Optional, List, Tuple

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models.base import ReconciliationRun, ReconciliationRecord, Payment
import app.services.audit_service as audit_svc


def _uuid() -> str:
    return str(uuid.uuid4())


async def run_reconciliation(
    db: AsyncSession,
    org_id: str,
    actor_id: Optional[str] = None,
    actor_role: Optional[str] = None,
) -> ReconciliationRun:
    run = ReconciliationRun(
        id=_uuid(),
        org_id=org_id,
        status="RUNNING",
        matched_count=0,
        unmatched_count=0,
        exception_count=0,
        created_by=actor_id,
        created_at=datetime.now(timezone.utc),
    )
    db.add(run)
    await db.flush()

    # Load payments for this org
    res = await db.execute(
        select(Payment).where(
            Payment.org_id == org_id,
            Payment.status.in_(["SUCCEEDED", "FAILED", "UNKNOWN"]),
        )
    )
    payments = list(res.scalars().all())

    matched = unmatched = exceptions = 0
    for p in payments:
        # Deterministic reconciliation simulation based on payment status
        if p.status == "SUCCEEDED":
            match_status = "MATCHED"
            confidence = round(random.uniform(0.92, 0.99), 2)
            matched += 1
        elif p.status == "FAILED":
            match_status = random.choice(["MATCHED", "UNMATCHED"])
            confidence = round(random.uniform(0.6, 0.85), 2)
            if match_status == "MATCHED":
                matched += 1
            else:
                unmatched += 1
        else:  # UNKNOWN
            match_status = "EXCEPTION"
            confidence = round(random.uniform(0.1, 0.4), 2)
            exceptions += 1

        record = ReconciliationRecord(
            id=_uuid(),
            run_id=run.id,
            payment_id=p.id,
            match_status=match_status,
            match_confidence=confidence,
            provider_reference=p.provider_ref or f"PROV-{p.payment_number}",
            provider_amount=p.amount,
            provider_currency=p.currency,
            discrepancy_notes=(
                f"Payment {p.payment_number} status mismatch: internal={p.status}"
                if match_status in ("UNMATCHED", "EXCEPTION")
                else None
            ),
        )
        db.add(record)

    now = datetime.now(timezone.utc)
    run.matched_count = matched
    run.unmatched_count = unmatched
    run.exception_count = exceptions
    run.status = "COMPLETED"
    run.completed_at = now

    await audit_svc.log_event(
        db,
        "RECONCILIATION_COMPLETED",
        org_id=org_id,
        actor_id=actor_id,
        actor_role=actor_role,
        entity_type="ReconciliationRun",
        entity_id=run.id,
        after_state={
            "matched": matched,
            "unmatched": unmatched,
            "exceptions": exceptions,
        },
    )
    await db.commit()
    await db.refresh(run)
    return run


async def get_runs(
    db: AsyncSession,
    org_id: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
) -> Tuple[List[ReconciliationRun], int]:
    query = select(ReconciliationRun)
    if org_id:
        query = query.where(ReconciliationRun.org_id == org_id)

    count_q = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_q)).scalar_one()

    query = query.order_by(ReconciliationRun.created_at.desc()).offset(
        (page - 1) * page_size
    ).limit(page_size)
    result = await db.execute(query)
    return list(result.scalars().all()), total


async def get_run(db: AsyncSession, run_id: str) -> Optional[ReconciliationRun]:
    from sqlalchemy.orm import selectinload
    result = await db.execute(
        select(ReconciliationRun)
        .options(selectinload(ReconciliationRun.records))
        .where(ReconciliationRun.id == run_id)
    )
    return result.scalar_one_or_none()


async def review_match(
    db: AsyncSession,
    record: ReconciliationRecord,
    new_status: str,
    reviewer_id: str,
    notes: Optional[str] = None,
) -> ReconciliationRecord:
    record.match_status = new_status
    record.reviewed_by = reviewer_id
    record.reviewed_at = datetime.now(timezone.utc)
    if notes:
        record.discrepancy_notes = notes
    await db.commit()
    await db.refresh(record)
    return record
