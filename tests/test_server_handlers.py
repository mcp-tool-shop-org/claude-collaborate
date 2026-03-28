"""Tests for server.py HTTP handlers — traversal, health, CORS, API endpoints."""

from __future__ import annotations

import pytest
from aiohttp.test_utils import TestClient, TestServer

from server import create_app


@pytest.fixture
async def client():
    app = create_app()
    async with TestClient(TestServer(app)) as c:
        yield c


# =============================================================================
# Directory traversal prevention
# =============================================================================


@pytest.mark.parametrize("path", [
    "../etc/passwd",
    "..\\server.py",
    "..%2Fetc%2Fpasswd",
    "....//etc/passwd",
])
async def test_static_handler_blocks_traversal(client, path: str):
    """Traversal attempts must not leak files outside DIRECTORY."""
    resp = await client.get(f"/{path}")
    assert resp.status in (403, 404)


async def test_static_handler_404_for_nonexistent(client):
    """Requesting a file that does not exist returns 404."""
    resp = await client.get("/this_file_does_not_exist_12345.txt")
    assert resp.status == 404


# =============================================================================
# Health endpoint
# =============================================================================


async def test_health_returns_200_with_status(client):
    """GET /health returns 200 and JSON with 'status' key."""
    resp = await client.get("/health")
    assert resp.status == 200
    body = await resp.json()
    assert "status" in body


# =============================================================================
# CORS middleware
# =============================================================================


async def test_cors_headers_present(client):
    """Responses include Access-Control-Allow-Origin header."""
    resp = await client.get("/health")
    assert "Access-Control-Allow-Origin" in resp.headers


async def test_cors_options_preflight(client):
    """OPTIONS requests return CORS headers."""
    resp = await client.options("/health")
    assert resp.status == 200
    assert "Access-Control-Allow-Methods" in resp.headers


# =============================================================================
# /api/ws/respond
# =============================================================================


async def test_ws_respond_valid_json(client):
    """POST /api/ws/respond with content returns 200."""
    resp = await client.post(
        "/api/ws/respond",
        json={"content": "Hello from test"},
    )
    assert resp.status == 200
    body = await resp.json()
    assert body.get("status") == "sent"


async def test_ws_respond_empty_content(client):
    """POST /api/ws/respond with empty content returns 400."""
    resp = await client.post(
        "/api/ws/respond",
        json={"content": ""},
    )
    assert resp.status == 400


async def test_ws_respond_invalid_body(client):
    """POST /api/ws/respond with non-JSON body returns 400 or 500."""
    resp = await client.post(
        "/api/ws/respond",
        data=b"not json",
        headers={"Content-Type": "application/json"},
    )
    assert resp.status in (400, 500)


# =============================================================================
# /api/ws/messages
# =============================================================================


async def test_ws_messages_returns_array(client):
    """GET /api/ws/messages returns 200 with a messages array."""
    resp = await client.get("/api/ws/messages")
    assert resp.status == 200
    body = await resp.json()
    assert isinstance(body.get("messages"), list)
