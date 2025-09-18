from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy import Integer, Boolean, ForeignKey
from typing import TYPE_CHECKING
from app.database import Base

if TYPE_CHECKING:
    
    from app.models.users import User
    from app.models.products import Product

class Wishlist(Base):
    __tablename__ = 'wishlist'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'))

    user: Mapped['User'] = relationship('User', back_populates='wishlist')
    items: Mapped[list['WishlistItem']] = relationship('WishlistItem', back_populates='wishlist')




class WishlistItem(Base):
    __tablename__ = "wishlist_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    wishlist_id: Mapped[int] = mapped_column(ForeignKey('wishlist.id'))
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


    wishlist: Mapped['Wishlist'] = relationship('Wishlist', back_populates='items')
    product: Mapped["Product"] = relationship("Product", back_populates="wishlist_items")
