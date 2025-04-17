from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..schemas import ModelCreate, ModelResponse
from services.model_services import ModelService
from ..dependencies import get_current_user
from database.database import get_session
from models.base_user import BaseUser
from uuid import uuid4

router = APIRouter(prefix="/models", tags=["models"])

@router.post("/", response_model=ModelResponse)
def create_model(
    model: ModelCreate,
    current_user: BaseUser = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    model_service = ModelService(db)
    try:
        db_model = model_service.create_model({
            'model_id': str(uuid4()),
            'name': model.name,
            'owner_id': current_user.user_id,
            'model_type': model.model_type
        })
        return db_model
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))