from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from models.subscription_plans import SubscriptionPlan, Quota, Price, ResourceType
from repositories.base_repository import BaseRepository

class AbstractSubscriptionPlanRepository(BaseRepository, ABC):
    """
    Абстрактный класс для репозитория планов подписок.
    Определяет методы, которые должны быть реализованы в конкретных репозиториях планов подписок.
    """
    
    @abstractmethod
    async def create_subscription_plan(self, name: str, description: str, billing_interval: int,
                               is_active: bool = True, has_trial: bool = False,
                               trial_discount: float = 0.0, transfer_plan_id: str = None) -> SubscriptionPlan:
        pass

    @abstractmethod
    async def get_subscription_plan(self, plan_id: str) -> Optional[SubscriptionPlan]:
        pass

    @abstractmethod
    async def get_all_subscription_plans(self, active_only: bool = False) -> List[SubscriptionPlan]:
        pass

    @abstractmethod
    async def update_subscription_plan(self, plan_id: str, **kwargs) -> Optional[SubscriptionPlan]:
        pass

    @abstractmethod
    async def delete_subscription_plan(self, plan_id: str) -> bool:
        pass
    
    # Методы для работы с квотами
    @abstractmethod
    async def add_quota(self, plan_id: str, resource_type: ResourceType, limit: int, 
                 constraints: Dict[str, Any] = None) -> Quota:
        pass
    
    @abstractmethod
    async def get_plan_quotas(self, plan_id: str) -> List[Quota]:
        pass
    
    @abstractmethod
    async def update_quota(self, quota_id: str, **kwargs) -> Optional[Quota]:
        pass
    
    @abstractmethod
    async def delete_quota(self, quota_id: str) -> bool:
        pass
    
    # Методы для работы с ценами
    @abstractmethod
    async def add_price(self, plan_id: str, amount: float, currency: str) -> Price:
        pass
    
    @abstractmethod
    async def get_plan_prices(self, plan_id: str) -> List[Price]:
        pass
    
    @abstractmethod
    async def update_price(self, price_id: str, **kwargs) -> Optional[Price]:
        pass
    
    @abstractmethod
    async def delete_price(self, price_id: str) -> bool:
        pass