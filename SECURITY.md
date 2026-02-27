# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| 1.0.x   | Yes       |
| < 1.0   | No        |

## Reporting a Vulnerability

**Email:** 64996768+mcp-tool-shop@users.noreply.github.com

Please include:
- Description of the vulnerability
- Steps to reproduce
- Potential impact

**Response timeline:**
- Acknowledgment: within 48 hours
- Assessment: within 7 days
- Fix (if confirmed): within 30 days

## Scope

Claude Collaborate is a **local-first collaboration sandbox** with a Python web server and WebSocket bridge.
- **Data accessed:** Serves static HTML/JS files from the project directory. WebSocket bridge relays messages between browser and Claude Code. All data stays in-process memory — no persistence layer.
- **Data NOT accessed:** No telemetry. No cloud services. No credential storage. No database. Messages are ephemeral (in-memory only, lost on server restart).
- **Permissions required:** Network listen on localhost (default port 8877). File system read for static assets in the project directory. No write access required.
