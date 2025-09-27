from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload, with_loader_criteria
from fastapi import HTTPException, status

from app.models.cart import CartItem, Cart
from app.models.products import Product
from app.models.orders import Order, OrderItem
from app.shemas import User
from app.shemas import OrderCreate
from decimal import Decimal


class OrderServics:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_list(self, user: User):
        resalt = await self.db.scalars(select(Order).options(
            selectinload(Order.orderitems).
            selectinload(OrderItem.product),
            with_loader_criteria(Product, Product.is_active == True)
        ).where(Order.user_id == user.id))

        order = resalt.all()
        return order
    
    async def get_id(self, user:User, order_id:int):
        resalt = await self.get_list(user)
        for i in resalt:
            if i.id == order_id:
                return i
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail='Order not found')
        
    async def checkout_order(self, user: User):
        try:
            # 1) Берём активную корзину и блокируем её до конца операции
            cart = await self.db.scalar(
                select(Cart)
                .options(selectinload(Cart.items).selectinload(CartItem.product))
                .where(Cart.user_id == user.id, Cart.is_active == True)
                .with_for_update()
            )
            if not cart or not cart.items:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Корзина пуста")

            # 2) Создаём заказ и получаем ID
            order = Order(user_id=user.id)
            self.db.add(order)
            await self.db.flush()

            # 3) Переносим позиции (фиксируем цены)
            total = Decimal("0.00")
            for ci in cart.items:
                if not ci.is_active:
                    continue
                unit_price = Decimal(str(ci.product.price))
                new_order_item = OrderItem(order_id = order.id,
                          product_id = ci.product.id,
                          price = unit_price,
                          quantity = ci.quantity)
                self.db.add(new_order_item)
                total += unit_price * ci.quantity
                ci.is_active = False

            # 4) Фиксируем сумму, закрываем корзину, создаём новую
            order.total_price = total
            cart.is_active = False

            # Можно создавать новую корзину «лениво» при первом добавлении,
            # но если хочется сразу — оставь так:
            self.db.add(Cart(user_id=user.id, is_active=True))

            # 5) Коммит всей операции
            await self.db.commit()

            # 6) Возвращаем заказ с товаром
            return await self.db.scalar(
                select(Order)
                .options(selectinload(Order.orderitems).selectinload(OrderItem.product))
                .where(Order.id == order.id)
            )

        except IntegrityError:
            await self.db.rollback()
            # Например, частичный уникальный индекс "одна активная корзина на пользователя"
            raise HTTPException(status_code=409, detail="Конфликт данных при оформлении заказа")
        except Exception:
            await self.db.rollback()
            raise