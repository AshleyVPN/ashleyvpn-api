from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.subscriptions import Subscription, SubscriptionStatus
from typing import Optional, List
from datetime import datetime
import uuid
from repositories.abstract_subscriptions_repository import AbstractSubscriptionRepository

class SubscriptionRepository(AbstractSubscriptionRepository):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_subscription(self, customer_id: str, plan_id: str, invoice_id: str,
                          starts_at: datetime, ends_at: datetime,
                          status: SubscriptionStatus = SubscriptionStatus.INACTIVE) -> Subscription:
        subscription = Subscription(
            id=str(uuid.uuid4()),
            customer_id=customer_id,
            plan_id=plan_id,
            invoice_id=invoice_id,
            starts_at=starts_at,
            ends_at=ends_at,
            status=status
        )
        self.db.add(subscription)
        await self.db.commit()
        await self.db.refresh(subscription)
        return subscription

    async def get_subscription(self, subscription_id: str) -> Optional[Subscription]:
        result = await self.db.execute(select(Subscription).where(Subscription.id == subscription_id))
        return result.scalars().first()

    async def get_user_subscriptions(self, customer_id: str, active_only: bool = False) -> List[Subscription]:
        query = select(Subscription).where(Subscription.customer_id == customer_id)
        if active_only:
            query = query.where(Subscription.status == SubscriptionStatus.ACTIVE)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_plan_subscriptions(self, plan_id: str) -> List[Subscription]:
        result = await self.db.execute(select(Subscription).where(Subscription.plan_id == plan_id))
        return result.scalars().all()

    async def update_subscription(self, subscription_id: str, **kwargs) -> Optional[Subscription]:
        subscription = await self.get_subscription(subscription_id)
        if subscription:
            for key, value in kwargs.items():
                setattr(subscription, key, value)
            await self.db.commit()
            await self.db.refresh(subscription)
        return subscription

    async def delete_subscription(self, subscription_id: str) -> bool:
        subscription = await self.get_subscription(subscription_id)
        if subscription:
            subscription.deleted_at = datetime.utcnow()
            await self.db.commit()
            return True
        return False
    
    async def activate_subscription(self, subscription_id: str) -> Optional[Subscription]:
        return await self.update_subscription(subscription_id, status=SubscriptionStatus.ACTIVE)
    
    async def renew_subscription(self, subscription_id: str, new_subscription_id: str) -> Optional[Subscription]:
        return await self.update_subscription(
            subscription_id,
            renewed_at=datetime.utcnow(),
            renewed_subscription_id=new_subscription_id
        )
    
    async def upgrade_subscription(self, subscription_id: str, new_plan_id: str) -> Optional[Subscription]:
        return await self.update_subscription(
            subscription_id,
            upgraded_at=datetime.utcnow(),
            upgraded_to_plan_id=new_plan_id,
            status=SubscriptionStatus.UPGRADED
        )
    
    async def downgrade_subscription(self, subscription_id: str, new_plan_id: str) -> Optional[Subscription]:
        return await self.update_subscription(
            subscription_id,
            downgraded_at=datetime.utcnow(),
            downgraded_to_plan_id=new_plan_id
        )
    
    async def cancel_subscription(self, subscription_id: str) -> Optional[Subscription]:
        return await self.update_subscription(
            subscription_id,
            cancelled_at=datetime.utcnow()
        )
    
    async def get_active_subscription_for_user(self, customer_id: str) -> Optional[Subscription]:
        query = select(Subscription)\
            .where(Subscription.customer_id == customer_id)\
            .where(Subscription.status == SubscriptionStatus.ACTIVE)\
            .where(Subscription.ends_at > datetime.utcnow())
        result = await self.db.execute(query)
        return result.scalars().first()