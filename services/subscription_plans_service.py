from typing import Optional, List, Dict, Any
from fastapi import HTTPException
from sqlalchemy.orm import Session
from repositories.subscription_plans_repository import SubscriptionPlanRepository
from models.subscription_plans import SubscriptionPlan, Quota, Price, ResourceType

class SubscriptionPlanService:
    def __init__(self, db: Session):
        self.repository = SubscriptionPlanRepository(db)

    async def create_subscription_plan(self, name: str, description: str, billing_interval: int,
                                    is_active: bool = True, has_trial: bool = False,
                                    trial_discount: float = 0.0, transfer_plan_id: str = None) -> SubscriptionPlan:
        try:
            return self.repository.create_subscription_plan(
                name=name,
                description=description,
                billing_interval=billing_interval,
                is_active=is_active,
                has_trial=has_trial,
                trial_discount=trial_discount,
                transfer_plan_id=transfer_plan_id
            )
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    async def get_subscription_plan(self, plan_id: str) -> Optional[SubscriptionPlan]:
        plan = self.repository.get_subscription_plan(plan_id)
        if not plan:
            raise HTTPException(status_code=404, detail="Subscription plan not found")
        return plan

    async def get_all_subscription_plans(self, active_only: bool = False) -> List[SubscriptionPlan]:
        return self.repository.get_all_subscription_plans(active_only)

    async def update_subscription_plan(self, plan_id: str, **kwargs) -> SubscriptionPlan:
        plan = self.repository.update_subscription_plan(plan_id, **kwargs)
        if not plan:
            raise HTTPException(status_code=404, detail="Subscription plan not found")
        return plan

    async def delete_subscription_plan(self, plan_id: str) -> bool:
        if not self.repository.delete_subscription_plan(plan_id):
            raise HTTPException(status_code=404, detail="Subscription plan not found")
        return True
    
    # Методы для работы с квотами
    async def add_quota(self, plan_id: str, resource_type: ResourceType, limit: int, 
                      constraints: Dict[str, Any] = None) -> Quota:
        try:
            # Проверка существования плана подписки
            await self.get_subscription_plan(plan_id)
            
            return self.repository.add_quota(plan_id, resource_type, limit, constraints)
        except Exception as e:
            if isinstance(e, HTTPException):
                raise e
            raise HTTPException(status_code=400, detail=str(e))
    
    async def get_plan_quotas(self, plan_id: str) -> List[Quota]:
        # Проверка существования плана подписки
        await self.get_subscription_plan(plan_id)
        
        return self.repository.get_plan_quotas(plan_id)
    
    async def update_quota(self, quota_id: str, **kwargs) -> Optional[Quota]:
        quota = self.repository.update_quota(quota_id, **kwargs)
        if not quota:
            raise HTTPException(status_code=404, detail="Quota not found")
        return quota
    
    async def delete_quota(self, quota_id: str) -> bool:
        if not self.repository.delete_quota(quota_id):
            raise HTTPException(status_code=404, detail="Quota not found")
        return True
    
    # Методы для работы с ценами
    async def add_price(self, plan_id: str, amount: float, currency: str) -> Price:
        try:
            # Проверка существования плана подписки
            await self.get_subscription_plan(plan_id)
            
            return self.repository.add_price(plan_id, amount, currency)
        except Exception as e:
            if isinstance(e, HTTPException):
                raise e
            raise HTTPException(status_code=400, detail=str(e))
    
    async def get_plan_prices(self, plan_id: str) -> List[Price]:
        # Проверка существования плана подписки
        await self.get_subscription_plan(plan_id)
        
        return self.repository.get_plan_prices(plan_id)
    
    async def update_price(self, price_id: str, **kwargs) -> Optional[Price]:
        price = self.repository.update_price(price_id, **kwargs)
        if not price:
            raise HTTPException(status_code=404, detail="Price not found")
        return price
    
    async def delete_price(self, price_id: str) -> bool:
        if not self.repository.delete_price(price_id):
            raise HTTPException(status_code=404, detail="Price not found")
        return True