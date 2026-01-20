"""MCP server for aive - allows LLMs to control video editing."""

from mcp.server.fastmcp import FastMCP
from aive.manager import VideoProjectManager
from aive.models import SearchResult
from aive.errors import aiveError
import json
import logging
from typing import Literal, Optional

import sys
logging.basicConfig(level=logging.INFO, stream=sys.stderr)
logger = logging.getLogger(__name__)

# Initialize the server and manager
mcp = FastMCP("aive")
manager = VideoProjectManager()


# =============================================================================
# Project Management Tools
# =============================================================================

@mcp.tool()
def create_project(
    name: str,
    resolution: list[int] = [1920, 1080],
    fps: int = 30
) -> str:
    """Create a new video project with specified settings."""
    try:
        res = (resolution[0], resolution[1]) if len(resolution) >= 2 else (1920, 1080)
        result = manager.create_project(
            name=name,
            resolution=res,
            fps=fps
        )
        track_names = [t.name for t in result.tracks]
        return f"Created project: {result.name} ({result.resolution[0]}x{result.resolution[1]} @ {result.fps}fps) with tracks: {', '.join(track_names)}"
    except aiveError as e:
        return f"Error: {str(e)}"


@mcp.tool()
def load_template(template_name: str) -> str:
    """Load a project from a template (tiktok_vertical, youtube_landscape, edu_landscape)."""
    try:
        result = manager.load_template(template_name)
        return f"Loaded template: {result.name}"
    except aiveError as e:
        return f"Error: {str(e)}"


@mcp.tool()
def save_project(filename: Optional[str] = None) -> str:
    """Save the current project to storage."""
    try:
        path = manager.save_project(filename)
        return f"Saved project to: {path}"
    except aiveError as e:
        return f"Error: {str(e)}"


@mcp.tool()
def load_project(filename: str) -> str:
    """Load a project from storage."""
    try:
        result = manager.load_project(filename)
        return f"Loaded project: {result.name}"
    except aiveError as e:
        return f"Error: {str(e)}"


# =============================================================================
# Track and Clip Tools
# =============================================================================

@mcp.tool()
def create_track(
    track_type: Literal["video", "audio", "text"],
    name: Optional[str] = None
) -> str:
    """Create a new track in the project. track_type must be 'video', 'audio', or 'text'."""
    try:
        track = manager.create_track(track_type=track_type, name=name)
        return f"Created track: {track.name} (id: {track.id}, type: {track.type})"
    except aiveError as e:
        return f"Error: {str(e)}"


@mcp.tool()
def append_clip(
    clip_type: str,
    duration: float,
    source: Optional[str] = None,
    track_id: Optional[str] = None
) -> str:
    """Add a clip to end of timeline. clip_type: video, audio, image, text, or gap."""
    try:
        clip = manager.append_clip(
            clip_type=clip_type,
            source=source,
            duration=duration,
            track_id=track_id,
        )
        return f"Appended {clip.type} clip: {clip.id} (duration: {clip.duration}s)"
    except aiveError as e:
        return f"Error: {str(e)}"


@mcp.tool()
def insert_clip(
    clip_type: str,
    duration: float,
    track_id: str,
    index: int,
    source: Optional[str] = None
) -> str:
    """Insert a clip at a specific position in a track. clip_type: video, audio, image, text, or gap."""
    try:
        clip = manager.insert_clip(
            clip_type=clip_type,
            source=source,
            duration=duration,
            track_id=track_id,
            index=index
        )
        return f"Inserted {clip.type} clip: {clip.id} at index {index} (duration: {clip.duration}s)"
    except aiveError as e:
        return f"Error: {str(e)}"


@mcp.tool()
def advanced_add_clip(
    clip_type: str,
    duration: float,
    source: Optional[str] = None,
    track_id: Optional[str] = None,
    index: Optional[int] = None,
    media_start: float = 0.0,
    volume: float = 1.0,
    effects: Optional[list[dict]] = None
) -> str:
    """Advanced way to add a clip with full control over placement, trimming, and effects."""
    try:
        clip = manager.advanced_add_clip(
            clip_type=clip_type,
            source=source,
            duration=duration,
            track_id=track_id,
            index=index,
            media_start=media_start,
            volume=volume,
            effects=effects
        )
        pos_desc = f"at index {index}" if index is not None else "at end"
        return f"Advanced added {clip.type} clip: {clip.id} {pos_desc} (duration: {clip.duration}s)"
    except aiveError as e:
        return f"Error: {str(e)}"


