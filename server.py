"""
Claude Collaborate - Real-time collaboration server.

A unified sandbox environment for human-AI collaboration with WebSocket bridge.

Usage:
    python server.py

Then open http://localhost:8877 in your browser.
"""

from __future__ import annotations

import asyncio
import contextlib
import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path

from aiohttp import WSMsgType, web

__version__ = "1.0.4"

# Configure logging
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
logger = logging.getLogger(__name__)

PORT = 8877
DIRECTORY = Path(__file__).parent.resolve()
MAX_WS_CLIENTS = 50

# WebSocket state
connected_ws_clients: set[web.WebSocketResponse] = set()
_messages_lock = asyncio.Lock()
MESSAGE_FILE = DIRECTORY / "messages.jsonl"
RESPONSE_FILE = DIRECTORY / "claude_responses.jsonl"


def _safe_resolve(root: Path, filename: str) -> Path | None:
    try:
        resolved = (root / filename).resolve()
    except (OSError, ValueError):
        return None
    if not str(resolved).startswith(str(root)):
        return None
    if not resolved.is_file():
        return None
    return resolved


async def index_handler(request: web.Request) -> web.StreamResponse:
    """Serve main Claude Collaborate UI."""
    return web.FileResponse(DIRECTORY / "index.html")


async def static_handler(request: web.Request) -> web.StreamResponse:
    """Serve static files."""
    filename = request.match_info.get('filename', '')
    file_path = _safe_resolve(DIRECTORY, filename)
    if file_path:
        return web.FileResponse(file_path)
    return web.Response(text="Not Found", status=404)


async def adventures_handler(request: web.Request) -> web.StreamResponse:
    """Serve Creative Lab."""
    adventures_path = DIRECTORY / "adventures" / "index.html"
    if adventures_path.exists():
        return web.FileResponse(adventures_path)
    return web.Response(text="Creative Lab not found", status=404)


async def adventures_static_handler(request: web.Request) -> web.StreamResponse:
    """Serve Creative Lab static files."""
    filename = request.match_info.get('filename', '')
    file_path = _safe_resolve(DIRECTORY / "adventures", filename)
    if file_path:
        return web.FileResponse(file_path)
    return web.Response(text="Not Found", status=404)


async def websocket_handler(request: web.Request) -> web.WebSocketResponse:
    """Handle WebSocket connections for real-time Claude communication."""
    if len(connected_ws_clients) >= MAX_WS_CLIENTS:
        return web.Response(text="Too many connections", status=503)

    ws = web.WebSocketResponse()
    await ws.prepare(request)

    connected_ws_clients.add(ws)
    logger.info(f"WebSocket client connected. Total: {len(connected_ws_clients)}")

    # Send welcome message
    await ws.send_json({
        "type": "connected",
        "message": "Connected to Claude Collaborate Bridge",
        "timestamp": datetime.now(timezone.utc).isoformat()
    })

    try:
        async for msg in ws:
            if msg.type == WSMsgType.TEXT:
                await handle_ws_message(ws, msg.data)
            elif msg.type == WSMsgType.ERROR:
                logger.error(f"WebSocket error: {ws.exception()}")
    finally:
        connected_ws_clients.discard(ws)
        logger.info(f"WebSocket client disconnected. Total: {len(connected_ws_clients)}")

    return ws


async def handle_ws_message(ws: web.WebSocketResponse, data: str):
    """Process incoming WebSocket message."""
    try:
        message = json.loads(data)
        msg_type = message.get("type", "")

        if msg_type == "user_message":
            content = message.get("content", "")
            logger.info(f"User message: {content[:100]}...")

            # Store message for Claude Code to read
            MESSAGE_FILE.parent.mkdir(parents=True, exist_ok=True)
            with open(MESSAGE_FILE, "a", encoding="utf-8") as f:
                f.write(json.dumps({
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "content": content,
                    "type": "user_message"
                }) + "\n")

            # Acknowledge receipt
            await ws.send_json({
                "type": "message_received",
                "timestamp": datetime.now(timezone.utc).isoformat()
            })

        elif msg_type == "ping":
            await ws.send_json({"type": "pong"})

    except json.JSONDecodeError:
        logger.warning(f"Invalid JSON received: {data[:100]}")
    except Exception as e:
        logger.error(f"Error handling WebSocket message: {e}")


