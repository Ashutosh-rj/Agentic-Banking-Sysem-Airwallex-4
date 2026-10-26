"""
KAIZEN FinTech — Auth API Routes
POST /api/v1/auth/register
POST /api/v1/auth/login
POST /api/v1/auth/logout
GET  /api/v1/auth/me
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timezone

from app.core.database import get_db
from app.core.security import verify_password, get_password_hash, create_access_token
from app.core.deps import get_current_user
from app.models.base import User, Organization, AuditLog
from app.schemas.schemas import RegisterRequest, LoginRequest, TokenResponse, UserResponse, MessageResponse
from app.core.config import settings

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=TokenResponse, status_code=201)
async def register(req: RegisterRequest, request: Request, db: AsyncSession = Depends(get_db)):
    # Check existing user
    result = await db.execute(select(User).where(User.email == req.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Email already registered")

    # Get or create org (demo: use existing org or create new)
    result = await db.execute(select(Organization).limit(1))
    org = result.scalar_one_or_none()
    if not org:
        import uuid
        org = Organization(
            id=str(uuid.uuid4()), name="My Organization",
            slug=f"org-{str(uuid.uuid4())[:8]}",
        )
        db.add(org)
        await db.flush()

    import uuid
    user_id = str(uuid.uuid4())
    initials = "".join(w[0].upper() for w in req.full_name.split()[:2])
    user = User(
        id=user_id, org_id=org.id, email=req.email,
        hashed_password=get_password_hash(req.password),
        full_name=req.full_name, role=req.role,
        avatar_initials=initials,
    )
    db.add(user)

    # Audit log
    al = AuditLog(
        id=str(uuid.uuid4()), org_id=org.id, actor_id=user_id,
        actor_email=req.email, actor_role=req.role,
        action="user_registered", entity_type="user", entity_id=user_id,
        ip_address=request.client.host if request.client else None,
    )
    db.add(al)
    await db.commit()

    token = create_access_token({"sub": user_id, "email": req.email, "role": req.role})
    return TokenResponse(
        access_token=token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=UserResponse.model_validate(user),
    )


@router.post("/login", response_model=TokenResponse)
async def login(req: LoginRequest, request: Request, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == req.email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(req.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Account is deactivated")

    user.last_login = datetime.now(timezone.utc)

    import uuid
    al = AuditLog(
        id=str(uuid.uuid4()), org_id=user.org_id, actor_id=user.id,
        actor_email=user.email, actor_role=user.role,
        action="user_login", entity_type="user", entity_id=user.id,
        ip_address=request.client.host if request.client else None,
    )
    db.add(al)
    await db.commit()

    token = create_access_token({"sub": user.id, "email": user.email, "role": user.role})
    return TokenResponse(
        access_token=token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=UserResponse.model_validate(user),
    )


@router.post("/logout", response_model=MessageResponse)
async def logout(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    import uuid
    al = AuditLog(
        id=str(uuid.uuid4()), org_id=current_user.org_id, actor_id=current_user.id,
        actor_email=current_user.email, actor_role=current_user.role,
        action="user_logout", entity_type="user", entity_id=current_user.id,
    )
    db.add(al)
    await db.commit()
    return MessageResponse(message="Logged out successfully")


@router.get("/me", response_model=UserResponse)
async def me(current_user: User = Depends(get_current_user)):
    return UserResponse.model_validate(current_user)
