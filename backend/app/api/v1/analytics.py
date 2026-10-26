"""
KAIZEN FinTech — Analytics & Business Impact API Routes
GET /api/v1/analytics/overview
GET /api/v1/analytics/incident-performance
GET /api/v1/analytics/business-impact
GET /api/v1/analytics/trends
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.base import User
from app.schemas.schemas import (
    AnalyticsOverviewResponse, IncidentPerformanceEntry,
    BusinessImpactResponse, TrendPoint,
)
from app.services import analytics_service

router = APIRouter(prefix="/analytics", tags=["Analytics & Business Impact"])


@router.get("/overview", response_model=AnalyticsOverviewResponse)
async def get_overview(
    period_days: int = Query(30, ge=1, le=365),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    overview = await analytics_service.get_overview(
        db, current_user.org_id, period_days=period_days
    )
    return overview


@router.get("/incident-performance", response_model=IncidentPerformanceEntry)
async def get_incident_performance(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    perf = await analytics_service.get_incident_performance(db, current_user.org_id)
    return perf


@router.get("/business-impact", response_model=BusinessImpactResponse)
async def get_business_impact(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    impact = await analytics_service.get_business_impact(db, current_user.org_id)
    return impact


@router.get("/trends", response_model=List[TrendPoint])
async def get_trends(
    days: int = Query(14, ge=7, le=90),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    trends = await analytics_service.get_trends(db, current_user.org_id, days=days)
    return trends
