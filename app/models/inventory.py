import uuid
from datetime import datetime
from enum import Enum
from sqlalchemy import Column, String, Integer, Numeric, DateTime, ForeignKey, Index, Enum as SQLEnum, Boolean, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.infrastructure.database import Base

# --- Enums ---

class TransactionType(str, Enum):
    PURCHASE = "PURCHASE"
    SALE = "SALE"
    RETURN = "RETURN"
    ADJUSTMENT = "ADJUSTMENT"
    TRANSFER = "TRANSFER" # Inter-warehouse

class StockStatus(str, Enum):
    AVAILABLE = "AVAILABLE"
    QUARANTINE = "QUARANTINE"
    RESERVED = "RESERVED"
    EXPIRED = "EXPIRED"

class OrderStatus(str, Enum):
    PROFORMA = "PROFORMA" # پیش‌فاکتور
    CONFIRMED = "CONFIRMED"
    SHIPPED = "SHIPPED"
    CANCELLED = "CANCELLED"

# --- Models ---

class Supplier(Base):
    __tablename__ = "suppliers"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    contact_person = Column(String(100))
    phone = Column(String(20))
    address = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

class Warehouse(Base):
    __tablename__ = "warehouses"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    location = Column(String(255), nullable=True)

    locations = relationship("WarehouseLocation", back_populates="warehouse")

class WarehouseLocation(Base):
    __tablename__ = "warehouse_locations"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    warehouse_id = Column(UUID(as_uuid=True), ForeignKey("warehouses.id"), nullable=False)
    aisle = Column(String(10)) # ردیف
    rack = Column(String(10))  # قفسه
    shelf = Column(String(10)) # طبقه
    bin = Column(String(10))   # سلول

    warehouse = relationship("Warehouse", back_populates="locations")

class Product(Base):
    __tablename__ = "products"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sku = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Numeric(15, 2), nullable=False, default=0.00)
    
    reorder_point = Column(Integer, default=5) # نقطه سفارش
    batch_tracking = Column(Boolean, default=False)
    serial_tracking = Column(Boolean, default=False)

    # Stock summarized (denormalized for speed)
    total_stock = Column(Integer, default=0)
    
    version = Column(Integer, nullable=False, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    transactions = relationship("InventoryTransaction", back_populates="product")

    __mapper_args__ = {"version_id_col": version}

class InventoryItem(Base):
    """Specific stock units in a specific location/batch"""
    __tablename__ = "inventory_items"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=False)
    warehouse_id = Column(UUID(as_uuid=True), ForeignKey("warehouses.id"), nullable=False)
    location_id = Column(UUID(as_uuid=True), ForeignKey("warehouse_locations.id"), nullable=True)

    quantity = Column(Integer, nullable=False, default=0)
    status = Column(SQLEnum(StockStatus), default=StockStatus.AVAILABLE)

    batch_number = Column(String(50), nullable=True)
    serial_number = Column(String(100), nullable=True)
    expiry_date = Column(DateTime, nullable=True)

class SalesOrder(Base):
    __tablename__ = "sales_orders"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_number = Column(String(50), unique=True, index=True)
    customer_name = Column(String(255))
    total_amount = Column(Numeric(15, 2))
    status = Column(SQLEnum(OrderStatus), default=OrderStatus.PROFORMA)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

class InventoryTransaction(Base):
    __tablename__ = "inventory_transactions"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=False)
    from_warehouse_id = Column(UUID(as_uuid=True), ForeignKey("warehouses.id"), nullable=True)
    to_warehouse_id = Column(UUID(as_uuid=True), ForeignKey("warehouses.id"), nullable=True)
    
    quantity_change = Column(Integer, nullable=False)
    transaction_type = Column(SQLEnum(TransactionType), nullable=False)
    
    reference_id = Column(String(100), nullable=True)
    performed_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    product = relationship("Product", back_populates="transactions")

class StockHistory(Base):
    __tablename__ = "stock_history"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=False)
    old_stock = Column(Integer)
    new_stock = Column(Integer)
    changed_at = Column(DateTime, default=datetime.utcnow)

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    action = Column(String(255)) # e.g. "PRODUCT_UPDATE", "STOCK_TRANSFER"
    details = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
