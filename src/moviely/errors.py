"""Custom exceptions for Moviely."""


class MovielyError(Exception):
    """Base exception for all Moviely errors."""
    pass


class InvalidActionError(MovielyError):
    """Raised when an invalid action is requested."""
    pass


class RenderError(MovielyError):
    """Raised when rendering fails."""
    pass


class StorageError(MovielyError):
    """Raised when storage operations fail."""
    pass


class ValidationError(MovielyError):
    """Raised when data validation fails."""
    pass


class AssetError(MovielyError):
    """Raised when asset operations fail."""
    pass
