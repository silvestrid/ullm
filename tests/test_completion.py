"""Tests for completion API (integration tests - require API keys)."""

import os

import pytest

import ullm
from ullm.exceptions import AuthenticationError


@pytest.mark.skipif(not os.getenv("OPENAI_API_KEY"), reason="OPENAI_API_KEY not set")
def test_openai_completion():
    """Test OpenAI completion."""
    response = ullm.completion(
        model="openai/gpt-4o-mini", messages=[{"role": "user", "content": "Say hello!"}], max_tokens=50
    )

    assert isinstance(response, ullm.ModelResponse)
    assert len(response.choices) > 0
    assert response.choices[0].message.content is not None
    assert response.usage is not None
    assert response.usage.total_tokens > 0


@pytest.mark.skipif(not os.getenv("OPENAI_API_KEY"), reason="OPENAI_API_KEY not set")
def test_openai_streaming():
    """Test OpenAI streaming."""
    response = ullm.completion(
        model="openai/gpt-4o-mini", messages=[{"role": "user", "content": "Count to 3"}], stream=True, max_tokens=50
    )

    chunks = list(response)
    assert len(chunks) > 0

    # Check that we got content
    content = "".join(chunk.choices[0].delta.content or "" for chunk in chunks)
    assert len(content) > 0


@pytest.mark.skipif(not os.getenv("OPENAI_API_KEY"), reason="OPENAI_API_KEY not set")
def test_openai_tool_calling():
    """Test OpenAI tool calling."""
    tools = [
        {
            "type": "function",
            "function": {
                "name": "get_weather",
                "description": "Get weather for a location",
                "parameters": {
                    "type": "object",
                    "properties": {"location": {"type": "string"}},
                    "required": ["location"],
                },
            },
        }
    ]

    response = ullm.completion(
        model="openai/gpt-4o-mini",
        messages=[{"role": "user", "content": "What's the weather in San Francisco?"}],
        tools=tools,
        max_tokens=100,
    )

    assert isinstance(response, ullm.ModelResponse)
    # Note: Tool calls are not guaranteed, model might just respond with text


@pytest.mark.skipif(not os.getenv("ANTHROPIC_API_KEY"), reason="ANTHROPIC_API_KEY not set")
def test_anthropic_completion():
    """Test Anthropic completion."""
    response = ullm.completion(
        model="anthropic/claude-3-5-haiku-20241022", messages=[{"role": "user", "content": "Say hello!"}], max_tokens=50
    )

    assert isinstance(response, ullm.ModelResponse)
    assert len(response.choices) > 0
    assert response.choices[0].message.content is not None
    assert response.usage is not None


@pytest.mark.skipif(not os.getenv("ANTHROPIC_API_KEY"), reason="ANTHROPIC_API_KEY not set")
def test_anthropic_streaming():
    """Test Anthropic streaming."""
    response = ullm.completion(
        model="anthropic/claude-3-5-haiku-20241022",
        messages=[{"role": "user", "content": "Count to 3"}],
        stream=True,
        max_tokens=50,
    )

    chunks = list(response)
    assert len(chunks) > 0


@pytest.mark.skipif(not os.getenv("GROQ_API_KEY"), reason="GROQ_API_KEY not set")
def test_groq_completion():
    """Test Groq completion."""
    response = ullm.completion(
        model="groq/llama-3.1-8b-instant", messages=[{"role": "user", "content": "Say hello!"}], max_tokens=50
    )

    assert isinstance(response, ullm.ModelResponse)
    assert len(response.choices) > 0
    assert response.choices[0].message.content is not None


@pytest.mark.asyncio
@pytest.mark.skipif(not os.getenv("OPENAI_API_KEY"), reason="OPENAI_API_KEY not set")
async def test_async_completion():
    """Test async completion."""
    response = await ullm.acompletion(
        model="openai/gpt-4o-mini", messages=[{"role": "user", "content": "Say hello!"}], max_tokens=50
    )

    assert isinstance(response, ullm.ModelResponse)
    assert len(response.choices) > 0
    assert response.choices[0].message.content is not None


def test_invalid_api_key():
    """Test that invalid API key raises AuthenticationError."""
    with pytest.raises(AuthenticationError):
        ullm.completion(
            model="openai/gpt-4", messages=[{"role": "user", "content": "Hello"}], api_key="invalid", max_tokens=10
        )


def test_auto_provider_detection():
    """Test automatic provider detection."""
    # This will fail without API key, but tests provider resolution
    try:
        ullm.completion(model="gpt-4o-mini", messages=[{"role": "user", "content": "Hello"}], max_tokens=10)
    except AuthenticationError:
        pass  # Expected without API key


def test_structured_output_with_pydantic():
    """Test structured output with Pydantic model."""
    from pydantic import BaseModel

    class Person(BaseModel):
        name: str
        age: int

    # Test schema generation
    schema = Person.model_json_schema()
    assert "properties" in schema
    assert "name" in schema["properties"]
    assert "age" in schema["properties"]
