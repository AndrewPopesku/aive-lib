# Using Moviely with MCP (Claude)

This guide shows how to use Moviely through the MCP (Model Context Protocol) to control video editing via natural language with Claude.

## Setup

1. Install Moviely:
```bash
uv add moviely
```

2. Configure Claude Desktop to use the Moviely MCP server.

Edit your Claude Desktop config file:
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%/Claude/claude_desktop_config.json`

Add the moviely server:
```json
{
  "mcpServers": {
    "moviely": {
      "command": "moviely-server"
    }
  }
}
```

3. Restart Claude Desktop

## Example Conversations

### Creating a TikTok Video

**You**: I have a landscape video called `nature.mp4`. Can you convert it to TikTok vertical format and add a catchy title that says "Nature is Beautiful"?

**Claude**: I'll help you create a TikTok-ready vertical video. Let me:
1. Load the TikTok vertical template
2. Add your video
3. Crop it to 9:16 aspect ratio
4. Add the title text

[Claude uses the following MCP tools:]
- `load_template("tiktok_vertical")`
- `add_clip(clip_type="video", source="nature.mp4", duration=15.0)`
- `apply_action("crop_vertical", parameters={"clip_id": "...", "target_aspect": "9:16"})`
- `add_clip(clip_type="text", source="Nature is Beautiful", duration=5.0, track_layer=2)`
- `render_project(output_path="nature_tiktok.mp4")`

Your video is ready at `nature_tiktok.mp4`!

---

### Editing an Existing Project

**You**: Can you load my project called `my_video.json`, trim the first clip to 10 seconds, and add a fade effect?

**Claude**: I'll load your project and make those edits.

[Claude uses:]
- `load_project("my_video.json")`
- `get_project_info()` [to find the first clip ID]
- `apply_action("trim_clip", parameters={"clip_id": "...", "new_duration": 10.0})`
- `apply_action("apply_effect", parameters={"clip_id": "...", "effect_type": "fade", "parameters": {"fade_in": 1.0, "fade_out": 1.0}})`
- `save_project("my_video.json")`

Done! Your project has been updated with a 10-second trimmed clip and fade effects.

---

### Creating an Educational Video

**You**: I want to create an educational video. Start with the edu template, add my slides (slide1.png, slide2.png, slide3.png) for 10 seconds each, and add narration from audio.mp3.

**Claude**: I'll create an educational video with your slides and narration.

[Claude uses:]
- `load_template("edu_landscape")`
- `add_clip(clip_type="image", source="slide1.png", duration=10.0, start=0.0)`
- `add_clip(clip_type="image", source="slide2.png", duration=10.0, start=10.0)`
- `add_clip(clip_type="image", source="slide3.png", duration=10.0, start=20.0)`
- `add_clip(clip_type="audio", source="audio.mp3", duration=30.0, start=0.0)`
- `render_project(output_path="educational_video.mp4")`

Your educational video is complete!

---

### Batch Processing

**You**: I have 5 videos (video1.mp4 through video5.mp4). For each one, crop them to vertical format and render them as output1.mp4 through output5.mp4.

**Claude**: I'll process all 5 videos for you.

[For each video, Claude uses:]
- `load_template("tiktok_vertical")`
- `add_clip(clip_type="video", source="videoN.mp4", duration=15.0)`
- `apply_action("crop_vertical", parameters={...})`
- `render_project(output_path="outputN.mp4")`

All 5 videos have been processed and are ready!

---

## Available MCP Tools

Claude has access to these Moviely tools:

1. **create_project** - Create a new project
2. **load_template** - Load a template (tiktok_vertical, youtube_landscape, edu_landscape)
3. **add_clip** - Add video, audio, image, or text clips
4. **apply_action** - Apply editing actions (trim, crop, effects, volume)
5. **render_project** - Render the final video
6. **save_project** - Save project to storage
7. **load_project** - Load a saved project
8. **get_project_info** - Get details about the current project
9. **list_actions** - List all available actions
10. **list_templates** - List available templates

## Tips for Working with Claude

1. **Be specific about file paths**: Provide full or relative paths to your media files.

2. **Ask for project info**: You can ask Claude to show you the current state of your project at any time.

3. **Iterate easily**: After rendering, you can ask Claude to make adjustments and re-render.

4. **Save your work**: Ask Claude to save your project so you can come back to it later.

5. **Explore actions**: Ask Claude "What actions can I perform?" to see all available editing operations.

## Common Workflows

### Quick TikTok Conversion
```
"Convert landscape.mp4 to TikTok format with the title 'Check this out!'"
```

### Multi-clip Composition
```
"Create a video with intro.mp4 for 5 seconds, then main.mp4 for 20 seconds, 
with background music from audio.mp3"
```

### Text Overlay Video
```
"Add the text 'Subscribe for more!' to my_video.mp4 from 10 to 15 seconds"
```

### Volume Adjustment
```
"Load project.json and reduce the audio volume to 50%"
```

## Troubleshooting

If Claude can't find the moviely-server:
1. Ensure moviely is installed: `uv add moviely`
2. Check that the config path is correct
3. Restart Claude Desktop

If rendering fails:
- Verify all media file paths exist
- Check that you have write permissions for the output directory
- Ask Claude to show you the project info to debug

## Advanced: Accessing Project State

You can ask Claude to read the project state resource:

**You**: Show me the current project state as JSON

Claude will access the `moviely://project/state` resource and display the complete project structure.

---

Happy video editing with AI! 🎬
