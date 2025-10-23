"""Response types for ullm - compatible with litellm types."""

from typing import Any, Dict, List, Literal, Optional, Union

from pydantic import BaseModel


class FunctionCall(BaseModel):
    """Function call in a message."""

    name: str
    arguments: str  # JSON string


class ToolCall(BaseModel):
    """Tool call in a message."""

    id: str
    type: Literal["function"] = "function"
    function: FunctionCall


class Message(BaseModel):
    """Message in a completion response."""

    role: Literal["system", "user", "assistant", "tool"]
    content: Optional[str] = None
    tool_calls: Optional[List[ToolCall]] = None
    function_call: Optional[FunctionCall] = None  # Legacy support
    name: Optional[str] = None


class Usage(BaseModel):
    """Token usage information."""

    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class Choice(BaseModel):
    """A choice in a completion response."""

    index: int
    message: Message
    finish_reason: Optional[str] = None
    logprobs: Optional[Any] = None


class ModelResponse(BaseModel):
    """Standard completion response - compatible with litellm.ModelResponse."""

    id: str
    object: str = "chat.completion"
    created: int
    model: str
    choices: List[Choice]
    usage: Optional[Usage] = None
    system_fingerprint: Optional[str] = None


class Delta(BaseModel):
    """Delta in a streaming chunk."""

    role: Optional[str] = None
    content: Optional[str] = None
    tool_calls: Optional[List[Dict[str, Any]]] = None
    function_call: Optional[Dict[str, Any]] = None


class StreamChoice(BaseModel):
    """A choice in a streaming response."""

    index: int
    delta: Delta
    finish_reason: Optional[str] = None
    logprobs: Optional[Any] = None


class StreamChunk(BaseModel):
    """Streaming chunk - compatible with litellm streaming."""

    id: str
    object: str = "chat.completion.chunk"
    created: int
    model: str
    choices: List[StreamChoice]
    usage: Optional[Usage] = None
    system_fingerprint: Optional[str] = None


class Function(BaseModel):
    """Function definition for tool calling."""

    name: str
    description: Optional[str] = None
    parameters: Dict[str, Any]


class Tool(BaseModel):
    """Tool definition."""

    type: Literal["function"] = "function"
    function: Function


class ResponseFormatType(BaseModel):
    """Response format specification."""

    type: Literal["text", "json_object"] = "text"


# Type alias for response format
ResponseFormat = Union[ResponseFormatType, type[BaseModel]]
