"""Custom exceptions for Pharos CLI."""

from typing import Any, Dict, Optional


class PharosError(Exception):
    """Base exception for Pharos CLI."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class APIError(PharosError):
    """API request failed."""

    def __init__(
        self,
        status_code: int,
        message: str,
        details: Optional[Dict[str, Any]] = None,
    ):
        self.status_code = status_code
        self.message = message
        self.details = details or {}
        super().__init__(f"API Error {status_code}: {message}")

    @classmethod
    def from_response(cls, response) -> "APIError":
        """Create APIError from HTTP response."""
        try:
            error_data = response.json()
            message = error_data.get("detail", response.text)
            details = error_data
        except Exception:
            message = response.text
            details = {}

        return cls(response.status_code, message, details)


class NetworkError(PharosError):
    """Network connection failed."""

    pass


class ConfigError(PharosError):
    """Configuration error."""

    pass


class AuthenticationError(PharosError):
    """Authentication failed."""

    pass


class ValidationError(PharosError):
    """Validation error."""

    pass


class ResourceNotFoundError(PharosError):
    """Resource not found."""

    pass


class PermissionError(PharosError):
    """Permission denied."""

    pass


class CollectionNotFoundError(PharosError):
    """Collection not found."""

    pass
class AnnotationNotFoundError(PharosError):
    """Annotation not found."""

    pass