"""
Custom exceptions for the backend
"""

class APIError(Exception):
    """Raised when an upstream API returns a non-200 status."""
    pass

class ValidationFailure(Exception):
    """Raised when Pydantic validation fails for all items."""
    pass
