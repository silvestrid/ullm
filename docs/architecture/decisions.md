# Architecture Decision Records

This document records the key architectural decisions made in ullm's design.

## Overview

ullm was created to provide a lightweight alternative to litellm specifically for DSPy users who need minimal overhead while maintaining API compatibility.

### The Problem

litellm is excellent but has significant overhead:

- ~200MB memory footprint
- ~1.2s import time
- 50+ dependencies
- Loads all 100+ provider implementations upfront

### The Solution

ullm (μLLM) provides:

- Only 4 core providers (OpenAI, Anthropic, Groq, AWS Bedrock)
- API compatibility with litellm
- Modern, efficient tooling
- Minimal dependencies (~2MB footprint, 3 dependencies)

---

## ADR-001: Use httpx for HTTP

**Decision**: Use httpx as the single HTTP library for both sync and async operations.

**Rationale**:

- Single library reduces dependencies
- Modern, async-first design
- Supports both sync and async with same API
- Smaller footprint than requests + aiohttp
- Excellent streaming support

**Status**: ✅ Implemented

---

## ADR-002: Use tenacity for retry logic

**Decision**: Use tenacity library for exponential backoff retry logic.

**Rationale**:

- Well-tested, battle-hardened
- Configurable retry strategies
- Only ~200KB overhead
- Handles edge cases (jitter, max delay, etc.)

**Status**: ✅ Implemented

---

## ADR-003: No built-in caching

**Decision**: Do not implement caching in ullm itself.

**Rationale**:

- DSPy already has its own caching
- Caching adds complexity and state
- Would increase memory footprint
- Users can add their own caching layer
- Accept `cache` parameter for API compatibility but ignore it

**Status**: ✅ Implemented (passthrough only)

---

## ADR-004: Pydantic v2 for validation

**Decision**: Use Pydantic v2 for response types and validation.

**Rationale**:

- Modern, fast (Rust core, 5-50x faster than v1)
- Excellent JSON schema generation
- Type-safe models
- Supports structured output validation
- ~1MB dependency

**Status**: ✅ Implemented

---

## ADR-005: Provider-specific client classes

**Decision**: Separate client class for each provider.

**Rationale**:

- Clean separation of concerns
- Each provider has unique API quirks
- Easy to add/remove providers
- Groq can inherit from OpenAI (API-compatible)
- Testable in isolation

**Structure**:
```
BaseClient (ABC)
├── OpenAIClient
├── AnthropicClient
├── GroqClient (inherits OpenAIClient)
└── BedrockClient
```

**Status**: ✅ Implemented

---

## ADR-006: Client Registry Pattern

**Decision**: Use decorator-based registry for client registration instead of if/elif chains.

**Rationale**:

- Cleaner, more maintainable code
- Each client self-registers with `@register_client(provider)`
- No need to modify main.py when adding providers
- Better separation of concerns
- No circular dependencies

**Implementation**:
```python
@register_client("openai")
class OpenAIClient(BaseClient):
    ...
```

**Status**: ✅ Implemented

---

## ADR-007: Minimal Python 3.8+ support

**Decision**: Target Python 3.8+ (same as litellm).

**Rationale**:

- Good ecosystem support
- DSPy targets similar range
- Modern syntax (type hints, async/await)
- Still widely used despite 3.8 EOL

**Status**: ✅ Implemented

---

## ADR-008: Streaming returns iterators

**Decision**: Streaming returns bare Iterator/AsyncIterator, not custom wrapper classes.

**Rationale**:

- Simpler API
- More Pythonic
- litellm's streaming wrappers add complexity
- Easy iteration: `for chunk in response`

**Status**: ✅ Implemented

---

## ADR-009: OpenAI format for tool calling

**Decision**: Always accept and return tools in OpenAI format, convert internally per provider.

**Rationale**:

- OpenAI format is most common
- Easier for users (one format to learn)
- Internal conversion keeps API clean
- All providers have similar concepts

**Status**: ✅ Implemented

---

## ADR-010: Structured output via Pydantic

**Decision**: Accept `response_format` as either `{"type": "json_object"}` or a Pydantic model class.

