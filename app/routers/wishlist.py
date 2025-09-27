from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated

from app.models.users import User as UserModel
from app.shemas import Wishlist, WishlistItem
from app.database.db_depends import get_async_db
from app.auth import get_current_buyer
from app.services.wishlist import WishlistService

router = APIRouter(prefix='/wishlist', tags=['Wishlist'])


async def get_wishlist_service(db: AsyncSession = Depends(get_async_db)) -> WishlistService:
    """
    Dependency injection для WishlistService
    """
    return WishlistService(db)


@router.get("/", response_model=Wishlist)
async def get_wishlist(
    user: Annotated[UserModel, Depends(get_current_buyer)],
    wishlist_service: WishlistService = Depends(get_wishlist_service)
):
    """
    Получить вишлист текущего пользователя
    """
    wishlist = await wishlist_service.get_wishlist_with_items(user)
    return Wishlist.model_validate(wishlist) 


@router.get('/quantity')
async def get_wishlist_items_count(
    user: Annotated[UserModel, Depends(get_current_buyer)],
    wishlist_service: WishlistService = Depends(get_wishlist_service)
):
    """
    Получить количество товаров в вишлисте
    """
    count = await wishlist_service.get_wishlist_items_count(user)
    return {'count_product': count}


@router.post('/{product_id}', response_model=WishlistItem)
async def add_product_to_wishlist(
    product_id: int,
    user: Annotated[UserModel, Depends(get_current_buyer)],
    wishlist_service: WishlistService = Depends(get_wishlist_service)
):
    """
    Добавить товар в вишлист
    """
    wislist = await wishlist_service.add_product_to_wishlist(user, product_id)
    return WishlistItem.model_validate(wislist)


@router.delete('/{wishlist_item_id}', response_model=WishlistItem)
async def remove_product_from_wishlist(
    wishlist_item_id: int,
    user: Annotated[UserModel, Depends(get_current_buyer)],
    wishlist_service: WishlistService = Depends(get_wishlist_service)
):
    """
    Удалить товар из вишлиста
    """
    wishlist = await wishlist_service.remove_product_from_wishlist(user, wishlist_item_id)
    return wishlist


@router.delete('/')
async def clear_wishlist(
    user: Annotated[UserModel, Depends(get_current_buyer)],
    wishlist_service: WishlistService = Depends(get_wishlist_service)
):
    """
    Очистить весь вишлист
    """
    wislist = await wishlist_service.clear_wishlist(user)
    return Wishlist.model_validate(wislist)