from sqlalchemy import Integer, String, Text, BOOLEAN, ForeignKey
from sqlalchemy.orm import relationship, mapped_column, Mapped
from typing import TYPE_CHECKING
from datetime import datetime, timezone
from app.database.database import Base
if TYPE_CHECKING:

    from app.models.users import User
    from app.models.products import Product

class Review(Base):
    __tablename__ = 'reviews'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    product_id: Mapped[int] = mapped_column(Integer, ForeignKey('products.id'), nullable=False, index=True)
    comment: Mapped[str] = mapped_column(Text, nullable=True)
    comment_date: Mapped[datetime] = mapped_column(default=datetime.now)
    grade: Mapped[int] = mapped_column(Integer)
    is_active: Mapped[bool] = mapped_column(BOOLEAN, default=True)

    user: Mapped['User'] = relationship('User', back_populates='reviews')
    product: Mapped['Product'] = relationship('Product', back_populates='reviews')