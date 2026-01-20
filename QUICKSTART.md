# AIVE Quick Start Guide

Get up and running with AIVE in 5 minutes!

## Installation

```bash
uv add aive
```

## 30-Second Test

Verify installation works:

```bash
uv run python test_installation.py
```

You should see: `✅ All tests passed! AIVE is ready to use! 🎬`

## Your First Video (5 minutes)

### Step 1: Create a Simple Video

Create a file `my_first_video.py`:

```python
from aive import VideoProjectManager

# Create manager
manager = VideoProjectManager()

# Create a project
manager.create_project(
    name="My First Video",
    resolution=(1920, 1080),
    fps=30
)

# Add a text clip (no external files needed!)
manager.add_clip(
    clip_type="text",
    source="Hello aive!",
    duration=5.0
)

# Render it
manager.render("my_first_video.mp4")
print("Done! Check my_first_video.mp4")
```

Run it:
```bash
uv run python my_first_video.py
```

### Step 2: Use a Template

```python
from aive import VideoProjectManager

manager = VideoProjectManager()

# Load TikTok template (vertical, 1080x1920)
manager.load_template("tiktok_vertical")

# Add your content
manager.add_clip(
    clip_type="text",
    source="TikTok Ready!",
    duration=10.0
)

manager.render("tiktok_video.mp4")
```

### Step 3: Add Real Media

```python
from aive import VideoProjectManager

manager = VideoProjectManager()
manager.create_project("Real Video", (1920, 1080), 30)

# Add a video file
manager.add_clip(
    clip_type="video",
    source="my_video.mp4",  # Your video file
    duration=10.0,
    start=0.0
)

# Add text overlay
manager.add_clip(
    clip_type="text",
    source="Check this out!",
    duration=3.0,
    start=2.0,
    track_layer=2  # Layer 2 = on top
)

# Crop to vertical for TikTok
clip_id = manager.project.clips[0].id
manager.apply_action("crop_vertical", clip_id=clip_id)

manager.render("final_video.mp4")
```

## Common Tasks

### Add Multiple Clips

```python
# Background video
manager.add_clip("video", "bg.mp4", duration=20.0, start=0.0, track_layer=1)

# Music
manager.add_clip("audio", "music.mp3", duration=20.0, start=0.0, track_layer=2)

# Title
manager.add_clip("text", "My Video", duration=5.0, start=0.0, track_layer=3)
```

### Apply Effects

```python
# Get clip ID
clip_id = manager.project.clips[0].id

# Add fade
manager.apply_action(
    "apply_effect",
    clip_id=clip_id,
    effect_type="fade",
    parameters={"fade_in": 1.0, "fade_out": 1.0}
)

# Adjust volume
manager.apply_action("set_volume", clip_id=clip_id, volume=0.5)
```

### Save and Load

```python
# Save your work
manager.save_project("my_project.json")

# Load it later
manager2 = VideoProjectManager()
manager2.load_project("my_project.json")
```

### Check Project Info

```python
info = manager.get_project_info()
print(f"Duration: {info['total_duration']}s")
print(f"Clips: {info['num_clips']}")
print(f"Resolution: {info['resolution']}")
```

## Use with Claude (MCP)

### Setup

1. Install aive:
```bash
uv add aive
```

2. Edit Claude Desktop config:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "aive": {
      "command": "aive-server"
    }
  }
}
```

3. Restart Claude Desktop

### Use It

Talk to Claude:

> "I have a video called vacation.mp4. Can you crop it to TikTok vertical format and add the title 'Summer 2025' at the start?"

Claude will:
1. Load the TikTok template
2. Add your video
3. Crop it to 9:16
4. Add the title text
5. Render it for you

## Tips

1. **Start Simple**: Begin with text-only videos (no external files needed)
2. **Use Templates**: Don't create from scratch - load a template
3. **Test Fast**: Use `preset="ultrafast"` for quick tests
4. **Save Often**: Use `save_project()` to save your work
5. **Check Info**: Use `get_project_info()` before rendering

## Troubleshooting

### Issue: "No module named 'aive'"
**Solution**: Install with `uv add aive`

### Issue: "Source file does not exist"
**Solution**: Use absolute paths or check file exists:
```python
from pathlib import Path
path = Path("my_video.mp4").absolute()
print(f"File exists: {path.exists()}")
```

### Issue: Rendering is slow
**Solution**: Use faster preset:
```python
manager.render("output.mp4", preset="ultrafast")
```

### Issue: Text clip doesn't appear
**Solution**: Ensure text clips are on higher layers:
```python
manager.add_clip(..., track_layer=2)  # Higher = on top
```

## Next Steps

1. **Examples**: Check `examples/` directory for more
2. **Documentation**: Read the full README.md
3. **API Reference**: Check docstrings in the code
4. **Community**: Open discussions on GitHub

## Complete Working Example

```python
#!/usr/bin/env python3
"""Complete working example - copy and run this!"""

from aive import VideoProjectManager

def main():
    # Create manager
    manager = VideoProjectManager()
    
    # Load template
    manager.load_template("youtube_landscape")
    
    # Add content (text-only, no files needed)
    manager.add_clip(
        clip_type="text",
        source="Welcome to aive!",
        duration=3.0,
        start=0.0
    )
    
    manager.add_clip(
        clip_type="text",
        source="Easy video automation",
        duration=3.0,
        start=3.0
    )
    
    manager.add_clip(
        clip_type="text",
        source="for Python developers",
        duration=3.0,
        start=6.0
    )
    
    # Add fade to all clips
    for clip in manager.project.clips:
        manager.apply_action(
            "apply_effect",
            clip_id=clip.id,
            effect_type="fade",
            parameters={"fade_in": 0.5, "fade_out": 0.5}
        )
    
    # Info
    info = manager.get_project_info()
    print(f"\nCreating video with {info['num_clips']} clips")
    print(f"Total duration: {info['total_duration']}s")
    
    # Render
    print("\nRendering...")
    manager.render("demo_video.mp4", preset="fast")
    print("✅ Done! Check demo_video.mp4")

if __name__ == "__main__":
    main()
```

Save as `demo.py` and run:
```bash
uv run python demo.py
```

---

**You're ready to create videos with aive!** 🎬

Need help? Check the examples or open an issue on GitHub.
