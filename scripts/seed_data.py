import asyncio
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.infrastructure.database import engine, async_session_maker, Base
from app.models.user import User, UserRole
from app.models.inventory import Product, Warehouse, TransactionType, WarehouseLocation
from app.core.auth import get_password_hash
from decimal import Decimal

async def seed_data():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    async with async_session_maker() as session:
        # Users
        users = [
            User(username="admin", hashed_password=get_password_hash("admin123"), full_name="مدیر کل", role=UserRole.ADMIN),
            User(username="seller", hashed_password=get_password_hash("seller123"), full_name="فروشنده برتر", role=UserRole.SELLER),
            User(username="cashier", hashed_password=get_password_hash("cashier123"), full_name="صندوق‌دار ۱", role=UserRole.CASHIER),
            User(username="storekeeper", hashed_password=get_password_hash("storekeeper123"), full_name="انباردار اصلی", role=UserRole.STOREKEEPER),
            User(username="worker", hashed_password=get_password_hash("worker123"), full_name="کارگر انبار", role=UserRole.WORKER)
        ]
        session.add_all(users)

        # Warehouses
        w1 = Warehouse(name="انبار مرکزی (تهران)")
        w2 = Warehouse(name="انبار غرب (کرج)")
        session.add_all([w1, w2])
        await session.flush()

        # Locations
        session.add_all([
            WarehouseLocation(warehouse_id=w1.id, aisle="A", rack="1", shelf="1", bin="01"),
            WarehouseLocation(warehouse_id=w1.id, aisle="B", rack="2", shelf="3", bin="12")
        ])

        # Products
        session.add_all([
            Product(sku="LAP-ASUS-Z", name="لپ‌تاپ ایسوس ZenBook", price=Decimal("65000000"), total_stock=15, reorder_point=5),
            Product(sku="PHN-SAMI-S23", name="گوشی سامسونگ S23", price=Decimal("45000000"), total_stock=40, reorder_point=10),
            Product(sku="MOU-LOGI-MX", name="ماوس لاجیتک MX", price=Decimal("4500000"), total_stock=100, reorder_point=20),
            Product(sku="TAB-APPL-IP", name="آی‌پد پرو ۲۰۲۴", price=Decimal("85000000"), total_stock=8, reorder_point=3)
        ])

        await session.commit()
        print("Advanced Data seeded successfully!")

if __name__ == "__main__":
    asyncio.run(seed_data())
