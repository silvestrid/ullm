# Basic Usage

Learn the fundamentals of using ullm.

## Simple Completion

The most basic operation is a completion request:

```python
import ullm

response = ullm.completion(
    model="openai/gpt-4o-mini",
    messages=[
        {"role": "user", "content": "Hello!"}
    ]
)

print(response.choices[0].message.content)
```

## Message Format

Messages follow the OpenAI chat format:

```python
messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "What is Python?"},
    {"role": "assistant", "content": "Python is a programming language."},
    {"role": "user", "content": "Tell me more."}
]

response = ullm.completion(model="gpt-4o-mini", messages=messages)
```

### Roles

- **system**: Sets behavior and context
- **user**: User messages
- **assistant**: Assistant responses (for conversation history)

## Model Names

ullm supports multiple formats:

```python
# With provider prefix (recommended)
model="openai/gpt-4o-mini"
model="anthropic/claude-3-5-sonnet-20241022"
model="groq/llama-3.1-70b-versatile"
model="bedrock/anthropic.claude-3-sonnet"

# Auto-detect provider (for well-known models)
model="gpt-4o-mini"              # Detects OpenAI
model="claude-3-5-sonnet-20241022"  # Detects Anthropic
```

## Common Parameters

### Temperature

Controls randomness (0-2):

```python
# More focused and deterministic
response = ullm.completion(
    model="gpt-4o-mini",
    messages=[...],
    temperature=0.0
)

# More creative and random
response = ullm.completion(
    model="gpt-4o-mini",
    messages=[...],
    temperature=1.0
)
```

### Max Tokens

Limit response length:

```python
response = ullm.completion(
    model="gpt-4o-mini",
    messages=[...],
    max_tokens=100  # Limit to 100 tokens
)
```

### Timeout

Set request timeout:

```python
response = ullm.completion(
    model="gpt-4o-mini",
    messages=[...],
    timeout=30.0  # 30 seconds
)
```

## Response Format

The response is a `ModelResponse` object:

```python
response = ullm.completion(model="gpt-4o-mini", messages=[...])

# Access the message content
content = response.choices[0].message.content

# Access usage information
print(f"Prompt tokens: {response.usage.prompt_tokens}")
print(f"Completion tokens: {response.usage.completion_tokens}")
print(f"Total tokens: {response.usage.total_tokens}")

# Access model and other metadata
print(f"Model: {response.model}")
print(f"Finish reason: {response.choices[0].finish_reason}")
```

## API Keys

### From Environment

```bash
export OPENAI_API_KEY=sk-...
export ANTHROPIC_API_KEY=sk-ant-...
export GROQ_API_KEY=gsk_...
```

```python
# Keys automatically loaded from environment
response = ullm.completion(
    model="gpt-4o-mini",
    messages=[...]
)
```

### Direct Pass

```python
response = ullm.completion(
    model="gpt-4o-mini",
    messages=[...],
    api_key="sk-..."
)
```

### Custom API Base

```python
response = ullm.completion(
    model="gpt-4o-mini",
    messages=[...],
    api_base="https://custom.openai.endpoint"
)
```

## Error Handling

```python
try:
    response = ullm.completion(
        model="gpt-4o-mini",
        messages=[...]
    )
except ullm.AuthenticationError as e:
    print(f"Invalid API key: {e}")
except ullm.RateLimitError as e:
    print(f"Rate limited: {e}")
except ullm.BadRequestError as e:
    print(f"Bad request: {e}")
except ullm.Timeout as e:
    print(f"Timeout: {e}")
except ullm.APIError as e:
    print(f"API error: {e}")
```

See [Error Handling Guide](../guide/error-handling.md) for details.

## Retry Logic

ullm automatically retries on rate limits and timeouts:

```python
response = ullm.completion(
    model="gpt-4o-mini",
    messages=[...],
    num_retries=3  # Retry up to 3 times (default)
)

# Disable retries
response = ullm.completion(
    model="gpt-4o-mini",
    messages=[...],
    num_retries=0
)
```

## Next Steps

- [Streaming](../guide/streaming.md) - Stream responses
- [Tool Calling](../guide/tool-calling.md) - Use functions/tools
- [Structured Output](../guide/structured-output.md) - Get JSON responses
- [API Reference](../api/completion.md) - Full API documentation
