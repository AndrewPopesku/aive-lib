"""Action registry for video editing operations."""

from typing import Callable, Dict, Any, Optional
from moviely.models import ProjectState, Clip, Effect, Track
from moviely.errors import InvalidActionError
import uuid


class ActionRegistry:
    """Registry for managing video editing actions."""

    _actions: Dict[str, Callable] = {}

    @classmethod
    def register(cls, name: str):
        """Decorator to register an action.

        Args:
            name: Name of the action
        """
        def decorator(func: Callable) -> Callable:
            cls._actions[name] = func
            return func
        return decorator

    @classmethod
    def execute(cls, name: str, context: ProjectState, **kwargs) -> ProjectState:
        """Execute an action.

        Args:
            name: Name of action to execute
            context: Current project state
            **kwargs: Action parameters

        Returns:
            Updated project state
        """
        if name not in cls._actions:
            raise InvalidActionError(f"Action '{name}' not found. Available: {list(cls._actions.keys())}")

        try:
            return cls._actions[name](context, **kwargs)
        except InvalidActionError:
            raise
        except Exception as e:
            raise InvalidActionError(f"Action '{name}' failed: {e}")

    @classmethod
    def list_actions(cls) -> list[str]:
        """List all registered actions.

        Returns:
            List of action names
        """
        return list(cls._actions.keys())

    @classmethod
    def get_action_doc(cls, name: str) -> str:
        """Get documentation for an action.

        Args:
            name: Name of action

        Returns:
            Action docstring
        """
        if name not in cls._actions:
            raise InvalidActionError(f"Action '{name}' not found")
        return cls._actions[name].__doc__ or "No documentation available"


# =============================================================================
# Track Management Actions
# =============================================================================

@ActionRegistry.register("create_track")
def create_track(
    context: ProjectState,
    track_type: str,
    track_name: Optional[str] = None,
    track_id: Optional[str] = None,
) -> ProjectState:
    """Create a new track in the project.

    Args:
        context: Project state
        track_type: Type of track (video, audio, text)
        track_name: Display name for the track (auto-generated if not provided)
        track_id: Optional track ID (auto-generated if not provided)

    Returns:
        Updated project state
    """
    if track_type not in ("video", "audio", "text"):
        raise InvalidActionError(f"Invalid track type: {track_type}")

    track_id = track_id or f"track_{uuid.uuid4().hex[:8]}"

    # Check for duplicate track ID
    if context.get_track_by_id(track_id):
        raise InvalidActionError(f"Track with id '{track_id}' already exists")

    # Generate default name based on type count
    if not track_name:
        existing_count = len(context.get_tracks_by_type(track_type))
        track_name = f"{track_type.capitalize()} {existing_count + 1}"

    track = Track(
        id=track_id,
        name=track_name,
        type=track_type,
    )

    context.tracks.append(track)
    return context


@ActionRegistry.register("delete_track")
def delete_track(context: ProjectState, track_id: str) -> ProjectState:
    """Delete a track from the project.

    Args:
        context: Project state
        track_id: ID of track to delete

    Returns:
        Updated project state
    """
    track_index = context.get_track_index(track_id)
    if track_index is None:
        raise InvalidActionError(f"Track '{track_id}' not found")

    context.tracks.pop(track_index)
    return context


@ActionRegistry.register("reorder_tracks")
def reorder_tracks(context: ProjectState, track_ids: list[str]) -> ProjectState:
    """Reorder tracks in the project.

    Args:
        context: Project state
        track_ids: List of track IDs in the desired order

    Returns:
        Updated project state
    """
    existing_ids = {track.id for track in context.tracks}
    provided_ids = set(track_ids)

    if existing_ids != provided_ids:
        missing = existing_ids - provided_ids
        extra = provided_ids - existing_ids
        if missing:
            raise InvalidActionError(f"Missing track IDs in reorder: {missing}")
        if extra:
            raise InvalidActionError(f"Unknown track IDs in reorder: {extra}")

    # Build new track order
    track_map = {track.id: track for track in context.tracks}
    context.tracks = [track_map[tid] for tid in track_ids]
    return context


