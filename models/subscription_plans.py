import enum
from .base import Base

from datetime import datetime

from sqlalchemy import Enum, Integer, String,\
     Column, ForeignKey, Float, Numeric, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

import uuid


class Currency(enum.Enum):
    RUB = 'RUB'
    USD = 'USD'
    EUR = 'EUR'


class BillingInterval(enum.Enum):
    MONTH = 'MONTH'
    HALF_YEAR = 'HALF_YEAR'
    YEAR = 'YEAR'


class BaseResource():
     maped_constarints = {}
     limit = None

     def map_constarints(self, constarints):
          self.maped_constarints = constarints


class LocationsCountResource(BaseResource):
     def __init__(self):
          self.type_ = ResourceType.LOCATIONS_COUNT
          self.constarints = [
               'CAN_CHOOSE', 'SELECTION_BY_POPULARITY'
          ]
     
     def is_can_choose(self):
          return self.maped_constarints['CAN_CHOOSE']


class ProtocolsCountResource(BaseResource):
     def __init__(self):
          self.type_ = ResourceType.PROTOCOLS_COUNT
          self.constarints = [
               'SIMULTANEOUS_USE', 'USE_VLESS', 'USE_OUTLINE', 'USE_WIREGUARD'
          ]

     def get_available_protocols(self):
          protocols = []

          if self.maped_constarints['USE_VLESS']:
               protocols.append('vless')
          
          if self.maped_constarints['USE_OUTLINE']:
               protocols.append('outline')
          
          if self.maped_constarints['USE_WIREGUARD']:
               protocols.append('wg')

          return protocols
     
     def can_use_same_time(self):
          return self.maped_constarints['SIMULTANEOUS_USE']


class ResourceType(enum.Enum):
    LOCATIONS_COUNT = 'LOCATIONS_COUNT'
    PROTOCOLS_COUNT = 'PROTOCOLS_COUNT'


resources = {
     ResourceType.LOCATIONS_COUNT: LocationsCountResource,
     ResourceType.PROTOCOLS_COUNT: ProtocolsCountResource,
}


class SubscriptionPlan(Base):
    __tablename__ = 'subscription_plans'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String)
    description = Column(String)
    billing_interval = Column(Integer)
    is_active = Column(Boolean, default=True)
    has_trial = Column(Boolean, default=False)
    quotas = relationship("Quota")
    prices = relationship("Price")
    trial_discount = Column(Float, default=0.0, nullable=True)

    transfer_plan_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    transfer_plan = relationship("User")
    
    created_at = Column(String, default=datetime.utcnow)
    updated_at = Column(String, default=datetime.utcnow, onupdate=datetime.utcnow)

    async def get_quota(self, resource_type):
          quota = next((q for q in self.quotas if q.resource_type == resource_type), None)
          resource = resources[resource_type]()

          if quota and resource:
               resource.limit = quota.limit
               resource.map_constarints(quota.map_constarints(resource.constarints))
               return resource

          return None
    

class Quota(Base):
    __tablename__ = 'quotas'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    subscription_plan_id = Column(UUID(as_uuid=True), ForeignKey("subscription_plans.id"), nullable=False)
    resource_type = Column(Enum(Currency))
    limit = Column(Integer, nullable=True)


class Price(Base):
    __tablename__ = 'prices'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    subscription_plan_id = Column(UUID(as_uuid=True), ForeignKey("subscription_plans.id"), nullable=False)
    amount = Column(Float)
    currency = Column(Enum(Currency))
    interval = Column(Enum(BillingInterval))

