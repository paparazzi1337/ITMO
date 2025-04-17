from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from schemas import Token, UserLogin
from services.base_user_services import UserService
from database.database import get_session
from datetime import timedelta
from database.config import settings

router = APIRouter(tags=["auth"])

@router.post("/login", response_model=Token)
async def login(
    form_data: UserLogin,
    db: Session = Depends(get_session)
):
    user_service = UserService(db)
    user = user_service.verify_user(form_data.email, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # In a real app, implement proper JWT token creation
    access_token = "fake-jwt-token"
    return {"access_token": access_token, "token_type": "bearer"}