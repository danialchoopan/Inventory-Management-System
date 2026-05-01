from typing import List, Optional
from uuid import UUID
from sqlalchemy import select, update, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.models.inventory import Product, InventoryTransaction, StockHistory, TransactionType
from app.api.schemas import ProductCreate, ProductUpdate
import logging

logger = logging.getLogger(__name__)

class ProductRepository:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_product(self, product_data: ProductCreate) -> Product:
        db_product = Product(
            sku=product_data.sku,
            name=product_data.name,
            description=product_data.description,
            price=product_data.price,
            current_stock=product_data.current_stock
        )
        self.session.add(db_product)
        await self.session.commit()
        await self.session.refresh(db_product)
        return db_product

    async def get_product_by_sku(self, sku: str) -> Optional[Product]:
        result = await self.session.execute(
            select(Product).where(Product.sku == sku)
        )
        return result.scalars().first()

    async def get_product_by_id(self, product_id: UUID) -> Optional[Product]:
        result = await self.session.execute(
            select(Product).where(Product.id == product_id)
        )
        return result.scalars().first()

    async def update_product_details(self, product: Product, update_ ProductUpdate) -> Product:
        if update_data.name is not None:
            product.name = update_data.name
        if update_data.description is not None:
            product.description = update_data.description
        if update_data.price is not None:
            product.price = update_data.price
        
        await self.session.commit()
        await self.session.refresh(product)
        return product

    async def list_products(self, skip: int = 0, limit: int = 100) -> List[Product]:
        result = await self.session.execute(
            select(Product).offset(skip).limit(limit)
        )
        return result.scalars().all()


class TransactionRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_transaction(self, transaction: InventoryTransaction) -> InventoryTransaction:
        self.session.add(transaction)
        return transaction


class StockHistoryRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def record_history(self, history: StockHistory) -> StockHistory:
        self.session.add(history)
        return history

    async def get_history_by_product(self, product_id: UUID, limit: int = 50) -> List[StockHistory]:
        result = await self.session.execute(
            select(StockHistory)
            .where(StockHistory.product_id == product_id)
            .order_by(desc(StockHistory.changed_at))
            .limit(limit)
        )
        return result.scalars().all()

    async def get_transactions_by_product(self, product_id: UUID, limit: int = 50) -> List[InventoryTransaction]:
        result = await self.session.execute(
            select(InventoryTransaction)
            .where(InventoryTransaction.product_id == product_id)
            .order_by(desc(InventoryTransaction.created_at))
            .limit(limit)
        )
        return result.scalars().all()