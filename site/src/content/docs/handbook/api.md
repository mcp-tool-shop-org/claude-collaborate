---
title: API Reference
description: WebSocket protocol, REST endpoints, and Claude Code integration.
sidebar:
  order: 3
---

claude-collaborate exposes a WebSocket connection for real-time browser communication and a set of REST endpoints for Claude Code integration.

## WebSocket protocol

Connect to `ws://localhost:8877/ws` from the browser or any WebSocket client. The protocol uses JSON messages with a `type` field.

### Message types

**`user_message`** -- Sent from the browser to Claude Code when the user types in the chat panel.

```json
{
  "type": "user_message",
  "content": "Can you help me refactor this component?"
}
```

**`claude_response`** -- Sent from Claude Code back to the browser.

```json
{
  "type": "claude_response",
  "content": "Sure! Let me look at the structure first."
}
```

**`connected`** -- Sent by the server when a WebSocket client connects successfully.

```json
{
  "type": "connected",
  "message": "WebSocket connection established"
}
```

## REST endpoints

The REST API lets Claude Code interact with the WebSocket bridge without maintaining a persistent connection.

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/ws/messages` | Read pending messages sent from the browser UI. Returns an array of messages and clears the queue. |
| `POST` | `/api/ws/respond` | Send a response from Claude back to the browser. Body: `{"content": "..."}` |
| `GET` | `/api/ws/status` | Check WebSocket bridge connection status. Returns connected client count and bridge state. |
| `GET` | `/health` | Server health check. Returns server uptime and version info. |
| `WS` | `/ws` | Direct WebSocket connection for real-time bidirectional messaging. |

## Claude Code integration

### Read messages

Poll for new messages from the browser. Each call returns all pending messages and clears the queue.

```bash
curl http://localhost:8877/api/ws/messages
```

Example response:

```json
[
  {
    "type": "user_message",
    "content": "Draw a box around the header",
    "timestamp": "2026-03-05T10:30:00Z"
  }
]
```

### Send a response

Push a response back to the browser. The message appears in the chat panel immediately.

```bash
curl -X POST http://localhost:8877/api/ws/respond \
  -H "Content-Type: application/json" \
  -d '{"content": "Done! I added a 2px border around the header element."}'
```

### Check bridge status

Verify the WebSocket bridge is running and clients are connected.

```bash
curl http://localhost:8877/api/ws/status
```

Example response:

```json
{
  "connected_clients": 1,
  "bridge_active": true
}
```

### Health check

Confirm the server is up and responding.

```bash
curl http://localhost:8877/health
```

## Integration pattern

A typical Claude Code integration loop:

1. **Poll** `/api/ws/messages` to check for new user messages
2. **Process** the message content (generate code, analyze a drawing, suggest a move)
3. **Respond** via `POST /api/ws/respond` with the result
4. **Repeat** -- the browser user sees the response instantly and can continue the conversation
