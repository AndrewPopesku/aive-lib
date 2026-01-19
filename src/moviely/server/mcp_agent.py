"""MCP server for Moviely - allows LLMs to control video editing."""

from mcp.server import Server
from mcp.types import Tool, TextContent, Resource
from moviely.manager import VideoProjectManager
from moviely.errors import MovielyError
import json
import logging

logging.basicConfig(level=logging.INFO)
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
            name="add_clip",
            description="Add a media clip to the project",
            inputSchema={
                "type": "object",
                "properties": {
                    "clip_type": {
                        "type": "string",
                        "enum": ["video", "audio", "image", "text"],
                        "description": "Type of clip"
                    },
                    "source": {"type": "string", "description": "Path to media file or text content"},
                    "duration": {"type": "number", "description": "Duration in seconds"},
                    "start": {"type": "number", "description": "Start time in timeline", "default": 0.0},
                    "track_layer": {"type": "integer", "description": "Layer number", "default": 1}
                },
                "required": ["clip_type", "source", "duration"]
            }
        ),
        Tool(
            name="apply_action",
            description="Apply an editing action (trim_clip, apply_effect, crop_vertical, set_volume, etc.)",
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
            description="Get information about the current project",
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
            return [TextContent(
                type="text",
                text=f"Created project: {result.name} ({result.resolution[0]}x{result.resolution[1]} @ {result.fps}fps)"
            )]
        
        elif name == "load_template":
            result = manager.load_template(arguments["template_name"])
            return [TextContent(
                type="text",
                text=f"Loaded template: {result.name}"
            )]
        
        elif name == "add_clip":
            clip = manager.add_clip(
                clip_type=arguments["clip_type"],
                source=arguments["source"],
                duration=arguments["duration"],
                start=arguments.get("start", 0.0),
                track_layer=arguments.get("track_layer", 1)
            )
            return [TextContent(
                type="text",
                text=f"Added {clip.type} clip: {clip.id} (start: {clip.start}s, duration: {clip.duration}s)"
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
