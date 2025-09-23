from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.models.products import Product as ProductModel
from app.models.categories import Category as CategoryModel
from app.models.reviews import Review as ReviewModel
from app.models.users import User as UserModel
from app.shemas import ProductCreate, Review as ReviewShemas


class ProductService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_product(self, product_data: ProductCreate, seller: UserModel):
        """
        Создаёт новый товар, привязанный к продавцу.
        """
        # Проверяем существование категории
        category = await self._get_active_category(product_data.category_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Category not found or inactive"
            )

        # Создаем продукт
        db_product = ProductModel(**product_data.model_dump(), seller_id=seller.id)
        self.db.add(db_product)
        await self.db.commit()
        await self.db.refresh(db_product)
        return db_product

    async def get_all_products(self):
        """
        Возвращает список всех активных товаров.
        """
        result = await self.db.scalars(
            select(ProductModel).where(ProductModel.is_active == True)
        )
        return result.all()

    async def get_products_by_category(self, category_id: int):
        """
        Возвращает список активных товаров в указанной категории.
        """
        # Проверяем существование категории
        category = await self._get_active_category(category_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found or inactive"
            )

        # Получаем товары категории
        result = await self.db.scalars(
            select(ProductModel).where(
                ProductModel.category_id == category_id,
                ProductModel.is_active == True
            )
        )
        return result.all()

    async def get_product(self, product_id: int):
        """
        Возвращает детальную информацию о товаре.
        """
        product = await self._get_active_product(product_id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Product not found or inactive"
            )
        return product

    async def update_product(self, product_id: int, product_data: ProductCreate, seller: UserModel):
        """
        Обновляет товар, если он принадлежит продавцу.
        """
        product = await self._get_product_by_id(product_id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Product not found"
            )

        # Проверяем права доступа
        if product.seller_id != seller.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, 
                detail="You can only update your own products"
            )

        # Проверяем категорию
        category = await self._get_active_category(product_data.category_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Category not found or inactive"
            )

        # Обновляем продукт
        await self.db.execute(
            update(ProductModel)
            .where(ProductModel.id == product_id)
            .values(**product_data.model_dump())
        )
        await self.db.commit()
        await self.db.refresh(product)
        return product

    async def delete_product(self, product_id: int, seller: UserModel):
        """
        Выполняет мягкое удаление товара, если он принадлежит продавцу.
        """
        product = await self._get_active_product(product_id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Product not found or inactive"
            )

        # Проверяем права доступа
        if product.seller_id != seller.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, 
                detail="You can only delete your own products"
            )

        # Мягкое удаление
        await self.db.execute(
            update(ProductModel)
            .where(ProductModel.id == product_id)
            .values(is_active=False)
        )
        await self.db.commit()
        await self.db.refresh(product)
        return product

    async def get_product_reviews(self, product_id: int):
        """
        Возвращает отзывы для продукта.
        """
        # Проверяем существование продукта
        product = await self._get_active_product(product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        # Получаем отзывы
        result = await self.db.scalars(
            select(ReviewModel).where(
                ReviewModel.is_active == True,
                ReviewModel.product_id == product_id
            )
        )
        return result.all()

    async def _get_active_category(self, category_id: int):
        """Получение активной категории"""
        result = await self.db.scalars(
            select(CategoryModel).where(
                CategoryModel.id == category_id,
                CategoryModel.is_active == True
            )
        )
        return result.first()

    async def _get_active_product(self, product_id: int):
        """Получение активного продукта"""
        result = await self.db.scalars(
            select(ProductModel).where(
                ProductModel.id == product_id,
                ProductModel.is_active == True
            )
        )
        return result.first()

    async def _get_product_by_id(self, product_id: int):
        """Получение продукта по ID (без проверки активности)"""
        result = await self.db.scalars(
            select(ProductModel).where(ProductModel.id == product_id)
        )
        return result.first()