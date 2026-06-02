import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.fixture(scope="session")
def anyio_backend(): return "asyncio"

@pytest.mark.anyio
async def test_health():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/health")
    assert response.status_code == 200

@pytest.mark.anyio
async def test_login():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/auth/login", data={"username": "admin", "password": "admin123"})
    assert response.status_code == 200
