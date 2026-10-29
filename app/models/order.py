from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base


class Order(Base):
    __tablename__ = "orders"
    __table_args__ = {"schema": "sales"}

    id = Column(UUID(as_uuid=True), primary_key=True)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customer.customers.id"), nullable=False)
    status = Column(Integer, default=1, nullable=False)  # 1: Pending, 2: Processing, 3: Completed, etc.
    payment_method = Column(String(100), nullable=True)  # CASH, TRANSFER, CREDIT_LIMIT
    payment_status = Column(Integer, default=0, nullable=False)  # 0: Unpaid, 1: Paid, 2: Failed
    subtotal = Column(Numeric(15, 2), default=0, nullable=False)
    tax = Column(Numeric(15, 2), default=0, nullable=False)
    discount = Column(Numeric(15, 2), default=0, nullable=False)
    total = Column(Numeric(15, 2), default=0, nullable=False)
    notes = Column(Text, nullable=True)
    meta = Column(JSON, nullable=True)
    creator = Column(String(255), nullable=True)
    editor = Column(String(255), nullable=True)
    deleted = Column(Boolean, default=False, nullable=False)
    voucher_id = Column(UUID(as_uuid=True), nullable=True)
    transaction_fee = Column(Numeric(15, 2), default=0, nullable=False)
    order_number = Column(String(255), nullable=False, unique=True)
    store_id = Column(UUID(as_uuid=True), nullable=True)
    store_channel_id = Column(UUID(as_uuid=True), nullable=True)
    business_unit = Column(String(50), nullable=True)
    address_number = Column(Integer, nullable=True)
    created_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, nullable=True)

    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")


class OrderItem(Base):
    __tablename__ = "order_items"
    __table_args__ = {"schema": "sales"}

    id = Column(UUID(as_uuid=True), primary_key=True)
    order_id = Column(UUID(as_uuid=True), ForeignKey("sales.orders.id"), nullable=False)
    product_id = Column(UUID(as_uuid=True), ForeignKey("finish_goods.products.id"), nullable=False)
    product_variant_id = Column(UUID(as_uuid=True), ForeignKey("finish_goods.product_variants.id"), nullable=True)
    name = Column(String(255), nullable=False)
    quantity = Column(Integer, default=1, nullable=False)
    unit_price = Column(Numeric(15, 2), default=0, nullable=False)
    total = Column(Numeric(15, 2), default=0, nullable=False)
    discount_nominal = Column(Numeric(15, 2), default=0, nullable=False)
    discount_percent = Column(Numeric(5, 2), default=0, nullable=False)
    item_notes = Column(Text, nullable=True)
    meta = Column(JSON, nullable=True)
    created_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, nullable=True)

    order = relationship("Order", back_populates="items")
