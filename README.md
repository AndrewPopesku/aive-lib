# AIVE

**Video automation framework for Python and LLMs**

AIVE is a powerful video editing framework that can be used both as a Python library and through Large Language Models (LLMs) via MCP (Model Context Protocol). Perfect for automated video generation, TikTok creators, educational content, and more.

## Features

- **Dual Interface**: Use as a Python library or control via LLMs
- **Template System**: Pre-built templates for TikTok, YouTube, educational content
- **Action Registry**: Extensible system for video editing operations
- **Multiple Storage Backends**: JSON file storage or in-memory for testing
- **Type-Safe**: Built with Pydantic for robust data validation
- **Flexible Rendering**: MoviePy-powered rendering with customizable codecs

## Installation

```bash
# Using uv (recommended)
uv add aive

# Using pip
pip install aive
```

## Quick Start

### As a Python Library

```python
from aive import VideoProjectManager

# Create a manager
manager = VideoProjectManager()

# Load a template
manager.load_template("tiktok_vertical")

# Add clips
manager.add_clip(
    clip_type="video",
    source="path/to/video.mp4",
    duration=15.0,
    start=0.0
)

manager.add_clip(
    clip_type="text",
    source="Hello TikTok!",
    duration=3.0,
    start=0.0,
    track_layer=2
)

# Apply effects
clip_id = manager.project.clips[0].id
manager.apply_action("crop_vertical", clip_id=clip_id, target_aspect="9:16")

# Render
manager.render("output.mp4")
```

### As an MCP Server (for LLMs)

1. Install aive:
```bash
uv add aive
```

2. Configure your MCP client (e.g., Claude Desktop):
```json
{
  "mcpServers": {
    "aive": {
      "command": "aive-server"
    }
  }
}
```

3. Use with Claude:
```
"I have a video file called landscape.mp4. Can you crop it to TikTok vertical format?"
```

Claude will automatically:
- Load the appropriate template
- Add your video
- Apply the crop effect
- Render the output

## Templates

Built-in templates:

- **tiktok_vertical**: 1080x1920, 30fps, vertical format
- **youtube_landscape**: 1920x1080, 60fps, landscape format
- **edu_landscape**: 1920x1080, 30fps, white background

```python
# List available templates
manager.list_templates()

# Load a template
manager.load_template("youtube_landscape")

# Create custom template
manager.create_project(
    name="Custom",
    resolution=(1280, 720),
    fps=24
)
```

## Available Actions

- **add_clip**: Add video, audio, image, or text clips
- **remove_clip**: Remove a clip by ID
- **trim_clip**: Adjust clip duration and start time
- **apply_effect**: Add effects (fade, crop, resize)
- **set_volume**: Adjust audio volume (0.0 to 2.0)
- **crop_vertical**: Smart crop to vertical format

```python
# List all actions
manager.list_actions()

# Apply an action
manager.apply_action(
    "trim_clip",
    clip_id="clip_abc123",
    new_duration=10.0,
    new_start=2.0
)
```

## Advanced Usage

### Custom Effects

```python
manager.apply_action(
    "apply_effect",
    clip_id="clip_id",
    effect_type="fade",
    parameters={"fade_in": 1.0, "fade_out": 1.0}
)
```

### Layered Composition

```python
# Background video (layer 1)
manager.add_clip(
    clip_type="video",
    source="background.mp4",
    duration=30.0,
    track_layer=1
)

# Overlay text (layer 2)
manager.add_clip(
    clip_type="text",
    source="Title Text",
    duration=5.0,
    start=0.0,
    track_layer=2
)
```

### Save and Load Projects

```python
# Save project
manager.save_project("my_project.json")

# Load project
manager.load_project("my_project.json")

# Get project info
info = manager.get_project_info()
print(f"Duration: {info['total_duration']}s")
print(f"Clips: {info['num_clips']}")
```

### Custom Rendering Options

```python
manager.render(
    "output.mp4",
    codec="libx264",      # Video codec
    preset="medium"       # ultrafast, fast, medium, slow, veryslow
)
```

## Architecture

```
aive/
├── models.py           # Pydantic models (ProjectState, Clip, Effect)
├── manager.py          # Main VideoProjectManager class
├── engine/
│   ├── actions.py      # Action registry and built-in actions
│   └── renderer.py     # MoviePy rendering engine
├── storage/
│   ├── json_store.py   # File-based JSON storage
│   └── memory_store.py # In-memory storage (for testing)
├── utils/
│   ├── assets.py       # Asset management
│   └── templates.py    # Template system
└── server/
    └── mcp_agent.py    # MCP server for LLM integration
```

## Development

```bash
# Clone the repository
git clone https://github.com/yourusername/aive.git
cd aive

# Install with dev dependencies
uv sync --dev

# Run tests
uv run pytest

# Format code
uv run black src/ tests/

# Lint
uv run ruff check src/ tests/
```

## Examples

See the `examples/` directory for complete examples:

- `basic_video.py`: Simple video composition
- `tiktok_automation.py`: Automated TikTok video creation
- `educational_video.py`: Educational content with synced audio
- `mcp_usage.md`: Using aive with Claude

## Error Handling

```python
from aive.errors import aiveError, RenderError, InvalidActionError

try:
    manager.render("output.mp4")
except RenderError as e:
    print(f"Rendering failed: {e}")
except aiveError as e:
    print(f"General error: {e}")
```

## Requirements

- Python >= 3.10
- moviepy >= 2.0.0
- pydantic >= 2.0.0
- opencv-python >= 4.8.0
- mcp >= 1.0.0 (for MCP server functionality)

## License

MIT License - see LICENSE file for details

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## Support

- Documentation: https://aive.readthedocs.io
- Issues: https://github.com/yourusername/aive/issues
- Discussions: https://github.com/yourusername/aive/discussions

## Roadmap

- [ ] Additional effects (transitions, filters)
- [ ] Real-time preview support
- [ ] GPU-accelerated rendering
- [ ] Audio waveform visualization
- [ ] Advanced text styling
- [ ] Video stabilization
- [ ] Auto-captioning support
- [ ] Cloud storage integration

---

Built with ❤️ for content creators and developers
