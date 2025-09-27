from fastapi import FastAPI

from app.routers import categories, products, users, reviews, cart, wishlist, order
from fastapi.middleware.cors import CORSMiddleware

# Создаём приложение FastAPI
app = FastAPI(
    title="FastAPI Интернет-магазин",
    version="0.1.0",
)

# Подключаем маршруты категорий и товаров
app.include_router(categories.router, prefix="/api")
app.include_router(products.router, prefix="/api")
app.include_router(users.router, prefix="/api")
app.include_router(reviews.router, prefix="/api")
app.include_router(cart.router, prefix="/api")
app.include_router(wishlist.router, prefix="/api")
app.include_router(order.router, prefix="/api")


# Корневой эндпоинт для проверки
@app.get("/")
async def root():
    """
    Корневой маршрут, подтверждающий, что API работает.
    """
    return {"message": "Добро пожаловать в API интернет-магазина!"}


from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)