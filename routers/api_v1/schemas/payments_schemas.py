from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field


class PaymentCreate(BaseModel):
    user_id: str


class PaymentInput(BaseModel):
    price: str
    currency: str
    it_first_pay: bool
    tarrif_id: str
    paid_up_to: datetime
    autopay: bool
    payment_method: str = Field(description="Payment method (e.g. card, crypto)")
    status: str = Field(description="Payment status")
    transaction_id: Optional[str] = Field(default=None, description="External payment transaction ID")
    metadata: Optional[dict] = Field(default=None, description="Additional payment metadata")
    customer_id: Optional[str] = Field(default=None)
    customer_email: Optional[str] = Field(default=None)


class PaymentResponse(BaseModel):
    id: str
    user_id: str
    price: str
    currency: str
    it_first_pay: bool
    tarrif_id: str
    paid_up_to: datetime
    autopay: bool
    payment_method: str
    status: str
    transaction_id: Optional[str]
    metadata: Optional[dict]

class PaymentMethodResponse(BaseModel):
    id: str
    method_name: str
    method_id: str