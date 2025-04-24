from contextlib import asynccontextmanager
from datetime import datetime
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import os
import logging
from typing import AsyncGenerator

# Импорты роутеров
from api.routers.auth import router as auth_router
from api.routers.users import router as users_router
from api.routers.balance import router as balance_router
from api.routers.models import ml_route as models_router
from api.routers.predictions import router as predictions_router
from api.routers.web import router as web_router

from database.database import init_db, get_session
from database.config import settings
from services.base_user_services import UserService
from jose import jwt

# Настройка логгера
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Lifespan handler для управления событиями жизненного цикла приложения"""
    try:
        init_db(drop_all=True)
        os.makedirs("app/static/css", exist_ok=True)
        os.makedirs("app/templates", exist_ok=True)
    except Exception as e:
        logger.error(f"Error initializing: {str(e)}")
        raise
    yield
    logger.info("Application shutdown")

app = FastAPI(
    title="ML Prediction Service",
    version="1.0.0",
    description="API и веб-интерфейс для управления ML-моделями",
    lifespan=lifespan
)

# Подключаем статические файлы
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Инициализация Jinja2 для веб-роутера
templates = Jinja2Templates(directory="app/templates")
web_router.templates = templates
web_router.create_access_token = lambda data, expires_delta: jwt.encode(
    {**data, "exp": datetime.utcnow() + expires_delta},
    settings.SECRET_KEY,
    algorithm=settings.ALGORITHM
)

# Подключаем CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем все роутеры
app.include_router(auth_router, prefix="/api/auth")
app.include_router(users_router, prefix="/api/users")
app.include_router(balance_router, prefix="/api/balance")
app.include_router(models_router, prefix="/api/models")
app.include_router(predictions_router, prefix="/api/predictions")
app.include_router(web_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api_main:app", host="0.0.0.0", port=8000, reload=True)