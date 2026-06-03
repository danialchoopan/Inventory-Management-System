import logging
from typing import List, Optional
from uuid import UUID
from sqlalchemy import select, update, desc, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.inventory import Product, InventoryTransaction, StockHistory, Warehouse, WarehouseLocation, AuditLog, SalesOrder
from app.api.schemas import ProductCreate, ProductUpdate

logger = logging.getLogger(__name__)

class ProductRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def list_products(self) -> List[Product]:
        result = await self.session.execute(select(Product).order_by(Product.name))
        return result.scalars().all()

    async def get_product_by_sku(self, sku: str) -> Optional[Product]:
        result = await self.session.execute(select(Product).where(Product.sku == sku))
        return result.scalars().first()

    async def create_product(self, data: ProductCreate) -> Product:
        product = Product(**data.dict())
        self.session.add(product)
        await self.session.commit()
        await self.session.refresh(product)
        return product

class InventoryRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_transaction(self, txn: InventoryTransaction):
        self.session.add(txn)
        return txn

    async def log_audit(self, user_id: UUID, action: str, details: str):
        log = AuditLog(user_id=user_id, action=action, details=details)
        self.session.add(log)

    async def get_warehouse_stats(self):
        # Real implementation would query DB
        return {
            "total_value": 1250000000,
            "alerts": 12
        }
