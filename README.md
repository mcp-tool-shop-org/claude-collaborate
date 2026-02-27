<p align="center">
  <a href="README.md">English</a> | <a href="README.ja.md">日本語</a> | <a href="README.zh.md">中文</a> | <a href="README.es.md">Español</a> | <a href="README.fr.md">Français</a> | <a href="README.hi.md">हिन्दी</a> | <a href="README.it.md">Italiano</a> | <a href="README.pt-BR.md">Português (BR)</a>
</p>

<p align="center">
  <img src="https://raw.githubusercontent.com/mcp-tool-shop-org/brand/main/logos/claude-collaborate/readme.png" alt="Claude Collaborate" width="400" />
</p>

<p align="center">
  <a href="https://github.com/mcp-tool-shop-org/claude-collaborate/actions/workflows/ci.yml"><img src="https://github.com/mcp-tool-shop-org/claude-collaborate/actions/workflows/ci.yml/badge.svg" alt="CI"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-green" alt="License"></a>
  <a href="https://mcp-tool-shop-org.github.io/claude-collaborate/"><img src="https://img.shields.io/badge/Landing_Page-live-blue" alt="Landing Page"></a>
</p>

> *Where Human Creativity Meets AI Intelligence*

Claude Collaborate is a unified sandbox environment for real-time human-AI collaboration. It brings together interactive workspaces, seamless communication, and creative tools in one beautiful interface.

## ✨ The Vision

Imagine a workspace where you can:
- **Draw and brainstorm** on a shared whiteboard
- **Write code together** with instant preview
- **Play chess** and discuss strategy
- **Create content** with GitHub-ready tools
- **Communicate in real-time** via WebSocket bridge

All in one place. All beautifully integrated.

## 🚀 Quick Start

```bash
# Clone the repository
git clone https://github.com/mcp-tool-shop-org/claude-collaborate.git
cd claude-collaborate

# Install dependencies
pip install aiohttp

# Start the server
python server.py

# Open in browser
# http://localhost:8877
```

## 🎨 Environments

| Environment | Description |
|-------------|-------------|
| **Whiteboard** | Draw, sketch, and brainstorm visually |
| **Code Workshop** | HTML/CSS/JS editor with live preview |
| **Chess Workshop** | Strategy and tactics playground |
| **Capture Viewer** | Screenshots and recordings viewer |
| **GitHub Toolkit** | README and marketing generators |
| **Creative Lab** | Interactive experiments |
| **Template** | Starter for creating new environments |

## 🏗️ Architecture

```
claude-collaborate/
├── index.html           # Main UI with environment switcher
├── server.py            # aiohttp server
├── ws_bridge.py         # WebSocket bridge for Claude Code
├── whiteboard.html      # Drawing and brainstorming
├── code-playground.html # Live HTML/CSS/JS editor
├── chess.html           # Chess analysis board
├── capture-viewer.html  # Screenshot/recording viewer
├── github-toolkit.html  # README and marketing tools
├── template.html        # Starter for new environments
└── adventures/          # Creative Lab experiments
    └── index.html
```

## 🔌 WebSocket Protocol

Claude Collaborate includes a WebSocket bridge for real-time communication with Claude Code:

```javascript
// Browser sends to Claude
{ "type": "user_message", "content": "Hello!" }

// Claude responds
{ "type": "claude_response", "content": "Hi there!" }

// Connection status
{ "type": "connected", "message": "Connected to Claude Collaborate Bridge" }
```

## 🔗 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Main Claude Collaborate UI |
| `/{file}` | GET | Static files (whiteboard, etc.) |
| `/ws` | WS | WebSocket bridge |
| `/api/ws/messages` | GET | Read pending user messages |
| `/api/ws/respond` | POST | Send response to browser |
| `/api/ws/status` | GET | WebSocket bridge status |
| `/health` | GET | Server health check |

## 💬 For Claude Code Users

Integrate with Claude Collaborate via the WebSocket bridge:

```bash
# Read messages from the UI
curl http://localhost:8877/api/ws/messages

# Send a response back
curl -X POST http://localhost:8877/api/ws/respond \
  -H "Content-Type: application/json" \
  -d '{"content": "Hello from Claude!"}'
```

## 🎭 Optional: Voice Integration

Claude Collaborate works beautifully with [Voice Soundboard](https://github.com/mcp-tool-shop-org/voice-soundboard) for TTS:

```bash
# In another terminal, start Voice Soundboard
cd voice-soundboard
python -m voice_soundboard.web_server

# Voice Studio will be available at http://localhost:8080/studio
```

## 🛠️ Creating New Environments

1. Copy `template.html` to `your-environment.html`
2. Add it to the sidebar in `index.html`:
```html
<div class="env-item" data-url="/your-environment.html" data-name="Your Environment">
    <div class="env-icon" style="background: linear-gradient(...);">🎯</div>
    <div class="env-info">
        <h3>Your Environment</h3>
        <p>Description</p>
    </div>
</div>
```
3. Refresh and start building!

## 📋 Requirements

- Python 3.10+
- aiohttp
- Modern browser with WebSocket support

## 🤝 Contributing

We welcome contributions! Whether it's:
- New environment templates
- UI/UX improvements
- Bug fixes
- Documentation

Please open an issue or submit a PR.

## Security & Data Scope

Claude Collaborate is a **local-first collaboration sandbox** — no telemetry, no cloud services, no persistence.

- **Data accessed:** Serves static HTML/JS files from the project directory. WebSocket bridge relays messages between browser and Claude Code in-memory only.
- **Data NOT accessed:** No telemetry. No cloud services. No credential storage. No database. Messages are ephemeral (lost on server restart).
- **Permissions required:** Network listen on localhost (default port 8877). File system read for static assets.

See [SECURITY.md](SECURITY.md) for vulnerability reporting.

---

## Scorecard

| Category | Score |
|----------|-------|
| Security | 10/10 |
| Error Handling | 10/10 |
| Operator Docs | 10/10 |
| Shipping Hygiene | 10/10 |
| Identity | 10/10 |
| **Overall** | **50/50** |

---

## 📄 License

MIT License - See [LICENSE](LICENSE) for details.

---

Built by <a href="https://mcp-tool-shop.github.io/">MCP Tool Shop</a>
