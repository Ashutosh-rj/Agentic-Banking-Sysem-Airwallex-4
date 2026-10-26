"""Reconciliation routes."""
import math
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.base import User, ReconciliationRun, ReconciliationRecord
from app.schemas.schemas import (
    ReconciliationRunResponse, ReconciliationRecordResponse, PaginatedResponse,
)
from app.services import reconciliation_service

router = APIRouter(prefix="/reconciliation", tags=["reconciliation"])


@router.post("/runs", response_model=ReconciliationRunResponse, status_code=201)
async def trigger_reconciliation(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await reconciliation_service.run_reconciliation(
        db,
        org_id=current_user.org_id,
        actor_id=current_user.id,
        actor_role=current_user.role,
    )


@router.get("/runs", response_model=PaginatedResponse[ReconciliationRunResponse])
async def list_runs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    items, total = await reconciliation_service.get_runs(
        db, org_id=current_user.org_id, page=page, page_size=page_size
    )
    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        pages=math.ceil(total / page_size) if total else 0,
    )


@router.get("/runs/{run_id}", response_model=ReconciliationRunResponse)
async def get_run(
    run_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    run = await reconciliation_service.get_run(db, run_id)
    if not run or run.org_id != current_user.org_id:
        raise HTTPException(status_code=404, detail="Reconciliation run not found")
    return run


@router.patch("/records/{record_id}/review", response_model=ReconciliationRecordResponse)
async def review_record(
    record_id: str,
    match_status: str = Body(..., embed=True),
    notes: Optional[str] = Body(None, embed=True),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    res = await db.execute(
        select(ReconciliationRecord).where(ReconciliationRecord.id == record_id)
    )
    record = res.scalar_one_or_none()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    return await reconciliation_service.review_match(
        db, record, match_status, reviewer_id=current_user.id, notes=notes
    )
