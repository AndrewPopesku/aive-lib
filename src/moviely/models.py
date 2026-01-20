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
    """Represents a media clip in a track.

    Timeline position is determined by sequence order within the parent track,
    not by an absolute start time. The actual render start time is calculated
    dynamically as the sum of durations of all preceding clips.
    """
    id: str = Field(..., description="Unique identifier for the clip (unique within track)")
    type: Literal["video", "audio", "image", "text", "gap"] = Field(..., description="Type of media")
    source: Optional[str] = Field(None, description="Path or content for the clip (None for gap clips)")
    duration: float = Field(..., gt=0, description="Duration in seconds")
    media_start: float = Field(0.0, ge=0, description="Start offset in source media (for trimming)")
    effects: List[Effect] = Field(default_factory=list, description="Applied effects")
    volume: float = Field(1.0, ge=0, le=2.0, description="Audio volume multiplier")

    @field_validator('source')
    @classmethod
    def validate_source(cls, v: Optional[str], info) -> Optional[str]:
        """Validate source path for non-text and non-gap clips."""
        clip_type = info.data.get('type')
        # Gap clips don't need a source
        if clip_type == 'gap':
            return None
        # Text clips use source as content, not a file path
        if clip_type == 'text':
            if not v:
                raise ValueError("Text clips require source content")
            return v
        # Media clips need a valid source
        if not v:
            raise ValueError(f"{clip_type} clips require a source path")
        # Check if it's a valid path or URL
        if not v.startswith(('http://', 'https://')):
            path = Path(v)
            if not path.exists():
                raise ValueError(f"Source file does not exist: {v}")
        return v


class Track(BaseModel):
    """Represents a track containing an ordered sequence of clips.

    Clips are stored in sequential order. Their timeline positions are
    calculated dynamically based on the sum of preceding clip durations.
    """
    id: str = Field(..., description="Unique identifier for the track")
    name: str = Field(..., description="Display name for the track")
    type: Literal["video", "audio", "text"] = Field(..., description="Type of content this track holds")
    clips: List[Clip] = Field(default_factory=list, description="Ordered list of clips")
    volume: float = Field(1.0, ge=0, le=2.0, description="Track-level volume multiplier")
    visible: bool = Field(True, description="Whether the track is visible during render")
    locked: bool = Field(False, description="Whether the track is locked for editing")

    def get_clip_by_id(self, clip_id: str) -> Optional[Clip]:
        """Get a clip by its ID."""
        for clip in self.clips:
            if clip.id == clip_id:
                return clip
        return None

    def get_clip_index(self, clip_id: str) -> Optional[int]:
        """Get the index of a clip by its ID."""
        for i, clip in enumerate(self.clips):
            if clip.id == clip_id:
                return i
        return None

    def get_duration(self) -> float:
        """Calculate total duration of all clips in the track."""
        return sum(clip.duration for clip in self.clips)

    def get_clip_start_time(self, clip_index: int) -> float:
        """Calculate the start time of a clip at the given index."""
        if clip_index < 0 or clip_index >= len(self.clips):
            raise IndexError(f"Clip index {clip_index} out of range")
        return sum(clip.duration for clip in self.clips[:clip_index])


class ProjectState(BaseModel):
    """Represents the complete state of a video project.

    Projects are organized into tracks, where each track contains an ordered
    sequence of clips. Timeline positions are calculated dynamically from
    clip sequence order, not stored as absolute timestamps.
    """
    name: str = Field(..., description="Project name")
    resolution: Tuple[int, int] = Field(..., description="Video resolution (width, height)")
    fps: int = Field(30, gt=0, le=120, description="Frames per second")
    tracks: List[Track] = Field(default_factory=list, description="Ordered list of tracks")
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

    def get_track_by_id(self, track_id: str) -> Optional[Track]:
        """Get a track by its ID."""
        for track in self.tracks:
            if track.id == track_id:
                return track
        return None

    def get_track_index(self, track_id: str) -> Optional[int]:
        """Get the index of a track by its ID."""
        for i, track in enumerate(self.tracks):
            if track.id == track_id:
                return i
        return None

    def get_tracks_by_type(self, track_type: str) -> List[Track]:
        """Get all tracks of a specific type."""
        return [track for track in self.tracks if track.type == track_type]

    def get_total_duration(self) -> float:
        """Calculate the total duration across all tracks."""
        if not self.tracks:
            return 0.0
        return max((track.get_duration() for track in self.tracks), default=0.0)

    def get_clip_count(self) -> int:
        """Get total number of clips across all tracks."""
        return sum(len(track.clips) for track in self.tracks)
