"""Exception types for ullm - compatible with litellm exceptions."""

from typing import Optional


class UllmException(Exception):
    """Base exception for all ullm errors."""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        model: Optional[str] = None,
        llm_provider: Optional[str] = None,
    ):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.model = model
        self.llm_provider = llm_provider


class AuthenticationError(UllmException):
    """Raised when authentication fails (401)."""

    def __init__(self, message: str, model: Optional[str] = None, llm_provider: Optional[str] = None):
        super().__init__(message, status_code=401, model=model, llm_provider=llm_provider)


class BadRequestError(UllmException):
    """Raised for invalid requests (400)."""

    def __init__(self, message: str, model: Optional[str] = None, llm_provider: Optional[str] = None):
        super().__init__(message, status_code=400, model=model, llm_provider=llm_provider)


class RateLimitError(UllmException):
    """Raised when rate limit is exceeded (429)."""

    def __init__(self, message: str, model: Optional[str] = None, llm_provider: Optional[str] = None):
        super().__init__(message, status_code=429, model=model, llm_provider=llm_provider)


class Timeout(UllmException):
    """Raised on request timeout (504)."""

    def __init__(self, message: str, model: Optional[str] = None, llm_provider: Optional[str] = None):
        super().__init__(message, status_code=504, model=model, llm_provider=llm_provider)


class APIError(UllmException):
    """Raised for general API errors (500+)."""

    def __init__(
        self, message: str, status_code: int = 500, model: Optional[str] = None, llm_provider: Optional[str] = None
    ):
        super().__init__(message, status_code=status_code, model=model, llm_provider=llm_provider)


class ProviderNotFoundError(UllmException):
    """Raised when provider cannot be determined from model string."""

    def __init__(self, model: str):
        super().__init__(f"Could not determine provider from model: {model}", model=model)


class UnsupportedProviderError(UllmException):
    """Raised when provider is not supported."""

    def __init__(self, provider: str, model: str):
        super().__init__(f"Provider '{provider}' is not supported", model=model, llm_provider=provider)
