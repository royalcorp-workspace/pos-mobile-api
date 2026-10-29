from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base


class StoreUser(Base):
    __tablename__ = "store_users"
    __table_args__ = {"schema": "user_managements"}

    id = Column(UUID(as_uuid=True), primary_key=True)
    user_id = Column(UUID(as_uuid=True), nullable=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    phone = Column(String(50), nullable=True)
    username = Column(String(100), nullable=True, unique=True)
    sales_code = Column(String(50), nullable=True)
    password_hash = Column(String(255), nullable=False)
    email_verified = Column(Boolean, default=False)
    email_verified_at = Column(DateTime, nullable=True)
    remember_token = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True)
    deleted = Column(Boolean, default=False)
    store_id = Column(UUID(as_uuid=True), ForeignKey("store.store.id"), nullable=True)
    user_type = Column(String(50), default="store", nullable=False)
    is_owner = Column(Boolean, default=False)
    role_persona = Column(String(50), nullable=True)
    parent_user_id = Column(UUID(as_uuid=True), ForeignKey("user_managements.store_users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=True)
    updated_at = Column(DateTime(timezone=True), nullable=True)

    store = relationship("Store", back_populates="users", foreign_keys=[store_id])
