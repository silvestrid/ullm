# ullm (μLLM)

**Lightweight, fast alternative to litellm** - A minimal unified interface for LLM providers.

[![Tests](https://github.com/silvestrid/ullm/workflows/tests/badge.svg)](https://github.com/silvestrid/ullm/actions)
[![PyPI version](https://badge.fury.io/py/ullm.svg)](https://badge.fury.io/py/ullm)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Documentation](https://img.shields.io/badge/docs-mkdocs-blue.svg)](https://silvestrid.github.io/ullm/)

## Why ullm?

- **🪶 Lightweight**: Only ~2MB in memory vs 200MB for litellm
- **⚡ Fast**: Minimal dependencies, optimized for performance
- **🔌 Compatible**: Drop-in replacement for litellm in most cases
- **🎯 Focused**: Only essential providers (OpenAI, Anthropic, Groq, AWS Bedrock)
- **🛠️ Modern**: Built with httpx, Pydantic v2, and modern Python practices

## Installation

```bash
# Basic installation
pip install ullm

# With AWS Bedrock support
pip install ullm[aws]

# Development installation
pip install ullm[dev]
```

Or with uv (recommended):

```bash
uv pip install ullm
```

## Quick Start

```python
import ullm

# Same API as litellm
response = ullm.completion(
    model="openai/gpt-4",
    messages=[{"role": "user", "content": "Hello!"}]
)
print(response.choices[0].message.content)

# Streaming
response = ullm.completion(
    model="anthropic/claude-3-5-sonnet-20241022",
    messages=[{"role": "user", "content": "Tell me a story"}],
    stream=True
)
for chunk in response:
    print(chunk.choices[0].delta.content, end="")

# Async support
import asyncio

async def main():
    response = await ullm.acompletion(
        model="groq/llama-3.1-70b-versatile",
        messages=[{"role": "user", "content": "Hello!"}]
    )
    print(response.choices[0].message.content)

asyncio.run(main())
```

## Supported Providers

| Provider | Model Format | Example |
|----------|-------------|---------|
| OpenAI | `openai/model-name` | `openai/gpt-4o` |
| Anthropic | `anthropic/model-name` | `anthropic/claude-3-5-sonnet-20241022` |
| Groq | `groq/model-name` | `groq/llama-3.1-70b-versatile` |
| AWS Bedrock | `bedrock/model-id` | `bedrock/anthropic.claude-3-sonnet` |

## Features

### Tool Calling

```python
response = ullm.completion(
    model="openai/gpt-4",
    messages=[{"role": "user", "content": "What's the weather in SF?"}],
    tools=[{
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
)
```

### Structured Output

```python
from pydantic import BaseModel

class Person(BaseModel):
    name: str
    age: int

response = ullm.completion(
    model="openai/gpt-4",
    messages=[{"role": "user", "content": "Tell me about Alice, age 30"}],
    response_format=Person
)
# Response automatically validated against Person schema
```

### Configuration

Environment variables:
```bash
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GROQ_API_KEY=gsk_...
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
AWS_REGION_NAME=us-east-1
```

Or pass directly:
```python
ullm.completion(
    model="openai/gpt-4",
    api_key="sk-...",
    messages=[...]
)
```

## API Compatibility with litellm

ullm is designed as a drop-in replacement for litellm's core functionality:

```python
# litellm code
import litellm
response = litellm.completion(model="gpt-4", messages=[...])

# ullm code (same API)
import ullm
response = ullm.completion(model="gpt-4", messages=[...])
```

**Compatible APIs:**
- ✅ `completion()` / `acompletion()`
- ✅ `responses()` / `aresponses()` (OpenAI responses API)
- ✅ Streaming support
- ✅ Tool calling
- ✅ Structured output with Pydantic
- ✅ Retry logic with exponential backoff
- ✅ Standard exception types

**Not included** (to keep it lightweight):
- ❌ 100+ providers (only 4 core providers)
- ❌ Built-in caching (use dspy's cache or your own)
- ❌ Proxy server mode
- ❌ Spend tracking/analytics
- ❌ Legacy text completion API

## Performance

```
Memory usage comparison (Python 3.11):
litellm: ~200MB
ullm: ~2MB (100x smaller)

Import time:
litellm: ~1.2s
ullm: ~0.05s (24x faster)
```

## Documentation

📚 **[Full documentation available at silvestrid.github.io/ullm](https://silvestrid.github.io/ullm/)**

- [Installation Guide](https://silvestrid.github.io/ullm/getting-started/installation/)
- [Quick Start](https://silvestrid.github.io/ullm/getting-started/quickstart/)
- [API Reference](https://silvestrid.github.io/ullm/api/completion/)
- [Architecture Decisions](https://silvestrid.github.io/ullm/architecture/decisions/)

## Use with DSPy

```python
import dspy
import ullm

# Configure DSPy to use ullm instead of litellm
# Simply replace the import - API is compatible
lm = dspy.LM(model="openai/gpt-4o-mini", temperature=0.7)
dspy.configure(lm=lm)
```

## Development

```bash
# Clone the repo
git clone https://github.com/silvestrid/ullm.git
cd ullm

# Install with uv
uv venv
source .venv/bin/activate  # or `.venv\Scripts\activate` on Windows
uv pip install -e ".[dev]"

# Run tests
pytest

# Lint and format
ruff check .
ruff format .

# Type check
mypy ullm
```

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass and code is formatted
5. Submit a pull request

## License

MIT License - see LICENSE file for details

## Credits

Inspired by [litellm](https://github.com/BerriAI/litellm) - we're grateful for their pioneering work in unified LLM interfaces. ullm aims to provide a more lightweight alternative for users who need core functionality without the overhead.
