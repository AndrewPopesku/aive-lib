# Migration to FastMCP

The objective is to rewrite `mcp_agent.py` using the `FastMCP` framework. This will enable compatibility with the `mcp dev` command and simplify the code by using decorators for tool and resource definitions.

## Proposed Changes

### [Component Name]

#### [MODIFY] [mcp_agent.py](file:///Users/andriipopesku/projects/experiments/lib/aive/src/aive/server/mcp_agent.py)

- Replace `mcp.server.Server` with `mcp.server.fastmcp.FastMCP`.
- Convert the centralized `call_tool` logic into individual `@mcp.tool()` decorated functions.
- Convert resource listing and reading into `@mcp.resource()` decorated functions.
- Maintain the `VideoProjectManager` instance as a global or accessible inside tool functions.
- Use `pydantic` models or explicit arguments in `@mcp.tool()` for automatic schema generation.

### Detailed Tool Mapping

| Old Tool Name | New FastMCP Tool Function |
|---------------|---------------------------|
| `create_project` | `create_project(name: str, resolution: list[int] = [1920, 1080], fps: int = 30)` |
| `load_template` | `load_template(template_name: str)` |
| `create_track` | `create_track(track_type: str, name: str = None)` |
| `append_clip` | `append_clip(clip_type: str, duration: float, source: str = None, track_id: str = None)` |
| `advanced_add_clip` | `advanced_add_clip(...)` (with all parameters) |
| `delete_clip` | `delete_clip(track_id: str, clip_id: str = None, index: int = None)` |
| `move_clip" | `move_clip(track_id: str, from_index: int, to_index: int)` |
| `trim_clip" | `trim_clip(track_id: str, clip_id: str = None, index: int = None, media_start: float = None, duration: float = None)` |
| `insert_clip" | `insert_clip(...)` |
| `apply_action" | `apply_action(action_name: str, parameters: dict)` |
| `render_project" | `render_project(output_path: str, codec: str = "libx264", preset: str = "medium")` |
| `get_project_info" | `get_project_info()` |
| `list_actions" | `list_actions()` |
| `list_templates" | `list_templates()` |
| `save_project" | `save_project(filename: str = None)` |
| `load_project" | `load_project(filename: str)` |
| `search_media" | `search_media(query: str, provider: str, media_type: str, limit: int = 10)` |
| `search_music" | `search_music(query: str, limit: int = 10)` |
| `download_media" | `download_media(provider: str, media_id: str, url: str, media_type: str)` |

## Verification Plan

### Automated Tests
- Run `mcp dev src/aive/server/mcp_agent.py` and verify that all tools are listed correctly in the UI.
- Run existing tests using `pytest tests/test_advanced_add.py` and `pytest tests/test_actions.py`.

### Manual Verification
- Use the `mcp dev` inspector to call `list_templates` and `get_project_info`.
- Create a simple project through the inspector to ensure components are wired correctly.
