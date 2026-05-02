from sqlalchemy.ext.asyncio import AsyncSession

from app.models.category import Category
from app.models.question import Question
from app.repositories.category_repository import CategoryRepository
from app.repositories.question_repository import QuestionRepository
from app.schemas.question import QuestionCreate, QuestionUpdate


class QuestionNotFoundError(Exception):
    pass


class CategoryNotFoundError(Exception):
    pass


class QuestionForbiddenError(Exception):
    """Sistem sorusu veya başkasının sorusu."""


def _category_visible(cat: Category, viewer_user_id: int | None) -> bool:
    if cat.owner_id is None:
        return True
    return viewer_user_id is not None and cat.owner_id == viewer_user_id


def _question_visible(q: Question, viewer_user_id: int | None) -> bool:
    if q.owner_id is None:
        return True
    return viewer_user_id is not None and q.owner_id == viewer_user_id


def _can_post_question_to_category(cat: Category, user_id: int) -> bool:
    if cat.owner_id is None:
        return True
    return cat.owner_id == user_id


class QuestionService:
    def __init__(self, session: AsyncSession) -> None:
        self._questions = QuestionRepository(session)
        self._categories = CategoryRepository(session)
        self._session = session

    async def list_for_category(
        self,
        category_id: int,
        viewer_user_id: int | None,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Question]:
        cat = await self._categories.get_by_id(category_id)
        if cat is None:
            raise CategoryNotFoundError
        if not _category_visible(cat, viewer_user_id):
            raise CategoryNotFoundError
        return await self._questions.list_by_category_visible(
            category_id, viewer_user_id, skip=skip, limit=limit
        )

    async def get_visible(self, question_id: int, viewer_user_id: int | None) -> Question:
        q = await self._questions.get_by_id(question_id)
        if q is None:
            raise QuestionNotFoundError
        cat = await self._categories.get_by_id(q.category_id)
        if cat is None:
            raise QuestionNotFoundError
        if not _category_visible(cat, viewer_user_id):
            raise QuestionNotFoundError
        if not _question_visible(q, viewer_user_id):
            raise QuestionNotFoundError
        return q

    async def create(self, data: QuestionCreate, owner_user_id: int) -> Question:
        cat = await self._categories.get_by_id(data.category_id)
        if cat is None:
            raise CategoryNotFoundError
        if not _category_visible(cat, owner_user_id):
            raise CategoryNotFoundError
        if not _can_post_question_to_category(cat, owner_user_id):
            raise QuestionForbiddenError
        entity = Question(
            category_id=data.category_id,
            text=data.text.strip(),
            option_a=data.option_a.strip(),
            option_b=data.option_b.strip(),
            option_c=data.option_c.strip(),
            option_d=data.option_d.strip(),
            correct_index=data.correct_index,
            owner_id=owner_user_id,
        )
        await self._questions.add(entity)
        await self._session.commit()
        return entity

    async def update(self, question_id: int, data: QuestionUpdate, actor_user_id: int) -> Question:
        entity = await self._questions.get_by_id(question_id)
        if entity is None:
            raise QuestionNotFoundError
        if entity.owner_id is None:
            raise QuestionForbiddenError
        if entity.owner_id != actor_user_id:
            raise QuestionForbiddenError
        if data.category_id is not None:
            cat = await self._categories.get_by_id(data.category_id)
            if cat is None:
                raise CategoryNotFoundError
            if not _category_visible(cat, actor_user_id):
                raise CategoryNotFoundError
            if not _can_post_question_to_category(cat, actor_user_id):
                raise QuestionForbiddenError
            entity.category_id = data.category_id
        if data.text is not None:
            entity.text = data.text.strip()
        if data.option_a is not None:
            entity.option_a = data.option_a.strip()
        if data.option_b is not None:
            entity.option_b = data.option_b.strip()
        if data.option_c is not None:
            entity.option_c = data.option_c.strip()
        if data.option_d is not None:
            entity.option_d = data.option_d.strip()
        if data.correct_index is not None:
            entity.correct_index = data.correct_index
        await self._session.commit()
        await self._session.refresh(entity)
        return entity

    async def delete(self, question_id: int, actor_user_id: int) -> None:
        entity = await self._questions.get_by_id(question_id)
        if entity is None:
            raise QuestionNotFoundError
        if entity.owner_id is None:
            raise QuestionForbiddenError
        if entity.owner_id != actor_user_id:
            raise QuestionForbiddenError
        await self._questions.delete(entity)
        await self._session.commit()
