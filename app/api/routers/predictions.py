from uuid import uuid4
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..schemas import PredictionCreate, PredictionResponse
from services.prediction_history_services import PredictionService
from services.balance_services import BalanceService
from ..dependencies import get_current_user
from database.database import get_session
from models.base_user import BaseUser
from typing import List
from decimal import Decimal

router = APIRouter(prefix="/predictions", tags=["predictions"])

PREDICTION_COST = Decimal('10')

@router.post("/", response_model=PredictionResponse)
def create_prediction(
    prediction: PredictionCreate,
    current_user: BaseUser = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    prediction_service = PredictionService(db)
    balance_service = BalanceService(db)
    
    try:
        balance_service.withdraw(
            current_user.user_id,
            PREDICTION_COST,
            f"Prediction using model {prediction.model_id}"
        )
        
        task = prediction_service.create_task({
            'task_id': str(uuid4()),
            'user_id': current_user.user_id,
            'model_id': prediction.model_id,
            'input_data': prediction.input_data
        })
        
        prediction_service.complete_task(task.task_id, {"result": "sample"})
        
        return task
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/history", response_model=List[PredictionResponse])
def get_prediction_history(
    current_user: BaseUser = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    prediction_service = PredictionService(db)
    return prediction_service.get_user_history(current_user)