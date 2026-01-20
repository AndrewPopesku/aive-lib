# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AIVE is a video automation framework for Python and LLMs. It provides both a Python library API and an MCP (Model Context Protocol) server for LLM-controlled video editing.

## Development Commands

### Testing
```bash
# Run all tests
uv run pytest

# Run specific test file
uv run pytest tests/test_models.py

# Run with verbose output
uv run pytest -v

# Verify installation
uv run python test_installation.py
```

### Code Quality
```bash
# Format code with Black
uv run black src/ tests/ examples/

# Lint with Ruff
uv run ruff check src/ tests/ examples/
```

### Running Examples
```bash
# Run example scripts
uv run python examples/basic_video.py
uv run python examples/tiktok_automation.py

# Start MCP server (for LLM integration)
uv run aive-server
```

### Development Setup
```bash
# Install with dev dependencies
uv sync --dev
```

## Architecture

### Core Design Principles

1. **Separation of Concerns**: The architecture separates core business logic from interfaces (Python API and MCP server)
2. **Action Registry Pattern**: All editing operations use a registry pattern for extensibility
3. **Storage Abstraction**: Pluggable storage backends (JSON file-based and in-memory)
4. **Type Safety**: Pydantic models throughout for validation and serialization
5. **Stateful Manager**: `VideoProjectManager` maintains project state and coordinates between components

### Key Components

**VideoProjectManager** ([manager.py](src/aive/manager.py))
- Central orchestrator that coordinates all components
- Maintains current project state (`self.project: Optional[ProjectState]`)
- Delegates to specialized components (storage, renderer, actions, templates, assets)
- Provides high-level API for both Python and MCP interfaces

**Data Models** ([models.py](src/aive/models.py))
- `ProjectState`: Complete project state with clips, resolution, fps, background color
- `Clip`: Individual media clip with source, timing, effects, volume
- `Effect`: Video effect with type and parameters
- All models use Pydantic for validation and JSON serialization

**Action Registry** ([engine/actions.py](src/aive/engine/actions.py))
- Registry pattern for video editing operations
- Actions are pure functions: `(ProjectState, **kwargs) -> ProjectState`
- Built-in actions: add_clip, remove_clip, trim_clip, apply_effect, set_volume, crop_vertical
- Add new actions by decorating with `@ActionRegistry.register("name")`

**Storage Layer** ([storage/](src/aive/storage/))
- Abstract interface with two implementations:
  - `JSONStore`: File-based persistence
  - `MemoryStore`: In-memory storage for testing
- Manager selects backend via `storage_backend` parameter

**Renderer** ([engine/renderer.py](src/aive/engine/renderer.py))
- MoviePy-based rendering engine
- Handles multi-layer composition based on track_layer
- Applies effects (fade, crop, resize) to clips
- Configurable codec and preset for rendering

**Template System** ([utils/templates.py](src/aive/utils/templates.py))
- Templates are JSON files defining project presets
- Located in `templates/` directory
- Built-in: tiktok_vertical, youtube_landscape, edu_landscape
- Templates define resolution, fps, background_color, and optional initial clips

**MCP Server** ([server/mcp_agent.py](src/aive/server/mcp_agent.py))
- Exposes 10 MCP tools for LLM control
- Creates singleton `VideoProjectManager` instance
- Maps MCP tool calls to manager methods
- Entry point: `aive-server` command defined in pyproject.toml

### Data Flow

1. **Project Creation**: User creates project via manager → ProjectState created → stored in manager.project
2. **Adding Clips**: User calls add_clip → action registry executes add_clip action → ProjectState updated with new Clip
3. **Applying Effects**: User calls apply_action → ActionRegistry.execute() → action modifies ProjectState → returns updated state
4. **Rendering**: User calls render → Renderer reads ProjectState → composes clips by layer → applies effects → outputs video file
5. **Persistence**: User calls save_project → manager delegates to storage backend → ProjectState serialized to JSON

### Important Implementation Details

