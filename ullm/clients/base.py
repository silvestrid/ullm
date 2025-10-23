"""Base client for all providers."""

from abc import ABC, abstractmethod
from typing import Any, AsyncIterator, Dict, Iterator, Optional, Union

from pydantic import BaseModel

from ullm.exceptions import (
    APIError,
    AuthenticationError,
    BadRequestError,
    RateLimitError,
    Timeout,
)
from ullm.types import ModelResponse, ResponseFormat, StreamChunk, Tool


class BaseClient(ABC):
    """Base class for all provider clients."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        api_base: Optional[str] = None,
        timeout: float = 600.0,
        **kwargs: Any,
    ):
        self.api_key = api_key or self._get_api_key_from_env()
        self.api_base = api_base or self._get_default_api_base()
        self.timeout = timeout
        self.extra_kwargs = kwargs

    @abstractmethod
    def _get_api_key_from_env(self) -> Optional[str]:
        """Get API key from environment variables."""
        pass

    @abstractmethod
    def _get_default_api_base(self) -> str:
        """Get default API base URL."""
        pass

    @abstractmethod
    def completion(
        self,
        model: str,
        messages: list[Dict[str, Any]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        stream: bool = False,
        tools: Optional[list[Tool]] = None,
        tool_choice: Optional[Union[str, Dict[str, Any]]] = None,
        response_format: Optional[ResponseFormat] = None,
        **kwargs: Any,
    ) -> Union[ModelResponse, Iterator[StreamChunk]]:
        """Make a completion request."""
        pass

    @abstractmethod
    async def acompletion(
        self,
        model: str,
        messages: list[Dict[str, Any]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        stream: bool = False,
        tools: Optional[list[Tool]] = None,
        tool_choice: Optional[Union[str, Dict[str, Any]]] = None,
        response_format: Optional[ResponseFormat] = None,
        **kwargs: Any,
    ) -> Union[ModelResponse, AsyncIterator[StreamChunk]]:
        """Make an async completion request."""
        pass

    def _handle_error(self, status_code: int, error_text: str, model: str, provider: str) -> None:
        """Handle HTTP errors and raise appropriate exceptions."""
        if status_code == 401:
            raise AuthenticationError(error_text, model=model, llm_provider=provider)
        elif status_code == 400:
            raise BadRequestError(error_text, model=model, llm_provider=provider)
        elif status_code == 429:
            raise RateLimitError(error_text, model=model, llm_provider=provider)
        elif status_code == 504:
            raise Timeout(error_text, model=model, llm_provider=provider)
        else:
            raise APIError(error_text, status_code=status_code, model=model, llm_provider=provider)

    def _get_headers(self) -> Dict[str, str]:
        """Get default headers for requests."""
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

    def _convert_response_format(self, response_format: Optional[ResponseFormat]) -> Optional[Dict[str, Any]]:
        """Convert response format to provider-specific format."""
        if response_format is None:
            return None

        # If it's a Pydantic model, convert to JSON schema
        if isinstance(response_format, type) and issubclass(response_format, BaseModel):
            schema = response_format.model_json_schema()
            return {"type": "json_schema", "json_schema": {"name": response_format.__name__, "schema": schema}}

        # Otherwise return as-is (should be ResponseFormatType)
        return response_format.model_dump() if isinstance(response_format, BaseModel) else response_format
