"""Action registry for video editing operations."""

from typing import Callable, Dict, Any
from moviely.models import ProjectState, Clip, Effect
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


# Register built-in actions

@ActionRegistry.register("add_clip")
def add_clip(
    context: ProjectState,
    clip_type: str,
    source: str,
    duration: float,
    start: float = 0.0,
    track_layer: int = 1,
    clip_id: str = None,
    **kwargs
) -> ProjectState:
    """Add a new clip to the project.
    
    Args:
        context: Project state
        clip_type: Type of clip (video, audio, image, text)
        source: Path to media file or text content
        duration: Clip duration in seconds
        start: Start time in timeline
        track_layer: Layer number
        clip_id: Optional clip ID (auto-generated if not provided)
        **kwargs: Additional clip parameters
    """
    clip_id = clip_id or f"clip_{uuid.uuid4().hex[:8]}"
    
    clip = Clip(
        id=clip_id,
        type=clip_type,
        source=source,
        start=start,
        duration=duration,
        track_layer=track_layer,
        **kwargs
    )
    
    context.add_clip(clip)
    return context


@ActionRegistry.register("remove_clip")
def remove_clip(context: ProjectState, clip_id: str) -> ProjectState:
    """Remove a clip from the project.
    
    Args:
        context: Project state
        clip_id: ID of clip to remove
    """
    if not context.remove_clip(clip_id):
        raise InvalidActionError(f"Clip '{clip_id}' not found")
    return context


@ActionRegistry.register("trim_clip")
def trim_clip(
    context: ProjectState,
    clip_id: str,
    new_duration: float = None,
    new_start: float = None
) -> ProjectState:
    """Trim a clip by adjusting duration or start time.
    
    Args:
        context: Project state
        clip_id: ID of clip to trim
        new_duration: New duration (optional)
        new_start: New start time (optional)
    """
    clip = context.get_clip_by_id(clip_id)
    if not clip:
        raise InvalidActionError(f"Clip '{clip_id}' not found")
    
    if new_duration is not None:
        if new_duration <= 0:
            raise InvalidActionError("Duration must be positive")
        clip.duration = new_duration
    
    if new_start is not None:
        if new_start < 0:
            raise InvalidActionError("Start time must be non-negative")
        clip.start = new_start
    
    return context


@ActionRegistry.register("apply_effect")
def apply_effect(
    context: ProjectState,
    clip_id: str,
    effect_type: str,
    parameters: Dict[str, Any] = None
) -> ProjectState:
    """Apply an effect to a clip.
    
    Args:
        context: Project state
        clip_id: ID of clip
        effect_type: Type of effect
        parameters: Effect parameters
    """
    clip = context.get_clip_by_id(clip_id)
    if not clip:
        raise InvalidActionError(f"Clip '{clip_id}' not found")
    
    effect = Effect(
        type=effect_type,
        parameters=parameters or {}
    )
    
    clip.effects.append(effect)
    return context


@ActionRegistry.register("set_volume")
def set_volume(context: ProjectState, clip_id: str, volume: float) -> ProjectState:
    """Set volume for a clip.
    
    Args:
        context: Project state
        clip_id: ID of clip
        volume: Volume level (0.0 to 2.0)
    """
    clip = context.get_clip_by_id(clip_id)
    if not clip:
        raise InvalidActionError(f"Clip '{clip_id}' not found")
    
    if not 0 <= volume <= 2.0:
        raise InvalidActionError("Volume must be between 0.0 and 2.0")
    
    clip.volume = volume
    return context


@ActionRegistry.register("crop_vertical")
def crop_vertical(
    context: ProjectState,
    clip_id: str,
    target_aspect: str = "9:16"
) -> ProjectState:
    """Crop a clip to vertical format (e.g., for TikTok).
    
    Args:
        context: Project state
        clip_id: ID of clip to crop
        target_aspect: Target aspect ratio (default 9:16)
    """
    clip = context.get_clip_by_id(clip_id)
    if not clip:
        raise InvalidActionError(f"Clip '{clip_id}' not found")
    
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
