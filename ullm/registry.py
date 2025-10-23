"""Client registry for provider-to-client mapping."""

from typing import Any, Dict, Type

from ullm.clients.base import BaseClient

# Global registry mapping provider names to client classes
_CLIENT_REGISTRY: Dict[str, Type[BaseClient]] = {}


def register_client(provider: str):
    """Decorator to register a client class for a provider.

    Usage:
        @register_client("openai")
        class OpenAIClient(BaseClient):
            ...
    """

    def decorator(client_class: Type[BaseClient]) -> Type[BaseClient]:
        _CLIENT_REGISTRY[provider] = client_class
        return client_class

    return decorator


def get_client(provider: str, **kwargs: Any) -> BaseClient:
    """Get a client instance for the given provider.

    Args:
        provider: The provider name (e.g., "openai", "anthropic")
        **kwargs: Arguments to pass to the client constructor

    Returns:
        Instance of the appropriate client class

    Raises:
        UnsupportedProviderError: If provider is not registered
    """
    client_class = _CLIENT_REGISTRY.get(provider)

    if client_class is None:
        from ullm.exceptions import UnsupportedProviderError

        raise UnsupportedProviderError(provider, kwargs.get("model", "unknown"))

    return client_class(**kwargs)


def get_registered_providers() -> list[str]:
    """Get list of all registered provider names."""
    return list(_CLIENT_REGISTRY.keys())
