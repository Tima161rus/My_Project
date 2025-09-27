from fastapi import APIRouter, Depends, HTTPException, status
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_buyer
from app.services.order import OrderServics
from app.shemas import OrderOut, OrderCreate, OrderItemOut
from app.database.db_depends import get_async_db
from app.shemas import User

router = APIRouter(
    prefix="/orders",
    tags=["Order"],
)

async def get_order_service(db: AsyncSession = Depends(get_async_db)) -> OrderServics:
    """
    Dependency injection для OrderServics
    """
    return OrderServics(db)

@router.get("/", response_model=list[OrderOut])
async def list_orders(
    user: Annotated[User, Depends(get_current_buyer)],
    order_servics: Annotated[OrderServics, Depends(get_order_service)]
):
    '''
    Вернуть список заказов
    '''
    order = await order_servics.get_list(user)
    return [OrderOut.model_validate(order) for order in order]


@router.get("/{order_id}", response_model=OrderOut)
async def get_order_id(
    order_id: int,
    order_servics: Annotated[OrderServics, Depends(get_order_service)],
    user: Annotated[User, Depends(get_current_buyer)],
):
    '''
    Вернуть конкретный товар из заказа
    '''
    order = await order_servics.get_id(user, order_id)
    return OrderOut.model_validate(order)



@router.post("/", response_model=OrderOut, status_code=status.HTTP_201_CREATED)
async def checkout_order(
    
    order_servics: Annotated[OrderServics, Depends(get_order_service)],
    user: Annotated[User, Depends(get_current_buyer)],
):
    '''
    Создать заказ
    '''
    db_order = await order_servics.checkout_order(user)
    return OrderOut.model_validate(db_order)


