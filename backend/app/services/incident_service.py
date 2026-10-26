"""Incident management service."""
from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone, timedelta
from typing import Optional, List, Tuple

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.models.base import (
    Incident, IncidentEvidence, AgentExecution, Payment,
    ReconciliationRecord, Account, PaymentObligation,
)
from app.schemas.schemas import IncidentCreate, IncidentUpdate, EvidenceCreate
from app.agents.investigation import InvestigationPipeline, build_pipeline_context
import app.services.audit_service as audit_svc


def _uuid() -> str:
    return str(uuid.uuid4())


_SLA_HOURS = {"CRITICAL": 4, "HIGH": 8, "MEDIUM": 24, "LOW": 72}
_PRIORITY_SCORES = {"CRITICAL": 1.0, "HIGH": 0.75, "MEDIUM": 0.5, "LOW": 0.25}


async def create_incident(
    db: AsyncSession,
    data: IncidentCreate,
    created_by: Optional[str] = None,
    actor_role: Optional[str] = None,
) -> Incident:
    sla_hours = _SLA_HOURS.get(data.severity, 24)
    incident = Incident(
        id=_uuid(),
        org_id=data.org_id,
        payment_id=data.payment_id,
        title=data.title,
        description=data.description,
        severity=data.severity,
        status="OPEN",
        priority_score=_PRIORITY_SCORES.get(data.severity, 0.5),
        sla_deadline=datetime.now(timezone.utc) + timedelta(hours=sla_hours),
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    db.add(incident)
    await audit_svc.log_event(
        db,
        "INCIDENT_CREATED",
        org_id=data.org_id,
        actor_id=created_by,
        actor_role=actor_role,
        entity_type="Incident",
        entity_id=incident.id,
        after_state={"title": data.title, "severity": data.severity},
    )
    await db.commit()
    await db.refresh(incident)
    return incident


async def get_incidents(
    db: AsyncSession,
    org_id: Optional[str] = None,
    status: Optional[str] = None,
    severity: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
) -> Tuple[List[Incident], int]:
    query = select(Incident).options(
        selectinload(Incident.evidence),
        selectinload(Incident.agent_executions),
    )
    if org_id:
        query = query.where(Incident.org_id == org_id)
    if status:
        query = query.where(Incident.status == status)
    if severity:
        query = query.where(Incident.severity == severity)

    count_q = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_q)).scalar_one()

    query = query.order_by(Incident.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    return list(result.scalars().all()), total


async def get_incident(db: AsyncSession, incident_id: str) -> Optional[Incident]:
    result = await db.execute(
        select(Incident)
        .options(
            selectinload(Incident.evidence),
            selectinload(Incident.agent_executions),
        )
        .where(Incident.id == incident_id)
    )
    return result.scalar_one_or_none()


async def investigate_incident(
    db: AsyncSession, incident: Incident, actor_id: Optional[str] = None
) -> dict:
    # Load payment
    payment = None
    if incident.payment_id:
        res = await db.execute(select(Payment).where(Payment.id == incident.payment_id))
        payment = res.scalar_one_or_none()

    # Load reconciliation records
    recon_records = []
    if payment:
        res = await db.execute(
            select(ReconciliationRecord).where(ReconciliationRecord.payment_id == payment.id)
        )
        recon_records = list(res.scalars().all())

    # Load accounts
    res = await db.execute(select(Account).where(Account.org_id == incident.org_id))
    accounts = list(res.scalars().all())

    # Load obligations
    res = await db.execute(
        select(PaymentObligation).where(PaymentObligation.org_id == incident.org_id)
    )
    obligations = list(res.scalars().all())

    ctx = build_pipeline_context(
        incident=incident,
        payment=payment,
        reconciliation_records=recon_records,
        accounts=accounts,
        obligations=obligations,
    )

    pipeline = InvestigationPipeline()
    report = pipeline.run(ctx)

    # Record agent executions
    now = datetime.now(timezone.utc)
    for stage in report.get("pipeline_stages", []):
        exec_record = AgentExecution(
            id=_uuid(),
            incident_id=incident.id,
            agent_name=stage["agent"],
            status=stage["status"],
            input_data=None,
            output_data=json.dumps(stage.get("output", {})),
            error=stage.get("error"),
            started_at=now,
            completed_at=now,
        )
        db.add(exec_record)

    # Update incident with findings
    summary = report.get("summary", {})
    incident.root_cause = summary.get("root_cause")
    incident.ai_report = json.dumps(report)
    incident.financial_impact = summary.get("financial_impact")
    incident.status = "INVESTIGATING"
    incident.updated_at = now

    await audit_svc.log_event(
        db,
        "INCIDENT_INVESTIGATED",
        org_id=incident.org_id,
        actor_id=actor_id,
        entity_type="Incident",
        entity_id=incident.id,
        after_state={"root_cause": incident.root_cause, "status": "INVESTIGATING"},
    )
    await db.commit()
    return report


async def resolve_incident(
    db: AsyncSession,
    incident: Incident,
    resolution_notes: Optional[str] = None,
    actor_id: Optional[str] = None,
    actor_role: Optional[str] = None,
) -> Incident:
    now = datetime.now(timezone.utc)
    incident.status = "RESOLVED"
    incident.resolved_at = now
    incident.updated_at = now
    if resolution_notes:
        ev = IncidentEvidence(
            id=_uuid(),
            incident_id=incident.id,
            evidence_type="RESOLUTION_NOTE",
            content=resolution_notes,
            created_by=actor_id,
            created_at=now,
        )
        db.add(ev)
    await audit_svc.log_event(
        db,
        "INCIDENT_RESOLVED",
        org_id=incident.org_id,
        actor_id=actor_id,
        actor_role=actor_role,
        entity_type="Incident",
        entity_id=incident.id,
        after_state={"status": "RESOLVED"},
    )
    await db.commit()
    await db.refresh(incident)
    return incident


async def add_evidence(
    db: AsyncSession,
    incident: Incident,
    data: EvidenceCreate,
    actor_id: Optional[str] = None,
) -> IncidentEvidence:
    ev = IncidentEvidence(
        id=_uuid(),
        incident_id=incident.id,
        evidence_type=data.evidence_type,
        content=data.content,
        created_by=actor_id,
        created_at=datetime.now(timezone.utc),
    )
    db.add(ev)
    await db.commit()
    await db.refresh(ev)
    return ev


async def assign_incident(
    db: AsyncSession,
    incident: Incident,
    assignee_id: str,
    actor_id: Optional[str] = None,
) -> Incident:
    incident.assigned_to = assignee_id
    incident.updated_at = datetime.now(timezone.utc)
    await audit_svc.log_event(
        db,
        "INCIDENT_ASSIGNED",
        org_id=incident.org_id,
        actor_id=actor_id,
        entity_type="Incident",
        entity_id=incident.id,
        after_state={"assigned_to": assignee_id},
    )
    await db.commit()
    await db.refresh(incident)
    return incident
