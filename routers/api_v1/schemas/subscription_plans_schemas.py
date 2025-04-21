from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from uuid import UUID
from enum import Enum
from datetime import datetime

class ResourceTypeEnum(str, Enum):
    LOCATIONS_COUNT = 'LOCATIONS_COUNT'
    PROTOCOLS_COUNT = 'PROTOCOLS_COUNT'

class BillingIntervalEnum(str, Enum):
    MONTH = 'MONTH'
    HALF_YEAR = 'HALF_YEAR'
    YEAR = 'YEAR'

class CurrencyEnum(str, Enum):
    RUB = 'RUB'
    USD = 'USD'
    EUR = 'EUR'

# Схемы для квот
class QuotaBase(BaseModel):
    resource_type: ResourceTypeEnum
    limit: int
    constraints: Optional[Dict[str, Any]] = Field(default_factory=dict)

class QuotaCreate(QuotaBase):
    pass

class QuotaResponse(QuotaBase):
    id: UUID
    subscription_plan_id: UUID

    class Config:
        from_attributes = True

# Схемы для цен
class PriceBase(BaseModel):
    amount: float
    currency: CurrencyEnum

class PriceCreate(PriceBase):
    pass

class PriceResponse(PriceBase):
    id: str
    subscription_plan_id: UUID

    class Config:
        from_attributes = True

# Схемы для планов подписки
class SubscriptionPlanBase(BaseModel):
    name: str
    description: str
    billing_interval: int
    is_active: bool = True
    has_trial: bool = False
    trial_discount: Optional[float] = 0.0
    transfer_plan_id: Optional[str] = None

class SubscriptionPlanCreate(SubscriptionPlanBase):
    quotas: Optional[List[QuotaCreate]] = None
    prices: Optional[List[PriceCreate]] = None

class SubscriptionPlanUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    has_trial: Optional[bool] = None
    trial_discount: Optional[float] = None
    transfer_plan_id: Optional[str] = None

class SubscriptionPlanResponse(SubscriptionPlanBase):
    id: UUID
    name: str
    description: str
    has_trial: bool
    trial_discount: float
    quotas: List[QuotaResponse] = []
    prices: List[PriceResponse] = []

    class Config:
        from_attributes = True