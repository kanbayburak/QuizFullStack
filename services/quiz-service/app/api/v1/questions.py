from fastapi import APIRouter, HTTPException, Query, status

from app.api.deps import QuestionServiceDep
from app.schemas.question import QuestionCreate, QuestionRead, QuestionUpdate
from app.services.question_service import (
    CategoryNotFoundError,
    QuestionNotFoundError,
)

router = APIRouter(prefix="/questions", tags=["questions"])


@router.get("", response_model=list[QuestionRead])
async def list_questions(
    service: QuestionServiceDep,
    category_id: int = Query(..., description="Soru listesi filtresi"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
) -> list[QuestionRead]:
    try:
        rows = await service.list_for_category(category_id, skip=skip, limit=limit)
    except CategoryNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Kategori bulunamadı.") from None
    return [QuestionRead.model_validate(r) for r in rows]


@router.post("", response_model=QuestionRead, status_code=status.HTTP_201_CREATED)
async def create_question(data: QuestionCreate, service: QuestionServiceDep) -> QuestionRead:
    try:
        row = await service.create(data)
    except CategoryNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Kategori bulunamadı.") from None
    return QuestionRead.model_validate(row)


@router.get("/{question_id}", response_model=QuestionRead)
async def get_question(question_id: int, service: QuestionServiceDep) -> QuestionRead:
    try:
        row = await service.get(question_id)
    except QuestionNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Soru bulunamadı.") from None
    return QuestionRead.model_validate(row)


@router.patch("/{question_id}", response_model=QuestionRead)
async def update_question(
    question_id: int,
    data: QuestionUpdate,
    service: QuestionServiceDep,
) -> QuestionRead:
    try:
        row = await service.update(question_id, data)
    except QuestionNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Soru bulunamadı.") from None
    except CategoryNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Kategori bulunamadı.") from None
    return QuestionRead.model_validate(row)


@router.delete("/{question_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_question(question_id: int, service: QuestionServiceDep) -> None:
    try:
        await service.delete(question_id)
    except QuestionNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Soru bulunamadı.") from None
