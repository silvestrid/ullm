"""Groq provider client."""

import os
from typing import Optional

from ullm.clients.openai import OpenAIClient


class GroqClient(OpenAIClient):
    """
    Client for Groq API.
    Groq uses OpenAI-compatible API, so we inherit from OpenAIClient.
    """

    def _get_api_key_from_env(self) -> Optional[str]:
        return os.getenv("GROQ_API_KEY")

    def _get_default_api_base(self) -> str:
        return os.getenv("GROQ_API_BASE", "https://api.groq.com/openai/v1")

    def _get_headers(self) -> dict[str, str]:
        """Get headers for Groq API."""
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }
