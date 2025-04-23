from contextlib import asynccontextmanager
from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from database.database import init_db
import logging
from typing import AsyncGenerator

# Настройка логгера
#logging.basicConfig(level=logging.INFO)
#logger = logging.getLogger(__name__)

# Импорты всех роутеров
from api.routers.auth import router as auth_router
from api.routers.users import router as users_router
from api.routers.balance import router as balance_router
from api.routers.models import router as models_router
from api.routers.predictions import router as predictions_router

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Lifespan handler для управления событиями жизненного цикла приложения"""
    # Инициализация при запуске
    try:
        init_db(drop_all=True)  # Очищаем и создаем БД заново
        #logger.info("Database initialized and cleared successfully")
    except Exception as e:
        #logger.error(f"Error initializing database: {str(e)}")
        raise
    
    yield  # Приложение работает
    
    # Очистка при завершении (если нужна)
    logger.info("Application shutdown")

app = FastAPI(
    title="ML Prediction Service",
    version="1.0.0",
    description="API для управления ML-моделями и балансом пользователей",
    lifespan=lifespan
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Создаем основной роутер с единым префиксом /api
api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(users_router, tags=["users"])
api_router.include_router(balance_router)
api_router.include_router(models_router)
api_router.include_router(predictions_router)

# Подключаем основной роутер к приложению
app.include_router(api_router, prefix="/api")

@app.get("/")
def read_root():
    return {"message": "ML Prediction Service is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api_main:app", host="0.0.0.0", port=8000, reload=True)