async def broadcast_to_ws_clients(message: dict):
    """Broadcast message to all connected WebSocket clients."""
    if not connected_ws_clients:
        return

    disconnected = set()
    for ws in connected_ws_clients:
        try:
            await ws.send_json(message)
        except Exception:
            disconnected.add(ws)

    connected_ws_clients.difference_update(disconnected)


async def ws_respond_handler(request: web.Request) -> web.Response:
    """HTTP endpoint for Claude Code to send responses to browser."""
    try:
        data = await request.json()
        content = data.get("content", "")

        if not content:
            return web.json_response({"error": "No content provided"}, status=400)

        # Broadcast to all connected clients
        await broadcast_to_ws_clients({
            "type": "claude_response",
            "content": content,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })

        # Store response
        with open(RESPONSE_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps({
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "content": content
            }) + "\n")

        return web.json_response({
            "status": "sent",
            "clients": len(connected_ws_clients)
        })

    except Exception:
        logger.exception("Error in ws_respond_handler")
        return web.json_response({"error": "Internal server error"}, status=500)


async def ws_messages_handler(request: web.Request) -> web.Response:
    """HTTP endpoint for Claude Code to read pending messages."""
    messages = []

    async with _messages_lock:
        if MESSAGE_FILE.exists():
            with open(MESSAGE_FILE, encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        with contextlib.suppress(json.JSONDecodeError):
                            messages.append(json.loads(line))

            MESSAGE_FILE.write_text("")

    return web.json_response({
        "messages": messages,
        "count": len(messages)
    })


async def ws_status_handler(request: web.Request) -> web.Response:
    """WebSocket bridge status."""
    return web.json_response({
        "connected_clients": len(connected_ws_clients),
        "status": "active" if connected_ws_clients else "idle",
        "timestamp": datetime.now(timezone.utc).isoformat()
    })


async def health_handler(request: web.Request) -> web.Response:
    """Health check endpoint."""
    return web.json_response({
        "status": "healthy",
        "service": "claude-collaborate",
        "timestamp": datetime.now(timezone.utc).isoformat()
    })


@web.middleware
async def cors_middleware(request: web.Request, handler):
    """Add CORS headers to all responses."""
    if request.method == "OPTIONS":
        response = web.Response()
    else:
        response = await handler(request)

    response.headers["Access-Control-Allow-Origin"] = "http://localhost:8877"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    return response


def create_app() -> web.Application:
    """Create and configure the application."""
    app = web.Application(middlewares=[cors_middleware], client_max_size=1*1024*1024)

    # Routes
    app.router.add_get("/", index_handler)
    app.router.add_get("/health", health_handler)
    app.router.add_get("/ws", websocket_handler)
    app.router.add_get("/adventures", adventures_handler)
    app.router.add_get("/adventures/{filename:.*}", adventures_static_handler)
    app.router.add_post("/api/ws/respond", ws_respond_handler)
    app.router.add_get("/api/ws/messages", ws_messages_handler)
    app.router.add_get("/api/ws/status", ws_status_handler)
    app.router.add_get("/{filename:.*}", static_handler)

    return app


def main():
    """Run the server."""
    args = sys.argv[1:]
    if "--version" in args or "-V" in args:
        print(f"claude-collaborate {__version__}")
        sys.exit(0)
    if "--help" in args or "-h" in args:
        print(f"claude-collaborate {__version__} — Real-time human-AI collaboration server\n")
        print("Usage: python server.py [options]\n")
        print("Options:")
        print("  --version, -V   Show version and exit")
        print("  --help, -h      Show this help and exit")
        print(f"\nStarts the server on http://localhost:{PORT}")
        sys.exit(0)

    print()
    print("=" * 60)
    print("  Claude Collaborate")
    print("  Where Human Creativity Meets AI Intelligence")
    print("=" * 60)
    print()
    print(f"  Main UI:        http://localhost:{PORT}")
    print(f"  WebSocket:      ws://localhost:{PORT}/ws")
    print(f"  Creative Lab:   http://localhost:{PORT}/adventures")
    print()
    print("  API Endpoints:")
    print("    GET  /api/ws/messages  - Read pending messages")
    print("    POST /api/ws/respond   - Send response to browser")
    print("    GET  /api/ws/status    - Bridge status")
    print()
    print("  Press Ctrl+C to stop")
    print("=" * 60)
    print()

    app = create_app()
    web.run_app(app, host="127.0.0.1", port=PORT, print=None)


if __name__ == "__main__":
    main()
