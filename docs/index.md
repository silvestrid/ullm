# ullm - Lightweight LLM Interface

**ullm (μLLM)** is a lightweight, fast alternative to litellm designed specifically for applications that need a minimal, efficient LLM interface.

## Why ullm?

### Performance First

- **100x smaller memory footprint**: ~2MB vs ~200MB for litellm
- **24x faster import time**: ~50ms vs ~1.2s
- **Minimal dependencies**: Only 3 core dependencies

### Production Ready

- ✅ Full litellm API compatibility
- ✅ Async/await support throughout
- ✅ Streaming (sync and async)
- ✅ Tool calling / function calling
- ✅ Structured output with Pydantic
- ✅ Exponential backoff retry logic
- ✅ Comprehensive test coverage

### Supported Providers

| Provider | Models | Status |
|----------|--------|--------|
| **OpenAI** | GPT-4, GPT-3.5, o1, o3, etc. | ✅ Full support |
| **Anthropic** | Claude 3 (Opus, Sonnet, Haiku) | ✅ Full support |
| **Groq** | Llama 3.1, Mixtral, etc. | ✅ Full support |
| **AWS Bedrock** | Claude via Bedrock | ✅ Full support |

## Quick Example

```python
import ullm

# Simple completion
response = ullm.completion(
    model="openai/gpt-4o-mini",
    messages=[{"role": "user", "content": "Hello!"}]
)
print(response.choices[0].message.content)

# Streaming
for chunk in ullm.completion(
    model="anthropic/claude-3-5-sonnet-20241022",
    messages=[{"role": "user", "content": "Tell me a story"}],
    stream=True
):
    print(chunk.choices[0].delta.content, end="")

# Async
import asyncio

async def main():
    response = await ullm.acompletion(
        model="groq/llama-3.1-8b-instant",
        messages=[{"role": "user", "content": "Hi!"}]
    )
    print(response.choices[0].message.content)

asyncio.run(main())
```

## Design Philosophy

1. **Lightweight First**: Every line of code and dependency must justify its existence
2. **Compatibility Second**: Stay compatible with litellm where practical, but not at cost of bloat
3. **Modern Tooling**: Use the best tools (uv, ruff, httpx)
4. **Pragmatic Over Perfect**: Ship working code, iterate based on feedback
5. **Clear Over Clever**: Readable code beats clever abstractions

## Comparison with litellm

| Feature | litellm | ullm | Notes |
|---------|---------|------|-------|
| Memory footprint | ~200MB | ~2MB | 100x smaller |
| Import time | ~1.2s | ~50ms | 24x faster |
| Dependencies | 50+ | 3 | Minimal overhead |
| Providers | 100+ | 4 | Core providers only |
| completion() | ✅ | ✅ | Full compatibility |
| streaming | ✅ | ✅ | Sync and async |
| tool calling | ✅ | ✅ | OpenAI format |
| structured output | ✅ | ✅ | Pydantic support |
| caching | ✅ | ❌ | By design (DSPy has it) |

## Next Steps

<div class="grid cards" markdown>

-   :material-clock-fast:{ .lg .middle } __Quick Start__

    ---

    Get up and running in 5 minutes

    [:octicons-arrow-right-24: Quick Start](getting-started/quickstart.md)

-   :material-book-open-variant:{ .lg .middle } __User Guide__

    ---

    Learn about all features

    [:octicons-arrow-right-24: User Guide](guide/overview.md)

-   :material-api:{ .lg .middle } __API Reference__

    ---

    Detailed API documentation

    [:octicons-arrow-right-24: API Reference](api/completion.md)

-   :material-code-braces:{ .lg .middle } __Contributing__

    ---

    Help improve ullm

    [:octicons-arrow-right-24: Contributing](development/contributing.md)

</div>

## License

ullm is released under the [MIT License](https://github.com/silvestrid/ullm/blob/main/LICENSE).
