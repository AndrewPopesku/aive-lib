"""aive - Video automation framework for Python and LLMs."""

from aive.models import ProjectState, Clip, Effect
from aive.manager import VideoProjectManager
from aive.errors import (
    aiveError,
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
    "aiveError",
    "InvalidActionError",
    "RenderError",
    "StorageError",
    "ValidationError",
    "AssetError",
]
