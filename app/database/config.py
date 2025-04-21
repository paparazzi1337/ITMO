from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from typing import Optional

class Settings(BaseSettings):
    # Database settings
    DB_HOST: Optional[str] = None
    DB_PORT: Optional[int] = None
    DB_USER: Optional[str] = None
    DB_PASS: Optional[str] = None
    DB_NAME: Optional[str] = None
    
    # Application settings
    APP_NAME: Optional[str] = None
    DEBUG: Optional[bool] = None
    API_VERSION: Optional[str] = None
    
    # JWT settings (добавляем новые поля)
    SECRET_KEY: str = "4fa426a8796848ffa27b6444bcfbacd17e342617a6718b095d2123a96d0433b5"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    @property
    def DATABASE_URL_asyncpg(self):
        return f'postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}'
    
    @property
    def DATABASE_URL_psycopg(self):
        return f'postgresql+psycopg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}'
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True
    )
    
    def validate(self) -> None:
        """Validate critical configuration settings"""
        if not all([self.DB_HOST, self.DB_USER, self.DB_PASS, self.DB_NAME]):
            raise ValueError("Missing required database configuration")
        
        # Добавляем валидацию для JWT (только в production)
        if not self.DEBUG and self.SECRET_KEY == "default-insecure-key-for-dev":
            raise ValueError("You must set JWT_SECRET_KEY in production environment")

@lru_cache()
def get_settings() -> Settings:
    settings = Settings()
    settings.validate()
    return settings


settings = get_settings()