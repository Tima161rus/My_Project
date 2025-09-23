from fastapi import APIRouter, Depends, status
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.db_depends import get_async_db
from app.auth import get_current_seller
from app.models.users import User as UserModel
from app.shemas import Product as ProductSchema, ProductCreate, Review as ReviewShemas
from app.services.products import ProductService

router = APIRouter(
    prefix="/products",
    tags=["Products"],
)


def get_product_service(db: AsyncSession = Depends(get_async_db)) -> ProductService:
    """Зависимость для получения сервиса продуктов"""
    return ProductService(db)


@router.post("/", response_model=ProductSchema, status_code=status.HTTP_201_CREATED)
async def create_product(
    product: ProductCreate,
    current_user: Annotated[UserModel, Depends(get_current_seller)],
    product_service: ProductService = Depends(get_product_service)
):
    """
    Создаёт новый товар, привязанный к текущему продавцу (только для 'seller').
    """
    return await product_service.create_product(product, current_user)


@router.get("/", response_model=list[ProductSchema])
async def get_all_products(
    product_service: ProductService = Depends(get_product_service)
):
    """
    Возвращает список всех активных товаров.
    """
    return await product_service.get_all_products()


@router.get("/category/{category_id}", response_model=list[ProductSchema])
async def get_products_by_category(
    category_id: int,
    product_service: ProductService = Depends(get_product_service)
):
    """
    Возвращает список активных товаров в указанной категории по её ID.
    """
    return await product_service.get_products_by_category(category_id)


@router.get("/{product_id}", response_model=ProductSchema)
async def get_product(
    product_id: int,
    product_service: ProductService = Depends(get_product_service)
):
    """
    Возвращает детальную информацию о товаре по его ID.
    """
    return await product_service.get_product(product_id)


@router.put("/{product_id}", response_model=ProductSchema)
async def update_product(
    product_id: int,
    product: ProductCreate,
    current_user: Annotated[UserModel, Depends(get_current_seller)],
    product_service: ProductService = Depends(get_product_service)
):
    """
    Обновляет товар, если он принадлежит текущему продавцу (только для 'seller').
    """
    return await product_service.update_product(product_id, product, current_user)


@router.delete("/{product_id}", response_model=ProductSchema)
async def delete_product(
    product_id: int,
    current_user: Annotated[UserModel, Depends(get_current_seller)],
    product_service: ProductService = Depends(get_product_service)
):
    """
    Выполняет мягкое удаление товара, если он принадлежит текущему продавцу (только для 'seller').
    """
    return await product_service.delete_product(product_id, current_user)


@router.get('/{product_id}/reviews/', response_model=list[ReviewShemas])
async def get_product_reviews(
    product_id: int,
    product_service: ProductService = Depends(get_product_service)
):
    """
    Возвращает активные отзывы для продукта.
    """
    return await product_service.get_product_reviews(product_id)