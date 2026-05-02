from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi.security.utils import get_authorization_scheme_param
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from app.core.security import decode_token
from app.db.session import get_db
from app.models.user import User
from app.repositories import user_repository
from app.services.category_service import CategoryService
from app.services.question_service import QuestionService

http_bearer = HTTPBearer(auto_error=False)


def _normalize_access_token(raw: str) -> str:
    s = raw.strip()
    if len(s) >= 2 and s[0] == s[-1] and s[0] in "\"'":
        s = s[1:-1].strip()
    lower = s.lower()
    if lower.startswith("bearer "):
        s = s[7:].strip()
    return s


def _jwt_like(value: str) -> bool:
    return value.count(".") == 2 and all(len(p) > 0 for p in value.split(".", 2))


def _extract_bearer_token(authorization: str | None) -> str | None:
    """Authorization başlığından JWT çıkarır; Swagger/düzensiz istemciler için toleranslı."""
    if not authorization:
        return None
    header = authorization.strip()
    scheme, param = get_authorization_scheme_param(header)
    if param and scheme.lower() in ("bearer", "token"):
        return _normalize_access_token(param)
    # Şema bozulmuş veya eksik: tek parça JWT (nadir proxy / elle curl)
    parts = header.split(None, 1)
    if len(parts) == 1 and _jwt_like(parts[0]):
        return _normalize_access_token(parts[0])
    return None


async def get_current_user(
    request: Request,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(http_bearer)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    token_str: str | None = None
    if credentials is not None and credentials.scheme.lower() == "bearer":
        token_str = _normalize_access_token(credentials.credentials)
    if not token_str:
        token_str = _extract_bearer_token(request.headers.get("Authorization"))
    if not token_str:
        raise HTTPException(
            status_code=401,
            detail="Kimlik doğrulama gerekli.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user_id_str = decode_token(token_str)
    if user_id_str is None:
        raise HTTPException(status_code=401, detail="Geçersiz veya süresi dolmuş oturum.")
    try:
        user_id = int(user_id_str)
    except ValueError:
        raise HTTPException(status_code=401, detail="Geçersiz oturum.") from None
    user = await user_repository.get_by_id(session, user_id)
    if user is None or not user.is_active:
        raise HTTPException(status_code=401, detail="Kullanıcı bulunamadı veya pasif.")
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


async def get_optional_user(
    request: Request,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(http_bearer)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> User | None:
    token_str: str | None = None
    if credentials is not None and credentials.scheme.lower() == "bearer":
        token_str = _normalize_access_token(credentials.credentials)
    if not token_str:
        token_str = _extract_bearer_token(request.headers.get("Authorization"))
    if not token_str:
        return None
    user_id_str = decode_token(token_str)
    if user_id_str is None:
        return None
    try:
        user_id = int(user_id_str)
    except ValueError:
        return None
    user = await user_repository.get_by_id(session, user_id)
    if user is None or not user.is_active:
        return None
    return user


OptionalUser = Annotated[User | None, Depends(get_optional_user)]


async def get_category_service(
    session: Annotated[AsyncSession, Depends(get_db)],
) -> CategoryService:
    return CategoryService(session)


async def get_question_service(
    session: Annotated[AsyncSession, Depends(get_db)],
) -> QuestionService:
    return QuestionService(session)


CategoryServiceDep = Annotated[CategoryService, Depends(get_category_service)]
QuestionServiceDep = Annotated[QuestionService, Depends(get_question_service)]
