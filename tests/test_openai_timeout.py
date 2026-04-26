from unittest.mock import Mock, patch

import app.clients.openai_client as openai_client_module
from app.clients.openai_client import OpenAIResponsesClient
from app.core.exceptions import OpenAIIntegrationError


def test_openai_client_passes_explicit_timeout(monkeypatch):
    monkeypatch.setattr(openai_client_module, "OPENAI_API_KEY", "test-key")
    monkeypatch.setattr(openai_client_module, "OPENAI_MODEL", "test-model")
    monkeypatch.setattr(openai_client_module, "OPENAI_TIMEOUT", 12.5)

    dummy_openai = Mock()
    dummy_openai.responses = Mock()

    with patch("app.clients.openai_client.OpenAI", return_value=dummy_openai) as mock_openai:
        client = OpenAIResponsesClient()

    mock_openai.assert_called_once_with(api_key="test-key", timeout=12.5)
    assert client.model == "test-model"


def test_openai_timeout_is_mapped_to_integration_error(monkeypatch):
    monkeypatch.setattr(openai_client_module, "OPENAI_API_KEY", "test-key")
    monkeypatch.setattr(openai_client_module, "OPENAI_MODEL", "test-model")
    monkeypatch.setattr(openai_client_module, "OPENAI_TIMEOUT", 12.5)

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
