from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import UUID
import logging

from app.infrastructure.database import get_db_session, redis_client
from app.services.inventory_service import InventoryService, ConcurrencyError
from app.api.schemas import (
    ProductCreate, 
    ProductUpdate, 
    ProductResponse, 
    StockUpdateRequest, 
    TransactionResponse, 
    UserResponse
)
from app.api.auth import get_current_user, check_role
from app.models.user import User, UserRole
from app.models.inventory import TransactionType

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/inventory", tags=["Inventory Management"])

def get_inventory_service(db_session: AsyncSession = Depends(get_db_session)) -> InventoryService:
    return InventoryService(db_session=db_session)

# --- Endpoints ---

@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.get("/products", response_model=List[ProductResponse])
async def list_products(service: InventoryService = Depends(get_inventory_service)):
    return await service.product_repo.list_products()

@router.post("/products", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    product_data: ProductCreate,
    service: InventoryService = Depends(get_inventory_service),
    current_user: User = Depends(check_role([UserRole.ADMIN]))
):
    return await service.create_product(product_data)

@router.post("/products/{sku}/stock", response_model=ProductResponse)
async def update_stock(
    sku: str,
    stock_request: StockUpdateRequest,
    service: InventoryService = Depends(get_inventory_service),
    current_user: User = Depends(get_current_user)
):
    # RBAC logic for stock updates
    if current_user.role == UserRole.WORKER:
        if stock_request.transaction_type != TransactionType.ADJUSTMENT:
             raise HTTPException(status_code=403, detail="Workers can only perform stock adjustments (counting)")
    elif current_user.role == UserRole.SELLER:
         if stock_request.transaction_type not in [TransactionType.SALE, TransactionType.RETURN]:
            raise HTTPException(status_code=403, detail="Sellers can only perform sales and returns")
    elif current_user.role == UserRole.CASHIER:
         if stock_request.transaction_type != TransactionType.SALE:
            raise HTTPException(status_code=403, detail="Cashiers can only perform sales")

    return await service.update_stock(sku, stock_request, performed_by=current_user.id)

@router.get("/stats/overview")
async def get_overview_stats(
    service: InventoryService = Depends(get_inventory_service),
    current_user: User = Depends(check_role([UserRole.ADMIN]))
):
    # Mock stats for demo
    return {
        "total_value": 1250000000,
        "active_warehouses": 5,
        "low_stock_alerts": 12,
        "dead_stock_items": 8
    }
