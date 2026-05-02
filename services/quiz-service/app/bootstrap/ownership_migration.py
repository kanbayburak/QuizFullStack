"""categories.owner_id ve questions.owner_id — NULL = sistem (varsayılan)."""

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine


async def ensure_ownership_columns(engine: AsyncEngine) -> None:
    dialect = engine.dialect.name
    async with engine.begin() as conn:
        if dialect == "postgresql":
            await conn.execute(text(
                "ALTER TABLE categories ADD COLUMN IF NOT EXISTS owner_id INTEGER REFERENCES users(id)"
            ))
            await conn.execute(text(
                "CREATE INDEX IF NOT EXISTS ix_categories_owner_id ON categories(owner_id)"
            ))
            await conn.execute(text(
                "ALTER TABLE questions ADD COLUMN IF NOT EXISTS owner_id INTEGER REFERENCES users(id)"
            ))
            await conn.execute(text(
                "CREATE INDEX IF NOT EXISTS ix_questions_owner_id ON questions(owner_id)"
            ))
        elif dialect == "sqlite":
            try:
                await conn.execute(text(
                    "ALTER TABLE categories ADD COLUMN owner_id INTEGER REFERENCES users(id)"
                ))
            except Exception:
                pass
            try:
                await conn.execute(text(
                    "ALTER TABLE questions ADD COLUMN owner_id INTEGER REFERENCES users(id)"
                ))
            except Exception:
                pass
