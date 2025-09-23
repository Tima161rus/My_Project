from sqlalchemy import select, update
from sqlalchemy.orm import selectinload, with_loader_criteria
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.models.cart import CartItem as CartItemModel, Cart as CartModel
from app.models.products import Product
from app.models.categories import Category
from app.models.users import User as UserModel
from app.shemas import CartItemCreate


class CartService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user_cart(self, user: UserModel, include_inactive: bool = False):
        """
        Получение корзины пользователя
        """
        cart_model = await self.db.scalar(
            select(CartModel)
            .options(
                selectinload(CartModel.items)
                .selectinload(CartItemModel.product)
                .selectinload(Product.category),
                with_loader_criteria(CartItemModel, CartItemModel.is_active == (not include_inactive)),
                with_loader_criteria(Product, Product.is_active == True),
                with_loader_criteria(Category, Category.is_active == True)
            )
            .where(CartModel.user_id == user.id)
        )

        if not cart_model:
            cart_model = await self._create_cart(user)

        return cart_model

    async def get_cart_summary(self, user: UserModel):
        """
        Получение сводки по корзине
        """
        cart = await self.db.scalar(
            select(CartModel)
            .options(selectinload(CartModel.items).
                     selectinload(CartItemModel.product))
            .where(CartModel.user_id == user.id)
        )
        
        if not cart:
            raise HTTPException(status_code=404, detail="Корзина не найдена")
            
        total_items = sum(item.quantity for item in cart.items if item.is_active)
        total_price = sum(item.product.price * item.quantity for item in cart.items if item.is_active)

        return {
            "total_items": total_items,
            "total_price": total_price,
            "currency": "RUB"
        }

    async def add_item_to_cart(self, user: UserModel, item_data: CartItemCreate):
        """
        Добавление товара в корзину
        """
        cart = await self._get_or_create_cart(user)

        # Проверяем существование товара
        product = await self.db.scalar(
            select(Product).where(Product.id == item_data.product_id, Product.is_active == True)
        )
        if not product:
            raise HTTPException(status_code=404, detail="Товар не найден")

        # Проверяем, есть ли уже такой товар в корзине
        cart_item = await self.db.scalar(
            select(CartItemModel)
            .where(
                CartItemModel.cart_id == cart.id,
                CartItemModel.product_id == item_data.product_id,
                CartItemModel.is_active == True
            )
        )

        if cart_item:
            cart_item.quantity += item_data.quantity
        else:
            cart_item = CartItemModel(**item_data.model_dump(), cart_id=cart.id)
            self.db.add(cart_item)

        await self.db.commit()
        await self.db.refresh(cart_item)

        # Подгружаем связанные данные
        result = await self.db.execute(
            select(CartItemModel)
            .options(selectinload(CartItemModel.product))
            .where(CartItemModel.id == cart_item.id)
        )
        return result.scalar_one()

    async def remove_item(self, user: UserModel, item_id: int):
        """
        Удаление товара из корзины
        """
        cart_item = await self._check_cart_item(user, item_id)
        cart_item.is_active = False
        await self.db.commit()
        await self.db.refresh(cart_item)
        return cart_item

    async def clear_cart(self, user: UserModel):
        """
        Очистка корзины
        """
        cart = await self._get_or_create_cart(user)

        await self.db.execute(
            update(CartItemModel)
            .where(CartItemModel.cart_id == cart.id)
            .values(is_active=False)
        )
        await self.db.commit()
        return {"user_id": user.id, "message": "Корзина очищена"}

    async def update_item_quantity(self, user: UserModel, item_id: int, count: int):
        """
        Обновление количества товара
        """
        cart_item = await self._check_cart_item(user, item_id)
        cart_item.quantity += count
        
        if cart_item.quantity < 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Количество не может быть меньше нуля: {cart_item.quantity}"
            )

        await self.db.commit()
        await self.db.refresh(cart_item)

        # Возвращаем обновленную корзину
        return await self.get_user_cart(user)

    async def _get_or_create_cart(self, user: UserModel):
        """
        Получение или создание корзины
        """
        cart = await self.db.scalar(
            select(CartModel).where(CartModel.user_id == user.id)
        )
        
        if not cart:
            cart = CartModel(user_id=user.id)
            self.db.add(cart)
            await self.db.commit()
            await self.db.refresh(cart)
            
        return cart

    async def _check_cart_item(self, user: UserModel, item_id: int):
        """
        Проверка наличия товара в корзине
        """
        cart = await self._get_or_create_cart(user)
        
        cart_item = await self.db.scalar(
            select(CartItemModel)
            .where(
                CartItemModel.cart_id == cart.id,
                CartItemModel.id == item_id,
                CartItemModel.is_active == True
            )
        )
        
        if not cart_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Товар не найден в корзине"
            )
            
        return cart_item

    async def _create_cart(self, user: UserModel):
        """
        Создание новой корзины
        """
        cart = CartModel(user_id=user.id)
        self.db.add(cart)
        await self.db.commit()
        await self.db.refresh(cart)
        return cart