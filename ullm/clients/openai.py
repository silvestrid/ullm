"""OpenAI provider client."""

import json
import os
import time
from typing import Any, AsyncIterator, Dict, Iterator, Optional, Union

import httpx

from ullm.clients.base import BaseClient
from ullm.types import (
    Choice,
    Delta,
    Message,
    ModelResponse,
    ResponseFormat,
    StreamChoice,
    StreamChunk,
    Tool,
    Usage,
)


class OpenAIClient(BaseClient):
    """Client for OpenAI API."""

    def _get_api_key_from_env(self) -> Optional[str]:
        return os.getenv("OPENAI_API_KEY")

    def _get_default_api_base(self) -> str:
        return os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")

    def _prepare_request(
        self,
        model: str,
        messages: list[Dict[str, Any]],
        temperature: Optional[float],
        max_tokens: Optional[int],
        stream: bool,
        tools: Optional[list[Tool]],
        tool_choice: Optional[Union[str, Dict[str, Any]]],
        response_format: Optional[ResponseFormat],
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Prepare request payload for OpenAI API."""
        payload: Dict[str, Any] = {
            "model": model,
            "messages": messages,
            "stream": stream,
        }

        if temperature is not None:
            payload["temperature"] = temperature

        if max_tokens is not None:
            # Handle OpenAI reasoning models (o1, o3, gpt-5)
            if any(model.startswith(prefix) for prefix in ["o1", "o3", "gpt-5"]):
                payload["max_completion_tokens"] = max_tokens
            else:
                payload["max_tokens"] = max_tokens

        if tools:
            payload["tools"] = [tool.model_dump() if hasattr(tool, "model_dump") else tool for tool in tools]

        if tool_choice:
            payload["tool_choice"] = tool_choice

        if response_format:
            payload["response_format"] = self._convert_response_format(response_format)

        # Add any extra kwargs
        payload.update(kwargs)

        return payload

    def _parse_response(self, data: Dict[str, Any]) -> ModelResponse:
        """Parse OpenAI API response into ModelResponse."""
        choices = []
        for choice_data in data.get("choices", []):
            message_data = choice_data.get("message", {})

            # Parse tool calls if present
            tool_calls = None
            if "tool_calls" in message_data:
                from ullm.types import FunctionCall, ToolCall

                tool_calls = [
                    ToolCall(
                        id=tc["id"],
                        type=tc["type"],
                        function=FunctionCall(name=tc["function"]["name"], arguments=tc["function"]["arguments"]),
                    )
                    for tc in message_data["tool_calls"]
                ]

            message = Message(
                role=message_data.get("role", "assistant"),
                content=message_data.get("content"),
                tool_calls=tool_calls,
            )

            choice = Choice(
                index=choice_data.get("index", 0),
                message=message,
                finish_reason=choice_data.get("finish_reason"),
            )
            choices.append(choice)

        usage_data = data.get("usage")
        usage = None
        if usage_data:
            usage = Usage(
                prompt_tokens=usage_data.get("prompt_tokens", 0),
                completion_tokens=usage_data.get("completion_tokens", 0),
                total_tokens=usage_data.get("total_tokens", 0),
            )

        return ModelResponse(
            id=data.get("id", ""),
            object=data.get("object", "chat.completion"),
            created=data.get("created", int(time.time())),
            model=data.get("model", ""),
            choices=choices,
            usage=usage,
            system_fingerprint=data.get("system_fingerprint"),
        )

    def _parse_stream_chunk(self, data: Dict[str, Any]) -> StreamChunk:
        """Parse OpenAI streaming chunk."""
        choices = []
        for choice_data in data.get("choices", []):
            delta_data = choice_data.get("delta", {})

            delta = Delta(
                role=delta_data.get("role"),
                content=delta_data.get("content"),
                tool_calls=delta_data.get("tool_calls"),
                function_call=delta_data.get("function_call"),
            )

            choice = StreamChoice(
                index=choice_data.get("index", 0), delta=delta, finish_reason=choice_data.get("finish_reason")
            )
            choices.append(choice)

        usage_data = data.get("usage")
        usage = None
        if usage_data:
            usage = Usage(
                prompt_tokens=usage_data.get("prompt_tokens", 0),
                completion_tokens=usage_data.get("completion_tokens", 0),
                total_tokens=usage_data.get("total_tokens", 0),
            )

        return StreamChunk(
            id=data.get("id", ""),
            object=data.get("object", "chat.completion.chunk"),
            created=data.get("created", int(time.time())),
            model=data.get("model", ""),
            choices=choices,
            usage=usage,
            system_fingerprint=data.get("system_fingerprint"),
        )

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
        """Make a completion request to OpenAI."""
        payload = self._prepare_request(
            model, messages, temperature, max_tokens, stream, tools, tool_choice, response_format, **kwargs
        )

        url = f"{self.api_base}/chat/completions"
        headers = self._get_headers()

        with httpx.Client(timeout=self.timeout) as client:
            if stream:
                return self._stream_completion(client, url, headers, payload, model)
            else:
                response = client.post(url, json=payload, headers=headers)

                if response.status_code != 200:
                    self._handle_error(response.status_code, response.text, model, "openai")

                return self._parse_response(response.json())

    def _stream_completion(
        self, client: httpx.Client, url: str, headers: Dict[str, str], payload: Dict[str, Any], model: str
    ) -> Iterator[StreamChunk]:
        """Handle streaming completion."""
        with client.stream("POST", url, json=payload, headers=headers) as response:
            if response.status_code != 200:
                error_text = ""
                for chunk in response.iter_text():
                    error_text += chunk
                self._handle_error(response.status_code, error_text, model, "openai")

            for line in response.iter_lines():
                if line.startswith("data: "):
                    data_str = line[6:]
                    if data_str.strip() == "[DONE]":
                        break

                    try:
                        data = json.loads(data_str)
                        yield self._parse_stream_chunk(data)
                    except json.JSONDecodeError:
                        continue

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
        """Make an async completion request to OpenAI."""
        payload = self._prepare_request(
            model, messages, temperature, max_tokens, stream, tools, tool_choice, response_format, **kwargs
        )

        url = f"{self.api_base}/chat/completions"
        headers = self._get_headers()

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            if stream:
                return self._astream_completion(client, url, headers, payload, model)
            else:
                response = await client.post(url, json=payload, headers=headers)

                if response.status_code != 200:
                    self._handle_error(response.status_code, response.text, model, "openai")

                return self._parse_response(response.json())

    async def _astream_completion(
        self, client: httpx.AsyncClient, url: str, headers: Dict[str, str], payload: Dict[str, Any], model: str
    ) -> AsyncIterator[StreamChunk]:
        """Handle async streaming completion."""
        async with client.stream("POST", url, json=payload, headers=headers) as response:
            if response.status_code != 200:
                error_text = ""
                async for chunk in response.aiter_text():
                    error_text += chunk
                self._handle_error(response.status_code, error_text, model, "openai")

            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    data_str = line[6:]
                    if data_str.strip() == "[DONE]":
                        break

                    try:
                        data = json.loads(data_str)
                        yield self._parse_stream_chunk(data)
                    except json.JSONDecodeError:
                        continue

    def responses(
        self,
        model: str,
        input: list[Dict[str, Any]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs: Any,
    ) -> ModelResponse:
        """
        Make a request using OpenAI's Responses API format.
        This converts the input format to messages format internally.
        """
        # Convert responses format to messages format
        messages = []
        for item in input:
            role = item.get("role", "user")
            content_blocks = item.get("content", [])

            # Flatten content blocks
            if isinstance(content_blocks, list):
                content = " ".join(
                    block.get("text", "") if isinstance(block, dict) else str(block) for block in content_blocks
                )
            else:
                content = str(content_blocks)

            messages.append({"role": role, "content": content})

        return self.completion(model=model, messages=messages, temperature=temperature, max_tokens=max_tokens, **kwargs)

    async def aresponses(
        self,
        model: str,
        input: list[Dict[str, Any]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs: Any,
    ) -> ModelResponse:
        """Async version of responses()."""
        # Convert responses format to messages format
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

        return await self.acompletion(
            model=model, messages=messages, temperature=temperature, max_tokens=max_tokens, **kwargs
        )
