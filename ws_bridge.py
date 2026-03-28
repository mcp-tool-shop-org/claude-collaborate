"""
WebSocket Bridge for Claude Collaborate
Enables real-time bidirectional communication between browser UI and Claude Code.

Architecture:
  Browser (Claude Collaborate) <--WebSocket--> ws_bridge.py <--File/API--> Claude Code

Usage:
  python ws_bridge.py

Then in Claude Collaborate, connect to ws://localhost:8878
"""

import asyncio
import datetime
import json
from pathlib import Path

import aiohttp
from aiohttp import web

# Configuration
WS_PORT = 8878
MESSAGE_FILE = Path(__file__).parent / "messages.jsonl"
CLAUDE_RESPONSE_FILE = Path(__file__).parent / "claude_responses.jsonl"
MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024
MAX_CLIENTS = 50

connected_clients: set[web.WebSocketResponse] = set()

# File I/O locks to prevent race conditions on read+clear operations
_message_file_lock = asyncio.Lock()
_response_file_lock = asyncio.Lock()


def _rotate_file_if_needed(file_path: Path) -> None:
    """Rotate file if it exceeds MAX_FILE_SIZE_BYTES.

    Rotation scheme: file.jsonl -> file.jsonl.1 -> file.jsonl.2 (deleted)
    """
    if not file_path.exists():
        return

    try:
        size = file_path.stat().st_size
        if size < MAX_FILE_SIZE_BYTES:
            return

        # Rotate: delete .2, rename .1 to .2, rename current to .1
        backup_2 = file_path.with_suffix(file_path.suffix + ".2")
        backup_1 = file_path.with_suffix(file_path.suffix + ".1")

        if backup_2.exists():
            backup_2.unlink()
        if backup_1.exists():
            backup_1.rename(backup_2)

        file_path.rename(backup_1)
        # Create fresh empty file
        file_path.touch()

        ts = datetime.datetime.now(datetime.timezone.utc).strftime('%H:%M:%S')
        print(f"[{ts}] Rotated {file_path.name} (was {size:,} bytes)")
    except OSError as e:
        ts = datetime.datetime.now(datetime.timezone.utc).strftime('%H:%M:%S')
        print(f"[{ts}] File rotation error: {e}")


async def websocket_handler(request):
    """Handle WebSocket connections from browser."""
    if len(connected_clients) >= MAX_CLIENTS:
        ts = datetime.datetime.now(datetime.timezone.utc).strftime('%H:%M:%S')
        print(f"[{ts}] Connection rejected: at capacity ({MAX_CLIENTS})")
        return web.Response(status=503, text="Server at capacity")

    ws = web.WebSocketResponse(max_msg_size=1*1024*1024)
    await ws.prepare(request)

    connected_clients.add(ws)
    ts = datetime.datetime.now(datetime.timezone.utc).strftime('%H:%M:%S')
    print(f"[{ts}] Client connected. Total: {len(connected_clients)}")

    # Send welcome message
    await ws.send_json({
        "type": "connected",
        "message": "Connected to Claude Collaborate Bridge",
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()
    })

    try:
        async for msg in ws:
            if msg.type == aiohttp.WSMsgType.TEXT:
                try:
                    data = json.loads(msg.data)
                    await handle_message(ws, data)
                except json.JSONDecodeError:
                    await ws.send_json({"type": "error", "message": "Invalid JSON"})
            elif msg.type == aiohttp.WSMsgType.ERROR:
                print(f"WebSocket error: {ws.exception()}")
    finally:
        connected_clients.discard(ws)
        ts = datetime.datetime.now(datetime.timezone.utc).strftime('%H:%M:%S')
        print(f"[{ts}] Client disconnected. Total: {len(connected_clients)}")

    return ws


async def handle_message(ws, data):
    """Process incoming messages from browser."""
    msg_type = data.get("type", "unknown")
    timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()

    if msg_type == "user_message":
        # User sent a message to Claude
        message = {
            "type": "user_message",
            "content": data.get("content", ""),
            "timestamp": timestamp,
            "source": "claude_collaborate"
        }

        # Append to message file for Claude Code to read (with lock)
        async with _message_file_lock:
            _rotate_file_if_needed(MESSAGE_FILE)
            with open(MESSAGE_FILE, "a", encoding="utf-8") as f:
                f.write(json.dumps(message) + "\n")

        # Acknowledge receipt
        await ws.send_json({
            "type": "message_received",
            "timestamp": timestamp,
            "content": data.get("content", "")[:50] + "..."
        })

        print(f"[{timestamp[:19]}] User: {data.get('content', '')[:80]}")

    elif msg_type == "ping":
        await ws.send_json({"type": "pong", "timestamp": timestamp})

    elif msg_type == "get_responses":
        # Check for Claude responses
        responses = await get_claude_responses()
        await ws.send_json({
            "type": "claude_responses",
            "responses": responses,
            "timestamp": timestamp
        })


