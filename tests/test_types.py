"""Tests for type definitions."""

from ullm.types import (
    Choice,
    FunctionCall,
    Message,
    ModelResponse,
    Tool,
    ToolCall,
    Usage,
)


def test_message_creation():
    """Test Message model creation."""
    msg = Message(role="user", content="Hello")
    assert msg.role == "user"
    assert msg.content == "Hello"
    assert msg.tool_calls is None


def test_message_with_tool_calls():
    """Test Message with tool calls."""
    tool_call = ToolCall(
        id="call_123", type="function", function=FunctionCall(name="get_weather", arguments='{"location": "SF"}')
    )

    msg = Message(role="assistant", content=None, tool_calls=[tool_call])
    assert msg.role == "assistant"
    assert msg.content is None
    assert len(msg.tool_calls) == 1
    assert msg.tool_calls[0].id == "call_123"
    assert msg.tool_calls[0].function.name == "get_weather"


def test_model_response_creation():
    """Test ModelResponse creation."""
    message = Message(role="assistant", content="Hello!")
    choice = Choice(index=0, message=message, finish_reason="stop")
    usage = Usage(prompt_tokens=10, completion_tokens=5, total_tokens=15)

    response = ModelResponse(id="resp_123", created=1234567890, model="gpt-4", choices=[choice], usage=usage)

    assert response.id == "resp_123"
    assert response.model == "gpt-4"
    assert len(response.choices) == 1
    assert response.choices[0].message.content == "Hello!"
    assert response.usage.total_tokens == 15


def test_tool_definition():
    """Test Tool definition."""
    from ullm.types import Function

    func = Function(name="get_weather", description="Get weather info", parameters={"type": "object", "properties": {}})

    tool = Tool(type="function", function=func)

    assert tool.type == "function"
    assert tool.function.name == "get_weather"
    assert tool.function.description == "Get weather info"
