"""MCP server for Moviely - allows LLMs to control video editing."""

from mcp.server import Server
from mcp.types import Tool, TextContent, Resource
from moviely.manager import VideoProjectManager
from moviely.models import SearchResult
from moviely.errors import MovielyError
import json
import logging

import sys
logging.basicConfig(level=logging.INFO, stream=sys.stderr)
logger = logging.getLogger(__name__)

# Initialize the server and manager
app = Server("moviely")
manager = VideoProjectManager()


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available MCP tools."""
    return [
        Tool(
            name="create_project",
            description="Create a new video project with specified settings",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Project name"},
                    "resolution": {
                        "type": "array",
                        "items": {"type": "integer"},
                        "description": "Resolution [width, height]",
                        "default": [1920, 1080]
                    },
                    "fps": {"type": "integer", "description": "Frames per second", "default": 30}
                },
                "required": ["name"]
            }
        ),
        Tool(
            name="load_template",
            description="Load a project from a template (tiktok_vertical, youtube_landscape, edu_landscape)",
            inputSchema={
                "type": "object",
                "properties": {
                    "template_name": {"type": "string", "description": "Name of template to load"}
                },
                "required": ["template_name"]
            }
        ),
        Tool(
            name="create_track",
            description="Create a new track in the project",
            inputSchema={
                "type": "object",
                "properties": {
                    "track_type": {
                        "type": "string",
                        "enum": ["video", "audio", "text"],
                        "description": "Type of track"
                    },
                    "name": {"type": "string", "description": "Display name for the track"}
                },
                "required": ["track_type"]
            }
        ),
        Tool(
            name="append_clip",
            description="Add a clip to end of timeline. This is a PRIMARY choice for simple additions.",
            inputSchema={
                "type": "object",
                "properties": {
                    "clip_type": {
                        "type": "string",
                        "enum": ["video", "audio", "image", "text", "gap"],
                        "description": "Type of clip"
                    },
                    "source": {
                        "type": "string",
                        "description": "Path to media file, text content, or null for gaps"
                    },
                    "duration": {"type": "number", "description": "Duration in seconds"},
                    "track_id": {
                        "type": "string",
                        "description": "Target track ID (optional)"
                    }
                },
                "required": ["clip_type", "duration"]
            }
        ),
        Tool(
            name="advanced_add_clip",
            description="Advanced way to add a clip with full control over placement, trimming, and effects.",
            inputSchema={
                "type": "object",
                "properties": {
                    "clip_type": {
                        "type": "string",
                        "enum": ["video", "audio", "image", "text", "gap"],
                        "description": "Type of clip"
                    },
                    "source": {
                        "type": "string",
                        "description": "Path to media file, text content, or null for gaps"
                    },
                    "duration": {"type": "number", "description": "Duration in seconds"},
                    "track_id": {
                        "type": "string",
                        "description": "Target track ID (optional)"
                    },
                    "index": {
                        "type": "integer",
                        "description": "Position to insert at (appends if omitted)"
                    },
                    "media_start": {
                        "type": "number",
                        "description": "Start offset in source media for trimming",
                        "default": 0.0
                    },
                    "volume": {
                        "type": "number",
                        "description": "Audio volume multiplier (0.0 to 2.0)",
                        "default": 1.0
                    },
                    "effects": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "type": {"type": "string"},
                                "parameters": {"type": "object"}
                            },
                            "required": ["type"]
                        },
                        "description": "Initial effects to apply"
                    }
                },
                "required": ["clip_type", "duration"]
            }
        ),
        Tool(
            name="delete_clip",
            description="Delete a clip from the timeline",
            inputSchema={
                "type": "object",
                "properties": {
                    "track_id": {"type": "string", "description": "Track ID containing the clip"},
                    "clip_id": {"type": "string", "description": "ID of clip to delete (use this OR index)"},
                    "index": {"type": "integer", "description": "Index of clip to delete (use this OR clip_id)"}
                },
                "required": ["track_id"]
            }
        ),
        Tool(
            name="move_clip",
            description="Move a clip to a different position within the same track",
            inputSchema={
                "type": "object",
                "properties": {
                    "track_id": {"type": "string", "description": "Track ID"},
                    "from_index": {"type": "integer", "description": "Current position of the clip"},
                    "to_index": {"type": "integer", "description": "Target position for the clip"}
                },
                "required": ["track_id", "from_index", "to_index"]
            }
        ),
        Tool(
            name="trim_clip",
            description="Trim a clip by adjusting its start point or duration",
            inputSchema={
                "type": "object",
                "properties": {
                    "track_id": {"type": "string", "description": "Track ID"},
                    "clip_id": {"type": "string", "description": "ID of clip to trim (use this OR index)"},
                    "index": {"type": "integer", "description": "Index of clip to trim (use this OR clip_id)"},
                    "media_start": {"type": "number", "description": "New start offset in source media"},
                    "duration": {"type": "number", "description": "New duration"}
                },
                "required": ["track_id"]
            }
        ),
        Tool(
            name="insert_clip",
            description="Insert a clip at a specific position in a track. This is a PRIMARY choice for simple insertions.",
            inputSchema={
                "type": "object",
                "properties": {
                    "clip_type": {
                        "type": "string",
                        "enum": ["video", "audio", "image", "text", "gap"],
                        "description": "Type of clip"
                    },
                    "source": {
                        "type": "string",
                        "description": "Path to media file, text content, or null for gaps"
                    },
                    "duration": {"type": "number", "description": "Duration in seconds"},
                    "track_id": {"type": "string", "description": "Target track ID"},
                    "index": {"type": "integer", "description": "Position to insert at (0-based)"}
                },
                "required": ["clip_type", "duration", "track_id", "index"]
            }
        ),
        Tool(
            name="apply_action",
            description="Apply an editing action (trim_clip, apply_effect, crop_vertical, set_clip_volume, delete_clip, move_clip, etc.)",
            inputSchema={
                "type": "object",
                "properties": {
                    "action_name": {"type": "string", "description": "Name of action to apply"},
                    "parameters": {"type": "object", "description": "Action parameters"}
                },
                "required": ["action_name", "parameters"]
            }
        ),
        Tool(
            name="render_project",
            description="Render the project to a video file",
            inputSchema={
                "type": "object",
                "properties": {
                    "output_path": {"type": "string", "description": "Output file path"},
                    "codec": {"type": "string", "description": "Video codec", "default": "libx264"},
                    "preset": {"type": "string", "description": "Encoding preset", "default": "medium"}
                },
                "required": ["output_path"]
            }
        ),
        Tool(
            name="get_project_info",
            description="Get information about the current project including tracks and clips",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="list_actions",
            description="List all available editing actions",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="list_templates",
            description="List all available project templates",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="save_project",
            description="Save the current project to storage",
            inputSchema={
                "type": "object",
                "properties": {
                    "filename": {"type": "string", "description": "Optional filename"}
                }
            }
        ),
        Tool(
            name="load_project",
            description="Load a project from storage",
            inputSchema={
                "type": "object",
                "properties": {
                    "filename": {"type": "string", "description": "Filename to load"}
                },
                "required": ["filename"]
            }
        ),
        Tool(
            name="search_media",
            description="Search for videos or images from Pexels or Pixabay",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"},
                    "provider": {
                        "type": "string",
                        "enum": ["pexels", "pixabay"],
                        "description": "Media provider"
                    },
                    "media_type": {
                        "type": "string",
                        "enum": ["video", "image"],
                        "description": "Type of media to search for"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results (default: 10, max: 50)",
                        "default": 10
                    }
                },
                "required": ["query", "provider", "media_type"]
            }
        ),
        Tool(
            name="search_music",
            description="Search for music tracks from Jamendo",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"},
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results (default: 10, max: 50)",
                        "default": 10
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="download_media",
            description="Download a search result to local cache for use with add_clip",
            inputSchema={
                "type": "object",
                "properties": {
                    "provider": {
                        "type": "string",
                        "enum": ["pexels", "pixabay", "jamendo"],
                        "description": "Provider name from search result"
                    },
                    "media_id": {"type": "string", "description": "ID from search result"},
                    "url": {"type": "string", "description": "Download URL from search result"},
                    "media_type": {
                        "type": "string",
                        "enum": ["video", "image", "audio"],
                        "description": "Type of media"
                    }
                },
                "required": ["provider", "media_id", "url", "media_type"]
            }
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls from the MCP client."""
    try:
        logger.info(f"Tool called: {name} with args: {arguments}")

        if name == "create_project":
            result = manager.create_project(
                name=arguments["name"],
                resolution=tuple(arguments.get("resolution", [1920, 1080])),
                fps=arguments.get("fps", 30)
            )
            track_names = [t.name for t in result.tracks]
            return [TextContent(
                type="text",
                text=f"Created project: {result.name} ({result.resolution[0]}x{result.resolution[1]} @ {result.fps}fps) with tracks: {', '.join(track_names)}"
            )]

        elif name == "load_template":
            result = manager.load_template(arguments["template_name"])
            return [TextContent(
                type="text",
                text=f"Loaded template: {result.name}"
            )]

        elif name == "create_track":
            track = manager.create_track(
                track_type=arguments["track_type"],
                name=arguments.get("name")
            )
            return [TextContent(
                type="text",
                text=f"Created track: {track.name} (id: {track.id}, type: {track.type})"
            )]

        elif name == "append_clip":
            clip = manager.append_clip(
                clip_type=arguments["clip_type"],
                source=arguments.get("source"),
                duration=arguments["duration"],
                track_id=arguments.get("track_id"),
            )
            return [TextContent(
                type="text",
                text=f"Appended {clip.type} clip: {clip.id} (duration: {clip.duration}s)"
            )]

        elif name == "advanced_add_clip":
            clip = manager.advanced_add_clip(
                clip_type=arguments["clip_type"],
                source=arguments.get("source"),
                duration=arguments["duration"],
                track_id=arguments.get("track_id"),
                index=arguments.get("index"),
                media_start=arguments.get("media_start", 0.0),
                volume=arguments.get("volume", 1.0),
                effects=arguments.get("effects")
            )
            pos_desc = f"at index {arguments['index']}" if arguments.get('index') is not None else "at end"
            return [TextContent(
                type="text",
                text=f"Advanced added {clip.type} clip: {clip.id} {pos_desc} (duration: {clip.duration}s)"
            )]

        elif name == "delete_clip":
            manager.apply_action(
                "delete_clip",
                track_id=arguments["track_id"],
                clip_id=arguments.get("clip_id"),
                index=arguments.get("index")
            )
            return [TextContent(
                type="text",
                text=f"Deleted clip from track {arguments['track_id']}"
            )]

        elif name == "move_clip":
            manager.apply_action(
                "move_clip",
                track_id=arguments["track_id"],
                from_index=arguments["from_index"],
                to_index=arguments["to_index"]
            )
            return [TextContent(
                type="text",
                text=f"Moved clip from index {arguments['from_index']} to {arguments['to_index']} in track {arguments['track_id']}"
            )]

        elif name == "trim_clip":
            manager.apply_action(
                "trim_clip",
                track_id=arguments["track_id"],
                clip_id=arguments.get("clip_id"),
                index=arguments.get("index"),
                media_start=arguments.get("media_start"),
                duration=arguments.get("duration")
            )
            return [TextContent(
                type="text",
                text=f"Trimmed clip in track {arguments['track_id']}"
            )]

        elif name == "insert_clip":
            clip = manager.insert_clip(
                clip_type=arguments["clip_type"],
                source=arguments.get("source"),
                duration=arguments["duration"],
                track_id=arguments["track_id"],
                index=arguments["index"]
            )
            return [TextContent(
                type="text",
                text=f"Inserted {clip.type} clip: {clip.id} at index {arguments['index']} (duration: {clip.duration}s)"
            )]

        elif name == "apply_action":
            result = manager.apply_action(
                arguments["action_name"],
                **arguments.get("parameters", {})
            )
            return [TextContent(
                type="text",
                text=f"Applied action: {arguments['action_name']}"
            )]

        elif name == "render_project":
            output = manager.render(
                output_path=arguments["output_path"],
                codec=arguments.get("codec", "libx264"),
                preset=arguments.get("preset", "medium")
            )
            return [TextContent(
                type="text",
                text=f"Rendered project to: {output}"
            )]

        elif name == "get_project_info":
            info = manager.get_project_info()
            return [TextContent(
                type="text",
                text=json.dumps(info, indent=2)
            )]

        elif name == "list_actions":
            actions = manager.list_actions()
            return [TextContent(
                type="text",
                text=f"Available actions: {', '.join(actions)}"
            )]

        elif name == "list_templates":
            templates = manager.list_templates()
            return [TextContent(
                type="text",
                text=f"Available templates: {', '.join(templates)}"
            )]

        elif name == "save_project":
            path = manager.save_project(arguments.get("filename"))
            return [TextContent(
                type="text",
                text=f"Saved project to: {path}"
            )]

        elif name == "load_project":
            result = manager.load_project(arguments["filename"])
            return [TextContent(
                type="text",
                text=f"Loaded project: {result.name}"
            )]

        elif name == "search_media":
            results = await manager.search_media(
                query=arguments["query"],
                provider=arguments["provider"],
                media_type=arguments["media_type"],
                limit=arguments.get("limit", 10)
            )
            results_data = [r.model_dump() for r in results]
            return [TextContent(
                type="text",
                text=json.dumps(results_data, indent=2)
            )]

        elif name == "search_music":
            results = await manager.search_music(
                query=arguments["query"],
                limit=arguments.get("limit", 10)
            )
            results_data = [r.model_dump() for r in results]
            return [TextContent(
                type="text",
                text=json.dumps(results_data, indent=2)
            )]

        elif name == "download_media":
            # Reconstruct SearchResult from arguments
            result = SearchResult(
                id=arguments["media_id"],
                url=arguments["url"],
                provider=arguments["provider"],
                media_type=arguments["media_type"]
            )
            path = await manager.download_media(result)
            return [TextContent(
                type="text",
                text=f"Downloaded to: {path}"
            )]

        else:
            return [TextContent(
                type="text",
                text=f"Unknown tool: {name}"
            )]

    except MovielyError as e:
        logger.error(f"Moviely error: {e}")
        return [TextContent(
            type="text",
            text=f"Error: {str(e)}"
        )]
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        return [TextContent(
            type="text",
            text=f"Unexpected error: {str(e)}"
        )]


@app.list_resources()
async def list_resources() -> list[Resource]:
    """List available resources."""
    return [
        Resource(
            uri="moviely://project/state",
            name="Current Project State",
            mimeType="application/json",
            description="The current project state as JSON"
        )
    ]


@app.read_resource()
async def read_resource(uri: str) -> str:
    """Read a resource."""
    if uri == "moviely://project/state":
        if manager.project:
            return json.dumps(manager.project.model_dump(), indent=2)
        return json.dumps({"error": "No active project"})

    return json.dumps({"error": f"Unknown resource: {uri}"})


def main():
    """Main entry point for the MCP server."""
    import asyncio
    from mcp.server.stdio import stdio_server

    async def run():
        async with stdio_server() as (read_stream, write_stream):
            await app.run(read_stream, write_stream, app.create_initialization_options())

    asyncio.run(run())


if __name__ == "__main__":
    main()
