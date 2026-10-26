"""
KAIZEN FinTech — Payments API Routes
Full CRUD + retry + timeline
"""
import uuid
import json
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload
from datetime import datetime, timezone
from typing import Optional, List

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.base import User, Payment, PaymentAttempt, Incident, Account, Beneficiary, AuditLog
from app.schemas.schemas import (
    PaymentCreate, PaymentResponse, PaymentTimelineEvent, PaginatedResponse, MessageResponse
)

router = APIRouter(prefix="/payments", tags=["Payments"])

VALID_TRANSITIONS = {
    "CREATED": ["VALIDATING", "CANCELLED"],
    "VALIDATING": ["SUBMITTED", "FAILED", "CANCELLED"],
    "SUBMITTED": ["PENDING", "SUCCEEDED", "FAILED", "UNKNOWN"],
    "PENDING": ["SUCCEEDED", "FAILED", "UNKNOWN", "REQUIRES_REVIEW"],
    "UNKNOWN": ["REQUIRES_REVIEW", "SUCCEEDED", "FAILED"],
    "REQUIRES_REVIEW": ["SUBMITTED", "CANCELLED"],
    "FAILED": ["CREATED"],  # allow retry by creating fresh attempt
    "SUCCEEDED": [],
    "CANCELLED": [],
}


def payment_to_response(p: Payment, beneficiary: Optional[Beneficiary] = None, account: Optional[Account] = None) -> PaymentResponse:
    return PaymentResponse(
        id=p.id, org_id=p.org_id, payment_number=p.payment_number, status=p.status,
        amount=p.amount, currency=p.currency, beneficiary_id=p.beneficiary_id,
        account_id=p.account_id, beneficiary_name=beneficiary.name if beneficiary else None,
        account_name=account.name if account else None,
        reference=p.reference, description=p.description,
        idempotency_key=p.idempotency_key, provider_ref=p.provider_ref,
        error_message=p.error_message, retry_count=p.retry_count,
        parent_payment_id=p.parent_payment_id, is_demo=p.is_demo,
        submitted_at=p.submitted_at, completed_at=p.completed_at,
        created_at=p.created_at, updated_at=p.updated_at,
    )


