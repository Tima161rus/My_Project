from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Float, Integer, String, ForeignKey, func, DateTime
from typing import TYPE_CHECKING

from app.database.database import Base

if TYPE_CHECKING:
    from app.models.users import User
    from app.models.products import Product

class Order(Base):
    __tablename__ = 'orders'

    id:Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'))
    status: Mapped[str] = mapped_column(String, default="pending")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())
    @property
    def total_price(self) -> float:
        return sum(item.price * item.quantity for item in self.orderitems)

    user: Mapped['User'] = relationship('User', back_populates='orders')
    orderitems: Mapped[list['OrderItem']] = relationship('OrderItem', back_populates='order')
    
    
class OrderItem(Base):
    __tablename__ = 'orderitems'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey('orders.id'))
    product_id: Mapped[int] = mapped_column(ForeignKey('products.id'))
    price: Mapped[float] = mapped_column(Float, default=0.0)
    quantity: Mapped[int] = mapped_column(Integer, default=1)

    order: Mapped['Order'] = relationship('Order', back_populates='orderitems')
    product: Mapped['Product']  = relationship('Product', back_populates='orderitems')