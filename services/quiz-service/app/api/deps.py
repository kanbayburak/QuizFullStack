from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.services.category_service import CategoryService
from app.services.question_service import QuestionService


async def get_category_service(
    session: Annotated[AsyncSession, Depends(get_db)],
) -> CategoryService:
    return CategoryService(session)


async def get_question_service(
    session: Annotated[AsyncSession, Depends(get_db)],
) -> QuestionService:
    return QuestionService(session)


CategoryServiceDep = Annotated[CategoryService, Depends(get_category_service)]
QuestionServiceDep = Annotated[QuestionService, Depends(get_question_service)]
