from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.models.categories import Category as CategoryModel
from app.shemas import CategoryCreate


class CategoryService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_category(self, category: CategoryCreate):
        """
        Создаёт новую категорию.
        """
        # Проверка существования parent_id, если указан
        if category.parent_id is not None and category.parent_id > 0:
            parent = await self._get_category_by_id(category.parent_id)
            if parent is None:
                raise HTTPException(status_code=400, detail="Parent category not found")

        # Создание новой категории
        db_category = CategoryModel(**category.model_dump())
        self.db.add(db_category)
        await self.db.commit()
        await self.db.refresh(db_category)
        return db_category

    async def get_all_categories(self):
        """
        Возвращает список всех активных категорий.
        """
        result = await self.db.scalars(
            select(CategoryModel).where(CategoryModel.is_active == True)
        )
        return result.all()

    async def delete_category(self, category_id: int):
        """
        Выполняет мягкое удаление категории по её ID, устанавливая is_active = False.
        """
        db_category = await self._get_category_by_id(category_id)
        if not db_category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Category not found"
            )

        await self.db.execute(
            update(CategoryModel)
            .where(CategoryModel.id == category_id)
            .values(is_active=False)
        )
        await self.db.commit()
        return db_category

    async def update_category(self, category_id: int, category: CategoryCreate):
        """
        Обновляет категорию по её ID.
        """
        # Проверяем существование категории
        db_category = await self._get_category_by_id(category_id)
        if not db_category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Category not found"
            )

        # Проверяем parent_id, если указан
        if category.parent_id is not None:
            parent = await self._get_category_by_id(category.parent_id)
            if not parent:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, 
                    detail="Parent category not found"
                )
            if parent.id == category_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, 
                    detail="Category cannot be its own parent"
                )

        # Обновляем категорию
        update_data = category.model_dump(exclude_unset=True)
        await self.db.execute(
            update(CategoryModel)
            .where(CategoryModel.id == category_id)
            .values(**update_data)
        )
        await self.db.commit()
        return db_category

    async def _get_category_by_id(self, category_id: int):
        """Вспомогательный метод для получения категории по ID"""
        stmt = select(CategoryModel).where(CategoryModel.id == category_id)
        result = await self.db.scalars(stmt)
        return result.first()