@ActionRegistry.register("update_track")
def update_track(
    context: ProjectState,
    track_id: str,
    track_name: Optional[str] = None,
    volume: Optional[float] = None,
    visible: Optional[bool] = None,
    locked: Optional[bool] = None,
) -> ProjectState:
    """Update track properties.

    Args:
        context: Project state
        track_id: ID of track to update
        track_name: New display name
        volume: New volume level (0.0 to 2.0)
        visible: New visibility state
        locked: New locked state

    Returns:
        Updated project state
    """
    track = context.get_track_by_id(track_id)
    if not track:
        raise InvalidActionError(f"Track '{track_id}' not found")

    if track_name is not None:
        track.name = track_name
    if volume is not None:
        if not 0 <= volume <= 2.0:
            raise InvalidActionError("Volume must be between 0.0 and 2.0")
        track.volume = volume
    if visible is not None:
        track.visible = visible
    if locked is not None:
        track.locked = locked

    return context


# =============================================================================
# Clip Management Actions
# =============================================================================

@ActionRegistry.register("append_clip")
def append_clip(
    context: ProjectState,
    track_id: str,
    clip_type: str,
    source: Optional[str],
    duration: float,
    clip_id: Optional[str] = None,
    media_start: float = 0.0,
    volume: float = 1.0,
    **kwargs
) -> ProjectState:
    """Append a clip to the end of a track.

    Args:
        context: Project state
        track_id: ID of target track
        clip_type: Type of clip (video, audio, image, text, gap)
        source: Path to media file, text content, or None for gaps
        duration: Clip duration in seconds
        clip_id: Optional clip ID (auto-generated if not provided)
        media_start: Start offset in source media for trimming
        volume: Audio volume multiplier
        **kwargs: Additional clip parameters (effects, etc.)

    Returns:
        Updated project state
    """
    track = context.get_track_by_id(track_id)
    if not track:
        raise InvalidActionError(f"Track '{track_id}' not found")

    if track.locked:
        raise InvalidActionError(f"Track '{track_id}' is locked")

    clip_id = clip_id or f"clip_{uuid.uuid4().hex[:8]}"

    # Check for duplicate clip ID within this track
    if track.get_clip_by_id(clip_id):
        raise InvalidActionError(f"Clip with id '{clip_id}' already exists in track")

    clip = Clip(
        id=clip_id,
        type=clip_type,
        source=source,
        duration=duration,
        media_start=media_start,
        volume=volume,
        **kwargs
    )

    track.clips.append(clip)
    return context


@ActionRegistry.register("insert_clip")
def insert_clip(
    context: ProjectState,
    track_id: str,
    index: int,
    clip_type: str,
    source: Optional[str],
    duration: float,
    clip_id: Optional[str] = None,
    media_start: float = 0.0,
    volume: float = 1.0,
    **kwargs
) -> ProjectState:
    """Insert a clip at a specific position in a track.

    Args:
        context: Project state
        track_id: ID of target track
        index: Position to insert at (0-based)
        clip_type: Type of clip (video, audio, image, text, gap)
        source: Path to media file, text content, or None for gaps
        duration: Clip duration in seconds
        clip_id: Optional clip ID (auto-generated if not provided)
        media_start: Start offset in source media for trimming
        volume: Audio volume multiplier
        **kwargs: Additional clip parameters

    Returns:
        Updated project state
    """
    track = context.get_track_by_id(track_id)
    if not track:
        raise InvalidActionError(f"Track '{track_id}' not found")

    if track.locked:
        raise InvalidActionError(f"Track '{track_id}' is locked")

    if index < 0 or index > len(track.clips):
        raise InvalidActionError(f"Index {index} out of range (0-{len(track.clips)})")

    clip_id = clip_id or f"clip_{uuid.uuid4().hex[:8]}"

    if track.get_clip_by_id(clip_id):
        raise InvalidActionError(f"Clip with id '{clip_id}' already exists in track")

    clip = Clip(
        id=clip_id,
        type=clip_type,
        source=source,
        duration=duration,
        media_start=media_start,
        volume=volume,
        **kwargs
    )

    track.clips.insert(index, clip)
    return context


