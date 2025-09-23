from sqlalchemy import select, update, func
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.models.reviews import Review as ReviewModel
from app.models.products import Product as ProductModel
from app.models.users import User as UserModel
from app.shemas import CreateReview


class ReviewService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all_reviews(self):
        """
        Возвращает список всех активных отзывов.
        """
        result = await self.db.scalars(
            select(ReviewModel).where(ReviewModel.is_active == True)
        )
        return result.all()

    async def create_review(self, review_data: CreateReview, user: UserModel):
        """
        Создаёт новый отзыв и обновляет средний рейтинг товара.
        """
        # Проверяем существование продукта
        product = await self._get_active_product(review_data.product_id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Product not found'
            )

        # Проверяем, не оставлял ли пользователь уже отзыв на этот товар
        existing_review = await self.db.scalar(
            select(ReviewModel).where(
                ReviewModel.user_id == user.id,
                ReviewModel.product_id == review_data.product_id,
                ReviewModel.is_active == True
            )
        )
        if existing_review:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='You have already reviewed this product'
            )

        # Создаем отзыв
        db_review = ReviewModel(**review_data.model_dump(), user_id=user.id)
        self.db.add(db_review)
        await self.db.commit()
        await self.db.refresh(db_review)

        # Обновляем рейтинг продукта
        await self._update_product_rating(review_data.product_id)

        return db_review

    async def delete_review(self, review_id: int):
        """
        Логическое удаление отзыва.
        """
        review = await self._get_review_by_id(review_id)
        if not review:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Review not found'
            )

        # Сохраняем product_id перед удалением
        product_id = review.product_id

        # Логическое удаление
        await self.db.execute(
            update(ReviewModel)
            .where(ReviewModel.id == review_id)
            .values(is_active=False)
        )
        await self.db.commit()

        # Обновляем рейтинг продукта
        await self._update_product_rating(product_id)

        return {"message": "Review deleted successfully"}

    async def _update_product_rating(self, product_id: int):
        """
        Обновляет средний рейтинг продукта.
        """
        # Получаем средний рейтинг
        avg_rating = await self.db.scalar(
            select(func.avg(ReviewModel.grade))
            .where(
                ReviewModel.is_active == True,
                ReviewModel.product_id == product_id
            )
        )
        
        # Округляем до 2 знаков после запятой
        rounded_rating = round(avg_rating, 2) if avg_rating is not None else None

        # Обновляем рейтинг продукта
        await self.db.execute(
            update(ProductModel)
            .where(ProductModel.id == product_id)
            .values(rating=rounded_rating)
        )
        await self.db.commit()

    async def _get_active_product(self, product_id: int):
        """Получение активного продукта"""
        result = await self.db.scalar(
            select(ProductModel).where(
                ProductModel.id == product_id,
                ProductModel.is_active == True
            )
        )
        return result

    async def _get_review_by_id(self, review_id: int):
        """Получение отзыва по ID"""
        result = await self.db.scalar(
            select(ReviewModel).where(ReviewModel.id == review_id)
        )
        return result

    async def get_product_reviews(self, product_id: int):
        """
        Получение всех активных отзывов для продукта.
        """
        # Проверяем существование продукта
        product = await self._get_active_product(product_id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Product not found'
            )

        # Получаем отзывы
        result = await self.db.scalars(
            select(ReviewModel)
            .where(
                ReviewModel.product_id == product_id,
                ReviewModel.is_active == True
            )
        )
        return result.all()

    async def get_user_reviews(self, user_id: int):
        """
        Получение всех отзывов пользователя.
        """
        result = await self.db.scalars(
            select(ReviewModel)
            .where(
                ReviewModel.user_id == user_id,
                ReviewModel.is_active == True
            )
        )
        return result.all()