"""Payment business logic service."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Optional, List, Tuple

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.models.base import Payment, PaymentAttempt, Account, Beneficiary
from app.schemas.schemas import PaymentCreate, PaymentUpdate, PaymentTimelineEvent
import app.services.audit_service as audit_svc


def _uuid() -> str:
    return str(uuid.uuid4())


def _payment_number() -> str:
    ts = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    return f"PAY-{ts}-{_uuid()[:6].upper()}"


async def create_payment(
    db: AsyncSession,
    data: PaymentCreate,
    created_by: Optional[str] = None,
    actor_role: Optional[str] = None,
) -> Payment:
    payment = Payment(
        id=_uuid(),
        org_id=data.org_id,
        payment_number=_payment_number(),
        status="CREATED",
        amount=data.amount,
        currency=data.currency,
        beneficiary_id=data.beneficiary_id,
        account_id=data.account_id,
        reference=data.reference,
        description=data.description,
        idempotency_key=data.idempotency_key,
        created_by=created_by,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    db.add(payment)

    attempt = PaymentAttempt(
        id=_uuid(),
        payment_id=payment.id,
        status="CREATED",
        created_at=datetime.now(timezone.utc),
    )
    db.add(attempt)

    await audit_svc.log_event(
        db,
        "PAYMENT_CREATED",
        org_id=data.org_id,
        actor_id=created_by,
        actor_role=actor_role,
        entity_type="Payment",
        entity_id=payment.id,
        after_state={"payment_number": payment.payment_number, "amount": data.amount},
    )
    await db.commit()
    await db.refresh(payment)
    return payment


async def get_payments(
    db: AsyncSession,
    org_id: Optional[str] = None,
    status: Optional[str] = None,
    currency: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
) -> Tuple[List[Payment], int]:
    query = (
        select(Payment)
        .options(
            selectinload(Payment.beneficiary),
            selectinload(Payment.account),
        )
    )
    if org_id:
        query = query.where(Payment.org_id == org_id)
    if status:
        query = query.where(Payment.status == status)
    if currency:
        query = query.where(Payment.currency == currency)

    count_q = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_q)).scalar_one()

    query = query.order_by(Payment.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    return list(result.scalars().all()), total


async def get_payment(db: AsyncSession, payment_id: str) -> Optional[Payment]:
    result = await db.execute(
        select(Payment)
        .options(
            selectinload(Payment.beneficiary),
            selectinload(Payment.account),
            selectinload(Payment.attempts),
        )
        .where(Payment.id == payment_id)
    )
    return result.scalar_one_or_none()


async def update_payment_status(
    db: AsyncSession,
    payment: Payment,
    new_status: str,
    actor_id: Optional[str] = None,
    actor_role: Optional[str] = None,
    reason: Optional[str] = None,
    provider_ref: Optional[str] = None,
    error_message: Optional[str] = None,
) -> Payment:
    old_status = payment.status
    payment.status = new_status
    payment.updated_at = datetime.now(timezone.utc)
    if provider_ref:
        payment.provider_ref = provider_ref
    if error_message:
        payment.error_message = error_message
    if new_status in ("SUCCEEDED", "FAILED", "CANCELLED"):
        payment.completed_at = datetime.now(timezone.utc)
    if new_status == "SUBMITTED":
        payment.submitted_at = datetime.now(timezone.utc)

    attempt = PaymentAttempt(
        id=_uuid(),
        payment_id=payment.id,
        status=new_status,
        created_at=datetime.now(timezone.utc),
    )
    db.add(attempt)

    await audit_svc.log_event(
        db,
        "PAYMENT_STATUS_CHANGED",
        org_id=payment.org_id,
        actor_id=actor_id,
        actor_role=actor_role,
        entity_type="Payment",
        entity_id=payment.id,
        before_state={"status": old_status},
        after_state={"status": new_status},
        reason=reason,
    )
    await db.commit()
    await db.refresh(payment)
    return payment


async def retry_payment(
    db: AsyncSession,
    payment: Payment,
    actor_id: Optional[str] = None,
    actor_role: Optional[str] = None,
) -> Payment:
    new_payment = Payment(
        id=_uuid(),
        org_id=payment.org_id,
        payment_number=_payment_number(),
        status="CREATED",
        amount=payment.amount,
        currency=payment.currency,
        beneficiary_id=payment.beneficiary_id,
        account_id=payment.account_id,
        reference=payment.reference,
        description=payment.description,
        created_by=actor_id,
        parent_payment_id=payment.id,
        retry_count=payment.retry_count + 1,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    payment.retry_count += 1
    db.add(new_payment)

    await audit_svc.log_event(
        db,
        "PAYMENT_RETRY",
        org_id=payment.org_id,
        actor_id=actor_id,
        actor_role=actor_role,
        entity_type="Payment",
        entity_id=payment.id,
        after_state={"new_payment_id": new_payment.id, "retry_count": new_payment.retry_count},
    )
    await db.commit()
    await db.refresh(new_payment)
    return new_payment


async def get_payment_timeline(
    db: AsyncSession, payment: Payment
) -> List[PaymentTimelineEvent]:
    result = await db.execute(
        select(PaymentAttempt)
        .where(PaymentAttempt.payment_id == payment.id)
        .order_by(PaymentAttempt.created_at.asc())
    )
    attempts = list(result.scalars().all())

    timeline = []
    timeline.append(
        PaymentTimelineEvent(
            timestamp=payment.created_at,
            event="Payment Created",
            status="CREATED",
            detail=f"Payment {payment.payment_number} created for {payment.currency} {payment.amount}",
        )
    )
    for att in attempts:
        timeline.append(
            PaymentTimelineEvent(
                timestamp=att.created_at,
                event=f"Status: {att.status}",
                status=att.status,
                detail=att.response_payload,
            )
        )
    return timeline