**Clip Layering**: Clips with higher `track_layer` values appear on top. Layer 1 is background, layer 2+ are overlays.

**Effect Application**: Effects are stored in `Clip.effects` list and applied during rendering, not immediately when added.

**Clip IDs**: Auto-generated using `uuid.uuid4().hex[:8]` if not provided. Used for referencing clips in actions.

**Source Validation**: Non-text clips validate that source files exist during Clip creation via Pydantic validator.

**Action Execution**: Actions receive current ProjectState and return modified ProjectState. They should NOT mutate the input state directly.

**Storage Backend Selection**: Determined in VideoProjectManager.__init__() via storage_backend parameter ("json" or "memory").

## Testing Strategy

- **Unit Tests**: Individual components (models, actions, storage)
- **Integration Tests**: Manager workflows (tests/test_manager.py)
- **Fixtures**: Use memory storage backend for fast, isolated tests
- **Coverage**: 34 tests covering all major functionality

## Adding New Features

### Adding a New Action

1. Define action function in [engine/actions.py](src/aive/engine/actions.py):
```python
@ActionRegistry.register("your_action")
def your_action(context: ProjectState, **kwargs) -> ProjectState:
    """Action description."""
    # Modify context (create new state, don't mutate)
    return context
```

2. Add tests in [tests/test_actions.py](tests/test_actions.py)

3. Update MCP server if needed to expose via LLM interface

### Adding a New Template

1. Create JSON file in `templates/your_template.json`:
```json
{
  "name": "Your Template",
  "resolution": [1920, 1080],
  "fps": 30,
  "clips": [],
  "background_color": [0, 0, 0]
}
```

2. Test with `manager.load_template("your_template")`

### Adding a New Storage Backend

1. Implement storage interface (see [storage/memory_store.py](src/aive/storage/memory_store.py) for example)
2. Methods needed: save_project, load_project, list_projects, delete_project, project_exists
3. Update VideoProjectManager.__init__() to support new backend
4. Add tests in [tests/test_storage.py](tests/test_storage.py)

## Common Pitfalls

**File Paths**: Always use absolute paths for media files. Pydantic validators check file existence for non-text clips.

**Layer Numbers**: track_layer must be >= 1. Higher numbers appear on top.

**Action State Management**: Actions must return a new/modified ProjectState, not mutate the input.

**Text vs Media Clips**: Text clips use source as content, other clips use source as file path.

**Manager State**: VideoProjectManager.project is None until create_project() or load_template() is called.

**Rendering Requirements**: Project must have at least one clip to render successfully.

## Code Style

- **Formatting**: Black with default settings (line length 88)
- **Linting**: Ruff for code quality
- **Type Hints**: Required for all function signatures
- **Docstrings**: Required for all public APIs (Google style)
- **Commit Messages**: Conventional commits format (feat:, fix:, docs:, test:, etc.)

## Key File References

- Main API: [manager.py](src/aive/manager.py) - VideoProjectManager class
- Data models: [models.py](src/aive/models.py) - ProjectState, Clip, Effect
- Actions: [engine/actions.py](src/aive/engine/actions.py) - ActionRegistry and built-in actions
- Rendering: [engine/renderer.py](src/aive/engine/renderer.py) - MoviePy integration
- MCP Server: [server/mcp_agent.py](src/aive/server/mcp_agent.py) - LLM integration
- Templates: [utils/templates.py](src/aive/utils/templates.py) - Template management
- Storage: [storage/json_store.py](src/aive/storage/json_store.py), [storage/memory_store.py](src/aive/storage/memory_store.py)

## Dependencies

- **moviepy** (>=2.2.1): Video rendering engine
- **pydantic** (>=2.12.5): Data validation and serialization
- **mcp** (>=1.25.0): Model Context Protocol for LLM integration
- **opencv-python** (>=4.12.0.88): Image processing
- **pillow** (>=11.3.0): Image handling

Dev dependencies: black, pytest, pytest-asyncio, ruff
