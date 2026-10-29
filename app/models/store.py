from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base


class StoreTier(Base):
    __tablename__ = "store_tier"
    __table_args__ = {"schema": "store"}

    id = Column(UUID(as_uuid=True), primary_key=True)
    code = Column(String(100), nullable=False, unique=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    level = Column(Integer, default=1, nullable=False)
    credit_limit = Column(Numeric(15, 2), default=0, nullable=False)
    status = Column(Boolean, default=True, nullable=False)
    deleted = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=True)
    updated_at = Column(DateTime(timezone=True), nullable=True)

    stores = relationship("Store", back_populates="tier")


class Store(Base):
    __tablename__ = "store"
    __table_args__ = {"schema": "store"}

    id = Column(UUID(as_uuid=True), primary_key=True)
    tier_id = Column(UUID(as_uuid=True), ForeignKey("store.store_tier.id"), nullable=True)
    code = Column(String(100), nullable=False, unique=True)
    name = Column(String(255), nullable=False)
    owner_user_id = Column(UUID(as_uuid=True), nullable=True)
    credit_limit = Column(Numeric(15, 2), default=0, nullable=False)
    outstanding_balance = Column(Numeric(15, 2), default=0, nullable=False)
    address = Column(Text, nullable=True)
    phone = Column(String(50), nullable=True)
    email = Column(String(255), nullable=True)
    payment_term = Column(Integer, default=0, nullable=False)
    status = Column(Boolean, default=True, nullable=False)
    sort_order = Column(Integer, default=0, nullable=False)
    deleted = Column(Boolean, default=False, nullable=False)
    address_number = Column(Integer, nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), nullable=True)
    updated_at = Column(DateTime(timezone=True), nullable=True)

    tier = relationship("StoreTier", back_populates="stores")
    users = relationship("StoreUser", back_populates="store", foreign_keys="StoreUser.store_id")

    @property
    def available_credit(self) -> float:
        limit = float(self.credit_limit or 0)
        outstanding = float(self.outstanding_balance or 0)
        return max(0.0, limit - outstanding)
