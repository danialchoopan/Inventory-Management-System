import asyncio
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.infrastructure.database import engine, async_session_maker, Base
from app.models.user import User, UserRole
from app.models.inventory import Product, Warehouse, TransactionType, InventoryTransaction
from app.core.auth import get_password_hash
from decimal import Decimal

async def seed_data():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    async with async_session_maker() as session:
        session.add_all([
            User(username="admin", hashed_password=get_password_hash("admin123"), full_name="مدیر سیستم", role=UserRole.MANAGER),
            User(username="seller", hashed_password=get_password_hash("seller123"), full_name="فروشنده ۱", role=UserRole.SELLER),
            User(username="worker", hashed_password=get_password_hash("worker123"), full_name="کارگر انبار", role=UserRole.WORKER)
        ])
        session.add_all([
            Product(sku="LAP-001", name="لپ‌تاپ ایسوس", description="ZenBook", price=Decimal("45000000"), current_stock=10),
            Product(sku="PHN-002", name="گوشی سامسونگ", description="S21", price=Decimal("25000000"), current_stock=25)
        ])
        await session.commit()
        print("Data seeded!")

if __name__ == "__main__":
    asyncio.run(seed_data())
