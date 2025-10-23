"""AWS Bedrock provider client."""

import json
import os
import time
from typing import Any, AsyncIterator, Dict, Iterator, Optional, Union

from ullm.clients.base import BaseClient
from ullm.exceptions import BadRequestError
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


@register_client("bedrock")
class BedrockClient(BaseClient):
    """Client for AWS Bedrock API."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        api_base: Optional[str] = None,
        timeout: float = 600.0,
        region_name: Optional[str] = None,
        **kwargs: Any,
    ):
        super().__init__(api_key, api_base, timeout, **kwargs)
        self.region_name = region_name or os.getenv("AWS_REGION_NAME", "us-east-1")
        self._boto3_client = None

    def _get_api_key_from_env(self) -> Optional[str]:
        # Bedrock uses AWS credentials, not a simple API key
        return None

    def _get_default_api_base(self) -> str:
        return ""  # Bedrock uses boto3, not HTTP directly

    def _get_boto3_client(self) -> Any:
        """Get or create boto3 Bedrock runtime client."""
        if self._boto3_client is None:
            try:
                import boto3
            except ImportError:
                raise BadRequestError(
                    "boto3 is required for AWS Bedrock. Install with: pip install ullm[aws]",
                    model="bedrock",
                    llm_provider="bedrock",
                )

            # Use credentials from environment or IAM role
            self._boto3_client = boto3.client(
                "bedrock-runtime",
                region_name=self.region_name,
                aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
                aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
                aws_session_token=os.getenv("AWS_SESSION_TOKEN"),
            )

        return self._boto3_client

    def _prepare_bedrock_request(
        self,
        model: str,
        messages: list[Dict[str, Any]],
        temperature: Optional[float],
        max_tokens: Optional[int],
        tools: Optional[list[Tool]],
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Prepare request for Bedrock based on model type."""
        # Bedrock supports multiple model families, we'll focus on Anthropic Claude via Bedrock
        # Model IDs look like: anthropic.claude-3-sonnet-20240229-v1:0

        # Extract system message
        system_message = None
        bedrock_messages = []

        for msg in messages:
            role = msg.get("role")
            content = msg.get("content")

            if role == "system":
                system_message = content
            else:
                bedrock_messages.append({"role": role, "content": content})

        payload: Dict[str, Any] = {
            "messages": bedrock_messages,
            "max_tokens": max_tokens or 4096,
        }

        if system_message:
            payload["system"] = system_message

        if temperature is not None:
            payload["temperature"] = temperature

        # Convert tools if provided
        if tools:
            bedrock_tools = []
            for tool in tools:
                tool_dict = tool.model_dump() if hasattr(tool, "model_dump") else tool
                func = tool_dict.get("function", {})
                bedrock_tools.append(
                    {
                        "name": func.get("name"),
                        "description": func.get("description", ""),
                        "input_schema": func.get("parameters", {}),
                    }
                )
            payload["tools"] = bedrock_tools

        # Anthropic-specific parameters
        payload["anthropic_version"] = "bedrock-2023-05-31"

        return payload

    def _parse_bedrock_response(self, data: Dict[str, Any], model: str) -> ModelResponse:
        """Parse Bedrock response (Anthropic format) into ModelResponse."""
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
                        function=FunctionCall(name=block.get("name", ""), arguments=json.dumps(block.get("input", {}))),
                    )
                )

        message = Message(
            role="assistant",
            content=text_content if text_content else None,
            tool_calls=tool_calls if tool_calls else None,
        )

        choice = Choice(index=0, message=message, finish_reason=data.get("stop_reason"))

        usage_data = data.get("usage", {})
        usage = Usage(
            prompt_tokens=usage_data.get("input_tokens", 0),
            completion_tokens=usage_data.get("output_tokens", 0),
            total_tokens=usage_data.get("input_tokens", 0) + usage_data.get("output_tokens", 0),
        )

        return ModelResponse(
            id=data.get("id", "bedrock-" + str(int(time.time()))),
            object="chat.completion",
            created=int(time.time()),
            model=model,
            choices=[choice],
            usage=usage,
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
        """Make a completion request to AWS Bedrock."""
        if stream:
            return self._stream_completion(model, messages, temperature, max_tokens, tools, **kwargs)

        client = self._get_boto3_client()
        payload = self._prepare_bedrock_request(model, messages, temperature, max_tokens, tools, **kwargs)

        try:
            response = client.invoke_model(modelId=model, body=json.dumps(payload), contentType="application/json")

            response_body = json.loads(response["body"].read())
            return self._parse_bedrock_response(response_body, model)

        except Exception as e:
            error_msg = str(e)
            if "AuthenticationException" in error_msg or "UnrecognizedClientException" in error_msg:
                from ullm.exceptions import AuthenticationError

                raise AuthenticationError(error_msg, model=model, llm_provider="bedrock")
            elif "ValidationException" in error_msg:
                raise BadRequestError(error_msg, model=model, llm_provider="bedrock")
            elif "ThrottlingException" in error_msg:
                from ullm.exceptions import RateLimitError

                raise RateLimitError(error_msg, model=model, llm_provider="bedrock")
            else:
                from ullm.exceptions import APIError

                raise APIError(error_msg, model=model, llm_provider="bedrock")

    def _stream_completion(
        self,
        model: str,
        messages: list[Dict[str, Any]],
        temperature: Optional[float],
        max_tokens: Optional[int],
        tools: Optional[list[Tool]],
        **kwargs: Any,
    ) -> Iterator[StreamChunk]:
        """Handle streaming completion for Bedrock."""
        client = self._get_boto3_client()
        payload = self._prepare_bedrock_request(model, messages, temperature, max_tokens, tools, **kwargs)

        try:
            response = client.invoke_model_with_response_stream(
                modelId=model, body=json.dumps(payload), contentType="application/json"
            )

            for event in response["body"]:
                chunk_data = json.loads(event["chunk"]["bytes"])
                chunk = self._parse_bedrock_stream_chunk(chunk_data, model)
                if chunk:
                    yield chunk

        except Exception as e:
            error_msg = str(e)
            if "AuthenticationException" in error_msg:
                from ullm.exceptions import AuthenticationError

                raise AuthenticationError(error_msg, model=model, llm_provider="bedrock")
            else:
                from ullm.exceptions import APIError

                raise APIError(error_msg, model=model, llm_provider="bedrock")

    def _parse_bedrock_stream_chunk(self, data: Dict[str, Any], model: str) -> Optional[StreamChunk]:
        """Parse Bedrock streaming chunk."""
        event_type = data.get("type")

        if event_type == "message_start":
            return StreamChunk(
                id=data.get("message", {}).get("id", ""),
                object="chat.completion.chunk",
                created=int(time.time()),
                model=model,
                choices=[StreamChoice(index=0, delta=Delta(), finish_reason=None)],
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
                        StreamChoice(index=0, delta=Delta(content=delta_data.get("text", "")), finish_reason=None)
                    ],
                )

        elif event_type == "message_delta":
            stop_reason = data.get("delta", {}).get("stop_reason")
            return StreamChunk(
                id="",
                object="chat.completion.chunk",
                created=int(time.time()),
                model=model,
                choices=[StreamChoice(index=0, delta=Delta(), finish_reason=stop_reason)],
            )

        return None

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
        """
        Async completion for Bedrock.
        Note: boto3 doesn't have async support, so we use sync in thread pool.
        For production use, consider aioboto3.
        """
        import asyncio

        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            lambda: self.completion(
                model, messages, temperature, max_tokens, stream, tools, tool_choice, response_format, **kwargs
            ),
        )
