# aive Examples

This directory contains example scripts demonstrating various use cases of aive.

## Examples

### 1. basic_video.py
**Basic video composition**

Learn the fundamentals:
- Creating a project from scratch
- Adding video and text clips
- Applying effects
- Rendering output

Run:
```bash
uv run python examples/basic_video.py
```

### 2. tiktok_automation.py
**Automated TikTok video creation**

Perfect for content creators:
- Using TikTok vertical template
- Smart cropping landscape to vertical
- Adding trendy text overlays
- Quick iteration with fast rendering

Run:
```bash
uv run python examples/tiktok_automation.py
```

### 3. educational_video.py
**Educational content creation**

For educators and trainers:
- Using educational template
- Syncing visuals with narration
- Creating chapter-based content
- High-quality rendering

Run:
```bash
uv run python examples/educational_video.py
```

### 4. mcp_usage.md
**Using aive with Claude (MCP)**

Natural language video editing:
- Setup instructions for MCP
- Example conversations with Claude
- Common workflows
- Troubleshooting tips

## Prerequisites

Before running the examples, make sure you have:

1. aive installed:
```bash
uv add aive
```

2. Sample media files (adjust paths in the examples):
   - Video files (.mp4, .mov, etc.)
   - Audio files (.mp3, .wav, etc.)
   - Image files (.png, .jpg, etc.)

## Modifying Examples

All examples are designed to be easily modified. Key things to customize:

1. **File paths**: Replace placeholder paths with your actual media files
2. **Durations**: Adjust clip durations to match your content
3. **Text**: Change text overlays to match your message
4. **Effects**: Experiment with different effects and parameters
5. **Resolution**: Change project resolution for different platforms

## Tips

- Start with `basic_video.py` to understand the core concepts
- Use `storage_backend="memory"` for quick testing without file I/O
- Try different render presets: `"ultrafast"` for testing, `"slow"` for production
- Check project info with `manager.get_project_info()` before rendering

## Need Help?

- Main documentation: See main README.md
- API reference: Check docstrings in the source code
- Issues: https://github.com/yourusername/aive/issues
