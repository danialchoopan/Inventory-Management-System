import logging
import json
from typing import Optional
from uuid import UUID
from decimal import Decimal
from sqlalchemy.exc import StaleDataError
from sqlalchemy.ext.asyncio import AsyncSession
from redis import asyncio as aioredis

from app.models.inventory import Product, InventoryTransaction, StockHistory, TransactionType
from app.repositories.inventory_repo import ProductRepository, TransactionRepository, StockHistoryRepository
from app.api.schemas import ProductCreate, ProductUpdate, StockUpdateRequest
from app.core.config import settings
from app.infrastructure.database import redis_client

logger = logging.getLogger(__name__)

class ConcurrencyError(Exception):
    pass

class InventoryService:

    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
        self.product_repo = ProductRepository(db_session)
        self.txn_repo = TransactionRepository(db_session)
        self.history_repo = StockHistoryRepository(db_session)


    async def _get_cached_product(self, sku: str) -> Optional[dict]:
        try:
            cached_data = await redis_client.get(f"product:{sku}")
            if cached_
                logger.info(f"Cache HIT for SKU: {sku}")
                return json.loads(cached_data)
        except Exception as e:
            logger.error(f"Redis error on get: {e}")
        return None

    async def _cache_product(self, product: Product):
        try:
            product_dict = {
                "id": str(product.id),
                "sku": product.sku,
                "name": product.name,
                "description": product.description,
                "current_stock": product.current_stock,
                "price": str(product.price), 
                "version": product.version,
                "created_at": product.created_at.isoformat(),
                "updated_at": product.updated_at.isoformat()
            }
            await redis_client.setex(
                f"product:{product.sku}", 
                settings.REDIS_CACHE_TTL, 
                json.dumps(product_dict)
            )
            logger.info(f"Cache SET for SKU: {product.sku}")
        except Exception as e:
            logger.error(f"Redis error on set: {e}")

    async def _invalidate_cache(self, sku: str):
        try:
            await redis_client.delete(f"product:{sku}")
            logger.info(f"Cache INVALIDATED for SKU: {sku}")
        except Exception as e:
            logger.error(f"Redis error on delete: {e}")


    async def create_product(self, product_ ProductCreate) -> Product:
        product = await self.product_repo.create_product(product_data)
        await self._cache_product(product)
        return product

    async def get_product_by_sku(self, sku: str) -> Optional[Product]:
       
        cached_data = await self._get_cached_product(sku)
        if cached_data:
            pass 

        product = await self.product_repo.get_product_by_sku(sku)
        
        if product:
            await self._cache_product(product)
            
        return product

    async def update_product_details(self, sku: str, update_ ProductUpdate) -> Product:
        product = await self.product_repo.get_product_by_sku(sku)
        if not product:
            raise ValueError("Product not found")
        
        updated_product = await self.product_repo.update_product_details(product, update_data)
        await self._invalidate_cache(sku)
        return updated_product

    async def update_stock(self, sku: str, stock_request: StockUpdateRequest) -> Product:
       
        product = await self.product_repo.get_product_by_sku(sku)
        if not product:
            raise ValueError("Product not found")

        new_stock = product.current_stock + stock_request.quantity_change
        if new_stock < 0:
            raise ValueError(f"Insufficient stock. Current: {product.current_stock}, Requested change: {stock_request.quantity_change}")

        old_stock = product.current_stock
        old_price = product.price
        
        product.current_stock = new_stock
        
        try:
            txn = InventoryTransaction(
                product_id=product.id,
                quantity_change=stock_request.quantity_change,
                transaction_type=stock_request.transaction_type,
                reference_id=stock_request.reference_id
            )
            await self.txn_repo.create_transaction(txn)

            history = StockHistory(
                product_id=product.id,
                old_stock=old_stock,
                new_stock=new_stock,
                old_price=old_price,
                new_price=product.price
            )
            await self.history_repo.record_history(history)

            await self.db_session.commit()
            
            await self.db_session.refresh(product)
            
            await self._invalidate_cache(sku)
            
            logger.info(f"Stock updated for {sku}: {old_stock} -> {new_stock}")
            return product

        except StaleDataError:
            await self.db_session.rollback()
            logger.warning(f"Concurrency conflict for SKU: {sku}")
            raise ConcurrencyError("Conflict: Product was modified by another process. Please retry.")
        except Exception as e:
            await self.db_session.rollback()
            logger.error(f"Error updating stock for {sku}: {e}")
            raise e

    async def get_transaction_history(self, product_id: UUID) -> list:
        return await self.history_repo.get_transactions_by_product(product_id)

    async def get_stock_history(self, product_id: UUID) -> list:
        return await self.history_repo.get_history_by_product(product_id)