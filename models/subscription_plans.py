import enum
from .base import Base

from datetime import datetime
from sqlalchemy import Enum, Integer, String,\
     Column, ForeignKey, Float, DateTime, Boolean
from sqlalchemy.orm import relationship

import uuid


class Currency(enum.Enum):
    RUB = 'RUB'
    USD = 'USD'
    EUR = 'EUR'


class ResourceType(enum.Enum):
    LOCATIONS_COUNT = 'LOCATIONS_COUNT'
    PROTOCOLS_COUNT = 'PROTOCOLS_COUNT'


class SubscriptionPlan(Base):
    __tablename__ = 'subscription_plans'
    id = Column(String, primary_key=True, default=str(uuid.uuid4()))
    name = Column(String)
    description = Column(String)
    billing_interval = Column(Integer)
    is_active = Column(Boolean, default=True)
    has_trial = Column(Boolean, default=False)
    quotas = relationship("Quota", back_populates="subscription_plans")
    prices = relationship("Price", back_populates="subscription_plans")
    discount = Column(Float)
    

class Quota(Base):
    __tablename__ = 'quotas'
    id = Column(String, primary_key=True, default=str(uuid.uuid4()))
    subscription_plan_id = Column(String, ForeignKey('subscription_plans.id'))
    resource_type = Column(Enum(Currency))
    limit = Column(Integer, nullable=True)


class Price(Base):
    __tablename__ = 'prices'
    id = Column(String, primary_key=True, default=str(uuid.uuid4()))
    subscription_plan_id = Column(String, ForeignKey('subscription_plans.id'))
    amount = Column(Float)
    currency = Column(Enum(Currency))
