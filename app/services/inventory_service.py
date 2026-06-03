import logging
from typing import Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.inventory import Product, InventoryTransaction, TransactionType
from app.repositories.inventory_repo import ProductRepository, InventoryRepository
from app.api.schemas import ProductCreate, StockUpdateRequest

logger = logging.getLogger(__name__)

class ConcurrencyError(Exception):
    pass

class InventoryService:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
        self.product_repo = ProductRepository(db_session)
        self.inventory_repo = InventoryRepository(db_session)

    async def create_product(self, data: ProductCreate) -> Product:
        return await self.product_repo.create_product(data)

    async def update_stock(self, sku: str, request: StockUpdateRequest, performed_by: UUID) -> Product:
        product = await self.product_repo.get_product_by_sku(sku)
        if not product:
            raise ValueError("کالا یافت نشد")

        product.total_stock += request.quantity_change
        
        txn = InventoryTransaction(
            product_id=product.id,
            quantity_change=request.quantity_change,
            transaction_type=request.transaction_type,
            reference_id=request.reference_id,
            performed_by=performed_by,
            from_warehouse_id=request.from_warehouse_id,
            to_warehouse_id=request.to_warehouse_id
        )
        
        await self.inventory_repo.create_transaction(txn)
        await self.inventory_repo.log_audit(performed_by, "STOCK_UPDATE", f"Update {sku} by {request.quantity_change}")

        await self.db_session.commit()
        await self.db_session.refresh(product)
        return product
