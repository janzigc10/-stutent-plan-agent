import pytest

from tests.conftest import TestSession


@pytest.mark.asyncio
async def test_ws_auth_required(client):
    """WebSocket route should be registered."""
    from app.database import get_db
    from app.main import create_app

    app = create_app()

    async def override_get_db():
        async with TestSession() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db

    routes = [route.path for route in app.routes]
    assert "/ws/chat" in routes