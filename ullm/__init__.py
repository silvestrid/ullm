"""ullm - Lightweight, fast alternative to litellm."""

from ullm.exceptions import (
    APIError,
    AuthenticationError,
    BadRequestError,
    RateLimitError,
    Timeout,
    UllmException,
)
from ullm.main import acompletion, aresponses, completion, responses
from ullm.types import Choice, Message, ModelResponse, StreamChunk, Usage

__version__ = "0.1.0"

__all__ = [
    # Main API
    "completion",
    "acompletion",
    "responses",
    "aresponses",
    # Types
    "ModelResponse",
    "Message",
    "Choice",
    "Usage",
    "StreamChunk",
    # Exceptions
    "UllmException",
    "AuthenticationError",
    "RateLimitError",
    "BadRequestError",
    "Timeout",
    "APIError",
]
