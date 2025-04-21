from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from models.payments import Payment, PaymentMethod
from repositories.base_repository import BaseRepository

class AbstractPaymentRepository(BaseRepository, ABC):
    """
    Абстрактный класс для репозитория платежей.
    Определяет методы, которые должны быть реализованы в конкретных репозиториях платежей.
    """
    
    @abstractmethod
    async def create_payment(self, user_id: str, amount: float, currency: str,
                      subscription_plan_id: str, payment_method: str,
                      payment_kassa: str, transaction_id: Optional[str] = None,
                      status: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None) -> Payment:
        pass

    @abstractmethod
    async def get_payment(self, payment_id: str) -> Optional[Payment]:
        pass

    @abstractmethod
    async def get_user_payments(self, user_id: str) -> List[Payment]:
        pass

    @abstractmethod
    async def update_payment(self, payment_id: str, **kwargs) -> Optional[Payment]:
        pass

    @abstractmethod
    async def delete_payment(self, payment_id: str) -> bool:
        pass

    @abstractmethod
    async def get_user_payment_methods(self, user_id: str) -> List[PaymentMethod]:
        pass

    @abstractmethod
    async def add_payment_method(self, user_id: str, method_name: str, method_id: str) -> PaymentMethod:
        pass
        
    @abstractmethod
    async def get_payment_by_transaction_id(self, transaction_id: str) -> Optional[Payment]:
        pass