from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.security import hash_password
from app.models.user import User
from app.repositories.user_repository import create_user


async def seed_bootstrap_admin(session: AsyncSession) -> None:
    settings = get_settings()
    username = (settings.admin_bootstrap_username or "").strip()
    password = settings.admin_bootstrap_password
    if not username or not password:
        return
    count = await session.scalar(select(func.count()).select_from(User))
    if count and count > 0:
        return
    await create_user(session, username, hash_password(password), role="member")
    await session.commit()
