"""
KAIZEN FinTech — Main API v1 Router
Aggregates all domain routes under the /api/v1 prefix.
"""
from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.dashboard import router as dashboard_router
from app.api.v1.payments import router as payments_router
from app.api.v1.incidents import router as incidents_router
from app.api.v1.reconciliation import router as reconciliation_router
from app.api.v1.treasury import router as treasury_router
from app.api.v1.risk import router as risk_router
from app.api.v1.analytics import router as analytics_router
from app.api.v1.audit import router as audit_router
from app.api.v1.integrations import router as integrations_router

api_v1_router = APIRouter(prefix="/api/v1")

api_v1_router.include_router(auth_router)
api_v1_router.include_router(dashboard_router)
api_v1_router.include_router(payments_router)
api_v1_router.include_router(incidents_router)
api_v1_router.include_router(reconciliation_router)
api_v1_router.include_router(treasury_router)
api_v1_router.include_router(risk_router)
api_v1_router.include_router(analytics_router)
api_v1_router.include_router(audit_router)
api_v1_router.include_router(integrations_router)
