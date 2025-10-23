# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-01-XX

### Added
- Initial release of ullm
- Support for OpenAI, Anthropic, Groq, and AWS Bedrock providers
- Chat completion API (`completion()` and `acompletion()`)
- OpenAI Responses API (`responses()` and `aresponses()`)
- Streaming support for all providers
- Tool calling/function calling support
- Structured output with Pydantic models
- Exponential backoff retry logic using tenacity
- Comprehensive test suite
- CI/CD with GitHub Actions
- Full API compatibility with litellm core features
- Examples and documentation

### Features
- 100x smaller memory footprint than litellm (~2MB vs ~200MB)
- 24x faster import time
- Modern Python tooling (uv, ruff, mypy)
- Type hints throughout
- Async/await support
- Minimal dependencies (httpx, pydantic, tenacity)

[0.1.0]: https://github.com/yourusername/ullm/releases/tag/v0.1.0
