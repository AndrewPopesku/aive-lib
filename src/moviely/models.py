"""Core data models for Moviely using Pydantic."""

from typing import List, Literal, Optional, Dict, Any, Tuple
from pydantic import BaseModel, Field, field_validator, model_validator
import json
from pathlib import Path


class Effect(BaseModel):
    """Represents a video effect."""
    type: str = Field(..., description="Type of effect (e.g., 'fade', 'crop', 'filter')")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Effect parameters")


class SearchResult(BaseModel):
    """Represents a search result from a media provider."""
    id: str = Field(..., description="Unique identifier from the provider")
    url: str = Field(..., description="Download URL for the media")
    preview_url: Optional[str] = Field(None, description="Preview/thumbnail URL")
    provider: Literal["pexels", "pixabay", "jamendo"] = Field(..., description="Media provider")
    media_type: Literal["video", "image", "audio"] = Field(..., description="Type of media")
    duration: Optional[float] = Field(None, description="Duration in seconds (video/audio)")
    width: Optional[int] = Field(None, description="Width in pixels (video/image)")
    height: Optional[int] = Field(None, description="Height in pixels (video/image)")
    title: Optional[str] = Field(None, description="Title or description")
    author: Optional[str] = Field(None, description="Author/creator name")


class Clip(BaseModel):
    """Represents a media clip in the project."""
    id: str = Field(..., description="Unique identifier for the clip")
    type: Literal["video", "audio", "image", "text"] = Field(..., description="Type of media")
    source: str = Field(..., description="Path or content for the clip")
    start: float = Field(0.0, ge=0, description="Start time in seconds")
    duration: float = Field(..., gt=0, description="Duration in seconds")
    track_layer: int = Field(1, ge=1, description="Track layer (higher = on top)")
    effects: List[Effect] = Field(default_factory=list, description="Applied effects")
    volume: float = Field(1.0, ge=0, le=2.0, description="Audio volume multiplier")
    
    @field_validator('source')
    @classmethod
    def validate_source(cls, v: str, info) -> str:
        """Validate source path for non-text clips."""
        if info.data.get('type') != 'text':
            # Check if it's a valid path or URL
            if not v.startswith(('http://', 'https://')):
                path = Path(v)
                if not path.exists():
                    raise ValueError(f"Source file does not exist: {v}")
        return v


class ProjectState(BaseModel):
    """Represents the complete state of a video project."""
    name: str = Field(..., description="Project name")
    resolution: Tuple[int, int] = Field(..., description="Video resolution (width, height)")
    fps: int = Field(30, gt=0, le=120, description="Frames per second")
    clips: List[Clip] = Field(default_factory=list, description="All clips in the project")
    background_color: Tuple[int, int, int] = Field((0, 0, 0), description="RGB background color")
    
    @field_validator('resolution')
    @classmethod
    def validate_resolution(cls, v: Tuple[int, int]) -> Tuple[int, int]:
        """Validate resolution values."""
        width, height = v
        if width <= 0 or height <= 0:
            raise ValueError(f"Resolution must be positive: {v}")
        if width > 7680 or height > 4320:  # 8K max
            raise ValueError(f"Resolution too large (max 8K): {v}")
        return v
    
    @model_validator(mode='after')
    def validate_background_color(self) -> 'ProjectState':
        """Validate RGB values."""
        r, g, b = self.background_color
        if not all(0 <= x <= 255 for x in [r, g, b]):
            raise ValueError(f"RGB values must be 0-255: {self.background_color}")
        return self
    
    def to_json(self, file_path: Path) -> None:
        """Save project state to JSON file."""
        with open(file_path, 'w') as f:
            json.dump(self.model_dump(), f, indent=2)
    
    @classmethod
    def from_json(cls, file_path: Path) -> 'ProjectState':
        """Load project state from JSON file."""
        with open(file_path, 'r') as f:
            data = json.load(f)
        return cls(**data)
    
    def get_clip_by_id(self, clip_id: str) -> Optional[Clip]:
        """Get a clip by its ID."""
        for clip in self.clips:
            if clip.id == clip_id:
                return clip
        return None
    
    def add_clip(self, clip: Clip) -> None:
        """Add a clip to the project."""
        if self.get_clip_by_id(clip.id):
            raise ValueError(f"Clip with id '{clip.id}' already exists")
        self.clips.append(clip)
    
    def remove_clip(self, clip_id: str) -> bool:
        """Remove a clip from the project."""
        for i, clip in enumerate(self.clips):
            if clip.id == clip_id:
                self.clips.pop(i)
                return True
        return False
    
    def get_total_duration(self) -> float:
        """Calculate the total duration of all clips."""
        if not self.clips:
            return 0.0
        return max(clip.start + clip.duration for clip in self.clips)
