from fastapi import APIRouter, HTTPException, Query, status

from app.api.deps import CurrentUser, OptionalUser, QuestionServiceDep
from app.schemas.question import QuestionCreate, QuestionRead, QuestionUpdate
from app.services.question_service import (
    CategoryNotFoundError,
    QuestionForbiddenError,
    QuestionNotFoundError,
)

router = APIRouter(prefix="/questions", tags=["questions"])


@router.get("", response_model=list[QuestionRead])
async def list_questions(
    service: QuestionServiceDep,
    viewer: OptionalUser,
    category_id: int = Query(..., description="Soru listesi filtresi"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
) -> list[QuestionRead]:
    try:
        rows = await service.list_for_category(
            category_id,
            viewer.id if viewer else None,
            skip=skip,
            limit=limit,
        )
    except CategoryNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Kategori bulunamadı.") from None
    return [QuestionRead.model_validate(r) for r in rows]


@router.post("", response_model=QuestionRead, status_code=status.HTTP_201_CREATED)
async def create_question(
    data: QuestionCreate,
    service: QuestionServiceDep,
    user: CurrentUser,
) -> QuestionRead:
    try:
        row = await service.create(data, user.id)
    except CategoryNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Kategori bulunamadı.") from None
    except QuestionForbiddenError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bu kategoriye soru eklenemez.",
        ) from None
    return QuestionRead.model_validate(row)


@router.get("/{question_id}", response_model=QuestionRead)
async def get_question(
    question_id: int,
    service: QuestionServiceDep,
    viewer: OptionalUser,
) -> QuestionRead:
    try:
        row = await service.get_visible(question_id, viewer.id if viewer else None)
    except QuestionNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Soru bulunamadı.") from None
    return QuestionRead.model_validate(row)


@router.patch("/{question_id}", response_model=QuestionRead)
async def update_question(
    question_id: int,
    data: QuestionUpdate,
    service: QuestionServiceDep,
    user: CurrentUser,
) -> QuestionRead:
    try:
        row = await service.update(question_id, data, user.id)
    except QuestionNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Soru bulunamadı.") from None
    except CategoryNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Kategori bulunamadı.") from None
    except QuestionForbiddenError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Varsayılan veya başka bir kullanıcının sorusu düzenlenemez.",
        ) from None
    return QuestionRead.model_validate(row)


@router.delete("/{question_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_question(
    question_id: int,
    service: QuestionServiceDep,
    user: CurrentUser,
) -> None:
    try:
        await service.delete(question_id, user.id)
    except QuestionNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Soru bulunamadı.") from None
    except QuestionForbiddenError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Varsayılan veya başka bir kullanıcının sorusu silinemez.",
        ) from None
