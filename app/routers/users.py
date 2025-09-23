from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated

from app.shemas import UserCreate, User as UserSchema
from app.database.db_depends import get_async_db
from app.services.users import UserService

router = APIRouter(prefix="/users", tags=["users"])


async def get_user_service(db: AsyncSession = Depends(get_async_db)) -> UserService:
    """
    Dependency injection для UserService
    """
    return UserService(db)


@router.post("/", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
async def create_user(
    user: UserCreate,
    user_service: UserService = Depends(get_user_service)
):
    """
    Регистрирует нового пользователя с ролью 'buyer' или 'seller'.
    """
    
    return await user_service.create_user(user)


@router.post("/token")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    user_service: UserService = Depends(get_user_service)
):
    """
    Аутентифицирует пользователя и возвращает access_token и refresh_token.
    """
    return await user_service.login_user(form_data)


@router.post("/refresh-token")
async def refresh_token(
    refresh_token: str,
    user_service: UserService = Depends(get_user_service)
):
    """
    Обновляет access_token с помощью refresh_token.
    """
    return await user_service.refresh_access_token(refresh_token)