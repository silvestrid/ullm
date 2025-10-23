# ullm Quick Start Guide

## Installation

```bash
# Using pip
pip install ullm

# Using uv (recommended)
uv pip install ullm

# With AWS Bedrock support
pip install ullm[aws]
```

## Basic Usage

### 1. Set API Key

```bash
export OPENAI_API_KEY=sk-...
# or
export ANTHROPIC_API_KEY=sk-ant-...
# or
export GROQ_API_KEY=gsk_...
```

### 2. Simple Completion

```python
import ullm

response = ullm.completion(
    model="openai/gpt-4o-mini",
    messages=[{"role": "user", "content": "Hello!"}]
)

print(response.choices[0].message.content)
```

### 3. Streaming

```python
response = ullm.completion(
    model="openai/gpt-4o-mini",
    messages=[{"role": "user", "content": "Write a poem"}],
    stream=True
)

for chunk in response:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="")
```

### 4. Async

```python
import asyncio

async def main():
    response = await ullm.acompletion(
        model="openai/gpt-4o-mini",
        messages=[{"role": "user", "content": "Hello!"}]
    )
    print(response.choices[0].message.content)

asyncio.run(main())
```

### 5. Tool Calling

```python
tools = [{
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "Get weather for a location",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {"type": "string"}
            },
            "required": ["location"]
        }
    }
}]

response = ullm.completion(
    model="openai/gpt-4o-mini",
    messages=[{"role": "user", "content": "What's the weather in SF?"}],
    tools=tools
)

if response.choices[0].message.tool_calls:
    tool_call = response.choices[0].message.tool_calls[0]
    print(f"Calling: {tool_call.function.name}")
    print(f"Args: {tool_call.function.arguments}")
```

### 6. Structured Output

```python
from pydantic import BaseModel

class Person(BaseModel):
    name: str
    age: int

response = ullm.completion(
    model="openai/gpt-4o-mini",
    messages=[{"role": "user", "content": "Tell me about Alice, age 30"}],
    response_format=Person
)

# Response is JSON matching the schema
print(response.choices[0].message.content)
```

## All Supported Providers

```python
# OpenAI
ullm.completion(model="openai/gpt-4o-mini", messages=[...])
ullm.completion(model="gpt-4o-mini", messages=[...])  # Auto-detected

# Anthropic
ullm.completion(model="anthropic/claude-3-5-sonnet-20241022", messages=[...])

# Groq
ullm.completion(model="groq/llama-3.1-70b-versatile", messages=[...])

# AWS Bedrock
ullm.completion(model="bedrock/anthropic.claude-3-sonnet", messages=[...])
```

## Common Parameters

```python
ullm.completion(
    model="openai/gpt-4o-mini",
    messages=[...],
    temperature=0.7,        # 0-2, controls randomness
    max_tokens=1000,        # Max tokens to generate
    stream=False,           # Enable streaming
    tools=[...],            # Tool/function definitions
    tool_choice="auto",     # "auto", "required", or specific tool
    response_format=Model,  # Pydantic model or {"type": "json_object"}
    num_retries=3,          # Number of retries on failure
    timeout=600.0,          # Request timeout in seconds
    api_key="...",          # Override API key
    api_base="...",         # Override API base URL
)
```

## Error Handling

```python
try:
    response = ullm.completion(model="openai/gpt-4", messages=[...])
except ullm.AuthenticationError:
    print("Invalid API key")
except ullm.RateLimitError:
    print("Rate limit exceeded")
except ullm.BadRequestError:
    print("Invalid request")
except ullm.Timeout:
    print("Request timed out")
except ullm.APIError as e:
    print(f"API error: {e.message}")
```

## Migration from litellm

ullm is designed as a drop-in replacement for litellm:

```python
# Old code with litellm
import litellm
response = litellm.completion(model="openai/gpt-4", messages=[...])

# New code with ullm (same API!)
import ullm
response = ullm.completion(model="openai/gpt-4", messages=[...])
```

Benefits:
- **100x smaller memory footprint** (~2MB vs ~200MB)
- **24x faster imports**
- Same API for core features
- Minimal dependencies

## Examples

Check the `examples/` directory for more:
- `basic_usage.py` - Basic completion examples
- `async_usage.py` - Async and concurrent requests
- `tool_calling.py` - Function/tool calling
- `structured_output.py` - Structured output with Pydantic
- `dspy_integration.py` - Using ullm with DSPy

## Next Steps

- Read the [README](README.md) for full documentation
- Check [CONTRIBUTING](CONTRIBUTING.md) to contribute
- Open issues on [GitHub](https://github.com/yourusername/ullm/issues)
