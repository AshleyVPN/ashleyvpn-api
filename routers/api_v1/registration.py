from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import os

from dependencies import get_session
from services.users_service import UserService
from services.email_service import EmailService
from .schemas.users_schemas import UserCreate, UserResponse
from .schemas.auth_schemas import Token
from services.auth import create_access_token, create_refresh_token
from datetime import timedelta
from config import AuthConfig

router = APIRouter(prefix="/registration", tags=["registration"])

# Инициализация сервиса для отправки email
email_service = EmailService(
    smtp_server=os.getenv("SMTP_SERVER"),
    smtp_port=int(os.getenv("SMTP_PORT", "587")),
    smtp_username=os.getenv("SMTP_USERNAME"),
    smtp_password=os.getenv("SMTP_PASSWORD"),
    from_email=os.getenv("SMTP_FROM_EMAIL"),
    verification_url=os.getenv("EMAIL_VERIFICATION_URL")
)

@router.post("/email", response_model=UserResponse)
async def register_with_email(user_data: UserCreate, background_tasks: BackgroundTasks, session: AsyncSession = Depends(get_session)):
    """
    Регистрация пользователя через email с отправкой ссылки для подтверждения
    """
    if not user_data.email:
        raise HTTPException(status_code=400, detail="Email обязателен для этого метода регистрации")
    
    if not user_data.password:
        raise HTTPException(status_code=400, detail="Пароль обязателен для этого метода регистрации")
    
    user_service = UserService(session)
    
    # Создаем пользователя
    user = await user_service.create_user(
        username=user_data.username,
        email=user_data.email,
        password=user_data.password,
        is_admin=user_data.is_admin
    )
    
    # Отправляем email для подтверждения в фоновом режиме
    background_tasks.add_task(
        email_service.send_verification_email,
        str(user.id),
        user.email
    )
    
    return user

@router.post("/telegram", response_model=UserResponse)
async def register_with_telegram(user_data: UserCreate, session: AsyncSession = Depends(get_session)):
    """
    Регистрация пользователя через Telegram
    """
    if not user_data.telegram_id:
        raise HTTPException(status_code=400, detail="Telegram ID обязателен для этого метода регистрации")
    
    user_service = UserService(session)
    
    # Создаем пользователя
    user = await user_service.create_user(
        username=user_data.username,
        email=user_data.email,
        telegram_id=user_data.telegram_id,
        password=user_data.password,
        is_admin=user_data.is_admin
    )
    
    return user

@router.get("/verify-email")
async def verify_email(token: str = Query(...), session: AsyncSession = Depends(get_session)):
    """
    Подтверждение email по токену из письма
    """
    user_id = email_service.verify_token(token)
    
    if not user_id:
        raise HTTPException(status_code=400, detail="Недействительный или истекший токен")
    
    user_service = UserService(session)
    user = await user_service.get_user(user_id)
    
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    
    # Обновляем статус подтверждения email
    await user_service.update_user(user_id, email_verified=True)
    
    return {"message": "Email успешно подтвержден"}

@router.post("/resend-verification", response_model=dict)
async def resend_verification_email(email: str, background_tasks: BackgroundTasks, session: AsyncSession = Depends(get_session)):
    """
    Повторная отправка письма для подтверждения email
    """
    user_service = UserService(session)
    
    try:
        user = await user_service.get_user_by_email(email)
    except HTTPException:
        # Не сообщаем, что пользователь не существует, чтобы избежать утечки информации
        return {"message": "Если указанный email зарегистрирован, письмо с инструкциями было отправлено"}
    
    # Отправляем email для подтверждения в фоновом режиме
    background_tasks.add_task(
        email_service.send_verification_email,
        str(user.id),
        user.email
    )
    
    return {"message": "Письмо с инструкциями отправлено"}