# Quick Start Guide

Get started with ullm in 5 minutes!

## Installation

```bash
pip install ullm
```

## Set API Key

```bash
export OPENAI_API_KEY=sk-...
```

## Your First Request

```python
import ullm

response = ullm.completion(
    model="openai/gpt-4o-mini",
    messages=[{"role": "user", "content": "Hello!"}]
)

print(response.choices[0].message.content)
```

That's it! You've made your first LLM request with ullm.

## Try Different Providers

=== "OpenAI"

    ```python
    response = ullm.completion(
        model="openai/gpt-4o-mini",
        messages=[{"role": "user", "content": "Hello!"}]
    )
    ```

=== "Anthropic"

    ```python
    # Set key: export ANTHROPIC_API_KEY=sk-ant-...
    response = ullm.completion(
        model="anthropic/claude-3-5-sonnet-20241022",
        messages=[{"role": "user", "content": "Hello!"}]
    )
    ```

=== "Groq"

    ```python
    # Set key: export GROQ_API_KEY=gsk_...
    response = ullm.completion(
        model="groq/llama-3.1-70b-versatile",
        messages=[{"role": "user", "content": "Hello!"}]
    )
    ```

=== "AWS Bedrock"

    ```python
    # Requires: pip install ullm[aws]
    # AWS credentials from environment
    response = ullm.completion(
        model="bedrock/anthropic.claude-3-sonnet",
        messages=[{"role": "user", "content": "Hello!"}]
    )
    ```

## Add Streaming

```python
for chunk in ullm.completion(
    model="openai/gpt-4o-mini",
    messages=[{"role": "user", "content": "Write a poem"}],
    stream=True
):
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="")
```

## Use Async

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

## Control Parameters

```python
response = ullm.completion(
    model="openai/gpt-4o-mini",
    messages=[{"role": "user", "content": "Be creative!"}],
    temperature=0.9,      # More random (0-2)
    max_tokens=500,       # Limit response length
    num_retries=3,        # Retry on failure
    timeout=60.0          # Timeout in seconds
)
```

## Handle Errors

```python
try:
    response = ullm.completion(
        model="openai/gpt-4o-mini",
        messages=[{"role": "user", "content": "Hello!"}]
    )
except ullm.AuthenticationError:
    print("Invalid API key")
except ullm.RateLimitError:
    print("Rate limit exceeded - will auto-retry")
except ullm.APIError as e:
    print(f"API error: {e}")
```

## Next Steps

Now that you're up and running:

- **[Basic Usage](basic-usage.md)** - Learn the fundamentals
- **[User Guide](../guide/overview.md)** - Explore all features
- **[API Reference](../api/completion.md)** - Detailed API docs
- **[Examples](https://github.com/silvestrid/ullm/tree/main/examples)** - See more examples

## Common Issues

!!! question "ModuleNotFoundError: No module named 'ullm'"
    Make sure ullm is installed: `pip install ullm`

!!! question "AuthenticationError: Invalid API key"
    Set your API key: `export OPENAI_API_KEY=sk-...`

!!! question "ImportError: boto3 not found (for Bedrock)"
    Install AWS extras: `pip install ullm[aws]`

!!! question "Different results than litellm?"
    ullm is designed as a drop-in replacement but may have slight differences in token counting or streaming chunk formatting.
