from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware

# Импорты всех роутеров
from api.routers.auth import router as auth_router
from api.routers.users import router as users_router
from api.routers.balance import router as balance_router
from api.routers.models import router as models_router
from api.routers.predictions import router as predictions_router

app = FastAPI(
    title="ML Prediction Service",
    version="1.0.0",
    description="API для управления ML-моделями и балансом пользователей"
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
api_router.include_router(auth_router, prefix="/auth")
api_router.include_router(users_router, tags=["users"])
api_router.include_router(balance_router, prefix="/balance")
api_router.include_router(models_router, prefix="/models")
api_router.include_router(predictions_router, prefix="/predictions")

# Подключаем основной роутер к приложению
app.include_router(api_router, prefix="/api")

@app.get("/")
def read_root():
    return {"message": "ML Prediction Service is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api_main:app", host="0.0.0.0", port=8000, reload=True)