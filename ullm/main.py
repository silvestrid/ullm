"""Main entry point for ullm - completion and responses APIs."""

from typing import Any, AsyncIterator, Dict, Iterator, Optional, Union

from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

# Import clients to trigger registration
import ullm.clients  # noqa: F401
from ullm.exceptions import RateLimitError, Timeout
from ullm.providers import parse_model_name
from ullm.registry import get_client as _get_client
from ullm.types import ModelResponse, ResponseFormat, StreamChunk, Tool


def _create_retry_decorator(num_retries: int = 3):
    """Create a retry decorator with exponential backoff."""
    return retry(
        retry=retry_if_exception_type((RateLimitError, Timeout)),
        stop=stop_after_attempt(num_retries),
        wait=wait_exponential(multiplier=1, min=1, max=60),
        reraise=True,
    )


def completion(
    model: str,
    messages: list[Dict[str, Any]],
    temperature: Optional[float] = None,
    max_tokens: Optional[int] = None,
    stream: bool = False,
    tools: Optional[list[Tool]] = None,
    tool_choice: Optional[Union[str, Dict[str, Any]]] = None,
    response_format: Optional[ResponseFormat] = None,
    num_retries: int = 3,
    retry_strategy: str = "exponential_backoff_retry",
    cache: Optional[Dict[str, Any]] = None,
    api_key: Optional[str] = None,
    api_base: Optional[str] = None,
    timeout: float = 600.0,
    **kwargs: Any,
) -> Union[ModelResponse, Iterator[StreamChunk]]:
    """
    Make a completion request to an LLM provider.

    Compatible with litellm.completion() API.

    Args:
        model: Model name in format "provider/model-name" or just "model-name"
        messages: List of message dicts with "role" and "content"
        temperature: Sampling temperature (0-2)
        max_tokens: Maximum tokens to generate
        stream: Whether to stream the response
        tools: List of tool/function definitions
        tool_choice: How to choose tools ("auto", "required", or specific tool)
        response_format: Response format (dict or Pydantic model)
        num_retries: Number of retries on rate limit or timeout
        retry_strategy: Retry strategy (currently only "exponential_backoff_retry")
        cache: Cache control dict (for compatibility, not used by ullm)
        api_key: API key (if not in environment)
        api_base: API base URL (if not default)
        timeout: Request timeout in seconds
        **kwargs: Additional provider-specific parameters

    Returns:
        ModelResponse or Iterator[StreamChunk] if streaming

    Raises:
        AuthenticationError: On authentication failure
        BadRequestError: On invalid request
        RateLimitError: On rate limit exceeded
        Timeout: On request timeout
        APIError: On other API errors
    """
    provider, model_name = parse_model_name(model)

    client = _get_client(
        provider,
        api_key=api_key,
        api_base=api_base,
        timeout=timeout,
        **kwargs,
    )

    # Create retry-wrapped function if retries are enabled
    if num_retries > 0 and not stream:  # Don't retry streaming requests

        @_create_retry_decorator(num_retries)
        def _make_request():
            return client.completion(
                model=model_name,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=stream,
                tools=tools,
                tool_choice=tool_choice,
                response_format=response_format,
                **kwargs,
            )

        return _make_request()
    else:
        return client.completion(
            model=model_name,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=stream,
            tools=tools,
            tool_choice=tool_choice,
            response_format=response_format,
            **kwargs,
        )


async def acompletion(
    model: str,
    messages: list[Dict[str, Any]],
    temperature: Optional[float] = None,
    max_tokens: Optional[int] = None,
    stream: bool = False,
    tools: Optional[list[Tool]] = None,
    tool_choice: Optional[Union[str, Dict[str, Any]]] = None,
    response_format: Optional[ResponseFormat] = None,
    num_retries: int = 3,
    retry_strategy: str = "exponential_backoff_retry",
    cache: Optional[Dict[str, Any]] = None,
    api_key: Optional[str] = None,
    api_base: Optional[str] = None,
    timeout: float = 600.0,
    **kwargs: Any,
) -> Union[ModelResponse, AsyncIterator[StreamChunk]]:
    """
    Make an async completion request to an LLM provider.

    Compatible with litellm.acompletion() API.

    Args:
        Same as completion()

    Returns:
        ModelResponse or AsyncIterator[StreamChunk] if streaming
    """
    provider, model_name = parse_model_name(model)

    client = _get_client(
        provider,
        api_key=api_key,
        api_base=api_base,
        timeout=timeout,
        **kwargs,
    )

    # Create retry-wrapped function if retries are enabled
    if num_retries > 0 and not stream:

        @_create_retry_decorator(num_retries)
        async def _make_request():
            return await client.acompletion(
                model=model_name,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=stream,
                tools=tools,
                tool_choice=tool_choice,
                response_format=response_format,
                **kwargs,
            )

        return await _make_request()
    else:
        return await client.acompletion(
            model=model_name,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=stream,
            tools=tools,
            tool_choice=tool_choice,
            response_format=response_format,
            **kwargs,
        )


