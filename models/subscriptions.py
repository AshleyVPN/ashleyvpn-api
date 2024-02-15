import enum
from .base import Base

from sqlalchemy import Enum, String,\
     Column, ForeignKey, text
from sqlalchemy.dialects.postgresql import TIMESTAMP

import uuid


class SubscriptionStatus(enum.Enum):
    INACTIVE = 'inactive'
    ACTIVE = 'active'
    UPGRADED = 'upgraded'


class Subscription(Base):
    __tablename__ = 'subscriptions'
    id = Column(String, primary_key=True, default=str(uuid.uuid4()))
    customer_id = Column(String, ForeignKey('users.id'), nullable=False)
    plan_id = Column(String, ForeignKey('subscription_plans.id'), nullable=False)
    invoice_id = Column(String, ForeignKey('invoices.id'), nullable=False)
    starts_at = Column(TIMESTAMP(timezone=True))
    ends_at = Column(TIMESTAMP(timezone=True))
    renewed_at = Column(TIMESTAMP(timezone=True))
    renewed_subscription_id = Column(String, ForeignKey('subscriptions.id'))
    downgraded_at = Column(TIMESTAMP(timezone=True))
    downgraded_to_plan_id = Column(String, ForeignKey('subscription_plans.id'))
    upgraded_at = Column(TIMESTAMP(timezone=True))
    upgraded_to_plan_id = Column(String, ForeignKey('subscription_plans.id'))
    cancelled_at = Column(TIMESTAMP(timezone=True))
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    deleted_at = Column(TIMESTAMP(timezone=True))
    status = Column(Enum(SubscriptionStatus))
