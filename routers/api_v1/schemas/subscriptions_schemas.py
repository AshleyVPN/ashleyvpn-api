from typing import Optional, List
from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from enum import Enum

class SubscriptionStatusEnum(str, Enum):
    INACTIVE = 'inactive'
    ACTIVE = 'active'
    UPGRADED = 'upgraded'

class SubscriptionBase(BaseModel):
    customer_id: str
    plan_id: str
    invoice_id: str
    starts_at: datetime
    ends_at: datetime
    status: SubscriptionStatusEnum = SubscriptionStatusEnum.INACTIVE

class SubscriptionCreate(SubscriptionBase):
    pass

class SubscriptionUpdate(BaseModel):
    renewed_at: Optional[datetime] = None
    renewed_subscription_id: Optional[str] = None
    downgraded_at: Optional[datetime] = None
    downgraded_to_plan_id: Optional[str] = None
    upgraded_at: Optional[datetime] = None
    upgraded_to_plan_id: Optional[str] = None
    cancelled_at: Optional[datetime] = None
    status: Optional[SubscriptionStatusEnum] = None

class SubscriptionResponse(SubscriptionBase):
    id: str
    renewed_at: Optional[datetime] = None
    renewed_subscription_id: Optional[str] = None
    downgraded_at: Optional[datetime] = None
    downgraded_to_plan_id: Optional[str] = None
    upgraded_at: Optional[datetime] = None
    upgraded_to_plan_id: Optional[str] = None
    cancelled_at: Optional[datetime] = None
    created_at: datetime
    deleted_at: Optional[datetime] = None

    class Config:
        from_attributes = True