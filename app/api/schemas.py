from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from uuid import UUID
from decimal import Decimal
from app.models.inventory import TransactionType

# --- Product Schemas ---

class ProductCreate(BaseModel):
    sku: str = Field(..., min_length=1, max_length=50, description="Unique Stock Keeping Unit")
    name: str = Field(..., min_length=1, max_length=255, description="Product Name (supports Farsi 🇮🇷)")
    description: Optional[str] = Field(None, max_length=1000, description="Product Description")
    price: Decimal = Field(..., ge=0, description="Price must be non-negative")
    current_stock: int = Field(0, ge=0, description="Initial stock level")


class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    price: Optional[Decimal] = Field(None, ge=0)

class ProductResponse(BaseModel):
    id: UUID
    sku: str
    name: str
    description: Optional[str]
    current_stock: int
    price: Decimal
    version: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# --- Stock Update Schemas ---

class StockUpdateRequest(BaseModel):
    quantity_change: int = Field(..., description="Positive for add, negative for remove")
    transaction_type: TransactionType = Field(..., description="Type of transaction")
    reference_id: Optional[str] = Field(None, max_length=100, description="Reference ID (e.g., Order #)")
    
    @validator('quantity_change')
    def quantity_cannot_be_zero(cls, v):
        if v == 0:
            raise ValueError("Quantity change cannot be zero")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "quantity_change": -5,
                "transaction_type": "SALE",
                "reference_id": "ORD-12345"
            }
        }

# --- History & Transaction Schemas ---

class TransactionResponse(BaseModel):
    id: UUID
    product_id: UUID
    quantity_change: int
    transaction_type: TransactionType
    reference_id: Optional[str]
    performed_by: Optional[UUID]
    created_at: datetime

    class Config:
        from_attributes = True

class StockHistoryResponse(BaseModel):
    id: UUID
    product_id: UUID
    old_stock: int
    new_stock: int
    old_price: Decimal
    new_price: Decimal
    changed_at: datetime

    class Config:
        from_attributes = True

class UserResponse(BaseModel):
    id: UUID
    username: str
    full_name: Optional[str]
    role: str
    created_at: datetime

    class Config:
        from_attributes = True
