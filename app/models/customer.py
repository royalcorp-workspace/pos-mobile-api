from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base


class Customer(Base):
    __tablename__ = "customers"
    __table_args__ = {"schema": "customer"}

    id = Column(UUID(as_uuid=True), primary_key=True)
    user_id = Column(UUID(as_uuid=True), nullable=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)
    meta = Column(Text, nullable=True)
    creator = Column(String(255), nullable=True)
    editor = Column(String(255), nullable=True)
    deleted = Column(Boolean, default=False, nullable=False)
    customer_type = Column(Integer, default=1, nullable=False)
    membership_level = Column(String(50), nullable=True)
    customer_code = Column(String(50), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=True)
    updated_at = Column(DateTime(timezone=True), nullable=True)
