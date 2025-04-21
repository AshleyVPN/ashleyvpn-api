import enum
from .base import Base

from sqlalchemy import Enum, String,\
     Column, ForeignKey, text
from sqlalchemy.dialects.postgresql import TIMESTAMP, UUID

import uuid


class SubscriptionStatus(enum.Enum):
    INACTIVE = 'inactive'
    ACTIVE = 'active'
    UPGRADED = 'upgraded'


class Subscription(Base):
    __tablename__ = 'subscriptions'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    plan_id = Column(UUID(as_uuid=True), ForeignKey("subscription_plans.id"), nullable=False)
    invoice_id = Column(UUID(as_uuid=True), ForeignKey("payments.id"), nullable=False)
    starts_at = Column(TIMESTAMP(timezone=True))
    ends_at = Column(TIMESTAMP(timezone=True))
    renewed_at = Column(TIMESTAMP(timezone=True))
    renewed_subscription_id = Column(UUID(as_uuid=True), ForeignKey("subscriptions.id"), nullable=False)
    downgraded_at = Column(TIMESTAMP(timezone=True))
    downgraded_to_plan_id = Column(UUID(as_uuid=True), ForeignKey("subscription_plans.id"), nullable=False)
    upgraded_at = Column(TIMESTAMP(timezone=True))
    upgraded_to_plan_id = Column(UUID(as_uuid=True), ForeignKey("subscription_plans.id"), nullable=False)
    cancelled_at = Column(TIMESTAMP(timezone=True))
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    deleted_at = Column(TIMESTAMP(timezone=True))
    status = Column(Enum(SubscriptionStatus))
