"""The AI provider boundary.

ARCHITECTURE.md section 18 requires AI to sit behind an abstraction so the rest
of the application never depends on a specific model runtime, and section 19
names Ollama as the only provider required initially, with Bedrock as a future
one. The application asks for structured output and validates it itself
(section 21): nothing here trusts what the model returns beyond checking that
it is a JSON object.

Resume text is sensitive career information, so prompts and model responses are
never logged and never appear in error messages.
"""

import json
from typing import Annotated, Any, Protocol, runtime_checkable

import httpx
from fastapi import Depends

from app.common.config import Settings, get_settings

AI_PROVIDER_OLLAMA = "ollama"

OLLAMA_GENERATE_PATH = "/api/generate"
JSON_FORMAT = "json"

UNAVAILABLE_MESSAGE = "The AI model is not available right now."
UNUSABLE_OUTPUT_MESSAGE = "The AI model did not return usable information."
BEDROCK_UNAVAILABLE_MESSAGE = (
    "AWS Bedrock is not implemented yet. Set AI_PROVIDER=ollama."
)


class AIError(Exception):
    """Raised when a provider cannot produce a usable result.

    The message is safe to show a user: it never carries the prompt, the model
    response, or transport detail.
    """


class AIConfigurationError(Exception):
    """Raised when the configured provider cannot be built."""


@runtime_checkable
class AIProvider(Protocol):
    """What CareerIQ needs from a model runtime."""

    async def generate_json(
        self,
        *,
        system: str,
        prompt: str,
        schema: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Return the model's answer as a JSON object.

        `schema` constrains the shape the model is asked to produce. Callers
        still validate the result; a schema is a hint to the model, not a
        guarantee.
        """
        ...


class OllamaProvider:
    """Local model runtime, used for development and self-hosted running."""

    def __init__(
        self,
        *,
        base_url: str,
        model: str,
        timeout_seconds: int,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._model = model
        self._timeout_seconds = timeout_seconds
        self._transport = transport

    async def generate_json(
        self,
        *,
        system: str,
        prompt: str,
        schema: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Ask Ollama for one JSON object, with sampling turned down."""
        payload = {
            "model": self._model,
            "system": system,
            "prompt": prompt,
            "stream": False,
            "format": schema if schema is not None else JSON_FORMAT,
            "options": {"temperature": 0},
        }

        try:
            async with httpx.AsyncClient(
                base_url=self._base_url,
                timeout=self._timeout_seconds,
                transport=self._transport,
            ) as client:
                response = await client.post(OLLAMA_GENERATE_PATH, json=payload)
                response.raise_for_status()
                body = response.json()
        except (httpx.HTTPError, json.JSONDecodeError) as error:
            raise AIError(UNAVAILABLE_MESSAGE) from error

        return _as_json_object(body.get("response") if isinstance(body, dict) else None)


def _as_json_object(content: object) -> dict[str, Any]:
    if not isinstance(content, str):
        raise AIError(UNUSABLE_OUTPUT_MESSAGE)

    try:
        parsed = json.loads(content)
    except json.JSONDecodeError as error:
        raise AIError(UNUSABLE_OUTPUT_MESSAGE) from error

    if not isinstance(parsed, dict):
        raise AIError(UNUSABLE_OUTPUT_MESSAGE)
    return parsed


def get_ai_provider(settings: Settings | None = None) -> AIProvider:
    """Build the provider named by configuration."""
    settings = settings or get_settings()

    if settings.ai_provider == AI_PROVIDER_OLLAMA:
        return OllamaProvider(
            base_url=settings.ollama_base_url,
            model=settings.ollama_model,
            timeout_seconds=settings.ai_timeout_seconds,
        )

    raise AIConfigurationError(BEDROCK_UNAVAILABLE_MESSAGE)


AIProviderDep = Annotated[AIProvider, Depends(get_ai_provider)]
