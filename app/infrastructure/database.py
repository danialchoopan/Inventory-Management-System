from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from redis import asyncio as aioredis
from app.core.config import settings

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_pre_ping=True,  
    future=True
)

async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,  
    autocommit=False,
    autoflush=False
)

class Base(DeclarativeBase):
    pass

redis_client = aioredis.from_url(
    settings.REDIS_URL,
    encoding="utf-8", 
    decode_responses=True
)

async def get_db_session() -> AsyncSession:
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()

async def get_redis() -> aioredis.Redis:
    return redis_client