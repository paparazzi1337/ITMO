from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import Optional

from services.balance_services import BalanceService
from ..dependencies import get_current_user
from models.base_user import BaseUser
from services.base_user_services import UserService
from database.database import get_session
from database.config import settings
from jose import JWTError
from models.base_user import BaseUser

from .auth import create_access_token

router = APIRouter()

@router.get("/", response_class=HTMLResponse)
async def home(
    request: Request,
    user: Optional[BaseUser] = Depends(get_current_user)
):
    return router.templates.TemplateResponse(
        "home.html",
        {"request": request, "logged_in": user is not None, "user": user}
    )

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return router.templates.TemplateResponse("login.html", {"request": request})

@router.post("/login", response_class=HTMLResponse)
async def login_submit(request: Request, db: Session = Depends(get_session)):
    form = await request.form()
    try:
        form_data = OAuth2PasswordRequestForm(
            username=form.get("username"),
            password=form.get("password"),
            scope=""
        )
        
        user = UserService(db).verify_user(form_data.username, form_data.password)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        access_token = router.create_access_token(
            data={"sub": user.username, "user_id": str(user.user_id)},
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        
        response = RedirectResponse(url="/", status_code=303)
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
        return response
    except HTTPException as e:
        return router.templates.TemplateResponse(
            "login.html",
            {"request": request, "error": e.detail},
            status_code=e.status_code
        )

@router.get("/logout", response_class=HTMLResponse)
async def logout():
    response = RedirectResponse(url="/")
    response.delete_cookie("access_token")
    return response

@router.get("/balance", response_class=HTMLResponse)
async def balance_page(
    request: Request,
    user: Optional[BaseUser] = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    if not user:
        return RedirectResponse(url="/login")
    
    # Получаем баланс из базы данных
    balance_service = BalanceService(db)
    balance = balance_service.get_user_balance(user.user_id)
    
    return router.templates.TemplateResponse(
        "balance.html", 
        {
            "request": request, 
            "user": user,
            "balance": balance.amount  # Передаем реальный баланс
        }
    )

@router.get("/balance/history", response_class=HTMLResponse)
async def history_page(
    request: Request,
    user: Optional[BaseUser] = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    if not user:
        return RedirectResponse(url="/login")
    
    history_service = BalanceService(db)
    history = history_service.get_user_history(user.user_id)
    
    return router.templates.TemplateResponse(
        "history.html",
        {
            "request": request,
            "user": user,
            "history": history,
            "logged_in": True
        }
    )