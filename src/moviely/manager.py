"""Main VideoProjectManager class."""

from pathlib import Path
from typing import Literal, Optional, Any, Dict
from moviely.models import ProjectState, Clip, Track, SearchResult
from moviely.engine.actions import ActionRegistry
from moviely.engine.renderer import Renderer
from moviely.storage.json_store import JSONStore
from moviely.storage.memory_store import MemoryStore
from moviely.utils.templates import TemplateManager
from moviely.utils.assets import AssetManager
from moviely.services.search import SearchService
from moviely.errors import MovielyError
import logging

logger = logging.getLogger(__name__)


class VideoProjectManager:
    """Main orchestrator for video projects."""

    def __init__(
        self,
        storage_backend: str = "json",
        storage_path: Optional[Path] = None,
        template_dir: Optional[Path] = None
    ):
        """Initialize the project manager.

        Args:
            storage_backend: Storage backend to use ('json' or 'memory')
            storage_path: Path for storage (for file-based backends)
            template_dir: Directory containing templates
        """
        # Initialize components
        if storage_backend == "json":
            self.storage = JSONStore(storage_path)
        elif storage_backend == "memory":
            self.storage = MemoryStore()
        else:
            raise MovielyError(f"Unknown storage backend: {storage_backend}")

        self.template_manager = TemplateManager(template_dir)
        self.asset_manager = AssetManager()
        self.renderer = Renderer()

        # Search service (lazy-initialized)
        self._search_service: Optional[SearchService] = None

        # Current project state
        self.project: Optional[ProjectState] = None

    def create_project(
        self,
        name: str,
        resolution: tuple[int, int] = (1920, 1080),
        fps: int = 30,
        background_color: tuple[int, int, int] = (0, 0, 0)
    ) -> ProjectState:
        """Create a new project with default tracks.

        Args:
            name: Project name
            resolution: Video resolution
            fps: Frames per second
            background_color: RGB background color

        Returns:
            Created project state
        """
        self.project = ProjectState(
            name=name,
            resolution=resolution,
            fps=fps,
            background_color=background_color
        )

        # Create default tracks
        self.apply_action("create_track", track_type="video", track_name="Video 1")
        self.apply_action("create_track", track_type="audio", track_name="Audio 1")
        self.apply_action("create_track", track_type="text", track_name="Text 1")

        logger.info(f"Created project: {name}")
        return self.project

    def load_template(self, template_name: str) -> ProjectState:
        """Load a project from a template.

        Args:
            template_name: Name of template

        Returns:
            Loaded project state
        """
        self.project = self.template_manager.load_template(template_name)
        logger.info(f"Loaded template: {template_name}")
        return self.project

    def save_project(self, filename: Optional[str] = None) -> Path:
        """Save current project.

        Args:
            filename: Optional filename

        Returns:
            Path to saved file
        """
        if not self.project:
            raise MovielyError("No active project to save")

        result = self.storage.save(self.project, filename)
        logger.info(f"Saved project: {result}")
        return result if isinstance(result, Path) else Path(result)

    def load_project(self, filename: str) -> ProjectState:
        """Load a project from storage.

        Args:
            filename: Name of file to load

        Returns:
            Loaded project state
        """
        self.project = self.storage.load(filename)
        logger.info(f"Loaded project: {filename}")
        return self.project

    def apply_action(self, action_name: str, **kwargs) -> ProjectState:
        """Apply an action to the current project.

        Args:
            action_name: Name of action
            **kwargs: Action parameters

        Returns:
            Updated project state
        """
        if not self.project:
            raise MovielyError("No active project")

        self.project = ActionRegistry.execute(action_name, self.project, **kwargs)
        logger.info(f"Applied action: {action_name}")
        return self.project

    # =========================================================================
    # Track Management
    # =========================================================================

    def create_track(
        self,
        track_type: Literal["video", "audio", "text"],
        name: Optional[str] = None,
    ) -> Track:
        """Create a new track.

        Args:
            track_type: Type of track
            name: Display name (auto-generated if not provided)

        Returns:
            Created track
        """
        if not self.project:
            raise MovielyError("No active project")

        self.apply_action("create_track", track_type=track_type, track_name=name)
        return self.project.tracks[-1]

    def get_track(self, track_id: str) -> Optional[Track]:
        """Get a track by ID.

        Args:
            track_id: Track ID

        Returns:
            Track or None if not found
        """
        if not self.project:
            return None
        return self.project.get_track_by_id(track_id)

    def get_default_track(self, track_type: Literal["video", "audio", "text"]) -> Optional[Track]:
        """Get the first track of a given type.

        Args:
            track_type: Type of track to find

        Returns:
            First matching track or None
        """
        if not self.project:
            return None
        tracks = self.project.get_tracks_by_type(track_type)
        return tracks[0] if tracks else None

    # =========================================================================
    # Clip Management
    # =========================================================================

    def append_clip(
        self,
        clip_type: str,
        source: Optional[str],
        duration: float,
        track_id: Optional[str] = None,
    ) -> Clip:
        """Add a clip to a track (appends to end).

        Args:
            clip_type: Type of clip (video, audio, image, text, gap)
            source: Path to media file, text content, or None for gaps
            duration: Duration in seconds
            track_id: Target track ID (uses default track for type if not provided)

        Returns:
            Created clip
        """
        if not self.project:
            raise MovielyError("No active project")

        # Resolve track
        if track_id is None:
            # Map clip type to track type
            track_type_map: Dict[str, Literal["video", "audio", "text"]] = {
                "video": "video",
                "image": "video",
                "audio": "audio",
                "text": "text",
                "gap": "video",
            }
            track_type = track_type_map.get(clip_type, "video")
            track = self.get_default_track(track_type)
            if not track:
                raise MovielyError(f"No {track_type} track available")
            track_id = track.id

        # Validate asset if it's a media file
        if clip_type not in ("text", "gap") and source:
            self.asset_manager.validate_asset(source)

        self.apply_action(
            "append_clip",
            track_id=track_id,
            clip_type=clip_type,
            source=source,
            duration=duration,
        )

        # Return the newly added clip
        track = self.project.get_track_by_id(track_id)
        if not track:
            raise MovielyError(f"Track '{track_id}' not found after adding clip")
        return track.clips[-1]

    def advanced_add_clip(
        self,
        clip_type: str,
        source: Optional[str],
        duration: float,
        track_id: Optional[str] = None,
        index: Optional[int] = None,
        media_start: float = 0.0,
        volume: float = 1.0,
        effects: Optional[list[Dict[str, Any]]] = None,
        **kwargs
    ) -> Clip:
        """Advanced way to add a clip with more control.

        Args:
            clip_type: Type of clip
            source: Source path or content
            duration: Duration in seconds
            track_id: Target track ID
            index: Position to insert at (appends if None)
            media_start: Start offset in source
            volume: Clip volume
            effects: Initial effects to apply
            **kwargs: Extra parameters

        Returns:
            Created clip
        """
        if not self.project:
            raise MovielyError("No active project")

        # Resolve track if needed
        if track_id is None:
            track_type_map: Dict[str, Literal["video", "audio", "text"]] = {
                "video": "video", "image": "video", "audio": "audio", "text": "text", "gap": "video"
            }
            track_type = track_type_map.get(clip_type, "video")
            track = self.get_default_track(track_type)
            if not track:
                raise MovielyError(f"No {track_type} track available")
            track_id = track.id

        # Validate
        if clip_type not in ("text", "gap") and source:
            self.asset_manager.validate_asset(source)

        # Use insert or append action
        action_name = "insert_clip" if index is not None else "append_clip"
        action_params = {
            "track_id": track_id,
            "clip_type": clip_type,
            "source": source,
            "duration": duration,
            "media_start": media_start,
            "volume": volume,
            **kwargs
        }
        if index is not None:
            action_params["index"] = index

        self.apply_action(action_name, **action_params)

        # Get the clip
        track = self.project.get_track_by_id(track_id)
        clip = track.clips[index] if index is not None else track.clips[-1]

        # Apply effects if any
        if effects:
            for effect_data in effects:
                self.apply_action(
                    "apply_effect",
                    track_id=track_id,
                    clip_id=clip.id,
                    effect_type=effect_data["type"],
                    parameters=effect_data.get("parameters", {})
                )

        return clip

    def insert_clip(
        self,
        clip_type: str,
        source: Optional[str],
        duration: float,
        track_id: str,
        index: int,
        **kwargs
    ) -> Clip:
        """Insert a clip at a specific position in a track.

        Args:
            clip_type: Type of clip
            source: Path to media file, text content, or None for gaps
            duration: Duration in seconds
            track_id: Target track ID
            index: Position to insert at
            **kwargs: Additional clip parameters

        Returns:
            Created clip
        """
        if not self.project:
            raise MovielyError("No active project")

        # Validate asset if it's a media file
        if clip_type not in ("text", "gap") and source:
            self.asset_manager.validate_asset(source)

        self.apply_action(
            "insert_clip",
            track_id=track_id,
            index=index,
            clip_type=clip_type,
            source=source,
            duration=duration,
            **kwargs
        )

        track = self.project.get_track_by_id(track_id)
        if not track:
            raise MovielyError(f"Track '{track_id}' not found after inserting clip")
        return track.clips[index]

    # =========================================================================
    # Rendering
    # =========================================================================

    def render(
        self,
        output_path: str,
        codec: str = "libx264",
        preset: str = "medium"
    ) -> Path:
        """Render the current project.

        Args:
            output_path: Output file path
            codec: Video codec
            preset: Encoding preset

        Returns:
            Path to rendered file
        """
        if not self.project:
            raise MovielyError("No active project to render")

        if self.project.get_clip_count() == 0:
            raise MovielyError("Project has no clips to render")

        logger.info(f"Starting render to: {output_path}")
        return self.renderer.render(self.project, output_path, codec=codec, preset=preset)

    # =========================================================================
    # Project Info
    # =========================================================================

    def get_project_info(self) -> Dict[str, Any]:
        """Get information about the current project.

        Returns:
            Project information dictionary
        """
        if not self.project:
            return {"error": "No active project"}

        tracks_info = []
        for track in self.project.tracks:
            clips_info = []
            current_time = 0.0
            for clip in track.clips:
                clips_info.append({
                    "id": clip.id,
                    "type": clip.type,
                    "start": current_time,
                    "duration": clip.duration,
                    "source": clip.source[:50] + "..." if clip.source and len(clip.source) > 50 else clip.source,
                })
                current_time += clip.duration

            tracks_info.append({
                "id": track.id,
                "name": track.name,
                "type": track.type,
                "duration": track.get_duration(),
                "clip_count": len(track.clips),
                "visible": track.visible,
                "locked": track.locked,
                "clips": clips_info,
            })

        return {
            "name": self.project.name,
            "resolution": self.project.resolution,
            "fps": self.project.fps,
            "total_duration": self.project.get_total_duration(),
            "track_count": len(self.project.tracks),
            "clip_count": self.project.get_clip_count(),
            "tracks": tracks_info,
        }

    def list_actions(self) -> list[str]:
        """List all available actions.

        Returns:
            List of action names
        """
        return ActionRegistry.list_actions()

    def list_templates(self) -> list[str]:
        """List available templates.

        Returns:
            List of template names
        """
        return self.template_manager.list_templates()

    # =========================================================================
    # Search & Download
    # =========================================================================

    def _get_search_service(self) -> SearchService:
        """Get or create the search service (lazy initialization)."""
        if self._search_service is None:
            self._search_service = SearchService()
        return self._search_service

    async def search_media(
        self,
        query: str,
        provider: Literal["pexels", "pixabay"],
        media_type: Literal["video", "image"],
        limit: int = 10,
    ) -> list[SearchResult]:
        """Search for videos or images from a provider.

        Args:
            query: Search query string
            provider: Media provider ("pexels" or "pixabay")
            media_type: Type of media ("video" or "image")
            limit: Maximum number of results (default 10, max 50)

        Returns:
            List of SearchResult objects
        """
        service = self._get_search_service()
        results = await service.search_media(query, provider, media_type, limit)
        logger.info(f"Found {len(results)} {media_type}s from {provider} for '{query}'")
        return results

    async def search_music(self, query: str, limit: int = 10) -> list[SearchResult]:
        """Search for music tracks from Jamendo.

        Args:
            query: Search query string
            limit: Maximum number of results (default 10, max 50)

        Returns:
            List of SearchResult objects
        """
        service = self._get_search_service()
        results = await service.search_music(query, limit)
        logger.info(f"Found {len(results)} music tracks for '{query}'")
        return results

    async def download_media(self, result: SearchResult) -> Path:
        """Download a search result to local cache.

        Args:
            result: SearchResult to download

        Returns:
            Path to the downloaded file
        """
        service = self._get_search_service()
        path = await service.download(result)
        logger.info(f"Downloaded media to: {path}")
        return path