@ActionRegistry.register("delete_clip")
def delete_clip(
    context: ProjectState,
    track_id: str,
    clip_id: Optional[str] = None,
    index: Optional[int] = None,
) -> ProjectState:
    """Delete a clip from a track.

    Args:
        context: Project state
        track_id: ID of target track
        clip_id: ID of clip to delete (mutually exclusive with index)
        index: Index of clip to delete (mutually exclusive with clip_id)

    Returns:
        Updated project state
    """
    track = context.get_track_by_id(track_id)
    if not track:
        raise InvalidActionError(f"Track '{track_id}' not found")

    if track.locked:
        raise InvalidActionError(f"Track '{track_id}' is locked")

    if clip_id is not None and index is not None:
        raise InvalidActionError("Provide either clip_id or index, not both")

    if clip_id is None and index is None:
        raise InvalidActionError("Must provide either clip_id or index")

    if clip_id is not None:
        index = track.get_clip_index(clip_id)
        if index is None:
            raise InvalidActionError(f"Clip '{clip_id}' not found in track")

    if index < 0 or index >= len(track.clips):
        raise InvalidActionError(f"Index {index} out of range")

    track.clips.pop(index)
    return context


@ActionRegistry.register("move_clip")
def move_clip(
    context: ProjectState,
    track_id: str,
    from_index: int,
    to_index: int,
) -> ProjectState:
    """Move a clip to a different position within the same track.

    Args:
        context: Project state
        track_id: ID of target track
        from_index: Current index of the clip
        to_index: Target index for the clip

    Returns:
        Updated project state
    """
    track = context.get_track_by_id(track_id)
    if not track:
        raise InvalidActionError(f"Track '{track_id}' not found")

    if track.locked:
        raise InvalidActionError(f"Track '{track_id}' is locked")

    if from_index < 0 or from_index >= len(track.clips):
        raise InvalidActionError(f"from_index {from_index} out of range")

    if to_index < 0 or to_index >= len(track.clips):
        raise InvalidActionError(f"to_index {to_index} out of range")

    clip = track.clips.pop(from_index)
    track.clips.insert(to_index, clip)
    return context


@ActionRegistry.register("insert_gap")
def insert_gap(
    context: ProjectState,
    track_id: str,
    index: int,
    duration: float,
    gap_id: Optional[str] = None,
) -> ProjectState:
    """Insert a gap (spacer) at a specific position in a track.

    Args:
        context: Project state
        track_id: ID of target track
        index: Position to insert at
        duration: Gap duration in seconds
        gap_id: Optional gap ID (auto-generated if not provided)

    Returns:
        Updated project state
    """
    return insert_clip(
        context,
        track_id=track_id,
        index=index,
        clip_type="gap",
        source=None,
        duration=duration,
        clip_id=gap_id,
    )


# =============================================================================
# Clip Editing Actions
# =============================================================================

@ActionRegistry.register("trim_clip")
def trim_clip(
    context: ProjectState,
    track_id: str,
    clip_id: Optional[str] = None,
    index: Optional[int] = None,
    media_start: Optional[float] = None,
    duration: Optional[float] = None,
) -> ProjectState:
    """Trim a clip by adjusting media_start or duration.

    Args:
        context: Project state
        track_id: ID of target track
        clip_id: ID of clip to trim (mutually exclusive with index)
        index: Index of clip to trim (mutually exclusive with clip_id)
        media_start: New start offset in source media
        duration: New duration

    Returns:
        Updated project state
    """
    track = context.get_track_by_id(track_id)
    if not track:
        raise InvalidActionError(f"Track '{track_id}' not found")

    if track.locked:
        raise InvalidActionError(f"Track '{track_id}' is locked")

    # Resolve clip
    if clip_id is not None:
        clip = track.get_clip_by_id(clip_id)
        if not clip:
            raise InvalidActionError(f"Clip '{clip_id}' not found in track")
    elif index is not None:
        if index < 0 or index >= len(track.clips):
            raise InvalidActionError(f"Index {index} out of range")
        clip = track.clips[index]
    else:
        raise InvalidActionError("Must provide either clip_id or index")

    if media_start is not None:
        if media_start < 0:
            raise InvalidActionError("media_start must be non-negative")
        clip.media_start = media_start

    if duration is not None:
        if duration <= 0:
            raise InvalidActionError("Duration must be positive")
        clip.duration = duration

    return context


