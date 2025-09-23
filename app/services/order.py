from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, with_loader_criteria
from fastapi import HTTPException, status

from app.models.cart import CartItem, Cart
from app.models.products import Product
from app.models.orders import Order, OrderItem
from app.shemas import User


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
        