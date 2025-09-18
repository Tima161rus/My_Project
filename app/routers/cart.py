from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, update, insert
from sqlalchemy.orm import Session, selectinload, with_loader_criteria
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.cart import CartItem as CartItemModel, Cart as CartModel
from app.models.products import Product
from app.models.categories import Category
from app.models.users import User as UserModel
from app.shemas import Cart, CartItems, CartItemCreate

from app.db_depends import get_async_db
from app.auth import get_current_buyer

router = APIRouter(
    prefix="/carts",
    tags=["Carts"],
)

@router.get('/', response_model=Cart)
async def get_user_cart(
    user: Annotated[UserModel, Depends(get_current_buyer)],
    db: Annotated[AsyncSession, Depends(get_async_db)]
):
    '''
    Просмотр всех активных товаров в корзине
    '''
    cart_model = await db.scalar(
        select(CartModel)
        .options(selectinload(CartModel.items).
                 selectinload(CartItemModel.product).
                 selectinload(Product.category),
                 with_loader_criteria(CartItemModel, CartItemModel.is_active == True),
                 with_loader_criteria(Product, Product.is_active == True),
                 with_loader_criteria(Category, Category.is_active == True))
        .where(CartModel.user_id == user.id)
    )

    if not cart_model:
        cart_model = await create_cart(user, db)

    return cart_model

@router.get('/summary')
async def get_cart_summary(
    db: Annotated[AsyncSession, Depends(get_async_db)],
    user: Annotated[UserModel, Depends(get_current_buyer)]
):
    cart = await db.scalar(
        select(CartModel)
        .options(selectinload(CartModel.items).selectinload(CartItemModel.product))
        .where(CartModel.user_id == user.id)
    )
    if not cart:
        raise HTTPException(status_code=404, detail="Корзина не найдена")
    total_items = sum(item.quantity for item in cart.items if item.is_active)
    total_price = sum(item.product.price * item.quantity for item in cart.items if item.is_active)

    return {
        "total_items": total_items,
        "total_price": total_price,
        "currency": "RUB"
    }



@router.get('/view_del_CartItem', response_model=Cart)
async def get_user_cart_del(
    user: Annotated[UserModel, Depends(get_current_buyer)],
    db: Annotated[AsyncSession, Depends(get_async_db)]
):
    '''
    Просмотр удаленых товаров из корзины
    '''
    cart_model = await db.scalar(
        select(CartModel)
        .options(selectinload(CartModel.items).
                 selectinload(CartItemModel.product).
                 selectinload(Product.category),
                 with_loader_criteria(CartItemModel, CartItemModel.is_active == False),
                 with_loader_criteria(Product, Product.is_active == True),
                 with_loader_criteria(Category, Category.is_active == True))
        .where(CartModel.user_id == user.id)
    )

    if not cart_model:
        cart_model = await create_cart(user, db)

    return cart_model

@router.post('/items', response_model=CartItems)
async def add_itens_cart(
    user: Annotated[UserModel, Depends(get_current_buyer)],
    items: CartItemCreate,
    db: Annotated[AsyncSession, Depends(get_async_db)]
):
    '''
    Добавление товаров в корзину
    '''
    cart = await db.scalar(select(CartModel).where(CartModel.user_id == user.id))
    if not cart:
        cart = await create_cart(user, db)

    cart_item = await db.scalar(
        select(CartItemModel)
        .where(
            CartItemModel.cart_id == cart.id,
            CartItemModel.product_id == items.product_id
        )
    )
    if cart_item:
        cart_item.quantity += items.quantity
    else:
        cart_item = CartItemModel(**items.model_dump(), cart_id = cart.id)
        db.add(cart_item)

    await db.commit()
    await db.refresh(cart_item)

    # Подгружаем продукт
    result = await db.execute(
        select(CartItemModel)
        .options(selectinload(CartItemModel.product))
        .where(CartItemModel.id == cart_item.id)
    )
    cart_item = result.scalar_one()

    return cart_item


@router.delete('/items/{id}')
async def del_CartItem(db: Annotated[AsyncSession, Depends(get_async_db)],
                       user: Annotated[AsyncSession, Depends(get_current_buyer)],
                       id: int):
    '''
    Логическое удаление товаров из корзины
    '''
    cartItem = await chek_cart(db, user, id)
    cartItem.is_active = False
    await db.commit()
    await db.refresh(cartItem)
    return cartItem

@router.delete('/all_items')
async def del_all_CartItem(db: Annotated[AsyncSession, Depends(get_async_db)],
                       user: Annotated[AsyncSession, Depends(get_current_buyer)]):
    '''
    Очистить корзину
    '''
    cart = await db.scalar(select(CartModel).
                           where(CartModel.user_id == user.id))

    await db.execute(
        update(CartItemModel)
        .where(CartItemModel.cart_id == cart.id)
        .values(is_active=False))

    await db.commit()
    return {user.id: 'Корзина очищена'}

@router.patch('/items/{id}', response_model=Cart)
async def up_quantity_product(
                            db: Annotated[AsyncSession, Depends(get_async_db)],
                            user: Annotated[AsyncSession, Depends(get_current_buyer)],
                            id: int,
                            count: int):
    '''
    Добавить или уменьшить количство товаров
    '''
    cartItem = await chek_cart(user, db, id)
    cartItem.quantity += count
    if cartItem.quantity < 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={'Количество не может быть меньше нуля': cartItem.quantity})
    
    await db.commit()
    await db.refresh(cartItem)

    cart_model = await db.scalar(
        select(CartModel)
        .options(selectinload(CartModel.items).
                 selectinload(CartItemModel.product).
                 selectinload(Product.category),
                 with_loader_criteria(CartItemModel, CartItemModel.is_active == True),
                 with_loader_criteria(Product, Product.is_active == True),
                 with_loader_criteria(Category, Category.is_active == True))
        .where(CartModel.user_id == user.id)
    )

    return cart_model



async def chek_cart(user: UserModel, db: AsyncSession, id:int):
    '''
    Проверка наличия козины и товара в ней
    '''
    cart = await db.scalar(select(CartModel).
                           where(CartModel.user_id == user.id))
    if not cart:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='Carts not found')
    
    cartItem = await db.scalar(select(CartItemModel).where(CartItemModel.cart_id == cart.id, 
                                                           CartItemModel.id == id,
                                                           CartItemModel.is_active == True))
    if not cartItem:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail= 'CartItem not found')
    return cartItem

async def create_cart(user: UserModel, db: AsyncSession):
    '''
    Создание корзины
    '''
    cart = await db.scalar(select(CartModel).where(CartModel.user_id == user.id))
    if not cart:
        cart = CartModel(user_id=user.id)
        db.add(cart)
        await db.commit()
        await db.refresh(cart)
    return cart