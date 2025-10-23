# CLAUDE.md - Development Journal & Architectural Decisions

This document serves as a development journal and architectural decision record for ullm. It's designed to help AI assistants (like Claude) understand the project's design philosophy and history when working on future iterations.

## Project Genesis

### Problem Statement
litellm is an excellent unified interface for LLMs but has significant overhead:
- ~200MB memory footprint
- ~1.2s import time
- 50+ dependencies
- Loads all 100+ provider implementations upfront

For DSPy users who typically use only 1-2 providers, this is excessive overhead.

### Solution: ullm (μLLM)
A lightweight, focused alternative that:
- Supports only 4 core providers (OpenAI, Anthropic, Groq, AWS Bedrock)
- Maintains API compatibility with litellm
- Uses modern, efficient tooling
- Minimizes dependencies and memory usage

---

## Architectural Decisions

### ADR-001: Use httpx for HTTP (not requests + aiohttp)

**Decision**: Use httpx as the single HTTP library for both sync and async operations.

**Rationale**:
- Single library reduces dependencies and import overhead
- httpx is modern and built for async-first design
- Supports both sync and async with same API
- ~2MB dependency vs ~3MB for requests + aiohttp
- Excellent streaming support
- Python 3.8+ compatible

**Alternatives Considered**:
- `requests + aiohttp`: More established but 2 dependencies, larger footprint
- `urllib`: Built-in but cumbersome async support

**Status**: Implemented ✅

---

### ADR-002: Use tenacity for retry logic (not manual implementation)

**Decision**: Use tenacity library for exponential backoff retry logic.

**Rationale**:
- Well-tested, battle-hardened library
- Configurable retry strategies
- Adds only ~200KB
- Decorators make code cleaner
- litellm uses similar approach
- Handles edge cases (jitter, max delay, etc.)

**Alternatives Considered**:
- Manual implementation: ~50 lines of code, but reinventing the wheel
- No retries: Not production-ready for flaky APIs

**Status**: Implemented ✅

---

### ADR-003: No built-in caching layer

**Decision**: Do not implement caching in ullm itself.

**Rationale**:
- DSPy already has its own caching mechanism
- Caching adds complexity and state management
- Would increase memory footprint
- Different use cases need different caching strategies
- Users can add their own caching layer if needed
- Accept `cache` parameter for API compatibility but ignore it

**Alternatives Considered**:
- Simple in-memory cache: Adds state, not thread-safe
- Disk-based cache: Adds I/O overhead and dependencies

**Status**: Implemented (passthrough only) ✅

---

### ADR-004: Pydantic v2 for type validation

**Decision**: Use Pydantic v2 for response types and validation.

**Rationale**:
- Modern, fast (Rust core)
- Excellent JSON schema generation
- Type-safe models
- litellm uses similar approach
- Supports structured output validation
- ~1MB dependency

**Performance Consideration**:
- Pydantic v2 is 5-50x faster than v1
- Negligible overhead for response parsing
- Benefits outweigh costs for type safety

**Status**: Implemented ✅

---

### ADR-005: Provider-specific client classes

**Decision**: Separate client class for each provider (OpenAI, Anthropic, Groq, Bedrock).

**Rationale**:
- Clean separation of concerns
- Each provider has unique API quirks
- Easy to add/remove providers
- Groq can inherit from OpenAI (API-compatible)
- Testable in isolation
- Clear error messages per provider

**Structure**:
```python
BaseClient (ABC)
├── OpenAIClient
├── AnthropicClient
├── GroqClient (inherits OpenAIClient)
└── BedrockClient
```

**Status**: Implemented ✅

---

### ADR-006: Support only chat completion (not legacy text completion)

**Decision**: Implement `completion()` and `responses()` APIs, skip legacy text completion.

**Rationale**:
- Chat completion is the modern API used by DSPy
- Text completion is legacy (GPT-3 era)
- Simplifies code and reduces maintenance
- Can add later if needed
- 95% of use cases use chat completion

**Compatibility Note**:
- litellm has `text_completion()` but DSPy rarely uses it
- `responses()` API handles OpenAI's newer Responses API format

**Status**: Implemented (chat + responses only) ✅

---

### ADR-007: Minimal Python 3.8+ support

**Decision**: Target Python 3.8+ (same as litellm).

