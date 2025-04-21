from typing import Optional, List
from fastapi import HTTPException
from sqlalchemy.orm import Session
from repositories.subscriptions_repository import SubscriptionRepository
from models.subscriptions import Subscription, SubscriptionStatus
from datetime import datetime

class SubscriptionService:
    def __init__(self, db: Session):
        self.repository = SubscriptionRepository(db)

    async def create_subscription(self, customer_id: str, plan_id: str, invoice_id: str,
                               starts_at: datetime, ends_at: datetime,
                               status: SubscriptionStatus = SubscriptionStatus.INACTIVE) -> Subscription:
        try:
            return self.repository.create_subscription(
                customer_id=customer_id,
                plan_id=plan_id,
                invoice_id=invoice_id,
                starts_at=starts_at,
                ends_at=ends_at,
                status=status
            )
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    async def get_subscription(self, subscription_id: str) -> Optional[Subscription]:
        subscription = self.repository.get_subscription(subscription_id)
        if not subscription:
            raise HTTPException(status_code=404, detail="Subscription not found")
        return subscription

    async def get_user_subscriptions(self, customer_id: str, active_only: bool = False) -> List[Subscription]:
        return self.repository.get_user_subscriptions(customer_id, active_only)

    async def get_plan_subscriptions(self, plan_id: str) -> List[Subscription]:
        return self.repository.get_plan_subscriptions(plan_id)

    async def update_subscription(self, subscription_id: str, **kwargs) -> Subscription:
        subscription = self.repository.update_subscription(subscription_id, **kwargs)
        if not subscription:
            raise HTTPException(status_code=404, detail="Subscription not found")
        return subscription

    async def delete_subscription(self, subscription_id: str) -> bool:
        if not self.repository.delete_subscription(subscription_id):
            raise HTTPException(status_code=404, detail="Subscription not found")
        return True
    
    async def activate_subscription(self, subscription_id: str) -> Subscription:
        subscription = self.repository.activate_subscription(subscription_id)
        if not subscription:
            raise HTTPException(status_code=404, detail="Subscription not found")
        return subscription
    
    async def renew_subscription(self, subscription_id: str, new_subscription_id: str) -> Subscription:
        subscription = self.repository.renew_subscription(subscription_id, new_subscription_id)
        if not subscription:
            raise HTTPException(status_code=404, detail="Subscription not found")
        return subscription
    
    async def upgrade_subscription(self, subscription_id: str, new_plan_id: str) -> Subscription:
        subscription = self.repository.upgrade_subscription(subscription_id, new_plan_id)
        if not subscription:
            raise HTTPException(status_code=404, detail="Subscription not found")
        return subscription
    
    async def downgrade_subscription(self, subscription_id: str, new_plan_id: str) -> Subscription:
        subscription = self.repository.downgrade_subscription(subscription_id, new_plan_id)
        if not subscription:
            raise HTTPException(status_code=404, detail="Subscription not found")
        return subscription
    
    async def cancel_subscription(self, subscription_id: str) -> Subscription:
        subscription = self.repository.cancel_subscription(subscription_id)
        if not subscription:
            raise HTTPException(status_code=404, detail="Subscription not found")
        return subscription
    
    async def get_active_subscription_for_user(self, customer_id: str) -> Optional[Subscription]:
        return self.repository.get_active_subscription_for_user(customer_id)