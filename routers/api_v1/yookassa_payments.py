from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, Optional
import os

from dependencies import get_session

from services.auth import get_current_user, get_admin_user
from services.yookassa_service import YookassaService
from services.payments_service import PaymentService
from services.subscriptions_service import SubscriptionService

from config import YookassaConfig

from .schemas.payments_schemas import PaymentInput

from models.users import User

router = APIRouter(prefix="/yookassa", tags=["yookassa"])

# Инициализация сервиса Yookassa
yookassa_service = YookassaService(
    shop_id=YookassaConfig.SHOP_ID,
    secret_key=YookassaConfig.SECRET_KEY
)

@router.post("/create-payment")
async def create_payment(
    payment_data: PaymentInput,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """
    Создает платеж в Yookassa и возвращает ссылку на оплату
    """
    # Проверяем, что пользователь создает платеж для себя
    if payment_data.customer_id and payment_data.customer_id != str(current_user.id):
        raise HTTPException(status_code=403, detail="Вы можете создавать платежи только для своего аккаунта")
    
    # Инициализируем сервисы
    payment_service = PaymentService(session)
    subscription_service = SubscriptionService(session)
    yookassa_service.set_services(payment_service, subscription_service)
    
    # Формируем описание платежа
    description = f"Оплата подписки на AshleyVPN, тариф: {payment_data.tarrif_id}"
    
    # URL для возврата после оплаты
    return_url = os.getenv("PAYMENT_RETURN_URL", "https://ashleyvpn.com/payment/success")
    
    # Создаем платеж в Yookassa
    payment_result = await yookassa_service.create_payment(
        user_id=str(current_user.id),
        amount=float(payment_data.price),
        currency=payment_data.currency,
        subscription_plan_id=payment_data.tarrif_id,
        description=description,
        return_url=return_url
    )
    
    return {
        "payment_id": payment_result["payment_id"],
        "confirmation_url": payment_result["confirmation_url"],
        "status": payment_result["status"]
    }

@router.get("/payment/{payment_id}")
async def get_payment_status(
    payment_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """
    Получает статус платежа
    """
    payment_service = PaymentService(session)
    
    try:
        # Сначала пытаемся найти платеж по transaction_id
        payment = await payment_service.get_payment_by_transaction_id(payment_id)
        
        # Проверяем, что пользователь запрашивает свой платеж
        if payment.user_id != str(current_user.id):
            # Если не свой платеж, проверяем права администратора
            admin_user = await get_admin_user(current_user)
        
        return {
            "payment_id": payment.id,
            "transaction_id": payment.transaction_id,
            "status": payment.status,
            "amount": payment.amount,
            "currency": payment.currency.value if payment.currency else None
        }
    except HTTPException as e:
        if e.status_code == 404:
            # Если платеж не найден по transaction_id, пробуем найти по внутреннему ID
            try:
                payment = await payment_service.get_payment(payment_id)
                
                # Проверяем, что пользователь запрашивает свой платеж
                if payment.user_id != str(current_user.id):
                    # Если не свой платеж, проверяем права администратора
                    admin_user = await get_admin_user(current_user)
                
                return {
                    "payment_id": payment.id,
                    "transaction_id": payment.transaction_id,
                    "status": payment.status,
                    "amount": payment.amount,
                    "currency": payment.currency.value if payment.currency else None
                }
            except HTTPException:
                raise HTTPException(status_code=404, detail="Платеж не найден")
        else:
            raise e