**Rationale**:
- Python 3.8+ has good ecosystem support
- DSPy targets similar range
- Allows use of modern syntax (type hints, async/await)
- 3.8 EOL is Oct 2024, but still widely used

**Note**: Considered 3.9+ for better type hints, but stayed with 3.8 for compatibility.

**Status**: Implemented ✅ (though mypy configured for 3.9)

---

### ADR-008: Streaming returns iterators, not wrapper objects

**Decision**: Streaming returns bare Iterator/AsyncIterator, not custom wrapper classes.

**Rationale**:
- Simpler API
- More Pythonic
- litellm's streaming wrappers add complexity
- Users can easily iterate: `for chunk in response`
- No need for `.iter()` or `.aiter()` methods

**Status**: Implemented ✅

---

### ADR-009: Tool calling uses OpenAI format (not provider-specific)

**Decision**: Always accept and return tools in OpenAI format, convert internally per provider.

**Rationale**:
- OpenAI format is most common
- Easier for users (one format to learn)
- Internal conversion keeps API clean
- Anthropic and others have similar concepts

**Conversion Handling**:
- OpenAI: Pass through as-is
- Anthropic: Convert to `tools` with `input_schema`
- Groq: Uses OpenAI format (compatible)
- Bedrock: Convert based on model

**Status**: Implemented ✅

---

### ADR-010: Structured output via Pydantic, not JSON mode alone

**Decision**: Accept `response_format` as either `{"type": "json_object"}` or a Pydantic model class.

**Rationale**:
- Pydantic models provide schema + validation
- Automatic JSON schema generation
- Type-safe parsing
- Better than raw JSON strings
- Compatible with OpenAI's JSON mode

**Implementation**:
```python
response_format = Person  # Pydantic model
# Converts to: {"type": "json_schema", "json_schema": {...}}
```

**Status**: Implemented ✅

---

### ADR-011: Error handling with custom exception types

**Decision**: Define exception hierarchy matching litellm's exceptions.

**Rationale**:
- Predictable error handling for users
- Easy to catch specific error types
- Compatible with existing DSPy error handling
- Include model and provider info in exceptions

**Exception Hierarchy**:
```python
UllmException (base)
├── AuthenticationError (401)
├── BadRequestError (400)
├── RateLimitError (429)
├── Timeout (504)
└── APIError (500+)
```

**Status**: Implemented ✅

---

### ADR-012: Use uv for development tooling

**Decision**: Use `uv` for package management, not pip or poetry.

**Rationale**:
- Fastest Python package installer (~10-100x faster)
- Modern tool by Astral (makers of ruff)
- Simple, no lock files for library
- Growing ecosystem support
- Future-proof choice

**Status**: Implemented ✅

---

### ADR-013: Use ruff for linting and formatting (not black + flake8)

**Decision**: Use ruff as single tool for linting and formatting.

**Rationale**:
- 10-100x faster than black + flake8
- Single tool, one config
- Rust-based, well-maintained
- Includes isort, pyupgrade, etc.
- Becoming industry standard

**Status**: Implemented ✅

---

### ADR-014: Relaxed mypy config for pragmatism

**Decision**: Use relaxed mypy settings, not strict mode.

**Rationale**:
- Some type errors from dynamic provider dispatch
- Boto3 has poor type stubs
- Async return types complex with Union[ModelResponse, Iterator]
- Pragmatic approach for MVP
- Can tighten later if needed

**Config**:
```toml
[tool.mypy]
python_version = "3.9"
strict = false
check_untyped_defs = true
```

**Status**: Implemented ✅

---

### ADR-015: Bedrock uses boto3 (optional dependency)

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

**Status**: Implemented ✅

---

## Known Limitations & Trade-offs

### 1. Limited Provider Support
**Limitation**: Only 4 providers vs 100+ in litellm.
**Trade-off**: Dramatically smaller footprint, easier maintenance.
**Mitigation**: Can add more providers if needed. Most DSPy users only need 1-2.

### 2. No Built-in Caching
**Limitation**: No response caching built-in.
**Trade-off**: Smaller, simpler codebase. DSPy has its own caching.
**Mitigation**: Users can implement their own caching wrapper.

### 3. Bedrock Async Uses Thread Pool
**Limitation**: boto3 is synchronous, so async uses thread pool.
**Trade-off**: Not truly async, but functional.
**Mitigation**: Could use aioboto3 in future (adds dependency).