@mcp.tool()
def delete_clip(
    track_id: str,
    clip_id: Optional[str] = None,
    index: Optional[int] = None
) -> str:
    """Delete a clip from the timeline. Use clip_id OR index to identify the clip."""
    try:
        manager.apply_action(
            "delete_clip",
            track_id=track_id,
            clip_id=clip_id,
            index=index
        )
        return f"Deleted clip from track {track_id}"
    except aiveError as e:
        return f"Error: {str(e)}"


@mcp.tool()
def move_clip(track_id: str, from_index: int, to_index: int) -> str:
    """Move a clip to a different position within the same track."""
    try:
        manager.apply_action(
            "move_clip",
            track_id=track_id,
            from_index=from_index,
            to_index=to_index
        )
        return f"Moved clip from index {from_index} to {to_index} in track {track_id}"
    except aiveError as e:
        return f"Error: {str(e)}"


@mcp.tool()
def trim_clip(
    track_id: str,
    clip_id: Optional[str] = None,
    index: Optional[int] = None,
    media_start: Optional[float] = None,
    duration: Optional[float] = None
) -> str:
    """Trim a clip by adjusting its start point or duration. Use clip_id OR index."""
    try:
        manager.apply_action(
            "trim_clip",
            track_id=track_id,
            clip_id=clip_id,
            index=index,
            media_start=media_start,
            duration=duration
        )
        return f"Trimmed clip in track {track_id}"
    except aiveError as e:
        return f"Error: {str(e)}"


# =============================================================================
# Action and Info Tools
# =============================================================================

@mcp.tool()
def apply_action(action_name: str, parameters: dict) -> str:
    """Apply an editing action (trim_clip, apply_effect, crop_vertical, set_clip_volume, etc.)."""
    try:
        manager.apply_action(action_name, **parameters)
        return f"Applied action: {action_name}"
    except aiveError as e:
        return f"Error: {str(e)}"


@mcp.tool()
def render_project(
    output_path: str,
    codec: str = "libx264",
    preset: str = "medium"
) -> str:
    """Render the project to a video file."""
    try:
        output = manager.render(
            output_path=output_path,
            codec=codec,
            preset=preset
        )
        return f"Rendered project to: {output}"
    except aiveError as e:
        return f"Error: {str(e)}"


@mcp.tool()
def get_project_info() -> str:
    """Get information about the current project including tracks and clips."""
    try:
        info = manager.get_project_info()
        return json.dumps(info, indent=2)
    except aiveError as e:
        return f"Error: {str(e)}"


@mcp.tool()
def list_actions() -> str:
    """List all available editing actions."""
    try:
        actions = manager.list_actions()
        return f"Available actions: {', '.join(actions)}"
    except aiveError as e:
        return f"Error: {str(e)}"


@mcp.tool()
def list_templates() -> str:
    """List all available project templates."""
    try:
        templates = manager.list_templates()
        return f"Available templates: {', '.join(templates)}"
    except aiveError as e:
        return f"Error: {str(e)}"


# =============================================================================
# Async Media Tools
# =============================================================================

@mcp.tool()
async def search_media(
    query: str,
    provider: Literal["pexels", "pixabay"],
    media_type: Literal["video", "image"],
    limit: int = 10
) -> str:
    """Search for videos or images from Pexels or Pixabay."""
    try:
        results = await manager.search_media(
            query=query,
            provider=provider,
            media_type=media_type,
            limit=limit
        )
        results_data = [r.model_dump() for r in results]
        return json.dumps(results_data, indent=2)
    except aiveError as e:
        return f"Error: {str(e)}"


@mcp.tool()
async def search_music(query: str, limit: int = 10) -> str:
    """Search for music tracks from Jamendo."""
    try:
        results = await manager.search_music(query=query, limit=limit)
        results_data = [r.model_dump() for r in results]
        return json.dumps(results_data, indent=2)
    except aiveError as e:
        return f"Error: {str(e)}"


@mcp.tool()
async def download_media(
    provider: Literal["pexels", "pixabay", "jamendo"],
    media_id: str,
    url: str,
    media_type: Literal["video", "image", "audio"]
) -> str:
    """Download a search result to local cache for use with add_clip."""
    try:
        result = SearchResult(
            id=media_id,
            url=url,
            provider=provider,
            media_type=media_type,
            preview_url=None,
            duration=None,
            width=None,
            height=None,
            title=None,
            author=None
        )
        path = await manager.download_media(result)
        return f"Downloaded to: {path}"
    except aiveError as e:
        return f"Error: {str(e)}"


# =============================================================================
# Resources
# =============================================================================

@mcp.resource("aive://project/state")
def get_project_state() -> str:
    """The current project state as JSON."""
    if manager.project:
        return json.dumps(manager.project.model_dump(), indent=2)
    return json.dumps({"error": "No active project"})


# =============================================================================
# Entry Point
# =============================================================================

def main():
    """Main entry point for the MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
