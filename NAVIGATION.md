# AIVE Navigation Guide

Quick reference for finding what you need in the AIVE codebase.

## 📁 Directory Structure

```
aive/
├── src/aive/              # Main package (THE CORE)
├── tests/                    # Test suite (VERIFY IT WORKS)
├── examples/                 # Usage examples (LEARN BY EXAMPLE)
├── templates/                # Project templates (READY-TO-USE)
└── Documentation files       # Guides & info (READ FIRST)
```

## 🔍 Finding What You Need

### "I want to understand the architecture"
→ Read: `PROJECT_SUMMARY.md`
→ Look at: `src/aive/` directory structure

### "I want to get started quickly"
→ Read: `QUICKSTART.md`
→ Run: `test_installation.py`
→ Try: `examples/basic_video.py`

### "I want to use it as a Python library"
→ Read: `README.md` (Quick Start section)
→ Examples: All files in `examples/`
→ API Docs: Docstrings in `src/aive/manager.py`

### "I want to use it with Claude (MCP)"
→ Read: `examples/mcp_usage.md`
→ Server code: `src/aive/server/mcp_agent.py`
→ Setup: `README.md` (MCP section)

### "I want to contribute"
→ Read: `CONTRIBUTING.md`
→ Tests: `tests/` directory
→ Run: `uv run pytest`

### "I want to understand the data models"
→ Look at: `src/aive/models.py` (Pydantic models)
→ Tests: `tests/test_models.py`

### "I want to add new actions"
→ Look at: `src/aive/engine/actions.py`
→ Example: See existing actions like `crop_vertical`
→ Register: Use `@ActionRegistry.register("name")`

### "I want to create templates"
→ Look at: `templates/*.json`
→ Code: `src/aive/utils/templates.py`
→ Example: `templates/tiktok_vertical.json`

## 📄 Key Files Explained

### Core Library

| File | Purpose | Use When |
|------|---------|----------|
| `src/aive/models.py` | Data structures | Understanding project/clip structure |
| `src/aive/manager.py` | Main API | Using the library |
| `src/aive/errors.py` | Exceptions | Error handling |
| `src/aive/__init__.py` | Package exports | Importing from aive |

### Engine

| File | Purpose | Use When |
|------|---------|----------|
| `src/aive/engine/actions.py` | Action registry | Adding new editing operations |
| `src/aive/engine/renderer.py` | Video rendering | Understanding rendering pipeline |

### Storage

| File | Purpose | Use When |
|------|---------|----------|
| `src/aive/storage/json_store.py` | File persistence | Saving/loading projects |
| `src/aive/storage/memory_store.py` | In-memory storage | Testing or temporary projects |

### Utilities

| File | Purpose | Use When |
|------|---------|----------|
| `src/aive/utils/templates.py` | Template management | Working with templates |
| `src/aive/utils/assets.py` | Asset handling | Managing media files |

### MCP Server

| File | Purpose | Use When |
|------|---------|----------|
| `src/aive/server/mcp_agent.py` | MCP server | Using with Claude/LLMs |

### Tests

| File | Purpose | Use When |
|------|---------|----------|
| `tests/test_models.py` | Model tests | Understanding data validation |
| `tests/test_actions.py` | Action tests | Understanding available actions |
| `tests/test_storage.py` | Storage tests | Understanding persistence |
| `tests/test_manager.py` | Integration tests | Understanding workflows |

### Examples

| File | Purpose | Use When |
|------|---------|----------|
| `examples/basic_video.py` | Basic usage | Learning fundamentals |
| `examples/tiktok_automation.py` | TikTok videos | Creating vertical content |
| `examples/educational_video.py` | Educational content | Multi-part videos with narration |
| `examples/mcp_usage.md` | Claude integration | Using with AI |

### Documentation

| File | Purpose | Use When |
|------|---------|----------|
| `README.md` | Main docs | First time using the library |
| `QUICKSTART.md` | Quick start | Want to try it in 5 minutes |
| `PROJECT_SUMMARY.md` | Complete overview | Understanding the whole project |
| `CONTRIBUTING.md` | Contribution guide | Want to contribute |
| `NAVIGATION.md` | This file | Finding your way around |

## 🎯 Common Tasks → Files

### Creating Videos
1. Start: `examples/basic_video.py`
2. API: `src/aive/manager.py` → `VideoProjectManager`
3. Models: `src/aive/models.py` → `ProjectState`, `Clip`

### Adding Effects
1. Actions: `src/aive/engine/actions.py` → existing actions
2. Rendering: `src/aive/engine/renderer.py` → effect application
3. Example: `examples/basic_video.py` → fade effect

### Storage
1. Interface: `src/aive/manager.py` → save/load methods
2. Implementation: `src/aive/storage/json_store.py`
3. Tests: `tests/test_storage.py`

### Templates
1. Examples: `templates/*.json`
2. Manager: `src/aive/utils/templates.py`
3. Usage: `examples/tiktok_automation.py`

### MCP/Claude
1. Guide: `examples/mcp_usage.md`
2. Server: `src/aive/server/mcp_agent.py`
3. Tools: See `@app.list_tools()` in mcp_agent.py

## 💡 Learning Path

### Beginner
1. Read `QUICKSTART.md`
2. Run `test_installation.py`
3. Try `examples/basic_video.py`
4. Read docstrings in `manager.py`

### Intermediate
1. Study `src/aive/models.py`
2. Explore `examples/tiktok_automation.py`
3. Read `tests/test_manager.py`
4. Experiment with templates

### Advanced
1. Study `src/aive/engine/actions.py`
2. Understand `src/aive/engine/renderer.py`
3. Create custom actions
4. Contribute to the project

### AI/MCP User
1. Read `examples/mcp_usage.md`
2. Configure Claude Desktop
3. Try example conversations
4. Explore MCP tools in `mcp_agent.py`

## 🔧 Development Tasks → Files

### Running Tests
- Command: `uv run pytest`
- Config: `pyproject.toml`
- Tests: `tests/*.py`

### Adding Features
- Models: `src/aive/models.py`
- Actions: `src/aive/engine/actions.py`
- Tests: `tests/test_*.py`

### Fixing Bugs
- Find tests: `tests/`
- Find code: `src/aive/`
- Run: `uv run pytest -v`

### Documentation
- Main: `README.md`
- Examples: `examples/`
- Docstrings: All `.py` files in `src/`

## 📞 Getting Help

### Documentation Issues
→ Check `README.md` and `QUICKSTART.md`

### Installation Issues
→ Run `test_installation.py`
→ Check `pyproject.toml` for dependencies

### Usage Issues
→ Check `examples/` directory
→ Read docstrings in code

### Bug Reports
→ See `CONTRIBUTING.md`
→ Check existing tests in `tests/`

### Feature Requests
→ See `CONTRIBUTING.md`
→ Look at `src/aive/engine/actions.py` for patterns

---

**Pro Tip**: Use your IDE's "Go to Definition" feature to navigate from usage to implementation quickly!
