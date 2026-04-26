from unittest.mock import patch

from fastapi.testclient import TestClient

from app.core.exceptions import InvalidToolInput
from app.main import app


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
