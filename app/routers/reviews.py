from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, update, func
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated

from app.db_depends import get_async_db

from app.models.reviews import Review as ReviewModel
from app.models.products import Product as ProductModel
from app.shemas import Review as ReviewSchema, CreateReview
from app.models.users import User as UserModel
from app.auth import get_current_buyer, get_current_admin


router = APIRouter(prefix='/reviews', tags=['Reviews'])


@router.get('/', response_model=list[ReviewSchema], status_code=status.HTTP_200_OK)
async def get_all_reviews(db: Annotated[AsyncSession, Depends(get_async_db)]):
    '''
    Возвращает список всех отзывов
    '''
    reviews = await db.scalars(select(ReviewModel).where(ReviewModel.is_active == True))
    return reviews.all()

@router.post('/', response_model=ReviewSchema,
             status_code=status.HTTP_201_CREATED)
async def create_reviews(reviews: CreateReview, 
                         db: Annotated[AsyncSession, Depends(get_async_db)],
                         current_user: Annotated[UserModel, Depends(get_current_buyer)]):
    '''
    Создаем новый отзыв, если существует продукт и обновляем средний рейтинг товара
    '''
    product = await db.scalar(select(ProductModel).where(
        ProductModel.id == reviews.product_id,
        ProductModel.is_active == True
    ))

    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='Product not found')

    db_review = ReviewModel(**reviews.model_dump(),  user_id=current_user.id)
    db.add(db_review)
    await db.commit()
    await db.refresh(db_review)
    await update_product(reviews.product_id, db)
    return db_review


@router.delete('/{review_id}', status_code=status.HTTP_200_OK)
async def delete_review(review_id: int, db: Annotated[AsyncSession, Depends(get_async_db)], 
                        current_user: Annotated[UserModel, Depends(get_current_admin)]):
    '''
    Логическое удаление
    '''
    review = await db.scalar(select(ReviewModel).where(ReviewModel.id == review_id))
    
    if not review:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='Review not found')
    
    await db.execute(update(ReviewModel).where(ReviewModel.id == review_id).values(is_active = False))
    await db.commit()
    await db.refresh(review)
    await update_product(review.product_id, db)
    return {"message": "Review deleted"}


async def update_product(id_product: int, db: AsyncSession):
    
    tsmt = await db.scalar(select(func.avg(ReviewModel.grade)).where(ReviewModel.is_active == True,
                                                 ReviewModel.product_id == id_product)) # получаем средний рейтинг для продукта
    avg_grade = round(tsmt,2) if tsmt else None
    await db.execute(update(ProductModel).where(ProductModel.id == id_product).
                         values(rating = avg_grade))
    await db.commit()