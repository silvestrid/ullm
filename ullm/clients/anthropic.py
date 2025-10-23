"""Anthropic provider client."""

import json
import os
import time
from typing import Any, AsyncIterator, Dict, Iterator, Optional, Union

import httpx

from ullm.clients.base import BaseClient
from ullm.registry import register_client
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


@register_client("anthropic")
class AnthropicClient(BaseClient):
    """Client for Anthropic API."""

    def _get_api_key_from_env(self) -> Optional[str]:
        return os.getenv("ANTHROPIC_API_KEY")

    def _get_default_api_base(self) -> str:
        return os.getenv("ANTHROPIC_API_BASE", "https://api.anthropic.com/v1")

    def _get_headers(self) -> Dict[str, str]:
        """Get headers for Anthropic API."""
        return {
            "Content-Type": "application/json",
            "x-api-key": self.api_key or "",
            "anthropic-version": "2023-06-01",
        }

    def _convert_messages(self, messages: list[Dict[str, Any]]) -> tuple[Optional[str], list[Dict[str, Any]]]:
        """
        Convert OpenAI-style messages to Anthropic format.
        Extracts system message and converts rest.
        """
        system_message = None
        anthropic_messages = []

        for msg in messages:
            role = msg.get("role")
            content = msg.get("content")

            if role == "system":
                system_message = content
            else:
                # Anthropic uses 'user' and 'assistant' roles
                anthropic_messages.append({"role": role, "content": content})

        return system_message, anthropic_messages

    def _convert_tools(self, tools: Optional[list[Tool]]) -> Optional[list[Dict[str, Any]]]:
        """Convert OpenAI-style tools to Anthropic format."""
        if not tools:
            return None

        anthropic_tools = []
        for tool in tools:
            tool_dict = tool.model_dump() if hasattr(tool, "model_dump") else tool
            func = tool_dict.get("function", {})

            anthropic_tools.append(
                {"name": func.get("name"), "description": func.get("description", ""), "input_schema": func.get("parameters", {})}
            )

        return anthropic_tools

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
        """Prepare request payload for Anthropic API."""
        system_message, anthropic_messages = self._convert_messages(messages)

        payload: Dict[str, Any] = {
            "model": model,
            "messages": anthropic_messages,
            "max_tokens": max_tokens or 4096,  # Anthropic requires max_tokens
            "stream": stream,
        }

        if system_message:
            payload["system"] = system_message

        if temperature is not None:
            payload["temperature"] = temperature

        if tools:
            payload["tools"] = self._convert_tools(tools)

        if tool_choice:
            # Convert OpenAI tool_choice to Anthropic format
            if isinstance(tool_choice, str):
                if tool_choice == "auto":
                    payload["tool_choice"] = {"type": "auto"}
                elif tool_choice == "required" or tool_choice == "any":
                    payload["tool_choice"] = {"type": "any"}
            elif isinstance(tool_choice, dict):
                payload["tool_choice"] = tool_choice

        # Handle JSON response format
        if response_format:
            # Anthropic doesn't have native JSON mode, but we can add instructions
            # to the system message
            json_instruction = "\n\nPlease respond with valid JSON only."
            if system_message:
                payload["system"] = system_message + json_instruction
            else:
                payload["system"] = json_instruction.strip()

        payload.update(kwargs)
        return payload

    def _parse_response(self, data: Dict[str, Any], model: str) -> ModelResponse:
        """Parse Anthropic API response into ModelResponse."""
        content_blocks = data.get("content", [])

        # Extract text content and tool calls
        text_content = ""
        tool_calls = []

        for block in content_blocks:
            if block.get("type") == "text":
                text_content += block.get("text", "")
            elif block.get("type") == "tool_use":
                from ullm.types import FunctionCall, ToolCall

                tool_calls.append(
                    ToolCall(
                        id=block.get("id", ""),
                        type="function",
                        function=FunctionCall(
                            name=block.get("name", ""), arguments=json.dumps(block.get("input", {}))
                        ),
                    )
                )

        message = Message(
            role="assistant", content=text_content if text_content else None, tool_calls=tool_calls if tool_calls else None
        )

        choice = Choice(index=0, message=message, finish_reason=data.get("stop_reason"))

        usage_data = data.get("usage", {})
        usage = Usage(
            prompt_tokens=usage_data.get("input_tokens", 0),
            completion_tokens=usage_data.get("output_tokens", 0),
            total_tokens=usage_data.get("input_tokens", 0) + usage_data.get("output_tokens", 0),
        )

        return ModelResponse(
            id=data.get("id", ""),
            object="chat.completion",
            created=int(time.time()),
            model=model,
            choices=[choice],
            usage=usage,
        )

    def _parse_stream_chunk(self, data: Dict[str, Any], model: str) -> Optional[StreamChunk]:
        """Parse Anthropic streaming chunk."""
        event_type = data.get("type")

        # Handle different event types
        if event_type == "message_start":
            return StreamChunk(
                id=data.get("message", {}).get("id", ""),
                object="chat.completion.chunk",
                created=int(time.time()),
                model=model,
                choices=[StreamChoice(index=0, delta=Delta(), finish_reason=None)],
            )

        elif event_type == "content_block_start":
            block = data.get("content_block", {})
            if block.get("type") == "text":
                return StreamChunk(
                    id="",
                    object="chat.completion.chunk",
                    created=int(time.time()),
                    model=model,
                    choices=[StreamChoice(index=0, delta=Delta(role="assistant", content=""), finish_reason=None)],
                )

        elif event_type == "content_block_delta":
            delta_data = data.get("delta", {})
            if delta_data.get("type") == "text_delta":
                return StreamChunk(
                    id="",
                    object="chat.completion.chunk",
                    created=int(time.time()),
                    model=model,
                    choices=[
                        StreamChoice(
                            index=0, delta=Delta(content=delta_data.get("text", "")), finish_reason=None
                        )
                    ],
                )

        elif event_type == "message_delta":
            stop_reason = data.get("delta", {}).get("stop_reason")
            usage_data = data.get("usage", {})
            usage = None
            if usage_data:
                usage = Usage(
                    prompt_tokens=0,
                    completion_tokens=usage_data.get("output_tokens", 0),
                    total_tokens=usage_data.get("output_tokens", 0),
                )

            return StreamChunk(
                id="",
                object="chat.completion.chunk",
                created=int(time.time()),
                model=model,
                choices=[StreamChoice(index=0, delta=Delta(), finish_reason=stop_reason)],
                usage=usage,
            )

        return None

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
        """Make a completion request to Anthropic."""
        payload = self._prepare_request(
            model, messages, temperature, max_tokens, stream, tools, tool_choice, response_format, **kwargs
        )

        url = f"{self.api_base}/messages"
        headers = self._get_headers()

        with httpx.Client(timeout=self.timeout) as client:
            if stream:
                return self._stream_completion(client, url, headers, payload, model)
            else:
                response = client.post(url, json=payload, headers=headers)

                if response.status_code != 200:
                    self._handle_error(response.status_code, response.text, model, "anthropic")

                return self._parse_response(response.json(), model)

    def _stream_completion(
        self, client: httpx.Client, url: str, headers: Dict[str, str], payload: Dict[str, Any], model: str
    ) -> Iterator[StreamChunk]:
        """Handle streaming completion."""
        with client.stream("POST", url, json=payload, headers=headers) as response:
            if response.status_code != 200:
                error_text = ""
                for chunk in response.iter_text():
                    error_text += chunk
                self._handle_error(response.status_code, error_text, model, "anthropic")

            for line in response.iter_lines():
                if line.startswith("data: "):
                    data_str = line[6:]
                    try:
                        data = json.loads(data_str)
                        chunk = self._parse_stream_chunk(data, model)
                        if chunk:
                            yield chunk
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
        """Make an async completion request to Anthropic."""
        payload = self._prepare_request(
            model, messages, temperature, max_tokens, stream, tools, tool_choice, response_format, **kwargs
        )

        url = f"{self.api_base}/messages"
        headers = self._get_headers()

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            if stream:
                return self._astream_completion(client, url, headers, payload, model)
            else:
                response = await client.post(url, json=payload, headers=headers)

                if response.status_code != 200:
                    self._handle_error(response.status_code, response.text, model, "anthropic")

                return self._parse_response(response.json(), model)

    async def _astream_completion(
        self, client: httpx.AsyncClient, url: str, headers: Dict[str, str], payload: Dict[str, Any], model: str
    ) -> AsyncIterator[StreamChunk]:
        """Handle async streaming completion."""
        async with client.stream("POST", url, json=payload, headers=headers) as response:
            if response.status_code != 200:
                error_text = ""
                async for chunk in response.aiter_text():
                    error_text += chunk
                self._handle_error(response.status_code, error_text, model, "anthropic")

            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    data_str = line[6:]
                    try:
                        data = json.loads(data_str)
                        chunk = self._parse_stream_chunk(data, model)
                        if chunk:
                            yield chunk
                    except json.JSONDecodeError:
                        continue
