from unittest.mock import Mock, patch

import pytest

import app.clients.openai_client as openai_client_module
from app.clients.openai_client import OpenAIResponsesClient
from app.core.exceptions import OpenAIIntegrationError, RateLimitError


class _FakeResponses:
    def __init__(self, result=None, error=None):
        self.result = result
        self.error = error
        self.calls = []

    def create(self, **kwargs):
        self.calls.append(kwargs)
        if self.error is not None:
            raise self.error
        return self.result


class _FakeOpenAI:
    def __init__(self, api_key, timeout, responses):
        self.api_key = api_key
        self.timeout = timeout
        self.responses = responses


def test_openai_client_passes_explicit_timeout(monkeypatch):
    monkeypatch.setattr(openai_client_module, "OPENAI_API_KEY", "test-key")
    monkeypatch.setattr(openai_client_module, "OPENAI_MODEL", "test-model")
    monkeypatch.setattr(openai_client_module, "OPENAI_TIMEOUT", 12.5)
    monkeypatch.setattr(openai_client_module, "OPENAI_SYSTEM_PROMPT", "test-prompt")

    dummy_openai = Mock()
    dummy_openai.responses = Mock()

    with patch("app.clients.openai_client.OpenAI", return_value=dummy_openai) as mock_openai:
        client = OpenAIResponsesClient()

    mock_openai.assert_called_once_with(api_key="test-key", timeout=12.5)
    assert client.model == "test-model"
    assert client.system_prompt == "test-prompt"


def test_openai_timeout_is_mapped_to_integration_error(monkeypatch):
    monkeypatch.setattr(openai_client_module, "OPENAI_API_KEY", "test-key")
    monkeypatch.setattr(openai_client_module, "OPENAI_MODEL", "test-model")
    monkeypatch.setattr(openai_client_module, "OPENAI_TIMEOUT", 12.5)
    monkeypatch.setattr(openai_client_module, "OPENAI_SYSTEM_PROMPT", "test-prompt")

    dummy_responses = Mock()
    dummy_responses.create.side_effect = RuntimeError("timeout")
    dummy_openai = Mock()
    dummy_openai.responses = dummy_responses

    with patch("app.clients.openai_client.OpenAI", return_value=dummy_openai):
        client = OpenAIResponsesClient()
        try:
            client.call_with_tools(messages=[], tools=[], trace_id="trace-1")
            assert False, "Expected OpenAIIntegrationError"
        except OpenAIIntegrationError as exc:
            assert exc.trace_id == "trace-1"


def test_openai_client_passes_previous_response_id_and_system_prompt(monkeypatch):
    monkeypatch.setattr(openai_client_module, "OPENAI_API_KEY", "test-key")
    monkeypatch.setattr(openai_client_module, "OPENAI_MODEL", "test-model")
    monkeypatch.setattr(openai_client_module, "OPENAI_TIMEOUT", 12.5)
    monkeypatch.setattr(openai_client_module, "OPENAI_SYSTEM_PROMPT", "test-prompt")

    responses = _FakeResponses(result={"ok": True})

    with patch(
        "app.clients.openai_client.OpenAI",
        side_effect=lambda api_key, timeout: _FakeOpenAI(api_key, timeout, responses),
    ) as mock_openai:
        client = OpenAIResponsesClient()
        result = client.call_with_tools(
            messages=[{"role": "user", "content": "hello"}],
            tools=[{"type": "function"}],
            trace_id="trace-2",
            previous_response_id="resp-previous",
        )

    mock_openai.assert_called_once_with(api_key="test-key", timeout=12.5)
    assert result == {"ok": True}
    assert responses.calls[0]["previous_response_id"] == "resp-previous"
    assert responses.calls[0]["instructions"] == "test-prompt"
    assert responses.calls[0]["model"] == "test-model"


@pytest.mark.parametrize(
    ("error_message", "expected_exception"),
    [
        ("rate_limit exceeded", RateLimitError),
        ("api_error from upstream", OpenAIIntegrationError),
        ("unexpected failure", OpenAIIntegrationError),
    ],
)
def test_openai_client_maps_error_messages(monkeypatch, error_message, expected_exception):
    monkeypatch.setattr(openai_client_module, "OPENAI_API_KEY", "test-key")
    monkeypatch.setattr(openai_client_module, "OPENAI_MODEL", "test-model")
    monkeypatch.setattr(openai_client_module, "OPENAI_TIMEOUT", 12.5)
    monkeypatch.setattr(openai_client_module, "OPENAI_SYSTEM_PROMPT", "test-prompt")

    responses = _FakeResponses(error=RuntimeError(error_message))

    with patch(
        "app.clients.openai_client.OpenAI",
        side_effect=lambda api_key, timeout: _FakeOpenAI(api_key, timeout, responses),
    ):
        client = OpenAIResponsesClient()

        with pytest.raises(expected_exception) as exc_info:
            client.call_with_tools(messages=[], tools=[], trace_id="trace-3")

    assert exc_info.value.trace_id == "trace-3"
