from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.question import Question


class QuestionRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_by_category_visible(
        self,
        category_id: int,
        viewer_user_id: int | None,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Question]:
        stmt = select(Question).where(Question.category_id == category_id)
        if viewer_user_id is None:
            stmt = stmt.where(Question.owner_id.is_(None))
        else:
            stmt = stmt.where(
                or_(Question.owner_id.is_(None), Question.owner_id == viewer_user_id)
            )
        stmt = stmt.order_by(Question.id).offset(skip).limit(min(limit, 500))
        result = await self._session.execute(stmt)
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
