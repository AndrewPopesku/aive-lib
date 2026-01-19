"""Moviely - Video automation framework for Python and LLMs."""

from moviely.models import ProjectState, Clip, Effect
from moviely.manager import VideoProjectManager
from moviely.errors import (
    MovielyError,
    InvalidActionError,
    RenderError,
    StorageError,
    ValidationError,
    AssetError,
)

__version__ = "0.1.0"

__all__ = [
    "ProjectState",
    "Clip",
    "Effect",
    "VideoProjectManager",
    "MovielyError",
    "InvalidActionError",
    "RenderError",
    "StorageError",
    "ValidationError",
    "AssetError",
]
