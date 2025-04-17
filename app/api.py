from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware

# Импорты всех роутеров
from api.routers.auth import router as auth_router
from api.routers.users import router as users_router
from api.routers.balance import router as balance_router
from api.routers.models import router as models_router
from api.routers.predictions import router as predictions_router

app = FastAPI(title="ML Prediction Service")

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Создаем и подключаем роутеры прямо здесь
api_router = APIRouter(prefix="/api")
api_router.include_router(auth_router)
api_router.include_router(users_router)
api_router.include_router(balance_router)
api_router.include_router(models_router)
api_router.include_router(predictions_router)

app.include_router(api_router)

@app.get("/")
def read_root():
    return {"message": "ML Prediction Service is running"}