### 4. No Legacy Text Completion API
**Limitation**: No `text_completion()` function.
**Trade-off**: Simpler codebase, modern API focus.
**Mitigation**: 95% of use cases use chat completion. Can add if needed.

### 5. Streaming Doesn't Support Chunked Tool Calls
**Limitation**: Tool calls in streaming are passed through as deltas, not aggregated.
**Trade-off**: Simpler implementation, good enough for most use cases.
**Mitigation**: Users can aggregate tool call chunks themselves if needed.

---

## Code Organization Principles

### 1. Clear Separation of Concerns
- `main.py`: Entry points, retry logic, provider dispatch
- `providers.py`: Provider resolution (model name → provider)
- `types.py`: Response types, Pydantic models
- `exceptions.py`: Exception classes
- `clients/`: Provider-specific implementations

### 2. Minimal Abstraction
- No unnecessary base classes or interfaces beyond BaseClient
- Direct, readable code over clever abstractions
- Explicit over implicit

### 3. Type Hints Everywhere
- Full type hints in public API
- Helps IDEs and users
- Documents expected types

### 4. Defensive Programming
- Validate inputs early
- Clear error messages
- Graceful degradation (e.g., boto3 missing)

---

## Testing Strategy

### Unit Tests
- Provider resolution logic
- Type model creation/validation
- Exception handling
- Auto-detection features

### Integration Tests
- Skipped without API keys (CI-friendly)
- Cover each provider when keys available
- Test streaming, tool calling, structured output

### Coverage Goals
- 80%+ for core logic (providers, types, exceptions)
- Lower for client implementations (require API keys)
- Focus on critical paths

---

## Future Considerations

### Potential Additions (Priority Order)

#### 1. Embeddings API (Medium Priority)
```python
ullm.embedding(model="openai/text-embedding-3-small", input=["text"])
```
**Rationale**: DSPy uses embeddings for retrieval.
**Effort**: Low (similar structure to completion)
**Bloat**: Minimal

#### 2. Additional Providers (Low Priority)
Possible additions:
- Cohere (good for embedding + reranking)
- Together AI (good for open models)
- Replicate (for open models)

**Rationale**: Only if users request them.
**Effort**: Low per provider (follow same pattern)

#### 3. Cost Tracking (Low Priority)
```python
response = ullm.completion(...)
print(f"Cost: ${response.usage.cost}")
```
**Rationale**: Useful for monitoring.
**Effort**: Low (just pricing tables)
**Bloat**: Minimal (~10KB pricing data)

#### 4. Lightweight Caching (Low Priority)
Optional in-memory LRU cache:
```python
ullm.configure(cache={"enabled": True, "max_size": 1000})
```
**Rationale**: Some users may want it.
**Effort**: Medium (add cachetools dependency)
**Bloat**: +500KB

#### 5. Image Input Support (Medium Priority)
For vision models (GPT-4V, Claude 3):
```python
messages = [{
    "role": "user",
    "content": [
        {"type": "text", "text": "What's in this image?"},
        {"type": "image_url", "image_url": {"url": "..."}}
    ]
}]
```
**Rationale**: Vision is becoming more common.
**Effort**: Low (mostly pass-through)

#### 6. Batch API Support (Low Priority)
For OpenAI's batch API.
**Rationale**: Cost savings for async workflows.
**Effort**: Medium (different API pattern)

### Things to NOT Add
- ❌ Proxy server mode (out of scope)
- ❌ Spend analytics dashboard (use separate tools)
- ❌ Fine-tuning API (different use case)
- ❌ Prompt templates (DSPy handles this)
- ❌ Evaluation frameworks (DSPy handles this)

---

## Performance Optimization Notes

### Import Time Optimization
- Lazy imports where possible
- No unnecessary __init__.py imports
- Defer boto3 import until needed

### Memory Optimization
- No global state
- No pre-loaded model configs
- Stream large responses

### Request Optimization
- Keep-alive connections via httpx
- Reuse HTTP client instances where possible
- Stream by default for large responses

---

## Migration Guide: litellm → ullm

For users switching from litellm to ullm:

### 1. Installation
```bash
pip uninstall litellm
pip install ullm[aws]  # if using Bedrock
```

