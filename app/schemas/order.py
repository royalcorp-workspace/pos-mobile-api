from datetime import datetime
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict


class OrderItemCreate(BaseModel):
    product_id: UUID
    product_variant_id: Optional[UUID] = None
    sku: Optional[str] = None
    name: str
    quantity: int = Field(..., gt=0, description="Kuantitas item (minimal 1)")
    unit_price: float = Field(..., ge=0, description="Harga satuan")
    item_notes: Optional[str] = None


class OrderCreateRequest(BaseModel):
    payment_method: str = Field(..., description="Metode pembayaran: CASH, TRANSFER, atau CREDIT_LIMIT")
    customer_name: Optional[str] = Field("Pelanggan Toko (Walk-in)", description="Nama pelanggan")
    customer_phone: Optional[str] = Field(None, description="No telp pelanggan")
    customer_email: Optional[str] = Field(None, description="Email pelanggan")
    notes: Optional[str] = Field(None, description="Catatan pesanan POS")
    items: List[OrderItemCreate] = Field(..., min_length=1, description="Daftar item belanja")


class OrderItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    product_id: UUID
    product_variant_id: Optional[UUID] = None
    name: str
    quantity: int
    unit_price: float
    discount_nominal: float = 0.0
    discount_percent: float = 0.0
    total: float
    item_notes: Optional[str] = None


class OrderOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    order_number: str
    store_id: Optional[UUID] = None
    customer_name: Optional[str] = None
    customer_phone: Optional[str] = None
    payment_method: Optional[str] = None
    payment_status: int
    status: int
    subtotal: float
    discount: float
    tax: float
    total: float
    notes: Optional[str] = None
    created_at: Optional[datetime] = None
    items: List[OrderItemOut] = []


class OrderListResponse(BaseModel):
    items: List[OrderOut]
    total: int
    page: int
    limit: int
