from fastapi import APIRouter, HTTPException, status

from app.api.deps import CategoryServiceDep
from app.schemas.category import CategoryCreate, CategoryRead, CategoryUpdate
from app.services.category_service import (
    CategoryNotFoundError,
    CategorySlugConflictError,
)

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("", response_model=list[CategoryRead])
async def list_categories(service: CategoryServiceDep) -> list[CategoryRead]:
    rows = await service.list_categories()
    return [CategoryRead.model_validate(r) for r in rows]


@router.post("", response_model=CategoryRead, status_code=status.HTTP_201_CREATED)
async def create_category(data: CategoryCreate, service: CategoryServiceDep) -> CategoryRead:
    try:
        row = await service.create(data)
    except CategorySlugConflictError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Bu slug zaten kullanılıyor.",
        ) from None
    return CategoryRead.model_validate(row)


@router.get("/{category_id}", response_model=CategoryRead)
async def get_category(category_id: int, service: CategoryServiceDep) -> CategoryRead:
    try:
        row = await service.get(category_id)
    except CategoryNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Kategori bulunamadı.") from None
    return CategoryRead.model_validate(row)


@router.patch("/{category_id}", response_model=CategoryRead)
async def update_category(
    category_id: int,
    data: CategoryUpdate,
    service: CategoryServiceDep,
) -> CategoryRead:
    try:
        row = await service.update(category_id, data)
    except CategoryNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Kategori bulunamadı.") from None
    except CategorySlugConflictError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Bu slug zaten kullanılıyor.",
        ) from None
    return CategoryRead.model_validate(row)


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(category_id: int, service: CategoryServiceDep) -> None:
    try:
        await service.delete(category_id)
    except CategoryNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Kategori bulunamadı.") from None