### 2. Code Changes
```python
# Before
import litellm
response = litellm.completion(model="openai/gpt-4", messages=[...])

# After
import ullm
response = ullm.completion(model="openai/gpt-4", messages=[...])
```

### 3. Compatibility Notes
- ✅ `completion()` - Direct replacement
- ✅ `acompletion()` - Direct replacement
- ✅ `responses()` - Direct replacement
- ❌ `text_completion()` - Not supported (use `completion()`)
- ❌ `set_verbose()` - Not needed (no logging)
- ⚠️ `cache` parameter - Accepted but ignored

### 4. DSPy Integration
In DSPy's `clients/lm.py`:
```python
# Option 1: Replace import
# import litellm
import ullm as litellm

# Option 2: Patch at runtime
import ullm
import sys
sys.modules['litellm'] = ullm
```

---

## Development Workflow

### Adding a New Provider

1. Create client class in `ullm/clients/new_provider.py`:
```python
class NewProviderClient(BaseClient):
    def _get_api_key_from_env(self):
        return os.getenv("NEW_PROVIDER_API_KEY")

    def completion(self, model, messages, **kwargs):
        # Implement...
```

2. Register in `ullm/providers.py`:
```python
SUPPORTED_PROVIDERS = [..., "new_provider"]
```

3. Add to factory in `ullm/main.py`:
```python
elif provider == "new_provider":
    return NewProviderClient(**kwargs)
```

4. Add tests in `tests/test_new_provider.py`

5. Update documentation

### Making a Release

1. Update version in `pyproject.toml`
2. Update `CHANGELOG.md`
3. Commit: `git commit -m "Bump version to X.Y.Z"`
4. Tag: `git tag vX.Y.Z`
5. Push: `git push && git push --tags`
6. Create GitHub release (triggers CI to publish to PyPI)

---

## Common Issues & Solutions

### Issue: httpx SSLError
**Solution**: Update system certificates or set `verify=False` (not recommended).

### Issue: Bedrock region mismatch
**Solution**: Set `AWS_REGION_NAME` or pass `region_name=` parameter.

### Issue: Token counting differs from litellm
**Solution**: We use provider-reported token counts (more accurate).

### Issue: Streaming chunks differ slightly
**Solution**: We return raw provider chunks, litellm sometimes aggregates.

---

## Maintenance Notes

### Dependencies to Watch
- **httpx**: Update for security patches
- **pydantic**: Update cautiously (breaking changes in v3?)
- **tenacity**: Stable, rarely needs updates
- **boto3**: Update for new Bedrock features

### Breaking Changes to Avoid
- Changing response types (ModelResponse, etc.)
- Changing exception types
- Changing function signatures
- Removing providers

### When to Bump Version
- Patch (0.1.X): Bug fixes, docs
- Minor (0.X.0): New features, new providers
- Major (X.0.0): Breaking API changes

---

## Design Philosophy

1. **Lightweight First**: Every line of code and dependency must justify its existence.
2. **Compatibility Second**: Stay compatible with litellm where practical, but not at cost of bloat.
3. **Modern Tooling**: Use the best tools of 2025 (uv, ruff, httpx).
4. **Pragmatic Over Perfect**: Ship working code, iterate based on feedback.
5. **Clear Over Clever**: Readable code beats clever abstractions.

---

## Questions for Future Iterations

1. Should we add embeddings API?
2. Should we support more providers? Which ones?
3. Should we add optional caching layer?
4. Should we support image inputs?
5. Should we provide a compatibility shim for DSPy?
6. Should we add cost tracking?
7. Should we support streaming tool calls better?
8. Should we add batch API support?

---

## Resources

- litellm source: https://github.com/BerriAI/litellm
- DSPy source: https://github.com/stanfordnlp/dspy
- httpx docs: https://www.python-httpx.org/
- Pydantic docs: https://docs.pydantic.dev/
- OpenAI API: https://platform.openai.com/docs/api-reference
- Anthropic API: https://docs.anthropic.com/
- Groq API: https://console.groq.com/docs
- AWS Bedrock: https://docs.aws.amazon.com/bedrock/

---

**Last Updated**: 2025-01-XX (Initial version)
**Project Status**: ✅ Production-ready MVP
**Next Review**: After 1-2 months of real-world usage
