from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import UUID
import time
import logging

from app.infrastructure.database import get_db_session, redis_client
from app.services.inventory_service import InventoryService, ConcurrencyError
from app.api.schemas import (
    ProductCreate, 
    ProductUpdate, 
    ProductResponse, 
    StockUpdateRequest, 
    TransactionResponse, 
    StockHistoryResponse
)
from app.core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/inventory", tags=["Inventory Management"])

# --- Dependencies ---

def get_inventory_service(db_session: AsyncSession = Depends(get_db_session)) -> InventoryService:
    return InventoryService(db_session=db_session)

async def rate_limit_middleware(request: Request):
    client_ip = request.client.host
    key = f"rate_limit:{client_ip}"
    
    current_count = await redis_client.get(key)
    
    if current_count is None:
        await redis_client.setex(key, settings.RATE_LIMIT_WINDOW, 1)
    else:
        current_count = int(current_count)
        if current_count >= settings.RATE_LIMIT_REQUESTS:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many requests. Please slow down."
            )
        await redis_client.incr(key)

# --- Endpoints ---

@router.post("/products", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    product_data: ProductCreate,
    service: InventoryService = Depends(get_inventory_service)
):
    try:
        return await service.create_product(product_data)
    except Exception as e:
        logger.error(f"Error creating product: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.get("/products/{sku}", response_model=ProductResponse)
async def get_product_by_sku(
    sku: str,
    service: InventoryService = Depends(get_inventory_service)
):
    product = await service.get_product_by_sku(sku)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.put("/products/{sku}", response_model=ProductResponse)
async def update_product(
    sku: str,
    update_data: ProductUpdate,
    service: InventoryService = Depends(get_inventory_service)
):
    try:
        return await service.update_product_details(sku, update_data)
    except ValueError:
        raise HTTPException(status_code=404, detail="Product not found")
    except Exception as e:
        logger.error(f"Error updating product: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.post("/products/{sku}/stock", response_model=ProductResponse)
async def update_stock(
    sku: str,
    stock_request: StockUpdateRequest,
    request: Request,
    service: InventoryService = Depends(get_inventory_service)
):
    
    # Apply Rate Limiting
    await rate_limit_middleware(request)

    try:
        return await service.update_stock(sku, stock_request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ConcurrencyError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, 
            detail="Conflict: Product was modified by another process. Please retry."
        )
    except Exception as e:
        logger.error(f"Error updating stock: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.get("/products/{product_id}/transactions", response_model=List[TransactionResponse])
async def get_transaction_history(
    product_id: UUID,
    service: InventoryService = Depends(get_inventory_service)
):
    return await service.get_transaction_history(product_id)

@router.get("/products/{product_id}/history", response_model=List[StockHistoryResponse])
async def get_stock_history(
    product_id: UUID,
    service: InventoryService = Depends(get_inventory_service)
):
    """
    Get stock/price history for trend analysis.
    """
    return await service.get_stock_history(product_id)