from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Float, Integer, ForeignKey, func, DateTime, Enum as SqlEnum
from enum import Enum
from typing import TYPE_CHECKING

from app.database.database import Base

if TYPE_CHECKING:
    from app.models.users import User
    from app.models.products import Product

class OrderStatus(str, Enum):
        PENDING = "pending"
        PAID = "paid"
        CANCELLED = "cancelled"
        COMPLETED = "completed"  

  
class Order(Base):
    __tablename__ = 'orders'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'))
    status: Mapped[OrderStatus] = mapped_column(SqlEnum(OrderStatus), default=OrderStatus.PENDING)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())
    _total_price: Mapped[float] = mapped_column(Float, default=0.0)  # Скрытая переменная для хранения суммы

    @property
    def total_price(self) -> float:
        return self._total_price

    @total_price.setter
    def total_price(self, value: float) -> None:
        self._total_price = value

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