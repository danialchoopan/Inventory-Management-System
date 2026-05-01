from fastapi import FastAPI
from contextlib import asynccontextmanager
import logging

from app.core.config import settings
from app.infrastructure.database import engine, Base
from app.api.routes import router

# Configure Logging 📝
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Create Database Tables
    logger.info("Starting up application...")
    async with engine.begin() as conn:
        # Create all tables defined in models
        await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created/verified.")
    
    yield
    
    # Shutdown: Cleanup (if needed)
    logger.info("Shutting down application...")
    await engine.dispose()

# Initialize FastAPI App
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Inventory Management System",
    lifespan=lifespan
)

# Include Routers
app.include_router(router)

@app.get("/")
def read_root():
    """Health Check Endpoint"""
    return {"status": "healthy", "message": "Inventory API is running!"}