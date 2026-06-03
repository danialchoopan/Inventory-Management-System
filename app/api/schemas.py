from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from uuid import UUID
from decimal import Decimal
from app.models.inventory import TransactionType, StockStatus, OrderStatus

# --- Base Schemas ---

class WarehouseResponse(BaseModel):
    id: UUID
    name: str
    location: Optional[str]

    class Config:
        from_attributes = True

class WarehouseLocationResponse(BaseModel):
    id: UUID
    aisle: str
    rack: str
    shelf: str
    bin: str

    class Config:
        from_attributes = True

# --- Product Schemas ---

class ProductCreate(BaseModel):
    sku: str = Field(..., min_length=1, max_length=50)
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    price: Decimal = Field(..., ge=0)
    reorder_point: int = 5
    batch_tracking: bool = False
    serial_tracking: bool = False

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[Decimal] = None
    reorder_point: Optional[int] = None

class ProductResponse(BaseModel):
    id: UUID
    sku: str
    name: str
    description: Optional[str]
    price: Decimal
    total_stock: int
    reorder_point: int
    version: int
    created_at: datetime

    class Config:
        from_attributes = True

# --- Inventory & Transaction ---

class StockUpdateRequest(BaseModel):
    quantity_change: int
    transaction_type: TransactionType
    reference_id: Optional[str] = None
    from_warehouse_id: Optional[UUID] = None
    to_warehouse_id: Optional[UUID] = None

class TransactionResponse(BaseModel):
    id: UUID
    product_id: UUID
    quantity_change: int
    transaction_type: TransactionType
    created_at: datetime

    class Config:
        from_attributes = True

# --- User ---

class UserResponse(BaseModel):
    id: UUID
    username: str
    full_name: Optional[str]
    role: str
    created_at: datetime

    class Config:
        from_attributes = True
