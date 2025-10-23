"""Tests for provider resolution."""

import pytest

from ullm.exceptions import UnsupportedProviderError
from ullm.providers import parse_model_name


def test_parse_model_with_provider():
    """Test parsing model names with explicit provider."""
    provider, model = parse_model_name("openai/gpt-4")
    assert provider == "openai"
    assert model == "gpt-4"

    provider, model = parse_model_name("anthropic/claude-3-opus")
    assert provider == "anthropic"
    assert model == "claude-3-opus"

    provider, model = parse_model_name("groq/llama-3.1-70b-versatile")
    assert provider == "groq"
    assert model == "llama-3.1-70b-versatile"

    provider, model = parse_model_name("bedrock/anthropic.claude-v2")
    assert provider == "bedrock"
    assert model == "anthropic.claude-v2"


def test_parse_model_without_provider():
    """Test auto-detection of provider from model name."""
    provider, model = parse_model_name("gpt-4")
    assert provider == "openai"
    assert model == "gpt-4"

    provider, model = parse_model_name("claude-3-opus")
    assert provider == "anthropic"
    assert model == "claude-3-opus"

    provider, model = parse_model_name("llama-3.1-70b")
    assert provider == "groq"
    assert model == "llama-3.1-70b"

    # Default to OpenAI for unknown models
    provider, model = parse_model_name("unknown-model")
    assert provider == "openai"
    assert model == "unknown-model"


def test_parse_openai_reasoning_models():
    """Test parsing OpenAI reasoning models."""
    provider, model = parse_model_name("o1-mini")
    assert provider == "openai"
    assert model == "o1-mini"

    provider, model = parse_model_name("openai/o3")
    assert provider == "openai"
    assert model == "o3"


def test_unsupported_provider():
    """Test unsupported provider raises error."""
    with pytest.raises(UnsupportedProviderError):
        parse_model_name("unsupported/model-name")


def test_case_insensitive():
    """Test provider parsing is case-insensitive."""
    provider, model = parse_model_name("OpenAI/gpt-4")
    assert provider == "openai"
    assert model == "gpt-4"

    provider, model = parse_model_name("ANTHROPIC/claude-3")
    assert provider == "anthropic"
    assert model == "claude-3"
