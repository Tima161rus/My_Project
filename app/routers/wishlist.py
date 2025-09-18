from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, update, insert
from sqlalchemy.orm import Session, selectinload, with_loader_criteria
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession


from app.models.products import Product
from app.models.users import User as UserModel
from app.models.wishlist import Wishlist as WishlistModel, WishlistItem as WishlistItemModel
from app.shemas import Wishlist, WishlistItem

from app.db_depends import get_async_db
from app.auth import get_current_buyer

router = APIRouter(prefix='/wishlist',
                   tags=['Wishlist'])

@router.get("/", response_model=Wishlist)
async def get_wishlist(
    db: Annotated[AsyncSession, Depends(get_async_db)],
    user: Annotated[UserModel, Depends(get_current_buyer)]
):
    '''
    вернуть вишлист
    '''
    wishlist = await chek_create_wishlist(db, user)
    return wishlist

@router.post('/{id_product}', response_model=WishlistItem)
async def add_product_wishlist(id_product: int,
        db: Annotated[AsyncSession, Depends(get_async_db)],
    user: Annotated[UserModel, Depends(get_current_buyer)]
):
    '''
    Добавить товар
    '''
    wish = await chek_create_wishlist(db, user)
    wishItem  = await db.scalar(select(WishlistItemModel).
                                where(WishlistItemModel.is_active == True,
                                      WishlistItemModel.wishlist_id == wish.id,
                                      WishlistItemModel.product_id == id_product))
    if not wishItem:
        res = WishlistItemModel(wishlist_id = wish.id,
                                           product_id = id_product)
        db.add(res)
        await db.commit()
        return res
    
    return wishItem

@router.delete('/{id_wishItem}', response_model=WishlistItem)
async def del_product(db: Annotated[AsyncSession, Depends(get_async_db)],
    user: Annotated[UserModel, Depends(get_current_buyer)],
    id_wishItem: int
):
    '''
    Удалить товар из виш листа
    '''
    wishList = await chek_create_wishlist(db, user)
    wishItem = await db.scalar(select(WishlistItemModel).
                         where(WishlistItemModel.wishlist_id == wishList.id,
                               WishlistItemModel.id == id_wishItem,
                               WishlistItemModel.is_active == True))
    if not wishItem:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND)
    wishItem.is_active = False

    await db.commit()
    return wishItem

@router.delete('/')
async def del_all(db: Annotated[AsyncSession, Depends(get_async_db)],
    user: Annotated[UserModel, Depends(get_current_buyer)],
):
    '''
    Очистить виш лист
    '''
    wishList = await chek_create_wishlist(db, user)
    wishItem = await db.scalars(select(WishlistItemModel).
                         where(WishlistItemModel.wishlist_id == wishList.id,
                               WishlistItemModel.is_active == True))
    if not wishItem.all():
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND)
    
    await db.execute(update(WishlistItemModel).where(WishlistItemModel.wishlist_id == wishList.id).
                     values(is_active = False))
    await db.commit()
    return {"status": "ok"}

async def chek_create_wishlist(db: AsyncSession, user: UserModel) -> WishlistModel:
    '''
    Проверка и создание вишлиста
    '''
    wishlist = await db.scalar(
        select(WishlistModel)
        .options(
            selectinload(WishlistModel.items).
            selectinload(WishlistItemModel.product),
            with_loader_criteria(WishlistItemModel, WishlistItemModel.is_active == True),
            with_loader_criteria(Product, Product.is_active == True),
        )
        .where(WishlistModel.user_id == user.id)
    )

    if wishlist:
        return wishlist

    wishlist = WishlistModel(user_id=user.id)
    db.add(wishlist)
    await db.commit()
    await db.refresh(wishlist)
    return wishlist