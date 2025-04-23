from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from models.base_user import BaseUser
from services.base_user_services import UserService
from database.database import get_session
from database.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login", scheme_name="BearerAuth")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_session)
) -> BaseUser:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        
        user_service = UserService(db)
        user = user_service.get_by_username(username)  # Исправлено!
        if not user:
            raise credentials_exception
        return user
    except JWTError:
        raise credentials_exception