@router.get("", response_model=PaginatedResponse)
async def list_payments(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    currency: Optional[str] = None,
    search: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    org_id = current_user.org_id
    q = select(Payment).where(Payment.org_id == org_id)

    if status:
        statuses = status.split(",")
        q = q.where(Payment.status.in_(statuses))
    if currency:
        q = q.where(Payment.currency == currency.upper())
    if search:
        q = q.where(or_(
            Payment.payment_number.ilike(f"%{search}%"),
            Payment.reference.ilike(f"%{search}%"),
        ))

    count_q = select(func.count()).select_from(q.subquery())
    total = (await db.execute(count_q)).scalar_one()

    q = q.order_by(Payment.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
    payments = (await db.execute(q)).scalars().all()

    # Enrich with beneficiary/account names
    items = []
    for p in payments:
        ben = None
        acc = None
        if p.beneficiary_id:
            ben_r = await db.execute(select(Beneficiary).where(Beneficiary.id == p.beneficiary_id))
            ben = ben_r.scalar_one_or_none()
        if p.account_id:
            acc_r = await db.execute(select(Account).where(Account.id == p.account_id))
            acc = acc_r.scalar_one_or_none()
        items.append(payment_to_response(p, ben, acc))

    return PaginatedResponse(
        items=items, total=total, page=page, page_size=page_size,
        pages=(total + page_size - 1) // page_size,
    )


@router.post("", response_model=PaymentResponse, status_code=201)
async def create_payment(
    req: PaymentCreate, request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if current_user.role not in ("admin", "treasury_manager", "payment_ops"):
        raise HTTPException(status_code=403, detail="Insufficient permissions to create payments")

    org_id = current_user.org_id

    # Idempotency check
    if req.idempotency_key:
        existing = await db.execute(
            select(Payment).where(Payment.idempotency_key == req.idempotency_key)
        )
        existing_pay = existing.scalar_one_or_none()
        if existing_pay:
            return payment_to_response(existing_pay)

    # Validate account
    acc_result = await db.execute(
        select(Account).where(and_(Account.id == req.account_id, Account.org_id == org_id))
    )
    account = acc_result.scalar_one_or_none()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    # Validate beneficiary
    ben_result = await db.execute(
        select(Beneficiary).where(and_(Beneficiary.id == req.beneficiary_id, Beneficiary.org_id == org_id))
    )
    beneficiary = ben_result.scalar_one_or_none()
    if not beneficiary:
        raise HTTPException(status_code=404, detail="Beneficiary not found")

    # Funds check
    if float(account.available_balance) < float(req.amount):
        raise HTTPException(status_code=422, detail="Insufficient available balance")

    # Duplicate detection
    recent_dup = await db.execute(
        select(Payment).where(and_(
            Payment.org_id == org_id,
            Payment.beneficiary_id == req.beneficiary_id,
            Payment.amount == req.amount,
            Payment.currency == req.currency,
            Payment.status.in_(["SUCCEEDED", "PENDING", "SUBMITTED", "UNKNOWN"]),
        )).order_by(Payment.created_at.desc()).limit(1)
    )
    dup = recent_dup.scalar_one_or_none()
    if dup:
        from datetime import timedelta
        if (datetime.now(timezone.utc) - dup.created_at).days < 1:
            raise HTTPException(
                status_code=409,
                detail=f"Potential duplicate detected: payment {dup.payment_number} with identical amount/beneficiary within 24h. Use idempotency key or confirm intent.",
            )

    # Generate payment number
    count_result = await db.execute(select(func.count(Payment.id)).where(Payment.org_id == org_id))
    count = count_result.scalar_one()
    pay_num = f"PAY-{2024000 + count + 1:07d}"

    p_id = str(uuid.uuid4())
    payment = Payment(
        id=p_id, org_id=org_id, payment_number=pay_num, status="CREATED",
        amount=req.amount, currency=req.currency, beneficiary_id=req.beneficiary_id,
        account_id=req.account_id, reference=req.reference, description=req.description,
        idempotency_key=req.idempotency_key or f"auto-{p_id}",
        is_demo=True, created_by=current_user.id,
    )
    db.add(payment)

    # Reserve funds
    account.reserved_balance = str(float(account.reserved_balance) + float(req.amount))
    account.available_balance = str(float(account.available_balance) - float(req.amount))

    al = AuditLog(
        id=str(uuid.uuid4()), org_id=org_id, actor_id=current_user.id,
        actor_email=current_user.email, actor_role=current_user.role,
        action="payment_created", entity_type="payment", entity_id=p_id,
        after_state=json.dumps({"status": "CREATED", "amount": req.amount, "currency": req.currency}),
        ip_address=request.client.host if request.client else None,
    )
    db.add(al)
    await db.commit()

    return payment_to_response(payment, beneficiary, account)


@router.get("/{payment_id}", response_model=PaymentResponse)
async def get_payment(
    payment_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Payment).where(and_(Payment.id == payment_id, Payment.org_id == current_user.org_id))
    )
    payment = result.scalar_one_or_none()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")

    ben = None
    acc = None
    if payment.beneficiary_id:
        ben_r = await db.execute(select(Beneficiary).where(Beneficiary.id == payment.beneficiary_id))
        ben = ben_r.scalar_one_or_none()
    if payment.account_id:
        acc_r = await db.execute(select(Account).where(Account.id == payment.account_id))
        acc = acc_r.scalar_one_or_none()

    return payment_to_response(payment, ben, acc)


@router.get("/{payment_id}/timeline", response_model=List[PaymentTimelineEvent])
async def get_payment_timeline(
    payment_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Payment).where(and_(Payment.id == payment_id, Payment.org_id == current_user.org_id))
    )
    payment = result.scalar_one_or_none()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")

    events = []
    events.append(PaymentTimelineEvent(
        timestamp=payment.created_at, event="Payment Created",
        description=f"Payment {payment.payment_number} created for {payment.currency} {float(payment.amount):,.2f}",
        status="CREATED",
    ))

    attempts_result = await db.execute(
        select(PaymentAttempt).where(PaymentAttempt.payment_id == payment_id)
        .order_by(PaymentAttempt.created_at)
    )
    for attempt in attempts_result.scalars().all():
        events.append(PaymentTimelineEvent(
            timestamp=attempt.created_at, event=f"Payment Attempt #{attempt.attempt_number}",
            description=f"Status: {attempt.status}. {attempt.error_message or ''}",
            status=attempt.status,
        ))

    if payment.submitted_at:
        events.append(PaymentTimelineEvent(
            timestamp=payment.submitted_at, event="Submitted to Provider",
            description=f"Payment submitted. Provider ref: {payment.provider_ref or 'N/A'}",
            status="SUBMITTED",
        ))

    if payment.completed_at:
        events.append(PaymentTimelineEvent(
            timestamp=payment.completed_at, event=f"Payment {payment.status.title()}",
            description=f"Final status: {payment.status}. {payment.error_message or ''}",
            status=payment.status,
        ))

    events.sort(key=lambda e: e.timestamp)
    return events


@router.post("/{payment_id}/retry", response_model=PaymentResponse)
async def retry_payment(
    payment_id: str, request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if current_user.role not in ("admin", "treasury_manager"):
        raise HTTPException(status_code=403, detail="Retry requires treasury manager or admin role")

    result = await db.execute(
        select(Payment).where(and_(Payment.id == payment_id, Payment.org_id == current_user.org_id))
    )
    payment = result.scalar_one_or_none()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")

    if payment.status not in ("FAILED",):
        raise HTTPException(
            status_code=409,
            detail=f"Payment in status {payment.status} cannot be retried. Only FAILED payments are eligible. UNKNOWN/REQUIRES_REVIEW payments must be resolved via incident workflow first.",
        )

    if payment.retry_count >= 3:
        raise HTTPException(status_code=409, detail="Maximum retry attempts (3) reached. Please create a new payment.")

    # Safe retry — preserve original, simulate new attempt
    payment.status = "SUBMITTED"
    payment.retry_count += 1
    payment.error_message = None
    payment.updated_at = datetime.now(timezone.utc)

    attempt = PaymentAttempt(
        id=str(uuid.uuid4()), payment_id=payment_id,
        attempt_number=payment.retry_count + 1, status="SUBMITTED",
        request_payload=json.dumps({"retry": True, "attempt": payment.retry_count}),
        response_payload=json.dumps({"status": "SUBMITTED", "message": "Retry submitted (demo mode)"}),
    )
    db.add(attempt)

    al = AuditLog(
        id=str(uuid.uuid4()), org_id=current_user.org_id, actor_id=current_user.id,
        actor_email=current_user.email, actor_role=current_user.role,
        action="payment_retried", entity_type="payment", entity_id=payment_id,
        before_state=json.dumps({"status": "FAILED", "retry_count": payment.retry_count - 1}),
        after_state=json.dumps({"status": "SUBMITTED", "retry_count": payment.retry_count}),
        reason="Manual retry authorized by treasury manager",
        ip_address=request.client.host if request.client else None,
    )
    db.add(al)
    await db.commit()

    return payment_to_response(payment)
