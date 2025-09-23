from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.orm import selectinload, with_loader_criteria
from fastapi import HTTPException, status

from app.models.users import User as UserModel
from app.models.products import Product
from app.models.wishlist import Wishlist as WishlistModel, WishlistItem as WishlistItemModel
from app.shemas import Wishlist, WishlistItem


class WishlistService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_or_create_wishlist(self, user: UserModel) -> WishlistModel:
        """
        Получение или создание вишлиста для пользователя
        """
        wishlist = await self.db.scalar(
            select(WishlistModel)
            .options(
                selectinload(WishlistModel.items)
                .selectinload(WishlistItemModel.product),
                with_loader_criteria(WishlistItemModel, WishlistItemModel.is_active == True),
                with_loader_criteria(Product, Product.is_active == True),
            )
            .where(WishlistModel.user_id == user.id)
        )

        if wishlist:
            return wishlist

        wishlist = WishlistModel(user_id=user.id)
        self.db.add(wishlist)
        await self.db.commit()
        await self.db.refresh(wishlist)
        return wishlist

    async def get_wishlist_items_count(self, user: UserModel) -> int:
        """
        Получение количества товаров в вишлисте
        """
        wishlist = await self.get_or_create_wishlist(user)
        return len(wishlist.items)

    async def add_product_to_wishlist(self, user: UserModel, product_id: int) -> WishlistItemModel:
        """
        Добавление товара в вишлист
        """
        wishlist = await self.get_or_create_wishlist(user)
        
        # Проверяем, есть ли уже товар в вишлисте
        existing_item = await self.db.scalar(
            select(WishlistItemModel)
            .where(
                WishlistItemModel.is_active == True,
                WishlistItemModel.wishlist_id == wishlist.id,
                WishlistItemModel.product_id == product_id
            )
        )
        
        if existing_item:
            return existing_item

        # Создаем новую запись
        wishlist_item = WishlistItemModel(
            wishlist_id=wishlist.id,
            product_id=product_id
        )
        self.db.add(wishlist_item)
        await self.db.commit()
        await self.db.refresh(wishlist_item)
        return wishlist_item

    async def remove_product_from_wishlist(self, user: UserModel, wishlist_item_id: int) -> WishlistItemModel:
        """
        Удаление конкретного товара из вишлиста
        """
        wishlist = await self.get_or_create_wishlist(user)
        
        wishlist_item = await self.db.scalar(
            select(WishlistItemModel)
            .where(
                WishlistItemModel.wishlist_id == wishlist.id,
                WishlistItemModel.id == wishlist_item_id,
                WishlistItemModel.is_active == True
            )
        )
        
        if not wishlist_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Wishlist item not found"
            )
        
        wishlist_item.is_active = False
        await self.db.commit()
        return wishlist_item

    async def clear_wishlist(self, user: UserModel) -> dict:
        """
        Очистка всего вишлиста
        """
        wishlist = await self.get_or_create_wishlist(user)
        
        # Проверяем, есть ли активные элементы
        active_items = await self.db.scalars(
            select(WishlistItemModel)
            .where(
                WishlistItemModel.wishlist_id == wishlist.id,
                WishlistItemModel.is_active == True
            )
        )
        
        if not active_items.all():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No active items in wishlist"
            )
        
        # Деактивируем все элементы вишлиста
        await self.db.execute(
            update(WishlistItemModel)
            .where(WishlistItemModel.wishlist_id == wishlist.id)
            .values(is_active=False)
        )
        await self.db.commit()
        
        return {"status": "ok", "message": "Wishlist cleared successfully"}

    async def get_wishlist_with_items(self, user: UserModel) -> WishlistModel:
        """
        Получение вишлиста с активными товарами
        """
        return await self.get_or_create_wishlist(user)