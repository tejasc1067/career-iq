"""Tests for the AI provider boundary.

Every model call is served by an in-process transport, so the suite needs no
Ollama, no AWS credentials and no network.
"""

import json
import logging

import httpx
import pytest
from pydantic import ValidationError

from app.ai.provider import (
    BEDROCK_UNAVAILABLE_MESSAGE,
    UNAVAILABLE_MESSAGE,
    UNUSABLE_OUTPUT_MESSAGE,
    AIConfigurationError,
    AIError,
    AIProvider,
    OllamaProvider,
    get_ai_provider,
)
from app.common.config import Settings, get_settings

RESUME_TEXT = "Jane Doe\nSenior Data Engineer at Acme\nPython, SQL, Airflow"
SYSTEM = "Read the resume text and return JSON."
SCHEMA = {"type": "object", "properties": {"role": {"type": "string"}}}
SECRET = "x" * 48


def _settings(**overrides: object) -> Settings:
    return Settings(jwt_secret=SECRET, **overrides)


def _provider(handler: object, **overrides: object) -> OllamaProvider:
    return OllamaProvider(
        base_url=str(overrides.get("base_url", "http://localhost:11434")),
        model=str(overrides.get("model", "llama3.1")),
        timeout_seconds=int(overrides.get("timeout_seconds", 120)),
        transport=httpx.MockTransport(handler),
    )


def _replies(payload: object, status: int = 200) -> object:
    def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(status, json=payload)

    return handler


def _returns(content: str) -> object:
    return _replies({"response": content, "done": True})


async def test_a_json_answer_is_returned_as_a_dictionary() -> None:
    """A well-behaved model reply becomes a plain object for the caller."""
    provider = _provider(_returns('{"role": "Senior Data Engineer"}'))

    result = await provider.generate_json(system=SYSTEM, prompt=RESUME_TEXT)

    assert result == {"role": "Senior Data Engineer"}


async def test_the_request_names_the_model_and_asks_for_json() -> None:
    """The Ollama call carries the configured model and disables streaming."""
    seen: dict[str, object] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["url"] = str(request.url)
        seen["body"] = json.loads(request.content)
        return httpx.Response(200, json={"response": "{}"})

    provider = _provider(handler, model="qwen2.5")
    await provider.generate_json(system=SYSTEM, prompt=RESUME_TEXT)

    assert seen["url"] == "http://localhost:11434/api/generate"
    body = seen["body"]
    assert isinstance(body, dict)
    assert body["model"] == "qwen2.5"
    assert body["system"] == SYSTEM
    assert body["prompt"] == RESUME_TEXT
    assert body["stream"] is False
    assert body["format"] == "json"
    assert body["options"] == {"temperature": 0}


async def test_a_schema_is_passed_to_the_model_as_the_output_format() -> None:
    """A caller that knows the shape it wants can ask the model for it."""
    seen: dict[str, object] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["body"] = json.loads(request.content)
        return httpx.Response(200, json={"response": '{"role": "Engineer"}'})

    provider = _provider(handler)
    await provider.generate_json(system=SYSTEM, prompt=RESUME_TEXT, schema=SCHEMA)

    body = seen["body"]
    assert isinstance(body, dict)
    assert body["format"] == SCHEMA


async def test_a_trailing_slash_in_the_base_url_is_tolerated() -> None:
    """Configuration is not required to be punctuated exactly."""
    seen: dict[str, object] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["url"] = str(request.url)
        return httpx.Response(200, json={"response": "{}"})

    provider = _provider(handler, base_url="http://localhost:11434/")
    await provider.generate_json(system=SYSTEM, prompt=RESUME_TEXT)

    assert seen["url"] == "http://localhost:11434/api/generate"


@pytest.mark.parametrize("status", [400, 404, 429, 500, 503])
async def test_an_error_status_becomes_a_safe_failure(status: int) -> None:
    """A model runtime that refuses the request is reported, not raised raw."""
    provider = _provider(_replies({"error": "model not found"}, status=status))

    with pytest.raises(AIError) as failure:
        await provider.generate_json(system=SYSTEM, prompt=RESUME_TEXT)

    assert str(failure.value) == UNAVAILABLE_MESSAGE


async def test_an_unreachable_model_runtime_becomes_a_safe_failure() -> None:
    """Ollama not running is an expected condition, not a crash."""

    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("connection refused", request=request)

    provider = _provider(handler)

    with pytest.raises(AIError) as failure:
        await provider.generate_json(system=SYSTEM, prompt=RESUME_TEXT)

    assert str(failure.value) == UNAVAILABLE_MESSAGE


async def test_a_timeout_becomes_a_safe_failure() -> None:
    """A model that takes too long fails the same way as an absent one."""

    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ReadTimeout("too slow", request=request)

    provider = _provider(handler)

    with pytest.raises(AIError) as failure:
        await provider.generate_json(system=SYSTEM, prompt=RESUME_TEXT)

    assert str(failure.value) == UNAVAILABLE_MESSAGE


