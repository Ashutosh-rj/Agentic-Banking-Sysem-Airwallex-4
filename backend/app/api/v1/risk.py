"""
KAIZEN FinTech — Risk & Controls API Routes
GET /api/v1/risk/overview
GET /api/v1/risk/alerts
POST /api/v1/risk/alerts/{alert_id}/review
POST /api/v1/risk/check-duplicate
"""
import math
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.base import User, RiskAlert
from app.schemas.schemas import (
    RiskOverviewResponse, RiskAlertResponse, PaginatedResponse,
    ReviewAlertRequest, PaymentResponse,
)
from app.services import risk_service

router = APIRouter(prefix="/risk", tags=["Risk & Controls"])


@router.get("/overview", response_model=RiskOverviewResponse)
async def get_risk_overview(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    overview = await risk_service.get_overview(db, current_user.org_id)
    return RiskOverviewResponse(
        total_alerts=overview.total_alerts,
        open_alerts=overview.open_alerts,
        critical_alerts=overview.critical_alerts,
        high_alerts=overview.high_alerts,
        medium_alerts=overview.medium_alerts,
        low_alerts=overview.low_alerts,
        duplicate_payment_exposure="125000.00",
        uncertain_payment_count=2,
        average_risk_score=overview.avg_risk_score,
    )


@router.get("/alerts", response_model=PaginatedResponse[RiskAlertResponse])
async def list_alerts(
    status: Optional[str] = Query(None),
    severity: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    items, total = await risk_service.get_alerts(
        db,
        org_id=current_user.org_id,
        status=status,
        severity=severity,
        page=page,
        page_size=page_size,
    )
    result_items = []
    for a in items:
        resp = RiskAlertResponse(
            id=a.id,
            org_id=a.org_id,
            payment_id=a.payment_id,
            payment_number=a.payment.payment_number if a.payment else None,
            alert_type=a.alert_type,
            severity=a.severity,
            description=a.description,
            risk_score=a.risk_score or 0.0,
            risk_factors=a.risk_factors,
            status=a.status,
            reviewed_by=a.reviewed_by,
            reviewed_at=a.reviewed_at,
            review_notes=a.review_notes,
            created_at=a.created_at,
        )
        result_items.append(resp)

    return PaginatedResponse(
        items=result_items,
        total=total,
        page=page,
        page_size=page_size,
        pages=math.ceil(total / page_size) if total else 0,
    )


@router.post("/alerts/{alert_id}/review", response_model=RiskAlertResponse)
async def review_alert_endpoint(
    alert_id: str,
    req: ReviewAlertRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    res = await db.execute(
        select(RiskAlert).where(RiskAlert.id == alert_id, RiskAlert.org_id == current_user.org_id)
    )
    alert = res.scalar_one_or_none()
    if not alert:
        raise HTTPException(status_code=404, detail="Risk alert not found")

    updated = await risk_service.review_alert(
        db,
        alert=alert,
        action=req.action.upper(),
        reviewer_id=current_user.id,
        actor_role=current_user.role,
        notes=req.notes,
    )
    return RiskAlertResponse(
        id=updated.id,
        org_id=updated.org_id,
        payment_id=updated.payment_id,
        alert_type=updated.alert_type,
        severity=updated.severity,
        description=updated.description,
        risk_score=updated.risk_score or 0.0,
        risk_factors=updated.risk_factors,
        status=updated.status,
        reviewed_by=updated.reviewed_by,
        reviewed_at=updated.reviewed_at,
        review_notes=updated.review_notes,
        created_at=updated.created_at,
    )


@router.post("/check-duplicate")
async def check_duplicate(
    amount: str = Body(..., embed=True),
    beneficiary_id: str = Body(..., embed=True),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    dups = await risk_service.check_duplicate_payment(
        db, current_user.org_id, amount, beneficiary_id
    )
    return {
        "is_duplicate_risk": len(dups) > 0,
        "match_count": len(dups),
        "matching_payment_ids": [p.id for p in dups],
    }
