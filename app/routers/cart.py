from fastapi import APIRouter, Depends, status
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.db_depends import get_async_db
from app.auth import get_current_buyer
from app.models.users import User as UserModel
from app.shemas import Cart, CartItems, CartItemCreate

def cart_to_dict(cart):
    return {
        "id": cart.id,
        "user_id": cart.user_id,
        "items": [
            {
                "id": item.id,
                "product_id": item.product_id,
                "quantity": item.quantity,
                "is_active": item.is_active,
                "product": {
                    "id": item.product.id,
                    "name": item.product.name,
                    "price": item.product.price,
                    "category_id": item.product.category_id,
                    "category": {
                        "name": item.product.category.name
                    } if item.product.category else None,
                } if item.product else None,
                "total_price_product": getattr(item, "total_price_product", None)
            }
            for item in getattr(cart, "items", [])
        ],
        "total": getattr(cart, "total", None),
        "sum": getattr(cart, "sum", None)
    }
from app.services.cart import CartService

router = APIRouter(
    prefix="/carts",
    tags=["Carts"],
)


def get_cart_service(db: AsyncSession = Depends(get_async_db)) -> CartService:
    """Зависимость для получения сервиса корзины"""
    return CartService(db)


@router.get('/', response_model=Cart)
async def get_user_cart(
    user: Annotated[UserModel, Depends(get_current_buyer)],
    cart_service: CartService = Depends(get_cart_service)
):
    """
    Просмотр всех активных товаров в корзине
    """
    cart = await cart_service.get_user_cart(user)
    return Cart.model_validate(cart_to_dict(cart))#cart#Cart.model_validate(cart)


@router.get('/summary')
async def get_cart_summary(
    user: Annotated[UserModel, Depends(get_current_buyer)],
    cart_service: CartService = Depends(get_cart_service)
):
    """
    Получение сводки по корзине
    """
    cart = await cart_service.get_cart_summary(user)
    return cart


@router.get('/view_del_CartItem', response_model=Cart)
async def get_user_cart_del(
    user: Annotated[UserModel, Depends(get_current_buyer)],
    cart_service: CartService = Depends(get_cart_service)
):
    """
    Просмотр удаленных товаров из корзины
    """
    cart = await cart_service.get_user_cart(user, include_inactive=True)
    return Cart.model_validate(cart_to_dict(cart))


@router.post('/items', response_model=CartItems)
async def add_items_cart(
    user: Annotated[UserModel, Depends(get_current_buyer)],
    items: CartItemCreate,
    cart_service: CartService = Depends(get_cart_service)
):
    """
    Добавление товаров в корзину
    """
    await cart_service.add_item_to_cart(user, items)
    cart = await cart_service.get_user_cart(user)
    return Cart.model_validate(cart_to_dict(cart))


@router.delete('/items/{item_id}')
async def del_cart_item(
    item_id: int,
    user: Annotated[UserModel, Depends(get_current_buyer)],
    cart_service: CartService = Depends(get_cart_service)
):
    """
    Логическое удаление товаров из корзины
    """
    return await cart_service.remove_item(user, item_id)


@router.delete('/all_items')
async def del_all_cart_item(
    user: Annotated[UserModel, Depends(get_current_buyer)],
    cart_service: CartService = Depends(get_cart_service)
):
    """
    Очистить корзину
    """
    cart = await cart_service.clear_cart(user)
    return Cart.model_validate(cart)


@router.patch('/items/{item_id}', response_model=Cart)
async def update_quantity_product(
    item_id: int,
    count: int,
    user: Annotated[UserModel, Depends(get_current_buyer)],
    cart_service: CartService = Depends(get_cart_service)
):
    """
    Добавить или уменьшить количество товаров
    """
    cart = await cart_service.update_item_quantity(user, item_id, count)
    return Cart.model_validate(cart_to_dict(cart))



