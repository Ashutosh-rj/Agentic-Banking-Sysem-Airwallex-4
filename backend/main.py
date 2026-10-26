"""
KAIZEN FinTech — FastAPI Backend Application Entrypoint
"Every Payment Accounted For. Every Decision Explained."
"""
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.core.config import settings
from app.core.database import create_tables, async_session_maker
from app.api.v1.router import api_v1_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: ensure tables created
    await create_tables()

    # If demo mode and database is fresh, run seed data automatically
    if settings.DEMO_MODE:
        async with async_session_maker() as db:
            from app.models.base import User
            from sqlalchemy import select, func
            user_count = (await db.execute(select(func.count(User.id)))).scalar_one()
            if user_count == 0:
                print("[INFO] Empty database detected in DEMO_MODE. Seeding initial data...")
                from seed import seed
                await seed()
                print("[SUCCESS] Seed data populated successfully.")

    yield
    # Shutdown logic if any


app = FastAPI(
    title="KAIZEN FinTech API",
    description="Agentic Banking, Treasury Operations, Payment Reliability, and Cashflow Intelligence Platform.",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS + ["*"] if settings.DEBUG else settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API v1 Router
app.include_router(api_v1_router)


# ---------------------------------------------------------------------------
# Health & Readiness Probes (Prompt Section 10)
# ---------------------------------------------------------------------------
@app.get("/health/live", tags=["System"])
async def liveness_probe():
    """Liveness probe: verifies process is alive and receiving traffic."""
    return {
        "status": "alive",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "app": settings.APP_NAME,
        "env": settings.APP_ENV,
    }


@app.get("/health/ready", tags=["System"])
async def readiness_probe():
    """Readiness probe: verifies essential dependencies (DB) before serving traffic."""
    db_healthy = False
    details = {}
    try:
        async with async_session_maker() as db:
            res = await db.execute(text("SELECT 1"))
            val = res.scalar()
            db_healthy = val == 1
            details["database"] = "connected"
    except Exception as e:
        details["database"] = f"unhealthy: {str(e)}"

    if not db_healthy:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"status": "not_ready", "dependencies": details},
        )

    return {
        "status": "ready",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "dependencies": details,
        "demo_mode": settings.DEMO_MODE,
    }


@app.get("/", tags=["System"])
async def root():
    return {
        "app": "KAIZEN FinTech",
        "tagline": "Every Payment Accounted For. Every Decision Explained.",
        "version": "1.0.0",
        "docs": "/docs",
        "api_v1": "/api/v1",
        "demo_credentials": {
            "admin": "admin@kaizen.dev / Demo1234!",
            "treasury_manager": "treasury@kaizen.dev / Demo1234!",
            "payment_ops": "ops@kaizen.dev / Demo1234!",
            "auditor": "auditor@kaizen.dev / Demo1234!",
        },
    }
