from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict


class ProductOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    product_id: Optional[UUID] = None
    product_variant_id: Optional[UUID] = None
    sku: str
    name: str
    item_size: Optional[str] = None
    brand_name: Optional[str] = None
    category_name: Optional[str] = None
    base_price: float = 0.0
    suggested_retail_price: Optional[float] = None
    custom_retail_price: Optional[float] = None
    effective_price: float = 0.0
    is_floor_display: bool = False
    is_active_for_pos: bool = True


class ProductListResponse(BaseModel):
    items: List[ProductOut]
    total: int
    page: int
    limit: int


class StoreProductUpdate(BaseModel):
    custom_retail_price: Optional[float] = Field(None, ge=0, description="Harga jual kustom untuk toko")
    is_floor_display: Optional[bool] = Field(None, description="Tandai kasur/produk terpasang di floor display toko")
    is_active_for_pos: Optional[bool] = Field(None, description="Aktifkan atau nonaktifkan produk di kasir POS")
