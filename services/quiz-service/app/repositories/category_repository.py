from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.category import Category


class CategoryRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_visible(self, viewer_user_id: int | None) -> list[Category]:
        stmt = select(Category).order_by(Category.name)
        if viewer_user_id is None:
            stmt = stmt.where(Category.owner_id.is_(None))
        else:
            stmt = stmt.where(
                or_(Category.owner_id.is_(None), Category.owner_id == viewer_user_id)
            )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_id(self, category_id: int) -> Category | None:
        return await self._session.get(Category, category_id)

    async def get_by_slug(self, slug: str) -> Category | None:
        result = await self._session.execute(select(Category).where(Category.slug == slug))
        return result.scalar_one_or_none()

    async def add(self, category: Category) -> Category:
        self._session.add(category)
        await self._session.flush()
        await self._session.refresh(category)
        return category

    async def delete(self, category: Category) -> None:
        await self._session.delete(category)
