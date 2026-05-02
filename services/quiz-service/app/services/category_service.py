from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.category import Category
from app.repositories.category_repository import CategoryRepository
from app.schemas.category import CategoryCreate, CategoryUpdate


class CategoryNotFoundError(Exception):
    pass


class CategorySlugConflictError(Exception):
    pass


class CategoryForbiddenError(Exception):
    """Varsayılan kategori veya başkasının kategorisi."""


def _category_visible(cat: Category, viewer_user_id: int | None) -> bool:
    if cat.owner_id is None:
        return True
    return viewer_user_id is not None and cat.owner_id == viewer_user_id


class CategoryService:
    def __init__(self, session: AsyncSession) -> None:
        self._repo = CategoryRepository(session)
        self._session = session

    async def list_visible(self, viewer_user_id: int | None) -> list[Category]:
        return await self._repo.list_visible(viewer_user_id)

    async def get_visible(self, category_id: int, viewer_user_id: int | None) -> Category:
        row = await self._repo.get_by_id(category_id)
        if row is None:
            raise CategoryNotFoundError
        if not _category_visible(row, viewer_user_id):
            raise CategoryNotFoundError
        return row

    async def create(self, data: CategoryCreate, owner_user_id: int) -> Category:
        existing = await self._repo.get_by_slug(data.slug)
        if existing is not None:
            raise CategorySlugConflictError
        entity = Category(
            name=data.name.strip(),
            slug=data.slug,
            description=data.description.strip() if data.description else None,
            owner_id=owner_user_id,
        )
        try:
            await self._repo.add(entity)
            await self._session.commit()
        except IntegrityError:
            await self._session.rollback()
            raise CategorySlugConflictError from None
        return entity

    async def update(self, category_id: int, data: CategoryUpdate, actor_user_id: int) -> Category:
        entity = await self._repo.get_by_id(category_id)
        if entity is None:
            raise CategoryNotFoundError
        if entity.owner_id is None:
            raise CategoryForbiddenError
        if entity.owner_id != actor_user_id:
            raise CategoryForbiddenError
        if data.name is not None:
            entity.name = data.name.strip()
        if data.slug is not None:
            other = await self._repo.get_by_slug(data.slug)
            if other is not None and other.id != category_id:
                raise CategorySlugConflictError
            entity.slug = data.slug
        if data.description is not None:
            entity.description = data.description.strip() if data.description else None
        try:
            await self._session.commit()
            await self._session.refresh(entity)
        except IntegrityError:
            await self._session.rollback()
            raise CategorySlugConflictError from None
        return entity

    async def delete(self, category_id: int, actor_user_id: int) -> None:
        entity = await self._repo.get_by_id(category_id)
        if entity is None:
            raise CategoryNotFoundError
        if entity.owner_id is None:
            raise CategoryForbiddenError
        if entity.owner_id != actor_user_id:
            raise CategoryForbiddenError
        await self._repo.delete(entity)
        await self._session.commit()
