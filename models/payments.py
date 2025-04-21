import enum
from .base import Base

from sqlalchemy import Enum, Integer, String,\
     Column, ForeignKey, Float, DateTime, Boolean, text
from sqlalchemy.dialects.postgresql import TIMESTAMP, UUID

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
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(ForeignKey('users.id'))
    amount = Column(Float)
    currency = Column(Enum(Currency))
    subscription_plan_id = Column(UUID(as_uuid=True), ForeignKey("subscription_plans.id"), nullable=False)
    payment_method = Column(Enum(PaymentMethods))
    payment_kassa = Column(Enum(PaymentKassa))
    transaction_id = Column(String, unique=True, nullable=True)  # ID транзакции в платежной системе
    status = Column(String, nullable=True)  # Статус платежа
    payment_metadata = Column(String, nullable=True)  # Метаданные платежа в формате JSON
    last_update = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("CURRENT_TIMESTAMP"))

class PaymentMethod(Base):
    __tablename__ = 'payment_methods'
    id = Column(Integer, primary_key=True, autoincrement=True)
    method_name = Column(String)
    method_id = Column(String)
    user = Column(ForeignKey("users.id"))
