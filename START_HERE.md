# 🎬 START HERE - Moviely

Welcome to Moviely! This is your starting point.

## What is Moviely?

Moviely is a **video automation framework** that lets you:
- Create videos programmatically with Python
- Edit videos using natural language with Claude (AI)
- Build automated video pipelines
- Generate TikTok, YouTube, and educational content

## 🚀 Try It Right Now (3 Steps)

### Step 1: Install
```bash
cd moviely
uv run python test_installation.py
```

Expected output:
```
✅ All tests passed!
Moviely is ready to use! 🎬
```

### Step 2: Run Your First Example
```bash
uv run python -c "
from moviely import VideoProjectManager

manager = VideoProjectManager(storage_backend='memory')
manager.create_project('First Video', (1920, 1080), 30)
manager.add_clip('text', 'Hello Moviely!', duration=5.0)
print('✓ Created a 5-second video project!')
print(f'Project info: {manager.get_project_info()}')
"
```

### Step 3: Check Out Examples
```bash
ls examples/
# basic_video.py
# tiktok_automation.py  
# educational_video.py
# mcp_usage.md
```

## 📚 What to Read Next

**Choose your path:**

### Path A: Python Developer
1. Read: [QUICKSTART.md](QUICKSTART.md) (5 minutes)
2. Try: [examples/basic_video.py](examples/basic_video.py)
3. Explore: [README.md](README.md) (full docs)

### Path B: Using with Claude (AI)
1. Read: [examples/mcp_usage.md](examples/mcp_usage.md)
2. Configure: Claude Desktop with moviely-server
3. Start chatting: "Convert my video to TikTok format"

### Path C: Contributing
1. Read: [CONTRIBUTING.md](CONTRIBUTING.md)
2. Run tests: `uv run pytest`
3. Explore: [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)

## 🎯 Quick Examples

### Create a TikTok Video
```python
from moviely import VideoProjectManager

manager = VideoProjectManager()
manager.load_template("tiktok_vertical")
manager.add_clip("text", "Check this out! 👀", duration=3.0)
# Add your video, effects, etc.
# manager.render("tiktok.mp4")
```

### Add Multiple Clips
```python
manager.create_project("My Video", (1920, 1080), 30)
manager.add_clip("video", "intro.mp4", duration=5.0, start=0.0)
manager.add_clip("text", "Welcome!", duration=3.0, start=1.0, track_layer=2)
manager.add_clip("audio", "music.mp3", duration=30.0, start=0.0)
```

### Apply Effects
```python
clip_id = manager.project.clips[0].id
manager.apply_action("apply_effect", 
    clip_id=clip_id,
    effect_type="fade",
    parameters={"fade_in": 1.0, "fade_out": 1.0}
)
```

## 📁 Project Structure

```
moviely/
├── src/moviely/          # Core library (import from here)
├── tests/                # Test suite (all passing ✓)
├── examples/             # Learn by example
├── templates/            # Ready-to-use templates
├── README.md             # Full documentation
├── QUICKSTART.md         # 5-minute guide
└── START_HERE.md         # You are here!
```

## 🆘 Need Help?

**Common Questions:**

Q: How do I render a video?
```python
manager.render("output.mp4")
```

Q: How do I save my project?
```python
manager.save_project("my_project.json")
```

Q: How do I load a project?
```python
manager.load_project("my_project.json")
```

Q: What actions are available?
```python
print(manager.list_actions())
# ['add_clip', 'remove_clip', 'trim_clip', 'apply_effect', 'set_volume', 'crop_vertical']
```

Q: What templates exist?
```python
print(manager.list_templates())
# ['tiktok_vertical', 'youtube_landscape', 'edu_landscape']
```

## 🎓 Learning Resources

| Resource | What It's For | Time |
|----------|--------------|------|
| [QUICKSTART.md](QUICKSTART.md) | Get started fast | 5 min |
| [README.md](README.md) | Complete documentation | 15 min |
| [examples/basic_video.py](examples/basic_video.py) | Basic concepts | 5 min |
| [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) | Architecture overview | 10 min |
| [NAVIGATION.md](NAVIGATION.md) | Find your way around | 3 min |

## ✅ Verify Installation

Run all tests:
```bash
uv run pytest -v
```

Should see:
```
35 tests passed ✓
```

## 🚦 Next Steps

1. ✅ You've installed Moviely
2. ⏭️ Run [test_installation.py](test_installation.py)
3. ⏭️ Read [QUICKSTART.md](QUICKSTART.md)
4. ⏭️ Try [examples/basic_video.py](examples/basic_video.py)
5. ⏭️ Build something awesome!

---

**Ready?** Start with [QUICKSTART.md](QUICKSTART.md) →

**Questions?** Check [README.md](README.md) →

**Contributing?** See [CONTRIBUTING.md](CONTRIBUTING.md) →

**Lost?** Read [NAVIGATION.md](NAVIGATION.md) →

---

🎬 **Happy video editing with Moviely!**
