from fastapi import APIRouter, Depends, status
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.db_depends import get_async_db
from app.shemas import Category as CategorySchema, CategoryCreate
from app.services.categories import CategoryService

router = APIRouter(
    prefix="/categorys",
    tags=["Categorys"],
)


def get_category_service(db: AsyncSession = Depends(get_async_db)) -> CategoryService:
    """Зависимость для получения сервиса категорий"""
    return CategoryService(db)


@router.post("/", response_model=CategorySchema, status_code=status.HTTP_201_CREATED)
async def create_category(
    category: CategoryCreate,
    category_service: CategoryService = Depends(get_category_service)
):
    """
    Создаёт новую категорию.
    """
    return await category_service.create_category(category)


@router.get("/", response_model=list[CategorySchema])
async def get_all_categories(
    category_service: CategoryService = Depends(get_category_service)
):
    """
    Возвращает список всех активных категорий.
    """
    return await category_service.get_all_categories()


@router.delete("/{category_id}", response_model=CategorySchema)
async def delete_category(
    category_id: int,
    category_service: CategoryService = Depends(get_category_service)
):
    """
    Выполняет мягкое удаление категории по её ID, устанавливая is_active = False.
    """
    return await category_service.delete_category(category_id)


@router.put("/{category_id}", response_model=CategorySchema)
async def update_category(
    category_id: int,
    category: CategoryCreate,
    category_service: CategoryService = Depends(get_category_service)
):
    """
    Обновляет категорию по её ID.
    """
    return await category_service.update_category(category_id, category)