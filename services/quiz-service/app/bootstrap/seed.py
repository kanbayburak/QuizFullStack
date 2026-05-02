from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.category import Category

DEFAULT_CATEGORIES: tuple[tuple[str, str, str], ...] = (
    ("Ülkeler", "countries", "Coğrafya ve ülkeler"),
    ("Hayvanlar", "animals", "Hayvanlar alemi"),
    ("Programlama", "programming", "Yazılım ve programlama"),
    ("Siber güvenlik", "cyber-security", "Güvenlik ve etik hackerlık"),
)


async def seed_default_categories(session: AsyncSession) -> None:
    result = await session.execute(select(Category.id).limit(1))
    if result.scalar_one_or_none() is not None:
        return
    for name, slug, description in DEFAULT_CATEGORIES:
        session.add(Category(name=name, slug=slug, description=description))
    await session.commit()
