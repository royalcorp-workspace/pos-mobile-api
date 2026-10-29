import uuid
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.core.database import Base


class Product(Base):
    __tablename__ = "products"
    __table_args__ = {"schema": "finish_goods"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    category_id = Column(UUID(as_uuid=True), nullable=False)
    brand_id = Column(UUID(as_uuid=True), nullable=False)
    name = Column(String(255), nullable=False)
    slug = Column(String(255), nullable=False)
    thumbnail = Column(String(500), nullable=True)
    short_description = Column(String(500), nullable=True)
    description = Column(Text, nullable=True)
    status = Column(Integer, default=1, nullable=False)
    deleted = Column(Boolean, default=False, nullable=False)
    show_on_web = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=True)
    updated_at = Column(DateTime(timezone=True), nullable=True)

    variants = relationship("ProductVariant", back_populates="product", cascade="all, delete-orphan")


class ProductVariant(Base):
    __tablename__ = "product_variants"
    __table_args__ = {"schema": "finish_goods"}

    id = Column(UUID(as_uuid=True), primary_key=True)
    product_id = Column(UUID(as_uuid=True), ForeignKey("finish_goods.products.id"), nullable=False)
    variant_name = Column(String(255), nullable=False)
    sku = Column(String(100), nullable=True)
    sell_price = Column(Numeric(15, 2), nullable=True)
    base_price = Column(Numeric(15, 2), nullable=True)
    stock_quantity = Column(Integer, default=0, nullable=False)
    status = Column(Integer, default=1, nullable=False)
    deleted = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=True)
    updated_at = Column(DateTime(timezone=True), nullable=True)

    product = relationship("Product", back_populates="variants")


class StoreProduct(Base):
    __tablename__ = "store_products"
    __table_args__ = {"schema": "finish_goods"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    store_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    branch_id = Column(Integer, nullable=True)
    business_unit = Column(String(50), nullable=True)
    short_item_no = Column(Integer, default=0, nullable=False)
    sku = Column(String(100), nullable=False)
    item_name = Column(String(255), nullable=False)
    item_size = Column(String(100), nullable=True)
    brand_name = Column(String(100), nullable=True)
    category_name = Column(String(100), nullable=True)
    segments = Column(JSONB, nullable=True)
    base_price = Column(Numeric(15, 2), default=0, nullable=False)
    suggested_retail_price = Column(Numeric(15, 2), nullable=True)
    custom_retail_price = Column(Numeric(15, 2), nullable=True)
    is_active_for_pos = Column(Boolean, default=True, nullable=False)
    is_floor_display = Column(Boolean, default=False, nullable=False)
    is_dedicated = Column(Boolean, default=False, nullable=False)
    display_order = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=True)
    updated_at = Column(DateTime(timezone=True), nullable=True)
