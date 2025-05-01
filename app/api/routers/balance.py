from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from ..schemas import TransactionCreate, TransactionResponse, BalanceResponse
from services.balance_services import BalanceService
from ..dependencies import get_current_user
from database.database import get_session
from models.base_user import BaseUser
from typing import List
from datetime import datetime

router = APIRouter(prefix="/balance", tags=["balance"])

@router.get("/", response_model=BalanceResponse)
def get_user_balance(
    current_user: BaseUser = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    balance_service = BalanceService(db)
    amount = balance_service.get_balance(current_user)
    return {"amount": amount, "updated_at": datetime.utcnow()}

@router.post("/deposit", response_model=TransactionResponse)
def deposit(
    transaction: TransactionCreate,
    current_user: BaseUser = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    balance_service = BalanceService(db)
    try:
        tx_id = balance_service.deposit(
            current_user,
            transaction.amount,
            transaction.description
        )
        balance_service.deposit(current_user, tx_id)
        return RedirectResponse(url="/balance/", status_code=303)  # Редирект после успеха
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/history", response_model=List[TransactionResponse])
def get_transaction_history(
    current_user: BaseUser = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    balance_service = BalanceService(db)
    return balance_service.get_transaction_history(current_user.user_id)