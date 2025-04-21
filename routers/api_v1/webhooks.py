from fastapi import APIRouter, Depends, HTTPException, Request, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any
import os

from dependencies import get_session
from services.yookassa_service import YookassaService
from services.payments_service import PaymentService
from services.subscriptions_service import SubscriptionService

router = APIRouter(prefix="/webhooks", tags=["webhooks"])

# Инициализация сервиса Yookassa
yookassa_service = YookassaService(
    shop_id=os.getenv("YOOKASSA_SHOP_ID"),
    secret_key=os.getenv("YOOKASSA_SECRET_KEY")
)

@router.post("/yookassa")
async def yookassa_webhook(request: Request, background_tasks: BackgroundTasks, session: AsyncSession = Depends(get_session)):
    """
    Обработчик webhook от Yookassa
    """
    try:
        # Получаем данные из запроса
        event_data = await request.json()
        
        # Инициализируем сервисы
        payment_service = PaymentService(session)
        subscription_service = SubscriptionService(session)
        yookassa_service.set_services(payment_service, subscription_service)
        
        # Обрабатываем webhook в фоновом режиме
        background_tasks.add_task(yookassa_service.process_webhook, event_data)
        
        return {"status": "accepted"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Ошибка при обработке webhook: {str(e)}")