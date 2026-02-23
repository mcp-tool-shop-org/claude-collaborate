# Claude Collaborate

> *Where Human Creativity Meets AI Intelligence*

Claude Collaborate is a unified sandbox environment for real-time human-AI collaboration. It brings together interactive workspaces, seamless communication, and creative tools in one beautiful interface.

![Claude Collaborate](https://img.shields.io/badge/Claude-Collaborate-cc785c?style=for-the-badge&logo=anthropic)
![Python](https://img.shields.io/badge/Python-3.10+-3776ab?style=for-the-badge&logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

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

## 📄 License

MIT License - See [LICENSE](LICENSE) for details.

## 🙏 Acknowledgments

- **Anthropic** - For Claude and the vision of helpful AI
- **The Community** - For pushing the boundaries of human-AI collaboration

---

<p align="center">
  <i>Built with ❤️ for the future of collaboration</i><br>
  <a href="https://github.com/mcp-tool-shop-org">MCP Tool Shop</a>
</p>