**Rationale**:

- Pydantic models provide schema + validation
- Automatic JSON schema generation
- Type-safe parsing
- Better than raw JSON strings

**Example**:
```python
class Person(BaseModel):
    name: str
    age: int

response = ullm.completion(
    model="gpt-4o-mini",
    messages=[...],
    response_format=Person
)
```

**Status**: ✅ Implemented

---

## ADR-011: Custom exception hierarchy

**Decision**: Define exception hierarchy matching litellm's exceptions.

**Rationale**:

- Predictable error handling for users
- Easy to catch specific error types
- Compatible with existing DSPy error handling
- Include model and provider info

**Hierarchy**:
```python
UllmException (base)
├── AuthenticationError (401)
├── BadRequestError (400)
├── RateLimitError (429)
├── Timeout (504)
└── APIError (500+)
```

**Status**: ✅ Implemented

---

## ADR-012: Use uv for development

**Decision**: Use `uv` for package management, not pip or poetry.

**Rationale**:

- Fastest Python package installer (10-100x faster)
- Modern tool by Astral (makers of ruff)
- Simple, no lock files for library
- Growing ecosystem support

**Status**: ✅ Implemented

---

## ADR-013: Use ruff for linting/formatting

**Decision**: Use ruff as single tool for linting and formatting.

**Rationale**:

- 10-100x faster than black + flake8
- Single tool, one config
- Rust-based, well-maintained
- Includes isort, pyupgrade, etc.

**Status**: ✅ Implemented

---

## ADR-014: Relaxed mypy configuration

**Decision**: Use relaxed mypy settings, not strict mode.

**Rationale**:

- Some type errors from dynamic provider dispatch
- boto3 has poor type stubs
- Async return types complex with Union[ModelResponse, Iterator]
- Pragmatic approach for MVP

**Status**: ✅ Implemented

---

## ADR-015: boto3 as optional dependency

**Decision**: Make boto3 an optional dependency via extras: `ullm[aws]`.

**Rationale**:

- boto3 is large (~20MB)
- Not all users need AWS Bedrock
- Keeps base install small
- Fails gracefully with clear error message

**Installation**:
```bash
pip install ullm        # No boto3
pip install ullm[aws]   # With boto3
```

**Status**: ✅ Implemented

---

## Design Principles

1. **Lightweight First**: Every line of code and dependency must justify its existence
2. **Compatibility Second**: Stay compatible with litellm where practical, not at cost of bloat
3. **Modern Tooling**: Use the best tools of 2025 (uv, ruff, httpx)
4. **Pragmatic Over Perfect**: Ship working code, iterate based on feedback
5. **Clear Over Clever**: Readable code beats clever abstractions

---

## Known Trade-offs

### 1. Limited Provider Support
**Trade-off**: Only 4 providers vs 100+ in litellm
**Rationale**: Dramatically smaller footprint, easier maintenance. Most DSPy users only need 1-2.

### 2. No Built-in Caching
**Trade-off**: No response caching built-in
**Rationale**: DSPy has its own caching. Keeps ullm simpler and smaller.

### 3. Bedrock Async Uses Thread Pool
**Trade-off**: boto3 is synchronous, so async uses thread pool
**Rationale**: Functional but not truly async. Could use aioboto3 in future.

### 4. No Legacy Text Completion API
**Trade-off**: No `text_completion()` function
**Rationale**: 95% of use cases use chat completion. Can add if needed.

---

## Future Considerations

Potential additions (priority order):

1. **Embeddings API** (Medium) - DSPy uses embeddings for retrieval
2. **Image Input Support** (Medium) - Vision is becoming more common
3. **Additional Providers** (Low) - Only if users request them
4. **Cost Tracking** (Low) - Useful for monitoring
5. **Lightweight Caching** (Low) - Optional in-memory LRU cache

### Things to NOT Add

- ❌ Proxy server mode
- ❌ Spend analytics dashboard
- ❌ Fine-tuning API
- ❌ Prompt templates (DSPy handles this)
- ❌ Evaluation frameworks (DSPy handles this)
