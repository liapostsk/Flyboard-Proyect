# Flyboard Agent Router API

Small HTTP API that routes ambiguous user requests through an OpenAI model, decides when to call server-side tools, executes them, and returns a traceable final answer.

## Tech Stack
- Python 3.11+
- FastAPI
- OpenAI Responses API
- SQLite
- Pydantic

## What It Does
The service acts as a small decision-and-execution layer:
- answers from the local knowledge base when possible,
- creates tickets when support action is needed,
- schedules follow-ups when requested,
- returns a final answer plus tool-call trace and metrics.

## Endpoints

### `POST /v1/agent/run`
Runs the agent orchestration loop.

Request body:
```json
{
  "task": "string",
  "customer_id": "optional string",
  "language": "optional string (e.g. en, es, pt)"
}
```

Response body:
```json
{
  "trace_id": "string",
  "final_answer": "string",
  "tool_calls": [
    {
      "name": "search_kb|create_ticket|schedule_followup",
      "arguments": {},
      "result": {}
    }
  ],
  "metrics": {
    "latency_ms": 0,
    "model": "string",
    "openai_calls": 0
  }
}
```

### `GET /health`
Returns:
```json
{ "status": "ok" }
```

## Required Tools
The model can call three server-side tools, and the service executes them until the model produces a final answer.

### `search_kb(query, top_k=5, filters?)`
Searches the local `data/kb.json` dataset using keyword scoring.

Return shape:
```json
{
  "results": [
    {
      "id": "KB-...",
      "title": "...",
      "score": 0.0,
      "snippet": "...",
      "tags": ["..."]
    }
  ]
}
```

### `create_ticket(title, body, priority)`
Creates a local support ticket.

Return shape:
```json
{ "ticket_id": "TICK-000123", "status": "created" }
```

### `schedule_followup(datetime_iso, contact, channel)`
Creates a local follow-up record.

Return shape:
```json
{ "scheduled": true, "followup_id": "FUP-000045" }
```

## Architecture
- [app/clients/openai_client.py](app/clients/openai_client.py): wrapper around OpenAI Responses API.
- [app/services/agent.py](app/services/agent.py): orchestration loop, tool execution, trace/metrics.
- [app/services/tool_router.py](app/services/tool_router.py): routes validated tool calls to the right service.
- [app/services/kb.py](app/services/kb.py): local KB search implementation.
- [app/services/storage.py](app/services/storage.py): SQLite-backed tickets and follow-ups.
- [app/schemas/](app/schemas/): request/response schemas and tool payload validation.
- [app/core/](app/core/): config, logging, and custom exceptions.

## Behavior
- The agent uses the OpenAI Responses API with tool/function calling.
- Tool input is validated at the router boundary and revalidated defensively before persistence.
- Tool iterations are capped to avoid infinite loops.
- Each request generates a `trace_id` and logs latency, tool call timing, and OpenAI call count.
- OpenAI errors are handled cleanly and surfaced as controlled API errors.

## Setup
1. Clone the repo.
2. Install dependencies:
```bash
pip install -e .[dev]
```
3. Create your `.env` file and set at least:
```bash
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-4o-mini
OPENAI_TIMEOUT=60
```
4. Run the tests:
```bash
python -m pytest -q
```
5. Start the API:
```bash
python -m uvicorn app.main:app --reload
```

## Example Requests

### Pricing question
```json
{
  "task": "Give me the pricing model at a high level and what can change the quote.",
  "language": "en"
}
```
Expected flow: `search_kb` → final answer referencing KB-006.

### CRM writeback question
```json
{
  "task": "How does CRM writeback work and how long does it take to set up?",
  "language": "en"
}
```
Expected flow: `search_kb` → final answer referencing KB-004 and/or KB-018.

### Troubleshooting with ticket
```json
{
  "task": "We’re failing to write back to HubSpot since this morning. What should we check and can you open a high priority ticket for ops?",
  "language": "en"
}
```
Expected flow: `search_kb` → `create_ticket(priority=high)` → final answer with ticket id and checklist.

### Follow-up scheduling
```json
{
  "task": "Schedule a follow-up call with Marta tomorrow at 10:30 CET via WhatsApp to discuss custom SLA.",
  "language": "en"
}
```
Expected flow: `schedule_followup` → `search_kb` → final answer with follow-up id and a short note on custom SLA.

### Spanish onboarding question
```json
{
  "task": "¿En qué idiomas funciona y qué incluye el onboarding?",
  "language": "es"
}
```
Expected flow: `search_kb` → answer in Spanish.

## Testing
Run the full suite:
```bash
python -m pytest -q
```

Current test coverage includes:
- KB search behavior.
- Tool validation at the router boundary.
- Defensive validation in storage.
- API error mapping for invalid tool input.
- OpenAI timeout wiring.
- Agent orchestration loop with tool execution.

## Notes
- Coding agent used: GitHub Copilot.
- The project uses local KB + local storage only; no external web browsing.
- Python version target is 3.11+, matching [pyproject.toml](pyproject.toml).
