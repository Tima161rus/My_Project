from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
import jwt

from app.models.users import User as UserModel
from app.shemas import UserCreate, User as UserSchema
from app.auth import hash_password, verify_password, create_access_token, create_refresh_token
from app.config import SECRET_KEY, ALGORITHM


class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_user(self, user_data: UserCreate) -> UserModel:
        """
        Создание нового пользователя
        """
        # Проверка уникальности email
        result = await self.db.scalars(
            select(UserModel).where(UserModel.email == user_data.email.lower())
        )
        if result.first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        # Создание объекта пользователя
        db_user = UserModel(
            email=user_data.email.lower(),
            hashed_password=hash_password(user_data.password),
            role=user_data.role
        )

        self.db.add(db_user)
        await self.db.commit()
        await self.db.refresh(db_user)
        return db_user

    async def authenticate_user(self, email: str, password: str) -> UserModel | None:
        """
        Аутентификация пользователя
        """
        result = await self.db.scalars(select(UserModel).where(UserModel.email == email))
        user = result.first()
        
        if not user or not verify_password(password, user.hashed_password):
            return None
        
        return user

    async def login_user(self, form_data: OAuth2PasswordRequestForm) -> dict:
        """
        Логин пользователя и генерация токенов
        """
        user = await self.authenticate_user(form_data.username, form_data.password)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        access_token = create_access_token(data={"sub": user.email, "role": user.role, "id": user.id})
        refresh_token = create_refresh_token(data={"sub": user.email, "role": user.role, "id": user.id})
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }

    async def refresh_access_token(self, refresh_token: str) -> dict:
        """
        Обновление access token
        """
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
        try:
            payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
            email: str = payload.get("sub")
            if email is None:
                raise credentials_exception
        except jwt.exceptions:
            raise credentials_exception
            
        result = await self.db.scalars(select(UserModel).where(
            UserModel.email == email, 
            UserModel.is_active == True
        ))
        user = result.first()
        
        if user is None:
            raise credentials_exception
            
        access_token = create_access_token(data={"sub": user.email, "role": user.role, "id": user.id})
        return {"access_token": access_token, "token_type": "bearer"}

    async def get_user_by_email(self, email: str) -> UserModel | None:
        """
        Получение пользователя по email
        """
        result = await self.db.scalars(
            select(UserModel).where(UserModel.email == email)
        )
        return result.first()

    async def get_user_by_id(self, user_id: int) -> UserModel | None:
        """
        Получение пользователя по ID
        """
        result = await self.db.scalars(
            select(UserModel).where(UserModel.id == user_id)
        )
        return result.first()