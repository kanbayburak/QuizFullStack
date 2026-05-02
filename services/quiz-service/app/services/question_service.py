from sqlalchemy.ext.asyncio import AsyncSession

from app.models.question import Question
from app.repositories.category_repository import CategoryRepository
from app.repositories.question_repository import QuestionRepository
from app.schemas.question import QuestionCreate, QuestionUpdate


class QuestionNotFoundError(Exception):
    pass


class CategoryNotFoundError(Exception):
    pass


class QuestionService:
    def __init__(self, session: AsyncSession) -> None:
        self._questions = QuestionRepository(session)
        self._categories = CategoryRepository(session)
        self._session = session

    async def list_for_category(self, category_id: int, skip: int = 0, limit: int = 100) -> list[Question]:
        if await self._categories.get_by_id(category_id) is None:
            raise CategoryNotFoundError
        return await self._questions.list_by_category(category_id, skip=skip, limit=limit)

    async def get(self, question_id: int) -> Question:
        row = await self._questions.get_by_id(question_id)
        if row is None:
            raise QuestionNotFoundError
        return row

    async def create(self, data: QuestionCreate) -> Question:
        if await self._categories.get_by_id(data.category_id) is None:
            raise CategoryNotFoundError
        entity = Question(
            category_id=data.category_id,
            text=data.text.strip(),
            option_a=data.option_a.strip(),
            option_b=data.option_b.strip(),
            option_c=data.option_c.strip(),
            option_d=data.option_d.strip(),
            correct_index=data.correct_index,
        )
        await self._questions.add(entity)
        await self._session.commit()
        return entity

    async def update(self, question_id: int, data: QuestionUpdate) -> Question:
        entity = await self._questions.get_by_id(question_id)
        if entity is None:
            raise QuestionNotFoundError
        if data.category_id is not None:
            if await self._categories.get_by_id(data.category_id) is None:
                raise CategoryNotFoundError
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

    async def delete(self, question_id: int) -> None:
        entity = await self._questions.get_by_id(question_id)
        if entity is None:
            raise QuestionNotFoundError
        await self._questions.delete(entity)
        await self._session.commit()
