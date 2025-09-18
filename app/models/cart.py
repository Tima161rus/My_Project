from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, text, ForeignKey, Boolean
from typing import TYPE_CHECKING
from app.database import Base

if TYPE_CHECKING:
    from app.models.users import User
    from app.models.products import Product



class Cart(Base):
    __tablename__ = 'carts'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), unique=True)

    user: Mapped['User'] = relationship('User', back_populates='cart')
    items: Mapped[list["CartItem"]] = relationship("CartItem", back_populates="cart")


class CartItem(Base):
    __tablename__ = "cart_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    cart_id: Mapped[int] = mapped_column(ForeignKey("carts.id"))
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    quantity: Mapped[int] = mapped_column(Integer, default=1)
    is_active: Mapped[bool] = mapped_column(Boolean, 
                                        server_default=text("true"), 
                                        nullable=False)

    cart: Mapped["Cart"] = relationship("Cart", back_populates="items")
    product: Mapped["Product"] = relationship("Product")
