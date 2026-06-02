import uuid
from datetime import datetime
from enum import Enum
from sqlalchemy import Column, String, Integer, Numeric, DateTime, ForeignKey, Index, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.infrastructure.database import Base

# --- Enums ---

class TransactionType(str, Enum):
    PURCHASE = "PURCHASE"
    SALE = "SALE"
    RETURN = "RETURN"
    ADJUSTMENT = "ADJUSTMENT"

# --- Models ---

class Product(Base):
    __tablename__ = "products"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sku = Column(String(50), unique=True, nullable=False, index=True) # Indexed for fast lookups
    name = Column(String(255), nullable=False) # Supports UTF-8 for Farsi 🇮🇷
    description = Column(String, nullable=True) # Text type for longer descriptions
    current_stock = Column(Integer, nullable=False, default=0)
    price = Column(Numeric(10, 2), nullable=False, default=0.00)
    
    # Optimistic Locking Column
    version = Column(Integer, nullable=False, default=1)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    transactions = relationship("InventoryTransaction", back_populates="product")
    stock_history = relationship("StockHistory", back_populates="product")

    # Enable Optimistic Locking in SQLAlchemy
    __mapper_args__ = {
        "version_id_col": version
    }

    def __repr__(self):
        return f"<Product(sku='{self.sku}', name='{self.name}')>"


class InventoryTransaction(Base):
    __tablename__ = "inventory_transactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=False)
    
    quantity_change = Column(Integer, nullable=False) # Positive for inbound, negative for outbound
    transaction_type = Column(SQLEnum(TransactionType), nullable=False)
    
    reference_id = Column(String(100), nullable=True) # e.g., Order ID, Invoice Number
    performed_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True) # User ID who made the change
    
    created_at = Column(DateTime, default=datetime.utcnow, index=True) # Indexed for time-range queries

    # Relationship
    product = relationship("Product", back_populates="transactions")
    user = relationship("app.models.user.User")

    # Indexes for performance
    __table_args__ = (
        Index('idx_txn_product_id', 'product_id'),
        Index('idx_txn_created_at', 'created_at'),
    )

    def __repr__(self):
        return f"<Transaction(id='{self.id}', type='{self.transaction_type}', qty={self.quantity_change})>"


class StockHistory(Base):
    __tablename__ = "stock_history"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=False)
    
    old_stock = Column(Integer, nullable=False)
    new_stock = Column(Integer, nullable=False)
    
    old_price = Column(Numeric(10, 2), nullable=False)
    new_price = Column(Numeric(10, 2), nullable=False)
    
    changed_at = Column(DateTime, default=datetime.utcnow, index=True) # Indexed for trends

    # Relationship
    product = relationship("Product", back_populates="stock_history")

    # Indexes
    __table_args__ = (
        Index('idx_history_product_id', 'product_id'),
        Index('idx_history_changed_at', 'changed_at'),
    )

    def __repr__(self):
        return f"<StockHistory(product_id='{self.product_id}', stock={self.old_stock}->{self.new_stock})>"


class Warehouse(Base):
    __tablename__ = "warehouses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False) # Supports Farsi 🇮🇷
    location = Column(String(255), nullable=True)

    def __repr__(self):
        return f"<Warehouse(name='{self.name}')>"
