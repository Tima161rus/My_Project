from sqlalchemy import Boolean, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING

from app.database import Base

if TYPE_CHECKING:
    from app.models.products import Product
    from app.models.reviews import Review
    from app.models.cart import Cart
    from app.models.wishlist import Wishlist

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    role: Mapped[str] = mapped_column(String, default="buyer")  # "buyer" or "seller" or "admin"

    products: Mapped[list["Product"]] = relationship("Product", back_populates="seller")
    reviews : Mapped[list['Review']] = relationship('Review', back_populates='user')
    cart: Mapped["Cart"] = relationship("Cart", back_populates="user", uselist=False)
    wishlist: Mapped['Wishlist'] = relationship('Wishlist', back_populates='user')
