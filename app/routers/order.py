from fastapi import APIRouter, Depends, HTTPException, status
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_buyer
from app.services.order import OrderServics
from app.shemas import OrderOut
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
    order = await order_servics.get_id(user, order_id)
    return OrderOut.model_validate(order)


# @router.post("/", response_model=OrderOut, status_code=status.HTTP_201_CREATED)
# async def create_new_order(
#     db: Annotated[AsyncSession, Depends(get_async_db)],
#     user: Annotated[UserModel, Depends(get_current_buyer)],
# ):
#     return await create_order(db, user)


# async def get_orders(db: AsyncSession, user: UserModel):
#     result = await db.scalars(
#         select(Order)
#         .options(
#             selectinload(Order.orderitems).selectinload(OrderItem.product),
#             with_loader_criteria(Product, Product.is_active == True),
#         )
#         .where(Order.user_id == user.id)
#     )
#     return result.all()


# async def get_order(db: AsyncSession, user: UserModel, order_id: int):
#     return await db.scalar(
#         select(Order)
#         .options(
#             selectinload(Order.orderitems).selectinload(OrderItem.product),
#             with_loader_criteria(Product, Product.is_active == True),
#         )
#         .where(Order.user_id == user.id, Order.id == order_id)
#     )


# async def create_order(db: AsyncSession, user: UserModel):
#     order = Order(user_id=user.id)
#     db.add(order)
#     await db.commit()
#     await db.refresh(order)
#     return order

