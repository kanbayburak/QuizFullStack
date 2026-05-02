from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.question import Question


class QuestionRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_by_category(self, category_id: int, skip: int = 0, limit: int = 100) -> list[Question]:
        q = (
            select(Question)
            .where(Question.category_id == category_id)
            .order_by(Question.id)
            .offset(skip)
            .limit(min(limit, 500))
        )
        result = await self._session.execute(q)
        return list(result.scalars().all())

    async def get_by_id(self, question_id: int) -> Question | None:
        return await self._session.get(Question, question_id)

    async def add(self, question: Question) -> Question:
        self._session.add(question)
        await self._session.flush()
        await self._session.refresh(question)
        return question

    async def delete(self, question: Question) -> None:
        await self._session.delete(question)
