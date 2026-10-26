"""
KAIZEN FinTech — Audit Logs API Routes
GET /api/v1/audit-logs
GET /api/v1/audit-logs/export
"""
import math
from typing import Optional
from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.base import User, AuditLog
from app.schemas.schemas import AuditLogResponse, PaginatedResponse
from app.services import audit_service

router = APIRouter(prefix="/audit-logs", tags=["Audit Logs"])


@router.get("", response_model=PaginatedResponse[AuditLogResponse])
async def list_audit_logs(
    actor_id: Optional[str] = Query(None),
    entity_type: Optional[str] = Query(None),
    entity_id: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    items, total = await audit_service.get_logs(
        db,
        org_id=current_user.org_id,
        actor_id=actor_id,
        entity_type=entity_type,
        entity_id=entity_id,
        page=page,
        page_size=page_size,
    )
    return PaginatedResponse(
        items=[AuditLogResponse.model_validate(log) for log in items],
        total=total,
        page=page,
        page_size=page_size,
        pages=math.ceil(total / page_size) if total else 0,
    )


@router.get("/export")
async def export_audit_logs(
    format: str = Query("csv", pattern="^(csv|json)$"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    items, total = await audit_service.get_logs(
        db,
        org_id=current_user.org_id,
        page=1,
        page_size=1000,
    )

    if format == "json":
        import json
        data = [AuditLogResponse.model_validate(log).model_dump(mode="json") for log in items]
        return Response(
            content=json.dumps(data, indent=2),
            media_type="application/json",
            headers={"Content-Disposition": "attachment; filename=kaizen_audit_logs.json"},
        )

    # CSV format
    import csv
    import io
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Timestamp", "Actor Email", "Actor Role", "Action", "Entity Type", "Entity ID", "Reason", "IP Address"])
    for log in items:
        writer.writerow([
            log.created_at.isoformat() if log.created_at else "",
            log.actor_email or "",
            log.actor_role or "",
            log.action,
            log.entity_type,
            log.entity_id or "",
            log.reason or "",
            log.ip_address or "",
        ])

    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=kaizen_audit_logs.csv"},
    )
