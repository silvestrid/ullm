"""Provider resolution and model name parsing."""

from typing import Tuple

from ullm.exceptions import UnsupportedProviderError

# Supported providers
SUPPORTED_PROVIDERS = ["openai", "anthropic", "groq", "bedrock"]

# Model name prefixes that indicate specific providers
PROVIDER_PREFIXES = {
    "gpt": "openai",
    "o1": "openai",
    "o3": "openai",
    "text-embedding": "openai",
    "claude": "anthropic",
    "llama": "groq",
    "mixtral": "groq",
    "gemma": "groq",
}


def parse_model_name(model: str) -> Tuple[str, str]:
    """
    Parse model name into provider and model.

    Supports formats:
    - provider/model-name (e.g., "openai/gpt-4")
    - model-name (e.g., "gpt-4" -> auto-detect provider)

    Args:
        model: Model string to parse

    Returns:
        Tuple of (provider, model_name)

    Raises:
        ProviderNotFoundError: If provider cannot be determined
        UnsupportedProviderError: If provider is not supported
    """
    # Check if model includes provider prefix
    if "/" in model:
        parts = model.split("/", 1)
        if len(parts) == 2:
            provider, model_name = parts
            provider = provider.lower()

            if provider not in SUPPORTED_PROVIDERS:
                raise UnsupportedProviderError(provider, model)

            return provider, model_name

    # Auto-detect provider from model name
    model_lower = model.lower()

    # Check common prefixes
    for prefix, provider in PROVIDER_PREFIXES.items():
        if model_lower.startswith(prefix):
            return provider, model

    # Default to OpenAI for unknown models (most common)
    # This matches litellm behavior for backward compatibility
    return "openai", model


def get_api_key_env_var(provider: str) -> str:
    """Get the environment variable name for a provider's API key."""
    return f"{provider.upper()}_API_KEY"


def get_api_base_env_var(provider: str) -> str:
    """Get the environment variable name for a provider's API base URL."""
    return f"{provider.upper()}_API_BASE"
