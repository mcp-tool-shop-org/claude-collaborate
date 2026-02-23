# Changelog

All notable changes to Claude Collaborate will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.0.1] - 2026-02-23

### Fixed
- Return type annotations in `server.py` (`FileResponse` vs `Response` mismatch)
- Unused import (`asyncio`) and f-strings without placeholders in `server.py`
- Unused variable in test file
- Repository URLs pointing to wrong GitHub org

### Added
- CI workflow with ruff lint, mypy type checking, and pytest (Python 3.11 + 3.12)
- Ruff configuration (`ruff.toml`) with expanded rule set
- pytest configuration (`pytest.ini`) for async test mode

### Changed
- Modernized type annotations (`Set` → `set` via `from __future__ import annotations`)
- Updated `softprops/action-gh-release` from v1 to v2 in publish workflow

## [1.0.0] - 2026-01-24

### Added
- **Main Interface** - Environment switcher with unified navigation
- **Whiteboard** - Interactive drawing and brainstorming canvas
- **Code Workshop** - HTML/CSS/JS editor with live preview
- **Chess Workshop** - Strategy and tactics playground
- **Capture Viewer** - Screenshots and recordings viewer
- **GitHub Toolkit** - README and marketing generators
- **Creative Lab** - Interactive experiments
- **Template** - Starter for creating new environments
- **WebSocket Bridge** - Real-time communication with Claude Code
- **aiohttp Server** - Lightweight Python web server

### Infrastructure
- GitHub repository setup
- MIT License

---

## Version History

| Version | Date | Highlights |
|---------|------|------------|
| 1.0.1 | 2026-02-23 | CI, lint fixes, URL corrections |
| 1.0.0 | 2026-01-24 | Initial release |

[Unreleased]: https://github.com/mcp-tool-shop-org/claude-collaborate/compare/v1.0.1...HEAD
[1.0.1]: https://github.com/mcp-tool-shop-org/claude-collaborate/compare/v1.0.0...v1.0.1
[1.0.0]: https://github.com/mcp-tool-shop-org/claude-collaborate/releases/tag/v1.0.0
