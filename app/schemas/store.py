from typing import Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict


class StoreTierOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    code: str
    name: str
    level: int = 1


class StoreProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    code: str
    name: str
    address_number: Optional[int] = None
    credit_limit: float
    outstanding_balance: float
    available_credit: float
    payment_term: int
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    status: bool
    tier: Optional[StoreTierOut] = None


class CreditCeilingResponse(BaseModel):
    store_id: UUID
    store_name: str
    address_number: Optional[int] = None
    credit_limit: float
    outstanding_balance: float
    available_credit: float
    payment_term_days: int
    can_place_order: bool
    max_order_amount_allowed: float
