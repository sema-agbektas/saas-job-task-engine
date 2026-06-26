from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from src.infrastructure.database.session import get_session
from src.infrastructure.repositories.pg_user_repository import PostgreSQLUserRepository
from src.api.v1.schemas.auth_schema import RegisterRequest
from src.core.security import get_password_hash, verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", status_code=201)
async def register(request: RegisterRequest, session: AsyncSession = Depends(get_session)):
    repo = PostgreSQLUserRepository(session)
    existing = await repo.get_by_email(request.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed = get_password_hash(request.password)
    user = await repo.save(request.email, hashed)
    return {"message": "User created", "email": user.email}


@router.post("/login")
async def login(request: RegisterRequest, session: AsyncSession = Depends(get_session)):
    repo = PostgreSQLUserRepository(session)
    user = await repo.get_by_email(request.email)
    if not user or not verify_password(request.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    token = create_access_token({"sub": user.email})
    return {"access_token": token, "token_type": "bearer"}