@pytest.mark.parametrize(
    "content",
    [
        "not json at all",
        '{"role": "Engineer"',
        '["Engineer"]',
        '"Engineer"',
        "42",
        "null",
        "",
    ],
)
async def test_output_that_is_not_a_json_object_is_rejected(content: str) -> None:
    """The application decides what counts as usable, not the model."""
    provider = _provider(_returns(content))

    with pytest.raises(AIError) as failure:
        await provider.generate_json(system=SYSTEM, prompt=RESUME_TEXT)

    assert str(failure.value) == UNUSABLE_OUTPUT_MESSAGE


async def test_a_reply_without_a_response_field_is_rejected() -> None:
    """A shape change in the runtime is a failure, not a silent empty result."""
    provider = _provider(_replies({"done": True}))

    with pytest.raises(AIError) as failure:
        await provider.generate_json(system=SYSTEM, prompt=RESUME_TEXT)

    assert str(failure.value) == UNUSABLE_OUTPUT_MESSAGE


async def test_a_reply_that_is_not_json_is_rejected() -> None:
    """An HTML error page from a proxy does not reach the caller as data."""

    def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, text="<html>gateway</html>")

    provider = _provider(handler)

    with pytest.raises(AIError):
        await provider.generate_json(system=SYSTEM, prompt=RESUME_TEXT)


async def test_a_failure_never_carries_the_prompt_or_the_model_output() -> None:
    """Resume text must not travel inside an error message."""
    provider = _provider(_returns(f"Sorry, I cannot help with {RESUME_TEXT}"))

    with pytest.raises(AIError) as failure:
        await provider.generate_json(system=SYSTEM, prompt=RESUME_TEXT)

    rendered = f"{failure.value!r} {failure.value.args}"
    assert "Jane Doe" not in rendered
    assert "Airflow" not in rendered


async def test_nothing_about_the_resume_is_logged(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """A model call writes neither the prompt nor the response to the log."""
    provider = _provider(_returns('{"role": "Senior Data Engineer"}'))

    with caplog.at_level(logging.DEBUG):
        await provider.generate_json(system=SYSTEM, prompt=RESUME_TEXT)

    assert "Jane Doe" not in caplog.text
    assert "Airflow" not in caplog.text
    assert "Senior Data Engineer" not in caplog.text


async def test_a_failure_logs_nothing_about_the_resume(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """The same holds when the model runtime is unavailable."""
    provider = _provider(_replies({"error": "boom"}, status=500))

    with caplog.at_level(logging.DEBUG), pytest.raises(AIError):
        await provider.generate_json(system=SYSTEM, prompt=RESUME_TEXT)

    assert "Jane Doe" not in caplog.text
    assert "Airflow" not in caplog.text


def test_ollama_is_the_configured_provider_by_default() -> None:
    """A project with no AI settings runs against the local runtime."""
    provider = get_ai_provider(_settings())

    assert isinstance(provider, OllamaProvider)
    assert isinstance(provider, AIProvider)


def test_the_provider_is_built_from_configuration() -> None:
    """Model and endpoint come from settings, not from source."""
    settings = _settings(
        ollama_base_url="http://ollama.internal:11434",
        ollama_model="qwen2.5",
        ai_timeout_seconds=30,
    )

    provider = get_ai_provider(settings)

    assert isinstance(provider, OllamaProvider)
    assert provider._base_url == "http://ollama.internal:11434"
    assert provider._model == "qwen2.5"
    assert provider._timeout_seconds == 30


def test_bedrock_is_refused_until_it_is_implemented() -> None:
    """The seam exists, and selecting it says plainly that it is not ready."""
    with pytest.raises(AIConfigurationError) as failure:
        get_ai_provider(_settings(ai_provider="bedrock"))

    assert str(failure.value) == BEDROCK_UNAVAILABLE_MESSAGE


@pytest.mark.parametrize("value", ["openai", "", "olama", "gpt-4"])
def test_an_unknown_provider_name_is_refused_by_configuration(value: str) -> None:
    """A misconfigured provider stops the application, it does not fall back."""
    with pytest.raises(ValidationError):
        _settings(ai_provider=value)


@pytest.mark.parametrize("value", ["OLLAMA", " ollama ", "Bedrock"])
def test_a_provider_name_is_normalized(value: str) -> None:
    """Case and stray spacing in configuration are not an error."""
    assert _settings(ai_provider=value).ai_provider == value.strip().lower()


def test_the_default_timeout_is_positive() -> None:
    """A non-positive timeout would make every call fail immediately."""
    with pytest.raises(ValidationError):
        _settings(ai_timeout_seconds=0)


def test_no_ai_secret_is_read_from_configuration() -> None:
    """Nothing about the AI provider requires a credential today."""
    fields = set(Settings.model_fields)

    assert not {name for name in fields if "ai" in name and "secret" in name}
    assert get_settings().ai_provider in {"ollama", "bedrock"}
