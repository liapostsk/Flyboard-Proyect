import json
from typing import Optional

from app.services.agent import AgentService
from app.services.storage import StorageService
from app.services.tool_router import ToolRouter


class _FakeResponse:
	def __init__(self, response_id: str, output: list, output_text: str = "") -> None:
		self.id = response_id
		self.output = output
		self.output_text = output_text


class _FakeFunctionCall:
	def __init__(self, call_id: str, name: str, arguments: dict) -> None:
		self.type = "function_call"
		self.call_id = call_id
		self.name = name
		self.arguments = json.dumps(arguments)


class _FakeOpenAIClient:
	def __init__(self) -> None:
		self.model = "gpt-4o-mini"
		self.calls = 0

	def call_with_tools(self, messages: list, tools: list, trace_id: str, previous_response_id: Optional[str] = None):
		self.calls += 1
		if self.calls == 1:
			return _FakeResponse(
				response_id="resp_1",
				output=[
					_FakeFunctionCall(
						call_id="call_1",
						name="search_kb",
						arguments={"query": "pricing model", "top_k": 3},
					)
				],
			)

		return _FakeResponse(response_id="resp_2", output=[], output_text="Pricing is platform fee + usage.")


class _FakeIncidentOpenAIClient:
	def __init__(self) -> None:
		self.model = "gpt-4o-mini"
		self.calls = 0

	def call_with_tools(self, messages: list, tools: list, trace_id: str, previous_response_id: Optional[str] = None):
		self.calls += 1
		if self.calls == 1:
			return _FakeResponse(
				response_id="resp_1",
				output=[
					_FakeFunctionCall(
						call_id="call_1",
						name="search_kb",
						arguments={"query": "write back HubSpot", "top_k": 3},
					)
				],
			)

		if self.calls == 2:
			return _FakeResponse(
				response_id="resp_2",
				output=[
					_FakeFunctionCall(
						call_id="call_2",
						name="create_ticket",
						arguments={
							"title": "CRM writeback failure",
							"body": "HubSpot writeback is failing for customers.",
							"priority": "high",
						},
					)
				],
			)

		return _FakeResponse(
			response_id="resp_3",
			output=[],
			output_text="Check expired tokens, field mapping drift, permissions, rate limits, customer_id, integration type, error logs, and sample payload.",
		)


def test_agent_orchestration_runs_tool_then_returns_final_answer(monkeypatch) -> None:
	monkeypatch.setenv("OPENAI_API_KEY", "test-key")
	service = AgentService()
	service.openai_client = _FakeOpenAIClient()

	result = service.run(task="Give me the pricing model")

	assert result.final_answer == "Pricing is platform fee + usage."
	assert result.metrics.openai_calls == 2
	assert result.metrics.model == "gpt-4o-mini"
	assert len(result.tool_calls) == 1
	assert result.tool_calls[0].name == "search_kb"


def test_agent_orchestration_appends_ticket_id_for_incident_flow(monkeypatch, tmp_path) -> None:
	monkeypatch.setenv("OPENAI_API_KEY", "test-key")
	monkeypatch.setattr("app.services.storage.generate_ticket_id", lambda: "TICK-000123")

	service = AgentService()
	service.openai_client = _FakeIncidentOpenAIClient()
	service.storage_service = StorageService(db_path=str(tmp_path / "app.db"))
	service.tool_router = ToolRouter(service.kb_service, service.storage_service)

	result = service.run(task="We are failing to write back to HubSpot since this morning.")

	assert result.metrics.openai_calls == 3
	assert [tool_call.name for tool_call in result.tool_calls] == ["search_kb", "create_ticket"]
	assert "Ticket ID: TICK-000123" in result.final_answer
