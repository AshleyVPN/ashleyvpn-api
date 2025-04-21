from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.payments import Payment, PaymentMethod
from typing import Optional, List, Dict, Any
from datetime import datetime
import json

from repositories.abstract_payments_repository import AbstractPaymentRepository

class PaymentRepository(AbstractPaymentRepository):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_payment(self, user_id: str, amount: float, currency: str,
                      subscription_plan_id: str, payment_method: str,
                      payment_kassa: str, transaction_id: Optional[str] = None,
                      status: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None) -> Payment:
        payment = Payment(
            user_id=user_id,
            amount=amount,
            currency=currency,
            subscription_plan_id=subscription_plan_id,
            payment_method=payment_method,
            payment_kassa=payment_kassa,
            transaction_id=transaction_id,
            status=status,
            payment_metadata=json.dumps(metadata) if metadata else None
        )
        self.db.add(payment)
        await self.db.commit()
        await self.db.refresh(payment)
        return payment

    async def get_payment(self, payment_id: str) -> Optional[Payment]:
        result = await self.db.execute(select(Payment).where(Payment.id == payment_id))
        return result.scalars().first()

    async def get_user_payments(self, user_id: str) -> List[Payment]:
        result = await self.db.execute(select(Payment).where(Payment.user_id == user_id))
        return result.scalars().all()

    async def update_payment(self, payment_id: str, **kwargs) -> Optional[Payment]:
        payment = await self.get_payment(payment_id)
        if payment:
            for key, value in kwargs.items():
                setattr(payment, key, value)
            payment.last_update = datetime.utcnow()
            await self.db.commit()
            await self.db.refresh(payment)
        return payment

    async def delete_payment(self, payment_id: str) -> bool:
        payment = await self.get_payment(payment_id)
        if payment:
            await self.db.delete(payment)
            await self.db.commit()
            return True
        return False

    async def get_user_payment_methods(self, user_id: str) -> List[PaymentMethod]:
        result = await self.db.execute(select(PaymentMethod).where(PaymentMethod.user == user_id))
        return result.scalars().all()

    async def add_payment_method(self, user_id: str, method_name: str, method_id: str) -> PaymentMethod:
        payment_method = PaymentMethod(
            user=user_id,
            method_name=method_name,
            method_id=method_id
        )
        self.db.add(payment_method)
        await self.db.commit()
        await self.db.refresh(payment_method)
        return payment_method
        
    async def get_payment_by_transaction_id(self, transaction_id: str) -> Optional[Payment]:
        result = await self.db.execute(select(Payment).where(Payment.transaction_id == transaction_id))
        return result.scalars().first()