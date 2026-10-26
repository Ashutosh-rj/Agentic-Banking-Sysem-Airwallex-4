"""Audit logging service."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Optional, Any
import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models.base import AuditLog


def _uuid() -> str:
    return str(uuid.uuid4())


async def log_event(
    db: AsyncSession,
    action: str,
    *,
    org_id: Optional[str] = None,
    actor_id: Optional[str] = None,
    actor_role: Optional[str] = None,
    entity_type: Optional[str] = None,
    entity_id: Optional[str] = None,
    before_state: Optional[Any] = None,
    after_state: Optional[Any] = None,
    reason: Optional[str] = None,
    ip_address: Optional[str] = None,
) -> AuditLog:
    entry = AuditLog(
        id=_uuid(),
        org_id=org_id,
        actor_id=actor_id,
        actor_role=actor_role,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        before_state=json.dumps(before_state) if before_state is not None else None,
        after_state=json.dumps(after_state) if after_state is not None else None,
        reason=reason,
        ip_address=ip_address,
        created_at=datetime.now(timezone.utc),
    )
    db.add(entry)
    return entry


async def get_logs(
    db: AsyncSession,
    org_id: Optional[str] = None,
    actor_id: Optional[str] = None,
    entity_type: Optional[str] = None,
    entity_id: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[AuditLog], int]:
    query = select(AuditLog)
    if org_id:
        query = query.where(AuditLog.org_id == org_id)
    if actor_id:
        query = query.where(AuditLog.actor_id == actor_id)
    if entity_type:
        query = query.where(AuditLog.entity_type == entity_type)
    if entity_id:
        query = query.where(AuditLog.entity_id == entity_id)

    count_q = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_q)).scalar_one()

    query = query.order_by(AuditLog.created_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    return list(result.scalars().all()), total
