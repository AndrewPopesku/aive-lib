"""Custom exceptions for aive."""


class aiveError(Exception):
    """Base exception for all aive errors."""
    pass


class InvalidActionError(aiveError):
    """Raised when an invalid action is requested."""
    pass


class RenderError(aiveError):
    """Raised when rendering fails."""
    pass


class StorageError(aiveError):
    """Raised when storage operations fail."""
    pass


class ValidationError(aiveError):
    """Raised when data validation fails."""
    pass


class AssetError(aiveError):
    """Raised when asset operations fail."""
    pass


class SearchError(aiveError):
    """Raised when search operations fail."""
    pass


class SearchConfigError(SearchError):
    """Raised when API keys are missing or invalid."""
    pass
