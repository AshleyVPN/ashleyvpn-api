import enum
from .base import Base

from sqlalchemy import Enum, Integer, String,\
     Column, ForeignKey, Float, DateTime, Boolean, text
from sqlalchemy.dialects.postgresql import TIMESTAMP

from .subscription_plans import Currency

import uuid


class PaymentMethods(enum.Enum):
    RU_DEBIT_CARD = 'RU_DEBIT_CARD'
    SBP = 'SBP'
    SBERPAY = 'SBERPAY'
    YOOMONEY = 'YOOMONEY'


class PaymentKassa(enum.Enum):
    YOOKASSA = 'YOOKASSA'    


class Payment(Base):
    __tablename__ = 'payments'
    id = Column(String, primary_key=True, default=str(uuid.uuid4()))
    user_id = Column(String, ForeignKey('users.id'))
    amount = Column(Float)
    currency = Column(Enum(Currency))
    subscription_plan_id = Column(String, ForeignKey('subscription_plans.id'))
    payment_method = Column(Enum(PaymentMethods))
    payment_kassa = Column(Enum(PaymentKassa))
    last_update = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("CURRENT_TIMESTAMP"))
