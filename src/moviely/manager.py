"""Main VideoProjectManager class."""

from pathlib import Path
from typing import Optional, Any, Dict
from moviely.models import ProjectState, Clip
from moviely.engine.actions import ActionRegistry
from moviely.engine.renderer import Renderer
from moviely.storage.json_store import JSONStore
from moviely.storage.memory_store import MemoryStore
from moviely.utils.templates import TemplateManager
from moviely.utils.assets import AssetManager
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
        
        # Current project state
        self.project: Optional[ProjectState] = None
    
    def create_project(
        self,
        name: str,
        resolution: tuple[int, int] = (1920, 1080),
        fps: int = 30,
        background_color: tuple[int, int, int] = (0, 0, 0)
    ) -> ProjectState:
        """Create a new project.
        
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
    
    def add_clip(
        self,
        clip_type: str,
        source: str,
        duration: float,
        start: float = 0.0,
        **kwargs
    ) -> Clip:
        """Add a clip to the project.
        
        Args:
            clip_type: Type of clip
            source: Path to media or text content
            duration: Duration in seconds
            start: Start time
            **kwargs: Additional clip parameters
            
        Returns:
            Created clip
        """
        if not self.project:
            raise MovielyError("No active project")
        
        # Validate asset if it's a file
        if clip_type != "text":
            self.asset_manager.validate_asset(source)
        
        self.apply_action(
            "add_clip",
            clip_type=clip_type,
            source=source,
            duration=duration,
            start=start,
            **kwargs
        )
        
        # Return the newly added clip
        return self.project.clips[-1]
    
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
        
        if not self.project.clips:
            raise MovielyError("Project has no clips to render")
        
        logger.info(f"Starting render to: {output_path}")
        return self.renderer.render(self.project, output_path, codec=codec, preset=preset)
    
    def get_project_info(self) -> Dict[str, Any]:
        """Get information about the current project.
        
        Returns:
            Project information dictionary
        """
        if not self.project:
            return {"error": "No active project"}
        
        return {
            "name": self.project.name,
            "resolution": self.project.resolution,
            "fps": self.project.fps,
            "num_clips": len(self.project.clips),
            "total_duration": self.project.get_total_duration(),
            "clips": [
                {
                    "id": clip.id,
                    "type": clip.type,
                    "start": clip.start,
                    "duration": clip.duration,
                    "layer": clip.track_layer,
                }
                for clip in self.project.clips
            ]
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
