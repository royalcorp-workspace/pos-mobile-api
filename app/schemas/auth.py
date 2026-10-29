from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict


class LoginRequest(BaseModel):
    identifier: str = Field(..., description="AN8 JDE Toko, Email, Username, atau No Telp")
    password: str = Field(..., min_length=4, description="Password akun toko")


class StoreContextOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    code: str
    name: str
    address_number: Optional[int] = None
    credit_limit: float = 0.0
    outstanding_balance: float = 0.0
    available_credit: float = 0.0
    payment_term: int = 0
    tier_name: Optional[str] = "Standard"
    phone: Optional[str] = None
    address: Optional[str] = None


class StoreUserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    email: str
    phone: Optional[str] = None
    username: Optional[str] = None
    user_type: str = "store"
    role_persona: Optional[str] = "store_owner"
    is_owner: bool = False
    store_id: Optional[UUID] = None


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in_minutes: int
    user: StoreUserOut
    store: Optional[StoreContextOut] = None
