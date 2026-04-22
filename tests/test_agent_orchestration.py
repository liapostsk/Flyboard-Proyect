import json
from typing import Optional

from app.services.agent import AgentService


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


def test_agent_orchestration_runs_tool_then_returns_final_answer(monkeypatch) -> None:
	monkeypatch.setenv("OPENAI_API_KEY", "test-key")
	service = AgentService()
	service.openai_client = _FakeOpenAIClient()

	result = service.run(task="Give me the pricing model")

	assert result.final_answer == "Pricing is platform fee + usage."
	assert result.metrics.openai_calls == 2
	assert len(result.tool_calls) == 1
	assert result.tool_calls[0].name == "search_kb"
