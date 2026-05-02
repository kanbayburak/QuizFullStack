"""users.role sütununu garanti eder; artık yetki kontrolünde kullanılmaz, tüm kayıtlar member olarak tutulabilir."""

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine


async def ensure_user_role_column(engine: AsyncEngine) -> None:
    dialect = engine.dialect.name
    async with engine.begin() as conn:
        if dialect == "postgresql":
            await conn.execute(
                text("ALTER TABLE users ADD COLUMN IF NOT EXISTS role VARCHAR(32)")
            )
            await conn.execute(
                text("UPDATE users SET role = 'member' WHERE role IS NULL OR trim(role) = ''")
            )
            await conn.execute(text("ALTER TABLE users ALTER COLUMN role SET DEFAULT 'member'"))
            await conn.execute(text("ALTER TABLE users ALTER COLUMN role SET NOT NULL"))
            await conn.execute(text("UPDATE users SET role = 'member'"))
        elif dialect == "sqlite":
            try:
                await conn.execute(
                    text(
                        "ALTER TABLE users ADD COLUMN role VARCHAR(32) NOT NULL DEFAULT 'member'"
                    )
                )
            except Exception:
                pass
