from typing import Optional, List, Dict, Any
from fastapi import HTTPException
from sqlalchemy.orm import Session
from repositories.payments_repository import PaymentRepository
from models.payments import Payment, PaymentMethod

class PaymentService:
    def __init__(self, db: Session):
        self.repository = PaymentRepository(db)

    async def create_payment(self, user_id: str, amount: float, currency: str,
                           subscription_plan_id: str, payment_method: str,
                           payment_kassa: str, transaction_id: Optional[str] = None,
                           status: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None) -> Payment:
        try:
            return self.repository.create_payment(
                user_id=user_id,
                amount=amount,
                currency=currency,
                subscription_plan_id=subscription_plan_id,
                payment_method=payment_method,
                payment_kassa=payment_kassa,
                transaction_id=transaction_id,
                status=status,
                metadata=metadata
            )
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    async def get_payment(self, payment_id: str) -> Optional[Payment]:
        payment = self.repository.get_payment(payment_id)
        if not payment:
            raise HTTPException(status_code=404, detail="Payment not found")
        return payment

    async def get_user_payments(self, user_id: str) -> List[Payment]:
        return self.repository.get_user_payments(user_id)

    async def update_payment(self, payment_id: str, **kwargs) -> Payment:
        payment = self.repository.update_payment(payment_id, **kwargs)
        if not payment:
            raise HTTPException(status_code=404, detail="Payment not found")
        return payment

    async def delete_payment(self, payment_id: str) -> bool:
        if not self.repository.delete_payment(payment_id):
            raise HTTPException(status_code=404, detail="Payment not found")
        return True

    async def get_user_payment_methods(self, user_id: str) -> List[PaymentMethod]:
        return self.repository.get_user_payment_methods(user_id)

    async def add_payment_method(self, user_id: str, method_name: str, method_id: str) -> PaymentMethod:
        try:
            return self.repository.add_payment_method(
                user_id=user_id,
                method_name=method_name,
                method_id=method_id
            )
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))
            
    async def get_payment_by_transaction_id(self, transaction_id: str) -> Optional[Payment]:
        payment = self.repository.get_payment_by_transaction_id(transaction_id)
        if not payment:
            raise HTTPException(status_code=404, detail="Payment not found")
        return payment