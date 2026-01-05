"""Custom exceptions for Piglet CLI"""


class PigletError(Exception):
    """Base exception for Piglet CLI"""

    pass


class ConfigurationError(PigletError):
    """Configuration-related errors"""

    pass


class PostHogAPIError(PigletError):
    """PostHog API errors"""

    def __init__(self, message: str, status_code: int | None = None):
        super().__init__(message)
        self.status_code = status_code


class AuthenticationError(PostHogAPIError):
    """Authentication failures (401)"""

    pass


class RateLimitError(PostHogAPIError):
    """Rate limit exceeded (429)"""

    pass


class NotFoundError(PostHogAPIError):
    """Resource not found (404)"""

    pass
