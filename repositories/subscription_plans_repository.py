from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.subscription_plans import SubscriptionPlan, Quota, Price, ResourceType
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid
from repositories.abstract_subscription_plans_repository import AbstractSubscriptionPlanRepository

class SubscriptionPlanRepository(AbstractSubscriptionPlanRepository):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_subscription_plan(self, name: str, description: str, billing_interval: int,
                               is_active: bool = True, has_trial: bool = False,
                               trial_discount: float = 0.0, transfer_plan_id: str = None) -> SubscriptionPlan:
        subscription_plan = SubscriptionPlan(
            name=name,
            description=description,
            billing_interval=billing_interval,
            is_active=is_active,
            has_trial=has_trial,
            trial_discount=trial_discount,
            transfer_plan_id=transfer_plan_id
        )
        self.db.add(subscription_plan)
        await self.db.commit()
        await self.db.refresh(subscription_plan)
        return subscription_plan

    async def get_subscription_plan(self, plan_id: str) -> Optional[SubscriptionPlan]:
        result = await self.db.execute(select(SubscriptionPlan).where(SubscriptionPlan.id == plan_id))
        return result.scalars().first()

    async def get_all_subscription_plans(self, active_only: bool = False) -> List[SubscriptionPlan]:
        query = select(SubscriptionPlan)
        if active_only:
            query = query.where(SubscriptionPlan.is_active == True)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def update_subscription_plan(self, plan_id: str, **kwargs) -> Optional[SubscriptionPlan]:
        plan = await self.get_subscription_plan(plan_id)
        if plan:
            for key, value in kwargs.items():
                setattr(plan, key, value)
            plan.updated_at = datetime.utcnow()
            await self.db.commit()
            await self.db.refresh(plan)
        return plan

    async def delete_subscription_plan(self, plan_id: str) -> bool:
        plan = await self.get_subscription_plan(plan_id)
        if plan:
            await self.db.delete(plan)
            await self.db.commit()
            return True
        return False
    
    # Методы для работы с квотами
    async def add_quota(self, plan_id: str, resource_type: ResourceType, limit: int, 
                 constraints: Dict[str, Any] = None) -> Quota:
        quota = Quota(
            subscription_plan_id=plan_id,
            resource_type=resource_type,
            limit=limit,
            constraints=constraints or {}
        )
        self.db.add(quota)
        await self.db.commit()
        await self.db.refresh(quota)
        return quota
    
    async def get_plan_quotas(self, plan_id: str) -> List[Quota]:
        result = await self.db.execute(select(Quota).where(Quota.subscription_plan_id == plan_id))
        return result.scalars().all()
    
    async def update_quota(self, quota_id: str, **kwargs) -> Optional[Quota]:
        result = await self.db.execute(select(Quota).where(Quota.id == quota_id))
        quota = result.scalars().first()
        if quota:
            for key, value in kwargs.items():
                setattr(quota, key, value)
            await self.db.commit()
            await self.db.refresh(quota)
        return quota
    
    async def delete_quota(self, quota_id: str) -> bool:
        result = await self.db.execute(select(Quota).where(Quota.id == quota_id))
        quota = result.scalars().first()
        if quota:
            await self.db.delete(quota)
            await self.db.commit()
            return True
        return False
    
    # Методы для работы с ценами
    async def add_price(self, plan_id: str, amount: float, currency: str) -> Price:
        price = Price(
            subscription_plan_id=plan_id,
            amount=amount,
            currency=currency
        )
        self.db.add(price)
        await self.db.commit()
        await self.db.refresh(price)
        return price
    
    async def get_plan_prices(self, plan_id: str) -> List[Price]:
        result = await self.db.execute(select(Price).where(Price.subscription_plan_id == plan_id))
        return result.scalars().all()
    
    async def update_price(self, price_id: str, **kwargs) -> Optional[Price]:
        result = await self.db.execute(select(Price).where(Price.id == price_id))
        price = result.scalars().first()
        if price:
            for key, value in kwargs.items():
                setattr(price, key, value)
            await self.db.commit()
            await self.db.refresh(price)
        return price
    
    async def delete_price(self, price_id: str) -> bool:
        result = await self.db.execute(select(Price).where(Price.id == price_id))
        price = result.scalars().first()
        if price:
            await self.db.delete(price)
            await self.db.commit()
            return True
        return False