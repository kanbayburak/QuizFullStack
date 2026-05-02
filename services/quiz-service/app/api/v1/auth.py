from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import CurrentUser, get_db
from app.core.security import create_access_token, hash_password, verify_password
from app.repositories import user_repository
from app.repositories.user_repository import create_user
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse, UserPublic

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest, session: Annotated[AsyncSession, Depends(get_db)]) -> TokenResponse:
    user = await user_repository.get_by_username(session, body.username.strip())
    if user is None or not user.is_active or not verify_password(body.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Kullanıcı adı veya şifre hatalı.",
        )
    token = create_access_token(str(user.id))
    return TokenResponse(access_token=token)


@router.post("/register", response_model=UserPublic, status_code=status.HTTP_201_CREATED)
async def register(
    body: RegisterRequest,
    session: Annotated[AsyncSession, Depends(get_db)],
) -> UserPublic:
    uname = body.username.strip()
    if await user_repository.get_by_username(session, uname):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Bu kullanıcı adı zaten kayıtlı.",
        )
    user = await create_user(session, uname, hash_password(body.password), role="member")
    await session.commit()
    return UserPublic.model_validate(user)


@router.get("/me", response_model=UserPublic)
async def me(user: CurrentUser) -> UserPublic:
    return UserPublic.model_validate(user)
