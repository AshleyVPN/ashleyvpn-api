from abc import ABC, abstractmethod
from typing import Optional, List
from datetime import datetime
from models.subscriptions import Subscription, SubscriptionStatus
from repositories.base_repository import BaseRepository

class AbstractSubscriptionRepository(BaseRepository, ABC):
    """
    Абстрактный класс для репозитория подписок.
    Определяет методы, которые должны быть реализованы в конкретных репозиториях подписок.
    """
    
    @abstractmethod
    async def create_subscription(self, customer_id: str, plan_id: str, invoice_id: str,
                          starts_at: datetime, ends_at: datetime,
                          status: SubscriptionStatus = SubscriptionStatus.INACTIVE) -> Subscription:
        pass

    @abstractmethod
    async def get_subscription(self, subscription_id: str) -> Optional[Subscription]:
        pass

    @abstractmethod
    async def get_user_subscriptions(self, customer_id: str, active_only: bool = False) -> List[Subscription]:
        pass

    @abstractmethod
    async def get_plan_subscriptions(self, plan_id: str) -> List[Subscription]:
        pass

    @abstractmethod
    async def update_subscription(self, subscription_id: str, **kwargs) -> Optional[Subscription]:
        pass

    @abstractmethod
    async def delete_subscription(self, subscription_id: str) -> bool:
        pass
    
    @abstractmethod
    async def activate_subscription(self, subscription_id: str) -> Optional[Subscription]:
        pass
    
    @abstractmethod
    async def renew_subscription(self, subscription_id: str, new_subscription_id: str) -> Optional[Subscription]:
        pass
    
    @abstractmethod
    async def upgrade_subscription(self, subscription_id: str, new_plan_id: str) -> Optional[Subscription]:
        pass
    
    @abstractmethod
    async def downgrade_subscription(self, subscription_id: str, new_plan_id: str) -> Optional[Subscription]:
        pass
    
    @abstractmethod
    async def cancel_subscription(self, subscription_id: str) -> Optional[Subscription]:
        pass
    
    @abstractmethod
    async def get_active_subscription_for_user(self, customer_id: str) -> Optional[Subscription]:
        pass