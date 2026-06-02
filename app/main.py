from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from contextlib import asynccontextmanager
import logging
import os

from app.core.config import settings
from app.infrastructure.database import engine, Base
from app.api.routes import router
from app.api.auth import router as auth_router

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
app.include_router(auth_router)
app.include_router(router)

# UI Logic
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(request, "login.html")

@app.get("/dashboard/manager", response_class=HTMLResponse)
async def manager_dashboard(request: Request):
    return templates.TemplateResponse(request, "manager_dashboard.html")

@app.get("/dashboard/seller", response_class=HTMLResponse)
async def seller_dashboard(request: Request):
    return templates.TemplateResponse(request, "seller_dashboard.html")

@app.get("/dashboard/worker", response_class=HTMLResponse)
async def worker_dashboard(request: Request):
    return templates.TemplateResponse(request, "worker_dashboard.html")

@app.get("/health")
def read_root():
    """Health Check Endpoint"""
    return {"status": "healthy", "message": "Inventory API is running!"}