def responses(
    model: str,
    input: list[Dict[str, Any]],
    temperature: Optional[float] = None,
    max_tokens: Optional[int] = None,
    num_retries: int = 3,
    retry_strategy: str = "exponential_backoff_retry",
    cache: Optional[Dict[str, Any]] = None,
    api_key: Optional[str] = None,
    api_base: Optional[str] = None,
    timeout: float = 600.0,
    **kwargs: Any,
) -> ModelResponse:
    """
    Make a request using OpenAI's Responses API format.

    Compatible with litellm.responses() API.

    Args:
        model: Model name in format "provider/model-name"
        input: List of input messages in Responses API format
        temperature: Sampling temperature
        max_tokens: Maximum tokens to generate
        num_retries: Number of retries
        retry_strategy: Retry strategy
        cache: Cache control (not used)
        api_key: API key
        api_base: API base URL
        timeout: Request timeout
        **kwargs: Additional parameters

    Returns:
        ModelResponse
    """
    provider, model_name = parse_model_name(model)

    client = _get_client(
        provider,
        api_key=api_key,
        api_base=api_base,
        timeout=timeout,
        **kwargs,
    )

    # Only OpenAI client has responses method
    if not hasattr(client, "responses"):
        # Fall back to converting to messages format
        messages = []
        for item in input:
            role = item.get("role", "user")
            content_blocks = item.get("content", [])

            if isinstance(content_blocks, list):
                content = " ".join(
                    block.get("text", "") if isinstance(block, dict) else str(block) for block in content_blocks
                )
            else:
                content = str(content_blocks)

            messages.append({"role": role, "content": content})

        return completion(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            num_retries=num_retries,
            api_key=api_key,
            api_base=api_base,
            timeout=timeout,
            **kwargs,
        )

    # Use native responses method
    if num_retries > 0:

        @_create_retry_decorator(num_retries)
        def _make_request():
            return client.responses(
                model=model_name, input=input, temperature=temperature, max_tokens=max_tokens, **kwargs
            )

        return _make_request()
    else:
        return client.responses(model=model_name, input=input, temperature=temperature, max_tokens=max_tokens, **kwargs)


async def aresponses(
    model: str,
    input: list[Dict[str, Any]],
    temperature: Optional[float] = None,
    max_tokens: Optional[int] = None,
    num_retries: int = 3,
    retry_strategy: str = "exponential_backoff_retry",
    cache: Optional[Dict[str, Any]] = None,
    api_key: Optional[str] = None,
    api_base: Optional[str] = None,
    timeout: float = 600.0,
    **kwargs: Any,
) -> ModelResponse:
    """
    Make an async request using OpenAI's Responses API format.

    Compatible with litellm.aresponses() API.

    Args:
        Same as responses()

    Returns:
        ModelResponse
    """
    provider, model_name = parse_model_name(model)

    client = _get_client(
        provider,
        api_key=api_key,
        api_base=api_base,
        timeout=timeout,
        **kwargs,
    )

    # Only OpenAI client has aresponses method
    if not hasattr(client, "aresponses"):
        # Fall back to converting to messages format
        messages = []
        for item in input:
            role = item.get("role", "user")
            content_blocks = item.get("content", [])

            if isinstance(content_blocks, list):
                content = " ".join(
                    block.get("text", "") if isinstance(block, dict) else str(block) for block in content_blocks
                )
            else:
                content = str(content_blocks)

            messages.append({"role": role, "content": content})

        return await acompletion(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            num_retries=num_retries,
            api_key=api_key,
            api_base=api_base,
            timeout=timeout,
            **kwargs,
        )

    # Use native aresponses method
    if num_retries > 0:

        @_create_retry_decorator(num_retries)
        async def _make_request():
            return await client.aresponses(
                model=model_name, input=input, temperature=temperature, max_tokens=max_tokens, **kwargs
            )

        return await _make_request()
    else:
        return await client.aresponses(
            model=model_name, input=input, temperature=temperature, max_tokens=max_tokens, **kwargs
        )