@ActionRegistry.register("apply_effect")
def apply_effect(
    context: ProjectState,
    track_id: str,
    effect_type: str,
    clip_id: Optional[str] = None,
    index: Optional[int] = None,
    parameters: Optional[Dict[str, Any]] = None,
) -> ProjectState:
    """Apply an effect to a clip.

    Args:
        context: Project state
        track_id: ID of target track
        effect_type: Type of effect
        clip_id: ID of clip (mutually exclusive with index)
        index: Index of clip (mutually exclusive with clip_id)
        parameters: Effect parameters

    Returns:
        Updated project state
    """
    track = context.get_track_by_id(track_id)
    if not track:
        raise InvalidActionError(f"Track '{track_id}' not found")

    # Resolve clip
    if clip_id is not None:
        clip = track.get_clip_by_id(clip_id)
        if not clip:
            raise InvalidActionError(f"Clip '{clip_id}' not found in track")
    elif index is not None:
        if index < 0 or index >= len(track.clips):
            raise InvalidActionError(f"Index {index} out of range")
        clip = track.clips[index]
    else:
        raise InvalidActionError("Must provide either clip_id or index")

    effect = Effect(
        type=effect_type,
        parameters=parameters or {}
    )

    clip.effects.append(effect)
    return context


@ActionRegistry.register("set_clip_volume")
def set_clip_volume(
    context: ProjectState,
    track_id: str,
    volume: float,
    clip_id: Optional[str] = None,
    index: Optional[int] = None,
) -> ProjectState:
    """Set volume for a clip.

    Args:
        context: Project state
        track_id: ID of target track
        volume: Volume level (0.0 to 2.0)
        clip_id: ID of clip (mutually exclusive with index)
        index: Index of clip (mutually exclusive with clip_id)

    Returns:
        Updated project state
    """
    track = context.get_track_by_id(track_id)
    if not track:
        raise InvalidActionError(f"Track '{track_id}' not found")

    # Resolve clip
    if clip_id is not None:
        clip = track.get_clip_by_id(clip_id)
        if not clip:
            raise InvalidActionError(f"Clip '{clip_id}' not found in track")
    elif index is not None:
        if index < 0 or index >= len(track.clips):
            raise InvalidActionError(f"Index {index} out of range")
        clip = track.clips[index]
    else:
        raise InvalidActionError("Must provide either clip_id or index")

    if not 0 <= volume <= 2.0:
        raise InvalidActionError("Volume must be between 0.0 and 2.0")

    clip.volume = volume
    return context


@ActionRegistry.register("crop_vertical")
def crop_vertical(
    context: ProjectState,
    track_id: str,
    clip_id: Optional[str] = None,
    index: Optional[int] = None,
    target_aspect: str = "9:16",
) -> ProjectState:
    """Crop a clip to vertical format (e.g., for TikTok).

    Args:
        context: Project state
        track_id: ID of target track
        clip_id: ID of clip to crop (mutually exclusive with index)
        index: Index of clip to crop (mutually exclusive with clip_id)
        target_aspect: Target aspect ratio (default 9:16)

    Returns:
        Updated project state
    """
    track = context.get_track_by_id(track_id)
    if not track:
        raise InvalidActionError(f"Track '{track_id}' not found")

    # Resolve clip
    if clip_id is not None:
        clip = track.get_clip_by_id(clip_id)
        if not clip:
            raise InvalidActionError(f"Clip '{clip_id}' not found in track")
    elif index is not None:
        if index < 0 or index >= len(track.clips):
            raise InvalidActionError(f"Index {index} out of range")
        clip = track.clips[index]
    else:
        raise InvalidActionError("Must provide either clip_id or index")

    # Parse aspect ratio
    try:
        w, h = map(int, target_aspect.split(':'))
        crop_width = int(context.resolution[1] * w / h)
        crop_height = context.resolution[1]

        effect = Effect(
            type="crop",
            parameters={
                "width": crop_width,
                "height": crop_height,
                "x": (context.resolution[0] - crop_width) // 2,
                "y": 0
            }
        )

        clip.effects.append(effect)
    except Exception as e:
        raise InvalidActionError(f"Invalid aspect ratio '{target_aspect}': {e}")

    return context
