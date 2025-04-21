from typing import Optional, Dict, Any
from yookassa import Configuration, Payment as YooKassaPayment
from fastapi import HTTPException
from uuid import uuid4
from datetime import datetime, timedelta

from models.payments import Payment, PaymentMethod, PaymentMethods, PaymentKassa
from models.subscriptions import Subscription, SubscriptionStatus
from services.subscriptions_service import SubscriptionService
from services.payments_service import PaymentService


class YookassaService:
    def __init__(self, shop_id: str, secret_key: str):
        Configuration.account_id = shop_id
        Configuration.secret_key = secret_key
        self.payment_service = None
        self.subscription_service = None
    
    def set_services(self, payment_service: PaymentService, subscription_service: SubscriptionService):
        self.payment_service = payment_service
        self.subscription_service = subscription_service
    
    async def create_payment(self, user_id: str, amount: float, currency: str, 
                           subscription_plan_id: str, description: str, 
                           return_url: str) -> Dict[str, Any]:
        """
        Создает платеж в Yookassa и возвращает данные для оплаты
        """
        idempotence_key = str(uuid4())
        
        payment_data = {
            "amount": {
                "value": str(amount),
                "currency": currency
            },
            "confirmation": {
                "type": "redirect",
                "return_url": return_url
            },
            "capture": True,
            "description": description,
            "metadata": {
                "user_id": user_id,
                "subscription_plan_id": subscription_plan_id
            }
        }
        
        try:
            # Создаем платеж в Yookassa
            yookassa_payment = YooKassaPayment.create(payment_data, idempotence_key)
            
            # Сохраняем платеж в нашей базе данных
            if self.payment_service:
                await self.payment_service.create_payment(
                    user_id=user_id,
                    amount=amount,
                    currency=currency,
                    subscription_plan_id=subscription_plan_id,
                    payment_method=PaymentMethods.RU_DEBIT_CARD.value,  # По умолчанию, будет обновлено после оплаты
                    payment_kassa=PaymentKassa.YOOKASSA.value,
                    transaction_id=yookassa_payment.id,
                    status=yookassa_payment.status,
                    metadata={
                        "yookassa_id": yookassa_payment.id,
                        "confirmation_url": yookassa_payment.confirmation.confirmation_url
                    }
                )
            
            return {
                "payment_id": yookassa_payment.id,
                "confirmation_url": yookassa_payment.confirmation.confirmation_url,
                "status": yookassa_payment.status
            }
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Ошибка при создании платежа: {str(e)}")
    
    async def process_webhook(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Обрабатывает webhook от Yookassa
        """
        try:
            event_type = event_data.get("event")
            payment_data = event_data.get("object")
            
            if not event_type or not payment_data:
                raise HTTPException(status_code=400, detail="Некорректные данные webhook")
            
            payment_id = payment_data.get("id")
            status = payment_data.get("status")
            metadata = payment_data.get("metadata", {})
            
            # Получаем данные из метаданных
            user_id = metadata.get("user_id")
            subscription_plan_id = metadata.get("subscription_plan_id")
            
            if not payment_id or not user_id or not subscription_plan_id:
                raise HTTPException(status_code=400, detail="Отсутствуют необходимые данные в метаданных")
            
            # Обновляем статус платежа в нашей базе данных
            if self.payment_service:
                payment = await self.payment_service.get_payment_by_transaction_id(payment_id)
                if payment:
                    # Обновляем статус платежа
                    await self.payment_service.update_payment(
                        payment.id,
                        status=status
                    )
                    
                    # Если платеж успешен, создаем или продлеваем подписку
                    if status == "succeeded" and self.subscription_service:
                        # Сохраняем метод оплаты для автосписаний
                        payment_method_id = payment_data.get("payment_method", {}).get("id")
                        if payment_method_id:
                            await self.payment_service.add_payment_method(
                                user_id=user_id,
                                method_name=payment_data.get("payment_method", {}).get("type", "card"),
                                method_id=payment_method_id
                            )
                        
                        # Проверяем, есть ли активная подписка у пользователя
                        active_subscription = await self.subscription_service.get_active_subscription_for_user(user_id)
                        
                        if active_subscription:
                            # Продлеваем существующую подписку
                            new_ends_at = active_subscription.ends_at + timedelta(days=30)  # Предполагаем месячную подписку
                            await self.subscription_service.update_subscription(
                                active_subscription.id,
                                ends_at=new_ends_at
                            )
                        else:
                            # Создаем новую подписку
                            now = datetime.now()
                            await self.subscription_service.create_subscription(
                                customer_id=user_id,
                                plan_id=subscription_plan_id,
                                invoice_id=payment.id,
                                starts_at=now,
                                ends_at=now + timedelta(days=30),  # Предполагаем месячную подписку
                                status=SubscriptionStatus.ACTIVE
                            )
            
            return {"status": "success", "message": f"Webhook обработан успешно: {event_type}"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Ошибка при обработке webhook: {str(e)}")