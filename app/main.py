from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from contextlib import asynccontextmanager
import logging

from app.core.config import settings
from app.infrastructure.database import engine, Base
from app.api.routes import router
from app.api.auth import router as auth_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

app = FastAPI(title="Advanced Inventory System", lifespan=lifespan)
app.include_router(auth_router)
app.include_router(router)
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(request, "login.html")

@app.get("/dashboard/{role}", response_class=HTMLResponse)
async def dashboard(request: Request, role: str):
    # Dynamic template selection based on role
    template_name = f"{role}_dashboard.html"
    return templates.TemplateResponse(request, template_name)

@app.get("/health")
def health(): return {"status": "ok"}
