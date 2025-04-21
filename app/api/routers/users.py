from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..schemas import UserCreate, UserResponse
from services.base_user_services import UserService
from database.database import get_session
from uuid import uuid4

router = APIRouter(prefix="/users")

@router.post("/", response_model=UserResponse)
def create_user(
    user: UserCreate,
    db: Session = Depends(get_session)
):
    user_service = UserService(db)
    try:
        db_user = user_service.create_user({
            'user_id': str(uuid4()),
            'username': user.username,
            'email': user.email,
            'password': user.password,
            'role': "regular"
        })
        return db_user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))