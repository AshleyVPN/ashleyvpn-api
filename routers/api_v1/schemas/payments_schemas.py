from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field


class PaymentCreate(BaseModel):
    user_id: str


class PaymentSave(BaseModel):
    promocode: str
    tariff_id: str
    payment_method: str

