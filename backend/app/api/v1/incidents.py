"""Incident routes: CRUD + investigate + actions + assign + resolve."""
import math
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.base import User, Incident
from app.schemas.schemas import (
    IncidentCreate, IncidentUpdate, IncidentResponse, EvidenceCreate,
    EvidenceResponse, PaginatedResponse, AgentExecutionResponse,
)
from app.services import incident_service

router = APIRouter(prefix="/incidents", tags=["incidents"])


@router.post("", response_model=IncidentResponse, status_code=201)
async def create_incident(
    data: IncidentCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await incident_service.create_incident(
        db, data, created_by=current_user.id, actor_role=current_user.role
    )


@router.get("", response_model=PaginatedResponse[IncidentResponse])
async def list_incidents(
    status: Optional[str] = Query(None),
    severity: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    items, total = await incident_service.get_incidents(
        db,
        org_id=current_user.org_id,
        status=status,
        severity=severity,
        page=page,
        page_size=page_size,
    )
    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        pages=math.ceil(total / page_size) if total else 0,
    )


@router.get("/{incident_id}", response_model=IncidentResponse)
async def get_incident(
    incident_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    inc = await incident_service.get_incident(db, incident_id)
    if not inc or inc.org_id != current_user.org_id:
        raise HTTPException(status_code=404, detail="Incident not found")
    return inc


@router.patch("/{incident_id}", response_model=IncidentResponse)
async def update_incident(
    incident_id: str,
    data: IncidentUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    inc = await incident_service.get_incident(db, incident_id)
    if not inc or inc.org_id != current_user.org_id:
        raise HTTPException(status_code=404, detail="Incident not found")

    update_data = data.model_dump(exclude_none=True)
    for k, v in update_data.items():
        setattr(inc, k, v)
    from datetime import datetime, timezone
    inc.updated_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(inc)
    return inc


@router.post("/{incident_id}/investigate")
async def investigate(
    incident_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    inc = await incident_service.get_incident(db, incident_id)
    if not inc or inc.org_id != current_user.org_id:
        raise HTTPException(status_code=404, detail="Incident not found")
    report = await incident_service.investigate_incident(db, inc, actor_id=current_user.id)
    return {"message": "Investigation complete", "report": report}


@router.post("/{incident_id}/resolve", response_model=IncidentResponse)
async def resolve(
    incident_id: str,
    notes: Optional[str] = Body(None, embed=True),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    inc = await incident_service.get_incident(db, incident_id)
    if not inc or inc.org_id != current_user.org_id:
        raise HTTPException(status_code=404, detail="Incident not found")
    return await incident_service.resolve_incident(
        db, inc, resolution_notes=notes,
        actor_id=current_user.id, actor_role=current_user.role
    )


@router.post("/{incident_id}/assign", response_model=IncidentResponse)
async def assign(
    incident_id: str,
    assignee_id: str = Body(..., embed=True),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    inc = await incident_service.get_incident(db, incident_id)
    if not inc or inc.org_id != current_user.org_id:
        raise HTTPException(status_code=404, detail="Incident not found")
    return await incident_service.assign_incident(db, inc, assignee_id, actor_id=current_user.id)


@router.post("/{incident_id}/evidence", response_model=EvidenceResponse, status_code=201)
async def add_evidence(
    incident_id: str,
    data: EvidenceCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    inc = await incident_service.get_incident(db, incident_id)
    if not inc or inc.org_id != current_user.org_id:
        raise HTTPException(status_code=404, detail="Incident not found")
    return await incident_service.add_evidence(db, inc, data, actor_id=current_user.id)


@router.get("/{incident_id}/actions")
async def get_actions(
    incident_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    inc = await incident_service.get_incident(db, incident_id)
    if not inc or inc.org_id != current_user.org_id:
        raise HTTPException(status_code=404, detail="Incident not found")

    import json
    actions = []
    if inc.ai_report:
        try:
            report = json.loads(inc.ai_report)
            actions = report.get("recommended_actions", [])
        except Exception:
            pass

    return {"incident_id": incident_id, "actions": actions}
