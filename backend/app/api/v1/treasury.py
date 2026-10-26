"""Treasury routes."""
import math
from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.base import User
from app.schemas.schemas import (
    AccountResponse, TreasuryPosition, ObligationResponse, ObligationCreate,
    ForecastPoint, PaginatedResponse,
)
from app.services import treasury_service

router = APIRouter(prefix="/treasury", tags=["treasury"])


@router.get("/accounts", response_model=PaginatedResponse[AccountResponse])
async def list_accounts(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    items, total = await treasury_service.get_accounts(
        db, org_id=current_user.org_id, page=page, page_size=page_size
    )
    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        pages=math.ceil(total / page_size) if total else 0,
    )


@router.get("/positions", response_model=List[TreasuryPosition])
async def get_positions(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await treasury_service.get_positions(db, org_id=current_user.org_id)


@router.get("/obligations", response_model=PaginatedResponse[ObligationResponse])
async def list_obligations(
    status: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    items, total = await treasury_service.get_obligations(
        db, org_id=current_user.org_id, status=status, page=page, page_size=page_size
    )
    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        pages=math.ceil(total / page_size) if total else 0,
    )


@router.post("/obligations", response_model=ObligationResponse, status_code=201)
async def create_obligation(
    data: ObligationCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await treasury_service.create_obligation(db, data)


@router.get("/forecast", response_model=List[ForecastPoint])
async def get_forecast(
    days: int = Query(14, ge=1, le=90),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await treasury_service.get_forecast(db, org_id=current_user.org_id, days=days)
