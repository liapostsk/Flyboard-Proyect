from unittest.mock import patch

from fastapi.testclient import TestClient

from app.core.exceptions import InvalidToolInput
from app.main import app
from app.schemas.agent import AgentRunResponse, Metrics


def test_agent_run_returns_400_for_invalid_tool_input():
    client = TestClient(app)

    with patch(
        "app.services.agent.AgentService.run",
        side_effect=InvalidToolInput(
            message="Invalid priority",
            trace_id="trace-test",
            tool_name="create_ticket",
            validation_details={"priority": ["must be one of: low, medium, high"]},
        ),
    ):
        response = client.post("/v1/agent/run", json={"task": "Open ticket"})

    assert response.status_code == 400
    payload = response.json()
    assert payload["detail"]["error"] == "invalid_tool_input"
    assert payload["detail"]["tool_name"] == "create_ticket"
    assert payload["detail"]["trace_id"] == "trace-test"


def test_agent_run_returns_success_payload_and_latency():
    client = TestClient(app)
    fake_result = AgentRunResponse(
        trace_id="trace-123",
        final_answer="All set.",
        tool_calls=[],
        metrics=Metrics(latency_ms=0, model="gpt-test", openai_calls=1),
    )

    with patch("app.services.agent.AgentService.run", return_value=fake_result):
        response = client.post("/v1/agent/run", json={"task": "Open a ticket"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["trace_id"] == "trace-123"
    assert payload["final_answer"] == "All set."
    assert payload["metrics"]["model"] == "gpt-test"
    assert payload["metrics"]["latency_ms"] >= 0


def test_agent_run_returns_502_for_unexpected_exception():
    client = TestClient(app)

    with patch("app.services.agent.AgentService.run", side_effect=ValueError("boom")):
        response = client.post("/v1/agent/run", json={"task": "Open a ticket"})

    assert response.status_code == 502
    payload = response.json()
    assert payload["detail"]["error"] == "OpenAI integration error"


def test_health_endpoint_returns_ok():
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
