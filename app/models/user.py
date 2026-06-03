import uuid
from datetime import datetime
from enum import Enum
from sqlalchemy import Column, String, DateTime, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from app.infrastructure.database import Base

class UserRole(str, Enum):
    ADMIN = "ADMIN"          # مدیر کل
    SELLER = "SELLER"        # فروشنده
    CASHIER = "CASHIER"      # صندوق‌دار
    STOREKEEPER = "STOREKEEPER" # انباردار
    WORKER = "WORKER"        # کارگر انبار

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(50), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=True)
    role = Column(SQLEnum(UserRole), nullable=False, default=UserRole.WORKER)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<User(username='{self.username}', role='{self.role}')>"