async def get_claude_responses():
    """Read Claude responses from file."""
    responses = []
    async with _response_file_lock:
        if CLAUDE_RESPONSE_FILE.exists():
            try:
                with open(CLAUDE_RESPONSE_FILE, encoding="utf-8") as f:
                    for line in f:
                        if line.strip():
                            try:
                                responses.append(json.loads(line))
                            except json.JSONDecodeError as e:
                                now = datetime.datetime.now(datetime.timezone.utc)
                                ts = now.strftime('%H:%M:%S')
                                print(f"[{ts}] Skipping malformed response line: {e}")
                CLAUDE_RESPONSE_FILE.write_text("")
            except Exception as e:
                print(f"Error reading responses: {e}")
    return responses


async def broadcast_to_clients(message):
    """Send message to all connected clients."""
    clients = list(connected_clients)
    if clients:
        await asyncio.gather(
            *[client.send_json(message) for client in clients if not client.closed],
            return_exceptions=True
        )


# HTTP endpoints for Claude Code to use
async def post_response(request):
    """Endpoint for Claude Code to send responses to browser."""
    try:
        data = await request.json()
        message = {
            "type": "claude_response",
            "content": data.get("content", ""),
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()
        }

        # Broadcast to all connected browser clients
        await broadcast_to_clients(message)

        # Also save to file as backup (with lock and rotation)
        async with _response_file_lock:
            _rotate_file_if_needed(CLAUDE_RESPONSE_FILE)
            with open(CLAUDE_RESPONSE_FILE, "a", encoding="utf-8") as f:
                f.write(json.dumps(message) + "\n")

        return web.json_response({"status": "sent", "clients": len(connected_clients)})
    except Exception as e:
        ts = datetime.datetime.now(datetime.timezone.utc).strftime('%H:%M:%S')
        print(f"[{ts}] post_response error: {e}")
        return web.json_response(
            {"status": "error", "message": "Internal server error"}, status=500
        )


async def get_messages(request):
    """Endpoint for Claude Code to read user messages."""
    messages = []
    async with _message_file_lock:
        if MESSAGE_FILE.exists():
            try:
                with open(MESSAGE_FILE, encoding="utf-8") as f:
                    for line in f:
                        if line.strip():
                            try:
                                messages.append(json.loads(line))
                            except json.JSONDecodeError as e:
                                now = datetime.datetime.now(datetime.timezone.utc)
                                ts = now.strftime('%H:%M:%S')
                                print(f"[{ts}] Skipping malformed message line: {e}")
                MESSAGE_FILE.write_text("")
            except Exception as e:
                ts = datetime.datetime.now(datetime.timezone.utc).strftime('%H:%M:%S')
                print(f"[{ts}] get_messages error: {e}")
                return web.json_response(
                    {"status": "error", "message": "Internal server error"},
                    status=500,
                )

    return web.json_response({"messages": messages, "count": len(messages)})


async def health_check(request):
    """Health check endpoint."""
    return web.json_response({
        "status": "ok",
        "connected_clients": len(connected_clients),
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()
    })


def create_app():
    """Create the aiohttp application."""
    app = web.Application(client_max_size=1*1024*1024)

    # WebSocket route
    app.router.add_get("/ws", websocket_handler)

    # HTTP API routes for Claude Code
    app.router.add_post("/api/respond", post_response)
    app.router.add_get("/api/messages", get_messages)
    app.router.add_get("/health", health_check)

    # CORS middleware for browser access
    async def cors_middleware(app, handler):
        async def middleware(request):
            if request.method == "OPTIONS":
                return web.Response(headers={
                    "Access-Control-Allow-Origin": "http://localhost:8877",
                    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
                    "Access-Control-Allow-Headers": "Content-Type",
                })
            response = await handler(request)
            response.headers["Access-Control-Allow-Origin"] = "http://localhost:8877"
            return response
        return middleware

    app.middlewares.append(cors_middleware)

    return app


if __name__ == "__main__":
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║           Claude Collaborate WebSocket Bridge                 ║
╠══════════════════════════════════════════════════════════════╣
║  WebSocket: ws://localhost:{WS_PORT}/ws                         ║
║  HTTP API:  http://localhost:{WS_PORT}/api/messages (GET)       ║
║             http://localhost:{WS_PORT}/api/respond (POST)       ║
║  Health:    http://localhost:{WS_PORT}/health                   ║
╚══════════════════════════════════════════════════════════════╝

For Claude Code, use these commands:
  - Read messages:  curl http://localhost:{WS_PORT}/api/messages
  - Send response:  curl -X POST http://localhost:{WS_PORT}/api/respond \\
                      -H "Content-Type: application/json" \\
                      -d '{{"content": "Hello from Claude!"}}'
""")

    app = create_app()
    web.run_app(app, host="127.0.0.1", port=WS_PORT, print=None)
