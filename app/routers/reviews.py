from fastapi import APIRouter, Depends, status
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.db_depends import get_async_db
from app.auth import get_current_buyer, get_current_admin
from app.models.users import User as UserModel
from app.shemas import Review as ReviewSchema, CreateReview
from app.services.reviews import ReviewService

router = APIRouter(
    prefix='/reviews',
    tags=['Reviews'],
)


def get_review_service(db: AsyncSession = Depends(get_async_db)) -> ReviewService:
    """Зависимость для получения сервиса отзывов"""
    return ReviewService(db)


@router.get('/', response_model=list[ReviewSchema], status_code=status.HTTP_200_OK)
async def get_all_reviews(
    review_service: ReviewService = Depends(get_review_service)
):
    """
    Возвращает список всех активных отзывов.
    """
    return await review_service.get_all_reviews()


@router.post('/', response_model=ReviewSchema, status_code=status.HTTP_201_CREATED)
async def create_review(
    review: CreateReview,
    current_user: Annotated[UserModel, Depends(get_current_buyer)],
    review_service: ReviewService = Depends(get_review_service)
):
    """
    Создаёт новый отзыв для продукта.
    """
    return await review_service.create_review(review, current_user)


@router.delete('/{review_id}', status_code=status.HTTP_200_OK)
async def delete_review(
    review_id: int,
    current_user: Annotated[UserModel, Depends(get_current_admin)],
    review_service: ReviewService = Depends(get_review_service)
):
    """
    Удаляет отзыв (только для администраторов).
    """
    return await review_service.delete_review(review_id)


@router.get('/product/{product_id}', response_model=list[ReviewSchema])
async def get_product_reviews(
    product_id: int,
    review_service: ReviewService = Depends(get_review_service)
):
    """
    Возвращает все активные отзывы для указанного продукта.
    """
    return await review_service.get_product_reviews(product_id)


@router.get('/user/{user_id}', response_model=list[ReviewSchema])
async def get_user_reviews(
    user_id: int,
    review_service: ReviewService = Depends(get_review_service)
):
    """
    Возвращает все отзывы указанного пользователя.
    """
    return await review_service.get_user_reviews(user_id)